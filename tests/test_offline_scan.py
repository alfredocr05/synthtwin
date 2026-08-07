"""Tests for the offline static scanner (plan D6.2 and D6.5).

The first tests prove the scanner accepts the real source tree and a
clean sample tree (no false alarms). Every other test is a mutation
check from plan D6.5: it writes a small source tree into tmp_path that
tries one known bypass class and asserts the scanner goes red on it,
with one 'file:line: explanation' line per violation.
"""

import importlib.util
import pathlib
import re
import subprocess
import sys
import textwrap

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCANNER_PATH = REPO_ROOT / "tools" / "offline_scan" / "scan_imports.py"
SRC_TREE = REPO_ROOT / "src" / "synthtwin"


def _load_scanner():
    spec = importlib.util.spec_from_file_location("scan_imports", SCANNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_SCANNER = _load_scanner()


def _scan_code(tmp_path, code):
    """Write one module into a fresh tree and scan that tree."""
    tree = tmp_path / "tree"
    tree.mkdir()
    (tree / "sample.py").write_text(textwrap.dedent(code), encoding="utf-8")
    return _SCANNER.scan_tree(tree)


def _assert_red(violations, needle):
    assert violations, (
        "expected the scanner to go red on this mutation, but it "
        "reported nothing"
    )
    joined = "\n".join(violations)
    assert needle in joined, (
        "expected a violation mentioning " + repr(needle) + ", got:\n" + joined
    )
    for line in violations:
        assert re.search(r":\d+: ", line), (
            "violation line is not in 'file:line: explanation' form: " + line
        )


# -- green paths -----------------------------------------------------


def test_real_src_tree_is_clean():
    """The shipped src/synthtwin tree passes the scanner."""
    violations = _SCANNER.scan_tree(SRC_TREE)
    assert violations == [], "\n".join(violations)


def test_clean_tree_passes(tmp_path):
    """A tree that uses every allowlisted API produces zero violations."""
    violations = _scan_code(
        tmp_path,
        '''
        import argparse
        import dataclasses
        import importlib.metadata
        import json
        import os
        import os.path
        import pathlib
        import sys
        import typing


        @dataclasses.dataclass
        class Record:
            label: str


        def version_text() -> str:
            try:
                return importlib.metadata.version("synthtwin")
            except Exception:
                return "unknown"


        def describe(raw: str) -> str:
            parser = argparse.ArgumentParser(prog="demo")
            parser.add_argument("--label")
            payload = json.loads(raw)
            base = pathlib.Path(os.getcwd())
            joined = os.path.join(os.fspath(base), "notes.txt")
            home = os.environ.get("HOME", "")
            details = os.lstat(os.fspath(base))
            label = typing.cast(str, home)
            sys.stdout.write(str(payload) + joined + str(details.st_mode))
            return label
        ''',
    )
    assert violations == [], "\n".join(violations)


def test_cli_exit_codes_and_line_format(tmp_path):
    """Exit 0 on a clean tree; exit 1 plus file:line lines on a red one."""
    clean = tmp_path / "clean"
    clean.mkdir()
    (clean / "ok.py").write_text("import json\n", encoding="utf-8")
    done = subprocess.run(
        [sys.executable, str(SCANNER_PATH), str(clean)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, done.stdout + done.stderr

    red = tmp_path / "red"
    red.mkdir()
    (red / "bad.py").write_text("import subprocess\n", encoding="utf-8")
    done = subprocess.run(
        [sys.executable, str(SCANNER_PATH), str(red)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 1, done.stdout + done.stderr
    assert re.search(r"bad\.py:1: ", done.stdout), done.stdout


# -- mutation checks, one per D6.5 bypass class ----------------------


def test_disallowed_import_goes_red(tmp_path):
    """Bypass class: importing a module that is not on the allowlist."""
    violations = _scan_code(
        tmp_path,
        '''
        import socket


        def touch() -> None:
            socket.create_connection(("example.com", 80))
        ''',
    )
    _assert_red(violations, "socket")


def test_dynamic_import_call_goes_red(tmp_path):
    """Bypass class: importlib.import_module loading a name built at
    run time."""
    violations = _scan_code(
        tmp_path,
        '''
        import importlib.metadata


        def sneak():
            return importlib.import_module("sub" + "process")
        ''',
    )
    _assert_red(violations, "import_module")


def test_entry_point_reference_goes_red(tmp_path):
    """Bypass class: importlib.metadata EntryPoint, a dynamic loader
    reachable through an otherwise allowed module."""
    violations = _scan_code(
        tmp_path,
        '''
        import importlib.metadata


        def sneak():
            handle = importlib.metadata.EntryPoint("n", "os:system", "g")
            return handle.load()
        ''',
    )
    _assert_red(violations, "EntryPoint")


def test_subprocess_reference_goes_red(tmp_path):
    """Bypass class: process launch through the subprocess module."""
    violations = _scan_code(
        tmp_path,
        '''
        import subprocess


        def run_it():
            return subprocess.run(["echo", "hi"])
        ''',
    )
    _assert_red(violations, "subprocess")


def test_os_spawnv_reference_goes_red(tmp_path):
    """Bypass class: process launch through os.spawn*."""
    violations = _scan_code(
        tmp_path,
        '''
        import os


        def run_it():
            return os.spawnv(0, "/bin/echo", ["echo"])
        ''',
    )
    _assert_red(violations, "spawn")


def test_ctypes_reference_goes_red(tmp_path):
    """Bypass class: native-code call through ctypes."""
    violations = _scan_code(
        tmp_path,
        '''
        import ctypes


        def native():
            return ctypes.CDLL(None)
        ''',
    )
    _assert_red(violations, "ctypes")


def test_sys_path_append_goes_red(tmp_path):
    """Bypass class: widening the import path via sys.path."""
    violations = _scan_code(
        tmp_path,
        '''
        import sys


        def widen():
            sys.path.append("/somewhere/else")
        ''',
    )
    _assert_red(violations, "sys.path")


def test_getattr_reflection_goes_red(tmp_path):
    """Bypass class: reflection primitives, including through an alias
    (g = getattr, then g(...))."""
    violations = _scan_code(
        tmp_path,
        '''
        import os


        def sneak():
            g = getattr
            launcher = g(os, "sys" + "tem")
            return launcher("echo hi")
        ''',
    )
    _assert_red(violations, "getattr")
    # The alias use must be caught too, not just the assignment line.
    alias_hits = [v for v in violations if "alias" in v]
    assert alias_hits, "\n".join(violations)


def test_split_string_lookup_via_module_registry_goes_red(tmp_path):
    """Bypass class (plan D6.2 reflective mutation 1): a split-string
    lookup through the preloaded module registry (sys.modules read),
    attempting a process call."""
    violations = _scan_code(
        tmp_path,
        '''
        import sys


        def sneak():
            module = sys.modules["o" + "s"]
            return module.system("echo hi")
        ''',
    )
    _assert_red(violations, "sys.modules")


def test_split_string_lookup_via_function_globals_goes_red(tmp_path):
    """Bypass class (plan D6.2 reflective mutation 2): a split-string
    lookup through an allowed function's global state (__globals__),
    attempting a process call."""
    violations = _scan_code(
        tmp_path,
        '''
        import os


        def anchor() -> str:
            return os.getcwd()


        def sneak():
            module = anchor.__globals__["o" + "s"]
            return module.system("echo hi")
        ''',
    )
    _assert_red(violations, "__globals__")
