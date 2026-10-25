"""Layer L0 built: every eligible column meets its L0 band totals (lane BT, plan P4-D429; method G4.2a, G4.2b, G5.7, G7.3l, G7A.4d, G12.15).

THE GATE OF LANE BT. Stage 6's layer L0 is built behind the switch no
shipped command sets (`contract.load_profile(..., chain=True)`): every
description a shipped command loads is laid out byte for byte as
before. This file holds each rule beside a MUTANT of the product (a
product function replaced by monkeypatch, never an input changed), and
every mutant test runs the same check its rule's test runs and finds it
failing:

- EACH BAND MET EXACTLY at 20,000 rows on count, continuous, affixed,
  date and clock columns of the product's own twin, read back the way
  the profile reads them (`chain.read_column`), against the twin made
  without L0;
- THE LEAST MOVE on number columns (G5.7c): sparse codes and a dose column keep
  every value they hold at the floor's rows or more and write none the
  real column never held, inside the Kolmogorov-Smirnov distance of
  today's twin; its proven heaps, its count of different values, its
  mode, its keys written once a row, its values kept;
- the method's cases (G14.3a), the oracle's L0 cases
  (`tests/reference/generation-branch-vectors-28.json`);
- the date's edge runs and piece (G7.3l) and the clock's halves (G7A.4d);
- THE RESERVATION of records holding nothing, in a text file and in a
  workbook, by spelling and by class, its shortfall named, and every
  workbook cell written by the class G4.2b handed over;
- THE INTERFACE G16 calls (`cells_by_band`) and G16.5's givers.

Every table is invented here; the key is a fixed test key.
"""

import dataclasses
import datetime
import io
import json
import pathlib
import random
import zipfile

import pytest

import fixtures
import workbooks

from synthtwin import (
    calendar_clock,
    chain,
    chain_rules,
    contract,
    dialect,
    errors,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    sheetwriting,
    taxonomy,
)

FLOOR = 11
TEST_KEY = bytes(range(32))
SPELLED = {"code": False, "measurement": False, "decimal_comma": False}
ROWS = 20000


# -- the tables -------------------------------------------------------------------


def _write(folder: pathlib.Path, name: str, header: "list[str]", rows: "list[list[str]]") -> pathlib.Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    lines = [",".join(header)] + [",".join(row) for row in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return path


def _ward(rows: int) -> "tuple[list[str], list[list[str]]]":
    """An invented ward: a stay, a lab, a change, a dose in mg, a date with heavy days, a stamp, two clocks; some records hold nothing."""
    draw = random.Random(20261024)
    heavy = ["2022-01-01", "2023-07-04"]
    body: "list[list[str]]" = []
    for place in range(rows):
        if draw.random() < 0.005:
            body += [[""] * 10]
            continue
        u = draw.random()
        stay = 0 if u < 0.2 else 1 if u < 0.35 else min(int(draw.lognormvariate(1.3, 1.0)), 400)
        if draw.random() < 0.03:
            lab = "NA"
        elif draw.random() < 0.06:
            lab = "4.00"
        else:
            lab = f"{draw.lognormvariate(1.5, 0.5):.2f}"
        change = "0.0" if draw.random() < 0.1 else f"{draw.gauss(0, 3):.1f}"
        dose = draw.choice(["250 mg", "500 mg", "500 mg", f"{draw.randint(10, 99) * 10} mg"])
        v = draw.random()
        if v < 0.08:
            day = heavy[0]
        elif v < 0.12:
            day = heavy[1]
        else:
            day = datetime.date.fromordinal(738156 + draw.randint(0, 3 * 365)).isoformat()
        minutes = draw.randint(0, 1439)
        stamp = f"{day} {minutes // 60:02d}:{minutes % 60:02d}:00"
        w = draw.random()
        if w < 0.04:
            arrival = ""
        elif w < 0.14:
            arrival = "08:00"
        elif w < 0.2:
            arrival = "12:00"
        else:
            m = int(min(max(draw.gauss(14 * 60, 180), 0), 1439))
            arrival = f"{m // 60:02d}:{m % 60:02d}"
        s = int(min(max(draw.gauss(10 * 3600, 12000), 0), 86399))
        given = f"{s // 3600:02d}:{(s // 60) % 60:02d}:{s % 60:02d}"
        body += [[f"R{place:07d}", str(stay), lab, change, dose, day, stamp, arrival, given, draw.choice(["F", "M"])]]
    return ["record", "stay", "lab", "change", "dose", "admit_date", "stamp", "arrival", "given_at", "gender"], body


def _zipf(values: "tuple[str, ...]") -> "tuple[list[str], list[float]]":
    return [value for value in values], [1.0 / (rank + 1) for rank in range(len(values))]


def _codes(rows: int) -> "tuple[list[str], list[list[str]]]":
    """Invented codes drawn as a payer's files draw them, a dose on a few levels, a score in steps of five, and two keys."""
    draw = random.Random(17)
    drg = _zipf(("470", "291", "871", "392", "190", "065", "064", "189", "292", "872"))
    revenue = _zipf(("0450", "0250", "0300", "0320", "0360", "0636", "0730", "0120"))
    apc = _zipf(("5012", "5521", "5072", "5302", "5734", "5822", "5113"))
    classes = _zipf(("98", "49", "108", "127", "205", "106", "59", "651", "101", "53"))
    amounts = (["250", "500", "750", "1000", "1500", "2000"], [0.20, 0.35, 0.10, 0.25, 0.06, 0.04])
    serial = [str(1 + step) for step in range(rows)]
    draw.shuffle(serial)
    body: "list[list[str]]" = []
    for place in range(rows):
        barthel = 5 * min(20, max(0, int(round(draw.gauss(13, 4.5)))))
        body += [[
            f"CLM{200000000 + place}",
            serial[place],
            draw.choices(drg[0], drg[1])[0],
            draw.choices(revenue[0], revenue[1])[0],
            draw.choices(apc[0], apc[1])[0],
            draw.choices(classes[0], classes[1])[0],
            draw.choices(amounts[0], amounts[1])[0],
            str(barthel),
        ]]
    return ["claim", "serial", "drg", "revenue_code", "apc", "clinical_class", "dose_mg", "barthel"], body


def _ten(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """G5.7i's invented ten-column table (K-S6-02's), whose age holds its mode beside a cut at table seed 11."""
    draw = random.Random(seed)
    body: "list[list[str]]" = []
    for place in range(rows):
        age = draw.randint(1, 9) * 10 + draw.randint(0, 9)
        pressure = "" if draw.random() < 0.05 else f"{round(draw.gauss(120, 15), 1)}"
        stay = f"{round(draw.lognormvariate(1.2, 0.8), 2)}"
        few = min(int(draw.expovariate(0.6)), 12)
        visits = min(int(draw.gammavariate(2, 2)), 25)
        money = f"{round(draw.lognormvariate(5, 1), 2):.2f}"
        change = f"{round(draw.gauss(0, 2), 1)}"
        day = draw.randint(0, 364)
        visit = f"2023-{1 + day // 31 if day // 31 < 12 else 12:02d}-{1 + day % 28:02d}"
        if draw.random() < 0.15:
            clock = "08:00"
        else:
            minutes = int(min(max(draw.gauss(13 * 60, 150), 6 * 60), 22 * 60))
            clock = f"{minutes // 60:02d}:{minutes % 60:02d}"
        body += [[f"R{place:06d}", str(age), pressure, stay, str(few), str(visits), money, change, visit, clock, draw.choice(["F", "M"])]]
    return ["id", "age", "pressure", "stay", "few", "visits", "money", "change", "visit_date", "clock", "gender"], body


def _few_values() -> "tuple[list[str], list[list[str]]]":
    """G14.3a case 1 (b): a count of few values with one rare high value, 20,000 rows."""
    counts = [1568, 8436, 5813, 2464, 1018, 425, 162, 59, 30, 14, 7, 1, 2]
    cells: "list[str]" = []
    for value in range(len(counts)):
        cells += [str(value)] * counts[value]
    cells += ["16"]
    draw = random.Random(5)
    draw.shuffle(cells)
    return ["id", "count", "group"], [[f"R{place:06d}", cells[place], draw.choice(["a", "b"])] for place in range(len(cells))]


# -- the switched descriptions ------------------------------------------------------


@dataclasses.dataclass
class _Switched:
    table: reading.Table
    document: "dict[str, object]"
    statistical: "dict[str, object]"
    loaded: contract.Profile
    plain: contract.Profile
    settings: taxonomy.Settings
    folder: pathlib.Path
    twins: "dict[tuple[str, int], generation.Twin]"

    def twin(self, which: str, seed: int) -> generation.Twin:
        """The twin made with L0 (``"l0"``) or without it (``"bare"``) at ``seed``, made once."""
        if (which, seed) not in self.twins:
            self.twins[(which, seed)] = generation.generate_held(self.loaded if which == "l0" else self.plain, seed)
        return self.twins[(which, seed)]


def _switched(folder: pathlib.Path, path: pathlib.Path) -> _Switched:
    """The table described with the chain's switch, loaded behind it and, beside it, without it."""
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    document = profile.build_document(table, settings, [], [], [])
    chained = chain.describe(table, document, settings, chain.ChainSwitch(path.stem, TEST_KEY))
    assert chained.statistical is not None, chained.notes
    written = dict(document)
    relationships = dict(written["relationships"])  # type: ignore[call-overload]
    relationships["statistical"] = chained.statistical
    written["relationships"] = relationships
    on = fixtures.write_profile(folder, f"{path.stem}-switched.json", written)
    off = fixtures.write_profile(folder, f"{path.stem}-plain.json", document)
    return _Switched(
        table, document, chained.statistical, contract.load_profile(str(on), chain=True),
        contract.load_profile(str(off)), settings, folder, {},
    )


def _table(tmp_path_factory: pytest.TempPathFactory, name: str, made: "tuple[list[str], list[list[str]]]") -> _Switched:
    folder = tmp_path_factory.mktemp(name)
    return _switched(folder, _write(folder, f"{name}.csv", made[0], made[1]))


@pytest.fixture(scope="module")
def ward(tmp_path_factory: pytest.TempPathFactory) -> _Switched:
    return _table(tmp_path_factory, "ward", _ward(ROWS))


@pytest.fixture(scope="module")
def codes(tmp_path_factory: pytest.TempPathFactory) -> _Switched:
    return _table(tmp_path_factory, "codes", _codes(ROWS))


@pytest.fixture(scope="module")
def ten11(tmp_path_factory: pytest.TempPathFactory) -> _Switched:
    return _table(tmp_path_factory, "ten", _ten(ROWS, 11))


@pytest.fixture(scope="module")
def ten11_small(tmp_path_factory: pytest.TempPathFactory) -> _Switched:
    return _table(tmp_path_factory, "ten5000", _ten(5000, 11))


@pytest.fixture(scope="module")
def few(tmp_path_factory: pytest.TempPathFactory) -> _Switched:
    return _table(tmp_path_factory, "few", _few_values())


def _read_back(switched: _Switched, twin: generation.Twin) -> "dict[str, list[int]]":
    """Each eligible column's L0 totals in the twin, read the way the profile reads the table (contract 4.6b.2)."""
    out_path = switched.folder / "twin.csv"
    out_path.write_text("".join(rendering.twin_csv_pieces(twin)), encoding="utf-8", newline="")
    back = reading.read_table(str(out_path), small_cell_floor=FLOOR)
    blocks: "dict[str, tuple[int, dict[str, object]]]" = {}
    for place, block in enumerate(switched.document["columns"]):  # type: ignore[arg-type]
        blocks[f"{block['name']}"] = (place, block)
    blank = chain_rules.records_holding_nothing(switched.document)
    # The first `E` records holding nothing are no tabled row (contract
    # 4.6b.2), as `chain.describe` reads the real table.
    held = [reading.column_values(back, place) for place in range(len(back.column_names))]
    skipped: "set[int]" = set()
    for row in range(back.n_rows):
        if len(skipped) < blank and all(dialect.holds_nothing(column[row]) for column in held):
            skipped |= {row}
    held = []
    found: "dict[str, list[int]]" = {}
    for entry in switched.statistical["ladder"]:  # type: ignore[union-attr]
        place, block = blocks[entry["column"]]
        read = chain.read_column(back, place, block, switched.settings, SPELLED, "", blank)
        assert read is not None
        start = [0] * len(read.start.names)
        for row in range(back.n_rows):
            if row not in skipped:
                start[read.codes[row]] += 1
        totals: "list[int]" = []
        for band in entry["l0"]:
            names = [tuple(name) if isinstance(name, list) else name for name in band]
            totals += [sum(start[k] for k in range(len(read.start.names)) if read.start.names[k] in names)]
        found[entry["column"]] = totals
    out_path.unlink()
    return found


def _rows_off(found: "list[int]", published: "list[int]") -> int:
    return sum(abs(left - right) for left, right in zip(found, published)) // 2


def _published(switched: _Switched) -> "dict[str, list[int]]":
    return {entry["column"]: entry["totals"] for entry in switched.statistical["ladder"]}  # type: ignore[index, union-attr]


def _numbers(cells: "list[str] | tuple[str, ...]") -> "dict[float, int]":
    held: "dict[float, int]" = {}
    for cell in cells:
        value = parsing.parse_number(cell) if cell.strip() else None
        if value is not None:
            held[value] = held.get(value, 0) + 1
    return held


def _twin_numbers(switched: _Switched, twin: generation.Twin, name: str) -> "dict[float, int]":
    place = [column.name for column in switched.loaded.columns].index(name)
    return _numbers(generation.twin_column(twin, place))


def _real_numbers(switched: _Switched, name: str) -> "dict[float, int]":
    return _numbers(reading.column_values(switched.table, switched.table.column_names.index(name)))


def _ks(left: "dict[float, int]", right: "dict[float, int]") -> int:
    """The Kolmogorov-Smirnov distance between two columns of numbers, in rows."""
    worst = 0
    up = 0
    down = 0
    for value in sorted(set(left) | set(right)):
        up += left.get(value, 0)
        down += right.get(value, 0)
        worst = max(worst, abs(up - down))
    return worst


def _l0_notes(twin: generation.Twin) -> "list[str]":
    return [note.column for note in twin.deviations if note.fact == "band totals"]


def _bands_missed(switched: _Switched, twin: generation.Twin, names: "tuple[str, ...]") -> int:
    found = _read_back(switched, twin)
    published = _published(switched)
    return sum(_rows_off(found[name], published[name]) for name in names)


# -- EACH BAND MET EXACTLY AT 20,000 ROWS ----------------------------------------------

WARD_RANGED = ("stay", "lab", "change", "dose", "admit_date", "stamp", "arrival", "given_at")


def test_every_band_holds_its_published_count_at_twenty_thousand_rows(ward) -> None:
    published = _published(ward)
    roles = {column.name: column.statistical_type for column in ward.loaded.columns}
    twin = ward.twin("l0", 0)
    found = _read_back(ward, twin)
    checked = set()
    for name in WARD_RANGED:
        assert _rows_off(found[name], published[name]) == 0, (name, found[name], published[name])
        checked |= {roles[name]}
    # (an affixed column's cores are held to their bands by `codes`'s claim key)
    assert checked >= {"count", "continuous", "datetime", "time_of_day"}
    # ...every eligible column laid with its band totals, no rule B3.
    assert _l0_notes(twin) == []
    # The twin made without L0 misses them, which is why the layer exists.
    assert _bands_missed(ward, ward.twin("bare", 0), WARD_RANGED) > 0


def test_a_band_one_row_off_is_red(ward, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the first cut rank one row high."""
    built = generation._l0_ranks

    def shifted(cuts: contract.L0Cuts) -> "list[int]":
        ranks = built(cuts)
        return [ranks[0] + 1] + ranks[1:] if ranks else ranks

    monkeypatch.setattr(generation, "_l0_ranks", shifted)
    assert _bands_missed(ward, generation.generate_held(ward.loaded, 0), ("stay",)) >= 1


def test_red_without_the_least_move(ward, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: today's twin unmoved (G5.7c withdrawn): the number columns miss their bands."""
    monkeypatch.setattr(generation, "_l0_least_move", lambda column, facts, layout, values: (layout, values, []))
    assert _bands_missed(ward, generation.generate_held(ward.loaded, 0), ("stay", "lab", "change", "dose")) >= 1


def test_the_switch_off_is_todays_twin_byte_for_byte(ward) -> None:
    """K-S6-02 (i): a description whose ladder is empty generates as before."""
    stripped = dataclasses.replace(
        ward.loaded,
        relationships=dataclasses.replace(ward.loaded.relationships, ladder=(), families=0),
    )
    left = "".join(rendering.twin_csv_pieces(generation.generate_held(stripped, 3)))
    right = "".join(rendering.twin_csv_pieces(generation.generate_held(ward.plain, 3)))
    assert left == right


# -- THE LEAST MOVE ON NUMBER COLUMNS (G5.7c) ----------------------------------------------


SPARSE = ("drg", "revenue_code", "apc", "clinical_class", "dose_mg", "barthel")


def _sparse_kept(switched: _Switched, twin: generation.Twin, bare: generation.Twin, name: str) -> "list[str]":
    """Every way the twin's column falls short of the statistics skeptic's bar (lane BT, its item 1); empty where it meets it."""
    real = _real_numbers(switched, name)
    held = _twin_numbers(switched, twin, name)
    today = _twin_numbers(switched, bare, name)
    wrong: "list[str]" = []
    for value in real:
        if real[value] >= FLOOR and held.get(value, 0) == 0:
            wrong += [f"{name}: the real value {value} ({real[value]} rows) emptied"]
    for value in held:
        if value not in real and value not in today:
            wrong += [f"{name}: {value} written, which neither the real column nor today's twin holds"]
    if len(held) < len(today) or (len(today) == len(real) and len(held) != len(real)):
        wrong += [f"{name}: {len(held)} different values where today's twin holds {len(today)} and the real column {len(real)}"]
    bound = max(2 * _ks(today, real), (136 * ROWS) // 10000)
    if _ks(held, real) > bound:
        wrong += [f"{name}: Kolmogorov-Smirnov {_ks(held, real)} rows against a bound of {bound}"]
    return wrong


def _all_sparse_kept(switched: _Switched, twin: generation.Twin, bare: generation.Twin) -> "list[str]":
    wrong: "list[str]" = []
    for name in SPARSE:
        wrong += _sparse_kept(switched, twin, bare, name)
    return wrong


def test_sparse_codes_keep_their_values_and_write_none_made_up(codes) -> None:
    """The statistics skeptic's bar (lane BT, its item 1), on codes drawn as a payer's files draw them."""
    for seed in (0, 1):
        twin = codes.twin("l0", seed)
        assert _bands_missed(codes, twin, SPARSE) == 0
        assert _all_sparse_kept(codes, twin, codes.twin("bare", seed)) == []
        assert _l0_notes(twin) == []


def test_the_twin_is_never_further_from_the_real_column_than_today(codes, ward, few) -> None:
    """G5.7c's promise, measured on the gate's tables, where today's twin writes the real value beside each cut: no distance grows."""
    for switched in (codes, ward, few):
        roles = {column.name: column.statistical_type for column in switched.loaded.columns}
        for name in _published(switched):
            if roles[name] not in ("count", "continuous"):
                continue
            real = _real_numbers(switched, name)
            assert _ks(_twin_numbers(switched, switched.twin("l0", 0), name), real) <= _ks(
                _twin_numbers(switched, switched.twin("bare", 0), name), real
            ), name


def test_red_without_the_proven_heaps(codes, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: step 1 withdrawn. Today's twin writes the dose's commonest level on a few cells, and the band totals alone cannot bring it back."""
    monkeypatch.setattr(generation, "_l0_proven_heaps", lambda facts, cells: [])
    assert _all_sparse_kept(codes, generation.generate_held(codes.loaded, 0), codes.twin("bare", 0)) != []


def test_red_without_the_count_kept(codes, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: step 3's count rule withdrawn. A heap the move restores stands beside a value today's twin made up."""
    monkeypatch.setattr(generation, "_l0_counted", lambda entries, distinct, gaps: None)
    assert _all_sparse_kept(codes, generation.generate_held(codes.loaded, 0), codes.twin("bare", 0)) != []


def test_red_with_the_smallest_stratum_merged_in_place_of_the_nearest(codes, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the count rule merging the smallest stratum no heap proves wherever it stands, not between two heaps: a real score is dropped."""

    def smallest(entries: "generation._Entries", distinct: int, gaps: "list[tuple[float, float]]") -> None:
        found = generation._l0_held_count(entries)
        while found > distinct:
            order = [at for _value, at in sorted([(entries.values[at], at) for at in range(len(entries.values)) if entries.sizes[at] > 0])]
            best = -1
            partner = -1
            for place in range(1, len(order)):
                at = order[place]
                if entries.proven[at] or entries.pieces[order[place - 1]] != entries.pieces[at]:
                    continue
                if best < 0 or entries.sizes[at] < entries.sizes[best]:
                    best = at
                    partner = order[place - 1]
            if best < 0:
                return
            entries.sizes[partner] = entries.sizes[partner] + entries.sizes[best]
            entries.sizes[best] = 0
            found = found - 1

    monkeypatch.setattr(generation, "_l0_counted", smallest)
    assert _all_sparse_kept(codes, generation.generate_held(codes.loaded, 0), codes.twin("bare", 0)) != []


KEYS = ("serial", "claim")


def _keys_lost(switched: _Switched, twin: generation.Twin) -> int:
    lost = 0
    for name in KEYS:
        place = [column.name for column in switched.loaded.columns].index(name)
        lost += ROWS - len(set(generation.twin_column(twin, place)))
    return lost


def test_a_key_every_one_different_is_written_once_a_row(codes) -> None:
    """The first skeptic's MAJOR 4 and the statistics skeptic's MAJOR 2: no value of an all-different column lost at the floor's size."""
    for seed in (0, 1):
        twin = codes.twin("l0", seed)
        assert _bands_missed(codes, twin, KEYS) == 0
        assert _keys_lost(codes, twin) == 0


def test_red_with_a_key_written_twice(codes, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: step 2a withdrawn: the keys a cut hands one entry stand on its value twice."""
    monkeypatch.setattr(generation, "_l0_spread", lambda facts, walls, entries, held: None)
    assert _keys_lost(codes, generation.generate_held(codes.loaded, 0)) >= 1


def _mode_missed(switched: _Switched, twin: generation.Twin) -> "list[str]":
    facts = [column for column in switched.loaded.columns if column.name == "age"][0].facts
    assert isinstance(facts, contract.NumericFacts) and facts.mode is not None
    wrong = [note.fact for note in twin.deviations if note.column == "age" and note.fact in ("mode", "mode_count")]
    if _twin_numbers(switched, twin, "age").get(facts.mode, 0) != facts.mode_count:
        wrong += ["the mode's count"]
    return wrong


def test_the_mode_keeps_its_published_count(ten11) -> None:
    twin = ten11.twin("l0", 0)
    assert _mode_missed(ten11, twin) == []
    assert _bands_missed(ten11, twin, ("age",)) == 0


def test_red_without_the_mode_kept(ten11, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: step 4 withdrawn: the cut beside the mode moves cells onto it or off it, and the twin's report names the count."""
    monkeypatch.setattr(generation, "_l0_mode_kept", lambda facts, entries, today: None)
    assert _mode_missed(ten11, generation.generate_held(ten11.loaded, 0)) != []


def _values_lost(pairs: "list[tuple[_Switched, generation.Twin, tuple[str, ...]]]") -> int:
    lost = 0
    for switched, twin, names in pairs:
        for name in names:
            lost += max(0, len(_twin_numbers(switched, switched.twin("bare", 0), name)) - len(_twin_numbers(switched, twin, name)))
    return lost


MANY = ("pressure", "stay", "money", "change")


def test_a_value_the_cut_empties_keeps_a_cell(ten11) -> None:
    """Step 3: no value of today's twin is lost to the move on a continuous column of many values."""
    assert _values_lost([(ten11, ten11.twin("l0", 0), MANY)]) == 0


def test_red_without_the_values_kept(ten11, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: step 3's donor and free point withdrawn: a value whose every cell crossed a cut is lost."""
    monkeypatch.setattr(generation, "_l0_values_kept", lambda facts, walls, entries, held: None)
    assert _values_lost([(ten11, generation.generate_held(ten11.loaded, 0), MANY)]) >= 1


def _strata_of_change(switched: _Switched, seed: int, value: float, monkeypatch: pytest.MonkeyPatch) -> "tuple[int, int]":
    """How many strata of today's `change` hold ``value`` before the least move, and how many hold a cell of it after."""
    seen: "list[tuple[int, int]]" = []
    built = generation._l0_least_move

    def spy(column, facts, layout, values):  # type: ignore[no-untyped-def]
        moved = built(column, facts, layout, values)
        if column.name == "change":
            before = len([held for held in values if held == value])
            after = len([at for at in range(len(moved[1])) if moved[1][at] == value and moved[0].sizes[at] > 0])
            seen.append((before, after))
        return moved

    monkeypatch.setattr(generation, "_l0_least_move", spy)
    generation.generate_held(switched.loaded, seed)
    assert len(seen) == 1
    return seen[0]


def test_a_value_two_strata_hold_is_kept_once(ten11_small, monkeypatch: pytest.MonkeyPatch) -> None:
    """G5.7c step 3 keeps a VALUE: today's `change` at 5,000 rows holds 0.5 in two strata and the cut at 0.5 empties the first; the value keeps its cells in the second, so the first is given none back."""
    assert _strata_of_change(ten11_small, 1, 0.5, monkeypatch) == (2, 1)


def test_red_with_every_emptied_stratum_a_lost_value(ten11_small, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: every emptied stratum counted lost, the step as first built: the emptied 0.5 takes a cell back from a neighbour beside the 0.5 that kept its cells."""
    monkeypatch.setattr(
        generation,
        "_l0_lost_values",
        lambda entries: [at for at in range(len(entries.values)) if entries.sizes[at] <= 0 and entries.before[at] > 0],
    )
    assert _strata_of_change(ten11_small, 1, 0.5, monkeypatch) == (2, 2)


# -- G14.3a CASE 1: A COUNT OF FEW VALUES WITH ONE RARE HIGH VALUE ------------------------


def test_case_1_every_band_exact_and_the_ones_and_twos_the_real_ones(few) -> None:
    for seed in (0, 1):
        twin = few.twin("l0", seed)
        assert _bands_missed(few, twin, ("count",)) == 0
        held = _twin_numbers(few, twin, "count")
        assert (held[0.0], held[1.0], held[2.0]) == (1568, 8436, 5813)
        top = sum(held[value] for value in held if value >= 3)
        assert held[3.0] > 0.55 * top


def test_case_1_red_without_the_least_move(few, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: G5.7c withdrawn, which is today's twin: the count of few values misses its bands."""
    monkeypatch.setattr(generation, "_l0_least_move", lambda column, facts, layout, values: (layout, values, []))
    assert _bands_missed(few, generation.generate_held(few.loaded, 0), ("count",)) >= 1


# -- THE ORACLE'S CASES (tests/reference/generation-branch-vectors-28.json) ------------------

ORACLE_VECTORS = pathlib.Path(__file__).resolve().parent / "reference" / "generation-branch-vectors-28.json"


def _oracle_cases() -> "dict[str, dict[str, object]]":
    return json.loads(ORACLE_VECTORS.read_text(encoding="utf-8"))["cases"]


def _case_profile(tmp_path: pathlib.Path, name: str, case: "dict[str, object]") -> contract.Profile:
    """An oracle cell case's one-column description, loaded, with its one ladder entry behind the switch."""
    import test_generation_reference

    document = test_generation_reference._profile_document({"column": case["column"], "cells": [""] * int(f"{case['rows']}")}, name)
    document["settings"]["small_cell_floor"] = FLOOR  # type: ignore[index]
    plain = contract.load_profile(str(fixtures.write_profile(tmp_path, f"{name}.json", document)))
    bands: "list[tuple[object, ...]]" = []
    for band in case["bands"]:  # type: ignore[union-attr]
        bands += [tuple(tuple(start) if isinstance(start, list) else start for start in band)]
    entry = contract.LadderEntry(plain.columns[0].name, tuple(bands), tuple(case["totals"]))  # type: ignore[arg-type]
    return dataclasses.replace(plain, relationships=dataclasses.replace(plain.relationships, ladder=(entry,), families=1))


def _counted(cells: "tuple[str, ...]") -> "list[list[object]]":
    held: "dict[str, int]" = {}
    for cell in cells:
        held[cell] = held.get(cell, 0) + 1
    return [[cell, held[cell]] for cell in sorted(held)]


@pytest.mark.parametrize("name", sorted(_oracle_cases()))
def test_the_product_answers_every_oracle_case(name: str, tmp_path: pathlib.Path) -> None:
    case = _oracle_cases()[name]
    answer = case["answer"]
    rule = case["rule"]
    if rule == "cells":
        loaded = _case_profile(tmp_path, name, case)
        cells = tuple(generation.twin_column(generation.generate_held(loaded, int(f"{case['seed']}")), 0))
        assert _counted(cells) == answer["counts"], name  # type: ignore[index]
        if "cells" in answer:  # type: ignore[operator]
            assert list(cells) == answer["cells"], name  # type: ignore[index]
    elif rule == "halves":
        halves = calendar_clock._cut_halves(
            0, 35, case["count"], [tuple(item) for item in case["heaps"]], "hh-mm", 1, (60, 400),  # type: ignore[arg-type, union-attr]
            ((case["edge"], case["cut_rank"]),), case["laid"],  # type: ignore[arg-type]
        )
        assert halves is not None
        assert [count for _span, count, _heaps in halves] == answer["halves"]  # type: ignore[index]
    elif rule == "heaps":
        known = [(int(percent), float(rung)) for percent, rung in case["rungs"]]  # type: ignore[union-attr]
        spans = generation._l0_heap_spans(known, int(f"{case['cells']}"))
        assert [[value, first, last] for value, first, last in spans] == answer["heaps"]  # type: ignore[index]
    else:
        assert dialect.reserved_cells(list(case["cells"]), case["count"], case["workbook"]) == answer["reserved"]  # type: ignore[arg-type, call-overload]


def test_the_oracle_holds_the_ruled_minimum_of_cell_cases() -> None:
    """The orchestrator's ruling (a) of 2026-10-25: case 1 (a) and (b)'s count at each value, case 2's and case 7 (a)'s cells, frozen."""
    names = {name for name, case in _oracle_cases().items() if case["rule"] == "cells"}
    assert names >= {"l0_cells_case_1a", "l0_cells_case_1b", "l0_cells_case_2", "l0_cells_case_7a"}


# -- G7.3l: THE DATE'S EDGE RUNS AND ITS PIECE --------------------------------------------------


def test_case_7_a_the_gap_below_an_edge_run_ends_one_unit_short(ward) -> None:
    assert _bands_missed(ward, ward.twin("l0", 0), ("admit_date", "stamp")) == 0


def test_case_7_a_red_with_the_gap_reaching_the_edges_unit(ward, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the gap's upper place at the unit's middle and its ordinals up to the edge, which lets a rank below the cut draw the edge."""
    monkeypatch.setattr(
        generation, "_date_gap_top", lambda edge: (edge * generation._PIN_STEPS + generation._PIN_STEPS // 2, edge)
    )
    assert _bands_missed(ward, generation.generate_held(ward.loaded, 0), ("admit_date", "stamp")) >= 1


def _cut_dates(tmp_path: pathlib.Path) -> contract.DatetimeFacts:
    """Forty dates, their facts with one L0 edge at ordinal 110 and its cut rank 10."""
    rows = [[f"2024-0{1 + step // 28}-{1 + step % 28:02d}"] for step in range(40)]
    path = _write(tmp_path, "dates.csv", ["day"], rows)
    settings = taxonomy.Settings(small_cell_floor=1)
    document = profile.build_document(reading.read_table(str(path), small_cell_floor=1), settings, [], [], [])
    facts = contract.load_profile(str(fixtures.write_profile(tmp_path, "dates.json", document))).columns[0].facts
    assert isinstance(facts, contract.DatetimeFacts)
    return dataclasses.replace(facts, l0=contract.L0Cuts((110.0,), (10, 30), 40))


def _windows_crossing(facts: contract.DatetimeFacts) -> "list[str]":
    wrong: "list[str]" = []
    if generation._date_windows_cut(facts, 3, [(100, 130)]) != [(100, 109)]:
        wrong += ["a rank below the cut may be stepped onto the edge or after it"]
    if generation._date_windows_cut(facts, 12, [(100, 130)]) != [(110, 130)]:
        wrong += ["a rank at or after the cut may be stepped below the edge"]
    return wrong


def test_case_7_b_the_spelling_step_keeps_the_piece(tmp_path: pathlib.Path) -> None:
    """G7.5's step of a rank off an absent spelling looks only inside the rank's piece."""
    assert _windows_crossing(_cut_dates(tmp_path)) == []


def test_case_7_b_red_with_the_windows_uncut(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the search over the G12.4 window and `[earliest, latest]` uncut."""
    monkeypatch.setattr(generation, "_date_windows_cut", lambda facts, rank, windows: windows)
    assert _windows_crossing(_cut_dates(tmp_path)) != []


# -- G7A.4d: THE CLOCK'S HALVES AND KNOTS -----------------------------------------------------------


def _hour_halves() -> "list[int]":
    """G14.3a case 10 through the product's census layout: 11 low-tail rows, an hour's 100 cells cut by an edge at the cut rank 39."""
    blocks = calendar_clock.clock_body_blocks(122, (11, 11), (60, 400), ((0, 35, 100),), (), "hh-mm", 1, (), ((200, 39),))
    assert blocks is not None
    return [sum(block.cells for block in blocks if block.group == 0 and block.half == half) for half in (0, 1)]


def test_case_10_a_cut_group_counts_its_boundary_once() -> None:
    assert _hour_halves() == [28, 72]


def test_case_10_red_with_the_boundary_subtracted_on_its_own(monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the low boundary's row taken out a second time where the halves are counted, which leaves 38 cells below the edge."""
    built = calendar_clock._cut_halves

    def twice(first, last, count, mine, form, stride, body, cuts, cursor):  # type: ignore[no-untyped-def]
        return built(first, last, count, mine, form, stride, body, cuts, cursor + 1)

    monkeypatch.setattr(calendar_clock, "_cut_halves", twice)
    assert _hour_halves() != [28, 72]


def test_case_9_the_clock_knots_stand_at_the_cut_and_at_the_rung(tmp_path: pathlib.Path) -> None:
    draw = random.Random(9)
    cells = ["08:00"] * 40 + [f"{6 + step // 60:02d}:{step % 60:02d}" for step in draw.sample(range(0, 120), 100)]
    cells += [f"{9 + step // 60:02d}:{step % 60:02d}" for step in draw.sample(range(0, 600), 260)]
    path = _write(tmp_path, "clock.csv", ["at"], [[cell] for cell in cells])
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    document = profile.build_document(reading.read_table(str(path), small_cell_floor=FLOOR), settings, [], [], [])
    column = contract.load_profile(str(fixtures.write_profile(tmp_path, "clock.json", document))).columns[0]
    facts = column.facts
    assert isinstance(facts, contract.ClockFacts) and facts.low_tail is not None and facts.high_tail is not None
    median = facts.clock_percentiles["p50"]
    assert median is not None
    edge = generation._clock_ordinal_of(median, facts.clock_form)
    parsed = column.n_present - facts.n_unparsed
    cut = contract.L0Cuts((float(edge),), (180, parsed - 180), parsed)
    knots = generation._clock_l0_knots(
        dataclasses.replace(facts, l0=cut), parsed, facts.low_tail.rows, parsed - 1 - facts.high_tail.rows,
        generation._clock_ordinal_of(facts.low_tail.boundary, facts.clock_form),
        generation._clock_ordinal_of(facts.high_tail.boundary, facts.clock_form),
    )
    scale = generation._WORD_SCALE
    assert (18000 * scale, edge) in knots
    assert any(position == 20000 * scale for position, _value in knots)


# -- THE RESERVATION: A TEXT FILE -------------------------------------------------------------------


def _reserved_table(folder: pathlib.Path, spelled: "list[tuple[str, int]]", ladder: str = "y") -> contract.Profile:
    """120 rows, twelve interior records holding nothing, three columns; ``spelled`` adds absent spellings to x."""
    draw = random.Random(11)
    rows: "list[list[str]]" = []
    places = set(range(5, 120, 10))
    extra: "list[str]" = []
    for spelling, count in spelled:
        extra += [spelling] * count
    at = 0
    for row in range(120):
        if row in places:
            rows += [["", "", ""]]
            continue
        x = extra[at] if at < len(extra) else f"{draw.randint(1, 50)}"
        at = at + 1
        y = "  " if row in (3, 5, 7, 13, 17) else draw.choice(["a", "b", "c"])
        rows += [[x, y, f"{draw.randint(0, 9)}"]]
    path = _write(folder, "reserved.csv", ["x", "y", "z"], rows)
    settings = taxonomy.Settings(small_cell_floor=1)
    document = profile.build_document(reading.read_table(str(path), small_cell_floor=1), settings, [], [], [])
    plain = contract.load_profile(str(fixtures.write_profile(folder, "reserved.json", document)))
    entry = contract.LadderEntry(ladder, ((("a",),), (("b",),), (("c",),)), (0, 0, 0))
    return dataclasses.replace(
        plain, relationships=dataclasses.replace(plain.relationships, ladder=(entry,), families=1)
    )


def _targets(loaded: contract.Profile) -> "list[int]":
    return [row for row, flag in enumerate(dialect._empty_targets(loaded.source.dialect, loaded.n_rows)) if flag]


def _reserved_by_spelling(loaded: contract.Profile) -> "list[str]":
    twin = generation.generate_held(loaded, 0)
    columns = [generation.twin_column(twin, place) for place in range(3)]
    wrong: "list[str]" = []
    for row in _targets(loaded):
        if not all(dialect.holds_nothing(columns[place][row]) for place in range(3)):
            wrong += [f"row {row} holds something"]
    if [columns[1][row] for row in _targets(loaded)] != [""] * 12:
        wrong += ["y's reserved cells are not its twelve empty ones"]
    return wrong


def test_case_11_the_reserved_rows_take_the_empty_cells_by_spelling(tmp_path: pathlib.Path) -> None:
    loaded = _reserved_table(tmp_path, [("NA", 12)])
    assert len(_targets(loaded)) == 12
    assert _reserved_by_spelling(loaded) == []


def test_case_11_red_with_absent_cells_reserved_whatever_their_spelling(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the absent cells reserved in G4.2's order, NA among them."""
    loaded = _reserved_table(tmp_path, [("NA", 12)])

    def any_absent(cells: "list[str]", count: int, workbook: bool, order: "list[int] | None" = None) -> "list[int]":
        rows = len(order) if order is not None else len(cells)
        return [row for row in range(rows) if (cells[order[row]] if order is not None else cells[row]) in ("", "NA")][:count]

    monkeypatch.setattr(dialect, "reserved_cells", any_absent)
    assert _reserved_by_spelling(loaded) != []


def _moved_after_placement(loaded: contract.Profile, monkeypatch: pytest.MonkeyPatch, place: int) -> bool:
    """Whether a cell of column ``place`` moved after the placement hook placed it."""
    placed: "dict[int, list[str]]" = {}
    built = generation._row_placement

    def hooked(step, profile_, content, drawn, finished, reserved=None, readings=None):  # type: ignore[no-untyped-def]
        order = built(step, profile_, content, drawn, finished, reserved, readings)
        placed[step] = [content[order[row]] for row in range(len(order))]
        return order

    monkeypatch.setattr(generation, "_row_placement", hooked)
    twin = generation.generate_held(loaded, 0)
    monkeypatch.setattr(generation, "_row_placement", built)
    return list(generation.twin_column(twin, place)) != placed[place]


def test_case_11_no_cell_of_an_eligible_column_moves_after_the_placement(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert not _moved_after_placement(_reserved_table(tmp_path, [("NA", 12)]), monkeypatch, 1)


def test_case_11_red_with_the_old_single_cell_exchange(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the reservation withdrawn in the product: today's first walk exchanges single cells into the records after the placement."""
    loaded = _reserved_table(tmp_path, [("NA", 12)])
    monkeypatch.setattr(generation, "_reservation", lambda profile_, plans, arranging: None)
    assert _moved_after_placement(loaded, monkeypatch, 1)


def _short_table(folder: pathlib.Path) -> contract.Profile:
    """Case 11 (b), a hand-written description: x publishes eleven empty cells beside thirteen `NA`, so `E_eff` is 11 of `E` = 12."""
    _reserved_table(folder, [("NA", 12)])
    document = json.loads((folder / "reserved.json").read_text(encoding="utf-8"))
    block = document["columns"][0]
    block["missing_by_source"] = {"NA": 13}
    block["missing_by_class"]["(blank)"] = 11
    block["missing_by_class"]["(text-code)"] = 13
    block["n_missing_blank"] = 11
    plain = contract.load_profile(str(fixtures.write_profile(folder, "short.json", document)))
    entry = contract.LadderEntry("y", ((("a",),), (("b",),), (("c",),)), (0, 0, 0))
    return dataclasses.replace(plain, relationships=dataclasses.replace(plain.relationships, ladder=(entry,), families=1))


def _short_kept(shorter: contract.Profile, monkeypatch: pytest.MonkeyPatch) -> "list[str]":
    seen: "list[generation.BandCells]" = []
    built = generation._row_placement

    def hooked(step, profile_, content, drawn, finished, reserved=None, readings=None):  # type: ignore[no-untyped-def]
        found = generation.cells_by_band(profile_, step, content, drawn, reserved, readings)
        if found is not None:
            seen.append(found)
        return built(step, profile_, content, drawn, finished, reserved, readings)

    monkeypatch.setattr(generation, "_row_placement", hooked)
    wrong: "list[str]" = []
    try:
        twin = generation.generate_held(shorter, 0)
    except errors.ProfileError as refused:
        return [f"refused: {refused}"]
    finally:
        monkeypatch.setattr(generation, "_row_placement", built)
    named = [note for note in twin.deviations if note.fact == "empty_rows"]
    if len(named) != 1 or not named[0].achieved.startswith(f"{len(_targets(shorter)) - 1} "):
        wrong += ["the shortfall is not named"]
    if not seen or sum(len(group) for group in seen[0].groups) != shorter.n_rows - len(_targets(shorter)) + 1:
        wrong += ["the arranged rows are not the rows left outside the reserved ones"]
    return wrong


def test_case_11_b_one_target_short_and_the_shortfall_named(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`E_eff = E - 1`: the first targets in row order reserved, the last arranged, the twin's report naming the shortfall."""
    assert _short_kept(_short_table(tmp_path), monkeypatch) == []


def test_case_11_b_red_with_every_target_reserved(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: all `E` targets reserved instead of `E_eff`: a column short of cells holding nothing cannot fill them."""
    shorter = _short_table(tmp_path)
    built = generation._reservation

    def every(profile_, plans, arranging):  # type: ignore[no-untyped-def]
        rows, workbook, givers, short = built(profile_, plans, arranging)
        return tuple(row for row, flag in enumerate(arranging.targets) if flag), workbook, givers, short

    monkeypatch.setattr(generation, "_reservation", every)
    assert _short_kept(shorter, monkeypatch) != []


def test_red_with_the_silent_fallback_to_the_drawn_arrangement(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The first skeptic's item 10: a column short of its reserved cells is refused, never placed as drawn. MUTANT: one cell short."""
    loaded = _reserved_table(tmp_path, [("NA", 12)])
    built = dialect.reserved_cells
    monkeypatch.setattr(dialect, "reserved_cells", lambda cells, count, workbook, order=None: built(cells, count, workbook, order)[:-1])
    with pytest.raises(errors.ProfileError):
        generation.generate_held(loaded, 0)


def _stray_table(folder: pathlib.Path) -> contract.Profile:
    """120 rows, twelve records holding nothing, three columns half empty: arranged rows can hold nothing in every column."""
    draw = random.Random(4)
    rows: "list[list[str]]" = []
    places = set(range(5, 120, 10))
    for row in range(120):
        if row in places:
            rows += [["", "", ""]]
            continue
        rows += [[
            draw.choice(["a", "b", ""]),
            "" if draw.random() < 0.5 else f"{draw.randint(1, 9)}",
            "" if draw.random() < 0.5 else draw.choice(["u", "v"]),
        ]]
    path = _write(folder, "stray.csv", ["x", "y", "z"], rows)
    settings = taxonomy.Settings(small_cell_floor=1)
    document = profile.build_document(reading.read_table(str(path), small_cell_floor=1), settings, [], [], [])
    plain = contract.load_profile(str(fixtures.write_profile(folder, "stray.json", document)))
    entry = contract.LadderEntry("x", ((("a",),), (("b",),)), (0, 0))
    return dataclasses.replace(plain, relationships=dataclasses.replace(plain.relationships, ladder=(entry,), families=1))


def test_g16_5_the_second_walk_takes_no_cell_of_an_eligible_column(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert not _moved_after_placement(_stray_table(tmp_path), monkeypatch, 0)


def test_g16_5_red_with_every_column_a_giver(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the second walk's givers unrestricted (the first skeptic's M24): the eligible column gives a cell to a stray row."""
    loaded = _stray_table(tmp_path)
    built = generation._reservation

    def every_giver(profile_, plans, arranging):  # type: ignore[no-untyped-def]
        rows, workbook, givers, short = built(profile_, plans, arranging)
        return rows, workbook, tuple(True for _giver in givers), short

    monkeypatch.setattr(generation, "_reservation", every_giver)
    assert _moved_after_placement(loaded, monkeypatch, 0)


# -- THE RESERVATION: A WORKBOOK -------------------------------------------------------------------------


def _book(folder: pathlib.Path, kind: str) -> pathlib.Path:
    """A 120-row workbook of three columns with twelve records holding nothing.

    ``plain``: every record holding nothing is formatted blank cells.
    ``withheld``: column C's twelve are 5 absent and 7 blank cells (each
    under the floor of 11) beside 20 empty strings in other rows, so its
    census publishes `empty` 20 and withholds the two others (G14.3a case
    12 (b)). ``mixed``: column C holds, beside them, 20 formatted blank
    cells and 20 empty strings in other rows (G14.3a case 13 (b)).
    """
    strings = ["a", "b", "c", "x", "y", "z", ""]
    letters = "ABC"
    draw = random.Random(13)
    places = sorted(set(range(5, 115, 9)))[:12]
    others = [row for row in range(30, 120) if row not in places]
    empties = set(others[:20]) if kind in ("withheld", "mixed") else set()
    blanks = set(others[20:40]) if kind == "mixed" else set()
    body = [(1, [workbooks.cell(f"{letters[k]}1", str(k), "s") for k in range(3)])]
    for row in range(120):
        number = row + 2
        if row in places:
            row_cells = [workbooks.cell(f"{letters[k]}{number}", "", "", workbooks.HEADER_STYLE) for k in range(2)]
            if kind != "withheld" or places.index(row) >= 5:
                row_cells += [workbooks.cell(f"C{number}", "", "", workbooks.HEADER_STYLE)]
            body += [(number, row_cells)]
            continue
        if row in empties:
            third = workbooks.cell(f"C{number}", "6", "s")
        elif row in blanks:
            third = workbooks.cell(f"C{number}", "", "", workbooks.HEADER_STYLE)
        else:
            third = workbooks.cell(f"C{number}", str(3 + draw.randint(0, 2)), "s")
        body += [(number, [
            workbooks.cell(f"A{number}", f"{draw.randint(1, 90)}"),
            workbooks.cell(f"B{number}", f"{round(draw.gauss(100, 10), 1)}"),
            third,
        ])]
    data = workbooks.package([
        ("[Content_Types].xml", workbooks._content_types(1, True, False, False)),
        ("_rels/.rels", workbooks._root_rels()),
        ("xl/workbook.xml", workbooks._workbook([("Data", "")])),
        ("xl/_rels/workbook.xml.rels", workbooks._workbook_rels(1, True)),
        ("xl/styles.xml", workbooks._styles()),
        ("xl/sharedStrings.xml", workbooks._shared_strings(strings)),
        ("xl/worksheets/sheet1.xml", workbooks.sheet(body, dimension="A1:C121")),
    ])
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"book-{kind}.xlsx"
    path.write_bytes(data)
    return path


def _book_profile(folder: pathlib.Path, kind: str = "plain", floor: int = 1) -> contract.Profile:
    path = _book(folder, kind)
    settings = taxonomy.Settings(small_cell_floor=floor)
    document = profile.build_document(reading.read_table(str(path), small_cell_floor=floor), settings, [], [], [])
    plain = contract.load_profile(str(fixtures.write_profile(folder, f"book-{kind}.json", document)))
    entry = contract.LadderEntry("c", ((("x",),), (("y",),), (("z",),)), (0, 0, 0))
    return dataclasses.replace(
        plain, relationships=dataclasses.replace(plain.relationships, ladder=(entry,), families=1)
    )


def _book_members(loaded: contract.Profile, twin: generation.Twin) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, text in sheetwriting.workbook_members(loaded, twin):
            archive.writestr(name, text)
    return buffer.getvalue()


def _book_back(folder: pathlib.Path, loaded: contract.Profile, twin: generation.Twin, floor: int = 1) -> "dict[str, object]":
    out = folder / "twin.xlsx"
    out.write_bytes(_book_members(loaded, twin))
    back = reading.read_table(str(out), small_cell_floor=floor)
    workbook_block = profile.build_document(back, taxonomy.Settings(small_cell_floor=floor), [], [], [])["source"]["workbook"]  # type: ignore[index]
    assert isinstance(workbook_block, dict)
    return workbook_block


def test_case_12_a_reserved_blank_reads_back_blank(tmp_path: pathlib.Path) -> None:
    loaded = _book_profile(tmp_path)
    assert loaded.source.workbook is not None and loaded.source.workbook.empty_rows_inside == 12
    twin = generation.generate_held(loaded, 0)
    assert twin.reserved_rows == 12
    back = _book_back(tmp_path, loaded, twin)
    assert back["empty_rows_inside"] == 12
    for column in back["columns"]:  # type: ignore[attr-defined]
        assert (column["cell_classes"]["absent"], column["cell_classes"]["blank"]) == (0, 12)


def test_case_12_red_with_the_rows_written_with_no_cells(tmp_path: pathlib.Path) -> None:
    """MUTANT: today's writer -- step 6's exchanges, and a reserved row written with no cells."""
    loaded = _book_profile(tmp_path)
    twin = dataclasses.replace(generation.generate_held(loaded, 0), reserved_rows=-1)
    back = _book_back(tmp_path, loaded, twin)
    assert [column["cell_classes"]["blank"] for column in back["columns"]] != [12, 12, 12]  # type: ignore[attr-defined]


def _withheld_kept(tmp_path: pathlib.Path, loaded: contract.Profile) -> "list[str]":
    back = _book_back(tmp_path, loaded, generation.generate_held(loaded, 0), FLOOR)
    wrong: "list[str]" = []
    if back["empty_rows_inside"] != 12:
        wrong += [f"{back['empty_rows_inside']} records holding nothing read back"]
    if back["columns"][2]["cell_classes"]["empty"] != 20:  # type: ignore[index]
        wrong += ["the empty strings' count moved"]
    return wrong


def test_case_12_b_no_reserved_cell_is_an_empty_string(tmp_path: pathlib.Path) -> None:
    """Withheld `absent` and `blank` beside `empty` 20, through the product's writer: twelve records holding nothing read back."""
    loaded = _book_profile(tmp_path, "withheld", FLOOR)
    census = loaded.source.workbook.columns[2].cell_classes  # type: ignore[union-attr]
    assert (census["absent"], census["blank"], census["empty"]) == (None, None, 20)
    assert _withheld_kept(tmp_path, loaded) == []


def test_case_12_b_red_with_the_classes_dealt_in_row_order(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the writer's reserved dealing replaced by step 1 in row order alone (the first skeptic's M6)."""
    loaded = _book_profile(tmp_path, "withheld", FLOOR)
    monkeypatch.setattr(
        sheetwriting, "reserved_cell_classes", lambda census, cells, value_class, reserved: sheetwriting.cell_classes(census, cells, value_class)
    )
    assert _withheld_kept(tmp_path, loaded) != []


def _classes_moved(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, strip: bool) -> "list[str]":
    """Case 13 (b): G16 reverses the eligible column's arranged cells; every cell must be written by the class it was handed."""
    loaded = _book_profile(tmp_path, "mixed", FLOOR)
    handed: "dict[int, tuple[str, ...]]" = {}
    built = generation._row_placement

    def reversed_g16(step, profile_, content, drawn, finished, reserved=None, readings=None):  # type: ignore[no-untyped-def]
        order = built(step, profile_, content, drawn, finished, reserved, readings)
        found = generation.cells_by_band(profile_, step, content, drawn, reserved, readings)
        if found is None or reserved is None:
            return order
        kept = set(reserved[0])
        arranged = [row for row in range(len(order)) if row not in kept]
        moved = [place for place in order]
        for at in range(len(arranged)):
            moved[arranged[at]] = order[arranged[len(arranged) - 1 - at]]
        handed[step] = tuple(found.classes[moved[row]] for row in range(len(moved)))
        return moved

    monkeypatch.setattr(generation, "_row_placement", reversed_g16)
    twin = generation.generate_held(loaded, 0)
    monkeypatch.setattr(generation, "_row_placement", built)
    if strip:
        twin = dataclasses.replace(twin, sheet_dealt=())
    captured: "list[list[bytes]]" = []
    pieces = sheetwriting._sheet_pieces

    def spied(names, cells, classes, *rest):  # type: ignore[no-untyped-def]
        captured.append([bytes(column) for column in classes])
        return pieces(names, cells, classes, *rest)

    monkeypatch.setattr(sheetwriting, "_sheet_pieces", spied)
    _book_members(loaded, twin)
    monkeypatch.setattr(sheetwriting, "_sheet_pieces", pieces)
    wrong: "list[str]" = []
    if not handed:
        return ["the eligible column was not handed over"]
    written = sheetwriting._class_names(captured[0][2])
    moved = sum(1 for row in range(len(written)) if written[row] != handed[2][row])
    if moved:
        wrong += [f"{moved} cells written by another class than the one handed over"]
    return wrong


def test_case_13_b_every_workbook_cell_is_written_by_the_class_handed_over(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """G4.2a steps 1 and 7, G4.2b: G16 moving the arranged cells moves no class (the first skeptic's item 2)."""
    assert _classes_moved(tmp_path, monkeypatch, False) == []


def test_case_13_b_red_with_the_classes_dealt_again_after_the_arrangement(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the classes not carried (`Twin.sheet_dealt` empty): the writer deals them again in row order."""
    assert _classes_moved(tmp_path, monkeypatch, True) != []


# -- THE INTERFACE G16 CALLS ---------------------------------------------------------------------------


def test_case_13_the_interface_hands_over_every_arranged_cell_once(ward, monkeypatch: pytest.MonkeyPatch) -> None:
    seen: "list[tuple[str, generation.BandCells, int]]" = []
    built = generation._row_placement

    def hooked(step, profile_, content, drawn, finished, reserved=None, readings=None):  # type: ignore[no-untyped-def]
        found = generation.cells_by_band(profile_, step, content, drawn, reserved, readings)
        if found is not None:
            seen.append((found.column, found, len(content)))
        return built(step, profile_, content, drawn, finished, reserved, readings)

    monkeypatch.setattr(generation, "_row_placement", hooked)
    # The interface reads its own column's cuts alone (the first skeptic's item 11).
    monkeypatch.setattr(generation, "_l0_columns", _every_column_read)
    generation.generate_held(ward.loaded, 0)
    published = _published(ward)
    assert seen
    blank = chain_rules.records_holding_nothing(ward.document)
    for name, found, count in seen:
        flat = sorted(cell for group in found.groups for cell in group)
        assert flat == sorted(set(range(count)) - set(found.reserved)), name
        ranges = [found.sizes[place] for place in range(len(found.names)) if found.names[place] in ("range", "level")]
        held = [len(found.groups[place]) for place in range(len(found.names)) if found.names[place] in ("range", "level")]
        assert ranges == held, name
        assert sum(held) <= sum(published[name])
        order = {"range": 0, "level": 0, "missing": 1, "other": 2, "labels": 3}
        kinds = [order[kind] for kind in found.names]
        assert kinds == sorted(kinds)
        if found.names[0] == "level":
            for place in range(len(found.names)):
                if found.names[place] == "level":
                    assert len(set(found.readings[place])) == 1
        assert len(found.reserved) == blank


_PLANNED: "list[int]" = []


def _every_column_read(profile_: contract.Profile) -> "dict[str, tuple[contract.L0Cuts | None, str]]":
    """`_l0_columns` as the plan calls it once; a second call is the interface reading every column again."""
    _PLANNED.append(1)
    if len(_PLANNED) > 1:
        raise AssertionError("every column's cuts were read again (the first skeptic's item 11)")
    return _L0_COLUMNS(profile_)


_L0_COLUMNS = generation._l0_columns


def test_case_13_a_reserved_cell_stands_in_no_group(tmp_path: pathlib.Path) -> None:
    """The same-cells promise: every cell but the reserved ones handed over once."""
    loaded = _reserved_table(tmp_path, [("NA", 12)])
    content = [""] * 12 + ["a"] * 54 + ["b"] * 54
    drawn = list(range(120))
    rows = tuple(range(5, 120, 10))
    found = generation.cells_by_band(loaded, 1, content, drawn, (rows, False), None)
    assert found is not None
    flat = sorted(cell for group in found.groups for cell in group)
    assert len(found.reserved) == 12 and set(found.reserved).isdisjoint(flat)
    assert flat == sorted(set(range(120)) - set(found.reserved))


def test_a_cell_with_no_reading_is_in_other(tmp_path: pathlib.Path) -> None:
    """G4.2b: a present cell with no reading lies in `other`, never in a range band (the first skeptic's item 11)."""
    loaded = _reserved_table(tmp_path, [("NA", 12)], ladder="z")
    content = [f"{place % 10}" for place in range(108)] + [""] * 12
    readings: "list[float | None]" = [float(place % 10) for place in range(108)]
    readings[0] = None
    found = generation.cells_by_band(loaded, 2, content, list(range(120)), ((), False), readings)
    assert found is not None
    others = [found.groups[place] for place in range(len(found.names)) if found.names[place] == "other"]
    assert others and 0 in others[0]


# -- G14.3a CASES 14, 15 AND 17: THE PIECE GRID, THE WORD BUDGET, RULE B3 ----------------------------------


def _width_column(tmp_path: pathlib.Path, cells: "list[str]") -> "tuple[contract.ColumnBlock, contract.NumericFacts, contract.Profile]":
    shuffled = [cell for cell in cells]
    random.Random(3).shuffle(shuffled)
    path = _write(tmp_path, "widths.csv", ["reading"], [[cell] for cell in shuffled])
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    document = profile.build_document(reading.read_table(str(path), small_cell_floor=FLOOR), settings, [], [], [])
    loaded = contract.load_profile(str(fixtures.write_profile(tmp_path, "widths.json", document)))
    column = loaded.columns[0]
    assert isinstance(column.facts, contract.NumericFacts)
    return column, column.facts, loaded


def _case_14_band(tmp_path: pathlib.Path) -> "tuple[int, int]":
    """G14.3a case 14: the grid and the cells of the piece from `1.01` to `1.02` of a column on the grid of tenths."""
    cells: "list[str]" = []
    for tenth in range(1, 7):
        cells += [f"0.{tenth}"] * 100
    cells += ["1.01"] * 150 + ["1.02"] * 150 + ["2.0"] * 100
    column, facts, _loaded = _width_column(tmp_path, cells)
    assert generation._written_grid(column, facts) == 1
    cut = contract.L0Cuts((1.01, 1.02), (600, 150, 250), 1000)
    pieces = generation._l0_pieces(column, facts, cut, 1)
    band = [piece for piece in pieces if piece.low == 1.01][0]
    return band.figures, band.cells


def test_case_14_a_band_of_a_finer_width_is_read_on_its_own_grid(tmp_path: pathlib.Path) -> None:
    assert _case_14_band(tmp_path) == (2, 150)


def test_case_14_red_with_the_piece_grid_withdrawn(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: every piece on the column's grid alone: the band holds no tenth, so (P3) fails (figures -2) and the column is made without L0."""
    built = generation._l0_count

    def column_grid_only(facts, piece, figures, below, above, limit):  # type: ignore[no-untyped-def]
        return 0 if figures > 1 else built(facts, piece, figures, below, above, limit)

    monkeypatch.setattr(generation, "_l0_count", column_grid_only)
    assert _case_14_band(tmp_path) == (-2, 150)


def test_case_15_the_budget_is_the_columns_without_l0(tmp_path: pathlib.Path) -> None:
    cells = ["1.0"] * 800 + [f"{1 + step / 1000:.3f}" for step in range(1, 101)] + ["2.0"] * 100
    draw = random.Random(2)
    draw.shuffle(cells)
    rows = [[cells[place], f"{draw.randint(0, 99)}"] for place in range(len(cells))]
    path = _write(tmp_path, "budget.csv", ["first", "second"], rows)
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    document = profile.build_document(reading.read_table(str(path), small_cell_floor=FLOOR), settings, [], [], [])
    plain = contract.load_profile(str(fixtures.write_profile(tmp_path, "budget.json", document)))
    entry = contract.LadderEntry("first", (((None, "p10"), ("p10", "p90")), (("p90", None),)), (900, 100))
    loaded = dataclasses.replace(
        plain, relationships=dataclasses.replace(plain.relationships, ladder=(entry,), families=1)
    )
    assert generation.plan_generation(loaded).columns[0].content_words == generation.plan_generation(plain).columns[0].content_words == 100
    assert generation.twin_column(generation.generate_held(loaded, 4), 1) == generation.twin_column(generation.generate_held(plain, 4), 1)


def _case_17_cells() -> "list[str]":
    cells: "list[str]" = []
    for tenth in range(1, 11):
        cells += [f"{tenth / 10:.1f}"] * 20
    for figures in (2, 3, 4, 5):
        for step in range(1, 11):
            cells += [f"{1 + (step % 9 + 1) / 100:.{figures}f}"]
    for tenth in range(11, 21):
        cells += [f"{tenth / 10:.1f}"] * 16
    return cells


def _case_17_named(tmp_path: pathlib.Path) -> "list[str]":
    """Describe case 17's 400 cells, load them with a ladder whose middle band is the one of the 1.01-1.09 cells, and read the twin's notes."""
    _column, facts, loaded = _width_column(tmp_path, _case_17_cells())
    p50 = facts.percentiles.rungs[generation._ladder_key_place("p50", generation._LADDER_NAMES)]
    p60 = facts.percentiles_between[generation._ladder_key_place("p60", generation._FINER_NAMES)]
    if p50 is None or p60 is None or not 1.0 < p50 < p60 < 1.1:
        return [f"the band runs from {p50} to {p60}"]
    below = sum(1 for cell in _case_17_cells() if float(cell) < p50)
    inside = sum(1 for cell in _case_17_cells() if p50 <= float(cell) < p60)
    entry = contract.LadderEntry(
        "reading", (((None, "p50"),), (("p50", "p60"),), (("p60", None),)), (below, inside, len(_case_17_cells()) - below - inside)
    )
    switched = dataclasses.replace(loaded, relationships=dataclasses.replace(loaded.relationships, ladder=(entry,), families=1))
    try:
        twin = generation.generate_held(switched, 0)
    except errors.ProfileError as refused:
        return [f"refused: {refused}"]
    named = [note for note in twin.deviations if note.fact == "band totals"]
    if [note.column for note in named] != ["reading"] or "(P3)" not in named[0].note:
        return ["the column is not named as made without its band totals under (P3)"]
    return []


def test_case_17_a_band_written_only_at_unnamed_widths_is_made_without_l0(tmp_path: pathlib.Path) -> None:
    """(P3) fails on the band from the 50th to the 60th percentile, and the twin names rule B3 for the column."""
    assert _case_17_named(tmp_path) == []


def test_case_17_red_with_p3_passed_on_any_grid(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: (P3) passed whatever the band holds: the column is laid with a band no grid of it reaches."""
    monkeypatch.setattr(generation, "_l0_count", lambda facts, piece, figures, below, above, limit: limit)
    assert _case_17_named(tmp_path) != []
