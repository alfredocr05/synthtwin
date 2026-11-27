"""The order the real rows stand in, kept in the inside record and given to the twin (lane TOOLS, `inside_order`).

MEASURED FIRST, on the base: eight invented tables sorted the way health
extracts are, through `synthtwin twin`. The description's own row order
kept a table sorted by an ISO date, a number or a descending ISO date;
the twin lost the order -- about half its adjacent rows out of order, a
shuffle's share -- of a table sorted by a date written month first, by a
stamp with its empty cells last, and by the person then each person's
visit dates (a person's rows scattered, 1 person of 302 with their visits
in time order). The record's `order` zone now keeps which column, or the
person and then which column, the rows are sorted by, and the inside
generation puts the twin's rows in that order by its own cells.

The readers and the sort are held here on small lists; one case runs
`synthtwin twin` on a long table of visits at the floor of 20,000 rows and
reads the twin's order back. Each guard is red on the mutant its case's
docstring names.
"""

from __future__ import annotations

import csv
import datetime
import json
import pathlib
import random

import pytest

from synthtwin import cli, inside, inside_order, installation


def test_the_date_reader_reads_the_layouts_and_nothing_else() -> None:
    """ISO, slashes, the month first with or without a zero, a clock with or without seconds or a meridiem."""
    assert inside_order.date_key("2023-03-14") == (2023, 3, 14, -1)
    assert inside_order.date_key("2023/03/14 09:15") == (2023, 3, 14, 33300)
    assert inside_order.date_key("3/4/2023") == (2023, 3, 4, -1)
    assert inside_order.date_key("03-04-2023 9:15 PM") == (2023, 3, 4, 76500)
    assert inside_order.date_key("2023-03-14T23:59:59") == (2023, 3, 14, 86399)
    for other in ("", "14/03/2023", "2023-02-30", "3/4/23", "March 4, 2023", "12:00", "2023-03-14 25:00", "abc"):
        assert inside_order.date_key(other) is None, other
    with pytest.raises(TypeError):
        inside_order.date_key(5)  # type: ignore[arg-type]


def test_one_key_reads_numbers_dates_then_text_with_empty_cells_last() -> None:
    """A column ordered under its first reading that keys every present cell; its empty cells only at the end."""
    assert inside_order.one_key(["1", "2", "2", "10"]) == ("number", "ascending")
    assert inside_order.one_key(["1/9/2023", "1/10/2023", "2/1/2023"]) == ("date", "ascending")
    assert inside_order.one_key(["P003", "P002", "P001"]) == ("text", "descending")
    assert inside_order.one_key(["2023-01-02 10:00", "2023-01-03 08:00", "2023-01-03 09:00", "", ""]) == (
        "date", "ascending")
    assert inside_order.one_key(["1", "2", "3", "", "4"]) is None, "an empty cell inside the run"
    assert inside_order.one_key(["2", "10", "9"]) is None, "numbers out of order are no text order"
    assert inside_order.one_key(["a", "a", "a"]) is None, "no change"
    assert inside_order.one_key(["b", "a", "c"]) is None


def _visits(people: int, seed: int, text_keys: bool = False, by_key: bool = True) -> "list[tuple[str, str, str]]":
    """A long table of visits: a person's rows together, each person's visits in time order; (person, date, reading)."""
    rng = random.Random(seed)
    rows: "list[tuple[str, str, str]]" = []
    order = list(range(1, people + 1))
    if not by_key:
        rng.shuffle(order)
    for person in order:
        day = datetime.date(2021, 1, 1) + datetime.timedelta(days=rng.randrange(300))
        for _ in range(rng.randint(2, 6)):
            day = day + datetime.timedelta(days=rng.randint(5, 60))
            key = f"P{person:05d}" if text_keys else f"{person}"
            rows += [(key, f"{day.month}/{day.day}/{day.year}", f"{rng.gauss(120, 10):.0f}")]
    return rows


def _columns(rows: "list[tuple[str, str, str]]") -> "list[tuple[str, list[str]]]":
    return [("pid", [row[0] for row in rows]), ("seen", [row[1] for row in rows]), ("sbp", [row[2] for row in rows])]


def test_the_person_then_the_date_is_found_and_the_persons_order() -> None:
    """Sorted by the person's key then the visit date: two keys, by key; grouped in another order: by each first visit.

    The zone holds column names and words alone. MUTANT: `see` not looking
    for a second key within the first key's tied runs -- the zone keeps the
    person alone, and each twin person's visits stay out of time order.
    """
    numbered = inside_order.zone_of(_columns(_visits(40, 1)), "pid")
    assert numbered == {
        "version": 1, "groups": "by key",
        "keys": [{"column": "pid", "read_as": "number", "direction": "ascending"},
                 {"column": "seen", "read_as": "date", "direction": "ascending"}],
    }
    texted = inside_order.zone_of(_columns(_visits(40, 2, text_keys=True)), "pid")
    assert texted is not None and texted["keys"][0]["read_as"] == "text"  # type: ignore[index]
    shuffled = inside_order.zone_of(_columns(_visits(40, 3, by_key=False)), "pid")
    assert shuffled is not None and shuffled["groups"] == "by first"
    assert inside_order.zone_of(_columns(_visits(40, 3, by_key=False)), "") is None, "no person, no order read"
    words = json.dumps(numbered)
    for row in _visits(40, 1):
        assert f'"{row[1]}"' not in words and f'"{row[2]}"' not in words


def test_the_twin_is_put_in_the_kept_order_by_its_own_cells() -> None:
    """A shuffled twin: each person's rows together, persons by key, visits in time order, ties as they stood.

    MUTANT: `permutation` sorting the persons' rows by their key alone (no
    second key) -- the visits are not in time order.
    """
    zone = inside_order.zone_of(_columns(_visits(40, 1)), "pid")
    assert zone is not None
    twin = _visits(60, 9)
    random.Random(4).shuffle(twin)
    cells = {"pid": [row[0] for row in twin], "seen": [row[1] for row in twin]}
    placed = inside_order.permutation(zone, cells, list(range(len(twin))))
    assert sorted(placed) == list(range(len(twin)))
    ordered = [twin[row] for row in placed]
    keys = [int(row[0]) for row in ordered]
    assert keys == sorted(keys)
    for person in set(keys):
        days = [inside_order.date_key(row[1]) for row in ordered if int(row[0]) == person]
        assert days == sorted(days)  # type: ignore[type-var]


def test_one_key_descending_with_empty_cells_last_and_ties_kept() -> None:
    """Descending dates: the twin's later dates first, its empty cells last, tied rows in the order they stood."""
    zone = {"version": 1, "groups": "by key", "keys": [{"column": "d", "read_as": "date", "direction": "descending"}]}
    cells = {"d": ["2023-01-01", "", "2023-02-01", "2023-01-01", "2023-03-01", ""]}
    assert inside_order.permutation(zone, cells, [0, 1, 2, 3, 4, 5]) == [4, 2, 0, 3, 1, 5]
    up = {"version": 1, "groups": "by key", "keys": [{"column": "d", "read_as": "date", "direction": "ascending"}]}
    assert inside_order.permutation(up, cells, [0, 1, 2, 3, 4, 5]) == [0, 3, 2, 4, 1, 5]


def test_a_row_sequence_column_is_passed_over() -> None:
    """A column the description publishes as the row sequence orders nothing: the date beside it is the key.

    MUTANT: `see` not passing over `Finder.skip` -- the row index is the key.
    """
    finder = inside_order.Finder("", ("row",))
    inside_order.see(finder, "row", [str(index) for index in range(30)])
    inside_order.see(finder, "seen", [f"2023-01-{1 + index:02d}" for index in range(30)])
    assert inside_order.finished(finder) == {
        "version": 1, "groups": "by key", "keys": [{"column": "seen", "read_as": "date", "direction": "ascending"}]
    }


def test_a_zone_not_this_versions_or_naming_another_column_is_not_read() -> None:
    good = {"version": 1, "groups": "by key", "keys": [{"column": "d", "read_as": "date", "direction": "ascending"}]}
    assert inside_order.read_zone(good, ["d"]) == good
    for bad in (None, [], {"version": 2, "groups": "by key", "keys": good["keys"]}, {"version": 1, "keys": good["keys"]},
                {"version": 1, "groups": "by key", "keys": []},
                {"version": 1, "groups": "by key", "keys": [{"column": "x", "read_as": "date", "direction": "ascending"}]},
                {"version": 1, "groups": "by key", "keys": [{"column": "d", "read_as": "colour", "direction": "ascending"}]}):
        assert inside_order.read_zone(bad, ["d"]) is None, bad


# -- at the floor, through `synthtwin twin` -------------------------------------------------------------------------


def _long_table(path: pathlib.Path) -> None:
    """20,000 rows of visits, about 2,850 people, sorted by the person then the visit date (written month first)."""
    rng = random.Random(11)
    rows: "list[list[str]]" = []
    person = 0
    while len(rows) < 20000:
        person += 1
        day = datetime.date(2021, 1, 1) + datetime.timedelta(days=rng.randrange(600))
        level = rng.gauss(130, 12)
        for _ in range(rng.randint(4, 10)):
            if len(rows) >= 20000:
                break
            day = day + datetime.timedelta(days=rng.randint(7, 90))
            rows += [[f"{person}", f"{day.month}/{day.day}/{day.year}", f"{level + rng.gauss(0, 8):.0f}",
                      rng.choice(["north", "south", "east", "west"])]]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["subject_id", "visit_date", "sbp", "ward"])
        writer.writerows(rows)


def _read(path: pathlib.Path) -> "list[list[str]]":
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.reader(handle))[1:]


def test_the_twin_of_a_long_table_keeps_each_persons_rows_together_and_in_time_order(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`synthtwin twin` at the floor: the record keeps the person then the date, and every twin person's rows stand
    together, the persons by their key, each one's visits in time order -- `groupby(...).first()` is each person's
    first visit on the twin as on the table.

    MUTANT: the inside generation not reading the zone -- the twin's persons
    scattered over the file, their visits out of order.
    """
    # The run's own private folder, as the inside gate files name it (the suite's folders are temporary to the
    # record's guard, which writes no record there).
    private = pathlib.Path(tmp_path, "installation", "synthtwin", "inside")
    for folder in (private.parent.parent, private.parent, private):
        folder.mkdir(mode=0o700, exist_ok=True)
        folder.chmod(0o700)
    monkeypatch.setattr(
        inside, "default_places", lambda: inside.Places(private, (), (), installation.system_name(), ())
    )
    work = tmp_path / "work"
    work.mkdir()
    table = work / "visits.csv"
    _long_table(table)
    code = cli.main(["twin", str(table), "--person", "subject_id"], small_tables_refused=True)
    assert code in (0, 3)
    records = sorted(private.glob(f"*{inside.SUFFIX}"))
    assert len(records) == 1
    zone = inside.load_record(records[0])["zones"]["order"]  # type: ignore[index]
    assert zone["keys"] == [  # type: ignore[index]
        {"column": "subject_id", "read_as": "number", "direction": "ascending"},
        {"column": "visit_date", "read_as": "date", "direction": "ascending"},
    ]
    twin = _read(work / "visits-synthtwin" / "visits-twin.csv")
    runs = 1 + sum(1 for place in range(1, len(twin)) if twin[place][0] != twin[place - 1][0])
    assert runs == len({row[0] for row in twin}), "each twin person's rows together"
    keys = [float(row[0]) for row in twin]
    assert keys == sorted(keys)
    out_of_time = 0
    for place in range(1, len(twin)):
        if twin[place][0] == twin[place - 1][0]:
            before = inside_order.date_key(twin[place - 1][1])
            after = inside_order.date_key(twin[place][1])
            if before is not None and after is not None and after < before:
                out_of_time += 1
    assert out_of_time == 0
