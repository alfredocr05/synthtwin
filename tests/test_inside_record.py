"""Gate file of lane IN-0 (plan P4-D495): the inside record's contract, its bounded size and the canary.

THE CONTRACT. A record's first line is the protected marker, exactly,
and its body one line of JSON naming its format, version and mode; the
writer writes nothing else, and the loader refuses a file whose first
line is anything else, a mode other than `inside` (the strict
description is retired and is never an inside record) and a body it
cannot read, quoting nothing of it.

THE BOUND. A record is a model, never data: doubling the rows of three
invented tables (the cohort, the visits and the laboratory table of the
reliability battery, 20,000 against 40,000 rows) moves its size by under
5 per cent, no list in it is longer than the quantile grid, and no
record number of the table is in it.

THE CANARY. An invented value of an invented table is in the record and
nowhere else: not in what the zone's functions print, log or raise, not
in the export, not in any file written outside the private folder.

Each clause is red on its mutant (lane IN-0's report).
"""

from __future__ import annotations

import io
import json
import logging
import os
import pathlib

import pytest

import reliability_tables as T
from synthtwin import inside, installation


def _places(root: pathlib.Path) -> inside.Places:
    home = pathlib.Path(root, "home")
    return inside.Places(pathlib.Path(home, "data", "synthtwin", "inside"), (pathlib.Path(root, "tmp"),),
                         (pathlib.Path(home, "Downloads"),), installation.system_name(), ())


def _columns(text: str) -> "dict[str, list[str]]":
    import csv

    rows = list(csv.reader(io.StringIO(text)))
    header, body = rows[0], rows[1:]
    return {name: [row[i] for row in body] for i, name in enumerate(header)}


def _identifiers(table: str) -> "tuple[str, ...]":
    return tuple(name for name, known in T.KNOWS[table].items() if known == "identifier")


def test_the_record_s_first_line_is_the_marker_and_its_body_one_line(tmp_path: pathlib.Path) -> None:
    places = _places(tmp_path)
    record = inside.build_record(_columns(T.text("T8", 600, 1)), _identifiers("T8"))
    written = inside.write_record(record, inside.record_path("attributes", places), places)
    lines = written.path.read_text(encoding="utf-8").split("\n")
    assert lines[0] == inside.MARKER
    assert len(lines) == 3 and lines[2] == ""
    body = json.loads(lines[1])
    assert body["format"] == inside.FORMAT and body["version"] == inside.VERSION and body["mode"] == inside.MODE
    assert written.size == written.path.stat().st_size
    assert inside.load_record(written.path) == body
    assert inside.carries_marker(written.path)


def test_the_loader_refuses_a_file_without_the_marker(tmp_path: pathlib.Path) -> None:
    places = _places(tmp_path)
    record = inside.build_record(_columns(T.text("T8", 600, 1)), _identifiers("T8"))
    body = json.dumps(record)
    bare = pathlib.Path(tmp_path, "bare.json")
    bare.write_text(body + "\n", encoding="utf-8", newline="\n")
    late = pathlib.Path(tmp_path, "late.txt")
    late.write_text("\n" + inside.MARKER + "\n" + body + "\n", encoding="utf-8", newline="\n")
    for path in (bare, late):
        with pytest.raises(inside.InsideError, match="protected marker"):
            inside.load_record(path)
        assert not inside.carries_marker(path)
    marked = pathlib.Path(tmp_path, "marked-with-a-byte-order-mark.txt")
    marked.write_bytes(b"\xef\xbb\xbf" + (inside.MARKER + "\n" + body + "\n").encode("utf-8"))
    assert inside.carries_marker(marked)
    assert inside.load_record(marked)["mode"] == inside.MODE
    assert places.private.exists() is False


@pytest.mark.parametrize("mode", ["strict", "", None])
def test_the_mode_field_holds_the_one_mode(tmp_path: pathlib.Path, mode: "str | None") -> None:
    places = _places(tmp_path)
    record = inside.build_record(_columns(T.text("T8", 600, 1)), _identifiers("T8"))
    changed = dict(record)
    if mode is None:
        changed.pop("mode")
    else:
        changed["mode"] = mode
    target = inside.record_path("attributes", places)
    with pytest.raises(inside.InsideError, match="mode"):
        inside.write_record(changed, target, places)
    assert not target.exists()
    by_hand = pathlib.Path(tmp_path, "by-hand.txt")
    by_hand.write_text(inside.MARKER + "\n" + json.dumps(changed) + "\n", encoding="utf-8", newline="\n")
    with pytest.raises(inside.InsideError, match="mode"):
        inside.load_record(by_hand)


def test_the_writer_never_writes_over_a_file_that_is_no_record(tmp_path: pathlib.Path) -> None:
    places = _places(tmp_path)
    target = inside.record_path("attributes", places)
    target.parent.mkdir(mode=0o700, parents=True)
    if installation.system_name() != "nt":
        for folder in (target.parent, places.private):
            folder.chmod(0o700)
    target.write_text("a file of the person's own\n", encoding="utf-8", newline="\n")
    record = inside.build_record(_columns(T.text("T8", 600, 1)), _identifiers("T8"))
    with pytest.raises(inside.InsideError, match="not an inside record"):
        inside.write_record(record, target, places)
    assert target.read_text(encoding="utf-8") == "a file of the person's own\n"
    target.unlink()
    first = inside.write_record(record, target, places)
    again = inside.write_record(record, target, places)
    assert first.size == again.size and inside.load_record(target) == record


def _lists(value: object) -> "list[int]":
    if isinstance(value, list):
        return [len(value)] + [n for item in value for n in _lists(item)]
    if isinstance(value, dict):
        return [n for item in value.values() for n in _lists(item)]
    return []


def test_the_record_s_size_follows_columns_and_levels_never_rows() -> None:
    """Three invented tables at the owner's table floor and at twice it: the record grows by under 5 per cent."""
    for table in ("T1", "T2", "T6"):
        sizes = []
        for rows in (20_000, 40_000):
            text = T.text(table, rows, 1)
            columns = _columns(text)
            record = inside.build_record(columns, _identifiers(table))
            written = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            sizes += [len(written.encode("utf-8"))]
            assert max(_lists(record)) <= inside.GRID
            for name in _identifiers(table):
                assert record["zones"]["marginals"][name]["kind"] == "identifier"  # type: ignore[index]
                for value in sorted(set(columns[name]))[:200]:
                    assert value not in written, f"{table}: a record number of {name} is in the record"
        assert sizes[1] <= 1.05 * sizes[0], f"{table}: {sizes[0]} bytes at 20,000 rows, {sizes[1]} at 40,000"


def test_a_date_keeps_its_quantiles_weekdays_and_minutes() -> None:
    import datetime

    first = datetime.date(1999, 12, 25)
    for step in range(0, 12_000, 7):
        day = first + datetime.timedelta(days=step + step % 5)
        assert inside._weekday(day.isoformat()) == day.weekday()
    cells = ["2024-02-26 07:30", "2024-02-27 07:45", "2024-03-02 23:59", ""]
    entry = inside.build_record({"start": cells})["zones"]["marginals"]["start"]  # type: ignore[index]
    assert entry["kind"] == "date" and entry["empty"] == 1
    assert entry["weekdays"] == {"0": 1, "1": 1, "5": 1} and entry["minutes"] == {"450": 1, "465": 1, "1439": 1}
    assert len(entry["quantiles"]) == inside.GRID and entry["quantiles"][0] == "2024-02-26"


CANARY = "Zq7-canary-label-not-to-leave"


def _canary_table() -> str:
    """The invented cohort of 600 rows with an invented label on three rows of an invented column."""
    lines = T.text("T8", 600, 3).splitlines()
    out = [lines[0] + ",service_note"]
    for i, line in enumerate(lines[1:]):
        out += [line + "," + (CANARY if i in (5, 250, 512) else ("routine" if i % 2 else "review"))]
    return "\n".join(out) + "\n"


def _every_file_outside(root: pathlib.Path, private: pathlib.Path) -> "list[pathlib.Path]":
    found: "list[pathlib.Path]" = []
    for folder, _subfolders, names in os.walk(root):
        for name in names:
            path = pathlib.Path(folder, name)
            if private not in path.parents:
                found += [path]
    return found


def test_the_canary_stays_in_the_record(tmp_path: pathlib.Path, capfd: pytest.CaptureFixture[str],
                                        caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG)
    places = _places(tmp_path)
    shared = pathlib.Path(tmp_path, "home", "work", "out")
    shared.mkdir(parents=True)
    table = pathlib.Path(tmp_path, "home", "work", "attributes.csv")
    table.write_text(_canary_table(), encoding="utf-8", newline="\n")
    record = inside.build_record(_columns(table.read_text(encoding="utf-8")), _identifiers("T8"))
    written = inside.write_record(record, inside.record_path("attributes", places), places)
    assert CANARY in written.path.read_text(encoding="utf-8"), "the record must hold the canary for this case to mean anything"
    said: "list[str]" = [inside.describe(written.path)]
    print(said[0])
    assert inside.load_record(written.path)["mode"] == inside.MODE
    # every refusal of the zone, said in words
    damaged = pathlib.Path(places.private, "damaged" + inside.SUFFIX)
    text = written.path.read_text(encoding="utf-8")
    damaged.write_text(text[: text.index(CANARY) + len(CANARY) + 3], encoding="utf-8", newline="\n")
    wrong_mode = pathlib.Path(places.private, "wrong-mode" + inside.SUFFIX)
    wrong_mode.write_text(text.replace('"mode":"inside"', '"mode":"strict"'), encoding="utf-8", newline="\n")
    no_marker = pathlib.Path(shared, "attributes-profile.json")
    no_marker.write_text(text.split("\n", 1)[1], encoding="utf-8", newline="\n")
    for bad in (damaged, wrong_mode, no_marker):
        with pytest.raises(inside.InsideError) as refused:
            inside.load_record(bad)
        said += [str(refused.value)]
    for target in (pathlib.Path(tmp_path, "tmp", "x" + inside.SUFFIX), pathlib.Path(shared, "x" + inside.SUFFIX)):
        with pytest.raises(inside.InsideError) as refused:
            inside.write_record(record, target, places)
        said += [str(refused.value)]
    # the export: the twin and its report leave, the record and the description do not
    pathlib.Path(shared, "attributes-twin.csv").write_text("person,service_note\nP1,routine\n", encoding="utf-8", newline="\n")
    pathlib.Path(shared, "attributes-twin-report.txt").write_text("twin report\n", encoding="utf-8", newline="\n")
    copied = inside.export(shared, pathlib.Path(tmp_path, "home", "outbox"))
    assert sorted(path.name for path in copied) == ["attributes-twin-report.txt", "attributes-twin.csv"]
    captured = capfd.readouterr()
    for words in said + [captured.out, captured.err, caplog.text]:
        assert CANARY not in words
    no_marker.unlink()
    for path in _every_file_outside(tmp_path, places.private):
        if path == table:
            continue
        assert CANARY.encode("utf-8") not in path.read_bytes(), f"{path} holds the canary"
