"""Check an unpacked synthtwin bundle before anything is installed from it.

Plan P4-D416 (lane DEP-2 of the December plan; the owner's D3 of
2026-10-20: the offline bundle is the only way synthtwin is installed).
It is kept in the repository as tools/bundle/check_bundle.py and placed
in each bundle as scripts/check_bundle.py, where `scripts/install.sh`
and `scripts\\install.bat` run it with the Python they found, before
they change anything on the computer:

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
* a Python older than 3.11 or newer than 3.14, and a bundle made for
  another system, another kind of chip, a newer macOS or a newer Linux
  than this computer's, or for other Pythons than the one found (the
  message names, in plain words, what the bundle is for and what to do).
"""

import hashlib
import os
import platform
import re
import sys
import sysconfig

# The Pythons every bundle serves: CI's tests matrix, 3.11 to 3.14 (plan
# P4-D410). tests/test_bundle.py holds these two, the install scripts'
# own range and the matrix to each other. The advice names NEWEST: a
# person sent to python.org's newest Python would get one no bundle
# serves once 3.15 is out (lane DEP-2's skeptic, item 2).
FLOOR = (3, 11)
NEWEST = (3, 14)

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


def _dotted(version):
    return str(version[0]) + "." + str(version[1])


def _in_words(versions):
    labels = [_dotted(item) for item in sorted(versions)]
    if len(labels) < 2:
        return "".join(labels)
    return ", ".join(labels[:-1]) + " and " + labels[-1]


def _served_range():
    return [(3, minor) for minor in range(FLOOR[1], NEWEST[1] + 1)]


def _python_advice():
    label = _dotted(NEWEST)
    return (
        "Install Python " + label + " from python.org (choose Downloads, then "
        "the newest Python " + label + " release; INSTALL.txt in this folder "
        "says how), open a new terminal window, and run the install script again."
    )


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


def _machine_word(raw):
    """A chip's name as wheels and Pythons spell it, in one word: arm, x86_64 or x86."""
    lowered = raw.lower()
    if lowered in ("arm64", "aarch64", "arm64e", "armv8l"):
        return "arm"
    if lowered in ("x86_64", "amd64", "x64", "em64t"):
        return "x86_64"
    if lowered in ("i386", "i486", "i586", "i686", "x86", "win32"):
        return "x86"
    return lowered


def _release(text):
    """(major, minor) of a release written 14.5.1, or None when it is not one."""
    found = re.match(r"(\d+)\.(\d+)", text or "")
    return (int(found.group(1)), int(found.group(2))) if found else None


def _this_computer():
    """This computer as a bundle's wheels ask about it.

    The chip is the one this Python runs on: an Intel Python on a Mac
    with an Apple chip runs as on an Intel Mac, and pip installs for it
    as for one. On Windows sysconfig names the Python's own build
    (win32, win-amd64, win-arm64), which a 32-bit Python on a 64-bit
    computer would otherwise hide.
    """
    system = _this_system()
    if system == "Windows":
        machine = _machine_word(sysconfig.get_platform().split("-")[-1])
    else:
        machine = _machine_word(platform.machine())
    macos = None
    glibc = None
    if system == "macOS":
        macos = _release(platform.mac_ver()[0])
    elif system == "Linux":
        name, number = platform.libc_ver()
        if name == "glibc":
            glibc = _release(number)
    return {"system": system, "machine": machine, "macos": macos, "glibc": glibc}


_MAC_MACHINES = {
    "arm64": ("arm",),
    "x86_64": ("x86_64",),
    "universal2": ("arm", "x86_64"),
    "intel": ("x86_64", "x86"),
    "universal": ("x86_64", "x86"),
    "i386": ("x86",),
}
_OLD_MANYLINUX = {"manylinux1": (2, 5), "manylinux2010": (2, 12), "manylinux2014": (2, 17)}


def _needs(tag):
    """What one platform tag asks of a computer: (system, chips, release).

    `chips` is empty when the tag names none this check knows, and
    `release` is the oldest macOS (macosx_12_0) or glibc (manylinux_2_28)
    the tag allows, or None.
    """
    found = re.fullmatch(r"macosx_(\d+)_(\d+)_([a-z0-9_]+)", tag)
    if found:
        chips = _MAC_MACHINES.get(found.group(3), (found.group(3),))
        return "macOS", frozenset(chips), (int(found.group(1)), int(found.group(2)))
    found = re.fullmatch(r"manylinux_(\d+)_(\d+)_([a-z0-9_]+)", tag)
    if found:
        return (
            "Linux",
            frozenset({_machine_word(found.group(3))}),
            (int(found.group(1)), int(found.group(2))),
        )
    found = re.fullmatch(r"(manylinux1|manylinux2010|manylinux2014)_([a-z0-9_]+)", tag)
    if found:
        return "Linux", frozenset({_machine_word(found.group(2))}), _OLD_MANYLINUX[found.group(1)]
    found = re.fullmatch(r"(?:musllinux_\d+_\d+|linux)_([a-z0-9_]+)", tag)
    if found:
        return "Linux", frozenset({_machine_word(found.group(1))}), None
    if tag == "win32":
        return "Windows", frozenset({"x86"}), None
    if tag.startswith("win_"):
        return "Windows", frozenset({_machine_word(tag[len("win_") :])}), None
    return _system_words(tag), frozenset(), None


def _misfit(needs, computer):
    """Why a computer cannot take a wheel of this tag: 'chip', 'release' or None."""
    _, chips, release = needs
    machine = computer.get("machine")
    if chips and machine is not None and machine not in chips:
        return "chip"
    have = computer.get("macos") if needs[0] == "macOS" else computer.get("glibc")
    if release is not None and have is not None and tuple(have) < release:
        return "release"
    return None


def _mac_words(release):
    """macOS 12 for (12, 0), as Apple names it; 10.9 for (10, 9)."""
    return str(release[0]) if release[1] == 0 else _dotted(release)


def _chip_words(chips, system):
    words = []
    for chip in sorted(chips):
        if chip == "arm":
            words += ["an Apple chip (M1 or later)" if system == "macOS" else "an Arm processor"]
        elif chip == "x86_64":
            words += ["an Intel chip" if system == "macOS" else "a 64-bit Intel or AMD processor"]
        elif chip == "x86":
            words += ["a 32-bit Intel or AMD processor"]
        else:
            words += ["a " + chip + " processor"]
    return " or ".join(words)


def _platform_problem(wheels, computer):
    """The plain-words refusal of a bundle whose wheels this computer cannot take, or None.

    A wheel fits when any of its platform tags fits; the message says
    what the whole bundle is for -- its chips, and the newest macOS or
    glibc any of its wheels needs -- what this computer is, and what to
    do (lane DEP-2's skeptic, item 3: a bundle of macOS 14 wheels passed
    the check on a Mac running macOS 12, and pip then stopped with
    nothing the person could act on).
    """
    system = computer.get("system")
    chips = None
    release = None
    reasons = []
    for name in wheels:
        tags = _wheel_tags(name)
        if tags is None:
            continue
        needs = [_needs(tag) for tag in tags[2].split(".") if tag != "any"]
        needs = [item for item in needs if item[0] == system]
        if not needs:
            continue
        offered = frozenset().union(*(item[1] for item in needs))
        if offered:
            chips = offered if chips is None else chips & offered
        lowest = [item[2] for item in needs if item[2] is not None]
        if lowest:
            least = min(lowest)
            release = least if release is None or least > release else release
        misfits = [_misfit(item, computer) for item in needs]
        if all(misfits):
            reasons += [misfits[0]]
    if not reasons:
        return None
    if system == "macOS":
        kind = "Macs"
        what = "this Mac"
    else:
        kind = system + " computers"
        what = "this computer"
    made_for = "this bundle is made for " + kind
    if chips:
        made_for += " with " + _chip_words(chips, system)
    if release is not None and system == "macOS":
        made_for += " on macOS " + _mac_words(release) + " or later"
    elif release is not None:
        made_for += " whose system library, glibc, is version " + _dotted(release) + " or later"
    if "chip" in reasons:
        machine = str(computer.get("machine"))
        said = made_for + ", and " + what + "'s Python runs on " + _chip_words({machine}, system) + ". "
        if system == "macOS" and machine == "x86_64" and chips and "arm" in chips:
            return said + (
                "If this Mac has an Apple chip, the Python found is one made for "
                "Intel Macs. " + _python_advice() + " On a Mac with an Intel "
                "chip this bundle cannot be installed: send this message to whoever "
                "looks after synthtwin."
            )
        if system == "Windows" and machine == "arm" and chips and "x86_64" in chips:
            return said + (
                "Windows 11 runs the 64-bit Python for Intel and AMD processors on "
                "an Arm processor too: install Python " + _dotted(NEWEST) + " from "
                "python.org choosing its \"Windows installer (64-bit)\", not the "
                "ARM64 one, open a new Command Prompt window, and run the install "
                "script again."
            )
        return said + (
            "There is no synthtwin bundle for this computer's processor yet: send "
            "this message to whoever looks after synthtwin."
        )
    have = computer.get("macos") if system == "macOS" else computer.get("glibc")
    if system == "macOS":
        return made_for + ", and this Mac runs macOS " + _dotted(have) + ". " + (
            "Update macOS to " + _mac_words(release) + " or later (Apple menu, "
            "then System Settings, General, Software Update), then run the install "
            "script again; if this Mac cannot take it, send this message to whoever "
            "looks after synthtwin."
        )
    return made_for + ", and this computer's is " + _dotted(have) + ". " + (
        "Ask whoever looks after this computer for a newer Linux, or send this "
        "message to whoever looks after synthtwin."
    )


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


def check(folder, version=None, system=None, computer=None):
    """Every reason the bundle in `folder` may not be installed from.

    `version` is the (major, minor) of the Python that will install;
    `computer` holds its `system` in words (Windows, macOS or Linux), its
    `machine` (arm, x86_64 or x86), its `macos` and its `glibc` release,
    each None where it is not known (and then not judged); `system`
    alone may be given in its place. All default to this computer's own.
    """
    version = tuple(version or sys.version_info[:2])
    if computer is None and system is None:
        computer = _this_computer()
    computer = dict(computer or {})
    computer["system"] = system or computer.get("system") or _this_system()
    system = computer["system"]
    if not FLOOR <= version <= NEWEST:
        return [
            "this computer's Python is " + _dotted(version) + ", and this "
            "synthtwin bundle serves Python " + _in_words(_served_range()) + ". "
            + _python_advice()
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
        # A wheel built for one CPython carries its version in the ABI
        # tag (cp311); a wheel for any Python 3 (py3, none, abi3) says
        # nothing about which Pythons the bundle serves.
        for tag in tags[1].split("."):
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
    unfit = _platform_problem(wheels, computer)
    if unfit is not None:
        return [unfit]
    if pythons and version not in pythons:
        return [
            "this bundle holds the libraries for Python " + _in_words(pythons)
            + ", and the Python found is " + _dotted(version) + ". Install "
            "Python " + _dotted(max(pythons)) + " from python.org (choose "
            "Downloads, then the newest Python " + _dotted(max(pythons))
            + " release; INSTALL.txt in this folder says how), open a new terminal "
            "window, and run the install script again."
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
