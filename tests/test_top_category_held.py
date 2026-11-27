"""Gate file of lane LEDGER: a top-coded column's published mark is held by its floor's people in the twin.

THE 2,000,000-ROW PROOF'S TWO MISSES (lane SPEED-2M's report 2, traced on the kept twin): two number columns
top-coded at 90, whose real top category at least the floor of people held, publish the mark 90.0 as their largest
value, and the twin's high tail wrote it on ONE row; validate describes the twin again with the producer's rule
(plan P4-D454: a top category fewer than the floor's people hold is pooled below the mark) and counted one value fewer
than published (775 of 776, 786 of 787). `generation.top_category_held` writes the mark on the high tail's repeats,
each from a new person, until the floor's people hold it; `cli._twin_drawn` runs it last.

WHAT IT HOLDS (each clause red on its mutant), on an invented table of 20,000 rows and 1,000 people (the owner's floor)
whose twin is thinned to one row at the mark, as the proof's twin was:

* the thinned twin's mark is pooled by the producer's rule and the column counts one value fewer; after the pass the
  floor's people hold it, on exactly the floor's rows, and the count of different spellings is the twin's own
  (mutants: a spelling's last cell taken; a person the mark holds taken again). AT THIS SIZE THE TWIN AS MADE holds
  the mark on its floor already (the high tail's draw reaches past it); the thinning is the proof's twin's shape;
* `cli._twin_drawn` runs the pass on the twin it hands back (mutant: the pass not called).
"""

from __future__ import annotations

import csv
import io
import pathlib
import random

import pytest

import reliability_battery as B
import reliability_tables as T
from synthtwin import cli, contract, generation, taxonomy, twinstore

ROWS_A_PERSON = 20


def _text() -> str:
    draw = random.Random(3)
    lines = ["pid,age,sbp"]
    for person in range(1000):
        # Fifteen people of about 88 hold the rows past 89, fewer than a hundredth of the rows: the real top
        # category is held by more than the floor's people and the 99th percentile stands below it, as on the proof.
        base = 88.5 if person % 66 == 0 else draw.gauss(52, 9)
        for _ in range(ROWS_A_PERSON):
            age = min(99.4, max(18.0, base + draw.gauss(0, 3)))
            lines += [f"P{person:05d},{age:.1f},{100 + 0.5 * age + draw.gauss(0, 9):.0f}"]
    return "\n".join(lines) + "\n"


@pytest.fixture(scope="module")
def made(tmp_path_factory: pytest.TempPathFactory) -> "tuple[contract.Profile, pathlib.Path, list[str], list[list[str]]]":
    folder = tmp_path_factory.mktemp("top-category") / "product"
    with pytest.MonkeyPatch.context() as patch:
        patch.setitem(T.FILES, "TC", "ages.csv")
        patch.setitem(T.KNOWS, "TC", {"age": "measurement", "sbp": "measurement", "pid": "identifier"})
        patch.setitem(T.AGES, "TC", {"age"})
        patch.setitem(T.PERSON, "TC", "pid")
        product = B.make_twins(folder, "TC", _text(), (0,), False)
    description = folder / "out" / "ages-profile.json"
    loaded = contract.load_profile(str(description), chain=True)
    rows = list(csv.reader(io.StringIO(product.twins[0])))
    return loaded, description, rows[0], [list(row) for row in rows[1:]]


def _thinned(loaded: contract.Profile, header: "list[str]", rows: "list[list[str]]") -> "list[list[str]]":
    """The twin's columns with the mark kept on its first row alone, as the proof's twin held it."""
    age = [block for block in loaded.columns if block.name == "age"][0]
    assert age.top_coded == 90 and age.top_category_pooled == 11 and age.top_category_people == ("pid",)
    top = age.facts.percentiles.maximum  # type: ignore[union-attr]
    columns = [[row[at] for row in rows] for at in range(len(header))]
    ages = columns[header.index("age")]
    assert top == 90.0 and age.facts.percentiles.p99 < top  # type: ignore[union-attr]
    marks = [row for row in range(len(ages)) if float(ages[row]) == top]
    assert marks, "the twin as made holds the mark"
    # Each other mark row takes a value of its own just below the mark that no other cell holds (two decimals, where
    # every cell holds one), as the proof's tail held its largest values once each: the largest values the pass
    # meets are single, so a pass that took a value's last cell would lose a value.
    assert len(marks) < 99
    for at, row in enumerate(marks[1:]):
        ages[row] = f"{(9000 - at - 1) / 100:.2f}"
    return columns


def _pooled_distinct(ages: "list[str]", pids: "list[str]") -> "tuple[int, int]":
    pooled = taxonomy.top_category_pooled(ages, False, frozenset(), 11, 90, [pids])
    return len({cell for cell in ages if cell}), len({cell for cell in pooled if cell})


def test_the_floors_people_hold_the_mark_and_no_value_is_lost(made) -> None:  # type: ignore[no-untyped-def]
    loaded, _description, header, rows = made
    columns = _thinned(loaded, header, rows)
    ages, pids = columns[header.index("age")], columns[header.index("pid")]
    distinct, pooled = _pooled_distinct(ages, pids)
    assert pooled == distinct - 1  # the proof's miss: the mark pooled below itself, one value fewer
    held = tuple(twinstore.held_column(column) for column in columns)
    kept, changed = generation.top_category_held(loaded, held, header)
    assert changed == {"age"}
    after = twinstore.column_cells(kept[header.index("age")])
    top = [row for row in range(len(after)) if after[row] == ages[[float(cell) for cell in ages].index(max(
        float(cell) for cell in ages))]]
    assert len(top) == 11 and len({pids[row] for row in top}) == 11
    assert _pooled_distinct(after, pids) == (distinct, distinct)
    # Nothing to do on a twin that already holds it.
    again, none = generation.top_category_held(loaded, kept, header)
    assert none == set() and again == kept


def test_the_twin_handed_back_holds_the_mark(made, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    loaded, description, header, _rows = made
    real = generation.generate_held

    def thin(profile, seed):  # type: ignore[no-untyped-def]
        twin = real(profile, seed)
        if "age" not in twin.names or "pid" not in twin.names:
            return twin  # the patient walk's own runs, inside the outer one
        cells = [twinstore.column_cells(column) for column in twin.held_columns]
        rows = [[cells[at][row] for at in range(len(cells))] for row in range(len(cells[0]))]
        columns = _thinned(profile, list(twin.names), rows)
        return generation.dataclasses.replace(twin, held_columns=tuple(twinstore.held_column(c) for c in columns))

    monkeypatch.setattr(generation, "generate_held", thin)
    twin, _drawn = cli._twin_drawn(str(description), loaded, None, 0)
    ages = twinstore.column_cells(twin.held_columns[header.index("age")])
    pids = twinstore.column_cells(twin.held_columns[header.index("pid")])
    distinct, pooled = _pooled_distinct(ages, pids)
    assert pooled == distinct
