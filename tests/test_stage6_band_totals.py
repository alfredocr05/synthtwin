"""Layer L0 built: every eligible column meets its L0 band totals (lane BT, plan P4-D429; method G4.2a, G4.2b, G5.7, G7.3l, G7A.4d, G12.15).

THE GATE OF LANE BT. Stage 6's layer L0 is built behind the switch no
shipped command sets (`contract.load_profile(..., chain=True)`): every
description a shipped command loads is laid out byte for byte as
before. This file holds each rule beside a MUTANT of the product (a
product function replaced by monkeypatch, never an input changed), and
every mutant test runs the same check its rule's test runs and finds it
failing.

ONE CASE PER WRITER AT 20,000 ROWS (the orchestrator's rule of
2026-10-26: a test file adds at most three minutes to the suite; lane
BT's second repair, after its verify, item 2): a text file and a
workbook, each holding count, continuous, date and clock columns, every
band met exactly, read back the way the profile reads them
(`chain.read_column`). Every other check of a twin at 20,000 rows or
more -- sparse codes, the Kolmogorov-Smirnov distance, every within-column
fact with and without L0, the keys, the mode, the values kept -- is
K-S6-02's, measured by `tools/measurements/kpi_band_totals.py` under
`kpi_run --slow`; and each mutant here stands on the smallest fixture on
which it goes red:

- THE LEAST MOVE on number columns (G5.7c), through the oracle's own
  cases (`tests/reference/generation-branch-vectors-28.json`): the
  proven heaps, the two-sided count rule (a sparse count short of today's
  count and over it), the values kept, the mode, today's twin unmoved;
  the keys once a row on a column of 5,000 different numbers;
- the date's edge runs and piece (G7.3l) and the clock's halves and
  knots (G7A.4d), an edge's rung at a boundary rank among them;
- the cells as written held inside their pieces (G5.7b, G5.7g);
- THE RESERVATION of records holding nothing, in a text file and in a
  workbook, by spelling and by class, its shortfall named; every
  workbook cell written by the class G4.2b handed over, after the sort
  too, held a byte a row;
- THE INTERFACE G16 calls (`cells_by_band`): one group per published
  band in the published order, the columns rule B3 makes, the cost of a
  column of many levels; and G16.5's givers;
- the searches a large or crowded column asks: the grid index near
  `1e30`, the free whole numbers of a piece.

Every table is invented here; the key is a fixed test key.
"""

import dataclasses
import datetime
import io
import json
import pathlib
import random
import time
import types
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
    grains,
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


def _ward(rows: int, span: int = 3 * 365) -> "tuple[list[str], list[list[str]]]":
    """An invented ward: a stay, a lab, a change, a dose in mg, a date with heavy days, a stamp, two clocks; some records hold nothing.

    Its days other than the two heavy ones fall over ``span + 1`` days
    from 2022-01-01. At 20,000 rows the gate's ward spreads them over
    551 days (to 2023-07-05), so each day holds the floor's rows and the
    date and the stamp keep the day the profile reads them at: over three
    years some days hold fewer, and lane PS2's floor counted in rows
    (plan P4-D433) publishes both columns at the month, where the date's
    edge runs (G7.3l, case 7 (a)) are never drawn (batch 4l's merge).
    """
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
            day = datetime.date.fromordinal(738156 + draw.randint(0, span)).isoformat()
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


def _ward_book(rows: int) -> bytes:
    """The ward's stay, lab, admission date, arrival and gender as a workbook: dates as day counts, clocks as day fractions, its records holding nothing formatted blank cells."""
    _header, body = _ward(rows)
    picked = [1, 2, 5, 7, 9]
    names = ["stay", "lab", "admit_date", "arrival", "gender"]
    strings = names + ["NA", "F", "M"]
    index_of = {text: place for place, text in enumerate(strings)}
    letters = "ABCDE"
    epoch = datetime.date(1899, 12, 30)
    sheet_rows = [(1, [workbooks.cell(f"{letters[k]}1", str(k), "s") for k in range(5)])]
    for place in range(len(body)):
        number = place + 2
        row = body[place]
        if not any(row):
            sheet_rows += [(number, [workbooks.cell(f"{letters[k]}{number}", "", "", workbooks.HEADER_STYLE) for k in range(5)])]
            continue
        cells: "list[str]" = []
        for k in range(5):
            text = row[picked[k]]
            reference = f"{letters[k]}{number}"
            if names[k] == "admit_date":
                cells += [workbooks.cell(reference, str((datetime.date.fromisoformat(text) - epoch).days), "", 1)]
            elif names[k] == "arrival":
                if text:
                    hours, minutes = text.split(":")
                    cells += [workbooks.cell(reference, repr((int(hours) * 60 + int(minutes)) / 1440), "", 3)]
            elif text in index_of:
                cells += [workbooks.cell(reference, str(index_of[text]), "s")]
            else:
                cells += [workbooks.cell(reference, text)]
        sheet_rows += [(number, cells)]
    return _package(strings, sheet_rows, f"A1:E{len(body) + 1}")


def _package(strings: "list[str]", sheet_rows: "list[tuple[int, list[str]]]", dimension: str) -> bytes:
    return workbooks.package([
        ("[Content_Types].xml", workbooks._content_types(1, True, False, False)),
        ("_rels/.rels", workbooks._root_rels()),
        ("xl/workbook.xml", workbooks._workbook([("Data", "")])),
        ("xl/_rels/workbook.xml.rels", workbooks._workbook_rels(1, True)),
        ("xl/styles.xml", workbooks._styles()),
        ("xl/sharedStrings.xml", workbooks._shared_strings(strings)),
        ("xl/worksheets/sheet1.xml", workbooks.sheet(sheet_rows, dimension=dimension)),
    ])


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


def _keys(rows: int) -> "tuple[list[str], list[list[str]]]":
    """A record number of ``rows`` different values, shuffled, beside a binary arm."""
    draw = random.Random(17)
    serial = [str(1 + step) for step in range(rows)]
    draw.shuffle(serial)
    return ["serial", "arm"], [[serial[at], draw.choice(["p", "q"])] for at in range(rows)]


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


def _l0_alone(loaded: contract.Profile) -> contract.Profile:
    """A switched description with its chain emptied: its ladder and its families' count kept, so layer L0 runs and G16 does not."""
    return dataclasses.replace(loaded, relationships=dataclasses.replace(loaded.relationships, chain=()))


def _switched(folder: pathlib.Path, path: pathlib.Path) -> _Switched:
    """The table described with the chain's switch, loaded behind it and, beside it, without it."""
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    document = profile.build_document(table, settings, [], [], [])
    chained = chain.describe(table, document, settings, chain.ChainSwitch(path.stem, TEST_KEY, rows_per_person=chain.ROWS_UNASKED))
    assert chained.statistical is not None, chained.notes
    written = dict(document)
    relationships = dict(written["relationships"])  # type: ignore[call-overload]
    relationships["statistical"] = chained.statistical
    written["relationships"] = relationships
    on = fixtures.write_profile(folder, f"{path.stem}-switched.json", written)
    off = fixtures.write_profile(folder, f"{path.stem}-plain.json", document)
    return _Switched(
        # LAYER L0 ALONE (lane CHb, plan P4-D435): the chain's walk would
        # move every eligible column's cells between rows after the layer;
        # this gate holds the layer, so it is loaded with its chain emptied,
        # and tests/test_stage6_chain_generate.py holds the walk on top of it.
        table, document, chained.statistical, _l0_alone(contract.load_profile(str(on), chain=True)),
        contract.load_profile(str(off)), settings, folder, {},
    )


def _table(tmp_path_factory: pytest.TempPathFactory, name: str, made: "tuple[list[str], list[list[str]]]") -> _Switched:
    folder = tmp_path_factory.mktemp(name)
    return _switched(folder, _write(folder, f"{name}.csv", made[0], made[1]))


@pytest.fixture(scope="module")
def ward(tmp_path_factory: pytest.TempPathFactory) -> _Switched:
    return _table(tmp_path_factory, "ward", _ward(ROWS, span=550))


@pytest.fixture(scope="module")
def ward_book(tmp_path_factory: pytest.TempPathFactory) -> _Switched:
    folder = tmp_path_factory.mktemp("ward-book")
    path = folder / "ward-book.xlsx"
    path.write_bytes(_ward_book(ROWS))
    return _switched(folder, path)


@pytest.fixture(scope="module")
def ward_small(tmp_path_factory: pytest.TempPathFactory) -> _Switched:
    return _table(tmp_path_factory, "ward2000", _ward(2000))


@pytest.fixture(scope="module")
def ten11_small(tmp_path_factory: pytest.TempPathFactory) -> _Switched:
    return _table(tmp_path_factory, "ten5000", _ten(5000, 11))


def _read_back(switched: _Switched, twin: generation.Twin) -> "dict[str, list[int]]":
    """Each eligible column's L0 totals in the twin, read the way the profile reads the table (contract 4.6b.2)."""
    if switched.loaded.source.workbook is not None:
        out_path = switched.folder / "twin.xlsx"
        out_path.write_bytes(_book_members(switched.loaded, twin))
    else:
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


def _l0_notes(twin: generation.Twin) -> "list[str]":
    return [note.column for note in twin.deviations if note.fact == "band totals"]


def _bands_missed(switched: _Switched, twin: generation.Twin, names: "tuple[str, ...]") -> int:
    found = _read_back(switched, twin)
    published = _published(switched)
    return sum(_rows_off(found[name], published[name]) for name in names)




# -- ONE CASE PER WRITER AT 20,000 ROWS ----------------------------------------------

WARD_RANGED = ("stay", "lab", "change", "dose", "admit_date", "stamp", "arrival", "given_at")
BOOK_RANGED = ("stay", "lab", "admit_date", "arrival")


def _every_band_met(switched: _Switched, names: "tuple[str, ...]") -> None:
    published = _published(switched)
    roles = {column.name: column.statistical_type for column in switched.loaded.columns}
    twin = switched.twin("l0", 0)
    found = _read_back(switched, twin)
    checked = set()
    for name in names:
        assert _rows_off(found[name], published[name]) == 0, (name, found[name], published[name])
        checked |= {roles[name]}
    assert checked >= {"count", "continuous", "datetime", "time_of_day"}
    # ...every eligible column laid with its band totals, no rule B3.
    assert _l0_notes(twin) == []


def test_every_band_holds_its_published_count_in_a_text_file_at_twenty_thousand_rows(ward) -> None:
    _every_band_met(ward, WARD_RANGED)


def test_every_band_holds_its_published_count_in_a_workbook_at_twenty_thousand_rows(ward_book) -> None:
    _every_band_met(ward_book, BOOK_RANGED)
    assert ward_book.twin("l0", 0).reserved_rows > 0


def test_case_7_a_red_with_the_gap_reaching_the_edges_unit(ward, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the gap's upper place at the unit's middle and its ordinals up to the edge, which lets a rank below the cut draw the edge: the date column is refused by its internal check or misses its bands."""
    # The mutant reaches G7.3l's edge runs only on dates read at the day:
    # a date column the floor counted in rows sends to the month (lane
    # PS2, plan P4-D433) carries a time grain and draws no edge run.
    grains = {f"{block['name']}": block.get("time_grain") for block in ward.document["columns"]}  # type: ignore[union-attr]
    assert grains["admit_date"] is None and grains["stamp"] is None, grains
    monkeypatch.setattr(
        generation, "_date_gap_top", lambda edge: (edge * generation._PIN_STEPS + generation._PIN_STEPS // 2, edge)
    )
    try:
        missed = _bands_missed(ward, generation.generate_held(ward.loaded, 0), ("admit_date", "stamp"))
    except errors.ProfileError as refused:
        assert "misses the count of one of its bands" in f"{refused}"
        return
    assert missed >= 1


def test_a_band_one_row_off_is_red(ward_small, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the first cut rank one row high: a band misses its count, and the generator refuses the column as an internal check."""
    built = generation._l0_ranks

    def shifted(cuts: contract.L0Cuts) -> "list[int]":
        ranks = built(cuts)
        return [ranks[0] + 1] + ranks[1:] if ranks else ranks

    assert _bands_missed(ward_small, ward_small.twin("l0", 0), WARD_RANGED) == 0
    monkeypatch.setattr(generation, "_l0_ranks", shifted)
    with pytest.raises(errors.ProfileError, match="misses the count of one of its bands"):
        generation.generate_held(ward_small.loaded, 0)


def test_the_switch_off_is_todays_twin_byte_for_byte(ward_small) -> None:
    """K-S6-02 (i): a description whose ladder is empty generates as before."""
    stripped = dataclasses.replace(
        ward_small.loaded,
        relationships=dataclasses.replace(ward_small.loaded.relationships, ladder=(), families=0),
    )
    left = "".join(rendering.twin_csv_pieces(generation.generate_held(stripped, 3)))
    right = "".join(rendering.twin_csv_pieces(generation.generate_held(ward_small.plain, 3)))
    assert left == right


# -- THE ORACLE'S CASES (tests/reference/generation-branch-vectors-28.json) ------------------

ORACLE_VECTORS = pathlib.Path(__file__).resolve().parent / "reference" / "generation-branch-vectors-28.json"
ORACLE_LATER = pathlib.Path(__file__).resolve().parent / "reference" / "generation-branch-vectors-31.json"


def _oracle_cases() -> "dict[str, dict[str, object]]":
    cases = json.loads(ORACLE_VECTORS.read_text(encoding="utf-8"))["cases"]
    cases.update(json.loads(ORACLE_LATER.read_text(encoding="utf-8"))["cases"])
    return cases


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
    elif rule == "moved":
        assert _moved(tmp_path, name, case) == answer, name
    elif rule == "room":
        loaded = _case_profile(tmp_path, name, case)
        laid = generation._l0_columns(loaded)[loaded.columns[0].name][0] is not None
        assert laid is answer["laid"] is False, name  # type: ignore[index]
    elif rule == "knots":
        column, facts = _case_9_column(tmp_path)
        cut = contract.L0Cuts((669.0,), (180, 220), 400)
        assert generation._clock_ordinal_of(facts.clock_percentiles["p50"], facts.clock_form) == 669  # type: ignore[arg-type]
        made = generation._clock_l0_knots(
            dataclasses.replace(facts, l0=cut), 400, case["low_rank"], case["high_rank"], case["low_at"], case["high_at"],  # type: ignore[arg-type]
        )
        assert [[str(position), value] for position, value in made] == answer["knots"], name  # type: ignore[index]
    elif rule == "book":
        census = {dialect.SHEET_CELL_ABSENT: case["absent"], dialect.SHEET_CELL_BLANK: case["blank"], dialect.SHEET_CELL_EMPTY: case["empty"]}
        cells = tuple(case["cells"])  # type: ignore[arg-type]
        classes = sheetwriting.reserved_cell_classes(census, cells, None, case["reserved"])  # type: ignore[arg-type]
        assert [[place, classes[place]] for place in range(len(cells)) if cells[place] == ""] == answer["classes"], name  # type: ignore[index]
    elif rule == "interface":
        found = _interface_case(tmp_path, case)
        by_name = {"missing": list(found.groups[found.names.index("missing")]), "other": list(found.groups[found.names.index("labels" if "labels" in found.names else "other")])}
        ranged = [list(found.groups[place]) for place in range(len(found.names)) if found.names[place] == "range"]
        assert ranged == answer["groups"] and by_name["missing"] == answer["missing"] and by_name["other"] == answer["other"], name  # type: ignore[index]
    elif rule == "mode":
        assert _mode_counts(case) == answer["counts"], name  # type: ignore[index]
    elif rule == "pooled":
        assert _pooled_written(tmp_path, case) == answer["written"], name  # type: ignore[index]
    elif rule == "windows":
        facts = _cut_dates(tmp_path)
        cut_windows = [generation._date_windows_cut(facts, rank, [tuple(window) for window in case["windows"]]) for rank in case["ranks"]]  # type: ignore[union-attr, misc]
        assert [[list(window) for window in windows] for windows in cut_windows] == answer["cut"], name  # type: ignore[index]
    else:
        assert dialect.reserved_cells(list(case["cells"]), case["count"], case["workbook"]) == answer["reserved"]  # type: ignore[arg-type, call-overload]


def _moved(tmp_path: pathlib.Path, name: str, case: "dict[str, object]") -> "dict[str, list[object]]":
    """The product's least move on an oracle case, from the strata its pipeline hands it, which must be the case's own."""
    seen: "dict[str, list[object]]" = {}
    built = generation._l0_least_move

    def spy(column, facts, layout, values, floor):  # type: ignore[no-untyped-def]
        today = case["today"]
        assert list(layout.sizes) == today["sizes"] and list(values) == today["values"], name  # type: ignore[index]
        moved = built(column, facts, layout, values, floor)
        kept = [at for at in range(len(moved[0].sizes)) if moved[0].sizes[at] > 0]
        seen.update(values=[moved[1][at] for at in kept], sizes=[moved[0].sizes[at] for at in kept], signs=[moved[0].bands[at] for at in kept])
        return moved

    generation._l0_least_move = spy  # type: ignore[assignment]
    try:
        generation.generate_held(_case_profile(tmp_path, name, case), int(f"{case['seed']}"))
    finally:
        generation._l0_least_move = built  # type: ignore[assignment]
    return seen


def _stamp_column(tmp_path: pathlib.Path) -> contract.ColumnBlock:
    """A column of stamps written with a space between date and time, described by the product, then pooled at the month (method G7.13)."""
    draw = random.Random(17)
    cells = [
        f"2024-{1 + draw.randrange(12):02d}-{1 + draw.randrange(28):02d} {draw.randrange(24):02d}:{draw.randrange(60):02d}:{draw.randrange(60):02d}"
        for _row in range(400)
    ]
    path = _write(tmp_path, "stamps.csv", ["at"], [[cell] for cell in cells])
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    document = profile.build_document(reading.read_table(str(path), small_cell_floor=FLOOR), settings, [], [], [])
    column = contract.load_profile(str(fixtures.write_profile(tmp_path, "stamps.json", document))).columns[0]
    assert isinstance(column.facts, contract.DatetimeFacts)
    grain = grains.Grain("month", grains.Reading(grains.STAMP, "iso-datetime"), column.n_present, ())
    return dataclasses.replace(column, time_grain=grain)


def _stamp_edges(column: contract.ColumnBlock, texts: "list[str]") -> "tuple[object, ...]":
    """`L0` edges in the value space the profile's reader compares a cell in, from their written text."""
    return tuple(generation._reader_reading(column.facts, text, False)[1] for text in texts)


def test_a_pooled_stamp_held_at_its_middle_leaves_wearing_the_columns_one_mark(tmp_path: pathlib.Path) -> None:
    """Codex's review of lane BT2, item 2: a bucket's start written with the internal `T`, drawn at the row's word below the `L0` cut that crosses its month, is written at the month's middle (the band G16 dealt it to), and leaves wearing the one mark the column publishes, a space, as every other cell does. MUTANT, the mark set before the middle is chosen (the first build): `2024-01-16T11:59:59`."""
    column = _stamp_column(tmp_path)
    joint = generation._grain_joint(column)
    assert joint == " "
    edges = _stamp_edges(column, ["2024-01-01 05:00:00"])
    assert generation._grain_written(column, "2024-01-01T00:00:00", 0, None, joint) == "2024-01-01 00:00:00"
    assert generation._grain_written(column, "2024-01-01T00:00:00", 0, edges, joint) == "2024-01-16 11:59:59"
    assert generation._grain_written(column, "2024-01-01T00:00:00", 0, edges, "") == "2024-01-16T11:59:59"


def _hole_reads(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> int:
    """How many times a pooled column's absent spellings are read while its 200 cells leave inside their grain, held in their bands."""
    column = _stamp_column(tmp_path)
    edges = _stamp_edges(column, ["2024-01-01 05:00:00"])
    reads = [0]
    built = generation._hole_spellings

    def counted(column_):  # type: ignore[no-untyped-def]
        reads[0] = reads[0] + 1
        return built(column_)

    monkeypatch.setattr(generation, "_hole_spellings", counted)
    # The column's count of different buckets is not this test's: its 200 cells leave as handed over.
    monkeypatch.setattr(generation, "_filled_to_the_count", lambda column_, cells_, holes_: cells_)
    cells = [f"2024-{1 + at % 12:02d}-01T00:00:00" for at in range(200)]
    left, _unwritten = generation._inside_the_grain(column, cells, [at * 7919 for at in range(200)], edges)
    assert len(left) == 200
    return reads[0]


def test_a_pooled_columns_absent_spellings_are_read_once_a_column(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's review of lane BT2, item 7: the absent spellings are read once a column as its cells leave, not once a cell (a million-row column of ten thousand spellings sorted the map ten billion times). MUTANT, read again for each cell's middle: 201 reads."""
    assert _hole_reads(tmp_path, monkeypatch) == 1


def test_the_band_reading_reads_a_pooled_columns_absent_spellings_once(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's review of lane BT2, item 7, its other path: the reader's bands of a pooled date made without its band totals (`_reader_l0_bands`) read the column's absent spellings once for 5,000 cells over two blocks. MUTANT H7, read again for each cell: 5,000 reads."""
    column = _stamp_column(tmp_path)
    loaded = dataclasses.replace(contract.load_profile(str(tmp_path / "stamps.json")), columns=(column,))
    entry = contract.LadderEntry(column.name, (((None, "p50"),), (("p50", None),)), (200, 200))
    reads = [0]
    built = generation._hole_spellings

    def counted(column_):  # type: ignore[no-untyped-def]
        reads[0] = reads[0] + 1
        return built(column_)

    monkeypatch.setattr(generation, "_hole_spellings", counted)
    cells = [f"2024-{1 + at % 12:02d}-01T00:00:00" for at in range(5000)]
    generation._reader_l0_bands(loaded, column, entry, cells, None)
    assert reads[0] == 1


def test_red_with_the_absent_spellings_read_for_each_cell(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: each cell's middle reads the column's absent spellings again."""
    built = generation._grain_written

    def again(column, cell, word, edges, joint):  # type: ignore[no-untyped-def]
        generation._grain_middle(column, cell, frozenset(generation._hole_spellings(column)))
        return built(column, cell, word, edges, joint)

    monkeypatch.setattr(generation, "_grain_written", again)
    assert _hole_reads(tmp_path, monkeypatch) == 201


def _mode_counts(case: "dict[str, object]") -> "list[list[int]]":
    """The product's step 4 (`_l0_mode_kept`) on each state of a mode case: one piece whose published lower cut is ``edge_low``."""
    found: "list[list[int]]" = []
    for state in case["states"]:  # type: ignore[attr-defined]
        count = len(state["values"])
        entries = generation._Entries(list(state["values"]), list(state["counts"]), list(range(count)), [0] * count, [0] * count, list(state["pieces"]))
        entries.ordered = count
        today = generation._Entries(list(state["values"]), list(state["today"]), list(range(count)), [0] * count, [], [])
        facts = types.SimpleNamespace(mode=case["mode"], mode_count=case["wanted"])
        walls = (types.SimpleNamespace(low=case["edge_low"], published_low=True, low_open=False, zero=False),)
        generation._l0_mode_kept(facts, walls, entries, today)  # type: ignore[arg-type]
        found += [list(entries.sizes)]
    return found


def _pooled_written(tmp_path: pathlib.Path, case: "dict[str, object]") -> "list[str]":
    """The product's writing of each cell of a pooled case (`_grain_written`), on a column of stamps described by the product."""
    column = _stamp_column(tmp_path)
    assert column.time_grain is not None
    assert column.time_grain.rung == case["rung"] and column.time_grain.reading.member == case["member"]
    assert generation._grain_joint(column) == case["joint"]
    edges = _stamp_edges(column, list(case["edges"]))  # type: ignore[call-overload]
    return [
        generation._grain_written(column, cell, int(word), edges, f"{case['joint']}")
        for cell, word in zip(case["cells"], case["words"])  # type: ignore[call-overload]
    ]


def test_red_with_the_modes_edge_neighbour_first(monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT G4 (lane BT2's skeptic 1, item 4; Codex's review, item 4): no stratum read as its piece's edge value, so the mode's cells over its count go to the edge value: the frozen case `l0_mode_edge_side` is red."""
    case = _oracle_cases()["l0_mode_edge_side"]
    monkeypatch.setattr(generation, "_l0_is_edge", lambda walls, entries, at: False)
    assert _mode_counts(case) != case["answer"]["counts"]  # type: ignore[index]


def test_red_with_the_pooled_draw_free_of_its_band(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT (Codex's review of lane BT2, item 4): every draw read in one band, so none is held at its month's middle: the frozen case `l0_pooled_in_band` is red."""
    case = _oracle_cases()["l0_pooled_in_band"]
    monkeypatch.setattr(generation, "_grain_band", lambda column, cell, edges: 0)
    assert _pooled_written(tmp_path, case) != case["answer"]["written"]  # type: ignore[index]


def _case_9_column(tmp_path: pathlib.Path) -> "tuple[contract.ColumnBlock, contract.ClockFacts]":
    """G14.3a case 9's clock column, described by the product."""
    draw = random.Random(9)
    cells = ["08:00"] * 40 + [f"{6 + step // 60:02d}:{step % 60:02d}" for step in draw.sample(range(0, 120), 100)]
    cells += [f"{9 + step // 60:02d}:{step % 60:02d}" for step in draw.sample(range(0, 600), 260)]
    path = _write(tmp_path, "clock.csv", ["at"], [[cell] for cell in cells])
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    document = profile.build_document(reading.read_table(str(path), small_cell_floor=FLOOR), settings, [], [], [])
    column = contract.load_profile(str(fixtures.write_profile(tmp_path, "clock.json", document))).columns[0]
    assert isinstance(column.facts, contract.ClockFacts) and column.facts.low_tail is not None and column.facts.high_tail is not None
    return column, column.facts


def _interface_case(tmp_path: pathlib.Path, case: "dict[str, object]") -> generation.BandCells:
    """The interface on case 13's cells, the column's cuts given as the oracle's."""
    readings: "list[float | None]" = list(case["readings"])  # type: ignore[call-overload]
    count = int(f"{case['count']}")
    rows = [[f"{reading_of:.1f}" if reading_of is not None else "low"] for reading_of in readings] + [[""]] * (count - len(readings))
    path = _write(tmp_path, "interface.csv", ["value", "pad"][:1], rows)
    settings = taxonomy.Settings(small_cell_floor=1)
    document = profile.build_document(reading.read_table(str(path), small_cell_floor=1), settings, [], [], [])
    loaded = contract.load_profile(str(fixtures.write_profile(tmp_path, "interface.json", document)))
    entry = contract.LadderEntry("value", (((None, "p10"),), (("p10", "p50"),), (("p50", None),)), (9, 11, 10))
    loaded = dataclasses.replace(loaded, relationships=dataclasses.replace(loaded.relationships, ladder=(entry,), families=1))
    column = dataclasses.replace(loaded.columns[0], n_present=len(readings), n_missing=count - len(readings))
    loaded = dataclasses.replace(loaded, columns=(column,))
    cut = contract.L0Cuts(tuple(case["edges"]), (9, 11, 10), 30)  # type: ignore[arg-type]
    real = generation._l0_entry_cut
    generation._l0_entry_cut = lambda column, entry, blank: (cut, "")  # type: ignore[assignment]
    try:
        content = [row[0] for row in rows]
        given = [value if value is not None else None for value in readings]
        return generation.cells_by_band(loaded, 0, content, list(range(count)), None, given)  # type: ignore[return-value]
    finally:
        generation._l0_entry_cut = real  # type: ignore[assignment]


def test_the_oracle_holds_the_ruled_minimum_of_cell_cases() -> None:
    """The orchestrator's ruling (a) of 2026-10-25, and lane BT's second repair: the count rule's two sides and the mode, frozen."""
    names = {name for name, case in _oracle_cases().items() if case["rule"] in ("cells", "moved")}
    assert names >= {
        "l0_cells_case_1a", "l0_cells_case_1b", "l0_cells_case_2", "l0_cells_case_7a",
        "l0_cells_count_short", "l0_cells_count_over", "l0_cells_mode_kept",
        "l0_cells_case_3", "l0_cells_case_4", "l0_cells_case_5", "l0_cells_case_8", "l0_cells_case_14", "l0_cells_case_15",
        "l0_cells_next_heap",
    }


# -- THE LEAST MOVE'S MUTANTS, ON THE ORACLE'S OWN CASES (G5.7c) ----------------------------------

_EDGE_KEPT = generation._l0_edge_kept


def _edge_kept_without_the_next_heap(entries, new, first, last, wall, proof, below=None):  # type: ignore[no-untyped-def]
    """MUTANT: step 2b with every heap but the edge value's own left unread."""
    kept = tuple(heap for heap in proof.heaps if heap[0] == wall.low)
    _EDGE_KEPT(entries, new, first, last, wall, dataclasses.replace(proof, heaps=kept), below)


LEAST_MUTANTS = {
    # step 1 withdrawn
    "heaps_off": ("_l0_proven_heaps", lambda facts, cells: []),
    # step 3's count rule below withdrawn: the one-sided rule the verify found
    "count_short_off": ("_l0_heap_lost", lambda facts, walls, entries, distinct, heaps: None),
    # step 3's count rule above withdrawn
    "count_over_off": ("_l0_counted", lambda facts, entries, distinct, gaps, floor: None),
    # step 3's first half withdrawn: a value the cut empties keeps no cell
    "values_kept_off": ("_l0_values_kept", lambda facts, walls, entries, held: None),
    # step 4 withdrawn
    "mode_off": ("_l0_mode_kept", lambda facts, walls, entries, today: None),
    # step 2b withdrawn: the edge value takes the crossing ranks
    "edge_off": ("_l0_edge_kept", lambda entries, new, first, last, wall, proof, below: None),
    # step 2b reading only the edge value's own heaps (Codex's review of lane BT2, item 1)
    "next_heap_off": ("_l0_edge_kept", _edge_kept_without_the_next_heap),
    # step 2a withdrawn: a stratum the band totals gave a second cell keeps it (lane BT2's skeptic 1, item 6)
    "spread_off": ("_l0_spread", lambda facts, walls, entries, held: None),
    # G5.7c withdrawn: today's twin unmoved
    "least_move_off": ("_l0_least_move", lambda column, facts, layout, values, floor: (layout, values, [])),
}

RED_ON = [
    ("heaps_off", "l0_cells_count_short"),
    ("count_short_off", "l0_cells_count_short"),
    ("count_over_off", "l0_cells_count_over"),
    ("values_kept_off", "l0_cells_count_short"),
    ("mode_off", "l0_cells_mode_kept"),
    ("edge_off", "l0_cells_mode_kept"),
    ("heaps_off", "l0_cells_case_3"),
    ("count_over_off", "l0_cells_case_4"),
    ("least_move_off", "l0_cells_case_1a"),
    ("next_heap_off", "l0_cells_next_heap"),
    ("spread_off", "l0_cells_case_5"),
]


@pytest.mark.parametrize("mutant, name", RED_ON)
def test_each_step_of_the_least_move_is_red_on_its_mutant(mutant: str, name: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    case = _oracle_cases()[name]
    loaded = _case_profile(tmp_path, name, case)
    function, replaced = LEAST_MUTANTS[mutant]
    monkeypatch.setattr(generation, function, replaced)
    if case["rule"] == "moved":
        assert _moved(tmp_path, name, case) != case["answer"]
        return
    cells = tuple(generation.twin_column(generation.generate_held(loaded, int(f"{case['seed']}")), 0))
    assert _counted(cells) != case["answer"]["counts"]  # type: ignore[index]


def _edge_step(
    today: "list[int]", now: "list[int]", cells: int, bounds: "tuple[int, int]", margin: int,
    below: "tuple[int, int] | None" = None, pinned: "frozenset[float]" = frozenset(),
    heaps: "tuple[tuple[float, int, int], ...]" = (),
) -> "list[int]":
    """G5.7c step 2b on one piece of values 10, 11, ... whose cut rank is 100 and whose rungs bound the edge's real count."""
    count = len(today)
    entries = generation._Entries([10.0 + at for at in range(count)], list(now), [at for at in range(count)], [0] * count, [0] * count, [0] * count)
    entries.today = list(today)
    wall = types.SimpleNamespace(low=10.0, first=100, cells=cells)
    rungs = ((100 + bounds[0] - 1, 100 + bounds[0], 10.0), (100 + bounds[1] - 1, 100 + bounds[1], 11.0))
    new = list(now)
    generation._l0_edge_kept(entries, new, 0, count - 1, wall, generation._EdgeProof(rungs, heaps, margin, pinned), below)  # type: ignore[arg-type]
    assert sum(new) == cells
    return new


def test_step_2b_the_edge_value_keeps_todays_count_beside_an_even_estimate() -> None:
    """The crossing cells go to the next value, on either side of today's count; every piece keeps its cells."""
    assert _edge_step([254, 200, 200, 200, 200], [281, 173, 200, 200, 200], 1054, (150, 400), 100) == [254, 200, 200, 200, 200]
    assert _edge_step([200, 200, 200, 200, 200], [163, 237, 200, 200, 200], 1000, (100, 300), 80) == [200, 200, 200, 200, 200]


def test_step_2b_the_edge_grows_no_further_than_the_next_values_heap() -> None:
    """Codex's review of lane BT2, item 1: the edge value grows toward today's count only up to the first rank a proven heap of the next value holds, and not at all where step 2's count already reaches it; a heap of a value further on, or the edge's own, does not stop it. MUTANT, the next value's heap unread: 38 proven ranks of a heap went to the edge on an invented column of 20,000 rows (the frozen case `l0_cells_next_heap`)."""
    assert _edge_step([200] * 5, [163, 237, 200, 200, 200], 1000, (100, 300), 80) == [200] * 5
    assert _edge_step([200] * 5, [163, 237, 200, 200, 200], 1000, (100, 300), 80, heaps=((11.0, 280, 330),)) == [180, 220, 200, 200, 200]
    assert _edge_step([200] * 5, [163, 237, 200, 200, 200], 1000, (100, 300), 80, heaps=((11.0, 250, 330),)) == [163, 237, 200, 200, 200]
    assert _edge_step([200] * 5, [163, 237, 200, 200, 200], 1000, (100, 300), 80, heaps=((12.0, 280, 330),)) == [200] * 5


def test_step_2b_an_estimate_outside_the_ladder_bounds_leaves_step_2s_count() -> None:
    """A piece that is not even (`few`'s top band: 3,377 cells over 14 values, the edge bound from 1,377 up): nothing is read from it. MUTANT, today's count held there: the column's distance opens from 99 rows to 134 (K-S6-02 (v))."""
    assert _edge_step([100, 50, 50], [120, 30, 50], 200, (110, 130), 40) == [120, 30, 50]


def test_step_2b_leaves_a_value_a_published_tail_lists() -> None:
    """MUTANT, a listed value moved: `zoo.prescriptions`' ndc_11 missed its `tails.high.values` (K-S6-02 (iv))."""
    assert _edge_step([254, 200, 200, 200, 200], [281, 173, 200, 200, 200], 1054, (150, 400), 100, None, frozenset({11.0})) == [281, 173, 200, 200, 200]


def test_step_2b_the_estimate_reads_the_piece_below_too() -> None:
    """A falling column (`zoo.us_vitals`' temp_f at 99.1: 712 real, today's 599, step 2's 646): the two shares read linearly at the edge, 671, move the count to 623; the piece's share alone held it at 599, and the distance opened from 97 rows to 113."""
    assert _edge_step([599, 601, 599], [646, 554, 599], 1799, (500, 800), 97, (1562, 2))[0] == 623
    assert _edge_step([599, 601, 599], [646, 554, 599], 1799, (500, 800), 97)[0] == 599


def test_step_2b_today_far_from_the_estimate_moves_toward_step_2s_count() -> None:
    """Today's 199 against an estimate of 266 and half a margin of 49: the count stands at 217, between 199 and step 2's 298. MUTANT, today's count held: `change`'s distance opens from 99 rows to 179."""
    assert _edge_step([199, 301, 300], [298, 202, 300], 800, (198, 398), 99)[0] == 217


def test_the_count_cases_hold_todays_count_of_different_values(tmp_path: pathlib.Path) -> None:
    """Lane BT's verify, item 1: the twin with L0 holds the count today's twin holds, short or over before the rule."""
    for name in ("l0_cells_count_short", "l0_cells_count_over"):
        case = _oracle_cases()[name]
        loaded = _case_profile(tmp_path, name, case)
        seed = int(f"{case['seed']}")
        held = {cell for cell in generation.twin_column(generation.generate_held(loaded, seed), 0) if cell}
        plain = dataclasses.replace(loaded, relationships=dataclasses.replace(loaded.relationships, ladder=(), families=0))
        today = {cell for cell in generation.twin_column(generation.generate_held(plain, seed), 0) if cell}
        assert len(held) == len(today) == 56, name


def test_a_key_every_one_different_is_written_once_a_row(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The first skeptic's MAJOR 4 (step 2a): 5,000 different record numbers, every one written once at seed 2; MUTANT: step 2a withdrawn writes one twice."""
    keyed = _table_at(tmp_path, "keys", _keys(5000))
    assert len(set(generation.twin_column(generation.generate_held(keyed.loaded, 2), 0))) == 5000
    monkeypatch.setattr(generation, "_l0_spread", lambda facts, walls, entries, held: None)
    assert len(set(generation.twin_column(generation.generate_held(keyed.loaded, 2), 0))) < 5000


def _table_at(folder: pathlib.Path, name: str, made: "tuple[list[str], list[list[str]]]") -> _Switched:
    return _switched(folder, _write(folder, f"{name}.csv", made[0], made[1]))


def _strata_of_change(switched: _Switched, seed: int, value: float, monkeypatch: pytest.MonkeyPatch) -> "tuple[int, int]":
    """How many strata of today's `change` hold ``value`` before the least move, and how many hold a cell of it after."""
    seen: "list[tuple[int, int]]" = []
    built = generation._l0_least_move

    def spy(column, facts, layout, values, floor):  # type: ignore[no-untyped-def]
        moved = built(column, facts, layout, values, floor)
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


# -- THE CELLS AS WRITTEN STAY IN THEIR PIECES (G5.7b, G5.7g; the outside review, item 2) ----------


def _widths_table(folder: pathlib.Path) -> _Switched:
    """600 readings drawn on -2 to 6, each written at one, two or three figures, beside a binary companion."""
    draw = random.Random(206)
    rows: "list[list[str]]" = []
    for place in range(600):
        value = draw.uniform(-2, 6)
        width = draw.choice([1, 1, 1, 2, 3])
        rows += [[f"{value:.{width}f}", "a" if place % 2 else "b"]]
    # (the table's name keys the chain's draw: under this one it publishes the ladder)
    return _table_at(folder, "m", (["m", "g"], rows))


def _written_bands(switched: _Switched, twin: generation.Twin) -> "tuple[list[int], list[int]]":
    cut = generation._l0_columns(switched.loaded)["m"][0]
    assert cut is not None
    found = [0] * (len(cut.edges) + 1)
    for cell in generation.twin_column(twin, 0):
        if cell.strip():
            value = float(cell)
            found[sum(1 for edge in cut.edges if value >= edge)] += 1
    return found, list(cut.counts)


def test_a_written_width_never_carries_a_cell_across_a_cut(tmp_path: pathlib.Path) -> None:
    switched = _widths_table(tmp_path)
    found, published = _written_bands(switched, generation.generate_held(switched.loaded, 0))
    assert found == published


def test_red_with_the_snap_free_of_the_pieces(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the width's snap held to no piece: 5.175 written 5.18 crosses the edge 5.1756, and the check on the written cells refuses it."""
    switched = _widths_table(tmp_path)
    monkeypatch.setattr(generation, "_l0_snap_leaves", lambda value, width, walls: False)
    with pytest.raises(errors.ProfileError, match="writes a cell outside its band"):
        generation.generate_held(switched.loaded, 0)
    monkeypatch.setattr(generation, "_l0_cells_met", lambda column, walls, layout, values, cells: None)
    found, published = _written_bands(switched, generation.generate_held(switched.loaded, 0))
    assert found != published


# -- G7.3l AND G7A.4d: THE DATE'S PIECE, THE CLOCK'S HALVES AND KNOTS ---------------------------


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




def _older_clock(folder: pathlib.Path) -> contract.Profile:
    """The outside review's item 3: 400 clock times, every minute from 06:00 to 12:09 once, ten 12:10s and twenty 13:20s, described with no step (an older description), cut at its 95th percentile, 12:10, the high boundary's own rank."""
    cells = [f"{6 + minute // 60:02d}:{minute % 60:02d}" for minute in range(370)] + ["12:10"] * 10 + ["13:20"] * 20
    random.Random(1).shuffle(cells)
    path = _write(folder, "clock-older.csv", ["at"], [[cell] for cell in cells])
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    document = profile.build_document(reading.read_table(str(path), small_cell_floor=FLOOR), settings, [], [], [])
    block = document["columns"][0]  # type: ignore[index]
    block["clock_step"] = None
    for key in ("clock_census", "clock_heaps", "clock_codes", "minute_census", "minute_heaps", "second_census", "second_heaps"):
        block.pop(key, None)
    plain = contract.load_profile(str(fixtures.write_profile(folder, "clock-older.json", document)))
    entry = contract.LadderEntry("at", (((None, "p95"),), (("p95", None),)), (370, 30))
    return dataclasses.replace(plain, relationships=dataclasses.replace(plain.relationships, ladder=(entry,), families=1))


def _below_the_edge(loaded: contract.Profile, seed: int) -> int:
    return sum(1 for cell in generation.twin_column(generation.generate_held(loaded, seed), 0) if cell < "12:10")


def test_an_edges_rung_at_a_boundary_rank_cuts_the_clock(tmp_path: pathlib.Path) -> None:
    loaded = _older_clock(tmp_path)
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.ClockFacts) and facts.clock_step is None and facts.clock_percentiles["p95"] == "12:10"
    assert [_below_the_edge(loaded, seed) for seed in (0, 1, 2)] == [370, 370, 370]


def test_red_with_the_boundary_rung_left_out_of_the_knots(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the knots built from the rungs strictly inside the boundaries, as first built: 379 cells below 12:10, which the readings' check refuses."""
    loaded = _older_clock(tmp_path)
    built = generation._clock_l0_knots

    def inside_only(facts, parsed, low_rank, high_rank, low_boundary, high_boundary):  # type: ignore[no-untyped-def]
        return _knots_inside(built, facts, parsed, low_rank, high_rank, low_boundary, high_boundary)

    monkeypatch.setattr(generation, "_clock_l0_knots", inside_only)
    with pytest.raises(errors.ProfileError, match="misses the count of one of its bands"):
        generation.generate_held(loaded, 0)
    monkeypatch.setattr(generation, "_l0_readings_met", lambda column, readings: None)
    assert _below_the_edge(loaded, 0) == 379


def _knots_inside(built, facts, parsed, low_rank, high_rank, low_boundary, high_boundary):  # type: ignore[no-untyped-def]
    """The knots with every rung at a boundary rank taken out of the ladder first (the first build's exclusion)."""
    rungs = dict(facts.clock_percentiles)
    for step in range(1, len(generation._PCT) - 1):
        name = generation._LADDER_NAMES[step]
        rank = generation._rung_rank(generation._PCT[step], parsed)
        if not low_rank < rank < high_rank:
            rungs[name] = None
    return built(dataclasses.replace(facts, clock_percentiles=rungs), parsed, low_rank, high_rank, low_boundary, high_boundary)


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




def _sorted_book(folder: pathlib.Path) -> contract.Profile:
    """The outside review's item 1: 120 rows sorted by x (sixty 1s, then sixty 2s), c alternating the number 3 and the text `north`, 60 cells of each class."""
    strings = ["x", "c", "g", "north"]
    sheet_rows = [(1, [workbooks.cell("A1", "0", "s"), workbooks.cell("B1", "1", "s"), workbooks.cell("C1", "2", "s")])]
    draw = random.Random(1)
    for row in range(120):
        number = row + 2
        second = workbooks.cell(f"B{number}", "3") if row % 2 else workbooks.cell(f"B{number}", "3", "s")
        sheet_rows += [(number, [
            workbooks.cell(f"A{number}", "1" if row < 60 else "2"), second, workbooks.cell(f"C{number}", f"{draw.randint(1, 9)}"),
        ])]
    path = folder / "sorted.xlsx"
    folder.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_package(strings, sheet_rows, "A1:C121"))
    settings = taxonomy.Settings(small_cell_floor=1)
    document = profile.build_document(reading.read_table(str(path), small_cell_floor=1), settings, [], [], [])
    # ...the rows published as sorted by x, as a producer's description may say.
    document["source"]["dialect"]["row_order"] = {"collation": "number", "column": 1, "direction": "ascending"}  # type: ignore[index]
    plain = contract.load_profile(str(fixtures.write_profile(folder, "sorted.json", document)))
    facts = plain.columns[1].facts
    assert isinstance(facts, contract.LabelFacts)
    entry = contract.LadderEntry("c", tuple(((level.label,),) for level in facts.levels), tuple(level.count for level in facts.levels))
    return dataclasses.replace(plain, relationships=dataclasses.replace(plain.relationships, ladder=(entry,), families=1))


def _sorted_classes(tmp_path: pathlib.Path) -> "dict[str, int]":
    loaded = _sorted_book(tmp_path)
    assert loaded.source.dialect.row_order.column == 1
    back = _book_back(tmp_path, loaded, generation.generate_held(loaded, 0))
    found = back["columns"][1]["cell_classes"]  # type: ignore[index]
    return {name: found[name] for name in ("text", "number")}  # type: ignore[index]


def test_the_classes_move_with_the_cells_when_the_rows_are_sorted(tmp_path: pathlib.Path) -> None:
    assert _sorted_classes(tmp_path) == {"text": 60, "number": 60}


def test_red_with_the_classes_left_in_the_unsorted_order(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the sort moves the cells and not what G4.2a dealt them: 32 numeric cells instead of 60, as the outside review measured."""
    monkeypatch.setattr(generation, "_sheet_dealt_moved", lambda entry, moved: entry)
    assert _sorted_classes(tmp_path) == {"text": 88, "number": 32}


def test_what_g42a_deals_a_workbook_column_is_held_a_byte_a_row(tmp_path: pathlib.Path) -> None:
    """The outside review's item 6: each eligible workbook column's classes, format kinds and kinds of date travel as one code byte a row and a short palette, never three tuples of a row's texts."""
    loaded = _book_profile(tmp_path, "mixed", FLOOR)
    twin = generation.generate_held(loaded, 0)
    carried = [entry for entry in twin.sheet_dealt if entry is not None]
    assert carried
    for entry in carried:
        assert isinstance(entry, generation.SheetDealt)
        assert isinstance(entry.codes, bytes) and len(entry.codes) == twin.n_rows
        assert len(entry.palette) <= 256
        assert entry.written is None or isinstance(entry.written, generation.twinstore.HeldColumn)


def test_red_with_the_dealt_cells_held_as_tuples(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the first build's holding, three tuples a row: what travels is no longer a byte a row."""
    loaded = _book_profile(tmp_path, "mixed", FLOOR)
    built = generation._sheet_dealt_before

    def tupled(*arguments):  # type: ignore[no-untyped-def]
        dealt = built(*arguments)
        return dataclasses.replace(dealt, codes=tuple(dealt.codes))

    monkeypatch.setattr(generation, "_sheet_dealt_before", tupled)
    twin = generation.generate_held(loaded, 0)
    assert not all(isinstance(entry.codes, bytes) for entry in twin.sheet_dealt if entry is not None)


# -- THE INTERFACE G16 CALLS (G4.2b) ---------------------------------------------------------------------------


def _handed(loaded: contract.Profile, monkeypatch: pytest.MonkeyPatch, seed: int = 0) -> "list[tuple[str, generation.BandCells, int]]":
    seen: "list[tuple[str, generation.BandCells, int]]" = []
    built = generation._row_placement

    def hooked(step, profile_, content, drawn, finished, reserved=None, readings=None):  # type: ignore[no-untyped-def]
        found = generation.cells_by_band(profile_, step, content, drawn, reserved, readings)
        if found is not None:
            seen.append((found.column, found, len(content)))
        return built(step, profile_, content, drawn, finished, reserved, readings)

    monkeypatch.setattr(generation, "_row_placement", hooked)
    generation.generate_held(loaded, seed)
    monkeypatch.setattr(generation, "_row_placement", built)
    return seen


def test_case_13_the_interface_hands_over_every_arranged_cell_once(ward_small, monkeypatch: pytest.MonkeyPatch) -> None:
    # The interface reads its own column's cuts alone (the first skeptic's item 11).
    _PLANNED.clear()
    monkeypatch.setattr(generation, "_l0_columns", _every_column_read)
    seen = _handed(ward_small.loaded, monkeypatch)
    published = _published(ward_small)
    entries = {entry.column: entry for entry in ward_small.loaded.relationships.ladder}
    assert seen
    blank = chain_rules.records_holding_nothing(ward_small.document)
    for name, found, count in seen:
        flat = sorted(cell for group in found.groups for cell in group)
        assert flat == sorted(set(range(count)) - set(found.reserved)), name
        # One group per published band, in the published band order.
        assert len(found.groups) == len(entries[name].bands), name
        if not found.without:
            ranged = [found.sizes[place] for place in range(len(found.names)) if found.names[place] in ("range", "level")]
            assert ranged == [published[name][place] for place in range(len(found.names)) if found.names[place] in ("range", "level")], name
        assert len(found.reserved) == blank


_PLANNED: "list[int]" = []


def _every_column_read(profile_: contract.Profile) -> "dict[str, tuple[contract.L0Cuts | None, str]]":
    """`_l0_columns` as the plan calls it once; a second call is the interface reading every column again."""
    _PLANNED.append(1)
    if len(_PLANNED) > 1:
        raise AssertionError("every column's cuts were read again (the first skeptic's item 11)")
    return _L0_COLUMNS(profile_)


_L0_COLUMNS = generation._l0_columns


def _merged_table(folder: pathlib.Path) -> _Switched:
    """The outside review's item 4: 425 A, 375 B and one absent cell beside a binary companion, whose published bands are (missing + B, A)."""
    cells = ["A"] * 425 + ["B"] * 375 + [""]
    random.Random(4).shuffle(cells)
    return _table_at(folder, "merged801", (["c", "g"], [[cells[at], "x" if at % 2 else "y"] for at in range(801)]))


def _merged_sizes(folder: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> "tuple[list[int], list[int]]":
    switched = _merged_table(folder)
    found = [band for name, band, _count in _handed(switched.loaded, monkeypatch) if name == "c"][0]
    return list(found.sizes), list(_published(switched)["c"])


def test_a_band_joining_missing_cells_is_one_group(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sizes, published = _merged_sizes(tmp_path, monkeypatch)
    assert published == [376, 425]
    assert sizes == published


def test_red_with_the_missing_cells_in_a_group_of_their_own(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the spread bands mapped to no published band, as first built: three groups of 375, 425 and 1."""
    built = generation._l0_band_groups

    def apart(entry, edges):  # type: ignore[no-untyped-def]
        band_of, names, lowers, ranged = built(entry, edges)
        return {key: at for key, at in band_of.items() if not isinstance(key, str)}, names, lowers, ranged

    monkeypatch.setattr(generation, "_l0_band_groups", apart)
    sizes, published = _merged_sizes(tmp_path, monkeypatch)
    assert sizes != published


def _labelled_table(folder: pathlib.Path) -> _Switched:
    """The outside review's item 5: 1,200 readings, `NOT DETECTED` on every fifteenth row, beside two binary companions."""
    rows: "list[list[str]]" = []
    for at in range(1200):
        reading_ = "NOT DETECTED" if at % 15 == 7 else f"{(1 + (at * 37) % 4000) / 100:.2f}"
        rows += [[reading_, "a" if at % 2 else "b", "u" if at % 3 else "v"]]
    return _table_at(folder, "labelled1200", (["m", "g", "h"], rows))


def _labelled_found(folder: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> generation.BandCells:
    switched = _labelled_table(folder)
    assert switched.loaded.columns[0].statistical_type == "numbers_with_labels"
    found = [band for name, band, _count in _handed(switched.loaded, monkeypatch) if name == "m"][0]
    assert found.without
    return found


def _labelled_groups(folder: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> "dict[str, int]":
    found = _labelled_found(folder, monkeypatch)
    held: "dict[str, int]" = {}
    for place in range(len(found.names)):
        held[found.names[place]] = held.get(found.names[place], 0) + found.sizes[place]
    return held


def _range_groups_outside(found: generation.BandCells) -> "tuple[int, int]":
    """How many range groups the interface hands over holding a cell, and how many of their readings lie outside their own band's edges."""
    ranged = [place for place in range(len(found.names)) if found.names[place] == "range" and found.sizes[place] > 0]
    outside = 0
    for order in range(len(ranged)):
        place = ranged[order]
        low = found.lowers[place]
        high = found.lowers[ranged[order + 1]] if order + 1 < len(ranged) else None
        for read in found.readings[place]:
            if read is None or (isinstance(low, float) and read < low) or (isinstance(high, float) and not read < high):
                outside += 1
    return len(ranged), outside


def test_a_column_rule_b3_makes_is_handed_over_by_the_bands_its_cells_fall_in(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Each of the 12 published range bands one group, every reading inside its own edges (lane BT's verify 2, item 2 (i); lane BT2)."""
    found = _labelled_found(tmp_path, monkeypatch)
    held: "dict[str, int]" = {}
    for place in range(len(found.names)):
        held[found.names[place]] = held.get(found.names[place], 0) + found.sizes[place]
    assert held == {"labels": 80, "range": 1120}
    assert list(found.sizes) == [80, 112, 113, 56, 55, 112, 112, 112, 113, 56, 55, 113, 111]
    assert _range_groups_outside(found) == (12, 0)


def test_red_with_the_numbers_edges_dropped(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT (the verify's b3_edges_off): the edges of a column of numbers and labels dropped, which puts all 1,120 numbers in one range group."""
    monkeypatch.setattr(generation, "_l0_published_edges", lambda column, entry: [])
    found = _labelled_found(tmp_path, monkeypatch)
    assert _range_groups_outside(found) != (12, 0)
    assert list(found.sizes) != [80, 112, 113, 56, 55, 112, 112, 112, 113, 56, 55, 113, 111]


def test_red_with_no_reading_on_a_column_of_numbers_and_labels(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the joined and the labelled content routes giving no readings, as first built: every cell in `other` or `labels`, no range cell."""
    monkeypatch.setattr(generation, "_b3_readings", lambda column, cells, readings: readings.extend([None] * len(cells)))
    assert _labelled_groups(tmp_path, monkeypatch).get("range", 0) == 0


def _many_levels(folder: pathlib.Path) -> "tuple[contract.Profile, list[str]]":
    """1,600 published levels of 25 cells each: a column of words of many levels."""
    letters = "bcdfghjklmnpqrstvwxz"
    words = [f"{letters[level // 80]}{letters[(level // 4) % 20]}{'aeio'[level % 4]}" for level in range(1600)]
    cells: "list[str]" = []
    for word in words:
        cells += [word] * 25
    random.Random(8).shuffle(cells)
    path = _write(folder, "levels.csv", ["code"], [[cell] for cell in cells])
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    document = profile.build_document(reading.read_table(str(path), small_cell_floor=FLOOR), settings, [], [], [])
    plain = contract.load_profile(str(fixtures.write_profile(folder, "levels.json", document)))
    facts = plain.columns[0].facts
    assert isinstance(facts, contract.LabelFacts) and len(facts.levels) == 1600
    entry = contract.LadderEntry("code", tuple(((level.label,),) for level in facts.levels), tuple(level.count for level in facts.levels))
    loaded = dataclasses.replace(plain, relationships=dataclasses.replace(plain.relationships, ladder=(entry,), families=1))
    return loaded, [level.label for level in facts.levels for _cell in range(level.count)]


class _Compared:
    """A level's place that counts every comparison made with it (the levels' places `cells_by_band` searches)."""

    count = 0

    def __init__(self, held: object) -> None:
        self.held = held

    def __le__(self, other: object) -> bool:
        _Compared.count += 1
        return bool(self.held <= other)  # type: ignore[operator]

    def __lt__(self, other: object) -> bool:
        _Compared.count += 1
        return bool(self.held < other)  # type: ignore[operator]

    def __ge__(self, other: object) -> bool:
        _Compared.count += 1
        return bool(self.held >= other)  # type: ignore[operator]

    def __gt__(self, other: object) -> bool:
        _Compared.count += 1
        return bool(self.held > other)  # type: ignore[operator]


def _linear_places(ordered, value):  # type: ignore[no-untyped-def]
    """The first build's lookup: every level asked for every cell."""
    return sum(1 for item in ordered if item <= value)


def _places_compared(loaded: contract.Profile, content: "list[str]", monkeypatch: pytest.MonkeyPatch, search) -> int:  # type: ignore[no-untyped-def]
    """How many comparisons with the levels' places `cells_by_band` makes to group ``content``, the places found by ``search``.

    The levels' places are wrapped once each in a value that counts every
    comparison made with it, so a search that iterates as well as one that
    indexes is counted (lane BT's verify 2, item 2 (ii)).
    """
    held: "dict[int, list[_Compared]]" = {}

    def counted(ordered, value):  # type: ignore[no-untyped-def]
        if id(ordered) not in held:
            held[id(ordered)] = [_Compared(item) for item in ordered]
        return search(held[id(ordered)], value)

    _Compared.count = 0
    monkeypatch.setattr(generation, "_places_at_or_below", counted)
    found = generation.cells_by_band(loaded, 0, content, list(range(len(content))), ((), False), None)
    assert found is not None and len(found.groups) == 1600 and set(found.sizes) == {25}
    return _Compared.count


def test_a_column_of_many_levels_is_grouped_a_few_steps_a_cell(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The outside review's item 8: each cell's level found by halving the levels' places, at most twelve comparisons a cell over 1,600 levels."""
    loaded, content = _many_levels(tmp_path)
    assert _places_compared(loaded, content, monkeypatch, generation._places_at_or_below) <= 12 * len(content)


def test_red_with_every_level_asked_for_every_cell(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the product run with the first build's lookup, every level asked for every cell: 1,600 comparisons a cell, 64 million in all."""
    loaded, content = _many_levels(tmp_path)
    assert _places_compared(loaded, content, monkeypatch, _linear_places) > 12 * len(content)


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


# -- G5.7c STEP 3'S COUNT RULE OVER TODAY'S COUNT: THE FLOOR TIER'S EXCLUSIONS (lane BT's verify 2, item 1; lane BT2) --


def _floor_tier(tmp_path: pathlib.Path) -> "tuple[contract.NumericFacts, generation._Entries]":
    """Ten whole values 0 to 9 laid in one piece, the six under the floor of 11 each excluded but one.

    The described column holds 100 cells at each of 0 to 9 (so `min` 0,
    `max` 9 and the 20th percentile's rung 1.8); its facts are given the
    published mode 4 and a low tail at the 20th percentile. The strata
    hold 2 cells at 0 (`min`, and a tail row), 3 at 1 (a tail row), 4 at
    the mode, 5 at 6 (a value step 3 gave back), 8 at 7 and 6 at 9
    (`max`), and 50 at every other value: the smallest stratum under the
    floor that is no kept value, mode, `min`, `max` or tail row is 7's.
    """
    cells = [str(value) for value in range(10) for _cell in range(100)]
    path = _write(tmp_path, "floor-tier.csv", ["v"], [[cell] for cell in cells])
    document = profile.build_document(reading.read_table(str(path), small_cell_floor=FLOOR), taxonomy.Settings(small_cell_floor=FLOOR), [], [], [])
    facts = contract.load_profile(str(fixtures.write_profile(tmp_path, "floor-tier.json", document))).columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    assert facts.percentiles.minimum == 0.0 and facts.percentiles.maximum == 9.0
    facts = dataclasses.replace(
        facts, mode=4.0, tails=contract.NumericTailFacts(contract.TailSide(20, 300, None, None, ()), None)
    )
    sizes = [2, 3, 50, 50, 4, 50, 5, 8, 50, 6]
    entries = generation._Entries(
        [float(value) for value in range(10)], list(sizes), list(range(10)), [0] * 10, list(sizes), [0] * 10
    )
    entries.ordered = 10
    entries.today = list(sizes)
    entries.kept = {6: 1}
    return facts, entries


def test_the_floor_tier_merges_no_kept_value_mode_min_max_or_tail_row(tmp_path: pathlib.Path) -> None:
    """G5.7c step 3, over today's count, where no stratum stands between two proven heaps: the smallest stratum under the
    floor joins its nearer neighbour, never a value step 3 gave back, the published mode, `min`, `max` or a tail's row.
    Each exclusion is red on its source mutant (the verify's over_kept_merged, over_ends_merged and over_tails_merged,
    and the mode's): the stratum merged is then 6's, 9's, 1's or 4's, never 7's."""
    facts, entries = _floor_tier(tmp_path)
    assert generation._l0_merged_pick(facts, entries, [], FLOOR, False) == (7, 6)
    generation._l0_counted(facts, entries, 9, [], FLOOR)
    assert entries.sizes == [2, 3, 50, 50, 4, 50, 13, 0, 50, 6]


# -- THE SEARCHES A LARGE OR CROWDED COLUMN ASKS (the outside review, items 7 and 9) ------------------------------


def _holds_asked(folder: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> "tuple[int, int]":
    """4,000 shuffled consecutive whole numbers beside a binary companion: how many times a point's freedom is asked, and how many different values are written."""
    values = [str(value) for value in range(100, 4100)]
    random.Random(7).shuffle(values)
    switched = _table_at(folder, "consecutive", (["v", "g"], [[values[at], "a" if at % 2 else "b"] for at in range(4000)]))
    asked = [0]
    built = generation._l0_holds

    def counted(taken, value):  # type: ignore[no-untyped-def]
        asked[0] += 1
        return built(taken, value)

    monkeypatch.setattr(generation, "_l0_holds", counted)
    twin = generation.generate_held(switched.loaded, 0)
    return asked[0], len(set(generation.twin_column(twin, 0)))


def test_a_free_whole_number_is_sought_inside_its_gap(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    asked, different = _holds_asked(tmp_path, monkeypatch)
    assert different == 4000
    assert asked <= 4000


def test_red_with_the_search_running_past_its_gap(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: each search unbounded by its gap, as first built: every occupied value beyond the gap asked again, hundreds of thousands of times."""
    monkeypatch.setattr(generation, "_l0_gap_room", lambda far, start, upward: 1 << 20)
    asked, _different = _holds_asked(tmp_path, monkeypatch)
    assert asked > 100000


class _TooManyReadings(Exception):
    """Raised by `_bounded_grid_float` past its readings: a walk a unit at a time fails instead of hanging."""


def _bounded_grid_float(monkeypatch: pytest.MonkeyPatch, most: int = 10000) -> "list[int]":
    """`generation._grid_float` replaced by itself behind a counter that raises past ``most`` readings (lane BT's verify 2, item 2 (iii))."""
    built = generation._grid_float
    read = [0]

    def bounded(index, figures):  # type: ignore[no-untyped-def]
        read[0] += 1
        if read[0] > most:
            raise _TooManyReadings(read[0])
        return built(index, figures)

    monkeypatch.setattr(generation, "_grid_float", bounded)
    return read


def _stands_asked(value: float, monkeypatch: pytest.MonkeyPatch) -> "tuple[int, int]":
    asked = [0]
    built = generation._grid_stands

    def counted(index, figures, value_, strictly):  # type: ignore[no-untyped-def]
        asked[0] += 1
        return built(index, figures, value_, strictly)

    monkeypatch.setattr(generation, "_grid_stands", counted)
    found = generation._grid_index_above(value, 0, False)
    return found, asked[0]


def test_a_grid_index_near_a_large_number_is_found_by_halving(monkeypatch: pytest.MonkeyPatch) -> None:
    value = float(10**30 + 2 * 10**26)
    _bounded_grid_float(monkeypatch)
    found, asked = _stands_asked(value, monkeypatch)
    assert generation._grid_float(found, 0) >= value > generation._grid_float(found - 1, 0)
    assert asked <= 200


def _walked_a_unit_at_a_time(value: float, figures: int, strictly: bool) -> int:
    """The first build's walk: a unit at a time from `floor(value * 10**figures)`."""
    index = generation._scaled_floor(value, figures)
    if generation._grid_stands(index, figures, value, strictly):
        while generation._grid_stands(index - 1, figures, value, strictly):
            index = index - 1
        return index
    while not generation._grid_stands(index, figures, value, strictly):
        index = index + 1
    return index


def test_red_with_the_index_walked_a_unit_at_a_time(monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the product's grid index found by the first build's walk, a unit at a time across the indices one binary64 rounds them to: it reads past ten thousand points and fails, where halving reads under two hundred."""
    monkeypatch.setattr(generation, "_grid_index_above", _walked_a_unit_at_a_time)
    _bounded_grid_float(monkeypatch)
    with pytest.raises(_TooManyReadings):
        _stands_asked(float(10**30 + 2 * 10**26), monkeypatch)


def test_a_column_of_numbers_near_ten_to_the_thirty_is_laid_at_once(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The outside review's item 9: 600 readings `10**30 + (i % 30) * 10**26` beside a binary companion are planned and made with L0, each band at its count."""
    _bounded_grid_float(monkeypatch, 20000)  # the column reads under 10,000 points, its description included (lane BT2)
    switched = _table_at(tmp_path, "large", (["v", "g"], [[str(10**30 + (at % 30) * 10**26), "a" if at % 2 else "b"] for at in range(600)]))
    cut = generation._l0_columns(switched.loaded)["v"][0]
    assert cut is not None
    started = time.process_time()
    twin = generation.generate_held(switched.loaded, 0)
    assert time.process_time() - started < 30.0
    found = [0] * (len(cut.edges) + 1)
    for cell in generation.twin_column(twin, 0):
        value = float(cell)
        found[sum(1 for edge in cut.edges if value >= edge)] += 1
    assert found == list(cut.counts)


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
