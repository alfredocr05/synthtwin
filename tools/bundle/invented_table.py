#!/usr/bin/env python3
"""Write the seeded invented table CI's bundle-test job runs synthtwin on.

Plan P4-D416 (lane DEP-2): after the bundle is installed with the
network denied, the job profiles, generates and validates this table
with the installed synthtwin. Three columns -- a whole-number count, a
label and a measurement with one figure after the point -- 300 rows,
the same bytes on every system:

    python tools/bundle/invented_table.py TABLE.csv
"""

import csv
import random
import sys


def main(argv: "list[str] | None" = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != 1:
        print("Give the file to write: python tools/bundle/invented_table.py TABLE.csv")
        return 2
    rng = random.Random(20261021)
    with open(arguments[0], "w", newline="", encoding="utf-8") as handle:
        out = csv.writer(handle, lineterminator="\n")
        out.writerow(["age", "group", "pressure"])
        for _ in range(300):
            out.writerow(
                [rng.randint(20, 90), rng.choice("ABC"), f"{rng.gauss(120, 15):.1f}"]
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
