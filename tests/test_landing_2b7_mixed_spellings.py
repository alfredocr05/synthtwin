"""Landing 2b.7: a mixture of conventions survives, and a singleton does not.

THE TWO DEFECTS THESE TESTS CLOSE, both found by the Codex review of
landing 2b.2 and both measured on this branch before anything changed.

1. A MIXTURE WAS COLLAPSED TO ITS MAJORITY (plan P4-D65.2). A column of
   600 charges writing 480 with a minus in front and 120 in accounting
   brackets published `minus` alone; its seed-4 twin wrote 600 minuses
   and no bracket, and the twin's report, the twin's validation and the
   real table's validation all passed with nothing missed. 200 cells
   grouped with a space beside 100 grouped with a narrow no-break space
   came back as 300 ordinary spaces, so code that strips an ordinary
   space succeeded on the twin and failed on the real table -- goal 1
   of the owner's two mandatory goals, broken in silence.

2. A CENSUS WITH ONE CATEGORY TOLD NOUGHT FROM ONE (plan P4-D65.1). At
   a floor of eleven, 1,200 measurements and the same 1,200 with one
   cell rewritten `+1600.5` gave descriptions differing in exactly one
   place -- `decimal_plus` moving from `{}` to `{"(withheld)": 1}` --
   and both loaded. `+` is that census's only category, so the pooled
   key named it: a reader holding the other 1,199 spellings can read off
   the remaining individual's.

Every test here drives the real command line in this process, as the
stage 2 round trips do: describe a realistic table, build the twin,
describe the twin again, and validate BOTH the twin and the real table,
reading what `cli.main` returned rather than trusting that a file was
written.
"""

from __future__ import annotations

import csv
import io
import json
import pathlib
import sys

import pytest

from tests import fixtures

# The floor these shapes are described at. The disclosure rule this
# landing implements binds at EVERY floor -- its own census floor is two
# whatever the settings say -- but eleven is the floor the review
# measured at and the one at which a pooled key could exist to leak.
FLOOR = ("--smallest-group", "11")

# A narrow no-break space, written as an escape deliberately: it cannot
# be told from an ordinary space on a page, which is exactly why a twin
# that replaced one with the other was never noticed.
NARROW = " "


def _exit_of(argv: "list[str]") -> int:
    """Run one synthtwin command in this process and return its exit code."""
    from synthtwin import cli

    before = sys.argv
    sys.argv = ["synthtwin"] + argv
    try:
        code = cli.main()
    except SystemExit as stop:
        return 0 if stop.code is None else int(stop.code)
    finally:
        sys.argv = before
    return code


def _round_trip(
    folder: pathlib.Path,
    cells: "list[str]",
    flags: "tuple[str, ...]" = FLOOR,
    seed: str = "4",
    header: str = "value",
) -> "tuple[dict[str, object], list[str], int, int]":
    """Describe, build, describe again, check the twin AND the real table.

    Returns the description of the source column, the twin's cells, and
    the two exit codes, which are what the gate reads: a twin nobody
    validated is a twin nobody checked.
    """
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv([header], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace"]
        + list(flags)
    ) == 0
    described = folder / "real-profile.json"
    assert _exit_of(
        [
            "generate", str(described), "--out-dir", str(folder),
            "--seed", seed, "--replace",
        ]
    ) == 0
    twin = folder / "real-twin.csv"
    written = [
        row[0]
        for row in csv.reader(io.StringIO(twin.read_text(encoding="utf-8")))
    ][1:]
    checked = folder / "check-twin"
    checked.mkdir()
    twin_exit = _exit_of(
        [
            "validate", str(described), "--twin", str(twin),
            "--out-dir", str(checked), "--replace",
        ]
    )
    real_checked = folder / "check-real"
    real_checked.mkdir()
    real_exit = _exit_of(
        [
            "validate", str(described), "--twin", str(table),
            "--out-dir", str(real_checked), "--replace",
        ]
    )
    first = json.loads(described.read_text(encoding="utf-8"))["columns"][0]
    return first, written, twin_exit, real_exit


def _wearing(cells: "list[str]", mark: str) -> int:
    """How many of these cells carry this character."""
    worn = 0
    for cell in cells:
        if mark in cell:
            worn += 1
    return worn


# -- the mixture of notations ------------------------------------------


@pytest.mark.parametrize("seed", ["4", "11", "23"])
def test_a_column_mixing_two_notations_keeps_both(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """480 minuses and 120 brackets come back as 480 and 120.

    The review's own column. Before this landing the description
    published `minus` and nothing else, and the twin wrote 600 minuses
    with every check passing.
    """
    cells = [
        f"({n}.25)" if n % 5 == 0 else f"-{n}.25" for n in range(1000, 1600)
    ]
    first, written, twin_exit, real_exit = _round_trip(
        tmp_path / "notations", cells, seed=seed, header="charge"
    )
    assert first["negative_notations"] == {"minus": 480, "brackets": 120}
    # The majority key is unchanged and still says what it always said.
    assert first["negative_form"] == "minus"
    assert _wearing(written, "(") == 120
    assert len([cell for cell in written if cell[:1] == "-"]) == 480
    assert twin_exit == 0
    assert real_exit == 0


@pytest.mark.parametrize("seed", ["4", "11", "23"])
def test_a_column_mixing_two_marks_keeps_both(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """200 spaces and 100 narrow no-break spaces come back as 200 and 100.

    The mixture that broke goal 1 outright: code stripping an ordinary
    space succeeded on the old twin and failed on the real table.
    """
    cells = [f"{1000 + i:,}".replace(",", " ") for i in range(200)] + [
        f"{3000 + i:,}".replace(",", NARROW) for i in range(100)
    ]
    first, written, twin_exit, real_exit = _round_trip(
        tmp_path / "marks", cells, seed=seed, header="count"
    )
    assert first["thousands_marks"] == {" ": 200, NARROW: 100}
    assert first["group_separator"] == " "
    assert _wearing(written, NARROW) == 100
    assert _wearing(written, " ") == 200
    assert twin_exit == 0
    assert real_exit == 0


def test_a_notation_worn_by_one_cell_is_not_published(
    tmp_path: pathlib.Path,
) -> None:
    """One bracket among 599 minuses names nobody.

    The mixture clause does not license publishing a group of one: the
    census floor is two whatever the settings floor is.

    **HOW IT NAMES NOBODY CHANGED, AND WHAT IT CLAIMS DID NOT** (the
    extra disclosure review of 2026-09-18, item 7; re-measured at the
    merge-close). This witness asserted `{"(unavailable)": 0}` -- the
    whole census withheld -- and that reading was itself the defect item
    7 closed: a census withheld ONLY where a group of one exists tells a
    reader that a group of one exists, which is the singleton it was
    meant to hide. The lone bracket is now counted into the column's
    commonest notation, the owner's ruling 6 of 2026-09-17 applied to a
    notation, so the census reads `{"minus": 600}` and is
    indistinguishable from the census of 600 cells that all wore a
    minus. Measured on the merge-close of 2026-09-18. The claim this
    test makes is unchanged: no group of one is published, and both
    files validate.
    """
    cells = [f"-{n}.25" for n in range(1000, 1600)]
    cells[7] = "(1007.25)"
    first, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "lone", cells, header="charge"
    )
    assert first["negative_notations"] == {"minus": 600}
    assert 1 not in first["negative_notations"].values()
    assert "(unavailable)" not in first["negative_notations"]
    assert twin_exit == 0
    assert real_exit == 0


def test_a_file_that_respells_the_mixture_is_missed(
    tmp_path: pathlib.Path,
) -> None:
    """A file written in ONE convention misses a description that names two.

    The obligation is what makes the census worth publishing, so it is
    pinned from the other side here: take the twin the generator wrote,
    rewrite every bracketed cell with a leading minus, and change
    nothing else. The values are the same, the count of negative cells
    is the same -- so the comparison is made rather than withheld --
    and the file now wears one convention where the description counts
    two. That is exactly the file the old generator wrote on every run,
    and it has to be MISSED.
    """
    cells = [
        f"({n}.25)" if n % 5 == 0 else f"-{n}.25" for n in range(1000, 1600)
    ]
    folder = tmp_path / "respelled"
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["charge"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace"]
        + list(FLOOR)
    ) == 0
    described = folder / "real-profile.json"
    assert _exit_of(
        [
            "generate", str(described), "--out-dir", str(folder),
            "--seed", "4", "--replace",
        ]
    ) == 0
    twin = folder / "real-twin.csv"
    remade: "list[str]" = []
    for row in twin.read_text(encoding="utf-8").split("\n"):
        body = row.strip()
        if body[:1] == "(" and body[len(body) - 1:] == ")":
            remade += ["-" + body[1: len(body) - 1]]
        else:
            remade += [row]
    respelled = folder / "respelled.csv"
    respelled.write_text("\n".join(remade), encoding="utf-8", newline="")
    checked = folder / "check"
    checked.mkdir()
    assert _exit_of(
        [
            "validate", str(described), "--twin", str(respelled),
            "--out-dir", str(checked), "--replace",
        ]
    ) == 3


# -- the census that could tell nought from one -------------------------


def test_a_signed_decimal_held_by_one_cell_is_not_told_apart_from_none(
    tmp_path: pathlib.Path,
) -> None:
    """The review's disclosure, closed: the two descriptions are identical.

    1,200 measurements, and the same 1,200 with cell 600 rewritten with
    a plus. The censuses must not differ, because `+` is this census's
    only category and any difference names the one cell that moved.
    """
    plain = [f"{1000 + i}.5" for i in range(1200)]
    signed = list(plain)
    signed[600] = "+1600.5"
    unsigned_first, _cells, unsigned_twin, unsigned_real = _round_trip(
        tmp_path / "none", plain, header="measurement"
    )
    signed_first, _also, signed_twin, signed_real = _round_trip(
        tmp_path / "one", signed, header="measurement"
    )
    assert unsigned_first["decimal_plus"] == {"(unavailable)": 0}
    assert signed_first["decimal_plus"] == unsigned_first["decimal_plus"]
    # ...and the whole published block agrees, so the census is not
    # simply moving the disclosure into a neighbouring key.
    assert signed_first == unsigned_first
    assert unsigned_twin == 0 and unsigned_real == 0
    assert signed_twin == 0 and signed_real == 0


def test_a_lone_convention_is_not_published_at_the_default_floor(
    tmp_path: pathlib.Path,
) -> None:
    """The census floor is TWO even where the person asked for one.

    `small_cell_floor` defaults to one, and a census governed by it
    alone publishes a count of one -- which names the individual who
    wrote that cell as plainly as printing the cell would. Every other
    test in this file describes at a floor of eleven, where the two
    floors agree and this rule cannot be told from the settings; these
    two columns are described at the DEFAULT floor, where only the
    census floor stands between the reader and the one odd cell.
    """
    charges = [f"-{n}.25" for n in range(1000, 1300)]
    charges[11] = "(1011.25)"
    first, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "one_bracket", charges, flags=(), header="charge"
    )
    assert first["negative_notations"] == {"(unavailable)": 0}
    # The majority key still says what it always said, so nothing about
    # the column's ordinary convention is lost with the singleton.
    assert first["negative_form"] == "minus"
    assert twin_exit == 0
    assert real_exit == 0

    measurements = [f"{1000 + i}.5" for i in range(300)]
    measurements[7] = "+1007.5"
    second, _also, signed_twin, signed_real = _round_trip(
        tmp_path / "one_plus", measurements, flags=(), header="measurement"
    )
    assert second["decimal_plus"] == {"(unavailable)": 0}
    assert signed_twin == 0
    assert signed_real == 0


def test_a_census_holds_nothing_back_at_a_floor_of_one(
    tmp_path: pathlib.Path,
) -> None:
    """Two odd cells are unavailable, never a pooled remainder.

    Invariant C5-S13: a description written at a floor of one holds
    nothing back, because there is no group below that size to hold.
    These censuses read a floor of two all the same, so they have a
    range below their own floor exactly where the document says there
    is none -- and the answer is the unavailable state, which holds
    back no COUNT, rather than a `(withheld)` remainder the loader
    would refuse.
    """
    charges = [f"-{n}.25" for n in range(1000, 1300)]
    charges[11] = "(1011.25)"
    charges[23] = "−1023.25"
    first, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "two_odd", charges, flags=(), header="charge"
    )
    assert first["negative_notations"] == {"(unavailable)": 0}
    assert twin_exit == 0
    assert real_exit == 0


def test_a_count_whose_complement_names_one_cell_is_not_published(
    tmp_path: pathlib.Path,
) -> None:
    """1,195 signed of 1,200 names the five that are not, so it is withheld.

    THE COMPLEMENT CLAUSE, which the first version of this rule did not
    have. A census that refuses to name a count of one still names one
    individual if it names the count of everybody ELSE: publishing
    "1,195 of these 1,200 cells carry a plus" tells a reader holding
    1,199 spellings exactly as much as publishing "5 do". So a count is
    named only where the cells it does NOT cover are nought or reach
    the census floor themselves.
    """
    cells = [f"+{1000 + i}.5" for i in range(1200)]
    for place in range(0, 5):
        cells[place] = f"{1000 + place}.5"
    first, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "complement", cells, header="measurement"
    )
    assert first["decimal_plus"] == {"(unavailable)": 0}
    assert twin_exit == 0
    assert real_exit == 0


def test_a_signed_decimal_count_that_names_a_group_is_still_published(
    tmp_path: pathlib.Path,
) -> None:
    """Forty signed cells of 1,200 are named, and the twin writes forty.

    The disclosure rule withdraws a count that names an individual. It
    does not withdraw the fact: a count reaching the census floor, whose
    complement reaches it too, is published and generated as before.
    """
    cells = [f"{1000 + i}.5" for i in range(1200)]
    for place in range(600, 640):
        cells[place] = "+" + cells[place]
    first, written, twin_exit, real_exit = _round_trip(
        tmp_path / "named", cells, header="measurement"
    )
    assert first["decimal_plus"] == {"+": 40}
    assert _wearing(written, "+") == 40
    assert twin_exit == 0
    assert real_exit == 0
