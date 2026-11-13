"""Every module-level name of the package is bound once (batch 4p's fix round; plan P4-D449's fix-round lines).

A merge can keep two definitions of one module-level name without a
textual conflict. Batch 4p's merge of lane GRa kept lane HB's
`asking.KEY_WORDS` (the words that name a key, plan P4-D442) beside lane
GRa's list of the same name (the person question's words, plan P4-D449);
the later one won at import, so `named_as_a_key` read the other list and a
repeating key named `CSN` was no longer asked about. This file reads every
module of `src/synthtwin` with the standard library's `ast` (nothing is
imported or run) and refuses a name a module binds twice at its top level:
an assignment's name (a tuple's names one by one), an annotated assignment
with a value, a def, a class, an import, a `for` target or a `with` target
(each of its `as` names), in the module's body or in a block of a top-level
`if`, `try`, `with`, `for` or `while`. MUTANTS: a module binding one of its
names a second time; the sealed head `d8f5e147`'s `asking.py`; and, since
batch 4p's records round (the fix round's scoped verify, its carry 4), a
second `KEY_WORDS` bound by a top-level `for` target and by a `with` target.
"""

import ast
import pathlib

SRC_TREE = pathlib.Path(__file__).resolve().parents[1] / "src" / "synthtwin"


def _names(target: ast.expr) -> "list[str]":
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.Tuple, ast.List)):
        out: "list[str]" = []
        for one in target.elts:
            out += _names(one)
        return out
    if isinstance(target, ast.Starred):
        return _names(target.value)
    return []


def _bindings(body: "list[ast.stmt]") -> "list[tuple[str, int]]":
    found: "list[tuple[str, int]]" = []
    for node in body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                found += [(name, node.lineno) for name in _names(target)]
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            found += [(name, node.lineno) for name in _names(node.target)]
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            found += [(node.name, node.lineno)]
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            found += [((alias.asname or alias.name).split(".")[0], node.lineno) for alias in node.names]
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            found += [(name, node.lineno) for name in _names(node.target)]
            found += _bindings(list(node.body) + list(node.orelse))
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                if item.optional_vars is not None:
                    found += [(name, node.lineno) for name in _names(item.optional_vars)]
            found += _bindings(list(node.body))
        elif isinstance(node, (ast.If, ast.Try, ast.While)):
            inner = list(node.body) + list(getattr(node, "orelse", [])) + list(getattr(node, "finalbody", []))
            for handler in getattr(node, "handlers", []):
                inner += list(handler.body)
            found += _bindings(inner)
    return found


def bound_twice(text: str) -> "dict[str, list[int]]":
    """Each name a module's top level binds more than once, with the lines that bind it."""
    seen: "dict[str, list[int]]" = {}
    for name, line in _bindings(ast.parse(text).body):
        seen.setdefault(name, []).append(line)
    return {name: lines for name, lines in seen.items() if len(lines) > 1}


def test_no_module_level_name_of_the_package_is_bound_twice() -> None:
    modules = sorted(SRC_TREE.glob("*.py"))
    assert len(modules) >= 30
    found = {path.name: bound_twice(path.read_text(encoding="utf-8")) for path in modules}
    assert not {name: twice for name, twice in found.items() if twice}


def test_the_check_reads_every_way_a_module_binds_a_name() -> None:
    assert bound_twice("A = 1\nB = 2\nA = 3\n") == {"A": [1, 3]}
    assert bound_twice("X, Y = 1, 2\ndef Y():\n    pass\n") == {"Y": [1, 2]}
    assert bound_twice("import os\nos: int = 1\n") == {"os": [1, 2]}
    assert bound_twice("class K:\n    pass\nK = None\n") == {"K": [1, 3]}
    assert bound_twice("A = 1\nif A:\n    A = 2\n") == {"A": [1, 3]}
    assert bound_twice("A: int\nA = 1\ndef f():\n    A = 2\n") == {}


def test_a_for_target_and_a_with_target_bind_a_name() -> None:
    # The fix round's scoped verify (its carry 4; the orchestrator's LANE I4p RULINGS 7 (2) (d)): a second
    # `KEY_WORDS` bound by `for KEY_WORDS in (frozenset(),): pass` at the end of `asking.py` left the case
    # above green. Each kind of binding below is read now, and a name bound only inside a function is
    # still the function's own.
    assert bound_twice("A = 1\nfor A in ():\n    pass\n") == {"A": [1, 2]}
    assert bound_twice("for B, *C in ():\n    pass\nC = 1\n") == {"C": [1, 3]}
    assert bound_twice("for D in ():\n    E = 1\nelse:\n    E = 2\n") == {"E": [2, 4]}
    assert bound_twice("import contextlib\nwith contextlib.nullcontext() as F:\n    pass\nF = 1\n") == {"F": [2, 4]}
    assert bound_twice("import contextlib\nwith contextlib.nullcontext() as (G, H):\n    H = 1\n") == {"H": [2, 3]}
    assert bound_twice("while False:\n    J = 1\nJ = 2\n") == {"J": [2, 3]}
    assert bound_twice("def f():\n    for M in ():\n        pass\n    with open(f) as M:\n        pass\nM = 1\n") == {}
