"""P1-R7-F1 (neighbour): ANY exception leaves honest state.

The first repair caught PathValidationError beside ProfileError. The
next exception class walked straight through it: a MemoryError from the
write itself is caught nowhere in the transaction, and the command
printed advice about memory that names no file at all. The verified
disk state after injecting one on the second write was

    table-profile.json.synthtwin-part-1  "PROFILE-DERIVED\\n"
    table-profile.txt.synthtwin-part-1   ""

-- a complete description computed from the real table, left in a hidden
neighbour, with no cleanup and no sentence naming it.

So the transaction stopped enumerating exception types. It holds one
handler that does not ask what was raised: whatever it is, the working
files are cleared away and the person is told what is at each name, and
then the failure continues to the caller AS ITSELF, with its type and
its message intact, so that the advice belonging to it -- the memory
message and its "close other programs" guidance -- is still what they
read. The cause and the disk state are both needed: one says why it
stopped, the other says what they are holding.

KeyboardInterrupt and SystemExit are covered too, and deliberately.
Neither is an Exception, and a person pressing Ctrl-C during the write
of a large profile is not a rare case -- it is the ordinary way a slow
command ends. The cleanup runs for them exactly as for a MemoryError.
What is NOT changed is what the interrupt then does: it ends the command
the way every other command on their computer ends, rather than being
dressed up as a refusal synthtwin decided on.

Every test fixes the state on disk, makes exactly one operation fail,
and asserts both halves: every surviving byte, and the sentence the
person reads. Nothing in the package is stubbed; the product code runs
exactly as shipped.
"""

import pathlib

import pytest

import fixtures
from synthtwin import errors, profile
from synthtwin.cli import main

PROFILE_TEXT = '{\n  "profile_version": 2,\n  "note": "PROFILE-DERIVED"\n}\n'
SUMMARY_TEXT = "A summary of the table, for a person to read.\n"


def _outputs(folder: pathlib.Path) -> "tuple[pathlib.Path, pathlib.Path]":
    """The two names a run beside a table called clinic.csv would use."""
    return (folder / "clinic-profile.json", folder / "clinic-profile.txt")


def _neighbours(folder: pathlib.Path) -> "list[str]":
    """Every working file left in ``folder``, by name, sorted."""
    found = [
        entry.name
        for entry in folder.iterdir()
        if profile.PART_SUFFIX in entry.name
        or profile.KEPT_SUFFIX in entry.name
    ]
    return sorted(found)


def _break_the_write_of(
    monkeypatch: pytest.MonkeyPatch,
    doomed: pathlib.Path,
    failure: BaseException,
) -> None:
    """Raise ``failure`` from the write of exactly one file."""
    real = pathlib.Path.write_text
    wanted = f"{doomed}"

    def brittle(
        self: pathlib.Path,
        data: str,
        encoding: "str | None" = None,
        errors_: "str | None" = None,
        newline: "str | None" = None,
    ) -> int:
        if f"{self}" == wanted:
            raise failure
        return real(self, data, encoding=encoding, newline=newline)

    monkeypatch.setattr(pathlib.Path, "write_text", brittle)


def _break_the_rename_of(
    monkeypatch: pytest.MonkeyPatch,
    doomed: pathlib.Path,
    failure: BaseException,
) -> None:
    """Raise ``failure`` from the rename of exactly one file."""
    real = pathlib.Path.replace
    wanted = f"{doomed}"

    def brittle(self: pathlib.Path, target: object) -> pathlib.Path:
        if f"{self}" == wanted:
            raise failure
        return real(self, target)  # type: ignore[arg-type]

    monkeypatch.setattr(pathlib.Path, "replace", brittle)


def _fail_unlink_of(
    monkeypatch: pytest.MonkeyPatch, doomed: "list[pathlib.Path]"
) -> None:
    """Make `Path.unlink` fail for exactly the named files."""
    real = pathlib.Path.unlink
    wanted = [f"{one}" for one in doomed]

    def stubborn(self: pathlib.Path, missing_ok: bool = False) -> None:
        if f"{self}" in wanted:
            raise PermissionError(13, "Operation not permitted")
        real(self, missing_ok=missing_ok)

    monkeypatch.setattr(pathlib.Path, "unlink", stubborn)


# ---------------------------------------------------------------------
# 1. the reviewer's probe: memory exhausted on the second write
# ---------------------------------------------------------------------


def test_memory_exhausted_on_the_second_write_leaves_nothing_behind(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first, second = _outputs(tmp_path)
    first_part = pathlib.Path(f"{first}{profile.PART_SUFFIX}-1")
    _break_the_write_of(
        monkeypatch,
        pathlib.Path(f"{second}{profile.PART_SUFFIX}-1"),
        MemoryError("simulated"),
    )
    state = profile.DiskState()
    with pytest.raises(MemoryError) as caught:
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    # The failure reaches the caller as itself: the command recognizes
    # it by type and has its own advice for it.
    assert f"{caught.value}" == "simulated"
    # And the folder is honest again.
    assert not first_part.exists()
    assert _neighbours(tmp_path) == [], (
        "a working file holding a description of the real table may not "
        "survive an exception the transaction could observe"
    )
    assert not first.exists() and not second.exists()
    # And the person is told so, by name.
    assert "PROFILE-DERIVED" not in state.sentence
    assert f"{first}" in state.sentence and f"{second}" in state.sentence
    assert "No new description was published" in state.sentence
    assert "There is nothing left to clear up" in state.sentence


def test_a_working_file_that_survives_the_cleanup_is_named(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The state the reviewer found, with the cleanup also failing. The
    # transaction cannot make the folder clean, so the one thing it must
    # do instead is NAME what is there and say what it holds.
    first, second = _outputs(tmp_path)
    first_part = pathlib.Path(f"{first}{profile.PART_SUFFIX}-1")
    _break_the_write_of(
        monkeypatch,
        pathlib.Path(f"{second}{profile.PART_SUFFIX}-1"),
        MemoryError("simulated"),
    )
    _fail_unlink_of(monkeypatch, [first_part])
    state = profile.DiskState()
    with pytest.raises(MemoryError):
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert first_part.read_text(encoding="utf-8") == PROFILE_TEXT
    assert f"{first_part}" in state.sentence
    assert "holds text taken from your table" in state.sentence
    assert "Check each one before you use it" in state.sentence


def test_memory_exhausted_on_the_first_write_is_covered_too(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first, second = _outputs(tmp_path)
    _break_the_write_of(
        monkeypatch,
        pathlib.Path(f"{first}{profile.PART_SUFFIX}-1"),
        MemoryError("simulated"),
    )
    state = profile.DiskState()
    with pytest.raises(MemoryError):
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert _neighbours(tmp_path) == []
    assert "There is nothing left to clear up" in state.sentence


def test_an_earlier_profile_is_untouched_by_a_failure_in_the_writes(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first, second = _outputs(tmp_path)
    first.write_text("last week's profile\n", encoding="utf-8")
    second.write_text("last week's summary\n", encoding="utf-8")
    _break_the_write_of(
        monkeypatch,
        pathlib.Path(f"{second}{profile.PART_SUFFIX}-1"),
        MemoryError("simulated"),
    )
    state = profile.DiskState()
    with pytest.raises(MemoryError):
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert first.read_text(encoding="utf-8") == "last week's profile\n"
    assert second.read_text(encoding="utf-8") == "last week's summary\n"
    assert _neighbours(tmp_path) == []
    assert "the file that was there before this run, unchanged" in (
        state.sentence
    )


# ---------------------------------------------------------------------
# 2. the two failures that are not Exceptions
# ---------------------------------------------------------------------


def test_pressing_ctrl_c_during_the_write_still_clears_up(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # KeyboardInterrupt is not an Exception, and a person stopping a slow
    # write is the ordinary way this happens rather than a rare one.
    first, second = _outputs(tmp_path)
    _break_the_write_of(
        monkeypatch,
        pathlib.Path(f"{second}{profile.PART_SUFFIX}-1"),
        KeyboardInterrupt(),
    )
    state = profile.DiskState()
    with pytest.raises(KeyboardInterrupt):
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert _neighbours(tmp_path) == [], (
        "a person who presses Ctrl-C also leaves working files behind, "
        "and one of them holds a description of their table"
    )
    assert "There is nothing left to clear up" in state.sentence


def test_a_stopping_program_is_covered_on_the_same_rule(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first, second = _outputs(tmp_path)
    _break_the_write_of(
        monkeypatch,
        pathlib.Path(f"{second}{profile.PART_SUFFIX}-1"),
        SystemExit(1),
    )
    state = profile.DiskState()
    with pytest.raises(SystemExit):
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert _neighbours(tmp_path) == []
    assert "No new description was published" in state.sentence


# ---------------------------------------------------------------------
# 3. the same rule while the two names are being moved into place
# ---------------------------------------------------------------------


def test_a_failure_while_installing_the_profile_names_every_file(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # An earlier profile is set aside, and the rename that would put the
    # new one in its place stops for a reason the transaction did not
    # foresee. The old profile is now under a working name and the
    # profile's own name is empty: both facts must be in the sentence.
    first, second = _outputs(tmp_path)
    first.write_text("last week's profile\n", encoding="utf-8")
    first_part = pathlib.Path(f"{first}{profile.PART_SUFFIX}-1")
    kept = pathlib.Path(f"{first}{profile.KEPT_SUFFIX}-1")
    _break_the_rename_of(monkeypatch, first_part, MemoryError("simulated"))
    state = profile.DiskState()
    with pytest.raises(MemoryError):
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert kept.read_text(encoding="utf-8") == "last week's profile\n"
    assert not first.exists()
    assert not first_part.exists(), "the working files are still cleared away"
    assert f"{kept}" in state.sentence
    assert "moved here and could not move back" in state.sentence
    assert "was moved aside and could not be put back" in state.sentence
    assert "could not put things back as they were" in state.sentence


def test_a_failure_while_moving_the_earlier_profile_aside_guesses_nothing(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The narrowest window there is: the move of the earlier profile to
    # its working name was in flight. That name now holds either the
    # earlier profile or the empty file synthtwin made for it, and the
    # one thing that must not happen is a guess -- naming it "the
    # description from before this run" would be a guess, and removing
    # it would be a guess with the reader's only earlier profile.
    first, second = _outputs(tmp_path)
    first.write_text("last week's profile\n", encoding="utf-8")
    kept = pathlib.Path(f"{first}{profile.KEPT_SUFFIX}-1")
    _break_the_rename_of(monkeypatch, first, MemoryError("simulated"))
    state = profile.DiskState()
    with pytest.raises(MemoryError):
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert first.read_text(encoding="utf-8") == "last week's profile\n"
    assert _neighbours(tmp_path) == [kept.name], (
        "the one file under these names that this run did not produce "
        "is the reader's earlier profile, so nothing here is deleted"
    )
    assert f"{kept}" in state.sentence
    assert "cannot say which of this run's files ended up here" in (
        state.sentence
    )
    assert "moved here and could not move back" not in state.sentence, (
        "that would state as a fact something this run cannot know"
    )
    # The two working files this run DID produce are still cleared away.
    assert not pathlib.Path(f"{first}{profile.PART_SUFFIX}-1").exists()
    assert not pathlib.Path(f"{second}{profile.PART_SUFFIX}-1").exists()


def test_a_failure_with_no_earlier_profile_says_the_names_are_empty(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first, second = _outputs(tmp_path)
    first_part = pathlib.Path(f"{first}{profile.PART_SUFFIX}-1")
    _break_the_rename_of(monkeypatch, first_part, MemoryError("simulated"))
    state = profile.DiskState()
    with pytest.raises(MemoryError):
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert not first.exists() and not second.exists()
    assert _neighbours(tmp_path) == []
    assert "just as before this run" in state.sentence
    assert "moved aside" not in state.sentence, (
        "nothing was set aside in this run, so nothing may say one was"
    )


# ---------------------------------------------------------------------
# 4. what the person sees, end to end
# ---------------------------------------------------------------------


def test_the_command_prints_the_disk_state_and_then_the_memory_advice(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The whole item, through the words a person would type. Before the
    # repair the screen said only that memory ran out -- naming no file
    # -- while a complete real-derived profile sat in a hidden neighbour.
    table = fixtures.write(
        tmp_path,
        "clinic.csv",
        fixtures.single_column_table("age", ["41"] * 30),
    )
    _first, second = _outputs(tmp_path)
    _break_the_write_of(
        monkeypatch,
        pathlib.Path(f"{second}{profile.PART_SUFFIX}-1"),
        MemoryError("simulated"),
    )
    assert main(["profile", f"{table}"]) == 1
    told = capsys.readouterr().err

    assert "No new description was published" in told, (
        "the person must be told what is on disk, not only why it stopped"
    )
    assert "There was not enough memory to finish describing" in told, (
        "and the failure's own advice must still reach them"
    )
    assert "Close other programs" in told
    assert told.index("No new description") < told.index(
        "There was not enough memory"
    ), "what they are holding first, then why it stopped"
    assert _neighbours(tmp_path) == []
    assert sorted(entry.name for entry in tmp_path.iterdir()) == ["clinic.csv"]


def test_the_command_names_a_working_file_it_could_not_remove(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    table = fixtures.write(
        tmp_path,
        "clinic.csv",
        fixtures.single_column_table("age", ["41"] * 30),
    )
    first, second = _outputs(tmp_path)
    first_part = pathlib.Path(f"{first}{profile.PART_SUFFIX}-1")
    _break_the_write_of(
        monkeypatch,
        pathlib.Path(f"{second}{profile.PART_SUFFIX}-1"),
        MemoryError("simulated"),
    )
    _fail_unlink_of(monkeypatch, [first_part])
    assert main(["profile", f"{table}"]) == 1
    told = capsys.readouterr().err

    assert first_part.exists()
    assert f"{first_part}" in told
    assert "holds text taken from your table" in told


# ---------------------------------------------------------------------
# 5. nothing is said twice, and nothing is said without cause
# ---------------------------------------------------------------------


def test_a_refusal_the_transaction_composed_is_not_reported_twice(
    tmp_path: pathlib.Path
) -> None:
    # A ProfileError already carries the state of every name in its own
    # message. A second sentence saying the same thing would read as two
    # different accounts of one folder.
    first, second = _outputs(tmp_path)
    first.mkdir()
    state = profile.DiskState()
    with pytest.raises(errors.ProfileError) as caught:
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert state.sentence == ""
    assert f"{first}" in f"{caught.value}"


def test_an_ordinary_run_leaves_no_sentence_at_all(
    tmp_path: pathlib.Path,
) -> None:
    first, second = _outputs(tmp_path)
    state = profile.DiskState()
    left = profile.write_both_files(
        first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
    )
    assert left == []
    assert state.sentence == ""
    assert first.read_text(encoding="utf-8") == PROFILE_TEXT
    assert second.read_text(encoding="utf-8") == SUMMARY_TEXT
    assert _neighbours(tmp_path) == []


def test_a_caller_that_asks_for_no_sentence_still_gets_the_cleanup(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The record is optional. Leaving it out costs the caller the
    # sentence, never the cleanup: the file that must not survive is the
    # one holding text taken from the table.
    first, second = _outputs(tmp_path)
    _break_the_write_of(
        monkeypatch,
        pathlib.Path(f"{second}{profile.PART_SUFFIX}-1"),
        MemoryError("simulated"),
    )
    with pytest.raises(MemoryError):
        profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)

    assert _neighbours(tmp_path) == []
