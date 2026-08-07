"""No-network runner for fixture generator scripts (plan D13).

check_provenance.py never runs a fixture generator directly. It runs
this wrapper, which first installs a Python audit hook through
``sys.addaudithook`` -- the interpreter provides no way to remove an
audit hook once installed -- and only then executes the generator
script with the documented argument convention:

    python guard_runner.py <generator-script> --seed <seed> --out <path>

The hook stops the run the moment the generator attempts any of:

- network access: every ``socket.*`` audit event, including the
  low-level constructor ``socket.__new__`` (raised even when a socket
  is built through the underlying C module rather than the high-level
  ``socket`` wrapper), ``socket.connect``, ``socket.bind``, and
  ``socket.getaddrinfo``;
- external programs and process creation: every ``subprocess.*`` event,
  ``os.system``, ``os.posix_spawn``, ``os.startfile``, and the
  ``os.exec``, ``os.spawn``, and ``os.fork`` families;
- native code loading: ``ctypes.dlopen``.

Because the hook observes interpreter-level audit events instead of
replacing importable Python names, re-importing, rebinding, or reaching
below the ``socket`` module cannot bypass it, and the generator has no
way to uninstall it. This is a Python-level tripwire supplementing
review of generator code, not operating-system network isolation.

This script uses only the Python standard library. Its use of ``runpy``
is permitted in tools/ (the D6 restriction applies to src/ only).
"""

from __future__ import annotations

import runpy
import sys

GUARD_MESSAGE = (
    "blocked by the no-network fixture guard: this fixture generator "
    "attempted a forbidden operation"
)

# Audit events that each name exactly one forbidden operation.
_BLOCKED_EVENTS = frozenset(
    {
        "os.system",
        "os.posix_spawn",
        "os.fork",
        "os.forkpty",
        "os.startfile",
        "ctypes.dlopen",
    }
)

# Audit-event prefixes covering whole forbidden families: every socket
# operation, every subprocess entry point, and the os.exec*/os.spawn*
# groups.
_BLOCKED_EVENT_PREFIXES = (
    "socket.",
    "subprocess.",
    "os.exec",
    "os.spawn",
)


def event_is_blocked(event: str) -> bool:
    """Return True when the named audit event is forbidden to generators."""
    if event in _BLOCKED_EVENTS:
        return True
    return event.startswith(_BLOCKED_EVENT_PREFIXES)


def _audit_hook(event: str, _args: tuple[object, ...]) -> None:
    if event_is_blocked(event):
        raise RuntimeError(
            GUARD_MESSAGE + " (audit event: " + event + "). Fixture "
            "generators must build their output from the seed alone: no "
            "network access, no external programs, no process creation, "
            "and no native code loading. Remove the call from the "
            "generator script."
        )


def install_guard() -> None:
    """Install the audit hook; ``sys.addaudithook`` is one-way by design."""
    sys.addaudithook(_audit_hook)


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
    install_guard()
    sys.argv = [script] + argv[2:]
    runpy.run_path(script, run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
