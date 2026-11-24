"""Gate file of lane SPEED-2M, part 4: the keyed pairs' reading counted by pairs of codes, the same readings.

`profile._reads_as_a_key` read every row of a value column once for each
key column it was read under (a pass of about ten operations a row, the
description's largest single cost at 100,000 rows). Where the value
column's different cells and the key's common keys make at most 65,536
pairs, its counts are now the rows each pair of codes holds
(`arrays.joint_counts`), each count of the pass the sum of its pairs'
rows. The counts the decision reads, and so the readings, are the row
pass's, on keyed and unkeyed pairs, numbers, pairs of numbers, clocks,
dates, words, blanks, absent spellings and keys that are not common.
Mutants: a key that is not common counted as the first common key; a
number's scale step counted once a cell instead of once a row.

Every column here is drawn by the standard library's `random` from a
seed, at run time; nothing is committed.
"""

from __future__ import annotations

import random
import typing

import pytest

from synthtwin import profile

CELLS = ["", "NA", "Normal", "Room air", "abc 12", "14:32", "2:05 pm", "2024-01-05", "03/14/2024", "120/80",
         "118/76", "7", "12", "12.5", "0.25", "-3", "1e3", "250", "4.75"]


def _column(rows: int, seed: int, keyed: bool) -> "tuple[list[str], tuple[str, ...], list[str]]":
    """A key column's levels, its common keys, and a value column (typed by the key where ``keyed``)."""
    r = random.Random(f"keyed-pairs-{seed}")
    levels = ["glucose", "potassium", "sodium", "note", "", "rare-a", "rare-b"]
    common = ("glucose", "potassium", "sodium", "note")
    k_levels: "list[str]" = []
    v_cells: "list[str]" = []
    for _row in range(rows):
        level = r.choices(levels, weights=[30, 25, 20, 10, 8, 4, 3])[0]
        k_levels += [level]
        if keyed and level == "glucose":
            v_cells += [f"{r.randrange(60, 300)}"]
        elif keyed and level == "potassium":
            v_cells += [f"{r.randrange(30, 60) / 10:.1f}"]
        elif keyed and level == "sodium":
            v_cells += [f"{r.randrange(125, 150)}"]
        elif keyed and level == "note":
            v_cells += [r.choice(["Normal", "Room air", "abc 12"])]
        else:
            v_cells += [r.choice(CELLS) if r.random() < 0.6 else f"{r.randrange(0, 400)}"]
    return k_levels, common, v_cells


def _decided(monkeypatch: "pytest.MonkeyPatch", k_levels: "list[str]", common: "tuple[str, ...]",
             v_cells: "list[str]", coded: "profile.KeyedCodes | None") -> "tuple[object, list[object]]":
    seen: "list[object]" = []
    original = profile._keyed_decision

    def watched(*args: typing.Any) -> object:
        seen.append(args[6:])
        return original(*args)

    monkeypatch.setattr(profile, "_keyed_decision", watched)
    result = profile._reads_as_a_key(k_levels, common, v_cells, frozenset(["NA"]), {}, {}, coded)
    monkeypatch.setattr(profile, "_keyed_decision", original)
    return result, seen


@pytest.mark.parametrize("seed,rows,keyed", [(1, 3000, True), (2, 3000, False), (3, 500, True), (4, 8000, True),
                                             (5, 40, False)])
def test_the_pairs_counted_by_codes_are_the_row_pass(monkeypatch: "pytest.MonkeyPatch", seed: int, rows: int,
                                                     keyed: bool) -> None:
    k_levels, common, v_cells = _column(rows, seed, keyed)
    passed, by_rows = _decided(monkeypatch, k_levels, common, v_cells, None)
    coded = profile.keyed_codes(v_cells)
    coded.key_place = 0
    counted, by_pairs = _decided(monkeypatch, k_levels, common, v_cells, coded)
    assert by_rows and by_pairs and by_pairs == by_rows
    assert counted == passed
    if keyed and rows >= 3000:
        # ...and a column the key types reads as keyed, so the decision past the pass is reached too.
        assert passed is not None


def test_pairs_past_the_cells_a_count_holds_are_read_row_by_row(monkeypatch: "pytest.MonkeyPatch") -> None:
    k_levels, common, _cells = _column(20000, 6, False)
    v_cells = [f"{row}.5" for row in range(len(k_levels))]
    coded = profile.keyed_codes(v_cells)
    coded.key_place = 0
    assert profile._keyed_counts_by_pairs(coded, k_levels, {level: at for at, level in enumerate(common)}, len(common),
                                          frozenset(), {}, {}) is None
    passed, by_rows = _decided(monkeypatch, k_levels, common, v_cells, None)
    counted, by_pairs = _decided(monkeypatch, k_levels, common, v_cells, coded)
    assert counted == passed and by_pairs == by_rows
