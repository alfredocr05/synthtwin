"""P4-D457 (lane ID-ROOM2), repair 1: the shapes its reviews measured at 20,000 rows, each through the command.

Each case writes a table of 20,000 rows (the owner's table floor), profiles it with nobody at the keyboard,
generates its twin at seed 0 and validates it, and counts the shape's column with this file's own linear
counter (a set of the real cells, their merged keys and the days they name; each twin cell read once).
Each is red on 18b17a9c, the build head the reviews measured (wave6/ID-ROOM2/r1/probes.log):

* C1 (BATCH 4n OWES 10; LANE ID-ROOM2 RULINGS 2): sequential keys with a constant prefix and suffix, each
  once, were read as affixed numbers, asked nothing, and written real (19,998 of 20,000 twin cells);
* skeptic 1's item 1: a held column of `dd-Mon-yyyy` births of 1930 to 1999 and `dd-Mon-yy` births of 2000
  to 2025 wrote two-figure made-up dates naming a real birth date (2,335 of 5,903 two-figure cells), and a
  real two-figure year meets a four-figure made-up one the other way;
* Codex's item 1: a held column of dates beside hourly stamps wrote no cell that parses (0 of 20,000);
* Codex's item 3: twelve month-first birth dates in three withheld layouts were left unreadable;
* Codex's item 2 and skeptic 1's item 2: 1,000 different month-first dates kept 864, and ten years of
  dates published too few years for their count, so validation missed it.
"""

from __future__ import annotations

import contextlib
import csv
import datetime
import io
import json
import pathlib
import random
import re

import pytest

from synthtwin import cli, parsing

import unanswered_identifier_shapes as held_shapes

ROWS = 20_000
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
# The forms a twin cell is read in: four-figure years as written, two-figure years in both centuries.
FOUR = ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%d-%b-%Y", "%Y-%m-%dT%H:%M:%S")
TWO = ("%m/%d/%y", "%d/%m/%y", "%d-%b-%y")


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


def _between(draw: random.Random, first: int, last: int) -> datetime.date:
    return datetime.date.fromordinal(
        draw.randint(datetime.date(first, 1, 1).toordinal(), datetime.date(last, 12, 31).toordinal())
    )


def _run(folder: pathlib.Path, column: str, cells: "list[str]", typed: "list[str]") -> "dict[str, object]":
    """Profile with nobody at the keyboard, generate at seed 0, validate; the column's block, twin and counts."""
    draw = random.Random(3)
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "t.csv"
    with open(table, "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow([column, "test", "value"])
        for cell in cells:
            writer.writerow([cell, ("Sodium", "Chloride", "Urea")[draw.randrange(3)], f"{draw.uniform(2, 140):.1f}"])
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
    block = [one for one in document["columns"] if one["name"] == column][0]
    with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
        written = list(csv.DictReader(handle))
    twin = [one[column] for one in written]
    real = {cell for cell in cells if cell.strip()}
    merged = {parsing.merged_key(cell) for cell in real}
    days: "set[datetime.date]" = set()
    for cell in real:
        days |= _days(cell)
    texts = {}
    for path in sorted(folder.iterdir()):
        if path.is_file() and path.name not in ("t.csv", "t-twin.csv"):
            texts[path.name] = path.read_text(encoding="utf-8", errors="replace")
    return {
        "exits": (profiled, generated, validated),
        "block": block,
        "twin": twin,
        "equal": sum(1 for cell in twin if cell in real),
        "merged": sum(1 for cell in twin if parsing.merged_key(cell) in merged),
        "same_day": sum(1 for cell in twin if _days(cell) & days),
        "dated": sum(1 for cell in twin if _days(cell)),
        "texts": texts,
    }


@pytest.mark.parametrize("rows", [ROWS, 600])
def test_c1_keys_with_a_prefix_and_a_suffix_are_asked_and_held(tmp_path: pathlib.Path, rows: int) -> None:
    """C1: `P200000Q4444` upward, each once, is asked as the same keys bare or prefixed are, and the unattended
    reading holds it: 0 real keys in the twin, none of their figures in any written file. 19,998 real on
    18b17a9c at 20,000 rows (598 at 600 rows, a test size the command refuses). Mutant: the affixed reading
    not read between its affixes (`_a_whole_number_between_affixes`).
    """
    cells = [f"P{200000 + place}Q4444" for place in range(rows)]
    seen = _run(tmp_path, "ref", cells, [])
    assert seen["exits"] == (0, 0, 0)
    asked = json.loads(seen["texts"]["t-questions.json"])  # type: ignore[index]
    entry = [one for one in asked["asked"] if one.get("column") == "ref"]
    assert len(entry) == 1 and "every one is different" in entry[0]["what_synthtwin_saw"], entry
    assert "identifier" in [offer["answer"] for offer in entry[0]["answers_you_can_give"]]
    assert seen["block"]["role"] == "identifier"  # type: ignore[index]
    assert seen["equal"] == 0 and seen["merged"] == 0
    runs = set()
    for name, text in seen["texts"].items():  # type: ignore[attr-defined]
        if name != "t-questions.json":
            runs |= set(re.findall(r"(?<![0-9.])[0-9]{5,}(?![0-9])", text))
    assert not any(f"{200000 + place}" in runs for place in range(rows))


def _both_widths(draw: random.Random, place: int, reverse: bool) -> str:
    """A birth date of skeptic 1's variant B: `dd-Mon-yyyy` of 1930 to 1999, or `dd-Mon-yy` of 2000 to 2025."""
    if draw.random() < 0.7:
        day = _between(draw, 1930, 1999)
        return f"{day.day:02d}-{MONTHS[day.month - 1]}-{day.year}"
    day = _between(draw, 2000, 2025)
    if reverse and place % 50 == 0:
        day = datetime.date(2045, day.month, min(day.day, 28))
    return f"{day.day:02d}-{MONTHS[day.month - 1]}-{day.year % 100:02d}"


def test_skeptic_1_item_1_no_made_up_day_is_a_real_one_with_the_other_year_width(tmp_path: pathlib.Path) -> None:
    """Variant B: no twin cell names a real birth day, two-figure years read in both centuries (2,335 on
    18b17a9c); the two-figure kind finds no room (its cells are record numbers), the four-figure kind keeps
    its block from 2028. Mutant: the cross readings dropped in `taxonomy.with_made_up_years`.
    """
    draw = random.Random(7)
    cells = [_both_widths(draw, place, False) for place in range(ROWS)]
    seen = _run(tmp_path, "dob", cells, ["--identifier", "dob"])
    assert seen["exits"][0:2] == (0, 0)
    assert seen["equal"] == 0 and seen["merged"] == 0 and seen["same_day"] == 0, seen["same_day"]
    years = seen["block"]["made_up_years"]  # type: ignore[index]
    assert years and all(first >= 2028 for first, _last in years), years


def test_skeptic_1_item_1_the_reverse_direction(tmp_path: pathlib.Path) -> None:
    """A real `13-Mar-45` (2045 read by `%y`) beside the four-figure births: no four-figure made-up date names it.
    The two-figure year 45 holds 2045 for the four-figure kind, whose block from 2028 reaches it, so that kind
    has no room either. Mutant: the cross readings dropped.
    """
    draw = random.Random(7)
    cells = [_both_widths(draw, place, True) for place in range(ROWS)]
    seen = _run(tmp_path, "dob", cells, ["--identifier", "dob"])
    assert seen["exits"][0:2] == (0, 0)
    assert seen["equal"] == 0 and seen["merged"] == 0 and seen["same_day"] == 0, seen["same_day"]
    assert seen["block"]["made_up_years"] == []  # type: ignore[index]


def test_codex_item_1_a_held_column_of_stamps_stays_readable(tmp_path: pathlib.Path) -> None:
    """600 values from 1900 cycled, every fiftieth an ISO date, the others hourly ISO stamps: every twin cell
    parses (0 of 20,000 on 18b17a9c). Since lane TR (its skeptic 1, item 1; plan P4-D473) a held column read as
    stamps takes the block of four-figure years its dates would -- four here, its dates beside its stamps a day
    each -- and its G1 floor draws each made-up stamp's calendar date from it (`generation._stamp_in_the_room`),
    so the twin stays readable and names no real day. Mutant: the grain's reading not looked at.
    """
    values = []
    start = datetime.datetime(1900, 1, 1)
    for place in range(600):
        at = start + datetime.timedelta(hours=37 * place)
        values += [at.date().isoformat() if place % 50 == 0 else at.strftime("%Y-%m-%dT%H:%M:%S")]
    seen = _run(tmp_path, "dob", [values[place % 600] for place in range(ROWS)], [])
    assert seen["exits"][0:2] == (0, 0)
    assert seen["block"]["made_up_years"] == [[2028, 2031]]  # type: ignore[index]
    assert seen["dated"] == ROWS, seen["dated"]
    assert seen["equal"] == 0 and seen["merged"] == 0 and seen["same_day"] == 0


def test_codex_item_3_a_withheld_layout_is_written_as_a_date(tmp_path: pathlib.Path) -> None:
    """Month-first birth dates, padded, beside four each of `M/D/YYYY`, `M/DD/YYYY` and `MM/D/YYYY`: the census
    withholds the twelve, and every twin cell is a valid month-first date (12 unreadable on 18b17a9c), none
    real. Mutant: the main layout's fallback dropped from the G1 floor.
    """
    draw = random.Random(7)
    cells = []
    for place in range(ROWS):
        if place < 4:
            cells += [f"3/7/{1931 + place}"]
        elif place < 8:
            cells += [f"4/17/{1941 + place}"]
        elif place < 12:
            cells += [f"11/5/{1951 + place}"]
        else:
            cells += [_between(draw, 1925, 1999).strftime("%m/%d/%Y")]
    seen = _run(tmp_path, "dob", cells, [])
    assert seen["exits"][0:2] == (0, 0)
    twin = seen["twin"]
    assert isinstance(twin, list)
    unread = [cell for cell in twin if not _days(cell)]
    assert unread == [], unread[:5]
    assert seen["equal"] == 0 and seen["merged"] == 0 and seen["same_day"] == 0


def test_codex_item_2_a_thousand_dates_keep_a_thousand(tmp_path: pathlib.Path) -> None:
    """1,000 different month-first dates from 1920, twenty rows each: the twin keeps 1,000 (864 on 18b17a9c).
    Mutant: the block sized at 366 dates a year.
    """
    first = datetime.date(1920, 1, 1).toordinal()
    dates = [datetime.date.fromordinal(first + 9 * place).strftime("%m/%d/%Y") for place in range(1000)]
    cells = [dates[place % 1000] for place in range(ROWS)]
    random.Random(7).shuffle(cells)
    seen = _run(tmp_path, "dob", cells, ["--identifier", "dob"])
    assert seen["exits"] == (0, 0, 0)
    assert len(set(seen["twin"])) == 1000  # type: ignore[arg-type]
    assert seen["equal"] == 0 and seen["merged"] == 0 and seen["same_day"] == 0


def test_skeptic_1_item_2_ten_years_of_dates_validate(tmp_path: pathlib.Path) -> None:
    """A held `%m/%d/%Y` column of dates over 2015 to 2024 (3,6xx different): it validates, exit 0, keeping every
    different date (validate exited 3 on 18b17a9c: 20 years of 144 dates held 2,880). Mutant: as above.
    """
    draw = random.Random(7)
    cells = [_between(draw, 2015, 2024).strftime("%m/%d/%Y") for _place in range(ROWS)]
    seen = _run(tmp_path, "dob", cells, ["--identifier", "dob"])
    assert seen["exits"] == (0, 0, 0)
    assert len(set(seen["twin"])) == len(set(cells))  # type: ignore[arg-type]
    assert seen["equal"] == 0 and seen["merged"] == 0
