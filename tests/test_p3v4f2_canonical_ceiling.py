"""The canonical ceiling misses at one cell again (amendment A-P3-13).

Owner ruling of 2026-08-14, put as a question: should the validator
defend against someone submitting hand-crafted descriptions to extract
hidden numbers? The ruling was no -- say so honestly instead. Plan
amendment A-P3-13 carries it, the validation method carries it as V5-A1,
and this file is the one place in the suite where the ruling BUYS
something rather than costing it.

WHAT THIS FILE USED TO HOLD, AND WHY IT DOES NOT. Amendment A-P3-5
clause 3 ruled that whether a numeric cell's TEXT is a spelling its own
value licenses sits outside V5.1's envelope: the producer's own form
ladder discards it, so it publishes canonicality about no file at any
count, there is no floor to appeal to and no window to draw, and
withholding it would withhold it on every file forever. Two files that
description cannot tell apart therefore get different verdicts at THIS
subcheck by ruling, and always did. What amendment A-P3-10 clause 1
added on top was a bound against a different reader -- a person trying
one candidate description after another -- by rounding the recount DOWN
to a whole number of publication floors before the comparison. That is
the reader the owner has now put out of scope, so the rounding is gone,
`_at_the_floors_resolution` is deleted, and the teeth A-P3-10 clause 1
priced in one sentence are back:

    "A file between ONE cell and one floor over its licence is no
    longer missed at this subcheck."

WHAT IS ASSERTED HERE:

* a file ONE cell over its licence MISSES, on both ceilinged forms --
  the sentence above, run;
* every count inside one floor-wide block of the licence misses, so the
  recovered teeth are counted rather than sampled at one point;
* no file inside its licence is ever accused, and the twin the shipped
  generator writes from a description keeps every ceiling -- the repair
  moves verdicts in one direction only;
* the subcheck prints no measured count on any file, which is the half
  of A-P3-5 clause 3's bound that is still owed and is what a reader of
  ONE report is protected by;
* the POOLED side is untouched: which of the six forms a cell wears is
  published and floored, so a form the file's own description pools is
  still settled against the room that description leaves and never
  against the recount;
* and the rounding cannot come back by accident: `validation` carries no
  function that reads a recount at the floor's resolution.

THE RED CHECK. `REINSTATE=A-P3-13` in the environment puts the rounded
comparison back before every test in this file, exactly as it stood --
the pre-amendment code rounded once and used the rounded number in both
branches, so rounding the recount itself restores it. Measured on the
commit that adds this file: **4 of the 11 fail**, which is every test
carrying the recovered teeth on both ceilinged forms, and none of the
others, because the change moves no verdict the other way and prints
nothing new. The structural guard has its own red, because a monkeypatch
does not restore a deleted function: defining
`validation._at_the_floors_resolution` in memory -- which is the first
half of the reversal the amendment records -- fails it, measured.

Every table is built at test time by the seeded neutral builders in
`fixtures.py`; no data-format file enters the repository (plan D13).
"""

import os
import pathlib

import pytest

import fixtures
from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    quality,
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


# -- the red check -----------------------------------------------------


_THE_ROUNDING_AS_IT_STOOD = validation._noncanonical_cells


def _rounded_to_the_floor(
    cells: "list[str]", style: str, integer_valued: bool
) -> int:
    """The recount as amendment A-P3-10 clause 1 let a verdict see it.

    The code this restores rounded once, into a local the named branch
    and the pooled branch both read, so rounding the recount itself is
    the same program. The floor is the default one because every
    description in this file is written under it -- `_describe` runs the
    shipped producer with `taxonomy.Settings()` and changes nothing --
    and a reinstatement that guessed a different floor would not be the
    rule it claims to restore.
    """
    floor = taxonomy.Settings().small_cell_floor
    found = _THE_ROUNDING_AS_IT_STOOD(cells, style, integer_valued)
    if floor <= 1:
        return found
    return floor * (found // floor)


@pytest.fixture(autouse=True)
def _reinstated(monkeypatch: pytest.MonkeyPatch) -> None:
    """Put the withdrawn rounding back when REINSTATE asks for it."""
    if os.environ.get("REINSTATE") == "A-P3-13":
        monkeypatch.setattr(
            validation, "_noncanonical_cells", _rounded_to_the_floor
        )


# -- helpers -----------------------------------------------------------


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


def _verdict(
    folder: pathlib.Path,
    described: contract.Profile,
    text: str,
    subcheck: str,
) -> "str | None":
    """The one verdict filed under ``subcheck``, or None where it is absent.

    The measured file's NAME is an input to the report (V7.1-A1), so it
    is held equal on every side of every comparison here.
    """
    target = fixtures.write(folder, "measured.csv", text)
    outcome = validation.measure(described, str(target))
    found = [
        check.verdict for check in outcome.checks if check.subcheck == subcheck
    ]
    assert len(found) <= 1, (subcheck, found)
    return found[0] if found else None


def _published(described: contract.Profile, style: str) -> int:
    """What the description publishes for one form."""
    facts = described.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    return facts.numeric_styles.get(style, 0)


# The two forms P3-D8.1's ceiling is filed against. Both are walked by
# every property below, because a repair aimed at the form the review
# named would leave the other open.
_FORMS = tuple(sorted(_SPELLINGS))


@pytest.fixture(scope="module")
def floor() -> int:
    """The publication floor every description here is written under."""
    return taxonomy.Settings().small_cell_floor


# -- what the ruling buys back ----------------------------------------


@pytest.mark.parametrize("style", _FORMS)
def test_one_cell_over_the_licence_misses(
    tmp_path: pathlib.Path, style: str
) -> None:
    """The sentence amendment A-P3-10 clause 1 priced, run.

    "A file between ONE cell and one floor over its licence is no longer
    missed at this subcheck" was the cost of a defence against a person
    who writes the descriptions. The owner ruled that person out of
    scope, so this is the file and this is its verdict.
    """
    folder = tmp_path / f"one-{style}"
    folder.mkdir()
    described = _describe(folder, _built(24, 0, style), "described")
    assert _published(described, style) == 24
    got = _verdict(
        folder, described, _built(48, 25, style), f"styles.canonical.{style}"
    )
    assert got == validation.MISSED, (
        "a file one cell over its licence is not missed, so the teeth "
        "amendment A-P3-13 clause 2 buys back are not there"
    )


@pytest.mark.parametrize("style", _FORMS)
def test_every_count_inside_one_block_of_the_licence_misses(
    tmp_path: pathlib.Path, floor: int, style: str
) -> None:
    """The teeth, counted rather than sampled.

    A whole floor-wide block sat under one verdict while the recount was
    read at the floor's resolution: eleven counts over the licence, all
    of them HELD. Every one of them misses now, which is what "at one
    cell" means when it is measured instead of asserted.
    """
    folder = tmp_path / f"block-{style}"
    folder.mkdir()
    licence = 24
    described = _describe(folder, _built(licence, 0, style), "described")
    assert _published(described, style) == licence
    verdicts = {
        odd: _verdict(
            folder,
            described,
            _built(48, odd, style),
            f"styles.canonical.{style}",
        )
        for odd in range(licence + 1, licence + floor + 1)
    }
    assert set(verdicts.values()) == {validation.MISSED}, verdicts
    assert len(verdicts) == floor


# -- the direction it may not move ------------------------------------


@pytest.mark.parametrize("style", _FORMS)
def test_the_ceiling_never_accuses_a_file_inside_its_licence(
    tmp_path: pathlib.Path, style: str
) -> None:
    """The exact comparison can only miss files that are over.

    The withdrawn rounding was never more than the count, so every file
    it held is a file the exact comparison holds too. Crossed over the
    range rather than checked at one point, because this is the property
    that makes the change one-directional.
    """
    folder = tmp_path / f"inside-{style}"
    folder.mkdir()
    for threshold in (11, 24, 36, 48):
        described = _describe(
            folder, _built(threshold, 0, style), f"c{threshold}"
        )
        for odd in (0, threshold // 2, threshold):
            got = _verdict(
                folder,
                described,
                _built(48, odd, style),
                f"styles.canonical.{style}",
            )
            assert got == validation.HELD, (threshold, odd, got)


def test_a_twin_of_its_own_description_keeps_every_ceiling(
    tmp_path: pathlib.Path,
) -> None:
    """The shipped generator's own output is not accused by the repair.

    A conforming twin's recount is at most its licence, so a stricter
    comparison cannot reach it -- and this is where that is checked
    rather than reasoned about, because rejecting a file `synthtwin
    generate` wrote is the fault amendment A-P3-9 clause 1 exists for.
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


# -- what one report still may not say --------------------------------


def test_the_ceiling_prints_no_measured_count_on_any_file(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """The half of A-P3-5 clause 3's bound that is still owed.

    V5-A1 gives up the defence against a person who chooses the
    descriptions; it gives up nothing about what ONE report says, and
    this subcheck's line carries the licence and the verdict and never
    the recount. Asserted on the check itself AND on the written report,
    over a file whose hidden count is a number that appears nowhere else
    in the run, so a leak would have to spell it out to pass.
    """
    folder = tmp_path / "printed"
    folder.mkdir()
    described = _describe(folder, _built(24, 0), "described")
    hidden = 37
    target = fixtures.write(folder, "measured.csv", _built(48, hidden))
    outcome = validation.measure(described, str(target))
    for check in outcome.checks:
        if check.subcheck.startswith("styles.canonical."):
            assert check.achieved == "", check
    report = quality.quality_report(described, outcome)
    for line in report.splitlines():
        if "canonical" in line:
            assert str(hidden) not in line, line


@pytest.mark.parametrize("style", _FORMS)
def test_a_pooled_form_is_still_settled_against_the_room_it_leaves(
    tmp_path: pathlib.Path, floor: int, style: str
) -> None:
    """Which of the six FORMS a cell wears is published, floored and gated.

    A MISSED against the recount on a form the file's own description
    POOLS would put a lower bound on that form's count in ONE report,
    and that count is inside V5.1's envelope. So the pooled side never
    consults the recount: it holds where the room the description leaves
    cannot reach the licence and withholds otherwise, and it never
    misses. Nothing in amendment A-P3-13 reaches it.
    """
    folder = tmp_path / f"pooled-{style}"
    folder.mkdir()
    described = _describe(folder, _built(48, 0, style), "described")
    assert _published(described, style) == 48
    under = floor - 1
    got = _verdict(
        folder,
        described,
        _built(under, under, style),
        f"styles.canonical.{style}",
    )
    assert got in (validation.HELD, validation.WITHHELD), got


def test_no_verdict_path_reads_a_recount_at_the_floors_resolution() -> None:
    """The withdrawn defence cannot come back unnoticed.

    `_at_the_floors_resolution` is deleted rather than left unused
    (amendment A-P3-13 clause 2), so a later reader cannot take it for a
    rule still in force and a later edit cannot quietly call it again.
    """
    assert not hasattr(validation, "_at_the_floors_resolution"), (
        "the rounding amendment A-P3-13 withdrew is back in the module"
    )
