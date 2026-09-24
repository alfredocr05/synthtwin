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
#   synthtwin profile table.csv --identifier record_code \
#       --measurement pressure --smallest-group 11
#   synthtwin generate table-profile.json --seed 20260811
#
# on a table.csv holding exactly
# `fixtures.every_role_and_joined_table()`.
#
# The smallest group is asked for rather than left to the default, for
# the reason the description fixture below gives at length: the shipped
# default is now one, and at one this run would hold nothing back at
# all.
GOLDEN_SEED = 20260811

# The version string is normalized out of the description before the
# digest is taken, for the reason the profile golden gives: the
# installed version is an input to the description by design (plan D12),
# and leaving it in would make every version bump look like a byte
# divergence. It is normalized rather than deleted because the loader
# requires the field to be there and to hold text.
NORMALIZED_VERSION = "(version normalized for the golden test)"


# THE PRE-WIDEN RUN, FROZEN AS DATA. These are what the demonstration
# carried BEFORE the joined column joined it, recorded once and never
# recomputed. Comparing the narrow run against the wide one at runtime
# proved only that appending a column does not perturb TODAY's
# implementation: a landing that removed a check from both runs, or
# changed an original column in both, left every subset assertion equal
# and the fresh digest blessing the regression (review item
# P4-A2-R5-F2). A frozen baseline cannot move with the code.
NARROW_CHECK_COUNT = 407
NARROW_CHECK_DIGEST = (
    "092371c4fead2ac71a787d56f71b070d5e65b4ce8dfb2c0cda84883448bc2a63"
)
# THE KEY THAT ARRIVED AFTER THAT BASELINE WAS FROZEN, and it is
# subtracted rather than folded in (plan amendment A-P4-47). Every
# published level of a label role now carries `shape_form_cells`, so
# the narrow demonstration files nine checks it did not file before:
# two on `answer`, one on `batch`, two on `note` and four on `region`.
#
# THE FROZEN 407 ARE STILL ASSERTED WHOLE. Re-recording the digest
# against 416 would have retired the only thing this test buys -- a
# baseline that cannot move with the code -- and blessed whatever else
# moved in the same commit. Setting the new key's checks aside instead
# reproduces the 2026-08-31 digest character for character, which is
# what says nothing was lost by IDENTITY rather than by count. That is
# review item P4-A2-R5-F2's own lesson, applied to the landing that
# came after it.
LEVEL_FORM_SUBCHECK = "shape_form_cells"
# ...and the LISTING that arrived after the listing baseline was
# frozen, subtracted from that baseline for the same reason (plan
# P4-D30). `field_widths` is REPORT-ONLY, so it is listed whole on
# every numeric-family column rather than checked width by width.
FIELD_WIDTH_FACT = "numeric.field_widths"
# ...and the SECOND listing to arrive after that baseline was frozen
# (plan P4-D32). `empty_bins` is REPORT-ONLY, listed whole, and listed
# ONLY where the description names a stretch -- so unlike the census
# above it does not appear once per numeric column, and the four it
# adds cannot be predicted from the column list alone. The two are
# subtracted together and each is then named, so a listing that moved
# for any other reason still has nowhere to hide.
EMPTY_BIN_FACT = "numeric.empty_bins"
# ...and the THIRD listing to arrive after that baseline was frozen
# (plan P4-D35, 2026-09-04). `empty_edges` stands beside `empty_bins`
# and is listed under exactly the same condition, so it appears on the
# same columns and nowhere else. Subtracted the same way, and named
# the same way just below.
EMPTY_EDGE_FACT = "numeric.empty_edges"
# ...and the FOURTH listing to arrive after that baseline was frozen
# (plan P4-D38, stage 2, 2026-09-14). `group_separator` is REPORT-ONLY
# and published on every numeric-family column, so like the field-width
# census it is listed once per such column. Subtracted the same way, and
# named just below.
GROUP_SEPARATOR_FACT = "numeric.group_separator"
# ...and the FIFTH and SIXTH (plan P4-D39, the same day): the census of
# marks between day and clock and the midnight statement, listed on every
# datetime column. The demonstration has one, `recorded_on`.
DATETIME_SEPARATORS_FACT = "datetime.datetime_separators"
ALL_AT_MIDNIGHT_FACT = "datetime.all_at_midnight"
# ...and the SEVENTH (landing 2b.3): the count of values at midnight,
# listed where the description publishes none, which on `recorded_on` --
# a column of dates that writes no clock -- is always.
N_AT_MIDNIGHT_FACT = "datetime.n_at_midnight"
# ...and the EIGHTH to ELEVENTH (landing 2b.6): the four censuses of
# HOW a column's dates were written, listed on every column whose member
# cannot show that convention. `recorded_on` is read as `iso-date` --
# fixed field widths, no month NAME, no quarter, no zulu offset -- so it
# lists all four.
WRITTEN_FORM_FACTS = (
    "datetime.date_field_widths",
    "datetime.month_name_styles",
    "datetime.quarter_marker_case",
    "datetime.zulu_case",
)
# ...and the TWELFTH and THIRTEENTH (landing 2b.7): the two mixed-convention
# censuses. Each is CHECKED on a column that wore more than one notation
# or more than one mark and LISTED where it wore one or none, which on
# this demonstration -- whose every column wears a single convention --
# is every numeric-family column. They are set aside from the frozen
# census the way the eleven above are, so the 2026-09-04 baseline has to
# come back character for character rather than be re-recorded against a
# larger number.
NEGATIVE_NOTATIONS_FACT = "numeric.negative_notations"
THOUSANDS_MARKS_FACT = "numeric.thousands_marks"
# ...and the FOURTEENTH to arrive after that baseline was frozen (plan
# P4-D90, landing 2b.13, 2026-09-16). `wide_runs` says whether a
# column's runs of figures past what a double keeps are the text their
# own values write, and its ceiling is EXECUTABLE only where the column
# publishes `canonical`. Every numeric column of the demonstration
# publishes `none` -- no cell of it reaches 2**53 -- so each lists the
# fact once with the sentence saying there is no such cell to govern,
# and the count rises by exactly those four columns.
#
# SET ASIDE RATHER THAN FOLDED IN, on the doctrine the eight above
# follow: re-recording 126 as 130 would bless whatever else moved
# beside them. With this key's own listings taken out the frozen
# baseline must still reproduce character for character.
WIDE_RUNS_FACT = "numeric.wide_runs"
# ...AND THE POOL'S OWN SCALE (plan P4-D301, 2026-09-21). Contract
# section 6.3.3 publishes the average and the spread of the numbers a
# column's floor held back; every label column of this demonstration
# holds back WORDS, so the block says nothing on all four of them and
# the two facts are LISTED rather than checked, one pair per label
# column. Set aside on the doctrine the keys above follow: with them
# out the frozen baseline must come back character for character,
# which is what says nothing else moved in the landing that added
# them.
POOLED_SCALE_FACTS = (
    "label.suppressed_numbers.mean",
)

# ...and the LISTINGS the tail landing brought (stage 3, plan P4-D328):
# the values neither tail of either column publishes, and every rung
# each ladder withholds -- its two ends always, and each rung whose
# rank lies inside a tail. The rungs are the same lines the check
# baseline above names as withdrawn: an obligation that MOVED from the
# checks to the listings is put back there and set aside here, so
# neither census can lose one quietly.
TAIL_LISTING_FACTS = (
    "datetime.low_tail.values",
    "datetime.high_tail.values",
    "clock.low_tail.values",
    "clock.high_tail.values",
    "|date-ladder.min",
    "|date-ladder.max",
    "|date-ladder.p01",
    "|date-ladder.p05",
    "|date-ladder.p99",
    "|clock-ladder.min",
    "|clock-ladder.max",
    "|clock-ladder.p01",
    "|clock-ladder.p05",
    "|clock-ladder.p99",
)

# THE LISTINGS STAGE 3'S TAIL RULE ADDED (landing 3.3, contract 6.7a),
# set aside on the doctrine this file keeps for an obligation that
# ARRIVED. A rung the tail rule withholds carries no window and is
# LISTED (method G5.6a); the grouped histogram of a tail block and the
# census it replaces are REPORT-ONLY and listed for the reason every
# report-only fact is. None of them replaces a check that left: the ones
# that MOVED from the checks are named in `WITHDRAWN_CHECKS` above and
# put back there.
TAIL_LISTINGS_ADDED = (
    "amount|numeric.bin_groups|",
    "amount|numeric.percentiles.max|ladder.max",
    "amount|numeric.percentiles.min|ladder.min",
    "amount|numeric.percentiles|ladder.p01",
    "amount|numeric.percentiles|ladder.p99",
    "amount|numeric.value_histogram|",
    "dose|numeric.bin_groups|",
    "dose|numeric.percentiles.max|ladder.max",
    "dose|numeric.percentiles.min|ladder.min",
    "dose|numeric.percentiles|ladder.p01",
    "dose|numeric.percentiles|ladder.p99",
    "dose|numeric.value_histogram|",
    "reading|numeric.bin_groups|",
    "reading|numeric.percentiles.max|ladder.max",
    "reading|numeric.percentiles.min|ladder.min",
    "reading|numeric.percentiles|ladder.p01",
    "reading|numeric.percentiles|ladder.p99",
    "reading|numeric.value_histogram|",
    "visits|numeric.bin_groups|",
    "visits|numeric.percentiles|ladder.p01",
    "visits|numeric.percentiles|ladder.p99",
)

LISTINGS_ADDED_SINCE = (
    FIELD_WIDTH_FACT,
    WIDE_RUNS_FACT,
    EMPTY_BIN_FACT,
    EMPTY_EDGE_FACT,
    GROUP_SEPARATOR_FACT,
    DATETIME_SEPARATORS_FACT,
    ALL_AT_MIDNIGHT_FACT,
    N_AT_MIDNIGHT_FACT,
    NEGATIVE_NOTATIONS_FACT,
    THOUSANDS_MARKS_FACT,
) + WRITTEN_FORM_FACTS + POOLED_SCALE_FACTS + TAIL_LISTING_FACTS
# ...and the CHECK that arrived after the 416 baseline was frozen
# (amendment A-P4-55, 2026-09-04). The count of different NUMBERS was
# REPORT-ONLY and listed whole; the owner ruled it an obligation
# because analysis code groups by and counts distinct on numeric
# columns, so it is a subcheck now on every column carrying a
# quantitative block -- four of them here.
#
# SUBTRACTED RATHER THAN FOLDED IN, on the doctrine two keys above
# already follow: re-recording 416 as 420 would retire the only thing
# this baseline buys. With the new subcheck set aside the frozen 416
# must come back character for character, which is what says nothing
# ELSE moved in the landing that added it.
VALUE_COUNT_SUBCHECK = "distinct.n_distinct_values"
# ...and the THREE checks plan P4-D36 added, set aside on the same
# doctrine (2026-09-05). A column may wear a SET of wrappers now, so
# the affixed role carries a count of them and two counts of different
# CORES; the demonstration's `dose` column wears one wrapper, so all
# three are held and none of them is a shortfall. Re-recording 416 as
# 419 would retire the only thing this baseline buys.
AFFIX_SET_SUBCHECKS = (
    "counts.affix_variants",
    "counts.n_core_distinct",
    "counts.n_core_distinct_folded",
)
# ...and the THREE spelling checks landing 2b.2 added (2026-09-15), set
# aside on the same doctrine. The mark between thousands was a LISTING
# on every numeric-family column and is a check now, and the notation of
# a negative and the count of signed decimals arrived beside it, so each
# numeric-family column of the demonstration carries all three.
SPELLING_SUBCHECKS = (
    "spelling.group_separator",
    "spelling.negative_form",
    "spelling.decimal_plus",
)
# ...and the ONE check landing 2b.6 added (2026-09-15), set aside on the
# same doctrine. `format` -- the member the real column's dates were
# written in -- was REPORT-ONLY and listed whole, because owner decision
# 5 had the twin write ISO whatever the source wrote, so no file could
# evidence it. The owner reversed that decision: the twin is written in
# the member that read the real column, so describing it again names
# that member and the fact is a check. The demonstration has one column
# of dates, so it is one check. Re-recording 416 as 417 would retire the
# only thing this baseline buys.
MEMBER_SUBCHECK = "format.member"
# ...and the ONE check landing 2b.18 added (contract 7.12, plan
# P4-D120), set aside on the same doctrine. The demonstration's
# `record_code` column is a DECLARED identifier, so it now publishes a
# census of layouts and the run files one check it did not file before:
# `record_code|identifier.layout_forms|forms.published.@%%%%%`.
# MEASURED before this entry was written: with the new check left IN,
# the wide list read 417 and the frozen 407 read 408; with it set
# aside, BOTH digests come back character for character, which is what
# says the landing added an obligation and moved nothing else.
LAYOUT_SUBCHECKS = (
    "forms.published.@%%%%%",
    # ...and the ONE check the owner's ruling of 2026-09-17 added (item
    # 1, plan P4-D202), set aside on the same doctrine: `record_code` is
    # `R` and five figures, so it publishes `{"(column)": "R"}` and the
    # run files `prefix.(column)` beside the layout. MEASURED before this
    # entry was written: with it left in the wide list read 417, and set
    # aside both digests came back character for character.
    "prefix.(column)",
)
# ...and THE CHECKS STAGE 3'S TAIL RULE ADDED (landing 3.3, contract
# 6.7a), set aside on the same doctrine. Every numeric block now
# publishes how far the rows beyond each boundary rung lie from it, and
# a block on a grid whose tail holds few values publishes those values:
# each of them is a fact a file can be held to, so the run files them.
# They land on numeric blocks and on nothing else, which is what the
# assertion below says: every one of them is filed under a
# `numeric.tails` fact.
TAIL_SUBCHECKS = (
    "tails.low.mean_distance",
    "tails.low.rms_distance",
    "tails.high.mean_distance",
    "tails.high.rms_distance",
    "tails.low.values",
    "tails.high.values",
)
# ...and it is SET ASIDE rather than folded into either baseline, which
# is this file's doctrine for an obligation that arrived: re-recording
# 416 as 417 would retire the only thing the baseline buys. Both frozen
# digests must come back character for character with this one check
# taken out, and the assertion below names the column it lands on.
WIDE_CHECK_COUNT = 416
# THE FOUR CHECKS THE OWNER'S RULING OF 2026-09-17 WITHDREW, named and put
# back rather than re-recorded (item 2, option A; plan P4-D201). The size
# of each held-back label is published no more, so the silent check of
# those sizes left every label column of the demonstration: `answer`,
# `batch`, `note` and `region`. An obligation that LEFT is the opposite
# of one that arrived, so it is restored to the run before either frozen
# digest is taken -- and asserted absent from the run first, so a check
# that came back would be caught rather than counted twice. MEASURED
# before this entry was written: the run read 412, and with these four
# restored both digests came back character for character.
WITHDRAWN_CHECKS = (
    "answer|label.suppressed_level_counts|suppressed.counts",
    "batch|label.suppressed_level_counts|suppressed.counts",
    "note|label.suppressed_level_counts|suppressed.counts",
    "region|label.suppressed_level_counts|suppressed.counts",
    # THE OBLIGATIONS THE TAIL LANDING WITHDREW (stage 3, plan
    # P4-D328), named and put back on exactly the doctrine the four
    # above are. A column of dates or clock times publishes no end and
    # no end offset, so `ends.earliest`, `ends.latest`,
    # `offsets.earliest` and `offsets.latest` left the run; each of the
    # two publishes `null` at `min` and `max` and at every rung
    # whose rank lies inside a tail, so those rungs moved from the
    # checks to the listings, where they are named again. What stands in their place
    # is a TAIL on each side, whose own checks are set aside below --
    # so both frozen digests come back character for character with the
    # exchange made explicit, which is what says nothing ELSE moved.
    # MEASURED before this entry was written: with these thirteen
    # restored and the sixteen tail checks set aside, the narrow list
    # reads 407 and the wide one 416, and both digests reproduce.
    "recorded_on|datetime.earliest|ends.earliest",
    "recorded_on|datetime.latest|ends.latest",
    "recorded_on|datetime.earliest_utc_offset|offsets.earliest",
    "recorded_on|datetime.latest_utc_offset|offsets.latest",
    "recorded_on|datetime.date_percentiles.min|date-ladder.min",
    "recorded_on|datetime.date_percentiles.max|date-ladder.max",
    "recorded_on|datetime.date_percentiles|date-ladder.p01",
    "recorded_on|datetime.date_percentiles|date-ladder.p05",
    "recorded_on|datetime.date_percentiles|date-ladder.p99",
    "seen_at|clock.earliest|ends.earliest",
    "seen_at|clock.latest|ends.latest",
    "seen_at|clock.clock_percentiles.min|clock-ladder.min",
    "seen_at|clock.clock_percentiles.max|clock-ladder.max",
    "seen_at|clock.clock_percentiles|clock-ladder.p01",
    "seen_at|clock.clock_percentiles|clock-ladder.p05",
    "seen_at|clock.clock_percentiles|clock-ladder.p99",
    # ...AND THE FOURTEEN RUNGS STAGE 3'S TAIL RULE MOVED FROM THE
    # CHECKS TO THE LISTINGS (landing 3.3, contract 6.7a). A rung whose
    # type-7 reading would touch one of the outermost eleven values is
    # withheld, and a withheld rung carries no window: the run LISTS it
    # instead of checking it, exactly as it lists any fact no file can
    # evidence. Each of them is an obligation that MOVED rather than
    # one that went, so each is put back here before the frozen digest
    # is taken -- the same doctrine, and the same treatment, as the
    # judged key of plan P4-D6.4 below. The two ENDS of `visits` are not
    # among them: eleven rows of that column hold each of its ends, so
    # the description publishes both and the run checks both, one-sided
    # (method G5.6a).
    "amount|numeric.percentiles.max|ladder.max",
    "amount|numeric.percentiles.min|ladder.min",
    "amount|numeric.percentiles|ladder.p01",
    "amount|numeric.percentiles|ladder.p99",
    "dose|numeric.percentiles.max|ladder.max",
    "dose|numeric.percentiles.min|ladder.min",
    "dose|numeric.percentiles|ladder.p01",
    "dose|numeric.percentiles|ladder.p99",
    "reading|numeric.percentiles.max|ladder.max",
    "reading|numeric.percentiles.min|ladder.min",
    "reading|numeric.percentiles|ladder.p01",
    "reading|numeric.percentiles|ladder.p99",
    "visits|numeric.percentiles|ladder.p01",
    "visits|numeric.percentiles|ladder.p99",
)

# ...and the subcheck family that ARRIVED with them, set aside rather
# than folded in: each side of a column of dates or clock times carries
# a boundary, a count of rows beyond it, its two distances and -- where
# it publishes them -- the values it holds (contract TL1). Sixteen
# checks on this demonstration's two such columns, and two listings per
# column for the values neither of them publishes.
TAIL_SUBCHECK = "|tails."

# THE ONE CHECK PLAN P4-D6.4 ADDED, set aside on the same doctrine, and
# it is the only one that can be: the demonstration's `reading` column
# publishes ONE judged key, the thirteen `-999` cells its stand-in pass
# read as "no value". Until the owner's ruling of 2026-09-15 reached
# them the twin wrote those cells blank and the key was on the census of
# facts no file can evidence; the twin writes them now, so the key is a
# check, and the listing it replaces is named below where the listings
# are held. MEASURED before this entry was written: the wide list read
# 417 against 416, and with this line set aside both digests come back.
JUDGED_KEY_CHECK = "reading|universal.missing_by_source|holes.by_source.-999"
# ...and the listing it replaces, which LEFT the census: an obligation
# that moved to the checks is put back before the frozen listing digest
# is taken, and asserted absent from the run first.
JUDGED_KEY_LISTING = JUDGED_KEY_CHECK

# The one fact every rule of the file's written form is filed under (plan
# P4-D86): thirteen on the document, one quoting rule per column and the
# row order on the column the table is sorted by.
FORM_FACT = "document.source.dialect"
WIDE_CHECK_DIGEST = (
    "a7ce60b12fb7b298a5643736c5c480d0e3f6169065e6b08080e1dc5c9116a6f9"
)
# Which columns of the demonstration leave a stretch of their range
# empty, written out rather than counted (plan P4-D32). Only these
# carry the listing; the other numeric-family columns make no claim
# here and get no line.
EMPTY_BIN_LISTINGS = ["visits|numeric.empty_bins|"]
EMPTY_EDGE_LISTINGS = ["visits|numeric.empty_edges|"]
# A HUNDRED AND TWENTY-SIX UNTIL 2026-09-04, and the four that left are
# named where the assertion is made: `numeric.n_distinct_values` was
# listed whole on every column carrying a quantitative block, and
# amendment A-P4-55 made the count of different numbers an obligation,
# so those four are subchecks now. This is the one baseline in this
# file that a landing may lower, and only this way: an obligation that
# MOVED to the checks, with the check baseline showing it arrive.
NARROW_LISTING_COUNT = 126
# LOWERED AGAIN 2026-09-15 (landing 2b.6), the second time and the only
# way this baseline may be lowered: an obligation MOVED to the checks.
# `datetime.format` -- the member the real column's dates were written
# in -- was listed whole on the demonstration's one column of dates,
# because owner decision 5 had the twin write ISO whatever the source
# wrote, so no file could evidence it. The owner reversed that decision:
# the twin is written in the member that read the real column, so the
# fact is a check now, and the check baseline above shows it arriving as
# `MEMBER_SUBCHECK`. One listing left, so 122 becomes 121 and this
# digest is re-recorded over the 121. A census that carries fewer
# obligations than it did is a defect UNLESS they moved, and the two
# baselines together are what show that they did.
NARROW_LISTING_DIGEST = (
    "5978ec5be61bdfe2b0b4f21cad6c7b3ae2477c21c697fa20192f24f86656bf92"
)
# RE-RECORDED 2026-09-15 for plan P4-D86, AS ORDER-FREE IDENTITIES. The
# demonstration table is sorted by `record_code`, the description now
# publishes that row order, and the twin keeps it -- so every column's
# cells moved to other rows while no cell changed. MEASURED before
# re-recording, column by column against a git archive of 53bb012 at this
# seed: each of the thirteen holds the same cells as a multiset, and
# `unused` and `batch`, whose cells cannot be told apart, are unchanged
# even in order. Each digest is now taken over the column's cells SORTED,
# because where rows stand is the written form's own fact, checked by
# `rows.order`; a digest that moved with it would re-record on every
# order change and stop meaning "a cell changed". `unused` and `batch`
# hash exactly as they did, which is the check that nothing else moved.
NARROW_COLUMN_DIGESTS = {
    # RE-RECORDED FOR THE NUMERIC TAIL (stage 3, landing 3.3): the three
    # numeric columns whose ends the tail rule withholds hold different
    # cells, because no ladder of theirs runs to a published extreme
    # and their outermost rows are placed by the two distances the
    # description publishes (contract 6.7a, method G5.3b). `visits` did
    # NOT move -- eleven rows hold each of its ends, so the description
    # publishes both and its ladder is the one it was -- and neither did
    # any column of any other role, which is what says the landing
    # reached the numeric blocks and nothing else.
    # RE-RECORDED AT LANDING 2b.18, and this is the ONE column of the
    # demonstration that may have moved: `record_code` is the table's
    # declared identifier, and the identifier role now publishes the
    # census of layouts and is written to it (contract 7.12, method
    # G9.6, plan P4-D120). MEASURED before re-recording: every cell of
    # the new column wears the published layout `@%%%%%`, the column's
    # own pattern matches every twin row where it matched none before,
    # both the twin and the real table pass the description at exit 0,
    # and the two columns beside it below did NOT move -- which is what
    # says the landing reached the declared identifier and nothing
    # else.
    #
    # RE-RECORDED AGAIN AT LANDING 2b.18's REPAIR PASS, and again only
    # this column moved (plan P4-D128): each layout's walk now starts at
    # its own step past nought and a step is spread by the exact golden
    # section of the layout's room, because the five-figure stride left
    # the leftmost figures of a filling mostly noughts on rooms that are
    # powers of ten. MEASURED before re-recording, against abd11f0: every
    # column but `record_code` is byte-identical; all 240 of its cells
    # still wear `@%%%%%`; and the quality report digest below did not
    # move, so every obligation is held as it was.
    # MERGED WITH LANDING 2b.10 (2026-09-16): that landing takes these
    # digests over the SORTED cells, and this column's cells are landing
    # 2b.8's, so the sorted digest is taken over 2b.8's cells and the
    # order digest below is the one 2b.8 recorded over the same cells as
    # written. Measured on the merged twin, whose bytes equal the tree's
    # before the merge.
    # RE-RECORDED FOR THE OWNER'S RULING OF 2026-09-17, item 1 (plan
    # P4-D202), and again only this column moved: `record_code` is `R`
    # and five figures, so it publishes `{"(column)": "R"}` and every one
    # of its 240 twin cells now opens with `R` where it opened with a
    # letter filled from the step. MEASURED before re-recording: every
    # other column of the demonstration's twin is byte-identical, the
    # 240 cells are still 240 different values wearing `@%%%%%`, and the
    # quality report holds the new obligation.
    "record_code": "a14f1696c9160fc472c68099dd9e4257",
    "region": "ba323f8f897027f35f93eb5e6add6ccc",
    "visits": "39c2d46a66ba3ecd62edfd441b0e47c0",
    # RE-RECORDED at the integer-grid landing, and again on 2026-09-04
    # (amendment A-P4-55). `reading` is whole-valued, so G6.5a's pass
    # declined it until the first of those and two of its strata could
    # be written as one cell; the second widened the pass again and the
    # column now holds ALL 178 of its published different numbers,
    # where it held 177 at some seeds before. MEASURED before
    # re-recording, which is what the sentence beside the twin digest
    # asks for.
    # RE-RECORDED AT THE REPAIR OF THE CARRIED ITEMS OF LANDING 2b
    # (2026-09-17, plan P4-D183). G6.5a now walks every stratum inside its
    # own share before any on wider ground, so four of `reading`'s strata
    # land on the neighbouring whole number instead: MEASURED cell by cell
    # against 7d4278b, 10 cells of this column differ (144/145, 47/48,
    # 171/172 and 28/29 trade places), every other column is
    # byte-identical, the report's variance, skew and kurtosis of this
    # column move in their fourth figure, and the quality report still
    # holds 467 obligations with nothing missed.
    # RE-RECORDED FOR PLAN P4-D6.4 (the owner's ruling of 2026-09-15 that
    # the twin writes everything as the source wrote it). `reading`'s
    # thirteen judged `-999` cells were written blank; they are written
    # `-999` now. MEASURED cell by cell against a git archive of e53d5f4
    # at this seed: exactly those thirteen cells differ, blank to `-999`,
    # in the narrow and the wide run alike, and every other column of
    # both is byte-identical.
    # RE-RECORDED AT THE CLOSE OF STAGE 3'S REVIEW (2026-09-24) for the
    # numeric robustness pass's item 3, the refitting of G5.3b's shape
    # over the tail's own rows. MEASURED column by column on the NARROW
    # demonstration against a git archive of 27b9915: exactly three of
    # the thirteen columns move -- `reading`, `amount` and `dose`, the
    # three whose tails are drawn by a fitted shape -- and the other ten
    # hash exactly as they did, sorted and as written alike. Each of the
    # three keeps its own count of different values and its own two ends.
    "reading": "3152113efa5a7d05a78c5634c0354a93",
    # RE-RECORDED at landing 2b.1 (2026-09-15). `amount` is written at
    # ONE fraction width, so method G5.2a now reads its ladder on that
    # grid and G5.3 gives each stratum the grid value of one of its own
    # ranks: 235 of its 240 cells moved, every one of them still a
    # two-figure number, and the quality report still misses nothing.
    "amount": "9e3ca3d56fe562867c1808f73dd3d57f",
    # RE-RECORDED at landing 2b.6 (2026-09-15). `recorded_on` is the
    # demonstration's one column of dates, and its interior cells move
    # because the placement rule of G7.3 moved: the nine interior rungs
    # are pinned to their PUBLISHED values and every other rank is drawn
    # inside the gap between the pinned ranks either side of it, where
    # each rank used to be interpolated inside its own slice. The two
    # ends, the member, the marks and every published count are
    # unchanged; what moved is where the ranks between the rungs land.
    # MERGED WITH LANDING 2b.10, for the reason given at `record_code`:
    # landing 2b.6's cells, sorted here and as written below.
    # RE-RECORDED AT THE REVIEW OF 158c811 (2026-09-16, plan P4-D130).
    # Method G7.3 gives each pinned rank a place inside its own day and
    # draws a gap across the stretch between two places, where it drew
    # over the gap's two pinned days whole. MEASURED against a git archive
    # of 158c811 at this seed: 90 of this column's 240 cells moved, the
    # other twelve columns are cell for cell the same, and the description
    # did not move.
    # RE-RECORDED AT PART 2 OF THE CARRIED ITEMS OF LANDING 2b (2026-09-17,
    # plan P4-D192). `recorded_on` publishes 84 different dates, and its
    # twin held 176 inside G12.5's envelope of 10 to 240; G7.3's count
    # pass now holds exactly 84. MEASURED against 98ba576: 105 cells of
    # this column differ, every other column is byte-identical, the report
    # prints 84 against a window of 84 for both distinct counts, and the
    # quality report moves those two from WITHIN-BOUND to HELD (467 held
    # and 68 within bound become 469 and 66), nothing missed.
    # RE-RECORDED AT THE TAIL LANDING (stage 3, plan P4-D328), on the
    # TWO columns the landing is about and no others. A column of dates
    # or clock times publishes a tail on each side in place of its two
    # ends: its outermost ranks are drawn through the shape the tail's
    # two distances fix and its interior rungs are pinned only where the
    # tail rule publishes them, so the cells of `recorded_on` and
    # `seen_at` move and nothing else does. MEASURED before re-recording:
    # of the demonstration's fourteen columns exactly these two moved in
    # both the sorted and the written order, the twin and the real table
    # both validate with nothing missed, and the check census reproduces
    # the frozen 407 and 416 with the thirteen withdrawn obligations put
    # back and the sixteen tail checks set aside.
    "recorded_on": "ebae28ac44a90a0c588fe7e8a8aab668",
    "answer": "f96508b26b4c8cae171b5bf0984d34a3",
    "comment": "87f0e3ed56d0f91358fb60fe8b3c9c29",
    "unused": "73be54e263565328cf0122ffc4c15570",
    "batch": "3a209af377e49829fb4ef147725677ca",
    # RE-RECORDED at landing 2b.1 (2026-09-15). The cores publish a
    # withheld mode pair beside 180 different numbers over 240 cells, so
    # G5.2a's stratum cap reads the ladder and is six: the widest
    # stratum was seven, and 139 cells moved to hold it at six.
    # RE-RECORDED AT THE REPAIR OF THE STAGE-2b INTEGRATION (2026-09-16).
    # Only `dose` moved, and only its values: its cores are written at one
    # and at two places, and a census of several widths is now the grid of
    # its commonest (method G5.2a step 1), so 228 cells took the value on
    # that grid the ladder puts there. MEASURED against the tree before the
    # repair: the same widths census (160 four-character and 80 five), the
    # same 180 different cells, every other column byte-identical, and no
    # verdict of the quality report moved.
    # RE-RECORDED AT THE REPAIR PASS AFTER THE FINAL SKEPTIC (2026-09-17,
    # plan P4-D179). A pinned value now takes the width its own value
    # needs where the census names it, so the published ends `10.0 mg`
    # and `189.7 mg` (five cells) are written at one place and six other
    # cells take the second place instead. MEASURED cell by cell against
    # a7ae404: 12 cells of `dose` differ, every value is the same number,
    # the census is still 160 at one place and 80 at two, and every other
    # column is byte-identical.
    # RE-RECORDED AT THE INTEGRATION OF STAGE 3'S FIVE LANDINGS
    # (2026-09-23), `dose` ONLY. Read cell by cell against the tree
    # before the merge: 30 of its 240 cells differ, its count of
    # different values is unchanged at 180, and its width census is
    # unchanged at 160 cells of one place and 80 of two -- what moved is
    # the column's REACH, from 10.0 to 189.7 mg to 5.41 to 194.74 mg,
    # because its cores' ladder no longer runs to two published extremes
    # and the numeric tail rule derives both ends instead. `seen_at`
    # holds its digest, which is the check that a CLOCK column is
    # untouched by the numeric rule: the numeric branch's own value for
    # it was a third one, measured on a tree that had no date and clock
    # tails, and neither branch's answer is this tree's.
    "dose": "f7c460e41b34314aa21372f2137cabf4",
    "seen_at": "904896a1750543a4b2f419ddd8f160ed",
    "note": "f0a181daf5af6bdb2db3d44e0a83a641",
}
# AND THE SAME COLUMNS IN THE ORDER THEIR CELLS STAND (repair of landing
# 2b.9). The sorted digests above say no cell changed wherever its row
# stands, and on their own they stop noticing a change that moves cells
# WITHIN a column and keeps the multiset -- a sort that lost its
# stability, an empty record placed elsewhere -- which only `rows.order`
# on the one sort column would still catch. These are taken over the
# cells as written, at the same seed, after the published sort. Recorded
# 2026-09-15 at the repair; `record_code`, the sort column, and `unused`
# and `batch`, whose cells cannot be told apart, hash as their sorted
# digests do, which is the check that the two digests read the same twin.
NARROW_COLUMN_ORDER_DIGESTS = {
    # MERGED (2026-09-16): landing 2b.8's cells as written, the digest
    # it recorded before landing 2b.10 changed how the sorted ones are taken.
    # Re-recorded for plan P4-D202 with the sorted digest above: the
    # same 240 cells, as written, each now opening with the prefix `R`.
    "record_code": "b01184fc67597fdbcb3139cae1b051b1",
    "region": "48583e2c694ee365c884cd8b99719dd1",
    "visits": "fac456b2607b807ffa636be2068ed181",
    # Re-recorded for plan P4-D183 with the sorted digest above: the same
    # ten cells, as written. Re-recorded for plan P4-D6.4 with the sorted
    # digest above: the same thirteen cells, blank to `-999`, in place.
    # Re-recorded with the sorted digests above at the close of stage 3's
    # review: the same moved cells, as written.
    "reading": "9655b1fc4822cfb098c661ef14eb968d",
    "amount": "87fda8264bcfb8d3989c4614026b3974",
    # MERGED (2026-09-16): landing 2b.6's cells as written.
    # RE-RECORDED AT THE REVIEW OF 158c811 (plan P4-D130): the same 90
    # moved cells as the sorted digest above, as written.
    # Re-recorded for plan P4-D192 with the sorted digest above: the same
    # 105 cells, as written.
    "recorded_on": "e9bfe1b5f6ab87930b13009970120aaa",
    "answer": "780ad3693f49d90a1fd2273eb91a6dc7",
    "comment": "8ec45aed18839baa03592651323aa6f6",
    "unused": "73be54e263565328cf0122ffc4c15570",
    "batch": "3a209af377e49829fb4ef147725677ca",
    # RE-RECORDED AT THE REPAIR OF THE STAGE-2b INTEGRATION: the cells
    # themselves moved (see `dose` in the sorted digests above), so the
    # digest of the cells as written moves with them.
    # RE-RECORDED AT THE REPAIR PASS AFTER THE FINAL SKEPTIC (2026-09-17,
    # plan P4-D179): the same 12 cells as the sorted digest above, in
    # the places they stood; no cell moved place.
    # RE-RECORDED AT THE SAME MERGE: the same 30 cells of `dose`, in
    # the places they stand; no cell moved place, and `seen_at` holds.
    "dose": "7f9c511cfa197a17851048d8f09cf985",
    "seen_at": "5230cc5d6f06d53b7c8a6b52cf4400bb",
    "note": "0b99ebde93cbd5fedc30a0d2b7fa9516",
}


def test_widening_the_demonstration_lost_no_obligation(
    tmp_path: pathlib.Path,
) -> None:
    """Every obligation the NARROW demonstration carried is still carried.

    When the joined column joined this demonstration the four digests
    moved, and what justified re-recording them was a COUNT: 407 checks
    became 479. A count is cardinality and not identity -- an
    obligation of the original thirteen columns could have gone while a
    pressure one arrived, the total still rise, the run still show no
    miss because an absent check files none, and the new digest bless
    the exchange.

    The first repair compared the narrow run against the wide one at
    RUNTIME, and that proves less than it looks: both runs come from
    the same implementation, so a landing that dropped a check from
    both left the comparison equal (review item P4-A2-R5-F2). The
    baseline above is FROZEN, so it cannot move with the code.
    """
    described = _described_narrow(tmp_path)
    twin = generation.generate(described, GOLDEN_SEED)
    twin_path = fixtures.write(
        tmp_path, "narrow-twin.csv", rendering.twin_csv(twin)
    )
    outcome = validation.measure(described, str(twin_path))
    # THE ENCODING RULE WAS RENAMED, not added or dropped (plan P4-D86):
    # `bytes.utf8` asks for `source.encoding` now and is called
    # `bytes.encoding`. The frozen baselines below hash the name they were
    # frozen with, so the rule is read back under that name.
    # ...AND A HEAPED END IS THE SAME OBLIGATION UNDER A NEW NAME (stage
    # 3, landing 3.3). A block that publishes an end because a group of
    # eleven rows holds it is checked ONE-SIDED and silently (method
    # G5.6a), and the run files that check under `numeric.percentiles.min`
    # with the subcheck saying so. It is the same rung the baseline was
    # frozen with, so it is read back under the name it had.
    def _named(check: object) -> str:
        subcheck = check.subcheck
        for end in ("min", "max"):
            if subcheck == f"ladder.{end} (heaped end, one-sided)":
                subcheck = f"ladder.{end}"
        if subcheck == "bytes.encoding":
            subcheck = "bytes.utf8"
        return f"{check.column}|{check.fact}|{subcheck}"

    checks = sorted(_named(check) for check in outcome.checks)
    listings = sorted(
        f"{entry.column}|{entry.fact}|{entry.subcheck}"
        for entry in outcome.listings
    )
    # THE WHOLE RUN, frozen as it stands, so an obligation cannot be
    # added or dropped without this moving.
    # The new subcheck's own lines set aside, so the frozen baseline
    # below is the run it was frozen against (amendment A-P4-55).
    def _since(entry: str) -> bool:
        """Whether this line belongs to a check added since the freeze."""
        if VALUE_COUNT_SUBCHECK in entry:
            return True
        # ...and the rules of the file's written form (plan P4-D86), one
        # fact filed on the document and on every column, named rather
        # than counted.
        if f"|{FORM_FACT}|" in entry:
            return True
        # ...and the tail rule's own facts (stage 3, landing 3.3).
        for one in TAIL_SUBCHECKS:
            if entry.endswith(f"|{one}"):
                return True
        if entry == JUDGED_KEY_CHECK:
            return True
        # ...and every obligation the two TAILS of a column of dates or
        # clock times brought (stage 3, plan P4-D328).
        if TAIL_SUBCHECK in entry:
            return True
        for one in (
            AFFIX_SET_SUBCHECKS
            + SPELLING_SUBCHECKS
            + (MEMBER_SUBCHECK,)
            + LAYOUT_SUBCHECKS
        ):
            if one in entry:
                return True
        return False

    for entry in WITHDRAWN_CHECKS:
        assert entry not in checks, entry
    # The check plan P4-D6.4 added is in the run, once, named.
    assert checks.count(JUDGED_KEY_CHECK) == 1, JUDGED_KEY_CHECK
    counted = sorted(
        [entry for entry in checks if not _since(entry)]
        + list(WITHDRAWN_CHECKS)
    )
    added = [entry for entry in checks if VALUE_COUNT_SUBCHECK in entry]
    # ...and the wrapper set's own three, named rather than counted:
    # the demonstration has ONE affixed column and it wears one
    # wrapper, so all three are on that column and nowhere else.
    wrapped = [
        entry
        for entry in checks
        if any(one in entry for one in AFFIX_SET_SUBCHECKS)
    ]
    assert sorted(entry.split("|")[0] for entry in wrapped) == [
        "dose", "dose", "dose",
    ], wrapped
    # ...and the tail rules' own, named rather than counted. BOTH
    # STAGE-3 TAIL LANDINGS FILE THE SAME SUBCHECK NAMES, which is why
    # this is asserted on the FIELD and not on the name: a numeric
    # column files them under `numeric.tails.<side>.<distance>` (landing
    # 3.3) and a column of dates or clock times under
    # `datetime.<side>_tail.<distance>` or `clock.<side>_tail.<distance>`
    # (plan P4-D328). No other role has tails, so no other field prefix
    # may appear here -- and the assertion said `numeric.tails` alone
    # while only one of the two landings was in the tree.
    tailed = [
        entry
        for entry in checks
        if any(entry.endswith(f"|{one}") for one in TAIL_SUBCHECKS)
    ]
    assert tailed, "the tail rules file their own facts"
    assert all(
        entry.split("|")[1].startswith(
            ("numeric.tails", "datetime.low_tail", "datetime.high_tail",
             "clock.low_tail", "clock.high_tail")
        )
        for entry in tailed
    ), tailed
    # ...and each of the three roles that can have them does, so a
    # landing that stopped filing one would be seen here rather than
    # only in a digest.
    assert {entry.split("|")[1].split(".")[0] for entry in tailed} == {
        "numeric", "datetime", "clock",
    }, sorted({entry.split("|")[1] for entry in tailed})
    assert len(counted) == WIDE_CHECK_COUNT, len(counted)
    # ...and the ONE check landing 2b.18 added is on the ONE column that
    # can carry it, named rather than counted: `record_code` is the only
    # DECLARED identifier in this table, and the census of layouts is
    # that role's alone (contract 7.12, C6-129).
    laid = sorted(
        entry
        for entry in checks
        if any(one in entry for one in LAYOUT_SUBCHECKS)
    )
    assert laid == [
        "record_code|identifier.layout_forms|forms.published.@%%%%%",
        "record_code|identifier.layout_prefixes|prefix.(column)",
    ], laid
    # ...and the three spelling checks, on the four numeric-family
    # columns and nowhere else (landing 2b.2).
    spelled = sorted(
        entry
        for entry in checks
        if any(one in entry for one in SPELLING_SUBCHECKS)
    )
    assert sorted(entry.split("|")[0] for entry in spelled) == sorted(
        ["amount", "dose", "reading", "visits"] * 3
    ), spelled
    # ...and the four the new obligation adds are the four it should,
    # named rather than counted: every column of this table that
    # carries a quantitative block and no other.
    assert sorted(entry.split("|")[0] for entry in added) == [
        "amount",
        "dose",
        "reading",
        "visits",
    ], added
    assert (
        hashlib.sha256("\n".join(counted).encode("utf-8")).hexdigest()
        == WIDE_CHECK_DIGEST
    ), (
        "the demonstration's own obligations changed. That is not a "
        "widening -- the narrow table is untouched -- so a check was "
        "added, removed or renamed. Read which before moving this."
    )
    # ...and the 407 that stood BEFORE `shape_form_cells` existed, whole
    # and by identity. This is the assertion that cannot be satisfied by
    # re-recording: set the new key's checks aside and the older digest
    # must come back character for character.
    before = sorted([
        entry
        for entry in checks
        if LEVEL_FORM_SUBCHECK not in entry
        # ...and the count of different numbers, which arrived after
        # this baseline too (amendment A-P4-55). Two keys set aside,
        # each named, and the 2026-08-31 digest still has to come back
        # character for character.
        and not _since(entry)
    ] + list(WITHDRAWN_CHECKS))
    assert len(before) == NARROW_CHECK_COUNT, len(before)
    assert (
        hashlib.sha256("\n".join(before).encode("utf-8")).hexdigest()
        == NARROW_CHECK_DIGEST
    ), (
        "an obligation the demonstration carried before amendment "
        "A-P4-47 is gone or renamed. A key added since then cannot "
        "excuse that: this list is the run with the new key's own "
        "checks taken out, so it must reproduce the frozen baseline."
    )
    # ...and the nine the new key adds are the nine it should, named
    # rather than counted.
    added = sorted(
        entry for entry in checks if LEVEL_FORM_SUBCHECK in entry
    )
    assert added == [
        "answer|label.shape_form_cells|levels.no.shape_form_cells",
        "answer|label.shape_form_cells|levels.yes.shape_form_cells",
        "batch|label.shape_form_cells|levels.one.shape_form_cells",
        "note|label.shape_form_cells|levels.clinic.shape_form_cells",
        "note|label.shape_form_cells|levels.referral.shape_form_cells",
        "region|label.shape_form_cells|levels.east.shape_form_cells",
        "region|label.shape_form_cells|levels.north.shape_form_cells",
        "region|label.shape_form_cells|levels.south.shape_form_cells",
        "region|label.shape_form_cells|levels.west.shape_form_cells",
    ], added
    # THE LISTINGS ARE HELD THE SAME WAY, and the same argument
    # applies to the key that arrived after THIS baseline was frozen.
    # `field_widths` is REPORT-ONLY (plan P4-D30), so every numeric
    # column of the demonstration lists it once and the count rises by
    # exactly those columns. Setting them aside must reproduce the
    # frozen 126 character for character; re-recording the digest
    # against 130 would bless whatever else moved beside them.
    kept = [
        entry
        for entry in listings
        if not any(fact in entry for fact in LISTINGS_ADDED_SINCE)
        and entry not in TAIL_LISTINGS_ADDED
    ]
    # FOUR LEFT THIS CENSUS ON 2026-09-04 and they are named rather
    # than absorbed: `numeric.n_distinct_values` was listed whole on
    # every column carrying a quantitative block, and amendment
    # A-P4-55 made the count of different numbers an OBLIGATION, so
    # those four are subchecks now. A census that carries fewer
    # obligations than it did is a defect -- unless the obligations
    # MOVED to the checks, which is what happened and which the check
    # baseline above shows arriving there.
    # ...AND A FIFTH LEFT IT ON 2026-09-15 (landing 2b.6), named here on
    # the same doctrine rather than absorbed: `datetime.format` was
    # listed whole on every column of dates, because owner decision 5
    # had the twin write ISO whatever the source wrote and no file could
    # evidence the member that read the real column. The owner reversed
    # that decision, so the member IS reproduced and the fact is a
    # check -- which the check baseline above shows arriving there, as
    # `MEMBER_SUBCHECK`. The demonstration has one column of dates, so
    # one listing left.
    # ...AND A SIXTH LEFT IT ON 2026-09-18 (plan P4-D6.4), named on the
    # same doctrine: `reading`'s judged key `-999` was listed because the
    # twin wrote its cells blank. The owner's ruling of 2026-09-15 has
    # the twin write them, so the key is a check -- `JUDGED_KEY_CHECK`
    # above shows it arriving there -- and it is put back here before
    # the digest is taken, so nothing else can leave with it.
    assert JUDGED_KEY_LISTING not in listings, JUDGED_KEY_LISTING
    assert len(kept) == NARROW_LISTING_COUNT - 6, len(kept)
    restored = sorted(kept + [JUDGED_KEY_LISTING])
    assert (
        hashlib.sha256("\n".join(restored).encode("utf-8")).hexdigest()
        == NARROW_LISTING_DIGEST
    ), (
        "a listing the demonstration carried before plan P4-D30 is "
        "gone or renamed. A key added since then cannot excuse that: "
        "this list is the run with the new key's own listings taken "
        "out, so it must reproduce the frozen baseline."
    )
    # ...and the pool's own scale is listed on the LABEL columns and
    # nowhere else (plan P4-D301), named rather than counted. Every
    # label column of this demonstration holds back words, so its block
    # says nothing and the pair is listed; a run that CHECKED either
    # here would be holding a column to a scale its description does
    # not publish.
    assert sorted(
        entry
        for entry in listings
        if any(fact in entry for fact in POOLED_SCALE_FACTS)
    ) == [
        "answer|label.suppressed_numbers.mean|suppressed.numbers.mean",
        "batch|label.suppressed_numbers.mean|suppressed.numbers.mean",
        "note|label.suppressed_numbers.mean|suppressed.numbers.mean",
        "region|label.suppressed_numbers.mean|suppressed.numbers.mean",
    ]
    # ...and the four the new key adds are the four it should, named
    # rather than counted: one per numeric-family column.
    assert sorted(
        entry for entry in listings if FIELD_WIDTH_FACT in entry
    ) == [
        "amount|numeric.field_widths|",
        "dose|numeric.field_widths|",
        "reading|numeric.field_widths|",
        "visits|numeric.field_widths|",
    ]
    # ...and the two mixed-convention censuses are listed on those SAME
    # four columns and nowhere else (landing 2b.7), named rather than
    # counted. Every column of this demonstration wears one notation and
    # one mark, so each census names fewer than two conventions and is
    # listed rather than checked; a run that CHECKED either here would
    # be holding a column to a mixture it does not have, and a run that
    # listed them on a fifth column would be publishing a census on a
    # column that carries no numeric block at all.
    assert sorted(
        entry
        for entry in listings
        if NEGATIVE_NOTATIONS_FACT in entry or THOUSANDS_MARKS_FACT in entry
    ) == [
        "amount|numeric.negative_notations|",
        "amount|numeric.thousands_marks|",
        "dose|numeric.negative_notations|",
        "dose|numeric.thousands_marks|",
        "reading|numeric.negative_notations|",
        "reading|numeric.thousands_marks|",
        "visits|numeric.negative_notations|",
        "visits|numeric.thousands_marks|",
    ]
    # ...and the mark between thousands is listed NOWHERE now: it was
    # listed on the same four columns until landing 2b.2 made it a check,
    # and the check baseline above shows the four arriving there. Its
    # listings were set aside from the frozen census when they arrived,
    # so the census is untouched by their going.
    assert [
        entry for entry in listings if GROUP_SEPARATOR_FACT in entry
    ] == []
    # ...and the three datetime listings, on the one datetime column,
    # which writes no clock and so carries no obligation of any of them.
    assert sorted(
        entry
        for entry in listings
        if DATETIME_SEPARATORS_FACT in entry
        or ALL_AT_MIDNIGHT_FACT in entry
        or N_AT_MIDNIGHT_FACT in entry
    ) == [
        "recorded_on|datetime.all_at_midnight|",
        "recorded_on|datetime.datetime_separators|",
        "recorded_on|datetime.n_at_midnight|",
    ]
    # ...and the empty-bin listings are named the same way, and the
    # list is SHORTER than the four above rather than equal to it,
    # which is the whole of what "listed only where the description
    # names a stretch" means. A run that listed it on every numeric
    # column would pass a count and fail here.
    assert sorted(
        entry for entry in listings if EMPTY_BIN_FACT in entry
    ) == EMPTY_BIN_LISTINGS
    # ...and the edges beside them, on the SAME columns and no others:
    # the two are one fact in two keys and a run that listed one
    # without the other would leave a reader told about the stretches
    # and not about where they really lie.
    assert sorted(
        entry for entry in listings if EMPTY_EDGE_FACT in entry
    ) == EMPTY_EDGE_LISTINGS
    for name, digest in NARROW_COLUMN_DIGESTS.items():
        cells = twin.columns[twin.names.index(name)]
        # Sorted: the cells a column holds, wherever its rows stand.
        found = hashlib.sha256(
            "\n".join(sorted(cells)).encode("utf-8")
        ).hexdigest()[:32]
        assert found == digest, (
            f"the twin's {name!r} column changed against the frozen "
            "baseline, so the demonstration's cells moved for a reason "
            "that has nothing to do with the column added beside them. "
            "Satisfy yourself the new cells are the ones the method "
            "requires before re-recording, exactly as the twin digest "
            f"below asks. New digest: {found}"
        )
    for name, digest in NARROW_COLUMN_ORDER_DIGESTS.items():
        cells = twin.columns[twin.names.index(name)]
        # As written: where each cell stands is part of what is pinned.
        found = hashlib.sha256("\n".join(cells).encode("utf-8")).hexdigest()[:32]
        assert found == digest, (
            f"the twin's {name!r} column holds its cells in a different "
            "order against the frozen baseline. If the sorted digest above "
            "held, no cell changed and only where cells stand moved: find "
            "the change in the arrangement (method G2.1) before "
            f"re-recording. New digest: {found}"
        )


def _described_narrow(folder: pathlib.Path) -> contract.Profile:
    """The demonstration as it stood BEFORE the joined column joined."""
    path = fixtures.write(folder, "narrow.csv", fixtures.every_role_table())
    table = reading.read_table(str(path), small_cell_floor=11)
    document = profile.build_document(
        table, taxonomy.Settings(small_cell_floor=11), ["record_code"]
    )
    document["created_with"] = NORMALIZED_VERSION
    written = fixtures.write_profile(folder, "narrow-profile.json", document)
    return contract.load_profile(str(written))


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

    THE SMALLEST GROUP IS DECLARED, AND ELEVEN IS THE RUN THIS FILE
    PINS. The owner lowered the shipped `small_cell_floor` to one (plan
    amendment A-P4-37), and at a floor of one nothing is ever held back:
    no level is pooled, no spelling is withheld, no group is suppressed
    (contract invariant C5-S13). This golden is the only place where one
    whole run over a table of every role -- description in, twin, report
    and quality report out -- is pinned byte for byte, and a run that
    holds nothing back would leave the pooled and withheld paths of the
    generator, the report and the census unpinned in every cell of the
    CI matrix. So the floor these bytes were recorded at is asked for by
    name: at eleven this description still suppresses levels on two
    columns and withholds spellings, and the twin, the report and the
    quality report below are the same bytes they have always been. The
    floor of one is not left untested by that choice -- it is the
    subject of `tests/test_p3v5f1_floor_one.py`, which is where it
    belongs.
    """
    folder = tmp_path_factory.mktemp("twin-golden")
    # THE JOINED COLUMN IS IN THIS GOLDEN, and it was not until
    # residual R-P4-62's landing. The shared table excludes the one
    # role that carries a blood pressure, so a joined-only change in
    # the twin's BYTES -- the thing this golden exists to catch -- was
    # outside it (review item P4-A2-R3-F4). The role needs a
    # declaration, so the combined table is used and the declaration is
    # passed; the documented command above carries it too.
    table_path = fixtures.write(
        folder, "table.csv", fixtures.every_role_and_joined_table()
    )
    table = reading.read_table(str(table_path), small_cell_floor=11)
    document = profile.build_document(
        table,
        taxonomy.Settings(small_cell_floor=11),
        ["record_code"],
        [],
        [fixtures.JOINED_COLUMN],
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
    # FOURTEEN since the joined column joined this demonstration
    # (review item P4-A2-R3-F4): the shared table excludes the one role
    # that carries a blood pressure, so a joined-only change in these
    # bytes was outside the golden that exists to catch one.
    assert len(built.names) == 14
    assert built.write_header is True
    assert built.seed == GOLDEN_SEED
    # The word budget is a fixed function of the published facts (method
    # G4.3), so it moves only when the plan for this description moves.
    # Pinned beside the bytes because "the run spends a different number
    # of words" is a different failure from "the run writes different
    # cells", and a reader is owed the difference.
    # FOUR THOUSAND EIGHT HUNDRED AND SEVENTY-THREE since landing L7,
    # and 5,133 before it: one stream feeds every column in order, so
    # this count moves by exactly what a column's own plan draws.
    # G5.2's grain rule divides each position of the joined column by
    # that position's own count of different NUMBERS rather than by the
    # whole cell's count of different CELLS -- 120 and 100 here against
    # 240 -- so the two positions between them draw 260 words fewer.
    assert built.words_drawn == 4873
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
        "pressure",
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
# THE THREE DIGESTS MOVED ON 2026-09-04 (amendment A-P4-55), and what
# moved is recorded here rather than left to the diff. The count of
# different NUMBERS became an obligation and the separation pass was
# widened to meet it, so the generator places this description's values
# differently. MEASURED on the new run before re-recording, which is
# what the sentences below ask for:
#
#   * the twin: 240 rows, 492 checks, **417 held and 75 inside their
#     bounds, nothing missed**;
#   * every numeric column now meets its published count of different
#     numbers exactly -- `visits` 10 of 10, `reading` 178 of 178,
#     `amount` 238 of 238;
#   * the report and the quality report say MORE than they did, not
#     less: four obligations moved from the census to the checks and
#     none was dropped, which the two baselines above assert by
#     identity.
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
#
# RE-RECORDED FOR THE SECOND DECLARATION (2026-08-24, plan P4-D19), and
# THIS ONE MOVED ALONE: the twin, the report and the quality report
# below all held, byte for byte, which is what a change to what the
# description RECORDS looks like as opposed to a change to what it says
# about the data. The settings block gained one key -- `forced_codes`,
# the list of columns declared with `--code`, empty in this run -- and
# nothing else in the document moved. HOW IT WAS CHECKED: the new
# document was written out again with that one key deleted from its
# settings block, and hashed; the result is the digest this one
# replaces --
# c527236bac66d2b312529a829dc157e753b71ed6bd6a878e4f8424f281819adf
# -- so the single added key is the whole of the difference.
#
# The floor is a separate matter and did NOT move these bytes: the
# fixture now ASKS for the eleven that used to be the default (plan
# amendment A-P4-37 lowered it to one), so the description this file
# pins describes the same table under the same rules it always did.
#
# RE-RECORDED FOR THE FOURTH DECLARATION (2026-08-27, plan P4-D26), and
# THIS ONE MOVED WITH THE TWO REPORTS AND NOT WITH THE TWIN. The
# settings block gained one key -- `forced_decimal_commas`, the columns
# declared with `--decimal-comma`, empty in this run -- and nothing
# else in the document moved. HOW IT WAS CHECKED, by this file's own
# procedure: the new document was written out again with that one key
# deleted from its settings block, and hashed; the result is the digest
# this one replaces --
# 21b0cf0a92fbf0d5911a288e47eff11e0c2048b2eac77015ce3cbeb3165dee0a
# -- so the single added key is the whole of the difference.
#
# GOLDEN_TWIN_SHA256 BELOW DID NOT MOVE, and that is the load-bearing
# observation of this re-recording. The same landing changed the
# numeric-spelling censuses, the rank-agreement helper and the joined
# approximations; if any of them had reached a cell of an UNDECLARED
# column, the twin's own bytes would have moved. They did not.
# RE-RECORDED 2026-08-31 for plan amendment A-P4-47, and the counted
# difference was read first: the description gains NINE lines and loses
# none, every one of them `"shape_form_cells": 0` on a published level
# of `region`, `answer`, `batch` and `note`. Nought on all nine because
# every label of this demonstration is letters alone, and letters are
# one kind where a written form carries two -- so the new key adds a
# fact here and moves no number that was already on the page.
#
# GOLDEN_TWIN_SHA256 BELOW DID NOT MOVE, again, and that is what says
# the change is to what a description RECORDS rather than to what the
# twin holds: the demonstration's twin is byte-identical, measured
# against the tree at the commit before this landing.
# RE-RECORDED 2026-09-04 for residual R-P4-138, and the counted
# difference was read first: every numeric block gains `empty_edges`,
# and SIX blocks of this description carry the key while ONE carries
# anything -- the count column, whose nine empty bins lie between
# consecutive whole numbers, so its pairs are [0,1] ... [8,9]. The
# same procedure as before: building these bytes, deleting that one
# key from every block and writing again reproduces the digest this
# one replaces --
# 050bc4c6f684af271f9a46a8c583c2151094311ee04e95500f9d0e05e97a1f16
# -- character for character, so the single added key is the whole of
# the difference.
#
# GOLDEN_TWIN_SHA256 BELOW DID NOT MOVE, and on this landing that is
# the load-bearing observation twice over. The value stage now walks
# from the published EDGES instead of from the bin edges, and on this
# description it reaches the same cells: the one block with a stretch
# is whole-numbered with its gaps between consecutive integers, where
# the edge and the bin edge ask for the same value. A description whose
# clusters sit further apart is where the two differ, and
# tests/test_p4d32_empty_bins.py is where that is measured.
# RE-RECORDED 2026-09-05 for plan P4-D36, and the difference was
# COUNTED and read first. The affixed role's split put the space
# between a number and its unit inside the CORE, and the value stage
# rewrites a core as a number and has no space to write -- so every
# cell of the demonstration's `dose` column came back `165.1mg` where
# the source reads `165.1 mg`. All 240 of them move, and they move to
# what the source says. The description gains three keys on that one
# column -- the wrapper set and the two counts of different cores --
# and no count, statistic, label, role or spelling of any other column
# changes.
# RE-RECORDED 2026-09-10 for landing L19, residual R-P4-72, and ONE
# STRING OF ONE COLUMN moved. `dose`'s affixed remark (contract NF35)
# told its reader "if these are codes rather than measurements, run the
# command again with --identifier and no value of this column will be
# published at all" -- which is the OPPOSITE declaration: `--code`
# keeps every code with the rows that carried it, `--identifier`
# publishes none of them, so a person doing exactly as the sentence
# said threw away the distribution they were trying to keep. NF43 shed
# the same flaw at landing L16; this one was pinned by a frozen
# reference vector and had to move with the oracle, which is what this
# landing did. No count, statistic, label, role, spelling or cell
# changed on `dose` or on any other column.
# RE-RECORDED 2026-09-14 (plan P4-D39): two keys added to `recorded_on`,
# `all_at_midnight: false` and `datetime_separators: {}`, and nothing else;
# the twin digest below did not move.
# RE-RECORDED 2026-09-15 at the integration of landings 2b.1 to 2b.5, which
# carries both causes below at once. Diffed against the integrated
# description before landing 2b.2 merged, only 2b.2's twelve keys moved;
# against landing 2b.2's own, only `n_at_midnight: 0`. The twin digest HELD.
# RE-RECORDED 2026-09-15 (landing 2b.3): one key added to `recorded_on`,
# `n_at_midnight: 0`, the count of values at midnight a column that writes
# no clock publishes as nought; read as a diff of the two documents,
# nothing else moved, and the twin and report digests below did not move.
# RE-RECORDED 2026-09-15 (landing 2b.2, plan P4-D41): every numeric block
# of the description gained `negative_form: "minus"` and the census
# `decimal_plus: {}` -- six blocks, twelve keys, and nothing else moved
# when the two documents were diffed against 53bb012. The twin digest below
# HELD: the twin's bytes are identical.
# RE-RECORDED 2026-09-15 (landing 2b.6), and the cause is ONE KEY of one
# column block: `n_at_midnight` on the demonstration table's column of
# dates (this file describes the same fixed table) went from `0` to `null`. A published nought could not be told
# from a count suppressed for naming one person, and being able to tell
# them apart IS being told that count -- measured on 400 moments a day
# apart at noon against the same 400 with a single row moved to
# midnight, whose two descriptions differed in that key and nowhere
# else. Nothing else about the document moved, and the twin's own bytes
# did not move at all (GOLDEN_TWIN_SHA256 below is untouched).
# RE-RECORDED AGAIN 2026-09-15 (landing 2b.6), for the cause recorded
# beside the profile golden in tests/test_profile_document.py: the
# column of dates gains the four written-form censuses, all four empty
# on a column read as `iso-date`. THE TWIN'S OWN BYTES DID NOT MOVE --
# GOLDEN_TWIN_SHA256 below is untouched -- and that is the load-bearing
# half of this re-recording: the reversal of owner decision 5 changes
# what a twin of a month-first, textual, compact, two-digit, dotted,
# slashed-ISO, quarter or zulu column is written as, and this
# demonstration holds none of those.
# RE-RECORDED 2026-09-16 (the repair pass of landing 2b.6), for the
# cause recorded beside the profile golden in
# tests/test_profile_document.py: the `reading` column's stand-in
# decision now names the published spelling its own pass took out
# (`"spellings": ["-999"]`, contract V5, plan P4-D63). THE TWIN'S OWN
# BYTES DID NOT MOVE -- GOLDEN_TWIN_SHA256 below is untouched -- because
# no column of this demonstration has a declaration and a judgement
# sharing one candidate, which is the case the key was published for.
# RE-RECORDED 2026-09-15 (landing 2b.7, plan P4-D65.1 and P4-D65.2):
# every numeric block gained the two mixed-convention censuses
# `negative_notations` and `thousands_marks`, both EMPTY because no
# column of this demonstration wears two notations or two marks, and
# `decimal_plus` moved from `{}` to `{"(unavailable)": 0}` wherever the
# column writes a cell with a point. The profile golden in
# tests/test_profile_document.py diagnoses the same change, and the
# twin's own digest below did NOT move: an empty census names no
# convention, so the generator writes the published majority for every
# cell exactly as it did before these keys existed.
# RE-RECORDED AT THE MERGE OF LANDINGS 2b.6 AND 2b.7 (2026-09-16), for
# the cause recorded beside the profile golden: diffed both ways, the
# description moved against each side only in the other landing's keys.
# THE TWIN'S OWN BYTES DID NOT MOVE from landing 2b.6's recording --
# GOLDEN_TWIN_SHA256 is 2b.6's -- because 2b.7's censuses are empty here
# and an empty census writes the published majority, as both landings
# measured.
# RE-RECORDED 2026-09-16 (landing 2b.12, plan P4-D85). The description
# moved by ONE LINE -- `comment` publishes `n_missing_blank: 160` where
# it published 0 -- diffed against the base commit, with nothing else
# changed.
#
# GOLDEN_TWIN_SHA256 BELOW DID NOT MOVE, and on this landing that is the
# load-bearing observation. The demonstration's free-text column holds
# 160 absent cells and every one of them held NOTHING, so the twin wrote
# them empty before this landing and writes them empty after it; the
# rule that changed reaches a column's absent cells only where they wore
# one of synthtwin's own words, and this column's wore none. Measured,
# not argued: the twin of the demonstration is byte-identical to the
# base commit's (6a88f23f629b53e506371f7f632709977e26d7155e8ee1cd357146c2e51a5c1c).
#
# THE REPORT DIGEST MOVED, AND IT NOW SAYS MORE RATHER THAN LESS, which
# is the condition this file sets before a report digest may be
# re-recorded. Two lines -- "the description names no spelling for these
# cells, so this report names none either" -- became one: "160 cell(s)
# with nothing written in them". The sentence it replaces was true only
# because the class had emptied the count the report wanted to print.
# THE THREE DIGESTS MOVED AT LANDING 2b.18, and what moved is recorded
# here rather than left to the diff. The demonstration's `record_code`
# column is declared an identifier, and the identifier role gained a
# seventh published key: `layout_forms`, the census of positional
# layouts (contract 7.12, plan P4-D120). So the DESCRIPTION moved
# first, and the twin and the quality report follow it:
#
#   * the description gained one key on one column -- the census
#     `{"@%%%%%": 12}` -- and nothing else moved in it;
#   * the TWIN moved because the generator now reads that census and
#     writes each record number to its published layout, which is the
#     whole of what the landing does. MEASURED on the new run before
#     re-recording: every `record_code` cell wears the published
#     layout, the column's own pattern matches every twin row where it
#     matched none before, and both the twin and the real table pass
#     the description at exit 0;
#   * the QUALITY REPORT says MORE and not less: it carries one
#     obligation it did not carry, `identifier.layout_forms`, and drops
#     none -- which the wide baseline above asserts by identity.
# THE DESCRIPTION DIGEST MOVED AGAIN AT LANDING 2b.18'S SECOND PART, and
# ONLY it: the two count blocks gained the empty census
# `number_spellings: {}` (contract 7.13, plan P4-D123), which is the whole
# of the diff against 2e2ec8f. MEASURED: the twin and the quality report
# digests below come back character for character, because an empty
# census writes nothing differently and sets no obligation.
# RE-RECORDED AT THE MERGE OF LANDING 2b.8 INTO LANDINGS 2b.6 AND 2b.7
# (2026-09-16), for the cause recorded beside the profile golden, plus
# landing 2b.8's `layout_forms` `{"@%%%%%": 240}` on `record_code`.
# Diffed both ways, the description moved against each side only in the
# other side's keys.
# RE-RECORDED 2026-09-15 for plan P4-D86 (owner ruling: the twin is
# written the way its source file was). `source` gained ONE key,
# `dialect`, the written form of the demonstration file -- a comma, UTF-8
# with no mark, line feeds on every line, minimal quoting in every column,
# and the rows sorted by `record_code`. HOW IT WAS CHECKED, by this file's
# own procedure: the new document written out again with that one key
# deleted hashes to the description of commit 53bb012 built the same
# way, so the single added key is the whole of the difference.
# RE-RECORDED 2026-09-15 again, at the repair of landing 2b.9:
# `source.dialect` gained `blank_lines_spread: null` and
# `line_endings_spread: []` (past their caps those facts are published
# counted instead of the file being refused). This description with those
# two keys deleted and written out again hashes to
# abbe3bcaab895e50d741748cf0af427492f2dd54587a855dcb635e27ade88c4e, the
# digest this one replaces; the twin, report and quality digests below did
# not move.
# RE-RECORDED 2026-09-15 at the merge of landing 2b.9 into landings
# 2b.1-2b.5, and NO CELL CHANGED. The sorted digests above moved because
# 2b.9 changed what they are taken OVER -- the cells sorted, not the cells
# as written -- and because 2b.9 sorts the twin's rows. MEASURED rather
# than argued, column by column against a git archive of the base commit
# 367e1d7 at this seed: all thirteen columns hold an IDENTICAL multiset of
# cells, and the twin's rows agree as a multiset while differing in order,
# so whole rows moved and nothing was written differently. `unused` and
# `batch`, whose cells cannot be told apart, are unchanged even in order.
# RE-RECORDED 2026-09-15 for plan P4-D76, and ONLY WHERE CELLS STAND
# MOVED. The demonstration's `record_code` is declared with
# `--identifier`, and landing 2b.9 published a row order for it -- which
# is a fact about a declared identifier's own values and is exactly what
# P4-D76 withdraws. MEASURED rather than argued: the published written
# form differs in ONE key of its twenty-two, `row_order`, which was
# `{collation: text, column: 1, direction: ascending}` and is now null;
# every column's cells are the same MULTISET as before, the sorted
# digests above did not move, and every order digest here is once more
# the one commit 367e1d7 froze -- the twin's rows have returned to the
# arrangement they had before the identifier was sorted on.
# RE-RECORDED 2026-09-15 for plan P4-D77 (reading a spreadsheet
# workbook), and NO CELL OF THE TWIN MOVED. `source` gained ONE key,
# `workbook`, and the demonstration table is a DELIMITED file, so its
# value here is `null`. MEASURED by this file's own procedure: this
# description written out again with that one key deleted hashes to
# a32bf775c2373134793c7b67f58cc8a5515ecfd4f149919ce339f23d89d8a7bd,
# the digest this one replaces, so the single added key is the whole of
# the difference. The twin, report and quality digests below did not
# move, which is the other half of the same statement: the generator is
# handed one more key and writes exactly what it wrote before.
# RE-RECORDED 2026-09-16 for plan P4-D81 (review item CODEX-2), and NO
# CELL OF THE TWIN MOVED. `settings` gained ONE key,
# `forced_metadata_rows`, how many rows under the column names the
# person declared to DESCRIBE those columns; this run declares none, so
# its value here is 0. MEASURED by this file's own procedure: this
# description written out again with that one key deleted hashes to
# b0537b40dc8141a5099a763e3cca88e925c4339e18277ee13e6e7f7e01426ee0,
# the digest this one replaces, so the single added key is the whole of
# the difference. The TWIN digest below did not move -- it is
# 494ae9dd2eef2b3a703e456a506224b1d799c447851666e03d089aef706fe84f on
# this commit and on the one before it -- which is the other half of
# the same statement: the generator is handed one more key and writes
# exactly what it wrote before.
# RE-RECORDED 2026-09-16 for plan P4-D110 (review item CODEX-4), and NO
# CELL OF THE TWIN MOVED. `settings` gained ONE key, `forced_delimiter`,
# the delimiter the person declared; this run declares none, so its
# value here is the empty string. MEASURED by this file's own
# procedure: this description written out again with that one key
# deleted hashes to
# d6ddc7ad0ec16c4f05865eca3e189b7c4d492d26f904ce35a390a0f7c7ace5d9,
# the digest this one replaces. The twin, report and quality digests
# below did not move.
# RE-RECORDED AT THE MERGE OF LANDING 2b.10 INTO LANDINGS 2b.6 TO 2b.8
# (2026-09-16), for the cause recorded beside the profile golden:
# diffed both ways, the description moved against each side only in the
# other side's keys.
# RE-RECORDED AT THE MERGE OF THE TWO RULING BRANCHES INTO THIS ONE,
# carrying all three moved values and NO CELL OF THE TWIN MOVING for any
# of them. Read as a diff against 039df54: `suppressed_level_counts`
# leaves the four label columns, `region` (`[7]`), `answer` and `batch`
# (`[]`) and `note` (182 sizes), because the sizes read off each pool are
# the sizes the table had (item 2, option A; plan P4-D201);
# `record_code` gains exactly `"layout_prefixes": {"(column)": "R"}`,
# whose 240 cells are `R` and five figures (item 1; plan P4-D202); and
# `reading`'s `field_widths` published `{"2": 57, "3": 165,
# "(withheld)": 5}` and now publishes `{"2": 57, "3": 170}`, the five
# cells at widths too rare to name counted into the commonest width
# (plan P4-D222, which replaces plan P4-D221's recording).
# RE-RECORDED AT THE POOLED-SCALE LANDING (2026-09-21, plan P4-D301,
# ledger K-2B-50), and NO CELL OF THE TWIN MOVED. The four label columns
# gained ONE key, `suppressed_numbers`, the scale of the numbers the
# floor held back, and all four publish the state that says nothing,
# because none of their held-back levels holds a number. MEASURED by the
# profile golden's own procedure (tests/test_profile_document.py): the
# description written out again with that one key deleted hashes to the
# digest this one replaces. The TWIN digest below did not move, which is
# the other half of the same statement: the generator is handed one more
# key and writes exactly what it wrote before.
# RE-RECORDED BY THE OWNER'S DECISION OF 2026-09-21 (plan P4-D302), and
# GOLDEN_TWIN_SHA256 DID NOT MOVE. The pool of held-back numbers
# publishes a mean and no longer a population spread, so the DESCRIPTION
# lost a key on each of this demonstration's four label columns, the
# twin's REPORT lost the record that measured the spread and rewrote the
# held-back sentence to say that an average over the column's numbers is
# about the reader's table and a spread is not, and the QUALITY report
# lost the obligation that compared the spread. Not one cell of the twin
# moved: none of this demonstration's columns publishes a pooled scale
# at all, so nothing placed any of its made-up numbers before or after.

# RE-RECORDED BY PLAN P4-D340. The description gained the settings key
# `person_columns`, reading `[]` on this demonstration because nothing
# was declared with --identifier, so its population is counted in rows.
# The twin's cells did not move -- no generator rule reads that key --
# and GOLDEN_TWIN_SHA256 is unchanged; the REPORT digest moved because
# the report quotes the description's own bytes back.
GOLDEN_DESCRIPTION_SHA256 = (
    # RE-RECORDED FOR THE NUMERIC TAIL (stage 3, landing 3.3). Every
    # numeric block now carries `tails` and `bin_groups`; the rungs
    # whose type-7 reading would touch one of the outermost eleven
    # values are null, and the two ends with them unless a group of
    # eleven rows holds one (contract 6.7a). The pages were read before
    # this was recorded: the twin's report names the four new
    # approximated facts of every numeric column and loses no line it
    # had, and the quality report carries the same obligations plus
    # those four per column. Nothing else about any role moved.
    # AND RE-RECORDED AT THE INTEGRATION OF STAGE 3'S FIVE LANDINGS
    # (2026-09-23). **IT WAS ALREADY STALE**: the date and clock tail
    # merge re-recorded the twin and the quality report below and left
    # this one and the report's alone, so the branch this merge lands on
    # was red here. Read as a leaf-by-leaf diff of the description
    # against that tree: 329 leaves ARRIVE -- `bin_groups` on every
    # numeric block and its parts, and each side's `percent`, `rows`,
    # two distances and, on two positions of the joined column, its
    # listed `values`; 10 LEAVE, every one a `value_histogram` bin the
    # groups replace; and 64 MOVE, every one a rung the rule withholds
    # (`min`, `max`, `p01`, `p99` and `p02` to `p04`, `p96` to `p98`)
    # going null, plus the publication notes shifting by one because a
    # numeric column gains the histogram-withheld note. No key of any
    # other role moved.
    # AND RE-RECORDED BY PLAN P4-D346 AND P4-D347 (2026-09-23), read as
    # a diff against the tree above before it was written. THE
    # DESCRIPTION loses exactly three leaves and gains none: the false
    # `histogram_publishes_no_shape` note on `visits`, `reading` and
    # `amount`, each of which published 9 to 14 bin groups while saying
    # its shape was not published (NF49). No other key of any role
    # moved. THE TWIN moves 44 cells, every one the second number of the
    # joined blood-pressure column: `contract._listed_counts` now gives
    # each value of a listed tail at least the listing rule's own number
    # of rows, so the twin's own tail is one that rule would list too.
    # THE REPORT moves the same column's construction windows, which
    # narrow with the counts. THE QUALITY REPORT holds four more exact
    # obligations -- the four joined `tails.*.rms_distance`, met by
    # equality now rather than inside a window -- carries the same two
    # missed ones, and prints six fewer "was found to hold" lines,
    # every one a `tails.*.values` whose measured side is withheld from
    # this pass on.
    # AND RE-RECORDED FOR ONE PUBLISHED SENTENCE (the review of
    # 2026-09-23, item 7). The description carries its remarks, and the
    # one a column no reading fits carries said that describing it from
    # the part that does read "would publish an average, a smallest and a
    # largest value" -- two values a measurement column has not published
    # since stage 3. ONE LEAF MOVES, the first remark of the column no
    # reading fits, and it is the only difference in the document --
    # measured as a leaf-by-leaf diff, 0 arriving and 0 leaving. The
    # TWIN's own digest
    # above did not move, so not one cell changed with it; the report
    # golden moves by the same one line, and the quality report not at
    # all.
    "f7feeefc1b7083ce631bccb8f7bbed2abdfa98ccefe49f42ef2e9174d772b41d"
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
# RE-RECORDED TWICE ON 2026-09-01: once for landing L7 (plan decision
# P4-D31) and again for that landing's first review round (amendment
# A-P4-49). The SECOND re-recording was read column by column against
# the first: the word count is unchanged at 4,873, THIRTEEN OF THE
# FOURTEEN columns are byte-identical, and the fourteenth is `pressure`
# again. Its 240 readings are all different on both sides, which is the
# obligation contract 9.8 puts on it, and its positions hold 101 and 83
# different numbers on both. What moved inside it is the pairing: the
# walk no longer scores an agreement inside the window the validator
# accepts, refuses a swap that takes a pair out of that window unless
# an exact fact gains, and stops on the obligations by name rather than
# on a fixed distance.
#
# The account of the FIRST re-recording, which still holds:
# GOLDEN_DESCRIPTION_SHA256 ABOVE DID NOT MOVE, so the producer is
# untouched and what changed is what the generator makes of the same
# bytes. THIRTEEN OF THE FOURTEEN COLUMNS ARE BYTE-IDENTICAL and the
# fourteenth is `pressure`, the joined one -- which is also the LAST, so
# the 260-word drop in its budget shifts no other column's share of the
# stream. Its 240 readings are all different before and after, which is
# the obligation contract 9.8 puts on it; what moved inside it is that
# each position is now laid out by its own count of different numbers,
# so the first holds 101 different numbers where it held 120 and the
# second 83 where it held 100, against 120 and 100 published. That fall
# is residual R-P4-120 becoming visible rather than arriving: the count
# this rule replaces equals the number of CELLS on an all-different
# column, so a position used to get one stratum per cell and could not
# collide. The count of different CELLS -- the fact `synthtwin validate`
# checks exactly -- is 240 of 240 on both sides.
# RE-RECORDED at the integer-grid landing (method G6.5a). The pass that
# keeps two strata from being written as one cell asked the
# fraction-width census for the column's grid, and a whole-number
# column's census is EMPTY -- so the pass declined every such column.
# WHAT THE REPORT SAYS ABOUT THE MOVE, read before re-recording: the
# twin now holds 177 different values of a published 178 where it held
# 162, and the approximation envelope closes from `162 to 178` to
# `177 to 178`. Three of the four moments named beside it move CLOSER
# to their published value and the fourth by a ten-thousandth. No
# sentence, obligation or verdict leaves the report, and the check
# census is unchanged at 416 wide and 407 narrow -- so the report says
# more than it did, which is the direction the assertion below asks
# about. The independent oracle carries G6.5a too and its frozen
# vectors agree, which is what makes these bytes the METHOD's answer
# rather than the implementation's.
# RE-RECORDED 2026-09-05 for plan P4-D36, and the difference was
# COUNTED and read first. The affixed role's split put the space
# between a number and its unit inside the CORE, and the value stage
# rewrites a core as a number and has no space to write -- so every
# cell of the demonstration's `dose` column came back `165.1mg` where
# the source reads `165.1 mg`. All 240 of them move, and they move to
# what the source says. The description gains three keys on that one
# column -- the wrapper set and the two counts of different cores --
# and no count, statistic, label, role or spelling of any other column
# changes.
# RE-RECORDED at landing 2b.1 (2026-09-15): the `amount` and `dose`
# columns moved for the causes recorded beside their column digests
# above, and no other column's cells moved.
# RE-RECORDED at landing 2b.6 (2026-09-15), and this time the twin's
# bytes DID move, where the reversal of owner decision 5 left them
# alone. The demonstration's `recorded_on` column is read as `iso-date`,
# so writing it in its source's own form changed nothing; the PLACEMENT
# of its ranks is what changed. Method G7.3 pins the nine interior rungs
# to their published values and draws every other rank inside the gap
# between the pinned ranks either side of it, because one cell per rank
# inside its own slice gave every day almost exactly its expected count
# -- measured across 54 runs, a per-day count variance of 0.057 to 0.514
# of the real column's -- and put every published rung a day or more
# early. Only `recorded_on`'s cells move: no other column of the
# demonstration is a column of dates, and the word budget per column is
# unchanged, so nothing downstream of it shifts either.
# RE-RECORDED at landing 2b.18's repair pass (2026-09-16): `record_code`
# moved for the cause recorded beside its column digest above -- the step
# a layout's walk starts at and the stride it takes (plan P4-D128) -- and
# no other column's cells moved; the description and quality report
# digests held.
# RE-RECORDED AT THE MERGE OF LANDING 2b.8 INTO LANDINGS 2b.6 AND 2b.7
# (2026-09-16), and BOTH SIDES HAD MOVED THE TWIN, each in its
# own column. Diffed cell by cell: against the tree before the merge only
# `record_code` moved (240 cells, written to their published layout);
# against landing 2b.8's own tree only `recorded_on` moved (214 cells,
# placed on the pinned rungs of landing 2b.6). No other cell moved.
# RE-RECORDED 2026-09-15 for plan P4-D86, and ONLY THE ORDER OF THE ROWS
# MOVED. The demonstration table is sorted by `record_code`, so the
# description now publishes that row order and the twin keeps it: its
# rows are sorted by `record_code`, where the twin of commit 53bb012 was
# not. MEASURED at this seed against a git archive of 53bb012: the header
# line is the same and the two twins hold the same lines as a multiset,
# so no cell was written differently; whole rows moved together.
# RE-RECORDED 2026-09-15 at the merge of landing 2b.9 into landings
# 2b.1-2b.5, and NO CELL CHANGED. The sorted digests above moved because
# 2b.9 changed what they are taken OVER -- the cells sorted, not the cells
# as written -- and because 2b.9 sorts the twin's rows. MEASURED rather
# than argued, column by column against a git archive of the base commit
# 367e1d7 at this seed: all thirteen columns hold an IDENTICAL multiset of
# cells, and the twin's rows agree as a multiset while differing in order,
# so whole rows moved and nothing was written differently. `unused` and
# `batch`, whose cells cannot be told apart, are unchanged even in order.
# RE-RECORDED 2026-09-15 for plan P4-D76, and ONLY WHERE CELLS STAND
# MOVED. The demonstration's `record_code` is declared with
# `--identifier`, and landing 2b.9 published a row order for it -- which
# is a fact about a declared identifier's own values and is exactly what
# P4-D76 withdraws. MEASURED rather than argued: the published written
# form differs in ONE key of its twenty-two, `row_order`, which was
# `{collation: text, column: 1, direction: ascending}` and is now null;
# every column's cells are the same MULTISET as before, the sorted
# digests above did not move, and every order digest here is once more
# the one commit 367e1d7 froze -- the twin's rows have returned to the
# arrangement they had before the identifier was sorted on.
# The twin is now BYTE-IDENTICAL to commit 367e1d7's, which is the
# whole of the claim: the only thing landing 2b.9 changed about this
# twin was the row order it took from a declared identifier.
# RE-RECORDED AT THE MERGE OF LANDING 2b.10 INTO LANDINGS 2b.6 TO 2b.8
# (2026-09-16), and THE TWIN DID NOT MOVE: its bytes are the tree's
# before the merge, because landing 2b.10's twin of this demonstration
# is byte-identical to commit 367e1d7's and its written form here is
# UTF-8, comma, line feeds and a final line ending, which the twin
# already wrote.
# RE-RECORDED AT THE REPAIR OF THE STAGE-2b INTEGRATION (2026-09-16).
# Only `dose` moved, and only its values: its cores are written at one
# and at two places, and a census of several widths is now the grid of
# its commonest (method G5.2a step 1), so 228 cells took the value on
# that grid the ladder puts there. MEASURED against the tree before the
# repair: the same widths census (160 four-character and 80 five), the
# same 180 different cells, every other column byte-identical, and no
# verdict of the quality report moved.
# RE-RECORDED AT THE REVIEW OF 158c811 (2026-09-16, plan P4-D130), and
# ONLY `recorded_on` MOVED: 90 of its 240 cells, placed on the pins'
# places inside their days. Diffed cell by cell against a git archive of
# 158c811 at this seed; the description digest held.
# RE-RECORDED AT THE MERGE OF carried-fix-dates INTO THE INTEGRATION
# (2026-09-16): the two moves above compose and nothing else moves.
# Diffed cell by cell: against the integration repair only
# `recorded_on` (90 cells) differs, against the date branch only `dose`
# (228 cells); the description digest held on all three trees.
# RE-RECORDED 2026-09-16 (plan P4-D147, the repair of the final Codex
# review of the merge, item 6). ONE column moved: `pressure`, whose
# systolic position publishes 120 different values between the ends 100
# and 219 -- exactly 120 integers, a saturated grid -- and whose twin held
# 117 of them. G6.5a now gives such a grid its integers in order, each
# once, and the twin holds 120. Diffed column by column against a git
# archive of 158c811 at this seed: 50 cells of `pressure` differ, every
# other column is byte-identical, and with the fill withdrawn the twin is
# byte-identical to 158c811's.
# RE-RECORDED AT THE MERGE OF carried-fix-numbers (2026-09-16): the
# two moves compose. Diffed cell by cell: against the merged dates tree
# only `pressure` (50 cells) differs, against the numbers branch only
# `recorded_on` (90) and `dose` (228); the description digest held.
# RE-RECORDED AT THE REPAIR PASS AFTER THE FINAL SKEPTIC (2026-09-17,
# plan P4-D179): only `dose` moved, 12 cells, each written at the other
# of its two published widths with the census exact; the description
# digest held and no verdict of the quality report moved.
# RE-RECORDED FOR THE OWNER'S RULING OF 2026-09-17, item 1 (plan
# P4-D202): diffed cell by cell against the ruling's first part, only
# `record_code` moved, and every one of its 240 cells now opens with the
# published `R` -- `Z09235` became `R55235` -- with 240 different values
# before and after and every other column byte-identical.
    # RE-RECORDED AT THE CLOSE OF STAGE 3'S REVIEW (2026-09-24), for the
    # numeric robustness pass's item 3 and NOTHING else. G5.3b's five
    # constants were the fitted shape's moments over a UNIFORM `s` and
    # the rule read that shape at the tail's own `m` ROW MIDPOINTS: the
    # two are not the same number, so every tail fitted by a shape moved
    # by a last place or two when the constants became the moments over
    # those rows. READ CELL BY CELL against a git archive of 27b9915
    # before re-recording: 29 of the 3,360 cells of the wide twin move,
    # and every one of them is in `dose` (20), `amount` (8) or `reading`
    # (1) -- the three numeric columns whose tails are drawn by a fitted
    # shape. `visits` does not move, because eleven rows hold each of its
    # ends and the description publishes both; `record_code` does not,
    # because its tails publish NEITHER distance and are read without a
    # shape at all (plan P4-D349); no column of any other role moves.
    # Every moved cell moves one grid step or two -- `99.61` to `99.62`,
    # `183.1 mg` to `183.9 mg`, `20` to `21` -- each column keeps its own
    # count of different values (`reading` 179, `amount` 238, `dose` 180)
    # and no cell leaves the range its column already held.
GOLDEN_TWIN_SHA256 = (
    # RE-RECORDED FOR THE NUMERIC TAIL (stage 3, landing 3.3). Every
    # numeric block now carries `tails` and `bin_groups`; the rungs
    # whose type-7 reading would touch one of the outermost eleven
    # values are null, and the two ends with them unless a group of
    # eleven rows holds one (contract 6.7a). The pages were read before
    # this was recorded: the twin's report names the four new
    # approximated facts of every numeric column and loses no line it
    # had, and the quality report carries the same obligations plus
    # those four per column. Nothing else about any role moved.
    # RE-RECORDED AT THE MERGE OF THE TWO RULING BRANCHES INTO THIS ONE,
    # and the merged cells are each side's own: `recorded_on` holds the
    # published 84 different dates (plan P4-D192) and every one of
    # `record_code`'s 240 cells opens with the published `R`, `Z09235`
    # becoming `R55235` (plan P4-D202, owner ruling of 2026-09-17 item 1).
    # No other column moved from either side's recording.
    # RE-RECORDED FOR PLAN P4-D6.4 (the owner's ruling of 2026-09-15):
    # diffed cell by cell against a git archive of e53d5f4, exactly
    # thirteen cells moved, all in `reading`, each from blank to the
    # `-999` the real table wrote there; the description digest held.
    # RE-RECORDED AT THE INTEGRATION OF STAGE 3'S FIVE LANDINGS
    # (2026-09-23), and read cell by cell against the tree before it:
    # 212 of the twin's 3,360 cells differ and every one of them is in a
    # NUMERIC column -- `reading` 123, `pressure` 34, `dose` 30,
    # `amount` 25 -- while every categorical, date, clock, text and
    # record-number column is byte-identical. That is the numeric tail
    # rule and nothing else: those four columns are built from a ladder
    # that no longer runs to two published extremes.
    "e6437069e13a909f773402205cdfc89a77d246e80bfcc4fa03afee04d249a04e"
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
#
# RE-RECORDED 2026-08-27 (review item P4-G3-R1-F7). ONE PARAGRAPH of
# the preamble was reworded and nothing else: the page used to open the
# approximation section with "THE RANGE IS NOT A MARGIN AROUND THE
# DESCRIPTION'S VALUE", which stopped being true when method G12.9 gave
# the joined rank agreement a window of two hundredths either side of
# the published value -- a margin, exactly. The sentence now says a
# range is not ALWAYS a margin and keeps the warning the paragraph
# exists for: "inside the range" means the method kept its promise and
# never that the two numbers are close.
#
# CHECKED rather than assumed: the report was rendered before and after
# and the two diffed. Nineteen lines differ and every one of them is
# inside that paragraph. No count, no verdict, no fact and no order
# moved, and the description and twin digests were both untouched by
# this edit.
# RE-RECORDED 2026-09-01 with the twin above, and it follows from it:
# the twin's own cells moved, so every figure this report prints about
# the joined column moved with them. The report was read before it was
# recorded and it says no less than it did -- the same facts, the same
# order, with the joined column's achieved numbers restated.
# RE-RECORDED at the integer-grid landing, and the page moved only
# where the twin did. Diffed line by line against the run before it:
# three lines carrying "the twin holds" go 162 to 177 against a
# published 178, two envelope lines close from "162 to 178" to
# "177 to 178", and four moment lines move by less than a twentieth.
# Nothing else differs -- no sentence added, none removed, no verdict
# changed -- so the page says the same things about a better twin.
# RE-RECORDED 2026-09-05 for plan P4-D36, and the difference was
# COUNTED and read first. The affixed role's split put the space
# between a number and its unit inside the CORE, and the value stage
# rewrites a core as a number and has no space to write -- so every
# cell of the demonstration's `dose` column came back `165.1mg` where
# the source reads `165.1 mg`. All 240 of them move, and they move to
# what the source says. The description gains three keys on that one
# column -- the wrapper set and the two counts of different cores --
# and no count, statistic, label, role or spelling of any other column
# changes.
# RE-RECORDED 2026-09-09 for review round 4 of landing L14, item 4, and
# the report SAYS MORE than it did rather than less. Two records about
# the `dose` column named `n_distinct` and `n_distinct_folded` -- keys
# an affixed column does not publish. What it publishes is
# `n_core_distinct` and `n_core_distinct_folded`, which is AF7's
# substitution, and a person following the old names into the
# description found nothing under them. No record was added or removed
# and no measured value moved; two identifiers now name real fields.
# RE-RECORDED 2026-09-10 for landing L17b, plan amendment A-P4-58, and
# the report SAYS MORE than it did. `synthtwin profile` now writes a
# sixth file -- the questions file -- on every run, so the handling
# paragraph names six files where it named five, and the questions file
# is named among them. ONE PARAGRAPH moved and it is that one: no
# record, count, statistic, label, role, spelling or verdict changed,
# and the twin's own digest above held.
# RE-RECORDED 2026-09-10 for landing L19, residual R-P4-70, and the
# report SAYS MORE than it did -- one sentence of it was FALSE and is
# now true. The section heading named "how your table wrote the cells
# it left empty" among the things no twin can carry, and every column
# block said the twin writes every absent cell empty. Both were true of
# contract version 5; P4-D6.1 made the twin write each published
# `missing_by_source` spelling at its count and neither sentence moved
# with it. The heading now excludes them and, where some spelling of
# THIS description travels, says so; every published spelling line says
# which way it goes. On the demonstration table every hole is a blank
# or a judged `-999`, so no spelling travels and the per-column
# sentence is unchanged in substance -- what moved is the heading, the
# per-spelling marking, and the wrapping of one paragraph. No count,
# statistic, label, role, spelling or verdict changed, and the twin's
# own digest above held.
# RE-RECORDED AGAIN 2026-09-10, same landing, for residual R-P4-152,
# and this one makes the report say LESS in two places. Both removals
# were the CONTRADICTORY telling of a fact the page states twice.
# `seen_at` printed `n_distinct 121 -> 122` among the facts the twin
# could not meet, and four lines later printed the same fact as
# "allowed anywhere from 62 to 122: inside the range". For an
# approximated fact the publication IS the range, so a measurement
# inside a range that CONTAINS the published value is the fact held.
# It is still printed, with the published value, the achieved value and
# both ends of the bound; what is gone is the second, opposite reading
# of it.
#
# AND `recorded_on` KEPT ITS TWO, which is what makes this a repair
# rather than a silencing: it publishes 84, the twin holds 224, and its
# bound runs 106 to 240 -- the twin landed inside what the method
# promises and nowhere near what the description says, so a reader
# grouping rows by that column still meets the fact that they will see
# 224 groups where the real table has 84.
#
# The R-P4-70 paragraph added above also leaves this page: nothing in
# the demonstration description travels into its twin -- every hole is
# a blank or a judged `-999` -- so the sentence saying spellings are
# carried is not printed here. No count, statistic, label, role,
# spelling or verdict changed, and the twin's own digest above held.
# RE-RECORDED A THIRD TIME 2026-09-10, same landing, for residual
# R-P4-72: the report quotes `dose`'s remark back as "Note from the
# description", so the corrected NF35 sentence moves this digest with
# the description's. Nothing else on the page changed.
# RE-RECORDED 2026-09-11 for residual R-P5-1, and ONE PARAGRAPH moved
# because it was FALSE. Limit 2 said "If your table holds several rows
# per person, per visit or per site, THE TWIN DOES NOT: its rows are
# independent of each other." The twin does: the identifier role
# publishes `n_distinct_by_occurrences`, the multiset of how often each
# identity repeats, and the generator reproduces it -- measured on 335
# rows over 100 subjects with uneven visits, where the twin's group
# sizes match the real ones exactly (32 ones, 17 twos, 20 threes, 13
# fives, 18 eights). The error ran in the SAFE direction and was still
# worth repairing: a researcher with a repeated-measures design, told
# the twin holds no several-rows-per-person, could discard a twin whose
# group-size distribution was the one they needed.
#
# THE LIMIT IS NOT SOFTENED, and a test holds that half: which identity
# gets which count is arbitrary, which rows share one carries nothing
# further, the rows of a subject hold unrelated values, and anything
# that groups rows still behaves differently.
# RE-RECORDED 2026-09-14 (stage 2): the first limit's sentence about
# analysis code running on the twin is qualified, and no other line moved.
# RE-RECORDED at landing 2b.1 (2026-09-15): the achieved figures and
# windows of `amount` and `dose` follow their moved cells, the `amount`
# windows widen by half a hundredth for G12.2's grid unit, and every
# line still says inside.
# RE-RECORDED at landing 2b.1, part 2 (2026-09-15, residual R-P4-61):
# 122 lines of window ends move in their last digits and nothing else.
# The report now reads every window's widest stratum off the description
# (G5.6) and computes each end in the one operation order G12.2, G12.3
# and G12.3a state, which is what the quality report prints; the twin,
# every achieved figure and every inside-the-range verdict are unchanged.
# RE-RECORDED at landing 2b.6 (2026-09-15). It follows the twin digest
# above: `recorded_on`'s cells moved, so the approximated date rungs the
# report prints beside their windows moved with them -- and the rungs
# now sit ON their published values rather than a day or so below, which
# is what the report says. The report also carries one sentence it did
# not carry before, naming what a twin of a column of dates still does
# not reproduce: the weekday composition, the time of day, days the real
# column heaps values on, and a column of a few scheduled dates.
# RE-RECORDED 2026-09-16 (the repair pass of landing 2b.6), and the
# cause is the WINDOW the report prints beside each approximated date
# rung, on nine lines and nowhere else. A rank a rung is pinned to has
# no room to be drawn in, so it is now allowed no reading allowance
# either: `allowed anywhere from 2023-12-31 to 2024-01-01` is now
# `allowed anywhere from 2024-01-01 to 2024-01-01`, at each of the nine.
# The band it replaces was wide enough to admit a twin with every
# interior cell written one day EARLY -- the defect landing 2b.6 part 2
# repaired -- and this landing's own text said in four places that the
# window was a point while the code spent the allowance anyway. The twin
# is untouched, every achieved figure is unchanged, and the report says
# strictly more than it did.
# RE-RECORDED AT THE MERGE OF LANDING 2b.8 INTO LANDINGS 2b.6 AND 2b.7
# (2026-09-16), read as a diff against each side. Against the tree
# before the merge only landing 2b.8's line moved: the free-text column's
# holes are named as 160 cells with nothing written in them. Against
# landing 2b.8's own tree only landing 2b.6's lines moved: the date rungs
# on their published values with point windows, its sentence on what a
# twin of dates does not reproduce, and the n_distinct note it removed.
# RE-RECORDED 2026-09-15 for plan P4-D86. The paragraph on how the twin
# is written no longer says it is UTF-8 with newline line endings
# whatever the table was: it states the written form the description
# records -- here UTF-8 without a mark, fields separated by a comma, line
# feed endings and a line ending after the last line -- and that quoting,
# blank lines, the lines before the names and the row order follow the
# table too.
# RE-RECORDED 2026-09-15 at the merge of landing 2b.9 into landings
# 2b.1-2b.5, and NO CELL CHANGED. The sorted digests above moved because
# 2b.9 changed what they are taken OVER -- the cells sorted, not the cells
# as written -- and because 2b.9 sorts the twin's rows. MEASURED rather
# than argued, column by column against a git archive of the base commit
# 367e1d7 at this seed: all thirteen columns hold an IDENTICAL multiset of
# cells, and the twin's rows agree as a multiset while differing in order,
# so whole rows moved and nothing was written differently. `unused` and
# `batch`, whose cells cannot be told apart, are unchanged even in order.
# RE-RECORDED AT THE MERGE OF LANDING 2b.10 INTO LANDINGS 2b.6 TO 2b.8
# (2026-09-16), read as a diff against each side. Against the tree
# before the merge only the sentence on how the twin is written moved --
# it now names the written form the description records. Against landing
# 2b.10's own tree only landings 2b.6's and 2b.8's lines moved.
# RE-RECORDED AT THE REPAIR OF THE STAGE-2b INTEGRATION (2026-09-16):
# only the achieved values printed for `dose` moved, because its cells
# did (see the twin digest above). No sentence moved.
# RE-RECORDED AT THE REVIEW OF 158c811 (2026-09-16, plan P4-D130), read
# line by line against the report of 158c811 at this seed: two lines
# moved and nothing else, the number of different dates `recorded_on`'s
# twin holds -- 171 to 176, beside the description's 84 -- once for each
# of the column's two distinct counts.
# RE-RECORDED AT THE MERGE OF carried-fix-dates (2026-09-16): against
# the integration repair only the two `recorded_on` distinct counts
# moved (171 to 176), exactly the date branch's two lines.
# RE-RECORDED 2026-09-16 (plan P4-D147), for the twin's one moved column
# above: only the achieved values printed for `pressure`'s two positions
# moved -- the ninetieth and ninety-ninth rungs, the mean, the spread, the
# skew and the tail weight -- and every one still sits where it sat
# against its window. No sentence and no other column moved.
# RE-RECORDED AT THE MERGE OF carried-fix-numbers (2026-09-16): against
# the numbers branch only the achieved values of `recorded_on` and
# `dose` differ; against the merged dates tree only `pressure`'s.
# RE-RECORDED AT THE REPAIR PASS AFTER THE FINAL SKEPTIC (2026-09-17,
# plan P4-D180): the one paragraph that moved is the date column's, which
# said the twin writes the international form; it now says the twin keeps
# the column's own spelling. Diffed line by line: that paragraph alone.
# RE-RECORDED FOR THE OWNER'S RULING OF 2026-09-17 (plan P4-D201), read
# as a diff against 039df54: two lines moved and nothing else, the
# held-back labels' reason on `region` and on `note`, which now says the
# twin keeps how many there were and the rows they covered together and
# not the rows of each one.
    # RE-RECORDED AT THE CLOSE OF STAGE 3'S REVIEW (2026-09-24), and the
    # TWIN is what moved: the numeric robustness pass's item 3 refitted
    # G5.3b's shape over the tail's own rows. READ LINE BY LINE against
    # 27b9915 before re-recording: the report holds 864 lines before and
    # after, names the same 107 facts in the same order, and every one of
    # the 45 lines that moved is an ACHIEVED value or a window bound on
    # `reading`, `amount` or `dose` -- 24 "the description says / the
    # twin holds" lines and 21 "allowed anywhere from" lines. No line
    # arrives, none leaves, "inside the range" still stands 136 times,
    # and "outside the range" stands nought times as it did.
GOLDEN_REPORT_SHA256 = (
    # RE-RECORDED FOR THE NUMERIC TAIL (stage 3, landing 3.3). Every
    # numeric block now carries `tails` and `bin_groups`; the rungs
    # whose type-7 reading would touch one of the outermost eleven
    # values are null, and the two ends with them unless a group of
    # eleven rows holds one (contract 6.7a). The pages were read before
    # this was recorded: the twin's report names the four new
    # approximated facts of every numeric column and loses no line it
    # had, and the quality report carries the same obligations plus
    # those four per column. Nothing else about any role moved.
    # RE-RECORDED AT THE MERGE OF THE TWO RULING BRANCHES INTO THIS ONE,
    # carrying every side's moved lines: `recorded_on`'s two distinct
    # counts, 84 held against a window of 84 where 176 stood in one of 10
    # to 240 (plan P4-D192); `reading`'s three moments, as held (plan
    # P4-D183); the held-back labels' reason on `region` and on `note`,
    # which now says how many there were and the rows they covered
    # together and not the rows of each one (plan P4-D201);
    # `record_code`'s recounted prefix (plan P4-D202); and the deviation
    # `'reading' -- field_widths`, 170 cells at three figures described
    # and 165 held, whose five counted-in cells the twin writes at their
    # own widths (plan P4-D222).
    #
    # RE-RECORDED AT THE FINAL REVIEW OF 2026-09-18 (plan P4-D244), read
    # as a line-by-line diff against 7f9a52d: FOUR LINES ARE ADDED, TWICE
    # -- once in each of the two columns synthtwin made up entirely --
    # and not one other line of the report moved. They say that a
    # made-up value can be one the table also holds by chance, which the
    # review measured: 40 of 2,000 made-up subject numbers were numbers
    # the real column held, at each of two seeds. The twin's own digest
    # above did NOT move, so not one cell of the twin changed with it.
    #
    # RE-RECORDED AT THE REPAIR PASS OF 2026-09-18 (plan P4-D276, as
    # amended), read line by line against c5d09d5: FOUR LINES MOVED and
    # not one other line of the report did. All four are the same note,
    # one on each of the four columns of LABELS, and all four say what
    # `n_distinct` means on those roles -- "how many different spellings
    # this column's description speaks of" where they read "how many
    # different spellings this column holds". P4-D276 changed the count
    # itself on exactly those roles and left the sentence beside it
    # saying the old meaning, so a person reading their own report was
    # told a column of three spellings holds two. A column of NUMBERS
    # keeps the old wording, because there the count is still of raw
    # present spellings. The twin's own digest above did NOT move, so
    # not one cell of the twin changed with it.
    # RE-RECORDED FOR PLAN P4-D6.4, read as a diff against e53d5f4:
    # `reading`'s absent-cell block says the twin WRITES its thirteen
    # `-999` cells rather than leaving them empty, and marks `-999` as a
    # spelling the twin writes; the stand-in heading drops "The twin does
    # not reproduce them"; the page's carried-spellings paragraph is
    # printed, because a spelling now travels; and the spreadsheet note
    # names the thirteen cells that begin with a minus. No other line
    # moved.
    # RE-RECORDED AT THE REPAIR PASS OF P4-D6.4, read line by line
    # against c9fa026: FOURTEEN LINES MOVED, one per column and all the
    # same line, the first count of each column block. "leaves N cell(s)
    # empty" became "N cell(s) with no value", every N unchanged (0,
    # 11, 13, 160 and 240). `reading`'s said it left 13 cells empty while
    # the twin holds thirteen `-999` cells and no blank. The twin's and
    # the quality report's digests did not move. No other line moved.
    # RE-RECORDED AT THE NUMBERS PASS OF THE SECOND CODEX ROUND
    # (2026-09-19, item 1), read line by line against 05e7d89: FIVE LINES
    # ARE ADDED, all five one new deviation block on `visits`, and not
    # one other line of the report moved. They say that the column's
    # published `mode_count` of 28 is held by 27 cells of the twin. That
    # gap is not new -- `validation` has recorded it in as many words
    # since P4-D267, because `visits`'s mode is its LARGEST value and so
    # a pinned end of the ladder, which the ladder gives 27 cells -- and
    # until now the report was SILENT about it, which is exactly the
    # defect the item reproduced: the mode pass declared success
    # wherever some stratum held the mode's value, whatever its size.
    # The twin's own digest above did NOT move, so not one cell of the
    # twin changed with it.
    #
    # RE-RECORDED AT THE POOLED-SCALE LANDING (2026-09-21, plan P4-D301,
    # ledger K-2B-50), read as a line-by-line diff against the report
    # before it: EIGHT LINES WERE ADDED, two facts on each of the four
    # LABEL columns, and one count moved with them -- 116 approximated
    # facts measured became 124. Not one other line moved. Contract
    # 6.3.3 publishes the average and the spread of the numbers a
    # column's floor held back, and every label column of this
    # demonstration holds back WORDS, so all eight lines say that this
    # column publishes no such scale. The twin's own digest above did
    # NOT move, so not one cell of the twin changed with it.
    # RE-RECORDED AT THE INTEGRATION OF STAGE 3'S FIVE LANDINGS
    # (2026-09-23), and stale before it for the description golden's
    # reason. Read line by line against that tree: 258 of 863 lines
    # differ. The count of approximated facts measured rises from 122 to
    # 134 -- each numeric column's two withdrawn rungs (`p01`, `p99`)
    # leave and its four tail distances arrive -- and one APPROXIMATION
    # MISS arrives with them: `reading` holds 58 cells two figures wide
    # against a published 57. The report NAMES that miss rather than
    # losing it, which is what this digest is read for; no line the
    # report used to carry was dropped.
    # RE-RECORDED FOR THE SENTENCE THE LADDER NO LONGER SUPPORTS (the
    # review of 2026-09-23, finding 7). Read line by line against the
    # tree above: 16 lines differ and they are one paragraph. It said "the
    # nine steps between its smallest and its largest value ... Every one
    # of them was measured on this twin", where the description withholds
    # both ends and the rungs nearest them -- measured on 100 readings
    # 0.125 to 99.125, three rungs published and eight withheld. The
    # paragraph now names the rungs the description publishes and each
    # tail's distances, and says which rungs are not among them and why.
    # No other line moved: no fact left the report, no count changed, and
    # the twin's own digest above did not move.
    # AND ONE LINE MORE, the same day and the same item: the note a
    # column no reading fits carries said that describing it from the
    # part that does read "would publish an average, a smallest and a
    # largest value", and a measurement column publishes neither end.
    # One line differs, the note on the column no reading fits, and
    # nothing else -- 18 lines against the tree before both passes.
    "50c2bc2bed376932fb8377618a21d7b21ce98455cb4f6c70f4d7d295560e9221"
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
# THE CENSUS LOST TWO OBLIGATIONS HERE, DELIBERATELY (plan P4-D18,
# adversarial round 1). The `note` column published the forms `AAAAAA`
# and `AAAAAAAA`, and a form carrying only ONE kind of symbol says
# nothing `length` and the two alphabet counts do not already say: the
# six and the eight are `length`'s own, and which alphabet is
# `n_code_alphabet`'s. A form is now published only where at least two
# of the three kinds -- figure, letter, mark -- appear, so `A9999`
# stands and `AAAAAA` does not. Fewer obligations here is the point of
# that rule and not a census that quietly shrank.
#
# RE-RECORDED 2026-08-27 (review item P4-G3-R1-F5). TEN LINES moved and
# all ten are the same line: a clock column's rung and distinctness
# verdicts print where their window comes from, and both cited
# `generation-method-v1.md G12.9` -- a section that did not exist when
# the clock role landed, and that, once it was written, turned out to
# be about rank agreement between the positions of a JOINED column,
# with a window of 0.02 that means nothing for a time of day. A reader
# following either citation from this very page first found nothing and
# then found the wrong rule. G12.10 and G12.11 now state the two clock
# envelopes and the citations point at them.
#
# CHECKED rather than assumed: the page was rendered before and after
# and the two diffed. Twenty lines differ, which is the ten citations
# in their before and after form, and NOTHING ELSE -- no verdict moved,
# no obligation was gained or lost, and the census carries what it
# carried. `tests/test_method_citations_resolve.py` now refuses any
# citation that names a section the method does not define, so this
# cannot happen again silently.
# RE-RECORDED 2026-08-31 for plan amendment A-P4-47, under a counted
# difference read against the tree at the commit before this landing:
# THIRTY lines added, THREE removed, and the three removed are the same
# three restated -- 479 obligations become 488, 402 HELD become 411, and
# the sentence that adds the five numbers up. The twenty-seven that
# remain are nine new `levels.<label>.shape_form_cells` records, three
# lines each, every one HELD. NOTHING was lost and no verdict moved:
# the census carries nine obligations more than it did and not one
# fewer, which is the thing this digest exists to make somebody check.
# RE-RECORDED 2026-09-01 with the twin above. Two things moved and
# both were read: the joined column's own achieved figures, which
# follow its cells; and the census, because landing L7 gives EVERY pair
# of positions method G12.9's window where a pair between two earlier
# positions used to be checked exactly with no citation. This
# demonstration has two positions and therefore one pair, so its own
# verdicts are unchanged in kind -- no obligation left the census and
# none was lowered.
# RE-RECORDED at the integer-grid landing. The census carries the SAME
# obligations -- 416 checks wide and 407 narrow, both asserted whole
# and by digest above and neither moved -- so what changed here is
# what the checks SAY about a twin whose distinct count rose, and not
# which checks were taken. A census carrying fewer obligations would
# have turned those two counts red first.
# RE-RECORDED 2026-09-04 for plan P4-D35. The census carries ONE MORE
# obligation and none fewer: `numeric.empty_edges` is LISTED beside
# `numeric.empty_bins`, on the same one column of this demonstration
# and no other, which the two assertions above name by identity rather
# than by count. The check counts held whole -- 416 wide and 407 narrow
# by digest -- and the twin's own digest did not move, so what changed
# here is one line the report SAYS.
# RE-RECORDED AGAIN 2026-09-04 for review round 2 item 3. The census
# carries the SAME obligations -- both check counts held by digest and
# both listing sets are asserted by identity above -- and what moved is
# ONE SENTENCE: the `numeric.empty_edges` listing used to say a cell
# that could not reach an edge takes the nearest free place inside the
# stretch, which the pass no longer does. It says the cell STAYS where
# it was and the report names it, which is what the pass does.
# RE-RECORDED 2026-09-04 for review round 8 item 5. The census carries
# the SAME obligations -- both check counts held by digest and both
# listing sets are asserted by identity above -- and what moved is ONE
# SENTENCE again: the `numeric.empty_edges` listing described a walk
# that tries the nearer edge alone, and the walk tries four routes.
# RE-RECORDED 2026-09-05 for plan P4-D36, and the difference was
# COUNTED and read first. The affixed role's split put the space
# between a number and its unit inside the CORE, and the value stage
# rewrites a core as a number and has no space to write -- so every
# cell of the demonstration's `dose` column came back `165.1mg` where
# the source reads `165.1 mg`. All 240 of them move, and they move to
# what the source says. The description gains three keys on that one
# column -- the wrapper set and the two counts of different cores --
# and no count, statistic, label, role or spelling of any other column
# changes.
# RE-RECORDED 2026-09-08 for review round 1 of that same landing, item
# 2, and the census was COUNTED on both sides before this moved: 1371
# obligations, 1309 HELD, 62 WITHIN-BOUND, 0 MISSED and 145 NOT
# CHECKABLE, identical before and after. What moved is TWO LINES, both
# of them `counts.affix_variants` on a column wearing ONE wrapper. That
# check compared how MANY other wrappers the file wears, which is a
# check a file wearing the same number of DIFFERENT ones passes; it
# compares the whole set now -- each wrapper's two spellings and its
# count -- and reports the outcome alone, because a wrapper is text of
# the measured file and V5.4 keeps that back. So the line's published
# side reads `no other wrapper` where it read `0`, and its measured
# side is no longer printed.
# RE-RECORDED 2026-09-10 for landing L17b, plan amendment A-P4-58, for
# the same reason as the report above and with the same one-paragraph
# reach. The census was COUNTED on both sides: the obligations, the
# HELD, WITHIN-BOUND, MISSED and NOT CHECKABLE totals and the verdict
# are identical before and after. What moved is the handling paragraph,
# which names six files where it named five and names the questions
# file among them.
# RE-RECORDED 2026-09-14 (stage 2): part one listed `group_separator` on
# six numeric positions; part two lists `datetime_separators` and
# `all_at_midnight` on `recorded_on`, raising the not-checkable count from
# 146 to 148. No verdict and no check moved.
# RE-RECORDED AGAIN 2026-09-14 (stage 2 audit): the reason printed beside
# each `numeric.group_separator` listing now says the mark was FOUND, not
# WRITTEN; ten lines changed and nothing else.
# RE-RECORDED AGAIN when landing 2b.1 merged into that integration: diffed
# against the integrated report before the merge, only window figures moved
# (50 asked-for windows, 5 signed ones and 21 found figures), 2b.1's cause
# below, with no verdict and no count; diffed against landing 2b.1's own
# report, only 2b.2's and 2b.3's lines moved, those stated here.
# RE-RECORDED 2026-09-15 at the integration of landings 2b.1 to 2b.5, which
# carries both causes below at once. Diffed against the integrated report
# before landing 2b.2 merged, only 2b.2's lines moved: obligations 495 to
# 507, HELD 420 to 432, and NOT CHECKABLE 149 to 143 (2b.3's 149 less
# 2b.2's six). Against landing 2b.2's own report, only 2b.3's datetime
# listings moved, NOT CHECKABLE 142 to 143. No verdict moved.
# RE-RECORDED 2026-09-15 (landing 2b.3): the marks and the values at midnight are
# obligations wherever a column writes a clock, and `recorded_on` writes
# none, so its two listings now give that reason in one sentence and a
# third listing, `datetime.n_at_midnight`, joins them, raising the
# not-checkable count from 148 to 149. Read as a diff: those five lines
# and the two counts moved, and no verdict and no check moved.
# RE-RECORDED 2026-09-15 (landing 2b.2, plan P4-D41), and the census was
# COUNTED on both sides against 53bb012. The mark between thousands was a
# listing and is a check now, beside the notation of a negative and the
# count of signed decimals: twelve checks arrived on the four
# numeric-family columns and every one of them is HELD, so obligations go
# 495 to 507 and HELD 420 to 432. The six `group_separator` listings left
# -- four columns and the joined column's two positions, whose spellings
# the loader now holds to the defaults -- so NOT CHECKABLE goes 148 to
# 142. No verdict moved and nothing else in the report changed.
# RE-RECORDED at landing 2b.1 (2026-09-15): the checker reads the widest
# stratum as no less than G5.2a's cap, so the rung and moment windows of
# the withheld-mode columns widen -- to a cap of three on `amount`, whose
# 240 cells hold 238 numbers, and of six on `reading`, `dose` and both
# pressure positions -- and `amount` and `dose` report their moved
# figures. The census is unchanged: 420 held, 75 within a window, none
# missed.
# RE-RECORDED at landing 2b.1, part 2 (2026-09-15, residual R-P4-61):
# 64 lines of window ends move in their last digits. The windows are
# read at exact fractions of the ladder and computed in G12.3's one
# operation order -- the twin report's own, digit for digit -- and the
# widest stratum is read off the description alone, which on this
# demonstration is the number it was already. The census is unchanged:
# 420 held, 75 within a window, none missed.
# RE-RECORDED AGAIN 2026-09-15 (landing 2b.6). Both inputs above are
# accounted for, so what moved here is WHAT THE CHECK SAYS: the column
# of dates files one obligation MORE than it did -- `format.member`, the
# member the dates were written in, which was NOT CHECKABLE while the
# twin wrote ISO whatever the source wrote -- and four listings more,
# one per written-form census, each saying that this column's member can
# show no such convention. The census carries no fewer obligations than
# it did: one moved from the listings to the checks and four arrived as
# listings, which the frozen baselines below show arriving by name.
# RE-RECORDED at landing 2b.6 (2026-09-15). The census carries no fewer
# obligations than it did -- which is the thing this digest exists to
# catch -- and the numbers beside the date rungs moved because the twin's
# own cells moved: each of the nine interior rungs is now measured AT its
# published value rather than a day or more below it, and the window it
# is measured against is that value rather than a band around its slice.
# RE-RECORDED 2026-09-15 (landing 2b.7, plan P4-D65.1 and P4-D65.2).
# The description above moved, so this report is built from different
# bytes; what it SAYS moved too, in exactly two ways. Every numeric
# block now LISTS the two mixed-convention censuses, because no column
# of this demonstration wears two notations or two marks and a census
# naming fewer than two is listed rather than checked. And
# `spelling.decimal_plus`, whose census is now the unavailable state on
# every column that writes a cell with a point, publishes the BAR
# instead of the count: the line reads "below the floor" on both sides
# and is HELD. READ BEFORE RE-RECORDING, as the message below asks: the
# census carries no FEWER obligations than it did -- the checked count
# is unchanged at 416 and `spelling.decimal_plus` is still executable
# on all four of the columns that carried it, which the red battery of
# tests/test_p3v1f2_entry_table.py asserts independently.
# RE-RECORDED at landing 2b.13's repair pass (2026-09-16, plan P4-D91),
# and the whole of what moved is ONE SENTENCE, printed six times. The
# wide-run word is now held to the smallest group size, as its sibling
# `negative_form` is by NS1, so the listing beside `none` no longer says
# "wrote no run of figures past what a double keeps" but "wrote fewer of
# them than the smallest group size it was described at" -- which is
# what the word now means and what the file it describes now is.
#
# MEASURED RATHER THAN ASSUMED, because "only a sentence moved" is the
# claim this digest exists to stop anyone making loosely: the report was
# rendered from this same fixture on the commit before the repair and on
# the repaired tree, and the two files differ in exactly 12 lines -- the
# six listings of that sentence, each one line out and one line in. No
# verdict, no count, no obligation and no order moved, the census still
# carries the same obligations, and `GOLDEN_TWIN_SHA256` and
# `GOLDEN_DESCRIPTION_SHA256` below did not move at all.
# RE-RECORDED AT THE MERGE OF LANDINGS 2b.6 AND 2b.7 (2026-09-16), read
# as a diff of the two reports against each side. Against 2b.6's tree
# only 2b.7's lines moved: the mixed-convention and wide-run listings on
# the numeric columns (NOT CHECKABLE 146 to 164) and `decimal_plus`
# reading "fewer than 11" where it read 0. Against 2b.7's tree only
# 2b.6's lines moved: `format.member` checked (507 to 508 obligations),
# the four written-form listings, and the date rungs held at their
# published values. The census carries no fewer obligations than either
# side: 508 checked, as 2b.6 has, and every verdict otherwise unchanged.
# RE-RECORDED AT THE MERGE OF LANDING 2b.8 INTO LANDINGS 2b.6 AND 2b.7
# (2026-09-16), read as a diff against each side. Against the tree
# before the merge only landing 2b.8's check arrived:
# `forms.published.@%%%%%` HELD on `record_code`, 508 to 509 obligations.
# Against landing 2b.8's own tree only landings 2b.6's and 2b.7's lines
# moved, as recorded above. No verdict otherwise moved.
# RE-RECORDED 2026-09-15 for plan P4-D86, and the quality report says
# MORE, not less. MEASURED on this run: 28 new checks under
# `document.source.dialect`, all HELD -- thirteen on the document
# (blank lines, delimiter, records of nothing, end-of-file mark, escaping,
# header quoting, metadata rows, the space after a delimiter, preamble,
# separator line, left-out cells, trailing delimiter, header cells written
# blank or repeated), one quoting rule for each of the fourteen columns,
# and the row order on `record_code`. The encoding rule `bytes.utf8` is
# renamed `bytes.encoding` and still HELD. No check was dropped: the
# widening test above reads every frozen obligation back by identity.
# RE-RECORDED 2026-09-15 at the merge of landing 2b.9 into landings
# 2b.1-2b.5, and NO CELL CHANGED. The sorted digests above moved because
# 2b.9 changed what they are taken OVER -- the cells sorted, not the cells
# as written -- and because 2b.9 sorts the twin's rows. MEASURED rather
# than argued, column by column against a git archive of the base commit
# 367e1d7 at this seed: all thirteen columns hold an IDENTICAL multiset of
# cells, and the twin's rows agree as a multiset while differing in order,
# so whole rows moved and nothing was written differently. `unused` and
# `batch`, whose cells cannot be told apart, are unchanged even in order.
# RE-RECORDED 2026-09-15 for plan P4-D76, and ONLY WHERE CELLS STAND
# MOVED. The demonstration's `record_code` is declared with
# `--identifier`, and landing 2b.9 published a row order for it -- which
# is a fact about a declared identifier's own values and is exactly what
# P4-D76 withdraws. MEASURED rather than argued: the published written
# form differs in ONE key of its twenty-two, `row_order`, which was
# `{collation: text, column: 1, direction: ascending}` and is now null;
# every column's cells are the same MULTISET as before, the sorted
# digests above did not move, and every order digest here is once more
# the one commit 367e1d7 froze -- the twin's rows have returned to the
# arrangement they had before the identifier was sorted on.
# RE-RECORDED 2026-09-16 for plans P4-D80 and P4-D81 (review items
# CODEX-3 and CODEX-2). The twin's own digest did not move -- it is
# 494ae9dd2eef2b3a703e456a506224b1d799c447851666e03d089aef706fe84f on
# this commit and on the one before it -- so the measured file is
# untouched and what moved is what the check SAYS. READ RATHER THAN
# ASSUMED, as this file requires: the report was built on this commit
# and on the one before it and the two were compared line by line.
# They differ in exactly two places.
#
# ONE LINE IS REWORDED. The subcheck naming the lines before the table
# read "0 line(s) before the table, as published" and now reads "0
# line(s) before the table in 0 shape(s), as published", because those
# lines are published as runs of one shape (P4-D80).
#
# AND ONE OBLIGATION LEAVES THE CENSUS: 534 to 533, with HELD 459 to
# 458. This file warns that a census carrying fewer obligations than it
# did is a defect even when nothing crashed, so the one that went is
# named here. It is `bytes.header-rows`, which read "0 row(s)
# describing the columns under the names, as published". Under P4-D81
# a checked file is read under the description's OWN declaration of how
# many rows describe the columns, and this description declares none --
# so both sides of that comparison are empty whatever the file holds,
# and no edit to any file could make it fail. It reported HELD on every
# file while measuring nothing. That is the vacuity V3.4 refuses by
# name, so it is no longer filed; it is filed, and falsifiable, on a
# description that DECLARES such rows.
# RE-RECORDED AT THE MERGE OF LANDING 2b.10 INTO LANDINGS 2b.6 TO 2b.8
# (2026-09-16), read as a diff against each side. Against the tree
# before the merge only landing 2b.10's checks arrived: the written-form
# obligations `bytes.*` [document.source.dialect], one per rule and one
# quoting check per column, all HELD, 509 to 535 obligations. Against
# landing 2b.10's own tree only landings 2b.6's, 2b.7's and 2b.8's lines
# moved. No verdict otherwise moved.
# RE-RECORDED AT THE REPAIR OF THE STAGE-2b INTEGRATION (2026-09-16):
# only the values found for `dose` moved, because its cells did; every
# verdict line is as it was, and so is the count of obligations.
# RE-RECORDED AT THE REVIEW OF 158c811 (2026-09-16, plan P4-D130), read
# line by line against the report of 158c811: two lines moved, the count
# of different dates found in `recorded_on`, 171.0 to 176.0 on both
# distinctness checks, both still inside their windows. No verdict moved
# and the census carries the same obligations; the new sentence of plan
# P4-D131 for an empty census of written forms is not reached, because
# this column's member writes none of the four.
# RE-RECORDED AT THE MERGE OF carried-fix-dates (2026-09-16): against
# the integration repair only the two `recorded_on` distinctness values
# moved (171.0 to 176.0); against the date branch only `dose`'s found
# values and the integration's listing words. No verdict moved.
# RE-RECORDED 2026-09-16 (plans P4-D142 and P4-D147), read as a diff
# against 158c811. The twin's `pressure` systolic p99 is 217.61 against a
# published 218, WITHIN-BOUND where it had been HELD at 218.0 (468 held and
# 67 within a window become 467 and 68, nothing missed), and the other
# printed values of that column's positions moved with its cells. The two
# mixture censuses' listings on `visits`, `reading`, `amount` and `dose`
# name the obligation in words now and carry the sentence of a census that
# names nothing, because a census naming one convention is CHECKED since
# plan P4-D142 and the listing is left for one naming none.
# RE-RECORDED AT THE MERGE OF carried-fix-numbers (2026-09-16): against
# the numbers branch only found values of `recorded_on` and `dose`
# differ. The two mixture listings carry the numbers branch's words: the
# integration repair had given them words of its own ("where the
# description names no more than one"), which plan P4-D142 made untrue
# by checking a census that names one, so ONE set of words was kept.
# RE-RECORDED FOR THE OWNER'S RULING OF 2026-09-17 (plan P4-D201), read
# as a diff against 039df54: the four `suppressed.counts` obligations
# left with the key they checked -- on `region`, `answer`, `batch` and
# `note`, all HELD before -- so 535 obligations became 531 and 467 HELD
# became 463. No other line moved and no verdict moved.
# RE-RECORDED FOR ITEM 1 OF THE SAME RULING (plan P4-D202): one
# obligation arrived, `prefix.(column)` on `record_code`, HELD, so 531
# became 532 and 463 HELD became 464. No other line moved.
    # RE-RECORDED AT THE CLOSE OF STAGE 3'S REVIEW (2026-09-24), and TWO
    # passes moved it. READ LINE BY LINE against a git archive of the
    # tree each half was last recorded on. From the six untrue sentences
    # (27b9915): the page's account of what the validator checks said
    # "the smallest and largest exactly, the nine steps between them"
    # over a description that publishes neither end, and now says "every
    # rung the description publishes ... a rung the description withholds
    # is not checked"; and the floor paragraph gains what the floor does
    # NOT cover -- a count of CELLS BY KIND, and that the floor counts
    # ROWS and not people (plan P4-D348). Fourteen lines arrive there and
    # none leaves. Six per-column sentences about the finer rungs and two
    # about a tail's withheld keys are reworded on the same pass. From
    # the numeric robustness pass (05a2398): the achieved numbers of
    # `reading`, `amount` and `dose` move with the twin's cells. THE
    # CENSUS IS UNCHANGED: 478 obligations HELD before and after, the
    # same 2 MISSED, the same 22 named facts in the same order, and
    # nothing "outside the range" either way.
GOLDEN_QUALITY_SHA256 = (
    # RE-RECORDED FOR THE NUMERIC TAIL (stage 3, landing 3.3). Every
    # numeric block now carries `tails` and `bin_groups`; the rungs
    # whose type-7 reading would touch one of the outermost eleven
    # values are null, and the two ends with them unless a group of
    # eleven rows holds one (contract 6.7a). The pages were read before
    # this was recorded: the twin's report names the four new
    # approximated facts of every numeric column and loses no line it
    # had, and the quality report carries the same obligations plus
    # those four per column. Nothing else about any role moved.
    # RE-RECORDED AT THE MERGE OF THE TWO RULING BRANCHES INTO THIS ONE.
    # The census carries 532 obligations and 466 of them HELD: the 531 and
    # 463 of plan P4-D201, plus `prefix.(column)` on `record_code` (plan
    # P4-D202), plus `recorded_on`'s two distinct counts HELD where they
    # were WITHIN-BOUND (plan P4-D192). No obligation was lost.
    # RE-RECORDED FOR THE MODE'S OWN SENTENCE (plan P4-D267). Not one
    # verdict moved and not one obligation was gained or lost: the census
    # is the same 532 and the same 466 HELD, and what changed is the
    # sentence the two mode listings carry, which now says that the twin
    # DOES write the published number where its ladder leaves room and
    # that the report beside it says so when it does not. Read against
    # the previous report line by line, those two lines are the only ones
    # that differ.
    # RE-RECORDED FOR PLAN P4-D6.4, read as a diff against e53d5f4: one
    # obligation MOVED from the census of facts no file can evidence to
    # the checks -- `holes.by_source.-999` on `reading`, HELD at 13 -- so
    # 532 obligations became 533, 466 HELD became 467, and 164 not
    # checkable became 163. No other line moved and no verdict moved.
    # RE-RECORDED AT THE POOLED-SCALE LANDING (2026-09-21, plan P4-D301,
    # ledger K-2B-50), read as a line-by-line diff: EIGHT OBLIGATIONS
    # WERE ADDED to the census of facts no file can evidence, two on
    # each of the four LABEL columns -- the average and the spread of
    # the numbers a column's floor held back (contract 6.3.3), which
    # every label column of this demonstration publishes as the state
    # that says nothing, because all four hold back WORDS. So 163 not
    # checkable became 171. NO OBLIGATION LEFT the census and no verdict
    # moved; the description and twin digests above tell which of the
    # two inputs changed, and it is the description alone.
    # RE-RECORDED AGAIN WITHIN LANDING 3.3, read as a line-by-line diff
    # against `ce8aa7d9`: TEN LINES differ and nothing else. Each is one
    # withheld END, and what moved is the registry fact the census names
    # beside it -- `numeric.percentiles.min` and `.max` where it read
    # `numeric.percentiles`. A rung the tail rule withholds is listed
    # under the field its check bound before, so the same obligation
    # goes quiet under its own name rather than under the ladder's, and
    # no subcheck binds two facts (contract 9, entry table V3.1). No
    # obligation was gained or lost and no verdict moved.
    # ...AND RE-RECORDED AGAIN AT THE INTEGRATION OF STAGE 3'S FIVE
    # LANDINGS (2026-09-23). Read line by line against the tree before
    # it: 397 of 2,292 lines differ. The census grows from 533
    # checkable obligations to 541 -- HELD 466 to 469 and WITHIN-BOUND
    # 67 to 72 -- and the NOT-CHECKABLE count rises from 181 to 214.
    # NO OBLIGATION LEFT THE CENSUS, and the two reports were read
    # against each other obligation by obligation to say so, under the
    # renaming `_named` makes below. 30 checkable obligations ARRIVED,
    # every one a tail's: four distances on each numeric block and, on
    # the two blocks whose tail publishes its rows as a group, that
    # group's values. 22 checkable obligations MOVED to the listings,
    # every one a rung the tail rule withholds -- `ladder.p01`,
    # `ladder.p99`, `ladder.min` and `ladder.max` on each numeric
    # column, and per part of the joined column its two ends and its
    # two outer rungs -- which carries no window and can no longer be
    # evidenced. 30 - 22 = 8. The listings gained 33 and LOST NONE:
    # those 22, plus eleven shape lines beside them. `ladder.min` and
    # `ladder.max` gain "(heaped end, one-sided)" where a group of
    # eleven rows holds the end and the block still publishes it.
    # THREE VERDICTS MOVED, each WITHIN-BOUND to HELD and none the
    # other way: `number 1 ladder.p95` and `number 2 ladder.p95` on
    # `pressure` and `ladder.p25` on `reading`, where the ladder the
    # tail rule leaves puts the twin on the published rung exactly.
    # ...AND RE-RECORDED AT THE FIX PASS OF STAGE 3 (2026-09-23, plan
    # P4-D349), read line by line against the tree before it: FOUR LINES
    # of 2,292 differ and they are one sentence printed four times --
    # the not-checkable reason a withheld tail key carries, which used to
    # say "a distance is published only where the tail has a row to
    # measure" and now says that the two distances are published only
    # where they would not give the tail's own cells back. The census is
    # the same on both trees to the number: 473 HELD, 68 WITHIN-BOUND, 0
    # WITHHELD, 0 MISSED and 214 not checkable. NO OBLIGATION ARRIVED,
    # LEFT OR MOVED, and no verdict moved; the description and twin
    # digests above hold, so neither input changed either. What moved is
    # only what the page SAYS, which is what this pass changed it to say.
    "3d2ab44006cde7c1d45e471c55ae1bc6124a3157cec09e24f130a6557f8dc33c"
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
