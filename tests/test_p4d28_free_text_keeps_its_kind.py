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

THE REPAIR IS IN TWO HALVES, and only the second is a guarantee.

* THE WALK PREFERS a parent that keeps the folded LEVEL under the line
  -- the level and not the pair, because a parent may already carry
  partners. This avoids the change wherever a safe parent exists.
* THE REPORT names the change where none does.
  `_levels_past_the_line` measures the FINISHED spellings, so it sees
  a crossing however it arose.

**THE PREFERENCE WAS WITHDRAWN ONCE AND RESTORED, and that is the most
useful thing in this file.** It was measured across 190 randomly built
free-text columns, changed no outcome, and was deleted as inert. The
sample was HOMOGENEOUS: every column had one family, and within one
family the sorted group order usually makes the choice anyway. A
reviewer supplied a MIXED-family column -- ordinary text beside a code
alphabet -- where the cyclic walk meets an unsafe same-family parent
before a safe one. Without the preference that column reaches eleven
and reads back as `long_tail_labels`; with it the largest level is ten
and it stays free text. **A measurement over one family is a
measurement of one family**, and the mixed column is pinned below so
the deletion cannot happen twice.

AND THE SENTENCE SAYS ONLY WHAT IT KNOWS. An earlier wording asserted
that reading the twin back DOES describe it as a long tail of labels,
and that every published count is still met. A reviewer showed both can
be false: declared missing words and the categorical share change what
a later reading sees, and under some declarations the twin reprofiles
as free text after all. The sentence now names what the twin HOLDS.
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
) -> "tuple[str, str, int, list[generation.Remark], list[generation.Deviation]]":
    """Describe a column, build its twin, and describe the twin again.

    Returns the source role, the role the TWIN reads back as, the
    largest folded level the twin holds, the twin's REMARKS -- things
    it holds that no published fact was missed for -- and its
    deviations, which are the published facts it could not meet. The
    crossing this file is about is a remark and never a deviation, and
    both are returned so a test can assert that.
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
        list(twin.remarks),
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


def test_a_column_of_small_groups_keeps_its_kind(
    tmp_path: pathlib.Path,
) -> None:
    """An ordinary free-text column stays free text, and says nothing.

    This is the common case, and the point of pinning it is that the
    sentence below must NOT fire on it: a report that fires on every
    free-text column tells nobody anything.
    """
    source, again, largest, held, notes = _round_trip(
        tmp_path, "small", _small_sizes()
    )
    assert source == taxonomy.ROLE_TEXT
    assert again == taxonomy.ROLE_TEXT, (
        "the twin of a free-text column reads back as "
        f"{again}, at a largest folded level of {largest}"
    )
    assert not [one for one in held if "long tail of labels" in one.note]
    assert not [note for note in notes if "long tail of labels" in note.note]


def test_a_column_no_pairing_can_answer_says_so(
    tmp_path: pathlib.Path,
) -> None:
    """THE REPAIR. This column reprofiles, and now says so.

    The assertion is deliberately on BOTH facts. A later change that
    fixed the reprofiling would turn the first half of this test red,
    which is the right way to find out that the report is no longer
    needed -- rather than leaving a sentence nobody can trigger.
    """
    source, again, largest, held, notes = _round_trip(
        tmp_path, "mixed", _mixed_sizes()
    )
    assert source == taxonomy.ROLE_TEXT
    # NAMED, not merely "different". The sentence claims a long tail of
    # labels, so the test claims it too -- otherwise the twin could
    # reprofile as something else while the sentence went on saying
    # this.
    assert again == taxonomy.ROLE_LONG_TAIL and largest >= 11
    said = [one for one in held if "long tail of labels" in one.note]
    assert said, "the twin changed kind and said nothing"
    assert said[0].column == "comment"
    # IT IS A REMARK AND NOT A DEVIATION, and this is the assertion a
    # reviewer opened item P4-G2-R4-F1 over. The sentence was once filed
    # as a deviation of `n_distinct_folded` -- a published fact that
    # this very column MEETS EXACTLY -- so the report printed it under
    # "a published fact could not be held exactly", beside a published
    # value measuring a different quantity. Two things are pinned: no
    # deviation carries this sentence, and the fact it used to borrow
    # is met.
    assert not [note for note in notes if "long tail of labels" in note.note]
    assert not [note for note in notes if note.fact == "n_distinct_folded"], (
        "the crossing is filed against a fact this twin meets exactly"
    )
    # THE SENTENCE HEDGES ON PURPOSE. It says a later reading MAY call
    # this a long tail, because whether it does depends on how the twin
    # is read -- a reviewer built a case where declared missing words
    # make it read back as free text after all. A wording that asserted
    # the outcome would be false there.
    assert "may call this column" in said[0].note
    assert "Code that dispatches on a column's type" in said[0].note
    # AND IT SAYS SO IN SO MANY WORDS. A reader meeting this sentence
    # must not be left wondering whether their twin lost a count.
    #
    # THE FIRST WORDING OF THIS SENTENCE WAS ITSELF A FALSE CLAIM, which
    # is why the assertion below is shaped the way it is. It said "every
    # count your description publishes about this column is still met
    # exactly" -- a statement about the WHOLE COLUMN, made by a sentence
    # that knows only about the fold. A reviewer built a 240-row column
    # that raises this remark while three deviations on the same column
    # report missed word counts and a missed shape census, so the report
    # said both. The sentence now claims only what it can know: that the
    # crossing itself cost no published fact.
    assert "Nothing was given up to produce it" in said[0].note
    assert "still met exactly" not in said[0].note, (
        "the remark is claiming again that every count of the column is "
        "met, which it cannot know and which a reviewer disproved"
    )


def _mixed_families() -> "list[str]":
    """Ordinary text beside a code alphabet, from a reviewer's own shape.

    Sizes 1, 2, 2, 2, 8 and 9 across four folded identities, split
    between a family whose spellings hold a space and one whose
    spellings do not. The cyclic walk meets an unsafe same-family
    parent before a safe one, so the preference is what decides.

    THIS COLUMN IS WHY THE PREFERENCE EXISTS. Every homogeneous column
    measured -- 190 of them -- was indifferent to it.
    """
    return (
        ["alpha phrase"] * 1
        + ["ALPHA PHRASE"] * 9
        + ["bravo phrase"] * 2
        + ["codeaa"] * 2
        + ["CODEAA"] * 8
        + ["codebb"] * 2
    )


def test_a_mixed_family_column_keeps_its_kind(
    tmp_path: pathlib.Path,
) -> None:
    """THE PREFERENCE, pinned on the only shape that shows it.

    Without it this column reaches a folded level of eleven and reads
    back as a long tail of labels; with it the largest level is ten and
    it stays free text. That is a type change a reader would have met,
    avoided.
    """
    source, again, largest, held, notes = _round_trip(
        tmp_path, "families", _mixed_families()
    )
    assert source == taxonomy.ROLE_TEXT
    assert largest <= 10, (
        "the preference regressed: a partner landed on a parent that "
        f"takes the level to {largest}"
    )
    assert again == taxonomy.ROLE_TEXT
    assert not [one for one in held if "long tail of labels" in one.note]


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
    """A PARENT TAKING TWO PARTNERS IS COUNTED BY ITS WHOLE LEVEL.

    A reviewer supplied this shape against a walk-side preference that
    compared only `parent + partner`: every PAIRWISE sum here is under
    the line and the level the three of them make is not. The answer is
    the ACCUMULATOR -- the walk reads what a candidate parent has
    already taken, not just its own size.

    **THIS TEST USED TO PIN NOTHING** (review item P4-G2-R4-F3). It
    asserted only, and only conditionally, that some sentence existed,
    so it stayed green with the accumulator removed; its docstring also
    still said the preference "is gone" after it had been restored. The
    numbers below are the mutation-sensitive assertion it lacked:

    * with the accumulator, this column's folded levels are 2, 2, 3, 11
    * with every call handed an empty carried map, they are 2, 2, 2, 12

    So the largest level is asserted EXACTLY. A change that stops the
    walk accumulating moves it to twelve and turns this red, which is
    the whole point of the shape.
    """
    source, again, largest, held, _notes = _round_trip(
        tmp_path, "cumulative", _cumulative_sizes()
    )
    assert source == taxonomy.ROLE_TEXT
    assert largest == 11, (
        "the accumulated check regressed: a parent took a partner "
        f"without counting what it already carried, and the level is "
        f"{largest} rather than 11"
    )
    # The crossing is unavoidable on this shape, so the sentence is
    # owed -- unconditionally, unlike the version this replaced.
    said = [one for one in held if "long tail of labels" in one.note]
    assert said, "the twin holds a level at the line and said nothing"
    assert again == taxonomy.ROLE_LONG_TAIL


def test_the_report_is_not_raised_when_nothing_crossed(
    tmp_path: pathlib.Path,
) -> None:
    """A sentence that always fires is a sentence nobody can act on.

    The small-sizes column keeps its kind, so no sentence is owed. Read
    together with the two above, this pins that the sentence tracks the
    OUTCOME rather than firing on every free-text column.
    """
    _source, again, _largest, held, notes = _round_trip(
        tmp_path, "quiet", _small_sizes()
    )
    assert again == taxonomy.ROLE_TEXT
    assert not held, f"a quiet column remarked anyway: {held}"
    assert not [note for note in notes if "long tail of labels" in note.note]


def _remarking_and_deviating() -> "list[str]":
    """A column that raises a remark AND misses published facts.

    A reviewer's own shape (item P4-G3-R5-F3). The remark half is the
    fold crossing; the deviation half is that this column's word counts
    and shape census cannot all be met at once. Both halves matter: a
    fixture that only remarked could not catch the claim below.
    """
    rows: list[str] = []
    for index in range(20):
        rows = rows + [f"longer ordinary phrase number {index:02d} here"] * 10
    rows = rows + ["code20"] * 4 + ["CODE20"] * 4
    for index in range(21, 25):
        rows = rows + [f"memo item {index}"] * 4
        rows = rows + [f"MEMO ITEM {index}"] * 4
    random.Random(3).shuffle(rows)
    return rows


def test_a_remark_never_claims_a_fact_it_cannot_know(
    tmp_path: pathlib.Path,
) -> None:
    """A REMARK SPEAKS FOR ITSELF AND NOT FOR THE WHOLE COLUMN.

    `Remark` was added because filing the fold crossing as a
    `Deviation` told a reader an exact fact had failed when it
    succeeded. Its first wording then made the mirror-image mistake: it
    said every count of the column was still met exactly -- a claim
    about facts it knows nothing about -- and a reviewer produced this
    column, where that sentence stands beside three deviations saying
    the opposite.

    So this test asserts the two halves TOGETHER. A future fixture that
    stopped deviating would make the second assertion vacuous, and the
    first is what catches that.
    """
    _source, _again, _largest, held, notes = _round_trip(
        tmp_path, "both", _remarking_and_deviating()
    )
    assert held, "the fixture no longer remarks, so it pins nothing"
    assert notes, "the fixture no longer deviates, so it pins nothing"
    for remark in held:
        assert "still met exactly" not in remark.note
        assert "every count" not in remark.note.lower(), (
            "a remark is claiming something about facts it cannot see, "
            f"beside {len(notes)} deviation(s) on the same column"
        )
