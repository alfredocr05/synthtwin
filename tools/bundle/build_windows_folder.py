#!/usr/bin/env python3
"""Assemble synthtwin's ready folder for Windows, and its backup, from checked files.

Plan P4-D483 (lane WIN of the December plan; the owner's D3 of
2026-10-20: the hash-checked offline bundle is the only way synthtwin is
installed; the orchestrator's LANE WIN RULINGS 1, W1 and W7). The
workflow file windows-bundle.yml in the repository's workflow folder
runs this on a Windows runner, after its own steps downloaded, with
every hash checked, python.org's embeddable Python 3.14 and its
installer (judged by windows_python.py) and the wheels of
requirements-install.lock. It opens no network connection, and nothing
it makes is ever committed.

THE READY FOLDER, made by `ready`, unzipped and run where it lands --
nothing installed, no administrator, no PATH change:

    synthtwin-VERSION-win\\
      START-HERE.bat           double-click: check every file, open the window
      synthtwin.bat            the folder's python.exe, -I -B -X utf8 -m synthtwin
      INSTALL-WINDOWS.txt      the steps for a physician, then For IT
      BUILD-INFO.txt           the commit, the versions and every wheel's hash
      LICENSE                  synthtwin's own licence
      THIRD-PARTY-NOTICES.txt  the libraries' licences and Python's own
      SHA256SUMS               the SHA-256 of every other file
      scripts\\check_folder.py  START-HERE's check (tools/bundle/check_folder.py)
      python\\                  python.org's embeddable Python, as it came
      python\\python314._pth    the zip, the dot and lib: no import site line
      python\\lib\\              the locked libraries and synthtwin

`python\\lib` is filled by pip with the runner's own Python 3.14 (the
same minor release, so the same wheels), exactly as install.bat installs
the bundle: --isolated, --no-index from the checked wheelhouse alone,
--require-hashes, binary wheels only, then synthtwin's wheel by name
with --no-deps. pip's bin folder (its unsigned .exe launchers) is
removed, and nothing else. Every .py of `python\\lib` is then compiled
by the folder's own python.exe in unchecked-hash mode, so the folder,
run with -B, never writes a byte into itself, and each compiled file
records its source as `python\\lib\\...`, never the build's own path, so
two builds of the same inputs in two different folders make the same
files and the same zip. A wheel the lock does not pin is refused
(build_bundle.wheelhouse_problems). Two checks refuse a folder that
would fail on a hospital computer:

* THE PATH BUDGET: no file's path inside the zip, its top folder
  included, is longer than 159 characters, and no folder's longer than
  147, so unzipped under any place of up to 99 characters (100 with its
  separator) every path stays inside Windows' limits with long paths
  off: 259 characters for a file and 247 for a folder, the drive
  included;
* THE DLL CLOSURE (pe_imports.py): every DLL a .pyd or .dll imports is
  in the folder or ships with every Windows 10 and 11 x64.

THE BACKUP, made by `backup`: the bundle build_bundle.py makes for
win_amd64 (all four Pythons), python.org's 3.14 installer and a short
note, in one zip. Usage:

    python tools/bundle/build_windows_folder.py ready --embeddable ZIP \\
        --wheelhouse DIR --synthtwin-wheel FILE --release 3.14.N \\
        --commit SHA --out DIR --zip-into DIR [--unpinned]
    python tools/bundle/build_windows_folder.py backup --bundle-zip ZIP \\
        --installer EXE --release 3.14.N --out DIR --zip-into DIR [--unpinned]

Each prints what it made and the zip's SHA-256, or every problem and
exits 1.
"""

import argparse
import email.parser
import os
import pathlib
import re
import shutil
import subprocess
import sys
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_bundle  # noqa: E402
import pe_imports  # noqa: E402
import windows_python  # noqa: E402

REPO = HERE.parents[1]

# Windows' limit without long paths is 259 characters in all, the drive
# included (MAX_PATH, 260, counts the terminating NUL); a place of up to
# 100 characters, its trailing backslash included, leaves 159 for the
# zip's paths.
PATH_BUDGET = 159
# A folder's own path may hold only 247 characters (248 with the NUL:
# CreateDirectory's MAX_PATH less 12), so the same place leaves 147 for
# the zip's folders; the deepest folder is projected at 107 characters.
FOLDER_BUDGET = 147
TAG = f"{windows_python.MINOR[0]}{windows_python.MINOR[1]}"

# What the ready folder copies from the repository, by its place there.
COPIED = {
    "START-HERE.bat": "scripts/windows/START-HERE.bat",
    "synthtwin.bat": "scripts/windows/synthtwin.bat",
    "INSTALL-WINDOWS.txt": "scripts/windows/INSTALL-WINDOWS.txt",
    "LICENSE": "LICENSE",
    "scripts/check_folder.py": "tools/bundle/check_folder.py",
}
SUMS = build_bundle.SUMS
NOTICES = build_bundle.NOTICES
BUILD_INFO = "BUILD-INFO.txt"
BACKUP_NOTE = "READ-ME-FIRST.txt"

_WHEEL = re.compile(r"(?P<name>[^-]+)-(?P<version>[^-]+)(?:-\d[^-]*)?-(?P<python>[^-]+)-(?P<abi>[^-]+)-(?P<platform>[^-]+)\.whl")


def version_of(synthtwin_wheel: pathlib.Path) -> str:
    return synthtwin_wheel.name.split("-")[1]


def top_name(synthtwin_wheel: pathlib.Path) -> str:
    """synthtwin-VERSION-win: the ready folder, inside its zip."""
    return f"synthtwin-{version_of(synthtwin_wheel)}-win"


def zip_name(synthtwin_wheel: pathlib.Path, kind: str, pinned: bool) -> str:
    """synthtwin-VERSION-windows-ready.zip (or -backup), -unpinned while the Python is not pinned."""
    return f"synthtwin-{version_of(synthtwin_wheel)}-windows-{kind}{'' if pinned else '-unpinned'}.zip"


def _normal(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def pth_text(original: str) -> str:
    """python3XX._pth: the standard library's zip, the folder itself and lib; no import site.

    The line ending of python.org's own file is kept.
    """
    ending = "\r\n" if "\r\n" in original else "\n"
    return ending.join((f"python{TAG}.zip", ".", "lib")) + ending


def pip_commands(
    python: str, wheelhouse: pathlib.Path, lock: pathlib.Path, own: pathlib.Path, target: pathlib.Path
) -> "list[list[str]]":
    """The two pip commands that fill ``target``, as install.bat runs them, binary wheels only."""
    common = [
        python,
        "-m",
        "pip",
        "install",
        "--isolated",
        "--disable-pip-version-check",
        "--no-index",
        "--only-binary=:all:",
        "--no-compile",
        "--target",
        str(target),
    ]
    return [
        common + ["--find-links", str(wheelhouse), "--require-hashes", "-r", str(lock)],
        common + ["--no-deps", "--find-links", str(own), "synthtwin"],
    ]


# The name each compiled file records for its source, in place of the
# build's own absolute path: the folder's own place for it, the same in
# every build. Python puts the real path back when it imports the file,
# so a traceback still names where the folder stands.
COMPILED_AS = os.path.join("python", "lib")


def compile_command(python: str, lib: pathlib.Path) -> "list[str]":
    """Every .py of ``lib`` compiled once, in unchecked-hash mode, by ``python``, naming COMPILED_AS.

    `-d` records each source as COMPILED_AS joined to its place under
    ``lib``, so no absolute path of the build lands in any bytecode and
    two builds of the same inputs in two folders write the same bytes.
    """
    return [
        python, "-I", "-m", "compileall", "-q", "-f", "--invalidation-mode", "unchecked-hash",
        "-d", COMPILED_AS, str(lib),
    ]


def _run(command: "list[str]") -> "tuple[int, str]":
    environment = dict(os.environ)
    environment["PIP_CONFIG_FILE"] = os.devnull
    done = subprocess.run(command, capture_output=True, text=True, env=environment, check=False)
    return done.returncode, (done.stdout + done.stderr)[-4000:]


def _extract(archive: pathlib.Path, into: pathlib.Path) -> "list[str]":
    """Unzip ``archive`` into ``into``, refusing a member that would land outside it."""
    with zipfile.ZipFile(archive) as opened:
        for member in opened.namelist():
            parts = member.replace("\\", "/").split("/")
            if member.startswith(("/", "\\")) or ".." in parts or ":" in member:
                return [f"{archive.name} holds a member outside its folder: {member!r}"]
        opened.extractall(into)
    return []


def installed(lib: pathlib.Path) -> "dict[str, str]":
    """The distributions pip installed into ``lib``: normalized name to version."""
    found: "dict[str, str]" = {}
    for info in sorted(lib.glob("*.dist-info")):
        metadata = info / "METADATA"
        if not metadata.is_file():
            continue
        meta = email.parser.HeaderParser().parsestr(metadata.read_text(encoding="utf-8", errors="replace"))
        found[_normal(str(meta.get("Name", "")))] = str(meta.get("Version", ""))
    return found


def wheels_used(wheelhouse: pathlib.Path, lib: pathlib.Path) -> "list[pathlib.Path]":
    """The wheelhouse's wheels of the versions installed in ``lib``, for this Python or any."""
    present = installed(lib)
    used: "list[pathlib.Path]" = []
    for wheel in sorted(wheelhouse.glob("*.whl")):
        parts = _WHEEL.fullmatch(wheel.name)
        if parts is None or present.get(_normal(parts["name"])) != parts["version"]:
            continue
        pythons = parts["python"].split(".")
        if f"cp{TAG}" in pythons or any(tag.startswith("py3") for tag in pythons) or parts["abi"] == "abi3":
            used += [wheel]
    return used


def longest_paths(top: pathlib.Path, count: int = 3, folders: bool = False) -> "list[tuple[int, str]]":
    """The longest file paths under ``top`` (its folders' with ``folders``), its own name included, with their lengths."""
    shown = (
        f"{top.name}/{path.relative_to(top).as_posix()}"
        for path in top.rglob("*")
        if (path.is_dir() if folders else path.is_file())
    )
    return sorted(((len(each), each) for each in shown), reverse=True)[:count]


def budget_problems(
    top: pathlib.Path, budget: int = PATH_BUDGET, folder_budget: int = FOLDER_BUDGET
) -> "list[str]":
    """Every file path past ``budget`` and every folder path past ``folder_budget``, top folder included."""
    problems = [
        f"{shown} is {length} characters long, past the path budget of {budget}"
        for length, shown in longest_paths(top, 10**9)
        if length > budget
    ]
    problems += [
        f"the folder {shown} is {length} characters long, past the folder budget of {folder_budget}"
        for length, shown in longest_paths(top, 10**9, folders=True)
        if length > folder_budget
    ]
    return problems


def write_sums(folder: pathlib.Path) -> None:
    """SHA256SUMS over every other file of ``folder``, as the bundle writes it."""
    listed = sorted(
        path.relative_to(folder).as_posix()
        for path in folder.rglob("*")
        if path.is_file() and path.name != SUMS
    )
    text = "".join(f"{build_bundle.sha256_of(folder / name)}  {name}\n" for name in listed)
    (folder / SUMS).write_bytes(text.encode("utf-8"))


def _python_notice(python: pathlib.Path, release: str) -> str:
    licence = python / "LICENSE.txt"
    text = licence.read_text(encoding="utf-8", errors="replace").rstrip("\n") if licence.is_file() else ""
    return "\n".join(
        [
            "=" * 72,
            f"Python {release} (python.org's embeddable package for Windows, 64-bit)",
            "Licence: PSF-2.0, and the licences its LICENSE.txt lists",
            "=" * 72,
            "",
            "--- python/LICENSE.txt ---",
            "",
            text,
            "",
        ]
    )


def build_info(
    synthtwin_wheel: pathlib.Path,
    embeddable: pathlib.Path,
    release: str,
    pinned: bool,
    commit: str,
    wheels: "list[pathlib.Path]",
) -> str:
    """BUILD-INFO.txt: the commit, the versions and every file's SHA-256; no times."""
    pin = (
        "pinned in tools/bundle/windows_python.py"
        if pinned
        else "NOT YET PINNED: trusted on first use after its signature check, so not for use on real data"
    )
    lines = [
        "synthtwin's ready folder for Windows",
        "",
        f"synthtwin {version_of(synthtwin_wheel)}, from commit {commit}, made by the",
        "workflow windows-bundle.yml of synthtwin's repository.",
        "",
        f"Python {release}: python.org's embeddable package {embeddable.name},",
        f"SHA-256 {build_bundle.sha256_of(embeddable)}; {pin}.",
        "",
        "The libraries in python\\lib, installed from requirements-install.lock",
        "with every wheel's SHA-256 checked:",
    ]
    lines += [f"  {wheel.name}  {build_bundle.sha256_of(wheel)}" for wheel in wheels]
    lines += [
        "",
        f"synthtwin itself: {synthtwin_wheel.name}  {build_bundle.sha256_of(synthtwin_wheel)}",
        "",
        "Every other file of this folder is listed in SHA256SUMS, and START-HERE.bat",
        "checks each one before synthtwin starts.",
    ]
    return "\n".join(lines) + "\n"


def assemble(
    embeddable: pathlib.Path,
    wheelhouse: pathlib.Path,
    synthtwin_wheel: pathlib.Path,
    out: pathlib.Path,
    release: str,
    commit: str,
    pinned: bool,
    repo: pathlib.Path = REPO,
    pip_python: str = sys.executable,
    compile_with: "str | None" = None,
    run=_run,
) -> "list[str]":
    """Make the ready folder ``out``; return the problems, empty when made.

    ``out`` must not exist yet; nothing is written when an input has a
    problem. ``run`` stands for running a command (tests hand in their
    own); ``compile_with`` is the folder's own python.exe where None.
    """
    lock = repo / "requirements-install.lock"
    problems = build_bundle.wheelhouse_problems(wheelhouse, lock)
    if not re.fullmatch(r"synthtwin-[^-]+-py3-none-any\.whl", synthtwin_wheel.name):
        problems += [f"{synthtwin_wheel.name} is not a synthtwin wheel for any Python"]
    problems += windows_python.embeddable_problems(embeddable, release)
    if out.exists():
        problems += [f"{out} exists already; the folder is made in a new place"]
    if problems:
        return problems
    python = out / "python"
    lib = python / "lib"
    python.mkdir(parents=True)
    problems = _extract(embeddable, python)
    if problems:
        return problems
    pth = python / f"python{TAG}._pth"
    pth.write_bytes(pth_text(pth.read_bytes().decode("utf-8", "replace")).encode("utf-8"))
    own = out.parent / (out.name + ".synthtwin-wheel")
    own.mkdir()
    shutil.copyfile(synthtwin_wheel, own / synthtwin_wheel.name)
    try:
        for command in pip_commands(pip_python, wheelhouse, lock, own, lib):
            status, said = run(command)
            if status != 0:
                return [f"pip stopped (exit {status}) on {' '.join(command[3:])}:\n{said}"]
    finally:
        shutil.rmtree(own)
    shutil.rmtree(lib / "bin", ignore_errors=True)
    status, said = run(compile_command(compile_with or str(python / "python.exe"), lib))
    if status != 0:
        return [f"compileall stopped (exit {status}):\n{said}"]
    (out / "scripts").mkdir()
    for placed, source in COPIED.items():
        shutil.copyfile(repo / source, out / placed)
    wheels = wheels_used(wheelhouse, lib)
    (out / NOTICES).write_bytes(
        (build_bundle.notices(wheels) + "\n" + _python_notice(python, release)).encode("utf-8")
    )
    (out / BUILD_INFO).write_bytes(
        build_info(synthtwin_wheel, embeddable, release, pinned, commit, wheels).encode("utf-8")
    )
    write_sums(out)
    problems = budget_problems(out)
    report = pe_imports.closure(out)
    problems += [f"DLL closure: {line}" for line in report["missing"] + report["damaged"] + report["foreign"]]
    return problems


BACKUP_TEXT = """synthtwin's backup for Windows: the bundle and the Python installer

Use this only if the ready folder (synthtwin-{version}-windows-ready.zip)
does not start on the computer. It needs a Python installed first.

1. Install Python {release} with the installer in this folder,
   {installer}. On its first screen, untick "Use admin privileges when
   installing py.exe", tick "Add python.exe to PATH", then choose
   "Install Now". Nothing else is needed from the internet.
2. Unzip synthtwin-{version}-win_amd64.zip (right-click it, Extract All)
   into a short place such as C:\\synthtwin-backup.
3. Follow INSTALL.txt inside the unzipped folder, "On Windows": in
   Command Prompt, scripts\\install.bat, then .venv\\Scripts\\activate in
   each new window.

SHA256SUMS in this folder holds the SHA-256 of the two other files;
the bundle checks every file of its own before it installs anything.
{pin}
"""


def backup(
    bundle_zip: pathlib.Path,
    installer: pathlib.Path,
    out: pathlib.Path,
    release: str,
    pinned: bool,
) -> "list[str]":
    """Make the backup folder ``out``: the bundle's zip, the installer, the note and SHA256SUMS."""
    problems: "list[str]" = []
    found = re.fullmatch(r"synthtwin-([^-]+)-win_amd64\.zip", bundle_zip.name)
    if found is None:
        problems += [f"{bundle_zip.name} is not the bundle build_bundle.py makes for win_amd64"]
    if installer.name != windows_python.INSTALLER.format(version=release):
        problems += [f"{installer.name} is not named {windows_python.INSTALLER.format(version=release)}"]
    if out.exists():
        problems += [f"{out} exists already; the backup is made in a new place"]
    if problems or found is None:
        return problems
    out.mkdir(parents=True)
    shutil.copyfile(bundle_zip, out / bundle_zip.name)
    shutil.copyfile(installer, out / installer.name)
    pin = "" if pinned else (
        "\nNOT YET PINNED: the Python installer was trusted on first use after its\n"
        "signature check, so this backup is not for use on real data.\n"
    )
    note = BACKUP_TEXT.format(version=found.group(1), release=release, installer=installer.name, pin=pin)
    (out / BACKUP_NOTE).write_bytes(note.replace("\n", "\r\n").encode("utf-8"))
    write_sums(out)
    return []


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(prog="build_windows_folder", description=__doc__.split("\n")[0])
    kinds = parser.add_subparsers(dest="kind", required=True)
    ready = kinds.add_parser("ready")
    ready.add_argument("--embeddable", required=True, type=pathlib.Path)
    ready.add_argument("--wheelhouse", required=True, type=pathlib.Path)
    ready.add_argument("--synthtwin-wheel", required=True, type=pathlib.Path)
    ready.add_argument("--commit", required=True)
    for each in (ready, kinds.add_parser("backup")):
        each.add_argument("--release", required=True)
        each.add_argument("--out", required=True, type=pathlib.Path)
        each.add_argument("--zip-into", required=True, type=pathlib.Path)
        each.add_argument("--unpinned", action="store_true")
    kinds.choices["backup"].add_argument("--bundle-zip", required=True, type=pathlib.Path)
    kinds.choices["backup"].add_argument("--installer", required=True, type=pathlib.Path)
    args = parser.parse_args(argv)
    pinned = not args.unpinned
    if args.kind == "ready":
        made = args.out / top_name(args.synthtwin_wheel)
        problems = assemble(
            args.embeddable, args.wheelhouse, args.synthtwin_wheel, made, args.release, args.commit, pinned
        )
        target = args.zip_into / zip_name(args.synthtwin_wheel, "ready", pinned)
    else:
        wheel = pathlib.Path(args.bundle_zip.name.replace("-win_amd64.zip", "-py3-none-any.whl"))
        made = args.out / zip_name(wheel, "backup", pinned)[: -len(".zip")]
        problems = backup(args.bundle_zip, args.installer, made, args.release, pinned)
        target = args.zip_into / zip_name(wheel, "backup", pinned)
    if problems:
        print(f"The {args.kind} folder was not made:")
        for problem in problems:
            print(" -", problem)
        return 1
    print(f"made {made}")
    for length, shown in longest_paths(made):
        print(f"  {length:3d} characters: {shown}")
    for length, shown in longest_paths(made, folders=True):
        print(f"  {length:3d} characters (a folder): {shown}")
    args.zip_into.mkdir(parents=True, exist_ok=True)
    print(f"{build_bundle.zip_folder(made, target)}  {target.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
