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


def _bundle(tmp_path: pathlib.Path) -> pathlib.Path:
    stub = _stub(tmp_path)
    out = tmp_path / "a folder with spaces" / "synthtwin-0.0.1-stub"
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
    )
    _refused(bundle, "wheelhouse/stubdep-1.0-py3-none-any.whl has no hash in SHA256SUMS")
    sums.write_text(whole, encoding="utf-8")
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
        with (fresh / script).open("a", encoding="utf-8") as handle:
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
        assert CHECK._lock_problems((REPO / name).read_text(encoding="utf-8")) == [], name


def test_the_check_refuses_a_wrong_python(tmp_path: pathlib.Path) -> None:
    """Older than 3.11 always; another Python than the bundle's wheels serve."""
    bundle = _bundle(tmp_path)
    _refused(bundle, "this computer's Python is 3.10, and synthtwin needs Python 3.11", version=(3, 10))
    house = bundle / "wheelhouse"
    for minor in (11, 12, 13, 14):
        _wheel(house, "stubnative", "1.0", {"stubnative/__init__.py": ""},
               tags=f"cp3{minor}-cp3{minor}-macosx_11_0_arm64")
    # A wheel for any Python 3 (abi3) names no Python the bundle serves.
    _wheel(house, "stubabi", "1.0", {"stubabi/__init__.py": ""},
           tags="cp37-abi3-macosx_11_0_arm64")
    lock = bundle / "requirements-install.lock"
    added = ""
    for project in ("stubnative", "stubabi"):
        pins = "".join(
            f"    --hash=sha256:{_sha256(path)} \\\n" for path in sorted(house.glob(project + "-*"))
        )
        added += f"{project}==1.0 \\\n" + pins.rstrip(" \\\n") + "\n"
    lock.write_text(lock.read_text(encoding="utf-8") + added, encoding="utf-8", newline="\n")
    _resum(bundle)
    assert CHECK.check(str(bundle), version=(3, 13), system="macOS") == []
    _refused(
        bundle,
        "holds the libraries for Python 3.11, 3.12, 3.13, 3.14, and the Python found is 3.15",
        version=(3, 15),
        system="macOS",
    )
    _refused(bundle, "this bundle is made for macOS, and this computer runs Windows",
             version=(3, 13), system="Windows")


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
        ["sh", "scripts/install.sh", *arguments],
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


@posix_only
def test_install_sh_installs_from_the_bundle_alone(tmp_path: pathlib.Path) -> None:
    bundle = _bundle(tmp_path)
    ran = _install(bundle)
    said = ran.stdout + ran.stderr
    assert ran.returncode == 0, said
    assert "The bundle's files match their hashes." in said
    assert "stand-in doctor ran: doctor the stand-in library loaded" in said
    assert "synthtwin is installed." in said
    assert "Downloading" not in said and "Looking in indexes" not in said
    assert (bundle / ".venv" / "bin" / "synthtwin").exists()


@posix_only
def test_install_sh_stops_and_never_fetches_when_a_library_is_missing(
    tmp_path: pathlib.Path,
) -> None:
    """The lock names a library the wheelhouse lacks: pip stops, so does the script."""
    bundle = _bundle(tmp_path)
    (bundle / "wheelhouse" / "stubdep-1.0-py3-none-any.whl").unlink()
    _resum(bundle)
    ran = _install(bundle)
    said = ran.stdout + ran.stderr
    assert ran.returncode == 1, said
    assert "pip could not install the bundle's libraries" in said
    assert "Downloading" not in said and "Looking in indexes" not in said
    assert "stand-in doctor ran" not in said


@posix_only
def test_install_sh_refuses_before_changing_anything(tmp_path: pathlib.Path) -> None:
    """A missing hash, a wrong Python and an argument stop it before the environment."""
    bundle = _bundle(tmp_path)
    sums = bundle / "SHA256SUMS"
    whole = sums.read_text(encoding="utf-8")
    sums.write_text(
        "".join(line + "\n" for line in whole.splitlines() if "stubdep" not in line),
        encoding="utf-8",
    )
    ran = _install(bundle)
    assert ran.returncode == 1 and "has no hash in SHA256SUMS" in ran.stdout, ran.stdout
    assert "the bundle's check above did not pass" in ran.stdout
    assert not (bundle / ".venv").exists()
    sums.write_text(whole, encoding="utf-8")

    ran = _install(bundle, "wheelhouse")
    assert ran.returncode == 1 and "this script takes no folder" in ran.stdout, ran.stdout
    assert not (bundle / ".venv").exists()

    fake = tmp_path / "old python"
    fake.mkdir()
    for name in ("python3", "python"):
        old = fake / name
        old.write_text(
            '#!/bin/sh\ncase "$2" in\n  *">= (3, 11)"*) exit 1 ;;\n  *version_info*) echo 3.9 ;;\nesac\n',
            encoding="utf-8",
        )
        old.chmod(0o755)
    ran = _install(bundle, SYNTHTWIN_PYTHON="", PATH=f"{fake}:/usr/bin:/bin")
    assert ran.returncode == 1, ran.stdout
    assert "this computer's Python is 3.9, and synthtwin needs Python 3.11" in ran.stdout
    assert "python.org" in ran.stdout and "INSTALL.txt" in ran.stdout
    assert not (bundle / ".venv").exists()
    ran = _install(bundle, SYNTHTWIN_PYTHON=str(fake / "python3"))
    assert ran.returncode == 1 and "which is not Python 3.11" in ran.stdout, ran.stdout


# -- both scripts' text -----------------------------------------------------------


def script_problems(name: str, text: str) -> "list[str]":
    """What in an install script could reach past the bundle or skip its check.

    Every pip command installs, with --isolated and --no-index; the lock
    is installed with --require-hashes; nothing is downloaded or fetched;
    the check runs after the Python floor and before the environment is
    made; the script refuses an argument before anything else.
    """
    problems: "list[str]" = []
    flat = re.sub(r"\\\n\s*", " ", text.replace("\r\n", "\n"))
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
    called = re.search(r'-I "[^"\n]*check_bundle\.py" "', text)
    checked = called.start() if called else -1
    made = text.find("-m venv --clear")
    floor = text.find("(3, 11)")
    if not 0 <= floor < checked < made:
        problems += [f"{name}: the bundle's check does not run after the floor and before the environment"]
    refuse = text.find('if [ "$#" -ne 0 ]') if name == "install.sh" else text.find('if not "%~1"=="" goto :takes_no_folder')
    if not 0 <= refuse < floor:
        problems += [f"{name}: an argument is not refused first"]
    return problems


@pytest.mark.parametrize("name", ["install.sh", "install.bat"])
def test_the_scripts_install_from_the_bundle_alone(name: str) -> None:
    text = (SCRIPTS / name).read_text(encoding="utf-8")
    assert script_problems(name, text) == []
    assert "PIP_CONFIG_FILE" in text and "doctor" in text.split("pip install")[-1]


@pytest.mark.parametrize(
    "name, mutate",
    [
        ("install.sh", lambda text: text.replace(
            'say ""\n"$env_dir/bin/synthtwin" doctor',
            '"$venv_python" -m pip install --require-hashes -r "$lock"\nsay ""\n"$env_dir/bin/synthtwin" doctor')),
        ("install.sh", lambda text: text.replace("--no-index --no-deps", "--no-deps")),
        ("install.sh", lambda text: text.replace('"$python" -I "$here/scripts/check_bundle.py" "$here"', "true")),
        ("install.sh", lambda text: text.replace('if [ "$#" -ne 0 ]; then', "if false; then")),
        ("install.bat", lambda text: text.replace("--isolated --disable-pip-version-check --no-index --find-links",
                                                  "--disable-pip-version-check --find-links")),
        ("install.bat", lambda text: text.replace(
            'set "STATUS=%ERRORLEVEL%"', 'set "STATUS=%ERRORLEVEL%"\r\ncurl https://example.invalid')),
        ("install.bat", lambda text: text.replace('%PY% -I "%HERE%\\scripts\\check_bundle.py" "%HERE%"', "rem")),
    ],
)
def test_a_script_reaching_past_the_bundle_is_red(name: str, mutate) -> None:
    text = (SCRIPTS / name).read_text(encoding="utf-8")
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
    assert "source .venv/bin/activate" in commands and ".venv\\Scripts\\activate" in commands
    for jargon in ("pip ", "wheel", "venv ", "hash ", "PATH variable", "environment variable"):
        assert jargon not in guide, jargon


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
        "Downloading|Looking in indexes",
        *GOLDEN,
    ):
        if needed not in tested:
            problems += [f"bundle-test lacks {needed!r}"]
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
    ],
)
def test_a_ci_job_short_of_the_plan_is_red(old: str, new: str) -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert old in text, old
    assert bundle_job_problems(text.replace(old, new, 1)), "the mutant passed"
