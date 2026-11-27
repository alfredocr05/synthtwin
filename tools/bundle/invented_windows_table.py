#!/usr/bin/env python3
"""Write the seeded invented tables the Windows rehearsal runs synthtwin on.

Plan P4-D483 (lane WIN of the December plan). The Windows rehearsal of
the ready folder and of the backup bundle (the workflow file
windows-bundle.yml in the repository's workflow folder) runs synthtwin
on two tables written here at run time; nothing written here is ever
committed. Both hold the same 20,000 rows, 1,000 invented people with
20 visits each -- the table floor `synthtwin profile` holds to (plan
P4-D425) -- written as a spreadsheet program on Windows writes a table
it saves as text:

    visits.csv        "CSV UTF-8": a byte-order mark, then UTF-8, every
                      line ended by a carriage return and a line feed
    visits-1252.csv   "CSV (Comma delimited)": Windows-1252, the same
                      line ends, the two labels Windows-1252 cannot hold
                      written in plain letters

The columns: `subject_id` (the person, S00001 to S01000), `visit_date`
written month/day/year without leading zeros, `age` in whole years (a
few people past 89), `weight` written with its unit (`72.4 kg`), `group`
(one label a person, two of them holding characters outside
Windows-1252 -- the one-character greater-or-equal sign and a Greek
beta -- and two holding characters inside it, a typographic apostrophe
and an accented e), `code` written with leading zeros, and `result`, a
measurement with one figure after the point and `NA` where it is
missing. Every value is drawn with whole numbers from one seeded stream,
so both files are the same bytes on every system and every Python:

    python tools/bundle/invented_windows_table.py FOLDER
"""

import csv
import datetime
import pathlib
import random
import sys

UTF8_NAME = "visits.csv"
CP1252_NAME = "visits-1252.csv"
PEOPLE = 1000
VISITS = 20
HEADER = ("subject_id", "visit_date", "age", "weight", "group", "code", "result")
# The labels, one a person. The first two hold characters Windows-1252
# has no byte for (U+2265 and U+03B2); the next two hold characters it
# has (U+2019 and U+00E9); the last two are plain letters.
GROUPS = (
    "≥ 65 years",
    "β-blocker",
    "Crohn’s disease",
    "café au lait",
    "asthma",
    "diabetes",
)
# How the Windows-1252 copy writes the two labels it cannot hold.
PLAIN = {"≥ 65 years": ">= 65 years", "β-blocker": "beta-blocker"}
CODES = tuple(f"{number:05d}" for number in (17, 42, 108, 230, 311, 425, 512, 640, 777, 901))
FIRST_DAY = datetime.date(2021, 1, 4)


def rows(seed: int = 20261111) -> "list[tuple[str, ...]]":
    """The 20,000 rows, the same on every system: whole numbers only."""
    rng = random.Random(seed)
    made: "list[tuple[str, ...]]" = []
    for person in range(1, PEOPLE + 1):
        group = GROUPS[rng.randrange(len(GROUPS))]
        # A few people past 89, so the Safe Harbor question about ages is put.
        age = rng.randint(90, 97) if rng.randrange(40) == 0 else rng.randint(18, 84)
        weight_tenths = rng.randint(480, 1150)
        day = FIRST_DAY + datetime.timedelta(days=rng.randrange(400))
        for _ in range(VISITS):
            day = day + datetime.timedelta(days=rng.randint(7, 70))
            weight_tenths = max(400, weight_tenths + rng.randint(-15, 15))
            reading = rng.randint(45, 120)
            made.append(
                (
                    f"S{person:05d}",
                    f"{day.month}/{day.day}/{day.year}",
                    str(age + (day.year - FIRST_DAY.year) // 2),
                    f"{weight_tenths // 10}.{weight_tenths % 10} kg",
                    group,
                    CODES[rng.randrange(len(CODES))],
                    "NA" if rng.randrange(10) == 0 else f"{reading // 10}.{reading % 10}",
                )
            )
    return made


def write(folder: pathlib.Path) -> "tuple[pathlib.Path, pathlib.Path]":
    """Write both tables into ``folder`` (made if missing); return their paths."""
    folder.mkdir(parents=True, exist_ok=True)
    table = rows()
    utf8 = folder / UTF8_NAME
    cp1252 = folder / CP1252_NAME
    with open(utf8, "w", encoding="utf-8-sig", newline="") as handle:
        out = csv.writer(handle, lineterminator="\r\n")
        out.writerow(HEADER)
        out.writerows(table)
    with open(cp1252, "w", encoding="cp1252", newline="") as handle:
        out = csv.writer(handle, lineterminator="\r\n")
        out.writerow(HEADER)
        out.writerows(tuple(PLAIN.get(cell, cell) for cell in row) for row in table)
    return utf8, cp1252


def main(argv: "list[str] | None" = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != 1:
        print("Give the folder to write into: python tools/bundle/invented_windows_table.py FOLDER")
        return 2
    for path in write(pathlib.Path(arguments[0])):
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
