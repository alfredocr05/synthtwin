"""P1-R7-F1: no caught failure leaves a data-bearing part unnamed.

The transaction promises that both files appear or neither does, and
that whatever survives a failure is NAMED to the person. Two routes
broke that promise, and each has its own section below.

1. `write_text_file` puts the working name through the locality check
   immediately before writing, and that check raises
   PathValidationError. The two write handlers caught only
   ProfileError, so a refusal on the SECOND working file escaped the
   whole transaction: no cleanup ran, and the first working file --
   holding a complete description computed from the real table -- was
   left in the output folder while the message discussed only the path.

2. `_create_empty` could create a working file successfully and then
   get an uncertain answer from the look that follows. It reported a
   plain refusal and dropped the name it had just claimed, so the
   caller cleaned an inventory that did not mention it and could
   truthfully say nothing was left.

Every test fixes the state on disk, makes exactly one operation fail,
and asserts BOTH halves: every surviving byte, and the sentence the
person reads. Nothing in the package is stubbed; the product code runs
exactly as shipped.
"""

import json
import pathlib

import pytest

import fixtures
from synthtwin import errors, profile, writing
from synthtwin.cli import main
from synthtwin.paths import PathValidationError

PROFILE_TEXT = '{\n  "profile_version": 2,\n  "note": "PROFILE-DERIVED"\n}\n'
SUMMARY_TEXT = "A summary of the table, for a person to read.\n"
TABLE_TEXT = "record_code,age\nA1,41\nB2,52\n"

REFUSAL = (
    "The working path was refused by the check that runs immediately "
    "before the write. Use a path on this computer and try again."
)


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


def _refuse_the_write_of(
    monkeypatch: pytest.MonkeyPatch, doomed: pathlib.Path
) -> None:
    """Refuse the locality check that `write_text_file` runs on ``doomed``.

    Keyed on the purpose as well as the path, so that claiming the
    working name still succeeds and only the write is refused -- which
    is the state the review item describes.
    """
    real = writing.validate_local_path
    wanted = f"{doomed}"

    def picky(raw: object, *, purpose: str) -> pathlib.Path:
        if f"{raw}" == wanted and purpose == "output file":
            raise PathValidationError(REFUSAL)
        return real(raw, purpose=purpose)  # type: ignore[arg-type]

    monkeypatch.setattr(writing, "validate_local_path", picky)


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


def _hide_the_file(
    monkeypatch: pytest.MonkeyPatch, doomed: pathlib.Path
) -> None:
    """Make one name answer "not an ordinary file" once it exists.

    This is the second half of the item: exclusive creation succeeds and
    the look that follows it does not confirm an ordinary file.
    """
    real = pathlib.Path.is_file
    wanted = f"{doomed}"

    def shy(self: pathlib.Path) -> bool:
        if f"{self}" == wanted:
            return False
        return real(self)

    monkeypatch.setattr(pathlib.Path, "is_file", shy)


# ---------------------------------------------------------------------
# 1. a path refusal on the second working-file write
# ---------------------------------------------------------------------


def test_a_path_refusal_on_the_second_write_undoes_the_first(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The reviewer's exact route: both working names are claimed, the
    # first working file is written in full from the real table, and the
    # second working file's immediate path check reports a refusal.
    first, second = _outputs(tmp_path)
    _refuse_the_write_of(
        monkeypatch, pathlib.Path(f"{second}{profile.PART_SUFFIX}-1")
    )
    with pytest.raises(errors.ProfileError) as caught:
        profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)

    told = f"{caught.value}"
    assert not first.exists() and not second.exists()
    assert _neighbours(tmp_path) == [], (
        "a working file holding a description of the real table may not "
        "survive a refusal the code caught"
    )
    assert "PROFILE-DERIVED" not in told
    # Both output names are accounted for by name, and the person is
    # told there is nothing to clear up -- which is now true.
    assert f"{first}" in told and f"{second}" in told
    assert "No new description was published" in told
    assert "There is nothing left to clear up" in told
    # And the refusal still says what was wrong with the path.
    assert "try again" in told


def test_the_first_working_file_is_named_when_it_cannot_be_removed(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The same refusal, with the cleanup of the data-bearing part also
    # failing. The transaction cannot make the folder clean, so the one
    # thing it must do instead is NAME what is there and say what it
    # holds.
    first, second = _outputs(tmp_path)
    first_part = pathlib.Path(f"{first}{profile.PART_SUFFIX}-1")
    _refuse_the_write_of(
        monkeypatch, pathlib.Path(f"{second}{profile.PART_SUFFIX}-1")
    )
    _fail_unlink_of(monkeypatch, [first_part])
    with pytest.raises(errors.ProfileError) as caught:
        profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)

    told = f"{caught.value}"
    assert first_part.read_text(encoding="utf-8") == PROFILE_TEXT
    assert f"{first_part}" in told, (
        "a working file holding text computed from the real table that "
        "could not be removed must be named to the person"
    )
    assert "holds text taken from your table" in told
    assert "Check each one before you use it" in told


def test_a_path_refusal_on_the_first_write_leaves_nothing_behind(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first, second = _outputs(tmp_path)
    _refuse_the_write_of(
        monkeypatch, pathlib.Path(f"{first}{profile.PART_SUFFIX}-1")
    )
    with pytest.raises(errors.ProfileError) as caught:
        profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)

    told = f"{caught.value}"
    assert not first.exists() and not second.exists()
    assert _neighbours(tmp_path) == []
    assert "There is nothing left to clear up" in told


def test_an_earlier_profile_is_still_there_after_the_refusal(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The neighbouring promise: a refusal inside the transaction leaves
    # the files that were there before it exactly as they were.
    first, second = _outputs(tmp_path)
    first.write_text("last week's profile\n", encoding="utf-8")
    second.write_text("last week's summary\n", encoding="utf-8")
    _refuse_the_write_of(
        monkeypatch, pathlib.Path(f"{second}{profile.PART_SUFFIX}-1")
    )
    with pytest.raises(errors.ProfileError) as caught:
        profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)

    assert first.read_text(encoding="utf-8") == "last week's profile\n"
    assert second.read_text(encoding="utf-8") == "last week's summary\n"
    assert _neighbours(tmp_path) == []
    told = f"{caught.value}"
    assert "the file that was there before this run, unchanged" in told


def test_the_command_reports_the_refusal_and_leaves_the_folder_clean(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # End to end, through the words a person would type. The screen said
    # only that a path was refused, while a complete real-derived
    # profile sat in a hidden neighbour nobody had been told about.
    table = fixtures.write(
        tmp_path, "clinic.csv", fixtures.single_column_table("age", ["41"] * 30)
    )
    _first, second = _outputs(tmp_path)
    _refuse_the_write_of(
        monkeypatch, pathlib.Path(f"{second}{profile.PART_SUFFIX}-1")
    )
    assert main(["profile", f"{table}"]) == 1
    told = capsys.readouterr().err
    assert "No new description was published" in told
    assert _neighbours(tmp_path) == []
    assert sorted(entry.name for entry in tmp_path.iterdir()) == ["clinic.csv"]


# ---------------------------------------------------------------------
# 2. a working name that was created and then could not be examined
# ---------------------------------------------------------------------


def test_a_created_name_that_cannot_be_examined_is_cleared_away(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first, second = _outputs(tmp_path)
    candidate = pathlib.Path(f"{first}{profile.PART_SUFFIX}-1")
    _hide_the_file(monkeypatch, candidate)
    with pytest.raises(errors.ProfileError) as caught:
        profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)

    assert _neighbours(tmp_path) == [], (
        "ownership of a working name starts at the creation, so the file "
        "created a moment before the uncertain check must be cleared away"
    )
    assert "There is nothing left to clear up" in f"{caught.value}"


def test_a_created_name_that_survives_cleanup_is_named(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first, second = _outputs(tmp_path)
    candidate = pathlib.Path(f"{first}{profile.PART_SUFFIX}-1")
    _hide_the_file(monkeypatch, candidate)
    _fail_unlink_of(monkeypatch, [candidate])
    with pytest.raises(errors.ProfileError) as caught:
        profile.write_both_files(first, second, PROFILE_TEXT, SUMMARY_TEXT)

    told = f"{caught.value}"
    assert candidate.exists()
    assert f"{candidate}" in told, (
        "a name synthtwin created and could not clear away must be named, "
        "whether or not anything was written into it"
    )
    assert "wrote nothing into" in told
    assert "There is nothing left to clear up" not in told


def test_the_words_for_the_uncertain_working_name_are_in_the_catalog(
) -> None:
    # The code is only worth having if it renders as a sentence rather
    # than falling through to "not known".
    stated = errors.nothing_was_written(
        [],
        [
            ("/reports/t-profile.json", errors.ON_DISK_ABSENT),
            ("/reports/t-profile.txt", errors.ON_DISK_ABSENT),
            (
                "/reports/t-profile.json.synthtwin-part-1",
                errors.ON_DISK_UNCERTAIN_WORKING,
            ),
        ],
    )
    assert "synthtwin could not say what is there" not in stated
    assert "wrote nothing into" in stated
    assert "Check each one before you use it" in stated


# ---------------------------------------------------------------------
# 3. the ordinary run is unharmed
# ---------------------------------------------------------------------


def test_an_ordinary_run_still_writes_both_files_and_clears_up(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = fixtures.write(tmp_path, "clinic.csv", TABLE_TEXT)
    assert main(["profile", f"{table}", "--identifier", "record_code"]) == 0
    first, second = _outputs(tmp_path)
    assert json.loads(first.read_text(encoding="utf-8"))["n_rows"] == 2
    assert second.read_text(encoding="utf-8")
    assert _neighbours(tmp_path) == []
    assert capsys.readouterr().err == ""
