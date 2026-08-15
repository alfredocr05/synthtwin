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

AND ROUND 6 FOUND THE CLASS WIDER THAN EITHER OF THEM. The settings the
validator re-describes under are a RECONSTRUCTION of what the person
declared, and it was incomplete on BOTH declaration tuples. The other
one had no route at all: `--missing-value` spellings were not recovered
anywhere, although a column publishes the exact spelling of every hole
whose count reaches the floor. A table profiled `--missing-value XX` and
validated against its own profile reported SEVEN obligations MISSED --
the column re-read as free text -- and `--missing-value -777` reported
SEVENTEEN. That is closed here, by the fourth published route. What is
NOT closed is a `--keep-value` spelling that is one of the built-in
missing texts on a column publishing no level that carries it: no field
of the document holds it, and the two files that decide the question are
described byte for byte alike (plan amendment A-P3-15 clause 3). That
one is MEASURED here at its size instead of claimed closed.

SO THIS FILE ASSERTS THE CLASS AND NOT THE WITNESS, in nine parts:

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
* THE OTHER DECLARATION, closed: a table whose holes are spelled by the
  person's own `--missing-value`, as text and as a number, misses
  nothing against its own profile -- and the recovery names a
  declaration and never a hole the producer's own rules make, which is
  asserted on a column of built-in markers, a column of blanks and a
  column of stand-ins;
* THE TWO PRESENCE COUNTS, taken off the same split description every
  other presence-dependent obligation is read off, so one report cannot
  answer one question twice;
* WHAT IS OPEN, MEASURED RATHER THAN DESCRIBED: the sub-floor
  declaration and the unrecoverable kept marker, each pinned to the
  exact list of subchecks it costs, with the marker's unrecoverability
  proved against every string the document carries and the reason it
  does not close in this module shown as arithmetic on two files;
* AND THE CLASS AS A SHAPE, not as a case: no function that decides
  which cells the file's own description reads may ask a rounding reader
  for a number, whatever it is called and whenever it is added -- with
  the six routes past that guard put through it, five of which the
  version this replaces called clean.

Every table is built at test time by the seeded neutral builders in
`fixtures.py`; no data-format file enters the repository (plan D13).
"""

import ast
import inspect
import pathlib
import types

import pytest

import fixtures
import synthtwin as synthtwin_package
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
        block,
        columns[1],
        validation.kept_spellings(described),
        validation.declared_spellings(described),
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
    declared = validation.declared_spellings(described)
    for position, block in enumerate(blocks):
        assert isinstance(block, dict)
        cells = columns[position]
        read = validation._cells_that_description_reads(
            block, cells, kept, declared
        )
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
        holes = validation._holes_by_the_description(
            block, cells, kept, declared
        )
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


# -- the OTHER declaration, and the one that cannot be recovered -------


# A marker no rule of the producer's own reads as a hole, so the only
# way a description can carry it as one is the person's `--missing-value`
# -- and a number that is no stand-in, for the same reason.
_DECLARED_TEXT = "XX"
_DECLARED_NUMBER = "-777"


def _declared_values(marker: str, every: int, rows: int) -> "list[str]":
    """One column of readings with ``marker`` written every so often."""
    return [
        marker if index % every == 0 else str(round(1.0 + index * 0.25, 2))
        for index in range(rows)
    ]


def _declared_witness(
    folder: pathlib.Path, marker: str, every: int, stem: str
) -> "tuple[contract.Profile, str, str]":
    """A `--missing-value` description, its own table, and its twin."""
    table = _two_column_table(_declared_values(marker, every, 211))
    described = _described(
        folder,
        table,
        stem,
        taxonomy.Settings(declared_missing_values=(marker,)),
    )
    return (
        described,
        table,
        rendering.twin_csv(generation.generate(described, SEED)),
    )


@pytest.fixture(scope="module")
def declared_text(
    tmp_path_factory: pytest.TempPathFactory,
) -> "tuple[contract.Profile, str, str]":
    """Twelve `XX` holes -- above the floor, so the spelling is published."""
    folder = tmp_path_factory.mktemp("declared-text")
    return _declared_witness(folder, _DECLARED_TEXT, 18, "declared-text")


@pytest.fixture(scope="module")
def declared_number(
    tmp_path_factory: pytest.TempPathFactory,
) -> "tuple[contract.Profile, str, str]":
    """The same, declared as a NUMBER that is no built-in stand-in."""
    folder = tmp_path_factory.mktemp("declared-number")
    return _declared_witness(folder, _DECLARED_NUMBER, 18, "declared-number")


@pytest.fixture(scope="module")
def declared_below_the_floor(
    tmp_path_factory: pytest.TempPathFactory,
) -> "tuple[contract.Profile, str, str]":
    """Four `XX` holes -- under the floor, so the spelling is pooled away."""
    folder = tmp_path_factory.mktemp("declared-pooled")
    return _declared_witness(folder, _DECLARED_TEXT, 60, "declared-pooled")


def test_each_declared_fixture_reaches_the_publication_it_is_for(
    declared_text: "tuple[contract.Profile, str, str]",
    declared_number: "tuple[contract.Profile, str, str]",
    declared_below_the_floor: "tuple[contract.Profile, str, str]",
) -> None:
    """The three fixtures sit where their names claim, above and below.

    Written first for the reason the kept fixtures have the same test:
    a floor change would leave every assertion below true of a file with
    no declaration in it.
    """
    for described, marker in (
        (declared_text[0], _DECLARED_TEXT),
        (declared_number[0], _DECLARED_NUMBER),
    ):
        column = _reading_column(described)
        assert column.missing_by_source.get(marker, 0) >= _FLOOR
        assert column.role == taxonomy.ROLE_CONTINUOUS
    pooled = _reading_column(declared_below_the_floor[0])
    assert pooled.missing_by_source == {parsing.MISSING_WITHHELD: 4}
    assert 0 < pooled.n_missing < _FLOOR


@pytest.mark.parametrize("route", ["text", "number"])
def test_the_fourth_published_route_is_recovered(
    route: str,
    declared_text: "tuple[contract.Profile, str, str]",
    declared_number: "tuple[contract.Profile, str, str]",
) -> None:
    """V2.3's three routes had a fourth, and it was not taken.

    `missing_by_source` publishes the exact spelling of every hole whose
    count reaches the floor, so a `--missing-value` declaration IS in the
    description -- the settings block records it as a count, and the
    COLUMN records the spelling. Recovering it is the same act as
    recovering a level's variants.
    """
    described = (declared_text if route == "text" else declared_number)[0]
    marker = _DECLARED_TEXT if route == "text" else _DECLARED_NUMBER
    assert validation.declared_spellings(described) == (marker,)
    assert validation.settings_for(described).declared_missing_values == (
        marker,
    )


@pytest.mark.parametrize("route", ["text", "number"])
@pytest.mark.parametrize("measured", ["twin", "the-table-itself"])
def test_a_declared_file_its_description_calls_right_misses_nothing(
    tmp_path: pathlib.Path,
    route: str,
    measured: str,
    declared_text: "tuple[contract.Profile, str, str]",
    declared_number: "tuple[contract.Profile, str, str]",
) -> None:
    """The direction the finding did not name, on both files (V1.2).

    A researcher runs `synthtwin profile --missing-value XX`, then
    validates the table it was written from. Every published fact is true
    of that file, and the report said otherwise: twelve `XX` cells read
    back as data, the column re-read as free text, and
    `presence.n_present`, `presence.n_missing`, `axes.role`,
    `axes.statistical_type`, `counts.n_not_numeric` and both distinctness
    counts came back MISSED -- SEVEN, against the table's own profile.
    Declared as the number `-777` instead, the same table missed
    SEVENTEEN: the ladder, the moments and the styles with them, because
    twelve readings of `-777` sat in the recount the description was
    written without.
    """
    described, table, twin = (
        declared_text if route == "text" else declared_number
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


def test_the_recovery_names_a_declaration_and_nothing_else(
    tmp_path: pathlib.Path,
    kept_by_you: "tuple[contract.Profile, str, str]",
) -> None:
    """A hole the producer's OWN rules make is never called a declaration.

    The route derives which keys are a declaration rather than guessing,
    and the derivation is only sound if the other three ways a cell
    becomes a hole are excluded by name. So each of them is built here
    and asked for: a column of built-in markers, a column of blanks, and
    a column whose stand-in the sentinel rule turned down. Recovering any
    of those would put a spelling in the settings the person never
    declared, and the file would then be described under rules its
    description was not written under -- the same defect, mirrored.
    """
    markers = _two_column_table(
        [
            "n/a" if index % 4 == 0 else str(round(1.0 + index * 0.25, 2))
            for index in range(120)
        ]
    )
    blanks = _two_column_table(
        [
            "" if index % 4 == 0 else str(round(1.0 + index * 0.25, 2))
            for index in range(120)
        ]
    )
    stand_ins = _two_column_table(
        [
            "-999" if index % 4 == 0 else str(round(1.0 + index * 0.25, 2))
            for index in range(120)
        ]
    )
    for stem, text in (
        ("markers", markers),
        ("blanks", blanks),
        ("stand-ins", stand_ins),
    ):
        described = _described(tmp_path, text, f"no-declaration-{stem}")
        column = _reading_column(described)
        assert column.n_missing >= _FLOOR, (
            f"{stem}: the holes did not reach the floor, so the source "
            f"map publishes nothing and this case proves nothing"
        )
        assert validation.declared_spellings(described) == (), (
            f"{stem}: the description publishes "
            f"{column.missing_by_source} and the recovery read one of "
            f"those as a declaration the person never made"
        )
    # ...and the same on the kept fixture, whose stand-in the person DID
    # declare -- as data. A declaration is recovered by what it does to
    # the description, not by the fact that one was made.
    described, _table, _twin = kept_by_you
    assert validation.declared_spellings(described) == ()


@pytest.mark.parametrize("route", ["text", "number"])
def test_the_two_presence_counts_come_off_the_split_description(
    tmp_path: pathlib.Path,
    route: str,
    declared_text: "tuple[contract.Profile, str, str]",
    declared_number: "tuple[contract.Profile, str, str]",
) -> None:
    """One question, one measurement (plan amendment A-P3-15 clause 3).

    V2.4 reads every presence-dependent obligation off the split
    description. These two were recounted beside it, and while both
    declaration tuples were empty the two answers were the same number.
    They are not once a declaration is recovered, and a report holding
    both is a report that disagrees with itself: `presence.n_present`
    said 211 while `distinct.n_distinct`, taken over the very cells that
    count claims are present, said 199.

    So the two counts are asserted against the split DESCRIPTION here,
    not against a number written out in this file.
    """
    described, table, _twin = (
        declared_text if route == "text" else declared_number
    )
    blocks, _columns = _blocks_of(described, table, tmp_path, f"split-{route}")
    split = blocks[1]
    assert isinstance(split, dict)
    outcome = _measure(tmp_path, described, table, f"presence-{route}.csv")
    found = {
        check.subcheck: check.achieved
        for check in outcome.checks
        if check.column == "reading"
    }
    assert found["presence.n_present"] == str(split["n_present"])
    assert found["presence.n_missing"] == str(split["n_missing"])
    # And the split description is not the raw blank count here, which is
    # what makes the assertion above say something.
    assert split["n_present"] != len(
        [cell for cell in _columns_of(described, table, tmp_path, route) if cell]
    )


def _columns_of(
    described: contract.Profile,
    text: str,
    folder: pathlib.Path,
    stem: str,
) -> "list[str]":
    """The reading column's written cells, trimmed."""
    path = fixtures.write(folder, f"cells-{stem}.csv", text)
    table = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    return [parsing.trimmed(cell) for cell in table.columns[1]]


def test_the_declaration_below_the_floor_is_left_open_at_its_size(
    tmp_path: pathlib.Path,
    declared_below_the_floor: "tuple[contract.Profile, str, str]",
) -> None:
    """WHAT IS NOT CLOSED, measured rather than described.

    A declaration whose cells sit below `small_cell_floor` in every
    column is pooled into `(withheld)` and published nowhere, so no
    route can recover it and the table it was written from still misses.
    The residual is bounded -- fewer than the floor per spelling per
    column -- and it is asserted at that bound here, so a repair that
    widens it turns this red instead of passing quietly.

    The twin is the other half: it writes its holes empty, so the twin of
    this very description misses nothing at all, and what is open is
    open only for the table.
    """
    described, table, twin = declared_below_the_floor
    column = _reading_column(described)
    assert column.n_missing < _FLOOR
    open_run = _measure(tmp_path, described, table, "pooled-table.csv")
    missed = sorted(
        {
            check.subcheck
            for check in open_run.checks
            if check.verdict == validation.MISSED
        }
    )
    assert missed == [
        "axes.role",
        "axes.statistical_type",
        "counts.n_not_numeric",
        "distinct.n_distinct",
        "distinct.n_distinct_folded",
        "presence.n_missing",
        "presence.n_present",
    ], (
        "the sub-floor residual changed size; it is stated in "
        "`declared_spellings` and in plan amendment A-P3-15 and both "
        "have to move with it"
    )
    closed_run = _measure(tmp_path, described, twin, "pooled-twin.csv")
    assert closed_run.census.missed == 0


# -- the kept marker no field publishes: open, and proved unrecoverable


_KEPT_MARKER = "n/a"


@pytest.fixture(scope="module")
def kept_marker(
    tmp_path_factory: pytest.TempPathFactory,
) -> "tuple[contract.Profile, str, taxonomy.Settings]":
    """The review's own witness: `--keep-value n/a` on a column of numbers."""
    folder = tmp_path_factory.mktemp("kept-marker")
    settings = taxonomy.Settings(kept_values=(_KEPT_MARKER,))
    table = _two_column_table(
        [
            _KEPT_MARKER
            if index == 100
            else str(round(1.0 + index * 0.25, 2))
            for index in range(201)
        ]
    )
    return (_described(folder, table, "kept-marker", settings), table, settings)


def _texts_in(value: object) -> "list[str]":
    """Every string a loaded document carries, keys and values alike."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        found: list[str] = []
        for key in sorted(value):
            found = found + [key] + _texts_in(value[key])
        return found
    if isinstance(value, list):
        found = []
        for item in value:
            found = found + _texts_in(item)
        return found
    return []


def test_no_published_field_carries_the_kept_marker(
    tmp_path: pathlib.Path,
    kept_marker: "tuple[contract.Profile, str, taxonomy.Settings]",
) -> None:
    """The unrecoverability, proved rather than asserted.

    The three routes of V2.3 recover a spelling from a level's variants,
    a level's label, or a `kept_by_you` sentinel verdict. A column of
    numbers publishes no level, and a verdict exists only for a
    candidate that reads as a number, so a kept NON-NUMERIC marker has
    no route. This does not take that on trust: every string the whole
    document carries, key and value alike, is compared with the marker
    at the producer's own folded identity, and none of them is it.
    """
    described, table, settings = kept_marker
    column = _reading_column(described)
    assert column.n_present == 201
    assert column.n_missing == 0
    assert column.n_not_numeric == 1
    assert validation.kept_spellings(described) == ()
    assert validation.declared_spellings(described) == ()
    document = _description_of(
        tmp_path, table, "kept-marker-again", settings
    )
    marker = parsing.folded(_KEPT_MARKER)
    carried = [
        text for text in _texts_in(document) if parsing.folded(text) == marker
    ]
    assert not carried, (
        "the description does carry the marker somewhere, so a fourth "
        f"route exists and was not taken: {carried}"
    )
    assert table.count(_KEPT_MARKER) == 1


def test_the_kept_marker_gap_is_measured_at_its_size(
    tmp_path: pathlib.Path,
    kept_marker: "tuple[contract.Profile, str, taxonomy.Settings]",
) -> None:
    """WHAT IS NOT CLOSED, at its exact size (plan amendment A-P3-15).

    Five obligations of the table the description was written from come
    back MISSED, and the list is written out so that a repair which
    closes it turns this red -- and so that a change which WIDENS it
    turns this red too. The bound is stated in `kept_spellings`; a
    sentence in a docstring that nothing measures is the defect review
    item P3-V5-F2 named.
    """
    described, table, _settings = kept_marker
    outcome = _measure(tmp_path, described, table, "kept-marker.csv")
    missed = sorted(
        {
            check.subcheck
            for check in outcome.checks
            if check.verdict == validation.MISSED
        }
    )
    assert missed == [
        "counts.n_left_out_of_statistics",
        "counts.n_not_numeric",
        "counts.numeric_share",
        "presence.n_missing",
        "presence.n_present",
    ], (
        "the size of the open kept-marker gap changed; "
        "`kept_spellings`, the module docstring and plan amendment "
        "A-P3-15 all state it and all have to move with it"
    )


def test_closing_it_here_would_state_what_the_producer_does_not_publish(
    tmp_path: pathlib.Path,
    kept_marker: "tuple[contract.Profile, str, taxonomy.Settings]",
) -> None:
    """WHY it is not closed in this module, as arithmetic.

    Two files: the witness table, and the same table with its one `n/a`
    written `NULL`. The first meets every fact the description
    publishes; the second does not, because the description's own
    producer reads `NULL` as a hole and the description says the column
    has none. So a correct report passes the first and fails the second.

    And the producer describes the two BYTE FOR BYTE ALIKE under the
    settings this module can build, which is what is asserted here. Any
    rule that reads the blank split for the first reads it for the second
    as well, and stating 201 present about the second states a count
    `synthtwin profile` run on that file would not publish -- V5.1. The
    gap therefore closes on a ruling about what the profile publishes,
    not on an edit to `validation.py`, and that is why the amendment
    records it instead of a repair claiming it.
    """
    described, table, settings = kept_marker
    other = table.replace(f",{_KEPT_MARKER}\n", ",NULL\n")
    assert other != table
    reconstructed = validation.settings_for(described)
    mine = _description_of(tmp_path, table, "witness", reconstructed)
    theirs = _description_of(tmp_path, other, "sibling", reconstructed)
    assert mine == theirs, (
        "the two files are told apart by the settings this module can "
        "build, so the gap is closable here after all and the amendment "
        "is wrong"
    )
    # ...while the description's OWN settings tell them apart exactly.
    was = _description_of(tmp_path, table, "witness-true", settings)
    now = _description_of(tmp_path, other, "sibling-true", settings)
    assert was["columns"][1]["n_present"] == 201
    assert now["columns"][1]["n_present"] == 200


def _description_of(
    folder: pathlib.Path,
    text: str,
    stem: str,
    settings: taxonomy.Settings,
) -> "dict[str, object]":
    """One file described by the real producer under given settings."""
    path = fixtures.write(folder, f"{stem}.csv", text)
    table = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    return profile.build_document(table, settings, [])


# -- the class as a shape, so a new site cannot reopen it --------------


# The readers that answer "what number is this text?" by rounding it to
# binary64. The producer decides a cell's identity exactly and every one
# of these loses the distinction it decides by.
_ROUNDING_READERS = ["parse_number", "float", "int", "round"]

# The rule that decides which cells the file's own description reads.
# The walk below starts here and follows every call it makes.
_THE_HOLE_RULE = "_cells_that_description_reads"

# The producer's own published identity for "which number is this?",
# and the one place in the closure a number may be read at all. The walk
# counts these and does not go through them: they are what the closure
# has to be STANDING on, and reading a number is what they are for --
# `taxonomy.exact_of_spelling` reaches `parsing.classify_number` by
# design, and the exact triple it returns is the thing that survives.
# Anything else that rounds is the defect this guard is for.
_THE_EXACT_IDENTITY = ["exact_of_spelling", "exact_of_number"]


def _shipped_trees() -> "dict[str, ast.Module]":
    """Every shipped module the walk may cross into, parsed, by import name.

    Keyed by the name the importing module would spell, which is the
    name an `Attribute` call carries: `synthtwin.parsing` is reached as
    `parsing` and is listed under that. Anything outside the package is
    not here, and a call into it is treated as a leaf the walk cannot
    see through -- which is why `_ROUNDING_READERS` names the readers by
    the terminal names those leaves carry.
    """
    found: dict[str, ast.Module] = {}
    for name in sorted(vars(synthtwin_package)):
        member = getattr(synthtwin_package, name)
        if isinstance(member, types.ModuleType):
            found[name] = ast.parse(inspect.getsource(member))
    return found


def _functions_of(tree: ast.AST) -> "dict[str, ast.AST]":
    """Every function of one parsed module, by name.

    Nested and method definitions are included, and both `def` and
    `async def`: a rule that walked only the module's top level would
    stop at the first helper somebody indented (review item P3-V4-F1,
    round 6).
    """
    found: dict[str, ast.AST] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            found[node.name] = node
    return found


def _dotted(node: ast.AST) -> "tuple[str, ...]":
    """The dotted path a call target spells, head first, or ()."""
    if isinstance(node, ast.Name):
        return (node.id,)
    if isinstance(node, ast.Attribute):
        head = _dotted(node.value)
        if not head:
            return ()
        return head + (node.attr,)
    return ()


def _bindings_in(node: ast.AST) -> "dict[str, tuple[str, ...]]":
    """Every name this scope binds to another name, and to what.

    Three shapes, and each is one of the three routes round 6's probes
    walked past: `from m import a as b`, `import m as b`, and a plain
    `b = a` or `b = m.a`. The value is the dotted path the alias stands
    for, so resolving an alias is following this map until it stops
    moving.
    """
    bound: dict[str, tuple[str, ...]] = {}
    for inner in ast.walk(node):
        if isinstance(inner, ast.ImportFrom):
            for alias in inner.names:
                bound[alias.asname if alias.asname else alias.name] = (
                    alias.name,
                )
        elif isinstance(inner, ast.Import):
            for alias in inner.names:
                spelled = alias.name.split(".")
                bound[
                    alias.asname if alias.asname else spelled[0]
                ] = tuple(spelled)
        elif isinstance(inner, ast.Assign):
            path = _dotted(inner.value)
            if not path:
                continue
            for target in inner.targets:
                if isinstance(target, ast.Name):
                    bound[target.id] = path
    return bound


def _resolved(
    path: "tuple[str, ...]", bound: "dict[str, tuple[str, ...]]"
) -> "tuple[str, ...]":
    """One dotted path with its head followed through the aliases."""
    seen: dict[str, int] = {}
    while path and path[0] in bound and path[0] not in seen:
        seen[path[0]] = 1
        path = bound[path[0]] + path[1:]
    return path


def _calls_in(
    node: ast.AST, bound: "dict[str, tuple[str, ...]]"
) -> "list[tuple[str, ...]]":
    """Every call this function makes, as a resolved dotted path.

    The aliases of the enclosing module are handed in and the ones this
    function binds itself are added on top, so a local `reader = float`
    resolves the same way an imported one does.
    """
    mine: dict[str, tuple[str, ...]] = {}
    for name in bound:
        mine[name] = bound[name]
    for name in _bindings_in(node):
        mine[name] = _bindings_in(node)[name]
    named: list[tuple[str, ...]] = []
    for inner in ast.walk(node):
        if isinstance(inner, ast.Call):
            path = _resolved(_dotted(inner.func), mine)
            if path:
                named = named + [path]
    return named


def _asks_a_rounding_reader(path: "tuple[str, ...]") -> str:
    """The rounding reader this call names, at ANY position, or "".

    EVERY POSITION, because the terminal name is not where the reader
    always sits (review item P3-V4-F1, round 6). `parse_number.__call__`
    ends in `__call__`; `float.__call__`, a bound method taken off a
    reader, and a reader reached through a module all put the name
    somewhere else in the path. A path is clean only when no part of it
    is a reader.
    """
    for part in path:
        if part in _ROUNDING_READERS:
            return part
    return ""


def _the_closure_of(
    trees: "dict[str, ast.Module]",
) -> "tuple[str, int, dict[tuple[str, str], int]]":
    """Walk the hole rule's closure; say what it found.

    Returns the complaint (empty when the closure is clean), how many
    times it asked the producer for an exact number, and every
    (module, function) it reached. Taking the parsed modules as an
    argument is what lets the probes below run the SAME walk over a
    doctored tree: a guard whose teeth are described rather than
    exercised is the guard round 6 walked past.
    """
    functions: dict[str, dict[str, ast.AST]] = {}
    bindings: dict[str, dict[str, tuple[str, ...]]] = {}
    for module_name in trees:
        functions[module_name] = _functions_of(trees[module_name])
        bindings[module_name] = _bindings_in(trees[module_name])
    if "validation" not in functions:
        return ("the shipped module list is empty", 0, {})
    if _THE_HOLE_RULE not in functions["validation"]:
        renamed = (
            "the rule this walk starts from was renamed, so the walk is "
            "asserting nothing"
        )
        return (renamed, 0, {})
    start = ("validation", _THE_HOLE_RULE)
    reached: dict[tuple[str, str], int] = {start: 1}
    frontier = [start]
    exact_asked = 0
    while frontier:
        module_name, name = frontier[0]
        frontier = frontier[1:]
        for path in _calls_in(
            functions[module_name][name], bindings[module_name]
        ):
            reader = _asks_a_rounding_reader(path)
            if reader:
                complaint = (
                    f"`{module_name}.{name}` is in the closure of the "
                    f"rule that decides which cells the file's own "
                    f"description reads, and it calls "
                    f"`{'.'.join(path)}`, which asks `{reader}` -- a "
                    f"reader that answers in binary64. The producer "
                    f"decides the same question exactly, and two "
                    f"spellings a person can tell apart round to one "
                    f"value (review items P1-R8-F2 and P3-V4-F1)"
                )
                return (complaint, exact_asked, reached)
            if path[-1] in _THE_EXACT_IDENTITY:
                exact_asked = exact_asked + 1
                continue
            # Where the call lands, if it lands anywhere the walk can
            # read: a bare name in this module, or a function of another
            # shipped module reached through its import name.
            landed: tuple[str, str] | None = None
            crosses = len(path) > 1 and path[-2] in functions
            if len(path) == 1 and path[0] in functions[module_name]:
                landed = (module_name, path[0])
            elif crosses and path[-1] in functions[path[-2]]:
                landed = (path[-2], path[-1])
            if landed is not None and landed not in reached:
                reached[landed] = 1
                frontier = frontier + [landed]
    return ("", exact_asked, reached)


def test_the_hole_rule_asks_no_rounding_reader() -> None:
    """No function that decides which cells are read may round a number.

    THE CLASS, NOT THE CASE. Three repairs of this finding have now been
    written, and every time the defect was one comparison in one
    function; the next time it would be a helper somebody adds beside
    them. So this walks the whole closure -- every function reachable by
    call from the rule that decides which cells the file's own
    description reads -- and asserts that not one of them asks a reader
    that answers in binary64. A new helper is inside the walk on the
    commit that adds it, without anybody remembering this file exists.

    AND THE WALK IS THE CLOSURE NOW, WHICH IT WAS NOT (review round 6).
    The version this replaces read one module and compared TERMINAL
    NAMES, and three probes walked straight past it: `parse_number.__call__`
    was seen as `__call__`, a rounding helper in another shipped module
    was seen as its own blameless name with its body never read, and
    `reader = float; reader(cell)` was seen as `reader`. A guard that
    exists because a finding keeps coming back has to be harder to walk
    past than the finding is to reintroduce. So the walk now
    * follows a call into any shipped module and reads that function's
      body too, rather than stopping at the package boundary;
    * resolves every alias -- `import ... as`, `from ... import ... as`,
      and a plain assignment, at module level and inside the function --
      before it judges a name;
    * and judges EVERY part of a dotted path rather than its last, so a
      reader reached as an attribute of itself is still that reader.

    The exact identity is `taxonomy`'s published rule, and the closure
    has to be standing on it rather than beside it, so that is asserted
    too: taking it away leaves the closure with no way to tell two
    numbers apart at all.
    """
    trees = _shipped_trees()
    complaint, exact_asked, reached = _the_closure_of(trees)
    assert not complaint, complaint
    assert exact_asked, (
        "nothing in the closure asks `taxonomy` for an exact number, so "
        "it is deciding a cell's identity some other way"
    )
    # The walk has to have gone somewhere, and it has to have LEFT this
    # module: a closure that stops at the package boundary would pass
    # every assertion above while the rounding sat one import away.
    assert len(reached) > 3
    crossed = [where for where in reached if where[0] != "validation"]
    assert crossed, (
        "the walk never left `validation`, so its cross-module claim is "
        "asserting nothing"
    )


# The three routes round 6's probes took past the version of this guard
# that read one module and compared terminal names. Each is a whole
# `validation` module, so the walk starts where it really starts and the
# probe is the only thing it finds.
_PROBES = {
    "an-attribute-of-the-reader": (
        "from synthtwin.parsing import parse_number\n"
        "\n"
        "\n"
        "def _cells_that_description_reads(block, cells, kept, declared):\n"
        "    return parse_number.__call__(cells[0])\n"
    ),
    "a-helper-in-another-shipped-module": (
        "from synthtwin import parsing\n"
        "\n"
        "\n"
        "def _cells_that_description_reads(block, cells, kept, declared):\n"
        "    return parsing.classify_number(cells[0])\n"
    ),
    "a-local-alias": (
        "def _cells_that_description_reads(block, cells, kept, declared):\n"
        "    reader = float\n"
        "    return reader(cells[0])\n"
    ),
    "a-module-level-alias": (
        "_reader = float\n"
        "\n"
        "\n"
        "def _cells_that_description_reads(block, cells, kept, declared):\n"
        "    return _reader(cells[0])\n"
    ),
    "a-renamed-import": (
        "from builtins import int as whole\n"
        "\n"
        "\n"
        "def _cells_that_description_reads(block, cells, kept, declared):\n"
        "    return whole(cells[0])\n"
    ),
    "one-helper-away": (
        "def _reads_it(cell):\n"
        "    return float(cell)\n"
        "\n"
        "\n"
        "def _cells_that_description_reads(block, cells, kept, declared):\n"
        "    return _reads_it(cells[0])\n"
    ),
}


@pytest.mark.parametrize("route", sorted(_PROBES))
def test_the_guard_catches_each_route_that_walked_past_it(route: str) -> None:
    """The guard's own teeth, one route per case (review round 6).

    A guard is a claim, and a claim nobody made fail is a claim nobody
    checked. Round 6 did not argue that the walk was imperfect; it
    showed three writings of the defect the walk called clean. Each of
    those, and three more of the same shape, is put through the SAME
    machinery here with a doctored `validation` module in place of the
    real one -- so what is asserted is that the walk complains, not that
    somebody remembered to widen a list.

    SAID PLAINLY: FIVE OF THE SIX ARE NEW. The old walk called
    `an-attribute-of-the-reader`, `a-helper-in-another-shipped-module`,
    `a-local-alias`, `a-module-level-alias` and `a-renamed-import`
    clean; it already caught `one-helper-away`, which is here because a
    widening that lost the case the old walk DID hold would be a repair
    that broke something to fix something.

    The helper-in-another-module probe stands on a real shipped function
    (`parsing.classify_number`) rather than an invented one: crossing
    the package boundary is the part that has to work on the real tree.
    """
    trees = _shipped_trees()
    trees["validation"] = ast.parse(_PROBES[route])
    complaint, _asked, _reached = _the_closure_of(trees)
    assert complaint, (
        f"the walk called `{route}` clean, so this guard is not the "
        f"closure it says it is"
    )
