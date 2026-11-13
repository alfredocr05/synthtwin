"""P4-D457 (lane ID-ROOM2), repair 2: a pool of the other year width, at 20,000 rows, each through the command.

The verify of repair 1 (LANE ID-ROOM2 RULINGS 6 (1) and (2)) measured at 20,000 rows (the owner's table floor)
held birth-date columns whose census withholds a pool of layouts of the OTHER year width, and wrote the shapes
here: two-figure births of 2000 to 2025 beside twelve four-figure births of 1928 to 1937 in three withheld
layouts (F2), or four-figure births of 1930 to 1999 beside twelve two-figure ones of 1945 to 1960 (G2), each
held with `--identifier` (the date pass) and with nobody at the keyboard (the G1 floor, F2u and G2u), and a
pool past the two-figure block beside two-figure births of 2000 to 2025 (F3c). Each case profiles a table of a person key,
the birth dates and two other columns, generates its twin at seed 0, validates it, and counts the date column
with this file's own linear counter (the real cells, their merged keys and the days they name in sets, a
two-figure year read in both centuries; each twin cell read once).

On repair 1's head af60db46 the twin named real births the other width wrote: 20, 7, 9 and 6 cells (the
Safe Harbor 90-plus years among them); F2u, G2u and F3c failed validation (a withheld member written at the
room's width). Each case is red there and on the mutant its docstring names (wave6/ID-ROOM2/r2/mutants.log).
"""

from __future__ import annotations

import contextlib
import csv
import datetime
import io
import json
import pathlib
import random

from synthtwin import cli, parsing

import unanswered_identifier_shapes as held_shapes

ROWS = 20_000
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
FOUR = ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%d-%b-%Y", "%d %b %Y", "%Y%m%d")
TWO = ("%m/%d/%y", "%d/%m/%y", "%d-%b-%y", "%d %b %y")


def _days(cell: str) -> "set[datetime.date]":
    """Every day a cell names in an ordinary form, a two-figure year read in the 1900s and in the 2000s."""
    found: "set[datetime.date]" = set()
    for form in FOUR:
        try:
            found.add(datetime.datetime.strptime(cell, form).date())
        except ValueError:
            continue
    for form in TWO:
        try:
            read = datetime.datetime.strptime(cell, form)
        except ValueError:
            continue
        for century in (1900, 2000):
            try:
                found.add(datetime.date(century + read.year % 100, read.month, read.day))
            except ValueError:
                continue
    return found


def _day(draw: random.Random, first: int, last: int, top: int = 31) -> datetime.date:
    while True:
        found = datetime.date.fromordinal(
            draw.randint(datetime.date(first, 1, 1).toordinal(), datetime.date(last, 12, 31).toordinal())
        )
        if found.day <= top:
            return found


def _other_width(old: bool, first: int, last: int) -> "list[str]":
    """The verify's shapes: 19,988 births of one width, twelve of the other in three layouts, four each, shuffled."""
    draw = random.Random(11)
    few: "list[str]" = []
    for _place in range(4):
        for shape in range(3):
            day = _day(draw, first, last, 9 if shape == 1 else 28)
            year = f"{day.year}" if old else f"{day.year % 100:02d}"
            if shape == 0:
                few += [f"{day.day:02d}-{MONTHS[day.month - 1]}-{year}"]
            elif shape == 1:
                few += [f"{day.day}-{MONTHS[day.month - 1]}-{year}"]
            else:
                few += [f"{day.day:02d} {MONTHS[day.month - 1]} {year}"]
    main: "list[str]" = []
    for _place in range(ROWS - len(few)):
        day = _day(draw, 2000, 2025) if old else _day(draw, 1930, 1999)
        main += [f"{day.day:02d}-{MONTHS[day.month - 1]}-{day.year % 100:02d}" if old
                 else f"{day.day:02d}-{MONTHS[day.month - 1]}-{day.year}"]
    cells = main + few
    draw.shuffle(cells)
    return cells


def _run(folder: pathlib.Path, cells: "list[str]", typed: "list[str]") -> "dict[str, object]":
    """Profile (nobody at the keyboard), generate at seed 0, validate; the date column's block, twin and counts."""
    draw = random.Random(3)
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "t.csv"
    with open(table, "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["person_key", "dob", "group", "value"])
        for place, cell in enumerate(cells):
            writer.writerow([f"Q{700000 + place}", cell, draw.choice("MF"), 100 + draw.randrange(60)])
    screen = io.StringIO()
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        profiled = cli.main(["profile", f"{table}", "--out-dir", f"{folder}", "--replace"] + typed)
        generated = validated = -1
        if profiled == 0:
            generated = cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{folder}",
                                  "--seed", "0", "--replace"])
        if generated == 0:
            validated = cli.main(["validate", f"{folder / 't-profile.json'}", "--twin", f"{folder / 't-twin.csv'}",
                                  "--out-dir", f"{folder}", "--replace"])
    document = json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))
    block = [one for one in document["columns"] if one["name"] == "dob"][0]
    with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
        twin = [one["dob"] for one in csv.DictReader(handle)]
    real = {cell for cell in cells if cell.strip()}
    merged = {parsing.merged_key(cell) for cell in real}
    days: "set[datetime.date]" = set()
    for cell in real:
        days |= _days(cell)
    read: "dict[str, set[datetime.date]]" = {}
    for cell in set(twin):
        read[cell] = _days(cell)
    return {
        "exits": (profiled, generated, validated),
        "block": block,
        "twin": twin,
        "equal": sum(1 for cell in twin if cell in real),
        "merged": sum(1 for cell in twin if parsing.merged_key(cell) in merged),
        "same_day": sum(1 for cell in twin if read[cell] & days),
        "dated": sum(1 for cell in twin if read[cell]),
    }


def test_f2_a_withheld_pool_of_four_figure_births_typed(tmp_path: pathlib.Path) -> None:
    """F2 with `--identifier`: 20 twin cells named 7 of the 12 real four-figure births (1928 to 1937) on af60db46.
    Each cell is now read in its own layout's orders and the pool's years hold `28` to `37` for the two-figure
    kind (the cross rule), so its block from `28` is no room: 0 cells naming a real day; the price, the column's
    19,988 named cells written as record numbers (NF137). Mutants M14 (the own layout's orders not read) and M15
    (the cross rule only where both kinds are named).
    """
    seen = _run(tmp_path, _other_width(True, 1928, 1937), ["--identifier", "dob"])
    assert seen["exits"] == (0, 0, 0)
    assert seen["equal"] == 0 and seen["merged"] == 0 and seen["same_day"] == 0, seen["same_day"]
    assert seen["block"]["made_up_years"] == []  # type: ignore[index]


def test_g2_a_withheld_pool_of_two_figure_births_typed(tmp_path: pathlib.Path) -> None:
    """G2 with `--identifier`: 7 twin cells named 6 of the 12 real two-figure births (1945 to 1960) on af60db46.
    The pool's `45` to `60` hold 2045 to 2060 for the four-figure kind, so its block is no room: 0 cells naming a
    real day, the column's 19,988 named cells written as record numbers. Mutants M14 and M15.
    """
    seen = _run(tmp_path, _other_width(False, 1945, 1960), ["--identifier", "dob"])
    assert seen["exits"] == (0, 0, 0)
    assert seen["equal"] == 0 and seen["merged"] == 0 and seen["same_day"] == 0, seen["same_day"]
    assert seen["block"]["made_up_years"] == []  # type: ignore[index]


def test_f2u_the_g1_floor_names_no_real_birth_and_validates(tmp_path: pathlib.Path) -> None:
    """F2 with nobody at the keyboard (the G1 floor): 9 twin cells named real births and validation exited 3 on
    af60db46 (`max_length` 11 asked, 9 held: the withheld four-figure members written at the room's width). Now
    0 naming a real day, and it validates. Mutants M14, M15 and M17 (the withheld path's any length).
    """
    seen = _run(tmp_path, _other_width(True, 1928, 1937), [])
    assert seen["exits"] == (0, 0, 0)
    assert seen["block"]["role"] == "identifier"  # type: ignore[index]
    assert seen["equal"] == 0 and seen["merged"] == 0 and seen["same_day"] == 0, seen["same_day"]


def test_g2u_the_g1_floor_names_no_real_birth_and_validates(tmp_path: pathlib.Path) -> None:
    """G2 with nobody at the keyboard: 6 twin cells named real births and validation exited 3 on af60db46
    (`min_length` and `n_code_alphabet`). Now 0 naming a real day, and it validates. Mutants M14, M15 and M17.
    """
    seen = _run(tmp_path, _other_width(False, 1945, 1960), [])
    assert seen["exits"] == (0, 0, 0)
    assert seen["block"]["role"] == "identifier"  # type: ignore[index]
    assert seen["equal"] == 0 and seen["merged"] == 0 and seen["same_day"] == 0, seen["same_day"]


def test_f3c_a_pool_past_the_block_keeps_the_room_and_its_lengths(tmp_path: pathlib.Path) -> None:
    """The verify's further shape, the room surviving (LANE ID-ROOM2 RULINGS 6 (2)): two-figure births of 2000 to
    2025 beside a withheld pool of twelve four-figure births whose years' last two figures lie past the two-figure
    block -- of 1905 to 1925 -- with nobody at the keyboard, beside this gate's companion columns, where the census
    is named, as F2u's is. The pool's `05` to `25`, held for the two-figure kind, leave the block from `28` standing;
    the withheld four-figure members, no date of the room's kind being as long, keep the walk's values: 0 cells
    naming a real day, and it validates (exit 3 on af60db46: `max_length` 11 asked, 9 held). What names the census
    is not the pool's years or the Safe Harbor cut (the scoped verify of repair 2; LANE ID-ROOM2 RULINGS 7 (1)):
    held in people with its census withheld whole -- a rare layout held by too few people -- a column names no
    layout and publishes nothing, and its G1 floor draws from its grain's span whatever the pool's years: this pool
    and F2u's beside other companions (a two-level label alternating row by row, a measurement cycling with the
    row), 17,513 of 20,000 cells each equal to a real birth by chance, and the pool of 1980 to 1985 beside this
    gate's own companions 17,517, each exiting 3 in validation, as on the public head 2af926ce. These companions hid it;
    P4-D457 states it (owner lane ID-ROOM3). Mutant M17.
    """
    seen = _run(tmp_path, _other_width(True, 1905, 1925), [])
    assert seen["exits"] == (0, 0, 0)
    assert seen["equal"] == 0 and seen["merged"] == 0 and seen["same_day"] == 0, seen["same_day"]
    years = seen["block"]["made_up_years"]  # type: ignore[index]
    assert years and years[0][0] == 28 and years[-1][1] < 80, years
    assert seen["dated"] >= ROWS - 12, seen["dated"]
