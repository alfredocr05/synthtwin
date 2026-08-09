"""P1-R8-F1: an interrupt inside a working-name creation names its file.

The transaction survives an interrupt in the writes and in the renames
and leaves nothing data-bearing behind. One moment earlier than any of
those was still uncovered.

`pathlib.Path.touch(exist_ok=False)` creates the file through the
operating system and THEN hands back to Python. A KeyboardInterrupt
landing in that window leaves the file on disk while the run never
recorded that it owns the name: the local variable that would have held
it was never assigned, the cleanup inventory did not mention it, and the
sentence about what is on disk did not name it. The person was left with
a file synthtwin had made and had not been told about.

The repair claims the name BEFORE attempting to create it, so the window
falls inside the claim rather than outside it.

THE SAFETY BOUND THESE TESTS EXIST TO HOLD. Exclusive creation also
fails because the name was ALREADY TAKEN by a file this run did not
make, so a claim that was never seen to finish cannot say which of the
two it is looking at. Such a name is NAMED to the person and never
removed -- a file synthtwin failed to mention is a disclosure defect,
and a file synthtwin deleted is a data-destruction defect, which is
worse. Half of the tests below assert the naming; the other half assert
that nothing is deleted.

Every test fixes the state on disk, makes exactly one operation stop at
exactly the moment in question, and asserts both halves: every surviving
byte, and the sentence the person reads. Nothing in the package is
stubbed; the product code runs exactly as shipped.
"""

import json
import pathlib

import pytest

import fixtures
from synthtwin import errors, profile
from synthtwin.cli import main

PROFILE_TEXT = '{\n  "profile_version": 2,\n  "note": "PROFILE-DERIVED"\n}\n'
SUMMARY_TEXT = "A summary of the table, for a person to read.\n"

# What a person's own file under a working name holds. If any test ever
# finds this text gone, synthtwin deleted something it did not make.
SOMEBODY_ELSES = "a file synthtwin did not make\n"


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


def _stop_inside_the_creation_of(
    monkeypatch: pytest.MonkeyPatch,
    doomed: pathlib.Path,
    failure: BaseException,
) -> None:
    """Reproduce the window exactly: the file appears, the call does not.

    The real creation runs first, so the file really is on disk with the
    real permissions, and only then does the failure arrive -- which is
    what a signal delivered between the operating system's work and the
    call handing back looks like from Python.
    """
    real = pathlib.Path.touch
    wanted = f"{doomed}"

    def interrupted(
        self: pathlib.Path, mode: int = 0o666, exist_ok: bool = True
    ) -> None:
        if f"{self}" == wanted:
            real(self, mode=mode, exist_ok=exist_ok)
            raise failure
        real(self, mode=mode, exist_ok=exist_ok)

    monkeypatch.setattr(pathlib.Path, "touch", interrupted)


def _stop_before_the_creation_of(
    monkeypatch: pytest.MonkeyPatch,
    doomed: pathlib.Path,
    failure: BaseException,
) -> None:
    """The other side of the same window: nothing is created at all."""
    real = pathlib.Path.touch
    wanted = f"{doomed}"

    def interrupted(
        self: pathlib.Path, mode: int = 0o666, exist_ok: bool = True
    ) -> None:
        if f"{self}" == wanted:
            raise failure
        real(self, mode=mode, exist_ok=exist_ok)

    monkeypatch.setattr(pathlib.Path, "touch", interrupted)


# ---------------------------------------------------------------------
# 1. the reviewer's probe: Ctrl-C inside the very first creation
# ---------------------------------------------------------------------


def test_ctrl_c_inside_the_first_creation_names_the_file_it_made(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Before the repair: the file was on disk, `first_part` was still
    # None, the cleanup inventory was empty, and the sentence said there
    # was nothing left to clear up. It was a lie about a file synthtwin
    # had made.
    first, second = _outputs(tmp_path)
    candidate = pathlib.Path(f"{first}{profile.PART_SUFFIX}-1")
    _stop_inside_the_creation_of(monkeypatch, candidate, KeyboardInterrupt())
    state = profile.DiskState()
    with pytest.raises(KeyboardInterrupt):
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert candidate.exists(), (
        "the operating system made this file; the test is worthless if it "
        "does not reproduce that"
    )
    assert f"{candidate}" in state.sentence, (
        "a file synthtwin made under a name it was still creating must be "
        "named to the person, whatever stopped the run"
    )
    assert "still creating when the run stopped" in state.sentence
    assert "There is nothing left to clear up" not in state.sentence, (
        "there IS something left, so the sentence may not say otherwise"
    )
    # Both output names are accounted for as well, and neither was made.
    assert f"{first}" in state.sentence and f"{second}" in state.sentence
    assert not first.exists() and not second.exists()


def test_the_file_it_may_not_have_made_is_never_removed(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The safety bound. From inside the window synthtwin cannot tell its
    # own empty file from one that was already under that name, so the
    # sentence says so and the file stays. Deleting it on the chance that
    # it is ours is the failure this test exists to prevent.
    first, second = _outputs(tmp_path)
    candidate = pathlib.Path(f"{first}{profile.PART_SUFFIX}-1")
    _stop_inside_the_creation_of(monkeypatch, candidate, KeyboardInterrupt())
    state = profile.DiskState()
    with pytest.raises(KeyboardInterrupt):
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert _neighbours(tmp_path) == [candidate.name]
    assert "did not remove it" in state.sentence
    assert "cannot tell whether it made this file" in state.sentence
    assert "please look at it before you delete it" in state.sentence


def test_nothing_is_invented_when_the_creation_never_started(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The other side of the same window. A claim that came to nothing is
    # not a file, and a sentence that names one sends the reader hunting
    # for something that is not there. The claim is looked at, not
    # assumed.
    first, second = _outputs(tmp_path)
    candidate = pathlib.Path(f"{first}{profile.PART_SUFFIX}-1")
    _stop_before_the_creation_of(monkeypatch, candidate, KeyboardInterrupt())
    state = profile.DiskState()
    with pytest.raises(KeyboardInterrupt):
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert _neighbours(tmp_path) == []
    assert f"{candidate}" not in state.sentence
    assert "There is nothing left to clear up" in state.sentence


def test_a_stop_in_the_second_creation_still_clears_the_first(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The first working file IS synthtwin's beyond doubt -- its creation
    # handed back -- so it is removed as always. Only the name caught in
    # the window is left, and only that one is named.
    first, second = _outputs(tmp_path)
    first_part = pathlib.Path(f"{first}{profile.PART_SUFFIX}-1")
    second_part = pathlib.Path(f"{second}{profile.PART_SUFFIX}-1")
    _stop_inside_the_creation_of(monkeypatch, second_part, KeyboardInterrupt())
    state = profile.DiskState()
    with pytest.raises(KeyboardInterrupt):
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert not first_part.exists(), (
        "a working name whose creation handed back is synthtwin's for "
        "certain and is cleared away like any other"
    )
    assert _neighbours(tmp_path) == [second_part.name]
    assert f"{second_part}" in state.sentence


def test_a_stopping_program_is_covered_on_the_same_rule(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The window belongs to the moment, not to the exception. SystemExit
    # is not an Exception either, and the handler does not ask what was
    # raised.
    first, second = _outputs(tmp_path)
    candidate = pathlib.Path(f"{first}{profile.PART_SUFFIX}-1")
    _stop_inside_the_creation_of(monkeypatch, candidate, SystemExit(1))
    state = profile.DiskState()
    with pytest.raises(SystemExit):
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert candidate.exists()
    assert f"{candidate}" in state.sentence


def test_memory_exhausted_inside_a_creation_is_covered_too(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first, second = _outputs(tmp_path)
    candidate = pathlib.Path(f"{first}{profile.PART_SUFFIX}-1")
    _stop_inside_the_creation_of(
        monkeypatch, candidate, MemoryError("simulated")
    )
    state = profile.DiskState()
    with pytest.raises(MemoryError):
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert candidate.exists()
    assert f"{candidate}" in state.sentence


# ---------------------------------------------------------------------
# 2. nothing this run did not make is ever removed
# ---------------------------------------------------------------------


def test_a_neighbour_file_is_passed_over_and_left_exactly_as_it_was(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A file of somebody else's sits at the first candidate name, so the
    # run moves to the second -- and stops inside creating that one. The
    # neighbour must come through untouched, and it must not be described
    # as anything of synthtwin's.
    first, second = _outputs(tmp_path)
    neighbour = pathlib.Path(f"{first}{profile.PART_SUFFIX}-1")
    neighbour.write_text(SOMEBODY_ELSES, encoding="utf-8")
    candidate = pathlib.Path(f"{first}{profile.PART_SUFFIX}-2")
    _stop_inside_the_creation_of(monkeypatch, candidate, KeyboardInterrupt())
    state = profile.DiskState()
    with pytest.raises(KeyboardInterrupt):
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert neighbour.read_text(encoding="utf-8") == SOMEBODY_ELSES, (
        "synthtwin never writes to or removes a file it did not create"
    )
    assert f"{neighbour}" not in state.sentence
    assert f"{candidate}" in state.sentence


def test_the_earlier_profile_survives_a_stop_in_the_set_aside_creation(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The working name an earlier profile is moved to is created the same
    # way, so it has the same window. The move itself has not happened
    # yet, so the earlier profile is still under its own name -- and that
    # is the one file in this transaction no failure path may delete.
    first, second = _outputs(tmp_path)
    first.write_text("last week's profile\n", encoding="utf-8")
    kept = pathlib.Path(f"{first}{profile.KEPT_SUFFIX}-1")
    _stop_inside_the_creation_of(monkeypatch, kept, KeyboardInterrupt())
    state = profile.DiskState()
    with pytest.raises(KeyboardInterrupt):
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert first.read_text(encoding="utf-8") == "last week's profile\n", (
        "the earlier profile had not moved yet, so it is still there"
    )
    assert kept.exists()
    assert f"{kept}" in state.sentence
    assert "still creating when the run stopped" in state.sentence
    # The two data-bearing working files are cleared away as always.
    assert not pathlib.Path(f"{first}{profile.PART_SUFFIX}-1").exists()
    assert not pathlib.Path(f"{second}{profile.PART_SUFFIX}-1").exists()


def test_a_set_aside_earlier_profile_is_still_never_removed(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The neighbouring promise, restated against the claim record: once
    # the earlier profile HAS been moved to its working name, that name
    # holds the reader's own file. The record knows synthtwin created
    # that name and must not act on it, because what is under it now is
    # not what synthtwin put there.
    first, second = _outputs(tmp_path)
    first.write_text("last week's profile\n", encoding="utf-8")
    first_part = pathlib.Path(f"{first}{profile.PART_SUFFIX}-1")
    kept = pathlib.Path(f"{first}{profile.KEPT_SUFFIX}-1")
    real = pathlib.Path.replace
    wanted = f"{first_part}"

    def brittle(self: pathlib.Path, target: object) -> pathlib.Path:
        if f"{self}" == wanted:
            raise KeyboardInterrupt()
        return real(self, target)  # type: ignore[arg-type]

    monkeypatch.setattr(pathlib.Path, "replace", brittle)
    state = profile.DiskState()
    with pytest.raises(KeyboardInterrupt):
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert kept.read_text(encoding="utf-8") == "last week's profile\n", (
        "the reader's only earlier profile may never be deleted by any "
        "path, including the record of names this run created"
    )
    assert f"{kept}" in state.sentence
    assert "moved here and could not move back" in state.sentence


# ---------------------------------------------------------------------
# 3. what the person sees, end to end
# ---------------------------------------------------------------------


def test_the_command_names_the_file_left_by_an_interrupted_creation(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The whole item through the words a person would type. Ctrl-C ends
    # the command the way every other command on their computer ends, and
    # what they must not lose in the process is the sentence saying which
    # file synthtwin left in their folder.
    table = fixtures.write(
        tmp_path,
        "clinic.csv",
        fixtures.single_column_table("age", ["41"] * 30),
    )
    first, _second = _outputs(tmp_path)
    candidate = pathlib.Path(f"{first}{profile.PART_SUFFIX}-1")
    _stop_inside_the_creation_of(monkeypatch, candidate, KeyboardInterrupt())
    with pytest.raises(KeyboardInterrupt):
        main(["profile", f"{table}"])
    told = capsys.readouterr().err

    assert candidate.exists()
    assert f"{candidate}" in told, (
        "the person must be told about a file synthtwin left in their "
        "folder, whatever ended the command"
    )
    assert "wrote nothing into it" in told
    assert sorted(entry.name for entry in tmp_path.iterdir()) == sorted(
        ["clinic.csv", candidate.name]
    ), "the table, and the one file the interrupted creation left"


# ---------------------------------------------------------------------
# 4. the catalog, and the ordinary run
# ---------------------------------------------------------------------


def test_the_words_for_a_claimed_working_name_are_in_the_catalog() -> None:
    # The code is only worth having if it renders as a sentence rather
    # than falling through to "not known", and if it says the two things
    # a reader needs: nothing of theirs went into it, and synthtwin did
    # not decide for them whose it is.
    stated = errors.nothing_was_written(
        [],
        [
            ("/reports/t-profile.json", errors.ON_DISK_ABSENT),
            ("/reports/t-profile.txt", errors.ON_DISK_ABSENT),
            (
                "/reports/t-profile.json.synthtwin-part-1",
                errors.ON_DISK_CLAIMED_WORKING,
            ),
        ],
    )
    assert "synthtwin could not say what is there" not in stated
    assert "wrote nothing into it" in stated
    assert "did not remove it" in stated
    assert "Check each one before you use it" in stated
    assert "There is nothing left to clear up" not in stated


def test_the_two_claim_states_are_not_the_same_code() -> None:
    # One may be removed and the other may only be named. A repair that
    # ran them together would read as tidy and would delete files.
    assert profile.CLAIM_MADE != profile.CLAIM_REACHED
    assert (
        errors.ON_DISK_CLAIMED_WORKING != errors.ON_DISK_UNCERTAIN_WORKING
    ), (
        "a name synthtwin certainly made and a name it may have made are "
        "different things to tell a person"
    )
    assert errors.ON_DISK_CLAIMED_WORKING != errors.ON_DISK_EMPTY_WORKING


def test_an_ordinary_run_is_unchanged_by_the_claim(
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


def test_a_plain_csv_still_profiles_cleanly_through_the_command(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # A repair that breaks ordinary correct input is worse than the bug,
    # so the plainest possible table goes through the real command.
    table = fixtures.write(
        tmp_path, "clinic.csv", fixtures.every_role_table()
    )
    assert main(["profile", f"{table}"]) == 0
    told = capsys.readouterr()
    first, second = _outputs(tmp_path)
    document = json.loads(first.read_text(encoding="utf-8"))
    assert document["n_rows"] == 240
    assert second.read_text(encoding="utf-8")
    assert _neighbours(tmp_path) == []
    assert told.err == ""
    assert "Written:" in told.out


def test_the_same_table_still_produces_the_same_bytes(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The claim record holds working names, which never reach the
    # published output. Two runs over one table must still agree byte
    # for byte (plan D12).
    text = fixtures.every_role_table()
    one = tmp_path / "one"
    two = tmp_path / "two"
    one.mkdir()
    two.mkdir()
    first_table = fixtures.write(one, "clinic.csv", text)
    second_table = fixtures.write(two, "clinic.csv", text)
    assert main(["profile", f"{first_table}"]) == 0
    assert main(["profile", f"{second_table}"]) == 0
    capsys.readouterr()
    assert (one / "clinic-profile.json").read_bytes() == (
        two / "clinic-profile.json"
    ).read_bytes()
    assert (one / "clinic-profile.txt").read_bytes() == (
        two / "clinic-profile.txt"
    ).read_bytes()
