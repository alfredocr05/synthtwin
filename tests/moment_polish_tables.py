"""Invented tables for the twin meeting rule B (lane MPg, plan P4-D456): two nearly collinear pairs.

`collinear_text(rows, seed)` writes a table of an age, two pairs of
measurements built so that each pair's correlation on the chain's codes is
about 0.95 (`pa`, `pb`) and about 0.995 (`qa`, `qb`), a third measurement
blank on about one row in five that depends on the age and on `qa`, a
two-valued outcome that depends on the age and on `pa`, and a label. Every
reading lies far above 125, so no column reads as an age. Invented
numbers only; a health table can hold any of these shapes. K-S6-12
(`tools/measurements/kpi_moment_polish.py`) and the polish's gate read it.
"""

import math
import random

HEADER = ("age", "pa", "pb", "qa", "qb", "lab", "flag", "kind")


def collinear_rows(rows: int, seed: int) -> "list[list[str]]":
    """`rows` invented rows of `HEADER`, a fixed function of `seed`."""
    draw = random.Random(7919 * seed + 13)
    out: "list[list[str]]" = []
    for _row in range(rows):
        age = draw.randint(18, 89)
        pa = 300.0 + 1.5 * (age - 50) + draw.gauss(0.0, 30.0)
        pb = pa + draw.gauss(0.0, 10.5)
        qa = 500.0 + 2.0 * (age - 50) + draw.gauss(0.0, 40.0)
        qb = 0.9 * qa + 40.0 + draw.gauss(0.0, 3.4)
        lab = "" if draw.random() < 0.2 else f"{200.0 + 1.2 * age + 0.1 * (qa - 500.0) + draw.gauss(0.0, 20.0):.1f}"
        chance = 1.0 / (1.0 + math.exp(-(-4.0 + 0.04 * age + 0.01 * (pa - 300.0))))
        flag = "1" if draw.random() < chance else "0"
        kind = draw.choice("rst") if age < 55 else draw.choice("tu")
        out += [[f"{age}", f"{pa:.1f}", f"{pb:.1f}", f"{qa:.1f}", f"{qb:.1f}", lab, flag, kind]]
    return out


def collinear_text(rows: int, seed: int) -> str:
    """The table as a CSV file's text (`HEADER` first, one row a line, newline-ended)."""
    return ",".join(HEADER) + "\n" + "".join(",".join(row) + "\n" for row in collinear_rows(rows, seed))


def missing_beside_high_text(rows: int = 21000, seed: int = 5) -> str:
    """An invented pair whose second member is blank beside the high readings of the first, softly (lane MPg's repair 2).

    `x` about normal (mean 100, spread 15); `y` twice `x` plus noise;
    `y` blank where `x` plus noise passes 105, so the rows holding both
    hold the lower `x` and the pair's own spread of `x` (about 10.5) is
    well below its whole spread (15): a complete-case slope of `y` on `x`
    reads the pair's spreads (contract 4.6d.0). A three-level label `g`.
    """
    draw = random.Random(seed)
    lines = ["x,y,g"]
    for row in range(rows):
        x = draw.gauss(100.0, 15.0)
        y = 2.0 * x + draw.gauss(0.0, 10.0)
        blank = x + draw.gauss(0.0, 5.0) > 105.0
        lines += [f"{x:.1f},{'' if blank else f'{y:.1f}'},{'abc'[row % 3]}"]
    return "\n".join(lines) + "\n"


def blocks_text() -> str:
    """Codex's 21,000-row case (lane MPp's repair 2): `x` on 0 to 20 and 100 to 120, 500 rows a value; `y` equal to
    `x` beside the first block and blank beside the second; a three-level label `g`."""
    lines = ["x,y,g"]
    for block in (range(0, 21), range(100, 121)):
        for value in block:
            for place in range(500):
                lines += [f"{value},{value if block.start == 0 else ''},{'abc'[place % 3]}"]
    return "\n".join(lines) + "\n"
