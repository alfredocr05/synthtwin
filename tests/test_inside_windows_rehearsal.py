"""Gate file of lane IN-8 (plan P4-D502): the Windows rehearsal of the inside record's write guard, on any computer.

THE PROTECTED COMPUTER IS WINDOWS, and the guard's Windows decisions were
until now read only through `pathlib` on Windows itself. The guard now
reads a path by the rules of the system its places name (`Places.os_name`),
so the places of a Windows computer (`inside.default_places(os_name="nt",
variables=..., home=...)`, built by the same code as on Windows) are put to
the guard here on macOS and Linux: each path read as Windows writes it
(`inside._windows_parts`: either slash, the drive or the share first, case
blind, dots resolved), and nothing of the file system asked.

WHAT IT REHEARSES. A record accepted in the account's local application
data folder whatever the case and the slashes; refused: a network or
device form (two slashes, a share, the device prefixes), a folder a cloud
service keeps in step (OneDrive and an organisation's OneDrive, Dropbox,
Google Drive's drive letter folder, Box, iCloud), the private folder itself
moved under OneDrive, the temporary folders, a downloads folder, and any
place outside the private folder (another drive, the documents folder,
the folder itself, two dots that climb out of it). The Windows reading of
a path is `pathlib`'s on Windows, checked against `pathlib.PureWindowsPath`
on every system.

WHAT IT CANNOT RUN HERE, said plainly (lane IN-8's report): the locality
gate's walk of each part for a link, a junction or a mount point (Windows
alone; a fake of it is lane IN-0's case), Windows' own resolution of a
mapped drive letter to its share (which the gate then refuses by its two
slashes), a cloud folder known by no name (a library synchronised under an
organisation's name), and the account's permissions: Windows has no POSIX
mode, synthtwin sets no access list, and a record keeps what the local
application data folder gives it. On Windows the rehearsal's cases stand
down (the guard's own gate file runs there natively); the reading of a
path runs everywhere.

Each clause is red on its mutant (lane IN-8's report).
"""

from __future__ import annotations

import ntpath
import os
import pathlib

import pytest

from synthtwin import inside, installation

REHEARSAL = installation.system_name() != "nt"
rehearsal_only = pytest.mark.skipif(not REHEARSAL, reason="on Windows the guard's own gate file runs natively")

HOME = "C:\\Users\\ana"
LOCAL = "C:\\Users\\ana\\AppData\\Local"
PRIVATE = "C:\\Users\\ana\\AppData\\Local\\synthtwin\\inside"
RECORD = "visits-0123456789ab.synthtwin-inside"


def _windows(local: str = LOCAL) -> inside.Places:
    return inside.default_places(os_name="nt", variables={"LOCALAPPDATA": local}, home=HOME)


PATHS = [
    "C:\\Users\\ana\\AppData\\Local\\synthtwin\\inside\\" + RECORD,
    "c:/users/ana/appdata/local/synthtwin/inside/" + RECORD,
    "C:\\Users\\ana\\AppData\\Local\\synthtwin\\inside\\",
    "C:\\Users\\ana/AppData\\Local/./synthtwin",
    "D:\\My Drive\\exports\\twin.csv",
    "\\\\server\\share\\folder\\" + RECORD,
    "//server/share/folder/" + RECORD,
    "\\\\?\\C:\\Users\\ana\\" + RECORD,
    "relative\\folder\\" + RECORD,
    "C:relative\\" + RECORD,
]


def test_the_windows_reading_of_a_path_is_pathlib_s_on_windows() -> None:
    for path in PATHS:
        assert inside._windows_parts(path) == list(pathlib.PureWindowsPath(path).parts), path
    climbing = "C:\\Users\\ana\\AppData\\Local\\synthtwin\\inside\\..\\..\\Temp\\" + RECORD
    assert inside._windows_parts(climbing) == list(pathlib.PureWindowsPath(ntpath.normpath(climbing)).parts)


def test_a_windows_computer_s_places_are_built_as_on_windows() -> None:
    places = _windows()
    assert places.os_name == "nt"
    assert inside._windows_parts(f"{places.private}") == inside._windows_parts(PRIVATE)
    temporary = [inside._windows_parts(f"{folder}") for folder in places.temporary]
    assert inside._windows_parts(LOCAL + "\\Temp") in temporary
    assert inside._windows_parts("C:\\Windows\\Temp") in temporary
    assert [inside._windows_parts(f"{folder}") for folder in places.downloads] == [inside._windows_parts(HOME + "\\Downloads")]


@rehearsal_only
@pytest.mark.parametrize("target", [
    PRIVATE + "\\" + RECORD,
    "c:\\users\\ANA\\appdata\\local\\SYNTHTWIN\\inside\\" + RECORD,
    "C:/Users/ana/AppData/Local/synthtwin/inside/" + RECORD,
    PRIVATE + "\\cohort\\" + RECORD,
])
def test_the_rehearsal_accepts_the_private_folder_in_any_case_and_slash(target: str) -> None:
    assert inside.place_refusal(target, _windows()) == ""


@rehearsal_only
@pytest.mark.parametrize(("target", "words"), [
    ("\\\\server\\share\\synthtwin\\inside\\" + RECORD, "shared network location"),
    ("//server/share/synthtwin/inside/" + RECORD, "shared network location"),
    ("\\\\?\\UNC\\server\\share\\" + RECORD, "device prefix"),
    ("\\\\?\\" + PRIVATE + "\\" + RECORD, "device prefix"),
    ("\\\\.\\pipe\\" + RECORD, "device prefix"),
])
def test_the_rehearsal_refuses_network_and_device_forms(target: str, words: str) -> None:
    assert words in inside.place_refusal(target, _windows())


@rehearsal_only
@pytest.mark.parametrize(("target", "part"), [
    (HOME + "\\OneDrive - Hospital\\synthtwin\\inside\\" + RECORD, "OneDrive - Hospital"),
    (HOME + "\\OneDrive\\Documents\\" + RECORD, "OneDrive"),
    (HOME + "\\Dropbox (Clinic)\\" + RECORD, "Dropbox (Clinic)"),
    ("G:\\My Drive\\synthtwin\\" + RECORD, "My Drive"),
    (HOME + "\\Google Drive\\" + RECORD, "Google Drive"),
    (HOME + "\\Box\\" + RECORD, "Box"),
    (HOME + "\\Box Sync\\" + RECORD, "Box Sync"),
    (HOME + "\\iCloudDrive\\" + RECORD, "iCloudDrive"),
])
def test_the_rehearsal_refuses_a_folder_a_cloud_service_keeps_in_step(target: str, part: str) -> None:
    reason = inside.place_refusal(target, _windows())
    assert "cloud service" in reason and repr(part) in reason, reason


@rehearsal_only
def test_the_rehearsal_refuses_the_private_folder_moved_under_onedrive() -> None:
    moved = HOME + "\\OneDrive - Hospital\\AppData\\Local"
    places = _windows(moved)
    target = moved + "\\synthtwin\\inside\\" + RECORD
    assert "cloud service" in inside.place_refusal(target, places)


@rehearsal_only
@pytest.mark.parametrize(("target", "words"), [
    (LOCAL + "\\Temp\\" + RECORD, "temporary folder"),
    ("C:\\Windows\\Temp\\" + RECORD, "temporary folder"),
    ("c:\\TEMP\\" + RECORD, "temporary folder"),
    (HOME + "\\Downloads\\" + RECORD, "downloads folder"),
    ("D:\\Exports\\downloads\\" + RECORD, "downloads folder"),
])
def test_the_rehearsal_refuses_temporary_and_downloads_folders(target: str, words: str) -> None:
    assert words in inside.place_refusal(target, _windows())


@rehearsal_only
@pytest.mark.parametrize("target", [
    HOME + "\\Documents\\" + RECORD,
    "Z:\\synthtwin\\inside\\" + RECORD,
    PRIVATE,
    PRIVATE + "\\..\\..\\" + RECORD,
    PRIVATE + "/../" + RECORD,
])
def test_the_rehearsal_refuses_a_place_outside_the_private_folder(target: str) -> None:
    assert "outside your private data folder" in inside.place_refusal(target, _windows())


@rehearsal_only
def test_the_guard_reads_a_rehearsed_path_as_written(monkeypatch: pytest.MonkeyPatch) -> None:
    """The guard's own reading asks nothing of this computer's files: no resolution, no version control, no mount.

    (The locality gate before it still resolves the text on this system,
    as it always does, and its result is set aside on a rehearsal.)
    """
    def refused(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("the rehearsal asked this computer's file system")

    monkeypatch.setattr(inside, "_resolved", refused)
    monkeypatch.setattr(os.path, "lexists", refused)
    monkeypatch.setattr(os.path, "ismount", refused)
    places = _windows()
    assert inside.place_refusal(PRIVATE + "\\" + RECORD, places) == ""
    assert "temporary folder" in inside.place_refusal(LOCAL + "\\Temp\\" + RECORD, places)
    assert "cloud service" in inside.place_refusal(HOME + "\\OneDrive\\" + RECORD, places)
