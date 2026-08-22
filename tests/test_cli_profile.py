"""`synthtwin profile` end to end (plan P1-D3, P1-D6, P1-D7).

Zero-code use is the requirement being tested here: a path and nothing
else has to work, every refusal has to arrive as a readable sentence
rather than a traceback, and the person running the command has to be
told what left their table before they move the files anywhere.
"""

import json
import pathlib
import sys

import pytest

import fixtures
from synthtwin import cli, profile
from synthtwin.cli import main

# The bytes for "clear the display", which a terminal obeys rather than
# prints.
_CLEAR_THE_SCREEN = "\x1b[2J"

# POSIX filenames may hold any byte but the separator and the null, so
# a folder whose NAME carries the sequence above can really be made
# there. The Windows filename grammar refuses that byte outright
# (WinError 123), so the folder cannot exist at all and a test that
# tries to make one errors before it asserts anything.
#
# The property is the same on both: text carrying a display control
# must be SHOWN, never obeyed, and Windows terminals obey these
# sequences too. The escaping boundary takes any text, so the control
# does not have to arrive in a filename to prove it holds -- it arrives
# in the folder name where a filesystem allows one, and in the caution
# sentence's own text where it does not. Both routes end at the same
# two pieces of code, and the second route runs everywhere.
_A_FILENAME_MAY_CARRY_A_CONTROL = sys.platform != "win32"


def _table(tmp_path: pathlib.Path, text: str = "") -> pathlib.Path:
    return fixtures.write(
        tmp_path, "clinic.csv", text or fixtures.every_role_table()
    )


def _working_files(folder: pathlib.Path) -> list[str]:
    """Every file synthtwin left in ``folder`` under a working name."""
    found = [
        place.name
        for place in sorted(folder.iterdir())
        if profile.PART_SUFFIX in place.name
        or profile.KEPT_SUFFIX in place.name
    ]
    return found


def _refuse_to_delete(
    monkeypatch: pytest.MonkeyPatch, doomed: pathlib.Path
) -> None:
    """Make deleting one exact path fail, as a locked folder would."""
    real = pathlib.Path.unlink

    def stubborn(self: pathlib.Path, **rest: object) -> None:
        if f"{self}" == f"{doomed}":
            raise OSError(13, "Permission denied")
        real(self, **rest)  # type: ignore[arg-type]

    monkeypatch.setattr(pathlib.Path, "unlink", stubborn)


def test_a_path_and_nothing_else_is_enough(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = _table(tmp_path)
    assert main(["profile", str(table)]) == 0
    out = capsys.readouterr().out
    assert (tmp_path / "clinic-profile.json").is_file()
    assert (tmp_path / "clinic-profile.txt").is_file()
    assert "clinic-profile.json" in out
    assert "COLUMNS, ONE BY ONE" in out


def test_the_summary_on_screen_and_on_disk_are_the_same_text(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = _table(tmp_path)
    main(["profile", str(table)])
    out = capsys.readouterr().out
    written = (tmp_path / "clinic-profile.txt").read_text(encoding="utf-8")
    assert written in out


def test_the_written_profile_is_valid_json_and_readable_back(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = _table(tmp_path)
    main(["profile", str(table)])
    capsys.readouterr()
    document = json.loads(
        (tmp_path / "clinic-profile.json").read_text(encoding="utf-8")
    )
    assert document["n_rows"] == 240
    assert document["n_columns"] == 12


def test_running_twice_produces_identical_files(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = _table(tmp_path)
    main(["profile", str(table)])
    first = (tmp_path / "clinic-profile.json").read_bytes()
    main(["profile", str(table)])
    capsys.readouterr()
    assert (tmp_path / "clinic-profile.json").read_bytes() == first


def test_the_output_folder_option(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = _table(tmp_path)
    reports = tmp_path / "reports"
    reports.mkdir()
    assert main(["profile", str(table), "--out-dir", str(reports)]) == 0
    capsys.readouterr()
    assert (reports / "clinic-profile.json").is_file()
    assert not (tmp_path / "clinic-profile.json").exists()


def test_the_disclosure_section_is_printed_every_run(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = _table(tmp_path)
    main(["profile", str(table)])
    out = capsys.readouterr().out
    assert "WHAT THIS PROFILE CARRIES FROM YOUR TABLE" in out
    assert "real-derived material" in out
    assert "not anonymous" in out


def test_no_withheld_value_is_ever_printed(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = _table(tmp_path)
    main(["profile", str(table)])
    printed = capsys.readouterr().out
    written = (tmp_path / "clinic-profile.txt").read_text(encoding="utf-8")
    for text in (printed, written):
        assert "outlying" not in text, "a below-floor label reached the screen"
        assert "R00007" not in text, "an identifier reached the screen"
        assert "observation 3 written out" not in text, "free text reached it"


def test_lowering_the_smallest_group_warns(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The warning names the count, the person, and where the counts go.

    IT CHECKS THE CONTENT, NOT THE WORD "Warning" (owner ruling
    2026-08-14, plan amendment A-P3-11). The version this replaces
    asserted that the string "Warning" reached the error stream, which
    the sentence it was written for satisfied while telling a person
    nothing they could act on -- it never said that the description
    prints the small count itself, never said one row may be one person,
    and never said the counts travel into the twin and the reports. The
    owner ruled the floor through end to end KNOWING the consequence and
    ruled that the consequence be made visible, so what this test holds
    is that the warning states it.
    """
    table = _table(tmp_path)
    assert main(["profile", str(table), "--smallest-group", "2"]) == 0
    captured = capsys.readouterr()
    said = captured.err
    for owed in (
        # the number typed, and the number it replaces
        "2",
        "11",
        # what a small group is, in the terms a person thinks in
        "one person",
        # that the count itself is the disclosure, not a route to it
        "the count is the disclosure",
        # that it does not stop at the description
        "twin",
        "quality report",
        # what to do instead
        "--smallest-group",
    ):
        assert owed in said, (
            f"the lowered-floor warning no longer says {owed!r}. It is the "
            "only place a person is told what a group of two can reveal "
            "before the files exist"
        )
    assert "outlying" in captured.out, (
        "with the floor lowered the rare label becomes visible -- which is "
        "exactly why the warning has to be there"
    )


def test_a_smallest_group_below_one_is_refused(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = _table(tmp_path)
    assert main(["profile", str(table), "--smallest-group", "0"]) == 2
    assert "whole number of 1 or more" in capsys.readouterr().err


def test_naming_a_column_as_a_record_number(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = _table(tmp_path)
    assert main(["profile", str(table), "--identifier", "amount"]) == 0
    capsys.readouterr()
    document = json.loads(
        (tmp_path / "clinic-profile.json").read_text(encoding="utf-8")
    )
    amount = next(
        c for c in document["columns"] if c["name"] == "amount"
    )
    assert amount["role"] == "identifier"


def test_naming_a_column_that_is_not_there_is_refused_before_writing(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Round 1 found this warned AFTER writing the profile, so a column
    # the user meant to suppress had already been described on disk.
    table = _table(tmp_path)
    assert main(["profile", str(table), "--identifier", "no_such_column"]) == 2
    error = capsys.readouterr().err
    assert "no column with that name" in error
    assert "record_code" in error, "the message must name the real columns"
    assert not (tmp_path / "clinic-profile.json").exists(), (
        "nothing may be written when an option names a column that is "
        "not in the table"
    )


def test_the_disclosure_is_printed_before_the_files_exist(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Plan P1-D6 says the disclosure comes first. It is the step that
    # lets a person stop before real-derived material is on disk.
    table = _table(tmp_path)
    assert main(["profile", str(table)]) == 0
    out = capsys.readouterr().out
    disclosure = out.index("WHAT THIS PROFILE CARRIES FROM YOUR TABLE")
    will_write = out.index("These two files will be written")
    written = out.index("Written:")
    assert disclosure < will_write < written


def test_a_working_file_left_behind_is_named_and_the_run_still_succeeds(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Review item P1-R6-F5. write_both_files hands back every working
    # file still on disk after an otherwise complete run, and the
    # command threw that list away: the earlier profile stayed in the
    # folder under a name nobody had been given, holding a description
    # of the real table, while the screen said only "Written:".
    #
    # Here last week's profile is set aside as usual and the delete that
    # should clear it away is refused, exactly as a folder locked by
    # another program would refuse it.
    table = _table(tmp_path)
    earlier = tmp_path / "clinic-profile.json"
    earlier.write_text("last week's profile\n", encoding="utf-8", newline="\n")
    kept = tmp_path / f"clinic-profile.json{profile.KEPT_SUFFIX}-1"
    _refuse_to_delete(monkeypatch, kept)

    assert main(["profile", str(table)]) == 0, (
        "the profile is written and correct, so this is a caution and "
        "not a failure: the exit code may not change"
    )
    captured = capsys.readouterr()

    # Both outputs really are the finished ones.
    assert json.loads(earlier.read_text(encoding="utf-8"))["n_rows"] == 240
    assert (tmp_path / "clinic-profile.txt").is_file()
    # And the stray file is still there, holding real-derived text.
    assert kept.read_text(encoding="utf-8") == "last week's profile\n"

    told = captured.err
    assert kept.name in told, (
        "the user cannot delete a file synthtwin never named"
    )
    assert "tidy up by hand" in told
    assert "this one could not be removed" in told
    assert "delete it once you have looked" in told
    assert "nothing is wrong with your profile" in told, (
        "a leftover working file is not a failure of the profile and "
        "must not be reported as one"
    )
    assert "Written:" in captured.out


def test_an_ordinary_run_says_nothing_about_working_files(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The other half of the repair: a run that cleans up after itself
    # must stay silent about it. A caution printed every time is a
    # caution nobody reads.
    table = _table(tmp_path)
    (tmp_path / "clinic-profile.json").write_text(
        "last week's profile\n", encoding="utf-8", newline="\n"
    )
    assert main(["profile", str(table)]) == 0
    captured = capsys.readouterr()
    assert _working_files(tmp_path) == [], (
        "an ordinary run leaves no working file in the output folder"
    )
    assert "tidy up by hand" not in captured.err
    assert "tidy up by hand" not in captured.out
    assert captured.err == "", "an ordinary run has nothing to caution about"


def _assert_the_caution_shows_the_control(told: str) -> None:
    """What both halves of the P1-R6-F11 check below require."""
    assert "\x1b" not in told, "an escape sequence reached the terminal"
    assert "reports\\x1b[2J" in told, (
        "the folder must still be recognizable to the person who has to "
        "go and delete the file"
    )


@pytest.mark.skipif(
    not _A_FILENAME_MAY_CARRY_A_CONTROL,
    reason=(
        "this filesystem refuses a filename holding \\x1b, so the folder "
        "cannot be made; the same property is checked on every platform "
        "by test_a_left_behind_name_that_instructs_the_terminal_is_shown"
    ),
)
def test_a_left_behind_path_cannot_instruct_the_terminal(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The new sentence prints a path, so it is a display sink like every
    # other, and the path is the user's own folder name (P1-R6-F11).
    # This is the whole route, from a real folder on disk through the
    # command to the error stream.
    folder = tmp_path / f"reports{_CLEAR_THE_SCREEN}"
    folder.mkdir()
    table = _table(tmp_path)
    earlier = folder / "clinic-profile.json"
    earlier.write_text("last week's profile\n", encoding="utf-8", newline="\n")
    kept = folder / f"clinic-profile.json{profile.KEPT_SUFFIX}-1"
    _refuse_to_delete(monkeypatch, kept)

    assert main(["profile", str(table), "--out-dir", str(folder)]) == 0
    told = capsys.readouterr().err
    _assert_the_caution_shows_the_control(told)


def test_a_left_behind_name_that_instructs_the_terminal_is_shown(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The same property where a filename cannot carry the control.

    The test above needs a folder on disk whose name holds the escape
    sequence, which Windows has no way to create. So the control
    arrives here as what it really is -- text -- and goes through the
    two pieces of code the whole route ends at: the sentence that lists
    a working file left behind, and the emitter that puts every message
    on the error stream. Neither cares where the text came from, which
    is why this route proves the same thing.

    Deleting the Windows case instead would leave the one platform
    whose terminals also obey these sequences with nothing asserted at
    all, so this runs on every platform, beside the route above.
    """
    left = (
        f"reports{_CLEAR_THE_SCREEN}/"
        f"clinic-profile.json{profile.KEPT_SUFFIX}-1"
    )
    cli._warn(cli._left_behind_note([left]))
    told = capsys.readouterr().err
    _assert_the_caution_shows_the_control(told)
    assert f"clinic-profile.json{profile.KEPT_SUFFIX}-1" in told, (
        "the file the reader has to go and delete must still be named"
    )
    assert "tidy up by hand" in told, (
        "the escaping must not have eaten the sentence around the path"
    )


def test_a_link_pointing_at_the_table_is_refused(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The worst outcome this tool has: writing the description over the
    # data it was asked to describe. Found by verification of round 1.
    #
    # TWO rules can stop it, and which one does is the platform's
    # business, not this test's. On POSIX a link resolves to an ordinary
    # local path, so the locality check passes it and the run is stopped
    # by the later comparison: the profile's name and the table are one
    # file. On Windows the locality check refuses the link itself --
    # ANY link, symbolic link, junction or mount point, because one
    # there can quietly lead to a network location -- and the run stops
    # before that comparison is reached.
    #
    # The promise is the same under both and it is asserted under both:
    # the command refuses, the table is byte-for-byte what it was, the
    # link is left as it was found, nothing is written, and the reason
    # arrives as a sentence. Only the sentence itself differs, so each
    # is pinned on the platform whose rule produced it. Skipping the
    # Windows half would leave the STRICTER of the two rules with
    # nothing asserted about it at all.
    table = _table(tmp_path)
    was = table.read_bytes()
    link = tmp_path / "clinic-profile.json"
    link.symlink_to(table)

    assert main(["profile", str(table)]) == 1
    told = capsys.readouterr().err

    assert table.read_bytes() == was, (
        "the table the command was asked to describe must come out of a "
        "refusal byte-for-byte what it went in as"
    )
    assert link.is_symlink(), (
        "the link was the user's; a refusal may not replace it with a file"
    )
    # Where it points is asked by FOLLOWING it: `readlink` hands back
    # the substitution path the filesystem stored, and on Windows that
    # is the `\\?\`-prefixed spelling rather than the one `symlink_to`
    # was given, so reading the target back would answer "no" for a link
    # that is perfectly intact.
    assert link.resolve() == table.resolve(), (
        "a refusal may not repoint the user's own link"
    )
    assert not (tmp_path / "clinic-profile.txt").exists(), (
        "a refused run publishes neither of the two files"
    )
    assert _working_files(tmp_path) == [], (
        "and leaves no working file of its own behind"
    )
    assert "Traceback" not in told, "the reason must arrive as a sentence"

    if sys.platform == "win32":
        # The stricter rule, and the only place it is exercised.
        assert "is a link" in told
        assert "network location" in told
        assert link.name in told, (
            "the person has to be told which name is the link"
        )
    else:
        assert "would have replaced your own table" in told
        assert f"{table}" in told, (
            "the person has to be told which file was nearly lost"
        )


def test_a_folder_in_the_way_is_refused_before_anything_is_written(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = _table(tmp_path)
    (tmp_path / "clinic-profile.txt").mkdir()
    assert main(["profile", str(table)]) == 1
    assert "a folder of that name" in capsys.readouterr().err
    assert not (tmp_path / "clinic-profile.json").exists(), (
        "the first file must not survive a refusal of the second"
    )


def test_a_missing_file_is_a_sentence_not_a_traceback(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["profile", str(tmp_path / "absent.csv")]) == 1
    error = capsys.readouterr().err
    assert "There is no file at" in error
    assert "Traceback" not in error


def test_a_web_address_is_refused_before_anything_is_opened(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["profile", "https://example.invalid/data.csv"]) == 1
    error = capsys.readouterr().err
    assert "network" in error


def test_a_malformed_table_is_a_sentence_not_a_traceback(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = _table(tmp_path, "a,b,c\n1,2,3\n4,5\n")
    assert main(["profile", str(table)]) == 1
    error = capsys.readouterr().err
    assert "row 2 has 2" in error
    assert "Traceback" not in error


def test_asking_for_the_command_without_a_file_says_so(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["profile"])
    assert caught.value.code == 2
    assert "which file to describe" in capsys.readouterr().err


def test_the_bare_command_still_prints_the_status(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "synthtwin profile" in out
    assert "never sends anything" in out


def test_help_shows_an_example(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["--help"])
    assert caught.value.code == 0
    out = capsys.readouterr().out
    assert "synthtwin profile data.csv" in out
