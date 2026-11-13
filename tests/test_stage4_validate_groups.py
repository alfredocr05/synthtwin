"""Lane SV of the December plan: `synthtwin validate` reads the checked file in groups of columns (plan P4-D476).

THE GATE. Read whole, `synthtwin validate` held the checked twin's bytes,
its text and a Python text object a cell -- about 4.4 KB a row of the
made-up 50-column health table, about 9 GB at 2,000,000 x 50 -- because
its `reading.read_table` call passed no ``in_groups``. A delimited file
past 25.6 MiB (its bytes ten times over past `reading.GROUP_BYTES`) is
now read as `synthtwin profile` reads a table (lane SR, plan P4-D400): a
line at a time, one group of columns at a time, every column asked of
`reading.column_values`; the three rewrites the check makes of the table
it describes and counts (the Safe Harbor ages and years, the published
grains) are made of each column as it is asked for
(`validation.column_as_checked`); the form checks ask the file's encoding
a line at a time and read a column again where the survey of a file read
in groups holds no cell. A smaller file, and every workbook, is read
whole, as before. EVERY BYTE IT WRITES AND PRINTS IS UNCHANGED.

WHAT THIS FILE PINS, every claim of a file read in groups of ONE column
(`GROUP_BYTES` and `WALK_BYTES` at 1, the most groups there are, and so
every file past the size rule) against the same file read in one group,
which runs the code of a table read whole (the lane's own cases compare
the head with the base, byte for byte):

1. A GENERATED SWEEP AT THE UNIT LEVEL: every column of a table read in
   groups and handed through the rewrites is the column the rewrites make
   of the table read whole -- ages, top categories pooled in people beside
   the subject columns they are counted in, years, grains -- over seeded
   cells of every spelling the rewrites read (blanks, built-in and declared
   spellings of no value, decimal commas, placeholders, past 125); and the
   encoding words asked of a file a line at a time are those asked of its
   bytes, over seeded bytes in every published encoding.
2. The table level: the quality report, the screen and the exit code of
   `synthtwin validate` read in groups of one column are those read in one
   group, on every written form the reader knows (lane SR's shapes), on
   files the reader refuses, on a table whose dates are published at a
   grain beside a person column, with the chain's switch on a switched
   description holding a top-coded age, and on ONE table of 20,000 rows
   whose ages, years and dates the check rewrites. The form checks a file
   read in groups asks of the file again, each on a file checked against
   ANOTHER file's description so that the check finds something (skeptic
   1 of lane SV, item 1): the quoting by class of a column quoted all one
   way, the first record of a headerless file, a row order broken inside
   one published grain, and a workbook with its twin.
3. Read in groups, the checked file's bytes and text are never read whole
   (`pathlib.Path.read_bytes` refused while it is checked), and a check
   stopped by a file changed between two readings leaves no file behind.
4. K-S4-23's driver, machine-free: each size's peak, CPU seconds and
   instructions the largest of three runs; the peak projected only from
   three sizes of 100,000 rows or more, the largest reaching 1,000,000,
   as lane B0 projects (and only then K-S4-09's validate keys), else the
   lines through each two sizes recorded and the entry held OPEN; every
   file either run wrote, the screen and the exit compared (the
   statistics skeptic of lane SV, items 2, 4 and 8; the combined verify
   of its repair 1, items 3 and 5). Its evidence withheld, never
   favourable by accident (Codex's review of lane SV, LANE SV RULINGS 3):
   a generated check of every combination of a validation that did not
   complete, a memory counter that read nothing, a pair of another size
   and a size list that cannot carry the projection; the size list read
   before any work; a kept pair used only where its record holds; and
   `run` never clearing a folder it is handed.
5. BATCH 4s'S MERGE OF THIS LANE (step 10; plan P4-D476's merge
   paragraph): the line's top-coded readings -- the age words and the
   ends of lane HB2 (plan P4-D477), the bands past 89 of lane CZ-E
   (plan P4-D472) -- made in groups as they are made whole, at the unit
   level over 48 generated tables (red on the merge as git wrote it,
   whose grouped branch handed the column over without them, and on
   the mutant dropping each of the three), and at the table level on
   two generated tables of the line's top-coded and time shapes (ends
   in each unit and top categories pooled in people at the table
   floor, worded ages, bands, stamps under their rule at a grain, clock
   figures, years of birth): the same exit, screen and files, and the
   checked file never read whole while it is read in groups.
"""

from __future__ import annotations

import contextlib
import csv
import datetime
import hashlib
import io
import itertools
import json
import os
import pathlib
import random
import shutil
import typing

import pytest

import chain_twins
import kpi_rules
import lowered_floor
import test_stage4_describe_groups as groups_gate
import workbooks

from synthtwin import asking, cli, contract, dialect, errors, profile, reading, taxonomy, validation


def _one_column_a_group(monkeypatch: pytest.MonkeyPatch) -> None:
    """One column a group and a group a walk: the finest the reading goes (lane SR's gate)."""
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    monkeypatch.setattr(reading, "WALK_BYTES", 1)


def _written(path: pathlib.Path, header: "list[str]", columns: "list[list[str]]") -> pathlib.Path:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for row in range(len(columns[0])):
            writer.writerow([column[row] for column in columns])
    return path


def _read_both(path: pathlib.Path) -> "tuple[reading.Table, reading.Table]":
    whole = reading.read_table(str(path), reading.FIRST_ROW_NAMES)
    with pytest.MonkeyPatch.context() as groups:
        _one_column_a_group(groups)
        grouped = reading.read_table(str(path), reading.FIRST_ROW_NAMES, in_groups=True)
    assert grouped.source is not None and grouped.columns == []
    return whole, grouped


def _columns(table: reading.Table) -> "list[list[str]]":
    return [list(reading.column_values(table, place)) for place in range(len(table.column_names))]


# -- 1. the generated sweep at the unit level --------------------------------

_AGE_SPELLINGS = ["", " ", "NA", "N/A", "-1", "999", "unknown", "90+", " 95", "95.5", "89.9", "1,05", "126", "0"]


def _age_cells(draw: random.Random, rows: int, comma: bool) -> "list[str]":
    cells: "list[str]" = []
    for _row in range(rows):
        pick = draw.random()
        if pick < 0.55:
            cells += [f"{draw.randrange(0, 89)}"]
        elif pick < 0.85:
            value = draw.randrange(89, 140)
            cells += [f"{value},5" if comma and draw.random() < 0.3 else f"{value}"]
        else:
            cells += [draw.choice(_AGE_SPELLINGS)]
    return cells


def _year_cells(draw: random.Random, rows: int) -> "list[str]":
    spellings = ["", "NA", "0000", "1850", "1849", "2031", "19x5", " 1920"]
    return [
        f"{draw.randrange(1820, 2030)}" if draw.random() < 0.85 else draw.choice(spellings)
        for _row in range(rows)
    ]


def test_a_column_as_checked_in_groups_is_the_column_the_rewrites_make_of_the_whole_table(
    tmp_path: pathlib.Path,
) -> None:
    """Seeded tables: ages, pooled top categories beside their subject columns, years -- read in groups and whole."""
    draw = random.Random(20261109)
    compared = 0
    for case in range(60):
        rows = draw.randrange(20, 160)
        people = [f"P{draw.randrange(10 ** 4):04d}" for _ in range(max(2, rows // draw.choice([1, 3, 8])))]
        width = draw.randrange(2, 7)
        header: "list[str]" = []
        columns: "list[list[str]]" = []
        marks: "dict[str, int]" = {}
        years: "dict[str, int]" = {}
        commas: "list[str]" = []
        for place in range(width):
            kind = draw.choice(["age", "age", "year", "person", "other"])
            name = f"{kind}_{place}"
            header += [name]
            if kind == "age":
                comma = draw.random() < 0.2
                if comma:
                    commas += [name]
                columns += [_age_cells(draw, rows, comma)]
                marks[name] = draw.choice(taxonomy.TOP_CODE_MARKS) if draw.random() < 0.3 else taxonomy.TOP_CODE
            elif kind == "year":
                columns += [_year_cells(draw, rows)]
                years[name] = draw.choice([1934, 1937, 1940])
            elif kind == "person":
                columns += [[draw.choice(people) if draw.random() < 0.95 else "" for _ in range(rows)]]
            else:
                columns += [[f"{draw.gauss(5, 2):.1f}" for _ in range(rows)]]
        subjects = tuple(name for name in header if name.startswith("person"))
        pooled: "dict[str, tuple[int, tuple[str, ...]]]" = {}
        for name in marks:
            if draw.random() < 0.6:
                pooled[name] = (draw.choice([3, 11]), subjects if subjects and draw.random() < 0.7 else ())
        declared = tuple(draw.sample(["999", "-1", "unknown", "NA"], draw.randrange(0, 3)))
        path = _written(tmp_path / f"case{case}.csv", header, columns)
        whole, grouped = _read_both(path)
        whole_checked = validation._year_top_coded_table(
            validation._top_coded_table(whole, marks, pooled, commas, declared, declared),
            years, commas, declared,
        )
        grouped_checked = validation._year_top_coded_table(
            validation._top_coded_table(grouped, marks, pooled, commas, declared, declared),
            years, commas, declared,
        )
        if marks or years:
            assert grouped_checked.source is not None and grouped_checked.source.rewrites
        assert _columns(grouped_checked) == _columns(whole_checked), (case, header)
        # ...and the reading underneath is untouched: the cells as read.
        assert [reading.column_as_read(grouped_checked, place) for place in range(width)] == _columns(whole)
        compared += width
    assert compared >= 200


def _visits_table(rows: int, patients: int, seed: int) -> str:
    """Visits (tests/test_dates_pooled_in_people.py's shape): a patient key, a day of each visit over two years, a measurement."""
    draw = random.Random(seed)
    lines = ["patient,seen,value"]
    picked = []
    for _row in range(rows):
        picked += [(draw.randrange(patients), datetime.date(2023, 1, 1) + datetime.timedelta(days=draw.randrange(730)))]
    for person, day in picked:
        lines += [f"REC{80000000 + 7 * person:08d},{day.isoformat()},{draw.uniform(3, 150):.1f}"]
    return "\n".join(lines) + "\n"


def _described(folder: pathlib.Path, table: pathlib.Path, *options: str) -> pathlib.Path:
    screen = io.StringIO()
    with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        code = lowered_floor.main(["profile", str(table), "--out-dir", str(folder), "--replace", *options])
    assert code == 0, screen.getvalue()[-2000:]
    return folder / f"{table.stem}-profile.json"


def test_a_column_at_its_grain_in_groups_is_the_column_put_at_its_grain_whole(
    tmp_path: pathlib.Path,
) -> None:
    """A published grain (P4-D417) applied to seeded columns of dates, with seeded spellings the reading took as no value."""
    table = tmp_path / "visits.csv"
    table.write_text(_visits_table(600, 200, 11), encoding="utf-8", newline="\n")
    described = contract.load_profile(f"{_described(tmp_path, table, '--identifier', 'patient')}")
    grained = validation.published_grains(described)
    assert "seen" in grained, "the visits' dates are published at a grain"
    draw = random.Random(4)
    moved = 0
    for case in range(12):
        rows = draw.randrange(30, 200)
        first = datetime.date(2022, 12, 1)
        cells = []
        for _row in range(rows):
            day = first + datetime.timedelta(days=draw.randrange(500))
            cells += [draw.choice([day.isoformat(), day.isoformat(), day.strftime("%m/%d/%Y"), "", "unknown", "1900-01-01", "2023-02-30"])]
        path = _written(tmp_path / f"grain{case}.csv", ["patient", "seen", "value"], [
            [f"REC{80000000 + 7 * draw.randrange(50):08d}" for _ in range(rows)], cells, [f"{draw.random():.2f}" for _ in range(rows)],
        ])
        absent_read = {"seen": tuple(draw.sample(["1900-01-01", "unknown", "2023-02-30"], draw.randrange(0, 3)))}
        whole, grouped = _read_both(path)
        expected = validation._at_their_grains(whole, grained, described, absent_read)
        found = validation._at_their_grains(grouped, grained, described, absent_read)
        assert _columns(found) == _columns(expected), case
        moved += sum(1 for at, cell in enumerate(_columns(expected)[1]) if cell != _columns(whole)[1][at])
    assert moved, "the grain rewrites cells"


_ENCODED_ALPHABET = [b"a", b"1", b",", b"\n", b"\r\n", b"\xe9", b"\xc3\xa9", b"\xe2\x82\xac", b"\x81", b"\x93", b"\xff",
                     b"\xfe", b"\x00", b"\xef\xbb\xbf", b"\xf0\x9f\x98\x80", b"\xed\xa0\x80", b"\xc3"]


def test_the_encoding_words_asked_of_a_file_are_those_asked_of_its_bytes(tmp_path: pathlib.Path) -> None:
    """Seeded byte strings, every published encoding, with and without a description's characters."""
    draw = random.Random(31)
    path = tmp_path / "bytes.csv"
    latin = tmp_path / "latin.csv"
    latin.write_bytes(_FORMS["latin-1"][0])
    described = contract.load_profile(f"{_described(tmp_path, latin, '--smallest-group', '3')}")
    found: "dict[str, int]" = {}
    for case in range(400):
        data = b"".join(draw.choice(_ENCODED_ALPHABET) for _ in range(draw.randrange(0, 40)))
        if draw.random() < 0.15:
            data = draw.choice([b"\xff\xfe", b"\xfe\xff"]) + data
        path.write_bytes(data)
        for encoding in dialect.ENCODINGS:
            for description in (None, described):
                words = validation._encoding_found(data, encoding, description)
                assert validation._encoding_found(path, encoding, description) == words, (case, data, encoding)
                found[words] = found.get(words, 0) + 1
    assert len(found) >= 8, found


# -- 2. the table level -------------------------------------------------------

# Every written form lane SR's gate reads (`test_stage4_describe_groups._SHAPES`), at 150 records so a
# description of each is made (the population floor of 100 rows, plan P4-D341).
_ROWS = range(150)
_FORMS: "dict[str, tuple[bytes, str]]" = {
    "quoted line breaks": (
        b'id,note,score\r\n1,"two\nlines",3.5\r\n2,"x, y",4.5\r\n'
        + b"".join(f"{k},n{k % 3},{k}.5\r\n".encode() for k in range(3, 150)),
        "auto",
    ),
    "carriage returns alone": (b"a;b;c\r" + b"".join(f"{k};x{k % 4};{k * 3}\r".encode() for k in _ROWS), "auto"),
    "a title and a separator line": (
        b"sep=,\nExtract for unit 7\nrecord_id,age,arm\n"
        + b"".join(f"R{k:03d},{20 + k % 50},{'AB'[k % 2]}\n".encode() for k in _ROWS),
        "auto",
    ),
    "a utf-8 mark and an end-of-file mark": (
        b"\xef\xbb\xbfname,value\n" + b"".join(f"caf\u00e9{k % 5},{k}\n".encode("utf-8") for k in _ROWS) + b"\x1a",
        "auto",
    ),
    "utf-16 behind its mark": (
        b"\xff\xfe" + "id\tlabel\r\n".encode("utf-16-le") + "".join(f"{k}\tL{k % 4}\r\n" for k in _ROWS).encode("utf-16-le"),
        "auto",
    ),
    "windows-1252": (b"word,n\n" + b"".join(b"\x93q\x94" + f"{k % 3},{k}\n".encode() for k in _ROWS), "auto"),
    "latin-1": (b"word,n\n" + b"".join(b"\xe9t\xe9" + f"{k % 3},{k}\n".encode() for k in _ROWS), "auto"),
    "trailing delimiters": (b"a,b,c,\n" + b"".join(f"{k},{k * 2},{k % 3},\n".encode() for k in _ROWS), "auto"),
    "blank lines between records": (
        b"a,b\n1,2\n\n3,4\n   \n5,6\n" + b"".join(f"{k},{k}\n".encode() for k in range(7, 157)),
        "auto",
    ),
    "a first row said to be data": (b"x,y,z\n" + b"".join(f"{k},{k % 7},w{k % 2}\n".encode() for k in _ROWS), "data"),
    "records that hold nothing, and an order": (
        b"n,a,b\n" + b"".join((b",,\n" if k % 7 == 3 else f"{k},x{k % 3},{200 - k}\n".encode()) for k in range(170)),
        "auto",
    ),
    "every field quoted": (b'"p","q"\n' + b"".join(f'"{k}","t{k % 5}"\n'.encode() for k in _ROWS), "auto"),
    "comma-space": (b"a, b, c\n" + b"".join(f"{k}, x{k % 3},  {k}\n".encode() for k in _ROWS), "auto"),
    "a decimal comma under semicolons": (
        b"level;dose\n" + b"".join(f"{k % 40},{k % 10};{k % 4 * 5} mg\n".encode() for k in _ROWS),
        "auto",
    ),
}


def _validated(described: pathlib.Path, checked: pathlib.Path, out: pathlib.Path, chain: "cli.ChainRun | None" = None) -> "tuple[int, str, dict[str, bytes]]":
    out.mkdir(exist_ok=True)
    for old in out.iterdir():
        old.unlink()
    screen = io.StringIO()
    with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        if chain is None:
            code = lowered_floor.main(["validate", str(described), "--twin", str(checked), "--out-dir", str(out), "--replace"])
        else:
            code = cli.main(["validate", str(described), "--twin", str(checked), "--out-dir", str(out), "--replace"], chain=chain)
    return code, screen.getvalue(), {path.name: path.read_bytes() for path in sorted(out.iterdir())}


def _same_in_groups(
    described: pathlib.Path, checked: pathlib.Path, out: pathlib.Path, chain: "cli.ChainRun | None" = None,
) -> "tuple[int, str, dict[str, bytes]]":
    """The check in one group, then one column a group: the same exit, the same screen, the same files."""
    one_group = _validated(described, checked, out, chain)
    with pytest.MonkeyPatch.context() as groups:
        _one_column_a_group(groups)
        in_groups = _validated(described, checked, out, chain)
    assert in_groups == one_group, (checked.name, one_group[1][-1500:], in_groups[1][-1500:])
    return one_group


@pytest.mark.parametrize("shape", sorted(_FORMS))
def test_validate_in_groups_writes_and_says_what_it_does_in_one_group(
    shape: str, tmp_path: pathlib.Path
) -> None:
    """Every written form lane SR's gate reads: the table checked against its own description, and its twin."""
    data, first_row = _FORMS[shape]
    table = tmp_path / "shape.csv"
    table.write_bytes(data)
    options = ["--smallest-group", "3"] + (["--first-row", first_row] if first_row != "auto" else [])
    screen = io.StringIO()
    with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        code = lowered_floor.main(["profile", str(table), "--out-dir", str(tmp_path), "--replace", *options])
    assert code == 0, screen.getvalue()[-600:]
    described = tmp_path / "shape-profile.json"
    with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        made = lowered_floor.main(["generate", str(described), "--out-dir", str(tmp_path), "--seed", "0", "--replace"])
    checked = [table] + ([tmp_path / "shape-twin.csv"] if made == 0 else [])
    for path in checked:
        _same_in_groups(described, path, tmp_path / "out")


def test_files_the_reader_refuses_are_reported_alike_in_groups(
    tmp_path: pathlib.Path
) -> None:
    """Seeded files of lane SR's adversarial alphabet, checked against one description: refused or read, the same report."""
    table = tmp_path / "base.csv"
    table.write_text("c0,c1,c2\n" + "".join(f"{k},x{k % 3},{k * 2}\n" for k in _ROWS), encoding="utf-8", newline="\n")
    described = _described(tmp_path, table, "--smallest-group", "3")
    draw = random.Random(20261110)
    codes: "dict[int, int]" = {}
    for case in range(40):
        head = b"c0,c1,c2\n" if draw.random() < 0.6 else b""
        checked = tmp_path / f"fuzz{case}.csv"
        checked.write_bytes(head + b"".join(draw.choice(groups_gate._ALPHABET) for _ in range(draw.randrange(1, 50))))
        try:
            code = _same_in_groups(described, checked, tmp_path / "out")[0]
        except errors.ProfileError:
            code = -1
        codes[code] = codes.get(code, 0) + 1
    assert len(codes) >= 2, codes


def test_dates_at_a_grain_beside_a_person_column_validate_alike_in_groups(
    tmp_path: pathlib.Path
) -> None:
    """The grain rewrite at the table level: the table itself (cells off their buckets) and its twin."""
    table = tmp_path / "visits.csv"
    table.write_text(_visits_table(600, 200, 11), encoding="utf-8", newline="\n")
    described = _described(tmp_path, table, "--identifier", "patient")
    assert "time_grain" in described.read_text(encoding="utf-8")
    with contextlib.redirect_stdout(io.StringIO()):
        assert lowered_floor.main(["generate", str(described), "--out-dir", str(tmp_path), "--seed", "0", "--replace"]) == 0
    for checked in (table, tmp_path / "visits-twin.csv"):
        _same_in_groups(described, checked, tmp_path / "out")


def test_the_chain_s_lines_read_a_top_coded_age_alike_in_groups(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The chain's switch: the clinic's age published top-coded, checked on the table and on rows past 89."""
    for name in ("HOME", "APPDATA", "LOCALAPPDATA", "XDG_DATA_HOME"):
        monkeypatch.setenv(name, str(tmp_path / "home"))
    with monkeypatch.context() as floor:
        floor.setitem(cli.main.__kwdefaults__, "small_tables_refused", False)
        clinic = chain_twins.Described(tmp_path, chain_twins.HEADER, chain_twins._clinic_rows())
    assert '"top_coded"' in clinic.path.read_text(encoding="utf-8")
    older = [[f"{int(row[0]) + 9}" if int(row[0]) > 84 else row[0]] + row[1:] for row in chain_twins._clinic_rows()]
    aged = chain_twins._write(tmp_path / "aged.csv", chain_twins.HEADER, older)
    run = cli.ChainRun(rows_per_person=asking.ANSWER_ONE_ROW_EACH)
    for checked in (clinic.table, aged):
        with monkeypatch.context() as floor:
            floor.setitem(cli.main.__kwdefaults__, "small_tables_refused", False)
            code, said, written = _same_in_groups(clinic.path, checked, tmp_path / "out", chain=run)
        assert code in (0, 3) and written


# The form checks a file read in groups asks of the file again (skeptic 1 of lane SV, item 1), each on a
# file checked against ANOTHER file's description, so that the check has something to find.

_WORDS = ["alpha", "bravo", "cedar", "delta", "ember", "fable", "grove", "harbor"]


def _records(seed: int) -> "tuple[list[str], list[list[object]]]":
    """150 records: a record number, a count, a measurement, a word, a note of words and a dose."""
    draw = random.Random(seed)
    header = ["record_no", "count", "level", "kind", "note", "dose"]
    rows: "list[list[object]]" = []
    for row in _ROWS:
        rows += [[
            f"R{100000 + 3 * row:07d}", draw.randrange(0, 90), round(draw.gauss(5, 1.5), 2), draw.choice(_WORDS),
            " ".join(draw.choice(_WORDS) for _ in range(draw.randrange(1, 4))), draw.choice([5, 10, 20, 40]),
        ]]
    return header, rows


def _quoted(path: pathlib.Path, header: "list[str] | None", rows: "list[list[object]]", quoting: int) -> pathlib.Path:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n", quoting=quoting)
        if header is not None:
            writer.writerow(header)
        writer.writerows(rows)
    return path


def _report_of(found: "tuple[int, str, dict[str, bytes]]") -> str:
    """The one quality report a check wrote, as text."""
    (report,) = found[2].values()
    return report.decode("utf-8")


def test_quoting_by_class_is_judged_alike_in_groups(tmp_path: pathlib.Path) -> None:
    """Numbers bare and words quoted (csv.QUOTE_NONNUMERIC), described; the same records with every field quoted, and with none.

    A column quoted all one way does not show the survey which class each
    of its quotings belongs to, so the check reads the column's cells for
    the classes it holds (`_surveyed_cells`), again from the file where it
    is read in groups (`_quoting_holds` handed the table). Red on the
    mutant handing no cell (the quoting found HELD) and on the one handing
    no table (the check stops on the survey's empty columns).
    """
    header, rows = _records(7)
    table = _quoted(tmp_path / "table.csv", header, rows, csv.QUOTE_NONNUMERIC)
    described = _described(tmp_path, table, "--smallest-group", "3")
    assert "bytes.quoting [document.source.dialect]: HELD" in _report_of(_same_in_groups(described, table, tmp_path / "out"))
    for name, quoting in (("every", csv.QUOTE_ALL), ("none", csv.QUOTE_MINIMAL)):
        checked = _quoted(tmp_path / f"{name}.csv", header, rows, quoting)
        said = _report_of(_same_in_groups(described, checked, tmp_path / "out"))
        assert "bytes.quoting [document.source.dialect]: MISSED" in said, name


def test_a_header_line_written_into_a_headerless_file_is_found_alike_in_groups(tmp_path: pathlib.Path) -> None:
    """A headerless table described with --first-row data; the same records under a first line of the generated names, and with one record fewer.

    The check asks every column's first value (`_first_values`), a column
    at a time from the file where it is read in groups. Red on the mutant
    reading the columns a table read whole holds (none, read in groups).
    """
    header, rows = _records(8)
    table = _quoted(tmp_path / "table.csv", None, rows, csv.QUOTE_MINIMAL)
    described = _described(tmp_path, table, "--smallest-group", "3", "--first-row", "data")
    found = _report_of(_same_in_groups(described, table, tmp_path / "out"))
    assert "header.presence [document.source.header_source]: HELD" in found
    names = [f"column_{place + 1}" for place in range(len(header))]
    for name, records in (("named", rows), ("short", rows[1:])):
        checked = _quoted(tmp_path / f"{name}.csv", names, records, csv.QUOTE_MINIMAL)
        said = _report_of(_same_in_groups(described, checked, tmp_path / "out"))
        assert "header.presence [document.source.header_source]: MISSED" in said, name


def test_a_row_order_broken_inside_one_grain_is_found_alike_in_groups(tmp_path: pathlib.Path) -> None:
    """Visits in the order of their day beside a person key, the day published at a grain and the row order published; two records of one month swapped.

    The order is asked of the order column as the file wrote it
    (`_order_holds`, `reading.column_as_read`): at the published grain the
    two days read alike, so the swap shows only as written. Red on the
    mutant reading the order column as the check rewrote it.
    """
    draw = random.Random(11)
    visits = sorted(
        (datetime.date(2023, 1, 1) + datetime.timedelta(days=draw.randrange(730)), draw.randrange(200))
        for _row in range(600)
    )
    lines = ["patient,seen,value"] + [
        f"REC{80000000 + 7 * person:08d},{day.isoformat()},{draw.uniform(3, 150):.1f}" for day, person in visits
    ]
    table = tmp_path / "visits.csv"
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    described = _described(tmp_path, table, "--identifier", "patient")
    published = json.loads(described.read_text(encoding="utf-8"))
    (grain,) = [block["time_grain"] for block in published["columns"] if block["name"] == "seen"]
    assert grain["rung"] in ("month", "quarter", "year") and published["source"]["dialect"]["row_order"], grain
    place = next(
        at for at in range(1, len(visits))
        if visits[at - 1][0] != visits[at][0] and visits[at - 1][0].replace(day=1) == visits[at][0].replace(day=1)
    )
    swapped = list(lines)
    swapped[place], swapped[place + 1] = swapped[place + 1], swapped[place]
    other = tmp_path / "swapped.csv"
    other.write_text("\n".join(swapped) + "\n", encoding="utf-8", newline="\n")
    assert "rows.order [document.source.dialect]: HELD" in _report_of(_same_in_groups(described, table, tmp_path / "out"))
    assert "rows.order [document.source.dialect]: MISSED" in _report_of(_same_in_groups(described, other, tmp_path / "out"))


def test_a_workbook_and_its_twin_validate_alike_in_groups(tmp_path: pathlib.Path) -> None:
    """A workbook of numbers, dates and words (tests/workbooks.py's typed book, 150 records) and its twin.

    The reader holds a workbook whole whatever the budget, and the form
    checks read its whole bytes (`measure`'s `_whole_bytes`). Red on the
    mutant handing the checks the workbook's path instead.
    """
    book = tmp_path / "book.xlsx"
    book.write_bytes(workbooks.typed_book(150))
    described = _described(tmp_path, book, "--smallest-group", "3")
    with contextlib.redirect_stdout(io.StringIO()):
        assert lowered_floor.main(["generate", str(described), "--out-dir", str(tmp_path), "--seed", "0", "--replace"]) == 0
    for checked in (book, tmp_path / "book-twin.xlsx"):
        code, _said, written = _same_in_groups(described, checked, tmp_path / "out")
        assert code == 0 and written, checked.name


def test_a_table_of_twenty_thousand_rows_validates_alike_in_groups(
    tmp_path: pathlib.Path
) -> None:
    """ONE 20,000-row case: ages past 89 pooled in people and visit dates at a grain beside a person column.

    Lane SH's long table of ages (`age_address_shapes`' ``ages_long_table``:
    four patients aged 92 to 101 on 40 of 20,000 rows, ten rows a patient)
    with a day of each visit over twenty years beside it, described as the
    command describes it -- the Safe Harbor top-code and the count in people
    over the person column -- so the check rewrites ages (their top category
    pooled in the person column's people) and dates (at their published
    grain), checked against the table itself. Years are the unit sweep's.
    """
    import age_address_shapes as shapes
    import fixtures

    header, rows = shapes.build("ages_long_table", 20_000, 0)
    draw = random.Random(20000)
    lines = [",".join(header + ["seen"])]
    for row in rows:
        seen = datetime.date(2004, 1, 1) + datetime.timedelta(days=draw.randrange(7_300))
        lines += [",".join(row + [seen.isoformat()])]
    table = tmp_path / "people.csv"
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    read = reading.read_table(f"{table}", first_row=reading.FIRST_ROW_AUTOMATIC)
    document = profile.build_document(
        read, taxonomy.Settings(), [], subjects=[header[0]], top_code=True,
        harbor_year=taxonomy.SAFE_HARBOR_REFERENCE_YEAR,
    )
    blocks = {f"{block['name']}": block for block in document["columns"]}  # type: ignore[union-attr]
    assert blocks["age"]["top_coded"] == taxonomy.TOP_CODE and blocks["age"]["top_category_people"], blocks["age"]
    assert blocks["seen"].get("time_grain"), blocks["seen"]
    described = fixtures.write_profile(tmp_path, "people-profile.json", document)
    code, _said, written = _same_in_groups(described, table, tmp_path / "out")
    assert code in (0, 3) and written


# -- 3. never whole, and nothing left behind ----------------------------------


def test_a_file_checked_in_groups_is_never_read_whole(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    table = tmp_path / "visits.csv"
    table.write_text(_visits_table(400, 120, 3), encoding="utf-8", newline="\n")
    described = contract.load_profile(f"{_described(tmp_path, table, '--identifier', 'patient')}")
    expected = validation.measure(described, f"{table}")

    def refused(*_arguments: object) -> bytes:
        raise AssertionError("the checked file was read whole")

    _one_column_a_group(monkeypatch)
    monkeypatch.setattr(pathlib.Path, "read_bytes", refused)
    assert validation.measure(described, f"{table}") == expected


def test_a_file_changed_while_it_is_checked_in_groups_leaves_no_file(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    table = tmp_path / "visits.csv"
    table.write_text(_visits_table(400, 120, 5), encoding="utf-8", newline="\n")
    described = _described(tmp_path, table, "--identifier", "patient")
    before = sorted(os.listdir(tmp_path))
    built = profile.build_document
    calls = [0]

    def changing(*arguments: object, **options: object) -> object:
        calls[0] += 1
        if calls[0] == 2:
            with table.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write("REC80000007,2023-03-03,9.9\n")
        return built(*arguments, **options)  # type: ignore[arg-type]

    _one_column_a_group(monkeypatch)
    monkeypatch.setattr(profile, "build_document", changing)
    out = tmp_path / "out"
    out.mkdir()
    code, said, written = _validated(described, table, out)
    assert code == 1 and written == {}, said[-600:]
    assert sorted(os.listdir(tmp_path)) == sorted(before + ["out"])


def test_the_description_s_own_json_is_unchanged_by_reading_in_groups(tmp_path: pathlib.Path) -> None:
    """A table read in groups carries no rewrite unless the validator gives it one: the profile path reads as before."""
    table = tmp_path / "visits.csv"
    table.write_text(_visits_table(300, 90, 9), encoding="utf-8", newline="\n")
    read = reading.read_table(str(table), in_groups=True)
    assert read.source is None or read.source.rewrites == ()
    assert json.loads(_described(tmp_path, table).read_text(encoding="utf-8"))["columns"]


# -- 4. K-S4-23's driver, machine-free ----------------------------------------


def _the_driver(monkeypatch: pytest.MonkeyPatch) -> object:
    """`tools/measurements/kpi_validate_groups.py`, imported by name from its folder put first on the path for this test."""
    monkeypatch.syspath_prepend(str(pathlib.Path(__file__).resolve().parents[1] / "tools" / "measurements"))
    import kpi_validate_groups

    return kpi_validate_groups


def _rows_of(arguments: "list[str]") -> int:
    """The rows of the size a made-up run was handed, read off its OUT_DIR's folder (`<table>-<rows>/out`)."""
    return int(pathlib.Path(arguments[3]).parent.name.split("-")[1])


def _fake_runs(
    driver: object,
    monkeypatch: pytest.MonkeyPatch,
    shipped: "dict[str, str] | None" = None,
    alter: "typing.Callable[[dict[str, object], list[str], str], None] | None" = None,
    handed: "typing.Callable[[int], int] | None" = None,
) -> "list[tuple[str, str, bool, bool]]":
    """Made-up runs in place of the driver's processes: a size's peak 100 MiB and a MiB each 2,000 rows, 40 MiB more at hash seed 2.

    ``alter`` changes a run's record in place (a run of `imports` too);
    ``handed`` gives the rows the pair handed for a size holds.
    """
    mebibyte: int = driver.MEBIBYTE  # type: ignore[attr-defined]
    runs: "list[tuple[str, str, bool, bool]]" = []

    def child(arguments: "list[str]", seed: str = "1") -> "dict[str, object]":
        nonlocal runs
        if arguments[0] == "imports":
            record: "dict[str, object]" = {"exit": 0, "peak_footprint_bytes": 80 * mebibyte}
        else:
            rows = _rows_of(arguments)
            grouped = "--group-bytes" in arguments
            runs += [(pathlib.Path(arguments[3]).parent.name, seed, grouped, "--trace" in arguments)]
            record = {
                "exit": 3, "cpu_seconds": rows / 1_000, "wall_seconds": rows / 500, "pressure_level": 2,
                "peak_footprint_bytes": int((100 + rows / 2_000 + (40 if seed == "2" else 0)) * mebibyte),
                "instructions": rows * 100_000, "traced_peak_bytes": 4_000_000,
                "written": dict(shipped) if shipped is not None and not grouped else {"t-twin-quality.txt": "a" * 64},
                "screen": "s", "counter": "c",
            }
        if alter is not None:
            alter(record, arguments, seed)
        return record

    def prepare(kind: str, rows: int, folder: pathlib.Path) -> "tuple[pathlib.Path, pathlib.Path, dict[str, object]]":
        holds = handed(rows) if handed is not None else rows
        record = {"table": kind, "rows": holds, "columns": 50, "description_sha256": "d" * 64, "twin_sha256": "e" * 64}
        return folder / "d.json", folder / "t-twin.csv", record

    monkeypatch.setattr(driver, "_child", child)
    monkeypatch.setattr(driver, "prepare", prepare)
    return runs


def _measured(
    monkeypatch: pytest.MonkeyPatch,
    sizes: "tuple[int, ...]",
    shipped: "dict[str, str] | None" = None,
    alter: "typing.Callable[[dict[str, object], list[str], str], None] | None" = None,
) -> "tuple[dict[str, object], dict[str, object], list[tuple[str, str, bool, bool]]]":
    """`measure` over made-up runs (`_fake_runs`)."""
    driver = _the_driver(monkeypatch)
    runs = _fake_runs(driver, monkeypatch, shipped, alter)
    found, validate_keys = driver.measure(list(sizes), "")  # type: ignore[attr-defined]
    return found, validate_keys, runs


def _kpi_printed(driver: object, capsys: pytest.CaptureFixture[str]) -> "tuple[bool, list[dict[str, object]]]":
    """The driver's --kpi run: whether it stopped, and the KPI records it printed."""
    try:
        driver.main()  # type: ignore[attr-defined]
        stopped = False
    except SystemExit:
        stopped = True
    out = capsys.readouterr().out
    return stopped, [json.loads(line[4:]) for line in out.splitlines() if line.startswith("KPI ")]


def test_k_s4_23_projects_no_peak_from_sizes_under_a_million_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    """The statistics skeptic of lane SV, items 2 and 4 (LANE SV RULINGS 1 (3)).

    One run a size moved by about two between runs of the same check, so
    each size's peak is the largest of three runs (hash seeds 1, 2 and 3),
    each run's peak, wall seconds and memory-pressure level beside it; and
    below 1,000,000 rows no peak is projected: the lines through each two
    sizes are recorded, the entry's target keys are not measured, so the
    ledger's judge holds it OPEN even on the reference machine (never
    IMPROVED), and K-S4-09's validate keys are not emitted. Red on the
    mutant projecting from these sizes, on the one emitting K-S4-09's
    keys, and on the one taking one run a size.
    """
    found, validate_keys, runs = _measured(monkeypatch, (20_000, 100_000, 200_000))
    assert validate_keys == {}
    assert not [key for key in found if key.endswith("_peak_mb_2m_projected")], found
    assert found["mixed_validate_peak_mb"] == [150.0, 190.0, 240.0]
    assert found["mixed_validate_peak_mb_2m_lines"] == {"20000-100000": 1140.0, "20000-200000": 1140.0, "100000-200000": 1140.0}
    assert found["gaussian_validate_runs"][0] == [[110.0, 40.0, 2.0], [150.0, 40.0, 2.0], [110.0, 40.0, 2.0]]  # type: ignore[index]
    assert sorted({seed for _folder, seed, grouped, traced in runs if grouped and not traced}) == ["1", "2", "3"]
    entry = kpi_rules.entries_by_id(kpi_rules.load_ledger())["K-S4-23"]
    verdict = kpi_rules.judge(entry, found, seconds_count=True)
    assert verdict.word == kpi_rules.OPEN_HELD, verdict
    # Three sizes of 100,000 rows or more whose largest is under 1,000,000 rows project nothing either.
    found, validate_keys, _runs = _measured(monkeypatch, (20_000, 100_000, 200_000, 500_000))
    assert validate_keys == {} and not [key for key in found if key.endswith("_peak_mb_2m_projected")], found
    assert "100000-500000" in found["mixed_validate_peak_mb_2m_lines"]  # type: ignore[operator]
    assert kpi_rules.judge(entry, found, seconds_count=True).word == kpi_rules.OPEN_HELD


def test_k_s4_23_projects_the_peak_as_lane_b0_does_from_a_million_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    """From 1,000,000 rows the peak is projected over the three largest sizes above the imports' footprint (lane B0's projection), and K-S4-09's validate keys carry it.

    Only sizes of 100,000 rows or more are fitted (the combined verify of
    lane SV's repair 1, item 5): sizes of 20,000, 500,000 and 1,000,000
    rows project nothing, red on the mutant fitting the 20,000-row point.
    """
    found, validate_keys, _runs = _measured(monkeypatch, (20_000, 250_000, 500_000, 1_000_000))
    import kpi_describe_groups

    _growth, at = kpi_describe_groups.projected([250_000, 500_000, 1_000_000], [265.0, 390.0, 640.0], 80.0)
    assert found["imports_mb"] == 80.0 and "mixed_validate_peak_mb_2m_lines" not in found
    assert found["mixed_validate_peak_mb_2m_projected"] == round(at, 1)
    assert validate_keys == {"mixed_validate_peak_mb_2m": round(at, 1), "gaussian_validate_peak_mb_2m": round(at, 1)}
    # Two sizes, one of them 1,000,000 rows, hold no fit over three: no peak is projected.
    found, validate_keys, _runs = _measured(monkeypatch, (20_000, 1_000_000))
    assert validate_keys == {} and "mixed_validate_peak_mb_2m_projected" not in found
    assert found["mixed_validate_peak_mb_2m_lines"] == {"20000-1000000": 1140.0}
    # Three sizes, two of them of 100,000 rows or more: the 20,000-row point is never fitted.
    found, validate_keys, _runs = _measured(monkeypatch, (20_000, 500_000, 1_000_000))
    assert validate_keys == {} and "mixed_validate_peak_mb_2m_projected" not in found and "imports_mb" not in found
    assert set(found["mixed_validate_peak_mb_2m_lines"]) == {"20000-500000", "20000-1000000", "500000-1000000"}  # type: ignore[arg-type]
    # Four sizes of 100,000 rows or more: the peak is fitted over the three largest of them.
    found, validate_keys, _runs = _measured(monkeypatch, (20_000, 100_000, 250_000, 500_000, 1_000_000))
    assert found["mixed_validate_peak_mb_2m_projected"] == round(at, 1) and validate_keys["mixed_validate_peak_mb_2m"] == round(at, 1)


@pytest.mark.parametrize("projected", [False, True])
def test_k_s4_23_s_driver_emits_k_s4_09_s_keys_only_with_a_projection(
    projected: bool, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """The statistics skeptic of lane SV, item 4: K-S4-09's validate keys are printed for kpi_run only where the peak was projected by K-S4-09's rule. Red on the mutant printing them always."""
    driver = _the_driver(monkeypatch)
    keys = {"mixed_validate_peak_mb_2m": 900.0} if projected else {}
    monkeypatch.setattr(driver, "measure", lambda _sizes, _keep: ({"equal_files_ratio": 1.0}, keys))
    monkeypatch.setattr(driver.kpi_rules, "guard_this_tree", lambda: "")  # type: ignore[attr-defined]
    monkeypatch.setattr("sys.argv", ["kpi_validate_groups.py", "--kpi"])
    assert driver.main() == 0  # type: ignore[attr-defined]
    printed = [json.loads(line[4:])["id"] for line in capsys.readouterr().out.splitlines() if line.startswith("KPI ")]
    assert printed == (["K-S4-23", "K-S4-09"] if projected else ["K-S4-23"])


def test_k_s4_23_counts_a_file_one_run_alone_wrote_as_unequal(monkeypatch: pytest.MonkeyPatch) -> None:
    """The statistics skeptic of lane SV, item 8, and the combined verify of its repair 1, item 3 (D16): every name either run wrote is compared, whichever run alone wrote it. Red on the mutants reading only one run's names."""
    found, _keys, _runs = _measured(
        monkeypatch, (20_000, 100_000), shipped={"t-twin-quality.txt": "a" * 64, "t-more.txt": "b" * 64},
    )
    assert (found["files_compared"], found["files_equal"]) == (6, 4)
    assert found["equal_files_ratio"] == 0.667

    def grouped_writes_more(record: "dict[str, object]", arguments: "list[str]", _seed: str) -> None:
        if arguments[0] == "run" and "--group-bytes" in arguments:
            record["written"] = {"t-twin-quality.txt": "a" * 64, "t-extra.txt": "c" * 64}

    found, _keys, _runs = _measured(monkeypatch, (20_000, 100_000), alter=grouped_writes_more)
    assert (found["files_compared"], found["files_equal"]) == (6, 4)
    assert found["equal_files_ratio"] == 0.667


def test_k_s4_23_takes_each_size_s_seconds_and_instructions_as_the_largest_of_three_runs(monkeypatch: pytest.MonkeyPatch) -> None:
    """The combined verify of lane SV's repair 1, item 3 (D5 and D6): a size's CPU seconds and instructions retired are the largest of its three runs, as its peak is. Red on the mutants taking run 1's."""

    def third_run_works_more(record: "dict[str, object]", arguments: "list[str]", seed: str) -> None:
        if arguments[0] == "run" and seed == "3" and "--group-bytes" in arguments and "--trace" not in arguments:
            rows = _rows_of(arguments)
            record["cpu_seconds"] = rows / 1_000 + rows / 2_000
            record["instructions"] = rows * 110_000

    found, _keys, _runs = _measured(monkeypatch, (20_000, 100_000), alter=third_run_works_more)
    assert found["mixed_validate_cpu_seconds"] == [30.0, 150.0]
    assert found["gaussian_validate_g_instructions"] == [2.2, 11.0]


@pytest.mark.parametrize("differs", ["screen", "exit"])
def test_k_s4_23_compares_the_screen_and_the_exit_of_the_two_runs(differs: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """The combined verify of lane SV's repair 1, item 3 (D12 and D13): two runs that print different screens, or exit differently (both completed), are unequal on that unit. Red on the mutants dropping the screen or the exit from it."""

    def shipped_run_differs(record: "dict[str, object]", arguments: "list[str]", _seed: str) -> None:
        if arguments[0] == "run" and "--group-bytes" not in arguments:
            record["screen" if differs == "screen" else "exit"] = "t" if differs == "screen" else 0

    found, _keys, _runs = _measured(monkeypatch, (20_000, 100_000), alter=shipped_run_differs)
    assert (found["files_compared"], found["files_equal"]) == (4, 2)
    assert found["equal_files_ratio"] == 0.5


_FAULTS = ("failed exit", "missing report", "counter -1", "wrong size", "short list")
_PLACES = ("first size", "last size", "shipped", "traced")


def test_k_s4_23_s_evidence_is_withheld_never_favourable_by_accident(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """LANE SV RULINGS 3 (2), Codex's review of lane SV, items 2 to 5: a GENERATED check of the driver's --kpi run.

    Every combination of five faults -- a validation that exited 1, one
    that exited 3 and wrote no report, a memory counter that read nothing
    (-1: a grouped run's peak, or the imports' when the fault lands on the
    shipped or the traced run), a pair handed for a size that holds
    another, and a size list that cannot carry the projection (20,000,
    500,000 and 1,000,000 rows, or 20,000, 100,000 and 200,000) -- each
    landing on the first size's run at hash seed 1, the last size's at
    seed 3, the shipped run or the traced run: 128 runs of the driver.
    With any fault NO target key is printed and the judge reads no
    IMPROVED, on the quiet machine or off it; a run that did not complete
    and a pair of another size stop the measurement with nothing printed.
    Without a fault, over 20,000, 250,000, 500,000 and 1,000,000 rows,
    both projected peaks and K-S4-09's keys are printed and the judge
    reads IMPROVED on the quiet machine: the check sees what it bars. Red
    on the mutant consuming any run (Codex's probe: exit 1 at 250,000 to
    1,000,000 rows read IMPROVED), the one reading no report, the one
    taking a counter of -1 (both keys -0.0, IMPROVED), the one trusting
    the handed pair's size and the one fitting the 20,000-row point.
    """
    driver = _the_driver(monkeypatch)
    entry = kpi_rules.entries_by_id(kpi_rules.load_ledger())["K-S4-23"]
    monkeypatch.setattr(driver.kpi_rules, "guard_this_tree", lambda: "")  # type: ignore[attr-defined]
    monkeypatch.setattr("sys.argv", ["kpi_validate_groups.py", "--kpi"])
    cases = 0
    for count in range(len(_FAULTS) + 1):
        for chosen in itertools.combinations(_FAULTS, count):
            for place in _PLACES:
                sizes: "tuple[int, ...]" = (20_000, 250_000, 500_000, 1_000_000)
                if "short list" in chosen:
                    sizes = (20_000, 500_000, 1_000_000) if place in ("first size", "shipped") else (20_000, 100_000, 200_000)
                monkeypatch.setenv("SV_KPI_SIZES", ",".join(f"{size}" for size in sizes[1:]))
                target = (sizes[0], "1") if place == "first size" else (sizes[-1], "3")

                def alter(
                    record: "dict[str, object]", arguments: "list[str]", seed: str,
                    chosen: "tuple[str, ...]" = chosen, place: str = place, target: "tuple[int, str]" = target,
                ) -> None:
                    if arguments[0] == "imports":
                        if "counter -1" in chosen and place in ("shipped", "traced"):
                            record["peak_footprint_bytes"] = -1
                        return
                    grouped = "--group-bytes" in arguments
                    traced = "--trace" in arguments
                    hit = (
                        (place == "shipped" and not grouped)
                        or (place == "traced" and traced)
                        or (place in ("first size", "last size") and grouped and not traced and (_rows_of(arguments), seed) == target)
                    )
                    if not hit:
                        return
                    if "failed exit" in chosen:
                        record["exit"] = 1
                    if "missing report" in chosen:
                        record["written"] = {"t-twin-other.txt": "c" * 64}
                    if "counter -1" in chosen and place in ("first size", "last size"):
                        record["peak_footprint_bytes"] = -1

                def handed(rows: int, wrong: int = sizes[-1] if place == "last size" else sizes[0]) -> int:
                    return rows + 1 if rows == wrong else rows

                _fake_runs(driver, monkeypatch, alter=alter, handed=handed if "wrong size" in chosen else None)
                stopped, printed = _kpi_printed(driver, capsys)
                cases += 1
                label = (chosen, place)
                if not chosen:
                    assert not stopped and [record["id"] for record in printed] == ["K-S4-23", "K-S4-09"], label
                    value = printed[0]["value"]
                    assert isinstance(value, dict) and value["equal_files_ratio"] == 1.0, label
                    assert sorted(key for key in value if key.endswith("_peak_mb_2m_projected")) == [
                        "gaussian_validate_peak_mb_2m_projected", "mixed_validate_peak_mb_2m_projected",
                    ], label
                    assert sorted(printed[1]["value"]) == ["gaussian_validate_peak_mb_2m", "mixed_validate_peak_mb_2m"], label  # type: ignore[arg-type]
                    assert kpi_rules.judge(entry, value, seconds_count=True).word == kpi_rules.IMPROVED, label
                    continue
                if {"failed exit", "missing report", "wrong size"} & set(chosen):
                    assert stopped and printed == [], label
                    continue
                assert not stopped and [record["id"] for record in printed] == ["K-S4-23"], label
                value = printed[0]["value"]
                assert isinstance(value, dict) and not [key for key in value if key.endswith("_peak_mb_2m_projected")], label
                for seconds_count in (True, False):
                    assert kpi_rules.judge(entry, value, seconds_count=seconds_count).word != kpi_rules.IMPROVED, label
    assert cases == 2 ** len(_FAULTS) * len(_PLACES) == 128


def test_k_s4_23_s_size_list_is_read_before_any_work(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Codex's review of lane SV, item 5 (LANE SV RULINGS 3 (2)(d)): `SV_KPI_SIZES` is read before any process is started.

    A list giving one size (20,000 rows, always measured), a word, a size
    under the table floor or no size at all is refused with nothing run
    and nothing printed -- never an IndexError after the measuring. Red on
    the driver that read `SV_KPI_SIZES=20000` and measured.
    """
    driver = _the_driver(monkeypatch)
    started: "list[list[str]]" = []

    def child(arguments: "list[str]", seed: str = "1") -> "dict[str, object]":
        nonlocal started
        started += [arguments]
        return {}

    monkeypatch.setattr(driver, "_child", child)
    monkeypatch.setattr(driver.kpi_rules, "guard_this_tree", lambda: "")  # type: ignore[attr-defined]
    monkeypatch.setattr("sys.argv", ["kpi_validate_groups.py", "--kpi"])
    for named in ("20000", "20000,20000", "abc", "5000,100000", "100000,1e6", " , "):
        monkeypatch.setenv("SV_KPI_SIZES", named)
        stopped, printed = _kpi_printed(driver, capsys)
        assert stopped and printed == [] and started == [], named
    monkeypatch.setenv("SV_KPI_SIZES", "100000, 20000,100000")
    assert driver.sizes_asked() == [20_000, 100_000]  # type: ignore[attr-defined]


def _files_under(root: pathlib.Path) -> "dict[str, bytes]":
    """Every file under ``root``, by its path below it, with its bytes."""
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in sorted(root.rglob("*")) if path.is_file()}


def test_k_s4_23_s_run_never_clears_the_folder_it_is_handed(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's review of lane SV, item 1 (LANE SV RULINGS 3 (1)): `run` never clears the contents of a folder it was handed.

    An OUT_DIR that is either input, or is or holds either input's folder,
    or is a file, or holds the run's own folder already, is refused before
    anything is read or written: both inputs, an unrelated file and the
    earlier run's folder survive byte for byte, and no check runs. Red on
    the driver that emptied OUT_DIR first (both inputs lost). A folder of
    its own is written in and taken away again: the report's digest comes
    back, everything else under the folders stays as it was.
    """
    driver = _the_driver(monkeypatch)
    checked: "list[list[str]]" = []

    def check(arguments: "list[str]", **_options: object) -> int:
        nonlocal checked
        checked += [arguments]
        out = pathlib.Path(arguments[arguments.index("--out-dir") + 1])
        (out / "t-twin-quality.txt").write_text("report\n", encoding="utf-8", newline="\n")
        print(f"Written:\n  {out / 't-twin-quality.txt'}")
        return 3

    monkeypatch.setattr(cli, "main", check)

    def laid_out(name: str, description_in: str, twin_in: str) -> "tuple[pathlib.Path, pathlib.Path, pathlib.Path]":
        root = tmp_path / name
        out = root / "out"
        for folder in (out, root / description_in, root / twin_in):
            folder.mkdir(parents=True, exist_ok=True)
        described = root / description_in / "t-profile.json"
        twin = root / twin_in / "t-twin.csv"
        described.write_text("{}\n", encoding="utf-8", newline="\n")
        twin.write_text("a\n1\n", encoding="utf-8", newline="\n")
        (out / "notes.txt").write_text("kept\n", encoding="utf-8", newline="\n")
        return described, twin, out

    refused = {
        "the inputs inside OUT_DIR": ("out", "out", None),
        "OUT_DIR holds both inputs' folders": ("out/desc", "out/twin", None),
        "OUT_DIR is the description's folder": ("out", "twin", None),
        "OUT_DIR is the twin's folder": ("desc", "out", None),
        "OUT_DIR is the description": ("desc", "twin", "description"),
        "OUT_DIR is the twin": ("desc", "twin", "twin"),
        "OUT_DIR is a file": ("desc", "twin", "notes"),
        "an earlier run's folder in OUT_DIR": ("desc", "twin", "earlier"),
    }
    for name, (description_in, twin_in, handed) in refused.items():
        described, twin, out = laid_out(name.replace(" ", "-").replace("'", ""), description_in, twin_in)
        if handed == "earlier":
            (out / driver.RUN_FOLDER).mkdir()  # type: ignore[attr-defined]
            (out / driver.RUN_FOLDER / "t-twin-quality.txt").write_text("earlier\n", encoding="utf-8", newline="\n")  # type: ignore[attr-defined]
        given = {"description": described, "twin": twin, "notes": out / "notes.txt"}.get(f"{handed}", out)
        before = _files_under(tmp_path)
        with pytest.raises(SystemExit):
            driver.run(str(described), str(twin), given, 0, 0, False)  # type: ignore[attr-defined]
        assert _files_under(tmp_path) == before and checked == [], name
    for name, description_in, twin_in in (("apart", "desc", "twin"), ("inside the description's folder", "desc", "twin")):
        described, twin, out = laid_out(name.replace(" ", "-").replace("'", ""), description_in, twin_in)
        if name != "apart":
            out = described.parent / "out"
        before = _files_under(tmp_path)
        found = driver.run(str(described), str(twin), out, 0, 0, False)  # type: ignore[attr-defined]
        assert found["exit"] == 3 and found["written"] == {"t-twin-quality.txt": hashlib.sha256(b"report\n").hexdigest()}, name
        assert _files_under(tmp_path) == before and not (out / driver.RUN_FOLDER).exists(), name  # type: ignore[attr-defined]
        assert checked[-1][checked[-1].index("--out-dir") + 1] == f"{out / driver.RUN_FOLDER}", name  # type: ignore[attr-defined]


def test_k_s4_23_uses_a_kept_pair_only_where_its_record_holds(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's review of lane SV, item 4 (LANE SV RULINGS 3 (2)(c)): a pair kept by `SV_KPI_KEEP` is never trusted by its folder's name.

    A size's pair is measured only where the record written beside it once
    it was made and read back (`inputs.json`) still holds: its table, rows,
    columns, seed and code, and both files' digests. A pair with no record,
    one whose twin was edited, one made by other code and one made at 300
    rows kept under the folder of 3,000 are made again; a pair that reads
    back at another size is refused, its record never written. Red on the
    driver that reused any pair whose two files were there (Codex's probe:
    a 20,000-row pair under mixed-1000000 measured as 1,000,000 rows).
    Made-up steps write three columns in place of the 50.
    """
    driver = _the_driver(monkeypatch)
    monkeypatch.setattr(driver, "COLUMNS", 3)
    made: "list[tuple[str, int]]" = []
    short = [False]
    narrow = [False]

    def child(arguments: "list[str]", seed: str = "1") -> "dict[str, object]":
        nonlocal made
        action, kind, rows, place = arguments[0], arguments[1], int(arguments[2]), pathlib.Path(arguments[3])
        made += [(action, rows)]
        if action == "write":
            place.mkdir(parents=True, exist_ok=True)
            (place / f"{kind}.csv").write_text("a,b,c\n", encoding="utf-8", newline="\n")
        elif action == "describe":
            (place / "desc").mkdir(exist_ok=True)
            document = {"n_rows": rows, "columns": [{"name": name} for name in "abc"]}
            (place / "desc" / f"{kind}-profile.json").write_text(json.dumps(document), encoding="utf-8", newline="\n")
        else:
            (place / "twin").mkdir(exist_ok=True)
            records = rows - 1 if short[0] else rows
            header, line = ("a,b\n", "1,2\n") if narrow[0] else ("a,b,c\n", "1,2,3\n")
            (place / "twin" / f"{kind}-twin.csv").write_text(header + line * records, encoding="utf-8", newline="\n")
        return {"exit": 0}

    monkeypatch.setattr(driver, "_child", child)
    folder = tmp_path / "mixed-300"
    described, twin, record = driver.prepare("mixed", 300, folder)  # type: ignore[attr-defined]
    assert [action for action, _rows in made] == ["write", "describe", "generate"] and not (folder / "mixed.csv").exists()
    assert (record["table"], record["rows"], record["columns"]) == ("mixed", 300, 3)
    assert record["twin_sha256"] == hashlib.sha256(twin.read_bytes()).hexdigest()
    assert json.loads((folder / "inputs.json").read_text(encoding="utf-8")) == record
    made.clear()
    assert driver.prepare("mixed", 300, folder)[2] == record and made == []  # type: ignore[attr-defined]
    # Another size's folder holding the 300-row pair and its record: made again at 3,000 rows.
    shutil.copytree(folder, tmp_path / "mixed-3000")
    _described, twin, record = driver.prepare("mixed", 3000, tmp_path / "mixed-3000")  # type: ignore[attr-defined]
    assert made == [("write", 3000), ("describe", 3000), ("generate", 3000)] and record["rows"] == 3000
    assert twin.read_text(encoding="utf-8").count("\n") == 3001
    for spoiled in ("edited twin", "edited description", "no record", "other code"):
        made.clear()
        with pytest.MonkeyPatch.context() as code:
            if spoiled == "edited twin":
                with (folder / "twin" / "mixed-twin.csv").open("a", encoding="utf-8", newline="\n") as handle:
                    handle.write("1,2,3\n")
            elif spoiled == "edited description":
                with (folder / "desc" / "mixed-profile.json").open("a", encoding="utf-8", newline="\n") as handle:
                    handle.write(" ")
            elif spoiled == "no record":
                (folder / "inputs.json").unlink()
            else:
                code.setattr(driver, "code_digest", lambda: "0" * 64)
            assert driver.prepare("mixed", 300, folder)[2]["rows"] == 300, spoiled  # type: ignore[attr-defined]
        assert [action for action, _rows in made] == ["write", "describe", "generate"], spoiled
    # A pair that reads back at another size is refused, its record never written.
    short[0] = True
    with pytest.raises(SystemExit):
        driver.prepare("mixed", 500, tmp_path / "mixed-500")  # type: ignore[attr-defined]
    assert not (tmp_path / "mixed-500" / "inputs.json").exists()
    # A pair that reads back a column short is refused too.
    short[0], narrow[0] = False, True
    with pytest.raises(SystemExit):
        driver.prepare("mixed", 500, tmp_path / "mixed-500-narrow")  # type: ignore[attr-defined]
    assert not (tmp_path / "mixed-500-narrow" / "inputs.json").exists()


# -- 5. batch 4s's merge: the line's top-coded readings and time checks -------
#
# The integration line beside this lane read a top-coded column with the age
# words around its numbers and its ends pooled in people (lane HB2, plan
# P4-D477: `top_coded_words`, `top_coded_ends`) and its bands of ages past 89
# as one band (lane CZ-E, plan P4-D472: `top_coded_bands`), through three more
# arguments of `validation._top_coded_table`; git merged that function and this
# lane's grouped branch of it without a conflict, and the grouped branch handed
# its column over WITHOUT them (batch 4s, step 10). The cases below pin the
# join, at the unit level over generated tables and at the table level.

_LINE_UNITS = ("y", "m", "w", "d")
_LINE_WORDED = ("Age {}", "AGE: {}", "age={}", "Age {} yrs", "[Age {}]", "{} y/o")
_LINE_BANDS = ("90-94", "95+", "18-44", "45-64", "65-89", "Age 90-94", "age >= 95", "[AGED: 90-94]", "90+", ">= 95",
               "Age 95+", "ages 90-94 years")
_LINE_ABSENT = ("", " ", "NA", "unknown", "999", "-1")


def _line_years(draw: random.Random) -> int:
    """An age in whole years: mostly 18 to 89, a few under 10 and a few from 90 to 140."""
    pick = draw.random()
    if pick < 0.08:
        return draw.randrange(0, 10)
    if pick < 0.22:
        return draw.randrange(90, 141)
    return draw.randrange(18, 90)


def _line_in_unit(draw: random.Random, years: int, unit: str) -> str:
    """One age of ``years`` written in ``unit`` as lane HB2's gate writes them: bare or with its unit word."""
    if unit == "y":
        return draw.choice((f"{years}", f"{years} years", f"{years} yrs"))
    mark = taxonomy.AGE_MARKS[unit]
    value = (years * mark) // 90 + draw.randrange(max(1, mark // 90))
    return f"{value} " + {"m": "months", "w": "wk", "d": "days"}[unit]


def _line_cells(draw: random.Random, kind: str, ages: "list[int]") -> "list[str]":
    """One column of ``kind`` over each row's age: a unit's ages, worded ages, bands, or years of birth."""
    cells: "list[str]" = []
    for years in ages:
        if draw.random() < 0.06:
            cells += [draw.choice(_LINE_ABSENT)]
        elif kind in _LINE_UNITS:
            cells += [_line_in_unit(draw, years, kind)]
        elif kind == "worded":
            cells += [draw.choice(_LINE_WORDED).format(years)]
        elif kind == "bands":
            cells += [draw.choice(_LINE_BANDS) if years >= 90 or draw.random() < 0.3 else f"{years}"]
        else:
            cells += [f"{2026 - years}" if draw.random() < 0.9 else draw.choice(["1850", "1849", "19x5", " 1920"])]
    return cells


def test_the_line_s_age_readings_in_groups_are_those_of_the_whole_table(tmp_path: pathlib.Path) -> None:
    """Seeded tables of the line's top-coded shapes -- ages in years, months, weeks and days with ends drawn in the
    column's unit, worded ages, bands past 89 bare and worded, top categories pooled in a person column's people, years
    -- each column read through `_top_coded_table` with the age words, the ends and the bands the description records
    and through `_year_top_coded_table`, in groups of one column and whole: the same cells, column for column.

    Red on the merge as git wrote it (batch 4s, step 10), whose grouped branch handed the column over without the
    line's three arguments, and on each mutant dropping one of them in `column_as_checked`: the counts below are the
    cells each argument moves on these tables, so each loss shows.
    """
    draw = random.Random(20261112)
    compared = 0
    moved = {"words": 0, "ends": 0, "bands": 0}
    for case in range(48):
        people = draw.randrange(12, 60)
        each = draw.randrange(1, 4)
        ages = [_line_years(draw) for _person in range(people)]
        keys = [f"P{draw.randrange(10 ** 5):05d}" for _person in range(people)]
        header = ["person"]
        columns: "list[list[str]]" = [[keys[who] for who in range(people) for _row in range(each)]]
        marks: "dict[str, int]" = {}
        years: "dict[str, int]" = {}
        ends: "dict[str, tuple[int, int]]" = {}
        words: "list[str]" = []
        banded: "set[str]" = set()
        pooled: "dict[str, tuple[int, tuple[str, ...]]]" = {}
        for place in range(draw.randrange(2, 6)):
            kind = draw.choice(_LINE_UNITS + ("worded", "bands", "year", "y", "worded", "bands"))
            name = f"{kind}_{place}"
            header += [name]
            rows = [ages[who] if draw.random() < 0.8 else _line_years(draw) for who in range(people) for _row in range(each)]
            columns += [_line_cells(draw, kind, rows)]
            if kind == "year":
                years[name] = draw.choice([1934, 1937, 1940])
                continue
            mark = taxonomy.AGE_MARKS[kind] if kind in _LINE_UNITS and draw.random() < 0.5 else taxonomy.TOP_CODE
            marks[name] = mark
            if draw.random() < 0.7:
                low = (draw.randrange(10, 40) * mark) // 90
                ends[name] = (low, max(low + 1, (draw.randrange(55, 90) * mark) // 90))
            if kind == "worded" or draw.random() < 0.3:
                words += [name]
            if kind == "bands" or draw.random() < 0.3:
                banded |= {name}
            if draw.random() < 0.4:
                pooled[name] = (draw.choice([3, 11]), ("person",) if draw.random() < 0.7 else ())
        declared = tuple(draw.sample(["999", "-1", "unknown", "NA"], draw.randrange(0, 3)))
        path = _written(tmp_path / f"line{case}.csv", header, columns)
        whole, grouped = _read_both(path)
        both: "list[list[list[str]]]" = []
        for table in (whole, grouped):
            coded = validation._top_coded_table(table, marks, pooled, [], declared, declared, words, ends, frozenset(banded))
            both += [_columns(validation._year_top_coded_table(coded, years, [], declared))]
        assert both[1] == both[0], (case, header)
        assert [reading.column_as_read(grouped, place) for place in range(len(header))] == _columns(whole)
        # ...and what each of the line's three arguments moves here, read whole: each loss would show above.
        full = _columns(validation._top_coded_table(whole, marks, pooled, [], declared, declared, words, ends,
                                                    frozenset(banded)))
        for argument, without in (
            ("words", validation._top_coded_table(whole, marks, pooled, [], declared, declared, None, ends, frozenset(banded))),
            ("ends", validation._top_coded_table(whole, marks, pooled, [], declared, declared, words, None, frozenset(banded))),
            ("bands", validation._top_coded_table(whole, marks, pooled, [], declared, declared, words, ends, frozenset())),
        ):
            moved[argument] += sum(
                1 for place, cells in enumerate(_columns(without)) for row, cell in enumerate(cells) if cell != full[place][row]
            )
        compared += len(header)
    assert compared >= 150, compared
    assert moved["words"] >= 200 and moved["ends"] >= 200 and moved["bands"] >= 100, moved


def _line_visits(draw: random.Random, people: int, each: int) -> "tuple[list[str], list[list[str]]]":
    """Visits beside a person column, each person's age the same on every row, in the line's top-coded shapes.

    Ages in years, in months, in weeks and in days, the unit written in each cell (`N months`, `N wk`, `N days`), worded
    ages (lane HB2's words, one spelling a person) and bands bare and worded (lanes CZ-E and HB2), a person in about
    sixty at either end, past 89 among them, so the description pools its ends and its top category in people.
    """
    header = ["sid", "age", "age_in_months", "age_in_weeks", "age_in_days", "age_text", "age_band"]
    rows: "list[list[str]]" = []
    for who in range(people):
        years = min(89, max(22, int(round(draw.gauss(55, 12)))))
        if who % 61 == 0:
            years = draw.choice([3, 5, 7, 93, 97, 101, 108])
        spelled = draw.choice(["Age {}", "Age: {}", "{} yrs", "AGE {}"]).format(years)
        if years >= 90:
            band = draw.choice(["90-94", "Age 90-94", "95+", "age >= 95"] if years >= 95 else ["90-94", "Age 90-94"])
        else:
            band = "18-44" if years < 45 else "45-64" if years < 65 else "65-89"
        for _row in range(each):
            rows += [[f"P{who:06d}", f"{years}", f"{12 * years} months", f"{52 * years} wk", f"{365 * years} days", spelled, band]]
    return header, rows


def _line_times(draw: random.Random, rows: int, people: int) -> "tuple[list[str], list[list[str]]]":
    """Visits beside a person column: stamps at the offsets US Eastern puts in force, each month's stamps wearing one
    (lane DST's shape), clock times written as four figures (lane TR's shape, read on `clock-figures`) and years of
    birth of people aged 18 to 104 against the reference year, one cell a stray `19` (lane SH2's shape
    `birth_years_stray`)."""
    header = ["sid", "seen_at", "chart_time", "birth_year"]
    found: "list[list[str]]" = []
    for index in range(rows):
        month = index % 12 + 1
        day = draw.randrange(1, 10) if month == 3 else draw.randrange(1, 3) if month == 11 else draw.randrange(1, 29)
        offset = "-04:00" if 4 <= month <= 11 else "-05:00"
        clock = f"{draw.randrange(24):02d}:{draw.randrange(60):02d}:{draw.randrange(60):02d}"
        found += [[f"PT{500000 + index % people}", f"2024-{month:02d}-{day:02d} {clock}{offset}",
                   f"{draw.randrange(24):02d}{draw.randrange(0, 60, 5):02d}",
                   f"{taxonomy.SAFE_HARBOR_REFERENCE_YEAR - (draw.randint(18, 104) if draw.random() < 0.3 else draw.randint(18, 89))}"]]
    found[5][3] = "19"
    return header, found


def _line_described(folder: pathlib.Path, name: str, header: "list[str]", rows: "list[list[str]]",
                    subjects: str) -> "tuple[pathlib.Path, pathlib.Path, dict[str, dict[str, object]]]":
    """The table written and described by the library under its person column with the Safe Harbor top-code (the
    command's rule at the table floor), clock figures read as the answer `clock-figures` reads them."""
    import dataclasses

    import fixtures

    table = _written(folder / f"{name}.csv", header, [[row[place] for row in rows] for place in range(len(header))])
    settings = dataclasses.replace(taxonomy.Settings(), person_columns=(subjects,),
                                   forced_clock_figures=tuple(one for one in header if one == "chart_time"))
    document = profile.build_document(
        reading.read_table(f"{table}"), settings, [subjects], [], [], subjects=[subjects], top_code=True,
        harbor_year=taxonomy.SAFE_HARBOR_REFERENCE_YEAR,
    )
    blocks = {f"{block['name']}": block for block in document["columns"]}  # type: ignore[union-attr]
    return table, fixtures.write_profile(folder, f"{name}-profile.json", document), blocks


def _never_read_whole(patch: pytest.MonkeyPatch, checked: pathlib.Path) -> None:
    """While ``checked`` is validated in groups, a whole reading of it, its whole bytes and its whole text are refused."""
    def it(place: object) -> bool:
        return pathlib.Path(f"{place}").resolve() == checked.resolve()

    reader = reading.read_table

    def in_groups_only(raw_path: str, *arguments: object, **options: object) -> reading.Table:
        assert not it(raw_path) or options.get("in_groups") is True, "the checked file was read whole"
        return reader(raw_path, *arguments, **options)  # type: ignore[arg-type]

    patch.setattr(reading, "read_table", in_groups_only)
    for name in ("_read_bytes", "_read_utf8", "_read_fallback"):
        whole = getattr(validation, name)

        def refused(place: pathlib.Path, _whole: "typing.Callable[[pathlib.Path], object]" = whole) -> object:
            assert not it(place), "the checked file's bytes or text were read whole"
            return _whole(place)

        patch.setattr(validation, name, refused)


def test_the_line_s_top_coded_and_time_columns_validate_alike_in_groups(tmp_path: pathlib.Path) -> None:
    """Two generated tables of the line's shapes, each described by the library under its person column with the Safe
    Harbor top-code, and each checked against its description in groups of one column and whole: the same exit, screen
    and files, and the checked file never read whole while it is read in groups.

    `_line_visits`, 1,000 people of 20 rows (the table floor, at which the description pools an age column's ends and
    its top category in people): ages in years, months, weeks and days, each top-coded in its unit with its ends;
    worded ages read with their words; bands past 89 read as one band. `_line_times`, 1,200 rows of 100 people: stamps
    under their rule at a grain, clock figures read as clock times at theirs, years of birth top-coded; checked as it
    is and with one stamp in the hour the clocks skip, which the rule's check misses.

    Red on the merge as git wrote it (batch 4s, step 10: read in groups, the line's top-coded columns were read without
    the age words, the ends and the bands their description records) and on the mutant reading the columns it rewrites
    from a whole reading of the file.
    """
    visits, described, blocks = _line_described(tmp_path, "visits", *_line_visits(random.Random(20261112), 1000, 20), "sid")
    for name, unit in (("age", "y"), ("age_in_months", "m"), ("age_in_weeks", "w"), ("age_in_days", "d")):
        assert blocks[name].get("top_coded") == taxonomy.AGE_MARKS[unit], (name, blocks[name].get("role"))
        assert blocks[name].get("top_coded_ends") and blocks[name].get("top_category_people") == ["sid"], name
    assert blocks["age_text"].get("top_coded_words") is True and blocks["age_band"].get("top_coded_bands") is True
    header, rows = _line_times(random.Random(701), 1200, 100)
    times, timed, held = _line_described(tmp_path, "times", header, rows, "sid")
    assert held["seen_at"].get("offset_rule") and held["seen_at"].get("time_grain"), held["seen_at"]
    assert held["chart_time"].get("clock_form") and held["birth_year"].get("top_coded_year"), held
    rows[3][1] = "2024-03-10 02:30:00-05:00"
    skipped = _written(tmp_path / "skipped.csv", header, [[row[place] for row in rows] for place in range(len(header))])
    found = 0
    for description, checked in ((described, visits), (timed, times), (timed, skipped)):
        expected = _validated(description, checked, tmp_path / "out")
        with pytest.MonkeyPatch.context() as groups:
            _one_column_a_group(groups)
            _never_read_whole(groups, checked)
            in_groups = _validated(description, checked, tmp_path / "out")
        assert in_groups == expected, (checked.name, expected[1][-1500:], in_groups[1][-1500:])
        assert expected[0] in (0, 3) and expected[2], expected[1][-600:]
        found += 1
    assert "offsets.rule [datetime.offset_rule]: MISSED" in _report_of(expected) and found == 3
