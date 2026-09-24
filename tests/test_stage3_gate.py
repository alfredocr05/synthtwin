"""THE STAGE-3 GATE, asked of a whole description in the gate's own words.

**No published number is held by fewer than the floor, and a one-row
table is refused.** That is stage 3's gate as the plan of record states
it, and until this file nothing asked it. Pieces of it are held
elsewhere -- the tail rule's own guard
(`tests/test_stage3_tail_rule.py`), the sentence-argument guard
(`tests/test_p4d334_sentence_arguments.py`), the population floor's
tests (`tests/test_p4d341_population_floor.py`) -- and a landing that
publishes something NEW lands outside all three. This file walks every
published number of a finished description, puts each into exactly one
class, and asks that class's own question of it. **A path with no class
fails**, which is what makes the gate survive a landing nobody here
foresaw.

THE CLASSES, AND WHAT EACH IS ASKED (design section 2, read off
`profile.PUBLICATION_RULES`):

* **GROUP** -- a count of rows meeting a predicate. Nought, or at the
  line; and so is every complement a reader can take against a
  population the same block publishes (`GATE_POPULATIONS`). A census is
  asked WHOLE, through `parsing.census_nameable`, because what a reader
  subtracts is the sum of its named counts.
* **POOLED** -- a pool of what the floor held back. Exempt under the
  owner's ruling 2 of 2026-09-17: the pool exists to say nothing about
  its members.
* **SETTLED** -- the counts the owner has accepted. Exempt BY NAME,
  each with the entry that settled it in `GATE_SETTLED_BY`, and never
  by a rule that could quietly widen.
* **DISTINCT** -- a count of different VALUES, not of rows. Each value
  stands on at least one row and the count says which nothing.
* **WRITTEN_FORM** -- the lengths and widths the owner kept (decision 2
  of 2026-09-15). Exempt by name in `GATE_SETTLED_BY` too.
* **VALUE** -- a cell's own value, or a statistic read off the cells.
  Governed by the stage-3 TAIL RULE and by nothing else: asked in
  `test_no_published_value_of_the_battery_names_a_lone_outer_cell`.
* **STRUCTURAL** -- held by nobody: a version, a column's place, a
  setting, the file's own form.
* **WORD_BY_COUNT** -- a word a count moves. A non-default word implies
  that at least the census line of the COLUMN'S OWN CELLS wear the
  convention it names (rule W, plan P4-D335), read with the producer's
  own readers and not off a census, which can be withheld while the
  word legitimately stands.
* **SENTENCE** -- a whole-number argument of a published sentence, held
  to `taxonomy.ARGUMENT_BINDINGS`.
* **INDEX** -- a place rather than a count: a bin's number, a tail's
  boundary percent, a width standing as a census key.

WHAT THE GATE IS NOT. It is not a second copy of the rules it checks:
where a rule is already written once -- `parsing.census_nameable`,
`parsing.tail_may_list`, `taxonomy.ARGUMENT_BINDINGS`, the tail-leak
driver's back-solve -- the gate ASKS it rather than restating it, so a
rule that drifts drifts in one place and this file sees it.

AND THE LINE IS THE LINE THE PATH'S OWN RULE NAMES. At a settings floor
of one the census line is two, and the description still names every
level of one row: that is contract invariant C5-S13 and the owner's own
reading of it, quoted at `parsing.tail_may_list` -- "a floor lowered to
one still names what it always named, which is what lowering it asks
for". So the GROUP line is `parsing.census_floor(floor)` above one and
the settings floor at one, where the class is vacuous by the owner's
decision rather than by an oversight. The VALUE, SENTENCE and refusal
halves bite at every floor.

THE LIMIT THE OWNER ACCEPTED ON 2026-09-23 (plan P4-D348). The
disclosure floor counts ROWS, not people. On a repeated-measures table
a value held by twelve visits of ONE patient is published with its
count, and this gate does not fail on it. It is measured instead, and
held at a ceiling: ledger `K-S3-14`.

THE MUTATIONS ARE AT THE FOOT OF THIS FILE. A guard that passes is not
a guard: each of the five withdraws one rule and the gate must turn
red.

WHAT THIS GATE DOES NOT YET SEE, written here because a gate whose
edges nobody states reads as a gate with none:

* **"names nothing", measured.** Section 8.8 of the count design asks
  a second question of the same battery: the table with the odd cells a
  shape writes in BLANKED gives a byte-identical description apart from
  `rare_kinds`. That is the method of
  `tests/test_older_censuses_name_no_row.py` and
  `tests/test_number_censuses_name_no_row.py`, and it is held there for
  the shapes those files carry and nowhere else. This gate asks what a
  description SAYS, not what two descriptions differ by.
* **A value held by too few rows INSIDE the band.** The VALUE clause
  asks the outermost `max(floor, 3)` order statistics on each side,
  which is the band the tail rule withholds. A published rung further in
  names a value a handful of rows hold, and the owner kept the ladder
  (decision 3 of 2026-09-15), so the gate does not ask about it.
* **`wide_runs`.** Its count -- how many wide runs are not the text
  their own values write -- is published by no key, so the gate names
  it in `WORD_NOT_ASKED` instead of asking it.
* **A joined column's halves and a date column's own values.** The
  VALUE clause reads a column's cells with `parsing.parse_number`, so a
  cell of two numbers and a cell holding a date give it nothing. The
  date and clock side is asked by the back-solve and by
  `tests/test_stage3_tail_rule.py`; a `parts[]` half is asked by
  neither.
* **The census populations the battery never reaches.**
  `pad_widths`, `decimal_plus`, `number_spellings`,
  `quarter_marker_case` and `value_histogram` carry a population in
  `GATE_POPULATIONS` that no shape of this battery exercises, so those
  five lines are closure and not measurement.
"""

from __future__ import annotations

import collections
import copy
import datetime
import importlib.util
import math
import json
import pathlib
import random
import re

import pytest

import fixtures
import kpi_rules
import kpi_shapes
import stage3_battery
import test_p4d334_sentence_arguments as bound
from synthtwin import (
    cli,
    parsing,
    profile,
    reading,
    taxonomy,
)

FLOORS = (1, 5, 11)


# -- the classes -------------------------------------------------------


GROUP = "GROUP"
POOLED = "POOLED"
SETTLED = "SETTLED"
DISTINCT = "DISTINCT"
WRITTEN_FORM = "WRITTEN_FORM"
VALUE = "VALUE"
STRUCTURAL = "STRUCTURAL"
WORD_BY_COUNT = "WORD_BY_COUNT"
SENTENCE = "SENTENCE"
INDEX = "INDEX"

GATE_CLASSES = (
    GROUP,
    POOLED,
    SETTLED,
    DISTINCT,
    WRITTEN_FORM,
    VALUE,
    STRUCTURAL,
    WORD_BY_COUNT,
    SENTENCE,
    INDEX,
)

# THE KINDS OF `profile.PUBLICATION_RULES` THAT CAN CARRY A NUMBER.
# Written out rather than gathered, for the reason `_STATED_WORDS` is:
# a set read off the rules themselves would take in whatever kind a
# later landing added, and the closure check below would then pass over
# it in silence.
NUMERIC_KINDS = (
    "count",
    "count-at-the-floor",
    "count-at-the-floor-or-withheld",
    "count-at-the-census-floor-or-unavailable",
    "count-at-the-disclosure-line",
    "count-at-the-disclosure-line-or-withheld",
    "count-of-what-the-floor-held-back",
    "count-of-a-pooled-aggregate-or-nought",
    "count-on-both-sides-or-unavailable",
    "count-of-the-files-lines-zero-or-at-the-census-line",
    "count-zero-or-at-the-floor",
    "one-group-size-below-the-floor",
    "numeric-sentinel-number",
    "number",
    "number-or-nothing",
    "tail-boundary-percent",
    "histogram-bin-number",
    "histogram-bin-number-holding-nothing",
    "histogram-bin-number-of-a-group",
    "blank-places-at-the-census-line",
    "fraction-width-as-figures",
    "whole-number-as-text",
)

# The kinds whose OWN NAME says the settings floor rather than the
# census line, so the gate asks them at the settings floor: a level of
# one row at a floor of one is published on purpose (C5-S13).
SETTINGS_FLOOR_KINDS = (
    "count-at-the-floor",
    "count-at-the-floor-or-withheld",
    "count-zero-or-at-the-floor",
)

# THE WRAPPERS `profile` BUILDS THE RULES TABLE THROUGH. `_compound_rules`
# mirrors every `columns[]` rule under `numbers` and every label rule
# under `labels`, and `_wrapper_rules` mirrors every `parts[]` rule under
# `affix_variants[].numbers`. A class table written per mirror would be
# four copies of one decision, so the table below is written once over
# the shape those mirrors are made from, and `gate_class` undoes them.
_WRAPPERS = (("numbers",), ("labels",), ("parts", "[]"), ("affix_variants", "[]"))

_EACH = profile._EACH
_ANY = profile._ANY_KEY
_KEY = profile._KEY_OF
_C = ("columns", _EACH)


def _path(dotted: str) -> "tuple[str, ...]":
    """A dotted path as the tuple `profile.PUBLICATION_RULES` keys it by."""
    return tuple(dotted.split("."))


def _paths(*dotted: str) -> "tuple[tuple[str, ...], ...]":
    return tuple(_path(one) for one in dotted)


# EVERY PUBLISHED NUMBER, IN EXACTLY ONE CLASS. A path missing from this
# table fails `test_every_published_number_of_the_document_has_one_class`,
# which is the whole point of writing it out: a landing that publishes
# something new has to say what class of number it is before the suite
# is green again.
GATE_CLASS: "dict[tuple[str, ...], str]" = {}


def _place(names: "tuple[tuple[str, ...], ...]", gate_class: str) -> None:
    for one in names:
        assert one not in GATE_CLASS, one
        GATE_CLASS[one] = gate_class


# -- STRUCTURAL: held by nobody ----------------------------------------
#
# A version, the number of columns, a column's place in the table, how
# many numbers one cell holds, the ceiling on how many levels may be
# named, every setting the person chose -- and the FILE's own form. A
# blank line, an empty row, a line ending and a sheet's extent are facts
# about whoever wrote the file: no row of the table stands behind them,
# and the form has a disclosure rule of its own
# (`dialect.blank_places_broken`, plan P4-D317) that the loader asks.
_place(
    _paths(
        "profile_version",
        "n_columns",
        "settings.small_cell_floor",
        "settings.identifier_uniqueness",
        "settings.identifier_minimum_rows",
        "settings.minimum_parse_rate",
        "settings.categorical_share",
        "settings.categorical_ceiling",
        "settings.categorical_floor",
        "settings.sentinel_outlier_iqr_multiple",
        "settings.sentinel_minimum_share",
        "settings.near_threshold_slack",
        "settings.long_tail_minimum_level",
        "settings.forced_metadata_rows",
        "settings.kept_values.n_declared",
        "settings.kept_values.built_in_numbers.[]",
        "settings.declared_missing_values.n_declared",
        "settings.declared_missing_values.built_in_numbers.[]",
        "columns.[].position",
        "columns.[].n_parts",
        "columns.[].level_ceiling",
        "source.dialect.blank_lines",
        "source.dialect.blank_lines.[].after",
        "source.dialect.blank_lines.[].lines",
        "source.dialect.blank_lines_spread.first",
        "source.dialect.blank_lines_spread.last",
        "source.dialect.blank_lines_spread.lines",
        "source.dialect.empty_rows.leading",
        "source.dialect.empty_rows.interior",
        "source.dialect.empty_rows.trailing",
        "source.dialect.line_endings.[].lines",
        "source.dialect.line_endings_spread.[].lines",
        "source.dialect.preamble.[].lines",
        "source.dialect.row_order.column",
        "source.dialect.written_names.[].position",
        "source.dialect.columns.[].sequence_start",
        "source.workbook.defined_names",
        "source.workbook.empty_rows_inside",
        "source.workbook.frozen_rows",
        "source.workbook.rows_above_header",
        "source.workbook.sheet_count",
        "source.workbook.sheet_position",
        "source.workbook.sheet_extents.[].rows",
        "source.workbook.sheet_extents.[].columns",
        "source.workbook.trailing_blank_rows",
        "source.workbook.trailing_blank_columns",
    ),
    STRUCTURAL,
)

# -- INDEX: a place, not a count ---------------------------------------
#
# A bin's number, a tail's boundary percent and a width standing as a
# census KEY. A gate that floored these would read "bin 3" as a group
# of three, which is exactly why `profile` gives them kinds of their own
# (`_BIN`, `_BIN_INDEX`, `_TAIL_PERCENT`, plan P4-D344).
_place(
    _paths(
        "columns.[].bin_groups.[].first",
        "columns.[].bin_groups.[].last",
        "columns.[].empty_bins.[]",
        "columns.[].value_histogram.<key>",
        "columns.[].tails.low.percent",
        "columns.[].tails.high.percent",
        "columns.[].n_distinct_by_occurrences.<key>",
    ),
    INDEX,
)

# -- WRITTEN_FORM: the lengths and widths the owner kept ---------------
#
# Owner decision 2 of 2026-09-15: the twin writes every column as the
# source wrote it, so the widths and lengths that say HOW a cell was
# spelled are published. They are one cell's spelling and not its value,
# and the owner accepted them by name.
_place(
    _paths(
        "columns.[].min_length",
        "columns.[].max_length",
        "columns.[].length.{}",
        "columns.[].words.{}",
        "columns.[].part_min_widths.[]",
        "columns.[].subsecond_digits",
        "columns.[].field_widths.<key>",
        "columns.[].fraction_widths.<key>",
        "columns.[].pad_widths.<key>",
        "columns.[].number_spellings.<key>",
        "source.dialect.columns.[].pad.width",
    ),
    WRITTEN_FORM,
)

# -- DISTINCT: how many different values, not how many rows ------------
#
# Each different value stands on at least one row, so a distinct count
# names no group: it is the size of the column's vocabulary. The repeats
# it implies against `n_present` belong to the multiplicity designer
# (design section 2).
_place(
    _paths(
        "columns.[].n_distinct",
        "columns.[].n_distinct_folded",
        "columns.[].n_distinct_values",
        "columns.[].n_core_distinct",
        "columns.[].n_core_distinct_folded",
        "columns.[].n_numeric_distinct",
        "columns.[].n_numeric_distinct_folded",
        "columns.[].n_distinct_by_occurrences.{}",
    ),
    DISTINCT,
)

# -- VALUE: a cell's own value, or a statistic read off the cells ------
#
# Outside the count rules by owner decision 3 and governed by the
# stage-3 TAIL RULE instead (contract 6.7a). The sweep that holds them
# is `test_no_published_value_of_the_battery_names_a_lone_outer_cell`.
_place(
    _paths(
        "columns.[].mean",
        "columns.[].std",
        "columns.[].skew",
        "columns.[].kurtosis",
        "columns.[].mode",
        "columns.[].percentiles.{}",
        "columns.[].percentiles_between.{}",
        "columns.[].empty_edges.[].[]",
        "columns.[].tails.low.values.[]",
        "columns.[].tails.high.values.[]",
        "columns.[].tails.low.mean_distance",
        "columns.[].tails.low.rms_distance",
        "columns.[].tails.high.mean_distance",
        "columns.[].tails.high.rms_distance",
        "columns.[].low_tail.mean_distance",
        "columns.[].low_tail.rms_distance",
        "columns.[].high_tail.mean_distance",
        "columns.[].high_tail.rms_distance",
        "columns.[].suppressed_numbers.mean",
        "columns.[].part_agreements.[]",
    ),
    VALUE,
)

# -- POOLED: what the floor held back ----------------------------------
#
# Ruling 2 of 2026-09-17: held-back rare labels publish a pooled total
# only. A pool exists to say nothing about its members, so its own size
# is not a group anybody is in.
_place(
    _paths(
        "columns.[].suppressed_levels",
        "columns.[].suppressed_rows",
        "columns.[].n_missing_withheld",
        "columns.[].n_sentinel_candidates_unpublished",
        "columns.[].suppressed_numbers.n_cells",
        "columns.[].levels.[].variants_withheld.{}",
        "columns.[].levels.[].variants_withheld.<key>",
    ),
    POOLED,
)

# -- SETTLED: exempt BY NAME, each with the entry that settled it ------
#
# Not a rule -- a list. Every one of these counts CAN stand below the
# line, every one of them was put to the owner or ruled on by the
# orchestrator, and the entry that settled it is named beside it. A
# count that wants this exemption has to be added here, which is a line
# somebody reads.
GATE_SETTLED_BY: "dict[tuple[str, ...], str]" = {
    _path("columns.[].n_present"): "P4-D271 (the four missing-value counts)",
    _path("columns.[].n_missing"): "P4-D271",
    _path("columns.[].n_missing_blank"): "P4-D271, contract C5-N4",
    _path("columns.[].missing_by_class.{}"): "P4-D271",
    _path("columns.[].n_numeric"): "K-2B-28 (free text's one number), P4-D332",
    _path("columns.[].n_not_numeric"): "P4-D332, ceiling K-S3-12",
    _path("columns.[].n_out_of_range"): "P4-D332, ceiling K-S3-12",
    _path("columns.[].n_contradictory"): "P4-D332, ceiling K-S3-12",
    _path("columns.[].n_negative_unrepresentable"): "P4-D332, ceiling K-S3-12",
    _path("columns.[].n_core_numeric"): "P4-D332, ceiling K-S3-12",
    _path("columns.[].n_core_not_numeric"): "P4-D332, ceiling K-S3-12",
    _path("columns.[].n_core_out_of_range"): "P4-D332, ceiling K-S3-12",
    _path("columns.[].n_core_contradictory"): "P4-D332, ceiling K-S3-12",
    _path("columns.[].n_numeric_out_of_range"): "P4-D332, ceiling K-S3-12",
    _path("columns.[].n_numeric_contradictory"): "P4-D332, ceiling K-S3-12",
    _path("columns.[].n_unparsed"): "K-2B-48 (the date role), P4-D332",
    _path("columns.[].n_zero"): "P4-D332 (a sign count), ceiling K-S3-12",
    _path("columns.[].n_negative"): "P4-D332 (a sign count), ceiling K-S3-12",
    _path("columns.[].n_positive"): "P4-D332 (a sign count), ceiling K-S3-12",
    _path("columns.[].n_sign_unknown"): "P4-D332 (a sign count), ceiling K-S3-12",
    _path("columns.[].n_whole"): "P4-D332, ceiling K-S3-12",
    _path("columns.[].n_whole_unknown"): "P4-D332, ceiling K-S3-12",
    _path("columns.[].n_fraction"): "P4-D332, ceiling K-S3-12",
    _path("columns.[].part_above.[]"): "P4-D332 (a pair count), ceiling K-S3-12",
    _path("columns.[].n_used_in_statistics"): "derived from the counts above, design row 4",
    _path("columns.[].n_left_out_of_statistics"): "derived from the counts above, design row 4",
    _path("columns.[].n_affixed"): "P4-D332 (the affixed complement), ceiling K-S3-12",
    _path("columns.[].n_joined"): "P4-D332, ceiling K-S3-12",
    _path("columns.[].n_numeric_cells"): "P4-D332 (the compound partition), ceiling K-S3-12",
    _path("columns.[].n_label_cells"): "P4-D332 (the compound partition), ceiling K-S3-12",
    _path("columns.[].n_all_digits"): "P4-D277 (the identifier partition is absorbed)",
    _path("columns.[].n_code_alphabet"): "P4-D277",
    _path("columns.[].n_rows"): "the rows of one half of a block; its complement is published beside it",
    _path("columns.[].resolution_mix.{}"): "design row 22: settled, complement = n_unparsed",
    _path("columns.[].n_at_midnight"): "design row 23, invariant D15 (both sides at the line)",
    _path("columns.[].numeric_share"): "Q9: the ratio of two counts the block publishes",
    _path("columns.[].levels.[].shape_form_cells"): (
        "P4-D160: a cell with no form is counted nowhere, so no population is published"
    ),
}
_place(tuple(GATE_SETTLED_BY), SETTLED)

# ...and the WRITTEN_FORM paths are exempt by name too, under the one
# decision that covers all of them.
for _written in tuple(GATE_CLASS):
    if GATE_CLASS[_written] == WRITTEN_FORM:
        GATE_SETTLED_BY[_written] = (
            "owner decision 2 of 2026-09-15: the twin writes each column as "
            "the source wrote it"
        )

# -- WORD_BY_COUNT: a word a count moves -------------------------------
#
# The word itself is not a number, and it is in this table because the
# COUNT behind it is: a non-default word says that enough cells wore
# that convention, and at a floor of one that count was one until rule W
# (plan P4-D335) made every one of them read `parsing.census_floor`.
_place(
    _paths(
        "columns.[].negative_form",
        "columns.[].group_separator",
        "columns.[].wide_runs",
        "columns.[].all_at_midnight",
    ),
    WORD_BY_COUNT,
)

# HOW MANY CELLS WEAR THE CONVENTION ONE WORD NAMES, read from the
# COLUMN and not from a key beside it. The census is the wrong place to
# ask: measured on `numeric_all_but_one_grouped_comma`, 1,199 grouped
# prices beside one bare cell publish `group_separator ","` while the
# `thousands_marks` census is withheld WHOLE, because its own complement
# clause refuses it -- so a gate reading the census would have called a
# word rule W holds at 1,199 cells a breach. The two readers below are
# the producer's own (`taxonomy._negative_form` and the mark rule beside
# it both ask exactly these functions of exactly these cells).
#
# `wide_runs` IS THE ONE THE GATE CANNOT ASK. Its count is how many wide
# runs are not the text their own values write, and no key of the block
# publishes it; `taxonomy._wide_runs` holds it at `parsing.census_floor`
# itself, beside invariants NS1 and WR1. It is named here rather than
# passed over. `all_at_midnight` is the other: invariant D15 holds both
# of its sides at the line where the pair is published at all.
WORD_READERS: "dict[tuple[str, ...], object]" = {
    _path("columns.[].negative_form"): parsing.negative_notation,
    _path("columns.[].group_separator"): parsing.thousands_mark,
}
WORD_NOT_ASKED: "dict[tuple[str, ...], str]" = {
    _path("columns.[].wide_runs"): (
        "no key publishes the respelled runs behind it; taxonomy._wide_runs "
        "holds it at parsing.census_floor, and invariants NS1 and WR1 beside it"
    ),
    _path("columns.[].all_at_midnight"): (
        "invariant D15: the pair is published only where both sides reach the "
        "floor, and is absent for both states otherwise"
    ),
}
WORD_DEFAULTS: "dict[tuple[str, ...], object]" = {
    _path("columns.[].negative_form"): parsing.NEGATIVE_MINUS,
    _path("columns.[].group_separator"): "",
    _path("columns.[].wide_runs"): "none",
    _path("columns.[].all_at_midnight"): False,
}

# -- GROUP: a count of rows meeting a predicate ------------------------
#
# What is left. Each is nought or at the line, and each names the
# populations a reader can subtract it from.
#
# A POPULATION IS A KEY OF THE SAME BLOCK, or `()` -- and `()` is a
# decision with a reason, never a blank. The three reasons that appear:
# the remainder is itself a published key of the block, so nothing is
# subtracted out (that class is P4-D332's, held at a ceiling by
# K-S3-12); the census's own population is NOT published, so there is
# nothing for a reader to take it off; or the number is the population
# itself, which has no smaller group behind it (the reasoning of
# `taxonomy.BIND_POPULATION`).
#
# `PARSED` and `LEVEL_ROOM` are the two populations a block states in
# two keys rather than one, spelled out in `_population`.
GATE_POPULATIONS: "dict[tuple[str, ...], tuple[str, ...]]" = {
    _path("n_rows"): (),
    _path("columns.[].count"): (),
    _path("columns.[].mode_count"): ("n_used_in_statistics",),
    _path("columns.[].sentinel_verdicts.[].n_occurrences"): (),
    _path("columns.[].levels.[].count"): ("LEVEL_ROOM",),
    _path("columns.[].levels.[].variants.{}"): ("VARIANT_ROOM",),
    _path("columns.[].missing_by_source.{}"): ("n_missing",),
    _path("columns.[].numeric_styles.{}"): ("n_used_in_statistics",),
    _path("columns.[].field_widths.{}"): ("n_used_in_statistics",),
    _path("columns.[].fraction_widths.{}"): ("n_used_in_statistics",),
    _path("columns.[].pad_widths.{}"): ("n_used_in_statistics",),
    _path("columns.[].negative_notations.{}"): ("n_negative",),
    _path("columns.[].thousands_marks.{}"): ("n_used_in_statistics",),
    _path("columns.[].decimal_plus.{}"): ("n_used_in_statistics",),
    _path("columns.[].number_spellings.{}"): ("n_used_in_statistics",),
    _path("columns.[].datetime_separators.{}"): ("PARSED",),
    _path("columns.[].utc_offsets.{}"): ("PARSED",),
    _path("columns.[].date_field_widths.{}"): ("PARSED",),
    _path("columns.[].month_name_styles.{}"): ("PARSED",),
    _path("columns.[].quarter_marker_case.{}"): ("PARSED",),
    _path("columns.[].zulu_case.{}"): ("PARSED",),
    _path("columns.[].layout_forms.{}"): ("n_present",),
    _path("columns.[].shape_forms.{}"): (),
    _path("columns.[].value_histogram.{}"): ("n_used_in_statistics",),
    _path("columns.[].bin_groups.[].count"): (),
    _path("columns.[].tails.low.rows"): (),
    _path("columns.[].tails.high.rows"): (),
    _path("columns.[].low_tail.rows"): (),
    _path("columns.[].high_tail.rows"): (),
    _path("source.workbook.columns.[].cell_classes.{}"): (),
    _path("source.workbook.columns.[].format_kinds.{}"): (),
    _path("source.workbook.columns.[].formulas"): (),
}
_place(tuple(GATE_POPULATIONS), GROUP)

# ...AND THE REASON FOR EVERY EMPTY ONE, so that "a decision with a
# reason, never a blank" is a thing this file can be held to rather
# than a thing it says about itself.
GATE_NO_POPULATION: "dict[tuple[str, ...], str]" = {
    _path("n_rows"): (
        "the number IS the population: the floor protects groups inside one, "
        "and there is no smaller group behind it (taxonomy.BIND_POPULATION, "
        "contract NF59). What governs it is the POPULATION floor, asked in "
        "the refusal half"
    ),
    _path("columns.[].count"): (
        "an affix wrapper's cells; what is left of the column's n_affixed is "
        "the MAIN wrapper, which the evidence sentence publishes through "
        "taxonomy.BIND_MAIN_WRAPPER and the sentence half asks there"
    ),
    _path("columns.[].sentinel_verdicts.[].n_occurrences"): (
        "a judged stand-in's occurrences; the cells that are not it are the "
        "column's own numbers, which n_used_in_statistics publishes beside it"
    ),
    _path("columns.[].shape_forms.{}"): (
        "P4-D160: a cell with NO form is counted nowhere and is not pooled "
        "either, so the census's own population -- the cells that have a "
        "form -- is not published and there is nothing to subtract from"
    ),
    _path("columns.[].bin_groups.[].count"): (
        "a group of histogram bins; the rest of the rows are in the other "
        "groups of the same list, each published at the floor beside it"
    ),
    _path("columns.[].tails.low.rows"): (
        "the boundary percent publishes it: `parsing.tail_rows` is a fixed "
        "function of the count and the percent, both published, so the rows "
        "are not a count a reader takes off anything"
    ),
    _path("columns.[].tails.high.rows"): "as tails.low.rows",
    _path("columns.[].low_tail.rows"): "as tails.low.rows",
    _path("columns.[].high_tail.rows"): "as tails.low.rows",
    _path("source.workbook.columns.[].cell_classes.{}"): (
        "a census of the SHEET's cells; what a reader would subtract it from "
        "is the sheet's own extent, and `workbook.floored` with contract WB3 "
        "is where that rule is written"
    ),
    _path("source.workbook.columns.[].format_kinds.{}"): "as cell_classes",
    _path("source.workbook.columns.[].formulas"): (
        "the column's formula cells; the cells that are not formulas are the "
        "value cells the class census beside it counts"
    ),
}

# The census paths, which are asked WHOLE: a reader subtracts the sum of
# the named counts, not one of them.
GATE_CENSUSES = frozenset(
    one
    for one in GATE_POPULATIONS
    if one and one[len(one) - 1] in (_ANY,)
) | {_path("columns.[].levels.[].count")}

# The two keys a census map may carry that name no group: the pool, and
# the state a census speaks where it may not speak at all.
POOL_KEYS = (taxonomy.SUPPRESSED_LABEL, taxonomy.UNAVAILABLE_LABEL)


def gate_class(path: "tuple[str, ...]") -> "str | None":
    """The class of one path, the rules table's own mirrors undone."""
    for shape in _shapes_of(path):
        if shape in GATE_CLASS:
            return GATE_CLASS[shape]
    return None


def gate_shape(path: "tuple[str, ...]") -> "tuple[str, ...]":
    """The shape of the class table this path is classified by."""
    for shape in _shapes_of(path):
        if shape in GATE_CLASS:
            return shape
    return path


def _shapes_of(path: "tuple[str, ...]"):
    """`path`, then the same path with each wrapper step taken off."""
    yield path
    if path[:2] != _C:
        return
    rest = path[2:]
    while True:
        cut = 0
        for wrapper in _WRAPPERS:
            if rest[: len(wrapper)] == wrapper:
                cut = len(wrapper)
                break
        if not cut:
            return
        rest = rest[cut:]
        yield _C + rest


# -- the battery -------------------------------------------------------


def _blank_line_heavy(rows: int = 400) -> str:
    """A delimited file whose writer left a blank line every seventh record."""
    draw = random.Random(5)
    lines = ["value,site"]
    for place in range(rows):
        lines += [f"{draw.randint(1, 900)},{fixtures.REGIONS[place % 4]}"]
        if place % 7 == 0:
            lines += [""]
    return "\n".join(lines) + "\n"


def _sparse_block(rows: int = 400) -> str:
    """A date column fifteen rows hold and the rest leave empty."""
    draw = random.Random(6)
    present = set(draw.sample(range(rows), 15))
    lines = ["died,site"]
    for place in range(rows):
        day = (
            datetime.date(2021, 1, 1) + datetime.timedelta(days=draw.randrange(700))
        ).isoformat()
        lines += [f"{day if place in present else ''},{fixtures.REGIONS[place % 4]}"]
    return "\n".join(lines) + "\n"


def _sized(rows: int) -> str:
    """A table of exactly `rows` records, for the two band edges either side."""
    draw = random.Random(rows)
    lines = ["value,site"]
    for place in range(rows):
        lines += [f"{draw.gauss(50, 12):.1f},{fixtures.REGIONS[place % 4]}"]
    return "\n".join(lines) + "\n"


def _bounded_scales(rows: int = 1800) -> "list[tuple[str, list[str]]]":
    """Three bounded clinical scales: the shape a listed tail is for."""
    built: "list[tuple[str, list[str]]]" = []
    draw = random.Random(1)
    built += [(
        "pain",
        [
            str(draw.choices(range(11), weights=[30, 10, 12, 14, 12, 10, 8, 6, 4, 2, 0.4])[0])
            for _row in range(rows)
        ],
    )]
    draw = random.Random(101)
    built += [(
        "gcs",
        [
            str(
                draw.choices(
                    range(3, 16),
                    weights=[0.4, 0.3, 0.4, 0.5, 0.6, 0.8, 1, 1.5, 2, 3, 6, 12, 70],
                )[0]
            )
            for _row in range(rows)
        ],
    )]
    draw = random.Random(401)
    built += [(
        "children",
        [str(min(12, int(draw.gammavariate(1.6, 1.1)))) for _row in range(rows)],
    )]
    return built


def _heavy_tails(rows: int = 600) -> "list[tuple[str, list[str]]]":
    """Two columns whose tail reaches far past the body of the column."""
    built: "list[tuple[str, list[str]]]" = []
    draw = random.Random(27)
    built += [("charges", [f"{1000 * draw.paretovariate(1.5):.2f}" for _row in range(rows)])]
    draw = random.Random(17)
    built += [("lognormal", [f"{draw.lognormvariate(3, 0.5):.2f}" for _row in range(rows)])]
    return built


def _one_column(name: str, cells: "list[str]") -> str:
    return f"{name}\n" + "\n".join(cells) + "\n"


class Case:
    """One table of the battery, written to disk and described."""

    def __init__(
        self,
        name: str,
        folder: pathlib.Path,
        table: pathlib.Path,
        document: "dict",
        floor: int,
    ) -> None:
        self.name = name
        self.folder = folder
        self.table = table
        self.document = document
        self.floor = floor
        self.cells: "dict[str, list[str]]" = {}


def _tables() -> "list[tuple[str, str, str, list[str], list[str]]]":
    """(name, suffix, text, declared identifiers, declared measurements).

    THE BATTERY'S DELIMITED HALF. Every role with its joined column, the
    four realistic families, bounded scales, heavy tails, a sparse
    block, a repeated-measures table with a declared identifier, a
    blank-line-heavy file, and tables at 99, 100, 999 and 1,000 rows --
    beside the forty-six seeded shapes of `tests/stage3_battery.py`, one
    per count that can sit below the floor. `_workbook_cases` writes the
    four families again as WORKBOOKS, which makes the realistic shapes
    eight. All of it is built at runtime from fixed seeds and nothing is
    read from any real data (plan D13).
    """
    built: "list[tuple[str, str, str, list[str], list[str]]]" = []
    for name in sorted(stage3_battery.SHAPES):
        cells, flags = stage3_battery.SHAPES[name](
            random.Random(stage3_battery.BATTERY_SEED)
        )
        built += [(
            f"battery-{name}",
            ".csv",
            stage3_battery.rows_text(["value"], [[cell] for cell in cells]),
            list(flags["identifiers"] if "identifiers" in flags else ()),
            [],
        )]
    for name, cells in _bounded_scales() + _heavy_tails():
        built += [(f"scale-{name}", ".csv", _one_column(name, cells), [], [])]
    built += [(
        "every-role",
        ".csv",
        fixtures.every_role_and_joined_table(),
        ["record_code"],
        [fixtures.JOINED_COLUMN],
    )]
    built += [(
        "repeated-measures",
        ".csv",
        kpi_shapes.visits_table(1200, 300),
        ["subject_id"],
        [],
    )]
    built += [("blank-lines", ".csv", _blank_line_heavy(), [], [])]
    built += [("sparse", ".csv", _sparse_block(), [], [])]
    for rows in (99, 100, 999, 1000):
        built += [(f"rows-{rows}", ".csv", _sized(rows), [], [])]
    for family in kpi_shapes.eight_shape_tables():
        declared = [family["identifier"]] if family["identifier"] else []
        built += [(
            f"family-{family['family']}",
            ".csv",
            kpi_shapes.delimited_text(family["names"], family["rows"]),
            declared,
            [],
        )]
    return built


def _workbook_cases(home: pathlib.Path, floor: int) -> "list[Case]":
    """The four realistic families again, as WORKBOOKS."""
    built: "list[Case]" = []
    for family in kpi_shapes.eight_shape_tables():
        folder = home / f"book-{family['family']}"
        folder.mkdir(parents=True, exist_ok=True)
        table = folder / "real.xlsx"
        kpi_shapes._workbook(table, family["names"], family["rows"])
        declared = [family["identifier"]] if family["identifier"] else []
        settings = taxonomy.Settings(small_cell_floor=floor)
        read = reading.read_table(f"{table}", small_cell_floor=floor)
        document = profile.build_document(read, settings, declared, [], [])
        case = Case(f"book-{family['family']}", folder, table, document, floor)
        for place, name in enumerate(family["names"]):
            case.cells[name] = [row[place] for row in family["rows"]]
        built += [case]
    return built


def battery(home: pathlib.Path, floor: int) -> "list[Case]":
    """Every case of the battery, described at `floor` through the real path."""
    built: "list[Case]" = []
    for name, suffix, text, declared, measured in _tables():
        folder = home / name
        folder.mkdir(parents=True, exist_ok=True)
        table = fixtures.write(folder, f"real{suffix}", text)
        settings = taxonomy.Settings(small_cell_floor=floor)
        read = reading.read_table(f"{table}", small_cell_floor=floor)
        document = profile.build_document(read, settings, declared, [], measured)
        case = Case(name, folder, table, document, floor)
        # READ BACK WITH A CSV READER AND NOT BY SPLITTING (measured while
        # this file was built): four of these tables quote a field that
        # holds the delimiter -- `"1,234.56"` is one cell of the numbers
        # family -- and splitting on the mark turned every one of them
        # into two, so the VALUE and WORD clauses below were asked about
        # cells no file holds.
        rows = kpi_shapes.csv_rows(table)
        for place, column in enumerate(rows[0]):
            case.cells[column] = [
                row[place] for row in rows[1:] if len(row) > place
            ]
        built += [case]
    built += _workbook_cases(home, floor)
    return built


@pytest.fixture(scope="module")
def described(tmp_path_factory: pytest.TempPathFactory) -> "dict[int, list[Case]]":
    """The battery at all three floors, built once for this module."""
    home = tmp_path_factory.mktemp("stage3-gate")
    return {floor: battery(home / f"f{floor}", floor) for floor in FLOORS}


# -- the walk ----------------------------------------------------------


def _leaves(
    node: object, path: "tuple[str, ...]", keys: "tuple[str, ...]" = ()
):
    """Every number a document carries, with its path and its map keys.

    The same walk `profile._check_published` takes, so a mapping whose
    keys the data decides is reported at the `{}` path the rules table
    keys it by, with the key itself carried alongside.
    """
    rules = profile.PUBLICATION_RULES
    if isinstance(node, dict):
        for name in sorted(node):
            free = path + (_ANY,)
            if free in rules:
                yield from _leaves(node[name], free, keys + (name,))
            else:
                yield from _leaves(node[name], path + (name,), keys)
        return
    if isinstance(node, list):
        for item in node:
            yield from _leaves(item, path + (_EACH,), keys)
        return
    if isinstance(node, bool):
        return
    if isinstance(node, (int, float)):
        yield path, keys, node


def _group_line(floor: int, kind: str) -> int:
    """The line a GROUP count at this kind of path is held to.

    `parsing.census_floor` above a floor of one; the settings floor at
    one, where the description names every value the column holds
    anyway (contract C5-S13 and the owner's own reading of it, quoted
    at `parsing.tail_may_list`). Kinds whose own name says the settings
    floor read it at every floor.
    """
    if floor < 2 or kind in SETTINGS_FLOOR_KINDS:
        return floor
    return parsing.census_floor(floor)


def _key(block: object, dotted: str) -> "int | None":
    """One whole-number key of a block, by its dotted name."""
    node: object = block
    for step in dotted.split("."):
        if not isinstance(node, dict) or step not in node:
            return None
        node = node[step]
    return node if isinstance(node, int) and not isinstance(node, bool) else None


def _population(block: object, name: str, holder: object) -> "int | None":
    """One population a reader can subtract a published count from.

    Two of them are stated in two keys rather than one, so they are
    spelled out here: `PARSED` is the cells a date or clock reading
    reached, which is `n_present` less `n_unparsed`; `LEVEL_ROOM` is the
    present cells the named levels may cover, which is `n_present` less
    the rows the floor pooled. `VARIANT_ROOM` is the same question one
    level down: the level's own cells less the spellings it withheld.
    """
    if name == "PARSED":
        present, unread = _key(block, "n_present"), _key(block, "n_unparsed")
        if present is None or unread is None:
            return None
        return present - unread
    if name == "LEVEL_ROOM":
        present = _key(block, "n_present")
        if present is None:
            return None
        pooled = _key(block, "suppressed_rows")
        return present - (pooled if pooled is not None else 0)
    if name == "VARIANT_ROOM":
        if not isinstance(holder, dict):
            return None
        count = _key(holder, "count")
        if count is None:
            return None
        withheld = holder["variants_withheld"] if "variants_withheld" in holder else {}
        pooled = 0
        if isinstance(withheld, dict):
            for one in withheld.values():
                if isinstance(one, int) and not isinstance(one, bool):
                    pooled = pooled + one
        return count - pooled
    return _key(block, name)


def _blocks(document: "dict"):
    """Every block a GROUP count's population may be read from, with its holder.

    A count stands in the block that publishes the totals it is
    subtracted from, and the wrappers are blocks of their own: a
    `parts[]` entry has its own `n_present`, and so does the `labels`
    half of a compound column.
    """
    for block in document["columns"]:
        yield block, block
        for name in ("numbers", "labels"):
            if isinstance(block[name] if name in block else None, dict):
                yield block[name], block[name]
        for part in block["parts"] if "parts" in block else []:
            if isinstance(part, dict):
                yield part, part
        for wrapper in block["affix_variants"] if "affix_variants" in block else []:
            if not isinstance(wrapper, dict) or "numbers" not in wrapper:
                continue
            if isinstance(wrapper["numbers"], dict):
                yield wrapper["numbers"], wrapper["numbers"]


def _census_breaches(block: object, floor: int, where: str) -> "list[str]":
    """Every census of one block whose named counts leave a group over.

    `parsing.census_nameable` asked from outside: the rule is written
    once, in the module the producer, the loader and the checker all
    read it from, and this gate asks it of the finished document
    instead of restating it.

    NOT ASKED AT A FLOOR OF ONE, for the reason `_group_line` gives: a
    census of levels and spellings names every group of one row there,
    on purpose (contract C5-S13), while `census_nameable`'s own line is
    two at every floor. Measured: 254 of these at a floor of one, every
    one of them a level or a spelling one row wrote.
    """
    found: "list[str]" = []
    if not isinstance(block, dict) or floor < 2:
        return found
    for path in sorted(GATE_CENSUSES):
        holder = block
        if path == _path("columns.[].levels.[].count"):
            levels = block["levels"] if "levels" in block else None
            if not isinstance(levels, list) or not levels:
                continue
            named = [
                level["count"]
                for level in levels
                if isinstance(level, dict) and isinstance(level["count"], int)
            ]
            totals = [
                _population(block, one, holder)
                for one in GATE_POPULATIONS[path]
            ]
            if None in totals:
                continue
            if not parsing.census_nameable(named, list(totals), floor):
                found += [
                    f"{where}: the levels census names {named} against {totals}, "
                    f"which leaves a group below the line"
                ]
            continue
        name = path[len(path) - 2]
        census = block[name] if name in block else None
        if not isinstance(census, dict) or not census:
            continue
        named = [
            census[key]
            for key in sorted(census)
            if key not in POOL_KEYS
            and isinstance(census[key], int)
            and not isinstance(census[key], bool)
        ]
        if not named or any(key in POOL_KEYS for key in census):
            # A CENSUS THAT POOLED SOMETHING HAS ALREADY SPOKEN about
            # its remainder: the pool is the group it may not name, and
            # what is left over of the population is that pool. There
            # is no subtraction left for a reader to do.
            continue
        totals = [_population(block, one, holder) for one in GATE_POPULATIONS[path]]
        if None in totals or not totals:
            continue
        if not parsing.census_nameable(named, list(totals), floor):
            found += [
                f"{where}.{name}: names {named} against {totals}, which leaves "
                f"a group below the line"
            ]
    # ...and the variants of each level, one level down.
    for level in (block["levels"] if "levels" in block else []) or []:
        if not isinstance(level, dict):
            continue
        variants = level["variants"] if "variants" in level else None
        if not isinstance(variants, dict) or not variants:
            continue
        if any(key in POOL_KEYS for key in variants):
            continue
        named = [
            variants[key]
            for key in sorted(variants)
            if isinstance(variants[key], int) and not isinstance(variants[key], bool)
        ]
        room = _population(block, "VARIANT_ROOM", level)
        if not named or room is None:
            continue
        if not parsing.census_nameable(named, [room], floor):
            found += [
                f"{where}.levels[].variants: names {named} against {room}"
            ]
    return found


def _word_breaches(
    block: object, cells: "list[str]", floor: int, where: str
) -> "list[str]":
    """Every WORD_BY_COUNT word standing where too few cells wore it.

    Rule W of the stage-3 count inventory (plan P4-D335): a word moved
    by a count stands exactly where enough cells wore it, so a reader
    who knows how every other cell was written reads the last one's
    spelling off the word. The line is `parsing.census_floor` at every
    floor -- never one, whatever the settings floor -- which is what
    `taxonomy._negative_form` and the mark rule beside it already read.
    """
    found: "list[str]" = []
    if not isinstance(block, dict):
        return found
    line = parsing.census_floor(floor)
    for path in sorted(WORD_READERS):
        name = path[len(path) - 1]
        if name not in block:
            continue
        word = block[name]
        if word == WORD_DEFAULTS[path]:
            continue
        read = WORD_READERS[path]
        held = len([cell for cell in cells if read(cell) == word])
        if held < line:
            found += [
                f"{where}.{name}: the word {word!r} stands, and {held} cell(s) "
                f"of the column wear it, which is under {line}"
            ]
    return found


def breaches(
    document: "dict",
    floor: int,
    where: str = "",
    cells: "dict[str, list[str]] | None" = None,
) -> "list[str]":
    """EVERY WAY THIS DOCUMENT BREAKS THE GATE, named. Empty means it holds.

    One pass over every published number, one class per path, one
    question per class -- and the sentences through the binding table,
    which `tests/test_p4d334_sentence_arguments.py` states once.
    """
    found: "list[str]" = []
    rules = profile.PUBLICATION_RULES
    for path, keys, value in _leaves(document, ()):
        if path not in rules:
            found += [f"{where}{'.'.join(path)}: no publication rule"]
            continue
        kind = rules[path]
        if kind not in NUMERIC_KINDS:
            continue
        held = gate_class(path)
        if held is None:
            found += [
                f"{where}{'.'.join(path)}: no gate class. Every published number "
                f"belongs to one of {GATE_CLASSES}; add it to GATE_CLASS with the "
                f"reason, or the gate cannot say what its floor is"
            ]
            continue
        if held != GROUP:
            continue
        if keys and keys[len(keys) - 1] in POOL_KEYS:
            # THE POOLED ENTRY OF A CENSUS IS POOLED, whatever the path
            # its siblings stand at (`_FLOORED_ENTRY`, `_MIXTURE_ENTRY`).
            continue
        if not isinstance(value, int) or isinstance(value, bool):
            continue
        line = _group_line(floor, kind)
        if value != 0 and value < line:
            found += [
                f"{where}{'.'.join(path)}{list(keys)}: a GROUP count of {value}, "
                f"under the line {line}"
            ]
    for block, _holder in _blocks(document):
        name = block["name"] if isinstance(block, dict) and "name" in block else "?"
        found += _census_breaches(block, floor, f"{where}{name}")
    # ...AND THE WORDS, ASKED OF THE COLUMN'S OWN CELLS, so only of the
    # top block: a `parts[]` half or an affix wrapper holds part of a
    # cell, and the column's text is not what its word is counted over.
    for block in document["columns"] if cells is not None else []:
        held = cells[block["name"]] if block["name"] in cells else []
        found += _word_breaches(block, held, floor, f"{where}{block['name']}")
    for single in _single_group_breaches(document, floor, where):
        found += [single]
    for finding in bound._unaccounted(document, floor):
        found += [f"{where}SENTENCE: {finding}"]
    return found


def _own_leaves(block: "dict"):
    """The numbers of one block, the wrapper blocks under it left alone.

    A population is read from the block the count stands in, and
    `_blocks` already yields every wrapper as a block of its own -- so a
    walk that descended into them would ask `numbers.mode_count` against
    the TOP block's `n_used_in_statistics`, which is a different
    population and a different column half.
    """
    shallow = {
        name: block[name]
        for name in block
        if name not in ("numbers", "labels", "parts", "affix_variants")
    }
    yield from _leaves(shallow, _C)


def _single_group_breaches(
    document: "dict", floor: int, where: str
) -> "list[str]":
    """The complements of the GROUP leaves that are not censuses."""
    found: "list[str]" = []
    line = parsing.census_floor(floor) if floor > 1 else floor
    for block, holder in _blocks(document):
        if not isinstance(block, dict):
            continue
        for path, keys, value in _own_leaves(block):
            shape = gate_shape(path)
            if shape in GATE_CENSUSES or GATE_CLASS.get(shape) != GROUP:
                continue
            if not isinstance(value, int) or isinstance(value, bool):
                continue
            for name in GATE_POPULATIONS[shape]:
                total = _population(block, name, holder)
                if total is None:
                    continue
                rest = total - value
                if rest != 0 and rest < line:
                    found += [
                        f"{where}{'.'.join(path)}{list(keys)}: {value} against "
                        f"{name}={total} leaves {rest}, under the line {line}"
                    ]
    return found


# -- 1. the classification is closed -----------------------------------


def test_every_published_number_of_the_rules_table_has_exactly_one_class() -> None:
    """A path with no class fails, and that is what makes the gate survive.

    `profile.PUBLICATION_RULES` is the whole of what a description may
    carry. Every path of it whose kind can hold a NUMBER is classified
    here; a landing that publishes something new adds a rule there and
    has to add a class here before this is green again.
    """
    unplaced: "list[str]" = []
    for path in sorted(profile.PUBLICATION_RULES):
        if profile.PUBLICATION_RULES[path] not in NUMERIC_KINDS:
            continue
        if gate_class(path) is None:
            unplaced += [f"{'.'.join(path)} ({profile.PUBLICATION_RULES[path]})"]
    assert unplaced == [], (
        "these published numbers are in no class of the stage-3 gate, so the "
        "gate cannot say what floor they are held to:\n" + "\n".join(unplaced)
    )


def test_the_class_table_names_only_classes_the_gate_asks_about() -> None:
    """Every value of the table is one of the ten, and every one of the ten is used."""
    assert set(GATE_CLASS.values()) <= set(GATE_CLASSES)
    used = set(GATE_CLASS.values()) | {SENTENCE}
    assert used == set(GATE_CLASSES), sorted(set(GATE_CLASSES) - used)


def test_every_group_path_names_the_populations_a_reader_can_subtract_it_from() -> None:
    """A GROUP path with no population entry is a complement nobody asked about.

    And an EMPTY entry has to say why, in `GATE_NO_POPULATION`: without
    that, "no population" and "nobody looked" are the same line in this
    table and the second one is invisible.
    """
    missing = sorted(
        ".".join(path)
        for path in GATE_CLASS
        if GATE_CLASS[path] == GROUP and path not in GATE_POPULATIONS
    )
    assert missing == [], missing
    empty = {path for path in GATE_POPULATIONS if not GATE_POPULATIONS[path]}
    assert set(GATE_NO_POPULATION) == empty, sorted(
        ".".join(one) for one in empty ^ set(GATE_NO_POPULATION)
    )
    assert all(reason.strip() for reason in GATE_NO_POPULATION.values())


def test_every_exempt_path_cites_the_entry_that_settled_it() -> None:
    """SETTLED and WRITTEN_FORM are exempt BY NAME, with their entry beside them."""
    uncited = sorted(
        ".".join(path)
        for path in GATE_CLASS
        if GATE_CLASS[path] in (SETTLED, WRITTEN_FORM)
        and not GATE_SETTLED_BY.get(path, "").strip()
    )
    assert uncited == [], uncited
    ledger = kpi_rules.entries_by_id(kpi_rules.load_ledger())
    named = sorted(
        {
            found
            for reason in GATE_SETTLED_BY.values()
            for found in re.findall(r"K-[0-9A-Z]+-\d+", reason)
        }
    )
    assert named, "no exemption cites a ledger entry"
    assert [one for one in named if one not in ledger] == [], named


def test_every_word_moved_by_a_count_is_either_asked_or_named_as_not_asked() -> None:
    """A word the gate cannot ask is NAMED, with the rule that holds it instead.

    Without this, `WORD_NOT_ASKED` is prose nothing reads, and a fifth
    word added to the class would sit in neither table and be passed
    over in silence.
    """
    words = {path for path in GATE_CLASS if GATE_CLASS[path] == WORD_BY_COUNT}
    assert set(WORD_READERS) | set(WORD_NOT_ASKED) == words
    assert set(WORD_READERS) & set(WORD_NOT_ASKED) == set()
    assert set(WORD_DEFAULTS) == words
    assert all(reason.strip() for reason in WORD_NOT_ASKED.values())


def test_the_binding_table_is_closed_over_every_sentence() -> None:
    """The SENTENCE class rests on a table with no unbound position."""
    assert taxonomy.unbound_argument_positions() == []


# -- 2. the gate, over the battery at three floors ---------------------


@pytest.mark.parametrize("floor", FLOORS)
def test_no_published_number_of_the_battery_is_held_by_fewer_than_the_floor(
    described: "dict[int, list[Case]]", floor: int
) -> None:
    """THE GATE'S FIRST HALF, asked of every published number of every shape."""
    found: "list[str]" = []
    for case in described[floor]:
        found += breaches(case.document, floor, f"{case.name}: ", case.cells)
    assert found == [], "\n".join(found)


def test_the_battery_reaches_every_class_the_gate_asks_about(
    described: "dict[int, list[Case]]",
) -> None:
    """A gate over a battery that never reaches a class proves nothing there.

    What the battery DOES reach is measured here rather than assumed,
    so a class that stops being exercised is a red test and not a
    silence. The classes with no published number in this battery are
    named in the assertion, which is the honest statement of what the
    gate cannot yet see.
    """
    reached: "set[str]" = set()
    for case in described[11]:
        for path, _keys, _value in _leaves(case.document, ()):
            if profile.PUBLICATION_RULES.get(path) not in NUMERIC_KINDS:
                continue
            held = gate_class(path)
            if held is not None:
                reached.add(held)
        for _where, note, _block in bound._sentences(case.document):
            for _form, _place, argument in bound._positions(
                note.form, note.arguments, parsing.census_floor(11)
            ):
                if isinstance(argument, int) and not isinstance(argument, bool):
                    reached.add(SENTENCE)
        for block in case.document["columns"]:
            for path in WORD_DEFAULTS:
                name = path[len(path) - 1]
                if name in block and block[name] != WORD_DEFAULTS[path]:
                    reached.add(WORD_BY_COUNT)
    assert sorted(set(GATE_CLASSES) - reached) == [], (
        "the battery publishes no number of these classes, so the gate proves "
        "nothing about them here"
    )


# -- 3. the VALUE half: the tail rule, asked from the column -----------


_NUMBER_TOKEN = re.compile(r"(?<![A-Za-z0-9.])-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")


def _numeric_cells(cells: "list[str]") -> "list[float]":
    found = [parsing.parse_number(cell) for cell in cells]
    return sorted(one for one in found if one is not None)


def _tails_of(block: object):
    """(side, tail) for every tail anywhere in one column's block.

    A COLUMN CAN CARRY ITS TAIL ONE LEVEL DOWN. The compound role's
    numbers stand under `numbers`, a joined column's under `parts[]`,
    an affixed wrapper's under `affix_variants[].numbers` -- and a
    sweep that read `block["tails"]` alone asked the listing rule of a
    tail that was not there. Measured at a floor of one: twenty listed
    values of two compound shapes were reported as leaks because the
    admission was looked up on the wrong block.
    """
    if not isinstance(block, dict):
        return
    tails = block["tails"] if "tails" in block else None
    if isinstance(tails, dict):
        for side in ("low", "high"):
            if isinstance(tails[side] if side in tails else None, dict):
                yield side, tails[side]
    for name in ("numbers", "labels"):
        if name in block:
            yield from _tails_of(block[name])
    for part in block["parts"] if "parts" in block else []:
        yield from _tails_of(part)
    for wrapper in block["affix_variants"] if "affix_variants" in block else []:
        if isinstance(wrapper, dict) and "numbers" in wrapper:
            yield from _tails_of(wrapper["numbers"])


def _admitted(block: "dict", values: "list[float]", floor: int) -> "set[float]":
    """The outer values the LISTING RULE admits, asked of the column.

    `parsing.tail_may_list` and nothing else -- never "the tail listed
    it", which is the exemption plan P4-D346 removed because a drifted
    listing rule could not fail against it, and no longer P4-D346's own
    SECOND road either. That road exempted a tail of at most
    `parsing.TAIL_SETTLED_VALUES` values whatever the rule said, and it
    is withdrawn (plan P4-D349): it named values one row holds, and the
    pair it said those values were settled by is now withheld rather than
    published. One rule, one exemption.
    """
    allowed: "set[float]" = set()
    count = len(values)
    distinct = len(set(values))
    # HOW MANY CELLS MAKE A VALUE NOBODY'S OWN, read the way
    # `parsing.tail_may_list` reads it and not as a bare two: at a floor
    # of ONE the line is one, because the description names every value
    # the column holds there anyway (contract C5-S13, and the owner's
    # own reading of it quoted in that function). Measured: at a floor
    # of one, 182 listed values of this battery stand on a single cell
    # apiece and every one of them is listed on purpose.
    shared = (
        parsing.TAIL_SHARED_CELLS
        if floor >= parsing.TAIL_SHARED_CELLS
        else floor
    )
    for side, tail in _tails_of(block):
        if not tail["values"]:
            continue
        rows = tail["rows"]
        beyond = values[:rows] if side == "low" else values[count - rows:]
        held = collections.Counter(beyond)
        if parsing.tail_may_list(
            [held[value] for value in sorted(held)], floor, distinct, count
        ):
            for value in tail["values"]:
                if held[value] >= shared:
                    allowed.add(value)
    return allowed


def _withheld_rows(block: "dict", floor: int) -> "tuple[int, int]":
    """How many rows each side of the column the tail rule withholds.

    The block's own published `tails.low.rows` and `tails.high.rows`
    where it carries them, and `max(floor, 3)` -- the rule's own units
    -- where it carries none.
    """
    units = floor if floor > 3 else 3
    low = high = units
    for side, tail in _tails_of(block):
        rows = tail["rows"]
        if not isinstance(rows, int) or isinstance(rows, bool):
            continue
        if side == "low":
            low = max(low, rows)
        else:
            high = max(high, rows)
    return low, high


def _lone_outer(cells: "list[str]", block: "dict", floor: int) -> "set[float]":
    """The outermost values of a column that the description must not name.

    A value is one of these when EVERY row holding it lies inside the
    band the tail rule withholds, and fewer than `max(floor, 3)` rows
    hold it. Both halves are load-bearing:

    * FEWER THAN THE UNITS -- a value a larger group shares is one the
      owner's ruling of 2026-09-22 puts outside this question ("many
      people will be there and there is no big deal in knowing that
      it's there");
    * EVERY ROW INSIDE THE BAND -- because a value that also stands at
      a PUBLISHED order statistic is named there on purpose, and the
      description is allowed to name it. Measured on
      `two_readings_fit`: five rows hold 3.2, at the sorted positions 9
      to 13, and the twelve-row tail withholds 0 to 11. The boundary
      rung reads positions 11 and 12 and comes back 3.2 -- which is the
      thirteenth smallest value, a position the ladder publishes. A
      band read by VALUE rather than by position called that a leak,
      and it is the ladder the owner kept (decision 3): an interior
      rung reads two neighbouring order statistics and says what the
      column holds there.
    """
    values = _numeric_cells(cells)
    if not values:
        return set()
    counted = collections.Counter(values)
    units = floor if floor > 3 else 3
    low, high = _withheld_rows(block, floor)
    count = len(values)
    inside = collections.Counter(values[:low] + values[count - high:])
    listed = _admitted(block, values, floor)
    return {
        value
        for value in inside
        if counted[value] < units
        and inside[value] == counted[value]
        and value not in listed
    }


# A TAIL'S TWO DISTANCES ARE NOT VALUES OF THE COLUMN (plan P4-D346),
# and sweeping them as if they were reports coincidences. A mean or a
# root-mean-square over `rows` distances equals `boundary - v` for a
# single `v` only where every one of those rows holds `v`, and then `v`
# stands under at least `rows` cells and is not lone at all. Measured on
# `count_whole_one_fraction`: the high tail is a heap at the boundary,
# so both its distances are 0.0, and 0.0 is also a value one row of that
# column holds at the other end.
#
# WHAT A READER CAN DO WITH A DISTANCE IS ARITHMETIC, AND THE GATE ASKS
# THAT THROUGH THE BACK-SOLVE THE TAIL-LEAK DRIVER ALREADY HOLDS
# (`test_no_tail_of_the_battery_back_solves_to_the_value_it_withheld`),
# rather than through a second one of its own. Measured while this file
# was built: `boundary + mean_distance` over a TWELVE-row tail came back
# 7.2 on `two_readings_fit`, which is a cell of that column and is a
# coincidence -- the mean of twelve unequal distances names no row --
# and the second arithmetic written here reported it as a disclosure.
VALUE_DISTANCES = frozenset(
    _paths(
        "columns.[].tails.low.mean_distance",
        "columns.[].tails.low.rms_distance",
        "columns.[].tails.high.mean_distance",
        "columns.[].tails.high.rms_distance",
        "columns.[].low_tail.mean_distance",
        "columns.[].low_tail.rms_distance",
        "columns.[].high_tail.mean_distance",
        "columns.[].high_tail.rms_distance",
    )
)


def _value_numbers(block: "dict"):
    """Every published VALUE of one block, with the path it stands at."""
    for path, keys, value in _leaves(block, _C):
        if gate_class(path) == VALUE and gate_shape(path) not in VALUE_DISTANCES:
            yield ".".join(path), keys, float(value)


@pytest.mark.parametrize("floor", FLOORS)
def test_no_published_value_of_the_battery_names_a_lone_outer_cell(
    described: "dict[int, list[Case]]", floor: int
) -> None:
    """THE GATE'S VALUE HALF: no published value is held by too few rows.

    Asked of every numeric column of every battery shape: no number of
    the VALUE class equals a value the tail rule withholds -- one whose
    every row lies inside the band the block's own tails name, held by
    fewer than `max(floor, 3)` rows -- unless the LISTING RULE admits
    it, which is `parsing.tail_may_list` asked of the column's own cells
    beyond that boundary and never a list of paths. `_lone_outer` above
    states the band and why both its halves are there.
    """
    found: "list[str]" = []
    for case in described[floor]:
        for block in case.document["columns"]:
            cells = case.cells[block["name"]] if block["name"] in case.cells else []
            if not cells:
                continue
            lone = _lone_outer(cells, block, floor)
            if not lone:
                continue
            for where, keys, number in _value_numbers(block):
                if number in lone:
                    found += [
                        f"{case.name}/{block['name']}: {where}{list(keys)} = "
                        f"{number}, which is an outer value too few rows hold"
                    ]
    assert found == [], "\n".join(found)


def _tail_leak_driver() -> object:
    """`tools/measurements/kpi_stage3_tail_leak.py`, loaded as a module.

    THE BACK-SOLVE IS NOT WRITTEN TWICE. The driver already holds the
    walk a reader would make with a tail's published rows, mean and
    root-mean-square distance, with its own budget and its own
    permissive default; the gate asks that walk rather than growing a
    second one that could disagree with it.
    """
    spec = importlib.util.spec_from_file_location(
        "kpi_stage3_tail_leak_under_the_gate",
        kpi_rules.MEASUREMENTS / "kpi_stage3_tail_leak.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("floor", FLOORS)
def test_no_tail_of_the_battery_back_solves_to_the_value_it_withheld(
    described: "dict[int, list[Case]]", floor: int
) -> None:
    """THE OTHER WAY A VALUE REACHES A READER: arithmetic, not equality.

    A date or clock tail publishes how many rows lie beyond its
    boundary and two distances. Where those three leave exactly ONE
    multiset of whole distances, the outermost value follows from them,
    and a gate that only compared numbers would not see it. The walk is
    the tail-leak driver's own (`_pinned_and_room`), asked here of every
    block of the battery that carries a tail.
    """
    driver = _tail_leak_driver()
    found: "list[str]" = []
    for case in described[floor]:
        for block in case.document["columns"]:
            pinned, _room, _unsearched = driver._pinned_and_room(block, floor)
            if pinned:
                found += [
                    f"{case.name}/{block['name']}: {pinned} tail(s) settled to one "
                    f"arithmetic by their own published facts"
                ]
    assert found == [], "\n".join(found)


# -- 3a. what the two measurements miss, and the mutants that say so ---
#
# THE GOVERNANCE PASS OF STAGE 3'S REVIEW (items 3 and 4). Both numbers
# the section above rests on scored NOUGHT on a disclosure that had
# happened, and each for a reason of its own. They are reproduced here
# as the driver's own functions, asked of the exact inputs the review
# gave, and each is watched failing under the arithmetic it replaced --
# a measurement nobody has watched fail is a measurement nobody knows
# the reach of.

# The review's own reconstruction: eleven distances summing to 24 whose
# squares sum to 104. Two multisets meet both sums -- [8, 4, 4, 1 x 8]
# and [8, 5, 2, 2, 1 x 7] -- so the whole multiset is NOT settled, while
# both say the largest distance is 8 and that ONE row holds it. At a low
# clock boundary of 00:20 that names the minimum 00:12 and its count.
AMBIGUOUS_BUT_REVEALING = (11, 24, 104)


def test_the_back_solve_sees_an_extreme_every_solution_agrees_on() -> None:
    """Item 3: the protected value is the EXTREME, not the whole multiset.

    The measurement asked whether the published facts leave one multiset
    of distances, and answered "no, two" -- while both of the two named
    the same outermost value and the same count of it. The question is
    now whether the extreme and its count VARY across the solutions.
    """
    driver = _tail_leak_driver()
    rows, total, squares = AMBIGUOUS_BUT_REVEALING
    assert driver._multisets(
        rows, total, squares, total, [driver.ROOM_STEPS], [False]
    ) == 2, (
        "this case is here because the multiset is NOT unique; if that "
        "stopped being true the case would prove nothing"
    )
    settled, spent = driver._settled(rows, total, squares, total)
    assert not spent
    assert settled, (
        "both multisets these facts admit put the largest distance at 8 "
        "and one row on it, so the outermost value and its count are "
        "named and the measurement must say so"
    )
    assert driver._extremes(
        rows, total, squares, total, [driver.ROOM_STEPS], [False]
    ) == {(8, 1)}


def test_the_back_solve_still_reports_room_where_the_extreme_varies() -> None:
    """...and it is not a measurement that always says "settled".

    Eleven different whole distances summing to 66 with squares 506 admit
    a largest of 15 and a largest of 16, so a reader cannot name the
    outermost value and this must read UNSETTLED. Without this half the
    repair above would be a number that cannot go down.
    """
    driver = _tail_leak_driver()
    settled, spent = driver._settled(11, 66, 506, 66)
    assert not spent and not settled
    assert len(driver._extremes(
        11, 66, 506, 66, [driver.ROOM_STEPS], [False]
    )) > 1


# Two pages, each printing a value the description withholds, and each
# in the shape that scored nought: a moment after a label, whose spelling
# carries a SPACE and split into two tokens; and a clock value at the end
# of a sentence, which wears the full stop because a point is part of the
# number spellings the split must keep together.
SENTENCE_LEAKS = (
    ("Earliest: 2024-02-02 12:34:56", "2024-02-02 12:34:56", "a moment after a label"),
    ("  Earliest: 2024-02-02 12:34:56 +0100", "2024-02-02 12:34:56 +0100", "a moment and its offset"),
    ("The earliest is 00:12.", "00:12", "a clock value ending a sentence"),
    ("The smallest is 1002.32.", "1002.32", "a number ending a sentence"),
)


def _sentence_leaks_missed(split) -> "list[str]":
    """Every page of `SENTENCE_LEAKS` whose withheld value ``split`` misses."""
    return [
        f"{why}: {line.strip()!r} does not give back {value!r}"
        for line, value, why in SENTENCE_LEAKS
        if value not in split(line)
    ]


def test_the_literal_leak_measurement_reads_a_value_inside_a_sentence() -> None:
    """Item 4: a withheld end printed in prose is a leak and must count."""
    driver = _tail_leak_driver()
    assert _sentence_leaks_missed(driver._tokens) == []


def test_the_sentence_leak_witness_fails_on_the_whole_word_split() -> None:
    """And it is watched failing, on the split it replaced.

    The old split yielded whole tokens and nothing else, so a moment
    broke in two at its space and a value at the end of a sentence kept
    the full stop: every page above scored nought.
    """
    def whole_words(text):
        found = []
        word = ""
        for letter in text:
            if letter.isalnum() or letter in "-:+./":
                word += letter
            else:
                if word:
                    found += [word]
                word = ""
        if word:
            found += [word]
        return found

    missed = _sentence_leaks_missed(whole_words)
    assert len(missed) == len(SENTENCE_LEAKS), missed


# -- 3b. the reconstruction attacks (the fix pass, plan P4-D349) -------
#
# WHY THIS SECTION EXISTS. The walk above asks the tail-leak driver's
# back-solve of the BATTERY, and the battery is the count design's own
# shapes. It could not see the defect the adversarial round of stage 3
# returned REJECT on, for three reasons at once: no shape of it is a
# column of consecutive values; the driver's walk read `low_tail` and
# `high_tail` and so measured a numeric block as having no tail at all;
# and neither the walk nor the gate used the one fact that turns close
# estimation into exact reconstruction -- the column's own published
# remark that every value in it is different.
#
# Each case below IS one of the round's reproductions, named by what it
# reproduces, and the three tests after them are the three things that
# must hold of every one: nothing a single row holds is named, no tail's
# published pair settles its own distances once the reader uses the whole
# description, and the bounded scales the owner keeps are still named.


def _consecutive_dates(count: int, start: str = "2020-01-01") -> "list[str]":
    """`count` consecutive days as text, from `start`."""
    first = datetime.date.fromisoformat(start)
    return [
        (first + datetime.timedelta(days=step)).isoformat()
        for step in range(count)
    ]


def _consecutive_minutes(count: int, first: int = 7 * 60) -> "list[str]":
    """`count` consecutive minutes as `hh:mm`, from `first` minutes of day."""
    return [
        "%02d:%02d" % divmod(first + step, 60) for step in range(count)
    ]


# THE ROUND'S OWN REPRODUCTIONS, each with the item that found it.
RECONSTRUCTIONS = (
    # numeric item 1: the pair, the grid and "every value different"
    # leave one multiset on both sides at once.
    ("integers_0_to_1100", [str(value) for value in range(1101)]),
    # ...and it is not a property of whole numbers.
    ("tenths_0_to_110", [f"{value / 10.0:.1f}" for value in range(1101)]),
    # ...nor of 1,101 of them.
    ("integers_0_to_1199", [str(value) for value in range(1200)]),
    # numeric item 1's second half: the withdrawn second listing road
    # published `[1089, 1100]`, and one row holds 1100.
    (
        "heap_then_one_far",
        [str(value) for value in range(1089)] + ["1089"] * 11 + ["1100"],
    ),
    # dates item 2: 240 consecutive days, and 240 unique minutes.
    ("dates_240_consecutive", _consecutive_dates(240)),
    ("minutes_240_unique", _consecutive_minutes(240)),
    # dates item 3: the second road named `06:59`, held by ONE cell.
    (
        "clock_one_beside_a_heap",
        ["06:58"] * 10 + ["06:59"] + _consecutive_minutes(239),
    ),
    # dates item 1's own shape, whose boundary is January 12.
    ("dates_200_consecutive", _consecutive_dates(200)),
)

# THE SCALES THE OWNER KEEPS, at the size at which the listing rule
# reaches them (plan P4-D346's own measurement). They are here so that
# the fix cannot be bought by withholding everything: a pass that
# stopped these tails naming their values would be a pass that threw
# away what the owner ruled publishable.
KEPT_SCALES = (
    ("pain_0_to_10", [str(value % 11) for value in range(1800)]),
    ("risk_grade_1_to_5", [str(1 + value % 5) for value in range(1800)]),
    ("likert_1_to_7", [str(1 + value % 7) for value in range(1800)]),
)


# THE SHAPES THE WITHHELD PAIR COSTS SOMETHING, beside the attacks. The
# first is the review's own padded column: 399 consecutive record numbers
# beside one far value, where the withheld tail carries the whole of the
# column's spread. The second is that column without the far value, so
# the measurement says which half the cost belongs to.
COST_SHAPES = (
    (
        "padded_399_beside_one_far",
        [f"{value:05}" for value in range(1, 400)] + ["12345"],
    ),
    ("padded_399_alone", [f"{value:05}" for value in range(1, 400)] + ["00400"]),
)


def withheld_cost(folder: pathlib.Path) -> "tuple[int, int, int]":
    """The withheld pair's own cost, measured (ledger entry `K-S3-15`).

    Three numbers over the fix pass's own shapes -- every reconstruction
    attack and the two `COST_SHAPES`: how many tail SIDES publish neither
    distance, how many checkable obligations their twins MISS at seeds 0
    and 4 together, and how many shapes were measured. The second number
    is the cost: a tail with no pair of its own is read through the
    column's own published mean and spread, and where the withheld tail
    IS the column's spread no reading can average to a mean the far cell
    carries.
    """
    sides = 0
    missing = 0
    shapes = RECONSTRUCTIONS + COST_SHAPES
    for name, cells in shapes:
        described = kpi_shapes.describe(
            folder / name, name, _one_column("value", cells), 11
        )
        for block in described.document["columns"]:
            for _side, tail in _tails_of(block):
                if tail["mean_distance"] is None:
                    sides += 1
            for key in ("low_tail", "high_tail"):
                one = block[key] if key in block else None
                if isinstance(one, dict) and one["mean_distance"] is None:
                    sides += 1
        for seed in (0, 4):
            twin = kpi_shapes.twin_text(described, seed)
            outcome = kpi_shapes.measure(described, twin, f"twin-{seed}.csv")
            missing += len(kpi_shapes.missed(outcome))
    return sides, missing, len(shapes)


def _attack(folder: pathlib.Path, name: str, cells: "list[str]") -> Case:
    """One reconstruction attack through the whole product path."""
    home = folder / name
    home.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(home, "real.csv", _one_column("value", cells))
    read = reading.read_table(f"{table}", small_cell_floor=11)
    document = profile.build_document(
        read, taxonomy.Settings(small_cell_floor=11), [], [], []
    )
    case = Case(name, home, table, document, 11)
    case.cells["value"] = list(cells)
    return case


@pytest.fixture(scope="module")
def attacked(tmp_path_factory: pytest.TempPathFactory) -> "dict[str, Case]":
    """Every reconstruction attack and every kept scale, described once."""
    home = tmp_path_factory.mktemp("stage3-gate-attacks")
    built: "dict[str, Case]" = {}
    for name, cells in RECONSTRUCTIONS + KEPT_SCALES:
        built[name] = _attack(home, name, cells)
    return built


def _reader_settles(block: "dict", driver: object) -> int:
    """How many of one block's tails the WHOLE description settles.

    The driver's own walk, asked with the facts a reader of that
    description holds beside a tail's three numbers: for a numeric block
    the published grid, the sign counts and the column's own "every value
    different" remark; for a date or clock block the space's own edges
    and the same remark. Nothing here restates the walk.
    """
    settled = 0
    if isinstance(block.get("tails"), dict):
        pinned, _room, _unsearched = driver._numeric_pinned(
            block, 11, driver._numeric_all_different(block)
        )
        settled += pinned
    if block.get("low_tail") is not None or block.get("high_tail") is not None:
        pinned, _room, _unsearched = driver._pinned_and_room(block, 11)
        settled += pinned
    return settled


# THE FOUR MOMENTS, WHICH A SYMMETRIC COLUMN MAKES COINCIDE WITH A CELL.
# The owner ruled on 2026-09-22 that the column's own mean, spread, skew
# and tail weight stay EXACT, and a moment is a statistic over every cell
# rather than any cell's value. The integers 0 to 1199 are symmetric, so
# their skew is exactly 0.0 -- which is also the value one row of that
# column holds, and the sweep below would read the coincidence as a
# naming. It is the same exemption `VALUE_DISTANCES` is: a number of the
# VALUE class that is not a value.
def _outermost_text(cells: "list[str]", units: int) -> "set[str]":
    """The `units` outermost cells of a column, as the text they were written.

    Sorted as TEXT, which is the ordering of every shape in
    `RECONSTRUCTIONS`: an ISO date and an `hh:mm` clock time both sort by
    their own order as text, so no parser is needed and none can disagree
    with the producer's. A column whose spellings do not sort that way
    would need its own reading, and none here is of that kind.
    """
    ordered = sorted(cell for cell in cells if cell)
    if len(ordered) <= 2 * units:
        return set(ordered)
    return set(ordered[:units]) | set(ordered[len(ordered) - units:])


_MOMENT_LINES = (".mean[", ".std[", ".skew[", ".kurtosis[")


def _is_a_moment(line: str) -> bool:
    """Whether one leak line names a moment rather than a cell's value."""
    for name in _MOMENT_LINES:
        if name in line:
            return True
    return False


@pytest.mark.parametrize("name", [one for one, _cells in RECONSTRUCTIONS])
def test_no_reconstruction_attack_names_a_value_one_row_holds(
    attacked: "dict[str, Case]", name: str
) -> None:
    """THE VALUE HALF, asked of the round's own reproductions.

    `list(range(1089)) + [1089] * 11 + [1100]` published the high-tail
    values `[1089, 1100]` before this pass, and ONE row of that column
    holds 1100 while `percentiles.max` is null. The clock shape published
    `06:59` beside ten cells at `06:58` for the same reason.
    """
    case = attacked[name]
    for block in case.document["columns"]:
        held = case.cells[block["name"]] if block["name"] in case.cells else []
        found = [
            line for line in _value_leaks(block, held, 11)
            if not _is_a_moment(line)
        ]
        assert found == [], (
            f"{name}: the description names a value too few rows hold: "
            f"{found}"
        )
        # AND THE DATE AND CLOCK CASES ARE ASKED IN THEIR OWN UNIT. The
        # sweep above reads NUMBERS, so on a column of dates or clock
        # times it has nothing to compare and would pass by saying
        # nothing. What those columns publish as a value is TEXT -- each
        # tail's boundary, and the values a listed tail names -- so the
        # outermost eleven cells are compared against that text directly.
        # A boundary is a real cell of the column and is published on
        # purpose; what it may not be is one of the cells the floor
        # protects.
        outer = _outermost_text(held, 11)
        for key in ("low_tail", "high_tail"):
            tail = block[key] if key in block else None
            if not isinstance(tail, dict):
                continue
            named = [tail["boundary"]]
            if isinstance(tail["values"], list):
                named += list(tail["values"])
            for value in named:
                assert value not in outer, (
                    f"{name} {key}: the description names {value!r}, one of "
                    f"the eleven outermost cells of the column"
                )


@pytest.mark.parametrize("name", [one for one, _cells in RECONSTRUCTIONS])
def test_no_reconstruction_attack_has_a_tail_the_description_settles(
    attacked: "dict[str, Case]", name: str
) -> None:
    """THE ARITHMETIC HALF, with the whole description in the reader's hands.

    The integers 0 to 1100 once each published eleven rows, a mean
    distance of 6 and a root-mean-square of root-46 on each side, and the
    same description says every value is different: eleven DIFFERENT whole
    distances summing to 66 are 1 to 11 and nothing else, so both ends
    came back exactly. Measured with the driver's own walk before the fix:
    each side admitted ONE multiset with the remark and 64 without it.
    """
    driver = _tail_leak_driver()
    case = attacked[name]
    for block in case.document["columns"]:
        assert _reader_settles(block, driver) == 0, (
            f"{name}/{block['name']}: a published tail is settled to one "
            f"multiset by the description's own facts"
        )


@pytest.mark.parametrize("name", [one for one, _cells in KEPT_SCALES])
def test_the_scales_the_owner_keeps_still_name_their_values(
    attacked: "dict[str, Case]", name: str
) -> None:
    """AND THE FIX IS NOT BOUGHT BY WITHHOLDING EVERYTHING.

    The owner ruled on bounded scales with few values: "we don't need to
    be worried about the tails ... many people will be there and there is
    no big deal in knowing that it's there." Every one of these three
    holds each of its steps on more than a hundred rows, so the listing
    rule reaches both of its tails, and a pass that made them say their
    shape instead would have thrown the ruling away.
    """
    case = attacked[name]
    block = case.document["columns"][0]
    tails = block["tails"]
    assert isinstance(tails, dict)
    for side in ("low", "high"):
        one = tails[side]
        assert isinstance(one, dict) and one["values"], (
            f"{name} {side}: a bounded scale the owner keeps stopped naming "
            f"its values"
        )
        assert one["mean_distance"] is not None, (
            f"{name} {side}: a listed tail publishes its two distances"
        )


def test_the_reconstruction_gate_turns_red_when_the_pair_goes_back(
    attacked: "dict[str, Case]",
) -> None:
    """MUTATION 6: the withheld pair put back, and the gate must see it.

    A guard that passes is not a guard. The two distances of the integer
    column's low tail are the ones the producer withheld -- eleven
    distances 1 to 11, so a whole sum of 66 and a whole sum of squares of
    506 over eleven rows -- and with them back the walk above must find
    the tail settled. The numbers are derived from the rule and not
    copied from any output: the tail rule puts the low boundary at the
    eleventh order statistic, which on the integers 0 to 1100 is 11, and
    the eleven rows below it are 0 to 10.
    """
    driver = _tail_leak_driver()
    case = attacked["integers_0_to_1100"]
    block = copy.deepcopy(case.document["columns"][0])
    tails = block["tails"]
    assert isinstance(tails, dict) and isinstance(tails["low"], dict)
    rows = 11
    tails["low"] = dict(tails["low"])
    tails["low"]["mean_distance"] = 66.0 / rows
    tails["low"]["rms_distance"] = math.sqrt(506.0 / rows)
    assert _reader_settles(block, driver) > 0, (
        "the published pair of the low tail was put back and the "
        "back-solve did not settle it: the walk does not see what the "
        "review reconstructed by hand"
    )


# -- 4. the refusal half -----------------------------------------------


def _clinic(folder: pathlib.Path, rows: int, subjects: "int | None" = None) -> pathlib.Path:
    return fixtures.write(folder, "clinic.csv", kpi_shapes.visits_table(rows, subjects))


def _left(folder: pathlib.Path) -> "list[str]":
    return sorted(one.name for one in folder.iterdir())


@pytest.mark.parametrize(
    "name,rows,subjects",
    [
        ("one row", 1, None),
        ("one short of the floor", parsing.POPULATION_FLOOR - 1, None),
        ("people one short of the floor", 500, parsing.POPULATION_FLOOR - 1),
    ],
)
def test_a_population_under_the_floor_is_refused_and_nothing_is_written(
    tmp_path: pathlib.Path, name: str, rows: int, subjects: "int | None"
) -> None:
    """THE GATE'S SECOND HALF, through `cli.main` and not a function beside it.

    A one-row table, a table one row short of the floor, and 500 rows
    over 99 people: each is refused, and the refusal happens before a
    description is built, so nothing reaches the disk.
    """
    folder = tmp_path / name.replace(" ", "-")
    folder.mkdir()
    table = _clinic(folder, rows, subjects)
    flags = ["--identifier", "subject_id"] if subjects is not None else []
    assert cli.main(["profile", f"{table}"] + flags) == 1
    assert _left(folder) == ["clinic.csv"], (
        "a refused run left a file behind: nothing may be written for a "
        "population the floor refuses"
    )


@pytest.mark.parametrize(
    "rows", [parsing.POPULATION_FLOOR, parsing.POPULATION_NOTICE_LINE - 1]
)
def test_a_population_in_the_notice_band_carries_the_notice_on_every_page(
    tmp_path: pathlib.Path, rows: int
) -> None:
    """Both ends of the band: the description, the twin's report and the summary."""
    folder = tmp_path / f"band-{rows}"
    folder.mkdir()
    table = _clinic(folder, rows)
    assert kpi_shapes.quiet_cli(["profile", f"{table}", "--out-dir", f"{folder}"]) == 0
    document = json.loads(
        (folder / "clinic-profile.json").read_text(encoding="utf-8")
    )
    said = [note for note in document["publication_notes"] if note["column"] == ""]
    assert said, f"{rows} rows carries no note about the size of the table"
    assert kpi_shapes.quiet_cli(
        ["generate", f"{folder / 'clinic-profile.json'}", "--out-dir", f"{folder}",
         "--seed", "4", "--replace"]
    ) == 0
    written = [
        one
        for one in folder.iterdir()
        if one.suffix in (".md", ".txt") or one.name.endswith("-report.md")
    ]
    assert len(written) >= 2, (
        "the run wrote fewer than two pages for the notice to reach: the "
        "description's own plain-language page and the twin's report are "
        f"both written here, and what it left was {sorted(one.name for one in written)}"
    )
    for page in written:
        assert f"{said[0]['note']}" in page.read_text(encoding="utf-8"), (
            f"{page.name} does not carry the notice the description states"
        )


def test_a_population_at_the_line_carries_no_notice(tmp_path: pathlib.Path) -> None:
    """At `POPULATION_NOTICE_LINE` the run says nothing about its size."""
    folder = tmp_path / "at-the-line"
    folder.mkdir()
    table = _clinic(folder, parsing.POPULATION_NOTICE_LINE)
    assert kpi_shapes.quiet_cli(["profile", f"{table}", "--out-dir", f"{folder}"]) == 0
    document = json.loads(
        (folder / "clinic-profile.json").read_text(encoding="utf-8")
    )
    assert [note for note in document["publication_notes"] if note["column"] == ""] == []


# -- 5. the mutations --------------------------------------------------
#
# A GUARD THAT PASSES IS NOT A GUARD. Each of these withdraws one rule
# from a document the gate has just accepted, and each must turn it red.


@pytest.fixture(scope="module")
def one_case(tmp_path_factory: pytest.TempPathFactory) -> Case:
    """One battery shape at the default floor, for the mutants to break."""
    home = tmp_path_factory.mktemp("stage3-gate-mutants")
    folder = home / "pooled"
    folder.mkdir(parents=True)
    cells, _flags = stage3_battery.SHAPES["labels_one_blank_pooled"](
        random.Random(stage3_battery.BATTERY_SEED)
    )
    text = stage3_battery.rows_text(["value"], [[cell] for cell in cells])
    table = fixtures.write(folder, "real.csv", text)
    read = reading.read_table(f"{table}", small_cell_floor=11)
    document = profile.build_document(
        read, taxonomy.Settings(small_cell_floor=11), [], [], []
    )
    case = Case("labels_one_blank_pooled", folder, table, document, 11)
    case.cells["value"] = list(cells)
    return case


def test_the_gate_turns_red_on_a_group_count_republished_below_the_line(
    one_case: Case,
) -> None:
    """MUTATION 1: one level's count re-published at its measured 1..line-1.

    The shape's rare level covers exactly one row and the floor pooled
    it. Writing that one back into the levels census is the disclosure
    the floor exists to stop, and the gate must see it.
    """
    document = json.loads(json.dumps(one_case.document, default=str))
    assert breaches(one_case.document, 11) == []
    levels = document["columns"][0]["levels"]
    assert levels, "this shape publishes no level for the mutant to move"
    before = levels[0]["count"]
    levels[0]["count"] = 1
    assert 0 < 1 < parsing.census_floor(11) <= before
    found = [one for one in breaches(document, 11) if "GROUP count of 1" in one]
    assert found, (
        "a level of ONE row was published and the gate said nothing: the GROUP "
        "clause is not asking its own question"
    )


def test_the_gate_turns_red_on_a_sentence_argument_that_differs_from_its_key(
    described: "dict[int, list[Case]]",
) -> None:
    """MUTATION 2: a sentence carries a count the key beside it does not.

    The binding table says an argument IS the key it restates. A
    sentence that prints one more than its key is a count no rule
    governs, and it is the whole reason `ARGUMENT_BINDINGS` exists.
    """
    moved = 0
    for case in described[11]:
        document = dict(case.document)
        columns = []
        for block in case.document["columns"]:
            copy = dict(block)
            remarks = list(copy["remarks"])
            for place in range(len(remarks)):
                note = remarks[place]
                if not isinstance(note, taxonomy.Note):
                    continue
                for argument in range(len(note.arguments)):
                    binding = taxonomy.argument_binding(note.form, argument)
                    value = note.arguments[argument]
                    if binding[:1] != (taxonomy.BIND_KEY,):
                        continue
                    if isinstance(value, bool) or not isinstance(value, int):
                        continue
                    parts = list(note.arguments)
                    parts[argument] = value + 1
                    remarks[place] = taxonomy.note(note.form, tuple(parts))
                    moved += 1
                    break
                if moved:
                    break
            copy["remarks"] = remarks
            columns += [copy]
            if moved:
                break
        if not moved:
            continue
        document["columns"] = columns + case.document["columns"][len(columns):]
        found = [one for one in breaches(document, 11) if "SENTENCE" in one]
        assert found, (
            "a sentence printed a count one greater than the key it restates "
            "and the gate said nothing"
        )
        return
    raise AssertionError("no sentence of the battery binds an argument to a key")


def test_the_gate_turns_red_on_an_exact_minimum_put_back_into_a_block(
    tmp_path: pathlib.Path,
) -> None:
    """MUTATION 3: `percentiles.min` set back to the column's own smallest value.

    This is what every numeric block published before the tail rule,
    and it names the row that holds the smallest value outright.
    """
    folder = tmp_path / "minimum"
    folder.mkdir()
    _name, cells = _heavy_tails()[0]
    table = fixtures.write(folder, "real.csv", _one_column("charges", cells))
    read = reading.read_table(f"{table}", small_cell_floor=11)
    document = profile.build_document(
        read, taxonomy.Settings(small_cell_floor=11), [], [], []
    )
    block = document["columns"][0]
    assert _value_leaks(block, cells, 11) == []
    values = _numeric_cells(cells)
    block["percentiles"]["min"] = values[0]
    assert _value_leaks(block, cells, 11), (
        "the column's exact minimum was published and the VALUE clause said "
        "nothing"
    )


@pytest.mark.parametrize("named", (1, 2, 3))
@pytest.mark.parametrize("side", ("low", "high"))
def test_the_gate_turns_red_on_a_tail_listing_a_value_one_row_holds(
    tmp_path: pathlib.Path, side: str, named: int,
) -> None:
    """MUTATION 4: a tail lists values one row of the column holds.

    The listing rule admits a tail only where every value it would name
    stands on at least `parsing.TAIL_SHARED_CELLS` of its cells. A tail
    that lists lone values is the exemption the gate must not grant,
    and `_admitted` asks `parsing.tail_may_list` -- the RULE, and its
    premise -- rather than membership, so that a drifted listing rule
    cannot buy itself the answer.

    ONE VALUE, TWO, AND THREE, ON BOTH SIDES (the governance pass of
    stage 3's review, item 5). The committed mutant listed THREE, and
    the road plan P4-D349 withdrew had exempted any list of at most
    `parsing.TAIL_SETTLED_VALUES` values whatever the rule said -- so the
    one mutant this file carried was the one shape that branch could not
    have hidden, and a gate still granting the exemption would have
    passed it. Measured on this file's own 600-row `charges` fixture at
    a floor of eleven, where the twelve outermost rows on each side hold
    twelve different values apiece: every list of one, two or three of
    them is a leak, and each is asserted here rather than argued.
    """
    folder = tmp_path / f"listed-{side}-{named}"
    folder.mkdir()
    _name, cells = _heavy_tails()[0]
    table = fixtures.write(folder, "real.csv", _one_column("charges", cells))
    read = reading.read_table(f"{table}", small_cell_floor=11)
    document = profile.build_document(
        read, taxonomy.Settings(small_cell_floor=11), [], [], []
    )
    block = document["columns"][0]
    assert _value_leaks(block, cells, 11) == []
    values = _numeric_cells(cells)
    tails = block["tails"]
    assert isinstance(tails, dict) and isinstance(tails[side], dict)
    listed = (
        [values[place] for place in range(named)]
        if side == "low"
        else [values[len(values) - place] for place in range(named, 0, -1)]
    )
    assert len(set(listed)) == named, (
        "this mutation is about values ONE row holds, so the cells it "
        "names must be different from each other"
    )
    tails[side] = dict(tails[side])
    tails[side]["values"] = listed
    assert _value_leaks(block, cells, 11), (
        f"a tail listed {named} of the column's outermost values, each "
        f"held by one row, and the VALUE clause admitted them"
    )


def test_the_gate_turns_red_on_a_population_floor_lowered_below_a_hundred(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION 5: the population floor lowered, and the refusal stops happening.

    The refusal half rests on one number. Lowered to half of itself, a
    table of 99 rows is described rather than refused -- and a test that
    could not see that is a test of nothing.
    """
    folder = tmp_path / "lowered"
    folder.mkdir()
    table = _clinic(folder, parsing.POPULATION_FLOOR - 1)
    assert cli.main(["profile", f"{table}"]) == 1
    monkeypatch.setattr(parsing, "POPULATION_FLOOR", 50)
    assert kpi_shapes.quiet_cli(
        ["profile", f"{table}", "--out-dir", f"{folder}", "--replace"]
    ) == 0, (
        "the population floor was halved and the command still refused: the "
        "refusal does not rest on `parsing.POPULATION_FLOOR`, so lowering it "
        "could not be seen"
    )
    assert _left(folder) != ["clinic.csv"]


def _value_leaks(block: "dict", cells: "list[str]", floor: int) -> "list[str]":
    """Every published VALUE of one block that names a lone outer cell."""
    lone = _lone_outer(cells, block, floor)
    found: "list[str]" = []
    if not lone:
        return found
    for where, keys, number in _value_numbers(block):
        if number in lone:
            found += [f"{where}{list(keys)} = {number}"]
    return found


# -- 6. THE LIMIT THE OWNER ACCEPTED ON 2026-09-23 (plan P4-D348) ------
#
# THE DISCLOSURE FLOOR COUNTS ROWS, NOT PEOPLE. On a repeated-measures
# table a value held by twelve visits of ONE patient clears a floor of
# eleven and is published with its count. The owner accepted that on
# 2026-09-23 and it is not changed here; what it gets instead is a
# number, measured over the shapes it happens on and held at a ceiling
# so it cannot widen while nobody is looking (ledger `K-S3-14`).
#
# WHY IT IS NOT CLOSED HERE. Counting the floor in people would change
# what every column of every repeated-measures table publishes, which is
# a landing and not a clause. The population floor DOES count people
# already (`asking` and plan P4-D340), so the two halves of stage 3
# count different units on purpose, and this is the statement of that.


def repeated_measures_shapes() -> "list[tuple[str, str, str, int]]":
    """(name, table text, the declared identifier, rows per subject).

    Three tables, each with several rows per subject and a declared
    identifier. The middle one is the plan's own cited case (P4-D340,
    "a table of 12 subjects over 1,196 rows"), which is where a value
    held by one person most easily clears a floor counted in rows.
    """
    built: "list[tuple[str, str, str, int]]" = []
    built += [(
        "300 patients over 1,200 visits",
        kpi_shapes.visits_table(1200, 300),
        "subject_id",
        4,
    )]
    built += [(
        "12 patients over 1,196 visits",
        kpi_shapes.visits_table(1196, 12),
        "subject_id",
        99,
    )]
    draw = random.Random(23)
    rows: "list[list[str]]" = []
    for place in range(2000):
        who = place % 200
        rows += [[
            f"P{who + 1:05d}",
            f"{draw.gauss(70, 9) + who * 0.05:.1f}",
            fixtures.REGIONS[place % 4],
        ]]
    built += [(
        "200 patients over 2,000 measured visits",
        kpi_shapes.delimited_text(["subject_id", "reading", "site"], rows),
        "subject_id",
        10,
    )]
    return built

def values_held_by_too_few_people(
    document: "dict",
    cells: "dict[str, list[str]]",
    subjects: "list[str]",
    floor: int,
) -> "tuple[list[str], list[str]]":
    """(every published VALUE too few PEOPLE hold, the subset the ROWS clear).

    The unit is the distinct declared identifier, recomputed from the
    table this description was built from -- never read off a key,
    because no key of the description publishes it.

    THE SECOND LIST IS THE LIMIT ITSELF, and it is the first list less
    what the owner had already accepted. A rung of the ladder reads two
    neighbouring order statistics and names a value a handful of ROWS
    hold: the owner kept the ladder (decision 3), and the people behind
    those few rows are equally few, so such a rung stands in the first
    list while saying nothing about rows against people. What the
    ruling of 2026-09-23 is about is the value whose ROWS reach the
    floor and whose PEOPLE do not -- twelve visits of one patient --
    and that is the second list.
    """
    every: "list[str]" = []
    limit: "list[str]" = []
    for block in document["columns"]:
        held = cells[block["name"]] if block["name"] in cells else []
        if not held or len(held) != len(subjects):
            continue
        people: "dict[float, set[str]]" = {}
        rows: "collections.Counter" = collections.Counter()
        for place in range(len(held)):
            number = parsing.parse_number(held[place])
            if number is None:
                continue
            if number not in people:
                people[number] = set()
            people[number].add(subjects[place])
            rows[number] += 1
        for where, keys, number in _value_numbers(block):
            if number not in people or len(people[number]) >= floor:
                continue
            said = (
                f"{block['name']}: {where}{list(keys)} = {number}, held by "
                f"{len(people[number])} of the table's people and by "
                f"{rows[number]} of its rows"
            )
            every += [said]
            if rows[number] >= floor:
                limit += [said]
    return every, limit


def people_limit(home: pathlib.Path, floor: int = 11) -> "tuple[int, int, int]":
    """(values too few people hold, of those the rows clear, shapes measured)."""
    below = 0
    limited = 0
    shapes = repeated_measures_shapes()
    for name, text, identifier, _per in shapes:
        folder = home / name.replace(" ", "-").replace(",", "")
        folder.mkdir(parents=True, exist_ok=True)
        table = fixtures.write(folder, "real.csv", text)
        read = reading.read_table(f"{table}", small_cell_floor=floor)
        document = profile.build_document(
            read, taxonomy.Settings(small_cell_floor=floor), [identifier], [], []
        )
        rows = kpi_shapes.csv_rows(table)
        cells = {
            column: [row[place] for row in rows[1:] if len(row) > place]
            for place, column in enumerate(rows[0])
        }
        every, limit = values_held_by_too_few_people(
            document, cells, cells[identifier], floor
        )
        below = below + len(every)
        limited = limited + len(limit)
    return below, limited, len(shapes)


def test_the_floor_counts_rows_and_not_people_which_the_owner_accepted(
    tmp_path: pathlib.Path,
) -> None:
    """THE LIMIT, MEASURED HERE AND HELD AT A CEILING BY `K-S3-14`.

    Two things are asserted, and the second is why this test exists at
    all. The limit is REAL -- the repeated-measures shapes do publish
    values whose ROWS clear the floor and whose PEOPLE do not -- and the
    gate above does NOT fail on them, because the floor the product
    applies counts rows. A landing that closed the limit would make the
    first assertion fail, which is the right way for it to be noticed.
    """
    below, limited, shapes = people_limit(tmp_path)
    assert shapes == 3
    assert limited > 0, (
        "no published value of a repeated-measures shape has its rows at the "
        "floor and its people below it: the limit `K-S3-14` records has "
        "closed, so that entry and plan decision P4-D348 are out of date"
    )
    entry = kpi_rules.entries_by_id(kpi_rules.load_ledger())["K-S3-14"]
    assert below <= entry["expected"]["values_fewer_people_hold_than_the_floor"]
    assert limited <= entry["expected"]["and_whose_rows_reach_the_floor"]
