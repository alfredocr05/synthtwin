"""The guard's own proof that it can fail (plan D6.5 / acceptance 6)."""

import socket

import pytest


def test_socket_creation_is_blocked() -> None:
    with pytest.raises(RuntimeError, match="network operation was attempted"):
        socket.socket()


def test_create_connection_is_blocked() -> None:
    with pytest.raises(RuntimeError, match="network operation was attempted"):
        socket.create_connection(("localhost", 80))


def test_guard_replaced_the_real_functions() -> None:
    from conftest import _ORIGINALS, _blocked, _GuardedSocket

    assert socket.socket is _GuardedSocket
    assert socket.create_connection is _blocked
    assert _ORIGINALS["socket"] is not _GuardedSocket
    # Subclassing must remain possible (stdlib ssl requires it) while
    # instantiation stays blocked.
    class _Sub(socket.socket):  # type: ignore[misc]
        pass
    with pytest.raises(RuntimeError, match="network operation"):
        _Sub()
