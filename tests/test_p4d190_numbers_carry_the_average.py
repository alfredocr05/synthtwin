"""The numbers of a free-text column carry what the length walk could not (P4-D190).

THE REPRODUCTION. The final skeptic's workbook column of sixty numbers,
thirty-nine codes `txtNN` and one boolean, beside a label column: at
floors of one and five its twin wrote the boolean as a made-up word and
missed `length.mean` (3.0 asked, 2.96 found). A later repair stopped
that one shape publishing its forms and hid the miss; the same column
with two or three truth values still missed it on every seed, in a
workbook and in the text file of the same cells alike. Every number
stood at its own shortest length, every code wore its form's length,
and the two made-up words carried the published ends -- so the walk
toward the average had no group left to move.

The walk now moves the numbers' own lengths where nothing else can move.
Every test is a round trip -- describe, generate, describe the twin,
validate the twin AND the real table at exit 0 -- and recounts the
twin's average length itself.
"""

import pathlib

import pytest

from tests.test_files_review_repairs import _book, _cell, _held, _rows, _trip


def _values(truths: int) -> "list[str]":
    return (
        [f"{index + 1}" for index in range(60)]
        + [f"txt{index}" for index in range(40 - truths)]
        + ["TRUE"] * truths
    )


def _workbook(truths: int) -> bytes:
    """The skeptic's column: numbers, codes and `truths` boolean cells."""
    strings = ["value", "other"] + [f"txt{index}" for index in range(40 - truths)] + ["x", "y"]
    grid = {1: [_cell("A1", "0", "s"), _cell("B1", "1", "s")]}
    for place in range(100):
        number = 2 + place
        if place < 60:
            cell = _cell(f"A{number}", f"{place + 1}")
        elif place < 100 - truths:
            cell = _cell(f"A{number}", f"{2 + place - 60}", "s")
        else:
            cell = _cell(f"A{number}", "1", "b")
        other = _cell(f"B{number}", f"{2 + (40 - truths) + place % 2}", "s")
        grid[number] = [cell, other]
    return _book([("Data", _rows(grid))], strings)


def _text(truths: int) -> bytes:
    lines = ["value,other"] + [
        f"{value},{'xy'[index % 2]}" for index, value in enumerate(_values(truths))
    ]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _average(result: "dict[str, object]") -> "tuple[float, float]":
    published = result["document"]["columns"][0]["length"]["mean"]
    again = result["again"]["columns"][0]["length"]["mean"]
    return published, again


@pytest.mark.parametrize("truths, floor", [(1, "1"), (1, "5"), (2, "5"), (3, "5")])
def test_the_workbook_twin_meets_its_average_length(
    tmp_path: pathlib.Path, truths: int, floor: str
) -> None:
    for seed in (0, 4):
        result = _trip(tmp_path / f"s{seed}", "book", _workbook(truths),
                       ("--smallest-group", floor), seed=seed)
        _held(result)
        published, again = _average(result)
        assert abs(published - again) <= 0.02 + 1e-9, (published, again)


@pytest.mark.parametrize("truths, floor", [(2, "1"), (2, "5"), (3, "1"), (5, "5")])
def test_the_text_file_twin_meets_its_average_length(
    tmp_path: pathlib.Path, truths: int, floor: str
) -> None:
    for seed in (0, 4):
        result = _trip(tmp_path / f"s{seed}", "text", _text(truths),
                       ("--smallest-group", floor), suffix=".csv", seed=seed)
        _held(result)
        published, again = _average(result)
        assert abs(published - again) <= 0.02 + 1e-9, (published, again)
    assert result["document"]["columns"][0]["role"] == "free_text"
    assert result["document"]["columns"][0]["shape_forms"], "the forms must be named"
