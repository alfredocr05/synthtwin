"""Five defects found by reading the three shipped pages by hand.

None of them crashed anything, none was caused by a recent change, and
no test in this suite covered any of them -- which is the point. The
suite checked BYTES and COUNTS: that the report's digest was what it was
last time, and that the census added up. It did not check whether a
sentence on the page is TRUE OF THE RUN THAT PRINTED IT, and every one
of these five is a sentence that was not.

WHAT WAS FOUND, on a real table at floor 11 and again at floor 1:

1. **The generation report asserted a false reason for pooled blanks.**
   A column with eight EMPTY cells printed, at the default floor:

       (withheld): 8 cell(s)
       counted absent because a spelling held back, because too few
       rows wrote it that way: 8

   `(withheld)` is synthtwin's own word for "not published here" -- the
   key both missing maps pool everything under the floor into. Printed
   where a spelling goes it names a spelling no table wrote, and
   rendered as a REASON it tells a researcher their blanks carried a
   marker they must account for, which was false of all eight cells. At
   floor 1 the same table printed `(blank): 8` and "counted absent
   because nothing was written there: 8", which is the truth. And the
   two lines are the SAME eight cells, drawn from two different maps and
   printed one under the other, so the block reads as sixteen.

2. **Three date rungs printed a window that excludes the description's
   own value.** `p90` said 2023-11-23, the twin held 2023-11-20, and the
   window ran 2023-11-19 to 2023-11-21 -- under a section saying
   "'Inside the range' means the twin did what this method promises" and
   never saying a window can miss the published value. The arithmetic
   was right: G12.4 bounds the twin's rung by the band its own RANK was
   built in, and the rank holding a named rung covers a slightly
   different share of the column from the share the rung's name names.
   The page contradicted itself, so the page is what was repaired.

3. **A label obligation asked for the bare number 1.**
   `levels.<label>.label: HELD -- the description asks for: 1`, with no
   found line under it, and the same for `.variants` and
   `.variants_withheld`. Withholding the found value is the disclosure
   rule and stays. The `1` was a placeholder standing where a count
   goes, on an obligation that is not a count.

4. **The not-checkable census printed registry identifiers** --
   `'seen_on' -- universal.missing_by_class` -- where every verdict line
   above it leads with a name, and where the `axes.structural_role`
   entries in the same list already carried one.

5. **The WITHHELD explanation was written in the present indicative
   about a report that has none.** With `0 WITHHELD` in the census it
   still read "Some obligations carry no verdict at all and the report
   says WITHHELD where the verdict would have stood ... the line itself
   says which", and there were no such lines to read.

WHERE THESE TESTS PUT THEIR WEIGHT. Each one is written, as far as it
can be, as a property of the run rather than as a search for a string:
the counts a block prints are summed and compared with the count the
description publishes; the flag that decides sentence 2 is recomputed
from the very numbers the page printed; every listing of every battery
run is required to name itself; and the WITHHELD paragraph is compared
with the census on both sides of zero. A string match would have passed
every one of these five defects, because every one of them was a
perfectly stable string.

A SIXTH was found on the same reading and belongs to the same family as
the fourth, so it is repaired and guarded here too: the twin's report
printed the stand-in decision as the producer's machine code -- "-999 in
13 row(s): read_as_missing, because outlier_and_frequent" -- because its
own words table was keyed on `missing` and `kept`, which the producer
has never published. Every lookup missed in silence.

THE RED CHECK. Nine `REINSTATE` values put one piece of the pre-repair
behaviour back, so no test here has an assumed red:

* `REINSTATE=page-pooled-name` -- the absent-cell block of the twin's
  report exactly as it stood: one flat list of both maps, with the
  pooled key printed as a spelling and the pooled class printed as a
  fifth reason;
* `REINSTATE=page-pooled-name-summary` -- the same for the profile's
  plain-language summary, which listed `(withheld)` among the spellings;
* `REINSTATE=page-range-silence` -- the twin's report saying nothing
  where a range misses the published value, and the quality report
  printing no note under a rung;
* `REINSTATE=page-range-flag` -- the flag that decides whether either
  page speaks, set to "the range covers it" on every date rung;
* `REINSTATE=page-raw-ordinals` -- the quality report's date rungs drawn
  by the generic envelope builder again, so all three numbers print as
  the ordinals the arithmetic runs in;
* `REINSTATE=page-label-number` -- the label obligations asking for
  a bare number again;
* `REINSTATE=page-listing-identifier` -- the not-checkable census naming
  a report-only obligation by its registry identifier alone;
* `REINSTATE=page-decision-code` -- the twin's report's words table
  keyed on codes the producer does not publish, and no reason table;
* `REINSTATE=page-withheld-mood` -- the WITHHELD paragraph in the
  present indicative, whatever the census says;
* `REINSTATE=P3-V10-F5` -- both envelope functions as they shipped, with
  every approximated verdict read off window membership alone. Reds the
  line that said a file holding the description's own value had missed
  the obligation to hold it.
"""

import dataclasses
import os
import pathlib
import typing

import pytest

import fixtures
import test_p3v10f5_exact_equality_wins as exact_equality_wins
from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    quality,
    reading,
    rendering,
    summary,
    taxonomy,
    validation,
)

# The generator's own datetime measurement, kept before any patch can
# reach it, so the flag-drift red below wraps the real one.
_THE_REAL_DATETIME_APPROXIMATIONS = generation._datetime_approximations

# The floor the defects were found at, and the floor the same table was
# read at to see what the truth had been. Both are run everywhere below:
# the first defect only APPEARS at a floor above the group it pools, and
# a repair that reads well at one floor and lies at the other is not a
# repair.
DEFAULT_FLOOR = 11
NAMING_FLOOR = 1

# How many cells of `amount` are left empty. Eight is under the default
# floor and over nothing, which is what makes the pooled case ordinary
# rather than a corner: every column with a handful of blanks meets it.
BLANK_CELLS = 8


# -- the table the defects were read on -------------------------------


def _table_text() -> str:
    """A neutral table with blanks, dates and labels, built here.

    Nothing is committed (plan D13). The shapes it has to carry are the
    ones the five defects live on: a numeric column with fewer blank
    cells than the default floor, two date columns long enough for the
    ladder's upper rungs to separate, labels well above the floor, and a
    free-text column.
    """
    header = ["site", "grade", "amount", "recorded_on", "note", "seen_on"]
    regions = ("north", "south", "east", "west")
    grades = ("alpha", "beta", "gamma")
    blanks = frozenset([3, 17, 40, 61, 88, 130, 175, 202])
    rows = []
    for index in range(240):
        amount = ""
        if index not in blanks:
            amount = f"{(index * 37) % 883 + 10}.{(index * 7) % 100:02d}"
        seen_on = ""
        if index % 37:
            seen_on = f"2023-{index % 12 + 1:02d}-{index % 27 + 1:02d}"
        rows = rows + [
            [
                regions[index % 4],
                grades[index % 3],
                amount,
                f"2024-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
                f"free text line number {index} with some words",
                seen_on,
            ]
        ]
    return fixtures.rows_to_csv(header, rows)


class Run(typing.NamedTuple):
    """One whole workflow: describe, build, check, at one floor.

    ``outcome`` is the twin measured against the description it was
    built from. ``against_source`` is the SAME description measured
    against the table it was written from, which is the first thing a
    researcher does and the run that carried review item P3-V10-F5: a
    date rung printed "the description asks for 2024-12-24 / the file
    was found to hold that same value" and MISSED under it.
    """

    floor: int
    described: contract.Profile
    document: "dict[str, object]"
    built: generation.Twin
    outcome: validation.Outcome
    against_source: validation.Outcome
    summary_text: str
    report: str
    quality_text: str


def _run(folder: pathlib.Path, floor: int) -> Run:
    """The three commands, on one table, at one publication floor."""
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(folder, "table.csv", _table_text())
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(small_cell_floor=floor),
        [],
    )
    written = fixtures.write_profile(folder, "table-profile.json", document)
    described = contract.load_profile(f"{written}")
    built = generation.generate(described, 0)
    twin = fixtures.write(folder, "twin.csv", rendering.twin_csv(built))
    outcome = validation.measure(described, f"{twin}")
    return Run(
        floor=floor,
        described=described,
        document=document,
        built=built,
        outcome=outcome,
        against_source=validation.measure(described, f"{table}"),
        summary_text=summary.render(document, "read as UTF-8."),
        report=rendering.report(described, built),
        quality_text=quality.quality_report(described, outcome),
    )


@pytest.fixture(scope="module")
def runs(tmp_path_factory: pytest.TempPathFactory) -> "dict[int, Run]":
    """The same table through the whole workflow at both floors."""
    folder = tmp_path_factory.mktemp("shipped-page")
    return {
        floor: _run(folder / f"floor-{floor}", floor)
        for floor in (DEFAULT_FLOOR, NAMING_FLOOR)
    }


# -- the pre-repair behaviour, for the red check ----------------------


def _the_absent_block_before_the_repair(
    column: contract.ColumnBlock, _floor: int
) -> "list[str]":
    """`rendering._missing_lines` exactly as it shipped.

    Both maps in one flat list, the pooled spelling printed as a
    spelling, and the pooled class printed as a fifth reason.
    """
    if not column.n_missing:
        return []
    lines = [
        "  The twin writes every one of them as an empty cell, so how your",
        "  table wrote them is here rather than in the twin:",
    ]
    for spelling in sorted(column.missing_by_source):
        count = column.missing_by_source[spelling]
        lines = lines + [f"    {spelling}: {count} cell(s)"]
    classes = column.missing_by_class
    reasons = [
        (classes.blank, "nothing was written there"),
        (classes.declared_missing, "a value you named with --missing-value"),
        (
            classes.numeric_sentinel,
            "a number this column used as a stand-in for 'no value'",
        ),
        (classes.text_code, "a code such as NA that reads as 'no value'"),
        (
            classes.withheld,
            "a spelling held back, because too few rows wrote it that way",
        ),
    ]
    for count, reason in reasons:
        if count:
            lines = lines + [f"    counted absent because {reason}: {count}"]
    return lines


def _the_spelling_words_before_the_repair(
    sources: "dict[str, object]", _floor: int
) -> "list[str]":
    """`summary._missing_spelling_words` as it shipped: the key, listed."""
    return [
        f"{spelling} ({sources[spelling]})" for spelling in sorted(sources)
    ]


def _the_label_spelling_before_the_repair(
    name: str,
    level: contract.LevelEntry,
    entry: "dict[str, object] | None",
    measured: "dict[str, dict[str, object]] | None",
) -> validation.Check:
    """`validation._level_spelling` as it shipped: asks for `1`."""
    fact = "label.label"
    subcheck = f"levels.{level.label}.label"
    if measured is None:
        return validation.Check(
            name, fact, subcheck, validation.WITHHELD, "1", "", "closed"
        )
    return validation.Check(
        name,
        fact,
        subcheck,
        validation.HELD if entry is not None else validation.MISSED,
        "1",
    )


def _the_variant_map_before_the_repair(
    name: str,
    level: contract.LevelEntry,
    entry: "dict[str, object] | None",
    measured: "dict[str, dict[str, object]] | None",
    field: str,
) -> validation.Check:
    """`validation._variant_map` as it shipped: asks for the entry count."""
    published = (
        level.variants if field == "variants" else level.variants_withheld
    )
    fact = f"label.{field}"
    subcheck = f"levels.{level.label}.{field}"
    shown = f"{len(published)}"
    if measured is None:
        return validation.Check(
            name, fact, subcheck, validation.WITHHELD, shown, "", "closed"
        )
    if entry is None:
        return validation.Check(
            name, fact, subcheck, validation.MISSED, shown
        )
    found = validation._map_at(entry, field)
    if found is None:
        return validation.Check(
            name, fact, subcheck, validation.WITHHELD, shown, "", "closed"
        )
    verdict = validation.HELD
    if found != published:
        verdict = validation.MISSED
    return validation.Check(name, fact, subcheck, verdict, shown)


def _a_flag_that_always_says_the_range_covers_it(
    column: contract.ColumnBlock,
    facts: contract.DatetimeFacts,
    written: "list[str]",
) -> "list[generation.Approximation]":
    """Every date rung claiming its window reaches the published value.

    The other way this defect can come back: not the page falling
    silent, but the flag that decides whether it speaks going wrong. A
    field nobody recomputes is a field that can drift into saying
    anything, so the test that recomputes it from the printed numbers
    gets its own red.
    """
    return [
        dataclasses.replace(found, covers_published=True)
        for found in _THE_REAL_DATETIME_APPROXIMATIONS(column, facts, written)
    ]


def _the_rung_check_before_the_repair(
    column: str,
    subcheck: str,
    facts: contract.DatetimeFacts,
    published: str,
    measured: "int | None",
    window: "tuple[int, int]",
) -> validation.Check:
    """`validation._date_ladder_checks` as it shipped: raw ordinals.

    The generic envelope builder, handed the ordinals the arithmetic
    runs in, so the line reads "2023-11-23 (between 1700352000.0 and
    1700524800.0)" and is "found to hold 1700438400.0".
    """
    low, high = window
    return validation._within(
        column,
        "datetime.date_percentiles",
        subcheck,
        published,
        None if measured is None else float(measured),
        (float(low), float(high)),
        validation.ENVELOPE_DATETIME_RUNGS,
    )


def _the_withheld_paragraph_before_the_repair(
    _withheld: int,
) -> "list[str]":
    """`quality._withheld_census_lines` as it shipped: no census at all.

    The two sentences it printed on every report, whatever the count --
    the opening moved above it and is now written as a rule, so what is
    reinstated here is the pair that spoke about lines the page carries.
    """
    return [
        "Some obligations carry no verdict at all and the report says",
        "WITHHELD where the verdict would have stood, and the line",
        "itself says which. A withheld count therefore stands on the",
        "verdict above rather than being quietly dropped: the obligation",
        "was set, and this report is not able to tell you whether this",
        "file met it.",
    ]


@pytest.fixture(scope="module", autouse=True)
def _reinstated() -> "typing.Iterator[None]":
    """Put one piece of the pre-repair page back when asked.

    MODULE-SCOPED, because the runs every test here reads are built in a
    module-scoped fixture: a function-scoped patch would be applied
    after the pages it was meant to change had already been rendered,
    and the red check would be a green run against a patch nobody used.
    """
    patch = pytest.MonkeyPatch()
    asked = os.environ.get("REINSTATE")
    if asked == "page-pooled-name":
        patch.setattr(
            rendering, "_missing_lines", _the_absent_block_before_the_repair
        )
    if asked == "page-pooled-name-summary":
        patch.setattr(
            summary,
            "_missing_spelling_words",
            _the_spelling_words_before_the_repair,
        )
    if asked == "page-raw-ordinals":
        patch.setattr(
            validation, "_within_instant", _the_rung_check_before_the_repair
        )
    if asked == "page-range-flag":
        patch.setattr(
            generation,
            "_datetime_approximations",
            _a_flag_that_always_says_the_range_covers_it,
        )
    if asked == "page-range-silence":
        patch.setattr(rendering, "_range_miss_lines", lambda _found: [])
        patch.setattr(quality, "_note_lines", lambda _check: [])
    if asked == "page-label-number":
        patch.setattr(
            validation, "_level_spelling", _the_label_spelling_before_the_repair
        )
        patch.setattr(
            validation, "_variant_map", _the_variant_map_before_the_repair
        )
    if asked == "page-listing-identifier":
        patch.setattr(quality, "_listing_name", lambda listing: listing.subcheck)
    if asked == "page-decision-code":
        patch.setattr(
            rendering, "_VERDICT_WORDS", {"missing": "x", "kept": "y"}
        )
        patch.setattr(rendering, "_REASON_WORDS", {})
    if asked == "page-withheld-mood":
        patch.setattr(
            quality,
            "_withheld_census_lines",
            _the_withheld_paragraph_before_the_repair,
        )
    if asked == "P3-V10-F5":
        exact_equality_wins.reinstate(patch)
    yield
    patch.undo()


# -- reading the page back --------------------------------------------


def _column_block(report: str, name: str) -> "list[str]":
    """One column's block of the report's LAST section, and no other.

    The section is found first, because the deviation list above it
    opens its entries with the same `'column' -- ` shape and a walk that
    took the first match read a different block entirely.
    """
    lines = report.split("\n")
    section = 0
    for place in range(len(lines)):
        if lines[place] == "COLUMN BY COLUMN: WHAT ONLY THE DESCRIPTION HOLDS":
            section = place
    inside = False
    found: list[str] = []
    for line in lines[section:]:
        if line.startswith(f"'{name}' -- "):
            inside = True
            continue
        if inside and line.startswith(("'", "=====")):
            break
        if inside:
            found = found + [line]
    return found


def _counts_in(lines: "list[str]") -> "list[int]":
    """Every whole number written in these lines, in order."""
    found: list[int] = []
    for line in lines:
        digits = ""
        for character in line + " ":
            if character.isdigit():
                digits = digits + character
                continue
            if digits:
                found = found + [int(digits)]
            digits = ""
    return found


def _absent_groups(block: "list[str]") -> "tuple[list[str], list[str]]":
    """The two groupings of the absent cells, split at their headings.

    A group runs from its heading to the first line indented no further
    than the heading itself, so what follows the block -- the date
    spelling paragraph, the stand-in decisions -- is not read into it.

    THE FIRST HEADING WAS RENAMED AT PLAN AMENDMENT A-P3-30 and this
    reader moved with it. It read "By the spelling your table used"
    while `missing_by_source` was the whole of that group; contract
    version 5 gave the blank count and the pooled count fields of their
    own, so on a column whose absent cells are all blank the heading
    stood over the line `11 cell(s) with nothing written in them` and
    told a researcher their empty cells wore a spelling. The heading now
    asks what the table WROTE in those cells. Nothing this test asserts
    changes: the property is still that each grouping accounts for the
    column's absent cells exactly once.
    """
    by_spelling: list[str] = []
    by_reason: list[str] = []
    where = ""
    for line in block:
        if line.strip() == "By what your table wrote in them:":
            where = "spelling"
            continue
        if line.strip() == "By the reason each was counted absent:":
            where = "reason"
            continue
        if not line.startswith("    "):
            where = ""
        if where == "spelling":
            by_spelling = by_spelling + [line]
        if where == "reason":
            by_reason = by_reason + [line]
    return by_spelling, by_reason


# -- 1. the pooled blanks ---------------------------------------------


def test_the_absent_cell_block_prints_one_set_of_cells_and_not_two(
    runs: "dict[int, Run]",
) -> None:
    """Each grouping accounts for the column's absent cells exactly once.

    The property, not the wording: `missing_by_source` and
    `missing_by_class` are two groupings of ONE set of cells, so the
    counts under each heading must sum to `n_missing` and the two sums
    must not be added together. Printed as one flat list -- which is
    what shipped -- the eight cells of `amount` appeared as sixteen with
    every individual number correct, which is exactly the kind of defect
    a byte digest and a census cannot see.
    """
    for floor in (DEFAULT_FLOOR, NAMING_FLOOR):
        run = runs[floor]
        for column in run.described.columns:
            if not column.n_missing:
                continue
            block = _column_block(run.report, column.name)
            by_spelling, by_reason = _absent_groups(block)
            assert by_spelling and by_reason, (
                f"floor {floor}, '{column.name}': the absent cells are "
                f"grouped two ways and the block names neither grouping, "
                f"so a reader adds the two together"
            )
            for heading, group in (
                ("spelling", by_spelling),
                ("reason", by_reason),
            ):
                counted = 0
                for number in _counts_in(group):
                    if number == floor:
                        # The floor is quoted in the pooled sentence as
                        # the reason, not as a count of cells.
                        continue
                    counted = counted + number
                assert counted == column.n_missing, (
                    f"floor {floor}, '{column.name}': the {heading} "
                    f"grouping accounts for {counted} cell(s) where the "
                    f"description publishes {column.n_missing}"
                )
            assert "not added together" in "\n".join(block), (
                f"floor {floor}, '{column.name}': nothing on the page "
                f"tells a reader the two groups count one set of cells"
            )


def test_no_page_prints_the_pooled_name_where_a_value_belongs(
    runs: "dict[int, Run]",
) -> None:
    """`(withheld)` is synthtwin's word, and never a fact about a table.

    It is the key both missing maps and the sentinel verdicts pool
    under, and all three of the pages a full run leaves behind printed
    it straight: as a spelling in the profile's summary and in the
    twin's report, and as the candidate of a stand-in decision. Every
    one of those reads as something the person's own table did.

    The check is on all three pages at both floors, because the pooled
    key exists only above the floor that pools it: a repair proved at
    floor 1 alone proves nothing at all.
    """
    for floor in (DEFAULT_FLOOR, NAMING_FLOOR):
        run = runs[floor]
        for label, page in (
            ("the profile summary", run.summary_text),
            ("the twin's report", run.report),
            ("the quality report", run.quality_text),
        ):
            assert parsing.MISSING_WITHHELD not in page, (
                f"floor {floor}: {label} prints {parsing.MISSING_WITHHELD} "
                f"where a value of the table belongs"
            )


def test_a_reason_the_report_names_is_a_reason_cells_of_that_column_had(
    runs: "dict[int, Run]",
) -> None:
    """The truth check on the sentence, not a search for its words.

    Every reason the absent-cell block NAMES has to be one of the four
    the profiler counts, carrying a positive count for that column in
    this description. Pooling is not a fifth reason: it is the report
    declining to give one, and it was rendered as "counted absent
    because a spelling held back, because too few rows wrote it that
    way" against eight cells that were empty.
    """
    real = {
        "nothing was written there": "blank",
        "a value you named with --missing-value": "declared_missing",
        (
            "a number this column used as a stand-in for 'no value'"
        ): "numeric_sentinel",
        "a code such as NA that reads as 'no value'": "text_code",
    }
    for floor in (DEFAULT_FLOOR, NAMING_FLOOR):
        run = runs[floor]
        for column in run.described.columns:
            if not column.n_missing:
                continue
            _spelling, by_reason = _absent_groups(
                _column_block(run.report, column.name)
            )
            page = "\n".join(by_reason)
            for sentence, field in real.items():
                if sentence not in page:
                    continue
                counted = getattr(column.missing_by_class, field)
                assert counted, (
                    f"floor {floor}, '{column.name}': the report says "
                    f"cells were counted absent because {sentence}, and "
                    f"this description counts none of them that way"
                )
            named = 0
            for sentence, field in real.items():
                if sentence in page:
                    named = named + getattr(column.missing_by_class, field)
            assert named + column.missing_by_class.withheld == (
                column.n_missing
            ), (
                f"floor {floor}, '{column.name}': the reasons the report "
                f"names cover {named} cell(s), the pooled group covers "
                f"{column.missing_by_class.withheld}, and the column has "
                f"{column.n_missing}"
            )


def test_the_blank_column_reads_as_blank_at_the_floor_that_pools_it(
    runs: "dict[int, Run]",
) -> None:
    """The defect exactly as it was met, on the column it was met on.

    Eight empty cells at floor 11. Non-vacuity first: the description
    really does pool them, so this is the shape the defect needs, and a
    later change that stops pooling them turns this red rather than
    quietly making the test prove nothing.
    """
    pooled = None
    for column in runs[DEFAULT_FLOOR].described.columns:
        if column.name == "amount":
            pooled = column
    assert pooled is not None and pooled.n_missing == BLANK_CELLS
    assert pooled.missing_by_class.withheld == BLANK_CELLS, (
        "this column is here because the default floor pools its blank "
        "cells; it no longer does, so the test proves nothing"
    )
    named = None
    for column in runs[NAMING_FLOOR].described.columns:
        if column.name == "amount":
            named = column
    assert named is not None and named.missing_by_class.blank == BLANK_CELLS
    block = "\n".join(_column_block(runs[DEFAULT_FLOOR].report, "amount"))
    assert "a spelling held back" not in block, (
        "the pooled class was rendered as a reason those cells were "
        "absent; every one of them was empty"
    )
    assert "not named here" in block


# -- 2. a range that does not reach the published value ---------------


def _as_a_number(text: str) -> "float | None":
    """One printed value as something comparable, or None.

    A rung of a date ladder and a count are not both numbers, so the
    date text goes through the reader that turns a canonical instant
    into a whole number and everything else is read as a number.
    """
    instant = parsing.instant_key(text, "")
    if instant is not None:
        return float(instant)
    quarter = validation._quarter_ordinal(text)
    if quarter is not None:
        return float(quarter)
    try:
        return float(text)
    except ValueError:
        return None


def test_every_range_agrees_with_the_two_values_printed_beside_it(
    runs: "dict[int, Run]",
) -> None:
    """The page's own claim, recomputed from the page's own numbers.

    `covers_published` decides whether the report says a range misses
    the description's value, and this recomputes it from the four texts
    the report actually prints. A flag that disagrees with the printed
    numbers is a page that contradicts itself in the other direction --
    silent where it should speak, or speaking where the range is fine.
    """
    for floor in (DEFAULT_FLOOR, NAMING_FLOOR):
        for found in runs[floor].built.approximations:
            published = _as_a_number(found.published)
            lowest = _as_a_number(found.lowest)
            highest = _as_a_number(found.highest)
            assert published is not None, (found.column, found.fact)
            assert lowest is not None and highest is not None
            covers = lowest <= published <= highest
            assert covers == found.covers_published, (
                f"floor {floor}, '{found.column}' {found.fact}: the "
                f"report prints {found.lowest} to {found.highest} around "
                f"{found.published} and claims covers_published="
                f"{found.covers_published}"
            )


def test_a_range_that_misses_the_published_value_says_so_where_it_happens(
    runs: "dict[int, Run]",
) -> None:
    """And a range that covers it says nothing, so the line means something.

    Non-vacuity is asserted first: this table has date rungs whose
    window sits wholly below the description's own value, which is what
    G12.4 does at the top of an ordinary ladder, and if it ever stops
    having them this test says so instead of passing empty.
    """
    for floor in (DEFAULT_FLOOR, NAMING_FLOOR):
        run = runs[floor]
        missing = [
            found
            for found in run.built.approximations
            if not found.covers_published
        ]
        assert missing, (
            f"floor {floor}: no approximated fact of this table has a "
            f"range that misses the published value, so this test can "
            f"no longer see the defect it exists for"
        )
        sentence = "this range does not cover the description's own value"
        assert run.report.count(sentence) == len(missing), (
            f"floor {floor}: {len(missing)} range(s) miss the published "
            f"value and the report says so {run.report.count(sentence)} "
            f"time(s)"
        )
        assert "THE RANGE IS NOT A MARGIN" in run.report


def _subcheck_of(fact: str) -> str:
    """The quality report's name for the fact the twin's report measured.

    Two vocabularies for one obligation: the generator names its
    approximated facts by the contract's own keys and the validator by
    the subcheck grain of V3.2. Written out rather than derived, because
    a derivation that quietly stopped matching would make the agreement
    check below pass by comparing nothing.
    """
    if fact.startswith("date_percentiles.p"):
        return f"date-ladder.{fact.split('.')[1]}"
    if fact.startswith("percentiles.p"):
        return f"ladder.{fact.split('.')[1]}"
    if fact in ("mean", "std", "skew"):
        return f"moments.{fact}"
    if fact in ("n_distinct", "n_distinct_folded"):
        return f"distinct.{fact}"
    if fact in ("length.mean", "length.p50", "words.mean"):
        return fact
    return ""


def test_the_quality_report_says_the_same_thing_about_the_same_windows(
    runs: "dict[int, Run]",
) -> None:
    """The second opinion may not be silent where the first one speaks.

    Both pages carry the same envelopes for the same facts, and the
    validator reaches them by its own arithmetic (V1.4). What is checked
    is that they AGREE about whether a window reaches the description's
    own value -- a disagreement is one of the two being wrong, and a
    reader holding both pages cannot tell which. It is checked over
    EVERY approximated fact the two pages share and not over the date
    rungs alone: the cardinality envelope of a column of dates
    ordinarily misses the published count too, and a repair that spoke
    on one page and not the other would have left the reader worse off
    than the silence it replaced.

    IT IS ASKED OF EVERY VERDICT THE ENVELOPE TOUCHED, and it used to be
    asked of WITHIN-BOUND alone (review item P3-V10-F5). A window that
    does not reach the published value is exactly the window that can
    produce a verdict which is NOT within-bound, so filtering to
    within-bound put the interesting half of the class outside what this
    test asserts -- and that is where the contradiction sat: a date rung
    reported MISSED with "that same value" printed beside it, on a
    window this test had already stopped looking at. Both pages are
    checked over BOTH runs now, the twin's and the source table's, since
    the source table is where such a window is reached exactly.
    """
    for floor in (DEFAULT_FLOOR, NAMING_FLOOR):
        run = runs[floor]
        wanted: dict[tuple[str, str], bool] = {}
        for found in run.built.approximations:
            subcheck = _subcheck_of(found.fact)
            if subcheck:
                wanted[(found.column, subcheck)] = found.covers_published
        seen = 0
        spoken = 0
        for outcome, printed in (
            (run.outcome, run.quality_text),
            (run.against_source, ""),
        ):
            for check in outcome.checks:
                if check.verdict not in (
                    validation.WITHIN_BOUND,
                    validation.HELD,
                    validation.MISSED,
                ):
                    continue
                key = (check.column, check.subcheck)
                if key not in wanted:
                    continue
                seen = seen + 1
                said = "\n".join(check.note)
                covers = "does NOT reach the" not in said
                assert covers == wanted[key], (
                    f"floor {floor}, '{check.column}' {check.subcheck} "
                    f"({check.verdict}): the twin's report and the quality "
                    f"report disagree about whether this window reaches "
                    f"the description's value"
                )
                if not covers:
                    spoken = spoken + 1
                # The page is the TWIN's page, so only the twin's own
                # checks are asked to appear on it.
                for line in check.note if printed else ():
                    assert line in printed, (
                        f"floor {floor}, '{check.column}' "
                        f"{check.subcheck}: the check carries this "
                        f"sentence and the page does not print it"
                    )
        assert seen, f"floor {floor}: the two pages share no window at all"
        assert spoken, (
            f"floor {floor}: no shared window misses the description's "
            f"value, so the agreement this test exists for is untested"
        )


def test_a_file_holding_the_published_value_is_never_reported_missing(
    runs: "dict[int, Run]",
) -> None:
    """Review item P3-V10-F5, as a property of every window there is.

    A window here is worked out from the description and the size of the
    column, not as a margin around the published value, so it can lie
    wholly to one side of that value -- and where it does, a file holding
    the published value EXACTLY falls outside it. Reading the verdict off
    the window alone then printed "the description asks for: 2024-12-24 /
    the file was found to hold: that same value" with MISSED above it, on
    the table the description was written from. Four rungs of that one
    table said it, and two cardinality counts said the same thing in
    numbers: "asks for 84 ... found 84.0: MISSED".

    So the property is asserted over both runs and every subcheck, not
    over the date ladder: a line whose two values are the same value may
    not carry MISSED, whatever its window says. The two values are
    compared as the page prints them, because that is what a reader
    compares.
    """
    for floor in (DEFAULT_FLOOR, NAMING_FLOOR):
        run = runs[floor]
        exact = 0
        for outcome in (run.outcome, run.against_source):
            for check in outcome.checks:
                if not check.achieved:
                    continue
                same = check.achieved == "that same value" or (
                    check.achieved == check.published
                )
                if not same:
                    continue
                exact = exact + 1
                assert check.verdict != validation.MISSED, (
                    f"floor {floor}, '{check.column}' {check.subcheck}: "
                    f"the page asks for {check.published!r}, says the file "
                    f"holds {check.achieved!r}, and calls it MISSED"
                )
        assert exact, (
            f"floor {floor}: no line of either page prints one value twice, "
            f"so this test can no longer see the defect it exists for"
        )


def test_no_page_prints_a_date_window_as_a_raw_ordinal(
    runs: "dict[int, Run]",
) -> None:
    """Ten figures of epoch seconds is not a message written for a person.

    The quality report used to print the measured rung and both ends of
    its window as the ordinals the arithmetic runs in -- "2023-11-23
    (between 1700352000.0 and 1700524800.0)" -- which no reader can
    compare with the date beside them, and which hid defect 2 entirely.
    """
    for floor in (DEFAULT_FLOOR, NAMING_FLOOR):
        run = runs[floor]
        for check in run.outcome.checks:
            if check.fact != "datetime.date_percentiles":
                continue
            for text in (check.published, check.achieved) + check.note:
                for number in _counts_in([text]):
                    assert number < 100000000, (
                        f"floor {floor}, '{check.column}' "
                        f"{check.subcheck}: this line prints {number}, "
                        f"which is an ordinal of the space the window is "
                        f"drawn in and not a value a reader can use"
                    )


# -- 3. an obligation that asks for a bare number ---------------------

# The silent checks whose "asks for" IS a bare number and reads as one,
# with the subcheck naming what the number counts. Every other silent
# check has to say what it asks for in words: a number alone, under a
# line with no found value beside it, is a number a reader cannot act
# on. New entries here need a reason written beside them.
BARE_NUMBER_IS_READABLE = (
    # "styles.exact.leading_zero: 0" -- the subcheck names the form and
    # the number counts cells written in it.
    "styles.exact.",
    "styles.at-least.",
)


def _is_a_bare_number(text: str) -> bool:
    """Whether the whole of ``text`` is one number and nothing else."""
    body = text.removeprefix("-")
    return bool(body) and body.replace(".", "", 1).isdigit()


def test_no_obligation_shown_without_a_found_value_asks_for_a_number_alone(
    runs: "dict[int, Run]",
) -> None:
    """A line with nothing under it has to say what it wants in words.

    The disclosure rule withholds the found value of a label
    obligation, so the "asks for" is the whole of what a reader gets --
    and it was `1`, three times per published label. This is the
    property over every check of both runs rather than a search for
    those three lines.
    """
    for floor in (DEFAULT_FLOOR, NAMING_FLOOR):
        for check in runs[floor].outcome.checks:
            if check.achieved or not check.published:
                continue
            if not _is_a_bare_number(check.published):
                continue
            allowed = False
            for prefix in BARE_NUMBER_IS_READABLE:
                if check.subcheck.startswith(prefix):
                    allowed = True
            assert allowed, (
                f"floor {floor}, '{check.column}' {check.subcheck} shows "
                f"no found value and asks for {check.published!r}, which "
                f"tells a reader nothing they can check"
            )


def test_the_label_obligations_say_what_they_ask_for(
    runs: "dict[int, Run]",
) -> None:
    """Non-vacuity, and the count that is a count of the right thing.

    `variants_withheld` is keyed on GROUP SIZES and its values are how
    many spellings wore each, so the number of entries is not the number
    of spellings -- printing it as one would have replaced an unreadable
    number with a wrong one.
    """
    seen = 0
    for column in runs[DEFAULT_FLOOR].described.columns:
        facts = column.facts
        if not isinstance(facts, contract.LabelFacts):
            continue
        for level in facts.levels:
            seen = seen + 1
            spellings = 0
            for key in level.variants_withheld:
                spellings = spellings + level.variants_withheld[key]
            for check in runs[DEFAULT_FLOOR].outcome.checks:
                if check.subcheck != f"levels.{level.label}.variants_withheld":
                    continue
                if check.column != column.name:
                    continue
                if spellings:
                    assert f"{spellings} spelling(s)" in check.published
                else:
                    assert "no spelling" in check.published
    assert seen, "this description publishes no label, so nothing is proved"


# -- 4. the not-checkable census ---------------------------------------


def test_every_not_checkable_line_names_its_obligation_in_words(
    runs: "dict[int, Run]",
) -> None:
    """Named or not stated, and the whole census is walked both ways.

    A listing carries a subcheck where the obligation has a finer grain
    and none where it is REPORT-ONLY, and the second kind printed the
    registry identifier alone. Every entry now has a name; a fact the
    words table does not know returns "", and this is what refuses it.
    """
    for floor in (DEFAULT_FLOOR, NAMING_FLOOR):
        run = runs[floor]
        assert run.outcome.listings
        for listing in run.outcome.listings:
            named = quality._listing_name(listing)
            assert named, (
                f"floor {floor}: the not-checkable census names "
                f"{listing.fact} by its registry identifier alone, under "
                f"a heading promising to say what could not be checked"
            )
            where = "the file as a whole"
            if listing.column:
                where = f"'{listing.column}'"
            assert f"  {where} -- {named} [{listing.fact}]" in (
                run.quality_text
            ), f"floor {floor}: {listing.fact} is not printed in that shape"


def test_the_shape_of_a_listing_line_is_the_shape_of_a_verdict_line(
    runs: "dict[int, Run]",
) -> None:
    """One report, one way of naming an obligation.

    Every verdict line reads `<name> [<registry fact>]`. The listing
    lines beside them read the same way now, so a reader comparing this
    census with an ordinary run's sees one obligation named one way --
    which is the whole reason `Listing.subcheck` exists.
    """
    for floor in (DEFAULT_FLOOR, NAMING_FLOOR):
        run = runs[floor]
        for check in run.outcome.checks:
            assert f"  {check.subcheck} [{check.fact}]: " in run.quality_text
        for listing in run.outcome.listings:
            assert f"[{listing.fact}]" in run.quality_text


# -- 5. the WITHHELD paragraph -----------------------------------------


def _withheld_lines(text: str) -> int:
    """How many verdict lines of the report read WITHHELD."""
    counted = 0
    for line in text.split("\n"):
        if line.endswith(f": {validation.WITHHELD}"):
            counted = counted + 1
    return counted


def test_the_withheld_paragraph_says_what_this_report_carries(
    runs: "dict[int, Run]",
) -> None:
    """Zero withheld, so no sentence may send a reader looking for one.

    The rule itself is printed on every report and should be: whether it
    bites is a fact about the description and the file. What may not be
    printed is a sentence about lines this page does not have.
    """
    for floor in (DEFAULT_FLOOR, NAMING_FLOOR):
        run = runs[floor]
        assert run.outcome.census.withheld == 0, (
            "this fixture is the zero side of the check; it no longer "
            "has zero withheld, so the test proves nothing"
        )
        assert _withheld_lines(run.quality_text) == 0
        assert "no line of this" in run.quality_text
        assert "reads WITHHELD" in run.quality_text
        for claim in (
            "Some obligations carry no verdict at all",
            "the line itself says which",
            "A withheld count therefore stands on the verdict above",
        ):
            assert claim not in run.quality_text, (
                f"floor {floor}: with 0 withheld the report still says "
                f"{claim!r}, which is about lines it does not carry"
            )


# -- 6. and the same habit, one page over -----------------------------


def test_both_pages_translate_a_stand_in_decision_out_of_its_code(
    tmp_path: pathlib.Path,
) -> None:
    """The sixth, found on the same reading and of the same family.

    The twin's report kept its own table of what a stand-in decision
    means, keyed on `missing` and `kept`, and the producer publishes
    `read_as_missing` and `kept_as_a_number` -- so every lookup missed
    silently and an ordinary report printed "-999 in 13 row(s):
    read_as_missing, because outlier_and_frequent". The reason codes had
    no table there at all. Both pages describe one decision and now
    describe it in the same words.
    """
    values = [f"{index % 90 + 1}" for index in range(200)]
    table = fixtures.write(
        tmp_path,
        "t.csv",
        fixtures.rows_to_csv(
            ["reading"], [[value] for value in values + ["-999"] * 40]
        ),
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(), []
    )
    described = contract.load_profile(
        f"{fixtures.write_profile(tmp_path, 't-profile.json', document)}"
    )
    column = described.columns[0]
    assert column.sentinel_verdicts, (
        "no stand-in was decided on this column, so nothing is proved"
    )
    report = rendering.report(described, generation.generate(described, 0))
    said = summary.render(document, "read as UTF-8.")
    for verdict in column.sentinel_verdicts:
        for code in (verdict.verdict, verdict.reason):
            assert code not in report, (
                f"the twin's report prints the code {code!r} where a "
                f"sentence for a person belongs"
            )
            assert code not in said
        assert rendering._VERDICT_WORDS[verdict.verdict] in report
        assert rendering._REASON_WORDS[verdict.reason] in report


def test_the_report_has_words_for_every_decision_the_producer_publishes(
) -> None:
    """A table keyed on a code nobody publishes fails silently.

    Which is exactly how the defect above survived: the lookup missed,
    the raw code went through, and nothing anywhere compared the two
    tables. Both are held to the producer's own constants, in both
    directions, so a new decision or a new reason cannot ship without
    words and a stale key cannot ship at all.
    """
    verdicts = {taxonomy.VERDICT_MISSING, taxonomy.VERDICT_KEPT}
    reasons = {
        taxonomy.REASON_OUTLIER_AND_FREQUENT,
        taxonomy.REASON_NOT_AN_OUTLIER,
        taxonomy.REASON_TOO_RARE,
        taxonomy.REASON_TOO_FEW_OTHERS,
        taxonomy.REASON_KEPT_BY_USER,
    }
    assert set(rendering._VERDICT_WORDS) == verdicts
    assert set(rendering._REASON_WORDS) == reasons
    assert set(summary._VERDICT_WORDS) == verdicts
    assert set(summary._REASON_WORDS) == reasons
    for code in verdicts:
        assert rendering._VERDICT_WORDS[code] == summary._VERDICT_WORDS[code]
    for code in reasons:
        assert rendering._REASON_WORDS[code] == summary._REASON_WORDS[code]


def test_the_withheld_paragraph_counts_the_lines_it_talks_about(
    tmp_path: pathlib.Path,
) -> None:
    """The other side of zero, so the sentence is not one branch deep.

    The checked file holds words where the description publishes
    numbers, so the type gate closes over every measurement describing
    THAT file would not publish. The paragraph then has lines to talk
    about, and the number it prints is the census's, which is the number
    of lines a reader can go and find.
    """
    header = ["amount", "visits", "recorded_on"]
    rows = [
        [
            f"{(index * 7) % 97}.50",
            f"{index % 9}",
            f"2024-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        ]
        for index in range(60)
    ]
    table = fixtures.write(tmp_path, "t.csv", fixtures.rows_to_csv(header, rows))
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(small_cell_floor=DEFAULT_FLOOR),
        [],
    )
    described = contract.load_profile(
        f"{fixtures.write_profile(tmp_path, 't-profile.json', document)}"
    )
    words = fixtures.write(
        tmp_path,
        "words.csv",
        fixtures.rows_to_csv(
            header, [["alpha", "beta", "gamma"] for _index in range(60)]
        ),
    )
    outcome = validation.measure(described, f"{words}")
    text = quality.quality_report(described, outcome)
    assert outcome.census.withheld > 0, (
        "the type gate no longer fires on this file, so this test can "
        "no longer see the other side of zero"
    )
    assert _withheld_lines(text) == outcome.census.withheld
    assert (
        f"On this file it closed over {outcome.census.withheld} "
        f"obligation(s)"
    ) in text
    assert "no line of this" not in text
