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
import pytest  # noqa: E402
from collections.abc import Iterator  # noqa: E402


@pytest.fixture(autouse=True)
def _the_small_table_refusal_off_in_process_runs() -> "Iterator[None]":
    # Its OWN MonkeyPatch, never the test's `monkeypatch`: a test that
    # calls `monkeypatch.undo()` part way (46 calls in tests/) would
    # otherwise undo this default too and turn the refusal back on for
    # the rest of that test (skeptic 1 of lane POP, item 1 (b)).
    from synthtwin import cli

    defaults = cli.main.__kwdefaults__
    assert defaults is not None and "small_tables_refused" in defaults
    with pytest.MonkeyPatch.context() as own:
        own.setitem(defaults, "small_tables_refused", False)
        yield
