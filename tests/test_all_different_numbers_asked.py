"""P4-D436 (lane HX5): whole numbers each on one row, or in sequence, asked the identifier question.

WHAT WAS MEASURED (lane E0c's strict twin scan, planning-notes/work-2026-10/
wave6/E0c-repair2.md, 'NEW' item 1, on ccebc947): the zoo's
`titled_report.report_ref` -- `RPT` and six figures, one a row, counting up
-- was read as an affixed number and asked nothing. Its description
published the run's percentile ladder and its twin wrote the sequence
again: 598 of 600 real references at 600 rows, 19,998 of 20,000 at 20,000.
The same tree published plain figures counting up across a power of ten
(`99701` up, read as a count: 97 real values in the description and 598 twin
cells at 600 rows) and `MRN` and six figures on about four rows in three (50
real record numbers as rungs), each with nothing asked: every route of the
person rule (plan P4-D401) asks from two rows a value on average, and the
width question asks plain figures of one width only.

THE RULE (`asking._whole_numbers_each_on_one_row`). A column read as a
count, a measurement, numbers too large for a float, an affixed number or
numbers beside labels, whose present cells are words and placeholders (set
aside whatever their share) and whole numbers -- figures alone, or one to
six letters, an optional `-`, `_` or `#`, and figures -- filling the floor's
cells and standing on fewer than two rows a value, and every one different,
or running in sequence under one opening, or letters and five figures or
more, is put P4-D401's identifier question (`keep`, `code`, `identifier`)
where no other question is put to it, and held whole until answered. A
cell carrying a decimal, a unit or any mark after its figures takes the
column out, and so do values that repeat on two rows each or more.

Each case runs the product's own command line, nobody at the keyboard (the
library's small-table switch off, so the 600-row legs stand below the
command's floor: identifier rules hold at every size), and each is red on
the mutant its docstring or the lane's mutants log names (planning-notes/
work-2026-10/wave6/HX5/mutants.log).
"""

from __future__ import annotations

import json
import pathlib
import random

import pytest

from synthtwin import asking, cli, taxonomy

import health_zoo as zoo
import unanswered_identifier_shapes as shapes

_ROWS = 600
_FLOOR_ROWS = 20000

# CHANCE, NOT COPY (stated in plan P4-D436; owner lane ID-ROOM, plan
# P4-D432, whose guarantee covers held blocks by the orchestrator's ruling
# 2 of 2026-10-25). A held column publishes no value, so its twin writes
# made-up record numbers in the column's layouts, and where the real
# values fill a layout's room densely -- 600 or 20,000 references counting
# up among a million six-figure spellings -- a made-up one can carry the
# figures of a real one. The count of such cells is about the share of the
# room the real values fill times the rows; a twin that copies the column
# (the mutant: the rule switched off) writes nearly every row real. The
# bound is a twentieth of the rows: far above chance on every shape here,
# far below a copy.
_CHANCE_SHARE = 20


def _check_held(seen: "dict[str, object]", kind: str, rows: int) -> None:
    """0 real values or fragments published, held as record numbers, asked once."""
    assert seen["profile_exit"] == 0 and seen["generate_exit"] == 0
    if kind not in shapes.VALIDATION_LIMITS:
        assert seen["validate_exit"] == 0, seen
    assert seen["description_values"] == 0, seen
    assert seen["description_fragments"] == 0, seen
    twin = seen["twin_cells"]
    assert isinstance(twin, int) and twin * _CHANCE_SHARE <= rows, seen
    asked = seen["asked"]
    assert isinstance(asked, list) and len(asked) == 1, seen
    assert asking.ANSWER_IDENTIFIER in asked[0]
    assert seen["role"] == taxonomy.ROLE_IDENTIFIER
    assert seen["evidence"] == taxonomy.rendered(taxonomy.EVIDENCE_UNANSWERED_IDENTITY, ())
    assert "COLUMNS HELD BACK UNTIL YOU ANSWER" in f"{seen['screen']}"
    assert seen["forced_identifiers"] == [kind]


@pytest.mark.parametrize("kind", shapes.ONE_A_ROW)
def test_a_column_of_whole_numbers_each_on_one_row_is_held(
    tmp_path: pathlib.Path, kind: str
) -> None:
    """Every shape at 600 rows: nothing real published, held, asked once.

    Red on the mutant "the rule switched off" (`_whole_numbers_each_on_one_row`
    false): `refseq` publishes 97 references and its twin writes 598.
    """
    _check_held(shapes.run(tmp_path, kind, _ROWS), kind, _ROWS)


@pytest.mark.parametrize("kind", ("refseq", "seqcross", "refmrn"))
def test_at_the_floor_size_the_column_is_held(tmp_path: pathlib.Path, kind: str) -> None:
    """The live shape and the plain run at 20,000 rows, the owner's table floor.

    Red on the mutant "the rule switched off": `refseq` publishes its ladder
    and the twin writes 19,998 of 20,000 real references.
    """
    _check_held(shapes.run(tmp_path, kind, _FLOOR_ROWS), kind, _FLOOR_ROWS)


def test_the_question_is_the_identifier_question_with_keep_first(
    tmp_path: pathlib.Path,
) -> None:
    """`keep`, `code`, `identifier`, the reason named, and no value in its words."""
    shapes.run(tmp_path, "refseq", _ROWS)
    entries = _asked_of(tmp_path, "refseq")
    assert len(entries) == 1
    entry = entries[0]
    assert [choice["answer"] for choice in entry["answers_you_can_give"]] == [
        asking.ANSWER_KEEP, asking.ANSWER_CODE, asking.ANSWER_IDENTIFIER,
    ]
    words = json.dumps(entry)
    assert "RPT" not in words and "3000" not in words
    assert "every one is different" in words
    screen = (tmp_path / "refseq_long-profile.txt").read_text(encoding="utf-8")
    assert "RPT3" not in screen


@pytest.mark.parametrize("kind", ("refseq", "seqcross", "refmrn"))
def test_the_indexed_count_is_the_pairwise_count(tmp_path: pathlib.Path, kind: str) -> None:
    """`shapes.count_real` read through its index counts what the pairwise search counts.

    The index is what K-S3-64 reads at 20,000 rows and more (20,000 real
    values by 20,000 twin cells); here both read the same 600-row run, and
    a copy of the column written as the twin, so every count is non-zero.
    """
    shapes.run(tmp_path, kind, _ROWS)
    (tmp_path / "again").mkdir()
    _table, real = shapes.write_table(tmp_path / "again", kind, _ROWS)
    texts = [(tmp_path / f"{kind}_long-{page}").read_text(encoding="utf-8")
             for page in ("profile.json", "profile.txt", "questions.json")]
    with open(tmp_path / f"{kind}_long-twin.csv", encoding="utf-8") as handle:
        cells = [line.split(",")[0] for line in handle.read().splitlines()[1:]]
    for twin in (cells, real, [f"x{value}." for value in real]):
        published = texts + [f"p50 {real[3]} and {real[5][:5]}"]
        pairwise = shapes.count_real(real, published, twin, indexed=False)
        assert shapes.count_real(real, published, twin, indexed=True) == pairwise
    assert shapes.count_real(real, texts, real, indexed=True)["twin_cells"] == len(real)


# -- the reach: what is asked, and what is not --------------------------------

_DRAW = random.Random(20261025)


def _run(start: int, count: int, opening: str = "") -> "list[str]":
    return [f"{opening}{start + place}" for place in range(count)]


_REACHED = {
    "the live shape": _run(300001, 600, "RPT"),
    "references at random": [f"RPT{value}" for value in _DRAW.sample(range(100000, 1000000), 600)],
    "row numbers": _run(1, 600),
    "plain across a power of ten": _run(99701, 600),
    "plain at random": [f"{value}" for value in _DRAW.sample(range(100000, 10000000), 600)],
    "a run with one number twice": _run(99701, 599) + ["99701"],
    "MRN on four rows in three": [f"MRN{value}" for value in _DRAW.sample(range(100000, 1000000), 450)]
    + [f"MRN{value}" for value in _DRAW.sample(range(100000, 1000000), 150)] * 1,
    "letters, a mark and figures": _run(10001, 600, "ACC-"),
    "beside words and placeholders": _run(99701, 400) + ["UNKNOWN"] * 150 + ["-1"] * 50,
    "written as whole decimals": [f"{value}.0" for value in range(99701, 100301)],
    "the floor's cells exactly": _run(99701, 11),
}

_NOT_REACHED = {
    "readings with decimals": [f"{value / 100:.2f}" for value in _DRAW.sample(range(1000, 99999), 600)],
    "a unit after the figures": [f"{value} mg" for value in _DRAW.sample(range(1000, 99999), 600)],
    "a currency sign": [f"${value}" for value in _DRAW.sample(range(1000, 99999), 600)],
    "a letter after the figures": [f"{value}A" for value in range(300001, 300601)],
    "ages that repeat": [f"{_DRAW.randint(18, 90)}" for _row in range(600)],
    "years that repeat": [f"{_DRAW.randint(2000, 2024)}" for _row in range(600)],
    "a run on two rows a value": [f"{99701 + place // 2}" for place in range(600)],
    "fewer than the floor's cells": _run(99701, 10),
    "a negative of four figures": _run(99701, 599) + ["-1234"],
    "seven letters before the figures": _run(300001, 600, "REPORTX"),
    "one value alone": ["12345"] * 600,
}


@pytest.mark.parametrize("label", sorted(_REACHED))
def test_the_rule_reaches(label: str) -> None:
    """Each column the rule asks, read as a count (the role is read apart)."""
    assert asking._whole_numbers_each_on_one_row(_REACHED[label], taxonomy.ROLE_COUNT)


@pytest.mark.parametrize("label", sorted(_NOT_REACHED))
def test_the_rule_leaves_measurements(label: str) -> None:
    """True measurements, repeats, units and decimals are not asked (the owner's principle)."""
    assert not asking._whole_numbers_each_on_one_row(_NOT_REACHED[label], taxonomy.ROLE_COUNT)


@pytest.mark.parametrize(
    "role",
    (taxonomy.ROLE_CATEGORICAL, taxonomy.ROLE_TEXT, taxonomy.ROLE_IDENTIFIER,
     taxonomy.ROLE_DATETIME, taxonomy.ROLE_CLOCK, taxonomy.ROLE_LONG_TAIL),
)
def test_the_rule_reads_only_the_number_roles(role: str) -> None:
    """Labels publish no value held by one row; dates and clock times are not keys."""
    assert not asking._whole_numbers_each_on_one_row(_REACHED["the live shape"], role)


# -- never a second question ---------------------------------------------------


def test_a_column_of_one_width_keeps_the_width_question(tmp_path: pathlib.Path) -> None:
    """Plain figures of one width, one a row, are the width question's, as before."""
    table = tmp_path / "width.csv"
    table.write_text(
        "width,value\n" + "".join(f"{300001 + row},{row % 7}\n" for row in range(_ROWS)),
        encoding="utf-8", newline="\n",
    )
    _profile(table, tmp_path)
    entries = _asked_of_file(tmp_path / "width-questions.json", "width")
    assert len(entries) == 1 and _saw(entries[0], asking._FIGURES_ALL_ONE_WIDTH)


def test_a_repeating_key_keeps_the_person_question(tmp_path: pathlib.Path) -> None:
    """A key on two rows a value or more is the person rule's, as before."""
    shapes.run(tmp_path, "randkey", _ROWS)
    entries = _asked_of(tmp_path, "randkey")
    assert len(entries) == 1 and "different value(s) over" in f"{entries[0]['what_synthtwin_saw']}"


# -- the answers give back the description as each reading writes it ---------


@pytest.mark.parametrize(
    ("answer", "typed"),
    [
        (asking.ANSWER_KEEP, []),
        (asking.ANSWER_CODE, ["--code", "refseq"]),
        (asking.ANSWER_IDENTIFIER, ["--identifier", "refseq"]),
    ],
)
def test_each_answer_gives_the_description_of_its_reading(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, answer: str, typed: "list[str]"
) -> None:
    """Byte for byte the description the rule-off tree writes with that reading typed."""
    shapes.run(tmp_path, "refseq", _ROWS)
    questions = json.loads((tmp_path / "refseq_long-questions.json").read_text(encoding="utf-8"))
    for entry in questions["asked"]:
        if entry["column"] == "refseq":
            entry["your_answer"] = answer
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(questions), encoding="utf-8", newline="\n")
    answered = tmp_path / "answered"
    answered.mkdir()
    with shapes.nobody_at_the_keyboard():
        assert cli.main(["profile", f"{tmp_path / 'refseq_long.csv'}", "--out-dir", f"{answered}",
                         "--answers", f"{answers}"], small_tables_refused=False) == 0
    before = tmp_path / "before"
    before.mkdir()
    with monkeypatch.context() as patched:
        patched.setattr(asking, "_whole_numbers_each_on_one_row", lambda present, role: False)
        with shapes.nobody_at_the_keyboard():
            assert cli.main(["profile", f"{tmp_path / 'refseq_long.csv'}", "--out-dir",
                             f"{before}"] + typed, small_tables_refused=False) == 0
    for page in ("refseq_long-profile.json", "refseq_long-profile.txt"):
        assert (answered / page).read_bytes() == (before / page).read_bytes(), page
    block = [one for one in json.loads((answered / "refseq_long-profile.json").read_text(
        encoding="utf-8"))["columns"] if one["name"] == "refseq"][0]
    if answer == asking.ANSWER_KEEP:
        assert block["role"] == taxonomy.ROLE_AFFIXED
    elif answer == asking.ANSWER_IDENTIFIER:
        assert block["role"] == taxonomy.ROLE_IDENTIFIER


# -- the zoo's live column ------------------------------------------------------


def test_the_zoo_report_reference_is_held_unanswered(tmp_path: pathlib.Path) -> None:
    """The zoo's `titled_report`, unanswered: report_ref asked, and no reference anywhere.

    Its title rows are not answered either, so the run reads its header where
    it can; the reference column is asked wherever it stands.
    """
    table = [one for one in zoo.TABLES if one.name == "titled_report"][0]
    header, rows = table.build(_ROWS, 20261016)
    names = ["report_ref", "ward", "admitted", "went_home"]
    assert header == names
    source = tmp_path / "titled_report.csv"
    source.write_text(
        ",".join(names) + "\n" + "".join(",".join(row) + "\n" for row in rows),
        encoding="utf-8", newline="\n",
    )
    _profile(source, tmp_path)
    real = [row[0] for row in rows]
    texts = [(tmp_path / f"titled_report-{page}").read_text(encoding="utf-8")
             for page in ("profile.json", "profile.txt", "questions.json")]
    with shapes.nobody_at_the_keyboard():
        assert cli.main(["generate", f"{tmp_path / 'titled_report-profile.json'}", "--out-dir",
                         f"{tmp_path}", "--seed", "0", "--replace"]) == 0
    with open(tmp_path / "titled_report-twin.csv", encoding="utf-8") as handle:
        cells = [line.split(",")[0] for line in handle.read().splitlines()[1:]]
    counted = shapes.count_real(real, texts, cells)
    assert counted["description_values"] == 0 and counted["description_fragments"] == 0, counted
    assert counted["twin_cells"] * _CHANCE_SHARE <= _ROWS, counted
    entries = _asked_of_file(tmp_path / "titled_report-questions.json", "report_ref")
    assert len(entries) == 1 and _saw(entries[0], asking._EACH_ON_ONE_ROW_OPENING)


# -- helpers -------------------------------------------------------------------


def _profile(table: pathlib.Path, folder: pathlib.Path) -> None:
    with shapes.nobody_at_the_keyboard():
        assert cli.main(["profile", f"{table}", "--out-dir", f"{folder}", "--replace"],
                        small_tables_refused=False) == 0


def _saw(entry: "dict[str, object]", opening: str) -> bool:
    """Whether what the entry says synthtwin saw opens with these words."""
    return f"{entry['what_synthtwin_saw']}".startswith(opening)


def _asked_of_file(path: pathlib.Path, column: str) -> "list[dict[str, object]]":
    asked = json.loads(path.read_text(encoding="utf-8"))["asked"]
    return [entry for entry in asked if entry["column"] == column]


def _asked_of(folder: pathlib.Path, kind: str, stem: str = "") -> "list[dict[str, object]]":
    return _asked_of_file(folder / f"{stem or kind + '_long'}-questions.json", kind)
