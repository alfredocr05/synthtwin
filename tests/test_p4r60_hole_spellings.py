"""Residual R-P4-60: the field the registry calls exact and nobody checked.

`missing_by_source` says which spelling each absent cell wore and how
many wore it -- `n/a`, `UNK`, a full stop, `-999`. At contract version 5
a twin wrote every absent cell blank, so the field owed a twin nothing
and was REPORT-ONLY. Version 6 writes each spelling at its published
count (plan P4-D6.1, contract C6-115) and the disposition registry has
said EXACT-OBSERVABLE since -- "each `missing_by_source` spelling at
exactly its count".

The validator never noticed. It went on filing the whole field as
not-checkable and built no check at all, so a file that dropped a
required spelling passed with no miss. THE VALIDATOR AND THE PROJECT'S
OWN REGISTRY DISAGREED ABOUT WHETHER SOMETHING WAS AN OBLIGATION, and
the registry is the authority.

Why it matters for the tables this tool is for: the convention a column
uses for "no value" is a fact somebody's analysis branches on. A twin
that quietly drops it teaches that analysis a shape the real table does
not have.
"""

import pathlib
import random

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

SEED = 5
FLOOR = 11


def _run(folder: pathlib.Path, text: str, stem: str):
    """One table through the real producer, loader, generator and check."""
    path = fixtures.write(folder, f"{stem}.csv", text)
    table = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(
        table, taxonomy.Settings(small_cell_floor=FLOOR), []
    )
    written = fixtures.write_profile(folder, f"{stem}-p.json", document)
    described = contract.load_profile(str(written))
    twin = generation.generate(described, SEED)
    return document, described, rendering.twin_csv(twin)


def _holes(outcome: "validation.Outcome") -> "list[validation.Check]":
    return [
        one for one in outcome.checks
        if one.fact == "universal.missing_by_source"
    ]


def test_a_named_hole_spelling_is_an_obligation(
    tmp_path: pathlib.Path,
) -> None:
    """Written at its published count, and MISSED where it is not.

    The witness the residual was opened with: 36 rows, 24 of them the
    label `A` and 12 spelled `n/a`. Both files below agree on presence,
    role, level counts and distinctness; they differ only in whether
    the required spelling is there.
    """
    rows = ["A"] * 24 + ["n/a"] * 12
    text = "grade,note\n" + "\n".join(f"{one},x" for one in rows) + "\n"
    document, described, honest = _run(tmp_path, text, "named")
    assert document["columns"][0]["missing_by_source"] == {"n/a": 12}

    kept = validation.measure(
        described, str(fixtures.write(tmp_path, "honest.csv", honest))
    )
    holes = _holes(kept)
    assert [one.verdict for one in holes] == [validation.HELD], holes
    assert holes[0].published == "12" and holes[0].achieved == "12"
    assert not [one for one in kept.checks if one.verdict == validation.MISSED]

    # THE SAME FILE WITH THE SPELLING GONE. Every `n/a` becomes a blank,
    # which is still an absent cell -- presence does not move.
    dropped = honest.replace("n/a,", ",")
    assert "n/a" not in dropped
    seen = validation.measure(
        described, str(fixtures.write(tmp_path, "dropped.csv", dropped))
    )
    holes = _holes(seen)
    assert [one.verdict for one in holes] == [validation.MISSED], holes
    assert holes[0].published == "12" and holes[0].achieved == "0"


def test_a_judged_hole_is_the_one_key_that_is_not_checked(
    tmp_path: pathlib.Path,
) -> None:
    """A CENSUS LINE, named rather than checked or passed over.

    Where the profiler JUDGED a number to be a stand-in for "no value"
    -- a `-999` among readings -- the twin writes those cells blank,
    because reproducing the number would make the twin's own
    measurement depend on a re-judgement of it (contract C6-116). The
    registry's word for that key is "REPORT-ONLY", so it belongs on the
    not-checkable census with the sentence that says why.

    NOT AN AUTHORIZED-DEVIATION CHECK, which is what this was built as
    first: a check that can only ever come back with one verdict is a
    check nothing can make miss, and the entry table's red battery
    refuses those by name. The battery was right and the first design
    was wrong.
    """
    spread = random.Random(3)
    rows = [
        str(round(spread.uniform(20, 80), 1)) for _each in range(48)
    ] + ["-999"] * 12
    spread.shuffle(rows)
    text = "reading\n" + "\n".join(rows) + "\n"
    document, described, honest = _run(tmp_path, text, "judged")
    block = document["columns"][0]
    assert block["missing_by_source"] == {"-999": 12}
    assert block["sentinel_verdicts"][0]["verdict"] == contract.VERDICT_MISSING

    outcome = validation.measure(
        described, str(fixtures.write(tmp_path, "judged-twin.csv", honest))
    )
    assert not _holes(outcome), _holes(outcome)
    listed = [
        one for one in outcome.listings
        if one.subcheck == "holes.by_source.-999"
    ]
    assert len(listed) == 1, [one.subcheck for one in outcome.listings]
    assert listed[0].fact == "universal.missing_by_source"
    assert "JUDGED" in listed[0].reason
    assert not [
        one for one in outcome.checks if one.verdict == validation.MISSED
    ]


def test_the_field_is_not_named_twice(tmp_path: pathlib.Path) -> None:
    """An obligation is a check OR a census line, never both.

    It was a census line while the registry called it exact; now it is
    a check, and leaving the census line behind would have named one
    obligation twice under two answers that contradict each other.
    """
    rows = ["A"] * 24 + ["n/a"] * 12
    text = "grade,note\n" + "\n".join(f"{one},x" for one in rows) + "\n"
    _document, described, honest = _run(tmp_path, text, "once")
    outcome = validation.measure(
        described, str(fixtures.write(tmp_path, "once-twin.csv", honest))
    )
    assert _holes(outcome)
    listed = [
        one for one in outcome.listings
        if str(one.fact) == "universal.missing_by_source"
    ]
    assert not listed, listed


def test_a_judged_candidate_is_matched_by_value_and_not_by_text(
    tmp_path: pathlib.Path,
) -> None:
    """The validator asks the generator's question (P4-R60-R2-F1).

    A column whose twelve outlier cells are spelled `-999.0` publishes
    that spelling, and the profiler's verdict names the candidate
    `-999`. The generator compares the NUMBER each denotes and writes
    twelve blanks; the validator compared the TEXT, did not match, built
    an exact check, and reported a CORRECT twin MISSED -- twelve
    published against nothing written. Accusing a correct twin is the
    one thing a check must never do.
    """
    spread = random.Random(3)
    rows = [
        str(round(spread.uniform(20, 80), 1)) for _each in range(48)
    ] + ["-999.0"] * 12
    spread.shuffle(rows)
    text = "reading\n" + "\n".join(rows) + "\n"
    document, described, honest = _run(tmp_path, text, "spelled")
    block = document["columns"][0]
    assert block["missing_by_source"] == {"-999.0": 12}
    assert block["sentinel_verdicts"][0]["candidate"] == "-999"

    outcome = validation.measure(
        described, str(fixtures.write(tmp_path, "spelled-twin.csv", honest))
    )
    assert not _holes(outcome), _holes(outcome)
    listed = [
        one for one in outcome.listings
        if one.subcheck == "holes.by_source.-999.0"
    ]
    assert len(listed) == 1, [one.subcheck for one in outcome.listings]
    assert not [
        one for one in outcome.checks if one.verdict == validation.MISSED
    ]

    # AND THE TWO MODULES AGREE ON WHICH KEYS ARE JUDGED, which is what
    # keeps them from parting again: the generator's rule and the
    # validator's are written out separately because one may not import
    # the other, so a test walks both.
    for spelling in block["missing_by_source"]:
        assert generation._is_the_same_candidate(spelling, "-999") == (
            spelling in validation._judged_hole_spellings(
                described.columns[0], described
            )
        )
