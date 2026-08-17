"""The head count counts WORDS on both sides (review P3-V9-F4).

THE DEFECT THIS FILE EXISTS TO KEEP CLOSED. Where a description cannot
be read back, the obligations counted over the affected column's cells
go to NOT CHECKABLE with the reason printed, instead of a failure the
description cannot support (validation method V2.4-A5). Two tests decide
that and the union is taken. One of them compared how many KEYS the
columns bring back with how many WORDS the settings block says were
named -- and one declared word can be worn by several published keys,
because the producer matches a declaration at its folded spelling.

So: declare `XX` and `YY`. A column of numbers publishes twelve `XX`
holes and twelve ` XX ` ones -- two keys, one word. A free-text column
holds twelve `YY` holes and publishes no spelling of anything, because
its publication class permits none. The head count saw two back and two
named and found no shortfall; the structural test is not asked on a
column of that class at all. `unrebuildable_columns` returned nothing,
and the free-text column reported ELEVEN obligations MISSED against the
table its own description was written from.

THE FREE-TEXT LIMIT IS KNOWN AND ACCEPTED -- it is contract 5 section
7.2, and no version of this format closes it. Failing to ROUTE it is
what this file is about.

THE REPAIR AND WHAT IT COST. `_own_declarations_recovered` counts
declarations rather than keys, at the producer's own identity. It is the
sound direction: what comes back is a subset of what was named, so
equality means everything came back, while a count of keys can exceed
the number of words and hide a loss. The cost was one more shape of
over-fire -- two SPELLINGS of one word, `XX` and `xx`, which the
producer folded into one declaration while `n_declared` counted the two
somebody typed -- measured at 43 obligations moved to NOT CHECKABLE on a
file that passes every one of them.

**THAT COST IS PAID OFF** (2026-08-17, review item P3-V9-F7, plan
amendment A-P3-37). This amendment said it would close "the day the
producer publishes a count of declarations rather than keystrokes", and
`n_declared` counts declarations now, so both sides fold at one
identity. The witness for it is still here, still built the same way,
with the answer it now has;
`tests/test_p3v9f7_declarations_not_keystrokes.py` carries the fold
itself. What is NOT closed is the other over-fire -- two different words
of the person's own where the table holds one -- because whether the
second was ever in a cell is a fact about the table.

THE RED CHECK:

* `REINSTATE=P3-V9-F4` -- the head count comparing keys with words, as
  it stood. Reds the routing witness.

Every table here is built by the seeded neutral builders in
`fixtures.py` (plan D13), and every description by the REAL producer.
"""

import os
import pathlib

import pytest

import fixtures
from synthtwin import contract, taxonomy, validation
from synthtwin.cli import main

FLOOR = taxonomy.Settings().small_cell_floor

# Two markers of the person's own: neither is one of synthtwin's
# thirteen published words, and neither is produced by any builder.
OURS = "XX"
THEIRS = "YY"


@pytest.fixture(autouse=True)
def _reinstated(monkeypatch: pytest.MonkeyPatch) -> None:
    """Put the count of KEYS back when REINSTATE asks for it."""
    if os.environ.get("REINSTATE") == "P3-V9-F4":
        monkeypatch.setattr(
            validation,
            "_own_declarations_recovered",
            lambda description: len(
                validation._named_in_the_columns(description)
            ),
        )


def _sentences(count: int, start: int = 0) -> "list[str]":
    """Distinct free-text values: several words, none of them a label."""
    return [
        f"a line of words numbered {row + start} and written out"
        for row in range(count)
    ]


def _two_columns(folder: pathlib.Path, name: str) -> pathlib.Path:
    """The witness: two keys of one word beside a word no column names."""
    numbers = [f"{row + 1}" for row in range(60)]
    column = numbers + [OURS] * 12 + [f" {OURS} "] * 12
    words = _sentences(60) + [THEIRS] * 12 + _sentences(12, start=60)
    rows = [[column[row], words[row]] for row in range(len(column))]
    return fixtures.write(
        folder, name, fixtures.rows_to_csv(["reading", "note"], rows)
    )


def _counts(report: str) -> "dict[str, int]":
    """The five verdict counts off a written quality report."""
    found: dict[str, int] = {}
    for line in report.splitlines():
        words = line.split()
        if len(words) > 2 and words[1].isupper() and words[0].isdigit():
            found[words[1]] = int(words[0])
    return found


def _described(
    folder: pathlib.Path, table: pathlib.Path, *declared: str
) -> "tuple[pathlib.Path, contract.Profile]":
    command = ["profile", f"{table}"]
    for word in declared:
        command = command + ["--missing-value", word]
    assert main(command) == 0
    written = folder / f"{table.stem}-profile.json"
    return written, contract.load_profile(f"{written}")


# -- the witness -------------------------------------------------------


def test_two_keys_of_one_word_do_not_hide_a_second_word(
    tmp_path: pathlib.Path,
) -> None:
    """The count of keys said two; the count of words says one."""
    table = _two_columns(tmp_path, "reading.csv")
    _written, description = _described(tmp_path, table, OURS, THEIRS)
    # What the description actually holds: two keys on the counting
    # column, nothing at all on the free-text one.
    named = validation._named_in_the_columns(description)
    assert sorted(named) == [f" {OURS} ", OURS]
    assert validation._own_declarations_recovered(description) == 1
    assert (
        validation._own_words_named(
            description.settings.declared_missing_values
        )
        == 2
    )


def test_the_free_text_column_is_routed_rather_than_failed(
    tmp_path: pathlib.Path,
) -> None:
    """A known limit is stated; eleven false misses are not printed."""
    table = _two_columns(tmp_path, "reading.csv")
    written, description = _described(tmp_path, table, OURS, THEIRS)
    routed = validation.unrebuildable_columns(description)
    assert "note" in routed
    assert "2 word(s) of your own" in routed["note"]
    assert "records 1 of them" in routed["note"]
    assert main(["validate", f"{written}", "--twin", f"{table}"]) == 0
    report = (tmp_path / "reading-quality.txt").read_text("utf-8")
    assert _counts(report)["MISSED"] == 0
    assert "NO CHECKABLE OBLIGATION WAS MISSED." in report


# -- and it does not fire where nothing was lost -----------------------


def test_a_description_that_lost_nothing_is_still_checked_in_full(
    tmp_path: pathlib.Path,
) -> None:
    """One word, two keys, one column: no shortfall, no routing.

    This is the case counting words could have broken and does not: the
    two keys are two spellings of the one word that was named, so what
    came back equals what was named and the column keeps every check.
    """
    numbers = [f"{row + 1}" for row in range(60)]
    values = numbers + [OURS] * 12 + [f" {OURS} "] * 12
    table = fixtures.write(
        tmp_path,
        "reading.csv",
        fixtures.single_column_table("reading", values),
    )
    written, description = _described(tmp_path, table, OURS)
    assert validation._own_declarations_recovered(description) == 1
    assert validation.unrebuildable_columns(description) == {}
    assert main(["validate", f"{written}", "--twin", f"{table}"]) == 0
    counted = _counts((tmp_path / "reading-quality.txt").read_text("utf-8"))
    assert counted["MISSED"] == 0
    assert counted["HELD"] > 0


def test_the_over_fire_this_cost_is_paid_off(tmp_path: pathlib.Path) -> None:
    """Two spellings of one word: no longer routed, and why.

    THE COST THIS AMENDMENT RECORDED, AND ITS CLOSURE. Counting
    declarations on the recovered side made one more shape of
    description over-fire: `XX` and `xx` are one declaration to the
    producer, and `n_declared` counted the two somebody typed, so the
    head count saw one back against two named and routed a column whose
    reading rule IS rebuildable -- 43 obligations to NOT CHECKABLE on a
    file that passes every one of them.

    That was recorded here as the safe direction and as closing "the day
    the producer publishes a count of declarations rather than
    keystrokes". The day was 2026-08-17 (review item P3-V9-F7; plan
    amendment A-P3-37; contract 5 C5-18 as amended). Both sides now
    count declarations at ONE identity, so this witness comes out level
    and the column keeps every check.

    What is asserted is unchanged in kind -- the same table, the same
    two spellings, the same run -- and only the expected answer moved,
    so a regression on either side reds this.
    """
    numbers = [f"{row + 1}" for row in range(60)]
    values = numbers + [OURS] * 12 + [OURS.lower()] * 12
    table = fixtures.write(
        tmp_path,
        "reading.csv",
        fixtures.single_column_table("reading", values),
    )
    written, description = _described(tmp_path, table, OURS, OURS.lower())
    assert validation._own_declarations_recovered(description) == 1
    assert description.settings.declared_missing_values.n_declared == 1
    assert validation.unrebuildable_columns(description) == {}
    assert main(["validate", f"{written}", "--twin", f"{table}"]) == 0
    counted = _counts((tmp_path / "reading-quality.txt").read_text("utf-8"))
    assert counted["MISSED"] == 0
    assert counted["HELD"] > 0
