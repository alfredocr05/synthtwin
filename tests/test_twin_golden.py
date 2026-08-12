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
    canonical,
    contract,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    taxonomy,
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
    target = folder / "table-profile.json"
    target.write_text(
        canonical.serialize(document), encoding="utf-8", newline="\n"
    )
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
    assert len(built.names) == 10
    assert built.write_header is True
    assert built.seed == GOLDEN_SEED
    # The word budget is a fixed function of the published facts (method
    # G4.3), so it moves only when the plan for this description moves.
    # Pinned beside the bytes because "the run spends a different number
    # of words" is a different failure from "the run writes different
    # cells", and a reader is owed the difference.
    assert built.words_drawn == 3048
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
GOLDEN_DESCRIPTION_SHA256 = (
    "ff6c704fbe94b116904899bef0dd1a7e30eb6a784c557fa6981da767db9a7593"
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
    "b4e59d547c49d425c7b9c9d673bce64d365fecd12640d27bfba6d6959fe32803"
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
GOLDEN_REPORT_SHA256 = (
    "4083f570c4548284dca9178eb5b2a56dcf3a1be25acd4953f0b483a7f16e72aa"
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
