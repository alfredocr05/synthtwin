"""R-P4-151: does a twin of a compound column keep its own role?

A `numbers_with_labels` column sitting near the rule's detection line
had a twin that often came back as a different role, because the
numeric machinery reached about nine tenths of a published count of
different values. Amendment A-P4-55 made that count an OBLIGATION. The
owner's answer to the residual was "fold it into A-P4-55 and
re-measure", so this is the re-measurement.

**Run it with the tree to measure as its first argument**, so the SAME
file measures the tree before that landing and the tree after it.

THE LINE IS NOT ELEVEN, and finding that out is half of what this file
records. The residual was written as though the numeric half had to
clear the long-tail line; rule 7b also refuses a half whose count of
different numbers is at or below the CATEGORICAL CEILING, which is
thirty on a table of three hundred rows. So a half holding eleven
different numbers never reaches this role at all, and the counts worth
measuring are the ones just above the ceiling.

Nothing here is stubbed: the real reader, producer, loader, generator
and renderer, and the twin described again by the same producer.
"""
import csv
import io
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(
    sys.argv[1] if len(sys.argv) > 1
    else pathlib.Path(__file__).resolve().parents[2]
)
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import fixtures  # noqa: E402
from synthtwin import (  # noqa: E402
    contract, generation, profile, reading, rendering, taxonomy,
)

SEEDS = tuple(range(40))
ROLE = "numbers_with_labels"


def column(distinct, rows=300):
    """One marker word among numbers that cycle through `distinct` values."""
    return [
        "NOT DETECTED" if index % 15 == 7
        else f"{(index % distinct) + 1}.5"
        for index in range(rows)
    ]


def described(folder, name, rows, floor):
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["reading"])
    for row in rows:
        writer.writerow([row])
    path = fixtures.write(folder, f"{name}.csv", out.getvalue())
    table = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(
        table, taxonomy.Settings(small_cell_floor=floor), [], [], []
    )
    loaded = contract.load_profile(
        str(fixtures.write_profile(folder, f"{name}.json", document))
    )
    return document, loaded


def main():
    print(f"===== R-P4-151, {len(SEEDS)} seeds, 300 rows, floor 1 =====")
    print("A numeric half of N different numbers beside one marker word.")
    print()
    print(f"{'N':>4} {'source role':>21} {'twin keeps it':>14}   the rest")
    with tempfile.TemporaryDirectory() as home:
        folder = pathlib.Path(home)
        for distinct in (29, 30, 31, 32, 33, 35, 40, 50, 97):
            rows = column(distinct)
            document, loaded = described(
                folder, f"line-{distinct}", rows, 1
            )
            role = document["columns"][0]["role"]
            if role != ROLE:
                print(f"{distinct:>4} {role:>21}   (does not reach the role)")
                continue
            kept = 0
            others = {}
            for seed in SEEDS:
                twin = generation.generate(loaded, seed)
                text = fixtures.write(
                    folder, "twin.csv", rendering.twin_csv(twin)
                )
                again = profile.build_document(
                    reading.read_table(
                        f"{text}", first_row=reading.FIRST_ROW_AUTOMATIC
                    ),
                    taxonomy.Settings(small_cell_floor=1), [], [], [],
                )["columns"][0]["role"]
                if again == ROLE:
                    kept = kept + 1
                else:
                    others[again] = others.get(again, 0) + 1
            print(
                f"{distinct:>4} {role:>21} {kept:>10} of {len(SEEDS)}"
                f"   {others or ''}"
            )


if __name__ == "__main__":
    main()
