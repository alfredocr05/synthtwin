"""Offline static scanner for the synthtwin source tree (plan D6.2, D6.5).

What this tool does, in plain terms: synthtwin promises to run fully
offline -- no network, no launching of other programs, no native code,
and no code loaded dynamically while the program runs. This scanner
reads every Python file under a given source tree WITHOUT running it and
checks that the code uses only the exact, enumerated APIs the Phase 0
plan allows. Anything else is reported, one line per problem, and the
scan fails.

Policy enforced (plan D6.2, a positive AST/name-binding policy):

* Allowed modules for src/: argparse, dataclasses, json, pathlib,
  typing, sys (but sys.modules and sys.path may never be read or
  written); from os only the os.path functions, os.fspath, os.getcwd,
  os.lstat, and read-only os.environ; from importlib.metadata only the
  version() function. Imports of the synthtwin package's own modules are
  allowed because those files are scanned too. Every other import is a
  violation.
* Always forbidden, allowlist aside: __import__,
  importlib.import_module, exec, eval, compile, subprocess, os.system,
  os.exec*, os.spawn*, os.popen, os.fork, os.posix_spawn, ctypes, cffi,
  multiprocessing, and the reflection primitives getattr, setattr,
  delattr, hasattr, vars, globals, locals, and dir. Aliases are traced
  to their origin, so "g = getattr" followed by "g(...)" is caught.
* Every attribute chain that starts from an imported module must
  resolve, in the source text alone, to an exact enumerated API. A
  chain may take exactly ONE attribute step past a module (os.getcwd,
  os.path.join, json.loads, sys.platform,
  importlib.metadata.version); the only deeper forms accepted are the
  read-only os.environ methods (os.environ.get and friends). Anything
  deeper is rejected, and so is any step whose attribute names another
  module (os.path.os, pathlib.os, json.decoder) or starts with an
  underscore: an allowed module that re-exports another module never
  makes that other module's power allowed.
* The same one-step rule applies to the package's own modules, and
  first-party `from` imports are verified against what the named
  sibling module really defines. Every scanned synthtwin module is
  parsed and its top-level names are recorded: names bound by def,
  class, or a plain assignment are genuine and may be imported or
  referenced in one attribute step
  (synthtwin.paths.validate_local_path); names the module itself
  imported are NOT importable from it ("from synthtwin.paths import
  os" is rejected), because that would launder the sibling's own
  imports past this audit -- the object handed over is the real
  imported module, with all its power. A second attribute step
  (synthtwin.paths.name.attr), or a step whose attribute names a
  module (synthtwin.paths.os), is rejected as before. When the
  sibling's source is not part of the scanned tree, importing a name
  that matches a known module name is rejected for the same reason.
* Name binding is flow-insensitive on purpose and keeps an EXPLICIT
  unknown member. A name bound to a module (or any traced origin)
  ANYWHERE in a scope keeps that origin for the whole scope, no
  matter what else is assigned to it, even on branches that can never
  run. A name bound to anything this audit cannot trace (a function
  parameter, a computed value) carries the unknown member, and other
  origins joining the set NEVER discard it: rebinding adds
  possibilities, it never clears suspicion.
* A call through a bare name is accepted only when EVERY possible
  origin of the name is a function or class defined in the scanned
  tree, an import traced to the allowlist, or one of a small fixed
  list of built-in constructors and helpers (str, len, print, ...).
  If any possible origin is unknown -- above all a function parameter
  used as a call target, even one that is rebound to an allowed API
  on some branch -- the call is rejected, because this audit cannot
  see what would run. Higher-order callback parameters are therefore
  banned in synthtwin source for Phase 0.
* Method calls (value.method(...)) are accepted in exactly two
  enumerated cases; every other method call target is rejected.
  (a) On a value this audit cannot trace (a function parameter, the
      result of a first-party call, a literal), only the fixed
      data-method list is accepted: find, format. That list is
      exactly the set of plain string data methods the current src
      tree calls on such values; none of them can start a program,
      open a connection, load code, or reach an attribute through a
      computed name. Threat-model rationale for accepting them at
      all: caller-supplied objects execute in the caller's own
      process, and this boundary controls what synthtwin's own code
      initiates, not what the caller's own code does; these data
      methods initiate nothing beyond reading or building text. Any
      other method name on an untraced value is a violation
      (parameter.resolve() is rejected).
  (b) A value returned by a call to an allowlisted API
      (parser = argparse.ArgumentParser(...)) is tracked as an
      api-instance, and method calls on it
      (parser.add_argument(...)) are accepted: the API that produced
      the value was itself checked against the allowlist. A value
      built by an operator expression with an api-instance operand
      (pathlib.Path(...) / name) is tracked the same way.
* A function or lambda passed as a call argument to any callee not
  defined in the scanned tree is rejected: outside code could keep
  the callable and run it at any time, in ways this audit cannot
  see. Handing a callable to a function defined in the scanned tree
  is fine, because every call site inside that function is scanned
  under the same rules. Targets put together while the program runs
  (double-underscore internals, lookups through the module table,
  subscripted call targets, star imports) are rejected as before.

Exit status: 0 clean; 1 one or more violations, each printed as
"file:line: explanation"; 2 the command line itself was wrong.

This tool uses only the Python standard library (ast, pathlib, sys,
argparse) and never imports or runs the code it checks.
"""

import argparse
import ast
import pathlib
import sys

_FIRST_PARTY_ROOT = "synthtwin"

_UNRESTRICTED_MODULES = {"argparse", "dataclasses", "json", "pathlib", "typing"}

# Dotted paths that name a module object (as opposed to a function or
# class). Bare references to these outside an import statement or a
# direct dotted access are rejected. Per-file scanning extends this set
# with intra-package module paths seen in import statements.
_KNOWN_MODULE_PATHS = _UNRESTRICTED_MODULES | {
    "sys",
    "os",
    "os.path",
    "importlib",
    "importlib.metadata",
}

_REFLECTION_PRIMITIVES = {
    "getattr",
    "setattr",
    "delattr",
    "hasattr",
    "vars",
    "globals",
    "locals",
    "dir",
}

_DYNAMIC_CODE_PRIMITIVES = {"exec", "eval", "compile", "__import__"}

_BANNED_BUILTINS = _REFLECTION_PRIMITIVES | _DYNAMIC_CODE_PRIMITIVES

_FORBIDDEN_MODULES = {
    "subprocess": "start other programs on this computer",
    "ctypes": "run native machine code",
    "cffi": "run native machine code",
    "multiprocessing": "launch new processes",
}

# Attribute names that are banned wherever they appear, because they
# name dynamic loaders reachable through otherwise-allowed objects.
_ENTRY_POINT_TOKENS = {"EntryPoint", "entry_points"}

_ALLOWED_DUNDER_NAMES = {"__name__", "__doc__", "__file__", "__version__", "__all__"}

_ENV_READ_METHODS = {"get", "keys", "items", "values", "copy"}

# The explicit unknown member of the origin lattice. A name carrying
# this member may hold ANYTHING at run time; other origins joining the
# same set never discard it.
_UNKNOWN = ("unknown", "")

# The only method names that may be called on a value this audit cannot
# trace (policy case (a) in the module docstring). This is exactly the
# set of plain string data methods the current src tree calls on such
# values; adding a name here is a policy decision reviewed against the
# threat model, not a routine code change.
_UNKNOWN_VALUE_METHODS = {"find", "format"}

# sys.modules and sys.path per the plan; the other three are the rest of
# the interpreter's import machinery reachable through sys.
_SYS_BANNED = (
    "sys.modules",
    "sys.path",
    "sys.meta_path",
    "sys.path_hooks",
    "sys.path_importer_cache",
)

_OS_ALLOWED_EXACT = {"os.fspath", "os.getcwd", "os.lstat"}

# Attribute names that are known to name modules when reached through
# another module's namespace (allowed modules re-export several of
# these: os.path holds os and sys, pathlib holds os, json holds its
# decoder/encoder/scanner submodules, and so on). Reaching one module
# through another module's attribute is never allowed, from any root,
# including the package's own modules (synthtwin.paths.os is how
# synthtwin.paths sees its own import of os).
_MODULE_ATTR_BLOCK = {
    "abc",
    "argparse",
    "cffi",
    "codecs",
    "collections",
    "contextlib",
    "copy",
    "copyreg",
    "csv",
    "ctypes",
    "dataclasses",
    "decoder",
    "email",
    "encoder",
    "enum",
    "errno",
    "fnmatch",
    "functools",
    "genericpath",
    "glob",
    "importlib",
    "inspect",
    "io",
    "itertools",
    "json",
    "keyword",
    "math",
    "multiprocessing",
    "nt",
    "ntpath",
    "operator",
    "os",
    "path",
    "pathlib",
    "pickle",
    "posix",
    "posixpath",
    "random",
    "re",
    "reprlib",
    "scanner",
    "shutil",
    "socket",
    "stat",
    "string",
    "struct",
    "subprocess",
    "sys",
    "tempfile",
    "textwrap",
    "threading",
    "time",
    "types",
    "typing",
    "unicodedata",
    "warnings",
    "zipfile",
}

# Bare-name call targets that are accepted without a traced origin:
# built-in constructors, plain data helpers, and the exception types
# product code may raise. Nothing on this list can start a program,
# open a connection, load code, or reach an attribute by computed name.
_ALLOWED_CALL_BUILTINS = {
    "abs",
    "all",
    "any",
    "bool",
    "bytearray",
    "bytes",
    "chr",
    "dict",
    "divmod",
    "enumerate",
    "filter",
    "float",
    "format",
    "frozenset",
    "hash",
    "hex",
    "int",
    "isinstance",
    "issubclass",
    "iter",
    "len",
    "list",
    "map",
    "max",
    "min",
    "next",
    "oct",
    "ord",
    "print",
    "range",
    "repr",
    "reversed",
    "round",
    "set",
    "slice",
    "sorted",
    "str",
    "sum",
    "tuple",
    "zip",
    "Exception",
    "FileNotFoundError",
    "IndexError",
    "KeyError",
    "NotImplementedError",
    "OSError",
    "PermissionError",
    "RuntimeError",
    "StopIteration",
    "TypeError",
    "ValueError",
}

_ALLOWLIST_NOTE = (
    "The Phase 0 allowlist (plan D6.2) permits only: argparse, "
    "dataclasses, json, pathlib, typing, sys (never sys.modules or "
    "sys.path), os.path plus os.fspath, os.getcwd, os.lstat and "
    "read-only os.environ, and importlib.metadata.version(). Adding "
    "anything is a plan-level decision, not a code change."
)


def _is_dunder(name: str) -> bool:
    return len(name) > 4 and name.startswith("__") and name.endswith("__")


def _chain_parts(node: ast.AST) -> "list[str] | None":
    """Return ["root", "attr", ...] for a pure Name/Attribute chain.

    Returns None when the expression is anything else (a call result, a
    subscript result, a literal, ...).
    """
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        parts.reverse()
        return parts
    return None


def _first_party_module_name(path: pathlib.Path) -> "str | None":
    """Dotted first-party module name for ``path``, or None.

    A file is first-party when a folder named exactly like the
    first-party root sits on its path. The LAST such folder is taken as
    the package root, because an outer folder (for example the
    repository folder itself) may carry the same name.
    """
    parts = path.parts
    root_index = None
    for index in range(len(parts) - 1):
        if parts[index] == _FIRST_PARTY_ROOT:
            root_index = index
    if root_index is None:
        return None
    stem = parts[-1].removesuffix(".py")
    pieces = list(parts[root_index:-1])
    if stem != "__init__":
        pieces.append(stem)
    return ".".join(pieces)


def _module_bindings(tree: ast.Module) -> "tuple[set[str], set[str]]":
    """Split one module's top-level names into (defined, imported).

    ``defined`` holds the names the module genuinely defines: def,
    class, and plain assignments to a bare name, anywhere at module
    level (including inside if/try blocks, which still bind module
    names). ``imported`` holds every name the module itself imported.
    A name in both sets counts as imported, because the source text
    alone cannot prove the assignment replaced the imported object.
    Nested function, class, and lambda bodies bind nothing at module
    level and are not entered.
    """
    defined: set[str] = set()
    imported: set[str] = set()
    stack: list[ast.AST] = list(tree.body)
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.add(node.name)
        elif isinstance(node, ast.Lambda):
            continue
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.asname or alias.name.partition(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name != "*":
                    imported.add(alias.asname or alias.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    defined.add(target.id)
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.value is not None:
                defined.add(node.target.id)
        else:
            stack.extend(ast.iter_child_nodes(node))
    return defined - imported, imported


def _primitive_message(name: str) -> str:
    if name in _REFLECTION_PRIMITIVES:
        return (
            "uses the reflection primitive '" + name + "', which can "
            "reach any function or attribute through a name computed "
            "while the program runs. That defeats this offline audit; "
            "call what you need by its direct, written-out name instead."
        )
    return (
        "uses '" + name + "', which can turn text into running code. "
        "That defeats this offline audit and is never allowed in "
        "synthtwin source."
    )


def _forbidden_module_message(name: str, how_used: str) -> str:
    return (
        how_used + " '" + name + "', which can "
        + _FORBIDDEN_MODULES[name]
        + ". synthtwin promises never to do that; remove it."
    )


def _bare_module_message(dotted: str) -> str:
    return (
        "refers to the module '" + dotted + "' as a bare value. Module "
        "objects passed through variables or containers can hide what "
        "gets called later; write the full dotted access (for example "
        "os.path.join) instead."
    )


def _module_hop_message(dotted: str, part: str) -> str:
    return (
        "uses '" + dotted + "': the attribute '" + part + "' names a "
        "module reached through another module's namespace. This audit "
        "accepts only APIs named directly on an allowlisted module, "
        "never a module re-exported by another module; import what you "
        "need directly from the allowlist instead."
    )


def _private_hop_message(dotted: str, part: str) -> str:
    return (
        "uses '" + dotted + "': the attribute '" + part + "' starts "
        "with an underscore. Underscore names are a module's internal "
        "machinery and often alias other modules; they are not part of "
        "any allowlisted API."
    )


def _deep_chain_message(dotted: str, prefix: str) -> str:
    return (
        "uses '" + dotted + "', which steps more than one attribute "
        "past the module '" + prefix + "'. Reading the source can "
        "verify only a single, directly named attribute of a module; "
        "anything deeper can reach objects this audit never cleared. "
        "Name the API you need in one step."
    )


def _unknown_call_message(name: str) -> str:
    return (
        "calls '" + name + "', but on at least one path '" + name + "' "
        "may hold a value this audit cannot trace to any function or "
        "class defined in the scanned code, to an allowlisted import, "
        "or to the fixed list of accepted built-ins. A function passed "
        "around as a value (a callback) cannot be checked by reading "
        "the source, and a possibility once recorded is never "
        "discarded, so Phase 0 synthtwin source must call every "
        "function by its written-out name."
    )


def _unknown_method_message(method: str) -> str:
    return (
        "calls the method '" + method + "' on a value this audit "
        "cannot trace to any allowlisted API. On an untraced value "
        "only the fixed data-method list ("
        + ", ".join(sorted(_UNKNOWN_VALUE_METHODS))
        + ") is accepted, because any other method could be a "
        "capability this audit never cleared. Build the value from an "
        "allowlisted API, or call the operation you need by its "
        "written-out allowlisted name."
    )


def _callable_argument_message(described: str) -> str:
    return (
        "passes " + described + " as an argument to a callee that is "
        "not defined in the scanned code. Outside code could keep the "
        "callable and run it at any time, in ways this audit cannot "
        "see; Phase 0 synthtwin source may hand functions only to its "
        "own scanned functions."
    )


def _reexport_message(module: str, name: str) -> str:
    return (
        "reaches '" + name + "' through '" + module + "', but '"
        + module + "' does not define '" + name + "': it merely "
        "imports it. Importing or reaching a name a sibling module "
        "itself imported would launder the sibling's own imports past "
        "this audit -- the object handed over is the real imported "
        "module or API, with all its power. Import what you need "
        "directly so the allowlist can check it."
    )


def _undefined_export_message(module: str, name: str) -> str:
    return (
        "reaches '" + name + "' through '" + module + "', but '"
        + module + "' does not define a top-level function, class, or "
        "plain assignment named '" + name + "'. Only names a sibling "
        "module genuinely defines can be verified from the source "
        "text; anything else is rejected."
    )


def _unverified_reexport_message(module: str, name: str) -> str:
    return (
        "imports '" + name + "' from '" + module + "'. '" + name + "' "
        "is the name of a module, and the source of '" + module + "' "
        "is not part of this scan, so the import would hand over a "
        "whole module this audit never cleared. Import what you need "
        "directly so the allowlist can check it."
    )


def _attr_component_message(name: str, dotted: "str | None") -> "str | None":
    """Message for one attribute name in a chain, or None if it is fine."""
    if name in _ENTRY_POINT_TOKENS:
        return (
            "refers to '" + name + "'. Package entry points can "
            "load arbitrary code from any installed package "
            "(EntryPoint.load is a dynamic loader), so any "
            "reference is banned."
        )
    if name == "import_module":
        return (
            "calls or references importlib.import_module, which "
            "loads a module chosen while the program runs; this "
            "audit cannot see what it would load. Use a plain "
            "import statement from the allowlist instead."
        )
    if _is_dunder(name):
        return (
            "reads the double-underscore attribute '" + name + "'. "
            "These attributes expose Python's internal machinery "
            "(module tables, code objects, global state) and can "
            "reach code this audit cannot see; they are banned in "
            "synthtwin source."
        )
    if name == "load" and dotted != "json.load":
        return (
            "reads an attribute named 'load'. Only json.load is "
            "recognized; on anything else, 'load' can be a dynamic "
            "code loader (EntryPoint.load), so the audit rejects "
            "it."
        )
    return None


class _Checker(ast.NodeVisitor):
    """Walks one module and records policy violations."""

    def __init__(
        self,
        module_exports: "dict[str, tuple[set[str], set[str]]] | None" = None,
        first_party_modules: "set[str] | None" = None,
    ) -> None:
        self.violations: list[tuple[int, str]] = []
        # A stack of scopes. Each scope maps a local name to the SET of
        # possible origins it may hold: ("module", dotted),
        # ("api", dotted), ("def", name) for functions and classes
        # defined in the scanned code, ("instance", dotted) for a value
        # returned by a call to an allowlisted API, and the explicit
        # ("unknown", "") member for anything this audit cannot trace.
        # Origins only accumulate -- a later store NEVER erases an
        # earlier origin (union semantics), and the unknown member is
        # never discarded when other origins join the set, so a
        # rebinding hidden behind a branch can neither launder away a
        # module nor make an untraceable callback look safe.
        self.scopes: list[dict[str, set[tuple[str, str]]]] = [{}]
        # Dotted paths known to name modules: the fixed allowlist plus
        # every intra-package path seen in this file's import
        # statements. The one-attribute-step rule counts from the
        # longest prefix found here.
        self.module_paths: set[str] = set(_KNOWN_MODULE_PATHS)
        # Per-module export records for every first-party module in the
        # scanned tree: module name -> (defined names, imported names).
        # First-party `from` imports and one-step attribute references
        # are verified against these records.
        self.module_exports = module_exports if module_exports is not None else {}
        self.first_party_modules = (
            set(first_party_modules) if first_party_modules is not None else set()
        )

    # -- bookkeeping -------------------------------------------------

    def _flag(self, node: ast.AST, message: str) -> None:
        self.violations.append((getattr(node, "lineno", 1), message))

    def _bind(self, name: str, value: "tuple[str, str] | None") -> None:
        slot = self.scopes[-1].setdefault(name, set())
        slot.add(value if value is not None else _UNKNOWN)

    def _lookup(self, name: str) -> "set[tuple[str, str]] | None":
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def _register_module_path(self, dotted: str) -> None:
        parts = dotted.split(".")
        for length in range(1, len(parts) + 1):
            self.module_paths.add(".".join(parts[:length]))

    def _module_prefix(self, dotted: str) -> "tuple[str | None, list[str]]":
        """Split dotted into (longest known module path, remaining parts)."""
        parts = dotted.split(".")
        for length in range(len(parts), 0, -1):
            prefix = ".".join(parts[:length])
            if prefix in self.module_paths:
                return prefix, parts[length:]
        return None, parts

    def _resolve(self, parts: "list[str]") -> "list[str]":
        """Turn a Name/Attribute chain into its possible dotted origins,
        tracing aliases back to the imports or builtins they came from.
        Yields only module/api-rooted dotted candidates; def, instance,
        and unknown possibilities carry no dotted path and are handled
        by the origin-set logic in _value_origins."""
        root = parts[0]
        bound = self._lookup(root)
        rest = parts[1:]
        if bound is None:
            if root in _BANNED_BUILTINS:
                return [".".join(["builtins." + root] + rest)]
            return []
        out = []
        for kind, origin in sorted(bound):
            if kind in ("module", "api"):
                out.append(".".join([origin] + rest))
        return out

    def _value_origins(self, value: ast.AST) -> "set[tuple[str, str]]":
        """The possible origins of an expression's VALUE.

        Every possibility this audit cannot pin down contributes the
        explicit unknown member; other origins never displace it.
        """
        if isinstance(value, (ast.Name, ast.Attribute)):
            parts = _chain_parts(value)
            if parts is None:
                return {_UNKNOWN}
            root, rest = parts[0], parts[1:]
            bound = self._lookup(root)
            if bound is None:
                if root in _BANNED_BUILTINS:
                    return {("api", ".".join(["builtins." + root] + rest))}
                return {_UNKNOWN}
            out: set[tuple[str, str]] = set()
            for kind, origin in bound:
                if kind in ("module", "api"):
                    if rest:
                        out.add(("api", ".".join([origin] + rest)))
                    else:
                        out.add((kind, origin))
                elif rest:
                    # An attribute read on a def, instance, or unknown
                    # value produces a value this audit cannot trace.
                    out.add(_UNKNOWN)
                else:
                    out.add((kind, origin))
            return out or {_UNKNOWN}
        if isinstance(value, ast.Call):
            return self._call_result_origins(value)
        if isinstance(value, ast.BinOp):
            merged = self._value_origins(value.left) | self._value_origins(
                value.right
            )
            instances = {origin for origin in merged if origin[0] == "instance"}
            # An operator on an api-instance runs the API class's own
            # operator method; the result is a value that allowlisted
            # code produced (policy case (b) in the module docstring).
            return instances or {_UNKNOWN}
        if isinstance(value, ast.IfExp):
            return self._value_origins(value.body) | self._value_origins(
                value.orelse
            )
        if isinstance(value, ast.BoolOp):
            out = set()
            for operand in value.values:
                out |= self._value_origins(operand)
            return out or {_UNKNOWN}
        return {_UNKNOWN}

    def _call_result_origins(self, call: ast.Call) -> "set[tuple[str, str]]":
        """Origins of a call expression's result.

        A call to an API that the allowlist accepts yields an
        api-instance (policy case (b)); every other call yields the
        unknown member.
        """
        func = call.func
        if not isinstance(func, (ast.Name, ast.Attribute)):
            return {_UNKNOWN}
        parts = _chain_parts(func)
        if parts is None:
            return {_UNKNOWN}
        out: set[tuple[str, str]] = set()
        for dotted in self._resolve(parts):
            if (
                dotted.partition(".")[0] != "builtins"
                and self._policy_for(dotted, False) is None
            ):
                out.add(("instance", dotted))
            else:
                out.add(_UNKNOWN)
        bound = self._lookup(parts[0])
        if bound is None:
            if parts[0] not in _BANNED_BUILTINS:
                out.add(_UNKNOWN)
        else:
            for kind, _origin in bound:
                if kind not in ("module", "api"):
                    out.add(_UNKNOWN)
        return out or {_UNKNOWN}

    def _bind_from_value(self, name: str, value: ast.AST) -> None:
        for kind, origin in self._value_origins(value):
            if kind == "api" and origin in self.module_paths:
                self._bind(name, ("module", origin))
            else:
                self._bind(name, (kind, origin))

    def _collect_scope_bindings(self, body: "list[ast.stmt]") -> None:
        """Pre-bind everything this scope binds anywhere in its body.

        Flow-insensitive on purpose: an import or a def/class statement
        anywhere in a scope -- inside any branch, loop, or try block --
        is visible to the whole scope before the statements are walked,
        and later stores never erase it. Nested function, class, and
        lambda bodies are separate scopes and are not entered here.
        """
        stack = list(body)
        while stack:
            node = stack.pop()
            if isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            ):
                self._bind(node.name, ("def", node.name))
                continue
            if isinstance(node, ast.Lambda):
                continue
            if isinstance(node, ast.Import):
                self._handle_import(node, report=False)
            elif isinstance(node, ast.ImportFrom):
                self._handle_import_from(node, report=False)
            else:
                stack.extend(ast.iter_child_nodes(node))

    # -- the positive policy -----------------------------------------

    def _policy_for(self, dotted: str, is_store: bool) -> "str | None":
        """Check a fully resolved dotted path against the D6.2 allowlist.

        Returns an explanation string when the path violates the policy,
        None when it is allowed.
        """
        top = dotted.partition(".")[0]

        if top in _FORBIDDEN_MODULES:
            return _forbidden_module_message(top, "uses " + repr(dotted) + " from")

        if top == "builtins":
            name = dotted.split(".")[1]
            return _primitive_message(name) + " (reached through an alias)"

        if is_store and "." in dotted:
            return (
                "writes to '" + dotted + "', an attribute of an imported "
                "module. Module state must stay exactly as Python ships it; "
                "changing it can change what code runs later. Remove the "
                "write."
            )

        prefix, rest = self._module_prefix(dotted)
        if prefix is None:
            return (
                "uses '" + dotted + "', which does not resolve to any "
                "allowlisted API. " + _ALLOWLIST_NOTE
            )
        if not rest:
            return None

        if top == "sys":
            for banned in _SYS_BANNED:
                if dotted == banned or dotted.startswith(banned + "."):
                    return (
                        "touches '" + dotted + "', part of Python's import "
                        "machinery. Reading or changing it can smuggle in "
                        "code this offline audit never sees; it is banned "
                        "in synthtwin source."
                    )

        if prefix == "os":
            if rest[0] == "environ":
                if len(rest) == 1:
                    return None
                if len(rest) == 2 and rest[1] in _ENV_READ_METHODS:
                    return None
                return (
                    "changes or misuses os.environ ('" + dotted + "'). The "
                    "allowlist permits reading environment variables only; "
                    "remove the write."
                )
            if rest[0] in {"system", "popen", "fork", "posix_spawn"} or rest[
                0
            ].startswith(("exec", "spawn")):
                return (
                    "uses '" + dotted + "', which can start or replace "
                    "programs on this computer. synthtwin promises never to "
                    "do that; remove it."
                )

        for part in rest:
            if part in _MODULE_ATTR_BLOCK:
                return _module_hop_message(dotted, part)
            if part.startswith("_"):
                return _private_hop_message(dotted, part)

        if len(rest) > 1:
            return _deep_chain_message(dotted, prefix)

        if prefix in self.module_exports:
            defined, imported_names = self.module_exports[prefix]
            if rest[0] in imported_names:
                return _reexport_message(prefix, rest[0])
            if rest[0] not in defined:
                return _undefined_export_message(prefix, rest[0])

        if prefix == "os":
            if dotted in _OS_ALLOWED_EXACT:
                return None
            return (
                "uses '" + dotted + "'. From the os module only the os.path "
                "functions, os.fspath, os.getcwd, os.lstat, and reading "
                "os.environ are allowed."
            )

        if prefix in ("importlib", "importlib.metadata"):
            if dotted == "importlib.metadata.version":
                return None
            return (
                "uses '" + dotted + "'. From importlib only "
                "importlib.metadata.version() is allowed (it reads the "
                "installed version string); everything else can load code "
                "chosen while the program runs."
            )

        return None

    # -- shared identifier checks ------------------------------------

    def _check_name(self, node: ast.AST, name: str) -> None:
        if name in _BANNED_BUILTINS:
            self._flag(node, _primitive_message(name))
        elif name in _FORBIDDEN_MODULES:
            self._flag(node, _forbidden_module_message(name, "refers to"))
        elif name in _ENTRY_POINT_TOKENS:
            self._flag(
                node,
                "refers to '" + name + "'. Package entry points can "
                "load arbitrary code from any installed package "
                "(EntryPoint.load is a dynamic loader), so any "
                "reference is banned.",
            )
        elif _is_dunder(name) and name not in _ALLOWED_DUNDER_NAMES:
            self._flag(
                node,
                "uses the double-underscore name '" + name + "'. These "
                "names expose Python's internal machinery; only "
                "__name__, __doc__, __file__, __version__ and __all__ "
                "are allowed in synthtwin source.",
            )

    def _check_attr_component(
        self, node: ast.AST, name: str, dotted: "str | None"
    ) -> bool:
        """Check one attribute name in a chain. Returns True if it was
        flagged."""
        message = _attr_component_message(name, dotted)
        if message is not None:
            self._flag(node, message)
            return True
        return False

    # -- imports -----------------------------------------------------

    def visit_Import(self, node: ast.Import) -> None:
        self._handle_import(node, report=True)

    def _handle_import(self, node: ast.Import, report: bool) -> None:
        for alias in node.names:
            name = alias.name
            top = name.partition(".")[0]
            bound_name = alias.asname or top
            origin = name if alias.asname else top

            if top == _FIRST_PARTY_ROOT:
                self._register_module_path(name)
                self._bind(bound_name, ("module", origin))
                continue
            if name in {"argparse", "dataclasses", "json", "pathlib",
                        "typing", "sys", "os"}:
                self._bind(bound_name, ("module", name))
                continue
            if name in {"os.path", "importlib.metadata"}:
                self._bind(bound_name, ("module", origin))
                continue
            if top in _UNRESTRICTED_MODULES:
                self._bind(bound_name, ("module", origin))
                continue

            # Not allowed. Bind anyway so later uses are reported too.
            self._bind(bound_name, ("module", origin))
            if not report:
                continue
            if top in _FORBIDDEN_MODULES:
                self._flag(node, _forbidden_module_message(top, "imports"))
            elif top == "importlib":
                self._flag(
                    node,
                    "imports '" + name + "'. Only 'import "
                    "importlib.metadata' is allowed, and from it only "
                    "the version() function may be used.",
                )
            elif top == "os":
                self._flag(
                    node,
                    "imports '" + name + "'. From os only 'import os' "
                    "or 'import os.path' is allowed. " + _ALLOWLIST_NOTE,
                )
            else:
                self._flag(
                    node,
                    "imports '" + name + "', which is not on the "
                    "Phase 0 allowlist. " + _ALLOWLIST_NOTE,
                )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self._handle_import_from(node, report=True)

    def _handle_import_from(self, node: ast.ImportFrom, report: bool) -> None:
        if node.level and node.level > 0:
            base = _FIRST_PARTY_ROOT
            if node.module:
                base = base + "." + node.module
            self._register_module_path(base)
            for alias in node.names:
                if alias.name == "*":
                    if report:
                        self._flag_star(node, base)
                    continue
                self._first_party_from_alias(node, base, alias, report)
            return

        module = node.module or ""
        top = module.partition(".")[0]

        if top == _FIRST_PARTY_ROOT:
            self._register_module_path(module)
            for alias in node.names:
                if alias.name == "*":
                    if report:
                        self._flag_star(node, module)
                    continue
                self._first_party_from_alias(node, module, alias, report)
            return

        for alias in node.names:
            if alias.name == "*":
                if report:
                    self._flag_star(node, module)
                continue
            dotted = module + "." + alias.name
            problem = _attr_component_message(alias.name, dotted)
            if problem is not None:
                if report:
                    self._flag(node, problem)
                continue
            message = self._policy_for(dotted, False)
            if message is not None:
                if report:
                    self._flag(node, message)
                continue
            kind = "module" if dotted in self.module_paths else "api"
            self._bind(alias.asname or alias.name, (kind, dotted))

    def _first_party_from_alias(
        self, node: ast.ImportFrom, module: str, alias: ast.alias, report: bool
    ) -> None:
        """Handle one name in a first-party `from` import.

        The name must be a submodule of the scanned tree or a name the
        sibling module genuinely defines. A name the sibling itself
        imported is rejected: importing it would launder the sibling's
        own imports past this audit (plan D6.2).
        """
        bound_name = alias.asname or alias.name
        dotted = module + "." + alias.name

        if dotted in self.first_party_modules:
            self._register_module_path(dotted)
            self._bind(bound_name, ("module", dotted))
            return

        exports = self.module_exports.get(module)
        if exports is not None:
            defined, imported_names = exports
            if alias.name in defined:
                self._bind(bound_name, ("api", dotted))
                return
            if report:
                if alias.name in imported_names:
                    self._flag(node, _reexport_message(module, alias.name))
                else:
                    self._flag(node, _undefined_export_message(module, alias.name))
            self._bind(bound_name, ("api", dotted))
            return

        # The sibling module's source is not part of this scan, so its
        # exports cannot be verified. A name that matches a known
        # module name would hand over a whole module; reject it.
        if alias.name in _MODULE_ATTR_BLOCK:
            if report:
                self._flag(node, _unverified_reexport_message(module, alias.name))
            self._bind(bound_name, ("api", dotted))
            return

        # The alias may itself be a module; register it so the
        # one-step rule counts from it, not through it.
        self._register_module_path(dotted)
        self._bind(bound_name, ("module", dotted))

    def _flag_star(self, node: ast.AST, module: str) -> None:
        self._flag(
            node,
            "uses 'from " + module + " import *', which creates names "
            "this audit cannot enumerate. Import each name explicitly.",
        )

    # -- expressions -------------------------------------------------

    def visit_Name(self, node: ast.Name) -> None:
        self._check_name(node, node.id)
        if isinstance(node.ctx, ast.Load):
            bound = self._lookup(node.id)
            if bound:
                seen: set[str] = set()
                for kind, origin in sorted(bound):
                    if kind in ("def", "instance", "unknown"):
                        # Reading a scanned definition, an api-instance,
                        # or an untraced value is fine; only CALLS
                        # through them are restricted.
                        continue
                    if kind == "module" and not origin.startswith(
                        _FIRST_PARTY_ROOT
                    ):
                        message: str | None = _bare_module_message(origin)
                    else:
                        message = self._policy_for(origin, False)
                    if message is not None and message not in seen:
                        seen.add(message)
                        self._flag(node, message)
        elif isinstance(node.ctx, (ast.Store, ast.Del)):
            # Record that the name is bound to something untraced here.
            # Every origin the name already had is kept: a store on one
            # path never proves the old value is gone on another path,
            # and the unknown member this store adds is never discarded.
            self._bind(node.id, None)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        parts = _chain_parts(node)
        if parts is None:
            # Attribute on a computed value (call result, subscript,
            # literal): only the attribute-name bans apply to the READ;
            # calling the attribute is checked in visit_Call.
            self._check_attr_component(node, node.attr, None)
            self.generic_visit(node)
            return

        candidates = self._resolve(parts)
        primary = candidates[0] if len(candidates) == 1 else None
        flagged = False
        for part in parts[1:]:
            if self._check_attr_component(node, part, primary):
                flagged = True
        if flagged:
            return
        if not candidates:
            self._check_name(node, parts[0])
            return
        is_store = isinstance(node.ctx, (ast.Store, ast.Del))
        seen: set[str] = set()
        for dotted in candidates:
            message = self._policy_for(dotted, is_store)
            if message is None and not is_store and dotted in self.module_paths:
                # The chain resolves to a module object used as a plain
                # value (for example passing os.path into a function).
                message = _bare_module_message(dotted)
            if message is not None and message not in seen:
                seen.add(message)
                self._flag(node, message)
        # A pure chain has no other children worth visiting; skipping
        # them avoids reporting the same chain twice.

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, (ast.Subscript, ast.Call)):
            self._flag(
                node,
                "calls a target that is computed while the program "
                "runs (the result of a lookup or of another call), so "
                "this audit cannot tell what would run. Call the "
                "function by its direct dotted name.",
            )
        elif isinstance(node.func, ast.Name):
            self._check_call_target(node, node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self._check_method_call(node)
        self._check_callable_arguments(node)
        self.generic_visit(node)

    def _check_call_target(self, node: ast.Call, name: str) -> None:
        """Reject a bare-name call unless EVERY possible origin of the
        name is something this audit can check (plan D6.2: callback
        parameters are banned in Phase 0 source). The unknown member is
        never discarded, so a name that might still hold an untraced
        value is rejected even when another branch rebound it to an
        allowed API. Traced origins are checked where the name is read.
        """
        bound = self._lookup(name)
        if bound is None:
            if (
                name in _ALLOWED_CALL_BUILTINS
                or name in _BANNED_BUILTINS
                or name in _FORBIDDEN_MODULES
                or name in _ENTRY_POINT_TOKENS
                or _is_dunder(name)
            ):
                # Either an accepted builtin, or already flagged by the
                # name checks that run on the same node.
                return
            self._flag(node, _unknown_call_message(name))
            return
        for kind, _origin in bound:
            if kind not in ("def", "module", "api"):
                self._flag(node, _unknown_call_message(name))
                return

    def _check_method_call(self, node: ast.Call) -> None:
        """Apply the two-case method-call policy from the module
        docstring: api-instances accept any method; untraced values
        accept only the fixed data-method list; module/api-rooted
        chains are checked by the dotted-path policy in
        visit_Attribute."""
        func = node.func
        if not isinstance(func, ast.Attribute):
            return
        method = func.attr
        for kind, _origin in sorted(self._value_origins(func.value)):
            if kind in ("module", "api", "instance"):
                continue
            if method in _UNKNOWN_VALUE_METHODS:
                continue
            self._flag(node, _unknown_method_message(method))
            return

    def _callee_is_first_party(self, func: ast.AST) -> bool:
        """True when every possible call target is defined in the
        scanned tree (a scanned def/class or a first-party module
        member)."""
        if isinstance(func, ast.Name):
            bound = self._lookup(func.id)
            if not bound:
                return False
            for kind, origin in bound:
                if kind == "def":
                    continue
                if kind in ("module", "api") and (
                    origin == _FIRST_PARTY_ROOT
                    or origin.startswith(_FIRST_PARTY_ROOT + ".")
                ):
                    continue
                return False
            return True
        if isinstance(func, ast.Attribute):
            parts = _chain_parts(func)
            if parts is None:
                return False
            candidates = self._resolve(parts)
            if not candidates:
                return False
            for dotted in candidates:
                if dotted != _FIRST_PARTY_ROOT and not dotted.startswith(
                    _FIRST_PARTY_ROOT + "."
                ):
                    return False
            return True
        return False

    def _check_callable_arguments(self, node: ast.Call) -> None:
        """Reject a function or lambda passed as an argument to a
        callee that is not defined in the scanned tree. Outside code
        could keep the callable and run it at any time; a scanned
        callee is fine because every call site inside it is scanned
        under the same rules."""
        if self._callee_is_first_party(node.func):
            return
        values = list(node.args) + [keyword.value for keyword in node.keywords]
        for value in values:
            inner = value.value if isinstance(value, ast.Starred) else value
            if isinstance(inner, ast.Lambda):
                self._flag(node, _callable_argument_message("a lambda function"))
            elif isinstance(inner, ast.Name):
                bound = self._lookup(inner.id)
                if bound and any(kind == "def" for kind, _origin in bound):
                    self._flag(
                        node,
                        _callable_argument_message(
                            "the function '" + inner.id + "'"
                        ),
                    )

    def visit_Subscript(self, node: ast.Subscript) -> None:
        parts = _chain_parts(node.value)
        candidates = self._resolve(parts) if parts else []
        if "os.environ" in candidates and isinstance(
            node.ctx, (ast.Store, ast.Del)
        ):
            self._flag(
                node,
                "changes os.environ. The allowlist permits reading "
                "environment variables only; remove the write.",
            )
        self.generic_visit(node)

    # -- statements that bind names ----------------------------------

    def visit_Assign(self, node: ast.Assign) -> None:
        self.visit(node.value)
        for target in node.targets:
            if isinstance(target, ast.Name):
                self._check_name(target, target.id)
                self._bind_from_value(target.id, node.value)
            else:
                self.visit(target)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self.visit(node.annotation)
        if node.value is not None:
            self.visit(node.value)
        if isinstance(node.target, ast.Name):
            self._check_name(node.target, node.target.id)
            if node.value is not None:
                self._bind_from_value(node.target.id, node.value)
            else:
                self._bind(node.target.id, None)
        else:
            self.visit(node.target)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self.visit(node.value)
        self.visit(node.target)

    # -- scopes ------------------------------------------------------

    def visit_Module(self, node: ast.Module) -> None:
        self._collect_scope_bindings(node.body)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._handle_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._handle_function(node)

    def _handle_function(self, node: "ast.FunctionDef | ast.AsyncFunctionDef") -> None:
        self._check_name(node, node.name)
        for decorator in node.decorator_list:
            self.visit(decorator)
        args = node.args
        for default in list(args.defaults) + [
            d for d in args.kw_defaults if d is not None
        ]:
            self.visit(default)
        all_args = list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
        if args.vararg is not None:
            all_args.append(args.vararg)
        if args.kwarg is not None:
            all_args.append(args.kwarg)
        for arg in all_args:
            if arg.annotation is not None:
                self.visit(arg.annotation)
        if node.returns is not None:
            self.visit(node.returns)
        self._bind(node.name, ("def", node.name))
        # Parameters hold caller-supplied values: the explicit unknown
        # member, never discarded when other origins join.
        self.scopes.append({arg.arg: {_UNKNOWN} for arg in all_args})
        self._collect_scope_bindings(node.body)
        for statement in node.body:
            self.visit(statement)
        self.scopes.pop()

    def visit_Lambda(self, node: ast.Lambda) -> None:
        args = node.args
        for default in list(args.defaults) + [
            d for d in args.kw_defaults if d is not None
        ]:
            self.visit(default)
        all_args = list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
        if args.vararg is not None:
            all_args.append(args.vararg)
        if args.kwarg is not None:
            all_args.append(args.kwarg)
        self.scopes.append({arg.arg: {_UNKNOWN} for arg in all_args})
        self.visit(node.body)
        self.scopes.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._check_name(node, node.name)
        for decorator in node.decorator_list:
            self.visit(decorator)
        for base in node.bases:
            self.visit(base)
        for keyword in node.keywords:
            self.visit(keyword.value)
        self._bind(node.name, ("def", node.name))
        self.scopes.append({})
        self._collect_scope_bindings(node.body)
        for statement in node.body:
            self.visit(statement)
        self.scopes.pop()


def scan_source(
    source_text: str,
    module_exports: "dict[str, tuple[set[str], set[str]]] | None" = None,
    first_party_modules: "set[str] | None" = None,
) -> "list[tuple[int, str]]":
    """Scan one module's source text. Returns (line, message) pairs.

    ``module_exports`` and ``first_party_modules`` carry the per-module
    export records for the surrounding scanned tree (see scan_files);
    without them, first-party `from` imports fall back to rejecting
    known module names only.
    """
    try:
        tree = ast.parse(source_text)
    except SyntaxError as error:
        line = error.lineno if error.lineno else 1
        detail = error.msg if error.msg else "invalid syntax"
        return [
            (
                line,
                "could not be parsed as Python (" + detail + "). Fix "
                "the syntax so the file can be audited.",
            )
        ]
    checker = _Checker(module_exports, first_party_modules)
    checker.visit(tree)
    return sorted(checker.violations)


def _python_files(root: pathlib.Path) -> "list[pathlib.Path]":
    if root.is_file():
        return [root]
    return sorted(root.rglob("*.py"))


def scan_files(files: "list[pathlib.Path]") -> "list[str]":
    """Scan the given files. Returns formatted 'file:line: message'
    violation lines (empty list = clean).

    Before any file is judged, every first-party module in the batch is
    parsed and its top-level names are recorded, so that first-party
    `from` imports and one-step attribute references can be verified
    against what the named sibling module really defines.
    """
    lines: list[str] = []
    texts: dict[pathlib.Path, str] = {}
    module_exports: dict[str, tuple[set[str], set[str]]] = {}
    first_party_modules: set[str] = set()
    for path in files:
        try:
            texts[path] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            lines.append(
                str(path) + ":1: could not be decoded as UTF-8 text. "
                "Source files must be plain UTF-8; re-save the file "
                "with UTF-8 encoding."
            )
            continue
        module_name = _first_party_module_name(path)
        if module_name is None:
            continue
        try:
            tree = ast.parse(texts[path])
        except SyntaxError:
            # scan_source reports the parse failure for this file below.
            continue
        module_exports[module_name] = _module_bindings(tree)
        pieces = module_name.split(".")
        for length in range(1, len(pieces) + 1):
            first_party_modules.add(".".join(pieces[:length]))
    for path in files:
        if path not in texts:
            continue
        for lineno, message in scan_source(
            texts[path], module_exports, first_party_modules
        ):
            lines.append(str(path) + ":" + str(lineno) + ": " + message)
    return lines


def scan_tree(root: "pathlib.Path | str") -> "list[str]":
    """Scan every .py file under root (or a single .py file)."""
    return scan_files(_python_files(pathlib.Path(root)))


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(
        prog="scan_imports",
        description=(
            "Check a Python source tree against synthtwin's offline "
            "allowlist (plan D6.2) without running any of it. Prints "
            "one line per violation and exits 1 if any were found, 0 "
            "when the tree is clean."
        ),
    )
    parser.add_argument(
        "source",
        help=(
            "folder that holds the Python source to audit (for "
            "synthtwin CI this is src/), or a single .py file"
        ),
    )
    args = parser.parse_args(argv)

    root = pathlib.Path(args.source)
    if not root.exists():
        parser.error(
            "the path '" + args.source + "' does not exist. Give the "
            "folder that holds the Python source to audit, for "
            "example src/."
        )
    files = _python_files(root)
    if not files:
        parser.error(
            "no Python files were found under '" + args.source + "'. "
            "Check that you gave the right folder; an empty scan "
            "proves nothing."
        )

    violations = scan_files(files)
    for line in violations:
        print(line)
    print(
        "scan_imports: checked "
        + str(len(files))
        + " Python file(s) under '"
        + str(root)
        + "': "
        + str(len(violations))
        + " violation(s)."
    )
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
