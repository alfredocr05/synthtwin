"""The ready folder for Windows, its backup, its launchers and their rehearsal.

Plan P4-D483 (lane WIN of the December plan; the orchestrator's LANE WIN
RULINGS 1). The folder is built and rehearsed only in CI, by the workflow
file windows-bundle.yml in the repository's workflow folder, on Windows
runners this machine is not; nothing here downloads anything. So this
file holds what can be held here, each rule red on its mutant:

* the workflow's text: its jobs, their order and runners, the four
  action pins equal to ci.yml's, nothing published, a read-only token, a
  time limit on every job, the internal artifacts kept a day and the
  rehearsed zips 90 (and only by the keep job), no package index or
  python.org in a rehearsal job, the network refused and proven refused
  before the trial runs, every later step running the rehearsed
  interpreter and handing the tools no other interpreter or folder, the
  backup's Python installed fresh and its trial run under the guard too;
* the builder on stub wheels and a stub embeddable Python (made here, as
  tests/test_bundle.py makes its stub wheels): the ._pth file, the
  launchers, SHA256SUMS over every file, an unpinned wheel refused, the
  path budget, the same zip twice and the same zip from two build
  folders, and the backup;
* check_folder.py's refusals and warnings, an extra program file
  refused, and the window it opens, every command in it naming the
  checked launcher or interpreter by its full path;
* pe_imports.py on Windows program files built here byte by byte, a DLL
  counted only where Windows looks when the file loads;
* windows_python.py's pin in both its states and its signature reading,
  fill_answers.py's rounds, guard_run.py's guard and its proofs (the
  firewall's only by its access-denied refusal), and
  rehearse_windows.py's commands and each of its verdicts;
* the launchers' line endings and words, INSTALL-WINDOWS.txt plain, and
  both guides checking the zip first and saying what the folder's own
  check guards against.
"""

import csv
import hashlib
import importlib.util
import io
import json
import os
import pathlib
import re
import shutil
import socket
import struct
import subprocess
import sys
import zipfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
WINDOWS = REPO / "scripts" / "windows"
WORKFLOW = REPO / ".github" / "workflows" / "windows-bundle.yml"
CI = REPO / ".github" / "workflows" / "ci.yml"


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, REPO / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sys.path.insert(0, str(REPO / "tools" / "bundle"))
BUILD = _load("build_windows_folder", "tools/bundle/build_windows_folder.py")
FOLDER = _load("check_folder", "tools/bundle/check_folder.py")
PE = _load("pe_imports", "tools/bundle/pe_imports.py")
PYTHON = _load("windows_python", "tools/bundle/windows_python.py")
ANSWERS = _load("fill_answers", "tools/bundle/fill_answers.py")
GUARD = _load("guard_run", "tools/bundle/guard_run.py")
REHEARSE = _load("rehearse_windows", "tools/bundle/rehearse_windows.py")
MODELS = _load("bundle_test_models", "tests/test_bundle.py")

RELEASE = "3.14.9"


def _sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# -- Windows program files, built byte by byte --------------------------------


def _pe(imports: "list[str]", delayed: "list[str] | None" = None, machine: int = 0x8664) -> bytes:
    """A minimal PE32+ file whose import and delay-import tables name ``imports`` and ``delayed``."""
    delayed = delayed or []
    section_rva, raw_at = 0x1000, 0x200
    imports_at = 0
    delayed_at = 20 * (len(imports) + 1)
    names_at = delayed_at + 32 * (len(delayed) + 1)
    names = b""
    offsets = []
    for name in imports + delayed:
        offsets += [names_at + len(names)]
        names += name.encode("ascii") + b"\0"
    body = bytearray(names_at) + names
    for index, name_offset in enumerate(offsets[: len(imports)]):
        struct.pack_into("<IIIII", body, imports_at + 20 * index, 0, 0, 0, section_rva + name_offset, 0)
    for index, name_offset in enumerate(offsets[len(imports) :]):
        struct.pack_into("<IIIIIIII", body, delayed_at + 32 * index, 1, section_rva + name_offset, 0, 0, 0, 0, 0, 0)
    raw_size = (len(body) + 0x1FF) // 0x200 * 0x200
    head = bytearray(raw_at)
    head[0:2] = b"MZ"
    struct.pack_into("<I", head, 0x3C, 0x40)
    head[0x40:0x44] = b"PE\0\0"
    struct.pack_into("<HHIIIHH", head, 0x44, machine, 1, 0, 0, 0, 240, 0x2022)
    optional = 0x58
    struct.pack_into("<H", head, optional, 0x20B)
    struct.pack_into("<Q", head, optional + 24, 0x180000000)
    struct.pack_into("<I", head, optional + 60, raw_at)
    struct.pack_into("<I", head, optional + 108, 16)
    if imports:
        struct.pack_into("<II", head, optional + 112 + 8 * 1, section_rva + imports_at, 20 * (len(imports) + 1))
    if delayed:
        struct.pack_into("<II", head, optional + 112 + 8 * 13, section_rva + delayed_at, 32 * (len(delayed) + 1))
    section = optional + 240
    head[section : section + 8] = b".rdata\0\0"
    struct.pack_into("<IIII", head, section + 8, len(body), section_rva, raw_size, raw_at)
    return bytes(head) + bytes(body) + b"\0" * (raw_size - len(body))


def test_the_import_tables_are_read_from_a_program_file() -> None:
    machine, imported, delayed = PE.imports_of(_pe(["KERNEL32.dll", "MSVCP140.dll"], ["late.dll"]))
    assert (machine, imported, delayed) == ("x64", ["KERNEL32.dll", "MSVCP140.dll"], ["late.dll"])
    for damaged, words in (
        (b"not a program", "does not start with MZ"),
        (_pe(["KERNEL32.dll"])[:0x60], "ends before its own headers do"),
    ):
        with pytest.raises(PE.PEError, match=words):
            PE.imports_of(damaged)


def _closure(tmp_path: pathlib.Path, extra: "dict[str, bytes]") -> "dict[str, list[str]]":
    folder = tmp_path / "ready"
    files = {"python/python.exe": _pe(["python314.dll", "KERNEL32.dll"]), "python/python314.dll": _pe(["KERNEL32.dll"])}
    files.update(extra)
    for name, data in files.items():
        (folder / name).parent.mkdir(parents=True, exist_ok=True)
        (folder / name).write_bytes(data)
    return PE.closure(folder)


def test_the_visual_cpp_runtime_must_be_carried_by_the_folder(tmp_path: pathlib.Path) -> None:
    needing = {"python/lib/pkg/_fast.pyd": _pe(["MSVCP140.dll", "api-ms-win-crt-runtime-l1-1-0.dll"])}
    missing = _closure(tmp_path / "one", needing)["missing"]
    assert missing == ["python/lib/pkg/_fast.pyd needs MSVCP140.dll"], missing
    carried = dict(needing, **{"python/msvcp140.dll": _pe(["KERNEL32.dll"])})
    assert _closure(tmp_path / "two", carried)["missing"] == []
    # Held where Windows does not look for the file that needs it: refused,
    # since on the runner the system's own copy would answer instead.
    elsewhere = dict(needing, **{"python/lib/other/msvcp140.dll": _pe(["KERNEL32.dll"])})
    assert "where Windows does not look for it" in " ".join(_closure(tmp_path / "three", elsewhere)["missing"])
    assert not PE.is_system("VCRUNTIME140.dll") and not PE.is_system("vcomp140.dll")
    assert PE.is_system("KERNEL32.dll") and PE.is_system("api-ms-win-core-path-l1-1-0.dll")
    assert len(PE.SYSTEM_DLLS) == 52, "the list's own comment says 51 names before run 1, and webservices.dll after"


def test_a_dll_counts_only_where_windows_looks_when_the_file_loads(tmp_path: pathlib.Path) -> None:
    """Codex's item 2: python.exe starts before any library registers its .libs folder; a folder is no DLL."""
    # The first counterexample: the runtime python.exe needs, carried only
    # in numpy's .libs folder, which no import has registered at startup.
    starting = {
        "python/python.exe": _pe(["python314.dll", "KERNEL32.dll", "VCRUNTIME140.dll"]),
        "python/lib/numpy.libs/VCRUNTIME140.dll": _pe(["KERNEL32.dll"]),
    }
    missing = _closure(tmp_path / "startup", starting)["missing"]
    assert missing == [
        "python/python.exe needs VCRUNTIME140.dll, which the folder holds only in another folder, "
        "where Windows does not look for it"
    ], missing
    # The second: a folder named like the DLL, beside the file that needs it.
    folder_named = {"python/lib/pkg/_fast.pyd": _pe(["MSVCP140.dll", "KERNEL32.dll"])}
    (tmp_path / "dir" / "ready" / "python" / "lib" / "pkg" / "MSVCP140.dll").mkdir(parents=True)
    (tmp_path / "dir" / "ready" / "python" / "MSVCP140.dll").mkdir(parents=True)
    assert _closure(tmp_path / "dir", folder_named)["missing"] == ["python/lib/pkg/_fast.pyd needs MSVCP140.dll"]
    # The layout the libraries' wheels hold: a package's own .libs folder
    # serves that package's files, once its import registered it, and no
    # other package's.
    vendored = {
        "python/lib/numpy/_core/_multiarray.pyd": _pe(["msvcp140-0a1b2c3d.dll", "python314.dll", "KERNEL32.dll"]),
        "python/lib/numpy.libs/msvcp140-0a1b2c3d.dll": _pe(["KERNEL32.dll"]),
    }
    assert _closure(tmp_path / "own", vendored)["missing"] == []
    borrowed = dict(vendored, **{"python/lib/scipy/_lib/_fast.pyd": _pe(["msvcp140-0a1b2c3d.dll", "KERNEL32.dll"])})
    assert _closure(tmp_path / "borrowed", borrowed)["missing"] == [
        "python/lib/scipy/_lib/_fast.pyd needs msvcp140-0a1b2c3d.dll, which the folder holds only in "
        "another folder, where Windows does not look for it"
    ]


def test_the_runtime_never_counts_as_windows_own_even_where_listed(monkeypatch) -> None:
    """A reviewer adding the runtime to the reviewed list does not make it a system DLL."""
    monkeypatch.setattr(PE, "SYSTEM_DLLS", PE.SYSTEM_DLLS | {"msvcp140.dll", "vcruntime140_1.dll", "concrt140.dll"})
    for name in ("MSVCP140.dll", "vcruntime140_1.dll", "CONCRT140.dll"):
        assert not PE.is_system(name), name


def test_the_web_services_dll_a_run_named_counts_as_windows_own(tmp_path: pathlib.Path) -> None:
    """A Windows run refused the folder for pyarrow's arrow.dll, which imports webservices.dll (Windows' own Web Services API)."""
    needing = {"python/lib/pyarrow/arrow.dll": _pe(["webservices.dll", "KERNEL32.dll"])}
    report = _closure(tmp_path, needing)
    assert report["missing"] == [], report["missing"]
    assert PE.is_system("webservices.dll") and PE.is_system("WebServices.dll")
    assert PE.main([str(tmp_path / "ready")]) == 0


def test_a_delayed_import_is_reported_and_a_damaged_file_refused(tmp_path: pathlib.Path) -> None:
    report = _closure(tmp_path, {"python/lib/pkg/_late.pyd": _pe(["KERNEL32.dll"], ["absent.dll"])})
    assert report["missing"] == [] and report["missing_delayed"] == ["python/lib/pkg/_late.pyd needs absent.dll"]
    report = _closure(tmp_path / "damaged", {"python/lib/pkg/_broken.pyd": b"MZ" + b"\0" * 40})
    assert report["damaged"] and "python/lib/pkg/_broken.pyd" in report["damaged"][0]
    report = _closure(tmp_path / "arm", {"python/lib/pkg/_arm.pyd": _pe(["KERNEL32.dll"], machine=0xAA64)})
    assert report["foreign"] and "Arm64" in report["foreign"][0]
    assert PE.main([str(tmp_path / "damaged" / "ready")]) == 1
    assert PE.main([str(tmp_path / "ready")]) == 0


# -- the stub embeddable Python, the stub wheels, the stub repository ------------


def _embeddable(folder: pathlib.Path) -> pathlib.Path:
    """python.org's embeddable zip in miniature: its names, small real program files."""
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / PYTHON.EMBEDDABLE.format(version=RELEASE)
    stdlib = io.BytesIO()
    with zipfile.ZipFile(stdlib, "w") as inner:
        inner.writestr("os.pyc", b"stand-in")
    members = {
        "python.exe": _pe(["python314.dll", "KERNEL32.dll", "VCRUNTIME140.dll"]),
        "pythonw.exe": _pe(["python314.dll", "KERNEL32.dll", "VCRUNTIME140.dll"]),
        "python314.dll": _pe(["KERNEL32.dll", "VCRUNTIME140.dll", "api-ms-win-crt-runtime-l1-1-0.dll"]),
        "vcruntime140.dll": _pe(["KERNEL32.dll"]),
        "_socket.pyd": _pe(["python314.dll", "WS2_32.dll"]),
        "python314.zip": stdlib.getvalue(),
        "python314._pth": b"python314.zip\r\n.\r\n\r\n# Uncomment to run site.main() automatically\r\n#import site\r\n",
        "LICENSE.txt": b"Stand-in licence of the stand-in Python, written by tests/test_windows_bundle.py.\n",
    }
    with zipfile.ZipFile(path, "w") as archive:
        for name, data in members.items():
            archive.writestr(name, data)
    return path


def _stub(
    tmp_path: pathlib.Path, long_name: str = "", binary: "dict[str, bytes] | None" = None
) -> "dict[str, pathlib.Path]":
    stub = MODELS._stub(tmp_path)
    repo = stub["repo"]
    (repo / "scripts" / "windows").mkdir(parents=True)
    for name in ("START-HERE.bat", "synthtwin.bat", "INSTALL-WINDOWS.txt"):
        shutil.copyfile(WINDOWS / name, repo / "scripts" / "windows" / name)
    shutil.copyfile(REPO / "tools" / "bundle" / "check_folder.py", repo / "tools" / "bundle" / "check_folder.py")
    if long_name or binary:
        files = {"stubdep/__init__.py": ""}
        if long_name:
            files[f"stubdep/{long_name}.py"] = ""
        library = MODELS._wheel(stub["house"], "stubdep", "1.0", files, licence=MODELS.STUB_LICENCE)
        # A library's own program files (a .pyd built byte by byte), added
        # after the text members, as a wheel of a compiled library holds them.
        with zipfile.ZipFile(library, "a") as archive:
            for member, data in (binary or {}).items():
                archive.writestr(member, data)
        (repo / "requirements-install.lock").write_text(
            "--only-binary :all:\nstubdep==1.0 \\\n    --hash=sha256:" + _sha256(library) + "\n",
            encoding="utf-8", newline="\n",
        )
    stub["embeddable"] = _embeddable(tmp_path / "python-org")
    return stub


def _fake_run(stub: "dict[str, pathlib.Path]"):  # type: ignore[no-untyped-def]
    """pip as it fills a --target folder (the wheels unpacked, a bin folder of launchers), and compileall for real."""
    seen: "list[list[str]]" = []

    def run(command: "list[str]") -> "tuple[int, str]":
        seen.append(command)
        if "compileall" in command:
            done = subprocess.run(command, capture_output=True, text=True, check=False)
            return done.returncode, done.stdout + done.stderr
        target = pathlib.Path(command[command.index("--target") + 1])
        wheels = sorted(stub["house"].glob("*.whl")) if "-r" in command else [stub["ours"]]
        for wheel in wheels:
            with zipfile.ZipFile(wheel) as archive:
                archive.extractall(target)
        (target / "bin").mkdir(exist_ok=True)
        (target / "bin" / "stubdep.exe").write_bytes(b"MZ an unsigned launcher pip would write")
        return 0, ""

    run.seen = seen  # type: ignore[attr-defined]
    return run


def _ready(tmp_path: pathlib.Path, long_name: str = "") -> "tuple[pathlib.Path, list[str], object]":
    stub = _stub(tmp_path, long_name)
    out = tmp_path / "with a space" / "synthtwin-0.0.1-win"
    run = _fake_run(stub)
    problems = BUILD.assemble(
        stub["embeddable"], stub["house"], stub["ours"], out, RELEASE, "0" * 40, True,
        repo=stub["repo"], pip_python="python-of-the-runner", compile_with=sys.executable, run=run,
    )
    return out, problems, run


def test_the_builder_makes_a_ready_folder_every_file_listed(tmp_path: pathlib.Path) -> None:
    out, problems, run = _ready(tmp_path)
    assert problems == []
    pth = (out / "python" / "python314._pth").read_bytes()
    assert pth == b"python314.zip\r\n.\r\nlib\r\n" and b"import site" not in pth
    assert not (out / "python" / "lib" / "bin").exists(), "pip's unsigned launchers are removed"
    assert (out / "python" / "lib" / "stubdep" / "__init__.py").is_file()
    compiled = sorted((out / "python" / "lib").rglob("*.pyc"))
    assert compiled and all(path.read_bytes()[4:8] == b"\x01\0\0\0" for path in compiled), "unchecked-hash .pyc"
    assert FOLDER.check(str(out), system="win32", environment={}) == ([], [])
    listed = {line.split("  ", 1)[1] for line in (out / "SHA256SUMS").read_text(encoding="utf-8").splitlines()}
    on_disk = {path.relative_to(out).as_posix() for path in out.rglob("*") if path.is_file()} - {"SHA256SUMS"}
    assert listed == on_disk
    for placed in ("START-HERE.bat", "synthtwin.bat", "INSTALL-WINDOWS.txt", "LICENSE", "scripts/check_folder.py"):
        assert (out / placed).is_file(), placed
    info = (out / "BUILD-INFO.txt").read_text(encoding="utf-8")
    assert "0" * 40 in info and f"Python {RELEASE}" in info and "stubdep-1.0-py3-none-any.whl" in info
    assert not re.search(r"\d\d:\d\d", info), "no times in BUILD-INFO.txt"
    notices = (out / "THIRD-PARTY-NOTICES.txt").read_text(encoding="utf-8")
    assert MODELS.STUB_LICENCE.strip() in notices and "Stand-in licence of the stand-in Python" in notices
    first, second = run.seen[0], run.seen[1]  # type: ignore[attr-defined]
    for flag in ("--isolated", "--no-index", "--only-binary=:all:", "--no-compile", "--target"):
        assert flag in first and flag in second, flag
    assert "--require-hashes" in first and "--no-deps" not in first
    assert "--no-deps" in second and second[-1] == "synthtwin" and "--require-hashes" not in second
    assert run.seen[2] == BUILD.compile_command(sys.executable, out / "python" / "lib")  # type: ignore[attr-defined]
    assert {"-I", "--invalidation-mode", "unchecked-hash"} <= set(run.seen[2])  # type: ignore[attr-defined]


def test_the_builder_refuses_an_unpinned_wheel_and_writes_nothing(tmp_path: pathlib.Path) -> None:
    stub = _stub(tmp_path)
    MODELS._wheel(stub["house"], "unpinned", "1.0", {"unpinned/__init__.py": ""})
    out = tmp_path / "out" / "synthtwin-0.0.1-win"
    problems = BUILD.assemble(
        stub["embeddable"], stub["house"], stub["ours"], out, RELEASE, "0" * 40, True,
        repo=stub["repo"], run=_fake_run(stub),
    )
    assert "unpinned-1.0-py3-none-any.whl has a SHA-256 the lock does not pin" in " ".join(problems)
    assert not out.exists()
    wrong = tmp_path / "python-3.14.9-embed-arm64.zip"
    shutil.copyfile(stub["embeddable"], wrong)
    assert "is not named python-3.14.9-embed-amd64.zip" in " ".join(PYTHON.embeddable_problems(wrong, RELEASE))


def test_the_path_budget_refuses_a_path_too_long_for_windows(tmp_path: pathlib.Path) -> None:
    out, problems, _ = _ready(tmp_path, long_name="x" * 120)
    assert any("past the path budget of 159" in problem for problem in problems), problems
    assert BUILD.budget_problems(out, budget=10**6) == []
    within, problems, _ = _ready(tmp_path / "within")
    assert problems == [] and BUILD.longest_paths(within)[0][0] <= BUILD.PATH_BUDGET


def _tree(tmp_path: pathlib.Path, relative: str) -> pathlib.Path:
    """A top folder named as the zip's is, holding one file at ``relative``."""
    top = tmp_path / "synthtwin-0.0.1-win"
    (top / relative).parent.mkdir(parents=True, exist_ok=True)
    (top / relative).write_bytes(b"")
    return top


def test_the_path_budget_holds_a_path_of_159_and_refuses_160(tmp_path: pathlib.Path) -> None:
    """Exactly at the edges: 259 characters in all is Windows' limit, 100 of them the place."""
    assert (BUILD.PATH_BUDGET, BUILD.FOLDER_BUDGET) == (159, 147)
    head = len("synthtwin-0.0.1-win/")
    assert BUILD.budget_problems(_tree(tmp_path / "a", "f" * (159 - head))) == []
    refused = BUILD.budget_problems(_tree(tmp_path / "b", "f" * (160 - head)))
    assert len(refused) == 1 and "is 160 characters long, past the path budget of 159" in refused[0]


def test_the_folder_budget_holds_a_folder_of_147_and_refuses_148(tmp_path: pathlib.Path) -> None:
    """A folder's own path may hold 247 characters in all, so 147 under a place of 100; its file is short."""
    head = len("synthtwin-0.0.1-win/")
    assert BUILD.budget_problems(_tree(tmp_path / "a", "d" * (147 - head) + "/x")) == []
    refused = BUILD.budget_problems(_tree(tmp_path / "b", "d" * (148 - head) + "/x"))
    assert len(refused) == 1 and "is 148 characters long, past the folder budget of 147" in refused[0], refused


def test_the_builder_refuses_a_library_whose_dll_the_folder_lacks(tmp_path: pathlib.Path) -> None:
    """A stub wheel's .pyd imports MSVCP140.dll, which the folder does not carry: assemble refuses it."""
    stub = _stub(tmp_path, binary={"stubdep/_fast.pyd": _pe(["MSVCP140.dll", "KERNEL32.dll"])})
    out = tmp_path / "out" / "synthtwin-0.0.1-win"
    problems = BUILD.assemble(
        stub["embeddable"], stub["house"], stub["ours"], out, RELEASE, "0" * 40, True,
        repo=stub["repo"], pip_python="python-of-the-runner", compile_with=sys.executable, run=_fake_run(stub),
    )
    assert problems == ["DLL closure: python/lib/stubdep/_fast.pyd needs MSVCP140.dll"], problems


def test_the_same_folder_makes_the_same_zip_twice(tmp_path: pathlib.Path) -> None:
    out, problems, _ = _ready(tmp_path)
    assert problems == []
    first = MODELS.BUILD.zip_folder(out, tmp_path / "one.zip")
    second = MODELS.BUILD.zip_folder(out, tmp_path / "two.zip")
    assert first == second
    with zipfile.ZipFile(tmp_path / "one.zip") as archive:
        assert all(name.startswith("synthtwin-0.0.1-win/") for name in archive.namelist())
    wheel = pathlib.Path("dist/synthtwin-0.1.0-py3-none-any.whl")
    assert BUILD.top_name(wheel) == "synthtwin-0.1.0-win"
    assert BUILD.zip_name(wheel, "ready", True) == "synthtwin-0.1.0-windows-ready.zip"
    assert BUILD.zip_name(wheel, "backup", False) == "synthtwin-0.1.0-windows-backup-unpinned.zip"


def test_two_builds_in_two_folders_make_the_same_zip(tmp_path: pathlib.Path) -> None:
    """Codex's item 9: the same inputs built in two different folders give the same zip, byte for byte.

    The library's modules are compiled for real (this machine's Python),
    and no bytecode may record the place it was built in.
    """
    stub = _stub(tmp_path / "inputs")
    digests = []
    for place in ("build-a", "a second build, in a longer place"):
        out = tmp_path / place / "synthtwin-0.0.1-win"
        problems = BUILD.assemble(
            stub["embeddable"], stub["house"], stub["ours"], out, RELEASE, "0" * 40, True,
            repo=stub["repo"], pip_python="python-of-the-runner", compile_with=sys.executable, run=_fake_run(stub),
        )
        assert problems == []
        compiled = sorted(out.rglob("*.pyc"))
        assert compiled and not any(place.encode() in path.read_bytes() for path in compiled), "a build path in a .pyc"
        digests += [MODELS.BUILD.zip_folder(out, tmp_path / f"{place}.zip")]
    assert digests[0] == digests[1]
    assert BUILD.compile_command("py", tmp_path)[-3:] == ["-d", BUILD.COMPILED_AS, str(tmp_path)]


def test_the_backup_carries_the_bundle_the_installer_and_a_note(tmp_path: pathlib.Path) -> None:
    bundle = tmp_path / "synthtwin-0.0.1-win_amd64.zip"
    bundle.write_bytes(b"the bundle")
    installer = tmp_path / PYTHON.INSTALLER.format(version=RELEASE)
    installer.write_bytes(b"the installer")
    out = tmp_path / "backup" / "synthtwin-0.0.1-windows-backup"
    assert BUILD.backup(bundle, installer, out, RELEASE, False) == []
    note = (out / BUILD.BACKUP_NOTE).read_bytes()
    assert b"\r\n" in note and b"\n" not in note.replace(b"\r\n", b"")
    assert "NOT YET PINNED" in note.decode("utf-8") and "Add python.exe to PATH" in note.decode("utf-8")
    listed = (out / "SHA256SUMS").read_text(encoding="utf-8")
    assert f"{_sha256(installer)}  {installer.name}" in listed and f"{_sha256(bundle)}  {bundle.name}" in listed
    other = tmp_path / "python-3.14.8-amd64.exe"
    other.write_bytes(b"another installer")
    assert BUILD.backup(bundle, other, tmp_path / "again", RELEASE, True)


# -- check_folder.py ------------------------------------------------------------


def _folder(tmp_path: pathlib.Path) -> pathlib.Path:
    folder = tmp_path / "Dr O'Brien files" / "synthtwin-0.0.1-win"
    for name, data in (
        ("START-HERE.bat", b"@echo off\r\n"),
        ("python/python.exe", b"MZ"),
        ("python/lib/numpy/__init__.py", b"x = 1\n"),
        ("scripts/check_folder.py", b"# the check\n"),
    ):
        (folder / name).parent.mkdir(parents=True, exist_ok=True)
        (folder / name).write_bytes(data)
    BUILD.write_sums(folder)
    return folder


def _refused(folder: pathlib.Path, needle: str) -> None:
    problems, _ = FOLDER.check(str(folder), system="win32", environment={})
    assert problems and needle in " ".join(problems), problems


def test_the_check_refuses_a_changed_or_missing_file(tmp_path: pathlib.Path) -> None:
    folder = _folder(tmp_path)
    assert FOLDER.check(str(folder), system="win32", environment={}) == ([], [])
    library = folder / "python" / "lib" / "numpy" / "__init__.py"
    library.write_bytes(b"x = 2\n")
    _refused(folder, "python/lib/numpy/__init__.py does not match its hash in SHA256SUMS")
    library.unlink()
    _refused(folder, "python/lib/numpy/__init__.py is listed in SHA256SUMS but missing")
    (folder / "SHA256SUMS").write_text("0" * 64 + "  ../outside\n", encoding="utf-8", newline="\n")
    _refused(folder, "line 1 of SHA256SUMS is not a SHA-256")
    (folder / "SHA256SUMS").unlink()
    _refused(folder, "the file SHA256SUMS is missing")


def test_the_check_reads_extra_files_by_where_they_are(tmp_path: pathlib.Path) -> None:
    folder = _folder(tmp_path)
    for leftover in ("._START-HERE.bat", ".DS_Store", "python/._python.exe", "python/Thumbs.db", "Desktop.ini"):
        (folder / leftover).write_bytes(b"left by a Mac or by Windows Explorer")
    assert FOLDER.check(str(folder), system="win32", environment={}) == ([], [])
    (folder / "my-table.csv").write_bytes(b"a,b\n")
    problems, warnings = FOLDER.check(str(folder), system="win32", environment={})
    assert problems == [] and "my-table.csv is not one of synthtwin's own files" in " ".join(warnings)
    (folder / "python" / "lib" / "extra.py").write_bytes(b"import os\n")
    _refused(folder, "python/lib/extra.py is not one of the folder's own files, and it sits inside the python folder")
    (folder / "python" / "lib" / "extra.py").unlink()
    # An ending no window runs is still refused inside the python folder,
    # where the folder's Python loads it: the python folder's own rule.
    (folder / "python" / "lib" / "extra.pth").write_bytes(b"import os\n")
    _refused(folder, "python/lib/extra.pth is not one of the folder's own files, and it sits inside the python folder")


def test_an_extra_program_beside_the_launcher_stops_the_run(tmp_path: pathlib.Path) -> None:
    """Codex's item 1, its second state: a program a window could run by the word synthtwin is an error, not a note.

    Generated over every ending the check names and one more the
    computer's own PATHEXT adds, at the folder's top (where the Command
    Prompt window's PATH starts) and deeper; a file of any other ending
    stays a note.
    """
    folder = _folder(tmp_path)
    endings = sorted(FOLDER.RUNNABLE) + [".xyz"]
    assert {".exe", ".com", ".cmd", ".bat", ".ps1"} <= set(FOLDER.RUNNABLE)
    environment = {"PATHEXT": ".COM;.EXE;.BAT;.CMD;.XYZ"}
    tried = 0
    for ending in endings:
        for place in ("synthtwin" + ending, "scripts/synthtwin" + ending.upper()):
            extra = folder / place
            extra.write_bytes(b"MZ a program SHA256SUMS does not list")
            problems, _ = FOLDER.check(str(folder), system="win32", environment=environment)
            extra.unlink()
            assert problems and (place + " is not one of the folder's own files, and a Windows window could run it") in problems[0], place
            tried += 1
    assert tried == 2 * len(endings)
    (folder / "synthtwin.xyz").write_bytes(b"not run: this computer's PATHEXT does not list it")
    problems, warnings = FOLDER.check(str(folder), system="win32", environment={})
    assert problems == [] and "synthtwin.xyz is not one of synthtwin's own files" in " ".join(warnings)


def test_the_check_refuses_another_system_and_warns_on_arm(tmp_path: pathlib.Path) -> None:
    folder = _folder(tmp_path)
    problems, _ = FOLDER.check(str(folder), system="darwin")
    assert "this computer runs macOS" in problems[0]
    problems, warnings = FOLDER.check(str(folder), system="win32", environment={"PROCESSOR_ARCHITECTURE": "ARM64"})
    assert problems == [] and "Arm processor" in warnings[0]


def test_the_check_never_shows_a_traceback(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:
    def broken(*_arguments: object, **_named: object) -> None:
        raise RuntimeError("an unforeseen failure")

    monkeypatch.setattr(FOLDER, "check", broken)
    assert FOLDER.main([str(tmp_path)]) == 1
    said = capsys.readouterr().out
    assert "stopped unexpectedly (RuntimeError)" in said and "Traceback" not in said


def test_start_here_opens_the_window_only_when_the_folder_passed(tmp_path: pathlib.Path, monkeypatch) -> None:
    folder = _folder(tmp_path)
    real = FOLDER.check
    monkeypatch.setattr(FOLDER, "check", lambda place: real(place, system="win32", environment={}))
    opened: "list[str]" = []
    assert FOLDER.main(["--start", str(folder), "/check"], opener=opened.append) == 0 and opened == []
    assert FOLDER.main(["--start", str(folder)], opener=lambda place: opened.append(place) or []) == 0
    assert opened == [str(folder)]
    assert FOLDER.main(["--start", str(folder)], opener=lambda place: ["no window"]) == 1
    (folder / "python" / "python.exe").write_bytes(b"MZ changed")
    assert FOLDER.main(["--start", str(folder)], opener=opened.append) == 1 and len(opened) == 1


def test_the_window_runs_the_folder_python_as_printed(tmp_path: pathlib.Path) -> None:
    folder = str(tmp_path / "Dr O\u2019Brien's files" / "synthtwin-0.0.1-win")
    command = FOLDER.powershell_command(folder)
    assert command.startswith("try { Set-PSReadLineOption -HistorySaveStyle SaveNothing } catch { }; "), "no history file"
    for banner in (FOLDER.POWERSHELL_BANNER, FOLDER.CMD_BANNER):
        flowing = " ".join(banner.split())
        assert "This window keeps no history of what you type" in flowing and "leaves nothing behind" not in flowing
    assert "(not yet measured on Windows)" in " ".join(FOLDER.POWERSHELL_BANNER.split())
    assert "Dr O\u2019\u2019Brien''s files" in command, "every PowerShell quote doubled inside single quotes"
    assert "function global:synthtwin { & '" in command and "' -I -B -X utf8 -m synthtwin @args }" in command
    python = FOLDER._quoted_for_powershell(os.path.join(os.path.abspath(folder), "python", "python.exe"))
    assert command.endswith("--banner powershell; & " + python + " -I -B -X utf8 -m synthtwin doctor")
    calls: "list[tuple[object, dict[str, object]]]" = []

    def popen(arguments: object, **named: object) -> None:
        calls.append((arguments, named))

    home = tmp_path / "home"
    (home / "twin-work").mkdir(parents=True)
    environment = {"SystemRoot": "C:\\Windows", "USERPROFILE": str(home), "PATH": "C:\\Windows"}
    assert FOLDER.open_window(folder, environment, popen, answers=lambda: True) == []
    arguments, named = calls[-1]
    assert isinstance(arguments, list) and arguments[0].endswith("powershell.exe")
    assert arguments[1:5] == ["-NoLogo", "-NoProfile", "-NoExit", "-Command"]
    assert named["cwd"] == str(home / "twin-work") and named["creationflags"]
    assert FOLDER.open_window(folder, environment, popen, answers=lambda: False) == []
    line, named = calls[-1]
    launcher = os.path.join(os.path.abspath(folder), "synthtwin.bat")
    assert isinstance(line, str) and " /d /s /k \"title synthtwin & \"" in line and line.endswith('"' + launcher + '" doctor"')
    assert str(named["env"]["PATH"]).startswith(os.path.abspath(folder) + ";")  # type: ignore[index]
    shutil.rmtree(home / "twin-work")
    assert FOLDER.window_place(environment) == str(home), "never synthtwin's own folder"


def _commands(line: str) -> "list[str]":
    """The commands of the Command Prompt window's /k line, split at each & that stands outside quotes."""
    inner = line.split(" /d /s /k ", 1)[1]
    assert inner.startswith('"') and inner.endswith('"')
    parts, current, quoted = [], "", False
    for character in inner[1:-1]:
        if character == '"':
            quoted = not quoted
        if character == "&" and not quoted:
            parts += [current.strip()]
            current = ""
            continue
        current += character
    return parts + [current.strip()]


def test_the_command_prompt_window_runs_only_the_checked_launcher(tmp_path: pathlib.Path) -> None:
    """Codex's item 1 (HIGH), its first state: a stale synthtwin.exe in the work folder, PowerShell blocked.

    The window opens in that work folder, so every command of its line
    names its program by its full path (title is Command Prompt's own),
    the word synthtwin is bound to the folder's synthtwin.bat by a DOSKEY
    macro, and the window's environment keeps Command Prompt from
    searching the current folder at all.
    """
    folder = str(tmp_path / "Dr O'Brien files" / "synthtwin-0.0.1-win")
    home = tmp_path / "home"
    (home / "twin-work").mkdir(parents=True)
    (home / "twin-work" / "synthtwin.exe").write_bytes(b"MZ a stale or hostile program")
    calls: "list[tuple[object, dict[str, object]]]" = []

    def popen(arguments: object, **named: object) -> None:
        calls.append((arguments, named))

    environment = {"SystemRoot": "C:\\Windows", "USERPROFILE": str(home), "PATH": "C:\\Windows"}
    assert FOLDER.open_window(folder, environment, popen, answers=lambda: False) == []
    line, named = calls[-1]
    assert named["cwd"] == str(home / "twin-work"), "the window opens where the stale program sits"
    assert str(named["executable"]).endswith(os.path.join("System32", "cmd.exe"))
    launcher = os.path.join(os.path.abspath(folder), "synthtwin.bat")
    commands = _commands(str(line))
    assert commands[0] == "title synthtwin"
    for command in commands[1:]:
        program = command.split('"')[1] if command.startswith('"') else command.split()[0]
        assert command.startswith('"') and (os.path.isabs(program) or program.startswith("C:\\")), command
    doskey = os.path.join("C:\\Windows", "System32", "doskey.exe")
    assert commands[1] == '"' + doskey + '" synthtwin="' + launcher + '" $*', "the word bound to the checked launcher"
    assert commands[-1] == '"' + launcher + '" doctor', "the computer check runs the checked launcher by its path"
    given = named["env"]
    assert isinstance(given, dict) and given["NoDefaultCurrentDirectoryInExePath"] == "1"
    assert str(given["PATH"]).startswith(os.path.abspath(folder) + ";")
    assert FOLDER.cmd_environment(folder, environment)["NoDefaultCurrentDirectoryInExePath"] == "1"


def test_command_prompt_opens_when_the_powershell_window_will_not(tmp_path: pathlib.Path) -> None:
    """The verify's carry C3: PowerShell's probe answers, its window will not open, Command Prompt opens instead."""
    folder = str(tmp_path / "synthtwin-0.0.1-win")
    calls: "list[object]" = []

    def popen(arguments: object, **named: object) -> None:
        calls.append(arguments)
        if isinstance(arguments, list) and str(arguments[0]).endswith("powershell.exe"):
            raise OSError(5, "Access is denied")

    environment = {"SystemRoot": "C:\\Windows", "USERPROFILE": str(tmp_path), "PATH": "C:\\Windows"}
    assert FOLDER.open_window(folder, environment, popen, answers=lambda: True) == []
    assert len(calls) == 2 and isinstance(calls[0], list) and isinstance(calls[1], str)
    assert calls[1].endswith('synthtwin.bat" doctor"')


# -- the launchers and the guide ---------------------------------------------------


# Every line of each launcher that does something (all but rem lines,
# @echo off and setlocal), in order: nothing runs before the check, and
# nothing runs the folder's Python without -I -B.
LAUNCHER_LINES = {
    "START-HERE.bat": [
        'if exist "%~dp0python\\python.exe" goto check',
        "echo Unzip synthtwin's zip first (right-click it, Extract All), then double-click START-HERE in the unzipped folder.",
        'if /i not "%~1"=="/check" pause',
        "exit /b 1",
        ":check",
        '"%~dp0python\\python.exe" -I -B "%~dp0scripts\\check_folder.py" --start "%~dp0." %1',
        'set "STATUS=%ERRORLEVEL%"',
        'if not "%STATUS%"=="0" if /i not "%~1"=="/check" pause',
        "exit /b %STATUS%",
    ],
    "synthtwin.bat": [
        '"%~dp0python\\python.exe" -I -B -X utf8 -m synthtwin %*',
        "exit /b %ERRORLEVEL%",
    ],
}


def test_the_launchers_are_crlf_and_run_the_folder_python() -> None:
    for name in ("START-HERE.bat", "synthtwin.bat", "INSTALL-WINDOWS.txt"):
        data = (WINDOWS / name).read_bytes()
        assert b"\r\n" in data and b"\n" not in data.replace(b"\r\n", b""), f"{name} is not CRLF throughout"
    for name, expected in LAUNCHER_LINES.items():
        lines = (WINDOWS / name).read_bytes().decode("ascii").split("\r\n")
        acting = [line for line in lines if line and line != "@echo off" and line != "setlocal" and not line.startswith("rem ")]
        assert acting == expected, (name, acting)


def test_start_here_turns_away_a_dropped_file_in_plain_words(tmp_path: pathlib.Path, capsys) -> None:
    folder = _folder(tmp_path)
    opened: "list[str]" = []
    assert FOLDER.main(["--start", str(folder), "C:\\Users\\me\\twin-work\\my-table.csv"], opener=opened.append) == 2
    said = capsys.readouterr().out
    assert "START-HERE takes no file: double-click it, then type synthtwin's commands in the window it opens" in said
    assert opened == [] and "Give synthtwin's folder" not in said


def test_the_check_says_how_many_seconds_it_took(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:
    folder = _folder(tmp_path)
    real = FOLDER.check
    monkeypatch.setattr(FOLDER, "check", lambda place: real(place, system="win32", environment={}))
    assert FOLDER.main([str(folder)]) == 0
    said = capsys.readouterr().out
    assert "this can take a minute or more; the window prints how many seconds it took" in said
    assert re.search(r"The check took \d+\.\d s\.", said) and "match their hashes in SHA256SUMS" in said
    (folder / "python" / "python.exe").write_bytes(b"MZ changed")
    assert FOLDER.main([str(folder)]) == 1
    assert re.search(r"The check took \d+\.\d s\.", capsys.readouterr().out), "the seconds on a refusal too"


def test_the_guide_in_the_folder_is_plain() -> None:
    guide = (WINDOWS / "INSTALL-WINDOWS.txt").read_text(encoding="utf-8")
    flowing = " ".join(guide.split())
    for needed in (
        "Task Manager",
        "Ctrl+Z, then Enter",
        "do not click inside the window",
        "Only the description",
        "START-HERE",
        "twin-work",
        "Get-FileHash",
        "C:\\Program Files",
        "opens no network connection",
        "writes no registry key",
        "Extract All writes about 8,400 files and can take several minutes",
        "this can take a minute or more; the window prints how many seconds it took",
        "If it says to unzip the zip first",
        "What it writes. synthtwin writes only beside the table the person names, in the folder given with --out-dir",
        "Only the description, my-table-profile.json, and only after your institution's approval",
        "FIRST, CHECK THE ZIP (before you unzip it)",
        "Get-FileHash -Algorithm SHA256 .\\synthtwin-*-windows-ready.zip",
        "The trusted start.",
    ):
        assert needed in flowing, needed
    assert flowing.index("FIRST, CHECK THE ZIP") < flowing.index("BEFORE YOU START"), "the zip is checked first"
    assert "up to a minute" not in flowing and "Nothing else on the computer was changed" not in flowing
    physician = guide[: guide.index("\nFOR IT\n")]
    for jargon in ("pip", "venv", "wheel"):
        assert not re.search(rf"\b{jargon}\b", physician, re.I), jargon


def test_the_how_to_says_only_what_is_true() -> None:
    """docs/windows-install.md: the path budget's arithmetic, the first run owed, one file leaving, one write paragraph."""
    page = " ".join((REPO / "docs" / "windows-install.md").read_text(encoding="utf-8").split())
    for needed in (
        "Windows refuses file paths of 260 characters or more",
        "any place of up to 99 characters (100 with its separator)",
        "Extract All writes about 8,400 files and can take several minutes",
        "This can take a minute or more",
        "the window prints how many seconds it took",
        "Its first run is owed to the push that carries it; STATE names the first green run.",
        "**Only the description, `my-table-profile.json`, and only after your institution's approval.**",
        "**What it writes.** synthtwin writes only beside the table the person names",
        "It keeps no history of what you type (not yet measured on Windows)",
        "START-HERE takes no file",
        "Unzip synthtwin's zip first",
    ):
        assert needed in page, needed
    for gone in ("longer than 260", "up to 100 characters", "up to a minute", "under the same approval",
                 "leaves nothing behind", "Nothing else was changed", "nothing else on the computer changes"):
        assert gone not in page, gone


def _decision(number: str) -> str:
    """One decision of the plan of record, from its heading to the next one."""
    plan = (REPO / "docs" / "plans" / "phase-4-columns.md").read_text(encoding="utf-8")
    start = plan.index(f"## Decision {number} ")
    end = plan.find("\n## ", start + 1)
    return plan[start : end if end > 0 else len(plan)]


def test_the_integrity_claim_is_stated_honestly() -> None:
    """Codex's item 7: the folder's own check runs after the code it checks, and every page says so.

    No page says the check runs "before anything runs"; both guides check
    the zip first, with Windows' own Get-FileHash against a SHA-256 from
    outside the zip, and state in plain words what the folder's check
    guards against and what it cannot.
    """
    pages = {
        name: (REPO / name).read_text(encoding="utf-8")
        for name in (
            "scripts/windows/START-HERE.bat",
            "scripts/windows/INSTALL-WINDOWS.txt",
            "docs/windows-install.md",
            "SECURITY.md",
            "tools/bundle/check_folder.py",
            "tools/bundle/rehearse_windows.py",
            ".github/workflows/windows-bundle.yml",
        )
    }
    pages["P4-D483"] = _decision("P4-D483")
    for name, text in pages.items():
        flowing = " ".join(text.split())
        assert "before anything runs" not in flowing and "before anything ran" not in flowing, name
    for name in ("scripts/windows/INSTALL-WINDOWS.txt", "docs/windows-install.md"):
        flowing = " ".join(pages[name].split())
        assert "Get-FileHash -Algorithm SHA256 .\\synthtwin-*-windows-ready.zip" in flowing, name
        assert "the folder's own Python and the check itself run before any file is compared" in flowing, name
        assert "damaged on its way or changed by accident" in flowing, name
    for name in ("SECURITY.md", "P4-D483", "tools/bundle/check_folder.py"):
        assert "changed on purpose" in " ".join(pages[name].split()), name


def test_the_recovery_without_command_prompt_runs_the_check_first() -> None:
    """Codex's item 6: where Command Prompt is disabled, the how-to's one line runs the check, then opens synthtwin.

    `--start` opens the window only when the folder passed (the case of
    START-HERE's own call above), and no line of the how-to starts
    synthtwin from the folder's python.exe without the check.
    """
    page = (REPO / "docs" / "windows-install.md").read_text(encoding="utf-8")
    line = (
        "& 'C:\\synthtwin-0.1.0-win\\python\\python.exe' -I -B "
        "'C:\\synthtwin-0.1.0-win\\scripts\\check_folder.py' --start 'C:\\synthtwin-0.1.0-win'"
    )
    assert line in page
    assert not re.search(r"python\.exe'?\s+-I -B -X utf8 -m synthtwin", page), "a line starts synthtwin unchecked"


# -- windows_python.py, fill_answers.py, guard_run.py -------------------------------


def test_the_python_addresses() -> None:
    assert PYTHON.urls(RELEASE) == (
        "https://www.python.org/ftp/python/3.14.9/python-3.14.9-embed-amd64.zip",
        "https://www.python.org/ftp/python/3.14.9/python-3.14.9-amd64.exe",
    )
    with pytest.raises(ValueError):
        PYTHON.urls("3.13.9")


def test_the_release_while_nothing_is_pinned(monkeypatch) -> None:
    """Codex's item 8, one state of two, set here whatever the file holds: no pin, the builder's own 3.14."""
    monkeypatch.setattr(PYTHON, "PINNED", None)
    with pytest.raises(ValueError, match="with Python 3.14"):
        PYTHON.version((3, 11, 15))
    assert PYTHON.version((3, 14, 2)) == ("3.14.2", False)


def test_the_release_once_the_pin_is_committed(monkeypatch) -> None:
    """The other state: a committed pin is the release, whatever Python builds, so committing it breaks no case."""
    monkeypatch.setattr(PYTHON, "PINNED", {"version": "3.14.7", "embeddable": "1" * 64, "installer": "2" * 64})
    assert PYTHON.version((3, 11, 15)) == ("3.14.7", True)
    assert PYTHON.version((3, 14, 2)) == ("3.14.7", True)


def test_the_pin_holds_both_files_once_committed(tmp_path: pathlib.Path, monkeypatch) -> None:
    embeddable = _embeddable(tmp_path)
    installer = tmp_path / PYTHON.INSTALLER.format(version=RELEASE)
    installer.write_bytes(b"installer")
    monkeypatch.setattr(PYTHON, "PINNED", None)
    problems, lines = PYTHON.check(embeddable, installer, RELEASE)
    assert problems == [] and any("UNPINNED" in line for line in lines)
    monkeypatch.setattr(PYTHON, "PINNED", {"version": RELEASE, "embeddable": "0" * 64, "installer": _sha256(installer)})
    problems, lines = PYTHON.check(embeddable, installer, RELEASE)
    assert len(problems) == 1 and "the embeddable has SHA-256" in problems[0] and not any("UNPINNED" in line for line in lines)
    monkeypatch.setattr(PYTHON, "PINNED", {"version": RELEASE, "embeddable": _sha256(embeddable), "installer": _sha256(installer)})
    assert PYTHON.check(embeddable, installer, RELEASE)[0] == []


def test_every_program_file_must_be_signed_by_an_allowed_signer() -> None:
    psf = "CN=Python Software Foundation, O=Python Software Foundation, L=Beaverton, S=Oregon, C=US"
    microsoft = "CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US"
    records = [
        {"Path": "C:\\x\\python.exe", "Status": "Valid", "Signer": psf},
        {"Path": "C:\\x\\python314.dll", "Status": "Valid", "Signer": psf},
        {"Path": "C:\\x\\vcruntime140.dll", "Status": "Valid", "Signer": microsoft},
        {"Path": "C:\\x\\python-3.14.9-amd64.exe", "Status": "Valid", "Signer": psf},
        {"Path": "C:\\x\\vcruntime140_1.dll", "Status": "Valid", "Signer": "CN=Microsoft Windows Software Compatibility Publisher, O=Microsoft Corporation, L=Redmond, S=Washington, C=US"},
    ]
    expected = ["python.exe", "python314.dll", "python-3.14.9-amd64.exe"]
    assert PYTHON.signature_problems(records, expected) == []
    unsigned = records + [{"Path": "C:\\x\\_socket.pyd", "Status": "NotSigned", "Signer": ""}]
    assert "the signature is NotSigned" in " ".join(PYTHON.signature_problems(unsigned, expected))
    stranger = records + [{"Path": "C:\\x\\a.dll", "Status": "Valid", "Signer": "CN=Someone Else"}]
    assert "signed by 'Someone Else'" in " ".join(PYTHON.signature_problems(stranger, expected))
    assert "python.exe was not among" in " ".join(PYTHON.signature_problems(records[1:], expected))


def _questions(asked: "list[tuple[str, list[str]]]", before: "list[tuple[str, str]]" = ()) -> "dict[str, object]":  # type: ignore[assignment]
    return {
        "asked": [
            {"column": column, "your_answer": "", "answers_you_can_give": [{"answer": word} for word in offered]}
            for column, offered in asked
        ],
        "answered_before": [{"column": column, "your_answer": answer} for column, answer in before],
        "checklist": {"columns": [{"column": "result", "your_answer": "", "answers_you_can_give": [{"answer": "code"}]}]},
    }


def test_the_answers_are_written_round_after_round(tmp_path: pathlib.Path) -> None:
    preferred = ANSWERS.preferences(["code=code,no", "age=years", "weight=no"])
    first = _questions([("code", ["measurement", "code", "identifier"]), ("age", ["no", "yes", "years"])])
    chosen, problems = ANSWERS.choose(first, preferred)
    assert problems == [] and chosen == [("code", "code"), ("age", "years")]
    assert first["checklist"]["columns"][0]["your_answer"] == "", "the checklist is left as it is"  # type: ignore[index]
    second = _questions([("code", ["no", "yes"])], [("code", "code"), ("age", "years")])
    assert ANSWERS.choose(second, preferred)[0] == [("code", "no")]
    unforeseen = _questions([("visit_date", ["date", "count"])])
    assert "the question about 'visit_date'" in ANSWERS.choose(unforeseen, preferred)[1][0]
    done = _questions([], [("code", "code"), ("age", "years"), ("code", "no")])
    assert ANSWERS.settled(done, [("code", "code"), ("age", "years"), ("code", "no")]) == []
    assert ANSWERS.settled(done, [("weight", "no")]) == ["the answer 'no' about 'weight' is not kept among answered_before"]
    assert ANSWERS.settled(_questions([("code", ["no", "yes"])]), []) == ["the question about 'code' is still open"]
    plain = tmp_path / "answers.txt"
    ANSWERS.write_plain(plain, chosen)
    assert plain.read_bytes() == b"code = code\r\nage = years\r\n"
    questions = tmp_path / "my-table-questions.json"
    questions.write_text(json.dumps(_questions([("code", ["measurement", "code"])])), encoding="utf-8", newline="\n")
    assert ANSWERS.main(["json", str(questions), "code=code"]) == 0
    assert json.loads(questions.read_text(encoding="utf-8"))["asked"][0]["your_answer"] == "code"


# What the in-process guard must refuse, named here rather than read from
# the guard, so a name the guard drops is missed here: the socket class,
# every connection and name lookup, and every way to start a program.
REFUSED = [(socket, "socket"), (subprocess, "Popen")]
REFUSED += [
    (socket, name)
    for name in ("create_connection", "getaddrinfo", "gethostbyname", "gethostbyname_ex", "gethostbyaddr", "getnameinfo")
]
REFUSED += [
    (os, name)
    for name in ("system", "popen", "startfile", "spawnv", "spawnve", "spawnvp", "spawnvpe", "execv", "execve",
                 "posix_spawn", "posix_spawnp", "fork", "forkpty")
    if hasattr(os, name)
]


def _guarded(monkeypatch) -> None:
    """Put back, after the case, everything the guard replaces, and start with no attempt recorded."""
    for module, name in REFUSED + GUARD.patched():
        monkeypatch.setattr(module, name, getattr(module, name))
    monkeypatch.setattr(GUARD, "ATTEMPTS", [])


def test_the_in_process_guard_refuses_every_network_call(monkeypatch, capsys) -> None:
    _guarded(monkeypatch)
    assert GUARD.prove() == 0
    said = capsys.readouterr()
    assert said.out.count("the guard stopped it") == 6 and "the guard recorded 6 attempts" in said.out
    assert said.err.count("guard_run: ") == 6, "each attempt printed the moment it was made"
    with pytest.raises(GUARD.NetworkAttempt):
        socket.getaddrinfo("example.com", 443)
    assert isinstance(socket.socket, type), "still a class, so the standard library's ssl can subclass it"
    assert issubclass(subprocess.Popen, GUARD._RefusedPopen.__mro__[1]), "still a subclass of the real Popen"


def test_the_proof_fails_when_an_attempt_goes_unrecorded(monkeypatch, capsys) -> None:
    """--prove reads the record as well as the stops: a guard that stops every try but keeps none fails it."""
    _guarded(monkeypatch)
    monkeypatch.setattr(GUARD, "_attempted", lambda name: f"stopped, not kept ({name})")
    assert GUARD.prove() == 1
    assert "the guard recorded 0 attempts for the 6 tries" in capsys.readouterr().out


def test_every_refused_call_raises_is_kept_and_is_printed_at_once(monkeypatch, capsys) -> None:
    """The unit sweep over every name: each refused before it can act, kept in ATTEMPTS, printed at once."""
    _guarded(monkeypatch)
    originals = {(module, name): getattr(module, name) for module, name in REFUSED}
    GUARD.apply()
    for (module, name), original in originals.items():
        replaced = getattr(module, name)
        # Checked before the call, so a name the guard leaves alone is
        # never called here (os.execv would replace this very process).
        assert replaced is not original, f"{module.__name__}.{name} is not refused"
        with pytest.raises(GUARD.NetworkAttempt):
            replaced("stand-in argument")
        label = f"{module.__name__}.{name}"
        assert GUARD.ATTEMPTS[-1] == label, (label, GUARD.ATTEMPTS)
        assert f"guard_run: {label} was attempted" in capsys.readouterr().err, label
    assert len(GUARD.ATTEMPTS) == len(REFUSED)


_STAND_IN = '''# A stand-in for code that tries the network and starts a program,
# catching each failure, as optional-feature and update-check code does.
import os
import socket
import subprocess
import sys
import urllib.request

for attempt in (
    lambda: urllib.request.build_opener(urllib.request.ProxyHandler({})).open("http://127.0.0.1:9/", timeout=1),
    lambda: socket.getaddrinfo("localhost", 9),
    lambda: subprocess.run([sys.executable, "-c", "pass"], check=False),
    lambda: os.system("exit 0"),
):
    try:
        attempt()
    except OSError:
        pass
print("the stand-in finished normally")
'''


def _run_guarded(monkeypatch, tmp_path: pathlib.Path, main_text: str, arguments: "list[str]") -> int:
    """guard_run.main over a stand-in synthtwin package; the real package's modules put back after."""
    package = tmp_path / "stand-in" / "synthtwin"
    package.mkdir(parents=True)
    (package / "__init__.py").write_bytes(b"")
    (package / "__main__.py").write_bytes(main_text.encode("utf-8"))
    monkeypatch.syspath_prepend(str(tmp_path / "stand-in"))
    monkeypatch.setattr(sys, "argv", list(sys.argv))
    saved = {name: module for name, module in sys.modules.items() if name.split(".")[0] == "synthtwin"}
    for name in saved:
        del sys.modules[name]
    try:
        return GUARD.main(arguments)
    finally:
        for name in [name for name in sys.modules if name.split(".")[0] == "synthtwin"]:
            del sys.modules[name]
        sys.modules.update(saved)


def test_a_swallowed_attempt_still_fails_the_guarded_run(monkeypatch, tmp_path: pathlib.Path, capsys) -> None:
    """The skeptic's stand-in: every attempt caught by its caller, and the run still exits 3, naming each."""
    _guarded(monkeypatch)
    assert _run_guarded(monkeypatch, tmp_path, _STAND_IN, ["doctor"]) == 3
    said = capsys.readouterr()
    assert "the stand-in finished normally" in said.out
    for label in ("socket.create_connection", "socket.getaddrinfo", "subprocess.Popen", "os.system"):
        assert label in GUARD.ATTEMPTS and f"guard_run: {label} was attempted" in said.err, label
    assert "the run fails with exit 3, whatever synthtwin's own exit status (0)" in said.err


def test_a_run_that_tries_nothing_keeps_its_own_status(monkeypatch, tmp_path: pathlib.Path) -> None:
    _guarded(monkeypatch)
    quiet = "import sys\nsys.exit(int(sys.argv[1]))\n"
    assert _run_guarded(monkeypatch, tmp_path / "zero", quiet, ["0"]) == 0
    assert _run_guarded(monkeypatch, tmp_path / "two", quiet, ["2"]) == 2
    assert GUARD.ATTEMPTS == []


def test_the_firewall_proof_fails_when_a_host_is_reached(capsys) -> None:
    class Opened:
        def close(self) -> None:
            pass

    def refuse(address: object, timeout: float) -> object:
        raise PermissionError(10013, "forbidden by its access permissions")

    assert GUARD.denied(refuse) == 0
    assert GUARD.denied(lambda address, timeout: Opened()) == 1
    assert "the network is NOT denied" in capsys.readouterr().out


def _failing(error: OSError, only: "str | None" = None):  # type: ignore[no-untyped-def]
    """A connect stand-in that fails with ``error`` (for ``only`` host, else for every host); the rest refused by policy."""

    def connect(address: "tuple[str, int]", timeout: float) -> object:
        if only is None or address[0] == only:
            raise error
        raise PermissionError(10013, "forbidden by its access permissions")

    return connect


def _winerror(code: int) -> OSError:
    error = OSError(code, "a Windows socket error")
    error.winerror = code  # type: ignore[attr-defined]
    return error


@pytest.mark.parametrize(
    "error, only",
    [
        (socket.gaierror(11001, "getaddrinfo failed"), None),
        (TimeoutError("timed out"), None),
        (ConnectionRefusedError(10061, "refused by the far end"), None),
        (socket.gaierror(11001, "getaddrinfo failed"), "github.com"),
        (TimeoutError("timed out"), "pypi.org"),
        (_winerror(10060), None),
    ],
)
def test_a_failure_other_than_the_rules_refusal_leaves_the_proof_inconclusive(error: OSError, only: "str | None", capsys) -> None:
    """Codex's item 4: a failed name lookup or a timeout on a host proves nothing about the rule, so the proof fails."""
    assert GUARD.denied(_failing(error, only)) == 2
    said = capsys.readouterr().out
    assert "INCONCLUSIVE" in said and "not with the rule's access-denied refusal" in said


def test_the_rules_refusal_is_read_by_its_windows_code_too(capsys) -> None:
    """WinError 10013 on a plain OSError counts as the rule's refusal, as a PermissionError does."""
    assert GUARD.refused_by_policy(_winerror(10013)) and GUARD.refused_by_policy(PermissionError(13, "denied"))
    assert not GUARD.refused_by_policy(_winerror(10060)) and not GUARD.refused_by_policy(TimeoutError("timed out"))
    assert GUARD.denied(_failing(_winerror(10013))) == 0
    assert capsys.readouterr().out.count("refused by the rule, as it should be") == 2


# -- rehearse_windows.py ---------------------------------------------------------------


def test_each_route_types_what_a_person_types(tmp_path: pathlib.Path) -> None:
    folder = tmp_path / "Dr O'Brien files" / "synthtwin-0.0.1-win"
    (folder / "scripts").mkdir(parents=True)
    shutil.copyfile(REPO / "tools" / "bundle" / "check_folder.py", folder / "scripts" / "check_folder.py")
    words = ["profile", "my table.csv", "--identifier", "subject_id"]
    shell = REHEARSE.Route("powershell", folder).command(words, into="screen.txt")
    assert isinstance(shell, list) and shell[1:5] == ["-NoLogo", "-NoProfile", "-NonInteractive", "-Command"]
    assert shell[5].startswith(FOLDER.powershell_function(str(folder)) + "; synthtwin profile 'my table.csv' --identifier subject_id > screen.txt")
    assert shell[5].endswith("exit $LASTEXITCODE")
    line = REHEARSE.Route("cmd", folder).command(words)
    assert isinstance(line, str) and line.endswith(' /d /s /c "synthtwin profile "my table.csv" --identifier subject_id"')
    assert REHEARSE.Route("cmd", folder).environment()["PATH"].startswith(str(folder) + ";")
    guarded = REHEARSE.Route("guard", folder).command(words)
    assert guarded[:5] == [str(folder / "python" / "python.exe"), "-I", "-B", "-X", "utf8"] and guarded[5].endswith("guard_run.py")
    # Codex's item 3: the backup's trial runs under the guard too, by its own .venv python.
    backup = REHEARSE.Route("guard", python="venv-python").command(words)
    assert backup[0] == "venv-python" and backup[1].endswith("guard_run.py") and backup[2:] == words
    assert REHEARSE.Route("direct", python="py").command(words)[:3] == ["py", "-m", "synthtwin"]
    assert REHEARSE.Route("direct", python="py").environment()["HTTPS_PROXY"] == "http://127.0.0.1:9"
    windowed = REHEARSE.Route("cmd", folder).environment()
    assert windowed["NoDefaultCurrentDirectoryInExePath"] == "1", "the window's own environment, from the folder's check"
    for incomplete in (("cmd",), ("guard",)):
        with pytest.raises(ValueError):
            REHEARSE.Route(*incomplete)


def test_the_trial_reads_the_run_it_judges(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "source"
    (source / "src" / "synthtwin").mkdir(parents=True)
    (source / "src" / "synthtwin" / "cli.py").write_text('OPTIONS = (\n    "--identifier",\n)\n', encoding="utf-8", newline="\n")
    assert REHEARSE.person_option(source) == "--identifier"
    (source / "src" / "synthtwin" / "cli.py").write_text('OPTIONS = (\n    "--person",\n)\n', encoding="utf-8", newline="\n")
    assert REHEARSE.person_option(source) == "--person"
    assert REHEARSE.people_counted({"columns": [{"name": "a"}, {"time_grain": {"people": 1000}}]}) == [1000]
    verdict = "     309  HELD -- the exact obligation was met\n       0  MISSED -- set by the description\n"
    assert REHEARSE.missed(verdict) == 0 and REHEARSE.missed("no verdict") is None
    work = tmp_path / "work"
    work.mkdir()
    assert "visits-profile.json was not written beside the table" in " ".join(REHEARSE.outcome_problems(work, "visits"))
    with open(work / "visits-twin.csv", "w", encoding="utf-8-sig", newline="") as handle:
        out = csv.writer(handle, lineterminator="\r\n")
        out.writerow(["subject_id", "age"])
        out.writerows([f"S{index % 1000:05d}", "40"] for index in range(2000))
    for name in REHEARSE.OUTPUTS:
        if not (work / name.format(stem="visits")).exists():
            (work / name.format(stem="visits")).write_text("", encoding="utf-8", newline="\n")
    (work / "visits-profile.json").write_text(json.dumps({"columns": [{"time_grain": {"people": 1000}}]}), encoding="utf-8", newline="\n")
    (work / "visits-twin-quality.txt").write_text(verdict, encoding="utf-8", newline="\n")
    assert REHEARSE.outcome_problems(work, "visits") == []
    (work / "visits-twin-quality.txt").write_text(verdict.replace("     0  MISSED", "     2  MISSED"), encoding="utf-8", newline="\n")
    assert REHEARSE.outcome_problems(work, "visits") == ["visits: the verdict's missed obligations read 2, not 0"]
    other = tmp_path / "other"
    shutil.copytree(work, other)
    assert REHEARSE.compare(work, other, ("visits",)) == []
    (other / "visits-twin.csv").write_bytes(b"changed")
    assert REHEARSE.compare(work, other, ("visits",), REHEARSE.HELD) == ["visits-twin.csv differs"]
    (source / "src" / "synthtwin" / "contract.py").write_bytes(b"def read():\n    return 1\n")
    assert not REHEARSE.plain_answers_read(source), "a tree without the plain-text answers"
    (source / "src" / "synthtwin" / "contract.py").write_bytes(b"def _answers_written_as_lines(text):\n    return text\n")
    assert REHEARSE.plain_answers_read(source), "a tree with them"


def _full_run(work: pathlib.Path, people: int = 1000, twin_people: int = 1000) -> pathlib.Path:
    """The six files a full run of visits.csv writes, small, as synthtwin writes them."""
    work.mkdir(parents=True)
    with open(work / "visits-twin.csv", "w", encoding="utf-8-sig", newline="") as handle:
        out = csv.writer(handle, lineterminator="\r\n")
        out.writerow(["subject_id", "age"])
        out.writerows([f"S{index % twin_people:05d}", "40"] for index in range(2 * twin_people))
    for name in REHEARSE.OUTPUTS:
        (work / name.format(stem="visits")).touch()
    (work / "visits-profile.json").write_bytes(json.dumps({"columns": [{"time_grain": {"people": people}}]}).encode())
    (work / "visits-twin-quality.txt").write_bytes(b"     309  HELD -- met\n       0  MISSED -- set by the description\n")
    return work


def test_the_verdict_holds_the_people_counted_and_in_the_twin(tmp_path: pathlib.Path) -> None:
    assert REHEARSE.outcome_problems(_full_run(tmp_path / "all"), "visits") == []
    fewer = _full_run(tmp_path / "fewer", people=999)
    assert REHEARSE.outcome_problems(fewer, "visits") == ["visits: synthtwin's people counts read [999], not 1000"]
    thinner = _full_run(tmp_path / "thinner", twin_people=999)
    assert REHEARSE.outcome_problems(thinner, "visits") == ["visits: the twin holds 999 people, not 1000"]


def test_an_asserted_comparison_fails_on_a_held_file_that_differs(tmp_path: pathlib.Path) -> None:
    first, second = _full_run(tmp_path / "one"), _full_run(tmp_path / "two")
    held = ["compare", "--assert", str(first), str(second), "--stems", "visits"]
    assert REHEARSE.main(held) == 0
    (second / "visits-profile.txt").write_bytes(b"the same description in other words")
    assert REHEARSE.main(held) == 0, "only the description and the twin are held"
    (second / "visits-twin.csv").write_bytes(b"changed")
    assert REHEARSE.main(held) == 1
    assert REHEARSE.main(["compare", "--report", str(first), str(second), "--stems", "visits"]) == 0, "reported, not held"


def _answering(monkeypatch, status: int, said: bytes = b"", writes: "tuple[str, ...]" = ()) -> "list[dict[str, object]]":
    """subprocess.run stood in for: each call writes ``writes`` where it runs and answers ``status`` and ``said``."""
    calls: "list[dict[str, object]]" = []

    def run(command: object, **named: object) -> "subprocess.CompletedProcess[bytes]":
        nonlocal calls
        place = pathlib.Path(str(named["cwd"]))
        calls += [{"command": command, "present": sorted(path.name for path in place.iterdir())}]
        for name in writes:
            (place / name).write_bytes(b"")
        return subprocess.CompletedProcess(command, status, said, b"")

    monkeypatch.setattr(REHEARSE.subprocess, "run", run)
    return calls


def test_the_redirected_run_passes_only_with_all_three_description_files(tmp_path: pathlib.Path, monkeypatch) -> None:
    tables = tmp_path / "tables"
    tables.mkdir()
    (tables / "visits.csv").write_bytes(b"subject_id\r\nS00001\r\n")
    words = ["redirect", "--route", "direct", "--python", "py", "--work", str(tmp_path / "work"), "--tables", str(tables)]
    three = ("visits-profile.json", "visits-profile.txt", "visits-questions.json")
    _answering(monkeypatch, 0, writes=three[:2])
    assert REHEARSE.main(words + ["--expect", "pass"]) == 1, "two of the three files"
    assert REHEARSE.main(words + ["--expect", "record"]) == 0, "recorded, not held"
    _answering(monkeypatch, 0, writes=three)
    assert REHEARSE.main(words + ["--expect", "pass"]) == 0
    _answering(monkeypatch, 1, writes=three)
    assert REHEARSE.main(words + ["--expect", "pass"]) == 1, "a run that exits 1"


def test_a_changed_copy_must_be_refused_by_its_status_and_its_words(tmp_path: pathlib.Path, monkeypatch) -> None:
    folder = tmp_path / "ready" / "synthtwin-0.0.1-win"
    library = folder / "python" / "lib" / "numpy" / "__init__.py"
    library.parent.mkdir(parents=True)
    library.write_bytes(b"x = 1\n" * 10)
    (folder / "START-HERE.bat").write_bytes(b"@echo off\r\n")
    refusal = b"synthtwin did not start: python/lib/numpy/__init__.py does not match its hash in SHA256SUMS"
    _answering(monkeypatch, 0, refusal)
    assert REHEARSE.tamper(folder, tmp_path / "copies") == ["START-HERE.bat ran a copy with a changed library file"]
    changed = (tmp_path / "copies" / folder.name / "python" / "lib" / "numpy" / "__init__.py").read_bytes()
    assert library.read_bytes() == b"x = 1\n" * 10 and sum(a != b for a, b in zip(changed, library.read_bytes())) == 1
    _answering(monkeypatch, 1, refusal)
    assert REHEARSE.tamper(folder, tmp_path / "copies") == []
    _answering(monkeypatch, 1, b"synthtwin did not start: something else")
    assert REHEARSE.tamper(folder, tmp_path / "copies") == ["START-HERE.bat's refusal did not name the changed file's hash"]


def test_start_here_alone_in_a_folder_must_say_to_unzip_first(tmp_path: pathlib.Path, monkeypatch) -> None:
    folder = tmp_path / "ready" / "synthtwin-0.0.1-win"
    folder.mkdir(parents=True)
    shutil.copyfile(WINDOWS / "START-HERE.bat", folder / "START-HERE.bat")
    words = b"Unzip synthtwin's zip first (right-click it, Extract All), then double-click START-HERE in the unzipped folder."
    assert words.decode("ascii") in (WINDOWS / "START-HERE.bat").read_text(encoding="ascii")
    calls = _answering(monkeypatch, 1, words)
    assert REHEARSE.alone_check(folder) == []
    assert calls[0]["present"] == ["START-HERE.bat"] and str(calls[0]["command"]).endswith('START-HERE.bat" /check"')
    _answering(monkeypatch, 0, words)
    assert REHEARSE.alone_check(folder), "an exit 0 alone"
    _answering(monkeypatch, 1, b"'C:\\x\\python\\python.exe' is not recognized as an internal or external command")
    assert REHEARSE.alone_check(folder), "cmd's own words, not synthtwin's"


# -- the driver's verdicts, each held by its own case (the verify's FIX 2) --------------


def _person(
    monkeypatch, people: int = 1000, keep_open: bool = False, failing: str = "", twin: "bytes | None" = None
) -> "list[dict[str, object]]":
    """subprocess.run stood in for synthtwin on the direct route: each command writes what synthtwin writes.

    ``failing`` names the command that exits 1; ``keep_open`` leaves the
    question open after every answer; ``people`` is how many people the
    description counts and the twin holds; ``twin`` the twin's bytes.
    """
    calls: "list[dict[str, object]]" = []

    def run(command: object, **named: object) -> "subprocess.CompletedProcess[bytes]":
        nonlocal calls
        place = pathlib.Path(str(named["cwd"]))
        words = [str(word) for word in command[3:]] if isinstance(command, list) else []
        calls += [{"words": words, "present": sorted(path.name for path in place.iterdir()), "env": named.get("env")}]
        verb = words[0] if words else ""
        if verb == failing:
            return subprocess.CompletedProcess(command, 1, b"", b"")
        stem = words[1].split(".")[0].replace("-profile", "") if len(words) > 1 else ""
        if verb == "profile":
            answered = "--answers" in words and not keep_open
            asked = [] if answered else [{"column": "code", "your_answer": "", "answers_you_can_give": [{"answer": "code"}]}]
            before = [{"column": "code", "your_answer": "code"}] if answered else []
            (place / f"{stem}-questions.json").write_bytes(json.dumps({"asked": asked, "answered_before": before}).encode())
            (place / f"{stem}-profile.json").write_bytes(json.dumps({"columns": [{"time_grain": {"people": people}}]}).encode())
            (place / f"{stem}-profile.txt").write_bytes(b"the description in words")
        elif verb == "generate":
            rows = "".join(f"S{index % people:05d},40\r\n" for index in range(2 * people))
            (place / f"{stem}-twin.csv").write_bytes(twin if twin is not None else ("subject_id,age\r\n" + rows).encode())
        elif verb == "validate":
            (place / f"{stem}-twin-quality.txt").write_bytes(b"     309  HELD -- met\n       0  MISSED -- set by the description\n")
            (place / f"{stem}-twin-report.txt").write_bytes(b"the report")
        return subprocess.CompletedProcess(command, 0, b"", b"")

    monkeypatch.setattr(REHEARSE.subprocess, "run", run)
    return calls


def _tables(tmp_path: pathlib.Path) -> pathlib.Path:
    tables = tmp_path / "tables"
    tables.mkdir(parents=True)
    (tables / "visits.csv").write_bytes(b"subject_id,code\r\nS00001,00017\r\n")
    return tables


def test_a_full_trial_on_the_stand_in_passes(tmp_path: pathlib.Path, monkeypatch) -> None:
    """The stand-in writes what a passing run writes, so each case below changes one thing only."""
    _person(monkeypatch)
    done = REHEARSE.trial(REHEARSE.Route("direct", python="py"), tmp_path / "work", _tables(tmp_path), ("visits",))
    assert done.problems == [] and [step["exit"] for step in done.steps] == [0] * 6
    assert [str(step["typed"]).split()[1] for step in done.steps] == ["--version", "doctor", "profile", "profile", "generate", "validate"]
    # The answered round types the record's remedy, as its refusal teaches (batch 4y's fix round; mutant: the round
    # typed without it, the bundle trial refused at the first answered round with the patient layer on).
    assert str(done.steps[3]["typed"]).split()[-2:] == ["--replace", "--replace-description"], done.steps[3]["typed"]
    assert "--replace-description" not in str(done.steps[2]["typed"])


def test_a_command_that_fails_is_a_problem_of_the_trial(tmp_path: pathlib.Path, monkeypatch) -> None:
    """L09: doctor exits 1, the trial stops there and names the exit."""
    _person(monkeypatch, failing="doctor")
    done = REHEARSE.trial(REHEARSE.Route("direct", python="py"), tmp_path / "work", _tables(tmp_path), ("visits",))
    assert done.problems == ["synthtwin doctor visits.csv exited 1, not 0"], done.problems


def test_a_question_left_open_is_a_problem_of_the_trial(tmp_path: pathlib.Path, monkeypatch) -> None:
    """L10: the question stays open after every round of answers."""
    _person(monkeypatch, keep_open=True)
    done = REHEARSE.trial(REHEARSE.Route("direct", python="py"), tmp_path / "work", _tables(tmp_path), ("visits",))
    assert "the question about 'code' is still open" in done.problems, done.problems


def test_an_outcome_short_of_the_bar_is_a_problem_of_the_trial(tmp_path: pathlib.Path, monkeypatch) -> None:
    """L11: 999 people counted and in the twin."""
    _person(monkeypatch, people=999)
    done = REHEARSE.trial(REHEARSE.Route("direct", python="py"), tmp_path / "work", _tables(tmp_path), ("visits",))
    assert "visits: synthtwin's people counts read [999], not 1000" in done.problems, done.problems
    assert "visits: the twin holds 999 people, not 1000" in done.problems, done.problems


def test_the_windows_routes_plant_decoys_where_the_window_opens(tmp_path: pathlib.Path, monkeypatch) -> None:
    """Codex's item 1 rehearsed: programs named synthtwin sit in the work folder before the first command."""
    folder = tmp_path / "Dr O'Brien files" / "synthtwin-0.0.1-win"
    (folder / "scripts").mkdir(parents=True)
    shutil.copyfile(REPO / "tools" / "bundle" / "check_folder.py", folder / "scripts" / "check_folder.py")
    for kind in ("cmd", "powershell", "direct"):
        calls = _person(monkeypatch, failing="--version")
        route = REHEARSE.Route(kind, folder) if kind != "direct" else REHEARSE.Route(kind, python="py")
        REHEARSE.trial(route, tmp_path / kind, _tables(tmp_path / f"tables-{kind}"), ("visits",))
        decoys = {"synthtwin.bat", "synthtwin.cmd", "synthtwin.ps1"}
        if kind == "direct":
            assert not decoys & set(calls[0]["present"]), "no window, no decoy"  # type: ignore[arg-type]
            continue
        assert decoys <= set(calls[0]["present"]), (kind, calls[0]["present"])  # type: ignore[arg-type]
        assert all(b"DECOY: not synthtwin" in (tmp_path / kind / name).read_bytes() for name in decoys)
    assert REHEARSE.DECOYS["synthtwin.bat"].endswith(b"exit /b 9\r\n")


def test_again_holds_the_twin_to_the_other_systems(tmp_path: pathlib.Path, monkeypatch) -> None:
    """L05: a twin made here that differs from the other system's is a problem; the same twin is none."""
    source = _full_run(tmp_path / "windows")
    _person(monkeypatch, twin=b"subject_id,age\r\nother,1\r\n")
    assert REHEARSE.again("py", source, tmp_path / "again", ("visits",)) == ["visits-twin.csv differs"]
    _person(monkeypatch, twin=(source / "visits-twin.csv").read_bytes())
    assert REHEARSE.again("py", source, tmp_path / "again", ("visits",)) == []


def test_an_asserted_comparison_holds_the_description_as_well(tmp_path: pathlib.Path) -> None:
    """L02: the description is held across systems, not the twin alone."""
    first, second = _full_run(tmp_path / "one"), _full_run(tmp_path / "two")
    (second / "visits-profile.json").write_bytes(b'{"columns": []}')
    assert REHEARSE.main(["compare", "--assert", str(first), str(second), "--stems", "visits"]) == 1


def test_a_quality_file_without_its_verdict_is_a_problem(tmp_path: pathlib.Path) -> None:
    """L04: no verdict block reads as None, which is not 0."""
    work = _full_run(tmp_path / "work")
    (work / "visits-twin-quality.txt").write_bytes(b"a quality file whose verdict block is missing\n")
    assert REHEARSE.outcome_problems(work, "visits") == ["visits: the verdict's missed obligations read None, not 0"]


def test_start_here_check_must_pass_and_say_so(tmp_path: pathlib.Path, monkeypatch) -> None:
    """L06: START-HERE /check's exit and its words are both read."""
    folder = tmp_path / "synthtwin-0.0.1-win"
    folder.mkdir()
    words = b"synthtwin's files match their hashes in SHA256SUMS."
    _answering(monkeypatch, 0, words)
    assert REHEARSE.start_check(folder) == []
    _answering(monkeypatch, 1, words)
    assert REHEARSE.start_check(folder) == ["START-HERE.bat /check did not pass the folder as it was unzipped"]
    _answering(monkeypatch, 0, b"something else")
    assert REHEARSE.start_check(folder) == ["START-HERE.bat /check did not pass the folder as it was unzipped"]


def test_the_install_log_is_read_for_the_network(tmp_path: pathlib.Path) -> None:
    """L07: a line of pip reaching for the network is found, and the scan exits 1."""
    log = tmp_path / "install.log"
    log.write_bytes(b"Processing c:\\bundle\\wheelhouse\\six.whl\r\nDownloading x\r\nInstalled\r\n")
    assert REHEARSE.scan_log(log) == ["Downloading x"]
    assert REHEARSE.main(["scan-log", str(log)]) == 1
    log.write_bytes(b"Processing c:\\bundle\\wheelhouse\\six.whl\r\nInstalled\r\n")
    assert REHEARSE.scan_log(log) == [] and REHEARSE.main(["scan-log", str(log)]) == 0


def test_the_golden_tests_status_is_given_back(tmp_path: pathlib.Path, monkeypatch) -> None:
    """L08: golden returns what pytest returned."""
    _answering(monkeypatch, 4)
    assert REHEARSE.golden("py", tmp_path) == 4
    _answering(monkeypatch, 0)
    assert REHEARSE.golden("py", tmp_path) == 0


# -- the workflow's text ------------------------------------------------------------------

JOBS = {
    "wheel": ("ubuntu-latest", []),
    "build": ("windows-latest", ["wheel"]),
    "rehearse-ready": ("windows-latest", ["build"]),
    "rehearse-fallback": ("windows-latest", ["build"]),
    "compare": ("ubuntu-latest", ["wheel", "rehearse-ready", "rehearse-fallback"]),
    "compare-macos": ("macos-latest", ["wheel", "rehearse-ready"]),
    "keep": ("ubuntu-latest", ["build", "rehearse-ready", "rehearse-fallback", "compare", "compare-macos"]),
}
TRIGGER_PATHS = (
    "requirements-install.lock",
    "requirements-install.in",
    "pyproject.toml",
    '"src/synthtwin/**"',
    '"tools/bundle/**"',
    '"scripts/**"',
    ".github/workflows/windows-bundle.yml",
)
PUBLISHING = (
    "twine upload",
    "gh release",
    "gh-action-pypi-publish",
    "action-gh-release",
    "upload-release-asset",
    "contents: write",
    "id-token: write",
)
# What a rehearsal job may never do once its checkout and downloads are
# done: words read anywhere in a step, and short command names read as
# whole words.
FETCHING = (
    "pypi.org", "pythonhosted", "python.org", "pip download", "pip install", "curl", "Invoke-WebRequest",
    "setup-python", "Invoke-RestMethod", "Start-BitsTransfer", "WebClient",
)
FETCHING_WORDS = ("irm", "iwr", "wget", "git", "winget", "choco")
# The interpreter each rehearsal job rehearses, which every step after its denial runs.
REHEARSED = {
    "rehearse-ready": "(Join-Path $env:READY 'python\\python.exe')",
    "rehearse-fallback": "$env:BASE_PYTHON",
}
# The other interpreter a rehearsal job may hand a tool after its denial:
# the backup's own .venv python, which starts the rehearsed base one.
OTHER_PYTHONS = {"rehearse-fallback": ("(Join-Path $env:BUNDLE '.venv\\Scripts\\python.exe')",)}
# The one step of each rehearsal job that may carry an `if:` (the runs are
# uploaded for the comparison even when the job fails); no other step or
# job of the file may carry one.
KEPT_WITH_IF = "Keep the runs for the comparison (internal, one day)"
# What the backup's rehearsal must hold: the carried installer, run fresh
# (every registered 3.14 removed first, by its bundle or, for a part a
# runner image registers with no bundle above it, by the key it is
# registered under; the target and its log made by this run) and its
# log read for downloads; install.bat with the carried
# Python first on PATH and its log holding that Python's path; the trial
# directly and under the guard; the redirect recorded; the golden tests.
FALLBACK_LINES = (
    "InstallAllUsers=0",
    "Where-Object { $_.DisplayName -like 'Python 3.14*' -and $_.BundleCachePath }",
    "-ArgumentList @('/uninstall', '/quiet')",
    "-FilePath 'msiexec.exe' -Wait -PassThru -ArgumentList @('/x', $part.PSChildName, '/quiet', '/norestart')",
    "throw 'a Python 3.14 is still registered on this runner, so the carried installer would not install fresh'",
    "if ((Test-Path $target) -or (Test-Path $log)) { throw ",
    "if (-not (Test-Path $log)) { throw ",
    "$base = Join-Path $target 'python.exe'",
    "if (-not (Test-Path $base)) { ",
    "Select-String -Path $log -SimpleMatch -Pattern 'download from:', 'http'",
    "if ($fetched.Count -gt 0) { $fetched | ForEach-Object { $_.Line }; throw ",
    "$env:PATH = (Split-Path $env:BASE_PYTHON) + ';' + $env:PATH",
    "scripts\\install.bat",
    "scan-log",
    "-SimpleMatch -Pattern $env:BASE_PYTHON -Quiet)) { throw ",
    "trial --route direct",
    "trial --route guard --utf8-screen --python (Join-Path $env:BUNDLE '.venv\\Scripts\\python.exe')",
    "--expect record",
    "golden --python",
)


def _shapes(interpreter: str) -> "list[re.Pattern[str]]":
    """The only lines a run block may hold once its job's denial is proven.

    Each runs the rehearsed interpreter (``interpreter``, or `$python`,
    which may only be set to it) on one of the bundle's tools, or does
    no more than read a file, change a variable of the step or check an
    exit status; the backup's install.bat is the one other program.
    """
    own = r"(?:" + re.escape(interpreter) + r"|\$python)"
    literal = r"'[^'`$;|&]*'"
    token = r"(?:\(Join-Path \$env:[A-Z_]+ " + literal + r"\)|\$env:[A-Z_]+|\$python|[A-Za-z0-9_./\\:,=-]+)"
    temp = r"\(Join-Path \$env:RUNNER_TEMP " + literal + r"\)"
    proxy = r"\$env:(?:HTTP_PROXY|HTTPS_PROXY|ALL_PROXY) = 'http://127\.0\.0\.1:9'"
    return [
        re.compile(shape)
        for shape in (
            r"& " + own + r" -I -B tools/bundle/[a-z_]+\.py(?: " + token + r")*",
            r"\$python = " + re.escape(interpreter.strip("()")),
            r"if \(\$LASTEXITCODE -ne 0\) \{ exit \$LASTEXITCODE \}",
            r"\$status = \$LASTEXITCODE",
            r"if \(\$status -ne 0\) \{ exit \$status \}",
            r"\$env:PATH = \(Split-Path " + own + r"\) \+ ';' \+ \$env:PATH",
            proxy + r"(?:; " + proxy + r")*(?:; \$env:NO_PROXY = '')?",
            r"Push-Location \$env:[A-Z_]+",
            r"Pop-Location",
            r"Get-Content " + temp,
            r"if \(-not \(Select-String -Path " + temp + r" -SimpleMatch -Pattern \$env:[A-Z_]+ -Quiet\)\) \{ throw '[^']*' \}",
            r"& cmd\.exe /d /c 'scripts\\install\.bat' \*> " + temp,
            r"# .*",
        )
    ]


def _run_lines(step: str) -> "list[str]":
    """The non-blank lines a step's run block holds, stripped: those indented deeper than the step's keys.

    A key after the block (an `if:` or an `env:`, at the keys' depth)
    ends it, and is read as a key, not as a line the block runs.
    """
    if "\n        run: |\n" in step:
        found: "list[str]" = []
        for line in step.split("\n        run: |\n", 1)[1].splitlines():
            if line.strip() and not line.startswith(" " * 10):
                break
            if line.strip():
                found += [line.strip()]
        return found
    single = re.search(r"\n        run: (.+)", step)
    return [single.group(1).strip()] if single else []


def _job_keys(block: str) -> "list[str]":
    """The keys a job sets at its own depth (four spaces), over its whole block, wherever they stand."""
    return re.findall(r"(?m)^    ([a-z-]+)\s*:", block)


def _keys(block: str, indent: int) -> "list[str]":
    """The YAML keys set at ``indent`` spaces in a job's or a step's text, wherever they stand.

    A run block's lines sit deeper, so none of them is read as a key;
    a step's first key stands right after its dash.
    """
    found = re.findall(r"(?m)^" + " " * indent + r"([a-z-]+):", block)
    first = re.match(r"([a-z-]+):", block)
    return found + ([first.group(1)] if first else [])


def _steps(block: str) -> "list[str]":
    return block.split("\n      - ")[1:]


def _needs(block: str) -> "list[str]":
    found = re.search(r"\n    needs: (\[[^\]]*\]|\S+)\n", "\n" + block)
    if not found:
        return []
    return [word.strip() for word in found.group(1).strip("[]").split(",")]


def workflow_problems(text: str, ci: str) -> "list[str]":
    """Every way the workflow falls short of plan P4-D483 and LANE WIN RULINGS 1."""
    try:
        jobs = MODELS.jobs_of(text)
    except ValueError as error:
        return [f"the workflow does not parse: {error}"]
    problems: "list[str]" = []
    if set(jobs) != set(JOBS):
        problems += [f"the jobs read {sorted(jobs)}"]
    for name, (runner, needs) in JOBS.items():
        block = jobs.get(name, "")
        if f"\n    runs-on: {runner}\n" not in "\n" + block:
            problems += [f"{name} does not run on {runner}"]
        if sorted(_needs(block)) != sorted(needs):
            problems += [f"{name} needs {_needs(block)}, not {needs}"]
        if not re.search(r"\n    timeout-minutes: \d+\n", "\n" + block):
            problems += [f"{name} has no time limit"]
        if "permissions:" in block:
            problems += [f"{name} sets its own permissions"]
    head = text[: text.index("\njobs:\n")]
    if "\npermissions:\n  contents: read\n" not in head or head.count("permissions:") != 1:
        problems += ["the token is not read-only"]
    if "group: windows-bundle-${{ github.ref }}" not in head or "cancel-in-progress: true" not in head:
        problems += ["no concurrency per ref"]
    trigger = head[head.index("\non:\n") : head.index("\npermissions:")]
    paths = [line.strip()[2:] for line in trigger.splitlines() if line.startswith("      - ")]
    if tuple(paths) != TRIGGER_PATHS or "\n  workflow_dispatch:\n" not in trigger:
        problems += [f"the triggers read {paths}"]
    pinned = set(re.findall(r"uses: (\S+)", ci))
    for used in re.findall(r"uses: (\S+)", text):
        if not re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", used) or used not in pinned:
            problems += [f"an action not among ci.yml's four pins: {used}"]
    for word in PUBLISHING:
        if word in text:
            problems += [f"the workflow publishes ({word!r})"]
    for name, block in jobs.items():
        for step in _steps(block):
            if "uses: actions/upload-artifact@" not in step:
                continue
            kept = re.search(r"name: synthtwin-windows-(ready|fallback)", step)
            days = re.search(r"retention-days: (\d+)", step)
            # Only the keep job, which waits for every rehearsal, keeps a zip
            # under a kept name, and keeps it 90 days; every other upload is
            # internal and kept one day.
            wanted = "90" if kept and name == "keep" else "1"
            if kept and name != "keep":
                problems += [f"an upload of {name} uses a kept name outside the keep job: {kept.group(0)}"]
            if days is None or days.group(1) != wanted:
                problems += [f"an upload of {name} is kept {days.group(1) if days else 'the default'} days, not {wanted}"]
    keep = jobs.get("keep", "")
    for needed in ("steps.ready.outputs.artifact-url", "steps.fallback.outputs.artifact-url", '>> "$GITHUB_STEP_SUMMARY"', "sha256sum", "What to click"):
        if needed not in keep:
            problems += [f"the keep job's record lacks {needed!r}"]
    # A failure is never let through (RULING W1 (8): only rehearsed zips are
    # kept): no step or job carries on after an error, and no `if:` runs or
    # skips a step on its own terms, but each rehearsal job's upload of its
    # runs for the comparison.
    if re.search(r"(?m)^\s*(?:- )?continue-on-error\s*:", text):
        problems += ["the workflow lets a failure through (continue-on-error)"]
    if re.search(r"(?m)^\s*(?:- )?if\s*:", head):
        problems += ["the workflow's head carries an if:"]
    if head.split("\nenv:\n", 1)[-1].split("\n\n", 1)[0].rstrip("\n") != '  PIP_DISABLE_PIP_VERSION_CHECK: "1"':
        problems += ["the workflow's own environment holds more than pip's version check"]
    for name, block in jobs.items():
        # The job's own keys are read over its WHOLE block, wherever they
        # stand: a step's keys sit at eight spaces or after its dash, and a
        # run block's lines at ten or more, so neither is read as one.
        if "if" in _job_keys(block):
            problems += [f"{name} carries an if: of its own"]
        for step in _steps(block):
            title = re.search(r"(?m)^(?:        )?name: (.+)$", step)
            allowed = name in REHEARSED and title is not None and title.group(1) == KEPT_WITH_IF
            if "if" in _keys(step, 8) and not allowed:
                problems += [f"a step of {name} carries an if:: {step.splitlines()[0]}"]
    for name, interpreter in REHEARSED.items():
        block = jobs.get(name, "")
        steps = _steps(block)
        own = r"(?:" + re.escape(interpreter) + r"|\$python)"
        if "env" in _job_keys(block) or any("env" in _keys(step, 8) for step in steps):
            problems += [f"{name} sets an environment of its own, which could point it at another interpreter"]
        for step in steps[3:]:
            for word in FETCHING:
                if word in step:
                    problems += [f"{name} fetches after its downloads ({word!r})"]
            for found in re.findall(r"(?<![\w.-])(" + "|".join(FETCHING_WORDS) + r")(?![\w.-])", step, re.I):
                problems += [f"{name} fetches after its downloads ({found!r})"]
        places = {
            "proxied": [
                index for index, step in enumerate(steps)
                if any(re.fullmatch(r"& " + own + r" -I -B tools/bundle/guard_run\.py --proxied", line) for line in _run_lines(step))
            ],
            "denied": [
                index for index, step in enumerate(steps)
                if any(re.match(r"New-NetFirewallRule .* -Direction Outbound -Action Block -Program " + own + r"(?: |$)", line)
                       for line in _run_lines(step))
                and any(re.fullmatch(r"& " + own + r" -I -B tools/bundle/guard_run\.py --denied", line) for line in _run_lines(step))
                and "TcpClient" in step and step.index("New-NetFirewallRule") < step.index("guard_run.py --denied")
            ],
            "guard": [index for index, step in enumerate(steps) if "guard_run.py --prove" in step],
            "trial": [index for index, step in enumerate(steps) if "rehearse_windows.py trial" in step],
        }
        if any(not found for found in places.values()):
            problems += [f"{name} lacks a level of the denial or the trial, or a proof run by another interpreter: {places}"]
            continue
        if not places["proxied"][0] < places["denied"][0] < places["guard"][0] < places["trial"][0]:
            problems += [f"{name} does not prove each level of the denial before the trial: {places}"]
        # From the denial step on, that step included, every interpreter a
        # line names is the rehearsed one: `$python` may only be set to it,
        # and each --python and --folder a tool is handed is the rehearsed
        # interpreter or folder, never another path written out as a token.
        handed = {"--python": {interpreter, "$python", *OTHER_PYTHONS.get(name, ())}, "--folder": {"$env:READY"}}
        for step in steps[places["denied"][0] :]:
            for line in _run_lines(step):
                if re.match(r"\$\{?python\}?\s*=", line) and not re.fullmatch(r"\$python = " + re.escape(interpreter.strip("()")), line):
                    problems += [f"{name} sets $python to another interpreter from its denial on: {line}"]
                for flag, value in re.findall(r"(--python|--folder) (\([^()]*\)|\S+)", line):
                    if value not in handed[flag]:
                        problems += [f"{name} hands a tool {flag} {value} after its denial"]
        shapes = _shapes(interpreter)
        for step in steps[places["denied"][0] + 1 :]:
            if re.search(r"(?m)^\s*uses: ", step):
                if not re.search(r"(?m)^\s*uses: actions/upload-artifact@", step):
                    problems += [f"{name} fetches through an action after the denial: {step.splitlines()[0]}"]
                continue
            lines = _run_lines(step)
            strays = [line for line in lines if not any(shape.fullmatch(line) for shape in shapes)]
            if not lines or strays:
                problems += [f"{name} runs something else than its rehearsed interpreter after the denial: {strays or step.splitlines()[0]}"]
        if "-Name LongPathsEnabled -Value 0" not in jobs.get(name, ""):
            problems += [f"{name} does not turn long paths off"]
        if "Expand-Archive" not in jobs.get(name, "") or "\"Dr O'Brien files\"" not in jobs.get(name, "") or "('x' * (99 - $base.Length - 1))" not in jobs.get(name, ""):
            problems += [f"{name} does not unzip under a padded place holding a space and an apostrophe"]
        if "\n          $ProgressPreference = 'SilentlyContinue'" not in block.split("\n          Expand-Archive -Path", 1)[0][-200:]:
            problems += [f"{name} unzips with Windows PowerShell's progress bar on (slow on thousands of files)"]
    ready = jobs.get("rehearse-ready", "")
    for needed in (
        "trial --route powershell",
        "trial --route cmd",
        "trial --route guard",
        "redirect --route cmd --folder $env:READY --expect pass",
        "golden --python",
        "tamper --folder",
        "start-check --folder",
    ):
        if needed not in ready:
            problems += [f"rehearse-ready lacks {needed!r}"]
    fallback = jobs.get("rehearse-fallback", "")
    for needed in FALLBACK_LINES:
        if needed not in fallback:
            problems += [f"rehearse-fallback lacks {needed!r}"]
    # The backup's interpreter is the one its carried installer made, fresh
    # (LANE WIN RULINGS 5, item 5): never one the runner already held.
    for stale in ("hostedtoolcache", "$candidates", "already installed on this runner"):
        if stale in fallback:
            problems += [f"rehearse-fallback could rehearse a Python the runner already held ({stale!r})"]
    compare = jobs.get("compare", "")
    for needed in (
        "--assert runs/ready-runs/powershell runs/fallback-runs/direct",
        "--assert runs/ready-runs/powershell runs/fallback-runs/guard",
        "--assert runs/ready-runs/powershell runs/linux-runs/linux-314",
        "--report runs/ready-runs/powershell runs/linux-runs/linux-311",
        "again --python",
    ):
        if needed not in compare:
            problems += [f"compare lacks {needed!r}"]
    if "again --python" not in jobs.get("compare-macos", ""):
        problems += ["compare-macos builds no twin from the Windows description"]
    wheel = jobs.get("wheel", "")
    for needed in ("sudo unshare --net", "SOURCE_DATE_EPOCH", "build --no-isolation --wheel", "git ls-files src/synthtwin"):
        if needed not in wheel and needed.replace(" ", '", "') not in wheel:
            problems += [f"wheel lacks {needed!r}"]
    build = jobs.get("build", "")
    for needed in (
        "windows_python.py check",
        "windows_python.py signatures",
        "Get-AuthenticodeSignature",
        "build_windows_folder.py ready",
        "build_windows_folder.py backup",
        "pe_imports.py",
        "--require-hashes --only-binary=:all:",
    ):
        if needed not in build:
            problems += [f"build lacks {needed!r}"]
    return problems


def test_the_workflow_keeps_every_rule() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert workflow_problems(text, CI.read_text(encoding="utf-8")) == []


_STEP_AFTER = "      - name: The golden tests on the folder's own Python\n"
_TRIAL = "      - name: The trial through the PowerShell window's synthtwin function\n"
_TABLES = "          & $python -I -B tools/bundle/invented_windows_table.py (Join-Path $env:RUNNER_TEMP 'tables')\n"
_LONG_PATHS = "          Set-ItemProperty -Path $key -Name LongPathsEnabled -Value 0 -Type DWord\n"
_GOLDEN_RUN = (
    "          & $python -I -B tools/bundle/rehearse_windows.py golden --python $python"
    " --pytest-only (Join-Path $env:RUNNER_TEMP 'pytest-only')\n"
    "          if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }\n"
)
_TOOLCACHE = "C:\\hostedtoolcache\\windows\\Python\\3.14.0\\x64\\python.exe"
_BACKUP_PYTHON = "--python (Join-Path $env:BUNDLE '.venv\\Scripts\\python.exe')"
_KEEP_END = '          } >> "$GITHUB_STEP_SUMMARY"\n'
_READY_END = "          retention-days: 1\n\n  rehearse-fallback:\n"
_READY_UPLOAD = "      - name: Hand the ready folder to its rehearsal (internal, one day)\n"
_KEPT_EARLY = (
    "      - name: Keep the ready folder 90 days, straight from the build\n"
    "        uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1\n"
    "        with:\n"
    "          name: synthtwin-windows-ready${{ needs.build.outputs.suffix }}\n"
    "          path: ${{ runner.temp }}/zipped/synthtwin-*-windows-ready*.zip\n"
    "          if-no-files-found: error\n"
    "          retention-days: 90\n"
)
_INSTALL_CHECK = (
    "          if (-not (Select-String -Path (Join-Path $env:RUNNER_TEMP 'install.log') -SimpleMatch"
    " -Pattern $env:BASE_PYTHON -Quiet)) { throw 'install.bat used another Python than the carried one' }\n"
)
# Lines a rehearsal step may never hold once the network is denied: each
# fetches, or runs another interpreter, or points the step at one.
FOREIGN = (
    "python -m synthtwin --version",
    "py -3.14 -m synthtwin --version",
    "& python -I -B tools/bundle/rehearse_windows.py trial --route direct",
    "& $env:READY\\python\\python.exe -m pip install pytest",
    "& $python -I -B tools/bundle/rehearse_windows.py golden; Invoke-Expression 'x'",
    "& $python -I -B tools/bundle/rehearse_windows.py golden --python (Get-Command python).Source",
    "& $python -I -B tools/bundle/rehearse_windows.py golden --work $(irm https://example.org/x)",
    "Invoke-RestMethod https://example.org/x -OutFile x.whl",
    "irm https://example.org/x -OutFile x.whl",
    "iwr https://example.org/x -OutFile x.whl",
    "Invoke-WebRequest https://example.org/x -OutFile x.whl",
    "wget https://example.org/x",
    "curl.exe -o x.whl https://example.org/x",
    "Start-BitsTransfer -Source https://example.org/x",
    "(New-Object Net.WebClient).DownloadFile('https://example.org/x', 'x.whl')",
    "git clone https://example.org/x",
    "winget install Python.Python.3.14",
    "choco install python",
    "Start-Process python -ArgumentList '-m synthtwin --version' -Wait",
    "cmd /c python -m synthtwin --version",
    "$env:READY = 'C:\\hostedtoolcache\\windows\\Python'",
    "$python = 'python'",
    "\"READY=C:\\x\" >> $env:GITHUB_ENV",
)


def test_every_foreign_line_after_the_denial_is_red() -> None:
    """The generated sweep: each foreign line, added to each step after each job's denial, turns the gate red."""
    text = WORKFLOW.read_text(encoding="utf-8")
    ci = CI.read_text(encoding="utf-8")
    jobs = MODELS.jobs_of(text)
    tried = 0
    for name in REHEARSED:
        steps = _steps(jobs[name])
        denied = next(index for index, step in enumerate(steps) if "guard_run.py --denied" in step)
        for step in steps[denied + 1 :]:
            if "\n        run: |\n" not in step:
                continue
            head, body = step.split("\n        run: |\n", 1)
            kept = body.rstrip("\n")
            for line in FOREIGN:
                mutant = head + "\n        run: |\n" + kept + "\n          " + line + body[len(kept) :]
                changed = jobs[name].replace(step, mutant, 1)
                assert changed != jobs[name]
                assert workflow_problems(text.replace(jobs[name], changed, 1), ci), (name, step.splitlines()[0], line)
                tried += 1
    assert tried >= 10 * len(FOREIGN), tried


@pytest.mark.parametrize(
    "old, new",
    [
        ("\n  workflow_dispatch:\n", "\n"),
        ('      - "scripts/**"\n', ""),
        ("permissions:\n  contents: read\n", "permissions:\n  contents: write\n"),
        ("    timeout-minutes: 20\n", ""),
        ("    needs: [build, rehearse-ready, rehearse-fallback, compare, compare-macos]\n", "    needs: [build, rehearse-ready]\n"),
        ("actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1", "actions/checkout@0000000000000000000000000000000000000000"),
        ("          retention-days: 90\n", "          retention-days: 5\n"),
        ("          name: pytest-only\n          path: ${{ runner.temp }}/pytest-only\n          if-no-files-found: error\n          retention-days: 1\n",
         "          name: pytest-only\n          path: ${{ runner.temp }}/pytest-only\n          if-no-files-found: error\n          retention-days: 5\n"),
        ("      - name: Write the record in the job summary\n", "      - name: Release\n        run: gh release upload v1 bundle.zip\n      - name: Write the record in the job summary\n"),
        ("          READY_URL: ${{ steps.ready.outputs.artifact-url }}\n", "          READY_URL: none\n"),
        ("-Direction Outbound -Action Block -Program $python", "-Direction Outbound -Action Allow -Program $python"),
        ("          & (Join-Path $env:READY 'python\\python.exe') -I -B tools/bundle/guard_run.py --prove\n", "          & python -I -B tools/bundle/guard_run.py --prove\n"),
        (_STEP_AFTER, "      - name: Fetch\n        shell: pwsh\n        run: |\n          & python -m pip install pytest\n" + _STEP_AFTER),
        ("Set-ItemProperty -Path $key -Name LongPathsEnabled -Value 0 -Type DWord", "Set-ItemProperty -Path $key -Name LongPathsEnabled -Value 1 -Type DWord"),
        ("--assert runs/ready-runs/powershell runs/fallback-runs/direct", "--report runs/ready-runs/powershell runs/fallback-runs/direct"),
        ("trial --route cmd", "trial --route powershell"),
        ("redirect --route cmd --folder $env:READY --expect pass", "redirect --route cmd --folder $env:READY --expect record"),
        ("    runs-on: macos-latest\n", "    runs-on: ubuntu-latest\n"),
        ("  rehearse-fallback:\n", "  rehearse-fallback:\n\t"),
        # Skeptic 1's item 2 (LANE WIN RULINGS 4 (3)): only rehearsed zips
        # are kept, and every step after the denial runs the rehearsed
        # interpreter.
        ("    needs: [build, rehearse-ready, rehearse-fallback, compare, compare-macos]\n",
         "    needs: [build, rehearse-ready, rehearse-fallback, compare, compare-macos]\n    if: always()\n"),
        ("  rehearse-ready:\n", "  rehearse-ready:\n    continue-on-error: true\n"),
        (_TRIAL, _TRIAL + "        continue-on-error: true\n"),
        (_TABLES, "          python -m synthtwin --version\n" + _TABLES),
        (_TABLES, "          Invoke-RestMethod https://example.org/x -OutFile x.whl\n" + _TABLES),
        # The neighbours of those five.
        ("          & $python -I -B tools/bundle/guard_run.py --denied\n", "          & python -I -B tools/bundle/guard_run.py --denied\n"),
        ("          & $env:BASE_PYTHON -I -B tools/bundle/guard_run.py --proxied\n", "          & python -I -B tools/bundle/guard_run.py --proxied\n"),
        ("-Direction Outbound -Action Block -Program $env:BASE_PYTHON |", "-Direction Outbound -Action Block -Program (Get-Command python).Source |"),
        ("    needs: [wheel, rehearse-ready, rehearse-fallback]\n", "    needs: [wheel, rehearse-ready, rehearse-fallback]\n    if: always()\n"),
        (_STEP_AFTER, _STEP_AFTER.replace("      - name: ", "      - if: always()\n        name: ")),
        (_GOLDEN_RUN, _GOLDEN_RUN + "        if: ${{ always() }}\n"),
        (_TRIAL, _TRIAL + "        env:\n          READY: C:\\hostedtoolcache\\windows\\Python\n"),
        ('env:\n  PIP_DISABLE_PIP_VERSION_CHECK: "1"\n', 'env:\n  PIP_DISABLE_PIP_VERSION_CHECK: "1"\n  BASE_PYTHON: python\n'),
        (_STEP_AFTER, "      - uses: actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c # v8.0.1\n"
                      "        with:\n          name: win-wheel\n" + _STEP_AFTER),
        ("          if ($fetched.Count -gt 0) {", "          if ($false) {"),
        ("          $ProgressPreference = 'SilentlyContinue'\n          $began = Get-Date\n", "          $began = Get-Date\n"),
        # Before the denial too, a rehearsal job fetches nothing once its
        # checkout and downloads are done (the short command names).
        (_LONG_PATHS, _LONG_PATHS + "          git clone https://example.org/x\n"),
        (_LONG_PATHS, _LONG_PATHS + "          irm https://example.org/x -OutFile x.whl\n"),
        # The combined verify's FIX 1 (LANE WIN RULINGS 6 (2)), its mutants
        # by their names: W01 and W02, a job's own if: written after its
        # steps; W12, the denial step's $python set to another interpreter;
        # W03, W04 and W09, another interpreter handed as a plain token;
        # W08, another folder; W05, a kept name uploaded before any
        # rehearsal.
        (_KEEP_END, _KEEP_END + "    if: always()\n"),
        (_READY_END, _READY_END.replace("\n\n", "\n    if: always()\n\n", 1)),
        ("          $python = Join-Path $env:READY 'python\\python.exe'\n          Set-NetFirewallProfile",
         "          $python = (Get-Command python).Source\n          Set-NetFirewallProfile"),
        ("rehearse_windows.py golden --python $python --pytest-only", "rehearse_windows.py golden --python " + _TOOLCACHE + " --pytest-only"),
        ("trial --route direct --utf8-screen " + _BACKUP_PYTHON, "trial --route direct --utf8-screen --python " + _TOOLCACHE),
        ("golden " + _BACKUP_PYTHON, "golden --python " + _TOOLCACHE),
        ("trial --route powershell --folder $env:READY", "trial --route powershell --folder D:\\a\\other-folder"),
        (_READY_UPLOAD, _KEPT_EARLY + _READY_UPLOAD),
        # Codex's item 3: the backup's trial under the guard, and held.
        ("trial --route guard --utf8-screen " + _BACKUP_PYTHON, "trial --route guard --utf8-screen --python " + _TOOLCACHE),
        ("trial --route guard --utf8-screen", "trial --route direct --utf8-screen"),
        ("--assert runs/ready-runs/powershell runs/fallback-runs/guard", "--report runs/ready-runs/powershell runs/fallback-runs/guard"),
        # Codex's item 5: the backup's Python installed fresh, or the step fails.
        ("          $base = Join-Path $target 'python.exe'\n", "          $base = \"C:\\hostedtoolcache\\windows\\Python\\$release\\x64\\python.exe\"\n"),
        ("          if ((Test-Path $target) -or (Test-Path $log)) { throw ", "          if ($false) { throw "),
        ("-ArgumentList @('/uninstall', '/quiet')", "-ArgumentList @('/repair', '/quiet')"),
        ("@('/x', $part.PSChildName", "@('/fa', $part.PSChildName"),
        ("          if (-not (Test-Path $log)) { throw ", "          if ($false) { throw "),
        # The verify's carry C4: install.bat must take the carried Python.
        ("          $env:PATH = (Split-Path $env:BASE_PYTHON) + ';' + $env:PATH\n", ""),
        (_INSTALL_CHECK, ""),
    ],
)
def test_a_workflow_short_of_the_plan_is_red(old: str, new: str) -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert old in text, old
    assert workflow_problems(text.replace(old, new, 1), CI.read_text(encoding="utf-8")), "the mutant passed"


def test_a_trial_moved_before_the_denial_is_red() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    jobs = MODELS.jobs_of(text)
    steps = _steps(jobs["rehearse-ready"])
    trial = next(step for step in steps if "trial --route powershell" in step)
    denied = next(step for step in steps if "guard_run.py --denied" in step)
    moved = jobs["rehearse-ready"].replace("\n      - " + trial, "").replace("\n      - " + denied, "\n      - " + trial + "\n      - " + denied)
    assert workflow_problems(text.replace(jobs["rehearse-ready"], moved), CI.read_text(encoding="utf-8"))


def test_the_workflow_is_yaml_where_a_reader_is_installed() -> None:
    """Runs only where a YAML reader is installed, so never in CI: PyYAML is in no lock CI installs.

    It is skipped on every machine the suite runs on today and is red on
    no mutant there; `workflow_problems` holds the file's structure
    everywhere, and GitHub's own reader decides at the push.
    """
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        pytest.skip("PyYAML is not installed here; the structure is held by workflow_problems")
    loaded = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    assert set(loaded["jobs"]) == set(JOBS)


def test_nothing_the_builder_makes_can_be_committed() -> None:
    ignored = (REPO / ".gitignore").read_text(encoding="utf-8").splitlines()
    for pattern in ("*.whl", "*.zip", "*.csv", "SHA256SUMS", "THIRD-PARTY-NOTICES*"):
        assert pattern in ignored, pattern
