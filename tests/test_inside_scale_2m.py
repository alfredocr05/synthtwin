"""Gate file of lane W5-2M: a table of 2,000,000 rows by 50 columns described and twinned within the memory a process is given.

THE PATIENT LAYER'S DESCRIBE. Every repeated column the layer reads
holds its codes a byte a row and its cells with their readings as places
in a palette of their pairs (`patient_intervals.HeldCells`), each pair
once, a byte a row up to 256 pairs, a large palette's whole readings as
numbers in bytes; the palette gives back every row's cell and reading as
they were, a cell spelled alike with two readings among them; and the description is the one the readings, cells and codes
made a row at a time give. Mutants: the codes held as numbers; the
palette keyed by the cell alone; its places a byte wider than they need;
a whole reading held without its sign;
every row given the first cell's reading; the cells as read; a coarser
level read through the finer level's map.

THE SCORES HELD AS BITS. The repeated numbers' latent scores, drawn for
every column at once, are held a column in eight bytes a row (and one
more for whether the row holds one) and given back as the very values put,
-0.0 apart from 0.0, a subnormal, an infinity and a value that is not a
number among them. Mutant: the scores kept to single precision.

EACH VALUE HELD ONCE. A column read back from the twin's held form holds
each different text as one object, its cells equal to the cells read.
Mutant: the cells handed on as read.

THE CELLS TAKEN. `applied` with `taken` works on the lists it is handed,
removing them from the caller's mapping, and gives back the columns it
gives back without it. Mutant: the lists copied and left with the caller.

THE COLUMNS DEALT HELD COMPACTLY. While the repeated numbers' scores are
drawn, no column the draw deals is held as a list of cells (the draw reads
which rows hold a number, a byte a row). Mutant: the columns left as lists.

THE SCORES' MEMORY. Every repeated number column dealt adds under 24 bytes
a row to what the dealing holds (a dictionary of floats a column took
about 85). Mutant: the scores held in a dictionary a column again.

THE TWIN IS THE SAME. The shipped commands on an invented visits table of
20,000 rows (the reliability battery's T2, the patient layer on) write the
twin pinned below (the public head's, moved only by lane TYPES-24's text zone), byte for byte, and the zone reads its columns
each value once; on a table of six repeated numbers dealt together,
`applied` gives the columns the public head gave. Mutants: the cells read
without `once_a_value`; the dealing given the scores of the next column.

THE CHECKS' RUNNING DIGESTS. The five twin-versus-real checks hold each
walk's four running digests (C1's row, C3's readings and dates, C5's
combination) as eight bytes a row, signed, read back as the numbers
written, and their two reports on the checks' own gate tables are the
public head's, byte for byte. Mutants: the words read back without their
sign; a side made with lists again.

THE DRAW'S WORDS. Each modelled column's draw words are held as eight
bytes a word, low byte first, and read back as the words drawn, a list's
and a store's alike; the twin they draw is the public head's (the T2
case above). Mutant: the words held as a list again.

THE HARNESS (tools/measurements/kpi_inside_scale.py). It reads the
quality report's census, its five outcome lines alone; it projects a
validate or checks step only where the twin was drawn from the record and
the step was measured; its clock names the stage that set a new peak,
a function of a second module under its module's name. Mutants are the
harness's own: a later line of the census's shape read as an outcome; a
checks line with no verdict admitted; the peak kept for every call.

Each clause is red on its mutant (lane W5-2M's report).
"""

from __future__ import annotations

import hashlib
import json
import math
import pathlib
import random
import tracemalloc
import typing

import pytest

from synthtwin import inside, inside_trajectories as I

PERSON = "patient_id"


def _bits(value: float) -> str:
    """A float's spelling with its sign, so -0.0 and 0.0 differ and a value that is not a number reads as itself."""
    return repr(value) if not math.isnan(value) else "nan"


def test_the_scores_held_as_bits_come_back_as_they_were_put() -> None:
    draw = random.Random(20261121)
    values = [0.0, -0.0, 5e-324, -5e-324, 2.2250738585072014e-308, -1e-310, 1.5, -2.75e300, 1.7976931348623157e308,
              float("inf"), float("-inf"), float("nan")]
    values += [draw.gauss(0.0, 3.0) for _ in range(500)] + [draw.uniform(-1e-300, 1e-300) for _ in range(100)]
    rows = 2 * len(values) + 7
    store = I.latent_store(rows)
    put: "dict[int, float]" = {}
    for at, value in enumerate(values):
        row = (2 * at + 3) % rows
        I.latent_put(store, row, value)
        put[row] = value
    # A later put replaces an earlier one, a value that is not a number by a number too.
    I.latent_put(store, (2 * 11 + 3) % rows, 0.25)
    put[(2 * 11 + 3) % rows] = 0.25
    got = I.latent_scores(store)
    assert list(got) == sorted(put)
    assert [_bits(got[row]) for row in got] == [_bits(put[row]) for row in sorted(put)]
    assert all(got[row] == put[row] for row in got if not math.isnan(put[row]))
    assert len(store.bits) == 0 and len(store.present) == 0 and store.odd == {}


def test_each_value_of_a_column_is_held_once() -> None:
    cells = [f"{k % 7}.5" for k in range(2000)] + [""] * 50
    held = I.once_a_value([str(cell) for cell in cells])
    assert held == cells
    assert len({id(cell) for cell in held}) == len(set(cells))


def _visits(patients: int, seed: int, numbers: int) -> "dict[str, list[str]]":
    """An invented visits table: an arm, an age, a visit number and date, ``numbers`` repeated readings and a yes/no."""
    # The patients' rows and dates from one stream, the readings from another: the same rows at any `numbers`.
    shape = random.Random(seed)
    draw = random.Random(seed + 1)
    names = [PERSON, "arm", "age", "visit", "visit_date"] + [f"n{k}" for k in range(numbers)] + ["event"]
    out: "dict[str, list[str]]" = {name: [] for name in names}
    for p in range(patients):
        visits = 1 + min(20, int(shape.expovariate(1 / 5.0)))
        arm = shape.random() < 0.5
        age = shape.randint(30, 80)
        levels = [draw.gauss(0.0, 12.0) for _ in range(numbers)]
        day = 18000 + shape.randrange(800)
        for k in range(visits):
            if k:
                day += shape.randint(25, 31)
            year, month, date = I.civil_from_days(day)
            row = {PERSON: f"P{100000 + p}", "arm": "B" if arm else "A", "age": f"{age}", "visit": f"{k + 1}",
                   "visit_date": f"{year:04d}-{month:02d}-{date:02d}",
                   "event": "Y" if draw.random() < 0.3 + 0.2 * arm else "N"}
            for j in range(numbers):
                row[f"n{j}"] = f"{int(round(130.0 + levels[j] + (j - 0.8 * arm) * k + draw.gauss(0.0, 8.0)))}"
            for name in names:
                out[name] += [row[name]]
    return out


@pytest.fixture(scope="module")
def wide() -> "tuple[dict[str, list[str]], dict[str, object]]":
    table = _visits(700, 5, 6)
    made = I.zone_from_columns(table, PERSON, (PERSON,))
    assert made is not None and len(made["numbers"]) >= 4  # type: ignore[arg-type]
    return table, made


def test_the_cells_taken_are_worked_on_once_and_the_columns_are_the_same(wide) -> None:  # type: ignore[no-untyped-def]
    table, zone = wide
    names = list(table)
    copied = {name: list(cells) for name, cells in table.items()}
    plain = I.applied(json.loads(json.dumps(zone)), names, copied, 3)
    assert copied == table
    handed = {name: list(cells) for name, cells in table.items()}
    taken = I.applied(json.loads(json.dumps(zone)), names, handed, 3, taken=True)
    assert handed == {}
    assert taken.columns == plain.columns and taken.order == plain.order
    # Worked on in place: in the dealing step, a column the zone does not deal comes back as the very list handed.
    handed = {name: list(cells) for name, cells in table.items()}
    lists = dict(handed)
    dealt = I.applied(json.loads(json.dumps(zone)), names, handed, 3, timing=False, taken=True)
    alone = I.applied(json.loads(json.dumps(zone)), names, {name: list(cells) for name, cells in table.items()}, 3,
                      timing=False)
    assert dealt.columns == alone.columns
    kept = [name for name in (PERSON, "arm", "age", "visit", "visit_date")]
    assert all(dealt.columns[name] is lists[name] for name in kept)


# The sha256 of `applied`'s columns and order on the wide fixture (six repeated numbers dealt together) at seed 3,
# on the public head e4d2e95b (lane W5-2M, before its change); moved by lane STATS-B alone, whose draw reads each
# patient's level and slope at the shares their shape holds its points at (7ed510c6... before it).
WIDE_APPLIED_SHA = "9dae08352e3b2e824a9c7389f04a0f2ca13b87324fcd6caff9855e5670bd4b5d"


def test_the_numbers_dealt_together_are_the_public_heads(wide) -> None:  # type: ignore[no-untyped-def]
    table, zone = wide
    got = I.applied(json.loads(json.dumps(zone)), list(table), {name: list(cells) for name, cells in table.items()}, 3)
    body = json.dumps({"columns": got.columns, "order": got.order}, sort_keys=True)
    assert len(typing.cast("list[object]", zone["numbers"])) >= 4
    assert hashlib.sha256(body.encode("utf-8")).hexdigest() == WIDE_APPLIED_SHA


def test_the_columns_dealt_are_held_compactly_while_their_scores_are_drawn(wide, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    table, zone = wide
    dealt = [str(entry["column"]) for entry in typing.cast("list[dict[str, object]]", zone["numbers"])]
    seen: "list[int]" = []
    drawing: "list[bool]" = []
    original = I._entry_time
    numbers = I._numbers_dealt

    def watched(entry: "dict[str, object]", work: "dict[str, list[str]]", *rest: typing.Any) -> float:
        if drawing:
            seen.append(sum(len(work[name]) for name in dealt if name in work))
        return original(entry, work, *rest)

    def drawn(*args: typing.Any, **options: typing.Any) -> None:
        drawing.append(True)
        try:
            numbers(*args, **options)
        finally:
            drawing.clear()

    monkeypatch.setattr(I, "_entry_time", watched)
    monkeypatch.setattr(I, "_numbers_dealt", drawn)
    got = I.applied(json.loads(json.dumps(zone)), list(table), {name: list(cells) for name, cells in table.items()}, 3,
                    timing=False)
    assert seen and max(seen) == 0
    assert all(len(got.columns[name]) == len(table[PERSON]) for name in dealt)


def _dealing_peak(table: "dict[str, list[str]]", zone: "dict[str, object]") -> int:
    """The most bytes `tracemalloc` saw held by `applied`'s dealing step on the table, above what it held before."""
    names = list(table)
    handed = {name: list(cells) for name, cells in table.items()}
    tracemalloc.start()
    try:
        before = tracemalloc.get_traced_memory()[0]
        I.applied(zone, names, handed, 3, timing=False, taken=True)
        return tracemalloc.get_traced_memory()[1] - before
    finally:
        tracemalloc.stop()


def test_each_number_column_dealt_adds_a_few_bytes_a_row_to_what_the_dealing_holds() -> None:
    narrow_table = _visits(1500, 9, 2)
    wide_table = _visits(1500, 9, 10)
    rows = len(wide_table[PERSON])
    assert rows == len(narrow_table[PERSON]) and rows > 5000
    narrow_zone = I.zone_from_columns(narrow_table, PERSON, (PERSON,))
    wide_zone = I.zone_from_columns(wide_table, PERSON, (PERSON,))
    assert narrow_zone is not None and wide_zone is not None
    dealt = len(typing.cast("list[object]", wide_zone["numbers"])) - len(typing.cast("list[object]", narrow_zone["numbers"]))
    assert dealt >= 6
    per_column_row = (_dealing_peak(wide_table, wide_zone) - _dealing_peak(narrow_table, narrow_zone)) / (dealt * rows)
    assert per_column_row < 24.0, per_column_row


# -- the commands: the twin the public head wrote -----------------------------------------------------------------

# The sha256 of the twin `synthtwin generate` writes at seed 0 for the reliability battery's T2 table at 20,000 rows
# (table seed 2), described by `synthtwin profile` with the patient layer on: the twin of this tree must be the same
# bytes. Lane W5-2M pinned its base e4d2e95b's twin (c8f79c76...), which its branch wrote too. AT BATCH 4Z'S MERGE
# the route's twin moved with lane ZOO-Y's passes on it (the real-range pass, plan P4-D517): lane ZOO-Y's branch
# alone (d498bb21) writes 3ecaa3b8..., and so does the merged line with W5-2M's compact stores on top, so the pin is
# the line's own and W5-2M's change stays byte neutral (measured on the three trees, 2026-11-22).
# ...moved by lane STATS-B alone (3ecaa3b8... before it: 7128e0de... on its branch), whose draw reads each patient's
# level and slope at the shares their shape holds its points at, and whose relations zone reads again, given the chosen
# parents, each one its screen left out (the visits table's twin, every other step as it was). LANE TYPES-24's text
# zone moves it on purpose (its measurement columns dealt from the real census in the order the relations zone drew
# them): its tree with the zone's entries switched off writes 3ecaa3b8... still, and with them 624dff3c... (measured
# 2026-11-23), so nothing else of that lane moves the route's twin. LANE IN-5's dates zone (every twin date kept inside
# its column's real months) moves it too: its branch alone writes 5f98408e..., and lane STATS-A's on top of it the
# same. THE BATCH 4ZZ LINE, with all three, writes 018fce2f... (measured on the merged tree, 2026-11-23).
T2_TWIN_SHA = "018fce2ff2510f1153daa5fa0de7601ef83264d44016fc66dec84693d217b20a"


def test_the_shipped_commands_write_the_twin_the_public_head_wrote(tmp_path: pathlib.Path,
                                                                     monkeypatch: "pytest.MonkeyPatch") -> None:
    import reliability_battery as B
    import reliability_tables as T

    from synthtwin import cli, installation

    def places() -> inside.Places:
        return inside.Places(pathlib.Path(installation.data_folder(), inside.FOLDER), (), (), installation.system_name())

    handed: "list[float]" = []
    original = I.applied

    def watched(zone: object, names: "list[str]", cells_of: "dict[str, list[str]]", seed: int,
                **options: typing.Any) -> I.Applied:
        if options.get("taken") and cells_of:
            cells = cells_of[names[0]]
            handed.append(len({id(cell) for cell in cells}) / max(1, len(set(cells))))
        return original(zone, names, cells_of, seed, **options)  # type: ignore[arg-type]

    monkeypatch.setattr(cli, "_PATIENT_LAYER_SHIPPED", True)
    monkeypatch.setattr(cli, "_INSIDE_RECORD_SHIPPED", True)
    monkeypatch.setattr(inside, "default_places", places)
    monkeypatch.setattr(I, "applied", watched)
    product = B.make_twins(pathlib.Path(f"{tmp_path}"), "T2", T.text("T2", 20000, 2), (0,), True)
    assert product.errors == {} and 0 in product.twins
    assert handed and max(handed) == 1.0, handed
    assert hashlib.sha256(product.twins[0].encode("utf-8")).hexdigest() == T2_TWIN_SHA


# -- the harness: the steps after the twin, and the stage that drives a step's peak --------------------------------

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
HARNESS = pathlib.Path(REPO_ROOT, "tools", "measurements", "kpi_inside_scale.py")


def _harness(code: str, tmp_path: pathlib.Path) -> str:
    """Run ``code`` in a process of its own with the harness imported as ``H`` (its guard alters that process alone)."""
    import os
    import subprocess
    import sys

    program = ("import sys\nsys.path.insert(0, " + repr(f"{HARNESS.parent}") + ")\nsys.argv = ['kpi_inside_scale.py']\n"
               "import kpi_inside_scale as H\n" + code)
    done = subprocess.run([sys.executable, "-c", program], capture_output=True, text=True, check=False,
                          env=dict(os.environ), cwd=f"{tmp_path}", timeout=300)
    assert done.returncode == 0, done.stderr[-2000:]
    return done.stdout


def test_the_harness_reads_the_quality_reports_census(tmp_path: pathlib.Path) -> None:
    from synthtwin import quality, validation

    counts = {validation.HELD: 2297, validation.WITHIN_BOUND: 41, validation.AUTHORIZED_DEVIATION: 153,
              validation.WITHHELD: 0, validation.MISSED: 6}
    lines = ["", "This description sets 2497 obligation(s) that a written file can be",
             "checked against. Each one landed on exactly one of five outcomes:", ""]
    lines += [f"  {counts[verdict]:>6}  {verdict} -- {quality._VERDICT_WORDS[verdict]}" for verdict in counts]
    lines += ["", "6 CHECKABLE OBLIGATION(S) WERE MISSED.", "  12  the first -- of the misses, never a census line"]
    report = pathlib.Path(tmp_path, "report.txt")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    said = _harness(f"import json, pathlib\nprint(json.dumps(H._quality_counts(pathlib.Path({str(report)!r})"
                    f".read_text(encoding='utf-8'))))", tmp_path)
    got = json.loads(said.strip().splitlines()[-1])
    assert got == {"obligations": 2497, **{verdict.replace(" ", "_"): count for verdict, count in counts.items()}}


def test_the_harness_projects_validate_and_checks_only_on_a_twin_drawn_from_the_record(tmp_path: pathlib.Path) -> None:
    import subprocess
    import sys

    def line(step: str, rows: int, **fields: object) -> str:
        found: "dict[str, object]" = {"step": step, "exit": 0, "shape": "dense", "rows": rows, "columns": 50,
                                      "seconds": rows / 100.0, "cpu_seconds": rows / 100.0, "peak_rss_mb": 100.0 + rows / 1000.0,
                                      "inside_seconds": {"measure": rows / 200.0}, "raised_peak_mb": {"measure": 90.0}}
        found.update(fields)
        return "RESULT " + json.dumps(found, sort_keys=True)

    lines = [line("validate", rows, exit=3, drawn_columns=48) for rows in (100000, 500000)]
    lines += [line("checks", rows, drawn_columns=48, checks_measured=5) for rows in (100000, 500000)]
    lines += [line("validate", 100000, drawn_columns=0, shape="plain"), line("validate", 500000, exit=1, drawn_columns=48,
                                                                         shape="plain")]
    lines += [line("checks", rows, drawn_columns=48, checks_measured=0, shape="plain") for rows in (100000, 500000)]
    results = pathlib.Path(tmp_path, "results.txt")
    results.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    done = subprocess.run([sys.executable, f"{HARNESS}", "project", f"{results}"], capture_output=True, text=True,
                          check=False, cwd=f"{tmp_path}", timeout=300)
    assert done.returncode == 0, done.stderr[-2000:]
    projected = [json.loads(text[len("PROJECTED "):]) for text in done.stdout.splitlines() if text.startswith("PROJECTED ")]
    assert sorted((each["shape"], each["step"]) for each in projected) == [("dense", "checks"), ("dense", "validate")]
    assert any(text.startswith("REFUSED 4 ") for text in done.stdout.splitlines()), done.stdout[-2000:]
    validate = [each for each in projected if each["step"] == "validate"][0]
    assert validate["peak_rss_mb"]["at"] == pytest.approx(2100.0) and "measure" in validate["raised_peak_mb"]


def test_the_harness_clock_names_the_stage_that_raised_the_peak(tmp_path: pathlib.Path) -> None:
    said = _harness(
        "import json, types\n"
        "peaks = iter([100.0, 100.0, 100.0, 180.0, 180.0, 180.0, 180.0, 250.0, 250.0, 250.0])\n"
        "H._peak_rss_mb = lambda: next(peaks)\n"
        "one = types.SimpleNamespace(__name__='synthtwin.one', quiet=lambda: 1, grow=lambda: 2)\n"
        "two = types.SimpleNamespace(__name__='synthtwin.two', grow=lambda: 3)\n"
        "clock = H.Clock(False)\n"
        "clock.wrap(one, 'quiet'); clock.wrap(one, 'grow'); clock.wrap(two, 'grow')\n"
        "one.quiet(); one.grow(); one.quiet(); two.grow()\n"
        "print(json.dumps({'peaks': clock.raised_peak_mb, 'seconds': sorted(clock.seconds)}))\n",
        tmp_path)
    got = json.loads(said.strip().splitlines()[-1])
    assert got["peaks"] == {"grow": 180.0, "two.grow": 250.0}
    assert got["seconds"] == ["grow", "quiet", "two.grow"]


# -- the patient layer's describe: each different cell and reading held once, codes a byte a row ---------------------


def _layer_visits(patients: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """An invented visits table of several rows a person: an arm, a visit date, two readings and a site."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for patient in range(patients):
        arm = draw.choice(["a", "b"])
        base = draw.gauss(100, 12)
        for j in range(draw.randint(2, 8)):
            day = 1 + 30 * j + draw.randint(0, 5)
            date = f"{2024 + day // 336}-{1 + (day // 28) % 12:02d}-{1 + day % 28:02d}"
            rows += [[f"S{patient:05d}", arm, date, f"{base + (1.5 if arm == 'b' else 0.3) * j + draw.gauss(0, 6):.1f}",
                      f"{draw.gauss(5.0, 1.0):.1f}", draw.choice(["clinic", "home", "phone"])]]
    return ["pid", "arm", "visit_date", "value", "second", "site"], rows


def _layer_described(folder: pathlib.Path, monkeypatch: "pytest.MonkeyPatch",
                     made: "list[object]") -> "dict[str, object]":
    import dataclasses

    import fixtures
    from synthtwin import chain, patient_layer, profile, reading, taxonomy

    original = patient_layer._RowColumn

    def kept(*args: typing.Any) -> object:
        column = original(*args)
        made.append(column)
        return column

    monkeypatch.setattr(patient_layer, "_RowColumn", kept)
    header, rows = _layer_visits(1500, 4)
    folder.mkdir(parents=True, exist_ok=True)
    text = ",".join(header) + "\n" + "".join(",".join(row) + "\n" for row in rows)
    path = fixtures.write(folder, "visits.csv", text)
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=11), person_columns=("pid",))
    table = reading.read_table(str(path), small_cell_floor=11)
    document = profile.build_document(table, settings, ["pid"], [], [], subjects=["pid"])
    chained = chain.describe(table, document, settings,
                             chain.ChainSwitch("visits", bytes(range(32)), (), rows_per_person=chain.ROWS_PERSON,
                                               trajectories=False))
    monkeypatch.setattr(patient_layer, "_RowColumn", original)
    assert chained.grain is not None
    return json.loads(json.dumps(chain.with_rules(document, chained) | {"grain": chained.grain,
                                                                          "columns": chained.columns}))


def test_the_patient_layer_holds_each_reading_once_and_its_codes_a_byte_a_row(tmp_path: pathlib.Path,
                                                                             monkeypatch: "pytest.MonkeyPatch") -> None:
    from synthtwin import patient_intervals as pi, patient_layer

    made: "list[typing.Any]" = []
    lean = _layer_described(pathlib.Path(tmp_path, "lean"), monkeypatch, made)
    assert made
    for column in made:
        assert all(isinstance(level, bytes) for level in column.codes), column.name
        cells = column.cells
        pairs = list(zip(cells.texts, pi.palette_readings(cells)))
        assert len(set(pairs)) == len(pairs) and cells.rows == len(column.codes[0]), column.name
        assert len(cells.places) == cells.width * cells.rows and (cells.width == 1) == (len(pairs) <= 256), column.name
        # The coarser levels read from the L0 codes are the three levels the codes were made with.
        three = patient_layer._codes_three(column.ladder, list(column.codes[0]))
        assert [list(patient_layer._codes_at_level(column, level)) for level in range(3)] == [list(one) for one in three]
        assert len(column.codes) == 1, column.name
    # The same description as the readings, cells and codes made a row at a time.
    monkeypatch.setattr(patient_layer, "_held_once", lambda cells: list(cells))
    monkeypatch.setattr(patient_layer, "_codes_held", patient_layer._codes_three)

    def per_row(texts: "list[str]", meaning: "dict[str, tuple[str, object]]", role: str,
                block: "dict[str, object]") -> "list[object]":
        out: "list[object]" = []
        for text in texts:
            kind, value = meaning[text] if text in meaning else ("missing", None)
            out += [patient_layer._reading(role, value, block) if kind == "value" else None]
        return out

    monkeypatch.setattr(patient_layer, "_readings_once", per_row)
    assert _layer_described(pathlib.Path(tmp_path, "plain"), monkeypatch, []) == lean


def test_a_columns_cells_held_as_places_in_a_palette_come_back_as_they_were() -> None:
    from fractions import Fraction

    from synthtwin import patient_intervals as pi

    for count in (3, 256, 257, 65536, 65537):
        texts = [f"{k % count}" for k in range(count + 400)]
        readings: "list[Fraction | None]" = [None if k % count == 1 else Fraction(k % count, 4) for k in range(count + 400)]
        # One cell spelled alike with two readings, as no reader writes it: each pair is its own place.
        texts[5] = texts[4]
        held = pi.held_cells(texts, readings)
        assert pi.texts_of(held) == texts and pi.readings_of(held) == readings
        assert [pi.text_at(held, row) for row in (0, 4, 5, count - 1)] == [texts[row] for row in (0, 4, 5, count - 1)]
        assert pi.reading_at(held, 5) == readings[5]
        assert held.width == (1 if len(held.texts) <= 256 else 2 if len(held.texts) <= 65536 else 3)
        assert len(held.places) == held.width * len(texts)
    # A large palette of whole readings (a stamp's seconds, negative and past 32 bits among them) holds them in bytes.
    texts = [f"t{k}" for k in range(pi.WHOLE_FROM + 50)]
    readings = [None if k % 97 == 0 else Fraction((k - 2000) * 86400 * 365 * 70) for k in range(pi.WHOLE_FROM + 50)]
    held = pi.held_cells(texts, readings)
    assert held.whole and held.readings == ()
    assert pi.readings_of(held) == readings and pi.palette_readings(held) == readings
    assert all(isinstance(value, Fraction) for value in pi.readings_of(held) if value is not None)
    # ...and a palette whose readings are not all whole keeps them as they are.
    readings[7] = Fraction(1, 3)
    kept = pi.held_cells(texts, readings)
    assert not kept.whole and pi.readings_of(kept) == readings


def test_a_cell_list_held_once_is_the_same_cells() -> None:
    from synthtwin import patient_layer

    cells = [str(k % 5) for k in range(400)]
    held = patient_layer._held_once([f"{cell}" for cell in cells])
    assert held == cells and len({id(cell) for cell in held}) == 5


# -- the five twin-versus-real checks: each walk's running digests held as words ------------------------------------

# The sha256 of the checks' two reports on tests/test_twin_checks.py's own tables (a clean twin; a twin holding a
# real patient's readings and stamps in another order) on the public head e4d2e95b (lane W5-2M, before its change).
CHECKS_REPORTS_SHA = "a87c7acb5f7c2b68d829e10560360da26ee0ad7e9d13cb592fb8b90b18c1d7fd"


def test_the_checks_hold_each_walks_digests_as_words_and_report_as_the_public_head(tmp_path: pathlib.Path) -> None:
    import test_twin_checks as C

    from synthtwin import twin_checks as K

    values = [0, 1, -1, -(1 << 63), (1 << 63) - 1, hash(("a", 7)), hash((-3, 11))]
    words = K._words_held(values)
    assert len(words) == 8 * len(values) and K._words_listed(words) == values
    assert [K._word(words, at) for at in range(len(values))] == values
    column = [hash(f"cell {k}") for k in range(len(values))]
    assert K._words_listed(K._held_words(K._fold_in(values, column))) == [hash((before, digest))
                                                                         for before, digest in zip(values, column)]
    real = C._visits(1, "P", C.RELATIVES_REAL)
    clean = C._visits(2, "Q", C.RELATIVES_TWIN)
    source = C._real_patient(real, "P000003")
    own = C._real_patient(clean, "Q000003")
    made = []
    for at in range(len(source)):
        row = source[len(source) - 1 - at]
        mine = own[at % len(own)]
        made += [["Q000003", row[1], row[2], mine[3], mine[4], row[5], row[6], f"QR{900000000 + at}", mine[8]]]
    sides: "list[typing.Any]" = []
    original = K._check_rows

    def watched(real_side: typing.Any, real_read: typing.Any, twin_side: typing.Any) -> typing.Any:
        sides.extend([real_side, twin_side])
        return original(real_side, real_read, twin_side)

    K._check_rows = watched  # type: ignore[assignment]
    try:
        one = K.report_text(C._checked(tmp_path, real, clean))
        two = K.report_text(C._checked(tmp_path, real, C._swap_patient(clean, "Q000003", made)))
    finally:
        K._check_rows = original  # type: ignore[assignment]
    assert hashlib.sha256((one + two).encode("utf-8")).hexdigest() == CHECKS_REPORTS_SHA
    # Each walk's four running digests are words once it ends.
    assert len(sides) == 4 and all(isinstance(held, bytearray) and len(held) == 8 * side.rows
                                   for side in sides
                                   for held in (side.row_digest, side.reading_digest, side.date_digest, side.combination))


# -- the draw: each column's words held as eight bytes a word --------------------------------------------------------


def test_the_draw_holds_a_columns_words_as_bytes_and_reads_them_as_drawn(monkeypatch: "pytest.MonkeyPatch") -> None:
    import test_inside_relations as Rt

    from synthtwin import inside_relations as R, twinstore

    words = [0, 1, 255, 256, (1 << 64) - 1, 1 << 63, 0x0123456789ABCDEF]
    held = bytearray()
    for word in words:
        held += bytes((word >> shift) & 255 for shift in range(0, 64, 8))
    assert [R._word(held, at) for at in range(len(words))] == words == [R._word(words, at) for at in range(len(words))]
    assert R._word_count(held) == R._word_count(words) == len(words)
    seen: "list[object]" = []
    for name in ("redeal_number", "redeal_label", "draw_number", "draw_label"):
        original = getattr(R, name)

        def watched(*args: typing.Any, _original: typing.Any = original, _name: str = name, **options: typing.Any) -> typing.Any:
            seen.append(args[2] if _name.startswith("redeal") else args[3])
            return _original(*args, **options)

        monkeypatch.setattr(R, name, watched)
    columns = Rt._visit_table(600, 1)
    zone = Rt._zone(columns, {"arm": Rt.KINDS_LABEL, "visit": Rt.KINDS_NUMBER, "pressure": Rt.KINDS_NUMBER}, person="pid")
    held_columns = {name: twinstore.held_column(cells) for name, cells in columns.items()}
    R.draw_columns(zone, Rt._person_profile(columns), held_columns, 7)  # type: ignore[arg-type]
    assert len(seen) == 2 and all(isinstance(each, bytearray) and len(each) % 8 == 0 and len(each) for each in seen)
