"""A cell the file's own description reads as DATA is never deleted.

REVIEW ITEM P3-V4-F1, and it is a regression the previous round wrote.
Amendment A-P3-5 clause 2 sends the gated side of a column whose own
description POOLS its missing sources a cell list with the disputed
spellings removed, so that two files the producer describes byte for
byte alike are recounted the same way. The implementation removed every
cell wearing a built-in missing spelling and every cell whose value is
one of the three built-in numeric stand-ins, UNCONDITIONALLY -- and the
producer reads neither kind as a hole where the description names it as
data.

WHAT THAT COST, MEASURED HERE. A researcher who keeps `-999` as a real
measurement runs `synthtwin profile --keep-value -999`; the description
publishes that candidate `kept_by_you`; `synthtwin generate` writes a
twin holding those cells; and validating THAT twin against THAT
description reported `styles.at-least.plain` and `styles.remainder`
MISSED and exited 3. The shipped generator's own output was rejected.
The note left beside the deletion called it "recount detail, in the safe
direction"; a smaller recount is a smaller count against a floor the
description publishes exactly, and `styles.at-least.plain` is a floor.

SO THIS FILE ASSERTS THE CLASS AND NOT THE WITNESS, in four parts:

* THE WITNESS ITSELF, end to end through the three commands' own code;
* EVERY PUBLISHED ROUTE by which a description names a spelling as data
  (V2.3's three, plus the file's own sentinel verdicts) keeps its cells,
  including the route the finding did not name: a stand-in the FILE's
  own description reads as an ordinary number because it is no outlier.
  That one is a false rejection the review never wrote down, and it was
  live on the same line;
* THE RULE IN ARITHMETIC, over every fixture and both directions: the
  cells left behind are never MORE than the file's own description
  counts as present -- which is the confidentiality half amendment
  A-P3-5 clause 2 exists for -- and never FEWER where that description
  publishes a verdict for every candidate it holds, which is the half
  this finding is;
* AND THE HALF THAT MUST NOT MOVE: two files that description cannot
  tell apart still get the same census, on a column that also holds
  kept stand-ins.

Every table is built at test time by the seeded neutral builders in
`fixtures.py`; no data-format file enters the repository (plan D13).
"""

import pathlib

import pytest

import fixtures
from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

SEED = 20260814

# A floor of eleven is the shipped default; the fixtures below lean on
# it rather than on a number written out here.
_FLOOR = taxonomy.Settings().small_cell_floor


def _described(
    folder: pathlib.Path,
    text: str,
    stem: str,
    settings: "taxonomy.Settings | None" = None,
) -> contract.Profile:
    """One table through the real producer and the strict loader."""
    table_path = fixtures.write(folder, f"{stem}.csv", text)
    table = reading.read_table(
        str(table_path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(
        table, settings if settings else taxonomy.Settings(), []
    )
    written = fixtures.write_profile(folder, f"{stem}-profile.json", document)
    return contract.load_profile(str(written))


def _two_column_table(readings: "list[str]") -> str:
    """The reading column beside a record number, so a cell may be blank.

    A one-column table cannot hold a blank line at all -- the reader
    refuses it rather than guess whether it is a record -- and a blank
    that stays below the publication floor is what sends a column down
    the branch this file is about.
    """
    return fixtures.rows_to_csv(
        ["record_code", "reading"],
        [
            [f"R{index:05d}", value]
            for index, value in enumerate(readings)
        ],
    )


def _kept_sentinel_values() -> "list[str]":
    """Eleven kept `-999` cells, forty-eight decimals and one hole.

    The decimals are written at the shortest text that reads back as the
    same number, which is the canonical spelling `styles.spelled` asks
    for, so the table is a file its own description calls right in every
    clause. A table written `1.00` where the value's canonical text is
    `1.0` misses that clause for a reason that has nothing to do with
    this finding, and a witness carrying an unrelated miss proves
    nothing about the one it is for.
    """
    values: list[str] = []
    for index in range(60):
        if index == 30:
            values = values + [""]
        elif index % 5 == 0:
            values = values + ["-999"]
        else:
            values = values + [str(1.0 + index * 0.25)]
    return values


def _ordinary_sentinel_values() -> "list[str]":
    """`-999` as an ordinary reading of a column that lives down there.

    Nothing is declared: the producer judges the candidate against the
    column's own spread, finds it is no outlier, and publishes it
    `kept_as_a_number`. The cells are data by the FILE's own description
    and the submitted one says nothing about them at all, so the kept
    set of V2.3 cannot rescue them -- only reading the verdict can.
    """
    values: list[str] = []
    for index in range(60):
        if index == 30:
            values = values + [""]
        elif index % 5 == 0:
            values = values + ["-999"]
        else:
            values = values + [str(round(-1100.0 + index * 3.5, 1))]
    return values


@pytest.fixture(scope="module")
def kept_by_you(
    tmp_path_factory: pytest.TempPathFactory,
) -> "tuple[contract.Profile, str, str]":
    """The finding's own description, the table it was written from, the twin."""
    folder = tmp_path_factory.mktemp("kept-by-you")
    table = _two_column_table(_kept_sentinel_values())
    described = _described(
        folder, table, "kept", taxonomy.Settings(kept_values=("-999",))
    )
    return (
        described,
        table,
        rendering.twin_csv(generation.generate(described, SEED)),
    )


@pytest.fixture(scope="module")
def not_an_outlier(
    tmp_path_factory: pytest.TempPathFactory,
) -> "tuple[contract.Profile, str, str]":
    """A stand-in kept because the column's own spread says it is data."""
    folder = tmp_path_factory.mktemp("not-an-outlier")
    table = _two_column_table(_ordinary_sentinel_values())
    described = _described(folder, table, "ordinary")
    return (
        described,
        table,
        rendering.twin_csv(generation.generate(described, SEED)),
    )


def _measure(
    folder: pathlib.Path, described: contract.Profile, text: str, name: str
) -> validation.Outcome:
    """Write a measured file and measure it against a description."""
    return validation.measure(
        described, str(fixtures.write(folder, name, text))
    )


def _reading_column(described: contract.Profile) -> contract.ColumnBlock:
    """The column of numbers these fixtures are about."""
    return described.columns[1]


def _verdict_of(published: str, verdicts: "tuple[object, ...]") -> str:
    """What the description says about one sentinel candidate."""
    for entry in verdicts:
        assert isinstance(entry, contract.SentinelVerdict)
        if entry.candidate == published:
            return entry.verdict
    return ""


def test_the_description_publishes_the_route_each_fixture_is_for(
    kept_by_you: "tuple[contract.Profile, str, str]",
    not_an_outlier: "tuple[contract.Profile, str, str]",
) -> None:
    """The fixtures reach the two routes their names claim.

    Written first because a fixture that quietly stopped publishing
    `kept_by_you` -- a floor change, a spread change -- would leave
    every assertion below true of a file with no kept stand-in in it,
    and this whole file would be measuring nothing.
    """
    declared, _table, _twin = kept_by_you
    column = _reading_column(declared)
    assert (
        _verdict_of("-999", column.sentinel_verdicts) == taxonomy.VERDICT_KEPT
    )
    for entry in column.sentinel_verdicts:
        if entry.candidate == "-999":
            assert entry.reason == taxonomy.REASON_KEPT_BY_USER
            assert entry.n_occurrences >= _FLOOR
    ordinary, _their_table, _also = not_an_outlier
    theirs = _reading_column(ordinary)
    assert (
        _verdict_of("-999", theirs.sentinel_verdicts) == taxonomy.VERDICT_KEPT
    )
    for entry in theirs.sentinel_verdicts:
        if entry.candidate == "-999":
            assert entry.reason != taxonomy.REASON_KEPT_BY_USER
    # ...and the submitted description does NOT name it as data, so the
    # kept set of V2.3 is empty of it and only the published verdict can
    # rescue those cells.
    assert "-999" not in validation.kept_spellings(ordinary)


@pytest.mark.parametrize("route", ["kept_by_you", "not_an_outlier"])
@pytest.mark.parametrize("measured", ["twin", "the-table-itself"])
def test_a_file_its_own_description_calls_right_misses_nothing(
    tmp_path: pathlib.Path,
    route: str,
    measured: str,
    kept_by_you: "tuple[contract.Profile, str, str]",
    not_an_outlier: "tuple[contract.Profile, str, str]",
) -> None:
    """V8.4's green direction on a column whose stand-ins are DATA.

    THE WITNESS, and the route the finding did not name beside it, each
    measured on both files a person can point this command at (V1.2):
    the twin `synthtwin generate` writes from the description, and the
    very table the description was written from. Every published fact is
    true of both, and both were reported MISSED.

    The second file matters on its own. The twin of a column whose
    stand-in sits INSIDE its own spread holds no cell reading `-999` at
    all -- the ladder never lands there -- so the deletion cannot bite on
    it, and that route would look closed while a person validating their
    own table watched eleven real readings vanish.
    """
    described, table, twin = (
        kept_by_you if route == "kept_by_you" else not_an_outlier
    )
    text = twin if measured == "twin" else table
    outcome = _measure(tmp_path, described, text, f"{route}-{measured}.csv")
    missed = sorted(
        {
            f"{check.column}: {check.subcheck}"
            for check in outcome.checks
            if check.verdict == validation.MISSED
        }
    )
    assert not missed, (
        "every fact this description publishes is true of this file, and "
        f"validating it reports these obligations MISSED: {missed}"
    )
    assert outcome.census.missed == 0


@pytest.mark.parametrize("route", ["kept_by_you", "not_an_outlier"])
@pytest.mark.parametrize("measured", ["twin", "the-table-itself"])
def test_the_style_recount_still_counts_the_kept_cells(
    tmp_path: pathlib.Path,
    route: str,
    measured: str,
    kept_by_you: "tuple[contract.Profile, str, str]",
    not_an_outlier: "tuple[contract.Profile, str, str]",
) -> None:
    """And it is the STYLE clauses that see them, at the published count.

    The census above says no obligation missed; this says the reason is
    that the cells were counted, not that the clause went quiet. The
    plain form is the one those cells wear, and its published count is a
    FLOOR the file has to reach.
    """
    described, table, twin = (
        kept_by_you if route == "kept_by_you" else not_an_outlier
    )
    text = twin if measured == "twin" else table
    outcome = _measure(
        tmp_path, described, text, f"{route}-{measured}-styles.csv"
    )
    facts = _reading_column(described).facts
    assert isinstance(facts, contract.NumericFacts)
    assert facts.numeric_styles.get(parsing.STYLE_PLAIN, 0) >= _FLOOR, (
        "the fixture stopped publishing a plain count, so the floor this "
        "asserts is not the floor the finding broke"
    )
    verdicts = {
        check.subcheck: check.verdict
        for check in outcome.checks
        if check.column == "reading"
    }
    for subcheck in (
        f"styles.at-least.{parsing.STYLE_PLAIN}",
        "styles.remainder",
        "styles.spelled",
    ):
        assert verdicts[subcheck] == validation.HELD, (
            f"{subcheck} is {verdicts[subcheck]} on a file every fact of "
            f"this description is true of"
        )


def _blocks_of(
    described: contract.Profile, text: str, folder: pathlib.Path, stem: str
) -> "tuple[dict[str, object], list[list[str]]]":
    """The file's own description of each column, and its cells."""
    path = fixtures.write(folder, f"{stem}.csv", text)
    table = reading.read_table(str(path), first_row=reading.FIRST_ROW_NAMES)
    document = profile.build_document(
        table, validation.settings_for(described), []
    )
    blocks = document["columns"]
    assert isinstance(blocks, list)
    return blocks, table.columns


@pytest.mark.parametrize(
    "stem",
    [
        "kept_by_you-twin",
        "kept_by_you-table",
        "not_an_outlier-twin",
        "not_an_outlier-table",
        "markers",
    ],
)
def test_the_cells_left_behind_are_the_cells_that_description_counts(
    tmp_path: pathlib.Path,
    stem: str,
    kept_by_you: "tuple[contract.Profile, str, str]",
    not_an_outlier: "tuple[contract.Profile, str, str]",
) -> None:
    """The rule in arithmetic, in both directions, per column.

    NEVER MORE than the file's own description counts as present: a cell
    that description reads as a hole is a cell whose spelling it pools,
    so leaving it in the recount is what let two indistinguishable files
    be told apart (amendment A-P3-5 clause 2). That direction is
    asserted on every column of every fixture, unconditionally.

    NEVER FEWER where that description publishes a verdict for every
    stand-in the column holds: there the reading is EXACT, and a cell it
    counts as a value is a cell the recount has to see. Where a stand-in
    sits below the publication floor its verdict is published by no
    entry at all, and the drop is settled from the count of holes
    instead -- bounded, and named in `_cells_that_description_reads`
    rather than left to be found.
    """
    if stem == "markers":
        # The other side of the same coin: cells that ARE holes to the
        # file's own description, which must be dropped.
        described, _table, _twin = kept_by_you
        values = _kept_sentinel_values()
        values[7] = "n/a"
        values[9] = "NULL"
        text = _two_column_table(values)
    else:
        route, which = stem.rsplit("-", 1)
        described, table, twin = (
            kept_by_you if route == "kept_by_you" else not_an_outlier
        )
        text = twin if which == "twin" else table
    blocks, columns = _blocks_of(described, text, tmp_path, stem)
    kept = validation.kept_spellings(described)
    for position, block in enumerate(blocks):
        assert isinstance(block, dict)
        cells = columns[position]
        read = validation._cells_that_description_reads(block, cells, kept)
        counted = len([cell for cell in read if parsing.trimmed(cell)])
        published = block["n_present"]
        assert isinstance(published, int)
        assert counted <= published, (
            f"{stem}, column {position}: the recount keeps {counted} "
            f"non-blank cells where the file's own description counts "
            f"{published} as values, so it is recounting cells that "
            f"description does not publish"
        )
        unpublished = block["n_sentinel_candidates_unpublished"]
        if unpublished == 0:
            assert counted == published, (
                f"{stem}, column {position}: the description publishes a "
                f"verdict for every stand-in this column holds, so the "
                f"reading is exact -- and {published - counted} cell(s) it "
                f"counts as values were deleted from the recount"
            )


def test_two_files_the_producer_describes_alike_still_agree(
    tmp_path: pathlib.Path,
    kept_by_you: "tuple[contract.Profile, str, str]",
) -> None:
    """The half that must not move (amendment A-P3-5 clause 2).

    The confidentiality property the deletion exists for, asserted on a
    column that ALSO holds kept stand-ins -- which is the shape the
    repair could have broken by keeping everything. One pooled hole is
    written empty in one file and `n/a` in the other; the producer
    describes the two byte for byte alike, so the two reports must be
    the same report.
    """
    described, _table, twin = kept_by_you
    rows = twin.splitlines()
    hole = 0
    for index in range(1, len(rows)):
        cell = rows[index].split(",")[1]
        if not cell:
            hole = index
    assert hole, "the twin holds no blank cell, so there is nothing to spell"
    marked = list(rows)
    marked[hole] = f"{rows[hole]}n/a"
    blank = _measure(tmp_path, described, "\n".join(rows) + "\n", "blank.csv")
    spelled = _measure(
        tmp_path, described, "\n".join(marked) + "\n", "spelled.csv"
    )
    assert blank.census == spelled.census, (
        "two files `synthtwin profile` describes identically got "
        f"different censuses: {blank.census} against {spelled.census}"
    )
    mine = [(check.subcheck, check.verdict) for check in blank.checks]
    theirs = [(check.subcheck, check.verdict) for check in spelled.checks]
    assert mine == theirs
