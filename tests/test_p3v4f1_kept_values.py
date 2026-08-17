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
SEVENTEEN. That is closed here, by the fourth published route.

AND THE ONE THIS FILE MEASURED AS OPEN FOR THREE ROUNDS IS CLOSED TOO,
BY THE FORMAT AND THEN BY THE VALIDATOR (contract version 5 section 6;
plan amendments A-P3-27, A-P3-28 and A-P3-29). It was a `--keep-value`
spelling that is one of the built-in missing texts, on a column
publishing no level that carries it: no field of a version 4 document
held it, and the two files that decide the question were described byte
for byte alike. Version 5 records which members of this package's own
thirteen published words a declaration named -- from the command line,
never from a cell -- and the validator now reads that record instead of
inferring the tuple from levels and verdicts. The witness that named
this class, two hundred readings and one `n/a` kept as data, is measured
in full and misses nothing. What the three tests below assert is
therefore the CLOSURE at the same width they used to assert the gap,
including the arithmetic that used to say why it could not close here.

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
* WHAT IS OPEN AND WHAT IS NOT, MEASURED RATHER THAN DESCRIBED: the
  sub-floor declaration, still open and pinned to the exact list of
  subchecks it costs, and the kept marker, now closed and pinned to the
  same list as a list of CHECKS -- with the marker still shown to be in
  no column of the document, and the two files that used to be described
  alike shown to be told apart;
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
import os
import pathlib
import types
import typing

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


def _kept_the_version_four_way(
    described: contract.Profile,
) -> "tuple[str, ...]":
    """`kept_spellings` as it stood before the settings block carried it.

    The three routes of V2.3, inferred from facts a description
    publishes for other reasons: a `kept_by_you` sentinel verdict, a
    level's label, and a level's `variants` keys. None of them reaches a
    rescued word on a column of numbers, which is the class this file is
    about.
    """
    found: dict[str, int] = {}
    for column in described.columns:
        for verdict in column.sentinel_verdicts:
            if verdict.reason == taxonomy.REASON_KEPT_BY_USER:
                found[verdict.candidate] = 1
        facts = column.facts
        if isinstance(facts, contract.LabelFacts):
            for level in facts.levels:
                found[level.label] = 1
                for spelling in level.variants:
                    found[spelling] = 1
    return tuple(sorted(found))


@pytest.fixture(scope="module", autouse=True)
def _reinstated() -> "typing.Iterator[None]":
    """Put the pre-ruling behaviour back when REINSTATE asks for it.

    `REINSTATE=A-P3-26` makes no column unrebuildable, so the gap this
    file still measures at its size goes back to being printed as
    misses and the assertions that say otherwise go red.

    `REINSTATE=A-P3-29` makes the validator infer the kept side from
    levels and verdicts again instead of reading the settings block, so
    every assertion that the kept-marker class is CLOSED goes red: the
    tuple comes back empty, the seven obligations of the witness table
    are reported missed again, and the two files the description used to
    be unable to tell apart are described alike again.

    MODULE-SCOPED, because the descriptions below are built in
    module-scoped fixtures.
    """
    monkeypatch = pytest.MonkeyPatch()
    asked = os.environ.get("REINSTATE")
    if asked == "A-P3-26":
        monkeypatch.setattr(
            validation, "unrebuildable_columns", lambda _described: {}
        )
    if asked == "A-P3-29":
        monkeypatch.setattr(
            validation, "kept_spellings", _kept_the_version_four_way
        )
    yield
    monkeypatch.undo()


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
    # THE POOLED REMAINDER IS A FIELD OF ITS OWN from contract version 5
    # (its section 5): the spellings map names groups the floor let it
    # name, and nothing else. Four cells is under the floor, so the map
    # names none of them and the count says how many it does not name.
    assert pooled.missing_by_source == {}
    assert pooled.n_missing_withheld == 4
    assert pooled.n_missing_blank == 0
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


_SUB_FLOOR_RESIDUAL = (
    "axes.role",
    "axes.statistical_type",
    "counts.n_not_numeric",
    "distinct.n_distinct",
    "distinct.n_distinct_folded",
    "presence.n_missing",
    "presence.n_present",
)


def test_the_declaration_below_the_floor_is_left_open_at_its_size(
    tmp_path: pathlib.Path,
    declared_below_the_floor: "tuple[contract.Profile, str, str]",
) -> None:
    """WHAT IS NOT CLOSED, measured rather than described.

    A declaration whose cells sit below `small_cell_floor` in every
    column is pooled into `(withheld)` and published nowhere, so no
    route can bring it back and the table it was written from cannot be
    read back the way it was written.

    WHAT THE SEVEN NAMES BELOW USED TO BE, AND WHAT THEY ARE NOW (owner
    ruling 2026-08-16, plan amendment A-P3-26). They were seven MISSED
    verdicts on a table that is its own description's perfect match --
    a confident false alarm, printed with numbers. They are now seven
    lines of the NOT-CHECKABLE census, each carrying the sentence that
    says what the description does not record. The gap did not close:
    the spelling is exactly as unrecoverable as it was. What changed is
    that the report no longer states a failure it cannot support.

    They are still written out one by one, so that a repair which closes
    the gap turns this red and a change which WIDENS it turns this red
    too.

    The twin is the other half: it writes its holes empty, so the twin
    of this description misses nothing -- and its obligations are moved
    by the same rule, because which obligations a run can check is a
    function of the DESCRIPTION and the two runs share one.
    """
    described, table, twin = declared_below_the_floor
    column = _reading_column(described)
    assert column.n_missing < _FLOOR
    open_run = _measure(tmp_path, described, table, "pooled-table.csv")
    assert open_run.census.missed == 0, (
        "the table its own description was written from is reported as "
        "missing an obligation again"
    )
    unsupported = sorted(
        {
            listing.subcheck
            for listing in open_run.listings
            if listing.reason.endswith(validation.UNREBUILDABLE_REASON_TAIL)
        }
    )
    for subcheck in _SUB_FLOOR_RESIDUAL:
        assert subcheck in unsupported, (
            f"the sub-floor residual changed size: {subcheck} is neither "
            f"checked nor named as unsupported; it is stated in "
            f"`declared_spellings`, in `unrebuildable_columns` and in "
            f"plan amendments A-P3-15 and A-P3-26, and all of them have "
            f"to move with it"
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


def test_no_column_carries_the_kept_marker_and_the_settings_now_do(
    tmp_path: pathlib.Path,
    kept_marker: "tuple[contract.Profile, str, taxonomy.Settings]",
) -> None:
    """Where the rescued word is, and where it still is not.

    THIS TEST WAS THE OTHER WAY ROUND UNTIL CONTRACT VERSION 5, and the
    change is that version's whole point on this side (its section 6;
    plan amendments A-P3-27, A-P3-28 and A-P3-29). The three routes of
    V2.3 brought a spelling back from a level's variants, a level's
    label, or a `kept_by_you` sentinel verdict. A column of numbers
    publishes no level, and a verdict exists only for a candidate that
    reads as a number, so no COLUMN of this description can name a
    rescued non-numeric marker -- and none does, which is asserted here
    at the width the finding was about.

    What changed is that `n/a` is one of synthtwin's OWN ten published
    words for "no value", so the settings block names it: the member's
    spelling, computed from the command line without reading a cell, and
    written the same whether or not the table holds it. That is the
    stated lowering of the Phase 1 settings rule, and its bound is that
    a word outside those thirteen is still written nowhere in the
    settings block -- which `tests/test_p1r7f2_disclosure_is_true.py`
    checks from the other side. It is a bound on THAT block: a word of
    the person's own named with `--missing-value` reaches its column's
    `missing_by_source` under the ordinary floor, which is review item
    P3-V9-F1 and plan amendment A-P3-31.

    AND THE VALIDATOR NOW READS THAT RECORD, which is this stage's half
    of it: `kept_spellings` returns the member, out of the one place the
    document holds it, so the reading rule this description was written
    under is rebuilt exactly although no column of it carries the word.
    """
    described, table, settings = kept_marker
    column = _reading_column(described)
    assert column.n_present == 201
    assert column.n_missing == 0
    assert column.n_not_numeric == 1
    assert validation.kept_spellings(described) == (_KEPT_MARKER,)
    assert validation.declared_spellings(described) == ()
    # ...and it came from the settings block, not from any column: the
    # three routes this replaced bring back nothing on this description.
    assert _kept_the_version_four_way(described) == ()
    document = _description_of(
        tmp_path, table, "kept-marker-again", settings
    )
    marker = parsing.folded(_KEPT_MARKER)
    for block in document["columns"]:
        assert not [
            text
            for text in _texts_in(block)
            if parsing.folded(text) == marker
        ], (
            "a column block carries the marker, so a fourth per-column "
            "route exists and was not taken"
        )
    assert described.settings.kept_values.built_in_texts == (_KEPT_MARKER,)
    carried = [
        text for text in _texts_in(document) if parsing.folded(text) == marker
    ]
    assert carried == [_KEPT_MARKER], (
        f"the rescued vocabulary member is named in exactly one place, "
        f"the settings block; it is in {len(carried)}"
    )
    assert table.count(_KEPT_MARKER) == 1


def test_the_kept_marker_gap_is_measured_at_its_size(
    tmp_path: pathlib.Path,
    kept_marker: "tuple[contract.Profile, str, taxonomy.Settings]",
) -> None:
    """THE SEVEN, NOW CHECKED AND HELD (plan amendment A-P3-29).

    The list is the same list this test has carried since round 6, and
    what it asserts about each entry has moved twice. Under amendment
    A-P3-15 the seven were MISSED on the table the description was
    written from -- a confident falsehood with numbers beside it. Under
    A-P3-26 they became seven lines of the NOT-CHECKABLE census, each
    saying what the description did not record. Under contract version 5
    the description records it and this validator reads it, so the seven
    are seven CHECKS and every one of them HOLDS.

    IT WAS FIVE, AND THE TWO THAT JOINED IT ARE A BAR BEING RAISED
    RATHER THAN A GAP GROWING (plan amendment A-P3-20 clause 3, review
    item P3-V8-F4). This description publishes two hundred decimal cells
    and one cell that is not a number, and G12.8's supply counts both
    classes: two hundred spellings from the decimal cells and one from
    the class beside them meet the published two hundred and one, so the
    description pins both distinctness counts. Until the second summand
    was written the supply read two hundred, a corner nobody needs was
    claimed, and the envelope it opened admitted this very file's two
    hundred as an AUTHORIZED DEVIATION.

    THE LIST IS STILL WRITTEN OUT ONE BY ONE, and it has to be: a
    regression that puts any of the seven back on the not-checkable
    census, or back on MISSED, turns this red by name rather than by a
    total that another change could hold level.
    """
    described, table, _settings = kept_marker
    outcome = _measure(tmp_path, described, table, "kept-marker.csv")
    assert outcome.census.missed == 0, (
        "the table its own description was written from is reported as "
        "missing an obligation again"
    )
    unsupported = sorted(
        {
            listing.subcheck
            for listing in outcome.listings
            if listing.reason.endswith(validation.UNREBUILDABLE_REASON_TAIL)
        }
    )
    assert unsupported == [], (
        "the kept-marker class is closed, so no obligation of this "
        "description is named as one it cannot support asking"
    )
    held = {
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.HELD
    }
    for subcheck in (
        "counts.n_left_out_of_statistics",
        "counts.n_not_numeric",
        "counts.numeric_share",
        "distinct.n_distinct",
        "distinct.n_distinct_folded",
        "presence.n_missing",
        "presence.n_present",
    ):
        assert subcheck in held, (
            f"the kept-marker class reopened: {subcheck} is not a check "
            f"that holds on the table its own description was written "
            f"from; `kept_spellings`, `unrebuildable_columns`, the "
            f"module docstring and plan amendments A-P3-15, A-P3-26 and "
            f"A-P3-29 all state it and all have to move with it"
        )


def test_closing_it_here_would_state_what_the_producer_does_not_publish(
    tmp_path: pathlib.Path,
    kept_marker: "tuple[contract.Profile, str, taxonomy.Settings]",
) -> None:
    """WHY it could not close here, and what the ruling changed.

    Two files: the witness table, and the same table with its one `n/a`
    written `NULL`. The first meets every fact the description
    publishes; the second does not, because the description's own
    producer reads `NULL` as a hole and the description says the column
    has none. So a correct report passes the first and fails the second.

    UNDER VERSION 4 THIS TEST ASSERTED THAT IT COULD NOT. The settings
    this module could build described the two BYTE FOR BYTE ALIKE, so
    any rule that passed the first passed the second, and stating 201
    present about the second stated a count `synthtwin profile` run on
    that file would not publish -- V5.1. The gap therefore closed on a
    ruling about what the profile publishes rather than on an edit to
    `validation.py`, and the owner took that ruling on 2026-08-17.

    SO THE ARITHMETIC IS ASSERTED THE OTHER WAY ROUND NOW, at the same
    width. The settings this module builds carry the rescued word, the
    two descriptions differ, and each file is measured under the rule
    its description was written under: the conforming file misses
    nothing and the file that does not conform MISSES. Both halves are
    here, because a change that passed both would be the same defect the
    version-4 arithmetic was recording.
    """
    described, table, settings = kept_marker
    other = table.replace(f",{_KEPT_MARKER}\n", ",NULL\n")
    assert other != table
    reconstructed = validation.settings_for(described)
    mine = _description_of(tmp_path, table, "witness", reconstructed)
    theirs = _description_of(tmp_path, other, "sibling", reconstructed)
    assert mine != theirs, (
        "the settings this module builds describe the two files alike "
        "again, so the reading rule is not being rebuilt from the "
        "description's own record of it"
    )
    # ...and the description's OWN settings tell them apart the same way.
    was = _description_of(tmp_path, table, "witness-true", settings)
    now = _description_of(tmp_path, other, "sibling-true", settings)
    assert was["columns"][1]["n_present"] == 201
    assert now["columns"][1]["n_present"] == 200
    assert mine["columns"][1]["n_present"] == 201
    assert theirs["columns"][1]["n_present"] == 200
    # The verdicts that follow from it: the file the description was
    # written from holds, and the file it was not written from misses.
    conforming = _measure(tmp_path, described, table, "conforming.csv")
    assert conforming.census.missed == 0
    other_run = _measure(tmp_path, described, other, "not-conforming.csv")
    assert other_run.census.missed > 0, (
        "a file the description does not describe is passed, which is "
        "the false pass this class used to hide behind"
    )


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
    """The dotted path a call target spells, head first, or ().

    PLAIN NAMES ONLY, and that is what this one is for now: it says
    whether an expression is something an alias may stand FOR. An alias
    to a thing the walk cannot name is not an alias -- it is the hole
    `_shape_of` reports below.
    """
    if isinstance(node, ast.Name):
        return (node.id,)
    if isinstance(node, ast.Attribute):
        head = _dotted(node.value)
        if not head:
            return ()
        return head + (node.attr,)
    return ()


# WHAT A CALL TARGET REDUCES TO WHEN IT IS NOT A DOTTED PATH (review
# item P3-V7-F5). Each mark stands for one step the walk cannot see the
# far side of, and `_complaint_about` below says what each one costs.
# They are spelled so that no Python name can equal one, which is why a
# mark can stand in the same tuple as a name without being mistaken for
# one.
_INDEXED = "[]"
_RETURNED = "()"
_UNREADABLE = "?"

_MARKS = (_INDEXED, _RETURNED, _UNREADABLE)


def _shape_of(node: ast.AST) -> "tuple[str, ...]":
    """Every way a call target can be spelled, reduced to one shape.

    TOTAL BY CONSTRUCTION, and that is round 7's repair (review item
    P3-V7-F5). The version this replaces answered the empty tuple for
    anything that was not a `Name` or an `Attribute`, and `_calls_in`
    then DROPPED such a call -- so `readers = (float,); readers[0]("1")`
    put a rounding reader inside the closure and the guard reported
    nothing. A guard that exists because one finding came back three
    times may not have a shape of call it cannot see.

    So every expression answers something. A name answers itself, an
    attribute answers its base plus its own name, and the three ways a
    call target can stop being a name at all answer a MARK:

    * `_INDEXED` -- the target was taken out of a container:
      `readers[0]`, `{"r": float}["r"]`, `[float][0]`.
    * `_RETURNED` -- the target is what another call handed back:
      `getattr(parsing, "parse_number")(cell)`, `_chosen()(cell)`,
      `functools.partial(float)(cell)`.
    * `_UNREADABLE` -- everything else, which is where a lambda, a
      conditional expression, a walrus, a comprehension and anything
      written after this file was closed all land. This is the arm that
      makes the function total: there is no expression it answers
      nothing for.

    A `Starred` and an `Await` are stepped THROUGH rather than marked:
    neither changes what is being called, and treating them as opaque
    would report a hole where there is none.
    """
    if isinstance(node, ast.Name):
        return (node.id,)
    if isinstance(node, ast.Attribute):
        return _shape_of(node.value) + (node.attr,)
    if isinstance(node, ast.Call):
        return _shape_of(node.func) + (_RETURNED,)
    if isinstance(node, ast.Subscript):
        return _shape_of(node.value) + (_INDEXED,)
    if isinstance(node, (ast.Starred, ast.Await)):
        return _shape_of(node.value)
    return (_UNREADABLE,)


def _bindings_in(node: ast.AST) -> "dict[str, tuple[str, ...]]":
    """Every name this scope binds to another name, and to what.

    Four shapes, and the first three are the routes round 6's probes
    walked past: `from m import a as b`, `import m as b`, and a plain
    `b = a` or `b = m.a`. The fourth is the annotated form of the third
    (`b: object = a`), which round 7 added with the rest of the
    spellings. The value is the dotted path the alias stands for, so
    resolving an alias is following this map until it stops moving.

    A binding to something that is NOT a dotted path is not here: it is
    in `_bound_to_nothing_readable` instead, which is where the walk
    keeps the names it cannot follow.
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
        elif isinstance(inner, ast.AnnAssign):
            if inner.value is None or not isinstance(inner.target, ast.Name):
                continue
            path = _dotted(inner.value)
            if path:
                bound[inner.target.id] = path
    return bound


def _names_bound_by(target: ast.AST) -> "list[str]":
    """The names one assignment target binds, unpacking included.

    Only names the statement REALLY binds: `holes[key] = 1` binds
    nothing, and reading `key` out of it as though it did was the first
    thing this rule got wrong.
    """
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.Tuple, ast.List)):
        found: list[str] = []
        for item in target.elts:
            found = found + _names_bound_by(item)
        return found
    if isinstance(target, ast.Starred):
        return _names_bound_by(target.value)
    return []


def _bound_to_nothing_readable(
    node: ast.AST, deep: bool
) -> "dict[str, str]":
    """Every name this scope binds to a thing the walk cannot name.

    The other half of the totality (review item P3-V7-F5). A shape can
    be a plain name and still be opaque: `reader = readers[0]` then
    `reader(cell)` spells a bare name at the call, and the walk has no
    idea what it holds. Every way of binding a name is collected here --
    assignment, annotated assignment, augmented assignment, the walrus,
    a loop variable, a comprehension variable, a `with ... as`, an
    `except ... as`, and a PARAMETER, which is how a reader gets handed
    in from outside -- and a name is left out only where what it is
    bound to is a dotted path the walk can follow instead.

    ``deep`` says whether to look inside nested statements. The walked
    function is read deeply, because a name it binds anywhere is a name
    it may call. Its module is read at the TOP LEVEL ONLY: reading a
    module deeply would collect every local of every other function in
    it, and `text = text.strip()` in one function would then be read as
    a fact about the module's own `text`.
    """
    opaque: dict[str, str] = {}

    def _record(names: "list[str]", how: str) -> None:
        for name in names:
            if name not in opaque:
                opaque[name] = how

    statements = ast.walk(node) if deep else _top_level_of(node)
    for inner in statements:
        if isinstance(inner, ast.Assign):
            for target in inner.targets:
                # A SINGLE NAME taking a dotted path is the one shape
                # `_bindings_in` records as an alias, so it is the one
                # shape left out here. `reader, other = _READERS` binds
                # nothing there and is opaque, which is the correction
                # this comment exists for.
                if isinstance(target, ast.Name) and _dotted(inner.value):
                    continue
                _record(_names_bound_by(target), "an assignment")
        elif isinstance(inner, ast.AnnAssign):
            if (
                isinstance(inner.target, ast.Name)
                and inner.value is not None
                and _dotted(inner.value)
            ):
                continue
            _record(_names_bound_by(inner.target), "an annotated assignment")
        elif isinstance(inner, ast.AugAssign):
            _record(_names_bound_by(inner.target), "an augmented assignment")
        elif isinstance(inner, ast.NamedExpr):
            if _dotted(inner.value):
                continue
            _record(_names_bound_by(inner.target), "a walrus")
        elif isinstance(inner, (ast.For, ast.AsyncFor)):
            _record(_names_bound_by(inner.target), "a loop")
        elif isinstance(inner, ast.comprehension):
            _record(_names_bound_by(inner.target), "a comprehension")
        elif isinstance(inner, ast.withitem):
            if inner.optional_vars is not None:
                _record(_names_bound_by(inner.optional_vars), "a with block")
        elif isinstance(inner, ast.ExceptHandler):
            if inner.name:
                _record([inner.name], "a caught error")
        elif isinstance(
            inner, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
        ):
            _record(_parameters_of(inner.args), "a parameter")
    return opaque


def _top_level_of(node: ast.AST) -> "list[ast.AST]":
    """The statements of a module, without descending into any of them."""
    if isinstance(node, ast.Module):
        return list(node.body)
    return []


def _parameters_of(args: ast.arguments) -> "list[str]":
    """Every parameter name of one signature, in every position."""
    found = [
        argument.arg
        for argument in list(args.posonlyargs)
        + list(args.args)
        + list(args.kwonlyargs)
    ]
    if args.vararg is not None:
        found = found + [args.vararg.arg]
    if args.kwarg is not None:
        found = found + [args.kwarg.arg]
    return found


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
    """Every call this function makes, as a resolved SHAPE.

    EVERY call, which is round 7's repair: `_shape_of` is total, so
    there is no longer a call this drops on the floor. The aliases of
    the enclosing module are handed in and the ones this function binds
    itself are added on top, so a local `reader = float` resolves the
    same way an imported one does.
    """
    mine: dict[str, tuple[str, ...]] = {}
    for name in bound:
        mine[name] = bound[name]
    for name in _bindings_in(node):
        mine[name] = _bindings_in(node)[name]
    named: list[tuple[str, ...]] = []
    for inner in ast.walk(node):
        if isinstance(inner, ast.Call):
            named = named + [_resolved(_shape_of(inner.func), mine)]
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


def _is_a_dunder(part: str) -> bool:
    """Whether this name is one of the language's own double-underscores."""
    return part.startswith("__") and part.endswith("__") and len(part) > 4


def _complaint_about(
    shape: "tuple[str, ...]", opaque: "dict[str, str]", where: str
) -> str:
    """What is wrong with one call target, or "".

    THE RULES, IN ORDER, AND WHAT EACH ONE COVERS. Together they are
    total over the shapes `_shape_of` can answer: every shape either
    names a rounding reader, carries a mark, ends in a dunder, is a bare
    name the walk saw bound to something it cannot read, or is a dotted
    path of plain names the walk goes on to follow.

    1. A rounding reader ANYWHERE in the path -- round 6's rule, kept.
    2. A target that IS a subscript. This is the round-7 witness:
       `readers[0]("1")` calls whatever the container holds, and no
       reading of the source says what that is.
    3. A target the walk could not read at all -- a lambda, a
       conditional, a walrus, anything the language grows later.
    4. A target that is what another call HANDED BACK:
       `getattr(parsing, "parse_number")(cell)` and `_chosen()(cell)`.
    5. A target whose last step is a DUNDER. `reader.__call__(cell)`
       is a call spelled as an attribute, and it is the one route
       through a value the walk cannot name that it can still refuse by
       shape.
    6. A BARE NAME the walk saw bound to something it cannot read --
       including a parameter, which is how a reader arrives from
       outside. Only a bare name: `text.strip()` is a method on a value
       and its head is a parameter in three shipped functions, so
       refusing an opaque HEAD would report a hole where there is none.

    WHY RULES 2, 3 AND 4 READ THE LAST STEP AND NOT THE WHOLE PATH, and
    it is measured rather than chosen: `text[0].strip()` in
    `parsing.classify_number` and `text.strip().casefold()` in
    `parsing.folded` are both a METHOD ON A VALUE, which is the ordinary
    way this package handles text, and a rule that refused a mark
    anywhere in the path reported both. What these three refuse is a
    call whose target is not named at all.

    WHAT REMAINS OPEN, said here rather than found later: a rounding
    reader reached as an ordinarily-named method of a value the walk
    cannot name -- `_chosen().reads(cell)`, `readers[0].reads(cell)` --
    is refused by none of these, because it has the shape of the honest
    method calls just named. Telling those apart needs the types, which
    this file does not have. Reaching it means adding a function whose
    whole purpose is to hand a reader back under a name that is not one
    of `_ROUNDING_READERS`, and the mention rule takes the plain
    spellings of that.
    """
    reader = _asks_a_rounding_reader(shape)
    if reader:
        return (
            f"{where} calls `{'.'.join(shape)}`, which asks `{reader}` -- "
            f"a reader that answers in binary64. The producer decides "
            f"the same question exactly, and two spellings a person can "
            f"tell apart round to one value (review items P1-R8-F2 and "
            f"P3-V4-F1)"
        )
    if shape[-1] == _INDEXED:
        return (
            f"{where} reaches what it calls THROUGH A SUBSCRIPT "
            f"(`{'.'.join(shape)}`), so no reading of this source says "
            f"which reader it is (review item P3-V7-F5)"
        )
    if shape[-1] == _UNREADABLE:
        return (
            f"{where} makes a call whose target this walk cannot read "
            f"(`{'.'.join(shape)}`), so it cannot say the call asks no "
            f"rounding reader (review item P3-V7-F5)"
        )
    if shape[-1] == _RETURNED:
        return (
            f"{where} calls what another call handed back "
            f"(`{'.'.join(shape)}`), so which reader that is is decided "
            f"where this walk cannot see it (review item P3-V7-F5)"
        )
    if _is_a_dunder(shape[-1]):
        return (
            f"{where} calls `{'.'.join(shape)}`, and a call spelled as a "
            f"double-underscore attribute hides which reader it is "
            f"(review item P3-V7-F5)"
        )
    if len(shape) == 1 and shape[0] in opaque:
        return (
            f"{where} calls `{shape[0]}`, which this scope binds by "
            f"{opaque[shape[0]]} -- something the walk cannot follow to a "
            f"reader (review item P3-V7-F5)"
        )
    return ""


# The fields of the tree that hold a TYPE rather than a value. `int` is
# the return of two shipped functions in the closure and the second
# argument of one `isinstance`, and neither reads a number: what the
# mention rule below is for is a reader used as a VALUE.
_TYPE_FIELDS = ("annotation", "returns")
_TYPE_TESTS = (("isinstance",), ("issubclass",))


def _value_nodes(node: ast.AST) -> "list[ast.AST]":
    """Every node of this function that stands where a VALUE stands.

    Type annotations are stepped over, and so are the classes named to
    `isinstance` and `issubclass`. Everything else is a place a rounding
    reader would be doing something.
    """
    found: list[ast.AST] = []
    frontier: list[ast.AST] = [node]
    while frontier:
        current = frontier[0]
        frontier = frontier[1:]
        found = found + [current]
        skipped: list[int] = []
        if (
            isinstance(current, ast.Call)
            and _shape_of(current.func) in _TYPE_TESTS
        ):
            skipped = [id(named) for named in current.args[1:]]
        for field, value in ast.iter_fields(current):
            if field in _TYPE_FIELDS:
                continue
            items = value if isinstance(value, list) else [value]
            for item in items:
                if isinstance(item, ast.AST) and id(item) not in skipped:
                    frontier = frontier + [item]
    return found


def _mentions_a_rounding_reader(node: ast.AST) -> str:
    """The rounding reader this function NAMES as a value, or "".

    THE ROUTE THAT NEVER SPELLS A CALL AT ALL. `list(map(float, cells))`
    reads every cell in binary64 and the only call written here is to
    `map`; `functools.partial(float)` and `sorted(key=float)` do the
    same. So the closure may not so much as name a rounding reader where
    a value belongs, which is a rule about mentions rather than about
    calls and needs no guess about what the mentioning code does with
    it.

    A reader named where a TYPE belongs is left alone -- `-> int`,
    `code: int`, `isinstance(value, int)` -- because none of those reads
    anything, and three shipped functions of the closure carry one.
    """
    for current in _value_nodes(node):
        if isinstance(current, ast.Name) and current.id in _ROUNDING_READERS:
            return current.id
        if (
            isinstance(current, ast.Attribute)
            and current.attr in _ROUNDING_READERS
        ):
            return current.attr
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
    at_module: dict[str, dict[str, str]] = {}
    for module_name in trees:
        at_module[module_name] = _bound_to_nothing_readable(
            trees[module_name], False
        )
    while frontier:
        module_name, name = frontier[0]
        frontier = frontier[1:]
        body = functions[module_name][name]
        where = (
            f"`{module_name}.{name}` is in the closure of the rule that "
            f"decides which cells the file's own description reads, and it"
        )
        opaque: dict[str, str] = {}
        for bound_name in at_module[module_name]:
            opaque[bound_name] = at_module[module_name][bound_name]
        deep = _bound_to_nothing_readable(body, True)
        for bound_name in deep:
            opaque[bound_name] = deep[bound_name]
        for path in _calls_in(body, bindings[module_name]):
            complaint = _complaint_about(path, opaque, where)
            if complaint:
                return (complaint, exact_asked, reached)
            if path[-1] in _THE_EXACT_IDENTITY:
                exact_asked = exact_asked + 1
                continue
            # Where the call lands, if it lands anywhere the walk can
            # read: a bare name in this module, or a function of another
            # shipped module reached through its import name. Every path
            # that reaches here is plain names throughout, because every
            # shape carrying a mark was refused above.
            landed: tuple[str, str] | None = None
            crosses = len(path) > 1 and path[-2] in functions
            if len(path) == 1 and path[0] in functions[module_name]:
                landed = (module_name, path[0])
            elif crosses and path[-1] in functions[path[-2]]:
                landed = (path[-2], path[-1])
            if landed is not None and landed not in reached:
                reached[landed] = 1
                frontier = frontier + [landed]
        named = _mentions_a_rounding_reader(body)
        if named:
            mentions = (
                f"{where} names `{named}` where a value belongs. A reader "
                f"that answers in binary64 does not have to be CALLED "
                f"here to read this closure's cells -- `map({named}, "
                f"cells)` hands it every one of them (review item "
                f"P3-V7-F5)"
            )
            return (mentions, exact_asked, reached)
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


# EVERY WAY OF SPELLING THE CALL THAT THIS GUARD HAS BEEN SHOWN. Each
# entry is a whole `validation` module, so the walk starts where it
# really starts and the probe is the only thing it finds; each carries
# the words its complaint has to contain, so a probe cannot be satisfied
# by the walk complaining about something else.
#
# The first six are round 6's, and are the routes past the version that
# read one module and compared terminal names. The rest are round 7's
# (review item P3-V7-F5), and they are the ways a call can be spelled
# that `_dotted` answered nothing for -- every one of which the walk
# then DROPPED. The witness the review wrote is `through-a-subscript`.
_ROUNDS = "a reader that answers in binary64"
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
    # ROUND 7's WITNESS, exactly as the review wrote it.
    "through-a-subscript": (
        "def _cells_that_description_reads(block, cells, kept, declared):\n"
        "    readers = (float,)\n"
        '    if readers[0]("1"):\n'
        "        return []\n"
        "    return cells\n"
    ),
    # ...and the same route with the container out of the closure's
    # sight, so that the SHAPE rule is what fires and not the mention
    # rule beside it.
    "out-of-a-table-defined-elsewhere": (
        "def _cells_that_description_reads(block, cells, kept, declared):\n"
        '    return _READERS["exact"](cells[0])\n'
    ),
    "what-a-call-handed-back": (
        "def _cells_that_description_reads(block, cells, kept, declared):\n"
        "    return _chosen_reader()(cells[0])\n"
    ),
    "reached-by-a-written-out-name": (
        "from synthtwin import parsing\n"
        "\n"
        "\n"
        "def _cells_that_description_reads(block, cells, kept, declared):\n"
        '    return getattr(parsing, "parse_number")(cells[0])\n'
    ),
    "chosen-by-a-condition": (
        "def _cells_that_description_reads(block, cells, kept, declared):\n"
        "    return (_exact if kept else _rounded)(cells[0])\n"
    ),
    "a-reader-a-walrus-named": (
        "def _cells_that_description_reads(block, cells, kept, declared):\n"
        "    return (reader := _rounded)(cells[0])\n"
    ),
    "behind-a-double-underscore": (
        "def _cells_that_description_reads(block, cells, kept, declared):\n"
        "    reader = _READERS[0]\n"
        "    return reader.__call__(cells[0])\n"
    ),
    "handed-in-as-a-parameter": (
        "def _reads_it(reader, cell):\n"
        "    return reader(cell)\n"
        "\n"
        "\n"
        "def _cells_that_description_reads(block, cells, kept, declared):\n"
        "    return _reads_it(_chosen_reader, cells[0])\n"
    ),
    "bound-by-a-loop": (
        "def _cells_that_description_reads(block, cells, kept, declared):\n"
        "    for reader in _READERS:\n"
        "        if reader(cells[0]):\n"
        "            return []\n"
        "    return cells\n"
    ),
    "bound-by-unpacking": (
        "def _cells_that_description_reads(block, cells, kept, declared):\n"
        "    reader, other = _READERS\n"
        "    return reader(cells[0])\n"
    ),
    "bound-by-a-comprehension": (
        "def _cells_that_description_reads(block, cells, kept, declared):\n"
        "    return [reader(cells[0]) for reader in _READERS]\n"
    ),
    # ...and the two that never spell a call on the reader at all.
    "handed-to-something-that-calls-it": (
        "def _cells_that_description_reads(block, cells, kept, declared):\n"
        "    return list(map(float, cells))\n"
    ),
    "kept-in-a-table-of-readers": (
        "from synthtwin.parsing import parse_number\n"
        "\n"
        "\n"
        "def _cells_that_description_reads(block, cells, kept, declared):\n"
        '    readers = {"exact": parse_number}\n'
        "    return _apply(readers, cells)\n"
    ),
    # An annotated alias, which is the one binding shape `_bindings_in`
    # did not read before round 7.
    "an-annotated-alias": (
        "def _cells_that_description_reads(block, cells, kept, declared):\n"
        "    reader: object = int\n"
        "    return reader(cells[0])\n"
    ),
}


# The words each probe's complaint has to contain -- kept beside the
# probes rather than inside them, so that what a route is FOR is one
# lookup and not a tuple position.
_EXPECTED = {
    "an-attribute-of-the-reader": _ROUNDS,
    "a-helper-in-another-shipped-module": _ROUNDS,
    "a-local-alias": _ROUNDS,
    "a-module-level-alias": _ROUNDS,
    "a-renamed-import": _ROUNDS,
    "one-helper-away": _ROUNDS,
    "through-a-subscript": "THROUGH A SUBSCRIPT",
    "out-of-a-table-defined-elsewhere": "THROUGH A SUBSCRIPT",
    "what-a-call-handed-back": "calls what another call handed back",
    "reached-by-a-written-out-name": "calls what another call handed back",
    "chosen-by-a-condition": "cannot read",
    "a-reader-a-walrus-named": "cannot read",
    "behind-a-double-underscore": "double-underscore attribute",
    "handed-in-as-a-parameter": "a parameter",
    "bound-by-a-loop": "a loop",
    "bound-by-unpacking": "an assignment",
    "bound-by-a-comprehension": "a comprehension",
    "handed-to-something-that-calls-it": "names `float` where a value belongs",
    "kept-in-a-table-of-readers": "names `parse_number` where a value belongs",
    "an-annotated-alias": _ROUNDS,
}


@pytest.mark.parametrize("route", sorted(_PROBES))
def test_the_guard_catches_each_route_that_walked_past_it(route: str) -> None:
    """The guard's own teeth, one route per case (rounds 6 and 7).

    A guard is a claim, and a claim nobody made fail is a claim nobody
    checked. Round 6 did not argue that the walk was imperfect; it
    showed three writings of the defect the walk called clean. Round 7
    did it again with a fourth (`through-a-subscript`). Each of those,
    and every other spelling of a call this file has been shown, is put
    through the SAME machinery here with a doctored `validation` module
    in place of the real one -- so what is asserted is that the walk
    complains, not that somebody remembered to widen a list.

    AND THE COMPLAINT HAS TO BE THE RIGHT ONE. `_EXPECTED` carries the
    words each route's complaint must contain. Without that, a walk that
    complained about the first thing it saw in every doctored module
    would pass this whole battery while covering one route.

    SAID PLAINLY: FIVE OF THE FIRST SIX WERE NEW IN ROUND 6. The old
    walk called `an-attribute-of-the-reader`,
    `a-helper-in-another-shipped-module`, `a-local-alias`,
    `a-module-level-alias` and `a-renamed-import` clean; it already
    caught `one-helper-away`, which is here because a widening that lost
    the case the old walk DID hold would be a repair that broke
    something to fix something. THE OTHER THIRTEEN ARE ROUND 7's, and
    every one of them was called clean by the round-6 walk: `_dotted`
    answered the empty tuple for the target and `_calls_in` dropped the
    call on the floor.

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
    assert _EXPECTED[route] in complaint, (
        f"the walk complained about `{route}`, but about something else: "
        f"it should have said {_EXPECTED[route]!r} and said "
        f"{complaint!r}"
    )


def test_every_rule_of_the_walk_is_reached_by_a_probe() -> None:
    """No rule of the battery may be one nothing ever fires.

    `_complaint_about` decides six things and the mention rule a
    seventh, and a rule no probe reaches is a rule that could be deleted
    without turning anything red -- which is the state round 7 found the
    subscript arm in, except that the arm did not exist. So the
    complaints the probes actually produce are collected and every one
    of the seven has to be among them.
    """
    assert sorted(_EXPECTED) == sorted(_PROBES), (
        "a probe has no words its complaint must contain, or a set of "
        "words has no probe: the two tables are one table in two halves"
    )
    said: list[str] = []
    for route in sorted(_PROBES):
        trees = _shipped_trees()
        trees["validation"] = ast.parse(_PROBES[route])
        complaint, _asked, _reached = _the_closure_of(trees)
        said = said + [complaint]
    for rule in (
        _ROUNDS,
        "THROUGH A SUBSCRIPT",
        "cannot read",
        "calls what another call handed back",
        "double-underscore attribute",
        "which this scope binds by",
        "where a value belongs",
    ):
        assert any(rule in complaint for complaint in said), (
            f"no probe in this file makes the walk say {rule!r}, so that "
            f"rule of the closure is asserting nothing"
        )
