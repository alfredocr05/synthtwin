"""P4-D457 (lane ID-ROOM2): one held date column a writer at 20,000 rows, run through the zoo; split from
tests/test_held_dates_off_the_real_zoo.py at repair 1 by the CPU-seconds rule (LANE ID-ROOM2 RULINGS 3 (8)).

The G1 floor's ISO birth dates (`phi_registry`) and the date pass's diagnosis dates (`tumor_registry`), each
run as the zoo runs its table at its catalogue seed and counted with the zoo's own counter: 0 equal and 0
merging, every cell a date of the block's years or the walk's. Red on the mutant its docstring names
(wave6/ID-ROOM2/mutants.log).
"""

from __future__ import annotations

import pathlib

import pytest

import test_held_dates_off_the_real_zoo as zoo


@pytest.mark.parametrize("table", ["phi_registry", "tumor_registry"])
def test_one_column_a_writer_at_20000_rows(tmp_path: pathlib.Path, table: str) -> None:
    """At 20,000 rows: the G1 floor's ISO birth dates (756 / 782 on the base) and the date pass's diagnosis dates
    (3,138 / 3,222 on the base), 0 equal and 0 merging, every cell a date of the room's years or the walk's.

    Mutant: the room's years ignored by the writers (`_room_years` returning None): red on 756 and 3,138.
    """
    seen = zoo._held_dates(tmp_path, 20_000, (table,))
    column = (zoo.FOUR_FIGURES if table == "phi_registry" else zoo.DIAGNOSES)[-1]
    assert column in seen
    assert seen[column]["counts"] == (0, 0)
    years = seen[column]["years"]
    assert isinstance(years, list) and years and years[0][0] == 2028
    written = zoo._years_written(seen[column]["twin"])  # type: ignore[arg-type]
    assert written and min(written) >= 2028
