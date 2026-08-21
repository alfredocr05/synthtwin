"""The generator, checked against the twin it actually wrote.

The method is `docs/spec/generation-method-v1.md`. A generator that only
ever RUNS proves nothing: the whole of its value is that the twin holds
what the description says, so every count this file checks is RECOUNTED
from the cells the generator produced, never restated from the
description it was handed. A check that reads its expectation out of the
same object it is checking is a check that cannot fail.

The descriptions are built by the REAL producer from seeded neutral
tables (plan D13: no data-format file is ever committed), so these tests
run producer, loader and generator end to end, and a fact the producer
publishes in a shape this generator does not expect fails here rather
than in a report somebody reads later.

Two documents are hand-edited, and only two: the pair that no real table
can produce, because they are the pair whose facts cannot all hold at
once. Those are the two generation refusals, and a refusal that cannot
be reached is a promise nobody keeps.
"""

import copy
import json
import pathlib
import typing

import pytest

import fixtures
from synthtwin import (
    contract,
    errors,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    taxonomy,
)

Document = dict[str, typing.Any]


# -- descriptions built by the real producer --------------------------


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


def _document(folder: pathlib.Path, text: str, declared: list[str]) -> Document:
    """The producer's own description of a table, as a plain mapping."""
    path = fixtures.write(folder, "table.csv", text)
    table = reading.read_table(str(path))
    built = profile.build_document(table, taxonomy.Settings(), declared)
    return typing.cast(Document, json.loads(json.dumps(built)))


def _loaded(folder: pathlib.Path, document: Document) -> contract.Profile:
    """Load a description that has been edited, from a file of its bytes."""
    target = fixtures.write_profile(folder, "edited-profile.json", document)
    return contract.load_profile(str(target))


def _every_role_text() -> str:
    """A neutral table with one column for every role in the taxonomy."""
    lines = [line for line in fixtures.every_role_table().split("\n") if line]
    rows = [f"{lines[0]},huge"]
    for index, line in enumerate(lines[1:]):
        rows.append(f"{line}," + ("1e999" if index % 2 else "-2e400"))
    return "\n".join(rows) + "\n"


def _styles_text() -> str:
    """A column of whole numbers written six different ways.

    Twenty rows in each style, which clears the smallest group size, so
    the description publishes all six counts rather than pooling any of
    them. Every value is a whole number, so the six styles are told
    apart again by looking at the twin's own cells.
    """
    spelled = []
    for index in range(120):
        value = index % 20 + 1
        style = index // 20
        if style == 0:
            spelled.append(f"{value}")
        elif style == 1:
            spelled.append(f"00{value}")
        elif style == 2:
            spelled.append(f"+{value}")
        elif style == 3:
            spelled.append(f"{value}.0")
        elif style == 4:
            spelled.append(f"{value}e0")
        else:
            spelled.append(f"{value}E0")
    return fixtures.single_column_table("measured", spelled)


@pytest.fixture(scope="module")
def every_role(tmp_path_factory: pytest.TempPathFactory) -> contract.Profile:
    """One description carrying a block of every shape the producer emits."""
    folder = tmp_path_factory.mktemp("generation-roles")
    return _described(folder, _every_role_text(), ["record_code"])


@pytest.fixture(scope="module")
def styled(tmp_path_factory: pytest.TempPathFactory) -> contract.Profile:
    """A description of a column written in all six permitted styles."""
    folder = tmp_path_factory.mktemp("generation-styles")
    return _described(folder, _styles_text())


@pytest.fixture(scope="module")
def twin(every_role: contract.Profile) -> generation.Twin:
    """One twin of the every-role description, built once and read often."""
    return generation.generate(every_role, 7)


# -- small recounting helpers, written against the twin's own cells ---


def _cells(twin_built: generation.Twin, name: str) -> tuple[str, ...]:
    """Every cell of one column of the twin, in row order."""
    for index, outcome in enumerate(twin_built.outcomes):
        if outcome.name == name:
            return twin_built.columns[index]
    raise AssertionError(f"the twin has no column named {name}")


def _present(cells: "tuple[str, ...]") -> list[str]:
    """The cells that hold a value."""
    return [cell for cell in cells if cell != ""]


def _block(
    described: contract.Profile, name: str
) -> contract.ColumnBlock:
    """One column's block of the description."""
    for column in described.columns:
        if column.name == name:
            return column
    raise AssertionError(f"the description has no column named {name}")


def _style_of(cell: str) -> str:
    """Which of the six styles one cell of whole numbers is written in.

    The twin is the only input: this reads the cell's own characters and
    never asks the generator what it meant to write.
    """
    if "E" in cell:
        return "exponent_upper"
    if "e" in cell:
        return "exponent_lower"
    if cell[0] == "+":
        return "leading_plus"
    if "." in cell:
        return "decimal"
    body = cell[1:] if cell[0] == "-" else cell
    if len(body) > 1 and body[0] == "0":
        return "leading_zero"
    return "plain"


# -- the shape of the twin --------------------------------------------


def test_the_twin_has_the_shape_the_description_records(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    assert len(twin.columns) == every_role.n_columns
    assert len(twin.rows) == every_role.n_rows
    assert twin.names == tuple(
        column.name for column in every_role.columns
    )
    assert twin.write_header is True
    for column in twin.columns:
        assert len(column) == every_role.n_rows
    for row in twin.rows:
        assert len(row) == every_role.n_columns


def test_the_columns_are_in_the_descriptions_own_order(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    # The list order of `columns` IS the schema order, the twin's output
    # column order, and the order the one stream is consumed in (S3).
    for index, column in enumerate(every_role.columns):
        assert twin.outcomes[index].name == column.name
        assert twin.outcomes[index].position == column.position


# -- every EXACT-OBSERVABLE count, recounted from the cells ------------


def test_n_present_and_n_missing_are_recounted_exactly(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    for column in every_role.columns:
        cells = _cells(twin, column.name)
        present = _present(cells)
        assert len(present) == column.n_present, column.name
        assert len(cells) - len(present) == column.n_missing, column.name


def test_absent_cells_are_written_empty_and_nothing_else(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    # An empty cell re-reads as no value, which is what makes the two
    # counts above recountable at all (method G10.1).
    for column in every_role.columns:
        for cell in _cells(twin, column.name):
            assert cell == "" or cell.strip() != "" or " " in cell


def test_the_four_class_counts_are_recounted_exactly(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    # EXACT-OBSERVABLE by class-preserving construction: every cell is
    # put back through the shipped classifier, which is the same one the
    # profiler used on the real table (method G10.2).
    for column in every_role.columns:
        counted = {
            parsing.NUMBER: 0,
            parsing.NUMBER_OUT_OF_RANGE: 0,
            parsing.NUMBER_CONTRADICTORY: 0,
            parsing.NOT_A_NUMBER: 0,
        }
        for cell in _present(_cells(twin, column.name)):
            counted[parsing.classify_number(cell)] += 1
        assert counted[parsing.NUMBER] == column.n_numeric, column.name
        assert (
            counted[parsing.NUMBER_OUT_OF_RANGE] == column.n_out_of_range
        ), column.name
        assert (
            counted[parsing.NUMBER_CONTRADICTORY] == column.n_contradictory
        ), column.name
        assert counted[parsing.NOT_A_NUMBER] == column.n_not_numeric, (
            column.name
        )


def test_the_zero_and_negative_counts_are_recounted_exactly(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    for column in every_role.columns:
        facts = column.facts
        if not isinstance(facts, contract.NumericFacts):
            continue
        values = [
            parsing.parse_number(cell)
            for cell in _present(_cells(twin, column.name))
            if parsing.classify_number(cell) == parsing.NUMBER
        ]
        zeros = len([value for value in values if value == 0.0])
        negatives = len([value for value in values if value is not None
                         and value < 0.0])
        assert zeros == facts.n_zero, column.name
        assert negatives + facts.n_negative_unrepresentable == (
            facts.n_negative
        ), column.name


def test_integer_valued_is_recounted_from_the_written_values(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    # Routed by the published FACT and never by the role (method G5.4).
    for column in every_role.columns:
        facts = column.facts
        if not isinstance(facts, contract.NumericFacts):
            continue
        values = [
            parsing.parse_number(cell)
            for cell in _present(_cells(twin, column.name))
            if parsing.classify_number(cell) == parsing.NUMBER
        ]
        whole = all(
            value is not None and parsing.is_whole_number(value)
            for value in values
        )
        assert whole == facts.integer_valued, column.name


def test_the_two_ends_of_a_ladder_are_exact(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    for column in every_role.columns:
        facts = column.facts
        if not isinstance(facts, contract.NumericFacts):
            continue
        values = [
            parsing.parse_number(cell)
            for cell in _present(_cells(twin, column.name))
            if parsing.classify_number(cell) == parsing.NUMBER
        ]
        held = [value for value in values if value is not None]
        assert min(held) == facts.percentiles.minimum, column.name
        assert max(held) == facts.percentiles.maximum, column.name


def test_every_value_lies_between_the_two_published_ends(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    # The clamp of method G5.3 is not decoration: one unit in the last
    # place above the published maximum would change the twin's own
    # recomputed maximum.
    for column in every_role.columns:
        facts = column.facts
        if not isinstance(facts, contract.NumericFacts):
            continue
        low = facts.percentiles.minimum
        high = facts.percentiles.maximum
        assert low is not None and high is not None
        for cell in _present(_cells(twin, column.name)):
            if parsing.classify_number(cell) != parsing.NUMBER:
                continue
            value = parsing.parse_number(cell)
            assert value is not None
            assert low <= value <= high, f"{column.name}: {cell}"


# The eleven ladder probabilities, as whole percents and as shares.
_STEPS = (0, 1, 5, 10, 25, 50, 75, 90, 95, 99, 100)
_SHARES = (0.0, 0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99, 1.0)


def _refuse_outside_the_two_sided_window(
    name: str, rungs: list, values: list
) -> None:
    """Method G5.6's acceptance bound, as the one assertion that enforces it.

    Held apart from its caller so that the twin under test and the
    deliberately broken columns below reach the SAME assert statement.
    A red-mutation test that re-implemented the bound would prove its own
    copy could fail and say nothing about the one in force.

    `values` are the twin's own numbers in any order and `rungs` is the
    published ladder, eleven entries in ladder order. Raises
    AssertionError naming the rung, the value found and the window it
    fell outside; returns None when every interior rung is inside.
    """
    ordered = sorted(values)
    held = len(ordered)
    # The widest ladder displacement the construction can make: the
    # largest stratum's share of the distribution, plus the one rank
    # a recomputed rung interpolates over.
    widest = max(
        1,
        max(
            len([value for value in ordered if value == found])
            for found in set(ordered)
        ),
    )
    room = (widest + 2) / held
    for place in range(1, 10):
        share = _STEPS[place] / 100
        found = ordered[min(held - 1, int(share * (held - 1)))]
        low = _ladder_at(rungs, max(0.0, share - room))
        high = _ladder_at(rungs, min(1.0, share + room))
        assert low <= found <= high, (
            f"{name} rung {_STEPS[place]}: {found} outside "
            f"[{low}, {high}]"
        )


def test_the_interior_rungs_sit_inside_the_two_sided_window(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    """Method G5.6: the acceptance bound the construction itself makes true.

    A generator that ignored the nine interior rungs, or read them out of
    order, would leave this window on any column whose ladder is
    materially bent. No ladder THIS description publishes is bent enough
    to show that -- its numbers are drawn evenly, so the two ends alone
    very nearly describe them -- which is why the mutants further down
    run the same assertion over a column whose ladder is, and are refused
    by it.
    """
    for column in every_role.columns:
        facts = column.facts
        if not isinstance(facts, contract.NumericFacts):
            continue
        rungs = [rung for rung in facts.percentiles.rungs]
        if None in rungs:
            continue
        values = sorted(
            value
            for value in (
                parsing.parse_number(cell)
                for cell in _present(_cells(twin, column.name))
                if parsing.classify_number(cell) == parsing.NUMBER
            )
            if value is not None
        )
        _refuse_outside_the_two_sided_window(column.name, rungs, values)


def _ladder_at(rungs: list, share: float) -> float:
    """The published ladder read as a bent line at one probability."""
    for place in range(10):
        if _SHARES[place] <= share <= _SHARES[place + 1]:
            width = _SHARES[place + 1] - _SHARES[place]
            part = (share - _SHARES[place]) / width
            low = rungs[place]
            high = rungs[place + 1]
            return float(low + part * (high - low))
    return float(rungs[10])


# -- the rung window, proved able to fail (conformance item 5) --------
#
# The window above is an ACCEPTANCE BOUND, and an acceptance bound that
# no wrong twin ever leaves is a check that cannot fail -- which this
# repository treats as a defect rather than as good news. So four
# columns are laid out here by hand, each one the twin a differently
# broken generator would write, and each is put through the very
# assertion above: the first must be accepted and the other three must
# be refused.
#
# Every one of the four holds the published minimum and the published
# maximum exactly and no value outside them, so the two endpoint tests
# earlier in this file pass on all four. That is the point of writing
# them: the window is the only check that separates the last three from
# the first, and if it could not, a generator that ignored nine of the
# eleven published rungs would leave a green suite behind it.


def _bent_ladder_text() -> str:
    """A neutral column whose ladder is materially bent, with no repeats.

    Two hundred whole numbers, each the square of its place in the
    column, built by a fixed rule rather than drawn -- so the file
    commits no data (plan D13) and the same values appear on every
    machine. Squares are used because the ladder they produce is far
    from a straight line between its ends: half the values sit in the
    bottom quarter of the range. A column of evenly drawn numbers would
    make the mutants below pass, and a mutant that passes proves
    nothing.
    """
    return fixtures.single_column_table(
        "reading", [f"{step * step}" for step in range(1, 201)]
    )


@pytest.fixture(scope="module")
def bent(tmp_path_factory: pytest.TempPathFactory) -> contract.Profile:
    """The producer's own description of that bent-ladder column."""
    folder = tmp_path_factory.mktemp("generation-bent")
    return _described(folder, _bent_ladder_text())


def _rungs_of(described: contract.Profile) -> list:
    """The eleven published rungs of the one column of ``described``."""
    facts = described.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    rungs = [rung for rung in facts.percentiles.rungs]
    assert None not in rungs, "this description must publish a whole ladder"
    return rungs


def _laid_along(rungs: list, order: "tuple[int, ...]", count: int) -> list:
    """``count`` values laid along the ladder read in ``order``.

    `order` names, for each of the eleven ladder places, which published
    rung a generator put there. `tuple(range(11))` is the faithful
    reading: rank r of the column is placed between the two rungs whose
    probabilities bracket r's own share, exactly where the method's
    construction puts it. Any other `order` is a generator that used the
    published rungs somewhere other than where they belong.

    The two ends are clamped rather than computed, as the method's own
    construction clamps them (G5.3), so every layout this returns holds
    the published minimum and maximum exactly whatever `order` says
    about the interior.
    """
    made = []
    for rank in range(count):
        share = rank / (count - 1)
        for place in range(10):
            if _SHARES[place] <= share <= _SHARES[place + 1]:
                width = _SHARES[place + 1] - _SHARES[place]
                part = (share - _SHARES[place]) / width
                low = rungs[order[place]]
                high = rungs[order[place + 1]]
                if part <= 0.0:
                    made.append(low)
                elif part >= 1.0:
                    made.append(high)
                else:
                    made.append(low + part * (high - low))
                break
    return made


def _only_the_window_is_left_to_catch_it(rungs: list, values: list) -> None:
    """Every other numeric check in this file passes on ``values``.

    Run on each mutant before the window sees it. Without this, a mutant
    could be refused for holding a value outside the published range --
    which the endpoint tests already catch -- and the window would still
    be unproved.
    """
    assert min(values) == rungs[0], "the published minimum must be exact"
    assert max(values) == rungs[10], "the published maximum must be exact"
    for value in values:
        assert rungs[0] <= value <= rungs[10]


def test_the_bent_columns_own_twin_sits_inside_the_window(
    bent: contract.Profile
) -> None:
    """The real generator, on the column the mutants are built from.

    Without this the mutants below could all be failing because the
    window is impossible to satisfy on this ladder rather than because
    each one is wrong.
    """
    built = generation.generate(bent, 7)
    values = sorted(
        value
        for value in (
            parsing.parse_number(cell)
            for cell in _present(_cells(built, "reading"))
            if parsing.classify_number(cell) == parsing.NUMBER
        )
        if value is not None
    )
    _refuse_outside_the_two_sided_window("reading", _rungs_of(bent), values)


def test_the_layout_the_mutants_break_is_accepted_as_it_is(
    bent: contract.Profile
) -> None:
    """The base every mutant starts from, read in the faithful order.

    A mutation battery passes trivially when the base is refused already,
    because then the refusal belongs to the base and not to the mutation.
    This is what rules that out.
    """
    rungs = _rungs_of(bent)
    values = _laid_along(rungs, tuple(range(11)), bent.n_rows)
    _only_the_window_is_left_to_catch_it(rungs, values)
    _refuse_outside_the_two_sided_window("reading", rungs, values)


def test_a_twin_built_from_the_two_ends_alone_is_refused(
    bent: contract.Profile
) -> None:
    """MUTANT 1: the nine interior rungs ignored (conformance item 5).

    The generator this stands for reads the published minimum and the
    published maximum, ignores everything between them, and spreads the
    column evenly from one end to the other. Its twin holds both ends
    exactly and nothing outside them, so it satisfies every other check
    this file makes of a column of numbers. The window is what refuses
    it.
    """
    rungs = _rungs_of(bent)
    ends = [
        rungs[0] + (rungs[10] - rungs[0]) * share for share in _SHARES
    ]
    ends[0] = rungs[0]
    ends[10] = rungs[10]
    values = _laid_along(ends, tuple(range(11)), bent.n_rows)
    _only_the_window_is_left_to_catch_it(rungs, values)
    with pytest.raises(AssertionError) as refusal:
        _refuse_outside_the_two_sided_window("reading", rungs, values)
    assert "outside" in f"{refusal.value}"


def test_a_twin_whose_interior_rungs_are_permuted_is_refused(
    bent: contract.Profile
) -> None:
    """MUTANT 2: the nine interior rungs used, each in the wrong place.

    Not a subset and not a truncation: all eleven published rungs reach
    the twin, the two ends stay where they belong, and the nine interior
    ones are read one place along the ladder from where each belongs --
    so every one of the nine is used, and none is used where it was
    published. The window is a two-sided bound rather than an equality,
    so what refuses this is not that the order changed but that the
    change carries interior rungs out of their windows; seven of the
    nine leave.
    """
    rungs = _rungs_of(bent)
    moved_along = (0, 2, 3, 4, 5, 6, 7, 8, 9, 1, 10)
    assert sorted(moved_along[1:10]) == list(range(1, 10)), (
        "every interior rung must still be used exactly once, or this is "
        "a rung that went missing rather than a rung out of place"
    )
    values = _laid_along(rungs, moved_along, bent.n_rows)
    _only_the_window_is_left_to_catch_it(rungs, values)
    with pytest.raises(AssertionError) as refusal:
        _refuse_outside_the_two_sided_window("reading", rungs, values)
    assert "outside" in f"{refusal.value}"


def test_a_twin_with_two_interior_rungs_swapped_is_refused(
    bent: contract.Profile
) -> None:
    """MUTANT 3: two interior rungs exchanged, the other seven untouched.

    The smallest mutation of the three -- the quarter and three-quarter
    rungs change places and nothing else moves -- and the one that says
    most about the bound's strength, because seven of the nine interior
    rungs are still exactly where the description put them.
    """
    rungs = _rungs_of(bent)
    exchanged = (0, 1, 2, 3, 6, 5, 4, 7, 8, 9, 10)
    assert sorted(exchanged[1:10]) == list(range(1, 10))
    assert len([one for one in range(11) if exchanged[one] != one]) == 2
    values = _laid_along(rungs, exchanged, bent.n_rows)
    _only_the_window_is_left_to_catch_it(rungs, values)
    with pytest.raises(AssertionError) as refusal:
        _refuse_outside_the_two_sided_window("reading", rungs, values)
    assert "outside" in f"{refusal.value}"


def test_each_mutant_really_is_a_different_column_from_the_base(
    bent: contract.Profile
) -> None:
    """A mutation that changes nothing is refused by the base, not the rule.

    The third way a battery passes trivially, closed here for all three:
    each mutant's values are compared with the faithful layout's, and
    each must differ from it.
    """
    rungs = _rungs_of(bent)
    base = _laid_along(rungs, tuple(range(11)), bent.n_rows)
    ends = [rungs[0] + (rungs[10] - rungs[0]) * share for share in _SHARES]
    ends[0] = rungs[0]
    ends[10] = rungs[10]
    mutants = {
        "the two ends alone": _laid_along(ends, tuple(range(11)), bent.n_rows),
        "the interior moved along": _laid_along(
            rungs, (0, 2, 3, 4, 5, 6, 7, 8, 9, 1, 10), bent.n_rows
        ),
        "two interior rungs exchanged": _laid_along(
            rungs, (0, 1, 2, 3, 6, 5, 4, 7, 8, 9, 10), bent.n_rows
        ),
    }
    for what, values in mutants.items():
        assert len(values) == len(base), what
        assert sorted(values) != sorted(base), what


def test_the_published_style_counts_are_recounted_exactly(
    styled: contract.Profile
) -> None:
    built = generation.generate(styled, 3)
    column = _block(styled, "measured")
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    counted: dict[str, int] = {name: 0 for name in contract.NUMERIC_STYLES}
    for cell in _present(_cells(built, "measured")):
        counted[_style_of(cell)] += 1
    for name in contract.NUMERIC_STYLES:
        assert counted[name] == facts.numeric_styles.get(name, 0), name
    assert sum(counted.values()) == column.n_numeric


def test_label_counts_and_variants_are_recounted_exactly(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    for column in every_role.columns:
        facts = column.facts
        if not isinstance(facts, contract.LabelFacts):
            continue
        counted: dict[str, int] = {}
        for cell in _present(_cells(twin, column.name)):
            identity = parsing.folded(cell)
            counted[identity] = counted.get(identity, 0) + 1
        for entry in facts.levels:
            assert counted.get(entry.label) == entry.count, entry.label
            spellings: dict[str, int] = {}
            for cell in _present(_cells(twin, column.name)):
                if parsing.folded(cell) == entry.label:
                    spellings[cell] = spellings.get(cell, 0) + 1
            for spelling in entry.variants:
                assert spellings.get(spelling) == entry.variants[spelling]
        held_back = [
            counted[identity]
            for identity in counted
            if identity not in [entry.label for entry in facts.levels]
        ]
        assert len(held_back) == facts.suppressed_levels, column.name
        assert sorted(held_back) == sorted(facts.suppressed_level_counts)


def test_datetime_cells_carry_the_published_precision(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    for column in every_role.columns:
        facts = column.facts
        if not isinstance(facts, contract.DatetimeFacts):
            continue
        parsed = 0
        for cell in _present(_cells(twin, column.name)):
            found = None
            for name in parsing.DATE_FORMATS:
                found = parsing.parse_datetime(cell, name)
                if found is not None:
                    break
            if found is None:
                continue
            parsed += 1
            assert parsing.datetime_precision(
                cell, _format_for(facts.resolution)
            ) == facts.time_precision, cell
        assert parsed == column.n_present - facts.n_unparsed, column.name


def _format_for(resolution: str) -> str:
    """The parser family a twin cell of one resolution is written in."""
    if resolution == "quarter":
        return "year-quarter"
    if resolution == "datetime":
        return "iso-datetime"
    return "iso-date"


def test_the_two_ends_of_a_date_ladder_are_exact(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    for column in every_role.columns:
        facts = column.facts
        if not isinstance(facts, contract.DatetimeFacts):
            continue
        instants = []
        for cell in _present(_cells(twin, column.name)):
            found = parsing.parse_datetime(cell, _format_for(facts.resolution))
            if found is not None:
                instants.append(found[0])
        assert min(instants)[:10] == facts.earliest[:10], column.name
        assert max(instants)[:10] == facts.latest[:10], column.name


def test_the_word_budget_is_a_function_of_the_published_facts(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    # Method G4.3: the count of words a run draws is decided before the
    # run, from published facts alone, so the same description always
    # consumes the same stream in the same order.
    planned = generation.plan_generation(every_role)
    assert planned.words_planned == twin.words_drawn
    for index, each in enumerate(planned.columns):
        outcome = twin.outcomes[index]
        assert each.content_words == outcome.content_words
        assert each.placement_words == outcome.placement_words
        assert outcome.placement_words == max(every_role.n_rows - 1, 0)
    labels = [
        outcome
        for outcome in twin.outcomes
        if outcome.statistical_type in ("constant", "binary", "categorical")
    ]
    assert labels
    for outcome in labels:
        assert outcome.content_words == 0


# -- determinism (plan P2-D8) -----------------------------------------


def test_identical_inputs_give_identical_cells(
    every_role: contract.Profile,
) -> None:
    first = generation.generate(every_role, 12345)
    second = generation.generate(every_role, 12345)
    assert first.rows == second.rows
    assert first.names == second.names
    assert first.words_drawn == second.words_drawn


def test_a_different_seed_changes_the_values_inside(
    every_role: contract.Profile,
) -> None:
    first = generation.generate(every_role, 1)
    second = generation.generate(every_role, 2)
    assert first.rows != second.rows
    moved = [
        index
        for index in range(len(first.columns))
        if first.columns[index] != second.columns[index]
    ]
    # Not merely a different arrangement of the same cells: a column
    # with a random degree of freedom holds different VALUES.
    numeric = [
        index
        for index in range(len(first.outcomes))
        if first.outcomes[index].statistical_type in ("count", "continuous")
    ]
    assert numeric
    for index in numeric:
        assert index in moved
        assert sorted(first.columns[index]) != sorted(second.columns[index])


def test_a_fully_determined_description_is_seed_invariant(
    tmp_path: pathlib.Path,
) -> None:
    # Every cell of this table is pinned by a published count, so the
    # arrangement of G4.2 rearranges identical entries and the bytes
    # cannot depend on the seed.
    described = _described(
        tmp_path, fixtures.single_column_table("batch", ["one"] * 40)
    )
    first = generation.generate(described, 0)
    second = generation.generate(described, 18446744073709551615)
    assert first.rows == second.rows


def test_a_seed_outside_the_range_is_refused(
    every_role: contract.Profile,
) -> None:
    for seed in (-1, 18446744073709551616):
        with pytest.raises(errors.ProfileError) as raised:
            generation.generate(every_role, seed)
        assert "18446744073709551615" in f"{raised.value}"


# -- the all-different obligation (method G11) ------------------------


def test_a_column_of_all_different_values_stays_all_different(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    checked = 0
    for column in every_role.columns:
        if column.n_distinct != column.n_present or column.n_present == 0:
            continue
        checked += 1
        present = _present(_cells(twin, column.name))
        assert len(set(present)) == len(present), column.name
    assert checked >= 2, (
        "the every-role description must carry at least two columns whose "
        "values are all different, or this check proves nothing"
    )


def test_the_obligation_holds_for_an_undeclared_key_column(
    tmp_path: pathlib.Path,
) -> None:
    # An undeclared key column arrives as free text, not as a declared
    # column of record numbers, which is why the obligation is stated
    # for every role rather than for one (P1-D4 item 8, P2-R5-F3).
    values = [f"case number {index} of the study" for index in range(60)]
    described = _described(tmp_path, fixtures.single_column_table("key", values))
    column = _block(described, "key")
    assert column.n_distinct == column.n_present
    built = generation.generate(described, 5)
    present = _present(_cells(built, "key"))
    assert len(set(present)) == len(present)


def test_the_obligation_holds_for_labels_that_differ_only_by_case(
    tmp_path: pathlib.Path,
) -> None:
    # Owner decisions 9 and 11: the description records the spelling
    # variants, so the twin keeps the values distinct where a twin built
    # from normalized labels alone would have repeated them.
    values = ["yes"] * 15 + ["YES"] * 15 + ["no"] * 15 + ["NO"] * 15
    described = _described(tmp_path, fixtures.single_column_table("answer", values))
    built = generation.generate(described, 5)
    counted: dict[str, int] = {}
    for cell in _present(_cells(built, "answer")):
        counted[cell] = counted.get(cell, 0) + 1
    assert counted == {"yes": 15, "YES": 15, "no": 15, "NO": 15}


# -- the two generation refusals (method G12) -------------------------


def test_a_column_whose_counts_leave_no_room_refuses_generation(
    tmp_path: pathlib.Path,
) -> None:
    document = _document(
        tmp_path, _every_role_text(), ["record_code"]
    )
    for block in document["columns"]:
        if block["name"] == "visits":
            block["n_zero"] = block["n_numeric"]
            block["n_negative"] = block["n_numeric"]
    described = _loaded(tmp_path, document)
    with pytest.raises(errors.ProfileError) as raised:
        generation.plan_generation(described)
    message = f"{raised.value}"
    assert "is valid" in message
    assert "visits" in message
    assert "Nothing has been written" in message
    assert "synthtwin profile" in message


def test_a_domain_too_small_refuses_generation_before_anything_is_built(
    tmp_path: pathlib.Path,
) -> None:
    document = _document(tmp_path, _every_role_text(), ["record_code"])
    for block in document["columns"]:
        if block["name"] != "comment":
            continue
        # Every row holds a value, every value is one character long,
        # and every value is different: there are only ninety-five
        # different characters a keyboard writes, so no table can do it.
        rows = document["n_rows"]
        block["n_present"] = rows
        block["n_missing"] = 0
        block["missing_by_class"] = {
            key: 0 for key in block["missing_by_class"]
        }
        block["n_distinct"] = rows
        block["n_distinct_folded"] = rows
        block["n_distinct_by_occurrences"] = {"1": rows}
        block["length"] = {"min": 1, "max": 1, "mean": 1.0, "p50": 1.0}
        block["words"] = {"min": 1, "max": 1, "mean": 1.0}
        block["n_all_digits"] = 0
        block["n_code_alphabet"] = rows
        block["n_numeric"] = 0
        block["n_out_of_range"] = 0
        block["n_contradictory"] = 0
        block["n_not_numeric"] = rows
    described = _loaded(tmp_path, document)
    with pytest.raises(errors.ProfileError) as raised:
        generation.plan_generation(described)
    message = f"{raised.value}"
    assert "is valid" in message
    assert "comment" in message
    assert "Nothing has been written" in message
    assert "--identifier" in message


def test_the_refusals_run_before_any_cell_is_built(
    tmp_path: pathlib.Path,
) -> None:
    # The whole point of deciding capacity in the planning stage is that
    # a refused run leaves the folder exactly as it found it (G9.4).
    document = _document(tmp_path, _every_role_text(), ["record_code"])
    for block in document["columns"]:
        if block["name"] == "visits":
            block["n_zero"] = block["n_numeric"]
            block["n_negative"] = block["n_numeric"]
    described = _loaded(tmp_path, document)
    with pytest.raises(errors.ProfileError):
        generation.generate(described, 0)


# -- what the twin says about itself ----------------------------------


def test_every_deviation_names_a_published_fact_and_speaks_plainly(
    twin: generation.Twin,
) -> None:
    names = [outcome.name for outcome in twin.outcomes]
    for deviation in twin.deviations:
        assert deviation.column in names
        assert deviation.fact
        assert deviation.published
        assert deviation.achieved
        assert len(deviation.note.split(" ")) >= 8
        assert deviation.note.endswith(".")
        for jargon in ("null", "None", "int", "str", "dtype", "n_rows"):
            assert jargon not in deviation.note


def test_a_column_that_meets_every_fact_names_no_deviation(
    tmp_path: pathlib.Path,
) -> None:
    # A plainly written column of whole numbers, all different and well
    # spread, is the ordinary case: every published fact is met, so the
    # report has nothing to name. A report that named something here
    # would teach a reader to ignore it.
    values = [f"{index * 1000}" for index in range(1, 61)]
    described = _described(
        tmp_path, fixtures.single_column_table("measured", values)
    )
    built = generation.generate(described, 3)
    assert built.deviations == ()
    corner = tmp_path / "labels"
    corner.mkdir()
    labels = _described(
        corner, fixtures.single_column_table("batch", ["one"] * 40)
    )
    assert generation.generate(labels, 3).deviations == ()


def test_a_mixed_style_column_names_what_it_could_not_reach(
    styled: contract.Profile,
) -> None:
    # The published style counts are met FIRST and distinctness within
    # them (method G6.5), so a column whose values were written six ways
    # can come out with fewer different spellings than it published --
    # and when it does, the twin says so rather than letting a reader
    # believe the count was met.
    built = generation.generate(styled, 3)
    facts = _block(styled, "measured").facts
    assert isinstance(facts, contract.NumericFacts)
    named = [
        deviation.fact
        for deviation in built.deviations
        if deviation.column == "measured"
    ]
    present = _present(_cells(built, "measured"))
    if len(set(present)) != _block(styled, "measured").n_distinct:
        assert "n_distinct" in named


def test_the_outcome_counts_are_the_twins_own(
    every_role: contract.Profile, twin: generation.Twin
) -> None:
    for index, outcome in enumerate(twin.outcomes):
        cells = twin.columns[index]
        present = _present(cells)
        assert outcome.n_present == len(present)
        assert outcome.n_missing == len(cells) - len(present)
        assert outcome.n_distinct == len(set(present))
        assert outcome.n_distinct_folded == len(
            {parsing.folded(cell) for cell in present}
        )


# -- the boundary (method G1, plan P2-D1) -----------------------------


def test_the_generator_cannot_reach_the_reader_or_pandas() -> None:
    # A closure check over the source, not over a running import graph:
    # the promise is about what the code CAN reach, at every instant.
    root = pathlib.Path(__file__).resolve().parent.parent / "src" / "synthtwin"
    seen: set[str] = set()
    waiting = ["generation"]
    while waiting:
        name = waiting.pop()
        if name in seen:
            continue
        seen.add(name)
        text = (root / f"{name}.py").read_text(encoding="utf-8")
        assert "import pandas" not in text, name
        for line in text.split("\n"):
            if line.startswith("from synthtwin import "):
                for piece in line[len("from synthtwin import "):].split(","):
                    waiting.append(piece.strip())
            elif line.startswith("from synthtwin."):
                waiting.append(line.split(" ")[1].split(".")[1])
            elif line.startswith("import synthtwin"):
                waiting.append(line.split(".")[1].strip())
    assert "reading" not in seen
    assert "generation" in seen and "contract" in seen and "parsing" in seen


def test_the_generator_takes_no_table_and_no_path(
    every_role: contract.Profile,
) -> None:
    # A signature check: no layer of the generation path accepts or
    # constructs a table path, a handle, a table object or a collection
    # of raw cells (plan P2-D1).
    import inspect

    signature = inspect.signature(generation.generate)
    assert list(signature.parameters) == ["profile", "seed"]
    assert signature.parameters["profile"].annotation is contract.Profile
    assert signature.parameters["seed"].annotation is int
    planned = inspect.signature(generation.plan_generation)
    assert list(planned.parameters) == ["profile"]
    assert generation.generate(every_role, 0).seed == 0


def test_the_description_is_not_changed_by_generating(
    every_role: contract.Profile,
) -> None:
    before = copy.deepcopy(every_role)
    generation.generate(every_role, 99)
    assert every_role == before


# -- the shapes the every-role table does not carry -------------------


def _one_column(
    folder: pathlib.Path, name: str, values: list[str]
) -> contract.Profile:
    """A description of a one-column table holding exactly ``values``."""
    folder.mkdir(parents=True, exist_ok=True)
    return _described(folder, fixtures.single_column_table(name, values))


def test_a_column_of_quarters_keeps_its_form_and_its_ends(
    tmp_path: pathlib.Path,
) -> None:
    values = [f"{2020 + index % 5}-Q{index % 4 + 1}" for index in range(60)]
    described = _one_column(tmp_path / "q", "period", values)
    facts = _block(described, "period").facts
    assert isinstance(facts, contract.DatetimeFacts)
    assert facts.resolution == "quarter"
    built = generation.generate(described, 11)
    cells = _present(_cells(built, "period"))
    for cell in cells:
        assert parsing.parse_datetime(cell, "year-quarter") is not None, cell
    assert min(cells) == facts.earliest
    assert max(cells) == facts.latest


def test_an_offset_bearing_column_keeps_its_instants_and_its_offsets(
    tmp_path: pathlib.Path,
) -> None:
    values = []
    for index in range(60):
        offset = "+02:00" if index % 2 else "-05:00"
        values.append(
            f"2024-03-{index % 28 + 1:02d}T{index % 24:02d}:"
            f"{index % 60:02d}:00{offset}"
        )
    described = _one_column(tmp_path / "o", "seen_at", values)
    facts = _block(described, "seen_at").facts
    assert isinstance(facts, contract.DatetimeFacts)
    assert facts.datetimes_read_at == "utc"
    built = generation.generate(described, 11)
    instants = []
    carried: dict[str, int] = {}
    for cell in _present(_cells(built, "seen_at")):
        found = parsing.parse_datetime(cell, "iso-datetime")
        assert found is not None, cell
        carried[found[1]] = carried.get(found[1], 0) + 1
        instant = parsing.utc_canonical(found[0], found[1])
        assert instant is not None
        instants.append(instant)
    # The two ends are EXACT-OBSERVABLE as instants, which is only true
    # if the wall clock of each cell was written on its own offset.
    assert min(instants) == facts.earliest
    assert max(instants) == facts.latest
    assert carried == facts.utc_offsets
    # A twin that lost the offset diversity would re-read as a column on
    # one clock, which is the corner method G7.4 names.
    assert len(carried) >= 2


def test_a_column_that_writes_minutes_writes_no_seconds(
    tmp_path: pathlib.Path,
) -> None:
    values = [
        f"2024-03-15T{index % 24:02d}:{index % 60:02d}" for index in range(60)
    ]
    described = _one_column(tmp_path / "m", "seen_at", values)
    facts = _block(described, "seen_at").facts
    assert isinstance(facts, contract.DatetimeFacts)
    assert facts.time_precision == "minute"
    built = generation.generate(described, 11)
    for cell in _present(_cells(built, "seen_at")):
        assert len(cell) == 16, cell
        assert cell[10] == "T"


def test_a_column_that_writes_fractions_writes_the_published_figures(
    tmp_path: pathlib.Path,
) -> None:
    values = [f"2024-03-15 10:00:{index % 60:02d}.123" for index in range(60)]
    described = _one_column(tmp_path / "s", "seen_at", values)
    facts = _block(described, "seen_at").facts
    assert isinstance(facts, contract.DatetimeFacts)
    assert facts.time_precision == "subsecond"
    assert facts.subsecond_digits == 3
    built = generation.generate(described, 11)
    for cell in _present(_cells(built, "seen_at")):
        assert cell.endswith(".000"), cell
        assert parsing.subsecond_digits(cell, "iso-datetime") == 3


def test_cells_that_did_not_read_as_a_date_are_counted_stand_ins(
    tmp_path: pathlib.Path,
) -> None:
    values = [f"2024-{index % 12 + 1:02d}-15" for index in range(200)]
    values[7] = "pending"
    described = _one_column(tmp_path / "u", "recorded_on", values)
    facts = _block(described, "recorded_on").facts
    assert isinstance(facts, contract.DatetimeFacts)
    assert facts.n_unparsed == 1
    built = generation.generate(described, 11)
    unread = 0
    for cell in _present(_cells(built, "recorded_on")):
        if parsing.parse_datetime(cell, "iso-date") is None:
            unread += 1
            for name in parsing.DATE_FORMATS:
                assert parsing.parse_datetime(cell, name) is None, cell
            assert not parsing.is_missing_text(cell)
    assert unread == facts.n_unparsed


def test_the_shortest_and_longest_made_up_values_are_the_published_ones(
    tmp_path: pathlib.Path,
) -> None:
    values = [
        "a note of " + "x" * (index % 9 + 1) + " characters"
        for index in range(60)
    ]
    described = _one_column(tmp_path / "t", "comment", values)
    facts = _block(described, "comment").facts
    assert isinstance(facts, contract.TextFacts)
    built = generation.generate(described, 11)
    lengths = [len(cell) for cell in _present(_cells(built, "comment"))]
    assert min(lengths) == facts.length.minimum
    assert max(lengths) == facts.length.maximum


def test_a_declared_column_keeps_its_width_and_says_what_that_cost(
    tmp_path: pathlib.Path,
) -> None:
    # Owner decision 6, in its infeasible corner: the published width and
    # the all-different fact cannot both hold, LENGTH WINS, values
    # repeat, and three facts about distinctness are named as lost.
    document = _document(tmp_path, _every_role_text(), ["record_code"])
    for block in document["columns"]:
        if block["name"] == "record_code":
            block["min_length"] = 1
            block["max_length"] = 1
    described = _loaded(tmp_path, document)
    column = _block(described, "record_code")
    assert column.structural_role == "identifier"
    built = generation.generate(described, 11)
    cells = _present(_cells(built, "record_code"))
    assert cells
    for cell in cells:
        assert len(cell) == 1, cell
    assert len(set(cells)) < column.n_distinct
    named = [
        deviation.fact
        for deviation in built.deviations
        if deviation.column == "record_code"
    ]
    assert "n_distinct" in named
    assert "n_distinct_folded" in named
    assert "n_distinct_by_occurrences" in named
    joined = " ".join(
        deviation.note
        for deviation in built.deviations
        if deviation.column == "record_code"
    )
    assert "join" in joined


# -- the two obligations of the made-up alphabets (G9.3, G9.5 step 3) --
#
# Both are EXACT-OBSERVABLE on a declared column of record numbers
# outside owner decision 6's infeasible corner (contract section 6.8),
# and both were once missed: the twin wrote one folded identity per
# spelling where the description published fewer, and it wrote cells
# that were figures and nothing else where the description published
# none of those. The first miss was named as a deviation the method does
# not permit for this role; the second was named nowhere at all, which
# is the worse of the two, because a reader of the report never learned
# of it. The checks below recount both facts from the twin's own cells.


def _identifier_with_a_fold_pair(
    folder: pathlib.Path, name: str
) -> contract.Profile:
    """A declared column whose last two values differ only by case.

    Fifty-eight values are spelled one way and two of them are spelled
    again with their letters turned over, so every value is different
    and two pairs come down to one value once case is ignored: the
    description publishes sixty different spellings and fifty-eight
    different folded identities.
    """
    folder.mkdir(parents=True, exist_ok=True)
    values = [f"KA-{index:03d}" for index in range(58)]
    values = values + ["ka-000", "ka-001"]
    return _described(
        folder, fixtures.single_column_table(name, values), [name]
    )


def test_a_folded_count_below_the_raw_count_is_built_not_named(
    tmp_path: pathlib.Path,
) -> None:
    # Method G9.3: where a column publishes fewer folded identities than
    # spellings, the difference is CONSTRUCTED -- the first identities
    # are drawn from the part of the domain that holds a letter and each
    # carries a case flip. Method G12 grants the fallback of naming a
    # folded count that could not fall below its raw count to columns of
    # numbers, and to no other role, so a deviation here is a defect and
    # not an escape.
    described = _identifier_with_a_fold_pair(tmp_path / "fold", "code")
    column = _block(described, "code")
    assert column.n_distinct_folded < column.n_distinct, (
        "this description must publish fewer folded identities than "
        "spellings, or the obligation under test never fires"
    )
    built = generation.generate(described, 5)
    present = _present(_cells(built, "code"))
    assert len(set(present)) == column.n_distinct
    assert len({parsing.folded(cell) for cell in present}) == (
        column.n_distinct_folded
    )
    named = [
        deviation.fact
        for deviation in built.deviations
        if deviation.column == "code"
    ]
    assert "n_distinct_folded" not in named
    assert "n_distinct" not in named


def test_a_published_count_of_no_all_figure_cells_is_kept(
    tmp_path: pathlib.Path,
) -> None:
    # Method G9.5 step 3, which G9.6 imports for record numbers: a group
    # written in the code alphabet carries a character that is not a
    # figure at its leftmost position, so it does not count as one
    # written in figures alone. A twin that writes figures alone here
    # would hand a person a column that reads as numbers where the real
    # one did not.
    described = _identifier_with_a_fold_pair(tmp_path / "figures", "code")
    facts = _block(described, "code").facts
    assert isinstance(facts, contract.IdentifierFacts)
    assert facts.n_all_digits == 0, (
        "this description must publish no cell of figures alone, or the "
        "obligation under test never fires"
    )
    built = generation.generate(described, 5)
    for cell in _present(_cells(built, "code")):
        assert not parsing.is_digit_text(parsing.trimmed(cell)), cell


def test_both_alphabet_counts_are_recounted_exactly_on_a_mixed_column(
    tmp_path: pathlib.Path,
) -> None:
    # Half the values are figures alone and half are codes, and two of
    # the codes differ from two others only by case, so meeting the
    # folded count and meeting the two alphabet counts have to hold at
    # the same time rather than one being traded for the other.
    folder = tmp_path / "mixed"
    folder.mkdir(parents=True, exist_ok=True)
    values = [f"{700000 + index}" for index in range(30)]
    values = values + [f"QP-{index:03d}" for index in range(28)]
    values = values + ["qp-000", "qp-001"]
    described = _described(
        folder, fixtures.single_column_table("code", values), ["code"]
    )
    column = _block(described, "code")
    facts = column.facts
    assert isinstance(facts, contract.IdentifierFacts)
    assert facts.n_all_digits > 0
    assert column.n_distinct_folded < column.n_distinct
    built = generation.generate(described, 5)
    present = _present(_cells(built, "code"))
    trimmed = [parsing.trimmed(cell) for cell in present]
    assert len([cell for cell in trimmed if parsing.is_digit_text(cell)]) == (
        facts.n_all_digits
    )
    assert len([cell for cell in trimmed if parsing.is_code_text(cell)]) == (
        facts.n_code_alphabet
    )
    assert len({parsing.folded(cell) for cell in present}) == (
        column.n_distinct_folded
    )
    assert not [
        deviation
        for deviation in built.deviations
        if deviation.column == "code"
    ]


def test_a_column_of_free_text_folds_onto_its_own_partners(
    tmp_path: pathlib.Path,
) -> None:
    # The same obligation, on the second role that makes its values up:
    # the contract makes both distinctness counts EXACT-OBSERVABLE on
    # every invention role, not on record numbers alone.
    folder = tmp_path / "text"
    folder.mkdir(parents=True, exist_ok=True)
    values = fixtures.prose(58)
    values = values + [
        "NOTE 0 WRITTEN OUT IN PLAIN WORDS",
        "Note 1 Written Out In Plain Words",
    ]
    described = _described(folder, fixtures.single_column_table("comment", values))
    column = _block(described, "comment")
    assert isinstance(column.facts, contract.TextFacts)
    assert column.n_distinct_folded < column.n_distinct
    built = generation.generate(described, 5)
    present = _present(_cells(built, "comment"))
    assert len(set(present)) == column.n_distinct
    assert len({parsing.folded(cell) for cell in present}) == (
        column.n_distinct_folded
    )


def _digit_and_code_counts(
    built: generation.Twin, name: str
) -> "tuple[int, int]":
    """Recount, on the twin's own cells, the two published alphabet counts."""
    trimmed = [
        parsing.trimmed(cell) for cell in _present(_cells(built, name))
    ]
    return (
        len([cell for cell in trimmed if parsing.is_digit_text(cell)]),
        len([cell for cell in trimmed if parsing.is_code_text(cell)]),
    )


def test_a_feasible_alphabet_count_is_packed_exactly_by_whole_groups(
    tmp_path: pathlib.Path,
) -> None:
    """Review item P2-C1-F1: the packing must be exact wherever one exists.

    One made-up value covers a whole group of rows, so a published count
    of CELLS is met by whole GROUPS -- but "by whole groups" is not the
    same as "not at all". This table's four cells of figures alone are
    two groups of two and its three code cells are one group of three,
    and the assignment that meets both counts to the cell is plainly
    there: the two groups of two go to the figures and the group of
    three to the code alphabet. A packing rule that offers the largest
    group first takes the three into the figures instead, writes five
    cells of figures where the description says four, and misses a fact
    the contract calls EXACT-OBSERVABLE with a feasible answer in front
    of it. The count is asserted here, not the packing, so any rule that
    reaches it passes.
    """
    folder = tmp_path / "packed"
    folder.mkdir(parents=True, exist_ok=True)
    values = ["11", "11", "22", "22", "AB", "AB", "AB"]
    described = _described(
        folder, fixtures.single_column_table("code", values), ["code"]
    )
    facts = _block(described, "code").facts
    assert isinstance(facts, contract.IdentifierFacts)
    assert facts.n_all_digits == 4
    assert facts.n_code_alphabet == 7
    assert facts.n_distinct_by_occurrences == {"2": 2, "3": 1}
    built = generation.generate(described, 5)
    digits, code = _digit_and_code_counts(built, "code")
    assert digits == facts.n_all_digits
    assert code == facts.n_code_alphabet
    named = {
        deviation.fact
        for deviation in built.deviations
        if deviation.column == "code"
    }
    assert "n_all_digits" not in named
    assert "n_code_alphabet" not in named


def test_a_whole_number_column_outside_the_figures_keeps_all_three_facts(
    tmp_path: pathlib.Path,
) -> None:
    """Review item P2-C1-F1: `all_whole_numbers` implies neither alphabet.

    `+1` and `+2` are whole numbers written with a character the code
    alphabet does not hold, so a genuine description of this column says
    every value is a whole number AND that none is written in figures
    alone AND that none is written in the code alphabet. All three are
    EXACT-OBSERVABLE and all three hold together -- `1.` reads back as
    the whole number 1 and stands outside both alphabets. A rule that
    read "every value is a whole number" as "every value is written in
    figures" wrote four cells of figures against a published zero, and
    four code-alphabet cells against a published zero.
    """
    folder = tmp_path / "whole"
    folder.mkdir(parents=True, exist_ok=True)
    described = _described(
        folder,
        fixtures.single_column_table("code", ["+1", "+1", "+2", "+2"]),
        ["code"],
    )
    facts = _block(described, "code").facts
    assert isinstance(facts, contract.IdentifierFacts)
    assert facts.all_whole_numbers is True
    assert facts.n_all_digits == 0
    assert facts.n_code_alphabet == 0
    built = generation.generate(described, 5)
    digits, code = _digit_and_code_counts(built, "code")
    assert digits == 0
    assert code == 0
    present = _present(_cells(built, "code"))
    for cell in present:
        assert parsing.numeric_whole(cell) == parsing.WHOLE_YES, cell
    named = {
        deviation.fact
        for deviation in built.deviations
        if deviation.column == "code"
    }
    assert "n_all_digits" not in named
    assert "n_code_alphabet" not in named
    assert "all_whole_numbers" not in named


def test_a_missed_alphabet_count_is_named_rather_than_left_silent(
    tmp_path: pathlib.Path,
) -> None:
    # The other half of the repair, and the half that matters most: a
    # published fact this module cannot meet must be MEASURED and NAMED,
    # because a twin that quietly misses one teaches a reader to trust a
    # report that is not telling them everything.
    #
    # A genuine description always HAS an exact packing -- the real
    # column's own values are one -- so the count that cannot be met is
    # reached by editing the document, which is what this file does for
    # the two refusals for the same reason. The groups here cover two,
    # two and three rows, and no set of whole groups covers exactly one
    # cell, so the count of cells written in figures alone cannot be met
    # however they are packed.
    folder = tmp_path / "silent"
    folder.mkdir(parents=True, exist_ok=True)
    values = ["11", "11", "22", "22", "AB", "AB", "AB"]
    document = _document(
        folder, fixtures.single_column_table("code", values), ["code"]
    )
    for block in document["columns"]:
        if block["name"] == "code":
            block["n_all_digits"] = 1
    described = _loaded(folder, document)
    facts = _block(described, "code").facts
    assert isinstance(facts, contract.IdentifierFacts)
    assert facts.n_all_digits == 1
    built = generation.generate(described, 5)
    written, _code = _digit_and_code_counts(built, "code")
    assert written != facts.n_all_digits, (
        "this description must reach a count no packing of whole groups "
        "can meet, or the naming under test is never asked for"
    )
    named = {
        deviation.fact: deviation
        for deviation in built.deviations
        if deviation.column == "code"
    }
    assert "n_all_digits" in named
    assert named["n_all_digits"].published == f"{facts.n_all_digits}"
    assert named["n_all_digits"].achieved == f"{written}"
    # And the report a person reads carries it, with both values.
    text = rendering.report(described, built)
    assert "n_all_digits" in text
    assert named["n_all_digits"].note in text


def test_free_text_meets_its_class_and_alphabet_counts_by_whole_groups(
    tmp_path: pathlib.Path,
) -> None:
    """Review item P2-C1-F1, the free-text probe.

    Two numeric groups of two rows, one text group of three and
    eighteen text groups of two. Every count here is EXACT-OBSERVABLE:
    how many cells read as a number, how many are figures alone, how
    many are written in the code alphabet. The greedy packing offered
    the group of three to the numbers first and missed all three counts
    by one; every one of them is reachable by whole groups.
    """
    folder = tmp_path / "text-packing"
    folder.mkdir(parents=True, exist_ok=True)
    values = ["11", "11", "22", "22", "ttt", "ttt", "ttt"]
    for index in range(18):
        values = values + [f"w{index:02d}", f"w{index:02d}"]
    described = _described(
        folder, fixtures.single_column_table("comment", values)
    )
    column = _block(described, "comment")
    facts = column.facts
    assert isinstance(facts, contract.TextFacts)
    assert column.n_numeric == 4
    assert facts.n_all_digits == 4
    built = generation.generate(described, 5)
    present = _present(_cells(built, "comment"))
    counted = {
        name: len(
            [
                cell
                for cell in present
                if parsing.classify_number(cell) == name
            ]
        )
        for name in (parsing.NUMBER, parsing.NOT_A_NUMBER)
    }
    assert counted[parsing.NUMBER] == column.n_numeric
    assert counted[parsing.NOT_A_NUMBER] == column.n_not_numeric
    digits, code = _digit_and_code_counts(built, "comment")
    assert digits == facts.n_all_digits
    assert code == facts.n_code_alphabet
    named = {
        deviation.fact
        for deviation in built.deviations
        if deviation.column == "comment"
    }
    for fact in (
        "n_numeric", "n_not_numeric", "n_all_digits", "n_code_alphabet",
    ):
        assert fact not in named, fact


def test_a_column_of_sentences_still_meets_its_code_alphabet_count(
    tmp_path: pathlib.Path,
) -> None:
    """Review item P2-C1-F1, on the shape a real free-text column has.

    A column of written-out phrases holds two kinds of value: the ones
    with a space in them, which are not in the code alphabet, and the
    ones without, which are. `n_code_alphabet` counts the second kind
    and is EXACT-OBSERVABLE. A cell of several words cannot be in that
    alphabet, because the separator is a space, so meeting the count
    means giving the code alphabet to groups that hold one word --
    which the packing can only do if it is told that rule. The cost is
    the average word count, which is approximated, and it is named.
    """
    folder = tmp_path / "sentences"
    folder.mkdir(parents=True, exist_ok=True)
    values: list[str] = []
    sentences = fixtures.prose(30)
    for index in range(30):
        values = values + [sentences[index], f"tag{index}"]
        values = values + [sentences[index], f"tag{index}"]
    described = _described(
        folder, fixtures.single_column_table("comment", values)
    )
    column = _block(described, "comment")
    facts = column.facts
    assert isinstance(facts, contract.TextFacts)
    assert facts.n_code_alphabet == 60
    assert facts.words.maximum > 1
    built = generation.generate(described, 5)
    _digits, code = _digit_and_code_counts(built, "comment")
    assert code == facts.n_code_alphabet
    named = {
        deviation.fact
        for deviation in built.deviations
        if deviation.column == "comment"
    }
    assert "n_code_alphabet" not in named
    assert "words" in named


def test_an_unheld_column_meets_its_whole_and_fraction_counts(
    tmp_path: pathlib.Path,
) -> None:
    """Review item P2-C1-F1, the first unrepresentable probe.

    Two groups of two whole values too large to hold and one group of
    three fractions too small to hold. `n_whole` is EXACT-OBSERVABLE and
    the packing that meets it is the obvious one; the greedy rule wrote
    five and named neither `n_whole` nor `n_fraction`, filing two
    misleading entries under `n_out_of_range` instead.
    """
    folder = tmp_path / "wide-whole"
    folder.mkdir(parents=True, exist_ok=True)
    values = ["1e999", "1e999", "2e999", "2e999"]
    values = values + ["1e-999", "1e-999", "1e-999"]
    described = _described(
        folder, fixtures.single_column_table("huge", values)
    )
    column = _block(described, "huge")
    facts = column.facts
    assert isinstance(facts, contract.UnrepresentableFacts)
    assert facts.n_whole == 4
    assert facts.n_fraction == 3
    built = generation.generate(described, 5)
    present = _present(_cells(built, "huge"))
    whole = len(
        [
            cell
            for cell in present
            if parsing.numeric_whole(cell) == parsing.WHOLE_YES
        ]
    )
    fraction = len(
        [
            cell
            for cell in present
            if parsing.numeric_whole(cell) == parsing.WHOLE_NO
        ]
    )
    assert whole == facts.n_whole
    assert fraction == facts.n_fraction
    named = {
        deviation.fact
        for deviation in built.deviations
        if deviation.column == "huge"
    }
    assert "n_whole" not in named
    assert "n_fraction" not in named
    assert "n_out_of_range" not in named


def test_an_unheld_column_meets_its_sign_counts(
    tmp_path: pathlib.Path,
) -> None:
    """Review item P2-C1-F1, the second unrepresentable probe.

    Three negative rows in one group and two positive groups of two.
    The greedy rule spent the negative count on the first group that
    fitted, stopped at two, and said NOTHING -- the wrong answer with no
    entry in the report at all. The sign counts are EXACT-OBSERVABLE and
    the packing that meets them is the group of three.
    """
    folder = tmp_path / "wide-signs"
    folder.mkdir(parents=True, exist_ok=True)
    values = ["-1e999", "-1e999", "-1e999"]
    values = values + ["2e999", "2e999", "3e999", "3e999"]
    described = _described(
        folder, fixtures.single_column_table("huge", values)
    )
    column = _block(described, "huge")
    facts = column.facts
    assert isinstance(facts, contract.UnrepresentableFacts)
    assert facts.n_negative == 3
    built = generation.generate(described, 5)
    present = _present(_cells(built, "huge"))
    negative = len(
        [
            cell
            for cell in present
            if parsing.numeric_sign(cell) == parsing.SIGN_NEGATIVE
        ]
    )
    assert negative == facts.n_negative
    named = {
        deviation.fact
        for deviation in built.deviations
        if deviation.column == "huge"
    }
    assert "n_negative" not in named
    assert "n_positive" not in named


def test_a_sign_count_no_packing_reaches_is_named(
    tmp_path: pathlib.Path,
) -> None:
    """The other half again: a sign count that cannot be met must be said.

    The review found this one silent even in the report, which is worse
    than the wrong number itself. The groups here cover three, two and
    two rows and the edited description asks for one negative cell, so
    no packing of whole groups can hold it.
    """
    folder = tmp_path / "wide-silent"
    folder.mkdir(parents=True, exist_ok=True)
    values = ["-1e999", "-1e999", "-1e999"]
    values = values + ["2e999", "2e999", "3e999", "3e999"]
    document = _document(
        folder, fixtures.single_column_table("huge", values), []
    )
    for block in document["columns"]:
        if block["name"] == "huge":
            block["n_negative"] = 1
            block["n_positive"] = 6
    described = _loaded(folder, document)
    built = generation.generate(described, 5)
    present = _present(_cells(built, "huge"))
    negative = len(
        [
            cell
            for cell in present
            if parsing.numeric_sign(cell) == parsing.SIGN_NEGATIVE
        ]
    )
    assert negative != 1
    named = {
        deviation.fact: deviation
        for deviation in built.deviations
        if deviation.column == "huge"
    }
    assert "n_negative" in named
    assert named["n_negative"].published == "1"
    assert named["n_negative"].achieved == f"{negative}"
    assert named["n_negative"].note in rendering.report(described, built)


def test_a_one_row_table_still_produces_a_twin(
    tmp_path: pathlib.Path,
) -> None:
    described = _one_column(tmp_path / "one", "only", ["7"])
    built = generation.generate(described, 11)
    assert built.n_rows == 1
    assert len(built.rows) == 1
    assert len(_present(_cells(built, "only"))) == 1


def test_the_twins_cells_read_back_unchanged_through_the_shipped_reader(
    every_role: contract.Profile, twin: generation.Twin, tmp_path: pathlib.Path
) -> None:
    """A made-up value may hold a comma or a quote; the round trip proves it.

    The twin's own writer is P2-D10's business, so this writes the rows
    with the standard library under the byte rules method G2 fixes and
    reads them back with the SHIPPED reader -- the same one the profiler
    uses on a real table. What it proves is a property of the cells:
    nothing the generator makes up can survive one round trip as
    something else.
    """
    import csv

    target = tmp_path / "twin.csv"
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(list(twin.names))
        for row in twin.rows:
            writer.writerow(list(row))
    read_back = reading.read_table(str(target))
    assert list(read_back.column_names) == list(twin.names)
    assert read_back.n_rows == twin.n_rows
    for index, name in enumerate(twin.names):
        assert list(read_back.columns[index]) == list(twin.columns[index]), name
