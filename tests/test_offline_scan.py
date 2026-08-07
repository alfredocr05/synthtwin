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


def _scan_package(tmp_path, modules):
    """Write several modules (relative path -> source) and scan the tree."""
    tree = tmp_path / "tree"
    for relative, code in modules.items():
        path = tree / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(code), encoding="utf-8")
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
    """A tree that uses every allowlisted API produces zero violations.

    Every module-rooted access here is a single attribute step past an
    allowlisted module (or a read-only os.environ method), which is the
    exact surface the scanner can verify from the source text alone.
    """
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
            if sys.platform != "made-up":
                print(str(payload) + joined + str(details.st_mode))
            return label
        ''',
    )
    assert violations == [], "\n".join(violations)


def test_intra_package_single_step_stays_clean(tmp_path):
    """Intra-package imports stay allowed: one attribute step past a
    synthtwin module (a direct reference to something that module
    defines) produces zero violations, in both import styles."""
    violations = _scan_code(
        tmp_path,
        '''
        import synthtwin.paths
        from synthtwin import paths


        def check(raw: str):
            first = synthtwin.paths.validate_local_path(raw, purpose="input")
            second = paths.validate_local_path(raw, purpose="output")
            return first, second
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


def test_os_path_module_reexport_route_goes_red(tmp_path):
    """Bypass class: a process call reached through a module that an
    allowed module re-exports (os.path.os is the os module itself, so
    os.path.os.system reaches os.system through the allowed os.path).
    A module re-exported by an allowed module must never be trusted."""
    violations = _scan_code(
        tmp_path,
        '''
        import os


        def sneak():
            return os.path.os.system("echo hi")
        ''',
    )
    _assert_red(violations, "os.path.os.system")


def test_intra_package_chain_to_capability_goes_red(tmp_path):
    """Bypass class: reaching a capability through an intra-package
    module's own imports (synthtwin.paths imports os, so
    synthtwin.paths.os.system would reach a process call through a
    first-party module that scans clean on its own)."""
    violations = _scan_code(
        tmp_path,
        '''
        import synthtwin.paths


        def sneak():
            return synthtwin.paths.os.system("echo hi")
        ''',
    )
    _assert_red(violations, "synthtwin.paths.os.system")


def test_intra_package_second_attribute_step_goes_red(tmp_path):
    """Only one attribute step past an intra-package module can be
    checked from the source text; a second step must be rejected."""
    violations = _scan_code(
        tmp_path,
        '''
        import synthtwin.paths


        def sneak():
            return synthtwin.paths.PathValidationError.args
        ''',
    )
    _assert_red(violations, "more than one attribute")


def test_conditional_rebinding_never_clears_module_origin(tmp_path):
    """Bypass class: name binding must be flow-insensitive. A store on
    a branch that can never run must not make the scanner forget that
    the name still holds an imported module at run time."""
    violations = _scan_code(
        tmp_path,
        '''
        import os as capability

        if False:
            capability = 0

        capability.system("noop")
        ''',
    )
    _assert_red(violations, "os.system")


def test_unknown_callback_call_goes_red(tmp_path):
    """Bypass class: a call through a name the scanner cannot trace to
    any known function or class (a callback parameter) must be
    rejected, because the source text alone cannot say what would run."""
    violations = _scan_code(
        tmp_path,
        '''
        def invoke(cb):
            cb("x")
        ''',
    )
    _assert_red(violations, "cb")


def test_module_passed_as_bare_value_goes_red(tmp_path):
    """Bypass class: handing a module object to a helper as a plain
    value would let the helper reach any of that module's attributes
    without a traceable chain; the hand-off itself must be rejected."""
    violations = _scan_code(
        tmp_path,
        '''
        import os


        def helper(thing):
            return thing


        helper(os.path)
        ''',
    )
    _assert_red(violations, "bare value")


# -- first-party re-export laundering (round-2 blocker 1) ------------


def test_first_party_from_import_of_sibling_import_goes_red(tmp_path):
    """Bypass class: 'from synthtwin.paths import os' hands over the
    real standard-library os module through a sibling that merely
    imported it. The scanner parses the sibling's source, sees that
    'os' is an import and not a definition, and must reject the
    laundering by name."""
    violations = _scan_package(
        tmp_path,
        {
            "synthtwin/__init__.py": "",
            "synthtwin/paths.py": '''
                import os


                def validate_local_path(raw, *, purpose):
                    return raw
            ''',
            "consumer.py": '''
                from synthtwin.paths import os


                def sneak():
                    return os.system("echo hi")
            ''',
        },
    )
    _assert_red(violations, "launder")
    named = [v for v in violations if "'os'" in v and "synthtwin.paths" in v]
    assert named, "\n".join(violations)


def test_first_party_reexport_without_sibling_source_goes_red(tmp_path):
    """Same laundering route when the sibling's source is NOT part of
    the scanned tree: an imported name that matches a known module
    name cannot be verified and must be rejected."""
    violations = _scan_code(
        tmp_path,
        '''
        from synthtwin.paths import os


        def sneak():
            return os.system("echo hi")
        ''',
    )
    _assert_red(violations, "'os'")


def test_first_party_from_import_of_defined_name_stays_clean(tmp_path):
    """A first-party `from` import of a name the sibling genuinely
    defines (a def at its top level) produces zero violations."""
    violations = _scan_package(
        tmp_path,
        {
            "synthtwin/__init__.py": "",
            "synthtwin/paths.py": '''
                import os


                def validate_local_path(raw, *, purpose):
                    return raw
            ''',
            "consumer.py": '''
                from synthtwin.paths import validate_local_path


                def check(raw):
                    return validate_local_path(raw, purpose="input")
            ''',
        },
    )
    assert violations == [], "\n".join(violations)


# -- unresolved call targets (round-2 blocker 2) ---------------------


def test_parameter_method_outside_data_list_goes_red(tmp_path):
    """A method call on a caller-supplied value must be rejected when
    the method name is outside the enumerated data-method list;
    'resolve' is deliberately not on that list."""
    violations = _scan_code(
        tmp_path,
        '''
        def sneak(p):
            return p.resolve()
        ''',
    )
    _assert_red(violations, "resolve")


def test_callback_union_keeps_unknown_and_goes_red(tmp_path):
    """A callback whose origin set still holds the unknown member must
    be rejected even when a branch rebinds it to an allowed API: the
    unknown possibility is never discarded when other origins join."""
    violations = _scan_code(
        tmp_path,
        '''
        import json


        def invoke(cb, flag):
            if flag:
                cb = json.loads
            return cb("{}")
        ''',
    )
    _assert_red(violations, "cb")


def test_def_name_passed_to_external_helper_goes_red(tmp_path):
    """A scanned function passed as a value to an allowed external
    helper must be rejected: the helper decides when and how the
    callable runs, outside anything this audit can see."""
    violations = _scan_code(
        tmp_path,
        '''
        def shout(text):
            return text


        def run():
            return sorted(["b", "a"], key=shout)
        ''',
    )
    _assert_red(violations, "shout")


def test_lambda_passed_to_external_helper_goes_red(tmp_path):
    """A lambda handed to an external helper is the same hand-off of a
    callable and must be rejected."""
    violations = _scan_code(
        tmp_path,
        '''
        def run(rows):
            return sorted(rows, key=lambda row: row)
        ''',
    )
    _assert_red(violations, "lambda")


def test_argparse_instance_method_calls_stay_clean(tmp_path):
    """Values returned by allowlisted APIs are tracked as
    api-instances whose method calls are accepted: the full argparse
    build/parse sequence produces zero violations."""
    violations = _scan_code(
        tmp_path,
        '''
        import argparse


        def run(argv):
            parser = argparse.ArgumentParser(prog="demo")
            parser.add_argument("--version", action="store_true")
            args = parser.parse_args(argv)
            if args.version:
                print("ok")
            return 0
        ''',
    )
    assert violations == [], "\n".join(violations)


def test_string_data_method_on_parameter_stays_clean(tmp_path):
    """A data method from the enumerated list, called on a
    caller-supplied string, produces zero violations."""
    violations = _scan_code(
        tmp_path,
        '''
        def marker_position(text):
            return text.find("://")
        ''',
    )
    assert violations == [], "\n".join(violations)


# -- callback slots of allowed APIs (round-3 follow-up on R2-B2) -----


def test_unknown_callback_in_sorted_key_slot_goes_red(tmp_path):
    """Bypass class: an unknown parameter placed in the 'key' slot of
    sorted. The helper itself is allowed, but it calls whatever sits
    in that slot, so an untraceable value there is a hidden call
    target and must be rejected."""
    violations = _scan_code(
        tmp_path,
        '''
        def run(rows, cb):
            return sorted(rows, key=cb)
        ''',
    )
    _assert_red(violations, "callback slot 'key'")


def test_unknown_callback_in_json_object_hook_slot_goes_red(tmp_path):
    """Bypass class: an unknown parameter as the object_hook of
    json.loads. json would call it once per parsed object."""
    violations = _scan_code(
        tmp_path,
        '''
        import json


        def parse(s, cb):
            return json.loads(s, object_hook=cb)
        ''',
    )
    _assert_red(violations, "callback slot 'object_hook'")


def test_unknown_callback_in_add_argument_type_slot_goes_red(tmp_path):
    """Bypass class: an unknown parameter as the 'type' conversion of
    ArgumentParser.add_argument. argparse would call it on every
    matching command-line value."""
    violations = _scan_code(
        tmp_path,
        '''
        import argparse


        def build(cb):
            parser = argparse.ArgumentParser(prog="demo")
            parser.add_argument("--n", type=cb)
            return parser
        ''',
    )
    _assert_red(violations, "callback slot 'type'")


def test_unknown_callback_in_map_function_slot_goes_red(tmp_path):
    """The same rule for a POSITIONAL callback slot: map's first
    argument is the function it applies, so an unknown parameter
    there must be rejected."""
    violations = _scan_code(
        tmp_path,
        '''
        def run(rows, cb):
            return list(map(cb, rows))
        ''',
    )
    _assert_red(violations, "'map'")


def test_first_party_import_in_callback_slot_goes_red(tmp_path):
    """A first-party function imported from a sibling and placed in a
    callback slot must be rejected: the external API would invoke it
    outside scanned control."""
    violations = _scan_package(
        tmp_path,
        {
            "synthtwin/__init__.py": "",
            "synthtwin/paths.py": '''
                def validate_local_path(raw, *, purpose):
                    return raw
            ''',
            "consumer.py": '''
                from synthtwin.paths import validate_local_path


                def run(rows):
                    return sorted(rows, key=validate_local_path)
            ''',
        },
    )
    _assert_red(violations, "callback slot 'key'")


def test_data_arguments_in_non_callback_slots_stay_clean(tmp_path):
    """Data arguments outside the enumerated callback slots stay
    accepted: json.loads(raw) and parser.parse_args(argv) with
    caller-supplied values produce zero violations."""
    violations = _scan_code(
        tmp_path,
        '''
        import argparse
        import json


        def run(raw, argv):
            parser = argparse.ArgumentParser(prog="demo")
            parser.add_argument("--version", action="store_true")
            args = parser.parse_args(argv)
            payload = json.loads(raw)
            return args, payload
        ''',
    )
    assert violations == [], "\n".join(violations)


def test_unknown_argument_to_data_method_goes_red(tmp_path):
    """An accepted data method on an untraced value must reject an
    unknown argument: the receiver's method could do anything with
    what it receives, including calling it."""
    violations = _scan_code(
        tmp_path,
        '''
        def sneak(text, needle):
            return text.find(needle)
        ''',
    )
    _assert_red(violations, "'find'")


def test_unknown_callback_argument_to_data_method_goes_red(tmp_path):
    """The same rule for format: an unknown parameter handed to the
    format method of an untraced value must be rejected."""
    violations = _scan_code(
        tmp_path,
        '''
        def sneak(text, cb):
            return text.format(cb)
        ''',
    )
    _assert_red(violations, "'format'")


def test_literal_and_scanned_result_data_method_arguments_stay_clean(tmp_path):
    """Data-method arguments that this audit fully resolves stay
    accepted: a name bound only to a literal, and the result of a
    call to a function defined in the scanned tree (the shape the
    shipped cli module uses)."""
    violations = _scan_code(
        tmp_path,
        '''
        _LABEL = "demo {version} at {home}"


        def _version():
            return "1"


        def render():
            return _LABEL.format(version=_version(), home="here")
        ''',
    )
    assert violations == [], "\n".join(violations)
