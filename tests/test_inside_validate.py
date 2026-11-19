"""Gate file of the 4w integration: `validate` of a twin drawn from the inside record is not a rubber stamp.

A column drawn from the inside record keeps its shape and relations, not the description's exact counts and spellings,
so `synthtwin validate` excuses exactly those obligations (a label's level counts and spelling census, a number's
distinct and zero counts, a made-up date column's day-level ladder and tails, `cli._INSIDE_EXCUSED_FACTS` and
`cli._INSIDE_EXCUSED_DATE_FACTS`) and nothing else.

WHAT IT HOLDS (each clause red on its mutant):

* The faithful drawn twin validates with exit 0 and no MISSED (mutant: nothing is excused, so exit 3).
* A damaged drawn twin (the age column blanked on every third row, which the presence obligations of a drawn column
  never excuse) still exits 3 (mutant: every MISSED check of a drawn column is relabelled, so exit 0).
"""

from __future__ import annotations

import contextlib
import io
import pathlib
import typing

import pytest

import reliability_battery as B
import reliability_tables as T
from synthtwin import cli, inside, installation


@pytest.fixture(scope="module", autouse=True)
def _inside_record_switched_on() -> "typing.Iterator[None]":
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("synthtwin.cli._INSIDE_RECORD_SHIPPED", True)
        yield


def _places(folder: pathlib.Path) -> inside.Places:
    return inside.Places(pathlib.Path(folder, "installation", "synthtwin", "inside"), (), (),
                         installation.system_name(), ())


@pytest.fixture(scope="module")
def made(tmp_path_factory: pytest.TempPathFactory) -> "tuple[pathlib.Path, pathlib.Path, pathlib.Path]":
    folder = tmp_path_factory.mktemp("inside-validate") / "product"
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("synthtwin.cli._INSIDE_RECORD_SHIPPED", True)
        patch.setattr(inside, "default_places", lambda: _places(folder))
        B.make_twins(folder, "T2", T.text("T2", 20000, 1), (0,), False)
    return folder, folder / "out" / "visits-profile.json", folder / "out" / "visits-twin.csv"


def _validate(folder: pathlib.Path, description: pathlib.Path) -> int:
    places = _places(folder)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("synthtwin.cli._INSIDE_RECORD_SHIPPED", True)
        patch.setattr(inside, "default_places", lambda: places)
        with B.installed(folder), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return int(cli.main(["validate", f"{description}", "--replace"], small_tables_refused=False))


def test_the_faithful_drawn_twin_validates(made) -> None:  # type: ignore[no-untyped-def]
    folder, description, _twin = made
    assert _validate(folder, description) == 0


def test_a_damaged_drawn_twin_still_exits_three(made) -> None:  # type: ignore[no-untyped-def]
    folder, description, twin = made
    kept = twin.read_bytes()
    lines = kept.decode("utf-8").split("\n")
    header = lines[0].split(",")
    at = header.index("age")
    damaged = [lines[0]]
    for number, line in enumerate(lines[1:]):
        cells = line.split(",")
        if len(cells) == len(header) and number % 3 == 0:
            cells[at] = ""
        damaged.append(",".join(cells))
    try:
        twin.write_bytes("\n".join(damaged).encode("utf-8"))
        assert _validate(folder, description) == 3
    finally:
        twin.write_bytes(kept)
