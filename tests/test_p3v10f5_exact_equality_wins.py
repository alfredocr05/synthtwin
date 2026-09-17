"""A file holding the published value is not missing it (review P3-V10-F5).

THE DEFECT THIS FILE EXISTS TO KEEP CLOSED. An approximated obligation
is settled against a window, and a window here is not a margin around
the description's own value: it is worked out from the description and
the size of the column, so it can lie wholly to one side of that value.
Reading the verdict off the window alone therefore printed a line that
contradicted itself --

    date-ladder.p99 [datetime.date_percentiles]: MISSED
        the description asks for: 2024-12-24
        the file was found to hold: that same value

-- on the source table checked against its own description, because
G12.4's window for that rung ends a day earlier. Four rungs of that one
table said it, and the cardinality envelope of a column of dates said
the same thing in numbers on two more: "asks for 84 (between 106.0 and
240.0) ... found 84.0: MISSED".

THE REPAIR IS THE VERDICT AND NOT THE WORDING. V6.1's two definitions
overlap here rather than conflict: HELD is "the exact obligation was
met", and a file holding the description's own value has met it. So the
exact reading is taken first, on every envelope this module draws --
`_within` and `_within_instant` both -- and the window is left to
explain itself in the note beneath. Plan amendment A-P3-40 and
validation method clause V6.1-A1 are the ruling.

WHAT DOES NOT MOVE, asserted below so the repair cannot creep: a file
holding anything OTHER than the published value is judged by the window
exactly as before, inside it and outside it.

THE RED CHECK:

* `REINSTATE=P3-V10-F5` -- both envelope functions as they shipped, with
  the verdict read off window membership alone. Reds the source-table
  witness and the two narrowness cases below it.

Every table here is built by the seeded neutral builders in
`fixtures.py` (plan D13), and every description by the REAL producer.
"""

import os
import pathlib

import pytest

import fixtures
from synthtwin import contract, validation
from synthtwin.cli import main


def _within_as_it_shipped(
    column: str,
    fact: str,
    subcheck: str,
    published: str,
    measured: "float | None",
    window: "tuple[float, float] | None",
    citation: str,
    value: "float | None" = None,
    anchored: bool = False,
) -> validation.Check:
    """`validation._within` exactly as it shipped: the window decides.

    ``anchored`` (V6.1-A2, added later) is accepted and not read, so the
    red check reinstates the window-only verdict and nothing else.
    """
    if measured is None or window is None:
        return validation.Check(
            column, fact, subcheck, validation.WITHHELD, published, "",
            validation._GATE_CLOSED,
        )
    low, high = window
    verdict = (
        validation.WITHIN_BOUND
        if low <= measured <= high
        else validation.MISSED
    )
    note: tuple[str, ...] = ()
    if value is not None and not low <= value <= high:
        note = (
            (
                "      this window does NOT reach the description's own "
                "value. It is"
            ),
            "      what the method allows the file here, worked out from",
            "      the description and the size of this column; it is not",
            "      a margin around that value.",
        )
    return validation.Check(
        column,
        fact,
        subcheck,
        verdict,
        f"{published} ({validation._shown_window(low, high)})",
        validation._shown_number(measured),
        citation,
        note,
    )


def _within_instant_as_it_shipped(
    column: str,
    subcheck: str,
    facts: contract.DatetimeFacts,
    published: str,
    measured: "int | None",
    window: "tuple[int, int]",
) -> validation.Check:
    """`validation._within_instant` as it shipped: the window decides."""
    rung = validation._ordinal_of(published, facts.resolution)
    low, high = window
    allowed = (
        f"      this rung of the file is allowed from "
        f"{validation._shown_distance(low, rung, facts)}"
    )
    note: tuple[str, ...] = (
        allowed,
        (
            f"        to {validation._shown_distance(high, rung, facts)}, "
            f"and it covers the value above"
        ),
    )
    if not low <= rung <= high:
        note = (
            allowed,
            (
                f"        to "
                f"{validation._shown_distance(high, rung, facts)}, and it "
                f"does NOT reach the"
            ),
            "        value above. This window is what the method allows",
            "        the file's own rung, worked out from the description",
            "        and the size of this column; it is not a margin",
            "        around the description's value.",
        )
    if measured is None:
        return validation.Check(
            column,
            "datetime.date_percentiles",
            subcheck,
            validation.WITHHELD,
            published,
            "",
            validation._GATE_CLOSED,
        )
    verdict = (
        validation.WITHIN_BOUND
        if low <= measured <= high
        else validation.MISSED
    )
    return validation.Check(
        column,
        "datetime.date_percentiles",
        subcheck,
        verdict,
        published,
        validation._shown_distance(measured, rung, facts),
        validation.ENVELOPE_DATETIME_RUNGS,
        note,
    )


def reinstate(monkeypatch: pytest.MonkeyPatch) -> None:
    """Both envelope functions as they shipped, window-only verdicts."""
    monkeypatch.setattr(validation, "_within", _within_as_it_shipped)
    monkeypatch.setattr(
        validation, "_within_instant", _within_instant_as_it_shipped
    )


@pytest.fixture(autouse=True)
def _reinstated(monkeypatch: pytest.MonkeyPatch) -> None:
    if os.environ.get("REINSTATE") == "P3-V10-F5":
        reinstate(monkeypatch)


def _dated_table() -> str:
    """One column of dates and one of readings, over a whole year.

    Deterministic and written out, so the ladder the description
    publishes and the windows G12.4 draws around it are the same on
    every machine. The dates are what put a window wholly below the
    value it stands beside, which is what this file is about.
    """
    rows = []
    for index in range(240):
        rows = rows + [
            [
                f"2024-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
                f"{(index * 37) % 883 + 10}",
            ]
        ]
    return fixtures.rows_to_csv(["recorded_on", "reading"], rows)


def _tailed_table() -> str:
    """A column of amounts with a long right tail and one far value.

    WHY THE WITNESS MOVED HERE (measured at the stage-2b integration).
    Landing 2b.6 redrew G12.4's date windows so that a column's dates
    spread across days like the real table's, and no date rung of the
    table above -- nor of sixty seeded date tables searched for one --
    has a window lying wholly to one side of its own value any more.
    The corner this file guards is still reachable through the other
    envelope function, `_within`: on this column G12.3's windows for the
    mean, the standard deviation and the tail weight all sit away from
    the published values, so the real table is exactly the file that
    holds a value its window does not reach. Seeded, so the same table
    is written on every machine.
    """
    import random

    draw = random.Random(2)
    rows = []
    for index in range(5000):
        amount = draw.lognormvariate(6, 1.4)
        if index == 4321:
            amount = 124284.2
        rows = rows + [[f"{index + 1}", f"{amount:.2f}"]]
    return fixtures.rows_to_csv(["line", "amount"], rows)


def _described(
    folder: pathlib.Path, table: pathlib.Path
) -> "tuple[pathlib.Path, contract.Profile]":
    assert main(["profile", f"{table}"]) == 0
    written = folder / f"{table.stem}-profile.json"
    return written, contract.load_profile(f"{written}")


def _outcome(
    folder: pathlib.Path,
) -> "tuple[validation.Outcome, contract.Profile]":
    table = fixtures.write(folder, "table.csv", _dated_table())
    _written, description = _described(folder, table)
    return validation.measure(description, f"{table}"), description


def test_the_witness_has_a_window_that_misses_its_own_value(
    tmp_path: pathlib.Path,
) -> None:
    """Non-vacuity first: this table really does reach that corner.

    If it ever stops having a rung whose window sits wholly below the
    description's own value, this file says so rather than passing on a
    corner it can no longer see.
    """
    table = fixtures.write(tmp_path, "tailed.csv", _tailed_table())
    _written, description = _described(tmp_path, table)
    outcome = validation.measure(description, f"{table}")
    outside = [
        check
        for check in outcome.checks
        if check.fact in ("numeric.mean", "numeric.std")
        and "does NOT reach the" in "\n".join(check.note)
    ]
    assert len(outside) == 2, (
        "the tailed column no longer has a mean and a spread whose "
        "windows miss the description's own values, so this file can no "
        "longer see the defect it exists for"
    )
    for check in outside:
        assert check.achieved == check.published
        assert check.verdict == validation.HELD


def test_no_line_says_the_file_holds_the_value_and_misses_it(
    tmp_path: pathlib.Path,
) -> None:
    """The property, over every obligation of the whole run."""
    outcome, _description = _outcome(tmp_path)
    exact = 0
    for check in outcome.checks:
        if not check.achieved:
            continue
        if check.achieved != "that same value" and (
            check.achieved != check.published
        ):
            continue
        exact = exact + 1
        assert check.verdict == validation.HELD, (
            f"'{check.column}' {check.subcheck}: the page asks for "
            f"{check.published!r}, says the file holds {check.achieved!r}, "
            f"and calls it {check.verdict}"
        )
    assert exact, "no line of this page prints one value twice"


def test_the_table_its_own_description_came_from_misses_nothing(
    tmp_path: pathlib.Path,
) -> None:
    """The run a researcher makes first, end to end through the CLI."""
    table = fixtures.write(tmp_path, "table.csv", _dated_table())
    written, _description = _described(tmp_path, table)
    assert main(["validate", f"{written}", "--twin", f"{table}"]) == 0
    report = (tmp_path / "table-quality.txt").read_text("utf-8")
    assert "0  MISSED" in report
    # ...and the line the reviewer read is now HELD, with the window
    # still explaining itself underneath.
    assert "date-ladder.p99 [datetime.date_percentiles]: HELD" in report
    assert "the file was found to hold: that same value" in report
    # ...and the window that does not reach its own value is on the
    # tailed table now (see `_tailed_table`), which misses nothing either.
    tailed = fixtures.write(tmp_path, "tailed.csv", _tailed_table())
    tailed_written, _tailed_description = _described(tmp_path, tailed)
    assert main(["validate", f"{tailed_written}", "--twin", f"{tailed}"]) == 0
    tailed_report = (tmp_path / "tailed-quality.txt").read_text("utf-8")
    assert "0  MISSED" in tailed_report
    assert "moments.mean [numeric.mean]: HELD" in tailed_report
    assert "the file holds the description's own value exactly" in tailed_report


def test_a_file_that_holds_something_else_is_still_judged_by_the_window(
    tmp_path: pathlib.Path,
) -> None:
    """The narrowness: nothing but exact equality is given precedence.

    The same description, measured against a file whose dates are all
    moved a long way. Every rung then holds a value that is not the
    published one, so every one of them is settled by its window exactly
    as before -- and this table is moved far enough that they fall
    outside it.
    """
    table = fixtures.write(tmp_path, "table.csv", _dated_table())
    _written, description = _described(tmp_path, table)
    moved = []
    for index in range(240):
        moved = moved + [
            [
                f"2025-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
                f"{(index * 37) % 883 + 10}",
            ]
        ]
    other = fixtures.write(
        tmp_path,
        "moved.csv",
        fixtures.rows_to_csv(["recorded_on", "reading"], moved),
    )
    outcome = validation.measure(description, f"{other}")
    rungs = [
        check
        for check in outcome.checks
        if check.fact == "datetime.date_percentiles"
        and check.subcheck not in ("date-ladder.min", "date-ladder.max")
    ]
    assert rungs
    for check in rungs:
        assert check.achieved != "that same value"
        assert check.verdict == validation.MISSED, check
