"""Review item P2-C1-F4: approximated facts owe a bound and an honest report.

The profile contract gives every published field one disposition, and
APPROXIMATED means the field is "reproduced under a stated rule inside a
two-sided finite-sample bound", MEASURED from the written CSV, checked
against BOTH ends, and named in the generation report with the achieved
value beside the published one (`docs/spec/profile-contract-v4.md`
section 2.2). Round 1 found the obligation unmet in three ways at once:
no bound existed for `mean`, `std` or `skew` at all -- the method
delegated that normative job to a test battery -- no independent
measurement of the twin existed for any of the other approximated
families, and the report printed neither an achieved value nor a bound
outcome for any of them.

WHAT THIS FILE HOLDS THE REPAIR TO, in the order the item asks for it:

1. every APPROXIMATED cell of the contract's matrix is measured, and
   nothing outside that matrix is measured under this disposition;
2. every bound has two FINITE ends, and the twin's own value is checked
   against both;
3. every one of them reaches the report, with the published value, the
   achieved value, both ends and the answer;
4. every bound is proved ABLE TO FAIL by putting a deliberately broken
   twin through the SAME shipped measurement -- because a bound no wrong
   twin can leave is not a check, and a report full of such bounds is
   worse than no report at all.

Point 4 is what the rest of the file exists for. Each mutant below is
the column a differently broken generator would have written: one that
collapsed the interior rungs onto the two ends, one that shrank the
spread, one that mirrored the shape, one that wrote every date the same,
one that wrote a date per row where the published range holds twelve,
one that mislaid a character, one that dropped the spaces, one that
invented a spelling. Every one of them is measured by
`generation._approximations` itself -- the function the shipped run
calls -- so what is proved able to fail is the check in force and not a
copy of it written in a test.

The descriptions are built by the REAL producer from seeded neutral
tables (plan D13: no data-format file is ever committed), so the whole
path from table to bound runs here.
"""

import dataclasses
import math
import pathlib
import re
import typing

import pytest

import dispositions
import fixtures
from synthtwin import (
    contract,
    generation,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

SPEC = pathlib.Path(__file__).resolve().parent.parent / "docs" / "spec"

# THE CONTRACT THAT GOVERNS, derived from the loader's own constant
# rather than named. A reader pinned to a number is how residual
# R-P4-25 happened: the producer and the loader moved and these
# governance checks went on reading an older document, agreeing by
# luck. Deriving it means a version bump moves this reader with the
# code or fails loudly (review item P4-A1-R2-F6).
MATRIX_CONTRACT = fixtures.GOVERNING_CONTRACT


def _described(
    folder: pathlib.Path, text: str, declared: "list[str] | None" = None
) -> contract.Profile:
    """Write a table, describe it with the producer, load the description."""
    path = fixtures.write(folder, "table.csv", text)
    table = reading.read_table(str(path))
    document = profile.build_document(
        table, taxonomy.Settings(), declared if declared else []
    )
    target = fixtures.write_profile(folder, "table-profile.json", document)
    return contract.load_profile(str(target))


# -- the descriptions every test below is measured against ------------


@pytest.fixture(scope="module")
def every_role(tmp_path_factory: pytest.TempPathFactory) -> contract.Profile:
    """One column for nearly every role, from the shared neutral table."""
    folder = tmp_path_factory.mktemp("f4-every-role")
    return _described(folder, fixtures.every_role_table(), ["record_code"])


@pytest.fixture(scope="module")
def twin(every_role: contract.Profile) -> generation.Twin:
    """The twin of that description, built once."""
    return generation.generate(every_role, 20260811)


def _bent_ladder_text() -> str:
    """Two hundred squares: a column whose ladder is materially bent.

    The same neutral fixture the rung battery in `test_generation.py`
    uses, and for the same reason: half its values sit in the bottom
    quarter of its range, so a generator that read only the two ends
    produces a visibly different column rather than nearly the same one.
    A column of evenly spread numbers would let every mutant below pass,
    and a mutant that passes proves nothing.
    """
    return fixtures.single_column_table(
        "reading", [f"{step * step}" for step in range(1, 201)]
    )


@pytest.fixture(scope="module")
def bent(tmp_path_factory: pytest.TempPathFactory) -> contract.Profile:
    """The producer's own description of that bent-ladder column."""
    folder = tmp_path_factory.mktemp("f4-bent")
    return _described(folder, _bent_ladder_text())


@pytest.fixture(scope="module")
def narrow_dates(
    tmp_path_factory: pytest.TempPathFactory,
) -> contract.Profile:
    """240 rows of dates over twelve days, so the range is the ceiling.

    The number of different values a datetime column can hold is bounded
    above by the number of instants its published range holds at its
    published precision (method G12.5). On a column whose range is wider
    than the column is long that ceiling is the row count and cannot be
    exceeded by anything; here it is twelve, so a generator that wrote a
    different date per row has somewhere to be caught.
    """
    folder = tmp_path_factory.mktemp("f4-narrow-dates")
    days = [f"2024-03-{(step % 12) + 1:02d}" for step in range(240)]
    return _described(folder, fixtures.single_column_table("day", days))


def _place_of(loaded: contract.Profile, name: str) -> int:
    """Where one column sits in the description's own order."""
    for place in range(len(loaded.columns)):
        if loaded.columns[place].name == name:
            return place
    raise AssertionError(f"no column named {name}")


def _measure(
    loaded: contract.Profile, name: str, cells: "list[str]"
) -> "list[generation.Approximation]":
    """Put ``cells`` through the SHIPPED measurement for one column.

    The plan is the real one this description produces, so the window
    the bound is drawn from is the window the run itself would use; only
    the CELLS are replaced. That is what makes a mutant below a test of
    the check in force rather than of a second implementation of it.
    """
    plan = generation.plan_generation(loaded)
    place = _place_of(loaded, name)
    return generation._approximations(
        loaded.columns[place], plan.columns[place], cells
    )


def _cells(twin: generation.Twin, name: str) -> "list[str]":
    """One column of the twin, in row order."""
    for place in range(len(twin.names)):
        if twin.names[place] == name:
            return list(twin.columns[place])
    raise AssertionError(f"no column named {name}")


def _found(
    measured: "list[generation.Approximation]", fact: str
) -> generation.Approximation:
    """The one record for a named fact, or a failure saying it is absent."""
    for record in measured:
        if record.fact == fact:
            return record
    raise AssertionError(
        f"no approximated fact named {fact} was measured; measured: "
        f"{[record.fact for record in measured]}"
    )


# -- 1. the matrix says what is approximated, and exactly that is measured


# The nine INTERIOR rungs of a ladder, which the matrix names by their
# container: "`percentiles` interior rungs (`p01` … `p99`)". The two
# ends are named in their own row and are EXACT-OBSERVABLE.
RUNGS = (
    "p01", "p05", "p10", "p25", "p50", "p75", "p90", "p95", "p99",
)

# The containers whose interior rungs the matrix disposes as one row.
# `clock_percentiles` joins now that the clock role is READ out of
# version 6's own table rather than having its inventory stated.
NUMERIC_SECTION = (
    "9.4 The numeric roles: `count`, `continuous`, `affixed_number`"
)
LABEL_SECTION = (
    "9.5 The label roles: `constant`, `binary`, `categorical`, "
    "`long_tail_labels`"
)

RUNG_HOLDERS = ("percentiles", "date_percentiles", "clock_percentiles")


# A bold line naming ONE role opens that role's sub-table inside a
# shared numbered section -- 9.4's affixed block, 9.6's two roles, 9.7's
# three. A bold naming several ("`count` and `continuous`") opens
# nothing, so those rows stay under the numbered heading.
_SUB_TABLE = re.compile(r"^\*\*`([a-z_]+)`\.?\*\*")

# A role named in a parenthetical qualifier is not a field: 9.5 reads
# "`level_ceiling` (`categorical` only)". Matched on shape rather than
# against a list of role names, because `count` is both a role and a
# real sub-key of the `levels` row.
_QUALIFIER = re.compile(r"\(`[a-z_]+` only\)")


def _unqualified(cell: str) -> str:
    """The first cell of a row, as KEY NAMES.

    Two things are stripped, and neither is part of a key. A role
    named in a parenthetical qualifier -- "`level_ceiling`
    (`categorical` only)" -- is a scope note. And a trailing `[]`
    is ARRAY NOTATION: 9.4a writes `parts[]` for the key the
    producer emits as `parts`, one block per position.
    """
    return _QUALIFIER.sub("", cell).replace("[]`", "`")


def _sub_table(line: str, heading: str) -> "str | None":
    """The heading a bold role line opens, or None if it opens nothing."""
    if not heading:
        return None
    found = _SUB_TABLE.match(line.strip())
    if found is None or found.group(1) not in dispositions.ROLES:
        return None
    return f"{heading.split()[0]} {found.group(1)}"


def _matrix_rows() -> "dict[str, list[tuple[tuple[str, ...], str]]]":
    """Section 9 of the profile contract, as ORDERED rows per table.

    Each entry is the backticked names in a row's first cell against
    that row's disposition text, in the order the contract writes them.
    Order matters here: the inventory below is derived from it, and the
    run emits its measurements in the same order.
    """
    text = MATRIX_CONTRACT.read_text(encoding="utf-8")
    start = text.index("## 9. The disposition matrix")
    body = text[start:text.index("\n## ", start + 10)]
    sections: dict[str, list[tuple[tuple[str, ...], str]]] = {}
    heading = ""
    for line in body.split("\n"):
        if line.startswith("### "):
            heading = line[4:].strip()
            sections.setdefault(heading, [])
            continue
        opened = _sub_table(line, heading)
        if opened is not None:
            heading = opened
            sections.setdefault(heading, [])
            continue
        if not line.startswith("|") or not heading:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2 or set(cells[0]) <= set("-: "):
            continue
        sections[heading].append(
            (tuple(re.findall(r"`([^`]+)`", _unqualified(cells[0]))), cells[1])
        )
    return sections


def _approximated_of(rows: "list[tuple[tuple[str, ...], str]]") -> "tuple[str, ...]":
    """Every APPROXIMATED field of one matrix table, in the matrix's order.

    DERIVED, NEVER TRANSCRIBED (review item P2-C2-F4). Round 2 found a
    hand-written inventory that omitted the two numeric cardinalities --
    fields the matrix disposes with a CONDITIONAL clause, "exact where
    the permitted spellings supply the count, APPROXIMATED where they
    do not" -- so the test agreed with an implementation that measured
    neither while disagreeing with both normative tables. A list read
    out of the matrix cannot omit a conditional field, because the word
    APPROXIMATED appears in the row either way.
    """
    owed: list[str] = []
    for names, disposition in rows:
        if "APPROXIMATED" not in disposition:
            continue
        for name in names:
            if name in RUNG_HOLDERS:
                owed = owed + [f"{name}.{rung}" for rung in RUNGS]
            elif name not in RUNGS:
                owed = owed + [name]
    return tuple(owed)


APPROXIMATED = {
    role: _approximated_of(_matrix_rows()[section])
    for role, section in {
        "count": NUMERIC_SECTION,
        "continuous": NUMERIC_SECTION,
        "datetime": "9.6 datetime",
        "free_text": "9.7 free_text",
        "constant": LABEL_SECTION,
        "binary": LABEL_SECTION,
        "categorical": LABEL_SECTION,
        # The affixed role's quantitative block IS the numeric block
        # read over the cores, so it owes what the numeric roles owe.
        # Version 6 restates those rows in its own sub-table; the
        # inventory is read from the numeric section either way, which
        # keeps one source for the approximations that carry a
        # distribution.
        "affixed_number": NUMERIC_SECTION,
        # A long tail publishes the label roles' own four keys and
        # nothing else, so it owes what they owe, read from their
        # section (plan P4-D5).
        "long_tail_labels": LABEL_SECTION,
        # The joined role's own table, whose one approximated fact is
        # the rank agreement of a pair of positions -- every pair since
        # landing L7 (contract 9.4a, plan P4-D25). Each position's own
        # ladder and its moments are
        # approximated too, but under the NUMERIC group's dispositions
        # read per position, which is where they are checked.
        "joined_numbers": "9.4a The joined role: `joined_numbers`",
        # READ, not stated. Version 6 gives this role its own table --
        # `clock_form`, both ladder ends, the interior rungs, the
        # unparsed count and the two distinctness counts -- so the
        # inventory comes out of the contract like every other role's.
        # Version 4 had no such table, which is why it used to be
        # written out here (residual R-P4-25).
        "time_of_day": "9.6 time_of_day",
        # The compound role's own table. Its four counts of different
        # cells are the only rows there that name an approximated
        # outcome -- each is EXACT-OBSERVABLE and falls to an envelope
        # where the published spellings cannot settle it -- and its two
        # halves' interiors are disposed in the numeric and label
        # sections, where they are read for those roles (contract 9.4b,
        # plan P4-D33). It was missing while the role shipped, so the
        # completeness walk below never reached it (review round 4 of
        # landing L8, item 3).
        "numbers_with_labels": (
            "9.4b The compound role: `numbers_with_labels`"
        ),
    }.items()
}

# NO ROLE'S INVENTORY IS STATED RATHER THAN READ ANY MORE. The clock
# role's three approximated facts used to be written out here, because
# the version 4 matrix this file read had no table for a role that
# version never had. Version 6 has one, so the inventory is read from
# it -- and the list version 6 produces is character for character the
# list that used to be written here, which is what says the migration
# kept the obligation rather than moving it (residual R-P4-25).
ROLES_STATED_RATHER_THAN_READ: "tuple[str, ...]" = ()


def _matrix_sections() -> "dict[str, dict[str, str]]":
    """The disposition matrix, read from both versions, as fields.

    Returns one mapping per matrix table, keyed by the heading version 4
    gives it, whose entries are every name in the first cell of a row
    against the disposition text in the second. Reading the contract
    rather than restating it is the point: a matrix that gains a field,
    loses one, or changes a disposition moves these tests.

    VERSION 6 IS READ ALONE, because it states the whole matrix and is
    the version that governs: `PROFILE_VERSION` is 6, so every
    description this tree writes is a version 6 one. This used to read
    version 4 merged with version 5's delta table -- the record of what
    two superseded versions required -- which is residual R-P4-25.
    """
    text = MATRIX_CONTRACT.read_text(encoding="utf-8")
    start = text.index("## 9. The disposition matrix")
    body = text[start:text.index("\n## ", start + 10)]
    sections: dict[str, dict[str, str]] = {}
    heading = ""
    for line in body.split("\n"):
        if line.startswith("### "):
            heading = line[4:].strip()
            sections.setdefault(heading, {})
            continue
        opened = _sub_table(line, heading)
        if opened is not None:
            heading = opened
            sections.setdefault(heading, {})
            continue
        if not line.startswith("|") or not heading:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2 or set(cells[0]) <= set("-: "):
            continue
        for name in re.findall(r"`([^`]+)`", _unqualified(cells[0])):
            sections[heading][name] = cells[1]
    return sections


# Which matrix table governs which role. `empty`, `identifier` and
# `numeric_unrepresentable` are here too, with no approximated field of
# their own, because a role missing from this map would silently escape
# the completeness check below.
#
# SIX FAMILIES OF EXEMPTION USED TO STAND HERE and are gone, because
# version 6 disposes what version 4 could not (residual R-P4-25): the
# affixed role's own seven keys, the clock role's own five, both width
# censuses, `shape_forms`, `resolution_mix`, and the unrepresentable
# role's two lengths. Every one of them is read out of the contract
# now. What remains below is exactly the family that landed AFTER
# amendment A-P4-46 froze the contract, which is disposed in the Phase
# 4 plan and checked against it by `dispositions.PLAN4_REGIONS`.

# ...the value histogram, which the owner asked for by name. It is
# EXACT-OBSERVABLE the way every census here is: put each of the twin's
# values in its bin by the published ends, count them, and the
# published census comes back. Disposed in the Phase 4 plan (P4-D4.7).
# The keys plan P4-D36 added to the affixed role (2026-09-04): the
# wrapper SET a column may wear, and the two counts of different
# CORES. They are EXACT-OBSERVABLE -- each is recounted from the
# twin's own text -- and are named here because the contract states
# them in prose rather than as rows of the role's sub-table.
AFFIX_SET_KEYS = (
    "affix_variants",
    "n_core_distinct",
    "n_core_distinct_folded",
)
PHASE_4_HISTOGRAM_KEYS = ("value_histogram",)

# ...and the kurtosis, the owner's own second ask of 2026-08-26. It is
# APPROXIMATED as the skewness beside it is, under a window method
# G12.3a states, and the Phase 4 plan disposes it (P4-D4.8).
PHASE_4_MOMENT_KEYS = ("kurtosis",)

# ...and the count of different NUMBERS, the owner's fourth ask and the
# close of residual R-P4-20. Disposed in the Phase 4 plan (P4-D4.9).
PHASE_4_VALUE_COUNT_KEYS = ("n_distinct_values",)

# Plan P4-D4.11. The mode pair takes the same disposition as the value
# count beside it and for the same reason: the generator carves no
# stratum sized to a published count except the zero one, so no file is
# held to the pair and the quality report LISTS it.
PHASE_4_MODE_KEYS = ("mode", "mode_count")

# Plan P4-D4.10. The finer ladder is REPORT-ONLY as ONE fact: no rung
# of it has a subcheck, and the fidelity comes from the generator
# interpolating it rather than from a file being held to any of them.
PHASE_4_FINER_LADDER_KEYS = ("percentiles_between",)

ROLE_SECTIONS = {
    "empty": "9.3 `empty`",
    "count": NUMERIC_SECTION,
    "continuous": NUMERIC_SECTION,
    "constant": LABEL_SECTION,
    "binary": LABEL_SECTION,
    "categorical": LABEL_SECTION,
    "datetime": "9.6 datetime",
    "free_text": "9.7 free_text",
    "identifier": "9.7 identifier",
    "numeric_unrepresentable": "9.7 numeric_unrepresentable",
    # The affixed role reads the NUMERIC section, because its
    # quantitative block IS the numeric block read over the cores
    # (AF7). Version 6 also gives it a sub-table of its own for the
    # seven keys it ADDS, and the walk merges that in -- so both halves
    # are read from the contract now, where the seven used to be
    # injected from a constant because version 4 predated the role.
    "affixed_number": NUMERIC_SECTION,
    # The clock role has its OWN table in version 6 and reads it. It
    # used to borrow the datetime section, which disposes the date
    # ladder and the offset fields it publishes none of, with its own
    # five keys injected from a constant (residual R-P4-25).
    "time_of_day": "9.6 time_of_day",
    # The long tail reads the LABEL section: its keys ARE the label
    # roles' keys, under the same invariants, and it publishes none of
    # its own (plan P4-D5). Version 6's heading names it outright.
    "long_tail_labels": LABEL_SECTION,
    # The joined role reads its OWN table, 9.4a -- which the contract
    # gained when the role was found to have none, and which this map
    # did not name until residual R-P4-62's landing. Its positions each
    # carry a numeric block and take 9.4's dispositions read over that
    # position; the keys below are the role's own.
    "joined_numbers": "9.4a The joined role: `joined_numbers`",
    # The compound role reads its OWN table, 9.4b. Its two sub-blocks
    # are containers this walk does not open -- the same treatment
    # `parts[]` gets one role above -- because the facts inside them
    # are the numeric and label groups' facts, disposed where those
    # groups are disposed and checked there.
    "numbers_with_labels": "9.4b The compound role: `numbers_with_labels`",
}


def test_the_inventory_is_read_out_of_the_matrix_and_misses_no_clause(
) -> None:
    """The inventory is the contract's own, conditional rows included.

    Two things are checked, and the second is the one round 2 found
    missing (review item P2-C2-F4). First, every fact the inventory
    carries is disposed APPROXIMATED by the row that names it. Second,
    every row of every table whose disposition holds the word
    APPROXIMATED reaches the inventory -- including the numeric
    cardinality row, whose clause reads "EXACT-OBSERVABLE ... falling
    back to the two-sided envelope", which a reader transcribing the
    word at the head of each row leaves out.
    """
    sections = _matrix_sections()
    for role, owed in APPROXIMATED.items():
        if role in ROLES_STATED_RATHER_THAN_READ:
            # Its inventory is stated beside the plan clauses that
            # decide it, above, and the registry is what holds those
            # decisions -- `tests/dispositions.py`, whose seal moves
            # when they do. Reading it out of a matrix written before
            # the role existed is what is impossible, not checking it.
            continue
        table = sections[ROLE_SECTIONS[role]]
        for fact in owed:
            found = table.get(fact)
            if found is None:
                found = table.get(fact.split(".")[0])
            assert found is not None, f"{role}/{fact} is in no matrix row"
            assert "APPROXIMATED" in found, (
                f"{role}/{fact} is disposed as {found}"
            )
    for role, section in ROLE_SECTIONS.items():
        if role in ROLES_STATED_RATHER_THAN_READ:
            continue
        for names, disposition in _matrix_rows()[section]:
            if "APPROXIMATED" not in disposition:
                continue
            for name in names:
                if name in RUNGS:
                    continue
                carried = [
                    fact for fact in APPROXIMATED.get(role, ())
                    if fact == name or fact.split(".")[0] == name
                ]
                assert carried, f"{role}: the matrix disposes {name} "
    assert "n_distinct" in APPROXIMATED["count"]
    assert "n_distinct_folded" in APPROXIMATED["continuous"]


def test_every_approximated_fact_of_every_role_is_measured(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    """Point 1 of the item: complete, per role, on a genuine description.

    The description covers nearly every role at once, so this walks the
    matrix and the twin together: for each column, the facts measured
    must be EXACTLY the approximated facts its role owes -- no fact
    missing, and no fact measured under a disposition the matrix does
    not give it.
    """
    for place in range(len(every_role.columns)):
        column = every_role.columns[place]
        measured = [
            record.fact for record in twin.outcomes[place].approximations
        ]
        owed = list(APPROXIMATED.get(column.role, ()))
        # THE VERSION 4 MATRIX HAS NO ROW FOR THE KURTOSIS, because
        # version 4 published no such key; the Phase 4 plan disposes it
        # APPROXIMATED (P4-D4.8) and the registry carries it, exactly as
        # it does for the other keys that arrived after that matrix was
        # written. It is measured immediately after the skewness, which
        # is the order the description writes the moments in.
        if "skew" in owed:
            owed.insert(owed.index("skew") + 1, "kurtosis")
        # THE AFFIXED ROLE PUBLISHES THE TWO DISTINCTNESS COUNTS UNDER
        # ITS OWN NAMES, which is AF7's substitution and is what a
        # report must name (review round 4 of landing L14, item 4). The
        # inventory is read from the NUMERIC section, where they are
        # `n_distinct` and `n_distinct_folded`; this column publishes
        # `n_core_distinct` and `n_core_distinct_folded`, and a record
        # naming the numeric spelling names a key the description does
        # not carry.
        if column.role == "affixed_number":
            owed = [
                f"n_core_{one[2:]}" if one.startswith("n_distinct") else one
                for one in owed
            ]
        assert measured == owed, f"{column.name} ({column.role})"


def test_every_approximated_fact_of_the_compound_role_is_measured(
    numbers_with_labels_document: "dict[str, typing.Any]",
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """The same completeness, on the role the shared table cannot hold.

    REVIEW ROUND 5 OF LANDING L8, item 6. The inventory above gained a
    row for `numbers_with_labels` and nothing measured one: the walk
    reads the shared every-role description, which has no compound
    column, so the whole role's report -- four counts of different
    cells and a whole quantitative block -- was covered by nothing.

    WHAT THIS ROLE OWES is two tables added: 9.4b's four counts, which
    are its own, and the NUMERIC section's rungs and moments, which its
    numeric half carries and which are measured over that half.
    """
    folder = tmp_path_factory.mktemp("f4-compound-approximations")
    written = fixtures.write_profile(
        folder, "compound-profile.json", numbers_with_labels_document
    )
    described = contract.load_profile(str(written))
    twin = generation.generate(described, 7)
    measured = [record.fact for record in twin.outcomes[0].approximations]
    numeric = list(APPROXIMATED["continuous"])
    if "skew" in numeric:
        numeric.insert(numeric.index("skew") + 1, "kurtosis")
    # ...and the LABEL half's own count of different spellings, which
    # is the label section's approximated fact read over that half and
    # is named for the half it belongs to (review round 6, item 1).
    owed = (
        [
            name
            for name in numeric
            if name not in ("n_distinct", "n_distinct_folded")
        ]
        + list(APPROXIMATED["numbers_with_labels"])
        + ["labels -> n_distinct"]
    )
    assert sorted(measured) == sorted(owed), sorted(measured)
    # ...and the four counts each carry BOTH ends of their window, which
    # is what makes the fallback checkable (review item P2-C2-F4).
    # ...and the six carry ENDS THAT ARE THE HALVES' ENDS ADDED, which
    # is the arithmetic round 6 found assumed away (item 1): a first
    # writing shifted the numeric half's window by the label half's
    # PUBLISHED count, so a label half that cannot supply its own
    # spellings made the outer record say the twin held every value it
    # published while the same page said otherwise.
    windows = {
        record.fact: record
        for record in twin.outcomes[0].approximations
        if "distinct" in record.fact
    }
    # EQUALITY on both ends (review round 7, item 5). `<=` and `>=`
    # let a mutant widen every outer window by one in each direction,
    # authorizing counts neither half permits.
    assert int(windows["n_distinct"].achieved) == int(
        windows["n_numeric_distinct"].achieved
    ) + int(windows["labels -> n_distinct"].achieved)
    assert int(windows["n_distinct"].lowest) == int(
        windows["n_numeric_distinct"].lowest
    ) + int(windows["labels -> n_distinct"].lowest)
    assert int(windows["n_distinct"].highest) == int(
        windows["n_numeric_distinct"].highest
    ) + int(windows["labels -> n_distinct"].highest)
    for record in twin.outcomes[0].approximations:
        if "distinct" not in record.fact:
            continue
        assert record.lowest and record.highest, record.fact


def test_the_compound_windows_are_measured_where_the_two_halves_differ(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """The same six records on a column whose HALVES pull apart.

    REVIEW ROUND 6 OF LANDING L8, item 3. The walk above uses a column
    whose label half holds ONE identity, so its raw and folded shifts
    are the same number and a mutant using either for both stays
    green. This column's label half publishes four raw spellings and
    two folded identities, and the floor holds back the variants that
    would supply the raw four -- so the twin writes three, and the
    outer raw count is one short while the folded one is exact.
    """
    folder = tmp_path_factory.mktemp("f4-compound-windows")
    # THE NUMBERS ARE SPREAD rather than one to forty (amendment
    # A-P4-55): forty different values between ends that hold exactly
    # forty grid points is a SATURATED column, where the placement has
    # no freedom and the twin holds thirty-eight at some seeds. This
    # case is about the WINDOW arithmetic of the two halves, so its
    # numeric half is given room and the label half is untouched.
    values = (
        [f"{index * 2}e0" for index in range(1, 41)]
        + ["alpha"] * 6
        + ["Alpha"] * 6
        + ["beta"] * 5
        + ["Beta"] * 5
    )
    path = fixtures.write(
        folder,
        "windows.csv",
        fixtures.rows_to_csv(["c"], [[value] for value in values]),
    )
    table = reading.read_table(str(path))
    document = profile.build_document(
        table, taxonomy.Settings(small_cell_floor=11), []
    )
    block = document["columns"][0]
    assert block["role"] == "numbers_with_labels"
    assert block["labels"]["n_distinct"] == 4
    assert block["labels"]["n_distinct_folded"] == 2
    written = fixtures.write_profile(folder, "windows-profile.json", document)
    twin = generation.generate(contract.load_profile(str(written)), 7)
    records = {
        record.fact: record
        for record in twin.outcomes[0].approximations
        if "distinct" in record.fact
    }
    # The label half cannot supply its fourth spelling, and every
    # record says so at the same numbers.
    assert records["labels -> n_distinct"].achieved == "3"
    assert records["labels -> n_distinct"].lowest == "3"
    assert records["n_distinct"].achieved == "43"
    assert records["n_distinct"].published == "44"
    assert records["n_distinct"].inside
    # ...while the FOLDED side is exact on both halves, which is what a
    # raw-for-folded mutant would break. The label half's folded count
    # carries no record of its own -- it is exact, and a record for it
    # would sit in the approximated section saying otherwise (review
    # round 7, item 2) -- so the outer folded record is where it shows.
    assert "labels -> n_distinct_folded" not in records
    assert records["n_distinct_folded"].achieved == "42"
    assert records["n_distinct_folded"].lowest == "42"
    assert records["n_distinct_folded"].highest == "42"
    # AND THE OUTER RAW ENDS ARE THE NUMBERS THEMSELVES (round 7, item
    # 5): the numeric half is exact at 40 and the label half runs 3 to
    # 4, so the column owes between 43 and 44 and holds 43.
    assert records["n_distinct"].lowest == "43"
    assert records["n_distinct"].highest == "44"
    # AND THE VALIDATOR SAYS THE SAME THING ABOUT THE SAME FILE (review
    # round 7 of landing L8, item 4). This walk measured generation
    # alone, so taking the compound branch out of `_distinctness_checks`
    # brought back the false MISS on a conforming twin and left every
    # assertion above green.
    target = folder / "windows-twin.csv"
    target.write_text(
        rendering.twin_csv(twin), encoding="utf-8", newline="\n"
    )
    outcome = validation.measure(
        contract.load_profile(str(written)), str(target)
    )
    outer = [
        check
        for check in outcome.checks
        if check.fact == "compound.n_distinct"
    ]
    assert len(outer) == 1, outer
    assert outer[0].verdict == validation.AUTHORIZED_DEVIATION, outer[0]
    assert outer[0].achieved == "43", outer[0]
    assert "43" in outer[0].published and "44" in outer[0].published
    # ...and the citation names the half that widened the window, which
    # is the LABEL half here: the numeric half is exact at forty.
    assert outer[0].citation == validation.CORNER_CITATIONS[
        validation.CORNER_LABEL_VARIANTS_SHORT
    ], outer[0].citation
    assert not [
        check
        for check in outcome.checks
        if check.verdict == validation.MISSED
    ], [check.fact for check in outcome.checks if check.verdict == validation.MISSED]


def test_a_role_with_no_approximated_fact_measures_none(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    """The other half of completeness: no extra disposition is invented.

    `empty` and `identifier` publish no approximated field at all --
    owner decision 6 keeps the identifier's length, so its facts are
    exact or report-only, and an all-absent column has nothing to
    approximate. A measurement appearing on either would mean a field
    with two dispositions.
    """
    for place in range(len(every_role.columns)):
        column = every_role.columns[place]
        if column.role in APPROXIMATED:
            continue
        assert twin.outcomes[place].approximations == (), column.name


def test_the_twin_carries_every_column_measurement_in_column_order(
    twin: generation.Twin,
) -> None:
    """The whole-twin record is the columns' records, in the same order."""
    gathered: list[generation.Approximation] = []
    for outcome in twin.outcomes:
        gathered = gathered + list(outcome.approximations)
    assert list(twin.approximations) == gathered
    assert len(twin.approximations) > 0


# -- 2. every bound has two finite ends, and both are checked ---------


def _number(text: str) -> "float | None":
    """One end of a bound as a number, or None where it is a date."""
    try:
        return float(text)
    except ValueError:
        return None


def test_every_bound_has_two_ends_that_are_finite_and_in_order(
    twin: generation.Twin,
) -> None:
    """Point 2 of the item, on every approximated fact of every role.

    A bound with an infinite end is a bound in name only: nothing can
    leave it on that side. Method G12.1 rule 2 says so, and G12.3 names
    the finite value that replaces the skewness quotient where its own
    denominator reaches zero. This is that rule, asserted on every
    record the run produced.
    """
    for record in twin.approximations:
        low = _number(record.lowest)
        high = _number(record.highest)
        if low is None or high is None:
            # A date bound: the two ends are instants, compared as the
            # text the same calendar writes, which sorts as it orders.
            assert record.lowest <= record.highest, record.fact
            continue
        assert math.isfinite(low), record.fact
        assert math.isfinite(high), record.fact
        assert low <= high, record.fact


def test_the_answer_carried_is_the_answer_the_two_ends_give(
    twin: generation.Twin,
) -> None:
    """`inside` is recomputed from the printed ends, not taken on trust.

    The report prints four values and one answer. If the answer were
    ever computed from something other than the printed ends, the report
    would be internally false while every other test stayed green.
    """
    for record in twin.approximations:
        low = _number(record.lowest)
        high = _number(record.highest)
        value = _number(record.achieved)
        if low is None or high is None or value is None:
            assert record.inside == (
                record.lowest <= record.achieved <= record.highest
            ), record.fact
            continue
        assert record.inside == (low <= value <= high), record.fact


def test_the_skewness_bound_is_finite_on_a_coarse_ladder(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    """G12.3's finite fallback, on the column that reaches it.

    `visits` publishes ten different values over 229 rows, so its strata
    are wide, the displacement the construction allows is large, and the
    quotient the skewness bound is drawn from has a zero at its lower
    end. The bound must still have two finite ends -- the range every
    sample of that size lies in -- rather than an infinity nothing can
    leave.
    """
    place = _place_of(every_role, "visits")
    record = _found(list(twin.outcomes[place].approximations), "skew")
    low = _number(record.lowest)
    high = _number(record.highest)
    assert low is not None and high is not None
    assert low < 0 < high
    assert low > -1000 and high < 1000
    assert record.inside


def test_every_approximated_fact_of_a_genuine_run_lands_inside(
    twin: generation.Twin,
) -> None:
    """The base case each mutant below is measured against.

    Every bound is derived from the construction, so a twin this method
    built must satisfy all of them. A failure here is a defect in the
    generator or in the derivation, never a tolerance to widen.
    """
    outside = [
        record.fact for record in twin.approximations if not record.inside
    ]
    assert outside == []


# -- 3. every one of them reaches the report --------------------------


def test_the_report_prints_every_approximated_fact_in_full(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    """Point 3: published, achieved, both ends and the answer, for each.

    The report is the only place a person is told which facts the twin
    holds exactly and which it holds approximately, so every one of the
    four numbers has to be visible there. Checking the rendered text
    rather than the record is deliberate: a record nobody prints tells
    the reader nothing.
    """
    text = rendering.report(every_role, twin)
    assert "HOW CLOSE THE APPROXIMATE FACTS CAME" in text
    for record in twin.approximations:
        assert f"({record.fact})" in text, record.fact
        assert (
            f"the description says {record.published}; "
            f"the twin holds {record.achieved}"
        ) in text, record.fact
        assert (
            f"allowed anywhere from {record.lowest} to {record.highest}"
        ) in text, record.fact
    assert f"{len(twin.approximations)} approximated fact(s)" in text
    assert "Every one of them landed inside the range" in text


def test_the_report_names_the_column_each_measurement_belongs_to(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    """A measurement with no column beside it names nothing a reader has."""
    text = rendering.report(every_role, twin)
    for record in twin.approximations:
        assert f"'{record.column}'" in text, record.column


def test_the_report_says_plainly_when_a_bound_was_missed(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    """The renderer's other branch, which no genuine run reaches here.

    A section that only ever prints good news is one nobody reads
    twice. What this checks is the REPORT'S OWN WORDS, so the one
    measurement it is given is written out below rather than generated:
    handed a value outside its bound, the report has to say so plainly,
    and has to send the reader to the deviation list where the same fact
    is named.
    """
    missed = generation.Approximation(
        column="reading",
        fact="mean",
        published="10.0",
        achieved="40.0",
        lowest="9.0",
        highest="11.0",
        inside=False,
        note="this column's average",
        covers_published=True,
    )
    edited = dataclasses.replace(twin, approximations=(missed,))
    text = rendering.report(every_role, edited)
    assert "1 of them landed OUTSIDE the range" in text
    assert "the description says 10.0; the twin holds 40.0" in text
    assert "allowed anywhere from 9.0 to 11.0: OUTSIDE the range" in text
    assert "is also named in the section above" in text
    # A bound that DOES cover the published value says nothing extra:
    # the sentence about a range missing the description's value is
    # printed where it is true and nowhere else.
    assert "does not cover the description's own value" not in text


def test_the_report_still_has_the_section_with_nothing_to_put_in_it(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    """A twin of nothing but record numbers has no approximated fact.

    The section still appears and still says what it means, because a
    heading that comes and goes is a heading a reader cannot rely on.
    """
    edited = dataclasses.replace(twin, approximations=())
    text = rendering.report(every_role, edited)
    assert "HOW CLOSE THE APPROXIMATE FACTS CAME" in text
    assert "no approximated fact at all" in text


# -- 4. each bound proved able to fail --------------------------------


def _numeric_cells(loaded: contract.Profile, name: str) -> "list[float]":
    """The published ladder ends of one numeric column, as two numbers."""
    facts = loaded.columns[_place_of(loaded, name)].facts
    assert isinstance(facts, contract.NumericFacts)
    low = facts.percentiles.minimum
    high = facts.percentiles.maximum
    assert low is not None and high is not None
    return [low, high]


def _straight_line(low: float, high: float, held: int) -> "list[str]":
    """The column a generator that read only the two ends would write.

    Every published count is met, both published ends are exact, and no
    value falls outside them -- so every EXACT-OBSERVABLE check in the
    suite passes on this column. The nine interior rungs are the only
    thing it gets wrong, which is exactly what the window exists to
    catch (method G5.6, conformance item 5).
    """
    return [
        f"{int(low + (high - low) * step / (held - 1))}"
        for step in range(held)
    ]


def test_the_rung_bound_refuses_a_twin_built_from_the_two_ends_alone(
    bent: contract.Profile,
) -> None:
    """The collapse mutant, through the shipped measurement itself."""
    low, high = _numeric_cells(bent, "reading")
    measured = _measure(bent, "reading", _straight_line(low, high, 200))
    outside = [
        record.fact
        for record in measured
        if record.fact.startswith("percentiles.") and not record.inside
    ]
    assert len(outside) >= 5, [
        (record.fact, record.achieved, record.lowest, record.highest)
        for record in measured
    ]


def test_the_rung_bound_accepts_the_twin_this_method_builds(
    bent: contract.Profile,
) -> None:
    """The base beside that mutant: same column, same assertion, real cells."""
    built = generation.generate(bent, 7)
    measured = _measure(bent, "reading", _cells(built, "reading"))
    for record in measured:
        assert record.inside, (
            record.fact, record.achieved, record.lowest, record.highest
        )


def test_the_mean_bound_refuses_a_column_shifted_off_its_ladder(
    bent: contract.Profile,
) -> None:
    """A generator whose values are all a tenth of the range too high."""
    built = generation.generate(bent, 7)
    low, high = _numeric_cells(bent, "reading")
    step = (high - low) / 10
    moved = [
        f"{int(float(cell) + step)}" for cell in _cells(built, "reading")
    ]
    assert not _found(_measure(bent, "reading", moved), "mean").inside


def test_the_spread_bound_refuses_a_column_squeezed_toward_its_middle(
    bent: contract.Profile,
) -> None:
    """A generator that keeps the average and halves the spread.

    Its mean is untouched, so the mean bound passes; only the standard
    deviation moves. Two bounds that could not tell those apart would be
    one bound printed twice.
    """
    built = generation.generate(bent, 7)
    values = [float(cell) for cell in _cells(built, "reading")]
    middle = sum(values) / len(values)
    squeezed = [f"{int(middle + (value - middle) / 2)}" for value in values]
    measured = _measure(bent, "reading", squeezed)
    assert not _found(measured, "std").inside
    assert _found(measured, "mean").inside


def test_the_shape_bound_refuses_a_column_whose_tail_is_the_wrong_way(
    bent: contract.Profile,
) -> None:
    """A generator that turned the column back to front.

    The two published ends are still exact and the spread is unchanged;
    what moves is which side of the average the long tail is on. The
    squares fixture has a long tail on one side, so the turned column
    has one exactly as long on the other, and the twin's own average
    moves only a little. That is why the shape needs a bound of its own
    rather than one worked out from the other two.
    """
    built = generation.generate(bent, 7)
    low, high = _numeric_cells(bent, "reading")
    mirrored = [
        f"{int(low + high - float(cell))}" for cell in _cells(built, "reading")
    ]
    measured = _measure(bent, "reading", mirrored)
    assert not _found(measured, "skew").inside
    assert _found(measured, "std").inside


def test_the_date_rung_bound_refuses_a_twin_that_wrote_one_date(
    every_role: contract.Profile
) -> None:
    """A generator that met both published ends and nothing between them."""
    facts = every_role.columns[_place_of(every_role, "recorded_on")].facts
    assert isinstance(facts, contract.DatetimeFacts)
    collapsed = [facts.earliest for _step in range(239)] + [facts.latest]
    measured = _measure(every_role, "recorded_on", collapsed)
    outside = [
        record.fact
        for record in measured
        if record.fact.startswith("date_percentiles.") and not record.inside
    ]
    assert len(outside) >= 5, [
        (record.fact, record.achieved, record.lowest, record.highest)
        for record in measured
    ]


def test_the_date_cardinality_bound_refuses_a_collapsed_column(
    every_role: contract.Profile,
) -> None:
    """The lower end of G12.5: the published ladder forces values apart."""
    facts = every_role.columns[_place_of(every_role, "recorded_on")].facts
    assert isinstance(facts, contract.DatetimeFacts)
    collapsed = [facts.earliest for _step in range(239)] + [facts.latest]
    measured = _measure(every_role, "recorded_on", collapsed)
    assert not _found(measured, "n_distinct").inside
    assert not _found(measured, "n_distinct_folded").inside


def test_the_date_cardinality_bound_refuses_more_dates_than_the_range_holds(
    narrow_dates: contract.Profile,
) -> None:
    """The upper end of G12.5, on a column whose range is the ceiling.

    Twelve days are published, so twelve different values is all the
    published range can spell at the published precision. A generator
    that wrote a different date per row -- by reaching outside the range
    or by writing at a finer precision than the description records --
    is refused here rather than left to a reader to notice.
    """
    built = generation.generate(narrow_dates, 5)
    inside = _measure(narrow_dates, "day", _cells(built, "day"))
    assert _found(inside, "n_distinct").inside
    spread = [f"2024-{(step % 12) + 1:02d}-{(step % 20) + 1:02d}"
              for step in range(240)]
    measured = _measure(narrow_dates, "day", spread)
    assert not _found(measured, "n_distinct").inside


def test_the_length_bound_refuses_a_twin_that_mislaid_two_characters(
    every_role: contract.Profile,
) -> None:
    """The average length is met to within one group, and no further.

    The comment column's groups are single rows, so the walk of G9.5
    step 4 can overshoot the published total by at most one character.
    Two is outside, and the bound has to say so -- an average that may
    be off by any amount at all is not an average anybody can use.
    """
    built = generation.generate(every_role, 20260811)
    cells = _cells(built, "comment")
    edited: list[str] = []
    shortened = 0
    for cell in cells:
        if cell != "" and shortened < 2 and len(cell) > 40:
            edited = edited + [cell[0:len(cell) - 1]]
            shortened = shortened + 1
            continue
        edited = edited + [cell]
    assert shortened == 2
    assert not _found(
        _measure(every_role, "comment", edited), "length.mean"
    ).inside


def test_the_middle_length_bound_refuses_a_twin_of_short_values(
    every_role: contract.Profile,
) -> None:
    """A generator that met both length ends and put everything at one."""
    facts = every_role.columns[_place_of(every_role, "comment")].facts
    assert isinstance(facts, contract.TextFacts)
    built = generation.generate(every_role, 20260811)
    cells = _cells(built, "comment")
    edited: list[str] = []
    longest = 0
    for cell in cells:
        if cell == "":
            edited = edited + [""]
            continue
        if longest == 0:
            longest = 1
            edited = edited + ["a" * facts.length.maximum]
            continue
        edited = edited + ["a" * facts.length.minimum]
    assert not _found(
        _measure(every_role, "comment", edited), "length.p50"
    ).inside


def test_the_word_bound_refuses_a_twin_that_dropped_the_spaces(
    every_role: contract.Profile,
) -> None:
    """One long word where the description publishes eight.

    Every length is untouched, so the two length facts still hold; only
    the word count moves. This is the mutant the character-length bounds
    cannot see.
    """
    built = generation.generate(every_role, 20260811)
    edited = [
        "".join("x" if character == " " else character for character in cell)
        for cell in _cells(built, "comment")
    ]
    measured = _measure(every_role, "comment", edited)
    assert not _found(measured, "words.mean").inside
    assert _found(measured, "length.mean").inside


def test_the_label_cardinality_bound_refuses_an_invented_spelling(
    every_role: contract.Profile,
) -> None:
    """A generator that wrote one spelling the description never gave it."""
    built = generation.generate(every_role, 20260811)
    cells = _cells(built, "region")
    assert _found(_measure(every_role, "region", cells), "n_distinct").inside
    edited = ["one-more-spelling"] + cells[1:]
    assert not _found(
        _measure(every_role, "region", edited), "n_distinct"
    ).inside


def test_a_fact_outside_its_bound_becomes_a_named_deviation(
    bent: contract.Profile,
) -> None:
    """Rule 4 of G12.1: a promise this method could not keep is a miss.

    The deviation carries the contract's own field name, both values and
    the range, so the two lists a reader is given cannot disagree about
    what happened.
    """
    low, high = _numeric_cells(bent, "reading")
    measured = _measure(bent, "reading", _straight_line(low, high, 200))
    notes = generation._bound_notes(measured)
    outside = [record for record in measured if not record.inside]
    assert len(notes) == len(outside)
    assert [note.fact for note in notes] == [
        record.fact for record in outside
    ]
    for place in range(len(notes)):
        assert notes[place].published == outside[place].published
        assert notes[place].achieved == outside[place].achieved
        assert outside[place].lowest in notes[place].note
        assert outside[place].highest in notes[place].note


def test_a_genuine_run_names_no_bound_deviation(
    twin: generation.Twin,
) -> None:
    """The base beside that: no bound of a real run is filed as a miss."""
    facts = [record.fact for record in twin.approximations]
    for note in twin.deviations:
        if note.fact in facts:
            assert "landed outside the range" not in note.note, note.fact


# -- 5. the disposition matrix has no cell without a disposition ------


def _emitted_names(block: "dict[str, typing.Any]") -> "list[str]":
    """Every key one column block publishes, containers expanded one level.

    The matrix disposes a ladder's rungs by naming the ladder, and a
    level entry's parts by naming them, so the names this returns are
    the ones the matrix can be asked about: the block's own keys, plus
    the keys inside the four statistics containers and inside a level
    entry.
    """
    names: list[str] = []
    for key in sorted(block):
        names = names + [key]
        value = block[key]
        if key in ("percentiles", "date_percentiles", "length", "words"):
            for inner in sorted(value):
                names = names + [f"{key}.{inner}"]
        if key == "levels":
            for entry in value:
                for inner in sorted(entry):
                    names = names + [inner]
    return names


def _undisposed(
    names: "list[str]", table: "dict[str, str]", universal: "dict[str, str]"
) -> "list[str]":
    """The names in ``names`` that no matrix row disposes.

    A dotted name is disposed by its own row or by its container's row,
    once -- which is how the matrix writes a ladder's interior rungs.
    Everything else has to be named outright.
    """
    missing: list[str] = []
    for name in names:
        if name in table or name in universal:
            continue
        head = name.split(".")[0]
        if head in table or head in universal:
            continue
        missing = missing + [name]
    return missing


@pytest.fixture(scope="module")
def wide_numbers(
    tmp_path_factory: pytest.TempPathFactory,
) -> "dict[str, typing.Any]":
    """A description holding the one role the shared table cannot reach."""
    folder = tmp_path_factory.mktemp("f4-wide")
    values = ["1e999"] * 120 + ["-2e999"] * 120
    path = fixtures.write(
        folder, "wide.csv", fixtures.single_column_table("huge", values)
    )
    table = reading.read_table(str(path))
    return profile.build_document(table, taxonomy.Settings(), [])


@pytest.fixture(scope="module")
def joined_numbers_document(
    tmp_path_factory: pytest.TempPathFactory,
) -> "dict[str, typing.Any]":
    """A description holding the role NO completeness walk reached.

    Residual R-P4-62: this walk enumerated thirteen roles and closed
    with `reached == set(ROLE_SECTIONS)`, so it was satisfied by a
    fixture that never built `joined_numbers` -- the role that carries
    a blood pressure. The map and the fixtures agreed with each other
    and neither was compared against the contract.

    The role needs a DECLARATION: an undeclared `120/80` column is not
    this role, by design (plan P4-D23), so it cannot simply be a
    fourteenth column of the shared table -- any site profiling that
    table without the declaration would give the column another role
    and the guard would be blind again in a new way.
    """
    folder = tmp_path_factory.mktemp("f4-joined")
    path = fixtures.write(
        folder, "joined.csv", fixtures.joined_numbers_table()
    )
    table = reading.read_table(str(path))
    return profile.build_document(
        table, taxonomy.Settings(), [], [], ["reading"]
    )


@pytest.fixture(scope="module")
def numbers_with_labels_document(
    tmp_path_factory: pytest.TempPathFactory,
) -> "dict[str, typing.Any]":
    """A description holding the FIFTEENTH role, for the same reason.

    Residual R-P4-62 taught this walk that a map and a set of fixtures
    can agree with each other while the contract is never consulted, so
    a role added to `ROLE_SECTIONS` without a description that reaches
    it closes the walk on a table it never opened. This role cannot be
    a column of the shared table either: it needs BOTH populations in
    one column, and every column there holds one.
    """
    folder = tmp_path_factory.mktemp("f4-compound")
    path = fixtures.write(
        folder, "compound.csv", fixtures.numbers_with_labels_table()
    )
    table = reading.read_table(str(path))
    return profile.build_document(table, taxonomy.Settings(), [])


@pytest.fixture(scope="module")
def every_role_document(
    tmp_path_factory: pytest.TempPathFactory,
) -> "dict[str, typing.Any]":
    """The producer's own description of the shared table, as a mapping."""
    folder = tmp_path_factory.mktemp("f4-document")
    path = fixtures.write(folder, "table.csv", fixtures.every_role_table())
    table = reading.read_table(str(path))
    return profile.build_document(table, taxonomy.Settings(), ["record_code"])


def test_every_key_the_producer_emits_has_a_disposition(
    every_role_document: "dict[str, typing.Any]",
    wide_numbers: "dict[str, typing.Any]",
    joined_numbers_document: "dict[str, typing.Any]",
    numbers_with_labels_document: "dict[str, typing.Any]",
) -> None:
    """The completeness assertion the plan promised (P2-D12, contract 9).

    Every key the producer emits, for every role plus the top level, is
    looked up in the contract's matrix as the matrix is WRITTEN. A field
    that is published and disposed nowhere is a field whose obligation
    nobody has decided -- which is how an approximated fact came to have
    no bound in the first place.
    """
    sections = _matrix_sections()
    universal = dict(sections["9.2 Universal per-column fields"])
    top = dict(sections["9.1 Top level"])
    names: list[str] = []
    for key in sorted(every_role_document):
        names = names + [key]
        if key == "source":
            for inner in sorted(every_role_document[key]):
                names = names + [f"source.{inner}"]
    assert _undisposed(names, top, {}) == []
    reached: set[str] = set()
    for document in (
        every_role_document,
        wide_numbers,
        joined_numbers_document,
        numbers_with_labels_document,
    ):
        for block in document["columns"]:
            role = block["role"]
            reached.add(role)
            table = dict(sections[ROLE_SECTIONS[role]])
            # Version 6 states the affixed role's own seven keys in
            # its own sub-table, so they are read rather than injected.
            # The role's section here stays the NUMERIC one, because
            # its quantitative block IS the numeric block read over the
            # cores; the sub-table's own rows are merged in below.
            table = dict(table)
            if role == "affixed_number":
                table.update(sections["9.4 affixed_number"])
                # ...and the three keys plan P4-D36 added, which the
                # contract states in the same sub-table's prose rather
                # than as rows of it: the wrapper SET a column may
                # wear, and the two counts of different CORES the
                # generator spends as its budget of core spellings.
                for own in AFFIX_SET_KEYS:
                    table[own] = (
                        "EXACT-OBSERVABLE (Phase 4 plan, P4-D36)"
                    )
            for own in PHASE_4_HISTOGRAM_KEYS:
                table[own] = "EXACT-OBSERVABLE (Phase 4 plan, P4-D4.7)"
            for own in PHASE_4_MOMENT_KEYS:
                table[own] = "APPROXIMATED (Phase 4 plan, P4-D4.8)"
            for own in PHASE_4_VALUE_COUNT_KEYS:
                # EXACT-OBSERVABLE since amendment A-P4-55 (2026-09-04):
                # the owner ruled the count of different numbers an
                # obligation rather than a report line, because
                # analysis code groups by and counts distinct on
                # numeric columns.
                table[own] = "EXACT-OBSERVABLE (Phase 4 plan, A-P4-55)"
            for own in PHASE_4_MODE_KEYS:
                table[own] = "REPORT-ONLY (Phase 4 plan, P4-D4.11)"
            for own in PHASE_4_FINER_LADDER_KEYS:
                table[own] = "REPORT-ONLY (Phase 4 plan, P4-D4.10)"
            missing = _undisposed(_emitted_names(block), table, universal)
            assert missing == [], f"{role}: {missing}"
    assert reached == set(ROLE_SECTIONS)


def test_the_completeness_assertion_refuses_a_key_nobody_disposed(
    every_role_document: "dict[str, typing.Any]",
) -> None:
    """And it can fail: one invented key, and the same check refuses it.

    A completeness assertion that no document can fail would be the
    green light the round-1 review found most misleading of all.
    """
    sections = _matrix_sections()
    universal = dict(sections["9.2 Universal per-column fields"])
    for block in every_role_document["columns"]:
        if block["role"] != "count":
            continue
        table = dict(sections[ROLE_SECTIONS["count"]])
        for own in PHASE_4_HISTOGRAM_KEYS:
            table[own] = "EXACT-OBSERVABLE (Phase 4 plan, P4-D4.7)"
        for own in PHASE_4_MOMENT_KEYS:
            table[own] = "APPROXIMATED (Phase 4 plan, P4-D4.8)"
        for own in PHASE_4_VALUE_COUNT_KEYS:
            table[own] = "REPORT-ONLY (Phase 4 plan, P4-D4.9)"
        for own in PHASE_4_MODE_KEYS:
            table[own] = "REPORT-ONLY (Phase 4 plan, P4-D4.11)"
        for own in PHASE_4_FINER_LADDER_KEYS:
            table[own] = "REPORT-ONLY (Phase 4 plan, P4-D4.10)"
        names = _emitted_names(block) + ["a_field_nobody_disposed"]
        assert _undisposed(names, table, universal) == [
            "a_field_nobody_disposed"
        ]
        return
    raise AssertionError("the shared table has no column of counts")
