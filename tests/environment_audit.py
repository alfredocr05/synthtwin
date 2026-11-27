"""The one environment read the product makes, audited by its structure (batch 4j's records, Codex's review of batch 4i).

Lane CHa's `installation.data_folder` finds the platform's data folder
(contract 4.6b.4) from LOCALAPPDATA or XDG_DATA_HOME, behind the chain's
switch. Two checks hold that no other module reads the environment
(lane POP's `tests/test_table_floor.py`, lane MIN's
`tests/test_floor_is_a_minimum.py`); batch 4i's integration set aside
EVERY node of that function, so a third key, a computed key or the
environment used for anything but the folder escaped both (Codex's
review of batch 4i, its one Medium). `data_folder_set_aside` sets aside
only the one audited read, and only while the function keeps the
audited structure:

- exactly one `os.environ`, copied whole as the stand-in's default in
  one assignment, `where = environ if environ is not None else
  dict(os.environ)`, the one place the parameter `environ` is named;
- the copy `where` read only by a written-out key, LOCALAPPDATA or
  XDG_DATA_HOME, as `where["..."]` or `"..." in where`;
- the function chooses a folder and does nothing else: its statements
  are assignments to plain names, `if`s and returns; it calls only
  `system_name`, `dict`, `os.path.join`, `os.path.expanduser` and
  `pathlib.Path`; every return is a `pathlib.Path(...)`.

- no name the audit trusts is bound to anything else (batch 4k's
  records, Codex's review of batch 4j, its first Medium): `dict`,
  `system_name`, `os` and `pathlib` are bound in `installation.py` only
  by `import os`, `import pathlib` and the one module-level
  `def system_name`, and nothing there stores into `os.*`, `pathlib.*`
  or the built-ins, so `dict(os.environ)` and the four other calls the
  audit allows are the functions their spelling names (`dict = lambda
  source: ...` written before the copy read a third key through it, and
  both checks accepted it).
- nor through another spelling of the same objects (batch 4l's
  records, Codex's review of batch 4k, its one Medium): no module is
  imported as `builtins` or from it, nothing stores into an attribute or
  an item of a name an import binds (`import os as base; base.environ =
  ...`), of the built-ins' holders (`__builtins__["dict"] = ...`) or of a
  computed object, so an alias or a subscript write cannot stand in for
  the rebinding the line above rejects.
- nor through a function's namespace or a name bound to a trusted
  holder (batch 4m's records, Codex's review of batch 4l, its third
  Medium): no attribute of the reflective kind is read anywhere in the
  module (`system_name.__globals__`, `__dict__`, `__builtins__`, a
  frame's `f_globals` and the like), nor fetched by `getattr`, and a
  name assigned a trusted holder, an attribute or an item of one is a
  holder itself (`base = os` then `base.environ = ...`), followed to the
  end, so `base = system_name.__globals__; base["dict"] = ...` is
  rejected twice over.

Any other shape is a finding: the checks fail on it, and the exemption
sets nothing aside.
"""

import ast

AUDITED_NAMES = ("LOCALAPPDATA", "XDG_DATA_HOME")

_CALLED = ("system_name", "dict", "os.path.join", "os.path.expanduser", "pathlib.Path")

# The names those calls are spelled with: each must name what its
# spelling says (batch 4k's records).
_TRUSTED = ("system_name", "dict", "os", "pathlib")
_TRUSTED_IMPORTS = ("os", "os.path", "pathlib")
_BUILTIN_HOLDERS = ("builtins", "__builtins__")
# Attributes that reach a namespace or a code object (batch 4m's records,
# Codex's review of batch 4l): read anywhere in the module, they are a
# finding, as `globals()` and `vars()` already are.
_REFLECTIVE = (
    "__globals__", "__dict__", "__builtins__", "__code__", "__closure__",
    "__defaults__", "__kwdefaults__", "__self__", "__func__", "__module__",
    "__class__", "__subclasses__", "__getattribute__", "__setattr__",
    "__delattr__", "__setitem__", "__delitem__", "f_globals", "f_locals",
    "f_builtins", "f_back", "gi_frame", "cr_frame", "tb_frame",
)


def _dotted(node: ast.expr) -> str:
    """``a.b.c`` written out for a name or a chain of attributes, else the empty text."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        head = _dotted(node.value)
        return f"{head}.{node.attr}" if head else ""
    return ""


def _is_the_copy(node: ast.stmt) -> bool:
    """Is ``node`` exactly `where = environ if environ is not None else dict(os.environ)`?"""
    if not (isinstance(node, ast.Assign) and len(node.targets) == 1):
        return False
    target = node.targets[0]
    value = node.value
    if not (isinstance(target, ast.Name) and target.id == "where" and isinstance(value, ast.IfExp)):
        return False
    test = value.test
    default = value.orelse
    return (
        isinstance(test, ast.Compare)
        and _dotted(test.left) == "environ"
        and len(test.ops) == 1
        and isinstance(test.ops[0], ast.IsNot)
        and len(test.comparators) == 1
        and isinstance(test.comparators[0], ast.Constant)
        and test.comparators[0].value is None
        and _dotted(value.body) == "environ"
        and isinstance(default, ast.Call)
        and _dotted(default.func) == "dict"
        and len(default.args) == 1
        and _dotted(default.args[0]) == "os.environ"
        and not default.keywords
    )


def _audited_key(node: ast.expr) -> bool:
    """Is ``node`` one of the two written-out keys?"""
    return isinstance(node, ast.Constant) and node.value in AUDITED_NAMES


def data_folder_problems(function: ast.FunctionDef) -> "tuple[set[int], list[str]]":
    """The ids of the audited read's nodes in ``function``, and every way it leaves the audited structure."""
    problems: "list[str]" = []
    copies = [one for one in function.body if _is_the_copy(one)]
    if len(copies) != 1:
        problems += [f"data_folder: {len(copies)} copies of the environment, not one"]
    aside: "set[int]" = set()
    for copy in copies:
        aside |= {id(one) for one in ast.walk(copy)}
    # The copy read only by a written-out key.
    allowed_where: "set[int]" = set()
    for node in ast.walk(function):
        if isinstance(node, ast.Subscript) and _dotted(node.value) == "where":
            if _audited_key(node.slice) and isinstance(node.ctx, ast.Load):
                allowed_where |= {id(node.value)}
            else:
                problems += [f"data_folder:{node.lineno}: the copy read by a key not written out"]
        if isinstance(node, ast.Compare) and any(_dotted(one) == "where" for one in node.comparators):
            if (
                _audited_key(node.left)
                and len(node.ops) == 1
                and isinstance(node.ops[0], ast.In)
                and len(node.comparators) == 1
            ):
                allowed_where |= {id(node.comparators[0])}
            else:
                problems += [f"data_folder:{node.lineno}: the copy compared otherwise"]
    for node in ast.walk(function):
        if id(node) in aside:
            continue
        if isinstance(node, ast.Name) and node.id == "where" and id(node) not in allowed_where:
            problems += [f"data_folder:{node.lineno}: the copy used otherwise"]
        if isinstance(node, ast.Name) and node.id in ("environ", "getenv"):
            problems += [f"data_folder:{node.lineno}: {node.id} outside the copy"]
        if isinstance(node, ast.Attribute) and node.attr in ("environ", "getenv", "environb", "getenvb", "putenv"):
            problems += [f"data_folder:{node.lineno}: {node.attr} outside the copy"]
        if isinstance(node, ast.Call) and _dotted(node.func) not in _CALLED:
            problems += [f"data_folder:{node.lineno}: calls {_dotted(node.func) or 'a computed function'}"]
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value.isupper():
            if node.value not in AUDITED_NAMES:
                problems += [f"data_folder:{node.lineno}: names {node.value}"]
    # It chooses a folder and does nothing else.
    statements = function.body
    if statements and isinstance(statements[0], ast.Expr) and isinstance(statements[0].value, ast.Constant):
        statements = statements[1:]
    for statement in statements:
        for node in ast.walk(statement):
            if isinstance(node, ast.stmt) and not isinstance(node, (ast.Assign, ast.If, ast.Return)):
                problems += [f"data_folder:{node.lineno}: a {type(node).__name__} statement"]
            if isinstance(node, ast.Assign) and not all(isinstance(one, ast.Name) for one in node.targets):
                problems += [f"data_folder:{node.lineno}: assigns other than a plain name"]
            if isinstance(node, ast.Return) and not (
                isinstance(node.value, ast.Call) and _dotted(node.value.func) == "pathlib.Path"
            ):
                problems += [f"data_folder:{node.lineno}: returns other than a folder"]
    if not problems:
        return aside, []
    return set(), problems


def _bound_names(node: ast.AST) -> "list[str]":
    """Every plain name ``node`` binds itself (not the names bound inside it)."""
    bound: "list[str]" = []
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        bound += [node.name]
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        bound += [(one.asname or one.name).split(".")[0] for one in node.names]
    if isinstance(node, (ast.Global, ast.Nonlocal)):
        bound += list(node.names)
    if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
        bound += [node.id]
    if isinstance(node, ast.arg):
        bound += [node.arg]
    if isinstance(node, ast.ExceptHandler) and node.name:
        bound += [node.name]
    if isinstance(node, (ast.MatchAs, ast.MatchStar)) and node.name:
        bound += [node.name]
    if isinstance(node, ast.MatchMapping) and node.rest:
        bound += [node.rest]
    return bound


def _rooted_in(node: ast.expr, holders: "set[str]") -> bool:
    """Whether ``node`` names a holder, or an attribute or an item of one, with no call between."""
    if isinstance(node, ast.Name):
        return node.id in holders
    if isinstance(node, (ast.Attribute, ast.Subscript, ast.Starred)):
        return _rooted_in(node.value, holders)
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return any(_rooted_in(one, holders) for one in node.elts)
    # ...and a dictionary's keys and values, and what a comprehension yields (batch 4n's records,
    # Codex's review of batch 4m, its fourth Medium, BATCH 4n OWES 4:
    # `holder = {"one": sys.modules["builtins"]}["one"]` escaped both checks).
    if isinstance(node, ast.Dict):
        return any(_rooted_in(one, holders) for one in [*node.keys, *node.values] if one is not None)
    if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
        return _rooted_in(node.elt, holders)
    if isinstance(node, ast.DictComp):
        return _rooted_in(node.key, holders) or _rooted_in(node.value, holders)
    if isinstance(node, ast.IfExp):
        return _rooted_in(node.body, holders) or _rooted_in(node.orelse, holders)
    if isinstance(node, ast.BoolOp):
        return any(_rooted_in(one, holders) for one in node.values)
    if isinstance(node, ast.NamedExpr):
        return _rooted_in(node.value, holders)
    return False


def _aliases_of(tree: ast.Module, holders: "set[str]") -> "set[str]":
    """Every name bound to a holder, an attribute or an item of one, followed until no name is added."""
    grown = set(holders)
    while True:
        before = len(grown)
        for node in ast.walk(tree):
            targets: "list[ast.expr]" = []
            value: "ast.expr | None" = None
            if isinstance(node, ast.Assign):
                targets, value = list(node.targets), node.value
            elif isinstance(node, (ast.AnnAssign, ast.AugAssign)) and node.value is not None:
                targets, value = [node.target], node.value
            elif isinstance(node, ast.NamedExpr):
                targets, value = [node.target], node.value
            elif isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)):
                targets, value = [node.target], node.iter
            elif isinstance(node, ast.withitem) and node.optional_vars is not None:
                targets, value = [node.optional_vars], node.context_expr
            if value is None or not _rooted_in(value, grown):
                continue
            for target in targets:
                for one in ast.walk(target):
                    if isinstance(one, ast.Name):
                        grown |= {one.id}
        if len(grown) == before:
            return grown


def trusted_names_rebound(tree: ast.Module) -> "list[str]":
    """Every way ``tree`` binds a name the audit trusts to something else, or stores into the modules it trusts."""
    problems: "list[str]" = []
    # Every name an import binds, aliases included: an attribute or an
    # item stored through one is a store into a module (batch 4l).
    imported: "set[str]" = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for one in node.names:
                if one.name.split(".")[0] in _BUILTIN_HOLDERS:
                    problems += [f"installation.py:{node.lineno}: imports {one.name}"]
                imported |= {(one.asname or one.name).split(".")[0]}
        if isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in _BUILTIN_HOLDERS:
                problems += [f"installation.py:{node.lineno}: imports from {node.module}"]
            imported |= {one.asname or one.name for one in node.names}
    # ...and every name assigned one of them, an attribute or an item of
    # one, followed to the end (batch 4m: `base = os; base.environ = ...`).
    holders = _aliases_of(tree, set(_TRUSTED) | set(_BUILTIN_HOLDERS) | imported)
    allowed: "set[int]" = set()
    for node in tree.body:
        if isinstance(node, ast.Import) and all(
            one.asname is None and one.name in _TRUSTED_IMPORTS for one in node.names
        ):
            allowed |= {id(node)}
    systems = [one for one in tree.body if isinstance(one, ast.FunctionDef) and one.name == "system_name"]
    if len(systems) == 1:
        allowed |= {id(systems[0])}
    for node in ast.walk(tree):
        if id(node) in allowed:
            continue
        for bound in _bound_names(node):
            if bound in _TRUSTED:
                line = getattr(node, "lineno", 0)
                problems += [f"installation.py:{line}: binds {bound}, a name the audit trusts"]
        if isinstance(node, ast.Attribute) and isinstance(node.ctx, (ast.Store, ast.Del)):
            root = _dotted(node).split(".")[0]
            if root in holders or not root:
                problems += [f"installation.py:{node.lineno}: stores into {_dotted(node) or 'a computed object'}"]
        if isinstance(node, ast.Subscript) and isinstance(node.ctx, (ast.Store, ast.Del)):
            root = _dotted(node.value).split(".")[0]
            if root in holders or not root:
                problems += [f"installation.py:{node.lineno}: stores an item into {_dotted(node.value) or 'a computed object'}"]
        if isinstance(node, ast.Call) and _dotted(node.func) in ("setattr", "delattr", "globals", "vars", "exec", "eval"):
            problems += [f"installation.py:{node.lineno}: calls {_dotted(node.func)}"]
        if isinstance(node, ast.Attribute) and node.attr in _REFLECTIVE:
            problems += [f"installation.py:{node.lineno}: reads {node.attr}, a namespace"]
        if isinstance(node, ast.Name) and node.id in _BUILTIN_HOLDERS:
            problems += [f"installation.py:{node.lineno}: names {node.id}"]
        if isinstance(node, ast.Call) and _dotted(node.func) == "getattr" and not (
            len(node.args) >= 2
            and isinstance(node.args[1], ast.Constant)
            and isinstance(node.args[1].value, str)
            and not node.args[1].value.startswith("_")
            and node.args[1].value not in _REFLECTIVE
        ):
            problems += [f"installation.py:{node.lineno}: getattr of a namespace or a computed name"]
    return problems


def data_folder_set_aside(name: str, tree: ast.Module) -> "tuple[set[int], list[str]]":
    """In ``installation.py``: the audited read's node ids and every problem; elsewhere nothing set aside."""
    if name != "installation.py":
        return set(), []
    functions = [
        one for one in tree.body if isinstance(one, ast.FunctionDef) and one.name == "data_folder"
    ]
    if len(functions) != 1:
        return set(), [f"installation.py: {len(functions)} data_folder functions, not one"]
    rebound = trusted_names_rebound(tree)
    aside, problems = data_folder_problems(functions[0])
    if rebound:
        return set(), problems + rebound
    return aside, problems


# THE NEGATIVE CASES (Codex's condition): each a change to today's
# `installation.py` that both checks must reject, today's file accepted.
_ANCHOR = "    where = environ if environ is not None else dict(os.environ)\n"
# Where a case written at the module's top level goes: after its imports.
_MODULE_ANCHOR = "import sys\n"
_THIRD_KEY = 'lambda source: {"XDG_DATA_HOME": source["synthtwin_smallest_group"]}'

# Written into `data_folder`, in place of the audited read.
_IN_THE_FUNCTION: "dict[str, str]" = {
    # A third key, in lower case, read straight from the environment
    # (Codex's own case).
    "a-third-lowercase-key": _ANCHOR + '    extra = os.environ.get("synthtwin_smallest_group")\n',
    # The same key read through the audited copy.
    "a-third-key-through-the-copy": _ANCHOR
    + '    extra = where["synthtwin_smallest_group"] if "synthtwin_smallest_group" in where else ""\n',
    # A key computed, so no written-out name shows it.
    "a-computed-key": _ANCHOR + '    key = "xdg_data_home".upper()\n    extra = where[key] if key in where else ""\n',
    # An audited key used outside the folder's choice.
    "the-environment-used-outside-the-folder": _ANCHOR
    + '    globals()["CHOSEN"] = where["LOCALAPPDATA"] if "LOCALAPPDATA" in where else ""\n',
    # A callee the audit trusts rebound before the copy, so `dict(os.environ)`
    # reads a third key (Codex's review of batch 4j, its first Medium).
    "a-rebound-callee": '    dict = lambda source: {"XDG_DATA_HOME": source["synthtwin_smallest_group"]}\n'
    + _ANCHOR,
}

# Written at the module's top level, after its imports (Codex's review of
# batch 4k, its one Medium): the built-ins reached through an alias or an
# item, and a trusted module's attribute stored through an alias.
_AT_THE_TOP: "dict[str, str]" = {
    "the-builtins-through-an-alias": _MODULE_ANCHOR + f"import builtins as base\nbase.dict = {_THIRD_KEY}\n",
    "the-builtins-through-an-item": _MODULE_ANCHOR + f'__builtins__["dict"] = {_THIRD_KEY}\n',
    "the-environment-through-an-aliased-module": _MODULE_ANCHOR
    + 'import os as system\nsystem.environ = {"XDG_DATA_HOME": "third-key"}\n',
}
# Written before `data_folder` (Codex's review of batch 4l, its third
# Medium, BATCH 4m OWES 3): the module's namespace reached through a trusted
# function's `__globals__` and rebound through the name it was assigned to
# (Codex's own case), and a trusted holder assigned to a plain name whose
# attribute or item is then stored into.
_FUNCTION_ANCHOR = "\ndef data_folder(\n"
_BEFORE_THE_FUNCTION: "dict[str, str]" = {
    "the-namespace-through-globals": "\nbase = system_name.__globals__\n"
    + f'base["dict"] = {_THIRD_KEY}\n' + _FUNCTION_ANCHOR,
    "the-environment-through-an-assigned-alias": "\nsystem = os\n"
    + 'system.environ = {"XDG_DATA_HOME": "third-key"}\n' + _FUNCTION_ANCHOR,
    "the-builtins-through-an-assigned-alias": "\nheld = __builtins__\n"
    + f'held["dict"] = {_THIRD_KEY}\n' + _FUNCTION_ANCHOR,
    "the-namespace-through-getattr": '\nbase = getattr(system_name, "__glob" + "als__")\n'
    + f'base["dict"] = {_THIRD_KEY}\n' + _FUNCTION_ANCHOR,
    # ...and a holder carried as a dictionary's value (batch 4n's records, Codex's review of batch
    # 4m, its fourth Medium, BATCH 4n OWES 4; Codex's exact case), or yielded by a comprehension.
    "the-builtins-through-a-dictionary-value": '\nholder = {"one": sys.modules["builtins"]}["one"]\n'
    + f"holder.dict = {_THIRD_KEY}\n" + _FUNCTION_ANCHOR,
    "the-builtins-through-a-comprehension": '\nholder = [one for one in (sys.modules["builtins"],)][0]\n'
    + f"holder.dict = {_THIRD_KEY}\n" + _FUNCTION_ANCHOR,
}
# Each case: the text it replaces and the text written in its place.
MUTANTS: "dict[str, tuple[str, str]]" = {
    **{case: (_ANCHOR, text) for case, text in _IN_THE_FUNCTION.items()},
    **{case: (_MODULE_ANCHOR, text) for case, text in _AT_THE_TOP.items()},
    **{case: (_FUNCTION_ANCHOR, text) for case, text in _BEFORE_THE_FUNCTION.items()},
}


def mutated(source: str, case: str) -> str:
    """Today's `installation.py` with the negative case ``case`` written in: in place of the audited read, after the module's imports, or before `data_folder`."""
    if source.count(_ANCHOR) != 1 or source.count(_MODULE_ANCHOR) != 1 or source.count(_FUNCTION_ANCHOR) != 1:
        raise AssertionError(
            "installation.py no longer holds the audited read, its import of sys or its data_folder, once"
        )
    anchor, text = MUTANTS[case]
    return source.replace(anchor, text)
