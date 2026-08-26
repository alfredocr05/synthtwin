"""P4-D28: a free-text twin keeps its kind, or says it did not (R-P4-36).

A column read as FREE TEXT could produce a twin that reads back as
`long_tail_labels`, with every published count met and nothing saying
so. Measured before the repair on a column of twenty spellings at ten
rows each beside five at four rows each: source `free_text`, twin
`long_tail_labels`, caused by a folded level of fourteen where the
detection line is eleven.

THE CAUSE. A fold-collision partner folds onto its parent, so the pair
makes a level covering BOTH their rows. The walk that chose the parent
did so by a cyclic order over the families and never by the SIZES.

THE REPAIR IS IN TWO HALVES, and the second exists because the first
cannot always work:

* the walk now PREFERS a parent that keeps the pair under the line,
  which answers every column where such a parent exists;
* where the sizes this run laid out leave NO such pairing -- the
  partner groups may themselves be larger than the line, and which
  group is which size is settled before this walk runs -- the twin's
  report NAMES the change. That is the half the residual was opened
  for: the column changed kind "and says nothing".

Both halves are pinned here, and so is the honest limit: the first
column below still reprofiles, because no pairing of its groups can
stay under the line.
"""

import collections
import csv
import pathlib
import random

import fixtures
from synthtwin import contract, generation, profile, reading, taxonomy


def _write(folder: pathlib.Path, name: str, values: "list[str]") -> pathlib.Path:
    """One single-column table, written as the profiler reads them."""
    table = folder / f"{name}.csv"
    with table.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["comment"])
        for value in values:
            writer.writerow([value])
    return table


def _round_trip(
    folder: pathlib.Path, name: str, values: "list[str]"
) -> "tuple[str, str, int, list[generation.Deviation]]":
    """Describe a column, build its twin, and describe the twin again.

    Returns the source role, the role the TWIN reads back as, the
    largest folded level the twin holds, and the twin's deviations.
    """
    table = _write(folder, name, values)
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(), []
    )
    # THE CANONICAL WRITER, not a hand-rolled dump: the loader refuses
    # a description it cannot prove is byte-for-byte the one the
    # profiler writes, and it is right to.
    written = fixtures.write_profile(folder, f"{name}-profile.json", document)
    loaded = contract.load_profile(f"{written}")
    twin = generation.generate(loaded, 5)
    cells = list(twin.columns[0])
    folded = collections.Counter(cell.strip().lower() for cell in cells if cell)
    again = profile.build_document(
        reading.read_table(f"{_write(folder, name + '-twin', cells)}"),
        taxonomy.Settings(),
        [],
    )
    return (
        document["columns"][0]["role"],
        again["columns"][0]["role"],
        max(folded.values()),
        list(twin.deviations),
    )


def _mixed_sizes() -> "list[str]":
    """Twenty spellings at ten rows, five at four -- the residual's own.

    No pairing of the groups this lays out can stay under the line, so
    this column is where the REPORT half has to answer.
    """
    rows: list[str] = []
    for index in range(20):
        rows = rows + [f"note text {index:02d} here"] * 10
    for index in range(20, 25):
        rows = rows + [f"note text {index:02d} here"] * 4
        rows = rows + [f"NOTE TEXT {index:02d} HERE"] * 4
    random.Random(9).shuffle(rows)
    return rows


def _small_sizes() -> "list[str]":
    """Every spelling small enough that a pairing CAN stay under."""
    rows: list[str] = []
    for index in range(54):
        rows = rows + [f"free comment number {index:02d} written out"] * 4
    for index in range(54, 57):
        rows = rows + [f"free comment number {index:02d} written out"] * 2
        rows = rows + [f"FREE COMMENT NUMBER {index:02d} WRITTEN OUT"] * 2
    random.Random(4).shuffle(rows)
    return rows


def test_the_walk_keeps_the_twin_free_text_where_a_pairing_exists(
    tmp_path: pathlib.Path,
) -> None:
    """THE FIRST HALF. Small groups pair with small groups.

    Before the preference the walk took parents in a cyclic order and
    could pile a partner onto a group large enough to cross the line.
    """
    source, again, largest, notes = _round_trip(
        tmp_path, "small", _small_sizes()
    )
    assert source == taxonomy.ROLE_TEXT
    assert again == taxonomy.ROLE_TEXT, (
        "the twin of a free-text column reads back as "
        f"{again}, at a largest folded level of {largest}"
    )
    assert not [note for note in notes if "long tail of labels" in note.note]


def test_a_column_no_pairing_can_answer_says_so(
    tmp_path: pathlib.Path,
) -> None:
    """THE SECOND HALF, and the honest limit beside it.

    This column still reprofiles: its partner groups are themselves
    larger than the line, and which group is which size is settled
    before the walk runs. What it no longer does is stay silent.

    The assertion is deliberately on BOTH facts. A later change that
    fixed the reprofiling would turn the first half of this test red,
    which is the right way to find out that the report is no longer
    needed -- rather than leaving a sentence nobody can trigger.
    """
    source, again, largest, notes = _round_trip(
        tmp_path, "mixed", _mixed_sizes()
    )
    assert source == taxonomy.ROLE_TEXT
    # NAMED, not merely "different". The sentence claims a long tail of
    # labels, so the test claims it too -- otherwise the twin could
    # reprofile as something else while the sentence went on saying
    # this.
    assert again == taxonomy.ROLE_LONG_TAIL and largest >= 11
    said = [note for note in notes if "long tail of labels" in note.note]
    assert said, "the twin changed kind and said nothing"
    assert said[0].column == "comment"
    assert "behaves differently here than on your table" in said[0].note


def _cumulative_sizes() -> "list[str]":
    """One parent taking TWO partners, which first-fit cannot pack well.

    Sizes 1, 2, 2, 2, 2 and 9 across four folded identities. Every
    PAIRWISE sum with the size-one parent is under the line and the
    level the three of them make is not, which is what the accumulated
    check exists for.
    """
    return (
        ["alpha note"] * 1
        + ["ALPHA NOTE"] * 9
        + ["bravo note"] * 2
        + ["BRAVO NOTE"] * 2
        + ["charlie note"] * 2
        + ["delta note"] * 2
    )


def test_a_parent_taking_two_partners_is_counted_by_its_level(
    tmp_path: pathlib.Path,
) -> None:
    """THE PREFERENCE READS THE LEVEL, NOT THE PAIR.

    A reviewer supplied this shape against a first draft that compared
    only `parent + partner`: two partners landed on one parent, each
    pairwise sum under the line, and the level they made was twelve.
    The accumulated check brings it to eleven.

    ELEVEN IS STILL AT THE LINE, and this test says so rather than
    pretending otherwise. The walk takes partners in index order and
    gives each the first parent that fits -- first-fit packing --
    where taking the largest partner first would have reached ten.
    What is GUARANTEED is that the twin says so, which is the
    assertion below.
    """
    source, again, largest, notes = _round_trip(
        tmp_path, "cumulative", _cumulative_sizes()
    )
    assert source == taxonomy.ROLE_TEXT
    assert largest <= 11, (
        "the accumulated check regressed: a parent took partners "
        f"summing to {largest}"
    )
    if again != taxonomy.ROLE_TEXT:
        assert [note for note in notes if "long tail of labels" in note.note], (
            "the twin changed kind and said nothing"
        )


def test_the_report_is_not_raised_when_nothing_crossed(
    tmp_path: pathlib.Path,
) -> None:
    """A sentence that always fires is a sentence nobody can act on.

    The small-sizes column keeps its kind, so no sentence is owed. Read
    together with the two above, this pins that the sentence tracks the
    OUTCOME rather than firing on every free-text column.
    """
    _source, again, _largest, notes = _round_trip(
        tmp_path, "quiet", _small_sizes()
    )
    assert again == taxonomy.ROLE_TEXT
    assert not [note for note in notes if "long tail of labels" in note.note]
