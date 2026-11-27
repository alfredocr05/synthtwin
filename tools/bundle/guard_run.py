"""Run synthtwin with every network call and child process made to fail loudly, in the same process.

Plan P4-D483 (lane WIN of the December plan). The Windows rehearsal runs
the trial once more through this file, with the ready folder's own
Python, after the firewall already blocks that Python: here the
standard library's socket calls raise before any connection is tried,
so an attempt synthtwin made would stop the run with this file's words
rather than wait on a refused connection. synthtwin opens no network
connection, so the run is the same run:

    python\\python.exe -I -B -X utf8 tools\\bundle\\guard_run.py synthtwin-arguments...
    python\\python.exe -I -B tools\\bundle\\guard_run.py --prove
    python\\python.exe -I -B tools\\bundle\\guard_run.py --denied
    python\\python.exe -I -B tools\\bundle\\guard_run.py --proxied

The socket class is replaced by a subclass that refuses to be made, so
a library that subclasses it when imported (the standard library's ssl
does) still imports; the connection calls and the name lookups both
ways (`getfqdn` goes through `gethostbyaddr`) raise. A child process is
refused the same way -- `subprocess.Popen`, again a subclass, and the
`os` calls that start or become another program -- because synthtwin
starts none (the offline audit of its source forbids it) and the guard
cannot follow a child out of its own process.

AN ATTEMPT IS NEVER SILENT. A caller may catch what the guard raises:
`NetworkAttempt` is an OSError, and so is urllib's URLError, which
optional-feature and update-check code catches as a matter of course.
So every attempt is also printed to standard error the moment it is
made and kept in ATTEMPTS, and the guarded run exits 3 whenever one was
made, whatever synthtwin's own exit status. The firewall level below it
has the same weakness and no such record: Windows' refusal there
(WinError 10013) is an OSError too, so a caller that swallowed it would
leave no trace. This level counts it, but only for Python's own calls
named here: a library's native code that connects by itself, refused by
the firewall and swallowed, is counted by neither level, and neither is
code that reaches the raw `_socket` module or POSIX's own spawn route
(`_posixsubprocess`; on Windows a child process goes through
`_winapi.CreateProcess`, refused here) -- none of the locked libraries'
Python files does either, and those routes are lane WIN-b's to word and
watch. The rehearsal runs the trial through this file as well.

--prove applies the guard and tries a socket, a name lookup each way, a
web address and two child processes: it exits 0 only when the guard
stopped every one and recorded every one. The two other proofs are of
the levels below this one, each run by the interpreter it concerns,
without the guard: --denied tries a plain connection to two hosts and
exits 0 only when the computer refused both WITH THE ACCESS-DENIED
REFUSAL a blocking firewall rule gives (WinError 10013, a
PermissionError): a failed name lookup, a timeout or a connection the
far end refused proves nothing about the rule, so it makes the proof
INCONCLUSIVE, exit 2 (the firewall rule on this interpreter bites; the
workflow shows first that another program still reaches the network);
and --proxied tries a web address through the proxy variables and exits
0 only when they point at a closed local port and the attempt was
refused there, so nothing left the computer.
"""

import os
import runpy
import socket
import subprocess
import sys
import traceback

_WORDS = (
    "guard_run: {} was attempted, and the rehearsal refuses every network call "
    "and every child process"
)

# Every attempt the guard refused in this process, in the order made.
ATTEMPTS: "list[str]" = []

# The socket module's calls that reach another computer or ask a name
# server, beside the socket class itself.
REFUSED_SOCKET_CALLS = (
    "create_connection",
    "getaddrinfo",
    "gethostbyname",
    "gethostbyname_ex",
    "gethostbyaddr",
    "getnameinfo",
)
# The os module's calls that start another program or turn this process
# into one (each where the system has it); os.popen and every subprocess
# helper go through subprocess.Popen, refused as well.
REFUSED_OS_CALLS = (
    "system",
    "popen",
    "startfile",
    "spawnv",
    "spawnve",
    "spawnvp",
    "spawnvpe",
    "execv",
    "execve",
    "posix_spawn",
    "posix_spawnp",
    "fork",
    "forkpty",
)


class NetworkAttempt(OSError):
    """Raised by the guard in place of any network call or child process."""


def _attempted(name: str) -> str:
    """Keep the attempt and print it at once, so a caller that swallows the error still leaves its trace."""
    global ATTEMPTS
    ATTEMPTS += [name]
    words = _WORDS.format(name)
    if sys.stderr is not None:
        print(words, file=sys.stderr, flush=True)
    return words


class _RefusedSocket(socket.socket):
    def __init__(self, *_arguments: object, **_named: object) -> None:
        raise NetworkAttempt(_attempted("socket.socket"))


class _RefusedPopen(subprocess.Popen):  # type: ignore[type-arg]
    def __init__(self, *_arguments: object, **_named: object) -> None:
        raise NetworkAttempt(_attempted("subprocess.Popen"))


def _refuse(name: str):  # type: ignore[no-untyped-def]
    def refused(*_arguments: object, **_named: object):  # type: ignore[no-untyped-def]
        raise NetworkAttempt(_attempted(name))

    return refused


def _process_starter():  # type: ignore[no-untyped-def]
    """Windows' own process call (_winapi.CreateProcess, multiprocessing's road), where this system has it."""
    try:
        import _winapi  # type: ignore[import-not-found]
    except ImportError:
        return None
    return _winapi


def patched() -> "list[tuple[object, str]]":
    """Every (module, name) apply() replaces on this system, so a test can put each back."""
    found: "list[tuple[object, str]]" = [(socket, "socket"), (subprocess, "Popen")]
    found += [(socket, name) for name in REFUSED_SOCKET_CALLS if hasattr(socket, name)]
    found += [(os, name) for name in REFUSED_OS_CALLS if hasattr(os, name)]
    starter = _process_starter()
    if starter is not None and hasattr(starter, "CreateProcess"):
        found += [(starter, "CreateProcess")]
    return found


def apply() -> None:
    """Make the socket class, the connection and lookup calls and every child process raise NetworkAttempt."""
    for module, name in patched():
        owner = getattr(module, "__name__", "")
        if (module, name) == (socket, "socket"):
            replacement: object = _RefusedSocket
        elif (module, name) == (subprocess, "Popen"):
            replacement = _RefusedPopen
        else:
            replacement = _refuse(f"{owner}.{name}")
        setattr(module, name, replacement)


def _stopped(attempt) -> bool:  # type: ignore[no-untyped-def]
    try:
        attempt()
    except NetworkAttempt as error:
        print(f"the guard stopped it: {error}")
        return True
    except OSError as error:
        reason = getattr(error, "reason", None)
        if isinstance(reason, NetworkAttempt):
            print(f"the guard stopped it: {reason}")
            return True
        print(f"the guard did NOT stop the attempt; it failed otherwise: {error!r}")
        return False
    print("the guard did NOT stop the attempt: it went through")
    return False


def prove() -> int:
    """Apply the guard, then try each kind of attempt: 0 when every one was stopped and recorded."""
    import urllib.request

    apply()
    before = len(ATTEMPTS)
    tries = (
        lambda: socket.socket(socket.AF_INET, socket.SOCK_STREAM),
        lambda: socket.getaddrinfo("pypi.org", 443),
        lambda: socket.gethostbyaddr("127.0.0.1"),
        lambda: urllib.request.urlopen("https://pypi.org/simple/", timeout=10),
        lambda: subprocess.run([sys.executable, "-c", "pass"], check=False),
        lambda: os.system("exit 0"),
    )
    stopped = all([_stopped(attempt) for attempt in tries])
    recorded = len(ATTEMPTS) - before
    print(f"the guard recorded {recorded} attempts for the {len(tries)} tries")
    return 0 if stopped and recorded >= len(tries) else 1


# The hosts the plain connections of --denied try: a package index the
# rehearsal must never reach, and the host the runner itself talks to.
DENIED_HOSTS = (("pypi.org", 443), ("github.com", 443))


# What Windows answers when a firewall rule refuses this program's
# connection: WSAEACCES, which Python raises as a PermissionError
# carrying winerror 10013 ("forbidden by its access permissions").
POLICY_REFUSAL = 10013


def refused_by_policy(error: OSError) -> bool:
    """Whether ``error`` is the access-denied refusal a blocking rule gives, not another failure."""
    return getattr(error, "winerror", None) == POLICY_REFUSAL or isinstance(error, PermissionError)


def denied(connect=socket.create_connection) -> int:  # type: ignore[no-untyped-def]
    """0 when every DENIED_HOSTS connection was refused by the rule; 1 when one was reached; 2 when unproven.

    Only the access-denied refusal counts as the rule's: a host whose
    name did not resolve, a timeout or a refusal by the far end leaves
    the rule unproven, so the proof is INCONCLUSIVE and fails.
    """
    reached = []
    unproven = []
    for host, port in DENIED_HOSTS:
        try:
            connection = connect((host, port), timeout=20)
        except OSError as error:
            if refused_by_policy(error):
                print(f"refused by the rule, as it should be: {host}:{port} ({error!r})")
            else:
                print(f"failed, but not with the rule's access-denied refusal: {host}:{port} ({error!r})")
                unproven += [f"{host}:{port}"]
            continue
        connection.close()
        reached += [f"{host}:{port}"]
    if reached:
        print(f"this interpreter REACHED {', '.join(reached)}: the network is NOT denied to it")
        return 1
    if unproven:
        print(
            f"INCONCLUSIVE: {', '.join(unproven)} failed without the access-denied refusal a "
            "blocking rule gives (a failed name lookup, a timeout or a refusal by the far end "
            "proves nothing about the rule), so the denial is not proven"
        )
        return 2
    return 0


def proxied() -> int:
    """0 when the proxy variables point at a closed local port and a web address was refused there."""
    import urllib.error
    import urllib.request

    proxies = urllib.request.getproxies()
    if not all(str(proxies.get(scheme, "")).startswith("http://127.0.0.1:") for scheme in ("http", "https")):
        print(f"the proxy variables do not point at this computer: {proxies}")
        return 1
    try:
        urllib.request.urlopen("https://pypi.org/simple/", timeout=20)
    except urllib.error.URLError as error:
        if isinstance(error.reason, ConnectionRefusedError):
            print(f"refused at the local proxy {proxies['https']}, as it should be: {error.reason!r}")
            return 0
        print(f"the attempt failed, but not at the local proxy: {error!r}")
        return 1
    except OSError as error:
        print(f"the attempt failed, but not at the local proxy: {error!r}")
        return 1
    print("a web address was reached through the proxy variables: they do NOT deny the network")
    return 1


def _status_of(code: object) -> int:
    """The exit status a SystemExit's code stands for, as the interpreter reads it."""
    if code is None:
        return 0
    if isinstance(code, int):
        return code
    print(code, file=sys.stderr)
    return 1


def main(argv: "list[str] | None" = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if arguments == ["--prove"]:
        return prove()
    if arguments == ["--denied"]:
        return denied()
    if arguments == ["--proxied"]:
        return proxied()
    apply()
    sys.argv = ["synthtwin", *arguments]
    status = 0
    try:
        runpy.run_module("synthtwin", run_name="__main__", alter_sys=True)
    except SystemExit as stop:
        status = _status_of(stop.code)
    except BaseException:
        if not ATTEMPTS:
            raise
        traceback.print_exc()
        status = 1
    if ATTEMPTS:
        print(
            f"guard_run: {len(ATTEMPTS)} attempt(s) refused in this run ({', '.join(ATTEMPTS)}); "
            f"the run fails with exit 3, whatever synthtwin's own exit status ({status})",
            file=sys.stderr,
            flush=True,
        )
        return 3
    return status


if __name__ == "__main__":
    sys.exit(main())
