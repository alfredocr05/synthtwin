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

import pytest

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

# A generator that reaches for the low-level C socket module, below
# the high-level socket wrapper. The guard now refuses the import
# itself, so the whole low-level socket family is unreachable by name
# (review item R2-B11).
LOW_LEVEL_SOCKET_GENERATOR_SOURCE = """\
import argparse
import _socket

parser = argparse.ArgumentParser()
parser.add_argument("--seed", type=int, required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()
raw = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
raw.close()
with open(args.out, "w", encoding="utf-8", newline="") as handle:
    handle.write("row-" + str(args.seed) + "\\n")
"""

# A generator that tries to start an external program before writing
# its output. The guard refuses the subprocess import itself.
SUBPROCESS_GENERATOR_SOURCE = """\
import argparse
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--seed", type=int, required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()
subprocess.run([sys.executable, "-c", "print('external')"], check=True)
with open(args.out, "w", encoding="utf-8", newline="") as handle:
    handle.write("row-" + str(args.seed) + "\\n")
"""

# A generator that starts a benign external program through a low-level
# os process primitive instead of the subprocess module -- the round-3
# review route that slipped below the earlier event-name list (review
# item R2-B11). The spawned command would write a sentinel file next to
# the generator; the guard must stop the spawn before any child runs.
SPAWN_PRIMITIVE_GENERATOR_SOURCE = """\
import argparse
import os
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--seed", type=int, required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()
sentinel = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "spawned.sentinel"
)
command = "open(" + repr(sentinel) + ", 'w').close()"
os.spawnl(os.P_WAIT, sys.executable, sys.executable, "-c", command)
with open(args.out, "w", encoding="utf-8", newline="") as handle:
    handle.write("row-" + str(args.seed) + "\\n")
"""

# A generator that goes for a native-call route: load the C library
# through ctypes and create a socket descriptor without touching any
# Python socket name. Native calls need not emit audit events, so the
# guard must refuse the ctypes import itself (review item R2-B11).
NATIVE_SOCKET_GENERATOR_SOURCE = """\
import argparse
import ctypes

parser = argparse.ArgumentParser()
parser.add_argument("--seed", type=int, required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()
libc = ctypes.CDLL(None)
descriptor = libc.socket(2, 1, 0)
with open(args.out, "w", encoding="utf-8", newline="") as handle:
    handle.write("row-" + str(args.seed) + "\\n")
"""

# A generator that reaches for the C helper the subprocess module is
# built on -- a process-creation route that emits no subprocess.* audit
# event of its own. The guard must refuse the import (review item
# R2-B11; POSIX-only module).
POSIX_FORK_EXEC_GENERATOR_SOURCE = """\
import argparse
import _posixsubprocess

parser = argparse.ArgumentParser()
parser.add_argument("--seed", type=int, required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()
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
# array stores, statistical packages and transport files, databases,
# spreadsheets, XML exports, and SQL dumps). YAML is tested separately
# because it carries a .github/ exemption.
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
    ".xml",
    ".sql",
    ".duckdb",
    ".ddb",
    ".db3",
    ".dbf",
    ".xpt",
    ".por",
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
    # YAML is data-format at the suffix level; only check_tree grants
    # the .github/ exemption.
    assert _CHECKER_MODULE.is_data_format("schema.yaml")
    assert _CHECKER_MODULE.is_data_format("schema.yml")
    # Case-insensitive on the final extension.
    assert _CHECKER_MODULE.is_data_format("model.RData")
    assert _CHECKER_MODULE.is_data_format("STORE.H5")
    assert _CHECKER_MODULE.is_data_format("DUMP.SQL")
    assert _CHECKER_MODULE.is_data_format("SCHEMA.YAML")
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
# R2-B7: YAML, XML, SQL-dump, DuckDB, DBF, and transport routes are
# closed. YAML is exempt only as a workflow file directly inside
# .github/workflows/ (single directory level) or via the manifest.
# ---------------------------------------------------------------------------


def test_is_workflow_configuration_single_level_only() -> None:
    """The exemption covers exactly .github/workflows/*.yml and *.yaml."""
    accepted = [
        ".github/workflows/ci.yml",
        ".github/workflows/release.yaml",
    ]
    for value in accepted:
        assert _CHECKER_MODULE.is_workflow_configuration(value), value

    rejected = [
        ".github/nonworkflow.yaml",
        ".github/workflows.yaml",
        ".github/workflows/nested/deep.yml",
        ".github/dependabot-lookalike.yml",
        "workflows/ci.yml",
        "other/.github/workflows/ci.yml",
        "schema.yaml",
        # Right place, wrong format: not a YAML file at all.
        ".github/workflows/notes.txt",
    ]
    for value in rejected:
        assert not _CHECKER_MODULE.is_workflow_configuration(value), value


def test_stray_yaml_outside_github_fails(tmp_path: Path) -> None:
    """Mutation: .yaml and .yml files at the tree root, both reported."""
    write_manifest(tmp_path, [])
    (tmp_path / "schema.yaml").write_text(
        "columns:\n  - a\n  - b\n", encoding="utf-8"
    )
    (tmp_path / "profile.yml").write_text(
        "count: 12\nmean: 3.5\n", encoding="utf-8"
    )

    result = run_checker(tmp_path)
    assert result.returncode == 1, (
        "expected exit code 1, got " + str(result.returncode) + ":\n"
        + result.stdout
        + result.stderr
    )
    assert "schema.yaml" in result.stderr
    assert "profile.yml" in result.stderr
    assert "not a GitHub Actions workflow file" in result.stderr


def test_yaml_elsewhere_under_github_fails(tmp_path: Path) -> None:
    """Mutation: tabular YAML below .github/ but not a workflow file.

    Round-3 review item R2-B7: the old exemption covered the whole
    .github/ directory, so a table saved as .github/nonworkflow.yaml
    passed with no manifest entry. Both a non-workflow file directly
    under .github/ and a file nested below workflows/ must be red.
    """
    write_manifest(tmp_path, [])
    github_dir = tmp_path / ".github"
    github_dir.mkdir()
    (github_dir / "nonworkflow.yaml").write_text(
        "rows:\n  - [3, 9, 27]\n  - [4, 16, 64]\n", encoding="utf-8"
    )
    nested = github_dir / "workflows" / "nested"
    nested.mkdir(parents=True)
    (nested / "deep.yml").write_text(
        "count: 12\nmean: 3.5\n", encoding="utf-8"
    )

    result = run_checker(tmp_path)
    assert result.returncode == 1, (
        "expected exit code 1, got " + str(result.returncode) + ":\n"
        + result.stdout
        + result.stderr
    )
    assert ".github/nonworkflow.yaml" in result.stderr
    assert ".github/workflows/nested/deep.yml" in result.stderr
    assert "not a GitHub Actions workflow file" in result.stderr


def test_yaml_under_github_passes(tmp_path: Path) -> None:
    """A workflow file directly inside .github/workflows/ is accepted."""
    write_manifest(tmp_path, [])
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_text(
        "name: neutral workflow stand-in\n", encoding="utf-8"
    )

    result = run_checker(tmp_path)
    assert result.returncode == 0, (
        "expected a clean pass:\n" + result.stdout + result.stderr
    )
    assert "passed" in result.stdout


def test_stray_sql_dump_fails(tmp_path: Path) -> None:
    """Mutation: an SQL dump placed in the tree with no allowlist entry."""
    write_manifest(tmp_path, [])
    (tmp_path / "dump.sql").write_text(
        "CREATE TABLE t (a INTEGER);\n", encoding="utf-8"
    )

    result = run_checker(tmp_path)
    assert result.returncode == 1, (
        "expected exit code 1, got " + str(result.returncode) + ":\n"
        + result.stdout
        + result.stderr
    )
    assert "dump.sql" in result.stderr
    assert "not on the fixture allowlist" in result.stderr


def test_stray_duckdb_fails(tmp_path: Path) -> None:
    """Mutation: a DuckDB store placed in the tree with no allowlist entry."""
    write_manifest(tmp_path, [])
    (tmp_path / "store.duckdb").write_bytes(b"neutral placeholder bytes")

    result = run_checker(tmp_path)
    assert result.returncode == 1, (
        "expected exit code 1, got " + str(result.returncode) + ":\n"
        + result.stdout
        + result.stderr
    )
    assert "store.duckdb" in result.stderr
    assert "not on the fixture allowlist" in result.stderr


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


# ---------------------------------------------------------------------------
# R2-B11: the guard runner refuses imports of capability modules and
# blocks the named dangerous audit events. It is a best-effort
# in-process guard -- reviewed generator code and CI remain the real
# controls -- but every route named by the reviews must go red here.
# ---------------------------------------------------------------------------

GUARD_RUNNER = REPO_ROOT / "tools" / "provenance" / "guard_runner.py"


def _load_guard_runner_module():
    """Import the guard runner for direct unit checks (no hook install)."""
    spec = importlib.util.spec_from_file_location(
        "guard_runner_under_test", GUARD_RUNNER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_guard_event_policy_covers_every_named_route() -> None:
    """The audit-event policy names socket, process, and native routes."""
    module = _load_guard_runner_module()
    blocked = [
        "socket.__new__",
        "socket.connect",
        "socket.bind",
        "socket.getaddrinfo",
        "socket.sendto",
        "subprocess.Popen",
        "os.system",
        "os.exec",
        "os.execve",
        "os.posix_spawn",
        "os.spawn",
        "os.fork",
        "os.forkpty",
        "os.startfile",
        "pty.spawn",
        "ctypes.dlopen",
        "ctypes.dlsym",
        "ctypes.call_function",
        "ctypes.addressof",
    ]
    for event in blocked:
        assert module.event_is_blocked(event), event
    # Ordinary interpreter activity a generator legitimately needs. The
    # "import" event is not unconditionally blocked: the hook decides it
    # per module through import_is_blocked.
    allowed = ["open", "import", "compile", "exec", "os.mkdir", "os.putenv"]
    for event in allowed:
        assert not module.event_is_blocked(event), event


def test_guard_import_policy_blocks_capability_modules() -> None:
    """Every capability module is refused at import, submodules included."""
    module = _load_guard_runner_module()
    blocked = [
        "socket",
        "_socket",
        "ssl",
        "ctypes",
        "_ctypes",
        "cffi",
        "subprocess",
        "_posixsubprocess",
        "multiprocessing",
        "pty",
        "fcntl",
        # Dotted forms are refused with their top-level package.
        "multiprocessing.pool",
        "ctypes.util",
        "socket.anything",
    ]
    for name in blocked:
        assert module.import_is_blocked(name), name
    # Modules an ordinary seeded generator legitimately needs.
    allowed = [
        "argparse",
        "os",
        "sys",
        "json",
        "random",
        "hashlib",
        "math",
        "pathlib",
        "collections.abc",
    ]
    for name in allowed:
        assert not module.import_is_blocked(name), name


def test_generator_low_level_socket_attempt_fails(tmp_path: Path) -> None:
    """Mutation: reaching below the high-level socket module is stopped.

    The generator imports the underlying C socket module directly --
    the route that bypassed the earlier name-replacement guard. The
    guard now refuses the import itself, before any constructor runs.
    """
    seed = 7
    payload = b"placeholder\n"
    (tmp_path / "gen_fixture.py").write_text(
        LOW_LEVEL_SOCKET_GENERATOR_SOURCE, encoding="utf-8"
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
    assert "no-network fixture guard" in result.stderr
    assert "forbidden import: _socket" in result.stderr


def test_generator_subprocess_attempt_fails(tmp_path: Path) -> None:
    """Mutation: a generator that starts an external program is stopped.

    The subprocess import is refused before subprocess.run can exist.
    """
    seed = 7
    payload = b"placeholder\n"
    (tmp_path / "gen_fixture.py").write_text(
        SUBPROCESS_GENERATOR_SOURCE, encoding="utf-8"
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
    assert "no-network fixture guard" in result.stderr
    assert "forbidden import: subprocess" in result.stderr


def test_generator_spawn_primitive_attempt_fails(tmp_path: Path) -> None:
    """Mutation: a low-level os spawn of a benign binary is stopped.

    Round-3 review item R2-B11: a process primitive below the
    subprocess module started an external program while the earlier
    guard stayed green. The spawn must now fail before any child runs,
    so the sentinel its child would write must not exist.
    """
    seed = 7
    payload = b"placeholder\n"
    (tmp_path / "gen_fixture.py").write_text(
        SPAWN_PRIMITIVE_GENERATOR_SOURCE, encoding="utf-8"
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
    assert "no-network fixture guard" in result.stderr
    assert not (tmp_path / "spawned.sentinel").exists(), (
        "the guard let a low-level os spawn start an external program"
    )


def test_generator_native_socket_attempt_fails(tmp_path: Path) -> None:
    """Mutation: a native-call socket route is stopped at the import.

    Round-3 review item R2-B11: native code called through ctypes need
    not emit any Python audit event, so the guard must refuse the
    ctypes import before the C library can be loaded at all.
    """
    seed = 7
    payload = b"placeholder\n"
    (tmp_path / "gen_fixture.py").write_text(
        NATIVE_SOCKET_GENERATOR_SOURCE, encoding="utf-8"
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
    assert "no-network fixture guard" in result.stderr
    assert "forbidden import: ctypes" in result.stderr


@pytest.mark.skipif(
    os.name != "posix",
    reason="the C fork-exec helper module exists only on POSIX hosts",
)
def test_generator_fork_exec_helper_import_fails(tmp_path: Path) -> None:
    """Mutation: the C helper below the subprocess module is refused.

    Round-3 review item R2-B11: this helper performs process creation
    without emitting a subprocess.* audit event of its own, so the
    guard must make it unreachable by refusing the import.
    """
    seed = 7
    payload = b"placeholder\n"
    (tmp_path / "gen_fixture.py").write_text(
        POSIX_FORK_EXEC_GENERATOR_SOURCE, encoding="utf-8"
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
    assert "no-network fixture guard" in result.stderr
    assert "forbidden import: _posixsubprocess" in result.stderr


def test_guard_runner_allows_innocent_generator(tmp_path: Path) -> None:
    """The audit-hook guard does not disturb an ordinary file-writing run."""
    generator = tmp_path / "gen_fixture.py"
    generator.write_text(GENERATOR_SOURCE, encoding="utf-8")
    out_path = tmp_path / "out.txt"

    proc = subprocess.run(
        [
            sys.executable,
            str(GUARD_RUNNER),
            str(generator),
            "--seed",
            "7",
            "--out",
            str(out_path),
        ],
        capture_output=True,
        check=False,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, (
        "the guard broke an innocent generator:\n" + proc.stdout + proc.stderr
    )
    assert out_path.read_bytes() == expected_generator_bytes(7)


# ---------------------------------------------------------------------------
# R2-M2: the hook installer never destroys an existing pre-push hook.
# Re-running over its own hook stays quiet; a different hook is refused.
# ---------------------------------------------------------------------------

INSTALLER = REPO_ROOT / "tools" / "hooks" / "install.sh"


def run_installer(repo: Path) -> subprocess.CompletedProcess:
    """Run the hook installer from inside the given git repository."""
    env = dict(os.environ)
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    return subprocess.run(
        ["sh", str(INSTALLER)],
        cwd=str(repo),
        capture_output=True,
        check=False,
        text=True,
        timeout=60,
        env=env,
    )


def test_installer_installs_and_rerun_stays_quiet(tmp_path: Path) -> None:
    """First run installs the hook; an identical re-run is silent."""
    git_in_tree(tmp_path, "init")

    first = run_installer(tmp_path)
    assert first.returncode == 0, first.stdout + first.stderr
    hook = tmp_path / ".git" / "hooks" / "pre-push"
    assert hook.is_file()
    assert os.access(hook, os.X_OK)
    installed = hook.read_bytes()
    assert b"check_provenance.py" in installed
    assert "Installed the advisory pre-push hook" in first.stdout

    second = run_installer(tmp_path)
    assert second.returncode == 0, second.stdout + second.stderr
    assert second.stdout == ""
    assert second.stderr == ""
    assert hook.read_bytes() == installed
    assert os.access(hook, os.X_OK)


def test_installer_refuses_to_overwrite_foreign_hook(tmp_path: Path) -> None:
    """Mutation: an existing different pre-push hook must survive intact."""
    git_in_tree(tmp_path, "init")
    hooks_dir = tmp_path / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook = hooks_dir / "pre-push"
    foreign = "#!/bin/sh\necho organizational security hook\n"
    hook.write_text(foreign, encoding="utf-8")
    hook.chmod(0o755)

    result = run_installer(tmp_path)
    assert result.returncode != 0, (
        "the installer overwrote an existing hook without refusing:\n"
        + result.stdout
        + result.stderr
    )
    assert hook.read_text(encoding="utf-8") == foreign
    assert "Refusing to overwrite" in result.stderr
    assert "Chain manually" in result.stderr
    assert not (hooks_dir / "pre-push.synthtwin.tmp").exists()


# ---------------------------------------------------------------------------
# R3-m1: the installer writes to the ACTIVE hook path git reports, not
# a hard-coded .git/hooks/pre-push, so core.hooksPath repositories and
# linked worktrees get a hook that actually runs.
# ---------------------------------------------------------------------------


def test_installer_honors_custom_hooks_path(tmp_path: Path) -> None:
    """Mutation: with core.hooksPath set, the active location gets the hook.

    Under the old hard-coded path, this repository would have gained an
    unused file at .git/hooks/pre-push while the active hook location
    stayed empty (review item R3-m1).
    """
    git_in_tree(tmp_path, "init")
    git_in_tree(tmp_path, "config", "core.hooksPath", "custom-hooks")

    first = run_installer(tmp_path)
    assert first.returncode == 0, first.stdout + first.stderr
    active_hook = tmp_path / "custom-hooks" / "pre-push"
    assert active_hook.is_file(), (
        "the installer did not write to the active hook path:\n"
        + first.stdout
        + first.stderr
    )
    assert os.access(active_hook, os.X_OK)
    assert b"check_provenance.py" in active_hook.read_bytes()
    assert "custom-hooks" in first.stdout
    # The inactive default location must gain nothing.
    assert not (tmp_path / ".git" / "hooks" / "pre-push").exists()

    # An identical re-run against the active path stays quiet.
    second = run_installer(tmp_path)
    assert second.returncode == 0, second.stdout + second.stderr
    assert second.stdout == ""
    assert second.stderr == ""
    assert os.access(active_hook, os.X_OK)


def test_installer_resolves_linked_worktree_hook_path(tmp_path: Path) -> None:
    """From a linked worktree, the hook lands at the shared active path.

    A linked worktree's .git is a file, not a directory, so the old
    hard-coded <root>/.git/hooks/pre-push shape could not even be
    created there (review item R3-m1).
    """
    main = tmp_path / "main"
    main.mkdir()
    git_in_tree(main, "init")
    (main / "README.txt").write_text("neutral placeholder\n", encoding="utf-8")
    git_in_tree(main, "add", "README.txt")
    git_in_tree(
        main,
        "-c",
        "user.name=synthtwin-test",
        "-c",
        "user.email=synthtwin-test@example.invalid",
        "commit",
        "-m",
        "first commit for the worktree",
    )
    worktree = tmp_path / "linked"
    git_in_tree(main, "worktree", "add", str(worktree))
    assert (worktree / ".git").is_file()

    result = run_installer(worktree)
    assert result.returncode == 0, result.stdout + result.stderr
    shared_hook = main / ".git" / "hooks" / "pre-push"
    assert shared_hook.is_file(), (
        "the installer did not write to the shared active hook path:\n"
        + result.stdout
        + result.stderr
    )
    assert os.access(shared_hook, os.X_OK)
    assert b"check_provenance.py" in shared_hook.read_bytes()
