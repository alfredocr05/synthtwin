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

What is held here: the twin of that shape is MISSED on both moments,
with the note naming the rule; the real table still misses nothing; and
the rule leaves a window that reaches its value exactly as it was.
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


def test_a_twin_far_from_the_published_moments_is_missed(
    tmp_path: pathlib.Path,
) -> None:
    table = fixtures.write(
        tmp_path, "amounts.csv", fixtures.rows_to_csv(["line", "amount"], _tailed_rows())
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
