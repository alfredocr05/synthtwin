"""Gate file of lane IN-4 (plan P4-D499): the keyed zone of the inside record and the twin it shapes.

THE ZONE. A long table whose rows are typed by a key (an item, a test)
is read into a model of each key level: the joint table of the row's
label cells, each number's marginal (by the label that sets its scale),
a pair's two parts and their correlation, a flag that is a function of
intervals of a number, a copy with its sentinel, and the level's
trajectory (a trend over the person's time, a person's share, a lag).
The twin's rows take them in two steps (`persons_and_labels`, then
`numbers_and_rules` on the time axis), and `generate_inside` runs both
around the dates zone.

WHAT IT HOLDS, each clause red on its mutant (named in the case):

* The zone is a model: no person's key, no value of a level kept as
  possible record numbers, and its size does not follow the rows.
* The key is the column the others follow; a table of no key has none.
* Every rule inside a row comes back on the twin: a unit by its level, a
  scale set apart by its unit, a label set by another label of the row,
  a flag by the intervals of its number, a copy and its sentinel, a
  pair's correlation, a later clock's gap and presence by level.
* Each level's trajectory comes back: a person's share, a trend over the
  person's time, the lag of successive readings.
* What the zone must not carry it does not: a level of possible record
  numbers whose values do not repeat, a level of dates; a level the
  description top-codes at 90 is written so.
* The same zone and seed give the same cells; another seed other cells.
* Through the commands at the table floor (lane RU-a's route S on the
  battery's charting table), the keyed zone's own sub-switch set on in
  place (`cli._KEYED_ZONE_SHIPPED`, off on the shipped route since batch
  4x, plan P4-D503): the record holds the zone, the twin's unit
  and device follow the item, its pressure pairs correlate, and IN-1's
  checks of row copies (C1), patient copies (C3), rare combinations (C5)
  and identifiers (C4's first clause) pass. C2 and C4's date clause read
  how near the twin's minute stamps lie to real ones, which the dates
  zone writes; they are not this file's.
"""

from __future__ import annotations

import csv
import datetime
import io
import json
import math
import pathlib
import random

import pytest

import reliability_battery as B
import reliability_tables as T
from synthtwin import cli, inside, inside_keyed, installation, twin_checks

ROWS = 6000
FLOOR_ROWS = 20000
SENTINEL = "-1"
# An invented long table: each item's reading, unit, printed range, flag, numeric copy and source.
ITEMS = ("PULSE", "PRESS", "TEMP", "SALT", "MOOD", "TROP", "GLUC", "CODE", "SEEN")
ITEM_WEIGHTS = (0.22, 0.16, 0.12, 0.12, 0.08, 0.08, 0.16, 0.03, 0.03)
EPOCH = datetime.datetime(2023, 1, 1)
COLUMNS = ["subject", "item", "taken_at", "reading", "unit", "range", "flag", "reading_num", "source", "seen_at",
           "ward", "shift"]


def _stamp(minutes: int) -> str:
    return (EPOCH + datetime.timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M")


def long_table(rows: int, seed: int) -> "dict[str, list[str]]":
    """The invented long table, column by column (every value drawn here; the codes made up row by row)."""
    r = random.Random(f"keyed-{seed}")
    other = random.Random(f"keyed-other-{seed}")
    out: "dict[str, list[str]]" = {name: [] for name in COLUMNS}
    written = 0
    person = 0
    while written < rows:
        person += 1
        count = min(rows - written, r.randint(2, 40))
        pulse_level = r.gauss(0.0, 10.0)
        press_level = r.gauss(0.0, 15.0)
        gluc_level = r.gauss(0.0, 1.0)
        fahrenheit = r.random() < 0.3
        start = r.randrange(400 * 1440)
        span = r.uniform(12.0, 96.0)
        offsets = sorted(r.uniform(0.0, span) for _ in range(count))
        noise = r.gauss(0.0, 1.0)
        ward = other.choice(("north", "south", "east", "west"))
        for hours in offsets:
            item = r.choices(ITEMS, ITEM_WEIGHTS)[0]
            unit, printed, source, reading = "", "", "hand", ""
            if item == "PULSE":
                reading = str(int(round(80.0 + pulse_level - 0.1 * hours + r.gauss(0.0, 8.0))))
                unit, printed, source = "bpm", "60-100", "auto"
            elif item == "PRESS":
                upper = int(round(120.0 + press_level + r.gauss(0.0, 10.0)))
                reading = f"{upper}/{int(round(10.0 + 0.55 * upper + r.gauss(0.0, 6.0)))}"
                unit, source = "mmHg", ("auto" if r.random() < 0.5 else "hand")
            elif item == "TEMP":
                celsius = r.gauss(37.0, 0.4)
                reading = f"{celsius * 1.8 + 32.0:.1f}" if fahrenheit else f"{celsius:.1f}"
                unit, source = ("F", "probe") if fahrenheit else ("C", "hand")
            elif item == "SALT":
                reading = str(int(round(r.gauss(139.0, 3.0))))
                unit, printed = "mmol/L", "135-145"
            elif item == "MOOD":
                reading = r.choices(("calm", "restless", "asleep"), (0.7, 0.2, 0.1))[0]
            elif item == "TROP":
                value = math.exp(r.gauss(-4.6, 1.0))
                reading = "<0.01" if value < 0.01 else f"{value:.3f}"[1:]
                unit = "ng/mL"
            elif item == "GLUC":
                noise = 0.6 * noise + 0.8 * r.gauss(0.0, 1.0)
                reading = f"{6.0 + gluc_level + noise:.1f}"
                unit = "mmol/L"
            elif item == "CODE":
                reading = str(r.randrange(1_000_000, 10_000_000))
            else:
                reading = _stamp(start + r.randrange(-400 * 1440, 0))[:10]
            flag = ""
            if printed and reading.lstrip("-").isdigit():
                low, high = (float(part) for part in printed.split("-"))
                flag = "" if low <= float(reading) <= high else "1"
            number = reading if _plain(reading) else SENTINEL
            moment = _stamp(start + int(hours * 60.0))
            lag = 0 if source == "auto" else 1 + int(r.expovariate(1.0 / 12.0))
            seen = "" if source == "probe" else _stamp(start + int(hours * 60.0) + lag)
            shift = "day" if other.random() < 0.6 else "night"
            for name, cell in zip(COLUMNS, (f"S{1000000 + person}", item, moment, reading, unit, printed, flag,
                                            number, source, seen, ward, shift)):
                out[name] += [cell]
            written += 1
    return out


def _plain(cell: str) -> bool:
    return inside_keyed.plain_number(cell) is not None


DATED = ("taken_at", "seen_at")
HELD = {"reading": {"salt": {"identifier": True, "top": 0}, "code": {"identifier": True, "top": 0}}}


def _zone(rows: int = ROWS, seed: int = 1, held: "dict | None" = None) -> "dict[str, object]":
    table = long_table(rows, seed)
    zone = inside_keyed.build_zone(table, "subject", (), DATED, {}, HELD if held is None else held)
    assert zone is not None
    return zone


def _twin(zone: "dict[str, object]", table: "dict[str, list[str]]", seed: int = 0) -> "dict[str, list[str]]":
    """A stand-in twin: the table's rows with made-up persons in another order and every content cell blank, then both steps."""
    cells = {name: list(cells) for name, cells in table.items()}
    r = random.Random(5)
    shuffled = list(cells["subject"])
    r.shuffle(shuffled)
    cells["subject"] = ["T" + cell[1:] for cell in shuffled]
    for name in ("reading", "unit", "range", "flag", "reading_num", "source", "seen_at"):
        cells[name] = ["?" for _cell in cells[name]]
    cells.update(inside_keyed.persons_and_labels(zone, cells, seed))
    _timelines(cells)
    cells.update(inside_keyed.numbers_and_rules(zone, cells, seed))
    return cells


def _timelines(cells: "dict[str, list[str]]") -> None:
    """Each twin person's rows timed as one stay (the dates zone's part in the product), in the rows' order."""
    r = random.Random(11)
    by: "dict[str, list[int]]" = {}
    for row in range(len(cells["subject"])):
        by.setdefault(cells["subject"][row], []).append(row)
    for person in sorted(by):
        start = r.randrange(400 * 1440)
        span = r.uniform(12.0, 96.0)
        offsets = sorted(r.uniform(0.0, span) for _ in by[person])
        for row, hours in zip(by[person], offsets):
            cells["taken_at"][row] = _stamp(start + int(hours * 60.0))


@pytest.fixture(scope="module")
def made() -> "tuple[dict[str, list[str]], dict[str, object], dict[str, list[str]]]":
    table = long_table(ROWS, 1)
    zone = inside_keyed.build_zone(table, "subject", (), DATED, {}, HELD)
    assert zone is not None
    return table, zone, _twin(zone, table)


def _rows_of(cells: "dict[str, list[str]]", item: str) -> "list[int]":
    return [row for row in range(len(cells["item"])) if cells["item"][row] == item]


def _hours(cells: "dict[str, list[str]]") -> "list[float]":
    first: "dict[str, float]" = {}
    moments: "list[float]" = []
    for row in range(len(cells["subject"])):
        moment = (datetime.datetime.strptime(cells["taken_at"][row], "%Y-%m-%d %H:%M") - EPOCH).total_seconds() / 3600.0
        moments += [moment]
        person = cells["subject"][row]
        first[person] = min(first[person], moment) if person in first else moment
    return [moments[row] - first[cells["subject"][row]] for row in range(len(moments))]


def _share_between(values: "list[float]", groups: "list[str]") -> float:
    """The one-way intraclass correlation of values by group (unbalanced moments)."""
    by: "dict[str, list[float]]" = {}
    for value, group in zip(values, groups):
        by.setdefault(group, []).append(value)
    count, sets = len(values), len(by)
    grand = sum(values) / count
    within = sum((v - sum(g) / len(g)) ** 2 for g in by.values() for v in g)
    between = sum(len(g) * (sum(g) / len(g) - grand) ** 2 for g in by.values())
    msw, msb = within / (count - sets), between / (sets - 1)
    n0 = (count - sum(len(g) ** 2 for g in by.values()) / count) / (sets - 1)
    person = max(0.0, (msb - msw) / n0)
    return person / (person + msw)


def _corr(first: "list[float]", second: "list[float]") -> float:
    mean_a, mean_b = sum(first) / len(first), sum(second) / len(second)
    sab = sum((a - mean_a) * (b - mean_b) for a, b in zip(first, second))
    saa = sum((a - mean_a) ** 2 for a in first)
    sbb = sum((b - mean_b) ** 2 for b in second)
    return sab / math.sqrt(saa * sbb)


def test_the_zone_is_a_model_with_no_person_and_no_record_number(made) -> None:  # type: ignore[no-untyped-def]
    """No person's key and no value of a level kept as possible record numbers (mutant: the zone keeps the persons' keys)."""
    table, zone, _twin_cells = made
    text = json.dumps(zone)
    for person in set(table["subject"]):
        assert person not in text
    codes = [table["reading"][row] for row in _rows_of(table, "CODE")]
    assert codes and not any(f'"{code}"' in text for code in codes)
    assert zone["key"] == "item" and zone["person"] == "subject"


def test_the_zone_size_follows_levels_not_rows() -> None:
    """Doubling the rows at the table floor moves the zone by under 5 per cent (mutant: every written number kept as a value table)."""
    small = len(json.dumps(_zone(FLOOR_ROWS)))
    large = len(json.dumps(_zone(2 * FLOOR_ROWS)))
    assert abs(large - small) / small < 0.05, (small, large)


def test_the_key_is_the_column_the_others_follow() -> None:
    """The item is the key; a table where no label types the others has none (mutant: the first label is the key)."""
    table = long_table(ROWS, 2)
    owners, _persons = inside_keyed._persons(table["subject"])
    content = ["source", "item", "reading", "unit", "range", "flag", "reading_num"]
    assert inside_keyed.key_of(table, content, owners) == "item"
    r = random.Random(3)
    plain = {"subject": table["subject"], "arm": [r.choice("AB") for _ in table["subject"]],
             "site": [r.choice(("north", "south", "east")) for _ in table["subject"]],
             "score": [str(r.randint(1, 50)) for _ in table["subject"]]}
    assert inside_keyed.build_zone(plain, "subject", (), (), {}, {}) is None


def test_units_follow_their_level_and_scales_stay_apart(made) -> None:  # type: ignore[no-untyped-def]
    """Every row's unit is its level's; Fahrenheit rows read as Fahrenheit (mutant: no label sets a number's scale)."""
    _table, _zone_built, twin = made
    expected = {"PULSE": "bpm", "PRESS": "mmHg", "SALT": "mmol/L", "TROP": "ng/mL", "GLUC": "mmol/L", "MOOD": ""}
    for item, unit in expected.items():
        rows = _rows_of(twin, item)
        assert rows and all(twin["unit"][row] == unit for row in rows), item
    temp = _rows_of(twin, "TEMP")
    for row in temp:
        value = float(twin["reading"][row])
        assert (value > 80.0) if twin["unit"][row] == "F" else (value < 45.0), (twin["unit"][row], value)


def test_a_label_set_by_another_label_of_its_row(made) -> None:  # type: ignore[no-untyped-def]
    """At one level the source follows the unit (a probe for Fahrenheit) (mutant: each label drawn apart from the others)."""
    _table, _zone_built, twin = made
    for row in _rows_of(twin, "TEMP"):
        assert twin["source"][row] == ("probe" if twin["unit"][row] == "F" else "hand")


def test_a_flag_follows_the_intervals_of_its_number(made) -> None:  # type: ignore[no-untyped-def]
    """The flag is set exactly where the reading lies outside its printed range (mutant: the interval rules not applied)."""
    _table, _zone_built, twin = made
    checked = 0
    for item in ("PULSE", "SALT"):
        for row in _rows_of(twin, item):
            low, high = (float(part) for part in twin["range"][row].split("-"))
            outside = not low <= float(twin["reading"][row]) <= high
            assert twin["flag"][row] == ("1" if outside else ""), (item, twin["reading"][row], twin["flag"][row])
            checked += 1
    assert checked > 1000


def test_a_copy_and_its_sentinel(made) -> None:  # type: ignore[no-untyped-def]
    """The numeric copy equals the reading where it is a number and the sentinel elsewhere (mutant: copies not applied)."""
    _table, zone, twin = made
    assert zone["copies"] == [{"column": "reading_num", "from": "reading", "else": SENTINEL}]
    modelled = [row for row in range(len(twin["item"])) if twin["item"][row] not in ("CODE", "SEEN")]
    for row in modelled:
        reading = twin["reading"][row]
        assert twin["reading_num"][row] == (reading if _plain(reading) else SENTINEL)


def test_a_pair_keeps_its_correlation(made) -> None:  # type: ignore[no-untyped-def]
    """The two parts of `a/b` correlate as on the table, within 0.08 (mutant: the parts drawn apart)."""
    table, _zone_built, twin = made

    def parts(cells: "dict[str, list[str]]") -> "tuple[list[float], list[float]]":
        rows = _rows_of(cells, "PRESS")
        return ([float(cells["reading"][row].split("/")[0]) for row in rows],
                [float(cells["reading"][row].split("/")[1]) for row in rows])

    real = _corr(*parts(table))
    drawn = _corr(*parts(twin))
    assert real > 0.7 and abs(drawn - real) < 0.08, (real, drawn)


def test_a_person_share_and_a_trend_over_the_person_time(made) -> None:  # type: ignore[no-untyped-def]
    """The pulse's person share within 0.12 and its trend per hour of the right sign and size (mutants: no person level; no trend)."""
    table, _zone_built, twin = made
    for cells in (table, twin):
        rows = _rows_of(cells, "PULSE")
        values = [float(cells["reading"][row]) for row in rows]
        cells["_icc"] = [str(_share_between(values, [cells["subject"][row] for row in rows]))]
    assert abs(float(twin["_icc"][0]) - float(table["_icc"][0])) < 0.12, (table["_icc"], twin["_icc"])
    slopes = []
    for cells in (table, twin):
        hours = _hours(cells)
        rows = _rows_of(cells, "PULSE")
        by: "dict[str, list[tuple[float, float]]]" = {}
        for row in rows:
            by.setdefault(cells["subject"][row], []).append((hours[row], float(cells["reading"][row])))
        sxy = sxx = 0.0
        for series in by.values():
            if len(series) < 2:
                continue
            mt = sum(t for t, _v in series) / len(series)
            mv = sum(v for _t, v in series) / len(series)
            sxy += sum((t - mt) * (v - mv) for t, v in series)
            sxx += sum((t - mt) ** 2 for t, _v in series)
        slopes += [sxy / sxx]
    assert slopes[0] < -0.05 and slopes[1] < 0.0 and abs(slopes[1] - slopes[0]) < 0.6 * abs(slopes[0]), slopes


def test_the_lag_of_successive_readings(made) -> None:  # type: ignore[no-untyped-def]
    """Successive readings of one person keep their lag-one correlation within 0.15 (mutant: the lag set to nought)."""
    table, zone, twin = made
    levels = {entry["level"]: entry for entry in zone["levels"]}
    assert levels["GLUC"]["numbers"]["reading"]["model"]["lag"] > 0.2
    lags = []
    for cells in (table, twin):
        hours = _hours(cells)
        by: "dict[str, list[tuple[float, float]]]" = {}
        for row in _rows_of(cells, "GLUC"):
            by.setdefault(cells["subject"][row], []).append((hours[row], float(cells["reading"][row])))
        top = bottom = 0.0
        for series in by.values():
            if len(series) < 3:
                continue
            values = [v for _t, v in sorted(series)]
            mean = sum(values) / len(values)
            deviations = [v - mean for v in values]
            top += sum(deviations[k] * deviations[k + 1] for k in range(len(deviations) - 1))
            bottom += sum(d * d for d in deviations)
        lags += [top / bottom]
    assert abs(lags[1] - lags[0]) < 0.15, lags


def test_a_later_clock_keeps_its_gap_and_presence_by_level(made) -> None:  # type: ignore[no-untyped-def]
    """A clock seen at once on the device's rows (a level, or a label inside a level) and later on the others, and none where the row's label says so (mutant: the later clocks not written)."""
    _table, zone, twin = made
    assert [pair[0] for pair in zone["gaps"]] == ["seen_at"]
    late = 0
    for row in range(len(twin["item"])):
        if twin["item"][row] in ("CODE", "SEEN"):
            continue
        if twin["source"][row] == "probe":
            assert twin["seen_at"][row] == "", twin["seen_at"][row]
            continue
        start = datetime.datetime.strptime(twin["taken_at"][row], "%Y-%m-%d %H:%M")
        gap = (datetime.datetime.strptime(twin["seen_at"][row], "%Y-%m-%d %H:%M") - start).total_seconds() / 60.0
        if twin["source"][row] == "auto":
            assert gap == 0.0, (twin["item"][row], gap)
        else:
            assert gap >= 1.0, (twin["item"][row], gap)
            late += 1
    assert late > 1000


def test_columns_the_key_leaves_alone(made) -> None:  # type: ignore[no-untyped-def]
    """A column the key does not move keeps the twin's own cells, and one constant within persons stays so after the persons are re-cut (mutants: every column taken; the constancy not restored)."""
    _table, zone, twin = made
    assert zone["constant"] == ["ward"] and "shift" not in zone["content"] and "ward" not in zone["content"]
    assert all(cell == "night" or cell == "day" for cell in twin["shift"])
    held: "dict[str, set[str]]" = {}
    for row in range(len(twin["subject"])):
        held.setdefault(twin["subject"][row], set()).add(twin["ward"][row])
    assert len(held) > 100 and all(len(wards) == 1 for wards in held.values())


def test_record_numbers_and_dates_are_not_carried(made) -> None:  # type: ignore[no-untyped-def]
    """A level of possible record numbers that do not repeat and a level of dates keep the twin's own cells, while a held level of repeating numbers is drawn (mutants: every held level drawn; no level read as dates)."""
    _table, zone, twin = made
    levels = {entry["level"]: entry for entry in zone["levels"]}
    assert levels["CODE"]["kept"] == inside_keyed.KEPT_IDENTIFIER
    assert levels["SEEN"]["kept"] == inside_keyed.KEPT_DATES
    assert levels["SALT"]["kept"] == ""
    for item in ("CODE", "SEEN"):
        assert all(twin["reading"][row] == "?" for row in _rows_of(twin, item)), item


def test_columns_the_description_keeps_for_privacy_are_never_drawn() -> None:
    """Identifiers, free text, a withheld count, a year top code and a computed column are kept out of the zone, an age's 90 is not (mutant: only identifiers kept)."""
    document = {"columns": [
        {"name": "a", "role": "categorical"}, {"name": "b", "role": "free_text"},
        {"name": "c", "role": "categorical", "present_count_withheld": True},
        {"name": "d", "role": "count", "top_coded_year": 2000}, {"name": "e", "role": "identifier"},
        {"name": "f", "role": "continuous", "top_coded": 90}, {"name": "g", "role": "count", "computed_from": ["a"]},
    ]}
    assert inside_keyed.kept_by_description(document) == ("b", "c", "d", "e", "g")
    table = long_table(ROWS, 1)
    zone = inside_keyed.build_zone(table, "subject", ("unit",), DATED, {}, HELD)
    assert zone is not None and "unit" not in zone["content"]


def test_a_level_top_coded_at_90_is_written_so() -> None:
    """The description's 90 on a level holds on every twin cell of it (mutant: the top code not applied)."""
    table = long_table(ROWS, 1)
    held = {"reading": {"pulse": {"identifier": False, "top": 90}}}
    zone = inside_keyed.build_zone(table, "subject", (), DATED, {}, held)
    assert zone is not None
    twin = _twin(zone, table)
    values = [float(twin["reading"][row]) for row in _rows_of(twin, "PULSE")]
    assert max(values) == 90.0 and sum(1 for value in values if value > 90.0) == 0


def test_the_same_seed_gives_the_same_cells(made) -> None:  # type: ignore[no-untyped-def]
    """A fixed function of the zone and the seed (mutant: the streams ignore the seed)."""
    table, zone, twin = made
    again = _twin(zone, table, 0)
    other = _twin(zone, table, 1)
    assert again["reading"] == twin["reading"] and again["subject"] == twin["subject"]
    assert other["reading"] != twin["reading"]


def _places(folder: pathlib.Path) -> inside.Places:
    return inside.Places(pathlib.Path(folder, "installation", "synthtwin", "inside"), (), (),
                         installation.system_name(), ())


def test_the_commands_write_the_zone_and_the_twin_follows_it(tmp_path: pathlib.Path) -> None:
    """Route S on the charting table at the table floor: the record holds the zone, the twin's unit and device follow the item, its pressure pairs correlate, IN-1's copy, combination and identifier checks pass (mutant: generate reads no keyed zone)."""
    folder = tmp_path / "product"
    text = T.text("T3", FLOOR_ROWS, 1)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inside, "default_places", lambda: _places(folder))
        # The keyed zone's own sub-switch, off on the shipped route since batch 4x (plan P4-D503), on for this case.
        patch.setattr(cli, "_KEYED_ZONE_SHIPPED", True)
        product = B.make_twins(folder, "T3", text, (0,), False)
    assert not product.errors, product.errors
    private = _places(folder).private
    records = sorted(private.glob(f"*{inside.SUFFIX}"))
    assert len(records) == 1
    record = json.loads(records[0].read_text(encoding="utf-8").split("\n", 1)[1])
    assert record["zones"]["keyed"]["key"] == "item"
    real = list(csv.DictReader(io.StringIO(text)))
    twin = list(csv.DictReader(io.StringIO(product.twins[0])))
    units: "dict[str, set[str]]" = {}
    devices: "dict[str, set[str]]" = {}
    for row in real:
        units.setdefault(row["item"], set()).add(row["unit"])
        devices.setdefault(row["item"], set()).add(row["device"])
    assert all(row["unit"] in units[row["item"]] and row["device"] in devices[row["item"]] for row in twin)
    pressure = [row["value"].split("/") for row in twin if row["item"] == "BP"]
    assert _corr([float(a) for a, _b in pressure], [float(b) for _a, b in pressure]) > 0.6
    real_path, twin_path = tmp_path / "real.csv", tmp_path / "twin.csv"
    real_path.write_text(text, encoding="utf-8", newline="\n")
    twin_path.write_text(product.twins[0], encoding="utf-8", newline="\n")
    outcome = twin_checks.run_checks(str(real_path), str(twin_path), person=T.PERSON["T3"])
    by_code = {check.code: check for check in outcome.checks}
    for code in ("C1", "C3", "C5"):
        assert by_code[code].passed, twin_checks.report_lines(outcome)
    assert any("0 twin cells equal a real one" in line for line in by_code["C4"].lines), by_code["C4"].lines
