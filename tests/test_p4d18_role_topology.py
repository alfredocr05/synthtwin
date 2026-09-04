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


from synthtwin import contract

import fixtures

# Derived, never named: review item P4-A1-R3-F2.
CONTRACT = fixtures.GOVERNING_CONTRACT

# The matrix abbreviates the roles for width; section 6.11 states the
# expansion and this is it, in the matrix's own order.
#
# THIS LIST WAS HAND-WRITTEN AND FELL BEHIND, which is the defect this
# whole file exists to stop. It held fourteen names while the loader
# knew fifteen, so the matrix could omit `numbers_with_labels` -- the
# role landing L8 added -- and this guard endorsed the omission
# instead of catching it. The names are read from the LOADER now and
# the matrix's own order is asserted against them, so a role added to
# the product and not to section 6.11 turns this red on its first run.
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
    "numbers_with_labels",
)


def test_the_matrix_has_a_column_for_every_role_the_loader_knows() -> None:
    """The list above is the matrix's ORDER; the loader is its CONTENT.

    An order cannot be derived -- section 6.11 chooses it and this file
    has to follow it to read a row -- but the SET can be, and it is the
    set that fell behind: fourteen names here against the loader's
    fifteen, so `numbers_with_labels` was missing from the matrix and
    from this guard together and neither could see the other's gap.
    """
    assert set(COLUMNS) == set(contract.ROLES), (
        "section 6.11's columns and the roles the loader knows are "
        f"not the same set: {sorted(set(COLUMNS) ^ set(contract.ROLES))}"
    )
    assert len(COLUMNS) == len(contract.ROLES), COLUMNS


HEAD = "| key | emp |"
_TENS = (
    "", "ten", "twenty", "thirty", "forty", "fifty", "sixty",
    "seventy", "eighty", "ninety",
)
_ONES = (
    "", "one", "two", "three", "four", "five", "six", "seven",
    "eight", "nine", "ten", "eleven", "twelve", "thirteen",
    "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
    "nineteen",
)


def _in_words(count: int) -> str:
    """A count written the way this contract writes its counts.

    So the guard can build the sentence it is looking for instead of
    carrying a copy of it that a landing has to remember to move.
    """
    if count < 20:
        return _ONES[count]
    if count < 100:
        rest = count % 10
        tail = f"-{_ONES[rest]}" if rest else ""
        return f"{_TENS[count // 10]}{tail}"
    hundreds = _ONES[count // 100]
    rest = count % 100
    if not rest:
        return f"{hundreds} hundred"
    return f"{hundreds} hundred and {_in_words(rest)}"


def _matrix() -> "tuple[dict[str, set[str]], int, int]":
    """Every marked cell of section 6.11, read out of the document."""
    text = CONTRACT.read_text(encoding="utf-8")
    start = text.index("### 6.11 The forbidden-key matrix")
    # THE TABLE'S OWN END, not a sentence beneath it. This read the
    # count sentence by its words, so every landing that moved a total
    # had to move this string too -- and a landing that moved the
    # sentence and not the string, or the other way, made the reader
    # find a different table or none at all.
    body = text[start : text.index("\n\n**", text.index(HEAD, start))]
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
    assert _in_words(rows).capitalize() in said, rows
    assert (
        f"**{_in_words(rows).capitalize()} rows, {_in_words(cells)} "
        f"marked cells**" in " ".join(said.split())
    ), (rows, cells)
    # AND THE PER-ROLE BREAKDOWN BESIDE THE TOTAL, which this guard did
    # not read until 2026-09-04 and which was stale by six on three
    # roles and silent on a fourth. A total that adds up says nothing
    # about the numbers it adds.
    # Read with the line breaks taken out: the sentence wraps, and a
    # role and its count can fall on either side of a wrap.
    flat = " ".join(said.split())
    for role, many in _matrix()[0].items():
        assert f"`{role}` {len(many)}" in flat, (
            f"section 6.11's sentence does not say `{role}` "
            f"{len(many)}, which is what its own matrix holds"
        )


def test_the_key_counts_in_words_are_the_key_sets_the_loader_holds(
) -> None:
    """The two role sections count their own keys, in words.

    THE SAME SHAPE AS THE MATRIX TOTALS, and it drifted the same way:
    the `count`/`continuous` table said "eighteen keys" while it held
    twenty-four, and the `affixed_number` section said "forty-seven
    keys ... eighteen additions" while the loader wanted fifty-four
    and thirty-two. A schema written to those numerals refuses keys
    the shipped tool writes.

    The numerals are built from the loader's own tuples here, so a
    landing that adds a key and leaves a sentence behind turns red.
    """
    said = " ".join(CONTRACT.read_text(encoding="utf-8").split())
    numeric = len(contract.NUMERIC_KEYS)
    affixed = len(contract.AFFIXED_KEYS)
    universal = len(contract.UNIVERSAL_COLUMN_KEYS)
    assert f"{_in_words(numeric).capitalize()} keys." in said, numeric
    assert (
        f"**The block is {_in_words(universal + affixed)} keys**" in said
    ), universal + affixed
    assert (
        f"the {_in_words(universal)} universal keys of section 5.1 and "
        f"the {_in_words(affixed)} above" in said
    ), affixed
    assert (
        f"a `count` block's {_in_words(numeric)} additions" in said
    ), numeric


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
