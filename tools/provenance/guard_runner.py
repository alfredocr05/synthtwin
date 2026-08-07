"""No-network runner for fixture generator scripts (plan D13).

check_provenance.py never runs a fixture generator directly. It runs
this wrapper, which first replaces the standard library's
``socket.socket`` and ``socket.create_connection`` with functions that
raise, and only then executes the generator script with the documented
argument convention:

    python guard_runner.py <generator-script> --seed <seed> --out <path>

Any attempt by the generator to open a network connection through the
standard socket API stops the run with the guard message below, the
wrapper exits with an error, and the provenance check fails. This is a
Python-level tripwire supplementing review of generator code, not
operating-system network isolation.

This script uses only the Python standard library. Its use of ``runpy``
is permitted in tools/ (the D6 restriction applies to src/ only).
"""

from __future__ import annotations

import runpy
import socket
import sys

GUARD_MESSAGE = (
    "blocked by the no-network fixture guard: this fixture generator "
    "tried to open a network connection. Fixture generators must build "
    "their output from the seed alone; remove the network call from the "
    "generator script."
)


def _blocked(*_args: object, **_kwargs: object) -> None:
    raise RuntimeError(GUARD_MESSAGE)


def install_no_network_guard() -> None:
    """Replace the socket entry points with functions that raise."""
    socket.socket = _blocked  # type: ignore[misc,assignment]
    socket.create_connection = _blocked  # type: ignore[assignment]


def main(argv: list[str]) -> int:
    """Install the guard, then run the named generator script.

    ``argv`` is the full process argument list: ``argv[1]`` is the
    generator script path and everything after it is passed through as
    the generator's own arguments (``--seed <seed> --out <path>``).
    Returns 2 on a usage error; otherwise the generator's own outcome
    (including any exception it raises) decides the exit status.
    """
    if len(argv) < 2:
        print(
            "usage: guard_runner.py <generator-script> --seed <seed> "
            "--out <output-path>",
            file=sys.stderr,
        )
        return 2
    script = argv[1]
    install_no_network_guard()
    sys.argv = [script] + argv[2:]
    runpy.run_path(script, run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
