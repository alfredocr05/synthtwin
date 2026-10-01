"""K-2B-42: how close the independent oracle's functions sit to the shipped code.

The oracle (`tools/reference/make_generation_reference_vectors.py`) is
worth something only while it is written from the method's statements
and not from the shipped generator. Method section G14.2 names what was
measured when the document transforms were added: 13 of 53 of them
scored 0.60 or above against their closest shipped function. The
skeptic's scoring script was not kept, so this is a re-statement of the
same measure that a reader can run:

- every function of six statements or more, in the oracle and in
  `src/synthtwin`, is reduced to the sequence of its syntax-node kinds,
  with its docstring and annotations dropped and every name ignored;
- each oracle function is scored against its closest shipped function
  by `difflib.SequenceMatcher.ratio` on those sequences (candidates whose
  node-kind multisets cannot reach 0.60 are skipped, which cannot change
  a score at or above 0.60);
- the count at or above 0.60 is the ledger value, and the functions are
  named, so a NEW close copy is named rather than summed.

It scores all the oracle's functions, not only the 53 document
transforms, so its count is not G14.2's 13. A few minutes.

    .venv/bin/python tools/measurements/kpi_oracle_similarity.py --kpi
"""

import ast
import collections
import difflib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
THRESHOLD = 0.60
MIN_STATEMENTS = 6


def kinds_of(function):
    body = list(function.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant):
        body = body[1:]
    out = []
    for statement in body:
        for node in ast.walk(statement):
            if isinstance(node, (ast.expr_context, ast.arg)):
                continue
            out.append(type(node).__name__)
    return out


def functions(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            statements = sum(1 for inner in ast.walk(node) if isinstance(inner, ast.stmt)) - 1
            if statements >= MIN_STATEMENTS:
                yield f"{path.name}:{node.name}", kinds_of(node)


shipped = []
for path in sorted((ROOT / "src" / "synthtwin").glob("*.py")):
    shipped += list(functions(path))
shipped_counts = [(name, kinds, collections.Counter(kinds)) for name, kinds in shipped]
oracle = list(functions(ROOT / "tools" / "reference" / "make_generation_reference_vectors.py"))
close = []
scores = []
for name, kinds in oracle:
    mine = collections.Counter(kinds)
    best, best_name = 0.0, ""
    matcher = difflib.SequenceMatcher(autojunk=False)
    matcher.set_seq2(kinds)
    for other_name, other, counts in shipped_counts:
        total = len(kinds) + len(other)
        if total == 0 or 2 * sum((mine & counts).values()) / total < max(THRESHOLD, best):
            continue
        matcher.set_seq1(other)
        score = matcher.ratio()
        if score > best:
            best, best_name = score, other_name
    scores.append(best)
    if best >= THRESHOLD:
        close.append(f"{name.split(':')[1]}~{best_name.split(':')[1]}={best:.2f}")
print(f"oracle functions scored: {len(oracle)} against {len(shipped)} shipped", flush=True)
for line in close:
    print("  ", line)
kpi_rules.emit("K-2B-42", {"at_or_above_0_60": len(close), "scored": len(oracle)}, ", ".join(close))
