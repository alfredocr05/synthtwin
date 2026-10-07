"""K-S3-60: numbers that are dates come back (landing R4).

PLAN P4-D384. The fourteen shapes of `tests/counted_dates.py` -- Excel's
1900 and 1904 serial dates and date-times, SAS and Stata days, seconds
and milliseconds, Unix seconds and milliseconds, Epic day numbers and
`*_DATE_REAL` with its contact number, and birth dates in three systems
-- and the same writers over events from 1985 to 2025 and births from
1920 to 2005 (the R4 design review, item 2), a floor of eleven, through
the real producer, generator and checker.

Asked, undeclared, described in this process at 1,000 rows:

* `shapes`: how many shapes were measured (fourteen);
* `asked`: shapes question Q3 asks on every one of seeds 0 to 2 with the
  system that wrote them among its answers (thirteen: signed SAS birth
  dates, written in a varying number of figures, are reached only by
  `--date-count`);
* `asked_with_a_stray_least`: the fewest shapes asked that way, at seed
  0, under any one of the six stray-value scenarios -- one cell keyed a
  century late or early, and one cell in a hundred written `0`, `-1`, or
  the system's own count for 9999-12-31 or 1900-01-01 (item 1, the
  BLOCKER);
* `events_1985_asked` and `births_1920_asked`: shapes asked that way over
  the two ranges at seed 0;
* `right_member_missing`: columns asked, in any of the above, whose
  answers do not name the system that wrote them;
* `new_questions`: columns of the chance battery -- its seventy-five
  generators of measurements, codes, money in cents, amounts to one
  figure and lengths of time, ten draws each at 1,000 rows -- that Q3
  asks where the fixed-width question did not ask already (items 1 and
  5, and the review of landing R4's item 7);
* `heap_10k_asked_least` and `heap_10k_wrong`: at 10,000 rows, the
  thirteen asked shapes with two and ten cells in a thousand holding
  one placeholder -- `0`, `-1`, or the system's own count for 9999-12-31
  or 1900-01-01 -- enough for the ladder to publish it as the column's
  end: the fewest shapes asked over the eight, and the shapes asked
  without the system that wrote them or with years more than one off
  the true span (the review of landing R4, item 1);
* `named_below_line`: set-aside numbers NF113 names that fewer than
  eleven cells hold, over the thirteen shapes at 1,000 rows with one
  cell of each placeholder (item 4).

Declared, `--date-count` naming the writer's system, each of the
forty-two columns (the fourteen shapes and each over the two ranges) at
1,000 rows for seeds 0 to 2 and at 10,000 rows for seed 0, through the
command line:

* `not_read_as_dates`: columns described as anything but dates with a
  `count_form`;
* `twin_cells_off_form`: twin cells, the column's own absent spellings
  aside, written otherwise than its published `count_form` writes, or
  naming no date in the system;
* `cells_not_round_tripped`: source cells naming a date whose date,
  written back by the published form, is not the cell character for
  character;
* `missed` and `source_missed`: twins, and sources checked against their
  own description, that `validate` does not pass;
* `weekday_tvd_10k`: the largest total variation distance between the
  source's weekdays and its twin's over the columns of dates at 10,000
  rows -- read the way the table's owner reads them (`decode`);
* `contacts_half_off_points`: the largest distance, in points, between
  the share of a contact number in either half of an Epic twin's dated
  cells at 10,000 rows and the census's share (item 8).

Declared at 1,000 rows, seed 0, beside the battery:

* `coarse_misread`: of `COARSE`'s seven columns, one whose figures no
  unit keeps read as dates, or one whose figures a unit keeps not read
  as dates or not written back cell for cell (item 2);
* `coarse_missed`: their twins and sources `validate` does not pass;
* `writers_missed`: columns pandas wrote with `repr` or as `45000.0`, and
  an Epic column written to seventeen significant figures, that are not
  read, written back and checked as their writer writes them -- the
  last read as numbers with NF115, and none stopping with a fault
  (items 3 and 5).

Before R4 (9cb2eb5, base 2) no question offered dates on any of these
columns; the epoch-band remark NF51 told only the four Unix-band
columns, and read SAS seconds and Stata milliseconds a decade late. The
twin kept every number's spelling and lost the calendar: weekday TVD
0.13 to 0.16 on the date counts at 1,000 rows (the R4 design, section 1).

    .venv/bin/python tools/measurements/kpi_counted_dates.py --kpi
"""

import contextlib
import csv
import io
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import counted_dates as battery  # noqa: E402
import kpi_rules  # noqa: E402

from synthtwin import (  # noqa: E402
    asking,
    contract,
    date_counts,
    profile,
    reading,
    taxonomy,
)
from synthtwin.cli import main as cli  # noqa: E402

ASKED_ROWS = 1000
ASKED_SEEDS = (0, 1, 2)
DECLARED_RUNS = ((1000, (0, 1, 2)), (10000, (0,)))
TVD_ROWS = 10000
CHANCE_DRAWS = 10


def _quiet(argv: "list[str]") -> int:
    held = io.StringIO()
    with contextlib.redirect_stdout(held), contextlib.redirect_stderr(held):
        return cli(argv)


def _write(path: pathlib.Path, cells: "list[str]") -> None:
    path.write_text(
        "seen\n" + "\n".join(f'"{cell}"' if "," in cell else cell for cell in cells) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _offered(home: pathlib.Path, cells: "list[str]") -> "list[str] | None":
    """The systems Q3 offers about an undeclared column, or None where it is not asked."""
    path = home / "asked.csv"
    _write(path, cells)
    table = reading.read_table(str(path))
    document = profile.build_document(table, taxonomy.Settings(), [])
    said = asking._date_counts_said(document["columns"][0])
    if said is None:
        return None
    return [member for member, _first, _last in said.readings]


def _median(ordered: "list[float]") -> float:
    middle = (len(ordered) - 1) * 0.5
    low = int(middle)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (middle - low) * (ordered[high] - ordered[low])


def asked(home: pathlib.Path, notes: "list[str]") -> "dict[str, int]":
    """Question Q3 over the battery, undeclared, and over the chance battery."""
    totals = {
        "shapes": len(battery.SHAPES),
        "asked": 0,
        "asked_with_a_stray_least": len(battery.SHAPES),
        "events_1985_asked": 0,
        "births_1920_asked": 0,
        "right_member_missing": 0,
        "new_questions": 0,
    }

    def offered_right(shape: "battery.Shape", cells: "list[str]", where: str) -> bool:
        nonlocal notes
        members = _offered(home, cells)
        if members is None:
            return False
        if shape.system not in members:
            totals["right_member_missing"] += 1
            notes += [f"{where}: asked without {shape.system}"]
            return False
        return True

    stray: "dict[str, int]" = {}
    for shape in battery.SHAPES:
        every = True
        for seed in ASKED_SEEDS:
            cells, truth = battery.cells(shape, ASKED_ROWS, seed)
            if not offered_right(shape, cells, f"{shape.name} seed {seed}"):
                every = False
            if seed != 0:
                continue
            for scenario in battery.SCENARIOS[1:]:
                dirty = battery.dirty(shape, cells, truth, scenario, 0)
                if offered_right(shape, dirty, f"{shape.name} {scenario}"):
                    stray[scenario] = stray.get(scenario, 0) + 1
        if every:
            totals["asked"] += 1
        for name in battery.RANGES:
            if offered_right(shape, battery.ranged(shape, name, ASKED_ROWS, 0), f"{shape.name} {name}"):
                totals[f"{name}_asked"] += 1
    for scenario in battery.SCENARIOS[1:]:
        totals["asked_with_a_stray_least"] = min(totals["asked_with_a_stray_least"], stray.get(scenario, 0))
    totals.update(_heaped(home, notes))
    totals["named_below_line"] = _named_below_line(home, notes)
    for name in sorted(battery.ORDINARY):
        for draw in range(CHANCE_DRAWS):
            texts = battery.ordinary(name, ASKED_ROWS, draw)
            numbers = [float(text) for text in texts]
            whole = all(value == int(value) for value in numbers)
            found = date_counts.asked_of(
                texts, numbers, taxonomy._needed(0.99, len(texts)), _median(sorted(numbers)), whole,
                floor=11,
            )
            if found is not None and asking.why_worth_asking(texts) is None:
                totals["new_questions"] += 1
                notes += [f"{name} draw {draw}: a new question"]
    return totals


HEAP_ROWS = 10000
HEAP_SHARES = (0.002, 0.01)


def _heaped(home: pathlib.Path, notes: "list[str]") -> "dict[str, int]":
    """Item 1 of the landing's review: a placeholder heaped into the published end, at 10,000 rows."""
    shapes = [shape for shape in battery.SHAPES if shape.name not in battery.NOT_ASKED]
    least = len(shapes)
    wrong = 0
    for kind in battery.PLACEHOLDERS:
        for share in HEAP_SHARES:
            columns: "list[list[str]]" = []
            spans: "list[tuple[int, int]]" = []
            for shape in shapes:
                cells, truth = battery.cells(shape, HEAP_ROWS, 0)
                columns += [battery.heaped(shape, cells, kind, share)]
                spans += [(min(t.year for t in truth), max(t.year for t in truth))]
            path = home / f"heap-{kind}-{share}.csv"
            rows = [",".join(shape.name for shape in shapes)]
            for place in range(HEAP_ROWS):
                rows += [",".join(column[place] for column in columns)]
            path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
            document = profile.build_document(reading.read_table(str(path)), taxonomy.Settings(), [])
            asked_here = 0
            for shape, block, span in zip(shapes, document["columns"], spans):
                said = asking._date_counts_said(block)
                if said is None:
                    continue
                asked_here += 1
                years = {member: (first, last) for member, first, last in said.readings}
                if shape.system not in years or max(
                    abs(years[shape.system][0] - span[0]), abs(years[shape.system][1] - span[1])
                ) > 1:
                    wrong += 1
                    notes += [f"{shape.name} {kind} {share}: {years.get(shape.system)} against {span}"]
            least = min(least, asked_here)
    return {"heap_10k_asked_least": least, "heap_10k_wrong": wrong}


def _named_below_line(home: pathlib.Path, notes: "list[str]") -> int:
    """Item 4: set-aside numbers NF113 names that fewer than eleven cells hold."""
    said_as = {"0": "0", "-1": "-1"}
    found = 0
    for shape in battery.SHAPES:
        if shape.name in battery.NOT_ASKED:
            continue
        cells, _truth = battery.cells(shape, ASKED_ROWS, 0)
        changed = list(cells)
        for place, kind in enumerate(battery.PLACEHOLDERS):
            changed[100 + 7 * place] = battery.placeholder(shape, kind)
        path = home / "below-line.csv"
        _write(path, changed)
        document = profile.build_document(reading.read_table(str(path)), taxonomy.Settings(), [])
        said = asking._date_counts_said(document["columns"][0])
        if said is None:
            continue
        for word in said.aside:
            if word in said_as and changed.count(said_as[word]) < 11:
                found += 1
                notes += [f"{shape.name}: NF113 names {word}, which fewer than eleven cells hold"]
    return found


def _twin_cells(path: pathlib.Path) -> "list[str]":
    rows = list(csv.reader(io.StringIO(path.read_text(encoding="utf-8"))))
    return [row[0] for row in rows[1:] if row]


def declared(home: pathlib.Path, notes: "list[str]") -> "dict[str, object]":
    """Every column declared, described, twinned and checked."""
    totals: "dict[str, object]" = {
        "not_read_as_dates": 0,
        "twin_cells_off_form": 0,
        "cells_not_round_tripped": 0,
        "missed": 0,
        "source_missed": 0,
    }
    worst = 0.0
    for rows, seeds in DECLARED_RUNS:
        for shape in battery.SHAPES:
            for seed in seeds:
                columns = [(shape.name, battery.cells(shape, rows, seed)[0])]
                for name in battery.RANGES:
                    columns += [(f"{shape.name}:{name}", battery.ranged(shape, name, rows, seed))]
                for label, cells in columns:
                    where = f"{label} at {rows}, seed {seed}"
                    tvd = _declared_one(home / f"{label.replace(':', '-')}-{rows}-{seed}", shape, cells, totals, where, notes)
                    if rows == TVD_ROWS and tvd is not None:
                        worst = max(worst, tvd)
    totals["weekday_tvd_10k"] = round(worst, 4)
    totals["contacts_half_off_points"] = round(float(f"{totals.pop('contacts_half_off_points', 0.0)}"), 3)
    totals.update(_figures_and_writers(home, notes))
    return totals


def _quiet_trip(folder: pathlib.Path, cells: "list[str]", system: str) -> "dict[str, object]":
    """Declared, described, twinned and checked through the command line: what came of it."""
    folder.mkdir(parents=True)
    table = folder / "real.csv"
    _write(table, cells)
    came: "dict[str, object]" = {"profile": _quiet(
        ["profile", str(table), "--date-count", "seen", system, "--out-dir", str(folder), "--replace"]
    )}
    if came["profile"] != 0:
        return came
    described = folder / "real-profile.json"
    loaded = contract.load_profile(str(described))
    came["facts"] = loaded.columns[0].facts
    came["holes"] = set(loaded.columns[0].missing_by_source)
    came["generate"] = _quiet(["generate", str(described), "--seed", "0", "--out-dir", str(folder), "--replace"])
    for label, checked in (("twin", folder / "real-twin.csv"), ("source", table)):
        out = folder / f"checked-{label}"
        out.mkdir()
        came[label] = _quiet(["validate", str(described), "--twin", str(checked), "--out-dir", str(out), "--replace"])
    came["twin_cells"] = _twin_cells(folder / "real-twin.csv")
    return came


def _written_back(system: str, cells: "list[str]", facts: object) -> int:
    """How many counted cells are not written back as themselves by the published form."""
    if not isinstance(facts, contract.DatetimeFacts) or facts.count_form is None:
        return len(cells)
    form = facts.count_form
    unit = contract.counted_unit(facts)
    moved = 0
    for cell in cells:
        written = date_counts.counted(system, cell, form.mark)
        if written is None:
            continue
        numerator, denominator = date_counts.exact_value(written)
        moment = date_counts.moment_of(system, numerator, denominator, unit)
        if moment is None or date_counts.written_for(system, moment, unit, form) != cell:
            moved += 1
    return moved


def _figures_and_writers(home: pathlib.Path, notes: "list[str]") -> "dict[str, int]":
    """Items 2, 3 and 5: figures no unit keeps, and the writers beside the battery's."""
    totals = {"coarse_misread": 0, "coarse_missed": 0, "writers_missed": 0}
    for name in sorted(battery.COARSE):
        system, _write_one, kept = battery.COARSE[name]
        cells = battery.coarse(name, ASKED_ROWS, 0)
        came = _quiet_trip(home / f"coarse-{name}", cells, system)
        facts = came.get("facts")
        read = isinstance(facts, contract.DatetimeFacts) and facts.count_form is not None
        if read != kept or (kept and _written_back(system, cells, facts)):
            totals["coarse_misread"] += 1
            notes += [f"{name}: read as dates {read}, kept {kept}"]
        if [came.get(step) for step in ("profile", "generate", "twin", "source")] != [0, 0, 0, 0]:
            totals["coarse_missed"] += 1
            notes += [f"{name}: exits {[came.get(step) for step in ('profile', 'generate', 'twin', 'source')]}"]
    for writer, shape_name in (
        ("repr", "xl_dt15g"), ("repr", "xl_dt6"), ("pandas_point_zero", "xl_date"),
        ("seventeen_significant", "epic_real"),
    ):
        shape = battery.BY_NAME[shape_name]
        cells = battery.written_by(writer, shape, ASKED_ROWS, 0)
        came = _quiet_trip(home / f"writer-{writer}-{shape_name}", cells, shape.system)
        facts = came.get("facts")
        read = isinstance(facts, contract.DatetimeFacts) and facts.count_form is not None
        twin = came.get("twin_cells") or []
        if writer == "seventeen_significant":
            ok = came.get("profile") == 0 and not read and came.get("twin") == 0
        else:
            ok = (
                read
                and [came.get(step) for step in ("profile", "generate", "twin", "source")] == [0, 0, 0, 0]
                and _written_back(shape.system, cells, facts) == 0
            )
            if writer == "repr":
                ok = ok and all(cell == repr(float(cell)) for cell in twin if cell)  # type: ignore[union-attr]
        if not ok:
            totals["writers_missed"] += 1
            notes += [f"{writer} {shape_name}: not read, written back and checked as written"]
    return totals


def _declared_one(
    folder: pathlib.Path,
    shape: "battery.Shape",
    cells: "list[str]",
    totals: "dict[str, object]",
    where: str,
    notes: "list[str]",
) -> "float | None":
    folder.mkdir(parents=True)
    table = folder / "real.csv"
    _write(table, cells)
    system = shape.system

    def count(key: str, said: str) -> None:
        nonlocal notes
        totals[key] = int(f"{totals[key]}") + 1
        notes += [f"{where}: {said}"]

    if _quiet(["profile", str(table), "--date-count", "seen", system, "--out-dir", str(folder), "--replace"]) != 0:
        count("not_read_as_dates", "not described")
        return None
    described = folder / "real-profile.json"
    loaded = contract.load_profile(str(described))
    column = loaded.columns[0]
    facts = column.facts
    if not isinstance(facts, contract.DatetimeFacts) or facts.count_form is None:
        count("not_read_as_dates", "not read as counted dates")
        return None
    form = facts.count_form
    unit = contract.counted_unit(facts)
    holes = set(column.missing_by_source)
    if _quiet(["generate", str(described), "--seed", "0", "--out-dir", str(folder), "--replace"]) != 0:
        count("missed", "no twin written")
        return None
    twin = folder / "real-twin.csv"
    out = folder / "checked"
    out.mkdir()
    if _quiet(["validate", str(described), "--twin", str(twin), "--out-dir", str(out), "--replace"]) != 0:
        count("missed", "the twin MISSED")
    out = folder / "source"
    out.mkdir()
    if _quiet(["validate", str(described), "--twin", str(table), "--out-dir", str(out), "--replace"]) != 0:
        count("source_missed", "the source MISSED its own description")
    fake = _twin_cells(twin)
    if form.contacts is not None and len(cells) == TVD_ROWS:
        words = [date_counts.contact_word(date_counts.written_count(cell)) for cell in fake if cell and cell not in holes]  # type: ignore[arg-type]
        total = sum(form.contacts.values())
        for half in (words[: len(words) // 2], words[len(words) // 2 :]):
            for word, count in form.contacts.items():
                gap = abs(half.count(word) / len(half) - count / total) * 100
                totals["contacts_half_off_points"] = max(float(f"{totals.get('contacts_half_off_points', 0.0)}"), gap)
    off = 0
    for cell in fake:
        if not cell or cell in holes:
            continue
        written = date_counts.written_count(cell, form.mark)
        if written is None or not date_counts.form_holds(form, written):
            off += 1
            continue
        numerator, denominator = date_counts.exact_value(written)
        if date_counts.moment_of(system, numerator, denominator, unit) is None:
            off += 1
    if off:
        totals["twin_cells_off_form"] = int(f"{totals['twin_cells_off_form']}") + off
        notes += [f"{where}: {off} twin cells off the form"]
    moved = 0
    contacts = date_counts.TABLE[system].contacts
    for cell in cells:
        written = date_counts.counted(system, cell, form.mark)
        if written is None or cell in holes:
            continue
        numerator, denominator = date_counts.exact_value(written)
        moment = date_counts.moment_of(system, numerator, denominator, unit)
        if moment is None:
            continue
        word = date_counts.contact_word(written) if contacts else date_counts.NO_CONTACT
        if date_counts.written_for(system, moment, unit, form, word) != cell:
            moved += 1
    if moved:
        totals["cells_not_round_tripped"] = int(f"{totals['cells_not_round_tripped']}") + moved
        notes += [f"{where}: {moved} source cells not written back as themselves"]
    if shape.kind != "date":
        return None
    real = [moment for moment in (battery.decode(system, cell) for cell in cells) if moment is not None]
    made = [moment for moment in (battery.decode(system, cell) for cell in fake if cell and cell not in holes) if moment is not None]
    return battery.tvd(battery.weekday_shares(real), battery.weekday_shares(made))


def main() -> int:
    notes: "list[str]" = []
    with tempfile.TemporaryDirectory() as folder:
        home = pathlib.Path(folder)
        value: "dict[str, object]" = dict(asked(home, notes))
        value.update(declared(home / "declared", notes))
    kpi_rules.emit(
        "K-S3-60", value, "; ".join(notes[:20]) if notes else "every shape asked as stated, read, written back and checked"
    )
    return 0


if __name__ == "__main__":
    if "--kpi" not in sys.argv[1:]:
        print(__doc__)
    sys.exit(main())
