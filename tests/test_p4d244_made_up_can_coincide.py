"""A made-up value can be one the table also holds, and the report says so.

The final review of 2026-09-18 measured a 2,000-row clinical table with
`--identifier subject_id` over identifiers `SUBJ-10000` to `SUBJ-11999`.
At both seeds, 40 of the twin's 2,000 identifiers were identifiers the
real table holds -- about two per cent, which is the chance rate for
drawing 2,000 five-figure values against a 2,000-value source. The
owner's rulings hold: no row of the twin is a row of the table, every
other field of those rows differs, and no real identifier reaches the
description, the summary or the questions file. But the twin's report
said of that column that synthtwin MADE UP all 2,000 of its values and
"They are not your data", which is not true of those forty, and a person
holding the twin could read a fabricated clinical record beside a real
subject's number and believe the two belong together.

The generator cannot avoid it BY DESIGN: it never reads the table, so it
cannot know which values the table holds. What it can do is say so, and
that sentence is what this pins. The bytes of the demonstration report
are pinned beside it by `tests/test_twin_golden.py`, whose digest was
re-recorded for exactly these four lines and no others.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import pathlib

from synthtwin import contract, generation, rendering
from tests import fixtures
from tests.test_stage2_round_trip import _exit_of

ROWS = 400


def _described(folder: pathlib.Path) -> "contract.Profile":
    """A table with one declared identifier column, described."""
    folder.mkdir(parents=True, exist_ok=True)
    rows = [
        [f"SUBJ-{10000 + index}", f"{20 + index % 50}"] for index in range(ROWS)
    ]
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["subject_id", "age"], rows),
        encoding="utf-8", newline="",
    )
    assert _exit_of(
        ["profile", f"{table}", "--out-dir", f"{folder}", "--replace",
         "--identifier", "subject_id"]
    ) == 0
    return contract.load_profile(f"{folder / 'real-profile.json'}")


def test_the_report_says_a_made_up_value_can_coincide(
    tmp_path: pathlib.Path,
) -> None:
    """The four lines, in the paragraph that used to promise the opposite."""
    loaded = _described(tmp_path)
    written = rendering.report(loaded, generation.generate(loaded, 4))
    assert "MADE UP all" in written
    assert "A made-up value can be one your table also holds by" in written
    assert "chance: synthtwin never reads your table, so it cannot" in written
    assert "row of this twin belongs to whoever holds it in yours." in written


def test_the_sentence_stands_where_the_claim_stands(
    tmp_path: pathlib.Path,
) -> None:
    """It is part of the all-made-up paragraph, not a note somewhere else.

    The claim it qualifies is `synthtwin MADE UP all N of this column's
    present value(s)`, so it has to be read by whoever reads that: the
    two are counted here and must appear the same number of times.
    """
    loaded = _described(tmp_path)
    written = rendering.report(loaded, generation.generate(loaded, 4))
    claims = written.count("MADE UP all")
    said = written.count("A made-up value can be one your table also holds")
    assert claims >= 1
    assert said == claims
