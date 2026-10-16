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
import shlex
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
    """The lines that report a check, in order: passed, noted or failed."""
    return [
        line for line in lines if line.startswith(("  ok ", "  note ", "  PROBLEM "))
    ]


def _problems(lines: "list[str]") -> "list[str]":
    return [line for line in _check_lines(lines) if line.startswith("  PROBLEM ")]


def _words(line: str) -> "list[str]":
    """A taught line split as the shell it was quoted for splits it.

    POSIX quoting on a Mac or Linux; PowerShell's single quotes, a quote
    inside doubled, on Windows.
    """
    if sys.platform != "win32":
        return shlex.split(line)
    return [
        word[1:-1].replace("''", "'") if word.startswith("'") else word
        for word in re.findall(r"'(?:[^']|'')*'|\S+", line)
    ]


def _taught(text: str) -> "list[str]":
    """The lines of a taught command block, after its first line."""
    return text.splitlines()[1:]


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


def test_python_dash_m_on_an_old_python_says_so_in_words(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An older Python stops before the command's module, with words, exit 1.

    The command's module needs 3.10 to be read at all, so the check sits
    in `__main__.py` before the import (the Codex review of lane TI,
    item 8). Measured: Apple's Python 3.9.6 now prints this line and
    exits 1 where it stopped on a stack trace.
    """
    called: "list[object]" = []

    def standing_in(argv: "list[str] | None" = None) -> int:
        nonlocal called
        called += [argv]
        return 0

    monkeypatch.setattr(cli, "main", standing_in)
    monkeypatch.setattr(sys, "version_info", (3, 9, 6, "final", 0))
    said = _python_dash_m(monkeypatch, "doctor")
    assert called == [], "the command's module is never reached"
    assert isinstance(said, str), "sys.exit with a message exits 1 and prints it"
    assert "needs Python 3.10 or later" in said and "3.9.6" in said
    assert "Before you start" in said and "install.sh" in said


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
    assert lines[-2] == "Every check passed. Next, describe your table:"
    assert lines[-1] == "  synthtwin profile my-table.csv", "the next command ends it"
    assert list(tmp_path.iterdir()) == [], "the test file it wrote is removed"

    # Compared with the lines the module itself teaches, so a temporary
    # folder whose path the shell must quote -- one with a space in it,
    # as the suite's own lock runner gives -- reads the same (lane TI's
    # skeptic, item 1).
    table = _write_table(tmp_path / "clinic.csv")
    code, lines = _doctor(capsys, str(table))
    assert code == 0, "\n".join(lines)
    checks = _check_lines(lines)
    assert len(checks) == 6
    assert "The table is" in checks[5]
    taught = _taught(cli._teaching_profile(str(table)))
    assert lines[-len(taught) :] == taught


def test_doctor_ends_with_what_the_person_typed(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Both closing lines carry the table and --out-dir doctor was given (skeptic item 6)."""
    table = _write_table(tmp_path / "clinic.csv")
    out = tmp_path / "out"
    out.mkdir()
    code, lines = _doctor(capsys, str(table), "--out-dir", str(out))
    assert code == 0, "\n".join(lines)
    taught = _taught(cli._teaching_profile(str(table), str(out)))
    assert lines[-len(taught) :] == taught
    assert "--out-dir" in taught[0] and "synthtwin profile" in taught[0]

    missing = tmp_path / "not-made"
    code, lines = _doctor(capsys, str(table), "--out-dir", str(missing))
    assert code == 1
    again = cli._doctor_again(str(table), str(missing)).splitlines()
    assert lines[-len(again) :] == again
    assert again[0].startswith("  synthtwin doctor ") and "--out-dir" in again[0]
    assert _words(again[0]) == ["synthtwin", "doctor", str(table), "--out-dir", str(missing)]


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


def test_doctor_reports_a_package_whose_load_raises_another_exception(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A build for another Python raises ValueError as it loads: a line, not a trace.

    The Codex review of lane TI, item 7: every other check still runs.
    """
    monkeypatch.chdir(tmp_path)
    real = builtins.__import__

    def refusing(name: str, *rest: object, **named: object) -> object:
        if name == "pandas":
            raise ValueError("numpy.dtype size changed, may indicate binary incompatibility")
        return real(name, *rest, **named)  # type: ignore[arg-type]

    monkeypatch.delitem(sys.modules, "pandas", raising=False)
    monkeypatch.setattr(builtins, "__import__", refusing)
    code, lines = _doctor(capsys)
    assert code == 1
    assert len(_check_lines(lines)) == 5, "every check still runs"
    failed = _problems(lines)
    assert len(failed) == 1 and "pandas could not be loaded" in failed[0]


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
    """Kept, and the advice never says whose it is or to delete it (Codex item 11)."""
    kept = tmp_path / cli._DOCTOR_PROBE
    kept.write_bytes(b"somebody's own file\n")
    code, lines = _doctor(capsys, "--out-dir", str(tmp_path))
    assert code == 1
    assert kept.read_bytes() == b"somebody's own file\n"
    failed = _problems(lines)
    assert len(failed) == 1 and "does not touch" in failed[0]
    assert "Delete" not in failed[0] and "left by" not in failed[0]
    assert "--out-dir" in failed[0]


def test_doctor_creates_its_test_file_exclusively(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A file that appears at the name after the look is still never written over."""
    kept = tmp_path / cli._DOCTOR_PROBE
    kept.write_bytes(b"made in between\n")
    monkeypatch.setattr(cli.os.path, "lexists", lambda path: False)
    code, lines = _doctor(capsys, "--out-dir", str(tmp_path))
    assert code == 1
    assert kept.read_bytes() == b"made in between\n"
    assert "does not touch" in _problems(lines)[0]


@pytest.mark.skipif(sys.platform == "win32", reason="a symbolic link needs no privilege on POSIX alone")
def test_doctor_does_not_follow_a_link_at_its_test_name(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A dangling link at the name is refused, and its target is never made.

    The Codex review of lane TI, item 6: the probe used to be resolved
    through the link, so doctor wrote and removed a file in ANOTHER
    folder and said the one named takes a file.
    """
    asked = tmp_path / "asked"
    elsewhere = tmp_path / "elsewhere"
    asked.mkdir()
    elsewhere.mkdir()
    (asked / cli._DOCTOR_PROBE).symlink_to(elsewhere / "target")
    code, lines = _doctor(capsys, "--out-dir", str(asked))
    assert code == 1
    assert "does not touch" in _problems(lines)[0]
    assert list(elsewhere.iterdir()) == []


@pytest.mark.skipif(
    sys.platform == "win32" or (hasattr(os, "geteuid") and os.geteuid() == 0),
    reason="a folder's permissions are a POSIX mode, and root ignores them",
)
@pytest.mark.parametrize("named", ["table", "out-dir"])
def test_doctor_says_what_to_do_where_it_may_not_look(
    named: str, tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A folder it may not look into is a PROBLEM line with a next step, not a trace.

    Lane TI's skeptic, item 2: `Path.exists` raises on EACCES and EPERM,
    which is also what a Mac's protected folders give a terminal that
    was not let in.
    """
    shut = tmp_path / "shut"
    shut.mkdir()
    table = _write_table(shut / "clinic.csv")
    inside = shut / "out"
    inside.mkdir()
    shut.chmod(0)
    try:
        if named == "table":
            code, lines = _doctor(capsys, str(table), "--out-dir", str(tmp_path))
        else:
            code, lines = _doctor(capsys, "--out-dir", str(inside))
    finally:
        shut.chmod(0o700)
    assert code == 1
    failed = _problems(lines)
    assert len(failed) == 1 and "is not allowed to look at" in failed[0]
    assert "Privacy & Security" in failed[0] and "doctor again" in failed[0]


def test_doctor_reports_a_size_it_is_refused(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The file system refusing the size question is a line too, on every system."""
    table = _write_table(tmp_path / "clinic.csv")
    real = pathlib.Path.stat
    target = os.path.realpath(table)

    def refusing(self: pathlib.Path, *rest: object, **named: object) -> os.stat_result:
        if os.path.realpath(self) == target:
            raise PermissionError(1, "Operation not permitted", str(self))
        return real(self, *rest, **named)  # type: ignore[arg-type]

    monkeypatch.setattr(pathlib.Path, "stat", refusing)
    code, lines = _doctor(capsys, str(table), "--out-dir", str(tmp_path))
    assert code == 1
    failed = _problems(lines)
    assert len(failed) == 1 and "is not allowed to look at" in failed[0]


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
    assert code == 0, "a check that could not be made is no failure"
    checks = _check_lines(lines)
    # A note, neither ok nor PROBLEM, and the closing line claims only
    # what was checked (lane TI's skeptic, item 5).
    assert checks[4].startswith("  note ") and "could not be read" in checks[4]
    assert checks[5].startswith("  note ") and "could not be weighed" in checks[5]
    assert "Every check that could be made passed." in "\n".join(lines)
    assert "Every check passed." not in "\n".join(lines)
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
    assert "a guess from the file's size alone" in last_check
    monkeypatch.setattr(cli, "_total_memory", lambda: size * 20)
    code, lines = _doctor(capsys, str(table))
    assert code == 0, "exactly half the memory still fits"


def test_doctor_weighs_a_workbook_at_the_readers_bound_not_its_size(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A packed file's size says nothing of its cells (the Codex review, item 9).

    A small workbook on a 512 MB computer is large for it: reading a
    million cells measured 632 MB, whatever the file's size.
    """
    book = tmp_path / "clinic.xlsx"
    book.write_bytes(b"PK\x03\x04" + b"\x00" * 5000)
    monkeypatch.setattr(cli, "_total_memory", lambda: 512 * 1024 * 1024)
    code, lines = _doctor(capsys, str(book))
    assert code == 1
    last_check = _check_lines(lines)[-1]
    assert last_check.startswith("  PROBLEM ") and "size does not say" in last_check
    assert cli._size_words(cli._WORKBOOK_READ_BYTES) in last_check
    monkeypatch.setattr(cli, "_total_memory", lambda: 16 * 1024**3)
    code, lines = _doctor(capsys, str(book))
    assert code == 0
    assert "fits" in _check_lines(lines)[-1]


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


_NEXT = "Next, build the twin from this description:"


def _profile_lines(
    table: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> "list[str]":
    code = cli.main(["profile", str(table)])
    assert code == 0
    return [line for line in capsys.readouterr().out.splitlines() if line.strip()]


def _next_block(lines: "list[str]") -> "list[str]":
    """The command lines after "Next, ...:", the shell note dropped; once, at the end.

    The block is printed exactly once (lane TI's skeptic, item 8b) and
    nothing follows it but its own lines: the command, and the note
    naming the shell when the path had to be quoted -- as it is under a
    temporary folder with a space in it (the skeptic's item 1).
    """
    assert lines.count(_NEXT) == 1, "the next command is printed once"
    block = lines[lines.index(_NEXT) + 1 :]
    if block and block[-1].startswith("  (each value quoted for"):
        block = block[:-1]
    assert len(block) == 1, f"nothing but the command follows it: {block}"
    return block


def _names_the_description(lines: "list[str]", description: pathlib.Path) -> None:
    """The run ends with `synthtwin generate` and the written description's path."""
    (line,) = _next_block(lines)
    words = _words(line)
    assert words[:2] == ["synthtwin", "generate"] and len(words) == 3, line
    assert os.path.realpath(words[2]) == os.path.realpath(description)


def test_profile_ends_by_printing_the_generate_command(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The last lines are the command to type next, naming the written description."""
    table = _write_table(tmp_path / "clinic.csv")
    lines = _profile_lines(table, capsys)
    description = tmp_path / "clinic-profile.json"
    assert description.is_file()
    assert (tmp_path / "clinic-questions.json").is_file()
    _names_the_description(lines, description)


def test_profile_quotes_a_description_in_a_folder_with_a_space(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The path is quoted for the shell, and the shell is named after it."""
    spaced = tmp_path / "clinic data"
    spaced.mkdir()
    table = _write_table(spaced / "clinic.csv")
    lines = _profile_lines(table, capsys)
    _names_the_description(lines, spaced / "clinic-profile.json")
    assert lines[-1].startswith("  (each value quoted for")
    assert "'" in lines[-2], "a path with a space is written between quotes"


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
    _names_the_description(lines, tmp_path / "clinic-profile.json")


def test_a_refused_profile_teaches_no_next_command(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A table too small to describe writes nothing, so nothing is taught next."""
    table = _write_table(tmp_path / "clinic.csv", rows=40)
    assert cli.main(["profile", str(table)]) == 1
    said = capsys.readouterr()
    assert _NEXT not in said.out and _NEXT not in said.err
    assert not (tmp_path / "clinic-profile.json").exists()


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


def _offline_commands(name: str) -> "list[str]":
    """The script's pip commands that install from the wheel folder, one line each."""
    flat = re.sub(r"\\\s*\n\s*", " ", (SCRIPTS / name).read_text(encoding="utf-8"))
    return [line for line in flat.splitlines() if "pip install" in line and "--no-index" in line]


@pytest.mark.parametrize(
    "name, no_config", [("install.sh", "PIP_CONFIG_FILE=/dev/null"), ("install.bat", None)]
)
def test_the_offline_install_reads_no_pip_setting_of_this_computer(
    name: str, no_config: "str | None"
) -> None:
    """--isolated and PIP_CONFIG_FILE at the null device on both offline commands.

    The Codex review of lane TI, item 1, measured here: with a
    find-links in PIP_FIND_LINKS or in a pip.conf, `pip download
    --no-index --find-links EMPTY` still found the package there; with
    --isolated and PIP_CONFIG_FILE=/dev/null it found nothing.
    """
    commands = _offline_commands(name)
    assert len(commands) == 2, commands
    for command in commands:
        assert "pip install --isolated" in command, command
        if no_config is not None:
            assert command.lstrip().startswith(no_config), command
    if name == "install.bat":
        text = (SCRIPTS / name).read_text(encoding="utf-8")
        before = text[: text.index(commands[0].strip())]
        assert 'set "PIP_CONFIG_FILE=nul"' in before


@pytest.mark.parametrize("name", ["install.sh", "install.bat"])
def test_the_install_scripts_make_a_fresh_environment_every_time(name: str) -> None:
    """venv --clear, unconditionally, after the wheel folder is checked and before pip.

    An environment already there is never reused: pip skips a package
    whose version is in place without checking its files (the Codex
    review, items 2 and 3), and a broken or too-old one sent doctor's
    advice round in a loop (the skeptic, item 3). A Python running in a
    switched-on environment is refused first, since clearing it would
    pull its own interpreter from under it.
    """
    text = (SCRIPTS / name).read_text(encoding="utf-8")
    made = [line for line in text.splitlines() if "-m venv" in line]
    assert len(made) == 1 and "-m venv --clear " in made[0], made
    at = text.index(made[0])
    assert text.index("synthtwin-*.whl") < at, "the wheel folder is checked before anything changes"
    assert at < text.index("pip install")
    assert "sys.prefix == sys.base_prefix" in text[:at]
    assert "deactivate" in text


def test_the_windows_script_prints_paths_without_running_them() -> None:
    """No echo puts a path in by %...%: a folder named `A & exit & B` would run (Codex item 4)."""
    text = (SCRIPTS / "install.bat").read_text(encoding="utf-8")
    pathlike = re.compile(r"(?<!%)%(HERE|ENVDIR|LOCK|WHEELS|WHEEL|VPY|PY)%|(?<!%)%~")
    for line in text.splitlines():
        spoken = line.strip()
        if re.match(r"(?i)(echo\b|for .* do echo\b)", spoken):
            said = spoken.split(" do ", 1)[1] if spoken.lower().startswith("for ") else spoken
            assert not pathlike.search(said), line


@pytest.mark.parametrize("name", ["install.sh", "install.bat"])
def test_every_stop_of_the_install_scripts_says_what_to_do_next(name: str) -> None:
    """Each message that stops the installation ends with an action (the skeptic, item 9)."""
    text = (SCRIPTS / name).read_text(encoding="utf-8").replace("\r\n", "\n")
    if name == "install.sh":
        flat = re.sub(r"\\\n", "", text)
        stops = re.findall(r'stop "((?:[^"\\]|\\.)*)"', flat)
        stops = [said for said in stops if "$*" not in said]
        advice = re.findall(r'venv_advice="((?:[^"\\]|\\.)*)"', flat)
        assert len(advice) == 2 and all("again" in said for said in advice), advice
    else:
        stops = re.findall(r"echo The installation stopped:(.*?)exit /b 1", text, re.S)
    assert len(stops) >= 8, stops
    for said in stops:
        assert "again" in said or "$venv_advice" in said, said


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
    # The run is taught with the environment switched on, so the plain
    # `synthtwin` line a run prints works as printed (the Codex review,
    # item 5); no step says to run it by its path in .venv instead.
    assert "source .venv/bin/activate\n" in install
    assert ".venv\\Scripts\\activate" in install
    assert ".venv/bin/synthtwin" not in readme
    # Command Prompt is where README sends a Windows user, and synthtwin
    # quotes for PowerShell: the paragraph says how to retype a quoted
    # path (the skeptic, item 4; the Codex review, item 5).
    windows = install[install.index("synthtwin writes the commands it prints for PowerShell") :]
    assert "between double quotes" in " ".join(windows[:400].split())
    assert "--isolated" in install and "PIP_CONFIG_FILE" in install


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
    assert _step_runs_on_a_shard_of_the_matrix(job, step), (
        "the step's condition names no shard the matrix has, so it never runs"
    )
    for used in re.findall(r"uses: (\S+)", text):
        assert re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", used), used


def _step_runs_on_a_shard_of_the_matrix(job: str, step: str) -> bool:
    """The step has no `if:`, or its `if:` is `matrix.shard == N` for a shard N of the matrix.

    Lane TI's skeptic, item 8a: `== 99` left the gate green.
    """
    shards = re.search(r"\n\s+shard: \[([\d, ]+)\]", job)
    if shards is None:
        return False
    condition = re.search(r"\n\s+if: (.+)", step)
    if condition is None:
        return True
    named = re.fullmatch(r"matrix\.shard == (\d+)", condition.group(1).strip())
    return named is not None and named.group(1) in re.split(r",\s*", shards.group(1))


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


def journey_measures(readme: "str | None" = None) -> "dict[str, int]":
    """K-S8-01: what README asks of a new user, from a folder to a validated twin.

    * `install_commands`: the lines of the first block of "Installing"
      that build the environment -- every line but getting the folder
      (`git clone`, `cd`) and a run of synthtwin itself -- plus 1 for an
      environment the block needs and does not make: a `pip install`
      line with no `venv` line and no install script beside it (lane
      TI's skeptic, item 7: base 3d89303's lone `pip install -e .` read
      1, the same as the one install command that replaced it);
    * `run_commands`: what a person types for one run in a new terminal
      window -- switching the environment on (1 where "Installing" tells
      them to, or where the environment was left unstated, since it is
      then theirs to switch on too), the `synthtwin` lines of the first
      block of "What works today", and 1 more for the run `--answers`
      repeats when README tells them to hand the questions file back
      (the Codex review of lane TI, item 12: a column that needs an
      answer is described twice);
    * `hand_edited_files`: the files README tells the reader to write
      answers into, counted by name in each paragraph that says so.

    Read from README.md (or the text given), so a lane that changes what
    a person does changes the number only by changing what README tells
    them.
    """
    if readme is None:
        readme = (REPO / "README.md").read_text(encoding="utf-8")
    installing = _section(readme, "Installing")
    block = _first_block(installing)
    install = [
        line
        for line in block
        if not line.startswith(("git clone", "cd ", "synthtwin ", ".venv"))
    ]
    unstated = int(
        any(line.startswith("pip install") for line in install)
        and not any("venv" in line or "scripts/install" in line for line in install)
    )
    told_to_switch_on = int("activate" in installing)
    works = _section(readme, "What works today")
    run = [line for line in _first_block(works) if line.startswith("synthtwin ")]
    answered_again = int("--answers" in works)
    edited: "set[str]" = set()
    for paragraph in readme.split("\n\n"):
        if "your_answer" in paragraph or "Fill it in" in paragraph:
            edited |= set(re.findall(r"[\w.-]+-questions\.json", paragraph))
    return {
        "install_commands": len(install) + unstated,
        "run_commands": max(unstated, told_to_switch_on) + len(run) + answered_again,
        "hand_edited_files": len(edited),
    }


def ci_systems_configured(workflow: str) -> int:
    """The systems of the tests job whose matrix reaches the install step."""
    job = workflow[workflow.index("  tests:") : workflow.index("  shard-coverage:")]
    step = job[job.index("Install from a wheel folder with the install script") :]
    step = step[: step.index("- name:")]
    if not (
        "sh scripts/install.sh" in step
        and "scripts\\\\install.bat" in step
        and _step_runs_on_a_shard_of_the_matrix(job, step)
    ):
        return 0
    return sum(
        1 for system in ("ubuntu-latest", "windows-latest", "macos-latest") if system in job
    )


def test_the_ci_count_sees_a_step_that_never_runs() -> None:
    """A condition no shard meets counts no system (the skeptic, item 8a)."""
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert ci_systems_configured(workflow) == 3
    never = workflow.replace(
        "        if: matrix.shard == 1\n        run: |\n          WHEELS=",
        "        if: matrix.shard == 99\n        run: |\n          WHEELS=",
    )
    assert never != workflow
    assert ci_systems_configured(never) == 0


def install_measures(folder: pathlib.Path) -> "dict[str, int]":
    """K-S8-04: `python -m synthtwin`, the scripts' hash check, CI, and doctor here.

    * `main_module_dispatches`: 1 when `src/synthtwin/__main__.py` exits
      with `cli.main()` under the `__main__` guard, read from its syntax
      (the behaviour is `test_python_dash_m_synthtwin_prints_the_version`);
    * `scripts_keeping_hash_check`: the install scripts that run both of
      README's offline pip commands flag for flag and end with doctor;
    * `ci_systems_configured_to_run_the_scripts`: the systems of the
      tests job whose matrix reaches the install step -- the step names
      both scripts and its `if:` names a shard the matrix has. It counts
      configuration, not a run: the run is proved by the first push that
      carries the lane (the Codex review, item 13);
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
    systems = ci_systems_configured(WORKFLOW.read_text(encoding="utf-8"))
    code = cli.main(["doctor", "--out-dir", str(folder)])
    return {
        "main_module_dispatches": dispatches,
        "scripts_keeping_hash_check": keeping,
        "ci_systems_configured_to_run_the_scripts": systems,
        "doctor_exit_here": code,
    }


# What base 3d89303's README asked, its two sections as they stood: the
# block of "Installing" and the opening of "What works today".
_BASE_README = """## What works today

Three commands, run one after the other. Each one ends by printing the
next.

```
synthtwin profile my-table.csv
synthtwin generate my-table-profile.json
synthtwin validate my-table-profile.json --twin my-table-twin.csv
```

- `my-table-questions.json` - the columns synthtwin could read more than
  one way, what it saw in each and what it read each as, with the
  answers you can give. Fill it in and hand it back with `--answers`.

## Installing

synthtwin is **not on PyPI** yet. To use all three commands from a
clone:

```
git clone https://github.com/alfredocr05/synthtwin
cd synthtwin
pip install -e .
synthtwin profile my-table.csv
synthtwin generate my-table-profile.json
synthtwin validate my-table-profile.json
```

## License
"""


def test_the_measures_read_what_they_say() -> None:
    """Non-vacuity: the README journey reads today's numbers, and the base's.

    Base 3d89303 reads 2 install commands (`pip install -e .` and the
    environment it needs and does not make) where the lane's README
    reads 1, so the measure sees the lane's change and would see a
    return to a lone `pip install` (lane TI's skeptic, item 7).
    """
    assert journey_measures(_BASE_README) == {
        "install_commands": 2,
        "run_commands": 5,
        "hand_edited_files": 1,
    }
    assert journey_measures() == {
        "install_commands": 1,
        "run_commands": 5,
        "hand_edited_files": 1,
    }
