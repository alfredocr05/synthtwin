"""Batch 4zz's fix round: the outside review's items fixed on the merged line, each with a case its mutant turns red.

ITEM 1: a native file's column label holding a date, a telephone number,
a network address or a titled name, and a value label holding a date,
reached the description and the twin's bytes. ITEM 2: an SPSS missing
code of a held identifier column (a real record number) reached the
twin's dictionary. ITEMS 3 AND 4: a note's telephone number was drawn
back from its figures' census, and a titled name kept as a word. ITEM 5:
only a note's first date was made up. ITEM 6: a held birth date was
written again in a year at or before the year cut. ITEM 7: of two columns
whose names differ only in capitals, the one typed exactly lost to the
other. ITEM 8: the ties' last deal moved a date outside its column's
real months. ITEM 9: a column each person holds one value of was dealt
row by row as a gap's dependent. ITEM 14: a made-up ISO date was written
with a day of one figure. ITEM 18: a Parquet column read in pieces was
copied whole at every piece (checked by reading).

Machine-free: invented tables drawn here from a seed, read by the
product's own functions or through its commands below the table floor
(the suite's switch).
"""

import datetime
import json
import math
import pathlib
import random
import re

import pytest

from synthtwin import cli, inside_dates, inside_text, native, taxonomy

# -- item 1: native labels --------------------------------------------------------------------------------------


@pytest.mark.parametrize("text", ["Seen 2024-03-05", "2024-03-05", "call 312-555-0199", "(312) 555-0199",
                                  "10.1.2.3", "Dr. Alice Smith", "Mar 2024"])
def test_a_label_holding_an_identifier_form_or_a_date_is_withheld(text: str) -> None:
    assert not native.column_label_published(text)
    assert not native.label_published(text)


@pytest.mark.parametrize("text", ["Systolic BP", "Age in years", "Glucose (mg/dL)", "Visit 1-2", "Weight 2.5 kg"])
def test_an_ordinary_column_label_is_still_published(text: str) -> None:
    assert native.column_label_published(text)


def test_a_stata_files_dated_and_telephone_labels_reach_neither_description_nor_twin(tmp_path: pathlib.Path) -> None:
    pandas = pytest.importorskip("pandas")
    pyreadstat = pytest.importorskip("pyreadstat")
    rng = random.Random(4)
    frame = pandas.DataFrame({"age": [float(rng.randint(18, 89)) for _ in range(400)],
                              "arm": [float(rng.choice([1, 2])) for _ in range(400)]})
    source = tmp_path / "visits.dta"
    pyreadstat.write_dta(frame, str(source), column_labels={"age": "Age at 2024-03-05", "arm": "call 312-555-0199"},
                         variable_value_labels={"arm": {1: "Control", 2: "2024-03-06"}})
    assert cli.main(["profile", str(source)]) == 0
    assert cli.main(["generate", str(tmp_path / "visits-profile.json"), "--seed", "2"]) == 0
    twin = (tmp_path / "visits-twin.dta").read_bytes()
    described = (tmp_path / "visits-profile.json").read_text(encoding="utf-8")
    for secret in ("2024-03-05", "312-555-0199", "2024-03-06"):
        assert secret not in described, secret
        assert bytes(secret, "ascii") not in twin, secret
    assert "Control" in described


# -- item 2: SPSS missing codes of a held column -----------------------------------------------------------------


def test_a_held_columns_missing_code_never_reaches_the_twin(tmp_path: pathlib.Path) -> None:
    pandas = pytest.importorskip("pandas")
    pyreadstat = pytest.importorskip("pyreadstat")
    rng = random.Random(6)
    frame = pandas.DataFrame({"chart": [float(100000 + index) for index in range(400)],
                              "sbp": [round(rng.gauss(130, 15), 1) for _ in range(400)]})
    source = tmp_path / "visits.sav"
    pyreadstat.write_sav(frame, str(source), missing_ranges={"chart": [483712.0], "sbp": [999.0]})
    assert cli.main(["profile", str(source), "--identifier", "chart"]) == 0
    block = json.loads((tmp_path / "visits-profile.json").read_text(encoding="utf-8"))["source"]["native"]
    by_name = {entry["name"]: entry for entry in block["columns"]} if "name" in block["columns"][0] else {
        name: entry for name, entry in zip(("chart", "sbp"), block["columns"])}
    assert "missing" not in by_name["chart"] or by_name["chart"]["missing"] in (None, {}), by_name["chart"]
    assert cli.main(["generate", str(tmp_path / "visits-profile.json"), "--seed", "2"]) == 0
    _data, meta = pyreadstat.read_sav(str(tmp_path / "visits-twin.sav"), user_missing=True)
    assert "chart" not in meta.missing_ranges, meta.missing_ranges
    assert "sbp" in meta.missing_ranges, meta.missing_ranges


# -- items 3 to 6 and 14: the text zone --------------------------------------------------------------------------


def _notes(rows: int, form: str, seed: int) -> "list[str]":
    draw = random.Random(f"notes-{seed}")
    return [form.format(a=draw.randint(1000, 9999), b=draw.randint(60, 140), d=draw.randint(10, 28)) for _ in range(rows)]


def test_a_note_holding_a_telephone_number_or_a_titled_name_is_learned_as_no_template() -> None:
    for form in ("call 555-{a}; pulse {b}", "seen by Dr. Smith, pulse {b}"):
        entry = inside_text.entry_of(_notes(2000, form, 1), inside_text.MODE_FREE, [], None, 11)
        assert entry is None, (form, entry and sorted(entry))
    # ...and a note holding neither keeps its template.
    kept = inside_text.entry_of(_notes(2000, "pulse {b}, dose {a}", 1), inside_text.MODE_FREE, [], None, 11)
    assert kept is not None and kept["templates"]


def test_every_date_of_a_note_is_made_up() -> None:
    cells = _notes(2000, "admit 2023-01-{d} discharge 2023-02-{d} hr {b}", 2)
    entry = inside_text.entry_of(cells, inside_text.MODE_FREE, [], None, 11)
    assert entry is not None
    templates = entry["templates"]
    assert templates
    for key in templates:
        assert key.count(inside_text._DATE) == 6, key
    writer = inside_text._writer_of(entry, inside_text._stream(3, "notes", "test"))
    apart = 0
    for key in templates:
        for _draw in range(50):
            drawn = inside_text._cell_of(writer, key)
            found = re.findall(r"(\d{4})-(\d{2})-(\d{2})", drawn)
            assert len(found) == 2, drawn
            for year, month, day in found:
                datetime.date(int(year), int(month), int(day))
            apart += int(found[0] != found[1])
    # ...each date drawn on its own (mutant: the cell's first date written twice).
    assert apart > 0


def test_no_made_up_date_falls_in_a_year_at_or_before_the_year_cut() -> None:
    cut = taxonomy.year_cutoff(taxonomy.SAFE_HARBOR_REFERENCE_YEAR)
    rows = [inside_text.dated(inside_text.word_tokens(text)) for text in ("15 mars 1910", "16 mars 1950", "3 mai 1911")]
    calendar = inside_text._calendar(rows)
    years = {int(key.split(".")[0]) for key in calendar["cells"]}
    assert years == {1950}, years
    assert all(year > cut for year in years)
    # ...and a held column whose every date lies before the cut keeps no template: its cells are left blank.
    cells = [f"{1 + place % 28} mars {1905 + place % 20}" for place in range(2000)]
    entry = inside_text.entry_of(cells, inside_text.MODE_HELD, [], None, 11, [True] * len(cells))
    assert entry is None or not entry["templates"], entry and sorted(entry["templates"])


def test_a_made_up_iso_day_is_written_in_two_figures_where_the_months_are() -> None:
    rows = [inside_text.dated(inside_text.word_tokens(text)) for text in ("2023-03-15", "2023-04-20", "2023-05-11")]
    assert inside_text._calendar(rows)["padded"] is True


# -- item 7: a typed name -----------------------------------------------------------------------------------------


def test_the_name_typed_exactly_is_taken_and_two_alike_are_asked_again() -> None:
    assert cli._names_typed("VALUE", ("value", "VALUE")) == [("VALUE", "")]
    assert cli._names_typed("value", ("value", "VALUE")) == [("value", "")]
    assert cli._names_typed("Value", ("value", "VALUE")) is None
    assert cli._names_typed("AGE", ("age", "crp")) == [("age", "")]


# -- items 8 and 9: the ties' last deal ---------------------------------------------------------------------------

EPOCH = datetime.datetime(2022, 3, 1, 7, 30)
SERVICES = ("GEN", "ORTHO", "CARD")


def _cases(persons: int, seed: int) -> "dict[str, list[str]]":
    """Four cases a person: a service and an urgency set the minutes; a person's own flag, fixed on all their rows,
    goes with their minutes."""
    draw = random.Random(f"cases-{seed}")
    out: "dict[str, list[str]]" = {name: [] for name in ("pid", "service", "emergency", "incision", "close", "flagged")}
    for person in range(persons):
        flagged = draw.random() < 0.3
        for _visit in range(4):
            service = draw.choice(SERVICES)
            emergency = draw.random() < 0.2
            start = EPOCH + datetime.timedelta(days=draw.randrange(300), minutes=15 * draw.randrange(30))
            minutes = math.exp(draw.gauss({"GEN": 4.2, "ORTHO": 4.5, "CARD": 5.1}[service] + 0.5 * emergency
                                          + 0.6 * flagged, 0.4))
            close = start + datetime.timedelta(minutes=max(5, int(round(minutes))))
            out["pid"] += [f"P{person:05d}"]
            out["service"] += [service]
            out["emergency"] += ["Y" if emergency else "N"]
            out["incision"] += [start.strftime("%Y-%m-%d %H:%M")]
            out["close"] += [close.strftime("%Y-%m-%d %H:%M")]
            out["flagged"] += ["Y" if flagged else "N"]
    return out


def _levels(cells: "list[str]") -> "list[str]":
    counts: "dict[str, int]" = {}
    for cell in cells:
        counts[cell] = counts.get(cell, 0) + 1
    return [cell for _count, cell in sorted((-count, cell) for cell, count in counts.items())]


def _tied_zone(table: "dict[str, list[str]]", person: str) -> "dict[str, object]":
    rows = len(table["service"])
    gathered = inside_dates.census(person, {}, (), False)
    for name in ("pid", "service", "emergency", "incision", "close", "flagged"):
        inside_dates.take_column(gathered, name, table[name])
    zone = inside_dates.zone_of(gathered)
    at = inside_dates.tie_rows(rows)
    sources = [inside_dates.TieSource(name, "label", [table[name][row] for row in at], [], _levels(table[name]), place)
               for name, place in (("service", 1), ("emergency", 2), ("flagged", 5))]
    inside_dates.tie_chains(zone, gathered, at, sources)
    return zone


def test_the_last_deal_keeps_every_date_inside_its_columns_real_months() -> None:
    table = _cases(1000, 1)
    zone = _tied_zone(table, "")
    assert inside_dates.tied(zone)
    twin = {name: list(cells) for name, cells in table.items()}
    # A twin whose first rows of each service open on the real calendar's last evening, closing half an hour later:
    # inside the real months, but a longer gap dealt to them would close in the next month.
    final = datetime.date.fromisoformat(max(table["incision"])[:10])
    following = datetime.date(final.year + (final.month == 12), final.month % 12 + 1, 1)
    last = (following - datetime.timedelta(days=1)).isoformat()
    for service in SERVICES:
        mine = [row for row in range(len(table["service"])) if table["service"][row] == service][:150]
        for row in mine:
            twin["incision"][row] = f"{last} 23:00"
            twin["close"][row] = f"{last} 23:30"
    moved = inside_dates.tied_again(zone, {name: list(cells) for name, cells in twin.items()}, len(twin["pid"]), 7)
    assert "close" in moved
    real_last = max(table["close"])[:7]
    assert max(cell[:7] for cell in moved["close"] if cell) <= real_last, max(moved["close"])


def test_a_dependent_each_person_holds_one_value_of_is_never_dealt_row_by_row() -> None:
    table = _cases(1000, 2)
    zone = _tied_zone(table, "pid")
    dependents = zone["columns"]["close"]["chain"]["tie"]["dependents"]  # type: ignore[index]
    assert "flagged" in [entry["column"] for entry in dependents], dependents
    twin = {name: list(cells) for name, cells in table.items()}
    draw = random.Random(9)
    flags = {person: draw.choice(("Y", "N")) for person in sorted(set(table["pid"]))}
    twin["flagged"] = [flags[person] for person in twin["pid"]]
    moved = inside_dates.tied_again(zone, {name: list(cells) for name, cells in twin.items()}, len(twin["pid"]), 5)
    written = moved["flagged"] if "flagged" in moved else twin["flagged"]
    held: "dict[str, set[str]]" = {}
    for person, flag in zip(twin["pid"], written):
        held.setdefault(person, set()).add(flag)
    assert all(len(values) == 1 for values in held.values()), sum(1 for values in held.values() if len(values) > 1)
