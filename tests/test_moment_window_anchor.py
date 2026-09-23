"""A twin far from the published mean or spread is not WITHIN-BOUND (V6.1-A2).

THE DEFECT, AS MEASURED (repair of the stage-2b integration). A 5,000-row
column of amounts drawn `lognormvariate(6, 1.4)` with one far value
published a mean of 1049.66 and a standard deviation of 2697.30. Its
twin held 1485.25 and 7040.63 -- 41 and 161 per cent high -- and the
quality report called both WITHIN-BOUND at exit 0, because G12.3's
windows are drawn from the construction, and on this column they sat
wholly above the published values (1438.37 to 1682.34, 6442.66 to
8771.67). The owner's ruling is that statistics computed on the twin
are reliable; a report that passes this twin says they are.

What is held here: a twin far from the published moments is MISSED on
both, with the note naming the rule; the real table still misses
nothing; and the rule leaves a window that reaches its value exactly as
it was.

THE WITNESS MOVED IN LANDING 3.3 AND THE OLD ONE IS KEPT AS A
MEASUREMENT. The tail rule of contract 6.7a withholds the rungs that
read a column's outermost values, so the 5,000-row column above no
longer hands its twin a straight run out to that far value: the twin
stands within a third of a per cent of both moments and misses
nothing, which the second test records. The corner is reached now by a
column TOO THIN FOR TWO TAILS -- twenty amounts at a floor of eleven,
one of them far -- whose block publishes its moments alone and is read
as a uniform (method G5.3c). The rule is the same and so is the shape
of the defect: a twin four times the published mean, inside a window
that sits wholly above that mean.
"""

import contextlib
import io
import pathlib
import random
import sys

import fixtures
from synthtwin import validation


def _exit_of(argv: "list[str]") -> int:
    from synthtwin import cli

    before = sys.argv
    sys.argv = ["synthtwin"] + argv
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = cli.main()
    except SystemExit as stop:
        return 0 if stop.code is None else int(stop.code)
    finally:
        sys.argv = before
    return code


def _tailed_rows() -> "list[list[str]]":
    draw = random.Random(2)
    rows = []
    for index in range(5000):
        amount = draw.lognormvariate(6, 1.4)
        if index == 4321:
            amount = 124284.2
        rows = rows + [[f"{index + 1}", f"{amount:.2f}"]]
    return rows


def _thin_rows() -> "list[list[str]]":
    """Twenty amounts, one of them far from the rest.

    THE WITNESS MOVED HERE IN LANDING 3.3, and the move is the tail
    rule's doing. The five-thousand-row column above kept its shape
    from the two ends of a straight outer segment; the tail rule
    withholds those rungs and states each end as a group, so its twin
    now stands within a third of a per cent of both published moments
    and no window of it misses its own value. Twenty rows at a floor of
    eleven are TOO THIN FOR TWO TAILS (contract TL3), so the block
    publishes its moments alone and is read as the uniform with that
    mean and spread (method G5.3c) -- a reading a far value pulls a
    long way from the column's own moments, which is exactly the corner
    this rule exists for. Seeded, so the same table is written on every
    machine.
    """
    draw = random.Random(12)
    amounts = [f"{draw.expovariate(1 / 100):.2f}" for _each in range(20)]
    amounts[10] = "999999.99"
    return [
        [f"{index + 1}", amount] for index, amount in enumerate(amounts)
    ]


def test_a_twin_far_from_the_published_moments_is_missed(
    tmp_path: pathlib.Path,
) -> None:
    """The defect, end to end, on the thin column that still reaches it.

    Published mean 50,074.46 and spread 223,589.28; the twin holds
    208,831.03 and 131,293.81 at every seed from 0 to 3, and G12.3's
    windows -- 159,457 to 277,885 and 68,871 to 203,482 -- sit wholly
    away from the published values, so reading the verdict off window
    membership alone would call both a pass.
    """
    table = fixtures.write(
        tmp_path, "amounts.csv", fixtures.rows_to_csv(["line", "amount"], _thin_rows())
    )
    assert _exit_of(["profile", str(table), "--out-dir", str(tmp_path),
                     "--identifier", "line"]) == 0
    described = tmp_path / "amounts-profile.json"
    real = tmp_path / "real"
    real.mkdir()
    assert _exit_of(["validate", str(described), "--twin", str(table),
                     "--out-dir", str(real)]) == 0
    assert _exit_of(["generate", str(described), "--out-dir", str(tmp_path),
                     "--seed", "1"]) == 0
    checked = tmp_path / "checked"
    checked.mkdir()
    assert _exit_of(["validate", str(described), "--twin",
                     str(tmp_path / "amounts-twin.csv"),
                     "--out-dir", str(checked)]) == 3
    report = (checked / "amounts-twin-quality.txt").read_text(encoding="utf-8")
    assert "moments.mean [numeric.mean]: MISSED" in report
    assert "moments.std [numeric.std]: MISSED" in report
    assert "window is not taken as a pass (V6.1-A2)" in report


def test_the_column_this_file_opened_on_meets_its_moments_now(
    tmp_path: pathlib.Path,
) -> None:
    """The defect's own witness, measured again after landing 3.3.

    Five thousand lognormal amounts with one far value. Its twin held a
    mean 41 per cent high and a spread 161 per cent high, and both were
    called WITHIN-BOUND at exit 0 -- which is why this file exists. The
    tail rule withholds the rungs that read the far value and states
    each end as a group (contract 6.7a), so the twin now holds 1,079.99
    against a published 1,076.44 and 3,100.64 against 3,095.01: 0.33
    and 0.18 per cent. Nothing is missed and nothing needs the anchor.
    """
    table = fixtures.write(
        tmp_path, "amounts.csv", fixtures.rows_to_csv(["line", "amount"], _tailed_rows())
    )
    assert _exit_of(["profile", str(table), "--out-dir", str(tmp_path),
                     "--identifier", "line"]) == 0
    described = tmp_path / "amounts-profile.json"
    assert _exit_of(["generate", str(described), "--out-dir", str(tmp_path),
                     "--seed", "1"]) == 0
    checked = tmp_path / "checked"
    checked.mkdir()
    assert _exit_of(["validate", str(described), "--twin",
                     str(tmp_path / "amounts-twin.csv"),
                     "--out-dir", str(checked)]) == 0
    report = (checked / "amounts-twin-quality.txt").read_text(encoding="utf-8")
    assert "moments.mean [numeric.mean]: WITHIN-BOUND" in report
    assert "moments.std [numeric.std]: WITHIN-BOUND" in report
    assert "window is not taken as a pass (V6.1-A2)" not in report


def test_the_anchor_moves_no_verdict_where_the_window_reaches_the_value() -> None:
    """Inside a window that covers the value, the verdict is the window's."""
    reaching = validation._within(
        "c", "numeric.mean", "moments.mean", "10", 10.9, (9.0, 11.0),
        "G12.3", 10.0, anchored=True,
    )
    assert reaching.verdict == validation.WITHIN_BOUND
    # A window wholly above the value: near the value passes, far misses.
    near = validation._within(
        "c", "numeric.mean", "moments.mean", "10", 10.4, (10.2, 11.2),
        "G12.3", 10.0, anchored=True,
    )
    assert near.verdict == validation.WITHIN_BOUND
    far = validation._within(
        "c", "numeric.mean", "moments.mean", "10", 11.1, (10.2, 11.2),
        "G12.3", 10.0, anchored=True,
    )
    assert far.verdict == validation.MISSED
    # And skew and kurtosis, which are not anchored, keep the window alone.
    loose = validation._within(
        "c", "numeric.skew", "moments.skew", "10", 11.1, (10.2, 11.2),
        "G12.3", 10.0,
    )
    assert loose.verdict == validation.WITHIN_BOUND
