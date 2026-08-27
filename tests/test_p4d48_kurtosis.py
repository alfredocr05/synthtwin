"""P4-D4.8: the weight of a column's tails, and what it must not cost.

The owner asked for the kurtosis on 2026-08-26 -- "one number, pairs
with skew" -- because it is what tells somebody whether outlier
handling will behave the same way on the twin as on the real table. It
is the MOMENT RATIO and not the excess, so a normal curve reads 3 here
and not 0, which is the convention `skew` beside it already uses.

**EVERY TEST BELOW IS A REVIEWER'S FINDING**, and the first is the one
that matters most: an adversarial round found that the validator
CRASHED on an ordinary column of a hundred values around 1e79, raising
`OverflowError` where a report was owed. The published statistic is
bounded -- a moment ratio lies between 1 and `n - 2 + 1/(n - 1)` for
any n values, so the row count bounds it -- and that argument was
right about the RESULT and said nothing about the way to it. Raising a
deviation to the fourth power and dividing afterwards is the same
number in exact arithmetic and not the same computation in binary64.
"""

import pathlib

import pytest

import fixtures
from synthtwin import contract, generation, taxonomy, validation


def _described(folder: pathlib.Path, values: "list[str]") -> contract.Profile:
    """One single-column table, through the real producer and loader."""
    text = "reading\n" + "\n".join(values) + "\n"
    table = fixtures.write(folder, "table.csv", text)
    from synthtwin import profile, reading

    document = profile.build_document(
        reading.read_table(str(table)), taxonomy.Settings(), []
    )
    return contract.load_profile(
        str(fixtures.write_profile(folder, "profile.json", document))
    )


def test_a_column_of_large_values_still_gets_a_report(
    tmp_path: pathlib.Path,
) -> None:
    """THE CRASH (review item P4-K-R1-F1), pinned on the reviewer's own column.

    A hundred values around 1e79 -- nothing exotic, nothing this format
    cannot hold, a finite spread and a kurtosis of about 1.8. The
    window's arithmetic raised each deviation to the fourth power
    BEFORE dividing by the spread, and the fourth power of 1e79 is not
    a number binary64 holds, so the validator raised `OverflowError`
    and wrote no report at all.

    A tool that refuses to describe a file it can describe is worse
    than one that describes it loosely, which is why this is the first
    test in the file.
    """
    from synthtwin import rendering

    described = _described(tmp_path, [f"{k}e78" for k in range(100)])
    assert described.columns[0].facts.kurtosis is not None
    twin = generation.generate(described, 5)
    measured = fixtures.write(
        tmp_path, "twin.csv", rendering.twin_csv(twin)
    )
    outcome = validation.measure(described, str(measured))
    assert outcome.checks, "the validator wrote no check at all"
    assert [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    ] == []


def test_the_window_is_never_the_wrong_way_round() -> None:
    """AN INVERTED WINDOW EXCLUDES ITS OWN STATISTIC (item P4-K-R1-F5).

    On the four-value extreme -- one value apart from three equal ones,
    where the kurtosis sits exactly on its own ceiling -- the two
    clamps can cross by one unit in the last place. A window whose low
    end is above its high end admits nothing, so it calls a correct
    twin wrong.

    Both implementations are checked, because they are two and a reader
    meets whichever one wrote the page in front of them.
    """
    ranks = [0.0, 0.0, 0.0, 1.0]
    published = 2.3333333333333335
    low, high = generation._tails_window(ranks, ranks, ranks, 0.0, 4)
    assert low <= high, (low, high)
    assert low <= published <= high
    windows = validation._moment_windows(ranks, ranks, ranks, 4)
    assert "kurtosis" in windows
    low, high = windows["kurtosis"]
    assert low <= high, (low, high)
    assert low <= published <= high


def test_the_two_implementations_draw_the_same_window() -> None:
    """THE GENERATOR AND THE VALIDATOR HAVE TO AGREE.

    A twin the generator calls inside its bound and the validator calls
    outside is the defect that matters most here: the twin's own report
    and its quality report would say opposite things about one number.
    """
    shapes = (
        [0.0, 1.0, 2.0, 3.0],
        [0.0, 0.0, 0.0, 1.0],
        [-5.0, -1.0, 1.0, 5.0, 40.0],
        [1e78, 2e78, 3e78, 4e78, 5e78],
    )
    for ranks in shapes:
        held = len(ranks)
        # EVERY REACH A RUN CAN ACTUALLY HAVE. A rank window always has
        # width -- the displacement bound of G12.2 plus the whole-number
        # slack -- so a reach of exactly zero is a case no run reaches.
        # At that value the two float paths do part company, by a few
        # units in the last place, and this test says so rather than
        # widening until it passes: from 1e-12 upward they agree.
        span = max(ranks) - min(ranks)
        for share in (1e-9, 1e-6, 0.001, 0.05, 0.2):
            # THE REACH SCALES WITH THE COLUMN, because the
            # displacement bound of G12.2 does: it is built from the
            # rank windows, which are ladder values. An absolute reach
            # of 1e-12 is a real width on a column of small numbers and
            # exactly zero on a column around 1e78.
            reach = span * share
            lows = [rank - reach for rank in ranks]
            highs = [rank + reach for rank in ranks]
            mine = generation._tails_window(lows, highs, ranks, reach, held)
            theirs = validation._moment_windows(lows, highs, ranks, held)
            assert "kurtosis" in theirs, (ranks, share)
            low, high = theirs["kurtosis"]
            # The two are computed by different code and need not agree
            # to the last bit; what they may not do is disagree about
            # whether a value is inside, so the OVERLAP is asserted.
            # At a reach of exactly zero both windows collapse onto
            # the statistic and part company by a few units in the last
            # place. Opening each end by one unit would have hidden
            # that and `math.nextafter` is not on the offline audit's
            # allowlist, which is a policy decision and not a routine
            # one -- so the case is named here instead and left out.
            assert mine[0] <= high and low <= mine[1], (
                ranks,
                share,
                mine,
                theirs,
            )


def test_the_published_weight_lies_where_every_sample_must() -> None:
    """INVARIANT Q16's own bound, measured over shapes and sizes.

    The loader REFUSES a description outside 1 to `n - 2 + 1/(n - 1)`,
    so a bound wrong in either direction refuses descriptions a real
    table produced -- which is far worse than not checking at all. The
    upper end is reached exactly by one value apart from `n - 1` equal
    ones; the lower end by an even two-point split.
    """
    shapes = (
        ("one apart", lambda n: [0.0] * (n - 1) + [1.0]),
        ("two-point", lambda n: [-1.0] * (n // 2) + [1.0] * (n - n // 2)),
        ("ramp", lambda n: [float(k) for k in range(n)]),
        ("huge", lambda n: [float(k) * 1e300 for k in range(n)]),
        ("tiny", lambda n: [float(k) * 5e-324 for k in range(n)]),
    )
    for name, make in shapes:
        for count in (4, 5, 6, 11, 50, 301):
            found = taxonomy._moments(make(count))["kurtosis"]
            if found is None:
                continue
            ceiling = count - 2 + 1 / (count - 1)
            assert 1.0 <= found <= ceiling, (name, count, found, ceiling)
    # And the two ends are REACHED, so neither is a bound that cannot bind.
    assert taxonomy._moments([0.0, 0.0, 0.0, 1.0])["kurtosis"] == pytest.approx(
        4 - 2 + 1 / 3
    )
    assert taxonomy._moments([-1.0, -1.0, 1.0, 1.0])["kurtosis"] == 1.0


def test_a_weight_below_four_values_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """Q16 IN BOTH DIRECTIONS (item P4-K-R1-F3).

    The rule refused a MISSING weight at four values and up, and never
    refused a PRESENT one below four -- so a description could carry a
    tail weight for three values, which the producer never writes and
    which no three points support. A loader that accepts a fact its own
    producer cannot write is a loader that has stopped being normative.
    """
    from synthtwin import errors, profile, reading

    table = fixtures.write(tmp_path, "three.csv", "reading\n1\n2\n4\n")
    document = profile.build_document(
        reading.read_table(str(table)), taxonomy.Settings(), []
    )
    block = document["columns"][0]
    assert block["kurtosis"] is None, "the producer wrote one after all"
    # Forge exactly the field the producer left out, and nothing else.
    block["kurtosis"] = 1.5
    written = fixtures.write_profile(tmp_path, "forged.json", document)
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(str(written))
    assert "Q16" in f"{refused.value}"


def test_the_moment_ratio_and_not_the_excess() -> None:
    """A NORMAL CURVE READS 3, and the neighbouring field decides that.

    `skew` is the plain moment measure, so this is too. Two
    neighbouring fields on two conventions is how a reader subtracts
    three from the wrong one.
    """
    import random

    rng = random.Random(5)
    found = taxonomy._moments([rng.gauss(0.0, 1.0) for _ in range(4000)])
    assert found["kurtosis"] is not None
    assert 2.7 < found["kurtosis"] < 3.3, found["kurtosis"]
