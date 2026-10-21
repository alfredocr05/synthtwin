"""The installation's private key, its ledger and its lock (contract 4.6b.4; lane CHa, plan P4-D418).

NOT IN FORCE. Only a caller holding the chain's switch reaches this
module (`cli._run_profile(..., chain=...)`, the tools); `synthtwin
profile` never does, so no shipped run makes a key, a ledger or a lock.

THE KEY is 32 bytes from `secrets.token_bytes`, made by the first run on
the installation and kept in the installation's DATA FOLDER, a folder
private to the user's account: on POSIX `$XDG_DATA_HOME/synthtwin` (or
`~/.local/share/synthtwin`; `~/Library/Application Support/synthtwin` on
macOS), the folder made 0700 and the key file 0600; on Windows
`%LOCALAPPDATA%\\synthtwin`, the user's own local application data. A key
file another account can read or write is refused, in plain words, until
it is fixed. The key is never written into the description, the twin,
any log, the shared report or the private report; the private report
names only the key file's path (`key_path`).

THE LEDGER is a file beside the key (0600). It holds, for each table
described on the installation, its name, its content hash
(`chain.content_hash`), the fingerprint of the key that described it
(keyed BLAKE2b of `b"key fingerprint"`, `person=b"synthtwin.kfp.1"`, a
domain no draw word uses) and the DESCRIPTION DIGEST of what that run
published (unkeyed BLAKE2b over the canonical description less the keys
that stamp the run, `person=b"synthtwin.desc.1"`). Its decisions are
printed on the screen of the person who holds the table and never
written into any published file (inventory row 33).

THE LOCK is a file made in the data folder with `pathlib.Path.touch(...,
exist_ok=False)`, which is `os.open` with `O_CREAT | O_EXCL` (standard
library, the same on every platform), held from the moment the ledger is
read until the description and its entry are both written. The entry is
written first, to a temporary file moved into place with `os.replace`
(`pathlib.Path.replace`), and the description after it.
"""

import dataclasses
import hashlib
import json
import os
import pathlib
import secrets
import sys

from synthtwin import canonical

FOLDER = "synthtwin"
KEY_FILE = "chain-key"
# The record holds JSON but takes no ending: it lives in the installation's
# data folder, never among the files a run leaves beside the twin.
LEDGER_FILE = "chain-ledger"
LOCK_FILE = "chain-profile.lock"
LEDGER_VERSION = 1
KEY_BYTES = 32

# The keys of a description that stamp the run rather than describe the
# table (contract 4.1: the producer's version; no key records a time or a
# path), left out of the protected publication.
STAMPS = ("created_with",)

PROCEED = "proceed"
WARN = "warn"
REFUSE = "refuse"


@dataclasses.dataclass(frozen=True)
class Entry:
    """One table's line of the ledger."""

    name: str
    content: str
    fingerprint: str
    digest: str
    between: bool


@dataclasses.dataclass(frozen=True)
class Decision:
    """What the ledger says about a run: proceed, warn and proceed, or refuse, and the words."""

    verdict: str
    words: str


def system_name() -> str:
    """`nt` on Windows, `posix` elsewhere, read from `sys.platform`."""
    return "nt" if sys.platform == "win32" else "posix"


def data_folder(
    os_name: "str | None" = None,
    environ: "dict[str, str] | None" = None,
    home: "str | None" = None,
    platform: "str | None" = None,
) -> pathlib.Path:
    """The installation's data folder on this platform (4.6b.4).

    `os_name`, `environ`, `home` and `platform` stand in for `os.name`,
    `os.environ`, the home folder and `sys.platform`, so the Windows form
    is tested on every platform.
    """
    name = os_name if os_name is not None else system_name()
    where = environ if environ is not None else dict(os.environ)
    own = home if home is not None else os.path.expanduser("~")
    system = platform if platform is not None else sys.platform
    if name == "nt":
        local = where["LOCALAPPDATA"] if "LOCALAPPDATA" in where else ""
        if not local:
            local = os.path.join(own, "AppData", "Local")
        return pathlib.Path(local, FOLDER)
    xdg = where["XDG_DATA_HOME"] if "XDG_DATA_HOME" in where else ""
    if xdg:
        return pathlib.Path(xdg, FOLDER)
    if system == "darwin":
        return pathlib.Path(own, "Library", "Application Support", FOLDER)
    return pathlib.Path(own, ".local", "share", FOLDER)


def key_path(folder: pathlib.Path) -> pathlib.Path:
    """The key file's path: the one thing about the key a report may name."""
    return pathlib.Path(folder, KEY_FILE)


def fingerprint(key: bytes) -> str:
    """The key's FINGERPRINT: keyed BLAKE2b of `b"key fingerprint"`, 8 bytes, as hex."""
    return hashlib.blake2b(
        b"key fingerprint", key=key, digest_size=8, person=b"synthtwin.kfp.1"
    ).hexdigest()


def description_digest(document: "dict[str, object]") -> str:
    """The DESCRIPTION DIGEST: unkeyed BLAKE2b over the protected publication, as hex.

    The whole description in its canonical serialization, less only the
    keys that stamp the run (`STAMPS`), so another setting, another column
    block or another chain each gives another digest, and a description
    whose `statistical` is `null` is digested whole too.
    """
    protected: "dict[str, object]" = {}
    for key in document:
        if key not in STAMPS:
            protected[key] = document[key]
    text = canonical.serialize(protected)
    return hashlib.blake2b(
        bytes(text, "utf-8"), digest_size=32, person=b"synthtwin.desc.1"
    ).hexdigest()


def publishes_between(document: "dict[str, object]") -> bool:
    """Whether a description publishes something between columns (`statistical` not null)."""
    if "relationships" not in document:
        return False
    block = document["relationships"]
    if not isinstance(block, dict) or "statistical" not in block:
        return False
    return block["statistical"] is not None


# -- THE WORDS PRINTED ON THE SCREEN (4.6b.4), never written anywhere ----


def words_changed(name: str) -> str:
    return (
        f"This table was described before under the name '{name}', and this "
        "run would publish a different description of it (an answer, a "
        "setting or a newer version of synthtwin changed it). Someone holding "
        "both descriptions could narrow a small group of patients. If the "
        "earlier description was never shared with anyone, run again with "
        "--replace-description; otherwise share only the earlier one."
    )


def words_other_name(old: str) -> str:
    return (
        f"This table was described before under the name '{old}'. Describing "
        "it again under another name would give a second, different "
        "description, and someone holding both could narrow a small group of "
        f"patients. Run again with --name {old}."
    )


def words_other_key(path: str) -> str:
    return (
        "This table was described before with a different private key. "
        "Describing it again could let someone who holds both descriptions "
        f"narrow a small group of patients. Put the old key file back at {path}; "
        "or, if no description of this table made with the old key was ever "
        "shared, run again with --replace-description."
    )


def words_name_reused(name: str) -> str:
    return (
        f"A different table was described before under the name '{name}'. If "
        "this is a newer extract of the same table, share only one of the two "
        "descriptions with the same people; if it is a different table, run "
        "again with --name and a new name."
    )


def words_key_missing(path: str) -> str:
    return (
        f"The private key at {path} is missing, but this installation has "
        "described tables before. Put the key file back. If it is lost, run "
        "again with --new-key: each table described before will then be "
        "refused until you confirm, with --replace-description, that its "
        "earlier descriptions were never shared."
    )


def words_key_made(path: str) -> str:
    return (
        f"A new private key was made at {path}. Keep it: describing the same "
        "table again needs the same key."
    )


def words_ledger_started(path: str) -> str:
    return (
        "No record of earlier descriptions was found beside the private key "
        f"at {path}, so a new record was started. If this installation "
        "described tables before, describe each again only under its old name."
    )


def words_ledger_unreadable(path: str) -> str:
    return (
        f"The record of earlier descriptions at {path} cannot be read. Put back "
        "a copy that can; or, if no description made on this installation was "
        "ever shared, move it aside and run again."
    )


def words_locked(path: str) -> str:
    return (
        "Another synthtwin profile is running on this installation. Run again "
        "when it has finished. If none is running (the computer stopped during "
        f"a run), delete {path} and run again."
    )


def words_key_open(path: str) -> str:
    return (
        f"The private key at {path} can be read or changed by other accounts on "
        "this computer. Make it readable by you alone (on macOS or Linux: chmod "
        f"600 '{path}'), then run again."
    )


def words_new_key_refused() -> str:
    return (
        "--new-key makes a new private key only where this installation has "
        "described tables before and its key file cannot be read. Run again "
        "without it."
    )


# -- THE KEY ---------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Opened:
    """The installation opened for one run: its key and its ledger, or a refusal."""

    folder: pathlib.Path
    key: bytes = dataclasses.field(repr=False)
    entries: "tuple[Entry, ...]"
    lines: "tuple[str, ...]"
    refusal: str
    locked: bool


def _mode_is_private(path: pathlib.Path, os_name: str) -> bool:
    """POSIX: no permission for the group or others. Windows: the folder's own (no POSIX mode)."""
    if os_name == "nt":
        return True
    here = pathlib.Path(path)
    return here.stat().st_mode & 0o077 == 0


def _read_ledger(path: pathlib.Path) -> "tuple[Entry, ...] | None":
    """The ledger's entries, or None where it cannot be read."""
    here = pathlib.Path(path)
    try:
        loaded = json.loads(here.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return None
    if not isinstance(loaded, dict) or "version" not in loaded or "tables" not in loaded:
        return None
    if loaded["version"] != LEDGER_VERSION or not isinstance(loaded["tables"], list):
        return None
    out: "list[Entry]" = []
    for entry in loaded["tables"]:
        if not isinstance(entry, dict):
            return None
        fields: "list[object]" = []
        for key in ("name", "content", "fingerprint", "digest", "between"):
            if key not in entry:
                return None
            fields += [entry[key]]
        name, content, mark, digest, between = fields
        if not (isinstance(name, str) and isinstance(content, str) and isinstance(mark, str) and isinstance(digest, str) and isinstance(between, bool)):
            return None
        out += [Entry(name, content, mark, digest, between)]
    return tuple(out)


def open_installation(
    folder: pathlib.Path,
    new_key: bool = False,
    os_name: "str | None" = None,
) -> Opened:
    """Open the data folder before anything is read: take the lock, read the key and the ledger.

    Refuses (an `Opened` whose `refusal` holds the words) where another run
    holds the lock, where a ledger stands without a readable key (unless
    `new_key`), where the ledger cannot be read, or where the key file is
    open to other accounts. Makes the folder and the key where neither key
    nor ledger exists. `os_name` stands in for `os.name`.
    """
    name = os_name if os_name is not None else system_name()
    here = pathlib.Path(folder)
    here.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock = pathlib.Path(folder, LOCK_FILE)
    try:
        lock.touch(mode=0o600, exist_ok=False)
    except FileExistsError:
        return Opened(folder, b"", (), (), words_locked(f"{lock}"), False)
    key_file = pathlib.Path(key_path(folder))
    ledger_file = pathlib.Path(folder, LEDGER_FILE)
    lines: "list[str]" = []
    has_key = key_file.is_file()
    has_ledger = ledger_file.is_file()
    if new_key and (has_key or not has_ledger):
        return Opened(folder, b"", (), (), words_new_key_refused(), True)
    entries: "tuple[Entry, ...]" = ()
    if has_ledger:
        read = _read_ledger(ledger_file)
        if read is None:
            return Opened(folder, b"", (), (), words_ledger_unreadable(f"{ledger_file}"), True)
        entries = read
    key = b""
    if has_key:
        if not _mode_is_private(key_file, name):
            return Opened(folder, b"", (), (), words_key_open(f"{key_file}"), True)
        try:
            key = key_file.read_bytes()
        except OSError:
            key = b""
        if len(key) != KEY_BYTES:
            if has_ledger and not new_key:
                return Opened(folder, b"", (), (), words_key_missing(f"{key_file}"), True)
            key = b""
    elif has_ledger and not new_key:
        return Opened(folder, b"", (), (), words_key_missing(f"{key_file}"), True)
    if not key:
        key = secrets.token_bytes(KEY_BYTES)
        if key_file.exists():
            return Opened(folder, b"", (), (), words_key_missing(f"{key_file}"), True)
        key_file.touch(mode=0o600, exist_ok=False)
        if name != "nt":
            key_file.chmod(0o600)
        key_file.write_bytes(key)
        lines += [words_key_made(f"{key_file}")]
    if has_key and not has_ledger:
        lines += [words_ledger_started(f"{key_file}")]
    return Opened(folder, key, entries, tuple(lines), "", True)


def release(opened: Opened) -> None:
    """Remove the lock this run holds; nothing where it holds none."""
    if opened.locked:
        lock = pathlib.Path(opened.folder, LOCK_FILE)
        if lock.exists():
            lock.unlink()


# -- THE LEDGER'S DECISIONS (4.6b.4) --------------------------------------


def decide(
    opened: Opened,
    name: str,
    content: str,
    digest: str,
    between: bool,
    replace: bool = False,
) -> Decision:
    """The ledger's decision on one run, read before anything is published.

    - same content, name and key, same description: proceed;
    - same content, name and key, a different description where either
      publishes something between columns: refused (proceeds with
      `replace`); where neither does, recorded without a refusal;
    - the same content under another name: refused;
    - the same content under another key: refused (proceeds with `replace`);
    - a different content under a name already used: a one-line warning.
    """
    mark = fingerprint(opened.key)
    for entry in opened.entries:
        if entry.content != content:
            continue
        if entry.name != name:
            return Decision(REFUSE, words_other_name(entry.name))
        if entry.fingerprint != mark:
            if replace:
                return Decision(PROCEED, "")
            return Decision(REFUSE, words_other_key(f"{key_path(opened.folder)}"))
        if entry.digest == digest:
            return Decision(PROCEED, "")
        if not entry.between and not between:
            return Decision(PROCEED, "")
        if replace:
            return Decision(PROCEED, "")
        return Decision(REFUSE, words_changed(name))
    for entry in opened.entries:
        if entry.name == name:
            return Decision(WARN, words_name_reused(name))
    return Decision(PROCEED, "")


def record(opened: Opened, entry: Entry) -> None:
    """Write the run's entry, replacing the table's earlier one, by a temporary file moved into place."""
    kept: "list[dict[str, object]]" = []
    for old in opened.entries:
        if old.content == entry.content:
            continue
        kept += [dataclasses.asdict(old)]
    kept += [dataclasses.asdict(entry)]
    text = json.dumps({"tables": kept, "version": LEDGER_VERSION}, sort_keys=True, indent=2) + "\n"
    target = pathlib.Path(opened.folder, LEDGER_FILE)
    temporary = pathlib.Path(opened.folder, LEDGER_FILE + ".new")
    if temporary.exists():
        temporary.unlink()
    temporary.touch(mode=0o600, exist_ok=False)
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(target)
