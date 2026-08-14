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
of its own. The coverage identity below is now total but for the one
PROVED exemption, and reverting any of the five in memory turns it red
naming exactly the sites that finding named.

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

    Ten cells of one whole number and one each of two fractions: the two
    point-carrying spellings each cover one row, which is under the
    floor, so the description publishes the single pooled key and no
    count for either form. That is the shape the canonical-split
    subcheck exists for -- a pooled cell has no published form, so the
    only thing it can owe is its own value's canonical text -- and it is
    the shape review item P3-V1-F7 was found on.
    """
    values = ["1" for _index in range(10)] + ["1.5", "2.5"]
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
        built = built + [
            (
                f"moved-{name}",
                CLASS_DATE,
                _dated(described, twin, index, "moved"),
            ),
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
    """One registered red case, bound to the site it must make miss."""

    fixture: str
    perturbation: str
    column: str
    subcheck: str


# Each entry is one registered red case: the fixture and the
# perturbation, against the SITE it must make miss. A red case that
# names only the subcheck names a name, and a name is not an obligation
# (review item P3-V2-B-F4): `ladder.p50` missing on one column of a
# description says nothing about `ladder.p50` on another column of the
# same description, and the version this replaces could not tell the two
# apart. One perturbation may be registered against more than one site,
# which is why this is a list of cases and not a mapping from the edit.
NAMED_RED_CASES = (
    RedCase("every-role", "blanked-cell", "record_code", "presence.n_present"),
    RedCase("every-role", "moved-cell", "record_code", "length.min"),
    RedCase("every-role", "dropped-row", "", "rows.n_rows"),
    RedCase("every-role", "added-row", "", "rows.n_rows"),
    RedCase("every-role", "carriage-returns", "", "bytes.line-endings"),
    RedCase("every-role", "byte-order-mark", "", "bytes.byte-order-mark"),
    RedCase("every-role", "no-terminal-newline", "", "bytes.terminal-newline"),
    RedCase("every-role", "not-utf8", "", "bytes.utf8"),
    RedCase("every-role", "added-column", "", "columns.n_columns"),
    RedCase("every-role", "dropped-column", "", "columns.order"),
    RedCase("every-role", "swapped-1-2", "record_code", "position.at"),
    RedCase("every-role", "renamed-record_code", "", "header.names"),
    RedCase("every-role", "recased-region", "region", "levels.north.variants"),
    RedCase(
        "every-role",
        "spaced-region",
        "region",
        "levels.north.variants_withheld",
    ),
    RedCase(
        "every-role",
        "leading_zero-visits",
        "visits",
        f"styles.exact.{parsing.STYLE_LEADING_ZERO}",
    ),
    RedCase(
        "every-role",
        "leading_plus-visits",
        "visits",
        f"styles.exact.{parsing.STYLE_LEADING_PLUS}",
    ),
    RedCase(
        "every-role",
        "exponent_upper-amount",
        "amount",
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
        f"styles.exact.{parsing.STYLE_LEADING_ZERO}",
    ),
    RedCase(
        "every-role",
        "floor-plussed-amount",
        "amount",
        f"styles.exact.{parsing.STYLE_LEADING_PLUS}",
    ),
    RedCase(
        "pooled",
        "noncanonical-reading",
        "reading",
        f"styles.canonical.{parsing.STYLE_DECIMAL}",
    ),
    RedCase(
        "spelled",
        "exponent_upper-reading",
        "reading",
        f"styles.at-least.{parsing.STYLE_EXPONENT_LOWER}",
    ),
    RedCase("every-role", "moved-recorded_on", "recorded_on", "date-ladder.min"),
    RedCase(
        "every-role",
        "timed-recorded_on",
        "recorded_on",
        "precision.time_precision",
    ),
    RedCase(
        "every-role",
        "subsecond-recorded_on",
        "recorded_on",
        "counts.subsecond_digits",
    ),
    RedCase(
        "every-role",
        "one-worded-recorded_on",
        "recorded_on",
        "counts.n_unparsed",
    ),
    RedCase("every-role", "mixed-recorded_on", "recorded_on", "offsets.earliest"),
    RedCase("every-role", "shortened-comment", "comment", "length.min"),
    RedCase("every-role", "lengthened-comment", "comment", "words.max"),
    RedCase(
        "every-role",
        "repeated-record_code",
        "record_code",
        "distinct.n_distinct_by_occurrences",
    ),
    RedCase(
        "every-role", "digits-record_code", "record_code", "counts.n_all_digits"
    ),
    RedCase("every-role", "filled-visits", "visits", "presence.n_missing"),
    RedCase("every-role", "crowded-visits", "visits", "ladder.p50"),
    RedCase("every-role", "crowded-amount", "amount", "ladder.p90"),
    RedCase("every-role", "raised-amount", "amount", "ladder.max"),
    RedCase("every-role", "zeroed-visits", "visits", "counts.n_zero"),
    RedCase("every-role", "negated-visits", "visits", "counts.n_negative"),
    RedCase("every-role", "fractioned-visits", "visits", "type.integer_valued"),
    RedCase(
        "every-role", "contradicted-visits", "visits", "counts.n_contradictory"
    ),
    RedCase(
        "every-role", "overflowed-visits", "visits", "counts.n_out_of_range"
    ),
    # FOUR OF THE TEN THE REGISTER OF GAPS CARRIED, all of them on the
    # numeric roles. Each is ONE cell in two hundred and forty, so the
    # column keeps the role the file's own description reads it as and
    # the disclosure gate stays open (review item P3-V2-B-F5).
    RedCase("every-role", "one-worded-amount", "amount", "counts.numeric_share"),
    RedCase(
        "every-role",
        "one-overflowed-amount",
        "amount",
        "counts.n_left_out_of_statistics",
    ),
    RedCase(
        "every-role",
        "one-underflowed-amount",
        "amount",
        "counts.n_negative_unrepresentable",
    ),
    RedCase("every-role", "vast-amount", "amount", "type.std_unrepresentable"),
    RedCase("every-role", "rewritten-recorded_on", "recorded_on", "axes.role"),
    RedCase("every-role", "rewritten-unused", "unused", "presence.n_present"),
    RedCase("every-role", "emptied-region", "region", "axes.quality_state"),
    RedCase("unrepresentable", "rewritten-overflow", "overflow", "axes.role"),
    RedCase(
        "unrepresentable", "blanked-overflow", "overflow", "presence.n_present"
    ),
    # ...and the three the register carried on the invention role, all
    # three of them one cell of the hundred and twenty (review item
    # P3-V2-B-F5). The last two are one edit: a bracketed negative is a
    # cell whose sign and whose wholeness are both unreadable, and the
    # register said an edit that changes a cell's class here changes the
    # role the file's own description reads the column as, which this
    # one does not.
    RedCase(
        "unrepresentable", "one-fractioned-overflow", "overflow", "counts.n_fraction"
    ),
    RedCase(
        "unrepresentable",
        "one-contradicted-overflow",
        "overflow",
        "counts.n_sign_unknown",
    ),
    RedCase(
        "unrepresentable",
        "one-contradicted-overflow",
        "overflow",
        "counts.n_whole_unknown",
    ),
    RedCase("headerless", "written-header", "", "header.presence"),
    # ...AND THE SAME EDIT WITH ITS PRICE PAID (review item
    # P3-V2-C-F8). The check used to ask for a header line AND a row
    # count above the published one, so writing the header and dropping
    # one record defeated it and it reported "no header line, the first
    # row is a record" about a file whose first line was the published
    # names. Both cases are registered: the second is what proves the
    # conjunct is gone.
    RedCase("headerless", "header-and-short", "", "header.presence"),
    RedCase("headerless", "swapped-1-2", "column_1", "axes.role"),
    RedCase("headerless", "crowded-column_1", "column_1", "ladder.p25"),
    RedCase("headerless", "dropped-column", "column_2", "position.at"),
    # EVERY NUMERIC COLUMN OF EVERY FIXTURE, on the subcheck that asks
    # whether a cell's text is a spelling of its own value at all
    # (review item P3-V2-C-F1). One named case per site, because the
    # whole finding was a check that held on one column while a
    # same-named one failed on another.
    RedCase("every-role", "padded-visits", "visits", "styles.spelled"),
    RedCase("every-role", "padded-reading", "reading", "styles.spelled"),
    RedCase("every-role", "padded-amount", "amount", "styles.spelled"),
    RedCase("pooled", "padded-reading", "reading", "styles.spelled"),
    RedCase("spelled", "padded-reading", "reading", "styles.spelled"),
    RedCase("headerless", "padded-column_1", "column_1", "styles.spelled"),
)


def test_every_registered_red_case_misses_the_subcheck_it_names(
    battery: "dict[str, dict[str, Case]]",
) -> None:
    """V8.2: the case names the SITE, and that site must miss.

    Other subchecks failing alongside is fine. A perturbation caught
    only by a neighbour -- the mean tripping while a hard-coded rung
    check sleeps -- is a red battery, because the named check did not do
    its job. And a perturbation of one column caught only on ANOTHER
    column is the same failure at a finer grain (review item
    P3-V2-B-F4): it was accepted for as long as a case named a bare
    subcheck string.
    """
    for case in sorted(NAMED_RED_CASES):
        assert case.perturbation in battery[case.fixture], (
            f"{case.fixture}/{case.perturbation} was not built, so the "
            f"case names a perturbation this battery does not make"
        )
        reached = {
            (site.column, site.subcheck)
            for site in battery[case.fixture][case.perturbation].missed
        }
        assert (case.column, case.subcheck) in reached, (
            f"the red case {case.fixture}/{case.perturbation} names "
            f"{case.subcheck} on column {case.column!r}, and THAT check "
            f"did not report MISSED -- so whatever else went red, the "
            f"named check did not do its job"
        )


def test_the_coverage_identity_walks_the_shipped_table(
    tmp_path: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
    battery: "dict[str, dict[str, Case]]",
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

    ONE KIND OF ENTRY IS EXCUSED, and it is PROVED from the
    description's own published numbers by
    `_no_file_can_move_this_and_keep_the_role` below. There was a second
    -- a register of OPEN DEFECTS, five entries that could not fail
    because the CHECK could not fail -- and it is gone, because all five
    are repaired (review items P3-V2-C-F1, F2, F3, F7 and F8). An empty
    register policed by two assertions is two assertions asserting
    nothing, so the register and its tests went with the defects rather
    than staying as a place for the next one to be parked.
    """
    uncovered: list[str] = []
    walked: dict[str, int] = {}
    for name, described, twin in runs:
        reached: set[Site] = set()
        for label in battery[name]:
            reached = reached | battery[name][label].missed
        outcome = _measured(tmp_path, described, twin, f"{name}-green.csv")
        walked[name] = len(_sites_of(outcome))
        for site in _sites_of(outcome):
            if site in reached:
                continue
            if _no_file_can_move_this_and_keep_the_role(described, site):
                continue
            uncovered = uncovered + [f"{name}: {site.column}: {site.subcheck}"]
    assert not uncovered, (
        "these executable subchecks have no registered red case, so "
        "nothing in this suite shows they can fail at all:\n  "
        + "\n  ".join(sorted(set(uncovered)))
    )
    # ...and the walk walked. An identity that reaches no entry is an
    # identity that holds whatever the validator does, which is the
    # failure this whole file exists to refuse.
    for name, filed in walked.items():
        assert filed, f"{name} filed no executable subcheck at all"


# The three counts a numeric column publishes when every one of its
# written cells is a number this format can hold, and the value each
# takes there.
_ALL_NUMERIC_COUNTS = {
    "counts.numeric_share": "1.0",
    "counts.n_left_out_of_statistics": "0",
    "counts.n_negative_unrepresentable": "0",
}


def _no_file_can_move_this_and_keep_the_role(
    described: contract.Profile, site: Site
) -> bool:
    """Whether the producer's own role line leaves this entry no file.

    A PROOF, not an excuse, and it is the second of the two kinds of
    entry the coverage identity may pass over. Each of the three counts
    above moves only when the column holds a written cell that is not a
    number this format can hold. The producer decides the numeric roles
    on a COUNT -- at least `minimum_parse_rate` of the written cells
    must read as numbers it can hold -- so a column has room for
    `n_present - needed` such cells before the file's own description
    reads it as a column of another kind. Where that room is NONE, every
    file that moves one of these counts is a file whose role check
    MISSES and whose numeric block V5.3 requires to be withheld: the
    entry cannot reach MISSED, and no perturbation is hiding.

    The room is none for every column of fewer than a hundred written
    cells, which is three of the five fixtures here; the every-role
    fixture's numeric columns have room for two, and all three counts
    are reached on each of them by a single edited cell. So this is a
    statement about short columns and not about the checks, and
    `test_the_proof_excuses_nothing_a_red_case_reaches` holds it to
    exactly that.

    Nothing about this is a bar being lowered: the obligation stands,
    the check is real, and on a description with room it is one edited
    cell away from missing.
    """
    wanted = _ALL_NUMERIC_COUNTS.get(site.subcheck)
    if wanted is None:
        return False
    for column in described.columns:
        if column.name != site.column:
            continue
        if column.role not in NUMERIC_ROLES:
            return False
        return _needs_every_written_cell(described, column)
    return False


def _needs_every_written_cell(
    described: contract.Profile, column: contract.ColumnBlock
) -> bool:
    """Whether the numeric role line leaves this column no room at all.

    The producer applies its rate as a whole number of cells, never as a
    compared share, so this counts the same way: the smallest whole
    number of cells that reaches the rate, against how many the column
    has.
    """
    exact = described.settings.minimum_parse_rate * column.n_present
    whole = int(exact)
    needed = whole + 1 if whole < exact else whole
    return needed >= column.n_present


def test_the_proof_excuses_nothing_a_red_case_reaches(
    tmp_path: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
    battery: "dict[str, dict[str, Case]]",
) -> None:
    """The proved exemption, watched from both ends.

    A proof that quietly covered entries a perturbation DOES reach would
    be an excuse wearing a proof's clothes -- it would go on holding
    after the day somebody made one of them falsifiable. So: every entry
    the proof passes over is one the battery really does not reach, and
    the proof is not empty, and on the one fixture whose columns have
    room the same three counts are all reached by a red case.
    """
    excused = 0
    for name, described, twin in runs:
        reached: set[Site] = set()
        for label in battery[name]:
            reached = reached | battery[name][label].missed
        outcome = _measured(tmp_path, described, twin, f"{name}-proof.csv")
        for site in _sites_of(outcome):
            if not _no_file_can_move_this_and_keep_the_role(described, site):
                continue
            excused = excused + 1
            assert site not in reached, (
                f"{name}: {site.column}: {site.subcheck} is excused by a "
                f"proof that no file can make it miss, and a registered "
                f"perturbation makes it miss"
            )
    assert excused, "the proof excuses nothing here, so it asserts nothing"
    # ...and where the room is not none, all three are covered: the
    # proof is about the length of a column and not about the checks.
    for name, described, twin in runs:
        reached = set()
        for label in battery[name]:
            reached = reached | battery[name][label].missed
        for column in described.columns:
            if column.role not in NUMERIC_ROLES:
                continue
            if _needs_every_written_cell(described, column):
                continue
            for subcheck in sorted(_ALL_NUMERIC_COUNTS):
                assert any(
                    site.column == column.name and site.subcheck == subcheck
                    for site in reached
                ), f"{name}: {column.name}: {subcheck}"


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
    classes: dict[str, set[str]] = {}
    for name in battery:
        for label in battery[name]:
            case = battery[name][label]
            for site in case.missed:
                key = disposition_of(site.fact)
                if key not in classes:
                    classes[key] = set()
                classes[key].add(case.kind)
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
