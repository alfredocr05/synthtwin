"""The entry table: the registry's projection, and non-vacuity (V3, V8).

REVIEW ITEM P3-V1-F2, which named the machinery that did not exist. The
validation method fixes an entry's identity as the triple (registry
fact, profile predicate, subcheck) and requires three things of the
shipped validator that nothing was asserting:

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

WHAT THE PERTURBATIONS MAY BE, AND WHY THE DEGENERATE FILES ARE NOT
AMONG THEM. Every mutation here leaves a file that reads as a table and
is measured cell by cell, so a MISSED verdict is the outcome of a
comparison the validator actually made. Truncating a file to its header
makes nearly every subcheck miss -- because the validator is written to
miss them, not because any of them measured anything -- so it proves
nothing about whether a check can fail, and using it to satisfy the
coverage identity would be the same vacuity in a longer form. It is
tested in `test_validation.py`, where it belongs, and it is not a
registered red case.

Every table is built at test time by the seeded neutral builders in
`fixtures.py`; no data-format file enters the repository (plan D13).
"""

import csv
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
    missed by any file: `styles.at-least.exponent_lower` is unfalsifiable
    on a description that publishes none. This description publishes
    them, so the subcheck has a description it can fail on.
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
    text: str,
    name: str,
) -> validation.Outcome:
    """One measured file, measured."""
    target = fixtures.write(folder, name, text)
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


def _column_of(described: contract.Profile, role: str) -> int:
    """The position of the first column of one role, as an index."""
    for column in described.columns:
        if column.role == role:
            return column.position - 1
    raise AssertionError(f"no {role} column in this description")


def _first_record(described: contract.Profile) -> int:
    """The row the cells start at: after a header, or at the top."""
    if described.source.header_source == reading.HEADER_FROM_FILE:
        return 1
    return 0


def _every_cell(
    described: contract.Profile, text: str, role: str, value: str
) -> str:
    """Every cell of one column of one role replaced by ``value``."""
    index = _column_of(described, role)
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
    role: str,
    find_blank: bool,
    value: str,
) -> str:
    """The first cell of one column that is (or is not) blank, changed.

    "" where the column holds no such cell -- a column with no blank in
    it cannot have one filled -- and the caller leaves that perturbation
    out rather than building a file identical to the twin, which would
    be a red case that can never go red.
    """
    index = _column_of(described, role)
    rows = _rows_of(text)
    for row in range(_first_record(described), len(rows)):
        if bool(rows[row][index]) != find_blank:
            rows[row][index] = value
            return _rebuilt(rows)
    return ""


def _blank_one_cell(
    described: contract.Profile, text: str, role: str
) -> str:
    """The first non-blank cell of one column emptied."""
    return _changed(described, text, role, False, "")


def _fill_one_blank(
    described: contract.Profile, text: str, role: str, value: str
) -> str:
    """The first blank cell of one column filled in."""
    return _changed(described, text, role, True, value)


def _mapped(
    described: contract.Profile,
    text: str,
    role: str,
    rule: "typing.Callable[[str], str]",
) -> str:
    """Every non-blank cell of one column put through one rule."""
    index = _column_of(described, role)
    rows = _rows_of(text)
    for row in range(_first_record(described), len(rows)):
        if rows[row][index]:
            rows[row][index] = rule(rows[row][index])
    return _rebuilt(rows)


def _recased_labels(described: contract.Profile, text: str) -> str:
    """Every label of the first categorical column written in capitals."""
    return _mapped(described, text, "categorical", lambda cell: cell.upper())


def _respelled_numbers(described: contract.Profile, text: str) -> str:
    """Every number of the continuous column given a leading zero."""
    return _mapped(
        described, text, "continuous", lambda cell: f"0{cell}"
    )


def _flattened_ladder(
    described: contract.Profile, text: str, role: str
) -> str:
    """One numeric column's values collapsed onto a single value.

    Every cell that held a number holds the same number, which keeps the
    column numeric and present exactly as often, and destroys every
    other thing the description publishes about its shape.
    """
    return _mapped(described, text, role, lambda _cell: "7")


def _shifted_dates(described: contract.Profile, text: str) -> str:
    """Every date moved to one fixed day."""
    return _mapped(
        described, text, "datetime", lambda _cell: "2019-03-04"
    )


def _reworded_text(described: contract.Profile, text: str) -> str:
    """Every free-text cell replaced by one short word."""
    return _mapped(described, text, "free_text", lambda _cell: "zz")


def _repeated_identifiers(described: contract.Profile, text: str) -> str:
    """Every record number replaced by the same one."""
    return _mapped(described, text, "identifier", lambda _cell: "AA000")


# Each entry is one perturbation CLASS: a name, the class of edit it is,
# and the file it produces from a conforming twin. The class names are
# what V8.5's floor is counted over, so two entries sharing a class
# count once.
def _numbered(described: contract.Profile, text: str, role: str) -> str:
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
    index = _column_of(described, role)
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


def _dated(described: contract.Profile, text: str, rule: str) -> str:
    """One datetime column rewritten under one of three named rules.

    Each keeps the column reading as dates -- so the file's own
    description still publishes the datetime facts and the gate stays
    open -- and moves exactly one family of them: where the values sit,
    how precisely they are written, or which offset they carry.
    """
    index = _column_of(described, "datetime")
    rows = _rows_of(text)
    first = _first_record(described)
    step = 0
    for row in range(first, len(rows)):
        cell = rows[row][index]
        if not cell:
            continue
        day = f"{(step % 27) + 1:02d}"
        month = f"{(step % 11) + 1:02d}"
        if rule == "moved":
            rows[row][index] = f"2019-{month}-{day}"
        if rule == "timed":
            rows[row][index] = f"2024-{month}-{day}T09:{step % 60:02d}:00"
        if rule == "offset":
            rows[row][index] = (
                f"2024-{month}-{day}T09:{step % 60:02d}:00+02:00"
            )
        if rule == "mixed":
            zone = "+02:00" if step % 2 else "-05:30"
            rows[row][index] = (
                f"2024-{month}-{day}T09:{step % 60:02d}:00{zone}"
            )
        step = step + 1
    return _rebuilt(rows)


def _classed(
    described: contract.Profile,
    text: str,
    role: str,
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
    index = _column_of(described, role)
    rows = _rows_of(text)
    first = _first_record(described)
    step = 0
    for row in range(first, len(rows)):
        if rows[row][index]:
            if step % every == 0:
                rows[row][index] = value
            step = step + 1
    return _rebuilt(rows)


def _restyled(described: contract.Profile, text: str, role: str, style: str) -> str:
    """Every number of one column written in another permitted style."""
    index = _column_of(described, role)
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
    return _rebuilt(rows)


def _one_variant(described: contract.Profile, text: str, role: str) -> str:
    """Two cells of one label written with a trailing space.

    The two cells still fold to the same published label, so the level's
    own count is untouched; what changes is the spelling map, and at two
    cells the file's own description holds the new spelling back below
    the floor -- which is the `variants_withheld` map, published empty on
    a twin and not empty here.
    """
    index = _column_of(described, role)
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


def _text_shape(described: contract.Profile, text: str, longer: bool) -> str:
    """Every free-text cell written at one end of its published lengths.

    The cells stay text of several words, so the column keeps its role;
    what moves is the average and the middle of the lengths, and the two
    extremes with them.
    """
    index = _column_of(described, "free_text")
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


def _digit_codes(described: contract.Profile, text: str) -> str:
    """Every record number written as figures alone, all different."""
    index = _column_of(described, "identifier")
    rows = _rows_of(text)
    first = _first_record(described)
    step = 0
    for row in range(first, len(rows)):
        if rows[row][index]:
            rows[row][index] = f"{700000 + step}"
            step = step + 1
    return _rebuilt(rows)


def _compressed(described: contract.Profile, text: str, role: str) -> str:
    """One numeric column's values crowded down toward its own low end.

    The companion of the even spread: that one leaves the upper rungs
    close to where the description puts them, and this one moves them.
    The two ends stay where they were, so the column is still the same
    column by every fact but its shape.
    """
    index = _column_of(described, role)
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


def _raised_end(described: contract.Profile, text: str, role: str) -> str:
    """The largest number of one column made very much larger."""
    index = _column_of(described, role)
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


def _perturbations(
    described: contract.Profile, twin: str
) -> "list[tuple[str, str, str]]":
    """Every registered perturbation of one twin: name, class, text.

    A perturbation whose text is "" is one this description holds no
    cell for -- a column with no blank cell cannot have one filled --
    and is left out rather than registered as a file identical to the
    twin, which would be a red case that can never go red.
    """
    rows = _rows_of(twin)
    first = _first_record(described)
    built = [
        ("blanked-cell", "cell", _cell(twin, first, 0, "")),
        ("moved-cell", "cell", _cell(twin, first, 0, "zz")),
        ("dropped-row", "rows", _rebuilt(rows[: len(rows) - 1])),
        ("added-row", "rows", _rebuilt(rows + [rows[len(rows) - 1]])),
        ("carriage-returns", "line-endings", twin.replace("\n", "\r\n")),
        ("byte-order-mark", "byte-order-mark", "\ufeff" + twin),
        ("no-terminal-newline", "terminal-newline", twin[: len(twin) - 1]),
        ("added-column", "structure", _extra_column(twin)),
    ]
    if described.n_columns > 1:
        built = built + [
            ("swapped-columns", "structure", _swap_columns(twin, 0, 1))
        ]
    if described.source.header_source == reading.HEADER_FROM_FILE:
        built = built + [
            (
                "edited-header",
                "structure",
                _renamed_header(
                    twin, described.columns[0].name, "renamed_column"
                ),
            )
        ]
    else:
        built = built + [("written-header", "structure", _headed(described, twin))]
    for role in (
        "count",
        "continuous",
        "categorical",
        "datetime",
        "free_text",
        "identifier",
        "numeric_unrepresentable",
        "empty",
        "constant",
        "binary",
    ):
        if not _has(described, role):
            continue
        built = built + [
            (f"blanked-{role}", "presence", _blank_one_cell(described, twin, role)),
            (
                f"filled-{role}",
                "presence",
                _fill_one_blank(described, twin, role, "5"),
            ),
            (
                f"rewritten-{role}",
                "content",
                _every_cell(described, twin, role, "zz"),
            ),
        ]
    for role in ("count", "continuous"):
        if not _has(described, role):
            continue
        built = built + [
            (f"spread-{role}", "shape", _numbered(described, twin, role)),
            (f"raised-{role}", "shape", _raised_end(described, twin, role)),
            (
                f"crowded-{role}",
                "shape",
                _compressed(described, twin, role),
            ),
            (
                f"enormous-{role}",
                "class",
                _classed(described, twin, role, "1e200", 2),
            ),
            (f"zeroed-{role}", "class", _classed(described, twin, role, "0")),
            (
                f"negated-{role}",
                "class",
                _classed(described, twin, role, "-8"),
            ),
            (
                f"worded-{role}",
                "class",
                _classed(described, twin, role, "zz"),
            ),
            (
                f"bracketed-{role}",
                "class",
                _classed(described, twin, role, "(4)"),
            ),
            (
                f"overflowed-{role}",
                "class",
                _classed(described, twin, role, "9e999"),
            ),
            (
                f"underflowed-{role}",
                "class",
                _classed(described, twin, role, "-9e999"),
            ),
            (
                f"fractioned-{role}",
                "class",
                _classed(described, twin, role, "1.5"),
            ),
            (
                f"contradicted-{role}",
                "class",
                _classed(described, twin, role, "(-4)"),
            ),
        ]
        for style in (
            parsing.STYLE_LEADING_ZERO,
            parsing.STYLE_LEADING_PLUS,
            parsing.STYLE_EXPONENT_UPPER,
            parsing.STYLE_EXPONENT_LOWER,
            "noncanonical",
        ):
            built = built + [
                (
                    f"{style}-{role}",
                    "spelling",
                    _restyled(described, twin, role, style),
                )
            ]
    for role in ("categorical", "binary", "constant"):
        if not _has(described, role):
            continue
        built = built + [
            (f"recased-{role}", "spelling", _mapped(described, twin, role, lambda cell: cell.upper())),
            (f"spaced-{role}", "spelling", _one_variant(described, twin, role)),
        ]
    if _has(described, "datetime"):
        built = built + [
            ("moved-dates", "shape", _dated(described, twin, "moved")),
            ("mixed-offsets", "precision", _dated(described, twin, "mixed")),
            ("timed-dates", "precision", _dated(described, twin, "timed")),
            ("offset-dates", "precision", _dated(described, twin, "offset")),
        ]
    if _has(described, "free_text"):
        built = built + [
            ("shortened-text", "shape", _text_shape(described, twin, False)),
            ("lengthened-text", "shape", _text_shape(described, twin, True)),
            (
                "one-text",
                "content",
                _every_cell(described, twin, "free_text", "wo rd"),
            ),
        ]
    if _has(described, "identifier"):
        built = built + [
            (
                "repeated-identifiers",
                "content",
                _mapped(described, twin, "identifier", lambda _cell: "AA000"),
            ),
            ("digit-identifiers", "content", _digit_codes(described, twin)),
        ]
    return [entry for entry in built if entry[2]]


def _has(described: contract.Profile, role: str) -> bool:
    """Whether this description carries a column of one role."""
    for column in described.columns:
        if column.role == role:
            return True
    return False


def _missed_by(outcome: validation.Outcome) -> "set[str]":
    """Every subcheck identity this run reported MISSED."""
    return {
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    }


@pytest.fixture(scope="module")
def battery(
    tmp_path_factory: pytest.TempPathFactory,
    runs: "list[tuple[str, contract.Profile, str]]",
) -> "dict[str, dict[str, set[str]]]":
    """Every perturbation of every fixture, measured once.

    Keyed by fixture name, then by perturbation name, holding the set of
    subcheck identities that perturbation made MISS. Built once because
    the battery is dozens of whole validate runs.
    """
    folder = tmp_path_factory.mktemp("red-battery")
    found: dict[str, dict[str, set[str]]] = {}
    for name, described, twin in runs:
        mine: dict[str, set[str]] = {}
        for label, _kind, text in _perturbations(described, twin):
            outcome = _measured(
                folder, described, text, f"{name}-{label}.csv"
            )
            mine[label] = _missed_by(outcome)
        found[name] = mine
    return found


def test_every_registered_red_case_misses_the_subcheck_it_names(
    battery: "dict[str, dict[str, set[str]]]",
) -> None:
    """V8.2: the case names the subcheck, and THAT subcheck must miss.

    Other subchecks failing alongside is fine. A perturbation caught
    only by a neighbour -- the mean tripping while a hard-coded rung
    check sleeps -- is a red battery, because the named subcheck did not
    do its job.
    """
    named = {
        ("every-role", "blanked-cell"): "presence.n_present",
        ("every-role", "moved-cell"): "length.min",
        ("every-role", "dropped-row"): "rows.n_rows",
        ("every-role", "added-row"): "rows.n_rows",
        ("every-role", "carriage-returns"): "bytes.line-endings",
        ("every-role", "byte-order-mark"): "bytes.byte-order-mark",
        ("every-role", "no-terminal-newline"): "bytes.terminal-newline",
        ("every-role", "added-column"): "columns.n_columns",
        ("every-role", "swapped-columns"): "position.at",
        ("every-role", "edited-header"): "header.names",
        ("every-role", "recased-categorical"): "levels.north.variants",
        ("every-role", "spaced-categorical"): (
            "levels.north.variants_withheld"
        ),
        ("every-role", "leading_zero-count"): (
            f"styles.exact.{parsing.STYLE_LEADING_ZERO}"
        ),
        ("every-role", "leading_plus-count"): (
            f"styles.exact.{parsing.STYLE_LEADING_PLUS}"
        ),
        ("every-role", "exponent_upper-continuous"): (
            f"styles.exact.{parsing.STYLE_EXPONENT_UPPER}"
        ),
        ("pooled", "noncanonical-continuous"): (
            f"styles.canonical.{parsing.STYLE_DECIMAL}"
        ),
        ("spelled", "exponent_upper-continuous"): (
            f"styles.at-least.{parsing.STYLE_EXPONENT_LOWER}"
        ),
        ("every-role", "moved-dates"): "date-ladder.min",
        ("every-role", "timed-dates"): "precision.time_precision",
        ("every-role", "mixed-offsets"): "offsets.earliest",
        ("every-role", "shortened-text"): "length.min",
        ("every-role", "lengthened-text"): "words.max",
        ("every-role", "repeated-identifiers"): (
            "distinct.n_distinct_by_occurrences"
        ),
        ("every-role", "digit-identifiers"): "counts.n_all_digits",
        ("every-role", "filled-count"): "presence.n_missing",
        ("every-role", "crowded-count"): "ladder.p50",
        ("every-role", "crowded-continuous"): "ladder.p90",
        ("every-role", "raised-continuous"): "ladder.max",
        ("every-role", "zeroed-count"): "counts.n_zero",
        ("every-role", "negated-count"): "counts.n_negative",
        ("every-role", "fractioned-count"): "type.integer_valued",
        ("every-role", "contradicted-count"): "counts.n_contradictory",
        ("every-role", "overflowed-count"): "counts.n_out_of_range",
        ("every-role", "rewritten-datetime"): "axes.role",
        ("every-role", "rewritten-empty"): "presence.n_present",
        ("unrepresentable", "rewritten-numeric_unrepresentable"): (
            "axes.role"
        ),
        ("unrepresentable", "blanked-numeric_unrepresentable"): (
            "presence.n_present"
        ),
        ("headerless", "written-header"): "header.presence",
        ("headerless", "swapped-columns"): "axes.role",
        ("headerless", "crowded-count"): "ladder.p25",
    }
    for key in sorted(named):
        fixture, label = key
        assert label in battery[fixture], (
            f"{fixture}/{label} was not built, so the case names a "
            f"perturbation this battery does not make"
        )
        assert named[key] in battery[fixture][label], (
            f"the red case {fixture}/{label} names {named[key]}, and that "
            f"subcheck did not report MISSED -- so whatever else went "
            f"red, the named check did not do its job"
        )


def test_the_coverage_identity_walks_the_shipped_table(
    tmp_path: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
    battery: "dict[str, dict[str, set[str]]]",
) -> None:
    """V8.3: every executable subcheck has a registered way to fail.

    THE IDENTITY IS WALKED, not a list written here: the entries come
    out of the shipped validator's own run over each conforming twin, so
    a subcheck added to the validator without a perturbation that can
    make it miss turns this red on the commit that adds it. That is the
    difference between a coverage identity and a coverage claim.

    TWO KINDS OF ENTRY ARE EXCUSED, and the two are not the same thing.
    One is PROVED here, from the description's own published side: a
    published style count is a FLOOR, so where the description publishes
    none of a style, "at least none" is an obligation no file can miss
    and no perturbation could ever make it. The other is the register of
    gaps below, which proves nothing at all -- it is the list of entries
    this battery does not reach yet, carried by name so that the census
    of what is covered cannot quietly grow to include them.
    """
    # AN ENTRY IS AN OBLIGATION, NOT A FIXTURE. Its identity is the
    # registry fact, the predicate and the subcheck, so a red case that
    # makes `ladder.p50` miss on one description has shown that entry
    # can fail; the fixtures are how the walk REACHES entries, not part
    # of what an entry is.
    reachable: set[str] = set()
    for name in battery:
        for label in battery[name]:
            reachable = reachable | battery[name][label]
    uncovered: list[str] = []
    for name, described, twin in runs:
        outcome = _measured(tmp_path, described, twin, f"{name}-green.csv")
        for check in outcome.checks:
            if check.subcheck in reachable:
                continue
            if _is_a_floor_of_none(check):
                continue
            if check.subcheck in NOT_REACHED_BY_THIS_BATTERY:
                continue
            uncovered = uncovered + [f"{name}: {check.subcheck}"]
    assert not uncovered, (
        "these executable subchecks have no registered red case, so "
        "nothing in this suite shows they can fail at all:\n  "
        + "\n  ".join(sorted(set(uncovered)))
    )


def _is_a_floor_of_none(check: validation.Check) -> bool:
    """Whether this entry is a published floor of zero.

    Contract 7.5.7 makes each published style count a floor: the recount
    must be AT LEAST the published number. Where the description
    publishes none of a style, every file on earth writes at least none
    of it, so the entry cannot be made to miss on THIS description --
    not because the check is vacuous, but because this description asks
    nothing of it. The `spelled` fixture publishes such a count, and the
    red case above makes it miss there.
    """
    if not check.subcheck.startswith("styles.at-least."):
        return False
    return check.published == "0"


# THE REGISTER OF GAPS. Every entry here is an executable subcheck this
# battery does not yet make miss. It is NOT a claim that any of them
# cannot be made to miss -- writing that would be the quiet lowering
# this project refuses -- and the review record and the implementation
# report carry it as an open item.
#
# The test below holds it to being exactly the residue: an entry that
# becomes covered has to leave this list, so the register cannot grow
# stale and hide a check that has since gone vacuous.
NOT_REACHED_BY_THIS_BATTERY = {
    # Every perturbation here is written as UTF-8 text. A file that is
    # not UTF-8 needs a bytes-level fixture, which the reading batteries
    # build and this harness does not.
    "bytes.utf8",
    # These three move only when a column's cells change class WITHOUT
    # changing the role the file's own description reads it as. Every
    # class edit in this battery moves enough cells to re-classify the
    # column, and the disclosure gate then WITHHOLDS the numeric block
    # rather than verdicting it -- so the miss never arrives.
    "counts.numeric_share",
    "counts.n_left_out_of_statistics",
    "counts.n_negative_unrepresentable",
    "type.std_unrepresentable",
    # The datetime facts a date-only column publishes as zero, which the
    # date rewrites here do not reach: a cell written to the second
    # changes the resolution first, and the resolution check catches it.
    "counts.subsecond_digits",
    "counts.n_unparsed",
    # The invention role's own class counts. Every cell of the
    # unrepresentable fixture is of one class by construction, and an
    # edit that changes a cell's class changes the role the file's own
    # description reads the column as.
    "counts.n_fraction",
    "counts.n_sign_unknown",
    "counts.n_whole_unknown",
}


def test_the_register_of_gaps_holds_no_entry_that_is_covered(
    tmp_path: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
    battery: "dict[str, dict[str, set[str]]]",
) -> None:
    """The register may not outlive the gap it records.

    A named exception that stays after the gap closes is how a coverage
    identity becomes a coverage claim again: the list grows, nobody
    rereads it, and an entry that has since become vacuous sits inside
    it unnoticed. So every name in the register has to be a subcheck
    that is still uncovered on some fixture.
    """
    covered: set[str] = set()
    live: set[str] = set()
    for name, described, twin in runs:
        outcome = _measured(tmp_path, described, twin, f"{name}-register.csv")
        for check in outcome.checks:
            live.add(check.subcheck)
        for label in battery[name]:
            covered = covered | battery[name][label]
    stale = []
    for subcheck in sorted(NOT_REACHED_BY_THIS_BATTERY):
        if subcheck not in live:
            stale = stale + [f"{subcheck} (no fixture carries it)"]
            continue
        if subcheck in covered:
            stale = stale + [f"{subcheck} (a red case now reaches it)"]
    assert not stale, (
        "these names are in the register of gaps and are not gaps:\n  "
        + "\n  ".join(stale)
    )


def test_the_vacuity_floor_counts_classes_per_disposition(
    tmp_path: pathlib.Path,
    runs: "list[tuple[str, contract.Profile, str]]",
    battery: "dict[str, dict[str, set[str]]]",
) -> None:
    """V8.5: a counted floor of red-case CLASSES per disposition class.

    The floor the review found was four mutations over the whole
    battery, which a battery could meet while every exact fact in the
    product was covered by one shared edit. This one is counted per
    disposition: for each class the registry carries an obligation in,
    at least three DIFFERENT perturbation classes must have made some
    subcheck of that class miss.
    """
    by_key = {
        f"{fact.group}.{fact.field}": fact for fact in dispositions.REGISTRY
    }
    classes: dict[str, set[str]] = {}
    for name, described, twin in runs:
        for label, kind, text in _perturbations(described, twin):
            outcome = _measured(
                tmp_path, described, text, f"floor-{name}-{label}.csv"
            )
            for check in outcome.checks:
                if check.verdict != validation.MISSED:
                    continue
                if check.fact in validation.BYTE_RULE_FACTS:
                    disposition = "BYTE-RULE"
                else:
                    disposition = by_key[check.fact].disposition
                if disposition not in classes:
                    classes[disposition] = set()
                classes[disposition].add(kind)
    for disposition in (
        dispositions.EXACT_OBSERVABLE,
        dispositions.EXACT_CONTROL,
        dispositions.APPROXIMATED,
        "BYTE-RULE",
    ):
        assert disposition in classes, (
            f"no perturbation in this battery makes any {disposition} "
            f"obligation miss, so nothing shows that class can fail"
        )
        assert len(classes[disposition]) >= 3, (
            f"{disposition} obligations are made to miss by only "
            f"{sorted(classes[disposition])} -- fewer than three "
            f"distinct classes of perturbation, so this battery could "
            f"rot into one shared edit and stay green"
        )
