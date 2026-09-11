"""The ordinal space is the method's own, for every resolution (V3.4).

REVIEW ITEM P3-V3-F4. A description publishing twelve quarters from
`2018-Q1` to `2024-Q4` was measured against a twelve-row file holding
five `2018-Q1`, two `2021-Q3` and five `2024-Q4`, and the run reported
22 HELD, 11 WITHHELD, 0 MISSED and exited 0 under "no checkable
obligation was missed". The eleven silenced obligations were both
distinctness counts and all nine interior ladder rungs, and the file was
wrong about every one of them.

WHAT WAS ACTUALLY WRONG, because the witness is not the class. Method
G7.1 fixes one ordinal unit per resolution -- one second for a date and
time, one day for a date, one quarter for a quarter -- and G12.4 and
G12.5 draw their windows in that space, saying in as many words that a
quarter cell carries its own unit exactly. The obligations were
therefore set, and the validator could not see them: it read every
instant through `parsing.instant_key`, which returns nothing for a
quarter by design, and turned that into a WITHHELD verdict. A
measurement the validator cannot take is not a fact the file's own
description withholds, and dressing one as the other is how eleven
obligations went silent on every file at once.

SO THIS FILE ASSERTS THE CLASS AND NOT THE WITNESS, in three parts:

* EVERY RESOLUTION THE TAXONOMY PUBLISHES has a fixture here, walked
  from `taxonomy.RESOLUTIONS` rather than written out, so a fourth
  resolution added to the producer arrives with no fixture and this
  file says so on the commit that adds it;
* A TWIN OF ITS OWN DESCRIPTION, at every one of them, misses nothing
  and withholds nothing (V8.4's green direction, per resolution). A
  resolution the validator cannot measure shows up here as a
  withholding on a conforming twin;
* THE TWO WRITINGS OF THE ORDINAL SPACE AGREE. The validator may not
  import the generator (V1.4), so the method's table is written twice
  from the method -- the same arrangement V4.2 makes for the corner
  classifier -- and a test that may import both compares them.

Every table is built at test time by the seeded neutral builders in
`fixtures.py`; no data-format file enters the repository (plan D13).
"""

import pathlib

import pytest

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

SEED = 20260814

# The eleven obligations the finding silenced, named here so a repair
# that quietly drops one of them cannot pass by measuring the other ten.
_SILENCED = (
    "distinct.n_distinct",
    "distinct.n_distinct_folded",
    "date-ladder.p01",
    "date-ladder.p05",
    "date-ladder.p10",
    "date-ladder.p25",
    "date-ladder.p50",
    "date-ladder.p75",
    "date-ladder.p90",
    "date-ladder.p95",
    "date-ladder.p99",
)


def _quarter_values(count: int) -> "list[str]":
    """Quarters spread over seven years, lopsided toward the early ones."""
    values = []
    for index in range(count):
        year = 2018 + (index * index) % 7
        values = values + [f"{year}-Q{(index % 4) + 1}"]
    return sorted(values)


def _month_values(count: int) -> "list[str]":
    """Months over seven years, lopsided the same way as the quarters.

    A month is the second span the producer publishes -- it names a
    stretch of days rather than one instant -- so it needs its own
    ordinal space for exactly the reason the quarter needed one, and
    this is the fixture that shows the validator reads it there.
    """
    values = []
    for index in range(count):
        year = 2018 + (index * index) % 7
        values = values + [f"{year}-{(index % 12) + 1:02d}"]
    return sorted(values)


def _date_values(count: int) -> "list[str]":
    """Whole dates over one year, lopsided the same way."""
    values = []
    for index in range(count):
        month = (index * index) % 12 + 1
        values = values + [f"2024-{month:02d}-{(index % 27) + 1:02d}"]
    return sorted(values)


def _datetime_values(count: int) -> "list[str]":
    """Dates and times, so the third ordinal unit is reached too."""
    values = []
    for index in range(count):
        month = (index * index) % 12 + 1
        day = f"{(index % 27) + 1:02d}"
        clock = f"{(index * 7) % 24:02d}:{(index * 13) % 60:02d}:00"
        values = values + [f"2024-{month:02d}-{day} {clock}"]
    return sorted(values)


# One builder per resolution the producer can publish. The mapping is
# checked against `taxonomy.RESOLUTIONS` below rather than trusted.
_BUILDERS = {
    taxonomy.RESOLUTION_QUARTER: _quarter_values,
    taxonomy.RESOLUTION_MONTH: _month_values,
    taxonomy.RESOLUTION_DATE: _date_values,
    taxonomy.RESOLUTION_DATETIME: _datetime_values,
}


def _described(
    folder: pathlib.Path, values: "list[str]", stem: str
) -> contract.Profile:
    """One column of instants through the real producer and loader."""
    text = fixtures.single_column_table("when", values)
    table_path = fixtures.write(folder, f"{stem}.csv", text)
    table = reading.read_table(
        str(table_path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(table, taxonomy.Settings(), [])
    written = fixtures.write_profile(folder, f"{stem}-profile.json", document)
    return contract.load_profile(str(written))


def _measure(
    folder: pathlib.Path, described: contract.Profile, text: str, name: str
) -> validation.Outcome:
    """Write a measured file and measure it against a description."""
    target = folder / name
    target.write_text(text, encoding="utf-8", newline="\n")
    return validation.measure(described, str(target))


@pytest.fixture(scope="module")
def by_resolution(
    tmp_path_factory: pytest.TempPathFactory,
) -> "dict[str, tuple[contract.Profile, str]]":
    """One description and its twin for each resolution, built once."""
    folder = tmp_path_factory.mktemp("ordinal-spaces")
    built: dict[str, tuple[contract.Profile, str]] = {}
    for resolution in taxonomy.RESOLUTIONS:
        described = _described(
            folder, _BUILDERS[resolution](240), f"{resolution}s"
        )
        facts = described.columns[0].facts
        assert isinstance(facts, contract.DatetimeFacts), resolution
        assert facts.resolution == resolution, (
            f"the {resolution} fixture describes as {facts.resolution}, so "
            f"it is not measuring what its name says"
        )
        built[resolution] = (
            described,
            rendering.twin_csv(generation.generate(described, SEED)),
        )
    return built


def test_every_resolution_the_producer_publishes_has_a_fixture() -> None:
    """The walk is over the taxonomy's own list, not over a written one.

    A fourth resolution added to the producer would otherwise arrive
    with every test below still green and nothing measuring it -- which
    is exactly how quarters reached a shipped validator that could not
    read one.
    """
    missing = [
        resolution
        for resolution in taxonomy.RESOLUTIONS
        if resolution not in _BUILDERS
    ]
    assert not missing, (
        "these resolutions the producer can publish have no fixture "
        "here, so nothing in this suite shows the validator can measure "
        f"a column of them: {missing}"
    )


def test_a_twin_of_its_own_description_is_measured_at_every_resolution(
    tmp_path: pathlib.Path,
    by_resolution: "dict[str, tuple[contract.Profile, str]]",
) -> None:
    """V8.4's green direction, taken per resolution.

    THIS IS THE ASSERTION THE FINDING BROKE. Zero WITHHELD is what says
    the validator can take every measurement the description sets: a
    resolution it cannot read produces a conforming twin whose own
    obligations are silenced, and eleven of them were.
    """
    for resolution in sorted(by_resolution):
        described, twin = by_resolution[resolution]
        outcome = _measure(tmp_path, described, twin, f"{resolution}.csv")
        silenced = [
            check.subcheck
            for check in outcome.checks
            if check.verdict == validation.WITHHELD
        ]
        assert not silenced, (
            f"a conforming twin of a column of {resolution}s has these "
            f"obligations silenced, so nothing in the file could have "
            f"missed them: {sorted(set(silenced))}"
        )
        missed = [
            check.subcheck
            for check in outcome.checks
            if check.verdict == validation.MISSED
        ]
        assert not missed, f"{resolution}: {sorted(set(missed))}"
        filed = {check.subcheck for check in outcome.checks}
        for subcheck in _SILENCED:
            assert subcheck in filed, (
                f"{resolution}: {subcheck} is filed by no check at all, so "
                f"the obligation is not silenced -- it is gone"
            )


def test_the_finding_s_own_witness_is_now_told_the_truth(
    tmp_path: pathlib.Path,
) -> None:
    """The reviewer's file, measured (review item P3-V3-F4).

    Twelve distinct quarters published from `2018-Q1` to `2024-Q4`,
    against a twelve-row file holding three of them. Both ENDS of the
    file are right, and everything between them is wrong -- so what has
    to catch it is exactly the eleven obligations that were withheld:
    the nine rungs between the ends and the two counts of how many
    different values the column holds.
    """
    folder = tmp_path / "witness"
    folder.mkdir()
    published = [
        "2018-Q1",
        "2018-Q4",
        "2019-Q2",
        "2019-Q4",
        "2020-Q2",
        "2020-Q4",
        "2021-Q2",
        "2021-Q3",
        "2022-Q1",
        "2022-Q4",
        "2023-Q3",
        "2024-Q4",
    ]
    described = _described(folder, published, "witness")
    assert described.columns[0].n_distinct == 12
    held = ["2018-Q1"] * 5 + ["2021-Q3"] * 2 + ["2024-Q4"] * 5
    outcome = _measure(
        folder,
        described,
        fixtures.single_column_table("when", held),
        "measured.csv",
    )
    assert outcome.census.withheld == 0
    assert outcome.census.missed > 0, (
        "the file holds three of the twelve published quarters and the "
        "report calls nothing missed, so it exits 0 and prints the pass "
        "conclusion"
    )
    verdicts = {check.subcheck: check.verdict for check in outcome.checks}
    for subcheck in ("distinct.n_distinct", "distinct.n_distinct_folded"):
        assert verdicts[subcheck] == validation.MISSED, subcheck
    missed_rungs = [
        subcheck
        for subcheck in _SILENCED
        if subcheck.startswith("date-ladder.")
        and verdicts[subcheck] == validation.MISSED
    ]
    assert len(missed_rungs) >= 5, (
        "the file piles its twelve rows onto three quarters, and this "
        f"many of the nine rungs between the ends saw it: {missed_rungs}"
    )
    # ...and the two ENDS are right, so the nine did the catching rather
    # than riding on a neighbour that was going to miss anyway (V8.2).
    assert verdicts["ends.earliest"] == validation.HELD
    assert verdicts["ends.latest"] == validation.HELD
    assert verdicts["date-ladder.min"] == validation.HELD
    assert verdicts["date-ladder.max"] == validation.HELD


def test_the_two_writings_of_the_ordinal_space_agree(
    by_resolution: "dict[str, tuple[contract.Profile, str]]",
) -> None:
    """V1.4 and V4.2: the method's table, written twice, compared once.

    The validator may not import the generator, so method G7.1's ordinal
    table is written in both modules from the method's own words. A
    shared design error then needs the same mistake written twice; a
    DRIFT between them is what this catches, and it is checked where
    both may be imported, which is here and nowhere in `src`.

    WHAT "AGREE" MEANS HERE, stated because the two do not print the
    same number for a whole date. The generator counts a date in DAYS
    and the validator counts it in the SECONDS its own reading of an
    instant already speaks, so the two spaces are the same space counted
    in a different unit. The assertion is therefore that one factor, a
    whole number of the validator's units to the generator's one, holds
    for EVERY moment of the resolution: same order, same proportions, no
    rung anywhere the two put differently. A drift in either writing
    breaks the factor at the moment it touches.

    AND THE FACTOR DOES NOT MAKE THE WINDOWS AGREE BY ITSELF, which is
    what this docstring used to say and what review item P3-V4-F4 found
    to be false. "A window is a comparison of differences, so a constant
    positive unit cancels out of every one of them" is true of a
    subtraction and false of a FLOOR, and G7.3's interpolation floors:
    taken in seconds it lands part way through a day, taken in days it
    lands on the day the construction can write, and the two are up to a
    whole day apart. The windows themselves are compared against the
    generator's own, at every resolution and every precision, in
    `tests/test_p3v4f4_datetime_windows.py`; this test is about the
    space alone.
    """
    for resolution in sorted(by_resolution):
        described, _twin = by_resolution[resolution]
        facts = described.columns[0].facts
        assert isinstance(facts, contract.DatetimeFacts)
        moments = list(facts.date_percentiles.rungs) + [
            facts.earliest,
            facts.latest,
        ]
        base = facts.earliest
        theirs = generation._ordinal_of(facts.latest, resolution) - (
            generation._ordinal_of(base, resolution)
        )
        ours = validation._instant_of(facts.latest, resolution)
        low = validation._instant_of(base, resolution)
        assert ours is not None and low is not None
        assert theirs > 0, f"{resolution}: the fixture spans no time at all"
        factor, remainder = divmod(ours - low, theirs)
        assert remainder == 0 and factor >= 1, (
            f"{resolution}: the validator's span is not a whole multiple "
            f"of the method's, so the two are not the same space"
        )
        for moment in moments:
            mine = validation._instant_of(moment, resolution)
            assert mine is not None, f"{resolution}: {moment}"
            assert mine - low == factor * (
                generation._ordinal_of(moment, resolution)
                - generation._ordinal_of(base, resolution)
            ), f"{resolution}: {moment}"
        if resolution == taxonomy.RESOLUTION_QUARTER:
            # The one this finding added is written in the method's own
            # unit exactly, so here the two writings are the same number.
            assert factor == 1
            assert validation._instant_of(base, resolution) == (
                generation._ordinal_of(base, resolution)
            )


def test_the_quarter_space_is_the_method_s_arithmetic() -> None:
    """`4 * (year - 1970) + (n - 1)`, and nothing near it accepted.

    The two writings agree above; this is what each of them has to BE,
    so a pair that drifted the same way twice is still caught. The
    rejected forms are the ones a lenient reader would accept -- and
    accepting one would put a cell that is not a quarter into the
    quarter space, where its ordinal would be compared against a ladder
    of quarters.
    """
    assert validation._instant_of("1970-Q1", taxonomy.RESOLUTION_QUARTER) == 0
    assert validation._instant_of("1970-Q4", taxonomy.RESOLUTION_QUARTER) == 3
    assert validation._instant_of("1971-Q1", taxonomy.RESOLUTION_QUARTER) == 4
    assert validation._instant_of("1969-Q4", taxonomy.RESOLUTION_QUARTER) == -1
    assert (
        validation._instant_of("2024-Q4", taxonomy.RESOLUTION_QUARTER)
        == 4 * (2024 - 1970) + 3
    )
    for refused in (
        "",
        "2024-Q",
        "2024-Q0",
        "2024-Q5",
        "2024-QX",
        "2024-01-01",
        "0000-Q1",
        "20240-Q1",
        "202a-Q1",
        "2024/Q1",
        " 2024-Q1",
    ):
        assert (
            validation._instant_of(refused, taxonomy.RESOLUTION_QUARTER)
            is None
        ), refused


def test_the_month_space_is_the_method_s_arithmetic() -> None:
    """`12 * (year - 1970) + (MM - 1)`, and nothing near it accepted.

    The second SPAN resolution needs this for the quarter's reason,
    with one edge of its own: a month is written `YYYY-MM`, and so is
    the first seven characters of a whole date. A reader that took
    those seven and answered would put a cell that is a DAY into the
    month space, where its ordinal would be compared against a ladder
    of months.

    Year zero is refused here too. The contract's canonical form runs
    from `0001` up, and the two span readers accepted `0000` until the
    month made the hole visible (review item P4-DATE3-F4).
    """
    assert validation._instant_of("1970-01", taxonomy.RESOLUTION_MONTH) == 0
    assert validation._instant_of("1970-12", taxonomy.RESOLUTION_MONTH) == 11
    assert validation._instant_of("1971-01", taxonomy.RESOLUTION_MONTH) == 12
    assert validation._instant_of("1969-12", taxonomy.RESOLUTION_MONTH) == -1
    assert (
        validation._instant_of("2024-12", taxonomy.RESOLUTION_MONTH)
        == 12 * (2024 - 1970) + 11
    )
    for refused in (
        "",
        "2024-",
        "2024-00",
        "2024-13",
        "2024-1",
        "2024-XX",
        "2024-01-01",
        "20240-01",
        "202a-01",
        "2024/01",
        " 2024-01",
        "2024-Q1",
        "0000-01",
    ):
        assert (
            validation._instant_of(refused, taxonomy.RESOLUTION_MONTH) is None
        ), refused


def test_a_quarter_ladder_is_read_in_quarters_and_not_in_seconds(
    by_resolution: "dict[str, tuple[contract.Profile, str]]",
) -> None:
    """The unit and the step belong to the same space as the ordinals.

    A window drawn in quarters and a slack measured in seconds would
    admit every file there is, which is the other way an obligation goes
    quiet. One quarter is one unit and one step; a date is a whole day
    of seconds; a date and time written to the minute steps sixty.

    THE MINUTE ALLOWANCE IS THE METHOD'S, AND THIS TEST USED TO ASSERT
    THE CODE'S (review item P3-V4-F5). It read `unit == 119.0`, which is
    one STEP of the published precision plus fifty-nine seconds; G12.4's
    `u` is one unit of the ordinal SPACE -- one second for a column of
    dates and times, whatever its precision -- plus those fifty-nine, so
    the number is 60. No fixture in this file publishes minute
    precision, so the branch asserted nothing on any run; the fixtures
    that reach every precision, and the comparison with the generator's
    own writing of the same number, are in
    `tests/test_p3v4f4_datetime_windows.py`.
    """
    for resolution in sorted(by_resolution):
        described, _twin = by_resolution[resolution]
        facts = described.columns[0].facts
        assert isinstance(facts, contract.DatetimeFacts)
        unit = validation._reading_unit(facts)
        step = validation._precision_step(facts)
        if resolution == taxonomy.RESOLUTION_QUARTER:
            assert unit == 1 and step == 1
        elif resolution == taxonomy.RESOLUTION_DATE:
            assert unit == 86400 and step == 86400
        elif facts.time_precision == parsing.PRECISION_MINUTE:
            assert unit == 1 + 59 and step == 60
        else:
            assert unit == 1 and step == 1
