"""Gate file of lane IN-0 (plan P4-D495): where an inside record may be written, and with which permissions.

ONE CASE A REFUSED PLACE: a network or web form; a link or junction the
Windows walk of the locality gate refuses; a temporary folder; a
downloads folder; a folder a cloud service keeps in step (OneDrive,
Dropbox, iCloud Drive, Google Drive, Box, by name); a folder under
version control; a mounted network share or another disk on the way
(POSIX); any path outside the private data folder, the folder itself
included; and, on POSIX, a private folder other accounts may enter.
ONE CASE AN ACCEPTED PLACE: a record in the private folder, in a
sub-folder of it, and written again over itself; it is created 0600 in
a 0700 folder (POSIX). Every place is injected (`inside.Places`): no
case reads or writes the account's own folders. Each clause is red on
its mutant (lane IN-0's report).
"""

from __future__ import annotations

import pathlib

import typing

import pytest

from synthtwin import inside, installation

POSIX = installation.system_name() != "nt"
RECORD = {"format": inside.FORMAT, "version": inside.VERSION, "mode": inside.MODE,
          "table": {"rows": 0, "columns": []}, "zones": {}}


def _places(root: pathlib.Path, **changed: object) -> inside.Places:
    home = pathlib.Path(root, "home")
    fields = {"private": pathlib.Path(home, "data", "synthtwin", "inside"),
              "temporary": (pathlib.Path(root, "tmp"),), "downloads": (pathlib.Path(home, "Downloads"),),
              "os_name": installation.system_name(), "mounts": ()}
    fields.update(changed)
    return inside.Places(**fields)  # type: ignore[arg-type]


def _refused(target: "str | pathlib.Path", places: inside.Places, words: str) -> None:
    reason = inside.place_refusal(target, places)
    assert words in reason, reason
    with pytest.raises(inside.InsideError):
        inside.write_record(RECORD, target, places)
    if not str(target).startswith(("\\\\", "//")) and "://" not in str(target):
        assert not pathlib.Path(target).exists()


@pytest.mark.parametrize("target", ["\\\\server\\share\\cohort.synthtwin-inside", "//server/share/cohort.synthtwin-inside",
                                    "smb://server/share/cohort.synthtwin-inside"])
def test_a_network_form_is_refused(tmp_path: pathlib.Path, target: str) -> None:
    _refused(target, _places(tmp_path), "network")


def test_a_link_the_windows_walk_refuses_is_refused(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    places = _places(tmp_path)
    target = pathlib.Path(places.private, "cohort" + inside.SUFFIX)

    def refuse(raw: str, *, purpose: str) -> pathlib.Path:
        raise inside.PathValidationError(f"The {purpose} path {raw!r} was not accepted: it passes through a link.")

    monkeypatch.setattr(inside, "validate_local_path", refuse)
    assert "passes through a link" in inside.place_refusal(target, places)


def test_a_temporary_folder_is_refused(tmp_path: pathlib.Path) -> None:
    _refused(pathlib.Path(tmp_path, "tmp", "run", "cohort" + inside.SUFFIX), _places(tmp_path), "temporary folder")


@pytest.mark.parametrize("where", ["the account's own, under another name", "a folder named so anywhere"])
def test_a_downloads_folder_is_refused(tmp_path: pathlib.Path, where: str) -> None:
    own = pathlib.Path(tmp_path, "home", "Transfers")
    places = _places(tmp_path, downloads=(own,))
    folder = own if where.startswith("the account") else pathlib.Path(places.private, "Downloads")
    _refused(pathlib.Path(folder, "cohort" + inside.SUFFIX), places, "downloads folder")


@pytest.mark.parametrize("name", ["OneDrive", "OneDrive - Hospital", "Dropbox", "Dropbox (Team)", "iCloud Drive",
                                  "Mobile Documents", "Google Drive", "My Drive", "GoogleDrive-person", "Box",
                                  "CloudStorage"])
def test_a_folder_a_cloud_service_keeps_in_step_is_refused(tmp_path: pathlib.Path, name: str) -> None:
    places = _places(tmp_path)
    _refused(pathlib.Path(places.private, name, "cohort" + inside.SUFFIX), places, "cloud service")


@pytest.mark.parametrize("mark", [".git", ".git file", ".hg", ".svn"])
def test_a_folder_under_version_control_is_refused(tmp_path: pathlib.Path, mark: str) -> None:
    places = _places(tmp_path)
    work = pathlib.Path(places.private, "project")
    work.mkdir(parents=True)
    if mark == ".git file":
        pathlib.Path(work, ".git").write_text("gitdir: elsewhere\n", encoding="utf-8", newline="\n")
    else:
        pathlib.Path(work, mark).mkdir()
    _refused(pathlib.Path(work, "cohort" + inside.SUFFIX), places, "version control")


@pytest.mark.skipif(not POSIX, reason="the mount table and mount roots are the POSIX side of the guard (lane IN-8 rehearses Windows)")
def test_a_network_share_in_the_mount_table_is_refused(tmp_path: pathlib.Path) -> None:
    places = _places(tmp_path)
    shared = _places(tmp_path, mounts=((str(pathlib.Path(places.private).resolve().parent), "nfs4"),))
    _refused(pathlib.Path(places.private, "cohort" + inside.SUFFIX), shared, "network file system")


@pytest.mark.skipif(not POSIX, reason="the mount table and mount roots are the POSIX side of the guard (lane IN-8 rehearses Windows)")
def test_a_private_folder_under_a_mount_root_is_refused(tmp_path: pathlib.Path) -> None:
    mounted = _places(tmp_path, private=pathlib.Path("/Volumes/share/synthtwin/inside"))
    reason = inside.place_refusal("/Volumes/share/synthtwin/inside/cohort" + inside.SUFFIX, mounted)
    assert "network share or another disk" in reason


@pytest.mark.parametrize("where", ["elsewhere", "the folder itself", "beside it"])
def test_a_path_outside_the_private_folder_is_refused(tmp_path: pathlib.Path, where: str) -> None:
    places = _places(tmp_path)
    target = {"elsewhere": pathlib.Path(tmp_path, "home", "work", "cohort" + inside.SUFFIX),
              "the folder itself": places.private,
              "beside it": pathlib.Path(places.private.parent, "cohort" + inside.SUFFIX)}[where]
    _refused(target, places, "outside your private data folder")


@pytest.mark.skipif(not POSIX, reason="POSIX permissions; on Windows the record inherits the account's own folder")
def test_a_private_folder_other_accounts_may_enter_is_refused(tmp_path: pathlib.Path) -> None:
    places = _places(tmp_path)
    places.private.mkdir(parents=True)
    places.private.chmod(0o755)
    _refused(pathlib.Path(places.private, "cohort" + inside.SUFFIX), places, "other accounts")


@pytest.mark.parametrize("where", ["the private folder", "a folder inside it"])
def test_a_record_in_the_private_folder_is_written_for_its_owner_alone(tmp_path: pathlib.Path, where: str) -> None:
    places = _places(tmp_path)
    folder = places.private if where == "the private folder" else pathlib.Path(places.private, "cohort-2026")
    target = pathlib.Path(folder, "cohort" + inside.SUFFIX)
    assert inside.place_refusal(target, places) == ""
    written = inside.write_record(RECORD, target, places)
    assert written.path == target.resolve()
    assert inside.load_record(target) == RECORD
    assert not pathlib.Path(folder, target.name + ".new").exists()
    if POSIX:
        assert target.stat().st_mode & 0o777 == 0o600
        assert folder.stat().st_mode & 0o777 == 0o700
        assert places.private.stat().st_mode & 0o777 == 0o700
    again = inside.write_record(RECORD, target, places)
    assert again.size == written.size


def test_the_default_place_is_the_installation_s_data_folder() -> None:
    places = inside.default_places()
    assert places.private == pathlib.Path(installation.data_folder(), inside.FOLDER)
    assert inside.record_path("cohort", places) == pathlib.Path(places.private, "cohort" + inside.SUFFIX)
    assert places.os_name == installation.system_name()


@pytest.fixture(scope="module", autouse=True)
def _inside_record_switched_on() -> "typing.Iterator[None]":
    """The inside record's sub-switch is on for this file (`cli._inside_record_switched_on`)."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("synthtwin.cli._INSIDE_RECORD_SHIPPED", True)
        yield
