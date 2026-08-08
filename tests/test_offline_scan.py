"""Tests for the offline static scanner (plan D6.2 and D6.5).

The first tests show the scanner accepts the real source tree and a
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


def test_untraced_receiver_method_call_goes_red(tmp_path):
    """A method call on a caller-supplied value must be rejected: the
    receiver is untraced, so the source text cannot say whose 'resolve'
    would run. There are no method calls on untraced values."""
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


def test_gated_string_method_on_parameter_stays_clean(tmp_path):
    """After the exact type gate checks that a parameter is a string,
    an enumerated string data method with a literal argument is
    accepted under the enumerated policy and produces zero violations.
    The gate does not settle that the receiver is a built-in str -- a
    str subclass passes isinstance and may supply its own find -- so
    this is the best-effort acceptance ratified as D6 Amendment A3,
    not a showing of exact dispatch. Both the negative gate shape and
    the positive-branch shape count."""
    violations = _scan_code(
        tmp_path,
        '''
        def marker_position(text):
            if not isinstance(text, str):
                raise ValueError("the text must be a plain string")
            return text.find("://")


        def marker_position_positive(text):
            if isinstance(text, str):
                return text.find("://")
            else:
                raise ValueError("the text must be a plain string")
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
    """The type gate covers the receiver, never the arguments: an
    unknown value handed to find on a gated parameter must still be
    rejected (an argument's own protocol hooks could run)."""
    violations = _scan_code(
        tmp_path,
        '''
        def sneak(text, needle):
            if not isinstance(text, str):
                raise ValueError("the text must be a plain string")
            return text.find(needle)
        ''',
    )
    _assert_red(violations, "'find'")


def test_unknown_callback_argument_to_data_method_goes_red(tmp_path):
    """The same rule for format: str.format invokes the formatting
    protocol of what it is handed, so an unknown parameter passed to
    a gated string's format method must be rejected."""
    violations = _scan_code(
        tmp_path,
        '''
        def sneak(text, cb):
            if not isinstance(text, str):
                raise ValueError("the text must be a plain string")
            return text.format(cb)
        ''',
    )
    _assert_red(violations, "'format'")


def test_literal_and_scanned_result_data_method_arguments_stay_clean(tmp_path):
    """Str-method arguments that this audit fully resolves stay
    accepted on a receiver this audit reads as a string: a name bound
    only to a literal, and the result of a call to a function defined
    in the scanned tree (the shape the shipped cli module uses)."""
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


# -- resolved call targets and enumerated module surfaces (round 4) --


def test_ungated_parameter_string_method_goes_red(tmp_path):
    """A string data method on a parameter WITHOUT the type gate must
    be rejected. Round 4 demonstrated the route at run time: with a
    caller-supplied object in place of the string, value.find("marker")
    ran the object's own find method, so without the isinstance check
    the scanner has no reading at all of what would run."""
    violations = _scan_code(
        tmp_path,
        '''
        def sneak(p):
            return p.find("marker")
        ''',
    )
    _assert_red(violations, "'find'")


def test_custom_object_method_dispatch_goes_red(tmp_path):
    """The dispatch route made concrete: an object of a scanned class
    that defines its own find method. The receiver is the result of a
    scanned constructor -- an untraced value -- so the method call
    must be rejected; at run time it would execute Probe.find, not
    str.find."""
    violations = _scan_code(
        tmp_path,
        '''
        class Probe:
            def find(self, needle):
                return len(needle)


        def run():
            probe = Probe()
            return probe.find("marker")
        ''',
    )
    _assert_red(violations, "'find'")


def test_shadowed_builtin_name_goes_red(tmp_path):
    """Rebinding a name this audit accepts as a built-in call target
    must be rejected: with str rebound, the isinstance type gate would
    check nothing at all. The binding itself is the violation, and the
    gate below it must not upgrade the parameter either."""
    violations = _scan_code(
        tmp_path,
        '''
        class Fake:
            pass


        str = Fake


        def sneak(text):
            if not isinstance(text, str):
                raise ValueError("nope")
            return text.find("marker")
        ''',
    )
    _assert_red(violations, "'str'")
    # The gate depended on the rebound name, so the method call must
    # stay red too, not just the rebinding line.
    find_hits = [v for v in violations if "'find'" in v]
    assert find_hits, "\n".join(violations)


def test_sys_call_tracing_goes_red(tmp_path):
    """sys.call_tracing invokes the function it is handed. sys is
    attribute-enumerated (platform, argv, exit, stdout, stderr,
    executable, version_info and nothing else), so this callback route
    missed in round 4 must be red."""
    violations = _scan_code(
        tmp_path,
        '''
        import sys


        def sneak(cb):
            return sys.call_tracing(cb, ())
        ''',
    )
    _assert_red(violations, "call_tracing")


def test_path_walk_on_error_callback_goes_red(tmp_path):
    """Path.walk hands its on_error argument to the library, which
    calls it on every failed directory read. walk is the one
    pathlib.Path instance method with a callable parameter, and its
    slot must reject an untraced value."""
    violations = _scan_code(
        tmp_path,
        '''
        import pathlib


        def sneak(raw, cb):
            base = pathlib.Path(raw)
            return list(base.walk(on_error=cb))
        ''',
    )
    _assert_red(violations, "callback slot 'on_error'")


def test_make_dataclass_decorator_callback_goes_red(tmp_path):
    """Python 3.14 adds a decorator parameter to make_dataclass and
    calls it to build the class. The slot must reject an untraced
    value no matter which interpreter runs the scan."""
    violations = _scan_code(
        tmp_path,
        '''
        import dataclasses


        def sneak(cb):
            return dataclasses.make_dataclass("C", [("n", int)], decorator=cb)
        ''',
    )
    _assert_red(violations, "callback slot 'decorator'")


def test_typing_get_type_hints_goes_red(tmp_path):
    """R4-B2: typing.get_type_hints evaluates string annotations as
    code. The round-4 runtime demonstration: with a string annotation
    whose text calls a marker function, get_type_hints compiled and
    evaluated that text and the marker function ran -- annotation text
    became running code while the offline scan stayed green. typing is
    now attribute-enumerated (Protocol and cast only), so every
    evaluator reference must be red."""
    violations = _scan_code(
        tmp_path,
        '''
        import typing


        def sneak(obj):
            return typing.get_type_hints(obj)


        def sneak_forward(text):
            return typing.ForwardRef(text)
        ''',
    )
    _assert_red(violations, "get_type_hints")
    _assert_red(violations, "ForwardRef")


# -- Phase 1 additions E1-E5 (plan phase-1-profiler.md, P1-D10) -------
#
# The two runtime libraries are enumerated down to individual attribute
# names, their instances may not be called through at all, and text
# tracking propagates only from origins this audit established. Each
# mutation below is one way that could be undone.


def test_unlisted_pandas_attribute_goes_red(tmp_path):
    violations = _scan_code(
        tmp_path,
        """
        import pandas


        def load(path):
            return pandas.read_sql("select 1", path)
        """,
    )
    _assert_red(violations, "pandas.read_sql")


def test_unlisted_numpy_attribute_goes_red(tmp_path):
    violations = _scan_code(
        tmp_path,
        """
        import numpy


        def load(path):
            return numpy.fromfile(path)
        """,
    )
    _assert_red(violations, "numpy.fromfile")


def test_numpy_load_goes_red(tmp_path):
    # numpy.load unpickles by default: it is a dynamic code loader
    # reached through an otherwise allowed module.
    violations = _scan_code(
        tmp_path,
        """
        import numpy


        def load(path):
            return numpy.load(path)
        """,
    )
    _assert_red(violations, "load")


def test_method_call_on_a_pandas_value_goes_red(tmp_path):
    # A data frame carries writers that reach the network on their own
    # (to_sql, to_gbq, the URL-accepting to_* family). Policy case (b)
    # would otherwise accept every one of them.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        import pathlib


        def export(path):
            frame = pandas.read_csv(pathlib.Path(path))
            return frame.to_sql("table", "postgresql://host/db")
        """,
    )
    _assert_red(violations, "produced by pandas")


def test_numpy_is_no_longer_importable_at_all(tmp_path):
    # Round 1 of the Phase 1 review showed numpy's reductions made the
    # published statistics depend on row order and on magnitude, so the
    # profiler computes them itself and imports numpy nowhere. The
    # library left the allowlist with the code that used it: the import
    # is now the violation, which is stricter than the method rule it
    # replaces.
    violations = _scan_code(
        tmp_path,
        """
        import numpy


        def dump(values, path):
            array = numpy.asarray(values, dtype=float)
            return array.tofile(path)
        """,
    )
    _assert_red(violations, "numpy")


def test_a_reduction_outside_the_math_enumeration_goes_red(tmp_path):
    # math.prod and math.sumprod are reductions with their own ordering
    # behaviour; only the five enumerated names are allowed.
    violations = _scan_code(
        tmp_path,
        """
        import math


        def total(values):
            return math.prod(values)
        """,
    )
    _assert_red(violations, "math.prod")


def test_reading_a_pandas_value_without_calling_it_stays_clean(tmp_path):
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        import pathlib

        from synthtwin.paths import validate_local_path


        def read(raw_path, names):
            validated = validate_local_path(raw_path, purpose="input")
            frame = pandas.read_csv(
                pathlib.Path(validated), names=names, dtype=str
            )
            return [list(frame[name]) for name in names], len(frame.columns)
        """,
    )
    assert violations == [], violations


def test_callable_in_a_read_csv_slot_goes_red(tmp_path):
    violations = _scan_code(
        tmp_path,
        """
        import pandas


        def clean(value):
            return value


        def read(path):
            return pandas.read_csv(path, converters={"a": clean})
        """,
    )
    _assert_red(violations, "converters")


def test_computed_callable_in_a_read_csv_slot_goes_red(tmp_path):
    violations = _scan_code(
        tmp_path,
        """
        import pandas


        def read(path, handler):
            return pandas.read_csv(path, on_bad_lines=handler)
        """,
    )
    _assert_red(violations, "on_bad_lines")


def test_unlisted_csv_attribute_goes_red(tmp_path):
    violations = _scan_code(
        tmp_path,
        """
        import csv


        def save(handle):
            return csv.writer(handle)
        """,
    )
    _assert_red(violations, "csv.writer")


def test_csv_dialect_callback_slot_goes_red(tmp_path):
    violations = _scan_code(
        tmp_path,
        """
        import csv


        def read(handle, dialect):
            return csv.reader(handle, dialect)
        """,
    )
    _assert_red(violations, "dialect")


def test_text_methods_chain_on_a_gated_parameter(tmp_path):
    # Extension E4: the result of a text method on accepted text is
    # text, so ordinary text handling no longer needs one helper
    # function per method call.
    violations = _scan_code(
        tmp_path,
        """
        def clean(text: str) -> str:
            if not isinstance(text, str):
                raise ValueError("not text")
            return text.strip().casefold().replace(",", "")
        """,
    )
    assert violations == [], violations


def test_a_method_outside_the_text_enumeration_goes_red(tmp_path):
    violations = _scan_code(
        tmp_path,
        """
        def clean(text: str) -> str:
            if not isinstance(text, str):
                raise ValueError("not text")
            return text.strip().encode("utf-8")
        """,
    )
    _assert_red(violations, "encode")


def test_a_non_text_result_does_not_become_text(tmp_path):
    # split returns a list. Treating its result as text would let a
    # method call through on a value this audit has not read.
    violations = _scan_code(
        tmp_path,
        """
        def first(text: str) -> str:
            if not isinstance(text, str):
                raise ValueError("not text")
            return text.split(",").pop()
        """,
    )
    _assert_red(violations, "pop")


def test_an_f_string_over_an_untraced_value_is_not_text(tmp_path):
    violations = _scan_code(
        tmp_path,
        """
        def describe(value):
            return f"{value}".strip()
        """,
    )
    _assert_red(violations, "strip")


def test_a_slice_of_an_untraced_value_is_not_text(tmp_path):
    violations = _scan_code(
        tmp_path,
        """
        def head(value):
            return value[:4].casefold()
        """,
    )
    _assert_red(violations, "casefold")


def test_a_slice_of_gated_text_stays_text(tmp_path):
    violations = _scan_code(
        tmp_path,
        """
        def head(text: str) -> str:
            if not isinstance(text, str):
                raise ValueError("not text")
            return text[:4].casefold()
        """,
    )
    assert violations == [], violations


# -- round-1 repairs: the fence, origin preservation, scope escapes ----


def test_read_csv_with_a_url_goes_red(tmp_path):
    # Round 1 (P1-R1-F1): this scanned clean, and the runtime probe
    # resolved a real hostname. Enumerating the NAME constrained nothing
    # about what it was handed.
    violations = _scan_code(
        tmp_path,
        """
        import pandas


        def fetch():
            return pandas.read_csv("https://example.invalid/table.csv")
        """,
    )
    _assert_red(violations, "trace to validate_local_path")


def test_read_csv_as_a_callback_goes_red(tmp_path):
    violations = _scan_code(
        tmp_path,
        """
        import pandas


        def fetch(paths):
            return list(map(pandas.read_csv, paths))
        """,
    )
    _assert_red(violations, "directly as the function of a call")


def test_read_csv_stored_in_a_variable_goes_red(tmp_path):
    violations = _scan_code(
        tmp_path,
        """
        import pandas


        def fetch(path):
            reader = pandas.read_csv
            return reader(path)
        """,
    )
    _assert_red(violations, "directly as the function of a call")


def test_read_csv_with_a_bare_path_object_goes_red(tmp_path):
    # A Path is not enough: the library turns it back into text before
    # deciding whether it is a URL.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        import pathlib


        def fetch(path):
            return pandas.read_csv(pathlib.Path(path))
        """,
    )
    _assert_red(violations, "trace to validate_local_path")


def test_read_csv_with_a_validated_path_stays_clean(tmp_path):
    violations = _scan_package(
        tmp_path,
        {
            "synthtwin/__init__.py": "",
            "synthtwin/paths.py": '''
                def validate_local_path(raw, purpose):
                    """Validate."""
                    if not isinstance(raw, str):
                        raise ValueError("not text")
                    return raw
                ''',
            "synthtwin/reading.py": """
                import pandas
                import pathlib

                from synthtwin.paths import validate_local_path


                def read(raw_path):
                    validated = validate_local_path(raw_path, purpose="input")
                    file_path = pathlib.Path(validated)
                    return pandas.read_csv(file_path, dtype=str)
                """,
        },
    )
    assert violations == [], violations


def test_a_cast_cannot_launder_a_pandas_frame(tmp_path):
    # Round 1 (P1-R1-F2): typing.cast retagged the value, E5 stopped
    # seeing pandas, and the reviewer's probe wrote a file with to_csv.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        import pathlib
        import typing

        from synthtwin.paths import validate_local_path


        def export(raw_path):
            validated = validate_local_path(raw_path, purpose="input")
            frame = pandas.read_csv(pathlib.Path(validated))
            disguised = typing.cast("object", frame)
            return disguised.to_sql("t", "postgresql://host/db")
        """,
    )
    _assert_red(violations, "produced by pandas")


def test_an_unenumerated_pandas_attribute_read_goes_red(tmp_path):
    # frame.style reaches a whole capability with no call in sight.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        import pathlib

        from synthtwin.paths import validate_local_path


        def style(raw_path):
            validated = validate_local_path(raw_path, purpose="input")
            frame = pandas.read_csv(pathlib.Path(validated))
            return frame.style
        """,
    )
    _assert_red(violations, "attribute")


def test_global_and_nonlocal_go_red(tmp_path):
    # Round 1 showed a module-level frame reached through `global`
    # shedding its origin on the way.
    violations = _scan_code(
        tmp_path,
        """
        frame = None


        def load():
            global frame
            frame = 1
        """,
    )
    _assert_red(violations, "global")


# -- round-2 repairs: every bypass the second review found -------------


def test_a_bare_imported_fenced_name_goes_red(tmp_path):
    # Round 2 (P1-R2-F1): `from pandas import read_csv` then map() over
    # it scanned clean, and pandas opened the URL it was handed.
    violations = _scan_code(
        tmp_path,
        """
        from pandas import read_csv


        def fetch(paths):
            return list(map(read_csv, paths))
        """,
    )
    _assert_red(violations, "read_csv")


def test_a_shadowed_validator_cannot_manufacture_provenance(tmp_path):
    # Round 2 (P1-R2-F1): redefining validate_local_path in the scanned
    # module as a pass-through minted the provenance the fence requires.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        import pathlib

        from synthtwin.paths import validate_local_path


        def validate_local_path(raw, purpose):
            return raw


        def fetch(raw_path):
            validated = validate_local_path(raw_path, purpose="input")
            return pandas.read_csv(pathlib.Path(validated))
        """,
    )
    _assert_red(violations, "trace to validate_local_path")


def test_a_keyword_cast_cannot_launder_a_frame(tmp_path):
    # Round 2 (P1-R2-F2): only the positional form was covered, and the
    # keyword form wrote a CSV.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        import pathlib
        import typing

        from synthtwin.paths import validate_local_path


        def export(raw_path):
            validated = validate_local_path(raw_path, purpose="input")
            frame = pandas.read_csv(pathlib.Path(validated))
            disguised = typing.cast(typ="object", val=frame)
            return disguised.to_csv("/tmp/out.csv")
        """,
    )
    _assert_red(violations, "produced by pandas")


def test_a_selected_column_is_still_a_pandas_object(tmp_path):
    # Round 2 (P1-R2-F2): frame["x"].to_csv wrote a file, and
    # frame["x"].values.tofile reached numpy even though numpy cannot be
    # imported at all.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        import pathlib

        from synthtwin.paths import validate_local_path


        def export(raw_path):
            validated = validate_local_path(raw_path, purpose="input")
            frame = pandas.read_csv(pathlib.Path(validated))
            return frame["secret"].to_csv("/tmp/out.csv")
        """,
    )
    _assert_red(violations, "produced by pandas")


def test_a_validated_path_still_obeys_the_callback_slot_rule(tmp_path):
    # Round 2 (P1-R2-F10): the new provenance origin made a validated
    # path stop being a Path for the slot table, so Path.walk's
    # on_error accepted a caller-supplied callback.
    violations = _scan_code(
        tmp_path,
        """
        from synthtwin.paths import validate_local_path


        def walk(raw_path, callback):
            validated = validate_local_path(raw_path, purpose="input")
            return validated.walk(on_error=callback)
        """,
    )
    _assert_red(violations, "on_error")


# -- round-3 repairs: a closed grammar for call targets ----------------


def test_a_conditional_receiver_goes_red(tmp_path):
    # Round 3 (P1-R3-F7): each computed receiver form scanned clean and
    # invoked the caller's callback at runtime.
    violations = _scan_code(
        tmp_path,
        """
        import pathlib


        def walk(raw, choose, callback):
            place = pathlib.Path(raw)
            return (place if choose else place).walk(on_error=callback)
        """,
    )
    _assert_red(violations, "does not resolve")


def test_a_boolean_receiver_goes_red(tmp_path):
    violations = _scan_code(
        tmp_path,
        """
        import pathlib


        def walk(raw, callback):
            place = pathlib.Path(raw)
            return (place or place).walk(False, callback)
        """,
    )
    _assert_red(violations, "does not resolve")


def test_a_computed_call_target_goes_red(tmp_path):
    violations = _scan_code(
        tmp_path,
        """
        def run(choose, callback):
            return (callback if choose else callback)("payload")
        """,
    )
    _assert_red(violations, "does not resolve")


# -- round-4: a name that is both imported and defined is not the API --


def test_a_locally_defined_path_is_not_pathlib_path(tmp_path):
    # Round 4 (P1-R4-F1). This RAN: the validator checked one file and
    # the reader opened another through a web address, because the
    # module both imported Path and defined one, and this audit kept
    # trusting the import.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        from pathlib import Path

        from synthtwin.paths import validate_local_path


        def Path(raw):
            return "file:///tmp/other.csv"


        def fetch(raw_path):
            validated = validate_local_path(raw_path, purpose="input")
            return pandas.read_csv(Path(validated))
        """,
    )
    _assert_red(violations, "trace to validate_local_path")


def test_a_locally_defined_cast_is_not_typing_cast(tmp_path):
    # Round 4 (P1-R4-F1), second example. This RAN too, and overwrote
    # the user's own table with the frame's contents.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        import pathlib
        from typing import cast

        from synthtwin.paths import validate_local_path


        def cast(typ, val):
            return typ


        def damage(raw_path):
            validated = validate_local_path(raw_path, purpose="input")
            frame = pandas.read_csv(pathlib.Path(validated))
            disguised = cast(frame, pathlib.Path(validated))
            disguised.to_csv(raw_path)
        """,
    )
    _assert_red(violations, "to_csv")


# -- round-5: class bodies are not closures; a match capture binds ------


def test_a_class_level_import_does_not_shadow_a_module_function(tmp_path):
    # Round 5 (P1-R5-F1). Python resolves an unqualified name in a method
    # to the MODULE, never to the enclosing class, so the class-level
    # pathlib.Path here is not what runs -- the module-level function is.
    violations = _scan_code(
        tmp_path,
        """
        import pandas

        from synthtwin.paths import validate_local_path


        def Path(raw):
            return "file:///tmp/other.csv"


        class Reader:
            from pathlib import Path

            def fetch(self, raw_path):
                validated = validate_local_path(raw_path, purpose="input")
                return pandas.read_csv(Path(validated))
        """,
    )
    _assert_red(violations, "trace to validate_local_path")


def test_a_match_capture_rebinds_the_name(tmp_path):
    # Round 5 (P1-R5-F1). `case path:` binds `path`, but the name lives
    # in a plain string field rather than a Name node, so nothing
    # recorded the store and the captured frame inherited the origin of
    # the validated path it replaced.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        import pathlib

        from synthtwin.paths import validate_local_path


        def damage(raw_path):
            validated = validate_local_path(raw_path, purpose="input")
            path = pathlib.Path(validated)
            frame = pandas.read_csv(path)
            match frame:
                case path:
                    return path.to_csv(raw_path)
            return None
        """,
    )
    _assert_red(violations, "to_csv")
