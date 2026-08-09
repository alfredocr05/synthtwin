"""`synthtwin profile` end to end (plan P1-D3, P1-D6, P1-D7).

Zero-code use is the requirement being tested here: a path and nothing
else has to work, every refusal has to arrive as a readable sentence
rather than a traceback, and the person running the command has to be
told what left their table before they move the files anywhere.
"""

import json
import pathlib

import pytest

import fixtures
from synthtwin import profile
from synthtwin.cli import main


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
    assert document["n_columns"] == 10


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
    table = _table(tmp_path)
    assert main(["profile", str(table), "--smallest-group", "2"]) == 0
    captured = capsys.readouterr()
    assert "Warning" in captured.err
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
    earlier.write_text("last week's profile\n", encoding="utf-8")
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
        "last week's profile\n", encoding="utf-8"
    )
    assert main(["profile", str(table)]) == 0
    captured = capsys.readouterr()
    assert _working_files(tmp_path) == [], (
        "an ordinary run leaves no working file in the output folder"
    )
    assert "tidy up by hand" not in captured.err
    assert "tidy up by hand" not in captured.out
    assert captured.err == "", "an ordinary run has nothing to caution about"


def test_a_left_behind_path_cannot_instruct_the_terminal(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The new sentence prints a path, so it is a display sink like every
    # other, and the path is the user's own folder name (P1-R6-F11).
    folder = tmp_path / "reports\x1b[2J"
    folder.mkdir()
    table = _table(tmp_path)
    earlier = folder / "clinic-profile.json"
    earlier.write_text("last week's profile\n", encoding="utf-8")
    kept = folder / f"clinic-profile.json{profile.KEPT_SUFFIX}-1"
    _refuse_to_delete(monkeypatch, kept)

    assert main(["profile", str(table), "--out-dir", str(folder)]) == 0
    told = capsys.readouterr().err
    assert "\x1b" not in told, "an escape sequence reached the terminal"
    assert "reports\\x1b[2J" in told, (
        "the folder must still be recognizable to the person who has to "
        "go and delete the file"
    )


def test_a_link_pointing_at_the_table_is_refused(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The worst outcome this tool has: writing the description over the
    # data it was asked to describe. Found by verification of round 1.
    table = _table(tmp_path)
    (tmp_path / "clinic-profile.json").symlink_to(table)
    assert main(["profile", str(table)]) == 1
    assert "would have replaced your own table" in capsys.readouterr().err
    assert table.read_text(encoding="utf-8").startswith("record_code,")


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
