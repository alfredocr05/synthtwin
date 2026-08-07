"""Tests for the structural requirement-file validator (plan D5).

The validator is exercised through its command-line interface so these
tests cover exactly what CI runs before every pip command that consumes
the lock. Every synthetic requirements file lives in tmp_path. The red
cases cover each refused reference class one by one; the green cases
cover the repository's real requirement files, whose acceptance is the
production behavior.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "tools" / "supply_chain" / "validate_lock.py"

DIRECTIVE = "--only-binary :all:"
GOOD_HASH = "0" * 64
HASH_OPT = f"--hash=sha256:{GOOD_HASH}"


def _load_module():
    """Import the validator as a module for direct unit checks."""
    spec = importlib.util.spec_from_file_location("validate_lock", VALIDATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODULE = _load_module()


def run_validator(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def write_reqs(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "requirements.txt"
    path.write_text(body, encoding="utf-8")
    return path


# ---------------------------------------------------------------- green


def test_real_lock_is_accepted() -> None:
    result = run_validator("--lock", str(REPO_ROOT / "requirements-dev.lock"))
    assert result.returncode == 0, result.stdout + result.stderr


def test_real_requirements_input_is_accepted() -> None:
    result = run_validator("--input", str(REPO_ROOT / "requirements-dev.in"))
    assert result.returncode == 0, result.stdout + result.stderr


def test_default_run_checks_both_repository_files() -> None:
    result = run_validator()
    assert result.returncode == 0, result.stdout + result.stderr
    assert "requirements-dev.in" in result.stdout
    assert "requirements-dev.lock" in result.stdout


def test_synthetic_lock_with_markers_and_hashes_is_accepted(
    tmp_path: Path,
) -> None:
    body = (
        "# hand-written for this test\n"
        f"{DIRECTIVE}\n"
        "\n"
        "example==1.2.3 ; sys_platform == 'linux' \\\n"
        f"    {HASH_OPT} \\\n"
        f"    --hash=sha256:{'1' * 64}\n"
        "    # via -r requirements-dev.in\n"
        "other==2.0 \\\n"
        f"    --hash=sha256:{'2' * 64}\n"
    )
    result = run_validator("--lock", str(write_reqs(tmp_path, body)))
    assert result.returncode == 0, result.stdout + result.stderr


# ------------------------------------------------------- red, lock rules

REFUSED_LOCK_LINES = [
    pytest.param(
        f"file:///somewhere/example-1.0.tar.gz {HASH_OPT}",
        "file:",
        id="direct-file-reference",
    ),
    pytest.param(
        f"./vendor/example {HASH_OPT}",
        "path separator",
        id="relative-path",
    ),
    pytest.param(
        f"..\\vendor\\example {HASH_OPT}",
        "path separator",
        id="windows-path",
    ),
    pytest.param(
        f"example-1.0.tar.gz {HASH_OPT}",
        "archive",
        id="source-archive",
    ),
    pytest.param(
        f"example-1.0.zip {HASH_OPT}",
        "archive",
        id="zip-archive",
    ),
    pytest.param(
        f"example-1.0-py3-none-any.whl {HASH_OPT}",
        "archive",
        id="wheel-file",
    ),
    pytest.param(
        f"git+https://example.invalid/repo.git {HASH_OPT}",
        "version-control",
        id="vcs-git",
    ),
    pytest.param(
        f"hg+https://example.invalid/repo {HASH_OPT}",
        "version-control",
        id="vcs-hg",
    ),
    pytest.param(
        f"svn+https://example.invalid/repo {HASH_OPT}",
        "version-control",
        id="vcs-svn",
    ),
    pytest.param("-e ./example", "editable", id="editable-dash-e"),
    pytest.param("--editable=./example", "editable", id="editable-long"),
    pytest.param(
        f"https://example.invalid/example {HASH_OPT}",
        "URL",
        id="url",
    ),
    pytest.param(
        f"example @ somewhere {HASH_OPT}",
        "'@'",
        id="at-direct-reference",
    ),
    pytest.param("example==1.0", "hash", id="missing-hash"),
    pytest.param(f"example>=1.0 {HASH_OPT}", "pin", id="range-not-pin"),
    pytest.param(f"example {HASH_OPT}", "pin", id="bare-name"),
    pytest.param(
        "example==1.0 --hash=md5:abcdef",
        "sha256",
        id="malformed-hash",
    ),
    pytest.param("--find-links wheels", "directive", id="unknown-directive"),
    pytest.param("ex\u00e4mple==1.0 " + HASH_OPT, "ASCII", id="non-ascii"),
]


@pytest.mark.parametrize(("line", "expected"), REFUSED_LOCK_LINES)
def test_lock_rules_refuse_forbidden_line(
    tmp_path: Path, line: str, expected: str
) -> None:
    result = run_validator(
        "--lock", str(write_reqs(tmp_path, f"{DIRECTIVE}\n{line}\n"))
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert expected in result.stdout


# ------------------------------------------------------ red, input rules

REFUSED_INPUT_LINES = [
    pytest.param("example", "version range", id="bare-name"),
    pytest.param("./example", "path separator", id="bare-local-path"),
    pytest.param("-e .", "editable", id="editable"),
    pytest.param(
        "git+ssh://example.invalid/repo",
        "version-control",
        id="vcs",
    ),
]


@pytest.mark.parametrize(("line", "expected"), REFUSED_INPUT_LINES)
def test_input_rules_refuse_forbidden_line(
    tmp_path: Path, line: str, expected: str
) -> None:
    result = run_validator(
        "--input", str(write_reqs(tmp_path, f"{DIRECTIVE}\n{line}\n"))
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert expected in result.stdout


# ----------------------------------------------- directive and file shape


def test_missing_only_binary_directive_is_refused(tmp_path: Path) -> None:
    result = run_validator(
        "--lock", str(write_reqs(tmp_path, f"example==1.0 {HASH_OPT}\n"))
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "exactly one" in result.stdout


def test_duplicated_only_binary_directive_is_refused(tmp_path: Path) -> None:
    body = f"{DIRECTIVE}\n{DIRECTIVE}\nexample==1.0 {HASH_OPT}\n"
    result = run_validator("--lock", str(write_reqs(tmp_path, body)))
    assert result.returncode == 1, result.stdout + result.stderr
    assert "exactly one" in result.stdout


def test_missing_file_exits_two_with_plain_message(tmp_path: Path) -> None:
    result = run_validator("--lock", str(tmp_path / "absent.lock"))
    assert result.returncode == 2, result.stdout + result.stderr
    assert "Cannot read" in result.stdout


def test_refusal_is_textual_and_opens_no_referenced_path(
    tmp_path: Path,
) -> None:
    # The named archive does not exist anywhere. A validator that tried
    # to resolve or open referenced paths would fail differently; the
    # refusal must come from the text alone, before anything runs.
    missing = tmp_path / "never-created" / "example-1.0.tar.gz"
    body = f"{DIRECTIVE}\n{missing} {HASH_OPT}\n"
    result = run_validator("--lock", str(write_reqs(tmp_path, body)))
    assert result.returncode == 1, result.stdout + result.stderr
    assert "path separator" in result.stdout


# ------------------------------------------------------- direct unit view


def test_check_text_joins_continuation_lines() -> None:
    text = f"{DIRECTIVE}\nexample==1.0 \\\n    {HASH_OPT}\n"
    assert MODULE.check_text(text, "lock", "lock") == []


def test_check_text_reports_the_physical_line_number() -> None:
    text = f"{DIRECTIVE}\n\ngit+https://example.invalid/repo\n"
    problems = MODULE.check_text(text, "lock", "lockfile")
    assert any(entry.startswith("lockfile:3:") for entry in problems)


def test_check_text_refuses_an_unknown_mode() -> None:
    with pytest.raises(ValueError):
        MODULE.check_text("", "loose", "label")
