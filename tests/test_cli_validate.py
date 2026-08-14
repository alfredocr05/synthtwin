"""`synthtwin validate` end to end (plan P3-D1, P3-D3, P3-D6; V6.5, V7).

The measurement itself is `tests/test_validation.py`'s subject. What is
checked here is the WIRING: the command, the one-target write
transaction under it, the exit codes automation reads, the quality
report's obligations, and the teaching chain that gets a person from one
command to the next.

Six properties, each checked against what actually reached the disk or
the screen rather than against what the code meant to do.

1. THE WHOLE CHAIN. profile, then generate, then validate, on a table
   this file builds from the seeded neutral fixtures -- so the producer,
   the loader, the generator, the validator and the report all run for
   real. A twin validated against its own description exits 0 and
   misses nothing.

2. THE EXIT-CODE SPLIT (V6.5). It is the machine channel this phase
   ships, so it is tested as one: 0 when the check ran and nothing was
   missed, 3 when it ran and something was, 1 when it could not run at
   all, 2 when the command line could not be used. A tool reading exit
   codes has to be able to tell a file that failed its check from a file
   that was never evaluated, and the difference between 3 and 1 is the
   whole of that.

3. THE REFUSALS, each twice. An exact-shape test says the sentence names
   what happened and what to do; a REACHABILITY test drives the real
   command to the state that produces it. The failure catalog forbids a
   catalogued message no code path raises, and a message asserted only
   by calling its builder is exactly that.

4. THE FORBIDDEN-TARGET SET, at both inputs. The report is one file and
   the command reads two, so the guarded source is a SET: neither the
   description nor the measured file may be landed on, by lexical path,
   by resolved path, or through a link. Each input crossed with each
   route is a case.

5. THE BOUNDARY, from both sides. A validate run DOES reach the table
   reader, and must -- measuring a file means describing it with the
   profiler's own producer. It must NOT reach the generator, whose
   planning defects a second opinion may not inherit and in which this
   package's only random number generator lives. And it may not write,
   move or re-encode either file it read.

6. DETERMINISM (V10). The same description and the same measured bytes
   produce the same report bytes, and the report names no path, so where
   the files sit cannot move them.

Every table here is built by the seeded neutral builders in
`fixtures.py` (plan D13: no data-format file is ever committed), and
every description by the REAL producer.
"""

import ast
import builtins
import hashlib
import pathlib
import typing

import pytest

import fixtures
from synthtwin import errors, profile, reading, taxonomy, writing
from synthtwin.cli import main

# ---------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------


def _plain_table(rows: int = 48) -> str:
    """A neutral two-column table: labels beside whole numbers."""
    made = [
        [fixtures.REGIONS[index % 4], f"{index % 7}"] for index in range(rows)
    ]
    return fixtures.rows_to_csv(["region", "visits"], made)


def _described(
    folder: pathlib.Path, text: str, name: str = "clinic.csv"
) -> pathlib.Path:
    """Write a table, describe it with the real producer, return the path."""
    table_path = fixtures.write(folder, name, text)
    table = reading.read_table(f"{table_path}")
    document = profile.build_document(table, taxonomy.Settings(), [])
    stem = f"{table_path.stem}"
    return fixtures.write_profile(folder, f"{stem}-profile.json", document)


def _twin_of(description: pathlib.Path) -> pathlib.Path:
    return description.parent / "clinic-twin.csv"


def _quality_of(description: pathlib.Path) -> pathlib.Path:
    return description.parent / "clinic-twin-quality.txt"


def _built(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    text: "str | None" = None,
) -> pathlib.Path:
    """A description with its twin already beside it; returns the description.

    Both commands are run for real and their output is swallowed, so a
    test below reads only what its own run printed.
    """
    description = _described(tmp_path, text if text is not None else _plain_table())
    assert main(["generate", f"{description}"]) == 0
    capsys.readouterr()
    return description


def _watching_imports(monkeypatch: pytest.MonkeyPatch) -> "list[str]":
    """Record every module name imported from now on.

    The recorder sees the import STATEMENT, not the module cache, so a
    module another test already imported is still recorded when this run
    reaches for it -- which is the point: the question is whether the
    validate path ASKS for the generator, not whether the generator
    happens to be in memory.
    """
    seen: list[str] = []
    real = builtins.__import__

    def watched(
        name: str,
        where: "dict[str, typing.Any] | None" = None,
        inside: "dict[str, typing.Any] | None" = None,
        fromlist: "tuple[str, ...] | None" = None,
        level: int = 0,
    ) -> object:
        seen.append(name)
        for extra in fromlist if fromlist else ():
            seen.append(f"{name}.{extra}")
        return real(name, where, inside, fromlist, level)  # type: ignore[arg-type]

    monkeypatch.setattr(builtins, "__import__", watched)
    return seen


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _said(text: str) -> str:
    """One surface with runs of whitespace collapsed to single spaces.

    The report is hard-wrapped for a person to read, and where a line
    happens to break is not a claim anybody made. The claim inventory
    normalizes the same way and for the same reason: what is asserted
    below is what a sentence SAYS, not where it wrapped.
    """
    return " ".join(text.split())


# ---------------------------------------------------------------------
# 1. the whole chain
# ---------------------------------------------------------------------


def test_the_three_commands_run_one_after_the_other(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """profile, generate, validate: five files, and nothing missed.

    The end-to-end property the phase exists for. It is asserted on the
    FILES rather than on the return values alone, because a run that
    exits 0 without writing the report has not validated anything.
    """
    table = fixtures.write(tmp_path, "clinic.csv", _plain_table())
    assert main(["profile", f"{table}"]) == 0
    description = tmp_path / "clinic-profile.json"
    assert main(["generate", f"{description}"]) == 0
    assert main(["validate", f"{description}"]) == 0
    capsys.readouterr()
    written = sorted(path.name for path in tmp_path.iterdir())
    assert written == [
        "clinic-profile.json",
        "clinic-profile.txt",
        "clinic-twin-quality.txt",
        "clinic-twin-report.txt",
        "clinic-twin.csv",
        "clinic.csv",
    ]
    report = _said(_quality_of(description).read_text(encoding="utf-8"))
    assert "NO CHECKABLE OBLIGATION WAS MISSED." in report


def test_the_report_reaches_the_screen_and_the_file_as_one_text(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Neither sink can say something the other does not."""
    description = _built(tmp_path, capsys)
    assert main(["validate", f"{description}"]) == 0
    printed = capsys.readouterr().out
    written = _quality_of(description).read_text(encoding="utf-8")
    assert written in printed


def test_the_twin_can_be_named_explicitly(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`--twin` measures the file it names, wherever that file is."""
    description = _built(tmp_path, capsys)
    elsewhere = tmp_path / "somewhere"
    elsewhere.mkdir()
    moved = elsewhere / "other.csv"
    moved.write_text(
        _twin_of(description).read_text(encoding="utf-8"),
        encoding="utf-8",
        newline="",
    )
    _twin_of(description).unlink()
    assert main(["validate", f"{description}", "--twin", f"{moved}"]) == 0
    capsys.readouterr()
    assert _quality_of(description).is_file()


def test_the_report_goes_where_out_dir_says(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    description = _built(tmp_path, capsys)
    folder = tmp_path / "reports"
    folder.mkdir()
    assert main(["validate", f"{description}", "--out-dir", f"{folder}"]) == 0
    capsys.readouterr()
    assert (folder / "clinic-twin-quality.txt").is_file()
    assert not _quality_of(description).exists()


# ---------------------------------------------------------------------
# 2. the exit-code split (V6.5)
# ---------------------------------------------------------------------


def test_a_file_that_misses_an_obligation_exits_three(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A perturbed twin exits 3, and the report names what it missed.

    The perturbation is a row removed from the end of the twin, which no
    conforming twin of this description can be: the description publishes
    a row count and the file no longer holds it. Exit 3 and exit 0 are
    the two halves of the machine channel, so both are asserted in this
    file against a real run.
    """
    description = _built(tmp_path, capsys)
    twin = _twin_of(description)
    lines = twin.read_text(encoding="utf-8").split("\n")
    # The text ends with a newline, so the last element is empty; the
    # row before it is the one dropped.
    twin.write_text(
        "\n".join(lines[: len(lines) - 2]) + "\n", encoding="utf-8", newline=""
    )
    assert main(["validate", f"{description}"]) == 3
    capsys.readouterr()
    report = _said(_quality_of(description).read_text(encoding="utf-8"))
    assert "CHECKABLE OBLIGATION(S) WERE MISSED." in report
    assert "MISSED" in report
    assert "NO CHECKABLE OBLIGATION WAS MISSED." not in report


def test_a_missed_run_still_writes_the_report(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Exit 3 is a verdict, not a refusal: the product is still produced.

    "The report is the product even when the news is bad" (V9). A run
    that exited 3 without writing anything would leave the person with a
    number and no explanation of it.
    """
    description = _built(tmp_path, capsys)
    twin = _twin_of(description)
    twin.write_text(
        twin.read_text(encoding="utf-8") + "north,3\n",
        encoding="utf-8",
        newline="",
    )
    assert main(["validate", f"{description}"]) == 3
    capsys.readouterr()
    assert _quality_of(description).is_file()


def test_a_structural_mismatch_is_a_verdict_and_not_a_refusal(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A wrong column name is MISSED with an explanation, never a stop.

    V9 names this one explicitly, because the obvious implementation
    refuses: the reader is handed a file whose header does not match, and
    stopping there would be the easy thing to do. The plan is explicit
    that it must not, so this drives it.
    """
    description = _built(tmp_path, capsys)
    twin = _twin_of(description)
    lines = twin.read_text(encoding="utf-8").split("\n")
    lines[0] = "region,visitcount"
    twin.write_text("\n".join(lines), encoding="utf-8", newline="")
    assert main(["validate", f"{description}"]) == 3
    told = capsys.readouterr()
    assert _quality_of(description).is_file()
    assert "Traceback" not in told.err


def test_a_repeated_header_name_writes_a_report_and_quotes_nothing(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Review item P3-V1-F10, end to end.

    A file whose first row uses one name twice was refused by the
    profiler's own reader, in a sentence that QUOTED the repeated name.
    Reached from `validate` that did two forbidden things at once: it
    printed a string out of a file nobody promised was the reader's, and
    it turned a wrong name into a run that never happened. Both halves
    are asserted here on what actually reached the disk and the screen:
    exit 3 with the report written, and the spelling in no byte of any
    surface.
    """
    description = _built(tmp_path, capsys)
    twin = _twin_of(description)
    marker = "zzmarkerzz"
    rows = [f"{index % 4},{index % 7}" for index in range(48)]
    twin.write_text(
        f"{marker},{marker}\n" + "\n".join(rows) + "\n",
        encoding="utf-8",
        newline="",
    )
    assert main(["validate", f"{description}"]) == 3
    told = capsys.readouterr()
    report = _quality_of(description)
    assert report.is_file(), "a structural mismatch is still a report"
    for surface in (report.read_text(encoding="utf-8"), told.out, told.err):
        assert marker not in surface
    assert "Traceback" not in told.err


def test_a_command_line_that_cannot_be_used_exits_two(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["validate"])
    assert caught.value.code == 2
    told = capsys.readouterr().err
    assert "synthtwin validate my-table-profile.json" in told
    assert "--twin" in told


def test_a_description_that_cannot_be_loaded_exits_one(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Could-not-run is 1, which is what makes 3 mean what it means."""
    not_a_description = fixtures.write(tmp_path, "clinic.csv", "a,b\n1,2\n")
    assert main(["validate", f"{not_a_description}"]) == 1
    told = capsys.readouterr().err
    assert "description" in told
    for jargon in ("Traceback", "JSONDecodeError", "None"):
        assert jargon not in told


def test_a_measured_file_that_is_not_there_exits_one(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    description = _described(tmp_path, _plain_table())
    assert main(["validate", f"{description}"]) == 1
    told = capsys.readouterr().err
    assert "no file" in told or "There is no" in told
    assert not _quality_of(description).exists(), (
        "a check that could not run must write nothing"
    )


def test_a_measured_file_that_is_a_folder_exits_one(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    description = _described(tmp_path, _plain_table())
    folder = tmp_path / "clinic-twin.csv"
    folder.mkdir()
    assert main(["validate", f"{description}"]) == 1
    assert "folder" in capsys.readouterr().err


# ---------------------------------------------------------------------
# 3. the new refusals: exact shape, and reachable
# ---------------------------------------------------------------------


def test_the_taken_target_refusal_has_its_exact_shape() -> None:
    message = errors.quality_target_already_there("/d/clinic-twin-quality.txt")
    assert "/d/clinic-twin-quality.txt" in message
    assert "one file" in message
    assert "--replace" in message
    assert "Nothing was written" in message
    assert "\n" not in message, (
        "a refusal is shown as a value on its way to the screen, so a "
        "line feed inside one reaches the reader as text"
    )


def test_the_taken_target_refusal_is_reachable(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """And the bytes that were there are still there afterwards."""
    description = _built(tmp_path, capsys)
    target = _quality_of(description)
    mine = "a file of my own that happens to sit here\n"
    target.write_text(mine, encoding="utf-8", newline="")
    assert main(["validate", f"{description}"]) == 1
    told = capsys.readouterr().err
    assert f"{target}" in told
    assert "--replace" in told
    assert target.read_text(encoding="utf-8") == mine


def test_replace_lets_the_run_write_over_its_own_earlier_report(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    description = _built(tmp_path, capsys)
    assert main(["validate", f"{description}"]) == 0
    first = _quality_of(description).read_text(encoding="utf-8")
    assert main(["validate", f"{description}", "--replace"]) == 0
    capsys.readouterr()
    assert _quality_of(description).read_text(encoding="utf-8") == first


def test_the_replaced_input_refusal_has_its_exact_shape() -> None:
    message = errors.output_would_replace_an_input(
        "/d/clinic-profile.json",
        errors.INPUT_DESCRIPTION,
        errors.QUALITY_WORDS,
    )
    assert "/d/clinic-profile.json" in message
    assert "the description" in message
    assert "the quality report" in message
    assert "Nothing was written" in message
    assert "run the command again" in message
    assert "\n" not in message


def test_the_replaced_input_refusal_names_which_input_it_caught() -> None:
    """Two inputs, and the person is told which one was about to go.

    One `ArtifactWords` carries one handed-in noun, and this command is
    handed two files. A refusal that said only "one of the files you gave
    me" would send somebody to check the wrong one.
    """
    on_description = errors.output_would_replace_an_input(
        "/d/p.json", errors.INPUT_DESCRIPTION, errors.QUALITY_WORDS
    )
    on_measured = errors.output_would_replace_an_input(
        "/d/t.csv", errors.INPUT_MEASURED_FILE, errors.QUALITY_WORDS
    )
    assert on_description != on_measured
    assert errors.INPUT_MEASURED_FILE in on_measured
    assert errors.INPUT_MEASURED_FILE not in on_description


def test_the_memory_refusal_has_its_exact_shape() -> None:
    message = errors.quality_out_of_memory("/d/clinic-profile.json")
    assert "/d/clinic-profile.json" in message
    assert "memory" in message
    assert "Nothing was written" in message
    assert "run the command again" in message


def test_the_memory_refusal_is_reachable(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Driven by exhausting memory where a real run can exhaust it.

    A catalogued message no code path raises is dead weight that reads
    like a promise, so this reaches the sentence through the command
    rather than by calling the builder. The failure is injected into the
    write, which is the last thing a validate run does and the one place
    the branch's own handler cannot compose a message of its own.
    """
    description = _built(tmp_path, capsys)

    def exhausted(
        self: pathlib.Path, *rest: object, **named: object
    ) -> None:
        raise MemoryError("no room")

    monkeypatch.setattr(pathlib.Path, "write_text", exhausted)
    assert main(["validate", f"{description}"]) == 1
    told = capsys.readouterr().err
    assert "not enough memory" in told
    assert "Nothing was written" in told
    assert not _quality_of(description).exists()


# ---------------------------------------------------------------------
# 4. the forbidden-target set: both inputs, several routes
# ---------------------------------------------------------------------


def test_a_report_that_would_land_on_the_description_is_refused(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A link at the report's name pointing back at the description.

    The locality gate cannot catch this one: a link resolves to a
    permitted local path. What would be destroyed is the description the
    verdicts are measured against.
    """
    description = _built(tmp_path, capsys)
    target = _quality_of(description)
    target.symlink_to(description)
    before = description.read_bytes()
    assert main(["validate", f"{description}", "--replace"]) == 1
    told = capsys.readouterr().err
    assert "description" in told
    assert description.read_bytes() == before
    assert target.is_symlink(), "the link itself must be left alone"


def test_a_report_that_would_land_on_the_measured_file_is_refused(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The second input, crossed with the same route.

    This is the one the two-file transaction could not have caught: its
    guarded source is the ONE file its command was handed, and here the
    file about to be destroyed is the other one -- which on this command
    may be somebody's own table rather than a twin.
    """
    description = _built(tmp_path, capsys)
    twin = _twin_of(description)
    target = _quality_of(description)
    target.symlink_to(twin)
    before = twin.read_bytes()
    assert main(["validate", f"{description}", "--replace"]) == 1
    told = capsys.readouterr().err
    assert errors.INPUT_MEASURED_FILE in told
    assert twin.read_bytes() == before


def test_a_report_named_as_the_measured_file_itself_is_refused(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The lexical route: --twin naming the file the report would be.

    No link is involved. The person points `--twin` at the name the
    report is derived to, which is a thing somebody will eventually do
    by accident with `--out-dir` and a tidy folder.
    """
    description = _built(tmp_path, capsys)
    target = _quality_of(description)
    target.write_text(_twin_of(description).read_text(encoding="utf-8"), encoding="utf-8", newline="")
    before = target.read_bytes()
    assert (
        main(["validate", f"{description}", "--twin", f"{target}", "--replace"])
        == 1
    )
    told = capsys.readouterr().err
    assert errors.INPUT_MEASURED_FILE in told
    assert target.read_bytes() == before


def test_the_transaction_refuses_a_guarded_source_before_writing(
    tmp_path: pathlib.Path
) -> None:
    """The one-target transaction's own guard, driven directly.

    The command checks the names before it measures anything; this
    checks that the transaction underneath refuses too, so a caller that
    forgot the earlier check still cannot write over an input.
    """
    source = fixtures.write(tmp_path, "an-input.txt", "the input\n")
    target = tmp_path / "report.txt"
    target.symlink_to(source)
    with pytest.raises(errors.ProfileError) as stopped:
        writing.write_one_file(
            target,
            "a report\n",
            sources=[(source, errors.INPUT_DESCRIPTION)],
            words=errors.QUALITY_WORDS,
        )
    assert errors.INPUT_DESCRIPTION in f"{stopped.value}"
    assert source.read_text(encoding="utf-8") == "the input\n"


def test_the_transaction_writes_one_file_or_leaves_the_folder_alone(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The one-target form's own rule, with the write made to fail.

    Two-files-or-neither is not a rule this form can keep. What it keeps
    is every other one: the name holds what it held, no working file is
    left behind, and the person is told which file could not be written
    in the words of the command that was running.
    """
    target = tmp_path / "clinic-twin-quality.txt"

    def refuse(self: pathlib.Path, *rest: object, **named: object) -> None:
        raise OSError(30, "Read-only file system")

    monkeypatch.setattr(pathlib.Path, "write_text", refuse)
    with pytest.raises(errors.ProfileError) as stopped:
        writing.write_one_file(
            target, "a report\n", words=errors.QUALITY_WORDS
        )
    message = f"{stopped.value}"
    assert "The quality report could not be written to" in message
    assert "The profile could not be written to" not in message
    assert "The twin could not be written to" not in message
    monkeypatch.undo()
    assert sorted(path.name for path in tmp_path.iterdir()) == []


def test_the_transaction_puts_an_earlier_report_back(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An earlier report is set aside and restored when the move fails.

    Only the INSTALL is made to fail -- the move of the working file onto
    the output name -- and the restore that follows it is left working.
    Failing every move onto that name would be testing a different thing:
    a rollback that could not finish, which has its own wording and its
    own test in the two-file battery.
    """
    target = fixtures.write(tmp_path, "report.txt", "last week's verdict\n")
    real = pathlib.Path.replace

    def fail_the_install(self: pathlib.Path, other: object) -> pathlib.Path:
        installing = writing.PART_SUFFIX in f"{self}"
        if installing and f"{other}" == f"{target}":
            raise OSError(13, "Permission denied")
        return real(self, other)  # type: ignore[arg-type]

    monkeypatch.setattr(pathlib.Path, "replace", fail_the_install)
    with pytest.raises(errors.ProfileError) as stopped:
        writing.write_one_file(
            target, "this week's verdict\n", words=errors.QUALITY_WORDS
        )
    monkeypatch.undo()
    assert target.read_text(encoding="utf-8") == "last week's verdict\n"
    assert "No new description was published" in f"{stopped.value}"
    left = [
        path.name
        for path in tmp_path.iterdir()
        if writing.PART_SUFFIX in path.name or writing.KEPT_SUFFIX in path.name
    ]
    assert left == [], f"working files were left behind: {left}"


# ---------------------------------------------------------------------
# 5. the boundary, from both sides
# ---------------------------------------------------------------------


def test_a_validate_run_never_asks_for_the_generator(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The whole run, from the command line to the written report.

    Two obligations in one assertion (plan P3-D1). A check that called
    the planner would inherit every planning defect of the thing it is
    checking; and the generator is where this package's only random
    number generator lives, so importing it would put a random source in
    the closure of a command whose bytes must be a fixed function of its
    two files.

    `rendering` is in this list for a reason that looks like an
    implementation detail and is not: it imports the generator, so a
    quality report rendered there would cross both lines at once. That is
    why the report is rendered by `quality`.
    """
    description = _built(tmp_path, capsys)
    seen = _watching_imports(monkeypatch)
    assert main(["validate", f"{description}"]) == 0
    capsys.readouterr()
    for forbidden in (
        "synthtwin.generation",
        "synthtwin.rendering",
        "numpy",
        "numpy.random",
    ):
        assert forbidden not in seen, (
            f"a validate run reached for {forbidden}, which puts the "
            f"planner's own defects -- and a random source -- inside a "
            f"second opinion that may carry neither"
        )
    assert "synthtwin.validation" in seen, (
        "the recorder must be seeing this run's imports at all"
    )


_PACKAGE = pathlib.Path(__file__).resolve().parents[1] / "src" / "synthtwin"


def _parsed(module: str) -> ast.Module:
    return ast.parse((_PACKAGE / f"{module}.py").read_text(encoding="utf-8"))


def _named_in(nodes: "typing.Iterable[ast.AST]") -> "list[str]":
    """Every module name imported by the given syntax nodes.

    The names come back as they are written -- `numpy.random`,
    `synthtwin.generation`, `math` -- because what the assertions below
    ask is whether a name appears at all, not what it resolves to.
    """
    found: list[str] = []
    for node in nodes:
        if isinstance(node, ast.Import):
            for alias in node.names:
                found = found + [alias.name]
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            found = found + [node.module]
            for alias in node.names:
                found = found + [f"{node.module}.{alias.name}"]
    return found


def _imports_of(module: str) -> "list[str]":
    """Every module `module` imports, read off its source rather than run."""
    return _named_in(ast.walk(_parsed(module)))


def _validate_branch_imports() -> "list[str]":
    """What a validate run imports from `cli`, and nothing another does.

    `cli` imports each command's modules inside that command's own
    branch, so walking the whole file would attribute the generator to
    every run. What a validate run reaches is the file's module-level
    imports -- every run reaches those, whatever was typed -- plus the
    ones inside `_run_validate`. Both are read from the syntax, so the
    walk tracks the branch rather than a list somebody has to remember.
    """
    tree = _parsed("cli")
    found = _named_in(tree.body)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_run_validate":
            found = found + _named_in(ast.walk(node))
    return found


def _validate_closure() -> "set[str]":
    """Every package module a validate run can reach, statically.

    The walk starts at what the validate branch itself imports and
    follows package imports to a fixed point. Names that are not this
    package's own are recorded by the caller, not followed.
    """
    start = {"cli"}
    for name in _validate_branch_imports():
        if name.startswith("synthtwin."):
            inner = name[len("synthtwin.") :].split(".")[0]
            if (_PACKAGE / f"{inner}.py").is_file():
                start.add(inner)
    reached = set(start)
    frontier = list(start)
    while frontier:
        module = frontier.pop()
        if module == "cli":
            # Its other branches belong to the other commands, and
            # `_validate_branch_imports` has already contributed the
            # part of it a validate run reaches.
            continue
        for name in _imports_of(module):
            if not name.startswith("synthtwin."):
                continue
            inner = name[len("synthtwin.") :].split(".")[0]
            if inner in reached:
                continue
            if not (_PACKAGE / f"{inner}.py").is_file():
                continue
            reached.add(inner)
            frontier.append(inner)
    return reached


def test_no_module_a_validate_run_can_reach_holds_a_random_source() -> None:
    """The static form of the boundary above, which a fixture cannot give.

    The import-watching test drives one description down one path. This
    one walks the whole closure a validate run can reach and asserts the
    generator is not in it and no module in it names numpy -- so a random
    source added behind a branch no fixture happens to take is caught
    too. Plan P3-D1 asks for exactly this scope: no RNG import in the
    validate closure.
    """
    closure = _validate_closure()
    assert "generation" not in closure, (
        "the generator is reachable from a validate run, so a second "
        "opinion can inherit the planner's own defects"
    )
    assert "rendering" not in closure, (
        "`rendering` imports the generator, so reaching it from a "
        "validate run reaches the generator too -- which is why the "
        "quality report is rendered by `quality`"
    )
    carrying = [
        module
        for module in sorted(closure)
        if module != "cli"
        and any(name.startswith("numpy") for name in _imports_of(module))
    ]
    if any(
        name.startswith("numpy") for name in _validate_branch_imports()
    ):
        carrying = carrying + ["cli"]
    assert carrying == [], (
        f"these modules are reachable from a validate run and name "
        f"numpy: {carrying}. Validation consumes no randomness, and the "
        f"report's bytes must be a fixed function of its two files."
    )
    # A floor under the walk: if the closure ever came back nearly
    # empty, both assertions above would pass by finding nothing.
    assert "validation" in closure and "reading" in closure
    assert len(closure) >= 8, f"the closure walk found only {closure}"


def test_the_closure_walk_can_fail() -> None:
    """The same walk, pointed at `generate`, finds what it must find.

    A static reachability check passes trivially when the walk is wrong:
    a renamed function, a changed prefix, a loop that never runs. The
    generate branch DOES import the generator, and the generator DOES
    name numpy, so running the identical machinery over it and finding
    both is the proof that finding neither above meant something.
    """
    tree = _parsed("cli")
    inside: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_run_generate":
            inside = inside + _named_in(ast.walk(node))
    assert "synthtwin.generation" in inside, (
        "the walk no longer finds the generator where it certainly is, "
        "so the validate-closure assertions above are checking nothing"
    )
    assert any(
        name.startswith("numpy") for name in _imports_of("generation")
    ), "the numpy test no longer finds numpy where it certainly is"


def test_a_validate_run_does_reach_the_reader(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The other side of the fence, asserted rather than assumed.

    The boundary this project keeps was never "nothing but the profiler
    opens a file" -- it is that GENERATION never does. Measuring a file
    means describing it with the profiler's own producer, so this branch
    reaches the reader by design, and a test that only forbade things
    would let a future change quietly stop measuring.
    """
    description = _built(tmp_path, capsys)
    seen = _watching_imports(monkeypatch)
    assert main(["validate", f"{description}"]) == 0
    capsys.readouterr()
    assert "synthtwin.reading" in seen or "synthtwin.validation" in seen


def test_validation_writes_nothing_but_the_report(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Neither input is written, moved, truncated or re-encoded (V1.3)."""
    description = _built(tmp_path, capsys)
    twin = _twin_of(description)
    before = (description.read_bytes(), twin.read_bytes())
    assert main(["validate", f"{description}"]) == 0
    capsys.readouterr()
    assert (description.read_bytes(), twin.read_bytes()) == before


# ---------------------------------------------------------------------
# 6. determinism (V10)
# ---------------------------------------------------------------------


def test_the_same_inputs_give_the_same_report_bytes(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Two runs, byte for byte, with the report removed in between."""
    description = _built(tmp_path, capsys)
    assert main(["validate", f"{description}"]) == 0
    first = _quality_of(description).read_bytes()
    _quality_of(description).unlink()
    assert main(["validate", f"{description}"]) == 0
    capsys.readouterr()
    assert _quality_of(description).read_bytes() == first


def test_where_the_files_sit_cannot_move_the_report(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The report names no path, so the same check writes the same bytes.

    This is what makes V10's scope -- the description's bytes and the
    measured file's bytes -- true rather than nearly true: a report that
    printed where it was written would differ between two folders holding
    identical files.
    """
    description = _built(tmp_path, capsys)
    assert main(["validate", f"{description}"]) == 0
    here = _quality_of(description).read_text(encoding="utf-8")
    capsys.readouterr()

    elsewhere = tmp_path / "deeper" / "still"
    elsewhere.mkdir(parents=True)
    for name in ("clinic-profile.json", "clinic-twin.csv"):
        (elsewhere / name).write_text(
            (tmp_path / name).read_text(encoding="utf-8"),
            encoding="utf-8",
            newline="",
        )
    assert main(["validate", f"{elsewhere / 'clinic-profile.json'}"]) == 0
    capsys.readouterr()
    there = (elsewhere / "clinic-twin-quality.txt").read_text(
        encoding="utf-8"
    )
    assert _digest(there) == _digest(here)
    assert f"{tmp_path}" not in here, "no path may reach the report"


# ---------------------------------------------------------------------
# the report's own obligations (V7)
# ---------------------------------------------------------------------


def test_the_summary_is_generated_from_the_census_alone(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The five counts add to the stated total, and nothing claims more.

    V7.2's identity, read off the report a real run wrote. A verdict that
    fell out of the census on its way to the page shows up here as a
    total that does not add up.
    """
    from synthtwin import contract, quality, validation

    description = _built(tmp_path, capsys)
    loaded = contract.load_profile(f"{description}")
    outcome = validation.measure(loaded, f"{_twin_of(description)}")
    census = outcome.census
    total = quality.checkable_total(census)
    assert total == (
        census.held
        + census.within_bound
        + census.authorized_deviation
        + census.withheld
        + census.missed
    )
    assert total == len(outcome.checks)
    assert census.not_checkable == len(outcome.listings)
    report = _said(quality.quality_report(loaded, outcome))
    assert f"sets {total} obligation(s)" in report
    assert f"add to {total}" in report
    assert f"A further {census.not_checkable} obligation(s)" in report


def test_no_report_says_every_published_fact_was_found(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The sentence V7.2 forbids appears on no output, on any fixture.

    It is checked on the every-role table, which carries approximated
    facts and authorized corners -- exactly the description on which
    "every published fact was found" would be false by construction.
    """
    description = _described(
        tmp_path, fixtures.every_role_table(n_rows=120), "clinic.csv"
    )
    assert main(["generate", f"{description}"]) == 0
    capsys.readouterr()
    assert main(["validate", f"{description}"]) == 0
    printed = capsys.readouterr()
    report = _quality_of(description).read_text(encoding="utf-8")
    for surface in (report, printed.out, printed.err):
        lowered = _said(surface).lower()
        for forbidden in (
            "every published fact was found",
            "every fact was found",
            "all published facts were found",
            "the twin is faithful",
            "fully validated",
        ):
            assert forbidden not in lowered, forbidden


def test_the_report_carries_its_limits_on_every_run(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """V7.3, V7.4 and V7.5, none of them conditional on the verdict."""
    description = _built(tmp_path, capsys)
    assert main(["validate", f"{description}"]) == 0
    capsys.readouterr()
    report = _said(_quality_of(description).read_text(encoding="utf-8"))
    for wanted in (
        # V7.3: the three inherited limits and the verdict-scope sentence
        "NO CROSS-COLUMN STRUCTURE WAS VALIDATED",
        "ROWS ARE TREATED AS INDEPENDENT",
        "never says what one row of the real table is",
        "NOT RESEARCH RESULTS",
        "not a verdict that the file is fit for any analysis",
        "cannot tell a",
        "nothing in a CSV proves",
        # V7.4: what is checked, and what is not
        "IF YOU CAME TO THIS REPORT WITH A QUESTION",
        "CHECKED IN THIS VERSION",
        "NOT CHECKABLE IN THIS VERSION",
        "any target that ties two columns together",
        "Nothing here promises when.",
        # V7.5: the fourth artifact
        "All four files a full run produces",
        (
            "the description, the twin, the twin's report and this "
            "quality report"
        ),
        # the not-checkable census
        "WHAT COULD NOT BE CHECKED, AND WHY",
    ):
        assert wanted in report, wanted


def test_the_report_promises_nothing_about_a_later_version(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """V7.4 commits to no version, no slot and no date."""
    description = _built(tmp_path, capsys)
    assert main(["validate", f"{description}"]) == 0
    capsys.readouterr()
    lowered = _said(
        _quality_of(description).read_text(encoding="utf-8")
    ).lower()
    for forbidden in ("phase 4", "phase 5", "phase 6", "version 2", "2027"):
        assert forbidden not in lowered, forbidden


# ---------------------------------------------------------------------
# the teaching chain (plan P3-D6)
# ---------------------------------------------------------------------


def test_a_finished_generate_run_teaches_the_validate_command(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The chain's middle link, with this twin's own paths in it.

    The line is asserted to be RUNNABLE, not merely present: what it
    prints is fed back through the command.
    """
    description = _described(tmp_path, _plain_table())
    assert main(["generate", f"{description}"]) == 0
    printed = capsys.readouterr().out
    expected = (
        f"  synthtwin validate {description} --twin {_twin_of(description)}"
    )
    assert "Next, measure the twin against the description:" in printed
    assert expected in printed
    assert main(["validate", f"{description}", "--twin", f"{_twin_of(description)}"]) == 0
    capsys.readouterr()
    assert _quality_of(description).is_file()


def test_a_finished_validate_run_says_what_the_verdict_means(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The chain's last link: what it means, what it does not, which code."""
    description = _built(tmp_path, capsys)
    assert main(["validate", f"{description}"]) == 0
    printed = _said(capsys.readouterr().out)
    assert "No checkable obligation was missed." in printed
    assert "not a verdict that the file is fit for any analysis" in printed
    assert "cannot tell a synthetic file from a real one" in printed
    assert "Automation saw exit code 0" in printed


def test_a_missed_validate_run_says_which_code_automation_saw(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    description = _built(tmp_path, capsys)
    twin = _twin_of(description)
    twin.write_text(
        twin.read_text(encoding="utf-8") + "north,3\n",
        encoding="utf-8",
        newline="",
    )
    assert main(["validate", f"{description}"]) == 3
    printed = _said(capsys.readouterr().out)
    assert "checkable obligation(s) were missed" in printed
    assert "Automation saw exit code 3" in printed


def test_the_profiler_teaches_the_whole_chain(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The summary a `profile` run prints names the third command too."""
    table = fixtures.write(tmp_path, "clinic.csv", _plain_table())
    assert main(["profile", f"{table}"]) == 0
    printed = capsys.readouterr().out
    assert "synthtwin validate" in printed


def test_the_status_screen_names_all_three_commands(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main([]) == 0
    out = capsys.readouterr().out
    for word in ("synthtwin profile", "synthtwin generate", "synthtwin validate"):
        assert word in out


# ---------------------------------------------------------------------
# what may be said out loud (V5.4)
# ---------------------------------------------------------------------


def test_no_string_from_the_measured_file_reaches_any_output(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A file holding a spelling the description never published.

    The measured file may be anything, so the report has to be safe to
    exist whatever it turns out to be. Here the file is the twin with one
    label replaced by a word that appears nowhere in the description; the
    word must appear in no byte of the report, the screen or the error
    stream.
    """
    description = _built(tmp_path, capsys)
    twin = _twin_of(description)
    marker = "zzmarkerzz"
    twin.write_text(
        twin.read_text(encoding="utf-8").replace("north", marker, 1),
        encoding="utf-8",
        newline="",
    )
    assert f"{marker}" not in description.read_text(encoding="utf-8")
    code = main(["validate", f"{description}"])
    assert code in (0, 3)
    printed = capsys.readouterr()
    report = _quality_of(description).read_text(encoding="utf-8")
    for surface in (report, printed.out, printed.err):
        assert marker not in surface
