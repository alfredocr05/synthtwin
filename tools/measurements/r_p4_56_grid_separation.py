"""R-P4-56: what separating two strata on the grid costs the twin.

`_apart_enough` moves a stratum whose written text another stratum has
already written to the nearest free point of the published width's own
grid, inside its own share of the ladder. Moving a value is not free:
it could carry a rung outside the window method G12.2 draws, or move a
moment. This walks fixed-width columns through the real producer,
loader and generator with the rule on and off, and counts what changed
-- the count of different numbers the twin holds, the cells whose shape
does not match the source's, and every deviation and approximation the
twin's own report files.
"""

import pathlib
import random
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import fixtures  # noqa: E402
from synthtwin import (  # noqa: E402
    contract,
    generation,
    profile,
    reading,
    taxonomy,
)

COLUMNS = 90


def built(home: pathlib.Path, stem: str, rows: "list[str]"):
    fixtures.write(home, f"{stem}.csv", "code\n" + "\n".join(rows) + "\n")
    table = reading.read_table(
        str(home / f"{stem}.csv"), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(table, taxonomy.Settings(), [])
    return document, contract.load_profile(
        str(fixtures.write_profile(home, f"{stem}-p.json", document))
    )


def too_wide(cells: "list[str]", rows: "list[str]") -> int:
    """How many twin cells are WIDER before the point than any source cell.

    The claim R-P4-56 makes, and no more than it. A column running from
    0.0 to 149.0 legitimately holds cells of one, two and three figures,
    so "every cell wears the widest shape" is the wrong test and an
    earlier version of this driver used it -- it reported every cell of
    every column as off-shape, which is what a test measuring the wrong
    property looks like when it is measuring nothing.
    """
    widest = max(len(row.split(".")[0].lstrip("-")) for row in rows)
    return sum(
        1
        for cell in cells
        if len(cell.split(".")[0].lstrip("-")) > widest
    )


def main() -> None:
    random.seed(20260830)
    shapes = []
    for _trial in range(COLUMNS):
        figures = random.choice([1, 1, 2])
        step = random.choice([1, 1.1, 0.5, 2.5])
        start = random.choice([0.0, 250.0, 1000.0])
        count = random.choice([40, 60, 99, 150])
        grid = [round(start + step * n, figures) for n in range(count)]
        rows = [
            ("%." + str(figures) + "f") % grid[n % len(grid)]
            for n in range(random.choice([120, 240]))
        ]
        shapes.append((figures, rows))

    kept = generation._apart_enough
    tried = refused = 0
    closer = further = 0
    moved_report = 0
    wide_off = wide_on = 0
    deviations_off = deviations_on = 0
    with tempfile.TemporaryDirectory() as folder:
        home = pathlib.Path(folder)
        for index, (figures, rows) in enumerate(shapes):
            try:
                document, loaded = built(home, f"s{index}", rows)
            except Exception:
                refused = refused + 1
                continue
            tried = tried + 1
            column = document["columns"][0]
            wanted = column.get("n_distinct_values")
            outcome = {}
            for label, rule in (("on", kept), ("off", lambda *a: a[-1])):
                generation._apart_enough = rule
                twin = generation.generate(loaded, 7)
                cells = [cell for cell in twin.columns[0] if cell != ""]
                outcome[label] = (
                    len({float(cell) for cell in cells}),
                    too_wide(cells, rows),
                    len(cells),
                    len(twin.deviations),
                    sum(1 for one in twin.approximations if not one.inside),
                )
            generation._apart_enough = kept
            on, off = outcome["on"], outcome["off"]
            if wanted is not None:
                near_on = abs(on[0] - wanted)
                near_off = abs(off[0] - wanted)
                if near_on < near_off:
                    closer = closer + 1
                elif near_on > near_off:
                    further = further + 1
            if on[3:] != off[3:]:
                moved_report = moved_report + 1
                print(
                    f"    column {index}: deviations/outside "
                    f"{off[3:]} -> {on[3:]}"
                )
            wide_off = wide_off + off[1]
            wide_on = wide_on + on[1]
            deviations_off = deviations_off + off[3]
            deviations_on = deviations_on + on[3]
            if on[1] or off[1]:
                print(
                    f"    column {index}: cells wider than any source cell, "
                    f"rule off {off[1]} -> rule on {on[1]}"
                )

    print(f"columns built: {tried}   refused: {refused}")
    print(f"  count of different numbers CLOSER to published: {closer}")
    print(f"  count of different numbers FURTHER from published: {further}")
    print(f"  columns where a deviation or an outside range moved: "
          f"{moved_report}")
    print(f"  CELLS wider before the point than any source cell: "
          f"{wide_off} with the rule off, {wide_on} with it on")
    print(f"  DEVIATIONS the twin filed against itself: "
          f"{deviations_off} off, {deviations_on} on")


if __name__ == "__main__":
    main()
