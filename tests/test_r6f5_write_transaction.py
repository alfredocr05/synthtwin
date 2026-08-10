"""The two-file write, one failure path at a time (review item P1-R6-F5).

Every test here fixes a state on disk, makes exactly one filesystem
operation fail, and then asserts BOTH halves of the promise: every
surviving byte, and the sentence the person reads. A message that
describes a clean failure it cannot vouch for is the defect being
tested, so the assertions on the message are as exact as the ones on
the files.

The failures are injected by replacing one pathlib method for the
duration of one test. Nothing in the package is stubbed, and no
tolerance is relaxed: the product code runs exactly as shipped.
"""

import pathlib
import sys

import pytest

from synthtwin import errors, profile

PROFILE_TEXT = '{\n  "profile_version": 1\n}\n'
SUMMARY_TEXT = "A summary of the table, for a person to read.\n"
TABLE_TEXT = "record_code,age\nA1,41\nB2,52\n"
EARLIER_PROFILE = "last week's profile\n"

# What a link left at one of synthtwin's own working names does to a run
# is decided by the platform, and the two answers are genuinely
# different rules rather than one rule with two wordings:
#
# * on POSIX a working name that is already taken -- by anything, a link
#   included -- is stepped past, the next number is tried, and the run
#   finishes normally;
# * on Windows the path check refuses ANY link, symbolic link, junction
#   or mount point, because a link there can quietly lead to a network
#   location. That refusal arrives BEFORE the step that would have
#   stepped past it, so the run stops and publishes nothing.
#
# The property the two tests below exist for is the same on both, and it
# is the one that matters: the table is byte-for-byte what it was, every
# link is exactly as it was found, and nothing synthtwin wrote went
# through one. That is asserted on every platform. The outcome of the
# RUN is then asserted on each side, so the Windows rule -- the stricter
# of the two, and the one no other test reaches -- is checked rather
# than skipped.
_WINDOWS = sys.platform == "win32"


def _still_the_link_it_was(place: pathlib.Path, table: pathlib.Path) -> None:
    """``place`` is still a link and still leads to ``table``.

    Where the link POINTS is asked by following it rather than by
    reading the target back out of it. `Path.readlink` hands back the
    substitution path the filesystem stored, and on Windows that is the
    `\\\\?\\`-prefixed spelling rather than the one that was handed to
    `symlink_to` -- so comparing what comes back with the table's own
    path answers "no" on Windows for a link that is perfectly intact.
    Following it settles the same question on every platform.
    """
    assert place.is_symlink(), f"{place.name} is no longer a link"
    assert place.resolve() == table.resolve(), (
        f"{place.name} no longer leads to the table"
    )


def _what_escapes(
    work: "object", *args: object, **named: object
) -> "BaseException | None":
    """Run ``work`` and hand back whatever came out of it, or None.

    The two link tests want to assert about the disk whichever way the
    run went, so neither `pytest.raises` nor a bare call will do: one
    demands a failure and the other forbids one, and which of those is
    right is the platform's answer, not the test's.
    """
    try:
        work(*args, **named)  # type: ignore[operator]
    except BaseException as failed:  # noqa: BLE001 -- the point of the test
        return failed
    return None


def _refused_the_link(
    raised: "BaseException | None", link: pathlib.Path
) -> None:
    """The Windows answer: a refusal naming the link and the reason.

    The message has to be actionable by somebody who does not program,
    so it is held to naming the file that stopped the run, saying that
    the file is a link, saying why a link is refused, and saying that
    nothing was published.
    """
    assert isinstance(raised, errors.ProfileError), (
        f"the run had to stop, and it stopped with "
        f"{type(raised).__name__}: {raised}"
    )
    message = f"{raised}"
    assert f"{link}" in message, "the link that stopped the run must be named"
    assert "is a link" in message
    assert "network location" in message
    assert "No new description was published" in message


def _outputs(folder: pathlib.Path) -> "tuple[pathlib.Path, pathlib.Path]":
    """The two names a run beside a table called clinic.csv would use."""
    return (folder / "clinic-profile.json", folder / "clinic-profile.txt")


def _table(folder: pathlib.Path) -> pathlib.Path:
    table = folder / "clinic.csv"
    table.write_text(TABLE_TEXT, encoding="utf-8")
    return table


def _working_files(folder: pathlib.Path) -> "list[str]":
    """Every leftover working file in ``folder``, by name, sorted."""
    found = [
        entry.name
        for entry in folder.iterdir()
        if profile.PART_SUFFIX in entry.name or profile.KEPT_SUFFIX in entry.name
    ]
    return sorted(found)


def _fail_replace_onto(
    monkeypatch: pytest.MonkeyPatch, doomed: "list[pathlib.Path]"
) -> None:
    """Make `Path.replace` fail whenever the destination is in ``doomed``."""
    real = pathlib.Path.replace
    wanted = [f"{one}" for one in doomed]

    def stubborn(self: pathlib.Path, other: object) -> pathlib.Path:
        if f"{other}" in wanted:
            raise OSError(28, "No space left on device")
        return real(self, other)  # type: ignore[arg-type]

    monkeypatch.setattr(pathlib.Path, "replace", stubborn)


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


# ---------------------------------------------------------------------------
# (a) the working names cannot reach the user's own files
# ---------------------------------------------------------------------------


def test_a_link_at_the_working_name_cannot_reach_the_table(
    tmp_path: pathlib.Path,
) -> None:
    # The reviewer's worst route, exactly as reported: a link left at
    # the profile's working name pointing at the table itself. The
    # earlier code wrote through the link and destroyed the table this
    # tool exists to protect. See the note above on why the run's
    # outcome differs by platform while the protection does not.
    table = _table(tmp_path)
    first, second = _outputs(tmp_path)
    links = [
        tmp_path / f"clinic-profile.json{profile.PART_SUFFIX}",
        tmp_path / f"clinic-profile.json{profile.PART_SUFFIX}-1",
        tmp_path / f"clinic-profile.txt{profile.PART_SUFFIX}-1",
    ]
    for place in links:
        place.symlink_to(table)

    raised = _what_escapes(
        profile.write_both_files,
        first,
        second,
        PROFILE_TEXT,
        SUMMARY_TEXT,
        table_path=table,
    )

    # Every platform, and this is what the test is for.
    assert table.read_text(encoding="utf-8") == TABLE_TEXT, (
        "the table must be byte-for-byte what it was: nothing synthtwin "
        "writes may ever pass through a link into the user's own data"
    )
    for place in links:
        _still_the_link_it_was(place, table)
    assert _working_files(tmp_path) == sorted(place.name for place in links), (
        "the three links were already there; synthtwin may add no working "
        "file of its own to them"
    )

    if _WINDOWS:
        # The run is refused before the search could step past the link.
        # Nothing is published, which is stricter than passing over it.
        _refused_the_link(raised, links[1])
        assert not first.exists() and not second.exists()
        return
    assert raised is None, f"the run had to finish; {raised!r} came out of it"
    assert first.read_text(encoding="utf-8") == PROFILE_TEXT
    assert second.read_text(encoding="utf-8") == SUMMARY_TEXT


def test_a_working_name_that_is_the_table_itself_is_passed_over(
    tmp_path: pathlib.Path,
) -> None:
    # The table happens to be named where a working file would go.
    table = tmp_path / f"clinic-profile.json{profile.PART_SUFFIX}-1"
    table.write_text(TABLE_TEXT, encoding="utf-8")
    first, second = _outputs(tmp_path)

    profile.write_both_files(
        first, second, PROFILE_TEXT, SUMMARY_TEXT, table_path=table
    )

    assert table.read_text(encoding="utf-8") == TABLE_TEXT
    assert first.read_text(encoding="utf-8") == PROFILE_TEXT
    assert second.read_text(encoding="utf-8") == SUMMARY_TEXT


def test_an_output_name_is_never_used_as_a_working_name(
    tmp_path: pathlib.Path,
) -> None:
    # A summary whose name IS the profile's first working name. The
    # working file must not land on it.
    first = tmp_path / "clinic-profile.json"
    second = tmp_path / f"clinic-profile.json{profile.PART_SUFFIX}-1"

    profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)

    assert first.read_text(encoding="utf-8") == PROFILE_TEXT
    assert second.read_text(encoding="utf-8") == SUMMARY_TEXT


def test_unrelated_working_neighbours_are_left_exactly_as_they_were(
    tmp_path: pathlib.Path,
) -> None:
    # Reviewer's third row: files of the working names, belonging to
    # somebody else, were written over and then deleted in silence.
    first, second = _outputs(tmp_path)
    neighbours = {
        f"clinic-profile.json{profile.PART_SUFFIX}-1": "someone else's file\n",
        f"clinic-profile.json{profile.PART_SUFFIX}-2": "and another\n",
        f"clinic-profile.txt{profile.PART_SUFFIX}-1": "a third\n",
        f"clinic-profile.json{profile.KEPT_SUFFIX}-1": "a fourth\n",
    }
    for name, text in neighbours.items():
        (tmp_path / name).write_text(text, encoding="utf-8")
    first.write_text("last week's profile\n", encoding="utf-8")

    profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)

    assert first.read_text(encoding="utf-8") == PROFILE_TEXT
    assert second.read_text(encoding="utf-8") == SUMMARY_TEXT
    for name, text in neighbours.items():
        assert (tmp_path / name).read_text(encoding="utf-8") == text, (
            f"{name} was not synthtwin's to touch"
        )
    assert _working_files(tmp_path) == sorted(neighbours), (
        "a completed run leaves no working file of its own behind"
    )


def test_every_working_name_taken_is_refused_in_words(
    tmp_path: pathlib.Path,
) -> None:
    first, second = _outputs(tmp_path)
    blocked = []
    for number in range(1, profile.WORKING_NAME_ATTEMPTS + 1):
        neighbour = tmp_path / (
            f"clinic-profile.json{profile.PART_SUFFIX}-{number}"
        )
        neighbour.write_text(f"leftover {number}\n", encoding="utf-8")
        blocked = blocked + [neighbour]

    with pytest.raises(errors.ProfileError) as raised:
        profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)

    message = f"{raised.value}"
    assert "could not make itself a working file" in message
    assert f"{profile.WORKING_NAME_ATTEMPTS}" in message
    assert f"{blocked[0]}" in message, "the message must name what is in the way"
    assert "run the command again" in message
    assert "No new description was published" in message
    for number, neighbour in enumerate(blocked, start=1):
        assert neighbour.read_text(encoding="utf-8") == f"leftover {number}\n"
    assert not first.exists() and not second.exists()


def test_a_link_at_the_backup_name_cannot_reach_the_table(
    tmp_path: pathlib.Path,
) -> None:
    # The name an earlier profile is set aside under is a working name
    # like any other, and a link left at it must never be written
    # through. It is reached later in the run than the one above -- both
    # working files are already written by then -- so it is the second
    # place the same rule has to hold.
    table = _table(tmp_path)
    first, second = _outputs(tmp_path)
    first.write_text(EARLIER_PROFILE, encoding="utf-8")
    trap = tmp_path / f"clinic-profile.json{profile.KEPT_SUFFIX}-1"
    trap.symlink_to(table)

    raised = _what_escapes(
        profile.write_both_files,
        first,
        second,
        PROFILE_TEXT,
        SUMMARY_TEXT,
        table_path=table,
    )

    # Every platform.
    assert table.read_text(encoding="utf-8") == TABLE_TEXT
    _still_the_link_it_was(trap, table)
    assert _working_files(tmp_path) == [trap.name], (
        "the link was already there; synthtwin may add no working file "
        "of its own to it"
    )

    if _WINDOWS:
        _refused_the_link(raised, trap)
        assert first.read_text(encoding="utf-8") == EARLIER_PROFILE, (
            "the profile from before the run is the one file no refusal "
            "may take away"
        )
        assert not second.exists()
        return
    assert raised is None, f"the run had to finish; {raised!r} came out of it"
    assert first.read_text(encoding="utf-8") == PROFILE_TEXT
    assert second.read_text(encoding="utf-8") == SUMMARY_TEXT


def test_an_output_that_is_a_link_is_refused_before_anything_is_written(
    tmp_path: pathlib.Path,
) -> None:
    table = _table(tmp_path)
    first, second = _outputs(tmp_path)
    first.symlink_to(tmp_path / "nowhere.json")
    assert not profile.is_the_same_file(first, table), (
        "a link leading nowhere leads nowhere: it is not the table"
    )

    with pytest.raises(errors.ProfileError) as raised:
        profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)

    message = f"{raised.value}"
    assert "not an ordinary file" in message
    assert "Remove it" in message
    assert not (tmp_path / "nowhere.json").exists(), (
        "a description of real data must not be written through a link"
    )
    assert not second.exists()
    assert _working_files(tmp_path) == []


def test_a_folder_that_cannot_be_written_is_a_sentence(
    tmp_path: pathlib.Path,
) -> None:
    folder = tmp_path / "locked"
    folder.mkdir()
    first, second = _outputs(folder)
    folder.chmod(0o500)
    probe = folder / "probe"
    try:
        probe.touch()
        allowed = True
    except OSError:
        allowed = False
    if allowed:  # pragma: no cover -- a user who overrides permissions
        probe.unlink()
        folder.chmod(0o700)
        pytest.skip("this user can write into a folder that forbids it")
    try:
        with pytest.raises(errors.ProfileError) as raised:
            profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)
    finally:
        folder.chmod(0o700)

    message = f"{raised.value}"
    assert f"{first}{profile.PART_SUFFIX}-1" in message
    assert "permission" in message
    assert not first.exists() and not second.exists()


def test_the_published_bytes_do_not_depend_on_the_working_name(
    tmp_path: pathlib.Path,
) -> None:
    # Determinism (plan D12): which numbered working name a run had to
    # fall back to must not reach the published output.
    plain = tmp_path / "plain"
    crowded = tmp_path / "crowded"
    plain.mkdir()
    crowded.mkdir()
    for number in range(1, 6):
        (crowded / f"clinic-profile.json{profile.PART_SUFFIX}-{number}").touch()
        (crowded / f"clinic-profile.txt{profile.PART_SUFFIX}-{number}").touch()

    for folder in [plain, crowded]:
        first, second = _outputs(folder)
        profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)

    assert (plain / "clinic-profile.json").read_bytes() == (
        crowded / "clinic-profile.json"
    ).read_bytes()
    assert (plain / "clinic-profile.txt").read_bytes() == (
        crowded / "clinic-profile.txt"
    ).read_bytes()


# ---------------------------------------------------------------------------
# (b) the message describes the disk
# ---------------------------------------------------------------------------


def test_the_second_rename_failing_with_no_earlier_profile_leaves_nothing(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Reviewer's second row: no old profile, the second rename fails,
    # and the new JSON was left at the final profile name while the
    # message said "Nothing was written: both files are as they were
    # before".
    first, second = _outputs(tmp_path)
    _fail_replace_onto(monkeypatch, [second])

    with pytest.raises(errors.ProfileError) as raised:
        profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)

    message = f"{raised.value}"
    assert not first.exists(), (
        "the newly installed profile must be taken back out when there "
        "was no earlier file to put back in its place"
    )
    assert not second.exists()
    assert _working_files(tmp_path) == []
    assert "No new description was published" in message
    assert f"{first} holds nothing -- there is no file of that" in message
    assert f"{second} holds nothing -- there is no file of that" in message
    assert "There is nothing left to clear up." in message


def test_the_second_rename_failing_puts_the_earlier_profile_back(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first, second = _outputs(tmp_path)
    first.write_text("last week's profile\n", encoding="utf-8")
    second.write_text("last week's summary\n", encoding="utf-8")
    _fail_replace_onto(monkeypatch, [second])

    with pytest.raises(errors.ProfileError) as raised:
        profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)

    message = f"{raised.value}"
    assert first.read_text(encoding="utf-8") == "last week's profile\n"
    assert second.read_text(encoding="utf-8") == "last week's summary\n"
    assert _working_files(tmp_path) == []
    assert "No new description was published" in message
    assert f"{first} holds the file that was there before this run" in message
    assert f"{second} holds the file that was there before this run" in message


def test_a_rollback_that_itself_fails_names_the_new_and_the_old_file(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The second rename fails AND the earlier profile cannot be put
    # back. The person is holding a new profile and last week's summary
    # and must be told so in as many words.
    first, second = _outputs(tmp_path)
    first.write_text("last week's profile\n", encoding="utf-8")
    second.write_text("last week's summary\n", encoding="utf-8")
    kept = tmp_path / f"clinic-profile.json{profile.KEPT_SUFFIX}-1"
    real = pathlib.Path.replace

    def stubborn(self: pathlib.Path, other: object) -> pathlib.Path:
        # The summary will not go into place, and the set-aside profile
        # will not come back out of its working name either.
        if f"{other}" == f"{second}":
            raise OSError(28, "No space left on device")
        if profile.KEPT_SUFFIX in f"{self}" and f"{other}" == f"{first}":
            raise PermissionError(13, "Operation not permitted")
        return real(self, other)  # type: ignore[arg-type]

    monkeypatch.setattr(pathlib.Path, "replace", stubborn)

    with pytest.raises(errors.ProfileError) as raised:
        profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)

    message = f"{raised.value}"
    # The disk, byte for byte.
    assert first.read_text(encoding="utf-8") == PROFILE_TEXT
    assert second.read_text(encoding="utf-8") == "last week's summary\n"
    assert kept.read_text(encoding="utf-8") == "last week's profile\n"
    # The message, name by name.
    assert "could not put things back as they were" in message
    assert f"{first} holds the new description this run produced" in message
    assert f"{second} holds the file that was there before this run" in message
    assert f"{kept} holds the description from before this run" in message
    assert "do not describe the same table" in message


def test_a_rollback_that_fails_with_no_earlier_profile_names_the_new_file(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Nothing was there before, so undoing means removing the file just
    # installed -- and when THAT fails the message must say the new
    # profile is sitting at its final name.
    first, second = _outputs(tmp_path)
    _fail_replace_onto(monkeypatch, [second])
    _fail_unlink_of(monkeypatch, [first])

    with pytest.raises(errors.ProfileError) as raised:
        profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)

    message = f"{raised.value}"
    assert first.read_text(encoding="utf-8") == PROFILE_TEXT
    assert not second.exists()
    assert "could not put things back as they were" in message
    assert f"{first} holds the new description this run produced" in message
    assert f"{second} holds nothing -- there is no file of that" in message


def test_a_working_file_that_will_not_go_is_reported_as_holding_data(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Reviewer's fourth row: the first working file was written, the
    # second step failed, cleanup of the first failed too, and the
    # message said the leftovers "hold no description of your table"
    # while one of them held a whole profile.
    first, second = _outputs(tmp_path)
    part = tmp_path / f"clinic-profile.json{profile.PART_SUFFIX}-1"
    _fail_replace_onto(monkeypatch, [first])
    _fail_unlink_of(monkeypatch, [part])

    with pytest.raises(errors.ProfileError) as raised:
        profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)

    message = f"{raised.value}"
    assert part.read_text(encoding="utf-8") == PROFILE_TEXT
    assert f"{part} holds a working file synthtwin could not clear away" in (
        message
    )
    assert "it holds text taken from your table" in message
    assert "holds no description of your table" not in message
    assert not first.exists() and not second.exists()


def test_the_summary_working_file_is_cleared_when_the_profile_write_fails(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first, second = _outputs(tmp_path)
    real = pathlib.Path.write_text

    def stubborn(
        self: pathlib.Path, data: str, **rest: object
    ) -> int:
        if profile.PART_SUFFIX in f"{self}":
            raise OSError(28, "No space left on device")
        return real(self, data, **rest)  # type: ignore[arg-type]

    monkeypatch.setattr(pathlib.Path, "write_text", stubborn)

    with pytest.raises(errors.ProfileError) as raised:
        profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)

    message = f"{raised.value}"
    assert _working_files(tmp_path) == [], (
        "both working files must be cleared away when a write fails"
    )
    assert not first.exists() and not second.exists()
    assert "No new description was published" in message
    assert f"{first} holds nothing -- there is no file of that" in message


def test_a_backup_that_will_not_go_is_handed_back_not_passed_over(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A completed run whose only loose end is the earlier profile,
    # still sitting under a working name. It is real-derived material,
    # so the caller is given it to report rather than left in the dark.
    first, second = _outputs(tmp_path)
    first.write_text("last week's profile\n", encoding="utf-8")
    kept = tmp_path / f"clinic-profile.json{profile.KEPT_SUFFIX}-1"
    _fail_unlink_of(monkeypatch, [kept])

    left = profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)

    assert first.read_text(encoding="utf-8") == PROFILE_TEXT
    assert second.read_text(encoding="utf-8") == SUMMARY_TEXT
    assert kept.read_text(encoding="utf-8") == "last week's profile\n"
    assert left == [f"{kept}"]


def test_a_completed_run_hands_back_nothing(tmp_path: pathlib.Path) -> None:
    first, second = _outputs(tmp_path)
    first.write_text("last week's profile\n", encoding="utf-8")
    assert profile.write_both_files(
        first, second, PROFILE_TEXT, SUMMARY_TEXT
    ) == []
    assert _working_files(tmp_path) == []


# ---------------------------------------------------------------------------
# metadata failures are sentences, not tracebacks
# ---------------------------------------------------------------------------


def test_a_metadata_failure_on_an_output_is_a_sentence(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first, second = _outputs(tmp_path)
    real = pathlib.Path.exists

    def stubborn(self: pathlib.Path, **rest: object) -> bool:
        if f"{self}" == f"{first}":
            raise OSError(5, "Input/output error")
        return real(self, **rest)  # type: ignore[arg-type]

    monkeypatch.setattr(pathlib.Path, "exists", stubborn)

    with pytest.raises(errors.ProfileError) as raised:
        profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)

    message = f"{raised.value}"
    assert "could not read what is at that name" in message
    assert "Please check that you have permission" in message


def test_a_metadata_failure_inside_the_commit_is_a_sentence(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The check that asks whether an earlier profile is there ran
    # outside any handler and could escape as a raw traceback.
    first, second = _outputs(tmp_path)
    # The drive goes unreadable at the moment both working files are on
    # disk and the commit is about to ask what is at the profile's name.
    armed = {"yet": False}
    real_write = pathlib.Path.write_text
    real_exists = pathlib.Path.exists

    def note(self: pathlib.Path, data: str, **rest: object) -> int:
        written = real_write(self, data, **rest)  # type: ignore[arg-type]
        if data == SUMMARY_TEXT:
            armed["yet"] = True
        return written

    def stubborn(self: pathlib.Path, **rest: object) -> bool:
        if armed["yet"] and f"{self}" == f"{first}":
            raise OSError(5, "Input/output error")
        return real_exists(self, **rest)  # type: ignore[arg-type]

    monkeypatch.setattr(pathlib.Path, "write_text", note)
    monkeypatch.setattr(pathlib.Path, "exists", stubborn)

    with pytest.raises(errors.ProfileError) as raised:
        profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)

    message = f"{raised.value}"
    assert "could not read what is at that name" in message
    assert "not known: synthtwin could not check this name" in message
    assert _working_files(tmp_path) == []


def test_two_names_the_filesystem_folds_together_are_caught(
    tmp_path: pathlib.Path,
) -> None:
    # Two dangling names that this host treats as one file: the
    # identity check cannot settle it while neither exists, so the run
    # must settle it once the first file is on disk and undo itself.
    # The same name in its two spellings: one code point for the
    # accented letter, or the plain letter followed by the accent.
    composed = tmp_path / "caf\u00e9-profile.json"
    decomposed = tmp_path / "cafe\u0301-profile.json"
    assert f"{composed}" != f"{decomposed}"
    probe = tmp_path / "prob\u00e9.txt"
    probe.write_text("x", encoding="utf-8")
    folds_together = (tmp_path / "probe\u0301.txt").exists()
    probe.unlink()
    if not folds_together:
        pytest.skip("this filesystem keeps the two spellings apart")

    with pytest.raises(errors.ProfileError) as raised:
        profile.write_both_files(
            composed, decomposed, PROFILE_TEXT, SUMMARY_TEXT
        )

    message = f"{raised.value}"
    assert "two names for the same file" in message
    # The clause is what marks this as the LATE check: the early one
    # cannot answer while neither name exists, and raises on its own.
    assert "No new description was published" in message
    assert not composed.exists(), (
        "the run must take back out what it had just installed"
    )
    assert not decomposed.exists()
    assert _working_files(tmp_path) == []


def test_the_identity_check_fails_closed_when_existence_cannot_be_read(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    left = tmp_path / "one.json"
    right = tmp_path / "two.json"
    left.write_text("a", encoding="utf-8")
    right.write_text("b", encoding="utf-8")
    assert not profile.is_the_same_file(left, right)

    def stubborn(self: pathlib.Path, **rest: object) -> bool:
        raise OSError(5, "Input/output error")

    monkeypatch.setattr(pathlib.Path, "exists", stubborn)
    assert profile.is_the_same_file(left, right), (
        "a check that protects the user's data answers YES on any doubt"
    )


# ---------------------------------------------------------------------------
# the sentences themselves
# ---------------------------------------------------------------------------


def test_nothing_was_written_never_claims_what_it_did_not_check() -> None:
    unchecked = errors.nothing_was_written([])
    assert "as they were before" not in unchecked
    assert "did not check" in unchecked
    assert unchecked.rstrip().endswith(".")


def test_nothing_was_written_states_every_name_it_was_given() -> None:
    message = errors.nothing_was_written(
        [],
        [
            ("/d/t-profile.json", errors.ON_DISK_BEFORE),
            ("/d/t-profile.txt", errors.ON_DISK_ABSENT),
            ("/d/t-profile.json.synthtwin-part-1", errors.ON_DISK_WORKING),
        ],
    )
    assert "/d/t-profile.json holds the file that was there before" in message
    assert "/d/t-profile.txt holds nothing -- there is no file" in message
    assert "text taken from your table" in message
    assert "Check each one before you use it" in message


def test_nothing_was_written_does_not_send_anyone_to_look_at_nothing() -> None:
    message = errors.nothing_was_written(
        [],
        [
            ("/d/t-profile.json", errors.ON_DISK_ABSENT),
            ("/d/t-profile.txt", errors.ON_DISK_TAKEN_AWAY),
        ],
    )
    assert "There is nothing left to clear up." in message
    assert "Check each one" not in message


def test_rollback_failed_says_which_run_each_file_came_from() -> None:
    message = errors.rollback_failed(
        [],
        [
            ("/d/t-profile.json", errors.ON_DISK_NEW),
            ("/d/t-profile.txt", errors.ON_DISK_BEFORE),
            ("/d/t-profile.json.synthtwin-kept-1", errors.ON_DISK_SET_ASIDE),
        ],
    )
    assert "could not put things back" in message
    assert "the new description this run produced" in message
    assert "moved here and could not move back" in message
    assert "do not describe the same table" in message


def test_a_state_code_nobody_recognizes_is_reported_not_dropped() -> None:
    message = errors.nothing_was_written([], [("/d/x", "no-such-code")])
    assert "/d/x" in message
    assert "could not say what is there" in message


def test_the_old_call_shapes_still_read_as_sentences() -> None:
    # Both builders are appended to another refusal and are called with
    # one list by the catalog test; that call must keep working.
    assert errors.nothing_was_written([]).endswith(".")
    assert errors.rollback_failed(["/d/t-profile.json"]).endswith(".")
    assert "/d/t-profile.json" in errors.rollback_failed(
        ["/d/t-profile.json"]
    )


def test_the_working_name_message_says_what_to_do() -> None:
    message = errors.working_name_unavailable(
        "/d/t-profile.json", ["/d/t-profile.json.synthtwin-part-1"], 64
    )
    assert "/d/t-profile.json.synthtwin-part-1" in message
    assert "64" in message
    assert "move or delete them" in message
    assert "run the command again" in message
    assert message.rstrip().endswith(".")
