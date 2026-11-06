"""The invented event table the rules gate `K-S6-06` is judged on (contract 4.6b.7, plan P4-D452).

Why a file of its own. `K-S6-06` was stated on the relationships draft's event table of 300 rows,
under the owner's table floor of 20,000 rows, so the product now refuses that table. This module
writes the same kinds of rule at the floor. Lanes RO, RD and RZ measure on it; no test of the page
runs the product on it.

Every number is a round figure chosen by hand, and no cell comes from a real table. It holds one
rule of each kind on every row:

- ORDER, with the source's own difference: `ended_on` is on or after `started_on`, and `days_open`
  is `ended_on - started_on` in whole days;
- ORDER, with no source difference: `closed_at` is on or after `opened_at`, stamps to the minute;
- FORMULA: `total` is `units x rate`;
- IMPOSSIBLE COMBINATION: `pregnant` is never `yes` where `gender` is `M`.

`keyed_rows` keys that many rows into the derived order (part (v): `closed_at` one to three days
before `opened_at`), and `binary_rates` writes the formula from binary64 (part (viii): rates not
exact in binary, `total` the shortest text of the binary product). Beside it, repair 1's fixtures:
`chain_rows` (part (vii), a chain of events and a date beside its own stamp), `ages_rows` (two
ages under the age top-code: no computed cell may pass 90), `person_rows` (several rows a person,
every failing row one person's) and `layout_rows` (one date written in two layouts). Repair 2's,
each a `K-S6-08` shape the page names in MR.12: `heap_rows` (a gap on nearly every row, a few rows
above it), `sum_rows` (a net amount written from binary64, the adjustment nearly cancelling the
charge), `exponent_rows` (a second number written in E-notation), `seconds_rows` (clocks to the
second beside the next minute written to the minute) and `day_end_rows` (clocks at the day's end
beside a source length in minutes, the sum held at the day's last minute).

Guarantee: the same arguments give the same text, on every platform, because the rows come from
`random.Random(seed)` and the text is joined with `\n`. Boundary: the standard library only.
"""
import datetime
import random

ROWS_AT_THE_FLOOR = 20000
SEED = 7
HEADER = (
    "subject_id",
    "started_on",
    "ended_on",
    "days_open",
    "opened_at",
    "closed_at",
    "units",
    "rate",
    "total",
    "gender",
    "pregnant",
    "age",
    "site",
)
_FIRST_DAY = datetime.date(2023, 1, 2)
_FIRST_STAMP = datetime.datetime(2023, 1, 2)
_RATES = ("12.50", "18.75", "22.00", "40.25", "64.50")
_BINARY_RATES = ("19.99", "7.15", "12.35", "0.10", "33.30")
_SITES = ("north", "south", "east", "west")


def _money(units: int, rate: str) -> str:
    whole, part = rate.split(".")
    cents = units * (int(whole) * 100 + int(part))
    return f"{cents // 100}.{cents % 100:02d}"


def event_rows(
    rows: int = ROWS_AT_THE_FLOOR,
    seed: int = SEED,
    events_per_subject: int = 1,
    keyed_rows: int = 0,
    binary_rates: bool = False,
) -> "list[list[str]]":
    """The table's rows; `events_per_subject` 3 is the draft's several-rows leg (lanes GR and RO)."""
    if rows < 1 or events_per_subject < 1:
        raise ValueError("a table holds at least one row, and a subject at least one event")
    if not 0 <= keyed_rows <= rows:
        raise ValueError("the keyed rows are rows of the table")
    draw = random.Random(seed)
    keyed = set(random.Random(seed + 1).sample(range(rows), keyed_rows))
    out: "list[list[str]]" = []
    for row in range(rows):
        started = _FIRST_DAY + datetime.timedelta(days=draw.randrange(720))
        days_open = int(draw.expovariate(1 / 3.5))
        opened = _FIRST_STAMP + datetime.timedelta(minutes=draw.randrange(720 * 24 * 60))
        closed = opened + datetime.timedelta(minutes=int(draw.expovariate(1 / 90)))
        if row in keyed:
            closed = opened - datetime.timedelta(days=1 + row % 3)
        units = draw.randint(1, 40)
        rate = draw.choice(_BINARY_RATES if binary_rates else _RATES)
        gender = draw.choice("FM")
        age = draw.randint(18, 89)
        pregnant = "yes" if gender == "F" and age < 45 and draw.random() < 0.2 else "no"
        out += [[
            f"S{row // events_per_subject:06d}",
            started.isoformat(),
            (started + datetime.timedelta(days=days_open)).isoformat(),
            f"{days_open}",
            opened.strftime("%Y-%m-%d %H:%M"),
            closed.strftime("%Y-%m-%d %H:%M"),
            f"{units}",
            rate,
            repr(units * float(rate)) if binary_rates else _money(units, rate),
            gender,
            pregnant,
            f"{age}",
            draw.choice(_SITES),
        ]]
    return out


def event_table(
    rows: int = ROWS_AT_THE_FLOOR,
    seed: int = SEED,
    events_per_subject: int = 1,
    keyed_rows: int = 0,
    binary_rates: bool = False,
) -> str:
    """The table as comma-separated text with a header line, ending in one newline."""
    return as_text(HEADER, event_rows(rows, seed, events_per_subject, keyed_rows, binary_rates))


def as_text(header: "tuple[str, ...]", rows: "list[list[str]]") -> str:
    """Comma-separated text with a header line, ending in one newline."""
    lines = [",".join(header)]
    for row in rows:
        lines += [",".join(row)]
    return "\n".join(lines) + "\n"


CHAIN_HEADER = ("arrived_at", "seen_at", "left_at", "left_on", "ward")


def chain_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED) -> "list[list[str]]":
    """Part (vii): `arrived_at <= seen_at <= left_at` on every row, and `left_on` the day of `left_at`."""
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for _row in range(rows):
        arrived = _FIRST_STAMP + datetime.timedelta(minutes=draw.randrange(720 * 24 * 60))
        seen = arrived + datetime.timedelta(minutes=0 if draw.random() < 0.1 else 1 + int(draw.expovariate(1 / 30)))
        left = seen + datetime.timedelta(minutes=5 + int(draw.expovariate(1 / 180)))
        out += [[
            arrived.strftime("%Y-%m-%d %H:%M"),
            seen.strftime("%Y-%m-%d %H:%M"),
            left.strftime("%Y-%m-%d %H:%M"),
            left.date().isoformat(),
            draw.choice(_SITES),
        ]]
    return out


AGES_HEADER = ("age_at_admit", "age_at_discharge", "site")


def ages_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED) -> "list[list[str]]":
    """Two ages, the second 0 to 3 years above the first, up to 104: both under the age top-code."""
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for _row in range(rows):
        age = min(104, max(18, int(draw.gauss(70, 14))))
        out += [[f"{age}", f"{age + draw.choice((0, 0, 0, 1, 1, 2, 3))}", draw.choice(_SITES)]]
    return out


PERSON_HEADER = ("subject_id", "visit_on", "ended_on", "site")


def person_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED, failing_rows: int = 12) -> "list[list[str]]":
    """Ten rows a subject; the first `failing_rows` rows, all of subject S000000, end before they start."""
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for row in range(rows):
        visit = _FIRST_DAY + datetime.timedelta(days=draw.randrange(720))
        end = visit + datetime.timedelta(days=int(draw.expovariate(1 / 3.5)))
        who = row // 10
        if row < failing_rows:
            who = 0
            end = visit - datetime.timedelta(days=1 + row % 3)
        out += [[f"S{who:06d}", visit.isoformat(), end.isoformat(), draw.choice(_SITES)]]
    return out


LAYOUT_HEADER = ("ordered_on", "filled_on", "site")


def layout_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED) -> "list[list[str]]":
    """`filled_on` on or after `ordered_on` on every row, the first written year first, the second month first."""
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for _row in range(rows):
        ordered = _FIRST_DAY + datetime.timedelta(days=draw.randrange(720))
        filled = ordered + datetime.timedelta(days=int(draw.expovariate(1 / 2)))
        out += [[ordered.isoformat(), filled.strftime("%m/%d/%Y"), draw.choice(_SITES)]]
    return out


HEAP_HEADER = ("opened_on", "closed_on", "site")


def heap_rows(
    rows: int = ROWS_AT_THE_FLOOR,
    seed: int = SEED,
    heap_days: int = 0,
    above: int = 21,
    failing: int = 0,
) -> "list[list[str]]":
    """`closed_on` is `heap_days` after `opened_on` on every row but `failing` rows a day before it and
    `above` rows one to three days past the heap."""
    if not 0 <= failing + above <= rows:
        raise ValueError("the failing rows and the rows above the heap are rows of the table")
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for row in range(rows):
        opened = _FIRST_DAY + datetime.timedelta(days=draw.randrange(720))
        gap = heap_days
        if row < failing:
            gap = -1
        elif row < failing + above:
            gap = heap_days + 1 + row % 3
        out += [[opened.isoformat(), (opened + datetime.timedelta(days=gap)).isoformat(), draw.choice(_SITES)]]
    return out


SUM_HEADER = ("charge", "adjustment", "net", "site")


def sum_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED) -> "list[list[str]]":
    """`net` is `charge + adjustment`, written as the shortest text of the binary64 sum; on half the
    rows the adjustment cancels the charge but for 1 to 99 cents."""
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for row in range(rows):
        charge = draw.randint(1000, 50000)
        if row % 2:
            adjustment = -(charge - draw.randint(1, 99))
        else:
            adjustment = -draw.randint(0, charge // 2)
        charge_text = f"{charge // 100}.{charge % 100:02d}"
        adjustment_text = f"-{-adjustment // 100}.{-adjustment % 100:02d}"
        net = repr(float(charge_text) + float(adjustment_text))
        out += [[charge_text, adjustment_text, net, draw.choice(_SITES)]]
    return out


EXPONENT_HEADER = ("dose_base", "dose_given", "site")


def exponent_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED) -> "list[list[str]]":
    """`dose_given` is `dose_base + 200` on every row, written in E-notation (`12e2` for 1,200)."""
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for row in range(rows):
        out += [[f"{1000 + 100 * (row % 40)}", f"{12 + row % 40}e2", draw.choice(_SITES)]]
    return out


SECONDS_HEADER = ("began_at", "ended_at", "site")


def seconds_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED, any_second: bool = False) -> "list[list[str]]":
    """`began_at` a clock to the second, 100 clocks ending in `:30` each on a hundredth of the rows (or,
    with `any_second`, at any second); `ended_at` the next minute, written to the minute."""
    draw = random.Random(seed)
    clocks = draw.sample(range(1, 23 * 60), 100)
    out: "list[list[str]]" = []
    for row in range(rows):
        minute = clocks[row % len(clocks)]
        second = draw.randrange(60) if any_second else 30
        out += [[
            f"{minute // 60:02d}:{minute % 60:02d}:{second:02d}",
            f"{(minute + 1) // 60:02d}:{(minute + 1) % 60:02d}",
            draw.choice(_SITES),
        ]]
    return out


DAY_END_HEADER = ("began_at", "minutes", "ended_at", "site")


def day_end_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED) -> "list[list[str]]":
    """Clocks of 23:57, 23:58 and 23:59 on a third of the rows each, a source length of 0 to 3 minutes,
    and `ended_at` their sum held at 23:59 (one row's sum passes it). The counts scale with `rows`."""
    if rows < 30:
        raise ValueError("the table holds at least 30 rows")
    draw = random.Random(seed)
    first = rows // 3
    second = (rows - first) // 2
    lengths = {
        "23:57": [0] * (20 * rows // 20000) + [1] * (first // 2) + [3],
        "23:58": [0] * (3000 * rows // 20000),
        "23:59": [0] * (rows - first - second),
    }
    lengths["23:57"] += [2] * (first - len(lengths["23:57"]))
    lengths["23:58"] += [1] * (second - len(lengths["23:58"]))
    out: "list[list[str]]" = []
    for began, minutes in lengths.items():
        start = int(began[:2]) * 60 + int(began[3:])
        for length in minutes:
            end = min(start + length, 23 * 60 + 59)
            out += [[began, f"{length}", f"{end // 60:02d}:{end % 60:02d}", draw.choice(_SITES)]]
    return out
