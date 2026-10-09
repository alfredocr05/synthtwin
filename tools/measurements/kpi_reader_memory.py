"""K-S4-02: the most memory reading a large mixed table holds, per row.

PLAN P4-D387. A made-up table of fifty columns -- three record numbers,
six codes, ten labels, fifteen numbers in their spellings (`12,345.67`,
`5 mg`, `97%`, `<0.3`), four dates, five stamps, three clocks and four
free texts, about 480 bytes a row -- is written from one seeded random
stream and read by the reader alone (`reading.read_table`), in a process
of its own so the high-water mark is this read's:

* `reader_peak_kb_per_row`: the process's peak resident memory above
  what it held before the read, in kilobytes a row. RECORDED everywhere
  and JUDGED only on the quiet reference machine (`kpi_rules`), because
  the allocator and the platform move it;
* `reader_seconds`: the read's CPU seconds, recorded;
* `rows`: the rows read;
* `survey_peak_cr_over_lf` and `survey_peak_mixed_over_lf`: the most
  memory the survey (`dialect.settle`) holds above its text, traced by
  `tracemalloc`, with the table's lines ended by carriage returns alone,
  and by line feeds for a quarter of them and carriage returns alone
  after, over the same with line feeds, on the same table at 10,000
  rows. MACHINE-FREE, so judged everywhere (the Codex review of plan
  P4-D387, item 2): 9fa2008 cut a file at its line feeds alone, so every
  line of a run of carriage-return lines was cut into one list held
  while the survey filled its table, 1.164 and 1.125 times the line
  feeds' peak; each line ending now ends a block. `survey_bytes_a_row`
  records the line feeds' peak beside them.

200,000 ROWS, NOT THE DESIGN'S 500,000. One read of 500,000 rows holds
about two gigabytes at its peak, more than one process is given beside
other work on the shared build machine; the reader's work grows with the
rows (`tests/test_stage4_tier2a.py`), so 500,000 rows hold about two and
a half times what 200,000 do. `--rows` reads another size.

At 110cb46 the same 200,000 rows read in 37.7 CPU seconds at a peak of
5.41 KB a row above the start, and at eb6c378 in 25.8 at 4.38, both at a
load average near 9: the checking pass held the whole second reading,
and the survey and the standard reader's check each a list of every
line. Under more load the system compresses pages and the resident peak
reads lower on both, which is why it is judged on the quiet machine only.
The peak is not read on Windows, which has no `resource` module.

    .venv/bin/python tools/measurements/kpi_reader_memory.py --kpi [--rows N]
"""

import argparse
import datetime
import math
import pathlib
import random
import sys
import tempfile
import time
import tracemalloc
import typing

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import kpi_rules  # noqa: E402

from synthtwin import dialect, reading  # noqa: E402

SEED = 20261002
ROWS = 200_000
# The rows whose survey is traced with each line ending: tracing every
# allocation is slow, and the ratio of two peaks does not move with the rows.
SURVEY_ROWS = 10_000

_GROUPS = {
    "ids": ["unit_id", "visit_id", "record_no"],
    "codes": ["code_a", "code_b", "code_c", "post_code", "lab_code", "site_code"],
    "labels": ["kind", "colour", "shape", "tier", "channel", "outcome", "team", "status",
               "language", "plan"],
    "numbers": ["years", "mass", "span", "ratio", "upper", "lower", "beat", "warmth",
                "level", "factor", "count_a", "amount", "days", "dose", "share"],
    "dates": ["start_date", "end_date", "born_date", "step_date"],
    "stamps": ["start_at", "order_at", "result_at", "check_at", "end_at"],
    "clocks": ["shift_clock", "round_clock", "arrive_clock"],
    "texts": ["reason", "note", "author", "remark"],
}
_NAMES = [name for group in _GROUPS.values() for name in group]

_WORDS = ["alpha", "bravo", "cedar", "delta", "ember", "fable", "grove", "harbor", "indigo",
          "juniper", "kettle", "lantern", "meadow", "nectar", "orbit", "pebble", "quartz",
          "ripple", "saffron", "timber", "umber", "violet", "willow", "yonder", "zephyr"]


def _weights(count: int) -> "list[float]":
    return [1.0 / (place + 1) ** 1.1 for place in range(count)]


def _pools(draw: random.Random) -> "dict[str, list[str]]":
    letters = "ABCDEFGHJKLMNPRSTVWXYZ"
    codes_a = sorted({f"{draw.choice(letters)}{draw.randrange(100):02d}.{draw.randrange(10)}"
                      for _ in range(700)})[:600]
    codes_b = sorted({f"{draw.randrange(10000, 99999)}" for _ in range(300)})[:250]
    codes_c = sorted({f"{draw.randrange(10000):04d}-{draw.randrange(10000):04d}-{draw.randrange(100):02d}"
                      for _ in range(400)})
    posts = sorted({f"{draw.randrange(100000):05d}" for _ in range(1500)})
    labs = sorted({f"{draw.randrange(1000, 99999)}-{draw.randrange(10)}" for _ in range(150)})
    sites = [f"S{place:03d}" for place in range(40)]
    authors = sorted({f"{draw.choice(letters)}. {draw.choice(_WORDS).capitalize()}{draw.randrange(100)}"
                      for _ in range(900)})[:800]
    for pool in (codes_a, codes_b, codes_c, posts, labs, authors):
        draw.shuffle(pool)
    return {"code_a": codes_a, "code_b": codes_b, "code_c": codes_c, "post_code": posts,
            "lab_code": labs, "site_code": sites, "author": authors}


def _row(draw: random.Random, row: int, rows: int, pools: "dict[str, list[str]]",
         weights: "dict[str, list[float]]") -> "list[str]":
    def pick(name: str) -> str:
        return draw.choices(pools[name], weights[name])[0]

    out = [f"U{draw.randrange(max(1, rows // 4)):07d}", f"V{(row * 2654435761) % 10**9:09d}",
           f"{(row * 48271 + 12345) % 10**8:08d}"]
    out += [pick("code_a"), pick("code_b"), pick("code_c") if draw.random() > 0.2 else "",
            pick("post_code"), pick("lab_code"), pick("site_code")]
    out += [draw.choice(("P", "Q", "R")), draw.choice(("red", "green", "blue", "grey", "")),
            draw.choice(("round", "square", "flat", "long")), draw.choice(("one", "two", "three")),
            draw.choice(("mail", "phone", "visit", "web", "other")),
            draw.choice(("done", "open", "moved", "closed", "held", "lost", "kept", "sent")),
            f"Team {draw.choice('ABCDEFGHIJKLMNOPQRSTUVWXY')}", draw.choice(("new", "old", "now", "")),
            draw.choice(("en", "es", "fr", "de", "it", "pt", "nl")),
            draw.choice(("basic", "plus", "full", "none", "trial", "other"))]
    years = min(100, max(0, int(draw.gauss(55, 18))))
    mass = max(2.5, draw.gauss(80, 18))
    span = max(45, int(draw.gauss(170, 10)))
    stay = int(draw.expovariate(1 / 4.5))
    factor = math.exp(draw.gauss(0.0, 0.35))
    out += [str(years), f"{mass:.1f}" if draw.random() > 0.02 else "", str(span),
            f"{mass / (span / 100) ** 2:.1f}", str(int(draw.gauss(128, 18))), str(int(draw.gauss(78, 11))),
            str(int(draw.gauss(80, 14))), f"{draw.gauss(36.9, 0.5):.1f}", str(int(math.exp(draw.gauss(4.7, 0.3)))),
            "<0.3" if factor < 0.42 else f"{factor:.2f}", f"{draw.gauss(13, 1.8):.1f}",
            f"{math.exp(draw.gauss(9, 1.1)):,.2f}", str(stay),
            draw.choice(("0.5 mg", "1 mg", "2 mg", "5 mg", "10 mg", "20 mg", "50 mg", "100 mg")),
            f"{min(100, int(draw.gauss(96.5, 2.2)))}%"]
    start = datetime.date(2019, 1, 1) + datetime.timedelta(days=draw.randrange(2192))
    end = start + datetime.timedelta(days=stay)
    born = start - datetime.timedelta(days=years * 365 + draw.randrange(365))
    step = start + datetime.timedelta(days=draw.randrange(stay + 1))
    out += [start.isoformat(), f"{end.month:02d}/{end.day:02d}/{end.year}", born.isoformat(),
            step.strftime("%d-%b-%Y") if draw.random() < 0.7 else ""]
    hour = int(draw.choices(range(24), [2, 1, 1, 1, 1, 2, 2, 4, 6, 7, 7, 7, 6, 6, 6, 6, 6, 5, 5, 4, 4, 3, 3, 2])[0])
    minute = draw.randrange(60)
    at = datetime.datetime(start.year, start.month, start.day, hour, minute)
    order = at + datetime.timedelta(minutes=int(draw.expovariate(1 / 45)))
    result = order + datetime.timedelta(seconds=int(draw.expovariate(1 / 5400)))
    check = at + datetime.timedelta(minutes=draw.randrange(0, 600, 5))
    twelve = check.hour % 12 or 12
    finish = datetime.datetime(end.year, end.month, end.day, int(draw.gauss(13, 2.5)) % 24, draw.randrange(60))
    out += [at.strftime("%Y-%m-%d %H:%M:00"), f"{order.month}/{order.day}/{order.year} {order.hour}:{order.minute:02d}",
            result.strftime("%Y-%m-%dT%H:%M:%S"),
            f"{check.month:02d}/{check.day:02d}/{check.year} {twelve:02d}:{check.minute:02d} "
            f"{'AM' if check.hour < 12 else 'PM'}",
            finish.strftime("%Y-%m-%d %H:%M")]
    quarter = draw.randrange(96)
    hours, minutes = divmod(quarter * 15, 60)
    out += [draw.choice(("07:00", "15:00", "19:00", "23:00", "07:30")),
            f"{(hours % 12) or 12:02d}:{minutes:02d} {'AM' if hours < 12 else 'PM'}",
            f"{hour:02d}:{minute:02d}:{draw.randrange(60):02d}"]
    reason = draw.choice(_WORDS)
    note = " ".join(draw.choice(_WORDS) for _ in range(draw.randrange(6, 13)))
    out += [reason if draw.random() < 0.3 else f"{reason} x {draw.randrange(1, 15)} days", note.capitalize(),
            pick("author"), draw.choice(("see note", "call back", "pending", "kept")) if draw.random() < 0.08 else ""]
    return out


def table_lines(rows: int) -> "typing.Iterator[str]":
    """The made-up table's lines, the header first and ``rows`` rows, without their endings, from one seeded stream."""
    draw = random.Random(SEED)
    pools = _pools(draw)
    weights = {name: _weights(len(pool)) for name, pool in pools.items()}
    yield ",".join(_NAMES)
    for row in range(rows):
        cells = _row(draw, row, rows, pools, weights)
        yield ",".join(f'"{cell}"' if "," in cell else cell for cell in cells)


def write_table(path: pathlib.Path, rows: int) -> None:
    """The made-up table, ``rows`` rows, its lines ended by line feeds; nothing comes from a real table."""
    with path.open("w", encoding="utf-8", newline="") as out:
        for line in table_lines(rows):
            out.write(line + "\n")


def ended(lines: "list[str]", ending: str) -> str:
    """The lines ended by line feeds ("lf"), by carriage returns alone ("cr"), or "mixed".

    "mixed" ends the first quarter of the lines by line feeds, the rest by
    carriage returns alone and the last line by the pair: a long run of
    carriage-return lines after the last line feed.
    """
    if ending in ("lf", "cr"):
        mark = "\n" if ending == "lf" else "\r"
        return "".join(line + mark for line in lines)
    quarter = len(lines) // 4
    last = len(lines) - 1
    return "".join(
        line + ("\n" if place < quarter else "\r\n" if place == last else "\r") for place, line in enumerate(lines)
    )


def survey_peaks(rows: int) -> "dict[str, int]":
    """The most memory the survey of the table holds above its text, traced, with each line ending, in bytes."""
    lines = list(table_lines(rows))
    peaks: "dict[str, int]" = {}
    for ending in ("lf", "cr", "mixed"):
        text = ended(lines, ending)
        tracemalloc.start()
        try:
            before = tracemalloc.get_traced_memory()[0]
            tracemalloc.reset_peak()
            surveyed = dialect.settle(text, "utf-8", False, False, "mixed.csv")
            peaks[ending] = tracemalloc.get_traced_memory()[1] - before
        finally:
            tracemalloc.stop()
        if surveyed.n_rows != rows:
            raise SystemExit(f"the survey read {surveyed.n_rows} rows of {rows} with {ending} endings")
        del surveyed, text
    return peaks


def measure(rows: int) -> "dict[str, float | int]":
    """Write the table, read it once, and say what the read held at its peak; then trace the survey by line ending."""
    with tempfile.TemporaryDirectory() as folder:
        path = pathlib.Path(folder) / "mixed.csv"
        write_table(path, rows)
        before = _resident_peak()
        started = time.process_time()
        table = reading.read_table(str(path))
        seconds = time.process_time() - started
        peak = _resident_peak()
        read = table.n_rows
        del table
    found: "dict[str, float | int]" = {
        "reader_seconds": round(seconds, 1),
        "rows": read,
    }
    if before >= 0 and peak >= 0:
        found["reader_peak_kb_per_row"] = round((peak - before) / 1024 / read, 2)
    peaks = survey_peaks(SURVEY_ROWS)
    found["survey_bytes_a_row"] = round(peaks["lf"] / SURVEY_ROWS, 1)
    found["survey_peak_cr_over_lf"] = round(peaks["cr"] / peaks["lf"], 3)
    found["survey_peak_mixed_over_lf"] = round(peaks["mixed"] / peaks["lf"], 3)
    return found


def _resident_peak() -> int:
    """The process's peak resident memory so far, in bytes, or -1 where it cannot be read."""
    try:
        import resource
    except ImportError:
        return -1
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # ru_maxrss is in bytes on macOS and in kilobytes on Linux.
    return peak if sys.platform == "darwin" else peak * 1024


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kpi", action="store_true")
    parser.add_argument("--rows", type=int, default=ROWS)
    arguments = parser.parse_args()
    if not arguments.kpi:
        print(__doc__)
        return 0
    kpi_rules.guard_this_tree()
    found = measure(arguments.rows)
    kpi_rules.emit("K-S4-02", found, f"{found['rows']:,} rows of the made-up 50-column table")
    return 0


if __name__ == "__main__":
    sys.exit(main())
