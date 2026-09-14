"""No list in the product is grown by copying it.

WHAT THIS PINS, AND WHY IT IS STATIC RATHER THAN TIMED. Both commands
were quadratic in the number of rows, and the cause was one idiom:
`x = x + [item]` rebuilds the whole list on every pass, so a loop over
rows copies a triangular number of elements. It stood in 661 places
plus 8 more where the target was a container slot rather than a plain
name, and neither the suite nor any guard noticed for the life of the
project. The accepted form is `x += [item]`, which is amortised
constant and which the offline scanner permits; `list.append` is
refused by that scanner, which is why the quadratic form was what the
rules left standing.

THE FIRST VERSION OF THIS GUARD WAS TIMED, AND REVIEW REJECTED IT. A
wall-clock ratio is not a gate: measured independently, restoring the
list defect alone gave a describing ratio of 2.506 and a generating
ratio of 2.155, both of which pass a threshold of three, so the guard
accepted a quadratic tree. In the other direction a single 0.6-second
pause during one sample made repaired code fail at 3.4. A ratio over
one sample each cannot cancel load that lands on only one of them.

So this counts the DEFECT rather than its symptom. It reads the source,
finds every assignment whose target and left operand name the same
storage and whose right operand is a list, and requires there to be
none. That is deterministic, costs milliseconds, names the file and
line, and cannot flake.

WHAT IT DELIBERATELY DOES NOT COVER. It sees this one idiom. A
quadratic written another way -- a rescan repeated once per item, which
is what `_shape_sizes` used to do -- is invisible to it, and that one
is pinned instead by `_merge_down`'s equivalence to `_merge_nearest`
over 4,200 randomised cases and by the frozen twin bytes. The two
defects this landing repaired are guarded by two different mechanisms
on purpose, because no single one caught both.
"""

import ast
import pathlib

PRODUCT = pathlib.Path(__file__).resolve().parent.parent / "src" / "synthtwin"


def _index(node: ast.expr) -> "tuple[str, ...] | None":
    """A subscript index, only where reading it twice is free of effect."""
    if isinstance(node, ast.Name):
        return ("name", node.id)
    if isinstance(node, ast.Constant):
        return ("const", repr(node.value))
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return ("attr", node.value.id, node.attr)
    return None


def _same_storage(left: ast.expr, right: ast.expr) -> bool:
    """Whether the two expressions name the same list, conservatively.

    A call, or a subscript whose index is itself computed, is never
    treated as the same storage: this guard reports what it is sure of.
    """
    if type(left) is not type(right):
        return False
    if isinstance(left, ast.Name) and isinstance(right, ast.Name):
        return left.id == right.id
    if isinstance(left, ast.Attribute) and isinstance(right, ast.Attribute):
        return left.attr == right.attr and _same_storage(left.value, right.value)
    if isinstance(left, ast.Subscript) and isinstance(right, ast.Subscript):
        here = _index(left.slice)
        there = _index(right.slice)
        return (
            here is not None
            and here == there
            and _same_storage(left.value, right.value)
        )
    return False


def test_no_product_source_grows_a_list_by_copying_it() -> None:
    """`x = x + [item]` appears nowhere in the product.

    Turns red the moment the idiom comes back, in any module, with a
    plain name or a container slot as its target.
    """
    found: "list[str]" = []
    for source in sorted(PRODUCT.glob("*.py")):
        tree = ast.parse(source.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            value = node.value
            if not isinstance(value, ast.BinOp):
                continue
            if not isinstance(value.op, ast.Add):
                continue
            if not isinstance(value.right, ast.List):
                continue
            if not _same_storage(node.targets[0], value.left):
                continue
            found += [f"{source.name}:{node.lineno}"]
    assert not found, (
        "a list is grown by copying it, which makes the loop around it "
        "quadratic in the number of rows or cells:\n  "
        + "\n  ".join(found)
        + "\n\nWrite `x += [item]` instead. It is amortised constant and "
        "the offline scanner accepts it, where it refuses `list.append`. "
        "This exact idiom in 669 places is what made describing a "
        "200,000-row table take 390 seconds and building a twin of "
        "20,000 rows take 1,113 seconds."
    )
