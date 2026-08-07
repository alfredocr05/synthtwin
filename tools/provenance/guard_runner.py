"""Best-effort in-process guard for fixture generator runs (plan D13).

check_provenance.py never runs a fixture generator directly. It runs
this wrapper, which first installs a Python audit hook through
``sys.addaudithook`` -- the interpreter provides no way to remove an
audit hook once installed -- and only then executes the generator
script with the documented argument convention:

    python guard_runner.py <generator-script> --seed <seed> --out <path>

The hook applies two layers:

1. Import blocking. At the ``import`` audit event, the hook refuses
   every module whose top-level name carries network, process,
   native-call, or terminal-control capability (BLOCKED_IMPORT_MODULES:
   socket, _socket, ssl, ctypes, _ctypes, cffi, subprocess,
   _posixsubprocess, multiprocessing, pty, fcntl). Blocking the import
   makes the whole capability family unreachable by name, including
   low-level helpers that perform their work without emitting further
   audit events.
2. Event blocking. Independently of imports, the hook stops the named
   dangerous audit events: every ``socket.*`` and ``subprocess.*``
   event, the ``os.exec*``/``os.spawn*``/``os.posix_spawn*``/
   ``os.fork*`` families, ``os.system``, ``os.startfile``,
   ``pty.spawn``, and every ``ctypes.*`` event.

Scope, stated plainly: this is a best-effort in-process guard aligned
with the project's documented offline posture -- a guard, not a
sandbox. A Python audit hook only sees what emits audit events, and
native code need not emit any. The controls that actually hold are
that every fixture generator is repository-reviewed code and that CI
are the authoritative automated verification (a standing rule, not a
mechanically enforced merge barrier while the repository is private);
this runner exists to catch mistakes early
and loudly, not to confine a hostile program.

This script uses only the Python standard library. Its use of ``runpy``
is permitted in tools/ (the D6 restriction applies to src/ only).
"""

from __future__ import annotations

import runpy
import sys

GUARD_MESSAGE = (
    "blocked by the best-effort fixture guard: this fixture generator "
    "attempted a forbidden operation"
)

# Modules whose import is refused outright: each one hands the
# generator network, process, native-call, or terminal-control
# capability. Comparison is by top-level name, so a dotted submodule
# import is refused with its package.
BLOCKED_IMPORT_MODULES = frozenset(
    {
        "socket",
        "_socket",
        "ssl",
        "ctypes",
        "_ctypes",
        "cffi",
        "subprocess",
        "_posixsubprocess",
        "multiprocessing",
        "pty",
        "fcntl",
    }
)

# Audit events that each name exactly one forbidden operation.
_BLOCKED_EVENTS = frozenset(
    {
        "os.system",
        "os.startfile",
        "pty.spawn",
    }
)

# Audit-event prefixes covering whole forbidden families: every socket
# operation, every subprocess entry point, the os.exec*/os.spawn*/
# os.posix_spawn*/os.fork* process-creation groups, and every ctypes
# native-call event.
_BLOCKED_EVENT_PREFIXES = (
    "socket.",
    "subprocess.",
    "os.exec",
    "os.spawn",
    "os.posix_spawn",
    "os.fork",
    "ctypes.",
)


def import_is_blocked(module_name: str) -> bool:
    """Return True when generators may not import the named module.

    The check uses the top-level package name, so refusing
    ``multiprocessing`` also refuses ``multiprocessing.pool``.
    """
    return module_name.partition(".")[0] in BLOCKED_IMPORT_MODULES


def event_is_blocked(event: str) -> bool:
    """Return True when the named audit event is forbidden to generators.

    The ``import`` event is not decided here: the hook resolves it
    per module through ``import_is_blocked``.
    """
    if event in _BLOCKED_EVENTS:
        return True
    return event.startswith(_BLOCKED_EVENT_PREFIXES)


def _audit_hook(event: str, args: tuple[object, ...]) -> None:
    if event == "import" and args and import_is_blocked(str(args[0])):
        raise RuntimeError(
            GUARD_MESSAGE + " (forbidden import: " + str(args[0]) + "). "
            "Fixture generators must build their output from the seed "
            "alone; a module that provides network access, process "
            "creation, or native-code calls may not even be imported. "
            "Remove the import from the generator script."
        )
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
