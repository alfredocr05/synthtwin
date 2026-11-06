"""Yes-no letters are codes only as one pair in one case (the orchestrator's LANE I4m RULINGS 27 (1)).

The independent verify of batch 4o's fix round, finding 1: the round read each of
`y`, `n`, `t` and `f` as a code alone, so a column of first initials holding only
`Y`, `N` and `T` (shape B6: 1,000 declared people on 20 rows each, `F` for two of
them) was published with no question put, `N`, `T` and `Y` with their counts, and
its twin wrote 19,960 cells equal to a real initial at 20,000 rows, where 591b356f
and 2af926ce held the column. Now a published level of one of these letters counts
as a code only where every such level of its column belongs to one pair written in
one case (`Y` and `N`, `y` and `n`, `T` and `F`, `t` and `f`); otherwise the column
keeps its hold and its Safe Harbor question until it is answered, and `no`, or the
column declared a code, releases it as before. A flag of one pair with a rare third
level is still pooled with no question. Each case is red on fcd01166 or on the
mutant its comment names. The shapes are invented.
"""

from __future__ import annotations

import pathlib

import pytest
import released_hold_cases as cases

from synthtwin import profile, reading, taxonomy

LETTERS = ("Y", "N", "T", "F", "U", "y", "n", "t", "f", "u")


def _letters_in(text: str) -> "list[str]":
    return [letter for letter in LETTERS if f'"{letter}"' in text]


def test_first_initials_of_yes_no_letters_are_held_and_asked(tmp_path: pathlib.Path) -> None:
    # Shape B6 through the command at 20,000 rows, unanswered: the question put, no
    # initial in the description, 0 twin cells equal to or merging with a real one
    # (no question, `N`, `T` and `Y` published and 19,960 and 19,960 on fcd01166).
    # Mutant: the pair check removed (each letter a code alone).
    found = cases.run(tmp_path / "unanswered", cases.yes_no_letters_as_initials())
    assert found["exits"] == [0, 0], found["exits"]
    assert [sorted(offered) for offered in found["put"][0]] == [["no", "yes"]], found["put"]
    assert found["block"]["role"] == "identifier" and "levels" not in found["block"], found["block"]  # type: ignore[index, operator]
    assert _letters_in(found["text"]) == []  # type: ignore[arg-type]
    assert cases.equal_cells(found["real"], found["twin"]) == 0  # type: ignore[arg-type]
    assert cases.merged_cells(found["real"], found["twin"]) == 0  # type: ignore[arg-type]


def test_a_yes_no_flag_with_a_rare_third_level_is_released_unasked(tmp_path: pathlib.Path) -> None:
    # `Y` and `N` by person beside `U` five people hold, through the command at
    # 20,000 rows: one pair in one case, so `U` is pooled and never named, and `Y`
    # and `N` keep their counts with no question put (plan P4-D453 as lane PL
    # wrote it). Mutant: every column of yes-no letters held.
    found = cases.run(tmp_path / "flag", cases.a_yes_no_flag_with_a_rare_third_level())
    assert found["exits"] == [0, 0], found["exits"]
    assert found["put"] == [[]], found["put"]
    assert found["block"]["role"] == "categorical", found["block"]  # type: ignore[index]
    levels = {entry["label"]: entry["count"] for entry in found["block"]["levels"]}  # type: ignore[index]
    assert levels == {"n": 9960, "y": 9940}, levels
    assert '"U"' not in found["text"] and '"u"' not in found["text"]  # type: ignore[operator]


def test_only_one_pair_in_one_case_reads_as_codes() -> None:
    # The rule on its own, the case read off the published spellings. Mutants: the
    # pair check removed (`{y, n, t}` and `{y, f}` read as codes); the case not
    # read (`Y` beside `n` read as codes).
    def reads(spellings: "dict[str, list[str]]") -> bool:
        return taxonomy.levels_read_as_codes("flag", sorted(spellings), len(spellings), spellings)

    for spellings in (
        {"y": ["Y"], "n": ["N"]},
        {"y": ["y"], "n": ["n"]},
        {"t": ["T"], "f": ["F"]},
        {"t": ["t"], "f": ["f"]},
        {"y": ["Y"]},
        {"y": ["Y"], "n": ["N"], "1": ["1"], "yes": ["yes"]},
    ):
        assert reads(spellings), spellings
    for spellings in (
        {"y": ["Y"], "n": ["n"]},
        {"y": ["Y"], "n": ["N"], "t": ["T"]},
        {"y": ["Y"], "f": ["F"]},
        {"y": ["Y", "y"], "n": ["N"]},
        {"t": ["T"], "f": ["F"], "y": ["Y"], "n": ["N"]},
    ):
        assert not reads(spellings), spellings
    assert taxonomy.levels_read_as_codes("flag", ["n", "y"], 2)
    assert not taxonomy.levels_read_as_codes("flag", ["n", "t", "y"], 3)


def _flag_described(kept: "tuple[str, ...]", tmp_path: pathlib.Path) -> "tuple[dict[str, object], list[str]]":
    """Three hundred declared people on four rows: five hold `U`, the others ``kept``'s letters by place."""
    lines = ["patient_key,flag"]
    for who in range(300):
        for _row in range(4):
            lines += [f"{100000 + who},{'U' if who < 5 else kept[who % len(kept)]}"]
    path = tmp_path / "flag.csv"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    held: "list[str]" = []
    reasons: "dict[str, str]" = {}
    document = profile.build_document(
        reading.read_table(f"{path}"),
        taxonomy.Settings(),
        ["patient_key"],
        subjects=["patient_key"],
        five_figures=held,
        harbor_reasons=reasons,
    )
    block = [one for one in document["columns"] if one["name"] == "flag"][0]  # type: ignore[union-attr, index]
    return block, [f"{name}:{reasons[name]}" for name in held]  # type: ignore[return-value]


@pytest.mark.parametrize(
    ("kept", "held"),
    [(("Y", "N"), False), (("t", "f"), False), (("Y", "n"), True), (("Y", "N", "T"), True), (("Y", "F"), True)],
)
def test_the_profiler_reads_the_case_the_levels_are_written_in(
    kept: "tuple[str, ...]", held: bool, tmp_path: pathlib.Path
) -> None:
    # The library's size (1,200 rows, a test device; the command's cases are above):
    # a held column is put the question of a column whose values cannot tell.
    # Mutant: the published spellings not handed to the rule (`Y` beside `n`
    # released).
    block, asked = _flag_described(kept, tmp_path)
    if held:
        assert block["role"] == "identifier" and "levels" not in block, block
        assert asked == [f"flag:{taxonomy.HELD_LEVELS_OF_FEW_PEOPLE}"], asked
    else:
        assert block["role"] == "categorical" and asked == [], (block, asked)
        assert sorted(entry["label"] for entry in block["levels"]) == sorted(letter.lower() for letter in kept)  # type: ignore[union-attr]
