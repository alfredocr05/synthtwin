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
* Every attribute access or call that starts from an imported module
  must resolve, in the source text alone, to an API named above.
  Targets put together while the program runs (double-underscore
  internals, lookups through the module table, subscripted call
  targets, star imports, bare module objects passed around as values)
  are rejected, because this audit cannot see what they would reach.

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
# direct dotted access are rejected.
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


def _policy_for(dotted: str, is_store: bool) -> "str | None":
    """Check a fully resolved dotted path against the D6.2 allowlist.

    Returns an explanation string when the path violates the policy,
    None when it is allowed.
    """
    top = dotted.partition(".")[0]

    if top == _FIRST_PARTY_ROOT:
        return None

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

    if top in _UNRESTRICTED_MODULES:
        return None

    if top == "sys":
        if dotted == "sys":
            return None
        for banned in _SYS_BANNED:
            if dotted == banned or dotted.startswith(banned + "."):
                return (
                    "touches '" + dotted + "', part of Python's import "
                    "machinery. Reading or changing it can smuggle in "
                    "code this offline audit never sees; it is banned "
                    "in synthtwin source."
                )
        return None

    if top == "os":
        if dotted == "os":
            return None
        if dotted == "os.path" or dotted.startswith("os.path."):
            return None
        if dotted in _OS_ALLOWED_EXACT:
            return None
        if dotted == "os.environ":
            return None
        if dotted.startswith("os.environ."):
            method = dotted[len("os.environ."):]
            if method in _ENV_READ_METHODS:
                return None
            return (
                "changes or misuses os.environ ('" + dotted + "'). The "
                "allowlist permits reading environment variables only; "
                "remove the write."
            )
        attr = dotted.split(".")[1]
        if attr in {"system", "popen", "fork", "posix_spawn"} or attr.startswith(
            ("exec", "spawn")
        ):
            return (
                "uses '" + dotted + "', which can start or replace "
                "programs on this computer. synthtwin promises never to "
                "do that; remove it."
            )
        return (
            "uses '" + dotted + "'. From the os module only the os.path "
            "functions, os.fspath, os.getcwd, os.lstat, and reading "
            "os.environ are allowed."
        )

    if top == "importlib":
        if dotted in {"importlib", "importlib.metadata", "importlib.metadata.version"}:
            return None
        return (
            "uses '" + dotted + "'. From importlib only "
            "importlib.metadata.version() is allowed (it reads the "
            "installed version string); everything else can load code "
            "chosen while the program runs."
        )

    return (
        "uses '" + dotted + "', which does not resolve to any "
        "allowlisted API. " + _ALLOWLIST_NOTE
    )


class _Checker(ast.NodeVisitor):
    """Walks one module and records policy violations."""

    def __init__(self) -> None:
        self.violations: list[tuple[int, str]] = []
        # A stack of scopes. Each scope maps a local name either to
        # ("module" | "api", dotted-origin) or to None (bound, origin
        # unknown -- shadows any outer binding).
        self.scopes: list[dict] = [{}]

    # -- bookkeeping -------------------------------------------------

    def _flag(self, node: ast.AST, message: str) -> None:
        self.violations.append((getattr(node, "lineno", 1), message))

    def _bind(self, name: str, value: "tuple[str, str] | None") -> None:
        self.scopes[-1][name] = value

    def _lookup(self, name: str) -> "tuple[str, str] | None":
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def _resolve(self, parts: "list[str]") -> "str | None":
        """Turn a Name/Attribute chain into its dotted origin, tracing
        aliases back to the import or builtin they came from."""
        root = parts[0]
        bound = self._lookup(root)
        if bound is not None:
            return ".".join([bound[1]] + parts[1:])
        if root in _BANNED_BUILTINS:
            return ".".join(["builtins." + root] + parts[1:])
        return None

    def _bind_from_value(self, name: str, value: ast.AST) -> None:
        parts = _chain_parts(value)
        dotted = self._resolve(parts) if parts else None
        if dotted is None:
            self._bind(name, None)
            return
        top = dotted.partition(".")[0]
        if dotted in _KNOWN_MODULE_PATHS or top == _FIRST_PARTY_ROOT:
            self._bind(name, ("module", dotted))
        else:
            self._bind(name, ("api", dotted))

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
        if name in _ENTRY_POINT_TOKENS:
            self._flag(
                node,
                "refers to '" + name + "'. Package entry points can "
                "load arbitrary code from any installed package "
                "(EntryPoint.load is a dynamic loader), so any "
                "reference is banned.",
            )
            return True
        if name == "import_module":
            self._flag(
                node,
                "calls or references importlib.import_module, which "
                "loads a module chosen while the program runs; this "
                "audit cannot see what it would load. Use a plain "
                "import statement from the allowlist instead.",
            )
            return True
        if _is_dunder(name):
            self._flag(
                node,
                "reads the double-underscore attribute '" + name + "'. "
                "These attributes expose Python's internal machinery "
                "(module tables, code objects, global state) and can "
                "reach code this audit cannot see; they are banned in "
                "synthtwin source.",
            )
            return True
        if name == "load" and dotted != "json.load":
            self._flag(
                node,
                "reads an attribute named 'load'. Only json.load is "
                "recognized; on anything else, 'load' can be a dynamic "
                "code loader (EntryPoint.load), so the audit rejects "
                "it.",
            )
            return True
        return False

    # -- imports -----------------------------------------------------

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            name = alias.name
            top = name.partition(".")[0]
            bound_name = alias.asname or top
            origin = name if alias.asname else top

            if top == _FIRST_PARTY_ROOT:
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
        if node.level and node.level > 0:
            base = _FIRST_PARTY_ROOT
            if node.module:
                base = base + "." + node.module
            for alias in node.names:
                if alias.name == "*":
                    self._flag_star(node, base)
                    continue
                self._bind(
                    alias.asname or alias.name,
                    ("module", base + "." + alias.name),
                )
            return

        module = node.module or ""
        top = module.partition(".")[0]

        if top == _FIRST_PARTY_ROOT:
            for alias in node.names:
                if alias.name == "*":
                    self._flag_star(node, module)
                    continue
                self._bind(
                    alias.asname or alias.name,
                    ("module", module + "." + alias.name),
                )
            return

        for alias in node.names:
            if alias.name == "*":
                self._flag_star(node, module)
                continue
            dotted = module + "." + alias.name
            if self._check_attr_component(node, alias.name, dotted):
                continue
            message = _policy_for(dotted, False)
            if message is not None:
                self._flag(node, message)
                continue
            kind = "module" if dotted in _KNOWN_MODULE_PATHS else "api"
            self._bind(alias.asname or alias.name, (kind, dotted))

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
            if bound is not None:
                kind, origin = bound
                if kind == "module" and not origin.startswith(_FIRST_PARTY_ROOT):
                    self._flag(
                        node,
                        "refers to the module '" + origin + "' as a "
                        "bare value. Module objects passed through "
                        "variables or containers can hide what gets "
                        "called later; write the full dotted access "
                        "(for example os.path.join) instead.",
                    )
                else:
                    message = _policy_for(origin, False)
                    if message is not None:
                        self._flag(node, message)
        elif isinstance(node.ctx, (ast.Store, ast.Del)):
            # The name is being rebound; forget any module alias it held.
            self.scopes[-1][node.id] = None

    def visit_Attribute(self, node: ast.Attribute) -> None:
        parts = _chain_parts(node)
        if parts is None:
            # Attribute on a computed value (call result, subscript,
            # literal): only the attribute-name bans apply here.
            self._check_attr_component(node, node.attr, None)
            self.generic_visit(node)
            return

        dotted = self._resolve(parts)
        flagged = False
        for part in parts[1:]:
            if self._check_attr_component(node, part, dotted):
                flagged = True
        if flagged:
            return
        if dotted is None:
            self._check_name(node, parts[0])
            return
        is_store = isinstance(node.ctx, (ast.Store, ast.Del))
        message = _policy_for(dotted, is_store)
        if message is not None:
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
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        parts = _chain_parts(node.value)
        dotted = self._resolve(parts) if parts else None
        if dotted == "os.environ" and isinstance(node.ctx, (ast.Store, ast.Del)):
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
            self.visit(target)
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            self._bind_from_value(node.targets[0].id, node.value)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self.visit(node.annotation)
        if node.value is not None:
            self.visit(node.value)
        self.visit(node.target)
        if isinstance(node.target, ast.Name) and node.value is not None:
            self._bind_from_value(node.target.id, node.value)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self.visit(node.value)
        self.visit(node.target)

    # -- scopes ------------------------------------------------------

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
        self._bind(node.name, None)
        self.scopes.append({arg.arg: None for arg in all_args})
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
        self.scopes.append({arg.arg: None for arg in all_args})
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
        self._bind(node.name, None)
        self.scopes.append({})
        for statement in node.body:
            self.visit(statement)
        self.scopes.pop()


def scan_source(source_text: str) -> "list[tuple[int, str]]":
    """Scan one module's source text. Returns (line, message) pairs."""
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
    checker = _Checker()
    checker.visit(tree)
    return sorted(checker.violations)


def _python_files(root: pathlib.Path) -> "list[pathlib.Path]":
    if root.is_file():
        return [root]
    return sorted(root.rglob("*.py"))


def scan_files(files: "list[pathlib.Path]") -> "list[str]":
    """Scan the given files. Returns formatted 'file:line: message'
    violation lines (empty list = clean)."""
    lines: list[str] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            lines.append(
                str(path) + ":1: could not be decoded as UTF-8 text. "
                "Source files must be plain UTF-8; re-save the file "
                "with UTF-8 encoding."
            )
            continue
        for lineno, message in scan_source(text):
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
