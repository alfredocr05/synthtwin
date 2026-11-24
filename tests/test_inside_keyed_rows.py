"""Gate file of lane SPEED-2M, part 3: the inside record's keyed zone past its 250,000 rows, on whole persons.

THE ROWS IT READS. The keyed zone reads its rows' columns whole as text,
so it was built only for a table of at most 250,000 rows, and a larger
table's twin kept the description's keyed values. Past the bound it is
now read on whole persons hashed under it (`cli._keyed_rows_of`, the
relations fit's own choice of rows): every row of a person or none, about
the bound's rows, in the table's order, each column read a column at a
time. Mutant: the rows hashed one by one, a person's rows split.

THROUGH THE COMMANDS. The battery's charting table (T3, keyed by item) of
20,000 rows, described with the bound set to 10,000: the record holds a
keyed zone read on the persons the bound keeps, the description is the
one the keyed zone stands beside (no patient layer), and the twin is drawn
from it. Mutant: the bound left as a refusal, so no zone is written.

AT OR UNDER THE BOUND NOTHING MOVES: every row is read, as before
(`_keyed_rows_of` gives None), so the reliability battery's tables and
every table of 250,000 rows or fewer keep their bytes.

Every table here is drawn by the standard library's `random` from a
seed, at run time; nothing is committed.
"""

from __future__ import annotations

import pathlib

import pytest

from synthtwin import cli, inside, inside_relations as R


def _persons(rows: int, seed: int) -> R.Persons:
    import random

    draw = random.Random(f"keyed-rows-{seed}")
    cells: "list[str]" = []
    person = 0
    while len(cells) < rows:
        person += 1
        cells += [f"P{person:06d}"] * min(rows - len(cells), 1 + draw.randrange(30))
    return R.persons_of(cells)


def test_at_or_under_the_bound_every_row_is_read() -> None:
    persons = _persons(5000, 1)
    assert cli._keyed_rows_of(5000, persons) is None
    assert cli._keyed_rows_of(cli._KEYED_ZONE_MOST_ROWS, persons) is None


def test_past_the_bound_whole_persons_about_the_bounds_rows(monkeypatch: "pytest.MonkeyPatch") -> None:
    monkeypatch.setattr(cli, "_KEYED_ZONE_MOST_ROWS", 4000)
    persons = _persons(20000, 2)
    kept = cli._keyed_rows_of(20000, persons)
    assert kept is not None
    assert kept == sorted(kept) and len(set(kept)) == len(kept)
    assert 0.8 * 4000 <= len(kept) <= 1.2 * 4000, len(kept)
    taken = {persons.person[row] for row in kept}
    whole = [row for row in range(20000) if persons.person[row] in taken]
    assert kept == whole


def test_a_charting_table_past_the_bound_writes_a_keyed_zone_on_its_kept_persons(
        tmp_path: pathlib.Path, monkeypatch: "pytest.MonkeyPatch") -> None:
    import reliability_battery as B
    import reliability_tables as T

    from synthtwin import installation

    def places() -> inside.Places:
        return inside.Places(pathlib.Path(installation.data_folder(), inside.FOLDER), (), (), installation.system_name())

    monkeypatch.setattr(cli, "_INSIDE_RECORD_SHIPPED", True)
    monkeypatch.setattr(cli, "_KEYED_ZONE_SHIPPED", True)
    monkeypatch.setattr(cli, "_KEYED_ZONE_MOST_ROWS", 10000)
    monkeypatch.setattr(inside, "default_places", places)
    product = B.make_twins(pathlib.Path(f"{tmp_path}"), "T3", T.text("T3", 20000, 1), (0,), True)
    assert product.errors == {} and 0 in product.twins
    # ...the record in the battery's own installation folder (`reliability_battery.installed`).
    records = sorted(pathlib.Path(f"{tmp_path}", "installation", "synthtwin", inside.FOLDER).glob(f"*{inside.SUFFIX}"))
    assert len(records) == 1
    record = inside.load_record(records[0])
    zones = record["zones"]
    assert isinstance(zones, dict) and "keyed" in zones, sorted(zones) if isinstance(zones, dict) else zones
    keyed = zones["keyed"]
    assert isinstance(keyed, dict)
    assert 0.8 * 10000 <= int(str(keyed["rows"])) <= 1.2 * 10000, keyed["rows"]
    assert "trajectories" not in zones
