"""One or two letters settle nothing: such a column keeps its hold and its question (the orchestrator's LANE I4m RULINGS 21 (2)).

Codex's review of batch 4o, item 2: lane PL's rule read every value of one or two
characters as a code, so `kind`, holding the given names `Al`, `Bo`, `Jo` and `Li`
beside one person's `Ed`, was published with 5,000 rows a name and its twin wrote
19,980 name cells at 20,000 rows, no question put, where 591b356f and 2af926ce held
the column. Now one or two characters with a letter and no figure are no code by
their shape: the column is held and put the Safe Harbor question of a column whose
values cannot tell (plan P4-D453); `no`, or the column declared a code, releases it
as before. A figure beside a letter (`A1`), a mark, a whole number of at most three
figures and a yes-no pair written short (`Y`, `N`, `T`, `F`) stay codes. Each case is
red on 015d5003 and on the mutant its comment names.
"""

from __future__ import annotations

import pathlib

import released_hold_cases as cases

from synthtwin import taxonomy


def _names_in(text: str) -> "list[str]":
    found: "list[str]" = []
    for name in cases.NAMES + (cases.RARE_NAME,):
        for spelling in (name, name.lower(), name.upper()):
            if f'"{spelling}"' in text:
                found += [spelling]
    return found


def test_given_names_of_two_letters_are_held_and_asked(tmp_path: pathlib.Path) -> None:
    # Codex's case, unanswered: 0 names in the description and 0 in the twin
    # (Bo, Jo and Li 5,000 rows each and Al 4,980 published, 19,980 twin cells, on
    # 015d5003). Mutant: one or two characters read as a code whatever they hold.
    found = cases.run(tmp_path / "unanswered", cases.given_names())
    assert found["exits"] == [0, 0], found["exits"]
    assert [sorted(offered) for offered in found["put"][0]] == [["no", "yes"]], found["put"]
    assert found["block"]["role"] == "identifier" and "levels" not in found["block"], found["block"]  # type: ignore[index, operator]
    assert _names_in(found["text"]) == []  # type: ignore[arg-type]
    assert cases.equal_cells(found["real"], found["twin"]) == 0  # type: ignore[arg-type]
    assert cases.merged_cells(found["real"], found["twin"]) == 0  # type: ignore[arg-type]


def test_given_names_answered_no_are_released_as_before(tmp_path: pathlib.Path) -> None:
    # The answer is the person's: `no` publishes the names many people hold, the
    # rare one pooled and never named (plan P4-D453 as lane PL wrote it).
    found = cases.run(tmp_path / "no", cases.given_names(), ("no",))
    assert found["exits"] == [0, 0, 0], found["exits"]
    levels = {entry["label"]: entry["count"] for entry in found["block"]["levels"]}  # type: ignore[index]
    assert levels == {"al": 4980, "bo": 5000, "jo": 5000, "li": 5000}, levels
    assert '"Ed"' not in found["text"] and '"ed"' not in found["text"]  # type: ignore[operator]


def test_one_or_two_letters_are_no_code_by_their_shape() -> None:
    # Mutant: `_letters_without_a_figure` never true (the build's one or two
    # characters, whatever they hold).
    for labels in (["al", "bo", "jo", "li"], ["j."], ["a"], ["ab", "1"], ["é"]):
        assert not taxonomy.levels_read_as_codes("kind", labels, len(labels)), labels
    for labels in (["a1", "3c"], ["+", "-"], ["y", "n"], ["t", "f"], ["yes", "no"], ["05", "120"], ["1", "2"]):
        assert taxonomy.levels_read_as_codes("kind", labels, len(labels)), labels
