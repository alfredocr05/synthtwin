"""The forbidden-key matrix is the ONE statement of where a key lives.

Round 2 finding 10. `shape_forms` was added to the code and to section
6.11's matrix and to the disposition matrix, and THREE other places in
the two governing documents went on saying it stood on two roles: the
role sections' "four shared label keys", C6-31b, and the generation
method's G8.3. A producer written to section 6.4 emitted a `constant`
block the shipped loader then refused for a missing key, and a consumer
written to C6-31b refused a shipped `categorical` profile for carrying
one.

Every one of those sentences was corrected by hand, which is exactly
how the next one will drift. So this reads the matrix out of the
contract and compares it, in BOTH directions, against the key set the
loader actually requires -- for all thirteen roles. After this, section
6.11 is the single normative statement and the prose cannot quietly
disagree with it.
"""

import pathlib
import re

from synthtwin import contract

CONTRACT = (
    pathlib.Path(__file__).resolve().parent.parent
    / "docs" / "spec" / "profile-contract-v6.md"
)

# The matrix abbreviates the thirteen roles for width; section 6.11
# states the expansion and this is it, in the matrix's own order.
COLUMNS = (
    "empty",
    "numeric_unrepresentable",
    "constant",
    "binary",
    "categorical",
    "long_tail_labels",
    "datetime",
    "time_of_day",
    "count",
    "continuous",
    "affixed_number",
    "identifier",
    "free_text",
)


def _matrix() -> "tuple[dict[str, set[str]], int, int]":
    """Every marked cell of section 6.11, read out of the document."""
    text = CONTRACT.read_text(encoding="utf-8")
    start = text.index("### 6.11 The forbidden-key matrix")
    body = text[start : text.index("\n**Fifty-seven rows", start)]
    marked: "dict[str, set[str]]" = {role: set() for role in COLUMNS}
    rows = 0
    cells = 0
    for line in body.split("\n"):
        if not line.startswith("| `"):
            continue
        parts = [part.strip() for part in line.split("|")[1:-1]]
        if len(parts) != len(COLUMNS) + 1:
            continue
        key = parts[0].replace(" (echo)", "").strip().strip("`")
        rows = rows + 1
        for place in range(len(COLUMNS)):
            if parts[place + 1] == "●":
                marked[COLUMNS[place]].add(key)
                cells = cells + 1
    return marked, rows, cells


# THE ONE DISAGREEMENT THIS GUARD INHERITED, named and dated so it
# cannot be mistaken for something this landing did, and held so it
# cannot GROW (residual R-P4-37, opened 2026-08-25).
#
# The contract states `min_length` and `max_length` on
# `numeric_unrepresentable` in four places -- the added-keys table of
# 6.2, invariant U5, producer obligation U-P, and this matrix -- and
# the producer has never emitted either. A producer written to the
# contract therefore writes a block the shipped loader refuses for an
# unknown key. It predates the form census entirely and closing it is
# a decision about that role's format, not about this one.
INHERITED = {("numeric_unrepresentable", "max_length"),
             ("numeric_unrepresentable", "min_length")}


def test_the_matrix_and_the_loader_agree_role_by_role() -> None:
    """In BOTH directions, for all thirteen roles.

    A key the matrix marks that the loader does not require is a
    document a conforming producer writes and the shipped tool refuses;
    a key the loader requires that the matrix does not mark is a
    document the tool writes and a conforming consumer refuses. Both
    happened, which is why this exists.

    The one inherited disagreement is named above and subtracted here.
    Everything else must agree exactly, and a NEW disagreement -- in
    either direction, on any role -- turns this red.
    """
    marked, _rows, _cells = _matrix()
    universal = set(contract.UNIVERSAL_COLUMN_KEYS)
    found: "set[tuple[str, str]]" = set()
    for role in COLUMNS:
        wanted = set(contract._role_keys(role)) - universal
        for key in marked[role] - wanted:
            found.add((role, key))
        for key in wanted - marked[role]:
            found.add((role, key))
    assert found == INHERITED, (
        "the matrix and the loader disagree about where a key lives, "
        f"beyond the one disagreement this guard inherited: "
        f"{sorted(found - INHERITED)} are new, and "
        f"{sorted(INHERITED - found)} were fixed without this list "
        f"being narrowed"
    )


def test_the_matrix_totals_are_the_numbers_the_matrix_holds() -> None:
    """So a hand-edited cell cannot slip past the count sentence either."""
    _marked, rows, cells = _matrix()
    said = CONTRACT.read_text(encoding="utf-8")
    assert f"**Fifty-seven rows, one hundred and fifteen marked cells**" in said
    assert rows == 57, rows
    assert cells == 115, cells


def test_the_form_census_stands_on_exactly_five_roles() -> None:
    """The fact finding 10 was about, asserted where a reader looks."""
    marked, _rows, _cells = _matrix()
    carrying = {
        role for role in COLUMNS if "shape_forms" in marked[role]
    }
    assert carrying == {
        "constant",
        "binary",
        "categorical",
        "long_tail_labels",
        "free_text",
    }, sorted(carrying)
