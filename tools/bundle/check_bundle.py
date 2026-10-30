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
* a lock (`requirements-install.lock`) holding anything but its two
  directives, written exactly (`--only-binary :all:` and
  `--require-hashes`), and requirements of one exact version, a
  condition this check can read and `--hash` options alone -- so no
  index, find-links, URL, path or editable can ride on any line -- or a
  library wheel whose SHA-256 the lock does not pin: pip then has
  nowhere to go but the bundle's own files, and each of them is the one
  the lock names;
* a `wheelhouse` without exactly one synthtwin wheel, or without a wheel
  this computer and its Python can take for every requirement the lock
  makes for them (so a bundle missing a file stops here, before an
  earlier environment is replaced, and not in pip afterwards);
* a Python older than 3.11 or newer than 3.14, a Python that is not
  CPython or is CPython's free-threaded build where the bundle's
  libraries are made for the usual one, and a bundle made for another
  system, another kind of chip, a newer macOS, a newer Linux or a Linux
  without glibc than this computer's, or for other Pythons than the one
  found (the message names, in plain words, what the bundle is for and
  what to do);
* a file it cannot read (a folder this computer will not let it read):
  the message names the file and what to do, never a traceback.
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
# One requirement as the lock writes it, whole: a name, one exact
# version, a condition after `;` and nothing but `--hash` options after.
_REQUIREMENT_LINE = re.compile(
    r"([A-Za-z0-9][A-Za-z0-9._-]*)==([A-Za-z0-9.+!_-]+)"
    r"(?:\s*;\s*(.+?))?((?:\s+--hash=sha256:[0-9a-f]{64})+)"
)
# The two directives a lock may carry, each written exactly: anything
# else on their line (Codex's review of lane DEP-2, item 1:
# `--only-binary=:all: --find-links https://...` passed when a line
# beginning with a directive was skipped whole) is read as an option.
_DIRECTIVE = re.compile(r"--only-binary(?: +|=):all:|--require-hashes")
# The conditions the lock writes after `;` (uv's markers): a name, a
# comparison and a quoted value, joined by `and` and `or`.
_MARKER_TERM = re.compile(
    r"\s*(python_full_version|python_version|sys_platform|os_name|platform_machine"
    r"|platform_system|implementation_name|platform_python_implementation)"
    r"\s*(==|!=|<=|>=|<|>)\s*'([^']*)'\s*"
)
_VERSIONED = ("python_full_version", "python_version")
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
    libc = None
    if system == "macOS":
        macos = _release(platform.mac_ver()[0])
    elif system == "Linux":
        # glibc answers by its own name (os.confstr); a Linux whose
        # system library is musl, as Alpine's is, gives none, and the
        # bundle's manylinux wheels do not run there (Codex's review of
        # lane DEP-2, item 4).
        name, number = platform.libc_ver()
        libc = "glibc" if name == "glibc" else "other"
        if name == "glibc":
            glibc = _release(number)
    return {"system": system, "machine": machine, "macos": macos, "glibc": glibc, "libc": libc}


def _this_python():
    """The Python running this check as wheels ask about it: its kind and its ABI tag.

    CPython's free-threaded build takes wheels tagged cp314t, not the
    usual build's cp314 (Codex's review of lane DEP-2, item 3).
    """
    free = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))
    return {
        "implementation": sys.implementation.name,
        "abi": "cp3" + str(sys.version_info[1]) + ("t" if free else ""),
    }


def _environment(version, computer, real):
    """The values the lock's conditions read, for this Python and computer."""
    system = computer.get("system")
    if real:
        return {
            "python_full_version": platform.python_version(),
            "python_version": _dotted(version),
            "sys_platform": sys.platform,
            "os_name": os.name,
            "platform_machine": platform.machine(),
            "platform_system": platform.system(),
            "implementation_name": sys.implementation.name,
            "platform_python_implementation": platform.python_implementation(),
        }
    machine = computer.get("machine")
    spelled = {
        ("arm", "macOS"): "arm64",
        ("arm", "Linux"): "aarch64",
        ("arm", "Windows"): "ARM64",
        ("x86_64", "Windows"): "AMD64",
        ("x86", "Windows"): "x86",
        ("x86", "Linux"): "i686",
    }.get((machine, system), machine or "")
    return {
        "python_full_version": _dotted(version) + ".0",
        "python_version": _dotted(version),
        "sys_platform": {"macOS": "darwin", "Windows": "win32", "Linux": "linux"}.get(system, str(system).lower()),
        "os_name": "nt" if system == "Windows" else "posix",
        "platform_machine": spelled,
        "platform_system": {"macOS": "Darwin"}.get(system, str(system)),
        "implementation_name": "cpython",
        "platform_python_implementation": "CPython",
    }


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
    """What one platform tag asks of a computer: (system, chips, release, libc).

    `chips` is empty when the tag names none this check knows,
    `release` is the oldest macOS (macosx_12_0) or glibc (manylinux_2_28)
    the tag allows, or None, and `libc` the system library a Linux tag
    asks for (glibc for manylinux, musl for musllinux), or None.
    """
    found = re.fullmatch(r"macosx_(\d+)_(\d+)_([a-z0-9_]+)", tag)
    if found:
        chips = _MAC_MACHINES.get(found.group(3), (found.group(3),))
        return "macOS", frozenset(chips), (int(found.group(1)), int(found.group(2))), None
    found = re.fullmatch(r"manylinux_(\d+)_(\d+)_([a-z0-9_]+)", tag)
    if found:
        return (
            "Linux",
            frozenset({_machine_word(found.group(3))}),
            (int(found.group(1)), int(found.group(2))),
            "glibc",
        )
    found = re.fullmatch(r"(manylinux1|manylinux2010|manylinux2014)_([a-z0-9_]+)", tag)
    if found:
        return "Linux", frozenset({_machine_word(found.group(2))}), _OLD_MANYLINUX[found.group(1)], "glibc"
    found = re.fullmatch(r"musllinux_\d+_\d+_([a-z0-9_]+)", tag)
    if found:
        return "Linux", frozenset({_machine_word(found.group(1))}), None, "musl"
    found = re.fullmatch(r"linux_([a-z0-9_]+)", tag)
    if found:
        return "Linux", frozenset({_machine_word(found.group(1))}), None, None
    if tag == "win32":
        return "Windows", frozenset({"x86"}), None, None
    if tag.startswith("win_"):
        return "Windows", frozenset({_machine_word(tag[len("win_") :])}), None, None
    return _system_words(tag), frozenset(), None, None


def _misfit(needs, computer):
    """Why a computer cannot take a wheel of this tag: 'chip', 'libc', 'release' or None."""
    _, chips, release, libc = needs
    machine = computer.get("machine")
    if chips and machine is not None and machine not in chips:
        return "chip"
    have_libc = computer.get("libc")
    if have_libc is None and computer.get("glibc") is not None:
        have_libc = "glibc"
    if libc == "glibc" and have_libc not in (None, "glibc"):
        return "libc"
    if libc == "musl" and have_libc == "glibc":
        return "libc"
    have = computer.get("macos") if needs[0] == "macOS" else computer.get("glibc")
    if release is not None and have is not None and tuple(have) < release:
        return "release"
    return None


def _python_fits(python_tag, abi_tag, version, abi):
    """Whether a Python of `version` and ABI tag `abi` (cp313, cp314t) takes this pair of a wheel's tags."""
    minor = version[1]
    if abi_tag == abi:
        return python_tag == "cp3" + str(minor)
    numbered = re.fullmatch(r"(cp|py)3(\d*)", python_tag)
    if numbered is None:
        return False
    below = numbered.group(2) == "" or int(numbered.group(2)) <= minor
    if abi_tag == "abi3":
        return numbered.group(1) == "cp" and numbered.group(2) != "" and below and not abi.endswith("t")
    if abi_tag == "none":
        if numbered.group(1) == "cp":
            return numbered.group(2) == str(minor)
        return below
    return False


def _wheel_fits(name, version, abi, computer):
    """Whether this computer and its Python take the wheel named `name`."""
    tags = _wheel_tags(name)
    if tags is None:
        return False
    if not any(
        _python_fits(python_tag, abi_tag, version, abi)
        for python_tag in tags[0].split(".")
        for abi_tag in tags[1].split(".")
    ):
        return False
    for tag in tags[2].split("."):
        if tag == "any":
            return True
        needs = _needs(tag)
        if needs[0] == computer.get("system") and _misfit(needs, computer) is None:
            return True
    return False


def _project(name):
    """A project's name as pip compares it: python_dateutil and python-dateutil alike."""
    return re.sub(r"[-_.]+", "-", name).lower()


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
    if "libc" in reasons and "chip" not in reasons:
        return made_for + ", and this computer's system library is not glibc (as on Alpine Linux). " + (
            "There is no synthtwin bundle for it yet: install synthtwin on a Linux "
            "whose system library is glibc, such as Ubuntu, Debian, Fedora or Red Hat, "
            "or send this message to whoever looks after synthtwin."
        )
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


def _marker(text):
    """A condition after `;` as or-groups of and-terms, or None when it is not one."""
    groups = []
    for part in re.split(r"\s+or\s+", text.strip()):
        terms = []
        for piece in re.split(r"\s+and\s+", part):
            found = _MARKER_TERM.fullmatch(piece)
            if found is None:
                return None
            if found.group(1) not in _VERSIONED and found.group(2) not in ("==", "!="):
                return None
            if found.group(1) in _VERSIONED and _version_of(found.group(3)) is None:
                return None
            terms += [found.groups()]
        groups += [terms]
    return groups


def _version_of(text):
    return tuple(int(part) for part in text.split(".")) if re.fullmatch(r"\d+(\.\d+)*", text) else None


def _holds(groups, environment):
    """Whether a condition read by `_marker` holds for `environment`."""
    for terms in groups:
        met = True
        for name, operator, value in terms:
            have = environment.get(name, "")
            if name in _VERSIONED:
                left = _version_of(have) or (0,)
                right = _version_of(value) or (0,)
                width = max(len(left), len(right))
                left = left + (0,) * (width - len(left))
                right = right + (0,) * (width - len(right))
            else:
                left, right = have, value
            if not {
                "==": left == right,
                "!=": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }[operator]:
                met = False
                break
        if met:
            return True
    return False


_COMMENT = re.compile(r"(^|\s+)#.*$")


def _lock_lines(lock_text):
    """The lock's lines with continuations joined and comments dropped, as pip reads it.

    pip splits the text into lines first. A line ending in a backslash
    continues onto the next, its backslashes stripped, unless it is a
    comment line: a comment line never continues, so the line after it
    is read on its own (a fetching line behind '# ... \\' is seen).
    Comments are dropped from each joined line afterwards.
    """
    joined = []
    pending = None
    for raw in lock_text.splitlines():
        if raw.endswith("\\") and not _COMMENT.match(raw):
            pending = (pending or "") + raw.strip("\\")
            continue
        if _COMMENT.match(raw):
            raw = " " + raw
        joined += [raw if pending is None else pending + raw]
        pending = None
    if pending is not None:
        joined += [pending]
    lines = []
    for raw in joined:
        line = _COMMENT.sub("", raw).strip()
        if line:
            lines += [line]
    return lines


def _requirements(lock_text):
    """(name, condition or None, set of pinned SHA-256s) of each requirement line of the lock."""
    found = []
    for line in _lock_lines(lock_text):
        whole = _REQUIREMENT_LINE.fullmatch(line)
        if whole is None:
            continue
        condition = _marker(whole.group(3)) if whole.group(3) else None
        found += [(whole.group(1), condition, set(_PINNED.findall(whole.group(4))))]
    return found


def _lock_problems(lock_text):
    """What in the lock could send pip anywhere but the bundle's files."""
    problems = []
    for line in _lock_lines(lock_text):
        padded = " " + line + " "
        if any(word in padded for word in _FETCHING):
            problems.append(
                "the lock names a place to fetch from or a file outside the "
                "bundle ('" + line[:60] + "'), so pip could reach past the bundle"
            )
            continue
        if _DIRECTIVE.fullmatch(line):
            continue
        if line.startswith("-"):
            problems.append(
                "the lock carries an option this check does not know ('"
                + line[:60]
                + "')"
            )
            continue
        whole = _REQUIREMENT_LINE.fullmatch(line)
        if whole is None:
            if not _REQUIREMENT.match(line):
                problems.append(
                    "the lock names a requirement that is not one exact version ('"
                    + line[:60]
                    + "')"
                )
            elif not _PINNED.search(line):
                problems.append("the lock names " + line.split()[0] + " with no hash")
            else:
                problems.append(
                    "the lock carries something beside a requirement's hashes ('"
                    + line[:60]
                    + "')"
                )
            continue
        if whole.group(3) and _marker(whole.group(3)) is None:
            problems.append(
                "the lock names a condition this check cannot read ('" + line[:60] + "')"
            )
    return problems


class _Unreadable(Exception):
    """A file of the bundle this computer would not let the check read."""

    def __init__(self, relative, error):
        super().__init__(relative)
        self.relative = relative
        self.reason = getattr(error, "strerror", None) or type(error).__name__


def _read(folder, relative):
    try:
        with open(os.path.join(folder, *relative.split("/")), "rb") as handle:
            return handle.read()
    except OSError as error:
        raise _Unreadable(relative, error) from None


def _digest(folder, relative):
    hasher = hashlib.sha256()
    try:
        with open(os.path.join(folder, *relative.split("/")), "rb") as handle:
            for block in iter(lambda: handle.read(1 << 20), b""):
                hasher.update(block)
    except OSError as error:
        raise _Unreadable(relative, error) from None
    return hasher.hexdigest()


def check(folder, version=None, system=None, computer=None, python=None):
    """Every reason the bundle in `folder` may not be installed from.

    `version` is the (major, minor) of the Python that will install and
    `python` its `implementation` (cpython) and its ABI tag (cp313, or
    cp313t for the free-threaded build); `computer` holds its `system` in
    words (Windows, macOS or Linux), its `machine` (arm, x86_64 or x86),
    its `macos` and its `glibc` release and its `libc` (glibc or other),
    each None where it is not known (and then not judged); `system`
    alone may be given in its place. All default to this computer's own
    (and `python`, when `version` is given, to the usual CPython of it).
    """
    real = version is None and computer is None and system is None
    if python is None:
        python = _this_python() if version is None else {
            "implementation": "cpython",
            "abi": "cp3" + str(tuple(version)[1]),
        }
    version = tuple(version or sys.version_info[:2])
    if computer is None and system is None:
        computer = _this_computer()
    computer = dict(computer or {})
    computer["system"] = system or computer.get("system") or _this_system()
    try:
        return _check(folder, version, computer, python, real)
    except _Unreadable as unreadable:
        # Codex's review of lane DEP-2, item 6: a folder an institution's
        # settings keep from being read gave a traceback, and the script
        # then said to follow it.
        return [
            "this computer would not let synthtwin read " + unreadable.relative
            + " in this folder (" + unreadable.reason + "), so the bundle cannot "
            "be checked. Copy the bundle's zip file into a folder of your own, such "
            "as one in Documents, unzip it there, and run the install script from "
            "the new folder; if it stops here again, send this message to whoever "
            "looks after this computer."
        ]


def _check(folder, version, computer, python, real):
    system = computer["system"]
    if not FLOOR <= version <= NEWEST:
        return [
            "this computer's Python is " + _dotted(version) + ", and this "
            "synthtwin bundle serves Python " + _in_words(_served_range()) + ". "
            + _python_advice()
        ]
    if python.get("implementation") != "cpython":
        return [
            "the Python found is " + str(python.get("implementation")) + " " + _dotted(version)
            + ", and this synthtwin bundle serves the usual Python, CPython, from "
            "python.org. " + _python_advice()
        ]
    sums_path = os.path.join(folder, "SHA256SUMS")
    if not os.path.isfile(sums_path):
        return [
            "the file SHA256SUMS is missing from this folder, so the files in "
            "it cannot be checked. Download the synthtwin bundle again and "
            "unzip it whole, then run the install script again."
        ]
    sums_text = _read(folder, "SHA256SUMS").decode("utf-8", "replace")
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
        if _digest(folder, relative) != digest:
            problems.append(
                relative + " does not match its hash in SHA256SUMS (it was "
                "changed or damaged after the bundle was made)"
            )
    house = os.path.join(folder, "wheelhouse")
    try:
        wheels = sorted(os.listdir(house)) if os.path.isdir(house) else []
    except OSError as error:
        raise _Unreadable("wheelhouse", error) from None
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
    lock_text = ""
    if os.path.isfile(lock_path):
        lock_text = _read(folder, "requirements-install.lock").decode("utf-8", "replace")
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
    abis = set()
    systems = set()
    for name in wheels:
        tags = _wheel_tags(name)
        if tags is None:
            continue
        # A wheel built for one CPython carries its version in the ABI
        # tag (cp311, cp314t for the free-threaded build); a wheel for
        # any Python 3 (py3, none, abi3) says nothing about which
        # Pythons the bundle serves.
        for tag in tags[1].split("."):
            found = re.fullmatch(r"cp3(\d+)t?", tag)
            if found:
                pythons.add((3, int(found.group(1))))
                abis.add(tag)
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
    abi = str(python.get("abi"))
    if abis and abi not in abis and abi.endswith("t"):
        return [
            "the Python found is the free-threaded build of Python " + _dotted(version)
            + ", and this bundle's libraries are made for its usual build. Run the "
            "install script with the usual Python " + _dotted(version) + " (python"
            + _dotted(version) + ", not python" + _dotted(version) + "t), or install "
            "it from python.org without the free-threaded option, open a new "
            "terminal window, and run the install script again."
        ]
    # Every requirement the lock makes of this computer and its Python
    # has a wheel here it can take (Codex's review of lane DEP-2, item 5:
    # a bundle missing one stopped in pip only after the environment it
    # replaced was gone).
    environment = _environment(version, computer, real)
    missing = []
    for project, condition, hashes in _requirements(lock_text):
        if condition is not None and not _holds(condition, environment):
            continue
        if not any(
            _project(name.split("-")[0]) == _project(project)
            and listed.get("wheelhouse/" + name) in hashes
            and _wheel_fits(name, version, abi, computer)
            for name in wheels
        ):
            missing += [project]
    if missing:
        return [
            "the bundle in this folder has no file of " + _in_names(missing)
            + " that this computer and its Python " + _dotted(version) + " can "
            "take, so it is not whole. Download the synthtwin bundle made for this "
            "computer again, unzip it whole into a new folder, and run the install "
            "script from there; if it stops here again, send this message to whoever "
            "looks after synthtwin."
        ]
    return []


def _in_names(names):
    if len(names) < 2:
        return "".join(names)
    return ", ".join(names[:-1]) + " and " + names[-1]


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
