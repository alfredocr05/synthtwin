"""Lane TOOLS: `synthtwin profile` at a keyboard asks in the one round `twin` asks in, and its scripted runs are as before.

Lane Q-FLOW put `twin`'s questions in ONE ROUND, grouped by kind, before
anything is written (the owner's decisions of 2026-11-23); `profile`, the
expert's command, kept its rounds after the files, so the same table asked
the same person two ways. Now `profile` with somebody at the keyboard puts
the same round (`cli._the_one_round_on`): the same prompts in the same
order, the same last screen, nothing written until it is answered, and the
same three files `twin`'s profile step writes. Nobody at the keyboard -- a
script, a pipe, `--answers` handed in by a script -- nothing is asked and
the files are byte for byte the files the rounds after the files wrote.

The suite's conftest pins `profile`'s rounds after the files for every
other case (`cli._PROFILE_ONE_ROUND`); each case here turns the one round
back on. The cohort is the suite's seeded table ST1 at 4,000 rows (the
suite's floor switch is off). Each guarded behaviour is red on the mutant
its docstring names.
"""

from __future__ import annotations

import pathlib
import shutil

import pytest

import analyst_tables
import test_q_flow_one_round as flow
from synthtwin import cli, results

ROWS = 4000
_WRITTEN = ("cohort-profile.json", "cohort-profile.txt", "cohort-questions.json")


@pytest.fixture(autouse=True)
def _the_one_round_on(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "_PROFILE_ONE_ROUND", True)


class _Beside(flow._Planned):
    """The planned keyboard of lane Q-FLOW, watching the three files `profile` writes beside the table."""

    def __getitem__(self, place):  # type: ignore[no-untyped-def]
        answer = super().__getitem__(place)
        if isinstance(place, int) and self.files_seen:
            self.files_seen[len(self.files_seen) - 1] = any((self.folder / name).exists() for name in _WRITTEN)
        return answer


def _cohort(folder: pathlib.Path) -> pathlib.Path:
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "cohort.csv"
    analyst_tables.write(table, "ST1", ROWS, 1)
    return table


def _profile(table: pathlib.Path, plan: "dict[str, str]", end_at: str = "") -> "tuple[results.Result, str, _Beside]":
    keyboard = _Beside(plan, table.parent, end_at)
    screen: "list[tuple[str, str]]" = []
    result = cli.run(["profile", f"{table}"], screen=screen, ask=keyboard)
    return result, "".join(text for _stream, text in screen), keyboard


def test_profile_asks_in_one_round_before_anything_is_written(tmp_path: pathlib.Path) -> None:
    """Enter at every prompt: no file of the run exists while a question is on screen, the last screen comes before
    the files, no round after them, and the three files are written once.

    MUTANT: `_the_one_round_on` reading `twin` alone (`_PROFILE_ONE_ROUND`
    False) -- the questions come after the files, in rounds of their own.
    """
    table = _cohort(tmp_path / "c")
    result, said, keyboard = _profile(table, {})
    assert result.verdict == results.NO_MISS, said[-2500:]
    assert keyboard.files_seen and not any(keyboard.files_seen), keyboard.files_seen
    assert all((table.parent / name).is_file() for name in _WRITTEN)
    assert "BEFORE ANYTHING IS WRITTEN" in said
    assert "MORE QUESTION(S), FROM THE QUESTIONS FILE" not in said
    assert said.count("These three files will be written") == 1
    assert said.index("BEFORE ANYTHING IS WRITTEN") < said.index("These three files will be written")


def test_profile_and_twin_put_the_same_round_and_write_the_same_description(tmp_path: pathlib.Path) -> None:
    """The same table and the same answers typed (crp released from the ages' cap): the same prompts in the same
    order, and the description `profile` writes is the one `twin`'s profile step writes, byte for byte.

    MUTANT: `_PROFILE_ONE_ROUND` False -- `profile` puts its questions one
    at a time after the files, and the prompts differ.
    """
    plan = {"AGES OVER 89": "crp"}
    alone = _cohort(tmp_path / "p")
    result, said, typed = _profile(alone, plan)
    assert result.verdict == results.NO_MISS, said[-2000:]
    journey = _cohort(tmp_path / "t")
    twin_result, twin_said, twin_typed = flow._twin(journey, plan)
    assert twin_result.verdict in (results.NO_MISS, results.MISSED), twin_said[-2000:]
    assert typed.heads == twin_typed.heads
    assert "crp (not an age)" in flow._section(said, "BEFORE ANYTHING IS WRITTEN")
    described = (alone.parent / "cohort-profile.json").read_bytes()
    assert described == (journey.parent / "cohort-synthtwin" / "cohort-profile.json").read_bytes()


def test_the_end_of_input_at_the_last_screen_writes_nothing(tmp_path: pathlib.Path) -> None:
    """Ctrl+D at the last screen: refused, and none of the three files is written."""
    table = _cohort(tmp_path / "s")
    result, said, _keyboard = _profile(table, {}, end_at="BEFORE ANYTHING IS WRITTEN")
    assert result.verdict == results.REFUSED, said[-2000:]
    assert not any((table.parent / name).exists() for name in _WRITTEN)


def test_a_scripted_profile_is_as_it_was(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Nobody at the keyboard: nothing is asked and the three files are the bytes the rounds after the files wrote --
    the scripted command, and the one handed its answers in a file, are unchanged by the one round."""
    table = _cohort(tmp_path / "one")
    screen: "list[tuple[str, str]]" = []
    assert cli.run(["profile", f"{table}"], screen=screen).verdict == results.NO_MISS
    assert "BEFORE ANYTHING IS WRITTEN" not in "".join(text for _stream, text in screen)
    other = tmp_path / "two"
    other.mkdir()
    shutil.copyfile(table, other / "cohort.csv")
    monkeypatch.setattr(cli, "_PROFILE_ONE_ROUND", False)
    assert cli.run(["profile", f"{other / 'cohort.csv'}"], screen=[]).verdict == results.NO_MISS
    for name in _WRITTEN:
        assert (table.parent / name).read_bytes() == (other / name).read_bytes(), name
    monkeypatch.setattr(cli, "_PROFILE_ONE_ROUND", True)
    answered = cli.run(["profile", f"{table}", "--answers", f"{table.parent / 'cohort-questions.json'}", "--replace"],
                       screen=[])
    assert answered.verdict == results.NO_MISS
