"""The offline bundle: its check, its install scripts and its CI jobs.

Plan P4-D416 (lane DEP-2 of the December plan). The owner's D3 of
2026-10-20: the hash-checked offline bundle is the only way synthtwin is
installed, never PyPI. The bundle itself is built only in CI, on each
platform's own runner (`bundle-build`), and installed there with the
network denied (`bundle-test`); nothing here downloads anything. The
wheelhouse these tests install from is a STUB made here from two wheels
written by this file -- a stand-in library and a stand-in synthtwin whose
`synthtwin doctor` only says it ran -- so the scripts' logic is proved on
every system of the matrix without one third-party file.

What this file holds:

* the check every install runs first (`scripts/check_bundle.py` in the
  bundle, `tools/bundle/check_bundle.py` here)
  refuses a missing hash, a changed file, an unpinned wheel, a lock
  that names a place to fetch from, a wrong Python and a wrong system;
* `scripts/install.sh`, run for real on a stub bundle (POSIX systems),
  installs from the bundle alone, refuses a missing hash, an old Python
  and an argument before it changes anything, and stops -- never
  fetches -- when a file is missing;
* both scripts' text: every pip command is --isolated and --no-index,
  the lock install --require-hashes, the check before the environment;
* the builder (`tools/bundle/build_bundle.py`) refuses a wheel the lock
  does not pin and anything that is not a wheel, gathers the notices
  from the wheels and lists every file in SHA256SUMS; none of what it
  makes can be committed;
* the CI job definitions parse and name every platform and Python, the
  gate names the three new jobs, and nothing is published.

Each rule is pinned by a mutation case red without it.
"""

import base64
import csv
import hashlib
import importlib.util
import io
import os
import pathlib
import re
import shutil
import subprocess
import sys
import zipfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
WORKFLOW = REPO / ".github" / "workflows" / "ci.yml"


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, REPO / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECK = _load("check_bundle", "tools/bundle/check_bundle.py")
BUILD = _load("build_bundle", "tools/bundle/build_bundle.py")

STUB_LICENCE = "Stand-in licence of the stand-in library, written by tests/test_bundle.py.\n"


# -- stub wheels and a stub bundle --------------------------------------------


def _wheel(
    folder: pathlib.Path,
    name: str,
    version: str,
    files: "dict[str, str]",
    tags: str = "py3-none-any",
    entry_points: str = "",
    licence: str = "",
) -> pathlib.Path:
    """A real, installable wheel holding ``files``, written by this test."""
    info = f"{name}-{version}.dist-info"
    members = dict(files)
    members[f"{info}/METADATA"] = (
        f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n"
        "License-Expression: MIT\n"
    )
    members[f"{info}/WHEEL"] = (
        "Wheel-Version: 1.0\nGenerator: test_bundle\nRoot-Is-Purelib: true\n"
        f"Tag: {tags}\n"
    )
    if entry_points:
        members[f"{info}/entry_points.txt"] = entry_points
    if licence:
        members[f"{info}/licenses/LICENSE"] = licence
    record = io.StringIO()
    writer = csv.writer(record, lineterminator="\n")
    for member, text in sorted(members.items()):
        data = text.encode("utf-8")
        digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=")
        writer.writerow([member, "sha256=" + digest.decode("ascii"), len(data)])
    writer.writerow([f"{info}/RECORD", "", ""])
    members[f"{info}/RECORD"] = record.getvalue()
    path = folder / f"{name}-{version}-{tags}.whl"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for member, text in sorted(members.items()):
            archive.writestr(zipfile.ZipInfo(member, (1980, 1, 1, 0, 0, 0)), text)
    return path


def _sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stub(tmp_path: pathlib.Path) -> "dict[str, pathlib.Path]":
    """A stub repository, a stub wheelhouse and a stub synthtwin wheel."""
    house = tmp_path / "downloaded"
    house.mkdir(parents=True)
    library = _wheel(
        house,
        "stubdep",
        "1.0",
        {"stubdep/__init__.py": 'WORD = "the stand-in library loaded"\n'},
        licence=STUB_LICENCE,
    )
    elsewhere = tmp_path / "built"
    elsewhere.mkdir()
    ours = _wheel(
        elsewhere,
        "synthtwin",
        "0.0.1",
        {
            "synthtwin/__init__.py": "",
            "synthtwin/stub.py": (
                "import sys\n\n\ndef main():\n    import stubdep\n\n"
                '    print("stand-in doctor ran:", " ".join(sys.argv[1:]), stubdep.WORD)\n'
                "    return 0\n"
            ),
        },
        entry_points="[console_scripts]\nsynthtwin = synthtwin.stub:main\n",
    )
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "tools" / "bundle").mkdir(parents=True)
    for name in ("install.sh", "install.bat", "INSTALL.txt"):
        shutil.copyfile(SCRIPTS / name, repo / "scripts" / name)
    shutil.copyfile(
        REPO / "tools" / "bundle" / "check_bundle.py",
        repo / "tools" / "bundle" / "check_bundle.py",
    )
    shutil.copyfile(REPO / "LICENSE", repo / "LICENSE")
    (repo / "requirements-install.lock").write_text(
        "--only-binary :all:\n"
        "stubdep==1.0 \\\n"
        f"    --hash=sha256:{_sha256(library)}\n"
        "    # via synthtwin\n",
        encoding="utf-8",
        newline="\n",
    )
    return {"house": house, "library": library, "ours": ours, "repo": repo}


def _bundle(tmp_path: pathlib.Path, parent: str = "a folder with spaces") -> pathlib.Path:
    stub = _stub(tmp_path)
    out = tmp_path / parent / "synthtwin-0.0.1-stub"
    assert BUILD.assemble(stub["house"], stub["ours"], out, repo=stub["repo"]) == []
    return out


def _resum(bundle: pathlib.Path) -> None:
    """Write SHA256SUMS again over every file, as the builder does."""
    listed = sorted(
        path.relative_to(bundle).as_posix()
        for path in bundle.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS" and ".venv" not in path.parts
    )
    (bundle / "SHA256SUMS").write_text(
        "".join(f"{_sha256(bundle / name)}  {name}\n" for name in listed),
        encoding="utf-8",
        newline="\n",
    )


def _refused(bundle: pathlib.Path, needle: str, **given: object) -> None:
    found = CHECK.check(str(bundle), **given)
    assert found, "the check passed a bundle it must refuse"
    assert needle in " ".join(found), found


# -- the check every install runs first ---------------------------------------


def test_a_whole_bundle_passes_its_check_and_lists_every_file(tmp_path: pathlib.Path) -> None:
    bundle = _bundle(tmp_path)
    assert CHECK.check(str(bundle)) == []
    listed = {
        line.split("  ", 1)[1]
        for line in (bundle / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
    }
    on_disk = {
        path.relative_to(bundle).as_posix()
        for path in bundle.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS"
    }
    assert listed == on_disk
    assert {
        "INSTALL.txt",
        "LICENSE",
        "THIRD-PARTY-NOTICES.txt",
        "requirements-install.lock",
        "scripts/install.sh",
        "scripts/install.bat",
        "scripts/check_bundle.py",
        "wheelhouse/stubdep-1.0-py3-none-any.whl",
        "wheelhouse/synthtwin-0.0.1-py3-none-any.whl",
    } == on_disk
    assert CHECK.main([str(bundle)]) == 0


def test_the_check_refuses_a_missing_hash(tmp_path: pathlib.Path) -> None:
    """No SHA256SUMS, a wheel it does not list, a lock line with no hash."""
    bundle = _bundle(tmp_path)
    sums = bundle / "SHA256SUMS"
    whole = sums.read_text(encoding="utf-8")
    sums.write_text(
        "".join(line + "\n" for line in whole.splitlines() if "stubdep" not in line),
        encoding="utf-8",
        newline="\n",
    )
    _refused(bundle, "wheelhouse/stubdep-1.0-py3-none-any.whl has no hash in SHA256SUMS")
    sums.write_text(whole, encoding="utf-8", newline="\n")
    assert CHECK.check(str(bundle)) == []
    shutil.copyfile(
        bundle / "wheelhouse" / "stubdep-1.0-py3-none-any.whl",
        bundle / "wheelhouse" / "stubdep-1.1-py3-none-any.whl",
    )
    _refused(bundle, "stubdep-1.1-py3-none-any.whl has no hash in SHA256SUMS")
    (bundle / "wheelhouse" / "stubdep-1.1-py3-none-any.whl").unlink()
    sums.unlink()
    _refused(bundle, "SHA256SUMS is missing")
    _resum(bundle)
    # The files the install reads besides the wheels: a line of SHA256SUMS
    # gone for any of them is refused (lane DEP-2's verify, item 2, V8).
    whole = sums.read_text(encoding="utf-8")
    for required in CHECK.REQUIRED:
        sums.write_text(
            "".join(line + "\n" for line in whole.splitlines() if not line.endswith("  " + required)),
            encoding="utf-8",
            newline="\n",
        )
        _refused(bundle, "SHA256SUMS gives no hash for " + required)
    sums.write_text(whole, encoding="utf-8", newline="\n")
    assert CHECK.check(str(bundle)) == []
    lock = bundle / "requirements-install.lock"
    lock.write_text(
        lock.read_text(encoding="utf-8") + "otherdep==2.0\n", encoding="utf-8", newline="\n"
    )
    _resum(bundle)
    _refused(bundle, "the lock names otherdep==2.0 with no hash")


def test_the_check_refuses_a_changed_file_and_an_unpinned_wheel(tmp_path: pathlib.Path) -> None:
    bundle = _bundle(tmp_path)
    wheel = bundle / "wheelhouse" / "stubdep-1.0-py3-none-any.whl"
    data = bytearray(wheel.read_bytes())
    data[-1] ^= 1
    wheel.write_bytes(bytes(data))
    _refused(bundle, "stubdep-1.0-py3-none-any.whl does not match its hash")
    # The same changed file listed again in SHA256SUMS: the lock still
    # pins the original bytes, so the wheel is refused all the same.
    _resum(bundle)
    _refused(bundle, "is not a file the lock pins by its hash")
    for script in ("scripts/install.sh", "scripts/check_bundle.py", "requirements-install.lock"):
        fresh = _bundle(tmp_path / script.replace("/", "-"))
        with (fresh / script).open("a", encoding="utf-8", newline="\n") as handle:
            handle.write("\n")
        _refused(fresh, script + " does not match its hash")


def test_the_check_refuses_a_bundle_without_one_synthtwin_wheel(tmp_path: pathlib.Path) -> None:
    bundle = _bundle(tmp_path)
    (bundle / "wheelhouse" / "synthtwin-0.0.1-py3-none-any.whl").unlink()
    _resum(bundle)
    _refused(bundle, "exactly one synthtwin wheel, and it holds 0")


@pytest.mark.parametrize(
    "line",
    [
        "--index-url https://pypi.org/simple",
        "--extra-index-url https://example.invalid/simple",
        "--find-links https://example.invalid/wheels",
        "-f /somewhere/else",
        "--trusted-host example.invalid",
        "-e .",
        "stubdep @ https://example.invalid/stubdep-1.0-py3-none-any.whl",
        "--no-binary :all:",
        "stubdep>=1.0 --hash=sha256:" + "0" * 64,
        # Codex's review of lane DEP-2, item 1: a directive with more on
        # its line, which the check skipped whole, and options riding on
        # a requirement's line.
        "--only-binary=:all: --find-links https://example.invalid/wheels",
        "--only-binary :all: -fhttps://example.invalid/wheels",
        "--require-hashes --index-url=https://example.invalid/simple",
        "--only-binary=:all: --no-index",
        "--require-hashes -r /somewhere/else.txt",
        "--only-binary :all: --no-binary stubdep",
        "otherdep==2.0 --hash=sha256:" + "0" * 64 + " --config-settings x=y",
        "otherdep==2.0 ; sys_platform == 'linux' --no-binary otherdep --hash=sha256:" + "0" * 64,
        "otherdep==2.0 ; extra == 'x' --hash=sha256:" + "0" * 64,
    ],
)
def test_the_check_refuses_a_lock_that_could_fetch(tmp_path: pathlib.Path, line: str) -> None:
    """A network fallback written into the lock is refused before pip reads it."""
    bundle = _bundle(tmp_path)
    lock = bundle / "requirements-install.lock"
    lock.write_text(line + "\n" + lock.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    _resum(bundle)
    found = " ".join(CHECK.check(str(bundle)))
    assert "the lock" in found, found


def test_the_check_reads_the_real_locks_as_clean() -> None:
    for name in ("requirements-install.lock", "requirements-dev.lock", "requirements-min.lock"):
        text = (REPO / name).read_text(encoding="utf-8")
        assert CHECK._lock_problems(text) == [], name
        # Every requirement line is read whole, its condition included.
        named = [line for line in CHECK._lock_lines(text) if not line.startswith("-")]
        assert len(CHECK._requirements(text)) == len(named) > 0, name


def test_the_directives_are_read_exactly() -> None:
    """Item 1's mutant: a line beginning with a directive skipped whole."""
    for line in ("--only-binary :all:", "--only-binary=:all:", "--require-hashes"):
        assert CHECK._lock_problems(line + "\n") == [], line
    assert CHECK._lock_problems("--only-binary=:all: --find-links https://example.invalid/wheels\n")


def test_the_lock_conditions_are_read_for_this_computer() -> None:
    """The lock's numpy for 3.11 and for 3.12 on, and tzdata on Windows alone."""
    text = (REPO / "requirements-install.lock").read_text(encoding="utf-8")

    def active(version: "tuple[int, int]", system: str) -> "dict[str, frozenset[str]]":
        environment = CHECK._environment(version, {"system": system, "machine": "x86_64"}, False)
        found: "dict[str, frozenset[str]]" = {}
        for name, condition, hashes in CHECK._requirements(text):
            if condition is None or CHECK._holds(condition, environment):
                assert name not in found, name
                found[name] = frozenset(hashes)
        return found

    assert "tzdata" in active((3, 13), "Windows") and "tzdata" not in active((3, 13), "Linux")
    assert active((3, 11), "Linux")["numpy"] != active((3, 12), "Linux")["numpy"]
    assert active((3, 12), "Linux")["numpy"] == active((3, 14), "macOS")["numpy"]
    assert CHECK._marker("python_full_version >= '3.12'") == [[("python_full_version", ">=", "3.12")]]
    assert CHECK._marker("sys_platform < 'win32'") is None
    assert CHECK._marker("extra == 'x'") is None


def _with_wheels(bundle: pathlib.Path, project: str, tags: "list[str]") -> None:
    """Stand-in native wheels of ``project``, one a tag, pinned in the lock and listed."""
    house = bundle / "wheelhouse"
    made = [_wheel(house, project, "1.0", {project + "/__init__.py": ""}, tags=tag) for tag in tags]
    lock = bundle / "requirements-install.lock"
    pins = " \\\n".join(f"    --hash=sha256:{_sha256(path)}" for path in made)
    lock.write_text(
        lock.read_text(encoding="utf-8") + f"{project}==1.0 \\\n{pins}\n",
        encoding="utf-8",
        newline="\n",
    )
    _resum(bundle)


def test_the_check_refuses_a_wrong_python(tmp_path: pathlib.Path) -> None:
    """Older than 3.11 or newer than 3.14 always; another Python than the wheels serve.

    The advice names Python 3.14, not python.org's newest Python, which
    from 3.15 on no bundle serves (lane DEP-2's skeptic, item 2).
    """
    bundle = _bundle(tmp_path)
    for version in ((3, 10), (3, 15)):
        _refused(
            bundle,
            f"this computer's Python is {version[0]}.{version[1]}, and this synthtwin bundle "
            "serves Python 3.11, 3.12, 3.13 and 3.14. Install Python 3.14 from python.org",
            version=version,
        )
    for minor in (11, 12, 13, 14):
        assert CHECK.check(str(bundle), version=(3, minor)) == []
    _with_wheels(bundle, "stubnative", [f"cp3{minor}-cp3{minor}-macosx_11_0_arm64" for minor in (11, 12, 13)])
    # A wheel for any Python 3 (abi3) names no Python the bundle serves.
    _with_wheels(bundle, "stubabi", ["cp37-abi3-macosx_11_0_arm64"])
    assert CHECK.check(str(bundle), version=(3, 13), system="macOS") == []
    _refused(
        bundle,
        "holds the libraries for Python 3.11, 3.12 and 3.13, and the Python found is 3.14. "
        "Install Python 3.13 from python.org",
        version=(3, 14),
        system="macOS",
    )
    _refused(bundle, "this bundle is made for macOS, and this computer runs Windows",
             version=(3, 13), system="Windows")


def test_the_pythons_agree_everywhere() -> None:
    """The check's range, both scripts' and the guide's are CI's tests matrix."""
    pythons = _list(jobs_of(WORKFLOW.read_text(encoding="utf-8")).get("tests", ""), "python-version")
    assert [CHECK._dotted(version) for version in CHECK._served_range()] == pythons
    assert (CHECK.FLOOR, CHECK.NEWEST) == (CHECK._served_range()[0], CHECK._served_range()[-1])
    for name in ("install.sh", "install.bat"):
        assert _version_range(pythons) in (SCRIPTS / name).read_text(encoding="utf-8"), name
    guide = (SCRIPTS / "INSTALL.txt").read_text(encoding="utf-8")
    assert "Python " + ", ".join(pythons[:-1]) + " or " + pythons[-1] + " first" in guide


MAC_ARM = {"system": "macOS", "machine": "arm", "macos": (14, 5)}


def test_the_check_reads_the_chip_and_the_macos_a_bundle_needs(tmp_path: pathlib.Path) -> None:
    """Lane DEP-2's skeptic, item 3: a Mac too old, an Intel chip, both in plain words."""
    bundle = _bundle(tmp_path)
    _with_wheels(bundle, "stubnative", ["cp313-cp313-macosx_12_0_arm64"])
    assert CHECK.check(str(bundle), version=(3, 13), computer=MAC_ARM) == []
    assert CHECK.check(str(bundle), version=(3, 13), computer=dict(MAC_ARM, macos=(12, 0))) == []
    _refused(
        bundle,
        "this bundle is made for Macs with an Apple chip (M1 or later) on macOS 12 or later, "
        "and this Mac runs macOS 11.7. Update macOS to 12 or later",
        version=(3, 13),
        computer=dict(MAC_ARM, macos=(11, 7)),
    )
    _refused(
        bundle,
        "and this Mac's Python runs on an Intel chip. If this Mac has an Apple chip, the "
        "Python found is one made for Intel Macs. Install Python 3.14",
        version=(3, 13),
        computer=dict(MAC_ARM, machine="x86_64"),
    )
    # What this computer is not known about is not judged: pip decides.
    assert CHECK.check(str(bundle), version=(3, 13), system="macOS") == []
    # The newest macOS any wheel needs is the bundle's: one wheel of
    # macOS 14 makes a macOS 12.7 Mac refuse the whole bundle.
    _with_wheels(bundle, "stubnewer", ["cp313-cp313-macosx_14_0_arm64"])
    _refused(
        bundle,
        "on macOS 14 or later, and this Mac runs macOS 12.7",
        version=(3, 13),
        computer=dict(MAC_ARM, macos=(12, 7)),
    )


def test_a_wheel_fits_when_any_of_its_tags_fits(tmp_path: pathlib.Path) -> None:
    bundle = _bundle(tmp_path)
    _with_wheels(bundle, "stubboth", ["cp313-cp313-macosx_10_9_x86_64.macosx_11_0_arm64"])
    _with_wheels(bundle, "stubuniversal", ["cp313-cp313-macosx_10_9_universal2"])
    assert CHECK.check(str(bundle), version=(3, 13), computer=dict(MAC_ARM, macos=(11, 0))) == []
    intel = {"system": "macOS", "machine": "x86_64", "macos": (10, 15)}
    assert CHECK.check(str(bundle), version=(3, 13), computer=intel) == []


def test_the_check_reads_the_chip_on_windows_and_the_glibc_on_linux(tmp_path: pathlib.Path) -> None:
    windows = _bundle(tmp_path / "windows")
    _with_wheels(windows, "stubnative", ["cp313-cp313-win_amd64"])
    assert CHECK.check(str(windows), version=(3, 13), computer={"system": "Windows", "machine": "x86_64"}) == []
    _refused(
        windows,
        "this bundle is made for Windows computers with a 64-bit Intel or AMD processor, and "
        "this computer's Python runs on an Arm processor. Windows 11 runs the 64-bit Python",
        version=(3, 13),
        computer={"system": "Windows", "machine": "arm"},
    )
    _refused(
        windows,
        "runs on a 32-bit Intel or AMD processor. There is no synthtwin bundle for this "
        "computer's processor yet",
        version=(3, 13),
        computer={"system": "Windows", "machine": "x86"},
    )
    linux = _bundle(tmp_path / "linux")
    _with_wheels(linux, "stubnative", ["cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64"])
    _with_wheels(linux, "stubolder", ["cp313-cp313-manylinux2014_x86_64"])
    computer = {"system": "Linux", "machine": "x86_64", "glibc": (2, 31)}
    assert CHECK.check(str(linux), version=(3, 13), computer=computer) == []
    _refused(
        linux,
        "whose system library, glibc, is version 2.27 or later, and this computer's is 2.17",
        version=(3, 13),
        computer=dict(computer, glibc=(2, 17)),
    )
    _refused(
        linux,
        "made for Linux computers with a 64-bit Intel or AMD processor whose system library",
        version=(3, 13),
        computer=dict(computer, machine="arm"),
    )


def test_this_computer_is_read_as_the_wheels_name_it() -> None:
    found = CHECK._this_computer()
    assert found["system"] == CHECK._this_system()
    assert found["machine"] in ("arm", "x86_64", "x86"), found
    if sys.platform == "darwin":
        assert found["macos"] is not None and found["macos"] >= (11, 0), found


def test_the_check_refuses_a_pinned_source_archive(tmp_path: pathlib.Path) -> None:
    """A source archive runs build code when installed, pinned by the lock or not."""
    bundle = _bundle(tmp_path)
    archive = bundle / "wheelhouse" / "stubdep-1.0.tar.gz"
    archive.write_bytes(b"a source archive")
    lock = bundle / "requirements-install.lock"
    lock.write_text(
        lock.read_text(encoding="utf-8").replace(
            "\n    # via synthtwin", f" \\\n    --hash=sha256:{_sha256(archive)}\n    # via synthtwin"
        ),
        encoding="utf-8",
        newline="\n",
    )
    assert _sha256(archive) in lock.read_text(encoding="utf-8")
    assert CHECK._lock_problems(lock.read_text(encoding="utf-8")) == []
    _resum(bundle)
    _refused(bundle, "wheelhouse/stubdep-1.0.tar.gz is not a wheel")


def _lock_line(bundle: pathlib.Path, line: str) -> None:
    lock = bundle / "requirements-install.lock"
    lock.write_text(lock.read_text(encoding="utf-8") + line + "\n", encoding="utf-8", newline="\n")
    _resum(bundle)


def test_the_check_refuses_a_bundle_missing_a_library_this_computer_needs(tmp_path: pathlib.Path) -> None:
    """Codex's review of lane DEP-2, item 5: an incomplete bundle stops in the check.

    Before, the check passed it, the script cleared the earlier
    environment, and pip stopped afterwards.
    """
    bundle = _bundle(tmp_path)
    (bundle / "wheelhouse" / "stubdep-1.0-py3-none-any.whl").unlink()
    _resum(bundle)
    _refused(bundle, "has no file of stubdep that this computer and its Python")
    # One library with every Python's wheel, one without 3.13's.
    native = _bundle(tmp_path / "native")
    _with_wheels(native, "stubnative", [f"cp3{minor}-cp3{minor}-macosx_11_0_arm64" for minor in (11, 12, 13)])
    _with_wheels(native, "stubother", [f"cp3{minor}-cp3{minor}-macosx_11_0_arm64" for minor in (11, 12)])
    assert CHECK.check(str(native), version=(3, 12), computer=MAC_ARM) == []
    _refused(native, "has no file of stubother that this computer and its Python 3.13 can take",
             version=(3, 13), computer=MAC_ARM)
    # A file stands for a library only when it is that library's and the
    # lock pins it on that library's line: stubother's 3.12 wheel pinned
    # on stubnative's line, and stubnative's on stubother's, leave
    # stubother with nothing for 3.12.
    house = native / "wheelhouse"
    other = _sha256(house / "stubother-1.0-cp312-cp312-macosx_11_0_arm64.whl")
    mine = _sha256(house / "stubnative-1.0-cp312-cp312-macosx_11_0_arm64.whl")
    lock = native / "requirements-install.lock"
    text = lock.read_text(encoding="utf-8")
    head, tail = text.split("stubother==1.0", 1)
    tail = tail.replace(other, mine)
    head = head.replace(mine, mine + " \\\n    --hash=sha256:" + other)
    lock.write_text(head + "stubother==1.0" + tail, encoding="utf-8", newline="\n")
    _resum(native)
    assert other in head and mine in tail and other not in tail
    _refused(native, "has no file of stubother", version=(3, 12), computer=MAC_ARM)
    # A requirement for Windows alone is asked of Windows alone.
    conditioned = _bundle(tmp_path / "conditioned")
    _lock_line(conditioned, "stubwin==1.0 ; sys_platform == 'win32' \\\n    --hash=sha256:" + "0" * 64)
    assert CHECK.check(str(conditioned), version=(3, 13), computer={"system": "Linux", "machine": "x86_64"}) == []
    _refused(conditioned, "has no file of stubwin", version=(3, 13),
             computer={"system": "Windows", "machine": "x86_64"})


def test_the_check_reads_the_kind_of_python(tmp_path: pathlib.Path) -> None:
    """Codex's review of lane DEP-2, item 3: a free-threaded or another Python is refused first."""
    bundle = _bundle(tmp_path)
    _with_wheels(bundle, "stubnative", ["cp314-cp314-macosx_12_0_arm64"])
    usual = {"implementation": "cpython", "abi": "cp314"}
    free = {"implementation": "cpython", "abi": "cp314t"}
    assert CHECK.check(str(bundle), version=(3, 14), computer=MAC_ARM, python=usual) == []
    _refused(
        bundle,
        "the Python found is the free-threaded build of Python 3.14, and this bundle's "
        "libraries are made for its usual build. Run the install script with the usual "
        "Python 3.14 (python3.14, not python3.14t)",
        version=(3, 14), computer=MAC_ARM, python=free,
    )
    _refused(
        bundle,
        "the Python found is pypy 3.14, and this synthtwin bundle serves the usual Python, "
        "CPython, from python.org. Install Python 3.14",
        version=(3, 14), computer=MAC_ARM, python={"implementation": "pypy", "abi": "pypy314_pp73"},
    )
    # A wheel for every CPython 3 (abi3) is not one the free-threaded build takes.
    stable = _bundle(tmp_path / "abi3")
    _with_wheels(stable, "stubabi", ["cp37-abi3-macosx_11_0_arm64"])
    assert CHECK.check(str(stable), version=(3, 14), computer=MAC_ARM, python=usual) == []
    _refused(stable, "has no file of stubabi", version=(3, 14), computer=MAC_ARM, python=free)
    # This Python, as the check reads it.
    import sysconfig

    found = CHECK._this_python()
    assert found["implementation"] == sys.implementation.name
    assert found["abi"] == f"cp3{sys.version_info[1]}" + ("t" if sysconfig.get_config_var("Py_GIL_DISABLED") else "")


def test_the_check_refuses_a_linux_without_glibc(tmp_path: pathlib.Path, monkeypatch) -> None:
    """Codex's review of lane DEP-2, item 4: Alpine's musl was read as 'not known' and passed."""
    linux = _bundle(tmp_path)
    _with_wheels(linux, "stubnative", ["cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64"])
    musl = {"system": "Linux", "machine": "x86_64", "glibc": None, "libc": "other"}
    _refused(
        linux,
        "made for Linux computers with a 64-bit Intel or AMD processor whose system library, "
        "glibc, is version 2.27 or later, and this computer's system library is not glibc (as "
        "on Alpine Linux). There is no synthtwin bundle for it yet",
        version=(3, 13), computer=musl,
    )
    assert CHECK.check(str(linux), version=(3, 13), computer=dict(musl, libc="glibc", glibc=(2, 35))) == []
    assert CHECK.check(str(linux), version=(3, 13), computer={"system": "Linux", "machine": "x86_64"}) == []
    # How this computer is read: glibc answers by its name, musl does not.
    monkeypatch.setattr(CHECK, "_this_system", lambda: "Linux")
    monkeypatch.setattr(CHECK.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(CHECK.platform, "libc_ver", lambda: ("", ""))
    assert CHECK._this_computer()["libc"] == "other"
    monkeypatch.setattr(CHECK.platform, "libc_ver", lambda: ("glibc", "2.35"))
    assert CHECK._this_computer() == {
        "system": "Linux", "machine": "x86_64", "macos": None, "glibc": (2, 35), "libc": "glibc",
    }


def test_a_32_bit_python_on_64_bit_windows_is_read_as_one(tmp_path: pathlib.Path, monkeypatch) -> None:
    """Lane DEP-2's verify, item 2 (V7): sysconfig names the Python's own build on Windows."""
    monkeypatch.setattr(CHECK, "_this_system", lambda: "Windows")
    monkeypatch.setattr(CHECK.sysconfig, "get_platform", lambda: "win32")
    monkeypatch.setattr(CHECK.platform, "machine", lambda: "AMD64")
    found = CHECK._this_computer()
    assert found["machine"] == "x86", found
    windows = _bundle(tmp_path)
    _with_wheels(windows, "stubnative", ["cp313-cp313-win_amd64"])
    _refused(windows, "runs on a 32-bit Intel or AMD processor", version=(3, 13), computer=found)


def test_an_unreadable_file_is_named_and_never_a_traceback(tmp_path: pathlib.Path, monkeypatch) -> None:
    """Codex's review of lane DEP-2, item 6: a file this computer will not let the check read."""
    bundle = _bundle(tmp_path)
    real_open = open
    for blocked in ("SHA256SUMS", "requirements-install.lock", "stubdep-1.0-py3-none-any.whl"):

        def refusing(path, *arguments, blocked=blocked, **named):
            if os.path.basename(str(path)) == blocked:
                raise PermissionError(13, "Permission denied", str(path))
            return real_open(path, *arguments, **named)

        monkeypatch.setattr(CHECK, "open", refusing, raising=False)
        found = " ".join(CHECK.check(str(bundle)))
        assert "this computer would not let synthtwin read " in found and blocked in found, found
        assert "(Permission denied)" in found and "Copy the bundle's zip file into a folder of your own" in found
        assert CHECK.main([str(bundle)]) == 1
    monkeypatch.setattr(CHECK, "open", real_open, raising=False)
    real_listdir = os.listdir

    def no_listing(path):
        if os.path.basename(str(path)) == "wheelhouse":
            raise PermissionError(13, "Permission denied", str(path))
        return real_listdir(path)

    monkeypatch.setattr(CHECK.os, "listdir", no_listing)
    assert "would not let synthtwin read wheelhouse" in " ".join(CHECK.check(str(bundle)))


# -- install.sh, run for real on the stub bundle --------------------------------


def _base_python() -> str:
    """A Python that is not itself a private environment (the scripts refuse one)."""
    for candidate in (getattr(sys, "_base_executable", ""), sys.executable):
        if candidate and subprocess.run(
            [candidate, "-c", "import sys; sys.exit(0 if sys.prefix == sys.base_prefix else 1)"],
            check=False,
        ).returncode == 0:
            return candidate
    pytest.skip("no Python outside a private environment to install with")


def _install(bundle: pathlib.Path, *arguments: str, **extra: str) -> "subprocess.CompletedProcess[str]":
    """sh scripts/install.sh in the bundle, with every proxy at a closed port."""
    dead = "http://127.0.0.1:9"
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": os.environ.get("HOME", str(bundle)),
        "SYNTHTWIN_PYTHON": _base_python(),
        "HTTP_PROXY": dead,
        "HTTPS_PROXY": dead,
        "http_proxy": dead,
        "https_proxy": dead,
        "ALL_PROXY": dead,
        "PIP_INDEX_URL": dead + "/simple",
    }
    env.update(extra)
    return subprocess.run(
        [shutil.which("sh") or "/bin/sh", "scripts/install.sh", *arguments],
        cwd=bundle,
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )


posix_only = pytest.mark.skipif(
    os.name == "nt", reason="install.sh is the macOS and Linux script; CI runs install.bat"
)


# What pip prints when it reaches for the network: a download, an index
# or a find-links URL it looks in, and -- with every proxy at a closed
# port, or no network at all -- the retries and connection errors of a
# lookup that failed. "Looking in indexes" alone is printed only for an
# index other than PyPI's, so an install that went to PyPI and fell back
# on the bundle printed none of the first three (lane DEP-2's skeptic,
# item 5). bundle-test's grep names every one of these.
NETWORK_WORDS = (
    "Downloading",
    "Looking in indexes",
    "Looking in links: http",
    "Retrying",
    "Could not fetch URL",
    "ProxyError",
    "NewConnectionError",
    "Failed to establish",
    "pypi.org",
    "files.pythonhosted.org",
)


def _reached_for_network(said: str) -> "list[str]":
    return [word for word in NETWORK_WORDS if word in said]


@posix_only
def test_install_sh_installs_from_the_bundle_alone(tmp_path: pathlib.Path) -> None:
    bundle = _bundle(tmp_path)
    ran = _install(bundle)
    said = ran.stdout + ran.stderr
    assert ran.returncode == 0, said
    assert "The bundle's files match their hashes." in said
    assert "stand-in doctor ran: doctor the stand-in library loaded" in said
    assert "synthtwin is installed." in said
    assert _reached_for_network(said) == [], said
    assert (bundle / ".venv" / "bin" / "synthtwin").exists()


@posix_only
def test_an_install_that_reaches_for_an_index_is_seen(tmp_path: pathlib.Path) -> None:
    """Mutation case of the real run: install.sh without --no-index on the lock install.

    Measured by the skeptic: pip tries PyPI through the closed proxy,
    retries, falls back on the bundle and the script ends "synthtwin is
    installed" with exit 0 -- so only the retries and errors show it.
    """
    bundle = _bundle(tmp_path)
    script = bundle / "scripts" / "install.sh"
    text = script.read_text(encoding="utf-8")
    mutated = text.replace('    --no-index --find-links "$wheels" \\\n', '    --find-links "$wheels" \\\n')
    assert mutated != text
    script.write_text(mutated, encoding="utf-8", newline="\n")
    _resum(bundle)
    ran = _install(bundle)
    said = ran.stdout + ran.stderr
    assert _reached_for_network(said), said


@posix_only
def test_install_sh_stops_before_the_environment_when_a_library_is_missing(
    tmp_path: pathlib.Path,
) -> None:
    """The lock names a library the wheelhouse lacks: the check stops it, nothing is fetched,
    and an earlier environment stays as it was (Codex's review of lane DEP-2, item 5)."""
    bundle = _bundle(tmp_path)
    ran = _install(bundle)
    assert ran.returncode == 0, ran.stdout + ran.stderr
    kept = bundle / ".venv" / "kept-by-the-check.txt"
    kept.write_text("an earlier environment\n", encoding="utf-8", newline="\n")
    (bundle / "wheelhouse" / "stubdep-1.0-py3-none-any.whl").unlink()
    _resum(bundle)
    ran = _install(bundle)
    said = ran.stdout + ran.stderr
    assert ran.returncode == 1, said
    assert "has no file of stubdep that this computer and its Python" in " ".join(said.split())
    assert "the bundle's check above did not pass" in said
    assert _reached_for_network(said) == [], said
    assert "stand-in doctor ran" not in said
    assert kept.exists() and (bundle / ".venv" / "bin" / "synthtwin").exists()


@posix_only
@pytest.mark.parametrize("form", ["by its name", "by its path"])
def test_install_sh_installs_from_a_folder_whose_name_holds_a_semicolon(
    tmp_path: pathlib.Path, form: str
) -> None:
    """Lane DEP-2's verify, item 3: pip reads a ';' in a file's path as a condition.

    synthtwin is installed by its name from the wheelhouse; installed by
    its file's path, as before, the bundle under `notes;old` stops (the
    mutation case).
    """
    bundle = _bundle(tmp_path, parent="notes;old")
    if form == "by its path":
        script = bundle / "scripts" / "install.sh"
        text = script.read_text(encoding="utf-8")
        mutated = text.replace('--no-deps --find-links "$wheels" synthtwin', '--no-deps "$wheel"')
        assert mutated != text
        script.write_text(mutated, encoding="utf-8", newline="\n")
        _resum(bundle)
    ran = _install(bundle)
    said = ran.stdout + ran.stderr
    if form == "by its name":
        assert ran.returncode == 0, said
        assert "stand-in doctor ran: doctor the stand-in library loaded" in said
    else:
        assert ran.returncode == 1 and "stand-in doctor ran" not in said, said


# A stand-in Python of any version (3.14t: the free-threaded build): the
# real interpreter, with sys.version_info and sys.version replaced before
# it runs what it was given (-c CODE or a script), so each script's own
# version test runs on it as written; asked to run a module (-m venv), it
# stops.
_FAKER = """import runpy
import sys

spoken = sys.argv[1]
version = tuple(int(part) for part in spoken.rstrip("t").split("."))
sys.version_info = version + (0, "final", 0)
sys.version = spoken.rstrip("t") + ".0 (a stand-in written by tests/test_bundle.py)"
if spoken.endswith("t"):
    # CPython's free-threaded build, as sysconfig names it.
    import sysconfig

    given = sysconfig.get_config_var
    sysconfig.get_config_var = lambda name: 1 if name == "Py_GIL_DISABLED" else given(name)
arguments = sys.argv[2:]
while arguments and arguments[0] in ("-I", "-E", "-s"):
    arguments = arguments[1:]
if arguments[0] == "-c":
    sys.argv = ["-c", *arguments[2:]]
    exec(compile(arguments[1], "<string>", "exec"), {"__name__": "__main__"})
elif arguments[0] == "-m":
    # A stand-in answers about itself and makes nothing: an environment
    # it made would be the real Python's, and a script making one with
    # the wrong Python would pass unseen (lane DEP-2's verify, item 1).
    sys.exit("a stand-in Python runs no module")
else:
    sys.argv = list(arguments)
    runpy.run_path(arguments[0], run_name="__main__")
"""


def _pythons(folder: pathlib.Path, **named: str) -> str:
    """A PATH of stand-in Pythons by name (a version, or "real") and the tools install.sh calls."""
    folder.mkdir(parents=True)
    faker = folder / "faker.py"
    faker.write_text(_FAKER, encoding="utf-8", newline="\n")
    real = _base_python()
    for name, version in named.items():
        if version == "real":
            body = f'#!/bin/sh\nexec "{real}" "$@"\n'
        else:
            body = f'#!/bin/sh\nexec "{real}" -I "{faker}" {version} "$@"\n'
        (folder / name).write_text(body, encoding="utf-8", newline="\n")
        (folder / name).chmod(0o755)
    for tool in ("dirname", "uname"):
        found = shutil.which(tool)
        assert found, tool
        (folder / tool).symlink_to(found)
    return str(folder)


@posix_only
@pytest.mark.parametrize("other", ["3.15", "3.14t"])
def test_install_sh_takes_a_served_python_beside_another(tmp_path: pathlib.Path, other: str) -> None:
    """python3 is 3.15 (the skeptic, item 2 (c)) or the free-threaded 3.14 (Codex's review,
    item 3) and python3.14 works: the script takes 3.14 and makes the environment with it
    (lane DEP-2's verify, item 1: the stand-in makes none)."""
    bundle = _bundle(tmp_path)
    path = _pythons(tmp_path / "pythons", python3=other, python=other, **{"python3.14": "real"})
    ran = _install(bundle, SYNTHTWIN_PYTHON="", PATH=path)
    said = ran.stdout + ran.stderr
    assert ran.returncode == 0, said
    using = [line for line in said.splitlines() if line.startswith("using ")]
    assert len(using) == 1 and "stand-in" not in using[0], using
    assert "synthtwin is installed." in said
    asked = [str(bundle / ".venv" / "bin" / "python"), "-c", "import sys; print(sys.version)"]
    made = subprocess.run(asked, capture_output=True, text=True, check=False).stdout
    real = subprocess.run([_base_python(), *asked[1:]], capture_output=True, text=True, check=False).stdout
    assert made == real and "stand-in" not in made, made


@posix_only
@pytest.mark.parametrize("version", ["3.9", "3.15", "3.14t"])
def test_install_sh_names_the_python_to_install(tmp_path: pathlib.Path, version: str) -> None:
    """No Python the bundle serves: it names the one found and Python 3.14, before any change."""
    bundle = _bundle(tmp_path)
    path = _pythons(tmp_path / "pythons", python3=version, python=version)
    ran = _install(bundle, SYNTHTWIN_PYTHON="", PATH=path)
    assert ran.returncode == 1, ran.stdout
    flowing = " ".join(ran.stdout.split())
    named = version.replace("t", " (free-threaded)")
    assert (
        f"this computer's Python is {named}, and this synthtwin bundle serves Python 3.11, "
        "3.12, 3.13 and 3.14. Install Python 3.14 from python.org"
    ) in flowing, flowing
    assert "INSTALL.txt" in flowing
    assert not (bundle / ".venv").exists()
    ran = _install(bundle, SYNTHTWIN_PYTHON=str(tmp_path / "pythons" / "python3"))
    assert ran.returncode == 1
    assert "which is not Python 3.11, 3.12, 3.13 or 3.14" in " ".join(ran.stdout.split())
    assert not (bundle / ".venv").exists()


@posix_only
def test_install_sh_refuses_before_changing_anything(tmp_path: pathlib.Path) -> None:
    """A missing hash and an argument stop it before the environment."""
    bundle = _bundle(tmp_path)
    sums = bundle / "SHA256SUMS"
    whole = sums.read_text(encoding="utf-8")
    sums.write_text(
        "".join(line + "\n" for line in whole.splitlines() if "stubdep" not in line),
        encoding="utf-8",
        newline="\n",
    )
    ran = _install(bundle)
    assert ran.returncode == 1 and "has no hash in SHA256SUMS" in ran.stdout, ran.stdout
    assert "the bundle's check above did not pass" in ran.stdout
    assert not (bundle / ".venv").exists()
    sums.write_text(whole, encoding="utf-8", newline="\n")

    ran = _install(bundle, "wheelhouse")
    assert ran.returncode == 1 and "this script takes no folder" in ran.stdout, ran.stdout
    assert not (bundle / ".venv").exists()


@posix_only
def test_install_sh_in_the_source_folder_says_it_is_not_a_bundle(tmp_path: pathlib.Path) -> None:
    """Run from a copy of the repository, it points to README's bundle (the skeptic, item 10)."""
    source = tmp_path / "synthtwin"
    (source / "scripts").mkdir(parents=True)
    (source / "src" / "synthtwin").mkdir(parents=True)
    for name in ("pyproject.toml", "requirements-install.lock"):
        shutil.copyfile(REPO / name, source / name)
    shutil.copyfile(SCRIPTS / "install.sh", source / "scripts" / "install.sh")
    ran = _install(source)
    flowing = " ".join(ran.stdout.split())
    assert ran.returncode == 1, flowing
    assert "this is synthtwin's source folder, not a bundle" in flowing
    assert "'Then get the synthtwin bundle'" in flowing
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    assert "**Then get the synthtwin bundle" in readme
    assert not (source / ".venv").exists()


# -- both scripts' text -----------------------------------------------------------


MATRIX = ("3.11", "3.12", "3.13", "3.14")


def _version_range(pythons: "tuple[str, ...] | list[str]" = MATRIX) -> str:
    """The one version test both scripts write: the first served Python to the last."""
    low, high = (tuple(int(part) for part in item.split(".")) for item in (pythons[0], pythons[-1]))
    return f"{low} <= sys.version_info[:2] <= {high}"


def _candidates(name: str, pythons: "tuple[str, ...] | list[str]" = MATRIX) -> str:
    """The Pythons a script tries, in order: the one a person types, then each served one, newest first."""
    newest_first = list(reversed(pythons))
    if name == "install.sh":
        return "for candidate in python3 python " + " ".join("python" + item for item in newest_first) + "; do"
    return "call :served python\n" + "".join(f"if not defined PY call :served py -{item}\n" for item in newest_first)


_CHECK_LINE = {
    "install.sh": '"$python" -I "$here/scripts/check_bundle.py" "$here"',
    "install.bat": '%PY% -I "%HERE%\\scripts\\check_bundle.py" "%HERE%"',
}
# The environment is made with the Python the script chose (lane
# DEP-2's verify, item 1: `python3 -m venv` beside a chosen python3.14
# passed every rule), and synthtwin is installed by its name from the
# wheelhouse, never by its file's path, which pip reads a ';' in as a
# condition (the verify's item 3).
_VENV_LINE = {
    "install.sh": '"$python" -m venv --clear "$env_dir"',
    "install.bat": '%PY% -m venv --clear "%ENVDIR%"',
}
_SYNTHTWIN_PIP = {
    "install.sh": '--no-index --no-deps --find-links "$wheels" synthtwin || stop',
    "install.bat": '--no-index --no-deps --find-links "%WHEELS%" synthtwin',
}
# The usual CPython alone is served (Codex's review of lane DEP-2, item 3).
_KIND = {
    "install.sh": ' and sys.implementation.name == "cpython" and not sysconfig.get_config_var("Py_GIL_DISABLED")',
    "install.bat": " and sys.implementation.name == 'cpython' and not sysconfig.get_config_var('Py_GIL_DISABLED')",
}
_REFUSE_LINE = {
    "install.sh": 'if [ "$#" -ne 0 ]; then',
    "install.bat": 'if not "%~1"=="" goto :takes_no_folder',
}


def _stops_after(name: str, text: str, line: str) -> bool:
    """The command on ``line`` stops the script when it fails.

    install.sh: the command ends in `|| stop`. install.bat: the next line
    is `if errorlevel 1 goto :LABEL`, and LABEL's block ends `exit /b 1`.
    """
    if name == "install.sh":
        return "|| stop " in line
    lines = text.splitlines()
    index = lines.index(line)
    following = lines[index + 1].strip() if index + 1 < len(lines) else ""
    label = re.fullmatch(r"if errorlevel 1 goto :(\w+)", following)
    if label is None:
        return False
    block = re.search(rf"\n:{label.group(1)}\n(.*?)\nexit /b (\S+)", "\n" + text, re.S)
    return block is not None and block.group(2) == "1"


def script_problems(name: str, text: str, pythons: "tuple[str, ...] | list[str]" = MATRIX) -> "list[str]":
    """What in an install script could reach past the bundle or skip its check.

    Every pip command installs, with --isolated and --no-index, this
    computer's pip configuration files set aside ON THE COMMAND (install.sh's
    pip lines begin `PIP_CONFIG_FILE=/dev/null`; install.bat sets it to nul
    on a line of its own before its first pip; a comment does not count:
    with --isolated alone pip 24 still reads the global and site files,
    and a find-links named there reaches the network, the skeptic's item
    4); the lock is installed with --require-hashes; nothing is
    downloaded or fetched; the check, the environment and each pip
    command stop the script when they fail; every version test is the
    one range, 3.11 to 3.14, and the Pythons are tried in their order;
    the script refuses an argument first, then finds its Python, then
    runs the check, then makes the environment.
    """
    problems: "list[str]" = []
    text = text.replace("\r\n", "\n")
    flat = re.sub(r"\\\n\s*", " ", text)
    pips = [line for line in flat.splitlines() if re.search(r"-m pip\b|\bpip install\b", line)]
    pips = [line for line in pips if not line.lstrip().startswith(("#", "rem ", "REM "))]
    if len(pips) != 2:
        problems += [f"{name} runs pip {len(pips)} times, not twice"]
    for line in pips:
        if "pip install --isolated" not in line or "--no-index" not in line:
            problems += [f"{name}: a pip command without --isolated and --no-index: {line.strip()}"]
    if not any("--require-hashes -r" in line and "--find-links" in line for line in pips):
        problems += [f"{name}: the lock is not installed --require-hashes from the bundle"]
    for word in ("pip download", "://", "curl ", "wget ", "Invoke-WebRequest", "bitsadmin"):
        if word in text:
            problems += [f"{name} fetches or names a place to fetch from ({word!r})"]
    # pip's own configuration files set aside, on the command itself.
    if name == "install.sh":
        for line in pips:
            if not line.lstrip().startswith('PIP_CONFIG_FILE=/dev/null "$venv_python" -m pip install'):
                problems += [f"{name}: a pip command without PIP_CONFIG_FILE=/dev/null on it: {line.strip()}"]
    else:
        sets = [
            line.strip()
            for line in text.splitlines()
            if "PIP_CONFIG_FILE" in line and not line.lstrip().lower().startswith("rem")
        ]
        first_pip = text.find(pips[0].strip()) if pips else -1
        if sets != ['set "PIP_CONFIG_FILE=nul"'] or not 0 <= text.find(sets[0]) < first_pip:
            problems += [f"{name}: PIP_CONFIG_FILE is not set to nul once, before the first pip: {sets}"]
    venvs = [
        line.strip()
        for line in flat.splitlines()
        if "-m venv" in line and not line.lstrip().startswith(("#", "rem ", "REM "))
    ]
    if len(venvs) != 1 or not venvs[0].startswith(_VENV_LINE[name]):
        problems += [f"{name}: the environment is not made as {_VENV_LINE[name]!r}: {venvs}"]
    ours = [line for line in pips if _SYNTHTWIN_PIP[name] in " ".join(line.split())]
    if len(ours) != 1 or any(word in line for line in pips for word in ('"$wheel"', '"%WHEEL%"')):
        problems += [f"{name}: synthtwin is not installed by its name from the wheelhouse ({_SYNTHTWIN_PIP[name]!r})"]
    if _version_range(pythons) + _KIND[name] not in text:
        problems += [f"{name}: a Python is served without being the usual CPython"]
    # Each step that can fail stops the script.
    commands = [_CHECK_LINE[name]] + [line.strip() for line in pips]
    commands += [line.strip() for line in flat.splitlines() if "-m venv --clear" in line]
    for command in commands:
        lines = [line for line in (flat if name == "install.sh" else text).splitlines() if command in line.strip()]
        if len(lines) != 1 or not _stops_after(name, flat if name == "install.sh" else text, lines[0]):
            problems += [f"{name}: a failure of `{command[:50]}` does not stop the script"]
    # One version test, the served range, everywhere; the Pythons in order.
    wanted = _version_range(pythons)
    if wanted not in text:
        problems += [f"{name} never tests the version as {wanted}"]
    rest = text.replace(wanted, "")
    if re.search(r"sys\.version_info(?:\[:2\])?\s*[<>]|[<>]=?\s*sys\.version_info", rest):
        problems += [f"{name}: a version test other than {wanted}"]
    tried = text.find(_candidates(name, pythons))
    if tried < 0:
        problems += [f"{name} does not try the Pythons as {_candidates(name, pythons)!r}"]
    checked = text.find(_CHECK_LINE[name])
    made = text.find("-m venv --clear")
    if not 0 <= tried < checked < made:
        problems += [f"{name}: the bundle's check does not run after the Python is found and before the environment"]
    if not 0 <= text.find(_REFUSE_LINE[name]) < tried:
        problems += [f"{name}: an argument is not refused first"]
    return problems


@pytest.mark.parametrize("name", ["install.sh", "install.bat"])
def test_the_scripts_install_from_the_bundle_alone(name: str) -> None:
    text = (SCRIPTS / name).read_text(encoding="utf-8")
    assert script_problems(name, text) == []
    assert "doctor" in text.split("pip install")[-1]


_SH_PIP_LOCK = 'PIP_CONFIG_FILE=/dev/null "$venv_python" -m pip install --isolated \\\n    --disable-pip-version-check \\\n    --no-index --find-links'


@pytest.mark.parametrize(
    "name, mutate",
    [
        ("install.sh", lambda text: text.replace(
            'say ""\n"$env_dir/bin/synthtwin" doctor',
            '"$venv_python" -m pip install --require-hashes -r "$lock"\nsay ""\n"$env_dir/bin/synthtwin" doctor')),
        ("install.sh", lambda text: text.replace("--no-index --no-deps", "--no-deps")),
        ("install.sh", lambda text: text.replace('"$python" -I "$here/scripts/check_bundle.py" "$here"', "true")),
        ("install.sh", lambda text: text.replace('if [ "$#" -ne 0 ]; then', "if false; then")),
        # S3: the configuration files read again (the comment still names the setting).
        ("install.sh", lambda text: text.replace(_SH_PIP_LOCK, _SH_PIP_LOCK.replace("PIP_CONFIG_FILE=/dev/null ", ""))),
        # A failed check, venv or pip goes on.
        ("install.sh", lambda text: text.replace(
            "    || stop \"the bundle's check above did not pass.", "    || say \"the bundle's check above did not pass.")),
        ("install.sh", lambda text: text.replace('--clear "$env_dir" || stop', '--clear "$env_dir" || say')),
        ("install.sh", lambda text: text.replace(
            '    --require-hashes -r "$lock" \\\n    || stop', '    --require-hashes -r "$lock" \\\n    || say')),
        # S7 and the ceiling: a version test of its own, or none above.
        ("install.sh", lambda text: text.replace(
            "sys.exit(0 if (3, 11) <= sys.version_info[:2] <= (3, 14) and",
            "sys.exit(0 if sys.version_info >= (3, 11) and")),
        ("install.sh", lambda text: text.replace(" python3.14 python3.13", " python3.13")),
        ("install.bat", lambda text: text.replace("--isolated --disable-pip-version-check --no-index --find-links",
                                                  "--disable-pip-version-check --find-links")),
        ("install.bat", lambda text: text.replace(
            'set "STATUS=%ERRORLEVEL%"', 'set "STATUS=%ERRORLEVEL%"\r\ncurl https://example.invalid')),
        ("install.bat", lambda text: text.replace('%PY% -I "%HERE%\\scripts\\check_bundle.py" "%HERE%"', "rem")),
        # S1 and S4: a failed check or library install goes on.
        ("install.bat", lambda text: text.replace("if errorlevel 1 goto :bundle_refused\r\n", "")),
        ("install.bat", lambda text: text.replace("if errorlevel 1 goto :no_locked_wheels\r\n", "")),
        ("install.bat", lambda text: text.replace("if errorlevel 1 goto :no_env\r\n", "")),
        # A label that does not stop.
        ("install.bat", lambda text: text.replace(
            "echo what it says, then run this script again.\r\nexit /b 1",
            "echo what it says, then run this script again.\r\nexit /b 0")),
        # S2: the setting gone, or left in a comment only.
        ("install.bat", lambda text: text.replace('set "PIP_CONFIG_FILE=nul"\r\n', "")),
        ("install.bat", lambda text: text.replace('set "PIP_CONFIG_FILE=nul"\r\n', 'rem set "PIP_CONFIG_FILE=nul"\r\n')),
        # S7: one floor lowered; the ceiling gone; a served Python not tried.
        ("install.bat", lambda text: text.replace("(3, 11) <= sys.version_info[:2]", "(3, 9) <= sys.version_info[:2]")),
        ("install.bat", lambda text: text.replace(" <= sys.version_info[:2] <= (3, 14)", " <= sys.version_info[:2]")),
        ("install.bat", lambda text: text.replace("if not defined PY call :served py -3.14\r\n", "")),
        ("install.bat", lambda text: text.replace('if not "%~1"=="" goto :takes_no_folder', "rem")),
        # The verify's V1 and V2: the environment made with another Python.
        ("install.sh", lambda text: text.replace('"$python" -m venv --clear "$env_dir"', 'python3 -m venv --clear "$env_dir"')),
        ("install.bat", lambda text: text.replace('%PY% -m venv --clear "%ENVDIR%"', 'python -m venv --clear "%ENVDIR%"')),
        # The verify's item 3: synthtwin's wheel installed by its path.
        ("install.sh", lambda text: text.replace('--no-deps --find-links "$wheels" synthtwin', '--no-deps "$wheel"')),
        ("install.bat", lambda text: text.replace('--no-deps --find-links "%WHEELS%" synthtwin', '--no-deps "%WHEEL%"')),
        # Codex's item 3: another Python, or the free-threaded build, served.
        ("install.sh", lambda text: text.replace(' and sys.implementation.name == "cpython"', "")),
        ("install.sh", lambda text: text.replace(' and not sysconfig.get_config_var("Py_GIL_DISABLED") else 1)', " else 1)")),
        ("install.bat", lambda text: text.replace(" and sys.implementation.name == 'cpython'", "")),
        ("install.bat", lambda text: text.replace(" and not sysconfig.get_config_var('Py_GIL_DISABLED') else 1)", " else 1)")),
    ],
)
def test_a_script_reaching_past_the_bundle_is_red(name: str, mutate) -> None:
    text = (SCRIPTS / name).read_bytes().decode("utf-8")
    mutated = mutate(text)
    assert mutated != text
    assert script_problems(name, mutated), "the mutant passed"


def test_the_guide_is_plain_and_every_command_is_on_its_own_line() -> None:
    guide = (SCRIPTS / "INSTALL.txt").read_text(encoding="utf-8")
    for heading in ("On a Mac", "On Windows", "If it stops"):
        assert heading in guide
    commands = [line.strip() for line in guide.splitlines() if line.startswith("       ")]
    assert "sh scripts/install.sh" in commands and "scripts\\install.bat" in commands
    assert "python3 --version" in commands and "python --version" in commands
    assert "python3.14 --version" in commands and "py -3.14 --version" in commands
    assert "source .venv/bin/activate" in commands and ".venv\\Scripts\\activate" in commands
    for jargon in ("pip ", "wheel", "venv ", "hash ", "PATH variable", "environment variable"):
        assert jargon not in guide, jargon
    flowing = " ".join(guide.split())
    # The Python to install is named, and a newer one sent away (item 2 (b)).
    assert "newest Python 3 " not in flowing
    assert flowing.count("install Python 3.14: go to python.org, choose Downloads, then the newest Python 3.14 release") == 2
    assert flowing.count("3.15 or later") == 3
    # Which computer each bundle serves (item 3 (c)); the folder inside the
    # folder Windows' Extract All opens (item 9).
    assert "a Mac with an Apple chip (M1 or later), macOS 12 or later" in flowing
    assert "A folder opens. Inside it, double-click the folder named like synthtwin-0.1.0-win_amd64." in flowing


POWERSHELL = (
    "synthtwin prints the commands it suggests for PowerShell. In Command Prompt, where a "
    "name stands between single quotes 'like this', type it between double quotes \"like this\", "
    "and where two single quotes stand together inside it, as in 'Crohn''s disease', type one: "
    "\"Crohn's disease\"."
)


def test_windows_is_told_how_to_type_what_synthtwin_prints() -> None:
    """Item 7: the guide and install.bat send people to Command Prompt; synthtwin prints PowerShell."""
    guide = " ".join((SCRIPTS / "INSTALL.txt").read_text(encoding="utf-8").split())
    assert POWERSHELL in guide
    windows = guide[guide.index("On Windows") : guide.index("On Linux")]
    assert POWERSHELL in windows
    batch = (SCRIPTS / "install.bat").read_bytes().decode("utf-8").replace("\r\n", "\n")
    closing = batch[batch.index('"%ENVDIR%\\Scripts\\synthtwin.exe" doctor') : batch.index("exit /b %STATUS%")]
    spoken = " ".join(line[len("echo ") :] for line in closing.splitlines() if line.startswith("echo "))
    assert POWERSHELL in " ".join(spoken.split())
    # The verify's item 4: PowerShell doubles a single quote inside a name;
    # Command Prompt takes it once. README says the same.
    readme = " ".join((REPO / "README.md").read_text(encoding="utf-8").split())
    assert "where it printed `'Crohn''s disease'`, type `\"Crohn's disease\"`" in readme
    from synthtwin import cli

    assert cli._quoted_for_the_shell("Crohn's disease", windows=True) == "'Crohn''s disease'"


# -- the builder -----------------------------------------------------------------------


def test_the_builder_refuses_what_may_not_enter_a_bundle(tmp_path: pathlib.Path) -> None:
    stub = _stub(tmp_path)
    lock = stub["repo"] / "requirements-install.lock"
    assert BUILD.wheelhouse_problems(stub["house"], lock) == []
    (stub["house"] / "stubdep-1.0.tar.gz").write_bytes(b"a source archive")
    _wheel(stub["house"], "unpinned", "1.0", {"unpinned/__init__.py": ""})
    found = " ".join(BUILD.wheelhouse_problems(stub["house"], lock))
    assert "stubdep-1.0.tar.gz is not a wheel" in found
    assert "unpinned-1.0-py3-none-any.whl has a SHA-256 the lock does not pin" in found
    out = tmp_path / "out" / "bundle"
    assert BUILD.assemble(stub["house"], stub["ours"], out, repo=stub["repo"])
    assert not out.exists(), "nothing is written when the wheelhouse has a problem"


def test_the_notices_come_from_the_wheels_and_the_zip_is_the_same_twice(tmp_path: pathlib.Path) -> None:
    bundle = _bundle(tmp_path)
    notices = (bundle / "THIRD-PARTY-NOTICES.txt").read_text(encoding="utf-8")
    assert "stubdep 1.0" in notices and "Licence: MIT" in notices
    assert STUB_LICENCE.strip() in notices
    first = BUILD.zip_folder(bundle, tmp_path / "one.zip")
    second = BUILD.zip_folder(bundle, tmp_path / "two.zip")
    assert first == second == _sha256(tmp_path / "one.zip")
    with zipfile.ZipFile(tmp_path / "one.zip") as archive:
        names = archive.namelist()
    assert all(name.startswith("synthtwin-0.0.1-stub/") for name in names)
    assert "synthtwin-0.0.1-stub/SHA256SUMS" in names


def test_the_zip_has_the_name_readme_gives_it() -> None:
    """synthtwin-<version>-<platform>.zip, holding the folder of the same name (item 9)."""
    named = BUILD.bundle_name(pathlib.Path("dist/synthtwin-0.1.0-py3-none-any.whl"), "win_amd64")
    assert named == "synthtwin-0.1.0-win_amd64"
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    for platform in ("macos_arm64", "win_amd64", "linux_x86_64"):
        assert f"`synthtwin-<version>-{platform}.zip`" in readme, platform
    guide = " ".join((SCRIPTS / "INSTALL.txt").read_text(encoding="utf-8").split())
    assert "named like synthtwin-0.1.0-macos_arm64" in guide
    assert "named like synthtwin-0.1.0-win_amd64" in guide


def test_nothing_the_builder_makes_can_be_committed() -> None:
    """Wheels, notices and sums are ignored by git; the builder writes outside the tree."""
    ignored = (REPO / ".gitignore").read_text(encoding="utf-8").splitlines()
    for pattern in ("*.whl", "*.zip", "wheelhouse/", "THIRD-PARTY-NOTICES*", "SHA256SUMS"):
        assert pattern in ignored, pattern
    for found in REPO.glob("*"):
        assert not found.name.startswith(("THIRD-PARTY-NOTICES", "SHA256SUMS")), found


# -- the CI jobs ---------------------------------------------------------------------

PLATFORMS = {
    ("ubuntu-latest", "linux_x86_64"),
    ("windows-latest", "win_amd64"),
    ("macos-latest", "macos_arm64"),
}
NEW_JOBS = ("bundle-build", "bundle-test", "numba-vectors")
GOLDEN = (
    "tests/test_twin_golden.py",
    "tests/test_generation_reference.py",
    "tests/test_numeric_reference.py",
)


def jobs_of(text: str) -> "dict[str, str]":
    """Each job's block of the workflow, by name, read by indentation.

    Refuses (raises ValueError) a tab, an odd indentation or a job
    without runs-on and steps -- the structure every job here keeps.
    """
    if "\t" in text:
        raise ValueError("the workflow holds a tab")
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip(" ")
        if stripped and (len(line) - len(stripped)) % 2:
            raise ValueError(f"line {number} is indented by an odd number of spaces")
    body = text[text.index("\njobs:\n") + len("\njobs:\n") :]
    heads = list(re.finditer(r"^  ([a-z0-9-]+):\n", body, re.M))
    jobs: "dict[str, str]" = {}
    for index, head in enumerate(heads):
        end = heads[index + 1].start() if index + 1 < len(heads) else len(body)
        block = body[head.end() : end]
        if "\n    runs-on: " not in "\n" + block or "\n    steps:\n" not in "\n" + block:
            raise ValueError(f"job {head.group(1)} has no runs-on or no steps")
        jobs[head.group(1)] = block
    return jobs


def _list(block: str, key: str) -> "list[str]":
    found = re.search(rf"\n\s+{re.escape(key)}: \[([^\]]*)\]", block)
    return [item.strip().strip('"') for item in found.group(1).split(",")] if found else []


def _pairs(block: str) -> "set[tuple[str, str]]":
    return set(re.findall(r"- os: (\S+)\n\s+platform: (\S+)", block))


def bundle_job_problems(text: str) -> "list[str]":
    """Every way the workflow falls short of plan P4-D416's three jobs."""
    try:
        jobs = jobs_of(text)
    except ValueError as error:
        return [f"the workflow does not parse: {error}"]
    problems: "list[str]" = []
    pythons = _list(jobs.get("tests", ""), "python-version")
    if pythons != ["3.11", "3.12", "3.13", "3.14"]:
        problems += [f"the tests matrix's Pythons read {pythons}"]
    gate = jobs.get("gate", "")
    for job in NEW_JOBS:
        if job not in jobs:
            problems += [f"no {job} job"]
        needs = gate[gate.index("needs:") : gate.index("]")] if "needs:" in gate else ""
        if not re.search(rf"\b{job},", needs) or f'"{job}",' not in gate:
            problems += [f"the gate does not require {job}"]
    build = jobs.get("bundle-build", "")
    if "\n    needs: build\n" not in "\n" + build:
        problems += ["bundle-build does not wait for the build job's wheel"]
    if _pairs(build) != PLATFORMS:
        problems += [f"bundle-build's platforms read {sorted(_pairs(build))}"]
    for version in pythons:
        if f'python-version: "{version}"' not in build:
            problems += [f"bundle-build downloads no wheels for Python {version}"]
    for needed in (
        "pip download --require-hashes --only-binary=:all:",
        "tools/bundle/build_bundle.py",
        "scripts/check_bundle.py",
        "actions/upload-artifact@",
        # The zip README names, synthtwin-<version>-<platform>.zip (item 9).
        '--zip-into "$RUNNER_TEMP/zipped"',
        "zipped/synthtwin-*-${{ matrix.platform }}.zip",
        # The wheels macOS 12 takes, and none needing a newer macOS (item 3).
        "--platform macosx_12_0_arm64 --implementation cp",
        # ... and the step stops on one (the verify's item 2, V3).
        "grep -E 'macosx_(1[3-9]|[2-9][0-9])_'; then\n"
        '            echo "A wheel above needs a macOS newer than 12; the bundle serves macOS 12 and later."\n'
        "            exit 1\n",
    ):
        if needed not in build:
            problems += [f"bundle-build lacks {needed!r}"]
    tested = jobs.get("bundle-test", "")
    if "\n    needs: bundle-build\n" not in "\n" + tested:
        problems += ["bundle-test does not wait for bundle-build"]
    if _pairs(tested) != PLATFORMS:
        problems += [f"bundle-test's platforms read {sorted(_pairs(tested))}"]
    if _list(tested, "python-version") != pythons:
        problems += [f"bundle-test's Pythons read {_list(tested, 'python-version')}"]
    for needed in (
        "sudo unshare --net",
        "http://127.0.0.1:9",
        "the network is NOT denied",
        "offline sh scripts/install.sh",
        'offline cmd.exe /d /c "scripts\\\\install.bat"',
        '"$ST" profile',
        '"$ST" generate',
        '"$ST" validate',
        # Every word pip prints when it reaches for the network (item 5).
        "|".join(NETWORK_WORDS),
        # The install used this cell's Python, not another one on the runner.
        "PYTHON_CELL: ${{ matrix.python-version }}",
        "if used != [sys.argv[1]]:",
        # A copy with one changed byte is refused, nothing made (item 4).
        "data[len(data) // 2] ^= 1",
        'if offline cmd.exe /d /c "scripts\\\\install.bat" > refused.log 2>&1; then',
        "if offline sh scripts/install.sh > refused.log 2>&1; then",
        'grep -q "does not match its hash in SHA256SUMS" refused.log',
        "test ! -e .venv",
        *GOLDEN,
    ):
        if needed not in tested:
            problems += [f"bundle-test lacks {needed!r}"]
    # Whatever runs the installed synthtwin, its tests or an install
    # script runs with the network denied (item 4: the golden tests ran
    # online with `offline` taken off their line, and the gate stayed green).
    for line in tested.splitlines():
        spoken = line.strip()
        if re.search(r'"\$ST" |-m pytest|scripts/install\.sh|install\.bat"', spoken) and not spoken.startswith(
            ("offline ", "if offline ", "#")
        ):
            problems += [f"bundle-test runs this with the network on: {spoken}"]
    # sudo strips LD_* variables; setup-python's Python may need its
    # library path inside the namespace (item 11).
    linux = tested.count("sudo unshare --net")
    if linux < 3 or tested.count('"LD_LIBRARY_PATH=${LD_LIBRARY_PATH:-}" "$@"; }') != linux:
        problems += ["a Linux offline() drops LD_LIBRARY_PATH"]
    for step in tested.split("      - name: ")[1:]:
        if "offline " in step and (
            "sudo unshare --net" not in step or "http://127.0.0.1:9" not in step
        ):
            problems += [f"a bundle-test step runs offline without denying the network: {step.splitlines()[0]}"]
    vectors = jobs.get("numba-vectors", "")
    if _list(vectors, "os") != ["ubuntu-latest", "windows-latest", "macos-latest"]:
        problems += [f"numba-vectors' systems read {_list(vectors, 'os')}"]
    if _list(vectors, "python-version") != pythons:
        problems += [f"numba-vectors' Pythons read {_list(vectors, 'python-version')}"]
    for needed in ('SYNTHTWIN_REQUIRE_NUMBA: "1"', "tests/test_numba_vectors.py"):
        if needed not in vectors:
            problems += [f"numba-vectors lacks {needed!r}"]
    for word in (
        "twine upload",
        "gh release",
        "gh-action-pypi-publish",
        "action-gh-release",
        "upload-release-asset",
        "contents: write",
        "id-token: write",
    ):
        if word in text:
            problems += [f"the workflow publishes ({word!r})"]
    for used in re.findall(r"uses: (\S+)", text):
        if not re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", used):
            problems += [f"an action not pinned by its commit: {used}"]
    return problems


def test_the_ci_jobs_parse_and_name_every_platform() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert bundle_job_problems(text) == []
    assert set(NEW_JOBS) <= set(jobs_of(text))
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        return
    loaded = yaml.safe_load(text)
    assert set(loaded["jobs"]) == set(jobs_of(text))


@pytest.mark.parametrize(
    "old, new",
    [
        ("          - os: macos-latest\n            platform: macos_arm64\n    runs-on: ${{ matrix.os }}",
         "    runs-on: ${{ matrix.os }}"),
        ('python-version: ["3.11", "3.12", "3.13", "3.14"]\n        system:',
         'python-version: ["3.11", "3.12", "3.13"]\n        system:'),
        ("        bundle-test,\n", ""),
        ('              "numba-vectors",\n', ""),
        ("sudo unshare --net", "sudo"),
        ("tests/test_twin_golden.py tests/test_generation_reference.py", "tests/test_generation_reference.py"),
        ("      - name: Hand the bundle to bundle-test", "      - name: Release\n        run: gh release upload v1 bundle.zip\n      - name: Hand the bundle to bundle-test"),
        ("os: [ubuntu-latest, windows-latest, macos-latest]\n        python-version",
         "os: [ubuntu-latest, macos-latest]\n        python-version"),
        ("  bundle-test:\n", "  bundle-test:\n\t"),
        # S6: the golden tests, or a run of synthtwin, with the network on.
        ('offline env "PYTHONPATH=$RUNNER_TEMP/pytest-only" "$BPY" -m pytest',
         'env "PYTHONPATH=$RUNNER_TEMP/pytest-only" "$BPY" -m pytest'),
        ('offline "$ST" generate', '"$ST" generate'),
        # S5's grep: the retries of a lookup PyPI never answered not read.
        ("|Retrying|Could not fetch URL", "|Could not fetch URL"),
        ('"LD_LIBRARY_PATH=${LD_LIBRARY_PATH:-}" "$@"; }', '"$@"; }'),
        ("--platform macosx_12_0_arm64 --implementation cp \\\n", ""),
        ('grep -q "does not match its hash in SHA256SUMS" refused.log\n', ""),
        ("          if used != [sys.argv[1]]:\n", "          if not used:\n"),
        ('--zip-into "$RUNNER_TEMP/zipped"', '--zip "$RUNNER_TEMP/synthtwin-bundle-${{ matrix.platform }}.zip"'),
        ('the bundle serves macOS 12 and later."\n            exit 1\n', 'the bundle serves macOS 12 and later."\n'),
    ],
)
def test_a_ci_job_short_of_the_plan_is_red(old: str, new: str) -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert old in text, old
    assert bundle_job_problems(text.replace(old, new, 1)), "the mutant passed"
