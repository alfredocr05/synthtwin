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


# -- Lane RO's price shapes (plan P4-D459): a hospital stay, an emergency visit and a lab order,
# each invented with round figures by hand, `keyed` rows keyed into its main pair (the later event
# one to three days before the earlier), at `rows` rows. Nothing here is read from any table.


def _minute_text(minutes: int) -> str:
    return (_FIRST_STAMP + datetime.timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M")


def _day_text(minutes: int) -> str:
    return (_FIRST_STAMP + datetime.timedelta(minutes=minutes)).date().isoformat()


STAY_HEADER = (
    "admitted_on", "operated_on", "released_on", "stay_days", "care_days", "age", "gender", "pregnant",
    "systolic", "diastolic", "units", "rate", "total", "ward", "died",
)


def stay_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED, keyed: int = 6) -> "list[list[str]]":
    """A hospital stay: release on or after admission (`stay_days` their gap), an operation between them on
    three stays in ten, `care_days` no longer than the stay, two pressures, a charge as units times a rate."""
    draw = random.Random(seed)
    wrong = set(random.Random(seed + 1).sample(range(rows), keyed))
    out: "list[list[str]]" = []
    for row in range(rows):
        admitted = 1440 * draw.randrange(700)
        gap = int(draw.expovariate(1 / 4))
        released = admitted + 1440 * gap
        written = admitted - 1440 * draw.randint(1, 3) if row in wrong else released
        operated = _day_text(admitted + 1440 * draw.randint(0, gap)) if draw.random() < 0.3 else ""
        care = draw.randint(0, gap) if draw.random() < 0.2 else 0
        age = min(88, max(20, int(draw.gauss(60, 15))))
        gender = draw.choice("FM")
        pregnant = "yes" if gender == "F" and age < 45 and draw.random() < 0.25 else "no"
        diastolic = int(draw.gauss(80, 10))
        systolic = diastolic + 20 + int(draw.expovariate(1 / 20))
        units = draw.randint(1, 30)
        rate = draw.choice(_RATES)
        out += [[
            _day_text(admitted), operated, _day_text(written), f"{gap}", f"{care}", f"{age}", gender, pregnant,
            f"{systolic}", f"{diastolic}", f"{units}", rate, _money(units, rate),
            draw.choice(("med", "surg", "crit", "obs")), "1" if draw.random() < 0.04 else "0",
        ]]
    return out


EMERGENCY_HEADER = (
    "arrived_at", "triaged_at", "seen_at", "left_at", "visit_minutes", "arrival_day", "departure_day",
    "age", "acuity", "outcome",
)


def emergency_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED, keyed: int = 6) -> "list[list[str]]":
    """An emergency visit: arrival, triage, a first provider and departure in order, the visit's minutes,
    the arrival and departure days; one visit in a hundred leaves no departure."""
    draw = random.Random(seed)
    wrong = set(random.Random(seed + 1).sample(range(rows), keyed))
    out: "list[list[str]]" = []
    for row in range(rows):
        arrived = draw.randrange(700 * 1440)
        triaged = arrived + (0 if draw.random() < 0.1 else 1 + int(draw.expovariate(1 / 10)))
        seen = triaged + (0 if draw.random() < 0.05 else 1 + int(draw.expovariate(1 / 30)))
        left = seen + 5 + int(draw.expovariate(1 / 120))
        gone = draw.random() < 0.01
        written = arrived - 1440 * draw.randint(1, 3) if row in wrong else left
        out += [[
            _minute_text(arrived), _minute_text(triaged), _minute_text(seen), "" if gone else _minute_text(written),
            "" if gone else f"{left - arrived}", _day_text(arrived), "" if gone else _day_text(written),
            f"{min(95, max(0, int(draw.gauss(45, 20))))}", f"{draw.choice((1, 2, 3, 3, 3, 4, 4, 5))}",
            draw.choice(("home", "home", "home", "admit", "transfer")),
        ]]
    return out


LAB_HEADER = ("drawn_at", "received_at", "resulted_at", "turnaround", "draw_day", "report_day", "test", "value", "low_limit", "high_limit")


def lab_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED, keyed: int = 6) -> "list[list[str]]":
    """A lab order: drawn, received and resulted in order, the turnaround in minutes, the draw and report
    days (the report the same day on four orders in five), one of three tests with its reference limits."""
    draw = random.Random(seed)
    wrong = set(random.Random(seed + 1).sample(range(rows), keyed))
    tests = (("glucose", "70", "100", 90, 15), ("sodium", "135", "145", 140, 3), ("potassium", "3.5", "5.0", 4.2, 0.4))
    out: "list[list[str]]" = []
    for row in range(rows):
        drawn = draw.randrange(700 * 1440)
        received = drawn + (0 if draw.random() < 0.1 else 1 + int(draw.expovariate(1 / 15)))
        resulted = received + 3 + int(draw.expovariate(1 / 60))
        written = drawn - 1440 * draw.randint(1, 3) if row in wrong else resulted
        u = draw.random()
        report = 0 if u < 0.8 else (1 if u < 0.95 else 2)
        name, low, high, mean, spread = tests[draw.randrange(3)]
        out += [[
            _minute_text(drawn), _minute_text(received), _minute_text(written), f"{resulted - drawn}",
            _day_text(drawn), _day_text(drawn + 1440 * report), name, f"{round(draw.gauss(mean, spread), 1)}", low, high,
        ]]
    return out


# -- `B`'s own forms, the association item and exact figures (lane RO's repair 1) -------------------------

OFFSET_HEADER = ("seen_at", "left_at", "ward")


def offset_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED) -> "list[list[str]]":
    """Two stamps written with the offset `+02:00`, the second 0 to 240 minutes after the first."""
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for row in range(rows):
        seen = _FIRST_STAMP + datetime.timedelta(days=draw.randrange(600), minutes=draw.randrange(600))
        left = seen + datetime.timedelta(minutes=draw.choice((0, 15, 30, 45, 60, 90, 120, 240)))
        out += [[seen.strftime("%Y-%m-%dT%H:%M:%S+02:00"), left.strftime("%Y-%m-%dT%H:%M:%S+02:00"), _SITES[row % 4]]]
    return out


MONTH_HEADER = ("admit_on", "release_on", "ward")


def month_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED) -> "list[list[str]]":
    """A date written year first, and a later one written day, month name and year (`05-Jan-2024`)."""
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for row in range(rows):
        admit = _FIRST_DAY + datetime.timedelta(days=draw.randrange(600))
        release = admit + datetime.timedelta(days=draw.choice((0, 1, 2, 3, 5, 8, 10, 20)))
        out += [[admit.isoformat(), release.strftime("%d-%b-%Y"), _SITES[row % 4]]]
    return out


AFFIX_HEADER = ("dose_start", "dose_end", "ward")


def affix_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED) -> "list[list[str]]":
    """Two amounts written with a unit after them (`1769 mg`), the second never below the first."""
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for row in range(rows):
        start = draw.randrange(50, 5000)
        end = start + draw.choice((0, 1, 2, 3, 5, 8, 10, 20))
        out += [[f"{start} mg", f"{end} mg", _SITES[row % 4]]]
    return out


POLISHED_HEADER = ("dose_start", "dose_end", "weight", "ward")


def polished_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED) -> "list[list[str]]":
    """Two amounts, the second never below the first, beside a weight that follows the first closely.

    Batch 4q's merge of lane RO with lane MPg's polish (method G16.3's "a column a carried rule reads"):
    rule B's moments publish the first amount's correlation with the weight, so the polish moves the
    first amount, and the order rule computes the second from it.
    """
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for row in range(rows):
        start = draw.randrange(50, 5000)
        end = start + draw.choice((0, 1, 2, 3, 5, 8, 10, 20))
        weight = 40 + start / 60 + draw.gauss(0, 6)
        out += [[str(start), str(end), f"{weight:.1f}", _SITES[row % 4]]]
    return out


COMMA_HEADER = ("level_start", "level_end", "ward")


def comma_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED) -> "list[list[str]]":
    """Two amounts written with a decimal comma (`3204,10`), the second never below the first; a reader is
    told both columns write the comma (`--decimal-comma`)."""
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for row in range(rows):
        start = draw.randrange(1000, 400000)
        end = start + draw.choice((0, 25, 50, 100, 150, 225, 300, 475))
        out += [[f"{start // 100},{start % 100:02d}", f"{end // 100},{end % 100:02d}", _SITES[row % 4]]]
    return out


ACUITY_HEADER = ("arrived_at", "left_at", "acuity")


def acuity_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED) -> "list[list[str]]":
    """A visit's length set by its acuity (1 to 5: 30 to 300 minutes and a little more), arrivals spread over
    two years: the length's whole share of variance lies between the acuities, the departure's own none."""
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for _row in range(rows):
        arrived = _FIRST_STAMP + datetime.timedelta(minutes=draw.randrange(720 * 24 * 60))
        acuity = draw.randint(1, 5)
        left = arrived + datetime.timedelta(minutes=30 * acuity * acuity // 2 + 30 + draw.randrange(20))
        out += [[arrived.strftime("%Y-%m-%d %H:%M"), left.strftime("%Y-%m-%d %H:%M"), f"{acuity}"]]
    return out


FIGURES_HEADER = ("reading_a", "reading_b", "ward")


def figures_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED, below: int = 30) -> "list[list[str]]":
    """Two readings of 18 significant figures: the second equal to the first or 1 to 5 units of the last
    figure above it, but on `below` rows one unit of the last figure BELOW it, a difference binary64 cannot
    tell (both cells round to one binary64 number)."""
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for row in range(rows):
        whole = draw.randrange(10, 99)
        tail = draw.randrange(10**15, 10**16 - 10)
        first = whole * 10**16 + tail
        second = first - 1 if row < below else first + draw.randrange(6)
        out += [[f"{first // 10**16}.{first % 10**16:016d}", f"{second // 10**16}.{second % 10**16:016d}", _SITES[row % 4]]]
    return out


VISIT_HEADER = ("arrival", "departure", "acuity", "age", "disposition")


def visit_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED, keyed: int = 25) -> "list[list[str]]":
    """A visit's departure after its arrival, the length set by the acuity (1 to 5, a mean of 6 hours down
    to 40 minutes), arrivals spread over two years; `keyed` departures written days before the arrival."""
    draw = random.Random(seed)
    mean = {1: 360, 2: 240, 3: 150, 4: 80, 5: 40}
    wrong = set(random.Random(seed + 1).sample(range(rows), keyed))
    out: "list[list[str]]" = []
    for row in range(rows):
        arrival = draw.randrange(720 * 1440)
        acuity = draw.choice((1, 2, 3, 3, 3, 4, 4, 5))
        departure = arrival + 5 + int(draw.expovariate(1 / mean[acuity]))
        if row in wrong:
            departure = arrival - 1440 * draw.randint(1, 3)
        out += [[_minute_text(arrival), _minute_text(departure), f"{acuity}", f"{draw.randint(18, 89)}", draw.choice(("home", "home", "ward"))]]
    return out


VITALS_HEADER = ("pulse", "pressure", "age", "treated", "ward")


def vitals_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED) -> "list[list[str]]":
    """A pulse below a systolic pressure on every row, both moved by one stress, the pressure by the age and
    a treatment as well: an order no rule is meant to carry, the pressure's own association kept apart."""
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for _row in range(rows):
        stress = draw.gauss(0, 1)
        age = draw.randint(18, 89)
        treated = draw.random() < 0.4
        pulse = int(78 + 11 * stress + draw.gauss(0, 6))
        pressure = int(128 + 0.5 * (age - 55) - (12 if treated else 0) + 11 * stress + draw.gauss(0, 6))
        out += [[f"{pulse}", f"{pressure}", f"{age}", "1" if treated else "0", draw.choice(("med", "surg", "rehab"))]]
    return out


# -- the outside review's shapes and the verify's (lane RO's repair 2) ---------------------------------------

POINT_HEADER = ("dose_low", "dose_high", "ward")


def point_rows(rows: int = ROWS_AT_THE_FLOOR) -> "list[list[str]]":
    """A whole number, and the next one written with a point after its figures (`43.`), on every row."""
    return [[f"{42 + row % 200}", f"{43 + row % 200}.", _SITES[row % 4]] for row in range(rows)]


BRACKET_HEADER = ("balance_low", "balance_high", "ward")


def bracket_rows(rows: int = ROWS_AT_THE_FLOOR) -> "list[list[str]]":
    """Two balances below 0 written in accounting brackets (`(299)`), the second 1 to 3 above the first."""
    out: "list[list[str]]" = []
    for row in range(rows):
        low = -300 + row % 200
        high = low + 1 + row % 3
        out += [[f"({-low})", f"({-high})", _SITES[row % 4]]]
    return out


MARKER_HEADER = ("start_units", "added_units", "end_units", "ward")


def marker_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED) -> "list[list[str]]":
    """A count, a whole number added to it (`-99` on one row in ten, a placeholder the source names for no
    value) and their sum, absent where the added number is the placeholder."""
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for row in range(rows):
        start = 100 + draw.randrange(500)
        ward = draw.choice(_SITES)
        if row % 10 == 3:
            out += [[f"{start}", "-99", "", ward]]
        else:
            added = draw.randrange(31)
            out += [[f"{start}", f"{added}", f"{start + added}", ward]]
    return out


GROUPED_HEADER = ("level_low", "level_high", "ward")
GROUPED_STARTS = ("1,25", "2,50", "3,75", "5,00")


def grouped_rows(rows: int = ROWS_AT_THE_FLOOR) -> "list[list[str]]":
    """Four amounts written with a decimal comma on a quarter of the rows each, the second amount 1 or 2
    above the first, 3 or 4, 5 or 6, 7 or 8, by the first (a reader is told both columns write the comma)."""
    out: "list[list[str]]" = []
    for row in range(rows):
        group = row % 4
        cents = 125 * (group + 1) + 100 * (2 * group + 1 + (row // 4) % 2)
        out += [[GROUPED_STARTS[group], f"{cents // 100},{cents % 100:02d}", _SITES[(row // 8) % 4]]]
    return out


STEP_HEADER = ("score_a", "score_b", "ward")


def step_rows(rows: int = ROWS_AT_THE_FLOOR) -> "list[list[str]]":
    """A score cycling through 1 to 100, and a second 1 above it up to 50 and 100 above it past 50."""
    out: "list[list[str]]" = []
    for row in range(rows):
        score = 1 + row % 100
        out += [[f"{score}", f"{score + 1 if score <= 50 else score + 100}", _SITES[(row // 100) % 4]]]
    return out


SUMMED_HEADER = ("base_a", "next_c", "extra_x", "total_b")


def summed_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED) -> "list[list[str]]":
    """A count, a second 1 to 5 above it, a third count, and the sum of the second and the third."""
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for _row in range(rows):
        base = 100 + draw.randrange(400)
        following = base + 1 + draw.randrange(5)
        extra = draw.randrange(50)
        out += [[f"{base}", f"{following}", f"{extra}", f"{extra + following}"]]
    return out


INSTANT_HEADER = ("sent_at", "seen_at", "ward")


def instant_rows(rows: int = ROWS_AT_THE_FLOOR) -> "list[list[str]]":
    """A stamp at one of 100 minutes from midnight written at `+00:00`, and the instant a minute later written
    at `+10:00` (its local clock ten hours on)."""
    out: "list[list[str]]" = []
    for row in range(rows):
        sent = datetime.datetime(2023, 3, 1) + datetime.timedelta(minutes=row % 100)
        seen = sent + datetime.timedelta(hours=10, minutes=1)
        out += [[sent.strftime("%Y-%m-%dT%H:%M+00:00"), seen.strftime("%Y-%m-%dT%H:%M+10:00"), _SITES[(row // 100) % 4]]]
    return out


MILLISECOND_HEADER = ("sent_at", "acked_at", "ward")


def millisecond_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED) -> "list[list[str]]":
    """Two stamps written to the millisecond (`2023-07-13 12:40:56.123`), the second 0 to 5 seconds later."""
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for row in range(rows):
        sent = _FIRST_STAMP + datetime.timedelta(seconds=draw.randrange(86400 * 300), milliseconds=draw.randrange(1000))
        acked = sent + datetime.timedelta(seconds=draw.randrange(6), milliseconds=draw.randrange(1000))
        out += [[sent.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], acked.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], _SITES[(row // 100) % 4]]]
    return out


BILLED_HEADER = ("began_on", "billed_month", "ward")


def billed_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED) -> "list[list[str]]":
    """A date, and the month it was billed in written year and month alone (`2023-05`), never before it."""
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for row in range(rows):
        began = _FIRST_DAY + datetime.timedelta(days=draw.randrange(600))
        billed = began + datetime.timedelta(days=draw.choice((0, 20, 40, 70)))
        out += [[began.isoformat(), billed.strftime("%Y-%m"), _SITES[row % 4]]]
    return out


FINER_HEADER = ("began_at", "ended_at", "ward")


def finer_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED) -> "list[list[str]]":
    """A stamp to the second, and a later one written to the microsecond (`2023-05-07 18:20:24.970512`)."""
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for row in range(rows):
        began = _FIRST_STAMP + datetime.timedelta(days=draw.randrange(600), seconds=draw.randrange(86400))
        ended = began + datetime.timedelta(seconds=draw.choice((0, 5, 30, 90)), microseconds=draw.randrange(1000000))
        out += [[began.strftime("%Y-%m-%d %H:%M:%S"), ended.strftime("%Y-%m-%d %H:%M:%S.%f"), _SITES[row % 4]]]
    return out


# -- a stamp in another zone or to other figures than its input (lane RO's follow-up, LANE RO RULINGS 7) -----

ZONED_HEADER = ("sent_at", "seen_at", "ward")


def zoned_rows(rows: int = ROWS_AT_THE_FLOOR) -> "list[list[str]]":
    """A stamp at one of 100 minutes from midnight written at `-05:00`, and the instant a minute later written
    at `+03:00` (its local clock eight hours on): two zones."""
    out: "list[list[str]]" = []
    for row in range(rows):
        sent = datetime.datetime(2023, 3, 1) + datetime.timedelta(minutes=row % 100)
        seen = sent + datetime.timedelta(hours=8, minutes=1)
        out += [[sent.strftime("%Y-%m-%dT%H:%M-05:00"), seen.strftime("%Y-%m-%dT%H:%M+03:00"), _SITES[(row // 100) % 4]]]
    return out


CLOCK_CHANGE_HEADER = ("arrived_at", "left_at", "ward")
_CLOCK_CHANGE = datetime.datetime(2023, 3, 12, 7)


def _zone_text(instant: datetime.datetime) -> str:
    """An instant (UTC) written in one zone with a clock change: `-05:00` before it, `-04:00` from it."""
    offset = -5 if instant < _CLOCK_CHANGE else -4
    return (instant + datetime.timedelta(hours=offset)).strftime("%Y-%m-%dT%H:%M") + f"-0{-offset}:00"


def clock_change_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED) -> "list[list[str]]":
    """Two stamps of one zone over twenty days across its clock change, the second 1 to 20 hours after the
    first: a row across the change holds `-05:00` in the first and `-04:00` in the second."""
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for row in range(rows):
        arrived = datetime.datetime(2023, 3, 2) + datetime.timedelta(minutes=draw.randrange(20 * 24 * 60))
        left = arrived + datetime.timedelta(minutes=draw.randrange(60, 1201))
        out += [[_zone_text(arrived), _zone_text(left), _SITES[row % 4]]]
    return out


COARSER_HEADER = ("sent_at", "acked_at", "ward")


def coarser_rows(rows: int = ROWS_AT_THE_FLOOR, seed: int = SEED) -> "list[list[str]]":
    """A stamp written to the microsecond (`2023-07-13 12:40:56.123456`), and one 0 to 5 seconds and a
    millisecond or more later written to the millisecond (`2023-07-13 12:40:59.457`)."""
    draw = random.Random(seed)
    out: "list[list[str]]" = []
    for row in range(rows):
        sent = _FIRST_STAMP + datetime.timedelta(seconds=draw.randrange(86400 * 300), microseconds=draw.randrange(1000000))
        acked = sent + datetime.timedelta(seconds=draw.randrange(6), milliseconds=1 + draw.randrange(999))
        out += [[sent.strftime("%Y-%m-%d %H:%M:%S.%f"), acked.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], _SITES[(row // 100) % 4]]]
    return out
