"""CLI stub behavior (plan D4)."""

import pytest

from synthtwin.cli import main


def test_default_prints_status(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "synthtwin" in out
    assert "pre-alpha" in out
    assert "github.com/alfredocr05/synthtwin" in out


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--version"]) == 0
    out = capsys.readouterr().out.strip()
    assert out, "version output must not be empty"
