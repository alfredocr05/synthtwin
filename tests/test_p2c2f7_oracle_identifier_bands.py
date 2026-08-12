"""The independent oracle's identifier bands (review item P2-C2-F7).

The oracle in `tools/reference/make_generation_reference_vectors.py`
carried a rule method section G9.6 had WITHDRAWN: that a column
publishing `all_whole_numbers` true is written from the figures alone.
No frozen vector reached the branch, so rebuilding the committed file
byte for byte never tested it, and an oracle that blesses a withdrawn
rule can reject a conforming implementation or certify a nonconforming
one.

The repair is the oracle's, not the implementation's: the bands come
from the two published alphabet counts and from nothing else, and what
`all_whole_numbers` decides is what each band WRITES. These tests
exercise the branch the vectors now cover, the corner they deliberately
do not, and the oracle's own recount -- which is what would have refused
the withdrawn rule at the moment it built its cells.

Everything here reads the oracle from its path, exactly as
`tests/test_generation_reference.py` does. Nothing here reads the
implementation: this file is about what the oracle says the
specification requires.
"""

import importlib.util
import pathlib

import pytest

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
GENERATOR = REPOSITORY / "tools" / "reference" / "make_generation_reference_vectors.py"


def _generator():
    spec = importlib.util.spec_from_file_location(
        "make_generation_reference_vectors", GENERATOR
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gen = _generator()

DIGIT_CHARACTERS = frozenset(gen.DIGITS)
CODE_CHARACTERS = frozenset(gen.CODE)


def _all_digits(cells: list) -> int:
    return sum(
        1 for cell in cells if cell.strip() and set(cell.strip()) <= DIGIT_CHARACTERS
    )


def _code_alphabet(cells: list) -> int:
    return sum(
        1 for cell in cells if cell.strip() and set(cell.strip()) <= CODE_CHARACTERS
    )


def _identifier_column(**facts) -> dict:
    """A declared identifier block carrying only hand-written neutral facts."""
    column = gen._identifier_fold_collisions()["column"]
    return dict(column, **facts)


# --------------------------------------------- the branch the review named


def test_whole_numbers_do_not_force_the_figures_alphabet() -> None:
    """The exact scenario review item P2-C2-F7 ran, with its exact numbers.

    A column of `+1` and `+2` publishes `all_whole_numbers` true with
    BOTH alphabet counts at nought, because `+` is in neither alphabet,
    and the producer writes exactly that (method section G9.6). The
    withdrawn rule built fourteen cells that were figures and nothing
    else against a published nought, and fourteen code-alphabet cells
    against a published nought. Both counts are EXACT-OBSERVABLE on
    this role in every case.
    """
    column = _identifier_column(
        all_whole_numbers=True,
        n_all_digits=0,
        n_code_alphabet=0,
        n_distinct_folded=14,
        n_numeric=14,
        n_not_numeric=0,
    )
    content = gen._identifier_content(column)
    assert len(content) == column["n_present"]
    assert _all_digits(content) == 0
    assert _code_alphabet(content) == 0
    assert all(gen._is_a_whole_number(cell) for cell in content)


def test_each_band_writes_its_own_whole_number_spelling() -> None:
    """G9.6's three templates, on a column whose counts reach all three.

    The figures write the digits themselves with a non-zero leading
    digit; the code band writes `<digits>e0`, which holds a character
    the figures do not; and outside the code alphabet the cell is
    written `<digits>.`, whose one character outside that alphabet is
    the LAST rather than the leftmost, because a whole number cannot
    begin with a point.
    """
    column = gen._identifier_whole_numbers()["column"]
    content = gen._identifier_content(column)
    assert _all_digits(content) == column["n_all_digits"] == 4
    assert _code_alphabet(content) == column["n_code_alphabet"] == 8
    assert all(gen._is_a_whole_number(cell) for cell in content)
    figures = [cell for cell in content if set(cell) <= DIGIT_CHARACTERS]
    assert all(not cell.startswith("0") for cell in figures)
    code = [
        cell
        for cell in content
        if set(cell) <= CODE_CHARACTERS and not set(cell) <= DIGIT_CHARACTERS
    ]
    assert all(cell.endswith("e0") for cell in code)
    wide = [cell for cell in content if not set(cell) <= CODE_CHARACTERS]
    assert all(cell.endswith(".") for cell in wide)
    assert min(len(cell) for cell in content) == column["min_length"]
    assert max(len(cell) for cell in content) == column["max_length"]


def test_the_bands_come_from_the_counts_and_not_from_the_role() -> None:
    """The same column, published with a different pair of counts.

    Nothing but `n_all_digits` and `n_code_alphabet` moves, and the
    whole band assignment moves with them. Under the withdrawn rule
    neither of these two columns could differ from the other, because
    `all_whole_numbers` alone decided the alphabet.
    """
    facts = {
        "n_present": 12,
        "n_distinct": 12,
        "n_distinct_folded": 12,
        "n_numeric": 12,
        "n_not_numeric": 0,
        "min_length": 3,
        "max_length": 5,
        "all_whole_numbers": True,
        "n_distinct_by_occurrences": {"1": 12},
    }
    figures_only = gen._identifier_content(
        _identifier_column(n_all_digits=12, n_code_alphabet=12, **facts)
    )
    wide_only = gen._identifier_content(
        _identifier_column(n_all_digits=0, n_code_alphabet=0, **facts)
    )
    assert _all_digits(figures_only) == 12
    assert _all_digits(wide_only) == 0
    assert _code_alphabet(figures_only) == 12
    assert _code_alphabet(wide_only) == 0
    assert set(figures_only).isdisjoint(wide_only)


# ------------------------------------------------ the counts are recounted


def test_the_oracle_refuses_the_cells_the_withdrawn_rule_would_have_built() -> None:
    """The recount is only worth what it refuses.

    These are the cells the withdrawn rule produced, held up against
    the counts the case publishes. A recount that accepted them would
    let the oracle publish expected cells that miss an EXACT-OBSERVABLE
    fact, which is the whole defect P2-C2-F7 named.
    """
    column = gen._identifier_whole_numbers()["column"]
    # Every published fact of the case except the two alphabet counts:
    # the multiplicity map, both distinctness counts and both pinned
    # lengths hold, and every cell is a whole number. Only the bands are
    # the withdrawn rule's.
    spellings = ["100", "10000", "101", "102", "103", "104", "105", "106"]
    withdrawn = []
    for group, spelling in zip([1, 1, 1, 1, 2, 2, 2, 2], spellings):
        withdrawn.extend([spelling] * group)
    assert _all_digits(withdrawn) == 12
    with pytest.raises(AssertionError) as refusal:
        gen._identifier_recount(column, withdrawn)
    assert "n_all_digits" in str(refusal.value)
    assert "do not move the published fact" in str(refusal.value)


def test_the_recount_accepts_the_cells_the_construction_builds() -> None:
    """And it is not refusing everything: the real answer passes it."""
    column = gen._identifier_whole_numbers()["column"]
    gen._identifier_recount(column, gen._identifier_content(column))


@pytest.mark.parametrize(
    "text,whole",
    [
        ("100", True),
        ("0e0", True),
        ("00.", True),
        ("+1", True),
        ("-0", True),
        ("12.5", False),
        ("(1)", False),
        ("text-1", False),
        ("", False),
        ("nan", False),
    ],
)
def test_a_cell_reads_back_as_a_whole_number_or_it_does_not(
    text: str, whole: bool
) -> None:
    """`all_whole_numbers` is recounted with the reading a reader takes."""
    assert gen._is_a_whole_number(text) is whole


# ------------------------------------------- the corners it states nothing for


def test_the_one_character_corner_is_refused_rather_than_guessed_at() -> None:
    """The contract's own example of a document whose facts cannot all hold.

    A one-character declared identifier published as whole numbers with
    `n_all_digits` below `n_present`: no single character is both a
    whole number and outside the figures. Method sections G9.6 and G12
    say a shipped run REFUSES generation for that description before any
    cell is built (review item P2-C5-F4), and the oracle freezes no case
    for it either, so it states no expected cells -- a reference vector
    nobody proved is worse than none.
    """
    column = _identifier_column(
        n_present=3,
        n_missing=0,
        n_distinct=3,
        n_distinct_folded=3,
        n_numeric=3,
        n_not_numeric=0,
        min_length=1,
        max_length=1,
        all_whole_numbers=True,
        n_all_digits=1,
        n_code_alphabet=1,
        n_distinct_by_occurrences={"1": 3},
    )
    with pytest.raises(AssertionError) as refusal:
        gen._identifier_content(column)
    # The packing of G9.6 now carries the four class counts beside the
    # two alphabet counts (review item P2-C5-F2), and a length window
    # that no class-and-alphabet pair can be written at narrows the grid
    # to nothing -- so the refusal arrives one step earlier than it did,
    # from the packing rather than from the walk, and says the same
    # thing about the same description.
    assert "cannot all hold at once" in str(refusal.value)
    assert "never about the search" in str(refusal.value)


def test_a_partner_ask_the_domain_cannot_answer_ends_rather_than_running_on() -> None:
    """The walk is bounded, so a corner is a refusal and never a hang.

    A spelling with `L` letters supplies `2**L - 1` partners (G9.3), and
    the whole-number spellings of the band outside the code alphabet
    carry no letter at all, so no round can produce the partners this
    profile asks for. That is owner decision 6's infeasible corner, and
    the oracle names it instead of walking for ever.
    """
    column = _identifier_column(
        all_whole_numbers=True,
        n_all_digits=0,
        n_code_alphabet=0,
        n_distinct_folded=12,
        n_numeric=14,
        n_not_numeric=0,
    )
    with pytest.raises(AssertionError) as refusal:
        gen._identifier_content(column)
    assert "owner decision 6" in str(refusal.value)


# ------------------------------------------------ the packing over the bands


def test_the_alphabet_counts_are_packed_over_whole_groups() -> None:
    """Both counts are counts of CELLS answered for by whole GROUPS (G9.5).

    Groups of 2, 2 and 3 against a figures quota of 4: the rule the
    method calls out as nonconforming -- largest group first -- writes
    5. A complete packing takes the two doubled groups.
    """
    groups = [2, 2, 3]
    quotas = {gen.FIGURES: 4, gen.CODE_BAND: 3, gen.WIDE_BAND: 0}
    column = _identifier_column(
        n_present=7,
        n_all_digits=4,
        n_code_alphabet=7,
        n_numeric=7,
        n_not_numeric=0,
        min_length=3,
        max_length=5,
        all_whole_numbers=True,
    )
    _classes, bands = gen._packed_bands(
        groups, column, gen._class_quotas(column), True, 3, 5
    )
    placed = {band: 0 for band in gen.IDENTIFIER_BANDS}
    for size, band in zip(groups, bands):
        placed[band] += size
    assert placed == quotas


def test_a_packing_that_does_not_exist_is_named_rather_than_approximated() -> None:
    """No assignment of whole groups can meet an odd quota out of even sizes."""
    column = _identifier_column(
        n_present=4,
        n_all_digits=1,
        n_code_alphabet=4,
        n_numeric=4,
        n_not_numeric=0,
        min_length=3,
        max_length=5,
        all_whole_numbers=True,
    )
    with pytest.raises(AssertionError) as refusal:
        gen._packed_bands(
            [2, 2], column, gen._class_quotas(column), True, 3, 5
        )
    assert "cannot all hold at once" in str(refusal.value)


def test_the_smallest_quota_is_answered_for_first() -> None:
    """G9.5 fixes the order so two implementations pack the same way.

    Four singletons against a figures quota of one and a wide quota of
    three: the first cell filled takes the earliest groups, so the
    figures quota -- the smallest -- takes group nought.
    """
    column = _identifier_column(
        n_present=4,
        n_all_digits=1,
        n_code_alphabet=1,
        n_numeric=4,
        n_not_numeric=0,
        min_length=3,
        max_length=5,
        all_whole_numbers=True,
    )
    _classes, bands = gen._packed_bands(
        [1, 1, 1, 1], column, gen._class_quotas(column), True, 3, 5
    )
    assert bands == [gen.FIGURES, gen.WIDE_BAND, gen.WIDE_BAND, gen.WIDE_BAND]


def test_the_band_quotas_are_the_two_published_counts_and_the_remainder() -> None:
    column = gen._identifier_whole_numbers()["column"]
    assert gen._band_quotas(column) == {
        gen.FIGURES: 4,
        gen.CODE_BAND: 4,
        gen.WIDE_BAND: 4,
    }
    with pytest.raises(AssertionError) as refusal:
        gen._band_quotas(dict(column, n_code_alphabet=2))
    assert "cannot both hold" in str(refusal.value)
