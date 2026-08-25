"""The entry table: the registry's projection, and non-vacuity (V3, V8).

REVIEW ITEM P3-V1-F2, which named the machinery that did not exist, and
REVIEW ITEMS P3-V2-B-F4, F5, F6, F9 and F10, which found that the
machinery was itself vacuous. The validation method fixes an entry's
identity as the triple (registry fact, profile predicate, subcheck) and
requires three things of the shipped validator:

* THE PROJECTION (V3.1, V3.3; plan P3-D2). The entry table IS the
  registry's projection -- same facts, same classes, the kinds derivable
  from the registry's dispositions plus the named predicates -- so
  nothing about what a fact owes can be re-decided in code. A fact the
  validator names that the registry does not carry is drift in one
  direction; a registry fact bound to nothing is drift in the other; and
  a REPORT-ONLY fact dressed as a check is the vacuity V3.4 refuses by
  name.
* THE RED BATTERY, BOUND BY NAME (V8.1, V8.2). Every executable
  subcheck carries a registered perturbation that must make THAT
  subcheck report MISSED. A perturbation caught only by a neighbour is a
  red battery.
* THE COVERAGE IDENTITY AND THE VACUITY FLOOR (V8.3, V8.5). The
  coverage identity walks the shipped table and asserts every entry has
  such a case. The floor counts distinct perturbation classes PER
  DISPOSITION CLASS, so the battery cannot rot into one shared edit.

AND THE THIRD ROUND FOUND THE MACHINERY WEAKER THAN IT CLAIMED AGAIN
(review item P3-V3-F7). Two things were wrong with it and both are
here. Coverage was credited to ANY perturbation whose wreckage happened
to reach a site, so the registration proved nothing about the identity:
a registered row could be deleted and the suite stayed green. And one
kind of entry was EXCUSED by a proof that no file could move it, which
was false -- it reasoned about the file's own description while the
counts it excused are taken over the blank split, where the floor's
worth of cells spelling a missing marker moves all three with the role
still holding. So: coverage is credited to a registered case and to
nothing else, which makes the registration total over the shipped sites
(672 rows over 668 sites, 73 curated and 599 derived); each derived row
must be an edit aimed
at the site it covers; the floor is counted over the registration; and
nothing is excused at all.

AND THE FOURTH ROUND FOUND THE EXPECTED SIDE READING ITSELF OFF THE
SUBJECT (review item P3-V4-F6). A covering row named its site by column
and subcheck and let the registration take the REGISTRY FACT off the
shipped validator's own output, so the third term of V3.1's identity
was not being asserted at all: production could bind `date-ladder.p05`
to a different fact of the same disposition and the expectation moved
with it, leaving coverage, membership and uniqueness green over a table
whose facts were wrong. Nothing here reads that output any more. What
governs each site is composed from two statements written out in this
file -- `FIXTURE_ROLES`, checked against the DESCRIPTION, and
`SUBCHECK_FACTS`, checked against the REGISTRY -- and
`test_every_shipped_site_binds_the_fact_this_file_states` holds the
shipped table to that composition in both directions.

WHAT AN ENTRY IS, AND WHY THE ANSWER CHANGED (review item P3-V2-B-F4).
This machinery used to reduce a run to the SET OF SUBCHECK NAMES it made
miss, and to ask of the shipped table only whether each name appeared in
that set. A name is not an obligation. `styles.canonical.decimal` on a
column whose style map is pooled away is a check with a ceiling of zero
that a single re-spelled cell breaks; the SAME NAME on a column whose
decimal count is published has a ceiling equal to its own cell count and
admits every file there is. Under the name-only rule the second was
"covered" by the first, and 104 of the 539 entries the shipped validator
then produced were covered that way while no perturbation ever made THAT
entry miss. Three checks that cannot fail survived a repair whose whole
subject was checks that cannot fail.

So an entry is a SITE: the fixture whose description sets it, the column
it is set for, the registry fact, and the subcheck. A red case covers a
site only when a perturbation OF THAT FIXTURE makes THAT column's
subcheck report MISSED. The fixtures are still how the walk reaches
entries; what changed is that reaching an entry somewhere else is no
longer reaching this one.

AND WHAT THE SITE GRAIN THEN FOUND (review items P3-V2-C-F1, F2, F3, F7
and F8). Eighteen sites across the five fixtures had no red case at all
once the identity carried the column: thirteen `axes.structural_role`,
two `moments.skew`, two `styles.canonical.<form>` and one `position.at`.
Every one of the four names is repaired -- each is a listing entry on
the descriptions that leave it nothing to check, recorded as a lowering
in plan amendment A-P3-2 -- and one check that was DEFEATED rather than
vacuous, the headerless `header.presence`, is repaired with a red case
of its own. The coverage identity below is total, with nothing excused
at all, and reverting any of the five in memory turns it red naming
exactly the sites that finding named.

WHAT THE PERTURBATIONS MAY BE, AND WHY A MISSING COLUMN IS NOT ONE.
Every mutation here leaves a file that reads as a table and is measured
cell by cell, so a MISSED verdict is the outcome of a comparison the
validator actually made. Truncating a file to its header makes nearly
every subcheck miss -- because the validator is written to miss them,
not because any of them measured anything -- so it proves nothing about
whether a check can fail, and using it to satisfy the coverage identity
would be the same vacuity in a longer form. It is tested in
`test_validation.py`, where it belongs, and it is not a registered red
case.

THE DELETED COLUMN IS THAT SAME ARGUMENT IN MINIATURE, and it is why
`dropped-column` is harvested with one exception. A file with the last
column taken out makes every obligation of that column miss, all of them
for the one reason that there is no column there to measure. Those
misses are not harvested. The exception is `position.at`, whose whole
obligation IS that a column stands at this number: its miss on a file
that stops short is the measurement, not the absence of one.

Every table is built at test time by the seeded neutral builders in
`fixtures.py`; no data-format file enters the repository (plan D13).
"""

import csv
import dataclasses
import io
import os
import pathlib
import typing

import pytest

import dispositions
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

SEED = 20260813

# The shipped corner listings, taken before anything here can replace
# them, so the reinstatement below stands in for exactly one binding.
_SHIPPED_CORNER_LISTINGS = validation._corner_listings


def _one_offset_fact_rebound(
    column: contract.ColumnBlock, mine: "tuple[str, ...]"
) -> "list[validation.Listing]":
    """The corner listings with `offsets.map` bound to another fact.

    THE MUTATION THE REVIEW NAMED, written out. `datetime.n_distinct` is
    a registry fact of the same column, so the resulting report is
    well-formed: it simply duplicates one fact and omits another. Every
    assertion in this file was green against it until the binding proof
    started reading `Listing.fact`.
    """
    built: list[validation.Listing] = []
    for listing in _SHIPPED_CORNER_LISTINGS(column, mine):
        if listing.subcheck == "offsets.map":
            built = built + [
                dataclasses.replace(listing, fact="datetime.n_distinct")
            ]
        else:
            built = built + [listing]
    return built


@pytest.fixture(scope="module", autouse=True)
def _reinstated() -> "typing.Iterator[None]":
    """Rebind one corner listing's registry fact on request.

    MODULE-SCOPED, because every run this file compares is built in a
    module-scoped fixture: a function-scoped `monkeypatch` would be
    applied after the runs it was meant to change, and the red check
    would be a green run against a patch nobody used.
    """
    monkeypatch = pytest.MonkeyPatch()
    if os.environ.get("REINSTATE") == "P3-V4-F6-listings":
        monkeypatch.setattr(
            validation, "_corner_listings", _one_offset_fact_rebound
        )
    yield
    monkeypatch.undo()


# -- the fixtures the table is walked over ----------------------------


def _described(
    folder: pathlib.Path,
    text: str,
    declared: "list[str] | None" = None,
    stem: str = "table",
    first_row: str = reading.FIRST_ROW_AUTOMATIC,
) -> contract.Profile:
    """One table through the real producer and the strict loader."""
    table_path = fixtures.write(folder, f"{stem}.csv", text)
    table = reading.read_table(str(table_path), first_row=first_row)
    document = profile.build_document(
        table, taxonomy.Settings(), declared if declared else []
    )
    written = fixtures.write_profile(folder, f"{stem}-profile.json", document)
    return contract.load_profile(str(written))


def _unrepresentable_table() -> str:
    """A table whose one column holds numbers too large to hold.

    The every-role fixture reaches nine of the ten roles; this is the
    tenth. Without it the registry's whole `numeric_unrepresentable`
    group is bound by nothing on any fixture, and the totality assertion
    below would pass while nine facts went unchecked.
    """
    values = []
    for index in range(60):
        values = values + [f"{index % 7 + 1}e400", f"-{index % 5 + 1}e400"]
    return fixtures.single_column_table("overflow", values)


def _pooled_styles_table() -> str:
    """A numeric column whose style map the publication floor pools.

    Whole numbers and one each of two fractions: the two point-carrying
    spellings each cover one row, which is under the floor, so the
    description publishes the single pooled key and no count for either
    form. That is the shape the canonical-split subcheck exists for -- a
    pooled cell has no published form, so the only thing it can owe is
    its own value's canonical text -- and it is the shape review item
    P3-V1-F7 was found on.

    IT IS THIRTY-SIX CELLS AND WAS TWELVE, AND THE LENGTH IS THE
    HARNESS'S DOING RATHER THAN THE FIXTURE'S (review item P3-V3-F7).
    Three counts of this column had no perturbation that could make them
    miss, and the round-2 machinery called that a proof that no file
    could -- which was false. What moves them without changing the role
    the file's own description reads is the publication floor's worth of
    cells spelling one of the producer's own absence words: the
    description then names that source, the blank split is published,
    and the counts are taken over it (plan amendment A-P3-5 clause 1).
    Twelve cells left no room for eleven of them, and ten of one number
    left the twenty-five that remain reading as a CONSTANT column, which
    moves the role and closes the gate just as surely. So the column is
    long enough for the edit to be made and its whole numbers are spread
    rather than repeated. Nothing else about it moved: the two fractions
    are still one cell each and still pooled.
    """
    values = [f"{index % 9 + 1}" for index in range(34)] + ["1.5", "2.5"]
    return fixtures.single_column_table("reading", values)


def _spelled_styles_table() -> str:
    """A numeric column whose values are written in exponent notation.

    Every published style count is a FLOOR, so a count of zero cannot be
    missed by any file. A description publishing none of a form is
    therefore asked nothing about it and the shipped validator no longer
    files a subcheck for it at all (review item P3-V2-B-F10). This
    description publishes the exponent count, so the floor subcheck
    exists here and has a file it can fail on.
    """
    values = [f"{index + 1}e-05" for index in range(40)]
    return fixtures.single_column_table("reading", values)


def _shaped_text_table() -> str:
    """A column of structured codes too many to be categories.

    THE FORM CENSUS HAD NO FREE-TEXT FIXTURE PUBLISHING A NAMED FORM,
    and a fact no fixture reaches is a fact no test asserts anything
    about -- which is the whole subject of this file. A laboratory-code
    column at claims scale is exactly the shape P4-D18 was raised for:
    far past the categorical ceiling, every value different, and every
    one of them written the same way. It lands on `free_text`, which
    publishes no value at all, and its form census is the only thing
    that says what its twin's cells should look like.

    IT IS TWO COLUMNS for the reason the quarter fixture is: a column
    of a one-column table cannot be emptied -- the file left behind is
    no table at all and the reader refuses it before any verdict exists
    -- so a one-column fixture leaves `axes.quality_state` with no
    perturbation that can move it.
    """
    return fixtures.rows_to_csv(
        ["lab_code", "region"],
        [
            [
                f"{4000 + number}-{number % 10}",
                fixtures.REGIONS[number % 4],
            ]
            for number in range(240)
        ],
    )


def _padded_code_table() -> str:
    """A numeric column of fixed-width codes written with leading zeros.

    THE CENSUS OF FIELD WIDTHS HAD NO FIXTURE PUBLISHING A NAMED WIDTH,
    and a fact no fixture reaches is a fact no test asserts anything
    about -- which is the whole subject of this file. Forty cells all
    five figures wide put `pad_widths` above the publication floor, so
    the description names the width and the subcheck that binds it
    exists here with a file it can fail on.

    Five figures is the shape a person actually holds: a procedure
    code, a zip code whose leading zero matters, an account number. It
    is the case P4-D14 was built for, so it is the case the coverage
    identity walks.
    """
    values = [f"{index:05d}" for index in range(40)]
    return fixtures.single_column_table("code", values)


def _quarter_table() -> str:
    """A datetime column whose values name QUARTERS rather than instants.

    REVIEW ITEM P3-V3-F4. Every datetime fixture in this file published
    `resolution: date`, and a quarter is the one resolution of the three
    that names no instant -- so both distinctness counts and all nine
    interior ladder rungs were unconditionally WITHHELD on any column of
    quarters, and no fixture here had a column of quarters for the
    coverage identity to notice. A description publishing twelve
    quarters from `2018-Q1` to `2024-Q4` therefore passed against a file
    holding three of them, at exit 0.

    The values are lopsided on purpose: a ladder that is nearly a
    straight line cannot tell a conforming file from one that spreads
    its values evenly, so most of them sit in the early years and the
    later ones are thin.

    It is TWO columns and it is as long as the every-role fixture, for
    two reasons that are the harness's and not the finding's. A column
    of one table cannot be emptied -- the file left behind is no table
    at all and the reader refuses it before any verdict exists -- so a
    one-column fixture leaves `axes.quality_state` with no perturbation
    that can move it. And the producer asks that at least
    `minimum_parse_rate` of a column's written cells read as its own
    kind, which at sixty cells is every one of them: a single cell that
    is not a quarter would change the column's ROLE rather than its
    count of unreadable cells, and `counts.n_unparsed` would have no
    case either.
    """
    quarters = []
    regions = []
    for index in range(240):
        year = 2018 + (index * index) % 7
        quarters = quarters + [f"{year}-Q{(index % 4) + 1}"]
        regions = regions + [fixtures.REGIONS[index % 4]]
    return fixtures.rows_to_csv(
        ["when", "region"],
        [[moment, regions[at]] for at, moment in enumerate(sorted(quarters))],
    )


@pytest.fixture(scope="module")
def runs(
    tmp_path_factory: pytest.TempPathFactory,
) -> "list[tuple[str, contract.Profile, str]]":
    """Every fixture the table is walked over: name, description, twin.

    Between them they reach every role the taxonomy carries and both
    header modes, because the projection is TOTAL over the registry and
    a fact no fixture reaches is a fact no test is asserting anything
    about.
    """
    folder = tmp_path_factory.mktemp("entry-table")
    built: list[tuple[str, contract.Profile, str]] = []
    for name, text, declared, first_row in (
        (
            "every-role",
            fixtures.every_role_table(),
            ["record_code"],
            reading.FIRST_ROW_AUTOMATIC,
        ),
        (
            "unrepresentable",
            _unrepresentable_table(),
            None,
            reading.FIRST_ROW_AUTOMATIC,
        ),
        (
            "pooled",
            _pooled_styles_table(),
            None,
            reading.FIRST_ROW_AUTOMATIC,
        ),
        (
            "spelled",
            _spelled_styles_table(),
            None,
            reading.FIRST_ROW_AUTOMATIC,
        ),
        (
            "quarters",
            _quarter_table(),
            None,
            reading.FIRST_ROW_AUTOMATIC,
        ),
        (
            "padded-codes",
            _padded_code_table(),
            None,
            reading.FIRST_ROW_AUTOMATIC,
        ),
        (
            "shaped-text",
            _shaped_text_table(),
            None,
            reading.FIRST_ROW_AUTOMATIC,
        ),
        (
            "headerless",
            fixtures.rows_to_csv(
                ["1", "north"],
                [
                    [value, fixtures.REGIONS[index % 4]]
                    for index, value in enumerate(
                        fixtures.numbers(41, 60, 1, 400)
                    )
                ],
            ),
            None,
            reading.FIRST_ROW_DATA,
        ),
    ):
        described = _described(
            folder, text, declared, stem=name, first_row=first_row
        )
        twin = rendering.twin_csv(generation.generate(described, SEED))
        built = built + [(name, described, twin)]
    return built


def _measured(
    folder: pathlib.Path,
    described: contract.Profile,
    text: "str | bytes",
    name: str,
) -> validation.Outcome:
    """One measured file, measured.

    ``text`` is the file's characters, or its BYTES where the point of
    the perturbation is that they are not the characters any encoding
    would give -- which is the only way to reach the UTF-8 byte rule.
    """
    target = folder / name
    if isinstance(text, bytes):
        target.write_bytes(text)
    else:
        target.write_text(text, encoding="utf-8", newline="\n")
    return validation.measure(described, str(target))


# -- V3.1 and V3.3: the entry table IS the registry's projection ------


def test_every_fact_the_validator_names_is_a_registry_fact(
    tmp_path: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
) -> None:
    """Drift in one direction: a fact nobody registered.

    The registry is the class authority. A check filed under a fact the
    registry does not carry is an obligation decided in code, which is
    the thing the disposition seal exists to prevent -- so the only
    names allowed outside it are V6.2's byte rules, which no published
    field states, and that list is closed and written out.
    """
    known = {
        f"{fact.group}.{fact.field}" for fact in dispositions.REGISTRY
    }
    for name, described, twin in runs:
        outcome = _measured(tmp_path, described, twin, f"{name}.csv")
        for check in outcome.checks:
            assert (
                check.fact in known
                or check.fact in validation.BYTE_RULE_FACTS
            ), f"{name}: {check.fact} is in no registry entry"
        for listing in outcome.listings:
            assert (
                listing.fact in known
                or listing.fact in validation.BYTE_RULE_FACTS
            ), f"{name}: {listing.fact} is in no registry entry"


def test_every_registry_fact_is_bound_to_one_of_the_three_kinds(
    tmp_path: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
) -> None:
    """Drift in the other direction, and the one this review found.

    Four registry facts -- `universal.position`, `universal.role`,
    `universal.quality_state` and `universal.structural_role` -- were in
    no check, no listing and no input-side binding, while the report
    said its counts covered every obligation (review item P3-V1-F3).
    Nothing was asserting the totality the plan requires, so nothing
    turned red. This is that assertion: over fixtures reaching every
    role, every fact the registry carries is an executable subcheck, a
    listing entry, or an input-side entry.
    """
    checked: set[str] = set()
    listed: set[str] = set()
    for name, described, twin in runs:
        outcome = _measured(tmp_path, described, twin, f"{name}.csv")
        for check in outcome.checks:
            checked.add(check.fact)
        for listing in outcome.listings:
            listed.add(listing.fact)
    input_side = {
        f"{group}.{field}"
        for group, field in validation.INPUT_SIDE_ENTRIES
    }
    unbound = []
    for fact in dispositions.REGISTRY:
        key = f"{fact.group}.{fact.field}"
        if key in checked or key in listed or key in input_side:
            continue
        unbound = unbound + [f"{key} ({fact.disposition})"]
    assert not unbound, (
        "these registry facts are bound by no entry of the shipped "
        "validator, so the census that calls itself every obligation "
        "does not cover them:\n  " + "\n  ".join(sorted(unbound))
    )


def test_an_input_side_entry_is_a_fact_whose_obligation_is_on_the_profile() -> (
    None
):
    """The escape hatch the totality assertion above used to leave open.

    REVIEW ITEM P3-V2-B-F6. The assertion above counts a registry fact
    bound when its name stands in `validation.INPUT_SIDE_ENTRIES`, and
    nothing said what a name on that list has to BE. V3.3 says: a
    LOADER-ONLY fact, or the profile-side membership rule of a
    STRUCTURAL container -- facts the contract gives no obligation over
    the written file at all. Any other class of fact DOES owe the file
    something, so putting its name on that list does not discharge it;
    it hides it. Measured on the shipped tree: adding an
    EXACT-OBSERVABLE fact to the list and stripping its check and its
    listing from every outcome left this file green in nine tests.

    So the list is read against the registry's own classes, and a name
    that is not LOADER-ONLY or STRUCTURAL is refused whatever else the
    run does. `document.columns` is the split V3.3 states in as many
    words: STRUCTURAL, input-side for its membership rule, and an
    executable subcheck for the column order the CSV can evidence.
    """
    by_key = {
        f"{fact.group}.{fact.field}": fact for fact in dispositions.REGISTRY
    }
    allowed = (dispositions.LOADER_ONLY, dispositions.STRUCTURAL)
    wrong = []
    for group, field in validation.INPUT_SIDE_ENTRIES:
        key = f"{group}.{field}"
        if key not in by_key:
            wrong = wrong + [f"{key} (no registry entry carries it)"]
            continue
        if by_key[key].disposition not in allowed:
            wrong = wrong + [f"{key} ({by_key[key].disposition})"]
    assert not wrong, (
        "these names are carried as input-side entries -- facts whose "
        "whole obligation lives on the profile -- and the registry "
        "gives them a class that owes the written file something:\n  "
        + "\n  ".join(sorted(wrong))
    )
    assert validation.INPUT_SIDE_ENTRIES, (
        "the input-side list is empty, so this assertion is asserting "
        "nothing and every LOADER-ONLY fact is bound by nothing"
    )


def test_the_kind_of_every_entry_follows_from_its_disposition(
    tmp_path: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
) -> None:
    """The three-way split, derived rather than re-decided (V3.3).

    * a REPORT-ONLY fact may never carry a verdict -- it is exactly the
      class the matrix says a CSV cannot evidence;
    * a LOADER-ONLY fact may carry neither a verdict nor a listing,
      because the contract says it imposes no obligation on the written
      file at all;
    * an EXACT or APPROXIMATED fact must reach a verdict on the ordinary
      predicate, where nothing strands it.
    """
    by_key = {
        f"{fact.group}.{fact.field}": fact for fact in dispositions.REGISTRY
    }
    for name, described, twin in runs:
        outcome = _measured(tmp_path, described, twin, f"{name}.csv")
        for check in outcome.checks:
            if check.fact in validation.BYTE_RULE_FACTS:
                continue
            fact = by_key[check.fact]
            assert fact.disposition != dispositions.REPORT_ONLY, (
                f"{name}: {check.subcheck} carries a verdict for a "
                f"REPORT-ONLY fact, which is a listing entry dressed as "
                f"a check"
            )
            assert fact.disposition != dispositions.LOADER_ONLY, (
                f"{name}: {check.subcheck} carries a verdict for a fact "
                f"whose whole obligation is on the description"
            )
        for listing in outcome.listings:
            if listing.fact in validation.BYTE_RULE_FACTS:
                continue
            fact = by_key[listing.fact]
            assert fact.disposition != dispositions.LOADER_ONLY, (
                f"{name}: {listing.fact} is listed as an unverified twin "
                f"fact, which invents an obligation the matrix refuses "
                f"to state"
            )


def test_no_obligation_is_both_checked_and_listed_in_one_run(
    tmp_path: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
) -> None:
    """Double-binding, which the plan refuses beside unbinding.

    One FACT may contribute entries of more than one kind -- `columns`
    is input-side for its membership rule and executable for its order
    rule, the contract's own split. One OBLIGATION may not: an identity
    that is both a verdict and a not-checkable line in the same run is
    counted twice, once in each census, and the two censuses then
    disagree about what the run did.
    """
    for name, described, twin in runs:
        outcome = _measured(tmp_path, described, twin, f"{name}.csv")
        verdicted = {
            (check.column, check.fact, check.subcheck)
            for check in outcome.checks
        }
        for listing in outcome.listings:
            identity = (listing.column, listing.fact, listing.subcheck)
            assert identity not in verdicted, f"{name}: {identity}"


def _predicate_runs(
    folder: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
) -> "list[tuple[str, contract.Profile, str, list[str]]]":
    """One measured run for each of V3.1's named profile predicates.

    The ordinary twin of a headed description and of a headerless one,
    and the two degenerate zero-row forms, which owner decision 7 makes
    two predicates and not one: the headerless zero-row profile expects
    the empty-byte form and the headed one expects its header line.
    """
    headed = None
    bare = None
    for name, described, twin in runs:
        if name == "every-role":
            headed = (described, twin)
        if name == "headerless":
            bare = (described, twin)
    assert headed is not None and bare is not None
    built = []
    for name, described, twin in (
        ("header-written", headed[0], headed[1]),
        ("names-generated", bare[0], bare[1]),
        ("zero-rows-headered", dataclasses.replace(headed[0], n_rows=0), ""),
        ("zero-rows-headerless", dataclasses.replace(bare[0], n_rows=0), ""),
    ):
        plain = headed if name in ("header-written", "zero-rows-headered") else bare
        ordinary = _measured(folder, plain[0], plain[1], f"{name}-plain.csv")
        facts = {check.fact for check in ordinary.checks}
        facts = facts | {listing.fact for listing in ordinary.listings}
        built = built + [(name, described, twin, sorted(facts))]
    return built


def _conforming_text(described: contract.Profile, twin: str) -> str:
    """The file each predicate's own description asks for, byte for byte.

    For the two ordinary predicates that is the twin. For the two
    zero-row predicates owner decision 7 fixes it: a description whose
    names were GENERATED asks for zero bytes, and one whose names came
    from the file asks for its header line and nothing more. The header
    line is written here from the published names rather than taken off
    the validator, and the fixture names carry nothing method G2 would
    quote, so the join is the whole of the writing --
    `test_a_conforming_zero_row_file_misses_nothing_it_can_hold` is what
    holds that construction to the shipped reader.
    """
    if described.n_rows:
        return twin
    if described.source.header_source != reading.HEADER_FROM_FILE:
        return ""
    return ",".join(
        column.name for column in described.columns
    ) + "\n"


def _predicate_sites(
    folder: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
) -> "list[tuple[str, contract.Profile, str, list[Site]]]":
    """Every executable subcheck each of the four predicates files.

    Measured against the file that predicate's own description asks
    for, so the sites are the ones a conforming run files and not the
    ones a refusal path happens to leave behind.
    """
    built: list[tuple[str, contract.Profile, str, list[Site]]] = []
    for label, described, twin, _ordinary in _predicate_runs(folder, runs):
        text = _conforming_text(described, twin)
        outcome = _measured(folder, described, text, f"{label}-sites.csv")
        built = built + [(label, described, text, _sites_of(outcome))]
    return built


def test_every_named_predicate_binds_every_fact_exactly_once(
    tmp_path: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
) -> None:
    """V3.3 on all four predicates, not on the ordinary one alone.

    REVIEW ITEM P3-V2-E-F5. Totality is asserted per PREDICATE, because
    that is what V3.1 makes an entry's identity: the same fact can be a
    check under one predicate and a listing under another, and the two
    tests above walk the ordinary twin only. On the zero-row predicates
    nothing was walking at all, and two things were wrong there. The
    headed form's byte check absorbed the names and the order into a
    conjunction, so `document.n_columns` and `universal.name` were bound
    by nothing while the report called its counts every obligation the
    description sets. The headerless form listed `universal.position`
    twice -- once per column and once for the document -- which counted
    an obligation the description does not set and inflated the
    not-checkable census by one.

    Two rules, and the second is what caught the double listing: no fact
    may be unbound, and no fact may be stated BOTH as a whole and in
    parts. A line at the empty grain says "this fact, entire"; a line at
    a named grain says "this piece of it". A run carrying both counts
    the same obligation twice, and which of the two the reader is meant
    to believe is not written anywhere.
    """
    for label, described, twin, ordinary in _predicate_runs(tmp_path, runs):
        outcome = _measured(tmp_path, described, twin, f"{label}.csv")
        grains: dict[str, set[str]] = {}
        for check in outcome.checks:
            grains.setdefault(check.fact, set()).add(check.subcheck)
        for listing in outcome.listings:
            grains.setdefault(listing.fact, set()).add(listing.subcheck)
        # WHICH FACTS A DESCRIPTION BINDS IS THE DESCRIPTION'S, and a
        # predicate changes the KIND of an entry, never whether the fact
        # is bound at all. So the comparison is against the SAME
        # description's ordinary run rather than against the whole
        # registry: a description with no column of some role sets none
        # of that role's facts under any predicate, and demanding them
        # would be demanding an obligation nobody stated.
        unbound = sorted(set(ordinary) - set(grains))
        assert not unbound, (
            f"{label}: these facts the same description binds on an "
            f"ordinary file are bound by no entry here, so the census "
            f"that calls itself every obligation does not cover "
            f"them:\n  " + "\n  ".join(unbound)
        )
        doubled = [
            fact
            for fact in sorted(grains)
            if "" in grains[fact] and len(grains[fact]) > 1
        ]
        assert not doubled, (
            f"{label}: these facts are stated both as a whole and in "
            f"parts, so one obligation is counted twice: {doubled}"
        )
        verdicted = {
            (check.column, check.fact, check.subcheck)
            for check in outcome.checks
        }
        for listing in outcome.listings:
            identity = (listing.column, listing.fact, listing.subcheck)
            assert identity not in verdicted, f"{label}: {identity}"
        seen: set[tuple[str, str, str]] = set()
        for listing in outcome.listings:
            identity = (listing.column, listing.fact, listing.subcheck)
            assert identity not in seen, f"{label}: listed twice {identity}"
            seen.add(identity)


def test_an_authorized_deviation_names_a_lesser_outcome_the_plan_grants(
    tmp_path: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
) -> None:
    """A lowering shown without its authority is one nobody can check.

    Every AUTHORIZED-DEVIATION verdict must belong to a fact the
    registry carries an authorization for, and must arrive with the
    passage that grants it.
    """
    by_key = {
        f"{fact.group}.{fact.field}": fact for fact in dispositions.REGISTRY
    }
    seen = 0
    for name, described, twin in runs:
        outcome = _measured(tmp_path, described, twin, f"{name}.csv")
        for check in outcome.checks:
            if check.verdict != validation.AUTHORIZED_DEVIATION:
                continue
            seen = seen + 1
            assert check.citation, f"{name}: {check.subcheck}"
            fact = by_key[check.fact]
            assert fact.authorized, (
                f"{name}: {check.subcheck} took a lesser outcome for a "
                f"fact the registry authorizes none for"
            )
    assert seen, (
        "no fixture here reached an authorized deviation at all, so this "
        "assertion is asserting nothing"
    )


# -- V8.1 and V8.2: the red cases, each naming its own subcheck -------


def _rows_of(text: str) -> "list[list[str]]":
    """The file as records, read with the same rules the writer wrote it.

    A free-text cell can hold a comma and is then quoted, so splitting a
    line on commas takes one column apart and leaves a ragged file that
    the reader refuses -- which would make a perturbation prove nothing
    at all. The records go back out through the writer's own rules, and
    `test_the_round_trip_changes_nothing` holds this pair to producing
    the twin's exact bytes when nothing is changed.
    """
    return [row for row in csv.reader(io.StringIO(text))]


def _rebuilt(rows: "list[list[str]]") -> str:
    """Records back into a file, in the twin writer's own format."""
    out = io.StringIO()
    csv.writer(out, lineterminator="\n").writerows(rows)
    return out.getvalue()


def _cell(text: str, row: int, column: int, value: str) -> str:
    """One cell replaced, and nothing else."""
    rows = _rows_of(text)
    rows[row][column] = value
    return _rebuilt(rows)


def _first_record(described: contract.Profile) -> int:
    """The row the cells start at: after a header, or at the top."""
    if described.source.header_source == reading.HEADER_FROM_FILE:
        return 1
    return 0


def _reshaped(
    described: contract.Profile, twin: str, index: int
) -> str:
    """Append a figure to every present cell of one column.

    The cell keeps its alphabet band and grows by one character, so
    what moves is the FORM it was written in: `clinic` becomes
    `clinic1`, whose form is `AAAAAA9` and not `AAAAAA`.
    """
    rows = _rows_of(twin)
    first = _first_record(described)
    for row in range(first, len(rows)):
        if index >= len(rows[row]):
            continue
        cell = rows[row][index]
        if not cell:
            continue
        rows[row][index] = f"{cell}1"
    return _rebuilt(rows)


# EVERY BUILDER BELOW TAKES A COLUMN INDEX, not a role. The version
# these replace asked the description for the FIRST column of a role and
# perturbed that one, so a description carrying two columns of one role
# had every obligation of the second reached by nothing -- and every one
# of them counted as covered, because the coverage rule compared names.
# The every-role fixture carries two `count` columns; between them and
# the roles that share a fixture, 104 of its entries were covered that
# way.


def _every_cell(
    described: contract.Profile, text: str, index: int, value: str
) -> str:
    """Every cell of one column replaced by ``value``."""
    rows = _rows_of(text)
    for row in range(_first_record(described), len(rows)):
        rows[row][index] = value
    return _rebuilt(rows)


def _swap_columns(text: str, first: int, second: int) -> str:
    """Two whole columns exchanged, header and cells together."""
    rows = _rows_of(text)
    for row in range(len(rows)):
        cells = rows[row]
        cells[first], cells[second] = cells[second], cells[first]
    return _rebuilt(rows)


def _renamed_header(text: str, was: str, becomes: str) -> str:
    """One header name replaced by another."""
    rows = _rows_of(text)
    for index, name in enumerate(rows[0]):
        if name == was:
            rows[0][index] = becomes
    return _rebuilt(rows)


def _changed(
    described: contract.Profile,
    text: str,
    index: int,
    find_blank: bool,
    value: str,
) -> str:
    """The first cell of one column that is (or is not) blank, changed.

    "" where the column holds no such cell -- a column with no blank in
    it cannot have one filled -- and the caller leaves that perturbation
    out rather than building a file identical to the twin, which would
    be a red case that can never go red.
    """
    rows = _rows_of(text)
    for row in range(_first_record(described), len(rows)):
        if bool(rows[row][index]) != find_blank:
            rows[row][index] = value
            return _rebuilt(rows)
    return ""


def _mapped(
    described: contract.Profile,
    text: str,
    index: int,
    rule: "typing.Callable[[str], str]",
) -> str:
    """Every non-blank cell of one column put through one rule."""
    rows = _rows_of(text)
    for row in range(_first_record(described), len(rows)):
        if rows[row][index]:
            rows[row][index] = rule(rows[row][index])
    return _rebuilt(rows)


def _numbered(described: contract.Profile, text: str, index: int) -> str:
    """One numeric column spread evenly between its own two ends.

    THE MUTANT A LADDER WINDOW EXISTS TO REJECT, and the one that keeps
    the column numeric while it does it. Writing one value into every
    cell would turn the column into a constant, the file's own
    description would publish no ladder at all, and the disclosure gate
    would WITHHOLD every rung -- proving nothing about whether a rung
    can miss. Spreading the values evenly leaves a column of the same
    role, the same count of numbers and the same two ends, whose nine
    interior rungs are all in the wrong place.
    """
    rows = _rows_of(text)
    first = _first_record(described)
    numbers: list[float] = []
    for row in range(first, len(rows)):
        found = parsing.parse_number(rows[row][index])
        if found is not None:
            numbers = numbers + [found]
    if len(numbers) < 3:
        return ""
    low = min(numbers)
    high = max(numbers)
    step = 0
    for row in range(first, len(rows)):
        if not rows[row][index]:
            continue
        share = step / (len(numbers) - 1)
        rows[row][index] = f"{low + (high - low) * share}"
        step = step + 1
    return _rebuilt(rows)


def _quartered(described: contract.Profile, text: str, index: int) -> str:
    """One column of quarters moved wholesale into other quarters.

    The companion of `_dated`'s `moved` rule for the resolution that
    names no instant (review item P3-V3-F4). Every cell stays a quarter,
    so the column keeps its role, its resolution and its precision and
    the file's own description still publishes a ladder of quarters --
    what moves is where on that ladder the values sit.
    """
    rows = _rows_of(text)
    first = _first_record(described)
    step = 0
    for row in range(first, len(rows)):
        if not rows[row][index]:
            continue
        rows[row][index] = f"{2030 + (step % 3)}-Q{(step % 4) + 1}"
        step = step + 1
    return _rebuilt(rows)


def _clock_piled(
    described: contract.Profile,
    text: str,
    index: int,
    at_the_top: bool,
) -> str:
    """A clock column with its two ends kept and its middle piled up.

    The clock analogue of the date ladder's own two edits, and it exists
    for the same reason: a rung's window is the band its own rank can
    reach, so a rung near the bottom is falsifiable only UPWARD and one
    near the top only downward. One direction alone leaves half the
    ladder covered by nothing.
    """
    column = described.columns[index]
    facts = column.facts
    if not isinstance(facts, contract.ClockFacts):
        return ""
    form = facts.clock_form
    low = parsing.clock_ordinal(facts.earliest, form)
    high = parsing.clock_ordinal(facts.latest, form)
    if low is None or high is None:
        return ""
    half = (high - low) // 2
    if half < 4:
        return ""
    rows = _rows_of(text)
    first = _first_record(described)
    written = [row for row in range(first, len(rows)) if rows[row][index]]
    if len(written) < 12:
        return ""
    keep: "set[int]" = set()
    for row in written:
        if rows[row][index] == facts.earliest:
            keep.add(row)
            break
    for row in written:
        if rows[row][index] == facts.latest and row not in keep:
            keep.add(row)
            break
    corner = high - half if at_the_top else low
    place = 0
    for row in written:
        if row in keep:
            continue
        if parsing.clock_form(rows[row][index]) != form:
            # A stand-in stays a stand-in: moving it would change how
            # many cells read as clock times, which is a different
            # check's business.
            continue
        rows[row][index] = parsing.clock_spelling(
            corner + (place % half), form
        )
        place = place + 1
    return _rebuilt(rows)


def _clock_crushed(
    described: contract.Profile, text: str, index: int
) -> str:
    """A clock column with its middle piled low."""
    return _clock_piled(described, text, index, at_the_top=False)


def _clock_lifted(
    described: contract.Profile, text: str, index: int
) -> str:
    """The same edit with the middle piled high."""
    return _clock_piled(described, text, index, at_the_top=True)


def _clock_reformed(
    described: contract.Profile, text: str, index: int
) -> str:
    """Every clock cell rewritten in the OTHER of the two forms.

    The one edit that moves the published form without moving a single
    time: `09:30` and `09:30:00` are the same moment, so the column
    still reads as clock times and every value it holds is the value it
    held -- what changes is the shape its own description reads off it.
    """
    column = described.columns[index]
    facts = column.facts
    if not isinstance(facts, contract.ClockFacts):
        return ""
    rows = _rows_of(text)
    for row in range(_first_record(described), len(rows)):
        cell = rows[row][index]
        if parsing.clock_form(cell) != facts.clock_form:
            continue
        if facts.clock_form == parsing.CLOCK_HH_MM:
            rows[row][index] = f"{cell}:00"
            continue
        rows[row][index] = cell[0:5]
    return _rebuilt(rows)


def _ladder_crushed(
    described: contract.Profile, text: str, index: int
) -> str:
    """A datetime column with its two ends kept and its middle piled low."""
    return _ladder_piled(described, text, index, at_the_top=False)


def _ladder_lifted(
    described: contract.Profile, text: str, index: int
) -> str:
    """The same edit with the middle piled HIGH, and it is not decoration.

    REVIEW ITEM P3-V4-F4. A rung's window is the band its own rank can
    reach, and near the bottom of a coarse ladder that band starts AT
    the published earliest: on the quarter fixture `date-ladder.p10`
    sits in `[2018-Q1, 2018-Q3]`, so no file that piles its middle low
    can miss it -- the lowest value a cell can hold is inside the
    window. The rung is falsifiable upward and only upward, and while
    the validator drew that window with a floating-point reading of the
    ladder it was a fraction of a quarter narrower and the low pile
    appeared to catch it. Reading the ladder in the method's own whole
    numbers (G7.3) made the window the construction's own, and the
    covering case had to become an edit that can actually fail it.
    """
    return _ladder_piled(described, text, index, at_the_top=True)


def _ladder_piled(
    described: contract.Profile,
    text: str,
    index: int,
    at_the_top: bool,
) -> str:
    """A datetime column with its two ends kept and its middle piled to one side.

    THE PERTURBATION THE NINE INTERIOR RUNGS ANSWER FOR ON THEIR OWN,
    written for EVERY resolution rather than for the two that name an
    instant (review item P3-V3-F4). The first and last written cells are
    left exactly where they are, so `earliest`, `latest` and both ENDS
    of the ladder still hold; every cell between them is moved into one
    half of the published range, spread over as many different values as
    that half holds, so the column keeps its role, its resolution, its
    precision and a cardinality like its own. What is left to catch the
    file is the nine rungs between the ends -- which is the shape the
    quarter finding was found on, where all nine were withheld whatever
    the file held.

    The cells are built with the GENERATOR's own writer, which a test
    may import and the validator may not: a perturbation has to be a
    file the description's own kind of column could be written as, or
    the verdict it draws is about the role and not about the ladder.
    """
    column = described.columns[index]
    facts = column.facts
    if not isinstance(facts, contract.DatetimeFacts):
        return ""
    low = generation._ordinal_of(facts.earliest, facts.resolution)
    high = generation._ordinal_of(facts.latest, facts.resolution)
    half = (high - low) // 2
    if half < 4:
        return ""
    rows = _rows_of(text)
    first = _first_record(described)
    written = [row for row in range(first, len(rows)) if rows[row][index]]
    if len(written) < 12:
        return ""
    # The two ends are kept where the twin put them -- WHEREVER it put
    # them. Keeping the first and last WRITTEN cells instead would keep
    # whatever the twin happens to hold at those two rows, and a twin
    # does not write its values in order, so the ends moved with
    # everything else and the two end checks did the catching.
    keep: set[int] = set()
    for row in written:
        if rows[row][index] == facts.earliest:
            keep.add(row)
            break
    for row in written:
        if rows[row][index] == facts.latest and row not in keep:
            keep.add(row)
            break
    corner = high - half if at_the_top else low
    place = 0
    for row in written:
        if row in keep:
            continue
        rows[row][index] = generation._cell_of_ordinal(
            corner + (place % half),
            facts.resolution,
            facts.time_precision,
            facts.subsecond_digits,
        )
        place = place + 1
    return _rebuilt(rows)


def _dated(described: contract.Profile, text: str, index: int, rule: str) -> str:
    """One datetime column rewritten under one of five named rules.

    Each keeps the column reading as dates -- so the file's own
    description still publishes the datetime facts and the gate stays
    open -- and moves exactly one family of them: where the values sit,
    how precisely they are written, or which offset they carry.

    `subsecond` is the fifth and is review item P3-V2-B-F5's: the
    register of gaps said a cell written to the second changes the
    resolution first and the resolution check catches it, so the
    fraction count could not be reached. Written to the fraction, both
    move, and the count of subsecond digits misses beside the
    resolution.
    """
    rows = _rows_of(text)
    first = _first_record(described)
    step = 0
    for row in range(first, len(rows)):
        cell = rows[row][index]
        if not cell:
            continue
        day = f"{(step % 27) + 1:02d}"
        month = f"{(step % 11) + 1:02d}"
        minute = f"{step % 60:02d}"
        if rule == "moved":
            rows[row][index] = f"2019-{month}-{day}"
        if rule == "timed":
            rows[row][index] = f"2024-{month}-{day}T09:{minute}:00"
        if rule == "offset":
            rows[row][index] = f"2024-{month}-{day}T09:{minute}:00+02:00"
        if rule == "mixed":
            zone = "+02:00" if step % 2 else "-05:30"
            rows[row][index] = f"2024-{month}-{day}T09:{minute}:00{zone}"
        if rule == "subsecond":
            rows[row][index] = f"2024-{month}-{day}T09:{minute}:00.123"
        step = step + 1
    return _rebuilt(rows)


def _classed(
    described: contract.Profile,
    text: str,
    index: int,
    value: str,
    every: int = 20,
) -> str:
    """One cell in ``every`` of a column replaced, the rest left alone.

    A column most of whose cells still read as numbers keeps its role,
    so the counts the description publishes about the classes its cells
    fall into are still measured rather than withheld -- which is the
    difference between a red case and a file the disclosure gate closes
    over.
    """
    rows = _rows_of(text)
    first = _first_record(described)
    step = 0
    for row in range(first, len(rows)):
        if rows[row][index]:
            if step % every == 0:
                rows[row][index] = value
            step = step + 1
    return _rebuilt(rows)


def _one_cell(
    described: contract.Profile, text: str, index: int, value: str
) -> str:
    """Exactly ONE written cell of one column replaced.

    REVIEW ITEM P3-V2-B-F5, and the whole of why that register emptied.
    The register of gaps said four class counts "move only when a
    column's cells change class WITHOUT changing the role the file's own
    description reads it as", and that every class edit in this battery
    moved enough cells to re-classify the column. Both halves were true
    of the battery and neither was true of the validator: one cell in
    two hundred and forty changes what that cell IS, leaves the role
    where it was, and the count of cells of its class misses with the
    disclosure gate wide open.
    """
    rows = _rows_of(text)
    for row in range(_first_record(described), len(rows)):
        if rows[row][index]:
            rows[row][index] = value
            return _rebuilt(rows)
    return ""


def _floor_cells(
    described: contract.Profile, text: str, index: int, value: str
) -> str:
    """The publication floor's worth of one column's cells replaced.

    REVIEW ITEM P3-V2-D-F2, and the smallest edit that can still be
    reported. A style clause is settled against what the file's own
    description publishes about its own spellings, and that description
    names a form only where at least the floor's cells wear it --
    everything under the floor goes into one pooled total and the form
    is never named. So a ONE-cell edit into a form is invisible to every
    description of the file and its verdict is withheld, and a
    floor's-worth is the first edit that is not. The registered red
    cases for the three exact-count forms are this edit, because they
    have to be: a red case that cannot be reported is not a red case.
    """
    rows = _rows_of(text)
    wanted = described.settings.small_cell_floor
    written = 0
    for row in range(_first_record(described), len(rows)):
        if written >= wanted:
            break
        if not rows[row][index]:
            continue
        rows[row][index] = value
        written = written + 1
    if written < wanted:
        return ""
    return _rebuilt(rows)


def _restyled(
    described: contract.Profile, text: str, index: int, style: str
) -> str:
    """Every number of one column written in another permitted style."""
    rows = _rows_of(text)
    first = _first_record(described)
    for row in range(first, len(rows)):
        cell = rows[row][index]
        if not cell:
            continue
        found = parsing.parse_number(cell)
        if found is None:
            continue
        if style == parsing.STYLE_LEADING_ZERO:
            rows[row][index] = f"0{cell}"
        if style == parsing.STYLE_LEADING_PLUS:
            rows[row][index] = f"+{cell}"
        if style == parsing.STYLE_EXPONENT_UPPER:
            rows[row][index] = f"{found:E}"
        if style == parsing.STYLE_EXPONENT_LOWER:
            rows[row][index] = f"{found:e}"
        if style == "noncanonical":
            rows[row][index] = f"{found:.12f}"
        if style == "padded":
            rows[row][index] = _one_figure_more(cell)
    return _rebuilt(rows)


def _one_figure_more(cell: str) -> str:
    """The same number, written with one figure its shortest spelling has not.

    REVIEW ITEM P3-V2-C-F1, and the edit its witness is. `noncanonical`
    above rewrites a cell at twelve decimal places, which on a column of
    values already shorter than that produces a DIFFERENT number whose
    own shortest spelling it then is -- so it moves the ladder and never
    reaches the spelling. This one moves nothing but the characters: a
    trailing zero after the point, or one inside the mantissa of an
    exponent form, or a `.00` on a whole one. The value the cell reads
    back as is the value it held, and the text is a spelling no style of
    method G6.1 can write for it.
    """
    for marker in ("e", "E"):
        for index in range(len(cell)):
            if cell[index] != marker:
                continue
            head = cell[:index]
            tail = cell[index:]
            if "." not in head:
                head = f"{head}.0"
            return f"{head}0{tail}"
    if "." in cell:
        return f"{cell}0"
    return f"{cell}.00"


def _huge_spread(described: contract.Profile, text: str, index: int) -> str:
    """One numeric column written at both ends of what a number can hold.

    Every cell is a number the format carries, so the column keeps its
    role and the gate stays open; the SPREAD of them is not, so the
    description of the file says the deviation cannot be held. That is
    the one thing `type.std_unrepresentable` states, and review item
    P3-V2-B-F5's register said no perturbation reached it.
    """
    biggest = 1.7976931348623157e308
    rows = _rows_of(text)
    first = _first_record(described)
    step = 0
    for row in range(first, len(rows)):
        if not rows[row][index]:
            continue
        sign = 1.0 if step % 2 else -1.0
        rows[row][index] = repr(sign * biggest * (1 - step * 1e-15))
        step = step + 1
    return _rebuilt(rows)


def _one_variant(described: contract.Profile, text: str, index: int) -> str:
    """Two cells of one label written with a trailing space.

    The two cells still fold to the same published label, so the level's
    own count is untouched; what changes is the spelling map, and at two
    cells the file's own description holds the new spelling back below
    the floor -- which is the `variants_withheld` map, published empty on
    a twin and not empty here.
    """
    rows = _rows_of(text)
    first = _first_record(described)
    changed: dict[str, int] = {}
    touched = 0
    for row in range(first, len(rows)):
        cell = rows[row][index]
        if not cell:
            continue
        seen = changed.get(cell, 0)
        if seen < 2:
            changed[cell] = seen + 1
            rows[row][index] = f"{cell} "
            touched = touched + 1
    if not touched:
        return ""
    return _rebuilt(rows)


_PROSE = fixtures.prose(300)
_SHORT = fixtures.short_prose(125)


def _text_shape(
    described: contract.Profile, text: str, index: int, longer: bool
) -> str:
    """Every free-text cell written at one end of its published lengths.

    The cells stay text of several words, so the column keeps its role;
    what moves is the average and the middle of the lengths, and the two
    extremes with them.
    """
    rows = _rows_of(text)
    first = _first_record(described)
    step = 0
    for row in range(first, len(rows)):
        if not rows[row][index]:
            continue
        # Distinct values, because a column whose cells are all the same
        # is a constant column and the gate closes over its whole role.
        #
        # Prose rather than `wo rd 0`, `wo rd 1`: that family is a
        # number wearing shared text, so the perturbed column would
        # take the affixed-number role and the free-text checks this
        # case is registered against would not run at all. The filler
        # goes in the MIDDLE so both ends keep varying and no affix
        # pair can form.
        if longer:
            sentence = _PROSE[step % len(_PROSE)]
            head, rest = sentence.split(" ", 1)
            sentence = f"{head} " + "and more words " * 12 + rest
        else:
            # Shorter than any sentence the column held, and still
            # distinct enough that the categorical rule does not claim
            # the perturbed column -- which would stop the free-text
            # checks running at all.
            sentence = _SHORT[step % len(_SHORT)]
        rows[row][index] = sentence
        step = step + 1
    return _rebuilt(rows)


def _digit_codes(described: contract.Profile, text: str, index: int) -> str:
    """Every record number written as figures alone, all different."""
    rows = _rows_of(text)
    first = _first_record(described)
    step = 0
    for row in range(first, len(rows)):
        if rows[row][index]:
            rows[row][index] = f"{700000 + step}"
            step = step + 1
    return _rebuilt(rows)


def _compressed(described: contract.Profile, text: str, index: int) -> str:
    """One numeric column's values crowded down toward its own low end.

    The companion of the even spread: that one leaves the upper rungs
    close to where the description puts them, and this one moves them.
    The two ends stay where they were, so the column is still the same
    column by every fact but its shape.
    """
    rows = _rows_of(text)
    first = _first_record(described)
    numbers: list[float] = []
    for row in range(first, len(rows)):
        found = parsing.parse_number(rows[row][index])
        if found is not None:
            numbers = numbers + [found]
    if len(numbers) < 3:
        return ""
    low = min(numbers)
    high = max(numbers)
    step = 0
    for row in range(first, len(rows)):
        if not rows[row][index]:
            continue
        share = step / (len(numbers) - 1)
        rows[row][index] = f"{low + (high - low) * share * share * share}"
        step = step + 1
    return _rebuilt(rows)


def _raised_end(described: contract.Profile, text: str, index: int) -> str:
    """The largest number of one column made very much larger."""
    rows = _rows_of(text)
    first = _first_record(described)
    highest = None
    where = 0
    for row in range(first, len(rows)):
        found = parsing.parse_number(rows[row][index])
        if found is None:
            continue
        if highest is None or found > highest:
            highest = found
            where = row
    if highest is None:
        return ""
    rows[where][index] = f"{highest * 1000 + 7}"
    return _rebuilt(rows)


def _headed(described: contract.Profile, text: str) -> str:
    """A header line written into a file the description says has none."""
    names = [column.name for column in described.columns]
    return _rebuilt([names] + _rows_of(text))


def _headed_and_short(described: contract.Profile, text: str) -> str:
    """A header line written in, and one record taken out to pay for it.

    REVIEW ITEM P3-V2-C-F8. `header.presence` used to call a first line
    a header only when the file ALSO held more rows than the description
    publishes, and a conjunction is only as strong as the conjunct an
    editor can pay off separately. This is that payment: the row count
    lands exactly where the description puts it, and the first line of
    the file is still the published names. The check has to answer for
    the line it governs on its own.
    """
    names = [column.name for column in described.columns]
    rows = _rows_of(text)
    return _rebuilt([names] + rows[: len(rows) - 1])


def _dropped_column(text: str) -> str:
    """The last column taken out of every row."""
    rows = _rows_of(text)
    for row in range(len(rows)):
        rows[row] = rows[row][: len(rows[row]) - 1]
    return _rebuilt(rows)


def _extra_column(text: str) -> str:
    """One column added to every row, header included."""
    rows = _rows_of(text)
    for row in range(len(rows)):
        rows[row] = rows[row] + ["extra"]
    return _rebuilt(rows)


# The class of edit each perturbation is, in the ratified plan's own
# vocabulary (P3-D4, which enumerates them: "wrong count, moved cell,
# re-cased label, re-spelled number, shifted date, truncated file,
# re-encoded bytes, reordered columns, edited header, injected
# byte-order mark"). The class names are what V8.5's floor is counted
# over, so a class label that bundles two of the plan's own classes into
# one word makes the floor say less than the plan asks: the version
# these replace filed reordered columns, an edited header and an added
# column together as "structure", and the whole STRUCTURAL disposition
# then reached exactly one class.
CLASS_CELL = "moved-cell"
CLASS_ROWS = "wrong-row-count"
CLASS_COLUMN_COUNT = "wrong-column-count"
CLASS_ORDER = "reordered-columns"
CLASS_HEADER = "edited-header"
CLASS_LINE_ENDINGS = "line-endings"
CLASS_MARK = "byte-order-mark"
CLASS_TERMINAL = "terminal-newline"
CLASS_ENCODING = "re-encoded-bytes"
CLASS_PRESENCE = "presence"
CLASS_CONTENT = "content"
CLASS_SHAPE = "shape"
CLASS_DATE = "shifted-date"
CLASS_MANY_CELLS = "class-of-many-cells"
CLASS_ONE_CELL = "class-of-one-cell"
CLASS_SPELLING = "re-spelled-number"
CLASS_CASING = "re-cased-label"
CLASS_PRECISION = "precision"

# THE AFFIXED ROLE IS ONE OF THESE, and the edits reach its CORES.
# Every numeric edit below is written against cells that parse as
# numbers, and no cell of an affixed column does -- so applied to the
# written cells they either skipped the column entirely or destroyed
# the role, and neither proves anything about a quantitative check. The
# battery therefore takes the pair off first, edits the column of cores
# the numeric way, and puts the pair back on: the same edit, aimed at
# the population the fact is about.
NUMERIC_ROLES = ("count", "continuous", "affixed_number")
LABEL_ROLES = ("categorical", "binary", "constant")

# What one written cell can be made into, and the name each edit goes
# under. Every one of them is applied to a cell that HAS a value and to
# a cell that has none, on every column of every fixture, because which
# of the two reaches an obligation depends on the column: an all-blank
# column has no written cell to change, and a column with no blank cell
# has none to fill.
ONE_CELL_VALUES = (
    ("worded", "zz"),
    ("overflowed", "1e400"),
    ("underflowed", "-1e400"),
    ("fractioned", "1.5"),
    ("bracketed", "(4)"),
    ("contradicted", "(-4)"),
    ("tiny", "1e-400"),
    ("zeroed", "0"),
    ("negated", "-8"),
    ("plussed", "+5"),
    ("zero-led", "05"),
)

# The spellings the three exact-count forms of contract 7.5.7 are missed
# by, written the publication floor's worth at a time (review item
# P3-V2-D-F2). One cell in a form is a cell every description of the
# file pools, so its verdict is withheld and a red case built on it
# shows nothing; the floor is the first count a description names.
FLOOR_STYLE_VALUES = (
    ("zero-led", "05"),
    ("plussed", "+5"),
    ("upper", "5E0"),
)


def _perturbations(
    described: contract.Profile, twin: str
) -> "list[tuple[str, str, str | bytes]]":
    """Every registered perturbation of one twin: name, class, file.

    A perturbation whose file is "" is one this description holds no
    cell for -- a column with no blank cell cannot have one filled --
    and is left out rather than registered as a file identical to the
    twin, which would be a red case that can never go red.

    EVERY COLUMN, NOT ONE COLUMN OF EVERY ROLE (review item
    P3-V2-B-F4). An obligation belongs to a column, and a perturbation
    of another column of the same role does not reach it.
    """
    rows = _rows_of(twin)
    first = _first_record(described)
    headed = described.source.header_source == reading.HEADER_FROM_FILE
    built: list[tuple[str, str, str | bytes]] = [
        ("blanked-cell", CLASS_CELL, _cell(twin, first, 0, "")),
        ("moved-cell", CLASS_CELL, _cell(twin, first, 0, "zz")),
        ("dropped-row", CLASS_ROWS, _rebuilt(rows[: len(rows) - 1])),
        ("added-row", CLASS_ROWS, _rebuilt(rows + [rows[len(rows) - 1]])),
        ("carriage-returns", CLASS_LINE_ENDINGS, twin.replace("\n", "\r\n")),
        ("byte-order-mark", CLASS_MARK, "﻿" + twin),
        ("no-terminal-newline", CLASS_TERMINAL, twin[: len(twin) - 1]),
        ("added-column", CLASS_COLUMN_COUNT, _extra_column(twin)),
        # THE ONE PERTURBATION THAT IS NOT CHARACTERS. A file that is
        # not UTF-8 cannot be written as text, and the register of gaps
        # carried `bytes.utf8` for exactly that reason (review item
        # P3-V2-B-F5) -- a gap in the harness, recorded as though it
        # were a property of the check.
        ("not-utf8", CLASS_ENCODING, b"\xff" + twin.encode("utf-8")[1:]),
    ]
    if described.n_columns > 1:
        built = built + [
            ("dropped-column", CLASS_COLUMN_COUNT, _dropped_column(twin))
        ]
    for index in range(described.n_columns - 1):
        built = built + [
            (
                f"swapped-{index + 1}-{index + 2}",
                CLASS_ORDER,
                _swap_columns(twin, index, index + 1),
            )
        ]
    if headed:
        for column in described.columns:
            built = built + [
                (
                    f"renamed-{column.name}",
                    CLASS_HEADER,
                    _renamed_header(twin, column.name, "renamed_column"),
                )
            ]
    else:
        built = built + [
            ("written-header", CLASS_HEADER, _headed(described, twin)),
            (
                "header-and-short",
                CLASS_HEADER,
                _headed_and_short(described, twin),
            ),
        ]
    for column in described.columns:
        built = built + _column_perturbations(described, twin, column)
    return [entry for entry in built if entry[2]]


def _pair_of(
    column: contract.ColumnBlock,
) -> "tuple[str, str] | None":
    """The two pieces of text an affixed column's cells wear, or None.

    None for every other role, so a caller can ask without first
    working out which kind of column it holds.
    """
    facts = column.facts
    if not isinstance(facts, contract.AffixedFacts):
        return None
    return (facts.affix_prefix, facts.affix_suffix)


def _without_pair(
    described: contract.Profile,
    text: str,
    index: int,
    pair: "tuple[str, str]",
) -> str:
    """One affixed column rewritten as the column of cores it holds.

    A cell that does not wear the pair is left exactly as it is: the
    stragglers a parse line tolerates are not cores, and making one up
    for them would edit cells the perturbation was not aimed at.
    """
    prefix, suffix = pair
    rows = _rows_of(text)
    for row in range(_first_record(described), len(rows)):
        cell = rows[row][index]
        trimmed = cell.strip()
        if not trimmed.startswith(prefix) or not trimmed.endswith(suffix):
            continue
        core = trimmed[len(prefix) : len(trimmed) - len(suffix)]
        if core:
            rows[row][index] = core
    return _rebuilt(rows)


def _wearing_pair(
    described: contract.Profile,
    text: str,
    index: int,
    pair: "tuple[str, str]",
) -> str:
    """One column of cores rewritten as the affixed column they make.

    Every WRITTEN cell wears the pair. A blank cell stays blank -- a
    hole wearing a unit is not a hole, and an edit that filled every
    hole would be a presence edit wearing another edit's name.
    """
    prefix, suffix = pair
    rows = _rows_of(text)
    for row in range(_first_record(described), len(rows)):
        cell = rows[row][index]
        if cell:
            rows[row][index] = f"{prefix}{cell}{suffix}"
    return _rebuilt(rows)


def _pair_perturbations(
    described: contract.Profile,
    twin: str,
    index: int,
    name: str,
    pair: "tuple[str, str]",
) -> "list[tuple[str, str, str | bytes]]":
    """The edits aimed at the PAIR rather than at the numbers inside it.

    Three, and each moves one thing. A column wearing another piece of
    text in front moves the published prefix and nothing else; one
    wearing another piece behind moves the published suffix and nothing
    else; and the publication floor's worth of cells with the pair
    taken off moves how many cells wear it, while leaving the pair
    itself the one the rest of the column still wears.

    THE FLOOR'S WORTH AND NOT ONE CELL, for the reason 7.5.7's style
    edits are written that way: an edit below the floor is pooled out
    of the file's own description, and a red case built on a fact no
    description names shows nothing.
    """
    prefix, suffix = pair
    rows = _rows_of(twin)
    first = _first_record(described)
    stripped = _rows_of(twin)
    taken = 0
    for row in range(first, len(stripped)):
        if taken >= described.settings.small_cell_floor:
            break
        cell = stripped[row][index].strip()
        if not cell.startswith(prefix) or not cell.endswith(suffix):
            continue
        core = cell[len(prefix) : len(cell) - len(suffix)]
        if not core:
            continue
        stripped[row][index] = core
        taken = taken + 1
    front = _rows_of(twin)
    behind = _rows_of(twin)
    for row in range(first, len(rows)):
        if rows[row][index]:
            front[row][index] = f"x{rows[row][index]}"
            behind[row][index] = f"{rows[row][index]}x"
    built: list[tuple[str, str, "str | bytes"]] = [
        (f"prefixed-{name}", CLASS_SPELLING, _rebuilt(front)),
        (f"suffixed-{name}", CLASS_SPELLING, _rebuilt(behind)),
    ]
    if taken:
        built = built + [
            (f"unaffixed-{name}", CLASS_SPELLING, _rebuilt(stripped))
        ]
    return built


def _column_perturbations(
    described: contract.Profile,
    twin: str,
    column: contract.ColumnBlock,
) -> "list[tuple[str, str, str | bytes]]":
    """Every perturbation this ONE column carries, whatever its role."""
    index = column.position - 1
    name = column.name
    built: list[tuple[str, str, str | bytes]] = [
        (
            f"blanked-{name}",
            CLASS_PRESENCE,
            _changed(described, twin, index, False, ""),
        ),
        # THE EDIT THE TWO READINGS OF PRESENCE DISAGREE ABOUT, and the
        # one the round-3 exemption was found false by (review item
        # P3-V3-F7). The producer reads a cell spelling one of its own
        # absence words as a HOLE; the blank split reads it as a written
        # cell that is not a number (V2.4). So the publication floor's
        # worth of them leaves the file's own description reading the
        # column as the same numeric kind -- the role check HOLDS and the
        # disclosure gate stays open -- while every count taken over the
        # split moves. It takes the FLOOR'S worth and not one: below the
        # floor the description pools the spelling away, the split is not
        # published, and amendment A-P3-5 clause 1 settles those counts
        # off the file's own description, where they hold.
        (
            f"marked-{name}",
            CLASS_PRESENCE,
            _floor_cells(described, twin, index, "na"),
        ),
        # THE FORM WITHOUT THE VALUE (plan P4-D18). A figure appended
        # to a cell leaves its alphabet band where it was and moves the
        # FORM it was written in, which is the one thing the form
        # census answers for -- so this is the edit that makes a
        # published form miss and disturbs as little else as an edit
        # can.
        (
            f"reshaped-{name}",
            CLASS_SPELLING,
            _reshaped(described, twin, index),
        ),
        (
            f"filled-{name}",
            CLASS_PRESENCE,
            _changed(described, twin, index, True, "5"),
        ),
        (
            f"rewritten-{name}",
            CLASS_CONTENT,
            _every_cell(described, twin, index, "zz"),
        ),
    ]
    if described.n_columns > 1:
        # A column emptied altogether, which is the only edit that moves
        # the quality axis of a column whose role is otherwise settled:
        # eight of the ten roles answer `ok`, and a file has to make the
        # column empty to make it answer anything else. Not built for a
        # one-column description, where it leaves a file holding no
        # table at all and the reader refuses before a verdict exists.
        built = built + [
            (
                f"emptied-{name}",
                CLASS_CONTENT,
                _every_cell(described, twin, index, ""),
            )
        ]
    for tag, value in ONE_CELL_VALUES:
        built = built + [
            (
                f"one-{tag}-{name}",
                CLASS_ONE_CELL,
                _one_cell(described, twin, index, value),
            ),
            (
                f"filled-{tag}-{name}",
                CLASS_PRESENCE,
                _changed(described, twin, index, True, value),
            ),
        ]
    # From here the numeric families are built against `source`, which
    # is the twin itself for a plain numeric column and the twin with
    # the pair taken off for an affixed one, and `shaped` collects them
    # so the pair can go back on before they are handed over.
    pair = _pair_of(column)
    source = twin if pair is None else _without_pair(described, twin, index, pair)
    shaped: list[tuple[str, str, "str | bytes"]] = []
    if pair is not None:
        built = built + _pair_perturbations(described, twin, index, name, pair)
    if column.role in NUMERIC_ROLES:
        for tag, value in FLOOR_STYLE_VALUES:
            shaped = shaped + [
                (
                    f"floor-{tag}-{name}",
                    CLASS_SPELLING,
                    _floor_cells(described, source, index, value),
                )
            ]
    if column.role in NUMERIC_ROLES:
        shaped = shaped + [
            (f"spread-{name}", CLASS_SHAPE, _numbered(described, source, index)),
            (
                f"raised-{name}",
                CLASS_SHAPE,
                _raised_end(described, source, index),
            ),
            (
                f"crowded-{name}",
                CLASS_SHAPE,
                _compressed(described, source, index),
            ),
            (
                f"enormous-{name}",
                CLASS_MANY_CELLS,
                _classed(described, source, index, "1e200", 2),
            ),
            (
                f"zeroed-{name}",
                CLASS_MANY_CELLS,
                _classed(described, source, index, "0"),
            ),
            (
                f"negated-{name}",
                CLASS_MANY_CELLS,
                _classed(described, source, index, "-8"),
            ),
            (
                f"worded-{name}",
                CLASS_MANY_CELLS,
                _classed(described, source, index, "zz"),
            ),
            (
                f"bracketed-{name}",
                CLASS_MANY_CELLS,
                _classed(described, source, index, "(4)"),
            ),
            (
                f"overflowed-{name}",
                CLASS_MANY_CELLS,
                _classed(described, source, index, "9e999"),
            ),
            (
                f"underflowed-{name}",
                CLASS_MANY_CELLS,
                _classed(described, source, index, "-9e999"),
            ),
            (
                f"fractioned-{name}",
                CLASS_MANY_CELLS,
                _classed(described, source, index, "1.5"),
            ),
            (
                f"contradicted-{name}",
                CLASS_MANY_CELLS,
                _classed(described, source, index, "(-4)"),
            ),
        ]
        for style in (
            parsing.STYLE_LEADING_ZERO,
            parsing.STYLE_LEADING_PLUS,
            parsing.STYLE_EXPONENT_UPPER,
            parsing.STYLE_EXPONENT_LOWER,
            "noncanonical",
            "padded",
        ):
            shaped = shaped + [
                (
                    f"{style}-{name}",
                    CLASS_SPELLING,
                    _restyled(described, source, index, style),
                )
            ]
    if column.role in NUMERIC_ROLES or column.role == "numeric_unrepresentable":
        shaped = shaped + [
            (f"vast-{name}", CLASS_SHAPE, _huge_spread(described, source, index))
        ]
    # The pair goes back on, character for character as the
    # description publishes it, so what the file carries is the edited
    # NUMBER wearing the column's own text. A perturbation that came
    # out empty stays empty: that is the battery's word for "this
    # column has no such edit", and wrapping it would build a file
    # identical to the twin and register a red case that can never go
    # red.
    if pair is not None:
        wrapped: list[tuple[str, str, "str | bytes"]] = []
        for edit_name, edit_class, written in shaped:
            if isinstance(written, str) and written:
                written = _wearing_pair(described, written, index, pair)
            wrapped = wrapped + [(edit_name, edit_class, written)]
        shaped = wrapped
    built = built + shaped
    if column.role in LABEL_ROLES:
        built = built + [
            (
                f"recased-{name}",
                CLASS_CASING,
                _mapped(described, twin, index, lambda cell: cell.upper()),
            ),
            (
                f"spaced-{name}",
                CLASS_CASING,
                _one_variant(described, twin, index),
            ),
        ]
    if column.role == "time_of_day":
        built = built + [
            (f"crushed-{name}", CLASS_DATE, _clock_crushed(described, twin, index)),
            (f"lifted-{name}", CLASS_DATE, _clock_lifted(described, twin, index)),
            (
                f"reformed-{name}",
                CLASS_PRECISION,
                _clock_reformed(described, twin, index),
            ),
        ]
    if column.role == "datetime":
        # THE TWO EDITS EVERY RESOLUTION CARRIES, and they are chosen by
        # the resolution the description publishes rather than assumed
        # (review item P3-V3-F4). A column of quarters rewritten as
        # whole dates is a column of another resolution, so the ladder
        # it moved is not the ladder it is measured against; a column of
        # quarters rewritten as quarters is.
        quarterly = column.facts.resolution == taxonomy.RESOLUTION_QUARTER
        built = built + [
            (
                f"crushed-{name}",
                CLASS_DATE,
                _ladder_crushed(described, twin, index),
            ),
            # ...AND THE SAME EDIT THE OTHER WAY UP (review item
            # P3-V4-F4). A rung whose window starts at the published
            # earliest cannot be missed from below by any file, so the
            # low pile leaves it covered by nothing; the high pile is
            # what a rung near the bottom of a coarse ladder answers to.
            (
                f"lifted-{name}",
                CLASS_DATE,
                _ladder_lifted(described, twin, index),
            ),
        ]
        moved = (
            _quartered(described, twin, index)
            if quarterly
            else _dated(described, twin, index, "moved")
        )
        built = built + [
            (f"moved-{name}", CLASS_DATE, moved),
            (
                f"mixed-{name}",
                CLASS_PRECISION,
                _dated(described, twin, index, "mixed"),
            ),
            (
                f"timed-{name}",
                CLASS_PRECISION,
                _dated(described, twin, index, "timed"),
            ),
            (
                f"offset-{name}",
                CLASS_PRECISION,
                _dated(described, twin, index, "offset"),
            ),
            (
                f"subsecond-{name}",
                CLASS_PRECISION,
                _dated(described, twin, index, "subsecond"),
            ),
        ]
    if column.role == "free_text":
        built = built + [
            (
                f"shortened-{name}",
                CLASS_SHAPE,
                _text_shape(described, twin, index, False),
            ),
            (
                f"lengthened-{name}",
                CLASS_SHAPE,
                _text_shape(described, twin, index, True),
            ),
            (
                f"one-word-{name}",
                CLASS_CONTENT,
                _every_cell(described, twin, index, "wo rd"),
            ),
        ]
    if column.role == "identifier":
        built = built + [
            (
                f"repeated-{name}",
                CLASS_CONTENT,
                _mapped(described, twin, index, lambda _cell: "AA000"),
            ),
            (
                f"digits-{name}",
                CLASS_CONTENT,
                _digit_codes(described, twin, index),
            ),
        ]
    return built


class Site(typing.NamedTuple):
    """One entry of the shipped table, at the grain vacuity lives at.

    V3.1's identity is (registry fact, profile predicate, subcheck). The
    predicate is the description, and the description sets the obligation
    for one column at a time: the same subcheck name against a published
    count of zero and against a published count of two hundred and forty
    is not the same obligation, and one of the two can be unfalsifiable
    while the other is not. So the identity a red case has to reach
    carries the column as well.
    """

    column: str
    fact: str
    subcheck: str


class Case(typing.NamedTuple):
    """One perturbation, measured: its class, and the sites it missed."""

    kind: str
    missed: "frozenset[Site]"


def _missed_by(
    outcome: validation.Outcome, vanished: "set[str]"
) -> "frozenset[Site]":
    """Every site this run reported MISSED, and the two it does not count.

    ``vanished`` names the columns this perturbation deleted from the
    file. Their obligations all miss, every one of them for the single
    reason that there is nothing at that position to measure, so none of
    them shows that any check can fail -- the header-only file's vacuity
    written one column wide. `position.at` is the exception and is
    counted, because "a column stands at this number" is precisely what
    it measures.
    """
    found = set()
    for check in outcome.checks:
        if check.verdict != validation.MISSED:
            continue
        if check.column in vanished and check.subcheck != "position.at":
            continue
        found.add(Site(check.column, check.fact, check.subcheck))
    return frozenset(found)


def _sites_of(outcome: validation.Outcome) -> "list[Site]":
    """Every executable subcheck one run filed, as sites.

    CHECKS ONLY, and deliberately: this feeds the red battery, where a
    site owes a perturbation that makes it MISS. A listing has no
    verdict and can miss nothing, so a walk that folded listings in here
    would demand red cases for entries that have none. What a listing
    DOES owe -- the registry fact it binds -- is asserted by
    `_listed_sites_of` below and the binding proof that reads it.
    """
    return [
        Site(check.column, check.fact, check.subcheck)
        for check in outcome.checks
    ]


def _listed_sites_of(outcome: validation.Outcome) -> "list[Site]":
    """Every not-checkable obligation one run filed, as sites.

    REVIEW ITEM P3-V4-F6, the half that outlived round 6. V3.1 makes an
    entry's identity (registry fact, profile predicate, subcheck) and
    V3.3 makes a listing an entry of that table; the binding proof read
    `Check.fact` and never `Listing.fact`, so half the table's third
    term was asserted by nothing. A listing carries the same identity a
    check carries -- the `Listing` docstring says so in terms -- so the
    same Site names it.
    """
    return [
        Site(listing.column, listing.fact, listing.subcheck)
        for listing in outcome.listings
    ]


@pytest.fixture(scope="module")
def battery(
    tmp_path_factory: pytest.TempPathFactory,
    runs: "list[tuple[str, contract.Profile, str]]",
) -> "dict[str, dict[str, Case]]":
    """Every perturbation of every fixture, measured once.

    Keyed by fixture name, then by perturbation name. Built once because
    the battery is several hundred whole validate runs, and read by
    every assertion below -- including the vacuity floor, which used to
    build and measure the whole battery a second time.
    """
    folder = tmp_path_factory.mktemp("red-battery")
    found: dict[str, dict[str, Case]] = {}
    for name, described, twin in runs:
        last = described.columns[described.n_columns - 1].name
        mine: dict[str, Case] = {}
        for label, kind, text in _perturbations(described, twin):
            outcome = _measured(
                folder, described, text, f"{name}-{label}.csv"
            )
            vanished = {last} if label == "dropped-column" else set()
            mine[label] = Case(kind, _missed_by(outcome, vanished))
        found[name] = mine
    return found


class RedCase(typing.NamedTuple):
    """One registered red case, bound to the SITE it must make miss.

    The site is the whole triple V3.1 fixes -- the registry FACT
    included (review item P3-V3-F7). Without it a case named a column
    and a subcheck, and the registry could move a subcheck from one fact
    to another with every registration still passing, which is drift the
    disposition seal exists to stop.
    """

    fixture: str
    perturbation: str
    column: str
    fact: str
    subcheck: str


# Each entry is one registered red case: the fixture and the
# perturbation, against the SITE it must make miss. A red case that
# names only the subcheck names a name, and a name is not an obligation
# (review item P3-V2-B-F4): `ladder.p50` missing on one column of a
# description says nothing about `ladder.p50` on another column of the
# same description, and the version this replaces could not tell the two
# apart. One perturbation may be registered against more than one site,
# which is why this is a list of cases and not a mapping from the edit.
#
# THESE ARE THE CURATED ONES, AND THEY ARE NO LONGER THE WHOLE
# REGISTRATION (review item P3-V3-F7). Coverage used to be credited to
# ANY perturbation in the battery that happened to make a site miss, so
# these rows proved something about the checks they name and nothing
# about the identity: deleting one left the suite green, because some
# other edit's collateral miss went on counting. Coverage is now
# credited to a registered case and to nothing else (V8.3), which makes
# these rows load-bearing and requires the registration to be TOTAL over
# the shipped sites. The rest of it is `COVERING_RED_CASES` below; these
# keep their place because a human chose each one against a finding, and
# they are preferred over the derived row for the same site.
NAMED_RED_CASES = (
    RedCase(
        "every-role",
        "blanked-cell",
        "record_code",
        "universal.n_present",
        "presence.n_present",
    ),
    RedCase(
        "every-role",
        "moved-cell",
        "record_code",
        "identifier.min_length",
        "length.min",
    ),
    RedCase("every-role", "dropped-row", "", "document.n_rows", "rows.n_rows"),
    RedCase("every-role", "added-row", "", "document.n_rows", "rows.n_rows"),
    RedCase(
        "every-role",
        "carriage-returns",
        "",
        "document.line-endings",
        "bytes.line-endings",
    ),
    RedCase(
        "every-role",
        "byte-order-mark",
        "",
        "document.encoding",
        "bytes.byte-order-mark",
    ),
    RedCase(
        "every-role",
        "no-terminal-newline",
        "",
        "document.line-endings",
        "bytes.terminal-newline",
    ),
    RedCase("every-role", "not-utf8", "", "document.encoding", "bytes.utf8"),
    RedCase(
        "every-role",
        "added-column",
        "",
        "document.n_columns",
        "columns.n_columns",
    ),
    RedCase("every-role", "dropped-column", "", "document.columns", "columns.order"),
    # ...AND THE SAME SITE UNDER TWO MORE CLASSES OF EDIT, which is what
    # the vacuity floor asks of the STRUCTURAL disposition and what the
    # shipped table gives it only one executable subcheck to answer with
    # (review item P3-V3-F7). The floor is counted over the REGISTRATION
    # now rather than over every collateral miss the battery makes, so
    # the three classes have to be registered: a column taken out, two
    # columns swapped, one column renamed. A site with more than one
    # registered case is deliberate here, as it is for the headerless
    # `header.presence` below, and it is the only thing that weakens
    # "delete a row and the identity says so" -- for these three, two
    # rows have to go.
    RedCase("every-role", "swapped-1-2", "", "document.columns", "columns.order"),
    RedCase(
        "every-role",
        "renamed-record_code",
        "",
        "document.columns",
        "columns.order",
    ),
    RedCase(
        "every-role",
        "swapped-1-2",
        "record_code",
        "universal.position",
        "position.at",
    ),
    RedCase("every-role", "renamed-record_code", "", "universal.name", "header.names"),
    RedCase(
        "every-role",
        "recased-region",
        "region",
        "label.variants",
        "levels.north.variants",
    ),
    RedCase(
        "every-role",
        "spaced-region",
        "region",
        "label.variants_withheld",
        "levels.north.variants_withheld",
    ),
    RedCase(
        "every-role",
        "leading_zero-visits",
        "visits",
        "numeric.numeric_styles",
        f"styles.exact.{parsing.STYLE_LEADING_ZERO}",
    ),
    RedCase(
        "every-role",
        "leading_plus-visits",
        "visits",
        "numeric.numeric_styles",
        f"styles.exact.{parsing.STYLE_LEADING_PLUS}",
    ),
    RedCase(
        "every-role",
        "exponent_upper-amount",
        "amount",
        "numeric.numeric_styles",
        f"styles.exact.{parsing.STYLE_EXPONENT_UPPER}",
    ),
    # The same two forms on a column the whole-column restyle cannot
    # reach, missed by the publication floor's worth of cells rather
    # than by one (review item P3-V2-D-F2). Prefixing a `0` to a cell
    # that already carries a decimal point leaves it in the decimal
    # form, so `amount` needs an edit that writes the form outright --
    # and it needs the floor's worth of it, because a form under the
    # floor is one every description of the file pools away.
    RedCase(
        "every-role",
        "floor-zero-led-amount",
        "amount",
        "numeric.numeric_styles",
        f"styles.exact.{parsing.STYLE_LEADING_ZERO}",
    ),
    RedCase(
        "every-role",
        "floor-plussed-amount",
        "amount",
        "numeric.numeric_styles",
        f"styles.exact.{parsing.STYLE_LEADING_PLUS}",
    ),
    RedCase(
        "pooled",
        "noncanonical-reading",
        "reading",
        "numeric.numeric_styles",
        f"styles.canonical.{parsing.STYLE_DECIMAL}",
    ),
    RedCase(
        "spelled",
        "exponent_upper-reading",
        "reading",
        "numeric.numeric_styles",
        f"styles.at-least.{parsing.STYLE_EXPONENT_LOWER}",
    ),
    RedCase(
        "every-role",
        "moved-recorded_on",
        "recorded_on",
        "datetime.date_percentiles.min",
        "date-ladder.min",
    ),
    RedCase(
        "every-role",
        "timed-recorded_on",
        "recorded_on",
        "datetime.time_precision",
        "precision.time_precision",
    ),
    RedCase(
        "every-role",
        "subsecond-recorded_on",
        "recorded_on",
        "datetime.subsecond_digits",
        "counts.subsecond_digits",
    ),
    RedCase(
        "every-role",
        "one-worded-recorded_on",
        "recorded_on",
        "datetime.n_unparsed",
        "counts.n_unparsed",
    ),
    RedCase(
        "every-role",
        "mixed-recorded_on",
        "recorded_on",
        "datetime.earliest_utc_offset",
        "offsets.earliest",
    ),
    # THE NINE RUNGS BETWEEN THE ENDS, ON THEIR OWN TERMS (review item
    # P3-V3-F4). A file whose ladder is moved wholesale is caught by the
    # two ENDS, so the interior rungs could be asleep behind them and
    # nothing here would say so. `crushed` keeps both ends, the role,
    # the resolution and the precision exactly where the description
    # puts them and piles the middle low, so the only checks left to
    # catch it are the nine -- and on the quarter fixture the two counts
    # of how many different values the column holds, which were WITHHELD
    # on every file before this repair.
    RedCase(
        "every-role",
        "crushed-recorded_on",
        "recorded_on",
        "datetime.date_percentiles",
        "date-ladder.p50",
    ),
    RedCase(
        "quarters",
        "crushed-when",
        "when",
        "datetime.date_percentiles",
        "date-ladder.p50",
    ),
    RedCase(
        "quarters",
        "crushed-when",
        "when",
        "datetime.date_percentiles",
        "date-ladder.p99",
    ),
    RedCase(
        "quarters",
        "crushed-when",
        "when",
        "datetime.n_distinct",
        "distinct.n_distinct",
    ),
    RedCase(
        "quarters",
        "crushed-when",
        "when",
        "datetime.n_distinct_folded",
        "distinct.n_distinct_folded",
    ),
    RedCase(
        "quarters",
        "moved-when",
        "when",
        "datetime.date_percentiles.min",
        "date-ladder.min",
    ),
    RedCase("quarters", "moved-when", "when", "datetime.latest", "ends.latest"),
    RedCase(
        "quarters",
        "timed-when",
        "when",
        "datetime.resolution",
        "precision.resolution",
    ),
    RedCase(
        "quarters",
        "one-worded-when",
        "when",
        "datetime.n_unparsed",
        "counts.n_unparsed",
    ),
    RedCase(
        "every-role",
        "shortened-comment",
        "comment",
        "free_text.length.min",
        "length.min",
    ),
    RedCase(
        "every-role",
        "lengthened-comment",
        "comment",
        "free_text.words.max",
        "words.max",
    ),
    RedCase(
        "every-role",
        "repeated-record_code",
        "record_code",
        "identifier.n_distinct_by_occurrences",
        "distinct.n_distinct_by_occurrences",
    ),
    RedCase(
        "every-role",
        "digits-record_code",
        "record_code",
        "identifier.n_all_digits",
        "counts.n_all_digits",
    ),
    RedCase(
        "every-role",
        "filled-visits",
        "visits",
        "universal.n_missing",
        "presence.n_missing",
    ),
    RedCase(
        "every-role",
        "crowded-visits",
        "visits",
        "numeric.percentiles",
        "ladder.p50",
    ),
    RedCase(
        "every-role",
        "crowded-amount",
        "amount",
        "numeric.percentiles",
        "ladder.p90",
    ),
    RedCase(
        "every-role",
        "raised-amount",
        "amount",
        "numeric.percentiles.max",
        "ladder.max",
    ),
    RedCase("every-role", "zeroed-visits", "visits", "numeric.n_zero", "counts.n_zero"),
    RedCase(
        "every-role",
        "negated-visits",
        "visits",
        "numeric.n_negative",
        "counts.n_negative",
    ),
    RedCase(
        "every-role",
        "fractioned-visits",
        "visits",
        "numeric.integer_valued",
        "type.integer_valued",
    ),
    RedCase(
        "every-role",
        "contradicted-visits",
        "visits",
        "universal.n_contradictory",
        "counts.n_contradictory",
    ),
    RedCase(
        "every-role",
        "overflowed-visits",
        "visits",
        "universal.n_out_of_range",
        "counts.n_out_of_range",
    ),
    # FOUR OF THE TEN THE REGISTER OF GAPS CARRIED, all of them on the
    # numeric roles. Each is ONE cell in two hundred and forty, so the
    # column keeps the role the file's own description reads it as and
    # the disclosure gate stays open (review item P3-V2-B-F5).
    RedCase(
        "every-role",
        "one-worded-amount",
        "amount",
        "numeric.numeric_share",
        "counts.numeric_share",
    ),
    RedCase(
        "every-role",
        "one-overflowed-amount",
        "amount",
        "numeric.n_left_out_of_statistics",
        "counts.n_left_out_of_statistics",
    ),
    RedCase(
        "every-role",
        "one-underflowed-amount",
        "amount",
        "numeric.n_negative_unrepresentable",
        "counts.n_negative_unrepresentable",
    ),
    RedCase(
        "every-role",
        "vast-amount",
        "amount",
        "numeric.std_unrepresentable",
        "type.std_unrepresentable",
    ),
    RedCase(
        "every-role",
        "rewritten-recorded_on",
        "recorded_on",
        "universal.role",
        "axes.role",
    ),
    RedCase(
        "every-role",
        "rewritten-unused",
        "unused",
        "universal.n_present",
        "presence.n_present",
    ),
    RedCase(
        "every-role",
        "emptied-region",
        "region",
        "universal.quality_state",
        "axes.quality_state",
    ),
    RedCase(
        "unrepresentable",
        "rewritten-overflow",
        "overflow",
        "universal.role",
        "axes.role",
    ),
    RedCase(
        "unrepresentable",
        "blanked-overflow",
        "overflow",
        "universal.n_present",
        "presence.n_present",
    ),
    # ...and the three the register carried on the invention role, all
    # three of them one cell of the hundred and twenty (review item
    # P3-V2-B-F5). The last two are one edit: a bracketed negative is a
    # cell whose sign and whose wholeness are both unreadable, and the
    # register said an edit that changes a cell's class here changes the
    # role the file's own description reads the column as, which this
    # one does not.
    RedCase(
        "unrepresentable",
        "one-fractioned-overflow",
        "overflow",
        "numeric_unrepresentable.n_fraction",
        "counts.n_fraction",
    ),
    RedCase(
        "unrepresentable",
        "one-contradicted-overflow",
        "overflow",
        "numeric_unrepresentable.n_sign_unknown",
        "counts.n_sign_unknown",
    ),
    RedCase(
        "unrepresentable",
        "one-contradicted-overflow",
        "overflow",
        "numeric_unrepresentable.n_whole_unknown",
        "counts.n_whole_unknown",
    ),
    RedCase(
        "headerless",
        "written-header",
        "",
        "document.source.header_source",
        "header.presence",
    ),
    # ...AND THE SAME EDIT WITH ITS PRICE PAID (review item
    # P3-V2-C-F8). The check used to ask for a header line AND a row
    # count above the published one, so writing the header and dropping
    # one record defeated it and it reported "no header line, the first
    # row is a record" about a file whose first line was the published
    # names. Both cases are registered: the second is what proves the
    # conjunct is gone.
    RedCase(
        "headerless",
        "header-and-short",
        "",
        "document.source.header_source",
        "header.presence",
    ),
    RedCase("headerless", "swapped-1-2", "column_1", "universal.role", "axes.role"),
    RedCase(
        "headerless",
        "crowded-column_1",
        "column_1",
        "numeric.percentiles",
        "ladder.p25",
    ),
    RedCase(
        "headerless",
        "dropped-column",
        "column_2",
        "universal.position",
        "position.at",
    ),
    # EVERY NUMERIC COLUMN OF EVERY FIXTURE, on the subcheck that asks
    # whether a cell's text is a spelling of its own value at all
    # (review item P3-V2-C-F1). One named case per site, because the
    # whole finding was a check that held on one column while a
    # same-named one failed on another.
    RedCase(
        "every-role",
        "padded-visits",
        "visits",
        "numeric.numeric_styles",
        "styles.spelled",
    ),
    RedCase(
        "every-role",
        "padded-reading",
        "reading",
        "numeric.numeric_styles",
        "styles.spelled",
    ),
    RedCase(
        "every-role",
        "padded-amount",
        "amount",
        "numeric.numeric_styles",
        "styles.spelled",
    ),
    RedCase(
        "pooled",
        "padded-reading",
        "reading",
        "numeric.numeric_styles",
        "styles.spelled",
    ),
    RedCase(
        "spelled",
        "padded-reading",
        "reading",
        "numeric.numeric_styles",
        "styles.spelled",
    ),
    RedCase(
        "headerless",
        "padded-column_1",
        "column_1",
        "numeric.numeric_styles",
        "styles.spelled",
    ),
)


# THE REST OF THE REGISTRATION: one row for every shipped site the
# curated table above does not name (review item P3-V3-F7). Coverage is
# credited to a registered case and to nothing else, so the registration
# has to reach every entry the shipped validator files -- five hundred
# and eighty-eight of them across the six fixtures -- or the coverage
# identity says so by name.
#
# A row is (perturbation, subcheck), under the fixture and the column
# whose site it covers. The registry FACT is not written out a second
# time here: `test_no_two_sites_of_one_fixture_share_a_name` below
# asserts that no two sites of one fixture share a column and a
# subcheck, so the pair names exactly one entry of the shipped table and
# the fact comes off that entry. The curated rows above carry the fact
# in full, because a hand wrote each of them.
#
# HOW EACH ROW WAS CHOSEN, written down so a later hand chooses the same
# way: the NARROWEST edit that reaches the site, preferring one aimed at
# the site's own column. Among the perturbations that make the site
# miss, that is the one making the fewest others miss; where two tie, the
# first by name. Aiming is what keeps a site from being "covered" by an
# edit that destroyed some other column and took this one down with it,
# which is V8.2's own complaint at the grain of the identity, and
# `test_a_registered_case_is_aimed_at_the_site_it_covers` holds every
# row to it with the two exceptions named there.
COVERING_RED_CASES: "dict[str, dict[str, tuple[tuple[str, str], ...]]]" = {
    "every-role": {
        "": (
            ("added-column", "header.presence"),
        ),
        "amount": (
            ("contradicted-amount", "axes.quality_state"),
            ("rewritten-amount", "axes.role"),
            ("rewritten-amount", "axes.statistical_type"),
            ("contradicted-amount", "counts.n_contradictory"),
            ("one-negated-amount", "counts.n_negative"),
            ("rewritten-amount", "counts.n_not_numeric"),
            ("rewritten-amount", "counts.n_numeric"),
            ("one-overflowed-amount", "counts.n_out_of_range"),
            ("one-contradicted-amount", "counts.n_used_in_statistics"),
            ("one-zeroed-amount", "counts.n_zero"),
            # WHY THIS ROW MOVED OFF `spread-amount` (plan amendment
            # A-P3-18 clause 2). This column publishes 240 present cells
            # all written in the decimal form and 238 different values,
            # so its own permitted spellings can carry 240 identities and
            # method G12.8's envelope authorizes any count between the
            # two. The even spread writes 240 different values, which
            # that envelope holds, so the check now answers
            # AUTHORIZED-DEVIATION there and the site needs the narrowest
            # edit that still makes it MISS. Both `rewritten-amount` and
            # `worded-amount` make six subchecks miss; the rule above
            # takes the first by name.
            # The census of fraction widths (plan P4-D4.5). One cell
            # given a third figure after the point is the narrowest edit
            # there is: the column still publishes one width, and one
            # fewer cell wears it.
            ("one-fractioned-amount", "widths.published.2"),
            ("rewritten-amount", "distinct.n_distinct"),
            ("rewritten-amount", "distinct.n_distinct_folded"),
            ("one-negated-amount", "ladder.min"),
            ("negated-amount", "ladder.p01"),
            ("fractioned-amount", "ladder.p05"),
            ("fractioned-amount", "ladder.p10"),
            ("spread-amount", "ladder.p25"),
            ("floor-plussed-amount", "ladder.p50"),
            ("spread-amount", "ladder.p75"),
            ("crowded-amount", "ladder.p95"),
            ("crowded-amount", "ladder.p99"),
            ("raised-amount", "moments.mean"),
            ("raised-amount", "moments.skew"),
            ("raised-amount", "moments.std"),
            ("renamed-amount", "position.at"),
            ("emptied-amount", "presence.n_missing"),
            ("emptied-amount", "presence.n_present"),
            ("one-plussed-amount", "styles.at-least.decimal"),
            ("exponent_lower-amount", "styles.canonical.exponent_lower"),
            ("one-plussed-amount", "styles.published.decimal"),
            ("negated-amount", "styles.remainder"),
            ("exponent_upper-amount", "styles.spill"),
            ("vast-amount", "type.integer_valued"),
        ),
        "answer": (
            ("emptied-answer", "axes.quality_state"),
            ("emptied-answer", "axes.role"),
            ("emptied-answer", "axes.statistical_type"),
            ("one-contradicted-answer", "counts.n_contradictory"),
            ("blanked-answer", "counts.n_not_numeric"),
            ("one-bracketed-answer", "counts.n_numeric"),
            ("one-overflowed-answer", "counts.n_out_of_range"),
            ("spaced-answer", "distinct.n_distinct"),
            ("marked-answer", "distinct.n_distinct_folded"),
            ("marked-answer", "levels.no.count"),
            ("rewritten-answer", "levels.no.label"),
            ("recased-answer", "levels.no.variants"),
            ("spaced-answer", "levels.no.variants_withheld"),
            ("marked-answer", "levels.set"),
            ("blanked-answer", "levels.yes.count"),
            ("rewritten-answer", "levels.yes.label"),
            ("recased-answer", "levels.yes.variants"),
            ("spaced-answer", "levels.yes.variants_withheld"),
            ("renamed-answer", "position.at"),
            ("blanked-answer", "presence.n_missing"),
            ("blanked-answer", "presence.n_present"),
            ("one-worded-answer", "suppressed.counts"),
            ("one-worded-answer", "suppressed.suppressed_levels"),
            ("one-worded-answer", "suppressed.suppressed_rows"),
        ),
        "batch": (
            ("emptied-batch", "axes.quality_state"),
            ("emptied-batch", "axes.role"),
            ("emptied-batch", "axes.statistical_type"),
            ("one-contradicted-batch", "counts.n_contradictory"),
            ("blanked-batch", "counts.n_not_numeric"),
            ("one-bracketed-batch", "counts.n_numeric"),
            ("one-overflowed-batch", "counts.n_out_of_range"),
            ("spaced-batch", "distinct.n_distinct"),
            ("marked-batch", "distinct.n_distinct_folded"),
            ("blanked-batch", "levels.one.count"),
            ("rewritten-batch", "levels.one.label"),
            ("recased-batch", "levels.one.variants"),
            ("spaced-batch", "levels.one.variants_withheld"),
            ("marked-batch", "levels.set"),
            ("renamed-batch", "position.at"),
            ("blanked-batch", "presence.n_missing"),
            ("blanked-batch", "presence.n_present"),
            ("one-worded-batch", "suppressed.counts"),
            ("one-worded-batch", "suppressed.suppressed_levels"),
            ("one-worded-batch", "suppressed.suppressed_rows"),
        ),
        "comment": (
            ("emptied-comment", "axes.quality_state"),
            ("one-word-comment", "axes.role"),
            ("one-word-comment", "axes.statistical_type"),
            ("one-zero-led-comment", "counts.n_all_digits"),
            ("one-worded-comment", "counts.n_code_alphabet"),
            ("one-contradicted-comment", "counts.n_contradictory"),
            ("marked-comment", "counts.n_not_numeric"),
            ("one-bracketed-comment", "counts.n_numeric"),
            ("one-overflowed-comment", "counts.n_out_of_range"),
            ("marked-comment", "distinct.n_distinct"),
            ("marked-comment", "distinct.n_distinct_by_occurrences"),
            ("marked-comment", "distinct.n_distinct_folded"),
            ("lengthened-comment", "length.max"),
            ("marked-comment", "length.mean"),
            ("lengthened-comment", "length.p50"),
            ("renamed-comment", "position.at"),
            ("blanked-comment", "presence.n_missing"),
            ("blanked-comment", "presence.n_present"),
            ("one-worded-comment", "words.mean"),
            ("one-worded-comment", "words.min"),
        ),
        "dose": (
            # THE AFFIXED ROLE, and the edits divide the way its two
            # populations do. The pair is moved by three edits of its
            # own -- another piece of text in front, another behind,
            # and the floor's worth of cells with the pair taken off
            # -- and every quantitative site is moved by the numeric
            # edit the plain numeric columns above use, applied to the
            # CORES and put back inside the pair. So each row here is
            # aimed at the population its fact is about, which is the
            # whole of what this role adds. Its cores carry a POINT,
            # so the census of fraction widths is walked here too.
            ("renamed-dose", "position.at"),
            ("emptied-dose", "presence.n_present"),
            ("emptied-dose", "presence.n_missing"),
            ("contradicted-dose", "axes.role"),
            ("contradicted-dose", "axes.statistical_type"),
            ("emptied-dose", "axes.quality_state"),
            ("unaffixed-dose", "counts.n_numeric"),
            ("unaffixed-dose", "counts.n_not_numeric"),
            ("one-overflowed-dose", "counts.n_out_of_range"),
            ("one-contradicted-dose", "counts.n_contradictory"),
            ("contradicted-dose", "distinct.n_distinct"),
            ("contradicted-dose", "distinct.n_distinct_folded"),
            ("one-worded-dose", "counts.n_affixed"),
            ("prefixed-dose", "counts.affix_prefix"),
            ("suffixed-dose", "counts.affix_suffix"),
            ("one-worded-dose", "counts.n_core_numeric"),
            ("marked-dose", "counts.n_core_out_of_range"),
            ("marked-dose", "counts.n_core_contradictory"),
            ("marked-dose", "counts.n_core_not_numeric"),
            ("zeroed-dose", "counts.n_zero"),
            ("bracketed-dose", "counts.n_negative"),
            ("marked-dose", "counts.n_negative_unrepresentable"),
            ("one-worded-dose", "counts.n_used_in_statistics"),
            ("one-worded-dose", "counts.n_left_out_of_statistics"),
            ("vast-dose", "type.integer_valued"),
            ("vast-dose", "type.std_unrepresentable"),
            ("one-worded-dose", "counts.numeric_share"),
            ("fractioned-dose", "ladder.min"),
            ("raised-dose", "ladder.max"),
            ("fractioned-dose", "ladder.p01"),
            ("crowded-dose", "ladder.p05"),
            ("crowded-dose", "ladder.p10"),
            ("crowded-dose", "ladder.p25"),
            ("crowded-dose", "ladder.p50"),
            ("crowded-dose", "ladder.p75"),
            ("crowded-dose", "ladder.p90"),
            ("crowded-dose", "ladder.p95"),
            ("crowded-dose", "ladder.p99"),
            ("raised-dose", "moments.mean"),
            ("raised-dose", "moments.std"),
            ("raised-dose", "moments.skew"),
            ("floor-zero-led-dose", "styles.exact.leading_zero"),
            ("floor-plussed-dose", "styles.exact.leading_plus"),
            ("exponent_upper-dose", "styles.exact.exponent_upper"),
            ("prefixed-dose", "styles.at-least.decimal"),
            ("prefixed-dose", "styles.spill"),
            ("zeroed-dose", "styles.remainder"),
            ("noncanonical-dose", "styles.spelled"),
            ("exponent_lower-dose", "styles.canonical.exponent_lower"),
            ("exponent_lower-dose", "styles.published.decimal"),
            ("spread-dose", "widths.published.1"),
            ("spread-dose", "widths.published.2"),
        ),
        "seen_at": (
            # THE CLOCK ROLE. Three edits are its own: the two halves
            # of the ladder, piled low and piled high, because a rung
            # near the bottom is falsifiable only upward and one near
            # the top only downward; and every cell rewritten in the
            # OTHER form, which moves the published form and the four
            # values written in it without moving a single time.
            ("renamed-seen_at", "position.at"),
            ("blanked-seen_at", "presence.n_present"),
            ("blanked-seen_at", "presence.n_missing"),
            ("one-worded-seen_at", "axes.role"),
            ("one-worded-seen_at", "axes.statistical_type"),
            ("emptied-seen_at", "axes.quality_state"),
            ("one-bracketed-seen_at", "counts.n_numeric"),
            ("blanked-seen_at", "counts.n_not_numeric"),
            ("one-overflowed-seen_at", "counts.n_out_of_range"),
            ("one-contradicted-seen_at", "counts.n_contradictory"),
            ("one-worded-seen_at", "distinct.n_distinct"),
            ("one-worded-seen_at", "distinct.n_distinct_folded"),
            ("reformed-seen_at", "form.clock_form"),
            ("reformed-seen_at", "ends.earliest"),
            ("reformed-seen_at", "ends.latest"),
            ("marked-seen_at", "counts.n_unparsed"),
            ("reformed-seen_at", "clock-ladder.min"),
            ("reformed-seen_at", "clock-ladder.max"),
            ("lifted-seen_at", "clock-ladder.p01"),
            ("crushed-seen_at", "clock-ladder.p05"),
            ("crushed-seen_at", "clock-ladder.p10"),
            ("crushed-seen_at", "clock-ladder.p25"),
            ("crushed-seen_at", "clock-ladder.p50"),
            ("crushed-seen_at", "clock-ladder.p75"),
            ("crushed-seen_at", "clock-ladder.p90"),
            ("crushed-seen_at", "clock-ladder.p95"),
            ("crushed-seen_at", "clock-ladder.p99"),
        ),
        "reading": (
            ("contradicted-reading", "axes.quality_state"),
            ("one-negated-reading", "axes.role"),
            ("one-negated-reading", "axes.statistical_type"),
            ("contradicted-reading", "counts.n_contradictory"),
            ("filled-overflowed-reading", "counts.n_left_out_of_statistics"),
            ("one-negated-reading", "counts.n_negative"),
            ("filled-underflowed-reading", "counts.n_negative_unrepresentable"),
            ("worded-reading", "counts.n_not_numeric"),
            ("filled-plussed-reading", "counts.n_numeric"),
            ("filled-overflowed-reading", "counts.n_out_of_range"),
            ("filled-plussed-reading", "counts.n_used_in_statistics"),
            ("one-zeroed-reading", "counts.n_zero"),
            ("filled-worded-reading", "counts.numeric_share"),
            ("emptied-reading", "distinct.n_distinct"),
            ("emptied-reading", "distinct.n_distinct_folded"),
            ("raised-reading", "ladder.max"),
            ("one-zeroed-reading", "ladder.min"),
            ("zeroed-reading", "ladder.p01"),
            ("zeroed-reading", "ladder.p05"),
            ("zeroed-reading", "ladder.p10"),
            ("zeroed-reading", "ladder.p25"),
            ("zeroed-reading", "ladder.p50"),
            ("enormous-reading", "ladder.p75"),
            ("spread-reading", "ladder.p90"),
            ("enormous-reading", "ladder.p95"),
            ("enormous-reading", "ladder.p99"),
            ("raised-reading", "moments.mean"),
            ("raised-reading", "moments.skew"),
            ("raised-reading", "moments.std"),
            ("renamed-reading", "position.at"),
            ("filled-overflowed-reading", "presence.n_missing"),
            ("filled-overflowed-reading", "presence.n_present"),
            ("one-plussed-reading", "styles.at-least.plain"),
            ("noncanonical-reading", "styles.canonical.decimal"),
            ("exponent_lower-reading", "styles.canonical.exponent_lower"),
            ("exponent_upper-reading", "styles.exact.exponent_upper"),
            ("leading_plus-reading", "styles.exact.leading_plus"),
            ("leading_zero-reading", "styles.exact.leading_zero"),
            ("one-plussed-reading", "styles.published.plain"),
            ("one-plussed-reading", "styles.remainder"),
            ("exponent_lower-reading", "styles.spill"),
            ("one-fractioned-reading", "type.integer_valued"),
            ("vast-reading", "type.std_unrepresentable"),
        ),
        "record_code": (
            ("emptied-record_code", "axes.quality_state"),
            ("renamed-record_code", "axes.role"),
            ("renamed-record_code", "axes.statistical_type"),
            ("one-bracketed-record_code", "counts.n_code_alphabet"),
            ("one-contradicted-record_code", "counts.n_contradictory"),
            ("one-tiny-record_code", "counts.n_not_numeric"),
            ("one-negated-record_code", "counts.n_numeric"),
            ("one-tiny-record_code", "counts.n_out_of_range"),
            ("marked-record_code", "distinct.n_distinct"),
            ("marked-record_code", "distinct.n_distinct_folded"),
            ("repeated-record_code", "length.max"),
            ("blanked-record_code", "presence.n_missing"),
            ("digits-record_code", "type.all_whole_numbers"),
        ),
        "recorded_on": (
            ("emptied-recorded_on", "axes.quality_state"),
            ("rewritten-recorded_on", "axes.statistical_type"),
            ("one-contradicted-recorded_on", "counts.n_contradictory"),
            ("blanked-recorded_on", "counts.n_not_numeric"),
            ("one-bracketed-recorded_on", "counts.n_numeric"),
            ("one-overflowed-recorded_on", "counts.n_out_of_range"),
            ("moved-recorded_on", "date-ladder.max"),
            ("moved-recorded_on", "date-ladder.p01"),
            ("crushed-recorded_on", "date-ladder.p05"),
            ("crushed-recorded_on", "date-ladder.p10"),
            ("crushed-recorded_on", "date-ladder.p25"),
            ("crushed-recorded_on", "date-ladder.p75"),
            ("crushed-recorded_on", "date-ladder.p90"),
            ("crushed-recorded_on", "date-ladder.p95"),
            ("crushed-recorded_on", "date-ladder.p99"),
            ("rewritten-recorded_on", "distinct.n_distinct"),
            ("rewritten-recorded_on", "distinct.n_distinct_folded"),
            ("moved-recorded_on", "ends.earliest"),
            ("moved-recorded_on", "ends.latest"),
            ("one-worded-recorded_on", "offsets.(none)"),
            ("offset-recorded_on", "offsets.latest"),
            ("mixed-recorded_on", "offsets.read-at"),
            ("renamed-recorded_on", "position.at"),
            ("timed-recorded_on", "precision.resolution"),
            ("blanked-recorded_on", "presence.n_missing"),
            ("blanked-recorded_on", "presence.n_present"),
        ),
        "note": (
            ("reshaped-note", "forms.published.AAAAAA"),
            ("reshaped-note", "forms.published.AAAAAAAA"),
            # THE LONG-TAIL ROLE (plan P4-D5). It publishes the four
            # shared label keys and no key of its own, so its
            # obligations are the label family's -- and each of them
            # is falsified by an edit to THIS column, never by the
            # column going missing.
            ("emptied-note", "axes.quality_state"),
            ("emptied-note", "axes.role"),
            ("emptied-note", "axes.statistical_type"),
            ("one-contradicted-note", "counts.n_contradictory"),
            ("blanked-note", "counts.n_not_numeric"),
            ("one-zeroed-note", "counts.n_numeric"),
            ("one-tiny-note", "counts.n_out_of_range"),
            ("marked-note", "distinct.n_distinct"),
            ("marked-note", "distinct.n_distinct_folded"),
            ("rewritten-note", "levels.clinic.count"),
            ("rewritten-note", "levels.clinic.label"),
            ("rewritten-note", "levels.clinic.variants"),
            ("rewritten-note", "levels.clinic.variants_withheld"),
            ("marked-note", "levels.referral.count"),
            ("marked-note", "levels.referral.label"),
            ("marked-note", "levels.referral.variants"),
            ("marked-note", "levels.referral.variants_withheld"),
            ("marked-note", "levels.set"),
            ("renamed-note", "position.at"),
            ("blanked-note", "presence.n_missing"),
            ("blanked-note", "presence.n_present"),
            ("marked-note", "suppressed.counts"),
            ("marked-note", "suppressed.suppressed_levels"),
            ("blanked-note", "suppressed.suppressed_rows"),
        ),
        "region": (
            ("emptied-region", "axes.role"),
            ("emptied-region", "axes.statistical_type"),
            ("one-contradicted-region", "counts.n_contradictory"),
            ("blanked-region", "counts.n_not_numeric"),
            ("one-bracketed-region", "counts.n_numeric"),
            ("one-overflowed-region", "counts.n_out_of_range"),
            ("one-worded-region", "distinct.n_distinct"),
            ("one-worded-region", "distinct.n_distinct_folded"),
            ("marked-region", "levels.east.count"),
            ("rewritten-region", "levels.east.label"),
            ("recased-region", "levels.east.variants"),
            ("spaced-region", "levels.east.variants_withheld"),
            ("blanked-region", "levels.north.count"),
            ("rewritten-region", "levels.north.label"),
            ("marked-region", "levels.set"),
            ("marked-region", "levels.south.count"),
            ("rewritten-region", "levels.south.label"),
            ("recased-region", "levels.south.variants"),
            ("spaced-region", "levels.south.variants_withheld"),
            ("marked-region", "levels.west.count"),
            ("rewritten-region", "levels.west.label"),
            ("recased-region", "levels.west.variants"),
            ("spaced-region", "levels.west.variants_withheld"),
            ("renamed-region", "position.at"),
            ("blanked-region", "presence.n_missing"),
            ("blanked-region", "presence.n_present"),
            ("one-worded-region", "suppressed.counts"),
            ("one-worded-region", "suppressed.suppressed_levels"),
            ("one-worded-region", "suppressed.suppressed_rows"),
        ),
        "unused": (
            ("filled-bracketed-unused", "axes.quality_state"),
            ("filled-bracketed-unused", "axes.role"),
            ("filled-bracketed-unused", "axes.statistical_type"),
            ("filled-contradicted-unused", "counts.n_contradictory"),
            ("filled-worded-unused", "counts.n_not_numeric"),
            ("filled-bracketed-unused", "counts.n_numeric"),
            ("filled-overflowed-unused", "counts.n_out_of_range"),
            ("filled-bracketed-unused", "distinct.n_distinct"),
            ("filled-bracketed-unused", "distinct.n_distinct_folded"),
            ("renamed-unused", "position.at"),
            ("filled-bracketed-unused", "presence.n_missing"),
        ),
        "visits": (
            ("contradicted-visits", "axes.quality_state"),
            ("one-negated-visits", "axes.role"),
            ("one-negated-visits", "axes.statistical_type"),
            ("filled-overflowed-visits", "counts.n_left_out_of_statistics"),
            ("filled-underflowed-visits", "counts.n_negative_unrepresentable"),
            ("worded-visits", "counts.n_not_numeric"),
            ("filled-plussed-visits", "counts.n_numeric"),
            ("filled-plussed-visits", "counts.n_used_in_statistics"),
            ("filled-worded-visits", "counts.numeric_share"),
            ("emptied-visits", "distinct.n_distinct"),
            ("emptied-visits", "distinct.n_distinct_folded"),
            ("raised-visits", "ladder.max"),
            ("one-negated-visits", "ladder.min"),
            ("negated-visits", "ladder.p01"),
            ("negated-visits", "ladder.p05"),
            ("marked-visits", "ladder.p10"),
            ("crowded-visits", "ladder.p25"),
            ("crowded-visits", "ladder.p75"),
            ("crowded-visits", "ladder.p90"),
            ("enormous-visits", "ladder.p95"),
            ("enormous-visits", "ladder.p99"),
            ("raised-visits", "moments.mean"),
            ("raised-visits", "moments.std"),
            ("renamed-visits", "position.at"),
            ("filled-overflowed-visits", "presence.n_present"),
            ("one-plussed-visits", "styles.at-least.plain"),
            ("noncanonical-visits", "styles.canonical.decimal"),
            ("exponent_lower-visits", "styles.canonical.exponent_lower"),
            ("exponent_upper-visits", "styles.exact.exponent_upper"),
            ("one-plussed-visits", "styles.published.plain"),
            ("one-plussed-visits", "styles.remainder"),
            ("exponent_lower-visits", "styles.spill"),
            ("marked-visits", "type.std_unrepresentable"),
        ),
    },
    "unrepresentable": {
        "": (
            ("byte-order-mark", "bytes.byte-order-mark"),
            ("carriage-returns", "bytes.line-endings"),
            ("no-terminal-newline", "bytes.terminal-newline"),
            ("not-utf8", "bytes.utf8"),
            ("added-column", "columns.n_columns"),
            ("added-column", "columns.order"),
            ("added-column", "header.names"),
            ("added-column", "header.presence"),
            ("added-row", "rows.n_rows"),
        ),
        "overflow": (
            ("rewritten-overflow", "axes.quality_state"),
            ("rewritten-overflow", "axes.statistical_type"),
            ("one-contradicted-overflow", "counts.n_contradictory"),
            ("marked-overflow", "counts.n_negative"),
            ("one-worded-overflow", "counts.n_not_numeric"),
            ("one-bracketed-overflow", "counts.n_numeric"),
            ("marked-overflow", "counts.n_out_of_range"),
            ("marked-overflow", "counts.n_positive"),
            ("marked-overflow", "counts.n_whole"),
            ("one-underflowed-overflow", "distinct.n_distinct"),
            ("one-underflowed-overflow", "distinct.n_distinct_by_occurrences"),
            ("one-underflowed-overflow", "distinct.n_distinct_folded"),
            ("renamed-overflow", "position.at"),
            ("blanked-overflow", "presence.n_missing"),
        ),
    },
    # THE PADDED-CODE FIXTURE (P4-D14). Its one column publishes a named
    # field width, which is what binds `numeric.pad_widths` to an
    # executable subcheck; before it, that fact was in the registry and
    # in no check any fixture reached.
    # THE SHAPED-TEXT FIXTURE (P4-D18). Its free-text column publishes
    # a named form, which is what binds `free_text.shape_forms` to an
    # executable subcheck; before it, that fact was in the registry and
    # in no check any fixture reached.
    "shaped-text": {
        "": (
            ("byte-order-mark", "bytes.byte-order-mark"),
            ("carriage-returns", "bytes.line-endings"),
            ("no-terminal-newline", "bytes.terminal-newline"),
            ("not-utf8", "bytes.utf8"),
            ("added-column", "columns.n_columns"),
            ("added-column", "columns.order"),
            ("added-column", "header.names"),
            ("added-column", "header.presence"),
            ("added-row", "rows.n_rows"),
        ),
        "lab_code": (
            ("emptied-lab_code", "axes.quality_state"),
            ("emptied-lab_code", "axes.role"),
            ("emptied-lab_code", "axes.statistical_type"),
            ("one-zero-led-lab_code", "counts.n_all_digits"),
            ("blanked-lab_code", "counts.n_code_alphabet"),
            ("one-contradicted-lab_code", "counts.n_contradictory"),
            ("blanked-lab_code", "counts.n_not_numeric"),
            ("one-bracketed-lab_code", "counts.n_numeric"),
            ("one-overflowed-lab_code", "counts.n_out_of_range"),
            ("blanked-lab_code", "distinct.n_distinct"),
            ("blanked-lab_code", "distinct.n_distinct_by_occurrences"),
            ("blanked-lab_code", "distinct.n_distinct_folded"),
            ("blanked-lab_code", "forms.published.9999-9"),
            ("lengthened-lab_code", "length.max"),
            ("lengthened-lab_code", "length.mean"),
            ("lengthened-lab_code", "length.min"),
            ("lengthened-lab_code", "length.p50"),
            ("renamed-lab_code", "position.at"),
            ("blanked-lab_code", "presence.n_missing"),
            ("blanked-lab_code", "presence.n_present"),
            ("lengthened-lab_code", "words.max"),
            ("lengthened-lab_code", "words.mean"),
            ("lengthened-lab_code", "words.min"),
        ),
        "region": (
            ("emptied-region", "axes.quality_state"),
            ("emptied-region", "axes.role"),
            ("emptied-region", "axes.statistical_type"),
            ("one-contradicted-region", "counts.n_contradictory"),
            ("blanked-region", "counts.n_not_numeric"),
            ("one-bracketed-region", "counts.n_numeric"),
            ("one-overflowed-region", "counts.n_out_of_range"),
            ("emptied-region", "distinct.n_distinct"),
            ("emptied-region", "distinct.n_distinct_folded"),
            ("marked-region", "levels.east.count"),
            ("reshaped-region", "levels.east.label"),
            ("marked-region", "levels.east.variants"),
            ("reshaped-region", "levels.east.variants_withheld"),
            ("blanked-region", "levels.north.count"),
            ("reshaped-region", "levels.north.label"),
            ("blanked-region", "levels.north.variants"),
            ("reshaped-region", "levels.north.variants_withheld"),
            ("marked-region", "levels.set"),
            ("marked-region", "levels.south.count"),
            ("reshaped-region", "levels.south.label"),
            ("marked-region", "levels.south.variants"),
            ("reshaped-region", "levels.south.variants_withheld"),
            ("marked-region", "levels.west.count"),
            ("reshaped-region", "levels.west.label"),
            ("marked-region", "levels.west.variants"),
            ("reshaped-region", "levels.west.variants_withheld"),
            ("renamed-region", "position.at"),
            ("blanked-region", "presence.n_missing"),
            ("blanked-region", "presence.n_present"),
            ("one-bracketed-region", "suppressed.counts"),
            ("one-bracketed-region", "suppressed.suppressed_levels"),
            ("one-bracketed-region", "suppressed.suppressed_rows"),
        ),
    },
    "padded-codes": {
        "": (
            ("byte-order-mark", "bytes.byte-order-mark"),
            ("carriage-returns", "bytes.line-endings"),
            ("no-terminal-newline", "bytes.terminal-newline"),
            ("not-utf8", "bytes.utf8"),
            ("added-column", "columns.n_columns"),
            ("added-column", "columns.order"),
            ("added-column", "header.names"),
            ("added-column", "header.presence"),
            ("added-row", "rows.n_rows"),
        ),
        "code": (
            # THE CENSUS CATCHES WHAT THE FORMS MAP CANNOT, and this
            # row is that claim made executable: `leading_zero-code`
            # writes every cell one figure wider WITHOUT leaving the
            # leading-zero style, so the forms map still balances and
            # only the width census goes red (P4-D14).
            ("contradicted-code", "axes.quality_state"),
            ("bracketed-code", "axes.role"),
            ("bracketed-code", "axes.statistical_type"),
            ("contradicted-code", "counts.n_contradictory"),
            ("marked-code", "counts.n_left_out_of_statistics"),
            ("bracketed-code", "counts.n_negative"),
            ("marked-code", "counts.n_negative_unrepresentable"),
            ("marked-code", "counts.n_not_numeric"),
            ("blanked-code", "counts.n_numeric"),
            ("one-overflowed-code", "counts.n_out_of_range"),
            ("blanked-code", "counts.n_used_in_statistics"),
            ("floor-plussed-code", "counts.n_zero"),
            ("marked-code", "counts.numeric_share"),
            ("enormous-code", "ladder.max"),
            ("bracketed-code", "ladder.min"),
            ("bracketed-code", "ladder.p01"),
            ("marked-code", "ladder.p05"),
            ("crowded-code", "ladder.p10"),
            ("crowded-code", "ladder.p25"),
            ("crowded-code", "ladder.p50"),
            ("crowded-code", "ladder.p75"),
            ("crowded-code", "ladder.p90"),
            ("crowded-code", "ladder.p95"),
            ("enormous-code", "ladder.p99"),
            ("crowded-code", "moments.mean"),
            ("marked-code", "moments.skew"),
            ("enormous-code", "moments.std"),
            ("leading_zero-code", "pads.published.5"),
            ("renamed-code", "position.at"),
            ("blanked-code", "presence.n_missing"),
            ("blanked-code", "presence.n_present"),
            ("crowded-code", "styles.canonical.decimal"),
            ("enormous-code", "styles.canonical.exponent_lower"),
            ("exponent_upper-code", "styles.exact.exponent_upper"),
            ("floor-plussed-code", "styles.exact.leading_plus"),
            ("blanked-code", "styles.exact.leading_zero"),
            ("blanked-code", "styles.published.leading_zero"),
            ("crowded-code", "styles.remainder"),
            ("bracketed-code", "styles.spelled"),
            ("crowded-code", "styles.spill"),
            ("crowded-code", "type.integer_valued"),
            ("marked-code", "type.std_unrepresentable"),
        ),
    },
    "pooled": {
        "": (
            ("byte-order-mark", "bytes.byte-order-mark"),
            ("carriage-returns", "bytes.line-endings"),
            ("no-terminal-newline", "bytes.terminal-newline"),
            ("not-utf8", "bytes.utf8"),
            ("added-column", "columns.n_columns"),
            ("added-column", "columns.order"),
            ("added-column", "header.names"),
            ("added-column", "header.presence"),
            ("added-row", "rows.n_rows"),
        ),
        "reading": (
            ("contradicted-reading", "axes.quality_state"),
            ("one-worded-reading", "axes.role"),
            ("one-worded-reading", "axes.statistical_type"),
            ("contradicted-reading", "counts.n_contradictory"),
            ("marked-reading", "counts.n_left_out_of_statistics"),
            ("one-negated-reading", "counts.n_negative"),
            ("marked-reading", "counts.n_negative_unrepresentable"),
            ("one-worded-reading", "counts.n_not_numeric"),
            ("one-worded-reading", "counts.n_numeric"),
            ("one-overflowed-reading", "counts.n_out_of_range"),
            ("blanked-reading", "counts.n_used_in_statistics"),
            ("one-zeroed-reading", "counts.n_zero"),
            ("marked-reading", "counts.numeric_share"),
            # WHY THESE TWO ROWS MOVED OFF `fractioned-reading` (plan
            # amendment A-P3-18 clause 2). This column's style map is
            # partly pooled -- two cells whose form the floor held back
            # -- so its own permitted spellings settle the count of
            # different values no closer than a range, and G12.8's
            # envelope is what the two facts owe. Writing fractions into
            # some cells lands inside that range; the even spread and
            # the compression do not, and the rule above takes the
            # narrower of the two.
            ("spread-reading", "distinct.n_distinct"),
            ("spread-reading", "distinct.n_distinct_folded"),
            ("raised-reading", "ladder.max"),
            ("one-negated-reading", "ladder.min"),
            ("one-negated-reading", "ladder.p01"),
            ("negated-reading", "ladder.p05"),
            ("vast-reading", "ladder.p10"),
            ("enormous-reading", "ladder.p25"),
            ("crowded-reading", "ladder.p50"),
            ("crowded-reading", "ladder.p75"),
            ("enormous-reading", "ladder.p90"),
            ("enormous-reading", "ladder.p95"),
            ("raised-reading", "ladder.p99"),
            ("raised-reading", "moments.mean"),
            ("raised-reading", "moments.std"),
            ("renamed-reading", "position.at"),
            ("blanked-reading", "presence.n_missing"),
            ("blanked-reading", "presence.n_present"),
            ("fractioned-reading", "styles.at-least.plain"),
            ("exponent_lower-reading", "styles.canonical.exponent_lower"),
            ("exponent_upper-reading", "styles.exact.exponent_upper"),
            ("leading_plus-reading", "styles.exact.leading_plus"),
            ("leading_zero-reading", "styles.exact.leading_zero"),
            ("fractioned-reading", "styles.published.plain"),
            ("leading_plus-reading", "styles.remainder"),
            ("exponent_lower-reading", "styles.spill"),
            ("vast-reading", "type.integer_valued"),
            ("vast-reading", "type.std_unrepresentable"),
        ),
    },
    "spelled": {
        "": (
            ("byte-order-mark", "bytes.byte-order-mark"),
            ("carriage-returns", "bytes.line-endings"),
            ("no-terminal-newline", "bytes.terminal-newline"),
            ("not-utf8", "bytes.utf8"),
            ("added-column", "columns.n_columns"),
            ("added-column", "columns.order"),
            ("added-column", "header.names"),
            ("added-column", "header.presence"),
            ("added-row", "rows.n_rows"),
        ),
        "reading": (
            ("one-contradicted-reading", "axes.quality_state"),
            ("one-worded-reading", "axes.role"),
            ("one-worded-reading", "axes.statistical_type"),
            ("one-contradicted-reading", "counts.n_contradictory"),
            ("marked-reading", "counts.n_left_out_of_statistics"),
            ("one-underflowed-reading", "counts.n_negative"),
            ("marked-reading", "counts.n_negative_unrepresentable"),
            ("one-worded-reading", "counts.n_not_numeric"),
            ("one-worded-reading", "counts.n_numeric"),
            ("one-overflowed-reading", "counts.n_out_of_range"),
            ("blanked-reading", "counts.n_used_in_statistics"),
            ("one-zeroed-reading", "counts.n_zero"),
            ("marked-reading", "counts.numeric_share"),
            ("rewritten-reading", "distinct.n_distinct"),
            ("rewritten-reading", "distinct.n_distinct_folded"),
            ("one-fractioned-reading", "ladder.max"),
            ("one-zeroed-reading", "ladder.min"),
            ("one-zeroed-reading", "ladder.p01"),
            ("zeroed-reading", "ladder.p05"),
            ("crowded-reading", "ladder.p10"),
            ("crowded-reading", "ladder.p25"),
            ("crowded-reading", "ladder.p50"),
            ("crowded-reading", "ladder.p75"),
            ("crowded-reading", "ladder.p90"),
            ("crowded-reading", "ladder.p95"),
            ("one-fractioned-reading", "ladder.p99"),
            ("one-fractioned-reading", "moments.mean"),
            ("one-fractioned-reading", "moments.skew"),
            ("one-fractioned-reading", "moments.std"),
            ("renamed-reading", "position.at"),
            ("blanked-reading", "presence.n_missing"),
            ("blanked-reading", "presence.n_present"),
            ("noncanonical-reading", "styles.canonical.decimal"),
            ("exponent_upper-reading", "styles.exact.exponent_upper"),
            ("floor-plussed-reading", "styles.exact.leading_plus"),
            ("floor-zero-led-reading", "styles.exact.leading_zero"),
            ("spread-reading", "styles.published.exponent_lower"),
            ("added-row", "styles.remainder"),
            ("exponent_upper-reading", "styles.spill"),
            ("vast-reading", "type.integer_valued"),
            ("vast-reading", "type.std_unrepresentable"),
        ),
    },
    "quarters": {
        "": (
            ("byte-order-mark", "bytes.byte-order-mark"),
            ("carriage-returns", "bytes.line-endings"),
            ("no-terminal-newline", "bytes.terminal-newline"),
            ("not-utf8", "bytes.utf8"),
            ("added-column", "columns.n_columns"),
            ("added-column", "columns.order"),
            ("added-column", "header.names"),
            ("added-column", "header.presence"),
            ("added-row", "rows.n_rows"),
        ),
        "region": (
            ("emptied-region", "axes.quality_state"),
            ("emptied-region", "axes.role"),
            ("emptied-region", "axes.statistical_type"),
            ("one-contradicted-region", "counts.n_contradictory"),
            ("blanked-region", "counts.n_not_numeric"),
            ("one-bracketed-region", "counts.n_numeric"),
            ("one-overflowed-region", "counts.n_out_of_range"),
            ("one-worded-region", "distinct.n_distinct"),
            ("one-worded-region", "distinct.n_distinct_folded"),
            ("marked-region", "levels.east.count"),
            ("rewritten-region", "levels.east.label"),
            ("recased-region", "levels.east.variants"),
            ("spaced-region", "levels.east.variants_withheld"),
            ("marked-region", "levels.north.count"),
            ("rewritten-region", "levels.north.label"),
            ("recased-region", "levels.north.variants"),
            ("spaced-region", "levels.north.variants_withheld"),
            ("marked-region", "levels.set"),
            ("blanked-region", "levels.south.count"),
            ("rewritten-region", "levels.south.label"),
            ("recased-region", "levels.south.variants"),
            ("spaced-region", "levels.south.variants_withheld"),
            ("marked-region", "levels.west.count"),
            ("rewritten-region", "levels.west.label"),
            ("recased-region", "levels.west.variants"),
            ("spaced-region", "levels.west.variants_withheld"),
            ("renamed-region", "position.at"),
            ("blanked-region", "presence.n_missing"),
            ("blanked-region", "presence.n_present"),
            ("one-worded-region", "suppressed.counts"),
            ("one-worded-region", "suppressed.suppressed_levels"),
            ("one-worded-region", "suppressed.suppressed_rows"),
        ),
        "when": (
            ("emptied-when", "axes.quality_state"),
            ("rewritten-when", "axes.role"),
            ("rewritten-when", "axes.statistical_type"),
            ("one-contradicted-when", "counts.n_contradictory"),
            ("blanked-when", "counts.n_not_numeric"),
            ("one-bracketed-when", "counts.n_numeric"),
            ("one-overflowed-when", "counts.n_out_of_range"),
            ("subsecond-when", "counts.subsecond_digits"),
            ("timed-when", "date-ladder.max"),
            ("moved-when", "date-ladder.p01"),
            ("moved-when", "date-ladder.p05"),
            ("lifted-when", "date-ladder.p10"),
            ("crushed-when", "date-ladder.p25"),
            ("crushed-when", "date-ladder.p75"),
            ("crushed-when", "date-ladder.p90"),
            ("crushed-when", "date-ladder.p95"),
            ("timed-when", "ends.earliest"),
            ("blanked-when", "offsets.(none)"),
            ("offset-when", "offsets.earliest"),
            ("offset-when", "offsets.latest"),
            ("mixed-when", "offsets.read-at"),
            ("renamed-when", "position.at"),
            ("timed-when", "precision.time_precision"),
            ("blanked-when", "presence.n_missing"),
            ("blanked-when", "presence.n_present"),
        ),
    },
    "headerless": {
        "": (
            ("byte-order-mark", "bytes.byte-order-mark"),
            ("carriage-returns", "bytes.line-endings"),
            ("no-terminal-newline", "bytes.terminal-newline"),
            ("not-utf8", "bytes.utf8"),
            ("added-column", "columns.n_columns"),
            ("added-row", "rows.n_rows"),
        ),
        "column_1": (
            ("contradicted-column_1", "axes.quality_state"),
            ("one-worded-column_1", "axes.statistical_type"),
            ("contradicted-column_1", "counts.n_contradictory"),
            ("marked-column_1", "counts.n_left_out_of_statistics"),
            ("one-negated-column_1", "counts.n_negative"),
            ("marked-column_1", "counts.n_negative_unrepresentable"),
            ("one-worded-column_1", "counts.n_not_numeric"),
            ("one-worded-column_1", "counts.n_numeric"),
            ("one-overflowed-column_1", "counts.n_out_of_range"),
            ("blanked-column_1", "counts.n_used_in_statistics"),
            ("one-zeroed-column_1", "counts.n_zero"),
            ("marked-column_1", "counts.numeric_share"),
            ("emptied-column_1", "distinct.n_distinct"),
            ("emptied-column_1", "distinct.n_distinct_folded"),
            ("raised-column_1", "ladder.max"),
            ("one-zeroed-column_1", "ladder.min"),
            ("zeroed-column_1", "ladder.p01"),
            ("zeroed-column_1", "ladder.p05"),
            ("floor-plussed-column_1", "ladder.p10"),
            ("floor-plussed-column_1", "ladder.p50"),
            ("floor-plussed-column_1", "ladder.p75"),
            ("crowded-column_1", "ladder.p90"),
            ("crowded-column_1", "ladder.p95"),
            ("raised-column_1", "ladder.p99"),
            ("floor-plussed-column_1", "moments.mean"),
            ("raised-column_1", "moments.skew"),
            ("raised-column_1", "moments.std"),
            ("blanked-column_1", "presence.n_missing"),
            ("blanked-column_1", "presence.n_present"),
            ("one-plussed-column_1", "styles.at-least.plain"),
            ("noncanonical-column_1", "styles.canonical.decimal"),
            ("exponent_lower-column_1", "styles.canonical.exponent_lower"),
            ("exponent_upper-column_1", "styles.exact.exponent_upper"),
            ("leading_plus-column_1", "styles.exact.leading_plus"),
            ("leading_zero-column_1", "styles.exact.leading_zero"),
            ("one-plussed-column_1", "styles.published.plain"),
            ("one-plussed-column_1", "styles.remainder"),
            ("exponent_lower-column_1", "styles.spill"),
            ("fractioned-column_1", "type.integer_valued"),
            ("vast-column_1", "type.std_unrepresentable"),
        ),
        "column_2": (
            ("emptied-column_2", "axes.quality_state"),
            ("emptied-column_2", "axes.role"),
            ("emptied-column_2", "axes.statistical_type"),
            ("one-contradicted-column_2", "counts.n_contradictory"),
            ("blanked-column_2", "counts.n_not_numeric"),
            ("one-bracketed-column_2", "counts.n_numeric"),
            ("one-overflowed-column_2", "counts.n_out_of_range"),
            ("one-worded-column_2", "distinct.n_distinct"),
            ("one-worded-column_2", "distinct.n_distinct_folded"),
            ("marked-column_2", "levels.east.count"),
            ("rewritten-column_2", "levels.east.label"),
            ("recased-column_2", "levels.east.variants"),
            ("spaced-column_2", "levels.east.variants_withheld"),
            ("marked-column_2", "levels.north.count"),
            ("rewritten-column_2", "levels.north.label"),
            ("recased-column_2", "levels.north.variants"),
            ("spaced-column_2", "levels.north.variants_withheld"),
            ("marked-column_2", "levels.set"),
            ("blanked-column_2", "levels.south.count"),
            ("rewritten-column_2", "levels.south.label"),
            ("recased-column_2", "levels.south.variants"),
            ("spaced-column_2", "levels.south.variants_withheld"),
            ("marked-column_2", "levels.west.count"),
            ("rewritten-column_2", "levels.west.label"),
            ("recased-column_2", "levels.west.variants"),
            ("spaced-column_2", "levels.west.variants_withheld"),
            ("blanked-column_2", "presence.n_missing"),
            ("blanked-column_2", "presence.n_present"),
            ("one-worded-column_2", "suppressed.counts"),
            ("one-worded-column_2", "suppressed.suppressed_levels"),
            ("one-worded-column_2", "suppressed.suppressed_rows"),
        ),
    },
}

# ---------------------------------------------------------------------
# WHAT GOVERNS EACH SITE, WRITTEN HERE AND NOWHERE ELSE (review item
# P3-V4-F6)
# ---------------------------------------------------------------------
#
# THE DEFECT THIS CLOSES. A covering row named its site by column and
# subcheck, and the registration then read the third term of the
# identity -- the REGISTRY FACT -- off the shipped validator's own
# output. So the expected side of the proof was a copy of the subject
# of the proof: production could bind `date-ladder.p05` to
# `datetime.n_distinct` instead of `datetime.date_percentiles`, keep
# the disposition, and the expectation moved with it. Coverage,
# membership and uniqueness all stayed green over a table whose facts
# were wrong, and only the seventy-three curated rows -- which carry
# their fact in full -- could have caught it.
#
# THE REPAIR IS NOT ANOTHER DERIVATION. Nothing below is read from
# `validation.measure`. The fact governing a site is composed from two
# statements written out in this file:
#
#   1. `FIXTURE_ROLES` -- the type path each fixture column is
#      described with. Twenty-three lines, and every one of them is
#      checked against the DESCRIPTION, which is the profile predicate
#      of V3.1's identity and an INPUT to the validator rather than
#      anything it says.
#   2. `SUBCHECK_FACTS` -- for a column of that family, which registry
#      fact each subcheck of the shipped table answers for. Two hundred
#      and five lines, every fact of them checked against the registry
#      itself.
#
# `test_every_shipped_site_binds_the_fact_this_file_states` then holds
# the shipped table to the composition, in BOTH directions: no site may
# bind a fact other than the one stated here, and no line here may go
# unreached. A rebinding is therefore red twice -- once in that
# identity, and once in `test_every_registered_red_case_misses_the_site
# _it_names`, because the site the case names no longer exists.
#
# WHY A FAMILY AND A SUBCHECK RATHER THAN FIVE HUNDRED AND EIGHTY-EIGHT
# LINES. The two are the same statement: the composition is total over
# the shipped sites and exact, so writing each site out separately
# would add no information and five hundred lines nobody re-reads. What
# it must not do is lose the COLUMN, and it does not: a covering row
# names its own column, and `FIXTURE_ROLES` gives that column its
# family, so moving one column's subcheck to another fact is caught on
# that column alone.
#
# THE VALUES WERE TAKEN OFF THE SHIPPED TABLE ONCE, at the commit that
# wrote them, and are frozen here. That is what a stated expectation
# is: it was true when a person wrote it down and it does not move
# again. What is forbidden is reading it at RUN TIME, which is what
# this replaces.

# The fact GROUP each type path publishes into. The ten roles the
# taxonomy carries, mapped onto the seven groups the registry files a
# column's own facts under; `universal` is every column's and is not a
# family. Written out rather than derived from a fact name, because a
# fact name is the thing being checked.
ROLE_FAMILIES = {
    "binary": "label",
    "categorical": "label",
    "constant": "label",
    # It publishes the four shared label keys and no key of its own,
    # so its facts are the label family's (plan P4-D5).
    "long_tail_labels": "label",
    # Its quantitative facts are the numeric family's, read over the
    # cores; the seven keys it adds carry the family name `affixed`.
    "affixed_number": "numeric",
    "time_of_day": "clock",
    "continuous": "numeric",
    "count": "numeric",
    "datetime": "datetime",
    "empty": "empty",
    "free_text": "free_text",
    "identifier": "identifier",
    "numeric_unrepresentable": "numeric_unrepresentable",
}

# The family of the DOCUMENT's own entries -- the ones filed against no
# column, whose fact group is `document` and whose one universal fact is
# the header names.
DOCUMENT_FAMILY = "document"

# The type path each fixture column is described with, stated here and
# checked against the description by
# `test_every_fixture_column_carries_the_role_this_file_states`.
FIXTURE_ROLES: "dict[str, dict[str, str]]" = {
    "every-role": {
        "amount": "continuous",
        "answer": "binary",
        "batch": "constant",
        "comment": "free_text",
        "dose": "affixed_number",
        "note": "long_tail_labels",
        "reading": "count",
        "seen_at": "time_of_day",
        "record_code": "identifier",
        "recorded_on": "datetime",
        "region": "categorical",
        "unused": "empty",
        "visits": "count",
    },
    "headerless": {
        "column_1": "count",
        "column_2": "categorical",
    },
    "padded-codes": {"code": "count"},
    "shaped-text": {"lab_code": "free_text", "region": "categorical"},
    "pooled": {"reading": "continuous"},
    "quarters": {
        "region": "categorical",
        "when": "datetime",
    },
    "spelled": {"reading": "continuous"},
    "unrepresentable": {"overflow": "numeric_unrepresentable"},
}

# THE FOUR PROFILE PREDICATES V3.1 NAMES, and the fixture each one is
# described from -- so `_family_of` can give a predicate's columns their
# family exactly as it gives an ordinary run's.
#
# REVIEW ITEM P3-V4-F6. The binding proof below walked the six ordinary
# runs and called itself total over the shipped table. It was total over
# the ordinary PREDICATE. Owner decision 7 makes the two zero-row forms
# predicates of their own, and the sites they file were outside the walk
# altogether: `bytes.zero-row-form` was bound by nothing here, and the
# headed form's `header.names` and `columns.order` could swap facts with
# every assertion in this file still green. A statement about "every
# shipped site" that skips a shipped predicate is a statement about a
# subset, and the difference is exactly where the defect sat.
#
# Checked against `_predicate_runs` by
# `test_the_predicate_walk_covers_every_predicate_that_file_names`, so
# the two statements of what the predicates ARE cannot drift apart.
PREDICATE_FIXTURES = {
    "header-written": "every-role",
    "names-generated": "headerless",
    "zero-rows-headered": "every-role",
    "zero-rows-headerless": "headerless",
}

# Which registry fact each subcheck of the shipped table answers for, on
# a column of each family. Keyed by (family, subcheck); the value is the
# fact, `group.field`, exactly as the registry spells it.
SUBCHECK_FACTS: "dict[tuple[str, str], str]" = {
    # -- clock ------------------------------------------------------------
    ("clock", "axes.quality_state"): "universal.quality_state",
    ("clock", "axes.role"): "universal.role",
    ("clock", "axes.statistical_type"): "universal.statistical_type",
    ("clock", "axes.structural_role"): "universal.structural_role",
    ("clock", "counts.n_contradictory"): "universal.n_contradictory",
    ("clock", "counts.n_not_numeric"): "universal.n_not_numeric",
    ("clock", "counts.n_numeric"): "universal.n_numeric",
    ("clock", "counts.n_out_of_range"): "universal.n_out_of_range",
    ("clock", "counts.n_unparsed"): "clock.n_unparsed",
    ("clock", "clock-ladder.max"): "clock.clock_percentiles.max",
    ("clock", "clock-ladder.min"): "clock.clock_percentiles.min",
    ("clock", "distinct.n_distinct"): "clock.n_distinct",
    ("clock", "distinct.n_distinct_folded"): "clock.n_distinct_folded",
    ("clock", "ends.earliest"): "clock.earliest",
    ("clock", "ends.latest"): "clock.latest",
    ("clock", "form.clock_form"): "clock.clock_form",
    ("clock", "position.at"): "universal.position",
    ("clock", "presence.n_missing"): "universal.n_missing",
    ("clock", "presence.n_present"): "universal.n_present",
    ("clock", "clock-ladder.p01"): "clock.clock_percentiles",
    ("clock", "clock-ladder.p05"): "clock.clock_percentiles",
    ("clock", "clock-ladder.p10"): "clock.clock_percentiles",
    ("clock", "clock-ladder.p25"): "clock.clock_percentiles",
    ("clock", "clock-ladder.p50"): "clock.clock_percentiles",
    ("clock", "clock-ladder.p75"): "clock.clock_percentiles",
    ("clock", "clock-ladder.p90"): "clock.clock_percentiles",
    ("clock", "clock-ladder.p95"): "clock.clock_percentiles",
    ("clock", "clock-ladder.p99"): "clock.clock_percentiles",
    # -- datetime ----------------------------------------------------------
    ("datetime", "axes.quality_state"): "universal.quality_state",
    ("datetime", "axes.role"): "universal.role",
    ("datetime", "axes.statistical_type"): "universal.statistical_type",
    ("datetime", "axes.structural_role"): "universal.structural_role",
    ("datetime", "counts.n_contradictory"): "universal.n_contradictory",
    ("datetime", "counts.n_not_numeric"): "universal.n_not_numeric",
    ("datetime", "counts.n_numeric"): "universal.n_numeric",
    ("datetime", "counts.n_out_of_range"): "universal.n_out_of_range",
    ("datetime", "counts.n_unparsed"): "datetime.n_unparsed",
    ("datetime", "counts.subsecond_digits"): "datetime.subsecond_digits",
    ("datetime", "date-ladder.max"): "datetime.date_percentiles.max",
    ("datetime", "date-ladder.min"): "datetime.date_percentiles.min",
    ("datetime", "date-ladder.p01"): "datetime.date_percentiles",
    ("datetime", "date-ladder.p05"): "datetime.date_percentiles",
    ("datetime", "date-ladder.p10"): "datetime.date_percentiles",
    ("datetime", "date-ladder.p25"): "datetime.date_percentiles",
    ("datetime", "date-ladder.p50"): "datetime.date_percentiles",
    ("datetime", "date-ladder.p75"): "datetime.date_percentiles",
    ("datetime", "date-ladder.p90"): "datetime.date_percentiles",
    ("datetime", "date-ladder.p95"): "datetime.date_percentiles",
    ("datetime", "date-ladder.p99"): "datetime.date_percentiles",
    ("datetime", "distinct.n_distinct"): "datetime.n_distinct",
    ("datetime", "distinct.n_distinct_folded"): "datetime.n_distinct_folded",
    ("datetime", "ends.earliest"): "datetime.earliest",
    ("datetime", "ends.latest"): "datetime.latest",
    ("datetime", "offsets.(none)"): "datetime.utc_offsets",
    ("datetime", "offsets.earliest"): "datetime.earliest_utc_offset",
    ("datetime", "offsets.latest"): "datetime.latest_utc_offset",
    ("datetime", "offsets.map"): "datetime.utc_offsets",
    ("datetime", "offsets.read-at"): "datetime.datetimes_read_at",
    ("datetime", "position.at"): "universal.position",
    ("datetime", "precision.resolution"): "datetime.resolution",
    ("datetime", "precision.time_precision"): "datetime.time_precision",
    ("datetime", "presence.n_missing"): "universal.n_missing",
    ("datetime", "presence.n_present"): "universal.n_present",
    # -- document ----------------------------------------------------------
    ("document", "bytes.byte-order-mark"): "document.encoding",
    ("document", "bytes.line-endings"): "document.line-endings",
    ("document", "bytes.terminal-newline"): "document.line-endings",
    ("document", "bytes.utf8"): "document.encoding",
    # REACHED BY NO ORDINARY RUN, and that is the point (review item
    # P3-V4-F6). Owner decision 7's byte form is filed only on the two
    # zero-row predicates, so a walk over the ordinary fixtures alone
    # states nothing about it -- and a line stating nothing is the
    # shape this whole file exists to refuse.
    ("document", "bytes.zero-row-form"): "document.n_rows",
    ("document", "columns.n_columns"): "document.n_columns",
    ("document", "columns.order"): "document.columns",
    ("document", "header.names"): "universal.name",
    ("document", "header.presence"): "document.source.header_source",
    ("document", "rows.n_rows"): "document.n_rows",
    # -- empty -------------------------------------------------------------
    ("empty", "axes.quality_state"): "universal.quality_state",
    ("empty", "axes.role"): "universal.role",
    ("empty", "axes.statistical_type"): "universal.statistical_type",
    ("empty", "axes.structural_role"): "universal.structural_role",
    ("empty", "counts.n_contradictory"): "universal.n_contradictory",
    ("empty", "counts.n_not_numeric"): "universal.n_not_numeric",
    ("empty", "counts.n_numeric"): "universal.n_numeric",
    ("empty", "counts.n_out_of_range"): "universal.n_out_of_range",
    ("empty", "distinct.n_distinct"): "empty.n_distinct",
    ("empty", "distinct.n_distinct_folded"): "empty.n_distinct_folded",
    ("empty", "position.at"): "universal.position",
    ("empty", "presence.n_missing"): "universal.n_missing",
    ("empty", "presence.n_present"): "universal.n_present",
    # -- free_text ---------------------------------------------------------
    ("free_text", "axes.quality_state"): "universal.quality_state",
    ("free_text", "axes.role"): "universal.role",
    ("free_text", "axes.statistical_type"): "universal.statistical_type",
    ("free_text", "axes.structural_role"): "universal.structural_role",
    ("free_text", "counts.n_all_digits"): "free_text.n_all_digits",
    ("free_text", "counts.n_code_alphabet"): "free_text.n_code_alphabet",
    ("free_text", "counts.n_contradictory"): "universal.n_contradictory",
    ("free_text", "counts.n_not_numeric"): "universal.n_not_numeric",
    ("free_text", "counts.n_numeric"): "universal.n_numeric",
    ("free_text", "counts.n_out_of_range"): "universal.n_out_of_range",
    ("free_text", "distinct.n_distinct"): "free_text.n_distinct",
    ("free_text", "distinct.n_distinct_by_occurrences"): (
        "free_text.n_distinct_by_occurrences"
    ),
    ("free_text", "distinct.n_distinct_folded"): "free_text.n_distinct_folded",
    ("free_text", "length.max"): "free_text.length.max",
    ("free_text", "length.mean"): "free_text.length.mean",
    ("free_text", "length.min"): "free_text.length.min",
    ("free_text", "length.p50"): "free_text.length.p50",
    ("free_text", "position.at"): "universal.position",
    ("free_text", "presence.n_missing"): "universal.n_missing",
    ("free_text", "presence.n_present"): "universal.n_present",
    ("free_text", "words.max"): "free_text.words.max",
    ("free_text", "words.mean"): "free_text.words.mean",
    ("free_text", "words.min"): "free_text.words.min",
    # -- identifier --------------------------------------------------------
    ("identifier", "axes.quality_state"): "universal.quality_state",
    ("identifier", "axes.role"): "universal.role",
    ("identifier", "axes.statistical_type"): "universal.statistical_type",
    ("identifier", "axes.structural_role"): "universal.structural_role",
    ("identifier", "counts.n_all_digits"): "identifier.n_all_digits",
    ("identifier", "counts.n_code_alphabet"): "identifier.n_code_alphabet",
    ("identifier", "counts.n_contradictory"): "universal.n_contradictory",
    ("identifier", "counts.n_not_numeric"): "universal.n_not_numeric",
    ("identifier", "counts.n_numeric"): "universal.n_numeric",
    ("identifier", "counts.n_out_of_range"): "universal.n_out_of_range",
    ("identifier", "distinct.n_distinct"): "identifier.n_distinct",
    ("identifier", "distinct.n_distinct_by_occurrences"): (
        "identifier.n_distinct_by_occurrences"
    ),
    ("identifier", "distinct.n_distinct_folded"): "identifier.n_distinct_folded",
    ("identifier", "length.max"): "identifier.max_length",
    ("identifier", "length.min"): "identifier.min_length",
    ("identifier", "position.at"): "universal.position",
    ("identifier", "presence.n_missing"): "universal.n_missing",
    ("identifier", "presence.n_present"): "universal.n_present",
    ("identifier", "type.all_whole_numbers"): "identifier.all_whole_numbers",
    # -- label -------------------------------------------------------------
    ("label", "axes.quality_state"): "universal.quality_state",
    ("label", "axes.role"): "universal.role",
    ("label", "axes.statistical_type"): "universal.statistical_type",
    ("label", "axes.structural_role"): "universal.structural_role",
    ("label", "counts.n_contradictory"): "universal.n_contradictory",
    ("label", "counts.n_not_numeric"): "universal.n_not_numeric",
    ("label", "counts.n_numeric"): "universal.n_numeric",
    ("label", "counts.n_out_of_range"): "universal.n_out_of_range",
    ("label", "distinct.n_distinct"): "label.n_distinct",
    ("label", "distinct.n_distinct_folded"): "label.n_distinct_folded",
    ("label", "levels.clinic.count"): "label.count",
    ("label", "levels.clinic.label"): "label.label",
    ("label", "levels.clinic.variants"): "label.variants",
    ("label", "levels.clinic.variants_withheld"): "label.variants_withheld",
    ("label", "levels.east.count"): "label.count",
    ("label", "levels.east.label"): "label.label",
    ("label", "levels.east.variants"): "label.variants",
    ("label", "levels.east.variants_withheld"): "label.variants_withheld",
    ("label", "levels.no.count"): "label.count",
    ("label", "levels.no.label"): "label.label",
    ("label", "levels.no.variants"): "label.variants",
    ("label", "levels.no.variants_withheld"): "label.variants_withheld",
    ("label", "levels.north.count"): "label.count",
    ("label", "levels.referral.count"): "label.count",
    ("label", "levels.referral.label"): "label.label",
    ("label", "levels.referral.variants"): "label.variants",
    ("label", "levels.referral.variants_withheld"): (
        "label.variants_withheld"
    ),
    ("label", "levels.north.label"): "label.label",
    ("label", "levels.north.variants"): "label.variants",
    ("label", "levels.north.variants_withheld"): "label.variants_withheld",
    ("label", "levels.one.count"): "label.count",
    ("label", "levels.one.label"): "label.label",
    ("label", "levels.one.variants"): "label.variants",
    ("label", "levels.one.variants_withheld"): "label.variants_withheld",
    ("label", "levels.set"): "label.levels",
    ("label", "levels.south.count"): "label.count",
    ("label", "levels.south.label"): "label.label",
    ("label", "levels.south.variants"): "label.variants",
    ("label", "levels.south.variants_withheld"): "label.variants_withheld",
    ("label", "levels.west.count"): "label.count",
    ("label", "levels.west.label"): "label.label",
    ("label", "levels.west.variants"): "label.variants",
    ("label", "levels.west.variants_withheld"): "label.variants_withheld",
    ("label", "levels.yes.count"): "label.count",
    ("label", "levels.yes.label"): "label.label",
    ("label", "levels.yes.variants"): "label.variants",
    ("label", "levels.yes.variants_withheld"): "label.variants_withheld",
    ("label", "position.at"): "universal.position",
    ("label", "presence.n_missing"): "universal.n_missing",
    ("label", "presence.n_present"): "universal.n_present",
    ("label", "suppressed.counts"): "label.suppressed_level_counts",
    ("label", "suppressed.suppressed_levels"): "label.suppressed_levels",
    ("label", "suppressed.suppressed_rows"): "label.suppressed_rows",
    # -- numeric -----------------------------------------------------------
    # The seven below are emitted only by the affixed role, whose
    # quantitative facts are the numeric family's read over the cores.
    # A plain numeric column emits none of them, so no row here says
    # that one owes them: this map answers which registry fact a
    # subcheck binds, never which subchecks a column owes.
    # The census of fraction widths names one subcheck per PUBLISHED
    # width, so its subcheck names are decided by the description rather
    # than fixed here. Only the widths the fixtures actually publish
    # need a row, and a width one of them publishes without a row here
    # reaches the coverage identity as a dead row and is reported by
    # name -- which is how a new fixture width is noticed.
    ("numeric", "widths.published.1"): "numeric.fraction_widths",
    ("numeric", "widths.published.2"): "numeric.fraction_widths",
    # The census of FIELD widths names one subcheck per published width
    # on the same terms, and for the same reason only the widths the
    # fixtures publish need a row here (P4-D14).
    ("numeric", "pads.published.5"): "numeric.pad_widths",
    # The census of written FORMS names one subcheck per published
    # form, so its subcheck names are decided by the description in
    # the same way the two width censuses are (P4-D18). Only the forms
    # the fixtures actually publish need a row.
    ("label", "forms.published.AAAAAA"): "label.shape_forms",
    ("label", "forms.published.AAAAAAAA"): "label.shape_forms",
    ("free_text", "forms.published.9999-9"): "free_text.shape_forms",
    ("numeric", "counts.affix_prefix"): "affixed.affix_prefix",
    ("numeric", "counts.affix_suffix"): "affixed.affix_suffix",
    ("numeric", "counts.n_affixed"): "affixed.n_affixed",
    ("numeric", "counts.n_core_contradictory"): "affixed.n_core_contradictory",
    ("numeric", "counts.n_core_not_numeric"): "affixed.n_core_not_numeric",
    ("numeric", "counts.n_core_numeric"): "affixed.n_core_numeric",
    ("numeric", "counts.n_core_out_of_range"): "affixed.n_core_out_of_range",
    ("numeric", "axes.quality_state"): "universal.quality_state",
    ("numeric", "axes.role"): "universal.role",
    ("numeric", "axes.statistical_type"): "universal.statistical_type",
    ("numeric", "axes.structural_role"): "universal.structural_role",
    ("numeric", "counts.n_contradictory"): "universal.n_contradictory",
    ("numeric", "counts.n_left_out_of_statistics"): "numeric.n_left_out_of_statistics",
    ("numeric", "counts.n_negative"): "numeric.n_negative",
    ("numeric", "counts.n_negative_unrepresentable"): (
        "numeric.n_negative_unrepresentable"
    ),
    ("numeric", "counts.n_not_numeric"): "universal.n_not_numeric",
    ("numeric", "counts.n_numeric"): "universal.n_numeric",
    ("numeric", "counts.n_out_of_range"): "universal.n_out_of_range",
    ("numeric", "counts.n_used_in_statistics"): "numeric.n_used_in_statistics",
    ("numeric", "counts.n_zero"): "numeric.n_zero",
    ("numeric", "counts.numeric_share"): "numeric.numeric_share",
    ("numeric", "distinct.n_distinct"): "numeric.n_distinct",
    ("numeric", "distinct.n_distinct_folded"): "numeric.n_distinct_folded",
    ("numeric", "ladder.max"): "numeric.percentiles.max",
    ("numeric", "ladder.min"): "numeric.percentiles.min",
    ("numeric", "ladder.p01"): "numeric.percentiles",
    ("numeric", "ladder.p05"): "numeric.percentiles",
    ("numeric", "ladder.p10"): "numeric.percentiles",
    ("numeric", "ladder.p25"): "numeric.percentiles",
    ("numeric", "ladder.p50"): "numeric.percentiles",
    ("numeric", "ladder.p75"): "numeric.percentiles",
    ("numeric", "ladder.p90"): "numeric.percentiles",
    ("numeric", "ladder.p95"): "numeric.percentiles",
    ("numeric", "ladder.p99"): "numeric.percentiles",
    ("numeric", "moments.mean"): "numeric.mean",
    ("numeric", "moments.skew"): "numeric.skew",
    ("numeric", "moments.std"): "numeric.std",
    ("numeric", "position.at"): "universal.position",
    ("numeric", "presence.n_missing"): "universal.n_missing",
    ("numeric", "presence.n_present"): "universal.n_present",
    ("numeric", "styles.at-least.decimal"): "numeric.numeric_styles",
    ("numeric", "styles.at-least.exponent_lower"): "numeric.numeric_styles",
    ("numeric", "styles.at-least.plain"): "numeric.numeric_styles",
    ("numeric", "styles.canonical.decimal"): "numeric.numeric_styles",
    ("numeric", "styles.canonical.exponent_lower"): "numeric.numeric_styles",
    ("numeric", "styles.exact.exponent_upper"): "numeric.numeric_styles",
    ("numeric", "styles.exact.leading_plus"): "numeric.numeric_styles",
    ("numeric", "styles.exact.leading_zero"): "numeric.numeric_styles",
    ("numeric", "styles.published.decimal"): "numeric.numeric_styles",
    ("numeric", "styles.published.exponent_lower"): "numeric.numeric_styles",
    ("numeric", "styles.published.leading_zero"): "numeric.numeric_styles",
    ("numeric", "styles.published.plain"): "numeric.numeric_styles",
    ("numeric", "styles.remainder"): "numeric.numeric_styles",
    ("numeric", "styles.spelled"): "numeric.numeric_styles",
    ("numeric", "styles.spill"): "numeric.numeric_styles",
    ("numeric", "type.integer_valued"): "numeric.integer_valued",
    ("numeric", "type.std_unrepresentable"): "numeric.std_unrepresentable",
    # -- numeric_unrepresentable -------------------------------------------
    ("numeric_unrepresentable", "axes.quality_state"): "universal.quality_state",
    ("numeric_unrepresentable", "axes.role"): "universal.role",
    ("numeric_unrepresentable", "axes.statistical_type"): "universal.statistical_type",
    ("numeric_unrepresentable", "axes.structural_role"): "universal.structural_role",
    ("numeric_unrepresentable", "counts.n_contradictory"): "universal.n_contradictory",
    ("numeric_unrepresentable", "counts.n_fraction"): (
        "numeric_unrepresentable.n_fraction"
    ),
    ("numeric_unrepresentable", "counts.n_negative"): (
        "numeric_unrepresentable.n_negative"
    ),
    ("numeric_unrepresentable", "counts.n_not_numeric"): "universal.n_not_numeric",
    ("numeric_unrepresentable", "counts.n_numeric"): "universal.n_numeric",
    ("numeric_unrepresentable", "counts.n_out_of_range"): "universal.n_out_of_range",
    ("numeric_unrepresentable", "counts.n_positive"): (
        "numeric_unrepresentable.n_positive"
    ),
    ("numeric_unrepresentable", "counts.n_sign_unknown"): (
        "numeric_unrepresentable.n_sign_unknown"
    ),
    ("numeric_unrepresentable", "counts.n_whole"): "numeric_unrepresentable.n_whole",
    ("numeric_unrepresentable", "counts.n_whole_unknown"): (
        "numeric_unrepresentable.n_whole_unknown"
    ),
    ("numeric_unrepresentable", "distinct.n_distinct"): (
        "numeric_unrepresentable.n_distinct"
    ),
    ("numeric_unrepresentable", "distinct.n_distinct_by_occurrences"): (
        "numeric_unrepresentable.n_distinct_by_occurrences"
    ),
    ("numeric_unrepresentable", "distinct.n_distinct_folded"): (
        "numeric_unrepresentable.n_distinct_folded"
    ),
    ("numeric_unrepresentable", "position.at"): "universal.position",
    ("numeric_unrepresentable", "presence.n_missing"): "universal.n_missing",
    ("numeric_unrepresentable", "presence.n_present"): "universal.n_present",
}

# WHICH FACTS EACH FAMILY MAY STATE AT THE WHOLE GRAIN. A listing whose
# subcheck is "" says "this fact, entire, and no CSV can evidence it"
# (V3.3), so its identity carries no subcheck name to key on and the map
# above cannot hold it: one family lists several such facts and they are
# different facts, not one fact under different names.
#
# REVIEW ITEM P3-V4-F6, the half round 7 found still open. The binding
# proof walked CHECKS alone, so a listing's `fact` was asserted nowhere
# at all -- and a listing is half of V3.1's entry table. Rebinding
# `offsets.map` to another registry fact of the same column left every
# assertion in this file green while the report duplicated one offset
# fact and omitted another.
WHOLE_FACT_LISTINGS: "dict[str, tuple[str, ...]]" = {
    # The clock role lists the eight universal facts no CSV can
    # evidence, and nothing of its own: every one of its five keys is
    # checked.
    "clock": (
        "universal.detection_evidence",
        "universal.missing_by_class",
        "universal.missing_by_source",
        "universal.n_missing_blank",
        "universal.n_missing_withheld",
        "universal.n_sentinel_candidates_unpublished",
        "universal.remarks",
        "universal.sentinel_verdicts",
    ),
    "datetime": (
        "datetime.format",
        "datetime.resolution_mix",
        "universal.detection_evidence",
        "universal.missing_by_class",
        "universal.missing_by_source",
        "universal.n_missing_blank",
        "universal.n_missing_withheld",
        "universal.n_sentinel_candidates_unpublished",
        "universal.remarks",
        "universal.sentinel_verdicts",
    ),
    # `document.columns`, `document.n_columns` and `universal.name` are
    # NOT here, and were until the review of the shipped reports on
    # 2026-08-15. All three are CHECKED on a file with a header line, as
    # `columns.order`, `columns.n_columns` and `header.names`, and the
    # headerless and zero-row predicates listed them at the whole grain
    # instead -- so a reader comparing that census with an ordinary
    # run's was given no way to see that they are the same three
    # obligations, and the report printed a registry identifier where
    # every other line prints a name. They now carry the subcheck their
    # check-side twin carries and are held to `SUBCHECK_FACTS`, which
    # already binds all three.
    "document": (
        "document.source.encoding",
        "document.source.header_by_convention",
        "document.source.header_evidence",
        "document.source.used_fallback_encoding",
    ),
    "empty": (
        "universal.detection_evidence",
        "universal.missing_by_class",
        "universal.missing_by_source",
        "universal.n_missing_blank",
        "universal.n_missing_withheld",
        "universal.n_sentinel_candidates_unpublished",
        "universal.remarks",
        "universal.sentinel_verdicts",
    ),
    "free_text": (
        "universal.detection_evidence",
        "universal.missing_by_class",
        "universal.missing_by_source",
        "universal.n_missing_blank",
        "universal.n_missing_withheld",
        "universal.n_sentinel_candidates_unpublished",
        "universal.remarks",
        "universal.sentinel_verdicts",
    ),
    "identifier": (
        "universal.detection_evidence",
        "universal.missing_by_class",
        "universal.missing_by_source",
        "universal.n_missing_blank",
        "universal.n_missing_withheld",
        "universal.n_sentinel_candidates_unpublished",
        "universal.remarks",
        "universal.sentinel_verdicts",
    ),
    "label": (
        "universal.detection_evidence",
        "universal.missing_by_class",
        "universal.missing_by_source",
        "universal.n_missing_blank",
        "universal.n_missing_withheld",
        "universal.n_sentinel_candidates_unpublished",
        "universal.remarks",
        "universal.sentinel_verdicts",
    ),
    "numeric": (
        "universal.detection_evidence",
        "universal.missing_by_class",
        "universal.missing_by_source",
        "universal.n_missing_blank",
        "universal.n_missing_withheld",
        "universal.n_sentinel_candidates_unpublished",
        "universal.remarks",
        "universal.sentinel_verdicts",
    ),
    "numeric_unrepresentable": (
        "universal.detection_evidence",
        "universal.missing_by_class",
        "universal.missing_by_source",
        "universal.n_missing_blank",
        "universal.n_missing_withheld",
        "universal.n_sentinel_candidates_unpublished",
        "universal.remarks",
        "universal.sentinel_verdicts",
    ),
}

# THE THREE DESCRIPTIONS WHOSE LISTINGS ONLY A CORNER FILES, and the
# type path of the one column each carries. They are walked by the
# listing half of the binding proof and by nothing else: a corner sends
# a fact to REPORT-ONLY, so these columns file entries the six ordinary
# fixtures cannot, and every one of them was outside the proof.
#
# They are NOT in `runs`, and that is deliberate rather than convenient.
# `runs` drives the red battery, where every executable subcheck owes a
# registered perturbation; a listing owes none, because a listing has no
# verdict to make miss. Adding these there would demand a red case for
# every ordinary check of three more columns and would prove nothing
# about the entries they are here for.
CORNER_FIXTURE_ROLES = {
    "withheld-offsets": {"recorded_on": "datetime"},
    "exhausted-identifier": {"record_code": "identifier"},
    "spent-spellings": {"reading": "count"},
}

# Which corner each of them must reach, checked by
# `test_every_corner_fixture_reaches_the_corner_it_is_for` so that the
# listing walk cannot go green because a fixture stopped reaching its
# corner and stopped filing the entries it is here for.
CORNER_FIXTURE_CORNERS = {
    "withheld-offsets": "datetime-offsets-withheld",
    "exhausted-identifier": "identifier-infeasible",
    "spent-spellings": "numeric-spellings-short",
}


def _corner_tables() -> "list[tuple[str, str, list[str] | None]]":
    """The bytes of each corner fixture: name, table, forced identifiers.

    Every one is built here from the seeded neutral builders and passed
    through the real producer, so what makes it a corner is the
    producer's own arithmetic and not a hand-written description.

    * WITHHELD OFFSETS -- six zones over sixty rows, ten rows each. Ten
      is under the publication floor, so the whole map is pooled into
      the single withheld key, which IS the corner (V4.1).
    * EXHAUSTED IDENTIFIER -- twenty-six one-character values outside
      every code alphabet, declared an identifier. The widest band's
      one-character family holds twenty-five spellings, so the twenty-
      sixth cannot be written and the three cardinality facts go
      REPORT-ONLY.
    * SPENT SPELLINGS -- two hundred whole numbers, all different, in
      one style. The supply is one spelling and the envelope G12.8
      authorizes runs from one value to two hundred, which every file of
      that length is inside, so both distinctness bars are listings
      rather than checks that cannot fail (V3.5).
    """
    zones = ("+00:00", "+01:00", "+02:00", "-03:00", "-04:00", "+05:30")
    stamps = [
        f"2024-01-{(index % 28) + 1:02d}T00:00:00{zones[index // 10]}"
        for index in range(60)
    ]
    wides = [chr(0x100 + 2 * index) for index in range(26)]
    return [
        (
            "withheld-offsets",
            fixtures.single_column_table("recorded_on", stamps),
            None,
        ),
        (
            "exhausted-identifier",
            fixtures.single_column_table("record_code", wides),
            ["record_code"],
        ),
        (
            "spent-spellings",
            fixtures.single_column_table(
                "reading", [f"{number}" for number in range(1, 201)]
            ),
            None,
        ),
    ]


@pytest.fixture(scope="module")
def corner_runs(
    tmp_path_factory: pytest.TempPathFactory,
) -> "list[tuple[str, contract.Profile, str]]":
    """The three corner descriptions and each one's own twin."""
    folder = tmp_path_factory.mktemp("corner-entries")
    built: list[tuple[str, contract.Profile, str]] = []
    for name, text, declared in _corner_tables():
        described = _described(folder, text, declared, stem=name)
        twin = rendering.twin_csv(generation.generate(described, SEED))
        built = built + [(name, described, twin)]
    return built


def _family_of(fixture: str, column: str) -> str:
    """The fact family of one column of one fixture, from this file alone.

    No part of this consults the validator. The document's own entries
    -- the ones filed against no column -- are their own family.
    """
    if not column:
        return DOCUMENT_FAMILY
    if fixture in CORNER_FIXTURE_ROLES:
        return ROLE_FAMILIES[CORNER_FIXTURE_ROLES[fixture][column]]
    return ROLE_FAMILIES[FIXTURE_ROLES[fixture][column]]


def _stated_fact(fixture: str, column: str, subcheck: str) -> str:
    """The registry fact this file says governs one site.

    Returns a sentence naming the gap where nothing is stated, rather
    than raising: a covering row for a site this file has no statement
    about must reach the coverage identity as a DEAD ROW and be
    reported by name, not disappear into an error at collection time.
    """
    family = _family_of(fixture, column)
    if (family, subcheck) not in SUBCHECK_FACTS:
        return f"(this file states no fact for {family}/{subcheck})"
    return SUBCHECK_FACTS[(family, subcheck)]



@pytest.fixture(scope="module")
def registered(
    tmp_path_factory: pytest.TempPathFactory,
    runs: "list[tuple[str, contract.Profile, str]]",
) -> "list[RedCase]":
    """The whole registration: the curated rows, then the covering ones.

    A covering row names its site by column and subcheck, and the third
    term of the identity -- the registry FACT -- comes from
    `SUBCHECK_FACTS` above, which is written out in this file.

    IT USED TO COME OFF THE SHIPPED TABLE (review item P3-V4-F6), which
    made the expected side of this proof a copy of its subject: a
    rebinding in production moved the expectation with it and every
    assertion here stayed green. Nothing about this fixture reads the
    validator's output any more, and a covering row for a site this
    file states no fact for is kept with the sentence saying so, so
    that the coverage identity reports it as a dead row rather than
    dropping it silently.
    """
    cases = list(NAMED_RED_CASES)
    for name, _described, _twin in runs:
        for column in sorted(COVERING_RED_CASES.get(name, {})):
            for perturbation, subcheck in COVERING_RED_CASES[name][column]:
                cases = cases + [
                    RedCase(
                        name,
                        perturbation,
                        column,
                        _stated_fact(name, column, subcheck),
                        subcheck,
                    )
                ]
    return cases


def test_every_fixture_column_carries_the_role_this_file_states(
    runs: "list[tuple[str, contract.Profile, str]]",
) -> None:
    """`FIXTURE_ROLES` is the description's own, not a guess at it.

    The family a site's fact is composed from comes from the type path
    the DESCRIPTION gives that column -- the profile predicate of
    V3.1's identity. It is written out in this file so that no
    expectation is read out of the validator, and it is compared here
    against the descriptions the fixtures actually build, in both
    directions: a fixture column this file does not name, or a name
    here for a column no fixture has, is as much a gap as a wrong role.
    """
    assert sorted(FIXTURE_ROLES) == sorted(name for name, _d, _t in runs), (
        "this file states roles for a set of fixtures that is not the "
        "set the table is walked over"
    )
    for name, described, _twin in runs:
        stated = FIXTURE_ROLES[name]
        published = {column.name: column.role for column in described.columns}
        assert stated == published, (
            f"{name}: this file states {sorted(stated.items())} and the "
            f"description publishes {sorted(published.items())}. The "
            f"family every site's fact is composed from comes off these "
            f"roles, so they are stated here and checked rather than "
            f"read out of the run"
        )
        for role in stated.values():
            assert role in ROLE_FAMILIES, (
                f"{name}: the type path {role!r} has no fact family in "
                f"this file, so nothing here says what its columns owe"
            )


def test_every_fact_this_file_states_is_a_registry_fact() -> None:
    """The stated facts are the registry's, checked against it.

    A frozen expectation can go wrong in a way a derived one cannot: a
    fact could be written here that no registry entry carries, and the
    identity below would then hold the shipped table to a name out of
    nowhere. So every value of `SUBCHECK_FACTS` is looked up in the
    registry -- or in the closed list of byte rules, which no published
    field states -- before it is used to judge anything.
    """
    known = {f"{fact.group}.{fact.field}" for fact in dispositions.REGISTRY}
    unknown = sorted(
        {
            f"{family}/{subcheck}: {fact}"
            for (family, subcheck), fact in SUBCHECK_FACTS.items()
            if fact not in known and fact not in validation.BYTE_RULE_FACTS
        }
    )
    assert not unknown, (
        "these lines state a fact the registry does not carry, so they "
        "would hold the shipped table to a name nobody registered:\n  "
        + "\n  ".join(unknown)
    )


def test_every_shipped_site_binds_the_fact_this_file_states(
    tmp_path: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
    corner_runs: "list[tuple[str, contract.Profile, str]]",
) -> None:
    """V3.1's third term, stated here and compared with the shipped table.

    THE PROOF THIS RESTORES (review item P3-V4-F6). The registration
    used to take each covering row's fact off the shipped table, so
    rebinding a subcheck to another fact of the same disposition moved
    the expectation and nothing turned red. The binding is now written
    out in this file and compared with the shipped table here, in both
    directions:

    * no site may bind a fact other than the one stated -- which is the
      rebinding, caught on the column it happened to;
    * no line of `SUBCHECK_FACTS` may go unreached -- because a
      statement no site meets is a statement that cannot fail, and it
      is also how a stale line survives a subcheck being removed.

    The shipped table is READ here; nothing about it is copied into an
    expectation. That is the difference between comparing two writings
    and deriving one from the other.

    AND THE WALK IS TOTAL OVER THE PREDICATES, not over the ordinary
    fixtures alone (review item P3-V4-F6 again, on this very test). V3.1
    makes an entry's identity a PREDICATE, a column and a subcheck, and
    the six runs below are all the one ordinary predicate. Owner
    decision 7 ships two more, and every site they file -- nine on the
    headed zero-row form, six on the headerless one -- was outside this
    walk: `bytes.zero-row-form` was stated by no line at all, and
    `header.names` and `columns.order` could be swapped there with the
    whole suite still green. Both directions now run over the ordinary
    runs AND the four predicates, so a rebinding on a predicate is as
    red as a rebinding on a column.

    AND IT WALKS LISTINGS AS WELL AS CHECKS, over the corner runs too
    (review item P3-V4-F6, the half round 7 found still open). The same
    subcheck can be a check under one predicate and a listing under
    another, and only the check side was ever compared. `offsets.map` is
    a listing on every file there is: no line here stated what it binds,
    and rebinding it to another registry fact of the same column turned
    nothing in this suite red.
    """
    wrong: list[str] = []
    reached: set[tuple[str, str]] = set()
    walked = _every_entry_walked(tmp_path, runs, corner_runs)
    for name, fixture, sites in walked:
        for site in sites:
            family = _family_of(fixture, site.column)
            if not site.subcheck:
                continue
            reached.add((family, site.subcheck))
            stated = _stated_fact(fixture, site.column, site.subcheck)
            if stated != site.fact:
                wrong = wrong + [
                    (
                        f"{name}: {site.column or '(the document)'}: "
                        f"{site.subcheck}: the shipped table binds "
                        f"{site.fact} and this file states {stated}"
                    )
                ]
    assert not wrong, (
        "the shipped validator binds these subchecks to a registry fact "
        "other than the one this file states, so either the table has "
        "drifted or this file has:\n  " + "\n  ".join(sorted(wrong))
    )
    unreached = sorted(
        f"{family}/{subcheck}"
        for family, subcheck in SUBCHECK_FACTS
        if (family, subcheck) not in reached
    )
    assert not unreached, (
        "these lines state what governs a site the shipped table does "
        "not file, so they assert nothing at all:\n  "
        + "\n  ".join(unreached)
    )
    # ...AND THE PREDICATE WALK REACHED SOMETHING THE ORDINARY ONE DOES
    # NOT. A walk widened to a predicate that files only sites the
    # ordinary runs already file would be a widening on paper, and the
    # line above would go on being true for the wrong reason.
    ordinary = set()
    for name, fixture, sites in walked:
        if name in PREDICATE_FIXTURES or name in CORNER_FIXTURE_ROLES:
            continue
        for site in sites:
            ordinary.add((_family_of(fixture, site.column), site.subcheck))
    only_here = {pair for pair in reached if pair not in ordinary}
    assert only_here, (
        "the four predicates file no subcheck the six ordinary runs do "
        "not, so walking them adds nothing and this test is total over "
        "the same set it always was"
    )


def _every_entry_walked(
    folder: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
    corners: "list[tuple[str, contract.Profile, str]] | None",
) -> "list[tuple[str, str, list[Site]]]":
    """Every ENTRY the shipped table files, over every predicate here.

    Each element is (the run's own name, the fixture whose roles give
    its columns their family, the entries it filed). An entry is a
    check or a listing: V3.1 makes both rows of one table and V3.3 says
    which kind a fact takes under which predicate, so a walk that
    collected one kind was a walk over half the table (review item
    P3-V4-F6).

    The corner runs are walked only when they are handed in, because
    they are the one thing here whose whole reason is a listing: the
    six ordinary fixtures reach no corner, so four offset facts, three
    identifier cardinalities and two distinctness bars are entries no
    other run in this file files.
    """
    walked: list[tuple[str, str, list[Site]]] = []
    for name, described, twin in runs:
        outcome = _measured(folder, described, twin, f"{name}-facts.csv")
        walked = walked + [
            (name, name, _sites_of(outcome) + _listed_sites_of(outcome))
        ]
    for label, described, twin, _ordinary in _predicate_runs(folder, runs):
        text = _conforming_text(described, twin)
        outcome = _measured(folder, described, text, f"{label}-facts.csv")
        walked = walked + [
            (
                label,
                PREDICATE_FIXTURES[label],
                _sites_of(outcome) + _listed_sites_of(outcome),
            )
        ]
    for name, described, twin in corners if corners else []:
        outcome = _measured(folder, described, twin, f"{name}-facts.csv")
        walked = walked + [
            (name, name, _sites_of(outcome) + _listed_sites_of(outcome))
        ]
    return walked


def test_every_corner_fixture_reaches_the_corner_it_is_for(
    corner_runs: "list[tuple[str, contract.Profile, str]]",
) -> None:
    """The three corner descriptions carry the corner they are named for.

    The listing proof below is only about corner entries while these
    descriptions still reach a corner. A change to the classifier that
    stopped claiming one here would leave that proof green over a set
    with the corner entries taken out of it -- which is the shape of
    every widening-on-paper this file has had to repair -- so the corner
    each fixture reaches is stated in `CORNER_FIXTURE_CORNERS` and
    checked, in both directions: the named corner must be claimed, and
    the roles this file states for those columns must be the roles the
    producer gave them.
    """
    assert sorted(CORNER_FIXTURE_ROLES) == sorted(CORNER_FIXTURE_CORNERS)
    assert sorted(CORNER_FIXTURE_ROLES) == sorted(
        name for name, _d, _t in corner_runs
    )
    for name, described, _twin in corner_runs:
        published = {column.name: column.role for column in described.columns}
        assert published == CORNER_FIXTURE_ROLES[name], (
            f"{name}: this file states {sorted(CORNER_FIXTURE_ROLES[name].items())} "
            f"and the producer published {sorted(published.items())}"
        )
        claimed: set[str] = set()
        for corners in validation.corners_of(described).values():
            for corner in corners:
                claimed.add(corner)
        assert CORNER_FIXTURE_CORNERS[name] in claimed, (
            f"{name}: this description no longer reaches "
            f"{CORNER_FIXTURE_CORNERS[name]!r} -- it claims {sorted(claimed)} "
            f"-- so the entries it is here to bind are not being filed"
        )


def test_every_shipped_listing_binds_the_fact_this_file_states(
    tmp_path: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
    corner_runs: "list[tuple[str, contract.Profile, str]]",
) -> None:
    """V3.1's third term on the OTHER half of the entry table.

    REVIEW ITEM P3-V4-F6, the part round 7 found still open. Round 6
    widened the binding proof from the ordinary fixtures to the four
    profile predicates and called it total. It was total over CHECKS.
    `Listing.fact` was compared with nothing anywhere in this suite, and
    the corner listings -- the entries whose whole existence IS a
    listing -- were filed by no run the proof walked. Rebinding
    `offsets.map` to another registry fact of the same column left every
    assertion in this file green while the report duplicated one offset
    fact and omitted another.

    So every listing of every run here is held to a statement written
    out in this file, at both grains a listing has:

    * a listing with a SUBCHECK is held to `SUBCHECK_FACTS`, the same
      statement its check-side twin is held to, because the same
      obligation under a different predicate is the same obligation;
    * a listing at the WHOLE grain -- "this fact, entire" -- is held to
      `WHOLE_FACT_LISTINGS`, which is a set per family rather than a
      function, because one family lists several such facts and they are
      different facts and not one fact under several names.

    Both directions, as everywhere else here: no listing may bind a fact
    outside the statement, and no line of the statement may go
    unreached.
    """
    wrong: list[str] = []
    reached: set[tuple[str, str]] = set()
    for name, fixture, sites in _every_entry_walked(
        tmp_path, runs, corner_runs
    ):
        for site in sites:
            if site.subcheck:
                continue
            family = _family_of(fixture, site.column)
            reached.add((family, site.fact))
            if site.fact not in WHOLE_FACT_LISTINGS.get(family, ()):
                wrong = wrong + [
                    (
                        f"{name}: {site.column or '(the document)'}: this "
                        f"file states no whole-grain listing of "
                        f"{site.fact} for the {family} family"
                    )
                ]
    assert not wrong, (
        "the shipped validator lists these facts whole and this file "
        "states none of them:\n  " + "\n  ".join(sorted(wrong))
    )
    unreached = sorted(
        f"{family}/{fact}"
        for family in WHOLE_FACT_LISTINGS
        for fact in WHOLE_FACT_LISTINGS[family]
        if (family, fact) not in reached
    )
    assert not unreached, (
        "these lines state a whole-grain listing the shipped table does "
        "not file, so they assert nothing at all:\n  "
        + "\n  ".join(unreached)
    )


def test_the_corner_listings_are_reached_by_this_walk_and_nowhere_else(
    tmp_path: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
    corner_runs: "list[tuple[str, contract.Profile, str]]",
) -> None:
    """The corner entries are IN the binding proof, and were not.

    REVIEW ITEM P3-V4-F6's named witness. Nine entries exist only where
    a corner sends a fact to REPORT-ONLY -- four offset facts, three
    identifier cardinalities and two distinctness bars -- and no fixture
    the proof walked filed one of them. This asserts two things at once:
    that the corner runs file every one of the nine, and that the six
    ordinary fixtures and the four predicates file none of the four
    offset ones, so the walk cannot be narrowed back to them and stay
    green.
    """
    ordinary = _every_entry_walked(tmp_path, runs, None)
    with_corners = _every_entry_walked(tmp_path, runs, corner_runs)
    owed = {
        ("withheld-offsets", "recorded_on", "datetime.utc_offsets", "offsets.map"),
        (
            "withheld-offsets",
            "recorded_on",
            "datetime.earliest_utc_offset",
            "offsets.earliest",
        ),
        (
            "withheld-offsets",
            "recorded_on",
            "datetime.latest_utc_offset",
            "offsets.latest",
        ),
        (
            "withheld-offsets",
            "recorded_on",
            "datetime.datetimes_read_at",
            "offsets.read-at",
        ),
        (
            "exhausted-identifier",
            "record_code",
            "identifier.n_distinct",
            "distinct.n_distinct",
        ),
        (
            "exhausted-identifier",
            "record_code",
            "identifier.n_distinct_folded",
            "distinct.n_distinct_folded",
        ),
        (
            "exhausted-identifier",
            "record_code",
            "identifier.n_distinct_by_occurrences",
            "distinct.n_distinct_by_occurrences",
        ),
        (
            "spent-spellings",
            "reading",
            "numeric.n_distinct",
            "distinct.n_distinct",
        ),
        (
            "spent-spellings",
            "reading",
            "numeric.n_distinct_folded",
            "distinct.n_distinct_folded",
        ),
    }
    filed = {
        (name, site.column, site.fact, site.subcheck)
        for name, _fixture, sites in with_corners
        for site in sites
    }
    missing = sorted(entry for entry in owed if entry not in filed)
    assert not missing, (
        "the corner runs no longer file these entries, so the proof "
        "that binds them is asserting nothing:\n  "
        + "\n  ".join(f"{entry}" for entry in missing)
    )
    without = {
        site.subcheck
        for _name, _fixture, sites in ordinary
        for site in sites
    }
    assert "offsets.map" not in without, (
        "an ordinary fixture now files the withheld-offset corner, so "
        "this walk no longer shows that the corner runs add anything"
    )


# -- P3-D4's red battery, on the predicates as well as the columns -----


ZERO_ROW_PREDICATES = ("zero-rows-headered", "zero-rows-headerless")

# One perturbation per site the two zero-row predicates file, each
# aimed at the site it covers, in the shape of `_perturbations`: the
# name, the site's subcheck, and how the conforming file is edited.
#
# REVIEW ITEM P3-V4-F6. V8.1 says EVERY executable subcheck carries a
# named red case, and the coverage identity below reads that over the
# ordinary runs. On these two predicates nothing did, so a site there
# could be pinned to HELD -- `columns.order` on the headed zero-row
# form is the review's own witness -- and no test in this suite would
# notice. Every one of the fifteen sites is covered here, none is
# excused, and the coverage is checked in both directions: a site with
# no case is red, and a case naming a site the predicate does not file
# is red too.
def _zero_row_edits(text: str, names: "list[str]") -> "list[tuple[str, str, str | bytes]]":
    """Every registered edit of one conforming zero-row file."""
    joined = ",".join(names)
    built: list[tuple[str, str, str | bytes]] = [
        ("zero-byte-order-mark", "bytes.byte-order-mark", "﻿" + text),
        (
            "zero-carriage-returns",
            "bytes.line-endings",
            text.replace("\n", "\r\n") if text else "\r\n",
        ),
        # THE SAME ENCODING EDIT THE ORDINARY BATTERY MAKES, and it is
        # the same edit for a reason (review item P3-V4-F3, carried;
        # plan amendment A-P3-20). It used to be a UTF-16 byte-order
        # mark, which is a file the shipped READER refuses outright --
        # and now that a zero-row description reaches its report through
        # the reader like every other description, a file the reader
        # refuses comes back as that refusal rather than as a report,
        # exactly as it does on the ordinary path. So the edit is a
        # single Latin-1 byte: a file that is not UTF-8, that the reader
        # accepts through its documented fallback, and that leaves
        # `bytes.utf8` a verdict to reach.
        ("zero-not-utf8", "bytes.utf8", b"\xff" + text.encode("utf-8")[1:]),
        (
            "zero-nonempty",
            "bytes.zero-row-form",
            text + joined + "\n" if text else "1,north\n",
        ),
    ]
    if not text:
        return built + [
            # A HEADERLESS ZERO-ROW FILE IS ZERO BYTES, so the one
            # structural thing it can get wrong is writing the names.
            ("zero-header-written", "header.presence", joined + "\n"),
            # ...and its terminal newline is missed by the conforming
            # file itself, which is recorded rather than dressed up:
            # `dataclasses.replace` is the only way to build a zero-row
            # description at all -- the producer refuses a zero-row
            # table outright -- so this description carries the line
            # ending fact of the twenty-row file it was cut down from.
            ("zero-empty-file", "bytes.terminal-newline", ""),
        ]
    return built + [
        ("zero-no-terminal-newline", "bytes.terminal-newline", text[:-1]),
        (
            "zero-dropped-name",
            "columns.n_columns",
            ",".join(names[: len(names) - 1]) + "\n",
        ),
        (
            "zero-reordered",
            "columns.order",
            ",".join([names[1], names[0]] + names[2:]) + "\n",
        ),
        (
            "zero-renamed",
            "header.names",
            ",".join(["zz"] + names[1:]) + "\n",
        ),
        (
            "zero-no-header-at-all",
            "header.presence",
            ",".join("9" for _each in names) + "\n",
        ),
    ]


def test_a_conforming_zero_row_file_misses_nothing_it_can_hold(
    tmp_path: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
) -> None:
    """The green direction on the headed zero-row predicate.

    P3-D4: a file its own description asks for must not miss and must
    not trip the disclosure gate. The headed zero-row form asks for the
    header line, and that is the file this walks -- which is also what
    holds `_conforming_text`'s construction to the shipped reader,
    since a header line written the wrong way would miss here.

    THE HEADERLESS FORM IS RECORDED RATHER THAN ASSERTED, and the
    reason is not a defect in the validator. `synthtwin profile` refuses
    a zero-row table outright, in both header modes, so no producer can
    write a zero-row description and the only way to have one is to cut
    an ordinary description down -- which leaves it carrying the line
    ending fact of the file it was cut from. A file of no bytes then
    misses `bytes.terminal-newline`, correctly, against a description
    no producer would have written. That measurement is pinned as a red
    case below rather than asserted away.
    """
    for label, described, text, _sites in _predicate_sites(tmp_path, runs):
        if label != "zero-rows-headered":
            continue
        outcome = _measured(tmp_path, described, text, f"{label}-green.csv")
        bad = [
            f"{check.subcheck}: {check.verdict}"
            for check in outcome.checks
            if check.verdict in (validation.MISSED, validation.WITHHELD)
        ]
        assert not bad, (
            "the file this description asks for missed its own "
            f"obligations: {sorted(bad)}"
        )
        assert len(outcome.checks) >= 9, len(outcome.checks)


def test_the_predicate_walk_covers_every_predicate_that_file_names(
    tmp_path: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
) -> None:
    """`PREDICATE_FIXTURES` states the same four predicates as the runs.

    Two statements of what the predicates are is two things to drift.
    """
    labels = sorted(
        label for label, _d, _t, _o in _predicate_runs(tmp_path, runs)
    )
    assert labels == sorted(PREDICATE_FIXTURES), (
        f"this file names {sorted(PREDICATE_FIXTURES)} and the predicate "
        f"runs are {labels}"
    )
    for label in ZERO_ROW_PREDICATES:
        assert label in PREDICATE_FIXTURES, label


def test_every_site_of_every_zero_row_predicate_can_be_made_to_miss(
    tmp_path: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
) -> None:
    """V8.1 and V8.2 on the two predicates the coverage identity skipped.

    Each registered edit NAMES the site it covers and that site must
    report MISSED -- other subchecks failing alongside is fine, a site
    caught only by a neighbour is not. Then, in the other direction,
    every site the predicate files must be covered by one of them, so
    the walk cannot narrow, and no edit may name a site the predicate
    does not file.

    This is what closes the review's witness: `columns.order` on the
    headed zero-row form pinned to HELD passes every other assertion in
    this file and fails here, because the reordered header line no
    longer makes it miss.
    """
    for label, described, text, sites in _predicate_sites(tmp_path, runs):
        if label not in ZERO_ROW_PREDICATES:
            continue
        names = [column.name for column in described.columns]
        filed = {site.subcheck for site in sites}
        covered: set[str] = set()
        for edit, subcheck, made in _zero_row_edits(text, names):
            assert subcheck in filed, (
                f"{label}: the edit {edit} names {subcheck}, which this "
                f"predicate does not file at all"
            )
            outcome = _measured(
                tmp_path, described, made, f"{label}-{edit}.csv"
            )
            missed = {
                check.subcheck
                for check in outcome.checks
                if check.verdict == validation.MISSED
            }
            assert subcheck in missed, (
                f"{label}: the edit {edit} names {subcheck} and THAT "
                f"check did not report MISSED -- whatever else went "
                f"red, the named check did not do its job. It reported "
                f"{sorted(missed) or 'nothing missed at all'}"
            )
            covered.add(subcheck)
        uncovered = sorted(filed - covered)
        assert not uncovered, (
            f"{label}: these executable subchecks have no registered "
            f"edit, so nothing here shows they can fail at all:\n  "
            + "\n  ".join(uncovered)
        )
        assert filed, f"{label} filed no executable subcheck at all"


def test_every_registered_red_case_misses_the_site_it_names(
    battery: "dict[str, dict[str, Case]]",
    registered: "list[RedCase]",
) -> None:
    """V8.2: the case names the SITE, and that site must miss.

    Other subchecks failing alongside is fine. A perturbation caught
    only by a neighbour -- the mean tripping while a hard-coded rung
    check sleeps -- is a red battery, because the named check did not do
    its job. And a perturbation of one column caught only on ANOTHER
    column is the same failure at a finer grain (review item
    P3-V2-B-F4): it was accepted for as long as a case named a bare
    subcheck string.

    THE COMPARISON IS THE WHOLE SITE, THE REGISTRY FACT INCLUDED
    (review item P3-V3-F7). It was the column and the subcheck, so the
    registry could rebind a subcheck to another fact with every case
    still passing. And it is asked of EVERY registered case, curated or
    covering, because coverage is now credited to nothing else.
    """
    for case in sorted(registered):
        assert case.perturbation in battery[case.fixture], (
            f"{case.fixture}/{case.perturbation} was not built, so the "
            f"case names a perturbation this battery does not make"
        )
        reached = battery[case.fixture][case.perturbation].missed
        assert Site(case.column, case.fact, case.subcheck) in reached, (
            f"the red case {case.fixture}/{case.perturbation} names "
            f"{case.subcheck} ({case.fact}) on column {case.column!r}, "
            f"and THAT check did not report MISSED -- so whatever else "
            f"went red, the named check did not do its job"
        )


def test_no_two_sites_of_one_fixture_share_a_name(
    tmp_path: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
) -> None:
    """A column and a subcheck name ONE entry, which the table relies on.

    `COVERING_RED_CASES` names its sites by column and subcheck and
    takes the registry fact off the shipped table. That is only honest
    while the pair identifies one entry: two sites sharing a column and
    a subcheck under different facts would make a covering row ambiguous
    and would hide one of the two from the coverage identity. It is
    asserted rather than assumed, on the shipped table itself.
    """
    for name, described, twin in runs:
        outcome = _measured(tmp_path, described, twin, f"{name}-names.csv")
        seen: dict[tuple[str, str], str] = {}
        for site in _sites_of(outcome):
            key = (site.column, site.subcheck)
            if key in seen:
                assert seen[key] == site.fact, (
                    f"{name}: {site.column}: {site.subcheck} is filed "
                    f"under two registry facts, {seen[key]} and "
                    f"{site.fact}, so naming the pair names neither"
                )
            seen[key] = site.fact


def test_a_registered_case_is_aimed_at_the_site_it_covers(
    registered: "list[RedCase]",
    runs: "list[tuple[str, contract.Profile, str]]",
) -> None:
    """V8.2 at the grain of the identity: the edit is aimed at the site.

    A site "covered" by an edit that destroyed some other column, or by
    a whole-file edit that took every column down with it, is the
    complaint V8.2 makes about a check caught by a neighbour -- the
    miss is the wreckage and not the measurement. So a derived row of
    `COVERING_RED_CASES` must be an edit of the site's OWN column, and a
    document-level site must be covered by an edit of no column at all.

    ONE SITE IN THE DERIVED TABLE IS NOT, and it is named here rather
    than waved through by a rule with a hole in it: `styles.remainder`
    on the `spelled` fixture's one column, which no edit named for that
    column reaches -- each of those either leaves the remainder where it
    is or moves the role -- and which `added-row` reaches by repeating a
    row, an edit that writes one more cell into that same column.

    THE CURATED ROWS ARE NOT WALKED HERE, and that is deliberate rather
    than an oversight: a hand chose each of them against a finding, with
    the reason written beside it, and several are whole-file edits ON
    PURPOSE -- a column swap is the edit a position check exists for,
    and a file that stops short is the only thing the last column's
    position can miss on. A rule that read their names would have to
    call those wreckage, which they are not.
    """
    allowed = {("spelled", "reading", "styles.remainder")}
    curated = set(NAMED_RED_CASES)
    columns = {
        name: [column.name for column in described.columns]
        for name, described, _twin in runs
    }
    for case in sorted(registered):
        if case in curated:
            continue
        if (case.fixture, case.column, case.subcheck) in allowed:
            continue
        mine = columns[case.fixture]
        if case.column:
            assert case.perturbation.endswith(f"-{case.column}"), (
                f"{case.fixture}/{case.perturbation} is registered "
                f"against {case.subcheck} on column {case.column!r} and "
                f"is not an edit of that column, so what it shows is "
                f"that the check misses when something else was broken"
            )
            continue
        for other in mine:
            assert not case.perturbation.endswith(f"-{other}"), (
                f"{case.fixture}/{case.perturbation} is an edit of "
                f"column {other!r} and is registered against the "
                f"document-level {case.subcheck}"
            )


def test_the_coverage_identity_walks_the_shipped_table(
    tmp_path: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
    battery: "dict[str, dict[str, Case]]",
    registered: "list[RedCase]",
) -> None:
    """V8.3: every executable subcheck has a registered way to fail.

    THE IDENTITY IS WALKED, not a list written here: the entries come
    out of the shipped validator's own run over each conforming twin, so
    a subcheck added to the validator without a perturbation that can
    make it miss turns this red on the commit that adds it.

    AND IT IS WALKED AT THE SITE (review item P3-V2-B-F4). A red case
    covers an entry only when a perturbation of the SAME description
    made the SAME column's subcheck miss. Under the rule this replaces
    -- a set of subcheck names, pooled over every fixture -- 104 of the
    539 entries were covered by a same-named check somewhere else, and
    three checks that cannot fail at all sat inside that number.

    AND COVERAGE IS CREDITED TO A REGISTERED CASE AND TO NOTHING ELSE
    (review item P3-V3-F7). It used to be credited to the whole
    battery's collateral: any perturbation that happened to make a site
    miss covered it, whatever it had been built for. Two things followed
    and both were defects. A registration could be deleted and the suite
    stayed green, because another edit's wreckage went on counting --
    which is V8.3's "registered, named" read as though it said
    "reached". And a site could be covered only by an edit that broke
    something else, which is exactly the failure V8.2 refuses one grain
    up. The registration is now total over the shipped sites: 672 rows
    over 668 sites, 73 curated and 599 derived, each derived one an edit
    aimed at the site it covers. THREE sites carry more than one row on
    purpose: `columns.order` carries three, because it is the whole of
    what the shipped table files for the STRUCTURAL disposition and the
    floor below asks that class for three edits; `rows.n_rows` carries
    two, a row taken out and a row added; and the headerless
    `header.presence` carries the plain edit and the compensating one
    that used to defeat it. For those three, deleting one row is not
    enough to turn this red. Every one of the other 665 is on its own.

    NOTHING IS EXCUSED. There were two exemptions here and both are
    gone. A register of OPEN DEFECTS went with round 2's repairs. The
    other called three short-numeric counts unreachable and PROVED it
    from the role line -- and the proof was false, because it reasoned
    about the file's own description and the counts are taken over the
    blank split (review item P3-V3-F7): the publication floor's worth of
    cells spelling a missing marker moves all three while the role holds
    and the gate stays open. The `marked-<column>` perturbation is that
    edit, one fixture was lengthened so the edit fits in it, and all
    nine sites have registered cases. An exemption that is argued rather
    than constructed is how that hole was made, so there is no longer a
    place to park one.
    """
    covered: dict[str, set[Site]] = {}
    for case in registered:
        if case.perturbation not in battery[case.fixture]:
            continue
        found = Site(case.column, case.fact, case.subcheck)
        if found in battery[case.fixture][case.perturbation].missed:
            covered.setdefault(case.fixture, set()).add(found)
    uncovered: list[str] = []
    walked: dict[str, int] = {}
    for name, described, twin in runs:
        outcome = _measured(tmp_path, described, twin, f"{name}-green.csv")
        sites = _sites_of(outcome)
        walked[name] = len(sites)
        mine = covered.get(name, set())
        for site in sites:
            if site in mine:
                continue
            uncovered = uncovered + [f"{name}: {site.column}: {site.subcheck}"]
    assert not uncovered, (
        "these executable subchecks have no registered red case, so "
        "nothing in this suite shows they can fail at all:\n  "
        + "\n  ".join(sorted(set(uncovered)))
    )
    # ...and no row of the registration names a site the shipped table
    # does not carry. A dead row is a registration that proves nothing
    # and reads as though it proved something, which is the other half
    # of the same rot.
    dead: list[str] = []
    for name, described, twin in runs:
        outcome = _measured(tmp_path, described, twin, f"{name}-alive.csv")
        sites = set(_sites_of(outcome))
        for case in registered:
            if case.fixture != name:
                continue
            if Site(case.column, case.fact, case.subcheck) in sites:
                continue
            dead = dead + [
                (
                    f"{name}: {case.perturbation}: {case.column}: "
                    f"{case.subcheck} ({case.fact})"
                )
            ]
    assert not dead, (
        "these registered red cases name a site the shipped validator "
        "does not file, so they cover nothing:\n  " + "\n  ".join(sorted(dead))
    )
    # ...and the walk walked. An identity that reaches no entry is an
    # identity that holds whatever the validator does, which is the
    # failure this whole file exists to refuse.
    for name, filed in walked.items():
        assert filed, f"{name} filed no executable subcheck at all"


# THE TWO EXEMPTIONS ARE GONE, BECAUSE NEITHER WAS ONE.
#
# Round 2 found five executable subchecks the shipped validator filed
# against descriptions no file could make them miss on -- `axes.
# structural_role` on every column of every ordinary description,
# `styles.canonical.<form>` on a column whose published count is its own
# cell count, `moments.skew` where G12.3's own fallback is the whole
# attainable range, `position.at` on the first column of a headerless
# description, and `header.presence` in the headerless direction, which
# a compensating edit defeated. They were carried here as a REGISTER OF
# OPEN DEFECTS while they stood (review items P3-V2-C-F1, F2, F3, F7 and
# F8). Four are now listing entries with a sentence saying why nothing
# in a CSV settles them, recorded as lowerings in plan amendment
# A-P3-2; the fifth is a repaired check with two registered red cases.
#
# The replacement was a PROOF that no file could move three counts of a
# short numeric column without moving its role, and the proof was false
# (review item P3-V3-F7). It read the role line off the file's own
# description, where a cell spelling `na` is a hole -- and these three
# counts are taken over the BLANK SPLIT, where the same cell is a
# written cell that is not a number (V2.4, and plan amendment A-P3-5
# clause 1 for which of the two supplies the verdict). The publication
# floor's worth of such cells therefore moves all three while the role
# check HOLDS and the disclosure gate stays open, so an entry the
# coverage identity was skipping could be forced to HELD with the suite
# still green. `marked-<column>` is that edit, the `pooled` fixture was
# lengthened until the edit fits in it, and all nine sites now carry
# registered cases.
#
# NOTHING IS EXCUSED FROM THE COVERAGE IDENTITY ANY MORE. An exemption
# that is argued rather than constructed is how the last one was made,
# and an empty register policed by two tests would be two tests
# asserting nothing -- so neither is kept as a place for the next one to
# be parked.


# THE REGISTER OF OPEN DEFECTS IS GONE, BECAUSE THE DEFECTS ARE.
#
# Round 2 found five executable subchecks the shipped validator filed
# against descriptions no file could make them miss on -- `axes.
# structural_role` on every column of every ordinary description,
# `styles.canonical.<form>` on a column whose published count is its own
# cell count, `moments.skew` where G12.3's own fallback is the whole
# attainable range, `position.at` on the first column of a headerless
# description, and `header.presence` in the headerless direction, which
# a compensating edit defeated. They were carried here by name while
# they stood (review items P3-V2-C-F1, F2, F3, F7 and F8). Four are now
# listing entries with a sentence saying why nothing in a CSV settles
# them, recorded as lowerings in plan amendment A-P3-2; the fifth is a
# repaired check with two registered red cases. Nothing is excused from
# the coverage identity above but the PROVED exemption, and an empty
# register policed by two tests would have been two tests asserting
# nothing.


def test_the_vacuity_floor_counts_classes_per_disposition(
    tmp_path: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
    battery: "dict[str, dict[str, Case]]",
    registered: "list[RedCase]",
) -> None:
    """V8.5: a counted floor of red-case CLASSES per disposition class.

    The floor the first review found was four mutations over the whole
    battery, which a battery could meet while every exact fact in the
    product was covered by one shared edit. This one is counted per
    disposition: for each class the registry carries an obligation in,
    at least three DIFFERENT perturbation classes must have made some
    subcheck of that class miss.

    AND THE CLASSES ARE THE REGISTRY'S OWN (review item P3-V2-B-F9).
    The version this replaces walked a tuple of four disposition names
    written out by hand while `dispositions.DISPOSITIONS` carried six,
    so STRUCTURAL -- four registry facts, contributing the executable
    subcheck `columns.order` -- was exempt from the floor with no
    sentence anywhere saying so, and reached exactly one perturbation
    class. The classes are now read off the registry, and which of them
    the floor applies to is read off the shipped table: a disposition
    that carries no executable subcheck at all owes the floor nothing,
    and that is asserted rather than assumed, because REPORT-ONLY and
    LOADER-ONLY carrying one would be the vacuity of V3.4's other
    direction.
    """
    by_key = {
        f"{fact.group}.{fact.field}": fact for fact in dispositions.REGISTRY
    }

    def disposition_of(fact: str) -> str:
        if fact in validation.BYTE_RULE_FACTS:
            return "BYTE-RULE"
        return by_key[fact].disposition

    carried: dict[str, int] = {}
    for name, described, twin in runs:
        outcome = _measured(tmp_path, described, twin, f"floor-{name}.csv")
        for site in _sites_of(outcome):
            key = disposition_of(site.fact)
            carried[key] = carried.get(key, 0) + 1
    # WHICH CLASSES THE FLOOR APPLIES TO IS DERIVED, AND PINNED. Derived
    # alone would be a filter that quietly stops applying on the day a
    # class loses its last executable subcheck, which is the shape of
    # the hole this test is repairing. So the classes the shipped table
    # carries obligations in are named, and the floor is then required
    # of each of them.
    assert set(carried) == {
        dispositions.EXACT_OBSERVABLE,
        dispositions.EXACT_CONTROL,
        dispositions.APPROXIMATED,
        dispositions.STRUCTURAL,
        "BYTE-RULE",
    }, (
        "the classes the shipped entry table carries executable "
        f"subchecks in have changed: {sorted(carried)}. The floor is "
        "counted per class, so a class that arrives or leaves changes "
        "what this asserts and is read in the diff"
    )
    # AND THE CLASSES ARE COUNTED OVER THE REGISTRATION, not over every
    # miss the battery produces (review item P3-V3-F7). A floor counted
    # over collateral is a floor a battery meets by accident: an edit
    # built for one class, taking a neighbour of another class down with
    # it, used to count for that neighbour's floor. What has to be
    # varied is what this suite REGISTERS, so that is what is counted --
    # and each of those rows has already been shown to make the site it
    # names miss.
    kinds = {
        label: battery[name][label].kind
        for name in battery
        for label in battery[name]
    }
    classes: dict[str, set[str]] = {}
    for case in registered:
        if case.perturbation not in battery[case.fixture]:
            continue
        key = disposition_of(case.fact)
        if key not in classes:
            classes[key] = set()
        classes[key].add(kinds[case.perturbation])
    for disposition in dispositions.DISPOSITIONS + ("BYTE-RULE",):
        if disposition not in carried:
            continue
        assert disposition in classes, (
            f"the shipped table files {carried[disposition]} executable "
            f"subcheck(s) for {disposition} obligations and no "
            f"perturbation in this battery makes any of them miss, so "
            f"nothing shows that class can fail"
        )
        assert len(classes[disposition]) >= 3, (
            f"{disposition} obligations are made to miss by only "
            f"{sorted(classes[disposition])} -- fewer than three "
            f"distinct classes of perturbation, so this battery could "
            f"rot into one shared edit and stay green"
        )
    for disposition in (dispositions.REPORT_ONLY, dispositions.LOADER_ONLY):
        assert disposition not in carried, (
            f"the shipped table files an executable subcheck for a "
            f"{disposition} fact, which is a listing or input-side entry "
            f"dressed as a check"
        )
