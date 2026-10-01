"""A record made of structured text names no column (plan P4-D241).

The final review of 2026-09-18 broke the owner's ruling 8 of 2026-09-17
on a shape the furniture rule cannot reach. A headerless export of 240
records whose first record is
`CASE-ZEBRA-471,Northfield Clinic 3,<0.10`, with a column of numbers
beside it, published that record as the three column names -- because
`<0.10` is not a number, so the numeric column read as EVIDENCE that the
first row is names, and `reading._names_evidence` is asked before the
furniture rule. The record's text then stood in the description four
times, in the plain summary six, in the twin's report four and verbatim
as row two of the twin, and the description said 239 rows where the file
holds 240. It happened with a title above, with a comment above, with
two titles, and with nothing above at all, so no rule that reads the
FILE's shape can close it.

THE FOURTH RECORD RULE closes it by reading the row itself: where every
value below it in one column wears the same silhouette -- runs of
letters and of figures collapsed, marks standing for themselves -- and
that silhouette is structured, and the first row's value wears it too,
the row is a record and the file is read as one (`reading._silhouette`,
`reading._shape_is_structured`, `reading._shares_the_shape_below`).

THE RULE IS BOUNDED BY WITNESSES THAT WERE RED WHEN IT WAS FIRST WRITTEN
WIDER, and each of them is here: `visit1` over `a1`, `region,2019` over
`r1` and `B10` over `B01` are all `A9` over `A9` and are ordinary headed
tables (review item P1-R6-F6), so fewer than two marks says nothing;
`Full Name` over `John Smith` is `A A` over `A A`, so letters and spaces
say nothing either.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import json
import pathlib
import random

import pytest

from synthtwin import parsing, reading
from tests.test_stage2_round_trip import _exit_of

_TOWNS = ("Eastcote", "Westbury", "Southgate", "Harlow", "Redmoor")
_WORDS = ("ALPHA", "BRAVO", "DELTA", "ECHO")


def _records(rows: int = 240) -> "list[str]":
    """The review's own export: a structured code, an address, a reading."""
    rng = random.Random(17)
    made = ["CASE-ZEBRA-471,Northfield Clinic 3,<0.10"]
    for index in range(1, rows):
        word = _WORDS[rng.randrange(len(_WORDS))]
        town = _TOWNS[index % len(_TOWNS)]
        made += [
            f"CASE-{word}-{100 + index:04d},"
            f"{town} Clinic {index},{30 + rng.randrange(60)}"
        ]
    return made


def _profile(folder: pathlib.Path, body: str, *flags: str) -> int:
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / "table.csv"
    target.write_text(body, encoding="utf-8", newline="")
    return _exit_of(
        ["profile", f"{target}", "--out-dir", f"{folder}", "--replace", *flags]
    )


def _document(folder: pathlib.Path) -> dict:
    return json.loads((folder / "table-profile.json").read_text("utf-8"))


# ------------------------------------------------- the silhouette itself


def test_a_silhouette_collapses_runs_and_keeps_marks() -> None:
    """The shape two values share, and the shapes they do not."""
    assert reading._silhouette("CASE-ZEBRA-471") == "A-A-9"
    assert reading._silhouette("CASE-ALPHA-0101") == "A-A-9"
    assert reading._silhouette("record_id") == "A_A"
    assert reading._silhouette("R001") == "A9"
    assert reading._silhouette("Northfield Clinic 3") == "A A 9"
    assert reading._silhouette("") == ""


def test_two_marks_and_something_that_is_not_a_word() -> None:
    """Both halves of the structure test, each with its own red witness."""
    assert reading._shape_is_structured("A-A-9")
    assert reading._shape_is_structured("A A 9")
    # ...and the four shapes that turned an ordinary headed table into a
    # headerless one when this was written wider.
    assert not reading._shape_is_structured("A9")
    assert not reading._shape_is_structured("A")
    assert not reading._shape_is_structured("A A")
    assert not reading._shape_is_structured("A A A")


# -------------------------------------------------- the review's own case


@pytest.mark.parametrize(
    "above",
    ["Cohort extract\n", "# an export\n", "Cohort extract\nunit 7\n", ""],
)
def test_a_structured_record_names_no_column(
    tmp_path: pathlib.Path, above: str
) -> None:
    """With furniture above it and with none, the record names nothing.

    The furniture rule cannot reach the last of these four, which is
    why the rule that closes them reads the ROW and not the file.
    """
    body = above + "\n".join(_records()) + "\n"
    assert _profile(tmp_path, body) == 0
    document = _document(tmp_path)
    assert [block["name"] for block in document["columns"]] == [
        "column_1",
        "column_2",
        "column_3",
    ]
    assert document["n_rows"] == 240
    source = document["source"]
    assert source["header_source"] == "generated"
    assert source["header_by_convention"] is False
    assert source["dialect"]["written_names"] == []


def test_no_text_of_that_record_reaches_any_file(
    tmp_path: pathlib.Path,
) -> None:
    """Round trip: describe, build, validate both, and read every byte.

    The description, the summary, the questions file, the twin and the
    twin's report are searched for the record's own words.
    """
    body = "Cohort extract\n" + "\n".join(_records()) + "\n"
    assert _profile(tmp_path, body, "--smallest-group", "11") == 0
    described = tmp_path / "table-profile.json"
    assert _exit_of(
        ["generate", f"{described}", "--out-dir", f"{tmp_path}", "--seed",
         "4", "--replace"]
    ) == 0
    for side, path in (
        ("twin", tmp_path / "table-twin.csv"), ("real", tmp_path / "table.csv")
    ):
        folder = tmp_path / side
        folder.mkdir()
        assert _exit_of(
            ["validate", f"{described}", "--twin", f"{path}", "--out-dir",
             f"{folder}", "--replace"]
        ) == 0
    for path in sorted(tmp_path.rglob("*")):
        if not path.is_file() or path.name == "table.csv":
            continue
        written = path.read_text("utf-8", errors="replace")
        for word in ("ZEBRA", "Northfield", "Cohort extract", "<0.10"):
            assert word not in written, f"{word} in {path.name}"


def test_the_questions_file_asks_and_quotes_no_cell(
    tmp_path: pathlib.Path,
) -> None:
    """The seventh declaration, with what was SEEN and no cell in it."""
    body = "\n".join(_records()) + "\n"
    assert _profile(tmp_path, body) == 0
    written = (tmp_path / "table-questions.json").read_text("utf-8")
    assert "first row" in written.lower()
    assert "same pattern of letters" in written
    for word in ("ZEBRA", "Northfield", "<0.10"):
        assert word not in written


def test_first_row_names_publishes_the_real_names(
    tmp_path: pathlib.Path,
) -> None:
    """The answer a person gives when the row IS the names."""
    body = "\n".join(_records()) + "\n"
    assert _profile(tmp_path, body, "--first-row", "names") == 0
    document = _document(tmp_path)
    assert [block["name"] for block in document["columns"]] == [
        "CASE-ZEBRA-471",
        "Northfield Clinic 3",
        "<0.10",
    ]
    assert document["n_rows"] == 239


# ------------------------------------- the headed tables that must stand


# EACH OF THEM WRITTEN AT THE POPULATION FLOOR (plan P4-D341):
# `synthtwin profile` refuses a table under it and writes nothing, and
# what every case here pins is how the FIRST ROW is read. The rows are
# not repeated to reach the floor -- three of these cases turn on their
# column's values being all DIFFERENT, and a repeated row would take
# that evidence away and settle the first row the other way. Each case's
# own generator is run to the floor instead, so every silhouette, every
# repetition and every witness below is the one the case was written
# with, and `n_rows` is derived from the rule rather than read off a
# run.
_ROWS = parsing.POPULATION_FLOOR

_HEADED = {
    "names that look like their own codes": ["visit1,visit2"]
    + [f"a{index % 9},b{index % 9}" for index in range(_ROWS)],
    "pivoted years over four-digit values": ["region,2019,2020"]
    + [f"place{index},1234,1567" for index in range(1, _ROWS + 1)],
    "a column whose name looks like a code": ["age,B10"]
    + [f"{30 + index},B{index:02d}" for index in range(1, _ROWS + 1)],
    "two words over two words": ["Full Name,Town"]
    + [
        f"{_WORDS[index % 4]} Smith,{_TOWNS[index % 5]}"
        for index in range(_ROWS)
    ],
    "a record number column under its own name": ["record_id,age"]
    + [f"R{index:03d},{30 + index}" for index in range(1, _ROWS + 1)],
    "a structured column under a real header": ["case_code,town,reading"]
    + [
        f"CASE-{_WORDS[index % 4]}-{100 + index:04d},"
        f"{_TOWNS[index % 5]} Clinic {index},{30 + index}"
        for index in range(1, _ROWS + 1)
    ],
}


@pytest.mark.parametrize("name", sorted(_HEADED))
def test_an_ordinary_headed_table_is_still_read_as_names(
    tmp_path: pathlib.Path, name: str
) -> None:
    """Six headed tables the rule must not touch, five of them measured red.

    The last is the one that matters most: the SAME structured column as
    the review's export, under a header of ordinary names. `case_code` is
    `A_A` and its values are `A-A-9`, so the row is not a record and the
    file is read exactly as its writer meant.
    """
    body = "\n".join(_HEADED[name]) + "\n"
    assert _profile(tmp_path, body) == 0
    document = _document(tmp_path)
    assert document["source"]["header_source"] == reading.HEADER_FROM_FILE
    assert document["n_rows"] == _ROWS
