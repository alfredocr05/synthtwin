"""The dates zone's ties and the relations zone's identities (lane STATS-B): a chained gap placed by the other columns of its row, the columns it places dealt again on it, and a record-number column equal to another on the rows of some levels.

THE GAPS THEY CLOSE (the reliability battery, K-RU-01, on the batch 4z
head): an operation's minutes on the cases table followed its service
alone, so a regression of the duration on the case's class and urgency, a
recovery time's rank correlation with the duration and a logistic of a
critical-care stay on the hours all read nothing (0 of 9 runs each); and
the accounts table's subscriber, the patient exactly where the
relationship is `Self`, was never the twin's patient (0 of 9).

Machine-free: invented tables of a few thousand rows, drawn here from a
seed, read by the zones' own functions.
"""

import datetime
import math
import random

from synthtwin import inside_dates, inside_relations

EPOCH = datetime.datetime(2022, 3, 1, 7, 30)
SERVICES = ("GEN", "ORTHO", "CARD")


def _cases(rows: int, seed: int) -> "dict[str, list[str]]":
    """Cases: a service and an urgency set an operation's minutes; a critical-care stay follows the minutes."""
    draw = random.Random(f"ties-{seed}")
    out: "dict[str, list[str]]" = {"service": [], "emergency": [], "incision": [], "close": [], "critical": []}
    for _row in range(rows):
        service = draw.choice(SERVICES)
        emergency = draw.random() < 0.2
        start = EPOCH + datetime.timedelta(days=draw.randrange(300), minutes=15 * draw.randrange(30))
        minutes = math.exp(draw.gauss({"GEN": 4.2, "ORTHO": 4.5, "CARD": 5.1}[service] + 0.5 * emergency, 0.4))
        close = start + datetime.timedelta(minutes=max(5, int(round(minutes))))
        critical = draw.random() < 1.0 / (1.0 + math.exp(-(-4.0 + 0.6 * minutes / 60.0)))
        out["service"] += [service]
        out["emergency"] += ["Y" if emergency else "N"]
        out["incision"] += [start.strftime("%Y-%m-%d %H:%M")]
        out["close"] += [close.strftime("%Y-%m-%d %H:%M")]
        out["critical"] += ["Y" if critical else "N"]
    return out


def _levels(cells: "list[str]") -> "list[str]":
    counts: "dict[str, int]" = {}
    for cell in cells:
        counts[cell] = counts.get(cell, 0) + 1
    return [cell for _count, cell in sorted((-count, cell) for cell, count in counts.items())]


def _zone_and_sources(table: "dict[str, list[str]]") -> "tuple[dict[str, object], inside_dates.Census, list[inside_dates.TieSource]]":
    rows = len(table["service"])
    gathered = inside_dates.census("", {}, (), False)
    for name in ("service", "emergency", "incision", "close", "critical"):
        inside_dates.take_column(gathered, name, table[name])
    zone = inside_dates.zone_of(gathered)
    at = inside_dates.tie_rows(rows)
    sources = [inside_dates.TieSource(name, "label", [table[name][row] for row in at], [], _levels(table[name]), place)
               for name, place in (("service", 0), ("emergency", 1), ("critical", 4))]
    return zone, gathered, sources


def _minutes(cells: "dict[str, list[str]]", row: int) -> float:
    first = datetime.datetime.strptime(cells["incision"][row], "%Y-%m-%d %H:%M")
    second = datetime.datetime.strptime(cells["close"][row], "%Y-%m-%d %H:%M")
    return (second - first).total_seconds() / 60.0


def _twin(table: "dict[str, list[str]]", seed: int) -> "dict[str, list[str]]":
    """A twin as the zones before the ties leave it: each service's minutes and the critical-care cells shuffled
    apart from the urgency and the minutes."""
    draw = random.Random(f"twin-{seed}")
    rows = len(table["service"])
    out = {name: list(cells) for name, cells in table.items()}
    for service in SERVICES:
        mine = [row for row in range(rows) if table["service"][row] == service]
        minutes = [_minutes(table, row) for row in mine]
        draw.shuffle(minutes)
        for row, value in zip(mine, minutes):
            start = datetime.datetime.strptime(table["incision"][row], "%Y-%m-%d %H:%M")
            out["close"][row] = (start + datetime.timedelta(minutes=value)).strftime("%Y-%m-%d %H:%M")
    draw.shuffle(out["critical"])
    return out


def _mean(values: "list[float]") -> float:
    return sum(values) / len(values)


def test_a_gap_is_tied_to_its_row_and_dealt_again_within_its_cells() -> None:
    """The chain incision -> close is tied to the urgency; on a twin whose minutes ignore it, the ties deal each
    service's own minutes again so the urgent cases' minutes are longer, every gap stays one of its service's own and
    every close stays after its incision (mutants: no term enters; the twin's gaps not dealt; the cell ignored)."""
    table = _cases(4000, 1)
    zone, gathered, sources = _zone_and_sources(table)
    chain = zone["columns"]["close"]["chain"]  # type: ignore[index]
    assert chain["reference"] == "incision"
    assert inside_dates.tie_chains(zone, gathered, inside_dates.tie_rows(4000), sources) >= 1
    tie = chain["tie"]
    assert ["emergency", "level", "Y"] in tie["terms"] or ["emergency", "level", "N"] in tie["terms"]
    assert inside_dates.tied(zone)
    assert set(inside_dates.tie_columns(zone)) >= {"emergency", "critical"}
    # ...and the dates the ties read are the chain's two columns alone (a twin's other date columns are never read).
    assert inside_dates.tie_dates(zone) == ["incision", "close"]
    twin = _twin(table, 2)
    rows = len(table["service"])
    urgent = [row for row in range(rows) if twin["emergency"][row] == "Y"]
    routine = [row for row in range(rows) if twin["emergency"][row] == "N"]
    before = _mean([_minutes(twin, row) for row in urgent]) / _mean([_minutes(twin, row) for row in routine])
    moved = inside_dates.tied_again(zone, {name: list(cells) for name, cells in twin.items()}, rows, 7)
    assert "close" in moved and "incision" not in moved
    after_cells = dict(twin)
    after_cells["close"] = moved["close"]
    after = _mean([_minutes(after_cells, row) for row in urgent]) / _mean([_minutes(after_cells, row) for row in routine])
    real = _mean([_minutes(table, row) for row in urgent]) / _mean([_minutes(table, row) for row in routine])
    assert before < 1.1 < real
    assert abs(after - real) < 0.5 * (real - 1.0), (before, after, real)
    for service in SERVICES:
        mine = [row for row in range(rows) if twin["service"][row] == service]
        assert sorted(_minutes(twin, row) for row in mine) == sorted(_minutes(after_cells, row) for row in mine)
    assert all(_minutes(after_cells, row) >= 0 for row in range(rows))
    again = inside_dates.tied_again(zone, {name: list(cells) for name, cells in twin.items()}, rows, 7)
    assert again == moved


def test_the_columns_a_gap_places_are_dealt_again_on_the_twin_s_gaps() -> None:
    """A two-level column after the chain that the gap places (a critical-care stay on the minutes) is a dependent of
    the tie: dealt again among its rows, its counts kept, it follows the twin's minutes again; a column another zone
    writes (`exclude`) is left as it stands (mutants: no dependent fitted; the dependent not dealt)."""
    table = _cases(4000, 3)
    zone, gathered, sources = _zone_and_sources(table)
    inside_dates.tie_chains(zone, gathered, inside_dates.tie_rows(4000), sources)
    dependents = zone["columns"]["close"]["chain"]["tie"]["dependents"]  # type: ignore[index]
    assert [entry["column"] for entry in dependents] == ["critical"]
    twin = _twin(table, 4)
    rows = len(table["service"])
    moved = inside_dates.tied_again(zone, {name: list(cells) for name, cells in twin.items()}, rows, 5)
    assert sorted(moved["critical"]) == sorted(twin["critical"])
    after = dict(twin)
    after["close"], after["critical"] = moved["close"], moved["critical"]

    def gap_by_stay(cells: "dict[str, list[str]]") -> float:
        stay = [_minutes(cells, row) for row in range(rows) if cells["critical"][row] == "Y"]
        rest = [_minutes(cells, row) for row in range(rows) if cells["critical"][row] == "N"]
        return _mean(stay) / _mean(rest)

    assert gap_by_stay(twin) < 1.1 < gap_by_stay(table)
    assert gap_by_stay(after) > 1.0 + 0.5 * (gap_by_stay(table) - 1.0), (gap_by_stay(after), gap_by_stay(table))
    kept = inside_dates.tied_again(zone, {name: list(cells) for name, cells in twin.items()}, rows, 5,
                                   exclude={"critical"})
    assert "critical" not in kept and "close" in kept


def test_a_gap_no_column_places_keeps_no_tie() -> None:
    """A chain whose gap no other column of its row moves holds no tie, and the twin's dates are not written again
    (mutant: the gate not read)."""
    table = _cases(3000, 5)
    draw = random.Random(11)
    draw.shuffle(table["emergency"])
    draw.shuffle(table["critical"])
    zone, gathered, sources = _zone_and_sources(table)
    inside_dates.tie_chains(zone, gathered, inside_dates.tie_rows(3000), sources)
    assert not inside_dates.tied(zone)
    assert inside_dates.tied_again(zone, {name: list(cells) for name, cells in table.items()}, 3000, 1) == {}


def _accounts(rows: int, seed: int) -> "dict[str, list[str]]":
    draw = random.Random(f"accounts-{seed}")
    out: "dict[str, list[str]]" = {"patient": [], "subscriber": [], "relationship": [], "staff": []}
    for _row in range(rows):
        patient = f"P{draw.randrange(1000000, 1900000)}"
        relation = draw.choices(("Self", "Spouse", "Child"), (0.6, 0.25, 0.15))[0]
        out["patient"] += [patient]
        out["relationship"] += [relation]
        out["subscriber"] += [patient if relation == "Self" else f"Q{draw.randrange(1000000, 1900000)}"]
        out["staff"] += [f"E{draw.randrange(10000, 10040)}"]
    return out


def test_a_record_number_equal_to_another_on_some_levels_is_held_in_the_twin() -> None:
    """The subscriber is the patient exactly where the relationship is `Self`: the identity is found by that label
    and no other, and the twin's subscriber is written as the twin's own (made-up) patient on those rows and on no
    other (mutants: the label's levels not read; the rule not held)."""
    table = _accounts(3000, 1)
    rules = inside_relations.identities_of({"patient": table["patient"], "subscriber": table["subscriber"],
                                            "staff": table["staff"]}, {"relationship": table["relationship"]})
    assert rules == [{"column": "subscriber", "equals": "patient", "by": "relationship", "levels": ["Self"]}]
    twin = {"patient": [f"X{row:09d}" for row in range(3000)], "subscriber": [f"Y{row:07d}" for row in range(3000)],
            "relationship": list(table["relationship"])}
    written = inside_relations.identities_held(rules, twin)
    assert list(written) == ["subscriber"]
    for row in range(3000):
        own = twin["relationship"][row] == "Self"
        assert (written["subscriber"][row] == twin["patient"][row]) is own
    assert all(cell[:1] in ("X", "Y") for cell in written["subscriber"])


def test_no_identity_where_two_numbers_meet_by_chance_only() -> None:
    """Two record-number columns that meet on a few rows no label parts are not an identity (mutant: any meeting
    taken)."""
    draw = random.Random(3)
    first = [f"P{draw.randrange(100000, 100030)}" for _row in range(3000)]
    second = [f"P{draw.randrange(100000, 100030)}" for _row in range(3000)]
    assert sum(1 for a, b in zip(first, second) if a == b) >= inside_relations.IDENTITY_LEAST_ROWS
    labels = {"relationship": [draw.choice(("Self", "Spouse")) for _row in range(3000)]}
    assert inside_relations.identities_of({"a": first, "b": second}, labels) == []


def test_a_random_effect_s_shape_is_read_at_its_own_shares() -> None:
    """The trajectories zone's random level and slope are drawn from a shape held at the shares (k + 1/2) / 101; read
    there, with the tails past its ends, a standard normal shape draws a variance of one (read as an even grid from 0
    to 1, as before lane STATS-B, it drew 0.93: every patient's level about 4 per cent short in spread, the clinic
    visits' intraclass correlation 0.745 against the real 0.758) (mutant: the even-grid reading)."""
    from synthtwin import chain_walk, inside_trajectories

    shape = [chain_walk.normal_score((k + 0.5) / inside_trajectories.SHAPE_GRID)
             for k in range(inside_trajectories.SHAPE_GRID)]
    draw = random.Random(17)
    values = [inside_trajectories._shaped(shape, draw.gauss(0.0, 1.0)) for _k in range(60000)]
    mean = _mean(values)
    variance = _mean([(value - mean) ** 2 for value in values])
    assert abs(mean) < 0.02 and 0.98 < variance < 1.03, (mean, variance)
    assert inside_trajectories._shaped(shape, 0.0) == shape[50]
    assert inside_trajectories._shaped(shape, -4.0) < shape[0] < shape[1]
    assert inside_trajectories._shaped(shape, 4.0) > shape[-1]


def test_the_accounts_twin_holds_its_identity_only_where_the_switch_is_on(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Through the commands on the battery's accounts table (the floors lowered in place for a quick run): the record
    holds the subscriber's identity with the patient on the `Self` rows whatever the switch; drawn with the switch on,
    every `Self` row's subscriber is its twin patient and no other row's is; off, as shipped, none is (mutant: the
    switch not read)."""
    import csv
    import io
    import pathlib

    import reliability_battery as B
    import reliability_tables as T
    from synthtwin import cli, inside, installation, parsing

    monkeypatch.setattr(parsing, "TABLE_ROW_FLOOR", 2000)
    monkeypatch.setattr(parsing, "TABLE_PEOPLE_FLOOR", 100)
    for switched in (False, True):
        folder = pathlib.Path(tmp_path, f"on-{switched}")
        places = inside.Places(pathlib.Path(folder, "installation", "synthtwin", "inside"), (), (),
                               installation.system_name(), ())
        monkeypatch.setattr(inside, "default_places", lambda: places)
        monkeypatch.setattr(cli, "_IDENTITIES_SHIPPED", switched)
        product = B.make_twins(folder, "T7", T.text("T7", 3000, 1), (0,), True)
        assert not product.errors, product.errors
        records = sorted(places.private.glob(f"*{inside.SUFFIX}"))
        assert len(records) == 1
        rules = inside.load_record(records[0])["zones"][inside_relations.IDENTITIES]["rules"]
        assert rules == [{"by": "relationship", "column": "subscriber_id", "equals": "patient_id", "levels": ["Self"]}]
        rows = list(csv.DictReader(io.StringIO(product.twins[0])))
        own = [row["subscriber_id"] == row["patient_id"] for row in rows if row["relationship"] == "Self"]
        other = [row["subscriber_id"] == row["patient_id"] for row in rows if row["relationship"] != "Self"]
        assert own and other and not any(other)
        assert all(own) if switched else not any(own)


def _confounded(rows: int, seed: int) -> "dict[str, list[str]]":
    """A treatment given to the older, which lowers the outcome's odds as age raises them: its patients' odds stand
    near the others', so against the intercept alone the treatment reads as nothing."""
    draw = random.Random(f"confounded-{seed}")
    out: "dict[str, list[str]]" = {"age": [], "treated": [], "outcome": []}
    for _row in range(rows):
        age = draw.gauss(60.0, 12.0)
        treated = draw.random() < 1.0 / (1.0 + math.exp(-0.12 * (age - 60.0)))
        eta = -1.0 + 0.06 * (age - 60.0) - 0.7 * treated
        outcome = draw.random() < 1.0 / (1.0 + math.exp(-eta))
        out["age"] += [f"{age:.1f}"]
        out["treated"] += ["Y" if treated else "N"]
        out["outcome"] += ["Y" if outcome else "N"]
    return out


def test_a_parent_the_others_mask_enters_the_fit() -> None:
    """The outcome's fit holds the treatment, whose relation only shows given the age (lane STATS-B: the screen against
    the intercept alone left it out); a column of no relation still enters no fit (mutant: no conditional pass)."""
    table = _confounded(6000, 1)
    exposed = [row for row in range(6000) if table["treated"][row] == "Y"]
    share_exposed = sum(1 for row in exposed if table["outcome"][row] == "Y") / len(exposed)
    share_others = sum(1 for row in range(6000) if table["treated"][row] == "N" and table["outcome"][row] == "Y") / (
        6000 - len(exposed))
    assert abs(share_exposed - share_others) < 0.02, (share_exposed, share_others)
    draw = random.Random(5)
    table["noise"] = [draw.choice(("A", "B")) for _row in range(6000)]
    rows = inside_relations.sample_rows(6000)
    specs = [inside_relations.ColumnSpec("age", 0, inside_relations.NUMBER, 0, (), ""),
             inside_relations.ColumnSpec("treated", 1, inside_relations.LABEL, 0, ("Y", "N"), ""),
             inside_relations.ColumnSpec("noise", 2, inside_relations.LABEL, 0, ("A", "B"), ""),
             inside_relations.ColumnSpec("outcome", 3, inside_relations.LABEL, 0, ("Y", "N"), "")]
    encoded = [inside_relations.encode(spec, table[spec.name], rows) for spec in specs]
    assert all(each is not None for each in encoded)
    zone = inside_relations.fit_zone([each for each in encoded if each is not None], len(rows), 6000)
    outcome = [entry for entry in zone["columns"] if entry["name"] == "outcome"][0]  # type: ignore[union-attr, index]
    parents = {term[1] for term in outcome["value"]["terms"] if isinstance(term, list) and len(term) > 1}
    assert "treated" in parents and "age" in parents, outcome["value"]["terms"]
    assert "noise" not in parents
