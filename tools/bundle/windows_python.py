#!/usr/bin/env python3
"""The Python the ready folder carries: its pin, its addresses and its checks.

Plan P4-D483 (lane WIN of the December plan). The ready folder for
Windows carries python.org's embeddable Python 3.14, and the backup
carries python.org's 3.14 installer. This file names the version, the
two addresses and the SHA-256 of each file, and judges what the
workflow's build job found. It never opens the network: the workflow
step downloads, this file checks.

THE PIN. ``PINNED`` holds the version and the two SHA-256s once they are
committed (the orchestrator's RULING W8). Until then the build TRUSTS ON
FIRST USE: it takes the 3.14 release of the runner's own Python, checks
the Authenticode signature of every program file, prints both SHA-256s,
and the workflow names its artifacts `-unpinned`: not for the trial
until a repair commits the pin printed by that run.

THE SIGNERS. Every .exe, .dll and .pyd of the embeddable zip, and the
installer, must carry a Valid Authenticode signature whose subject's
common name is one of ``SIGNERS``, held by that signer's own organisation
(``ORGANISATIONS``): python.org signs its own files, and the Visual C++
runtime DLLs it ships are signed by Microsoft. A Microsoft signer stands
on those runtime files alone (``RUNTIME``).

    python tools/bundle/windows_python.py version
    python tools/bundle/windows_python.py urls VERSION
    python tools/bundle/windows_python.py check EMBEDDABLE_ZIP INSTALLER VERSION
    python tools/bundle/windows_python.py signatures SIGNATURES_JSON VERSION
"""

import hashlib
import json
import pathlib
import re
import sys
import zipfile

MINOR = (3, 14)
# The committed pin: {"version": "3.14.N", "embeddable": SHA-256,
# "installer": SHA-256}, or None while the build trusts on first use.
PINNED: "dict[str, str] | None" = None
SIGNERS = (
    "Python Software Foundation",
    "Microsoft Corporation",
    # the C runtime files python.org ships (vcruntime140.dll, vcruntime140_1.dll) carry this Microsoft signer
    "Microsoft Windows Software Compatibility Publisher",
    # ...and this one, for the same bytes, on a later runner image: push 29's build read the embeddable of 3.14.10
    # with the very SHA-256 push 27's had, and Windows named its own catalog's signer for those two files
    "Microsoft Windows",
)
# Each signer's certificate is held by its own organisation (the subject's O=).
ORGANISATIONS = {
    "Python Software Foundation": "Python Software Foundation",
    "Microsoft Corporation": "Microsoft Corporation",
    "Microsoft Windows Software Compatibility Publisher": "Microsoft Corporation",
    "Microsoft Windows": "Microsoft Corporation",
}
# The only files a Microsoft signer stands on: the C runtime python.org ships beside its own.
RUNTIME = ("vcruntime140.dll", "vcruntime140_1.dll")
_BASE = "https://www.python.org/ftp/python/{version}/"
EMBEDDABLE = "python-{version}-embed-amd64.zip"
INSTALLER = "python-{version}-amd64.exe"
_VERSION = re.compile(r"3\.14\.(0|[1-9][0-9]*)")


def version(running: "tuple[int, int, int] | None" = None) -> "tuple[str, bool]":
    """(the 3.14 release to use, whether it is pinned).

    The pinned release where there is one; otherwise the release of the
    Python running this file, which must be a 3.14.
    """
    if PINNED is not None:
        return PINNED["version"], True
    major, minor, micro = running or tuple(sys.version_info[:3])  # type: ignore[misc]
    if (major, minor) != MINOR:
        raise ValueError(
            f"run this with Python {MINOR[0]}.{MINOR[1]}: with nothing pinned the folder "
            f"takes the release of the Python that builds it, and this is {major}.{minor}"
        )
    return f"{major}.{minor}.{micro}", False


def urls(release: str) -> "tuple[str, str]":
    """The two python.org addresses of a 3.14 release: the embeddable zip, then the installer."""
    if not _VERSION.fullmatch(release):
        raise ValueError(f"{release!r} is not a Python 3.14 release")
    base = _BASE.format(version=release)
    return base + EMBEDDABLE.format(version=release), base + INSTALLER.format(version=release)


def sha256_of(path: pathlib.Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(block)
    return hasher.hexdigest()


def embeddable_problems(path: pathlib.Path, release: str) -> "list[str]":
    """What makes this file something other than python.org's embeddable Python of ``release``."""
    tag = f"{MINOR[0]}{MINOR[1]}"
    needed = {"python.exe", f"python{tag}.dll", f"python{tag}.zip", f"python{tag}._pth", "LICENSE.txt"}
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
    except (OSError, zipfile.BadZipFile) as error:
        return [f"{path.name} is not a readable zip ({error})"]
    problems = [f"{path.name} lacks {name}" for name in sorted(needed - set(names))]
    for name in names:
        if name.startswith(("/", "\\")) or ".." in name.replace("\\", "/").split("/") or ":" in name:
            problems.append(f"{path.name} holds a member outside its folder: {name!r}")
    if not path.name == EMBEDDABLE.format(version=release):
        problems.append(f"{path.name} is not named {EMBEDDABLE.format(version=release)}")
    return problems


def check(embeddable: pathlib.Path, installer: pathlib.Path, release: str) -> "tuple[list[str], list[str]]":
    """(problems, lines to print) for the two downloads of ``release``."""
    problems = embeddable_problems(embeddable, release)
    lines = []
    digests = {"embeddable": sha256_of(embeddable), "installer": sha256_of(installer)}
    if installer.name != INSTALLER.format(version=release):
        problems.append(f"{installer.name} is not named {INSTALLER.format(version=release)}")
    for kind, digest in digests.items():
        lines.append(f"{digest}  {kind} ({release})")
        if PINNED is None:
            continue
        if PINNED["version"] != release:
            problems.append(f"the pin is Python {PINNED['version']}, and this is {release}")
        elif PINNED[kind] != digest:
            problems.append(f"the {kind} has SHA-256 {digest}, and the pin says {PINNED[kind]}")
    if PINNED is None:
        lines.append(
            "UNPINNED: trusted on first use after the signature check; the artifacts "
            "are named -unpinned and are not for the trial until the pin is committed"
        )
    return problems, lines


def signature_problems(records: "list[dict[str, object]]", expected: "list[str]") -> "list[str]":
    """What in Get-AuthenticodeSignature's records is not a Valid signature of an allowed signer.

    ``records`` holds Path, Status and Signer (the certificate's subject)
    for each file; ``expected`` names files that must be among them.
    """
    problems = []
    seen = set()
    for record in records:
        path = str(record.get("Path", ""))
        seen.add(pathlib.PureWindowsPath(path).name.lower())
        status = str(record.get("Status", ""))
        subject = str(record.get("Signer", "") or "")
        name = _subject_part(subject, "CN")
        held_by = _subject_part(subject, "O")
        if status != "Valid":
            problems.append(f"{path}: the signature is {status or 'missing'}, not Valid")
        elif name not in SIGNERS:
            problems.append(f"{path}: signed by {name or subject!r}, not by {' or '.join(SIGNERS)}")
        elif held_by != ORGANISATIONS[name]:
            problems.append(f"{path}: signed by {name!r} for {held_by or 'no organisation'!r}, not for {ORGANISATIONS[name]}")
        elif ORGANISATIONS[name] != "Python Software Foundation" and pathlib.PureWindowsPath(path).name.lower() not in RUNTIME:
            problems.append(f"{path}: signed by {name!r}, a signer that stands only on {' and '.join(RUNTIME)}")
    if not records:
        problems.append("no program file was checked")
    for name in expected:
        if name.lower() not in seen:
            problems.append(f"{name} was not among the files checked")
    return problems


def _subject_part(subject: str, key: str) -> str:
    """The value of ``key`` (CN, O) in a certificate's subject as PowerShell writes it, '' where it has none."""
    found = re.search(r"(?:^|,\s*)" + key + r"=(\"[^\"]*\"|[^,]*)", subject)
    return found.group(1).strip('"').strip() if found else ""


def _records(text: str) -> "list[dict[str, object]]":
    loaded = json.loads(text) if text.strip() else []
    if isinstance(loaded, dict):
        loaded = [loaded]
    return [item for item in loaded if isinstance(item, dict)]


def main(argv: "list[str] | None" = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    try:
        if arguments == ["version"]:
            release, pinned = version()
            print(f"{release} {'pinned' if pinned else 'unpinned'}")
            return 0
        if len(arguments) == 2 and arguments[0] == "urls":
            for address in urls(arguments[1]):
                print(address)
            return 0
        if len(arguments) == 4 and arguments[0] == "check":
            problems, lines = check(pathlib.Path(arguments[1]), pathlib.Path(arguments[2]), arguments[3])
            print("\n".join(lines))
        elif len(arguments) == 3 and arguments[0] == "signatures":
            urls(arguments[2])
            text = pathlib.Path(arguments[1]).read_text(encoding="utf-8-sig")
            records = _records(text)
            expected = ["python.exe", f"python{MINOR[0]}{MINOR[1]}.dll", INSTALLER.format(version=arguments[2])]
            problems = signature_problems(records, expected)
            print(f"checked the signatures of {len(records)} files")
        else:
            print(__doc__.split("\n\n")[-1])
            return 2
    except ValueError as error:
        print(f"windows_python: {error}")
        return 1
    if problems:
        print("The python.org files did not pass:")
        for problem in problems:
            print(" -", problem)
        return 1
    print("the python.org files passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
