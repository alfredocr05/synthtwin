"""Data-provenance guard for the synthtwin repository (plan D13).

Policy: no real data and no real-derived artifact ever enters the
repository. Test fixtures are produced by seeded neutral scripts committed
as code. A committed fixture file is allowed only if it is tiny and listed
in the fixture manifest (tools/provenance/fixture-manifest.json), which
binds: path -> generator script -> seed -> sha256 -> justification.

What this checker does:

1. Enumerates the repository tree. Inside a git repository it asks git for
   the tracked file list (``git ls-files``); if git is unavailable, or the
   repository has no tracked files yet (fresh clone before the first
   commit), it walks the directory tree instead, skipping ``.git``.
2. Fails on any data-format file (tabular, columnar, array, statistical-
   package, database, spreadsheet, JSON/JSON Lines, and archive forms;
   see DATA_SUFFIXES and ARCHIVE_SUFFIXES below) that is not listed in
   the manifest allowlist. A tracked .json file is allowed only when it
   is one of the checker's known configuration files (KNOWN_CONFIG_JSON)
   or listed in the fixture manifest; every other .json is a violation.
3. For every fixture listed in the manifest -- whatever its extension --
   it re-runs the named generator script with the recorded seed and
   byte-compares the freshly produced output to the committed file. Any
   difference (forged header, edited bytes, substituted content) fails.
   It also checks the committed bytes against the recorded sha256 and
   enforces the "tiny" policy with a hard size cap.
4. Confines every manifest entry to reviewed repository code: fixture
   and generator paths must be repository-relative (no absolute paths,
   no ".." components), must stay inside the repository, and must be
   tracked by git once the repository has commits.

Generator convention (recorded here and in the manifest schema note):
a generator is invoked as

    python <generator-script> --seed <seed> --out <output-path>

and must write the complete fixture bytes to the output path. The same
seed must always produce the same bytes, on every platform. Generators
must never touch the network; the checker enforces this by running every
generator through tools/provenance/guard_runner.py, which replaces the
socket entry points with raising stubs before the generator code runs.

Exit codes: 0 = clean; 1 = policy violation (unlisted data file, byte
mismatch, oversized fixture, broken generator); 2 = the checker could not
run (missing or malformed manifest, unreadable tree).

This script uses only the Python standard library. Subprocess use is
permitted in tools/ (the D6 restriction applies to src/ only).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath

# Hard cap enforcing the D13 "tiny" rule for committed fixtures, in bytes.
MAX_FIXTURE_BYTES = 100_000

# Seconds a single generator run may take before the checker gives up.
GENERATOR_TIMEOUT_SECONDS = 120

# Data-format extensions that must never be committed without an
# allowlist entry (plan D13). Compared case-insensitively against the
# final extension of the file name.
DATA_SUFFIXES = {
    ".csv",
    ".tsv",
    ".parquet",
    ".xlsx",
    ".xls",
    ".feather",
    ".pkl",
    ".pickle",
    ".db",
    ".json",
    ".jsonl",
    ".ndjson",
    ".arrow",
    ".orc",
    ".avro",
    ".dta",
    ".sas7bdat",
    ".sav",
    ".zsav",
    ".rds",
    ".rdata",
    ".h5",
    ".hdf5",
    ".npz",
    ".npy",
    ".mat",
    ".mdb",
    ".accdb",
    ".ods",
}

# Tracked .json files that are known configuration files of this
# repository's own guard tooling. Any other tracked .json file is
# treated as a data file and needs a fixture-manifest entry.
KNOWN_CONFIG_JSON = {
    "tools/provenance/fixture-manifest.json",
    "tools/decontamination/attestation.json",
}

ARCHIVE_SUFFIXES = {
    ".zip",
    ".tar",
    ".gz",
    ".tgz",
    ".bz2",
    ".tbz2",
    ".xz",
    ".txz",
    ".7z",
    ".rar",
    ".zst",
}

REQUIRED_ENTRY_KEYS = ("path", "generator", "seed", "sha256", "justification")


def file_suffix(relative_path: str) -> str:
    """Return the lowercased final extension of the path, or ''."""
    name = relative_path.rsplit("/", 1)[-1].lower()
    dot = name.rfind(".")
    if dot <= 0:
        return ""
    return name[dot:]


def is_data_format(relative_path: str) -> bool:
    """Return True if the path looks like a data-format or archive file.

    ``.json`` counts as a data format here; ``check_tree`` exempts only
    the known configuration files listed in KNOWN_CONFIG_JSON and paths
    listed in the fixture manifest.
    """
    suffix = file_suffix(relative_path)
    if not suffix:
        return False
    if suffix in DATA_SUFFIXES or suffix in ARCHIVE_SUFFIXES:
        return True
    # .sqlite, .sqlite3, .sqlitedb and friends all match here.
    return suffix.startswith(".sqlite")


def git_tracked_files(root: Path) -> set[str] | None:
    """Return the set of git-tracked root-relative POSIX paths, or None.

    Returns None when the root is not a git repository, git cannot be
    run, or git tracks nothing yet (a fresh tree before the first
    commit). A non-None result means git tracking is authoritative for
    this root.
    """
    if not (root / ".git").exists():
        return None
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            capture_output=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    names = {
        n for n in proc.stdout.decode("utf-8", errors="replace").split("\0") if n
    }
    return names or None


def list_repository_files(root: Path) -> list[str]:
    """Enumerate repository files as sorted root-relative POSIX paths.

    Prefers ``git ls-files`` when the root is a git repository and git
    reports at least one tracked file. Falls back to a directory walk
    (skipping .git) when git is absent, fails, or tracks nothing yet --
    the walk is strictly more protective for a repository whose first
    commit has not happened.
    """
    tracked = git_tracked_files(root)
    if tracked is not None:
        return sorted(tracked)

    # Build/tool noise skipped only in this pre-commit fallback walk; the
    # authoritative post-commit enumeration is `git ls-files`, where the
    # .gitignore rules govern.
    noise = {".git", "__pycache__", ".venv", "venv", ".pytest_cache",
             ".mypy_cache", ".ruff_cache", "dist", "build", "wheelhouse"}
    collected: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames
            if d not in noise and not d.endswith(".egg-info")
        ]
        for filename in filenames:
            full = Path(dirpath) / filename
            collected.append(full.relative_to(root).as_posix())
    return sorted(collected)


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def load_manifest(manifest_path: Path) -> tuple[list[dict], list[str]]:
    """Load and validate the fixture manifest.

    Returns (entries, errors). A non-empty error list means the manifest
    itself is unusable and the checker must stop with exit code 2.
    """
    errors: list[str] = []
    if not manifest_path.is_file():
        errors.append(
            "The fixture manifest is missing. Expected it at: "
            + str(manifest_path)
            + ". Every synthtwin checkout must contain this file; restore it "
            "from version control."
        )
        return [], errors

    try:
        raw = manifest_path.read_text(encoding="utf-8")
        document = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(
            "The fixture manifest could not be read as JSON: "
            + str(manifest_path)
            + " ("
            + str(exc)
            + "). Fix the file so it is valid JSON, or restore it from "
            "version control."
        )
        return [], errors

    if not isinstance(document, dict) or "fixtures" not in document:
        errors.append(
            "The fixture manifest must be a JSON object with a 'fixtures' "
            "list. File: " + str(manifest_path)
        )
        return [], errors

    fixtures = document["fixtures"]
    if not isinstance(fixtures, list):
        errors.append(
            "The 'fixtures' field in the manifest must be a list. File: "
            + str(manifest_path)
        )
        return [], errors

    entries: list[dict] = []
    for index, entry in enumerate(fixtures):
        label = "fixtures[" + str(index) + "]"
        if not isinstance(entry, dict):
            errors.append(
                label + " in the manifest is not a JSON object. Every entry "
                "must have the keys: " + ", ".join(REQUIRED_ENTRY_KEYS) + "."
            )
            continue
        missing = [k for k in REQUIRED_ENTRY_KEYS if k not in entry]
        if missing:
            errors.append(
                label + " is missing required key(s): " + ", ".join(missing)
                + ". Every entry must have: " + ", ".join(REQUIRED_ENTRY_KEYS)
                + "."
            )
            continue
        problems = []
        if not isinstance(entry["path"], str) or not entry["path"]:
            problems.append("'path' must be a non-empty repository-relative path")
        if not isinstance(entry["generator"], str) or not entry["generator"]:
            problems.append(
                "'generator' must be a non-empty repository-relative path to "
                "the script that rebuilds this fixture"
            )
        if not isinstance(entry["seed"], int) or isinstance(entry["seed"], bool):
            problems.append("'seed' must be an integer")
        sha = entry["sha256"]
        if (
            not isinstance(sha, str)
            or len(sha) != 64
            or any(c not in "0123456789abcdef" for c in sha.lower())
        ):
            problems.append("'sha256' must be a 64-character hex digest")
        if not isinstance(entry["justification"], str) or not entry[
            "justification"
        ].strip():
            problems.append(
                "'justification' must be a written sentence explaining why "
                "this fixture is committed"
            )
        if problems:
            errors.append(label + " is invalid: " + "; ".join(problems) + ".")
            continue
        entries.append(entry)

    return entries, errors


def manifest_path_problem(value: str) -> str | None:
    """Lexically reject a manifest path that could leave the repository.

    Returns a short reason string for an absolute path (POSIX or
    Windows form) or a path containing a ".." component, and None for a
    plain repository-relative path.
    """
    normalized = value.replace("\\", "/")
    if (
        PurePosixPath(normalized).is_absolute()
        or PureWindowsPath(value).is_absolute()
        or normalized.startswith("//")
    ):
        return "is an absolute path"
    if ".." in PurePosixPath(normalized).parts:
        return "contains a '..' component"
    return None


def entry_containment_problems(
    root: Path, tracked: set[str] | None, entry: dict
) -> list[str]:
    """Confine one manifest entry to reviewed repository code.

    Checks the fixture path and the generator path: both must be
    repository-relative (no absolute form, no ".." component), must
    resolve to a location inside ``root``, and -- when ``tracked`` is a
    set of git-tracked paths -- must be tracked by git. Returns one
    plain-language violation message per problem.
    """
    problems: list[str] = []
    for field, label in (("path", "fixture path"), ("generator", "generator path")):
        value = entry[field]
        reason = manifest_path_problem(value)
        if reason is None and not (root / value).resolve().is_relative_to(root):
            reason = "points outside the repository"
        if reason is None and tracked is not None and value not in tracked:
            reason = "is not tracked by git"
        if reason is not None:
            problems.append(
                "The manifest entry for fixture '" + entry["path"] + "' has a "
                + label + " that " + reason + ": " + value + ". Fixture and "
                "generator paths must be written relative to the repository "
                "root, must stay inside the repository, and must be tracked "
                "by git once the repository has commits, so the checker only "
                "ever reads and runs reviewed repository files. Fix the "
                "manifest entry."
            )
    return problems


def rebuild_fixture(root: Path, entry: dict) -> tuple[bytes | None, str | None]:
    """Run the entry's generator with its seed; return (bytes, error).

    The generator is never run directly: it is started through the
    no-network guard runner (tools/provenance/guard_runner.py), which
    replaces the socket entry points with raising stubs before the
    generator code runs, so a fixture rebuild can never touch the
    network.
    """
    generator = root / entry["generator"]
    if not generator.is_file():
        return None, (
            "The generator script listed for fixture '" + entry["path"]
            + "' does not exist: " + entry["generator"]
            + ". Restore the script or correct the manifest entry."
        )

    guard_runner = Path(__file__).resolve().parent / "guard_runner.py"
    if not guard_runner.is_file():
        return None, (
            "The no-network guard runner that must wrap every generator "
            "run is missing: " + str(guard_runner) + ". Restore it from "
            "version control."
        )

    with tempfile.TemporaryDirectory(prefix="synthtwin-provenance-") as tmp:
        out_path = os.path.join(tmp, os.path.basename(entry["path"]))
        command = [
            sys.executable,
            str(guard_runner),
            str(generator),
            "--seed",
            str(entry["seed"]),
            "--out",
            out_path,
        ]
        try:
            proc = subprocess.run(
                command,
                cwd=str(root),
                capture_output=True,
                timeout=GENERATOR_TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return None, (
                "The generator for fixture '" + entry["path"] + "' ran longer "
                "than " + str(GENERATOR_TIMEOUT_SECONDS) + " seconds and was "
                "stopped. Fixture generators must be quick; simplify the "
                "script: " + entry["generator"]
            )
        except OSError as exc:
            return None, (
                "The generator for fixture '" + entry["path"] + "' could not "
                "be started (" + str(exc) + "). Check that Python can run "
                "the script: " + entry["generator"]
            )
        if proc.returncode != 0:
            stderr_tail = proc.stderr.decode("utf-8", errors="replace")[-500:]
            return None, (
                "The generator for fixture '" + entry["path"] + "' exited "
                "with an error (exit code " + str(proc.returncode) + "). "
                "Script: " + entry["generator"] + ". Error output: "
                + stderr_tail.strip()
            )
        if not os.path.isfile(out_path):
            return None, (
                "The generator for fixture '" + entry["path"] + "' finished "
                "but wrote nothing to the requested output path. Generators "
                "must write the fixture bytes to the path given by --out. "
                "Script: " + entry["generator"]
            )
        with open(out_path, "rb") as handle:
            return handle.read(), None


def check_tree(root: Path, manifest_path: Path) -> tuple[list[str], list[str]]:
    """Run every provenance check. Returns (violations, setup_errors)."""
    violations: list[str] = []

    root = root.resolve()
    entries, setup_errors = load_manifest(manifest_path)
    if setup_errors:
        return [], setup_errors

    allowlisted_paths = {entry["path"] for entry in entries}
    tracked = git_tracked_files(root)

    # Check 1: no data-format file outside the allowlist. A .json file
    # is additionally exempt when it is one of the checker's known
    # configuration files.
    for relative in list_repository_files(root):
        if not is_data_format(relative):
            continue
        if relative in allowlisted_paths:
            continue
        if file_suffix(relative) == ".json":
            if relative in KNOWN_CONFIG_JSON:
                continue
            violations.append(
                "Found a tracked JSON file that is neither a known "
                "configuration file of this repository's tooling nor on the "
                "fixture allowlist: " + relative + ". JSON files can carry "
                "real-derived tables or profiles, so they are treated as "
                "data files. If this file is a legitimate, tiny test "
                "fixture built by a seeded script, add an entry for it to "
                + manifest_path.name
                + " (path, generator, seed, sha256, justification). "
                "Otherwise delete the file before committing."
            )
            continue
        violations.append(
            "Found a data file that is not on the fixture allowlist: "
            + relative
            + ". Real or unexplained data files may never be committed "
            "to this repository. If this file is a legitimate, tiny test "
            "fixture built by a seeded script, add an entry for it to "
            + manifest_path.name
            + " (path, generator, seed, sha256, justification). "
            "Otherwise delete the file before committing."
        )

    # Check 2: every listed fixture is confined to reviewed repository
    # code, present, tiny, hash-correct, and byte-identical to what its
    # generator produces from its seed.
    for entry in entries:
        containment_problems = entry_containment_problems(root, tracked, entry)
        if containment_problems:
            violations.extend(containment_problems)
            continue

        fixture_path = root / entry["path"]
        if not fixture_path.is_file():
            violations.append(
                "The manifest lists a fixture that does not exist: "
                + entry["path"]
                + ". Either restore the file or remove its manifest entry."
            )
            continue

        size = fixture_path.stat().st_size
        if size > MAX_FIXTURE_BYTES:
            violations.append(
                "The fixture '" + entry["path"] + "' is " + str(size)
                + " bytes, which is larger than the allowed maximum of "
                + str(MAX_FIXTURE_BYTES) + " bytes. Committed fixtures must "
                "be tiny; shrink the fixture or build it at test time "
                "instead of committing it."
            )
            continue

        actual_sha = sha256_of_file(fixture_path)
        if actual_sha != entry["sha256"].lower():
            violations.append(
                "The fixture '" + entry["path"] + "' does not match the "
                "sha256 recorded in the manifest. Recorded: "
                + entry["sha256"] + ". Actual: " + actual_sha + ". Either "
                "the file was changed without updating the manifest, or the "
                "file was replaced. Rebuild the fixture with its generator "
                "and update the manifest entry to match."
            )
            continue

        produced, error = rebuild_fixture(root, entry)
        if error is not None:
            violations.append(error)
            continue
        committed = fixture_path.read_bytes()
        if produced != committed:
            violations.append(
                "The committed fixture '" + entry["path"] + "' is NOT what "
                "its generator produces. Running '" + entry["generator"]
                + "' with seed " + str(entry["seed"]) + " gave "
                + str(len(produced or b"")) + " bytes that differ from the "
                + str(len(committed)) + " committed bytes. This means the "
                "committed file was edited by hand or substituted, which the "
                "provenance policy forbids. Rebuild the file by running: "
                "python " + entry["generator"] + " --seed "
                + str(entry["seed"]) + " --out " + entry["path"]
                + " and commit that output, or investigate where the "
                "committed bytes came from."
            )

    return violations, []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check_provenance",
        description=(
            "synthtwin data-provenance guard: verifies that no data-format "
            "file is committed without a fixture-manifest entry, and that "
            "every listed fixture is byte-identical to what its seeded "
            "generator script produces."
        ),
    )
    default_root = Path(__file__).resolve().parents[2]
    parser.add_argument(
        "--root",
        type=Path,
        default=default_root,
        help="repository root to check (default: this checkout)",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help=(
            "path to fixture-manifest.json (default: "
            "tools/provenance/fixture-manifest.json under the root)"
        ),
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not root.is_dir():
        print(
            "ERROR: the repository root to check does not exist or is not a "
            "directory: " + str(root),
            file=sys.stderr,
        )
        return 2

    manifest_path = args.manifest
    if manifest_path is None:
        manifest_path = root / "tools" / "provenance" / "fixture-manifest.json"
    manifest_path = manifest_path.resolve()

    violations, setup_errors = check_tree(root, manifest_path)

    if setup_errors:
        for message in setup_errors:
            print("ERROR: " + message, file=sys.stderr)
        return 2

    if violations:
        for message in violations:
            print("PROVENANCE VIOLATION: " + message, file=sys.stderr)
        print(
            "\nProvenance check FAILED with " + str(len(violations))
            + " problem(s). Nothing may be pushed until every problem above "
            "is fixed.",
            file=sys.stderr,
        )
        return 1

    print(
        "Provenance check passed: no unlisted data-format files; every "
        "manifest fixture matches its generator output."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
