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

AND ROUND 4'S REPAIR WAS NOT THE CLASS EITHER (review round 5, item 1).
It stopped the unconditional deletion and left the two sides deciding
"is this cell a hole?" by DIFFERENT ARITHMETIC: the producer compares
the exact number a cell's digits denote, and this module compared the
binary64 value that number rounds to. One column of eleven
`-999.00000000000001` cells, six exact `-999` holes and forty-three
ordinary readings then had all seventeen erased -- the producer keeps
the eleven and publishes `n_present=54` -- and `styles.at-least.decimal`
and `styles.spill` were reported MISSED against the table's own profile.
That is the class Phase 1 closed as P1-R8-F2, reintroduced one module
over: `taxonomy` made this comparison exact, and this module wrote a
rounding one beside it instead of standing on it.

The arithmetic test below skipped its equality assertion on exactly that
witness, which is why the witness survived the round it was written for.
It does not skip now: where cells are dropped, each one has to BE a cell
the producer itself could read as an absence.

SO THIS FILE ASSERTS THE CLASS AND NOT THE WITNESS, in six parts:

* THE WITNESS ITSELF, end to end through the three commands' own code;
* EVERY PUBLISHED ROUTE by which a description names a spelling as data
  (V2.3's three, plus the file's own sentinel verdicts) keeps its cells,
  including the route the finding did not name: a stand-in the FILE's
  own description reads as an ordinary number because it is no outlier.
  That one is a false rejection the review never wrote down, and it was
  live on the same line;
* THE ROUND-5 WITNESS, on every numeric sentinel rather than the one it
  names, at the grain the two sides meet: which cells ARE a candidate;
* THE RULE IN ARITHMETIC, over every fixture and both directions: the
  cells left behind are never MORE than the file's own description
  counts as present -- which is the confidentiality half amendment
  A-P3-5 clause 2 exists for -- and never FEWER except by the residual
  `_cells_that_description_reads` states, with every dropped cell shown
  to be a cell the producer's own rules could read as an absence;
* THE HALF THAT MUST NOT MOVE: two files that description cannot tell
  apart still get the same census, on a column that also holds kept
  stand-ins;
* AND THE CLASS AS A SHAPE, not as a case: no function that decides
  which cells the file's own description reads may ask a rounding reader
  for a number, whatever it is called and whenever it is added.

Every table is built at test time by the seeded neutral builders in
`fixtures.py`; no data-format file enters the repository (plan D13).
"""

import ast
import inspect
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

# One row per numeric sentinel: the sentinel as a person writes it, and a
# decimal spelling that denotes a DIFFERENT number while rounding to the
# same binary64 value. This is the same battery Phase 1 closed P1-R8-F2
# with, restated here because the defect came back on the other side of
# the boundary and a sentinel added later must arrive with its own
# neighbour rather than inherit a repair nothing checks for it.
NEIGHBOURS = [
    ("-9999", "-9999.0000000000001"),
    ("-999", "-999.00000000000001"),
    ("9999", "9999.0000000000001"),
]

# The round-5 witness's own two spellings.
_NEAR = "-999.00000000000001"
_HOLE = "-999"


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


def _near_neighbour_values(sentinel: str, neighbour: str) -> "list[str]":
    """The round-5 witness: eleven near numbers, six holes, forty-three readings.

    Eleven is the publication floor, and it is the number the witness
    needs rather than a round one: the residual
    `_cells_that_description_reads` states is bounded by cells of an
    UNPUBLISHED candidate, so a column that loses a whole floor's worth
    of cells has lost cells no residual can account for.

    The six exact `-999` cells sit below that floor, so the description
    publishes no verdict naming the candidate at all and pools their
    spelling in `missing_by_source` -- which is exactly the branch that
    hands the gated side a trimmed cell list. The readings are written
    at their canonical spelling, so nothing but the near numbers can put
    a cell outside its value's permitted spellings.
    """
    values: list[str] = []
    for index in range(60):
        if index % 5 == 0 and index < 55:
            values = values + [neighbour]
        elif index % 10 == 3:
            values = values + [sentinel]
        else:
            values = values + [str(round(1.0 + index * 0.25, 2))]
    return values


def _near_neighbour_witness(
    folder: pathlib.Path, sentinel: str, neighbour: str
) -> "tuple[contract.Profile, str]":
    """The witness table for one sentinel, and its own description.

    No twin is built: a conforming twin of this description cannot hold
    these spellings at all -- the generator writes a value's shortest
    round-trip text -- and the file a person points this command at is
    the table itself (V1.2). That is the file the finding is about.
    """
    table = _two_column_table(_near_neighbour_values(sentinel, neighbour))
    return (_described(folder, table, f"near{sentinel}"), table)


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


# -- the round-5 witness: one identity, asked the same way twice -------


@pytest.mark.parametrize(("sentinel", "neighbour"), NEIGHBOURS)
def test_the_two_sides_ask_the_same_question_of_a_near_neighbour(
    sentinel: str, neighbour: str
) -> None:
    """The premise, at the grain the two sides meet: which cells ARE a candidate.

    The producer decides that by the exact number a cell's digits denote
    (`taxonomy.exact_of_spelling`, made exact for review item P1-R8-F2),
    and this module has to reach the same answer about the same cell or
    it is describing a different table from the one it is checking. The
    neighbour is a number the sentinel is not, sharing the sentinel's
    binary64 value, so a rounding comparison calls it the candidate and
    an exact one does not.
    """
    held = parsing.parse_number(sentinel)
    assert held in parsing.NUMERIC_SENTINELS
    assert held is not None
    assert parsing.classify_number(neighbour) == parsing.NUMBER
    # The two spellings really are one binary64 value and two numbers.
    assert parsing.parse_number(neighbour) == held
    assert taxonomy.exact_of_spelling(neighbour) != taxonomy.exact_of_number(
        held
    )
    assert taxonomy.exact_of_spelling(sentinel) == taxonomy.exact_of_number(
        held
    )
    # ...and the validator answers the producer's question, not a
    # rounding of it.
    assert validation._stand_in_of(
        taxonomy.exact_of_spelling(sentinel)
    ) == taxonomy.exact_of_number(held)
    assert validation._stand_in_of(taxonomy.exact_of_spelling(neighbour)) is None


def test_every_numeric_sentinel_has_a_neighbour_here() -> None:
    """A sentinel added later arrives with its own case.

    The defect was in machinery all three share on both sides, so
    inheriting a repair nothing checks is exactly how it comes back.
    """
    named = [parsing.parse_number(row[0]) for row in NEIGHBOURS]
    assert sorted(named) == sorted(parsing.NUMERIC_SENTINELS)


@pytest.mark.parametrize(("sentinel", "neighbour"), NEIGHBOURS)
def test_the_witness_reaches_the_branch_the_finding_is_about(
    tmp_path: pathlib.Path, sentinel: str, neighbour: str
) -> None:
    """Written first, because every assertion below is about this shape.

    The producer keeps the eleven near numbers as ordinary readings and
    removes the six exact holes, so it publishes `n_present=54`; the six
    sit below the publication floor, so no verdict names the candidate
    and the missing source is pooled -- which is the branch that hands
    the gated side a trimmed cell list at all. If any of that stops
    being true the fixture stops being the witness.
    """
    described, table = _near_neighbour_witness(tmp_path, sentinel, neighbour)
    column = _reading_column(described)
    assert column.n_present == 54
    assert column.n_missing == 6
    assert column.sentinel_verdicts == ()
    blocks, _columns = _blocks_of(described, table, tmp_path, "reach")
    block = blocks[1]
    assert block["n_sentinel_candidates_unpublished"] == 1
    assert not validation._split_is_published(block)
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    assert facts.numeric_styles.get(parsing.STYLE_DECIMAL, 0) == 54


@pytest.mark.parametrize(("sentinel", "neighbour"), NEIGHBOURS)
def test_the_witness_keeps_every_cell_its_own_description_counts(
    tmp_path: pathlib.Path, sentinel: str, neighbour: str
) -> None:
    """THE FINDING (review round 5, item 1), on all three sentinels.

    Eleven cells the producer describes as ordinary readings were
    deleted from the recount, and the two obligations settled against
    that recount were reported MISSED against the table's OWN profile:
    `styles.at-least.decimal`, whose published count is a floor the file
    has to reach, and `styles.spill`, which is that floor's remainder.

    Both are asserted, and so is the arithmetic underneath them: the
    cells left behind are exactly the cells that description counts as
    values, no fewer.
    """
    described, table = _near_neighbour_witness(tmp_path, sentinel, neighbour)
    outcome = _measure(tmp_path, described, table, f"near{sentinel}.csv")
    verdicts = {
        check.subcheck: check.verdict
        for check in outcome.checks
        if check.column == "reading"
    }
    for subcheck in (
        f"styles.at-least.{parsing.STYLE_DECIMAL}",
        "styles.spill",
    ):
        assert verdicts[subcheck] == validation.HELD, (
            f"{subcheck} is {verdicts[subcheck]} against the very profile "
            f"this table was described by: the recount lost the cells that "
            f"description counts as values"
        )
    blocks, columns = _blocks_of(described, table, tmp_path, f"near{sentinel}")
    block = blocks[1]
    read = validation._cells_that_description_reads(
        block, columns[1], validation.kept_spellings(described)
    )
    counted = len([cell for cell in read if parsing.trimmed(cell)])
    assert counted == block["n_present"]


@pytest.mark.parametrize(("sentinel", "neighbour"), NEIGHBOURS)
def test_deleting_those_cells_hid_a_real_violation_as_well(
    tmp_path: pathlib.Path, sentinel: str, neighbour: str
) -> None:
    """The other direction of the same defect, and it is not a smaller one.

    A deletion does not only cost a floor its cells; it takes the cells
    out of every clause measured from the written text. These eleven are
    in no permitted spelling of the number they hold -- the shortest text
    that reads back as it is far shorter -- so `styles.spelled` is a
    genuine MISS of this file, and it was reported HELD while the cells
    were being deleted. A check that cannot see the cells that break it
    is the vacuity V3.4 refuses by name.

    So this file is one its own description calls right in every clause
    but that one, and the report now says exactly that: the two the
    finding names HOLD, and the one the bytes really break MISSES.
    """
    described, table = _near_neighbour_witness(tmp_path, sentinel, neighbour)
    outcome = _measure(tmp_path, described, table, f"spelled{sentinel}.csv")
    missed = sorted(
        {
            f"{check.column}: {check.subcheck}"
            for check in outcome.checks
            if check.verdict == validation.MISSED
        }
    )
    assert missed == ["reading: styles.spelled"], (
        "the only obligation this file breaks is the spelling of its near "
        f"numbers, and the report says: {missed}"
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


def _stand_in_exacts() -> "list[tuple[int, tuple[str, ...], int]]":
    """The three stand-ins as the producer's own exact numbers.

    Computed here from `taxonomy` rather than read off the validator, so
    that this test is a second opinion on the validator's identity and
    not a restatement of it.
    """
    return [
        taxonomy.exact_of_number(value)
        for value in parsing.NUMERIC_SENTINELS
    ]


def _candidates_named_in(
    block: "dict[str, object]",
) -> "list[tuple[int, tuple[str, ...], int]]":
    """Every stand-in this description publishes a verdict for, exactly."""
    entries = block["sentinel_verdicts"]
    assert isinstance(entries, list)
    named: list[tuple[int, tuple[str, ...], int]] = []
    for entry in entries:
        assert isinstance(entry, dict)
        spelling = entry["candidate"]
        assert isinstance(spelling, str)
        exact = taxonomy.exact_of_spelling(spelling)
        assert exact is not None
        named = named + [exact]
    return named


@pytest.mark.parametrize(
    "stem",
    [
        "kept_by_you-twin",
        "kept_by_you-table",
        "not_an_outlier-twin",
        "not_an_outlier-table",
        "markers",
        "near-0",
        "near-1",
        "near-2",
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

    NEVER FEWER, AND THE EXCEPTION IS STATED RATHER THAN STEPPED AROUND
    (review round 5, item 1). The version this replaces asserted equality
    only where the description published a verdict for every stand-in the
    column holds, and SKIPPED it otherwise -- which is exactly the shape
    of the witness that survived the round: eleven cells of a near
    neighbour erased under a candidate whose verdict sits below the
    publication floor. A test that steps around the case it was written
    for is worse than none.

    So the exception is now measured instead of assumed, in two parts
    that hold on every column of every fixture:

    * EVERY DROPPED CELL IS ONE THE PRODUCER'S OWN RULES COULD READ AS AN
      ABSENCE -- a built-in missing spelling, or a cell whose EXACT
      number is one of the three stand-ins. A cell that is neither is a
      cell no reading of the description calls a hole, and deleting it is
      the defect itself;
    * AND HOW MANY MAY GO IS BOUNDED BY THE CELLS OF THE CANDIDATES THAT
      DESCRIPTION DOES NOT NAME. That is the residual
      `_cells_that_description_reads` states at its size, counted from
      the cells rather than trusted: a near neighbour is not a cell of
      the candidate, so erasing eleven of them exceeds this bound even
      where a candidate does go unnamed.
    """
    if stem[:5] == "near-":
        sentinel, neighbour = NEIGHBOURS[int(stem[5:])]
        described, text = _near_neighbour_witness(
            tmp_path, sentinel, neighbour
        )
    elif stem == "markers":
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
        # Which cells went, and whether each one is a cell the producer
        # itself could read as an absence.
        holes = validation._holes_by_the_description(block, cells, kept)
        stand_ins = _stand_in_exacts()
        for index, is_hole in enumerate(holes):
            if not is_hole:
                continue
            cell = cells[index]
            if parsing.is_missing_text(cell):
                continue
            assert taxonomy.exact_of_spelling(cell) in stand_ins, (
                f"{stem}, column {position}, row {index}: a cell the "
                f"file's own description reads as neither a missing "
                f"spelling nor one of the three stand-ins was deleted "
                f"from the recount, so the recount is not that "
                f"description's reading of this column"
            )
        # ...and the residual, at the size the rule states: only the
        # cells of a candidate that description does not name may go
        # beyond the holes it accounts for.
        unnamed = 0
        named = _candidates_named_in(block)
        for exact in stand_ins:
            if exact in named:
                continue
            for cell in cells:
                if taxonomy.exact_of_spelling(cell) == exact:
                    unnamed = unnamed + 1
        assert published - counted <= unnamed, (
            f"{stem}, column {position}: {published - counted} cell(s) the "
            f"file's own description counts as values were deleted from "
            f"the recount, and that description holds only {unnamed} "
            f"cell(s) of a stand-in it publishes no verdict for -- so "
            f"cells that are no stand-in at all were deleted"
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


# -- the class as a shape, so a new site cannot reopen it --------------


# The readers that answer "what number is this text?" by rounding it to
# binary64. The producer decides a cell's identity exactly and every one
# of these loses the distinction it decides by.
_ROUNDING_READERS = ["parse_number", "float", "int", "round"]

# The rule that decides which cells the file's own description reads.
# The walk below starts here and follows every call it makes.
_THE_HOLE_RULE = "_cells_that_description_reads"


def _functions_of(module: object) -> "dict[str, ast.FunctionDef]":
    """Every module-level function of one shipped module, by name."""
    tree = ast.parse(inspect.getsource(module))  # type: ignore[arg-type]
    found: dict[str, ast.FunctionDef] = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            found[node.name] = node
    return found


def _calls_in(node: ast.FunctionDef) -> "list[str]":
    """Every name this function calls, plain or through a module."""
    named: list[str] = []
    for inner in ast.walk(node):
        if not isinstance(inner, ast.Call):
            continue
        if isinstance(inner.func, ast.Name):
            named = named + [inner.func.id]
        elif isinstance(inner.func, ast.Attribute):
            named = named + [inner.func.attr]
    return named


def test_the_hole_rule_asks_no_rounding_reader() -> None:
    """No function that decides which cells are read may round a number.

    THE CLASS, NOT THE CASE. Two repairs of this finding have now been
    written, and both times the defect was one comparison in one
    function; the third time it would be a helper somebody adds beside
    them. So this walks the whole closure -- every function reachable by
    call from the rule that decides which cells the file's own
    description reads -- and asserts that not one of them asks a reader
    that answers in binary64. A new helper is inside the walk on the
    commit that adds it, without anybody remembering this file exists.

    The exact identity is `taxonomy`'s published rule, and the closure
    has to be standing on it rather than beside it, so that is asserted
    too: taking it away leaves the closure with no way to tell two
    numbers apart at all.
    """
    functions = _functions_of(validation)
    assert _THE_HOLE_RULE in functions, (
        "the rule this walk starts from was renamed, so the walk is "
        "asserting nothing"
    )
    reached: dict[str, int] = {_THE_HOLE_RULE: 1}
    frontier = [_THE_HOLE_RULE]
    exact_asked = 0
    while frontier:
        name = frontier[0]
        frontier = frontier[1:]
        called = _calls_in(functions[name])
        for reader in _ROUNDING_READERS:
            assert reader not in called, (
                f"`{name}` decides which cells the file's own description "
                f"reads and calls `{reader}`, which answers in binary64 -- "
                f"the producer decides the same question exactly, and two "
                f"spellings a person can tell apart round to one value "
                f"(review items P1-R8-F2 and P3-V4-F1)"
            )
        for call in called:
            if call == "exact_of_spelling" or call == "exact_of_number":
                exact_asked = exact_asked + 1
            if call in functions and call not in reached:
                reached[call] = 1
                frontier = frontier + [call]
    assert exact_asked, (
        "nothing in the closure asks `taxonomy` for an exact number, so "
        "it is deciding a cell's identity some other way"
    )
    # The walk has to have gone somewhere: a closure of one function
    # would pass every assertion above while the rounding sat one call
    # away.
    assert len(reached) > 3
