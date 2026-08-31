"""Residual R-P4-53: a hole spelled as a number was counted by the recount.

A description publishes its style census over the cells IT counts as
values. The validator's style clauses do not read that census back off a
re-description -- they RECOUNT the written cells -- and the recount
walked every non-blank cell that reads as a number. On a column whose
"no value" word is `-9.99` those are two different sets: the description
counts 180, the recount finds 200, and THE FILE THE DESCRIPTION WAS
WRITTEN FROM was told it missed `numeric.numeric_styles`.

A false verdict on a correct file is the worst class of defect this
project has, because a person acts on it. The register's own witness is
the first case below.

WHAT THE FIX IS. Each side of `_governed` now recounts the cells ITS OWN
reading counts as values -- the gated side under the file's own
description, the measured side under the description taken over the
blank/non-blank split -- so the recount and the census it is compared
with stand over one population.

WHICH CASE PINS WHICH HALF, because the two halves are separately
revertible and a guard that only catches one of them is half a guard:

- the style subchecks of a plain numeric column and of an affixed
  column's cores are named in `_MEASURED_FROM_THE_CELLS`, so `_governed`
  takes the GATED side's verdict. Those cases turn red when the gated
  half is reverted.
- a joined position's style subchecks carry the position in their name,
  so they are not in that tuple and `_governed` takes the MEASURED
  side's verdict wherever the split is published. That case turns red
  when the measured half is reverted.

AND THE WIDTH THE REGISTER STATES IS ASSERTED RATHER THAN TRUSTED. It
does not reach every column whose hole happens to be numeric: 180 copies
of a label beside twenty declared `-9.99` cells make a CONSTANT column,
which publishes no style census, so no recount runs. The last case below
holds that boundary, and it holds it by asserting the column really is
the role the register names.

Every table is built here by a seeded neutral builder; no data-format
file enters the repository (plan D13).
"""

import pathlib
import random

import pytest

import fixtures
from synthtwin import (
    contract,
    parsing,
    profile,
    reading,
    taxonomy,
    validation,
)

# THE FLOOR IS ONE, which is the shipped default (amendment A-P4-37) and
# is what makes these cases say something: at a floor of one nothing is
# pooled, every count the report compares is published exactly, and a
# withholding is therefore a report going quiet about a fact its own
# description names. Raise the floor and the withholdings would be
# honest ones.
_FLOOR = 1

_ROWS = 200
_HOLES = 20


def _decimals(seed: int, count: int) -> "list[str]":
    """Ordinary two-place readings, none of them a stand-in number."""
    spread = random.Random(seed)
    return [f"{spread.uniform(1.0, 90.0):.2f}" for _each in range(count)]


def _shuffled(seed: int, rows: "list[str]") -> "list[str]":
    spread = random.Random(seed)
    order = list(rows)
    spread.shuffle(order)
    return order


def _numeric_table(hole: str, seed: int = 20260831) -> str:
    """180 readings and twenty holes, all spelled `hole`."""
    rows = _decimals(seed, _ROWS - _HOLES) + [hole] * _HOLES
    return fixtures.single_column_table("reading", _shuffled(seed, rows))


def _joined_table(hole: str, seed: int = 20260902) -> str:
    """180 two-position readings and twenty holes, all spelled `hole`."""
    spread = random.Random(seed)
    rows = [
        f"{spread.randint(90, 180)}/{spread.randint(50, 89)}"
        for _each in range(_ROWS - _HOLES)
    ]
    return fixtures.single_column_table(
        "pressure", _shuffled(seed, rows + [hole] * _HOLES)
    )


def _affixed_table(hole: str, seed: int = 20260903) -> str:
    """180 affixed readings and twenty holes, all wearing the pair."""
    rows = [f"EUR {one}" for one in _decimals(seed, _ROWS - _HOLES)]
    return fixtures.single_column_table(
        "price", _shuffled(seed, rows + [hole] * _HOLES)
    )


def _constant_table(hole: str, seed: int = 20260831) -> str:
    """180 copies of one label and twenty holes spelled as a number."""
    rows = ["A"] * (_ROWS - _HOLES) + [hole] * _HOLES
    return fixtures.single_column_table("grade", _shuffled(seed, rows))


def _blank_for(hole: str, text: str) -> str:
    """The same table with every hole cell written as an empty field.

    A blank is absent under BOTH readings, so this is the same table with
    the disagreement taken out of it. It is the control every case is
    read against: whatever these files are told, the blank one must be
    told the same.
    """
    lines = text.split("\n")
    kept = [lines[0]]
    for line in lines[1:]:
        kept = kept + ['""' if line == hole else line]
    return "\n".join(kept)


def _run(
    folder: pathlib.Path,
    stem: str,
    text: str,
    settings: taxonomy.Settings,
    measured: "list[str] | None" = None,
) -> "tuple[dict[str, object], validation.Outcome]":
    """Profile one table, then check THAT SAME FILE against its own description.

    Through the real reader, the real producer, the strict loader and the
    real `validation.measure` -- the four the residual names. The file
    handed to the check is the file the description was written from, so
    every obligation it sets is an obligation that file meets by
    construction.
    """
    path = fixtures.write(folder, f"{stem}.csv", text)
    table = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(
        table, settings, [], None, measured, None
    )
    written = fixtures.write_profile(folder, f"{stem}-profile.json", document)
    described = contract.load_profile(str(written))
    return document, validation.measure(described, str(path))


def _verdicts(
    outcome: "validation.Outcome", verdict: str
) -> "list[validation.Check]":
    return [one for one in outcome.checks if one.verdict == verdict]


def _named(checks: "list[validation.Check]") -> "list[str]":
    return sorted(f"{one.subcheck} [{one.fact}]" for one in checks)


# Each case: its name, the hole spelling, the table builder, the
# settings the description is written under, and the columns declared as
# measurements. The declaration is passed the way the command line
# passes it, so what is described here is what a person's run describes.
_CASES = (
    (
        "declared-number",
        "-9.99",
        _numeric_table,
        taxonomy.Settings(
            small_cell_floor=_FLOOR, declared_missing_values=("-9.99",)
        ),
        None,
    ),
    (
        "judged-stand-in",
        "-999",
        _numeric_table,
        taxonomy.Settings(small_cell_floor=_FLOOR),
        None,
    ),
    (
        "joined-positions",
        "-1/-1",
        _joined_table,
        taxonomy.Settings(
            small_cell_floor=_FLOOR, declared_missing_values=("-1/-1",)
        ),
        ["pressure"],
    ),
    (
        "affixed-cores",
        "EUR 0.00",
        _affixed_table,
        taxonomy.Settings(
            small_cell_floor=_FLOOR, declared_missing_values=("EUR 0.00",)
        ),
        None,
    ),
)


@pytest.mark.parametrize(
    ("case", "hole", "build", "settings", "measured"),
    _CASES,
    ids=[one[0] for one in _CASES],
)
def test_the_file_that_was_described_is_not_told_it_missed(
    tmp_path: pathlib.Path,
    case: str,
    hole: str,
    build: object,
    settings: taxonomy.Settings,
    measured: "list[str] | None",
) -> None:
    """No verdict moves because a hole is spelled as a number.

    Two files, one control: the table with its holes spelled `hole`, and
    the same table with those cells written blank. A blank is absent
    under both readings, so the blank file is what a correct report looks
    like -- and the spelled file, being equally the file its own
    description was written from, owes exactly the same report.

    Asserted as a comparison rather than as a bare "nothing missed", so
    the case cannot pass by both files going quiet.
    """
    folder = tmp_path / case
    folder.mkdir()
    spelled = build(hole)  # type: ignore[operator]
    _document, outcome = _run(
        folder, "spelled", spelled, settings, measured
    )
    _blank_document, control = _run(
        folder, "blank", _blank_for(hole, spelled), settings, measured
    )

    assert not _named(_verdicts(control, validation.MISSED))
    assert not _named(_verdicts(control, validation.WITHHELD))

    assert _named(_verdicts(outcome, validation.MISSED)) == [], (
        "the file the description was written from was told it missed an "
        "obligation, and the same file with its holes written blank was "
        "told it missed none -- so the miss is about how the hole is "
        "SPELLED and not about anything the file holds (R-P4-53)"
    )
    assert _named(_verdicts(outcome, validation.WITHHELD)) == [], (
        "the report went quiet about obligations its own description "
        "publishes exactly, because a hole spelled as a number widened "
        "the room the recount is settled against (R-P4-53)"
    )
    # AND NOT BY GOING QUIET IN SOME OTHER WAY. The two files do not owe
    # the same NUMBER of obligations -- the spelled one publishes the
    # spelling of its holes and the blank one publishes a blank count --
    # so the spelled file owes at least what the control owes and never
    # fewer, and an equality here would be asserting the wrong thing.
    assert len(_verdicts(outcome, validation.HELD)) >= len(
        _verdicts(control, validation.HELD)
    )


def test_the_two_populations_really_do_disagree(
    tmp_path: pathlib.Path,
) -> None:
    """The disagreement the residual is about, stated in numbers.

    Without this the case above could pass because the recount and the
    description happen to see the same cells, which would make it a test
    of nothing. So the gap is asserted: the description publishes its
    style census over 180 present cells while 200 of the file's cells are
    non-blank and read as numbers.
    """
    settings = taxonomy.Settings(
        small_cell_floor=_FLOOR, declared_missing_values=("-9.99",)
    )
    text = _numeric_table("-9.99")
    document, outcome = _run(tmp_path, "witness", text, settings)
    block = document["columns"][0]
    assert isinstance(block, dict)

    assert block["role"] == taxonomy.ROLE_CONTINUOUS
    assert block["n_present"] == _ROWS - _HOLES
    assert block["n_missing"] == _HOLES
    assert block["missing_by_source"] == {"-9.99": _HOLES}
    assert block["numeric_styles"] == {parsing.STYLE_DECIMAL: _ROWS - _HOLES}

    written = 0
    for line in text.split("\n")[1:]:
        body = parsing.trimmed(line)
        if body and parsing.classify_number(body) == parsing.NUMBER:
            written = written + 1
    assert written == _ROWS, (
        "the witness no longer holds a hole that reads as a number, so it "
        "cannot show the disagreement this residual is about"
    )
    assert not _verdicts(outcome, validation.MISSED)


def test_the_repaired_check_still_bites(tmp_path: pathlib.Path) -> None:
    """A narrower population must not be a check with nothing left to do.

    Everything above asserts that a CORRECT file is not failed. Half a
    repair would satisfy all of it by making the style clauses stop
    reaching a verdict at all, and this project has produced that shape
    before -- so the other direction is asserted here on the same
    witness's description.

    A perturbation that proved NOTHING is recorded rather than dropped:
    `+51.71` and `051.71` are both the DECIMAL form to
    `parsing.numeric_style`, so a file rewritten either way is described
    byte for byte alike and there is nothing for a check to catch. Both
    were tried first and both came back with no miss, which is the right
    answer and not a gap. The exponent form is what actually moves the
    census.
    """
    settings = taxonomy.Settings(
        small_cell_floor=_FLOOR, declared_missing_values=("-9.99",)
    )
    text = _numeric_table("-9.99")
    document, honest = _run(tmp_path, "honest", text, settings)
    block = document["columns"][0]
    assert isinstance(block, dict)
    assert not _verdicts(honest, validation.MISSED)

    path = fixtures.write(tmp_path, "honest.csv", text)
    described = contract.load_profile(
        str(tmp_path / "honest-profile.json")
    )

    def perturbed(name: str, change) -> "list[str]":
        lines = text.split("\n")
        built = [lines[0]]
        for line in lines[1:]:
            built = built + [change(line) if line else line]
        written = fixtures.write(tmp_path, name, "\n".join(built))
        assert written.read_text(encoding="utf-8") != path.read_text(
            encoding="utf-8"
        )
        return _named(
            _verdicts(
                validation.measure(described, str(written)), validation.MISSED
            )
        )

    def exponent(one: str) -> str:
        if one == "-9.99" or "." not in one:
            return one
        return f"{float(one):e}"

    def widened(one: str) -> str:
        if one == "-9.99" or "." not in one:
            return one
        return f"{float(one):.3f}"

    missed = perturbed("exponent.csv", exponent)
    assert "styles.at-least.decimal [numeric.numeric_styles]" in missed, missed
    assert (
        "styles.published.decimal [numeric.numeric_styles]" in missed
    ), missed

    missed = perturbed("widened.csv", widened)
    assert "styles.spelled [numeric.numeric_styles]" in missed, missed
    assert "widths.published.2 [numeric.fraction_widths]" in missed, missed

    # AND THE HOLE SPELLING IS STILL AN OBLIGATION. Dropping it for a
    # blank moves no other count -- the cell stays absent -- so this is
    # the one obligation the perturbation can reach, and the narrowed
    # population must not have taken it with it.
    missed = perturbed(
        "dropped.csv", lambda one: '""' if one == "-9.99" else one
    )
    assert missed == [
        "holes.by_source.-9.99 [universal.missing_by_source]"
    ], missed


def test_the_width_stops_where_the_register_says_it_does(
    tmp_path: pathlib.Path,
) -> None:
    """A constant column beside the same twenty numeric holes.

    The register is careful about this and an earlier draft of it was
    wrong at that width: the defect reaches a column that PUBLISHES a
    style census, not every column whose hole happens to be numeric. A
    constant column publishes none, so no recount runs and there is
    nothing to disagree about.

    The role is asserted rather than assumed, because a case that quietly
    stopped being a constant column would hold this boundary by never
    reaching it.
    """
    settings = taxonomy.Settings(
        small_cell_floor=_FLOOR, declared_missing_values=("-9.99",)
    )
    document, outcome = _run(
        tmp_path, "constant", _constant_table("-9.99"), settings
    )
    block = document["columns"][0]
    assert isinstance(block, dict)
    assert block["role"] == taxonomy.ROLE_CONSTANT
    assert "numeric_styles" not in block
    assert block["n_present"] == _ROWS - _HOLES
    assert not _verdicts(outcome, validation.MISSED)
    assert not _verdicts(outcome, validation.WITHHELD)
