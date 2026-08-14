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
(592 rows over 588 sites, 73 curated and 519 derived); each derived row
must be an edit aimed
at the site it covers; the floor is counted over the registration; and
nothing is excused at all.

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


def _ladder_crushed(
    described: contract.Profile, text: str, index: int
) -> str:
    """A datetime column with its two ends kept and its middle piled low.

    THE PERTURBATION THE NINE INTERIOR RUNGS ANSWER FOR ON THEIR OWN,
    written for EVERY resolution rather than for the two that name an
    instant (review item P3-V3-F4). The first and last written cells are
    left exactly where they are, so `earliest`, `latest` and both ENDS
    of the ladder still hold; every cell between them is moved into the
    lower half of the published range, spread over as many different
    values as that half holds, so the column keeps its role, its
    resolution, its precision and a cardinality like its own. What is
    left to catch the file is the nine rungs between the ends -- which
    is the shape the quarter finding was found on, where all nine were
    withheld whatever the file held.

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
    place = 0
    for row in written:
        if row in keep:
            continue
        rows[row][index] = generation._cell_of_ordinal(
            low + (place % half),
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
        body = f"wo rd {step}"
        if longer:
            body = f"wo rd {step} " + "and more words " * 12
        rows[row][index] = body
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

NUMERIC_ROLES = ("count", "continuous")
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
    if column.role in NUMERIC_ROLES:
        for tag, value in FLOOR_STYLE_VALUES:
            built = built + [
                (
                    f"floor-{tag}-{name}",
                    CLASS_SPELLING,
                    _floor_cells(described, twin, index, value),
                )
            ]
    if column.role in NUMERIC_ROLES:
        built = built + [
            (f"spread-{name}", CLASS_SHAPE, _numbered(described, twin, index)),
            (
                f"raised-{name}",
                CLASS_SHAPE,
                _raised_end(described, twin, index),
            ),
            (
                f"crowded-{name}",
                CLASS_SHAPE,
                _compressed(described, twin, index),
            ),
            (
                f"enormous-{name}",
                CLASS_MANY_CELLS,
                _classed(described, twin, index, "1e200", 2),
            ),
            (
                f"zeroed-{name}",
                CLASS_MANY_CELLS,
                _classed(described, twin, index, "0"),
            ),
            (
                f"negated-{name}",
                CLASS_MANY_CELLS,
                _classed(described, twin, index, "-8"),
            ),
            (
                f"worded-{name}",
                CLASS_MANY_CELLS,
                _classed(described, twin, index, "zz"),
            ),
            (
                f"bracketed-{name}",
                CLASS_MANY_CELLS,
                _classed(described, twin, index, "(4)"),
            ),
            (
                f"overflowed-{name}",
                CLASS_MANY_CELLS,
                _classed(described, twin, index, "9e999"),
            ),
            (
                f"underflowed-{name}",
                CLASS_MANY_CELLS,
                _classed(described, twin, index, "-9e999"),
            ),
            (
                f"fractioned-{name}",
                CLASS_MANY_CELLS,
                _classed(described, twin, index, "1.5"),
            ),
            (
                f"contradicted-{name}",
                CLASS_MANY_CELLS,
                _classed(described, twin, index, "(-4)"),
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
            built = built + [
                (
                    f"{style}-{name}",
                    CLASS_SPELLING,
                    _restyled(described, twin, index, style),
                )
            ]
    if column.role in NUMERIC_ROLES or column.role == "numeric_unrepresentable":
        built = built + [
            (f"vast-{name}", CLASS_SHAPE, _huge_spread(described, twin, index))
        ]
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
            )
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
    """Every executable subcheck one run filed, as sites."""
    return [
        Site(check.column, check.fact, check.subcheck)
        for check in outcome.checks
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
            ("spread-amount", "distinct.n_distinct"),
            ("spread-amount", "distinct.n_distinct_folded"),
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
            ("fractioned-reading", "distinct.n_distinct"),
            ("fractioned-reading", "distinct.n_distinct_folded"),
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
            ("crushed-when", "date-ladder.p10"),
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


@pytest.fixture(scope="module")
def registered(
    tmp_path_factory: pytest.TempPathFactory,
    runs: "list[tuple[str, contract.Profile, str]]",
) -> "list[RedCase]":
    """The whole registration: the curated rows, then the covering ones.

    A covering row names its site by column and subcheck, and the
    registry fact is read off the shipped table -- which
    `test_no_two_sites_of_one_fixture_share_a_name` proves is one entry
    and not two. A covering row that names no shipped site is kept,
    fact and all, so that the coverage identity reports it as a dead row
    rather than dropping it silently.
    """
    folder = tmp_path_factory.mktemp("registration")
    cases = list(NAMED_RED_CASES)
    for name, described, twin in runs:
        outcome = _measured(folder, described, twin, f"{name}-registered.csv")
        facts = {
            (site.column, site.subcheck): site.fact
            for site in _sites_of(outcome)
        }
        for column in sorted(COVERING_RED_CASES.get(name, {})):
            for perturbation, subcheck in COVERING_RED_CASES[name][column]:
                cases = cases + [
                    RedCase(
                        name,
                        perturbation,
                        column,
                        facts.get((column, subcheck), "(no such site)"),
                        subcheck,
                    )
                ]
    return cases


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
    up. The registration is now total over the shipped sites: 592 rows
    over 588 sites, 73 curated and 519 derived, each derived one an edit
    aimed at the site it covers. THREE sites carry more than one row on
    purpose: `columns.order` carries three, because it is the whole of
    what the shipped table files for the STRUCTURAL disposition and the
    floor below asks that class for three edits; `rows.n_rows` carries
    two, a row taken out and a row added; and the headerless
    `header.presence` carries the plain edit and the compensating one
    that used to defeat it. For those three, deleting one row is not
    enough to turn this red. Every one of the other 585 is on its own.

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
