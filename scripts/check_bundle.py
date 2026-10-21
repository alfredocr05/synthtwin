"""Check an unpacked synthtwin bundle before anything is installed from it.

Plan P4-D416 (lane DEP-2 of the December plan; the owner's D3 of
2026-10-20: the offline bundle is the only way synthtwin is installed).
`scripts/install.sh` and `scripts\\install.bat` run this file with the
Python they found, before they change anything on the computer:

    python -I scripts/check_bundle.py BUNDLE_FOLDER

It uses the standard library alone, opens no network connection and
writes nothing. It exits 0 when the bundle may be installed from, and 1
with a message in plain words when it may not. It refuses:

* a bundle with no `SHA256SUMS`, a line of it that is not a SHA-256 and
  a relative path inside the bundle, a file it lists that is missing or
  whose bytes do not match, and a file of the `wheelhouse` folder it
  does not list (every file the install reads is checked by its hash);
* a lock (`requirements-install.lock`) that names a place to fetch from
  (an index, a find-links, a URL, a path or an editable), a requirement
  with no `--hash`, or a library wheel whose SHA-256 the lock does not
  pin: pip then has nowhere to go but the bundle's own files, and each
  of them is the one the lock names;
* a `wheelhouse` without exactly one synthtwin wheel;
* a Python older than 3.11, and a bundle made for another system or
  for other Pythons than the one found (the message names the ones it
  was made for).
"""

import hashlib
import os
import re
import sys

FLOOR = (3, 11)

# The files every bundle lists in SHA256SUMS besides its wheels: the lock
# pip installs from and the three scripts that read it.
REQUIRED = (
    "requirements-install.lock",
    "scripts/install.sh",
    "scripts/install.bat",
    "scripts/check_bundle.py",
)

_SUM_LINE = re.compile(r"([0-9a-f]{64})  ([^\r\n]+)")
_PINNED = re.compile(r"--hash=sha256:([0-9a-f]{64})")
_REQUIREMENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*==[^\s;\\]+")
# Lock options that add a place to fetch from, or install something that
# is not a pinned release of the index's own files.
_FETCHING = (
    "--index-url",
    "-i ",
    "--extra-index-url",
    "--find-links",
    "-f ",
    "--trusted-host",
    "--editable",
    "-e ",
    "://",
    " @ ",
)


def _python_label(version):
    return str(version[0]) + "." + str(version[1])


def _wheel_tags(name):
    """The (python, abi, platform) tags of a wheel's file name, or None."""
    if not name.endswith(".whl"):
        return None
    pieces = name[: -len(".whl")].split("-")
    if len(pieces) not in (5, 6):
        return None
    return pieces[-3], pieces[-2], pieces[-1]


def _system_words(platform):
    if platform.startswith("win"):
        return "Windows"
    if platform.startswith("macosx"):
        return "macOS"
    if "linux" in platform:
        return "Linux"
    return platform


def _this_system():
    if sys.platform.startswith("win"):
        return "Windows"
    if sys.platform == "darwin":
        return "macOS"
    if sys.platform.startswith("linux"):
        return "Linux"
    return sys.platform


def _lock_problems(lock_text):
    """What in the lock could send pip anywhere but the bundle's files."""
    problems = []
    joined = re.sub(r"\\\r?\n", " ", lock_text)
    for raw in joined.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("--only-binary") or line.startswith("--require-hashes"):
            continue
        padded = " " + line + " "
        for word in _FETCHING:
            if word in padded:
                problems.append(
                    "the lock names a place to fetch from or a file outside the "
                    "bundle ('" + line[:60] + "'), so pip could reach past the bundle"
                )
                break
        else:
            if line.startswith("-"):
                problems.append(
                    "the lock carries an option this check does not know ('"
                    + line[:60]
                    + "')"
                )
                continue
            if not _REQUIREMENT.match(line):
                problems.append(
                    "the lock names a requirement that is not one exact version ('"
                    + line[:60]
                    + "')"
                )
                continue
            if not _PINNED.search(line):
                problems.append(
                    "the lock names " + line.split()[0] + " with no hash"
                )
    return problems


def check(folder, version=None, system=None):
    """Every reason the bundle in `folder` may not be installed from.

    `version` is the (major, minor) of the Python that will install, and
    `system` its system in words (Windows, macOS or Linux); both default
    to this Python's own.
    """
    version = tuple(version or sys.version_info[:2])
    system = system or _this_system()
    if version < FLOOR:
        return [
            "this computer's Python is " + _python_label(version) + ", and "
            "synthtwin needs Python 3.11 or later. Install the newest Python 3 "
            "from python.org (INSTALL.txt in this folder says how), open a new "
            "terminal window, and run the install script again."
        ]
    sums_path = os.path.join(folder, "SHA256SUMS")
    if not os.path.isfile(sums_path):
        return [
            "the file SHA256SUMS is missing from this folder, so the files in "
            "it cannot be checked. Download the synthtwin bundle again and "
            "unzip it whole, then run the install script again."
        ]
    with open(sums_path, "rb") as handle:
        sums_text = handle.read().decode("utf-8", "replace")
    listed = {}
    problems = []
    for number, raw in enumerate(sums_text.splitlines(), 1):
        if not raw.strip():
            continue
        found = _SUM_LINE.fullmatch(raw)
        relative = found.group(2) if found else ""
        parts = relative.replace("\\", "/").split("/")
        if (
            not found
            or relative.startswith(("/", "\\"))
            or ":" in relative
            or ".." in parts
            or relative in listed
        ):
            problems.append(
                "line " + str(number) + " of SHA256SUMS is not a SHA-256 and a "
                "file of this folder named once"
            )
            continue
        listed[relative.replace("\\", "/")] = found.group(1)
    for name in REQUIRED:
        if name not in listed:
            problems.append("SHA256SUMS gives no hash for " + name)
    for relative, digest in sorted(listed.items()):
        path = os.path.join(folder, *relative.split("/"))
        if not os.path.isfile(path):
            problems.append(relative + " is listed in SHA256SUMS but missing")
            continue
        hasher = hashlib.sha256()
        with open(path, "rb") as handle:
            for block in iter(lambda: handle.read(1 << 20), b""):
                hasher.update(block)
        if hasher.hexdigest() != digest:
            problems.append(
                relative + " does not match its hash in SHA256SUMS (it was "
                "changed or damaged after the bundle was made)"
            )
    house = os.path.join(folder, "wheelhouse")
    wheels = sorted(os.listdir(house)) if os.path.isdir(house) else []
    if not wheels:
        problems.append("the wheelhouse folder is missing or empty")
    for name in wheels:
        if "wheelhouse/" + name not in listed:
            problems.append(
                "wheelhouse/" + name + " has no hash in SHA256SUMS, so it "
                "cannot be checked"
            )
    lock_path = os.path.join(folder, "requirements-install.lock")
    pinned = set()
    if os.path.isfile(lock_path):
        with open(lock_path, "rb") as handle:
            lock_text = handle.read().decode("utf-8", "replace")
        problems += _lock_problems(lock_text)
        pinned = set(_PINNED.findall(lock_text))
    else:
        problems.append("requirements-install.lock is missing")
    ours = [name for name in wheels if name.startswith("synthtwin-") and name.endswith(".whl")]
    if len(ours) != 1:
        problems.append(
            "the wheelhouse must hold exactly one synthtwin wheel, and it "
            "holds " + str(len(ours))
        )
    for name in wheels:
        if name in ours:
            continue
        if not name.endswith(".whl"):
            problems.append("wheelhouse/" + name + " is not a wheel")
            continue
        digest = listed.get("wheelhouse/" + name)
        if digest is not None and digest not in pinned:
            problems.append(
                "wheelhouse/" + name + " is not a file the lock pins by its hash"
            )
    if problems:
        return [
            "the bundle in this folder did not pass its check: "
            + "; ".join(problems)
            + ". Download the synthtwin bundle again, unzip it whole into a "
            "new folder, and run the install script from there."
        ]
    pythons = set()
    systems = set()
    for name in wheels:
        tags = _wheel_tags(name)
        if tags is None:
            continue
        for tag in tags[0].split("."):
            if re.fullmatch(r"cp3\d+", tag):
                pythons.add((3, int(tag[3:])))
        for tag in tags[2].split("."):
            if tag != "any":
                systems.add(_system_words(tag))
    if systems and system not in systems:
        return [
            "this bundle is made for " + " and ".join(sorted(systems)) + ", and "
            "this computer runs " + system + ". Download the synthtwin bundle "
            "made for " + system + " and run its install script."
        ]
    if pythons and version not in pythons:
        served = ", ".join(_python_label(item) for item in sorted(pythons))
        return [
            "this bundle holds the libraries for Python " + served + ", and the "
            "Python found is " + _python_label(version) + ". Install one of "
            "those from python.org (INSTALL.txt in this folder says how), open "
            "a new terminal window, and run the install script again."
        ]
    return []


def main(argv=None):
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != 1:
        print("Give the bundle's folder: python -I scripts/check_bundle.py FOLDER")
        return 2
    found = check(arguments[0])
    if found:
        for problem in found:
            print("The installation stopped: " + problem)
        return 1
    print("The bundle's files match their hashes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
