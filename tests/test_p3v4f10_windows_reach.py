"""Every test in this suite has to be able to RUN on the whole matrix.

REVIEW ITEM P3-V4-F10, ROUND 5 ITEM 10, AND WHY THIS FILE EXISTS RATHER
THAN A ONE-LINE FIX. A repair test added in round 4 called
`os.geteuid()` to decide whether to skip. That function does not exist
on Windows, so every Windows cell of the governed matrix (the `tests`
job of `.github/workflows/ci.yml`, `windows-latest` at five Python
versions) ended in an AttributeError -- and the charter requires CI
green before a merge, so one line in one test blocked the branch
outright.

The defect is not that one line. It is that nothing in the suite was
asking the question, so nobody could have known until a Windows cell
ran. This file asks it, of every test module, from the source:

1. No test may name an `os` member some platform of the matrix does
   not have unless the very expression it sits in has already asked
   what platform this is, or the test carrying it is marked to be
   skipped off its platform.
2. No test may import at module level a standard-library module that
   only one platform has; a per-platform module is imported inside the
   helper that uses it, where an ImportError can be answered.

WHAT THIS DOES AND DOES NOT SETTLE. It settles that the suite can
START on every platform CI governs. It says nothing about a test that
runs everywhere and asserts something only one platform can satisfy --
that is a different class, and the per-platform assertions in
`test_cli_profile.py`, `test_cli_generate.py` and
`test_r6f5_write_transaction.py` are how this suite handles it. Nor is
the name list below a proof of completeness: it is what one platform or
the other is known to lack, written down, and a member nobody has
written down is a member this cannot catch. Both limits are stated because the round
that produced this file was a round about proofs claiming more than
they hold.
"""

import ast
import pathlib

# `os` members that some platform of the matrix does not have. The long
# group is POSIX-only -- account, process, terminal and filesystem calls
# Windows has no equivalent of at all -- and the short group at the end
# is Windows-only, so that this rule reads in both directions: a call
# that is missing on Linux and macOS costs eleven cells of the matrix
# rather than ten. Either way a test that needs one has to say which
# platform it is talking about.
NOT_ON_EVERY_PLATFORM = frozenset(
    {
        "chown",
        "chroot",
        "confstr",
        "fchmod",
        "fchown",
        "fork",
        "forkpty",
        "fpathconf",
        "getegid",
        "geteuid",
        "getgid",
        "getgroups",
        "getloadavg",
        "getpgid",
        "getpgrp",
        "getpriority",
        "getresgid",
        "getresuid",
        "getsid",
        "getuid",
        "initgroups",
        "killpg",
        "lchmod",
        "lchown",
        "mkfifo",
        "mknod",
        "nice",
        "openpty",
        "pathconf",
        "plock",
        "posix_spawn",
        "posix_spawnp",
        "setegid",
        "seteuid",
        "setgid",
        "setgroups",
        "setpgid",
        "setpgrp",
        "setpriority",
        "setregid",
        "setresgid",
        "setresuid",
        "setreuid",
        "setsid",
        "setuid",
        "statvfs",
        "sync",
        "tcgetpgrp",
        "tcsetpgrp",
        "ttyname",
        "uname",
        "wait3",
        "wait4",
        # ...and the other direction.
        "add_dll_directory",
        "get_handle_inheritable",
        "set_handle_inheritable",
        "startfile",
    }
)

# Standard-library modules that exist on one platform only.
ONE_PLATFORM_MODULES = frozenset(
    {
        "_posixsubprocess",
        "_winapi",
        "fcntl",
        "grp",
        "msvcrt",
        "posix",
        "pty",
        "pwd",
        "resource",
        "syslog",
        "termios",
        "tty",
        "winreg",
    }
)

# What counts as having asked. Either name settles the question, and
# both are how this suite already spells it.
_ASKING = ("os.name", "sys.platform", "platform.system")


def _test_modules() -> "list[pathlib.Path]":
    """Every module of this suite, this file included."""
    return sorted(pathlib.Path(__file__).parent.glob("*.py"))


def _asks_the_platform(node: ast.AST) -> bool:
    """Whether ``node`` contains a question about which platform this is."""
    for inner in ast.walk(node):
        if isinstance(inner, ast.Attribute):
            spelled = ast.unparse(inner)
            if spelled in _ASKING or spelled.startswith(_ASKING):
                return True
        if isinstance(inner, ast.Call):
            spelled = ast.unparse(inner.func)
            if spelled in _ASKING:
                return True
    return False


def calls_no_platform_asked(source: str) -> "list[tuple[int, str]]":
    """Every ``os.<member>`` some platform lacks that nothing guarded.

    A reference is guarded when the platform question is asked in the
    same boolean expression (``os.name != "nt" and os.geteuid() == 0``),
    in the ``if`` test it sits under, or in a skip mark on the function
    holding it. Anything else is a call that will simply not be there
    when a cell that does not have it reaches it.
    """
    tree = ast.parse(source)
    guarded: set[int] = set()
    for node in ast.walk(tree):
        asked = False
        if isinstance(node, ast.BoolOp):
            asked = _asks_the_platform(node)
            covered: list[ast.AST] = list(node.values)
        elif isinstance(node, (ast.If, ast.IfExp, ast.While)):
            asked = _asks_the_platform(node.test)
            covered = [node]
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            asked = any(
                _asks_the_platform(mark) for mark in node.decorator_list
            )
            covered = [node]
        else:
            continue
        if not asked:
            continue
        for branch in covered:
            for inner in ast.walk(branch):
                guarded.add(id(inner))
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute):
            continue
        base = node.value
        if not isinstance(base, ast.Name) or base.id != "os":
            continue
        if node.attr not in NOT_ON_EVERY_PLATFORM:
            continue
        if id(node) in guarded:
            continue
        found.append((node.lineno, f"os.{node.attr}"))
    return found


def one_platform_imports(source: str) -> "list[tuple[int, str]]":
    """Every module-level import of a module only one platform has."""
    tree = ast.parse(source)
    found: list[tuple[int, str]] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.partition(".")[0]
                if root in ONE_PLATFORM_MODULES:
                    found.append((node.lineno, root))
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").partition(".")[0]
            if root in ONE_PLATFORM_MODULES:
                found.append((node.lineno, root))
    return found


def test_no_test_needs_an_os_call_a_governed_platform_lacks() -> None:
    """The whole suite, read for calls a cell of the matrix cannot make."""
    loose = []
    for path in _test_modules():
        source = path.read_text(encoding="utf-8")
        for line, spelled in calls_no_platform_asked(source):
            loose.append(f"{path.name} line {line}: {spelled}")
    assert not loose, (
        "these calls do not exist on every platform CI governs and "
        "nothing here has asked what platform this is, so the cells "
        "without them raise AttributeError before the test proves "
        "anything: "
        + ", ".join(loose)
        + ". Ask `os.name` in the same expression, mark the test to be "
        "skipped off its own platform, or -- better than either -- write "
        "the condition in the mechanism the other platform has, the way "
        "`test_failure_catalog.py` builds a file that will not open."
    )


def test_no_test_imports_a_module_only_one_platform_has() -> None:
    """Module-level imports, which run at collection on every cell."""
    loose = []
    for path in _test_modules():
        source = path.read_text(encoding="utf-8")
        for line, named in one_platform_imports(source):
            loose.append(f"{path.name} line {line}: {named}")
    assert not loose, (
        "these modules exist on one platform only, and a module-level "
        "import of one fails COLLECTION on every other -- taking the "
        "whole file's tests with it, not just the one that needed it: "
        + ", ".join(loose)
        + ". Import it inside the helper that uses it, where an "
        "ImportError is an answer rather than a crash."
    )


def test_the_reading_recognizes_the_shapes_it_claims_to() -> None:
    """A rule nobody can see working is a rule that can go quiet.

    Every acceptance and every refusal above, spelled out, so that a
    suite which stopped calling these APIs at all cannot leave this
    file passing on an empty reading.
    """
    assert calls_no_platform_asked("os.geteuid()\n") == [(1, "os.geteuid")]
    assert calls_no_platform_asked("x = os.getuid\n") == [(1, "os.getuid")]
    assert calls_no_platform_asked(
        'if os.name != "nt" and os.geteuid() == 0:\n    pass\n'
    ) == []
    assert calls_no_platform_asked(
        'if os.name == "posix":\n    os.getuid()\n'
    ) == []
    assert calls_no_platform_asked(
        '@pytest.mark.skipif(sys.platform == "win32", reason="")\n'
        "def test_one():\n"
        "    os.getuid()\n"
    ) == []
    assert calls_no_platform_asked("os.stat(p)\nos.chmod(p, 0)\n") == []
    assert one_platform_imports("import fcntl\n") == [(1, "fcntl")]
    assert one_platform_imports("from pwd import getpwuid\n") == [(1, "pwd")]
    assert one_platform_imports("def f():\n    import msvcrt\n") == []
    assert one_platform_imports("import os\nimport pathlib\n") == []
