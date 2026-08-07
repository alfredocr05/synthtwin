"""Tests for the data-provenance guard (plan D13).

The checker is exercised through its command-line interface so the tests
cover exactly what CI runs. Every synthetic tree lives in tmp_path; the
repository itself gains no data-format files from this suite.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "tools" / "provenance" / "check_provenance.py"

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


def expected_generator_bytes(seed: int) -> bytes:
    lines = ["row-" + str(seed * 100 + i) for i in range(5)]
    return ("\n".join(lines) + "\n").encode("utf-8")


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
