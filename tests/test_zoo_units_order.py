"""Unit columns read as numbers: the rule order and the person's answer (plan P4-D438).

Lane UN-1a of the zoo-fix track (`wave6/ZOO/PLAN.md` section 2.1; the
method page P4-D419, ZR.1's stand-asides (i) and (ii), rule 0c's yield,
ZR.2's question Q-UNIT and ZR.5's carry-over). Each case is red on the
mutant its docstring names:

- (a) rule 7 stands aside for a suffix unit with a level below the floor,
  and for any affix reading the person answered `measurement`; `Stage 2`
  stays a label and the A-P4-58 remarks stay;
- (b) the validator reads a file's column the way its description read
  it, so a faithful file whose every level clears the floor is not
  reported as a role missed;
- (c) question Q-UNIT offers `measurement` on a unit column rule 7 kept
  as labels, inside the question already put where one is (never a
  second question);
- (d) rule 0c keeps the exact list where every whole-cell level clears
  the floor;
- HX's case: a unit column whose person question is open publishes
  nothing from it (plan P4-D401).

THE REPAIR ROUND (lane UN-1a, repair 1: skeptic 1 and Codex's review),
each case red on its mutant too: rule 0c's yield takes rule 7's list at
once, never a date or a clock rule between; a wrapper with no unit is
no suffix unit; a unit column read as numbers publishes what the same
numbers written bare publish, in rows and in people (lane UN-1b, plan
P4-D443, which withdrew UN-1a's stricter guard), and no written form
fewer cells than the floor write; Q-UNIT's `keep` is carried across rounds; no month is a
unit, nor a lab's flag; the terminal's `measurement` beside `keep` is a key of its own
and a declaration; the validator reads a column as its description
read it, labels and joined numbers included; a declared decimal comma
reads every cell; the KPI driver emits no total over a missing twin.

Most tables here are under the table floor (P4-D425), through the
suite's internal switch (`tests/conftest.py`); three cases run at the
floor's 20,000 rows, one profile each (the suite's time rule of
2026-10-26: one case per writer). The zoo's 20,000-row proof is the KPI
driver's (`tools/measurements/kpi_zoo_units.py`, K-HZ-08 and K-HZ-09,
under `kpi_run --slow`).
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import pathlib
import random
import re

import pytest

from synthtwin import asking, cli, taxonomy

import unanswered_identifier_shapes as shapes

_MISSED = re.compile(r"^\s*(\S+) \[[^\]]+\]: MISSED$", re.MULTILINE)


def _profile(folder: pathlib.Path, lines: "list[str]", *typed: str) -> int:
    table = folder / "t.csv"
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return cli.main(["profile", f"{table}", "--out-dir", f"{folder}", "--replace"] + list(typed))


def _block(folder: pathlib.Path, column: str) -> "dict[str, object]":
    document = json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))
    return [one for one in document["columns"] if one["name"] == column][0]


def _asked(folder: pathlib.Path, column: str) -> "list[dict[str, object]]":
    document = json.loads((folder / "t-questions.json").read_text(encoding="utf-8"))
    return [entry for entry in document["asked"] if entry["column"] == column]


def _offered(entry: "dict[str, object]") -> "list[str]":
    return [f"{one['answer']}" for one in entry["answers_you_can_give"]]  # type: ignore[union-attr]


def _answer(folder: pathlib.Path, column: str, answer: str) -> None:
    path = folder / "t-questions.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    for entry in document["asked"]:
        if entry["column"] == column:
            entry["your_answer"] = answer
    path.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")


def _spo2(rows: int, seed: int) -> "list[str]":
    """Oxygen saturations as the zoo writes them: `98%`, a few rare low readings."""
    draw = random.Random(seed)
    return [f"{min(100, max(85, round(draw.gauss(97, 2))))}%" for _row in range(rows)]


def _cycled(values: "list[str]", each: int) -> "list[str]":
    return [value for _turn in range(each) for value in values]


# -- (a) rule 7 stands aside ----------------------------------------------


@pytest.fixture(scope="module")
def spo2_at_the_floor(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    """The zoo's `98%` at the table floor's 20,000 rows, described once for (a) and (b)."""
    folder = tmp_path_factory.mktemp("spo2")
    assert _profile(folder, ["spo2"] + _spo2(20_000, 7)) == 0
    return folder


def test_a_suffix_unit_with_a_rare_level_is_read_as_numbers(spo2_at_the_floor: pathlib.Path) -> None:
    """(a) undeclared: `98%` with levels below the floor is `affixed_number`, its twin cells numbers.

    At 20,000 rows, where every value the block publishes is held by the
    floor's rows. Red on the mutant without stand-aside (i): rule 7
    claims the column, and the twin writes its held-back levels as
    `group-N`.
    """
    folder = spo2_at_the_floor
    assert _block(folder, "spo2")["role"] == taxonomy.ROLE_AFFIXED
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{folder}",
                         "--seed", "0", "--replace"]) == 0
    twin = (folder / "t-twin.csv").read_text(encoding="utf-8").split("\n")[1:]
    assert [cell for cell in twin if cell and not re.fullmatch(r"\d{2,3}%", cell)] == []


def test_a_word_in_front_stays_a_label(tmp_path: pathlib.Path) -> None:
    """(a) `Stage 2` and `Grade 3` beside a rare level stay `categorical` (amendment A-P4-58).

    Red on the mutant that stands aside for a word in front as well,
    where the reading of `Stage N` is asked of the wrappers themselves.
    """
    assert not taxonomy._suffix_wrapped(_reading([("Stage ", ""), ("Grade ", "")]))
    assert not taxonomy._suffix_wrapped(_reading([("Stage ", " mg")]))
    for word in ("Stage", "Grade"):
        cells = _cycled([f"{word} {level}" for level in range(1, 5)], 100) + [f"{word} 0"] * 3
        assert _profile(tmp_path, ["x"] + cells) == 0
        assert _block(tmp_path, "x")["role"] == taxonomy.ROLE_CATEGORICAL, word


def test_every_level_clearing_the_floor_keeps_the_exact_list(tmp_path: pathlib.Path) -> None:
    """(a) undeclared, a unit column whose every level clears the floor keeps its list.

    Red on the mutant without `_a_level_is_below_the_floor` in stand-aside (i).
    """
    cells = _cycled([f"{150 + level} cm" for level in range(20)], 30)
    assert _profile(tmp_path, ["stature"] + cells) == 0
    block = _block(tmp_path, "stature")
    assert block["role"] == taxonomy.ROLE_CATEGORICAL
    assert not block.get("suppressed_levels")


def test_the_measurement_answer_reads_either_wrapper(tmp_path: pathlib.Path) -> None:
    """(a) stand-aside (ii): `--measurement` reads `172 cm` whose levels all clear, and `Stage 2`.

    Red on the mutant that asks the floor of the declared column too.
    """
    cells = _cycled([f"{150 + level} cm" for level in range(20)], 30)
    assert _profile(tmp_path, ["stature"] + cells, "--measurement", "stature") == 0
    assert _block(tmp_path, "stature")["role"] == taxonomy.ROLE_AFFIXED
    staged = _cycled([f"Stage {level}" for level in range(1, 5)], 100)
    assert _profile(tmp_path, ["x"] + staged, "--measurement", "x") == 0
    assert _block(tmp_path, "x")["role"] == taxonomy.ROLE_AFFIXED


def test_the_a_p4_58_remarks_stay(tmp_path: pathlib.Path) -> None:
    """(a) the two remarks of amendment A-P4-58 are still written where they were.

    A lab column of readings beside spaced flags is asked which reading
    fits (`remark_two_readings_both_fit`), and readings with a letter
    flush against the digits are told a declaration reads them
    (`remark_a_letter_against_the_digits`). Red on a mutant that drops
    either remark.
    """
    draw = random.Random(3)
    flagged = [f"{draw.uniform(3.0, 9.0):.2f}" for _row in range(280)] + ["10.50 H"] * 11 + ["2.10 L"] * 11
    assert _profile(tmp_path, ["result"] + flagged) == 0
    assert _remarked(tmp_path, "result", taxonomy.REMARK_TWO_READINGS_FIT)
    letters = [f"{draw.uniform(3.0, 9.0):.1f}H" for _row in range(150)] + [f"{draw.uniform(3.0, 9.0):.1f}" for _row in range(150)]
    assert _profile(tmp_path, ["flagged"] + letters) == 0
    assert _remarked(tmp_path, "flagged", taxonomy.REMARK_A_LETTER_NEEDS_A_DECLARATION)


def _remarked(folder: pathlib.Path, column: str, form: str) -> bool:
    """Whether the column's remarks carry the sentence of ``form`` (its words after the count)."""
    words = taxonomy.rendered(form, (17,)).split("17 ", 1)[1][:60]
    return any(words in f"{remark}" for remark in _block(folder, column)["remarks"])  # type: ignore[union-attr]


# -- (b) the validator carries the reading over ----------------------------


def _missed_against(described: pathlib.Path, folder: pathlib.Path, column: str, cells: "list[str]") -> "list[str]":
    """The checks MISSED when a file of ``cells`` is validated against the description in ``described``."""
    checked = folder / "file.csv"
    checked.write_text("\n".join([column] + cells) + "\n", encoding="utf-8", newline="\n")
    out = folder / "checked"
    out.mkdir(exist_ok=True)
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        code = cli.main(["validate", f"{described / 't-profile.json'}", "--twin", f"{checked}",
                         "--out-dir", f"{out}", "--replace"])
    assert code in (0, 3), code
    report = "\n".join(path.read_text(encoding="utf-8") for path in sorted(out.glob("*quality*.txt")))
    return _MISSED.findall(report)


def test_a_file_is_read_as_its_description_read_the_column(
    spo2_at_the_floor: pathlib.Path, tmp_path: pathlib.Path
) -> None:
    """(b) a file whose levels all clear the floor is checked as `affixed_number`, as described.

    The description read `98%` at 20,000 rows as numbers (stand-aside
    (i)); the checked file holds its levels on 11 rows or more alone, so
    the order by itself would read it as labels. Red on the mutant
    without `validation._described_affixed_here`: `axes.role` is MISSED.
    """
    real = _spo2(20_000, 7)
    counts: "dict[str, int]" = {}
    for cell in real:
        counts[cell] = counts.get(cell, 0) + 1
    common = [cell for cell in real if counts[cell] >= 11]
    missed = _missed_against(spo2_at_the_floor, tmp_path, "spo2", common)
    assert "axes.role" not in missed and "axes.statistical_type" not in missed, missed


def test_a_description_of_labels_is_checked_as_labels(tmp_path: pathlib.Path) -> None:
    """(b) a description that read a unit column as labels is checked as labels.

    Codex's review of lane UN-1a, item 4: `98%` at 20,000 rows beside one
    `see note` is described as labels (stand-aside (i) reads every cell
    or none), as every description before P4-D438 described it; the file
    checked against it holds the readings alone, which stand-aside (i)
    would read as numbers. Red on the mutant without
    `validation._described_labels_here`: `axes.role` is MISSED.
    """
    real = _spo2(20_000, 7)
    assert _profile(tmp_path, ["spo2"] + real[:-1] + ["see note"]) == 0
    assert _block(tmp_path, "spo2")["role"] == taxonomy.ROLE_CATEGORICAL
    missed = _missed_against(tmp_path, tmp_path, "spo2", real)
    assert "axes.role" not in missed and "axes.statistical_type" not in missed, missed


def test_an_older_description_is_checked_as_it_read_the_column(tmp_path: pathlib.Path) -> None:
    """(b) a description that read a column as joined numbers is checked as joined numbers.

    Codex's review of lane UN-1a, item 4: a description written where
    rule 0c did not yield (a rare range beside five common ones,
    declared a measurement: `joined_numbers`, as every description
    before P4-D438 read it) is checked against a file of the five
    common ranges alone, which rule 0c would now yield to the list.
    Red on the mutant without `validation._described_labels_here`:
    `axes.role` is MISSED against the description's own reading.
    """
    ranges = ["3.5-5.0", "70-99", "0.6-1.2", "12.0-16.0", "4.0-5.6"]
    real = _cycled(ranges, 120) + ["8.0-9.0"] * 3
    assert _profile(tmp_path, ["ref_range"] + real, "--measurement", "ref_range") == 0
    assert _block(tmp_path, "ref_range")["role"] == taxonomy.ROLE_JOINED
    missed = _missed_against(tmp_path, tmp_path, "ref_range", _cycled(ranges, 120))
    assert "axes.role" not in missed and "axes.statistical_type" not in missed, missed


# -- (c) question Q-UNIT ---------------------------------------------------


def test_q_unit_offers_measurement_and_the_answer_reads_it(tmp_path: pathlib.Path) -> None:
    """(c) a unit column kept as labels is put Q-UNIT; `measurement` reads it as numbers.

    Q-UNIT offers `keep` (Enter), `measurement` and `code`, never
    `identifier`, and holds nothing: unanswered, the exact list stands.
    Red on the mutant without the question, and on the mutant whose
    answer the classifier ignores.
    """
    cells = _cycled([f"{150 + level} cm" for level in range(20)], 30)
    assert _profile(tmp_path, ["stature"] + cells) == 0
    asked = _asked(tmp_path, "stature")
    assert len(asked) == 1
    assert _offered(asked[0]) == [asking.ANSWER_KEEP, asking.ANSWER_MEASUREMENT, asking.ANSWER_CODE]
    assert "made-up `72 kg`" in f"{asked[0]['what_synthtwin_saw']}"
    # ...and claims no more than its trigger reads (Codex item 7).
    assert "every value is" not in f"{asked[0]['what_synthtwin_saw']}"
    assert _block(tmp_path, "stature")["role"] == taxonomy.ROLE_CATEGORICAL
    _answer(tmp_path, "stature", asking.ANSWER_MEASUREMENT)
    assert _profile(tmp_path, ["stature"] + cells, "--answers", f"{tmp_path / 't-questions.json'}") == 0
    assert _block(tmp_path, "stature")["role"] == taxonomy.ROLE_AFFIXED


def _flush_register(people: int, visits: int) -> "list[str]":
    """`172cm` flush, on a long table: the person question's route two reaches it."""
    return [f"{150 + (person % 40)}cm" for person in range(people) for _visit in range(visits)]


def test_one_question_a_column_and_hx_holds_it(tmp_path: pathlib.Path) -> None:
    """(c) and HX's case: the person question, put to a unit column, offers `measurement`; open, it holds.

    The column is put ONE question -- the person question (P4-D401's
    route two), which now offers `measurement` and `code` beside `keep`
    and `identifier` -- and, unanswered, publishes no value: the twin
    writes no real cell. Answered `measurement`, it is read as numbers.
    Red on the mutant that puts Q-UNIT as a second question, and on the
    mutant that lets Q-UNIT displace the person question (the column
    published whole).
    """
    cells = _flush_register(40, 15)
    assert _profile(tmp_path, ["stature_flush"] + cells) == 0
    asked = _asked(tmp_path, "stature_flush")
    assert len(asked) == 1
    offered = _offered(asked[0])
    assert asking.ANSWER_IDENTIFIER in offered and asking.ANSWER_MEASUREMENT in offered
    assert asking.ANSWER_CODE in offered
    block = _block(tmp_path, "stature_flush")
    assert block["role"] == taxonomy.ROLE_IDENTIFIER
    published = json.dumps(block)
    assert not [cell for cell in set(cells) if cell in published]
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["generate", f"{tmp_path / 't-profile.json'}", "--out-dir", f"{tmp_path}",
                         "--seed", "0", "--replace"]) == 0
    twin = set((tmp_path / "t-twin.csv").read_text(encoding="utf-8").split("\n")[1:])
    assert not twin & set(cells)
    _answer(tmp_path, "stature_flush", asking.ANSWER_MEASUREMENT)
    assert _profile(tmp_path, ["stature_flush"] + cells, "--answers", f"{tmp_path / 't-questions.json'}") == 0
    assert _block(tmp_path, "stature_flush")["role"] == taxonomy.ROLE_AFFIXED


# -- (d) rule 0c yields to rule 7 -------------------------------------------


def test_a_joined_answer_keeps_an_exact_list(tmp_path: pathlib.Path) -> None:
    """(d) a reference range of five levels, each on 120 rows, declared a measurement, keeps its list.

    Its twin writes the five ranges exactly as the real does. Red on the
    mutant without rule 0c's yield: `joined_numbers`, whose positions are
    spelled apart (`12.0-16`).
    """
    ranges = ["3.5-5.0", "70-99", "0.6-1.2", "12.0-16.0", "4.0-5.6"]
    cells = _cycled(ranges, 120)
    assert _profile(tmp_path, ["ref_range"] + cells, "--measurement", "ref_range") == 0
    block = _block(tmp_path, "ref_range")
    assert block["role"] == taxonomy.ROLE_CATEGORICAL
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["generate", f"{tmp_path / 't-profile.json'}", "--out-dir", f"{tmp_path}",
                         "--seed", "0", "--replace"]) == 0
    twin = [cell for cell in (tmp_path / "t-twin.csv").read_text(encoding="utf-8").split("\n")[1:] if cell]
    assert set(twin) == set(ranges)


def test_a_joined_answer_with_a_rare_level_is_still_joined(tmp_path: pathlib.Path) -> None:
    """(d) the yield is only where every level clears the floor: a rare pair keeps the joined reading.

    Red on the mutant that yields whatever the levels hold.
    """
    cells = _cycled(["120/80", "130/85", "110/70", "140/90"], 150) + ["150/95"] * 3
    assert _profile(tmp_path, ["bp"] + cells, "--measurement", "bp") == 0
    assert _block(tmp_path, "bp")["role"] == taxonomy.ROLE_JOINED


def test_a_register_with_a_letter_in_front_is_not_offered_measurement(tmp_path: pathlib.Path) -> None:
    """(c) a register written `P100000` keeps the person question as it was: no `measurement`.

    A letter flush in front of the number is a code's register
    (`taxonomy._stands_apart`), not a unit, so Q-UNIT neither asks it nor
    adds its answers to the question it is put. Red on the mutant that
    lets a flush prefix through `taxonomy.reads_as_a_unit`.
    """
    cells = [f"P{100000 + person}" for person in range(60) for _visit in range(10)]
    assert _profile(tmp_path, ["subject"] + cells) == 0
    asked = _asked(tmp_path, "subject")
    assert len(asked) == 1
    assert _offered(asked[0]) == [asking.ANSWER_KEEP, asking.ANSWER_IDENTIFIER]


def test_the_safe_harbor_question_is_the_one_put(tmp_path: pathlib.Path) -> None:
    """(c) an age column written `NN years`, levels above 89, is put the Safe Harbor question alone.

    Q-UNIT gives way where the Safe Harbor reach takes the column (plan
    P4-D427): one question a column, in the file and on the screen of a
    scripted run alike. Red on the mutant that drops the reach test from
    `asking.unit_questions` (the screen names Q-UNIT the file does not).
    """
    cells = _cycled([f"{age} years" for age in range(60, 100)], 15)
    table = tmp_path / "t.csv"
    table.write_text("\n".join(["age"] + cells) + "\n", encoding="utf-8", newline="\n")
    said = io.StringIO()
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
            assert cli.main(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace"]) == 0
    assert "MIGHT BE AMOUNTS IN A UNIT" not in said.getvalue()
    asked = _asked(tmp_path, "age")
    assert len(asked) == 1
    assert _offered(asked[0]) == [asking.ANSWER_SAFE_HARBOR_NO, asking.ANSWER_SAFE_HARBOR_YES]


def test_the_scripted_notice_names_a_unit_column_as_labels(tmp_path: pathlib.Path) -> None:
    """(c) where nobody is at the keyboard, the notice says the column was read as labels and names `--measurement`.

    Red on the mutant that lets Q-UNIT fall under the heading for columns
    read as measurements.
    """
    cells = _cycled([f"{150 + level} cm" for level in range(20)], 30)
    table = tmp_path / "t.csv"
    table.write_text("\n".join(["stature"] + cells) + "\n", encoding="utf-8", newline="\n")
    said = io.StringIO()
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
            assert cli.main(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace"]) == 0
    screen = said.getvalue()
    assert "READ AS LABELS, AND MIGHT BE AMOUNTS IN A UNIT" in screen
    assert "--measurement stature" in screen
    assert "MIGHT BE CODES" not in screen


def test_a_figure_or_a_mark_alone_behind_the_number_stays_a_label(tmp_path: pathlib.Path) -> None:
    """(a) undeclared, `2345-7` (a LOINC code) and `3+` (a dipstick grade) beside a rare level stay labels.

    Stand-aside (i) reads a unit behind the number: no figure in it, and a
    word or `%`. (The LOINC column is held by the two-numbers question,
    P4-D401, as before; it is never read as a number beside a unit.) Red
    on the mutants that take a suffix holding a figure, or marks alone,
    asked of the wrappers themselves too.

    CHANGED ON PURPOSE BY LANE UN-1b (plan P4-D443; the zoo-fix plan's
    2.1b (d)): a unit holding figures that stands apart from its number,
    `450 x10^9/L`, is a unit and no code's other half, so the platelets
    beside a rare level are read as numbers with their unit; a figure
    flush behind the number (`2345-7`) still keeps the labels.
    """
    assert not taxonomy._suffix_wrapped(_reading([("", "-7"), ("", "-0")]))
    assert not taxonomy._suffix_wrapped(_reading([("", "+"), ("", "-")]))
    codes = _cycled(["2345-7", "2160-0", "4548-4", "2951-2", "2823-3"], 100) + ["1742-6"] * 3
    assert _profile(tmp_path, ["loinc"] + codes) == 0
    assert _block(tmp_path, "loinc")["role"] != taxonomy.ROLE_AFFIXED
    counts = _cycled([f"{value} x10^9/L" for value in (150, 200, 250, 300)], 100) + ["450 x10^9/L"] * 3
    assert _profile(tmp_path, ["platelets"] + counts) == 0
    assert _block(tmp_path, "platelets")["role"] == taxonomy.ROLE_AFFIXED
    grades = _cycled(["1+", "2+", "3+"], 150) + ["4+"] * 4
    assert _profile(tmp_path, ["protein"] + grades) == 0
    assert _block(tmp_path, "protein")["role"] == taxonomy.ROLE_CATEGORICAL


def test_a_straggler_keeps_the_list_and_puts_the_question(tmp_path: pathlib.Path) -> None:
    """(a) and (c): `98%` beside one `see note` stays labels undeclared, and is put Q-UNIT.

    Read as numbers, the one cell no unit reads would be published as a
    count of one cell left out of the statistics, the class `K-S3-12`
    holds at its ceiling; the person's `measurement` reads it. Red on the
    mutant that stands aside whatever the stragglers, asked of the reading
    itself too.
    """
    settings = taxonomy.Settings(small_cell_floor=11)
    present = _spo2(600, 7) + ["see note"]
    tally = taxonomy._tally(taxonomy._classify_all(present, False), len(present), settings, False)
    every = taxonomy._affixed_reading(tally, True)
    assert every is not None and not taxonomy._reads_every_cell(every, tally)
    cells = _cycled([f"{value}%" for value in range(90, 100)], 60) + ["see note"]
    assert _profile(tmp_path, ["spo2"] + cells) == 0
    assert _block(tmp_path, "spo2")["role"] == taxonomy.ROLE_CATEGORICAL
    asked = _asked(tmp_path, "spo2")
    assert [_offered(entry) for entry in asked] == [
        [asking.ANSWER_KEEP, asking.ANSWER_MEASUREMENT, asking.ANSWER_CODE]
    ]


def test_a_register_list_keeps_its_own_answers(tmp_path: pathlib.Path) -> None:
    """(c) a record number closed by `;`, quoted, or beside `pending` is put the list question as it was.

    Lane HX4's registers of one record number a cell (plan P4-D424,
    `shapes.LISTED_ONE`) read, to the affix reading the answer
    `measurement` admits, as a number beside a mark or a word; a key is
    not an amount in a unit, so the list question offers `keep`, `code`
    and `identifier` alone and Q-UNIT is not put. Red on the mutant that
    adds Q-UNIT's answers to the list question.
    """
    for kind in ("reglistone6", "reglistquoted6", "reglistword6"):
        table, _keys = shapes.write_table(tmp_path, kind, 600)
        with shapes.nobody_at_the_keyboard():
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                assert cli.main(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace"]) == 0
        document = json.loads((tmp_path / f"{table.stem}-questions.json").read_text(encoding="utf-8"))
        asked = [entry for entry in document["asked"] if entry["column"] == kind]
        assert [_offered(entry) for entry in asked] == [
            [asking.ANSWER_KEEP, asking.ANSWER_CODE, asking.ANSWER_IDENTIFIER]
        ], kind


# -- the repair round (skeptic 1 and Codex's review of lane UN-1a) -----------


def test_a_joined_yield_never_reaches_a_date_or_a_clock_rule(tmp_path: pathlib.Path) -> None:
    """(d) rule 0c yields to rule 7's list at once: a joined column is never read as dates or clocks.

    Skeptic 1 item 1 (R-P4-51's `1/4/10`, `2/3/20`, ... declared joined
    came back as dates) and Codex item 3 (`1:02`, `01:02`, `2:03`,
    `02:03` declared a measurement came back as times of day). Both keep
    their exact list. Red on the mutant that lets the yield fall on
    through rules 2 to 6.
    """
    for name, levels in (
        ("dated", ["1/4/10", "2/3/20", "3/2/30", "4/1/40"]),
        ("ratio", ["1:02", "01:02", "2:03", "02:03"]),
    ):
        assert _profile(tmp_path, [name] + _cycled(levels, 150), "--measurement", name) == 0
        block = _block(tmp_path, name)
        assert block["role"] == taxonomy.ROLE_CATEGORICAL, (name, block["role"])
        assert not block.get("suppressed_levels"), name


def _reading(pairs: "list[tuple[str, str]]") -> "taxonomy._Affixed":
    """An affix reading wearing ``pairs``, the first the commonest: the wrappers alone."""
    return taxonomy._Affixed(
        pairs[0][0], pairs[0][1], [(one, other, 20) for one, other in pairs[1:]], [], [], 0
    )


def test_a_wrapper_with_no_unit_is_no_suffix_unit() -> None:
    """(a) censored counts `<5` and `>1000` beside bare counts are not a unit column.

    Skeptic 1 item 2: a wrapper with nothing behind the number passed as
    a suffix wrapper, so stand-aside (i) read a viral load the count in
    people held as numbers, its interior rungs held by 7 to 10 people.
    Some wrapper must carry a unit. Red on the mutant that accepts a
    reading of bare and marked wrappers alone.
    """
    assert not taxonomy._suffix_wrapped(_reading([("", ""), ("<", ""), (">", "")]))
    assert not taxonomy._suffix_wrapped(_reading([("<", ""), (">", "")]))
    assert taxonomy._suffix_wrapped(_reading([("", "%"), ("<", "%")]))
    assert taxonomy._suffix_wrapped(_reading([("", " cm"), ("", "")]))
    assert not taxonomy._suffix_wrapped(_reading([("", " Jan"), ("", " Feb")]))


def test_a_value_two_rows_hold_is_published_as_the_bare_numbers_publish_it(tmp_path: pathlib.Path) -> None:
    """A unit column read as numbers publishes what the same numbers written bare publish.

    CHANGED ON PURPOSE BY LANE UN-1b (plan P4-D443; the orchestrator's
    LANE UN-1a RULINGS 2 (2): P4-D35, the owner's rulings of 2026-09-03
    and 2026-09-22, THE PRINCIPLE of 2026-10-01). Codex's item 1 for
    UN-1a, at 600 rows: `10 cm` on 299 rows, `21 cm` on two and `30 cm`
    on 299. UN-1a kept the column as labels, stricter than the bare
    column `10`, `21`, `30`, which reads as a count and prints `p50: 21.0`;
    the unit column now prints exactly that, no stricter and no looser.
    Red on the mutant restoring UN-1a's rare-value guard.
    """
    cells = ["10 cm"] * 299 + ["21 cm"] * 2 + ["30 cm"] * 299
    assert _profile(tmp_path, ["x"] + cells) == 0
    unit = _block(tmp_path, "x")
    assert _profile(tmp_path, ["x"] + [cell[:-3] for cell in cells]) == 0
    bare = _block(tmp_path, "x")
    assert unit["role"] == taxonomy.ROLE_AFFIXED
    assert _numeric_facts(unit) == _numeric_facts(bare)


def test_a_value_two_people_hold_is_counted_as_the_bare_numbers_are(tmp_path: pathlib.Path) -> None:
    """In people as in rows: a unit column is held exactly where its bare numbers are.

    CHANGED ON PURPOSE BY LANE UN-1b (plan P4-D443; LANE UN-1a RULINGS 2
    (1) and (2)). Skeptic 1 item 3, at 20,000 rows: 2,000 people of 10
    rows each, two of them `266.5 mg` on every row (20 rows: the floor in
    rows, two people), answered `measurement`. A measurement not attached
    to its subject is counted as on a table of one row a person (plan
    P4-D406), so the bare column prints its 20-row minimum and so does the
    unit column; a column ATTACHED to its subject (one value a person on
    every row) is counted in people, so the bare column is held and so is
    the unit column (no `266.5` printed). Under a declared person column and
    an open person question alike (HX's case, P4-D401). Values from 285
    to 301 stay outside the Safe Harbor ages. Red on the mutant restoring
    UN-1a's count of every value in people (stricter than bare: the
    unattached unit column held) and on the mutant reading a unit
    column's cells without their unit in the count (looser: the
    attached unit column printed).
    """
    people = [f"P{1 + (row % 2000):05d}" for row in range(20_000)]
    once = random.Random(11)
    attached_values = {person: 200 + round(once.gauss(97, 2)) for person in people}
    for attached in (False, True):
        draw = random.Random(5)
        unit_lines = ["x,patient_id"]
        bare_lines = ["x,patient_id"]
        for person in people:
            value = (
                attached_values[person] if attached else 200 + round(draw.gauss(97, 2))
            )
            if person in ("P00007", "P00008"):
                value = 266
            unit_lines += [f"{value}.5 mg,{person}"]
            bare_lines += [f"{value}.5,{person}"]
        for typed in (["--identifier", "patient_id"], []):
            assert _profile(tmp_path, unit_lines, "--measurement", "x", *typed) == 0
            unit = _block(tmp_path, "x")
            assert _profile(tmp_path, bare_lines, "--measurement", "x", *typed) == 0
            bare = _block(tmp_path, "x")
            assert _publishes(unit, 266.5, "266.5 mg") == _publishes(bare, 266.5, "266.5"), (attached, typed)
            assert (unit["role"] == taxonomy.ROLE_AFFIXED) == (bare["role"] in _NUMBER_ROLES), (attached, typed)
            if unit["role"] == taxonomy.ROLE_AFFIXED:
                assert _numeric_facts(unit) == _numeric_facts(bare), (attached, typed)
            # The unattached column prints its 20-row minimum, as its bare
            # numbers do; the attached one prints nothing of the two people.
            assert _publishes(unit, 266.5, "266.5 mg") == (not attached), (attached, typed)


# The roles a column of bare numbers is read as, beside the unit
# column's `affixed_number` (plan P4-D443's parity).
_NUMBER_ROLES = (taxonomy.ROLE_COUNT, taxonomy.ROLE_CONTINUOUS)
# What a block publishes about its unit or its reading, set aside when a
# unit column is compared with its bare numbers (plan P4-D443).
_AFFIX_OWN = (
    "affix_", "detection_evidence", "n_affixed", "n_core_", "n_numeric",
    "n_not_numeric", "role", "statistical_type", "number_spellings", "remarks",
    "all_whole_numbers",
)


def _numeric_facts(block: "dict[str, object]") -> "dict[str, object]":
    """A block's published facts, those about its unit and reading set aside (plan P4-D443)."""
    return {
        key: value
        for key, value in block.items()
        if not any(key.startswith(word) for word in _AFFIX_OWN)
    }


def _publishes(block: object, number: float, cell: str) -> bool:
    """Whether a block holds ``number`` as a value leaf, or ``cell`` as a text leaf or key."""
    if isinstance(block, dict):
        return any(f"{key}" == cell or _publishes(value, number, cell) for key, value in block.items())
    if isinstance(block, list):
        return any(_publishes(item, number, cell) for item in block)
    if isinstance(block, bool) or block is None:
        return False
    if isinstance(block, (int, float)):
        return float(block) == number
    return f"{block}" == cell


def test_a_written_form_below_the_floor_keeps_the_labels(tmp_path: pathlib.Path) -> None:
    """(a) undeclared: one `96.0%` among whole percentages keeps the labels and is put Q-UNIT.

    Skeptic 1 item 4: a form fewer cells than the floor write is counted
    into the commonest form, and the twin of the column read as numbers
    missed the forms census (validate exit 3) where the labels passed.
    Every value here is held by 60 rows; the one spelling `96.0%` is the
    level below the floor. Red on the mutant without
    `taxonomy._written_forms_clear`.
    """
    cells = _cycled([f"{value}%" for value in range(90, 100)], 60) + ["96.0%"]
    assert _profile(tmp_path, ["spo2"] + cells) == 0
    assert _block(tmp_path, "spo2")["role"] == taxonomy.ROLE_CATEGORICAL
    assert [_offered(entry) for entry in _asked(tmp_path, "spo2")] == [
        [asking.ANSWER_KEEP, asking.ANSWER_MEASUREMENT, asking.ANSWER_CODE]
    ]


def test_q_unit_answered_keep_is_not_put_again(tmp_path: pathlib.Path) -> None:
    """(c) an answer given is not asked again: Q-UNIT answered `keep` stays answered.

    The orchestrator's LANE UN-1a RULINGS 1 (2) (plan P4-D408): round two
    puts nothing to the column and keeps the answer in `answered_before`;
    round three, handed round two's file, writes the same description
    and the same questions file. Red on the mutant that does not carry
    `keep` (Q-UNIT put again in round two).
    """
    cells = _cycled([f"{150 + level} cm" for level in range(20)], 30)
    lines = ["stature"] + cells
    assert _profile(tmp_path, lines) == 0
    _answer(tmp_path, "stature", asking.ANSWER_KEEP)
    answers = tmp_path / "t-questions.json"
    assert _profile(tmp_path, lines, "--answers", f"{answers}") == 0
    assert _asked(tmp_path, "stature") == []
    second = json.loads(answers.read_text(encoding="utf-8"))
    kept = [entry for entry in second.get("answered_before", []) if entry["column"] == "stature"]
    assert [entry["your_answer"] for entry in kept] == [asking.ANSWER_KEEP]
    described = (tmp_path / "t-profile.json").read_text(encoding="utf-8")
    assert _profile(tmp_path, lines, "--answers", f"{answers}") == 0
    assert _asked(tmp_path, "stature") == []
    assert json.loads(answers.read_text(encoding="utf-8")) == second
    assert (tmp_path / "t-profile.json").read_text(encoding="utf-8") == described


def test_a_day_of_a_month_is_put_no_unit_question(tmp_path: pathlib.Path) -> None:
    """(c) `12 Jan` is a day of a month, not an amount in the unit `Jan`: Q-UNIT is not put.

    Skeptic 1 item 9. Red on the mutant without `taxonomy._a_calendar_word`
    in `taxonomy.reads_as_a_unit`.
    """
    cells = _cycled([f"{day} {month}" for day in range(1, 6) for month in ("Jan", "Feb")], 60)
    assert _profile(tmp_path, ["seen"] + cells) == 0
    assert _block(tmp_path, "seen")["role"] == taxonomy.ROLE_CATEGORICAL
    assert _asked(tmp_path, "seen") == []


def test_a_lab_flag_is_never_a_unit(tmp_path: pathlib.Path) -> None:
    """(a) and (c): `4.4 H` is a value marked high, never 4.4 in the unit `H`.

    The orchestrator's LANE UN-1a RULINGS 2 (3), on skeptic 1's item 5:
    the battery's `s3_two_readings_fit` (`5.1` beside `4.4 H`) moved from
    labels to `affixed_number`. A lone flag (H, L, HH, LL, A, N, `*`, in
    brackets too) is no unit: neither stand-aside (i) nor question Q-UNIT
    reads it, so the column keeps the reading it had before plan P4-D438.
    `4 h` (hours, in lower case) is still a unit. Red on the mutant
    without `taxonomy._a_flag`.
    """
    for flag in ("H", "L", "HH", "LL", "A", "N", "*", "(H)"):
        assert not taxonomy._suffix_wrapped(_reading([("", f" {flag}"), ("", "")])), flag
    assert taxonomy._suffix_wrapped(_reading([("", " h"), ("", "")]))
    draw = random.Random(5)
    cells = [f"{draw.gauss(5, 1):.1f}" for _ in range(570)] + [f"{draw.gauss(5, 1):.1f} H" for _ in range(30)]
    draw.shuffle(cells)
    assert not taxonomy.reads_as_a_unit(cells, taxonomy.Settings(small_cell_floor=11))
    assert _profile(tmp_path, ["result"] + cells) == 0
    assert _block(tmp_path, "result")["role"] != taxonomy.ROLE_AFFIXED
    unit_answers = [asking.ANSWER_KEEP, asking.ANSWER_MEASUREMENT, asking.ANSWER_CODE]
    assert unit_answers not in [_offered(entry) for entry in _asked(tmp_path, "result")]


def test_the_terminal_types_measurement_apart_from_keep(monkeypatch: pytest.MonkeyPatch) -> None:
    """(c) at the keyboard, Q-UNIT shows `[1]` keep and `[m]` measurement, and `m` declares it.

    Codex item 2: both answers were shown as `[1]`, and `measurement`
    recorded no declaration, so the column stayed labels. Red on the
    mutant that keeps key 1 for `measurement` beside `keep`, and on the
    mutant that records no declaration for it.
    """
    question = asking.Question(
        "stature", taxonomy.ROLE_CATEGORICAL, asking.BECAUSE_UNIT, "shape",
        asking._unit_choices(taxonomy.ROLE_CATEGORICAL, 11), asking.ANSWER_KEEP,
    )
    shown = cli._the_question(question, 1, 1)
    assert "[1] labels to keep" in shown and "[m] amounts in that unit" in shown
    said: "list[str]" = []
    monkeypatch.setattr(cli, "_say", lambda text: said.append(text))
    for typed, measured in (("m", ["stature"]), ("1", []), ("", [])):
        monkeypatch.setattr("builtins.input", lambda _prompt, typed=typed: typed)
        put = cli._put_the_questions([question])
        assert put is not None
        assert put[2] == measured, typed


def test_a_declared_decimal_comma_reads_every_cell() -> None:
    """(a) under `--decimal-comma`, `150,5 cm` is read as every cell's number, as `150.5 cm` is.

    Codex item 5: the all-cell check read the cores with the default
    grammar, so the declared column stayed labels where its point twin
    became numbers. Red on the mutant that reads the cores undeclared.
    """
    settings = taxonomy.Settings(small_cell_floor=11)
    for comma, cells in ((True, ["150,5 cm", "151,5 cm"] * 50), (False, ["150.5 cm", "151.5 cm"] * 50)):
        tally = taxonomy._tally(taxonomy._classify_all(cells, comma), len(cells), settings, comma)
        reading = taxonomy._affixed_reading(tally, comma)
        assert reading is not None, comma
        assert taxonomy._reads_every_cell(reading, tally), comma


def _driver() -> object:
    path = pathlib.Path(__file__).resolve().parents[1] / "tools" / "measurements" / "kpi_zoo_units.py"
    spec = importlib.util.spec_from_file_location("kpi_zoo_units_under_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_unit_kpi_emits_no_total_over_a_missing_twin(monkeypatch: pytest.MonkeyPatch) -> None:
    """K-HZ-09 is not emitted where a twin of the nine columns is missing.

    Codex item 6: a generation that failed returned normally with no bad
    cells, and the total silently left the column out (2,176 -> 1,598).
    A step that exited other than 0 is no measurement, and `main`
    refuses to emit a total over fewer than the nine columns. Red on the
    mutant that sums whatever was measured.
    """
    driver = _driver()
    assert not driver._completed({"steps": {"profile": {"exit": 0}, "generate": {"exit": 1}}})  # type: ignore[attr-defined]
    assert driver._completed({"steps": {"profile": {"exit": 0}, "generate": {"exit": 0}}})  # type: ignore[attr-defined]
    found = {
        "spo2": {"role": "affixed_number", "exact_list": False, "bad_cells": 0},
        "result": {"role": "categorical", "exact_list": False, "bad_cells": None},
    }
    monkeypatch.setattr(driver.kpi_rules, "guard_this_tree", lambda: "")  # type: ignore[attr-defined]
    monkeypatch.setattr(driver, "measure", lambda *_given: found)
    emitted: "list[object]" = []
    monkeypatch.setattr(driver.kpi_rules, "emit", lambda *given: emitted.append(given))  # type: ignore[attr-defined]
    monkeypatch.setattr("sys.argv", ["kpi_zoo_units.py", "--kpi"])
    with pytest.raises(SystemExit):
        driver.main()  # type: ignore[attr-defined]
    assert emitted == []
