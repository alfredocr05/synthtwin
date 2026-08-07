"""Collection-time sentinel for the socket guard's timing (plan D6.3).

The guard must be installed at ``tests/conftest.py`` MODULE IMPORT time,
so that it is already active while pytest collects (imports) the test
modules.  The code below runs at import - that is, during collection,
before any fixture exists - and records which exception type a socket
connection attempt raises at that moment.  The test then asserts the
recorded type is the guard's own error class.

If the guard were ever moved into a fixture, this module would import
before the guard exists: the attempt would raise an ordinary socket
error (or nothing), the recorded type would differ, and the test would
turn red.  The attempted address is loopback-only, so even in that
broken state no traffic would leave this machine.
"""

import socket

_RECORDED_TYPE: type[BaseException] | None = None
try:
    _leaked = socket.create_connection(("127.0.0.1", 9), timeout=0.25)
except (RuntimeError, OSError) as caught:
    # RuntimeError covers the guard's error class; OSError covers every
    # real socket failure (refusal, timeout) in the broken-guard state.
    _RECORDED_TYPE = type(caught)
else:  # pragma: no cover - only reachable when the guard is absent
    _leaked.close()


def test_guard_error_was_raised_during_collection() -> None:
    from conftest import _GuardError

    assert _RECORDED_TYPE is not None, (
        "a socket connection attempt at collection time raised nothing: "
        "the socket guard was not active while this module was imported"
    )
    assert _RECORDED_TYPE is _GuardError, (
        f"a socket connection attempt at collection time raised "
        f"{_RECORDED_TYPE.__name__} instead of the guard's error: the "
        f"guard must be installed at conftest import time, before "
        f"collection, not in a fixture"
    )
