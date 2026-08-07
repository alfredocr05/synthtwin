"""Tests for the data-provenance guard (plan D13).

The checker is exercised through its command-line interface so the tests
cover exactly what CI runs. Every synthetic tree lives in tmp_path; the
repository itself gains no data-format files from this suite.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "tools" / "provenance" / "check_provenance.py"


def _load_checker_module():
    """Import the checker as a module for direct unit checks."""
    spec = importlib.util.spec_from_file_location("check_provenance", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_CHECKER_MODULE = _load_checker_module()

# A tiny seeded generator, written into tmp trees by the tests below. It
# produces a .txt fixture so the tests never need a data-format file for
# the passing and forged-content cases. The byte rule is trivial on
# purpose: the same seed always yields the same bytes.
GENERATOR_SOURCE = """\
import argparse


def build(seed):
    lines = []
    for i in range(5):
        lines.append("row-" + str(seed * 100 + i))
    return "\\n".join(lines) + "\\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    with open(args.out, "w", encoding="utf-8", newline="") as handle:
        handle.write(build(args.seed))
"""


# A generator that tries to open a real network connection before
# writing its output. Used to prove the no-network guard runner stops
# fixture rebuild runs that touch the socket API.
SOCKET_GENERATOR_SOURCE = """\
import argparse
import socket

parser = argparse.ArgumentParser()
parser.add_argument("--seed", type=int, required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()
connection = socket.create_connection(("127.0.0.1", 9), timeout=1)
connection.close()
with open(args.out, "w", encoding="utf-8", newline="") as handle:
    handle.write("row-" + str(args.seed) + "\\n")
"""

# A generator that drops a sentinel file next to itself when executed.
# Used to prove that a rejected manifest entry is refused BEFORE its
# generator script ever runs.
SENTINEL_GENERATOR_SOURCE = """\
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--seed", type=int, required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()
sentinel = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "ran.sentinel"
)
with open(sentinel, "w", encoding="utf-8") as handle:
    handle.write("the generator ran")
with open(args.out, "w", encoding="utf-8", newline="") as handle:
    handle.write("row\\n")
"""

# Suffixes added to the checker's data-format gate for common
# real-derived artifact forms (JSON Lines, Arrow family, columnar and
# array stores, statistical packages, databases, spreadsheets).
EXTENDED_DATA_SUFFIXES = [
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
]


def expected_generator_bytes(seed: int) -> bytes:
    lines = ["row-" + str(seed * 100 + i) for i in range(5)]
    return ("\n".join(lines) + "\n").encode("utf-8")


def git_in_tree(root: Path, *args: str) -> None:
    """Run one git command in the tree, isolated from user git config."""
    env = dict(os.environ)
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        timeout=60,
        env=env,
    )


def run_checker(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--root", str(root)],
        capture_output=True, check=False,
        text=True,
        timeout=300,
    )


def write_manifest(root: Path, fixtures: list[dict]) -> None:
    manifest_dir = root / "tools" / "provenance"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    document = {
        "schema_note": "test manifest",
        "fixtures": fixtures,
    }
    (manifest_dir / "fixture-manifest.json").write_text(
        json.dumps(document, indent=2) + "\n", encoding="utf-8"
    )


def make_entry(path: str, generator: str, seed: int, payload: bytes) -> dict:
    return {
        "path": path,
        "generator": generator,
        "seed": seed,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "justification": "neutral fixture used only to exercise the guard",
    }


def test_real_tree_is_clean() -> None:
    """The actual repository passes the provenance check."""
    result = run_checker(REPO_ROOT)
    assert result.returncode == 0, (
        "provenance check failed on the real tree:\n"
        + result.stdout
        + result.stderr
    )
    assert "passed" in result.stdout


def test_non_allowlisted_csv_fails(tmp_path: Path) -> None:
    """Mutation 1: a .csv placed in the tree, absent from the allowlist."""
    write_manifest(tmp_path, [])
    (tmp_path / "stray.csv").write_text("a,b\n1,2\n", encoding="utf-8")

    result = run_checker(tmp_path)
    assert result.returncode == 1, (
        "expected exit code 1, got " + str(result.returncode) + ":\n"
        + result.stdout
        + result.stderr
    )
    assert "stray.csv" in result.stderr
    assert "not on the fixture allowlist" in result.stderr


def test_forged_fixture_content_fails(tmp_path: Path) -> None:
    """Mutation 2: committed bytes differ from generator-with-seed output.

    The manifest sha256 matches the committed (substituted) bytes, so this
    isolates the generator byte-compare: only the re-run catches it.
    """
    seed = 7
    (tmp_path / "gen_fixture.py").write_text(GENERATOR_SOURCE, encoding="utf-8")
    fixture_dir = tmp_path / "fixtures"
    fixture_dir.mkdir()
    forged = b"this content was substituted and never came from the script\n"
    (fixture_dir / "sample.txt").write_bytes(forged)
    write_manifest(
        tmp_path,
        [make_entry("fixtures/sample.txt", "gen_fixture.py", seed, forged)],
    )

    result = run_checker(tmp_path)
    assert result.returncode == 1, (
        "expected exit code 1, got " + str(result.returncode) + ":\n"
        + result.stdout
        + result.stderr
    )
    assert "fixtures/sample.txt" in result.stderr
    assert "NOT what its generator produces" in result.stderr


def test_correct_fixture_passes(tmp_path: Path) -> None:
    """A listed fixture whose bytes equal its generator output is accepted."""
    seed = 7
    payload = expected_generator_bytes(seed)
    (tmp_path / "gen_fixture.py").write_text(GENERATOR_SOURCE, encoding="utf-8")
    fixture_dir = tmp_path / "fixtures"
    fixture_dir.mkdir()
    (fixture_dir / "sample.txt").write_bytes(payload)
    write_manifest(
        tmp_path,
        [make_entry("fixtures/sample.txt", "gen_fixture.py", seed, payload)],
    )

    result = run_checker(tmp_path)
    assert result.returncode == 0, (
        "expected a clean pass:\n" + result.stdout + result.stderr
    )
    assert "passed" in result.stdout


def test_stale_manifest_sha256_fails(tmp_path: Path) -> None:
    """A manifest digest that no longer matches the committed bytes fails."""
    seed = 7
    payload = expected_generator_bytes(seed)
    (tmp_path / "gen_fixture.py").write_text(GENERATOR_SOURCE, encoding="utf-8")
    fixture_dir = tmp_path / "fixtures"
    fixture_dir.mkdir()
    (fixture_dir / "sample.txt").write_bytes(payload)
    entry = make_entry("fixtures/sample.txt", "gen_fixture.py", seed, payload)
    entry["sha256"] = "0" * 64
    write_manifest(tmp_path, [entry])

    result = run_checker(tmp_path)
    assert result.returncode == 1
    assert "does not match the sha256 recorded in the manifest" in result.stderr


def test_listed_fixture_missing_from_disk_fails(tmp_path: Path) -> None:
    """A manifest entry whose fixture file is absent fails the check."""
    seed = 7
    payload = expected_generator_bytes(seed)
    (tmp_path / "gen_fixture.py").write_text(GENERATOR_SOURCE, encoding="utf-8")
    write_manifest(
        tmp_path,
        [make_entry("fixtures/sample.txt", "gen_fixture.py", seed, payload)],
    )

    result = run_checker(tmp_path)
    assert result.returncode == 1
    assert "does not exist" in result.stderr


# ---------------------------------------------------------------------------
# F14: the data-format gate covers common real-derived artifact forms,
# and .json is allowed only for known configuration files or manifest
# fixtures.
# ---------------------------------------------------------------------------


def test_is_data_format_covers_json_and_extended_suffixes() -> None:
    """The suffix gate flags JSON and every newly covered artifact form."""
    assert _CHECKER_MODULE.is_data_format("profile.json")
    assert _CHECKER_MODULE.is_data_format("rows.jsonl")
    for suffix in EXTENDED_DATA_SUFFIXES:
        assert _CHECKER_MODULE.is_data_format("stray" + suffix), suffix
    # Case-insensitive on the final extension.
    assert _CHECKER_MODULE.is_data_format("model.RData")
    assert _CHECKER_MODULE.is_data_format("STORE.H5")
    # Ordinary source and docs are untouched.
    assert not _CHECKER_MODULE.is_data_format("script.py")
    assert not _CHECKER_MODULE.is_data_format("README.md")


def test_stray_jsonl_fails(tmp_path: Path) -> None:
    """Mutation: a .jsonl table placed in the tree with no allowlist entry."""
    write_manifest(tmp_path, [])
    (tmp_path / "rows.jsonl").write_text(
        '{"a": 1, "b": 2}\n{"a": 3, "b": 4}\n', encoding="utf-8"
    )

    result = run_checker(tmp_path)
    assert result.returncode == 1, (
        "expected exit code 1, got " + str(result.returncode) + ":\n"
        + result.stdout
        + result.stderr
    )
    assert "rows.jsonl" in result.stderr
    assert "not on the fixture allowlist" in result.stderr


def test_stray_unlisted_json_fails(tmp_path: Path) -> None:
    """Mutation: a .json profile that is not a known configuration file."""
    write_manifest(tmp_path, [])
    (tmp_path / "profile.json").write_text(
        '{"count": 12, "mean": 3.5}\n', encoding="utf-8"
    )

    result = run_checker(tmp_path)
    assert result.returncode == 1, (
        "expected exit code 1, got " + str(result.returncode) + ":\n"
        + result.stdout
        + result.stderr
    )
    assert "profile.json" in result.stderr
    assert "known" in result.stderr
    assert "configuration file" in result.stderr


def test_known_configuration_json_files_pass(tmp_path: Path) -> None:
    """The two known configuration .json paths are accepted without entries."""
    write_manifest(tmp_path, [])
    decon_dir = tmp_path / "tools" / "decontamination"
    decon_dir.mkdir(parents=True)
    (decon_dir / "attestation.json").write_text(
        '{"note": "neutral stand-in for the known configuration file"}\n',
        encoding="utf-8",
    )

    result = run_checker(tmp_path)
    assert result.returncode == 0, (
        "expected a clean pass:\n" + result.stdout + result.stderr
    )
    assert "passed" in result.stdout


def test_every_extended_data_suffix_fails(tmp_path: Path) -> None:
    """Mutation: one stray file per newly covered suffix, all reported."""
    write_manifest(tmp_path, [])
    for suffix in EXTENDED_DATA_SUFFIXES:
        (tmp_path / ("stray" + suffix)).write_text("payload\n", encoding="utf-8")

    result = run_checker(tmp_path)
    assert result.returncode == 1
    for suffix in EXTENDED_DATA_SUFFIXES:
        assert "stray" + suffix in result.stderr, suffix


# ---------------------------------------------------------------------------
# F18: manifest entries are confined to reviewed repository code and
# generators run behind the no-network guard runner.
# ---------------------------------------------------------------------------


def test_manifest_path_problem_battery() -> None:
    """Lexical rejection of absolute and '..' forms, both path styles."""
    rejected = [
        "/etc/fixture.txt",
        "//server/share/fixture.txt",
        "C:\\data\\gen_fixture.py",
        "C:/data/gen_fixture.py",
        "..",
        "../gen_fixture.py",
        "fixtures/../../gen_fixture.py",
        "fixtures\\..\\gen_fixture.py",
    ]
    for value in rejected:
        assert _CHECKER_MODULE.manifest_path_problem(value) is not None, value

    accepted = ["fixtures/sample.txt", "tools/gen_fixture.py", "gen_fixture.py"]
    for value in accepted:
        assert _CHECKER_MODULE.manifest_path_problem(value) is None, value


def test_absolute_generator_path_rejected(tmp_path: Path) -> None:
    """Mutation: an absolute generator path is refused before it can run."""
    seed = 7
    payload = b"placeholder\n"
    generator = tmp_path / "gen_sentinel.py"
    generator.write_text(SENTINEL_GENERATOR_SOURCE, encoding="utf-8")
    fixture_dir = tmp_path / "fixtures"
    fixture_dir.mkdir()
    (fixture_dir / "sample.txt").write_bytes(payload)
    write_manifest(
        tmp_path,
        [make_entry("fixtures/sample.txt", str(generator), seed, payload)],
    )

    result = run_checker(tmp_path)
    assert result.returncode == 1, (
        "expected exit code 1, got " + str(result.returncode) + ":\n"
        + result.stdout
        + result.stderr
    )
    assert "generator path that is an absolute path" in result.stderr
    assert not (tmp_path / "ran.sentinel").exists(), (
        "the checker executed a generator named by an absolute path"
    )


def test_dotdot_paths_rejected(tmp_path: Path) -> None:
    """Mutation: '..' in the fixture path or generator path is refused."""
    root = tmp_path / "repo"
    root.mkdir()
    outside = tmp_path / "outside_gen.py"
    outside.write_text(SENTINEL_GENERATOR_SOURCE, encoding="utf-8")
    seed = 7
    payload = b"placeholder\n"
    fixture_dir = root / "fixtures"
    fixture_dir.mkdir()
    (fixture_dir / "sample.txt").write_bytes(payload)
    (root / "gen_fixture.py").write_text(GENERATOR_SOURCE, encoding="utf-8")
    write_manifest(
        root,
        [
            make_entry("fixtures/sample.txt", "../outside_gen.py", seed, payload),
            make_entry("../escape.txt", "gen_fixture.py", seed, payload),
        ],
    )

    result = run_checker(root)
    assert result.returncode == 1, (
        "expected exit code 1, got " + str(result.returncode) + ":\n"
        + result.stdout
        + result.stderr
    )
    assert "contains a '..' component" in result.stderr
    assert "../outside_gen.py" in result.stderr
    assert "../escape.txt" in result.stderr
    assert not (tmp_path / "ran.sentinel").exists(), (
        "the checker executed a generator that lives outside the repository"
    )


def test_generator_socket_attempt_fails_with_guard_message(
    tmp_path: Path,
) -> None:
    """Mutation: a generator that opens a socket is stopped by the guard."""
    seed = 7
    payload = b"placeholder\n"
    (tmp_path / "gen_fixture.py").write_text(
        SOCKET_GENERATOR_SOURCE, encoding="utf-8"
    )
    fixture_dir = tmp_path / "fixtures"
    fixture_dir.mkdir()
    (fixture_dir / "sample.txt").write_bytes(payload)
    write_manifest(
        tmp_path,
        [make_entry("fixtures/sample.txt", "gen_fixture.py", seed, payload)],
    )

    result = run_checker(tmp_path)
    assert result.returncode == 1, (
        "expected exit code 1, got " + str(result.returncode) + ":\n"
        + result.stdout
        + result.stderr
    )
    assert "exited with an error" in result.stderr
    assert "no-network fixture guard" in result.stderr


def test_untracked_generator_in_git_tree_fails(tmp_path: Path) -> None:
    """Mutation: in a committed tree, an untracked generator is refused."""
    seed = 7
    payload = expected_generator_bytes(seed)
    (tmp_path / "gen_fixture.py").write_text(GENERATOR_SOURCE, encoding="utf-8")
    fixture_dir = tmp_path / "fixtures"
    fixture_dir.mkdir()
    (fixture_dir / "sample.txt").write_bytes(payload)
    write_manifest(
        tmp_path,
        [make_entry("fixtures/sample.txt", "gen_fixture.py", seed, payload)],
    )
    git_in_tree(tmp_path, "init")
    git_in_tree(
        tmp_path,
        "add",
        "tools/provenance/fixture-manifest.json",
        "fixtures/sample.txt",
    )
    git_in_tree(
        tmp_path,
        "-c",
        "user.name=synthtwin-test",
        "-c",
        "user.email=synthtwin-test@example.invalid",
        "commit",
        "-m",
        "fixture tree without the generator",
    )

    result = run_checker(tmp_path)
    assert result.returncode == 1, (
        "expected exit code 1, got " + str(result.returncode) + ":\n"
        + result.stdout
        + result.stderr
    )
    assert "is not tracked by git" in result.stderr
    assert "gen_fixture.py" in result.stderr


def test_fully_tracked_git_tree_passes(tmp_path: Path) -> None:
    """A committed tree whose entry paths are all tracked stays green."""
    seed = 7
    payload = expected_generator_bytes(seed)
    (tmp_path / "gen_fixture.py").write_text(GENERATOR_SOURCE, encoding="utf-8")
    fixture_dir = tmp_path / "fixtures"
    fixture_dir.mkdir()
    (fixture_dir / "sample.txt").write_bytes(payload)
    write_manifest(
        tmp_path,
        [make_entry("fixtures/sample.txt", "gen_fixture.py", seed, payload)],
    )
    git_in_tree(tmp_path, "init")
    git_in_tree(tmp_path, "add", ".")
    git_in_tree(
        tmp_path,
        "-c",
        "user.name=synthtwin-test",
        "-c",
        "user.email=synthtwin-test@example.invalid",
        "commit",
        "-m",
        "complete fixture tree",
    )

    result = run_checker(tmp_path)
    assert result.returncode == 0, (
        "expected a clean pass:\n" + result.stdout + result.stderr
    )
    assert "passed" in result.stdout
