"""The inside record: the rich description that stays on the protected computer (plan P4-D495, lane IN-0).

WHAT IT IS. A description of a real table richer than the one the
strict rules let a person publish: every column's exact shape, every
category including the rare ones, and the zones later lanes add (the
relations between columns, the keyed rows, the date census, the
patient trajectories). It is a MODEL, never data: no row, no person's
list of values, no list of record numbers. It is patient information
all the same, so it never leaves the computer the real table is on.
Only the twin and the twin's report leave.

THE CONTRACT.

* The file's first line is `MARKER`, exactly. `write_record` writes it
  and nothing else as the first line; `load_record` refuses a file
  whose first line is anything else. The body after it is one line of
  JSON: an object with `format` (`FORMAT`), `version` (`VERSION`),
  `mode` (`MODE`, the one mode there is: the strict description of
  earlier batches was retired on 2026-11-18 and is not a mode of this
  record), `table` (the number of rows and the column names) and
  `zones`, one object a zone, each owned by the lane that fills it.
* Its size depends on the number of columns, categories, keys and grid
  points, never on the number of rows: a number keeps a quantile
  function of `GRID` points, a label at most `LEVEL_CAP` levels, a
  record number no value at all (only how many rows each value holds),
  a date a quantile function of its days and its weekday census, a
  clock also its minute-of-day census (a census by calendar day is the
  dates lane's, IN-5, in a form of fixed resolution). The gate file
  doubles the rows of three invented tables and holds the record's
  growth under 5 per cent.
* It is written only inside the owner's private data folder
  (`Places.private`, by default the installation's data folder of
  contract 4.6b.4, `installation.data_folder()`, then `FOLDER`). The
  guard (`place_refusal`) refuses, before anything is written: a path
  the locality gate refuses (`paths.validate_local_path`: a web or
  network form, a Windows device form, and on Windows a link, junction
  or mount point on the way); a temporary folder; a downloads folder;
  a folder a cloud service keeps in step with other computers
  (OneDrive, Dropbox, iCloud Drive, Google Drive, Box, by the folder's
  name); a folder under version control (git, Mercurial, Subversion);
  a mounted share or another disk on the way (on Linux the mount table
  names a network file system; on macOS and Linux a mount point between
  the private folder and the record, or a private folder under a
  mounted-volume root); any path outside the private folder; and, on
  macOS and Linux, a private folder or record folder other accounts may
  read or enter. The record is created with mode 0600 in a folder of
  mode 0700. On Windows the record inherits the account's own local
  application data folder (no POSIX mode); the Windows rehearsal of
  the guard is lane IN-8's.
* Nothing of it is printed. Every message of this module names a path,
  a size or a reason, never a value from a record; a damaged record is
  refused without quoting it.
* The export copies only the twin and its report (`export_manifest`):
  a file carrying the marker is never on the manifest, whatever its
  name, and `export` refuses to finish when the folder it wrote holds
  one. CI's sensitive-paths job fails on any file of the repository
  that starts with the marker (`tools/hooks/check_inside_records.py`).
  A file is read for the marker from its first line alone, whatever its
  size (`carries_marker`), and the writer refuses a record past
  `SIZE_CAP`, the size the loader refuses past, so every record written
  loads again.

No module of the package reads the environment except the
installation's data folder (`installation.data_folder`), so the guard
finds the temporary folders from the platform's fixed roots and the
account's home folder, and every place is a parameter the gate files
replace.
"""

import dataclasses
import json
import math
import os
import pathlib
import sys
import typing

from synthtwin import installation
from synthtwin.paths import PathValidationError, validate_local_path

MARKER = "SYNTHTWIN PROTECTED INSIDE RECORD 1 -- describes a real table; it stays on this computer, never shared, synced, printed or committed"
# The marker's bytes, written out (its text is ASCII; the gate file holds the two equal).
MARKER_BYTES = b"SYNTHTWIN PROTECTED INSIDE RECORD 1 -- describes a real table; it stays on this computer, never shared, synced, printed or committed"
BYTE_ORDER_MARK = b"\xef\xbb\xbf"
FORMAT = "synthtwin-inside"
VERSION = 1
MODE = "inside"
MODES = (MODE,)
SUFFIX = ".synthtwin-inside"
FOLDER = "inside"
GRID = 1001
LEVEL_CAP = 1000
SIZE_CAP = 256 * 1024 * 1024

# The twin's files and its report: the only files an export copies (the
# command's own suffixes, `cli._TWIN_SUFFIX`, `cli._WORKBOOK_TWIN_SUFFIX`
# and `cli._REPORT_SUFFIX`; the gate file holds them equal).
EXPORT_SUFFIXES = ("-twin.csv", "-twin.xlsx", "-twin-report.txt")

# Folder names a cloud service keeps in step with other computers, read
# case-blind on each part of the path; a part that starts with one of the
# prefixes is one too ("OneDrive - Hospital", "Dropbox (Team)", macOS's
# CloudStorage/OneDrive-Personal and GoogleDrive-name).
CLOUD_NAMES = ("onedrive", "dropbox", "icloud drive", "iclouddrive", "mobile documents", "com~apple~clouddocs",
               "google drive", "googledrive", "my drive", "box", "box sync", "cloudstorage")
CLOUD_PREFIXES = ("onedrive -", "onedrive-", "dropbox (", "dropbox-", "googledrive-", "box-")
VERSION_CONTROL = (".git", ".hg", ".svn")
DOWNLOADS = ("downloads",)
# Network file systems in a Linux mount table.
NETWORK_TYPES = ("nfs", "nfs4", "cifs", "smb3", "smbfs", "sshfs", "fuse.sshfs", "afpfs", "davfs", "fuse.rclone",
                 "9p", "afs", "glusterfs", "ceph", "fuse.s3fs", "webdav")
# Where a POSIX system mounts other disks and shares.
MOUNT_ROOTS = ("/Volumes", "/net", "/Network", "/mnt", "/media", "/run/media")
_DIGITS = "0123456789"


class InsideError(ValueError):
    """A refusal of the inside zone, in plain words naming paths, sizes and reasons only."""


@dataclasses.dataclass(frozen=True)
class Places:
    """Where a record may and may not go: the private folder, and the places refused by name."""

    private: pathlib.Path
    temporary: "tuple[pathlib.Path, ...]"
    downloads: "tuple[pathlib.Path, ...]"
    os_name: str
    mounts: "tuple[tuple[str, str], ...]" = ()


@dataclasses.dataclass(frozen=True)
class Written:
    """A record written: its path and its size in bytes (the two things a screen may say of it)."""

    path: pathlib.Path
    size: int


# -- words, read under the offline audit's exact type checks --------------------------------------


def _text(cell: object) -> str:
    """A cell or a name as text: refused where it is anything else."""
    if not isinstance(cell, str):
        raise TypeError("synthtwin reads a table's cells and a path's parts as text only.")
    return cell


def _low(word: object) -> str:
    if not isinstance(word, str):
        raise TypeError("synthtwin reads a path's parts as text only.")
    return word.lower()


def _bare(cell: object) -> str:
    if not isinstance(cell, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    return cell.strip()


def _is_cloud(part: object) -> bool:
    if not isinstance(part, str):
        raise TypeError("synthtwin reads a path's parts as text only.")
    low = part.lower()
    name = low.strip()
    if name in CLOUD_NAMES:
        return True
    for prefix in CLOUD_PREFIXES:
        if name[: len(prefix)] == prefix:
            return True
    return False


def _ends_with_one(name: object, suffixes: "tuple[str, ...]") -> bool:
    if not isinstance(name, str):
        raise TypeError("synthtwin reads a file's name as text only.")
    for suffix in suffixes:
        if suffix and name[len(name) - len(suffix):] == suffix:
            return True
    return False


def _under(here: object, point: object) -> bool:
    """Whether the path written `here` is the mount point written `point` or lies under it."""
    if not isinstance(here, str):
        raise TypeError("synthtwin reads a path as text only.")
    if not isinstance(point, str):
        raise TypeError("synthtwin reads a mount table's points as text only.")
    if here == point:
        return True
    root = point.rstrip("/") + "/"
    return here[: len(root)] == root


def _digits(text: str) -> bool:
    if not text:
        return False
    for character in text:
        if character not in _DIGITS:
            return False
    return True


# -- the places -------------------------------------------------------------------------------------------


def _home() -> pathlib.Path:
    return pathlib.Path(os.path.expanduser("~"))


def _mount_table() -> str:
    """The Linux mount table's text, '' where it cannot be read."""
    table = pathlib.Path("/proc/self/mounts")
    try:
        return table.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _mounts_of(text: object) -> "tuple[tuple[str, str], ...]":
    """The points and file-system types a mount table's text names."""
    if not isinstance(text, str):
        raise TypeError("synthtwin reads a mount table as text only.")
    found: "list[tuple[str, str]]" = []
    for line in text.split("\n"):
        mount = _mount_line(line)
        if mount is not None:
            found += [mount]
    return tuple(found)


def _mount_line(line: object) -> "tuple[str, str] | None":
    """One line of a mount table: its point (a space written \\040 read back) and its file-system type."""
    if not isinstance(line, str):
        raise TypeError("synthtwin reads a mount table as text only.")
    parts = line.split()
    if len(parts) < 3:
        return None
    return _unescaped(parts[1]), _text(parts[2])


def _unescaped(point: object) -> str:
    if not isinstance(point, str):
        raise TypeError("synthtwin reads a mount table as text only.")
    return point.replace("\\040", " ")


def _linux_mounts() -> "tuple[tuple[str, str], ...]":
    """The mount table's points and file-system types on Linux, () elsewhere or where it cannot be read."""
    if sys.platform != "linux":
        return ()
    return _mounts_of(_mount_table())


def default_places() -> Places:
    """The places of this computer: the installation's data folder, its fixed temporary roots, the downloads folder."""
    os_name = installation.system_name()
    home = _home()
    temporary: "tuple[pathlib.Path, ...]"
    if os_name == "nt":
        temporary = (pathlib.Path(home, "AppData", "Local", "Temp"), pathlib.Path("C:\\Windows\\Temp"),
                     pathlib.Path("C:\\Temp"), pathlib.Path("C:\\tmp"))
    else:
        temporary = (pathlib.Path("/tmp"), pathlib.Path("/var/tmp"), pathlib.Path("/private/tmp"),
                     pathlib.Path("/private/var/tmp"), pathlib.Path("/var/folders"), pathlib.Path("/private/var/folders"),
                     pathlib.Path("/dev/shm"))
    return Places(pathlib.Path(installation.data_folder(), FOLDER), temporary, (pathlib.Path(home, "Downloads"),),
                  os_name, _linux_mounts())


def _resolved(path: object) -> pathlib.Path:
    return pathlib.Path(os.path.realpath(f"{path}"))


def _parts(path: object) -> "list[str]":
    """The resolved path's parts, case-blind on Windows."""
    out: "list[str]" = []
    for part in _resolved(path).parts:
        out += [_low(part) if sys.platform == "win32" else _text(part)]
    return out


def _identity(path: object) -> "tuple[int, int] | None":
    """The file system's own name of a standing path, its device and its file number; None where it does not stand or the file system gives no number."""
    try:
        found = pathlib.Path(f"{path}").stat()
    except OSError:
        return None
    if found.st_ino == 0:
        return None
    return found.st_dev, found.st_ino


def _inside(path: object, folder: object) -> bool:
    """Whether `path` is `folder` or lies under it.

    Both resolved and compared part by part (case-blind on Windows); and
    BY THE FILE SYSTEM'S IDENTITY (the batch 4w Codex review, item 7):
    where `folder` stands, `path` lies in it when the folder or any of
    its own standing folders is that folder to the file system. A
    case-blind volume (macOS's and Windows' by default) reads
    `/private/TMP` and `/private/tmp` as one folder, so a record under
    the first spelling lay in a temporary folder the parts alone did not
    see.
    """
    here = _parts(path)
    there = _parts(folder)
    if len(here) >= len(there) and here[: len(there)] == there:
        return True
    wanted = _identity(_resolved(folder))
    if wanted is None:
        return False
    current = _resolved(path)
    for step in [current, *current.parents]:
        if _identity(step) == wanted:
            return True
    return False


def _one_place(path: object, folder: object) -> bool:
    """Whether two paths are one place: their resolved parts (case-blind on Windows), or, both standing, the file system's identity."""
    if _parts(path) == _parts(folder):
        return True
    wanted = _identity(_resolved(folder))
    return wanted is not None and _identity(_resolved(path)) == wanted


def _cloud_part(path: object) -> str:
    for part in _resolved(path).parts:
        if _is_cloud(part):
            return _text(part)
    return ""


def _version_control(path: object) -> str:
    """The first folder above `path` that holds a version-control folder or file, '' where none does."""
    here = _resolved(path)
    for folder in [here, *here.parents]:
        for name in VERSION_CONTROL:
            if os.path.lexists(f"{pathlib.Path(f'{folder}', name)}"):
                return f"{folder}"
    return ""


def _network_mount(path: object, places: Places) -> str:
    """Why `path` may sit on a mounted share or another disk ('' where it does not), on macOS and Linux."""
    if places.os_name == "nt":
        return ""
    here = f"{_resolved(path)}"
    best, kind = "", ""
    for point, fs_type in places.mounts:
        if _under(here, point) and len(f"{point}") >= len(best):
            best, kind = f"{point}", f"{fs_type}"
    if _low(kind) in NETWORK_TYPES:
        return f"the mount table says {best!r} is a network file system ({kind})"
    private = f"{_resolved(places.private)}"
    for root in MOUNT_ROOTS:
        if _under(private, root) or _inside(private, root):
            return f"the private folder itself lies under {root}, where other disks and network shares are mounted"
    folder = _resolved(path)
    stop = _resolved(places.private)
    for part in [folder, *folder.parents]:
        if f"{part}" == f"{stop}" or len(pathlib.Path(f"{part}").parts) <= len(stop.parts):
            break
        if os.path.ismount(f"{part}"):
            return f"{f'{part}'!r} is a mount point between the private folder and the record"
    return ""


def _open_to_others(folder: object, os_name: str) -> bool:
    """POSIX: a folder that stands and that the group or other accounts may read, write or enter."""
    here = pathlib.Path(f"{folder}")
    if os_name == "nt" or not here.is_dir():
        return False
    return here.stat().st_mode & 0o077 != 0


def place_refusal(target: "str | pathlib.Path", places: "Places | None" = None) -> str:
    """Why a record may not be written at `target` ('' where it may), checked before anything is written."""
    here = places if places is not None else default_places()
    try:
        validated = validate_local_path(f"{target}", purpose="inside record")
    except PathValidationError as refused:
        return f"{refused}"
    for folder in here.temporary:
        if _inside(validated, folder):
            return (f"The inside record was not written: {f'{validated}'!r} lies in a temporary folder ({f'{folder}'!r}), "
                    "which the system or other programs may copy, keep or clear.")
    for folder in here.downloads:
        if _inside(validated, folder):
            return (f"The inside record was not written: {f'{validated}'!r} lies in a downloads folder ({f'{folder}'!r}), "
                    "where files are shared and synchronised.")
    for part in _resolved(validated).parts:
        if _low(part) in DOWNLOADS:
            return (f"The inside record was not written: {f'{validated}'!r} lies in a downloads folder ({part!r}), "
                    "where files are shared and synchronised.")
    cloud = _cloud_part(validated)
    if cloud:
        return (f"The inside record was not written: {f'{validated}'!r} lies in a folder a cloud service keeps in step "
                f"with other computers ({cloud!r}). Keep it on this computer's own disk, in your private data folder.")
    held = _version_control(validated)
    if held:
        return (f"The inside record was not written: {f'{validated}'!r} lies in a folder under version control "
                f"({held!r}), from which files are committed and shared.")
    mounted = _network_mount(validated, here)
    if mounted:
        return (f"The inside record was not written: {f'{validated}'!r} may lie on a network share or another disk: "
                f"{mounted}. Keep it on this computer's own disk, in your private data folder.")
    if not _inside(validated, here.private) or _one_place(validated, here.private):
        return (f"The inside record was not written: {f'{validated}'!r} lies outside your private data folder "
                f"({f'{here.private}'!r}), the one place an inside record is kept.")
    for folder in (here.private, validated.parent):
        if _open_to_others(folder, here.os_name):
            return (f"The inside record was not written: the folder {f'{folder}'!r} can be read or entered by other "
                    f"accounts on this computer. Make it yours alone (on macOS or Linux: chmod 700 '{folder}').")
    return ""


def record_path(stem: str, places: "Places | None" = None) -> pathlib.Path:
    """The default place of a table's record: the private folder, the table's stem, the record's suffix."""
    here = places if places is not None else default_places()
    return pathlib.Path(f"{here.private}", f"{stem}{SUFFIX}")


# -- the record ---------------------------------------------------------------------------------------------


def _validate_record(record: object) -> "dict[str, object]":
    """The record checked for the contract's keys; its values are never quoted."""
    if not isinstance(record, dict):
        raise InsideError("An inside record must be a JSON object; this one is not.")
    for key, wanted in (("format", FORMAT), ("version", VERSION)):
        if key not in record or record[key] != wanted:
            raise InsideError(f"An inside record names its {key} as {wanted!r}; this one does not.")
    if "mode" not in record or record["mode"] not in MODES:
        raise InsideError(
            "An inside record names its mode, and the one mode there is is 'inside' (the strict description is "
            "retired and is never an inside record); this one names another or none.")
    for key in ("table", "zones"):
        if key not in record or not isinstance(record[key], dict):
            raise InsideError(f"An inside record holds an object under {key!r}; this one does not.")
    return typing.cast("dict[str, object]", record)


def _record_text(record: "dict[str, object]") -> str:
    body = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    text = MARKER + "\n" + body + "\n"
    if text.split("\n")[0] != MARKER or "\n" in body:
        raise InsideError("An inside record's first line must be the protected marker and its body one line.")
    return text


def write_record(record: "dict[str, object]", target: "str | pathlib.Path", places: "Places | None" = None) -> Written:
    """Write a record at `target` inside the private folder (mode 0600 in a 0700 folder), the guard first.

    THE WRITER HOLDS THE LOADER'S BOUND (the batch 4w Codex review, item
    8): a record whose text is past `SIZE_CAP` bytes is refused before
    anything is written, so every record written can be loaded again.
    """
    checked = _validate_record(record)
    text = _record_text(checked)
    size = len(bytes(text, "utf-8"))
    if size > SIZE_CAP:
        raise InsideError(
            f"The inside record was not written: it would hold {size} bytes, more than the {SIZE_CAP} bytes an "
            "inside record may hold.")
    here = places if places is not None else default_places()
    refusal = place_refusal(target, here)
    if refusal:
        raise InsideError(refusal)
    path = validate_local_path(f"{target}", purpose="inside record")
    if path.exists() and not carries_marker(path):
        raise InsideError(
            f"The inside record was not written: {f'{path}'!r} already holds a file that is not an inside record, "
            "and synthtwin never writes over it.")
    private = pathlib.Path(f"{here.private}")
    private.mkdir(mode=0o700, parents=True, exist_ok=True)
    folder = pathlib.Path(f"{path.parent}")
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    if here.os_name != "nt":
        private.chmod(0o700)
        folder.chmod(0o700)
    temporary = pathlib.Path(f"{folder}", f"{path.name}.new")
    if temporary.exists():
        temporary.unlink()
    temporary.touch(mode=0o600, exist_ok=False)
    if here.os_name != "nt":
        temporary.chmod(0o600)
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)
    return Written(path, path.stat().st_size)


def carries_marker(path: "str | pathlib.Path") -> bool:
    """Whether the file starts with the marker (a byte-order mark before it allowed), WHATEVER ITS SIZE.

    Read from the file's first line alone (`_first_line`), never the
    whole file: a marked file past `SIZE_CAP` is still a marked file (the
    batch 4w Codex review, item 8: a 257 MiB record renamed as a twin was
    read as unmarked, put on the export's manifest and copied out).
    """
    validated = validate_local_path(f"{path}", purpose="file")
    here = pathlib.Path(validated)
    if not here.is_file():
        return False
    head = _first_line(here)
    if head[: len(BYTE_ORDER_MARK)] == BYTE_ORDER_MARK:
        head = head[len(BYTE_ORDER_MARK):]
    return head[: len(MARKER_BYTES)] == MARKER_BYTES


def _first_line(path: pathlib.Path) -> bytes:
    """A file's first line up to the marker's length past a byte-order mark, its bytes one for one (read as Latin-1, whose characters are bytes)."""
    found = ""
    with pathlib.Path(f"{path}").open("r", encoding="latin-1", newline="") as handle:
        for line in handle:
            found = line
            break
    return bytes([ord(character) for character in found[: len(BYTE_ORDER_MARK) + len(MARKER_BYTES)]])


def load_record(path: "str | pathlib.Path") -> "dict[str, object]":
    """Read a record: the marker first, then the contract's keys; a refusal names the path and the size only."""
    validated = validate_local_path(f"{path}", purpose="inside record")
    here = pathlib.Path(validated)
    if not here.is_file():
        raise InsideError(f"No inside record was found at {f'{here}'!r}.")
    size = here.stat().st_size
    if size > SIZE_CAP:
        raise InsideError(f"The file at {f'{here}'!r} ({size} bytes) is larger than any inside record.")
    if not carries_marker(here):
        raise InsideError(
            f"The file at {f'{here}'!r} ({size} bytes) does not start with the inside record's protected marker, "
            "so it is not read as one.")
    try:
        loaded = json.loads(_body_of(here.read_text(encoding="utf-8-sig")))
    except (UnicodeDecodeError, ValueError):
        raise InsideError(
            f"The inside record at {f'{here}'!r} ({size} bytes) is damaged: its body is not readable. "
            "Describe the table again to write it anew.") from None
    return _validate_record(loaded)


def _body_of(text: object) -> str:
    """A record's body: its second line."""
    if not isinstance(text, str):
        raise TypeError("synthtwin reads an inside record as text only.")
    lines = text.split("\n")
    return lines[1] if len(lines) > 1 else ""


def describe(path: "str | pathlib.Path") -> str:
    """What a screen, a log or an error may say of a record: its path and its size, never a value."""
    validated = validate_local_path(f"{path}", purpose="inside record")
    here = pathlib.Path(validated)
    size = here.stat().st_size if here.is_file() else 0
    return f"inside record (stays on this computer): {f'{here}'!r}, {size} bytes"


# -- the export -----------------------------------------------------------------------------------


def export_manifest(folder: "str | pathlib.Path") -> "tuple[pathlib.Path, ...]":
    """The files an export may copy from `folder`: the twin and its report, never a file carrying the marker."""
    here = pathlib.Path(validate_local_path(f"{folder}", purpose="export folder"))
    found: "list[pathlib.Path]" = []
    for raw in sorted(here.iterdir()):
        entry = pathlib.Path(f"{raw}")
        if not entry.is_file() or entry.is_symlink():
            continue
        if not _ends_with_one(entry.name, EXPORT_SUFFIXES):
            continue
        if _ends_with_one(entry.name, (SUFFIX,)) or carries_marker(entry):
            continue
        found += [entry]
    return tuple(found)


def export(folder: "str | pathlib.Path", destination: "str | pathlib.Path") -> "tuple[pathlib.Path, ...]":
    """Copy the manifest's files into `destination`; refuse to finish where the destination then holds a record."""
    files = export_manifest(folder)
    there = pathlib.Path(validate_local_path(f"{destination}", purpose="export destination"))
    there.mkdir(parents=True, exist_ok=True)
    copied: "list[pathlib.Path]" = []
    for source in files:
        origin = pathlib.Path(f"{source}")
        target = pathlib.Path(f"{there}", f"{origin.name}")
        if target.exists() and carries_marker(target):
            raise InsideError(f"The export was stopped: {f'{target}'!r} is an inside record and is never written over.")
        target.write_bytes(origin.read_bytes())
        copied += [target]
    for raw in sorted(there.iterdir()):
        entry = pathlib.Path(f"{raw}")
        if entry.is_file() and (_ends_with_one(entry.name, (SUFFIX,)) or carries_marker(entry)):
            raise InsideError(
                f"The export folder {f'{there}'!r} holds an inside record ({f'{entry}'!r}); a record never leaves this "
                "computer. Remove it from the folder before anything is shared.")
    return tuple(copied)


# -- the record of a table (the zone of the marginals, lane IN-0) --------------------------------------


def _number(cell: object) -> "float | None":
    text = _bare(cell)
    if not text or _low(text) in ("nan", "inf", "-inf", "+inf", "infinity", "-infinity"):
        return None
    try:
        value = float(text)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def _decimals(cell: object) -> int:
    if not isinstance(cell, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    pieces = cell.strip().split(".")
    return len(pieces[1]) if len(pieces) > 1 else 0


def _date_parts(cell: object) -> "tuple[str, int] | None":
    """A cell written YYYY-MM-DD, with an optional HH:MM after a space or a T: its day and its minute of the day (-1 if none)."""
    if not isinstance(cell, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    text = cell.strip()
    if len(text) < 10 or text[4] != "-" or text[7] != "-" or not _digits(text[:4] + text[5:7] + text[8:10]):
        return None
    rest = text[10:].strip().lstrip("T").rstrip("Z")
    if not rest:
        return text[:10], -1
    if len(rest) >= 5 and rest[2] == ":" and _digits(rest[:2] + rest[3:5]):
        return text[:10], int(rest[:2]) * 60 + int(rest[3:5])
    return None


def _weekday(day: object) -> int:
    """Monday 0 to Sunday 6 of a day written YYYY-MM-DD (Zeller's congruence; no calendar module is needed)."""
    text = _text(day)
    year, month, date = int(text[:4]), int(text[5:7]), int(text[8:10])
    if month < 3:
        month += 12
        year -= 1
    zeller = (date + (13 * (month + 1)) // 5 + year + year // 4 - year // 100 + year // 400) % 7
    return (zeller + 5) % 7


def _grid(values: "list[float]") -> "list[float]":
    """The quantile function on `GRID` points, each an observed value (the lower order statistic)."""
    ordered = sorted(values)
    last = len(ordered) - 1
    out: "list[float]" = []
    for k in range(GRID):
        out += [ordered[(k * last) // (GRID - 1)]]
    return out


def _levels(cells: "list[str]") -> "dict[str, int]":
    counts: "dict[str, int]" = {}
    for cell in cells:
        counts[cell] = (counts[cell] if cell in counts else 0) + 1
    return counts


def _capped(counts: "dict[str, int]") -> "dict[str, object]":
    """A category table: every level when there are at most `LEVEL_CAP`, else the commonest and the rest's count."""
    ranked = sorted((-counts[level], level) for level in counts)
    kept: "dict[str, int]" = {}
    other = 0
    for negative, level in ranked:
        if len(kept) < LEVEL_CAP:
            kept[level] = -negative
        else:
            other += -negative
    return {"levels": kept, "other_levels": len(ranked) - len(kept), "other_rows": other}


def _column_zone(cells: "list[str]", identifier: bool) -> "dict[str, object]":
    filled = [cell for cell in cells if _bare(cell)]
    entry: "dict[str, object]" = {"rows": len(cells), "empty": len(cells) - len(filled)}
    counts = _levels(filled)
    if identifier:
        census: "dict[str, int]" = {}
        for level in counts:
            many = f"{counts[level]}"
            census[many] = (census[many] if many in census else 0) + 1
        entry["kind"] = "identifier"
        entry["values"] = len(counts)
        entry["rows_per_value"] = census
        return entry
    dates = [_date_parts(cell) for cell in filled]
    known: "list[tuple[str, int]]" = []
    for part in dates:
        if part is not None:
            known += [part]
    if filled and len(known) == len(filled):
        ordered = sorted(day for day, _minute in known)
        last = len(ordered) - 1
        entry["kind"] = "date"
        entry["quantiles"] = [ordered[(k * last) // (GRID - 1)] for k in range(GRID)]
        entry["weekdays"] = _levels([f"{_weekday(day)}" for day, _minute in known])
        entry["minutes"] = _levels([f"{minute}" for _day, minute in known if minute >= 0])
        return entry
    numbers = [_number(cell) for cell in filled]
    given: "list[float]" = []
    words: "list[str]" = []
    places: "list[str]" = []
    for cell, value in zip(filled, numbers):
        if value is None:
            words += [cell]
        else:
            given += [value]
            places += [f"{_decimals(cell)}"]
    if filled and len(given) >= 0.8 * len(filled) and len(counts) > 2:
        entry["kind"] = "number"
        entry["quantiles"] = _grid(given)
        entry["decimals"] = _levels(places)
        entry["words"] = _capped(_levels(words))
        return entry
    entry["kind"] = "label"
    capped = _capped(counts)
    for key in capped:
        entry[key] = capped[key]
    return entry


def column_entry(column: "list[str]", identifier: bool) -> "dict[str, object]":
    """One column's entry of the marginals zone (`build_record`'s, a column at a time, as a describe run reads them).

    `identifier` says the person or the description reads the column as
    record numbers; a column whose cells are nearly all different words
    is read as one too. Of those the entry keeps no value, only how many
    rows each value holds.
    """
    cells = [_text(cell) for cell in column]
    filled = [cell for cell in cells if _bare(cell)]
    distinct = len(set(filled))
    dated = bool(filled) and all(_date_parts(cell) is not None for cell in filled)
    wordy = bool(filled) and not dated and distinct > 0.5 * len(filled) and sum(
        1 for cell in filled if _number(cell) is None) > 0.5 * len(filled)
    return _column_zone(cells, identifier or wordy)


def in_temporary(target: "str | pathlib.Path", places: "Places | None" = None) -> bool:
    """Whether `target` lies in one of the temporary folders the guard refuses (a run whose data folder is a test's)."""
    here = places if places is not None else default_places()
    for folder in here.temporary:
        if _inside(target, folder):
            return True
    return False


def build_record(columns: "dict[str, list[str]]", identifiers: "tuple[str, ...]" = ()) -> "dict[str, object]":
    """The record of a table (its marginals zone): one entry a column, sized by columns, levels and grid points.

    `columns` maps each column's name to its cells as read; `identifiers`
    names the columns the person said are record numbers (and any column
    whose cells are nearly all different words is one too): of those the
    record keeps no value, only how many rows each value holds.
    """
    names = [name for name in columns]
    rows = len(columns[names[0]]) if names else 0
    zone: "dict[str, object]" = {}
    for name in names:
        zone[name] = column_entry(columns[name], name in identifiers)
    return {"format": FORMAT, "version": VERSION, "mode": MODE,
            "table": {"rows": rows, "columns": names}, "zones": {"marginals": zone}}
