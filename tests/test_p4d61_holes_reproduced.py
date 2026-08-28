"""The twin writes the hole spellings the description records.

Plan P4-D6.1, contract C6-115 and C6-116, landed with the version 6
wire flip because version 5's C5-9 said the opposite in a sealed
sentence and an older document is never quietly contradicted.

WHAT THIS BUYS, in the one sentence that matters: a person's `NA`,
`#N/A` or `Not recorded` was recorded in the description and then
thrown away by the twin, so `df[df.status != "NA"]` -- or a
`na_values=` list handed to a reader -- did something on the real
table and nothing at all on the twin.

WHAT IS PINNED HERE:

- each recorded spelling at EXACTLY its published count;
- every other absent cell empty -- the blank count, the withheld
  remainder, and every judged-pass-sourced cell;
- the judged passes' keys stay blank, both of them, for the reason
  C6-116 gives;
- the placement is the same single permutation, so the bytes stay a
  fixed function of the description and the seed;
- and the twin re-describes to the same counts, which is what makes
  the field EXACT-OBSERVABLE rather than merely written.
"""

import collections
import pathlib
import tempfile

import fixtures
from synthtwin import (
    contract,
    generation,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)


def _run(
    values: "list[str]", settings: "taxonomy.Settings | None" = None
) -> "tuple[dict, contract.Profile, generation.Twin, pathlib.Path]":
    """One column, described, loaded and generated."""
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "c.csv", fixtures.single_column_table("c", values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), settings or taxonomy.Settings(), []
    )
    written = fixtures.write_profile(folder, "c.json", document)
    described = contract.load_profile(f"{written}")
    return document, described, generation.generate(described, 3), folder


# THE PROTECTIVE FLOOR, WHICH IS NOT THE DEFAULT ANY MORE (owner ruling,
# plan amendment A-P4-37). The default floor is 1 and at 1 no spelling
# is pooled at all, so the one test here that needs a POOLED spelling to
# exist names the floor that pools it -- eleven, the floor it was
# written against.
_STRICT_FLOOR = 11


def _numbers(count: int) -> "list[str]":
    return [f"{10 + place % 90}" for place in range(count)]


def _counted(twin: generation.Twin) -> "dict[str, int]":
    return dict(collections.Counter(twin.columns[0]))


# -- the rule ---------------------------------------------------------


def test_a_recorded_spelling_is_written_at_its_count() -> None:
    """The whole point, on the commonest shape there is."""
    document, _described, twin, _folder = _run(_numbers(220) + ["NA"] * 20)
    assert document["columns"][0]["missing_by_source"] == {"NA": 20}
    assert _counted(twin)["NA"] == 20


def test_a_declared_spelling_is_written_too() -> None:
    """A word of the person's own, recorded and reproduced."""
    document, _described, twin, _folder = _run(
        _numbers(220) + ["Not recorded"] * 20,
        taxonomy.Settings(declared_missing_values=("Not recorded",)),
    )
    assert document["columns"][0]["missing_by_source"] == {"Not recorded": 20}
    assert _counted(twin)["Not recorded"] == 20


def test_two_spellings_are_each_written_at_their_own_count() -> None:
    """The counts are per spelling, not pooled."""
    document, _described, twin, _folder = _run(
        _numbers(200) + ["NA"] * 20 + ["#N/A"] * 20
    )
    assert document["columns"][0]["missing_by_source"] == {
        "#N/A": 20,
        "NA": 20,
    }
    counted = _counted(twin)
    assert counted["NA"] == 20
    assert counted["#N/A"] == 20


def test_the_twin_redescribes_to_the_same_counts() -> None:
    """What makes the field EXACT-OBSERVABLE rather than merely written."""
    _document, described, twin, folder = _run(_numbers(220) + ["NA"] * 20)
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    again = profile.build_document(
        reading.read_table(f"{written}"), taxonomy.Settings(), []
    )
    block = again["columns"][0]
    assert block["missing_by_source"] == {"NA": 20}
    assert block["n_present"] == 220
    assert block["n_missing"] == 20

    outcome = validation.measure(described, f"{written}")
    missed = [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    ]
    assert missed == []


# -- the exception, and it is both judged passes ----------------------


def test_a_stand_in_number_stays_blank() -> None:
    """C6-116: its absence reading runs through a re-judgement."""
    document, _described, twin, _folder = _run(_numbers(220) + ["-999"] * 20)
    assert document["columns"][0]["missing_by_source"] == {"-999": 20}
    counted = _counted(twin)
    assert counted[""] == 20
    assert "-999" not in counted


def test_a_calendar_placeholder_stays_blank() -> None:
    """The second judged pass, excluded for exactly the same reason."""
    dates = [
        f"2024-{1 + place % 12:02d}-{1 + place % 28:02d}"
        for place in range(220)
    ]
    document, _described, twin, _folder = _run(dates + ["9999-12-31"] * 20)
    assert document["columns"][0]["missing_by_source"] == {"9999-12-31": 20}
    counted = _counted(twin)
    assert counted[""] == 20
    assert "9999-12-31" not in counted


def test_a_blank_stays_blank_and_a_pooled_spelling_stays_blank() -> None:
    """Everything the rule does not name is written empty.

    RUN AT THE PROTECTIVE FLOOR, said out loud since amendment
    A-P4-37 made 1 the default. `rare` is declared and covers five
    rows, so a floor of eleven is what pools it out of
    `missing_by_source` and leaves it as part of the withheld
    remainder -- which is the second half of what this test pins. At
    the default floor of 1 it would be published by name and there
    would be no pooled spelling here to hold anything about.
    """
    values = _numbers(200) + ["NA"] * 20 + ["rare"] * 5 + [""] * 15
    document, _described, twin, _folder = _run(
        values,
        taxonomy.Settings(
            declared_missing_values=("rare",),
            small_cell_floor=_STRICT_FLOOR,
        ),
    )
    block = document["columns"][0]
    assert block["missing_by_source"] == {"NA": 20}
    counted = _counted(twin)
    assert counted["NA"] == 20
    assert "rare" not in counted
    assert counted[""] == block["n_missing"] - 20


# -- the bytes --------------------------------------------------------


def test_the_bytes_stay_a_function_of_the_description_and_the_seed() -> None:
    """One permutation places these too; no new draw is made."""
    _document, described, first, _folder = _run(_numbers(220) + ["NA"] * 20)
    again = generation.generate(described, 3)
    assert first.columns == again.columns
    other = generation.generate(described, 4)
    assert other.columns != first.columns
    assert _counted(other)["NA"] == 20
