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
   blank lines, a first row that is a record, comma-space files, a text
   longer than the part the survey's detection reads), and the refusals
   are word for word the same over seeded adversarial files.
2. `synthtwin profile` of tables read one column a group writes the
   same files, byte for byte, and says the same words, on tables that
   raise every kind of question it asks.
3. The file's text is never read whole for a plain file, and the reader
   holds one group: the most `tracemalloc` sees `synthtwin profile`
   hold, reading a wide table one column a group, is under half what it
   holds reading it whole; and each walk is read only once the walk
   before it is let go.
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
import weakref

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
        # One column a group and a group a walk: the finest the reading goes.
        monkeypatch.setattr(reading, "GROUP_BYTES", 1)
        monkeypatch.setattr(reading, "WALK_BYTES", 1)
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
    "records that hold nothing, and an order": (
        b"n,a,b\n" + b"".join((b",,\n" if k % 7 == 3 else f"{k},x{k % 3},{40 - k}\n".encode()) for k in range(40)),
        "auto",
    ),
    "a quoted empty last name over shorter rows": (
        b'a;b;""\n' + b"".join(f"{k};{k % 4}\n".encode() for k in range(40)),
        "auto",
    ),
    "comma-space": (
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
        # The first column holds nothing on some rows, so the census asks
        # the columns after it which rows hold a value.
        seen = "00/00/0000" if row % 37 == 0 else f"{1 + row % 12:02d}/{1 + row % 12:02d}/2023"
        lines += [
            ",".join(
                [
                    "" if row % 9 == 4 else f"V{row:05d}",
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


@pytest.mark.parametrize("walk", [1, 3])
@pytest.mark.parametrize(
    "options",
    [[], ["--smallest-group", "1"], ["--identifier", "patient"], ["--smallest-group", "36", "--code", "ward"]],
)
def test_profile_read_one_column_a_group_writes_the_same_files(
    options: "list[str]", walk: int, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    table = tmp_path / "clinic.csv"
    table.write_text(_table_of_every_question(), encoding="utf-8", newline="\n")
    whole = _profiled(table, tmp_path / "whole", options)
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    # One column a group; a walk of one group, or of every group.
    monkeypatch.setattr(reading, "WALK_BYTES", 1 if walk == 1 else 1 << 40)
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
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
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
    table.write_text("a,b,c,d,e\n" + "".join(f"{k},{k * 2},x{k},y{k % 5},{k % 3}\n" for k in range(60)), encoding="utf-8", newline="\n")
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    read = reading.read_table(str(table), in_groups=True)
    source = read.source
    assert source is not None
    assert reading.column_groups(read) == ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5))
    assert source.held_places == (0,) and len(source.held) == 1
    reading.column_values(read, 3)
    assert source.held_places == (3,) and len(source.held) == 1


# -- 4. a file that changes ----------------------------------------------


@pytest.mark.parametrize("change", ["a value", "a row more", "the moment it changed"])
def test_a_file_that_changes_between_readings_is_refused(
    change: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    table = tmp_path / "t.csv"
    text = "a,b,c\n" + "".join(f"{k},{k * 2},x{k}\n" for k in range(60))
    table.write_text(text, encoding="utf-8", newline="\n")
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    read = reading.read_table(str(table), in_groups=True)
    assert reading.column_values(read, 0)[5] == "5"
    seen = table.stat()
    if change == "a value":
        table.write_text(text.replace("x7\n", "x8\n"), encoding="utf-8", newline="\n")
        os.utime(table, ns=(seen.st_atime_ns, seen.st_mtime_ns))
    elif change == "a row more":
        table.write_text(text + "61,122,x61\n", encoding="utf-8", newline="\n")
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
    table.write_text(text, encoding="utf-8", newline="\n")
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    first_reading = reading._facts_under

    def then_changed(*arguments: object) -> object:
        found = first_reading(*arguments)  # type: ignore[arg-type]
        seen = table.stat()
        table.write_text(text.replace("x7\n", "x8\n"), encoding="utf-8", newline="\n")
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
    table.write_text("a,b,c,d,e,f\n" + "".join(",".join(row) + "\n" for row in rows), encoding="utf-8", newline="\n")
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
        "a,b,c,d\n" + "".join(f"{k},{k % 9},x{k % 4},{k * 3}\n" for k in range(300)), encoding="utf-8", newline="\n"
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


def test_a_label_written_one_way_otherwise_than_itself_holds_that_spelling_not_a_map() -> None:
    """`taxonomy._tally` holds a label only ever written `V000007` as that text; `_label_spellings` answers as before (plan P4-D400).

    A column of record numbers that never repeat held a map of one entry
    a row, about 184 bytes; the map begins at a label's second spelling,
    the first spelling first, with every earlier row it counted.
    """
    cells = [f"V{row:06d}" for row in range(1_000)] + ["ABC", "ABC", "Abc", "ABC", "abc", "x", "X", "Q", "Q"]
    tallied = taxonomy._tally(taxonomy._classify_all(cells), len(cells), taxonomy.Settings())
    held = tallied.spellings_by_folded
    assert held["v000007"] == "V000007"
    assert taxonomy._label_spellings(tallied.folded_counts, held, "v000007") == {"V000007": 1}
    assert list(taxonomy._label_spellings(tallied.folded_counts, held, "abc").items()) == [
        ("ABC", 3), ("Abc", 1), ("abc", 1),
    ]
    assert list(taxonomy._label_spellings(tallied.folded_counts, held, "x").items()) == [("x", 1), ("X", 1)]
    assert taxonomy._label_spellings(tallied.folded_counts, held, "q") == {"Q": 2}
    assert sum(1 for label in held if isinstance(held[label], dict)) == 2


def test_the_first_difference_of_either_check_is_the_one_refused_in_groups(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Differences in two groups, at two rows: the refusal names the first, as the reading of every column does.

    The standard reader is made to read two cells otherwise than the
    survey -- the third column at the fourth record, the first column at
    the eighth -- so each group's walk finds its own; weighed together,
    the fourth record's is refused.
    """
    path = tmp_path / "t.csv"
    path.write_text("a,b,c\n" + "".join(f"{k},{k * 2},x{k}\n" for k in range(40)), encoding="utf-8", newline="\n")
    standard = reading._standard_records

    def otherwise(*arguments: object) -> object:
        row = 0
        for kind, cells in standard(*arguments):  # type: ignore[arg-type]
            if kind == reading._RECORD_DATA:
                if row == 3:
                    cells = cells[:2] + ["changed"]
                if row == 7:
                    cells = ["changed"] + cells[1:]
                row = row + 1
            yield kind, cells

    monkeypatch.setattr(reading, "_standard_records", otherwise)
    found = _same_reading(path, "auto", monkeypatch)
    assert found == ("refused", errors.readers_disagree_about_a_value(str(path), 4, "c"))


def test_a_run_of_groups_is_held_together(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`reading.hold_columns` reads a run of groups at once, and `column_values` hands each over without reading again."""
    table = tmp_path / "t.csv"
    table.write_text("a,b,c,d,e\n" + "".join(f"{k},{k * 2},x{k},y{k % 5},{k % 3}\n" for k in range(60)), encoding="utf-8", newline="\n")
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    read = reading.read_table(str(table), in_groups=True)
    reading.hold_columns(read, (3, 4))
    source = read.source
    assert source is not None and source.held_places == (3, 4) and len(source.held) == 2
    reads: "list[int]" = []
    group_read = reading._read_group

    def counted(*arguments: object) -> object:
        reads.append(1)
        return group_read(*arguments)  # type: ignore[arg-type]

    monkeypatch.setattr(reading, "_read_group", counted)
    assert reading.column_values(read, 4) == [f"{k % 3}" for k in range(60)]
    assert reading.column_values(read, 3)[2] == "y2"
    assert reads == []


def test_the_walk_held_before_is_let_go_before_the_next_walk_is_read(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The reading takes each walk after the one before is let go, so two walks' cells are never held at once."""
    table = tmp_path / "t.csv"
    table.write_text("a,b,c\n" + "".join(f"{k},x{k},{k % 7}\n" for k in range(80)), encoding="utf-8", newline="\n")
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    monkeypatch.setattr(reading, "WALK_BYTES", 1)
    walked: "list[weakref.ref[object]]" = []
    alive_when_read: "list[int]" = []
    walk = reading._walk_a_group

    def watched(*arguments: object) -> object:
        if arguments[5]:
            alive_when_read.append(sum(1 for one in walked if one() is not None))
        found = walk(*arguments)  # type: ignore[arg-type]
        if arguments[5]:
            walked.append(weakref.ref(found[0]))  # type: ignore[index]
        return found

    monkeypatch.setattr(reading, "_walk_a_group", watched)
    read = reading.read_table(str(table), in_groups=True)
    assert reading.column_groups(read) == ((0, 1), (1, 2), (2, 3))
    assert alive_when_read == [0, 0, 0]
    assert reading.column_values(read, 1)[3] == "x3"


# -- 7. skeptic 1's and Codex's review of the lane (repair 1) -------------
#
# Each case below is red on the mutant named in its docstring
# (planning-notes/work-2026-10/wave6/SR/repair1/mutants.py and its log).
# 8. A walk the survey makes again reads the file's lines afresh and
#    holds no earlier walk; a text repeated late is shared when read
#    again; a record no longer where it was is a changed file; the
#    columns held are let go before the next are read; a file changed
#    while pandas or the survey reads it is refused; a text is measured
#    at its own width, and groups and walks are cut by those bytes; the
#    census reads one declared column at a time; the measuring driver
#    records no peak it could not read.


def _walk_entries(path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> "list[tuple[object, int]]":
    """Read ``path`` one column a group: at each walk the survey makes, the columns it holds and the bytes traced above what was traced when that group's settling began."""
    entries: "list[tuple[object, int]]" = []
    began = [0]
    walked = dialect.survey
    settled = dialect.settle

    def settling(*arguments: object, **named: object) -> object:
        began[0] = tracemalloc.get_traced_memory()[0]
        return settled(*arguments, **named)  # type: ignore[arg-type]

    def entered(*arguments: object, **named: object) -> object:
        keep = named.get("keep", arguments[14] if len(arguments) > 14 else None)
        if named.get("quoted_closing", arguments[13] if len(arguments) > 13 else None) is not None:
            entries.append((keep, tracemalloc.get_traced_memory()[0] - began[0]))
        return walked(*arguments, **named)  # type: ignore[arg-type]

    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    monkeypatch.setattr(reading, "WALK_BYTES", 1)
    monkeypatch.setattr(dialect, "survey", entered)
    monkeypatch.setattr(dialect, "settle", settling)
    tracemalloc.start()
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            reading.read_table(str(path), in_groups=True)
    finally:
        tracemalloc.stop()
        monkeypatch.undo()
    return entries


def _long_rows(row: int) -> "list[str]":
    """Three cells of about fifty characters, different on every row."""
    return [f"{row:06d}{'q' * 40}{row % 97:03d}", f"w{row}-{'z' * 44}", f"{row * 7:09d}{'m' * 38}"]


_RETRIED: "dict[str, bytes]" = {
    # Comma-space guessed from the first records, broken by two spaces
    # late in the file: walked again without the space.
    "comma-space shown wrong": (
        "a, b, c\n"
        + "".join(", ".join(_long_rows(row)) + "\n" for row in range(2_500))
        + "x,  y, z\n"
    ).encode(),
    # A doubled-quote reading leaving text after a closing quote, which
    # the backslash reading reads clean: walked again with backslashes.
    "a malformed doubled quote read with backslashes": (
        "a,b,c\n"
        + "".join(",".join(_long_rows(row)) + "\n" for row in range(2_500))
        + '1,"x\\"y",3\n'
    ).encode(),
    # The doubled-quote reading refused (a field split in three), the
    # backslash reading clean: the refusal kept while the next walk is made.
    "a refusal then the backslash reading": (
        "a,b\n"
        + "".join(f"{_long_rows(row)[0]},{_long_rows(row)[1]}\n" for row in range(2_500))
        + '1,"hello \\"quoted, text\\""\n'
    ).encode(),
    # Every walk reading `""` as a value refused, the walks made again
    # reading it as a closing (lane R6's table, Codex's case, long).
    "a closing written two quotes": (
        "site;dx\n"
        + f"{_long_rows(0)[0]};{_long_rows(0)[1]};\"\"\n"
        + "".join(f"{_long_rows(row)[0]};{_long_rows(row)[1]};\n" for row in range(1, 2_500))
    ).encode(),
    # Trailing delimiters guessed and broken: walked again without them.
    "trailing delimiters shown wrong": (
        "a,b,c,\n"
        + "".join(",".join(_long_rows(row)) + ",\n" for row in range(2_500))
        + "1,2,3,4\n"
    ).encode(),
}


@pytest.mark.parametrize("shape", sorted(_RETRIED))
def test_a_walk_made_again_holds_no_earlier_walk_and_reads_no_whole_text(
    shape: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Skeptic 1, item 4, and Codex's item 3: a walk made again reads the lines afresh, and no earlier walk's cells are held beside it.

    Read in groups, as read whole; the file's bytes never read whole nor
    decoded whole; and at every walk the survey makes, the bytes traced
    are within a third of one column's cells of what was traced when the
    settling of that group began -- so no walk is held while the next is
    made -- except beside a walk holding no column, which may be made
    beside the one walk it may replace. Red on each mutant: the walk shown wrong kept (`del found`
    taken out), the refusal kept with its frames (`_let_go` taken out),
    the backslash reading tried holding the columns beside the walk it
    may replace, the trailing retry made beside its walk's cells.
    """
    path = tmp_path / "retried.csv"
    path.write_bytes(_RETRIED[shape])
    found = _same_reading(path, "auto", monkeypatch)
    assert found[0] == "read", found

    def refused(*_arguments: object) -> object:
        raise AssertionError("the whole file was read or decoded")

    monkeypatch.setattr(pathlib.Path, "read_bytes", refused)
    monkeypatch.setattr(dialect, "decoded", refused)
    monkeypatch.setattr(dialect, "decoded_as", refused)
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    table = reading.read_table(str(path), in_groups=True)
    assert table.source is not None and len(reading.column_values(table, 1)) >= 2_500
    monkeypatch.undo()
    entries = _walk_entries(path, monkeypatch)
    # Some walk was made again.
    assert len(entries) > 2 * len(table.column_names) + 1, entries
    one_column = 2_500 * 100
    for keep, above in entries:
        if keep is None or True in keep:  # type: ignore[operator]
            assert above < one_column // 3, (shape, keep, entries)
        else:
            # A walk holding no column may be made beside the one walk
            # it may replace, and holds nothing itself.
            assert above < one_column * 3 // 2, (shape, keep, entries)


def test_a_text_repeated_late_in_a_column_is_shared_when_read_again(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Codex's item 1: past `parsing.SPELLING_MEMO_TEXTS` different texts, a text written on every later row is held once, read again as the survey holds it.

    Red on the mutant that keeps only the bound (`_read_group`'s memo as
    shipped at dad8ed3e): one text a row.
    """
    from synthtwin import parsing

    late = "n" * 300
    rows = parsing.SPELLING_MEMO_TEXTS + 2_000
    table = tmp_path / "late.csv"
    with table.open("w", encoding="utf-8", newline="\n") as out:
        out.write("k,note\n")
        for row in range(rows):
            note = f"t{row}" if row < parsing.SPELLING_MEMO_TEXTS else late
            out.write(f"{row % 5},{note}\n")
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    read = reading.read_table(str(table), in_groups=True)
    reading.column_values(read, 0)
    cells = reading.column_values(read, 1)
    assert cells[rows - 1] == late
    held = {id(cells[row]) for row in range(parsing.SPELLING_MEMO_TEXTS, rows)}
    assert len(held) <= 2, len(held)


@pytest.mark.parametrize("change", ["a record shorter", "a value too long to read"])
def test_a_record_no_longer_where_it_was_is_refused_as_a_changed_file(
    change: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Codex's item 5: a file whose records moved since the first reading is refused in the catalogued words, never an IndexError or a csv error.

    Red on the mutant that catches only OSError and UnicodeDecodeError
    around the reading again.
    """
    table = tmp_path / "t.csv"
    text = "a,b,c\n" + "".join(f"{k},{k * 2},x{k}\n" for k in range(60))
    table.write_text(text, encoding="utf-8", newline="\n")
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    read = reading.read_table(str(table), in_groups=True)
    if change == "a record shorter":
        table.write_text(text.replace("7,14,x7\n", "7,14\n"), encoding="utf-8", newline="\n")
    else:
        table.write_text(text.replace(",x7\n", ",x" + "7" * 300 + "\n"), encoding="utf-8", newline="\n")
        monkeypatch.setattr(reading, "FIELD_SIZE_LIMIT", 100)
    with pytest.raises(errors.ProfileError) as refused:
        reading.column_values(read, 2)
    assert f"{refused.value}" == errors.file_changed_while_read(str(table))


def test_the_columns_held_are_let_go_before_the_next_are_read(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Skeptic 1, item 5 (M8): `column_values` and `hold_columns` let go of what they hold before reading the next columns.

    Red on the mutant that reads the next group while the one held is
    still held.
    """
    table = tmp_path / "t.csv"
    table.write_text("a,b,c,d\n" + "".join(f"{k},x{k},{k % 7},y{k}\n" for k in range(80)), encoding="utf-8", newline="\n")
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    read = reading.read_table(str(table), in_groups=True)
    source = read.source
    assert source is not None
    held_when_read: "list[int]" = []
    group_read = reading._read_group

    def watched(*arguments: object) -> object:
        held_when_read.append(len(source.held))
        return group_read(*arguments)  # type: ignore[arg-type]

    monkeypatch.setattr(reading, "_read_group", watched)
    assert reading.column_values(read, 2)[3] == "3"
    reading.hold_columns(read, (0, 3))
    assert reading.column_values(read, 3)[1] == "y1" and reading.column_values(read, 0)[4] == "4"
    assert reading.column_values(read, 1)[5] == "x5"
    assert held_when_read == [0, 0, 0]


def test_a_file_changed_while_pandas_reads_it_is_refused(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Skeptic 1, item 5 (M3): a file whose moment of change moves while pandas reads it is refused, even where pandas read the same values.

    Red on the mutant that makes `reading._still_the_same` inert: a
    table that fits one walk is read no more after pandas.
    """
    table = tmp_path / "t.csv"
    table.write_text("a,b\n" + "".join(f"{k},w{k % 9}\n" for k in range(60)), encoding="utf-8", newline="\n")
    read_by_pandas = reading.pandas.read_csv

    def touched(*arguments: object, **named: object) -> object:
        found = read_by_pandas(*arguments, **named)  # type: ignore[call-overload]
        seen = table.stat()
        os.utime(table, ns=(seen.st_atime_ns, seen.st_mtime_ns + 2_000_000_000))
        return found

    monkeypatch.setattr(reading.pandas, "read_csv", touched)
    with pytest.raises(errors.ProfileError) as refused:
        reading.read_table(str(table), in_groups=True)
    assert f"{refused.value}" == errors.file_changed_while_read(str(table))


def test_what_a_text_costs_to_hold_is_never_less_than_python_holds_it_in() -> None:
    """Codex's item 4: the survey's measure of a column's cells counts each text at its own width.

    Every text is measured at least at what `sys.getsizeof` says it
    holds, on this Python; a column of texts carrying one character
    beyond the Basic Multilingual Plane measures four bytes a character.
    Red on the mutant that measures characters as bytes.
    """
    import sys

    for text in ["a", "ab" * 30, "é" * 7, "café", "€" * 11, "x\U0001f600" * 50, "\U0001f600"]:
        assert dialect._stored_bytes(text) >= sys.getsizeof(text), text
    texts = [f"{row:05d}" + "q" * 94 + "\U0001f600" for row in range(40)]
    surveyed = dialect.settle(
        "a,b\n" + "".join(f"{row},{texts[row]}\n" for row in range(40)), "utf-8", False, False, "t.csv", keep=()
    )
    assert surveyed.cell_bytes[1] >= sum(sys.getsizeof(text) for text in texts)
    assert surveyed.cell_bytes[1] >= 40 * 4 * 100


def test_wide_columns_are_grouped_and_walked_by_their_own_bytes(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Skeptic 1, item 3: four adjacent note columns beside six short ones; groups and walks cut by each column's bytes, and no walk holds more than its budget.

    A note column costs about a megabyte here and a short one a seventh
    of that: with a group of a MiB and a walk of two, every note column
    is a group of its own, the short columns share groups, and the cells
    each walk holds -- every text as `sys.getsizeof` says, and its place
    in the column -- stay within the walk's budget. Red on the mutant
    that sizes groups by the table's average cell and walks six groups
    at a time (every column in one walk here).
    """
    import sys

    draw = random.Random(31)
    rows = 2_000
    lines = ["k0,k1,k2,note0,note1,note2,note3,k3,k4,k5"]
    for row in range(rows):
        notes = [" ".join(f"w{draw.randrange(10 ** 6)}" for _word in range(55)) for _note in range(4)]
        lines += [",".join([f"{row}", f"{row % 7}", f"c{row % 3}"] + notes + [f"{row * 3}", "x", f"{row % 11}"])]
    table = tmp_path / "notes.csv"
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    mebibyte = 1024 * 1024
    monkeypatch.setattr(reading, "GROUP_BYTES", mebibyte)
    monkeypatch.setattr(reading, "WALK_BYTES", 2 * mebibyte)
    held_a_walk: "list[int]" = []
    walk = reading._walk_a_group

    def weighed(*arguments: object) -> object:
        found = walk(*arguments)  # type: ignore[arg-type]
        cells = 0
        for column in found[0].columns:  # type: ignore[index]
            shared: "set[int]" = set()
            for value in column:
                cells = cells + 8
                if id(value) not in shared:
                    shared.add(id(value))
                    cells = cells + sys.getsizeof(value)
        held_a_walk.append(cells)
        return found

    monkeypatch.setattr(reading, "_walk_a_group", weighed)
    read = reading.read_table(str(table), in_groups=True)
    assert reading.column_groups(read) == ((0, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 10))
    assert reading.column_walks(read) == ((0, 4), (4, 6), (6, 10))
    # The walk that plans holds nothing; each other walk holds its cells.
    assert held_a_walk[0] == 0 and len(held_a_walk) == 4
    assert max(held_a_walk) <= 2 * mebibyte, held_a_walk
    assert max(held_a_walk) > mebibyte, held_a_walk
    whole = reading.read_table(str(table))
    for place in range(10):
        assert reading.column_values(read, place) == whole.columns[place]


@pytest.mark.parametrize("declared", [["patient", "visit"], ["patient", "ward", "dose"]])
def test_the_census_of_several_identifiers_counts_as_the_whole_census_counts(
    declared: "list[str]", tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Codex's item 2: several declared identifiers, counted one column at a time, as the whole census counts them."""
    table = tmp_path / "clinic.csv"
    table.write_text(_table_of_every_question(), encoding="utf-8", newline="\n")
    settings = taxonomy.Settings()
    whole = reading.read_table(str(table))
    expected = profile.population_census_of(whole, settings, declared, [], [], [], ())
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    grouped = reading.read_table(str(table), in_groups=True)
    found = profile.population_census_of(grouped, settings, declared, [], [], [], ())
    assert found[:2] == expected[:2]
    assert found[0], found


def test_rows_naming_nobody_are_one_unknown_person_counted_in_groups(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`taxonomy.people_counted`: rows that hold a value but name no person are one more person, as `taxonomy.people_in` counts them.

    Red on the mutant that counts without the rows holding a value.
    """
    table = tmp_path / "people.csv"
    table.write_text(
        "p,x\n" + "".join(f"{'' if row % 7 == 0 else f'P{row // 3:04d}'},{row % 5}\n" for row in range(420)),
        encoding="utf-8",
        newline="\n",
    )
    settings = taxonomy.Settings()
    whole = reading.read_table(str(table))
    expected = profile.population_census_of(whole, settings, ["p"], [], [], [], ())
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    grouped = reading.read_table(str(table), in_groups=True)
    found = profile.population_census_of(grouped, settings, ["p"], [], [], [], ())
    named = {f"P{row // 3:04d}" for row in range(420) if row % 7}
    assert found[:2] == expected[:2] == (("p",), len(named) + 1)


def test_the_census_holds_one_declared_column_at_a_time(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Codex's item 2: twelve declared identifiers of long codes, read one column a group; the census holds about one column's cells, never all twelve.

    The most `tracemalloc` sees held while `profile.population_census_of`
    counts the table read one column a group, above what the table held
    before, is under twice what reading one column and its census
    reading hold; and it counts as the whole census counts. Red on the
    mutant that gathers every declared column before counting.
    """
    rows = 3_000
    names = [f"id{k}" for k in range(12)]
    table = tmp_path / "ids.csv"
    table.write_text(
        ",".join(names) + "\n"
        + "".join(",".join(f"{k}-{row // 2:06d}-{'c' * 60}" for k in range(12)) + "\n" for row in range(rows)),
        encoding="utf-8",
        newline="\n",
    )
    settings = taxonomy.Settings()
    whole = reading.read_table(str(table))
    expected = profile.population_census_of(whole, settings, names, [], [], [], ())
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    grouped = reading.read_table(str(table), in_groups=True)
    tracemalloc.start()
    try:
        reading.column_values(grouped, 11)
        before = tracemalloc.get_traced_memory()[0]
        tracemalloc.reset_peak()
        taxonomy.repeats_in(reading.column_values(grouped, 0), "id0", settings)
        one_column = tracemalloc.get_traced_memory()[1] - before
        reading.column_values(grouped, 11)
        before = tracemalloc.get_traced_memory()[0]
        tracemalloc.reset_peak()
        found = profile.population_census_of(grouped, settings, names, [], [], [], ())
        census = tracemalloc.get_traced_memory()[1] - before
    finally:
        tracemalloc.stop()
    assert found[:2] == expected[:2] and len(found[0]) == 12
    assert census < 2 * one_column, (census, one_column)




def _the_driver() -> object:
    """`tools/measurements/kpi_describe_groups.py`, imported from its path."""
    import importlib.util

    path = pathlib.Path(__file__).resolve().parents[1] / "tools" / "measurements" / "kpi_describe_groups.py"
    spec = importlib.util.spec_from_file_location("kpi_describe_groups_under_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("resident", [True, False])
def test_the_driver_records_no_peak_it_could_not_read(resident: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 6, and skeptic 1's items 2 and 6: the measuring driver's keys.

    Where resident memory cannot be read (`_resident_peak` -1, as on
    Windows), no peak and no projection of one is recorded, and the
    evidence says so, while the CPU seconds and the traced bytes are
    kept; where it can, the mixed table is projected from its three
    largest sizes (1,000,000 rows the largest) and each Gaussian size is
    the largest peak of its hash seeds. Red on the mutant that records
    the -1 as a peak.
    """
    driver = _the_driver()
    runs: "list[tuple[str, str]]" = []

    def child(table: str, out: pathlib.Path, _budget: int, trace: bool, seed: str = "0") -> "dict[str, object]":
        if not trace:
            runs.append((table, seed))
        # The rows are in the run's folder name (`measure` names it so).
        rows = int(out.name.split("-")[1]) if out.name.count("-") == 2 else 0
        mebibytes = 80 + rows / 10_000 + (50 if seed == "2" else 0)
        peak = -1 if not resident else int(mebibytes * driver.MEBIBYTE)  # type: ignore[attr-defined]
        return {"exit": 0, "cpu_seconds": rows / 10_000, "peak_rss_bytes": peak, "traced_peak_bytes": 4_000_000 if trace else -1}

    monkeypatch.setattr(driver, "_child", child)
    monkeypatch.setattr(driver, "write", lambda _kind, _rows, path: path.write_text("x\n", encoding="utf-8"))
    memory, seconds = driver.measure()  # type: ignore[attr-defined]
    peaks = [key for key in memory if "_peak_mb" in key or key == "imports_mb"]
    assert "mixed_describe_seconds_2m_projected" in seconds and "gaussian_describe_cpu_seconds" in seconds
    assert memory["mixed_traced_bytes_a_cell"] == 0.4
    if not resident:
        assert peaks == [] and "unavailable" in f"{memory['resident_memory']}"
        return
    assert "resident_memory" not in memory
    assert len(memory["mixed_describe_peak_mb"]) == 4 and memory["sizes"]["mixed"][-1] == 1_000_000
    assert memory["gaussian_describe_peak_mb"] == [140.0, 155.0, 180.0]
    assert memory["mixed_describe_peak_mb_2m_projected"] == 280.0
    assert sorted({seed for table, seed in runs if table.endswith("gaussian.csv")}) == ["1", "2", "3"]


def test_a_file_changed_only_while_the_survey_walks_it_is_refused(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every walk the survey reads to its end is held to the first reading (`reading._walked_unchanged`).

    The file is changed while the survey's first walk reads it and put
    back, its moment of change too, before the standard reader's check:
    only the walk's own digest shows it, and the file is refused as
    changed rather than as a difference between the readers. Red on the
    mutant that does not compare a finished walk's digest.
    """
    table = tmp_path / "t.csv"
    text = "a,b,c\n" + "".join(f"{k},{k * 2},x{k}\n" for k in range(60))
    table.write_text(text, encoding="utf-8", newline="\n")
    seen = table.stat()
    walks = reading._walks

    def changed_while_read(*arguments: object) -> object:
        first = True
        for lines in walks(*arguments):  # type: ignore[arg-type]
            if not first:
                yield lines
                continue
            first = False

            def reading_the_change(lines: object = lines) -> object:
                table.write_text(text.replace("x7\n", "x8\n"), encoding="utf-8", newline="\n")
                yield from lines  # type: ignore[misc]
                table.write_text(text, encoding="utf-8", newline="\n")
                os.utime(table, ns=(seen.st_atime_ns, seen.st_mtime_ns))

            yield reading_the_change()

    monkeypatch.setattr(reading, "_walks", changed_while_read)
    with pytest.raises(errors.ProfileError) as refused:
        reading.read_table(str(table), in_groups=True)
    assert f"{refused.value}" == errors.file_changed_while_read(str(table))
