"""The twin checks read an amount and a share as the numbers they write (lane ZOO-X).

Measured by the data-type zoo (`tests/types_zoo.py`, the typed_numbers
table at 20,000 rows): run as a first run types it -- the identifiers
named, no other column answered -- the checks read a column of dollar
amounts (`$1,234.56`, `($45.00)`) as keys, because their reader of
numbers (`twin_checks.read_number`) took no money mark and nearly every
amount is different, and C4 then counted each amount the twin happened
to share with the real column as a copied identifier: 3,857 of 20,000
cells, and a twin that copied nothing was quarantined. A percent column
(`45.5%`) was read as text the same way.

`read_number` now reads one money mark after the sign and one percent
sign at the end off the figures. Each test below is red on the mutant
that drops either reading.
"""

from __future__ import annotations

import csv
import io
import pathlib
import random

import pytest

from synthtwin import twin_checks


@pytest.mark.parametrize(
    ("cell", "value"),
    [
        ("$1,234.56", 1234.56),
        ("($45.00)", -45.0),
        ("-$5", -5.0),
        ("45.5%", 45.5),
        ("100%", 100.0),
        ("€12.50", 12.5),
        ("£3", 3.0),
    ],
)
def test_an_amount_and_a_share_read_as_their_numbers(cell: str, value: float) -> None:
    read = twin_checks.read_number(cell)
    assert read is not None, cell
    assert read.value == value


@pytest.mark.parametrize("cell", ["$", "%", "$$5", "5%%", "$5$", "%5", "USD 5", "5 mg"])
def test_a_mark_alone_or_twice_is_no_number(cell: str) -> None:
    assert twin_checks.read_number(cell) is None


def test_a_number_without_a_mark_reads_as_before() -> None:
    for cell, spelling in (("1,234.56", "1234.56"), ("007.50", "7.5"), ("1.0E+03", "1000"), ("-0.0", "0")):
        read = twin_checks.read_number(cell)
        assert read is not None and read.spelling == spelling, cell


def _amounts(seed: int, rows: int) -> "list[str]":
    draw = random.Random(seed)
    out = []
    for _ in range(rows):
        amount = draw.lognormvariate(6.0, 1.3)
        out += [f"(${amount:,.2f})" if draw.random() < 0.05 else f"${amount:,.2f}"]
    return out


def test_a_column_of_amounts_is_read_as_numbers_not_as_keys() -> None:
    cells = _amounts(3, 4000)
    assert len(set(cells)) * 1000 >= twin_checks.KEY_LIKE_SHARE * len(cells)
    column = twin_checks._kind_of(twin_checks.ColumnPlan("charge_amount"), cells)
    assert column.kind == twin_checks.KIND_NUMBER
    assert not twin_checks.reads_as_an_identifier("charge_amount", cells)
    shares = [f"{random.Random(place).uniform(0, 100):.1f}%" for place in range(4000)]
    assert twin_checks._kind_of(twin_checks.ColumnPlan("share_written"), shares).kind == twin_checks.KIND_NUMBER


def _write(path: pathlib.Path, prefix: str, seed: int) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["visit_ref", "charge_amount"])
    for place, amount in enumerate(_amounts(seed, 4000)):
        writer.writerow([f"{prefix}{place:07d}", amount])
    path.write_text(buffer.getvalue(), encoding="utf-8", newline="\n")
    return f"{path}"


def test_amounts_a_twin_shares_by_chance_are_no_copied_identifier(tmp_path: pathlib.Path) -> None:
    real = _write(tmp_path / "real.csv", "R", 11)
    twin = _write(tmp_path / "twin.csv", "T", 12)
    real_cells = set(_amounts(11, 4000))
    assert sum(1 for cell in _amounts(12, 4000) if cell in real_cells) > 0, "premise: some amount is shared by chance"
    outcome = twin_checks.run_checks(real, twin, identifiers=("visit_ref",), small_tables_refused=False)
    checks = {check.code: check for check in outcome.checks}
    assert checks["C4"].passed, checks["C4"].lines
    assert not any("charge_amount" in line for line in checks["C4"].lines), checks["C4"].lines
