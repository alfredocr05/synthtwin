"""Lane SR of the December plan: read and describe in groups of columns (plan P4-D400).

THE GATE. The owner's big table is 2,000,000 rows by 50 columns, and
`synthtwin profile` must describe it inside the 2.5 GB one process may
hold (TRACKED.md, T5). Lane B0 measured the profile process on lane
S4d's tree at 476 / 818 / 1,463 MB at 100,000 / 250,000 / 500,000 rows
of the made-up 50-column health table -- 4,008 MB projected at 2,000,000
-- with the reader alone holding 395 / 758 / 1,308 MB of it: the file's
bytes, its decoded text and a Python text object a cell, every column at
once. The lane reads a table too large for one group of columns
(`reading.GROUP_BYTES`) ONE GROUP AT A TIME: the file is read a line at
a time, never whole; the survey holds one group's cells
(`dialect.survey`'s ``keep``); each group is walked, checked by the
standard reader and by pandas, and the checks' first differences are
weighed once every group is read; the description, the census and the
questions ask each column of `reading.column_values`, which holds one
group and reads the file again for the next. Nothing is written to disk:
the file is read again, and a file that changed between two readings is
refused.

WHAT THIS FILE PINS, every claim against the reading of the whole table,
which is the code before the lane:

1. Read in groups -- a group of one column, the smallest there is -- a
   table reads as it reads whole: every field of the Table and every
   value of every column, over shapes of every written form the reader
   knows (quoted line breaks, every line ending, a title line, a
   separator line, metadata rows, byte-order marks, UTF-16, Latin-1 and
   Windows-1252, an end-of-file mark, trailing delimiters, short rows,
   blank lines, a first row that is a record, comma-space files, which
   are walked whole, a text longer than the part the survey's detection
   reads), and the refusals are word for word the same over seeded
   adversarial files.
2. `synthtwin profile` of tables read one column a group writes the
   same files, byte for byte, and says the same words, on tables that
   raise every kind of question it asks.
3. The file's text is never read whole for a plain file, and the reader
   holds one group: the most `tracemalloc` sees `synthtwin profile`
   hold, reading a wide table one column a group, is under half what it
   holds reading it whole.
4. A file that changes between two readings is refused, however small
   the change, and no reading of it is mixed with another.
5. `reading.column_values` gives back any column, in any order, any
   number of times; `reading.column_groups` covers every column once.
6. No file is written beside the description: a run stopped by an error
   half way through the description leaves no file anywhere, in the
   output folder or beside the table.
"""

from __future__ import annotations

import contextlib
import dataclasses
import io
import os
import pathlib
import random
import tracemalloc
import warnings

import pytest

from synthtwin import cli, dialect, errors, profile, reading, taxonomy


def _read(path: pathlib.Path, first_row: str, in_groups: bool) -> "tuple[str, object]":
    """The reading, or the refusal's words."""
    try:
        return "read", reading.read_table(str(path), first_row, in_groups=in_groups)
    except errors.ProfileError as refusal:
        return "refused", f"{refusal}"


def _as_read(table: reading.Table) -> "tuple[object, ...]":
    """Every field of a Table and every value of every column; the survey without the cells it held."""
    surveyed = table.survey
    if surveyed is not None:
        surveyed = dataclasses.replace(surveyed, columns=[], kept=(), first_cells=())
    return (
        table.column_names,
        table.n_rows,
        table.encoding,
        table.used_fallback_encoding,
        table.header_source,
        table.header_evidence,
        table.header_by_convention,
        table.first_row_seen,
        surveyed,
        [reading.column_values(table, place) for place in range(len(table.column_names))],
    )


def _same_reading(path: pathlib.Path, first_row: str, monkeypatch: pytest.MonkeyPatch) -> "tuple[str, object]":
    """Read whole, then in groups of one column: the two must be the same, field for field or word for word."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        whole = _read(path, first_row, False)
        monkeypatch.setattr(reading, "GROUP_BYTES", 1)
        grouped = _read(path, first_row, True)
        monkeypatch.undo()
    assert whole[0] == grouped[0], (path.read_bytes()[:300], whole, grouped)
    if whole[0] == "refused":
        assert whole[1] == grouped[1]
        return whole
    assert isinstance(whole[1], reading.Table) and isinstance(grouped[1], reading.Table)
    assert _as_read(whole[1]) == _as_read(grouped[1]), path.read_bytes()[:300]
    return whole


# -- 1. the reading -----------------------------------------------------

_SHAPES: "dict[str, tuple[bytes, str]]" = {
    "quoted line breaks": (
        b'id,note,score\r\n1,"two\nlines",3.5\r\n2,"x, y",4.5\r\n3,plain,5.5\r\n'
        + b"".join(f"{k},n{k % 3},{k}.5\r\n".encode() for k in range(4, 40)),
        "auto",
    ),
    "carriage returns alone": (
        b"a;b;c\r" + b"".join(f"{k};x{k % 4};{k * 3}\r".encode() for k in range(30)),
        "auto",
    ),
    "a title and a separator line": (
        b"sep=,\nExtract for unit 7\nrecord_id,age,arm\n"
        + b"".join(f"R{k:03d},{20 + k % 50},{'AB'[k % 2]}\n".encode() for k in range(40)),
        "auto",
    ),
    "a utf-8 mark and an end-of-file mark": (
        b"\xef\xbb\xbfname,value\n" + b"".join(f"caf\xc3\xa9{k % 5},{k}\n".encode("latin-1") for k in range(30)) + b"\x1a",
        "auto",
    ),
    "utf-16 behind its mark": (
        "id\tlabel\r\n".encode("utf-16-le").join([b"\xff\xfe", b""])
        + "".join(f"{k}\tL{k % 4}\r\n" for k in range(30)).encode("utf-16-le"),
        "auto",
    ),
    "windows-1252": (
        b"word,n\n" + b"".join(b"\x93q\x94" + f"{k % 3},{k}\n".encode() for k in range(30)),
        "auto",
    ),
    "latin-1": (
        b"word,n\n" + b"".join(b"\xe9t\xe9" + f"{k % 3},{k}\n".encode() for k in range(30)),
        "auto",
    ),
    "trailing delimiters and short rows": (
        b"a,b,c,\n" + b"".join(f"{k},{k * 2},{k % 3},\n".encode() for k in range(30)),
        "auto",
    ),
    "blank lines between records": (
        b"a,b\n1,2\n\n3,4\n   \n5,6\n" + b"".join(f"{k},{k}\n".encode() for k in range(7, 40)),
        "auto",
    ),
    "a first row that is a record": (
        b"P001,34\n" + b"".join(f"P{k:03d},{30 + k % 9}\n".encode() for k in range(2, 40)),
        "auto",
    ),
    "a first row said to be data": (
        b"x,y,z\n" + b"".join(f"{k},{k % 7},w{k % 2}\n".encode() for k in range(30)),
        "data",
    ),
    "a quoted empty last name over shorter rows": (
        b'a;b;""\n' + b"".join(f"{k};{k % 4}\n".encode() for k in range(40)),
        "auto",
    ),
    "comma-space, walked whole": (
        b"a, b, c\n" + b"".join(f"{k}, x{k % 3},  {k}\n".encode() for k in range(30)),
        "auto",
    ),
    "names shown by a column": (
        b"site,count\n" + b"".join(f"s{k % 4},{k}\n".encode() for k in range(30)),
        "names",
    ),
}


@pytest.mark.parametrize("shape", sorted(_SHAPES))
def test_a_table_read_one_column_a_group_reads_as_it_reads_whole(
    shape: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data, first_row = _SHAPES[shape]
    path = tmp_path / "shape.csv"
    path.write_bytes(data)
    found = _same_reading(path, first_row, monkeypatch)
    assert found[0] == "read", found


def test_a_text_longer_than_detection_reads_is_read_a_line_at_a_time(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Past the survey's head (a MiB and some), the walk reads the lines it is handed, and nothing reads the whole file."""
    draw = random.Random(4)
    lines = ["id,code,amount,note,day"]
    for row in range(26_000):
        lines += [
            f"{row},C{draw.randrange(60)},\"{draw.randrange(1, 9)},{draw.randrange(1000):03d}.{draw.randrange(100):02d}\","
            f"word{draw.randrange(900)} and more,2024-{1 + row % 12:02d}-{1 + row % 28:02d}"
        ]
    path = tmp_path / "long.csv"
    path.write_bytes(("\r\n".join(lines) + "\r\n\x1a").encode())
    assert path.stat().st_size > 1_100_000
    _same_reading(path, "auto", monkeypatch)
    # ...and read in groups, the file's bytes are never read whole.
    def refused(*_arguments: object) -> bytes:
        raise AssertionError("the whole file was read")

    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    monkeypatch.setattr(pathlib.Path, "read_bytes", refused)
    table = reading.read_table(str(path), in_groups=True)
    assert table.source is not None and table.columns == []
    assert len(reading.column_values(table, 4)) == 26_000


_ALPHABET = [b"a", b"b", b"1", b"2", b",", b",", b'"', b"\r", b"\n", b"\r\n", b" ", b";", b"\\",
             b"x,y\n", b"c0,c1,c2\n", b"\xe9", b"\x1a", b"sep=,\n", b"#", b"\x00"]


def test_adversarial_files_are_read_or_refused_the_same_way_in_groups(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Seeded byte strings: the round-1 reproductions' alphabet, read whole and one column a group."""
    draw = random.Random(20261016)
    outcomes = {"read": 0, "refused": 0}
    path = tmp_path / "fuzz.csv"
    for _case in range(400):
        head = b"c0,c1,c2\n" if draw.random() < 0.6 else b""
        path.write_bytes(head + b"".join(draw.choice(_ALPHABET) for _ in range(draw.randrange(1, 50))))
        found = _same_reading(path, draw.choice(["auto", "auto", "names", "data"]), monkeypatch)
        outcomes[found[0]] += 1
    # Both outcomes are exercised.
    assert outcomes["read"] >= 25 and outcomes["refused"] >= 25, outcomes


def test_the_standard_readers_first_difference_is_the_one_refused_reading_every_column(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Round 1's reproduction: values that move between columns, refused in the same words read in groups."""
    path = tmp_path / "moved.csv"
    path.write_bytes(b"c0,c1\n\r,B\nz,w\n" + b"".join(f"v{k},w{k}\n".encode() for k in range(30)))
    found = _same_reading(path, "auto", monkeypatch)
    assert found[0] == "refused"


# -- 2. synthtwin profile -------------------------------------------------


def _table_of_every_question() -> str:
    """Columns that raise the codes question with codes elsewhere, the person question, the checklist, a clock and Q6."""
    draw = random.Random(17)
    lines = ["visit,patient,seen_on,code,amount,clock,ward,stay,taken,dose"]
    for row in range(400):
        seen = "00/00/0000" if row % 37 == 0 else f"{1 + row % 12:02d}/{1 + row % 12:02d}/2023"
        lines += [
            ",".join(
                [
                    f"V{row:05d}",
                    f"P{draw.randrange(120):04d}",
                    seen,
                    f"{draw.choice(['99213', '99214', '99215', '00000'])}",
                    f"{draw.gauss(80, 12):.1f}",
                    f"{draw.randrange(1, 13)}:{draw.choice(['00', '15', '30', '45'])}",
                    "00/00/0000" if row % 41 == 0 else draw.choice(["east", "west", "north"]),
                    f"{draw.randrange(1, 30)}",
                    f"2024-{1 + row % 12:02d}" if row % 3 else "2024-252",
                    f"{draw.choice([5, 10, 20])}",
                ]
            )
        ]
    return "\n".join(lines) + "\n"


def _profiled(table: pathlib.Path, out: pathlib.Path, options: "list[str]") -> "dict[str, bytes]":
    """`synthtwin profile`'s files and the words it says, the paths taken out."""
    out.mkdir()
    said = io.StringIO()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(["profile", str(table), "--out-dir", str(out), "--replace"] + options)
    found = {"exit": f"{code}".encode(), "said": said.getvalue().replace(str(out), "OUT").replace(str(table), "IN").encode()}
    for written in sorted(out.iterdir()):
        found[written.name] = written.read_bytes()
    return found


@pytest.mark.parametrize(
    "options",
    [[], ["--smallest-group", "1"], ["--identifier", "patient"], ["--smallest-group", "36", "--code", "ward"]],
)
def test_profile_read_one_column_a_group_writes_the_same_files(
    options: "list[str]", tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    table = tmp_path / "clinic.csv"
    table.write_text(_table_of_every_question(), encoding="utf-8")
    whole = _profiled(table, tmp_path / "whole", options)
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    grouped = _profiled(table, tmp_path / "groups", options)
    assert sorted(whole) == sorted(grouped)
    for name in whole:
        assert whole[name] == grouped[name], name
    assert b"questions" in b" ".join(name.encode() for name in whole), sorted(whole)


# -- 3. what is held ------------------------------------------------------


def test_profile_in_groups_holds_one_group_not_the_table(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A wide table of different values, read one column a group: what it holds, and what describing it holds.

    The reading holds one column of eight, under a quarter of what
    the whole reading holds; and the most `tracemalloc` sees held while
    `synthtwin profile` describes it is under half of what it holds
    describing the table read whole.
    """
    draw = random.Random(9)
    columns = 8
    lines = [",".join(f"note{k}" for k in range(columns))]
    for row in range(2_000):
        lines += [",".join(f"t{row}-{k}-{draw.randrange(10 ** 9)}" for k in range(columns))]
    table = tmp_path / "wide.csv"
    table.write_text("\n".join(lines) + "\n", encoding="utf-8")
    held: "list[int]" = []
    for budget in (1 << 40, 1):
        monkeypatch.setattr(reading, "GROUP_BYTES", budget)
        tracemalloc.start()
        try:
            before = tracemalloc.get_traced_memory()[0]
            read = reading.read_table(str(table), in_groups=True)
            held += [tracemalloc.get_traced_memory()[0] - before]
            del read
        finally:
            tracemalloc.stop()
    assert held[1] < 0.25 * held[0], held
    describing: "list[int]" = []
    built = profile.build_document

    def traced(*arguments: object, **named: object) -> "dict[str, object]":
        # The most held while describing, the table read included.
        tracemalloc.reset_peak()
        found = built(*arguments, **named)  # type: ignore[arg-type]
        describing.append(tracemalloc.get_traced_memory()[1])
        return found

    monkeypatch.setattr(profile, "build_document", traced)
    for budget in (1 << 40, 1):
        monkeypatch.setattr(reading, "GROUP_BYTES", budget)
        tracemalloc.start()
        try:
            found = _profiled(table, tmp_path / f"out{budget}", [])
        finally:
            tracemalloc.stop()
        assert found["exit"] == b"0"
    assert len(describing) == 2
    assert describing[1] < 0.5 * describing[0], describing


def test_a_table_read_in_groups_holds_one_group(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    table = tmp_path / "t.csv"
    table.write_text("a,b,c,d,e\n" + "".join(f"{k},{k * 2},x{k},y{k % 5},{k % 3}\n" for k in range(60)), encoding="utf-8")
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    read = reading.read_table(str(table), in_groups=True)
    source = read.source
    assert source is not None
    assert reading.column_groups(read) == ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5))
    assert source.held_from == 0 and len(source.held) == 1
    reading.column_values(read, 3)
    assert source.held_from == 3 and len(source.held) == 1


# -- 4. a file that changes ----------------------------------------------


@pytest.mark.parametrize("change", ["a value", "a row more", "the moment it changed"])
def test_a_file_that_changes_between_readings_is_refused(
    change: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    table = tmp_path / "t.csv"
    text = "a,b,c\n" + "".join(f"{k},{k * 2},x{k}\n" for k in range(60))
    table.write_text(text, encoding="utf-8")
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    read = reading.read_table(str(table), in_groups=True)
    assert reading.column_values(read, 0)[5] == "5"
    seen = table.stat()
    if change == "a value":
        table.write_text(text.replace("x7\n", "x8\n"), encoding="utf-8")
        os.utime(table, ns=(seen.st_atime_ns, seen.st_mtime_ns))
    elif change == "a row more":
        table.write_text(text + "61,122,x61\n", encoding="utf-8")
    else:
        os.utime(table, ns=(seen.st_atime_ns, seen.st_mtime_ns + 1_000_000_000))
    with pytest.raises(errors.ProfileError) as refused:
        reading.column_values(read, 2)
    assert f"{refused.value}" == errors.file_changed_while_read(str(table))


def test_a_file_that_changes_while_its_groups_are_walked_is_refused(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    table = tmp_path / "t.csv"
    text = "a,b,c\n" + "".join(f"{k},{k * 2},x{k}\n" for k in range(60))
    table.write_text(text, encoding="utf-8")
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    first_reading = reading._facts_under

    def then_changed(*arguments: object) -> object:
        found = first_reading(*arguments)  # type: ignore[arg-type]
        seen = table.stat()
        table.write_text(text.replace("x7\n", "x8\n"), encoding="utf-8")
        os.utime(table, ns=(seen.st_atime_ns, seen.st_mtime_ns))
        return found

    monkeypatch.setattr(reading, "_facts_under", then_changed)
    with pytest.raises(errors.ProfileError) as refused:
        reading.read_table(str(table), in_groups=True)
    assert f"{refused.value}" == errors.file_changed_while_read(str(table))


# -- 5. the generic column access ----------------------------------------


def test_any_column_in_any_order_any_number_of_times(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    table = tmp_path / "t.csv"
    rows = [[f"{k}", f"{k % 7}", f"w{k % 3}", f"{k * 0.5}", f"z{k}", ""] for k in range(80)]
    table.write_text("a,b,c,d,e,f\n" + "".join(",".join(row) + "\n" for row in rows), encoding="utf-8")
    whole = reading.read_table(str(table))
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    grouped = reading.read_table(str(table), in_groups=True)
    draw = random.Random(3)
    for _ask in range(30):
        place = draw.randrange(6)
        assert reading.column_values(grouped, place) == whole.columns[place]
        assert reading.column_values(whole, place) is whole.columns[place]
    covered = [place for start, end in reading.column_groups(grouped) for place in range(start, end)]
    assert covered == list(range(6))
    assert reading.column_groups(whole) == ((0, 6),)


# -- 6. nothing written beside the description ----------------------------


def test_a_run_stopped_half_way_through_the_description_leaves_no_file(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = tmp_path / "in"
    folder.mkdir()
    table = folder / "t.csv"
    table.write_text(
        "a,b,c,d\n" + "".join(f"{k},{k % 9},x{k % 4},{k * 3}\n" for k in range(300)), encoding="utf-8"
    )
    out = tmp_path / "out"
    out.mkdir()
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    described = taxonomy.profile_column
    asked: "list[str]" = []

    def stopped(name: str, *arguments: object, **named: object) -> object:
        asked.append(name)
        if len(asked) == 3:
            raise RuntimeError("stopped half way through the description")
        return described(name, *arguments, **named)  # type: ignore[arg-type]

    monkeypatch.setattr(taxonomy, "profile_column", stopped)
    with pytest.raises(RuntimeError):
        cli.main(["profile", str(table), "--out-dir", str(out), "--replace"])
    assert asked == ["a", "b", "c"]
    assert sorted(path.name for path in folder.iterdir()) == ["t.csv"]
    assert not out.exists() or not any(out.iterdir())
    leftovers = [path for path in tmp_path.rglob("*") if path.is_file() and path != table]
    assert leftovers == []


def test_the_survey_names_the_columns_it_held(tmp_path: pathlib.Path) -> None:
    """`dialect.survey`'s ``keep``: every record read whole, the named columns held, the others left empty."""
    text = "a,b,c\n" + "".join(f"{k},{k % 4},x{k}\n" for k in range(20))
    whole = dialect.settle(text, "utf-8", False, False, "t.csv")
    held = dialect.settle(text, "utf-8", False, False, "t.csv", keep=(False, True, False))
    assert held.kept == (False, True, False)
    assert held.columns[1] == whole.columns[1] and held.columns[0] == [] and held.columns[2] == []
    assert held.n_rows == whole.n_rows and held.first_cells == whole.first_cells
    assert held.form.columns[1] == whole.form.columns[1]


def test_the_affixed_split_memo_holds_at_most_its_bound_and_answers_the_same() -> None:
    """`taxonomy._split_once` past `parsing.SPELLING_MEMO_TEXTS`: the same split, and no more texts held (plan P4-D400).

    A column of different record numbers held a split, its core and their
    place in the memo a row; past the bound a text is split again.
    """
    from synthtwin import parsing

    cells = taxonomy._tally(taxonomy._classify_all(["V1", "V2"]), 2, taxonomy.Settings())
    texts = [f"V{row:09d}" for row in range(parsing.SPELLING_MEMO_TEXTS + 500)]
    for text in texts + texts[:10] + texts[-10:]:
        assert taxonomy._split_once(cells, text) == taxonomy.affixed_split(text, cells.decimal_comma)
    assert len(cells.affixes[cells.decimal_comma]) == parsing.SPELLING_MEMO_TEXTS
