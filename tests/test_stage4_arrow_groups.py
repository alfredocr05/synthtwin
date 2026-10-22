"""Lane SR-A of the December plan: a group of columns read again by pyarrow's reader (plan P4-D414).

THE GATE. `synthtwin profile` reads a big table one group of columns at a
time (lane SR, plan P4-D400), and every group after the first is read
from the file again. The standard reader took 6.9 s to read one column of
2,000,000 rows of the made-up health table again; pyarrow's CSV reader,
parsing on one thread (its I/O read-ahead runs on pyarrow's own I/O
thread), the group's columns alone, 0.8 s (lib-study/LIB-scale.md).
It is never trusted to read as the survey reads: each walk folds every
column's values, as the survey, the standard reader and pandas agreed on
them, to a digest, and pyarrow's reading of a group is handed over only
where it read as many records and every column folds to the survey's
digest; otherwise the group is read again by the standard reader, and so
is every column of a form pyarrow is not asked of. Nothing of pyarrow's
is read while the walks are made.

WHAT THIS FILE PINS, against the reading of the whole table and against
the reading in groups by the standard reader alone:

1. Read whole, in groups by the standard reader, and in groups by
   pyarrow where it was held to the survey: the same Table, every field
   and every value, over shapes of every written form the reader knows
   and over seeded adversarial files, and the same refusals word for
   word. A form pyarrow reads otherwise is read again by the standard
   reader.
2. `synthtwin profile` writes the same files and says the same words all
   three ways.
3. What pyarrow is asked: nothing while the walks are made; then the
   group's columns alone (the include list), parsing on one thread
   (use_threads=False), every value as
   text; what is held afterwards: the group's columns as text and
   nothing of pyarrow's (its pool back where it was); a group whose
   values pyarrow would hold more of than `ARROW_GROUP_BYTES` (one note
   on every row, which the standard reader holds once) is not asked of
   it at all.
4. A file that changes between two readings is refused on pyarrow's
   route as on the standard reader's, however small the change and
   wherever it is -- a name, a column not asked, the quotes moved, the
   size and the moment kept -- and so is a file removed, renamed or
   closed to the person before a group is read again.
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

import pyarrow
import pyarrow.csv
import pytest

from synthtwin import errors, reading
from test_stage4_describe_groups import _ALPHABET, _SHAPES, _as_read, _profiled, _table_of_every_question


# Each pool a test hands pyarrow's reader, kept for the life of the
# process: a pool freed while a buffer it allocated lives crashes it.
_KEPT_POOLS: "list[object]" = []


def _no_arrow(
    facts: object, surveyed: object, headed: bool, columns: object, start: int, end: int,
) -> "list[reading._ArrowProof]":
    """The walk asking nothing of pyarrow: every group read again by the standard reader."""
    return [reading._NOT_PROVEN for _place in range(start, end)]


def _read(path: pathlib.Path, first_row: str, in_groups: bool) -> "tuple[str, object]":
    try:
        return "read", reading.read_table(str(path), first_row, in_groups=in_groups)
    except errors.ProfileError as refusal:
        return "refused", f"{refusal}"


def _three_readings(
    path: pathlib.Path, first_row: str, monkeypatch: pytest.MonkeyPatch
) -> "tuple[tuple[str, object], tuple[str, object], tuple[str, object], int]":
    """Whole; one column a group by the standard reader; one column a group by pyarrow where it reads as the survey. And how many columns pyarrow read again."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        whole = _read(path, first_row, False)
        monkeypatch.setattr(reading, "GROUP_BYTES", 1)
        monkeypatch.setattr(reading, "WALK_BYTES", 1)
        handed: "list[int]" = []
        route = reading._arrow_group

        def counted(source: reading.ColumnSource, places: "tuple[int, ...]") -> "list[list[str]] | None":
            found = route(source, places)
            if found is not None:
                handed.append(len(places))
            return found

        monkeypatch.setattr(reading, "_arrow_group", counted)
        arrow = _read(path, first_row, True)
        found_arrow = (arrow[0], _as_read(arrow[1]) if arrow[0] == "read" else arrow[1])  # type: ignore[arg-type]
        # The columns pyarrow's reading was handed over for, every column
        # read again once.
        proven = sum(handed)
        monkeypatch.setattr(reading, "_arrow_proof", _no_arrow)
        standard = _read(path, first_row, True)
        found_standard = (standard[0], _as_read(standard[1]) if standard[0] == "read" else standard[1])  # type: ignore[arg-type]
        monkeypatch.undo()
    found_whole = (whole[0], _as_read(whole[1]) if whole[0] == "read" else whole[1])  # type: ignore[arg-type]
    return found_whole, found_standard, found_arrow, proven


# -- 1. the reading -----------------------------------------------------


@pytest.mark.parametrize("shape", sorted(_SHAPES))
def test_a_table_reads_the_same_whole_in_groups_and_through_pyarrow(
    shape: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data, first_row = _SHAPES[shape]
    path = tmp_path / "shape.csv"
    path.write_bytes(data)
    whole, standard, arrow, _proven = _three_readings(path, first_row, monkeypatch)
    assert whole[0] == "read", whole
    assert whole == standard, shape
    assert whole == arrow, shape


def test_pyarrow_reads_again_the_plain_forms_and_leaves_the_others_to_the_standard_reader(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Which of the shapes pyarrow read again: the plain ones, and none it reads otherwise."""
    proven: "dict[str, int]" = {}
    for shape in sorted(_SHAPES):
        data, first_row = _SHAPES[shape]
        path = tmp_path / f"{len(proven)}.csv"
        path.write_bytes(data)
        proven[shape] = _three_readings(path, first_row, monkeypatch)[3]
    # Read by pyarrow again: line breaks inside quotes, carriage returns
    # alone, a title and a separator line above the names, UTF-16 behind
    # its mark and Windows-1252 and Latin-1 (decoded by Python's codecs),
    # a first row read as a record, and a file whose spaces after the
    # commas the survey reads as the values' own.
    for shape in (
        "quoted line breaks", "carriage returns alone", "a title and a separator line",
        "utf-16 behind its mark", "windows-1252", "latin-1", "a first row that is a record",
        "a first row said to be data", "comma-space",
    ):
        assert proven[shape] >= 1, (shape, proven)
    # Left to the standard reader: a closing delimiter and short rows, a
    # line of spaces between records, an end-of-file mark, a quoted empty
    # name over shorter rows.
    for shape in (
        "trailing delimiters and short rows", "a utf-8 mark and an end-of-file mark",
        "blank lines between records", "a quoted empty last name over shorter rows",
    ):
        assert proven[shape] == 0, (shape, proven)


def test_adversarial_files_read_or_refused_the_same_three_ways(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Seeded byte strings, the alphabet of lane SR's round 1, read whole, by the standard reader and by pyarrow."""
    draw = random.Random(20261021)
    outcomes = {"read": 0, "refused": 0}
    proven = 0
    path = tmp_path / "fuzz.csv"
    for _case in range(300):
        head = b"c0,c1,c2\n" if draw.random() < 0.6 else b""
        path.write_bytes(head + b"".join(draw.choice(_ALPHABET) for _ in range(draw.randrange(1, 50))))
        whole, standard, arrow, held = _three_readings(path, draw.choice(["auto", "auto", "names", "data"]), monkeypatch)
        assert whole == standard == arrow, path.read_bytes()
        outcomes[whole[0]] += 1
        proven += held
    assert outcomes["read"] >= 25 and outcomes["refused"] >= 25, outcomes
    # ...and pyarrow was held to some of them, so its route was taken.
    assert proven >= 3, proven


def test_an_empty_line_above_the_names_is_a_line_pyarrow_skips(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An empty line above the names is counted as pyarrow counts it, and handed over; skipped as the standard reader counts lines, pyarrow would read the names as a record (skeptic 1 of lane SR-A, item 1 (a))."""
    path = tmp_path / "lead.csv"
    path.write_text("\na,b\n" + "".join(f"{k},{k * 2}\n" for k in range(30)), encoding="utf-8", newline="\n")
    whole = reading.read_table(str(path))
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    monkeypatch.setattr(reading, "WALK_BYTES", 1)
    table = reading.read_table(str(path), in_groups=True)
    assert table.source is not None
    proofs = table.source.proofs
    assert all(proof.digest >= 0 for proof in proofs)
    assert proofs[0].skip == 2
    assert [reading.column_values(table, place) for place in (1, 0)] == [whole.columns[1], whole.columns[0]]
    # pyarrow read it as the survey did, so both columns stay its.
    assert all(proof.digest >= 0 for proof in table.source.proofs)
    # Skipping one line fewer, as the standard reader passes lines, pyarrow
    # reads the names as a record: what the record count refuses.
    found = reading._arrow_columns(
        str(path), str(path), 2, (0, 1), dataclasses.replace(proofs[0], skip=1)
    )
    assert found is not None
    assert found[0] == whole.n_rows + 1 and found[2][0][0] == "a"


def test_the_digest_holds_pyarrow_to_every_value_of_the_survey(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One value the survey read otherwise -- the last of the middle column -- and pyarrow's reading of that group is not handed over."""
    path = tmp_path / "t.csv"
    path.write_text("a,b,c\n" + "".join(f"{k},w{k % 4},{k * 3}\n" for k in range(50)), encoding="utf-8", newline="\n")
    whole = reading.read_table(str(path))
    real = reading._arrow_proof

    def doctored(
        facts: reading._Facts, surveyed: object, headed: bool,
        columns: "list[list[str]]", start: int, end: int,
    ) -> "list[reading._ArrowProof]":
        altered = [list(column) for column in columns]
        if start <= 1 < end:
            altered[1][len(altered[1]) - 1] = "another"
        return real(facts, surveyed, headed, altered, start, end)  # type: ignore[arg-type]

    monkeypatch.setattr(reading, "_arrow_proof", doctored)
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    monkeypatch.setattr(reading, "WALK_BYTES", 1)
    read = reading.read_table(str(path), in_groups=True)
    assert read.source is not None and all(proof.digest >= 0 for proof in read.source.proofs)
    taken: "list[tuple[tuple[int, ...], bool]]" = []
    route = reading._arrow_group

    def counted(source: reading.ColumnSource, places: "tuple[int, ...]") -> "list[list[str]] | None":
        found = route(source, places)
        taken.append((places, found is not None))
        return found

    monkeypatch.setattr(reading, "_arrow_group", counted)
    assert [reading.column_values(read, place) for place in range(3)] == whole.columns
    # The first group is held as the reading ends; the other two are read again.
    assert taken == [((1,), False), ((2,), True)], taken
    assert [proof.digest >= 0 for proof in read.source.proofs] == [True, False, True]


def test_a_reading_of_another_record_count_is_not_handed_over(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """pyarrow's reading counted one record more than the survey, its digests the survey's: read again by the standard reader."""
    path = tmp_path / "t.csv"
    path.write_text("a,b\n" + "".join(f"{k},w{k % 4}\n" for k in range(40)), encoding="utf-8", newline="\n")
    whole = reading.read_table(str(path))
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    monkeypatch.setattr(reading, "WALK_BYTES", 1)
    read = reading.read_table(str(path), in_groups=True)
    real = reading._arrow_columns

    def miscounted(*arguments: object) -> object:
        found = real(*arguments)  # type: ignore[arg-type]
        assert found is not None
        return found[0] + 1, found[1], [column[:1] for column in found[2]]

    monkeypatch.setattr(reading, "_arrow_columns", miscounted)
    assert reading.column_values(read, 1) == whole.columns[1]
    assert read.source is not None and read.source.proofs[1].digest == -1


def _clinic_rows(rows: int) -> "list[str]":
    """A six-column table's names and rows, as a report export writes them under its title."""
    return ["id,name,val,when,e,f"] + [
        f"{k},n{k % 7},{k * 1.5},2024-01-{k % 28 + 1:02d},e{k},f{k % 3}" for k in range(rows)
    ]


@pytest.mark.parametrize(
    "lead",
    ["Report of the clinic\nPrinted 2024-02-01\n\n", "Report of the clinic\r\n\r\n\r\n", "\nReport of the clinic\n\nPrinted 2024-02-01\n\n"],
)
def test_a_report_export_with_empty_lines_under_its_title_is_read_again_by_pyarrow(
    lead: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """pyarrow counts an empty line above the names as a line to skip: every column of a report export is read again by it (skeptic 1 of lane SR-A, item 1 (a))."""
    path = tmp_path / "report.csv"
    ending = "\r\n" if "\r\n" in lead else "\n"
    path.write_bytes((lead + ending.join(_clinic_rows(40)) + ending).encode("utf-8"))
    whole, standard, arrow, proven = _three_readings(path, reading.FIRST_ROW_AUTOMATIC, monkeypatch)
    assert whole[0] == "read", whole
    assert whole == standard == arrow
    # Six columns, one a group: the first is held as the reading ends,
    # the other five read again by pyarrow, every one handed over.
    assert proven == 5, proven


@pytest.mark.parametrize(
    "shape",
    ["an empty line at the end", "an empty line at the end, CRLF", "an empty line among the records"],
)
def test_an_empty_line_the_standard_reader_passes_is_one_pyarrow_passes(
    shape: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An empty line after or among the records, as an export often ends: every column read again is handed over (the verify of lane SR-A's repair 1, item 1: read as a record, every column would go back to the standard reader)."""
    ending = "\r\n" if "CRLF" in shape else "\n"
    lines = ["id,name,val,when"] + [f"{k},n{k % 7},{k * 3},2024-01-{k % 28 + 1:02d}" for k in range(40)]
    if shape == "an empty line among the records":
        lines = lines[:21] + [""] + lines[21:]
    path = tmp_path / "ending.csv"
    path.write_bytes((ending.join(lines) + ending + ("" if shape == "an empty line among the records" else ending)).encode("utf-8"))
    whole, standard, arrow, proven = _three_readings(path, reading.FIRST_ROW_AUTOMATIC, monkeypatch)
    assert whole[0] == "read", whole
    assert whole == standard == arrow
    # Four columns, one a group: the first is held as the reading ends,
    # the other three read again by pyarrow, every one handed over.
    assert proven == 3, (shape, proven)


@pytest.mark.parametrize("otherwise", ["a line break inside a quoted name", "another record count"])
def test_a_file_pyarrow_reads_otherwise_as_a_whole_is_asked_of_it_once(
    otherwise: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """pyarrow cannot read the file, or reads another record count: no other group of it is asked of pyarrow (skeptic 1 of lane SR-A, item 1 (b))."""
    path = tmp_path / "t.csv"
    if otherwise == "a line break inside a quoted name":
        path.write_bytes(("\n".join(['id,"long\nname",v,w'] + [f"{k},{k % 2},{k % 3},{k}" for k in range(40)]) + "\n").encode())
    else:
        path.write_bytes(("\n".join(_clinic_rows(40)) + "\n").encode())
        real = reading._arrow_columns

        def miscounted(*arguments: object) -> object:
            found = real(*arguments)  # type: ignore[arg-type]
            assert found is not None
            return found[0] + 1, found[1], found[2]

        monkeypatch.setattr(reading, "_arrow_columns", miscounted)
    whole = reading.read_table(str(path))
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    monkeypatch.setattr(reading, "WALK_BYTES", 1)
    read = reading.read_table(str(path), in_groups=True)
    assert read.source is not None and all(proof.digest >= 0 for proof in read.source.proofs)
    asked: "list[object]" = []
    real_read = pyarrow.csv.read_csv

    def watched(table: object, **settings: object) -> object:
        asked.append(table)
        return real_read(table, **settings)  # type: ignore[arg-type]

    monkeypatch.setattr(reading.pyarrow.csv, "read_csv", watched)
    width = len(whole.columns)
    assert [reading.column_values(read, place) for place in range(width)] == whole.columns
    assert len(asked) == 1, (otherwise, len(asked))
    assert all(proof.digest == -1 for proof in read.source.proofs)


# -- 2. synthtwin profile -------------------------------------------------


@pytest.mark.parametrize("options", [[], ["--identifier", "patient"], ["--smallest-group", "36", "--code", "ward"]])
def test_profile_writes_the_same_files_whole_in_groups_and_through_pyarrow(
    options: "list[str]", tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    table = tmp_path / "clinic.csv"
    table.write_text(_table_of_every_question(), encoding="utf-8", newline="\n")
    whole = _profiled(table, tmp_path / "whole", options)
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    monkeypatch.setattr(reading, "WALK_BYTES", 1)
    taken: "list[tuple[int, ...]]" = []
    route = reading._arrow_group

    def counted(source: reading.ColumnSource, places: "tuple[int, ...]") -> "list[list[str]]":
        taken.append(places)
        return route(source, places)

    monkeypatch.setattr(reading, "_arrow_group", counted)
    arrow = _profiled(table, tmp_path / "arrow", options)
    assert len(taken) >= 9, taken
    monkeypatch.setattr(reading, "_arrow_proof", _no_arrow)
    standard = _profiled(table, tmp_path / "standard", options)
    assert sorted(whole) == sorted(arrow) == sorted(standard)
    for name in whole:
        assert whole[name] == arrow[name], name
        assert whole[name] == standard[name], name


# -- 3. what pyarrow is asked, and what is held ----------------------------


def _wide(path: pathlib.Path, columns: int, rows: int) -> None:
    draw = random.Random(9)
    lines = [",".join(f"note{k}" for k in range(columns))]
    for row in range(rows):
        lines += [",".join(f"t{row}-{k}-{draw.randrange(10 ** 9)}" for k in range(columns))]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def test_pyarrow_is_asked_for_the_group_alone_on_one_thread(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The include list is the group's, the reader runs one thread, every value is text: mutants of each are red."""
    table = tmp_path / "wide.csv"
    _wide(table, 8, 400)
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    monkeypatch.setattr(reading, "WALK_BYTES", 1)
    read = reading.read_table(str(table), in_groups=True)
    asked: "list[tuple[object, object, object, int]]" = []
    real = pyarrow.csv.read_csv

    def watched(path: object, **settings: object) -> object:
        found = real(path, **settings)  # type: ignore[arg-type]
        convert = settings["convert_options"]
        asked.append(
            (
                tuple(convert.include_columns),  # type: ignore[attr-defined]
                settings["read_options"].use_threads,  # type: ignore[attr-defined]
                dict(convert.column_types),  # type: ignore[attr-defined]
                found.num_columns,
            )
        )
        return found

    monkeypatch.setattr(reading.pyarrow.csv, "read_csv", watched)
    for place in (5, 2, 7):
        values = reading.column_values(read, place)
        assert len(values) == 400 and values[0].startswith(f"t0-{place}-")
    assert len(asked) == 3, asked
    for (included, threads, types, width), place in zip(asked, (5, 2, 7)):
        assert included == (f"{reading._ARROW_NAMES}{place}",)
        assert width == 1
        assert threads is False
        assert set(types) == set(included) and all(f"{kind}" == "string" for kind in types.values())


def test_the_walks_ask_pyarrow_nothing_and_a_group_read_again_asks_for_the_group(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A walk of eight groups: no reading by pyarrow while the walks are made, then one reading of one column a group read again."""
    table = tmp_path / "wide.csv"
    _wide(table, 8, 400)
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    monkeypatch.setattr(reading, "WALK_BYTES", 1 << 40)
    asked: "list[tuple[object, ...]]" = []
    real = pyarrow.csv.read_csv

    def watched(path: object, **settings: object) -> object:
        asked.append(tuple(settings["convert_options"].include_columns))  # type: ignore[attr-defined]
        return real(path, **settings)  # type: ignore[arg-type]

    monkeypatch.setattr(reading.pyarrow.csv, "read_csv", watched)
    read = reading.read_table(str(table), in_groups=True)
    assert read.source is not None and len(read.source.walks) == 1
    assert len(read.source.groups) == 8
    assert asked == [], asked
    assert all(proof.digest >= 0 for proof in read.source.proofs)
    for place in (3, 0):
        reading.column_values(read, place)
    assert asked == [(f"{reading._ARROW_NAMES}3",), (f"{reading._ARROW_NAMES}0",)], asked


def test_a_group_read_through_pyarrow_holds_the_group_and_nothing_of_pyarrow(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One column a group of eight: the column's texts held, under a quarter of the whole reading; pyarrow's pool back where it was."""
    table = tmp_path / "wide.csv"
    _wide(table, 8, 2_000)
    tracemalloc.start()
    try:
        before = tracemalloc.get_traced_memory()[0]
        whole = reading.read_table(str(table), in_groups=True)
        held_whole = tracemalloc.get_traced_memory()[0] - before
        del whole
    finally:
        tracemalloc.stop()
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    monkeypatch.setattr(reading, "WALK_BYTES", 1)
    read = reading.read_table(str(table), in_groups=True)
    source = read.source
    assert source is not None and all(proof.digest >= 0 for proof in source.proofs)
    pool = pyarrow.default_memory_pool()
    allocated = pool.bytes_allocated()
    tracemalloc.start()
    try:
        before = tracemalloc.get_traced_memory()[0]
        reading.column_values(read, 6)
        held_group = tracemalloc.get_traced_memory()[0] - before
    finally:
        tracemalloc.stop()
    assert source.held_places == (6,) and len(source.held) == 1
    assert held_group < 0.25 * held_whole, (held_group, held_whole)
    # Nothing pyarrow allocated is still held once the group is handed over.
    assert pool.bytes_allocated() <= allocated, (pool.bytes_allocated(), allocated)


def test_a_group_pyarrow_would_hold_too_much_of_is_read_by_the_standard_reader(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One note of 4,096 characters on every row: the standard reader holds it once, pyarrow would hold every row's copy, so that group is not asked of pyarrow and nothing pyarrow allocates while reading the others comes near it (Codex's review of lane SR-A, item 2)."""
    rows = 3_000
    note = "".join(chr(ord("a") + k % 26) for k in range(4_096))
    table = tmp_path / "notes.csv"
    table.write_text(
        "id,note,ward\n" + "".join(f"{k},{note},w{k % 9}\n" for k in range(rows)),
        encoding="utf-8", newline="\n",
    )
    whole = reading.read_table(str(table))
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    monkeypatch.setattr(reading, "WALK_BYTES", 1)
    monkeypatch.setattr(reading, "ARROW_GROUP_BYTES", 1 << 20)
    read = reading.read_table(str(table), in_groups=True)
    assert read.source is not None and all(proof.digest >= 0 for proof in read.source.proofs)
    # What pyarrow would hold of the note: every row's 4,096 bytes and its offset.
    assert read.source.proofs[1].text_bytes == rows * (4_096 + 4)
    asked: "list[tuple[tuple[object, ...], int]]" = []
    real = pyarrow.csv.read_csv

    def watched(path: object, **settings: object) -> object:
        pool = pyarrow.proxy_memory_pool(pyarrow.default_memory_pool())
        _KEPT_POOLS.append(pool)
        found = real(path, memory_pool=pool, **settings)  # type: ignore[arg-type]
        asked.append((tuple(settings["convert_options"].include_columns), pool.max_memory()))  # type: ignore[attr-defined]
        return found

    monkeypatch.setattr(reading.pyarrow.csv, "read_csv", watched)
    assert [reading.column_values(read, place) for place in (2, 1, 0)] == [whole.columns[2], whole.columns[1], whole.columns[0]]
    assert [included for included, _most in asked] == [(f"{reading._ARROW_NAMES}2",), (f"{reading._ARROW_NAMES}0",)], asked
    # The note's copies alone are 12.3 MB; what pyarrow held at its most
    # reading the ward or the id is a small part of that.
    assert all(most < 4 << 20 for _included, most in asked), asked
    # The note is held once, as the standard reader holds a text met again.
    notes = reading.column_values(read, 1)
    assert len({id(value) for value in notes}) == 1


def test_what_pyarrow_holds_of_a_value_is_its_utf8_bytes_and_an_offset() -> None:
    """The bytes counted against `ARROW_GROUP_BYTES`, a value of any script: what pyarrow's string array holds of it."""
    for value in ["", "abc", "\u00e9t\u00e9", "\u65e5\u672c", "\U0001f600x", "a\u07ff\u0800\uffff\U00010000"]:
        assert reading._arrow_text_bytes(value) == len(value.encode("utf-8")) + 4, value


def test_a_text_met_again_is_held_once_through_pyarrow_as_through_the_standard_reader(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The texts of a column read again are shared in the same places either way (`reading._held_once`)."""
    table = tmp_path / "t.csv"
    table.write_text("a,b\n" + "".join(f"w{k % 5},z{k}\n" for k in range(400)), encoding="utf-8", newline="\n")
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    monkeypatch.setattr(reading, "WALK_BYTES", 1)
    shapes: "list[list[int]]" = []
    for route in ("arrow", "standard"):
        if route == "standard":
            monkeypatch.setattr(reading, "_arrow_proof", _no_arrow)
        read = reading.read_table(str(table), in_groups=True)
        reading.column_values(read, 1)
        values = reading.column_values(read, 0)
        # Each row's value as the first row holding that very object.
        first: "dict[int, int]" = {}
        shapes += [[first.setdefault(id(value), row) for row, value in enumerate(values)]]
    assert shapes[0] == shapes[1]
    # Five texts, each held once.
    assert sorted(set(shapes[0])) == [0, 1, 2, 3, 4]


# -- 4. a file that changes ----------------------------------------------


@pytest.mark.parametrize("change", ["a value", "two values swapped", "a row more", "the moment it changed"])
def test_a_file_that_changes_between_readings_is_refused_on_pyarrows_route(
    change: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    table = tmp_path / "t.csv"
    text = "a,b,c\n" + "".join(f"{k},{k * 2},x{k}\n" for k in range(60))
    table.write_text(text, encoding="utf-8", newline="\n")
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    read = reading.read_table(str(table), in_groups=True)
    assert read.source is not None and all(proof.digest >= 0 for proof in read.source.proofs)
    taken: "list[tuple[int, ...]]" = []
    route = reading._arrow_group

    def counted(source: reading.ColumnSource, places: "tuple[int, ...]") -> "list[list[str]]":
        taken.append(places)
        return route(source, places)

    monkeypatch.setattr(reading, "_arrow_group", counted)
    assert reading.column_values(read, 1)[5] == "10"
    seen = table.stat()
    if change == "a value":
        table.write_text(text.replace("x7\n", "x8\n"), encoding="utf-8", newline="\n")
        os.utime(table, ns=(seen.st_atime_ns, seen.st_mtime_ns))
    elif change == "two values swapped":
        table.write_text(text.replace("x7\n", "x@\n").replace("x8\n", "x7\n").replace("x@\n", "x8\n"), encoding="utf-8", newline="\n")
        os.utime(table, ns=(seen.st_atime_ns, seen.st_mtime_ns))
    elif change == "a row more":
        table.write_text(text + "61,122,x61\n", encoding="utf-8", newline="\n")
    else:
        os.utime(table, ns=(seen.st_atime_ns, seen.st_mtime_ns + 1_000_000_000))
    with pytest.raises(errors.ProfileError) as refused:
        reading.column_values(read, 2)
    assert f"{refused.value}" == errors.file_changed_while_read(str(table))
    assert (2,) in taken or change in ("the moment it changed", "a row more")


@pytest.mark.parametrize("change", ["the moment it changed", "a byte more"])
def test_a_file_whose_size_or_moment_moved_is_refused_before_pyarrow_reads_it(
    change: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The size and the moment are asked before pyarrow opens the file: a file that moved is refused unread by it."""
    table = tmp_path / "t.csv"
    table.write_text("a,b,c\n" + "".join(f"{k},{k * 2},x{k}\n" for k in range(60)), encoding="utf-8", newline="\n")
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    read = reading.read_table(str(table), in_groups=True)
    asked: "list[object]" = []
    real = pyarrow.csv.read_csv

    def watched(path: object, **settings: object) -> object:
        asked.append(path)
        return real(path, **settings)  # type: ignore[arg-type]

    monkeypatch.setattr(reading.pyarrow.csv, "read_csv", watched)
    assert reading.column_values(read, 1)[5] == "10"
    assert len(asked) == 1
    seen = table.stat()
    if change == "a byte more":
        with table.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write("\n")
        os.utime(table, ns=(seen.st_atime_ns, seen.st_mtime_ns))
    else:
        os.utime(table, ns=(seen.st_atime_ns, seen.st_mtime_ns + 1_000_000_000))
    with pytest.raises(errors.ProfileError) as refused:
        reading.column_values(read, 2)
    assert f"{refused.value}" == errors.file_changed_while_read(str(table))
    assert len(asked) == 1, asked


@pytest.mark.parametrize("change", ["a name", "a value of a column not asked", "the quotes moved"])
def test_a_change_outside_the_group_is_refused_on_pyarrows_route(
    change: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The size and the moment kept, the group's own values unchanged: pyarrow reads the survey's values, and the whole file read a line at a time is not the one first read (Codex's review of lane SR-A, item 1)."""
    table = tmp_path / "t.csv"
    text = "age,b,c\n" + "".join(
        (f'"{k}",{k * 2},x{k}\n' if k == 7 else f"{k},{k * 2},x{k}\n") for k in range(60)
    )
    table.write_text(text, encoding="utf-8", newline="\n")
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    read = reading.read_table(str(table), in_groups=True)
    assert read.source is not None and all(proof.digest >= 0 for proof in read.source.proofs)
    handed: "list[bool]" = []
    real = reading._arrow_columns

    def compared(*arguments: object) -> object:
        found = real(*arguments)  # type: ignore[arg-type]
        assert found is not None and read.source is not None
        handed.append(found[1] == [read.source.proofs[place].digest for place in arguments[3]])  # type: ignore[attr-defined]
        return found

    monkeypatch.setattr(reading, "_arrow_columns", compared)
    assert reading.column_values(read, 1)[5] == "10"
    seen = table.stat()
    if change == "a name":
        changed = text.replace("age,b,c\n", "bed,b,c\n")
    elif change == "a value of a column not asked":
        changed = text.replace("\n9,18,x9\n", "\n8,18,x9\n")
    else:
        changed = text.replace('"7",14,x7\n', '7,"14",x7\n')
    assert changed != text and len(changed) == len(text)
    table.write_text(changed, encoding="utf-8", newline="\n")
    os.utime(table, ns=(seen.st_atime_ns, seen.st_mtime_ns))
    assert table.stat().st_size == seen.st_size
    with pytest.raises(errors.ProfileError) as refused:
        reading.column_values(read, 2)
    assert f"{refused.value}" == errors.file_changed_while_read(str(table))
    # pyarrow read column c as the survey did: the line walk refused it.
    assert handed == [True, True], handed


@pytest.mark.parametrize("gone", ["removed", "renamed", "no longer open to this person"])
def test_a_file_gone_before_a_group_is_read_again_is_refused_on_pyarrows_route(
    gone: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The file removed, renamed or closed to this person after the reading: the changed-file refusal, never a traceback (Codex's review of lane SR-A, item 3)."""
    if gone == "no longer open to this person" and (os.name == "nt" or os.geteuid() == 0):
        pytest.skip("a folder's permissions close nothing on Windows or to the superuser")
    folder = tmp_path / "in"
    folder.mkdir()
    table = folder / "t.csv"
    table.write_text("a,b,c\n" + "".join(f"{k},{k * 2},x{k}\n" for k in range(60)), encoding="utf-8", newline="\n")
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    read = reading.read_table(str(table), in_groups=True)
    assert read.source is not None and all(proof.digest >= 0 for proof in read.source.proofs)
    taken: "list[tuple[int, ...]]" = []
    route = reading._arrow_group

    def counted(source: reading.ColumnSource, places: "tuple[int, ...]") -> "list[list[str]] | None":
        taken.append(places)
        return route(source, places)

    monkeypatch.setattr(reading, "_arrow_group", counted)
    assert reading.column_values(read, 1)[5] == "10"
    if gone == "removed":
        table.unlink()
    elif gone == "renamed":
        table.rename(folder / "moved.csv")
    else:
        folder.chmod(0)
    try:
        with pytest.raises(errors.ProfileError) as refused:
            reading.column_values(read, 2)
    finally:
        folder.chmod(0o755)
    assert f"{refused.value}" == errors.file_changed_while_read(str(table))
    assert taken == [(1,), (2,)], taken


def test_the_whole_route_is_unchanged_where_the_file_fits_one_group(tmp_path: pathlib.Path) -> None:
    """A table that fits one group is read whole and never asks pyarrow."""
    table = tmp_path / "t.csv"
    table.write_text("a,b\n" + "".join(f"{k},{k}\n" for k in range(40)), encoding="utf-8", newline="\n")
    read = reading.read_table(str(table), in_groups=True)
    assert read.source is None


def test_the_profile_says_nothing_new(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Read through pyarrow, the run prints the same words (no warning of pyarrow's reaches the screen)."""
    table = tmp_path / "clinic.csv"
    table.write_text(_table_of_every_question(), encoding="utf-8", newline="\n")
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    said = io.StringIO()
    out = tmp_path / "out"
    out.mkdir()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        from synthtwin import cli

        code = cli.main(["profile", str(table), "--out-dir", str(out), "--replace"])
    assert code == 0
    assert "pyarrow" not in said.getvalue().lower()
