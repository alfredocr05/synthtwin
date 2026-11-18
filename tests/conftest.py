"""Python-level socket guard (plan D6.3).

Installed at MODULE IMPORT TIME - not as a fixture - so it is active during
pytest collection and during every import of package modules by the suite.
It is a guard/tripwire supplementing the static import policy (D6.2), not
OS-level network disablement, and it is described that way everywhere.
The timing is regression-tested: ``tests/test_guard_timing_sentinel.py``
records at collection time what a connection attempt raises, and turns
red if this installation ever moves into a fixture.
"""

import socket

_MESSAGE = (
    "synthtwin test suite: a network operation was attempted. The suite "
    "runs network-dead by design; no test or package import may touch the "
    "network."
)


class _GuardError(RuntimeError):
    pass


def _blocked(*_args: object, **_kwargs: object) -> None:
    raise _GuardError(_MESSAGE)


# Keep originals so the guard's own self-test can verify what was replaced.
_ORIGINALS = {
    "socket": socket.socket,
    "create_connection": socket.create_connection,
}


class _GuardedSocket(_ORIGINALS["socket"]):  # type: ignore[misc]
    """Subclassable stand-in: stdlib modules (ssl) subclass socket.socket at
    import time, so the guard must remain a class; creating an instance is
    what gets blocked."""

    def __init__(self, *_args: object, **_kwargs: object) -> None:
        raise _GuardError(_MESSAGE)


socket.socket = _GuardedSocket  # type: ignore[misc,assignment]
socket.create_connection = _blocked  # type: ignore[assignment]


# THE TABLE FLOOR IS OFF FOR THE SUITE'S IN-PROCESS RUNS (plan P4-D425).
# `synthtwin profile` refuses a table under `parsing.TABLE_ROW_FLOOR`
# rows that hold a value, or, where a declared or answered person column
# repeats, under `parsing.TABLE_PEOPLE_FLOOR` people -- the owner's rule
# of 2026-10-22 -- and the suite runs the command on hundreds of small
# tables whose checks are about reading, roles and publication, not size.
# `cli.main` takes an INTERNAL keyword, `small_tables_refused`, which no
# command-line option sets; this fixture makes False its default for
# every test, on the function object itself, so a test that imported
# `main` by name gets the same default as one that calls `cli.main`. A
# test of the floor passes `small_tables_refused=True` (tests/test_table_floor.py),
# and a run in a fresh interpreter -- the installed command -- has the
# floor on, which that file checks too. The measurement drivers run
# outside pytest and pass the keyword themselves.
import os  # noqa: E402
import pathlib  # noqa: E402

import pytest  # noqa: E402
from collections.abc import Iterator  # noqa: E402

# THE INSTALLATION'S DATA FOLDER, ONE FOR EACH TEST (lane CHON, plan
# P4-D464; contract 4.6b.4). Every shipped `synthtwin profile` run opens the
# installation's data folder -- its private key, its record of earlier
# descriptions, its lock and its private reports -- which the platform
# places from XDG_DATA_HOME (POSIX) or LOCALAPPDATA (Windows). A test must
# never read or write the account's own folder, and no test's lock may meet
# another's, so each test gets a folder of its own holding the fixed test
# key (`bytes(range(32))`, the oracle's) and an empty record: a run's chain
# is then the same on every machine, and the screen says nothing about a
# key made or a record started. Written with the standard library alone:
# CI's static jobs run without the package installed. A test that names
# its own folder (`monkeypatch.setenv`) keeps it; a test that asks for
# `installation_folder` by name is handed its own data folder.
#
# AND ONE FOR EACH MODULE AND FOR THE SESSION (lane CHON's repair 1, from
# the whole suite of its build head): pytest makes a fixture of a wider
# scope BEFORE a test's own autouse fixtures, so a fixture of a module (a
# table described once for many cases) ran its shipped command with the
# account's own data folder in the environment -- on macOS the account's
# Library/Application Support/synthtwin -- and a later run of the same
# table met that folder's record. The same folder is made at the session's
# start and at each module's (autouse fixtures come first within their
# scope), so no fixture of any scope reaches the account's folder.
TEST_KEY = bytes(range(32))
_DATA_FOLDER = "synthtwin"
_KEY_FILE = "chain-key"
_LEDGER_FILE = "chain-ledger"
_EMPTY_LEDGER = '{\n  "tables": [],\n  "version": 1\n}\n'


def _fresh_installation(place: pathlib.Path) -> pathlib.Path:
    """A data folder under `place` holding the fixed test key and an empty record; its path."""
    data = place / _DATA_FOLDER
    data.mkdir(mode=0o700)
    key = data / _KEY_FILE
    key.touch(mode=0o600)
    if os.name != "nt":
        data.chmod(0o700)
        key.chmod(0o600)
    key.write_bytes(TEST_KEY)
    ledger = data / _LEDGER_FILE
    ledger.touch(mode=0o600)
    if os.name != "nt":
        ledger.chmod(0o600)
    ledger.write_text(_EMPTY_LEDGER, encoding="utf-8", newline="\n")
    return data


@pytest.fixture(autouse=True, scope="session")
def _installation_folder_of_the_session(tmp_path_factory: pytest.TempPathFactory) -> "Iterator[pathlib.Path]":
    place = tmp_path_factory.mktemp("installation-session")
    data = _fresh_installation(place)
    with pytest.MonkeyPatch.context() as own:
        own.setenv("XDG_DATA_HOME", str(place))
        own.setenv("LOCALAPPDATA", str(place))
        yield data


@pytest.fixture(autouse=True, scope="module")
def _installation_folder_of_the_module(tmp_path_factory: pytest.TempPathFactory) -> "Iterator[pathlib.Path]":
    place = tmp_path_factory.mktemp("installation-module")
    data = _fresh_installation(place)
    with pytest.MonkeyPatch.context() as own:
        own.setenv("XDG_DATA_HOME", str(place))
        own.setenv("LOCALAPPDATA", str(place))
        yield data


@pytest.fixture(autouse=True)
def installation_folder(tmp_path_factory: pytest.TempPathFactory) -> "Iterator[pathlib.Path]":
    place = tmp_path_factory.mktemp("installation")
    data = _fresh_installation(place)
    with pytest.MonkeyPatch.context() as own:
        own.setenv("XDG_DATA_HOME", str(place))
        own.setenv("LOCALAPPDATA", str(place))
        yield data


@pytest.fixture(autouse=True)
def _the_small_table_refusal_off_in_process_runs() -> "Iterator[None]":
    # Its OWN MonkeyPatch, never the test's `monkeypatch`: a test that
    # calls `monkeypatch.undo()` part way (46 calls in tests/) would
    # otherwise undo this default too and turn the refusal back on for
    # the rest of that test (skeptic 1 of lane POP, item 1 (b)).
    try:
        from synthtwin import cli
    except ModuleNotFoundError as missing:
        # CI's static jobs (the offline scan, provenance, decontamination)
        # run their test files without the package installed; they call
        # no command, so there is no default to set for them.
        if missing.name != "synthtwin":
            raise
        yield
        return

    defaults = cli.main.__kwdefaults__
    assert defaults is not None and "small_tables_refused" in defaults
    # ...and on `cli.run` too, the entry point `main` runs through (plan
    # P4-D437): a test calling it directly meets the suite's default.
    run_defaults = cli.run.__kwdefaults__
    assert run_defaults is not None and "small_tables_refused" in run_defaults
    with pytest.MonkeyPatch.context() as own:
        own.setitem(defaults, "small_tables_refused", False)
        own.setitem(run_defaults, "small_tables_refused", False)
        yield
