"""Gate file of batch 4x's outside review and fix round (plan P4-D503): the keyed zone's own switch and five items.

Each case is red on the merged 4x head before the fix round (6c098098) and
on a mutant of its fix (named in the case; the fix round's report lists
each run).

* THE KEYED ZONE'S OWN SUB-SWITCH (items 1, 2, 5 and 6 and the merged
  head's validate misses on the long keyed tables, which lane IN-4b
  closed, plan P4-D504). On the shipped route, the battery's charting
  table at the table floor: the switch is on, the inside record holds
  the keyed zone (lane IN-4, plan P4-D499), validate exits 0 and misses
  nothing of the person column's repetition pattern; set off in place,
  a record that holds the zone is drawn without it, byte for byte the
  twin of a record written with the switch off, which holds none.
  Mutants: the record written with the zone whatever the switch; the
  zone drawn whatever the switch.
* ITEM 3. A number held once a person and worn inside a unit (`72.5 kg`)
  keeps its unit on every twin cell. Mutant: the person-level writer
  drops the wrapper.
* ITEM 4. A number held once a person, where the persons with many rows
  hold the high values: the twin's rows keep the description's twin's
  mean and its rows below a cut, for each person takes the cell in the
  middle of the block of that twin's sorted numbers its rows cover (a
  quantile over persons weighted by their rows). Mutant: the persons'
  quantiles unweighted.
* ITEM 7. Through the commands at the floor, a table of kept columns
  alone (a key, a free remark, two dates) opening with 500 blank records:
  the twin's all-empty records stay where the description's twin holds
  them. Mutants: the dates' dealing without the mask (39 all-empty
  records left, none leading); the other kept columns' without it (500,
  none leading).
* ITEM 11. Validate excuses the calendar counts of a date column only
  where the twin's report names it among the columns drawn from the
  record: a dates zone the writer refuses (another version) leaves the
  column's misses standing. Mutant: eligibility read from the record
  alone.
* ITEM 14. The scale harness projects only steps that wrote or drew from
  an inside record: a profile with no record and a generate with no
  column drawn are refused. Mutant: admission by the exit code alone.
"""

from __future__ import annotations

import contextlib
import csv
import datetime
import io
import json
import os
import pathlib
import random
import subprocess
import sys

import pytest

import reliability_battery as B
import reliability_tables as T
import test_inside_missing as M
from synthtwin import cli, inside, inside_relations as R, installation, validation

ROWS = 20000
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _places(folder: pathlib.Path) -> inside.Places:
    return inside.Places(pathlib.Path(folder, "installation", "synthtwin", "inside"), (), (),
                         installation.system_name(), ())


def _records(folder: pathlib.Path) -> "list[pathlib.Path]":
    return sorted(_places(folder).private.glob(f"*{inside.SUFFIX}"))


# -- the keyed zone's own sub-switch -------------------------------------------------------------------------


def _generated(folder: pathlib.Path, description: pathlib.Path, seed: int) -> str:
    """`synthtwin generate` of the description at one seed, the record in the folder's own private place."""
    out = description.parent
    with B.installed(folder):
        code, said = B.command(["generate", f"{description}", "--out-dir", f"{out}", "--seed", f"{seed}",
                                "--replace"], False)
    assert code == 0, said[-600:]
    return pathlib.Path(out, "charting-twin.csv").read_text(encoding="utf-8")


def _validated(folder: pathlib.Path, description: pathlib.Path) -> "tuple[int, list[tuple[str, str]]]":
    """`synthtwin validate` of the description's twin beside it: its exit code and the MISSED checks after the relabel."""
    seen: "dict[str, list[tuple[str, str]]]" = {"missed": []}
    original = cli._outcome_of_a_drawn_twin

    def watched(described, checked, outcome):  # type: ignore[no-untyped-def]
        after = original(described, checked, outcome)
        seen["missed"] = [(each.column, each.fact) for each in after.checks if each.verdict == validation.MISSED]
        return after

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(cli, "_outcome_of_a_drawn_twin", watched)
        with B.installed(folder), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = int(cli.main(["validate", f"{description}", "--replace"], small_tables_refused=False))
    return code, seen["missed"]


def test_the_keyed_zone_has_its_own_switch_and_is_on_on_the_shipped_route(tmp_path: pathlib.Path) -> None:
    folder = tmp_path / "product"
    text = T.text("T3", ROWS, 1)
    person = T.PERSON["T3"]
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inside, "default_places", lambda: _places(folder))
        # The shipped route: the inside record on and the keyed zone's own switch on (lane IN-4b, plan P4-D504).
        assert cli._inside_record_switched_on() and cli._keyed_zone_switched_on()
        product = B.make_twins(folder, "T3", text, (0,), False)
        assert not product.errors, product.errors
        description = pathlib.Path(folder, "out", "charting-profile.json")
        records = _records(folder)
        assert len(records) == 1
        zones = inside.load_record(records[0])["zones"]
        assert "relations" in zones and "keyed" in zones, sorted(zones)
        shipped = product.twins[0]
        code, missed = _validated(folder, description)
        assert (person, "identifier.n_distinct_by_occurrences") not in missed, missed
        assert code == 0, missed
        # The switch off in place: a record holding the keyed zone is drawn without it ...
        patch.setattr(cli, "_KEYED_ZONE_SHIPPED", False)
        drawn_without = _generated(folder, description, 0)
        # ... and the record is written without it.
        again = B.make_twins(folder, "T3", text, (0,), False)
        assert not again.errors, again.errors
        zones = inside.load_record(_records(folder)[0])["zones"]
        assert "keyed" not in zones, sorted(zones)
        written_without = again.twins[0]
    # Compared as truth values: pytest's account of two unequal twins of a megabyte would take minutes.
    changed = drawn_without != shipped
    same = drawn_without == written_without
    assert changed, "the keyed zone changed nothing: the case would not see it drawn"
    assert same, "a record's keyed zone was drawn with its switch off"


# -- items 3 and 4: a number held once a person ----------------------------------------------------------------


def _person_entry(decimals: int, grid: "list[float]", wrapper: "list[str] | None" = None) -> "dict[str, object]":
    """A number column held once a person, every row a number, its score the residuals alone (no parent); `grid` is the
    zone's quantile function over the real persons (`inside_relations.encode` describes such a column a person)."""
    entry: "dict[str, object]" = {
        "name": "x", "place": 0, "kind": R.NUMBER, "level": R.PATIENT,
        "grid": grid, "decimals": decimals, "atoms": [], "spikes": [None, None],
        "top": 0, "states": [1000, 0, 0, 0, 0], "presence": None,
        "value": {"terms": [["one"]], "coefficients": [0.0], "spread": 1.0,
                  "residuals": [float(k - 20) / 10.0 for k in range(R.RESIDUAL_POINTS)]},
    }
    if wrapper is not None:
        entry["wrapper"] = wrapper
    return entry


def _words(count: int, seed: int) -> "list[int]":
    draw = random.Random(f"review-4x-words-{seed}")
    return [draw.getrandbits(64) for _ in range(count)]


def _persons(sizes: "list[int]", seed: int) -> "list[list[int]]":
    """Persons of the given sizes over rows in a shuffled order (each person's rows in row order)."""
    rows = sum(sizes)
    order = list(range(rows))
    random.Random(f"review-4x-persons-{seed}").shuffle(order)
    out: "list[list[int]]" = []
    at = 0
    for size in sizes:
        out += [sorted(order[at:at + size])]
        at += size
    return out


def test_item_3_a_number_worn_inside_a_unit_keeps_it_held_once_a_person() -> None:
    rows_of = _persons([20] * 1000, 3)
    rows = 20000
    strict = [f"{40.5 + (k % 100):.1f} kg" for k in range(rows)]
    grid = [40.5 + 99.0 * k / (R.GRID - 1) for k in range(R.GRID)]
    entry = _person_entry(1, grid, ["", " kg"])
    drawn = R.redeal_number(entry, {}, _words(2 * rows, 3), strict, R.Dealing(rows, None, rows_of))
    cells = [cell for cell in drawn.cells if cell is not None]
    assert len(cells) == rows
    assert all(cell[-3:] == " kg" for cell in cells), sorted(set(cell for cell in cells if cell[-3:] != " kg"))[:5]
    for person in rows_of:
        assert len(set(drawn.cells[row] for row in person)) == 1
    assert set(cells) <= set(strict)


def test_item_4_the_rows_keep_their_mean_where_long_persons_hold_high_values() -> None:
    sizes = [2] * 500 + [38] * 500
    rows = sum(sizes)
    rows_of = _persons(sizes, 4)
    draw = random.Random("review-4x-values")
    # The description's twin's cells, row by row (it carries no person): 1,000 rows near 45, 19,000 near 105.
    strict = [f"{draw.gauss(45.0, 2.0):.1f}" for _ in range(1000)] + [f"{draw.gauss(105.0, 2.0):.1f}" for _ in range(19000)]
    draw.shuffle(strict)
    mean = sum(float(cell) for cell in strict) / rows
    # The zone's quantile function over the real persons: half of them near 45, half near 105 (each person once).
    half = R.GRID // 2
    grid = [43.0 + 4.0 * k / half for k in range(half)] + [103.0 + 4.0 * k / (R.GRID - half) for k in range(R.GRID - half)]
    for seed in (4, 7):
        drawn = R.redeal_number(_person_entry(1, grid), {}, _words(2 * rows, seed), strict, R.Dealing(rows, None, rows_of))
        values = [float(str(cell)) for cell in drawn.cells]
        assert abs(sum(values) / rows - mean) < 1.0, (seed, sum(values) / rows, mean)
        below = sum(1 for value in values if value < 50.0)
        assert abs(below - 1000) <= 100, (seed, below)
        for person in rows_of:
            assert len(set(drawn.cells[row] for row in person)) == 1


# -- item 7: the all-empty records through the commands --------------------------------------------------------


def _blank_led_text(rows: int, seed: int) -> str:
    """An invented table of kept columns alone (a key a row, a free remark, two dates, each empty on some rows), opening
    with 500 blank records: no modelled column tells the missing-values zone where the blank records lie, so its
    latent emptiness is the dealing's alone there (lane IN-7's table, whose modelled columns are empty on such a
    record, would keep them empty by its fit and hide the mask)."""
    draw = random.Random(f"review-4x-blank-led-{seed}")
    lines = [f"{M.PERSON},remark,start_day,end_day"] + [",,,"] * 500
    first = datetime.date(2021, 1, 4)
    for row in range(rows):
        admit = first + datetime.timedelta(days=draw.randrange(900))
        remark = " ".join(draw.choice(M.WORDS) for _k in range(draw.randrange(5, 9))) if draw.random() < 0.4 else ""
        start = admit.isoformat() if draw.random() < 0.8 else ""
        end = (admit + datetime.timedelta(days=1 + int(draw.expovariate(0.2)))).isoformat() if draw.random() < 0.7 else ""
        lines += [f"P{2000000 + row},{remark},{start},{end}"]
    return "\n".join(lines) + "\n"


def test_item_7_the_twin_keeps_the_all_empty_records_the_description_keeps(tmp_path: pathlib.Path) -> None:
    folder = tmp_path / "product"
    source = pathlib.Path(folder, "table", "stays.csv")
    out = pathlib.Path(folder, "out")
    source.parent.mkdir(parents=True)
    out.mkdir(parents=True)
    source.write_text(_blank_led_text(ROWS, 3), encoding="utf-8", newline="\n")
    questions = pathlib.Path(out, "stays-questions.json")
    with pytest.MonkeyPatch.context() as patch, B.installed(folder):
        patch.setattr(inside, "default_places", lambda: _places(folder))
        code, said = M._run(["profile", f"{source}", "--out-dir", f"{out}", "--replace"])
        for _round in range(4):
            assert code == 0, said[-600:]
            if not M._answer(questions):
                break
            code, said = M._run(["profile", f"{source}", "--out-dir", f"{out}", "--answers", f"{questions}"])
            if code != 0:
                code, said = M._run(["profile", f"{source}", "--out-dir", f"{out}", "--answers", f"{questions}",
                                     "--replace-description"])
        assert code == 0, said[-600:]
        code, said = M._run(["generate", f"{pathlib.Path(out, 'stays-profile.json')}", "--out-dir", f"{out}",
                             "--seed", "0", "--replace"])
        assert code == 0, said[-600:]
    records = _records(folder)
    assert len(records) == 1
    from synthtwin import inside_missing

    record = inside.load_record(records[0])
    carried = set(inside_missing.carried(inside_missing.zone_of(record)))
    assert {"start_day", "end_day", "remark"} <= carried, carried
    report = pathlib.Path(out, "stays-twin-report.txt").read_text(encoding="utf-8")
    assert report.startswith(cli._INSIDE_REPORT_HEAD)
    rows = list(csv.reader(io.StringIO(pathlib.Path(out, "stays-twin.csv").read_text(encoding="utf-8"))))[1:]
    empty = [all(not cell.strip() for cell in row) for row in rows]
    assert len(rows) == ROWS + 500
    leading = 0
    while leading < len(empty) and empty[leading]:
        leading += 1
    assert leading == 500, leading
    assert sum(empty) == 500, sum(empty)


# -- item 11: validate excuses only a date column the twin's report names as drawn ----------------------------


def _outcome(column: str) -> validation.Outcome:
    # A day-of-month count: still excused under the owner's ruling of 2026-11-22 (a weekday count no longer is).
    checks = (validation.Check(column, "datetime.day_of_month_census", "day_of_month_census.groups", validation.MISSED),
              validation.Check("age", "numeric.mean", "mean", validation.HELD))
    census = validation.Census(held=1, within_bound=0, authorized_deviation=0, withheld=0, missed=1, not_checkable=0)
    return validation.Outcome(checks=checks, listings=(), census=census, measured_name="visits-twin.csv")


def test_item_11_a_date_column_the_dates_zone_did_not_write_is_not_excused(tmp_path: pathlib.Path) -> None:
    places = _places(tmp_path)
    description = pathlib.Path(tmp_path, "out", "visits-profile.json")
    description.parent.mkdir(parents=True)
    description.write_text("{}\n", encoding="utf-8", newline="\n")
    measured = pathlib.Path(tmp_path, "out", "visits-twin.csv")
    measured.write_text("age,visit_day\n", encoding="utf-8", newline="\n")
    report = pathlib.Path(tmp_path, "out", "visits-twin-report.txt")
    record = {"format": inside.FORMAT, "version": inside.VERSION, "mode": inside.MODE, "table": {},
              "zones": {"dates": {"version": 2, "order": ["visit_day"]}}}
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inside, "default_places", lambda: places)
        inside.write_record(record, cli._inside_record_at(f"{description}", places.private), places)
        # The writer refused the version-2 zone: the head names the drawn number alone.
        report.write_text(cli._inside_report_head(["age"]) + "The rest of the report.\n", encoding="utf-8", newline="\n")
        kept = cli._outcome_of_a_drawn_twin(f"{description}", f"{measured}", _outcome("visit_day"))
        assert [check.verdict for check in kept.checks] == [validation.MISSED, validation.HELD]
        assert kept.census.missed == 1
        # A column the head names as drawn is excused (the case sees the relabel when it is due).
        report.write_text(cli._inside_report_head(["age", "visit_day"]) + "The rest.\n", encoding="utf-8", newline="\n")
        moved = cli._outcome_of_a_drawn_twin(f"{description}", f"{measured}", _outcome("visit_day"))
        assert [check.verdict for check in moved.checks] == [validation.AUTHORIZED_DEVIATION, validation.HELD]
        assert moved.census.missed == 0 and moved.census.authorized_deviation == 1


def test_item_11_a_head_whose_list_is_in_doubt_excuses_nothing() -> None:
    head = cli._inside_report_head(["a, b", "visit_day"])
    assert cli._drawn_in_report(head) == set()
    assert cli._drawn_in_report(cli._inside_report_head(["a", "visit_day"])) == {"a", "visit_day"}
    assert cli._drawn_in_report("THIS TWIN WAS DRAWN FROM THE INSIDE RECORD\n") == set()


# -- item 14: the scale harness admits only the inside route ---------------------------------------------------


def _line(step: str, rows: int, **fields: object) -> str:
    line: "dict[str, object]" = {"step": step, "exit": 0, "shape": "dense", "rows": rows, "columns": 12,
                                 "seconds": rows / 1000.0, "cpu_seconds": rows / 1000.0, "peak_rss_mb": 100.0,
                                 "inside_seconds": {}, "inside_traced_mb": {}}
    line.update(fields)
    return "RESULT " + json.dumps(line, sort_keys=True)


def test_item_14_the_scale_harness_projects_no_run_without_a_record(tmp_path: pathlib.Path) -> None:
    results = pathlib.Path(tmp_path, "results.txt")
    lines = [_line("profile", rows, records=0, record_bytes=0) for rows in (20000, 40000)]
    lines += [_line("generate", rows, drawn_columns=0) for rows in (20000, 40000)]
    lines += [_line("profile", rows, records=1, record_bytes=5000, shape="wide302") for rows in (20000, 40000)]
    results.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    done = subprocess.run([sys.executable, f"{pathlib.Path(REPO_ROOT, 'tools', 'measurements', 'kpi_inside_scale.py')}",
                           "project", f"{results}"], capture_output=True, text=True, check=False,
                          env=dict(os.environ), cwd=f"{tmp_path}")
    assert done.returncode == 0, done.stderr[-2000:]
    projected = [json.loads(line[len("PROJECTED "):]) for line in done.stdout.splitlines()
                 if line.startswith("PROJECTED ")]
    assert [(each["shape"], each["step"]) for each in projected] == [("wide302", "profile")], projected
    assert any(line.startswith("REFUSED 4 ") for line in done.stdout.splitlines()), done.stdout[-2000:]

