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
# `cli.main` takes an INTERNAL keyword, `table_floor`, which no
# command-line option sets; this fixture makes False its default for
# every test, on the function object itself, so a test that imported
# `main` by name gets the same default as one that calls `cli.main`. A
# test of the floor passes `table_floor=True` (tests/test_table_floor.py),
# and a run in a fresh interpreter -- the installed command -- has the
# floor on, which that file checks too. The measurement drivers run
# outside pytest and pass the keyword themselves.
import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _the_table_floor_off_for_in_process_runs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from synthtwin import cli

    defaults = cli.main.__kwdefaults__
    assert defaults is not None and "table_floor" in defaults
    monkeypatch.setitem(defaults, "table_floor", False)
