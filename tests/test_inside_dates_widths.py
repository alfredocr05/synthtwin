"""Gate file of the Windows bundle workflow's trial on the inside record's route: a made-up date's field widths.

The trial of `.github/workflows/windows-bundle.yml` runs the commands a
person types on the bundle's invented visits table
(`tools/bundle/invented_windows_table.py`: 20,000 rows, 1,000 people,
`visit_date` written month/day/year without leading zeros). With the
inside record on for the shipped route (plan P4-D503) the twin's dates
come from the record's dates zone (lane IN-5, plan P4-D497), each date
taking one of the description's twin's spellings (lane IN-2b). A
spelling's width word is read off ONE cell and says only what that
cell's fields could show: a field of ten or more shows no width, so
`7/29/2021` is counted `first-field-unpadded`. Dealt to a made-up date
whose day is below ten, the field the word never decided took the
padded default, so 1,460 of the twin's 20,000 dates were written
`7/03/2021`, a convention neither the table nor the description's twin
holds, and `synthtwin validate` missed the column's width census (its one
published word and the unnamed remainder): exit 3, the trial failed.

* THE COLUMN'S UNPADDED FIELDS STAY UNPADDED: the zone's writer, with the
  description's twin's cells given and without them, and the writer of
  dates among other values, never pad a field of a column no cell of
  which pads one.
* A COLUMN WRITTEN BOTH WAYS NEVER MIXES THE TWO IN ONE CELL, and the
  share of padded cells among those showing both fields stays the
  description's twin's.
* THROUGH THE COMMANDS, the bundle's invented visits table at the table
  floor: the twin is drawn from the record (its report names
  `visit_date` among the drawn columns), no twin date pads a field, and
  validate misses nothing (exit 0).

MUTANTS (each red here): `_width_written` returning the dealt word as it
stands (the code before this fix); its agreement step removed (the
heaviest word of the pool whatever the dealt word decided).
"""

from __future__ import annotations

import contextlib
import csv
import datetime
import importlib.util
import io
import pathlib
import random
import sys

import pytest

import reliability_battery as B
from synthtwin import cli, inside, inside_dates, installation, parsing

REPO = pathlib.Path(__file__).resolve().parents[1]
NAME = "visit_date"
MEMBER = "month-first-date"
ROWS = 4000
# The width words a cell written month/day/year without leading zeros can show.
UNPADDED_WORDS = {parsing.WIDTH_UNPADDED, parsing.WIDTH_FIRST_FIELD_UNPADDED, parsing.WIDTH_SECOND_FIELD_UNPADDED}
# The words of a cell whose two fields are written at different widths.
MIXED_WORDS = {parsing.WIDTH_FIRST_PADDED, parsing.WIDTH_SECOND_PADDED}


def _dates(rows: int, seed: int, padded_share: float) -> "list[str]":
    """Invented dates over three years, each row written padded (`03/05/2021`) at `padded_share`, else `3/5/2021`."""
    rng = random.Random(seed)
    first = datetime.date(2021, 1, 1)
    cells: "list[str]" = []
    for _ in range(rows):
        day = first + datetime.timedelta(days=rng.randrange(1095))
        if rng.random() < padded_share:
            cells += [f"{day.month:02d}/{day.day:02d}/{day.year}"]
        else:
            cells += [f"{day.month}/{day.day}/{day.year}"]
    return cells


def _words(cells: "list[str]") -> "dict[str, int]":
    """How many cells show each width word (a cell showing none is not counted)."""
    counted: "dict[str, int]" = {}
    for cell in cells:
        word = parsing.date_field_style(cell, MEMBER) if cell else None
        if word is not None:
            counted[word] = (counted[word] if word in counted else 0) + 1
    return counted


# The padded and the unpadded word of each kind of cell: both fields below ten, the first alone, the second alone.
KINDS = (
    (parsing.WIDTH_PADDED, parsing.WIDTH_UNPADDED),
    (parsing.WIDTH_FIRST_FIELD_PADDED, parsing.WIDTH_FIRST_FIELD_UNPADDED),
    (parsing.WIDTH_SECOND_FIELD_PADDED, parsing.WIDTH_SECOND_FIELD_UNPADDED),
)


def _padded_shares(cells: "list[str]") -> "list[float]":
    """For each kind of cell (`KINDS`), the share of its cells written padded."""
    words = _words(cells)
    shares: "list[float]" = []
    for padded_word, unpadded_word in KINDS:
        padded = words[padded_word] if padded_word in words else 0
        unpadded = words[unpadded_word] if unpadded_word in words else 0
        shares += [padded / max(1, padded + unpadded)]
    return shares


def test_a_made_up_date_keeps_the_column_s_unpadded_fields() -> None:
    cells = _dates(ROWS, 1, 0.0)
    zone = inside_dates.build_zone({NAME: cells})
    assert zone["columns"][NAME]["reading"]["member"] == MEMBER  # type: ignore[index]
    given = inside_dates.write_dates(zone, ROWS, seed=3, months={NAME: cells})[NAME]
    drawn = inside_dates.write_dates(zone, ROWS, seed=3)[NAME]
    for written in (given, drawn):
        assert len(written) == ROWS
        found = _words(written)
        assert set(found) <= UNPADDED_WORDS, found
        # The case reaches cells showing a field below ten: a made-up day under ten on most of them.
        assert sum(found.values()) > ROWS // 2, found


def test_dates_among_other_values_keep_the_column_s_unpadded_fields() -> None:
    rng = random.Random(5)
    dates = _dates(ROWS, 2, 0.0)
    cells = [dates[row] if rng.random() < 0.3 else f"{rng.uniform(1, 400):.1f}" for row in range(ROWS)]
    zone = inside_dates.build_zone({"result": cells})
    assert "result" not in zone["columns"] and "result" in zone["mixed"]  # type: ignore[operator]
    written = inside_dates.rewrite_mixed(zone, "result", cells, seed=4)
    dated = [row for row in range(ROWS) if cells[row].count("/") == 2]
    assert len(dated) > ROWS // 5
    found = _words([written[row] for row in dated])
    assert set(found) <= UNPADDED_WORDS, found
    assert sum(found.values()) > len(dated) // 2, found


def test_a_column_written_both_ways_keeps_each_way_and_never_mixes_them_in_one_cell() -> None:
    for padded_share in (0.3, 0.7):
        cells = _dates(ROWS, 6, padded_share)
        zone = inside_dates.build_zone({NAME: cells})
        given = inside_dates.write_dates(zone, ROWS, seed=8, months={NAME: cells})[NAME]
        drawn = inside_dates.write_dates(zone, ROWS, seed=8)[NAME]
        real = _padded_shares(cells)
        for written in (given, drawn):
            found = _words(written)
            assert not set(found) & MIXED_WORDS, found
            # On each kind of cell (both fields below ten, the first alone, the second alone) the share written
            # padded stays the description's twin's (here the table's own cells), whether the twin's cells are
            # given or the zone's census is drawn: the 0.32 of the second field alone read 0.81 where a field the
            # dealt word never decided was kept at the padded default, and 0.06 where it took the heaviest word.
            shares = _padded_shares(written)
            assert all(abs(shares[k] - real[k]) < 0.08 for k in range(len(KINDS))), (padded_share, shares, real)


def test_a_field_the_dealt_word_never_decided_follows_the_one_it_did() -> None:
    """A spelling read off `3/15/2021` decided only the first field (unpadded); on a made-up `3/5/2021` its second
    field is written as the column's cells unpadded in the first write it, never at the padded default, and never
    by the column's commonest convention alone."""
    pools = {inside_dates.WIDTH_BOTH: {parsing.WIDTH_PADDED: 70, parsing.WIDTH_UNPADDED: 30},
             inside_dates.WIDTH_FIRST: {parsing.WIDTH_FIRST_FIELD_PADDED: 70, parsing.WIDTH_FIRST_FIELD_UNPADDED: 30},
             inside_dates.WIDTH_SECOND: {parsing.WIDTH_SECOND_FIELD_PADDED: 70,
                                         parsing.WIDTH_SECOND_FIELD_UNPADDED: 30}}
    state = [12345]
    for _ in range(200):
        assert inside_dates._width_written(parsing.WIDTH_FIRST_FIELD_UNPADDED, parsing.WIDTH_FIRST_FIELD_PADDED, 3, 5,
                                           MEMBER, pools, state) == parsing.WIDTH_UNPADDED
        assert inside_dates._width_written(parsing.WIDTH_FIRST_FIELD_PADDED, parsing.WIDTH_FIRST_FIELD_PADDED, 3, 5,
                                           MEMBER, pools, state) == parsing.WIDTH_PADDED
    # A word that decides every field the date shows, written as the column writes it, stands as dealt.
    assert inside_dates._width_written(parsing.WIDTH_FIRST_FIELD_UNPADDED, "", 3, 15, MEMBER, pools,
                                       state) == parsing.WIDTH_FIRST_FIELD_UNPADDED
    # A column no cell of which pads a field: the one word its cells showing both fields are written with.
    unpadded = {inside_dates.WIDTH_BOTH: {parsing.WIDTH_UNPADDED: 9},
                inside_dates.WIDTH_FIRST: {parsing.WIDTH_FIRST_FIELD_UNPADDED: 9},
                inside_dates.WIDTH_SECOND: {parsing.WIDTH_SECOND_FIELD_UNPADDED: 9}}
    for word in ("", parsing.WIDTH_FIRST_FIELD_UNPADDED, parsing.WIDTH_SECOND_FIELD_UNPADDED, parsing.WIDTH_PADDED):
        for month, day in ((7, 3), (12, 2), (3, 12)):
            chosen = inside_dates._width_written(word, parsing.WIDTH_FIRST_FIELD_UNPADDED, month, day, MEMBER,
                                                 unpadded, state)
            written = parsing.written_date(2021, month, day, MEMBER, chosen)
            assert written == f"{month}/{day}/2021", (word, month, day, chosen, written)


# -- through the commands, the bundle's own invented table -------------------------------------------------------


def _load(name: str, relative: str):  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location(name, REPO / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _places(folder: pathlib.Path) -> inside.Places:
    return inside.Places(pathlib.Path(folder, "installation", "synthtwin", "inside"), (), (),
                         installation.system_name(), ())


def _command(argv: "list[str]") -> int:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return int(cli.main(argv, small_tables_refused=True))


def test_the_bundle_s_visits_table_validates_on_the_inside_record_s_route(tmp_path: pathlib.Path) -> None:
    sys.path.insert(0, str(REPO / "tools" / "bundle"))
    try:
        table = _load("invented_windows_table", "tools/bundle/invented_windows_table.py")
        rehearse = _load("rehearse_windows", "tools/bundle/rehearse_windows.py")
    finally:
        sys.path.remove(str(REPO / "tools" / "bundle"))
    answers = rehearse.fill_answers
    folder = tmp_path / "product"
    work = folder / "work"
    source = table.write(work)[0]
    stem = source.stem
    questions = work / f"{stem}-questions.json"
    description = work / f"{stem}-profile.json"
    twin = work / f"{stem}-twin.csv"
    person = ["--person", rehearse.PERSON]
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inside, "default_places", lambda: _places(folder))
        assert cli._inside_record_switched_on()
        with B.installed(folder):
            assert _command(["profile", f"{source}", *person, "--out-dir", f"{work}"]) == 0
            for _round in range(rehearse.ROUNDS):
                document = answers.load(questions)
                chosen, problems = answers.choose(document, rehearse.ANSWERS)
                assert not problems, problems
                if not chosen:
                    break
                answers.write_json(questions, document)
                assert _command(["profile", f"{source}", *person, "--out-dir", f"{work}", "--answers",
                                 f"{questions}", "--replace"]) == 0
            assert _command(["generate", f"{description}", "--out-dir", f"{work}", "--seed", rehearse.SEED]) == 0
            code = _command(["validate", f"{description}", "--twin", f"{twin}"])
    report = (work / f"{stem}-twin-report.txt").read_text(encoding="utf-8")
    assert report.startswith(cli._INSIDE_REPORT_HEAD), report[:300]
    assert NAME in cli._drawn_in_report(report), report[:300]
    with open(twin, encoding="utf-8-sig", newline="") as handle:
        rows = csv.reader(handle)
        head = next(rows)
        place = head.index(NAME)
        dates = [row[place] for row in rows]
    assert len(dates) == 20000
    found = _words(dates)
    assert set(found) <= UNPADDED_WORDS, found
    quality = (work / f"{stem}-twin-quality.txt").read_text(encoding="utf-8")
    assert rehearse.missed(quality) == 0, [line for line in quality.splitlines() if "MISSED" in line][:6]
    assert code == 0
