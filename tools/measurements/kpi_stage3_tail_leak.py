"""K-S3-01: nothing a date or clock column publishes names one of its outer cells.

STAGE 3'S OWN GATE (plan P4-D328). A column of dates or clock times used
to publish its two ENDS -- the smallest value and the largest, each held
by as few as one row -- and every rung of its ladder, the two outermost
among them. This landing replaced them with two TAILS: a boundary, the
count of rows beyond it and how far they stand, or the values a tail
holds where publishing them settles no count below the floor. The thing
that must now be true, and that this driver measures, is that NOTHING
the description or either report says names one of the `k` outermost
cells of the column, `k` the smallest group size.

THREE MEASUREMENTS, over one battery:

* `literal`: how many published values, summary lines or report lines are
  equal, as text, to one of the `k` outermost values of the real column.
  Taken over every string the description holds at any depth, and over
  every line of the twin's report, the twin's quality report and the real
  table's quality report, by whole-token comparison so that a line
  carrying a value inside a sentence is caught;
* `pinned`: how many tails the published facts SETTLE -- the back-solve
  of contract TL1's own lattice, `taxonomy.tail_pinned`, asked of each
  published tail: whether the rows, the mean and the root-mean-square
  distance leave exactly one multiset of distances, which would name the
  outermost value, or exactly one count for some distance, which would
  name a count the floor protects;
* `window`: the construction window's own population, as a CEILING rather
  than a target. For each shape-drawn tail it is how many different
  multisets of distances the published facts admit inside G12.14's two
  ends -- counted by the same lattice walk, stopped at its budget -- and
  the smallest such population over the battery is reported. A population
  of one IS a pinned tail, so this number is the distance between the
  battery's tightest tail and a leak.

THE BATTERY is the seventeen shapes of the tail design and the eight the
skeptic of that design added, each at the sizes and seeds the design
names: 64 cases in all, at a floor of eleven, each through the real
producer, generator and checker. Every case also asserts that neither the
twin nor the real table misses a checkable obligation, so a zero here
cannot be bought by a description that says nothing.

    .venv/bin/python tools/measurements/kpi_stage3_tail_leak.py --kpi
"""

import datetime
import io
import pathlib
import random
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))
import kpi_rules  # noqa: E402
from synthtwin import (  # noqa: E402
    canonical,
    contract,
    quality,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    summary,
    taxonomy,
    validation,
)

kpi_rules.guard_this_tree()

FLOOR = 11
SEEDS = (0, 4, 11)


def _days(first, last):
    return [first + datetime.timedelta(days=step) for step in range((last - first).days + 1)]


def uniform(draw, rows):
    first = datetime.date(2021, 1, 1)
    return "when", [
        (first + datetime.timedelta(days=draw.randrange(3 * 365))).isoformat()
        for _ in range(rows)
    ], []


def admissions(draw, rows):
    accept = (1.0, 0.9, 0.9, 0.9, 0.85, 0.3, 0.25)
    pool = _days(datetime.date(2023, 1, 1), datetime.date(2024, 12, 31))
    weights = [accept[day.weekday()] for day in pool]
    onsets = (
        datetime.date(2023, 2, 3),
        datetime.date(2023, 11, 19),
        datetime.date(2024, 9, 7),
    )
    out = []
    for _ in range(rows):
        if draw.random() < 0.4:
            day = draw.choice(onsets) + datetime.timedelta(
                days=int(abs(draw.gauss(0, 4)))
            )
        else:
            day = draw.choices(pool, weights=weights, k=1)[0]
        out += [day.isoformat()]
    return "admitted", out, []


def births(draw, rows):
    out = []
    for _ in range(rows):
        year = int(min(2005, max(1925, draw.gauss(1962, 15))))
        roll = draw.random()
        if roll < 0.30:
            day = datetime.date(year, 1, 1)
        elif roll < 0.40:
            day = datetime.date(year, 7, 1)
        else:
            day = datetime.date(year, 1, 1) + datetime.timedelta(
                days=draw.randrange(365)
            )
        out += [f"{day.day:02d}/{day.month:02d}/{day.year:04d}"]
    return "born", out, ["--day-first"]


def offsets(draw, rows):
    out = []
    first = datetime.datetime(2022, 1, 1)
    for _ in range(rows):
        moment = first + datetime.timedelta(seconds=draw.randrange(2 * 365 * 86400))
        if draw.random() < 0.15:
            out += [moment.strftime("%Y-%m-%dT%H:%M:%S") + "Z"]
            continue
        out += [
            moment.strftime("%Y-%m-%dT%H:%M:%S")
            + ("+02:00" if 4 <= moment.month <= 9 else "+01:00")
        ]
    return "stamp", out, []


def minutes(draw, rows):
    first = datetime.datetime(2023, 1, 1)
    return "stamp", [
        (first + datetime.timedelta(minutes=draw.randrange(365 * 1440))).strftime(
            "%Y-%m-%d %H:%M"
        )
        for _ in range(rows)
    ], []


def clock_evening(draw, rows):
    out = []
    for _ in range(rows):
        if draw.random() < 0.7:
            minute = int(round(draw.gauss(17 * 60, 90)))
        else:
            minute = draw.randrange(6 * 60, 24 * 60)
        minute = min(1439, max(0, minute))
        out += [f"{minute // 60:02d}:{minute % 60:02d}"]
    return "arrived_at", out, []


def clock_seconds(draw, rows):
    out = []
    for _ in range(rows):
        second = int(min(86399, max(0, draw.gauss(17 * 3600, 5400))))
        out += [
            f"{second // 3600:02d}:{second % 3600 // 60:02d}:{second % 60:02d}"
        ]
    return "arrived_at", out, []


def midnight(draw, rows):
    first = datetime.date(2022, 1, 1)
    return "seen", [
        (first + datetime.timedelta(days=draw.randrange(730))).isoformat()
        + " 00:00:00"
        for _ in range(rows)
    ], []


def heap(draw, rows):
    first = datetime.date(2022, 1, 1)
    out = [
        (first + datetime.timedelta(days=draw.randrange(0, 60))).isoformat()
        for _ in range(10)
    ]
    out += ["2022-03-15"] * 30
    out += [
        (datetime.date(2022, 3, 16) + datetime.timedelta(days=draw.randrange(600))).isoformat()
        for _ in range(rows - 40)
    ]
    return "when", out, []


def lone_far(draw, rows):
    first = datetime.date(2022, 1, 1)
    out = [
        (first + datetime.timedelta(days=draw.randrange(730))).isoformat()
        for _ in range(rows - 2)
    ]
    return "when", out + ["2015-06-01", "2031-02-01"], []


def cet_midnight(draw, rows):
    first = datetime.date(2022, 1, 1)
    out = []
    for _ in range(rows):
        day = first + datetime.timedelta(days=draw.randrange(730))
        out += [
            day.isoformat()
            + "T00:00:00"
            + ("+02:00" if 4 <= day.month <= 9 else "+01:00")
        ]
    return "seen", out, []


def part_midnight(draw, rows):
    first = datetime.datetime(2022, 1, 1)
    out = []
    for _ in range(rows):
        day = first + datetime.timedelta(days=draw.randrange(730))
        if draw.random() < 0.7:
            out += [day.strftime("%Y-%m-%d") + " 00:00:00"]
        else:
            out += [
                (day + datetime.timedelta(seconds=draw.randrange(1, 86400))).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ]
    return "seen", out, []


def months(draw, rows):
    out = []
    for _ in range(rows):
        month = min(119, max(0, int(draw.gauss(60, 24))))
        out += [f"{2015 + month // 12:04d}-{month % 12 + 1:02d}"]
    return "period", out, []


def quarters(draw, rows):
    out = []
    for _ in range(rows):
        quarter = draw.randrange(0, 120)
        out += [f"{1995 + quarter // 4:04d}-Q{quarter % 4 + 1}"]
    return "period", out, []


def textual(draw, rows):
    names = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP",
             "OCT", "NOV", "DEC")
    first = datetime.date(2020, 1, 1)
    out = []
    for _ in range(rows):
        day = first + datetime.timedelta(days=draw.randrange(900))
        out += [f"{day.day:02d}-{names[day.month - 1]}-{day.year:04d}"]
    return "when", out, []


def pivot(draw, rows):
    """Two-figure years reaching the 1969 edge of the readable window."""
    out = []
    for _ in range(rows):
        year = int(min(2005, max(1969, draw.gauss(1975, 8))))
        day = datetime.date(year, 1, 1) + datetime.timedelta(
            days=draw.randrange(365)
        )
        out += [f"{day.day:02d}/{day.month:02d}/{day.year % 100:02d}"]
    return "born", out, ["--day-first"]


def dotnet_minimum(draw, rows):
    """Forty cells on the `0001-01-01` a common system writes for no date."""
    first = datetime.datetime(2020, 1, 1)
    out = ["0001-01-01 00:00:00"] * 40
    for _ in range(rows - 40):
        out += [
            (first + datetime.timedelta(seconds=draw.randrange(3 * 365 * 86400))).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ]
    return "stamp", out, []


def midnight_heap(draw, rows):
    """A heap at one midnight, with a tenth of the column off midnight."""
    first = datetime.date(2021, 6, 1)
    out = [
        (first + datetime.timedelta(days=draw.randrange(100))).strftime("%Y-%m-%d")
        + " 00:00:00"
        for _ in range(5)
    ]
    out += ["2022-01-01 00:00:00"] * 30
    for _ in range(rows - 35):
        day = datetime.date(2022, 1, 2) + datetime.timedelta(
            days=draw.randrange(700)
        )
        if draw.random() < 0.90:
            out += [day.strftime("%Y-%m-%d") + " 00:00:00"]
        else:
            out += [
                day.strftime("%Y-%m-%d")
                + f" {draw.randrange(1, 24):02d}:{draw.randrange(60):02d}"
                f":{draw.randrange(60):02d}"
            ]
    return "seen", out, []


def clock_all_different(draw, rows):
    return "at", [
        f"{minute // 60:02d}:{minute % 60:02d}"
        for minute in draw.sample(range(1440), rows)
    ], []


def clock_edges(draw, rows):
    """All-different minutes whose tails reach `00:00` and `23:59`."""
    picks = draw.sample(range(1440), rows)
    picks = list(dict.fromkeys(picks[: rows - 2] + [0, 1439]))
    while len(picks) < rows:
        extra = draw.randrange(1440)
        if extra not in picks:
            picks += [extra]
    return "at", [f"{minute // 60:02d}:{minute % 60:02d}" for minute in picks], []


def sparse(draw, rows):
    """A date present in fifteen rows of the column and absent in the rest."""
    first = datetime.date(2021, 1, 1)
    present = set(draw.sample(range(rows), 15))
    out = []
    for place in range(rows):
        if place in present:
            out += [
                (first + datetime.timedelta(days=draw.randrange(700))).isoformat()
            ]
        else:
            out += [""]
    return "died", out, []


# The seventeen shapes of the design, then the eight the skeptic added.
SHAPES = {
    "uniform": uniform,
    "admissions": admissions,
    "births": births,
    "offsets": offsets,
    "minutes": minutes,
    "clock_evening": clock_evening,
    "clock_seconds": clock_seconds,
    "midnight": midnight,
    "heap": heap,
    "lone_far": lone_far,
    "cet_midnight": cet_midnight,
    "part_midnight": part_midnight,
    "months": months,
    "quarters": quarters,
    "textual": textual,
    "clock_all_different": clock_all_different,
    "sparse": sparse,
    "pivot": pivot,
    "dotnet_minimum": dotnet_minimum,
    "midnight_heap": midnight_heap,
    "clock_edges": clock_edges,
}

# Which sizes each shape is run at. The clock shapes stay inside the
# day's own capacity, and the two heaps need room for their heap.
SIZES = {
    "clock_all_different": (400, 900),
    "clock_edges": (400, 900),
    "sparse": (400, 1500),
    "dotnet_minimum": (400, 1500),
    "midnight_heap": (400, 1500),
    "pivot": (400, 1500),
}
DEFAULT_SIZES = (400, 1500)


def _table(name, cells):
    out = io.StringIO()
    out.write(name + "\n")
    for cell in cells:
        # An absent cell of a ONE-COLUMN table is written as two quotes,
        # which is how a blank line is told from a record whose one
        # value is missing.
        out.write(('""' if not cell else cell.replace(",", "")) + "\n")
    return out.getvalue()


def _outermost(cells, member, reading_at, floor):
    """The `floor` outermost values of a column that the floor protects.

    The cells at the two ends of the sorted column, less any value at
    least `floor` of its cells hold: a value that many rows share is one
    the owner's ruling of 2026-09-22 puts outside this measurement --
    "many people will be there and there is no big deal in knowing that
    it's there" -- and it reaches the ends only because the column is
    tied there, not because it is rare.
    """
    # ORDERED BY THE INSTANT EACH CELL NAMES, never by its text: a
    # column written `17-MAR-2021` sorts by month name as text, which
    # puts April before January and makes the ends of the column
    # something else entirely.
    parsed = []
    for cell in cells:
        if not cell:
            continue
        found = parsing.parse_datetime(cell, member)
        if found is None:
            continue
        instant = found[0]
        if reading_at == "utc":
            shifted = parsing.utc_canonical(found[0], found[1])
            if shifted is None:
                continue
            instant = shifted
        parsed += [(instant, cell)]
    if not parsed:
        return set()
    tally = {}
    for _instant, cell in parsed:
        tally[cell] = tally.get(cell, 0) + 1
    ordered = [cell for _instant, cell in sorted(parsed)]
    ends = set(ordered[:floor]) | set(ordered[-floor:])
    return {value for value in ends if tally[value] < floor}


def _strings(node):
    """Every string a loaded description holds, at any depth."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for key in node:
            yield from _strings(node[key])
    elif isinstance(node, list):
        for item in node:
            yield from _strings(item)


def _tokens(text):
    """The whole tokens of a line, so a value inside a sentence is caught."""
    found = []
    word = ""
    for letter in text:
        if letter.isalnum() or letter in "-:+./":
            word += letter
        else:
            if word:
                found += [word]
            word = ""
    if word:
        found += [word]
    return found


# How many multisets the back-solve is allowed to count before it stops
# and reports what it has, and how many steps it may take to get there.
# A tail whose facts admit this many is as far from pinned as the
# measurement can say, and the step budget is what keeps the walk a
# measurement rather than a search: what matters here is telling ONE
# from MANY, and the numbers below tell them apart with room to spare.
ROOM_LIMIT = 64
ROOM_STEPS = 200000


def _multisets(rows, total, squares, most, steps=None):
    """How many multisets of `rows` whole distances meet both sums, up to a cap.

    Written here rather than taken from the producer, because this is
    the measurement a READER could make with the published facts alone:
    the distances descend, each is at least one and at most the one
    before it, and the walk is cut by the two bounds a sum and a sum of
    squares give -- the even split below and the widest split above.
    """
    if steps is None:
        steps = [ROOM_STEPS]
    steps[0] -= 1
    if steps[0] <= 0:
        return ROOM_LIMIT
    if rows == 0:
        return 1 if total == 0 and squares == 0 else 0
    if total < rows or squares < total:
        return 0
    even, spare = divmod(total, rows)
    least = (rows - spare) * even * even + spare * (even + 1) * (even + 1)
    if squares < least:
        return 0
    top = min(most, total - (rows - 1))
    found = 0
    for first in range(top, 0, -1):
        if first * first > squares:
            continue
        found += _multisets(
            rows - 1, total - first, squares - first * first, first, steps
        )
        if found >= ROOM_LIMIT or steps[0] <= 0:
            return ROOM_LIMIT if found >= ROOM_LIMIT else found
    return found


def _pinned_and_room(block, floor):
    """How many of a block's tails the published facts settle, and the room left.

    The back-solve of contract TL1, made from the published facts alone:
    a tail whose rows, mean and root-mean-square distance leave exactly
    ONE multiset of distances names its outermost value, and the count of
    multisets is how much room a reader is left with.
    """
    pinned = 0
    room = None
    for side in ("low_tail", "high_tail"):
        tail = block.get(side)
        if not isinstance(tail, dict) or tail.get("rows") is None:
            continue
        if tail.get("values") is not None:
            continue
        mean = tail.get("mean_distance")
        root = tail.get("rms_distance")
        if mean is None or root is None:
            continue
        rows = tail["rows"]
        total = int(rows * mean + 0.5)
        squares = int(rows * root * root + 0.5)
        count = _multisets(rows, total, squares, total)
        pinned += 1 if count == 1 else 0
        room = count if room is None else min(room, count)
    return pinned, room


def _case(folder, shape, rows, seed):
    draw = random.Random(seed * 7919 + rows)
    name, cells, flags = SHAPES[shape](draw, rows)
    home = folder / f"{shape}-{rows}-{seed}"
    home.mkdir(parents=True, exist_ok=True)
    table = home / "real.csv"
    table.write_text(_table(name, cells), encoding="utf-8", newline="")
    read = reading.read_table(str(table), first_row=reading.FIRST_ROW_AUTOMATIC)
    settings = taxonomy.Settings(
        small_cell_floor=FLOOR, day_first="--day-first" in flags
    )
    document = profile.build_document(read, settings, [])
    written = home / "real-profile.json"
    # The producer's OWN serializer, which the loader re-writes with and
    # compares against: a description written any other way is refused.
    written.write_text(canonical.serialize(document), encoding="utf-8", newline="")
    described = contract.load_profile(str(written))
    block = document["columns"][0]
    member = block.get("format", "iso-date")
    outer = _outermost(cells, member, block.get("datetimes_read_at", "local"), FLOOR)
    twin = generation.generate(described, seed)
    twin_text = rendering.twin_csv(twin)
    twin_path = home / "twin.csv"
    twin_path.write_text(twin_text, encoding="utf-8", newline="")
    pages = [
        summary.render(document, ""),
        rendering.report(described, twin),
        quality.quality_report(
            described, validation.measure(described, str(twin_path))
        ),
        quality.quality_report(
            described, validation.measure(described, str(table))
        ),
    ]
    # WHAT A TAIL PUBLISHES ON PURPOSE IS NOT A LEAK (the owner's ruling
    # of 2026-09-22, plan P4-D329): a tail holding few different values
    # publishes them, existence only and never a count, and the report
    # may print what the description publishes. Every OTHER outer value
    # is what this counts -- in the description, in the summary and in
    # either report.
    allowed = set()
    listed = 0
    for side in ("low_tail", "high_tail"):
        tail = block.get(side)
        if isinstance(tail, dict) and tail.get("values"):
            listed += 1
            for value in tail["values"]:
                allowed.add(value)
    # ...AND NEITHER IS THE MEMBER'S OWN FIXED EXAMPLE. The detection
    # evidence shows what the column's spelling LOOKS like -- "dates
    # written as 2024-03" -- and that text is a constant of the member,
    # the same on every column read that way, chosen before any table
    # was seen. It coincides with a real cell of a shape that happens to
    # hold it, which is a coincidence and not a disclosure, so it is
    # taken out of the comparison rather than counted.
    for token in _tokens(parsing.format_example(member)):
        allowed.add(token)
    hidden = outer - allowed
    leaked = 0
    for value in _strings(document):
        if value in hidden:
            leaked += 1
    for page in pages:
        for line in page.splitlines():
            for token in _tokens(line):
                if token in hidden:
                    leaked += 1
    missed = 0
    for path in (twin_path, table):
        outcome = validation.measure(described, str(path))
        for check in outcome.checks:
            if check.verdict == validation.MISSED:
                missed += 1
    pinned, room = _pinned_and_room(block, FLOOR)
    return {
        "leaked": leaked,
        "missed": missed,
        "pinned": pinned,
        "room": room,
        "listed": listed,
    }


def main():
    total = {"cases": 0, "literal": 0, "pinned": 0, "missed": 0}
    room = None
    with tempfile.TemporaryDirectory() as folder:
        home = pathlib.Path(folder)
        for shape in SHAPES:
            for rows in SIZES.get(shape, DEFAULT_SIZES):
                for seed in SEEDS:
                    if seed == 11 and rows != 400:
                        continue
                    found = _case(home, shape, rows, seed)
                    total["cases"] += 1
                    total["literal"] += found["leaked"]
                    total["pinned"] += found["pinned"]
                    total["missed"] += found["missed"]
                    total["listed"] = total.get("listed", 0) + found["listed"]
                    if found["room"] is not None:
                        room = found["room"] if room is None else min(room, found["room"])
                    print(
                        f"{shape} {rows} seed {seed}: {found}", flush=True
                    )
    value = {
        "cases": total["cases"],
        "literal": total["literal"],
        "pinned": total["pinned"],
        "missed": total["missed"],
        "listed": total.get("listed", 0),
        "window": room if room is not None else 0,
    }
    kpi_rules.emit("K-S3-01", value)


if __name__ == "__main__":
    main()
