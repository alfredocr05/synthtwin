"""P1-R8-F2: the numeric-sentinel rule asks the EXACT number too.

Round 7 made the declaration comparison exact, so `--keep-value` and
`--missing-value` tell two decimal spellings apart even when both round
to one binary64 value. The numeric-sentinel rule kept asking the rounded
question, and the two then disagreed about what a cell holds:

* a column of readings plus fifteen copies of `-999.00000000000001` --
  a number distinct from `-999`, sharing its binary64 value -- reported
  a candidate of `-999` in fifteen rows, called it a stand-in for "no
  value", and deleted all fifteen. Typing that exact spelling after
  `--keep-value` changed nothing: the person's instruction reached the
  ordinary path, and the sentinel path removed the rows anyway. The
  published distribution then described a table the person did not have.

The rule now asks the exact question at every step: which candidate a
column holds, how many rows hold it, which numbers the rest of the
column is judged against, and which cells are taken out. All three
numeric sentinels are checked here, in both directions, because the
defect was in shared machinery and not in one constant.

Everything goes through `cli.main` with the words a person would type,
except the unit checks at the end, which pin the premise each case
rests on.
"""

import json
import pathlib

import pytest

import fixtures
from synthtwin import parsing, taxonomy
from synthtwin.cli import main

# One row per numeric sentinel: the sentinel as a person writes it, a
# decimal spelling that denotes a DIFFERENT number while rounding to the
# same binary64 value, and a second spelling of the sentinel itself.
# `test_the_premise_of_every_case_above` pins all three properties.
NEIGHBOURS = [
    ("-9999", "-9999.0000000000001", "-9.999e3"),
    ("-999", "-999.00000000000001", "-9.99e2"),
    ("9999", "9999.0000000000001", "9.999e3"),
]

# The reviewer's column: rows 1 through 199, an ordinary population with
# nothing unusual in it.
READINGS = [f"{index}" for index in range(1, 200)]

# The floor a candidate must reach before the profile names it, and the
# number of copies every case below uses, which clears it.
COPIES = 15


def _written(tmp_path: pathlib.Path, name: str, values: list[str]) -> str:
    """One column on disk, and its path as a person would type it."""
    text = fixtures.single_column_table(name, values)
    return f"{fixtures.write(tmp_path, f'{name}.csv', text)}"


def _kept(spelling: str) -> str:
    """`--keep-value` and its value as one word.

    Joined with `=` so that a spelling opening with a minus sign reaches
    the option whatever the command-line parser makes of a leading `-`.
    """
    return f"--keep-value={spelling}"


def _missing(spelling: str) -> str:
    """`--missing-value` and its value as one word, for the same reason."""
    return f"--missing-value={spelling}"


def _run(
    tmp_path: pathlib.Path,
    values: list[str],
    options: list[str],
    capsys: pytest.CaptureFixture[str],
) -> dict:
    """Profile one column through the command; return its block."""
    table = _written(tmp_path, "reading", values)
    assert main(["profile", table] + options) == 0, capsys.readouterr().err
    capsys.readouterr()
    document = json.loads(
        (tmp_path / "reading-profile.json").read_text(encoding="utf-8")
    )
    column = document["columns"][0]
    assert isinstance(column, dict)
    return column


def _verdict_for(column: dict, candidate: str) -> dict:
    """The published verdict about one candidate, or an empty one."""
    for entry in column["sentinel_verdicts"]:
        if entry["candidate"] == candidate:
            assert isinstance(entry, dict)
            return entry
    return {}


# -- the item's own reproduction, for each sentinel -------------------


@pytest.mark.parametrize(("sentinel", "neighbour", "again"), NEIGHBOURS)
def test_a_kept_neighbour_of_a_sentinel_survives_the_sentinel_rule(
    sentinel: str,
    neighbour: str,
    again: str,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The reviewer's reproduction. Fifteen rows hold a number that is
    # not the sentinel, and the person named that exact spelling as
    # data. Before the repair the column came back with 199 present,
    # fifteen counted as `(numeric-sentinel)`, a verdict naming a
    # candidate the column never held, and a minimum of 1.0.
    values = READINGS + [neighbour] * COPIES
    column = _run(tmp_path, values, [_kept(neighbour)], capsys)
    assert column["n_missing"] == 0, (
        "not one of these rows holds the sentinel, and the person named "
        "the number they do hold as data"
    )
    assert column["n_present"] == len(READINGS) + COPIES
    assert column["missing_by_class"][parsing.MISSING_NUMERIC_SENTINEL] == 0
    assert column["sentinel_verdicts"] == [], (
        "the column holds no sentinel, so there is no candidate to judge"
    )
    reached = parsing.parse_number(neighbour)
    assert reached is not None
    extreme = "min" if reached < 0 else "max"
    assert column["percentiles"][extreme] == reached, (
        "the fifteen kept rows have to reach the published distribution"
    )


@pytest.mark.parametrize(("sentinel", "neighbour", "again"), NEIGHBOURS)
def test_the_neighbour_is_not_removed_even_when_nobody_named_it(
    sentinel: str,
    neighbour: str,
    again: str,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The same column with no declaration at all. A number that merely
    # rounds to a sentinel was never one of the three spellings the
    # tool documents as stand-ins for "no value", so nothing here
    # depends on the person having noticed the problem in time.
    values = READINGS + [neighbour] * COPIES
    column = _run(tmp_path, values, [], capsys)
    assert column["n_missing"] == 0
    assert column["n_present"] == len(READINGS) + COPIES
    assert column["sentinel_verdicts"] == []


# -- the two numbers side by side, in both directions -----------------


@pytest.mark.parametrize(("sentinel", "neighbour", "again"), NEIGHBOURS)
def test_only_the_sentinel_rows_are_counted_and_removed(
    sentinel: str,
    neighbour: str,
    again: str,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Both numbers in one column, fifteen rows each, and the neighbour
    # named as data. The candidate is judged and removed, and the count
    # it publishes is the sentinel's fifteen rows and not thirty: the
    # occurrence count, the removal and the published verdict all have
    # to draw the line in the same place.
    values = READINGS + [sentinel] * COPIES + [neighbour] * COPIES
    column = _run(tmp_path, values, [_kept(neighbour)], capsys)
    assert column["n_missing"] == COPIES
    assert column["n_present"] == len(READINGS) + COPIES
    assert column["missing_by_class"][parsing.MISSING_NUMERIC_SENTINEL] == (
        COPIES
    )
    verdict = _verdict_for(column, sentinel)
    assert verdict["verdict"] == taxonomy.VERDICT_MISSING
    assert verdict["n_occurrences"] == COPIES, (
        "the neighbour's rows are not rows of the candidate"
    )


@pytest.mark.parametrize(("sentinel", "neighbour", "again"), NEIGHBOURS)
def test_keeping_the_sentinel_keeps_the_sentinel_and_not_the_neighbour_too(
    sentinel: str,
    neighbour: str,
    again: str,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The mirror of the case above: the person names the SENTINEL as
    # data, and both sets of rows stay -- the sentinel because it was
    # named, the neighbour because it was never a candidate. Thirty
    # rows survive, and the verdict says which of them was a decision.
    values = READINGS + [sentinel] * COPIES + [neighbour] * COPIES
    column = _run(tmp_path, values, [_kept(sentinel)], capsys)
    assert column["n_missing"] == 0
    assert column["n_present"] == len(READINGS) + 2 * COPIES
    verdict = _verdict_for(column, sentinel)
    assert verdict["verdict"] == taxonomy.VERDICT_KEPT
    assert verdict["reason"] == taxonomy.REASON_KEPT_BY_USER
    assert verdict["n_occurrences"] == COPIES


@pytest.mark.parametrize(("sentinel", "neighbour", "again"), NEIGHBOURS)
def test_declaring_the_neighbour_missing_takes_the_neighbour_rows(
    sentinel: str,
    neighbour: str,
    again: str,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The missing direction. The neighbour's fifteen rows go because
    # the person said so; the sentinel's fifteen go separately, as the
    # sentinel rule's own decision, and the two are counted under two
    # different words so the person can see which rule took what.
    values = READINGS + [sentinel] * COPIES + [neighbour] * COPIES
    column = _run(tmp_path, values, [_missing(neighbour)], capsys)
    assert column["n_present"] == len(READINGS)
    by_class = column["missing_by_class"]
    assert by_class[parsing.MISSING_DECLARED] == COPIES
    assert by_class[parsing.MISSING_NUMERIC_SENTINEL] == COPIES
    verdict = _verdict_for(column, sentinel)
    assert verdict["n_occurrences"] == COPIES


@pytest.mark.parametrize(("sentinel", "neighbour", "again"), NEIGHBOURS)
def test_declaring_the_sentinel_missing_leaves_the_neighbour_alone(
    sentinel: str,
    neighbour: str,
    again: str,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The other missing direction, and the one that would lose data
    # quietly: the person declares the sentinel, and the fifteen rows
    # holding a different number stay. With the sentinel's rows gone
    # there is no candidate left, so nothing is judged afterwards.
    values = READINGS + [sentinel] * COPIES + [neighbour] * COPIES
    column = _run(tmp_path, values, [_missing(sentinel)], capsys)
    assert column["n_present"] == len(READINGS) + COPIES
    by_class = column["missing_by_class"]
    assert by_class[parsing.MISSING_DECLARED] == COPIES
    assert by_class[parsing.MISSING_NUMERIC_SENTINEL] == 0
    assert column["sentinel_verdicts"] == []


# -- the reference population -----------------------------------------


@pytest.mark.parametrize(("sentinel", "neighbour", "again"), NEIGHBOURS)
def test_a_neighbour_counts_as_one_of_the_other_numbers(
    sentinel: str,
    neighbour: str,
    again: str,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The candidate is judged against every number that is not a
    # candidate, and a number that merely rounds to one is not a
    # candidate. Three plain readings plus the neighbour is four other
    # numbers, which is the fewest the rule will judge against; while
    # the neighbour was mistaken for the candidate there were three,
    # and the rule declined to judge at all.
    values = ["1", "2", "3", neighbour] + [sentinel] * COPIES
    column = _run(tmp_path, values, [], capsys)
    verdict = _verdict_for(column, sentinel)
    assert verdict != {}, "the sentinel is present, so it is a candidate"
    assert verdict["n_occurrences"] == COPIES
    assert verdict["reason"] != taxonomy.REASON_TOO_FEW_OTHERS, (
        "the neighbour is an ordinary number and belongs in the "
        "population the candidate is judged against"
    )
    assert verdict["reason"] == taxonomy.REASON_NOT_AN_OUTLIER
    assert column["n_present"] == 4 + COPIES


# -- distinct versus equivalent declarations --------------------------


@pytest.mark.parametrize(("sentinel", "neighbour", "again"), NEIGHBOURS)
def test_the_two_numbers_may_be_declared_opposite_ways(
    sentinel: str,
    neighbour: str,
    again: str,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Two different numbers, two opposite instructions, and no
    # contradiction: the sentinel's rows stay because they were named,
    # the neighbour's go because they were named.
    values = READINGS + [sentinel] * COPIES + [neighbour] * COPIES
    column = _run(
        tmp_path, values, [_kept(sentinel), _missing(neighbour)], capsys
    )
    assert column["n_present"] == len(READINGS) + COPIES
    assert column["missing_by_class"][parsing.MISSING_DECLARED] == COPIES
    assert column["missing_by_class"][parsing.MISSING_NUMERIC_SENTINEL] == 0
    verdict = _verdict_for(column, sentinel)
    assert verdict["reason"] == taxonomy.REASON_KEPT_BY_USER


@pytest.mark.parametrize(("sentinel", "neighbour", "again"), NEIGHBOURS)
def test_the_same_number_declared_both_ways_is_still_refused(
    sentinel: str,
    neighbour: str,
    again: str,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # What round 6 established and this repair must not undo: two
    # spellings of ONE number, named as data and as "no value", is a
    # pair no order of precedence can resolve. Still refused, still
    # said in words, still nothing written.
    table = _written(tmp_path, "reading", READINGS + [sentinel] * COPIES)
    assert main(["profile", table, _kept(sentinel), _missing(again)]) == 2
    told = capsys.readouterr().err
    assert "contradict each other" in told
    assert not (tmp_path / "reading-profile.json").exists()


@pytest.mark.parametrize(("sentinel", "neighbour", "again"), NEIGHBOURS)
def test_the_library_tells_the_distinct_pair_from_the_equivalent_one(
    sentinel: str, neighbour: str, again: str
) -> None:
    assert taxonomy.contradictory_declarations((sentinel,), (neighbour,)) == []
    assert taxonomy.contradictory_declarations((neighbour,), (sentinel,)) == []
    assert len(taxonomy.contradictory_declarations((sentinel,), (again,))) == 1
    assert len(taxonomy.contradictory_declarations((again,), (sentinel,))) == 1


@pytest.mark.parametrize(("sentinel", "neighbour", "again"), NEIGHBOURS)
def test_another_spelling_of_the_sentinel_still_keeps_it(
    sentinel: str,
    neighbour: str,
    again: str,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The other half of "exact": two spellings of ONE number still match
    # each other, so `--keep-value -9.99e2` still keeps a file's `-999`.
    # An exact comparison that also stopped matching equivalent
    # spellings would be a different defect, not a repair.
    values = READINGS + [sentinel] * COPIES
    column = _run(tmp_path, values, [_kept(again)], capsys)
    assert column["n_missing"] == 0
    verdict = _verdict_for(column, sentinel)
    assert verdict["reason"] == taxonomy.REASON_KEPT_BY_USER


# -- the premise each case above rests on ------------------------------


@pytest.mark.parametrize(("sentinel", "neighbour", "again"), NEIGHBOURS)
def test_the_premise_of_every_case_above(
    sentinel: str, neighbour: str, again: str
) -> None:
    # These cases are only about anything while the neighbour is a
    # number this format can hold, denotes a number the sentinel does
    # not, and rounds to the sentinel's own binary64 value. If any of
    # the three ever stops being true, the cases above pass without
    # testing what they were written for.
    held = parsing.parse_number(sentinel)
    assert held in parsing.NUMERIC_SENTINELS
    assert parsing.classify_number(neighbour) == parsing.NUMBER
    assert parsing.parse_number(neighbour) == held
    assert taxonomy.exact_of_spelling(neighbour) != taxonomy.exact_of_spelling(sentinel)
    assert taxonomy.exact_of_spelling(again) == taxonomy.exact_of_spelling(sentinel)
    assert held is not None
    assert taxonomy.exact_of_number(held) == taxonomy.exact_of_spelling(sentinel)


def test_every_numeric_sentinel_has_a_case_here() -> None:
    # The defect was in machinery all three sentinels share, so a
    # sentinel added later must arrive with its own neighbour rather
    # than inherit a repair nothing checks for it.
    named = [parsing.parse_number(row[0]) for row in NEIGHBOURS]
    assert sorted(named) == sorted(parsing.NUMERIC_SENTINELS)
