"""Gate file of lanes IN-4 and IN-4b (plans P4-D499, P4-D504): the keyed zone of the inside record and the twin it shapes.

THE ZONE. A long table whose rows are typed by a key (an item, a test)
is read into a model of each key level: the joint table of the row's
label cells, each number's marginal (by the label that sets its scale),
a pair's two parts and their correlation, a flag that is a function of
intervals of a number, a copy with its sentinel, and the level's
trajectory (a trend over the person's time, a person's share, a lag).

THE TWIN (lane IN-4b, after batch 4x's outside review): the zone writes no
person and no spelling of its own choosing. Every column it deals keeps
the description's twin's own cells -- a column the description publishes
key by key on each key level's rows, any other over the rows it types --
and the zone decides only which row holds which, in two steps
(`persons_and_labels`, then `numbers_and_rules` on the time axis).

WHAT IT HOLDS, each clause red on its mutant (named in the case; the
lane's report lists each run):

* The zone is a model: no person's key, no value of a block the
  description holds as identifiers, and its size does not follow the rows.
* The key is the column the others follow; a table of no key has none.
* Every rule inside a row comes back on the twin, from the twin's own
  cells: a unit by its level, a scale set apart by its unit (a cell the
  deal leaves on the other scale written at its row's place in its own
  form, never past a top code), a label set by another label of the row,
  a flag by the intervals of its number, a copy and its sentinel (never
  beside a source a level top-codes, lane IN-4c), a pair's parts the
  twin's own spellings joined again at the record's correlation (lane
  IN-4c).
* Each level's trajectory comes back: a person's share, a trend over the
  person's time, the lag of successive readings.
* Every column the zone deals keeps the stand-in description twin's cells
  (a column published key by key on each level's rows), moved with its key
  where the key was dealt anew.
* ITEM 1: a block the description holds as identifiers is never modelled,
  whatever its values repeat across persons; its cells stay the twin's.
* ITEM 2: no cell past a top code and no censoring mark past it on any
  keyed path.
* ITEM 5: the persons are never re-cut: the person column, a person's
  allocation and a visit sequence stand.
* ITEM 6: a later clock keeps the dates zone's presence, written form and
  month on every row.
* Through the commands at the table floor, the keyed zone's own switch set
  on in place (`cli._KEYED_ZONE_SHIPPED`): the battery's charting and
  laboratory tables validate with exit 0 and pass the five checks, their
  dealt columns are the keyed-off twin's cells; the pressure and sodium
  blocks, put their own question (lane IN-4c), are modelled once answered
  `measurement` and held, the twin's made-up cells kept, while the
  pressure's is left open; the review table of items
  1, 2, 5 and 6 writes no real name, no age past 90, keeps its persons,
  allocations, sequences and its later clock's presence and months.
"""

from __future__ import annotations

import contextlib
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
from synthtwin import asking, cli, inside, inside_keyed, installation, twin_checks

ROWS = 6000
FLOOR_ROWS = 20000
SENTINEL = "-1"
# An invented long table: each item's reading, unit, printed range, flag, numeric copy and source.
ITEMS = ("PULSE", "PRESS", "TEMP", "SALT", "MOOD", "TROP", "GLUC", "CODE", "SEEN")
ITEM_WEIGHTS = (0.22, 0.16, 0.12, 0.12, 0.08, 0.08, 0.16, 0.03, 0.03)
EPOCH = datetime.datetime(2023, 1, 1)
COLUMNS = ["subject", "item", "taken_at", "reading", "unit", "range", "flag", "reading_num", "source", "seen_at",
           "ward", "shift"]
DEALT = ("reading", "unit", "range", "flag", "source")


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


def _form(cell: str) -> str:
    """A cell's written form: a plain number's sign, whether figures stand before its point, and its decimals; a pair's
    two parts' forms (lane IN-4c: a released block's pairs are joined again, each part a spelling of the twin's own);
    any other cell itself."""
    text = cell.strip()
    found = inside_keyed.pair_of(text)
    if found is not None:
        return f"{_form(found[0])}/{_form(found[1])}"
    if inside_keyed.plain_number(text) is None:
        return text
    sign = text[:1] if text[:1] in "+-" else ""
    body = text[len(sign):]
    return f"{sign}{'#' if body.split('.')[0] else ''}.{inside_keyed.decimals_of(body)}"


DATED = ("taken_at", "seen_at")
HELD = {"reading": {"code": {"identifier": True, "top": 0}}}
TYPED = {"reading": "item"}


def _zone(rows: int = ROWS, seed: int = 1, held: "dict | None" = None) -> "dict[str, object]":
    table = long_table(rows, seed)
    zone = inside_keyed.build_zone(table, "subject", (), DATED, {}, HELD if held is None else held, TYPED)
    assert zone is not None
    return zone


def _later(stamp: str, minutes: int) -> str:
    return (datetime.datetime.strptime(stamp, "%Y-%m-%d %H:%M") + datetime.timedelta(minutes=minutes)).strftime(
        "%Y-%m-%d %H:%M")


def _stand_in(table: "dict[str, list[str]]") -> "dict[str, list[str]]":
    """A stand-in for the description's twin, as the zone receives it: the persons renamed in place; the keyed reading
    permuted within each item (the CODE level's made up, as a held block's are); every other content column permuted
    over the rows, apart from the item; each person's rows timed as one stay and the later clock a few minutes after
    them where it is written (the dates zone's part)."""
    r = random.Random(5)
    cells = {name: list(values) for name, values in table.items()}
    cells["subject"] = ["T" + cell[1:] for cell in table["subject"]]
    by: "dict[str, list[int]]" = {}
    for row, item in enumerate(table["item"]):
        by.setdefault(item, []).append(row)
    for item, rows in by.items():
        values = [table["reading"][row] for row in rows]
        r.shuffle(values)
        for row, value in zip(rows, values):
            cells["reading"][row] = f"Z{1000000 + row}" if item == "CODE" else value
    for name in ("unit", "range", "flag", "reading_num", "source", "seen_at"):
        r.shuffle(cells[name])
    _timelines(cells)
    for row in range(len(cells["subject"])):
        if cells["seen_at"][row]:
            cells["seen_at"][row] = _later(cells["taken_at"][row], r.randrange(0, 40))
    return cells


def _twin(zone: "dict[str, object]", stand: "dict[str, list[str]]", seed: int = 0,
          original: "list[str] | None" = None) -> "dict[str, list[str]]":
    """Both steps on a copy of the stand-in twin."""
    cells = {name: list(values) for name, values in stand.items()}
    cells.update(inside_keyed.persons_and_labels(zone, cells, seed, original))
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
def made() -> "tuple[dict[str, list[str]], dict[str, object], dict[str, list[str]], dict[str, list[str]]]":
    table = long_table(ROWS, 1)
    zone = inside_keyed.build_zone(table, "subject", (), DATED, {}, HELD, TYPED)
    assert zone is not None
    stand = _stand_in(table)
    return table, zone, stand, _twin(zone, stand)


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


# -- the zone -----------------------------------------------------------------------------------------------


def test_the_zone_is_a_model_with_no_person_and_no_held_value(made) -> None:  # type: ignore[no-untyped-def]
    """No person's key and no value of a block the description holds as identifiers (mutants: the zone keeps the persons' keys; the held block modelled)."""
    table, zone, _stand, _twin_cells = made
    text = json.dumps(zone)
    for person in set(table["subject"]):
        assert person not in text
    codes = [table["reading"][row] for row in _rows_of(table, "CODE")]
    assert codes and not any(f'"{code}"' in text for code in codes)
    assert zone["key"] == "item" and zone["person"] == "subject" and zone["scoped"] == ["reading"]
    assert "census" not in zone and zone["version"] == inside_keyed.ZONE_VERSION


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


# -- the rules inside a row, from the twin's own cells ---------------------------------------------------------


def test_units_follow_their_level_and_scales_stay_apart(made) -> None:  # type: ignore[no-untyped-def]
    """Every row's unit is its level's; Fahrenheit rows read as Fahrenheit (mutant: no label sets a number's scale)."""
    _table, _zone_built, _stand, twin = made
    expected = {"PULSE": "bpm", "PRESS": "mmHg", "SALT": "mmol/L", "TROP": "ng/mL", "GLUC": "mmol/L", "MOOD": ""}
    for item, unit in expected.items():
        rows = _rows_of(twin, item)
        assert rows and all(twin["unit"][row] == unit for row in rows), item
    temp = _rows_of(twin, "TEMP")
    for row in temp:
        value = float(twin["reading"][row])
        assert (value > 80.0) if twin["unit"][row] == "F" else (value < 45.0), (twin["unit"][row], value)


def test_a_label_set_by_another_label_of_its_row(made) -> None:  # type: ignore[no-untyped-def]
    """At one level the source follows the unit (a probe for Fahrenheit) (mutant: each label wanted apart from the others)."""
    _table, _zone_built, _stand, twin = made
    for row in _rows_of(twin, "TEMP"):
        assert twin["source"][row] == ("probe" if twin["unit"][row] == "F" else "hand")


def test_a_flag_follows_the_intervals_of_its_number(made) -> None:  # type: ignore[no-untyped-def]
    """The flag is set exactly where the reading lies outside its printed range (mutant: the interval rules not applied)."""
    _table, _zone_built, _stand, twin = made
    checked = 0
    for item in ("PULSE", "SALT"):
        for row in _rows_of(twin, item):
            low, high = (float(part) for part in twin["range"][row].split("-"))
            outside = not low <= float(twin["reading"][row]) <= high
            assert twin["flag"][row] == ("1" if outside else ""), (item, twin["reading"][row], twin["flag"][row])
            checked += 1
    assert checked > 1000


def test_a_copy_and_its_sentinel_and_none_beside_a_held_source() -> None:
    """With no block of its source held, the numeric copy equals the reading where it is a number and the sentinel elsewhere, on every row; beside a held block it is not written (mutants: copies not applied; copies written beside a held block)."""
    table = long_table(ROWS, 1)
    stand = _stand_in(table)
    free = inside_keyed.build_zone(table, "subject", (), DATED, {}, {}, TYPED)
    assert free is not None and free["copies"] == [{"column": "reading_num", "from": "reading", "else": SENTINEL,
                                                    "cap": 0}]
    twin = _twin(free, stand)
    for row in range(len(twin["item"])):
        reading = twin["reading"][row]
        assert twin["reading_num"][row] == (reading if _plain(reading) else SENTINEL)
    held = _twin(_zone(), stand)
    assert held["reading_num"] == stand["reading_num"]


def test_a_pair_is_dealt_whole_and_keeps_its_correlation(made) -> None:  # type: ignore[no-untyped-def]
    """Each pair cell's two parts are spellings of the twin's own (lane IN-4c: joined again at the record's correlation), and the two parts correlate as on the table, within 0.08 (mutant: the parts dealt apart)."""
    table, _zone_built, stand, twin = made

    def parts(cells: "dict[str, list[str]]") -> "tuple[list[float], list[float]]":
        rows = _rows_of(cells, "PRESS")
        return ([float(cells["reading"][row].split("/")[0]) for row in rows],
                [float(cells["reading"][row].split("/")[1]) for row in rows])

    rows = _rows_of(twin, "PRESS")
    for side in (0, 1):
        assert sorted(twin["reading"][row].split("/")[side] for row in rows) == sorted(
            stand["reading"][row].split("/")[side] for row in rows)
    real = _corr(*parts(table))
    drawn = _corr(*parts(twin))
    assert real > 0.7 and abs(drawn - real) < 0.08, (real, drawn)


def test_a_person_share_and_a_trend_over_the_person_time(made) -> None:  # type: ignore[no-untyped-def]
    """The pulse's person share within 0.12 and its trend per hour of the right sign and size (mutants: no person level; no trend)."""
    table, _zone_built, _stand, twin = made
    icc = []
    for cells in (table, twin):
        rows = _rows_of(cells, "PULSE")
        values = [float(cells["reading"][row]) for row in rows]
        icc += [_share_between(values, [cells["subject"][row] for row in rows])]
    assert abs(icc[1] - icc[0]) < 0.12, icc
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
    table, zone, _stand, twin = made
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


# -- the twin's own cells ---------------------------------------------------------------------------------------


def test_every_dealt_column_keeps_the_twins_own_cells(made) -> None:  # type: ignore[no-untyped-def]
    """Each label the zone deals holds the stand-in twin's cells, a spelling the twin writes in another case dealt as itself, and the keyed reading the twin's written forms on each item's rows (mutants: a label written as its joint table asks whatever the cells hold; the keyed reading dealt over every level at once)."""
    table, zone, _stand, _twin_cells = made
    stand = _stand_in(table)
    renamed = 0
    for row in range(len(stand["unit"])):
        if stand["unit"][row] == "mmHg" and renamed < 30:
            stand["unit"][row] = "MMHG"
            renamed += 1
    twin = _twin(zone, stand)
    for name in DEALT:
        if name != "reading":
            assert sorted(twin[name]) == sorted(stand[name]), name
    for item in ITEMS:
        rows = _rows_of(twin, item)
        assert sorted(_form(twin["reading"][row]) for row in rows) == sorted(_form(stand["reading"][row])
                                                                             for row in rows), item
    assert all(twin["unit"][row].lower() == "mmhg" for row in _rows_of(twin, "PRESS"))
    moved = sum(1 for row in range(len(twin["unit"])) if twin["unit"][row] != stand["unit"][row])
    assert moved > len(twin["unit"]) // 2, moved


def test_a_keyed_column_moves_with_its_key_where_the_key_was_dealt_anew() -> None:
    """Where the relations zone dealt the key column anew, step one moves the column published key by key with it, each item's rows holding the cells the stand-in wrote under that item (mutant: no move)."""
    table = long_table(ROWS, 1)
    zone = _zone()
    stand = _stand_in(table)
    original = list(stand["item"])
    moved = list(stand["item"])
    random.Random(17).shuffle(moved)
    stand["item"] = moved
    twin = {name: list(values) for name, values in stand.items()}
    twin.update(inside_keyed.persons_and_labels(zone, twin, 0, original))
    for item in ITEMS:
        before = sorted(stand["reading"][row] for row in range(len(original)) if original[row] == item)
        after = sorted(twin["reading"][row] for row in range(len(moved)) if moved[row] == item)
        assert before == after, item


def test_numbers_take_the_records_values_in_the_twins_forms() -> None:
    """Where the twin's own cells at a level stray from the record (every Celsius reading half a degree high), each row's number is the record's at its place, written in the cell's own form: the Celsius mean comes back to the table's and every reading keeps one decimal (mutant: the twin's cells kept as they are)."""
    table = long_table(ROWS, 1)
    zone = _zone()
    stand = _stand_in(table)
    for row in _rows_of(stand, "TEMP"):
        value = float(stand["reading"][row])
        if value < 45.0:
            stand["reading"][row] = f"{value + 0.5:.1f}"
    twin = _twin(zone, stand)

    def celsius(cells: "dict[str, list[str]]") -> float:
        values = [float(cells["reading"][row]) for row in _rows_of(cells, "TEMP") if cells["unit"][row] == "C"]
        return sum(values) / len(values)

    assert abs(celsius(stand) - celsius(table)) > 0.4
    assert abs(celsius(twin) - celsius(table)) < 0.05, (celsius(twin), celsius(table))
    assert all(inside_keyed.decimals_of(twin["reading"][row]) == 1 for row in _rows_of(twin, "TEMP"))


def test_a_cell_on_the_other_scale_is_written_in_its_own_form_on_its_own() -> None:
    """Where the twin's own cells hold more Fahrenheit readings than its Fahrenheit units, a Celsius row dealt one is written at its place on the Celsius scale in the cell's own form (one decimal), never past a top code (mutants: no rewriting; the top code not applied)."""
    table = long_table(ROWS, 1)
    zone = _zone()
    stand = _stand_in(table)
    temp = _rows_of(stand, "TEMP")
    celsius = [row for row in temp if float(stand["reading"][row]) < 45.0]
    for row in celsius[:25]:
        stand["reading"][row] = "98.6"
    twin = _twin(zone, stand)
    for row in temp:
        value = float(twin["reading"][row])
        assert (value > 80.0) if twin["unit"][row] == "F" else (value < 45.0), (twin["unit"][row], value)
        assert inside_keyed.decimals_of(twin["reading"][row]) == 1, twin["reading"][row]
    assert inside_keyed._in_form("97.1", 120.4, 90) == "90.0"
    assert inside_keyed._in_form("97.1", 37.25, 0) == "37.3"
    assert inside_keyed._in_form(".5", 0.25, 0) == ".3"
    for kept, value in (("007", 5.0), (">95", 120.0), ("-1.5", 2.0), (".5", 2.0)):
        assert inside_keyed._in_form(kept, value, 90) == kept, kept


# -- the batch 4x review's items ------------------------------------------------------------------------------


def test_item1_a_held_block_is_never_modelled_whatever_its_values_repeat() -> None:
    """A block held as identifiers whose values repeat across many persons (a clinician's two names) is not in the zone and its rows keep the twin's cells (mutant: a held block of repeating values modelled)."""
    table = long_table(ROWS, 1)
    names = ("Orla Penhallow", "Bram Okonkwo-Vale")
    for at, row in enumerate(_rows_of(table, "SALT")):
        table["reading"][row] = names[at % 2]
    held = {"reading": {"salt": {"identifier": True, "top": 0}, "code": {"identifier": True, "top": 0}}}
    zone = inside_keyed.build_zone(table, "subject", (), DATED, {}, held, TYPED)
    assert zone is not None
    text = json.dumps(zone)
    assert not any(name in text for name in names)
    levels = {entry["level"]: entry for entry in zone["levels"]}
    assert ["reading", inside_keyed.KEPT_IDENTIFIER] in levels["SALT"]["held"]
    stand = _stand_in(table)
    twin = _twin(zone, stand)
    rows = _rows_of(twin, "SALT")
    assert all(twin["reading"][row] == stand["reading"][row] for row in rows)


def test_item2_no_cell_past_the_top_code_on_a_keyed_path() -> None:
    """A level the description top-codes at 90 (its twin's cells capped) keeps no cell past 90 nor a censoring mark past it, by the label path (two numbers) and the number path (mutant: a label written as its joint table asks)."""
    table = long_table(ROWS, 1)
    for at, row in enumerate(_rows_of(table, "MOOD")):
        table["reading"][row] = ("95", "110")[at % 2]
    for at, row in enumerate(_rows_of(table, "SALT")):
        table["reading"][row] = ("95", "110", "75", "20", ">95")[at % 5]
    held = {"reading": {"mood": {"identifier": False, "top": 90}, "salt": {"identifier": False, "top": 90},
                        "code": {"identifier": True, "top": 0}}}
    zone = inside_keyed.build_zone(table, "subject", (), DATED, {}, held, TYPED)
    assert zone is not None
    stand = _stand_in(table)
    for row in _rows_of(stand, "MOOD") + _rows_of(stand, "SALT"):
        cell = stand["reading"][row]
        stand["reading"][row] = "90" if cell in ("95", "110", ">95") else cell
    twin = _twin(zone, stand)
    for row in _rows_of(twin, "MOOD") + _rows_of(twin, "SALT"):
        cell = twin["reading"][row]
        assert not cell.startswith(">") and float(cell) <= 90.0, cell


def test_a_copy_keeps_its_own_top_code_key_by_key_and_is_not_written_where_held() -> None:
    """Codex's review of batch 4y, item 2: a copy is taken out of the modelled columns before their key blocks are
    read, so its own level's top code was lost (ages 92 to 116 written on the level's rows of a column the
    description top-codes there). Now the copy's rows of a level its own block top-codes at 90 hold no number past
    it, and a copy any of whose own blocks is held is not written (mutants: the copy's own levels not read; a held
    copy written)."""
    table = long_table(ROWS, 1)
    for at, row in enumerate(_rows_of(table, "SALT")):
        table["reading"][row] = str(92 + at % 25)
        table["reading_num"][row] = table["reading"][row]
    own = {"reading_num": {"salt": {"identifier": False, "top": 90, "privacy": False}}}
    zone = inside_keyed.build_zone(table, "subject", (), DATED, {}, own, TYPED)
    assert zone is not None
    assert zone["copies"] == [{"column": "reading_num", "from": "reading", "else": SENTINEL, "cap": 0,
                               "capped": ["salt"]}]
    stand = _stand_in(table)
    twin = _twin(zone, stand)
    salt = _rows_of(twin, "SALT")
    assert any(float(twin["reading"][row]) > 90.0 for row in salt)
    assert all(float(twin["reading_num"][row]) <= 90.0 for row in salt if _plain(twin["reading_num"][row]))
    for row in range(len(twin["item"])):
        if twin["item"][row] != "SALT" and _plain(twin["reading"][row]):
            assert twin["reading_num"][row] == twin["reading"][row]
    held = {"reading_num": {"salt": {"identifier": True, "top": 0, "privacy": False}}}
    zone = inside_keyed.build_zone(table, "subject", (), DATED, {}, held, TYPED)
    assert zone is not None and zone["copies"][0]["held"] is True
    assert _twin(zone, stand)["reading_num"] == stand["reading_num"]


def test_a_block_held_by_its_own_year_cut_is_never_modelled() -> None:
    """Codex's review of batch 4y, item 3: the nested block's year cut was dropped by `key_blocks_of`, so the keyed
    zone wrote birth years before the cut from the record's marginal on that level's rows. Every privacy mark of a
    key block now reaches the zone, the block is set aside, and its rows keep the twin's cells (mutants:
    `key_blocks_of` reading no mark but the top code; a privacy-held block modelled)."""
    document = {"columns": [{"name": "reading", "by_key": {"key": "item", "key_blocks": [
        {"key": "SALT", "block": {"role": "count", "top_coded_year": 1936}},
        {"key": "PULSE", "block": {"role": "count", "top_coded": 90}},
        {"key": "CODE", "block": {"role": "identifier"}}]}}]}
    _tops, read = inside_keyed.key_blocks_of(document)
    assert read["reading"]["salt"] == {"identifier": False, "top": 0, "privacy": True}
    assert read["reading"]["pulse"] == {"identifier": False, "top": 90, "privacy": False}
    assert read["reading"]["code"]["identifier"] is True
    table = long_table(ROWS, 1)
    r = random.Random(3)
    for row in _rows_of(table, "SALT"):
        table["reading"][row] = str(r.randint(1900, 1999))
    zone = inside_keyed.build_zone(table, "subject", (), DATED, {}, read, TYPED)
    assert zone is not None
    levels = {entry["level"]: entry for entry in zone["levels"]}
    assert ["reading", inside_keyed.KEPT_PRIVACY] in levels["SALT"]["held"]
    stand = _stand_in(table)
    for row in _rows_of(stand, "SALT"):
        stand["reading"][row] = str(max(1936, int(stand["reading"][row])))
    twin = _twin(zone, stand)
    rows = _rows_of(twin, "SALT")
    assert all(twin["reading"][row] == stand["reading"][row] for row in rows)
    assert min(int(twin["reading"][row]) for row in rows) >= 1936


def test_item5_the_persons_are_never_re_cut(made) -> None:  # type: ignore[no-untyped-def]
    """The person column, the ward a person holds and every column the key leaves alone stand as the twin wrote them (mutant: the persons re-cut to a census)."""
    _table, zone, stand, twin = made
    assert twin["subject"] == stand["subject"] and twin["ward"] == stand["ward"] and twin["shift"] == stand["shift"]
    assert "subject" not in inside_keyed.written_columns(zone)


def test_item6_a_later_clock_keeps_the_dates_presence_form_and_month(made) -> None:  # type: ignore[no-untyped-def]
    """The later clock is written exactly on the rows the stand-in writes it, in its form and month; moved, the device's rows read at once and the hand's later (mutants: presence drawn again; the month not kept)."""
    _table, zone, stand, twin = made
    assert [pair[0] for pair in zone["gaps"]] == ["seen_at"]
    assert [bool(cell) for cell in twin["seen_at"]] == [bool(cell) for cell in stand["seen_at"]]
    moved = 0
    for row in range(len(twin["item"])):
        cell = twin["seen_at"][row]
        if not cell:
            continue
        assert cell[:7] == stand["seen_at"][row][:7] and len(cell) == len(stand["seen_at"][row])
        if cell == stand["seen_at"][row] or twin["item"][row] in ("CODE", "SEEN"):
            continue
        moved += 1
        gap = (datetime.datetime.strptime(cell, "%Y-%m-%d %H:%M")
               - datetime.datetime.strptime(twin["taken_at"][row], "%Y-%m-%d %H:%M")).total_seconds() / 60.0
        if twin["source"][row] == "auto":
            assert gap == 0.0, (twin["item"][row], gap)
        elif twin["source"][row] == "hand":
            assert gap >= 1.0, (twin["item"][row], gap)
    assert moved > 1000, moved


def test_a_later_clocks_gap_is_read_between_its_grid_points() -> None:
    """A gap is read from the level's grid as a quantile function, so the largest gap seen weighs no more than the gaps beside it: on a grid of 200 noughts and one gap of 1,000 minutes the mean read is half the largest gap's share, not its whole (mutant: the grid's points drawn alike, 4.98 minutes)."""
    grid = [0 for _point in range(200)] + [1000]
    reads = [inside_keyed._gap_at(grid, (k + 0.5) / 20000) for k in range(20000)]
    assert abs(sum(reads) / len(reads) - 2.5) < 0.1, sum(reads) / len(reads)
    assert inside_keyed._gap_at([5, 7], 0.5) == 6 and inside_keyed._gap_at([5, 7], 1.0) == 7


def test_record_numbers_and_dates_are_not_carried(made) -> None:  # type: ignore[no-untyped-def]
    """A held block of record numbers and a level of dates keep the twin's cells (mutants: every held block modelled; no level read as dates)."""
    _table, zone, stand, twin = made
    levels = {entry["level"]: entry for entry in zone["levels"]}
    assert ["reading", inside_keyed.KEPT_IDENTIFIER] in levels["CODE"]["held"]
    assert ["reading", inside_keyed.KEPT_DATES] in levels["SEEN"]["held"]
    for item in ("CODE", "SEEN"):
        assert all(twin["reading"][row] == stand["reading"][row] for row in _rows_of(twin, item)), item


def test_columns_the_description_keeps_for_privacy_are_never_drawn() -> None:
    """Identifiers, free text, a withheld count, a year top code and a computed column are kept out of the zone, an age's 90 is not (mutant: only identifiers kept)."""
    document = {"columns": [
        {"name": "a", "role": "categorical"}, {"name": "b", "role": "free_text"},
        {"name": "c", "role": "categorical", "present_count_withheld": True},
        {"name": "d", "role": "count", "top_coded_year": 2000}, {"name": "e", "role": "identifier"},
        {"name": "f", "role": "continuous", "top_coded": 90}, {"name": "g", "role": "count", "computed_from": ["a"]},
    ]}
    assert inside_keyed.kept_by_description(document) == ("b", "c", "d", "e", "g")
    assert inside_keyed.typed_of({"columns": [{"name": "v", "by_key": {"key": "k", "key_blocks": []}},
                                              {"name": "w"}]}) == {"v": "k"}
    table = long_table(ROWS, 1)
    zone = inside_keyed.build_zone(table, "subject", ("unit",), DATED, {}, HELD, TYPED)
    assert zone is not None and "unit" not in zone["content"]


def test_the_same_seed_gives_the_same_cells(made) -> None:  # type: ignore[no-untyped-def]
    """A fixed function of the zone and the seed (mutant: the streams ignore the seed)."""
    _table, zone, stand, twin = made
    again = _twin(zone, stand, 0)
    other = _twin(zone, stand, 1)
    assert again["reading"] == twin["reading"] and again["unit"] == twin["unit"]
    assert other["reading"] != twin["reading"]


# -- through the commands at the table floor -----------------------------------------------------------------


def _places(folder: pathlib.Path) -> inside.Places:
    return inside.Places(pathlib.Path(folder, "installation", "synthtwin", "inside"), (), (),
                         installation.system_name(), ())


def _generated(folder: pathlib.Path, description: pathlib.Path, twin: pathlib.Path) -> str:
    with B.installed(folder):
        code, said = B.command(["generate", f"{description}", "--out-dir", f"{description.parent}", "--seed", "0",
                                "--replace"], False)
    assert code == 0, said[-600:]
    return twin.read_text(encoding="utf-8")


def _validate(folder: pathlib.Path, description: pathlib.Path) -> int:
    with B.installed(folder), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return int(cli.main(["validate", f"{description}", "--replace"], small_tables_refused=False))


def _route_s(folder: pathlib.Path, table: str, measurements: bool = True) -> "tuple[str, dict[str, object], str, str, int]":
    """Route S on a battery table at the floor, the keyed switch on in place: the real text, the record's keyed zone,
    the keyed twin, the twin of the same description and seed with the switch off, and validate's exit on the keyed
    twin (generated again, last). ``measurements``: whether the truthful holder answers the questions file's
    measurements asked on their own (lane IN-4c); the last round's questions file is left in `out`."""
    text = T.text(table, FLOOR_ROWS, 1)
    stem = pathlib.Path(T.FILES[table]).stem
    description = pathlib.Path(folder, "out", f"{stem}-profile.json")
    twin_path = pathlib.Path(folder, "out", f"{stem}-twin.csv")
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inside, "default_places", lambda: _places(folder))
        patch.setattr(cli, "_KEYED_ZONE_SHIPPED", True)
        patch.setattr(B, "ANSWER_MEASUREMENTS", measurements)
        product = B.make_twins(folder, table, text, (0,), False)
        assert not product.errors, product.errors
        records = sorted(_places(folder).private.glob(f"*{inside.SUFFIX}"))
        assert len(records) == 1
        zone = inside.load_record(records[0])["zones"]["keyed"]
        patch.setattr(cli, "_KEYED_ZONE_SHIPPED", False)
        off = _generated(folder, description, twin_path)
        patch.setattr(cli, "_KEYED_ZONE_SHIPPED", True)
        on = _generated(folder, description, twin_path)
        code = _validate(folder, description)
    return text, zone, on, off, code


def _keyed_alike(on: "list[dict[str, str]]", off: "list[dict[str, str]]", key: str, value: str,
                 carried: bool = False) -> None:
    """On each key level's rows the keyed column holds the keyed-off twin's written forms exactly (its values follow
    the record); with ``carried`` (lane STATS-B), a level whose keyed-off twin's cells a form cannot carry or whose
    number of decimals the level never writes (a whole-number stand-in on a level of thousandths, or on a level
    written to one place) may move cells to one form of its own, the level's commonest: every form it then writes is
    one the keyed-off twin writes there, or that one."""
    for level in sorted({row[key] for row in off}):
        mine = [row[value] for row in on if row[key] == level]
        theirs = [row[value] for row in off if row[key] == level]
        if sorted(_form(cell) for cell in mine) == sorted(_form(cell) for cell in theirs):
            continue
        assert carried, level
        moved = sorted(set(_form(cell) for cell in mine) - set(_form(cell) for cell in theirs))
        assert len(moved) <= 1, (level, moved)


def _checks_pass(tmp_path: pathlib.Path, table: str, text: str, twin: str) -> None:
    real_path, twin_path = tmp_path / "real.csv", tmp_path / "twin.csv"
    real_path.write_text(text, encoding="utf-8", newline="\n")
    twin_path.write_text(twin, encoding="utf-8", newline="\n")
    outcome = twin_checks.run_checks(str(real_path), str(twin_path), person=T.PERSON[table])
    assert outcome.passed, twin_checks.report_lines(outcome)


def _measured(folder: pathlib.Path, table: str) -> "list[dict[str, object]]":
    """The last round's questions file's measurements asked on their own (lane IN-4c), as entries."""
    stem = pathlib.Path(T.FILES[table]).stem
    questions = json.loads(pathlib.Path(folder, "out", f"{stem}-questions.json").read_text(encoding="utf-8"))
    section = questions[asking.MEASUREMENTS_ASKED] if asking.MEASUREMENTS_ASKED in questions else {}
    return list(section[asking.MEASUREMENTS_ENTRIES]) if section else []


def _no_layer(folder: pathlib.Path, table: str) -> None:
    """The last round's description publishes no patient layer: the record's keyed zone models the table, so the layer
    leaves it alone (batch 4y's fix round, plan P4-D513), whichever way a key block's own question stands (lane IN-4c)."""
    stem = pathlib.Path(T.FILES[table]).stem
    document = json.loads(pathlib.Path(folder, "out", f"{stem}-profile.json").read_text(encoding="utf-8"))
    relationships = document["relationships"]
    assert not (isinstance(relationships, dict) and isinstance(relationships.get("grain"), dict))


def _level(zone: "dict[str, object]", name: str) -> "dict[str, object]":
    return [entry for entry in zone["levels"] if entry["level"] == name][0]  # type: ignore[union-attr, index]


def _pressure_parts(rows: "list[dict[str, str]]") -> "tuple[list[float], list[float]]":
    pairs = [row["value"].split("/") for row in rows if row["item"] == "BP"]
    return [float(pair[0]) for pair in pairs], [float(pair[1]) for pair in pairs]


def _charting_alike(text: str, on: "list[dict[str, str]]", off: "list[dict[str, str]]") -> None:
    real = list(csv.DictReader(io.StringIO(text)))
    units: "dict[str, set[str]]" = {}
    devices: "dict[str, set[str]]" = {}
    for row in real:
        units.setdefault(row["item"], set()).add(row["unit"])
        devices.setdefault(row["item"], set()).add(row["device"])
    assert all(row["unit"] in units[row["item"]] and row["device"] in devices[row["item"]] for row in on)
    for name in ("unit", "device", "patient_id", "item"):
        assert sorted(row[name] for row in on) == sorted(row[name] for row in off), name
    _keyed_alike(on, off, "item", "value")


def test_the_charting_table_through_the_commands(tmp_path: pathlib.Path) -> None:
    """Route S on the charting table at the floor, the keyed switch on, the truthful holder answering the pressure's own question `measurement` (lane IN-4c): the record holds the zone and models the pressure pairs, the twin's unit and device follow the item from the keyed-off twin's own cells, each pressure part a spelling of that twin's own, the parts' correlation within 0.02 of the table's and the first part larger on as many rows, validate exits 0 and the five checks pass; the description publishes no patient layer, the keyed zone modelling the table (batch 4y, plan P4-D513) (mutants: generate reads no keyed zone; a label written as its joint table asks; the block's answer not read; the pairs left as dealt; the layer drawn on a table the keyed zone models)."""
    text, zone, on_text, off_text, code = _route_s(tmp_path / "product", "T3")
    on = list(csv.DictReader(io.StringIO(on_text)))
    off = list(csv.DictReader(io.StringIO(off_text)))
    assert zone["key"] == "item" and zone["scoped"] == ["value"]
    assert [(e["column"], e["measurement"], e["your_answer"]) for e in _measured(tmp_path / "product", "T3")] == [
        ("value", "BP", "measurement")]
    assert "value" in _level(zone, "BP")["pairs"]  # type: ignore[operator]
    _no_layer(tmp_path / "product", "T3")
    _charting_alike(text, on, off)
    mine, theirs = _pressure_parts(on), _pressure_parts(off)
    assert sorted(mine[0]) == sorted(theirs[0]) and sorted(mine[1]) == sorted(theirs[1])
    assert sum(a > b for a, b in zip(*mine)) == sum(a > b for a, b in zip(*theirs))
    real = _corr(*_pressure_parts(list(csv.DictReader(io.StringIO(text)))))
    assert abs(_corr(*mine) - real) < 0.02, (real, _corr(*mine))
    assert code == 0
    _checks_pass(tmp_path, "T3", text, on_text)


def test_the_charting_table_with_its_pressure_question_left_open(tmp_path: pathlib.Path) -> None:
    """The same route with the pressure's own question left blank: the questions file holds it open, read as `identifier`, the record does not model the pressure block, the twin keeps the keyed-off twin's made-up pressure cells, none a real pair, validate exits 0 and the five checks pass; the description publishes no patient layer, the keyed zone still modelling the table with the block held (batch 4y, plan P4-D513) (mutants: the question not put; a held block modelled; the layer drawn on a table the keyed zone models)."""
    text, zone, on_text, off_text, code = _route_s(tmp_path / "product", "T3", measurements=False)
    on = list(csv.DictReader(io.StringIO(on_text)))
    off = list(csv.DictReader(io.StringIO(off_text)))
    assert [(e["column"], e["measurement"], e["measurement_named_by"], e["read_as_now"], e["your_answer"])
            for e in _measured(tmp_path / "product", "T3")] == [("value", "BP", "item", "identifier", "")]
    assert not _level(zone, "BP")["pairs"]
    _no_layer(tmp_path / "product", "T3")
    _charting_alike(text, on, off)
    pressure = [at for at in range(len(on)) if on[at]["item"] == "BP"]
    real_pairs = {row["value"] for row in csv.DictReader(io.StringIO(text)) if row["item"] == "BP"}
    assert pressure and all(on[at]["value"] == off[at]["value"] for at in pressure)
    assert not any(on[at]["value"] in real_pairs for at in pressure)
    assert code == 0
    _checks_pass(tmp_path, "T3", text, on_text)


def test_the_laboratory_table_through_the_commands(tmp_path: pathlib.Path) -> None:
    """Route S on the laboratory table at the floor, the keyed switch on, the truthful holder answering the sodium's own question `measurement` (lane IN-4c): the record models the sodium results, validate exits 0, each dealt column holds that twin's cells, a result on each test's rows in that twin's written forms but where a form cannot carry its test's values (lane STATS-B: written in the test's own form, never `0` for a value that is not), the numeric copy is written by its rule from the result beside a source some tests top-code as possible ages (lane STATS-B, reversing lane IN-4c's hold: the result where it is a number, the sentinel elsewhere, never past 90 on a capped test's rows), and the five checks pass (mutants: the flag written by its rule whatever the cells hold; the copy written beside a held block; the copy held back beside a top-coded source; the cell's form kept whatever it writes)."""
    text, zone, on_text, off_text, code = _route_s(tmp_path / "product", "T6")
    on = list(csv.DictReader(io.StringIO(on_text)))
    off = list(csv.DictReader(io.StringIO(off_text)))
    assert zone["key"] == "test" and zone["scoped"] == ["result"]
    assert [(e["column"], e["measurement"], e["your_answer"]) for e in _measured(tmp_path / "product", "T6")] == [
        ("result", "SOD", "measurement")]
    assert "result" in _level(zone, "SOD")["numbers"]  # type: ignore[operator]
    assert inside_keyed.capped_anywhere(zone, "result")
    for name in ("unit", "ref_range", "abnormal", "patient_id", "test"):
        assert sorted(row[name] for row in on) == sorted(row[name] for row in off), name
    _keyed_alike(on, off, "test", "result", carried=True)
    for row in on:
        number = inside_keyed.plain_number(row["result"])
        assert row["result_num"] == (row["result"].strip() if number is not None else "9999999"), row
    real_zeros = {row["test"] for row in csv.DictReader(io.StringIO(text)) if row["result"].strip() in ("0", "0.0")}
    assert not [row for row in on if row["result"].strip() == "0" and row["test"] not in real_zeros]
    flagged = [row for row in on if row["test"] == "K" and row["ref_range"] == "3.5-5.1"
               and inside_keyed.plain_number(row["result"]) is not None]
    agree = sum(1 for row in flagged if (row["abnormal"] == "1") == (not 3.5 <= float(row["result"]) <= 5.1))
    assert flagged and agree >= 0.95 * len(flagged), (agree, len(flagged))
    assert code == 0
    _checks_pass(tmp_path, "T6", text, on_text)


REVIEW_NAMES = ("Orla Penhallow", "Bram Okonkwo-Vale")


def review_table(rows: int, seed: int) -> str:
    """The review table of batch 4x's items 1, 2, 5 and 6: 1,000 people of 10 or 30 rows, a person's arm, a visit
    sequence, keys whose values are two recurring clinician names, a pulse, ages past 89 with a censoring mark (and a
    level of two of them), a volume; a later clock written on about half the rows."""
    r = random.Random(f"review-{seed}")
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["patient_id", "arm", "visit", "measure", "value", "taken_at", "seen_at"])
    written = 0
    person = 0
    while written < rows:
        person += 1
        count = min(rows - written, 10 if person % 2 else 30)
        arm = "A" if r.random() < 0.5 else "B"
        start = r.randrange(300 * 1440)
        level = r.gauss(0.0, 8.0)
        for visit in range(1, count + 1):
            measure = r.choices(("provider", "pulse", "age", "volume", "years"), (0.25, 0.25, 0.2, 0.2, 0.1))[0]
            if measure == "provider":
                value = REVIEW_NAMES[0] if r.random() < 0.6 else REVIEW_NAMES[1]
            elif measure == "pulse":
                value = str(int(round(78.0 + level + r.gauss(0.0, 7.0))))
            elif measure == "age":
                value = r.choice(("95", "110", "75", "20", ">95"))
            elif measure == "volume":
                value = f"{r.uniform(100.0, 900.0):.1f}"
            else:
                value = r.choice(("95", "110"))
            moment = EPOCH + datetime.timedelta(minutes=start + 90 * visit + r.randrange(60))
            seen = "" if r.random() < 0.5 else (moment + datetime.timedelta(minutes=r.randrange(0, 45))).strftime(
                "%Y-%m-%d %H:%M")
            writer.writerow([f"P{4000000 + person}", arm, str(visit), measure, value, moment.strftime("%Y-%m-%d %H:%M"),
                             seen])
            written += 1
    return out.getvalue()


def test_items_1_2_5_6_through_the_commands(tmp_path: pathlib.Path) -> None:
    """The review table through the commands at the floor, the keyed switch on, against the keyed-off twin of the same description and seed: no real name and no age past 90 written, the persons, arms and visit sequences stand, the later clock keeps its presence and months, validate adds no miss (mutants: a held block of repeating values modelled; a label written as its joint table asks; the persons re-cut; presence drawn again)."""
    folder = tmp_path / "product"
    text = review_table(FLOOR_ROWS, 1)
    source = folder / "table" / "review.csv"
    out = folder / "out"
    source.parent.mkdir(parents=True)
    out.mkdir(parents=True)
    source.write_text(text, encoding="utf-8", newline="\n")
    description = out / "review-profile.json"
    twin_path = out / "review-twin.csv"
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inside, "default_places", lambda: _places(folder))
        patch.setattr(cli, "_KEYED_ZONE_SHIPPED", True)
        with B.installed(folder):
            code, said = B.command(["profile", f"{source}", "--out-dir", f"{out}", "--person", "patient_id",
                                    "--replace"], False)
        assert code == 0, said[-600:]
        records = sorted(_places(folder).private.glob(f"*{inside.SUFFIX}"))
        assert len(records) == 1
        zone = inside.load_record(records[0])["zones"]["keyed"]
        patch.setattr(cli, "_KEYED_ZONE_SHIPPED", False)
        off_text = _generated(folder, description, twin_path)
        code_off = _validate(folder, description)
        patch.setattr(cli, "_KEYED_ZONE_SHIPPED", True)
        on_text = _generated(folder, description, twin_path)
        code_on = _validate(folder, description)
    assert zone["key"] == "measure"
    assert not any(name in json.dumps(zone) for name in REVIEW_NAMES)
    on = list(csv.DictReader(io.StringIO(on_text)))
    off = list(csv.DictReader(io.StringIO(off_text)))
    assert on_text != off_text, "the keyed zone changed nothing: the case would not see it drawn"
    # Item 1: no real name; the held block's rows keep the keyed-off twin's cells.
    assert not any(row["value"] in REVIEW_NAMES for row in on)
    assert all(a["value"] == b["value"] for a, b in zip(on, off) if a["measure"] == "provider")
    # Item 2: no age past 90 and no censoring mark at 90 or past it (the description's own twin writes the class of
    # 90 and over as `>89`); the age rows hold only the keyed-off twin's cells.
    for row in on:
        if row["measure"] in ("age", "years"):
            cell = row["value"]
            if cell.startswith(">"):
                assert float(cell[1:]) < 90.0, cell
            else:
                assert float(cell) <= 90.0, cell
    for measure in ("age", "years"):
        assert (sorted(row["value"] for row in on if row["measure"] == measure)
                == sorted(row["value"] for row in off if row["measure"] == measure)), measure
    # Item 5: the persons, their arms and their visit sequences stand.
    for name in ("patient_id", "arm", "visit"):
        assert [row[name] for row in on] == [row[name] for row in off], name
    # Item 6: the later clock's presence and months stand on every row.
    assert [bool(row["seen_at"]) for row in on] == [bool(row["seen_at"]) for row in off]
    assert [row["seen_at"][:7] for row in on] == [row["seen_at"][:7] for row in off]
    assert code_on == code_off


def _review_described(folder: pathlib.Path, keyed: bool) -> "tuple[dict[str, object], list[dict[str, str]], dict]":
    """The review table described and twinned through the commands at the floor in a fresh installation: as shipped
    (`keyed`), or with the keyed zone's switch off and the table read as one the zone does not model (as a table above
    its rows bound is), so the layer stands: the description, the twin's rows and the record's zones."""
    source = folder / "table" / "review.csv"
    out = folder / "out"
    source.parent.mkdir(parents=True)
    out.mkdir(parents=True)
    source.write_text(review_table(FLOOR_ROWS, 1), encoding="utf-8", newline="\n")
    description = out / "review-profile.json"
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inside, "default_places", lambda: _places(folder))
        if not keyed:
            patch.setattr(cli, "_KEYED_ZONE_SHIPPED", False)
            patch.setattr(cli, "_keyed_zone_stands", lambda read, published: False)
        with B.installed(folder):
            code, said = B.command(["profile", f"{source}", "--out-dir", f"{out}", "--person", "patient_id",
                                    "--replace"], False)
        assert code == 0, said[-600:]
        records = sorted(_places(folder).private.glob(f"*{inside.SUFFIX}"))
        assert len(records) == 1
        zones = inside.load_record(records[0])["zones"]
        text = _generated(folder, description, out / "review-twin.csv")
    return json.loads(description.read_text(encoding="utf-8")), list(csv.DictReader(io.StringIO(text))), zones


def test_the_layer_leaves_a_keyed_table_alone_and_its_walk_keeps_each_level_s_values(tmp_path: pathlib.Path) -> None:
    """Batch 4y's fix round. With the keyed zone on, the review table (whose record holds a keyed zone) is described
    without the patient layer: the layer and the keyed zone together lost what the zone alone holds on the battery's
    keyed tables (dose units 9 of 9 runs to 0, item values 9 to 5). Where the zone does not model the table (its
    switch off and the table read as one above its rows bound), the layer stands, and the
    walk keeps each key level's values on its own rows: no number on a provider's row, no word on an age's, no age
    past 90 (on the merged head: 989 words and 1,384 numbers over 90 on the age rows of the description's own twin).
    Mutants: the layer drawn on a keyed table; `_following` leaving the value column where the row run wrote it."""
    document, rows, zones = _review_described(tmp_path / "keyed", True)
    relationships = document["relationships"]
    assert "keyed" in zones
    assert not (isinstance(relationships, dict) and isinstance(relationships.get("grain"), dict))
    document, rows, zones = _review_described(tmp_path / "layer", False)
    relationships = document["relationships"]
    assert "keyed" not in zones
    assert isinstance(relationships, dict) and isinstance(relationships.get("grain"), dict)
    for row in rows:
        cell = row["value"]
        numeric = inside_keyed.plain_number(cell.lstrip(">")) is not None
        if row["measure"] == "provider":
            assert not numeric, cell
        else:
            assert numeric, (row["measure"], cell)
        if row["measure"] in ("age", "years"):
            assert float(cell.lstrip(">")) <= 90.0, cell
