"""Lane SR-A of the December plan: a group of columns read again by pyarrow's reader (plan P4-D414).

THE GATE. `synthtwin profile` reads a big table one group of columns at a
time (lane SR, plan P4-D400), and every group after the first is read
from the file again. The standard reader took 6.9 s to read one column of
2,000,000 rows of the made-up health table again; pyarrow's CSV reader,
one thread, the group's columns alone, 0.8 s (lib-study/LIB-scale.md).
It is never trusted to read as the survey reads: each walk asks it for
the walk's columns and holds what it read to the survey's values, value
by value, and only a column it read exactly so is read by it again, under
the settings it was held under, its values folded to the digest the walk
took of them; every other column is read again by the standard reader.

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
3. What pyarrow is asked: the group's columns alone (the include list),
   one thread, every value as text; what is held afterwards: the group's
   columns as text and nothing of pyarrow's (its pool back where it was).
4. A file that changes between two readings is refused on pyarrow's
   route as on the standard reader's, however small the change.
"""

from __future__ import annotations

import contextlib
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


def _no_arrow(
    raw_path: str, shown: str, facts: object, surveyed: object, headed: bool,
    columns: object, start: int, end: int,
) -> "list[reading._ArrowProof]":
    """The walk's proof made to prove nothing: every group read again by the standard reader."""
    return [reading._NOT_PROVEN for _place in range(start, end)]


def _read(path: pathlib.Path, first_row: str, in_groups: bool) -> "tuple[str, object]":
    try:
        return "read", reading.read_table(str(path), first_row, in_groups=in_groups)
    except errors.ProfileError as refusal:
        return "refused", f"{refusal}"


def _three_readings(
    path: pathlib.Path, first_row: str, monkeypatch: pytest.MonkeyPatch
) -> "tuple[tuple[str, object], tuple[str, object], tuple[str, object], int]":
    """Whole; one column a group by the standard reader; one column a group by pyarrow where proven. And how many columns pyarrow proved."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        whole = _read(path, first_row, False)
        monkeypatch.setattr(reading, "GROUP_BYTES", 1)
        monkeypatch.setattr(reading, "WALK_BYTES", 1)
        arrow = _read(path, first_row, True)
        proven = 0
        if arrow[0] == "read":
            table = arrow[1]
            assert isinstance(table, reading.Table)
            if table.source is not None:
                proven = sum(1 for proof in table.source.proofs if proof.digest >= 0)
        found_arrow = (arrow[0], _as_read(arrow[1]) if arrow[0] == "read" else arrow[1])  # type: ignore[arg-type]
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
    """Which of the shapes pyarrow was held to: the plain ones, and none it reads otherwise."""
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
        assert proven[shape] >= 2, (shape, proven)
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


def test_a_proof_that_held_nothing_would_hand_over_other_values(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant of the proof: pyarrow trusted without being held to the survey reads a blank line above the names as a record."""
    path = tmp_path / "lead.csv"
    path.write_text("\na,b\n" + "".join(f"{k},{k * 2}\n" for k in range(30)), encoding="utf-8", newline="\n")
    whole = reading.read_table(str(path))
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    monkeypatch.setattr(reading, "WALK_BYTES", 1)
    table = reading.read_table(str(path), in_groups=True)
    assert table.source is not None
    assert [proof.digest for proof in table.source.proofs] == [-1, -1]
    assert [reading.column_values(table, place) for place in range(2)] == whole.columns
    # Trusted unheld, under the settings the survey's form gives:
    trusted = reading._ArrowProof(digest=0, skip=1, delimiter=",", backslash=False, codec="utf-8")
    found = reading._arrow_columns(str(path), str(path), 2, (0, 1), trusted, None)
    assert found is not None
    assert found[0] != whole.n_rows or found[2] != whole.columns


def test_the_proof_holds_pyarrow_to_every_value_of_the_survey(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One value the survey read otherwise -- the last of a column -- and no column of the walk is proven."""
    path = tmp_path / "t.csv"
    path.write_text("a,b,c\n" + "".join(f"{k},w{k % 4},{k * 3}\n" for k in range(50)), encoding="utf-8", newline="\n")
    asked: "list[list[reading._ArrowProof]]" = []
    real = reading._arrow_proof

    def doctored(
        raw_path: str, shown: str, facts: reading._Facts, surveyed: object, headed: bool,
        columns: "list[list[str]]", start: int, end: int,
    ) -> "list[reading._ArrowProof]":
        honest = real(raw_path, shown, facts, surveyed, headed, columns, start, end)  # type: ignore[arg-type]
        altered = [list(column) for column in columns]
        altered[start][len(altered[start]) - 1] = "another"
        asked.append(real(raw_path, shown, facts, surveyed, headed, altered, start, end))  # type: ignore[arg-type]
        return honest

    monkeypatch.setattr(reading, "_arrow_proof", doctored)
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    monkeypatch.setattr(reading, "WALK_BYTES", 1)
    read = reading.read_table(str(path), in_groups=True)
    assert read.source is not None and all(proof.digest >= 0 for proof in read.source.proofs)
    assert len(asked) == 3
    for proofs in asked:
        assert [proof.digest for proof in proofs] == [-1]


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
