"""The trajectories zone of the inside record (lane IN-3, plan P4-D498): gate files on invented tables of known truth.

Each case builds a table of several rows a patient from a generator whose
truth it states, describes it into the zone (`zone_from_columns`), and reads
the zone back or applies it to a twin whose structure was taken away. The
mutant each case is red on is named in its docstring; the lane's mutant
runner patches a scratch copy of the module and runs the case.
"""

import json
import math
import os
import pathlib
import random
import statistics

import typing

import pytest

from synthtwin import inside, inside_trajectories as I

PERSON = "patient_id"


def _visits(patients: int, seed: int, *, patient_sd: float = 0.9, row_term: float = 0.5, slope_sd: float = 0.6,
            level_shape: str = "normal", gap_days: "tuple[int, int]" = (25, 31), long_tail: bool = False) -> "dict[str, list[str]]":
    """An invented visits table: an arm, an age, a visit number, a visit date, a pressure with a random level and slope,
    and a yes/no outcome on a latent threshold with a patient term and a term on the row's pressure."""
    r = random.Random(seed)
    out: "dict[str, list[str]]" = {name: [] for name in (PERSON, "arm", "age", "visit", "visit_date", "sbp", "event")}
    for p in range(patients):
        visits = 1 + min(59 if long_tail else 20, int(r.expovariate(1 / (9.0 if long_tail else 5.0))))
        arm = r.random() < 0.5
        age = r.randint(30, 80)
        if level_shape == "skewed":
            level = 12.0 * (r.expovariate(1.0) - 1.0)
        else:
            level = r.gauss(0.0, 12.0)
        slope = r.gauss(0.0, slope_sd)
        u = r.gauss(0.0, patient_sd)
        day = 18000 + r.randrange(800)
        noise = r.gauss(0.0, 8.0)
        for k in range(visits):
            if k:
                day += r.randint(*gap_days)
                noise = 0.5 * noise + r.gauss(0.0, 8.0 * math.sqrt(0.75))
            sbp = 138.0 + level + (-0.4 - 0.8 * arm + slope) * k + 0.15 * (age - 60) + noise
            latent = -1.2 + row_term * (sbp - 138.0) / 10.0 + 0.5 * (not arm) + u + r.gauss(0.0, 1.0)
            year, month, date = I.civil_from_days(day)
            for name, value in ((PERSON, f"P{100000 + p}"), ("arm", "B" if arm else "A"), ("age", f"{age}"),
                                ("visit", f"{k + 1}"), ("visit_date", f"{year:04d}-{month:02d}-{date:02d}"),
                                ("sbp", f"{int(round(sbp))}"), ("event", "Y" if latent > 0 else "N")):
                out[name] += [value]
    return out


def _shuffled_within_column(columns: "dict[str, list[str]]", names: "tuple[str, ...]", seed: int) -> "dict[str, list[str]]":
    """A stand-in for a twin that lost these columns' structure: each column's cells permuted over the rows on its own."""
    r = random.Random(seed)
    out = {name: list(cells) for name, cells in columns.items()}
    for name in names:
        cells = list(out[name])
        r.shuffle(cells)
        out[name] = cells
    return out


def _pairs_agreement(columns: "dict[str, list[str]]", name: str, yes: str) -> float:
    """The correlation of a yes/no outcome between neighbouring rows of one patient (phi over consecutive pairs)."""
    first: "list[float]" = []
    second: "list[float]" = []
    keys = columns[PERSON]
    cells = columns[name]
    for row in range(1, len(keys)):
        if keys[row] == keys[row - 1]:
            first += [1.0 if cells[row - 1] == yes else 0.0]
            second += [1.0 if cells[row] == yes else 0.0]
    return statistics.correlation(first, second)


def _apply(zone: "dict[str, object]", columns: "dict[str, list[str]]", seed: int = 0) -> "dict[str, list[str]]":
    names = list(columns)
    got = I.applied(json.loads(json.dumps(zone)), names, columns, seed)
    out = {name: list(cells) for name, cells in columns.items()}
    if got.order is not None:
        for name in out:
            out[name] = [columns[name][row] for row in got.order]
    for name, cells in got.columns.items():
        out[name] = cells
    return out


@pytest.fixture(scope="module")
def visits() -> "dict[str, list[str]]":
    return _visits(900, 11)


@pytest.fixture(scope="module")
def zone(visits: "dict[str, list[str]]") -> "dict[str, object]":
    made = I.zone_from_columns(visits, PERSON, (PERSON,))
    assert made is not None
    return made


def test_the_zone_is_a_model_whose_size_does_not_follow_the_rows(visits: "dict[str, list[str]]", zone: "dict[str, object]") -> None:
    """No key, no row, and twice the rows move the zone's size by under 5 per cent (mutant: the zone keeps each patient's key)."""
    text = json.dumps(zone, sort_keys=True)
    assert not any(key in text for key in set(visits[PERSON]))
    bigger = I.zone_from_columns(_visits(1800, 11), PERSON, (PERSON,))
    assert bigger is not None
    grown = len(json.dumps(bigger, sort_keys=True)) / len(text)
    assert grown < 1.05, grown


def test_a_yes_no_outcome_keeps_its_patient_and_its_row_number(visits: "dict[str, list[str]]", zone: "dict[str, object]") -> None:
    """The latent within-patient correlation and the term on the row's pressure are read, and a twin that lost them gets them back with its yes count unchanged (mutant: the patient's shared draw left out)."""
    binaries = {entry["column"]: entry for entry in zone["binaries"]}
    entry = binaries["event"]
    truth = 0.81 / (0.81 + 1.0)
    assert abs(entry["latent_corr"] - truth) < 0.12, entry["latent_corr"]
    terms = dict(zip(entry["terms"], entry["coefficients"]))
    assert terms["row:sbp"] > 0.15
    lost = _shuffled_within_column(visits, ("event",), 5)
    twin = _apply(zone, lost)
    assert sorted(twin["event"]) == sorted(lost["event"])
    real = _pairs_agreement(visits, "event", "Y")
    assert abs(_pairs_agreement(lost, "event", "Y")) < 0.06
    assert _pairs_agreement(twin, "event", "Y") > 0.6 * real, (real, _pairs_agreement(twin, "event", "Y"))
    both = [(float(s), 1.0 if e == "Y" else 0.0) for s, e in zip(twin["sbp"], twin["event"])]
    assert statistics.correlation([a for a, _b in both], [b for _a, b in both]) > 0.1


def test_the_gaps_take_the_real_shape_and_the_first_dates_the_real_calendar(zone: "dict[str, object]") -> None:
    """A twin whose gaps are 1 to 120 days gets the real 25 to 31 days back (each patient's gaps scaled to the pace it draws and the dates set to the real calendar, so a few stand some days past them), and each patient's first date is the real calendar's (mutant: the gaps not read off the zone's quantile function)."""
    other = _visits(900, 11, gap_days=(1, 120))
    twin = _apply(zone, other)
    firsts: "dict[str, str]" = {}
    gaps: "list[int]" = []
    previous: "dict[str, int]" = {}
    for key, cell in zip(twin[PERSON], twin["visit_date"]):
        moment = I.moment_of(cell)
        assert moment is not None and moment.kind == I.KIND_DATE
        day = moment.seconds // I.SECONDS_A_DAY
        if key in previous:
            gaps += [day - previous[key]]
        else:
            firsts[key] = cell
        previous[key] = day
    ordered = sorted(gaps)
    assert ordered[len(ordered) // 10] >= 25 and ordered[(9 * len(ordered)) // 10] <= 31
    assert 27 <= ordered[len(ordered) // 2] <= 29 and ordered[0] >= 15 and ordered[-1] <= 45
    real = _visits(900, 11)
    real_firsts: "dict[str, str]" = {}
    for key, cell in zip(real[PERSON], real["visit_date"]):
        if key not in real_firsts:
            real_firsts[key] = cell
    mine = sorted(firsts.values())
    theirs = sorted(real_firsts.values())
    for share in (0.25, 0.5, 0.75):
        a = I.moment_of(mine[int(share * len(mine))])
        b = I.moment_of(theirs[int(share * len(theirs))])
        assert a is not None and b is not None and abs(a.seconds - b.seconds) <= 30 * I.SECONDS_A_DAY


def test_the_long_patients_take_the_census() -> None:
    """A twin whose top patients were flattened to even lengths takes the real census of rows a patient back, each patient's fixed cells one value (mutant: no row moves)."""
    real = _visits(700, 3, long_tail=True)
    made = I.zone_from_columns(real, PERSON, (PERSON,))
    assert made is not None
    counts: "dict[str, int]" = {}
    for key in real[PERSON]:
        counts[key] = counts[key] + 1 if key in counts else 1
    flat = _visits(700, 3, long_tail=True)
    keys = flat[PERSON]
    lengths: "dict[str, int]" = {}
    for key in keys:
        lengths[key] = lengths[key] + 1 if key in lengths else 1
    # The stand-in twin: the same rows, its long patients' rows handed round so none holds over 15.
    order = sorted(lengths, key=lambda key: -lengths[key])
    assert max(lengths.values()) > 30
    twin = _apply(made, _flattened(flat, 15))
    got: "dict[str, int]" = {}
    for key in twin[PERSON]:
        got[key] = got[key] + 1 if key in got else 1
    assert sorted(got.values()) == sorted(counts.values())
    for name in ("arm", "age"):
        per: "dict[str, set[str]]" = {}
        for key, cell in zip(twin[PERSON], twin[name]):
            per.setdefault(key, set()).add(cell)
        assert all(len(values) == 1 for values in per.values())
    assert order


def _flattened(columns: "dict[str, list[str]]", most: int) -> "dict[str, list[str]]":
    """The rows of patients over `most` rows handed one by one to the patients under `most`, as a flattened top band would make them."""
    keys = columns[PERSON]
    rows_of: "dict[str, list[int]]" = {}
    for row, key in enumerate(keys):
        rows_of.setdefault(key, []).append(row)
    extra: "list[int]" = []
    for key in rows_of:
        while len(rows_of[key]) > most:
            extra += [rows_of[key].pop()]
    for key in sorted(rows_of, key=lambda key: len(rows_of[key])):
        while extra and len(rows_of[key]) < most:
            rows_of[key] += [extra.pop()]
    out: "dict[str, list[str]]" = {name: [] for name in columns}
    for key in rows_of:
        first = rows_of[key][0]
        for place, row in enumerate(rows_of[key]):
            for name in columns:
                if name in (PERSON, "arm", "age"):
                    out[name] += [columns[name][first]]
                elif name == "visit":
                    out[name] += [f"{place + 1}"]
                else:
                    out[name] += [columns[name][row]]
    return out


def _levels(patients: int, seed: int, kind: str) -> "dict[str, list[str]]":
    """An invented visits table with no date: a bimodal random level (two groups of patients 30 apart) and a small noise,
    or a normal level with a random slope of 1.0 a visit; no arm effect on the slope."""
    r = random.Random(seed)
    out: "dict[str, list[str]]" = {name: [] for name in (PERSON, "arm", "visit", "sbp")}
    for p in range(patients):
        visits = 2 + min(18, int(r.expovariate(1 / 6.0)))
        arm = r.random() < 0.5
        if kind == "bimodal":
            level, slope, noise_sd = (15.0 if r.random() < 0.5 else -15.0) + r.gauss(0.0, 3.0), 0.0, 4.0
        else:
            level, slope, noise_sd = r.gauss(0.0, 12.0), r.gauss(0.0, 1.0), 8.0
        noise = r.gauss(0.0, noise_sd)
        for k in range(visits):
            if k:
                noise = 0.5 * noise + r.gauss(0.0, noise_sd * math.sqrt(0.75))
            for name, cell in ((PERSON, f"P{200000 + p}"), ("arm", "B" if arm else "A"), ("visit", f"{k + 1}"),
                               ("sbp", f"{138.0 + level + slope * k + noise:.0f}")):
                out[name] += [cell]
    return out


def _within_spread(columns: "dict[str, list[str]]") -> float:
    groups: "dict[str, list[float]]" = {}
    for key, cell in zip(columns[PERSON], columns["sbp"]):
        groups.setdefault(key, []).append(float(cell))
    squares = sum(sum((value - statistics.fmean(values)) ** 2 for value in values) for values in groups.values())
    return math.sqrt(squares / sum(len(values) - 1 for values in groups.values()))


def test_the_random_level_is_a_distribution_not_a_normal_spread() -> None:
    """A bimodal random level is kept as its shape, so a twin's patients stay in their own group: the spread within a patient within a quarter of the real (mutant: the shape read as the normal one, 5.0 against 3.6)."""
    real = _levels(1200, 3, "bimodal")
    made = I.zone_from_columns(real, PERSON, (PERSON,))
    assert made is not None
    shape = {e["column"]: e for e in made["numbers"]}["sbp"]["level_shape"]
    assert shape[55] - shape[45] > 0.6
    twin = _apply(made, _shuffled_within_column(real, ("sbp",), 9))
    assert _within_spread(twin) < 1.25 * _within_spread(real), (_within_spread(real), _within_spread(twin))


def test_the_random_slope_is_read_with_each_patients_noise() -> None:
    """A slope spread of 1.0 a visit is read within 0.2 of it, weighing each patient's line by its noise (mutant: the lines read as if they held no noise)."""
    real = _levels(1500, 33, "slope")
    made = I.zone_from_columns(real, PERSON, (PERSON,))
    assert made is not None
    entry = {e["column"]: e for e in made["numbers"]}["sbp"]
    assert entry["axis"] == I.AXIS_POSITION and entry["scale"] == I.SCALE_LINEAR
    per_visit = entry["slope_sd"] / entry["time_spread"] * entry["spread"]
    assert abs(per_visit - 1.0) < 0.2, per_visit


def test_every_dealt_column_keeps_its_own_cells(visits: "dict[str, list[str]]", zone: "dict[str, object]") -> None:
    """The repeated columns are dealt, never written: each keeps its multiset of cells (mutant: a dealt cell written from its latent score)."""
    lost = _shuffled_within_column(visits, ("sbp", "event"), 13)
    twin = _apply(zone, lost)
    for name in ("sbp", "event"):
        assert sorted(twin[name]) == sorted(lost[name])
    assert twin["sbp"] != lost["sbp"]


def test_the_twin_is_one_at_a_seed_and_another_at_another(visits: "dict[str, list[str]]", zone: "dict[str, object]") -> None:
    """The same zone, twin and seed give the same cells; another seed other cells (mutant: the stream seeded without the twin's seed)."""
    lost = _shuffled_within_column(visits, ("sbp", "event"), 13)
    assert _apply(zone, lost, 4) == _apply(zone, lost, 4)
    assert _apply(zone, lost, 4)["sbp"] != _apply(zone, lost, 5)["sbp"]


def _keyed(patients: int, seed: int) -> "dict[str, list[str]]":
    """An invented charting table: an item key; item A a value with a patient level and a trend over the hours, written
    in two units (on a few rows in tenths) with a copy of the value beside it; item B a value of its own; item C words."""
    r = random.Random(seed)
    out: "dict[str, list[str]]" = {name: [] for name in (PERSON, "item", "value", "copy", "unit", "taken_at")}
    for p in range(patients):
        level = r.gauss(0.0, 10.0)
        start = 18000 * 1440 + r.randrange(500 * 1440)
        moments = sorted(r.randrange(72 * 60) for _k in range(1 + int(r.expovariate(1 / 12.0))))
        for minutes in moments:
            item = r.choice("AAABC")
            if item == "A":
                value = 80.0 + level - 0.08 * minutes / 60.0 + r.gauss(0.0, 8.0)
                tenths = r.random() < 0.08
                text = f"{value / 10.0:.1f}" if tenths else f"{value:.0f}"
                unit = "per ten" if tenths else "per one"
            elif item == "B":
                text, unit = f"{r.gauss(17.0, 3.0):.0f}", "per minute"
            else:
                text, unit = r.choice(("alert", "voice", "pain")), ""
            moment = start + minutes
            year, month, date = I.civil_from_days(moment // 1440)
            for name, cell in ((PERSON, f"Q{5000 + p}"), ("item", item), ("value", text), ("copy", text), ("unit", unit),
                               ("taken_at", f"{year:04d}-{month:02d}-{date:02d} {(moment % 1440) // 60:02d}:{moment % 60:02d}")):
                out[name] += [cell]
    return out


def _icc(columns: "dict[str, list[str]]") -> float:
    """One-way intraclass correlation of item A's values, each written back to one unit."""
    groups: "dict[str, list[float]]" = {}
    for key, item, value, unit in zip(columns[PERSON], columns["item"], columns["value"], columns["unit"]):
        if item == "A":
            groups.setdefault(key, []).append(float(value) * (10.0 if unit == "per ten" else 1.0))
    kept = [values for values in groups.values() if len(values) >= 2]
    grand = statistics.fmean([value for values in kept for value in values])
    within = sum(sum((value - statistics.fmean(values)) ** 2 for value in values) for values in kept)
    within_df = sum(len(values) - 1 for values in kept)
    n0 = statistics.fmean([len(values) for values in kept])
    between = sum(len(values) * (statistics.fmean(values) - grand) ** 2 for values in kept) / (len(kept) - 1)
    mw = within / within_df
    return max(0.0, (between - mw) / n0) / (max(0.0, (between - mw) / n0) + mw)


def test_a_keyed_tables_values_follow_their_keys_trajectory() -> None:
    """Item A's patient level comes back on a twin that lost it, each value with its unit and its copy on its row (mutant: the value dealt alone, not its row's content)."""
    real = _keyed(800, 41)
    made = I.zone_from_columns(real, PERSON, (PERSON,))
    assert made is not None and made["key"] == "item"
    entries = {entry["level"]: entry for entry in made["keys"]}
    assert "A" in entries and entries["A"]["unit"] == "unit"
    lost = dict(real)
    rows_a = [row for row, item in enumerate(real["item"]) if item == "A"]
    shuffled = list(rows_a)
    random.Random(2).shuffle(shuffled)
    for name in ("value", "copy", "unit"):
        cells = list(real[name])
        for row, source in zip(rows_a, shuffled):
            cells[row] = real[name][source]
        lost[name] = cells
    assert _icc(lost) < 0.1 < _icc(real)
    twin = _apply(made, lost)
    assert twin["value"] == twin["copy"]

    def contents(columns: "dict[str, list[str]]") -> "list[tuple[str, str, str]]":
        return sorted((v, u, i) for v, u, i in zip(columns["value"], columns["unit"], columns["item"]))

    assert contents(twin) == contents(lost)
    assert twin["value"] != lost["value"]
    assert _icc(twin) > 0.6 * _icc(real), (_icc(real), _icc(twin))


def test_the_record_holds_the_zone_inside_and_refuses_another_tables(tmp_path: pathlib.Path, zone: "dict[str, object]", visits: "dict[str, list[str]]") -> None:
    """The zone is written into the inside record (marker first, owner-only) and read back for the same table only (mutant: the table's columns and rows not checked on reading)."""
    private = tmp_path / "private"
    places = inside.Places(private, (), (), "posix")
    names = list(visits)
    written = I.write_zone(zone, "visits", len(visits[PERSON]), names, places)
    assert written is not None and inside.carries_marker(written.path)
    assert I.zone_of_record("visits", names, len(visits[PERSON]), places) == json.loads(json.dumps(zone))
    assert I.zone_of_record("visits", names[:-1], len(visits[PERSON]), places) is None
    assert I.zone_of_record("visits", names, len(visits[PERSON]) + 1, places) is None
    assert I.zone_of_record("clinic", names, len(visits[PERSON]), places) is None


def test_a_twin_without_its_patients_is_left_as_made(zone: "dict[str, object]", visits: "dict[str, list[str]]") -> None:
    """A twin with a row naming no patient, or without the zone's person column, is not touched (mutant: the empty key read as a patient)."""
    blank = {name: list(cells) for name, cells in visits.items()}
    blank[PERSON][3] = ""
    got = I.applied(zone, list(blank), blank, 0)
    assert got.columns == {} and got.order is None
    other = {name: cells for name, cells in visits.items() if name != PERSON}
    assert I.applied(zone, list(other), other, 0).columns == {}


def test_the_commands_write_the_zone_inside_and_the_twin_follows_it(tmp_path: pathlib.Path, monkeypatch: "pytest.MonkeyPatch") -> None:
    """Route S on an invented visits table with the patient layer on: `profile` writes the zone into the inside record
    (marker first, owner-only, nothing of it in the description) and `generate` makes the twin's patients take the real
    census of rows a patient, which the walk alone flattens (mutant: generate's hook left out)."""
    import reliability_battery as B
    import reliability_tables as T

    from synthtwin import cli, installation

    def places() -> inside.Places:
        return inside.Places(pathlib.Path(installation.data_folder(), inside.FOLDER), (), (), installation.system_name())

    monkeypatch.setattr(cli, "_PATIENT_LAYER_SHIPPED", True)
    monkeypatch.setattr(inside, "default_places", places)
    text = T.text("T2", 20000, 2)
    product = B.make_twins(pathlib.Path(f"{tmp_path}"), "T2", text, (0,), True)
    assert product.errors == {}
    # The zone joins the record bound to the description's place and bytes (Codex's review of batch 4w, item 14).
    record = cli._inside_record_at(pathlib.Path(f"{tmp_path}", "out", "visits-profile.json"),
                                   pathlib.Path(f"{tmp_path}", "installation", "synthtwin", inside.FOLDER))
    assert inside.carries_marker(record) and I.ZONE in inside.load_record(record)["zones"]  # type: ignore[operator]
    if os.name != "nt":
        assert record.stat().st_mode & 0o077 == 0
    description = pathlib.Path(f"{tmp_path}", "out", "visits-profile.json").read_text(encoding="utf-8")
    assert I.ZONE not in json.loads(description) and inside.MARKER not in description

    def census(body: str) -> "list[int]":
        counts: "dict[str, int]" = {}
        for line in body.splitlines()[1:]:
            key = line.split(",")[0]
            counts[key] = counts[key] + 1 if key in counts else 1
        return sorted(counts.values())

    assert census(product.twins[0]) == census(text)


def test_the_fits_read_whole_patients_up_to_their_bound(visits: "dict[str, list[str]]", monkeypatch: "pytest.MonkeyPatch") -> None:
    """Past `FIT_ROWS` rows the fits read whole patients up to the bound, the same ones every time, and still read the yes/no outcome's patient (mutant: every patient read whatever the bound)."""
    rows_of: "dict[str, list[int]]" = {}
    for row, key in enumerate(visits[PERSON]):
        rows_of.setdefault(key, []).append(row)
    ordered = list(rows_of.values())
    monkeypatch.setattr(I, "FIT_ROWS", 2000)
    sample = I._fit_sample(ordered)
    assert sample == I._fit_sample(ordered)
    assert all(kept == whole or kept == [] for kept, whole in zip(sample, ordered))
    assert 1800 <= sum(len(kept) for kept in sample) <= 2000
    made = I.zone_from_columns(visits, PERSON, (PERSON,))
    assert made is not None
    entry = {e["column"]: e for e in made["binaries"]}["event"]
    assert abs(entry["latent_corr"] - 0.81 / 1.81) < 0.2


def test_the_two_steps_compose_to_the_whole(visits: "dict[str, list[str]]", zone: "dict[str, object]") -> None:
    """The timing step, then the dealing step on its twin, give the cells of both at once, so another zone's step may stand between them (mutant: the dealing step run within the timing step)."""
    lost = _shuffled_within_column(visits, ("sbp", "event", "visit_date"), 17)
    names = list(lost)
    first = I.applied(json.loads(json.dumps(zone)), names, lost, 6, dealing=False)
    middle = {name: list(cells) for name, cells in first.columns.items()}
    assert sorted(middle["sbp"]) == sorted(lost["sbp"]) and middle["sbp"] != _apply(zone, lost, 6)["sbp"]
    second = I.applied(json.loads(json.dumps(zone)), names, middle, 6, timing=False)
    whole = I.applied(json.loads(json.dumps(zone)), names, lost, 6)
    assert second.columns == whole.columns


def test_a_zone_that_cannot_be_read_leaves_the_commands_whole(tmp_path: pathlib.Path, monkeypatch: "pytest.MonkeyPatch") -> None:
    """A producer that raises on a table leaves `profile` and `generate` to finish as before, with no record written (mutant: the producer's error let through)."""
    import reliability_battery as B
    import reliability_tables as T

    from synthtwin import cli, installation

    def places() -> inside.Places:
        return inside.Places(pathlib.Path(installation.data_folder(), inside.FOLDER), (), (), installation.system_name())

    def broken(columns: "dict[str, list[str]]", person: str, identifiers: "tuple[str, ...]" = ()) -> "dict[str, object] | None":
        raise ValueError("an invented failure of the producer")

    monkeypatch.setattr(cli, "_PATIENT_LAYER_SHIPPED", True)
    monkeypatch.setattr(inside, "default_places", places)
    monkeypatch.setattr(I, "zone_from_columns", broken)
    product = B.make_twins(pathlib.Path(f"{tmp_path}"), "T2", T.text("T2", 20000, 4), (0,), True)
    assert product.errors == {} and 0 in product.twins
    # No zone joins the record bound to the description (Codex's review of batch 4w, item 14).
    record = cli._inside_record_at(pathlib.Path(f"{tmp_path}", "out", "visits-profile.json"),
                                   pathlib.Path(f"{tmp_path}", "installation", "synthtwin", inside.FOLDER))
    assert not inside.carries_marker(record) or I.ZONE not in inside.load_record(record)["zones"]  # type: ignore[operator]


@pytest.fixture(scope="module", autouse=True)
def _inside_record_switched_on() -> "typing.Iterator[None]":
    """The inside record's sub-switch is on for this file (`cli._inside_record_switched_on`)."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("synthtwin.cli._INSIDE_RECORD_SHIPPED", True)
        yield
