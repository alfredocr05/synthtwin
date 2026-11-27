"""Gate file of lane STATS-C: a count and the time it was counted over, in the inside record's relations zone.

THE CLASS. The relations zone fits each column on the columns before it, so a count written before the time it was
counted over (a patient's admissions, then the days the patient was followed) was fitted without that time, and the
time on the count: on the battery's methods table the twin's admissions a year fell with the days followed and the
treatment's rate ratio came back short (-0.22 against a real -0.31). `inside_relations.exposures_first` reads a
number after a count as the count's observed time where the count grows as a power of it near one (a Poisson fit of
the count on the time's logarithm), and fits that time just before the count.

WHAT IT HOLDS, each clause red on its mutant (lane STATS-C's report):

* A count's observed time is fitted before it and the count is fitted on it; the zone's columns stand in that order,
  which the twin draws them in (mutant: `exposures_first` leaves the table's order).
* A number unrelated to the count, and one that moves with it only through a third column, keep their places
  (mutant: the power's bounds not read).
* The twin drawn from the zone keeps the treatment's rate ratio and the share with any admission over the time
  followed, and its rate a year near flat over it (mutant: the table's order, as before the lane).

Every table here is drawn by the standard library's `random` from a seed, at run time; nothing is committed.
"""

from __future__ import annotations

import math
import random
import types
import typing

from synthtwin import contract, inside_relations as R, twinstore


def _negbin(r: random.Random, mean: float, shape: float) -> int:
    lam = r.gammavariate(shape, mean / shape)
    k, p = 0, math.exp(-lam)
    u, total = r.random(), p
    while u > total and k < 1000:
        k += 1
        p *= lam / k
        total += p
    return k


def _rate_table(rows: int, seed: int) -> "dict[str, list[str]]":
    """Patients: an age, a treatment, a diabetes letter, admissions over their own days followed (written after)."""
    r = random.Random(f"rates-{seed}")
    out: "dict[str, list[str]]" = {"age": [], "treated": [], "diabetes": [], "admissions": [], "weight": [], "days": []}
    for _ in range(rows):
        age = int(min(90.0, max(18.0, r.gauss(62.0, 14.0))))
        treated = r.random() < 0.45
        diabetes = r.random() < 0.25
        days = r.randint(30, 730)
        rate = math.exp(-0.4 + 0.02 * (age - 62) + 0.5 * diabetes - 0.3 * treated)
        out["age"] += [f"{age}"]
        out["treated"] += ["Y" if treated else "N"]
        out["diabetes"] += ["Y" if diabetes else "N"]
        out["admissions"] += [f"{_negbin(r, rate * days / 365.0, 1.5)}"]
        # a weight that rises with age (and so moves with the admissions only through it), never their time
        out["weight"] += [f"{70.0 + 0.3 * (age - 62) + r.gauss(0.0, 12.0):.1f}"]
        out["days"] += [f"{days}"]
    return out


KINDS = {"age": R.NUMBER, "treated": R.LABEL, "diabetes": R.LABEL, "admissions": R.NUMBER, "weight": R.NUMBER,
         "days": R.NUMBER}


def _encoded(columns: "dict[str, list[str]]", kinds: "dict[str, str] | None" = None) -> "tuple[list[R.Encoded], list[int]]":
    kinds = KINDS if kinds is None else kinds
    names = list(columns)
    rows = len(columns[names[0]])
    sample = R.sample_rows(rows)
    encoded = []
    for place, name in enumerate(names):
        kind = kinds[name]
        spellings = tuple(sorted(set(columns[name]))) if kind == R.LABEL else ()
        spec = R.ColumnSpec(name, place, kind, 90 if name == "age" else 0, spellings, "")
        found = R.encode(spec, columns[name], sample, None)
        if found is not None:
            encoded.append(found)
    return encoded, sample


def _zone(columns: "dict[str, list[str]]") -> "dict[str, object]":
    encoded, sample = _encoded(columns)
    return R.fit_zone(encoded, len(sample), len(sample))


def _profile(columns: "dict[str, list[str]]") -> object:
    blocks = []
    for name, cells in columns.items():
        counts: "dict[str, int]" = {}
        for cell in cells:
            counts[cell] = counts.get(cell, 0) + 1
        levels = tuple(contract.LevelEntry(label, count, {label: count}, {}, 0) for label, count in counts.items())
        facts = contract.LabelFacts(levels, 0, 0, {}, contract.PooledNumbers(0, None))
        blocks.append(types.SimpleNamespace(name=name, facts=facts))
    return types.SimpleNamespace(n_rows=len(columns["age"]), columns=blocks)


def _twin(columns: "dict[str, list[str]]", seed: int) -> "dict[str, list[str]]":
    """The zone's twin, every column written with the real column's own cells shuffled on their own (the description's
    twin stands in as cells with no relation between columns, so every relation must come from the zone)."""
    zone = _zone(columns)
    shuffle = random.Random(f"strict-{seed}")
    strict: "dict[str, list[str]]" = {}
    for name, cells in columns.items():
        mixed = list(cells)
        shuffle.shuffle(mixed)
        strict[name] = mixed
    held = {name: twinstore.held_column(cells) for name, cells in strict.items()}
    drawn = R.draw_columns(zone, _profile(columns), held, seed)  # type: ignore[arg-type]
    return {name: twinstore.column_cells(column) for name, column in drawn.items()}


def _log_rate_ratio(columns: "dict[str, list[str]]") -> float:
    totals = {"Y": [0.0, 0.0], "N": [0.0, 0.0]}
    for treated, admissions, days in zip(columns["treated"], columns["admissions"], columns["days"]):
        totals[treated][0] += float(admissions)
        totals[treated][1] += float(days)
    return math.log((totals["Y"][0] / totals["Y"][1]) / (totals["N"][0] / totals["N"][1]))


def _by_fifth(columns: "dict[str, list[str]]") -> "tuple[list[float], list[float]]":
    """By fifth of the days followed: the admissions a year, and the share of patients with any admission."""
    pairs = sorted((float(days), float(admissions)) for days, admissions in zip(columns["days"], columns["admissions"]))
    fifth = len(pairs) // 5
    rates: "list[float]" = []
    shares: "list[float]" = []
    for k in range(5):
        part = pairs[k * fifth:(k + 1) * fifth]
        rates += [365.0 * sum(a for _d, a in part) / sum(d for d, _a in part)]
        shares += [sum(1 for _d, a in part if a > 0) / len(part)]
    return rates, shares


def test_a_count_s_observed_time_is_fitted_before_it_and_the_count_on_it() -> None:
    columns = _rate_table(6000, 1)
    zone = _zone(columns)
    order = [entry["name"] for entry in zone["columns"]]  # type: ignore[union-attr,index]
    assert order == ["age", "treated", "diabetes", "days", "admissions", "weight"], order
    value_terms = next(entry for entry in zone["columns"] if entry["name"] == "admissions")["value"]["terms"]  # type: ignore[union-attr,index]
    presence_terms = next(entry for entry in zone["columns"] if entry["name"] == "admissions")["presence"]["terms"]  # type: ignore[union-attr,index]
    assert ["z", "days"] in value_terms + presence_terms, (value_terms, presence_terms)
    encoded, _sample = _encoded(columns)
    places = {encoded[at].entry["name"]: at for at in range(len(encoded))}
    counts = R._counted(encoded[places["admissions"]])
    assert counts is not None
    power = R.exposure_power(counts, R._timed(encoded[places["days"]]))  # type: ignore[arg-type]
    assert power is not None and abs(power[0] - 1.0) < 0.15 and power[1] > 10.0, power


def test_a_number_unrelated_to_the_count_or_moving_with_it_through_a_third_keeps_its_place() -> None:
    columns = _rate_table(6000, 2)
    encoded, _sample = _encoded(columns)
    places = {encoded[at].entry["name"]: at for at in range(len(encoded))}
    counts = R._counted(encoded[places["admissions"]])
    weight = R._timed(encoded[places["weight"]])
    assert counts is not None and weight is not None
    read = R.exposure_power(counts, weight)
    # the weight moves with the admissions only through age: if it passes the first look its power is far from one
    assert read is None or not R.EXPOSURE_POWER[0] <= read[0] <= R.EXPOSURE_POWER[1], read
    # ...and with no time among the columns, the table's order stands, a marker the admissions grow with only through
    # age (a power of about a quarter, read far past the gate) among them
    del columns["days"]
    r = random.Random("marker")
    columns["marker"] = [f"{math.exp(1.0 + 0.08 * (float(age) - 62) + r.gauss(0.0, 0.1)):.3f}" for age in columns["age"]]
    encoded, _sample = _encoded(columns, {**KINDS, "marker": R.NUMBER})
    places = {encoded[at].entry["name"]: at for at in range(len(encoded))}
    marker = R.exposure_power(typing.cast("list[float | None]", R._counted(encoded[places["admissions"]])),
                              typing.cast(R._Time, R._timed(encoded[places["marker"]])))
    assert marker is not None and marker[1] > R.EXPOSURE_Z and not R.EXPOSURE_POWER[0] <= marker[0] <= R.EXPOSURE_POWER[1]
    assert [one.entry["name"] for one in R.exposures_first(encoded)] == [one.entry["name"] for one in encoded]


def test_the_twin_keeps_the_rate_ratio_and_the_share_with_any_count_over_the_time_followed() -> None:
    columns = _rate_table(8000, 3)
    real_ratio = _log_rate_ratio(columns)
    real_rates, real_shares = _by_fifth(columns)
    ratios: "list[float]" = []
    for seed in (5, 6):
        twin = _twin(columns, seed)
        ratios += [_log_rate_ratio(twin)]
        rates, shares = _by_fifth(twin)
        # the share with any admission on each fifth of the days followed, as the real table's
        assert max(abs(a - b) for a, b in zip(shares, real_shares)) < 0.05, (shares, real_shares)
        # the rate a year on the shortest-followed fifth against the middle fifth, near the real table's: the lane's
        # measured limit (the positive counts' sizes follow the days a little less than in proportion, 1.2 to 1.4
        # here against a real 0.9; the table's order gave about 1.7 against 1.0 on the battery's methods table)
        assert abs(rates[0] / rates[2] - real_rates[0] / real_rates[2]) < 0.55, (rates, real_rates)
    # the treatment's rate ratio over the two twins, within about two of the real table's standard errors here
    assert abs(sum(ratios) / len(ratios) - real_ratio) < 0.06, (ratios, real_ratio)


def test_two_readings_of_one_measure_keep_their_order() -> None:
    """An arterial and a cuff pressure (whole numbers, the cuff about the arterial's size) grow as the power one of
    each other, but a pressure takes no nought, so it is no count of events: the table's order stands (mutant: nought
    not required among a count's values)."""
    r = random.Random("readings")
    columns: "dict[str, list[str]]" = {"age": [], "arterial": [], "cuff": []}
    for _ in range(6000):
        age = int(min(90.0, max(18.0, r.gauss(62.0, 14.0))))
        arterial = int(round(r.gauss(128.0 + 0.4 * (age - 62), 16.0)))
        columns["age"] += [f"{age}"]
        columns["arterial"] += [f"{arterial}"]
        columns["cuff"] += [f"{int(round(arterial + 3.0 + 0.06 * (arterial - 128) + r.gauss(0.0, 6.0)))}"]
    names = list(columns)
    sample = R.sample_rows(6000)
    encoded = [R.encode(R.ColumnSpec(name, place, R.NUMBER, 90 if name == "age" else 0, (), ""), columns[name], sample,
                        None) for place, name in enumerate(names)]
    kept = [one for one in encoded if one is not None]
    places = {one.entry["name"]: at for at, one in enumerate(kept)}
    assert R._counted(kept[places["arterial"]]) is None
    assert [one.entry["name"] for one in R.exposures_first(kept)] == ["age", "arterial", "cuff"]
