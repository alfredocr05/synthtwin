"""`synthtwin check`: the five twin-versus-real checks in one word (lane TOOLS).

The checks (`synthtwin.twin_checks`) were reached only as `python -m
synthtwin.twin_checks REAL TWIN`, which needs a Python on the path: the
Windows ready folder's window binds the word `synthtwin` and nothing else,
so a physician there had no way to run them before a twin left. `synthtwin
check TABLE` runs them on the twin `synthtwin twin TABLE` wrote, finds it
where `twin` writes it, reads the person column from the files `twin` left
beside it, writes the report beside the twin, and ends in one plain line:
PASS or FAIL, with what to do. Each guard below is shown to be what holds
(a mutant, named in the test's docstring, turns it red).
"""

from __future__ import annotations

import json
import pathlib
import runpy
import sys

import pytest

import test_checks_read_the_answers as claims
import test_twin_checks as tables
from synthtwin import cli, results, twin_checks


def _folder_twin(tmp_path: pathlib.Path, real: "list[list[str]]", twin: "list[list[str]]") -> "tuple[pathlib.Path, pathlib.Path]":
    """The real table `visits.csv` and its twin where `synthtwin twin` writes it: `visits-synthtwin/visits-twin.csv`."""
    table = pathlib.Path(tables._write(tmp_path / "visits.csv", real))
    folder = tmp_path / "visits-synthtwin"
    folder.mkdir()
    tables._write(folder / "visits-twin.csv", twin)
    return table, folder


def _check(capsys: pytest.CaptureFixture[str], *words: str) -> "tuple[int, str, str]":
    code = cli.main(["check", *words], small_tables_refused=False)
    said = capsys.readouterr()
    return code, said.out, said.err


@pytest.fixture(scope="module")
def real() -> "list[list[str]]":
    return tables._visits(1, "P", tables.RELATIVES_REAL)


@pytest.fixture(scope="module")
def clean() -> "list[list[str]]":
    return tables._visits(2, "Q", tables.RELATIVES_TWIN)


def test_a_clean_twin_passes_in_one_word(tmp_path: pathlib.Path, capsys, real, clean) -> None:
    """The twin in the twin's folder is found, checked and passed: exit 0, the report beside the twin, PASS in plain words.

    Red on: the twin looked for beside the table instead of in its folder
    (no twin found, exit 1).
    """
    table, folder = _folder_twin(tmp_path, real, clean)
    code, out, err = _check(capsys, str(table))
    assert code == 0, err
    report = folder / "visits-twin-checks.txt"
    assert report.is_file()
    assert report.read_text(encoding="utf-8") in out
    assert "RESULT: PASS. The twin passed all five checks." in out
    for code_said in ("C1", "C2", "C3", "C4", "C5"):
        assert f"PASS  {code_said}: " in out
    assert sorted(path.name for path in folder.iterdir()) == ["visits-twin-checks.txt", "visits-twin.csv"]


def test_a_copied_twin_fails_and_the_person_is_told_what_to_do(tmp_path: pathlib.Path, capsys, real, clean) -> None:
    """A twin holding real rows fails C1 (and the copies' patients C3): exit 3, FAIL named by check, the twin kept where it is.

    The closing lines say not to let the twin leave, and teach the two
    commands to type: a new twin with another seed, then the check again.
    Red on: `results.exit_code` reading `check`'s miss as 0 (exit 0).
    """
    twin = tables._copy(clean)
    twin[: len(real) // 2] = tables._copy(real[: len(real) // 2])
    table, folder = _folder_twin(tmp_path, real, twin)
    code, out, _ = _check(capsys, str(table))
    assert code == 3
    assert "RESULT: FAIL (C1" in out and "Do not let this twin leave this computer." in out
    assert "FAIL  C1: no twin row is a copy of a real row" in out
    taught = [line.strip() for line in out.splitlines() if line.strip().startswith("synthtwin ")]
    assert taught[-2].startswith("synthtwin twin ") and taught[-2].endswith(" --replace --seed 2")
    assert taught[-1].startswith("synthtwin check ")
    assert (folder / "visits-twin.csv").is_file(), "the twin is never moved"


def test_no_value_of_either_table_is_shown(tmp_path: pathlib.Path, capsys, real, clean) -> None:
    """The screen and the report carry counts and verdicts: no key, name, record number or stamp of either table."""
    twin = tables._copy(clean)
    twin[0] = list(real[0])
    table, folder = _folder_twin(tmp_path, real, twin)
    _, out, _ = _check(capsys, str(table))
    shown = out + (folder / "visits-twin-checks.txt").read_text(encoding="utf-8")
    for rows in (real, twin):
        for row in rows[:200]:
            for place in (0, 1, 7):
                assert row[place] not in shown, row[place]
    for name in tables.RELATIVES_REAL + tables.RELATIVES_TWIN:
        assert name not in shown


def test_the_person_column_comes_from_the_twins_folder(tmp_path: pathlib.Path, capsys, real, clean) -> None:
    """The person column the twin was built with is read from the folder's description, bound by its questions file.

    The table's person column is named `who`, which no reader of names
    takes for a person; `twin --person who` wrote it into the description's
    settings. With the two files beside the twin, C3 reads patients by
    `who`; with the questions file naming another table, nothing is taken
    from either file. Red on: `twin_checks.person_answered` returning ""
    (the report says no person column).
    """
    header = ["who"] + tables.HEADER[1:]
    table = pathlib.Path(tables._write(tmp_path / "visits.csv", real, header))
    folder = tmp_path / "visits-synthtwin"
    folder.mkdir()
    tables._write(folder / "visits-twin.csv", clean, header)
    (folder / "visits-profile.json").write_text(json.dumps({"settings": {"person_columns": ["who"]}}), encoding="utf-8", newline="\n")
    questions = folder / "visits-questions.json"
    questions.write_text(json.dumps({"table": "visits.csv"}), encoding="utf-8", newline="\n")
    code, out, err = _check(capsys, str(table))
    assert code == 0, err
    assert "(person column: who)" in out
    questions.write_text(json.dumps({"table": "another.csv"}), encoding="utf-8", newline="\n")
    _, out, _ = _check(capsys, str(table))
    assert "(no person column)" in out
    # Typed, the column is taken whatever the folder holds.
    _, out, _ = _check(capsys, str(table), "--person", "who")
    assert "(person column: who)" in out


def test_person_answered_reads_the_subject_answer_and_trusts_only_this_tables_file(tmp_path: pathlib.Path) -> None:
    """The questions file's answer to who each row is about, where the description names no one person; nothing from another table's file."""
    questions = tmp_path / "t-questions.json"
    description = tmp_path / "t-profile.json"
    entry = {"rows_per_person": {"your_answer": "  who  "}}
    questions.write_text(json.dumps({"table": "t.csv", "between_columns": entry}), encoding="utf-8", newline="\n")
    assert twin_checks.person_answered(f"{questions}", f"{description}", "t.csv") == "who"
    description.write_text(json.dumps({"settings": {"person_columns": ["pid"]}}), encoding="utf-8", newline="\n")
    assert twin_checks.person_answered(f"{questions}", f"{description}", "t.csv") == "pid"
    description.write_text(json.dumps({"settings": {"person_columns": ["pid", "other"]}}), encoding="utf-8", newline="\n")
    assert twin_checks.person_answered(f"{questions}", f"{description}", "t.csv") == "who"
    assert twin_checks.person_answered(f"{questions}", f"{description}", "u.csv") == ""
    questions.write_text("not json", encoding="utf-8", newline="\n")
    assert twin_checks.person_answered(f"{questions}", f"{description}", "t.csv") == ""
    assert twin_checks.person_answered(f"{tmp_path / 'none.json'}", f"{description}", "t.csv") == ""


def test_the_place_answers_of_the_twins_folder_are_read(tmp_path: pathlib.Path, capsys) -> None:
    """A place-named column answered `code` in the questions file `twin` left in its folder is no identifier to C4.

    The claims table of lane ZOO-Y (two-figure codes of settings of care
    in a column named `place_code`): read by its name, C4 counts every twin
    code as a copied identifier and the check fails; with the answer `code`
    in the twin's folder -- where `synthtwin twin` keeps it, never beside
    the table -- it passes. Red on: `_run_check` not handing the folder's
    questions file to the checks (C4 fails, exit 3).
    """
    folder = tmp_path / "claims-synthtwin"
    folder.mkdir()
    table = pathlib.Path(claims._write(tmp_path / "claims.csv", claims._claims(1, "P")))
    claims._write(folder / "claims-twin.csv", claims._claims(2, "T"))
    code, out, _ = _check(capsys, str(table))
    assert code == 3 and "FAIL  C4:" in out, "premise: read by its name, the codes are counted as identifiers"
    claims._answered(folder, [("place_code", "code"), ("place_code", "no")])
    assert twin_checks.place_names_answered(f"{table}", claims.HEADER) == (), "nothing beside the table"
    assert twin_checks.place_names_answered(f"{table}", claims.HEADER, f"{folder / 'claims-questions.json'}") == (
        "place_code",
    )
    code, out, err = _check(capsys, str(table))
    assert code == 0, err
    assert "PASS  C4:" in out


def test_no_twin_is_a_refusal_in_words(tmp_path: pathlib.Path, capsys, real) -> None:
    """No twin where `twin` writes it: exit 1, the place named, what to type; nothing written."""
    table = pathlib.Path(tables._write(tmp_path / "visits.csv", real))
    code, _, err = _check(capsys, str(table))
    assert code == 1
    assert "There is no twin at" in err and "visits-synthtwin" in err and "synthtwin twin" in err
    assert sorted(path.name for path in tmp_path.iterdir()) == ["visits.csv"]


def test_the_twin_named_and_the_folder_named(tmp_path: pathlib.Path, capsys, real, clean) -> None:
    """`--twin` names the twin to check; `--out-dir` the folder `twin --out-dir` wrote into."""
    table = pathlib.Path(tables._write(tmp_path / "visits.csv", real))
    other = tmp_path / "mine"
    other.mkdir()
    tables._write(other / "visits-twin.csv", clean)
    code, _, err = _check(capsys, str(table), "--out-dir", str(other))
    assert code == 0, err
    assert (other / "visits-twin-checks.txt").is_file()
    named = tables._write(tmp_path / "elsewhere.csv", clean)
    code, _, err = _check(capsys, str(table), "--twin", named)
    assert code == 0, err
    assert (tmp_path / "elsewhere-checks.txt").is_file()


def test_the_result_and_the_exit_status(tmp_path: pathlib.Path, real, clean) -> None:
    """The run's result: command `check`, the tally, the report as a file written; `missed` exits 3."""
    table, folder = _folder_twin(tmp_path, real, clean)
    done = cli.run(["check", str(table)], small_tables_refused=False)
    assert done.command == results.CHECK and done.verdict == results.NO_MISS
    assert done.tally == (("checks", 5), ("passed", 5), ("failed", 0))
    assert [(item.kind, pathlib.Path(item.path).name) for item in done.files] == [
        (results.FILE_CHECKS_REPORT, "visits-twin-checks.txt")
    ]
    assert results.exit_code(results.Result(command=results.CHECK, verdict=results.MISSED)) == 3


def test_the_command_line_and_the_page(capsys) -> None:
    """`check` with no table is refused (2) with the words to type; `help check` and `check --help` show its page."""
    code = cli.main(["check"])
    assert code == 2
    assert "synthtwin check my-table.csv" in capsys.readouterr().err
    assert cli.main(["help", "check"]) == 0
    page = capsys.readouterr().out
    assert page == cli.command_page("check")
    assert page.startswith("usage: synthtwin check TABLE [options]")
    assert len(page.splitlines()) <= 60 and max(len(line) for line in page.splitlines()) <= 79
    for option in ("--out-dir FOLDER", "--twin PATH", "--person COLUMN", "--identifier COLUMN", "--first-row"):
        assert option in page
    assert cli.main(["check", "--help"]) == 0
    assert capsys.readouterr().out == page
    assert cli.main(["help"]) == 0
    assert "synthtwin check my-table.csv" in capsys.readouterr().out


def test_python_dash_m_synthtwin_check_is_the_ready_folders_route(monkeypatch, tmp_path: pathlib.Path) -> None:
    """The Windows ready folder's `synthtwin` runs `python -m synthtwin` (`synthtwin.bat`): `check` reaches the checks there."""
    seen: "list[object]" = []

    def standing_in(argv: "list[str] | None" = None) -> int:
        seen.append(argv)
        return 0

    monkeypatch.setattr(cli, "main", standing_in)
    monkeypatch.setattr(sys, "argv", ["synthtwin", "check", "my-table.csv"])
    monkeypatch.delitem(sys.modules, "synthtwin.__main__", raising=False)
    with pytest.raises(SystemExit) as stopped:
        runpy.run_module("synthtwin", run_name="__main__", alter_sys=True)
    assert stopped.value.code == 0
    assert seen in ([None], [["check", "my-table.csv"]])
    folder_bat = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "windows" / "synthtwin.bat"
    assert "-m synthtwin %*" in folder_bat.read_text(encoding="utf-8")


def test_every_twin_ends_by_teaching_the_check(tmp_path: pathlib.Path, real) -> None:
    """`synthtwin twin` ends with the one word that checks its twin, on the person's own folder; the run's next command
    is left as it was (the check is taught, not chained).

    Red on: the closing lines of `cli._twin_ended` without the check.
    """
    table = pathlib.Path(tables._write(tmp_path / "visits.csv", real))
    screen: "list[tuple[str, str]]" = []
    done = cli.run(["twin", str(table), "--person", "patient_id"], screen=screen)
    said = "".join(text for _stream, text in screen)
    assert done.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    lines = [line for line in said.splitlines() if line.strip()]
    # ...the last lines, but for the note on which shell a quoted value is written for, where the folder's path
    # holds a space (release 37's landing: the suite's own folder does, and the note follows the command).
    if lines[-1].strip().startswith("(each value "):
        lines = lines[:-1]
    assert lines[-2] == "Before the twin leaves this computer, run the five twin-versus-real checks on it:"
    assert lines[-1].strip().startswith("synthtwin check ") and lines[-1].strip().rstrip("'").endswith("visits.csv")
    assert done.next_command is None or done.next_command.purpose != results.CHECK
    named = tmp_path / "mine"
    named.mkdir()
    screen = []
    cli.run(["twin", str(table), "--out-dir", str(named), "--person", "patient_id"], screen=screen)
    shown = [line for line in "".join(text for _stream, text in screen).splitlines() if line.strip()]
    last = shown[-2] if shown[-1].strip().startswith("(each value ") else shown[-1]
    assert "--out-dir" in last and last.strip().startswith("synthtwin check ")
