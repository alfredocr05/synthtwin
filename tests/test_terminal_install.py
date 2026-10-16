"""Lane TI's gate: installing synthtwin and its first run (plan P4-D397).

The owner, 2026-10-15: "we can run the app in the terminal, however the
instructions and the way to make the application to run needs to be
easy anyway!". This file holds the four things lane TI built to that:

* `python -m synthtwin` reaches the same `main` as the `synthtwin`
  command (it failed before: there was no `__main__.py`);
* `synthtwin doctor` prints one plain line per check, exits 0 when every
  check passed and 1 when any did not -- each check is forced to fail
  here in turn -- and never opens the table it is named;
* `profile` ends by printing the `generate` command on each way a run
  that wrote a description ends, as README promised and it did not;
* the install scripts keep the hash-checked offline procedure, end by
  running `doctor`, and CI runs them on Ubuntu, Windows and macOS.

Everything runs in this process: no test here starts a program.
"""

import builtins
import io
import os
import pathlib
import random
import re
import runpy
import sys

import pytest

from synthtwin import cli

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
WORKFLOW = REPO / ".github" / "workflows" / "ci.yml"


def _doctor(
    capsys: pytest.CaptureFixture[str], *arguments: str
) -> "tuple[int, list[str]]":
    """Run `synthtwin doctor` in this process; its exit code and its lines."""
    code = cli.main(["doctor", *arguments])
    said = capsys.readouterr().out
    return code, said.splitlines()


def _check_lines(lines: "list[str]") -> "list[str]":
    """The lines that report a check, in order."""
    return [line for line in lines if line.startswith(("  ok ", "  PROBLEM "))]


def _write_table(path: pathlib.Path, rows: int = 150) -> pathlib.Path:
    """A seeded neutral table of two columns: an age and a group."""
    draw = random.Random(397)
    lines = ["age,group"]
    for _ in range(rows):
        lines += [f"{draw.randint(20, 80)},{draw.choice('ABC')}"]
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")
    return path


# -- python -m synthtwin --------------------------------------------------


def _python_dash_m(
    monkeypatch: pytest.MonkeyPatch, *arguments: str
) -> "int | str | None":
    """`python -m synthtwin ARGUMENTS`, in this process; the exit code it ends with.

    `runpy.run_module` is what `python -m` itself calls, and it runs the
    committed `src/synthtwin/__main__.py` (registered in
    tests/test_version_reach.py's `ROUTES_THAT_RUN_SOURCE`).
    """
    monkeypatch.setattr(sys, "argv", ["synthtwin", *arguments])
    with pytest.raises(SystemExit) as stopped:
        runpy.run_module("synthtwin", run_name="__main__", alter_sys=True)
    return stopped.value.code


def test_python_dash_m_synthtwin_reaches_the_same_main(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`python -m synthtwin ARGS` calls `cli.main` and exits with its code."""
    seen: "list[object]" = []

    def standing_in(argv: "list[str] | None" = None) -> int:
        nonlocal seen
        seen += [argv]
        return 7

    monkeypatch.setattr(cli, "main", standing_in)
    assert _python_dash_m(monkeypatch, "doctor") == 7
    assert seen == [None], "main reads sys.argv itself, as the console script's does"


def test_python_dash_m_synthtwin_prints_the_version(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The real `main` behind `-m`: `--version` prints it and exits 0."""
    assert _python_dash_m(monkeypatch, "--version") == 0
    assert capsys.readouterr().out.strip() == cli._version()


def test_importing_the_module_runs_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Imported under its own name, `synthtwin.__main__` starts no command."""
    called: "list[object]" = []

    def standing_in(argv: "list[str] | None" = None) -> int:
        nonlocal called
        called += [argv]
        return 0

    monkeypatch.setattr(cli, "main", standing_in)
    monkeypatch.delitem(sys.modules, "synthtwin.__main__", raising=False)
    import synthtwin.__main__  # noqa: F401

    assert called == []


# -- synthtwin doctor ------------------------------------------------------


def test_doctor_passes_on_this_computer_with_one_line_per_check(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Five checks without a table, six with one, each one line, exit 0."""
    monkeypatch.chdir(tmp_path)
    code, lines = _doctor(capsys)
    assert code == 0, "\n".join(lines)
    checks = _check_lines(lines)
    assert len(checks) == 5, lines
    assert all(line.startswith("  ok ") for line in checks)
    assert re.search(r"Python \d+\.\d+\.\d+", checks[0])
    assert "numpy" in checks[1] and "pandas" in checks[2]
    assert "output folder" in checks[3]
    assert "memory" in checks[4]
    assert lines[-1] == "  synthtwin profile my-table.csv", "the next command ends it"
    assert list(tmp_path.iterdir()) == [], "the test file it wrote is removed"

    table = _write_table(tmp_path / "clinic.csv")
    code, lines = _doctor(capsys, str(table))
    assert code == 0, "\n".join(lines)
    checks = _check_lines(lines)
    assert len(checks) == 6
    assert "The table is" in checks[5]
    assert lines[-1] == f"  synthtwin profile {table}"


def test_doctor_fails_on_a_python_older_than_3_10(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "_python_version", lambda: (3, 9, 18))
    code, lines = _doctor(capsys)
    assert code == 1
    first = _check_lines(lines)[0]
    assert first.startswith("  PROBLEM ") and "3.9.18" in first
    assert "Before you start" in first and "install" in first
    assert "synthtwin doctor" in lines[-1]


@pytest.mark.parametrize("missing", ["numpy.random", "pandas"])
def test_doctor_fails_when_a_package_cannot_be_loaded(
    missing: str,
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A package the import system refuses is a PROBLEM line naming it."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setitem(sys.modules, missing, None)
    code, lines = _doctor(capsys)
    assert code == 1
    failed = [line for line in _check_lines(lines) if line.startswith("  PROBLEM ")]
    assert len(failed) == 1
    assert missing.split(".")[0] in failed[0]
    assert "scripts/install.sh" in failed[0] and "install.bat" in failed[0]


def test_doctor_fails_on_an_output_folder_that_is_not_there(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, lines = _doctor(capsys, "--out-dir", str(tmp_path / "not-made"))
    assert code == 1
    failed = [line for line in _check_lines(lines) if line.startswith("  PROBLEM ")]
    assert len(failed) == 1 and "does not exist" in failed[0]
    assert "--out-dir" in failed[0]


@pytest.mark.skipif(
    sys.platform == "win32" or (hasattr(os, "geteuid") and os.geteuid() == 0),
    reason="a folder's write permission is a POSIX mode, and root ignores it",
)
def test_doctor_fails_on_an_output_folder_that_takes_no_file(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    shut = tmp_path / "shut"
    shut.mkdir()
    shut.chmod(0o500)
    try:
        code, lines = _doctor(capsys, "--out-dir", str(shut))
    finally:
        shut.chmod(0o700)
    assert code == 1
    failed = [line for line in _check_lines(lines) if line.startswith("  PROBLEM ")]
    assert len(failed) == 1 and "could not save a file" in failed[0]
    assert list(shut.iterdir()) == []


def test_doctor_never_writes_over_a_file_at_its_test_name(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    kept = tmp_path / cli._DOCTOR_PROBE
    kept.write_bytes(b"somebody's own file\n")
    code, lines = _doctor(capsys, "--out-dir", str(tmp_path))
    assert code == 1
    assert kept.read_bytes() == b"somebody's own file\n"


def test_doctor_says_plainly_when_memory_cannot_be_read(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Windows has no os.sysconf: the line says so, and it is no failure."""

    def no_such_name(name: str) -> int:
        raise ValueError(name)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(os, "sysconf", no_such_name, raising=False)
    assert cli._total_memory() is None
    table = _write_table(tmp_path / "clinic.csv")
    code, lines = _doctor(capsys, str(table))
    assert code == 0
    checks = _check_lines(lines)
    assert "could not be read" in checks[4]
    assert "could not be weighed" in checks[5]
    monkeypatch.setattr(cli.sys, "platform", "win32")
    assert cli._total_memory() is None


def test_doctor_reads_total_memory_through_sysconf(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sizes = {"SC_PHYS_PAGES": 4, "SC_PAGE_SIZE": 1024 * 1024 * 1024}
    monkeypatch.setattr(cli.sys, "platform", "linux")
    monkeypatch.setattr(os, "sysconf", lambda name: sizes[name], raising=False)
    assert cli._total_memory() == 4 * 1024**3
    assert cli._size_words(4 * 1024**3) == "4.0 GB"


def test_doctor_warns_on_a_table_large_for_this_computer(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Ten times the file's size past half the memory is a PROBLEM, in words."""
    table = _write_table(tmp_path / "clinic.csv")
    size = table.stat().st_size
    monkeypatch.setattr(cli, "_total_memory", lambda: size * 10)
    code, lines = _doctor(capsys, str(table))
    assert code == 1
    last_check = _check_lines(lines)[-1]
    assert last_check.startswith("  PROBLEM ") and "large for this" in last_check
    assert "Close other programs" in last_check
    monkeypatch.setattr(cli, "_total_memory", lambda: size * 20)
    code, lines = _doctor(capsys, str(table))
    assert code == 0, "exactly half the memory still fits"


@pytest.mark.parametrize("kind", ["missing", "folder"])
def test_doctor_fails_on_a_table_path_that_names_no_file(
    kind: str, tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    named = tmp_path / "clinic.csv"
    if kind == "folder":
        named.mkdir()
    code, lines = _doctor(capsys, str(named))
    assert code == 1
    last_check = _check_lines(lines)[-1]
    assert last_check.startswith("  PROBLEM ")
    assert ("no file at" if kind == "missing" else "is a folder") in last_check


def test_doctor_never_opens_the_table(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Every way Python opens a file raises on the table; doctor still passes.

    On POSIX the table is also left with no permission at all, so the
    operating system itself would refuse a read.
    """
    table = _write_table(tmp_path / "clinic.csv")
    size = table.stat().st_size
    target = os.path.realpath(table)
    opened: "list[str]" = []

    def guarded(original: "object") -> "object":
        def opener(file: object, *rest: object, **named: object) -> object:
            nonlocal opened
            if isinstance(file, (str, bytes, os.PathLike)):
                if os.path.realpath(os.fsdecode(file)) == target:
                    opened += [f"{file}"]
                    raise AssertionError(f"doctor opened the table {file}")
            return original(file, *rest, **named)  # type: ignore[operator]

        return opener

    monkeypatch.setattr(builtins, "open", guarded(builtins.open))
    monkeypatch.setattr(io, "open", guarded(io.open))
    monkeypatch.setattr(os, "open", guarded(os.open))
    if sys.platform != "win32":
        table.chmod(0)
    try:
        code, lines = _doctor(capsys, str(table))
    finally:
        table.chmod(0o600)
    assert opened == []
    assert code == 0, "\n".join(lines)
    assert cli._size_words(size) in _check_lines(lines)[-1]


def test_the_help_names_doctor(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        cli.main(["--help"])
    said = capsys.readouterr().out
    assert "doctor" in said and "synthtwin doctor data.csv" in said


# -- profile's next command ------------------------------------------------


def _profile_lines(
    table: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> "list[str]":
    code = cli.main(["profile", str(table)])
    assert code == 0
    return [line for line in capsys.readouterr().out.splitlines() if line.strip()]


def test_profile_ends_by_printing_the_generate_command(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The last line is the command to type next, naming the written description."""
    table = _write_table(tmp_path / "clinic.csv")
    lines = _profile_lines(table, capsys)
    description = tmp_path / "clinic-profile.json"
    assert description.is_file()
    assert (tmp_path / "clinic-questions.json").is_file()
    assert lines[-2] == "Next, build the twin from this description:"
    _names_the_description(lines[-1], description)


def _names_the_description(line: str, description: pathlib.Path) -> None:
    """The line is `synthtwin generate` and the path of the written description."""
    prefix = "  synthtwin generate "
    assert line.startswith(prefix), line
    assert os.path.realpath(line[len(prefix) :]) == os.path.realpath(description)


@pytest.mark.skipif(sys.platform == "win32", reason="a symbolic link needs no privilege on POSIX alone")
def test_profile_prints_it_when_the_questions_file_could_not_be_written(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The other way a run that wrote a description ends prints it too.

    A link left at the questions file's name, pointing at the table, is
    refused before anything is written (review item L17b-R1-1): the pair
    is written and the questions file is not.
    """
    table = _write_table(tmp_path / "clinic.csv")
    (tmp_path / "clinic-questions.json").symlink_to(table)
    lines = _profile_lines(table, capsys)
    assert (tmp_path / "clinic-profile.json").is_file()
    _names_the_description(lines[-1], tmp_path / "clinic-profile.json")


def test_the_next_command_is_quoted_for_the_shell() -> None:
    line = cli._teaching_generate(pathlib.Path("/data/my clinic-profile.json"))
    assert "synthtwin generate '/data/my clinic-profile.json'" in line
    assert line.splitlines()[-1].startswith("  (each value quoted for")


# -- the install scripts, README and CI -------------------------------------


def test_the_install_scripts_keep_the_hash_checked_offline_procedure() -> None:
    """Both scripts run README's two offline pip commands, flag for flag."""
    for name in ("install.sh", "install.bat"):
        text = (SCRIPTS / name).read_text(encoding="utf-8")
        flat = re.sub(r"\\\s*\n\s*", " ", text)
        offline = re.search(
            r"pip install[^\n]*--no-index --find-links \S+[^\n]*--require-hashes -r \S+",
            flat,
        )
        assert offline, f"{name} lost the hash-checked install from the wheel folder"
        assert re.search(r"pip install[^\n]*--no-index --no-deps", flat), name
        assert re.search(r"pip install[^\n]*--require-hashes -r \S+", flat.replace(offline.group(0), "")), (
            f"{name}: the install from the folder fetches the lock's files unchecked"
        )
        assert "requirements-install.lock" in text
        assert "doctor" in text.split("pip install")[-1], f"{name} does not end with doctor"
        for fetcher in ("curl", "wget", "Invoke-WebRequest", "bitsadmin"):
            assert fetcher not in text, f"{name} fetches something itself ({fetcher})"


def test_the_windows_script_is_a_batch_file_with_windows_line_endings() -> None:
    raw = (SCRIPTS / "install.bat").read_bytes()
    assert raw.startswith(b"@echo off\r\n")
    assert b"\n" not in raw.replace(b"\r\n", b""), "every line ends CR LF, as cmd reads labels"


def test_the_readme_installs_as_written() -> None:
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    assert "## Before you start" in readme and "## Installing" in readme
    install = readme[readme.index("## Installing") :]
    assert "sh scripts/install.sh\n" in install
    assert "scripts\\install.bat\n" in install
    assert "synthtwin doctor" in install and "never opens" in install
    assert "python -m synthtwin" in install
    assert "Each one ends by printing the" not in readme
    for flags in ("--no-index --find-links wheelhouse", "--require-hashes", "--no-deps"):
        assert flags in install


def test_ci_runs_the_install_scripts_on_three_systems() -> None:
    """One step of the tests job runs both scripts; its matrix holds the three systems."""
    text = WORKFLOW.read_text(encoding="utf-8")
    job = text[text.index("  tests:") : text.index("  shard-coverage:")]
    step = job[job.index("Install from a wheel folder with the install script") :]
    step = step[: step.index("- name:")]
    assert "sh scripts/install.sh" in step and "scripts\\\\install.bat" in step
    assert "--require-hashes" in step and "dist/*.whl" in step
    for system in ("ubuntu-latest", "windows-latest", "macos-latest"):
        assert system in job
    for used in re.findall(r"uses: (\S+)", text):
        assert re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", used), used


def test_the_package_ships_its_main_module() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "wheel required synthtwin/__main__.py" in text
    assert "sdist required ROOT/src/synthtwin/__main__.py" in text


# -- the measures behind K-S8-01 and K-S8-04 ---------------------------------


def _section(text: str, heading: str) -> str:
    """One `## ` section of README, up to the next."""
    start = text.index(f"## {heading}\n")
    end = text.find("\n## ", start + 1)
    return text[start : end if end >= 0 else len(text)]


def _first_block(section: str) -> "list[str]":
    """The non-empty lines of a section's first fenced block."""
    opened = section.index("```\n") + len("```\n")
    closed = section.index("```", opened)
    return [line.strip() for line in section[opened:closed].splitlines() if line.strip()]


def journey_measures() -> "dict[str, int]":
    """K-S8-01: what README asks of a new user, from a folder to a validated twin.

    * `install_commands`: the lines of the first block of "Installing"
      that build the environment -- every line but getting the folder
      (`git clone`, `cd`) and a run of synthtwin itself;
    * `run_commands`: the `synthtwin` lines of the first block of "What
      works today", the run README teaches;
    * `hand_edited_files`: the files README tells the reader to write
      answers into, counted by name in each paragraph that says so.

    Read from README.md, so a lane that changes what a person does
    changes the number only by changing what README tells them.
    """
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    install = [
        line
        for line in _first_block(_section(readme, "Installing"))
        if not line.startswith(("git clone", "cd ", "synthtwin ", ".venv"))
    ]
    run = [
        line
        for line in _first_block(_section(readme, "What works today"))
        if line.startswith("synthtwin ")
    ]
    edited: "set[str]" = set()
    for paragraph in readme.split("\n\n"):
        if "your_answer" in paragraph or "Fill it in" in paragraph:
            edited |= set(re.findall(r"[\w.-]+-questions\.json", paragraph))
    return {
        "install_commands": len(install),
        "run_commands": len(run),
        "hand_edited_files": len(edited),
    }


def install_measures(folder: pathlib.Path) -> "dict[str, int]":
    """K-S8-04: `python -m synthtwin`, the scripts' hash check, CI, and doctor here.

    * `main_module_dispatches`: 1 when `src/synthtwin/__main__.py` exits
      with `cli.main()` under the `__main__` guard, read from its syntax
      (the behaviour is `test_python_dash_m_synthtwin_prints_the_version`);
    * `scripts_keeping_hash_check`: the install scripts that run both of
      README's offline pip commands flag for flag and end with doctor;
    * `ci_systems_running_the_scripts`: the systems of the tests job whose
      first shard runs the install step;
    * `doctor_exit_here`: `synthtwin doctor`'s exit code on this machine,
      run in this process with ``folder`` as the output folder.
    """
    import ast

    tree = ast.parse((REPO / "src" / "synthtwin" / "__main__.py").read_text(encoding="utf-8"))
    guarded = [
        node
        for node in tree.body
        if isinstance(node, ast.If) and "__main__" in ast.unparse(node.test)
    ]
    dispatches = int(
        len(guarded) == 1 and ast.unparse(guarded[0].body[0]) == "sys.exit(main())"
    )
    keeping = 0
    for name in ("install.sh", "install.bat"):
        text = (SCRIPTS / name).read_text(encoding="utf-8")
        flat = re.sub(r"\\\s*\n\s*", " ", text)
        if (
            re.search(r"--no-index --find-links \S+[^\n]*--require-hashes -r \S+", flat)
            and re.search(r"--no-index --no-deps", flat)
            and "doctor" in text.split("pip install")[-1]
        ):
            keeping += 1
    workflow = WORKFLOW.read_text(encoding="utf-8")
    job = workflow[workflow.index("  tests:") : workflow.index("  shard-coverage:")]
    systems = 0
    if "sh scripts/install.sh" in job and "scripts\\\\install.bat" in job:
        systems = sum(
            1 for system in ("ubuntu-latest", "windows-latest", "macos-latest") if system in job
        )
    code = cli.main(["doctor", "--out-dir", str(folder)])
    return {
        "main_module_dispatches": dispatches,
        "scripts_keeping_hash_check": keeping,
        "ci_systems_running_the_scripts": systems,
        "doctor_exit_here": code,
    }


def test_the_measures_read_what_they_say() -> None:
    """Non-vacuity: the README journey reads today's numbers."""
    assert journey_measures() == {
        "install_commands": 1,
        "run_commands": 3,
        "hand_edited_files": 1,
    }
