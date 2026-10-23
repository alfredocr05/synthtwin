"""The floor of 11 is a minimum: `--smallest-group` raises it, never lowers it.

THE OWNER'S ANSWER (Fri 2026-10-23, plan P4-D426). Asked whether a
user should still be able to lower the smallest published group from
11 -- which `--smallest-group` allowed down to 1, with a warning on
every page while the twin was still written -- when decision D7 lets a
twin be shared freely because nothing in it can break HIPAA, the owner
chose "Only raise it". So:

1. Every command refuses `--smallest-group` under 11 -- or text that is
   no number -- under every spelling argparse takes for the option, in
   plain words, with code 2 (the code of every other unusable option),
   writing nothing. 11 and more behave as before.
2. `generate` and `validate` refuse, with code 1 and nothing written, a
   description recording a floor under 11, which a version before the
   plan could write (HIPAA first: a twin built from it would hold every
   group it names, however small).
3. Lower floors stay reachable ONLY through `cli.main`'s keyword-only
   `lowered_floor`, which the suite reaches through
   `tests/lowered_floor.py`; no environment variable, questions file or
   settings file reaches it, and a fresh interpreter -- the installed
   command -- has it off.

Each refusal is checked again on the MUTANT that lets it through, and
the check has to fail there: a test that cannot fail proves nothing.
"""

import ast
import json
import os
import pathlib
import re
import subprocess
import sys

import pytest

import fixtures
import lowered_floor
from synthtwin import cli, contract, parsing

_SRC = pathlib.Path(cli.__file__).resolve().parent
_OPTION = "--smallest-group"
_REFUSED_BELOW = ("10", "1", "0", "-1")


def _table(folder: pathlib.Path) -> pathlib.Path:
    folder.mkdir(parents=True, exist_ok=True)
    return fixtures.write(folder, "clinic.csv", fixtures.every_role_table())


def _listing(folder: pathlib.Path) -> "list[str]":
    return sorted(
        f"{path.relative_to(folder)}" for path in folder.rglob("*")
    )


def _run(argv: "list[str]") -> int:
    """`cli.main` as a typed command runs it: its code, SystemExit included."""
    try:
        return cli.main(argv)
    except SystemExit as stop:
        return 0 if stop.code is None else int(f"{stop.code}")


@pytest.fixture(scope="module")
def spellings() -> "list[str]":
    """Every spelling argparse resolves to `--smallest-group`, read off the help.

    argparse takes any unambiguous prefix of a long option, so the list
    is every prefix of the option's name that no other option on the
    help screen shares; each is tried below also written with `=`.
    """
    import contextlib
    import io

    shown = io.StringIO()
    with contextlib.redirect_stdout(shown), pytest.raises(SystemExit):
        cli.main(["--help"])
    usage = shown.getvalue().split("\n\n")[0]
    others = {
        word
        for word in re.findall(r"--[a-z][a-z-]*", usage)
        if word != _OPTION
    }
    assert _OPTION in shown.getvalue() and len(others) >= 10, others
    found: "list[str]" = []
    for end in range(3, len(_OPTION) + 1):
        prefix = _OPTION[:end]
        if any(other.startswith(prefix) for other in others):
            continue
        found += [prefix]
    assert found[-1] == _OPTION and "--sm" in found, found
    return found


# -- 1. typed under 11: refused, nothing written, on every command --------


@pytest.mark.parametrize("given", _REFUSED_BELOW)
def test_a_number_under_eleven_is_refused_writing_nothing(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str], given: str
) -> None:
    table = _table(tmp_path / "in")
    before = _listing(tmp_path)
    code = _run(["profile", f"{table}", _OPTION, given])
    said = capsys.readouterr()
    assert code == 2, (code, said.err)
    assert "raised but not lowered" in said.err and given in said.err
    assert "least it can be is 11" in said.err
    assert _listing(tmp_path) == before
    assert said.out == ""


def test_text_that_is_no_number_is_refused_in_plain_words(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = _table(tmp_path / "in")
    before = _listing(tmp_path)
    assert _run(["profile", f"{table}", _OPTION, "abc"]) == 2
    said = capsys.readouterr().err
    assert "must be a whole number written in figures" in said
    assert "invalid int value" not in said
    assert _listing(tmp_path) == before


def test_every_spelling_of_the_option_is_refused(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    spellings: "list[str]",
) -> None:
    table = _table(tmp_path / "in")
    before = _listing(tmp_path)
    tried = 0
    for spelling in spellings:
        for argv in (
            ["profile", f"{table}", spelling, "5"],
            ["profile", f"{table}", f"{spelling}=5"],
            ["profile", f"{table}", spelling, "11", spelling, "1"],
        ):
            assert _run(argv) == 2, argv
            assert "raised but not lowered" in capsys.readouterr().err, argv
            tried += 1
    assert tried == 3 * len(spellings) and tried >= 30
    assert _listing(tmp_path) == before


@pytest.mark.parametrize("command", ["generate", "validate", "doctor"])
def test_every_command_refuses_it(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str], command: str
) -> None:
    table = _table(tmp_path / "in")
    assert lowered_floor.main(["profile", f"{table}"]) == 0
    capsys.readouterr()
    described = tmp_path / "in" / "clinic-profile.json"
    named = f"{table}" if command == "doctor" else f"{described}"
    before = _listing(tmp_path)
    for given in ("10", "1", "abc"):
        assert _run([command, named, _OPTION, given]) == 2
        assert "smallest group size" in capsys.readouterr().err
    assert _run(["--version", _OPTION, "1"]) == 2
    assert _listing(tmp_path) == before


@pytest.mark.parametrize("given", ["11", "20"])
def test_eleven_and_more_are_taken_as_before(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str], given: str
) -> None:
    typed = _table(tmp_path / "typed")
    assert _run(["profile", f"{typed}", _OPTION, given]) == 0
    capsys.readouterr()
    written = json.loads(
        (tmp_path / "typed" / "clinic-profile.json").read_text(encoding="utf-8")
    )
    assert written["settings"]["small_cell_floor"] == int(given)
    described = tmp_path / "typed" / "clinic-profile.json"
    assert _run(["generate", f"{described}"]) == 0
    assert _run(["validate", f"{described}"]) == 0
    capsys.readouterr()
    if given == "11":
        # TYPING THE DEFAULT WRITES THE SAME BYTES AS NOT TYPING IT.
        plain = _table(tmp_path / "plain")
        assert _run(["profile", f"{plain}"]) == 0
        for name in ("clinic-profile.json", "clinic-profile.txt"):
            assert (tmp_path / "plain" / name).read_bytes() == (
                tmp_path / "typed" / name
            ).read_bytes(), name


# -- the mutants: each refusal above, let through, must turn the check red -


def _let_through(typed: str) -> int:
    """The mutant: the number as typed, under 11 or not; junk read as 11."""
    try:
        return int(typed)
    except ValueError:
        return parsing.DEFAULT_SMALL_CELL_FLOOR


@pytest.mark.parametrize("given", _REFUSED_BELOW + ("abc",))
def test_each_refusal_is_red_on_the_mutant_that_lets_it_through(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    given: str,
) -> None:
    monkeypatch.setattr(cli, "_typed_floor", _let_through)
    table = _table(tmp_path / "in")
    before = _listing(tmp_path)
    code = _run(["profile", f"{table}", _OPTION, given])
    said = capsys.readouterr().err
    refused_in_plain_words = (
        code == 2
        and ("raised but not lowered" in said or "whole number written" in said)
        and _listing(tmp_path) == before
    )
    assert not refused_in_plain_words, (
        f"{given} is still refused with the check let through, so the "
        f"refusal test above proves nothing"
    )


def test_the_spellings_are_red_on_the_mutant(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    spellings: "list[str]",
) -> None:
    monkeypatch.setattr(cli, "_typed_floor", _let_through)
    table = _table(tmp_path / "in")
    for spelling in (spellings[0], spellings[len(spellings) // 2]):
        assert _run(["profile", f"{table}", f"{spelling}=5", "--replace"]) == 0
        capsys.readouterr()


# -- 2. a description written under a lowered floor -----------------------


@pytest.mark.parametrize("floor", [1, 5, 10])
def test_a_description_under_eleven_is_not_built_from_or_checked_against(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str], floor: int
) -> None:
    table = _table(tmp_path / "in")
    assert cli.main(["profile", f"{table}"], lowered_floor=floor) == 0
    capsys.readouterr()
    described = tmp_path / "in" / "clinic-profile.json"
    assert contract.load_profile(f"{described}").settings.small_cell_floor == floor
    before = _listing(tmp_path)
    for command, words in (
        ("generate", "will not build a twin from it"),
        ("validate", "will not check a file against it"),
    ):
        argv = [command, f"{described}"]
        if command == "validate":
            argv += ["--twin", f"{table}"]
        assert _run(argv) == 1
        said = capsys.readouterr()
        assert words in said.err and f"lowered to {floor}" in said.err
        assert "Describe the table again" in said.err
        assert said.out == ""
        assert _listing(tmp_path) == before
    # The internal setting reads it, as every run did before the plan.
    assert cli.main(["generate", f"{described}"], lowered_floor=1) == 0
    capsys.readouterr()


def test_the_description_refusal_is_red_on_the_mutant(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    table = _table(tmp_path / "in")
    assert cli.main(["profile", f"{table}"], lowered_floor=2) == 0
    described = tmp_path / "in" / "clinic-profile.json"
    monkeypatch.setattr(
        cli, "_description_floor_refused", lambda *arguments: False
    )
    assert _run(["generate", f"{described}"]) == 0
    assert _run(["validate", f"{described}"]) == 0
    capsys.readouterr()


# -- 3. the internal setting, and nothing else, lowers the floor -----------


def test_the_internal_setting_is_keyword_only_and_off_by_default() -> None:
    import inspect

    found = inspect.signature(cli.main).parameters["lowered_floor"]
    assert found.kind is inspect.Parameter.KEYWORD_ONLY
    assert found.default is None


def test_no_environment_variable_reaches_the_floor(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in (
        "SYNTHTWIN_SMALLEST_GROUP",
        "SYNTHTWIN_LOWERED_FLOOR",
        "SYNTHTWIN_FLOOR",
        "SMALLEST_GROUP",
        "LOWERED_FLOOR",
        "SMALL_CELL_FLOOR",
    ):
        monkeypatch.setenv(name, "1")
    table = _table(tmp_path / "in")
    assert _run(["profile", f"{table}"]) == 0
    capsys.readouterr()
    written = json.loads(
        (tmp_path / "in" / "clinic-profile.json").read_text(encoding="utf-8")
    )
    assert written["settings"]["small_cell_floor"] == 11
    assert _run(["profile", f"{table}", _OPTION, "1", "--replace"]) == 2
    capsys.readouterr()


def test_no_module_of_the_product_reads_the_environment() -> None:
    """The static half: no product module names the environment at all."""
    readers: "list[str]" = []
    for path in sorted(_SRC.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            named = (
                node.attr
                if isinstance(node, ast.Attribute)
                else node.id
                if isinstance(node, ast.Name)
                else ""
            )
            if named in ("environ", "getenv", "environb", "putenv"):
                readers += [f"{path.name}:{node.lineno}"]
    assert readers == []


def test_nothing_in_the_product_passes_the_internal_setting() -> None:
    """`lowered_floor` is read where `main` hands it on, and set nowhere."""
    passing: "list[str]" = []
    for path in sorted(_SRC.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and any(
                keyword.arg == "lowered_floor" for keyword in node.keywords
            ):
                passing += [f"{path.name}:{node.lineno}"]
    assert passing == []
    main_module = (_SRC / "__main__.py").read_text(encoding="utf-8")
    assert "lowered_floor" not in main_module


def test_no_questions_file_reaches_the_floor(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = _table(tmp_path / "in")
    assert _run(["profile", f"{table}"]) == 0
    capsys.readouterr()
    folder = tmp_path / "in"
    asked = json.loads((folder / "clinic-questions.json").read_text(encoding="utf-8"))
    for key in ("smallest_group", "small_cell_floor", "lowered_floor"):
        asked[key] = 1
    asked["settings"] = {"small_cell_floor": 1, "smallest_group": 1}
    answers = folder / "answers.json"
    answers.write_text(json.dumps(asked), encoding="utf-8", newline="\n")
    out = tmp_path / "out"
    out.mkdir()
    code = _run(
        ["profile", f"{table}", "--answers", f"{answers}", "--out-dir", f"{out}"]
    )
    capsys.readouterr()
    # The keys are not a questions file's, so they are not read at all.
    assert code == 0
    written = json.loads((out / "clinic-profile.json").read_text(encoding="utf-8"))
    assert written["settings"]["small_cell_floor"] == 11


def test_no_settings_file_reaches_the_floor(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    table = _table(tmp_path / "in")
    for folder in (tmp_path / "in", tmp_path):
        (folder / "synthtwin.toml").write_text(
            "smallest_group = 1\nsmall_cell_floor = 1\nlowered_floor = 1\n",
            encoding="utf-8",
        )
        (folder / "pyproject.toml").write_text(
            "[tool.synthtwin]\nsmallest_group = 1\nlowered_floor = 1\n",
            encoding="utf-8",
        )
        (folder / "setup.cfg").write_text(
            "[synthtwin]\nsmallest_group = 1\n", encoding="utf-8"
        )
        (folder / ".synthtwinrc").write_text(
            "--smallest-group 1\n", encoding="utf-8"
        )
        (folder / "synthtwin.json").write_text(
            '{"smallest_group": 1, "lowered_floor": 1}', encoding="utf-8"
        )
    monkeypatch.chdir(tmp_path)
    assert _run(["profile", f"{table}"]) == 0
    capsys.readouterr()
    written = json.loads(
        (tmp_path / "in" / "clinic-profile.json").read_text(encoding="utf-8")
    )
    assert written["settings"]["small_cell_floor"] == 11


def test_a_fresh_interpreter_has_the_setting_off(tmp_path: pathlib.Path) -> None:
    """The installed command is `python -m synthtwin`: it refuses 5 and 0."""
    table = _table(tmp_path / "in")
    before = _listing(tmp_path)
    environment = dict(os.environ)
    searched = [f"{_SRC.parent}"] + [
        entry for entry in sys.path if entry and entry != f"{_SRC.parent}"
    ]
    environment["PYTHONPATH"] = os.pathsep.join(searched)
    environment["SYNTHTWIN_LOWERED_FLOOR"] = "1"
    for given in ("5", "0"):
        finished = subprocess.run(
            [sys.executable, "-m", "synthtwin", "profile", f"{table}", _OPTION, given],
            capture_output=True,
            text=True,
            env=environment,
            cwd=f"{tmp_path}",
            timeout=300,
            check=False,
        )
        assert finished.returncode == 2, finished.stderr
        assert "raised but not lowered" in finished.stderr
    assert _listing(tmp_path) == before


# -- 4. what the screens say ------------------------------------------------


def test_the_help_says_the_floor_is_raised_and_never_lowered(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit):
        cli.main(["--help"])
    shown = " ".join(re.sub(r"-\n\s+", "-", capsys.readouterr().out).split())
    assert "never lowered" in shown
    assert "--smallest-group 20" in shown
    assert "--smallest-group 1 names" not in shown
    assert "smaller number is let through" not in shown


def test_the_bridge_moves_only_floors_under_eleven() -> None:
    moved = lowered_floor._moved
    assert moved(["profile", "t.csv", _OPTION, "5"]) == (["profile", "t.csv"], 5)
    assert moved(["profile", "t.csv", f"{_OPTION}=2"]) == (["profile", "t.csv"], 2)
    assert moved(["profile", "t.csv", _OPTION, "20"]) == (
        ["profile", "t.csv", _OPTION, "20"],
        None,
    )
    assert moved(["profile", "t.csv"]) == (["profile", "t.csv"], None)
