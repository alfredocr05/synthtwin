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
