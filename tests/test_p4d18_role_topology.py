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

from synthtwin import contract

CONTRACT = (
    pathlib.Path(__file__).resolve().parent.parent
    / "docs" / "spec" / "profile-contract-v6.md"
)

# The matrix abbreviates the FOURTEEN roles for width; section 6.11
# states the expansion and this is it, in the matrix's own order.
# `jnd` is `joined_numbers` and joined the matrix with plan P4-D26,
# which is what put the fourteenth role into the contract at all.
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
    "joined_numbers",
)


def _matrix() -> "tuple[dict[str, set[str]], int, int]":
    """Every marked cell of section 6.11, read out of the document."""
    text = CONTRACT.read_text(encoding="utf-8")
    start = text.index("### 6.11 The forbidden-key matrix")
    body = text[start : text.index("\n**Sixty-six rows", start)]
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
# THE ONE EXCEPTION THIS GUARD HELD IS GONE (residual R-P4-37, closed
# 2026-08-26). The contract stated `min_length` and `max_length` on
# `numeric_unrepresentable` in four places and the producer wrote
# neither, so a producer written to the contract emitted a block the
# shipped loader refused. This guard found it on its first run, held it
# as a NAMED exception so it could not be mistaken for new and could
# not grow, and the exception is now empty because the facts are built.
#
# IT STAYS AS AN EMPTY SET rather than being deleted: the guard reads
# it in both directions, and a future disagreement should have to be
# added here on purpose by somebody who writes down why.
INHERITED: "set[tuple[str, str]]" = set()


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
    assert (
        "**Sixty-six rows, one hundred and twenty-nine marked cells**"
        in said
    )
    assert rows == 66, rows
    assert cells == 129, cells


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
