"""Tests for the path-locality validator (plan D6.1).

The lexical checks are string-only, so URL, UNC, and device-form
rejection is testable on every OS.  Windows reparse-point tests are
fully written here and marked skipif on other platforms; the Phase 0 CI
matrix runs them in every Windows cell.
"""

import builtins
import os
import pathlib
import sys

import pytest

from synthtwin.paths import (
    FILE_ATTRIBUTE_REPARSE_POINT,
    PathValidationError,
    _resolve_local,
    validate_local_path,
)

URL_INPUTS = [
    "http://example.com/table",
    "https://example.com/table",
    "s3://bucket/key",
    "file:///home/user/table",
    "ftp://host/folder",
    "HTTP://EXAMPLE.COM/table",
    "a1://host/x",
    # RFC 3986 also allows '+', '-', and '.' inside a scheme; every one
    # of these is remote-address syntax and must be caught lexically.
    "git+ssh://host/item",
    "a-b://host/item",
    "a.b://host/item",
]

UNC_INPUTS = [
    "\\\\server\\share\\folder",
    "\\\\server",
    "//server/share/folder",
    "//server",
]

DEVICE_INPUTS = [
    "\\\\.\\PhysicalDrive0",
    "\\\\?\\C:\\folder\\file",
    "//./PhysicalDrive0",
    "//?/C:/folder/file",
]

_WINDOWS_ONLY = pytest.mark.skipif(
    sys.platform != "win32", reason="Windows reparse-point behavior"
)
_POSIX_ONLY = pytest.mark.skipif(
    sys.platform == "win32", reason="POSIX-specific behavior"
)


# ---------------------------------------------------------------------------
# Lexical rejection (any OS)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("raw", URL_INPUTS)
def test_url_scheme_is_rejected(raw: str) -> None:
    with pytest.raises(PathValidationError) as excinfo:
        validate_local_path(raw, purpose="input")
    assert "network" in str(excinfo.value)


@pytest.mark.parametrize("raw", UNC_INPUTS)
def test_unc_form_is_rejected_in_both_slash_styles(raw: str) -> None:
    with pytest.raises(PathValidationError) as excinfo:
        validate_local_path(raw, purpose="input")
    assert "network" in str(excinfo.value)


@pytest.mark.parametrize("raw", DEVICE_INPUTS)
def test_device_form_is_rejected_in_both_slash_styles(raw: str) -> None:
    with pytest.raises(PathValidationError) as excinfo:
        validate_local_path(raw, purpose="input")
    assert "device" in str(excinfo.value)


def test_empty_path_is_rejected_with_plain_language() -> None:
    with pytest.raises(PathValidationError) as excinfo:
        validate_local_path("", purpose="input")
    assert "empty" in str(excinfo.value)


def test_error_message_names_the_purpose_and_gives_advice() -> None:
    with pytest.raises(PathValidationError) as excinfo:
        validate_local_path("s3://bucket/key", purpose="output")
    message = str(excinfo.value)
    assert "output" in message
    assert "computer" in message  # steers the user toward a local path


def test_reparse_bit_matches_the_fixed_win32_value() -> None:
    # The value is hardcoded in paths.py because the `stat` module is
    # not on the import allowlist; pin it here against typos.
    assert FILE_ATTRIBUTE_REPARSE_POINT == 0x400


# ---------------------------------------------------------------------------
# Plain paths pass and resolve
# ---------------------------------------------------------------------------


def test_plain_absolute_path_passes_and_resolves(
    tmp_path: pathlib.Path,
) -> None:
    target = tmp_path / "out_folder" / "result.txt"  # need not exist yet
    got = validate_local_path(str(target), purpose="output")
    assert got == target.resolve()
    assert got.is_absolute()


def test_plain_relative_path_passes_and_resolves(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    got = validate_local_path("nested/result.txt", purpose="output")
    assert got == (tmp_path / "nested" / "result.txt").resolve()
    assert got.is_absolute()


@_POSIX_ONLY
def test_mid_string_separator_marker_is_not_a_url(
    tmp_path: pathlib.Path,
) -> None:
    # Contains "://" but the text before it is not scheme-shaped, so the
    # lexical URL rule must not fire.
    raw = str(tmp_path) + "/logs/b://c"
    got = validate_local_path(raw, purpose="input")
    assert got.is_absolute()


# ---------------------------------------------------------------------------
# POSIX: symlinks are followed, then the result is re-checked
# ---------------------------------------------------------------------------


@_POSIX_ONLY
def test_posix_symlink_chain_resolves(tmp_path: pathlib.Path) -> None:
    real_dir = tmp_path / "real_dir"
    real_dir.mkdir()
    target_file = real_dir / "content.txt"
    target_file.write_text("hello\n", encoding="utf-8")
    link_one = tmp_path / "link_one"
    link_one.symlink_to(real_dir)
    link_two = tmp_path / "link_two"
    link_two.symlink_to(link_one)

    got = validate_local_path(str(link_two / "content.txt"), purpose="input")
    assert got == target_file.resolve()


@_POSIX_ONLY
def test_posix_resolved_string_is_revalidated(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Force resolution to land on a UNC-shaped string; the validator
    # must re-check the resolved string and reject it.
    lure = pathlib.Path("//intruder/share/table")
    monkeypatch.setattr(pathlib.Path, "resolve", lambda self, strict=False: lure)
    with pytest.raises(PathValidationError) as excinfo:
        validate_local_path(str(tmp_path / "plain_name"), purpose="input")
    assert "network" in str(excinfo.value)


# ---------------------------------------------------------------------------
# Spy: no filesystem touchpoint may run on lexically rejected input
# ---------------------------------------------------------------------------


def test_no_filesystem_touchpoint_runs_on_lexical_rejection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # D6.1 requires the lexical checks to run on the raw string BEFORE
    # any filesystem call, so this spy covers every operation the module
    # could reach - resolution, both stat flavors, the working-directory
    # lookup, and file opening - not just Path.resolve.
    touched: list[str] = []

    def watch(target: object, name: str, label: str) -> None:
        real = getattr(target, name)

        def spy(*args: object, **kwargs: object) -> object:
            touched.append(label)
            return real(*args, **kwargs)

        monkeypatch.setattr(target, name, spy)

    watch(pathlib.Path, "resolve", "Path.resolve")
    watch(os, "lstat", "os.lstat")
    watch(os, "stat", "os.stat")
    watch(os, "getcwd", "os.getcwd")
    watch(builtins, "open", "open")

    for raw in URL_INPUTS + UNC_INPUTS + DEVICE_INPUTS:
        with pytest.raises(PathValidationError):
            validate_local_path(raw, purpose="input")
    assert touched == [], (
        "a filesystem operation ran on lexically rejected input; D6.1 "
        "requires lexical checks before any filesystem call"
    )


# ---------------------------------------------------------------------------
# The Windows reparse walk, driven on every OS (never skipped)
# ---------------------------------------------------------------------------
#
# `_resolve_local` takes the platform string as a parameter, so the
# Windows component walk itself is exercised here with "win32" and a
# fake `os.lstat` on every OS in the matrix.  These tests have no skip
# path: they hold even on a runner that cannot create real links.  The
# integration tests with real links further below stay as well.


class _FakeLstatDetails:
    """Stand-in for an os.lstat result carrying Windows attribute bits."""

    def __init__(self, attributes: int) -> None:
        self.st_file_attributes = attributes


def _forbid_resolve(
    monkeypatch: pytest.MonkeyPatch,
) -> list[pathlib.PurePath]:
    """Make Path.resolve record and fail; return the call record."""
    calls: list[pathlib.PurePath] = []

    def spy(self: pathlib.Path, *args: object, **kwargs: object) -> pathlib.Path:
        calls.append(pathlib.PurePath(self))
        raise AssertionError("Path.resolve must not run in this scenario")

    monkeypatch.setattr(pathlib.Path, "resolve", spy)
    return calls


def test_mocked_reparse_component_is_rejected_on_any_os(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_lstat(path: object, *args: object, **kwargs: object) -> object:
        if str(path).endswith("dir_link"):
            return _FakeLstatDetails(FILE_ATTRIBUTE_REPARSE_POINT)
        return _FakeLstatDetails(0)

    monkeypatch.setattr(os, "lstat", fake_lstat)
    resolve_calls = _forbid_resolve(monkeypatch)

    with pytest.raises(PathValidationError) as excinfo:
        _resolve_local(
            "/data/dir_link/inner.txt", purpose="input", platform="win32"
        )
    assert "link" in str(excinfo.value)
    assert resolve_calls == [], (
        "Path.resolve ran although the walk saw a reparse component; "
        "D6.1 allows resolution only after the walk finds no links"
    )


def test_mocked_lstat_permission_failure_rejects_on_any_os(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A component that exists but cannot be examined (PermissionError,
    # sharing conflicts, ...) must reject the path, never continue the
    # walk as if the component were absent.
    def denied_lstat(path: object, *args: object, **kwargs: object) -> object:
        raise PermissionError(13, "simulated access denied", str(path))

    monkeypatch.setattr(os, "lstat", denied_lstat)
    resolve_calls = _forbid_resolve(monkeypatch)

    with pytest.raises(PathValidationError) as excinfo:
        _resolve_local(
            "/data/locked/inner.txt", purpose="input", platform="win32"
        )
    message = str(excinfo.value)
    assert "could not be safely examined" in message
    assert resolve_calls == [], (
        "Path.resolve ran although a component could not be examined; "
        "an unexamined component must never reach resolution"
    )


def test_mocked_missing_components_still_pass_the_walk(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Only a genuinely missing component (or one below a plain file) may
    # continue the walk: an output path about to be created stays valid.
    def absent_lstat(path: object, *args: object, **kwargs: object) -> object:
        raise FileNotFoundError(2, "simulated missing component", str(path))

    monkeypatch.setattr(os, "lstat", absent_lstat)
    got = _resolve_local(
        "/data/new_folder/result.txt", purpose="output", platform="win32"
    )
    assert got.is_absolute()


# ---------------------------------------------------------------------------
# Windows: reparse-point components are rejected without resolution
# ---------------------------------------------------------------------------


def _make_windows_dir_link(
    tmp_path: pathlib.Path,
) -> tuple[pathlib.Path, pathlib.Path]:
    """Create real_dir and a directory symlink to it; skip if forbidden."""
    real_dir = tmp_path / "real_dir"
    real_dir.mkdir(exist_ok=True)
    link = tmp_path / "dir_link"
    try:
        link.symlink_to(real_dir, target_is_directory=True)
    except OSError:
        pytest.skip(
            "this Windows account cannot create links (needs Developer "
            "Mode or admin rights)"
        )
    return real_dir, link


@_WINDOWS_ONLY
def test_windows_reparse_component_is_rejected(
    tmp_path: pathlib.Path,
) -> None:
    _real_dir, link = _make_windows_dir_link(tmp_path)
    with pytest.raises(PathValidationError) as excinfo:
        validate_local_path(str(link / "inner.txt"), purpose="input")
    assert "link" in str(excinfo.value)


@_WINDOWS_ONLY
def test_windows_reparse_leaf_is_rejected(tmp_path: pathlib.Path) -> None:
    _real_dir, link = _make_windows_dir_link(tmp_path)
    with pytest.raises(PathValidationError):
        validate_local_path(str(link), purpose="output")


@_WINDOWS_ONLY
def test_windows_resolve_is_never_invoked_with_reparse_component(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _real_dir, link = _make_windows_dir_link(tmp_path)
    calls: list[pathlib.PurePath] = []

    def spy(self: pathlib.Path, *args: object, **kwargs: object) -> pathlib.Path:
        calls.append(pathlib.PurePath(self))
        raise AssertionError(
            "Path.resolve must not run when a link component is present"
        )

    monkeypatch.setattr(pathlib.Path, "resolve", spy)
    with pytest.raises(PathValidationError):
        validate_local_path(str(link / "inner.txt"), purpose="input")
    assert calls == []


@_WINDOWS_ONLY
def test_windows_plain_path_without_links_passes(
    tmp_path: pathlib.Path,
) -> None:
    real_dir = tmp_path / "real_dir"
    real_dir.mkdir(exist_ok=True)
    got = validate_local_path(str(real_dir / "result.txt"), purpose="output")
    assert got == (real_dir / "result.txt").resolve()
