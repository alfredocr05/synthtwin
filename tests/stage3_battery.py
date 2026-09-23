"""The stage-3 count battery: one seeded shape per count that can sit below the floor.

WHY IT LIVES IN THE TEST TREE. The inventory of stage 3's count design
was measured on these forty-three tables, and a measurement nobody can
re-run is a number somebody will one day have to take on trust. Every
table is built here from `random.Random(20260922)` and nothing is read
from any real data: each shape writes in a small group -- one to ten cells
-- of the kind one published count counts, so that a rule which starts
naming such a group turns a test red rather than going unnoticed.

The shapes are NEUTRAL in the sense plan D13 fixes: the values are
drawn from a fixed seed, no table enters the repository, and no shape
is derived from anybody's data.

Used by `tests/test_p4d334_sentence_arguments.py` for the landing's
gate and by `tests/test_kpi_ledger.py` for `K-S3-01`, the ceiling on
how many published counts of one to ten this tool leaves standing.
"""

import csv
import datetime
import io
import pathlib
import random

from synthtwin import profile, reading, taxonomy

# The seed the stage-3 inventory was measured at.
BATTERY_SEED = 20260922


def gauss_cells(rng, n, mu=100.0, sd=15.0, dp=1):
    """`n` cells drawn from a normal curve, written at `dp` figures."""
    return [f"{rng.gauss(mu, sd):.{dp}f}" for _ in range(n)]


def positive_cells(rng, n):
    """`n` positive cells, so a zero or negative written in is the only one."""
    return [f"{abs(rng.gauss(100.0, 15.0)) + 1:.1f}" for _ in range(n)]


def plant(cells, rng, written_in):
    """`written_in` written over randomly chosen cells of `cells`."""
    made = list(cells)
    for text in written_in:
        made[rng.randrange(len(made))] = text
    return made


SHAPES = {}


def shape(fn):
    SHAPES[fn.__name__] = fn
    return fn


@shape
def numeric_one_negative(rng):
    return plant(positive_cells(rng, 400), rng, ["-3.2"]), {}


@shape
def numeric_one_zero(rng):
    return plant(positive_cells(rng, 400), rng, ["0.0"]), {}


@shape
def numeric_three_not_numbers(rng):
    return plant(positive_cells(rng, 400), rng, ["pending", "pending", "see note"]), {}


@shape
def numeric_one_out_of_range(rng):
    return plant(positive_cells(rng, 400), rng, ["1e999"]), {}


@shape
def numeric_one_contradictory(rng):
    return plant(positive_cells(rng, 400), rng, ["(-5)"]), {}


@shape
def numeric_one_negative_unrepresentable(rng):
    return plant(positive_cells(rng, 400), rng, ["-1e999"]), {}


@shape
def numeric_one_blank(rng):
    return plant(positive_cells(rng, 400), rng, [""]), {}


@shape
def numeric_two_na_words(rng):
    return plant(positive_cells(rng, 400), rng, ["N/A", "N/A"]), {}


@shape
def numeric_one_grouped_comma(rng):
    cells = [f"{rng.randint(100, 999)}" for _ in range(400)]
    return plant(cells, rng, ["1,234"]), {}


@shape
def numeric_rare_sentinel(rng):
    return plant(positive_cells(rng, 400), rng, ["-999", "-999"]), {}


@shape
def count_whole_one_fraction(rng):
    cells = [f"{rng.randint(0, 40)}" for _ in range(400)]
    return plant(cells, rng, ["2.5"]), {}


@shape
def dates_one_unparsed(rng):
    start = datetime.date(2020, 1, 1)
    cells = [(start + datetime.timedelta(days=rng.randint(0, 900))).isoformat() for _ in range(400)]
    return plant(cells, rng, ["unknown"]), {}


@shape
def moments_one_date_only(rng):
    start = datetime.datetime(2020, 1, 1, 8, 0)
    cells = [
        (start + datetime.timedelta(minutes=rng.randint(0, 900 * 24 * 60))).strftime("%Y-%m-%d %H:%M:%S")
        for _ in range(400)
    ]
    return plant(cells, rng, ["2021-03-04"]), {}


@shape
def moments_one_midnight(rng):
    start = datetime.datetime(2020, 1, 1, 8, 5)
    cells = [
        (start + datetime.timedelta(hours=7 * i)).strftime("%Y-%m-%d %H:%M:%S")
        for i in range(400)
    ]
    cells[37] = "2020-06-01 00:00:00"
    return cells, {}


@shape
def slashed_dates_day_first_evidence(rng):
    cells = []
    for _ in range(400):
        d = datetime.date(2020, 1, 1) + datetime.timedelta(days=rng.randint(0, 800))
        cells += [f"{d.month:02d}/{d.day:02d}/{d.year}" if d.day <= 12 else f"{d.month:02d}/{d.day:02d}/{d.year}"]
    # three day-first-only cells (day > 12 in first place)
    cells = plant(cells, rng, ["25/03/2021", "28/04/2021", "30/05/2021"])
    return cells, {}


@shape
def compact_dates_also_numbers(rng):
    start = datetime.date(2020, 1, 1)
    cells = [(start + datetime.timedelta(days=rng.randint(0, 900))).strftime("%Y%m%d") for _ in range(400)]
    return cells, {}


@shape
def joined_one_reversed(rng):
    cells = []
    for _ in range(400):
        a = rng.randint(100, 160)
        b = rng.randint(50, 95)
        cells += [f"{a}/{b}"]
    cells[11] = "70/120"
    return cells, {}


@shape
def clock_two_not_clock(rng):
    cells = [f"{rng.randint(0, 23):02d}:{rng.randint(0, 59):02d}" for _ in range(400)]
    return plant(cells, rng, ["late", "early"]), {}


@shape
def affixed_one_variant(rng):
    cells = [f"{rng.randint(1, 40)} mg" for _ in range(400)]
    return plant(cells, rng, ["12 MG"]), {}


@shape
def compound_five_labels(rng):
    cells = positive_cells(rng, 300)
    return plant(cells, rng, ["NOT DETECTED"] * 5), {}


@shape
def labels_one_case_variant(rng):
    words = ["north", "south", "east", "west"]
    cells = [rng.choice(words) for _ in range(400)]
    cells[5] = "NORTH"
    return cells, {}


@shape
def labels_one_blank_pooled(rng):
    cells = ["NORTH"] * 1977 + ["SOUTH"] * 11 + ["SITE_X"]
    rng.shuffle(cells)
    return cells, {}


@shape
def identifier_declared(rng):
    cells = [f"REC{rng.randint(1000000, 9999999)}" for _ in range(999)] + ["42"]
    return cells, {"identifiers": ["value"]}


@shape
def free_text_one_number(rng):
    words = ["alpha", "beta", "gamma", "delta", "eps", "zeta", "eta", "theta"]
    cells = [" ".join(rng.choice(words) for _ in range(rng.randint(2, 9))) + f" {i}" for i in range(999)]
    cells += ["42"]
    return cells, {}


@shape
def numeric_padded_three(rng):
    cells = positive_cells(rng, 400)
    return plant(cells, rng, ["007.5", "012.5", "099.1"]), {}


@shape
def numeric_trailing_pct_near_line(rng):
    # 396 numbers + 4 text: just over the 99% line (396/400).
    return plant(positive_cells(rng, 400), rng, ["x1", "x2", "x3", "x4"]), {}


@shape
def categories_small_count(rng):
    cells = [rng.choice(["a", "b", "c"]) for _ in range(400)]
    return cells, {}







@shape
def affixed_many_one_variant(rng):
    cells = [f"{rng.gauss(50, 12):.1f} mg" for _ in range(400)]
    return plant(cells, rng, ["12.5mg", "13.0mg"]), {}


@shape
def affixed_one_out_of_range_core(rng):
    cells = [f"{rng.gauss(50, 12):.1f} mg" for _ in range(400)]
    return plant(cells, rng, ["1e999 mg"]), {}


@shape
def compound_twelve_labels_one_oor(rng):
    cells = positive_cells(rng, 400)
    return plant(cells, rng, ["NOT DETECTED"] * 12 + ["1e999"]), {}


@shape
def joined_one_unparsed(rng):
    cells = [f"{rng.randint(100, 160)}/{rng.randint(50, 95)}" for _ in range(400)]
    return plant(cells, rng, ["unknown"]), {}


@shape
def unrepresentable_mixed(rng):
    cells = [f"{rng.randint(1, 9)}e{rng.randint(400, 500)}" for _ in range(400)]
    return plant(cells, rng, ["-5e450", "1.5e420"]), {}


@shape
def epoch_seconds(rng):
    base = 1_600_000_000
    return [f"{base + rng.randint(0, 50_000_000)}" for _ in range(400)], {}


@shape
def label_stand_in(rng):
    cells = [rng.choice(["north", "south", "-999"]) for _ in range(400)]
    return cells, {}


@shape
def long_tail_labels(rng):
    cells = [rng.choice(["alpha", "beta", "gamma"]) for _ in range(300)]
    cells += [f"code{i:03d}" for i in range(100)]
    return cells, {}


@shape
def free_text_letters_against_digits(rng):
    cells = [f"{rng.randint(1000, 9999)}" for _ in range(380)]
    cells += [f"{rng.randint(1000, 9999)}F" for _ in range(20)]
    rng.shuffle(cells)
    return cells, {}


@shape
def two_readings_fit(rng):
    cells = [f"{rng.gauss(5, 1):.1f}" for _ in range(380)]
    cells += [f"{rng.gauss(5, 1):.1f} H" for _ in range(20)]
    rng.shuffle(cells)
    return cells, {}


@shape
def comma_settled_decimal(rng):
    cells = [f"{rng.randint(1, 999):,}" if rng.random() < 0.5 else f"{rng.randint(1000, 9999):,}" for _ in range(400)]
    return plant(cells, rng, ["12,5", "3,75"]), {}


@shape
def free_text_some_dates(rng):
    words = ["alpha", "beta", "gamma", "delta"]
    cells = [" ".join(rng.choice(words) for _ in range(5)) + f" {i}" for i in range(397)]
    cells += ["2021-01-05", "2021-02-07", "2021-03-09"]
    return cells, {}


@shape
def free_text_clock_reach(rng):
    words = ["alpha", "beta", "gamma", "delta"]
    cells = [" ".join(rng.choice(words) for _ in range(5)) + f" {i}" for i in range(396)]
    cells += ["10h30", "11h45", "09h05", "12h00"]
    return cells, {}


@shape
def free_text_affix_reach(rng):
    words = ["alpha", "beta", "gamma", "delta"]
    cells = [" ".join(rng.choice(words) for _ in range(5)) + f" {i}" for i in range(394)]
    cells += ["5 mg", "7 mg", "9 mg", "11 mg", "12 mg", "3 mg"]
    return cells, {}


@shape
def numbers_with_sentinel_frequent(rng):
    cells = positive_cells(rng, 400)
    return plant(cells, rng, ["-999"] * 30), {}


@shape
def near_category_line(rng):
    labels = [f"L{i:02d}" for i in range(40)]
    cells = [labels[i % 40] for i in range(400)]
    return cells, {}



def rows_text(header, rows):
    """A delimited table as text, written the way the reader expects it."""
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)
    return out.getvalue()


def described(
    folder: pathlib.Path, name: str, floor: int = 11
) -> "dict[str, object]":
    """One battery shape, written to `folder` and described at `floor`.

    The product's own path and nothing else: the table is written to
    disk, read by the real reader and described by the real producer.
    """
    cells, flags = SHAPES[name](random.Random(BATTERY_SEED))
    path = folder / f"{name}.csv"
    path.write_text(
        rows_text(["value"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    table = reading.read_table(str(path), small_cell_floor=floor)
    settings = taxonomy.Settings(small_cell_floor=floor)
    return profile.build_document(
        table,
        settings,
        list(flags["identifiers"] if "identifiers" in flags else ()),
        [],
        [],
    )
