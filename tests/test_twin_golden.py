"""The twin and the report: golden bytes for one fixed description.

Plan P2 acceptance criterion 6, and conformance items 10 and 11 of
`docs/spec/generation-method-v1.md`.

WHAT A GOLDEN IS, AND WHAT IT IS NOT. The three digests below are CHANGE
DETECTORS, not oracles. A hash transcribed out of the implementation
cannot check that implementation, and nothing here tries to: the oracle
for the generator is `tests/test_generation_reference.py`, whose cells
are computed from the method specification alone by a script that
imports none of this package, and every count the twin is supposed to
carry is RECOUNTED from the twin's own cells in `tests/test_generation.py`.
What those two cannot give is the property this file exists for -- that
one whole run, description in and twin and report out, produces the same
bytes on every platform, interpreter version and library version the
matrix covers. This file runs in the plain pytest run, so every cell of
that matrix runs it, exactly as the profile golden in
`tests/test_profile_document.py` does.

THE DESCRIPTION IS BUILT, NEVER COMMITTED (plan D13). The table comes
from the seeded neutral builder in `tests/fixtures.py` and the
description from the real producer, so no data-format file enters the
repository for this and the fixture manifest gains no entry. A committed
description could not be bound by that manifest in any case: the guard
that re-runs every registered generator refuses `ctypes`, and the
producer reaches pandas and numpy, both of which reach `ctypes`.

WHAT TO DO WHEN ONE OF THESE CHANGES. Three digests are pinned rather
than two, so a change names its own cause instead of leaving three
candidates:

* the INPUT digest moved -- the producer changed what it publishes for
  this table. The twin and the report were built from different bytes,
  so their digests will have moved with it, and re-recording all three
  is right once the producer's own change is understood. The profile
  golden in `tests/test_profile_document.py` moves for the same reason
  and is the place that change is read.
* the input digest held and the TWIN digest moved -- the generator turns
  the same description into different cells. Nothing about that is
  automatically wrong (a repair to a rule the method fixes moves cells
  on purpose), but it is never incidental: read the difference against
  the method specification, satisfy yourself the new cells are the ones
  the method requires, and re-record.
* the input and twin digests held and the REPORT digest moved -- the
  wording, the ordering or the set of facts the report states changed.
  The twin is untouched; what moved is what a person is told about it.

In every one of those cases the digest is re-recorded with a comment
saying WHAT moved and how that was checked, in the manner the profile
golden's own comment block does. And in every one of them, a difference
that appears on ONE platform, ONE interpreter version or ONE library
version only is not a legitimate change at all: it is a determinism
defect and is release-blocking (plan D12).
"""

import hashlib
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

# The seed the golden run is made at. Nothing about this number is
# special and no rule depends on it; it is written here in full so a
# reader can reproduce the run by hand:
#
#   synthtwin profile table.csv --identifier record_code
#   synthtwin generate table-profile.json --seed 20260811
#
# on a table.csv holding exactly `fixtures.every_role_table()`.
GOLDEN_SEED = 20260811

# The version string is normalized out of the description before the
# digest is taken, for the reason the profile golden gives: the
# installed version is an input to the description by design (plan D12),
# and leaving it in would make every version bump look like a byte
# divergence. It is normalized rather than deleted because the loader
# requires the field to be there and to hold text.
NORMALIZED_VERSION = "(version normalized for the golden test)"


@pytest.fixture(scope="module")
def description(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    """The description the golden twin is built from, written to a file.

    Built by the REAL producer from the seeded neutral table, written
    through the same serializer `synthtwin profile` writes, and then
    read back through the loader by the tests below -- so the generator
    is handed a genuine document and not one this file made up.

    `record_code` is declared, because declaring it is the only route to
    the identifier role since Phase 1 review round 6 withdrew inference,
    and a golden that never reached that role would leave the whole
    made-up-value path of the generator unpinned.
    """
    folder = tmp_path_factory.mktemp("twin-golden")
    table_path = fixtures.write(
        folder, "table.csv", fixtures.every_role_table()
    )
    table = reading.read_table(str(table_path))
    document = profile.build_document(
        table, taxonomy.Settings(), ["record_code"]
    )
    document["created_with"] = NORMALIZED_VERSION
    target = fixtures.write_profile(folder, "table-profile.json", document)
    return target


@pytest.fixture(scope="module")
def loaded(description: pathlib.Path) -> contract.Profile:
    """The description as the generator receives it, through the loader."""
    return contract.load_profile(str(description))


@pytest.fixture(scope="module")
def built(loaded: contract.Profile) -> generation.Twin:
    """The golden twin: one description, one seed, built once."""
    return generation.generate(loaded, GOLDEN_SEED)


def _digest(text: str) -> str:
    """The SHA-256 of ``text`` written as UTF-8, which is how it is written."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# -- what the fixture is, in words a hash cannot say ------------------


def test_the_golden_run_is_the_shape_this_file_says_it_is(
    loaded: contract.Profile, built: generation.Twin
) -> None:
    """The anchor a digest cannot be: what this run actually is.

    A file holding three hashes and nothing else tells the next person
    nothing about what broke. These four numbers are the ones a reader
    checks first when a digest moves, and each of them fails in its own
    words.
    """
    assert built.n_rows == 240
    assert len(built.names) == 13
    assert built.write_header is True
    assert built.seed == GOLDEN_SEED
    # The word budget is a fixed function of the published facts (method
    # G4.3), so it moves only when the plan for this description moves.
    # Pinned beside the bytes because "the run spends a different number
    # of words" is a different failure from "the run writes different
    # cells", and a reader is owed the difference.
    assert built.words_drawn == 4179
    assert [column.name for column in loaded.columns] == [
        "record_code",
        "region",
        "visits",
        "reading",
        "amount",
        "recorded_on",
        "answer",
        "comment",
        "unused",
        "batch",
        "dose",
        "seen_at",
        "note",
    ]


# -- the description the twin is built from ---------------------------

# Recorded from the fixed table in fixtures.py, with the version string
# normalized as `NORMALIZED_VERSION` says. This is the INPUT digest: it
# is here so that a moved twin digest can be read as the generator's
# doing or the producer's, and never as either one for want of knowing.
#
# It is NOT the same document as the profile golden's, and the one
# difference is deliberate: this one declares `record_code` as an
# identifier and that one declares nothing, so the two together pin the
# producer with the identifier role reached and with it not reached.
#
# IT MOVED AT CONTRACT VERSION 5 and the twin's did NOT, which is worth
# reading as one fact (plan amendment A-P3-28): the description gained
# `profile_version: 5`, two counts on every column block and two
# vocabulary lists in each declaration record, and no generation rule
# reads any of them, so `GOLDEN_TWIN_SHA256` below is untouched. The
# report and the quality report moved with the description, because
# both are about what the description says.
#
# RE-RECORDED 2026-08-21, and the cause is one change with one reach:
# the demonstration table's free-text column stopped being a template.
# It held `observation 0 written out in several plain words`,
# `observation 1 ...` and so on -- which the affixed-number rule of
# this phase reads as a number wearing shared text, because that is
# what those strings are. A fixture meant to stand for text NO rule
# reads had to become text no rule reads, so it is prose that varies
# at both ends and holds no digit.
#
# RE-RECORDED AGAIN THROUGH CODEX ROUNDS 2 AND 3 (2026-08-21), and the
# cause is NOT the one above: that free-text change is a round-1 record
# and the column has not moved since. What moved these digests is the
# `dose` column and the census beside it. `dose` was added to the
# shared table so the affixed role is walked by every battery, its
# spread was widened so a twin can carry its distinctness, and its
# cores were given a decimal point so the fraction-width census is
# exercised on THIS role rather than only on the plain numeric ones.
# The census itself is new in that range and publishes two more
# obligations on `dose` -- `widths.published.1` and
# `widths.published.2` -- so the quality report carries MORE than it
# did, which is the direction a re-recording must move in.
#
# All four digests moved together, which is what a change to the
# TABLE looks like: a different column of values makes a different
# description, a different twin, a different report and a different
# quality report. A change to the generator alone would have moved the
# last three and left the first.
# RE-RECORDED AGAIN FOR THE CLOCK ROLE (2026-08-22). The shared table
# gained a `seen_at` column of clock times -- the second of Phase 4's
# three new column types built end to end -- so the description, the
# twin, its report and the quality report moved together, which is what
# a change to the TABLE looks like. The quality report carries
# twenty-seven more obligations than it did, which is the direction a
# re-recording must move in.
GOLDEN_DESCRIPTION_SHA256 = (
    "8a8e12ee5454ca47f8dab35497053e11d6690881546604b49985aaa6d40191d1"
)


def test_golden_hash_of_the_description_the_twin_is_built_from(
    description: pathlib.Path,
) -> None:
    """Pin the exact bytes the generator is handed (plan D12).

    A change detector on the INPUT. Without it, a moved twin digest has
    two possible causes and the message could name neither.

    The BYTES are read, not the text: reading text translates line
    endings on Windows, and a digest that a translation could quietly
    repair would say the file was the same on a platform where it was
    not.
    """
    digest = hashlib.sha256(description.read_bytes()).hexdigest()
    assert digest == GOLDEN_DESCRIPTION_SHA256, (
        "the description built from the fixed demonstration table "
        "changed, so the twin and the report below were built from "
        "different bytes and their digests moved with it. Read the "
        "producer's change first -- the profile golden in "
        "tests/test_profile_document.py is where it is diagnosed -- and "
        "re-record all three digests together. If this appeared on one "
        "platform only, it is a determinism defect and is "
        f"release-blocking (plan D12). New digest: {digest}"
    )


# -- the twin's bytes -------------------------------------------------

# Recorded from the description above at GOLDEN_SEED. This hash is a
# CHANGE DETECTOR, not an oracle: a value transcribed from the
# implementation cannot check that implementation. The oracle for the
# generator's cells is tests/test_generation_reference.py, whose values
# are computed from the method specification by a script that imports
# neither this package nor numpy nor pandas; the oracle for the counts
# is the recounting in tests/test_generation.py, which reads its
# expectation out of the twin's own cells and never out of the
# description it is checking.
#
# What this one adds is the whole run, end to end, on every CI cell: the
# word stream, the order the columns consume it in, every rounding
# decision, every made-up spelling and the writer's own byte rules, all
# in one number. Any of them differing between two cells of the matrix
# turns red here rather than shipping as a quietly different twin.
GOLDEN_TWIN_SHA256 = (
    "ba6fde8b0435f86bb8c540c9768854b8374aea0092a930057c0a189912ba8af3"
)


def test_golden_hash_of_the_demonstration_twin(
    built: generation.Twin,
) -> None:
    """Pin the bytes of the twin file for one description and one seed.

    Conformance item 10, first clause: twin bytes are identical for
    identical inputs. This is that clause across machines rather than
    within one run -- the same description, the same seed, the same
    version, and the same bytes wherever CI runs it.
    """
    digest = _digest(rendering.twin_csv(built))
    assert digest == GOLDEN_TWIN_SHA256, (
        "the twin of the fixed demonstration description changed. If the "
        "description digest above also moved, the producer moved and this "
        "follows from it; if the description digest held, the generator "
        "turns the same description into different cells, which is never "
        "incidental -- read the difference against "
        "docs/spec/generation-method-v1.md and satisfy yourself the new "
        "cells are the ones the method requires before re-recording. If "
        "it appeared on one platform, one interpreter version or one "
        "numpy version only, it is a determinism defect and is "
        f"release-blocking (plan D12). New digest: {digest}"
    )


def test_the_same_description_and_seed_give_the_same_twin_twice(
    loaded: contract.Profile, built: generation.Twin
) -> None:
    """Within one run as well as across machines (conformance item 10).

    A hash pinned in a file cannot tell a stable generator from one that
    is stable only because it was built once and read many times, which
    is exactly how the fixture above hands it out. So the run is made
    again, from the same loaded description, and compared.
    """
    again = generation.generate(loaded, GOLDEN_SEED)
    assert rendering.twin_csv(again) == rendering.twin_csv(built)
    assert again.words_drawn == built.words_drawn


# -- the report's bytes -----------------------------------------------

# Recorded from the same run. The report is a fixed function of the
# description and the twin -- no path, no clock, no environment -- so
# these bytes are pinnable at all; `rendering.report` states that as a
# guarantee and this is what holds it to its word.
#
# The digest is taken over the text as the command WRITES it, which is
# the text after the display boundary (`parsing.visible_lines`), because
# that is the file a person opens. For this description the boundary
# changes nothing, and that is asserted below rather than assumed, so
# the number pinned here is unambiguously both the report the renderer
# returns and the report that reaches the disk.
#
# RE-RECORDED for review item P2-C1-F4. WHAT MOVED: the report only --
# the description and twin digests above both held, so not one cell of
# the twin changed and what moved is what a person is TOLD about it. The
# report gained the section "HOW CLOSE THE APPROXIMATE FACTS CAME",
# which names every fact the contract calls APPROXIMATED with its
# published value, the value measured on this twin, the two ends of the
# bound method G12 fixes for it and whether the twin landed inside; the
# closing paragraph of the deviation section, which used to say that how
# close the twin came is measured by a later version, now points at that
# section instead. In the same item the two distinctness deviations
# gained a second sentence: a twin holding MORE different values than
# the description records is not a twin that ran out of spellings, and
# the one sentence that used to serve both directions told the reader
# the opposite of what happened on the column of dates. HOW IT WAS
# CHECKED: the new section was read in full
# against the contract's disposition matrix (section 9) --
# `tests/test_p2c1f4_approximation_bounds.py` holds that agreement as
# assertions rather than as a reading -- and the report says strictly
# more than it did, never less.
#
# RE-RECORDED AGAIN for review item P2-C1-F7. WHAT MOVED: the report
# only, once more -- the description and twin digests above both held,
# so not one cell of the twin changed. The first of the three standing
# limits now names the fact in the words every other surface of this
# project uses for it (no cross-column structure at all), adds the
# co-missing case to its examples, and says which later version the
# structure arrives in; the second names the repeated-measures
# consequence at the end rather than leaving the reader to draw it, and
# its opening line was re-wrapped so that the clause about the grain
# survives the claim inventory's whole-phrase reading. HOW IT WAS
# CHECKED: the new section was read in full beside the old one, word
# for word; every sentence that was there is still there, and
# `tests/test_claim_inventory.py` now holds this file's wording, the
# charter's, the front page's, the security document's, the package
# docstring's, the status screen's and the profiler summary's to the
# same four marks, so a future edit cannot quietly drop one of them
# from the report alone.
#
# RE-RECORDED A THIRD TIME for review item P2-C2-F4. WHAT MOVED: the
# report only, once more -- the description and twin digests above both
# held, so not one cell of the twin changed. The approximation section
# gained six entries and its count line moved from 53 to 59: each of the
# three columns of numbers now carries `n_distinct` and
# `n_distinct_folded` with both ends of the envelope method G12.8 fixes
# for them. Round 2 found those two measured nowhere while both
# normative tables disposed them, so the closing sentence claiming every
# approximation had been measured was false on every column of numbers.
# HOW IT WAS CHECKED: the two reports were read side by side; the new
# one holds every line the old one held and six lines more, and the
# column whose count falls short of its published one now prints the
# range it could fall in rather than only the shortfall.
# RE-RECORDED 2026-08-13, owner decision 9, and what moved is a
# correction rather than a rewording. The spreadsheet paragraph used to
# tell every reader that a hazardous cell was a value their description
# published -- which is false for a column that publishes no value at
# all, where synthtwin invented the cell itself. The report now names
# those columns, says the cells were made up, says why the description's
# own counts left no other spelling of that width, and points the reader
# at the real table, where the same cells behave the same way. Nothing
# the old report said was dropped: the count, the column names, the
# refusal to alter the cells, the quoting warning and the import advice
# are all still there, with more beside them.
#
# RE-RECORDED AGAIN the same day, for review item P3-C5-F8: a column
# whose only hazardous cell is its NAME is no longer described as
# holding invented ones, because a name came from the description; and
# the closing sentence no longer says the same cells behave the same way
# in the real table, which an invented value cannot promise. It says
# what is true instead -- values written that way behave the same way
# there, which is why the twin has them.
#
# RE-RECORDED once more for review item P3-C6-F2: the paragraph said
# every other spelling of that width would have broken a count, and a
# case-varied exponent can be a safe one, so the sentence overstated
# necessity. It now says what the counts actually say -- that they left
# no spelling of that width without a sign, because the real table had
# values written that way.
#
# RE-RECORDED at the validator's landing (plan P3-D6, P3-D7 stage 2).
# The twin digest above held, so the cells are untouched; what moved is
# what a person is told. The report gained a section, "WHAT THIS REPORT
# IS NOT, AND WHAT TO RUN FOR THE OTHER THING", saying in as many words
# that this report passes no verdict and naming `synthtwin validate` as
# the command that does -- with what that verdict does and does not mean
# beside it, because a reader who runs it on the strength of this
# paragraph will read its answer through this one. And the handling rule
# moved from three files to four: the quality report states measurements
# taken from the file it checked, so it is real-derived exactly as the
# other three are. The report says strictly MORE than it did; nothing
# was dropped.
# RE-RECORDED AGAIN, for two paragraphs and nothing else (plan
# amendment A-P3-8, review item P3-V3-F8 and round 3's standing owner
# item). The twin digest above held again.
#
# The handling paragraph named four files where a full run leaves five:
# the profiler writes its description TWICE, once for a program and
# once in words, and the plain-language half -- the one a person
# actually reads, the one that repeats the published labels -- was
# named on no surface of this project, in this phase or the last. It is
# named now, and the paragraph rewrapped around it.
#
# The formula paragraph stopped stating a necessity it cannot always
# keep. It told a reader that the description's own counts leave no
# other way to spell a value of that width -- true of the cells the
# counts force, false of a fold-collision partner, which carries its
# parent's spelling and is not forced by anything (plan P3-C7-F1,
# measured at fourteen such cells where two would do). The claim is now
# under a "where" clause on both paragraphs that make it, the report
# says it cannot tell the reader which cell is which, and a blank line
# separates the two points that had run together.
#
# The report says strictly MORE than it did in the first case and less
# than it did in the second, which is the honest direction: what it
# stopped saying was not true. No verdict, count or order moved.
#
# RE-RECORDED AGAIN, for four things found by reading the shipped page
# by hand on a real table (2026-08-15). The description and twin digests
# above held, so nothing about the twin moved: every one of these is
# what the report SAYS.
#
# 1. The absent-cell block printed two groupings of one set of cells as
#    though they were two sets. `missing_by_source` and
#    `missing_by_class` count the same cells -- once by spelling, once
#    by reason -- and "(blank): 11 cell(s)" sat directly above "counted
#    absent because nothing was written there: 11", which reads as
#    twenty-two. The two groups are now labelled as two groupings of the
#    same cells, with the total named once above them.
# 2. And the pooled name was printed as a fact about the table. Both
#    maps pool everything under the floor into `(withheld)`, which is
#    synthtwin's word for "not published here"; at the default floor a
#    column of eight EMPTY cells printed "(withheld): 8 cell(s)" and
#    "counted absent because a spelling held back, because too few rows
#    wrote it that way: 8", telling a researcher their blanks carried a
#    marker. Each map's pooled entry now says how many cells it does not
#    name and why. (Not visible in THIS golden, whose pooled entries are
#    all above the floor; the shape is pinned by the floor-11 tests.)
# 3. An approximated fact's range is not a margin around the published
#    value and the page never said so. Three facts here have a range
#    that does not contain the description's own value at all -- the
#    ninety-ninth date rung, and both datetime cardinalities, whose
#    envelope G12.5's own docstring says need not contain it. Each now
#    says so on its own lines, and the section preamble says what the
#    range is made of.
# 4. The stand-in decision printed the machine code. `_VERDICT_WORDS`
#    was keyed on `missing` and `kept` where the producer publishes
#    `read_as_missing` and `kept_as_a_number`, so every lookup missed
#    and the line read "-999 in 13 row(s): read_as_missing, because
#    outlier_and_frequent" -- beside a summary of the same profile
#    saying it in English. The reason codes had no table here at all
#    and now have the summary's own.
#
# The report says strictly more than it did, in words rather than in
# codes. No verdict, count, measurement or order moved.
#
# IT MOVED AT CONTRACT VERSION 5, in one place, and the report says
# strictly more than it did there. Where a column's absent cells were
# all blank the line read `(blank): 11 cell(s)` -- this package's own
# word printed where a spelling goes -- and it now reads `11 cell(s)
# with nothing written in them`. The count is the same count under the
# same floor; what changed is that it is no longer dressed as a
# spelling somebody's table wrote (contract 5 section 5).
#
# AND ONE HEADING MOVED WITH IT, one stage later, because the fix above
# left the group it sits in mislabelled (plan amendment A-P3-30). The
# first grouping was called "By the spelling your table used" when
# `missing_by_source` was the whole of it; contract version 5 gave the
# blank count and the pooled count fields of their own, so the group
# holds up to three kinds of line and only one is a spelling. On a
# column whose absent cells are all blank it therefore read `By the
# spelling your table used: 11 cell(s) with nothing written in them`,
# which tells a researcher their empty cells wore something. The
# heading and the sentence introducing it now ask what the table WROTE
# in those cells, which is a question "nothing" is an answer to.
#
# FOUR BLOCKS OF THIS REPORT MOVED AND NOTHING ELSE DID, diffed line by
# line before this was re-recorded: `visits` (blank), `amount`
# (`-999`), `comment` (nothing named) and `unused` (blank). Same
# counts, same order, same totals, same sentences everywhere else. The
# description, twin and quality digests all held, which is what says
# this is the page and not the run.
#
# AND IT MOVED AT PHASE 4 STAGE 2, in four places, and again the report
# says strictly more than it did (plan P4-D2, the loud decline). Until
# now the only place this page called a cell invented was inside the
# spreadsheet warning, and only when such a cell began with a formula
# character -- so a reader of an ordinary free-text column met a twin
# full of made-up text with no sentence anywhere saying so. Three
# column blocks gained the sentence their CLASS owes them: `record_code`
# (DECLARED, so it carries the record-number role -- declaring it is the
# only route there) and `comment` (free text), each with every one of
# its present values made up, 240 and 80 of them; and `region` (a set of
# categories -- 7 of 240 cells are neutral stand-ins for the label the
# floor held back). A fourth block is new at
# the foot of the page: the count of columns invented outright and in
# part, printed whatever the count is, for the reason the spreadsheet
# count is printed whatever it is.
#
# AND THOSE SENTENCES WERE REWORDED AT ROUND 1 OF THE STAGE'S OWN CODE
# REVIEW, before anything shipped (items P4-C1-F1 and P4-C1-F2). The
# first wording said the invented cells "meet its counts, lengths and
# shapes" -- an achievement claim, which this same page can contradict
# two sections higher, because a twin does not always meet every
# published fact and the deviation list is where it says so. It now
# says what the cells were built to meet and sends the reader there.
# The column-section preamble moved with it: it said flatly that the
# twin reproduces the values, which is true where the description
# publishes values and false where it publishes none.
#
# NOTHING ELSE MOVED, diffed line by line before this was re-recorded:
# outside the four blocks named above -- the three column sentences,
# the page-foot count, and the column-section preamble those two
# paragraphs record as reworded -- every block, count, order, verdict
# and sentence of this page is unchanged. (An earlier draft of this
# comment closed with "no line was reworded or removed", which
# contradicted the paragraph above it and was wrong about the preamble:
# review item P4-C2-F5.) The description and twin digests both held,
# which is what says this is the page and not the run: stage 2 changes
# no wire, no generation rule and no twin byte.
GOLDEN_REPORT_SHA256 = (
    "4ae022f7d6c279fa7d89a4305402e311a2e16a35da70e53f0cee4b7bf5536b17"
)


def test_golden_hash_of_the_demonstration_report(
    loaded: contract.Profile, built: generation.Twin
) -> None:
    """Pin the bytes of the report file for one description and one seed.

    Conformance item 11's companion for the report: the vectors freeze
    the twin's cells and say in as many words that the report's bytes are
    golden-tested separately (method G14.4). This is that test.
    """
    written = parsing.visible_lines(rendering.report(loaded, built))
    digest = _digest(written)
    assert digest == GOLDEN_REPORT_SHA256, (
        "the report written beside the fixed demonstration twin changed. "
        "If the twin digest above held, the twin is untouched and what "
        "moved is what a person is TOLD about it -- a sentence, an "
        "order, or a fact the report now states or no longer states. "
        "Read the new report before re-recording: a report that says "
        "less than it did is a defect even when nothing crashed. If it "
        "appeared on one platform only, it is a determinism defect and "
        f"is release-blocking (plan D12). New digest: {digest}"
    )


def test_the_display_boundary_changes_nothing_in_this_report(
    loaded: contract.Profile, built: generation.Twin
) -> None:
    """What makes the digest above unambiguous.

    The command puts the report through the display boundary on its way
    to the screen and to the file, so the pinned bytes are the bytes
    after it. Nothing in this description carries a control character,
    so the boundary is the identity here -- which means the same number
    pins the renderer's own text. If this ever fails, the two are no
    longer the same text and the comment above has to say which one the
    digest is of.
    """
    text = rendering.report(loaded, built)
    assert parsing.visible_lines(text) == text


def test_the_report_names_the_seed_the_twin_was_built_at(
    loaded: contract.Profile, built: generation.Twin
) -> None:
    """One fact of the pinned report, stated where a hash cannot state it.

    A person who re-runs the command needs the seed from the report, so
    that it is in there is a property worth failing on by itself rather
    than inside a digest that would only say "something moved".
    """
    assert f"Seed: {GOLDEN_SEED}." in rendering.report(loaded, built)


# -- the quality report's bytes ---------------------------------------

# THE FOURTH ARTIFACT'S GOLDEN (review item P3-V1-F13). The twin above,
# validated against the description it was built from, and the quality
# report that check produces. Until this existed, every test of the
# report compared one platform's output with its own -- the repeat run,
# the relocated run -- so a formatting difference that appeared on one
# CI cell only made all of them pass while the cells disagreed with each
# other, which is exactly the determinism defect plan D12 calls
# release-blocking.
#
# WHAT MOVING IT MEANS, in the same three cases the twin's digests are
# read under:
#
# * the description or twin digest above moved as well -- the producer
#   or the generator changed, this follows from it, and all four are
#   re-recorded together once that change is understood;
# * they held and this moved -- what changed is what a person is TOLD
#   about a file that was checked: a sentence, an order, a verdict, or
#   the set of obligations the census carries. Read the new report
#   before re-recording. A census that carries FEWER obligations than it
#   did is a defect even when nothing crashed, because the summary above
#   it says the counts cover every obligation the description sets;
# * it moved on one platform, one interpreter version or one library
#   version only -- that is not a legitimate change at all. It is a
#   determinism defect and is release-blocking (plan D12, V10).
#
# IT MOVED ONCE, AND THE CENSUS GOT SMALLER, so the second case above is
# answered here rather than left to whoever reads the diff (review item
# P3-V2-B-F10). The description and twin digests held. Six lines left
# the report and nothing else changed, byte for byte:
#
#   styles.at-least.decimal [numeric.numeric_styles]: HELD
#       the description asks for: 0
#
# -- two of them on each of the three numeric columns. Contract 7.5.7
# makes a published style count a FLOOR, so "the file writes at least
# none of this form" is met by every file there is; the line was
# emitted whatever the description published, counted into HELD, and no
# file on earth could have made it miss. That is not an obligation the
# census stopped covering. It is a comparison against nothing that the
# census had been counting as an obligation, and V3.4 refuses an
# executable subcheck that cannot fail by name. The summary's own
# sentence -- these numbers are every obligation this description sets
# that a file can be measured against -- is truer at 309 than it was at
# 315. Every form the description says anything at all about is still
# governed: its published key carries `styles.published.<form>`, and
# both canonical forms carry `styles.canonical.<form>`.
#
# IT MOVED A SECOND TIME, and this one is worth reading line by line
# because twelve obligations changed BUCKET and three arrived (review
# items P3-V2-C-F1, F2, F3; plan amendment A-P3-2). The description and
# twin digests held again. Checked obligations went 309 -> 300 and
# not-checkable 65 -> 77, so the census as a whole went 374 -> 377:
#
# * ten `axes.structural_role` lines, one per column, left the checked
#   side and appear in the NOT-CHECKABLE census. The axis says whether
#   the person declared the column with `--identifier`; the validator
#   re-describes the file under that same declaration, so both sides
#   read the same word whatever the file holds. Every one of the ten was
#   HELD on every run and no file could move any of them;
# * one `moments.skew` line, on `visits`, for the same reason at a
#   different bound: G12.3's own finite fallback there is the range
#   every column of 229 values lies in whatever they are, so the window
#   admitted every file. `amount` keeps its skew check, which is what
#   says this narrows one description and not the fact;
# * one `styles.canonical.decimal` line, on `amount`, whose ceiling is
#   the published count -- 240 cells of a 240-row column, so every cell
#   the file can carry was already licensed;
# * and THREE NEW CHECKS arrive, one per numeric column:
#   `styles.spelled`, which asks the question none of the style
#   arithmetic did -- whether each cell's text is a spelling of its own
#   value that method G6.1's six styles can write. The file the review
#   built to show this, 240 decimal cells each given a trailing zero,
#   validated with exit 0 before it existed.
#
# So the checked census got smaller and every obligation that left it is
# named in the census beside it, with one sentence saying why nothing in
# a CSV settles it. The summary's own claim -- these numbers are every
# obligation this description sets that a file can be measured against
# -- is true of 300 and was false of the twelve it used to count.
#
# RE-RECORDED AGAIN (2026-08-13, review item P3-V2-E-F6). The
# description and twin digests held; the census did not move at all --
# 300 checked, 77 not-checkable, the same verdicts on the same
# obligations. What moved is one word and one paragraph, both about
# WITHHELD, and both were false sentences.
#
# * the census line read "WITHHELD -- measured, and not shown". That
#   was true of one class of withholding and false of the others, and
#   the class it was true of no longer exists: the presence-split
#   withholds it was written for became measurements under amendment
#   V2.4-A1. Where the gate closes because the file's own description
#   carries no fact of that kind, nothing was measured at all;
# * the closing paragraph said a withheld line is one where a
#   measurement "would have said more about the file than describing
#   that file on its own would publish". That is the RULE, and it is
#   right, but it left a reader to guess how it can happen. Both ways
#   are now written out, including the one this round added: a count
#   fewer cells carry than the publication floor is one no description
#   of the file names, so the comparison was made and which way it came
#   out is what cannot be shown.
#
# Both sentences are read by a person deciding what a report means, and
# both were the report describing itself wrongly.
#
# RE-RECORDED AGAIN (2026-08-14, review item P3-V2-G; plan amendment
# A-P3-4). The description and twin digests held; the census did not
# move -- 300 checked, 77 not-checkable, the same verdicts on the same
# obligations. What moved is the report's OPENING, and the reason is
# that the report never said which file it was about.
#
# The output name came from the DESCRIPTION's stem, so
# `validate clinic-profile.json --twin tampered.csv` wrote
# `clinic-twin-quality.txt` -- a report named after the twin, left
# beside the twin, about a different file -- and its bytes held the
# word `tampered` zero times and no path of any kind. Its own third
# paragraph said "It is a report about ONE file" and never said which.
# That is the one fact about a run a reader cannot recover from
# anywhere else once the shell scrollback is gone.
#
# So the outcome now carries the measured file's NAME, the report
# prints it above everything else, and the output name is derived from
# the measured file instead of the description. This digest moved
# because the report gained the line "THE FILE MEASURED: twin.csv" and
# the sentences around it, and because "HOW TO KEEP THIS FILE" now says
# that the report carries that name wherever it goes -- somebody who
# named their file after their study is emailing that name with the
# report. The whole of the rest of the file is byte for byte what it
# was: same census, same verdicts, same obligations, same order.
#
# THE GOLDEN'S OWN INPUT MOVED WITH IT, and that is worth reading
# twice: the report's bytes are now a function of the measured file's
# NAME as well as its bytes (V10, amended). This test measures a file
# it writes as `twin.csv`, so renaming that fixture moves this digest
# for a reason that is not a defect. The name is in the fixture, one
# line above the measurement, so a reader who sees this digest move can
# check that first.
#
# The ordinary run's output name did NOT move: the default measured
# file is `<stem>-twin.csv`, so its report is still
# `<stem>-twin-quality.txt` and the command a finished `generate` run
# teaches still writes exactly the file it always wrote.
# IT MOVED AGAIN, in the same sentence and for the same reason as the
# report's digest above (plan amendment A-P3-8, review item P3-V3-F8):
# "HOW TO KEEP THIS FILE" named four files where a full run leaves
# five, and the profiler's plain-language summary is the fifth. Nothing
# else in the report changed -- same census, same verdicts, same
# obligations, same order, same name line -- and the census was
# compared entry for entry before this was re-recorded.
#
# AND ONCE MORE, AT ELEVEN WINDOWS OF ONE COLUMN (review items P3-V4-F4
# and P3-V4-F5; plan amendment A-P3-9). The datetime windows of method
# G12.4 are now drawn the way the construction draws them, and the
# `recorded_on` column's lines move for it in two directions at once:
#
#   * the first and last ranks are PINNED to the published earliest and
#     latest, which forces one more instant apart;
#   * and the ladder is read by G7.3's whole-number interpolation IN THE
#     METHOD'S OWN UNIT, which for a column of whole dates is one day.
#     Read in the seconds this validator counts in, the floor landed
#     part way through a day and drew a window no date column can hold a
#     value in -- `between 1703980800.0 and 1704132000.0` ends at two in
#     the afternoon. Every one of the nine rung windows now ends on a
#     whole day, and the two distinctness lines read `84 (between 106.0
#     and 240.0)` where they read `119.0` before.
#
# The second half WIDENS that column's distinctness window, and the
# reason it is not a bar being lowered is written out in A-P3-9 clause
# 3: G12.5 fixes that envelope and this document may not draw a
# narrower one. The census is the same six numbers it was -- 249 held,
# 49 within, 2 authorized, 0 withheld, 0 missed, 77 not checkable -- and
# the two files were diffed line by line before this was re-recorded.
#
# AND ONCE MORE, FOR ONE PARAGRAPH THAT NOW NAMES ITS OWN NUMBER (owner
# ruling 2026-08-14; plan amendment A-P3-11 clause 3). The floor is a
# number the person running the tool sets, and `--smallest-group` below
# eleven now runs the whole workflow -- so the withholding rule at the
# foot of the report could no longer say "a group fewer rows carry than
# the publication floor is never named in ANY description". That
# sentence was true when every description had one floor; with floors
# varying it invites a reader to supply eleven and be wrong about what
# the lines above are showing them. It now prints the floor this
# description was made with, at the point where that number decides
# something, which is also the one place a reader of an ordinary report
# is told what protects them.
#
# THE TWO REPORTS WERE DIFFED LINE BY LINE BEFORE THIS WAS RE-RECORDED,
# and the diff is six lines out and seven lines in, all of them inside
# that one paragraph. Everything else is byte for byte what it was:
# same census -- 249 held, 49 within, 2 authorized, 0 withheld, 0
# missed, 77 not checkable -- same verdicts, same obligations, same
# order, same name line. The lowered-floor section that amendment
# A-P3-11 clause 2 adds does NOT appear here and must not: this
# description is made at the default floor, and that section is
# conditional on purpose (a paragraph printed on every run to say the
# floor was not lowered is how a reader is trained to skip the paragraph
# that matters). If this digest ever moves because that section
# appeared, the defect is that the fixture's floor changed, not that the
# report gained a sentence.
#
# AND ONCE MORE, FOR THE LIMIT THE WITHHOLDING RULE NOW STATES ABOUT
# ITSELF (owner ruling 2026-08-14; plan amendment A-P3-13 clause 4). The
# owner was asked whether the validator should defend against someone
# submitting hand-crafted descriptions to extract hidden numbers, and
# ruled: no -- say so honestly instead. So the report's own page says
# BOTH halves: what the withholding protects, which is this page and the
# reader who holds no file, and what it does not, which is a person who
# has the checked file and re-runs the check with descriptions of their
# own. A reader told only the first half reads WITHHELD as a promise it
# never made; a reader told only the second reads it as worthless.
#
# THE REPORTS WERE DIFFED LINE BY LINE BEFORE EACH RE-RECORD, and the
# paragraph landed in three goes: thirteen lines in and none out when it
# first appeared; then fifteen in and twelve out, when it gained the
# statement of what the rule PROTECTS and split into two blocks; then
# eight in and six out, the change this digest records.
#
# WHY THE THIRD, because it was found by reading the page and not by a
# test. The first block ended "so this page can be handed to somebody
# who has no copy of the file at all", and on a description made with
# `--smallest-group 3` that sentence sits nine hundred lines under a
# section saying this same page now carries counts down to three rows
# and that whoever approves data leaving the environment should be told
# before it moves. The withholding rule says what the page may SAY; it
# has never been permission to move the page, and the paragraph now says
# so where a reader meets it.
#
# Everything else is byte for byte what it was through all three: same
# census -- 249 held, 49 within, 2 authorized, 0 withheld, 0 missed, 77
# not checkable -- same verdicts, same obligations, same order, same
# name line. The canonical ceiling that amendment A-P3-13 clause 2 gives
# its teeth back to holds on this description, as it must: the twin is
# conforming, so its recount is inside its licence whichever way the
# comparison is read.
#
# RE-RECORDED AGAIN, for four things found by reading the shipped page
# by hand on a real table (2026-08-15). The census is byte for byte what
# it was -- 249 held, 49 within, 2 authorized, 0 withheld, 0 missed, 77
# not checkable -- and so are every verdict, every obligation and their
# order. What moved is what four kinds of line SAY.
#
# 1. Nine date rungs per datetime column printed their measurement and
#    both ends of their window as raw ordinals: "asks for 2024-11-23
#    (between 1732060800.0 and 1732320000.0) ... found to hold
#    1732147200.0". Three ten-figure numbers are not written for a
#    person (charter principle 2), and worse, they hid that the window
#    at p99 does not reach 2024-12-24 at all. All three are now said as
#    whole units of the column's own resolution away from the published
#    rung, and a window that does not reach the published value says so.
#    No calendar was added here: V1.4 keeps this module's arithmetic to
#    what the method fixes, so it is one subtraction and one exact
#    division in the space `_space_unit` already defines. The same
#    sentence goes on every OTHER window that misses its published
#    value: the cardinality envelope of a column of dates ordinarily
#    does -- "asks for 84 (between 106.0 and 240.0): WITHIN-BOUND" --
#    and a page that flagged it for date rungs alone would have left
#    the reader worse off than the silence it replaced.
# 2. Four label obligations asked for a bare number with no found line
#    under it -- `levels.west.label: HELD -- the description asks for:
#    1`, and the same for `.variants`, `.variants_withheld`,
#    `levels.set`, `suppressed.counts` and
#    `distinct.n_distinct_by_occurrences`. Withholding the found value
#    is the disclosure rule and stays; the "asks for" now says what the
#    obligation is. Two of those numbers were also counts of the wrong
#    thing: `variants_withheld` and `n_distinct_by_occurrences` are
#    keyed on GROUP SIZES, so the number of entries is neither a count
#    of spellings nor of rows.
# 3. The not-checkable census printed registry identifiers --
#    "'answer' -- universal.n_sentinel_candidates_unpublished" -- where
#    every verdict line above it leads with a name, and where the
#    `axes.structural_role` entries beside them already carried one.
#    Every line now names its obligation in words with the identifier
#    in brackets, the same shape a verdict line carries. Three of them
#    ARE verdict subchecks on a file with a header line and now carry
#    that identity: `header.names`, `columns.order`, `columns.n_columns`.
# 4. The WITHHELD paragraph was written in the present indicative about
#    lines this report does not carry: "Some obligations carry no
#    verdict at all and the report says WITHHELD ... the line itself
#    says which", under a census reading 0 WITHHELD. The rule is now
#    stated as a rule, which is true either way, and how many times it
#    bit is generated from the census exactly as the verdict summary is.
#    The census legend beside it went the same way: "0 WITHHELD -- not
#    shown -- the line below says why" sent a reader down the page after
#    lines that are not there, and the word's meaning is a fact about
#    the vocabulary rather than about this run.
#
# IT MOVED AT CONTRACT VERSION 5, and the census grew rather than
# shrank: `n_missing_blank` and `n_missing_withheld` are REPORT-ONLY
# facts of every column, so each column adds two lines to the
# not-checkable census, each naming what it is in words (plan amendment
# A-P3-28). No verdict moved and no obligation left the report.
#
# AND IT MOVED AGAIN WHEN EXACT EQUALITY WAS GIVEN PRECEDENCE OVER THE
# ENVELOPE (review item P3-V10-F5; plan amendment A-P3-40, validation
# method clause V6.1-A1). THIRTEEN checks moved from WITHIN-BOUND to
# HELD and nothing else moved at all: the same 300 checkable
# obligations AS AT THAT DATE, the same 97 not checkable, the same 2
# authorized deviations, 0 withheld and 0 missed, with 249/49 becoming
# 262/36. Those counts are a record of what that amendment did and are
# not this file's current census: Phase 4 added the affixed column and
# the fraction-width census, and the report carries more obligations
# now than it did then. Each
# of the thirteen is a line whose "asks for" and "found" were already
# the same number -- eight numeric rungs on `visits`, one on `amount`,
# one date rung on `recorded_on`, and the three text-shape facts of
# `comment` -- and each now prints the published value without its
# window, because the window is no longer what decided it. Read the diff
# that way: a line where the two values DIFFER may not have moved, and
# one that did would be this repair reaching further than its own rule.
GOLDEN_QUALITY_SHA256 = (
    "eb883c803f5d13bd4f08422ff30552b40b4fcdba2774417c509888b3e328ca5a"
)


def test_golden_hash_of_the_quality_report_for_the_demonstration_twin(
    tmp_path: pathlib.Path,
    description: pathlib.Path,
    loaded: contract.Profile,
    built: generation.Twin,
) -> None:
    """Pin the bytes of the quality report for one description and one file.

    V10: the report's bytes are a fixed function of the description's
    bytes, the measured file's bytes and the version, on one platform
    under the locked dependency set -- with cross-platform agreement
    verified empirically by this digest on every CI cell, exactly as the
    twin's is.

    The twin is written to a file and measured through `validation`'s
    own entry point, so what is pinned is the whole path a person takes:
    describe, build, check.

    THE FILE'S BYTES ARE DECIDED BY THE FIXTURE, not by the platform
    (review item P3-V2-F-F1). `write_text` with no ``newline`` argument
    runs in text mode, which on Windows turns every line feed the
    renderer emitted into a carriage return and a line feed -- so this
    test measured a CRLF twin on `windows-latest` and a LF twin
    everywhere else, and the byte rule `bytes.line-endings` MISSED on
    the one platform nobody runs locally. The product was never wrong:
    `writing.write_text_file` pins the line ending, so a real
    generate-then-validate holds that rule on Windows too. `fixtures.write`
    pins it the same way, and `tests/test_description_line_endings.py`
    now refuses any test that writes a file the product reads without
    deciding its own bytes.
    """
    target = fixtures.write(tmp_path, "twin.csv", rendering.twin_csv(built))
    outcome = validation.measure(loaded, str(target))
    written = parsing.visible_lines(quality.quality_report(loaded, outcome))
    digest = _digest(written)
    assert digest == GOLDEN_QUALITY_SHA256, (
        "the quality report for the fixed demonstration twin changed. If "
        "the description and twin digests above held, both inputs are "
        "untouched and what moved is what the check SAYS -- a sentence, "
        "an order, a verdict, or which obligations the census carries. "
        "Read the new report before re-recording: a census that carries "
        "fewer obligations than it did is a defect even when nothing "
        "crashed. If this appeared on one platform, one interpreter "
        "version or one library version only, it is a determinism defect "
        f"and is release-blocking (plan D12). New digest: {digest}"
    )


def test_the_quality_report_of_the_golden_twin_misses_nothing(
    tmp_path: pathlib.Path,
    loaded: contract.Profile,
    built: generation.Twin,
) -> None:
    """One fact of the pinned report, stated where a hash cannot state it.

    The digest above would be just as stable if the demonstration twin
    started missing half the description's obligations, so the property
    that makes it the RIGHT digest is asserted separately: the twin of
    this description, measured against it, misses nothing.

    The measured file comes from `fixtures.write` for the reason the
    test above gives at length: a `write_text` that leaves the line
    ending to the platform made this assertion fail on Windows alone.
    The bytes that reach `measure` are asserted here rather than
    assumed, because a fixture that stopped pinning them would put the
    same platform-only failure back and nothing else in this file would
    notice.
    """
    target = fixtures.write(tmp_path, "twin.csv", rendering.twin_csv(built))
    assert b"\r" not in target.read_bytes(), (
        "the file this golden measures was written with the platform's "
        "own line ending, so what is measured here is not the twin the "
        "product writes -- see `fixtures.write` and plan D12"
    )
    outcome = validation.measure(loaded, str(target))
    assert outcome.census.missed == 0
    assert outcome.census.withheld == 0
    assert outcome.census.held > 0
