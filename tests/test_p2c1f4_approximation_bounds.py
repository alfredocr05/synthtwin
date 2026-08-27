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
)

SPEC = pathlib.Path(__file__).resolve().parent.parent / "docs" / "spec"


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
RUNG_HOLDERS = ("percentiles", "date_percentiles")


def _matrix_rows() -> "dict[str, list[tuple[tuple[str, ...], str]]]":
    """Section 9 of the profile contract, as ORDERED rows per table.

    Each entry is the backticked names in a row's first cell against
    that row's disposition text, in the order the contract writes them.
    Order matters here: the inventory below is derived from it, and the
    run emits its measurements in the same order.
    """
    text = (SPEC / "profile-contract-v4.md").read_text(encoding="utf-8")
    start = text.index("## 9. The disposition matrix")
    body = text[start:text.index("\n## ", start + 10)]
    sections: dict[str, list[tuple[tuple[str, ...], str]]] = {}
    heading = ""
    for line in body.split("\n"):
        if line.startswith("### "):
            heading = line[4:].strip()
            sections[heading] = []
            continue
        if line.startswith("**`") and heading.startswith("9.7"):
            heading = f"9.7 {line.strip().strip('*').strip('`')}"
            sections[heading] = []
            continue
        if not line.startswith("|") or not heading:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2 or set(cells[0]) <= set("-: "):
            continue
        sections[heading].append(
            (tuple(re.findall(r"`([^`]+)`", cells[0])), cells[1])
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
        "count": "9.4 The numeric roles: `count`, `continuous`",
        "continuous": "9.4 The numeric roles: `count`, `continuous`",
        "datetime": "9.6 `datetime`",
        "free_text": "9.7 free_text",
        "constant": "9.5 The label roles: `constant`, `binary`, `categorical`",
        "binary": "9.5 The label roles: `constant`, `binary`, `categorical`",
        "categorical": (
            "9.5 The label roles: `constant`, `binary`, `categorical`"
        ),
        "affixed_number": "9.4 The numeric roles: `count`, `continuous`",
        # A long tail publishes the label roles' own four keys and
        # nothing else, so it owes what they owe, read from their
        # section (plan P4-D5).
        "long_tail_labels": (
            "9.5 The label roles: `constant`, `binary`, `categorical`"
        ),
    }.items()
}

# THE CLOCK ROLE'S INVENTORY IS STATED, because no matrix row carries
# it. The role borrows the datetime SECTION for the completeness walk
# -- its ladder is the date ladder's shape in another ordinal space --
# but the two documents name different keys: version 4 disposes
# `date_percentiles` and the offset fields, which this role publishes
# none of, and this role publishes `clock_percentiles`, which version 4
# never heard of. So the three approximated facts are written out here
# against the plan clauses that decide them, and the reverse walk over
# the matrix skips the role rather than demanding it carry rows about
# somebody else's keys.
APPROXIMATED["time_of_day"] = tuple(
    [f"clock_percentiles.{name}" for name in RUNGS]
    + ["n_distinct", "n_distinct_folded"]
)

# Roles whose approximated inventory is stated above rather than read
# out of the version 4 matrix, and why: the matrix predates them.
ROLES_STATED_RATHER_THAN_READ = ("time_of_day",)


def _matrix_sections() -> "dict[str, dict[str, str]]":
    """The disposition matrix, read from both versions, as fields.

    Returns one mapping per matrix table, keyed by the heading version 4
    gives it, whose entries are every name in the first cell of a row
    against the disposition text in the second. Reading the contract
    rather than restating it is the point: a matrix that gains a field,
    loses one, or changes a disposition moves these tests.

    VERSION 5 IS READ WITH IT, because version 5 carries version 4 by
    reference and states only its delta (its C5-30 requires the
    completeness assertion to pass against the two read together).
    `dispositions.CONTRACT5_SECTIONS` says which version 4 table each
    delta row belongs to.
    """
    text = (SPEC / "profile-contract-v4.md").read_text(encoding="utf-8")
    start = text.index("## 9. The disposition matrix")
    body = text[start:text.index("\n## ", start + 10)]
    sections: dict[str, dict[str, str]] = {}
    heading = ""
    for line in body.split("\n"):
        if line.startswith("### "):
            heading = line[4:].strip()
            sections[heading] = {}
            continue
        if line.startswith("**`") and heading.startswith("9.7"):
            heading = f"9.7 {line.strip().strip('*').strip('`')}"
            sections[heading] = {}
            continue
        if not line.startswith("|") or not heading:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2 or set(cells[0]) <= set("-: "):
            continue
        for name in re.findall(r"`([^`]+)`", cells[0]):
            sections[heading][name] = cells[1]
    delta = dispositions.contract5_delta(SPEC / "profile-contract-v5.md")
    for names, said in delta:
        for name in names:
            where = dispositions.CONTRACT5_SECTIONS.get(name)
            if where is not None:
                sections[where][name] = said
    return sections


# Which matrix table governs which role. `empty`, `identifier` and
# `numeric_unrepresentable` are here too, with no approximated field of
# their own, because a role missing from this map would silently escape
# the completeness check below.
# The seven keys the affixed role ADDS. They are counts and spellings,
# every one of them exactly observable off a written twin, and their
# disposition is stated in the Phase 4 plan rather than in the version
# 4 matrix -- which was written before the role existed.
# ...and the one key the NUMERIC roles gained in the same phase. It
# stands here for the same reason and no other: the version 4 matrix
# was written before the census of fraction widths existed, and its
# disposition is stated in the Phase 4 plan (P4-D4.5) and registered
# under `numeric` in `tests/dispositions.py`.
PHASE_4_NUMERIC_KEYS = ("fraction_widths", "pad_widths")

# ...and the census of written forms, which version 4's matrix has no
# row for because version 4 had no such key. It is disposed in the
# Phase 4 plan (P4-D18) and registered in `tests/dispositions.py`.
PHASE_4_SHAPE_KEYS = ("shape_forms",)

# ...and the two WIDTHS the unrepresentable role gained when the twin
# stopped making up a canonical width for it. Version 4's matrix has no
# row for them under that role because the role published no length at
# all when the matrix was written. Both are EXACT-OBSERVABLE in the
# strict sense this repository means by it: the generator recounts the
# narrowest and widest value it actually wrote and files a deviation
# naming whichever end it did not land on, so neither is ever missed
# silently. The Phase 4 plan disposes them (P4-D4.4).
PHASE_4_WIDTH_KEYS = ("min_length", "max_length")

# ...and the form census a column of dates now carries, for the same
# reason at one grain finer: version 4 HAS the datetime section, and
# that section has no row for a key version 4 never published. The
# Phase 4 plan disposes it (P4-D4.3) and the registry carries it.
PHASE_4_DATETIME_KEYS = (
    ("resolution_mix", "REPORT-ONLY (Phase 4 plan, P4-D4.3)"),
)

# ...and the clock role's own five, for the same reason: the version 4
# matrix was written before the role existed, and the Phase 4 plan
# disposes them (P4-D4.2, with A-P4-20 for the ladder).
CLOCK_OWN_KEYS = (
    ("clock_form", "EXACT-OBSERVABLE (Phase 4 plan, P4-D4.2)"),
    ("clock_percentiles", "APPROXIMATED (Phase 4 plan, A-P4-20)"),
    ("earliest", "EXACT-OBSERVABLE (Phase 4 plan, P4-D4.2)"),
    ("latest", "EXACT-OBSERVABLE (Phase 4 plan, P4-D4.2)"),
    ("n_unparsed", "EXACT-OBSERVABLE (Phase 4 plan, P4-D4.2)"),
)

AFFIXED_OWN_KEYS = (
    "affix_prefix",
    "affix_suffix",
    "n_affixed",
    "n_core_numeric",
    "n_core_out_of_range",
    "n_core_contradictory",
    "n_core_not_numeric",
)

ROLE_SECTIONS = {
    "empty": "9.3 `empty`",
    "count": "9.4 The numeric roles: `count`, `continuous`",
    "continuous": "9.4 The numeric roles: `count`, `continuous`",
    "constant": "9.5 The label roles: `constant`, `binary`, `categorical`",
    "binary": "9.5 The label roles: `constant`, `binary`, `categorical`",
    "categorical": "9.5 The label roles: `constant`, `binary`, `categorical`",
    "datetime": "9.6 `datetime`",
    "free_text": "9.7 free_text",
    "identifier": "9.7 identifier",
    "numeric_unrepresentable": "9.7 numeric_unrepresentable",
    # The affixed role reads the NUMERIC section, because its
    # quantitative block IS the numeric block read over the cores (AF7)
    # and every approximation the numeric roles carry it carries at the
    # same width. Its own five keys are counts and spellings, none of
    # them approximated, and they are registered in
    # `tests/dispositions.py` -- the version 4 matrix this reads
    # predates the role and states nothing about it.
    "affixed_number": "9.4 The numeric roles: `count`, `continuous`",
    # The clock role reads the DATETIME section: its ladder is the date
    # ladder's shape in another ordinal space, its two ends are exact
    # the same way, and its two distinctness counts are approximated
    # for the same reason (plan P4-D4.2 with amendment A-P4-20). Its
    # own five keys are counts, words and clock text, and they are
    # registered in `tests/dispositions.py` -- the version 4 matrix
    # this reads predates the role.
    "time_of_day": "9.6 `datetime`",
    # The long tail reads the LABEL section: its four keys ARE the
    # label roles' four keys, under the same invariants, and it
    # publishes no key of its own (plan P4-D5). `level_ceiling` is
    # categorical's alone and this role does not carry it, which is
    # why it is not simply the categorical row.
    "long_tail_labels": (
        "9.5 The label roles: `constant`, `binary`, `categorical`"
    ),
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
        assert measured == list(
            APPROXIMATED.get(column.role, ())
        ), f"{column.name} ({column.role})"


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
    for document in (every_role_document, wide_numbers):
        for block in document["columns"]:
            role = block["role"]
            reached.add(role)
            table = dict(sections[ROLE_SECTIONS[role]])
            # The affixed role's own seven keys are disposed in the
            # Phase 4 plan and registered in `tests/dispositions.py`;
            # the version 4 matrix this reads predates the role and
            # says nothing about them. Its QUANTITATIVE keys are not
            # exempt and are checked against the numeric section like
            # everything else -- which is the point, because those are
            # the ones that carry a distribution.
            table = dict(table)
            for own in AFFIXED_OWN_KEYS:
                table[own] = "EXACT-OBSERVABLE (Phase 4 plan, P4-D4.1)"
            for own in PHASE_4_NUMERIC_KEYS:
                table[own] = "EXACT-OBSERVABLE (Phase 4 plan, P4-D4.5)"
            for own in PHASE_4_SHAPE_KEYS:
                table[own] = "EXACT-OBSERVABLE (Phase 4 plan, P4-D18)"
            for own, said in PHASE_4_DATETIME_KEYS:
                table[own] = said
            if role == "numeric_unrepresentable":
                for own in PHASE_4_WIDTH_KEYS:
                    table[own] = "EXACT-OBSERVABLE (Phase 4 plan, P4-D4.4)"
            if role == "time_of_day":
                # The datetime section it borrows disposes the DATE
                # ladder and the offset fields, none of which this role
                # publishes; what it does publish is these five.
                for own, said in CLOCK_OWN_KEYS:
                    table[own] = said
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
        for own in PHASE_4_NUMERIC_KEYS:
            table[own] = "EXACT-OBSERVABLE (Phase 4 plan, P4-D4.5)"
        names = _emitted_names(block) + ["a_field_nobody_disposed"]
        assert _undisposed(names, table, universal) == [
            "a_field_nobody_disposed"
        ]
        return
    raise AssertionError("the shared table has no column of counts")
