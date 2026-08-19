"""A stand-in the description settles is a hole (review P3-V9-F5).

THE DEFECT THIS FILE EXISTS TO KEEP CLOSED. On the measurement side an
absence is BLANKNESS (validation method V2.4), and the reason is
residual R-P2-13: a generated value can legitimately BE the text of one
of synthtwin's own missing markers, and no file may be failed for
colliding with this package's vocabulary. That pin was applied to the
three stand-in NUMBERS whatever the description said about them -- and
the description says a great deal. Contract 5 section 3.2 way 3
publishes, per column, the candidate, the verdict, the reason and the
occurrences.

So a 180-row column of 168 ordinary decimals and twelve `-999` cells,
whose own description records `-999` as `read_as_missing` with reason
`outlier_and_frequent`, was measured with those twelve counted as data
and reported SEVENTEEN obligations MISSED against the table it was
written from: both presence counts, both distinctness counts, three
other counts, seven ladder rungs and all three moments, each with the
number the wrong reading produced printed beside it.

That is not a limit of the format. The verdict is published in full, and
the plan recorded this as acknowledged-open on the older reasoning that
V2.4 forbade consulting it. Nothing has to be consulted: the pin is
simply not applied to a number the description settles, which hands the
question back to the producer's own per-column sentinel rule under the
settings the description was written with. Same rule, same cells, same
answer -- and no second reading of `sentinel_verdicts` implemented here,
so V2.1 is met exactly as it is everywhere else.

WHAT STAYS PINNED, asserted below so the narrowing cannot creep. A
built-in missing TEXT is still data on the measurement side. A stand-in
number no column of the description settles as a hole is still data on
the measurement side. R-P2-13's protection is untouched except on the
one class of cell the description itself has already ruled on.

THE RED CHECK:

* `REINSTATE=P3-V9-F5` -- the description's verdicts read as naming
  nothing, which is the pin as it stood. Reds the witness and the
  settings assertion.

Every table here is built by the seeded neutral builders in
`fixtures.py` (plan D13), and every description by the REAL producer.
"""

import os
import pathlib

import pytest

import fixtures
from synthtwin import contract, parsing, taxonomy, validation
from synthtwin.cli import main

STAND_IN = "-999"


@pytest.fixture(autouse=True)
def _reinstated(monkeypatch: pytest.MonkeyPatch) -> None:
    """Pin every stand-in to data again when REINSTATE asks for it."""
    if os.environ.get("REINSTATE") == "P3-V9-F5":
        monkeypatch.setattr(
            validation,
            "_stand_ins_the_description_reads_as_holes",
            lambda _description: (),
        )


def _readings(holes: int, rows: int = 180) -> "list[str]":
    """Ordinary positive decimals, with ``holes`` of them a stand-in.

    Deterministic and written out rather than drawn, so the sentinel
    rule's own inputs -- the spread of the ordinary values and the share
    the candidate holds -- are the same on every machine.
    """
    ordinary = rows - holes
    values = [
        f"{10 + (row % 40) + (row % 7) / 10:.1f}" for row in range(ordinary)
    ]
    return values + [STAND_IN] * holes


def _table(folder: pathlib.Path, name: str, holes: int) -> pathlib.Path:
    return fixtures.write(
        folder,
        name,
        fixtures.single_column_table("reading", _readings(holes)),
    )


def _counts(report: str) -> "dict[str, int]":
    """The five verdict counts off a written quality report."""
    found: dict[str, int] = {}
    for line in report.splitlines():
        words = line.split()
        if len(words) > 2 and words[1].isupper() and words[0].isdigit():
            found[words[1]] = int(words[0])
    return found


def _described(
    folder: pathlib.Path, table: pathlib.Path
) -> "tuple[pathlib.Path, contract.Profile]":
    assert main(["profile", f"{table}"]) == 0
    written = folder / f"{table.stem}-profile.json"
    return written, contract.load_profile(f"{written}")


def test_the_description_publishes_the_whole_verdict(
    tmp_path: pathlib.Path,
) -> None:
    """The premise: nothing has to be guessed about these twelve cells."""
    table = _table(tmp_path, "reading.csv", 12)
    _written, description = _described(tmp_path, table)
    column = description.columns[0]
    assert column.n_present == 168
    assert column.n_missing == 12
    verdicts = column.sentinel_verdicts
    assert len(verdicts) == 1
    assert verdicts[0].candidate == STAND_IN
    assert verdicts[0].verdict == taxonomy.VERDICT_MISSING
    assert verdicts[0].n_occurrences == 12


def test_the_table_its_own_description_came_from_misses_nothing(
    tmp_path: pathlib.Path,
) -> None:
    """Seventeen misses on a perfect match, and now none."""
    table = _table(tmp_path, "reading.csv", 12)
    written, _description = _described(tmp_path, table)
    assert main(["validate", f"{written}", "--twin", f"{table}"]) == 0
    report = (tmp_path / "reading-quality.txt").read_text("utf-8")
    counted = _counts(report)
    assert counted["MISSED"] == 0
    # And the two counts the wrong reading got wrong are HELD rather
    # than merely unreported.
    assert "presence.n_present [universal.n_present]: HELD" in report
    assert "presence.n_missing [universal.n_missing]: HELD" in report


def test_the_measurement_side_stops_pinning_only_that_number(
    tmp_path: pathlib.Path,
) -> None:
    """The narrowing reaches one number, and the pin holds elsewhere."""
    table = _table(tmp_path, "reading.csv", 12)
    _written, description = _described(tmp_path, table)
    split = validation.settings_over_the_split(description)
    assert STAND_IN not in split.kept_values
    # Every built-in missing TEXT is still data on this side, which is
    # the whole of what R-P2-13 asks for on a marker the description
    # passes no verdict about.
    for spelling in parsing.MISSING_TEXTS:
        if spelling:
            assert spelling in split.kept_values
    # ...and so is a stand-in number, on a description whose columns
    # settle none.
    plain = _table(tmp_path, "plain.csv", 0)
    _elsewhere, other = _described(tmp_path, plain)
    assert other.columns[0].sentinel_verdicts == ()
    assert STAND_IN in validation.settings_over_the_split(other).kept_values


def test_the_twin_of_that_description_still_measures_clean(
    tmp_path: pathlib.Path,
) -> None:
    """End to end, because a repair that breaks the twin is not one.

    The twin writes every absent cell empty, so its holes are blank and
    nothing in it wears the stand-in. This is the run that would catch a
    narrowing that reached further than the description's own verdict.
    """
    table = _table(tmp_path, "reading.csv", 12)
    written, _description = _described(tmp_path, table)
    assert main(["generate", f"{written}"]) == 0
    twin = tmp_path / "reading-twin.csv"
    assert twin.exists()
    assert main(["validate", f"{written}", "--twin", f"{twin}"]) == 0
    counted = _counts((tmp_path / "reading-twin-quality.txt").read_text("utf-8"))
    assert counted["MISSED"] == 0
