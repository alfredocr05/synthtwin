"""The canonical ceiling is not an exact count oracle.

REVIEW ITEM P3-V4-F2, and plan amendment A-P3-10 clause 1. Amendment
A-P3-5 clause 3 ruled that whether a numeric cell's TEXT is a spelling
its own value licenses sits outside V5.1's envelope -- the producer
publishes canonicality about no file at any count, so there is no floor
to appeal to and no window to draw, and withholding it would withhold it
forever. A ruling of that kind is only as good as the BOUND it carries,
and the bound this one stated was one bit per column and nothing a
candidate search can walk.

WHAT WAS ACTUALLY TRUE. `styles.canonical.<form>` compared the exact
count of non-canonical cells -- a number no description of the measured
file publishes -- against the count the SUBMITTED description names, so
the verdict flipped at exactly that number and repeated candidates read
it off one guess at a time. Measured on the shipped code, with a fixed
file holding thirty-seven leading-zero decimal cells: candidate counts
0, 11, 20 and 36 gave MISSED and 37, 38 and 48 gave HELD. And two
measured files holding thirty-six and thirty-seven of them, whose full
descriptions `synthtwin profile` writes BYTE FOR BYTE ALIKE, got HELD
and MISSED.

WHAT IS ASSERTED HERE, AND WHY IT IS THE CLASS AND NOT THE WITNESS. The
witness is one pair at one threshold; the class is the whole map from
the file's hidden count to the report. So the battery holds a file and
walks EVERY candidate count the form can carry, and asserts the map:
the set of candidate counts that MISS is exactly the ones below the
count's own floor-wide block, so what a sweep locates is the block and
never the count. It asserts the same of the other ceilinged form, so a
repair aimed at `decimal` alone is red. It asserts that two files whose
counts share a block are indistinguishable at every threshold, which is
the property the witness is one instance of. And it asserts both edges
of what that costs and keeps: no file inside its licence is ever
accused, and a file one whole floor over it still MISSES, so the
subcheck is not the LISTING V3.4 refuses.

Every table is built at test time by the seeded neutral builders in
`fixtures.py`; no data-format file enters the repository (plan D13).
"""

import json
import pathlib

import pytest

import fixtures
from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

SEED = 20260814
ROWS = 60


def _table(values: "list[str]") -> str:
    """One single-column CSV, written the way the twin writer writes one."""
    return fixtures.single_column_table("amount", values)


def _decimal_cell(index: int) -> str:
    """One cell in the `decimal` form, in its own value's canonical text."""
    return f"{index + 1}.5"


def _exponent_cell(index: int) -> str:
    """One cell in the `exponent_lower` form, canonical for its own value.

    The magnitude is outside G6.2's fixed-point window, which is what
    makes the exponent spelling of these values the CANONICAL one -- an
    ordinary-sized value written `1.5e+00` is already non-canonical, so
    a column of those would have every one of its cells odd whatever
    else the fixture did, and the count this battery varies would not be
    the count it thinks it is. It is the SMALL side of the window
    rather than the large one, because a value of `1.5e+20` is a WHOLE
    number: a column of those publishes `integer_valued: true`, the
    canonical spelling of every one of them is then its digits in full,
    and every exponent cell is odd again for the other reason. The text
    is taken from the value rather than written out, so it is canonical
    by construction.
    """
    return repr((index + 1.5) * 1e-20)


_SPELLINGS = {
    parsing.STYLE_DECIMAL: _decimal_cell,
    parsing.STYLE_EXPONENT_LOWER: _exponent_cell,
}


def _built(
    shaped: int, odd: int, style: str = parsing.STYLE_DECIMAL
) -> str:
    """A sixty-row column: `shaped` cells in the form, `odd` of them odd.

    The first ``odd`` cells of the form carry a leading zero, which
    method G6.3 makes a spelling of the very same value inside the very
    same form and which the contract's own ladder still counts as that
    form. So the file's count of cells IN the form does not move with
    ``odd`` and its count of NON-CANONICAL ones is exactly ``odd``. The
    remaining cells are whole numbers written point-free, which is what
    keeps the published count of the form below the row count and the
    ceiling therefore an executable subcheck at all.
    """
    spell = _SPELLINGS[style]
    values: list[str] = []
    for index in range(ROWS):
        if index < shaped:
            body = spell(index)
            if index < odd:
                body = f"0{body}"
        else:
            body = f"{index + 1}"
        values = values + [body]
    return _table(values)


def _describe(
    folder: pathlib.Path, text: str, stem: str
) -> contract.Profile:
    """Profile one table through the real producer and the strict loader."""
    table_path = fixtures.write(folder, f"{stem}.csv", text)
    read = reading.read_table(
        str(table_path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(read, taxonomy.Settings(), [])
    written = fixtures.write_profile(folder, f"{stem}-profile.json", document)
    return contract.load_profile(str(written))


def _own_description(
    folder: pathlib.Path,
    described: contract.Profile,
    text: str,
    stem: str,
) -> str:
    """What `synthtwin profile` publishes about THIS file, as bytes.

    Built with the validator's own reconstructed settings, which is what
    V5.1 names: the file's own description, under the profile's settings.
    """
    table_path = fixtures.write(folder, f"{stem}.csv", text)
    read = reading.read_table(
        str(table_path), first_row=reading.FIRST_ROW_NAMES
    )
    document = profile.build_document(
        read, validation.settings_for(described), []
    )
    return json.dumps(document, sort_keys=True, default=str)


def _report(
    folder: pathlib.Path,
    described: contract.Profile,
    text: str,
) -> "tuple[tuple[object, ...], validation.Census]":
    """Every verdict of one run, under a name that does not move.

    The measured file's NAME is an input to the report (V7.1-A1), so it
    is held equal on every side of every comparison here.
    """
    target = fixtures.write(folder, "measured.csv", text)
    outcome = validation.measure(described, str(target))
    return (
        tuple(
            (
                check.column,
                check.fact,
                check.subcheck,
                check.verdict,
                check.published,
                check.achieved,
                check.citation,
            )
            for check in outcome.checks
        ),
        outcome.census,
    )


def _verdict(
    folder: pathlib.Path,
    described: contract.Profile,
    text: str,
    subcheck: str,
) -> "str | None":
    """The one verdict filed under ``subcheck``, or None where it is absent."""
    target = fixtures.write(folder, "measured.csv", text)
    outcome = validation.measure(described, str(target))
    found = [
        check.verdict for check in outcome.checks if check.subcheck == subcheck
    ]
    assert len(found) <= 1, (subcheck, found)
    return found[0] if found else None


def _published(described: contract.Profile, style: str) -> int:
    """What the candidate publishes for one form."""
    facts = described.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    return facts.numeric_styles.get(style, 0)


# The two forms P3-D8.1's ceiling is filed against. Both are walked by
# every property below, because a repair aimed at the form the review
# named would leave the other open.
_FORMS = tuple(sorted(_SPELLINGS))

# The candidate counts a sweep may ask for. A form used by fewer cells
# than the publication floor is NEVER named in a description -- it is
# pooled, and the candidate then publishes nothing about it -- so the
# thresholds a candidate can really carry are zero and the numbers from
# the floor upwards. Asking for four would build a description
# publishing none, and the sweep would be probing a threshold nobody
# can submit.
_THRESHOLDS = (0, 11, 15, 20, 25, 30, 33, 36, 40, 44, 48)


@pytest.fixture(scope="module")
def floor() -> int:
    """The publication floor every description here is written under."""
    return taxonomy.Settings().small_cell_floor


# -- the witness ------------------------------------------------------


def test_two_files_the_producer_describes_alike_get_one_report(
    tmp_path: pathlib.Path,
) -> None:
    """The review's own witness, at its own threshold.

    Thirty-six and thirty-seven non-canonical decimal spellings in a
    file of forty-eight decimal cells: the producer writes one
    description for both, and a candidate holding thirty-six used to
    separate them. The precondition is measured rather than assumed.
    """
    folder = tmp_path / "witness"
    folder.mkdir()
    thirty_six, thirty_seven = _built(48, 36), _built(48, 37)
    candidate = _describe(folder, _built(36, 0), "candidate")
    assert _published(candidate, parsing.STYLE_DECIMAL) == 36
    assert _own_description(folder, candidate, thirty_six, "own-a") == (
        _own_description(folder, candidate, thirty_seven, "own-b")
    ), "the premise of the finding: one description, two files"
    first = _report(folder, candidate, thirty_six)
    second = _report(folder, candidate, thirty_seven)
    assert first[1] == second[1], (
        "two files `synthtwin profile` describes byte for byte alike got "
        "different censuses"
    )
    assert first[0] == second[0], (
        "two files `synthtwin profile` describes byte for byte alike got "
        "different verdicts, so the ceiling still tells them apart (V5.3)"
    )


# -- the class: the whole map from the hidden count to the report -----


@pytest.mark.parametrize("style", _FORMS)
def test_no_candidate_sweep_reads_the_count_off_the_ceiling(
    tmp_path: pathlib.Path, floor: int, style: str
) -> None:
    """The class: hold the file, sweep every threshold, read the map.

    A candidate description is a file, so the sweep builds each one by
    profiling a table that really carries that many cells of the form --
    which is what keeps the attack honest about what can be asked. The
    assertion is not "the flip point moved" but WHERE it is: exactly the
    count's own floor-wide block, so the sweep locates the block and the
    count itself is never separated from the ten others beside it.
    """
    folder = tmp_path / f"sweep-{style}"
    folder.mkdir()
    odd = 37
    measured = _built(48, odd, style)
    missed: list[int] = []
    for threshold in _THRESHOLDS:
        candidate = _describe(
            folder, _built(threshold, 0, style), f"c{threshold}"
        )
        assert _published(candidate, style) == threshold, threshold
        got = _verdict(
            folder, candidate, measured, f"styles.canonical.{style}"
        )
        assert got is not None, threshold
        if got == validation.MISSED:
            missed = missed + [threshold]
    block = validation._at_the_floors_resolution(odd, floor)
    assert block < odd, (
        "the floor is rounding nothing, so nothing is hidden and this "
        "battery would prove nothing"
    )
    assert missed == [
        threshold for threshold in _THRESHOLDS if threshold < block
    ], (
        "the candidate sweep flips somewhere other than the count's own "
        "floor-wide block, so a sequence of candidate descriptions still "
        "reads a number off this subcheck that no description of the "
        "measured file publishes (V5.3)"
    )
    # ...and what the flip point is NOT: the count itself, which is what
    # the shipped version handed back. A candidate naming FEWER cells
    # than the file holds non-canonical ones still reads HELD, which no
    # exact comparison against that candidate's number can do.
    below = [
        threshold
        for threshold in _THRESHOLDS
        if threshold < odd and threshold not in missed
    ]
    assert below, (
        "every candidate publishing fewer than the file's own count of "
        "non-canonical cells MISSES, so the flip point IS that count and "
        "a sweep reads it exactly"
    )


@pytest.mark.parametrize("style", _FORMS)
def test_every_count_inside_one_floor_block_gets_one_report(
    tmp_path: pathlib.Path, floor: int, style: str
) -> None:
    """The property the witness is one instance of.

    Two files whose non-canonical counts share a floor-wide block are
    the same file as far as every candidate description can tell. The
    ends of the block and a count inside it are crossed with thresholds
    on both sides of it, so a repair that moved the block's edge without
    moving its width would be red.
    """
    folder = tmp_path / f"block-{style}"
    folder.mkdir()
    low = floor * 3
    inside = [low, low + 1, low + floor - 1]
    for threshold in (0, low - 1, low, low + floor - 1, 48):
        candidate = _describe(
            folder, _built(threshold, 0, style), f"c{threshold}"
        )
        first = _report(folder, candidate, _built(48, inside[0], style))
        for count in inside[1:]:
            other = _report(folder, candidate, _built(48, count, style))
            assert first == other, (
                f"a file holding {inside[0]} non-canonical cells and one "
                f"holding {count} of them -- the same floor-wide block -- "
                f"get different reports against a candidate publishing "
                f"{threshold}"
            )


# -- the two edges: what it keeps, and what it costs ------------------


@pytest.mark.parametrize("style", _FORMS)
def test_the_ceiling_never_accuses_a_file_inside_its_licence(
    tmp_path: pathlib.Path, style: str
) -> None:
    """Rounding DOWN is the direction that cannot accuse a conforming file.

    The result is never more than the count, so a MISSED here is a file
    genuinely over its licence, and a file at or under it is HELD
    whatever the floor is. Crossed over the whole range rather than
    checked at one point.
    """
    folder = tmp_path / f"inside-{style}"
    folder.mkdir()
    for threshold in (11, 24, 36, 48):
        candidate = _describe(
            folder, _built(threshold, 0, style), f"c{threshold}"
        )
        for odd in (0, threshold // 2, threshold):
            got = _verdict(
                folder,
                candidate,
                _built(48, odd, style),
                f"styles.canonical.{style}",
            )
            assert got == validation.HELD, (threshold, odd, got)


@pytest.mark.parametrize("style", _FORMS)
def test_the_ceiling_still_misses_a_file_a_floor_over_its_licence(
    tmp_path: pathlib.Path, floor: int, style: str
) -> None:
    """V3.4: what is kept, so the repair is not a silence.

    A subcheck that could never report MISSED on any file is the vacuity
    V3.4 refuses by name, and turning this one into that is the
    alternative amendment A-P3-10 clause 1 prices and does not take. One
    whole floor over the licence still misses, on both ceilinged forms.
    """
    folder = tmp_path / f"teeth-{style}"
    folder.mkdir()
    for threshold in (0, 11, 24):
        candidate = _describe(
            folder, _built(threshold, 0, style), f"c{threshold}"
        )
        over = threshold + floor
        got = _verdict(
            folder,
            candidate,
            _built(48, over, style),
            f"styles.canonical.{style}",
        )
        assert got == validation.MISSED, (threshold, over, got)


def test_one_cell_over_the_licence_is_the_cost_and_it_is_recorded(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """The cost, pinned so it cannot grow quietly.

    Teeth at ONE cell over the licence and a bound better than the exact
    count are mutually exclusive: the licence is a number the submitted
    description chooses, so a verdict separating `odd == p` from
    `odd == p + 1` for every `p` IS the oracle. A-P3-10 clause 1 records
    that a file between one cell and one floor over its licence is no
    longer missed here, and this is the file.
    """
    folder = tmp_path / "cost"
    folder.mkdir()
    candidate = _describe(folder, _built(24, 0), "candidate")
    assert _published(candidate, parsing.STYLE_DECIMAL) == 24
    got = _verdict(
        folder, candidate, _built(48, 25), "styles.canonical.decimal"
    )
    assert got == validation.HELD
    # ...and the file is not silently forgiven everywhere: the cells it
    # over-spends the licence on are cells of a form, and how many cells
    # wear each form is published, floored and still answered for.
    target = fixtures.write(folder, "measured.csv", _built(48, 25))
    outcome = validation.measure(candidate, str(target))
    answered = {
        check.subcheck for check in outcome.checks if check.subcheck.startswith("styles.")
    }
    assert f"styles.at-least.{parsing.STYLE_DECIMAL}" in answered
    assert "styles.spelled" in answered


# -- the green direction ----------------------------------------------


def test_a_twin_of_its_own_description_keeps_every_ceiling(
    tmp_path: pathlib.Path,
) -> None:
    """The shipped generator's own output is not accused by the repair.

    The repair moves a verdict only in the forgiving direction, so this
    can only stay green -- which is exactly why it is here: a future
    change that made the ceiling stricter to buy its teeth back would
    reject a file `synthtwin generate` wrote, and that is the fault
    amendment A-P3-9 clause 1 exists for.
    """
    folder = tmp_path / "twin"
    folder.mkdir()
    described = _describe(folder, _built(24, 0), "described")
    twin = rendering.twin_csv(generation.generate(described, SEED))
    target = fixtures.write(folder, "twin.csv", twin)
    outcome = validation.measure(described, str(target))
    missed = [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    ]
    assert missed == []
    ceilings = [
        check.verdict
        for check in outcome.checks
        if check.subcheck.startswith("styles.canonical.")
    ]
    assert ceilings and set(ceilings) == {validation.HELD}


# -- the rule itself, in arithmetic -----------------------------------


def test_the_floors_resolution_is_a_block_map_that_never_overstates() -> None:
    """The two properties every verdict above rests on, over a grid.

    Never more than the count -- which is what makes a MISSED honest --
    and constant on each floor-wide block -- which is what makes the
    bound the amendment states true. A floor of one is the identity and
    is asserted as such rather than left as a corner.
    """
    for size in (1, 2, 5, 11, 25):
        for count in range(60):
            found = validation._at_the_floors_resolution(count, size)
            assert 0 <= found <= count
            assert found == count - count % size if size > 1 else found == count
        if size > 1:
            blocks = {
                count // size: {
                    validation._at_the_floors_resolution(inner, size)
                    for inner in range(count // size * size, count // size * size + size)
                }
                for count in range(60)
            }
            for held in blocks.values():
                assert len(held) == 1
