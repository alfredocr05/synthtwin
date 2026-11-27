"""Gate file of the 4w integration (plans P4-D496 and P4-D497): the dates zone composed with the relations draw.

Lane IN-5 wrote the dates zone and its writer, lane IN-2 the relations draw
and the generate step; the integration wires them: `synthtwin profile`
writes the dates zone beside the relations zone, `generation.generate_inside`
writes each date column from it after the relations draw, and a date column
the description's twin holds blank stays blank.

WHAT IT HOLDS (each clause red on its mutant, the integrator's report):

* The record carries a dates zone naming the visits table's date column
  (mutant: the profile never writes the zone).
* The twin's date column is read from the zone: its weekday shares stand
  within 0.03 (total variation) of the real table's, which the description's
  month-published dates do not give (mutant: the generate step never reads
  the zone).
* Every twin date is a valid date in the real column's own written form
  (the zone writes the column's spelling).
"""

from __future__ import annotations

import csv
import datetime
import io
import pathlib

import typing

import pytest

import reliability_battery as B
import reliability_tables as T
from synthtwin import inside, installation

ROWS = 20000
DATE = "visit_date"


def _places(folder: pathlib.Path) -> inside.Places:
    return inside.Places(pathlib.Path(folder, "installation", "synthtwin", "inside"), (), (),
                         installation.system_name(), ())


@pytest.fixture(scope="module")
def made(tmp_path_factory: pytest.TempPathFactory) -> "tuple[pathlib.Path, str, B.Product]":
    folder = tmp_path_factory.mktemp("inside-compose") / "product"
    text = T.text("T2", ROWS, 1)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inside, "default_places", lambda: _places(folder))
        product = B.make_twins(folder, "T2", text, (0,), False)
    return folder, text, product


def _cells(text: str) -> "list[str]":
    return [row[DATE] for row in csv.DictReader(io.StringIO(text))]


def _weekdays(cells: "list[str]") -> "list[float]":
    counts = [0] * 7
    total = 0
    for cell in cells:
        if not cell:
            continue
        counts[datetime.date.fromisoformat(cell[:10]).weekday()] += 1
        total += 1
    return [each / total for each in counts]


def test_the_record_carries_the_dates_zone(made) -> None:  # type: ignore[no-untyped-def]
    folder, _text, product = made
    assert not product.errors, product.errors
    found = sorted(_places(folder).private.glob(f"*{inside.SUFFIX}"))
    assert found
    zones = inside.load_record(found[0])["zones"]  # type: ignore[index]
    assert "dates" in zones and DATE in zones["dates"]["order"]  # type: ignore[operator,index]


def test_the_twin_keeps_the_weekday_pattern(made) -> None:  # type: ignore[no-untyped-def]
    _folder, text, product = made
    real = _weekdays(_cells(text))
    twin = _weekdays(_cells(product.twins[0]))
    distance = sum(abs(a - b) for a, b in zip(real, twin)) / 2
    assert distance <= 0.03, (distance, real, twin)


def test_the_report_names_the_date_column_among_the_drawn(made) -> None:  # type: ignore[no-untyped-def]
    folder, _text, _product = made
    report = pathlib.Path(folder, "out", "visits-twin-report.txt").read_text(encoding="utf-8")
    opening = report.split("Each holds its own shape", 1)[0]
    assert DATE in opening, opening


def test_every_twin_date_is_valid_and_in_the_real_form(made) -> None:  # type: ignore[no-untyped-def]
    _folder, text, product = made
    real = [cell for cell in _cells(text) if cell]
    twin = [cell for cell in _cells(product.twins[0]) if cell]
    assert twin
    assert {len(cell) for cell in twin} == {len(real[0])}
    for cell in twin:
        datetime.date.fromisoformat(cell[:10])


@pytest.fixture(scope="module", autouse=True)
def _inside_record_switched_on() -> "typing.Iterator[None]":
    """The inside record's sub-switch is on for this file (`cli._inside_record_switched_on`)."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("synthtwin.cli._INSIDE_RECORD_SHIPPED", True)
        yield
