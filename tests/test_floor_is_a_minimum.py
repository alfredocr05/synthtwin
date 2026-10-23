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
   `internal_smallest_group`, which the suite reaches through
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
    assert cli.main(["profile", f"{table}"], internal_smallest_group=floor) == 0
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
    assert cli.main(["generate", f"{described}"], internal_smallest_group=1) == 0
    capsys.readouterr()


def test_the_description_refusal_is_red_on_the_mutant(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    table = _table(tmp_path / "in")
    assert cli.main(["profile", f"{table}"], internal_smallest_group=2) == 0
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

    found = inspect.signature(cli.main).parameters["internal_smallest_group"]
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
        "SYNTHTWIN_INTERNAL_SMALLEST_GROUP",
        "INTERNAL_SMALLEST_GROUP",
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
    """`internal_smallest_group` is read where `main` hands it on, set nowhere."""
    passing: "list[str]" = []
    for path in sorted(_SRC.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and any(
                keyword.arg == "internal_smallest_group"
                for keyword in node.keywords
            ):
                passing += [f"{path.name}:{node.lineno}"]
    assert passing == []
    main_module = (_SRC / "__main__.py").read_text(encoding="utf-8")
    assert "internal_smallest_group" not in main_module


def test_no_questions_file_reaches_the_floor(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = _table(tmp_path / "in")
    assert _run(["profile", f"{table}"]) == 0
    capsys.readouterr()
    folder = tmp_path / "in"
    asked = json.loads((folder / "clinic-questions.json").read_text(encoding="utf-8"))
    for key in (
        "smallest_group",
        "small_cell_floor",
        "lowered_floor",
        "internal_smallest_group",
    ):
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
            "smallest_group = 1\nsmall_cell_floor = 1\nlowered_floor = 1\n"
            "internal_smallest_group = 1\n",
            encoding="utf-8",
            newline="\n",
        )
        (folder / "pyproject.toml").write_text(
            "[tool.synthtwin]\nsmallest_group = 1\nlowered_floor = 1\n"
            "internal_smallest_group = 1\n",
            encoding="utf-8",
            newline="\n",
        )
        (folder / "setup.cfg").write_text(
            "[synthtwin]\nsmallest_group = 1\n", encoding="utf-8", newline="\n"
        )
        (folder / ".synthtwinrc").write_text(
            "--smallest-group 1\n", encoding="utf-8", newline="\n"
        )
        (folder / "synthtwin.json").write_text(
            '{"smallest_group": 1, "lowered_floor": 1, '
            '"internal_smallest_group": 1}',
            encoding="utf-8",
            newline="\n",
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
    environment["SYNTHTWIN_INTERNAL_SMALLEST_GROUP"] = "1"
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


# -- repair round 1 (skeptic 1 and Codex's review of lane MIN) -------------


def test_the_internal_setting_holds_no_floor_in_its_name() -> None:
    """The default-floor check stays whole (orchestrator, 2026-10-23 09:44).

    `tests/test_stage3_default_floor.py` reads every parameter named with
    "floor" as a cell floor that must carry no default of its own, with
    no exemption; `main`'s internal setting defaults to None, so its name
    holds no "floor". The mutant, the name `lowered_floor`, fails here
    and turns that check red (two of its tests, measured).
    """
    import inspect

    named = list(inspect.signature(cli.main).parameters)
    assert [name for name in named if "floor" in name] == []
    assert "internal_smallest_group" in named


def test_no_user_facing_page_names_the_internal_setting() -> None:
    """README, INSTALL and SECURITY say only what holds now (task point 4).

    The mutant is SECURITY.md's sentence naming `cli.main`'s keyword,
    which told a reader the library call that lowers the floor.
    """
    root = _SRC.parent.parent
    for page in ("README.md", "INSTALL.md", "SECURITY.md"):
        path = root / page
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for name in ("internal_smallest_group", "lowered_floor"):
            assert name not in text, (page, name)
    security = " ".join((root / "SECURITY.md").read_text(encoding="utf-8").split())
    assert "it is not part of synthtwin's interface" in security


def _names_the_unit(message: str) -> bool:
    flat = " ".join(message.split())
    return "counted in rows" in flat and "can still be one person's" in flat


def test_the_refusal_names_the_unit_the_floor_counts(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Codex's item 2: rows, and people where the person column is known."""
    table = _table(tmp_path / "in")
    assert _run(["profile", f"{table}", _OPTION, "10"]) == 2
    assert _names_the_unit(capsys.readouterr().err)
    mutant = (
        "The smallest group size can be raised but not lowered: 10 was "
        "given, and the least it can be is 11. synthtwin names no group "
        "smaller than 11 in what it writes, so that the twin and the files "
        "beside it never name a group small enough to point at one person."
    )
    assert not _names_the_unit(mutant)


def test_the_old_description_refusal_says_may_name(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Codex's item 2: a floor-1 description need not hold a small group."""
    folder = tmp_path / "in"
    folder.mkdir()
    table = fixtures.write(folder, "same.csv", "word\n" + "same\n" * 100)
    assert cli.main(["profile", f"{table}"], internal_smallest_group=1) == 0
    capsys.readouterr()
    assert _run(["generate", f"{folder / 'same-profile.json'}"]) == 1
    said = " ".join(capsys.readouterr().err.split())
    assert "it may name groups smaller than 11" in said
    assert "it names groups smaller than 11" not in said


def test_rebuilding_at_eleven_may_withhold_a_level_the_old_twin_named(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Codex's item 1, measured: code-runs-unchanged is not promised.

    99 rows of `common` and one of `rare`: a description at floor 1 names
    both, the one rebuilt at 11 names only `common`, so code that asks
    for `rare` on the old twin can fail on the new one. P4-D426 says so
    rather than promising the old code runs; the mutant is that promise.
    """
    text = "grade\n" + "common\n" * 99 + "rare\n"
    found: "dict[int, set[str]]" = {}
    for floor in (1, 11):
        folder = tmp_path / f"at-{floor}"
        folder.mkdir()
        table = fixtures.write(folder, "grade.csv", text)
        assert cli.main(["profile", f"{table}"], internal_smallest_group=floor) == 0
        capsys.readouterr()
        written = json.loads(
            (folder / "grade-profile.json").read_text(encoding="utf-8")
        )
        found[floor] = {
            f"{level['label']}"
            for column in written["columns"]
            for level in (column.get("levels") or [])
        }
    assert "rare" in found[1] and "common" in found[1]
    assert "rare" not in found[11] and "common" in found[11]
    plan = (_SRC.parent.parent / "docs" / "plans" / "phase-4-columns.md").read_text(
        encoding="utf-8"
    )
    decision = " ".join(plan.split("## Decision P4-D426")[1].split())
    assert "code that ran on such a twin runs on the new one" not in decision
    assert "may withhold levels the old one named" in decision


def test_the_counts_the_floor_does_not_govern_are_named_in_the_readme() -> None:
    """Codex's item 3: cells counted by kind are published whatever size."""
    readme = " ".join(
        (_SRC.parent.parent / "README.md").read_text(encoding="utf-8").split()
    )
    assert "every count those files carry covers at least eleven rows" not in readme
    assert "the counts of cells by kind above are not governed by it" in readme


# The bridge before this round: the first value under 11 moved, whatever
# came after it, and the first word not starting with "-" taken as the
# command. Each is the mutant of a check below.
def _first_moved(argv: "list[str]") -> "tuple[list[str], int | None]":
    kept: "list[str]" = []
    floor: "int | None" = None
    index = 0
    while index < len(argv):
        word, typed, width = argv[index], None, 1
        if word == _OPTION and index + 1 < len(argv):
            typed, width = argv[index + 1], 2
        elif word.startswith(f"{_OPTION}="):
            typed = word[len(_OPTION) + 1 :]
        try:
            number = None if typed is None else int(typed)
        except ValueError:
            number = None
        if number is not None and number < 11:
            floor = number
        else:
            kept += argv[index : index + width]
        index += width
    return kept, floor


def _first_word(argv: "list[str]") -> "str | None":
    return next((word for word in argv if not word.startswith("-")), "")


def _bridged_floor(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str], typed: "list[str]"
) -> "tuple[int, int | None]":
    table = _table(tmp_path / "in")
    try:
        code = lowered_floor.main(["profile", f"{table}", "--replace"] + typed)
    except SystemExit as stop:
        code = 0 if stop.code is None else int(f"{stop.code}")
    capsys.readouterr()
    if code != 0:
        return code, None
    written = json.loads(
        (tmp_path / "in" / "clinic-profile.json").read_text(encoding="utf-8")
    )
    return code, int(written["settings"]["small_cell_floor"])


def test_the_bridge_keeps_the_last_of_several_floors(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Codex's item 4: argparse keeps the last value, and so does the bridge."""
    later_twenty = [_OPTION, "5", _OPTION, "20"]
    later_junk = [_OPTION, "5", f"{_OPTION}=abc"]
    assert _bridged_floor(tmp_path, capsys, later_twenty) == (0, 20)
    assert _bridged_floor(tmp_path, capsys, later_junk) == (2, None)
    assert _bridged_floor(tmp_path, capsys, [_OPTION, "20", "--sm=5"]) == (0, 5)
    assert _bridged_floor(tmp_path, capsys, [_OPTION, "3"]) == (0, 3)
    assert lowered_floor._moved(["profile", "t.csv", "--", _OPTION, "5"]) == (
        ["profile", "t.csv", "--", _OPTION, "5"],
        None,
    )
    # Verify of repair 1: a typed floor that is no number under 11
    # reaches `generate` and `validate` as typed, never replaced by the
    # internal setting (the description below records floor 1).
    old = tmp_path / "old"
    assert cli.main(["profile", f"{_table(old)}"], internal_smallest_group=1) == 0
    described = f"{old / 'clinic-profile.json'}"
    typed = (
        (["generate", described, "--replace", _OPTION, "abc"], 2),
        (["validate", described, "--replace", _OPTION, "abc"], 2),
        (["generate", described, "--replace", "--sm=abc"], 2),
        (["generate", described, "--replace", _OPTION, "20"], 1),
        (["validate", described, "--replace", _OPTION, "20"], 1),
    )
    for argv, code in typed:
        assert _bridged(argv) == code, argv
    capsys.readouterr()
    monkeypatch.setattr(lowered_floor, "_found", _nothing_found)
    assert [_bridged(argv) for argv, _code in typed] == [0, 0, 0, 0, 0]
    capsys.readouterr()
    monkeypatch.setattr(lowered_floor, "_moved", _first_moved)
    assert _bridged_floor(tmp_path, capsys, later_twenty) == (0, 5)
    assert _bridged_floor(tmp_path, capsys, later_junk) == (0, 5)


def _bridged(argv: "list[str]") -> int:
    """The bridge as a typed command runs it: its code, SystemExit included."""
    try:
        return lowered_floor.main(argv)
    except SystemExit as stop:
        return 0 if stop.code is None else int(f"{stop.code}")


# The bridge of repair 1: no typed floor seen, so `generate` and
# `validate` were always handed the internal setting at 1.
def _nothing_found(argv: "list[str]") -> "list[tuple[int, int, str]]":
    return []


def test_the_shortest_spelling_the_bridge_reads_is_argparse_s(
    spellings: "list[str]",
) -> None:
    assert spellings[0] == lowered_floor._SHORTEST


def test_the_bridge_finds_the_command_past_an_option_value(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Codex's item 5: `--seed 0 generate` is `generate`, not `0`."""
    table = _table(tmp_path / "in")
    assert cli.main(["profile", f"{table}"], internal_smallest_group=1) == 0
    described = f"{tmp_path / 'in' / 'clinic-profile.json'}"
    orders = (
        ["generate", described, "--seed", "0", "--replace"],
        ["--seed", "0", "generate", described, "--replace"],
        ["--replace", "--seed", "0", "generate", described],
    )
    for order in orders:
        assert lowered_floor.main(order) == 0, order
    capsys.readouterr()
    assert lowered_floor._command(["--seed", "0", "generate", described]) == (
        "generate"
    )
    assert lowered_floor._command(["--help"]) is None
    monkeypatch.setattr(lowered_floor, "_command", _first_word)
    assert lowered_floor.main(orders[1]) == 1
    capsys.readouterr()


@pytest.mark.parametrize("given", [0, -1])
@pytest.mark.parametrize("command", ["generate", "validate"])
def test_an_internal_setting_under_one_is_refused_on_every_command(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    command: str,
    given: int,
) -> None:
    """Codex's item 6: 0 and less are no floor, whichever command."""
    table = _table(tmp_path / "in")
    assert cli.main(["profile", f"{table}"], internal_smallest_group=1) == 0
    argv = [command, f"{tmp_path / 'in' / 'clinic-profile.json'}", "--replace"]
    assert cli.main(["generate", argv[1]], internal_smallest_group=1) == 0
    capsys.readouterr()
    before = _listing(tmp_path)
    assert cli.main(argv, internal_smallest_group=given) == 2
    said = capsys.readouterr()
    assert "whole number of 1 or more" in said.err and said.out == ""
    assert _listing(tmp_path) == before
    monkeypatch.setattr(cli, "_no_floor_at_all", lambda given: False)
    assert cli.main(argv, internal_smallest_group=given) == 0
    capsys.readouterr()
