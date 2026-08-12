"""Fold collisions the domain can supply through edge spacing.

Review item P2-C2-F6. The fold a producer applies, and every recount in
this repository applies, is TRIM THEN CASE-FOLD. The collision
construction used only the second half of it, so a column whose folded
count is legitimately below its raw count lost that count whenever a
case flip could not carry the difference -- a value one character wide
with a single letter offers exactly one case variant, and a value
written in figures alone offers none at all. Owner decision 6 permits a
declared identifier to lose distinctness only where width and capacity
are jointly infeasible, and both distinctness counts are
EXACT-OBSERVABLE on every invention role outside that corner
(`docs/spec/profile-contract-v4.md` 9.7). A collision the domain can
supply is therefore a fact the twin owes, not a deviation it may name.

What this file holds to:

* the review's own producer-made case -- four spellings of one identity,
  one, two, two and three characters wide -- is BUILT: the twin holds
  four different spellings and one folded identity, and names no
  distinctness deviation;
* a case with NO letter anywhere in its domain, where edge spacing is
  the only construction there is, is built as well, so the closure is
  spacing and not a wider search over case;
* the built twin re-describes to the published facts, character for
  character through the shipped writer and reader, so the collisions
  survive the file rather than only the in-memory twin;
* the two published length ends survive being answered by a partner,
  and both alphabet counts and the whole-number fact survive edge
  spacing, because the fold trims before it counts;
* the partner family itself: case flips come first and in their old
  order, every partner folds onto its parent, partners are pairwise
  different, and the length window is never left.
"""

import pathlib

import pytest

import fixtures
from synthtwin import (
    canonical,
    contract,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    taxonomy,
)

SEEDS = (0, 1, 3, 17)


def _described(
    folder: pathlib.Path,
    name: str,
    text: str,
    declared: "list[str] | None" = None,
) -> contract.Profile:
    """Write a table, describe it with the producer, load the description."""
    path = fixtures.write(folder, f"{name}.csv", text)
    table = reading.read_table(str(path))
    document = profile.build_document(
        table, taxonomy.Settings(), declared if declared else []
    )
    target = folder / f"{name}-profile.json"
    target.write_text(
        canonical.serialize(document), encoding="utf-8", newline="\n"
    )
    return contract.load_profile(str(target))


def _column_of(rows: "list[str]") -> str:
    """One declared-identifier column of the given spellings."""
    return "key\n" + "\n".join(rows) + "\n"


def _counts(cells: "list[str]") -> "tuple[int, int]":
    """How many different spellings, and how many folded identities."""
    return (len(set(cells)), len({parsing.folded(cell) for cell in cells}))


def _named(twin: generation.Twin, fact: str) -> bool:
    """True when the twin names a deviation against ``fact``."""
    return any(note.fact == fact for note in twin.deviations)


# -- the review's own case ---------------------------------------------


@pytest.mark.parametrize("seed", SEEDS)
def test_the_spacing_collision_case_is_built_not_named(
    seed: int, tmp_path: pathlib.Path
) -> None:
    """Four spellings of one identity, one to three characters wide.

    This is the review's own producer input. Its source column proves
    the pattern is feasible inside the published length range, so owner
    decision 6's infeasible corner is not reached and the twin owes the
    exact folded count.
    """
    described = _described(
        tmp_path,
        "edges",
        _column_of(["a", " a", "a ", " a "]),
        ["key"],
    )
    column = described.columns[0]
    assert column.role == "identifier"
    assert (column.n_distinct, column.n_distinct_folded) == (4, 1)
    facts = column.facts
    assert isinstance(facts, contract.IdentifierFacts)
    assert (facts.min_length, facts.max_length) == (1, 3)

    twin = generation.generate(described, seed=seed)
    cells = list(twin.columns[0])
    assert _counts(cells) == (4, 1), (
        "the collisions this column publishes are buildable inside its own "
        "published length range, so the twin owes them exactly"
    )
    assert not _named(twin, "n_distinct")
    assert not _named(twin, "n_distinct_folded")
    lengths = [len(cell) for cell in cells]
    assert (min(lengths), max(lengths)) == (1, 3)


@pytest.mark.parametrize("seed", SEEDS)
def test_a_domain_with_no_letter_at_all_still_builds_its_collisions(
    seed: int, tmp_path: pathlib.Path
) -> None:
    """The closure is edge spacing, and this proves it is.

    Every value of this column is written in figures, is a whole number,
    and is counted in both alphabet counts. No character of that domain
    has a case, so no case flip exists to build a collision from: if the
    twin still holds one folded identity, edge spacing is what built it.
    """
    described = _described(
        tmp_path,
        "figures",
        _column_of(["1", " 1", "1 ", " 1 "]),
        ["key"],
    )
    column = described.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.IdentifierFacts)
    assert (column.n_distinct, column.n_distinct_folded) == (4, 1)
    assert facts.all_whole_numbers
    assert (facts.n_all_digits, facts.n_code_alphabet) == (4, 4)
    assert (facts.min_length, facts.max_length) == (1, 3)

    twin = generation.generate(described, seed=seed)
    cells = list(twin.columns[0])
    assert _counts(cells) == (4, 1)
    for cell in cells:
        assert not any(generation._has_case(figure) for figure in cell), (
            "no value of this column holds a character with a case, so no "
            "case flip can be what built the collisions"
        )
    assert [cell for cell in cells if cell != cell.strip()], (
        "at least one value carries the edge spacing that built the collision"
    )
    assert twin.deviations == ()


@pytest.mark.parametrize("seed", SEEDS)
def test_edge_spacing_leaves_every_other_published_fact_where_it_was(
    seed: int, tmp_path: pathlib.Path
) -> None:
    """The alphabet counts and the whole-number fact are read after trimming.

    That is what makes edge spacing a safe partner: the characters both
    alphabet counts are read from do not move, and neither does the
    reading that decides whether a value is a whole number.
    """
    described = _described(
        tmp_path,
        "figures",
        _column_of(["1", " 1", "1 ", " 1 "]),
        ["key"],
    )
    facts = described.columns[0].facts
    assert isinstance(facts, contract.IdentifierFacts)
    twin = generation.generate(described, seed=seed)
    cells = list(twin.columns[0])

    digits = len(
        [cell for cell in cells if parsing.is_digit_text(parsing.trimmed(cell))]
    )
    coded = len(
        [cell for cell in cells if parsing.is_code_text(parsing.trimmed(cell))]
    )
    assert (digits, coded) == (facts.n_all_digits, facts.n_code_alphabet)
    for cell in cells:
        assert parsing.classify_number(cell) == parsing.NUMBER
        value = parsing.parse_number(cell)
        assert value is not None and parsing.is_whole_number(value)


# -- the collisions survive the file, not only the twin ----------------


@pytest.mark.parametrize("seed", SEEDS)
def test_the_written_twin_describes_again_to_the_published_facts(
    seed: int, tmp_path: pathlib.Path
) -> None:
    """Through the shipped writer and the shipped reader, unchanged.

    A collision built from edge spacing is only worth anything if the
    spacing reaches the file: the writer quotes for a comma, a quote
    character and a line ending and for nothing else, and the reader
    keeps a leading space rather than eating it. This asks the twin
    itself, by describing it again and comparing every published fact.
    """
    described = _described(
        tmp_path,
        "edges",
        _column_of(["a", " a", "a ", " a "]),
        ["key"],
    )
    published = described.columns[0]
    twin = generation.generate(described, seed=seed)
    again = _described(
        tmp_path, "twin", rendering.twin_csv(twin), ["key"]
    )
    rebuilt = again.columns[0]
    assert rebuilt.n_present == published.n_present
    assert rebuilt.n_distinct == published.n_distinct
    assert rebuilt.n_distinct_folded == published.n_distinct_folded
    assert rebuilt.facts == published.facts


@pytest.mark.parametrize("seed", SEEDS)
def test_a_spacing_partner_never_creates_a_formula_hazard(
    seed: int, tmp_path: pathlib.Path
) -> None:
    """A space at the front is not a character a spreadsheet acts on."""
    described = _described(
        tmp_path,
        "edges",
        _column_of(["a", " a", "a ", " a "]),
        ["key"],
    )
    twin = generation.generate(described, seed=seed)
    hazards, columns = rendering._formula_hazard(twin)
    assert (hazards, columns) == (0, [])


# -- the partner family itself ------------------------------------------


def test_case_flips_still_come_first_and_in_their_old_order() -> None:
    """The widened family did not move the partners it already had.

    Orders one upward walk the case flips of method G8.2 before any
    spacing is reached, so a column whose collisions case alone could
    carry writes exactly what it wrote before this family was widened.
    """
    parent = "Ab"
    flips = [generation._case_variant(parent, order) for order in (1, 2, 3)]
    assert flips == ["ab", "AB", "aB"]
    partners = [
        generation._partner_at(parent, order, 2, 6) for order in (1, 2, 3)
    ]
    assert partners == flips
    assert generation._partner_at(parent, 4, 2, 6) == "Ab "
    assert generation._partner_at(parent, 5, 2, 6) == "ab "


def test_every_partner_folds_onto_its_parent_and_stays_in_its_window() -> None:
    """The two obligations a partner carries, over a range of parents."""
    for parent in ("A", "1", "Ab", "a-9", "  x  ".strip()):
        for longest in (len(parent), len(parent) + 1, len(parent) + 3):
            seen: list[str] = []
            for order in range(1, 40):
                built = generation._partner_at(
                    parent, order, 1, longest
                )
                if built is None:
                    break
                assert parsing.folded(built) == parsing.folded(parent)
                assert 1 <= len(built) <= longest
                assert built != parent
                seen = seen + [built]
            assert len(set(seen)) == len(seen), (
                "two orders of one parent's family never build the same "
                "partner, which is what bounds the walk over it"
            )


def test_a_parent_with_no_case_and_no_room_has_no_partner() -> None:
    """The genuinely infeasible corner still says so, rather than guessing.

    A value written in figures alone at the one length the description
    permits can neither be varied in case nor lengthened, so its family
    is empty and the walk hands back nothing. That is the corner owner
    decision 6 governs, and it is reached only here.
    """
    assert generation._partner_at("1", 1, 1, 1) is None
    assert generation._partner_at("1", 1, 1, 2) == "1 "
    assert generation._partner_at("1", 2, 1, 2) == " 1"
    assert generation._partner_at("A", 1, 1, 1) == "a"


def test_a_pinned_length_end_holds_when_a_partner_answers_for_it() -> None:
    """The window a pinned value carries is its one published length.

    Two invented values carry the shortest and the longest published
    length (method G9.2) -- the first two on a column of record numbers,
    and on a column of free text whichever two the allocation of G9.5
    settled on (review item P2-C4-F2). Edge spacing lengthens, so the
    value carrying the longest end CAN be a partner of the value
    carrying the shortest -- but only at the length it was pinned to,
    which is what `_length_windows` states, wherever the pins landed.
    """
    windows = generation._length_windows(4, 1, 3, True, (0, 1))
    assert windows[0] == (1, 1)
    assert windows[1] == (3, 3)
    assert windows[2] == (1, 3)
    assert generation._partner_at("A", 1, 3, 3) == "A  "
    assert generation._partner_at("A", 2, 3, 3) == "a  "
    assert len(generation._partner_at("A", 1, 3, 3) or "") == 3

    # The same statement with the ends carried by two other groups: the
    # window follows the pin and never the group's place in the order.
    moved = generation._length_windows(4, 1, 3, True, (2, 0))
    assert moved[2] == (1, 1)
    assert moved[0] == (3, 3)
    assert moved[1] == (1, 3)
    assert moved[3] == (1, 3)

    flat = generation._length_windows(4, 2, 2, False, (0, 1))
    assert flat[1] == (2, 2)
    unbounded = generation._length_windows(2, 1, None, False, (0, 1))
    assert unbounded[1] == (1, None)


def test_the_walk_over_one_parent_ends_when_its_window_is_spent() -> None:
    """No order past the family's own size ever builds anything."""
    built = []
    for order in range(1, 200):
        candidate = generation._partner_at("1", order, 1, 3)
        if candidate is None:
            break
        built = built + [candidate]
    # one space: two ways to place it; two spaces: three ways.
    assert len(built) == 5
    assert generation._partner_at("1", 6, 1, 3) is None


def test_spacing_never_turns_a_partner_into_something_it_must_not_be() -> None:
    """Every rejection the ordinary walk applies is blind to edge spacing.

    That is what lets a partner skip those checks and inherit its
    parent's answers: the spellings that mean "no value" are compared
    after trimming, the date reader trims, and the numeric class a cell
    reads back as is decided after trimming. A partner of a parent that
    passed all three passes all three.
    """
    for parent in ("x", "1e999", "12", "a-9", "(-1)"):
        for order in range(1, 12):
            built = generation._partner_at(parent, order, 1, len(parent) + 2)
            if built is None:
                break
            assert parsing.is_missing_text(built) == parsing.is_missing_text(
                parent
            )
            assert generation._reads_as_a_date(
                built
            ) == generation._reads_as_a_date(parent)
            assert parsing.classify_number(built) == parsing.classify_number(
                parent
            )
            assert parsing.is_digit_text(
                parsing.trimmed(built)
            ) == parsing.is_digit_text(parsing.trimmed(parent))
            assert parsing.is_code_text(
                parsing.trimmed(built)
            ) == parsing.is_code_text(parsing.trimmed(parent))
            assert parsing.token_count(built) == parsing.token_count(parent)


def test_the_shared_construction_reaches_spacing_on_every_role() -> None:
    """`_partner_of` is one function, and all three roles ask it.

    This asks it the way a column of free text does -- a family key
    carrying a numeric class beside a band, and a window taken from the
    published length range -- with a parent that offers no case flip at
    all. Spacing is what answers.
    """
    families = ["text/digits", "text/digits", "text/digits"]
    windows: list[tuple[int, int | None]] = [(2, 4), (4, 4), (2, 4)]
    spellings = ["12", "1234"]
    used: dict[str, int] = {"12": 1, "1234": 1}
    built = generation._partner_of(2, 2, spellings, families, used, windows)
    assert built is not None
    assert parsing.folded(built) in {"12", "1234"}
    assert 2 <= len(built) <= 4
    assert built.strip() != built, (
        "no value of this family holds a character with a case, so spacing "
        "is the only construction that can have built this"
    )


def test_the_collision_capacity_check_counts_both_constructions() -> None:
    """A pre-write refusal that counts one construction refuses too much.

    The check that runs before any cell is built asks whether the domain
    can carry the collisions the description publishes. Counting only
    the spellings with a case in them turns away a column whose
    collisions edge spacing can build, which is a refusal of a valid
    description. Both halves are counted and their counts add, because
    two different parents never build the same partner.
    """
    lettered = generation._lettered_domain_size(generation._WIDE, 1, 1, 60)
    assert lettered == 52
    padded = generation._padded_room(generation._WIDE, 1, 2, 200)
    assert padded == 2 * 95, (
        "one space, placed at either end, on each spelling of length one"
    )
    assert generation._padded_room(generation._WIDE, 1, 1, 200) == 0, (
        "a column whose one permitted length is also its shortest has no "
        "room for a space, which is the corner that genuinely cannot build"
    )
