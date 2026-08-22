"""The datetime windows are the method's, written twice and compared.

REVIEW ITEMS P3-V4-F4 AND P3-V4-F5, which are one item: the validator's
reading of method G12.4's rank window diverged from the construction it
is checking, in three separate places, and each divergence produced a
verdict the generator contradicts.

* THE ENDS WERE NOT PINNED. G7.3 writes rank `0` at the published
  `earliest` and rank `P - 1` at the published `latest`, exactly as
  published, so those two ranks have no room at all; the validator gave
  them the interior band. G12.5's separateness walk then let the first
  window swallow ranks that cannot share its instant, and the review's
  twelve-rank quarterly description passed a file holding four different
  quarters where the construction forces five. The witness below is a
  description of the same shape rather than that one, whose published
  quarters the review does not record: it passes six where the
  construction forces seven, and the two numbers are the same finding.
* THE READING UNIT WAS 119 SECONDS WHERE THE METHOD SAYS 60. `u` is one
  unit of the ordinal space -- one SECOND for a column of dates and
  times, whatever its precision -- plus the fifty-nine seconds a cell
  written to the minute carries no room for. The validator read the
  first term as one step of the published precision and allowed most of
  an extra minute, so a rung that misses its window was reported WITHIN.
  The repair test of the previous round asserted 119 rather than the
  method's number, and no fixture in the suite published minute
  precision at all, so nothing could have said otherwise.
* AND THE LADDER WAS READ WITH FLOATING-POINT ARITHMETIC. G12.4 reads
  `Ladder_d` "by the same whole-number interpolation G7.3 builds cells
  with", and "no float is formed anywhere in G7" is the method's own
  sentence about that space. The validator used the piecewise-linear
  float reader the NUMERIC ladder uses, which is a different function:
  it sits above the method's floor by the fraction the floor discards,
  so a window's low end was up to one unit too high and a conforming
  twin could be reported MISSED at a rung. Nobody had found that one; it
  came out of writing the construction from the method instead of
  patching the two constants the review named.

SO WHAT IS ASSERTED HERE IS THE WRITING, NOT THE TWO NUMBERS. The
validator may not import the generator (V1.4), so method G12.4's window
is written in both modules from the method's own words and compared
here, where both may be imported -- exactly the arrangement V4.2 makes
for the corner classifier. The comparison is over EVERY resolution and
EVERY precision the producer can publish, walked from the producer's own
lists, and over a spread of column lengths, so the next divergence in
this area is caught by construction rather than by a reviewer.

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

# How many ranks the windows are compared over. One and two are the two
# shapes the pinning is a special case of -- a column with one rank has
# nothing but a pinned rank, and one with two has nothing but two -- and
# the rest are ordinary. A rank count the two writings disagree at is a
# rank count some description can reach.
_RANK_COUNTS = (1, 2, 3, 5, 12, 60, 239, 240)


def _subsecond(index: int) -> str:
    return (
        f"2024-{(index * index) % 12 + 1:02d}-{(index % 27) + 1:02d} "
        f"{(index * 7) % 24:02d}:{(index * 13) % 60:02d}:"
        f"{(index * 17) % 60:02d}.{(index * 3) % 10}00"
    )


def _second(index: int) -> str:
    return (
        f"2024-{(index * index) % 12 + 1:02d}-{(index % 27) + 1:02d} "
        f"{(index * 7) % 24:02d}:{(index * 13) % 60:02d}:"
        f"{(index * 17) % 60:02d}"
    )


def _minute(index: int) -> str:
    return (
        f"2024-{(index * index) % 12 + 1:02d}-{(index % 27) + 1:02d} "
        f"{(index * 7) % 24:02d}:{(index * 13) % 60:02d}"
    )


def _date(index: int) -> str:
    return f"2024-{(index * index) % 12 + 1:02d}-{(index % 27) + 1:02d}"


def _month(index: int) -> str:
    return f"{2018 + (index * index) % 7}-{(index % 12) + 1:02d}"


def _quarter(index: int) -> str:
    return f"{2018 + (index * index) % 7}-Q{(index % 4) + 1}"


# One builder per PRECISION the producer can publish, which is one per
# resolution for the three that carry no clock and three for the one
# that does. The mapping is checked against the producer's own list below
# rather than trusted.
_BUILDERS = {
    parsing.PRECISION_SUBSECOND: _subsecond,
    parsing.PRECISION_SECOND: _second,
    parsing.PRECISION_MINUTE: _minute,
    parsing.PRECISION_DATE: _date,
    parsing.PRECISION_MONTH: _month,
    parsing.PRECISION_QUARTER: _quarter,
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
    return validation.measure(
        described, str(fixtures.write(folder, name, text))
    )


@pytest.fixture(scope="module")
def by_precision(
    tmp_path_factory: pytest.TempPathFactory,
) -> "dict[str, tuple[contract.Profile, str]]":
    """One description and its twin for each precision, built once."""
    folder = tmp_path_factory.mktemp("datetime-windows")
    built: dict[str, tuple[contract.Profile, str]] = {}
    for precision in sorted(_BUILDERS):
        make = _BUILDERS[precision]
        values = sorted([make(index) for index in range(240)])
        described = _described(folder, values, f"{precision}s")
        facts = described.columns[0].facts
        assert isinstance(facts, contract.DatetimeFacts), precision
        assert facts.time_precision == precision, (
            f"the {precision} fixture describes as {facts.time_precision}, "
            f"so it is not measuring what its name says"
        )
        built[precision] = (
            described,
            rendering.twin_csv(generation.generate(described, SEED)),
        )
    return built


def _facts_of(described: contract.Profile) -> contract.DatetimeFacts:
    facts = described.columns[0].facts
    assert isinstance(facts, contract.DatetimeFacts)
    return facts


def _factor_of(facts: contract.DatetimeFacts) -> int:
    """How many of the validator's units go to one of the generator's.

    The two write the same space in different units -- the generator
    counts a whole date in DAYS, the validator in the seconds its own
    reading of an instant already speaks -- so the comparison is up to
    one constant factor, derived here rather than written out, and then
    asserted to hold of every moment rather than assumed of the span.
    """
    resolution = facts.resolution
    theirs = generation._ordinal_of(
        facts.latest, resolution
    ) - generation._ordinal_of(facts.earliest, resolution)
    mine = validation._ordinal_of(
        facts.latest, resolution
    ) - validation._ordinal_of(facts.earliest, resolution)
    assert theirs > 0, f"{resolution}: the fixture spans no time at all"
    factor, remainder = divmod(mine, theirs)
    assert remainder == 0 and factor >= 1, (
        f"{resolution}: the validator's span is not a whole multiple of "
        f"the method's, so the two are not the same space"
    )
    for moment in list(facts.date_percentiles.rungs) + [
        facts.earliest,
        facts.latest,
    ]:
        assert validation._ordinal_of(moment, resolution) == factor * (
            generation._ordinal_of(moment, resolution)
        ), f"{resolution}: {moment}"
    return factor


def test_every_precision_the_producer_publishes_has_a_fixture() -> None:
    """The walk is over the producer's own list, not over a written one.

    THE HOLE THE 119 LIVED IN. Every datetime fixture in this suite
    published `second`, `date` or `quarter` precision, so the one branch
    of `_reading_unit` that carries an allowance at all was reached by
    no test -- and the previous round's repair test asserted the number
    the code returned rather than the number the method fixes, with
    nothing to say otherwise. A precision added to the producer without
    a fixture here is red on the commit that adds it.
    """
    missing = [
        precision
        for precision in parsing.PRECISION_ORDER
        if precision not in _BUILDERS
    ]
    assert not missing, (
        "these precisions the producer can publish have no fixture here, "
        f"so nothing in this suite measures a column of them: {missing}"
    )


def test_the_ladder_is_the_eleven_percentages_the_method_writes() -> None:
    """G7.3's arithmetic is in percent, and the taxonomy's ladder is too.

    The interpolation multiplies each rung's percentage by the column's
    rank count, so a rung carried as a fraction of anything but a hundred
    would be read at the wrong place with nothing said. The producer's
    ladder is the authority; this asserts the two agree, so a ladder
    change lands here rather than inside a window.
    """
    assert len(validation._LADDER_PERCENTS) == len(taxonomy.LADDER)
    for percent, denominator in zip(
        validation._LADDER_PERCENTS,
        validation._LADDER_DENOMINATORS,
        strict=True,
    ):
        assert denominator == 100, (
            "a ladder rung is carried out of "
            f"{denominator} rather than out of a hundred, and G7.3's "
            "interpolation is written in whole percentages"
        )
        assert 0 <= percent <= 100
    assert validation._LADDER_PERCENTS == generation._PCT


@pytest.mark.parametrize("precision", sorted(_BUILDERS))
def test_the_two_writings_of_the_reading_unit_agree(
    precision: str,
    by_precision: "dict[str, tuple[contract.Profile, str]]",
) -> None:
    """G12.4's `u`, written twice (review item P3-V4-F5).

    The generator carries the two terms apart -- `_precision_slack` is
    the fifty-nine seconds, and the `+ 1` beside it is the one unit of
    the ordinal space -- so this compares the sum with the validator's
    own, in the validator's units. 119 fails here at `minute` and passes
    everywhere else, which is exactly the shape the finding had.
    """
    described, _twin = by_precision[precision]
    facts = _facts_of(described)
    factor = _factor_of(facts)
    theirs = factor * (generation._precision_slack(facts) + 1)
    assert validation._reading_unit(facts) == theirs, (
        f"{precision}: the validator allows "
        f"{validation._reading_unit(facts)} where the construction loses "
        f"at most {theirs}"
    )


@pytest.mark.parametrize("precision", sorted(_BUILDERS))
def test_the_two_writings_of_the_rank_window_agree(
    precision: str,
    by_precision: "dict[str, tuple[contract.Profile, str]]",
) -> None:
    """G12.4's whole window, rank by rank, over eight rank counts.

    THE ASSERTION THIS FILE EXISTS FOR. The pinning, the reading unit
    and the interpolation are all inside these two lists, so a
    divergence in any of them -- including one nobody has found yet --
    shows up as two numbers that differ at some rank of some count.
    """
    described, _twin = by_precision[precision]
    facts = _facts_of(described)
    factor = _factor_of(facts)
    ladder = [
        generation._ordinal_of(rung, facts.resolution)
        for rung in facts.date_percentiles.rungs
    ]
    for ranks in _RANK_COUNTS:
        lows, highs = validation._rank_windows(facts, ranks)
        their_lows, their_highs = generation._datetime_window(
            ladder, facts, ranks
        )
        assert len(lows) == ranks and len(highs) == ranks
        for rank in range(ranks):
            assert lows[rank] == factor * their_lows[rank], (
                f"{precision}, {ranks} ranks, rank {rank}: the validator "
                f"admits from {lows[rank]} where the construction cannot "
                f"go below {factor * their_lows[rank]}"
            )
            assert highs[rank] == factor * their_highs[rank], (
                f"{precision}, {ranks} ranks, rank {rank}: the validator "
                f"admits up to {highs[rank]} where the construction "
                f"cannot pass {factor * their_highs[rank]}"
            )


def test_the_two_writings_of_the_rung_rank_agree() -> None:
    """Which rank a published rung is read off, written twice.

    The generator's own selection is `min(held - 1, ((held - 1) * c) //
    100)` and the validator worked the same thing out through a
    floating-point share. Two whole-number expressions that agree on
    every case a description can reach are one rule; a float in the
    middle of one of them is a second rule waiting to disagree, so this
    walks every rank count a column can have up to the fixtures' own,
    the eight the windows are compared at.
    """
    for ranks in list(_RANK_COUNTS) + list(range(1, 241)):
        for percent in validation._LADDER_PERCENTS:
            theirs = min(ranks - 1, ((ranks - 1) * percent) // 100)
            assert validation._rung_rank(percent, ranks) == theirs, (
                f"{ranks} ranks at {percent} percent: "
                f"{validation._rung_rank(percent, ranks)} against {theirs}"
            )


@pytest.mark.parametrize("precision", sorted(_BUILDERS))
def test_the_two_writings_of_the_distinctness_envelope_agree(
    precision: str,
    by_precision: "dict[str, tuple[contract.Profile, str]]",
) -> None:
    """G12.5's two ends, written twice, on a conforming twin.

    The generator computes its ends over the twin it has just written
    and the validator over the description alone; on a twin that holds
    every cell the description asks for, with no stand-ins and no holes,
    the two are answering exactly the same question and must give
    exactly the same pair.
    """
    described, twin = by_precision[precision]
    _compare_the_envelopes(described, twin, precision)


def _compare_the_envelopes(
    described: contract.Profile, twin: str, label: str
) -> None:
    """The validator's envelope against the generator's, on a twin.

    THE LOWER END MUST BE EQUAL, always: it is G12.4's windows walked,
    and a difference there is a difference in the windows. THE UPPER END
    IS COMPARED AS AN INEQUALITY, and the one place the two readings
    differ is pinned rather than papered over -- see
    `validation._spellings_of_an_instant`: a cell G7.4 routes to `(none)`
    or `(withheld)` is written with NO offset, which is a spelling of
    its own, and G12.5's upper end counts the NAMED offsets alone. The
    validator takes the wider reading, because a bound one factor too
    tight is a bound a conforming twin can be reported MISSED against,
    and V3.5 forbids this document to narrow a cited envelope on its own.
    """
    column = described.columns[0]
    facts = _facts_of(described)
    assert facts.n_unparsed == 0 and column.n_missing == 0, (
        "this fixture holds holes or unreadable cells, so the two ends "
        "are not being asked the same question"
    )
    ladder = [
        generation._ordinal_of(rung, facts.resolution)
        for rung in facts.date_percentiles.rungs
    ]
    written = [
        line.split(",")[0] for line in twin.splitlines()[1:] if line
    ]
    lows, highs = generation._datetime_window(
        ladder, facts, len(written)
    )
    lowest = generation._forced_apart(lows, highs)
    reachable = ladder[10] - ladder[0] + 1
    unit = generation._precision_slack(facts) + 1
    reachable = (reachable + unit - 1) // unit
    spellings = generation._spellings_of_a_date(facts)
    highest = min(len(written), reachable * spellings)
    mine, my_highest = validation._datetime_distinct_window(column, facts)
    assert my_highest >= float(highest), (
        f"{label}: the validator's upper end is {my_highest} where the "
        f"construction can reach {highest}, so a twin the construction "
        f"admits can be reported MISSED"
    )
    if validation._spellings_of_an_instant(facts) == spellings:
        assert my_highest == float(highest), label
    assert mine == float(min(lowest, highest)) or mine == float(
        min(lowest, int(my_highest))
    ), (
        f"{label}: the validator forces {mine} ranks apart where the "
        f"construction forces {lowest}"
    )


def test_the_envelopes_agree_where_a_column_carries_offsets(
    tmp_path: pathlib.Path,
) -> None:
    """The same comparison on a column whose cells are spelled three ways.

    The five fixtures above carry no offset at all, so the factor G12.5
    multiplies its upper end by is one on every one of them and the two
    writings of it were compared nowhere. A column mixing two named
    offsets with cells that carry none reaches all three keys of G7.4,
    which is where the two readings differ.
    """
    folder = tmp_path / "offsets"
    folder.mkdir()
    values: list[str] = []
    for index in range(240):
        stamp = _second(index)
        if index % 3 == 0:
            values = values + [f"{stamp}+02:00"]
        elif index % 3 == 1:
            values = values + [f"{stamp}+00:00"]
        else:
            values = values + [stamp]
    described = _described(folder, sorted(values), "offsets")
    facts = _facts_of(described)
    assert sorted(facts.utc_offsets) == ["(none)", "+00:00", "+02:00"], (
        "the fixture stopped reaching all three keys of G7.4, so the "
        "comparison below is not the one this test is for"
    )
    assert validation._spellings_of_an_instant(facts) == 3
    assert generation._spellings_of_a_date(facts) == 2
    twin = rendering.twin_csv(generation.generate(described, SEED))
    _compare_the_envelopes(described, twin, "offsets")
    outcome = _measure(folder, described, twin, "offsets.csv")
    wrong = sorted(
        {
            f"{check.subcheck}: {check.verdict}"
            for check in outcome.checks
            if check.verdict in (validation.MISSED, validation.WITHHELD)
        }
    )
    assert not wrong, wrong


@pytest.mark.parametrize("precision", sorted(_BUILDERS))
def test_a_twin_of_its_own_description_misses_nothing(
    tmp_path: pathlib.Path,
    precision: str,
    by_precision: "dict[str, tuple[contract.Profile, str]]",
) -> None:
    """V8.4's green direction, taken per precision.

    A window drawn tighter than the construction is a validator that
    rejects conforming twins, which is the failure this whole class is
    made of -- so every tightening above is asserted against the file
    the generator writes as well as against the generator's own numbers.
    """
    described, twin = by_precision[precision]
    outcome = _measure(tmp_path, described, twin, f"{precision}.csv")
    wrong = sorted(
        {
            f"{check.subcheck}: {check.verdict}"
            for check in outcome.checks
            if check.verdict in (validation.MISSED, validation.WITHHELD)
        }
    )
    assert not wrong, f"{precision}: {wrong}"


def test_the_pinned_ends_force_more_different_values(
    tmp_path: pathlib.Path,
) -> None:
    """P3-V4-F4's own witness: a file inside the old bound and outside this one.

    A twelve-rank quarterly description, measured against twelve rows
    holding SIX different quarters, both ends of the published range
    among them. Rank zero is the published earliest and rank eleven the
    published latest, exactly, so the walk of G12.5 cannot put either of
    them on a neighbour's instant and the construction forces seven
    different instants. Unpinned, the same walk found six: the file was
    reported WITHIN its stated window at both distinctness counts, which
    is a file passing a bound its own construction cannot meet.
    """
    folder = tmp_path / "quarters"
    folder.mkdir()
    published = [
        "2018-Q2",
        "2019-Q2",
        "2020-Q4",
        "2021-Q3",
        "2022-Q2",
        "2022-Q4",
        "2024-Q2",
        "2026-Q2",
        "2028-Q1",
        "2028-Q4",
        "2029-Q1",
        "2032-Q2",
    ]
    described = _described(folder, published, "witness")
    column = described.columns[0]
    facts = _facts_of(described)
    assert column.n_present == 12 and column.n_distinct == 12
    low, _high = validation._datetime_distinct_window(column, facts)
    # The bound is the CONSTRUCTION's own, taken from the generator's
    # writing of the same walk rather than written out here, so this
    # says what the file is short of rather than what today's code says.
    ladder = [
        generation._ordinal_of(rung, facts.resolution)
        for rung in facts.date_percentiles.rungs
    ]
    lows, highs = generation._datetime_window(ladder, facts, 12)
    assert low == float(generation._forced_apart(lows, highs))
    held = (
        ["2018-Q2"] * 2
        + ["2020-Q4"] * 2
        + ["2022-Q2"] * 2
        + ["2024-Q2"] * 2
        + ["2028-Q1"] * 2
        + ["2032-Q2"] * 2
    )
    assert len(set(held)) < low, (
        "the witness file holds as many different quarters as the "
        "construction forces, so it is not short of the bound at all"
    )
    outcome = _measure(
        folder,
        described,
        fixtures.single_column_table("when", held),
        "measured.csv",
    )
    verdicts = {check.subcheck: check.verdict for check in outcome.checks}
    for subcheck in ("distinct.n_distinct", "distinct.n_distinct_folded"):
        assert verdicts[subcheck] == validation.MISSED, (
            f"the file holds {len(set(held))} different quarters where the "
            f"construction forces {low:.0f}, and {subcheck} is "
            f"{verdicts[subcheck]}"
        )
    # ...and both ENDS are right, so this is the bound doing the
    # catching and not a neighbour that was going to fail anyway (V8.2).
    assert verdicts["ends.earliest"] == validation.HELD
    assert verdicts["ends.latest"] == validation.HELD
    assert verdicts["date-ladder.min"] == validation.HELD
    assert verdicts["date-ladder.max"] == validation.HELD


def test_a_rung_that_misses_by_most_of_a_minute_is_missed(
    tmp_path: pathlib.Path,
) -> None:
    """P3-V4-F5's own witness: sixty minutes, and a p05 below the bound.

    Sixty sequential minutes give a ladder that is a straight run, so
    every rung's window is a known handful of seconds wide. The measured
    file holds three cells at the first minute, fifty-six at the second
    and one at the last: its fifth-percentile rung is a whole minute
    below the window its rank leaves, which one second of interpolation
    slack and fifty-nine seconds of writing cannot reach. The 119-second
    allowance reported it WITHIN.
    """
    folder = tmp_path / "minutes"
    folder.mkdir()
    published = [
        f"2024-03-01 {index // 60:02d}:{index % 60:02d}" for index in range(60)
    ]
    described = _described(folder, published, "minutes")
    facts = _facts_of(described)
    assert facts.time_precision == parsing.PRECISION_MINUTE
    held = (
        ["2024-03-01 00:00"] * 3
        + ["2024-03-01 00:01"] * 56
        + ["2024-03-01 00:59"]
    )
    outcome = _measure(
        folder,
        described,
        fixtures.single_column_table("when", held),
        "measured.csv",
    )
    verdicts = {check.subcheck: check.verdict for check in outcome.checks}
    assert verdicts["date-ladder.p05"] == validation.MISSED, (
        "the file's fifth-percentile rung sits a minute below the window "
        f"its rank leaves, and the report calls it {verdicts['date-ladder.p05']}"
    )
    # The two ends still hold, so the rung is answering for itself.
    assert verdicts["ends.earliest"] == validation.HELD
    assert verdicts["ends.latest"] == validation.HELD
    assert outcome.census.missed > 0
