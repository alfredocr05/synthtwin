"""CLI stub behavior (plan D4)."""

import importlib.metadata

import pytest

from synthtwin.cli import main


def test_default_prints_status(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "synthtwin" in out
    assert "pre-alpha" in out
    assert "github.com/alfredocr05/synthtwin" in out


def test_version_flag_prints_exact_installed_version(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Plan D4: single version source. The suite runs against the
    # installed package, so the metadata version must exist; `--version`
    # must print exactly that value and nothing else. A stale constant
    # or a full status block here turns this test red.
    expected = importlib.metadata.version("synthtwin")
    assert main(["--version"]) == 0
    out = capsys.readouterr().out
    assert out == expected + "\n", (
        "--version must print exactly the installed package version "
        f"({expected!r}) followed by one newline, got {out!r}"
    )


def test_unknown_flag_raises_system_exit_code_2(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The main() docstring promises SystemExit only via argparse on bad
    # flags, with exit code 2 and the message on stderr.
    with pytest.raises(SystemExit) as excinfo:
        main(["--no-such-flag"])
    assert excinfo.value.code == 2
    captured = capsys.readouterr()
    assert captured.err, "argparse must explain the bad flag on stderr"
