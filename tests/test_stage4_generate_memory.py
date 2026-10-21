"""Lane SG's gate (plan P4-D415): generate holds the twin once.

THE FAULT. `generation.generate` held the whole twin as Python objects
both ways round -- a tuple of text objects a column and a tuple a row
holding the same objects -- then arranged its rows over a grid of every
column held as lists, then made the twin's whole text, a line at a time,
and handed it to the writer whole. Lane B0 projected the peak of
generate at 2,000,000 rows by 50 columns at 8,950 to 9,121 MB, the held
cells about 5.5 to 5.8 GB of it; and lane XW's night run of 2026-10-21
saw the workbook route killed by its 1.9 GB guard at 1,048,576 rows by
50 columns on the package's per-cell tuples.

THE CHANGE. Each finished column is held as its cells' own bytes
(`twinstore`); the rows are placed a column at a time
(`dialect.placed_column`, `dialect.arranged_columns`); the delimited
twin's text is made in pieces (`dialect.twin_pieces`) and written
through the file's handle a piece at a time; the workbook's cells,
classes and styles are held compactly too (`sheetwriting`). The
command builds the held twin (`generation.generate_held`); `generate`
keeps handing the cells back both ways round for whoever asks.

WHAT THIS FILE HOLDS IT TO.

1. EVERY BYTE AS BEFORE. The columns the generator makes are recorded
   where each is handed to `dialect.placed_column`, and arranged and
   written by 8a02faa3's own assembly, frozen as text in
   `tests/generate_memory_cases.py`; the command's twin must be those
   bytes, on seeded wide, sorted, sparse and differently encoded tables
   and on the health data zoo's delimited tables. The workbook route is
   held to lane XW's frozen writer on a held twin. The goldens, the
   generation reference vectors and lane XW's 31 workbooks have their
   own tests, unchanged.
2. A TRACED BOUND ON THE BYTES HELD A CELL: the held twin costs its
   text and at most a few bytes more a cell; a column held as text
   objects breaks it.
3. THE WHOLE TABLE IS NEVER TEXT OBJECTS AT ONCE: writing the twin holds
   one block of rows and one piece of text; a writer that makes the
   whole twin first breaks the bound, and so does a generator handing
   back the twin both ways round.
4. NO TEMPORARY FILE: a generate run opens for writing only its two
   outputs' working names and the outputs, in the folder it was told; a
   column spilled to a temporary file is caught.
"""

import gc
import io
import os
import pathlib
import tracemalloc
import typing

import pytest

import generate_memory_cases as cases
import health_zoo
import workbook_stream_cases as books
import workbooks
from synthtwin import (
    contract,
    dialect,
    generation,
    rendering,
    twinstore,
)

SEED = 7


def _loaded(description: pathlib.Path) -> contract.Profile:
    return contract.load_profile(str(description))


# -- 1. every byte as before -----------------------------------------------

_LATIN = (
    "name,town,score\n"
    + "".join(
        f"P{index:03d},{('Montréal', 'Zürich', 'Ålesund', 'Köln')[index % 4]},{index % 17}.5\n"
        for index in range(240)
    )
).encode("latin-1")

_UTF16 = (
    "﻿code\tlabel\tvalue\r\n"
    + "".join(
        f"C{index:03d}\t{('α', 'β', 'γ')[index % 3]}\t{(index * 7) % 101}\r\n"
        for index in range(240)
    )
).encode("utf-16-le")

_TABLES: "dict[str, tuple[str, typing.Callable[[], bytes], tuple[str, ...]]]" = {
    "wide": ("wide.csv", lambda: cases.wide_table(600), ()),
    "sorted": ("sorted.csv", lambda: cases.sorted_table(1500), ()),
    "sorted_floor_one": ("sorted.csv", lambda: cases.sorted_table(400), ("--smallest-group", "1")),
    "sparse": ("sparse.csv", lambda: cases.sparse_table(1200), ()),
    "sparse_floor_one": ("sparse.csv", lambda: cases.sparse_table(300), ("--smallest-group", "1")),
    "latin": ("latin.csv", lambda: _LATIN, ()),
    "utf16": ("utf16.csv", lambda: _UTF16, ()),
}


@pytest.mark.parametrize("case", sorted(_TABLES))
def test_the_command_writes_the_bytes_the_frozen_assembly_writes(
    tmp_path: pathlib.Path, case: str
) -> None:
    """The twin on disk is 8a02faa3's assembly of the same columns, byte for byte."""
    name, build, flags = _TABLES[case]
    description = cases.described(tmp_path, name, build(), flags)
    loaded = _loaded(description)
    before = cases.before_bytes(loaded, SEED)
    after = cases.after_bytes(description, SEED)
    assert after == before, case


def test_the_seeded_tables_reach_every_arrangement(tmp_path: pathlib.Path) -> None:
    """The cases above are not idle: a sort, empty records and records no column fills.

    The sorted table publishes its order and its empty records; the
    sparse one publishes empty records, and its twin has rows that no
    column fills once each column is placed, which `dialect.arranged_columns`
    gives a cell (`_given_cells`).
    """
    sorted_form = _loaded(
        cases.described(tmp_path / "s", "sorted.csv", cases.sorted_table(1500))
    ).source.dialect
    assert sorted_form.row_order.column == 1
    assert sorted_form.empty_rows_interior > 0
    sparse = _loaded(
        cases.described(tmp_path / "p", "sparse.csv", cases.sparse_table(1200))
    )
    form = sparse.source.dialect
    assert form.empty_rows_leading + form.empty_rows_interior + form.empty_rows_trailing > 0
    needy: "list[int]" = []
    shipped = dialect._given_cells

    def watched(
        state: dialect.Arranging, columns: "list[twinstore.HeldColumn]"
    ) -> "list[twinstore.HeldColumn]":
        nonlocal needy
        needy += [
            sum(
                1
                for row in range(state.n_rows)
                if not state.targets[row] and not state.filled[row]
            )
        ]
        return shipped(state, columns)

    dialect._given_cells = watched  # type: ignore[assignment]
    try:
        generation.generate_held(sparse, SEED)
    finally:
        dialect._given_cells = shipped  # type: ignore[assignment]
    assert needy and needy[0] > 0, needy


_ZOO_DELIMITED = [table for table in health_zoo.TABLES if table.suffix != ".xlsx"]


@pytest.mark.parametrize("table", _ZOO_DELIMITED, ids=[table.name for table in _ZOO_DELIMITED])
def test_the_zoo_keeps_every_byte(tmp_path: pathlib.Path, table: "health_zoo.Table") -> None:
    """Every delimited table of the health data zoo, described as it comes: the same bytes."""
    path = health_zoo.write_table(table, tmp_path, 150, 3)
    code = cases.run(["profile", str(path), "--out-dir", str(tmp_path), "--replace"])
    assert code == 0, table.name
    description = tmp_path / f"{path.stem}-profile.json"
    loaded = _loaded(description)
    assert cases.after_bytes(description, SEED) == cases.before_bytes(loaded, SEED)


def test_the_held_twin_is_the_materialised_twin(tmp_path: pathlib.Path) -> None:
    """`generate` is `generate_held` with the cells handed back both ways round."""
    loaded = _loaded(cases.described(tmp_path, "wide.csv", cases.wide_table(700, 20)))
    whole = generation.generate(loaded, SEED)
    held = generation.generate_held(loaded, SEED)
    assert whole.held_columns is None and held.held_columns is not None
    assert held.columns == () and held.rows == ()
    assert tuple(generation.twin_rows(held)) == whole.rows
    for index in range(len(whole.columns)):
        assert generation.twin_column(held, index) == whole.columns[index]
    assert held.outcomes == whole.outcomes
    assert rendering.twin_csv(held) == rendering.twin_csv(whole)
    assert rendering.report(loaded, held) == rendering.report(loaded, whole)


def test_a_held_workbook_twin_is_the_frozen_writers_file(tmp_path: pathlib.Path) -> None:
    """The workbook route on a held twin: lane XW's frozen writer's file, member by member."""
    for stem, data in (("wide", books.wide_book(700)), ("study", workbooks.study_book(400, 9, "excel"))):
        described = books.describe_book(tmp_path / stem, stem, data)
        whole = generation.generate(described, 0)
        held = generation.generate_held(described, 0)
        old = books.as_built_file(
            tmp_path / stem / "as-built.xlsx", books.as_built_members(described, whole)
        )
        new = books.streamed_file(tmp_path / stem / "held.xlsx", described, held)
        assert books.package_differences(old, new) == [], stem


# -- the store itself -------------------------------------------------------

_AWKWARD = [
    "",
    "plain",
    " spaced ",
    "comma, inside",
    "line\nbreak",
    "Montréal",
    "’curly’",
    "\ud800",
    "\udcff tail",
    "😀",
    "😀",
    "tab\there",
]


@pytest.mark.parametrize("count", [0, 1, 255, 256, 257, 600])
def test_a_held_column_gives_back_every_cell(count: int) -> None:
    """Round trip, block boundaries, empty cells, lone surrogates and wide characters."""
    cells = [_AWKWARD[(index * 5) % len(_AWKWARD)] + f"{index % 3 or ''}" for index in range(count)]
    held = twinstore.held_column(cells)
    assert held.count == count
    assert twinstore.column_cells(held) == cells
    joined: "list[str]" = []
    for block in range(twinstore.blocks_of(count)):
        joined += twinstore.column_block(held, block)
    assert joined == cells
    assert twinstore.column_block(held, twinstore.blocks_of(count)) == []
    assert held.cells == ()


def test_a_cell_holding_the_separator_keeps_its_column_as_text() -> None:
    """The one case the separator cannot serve: the column is held as its cells, unchanged."""
    cells = ["a", "b\x00c", ""] * 200
    held = twinstore.held_column(cells)
    assert held.blocks == () and held.cells == tuple(cells)
    assert twinstore.column_cells(held) == cells
    assert twinstore.column_block(held, 1) == cells[256:512]


# -- 2. a traced bound on the bytes held a cell -------------------------------

# A held cell costs its UTF-8 bytes, one separator byte, and the block's
# share of its bytes object and of the column's tuple (about a sixth of a
# byte); everything else `generate_held` hands back with the twin -- each
# column's outcome, its deviations and approximations, about eight
# kilobytes a column here -- grows with the columns and not the rows.
# Measured: 11.5 traced bytes a cell beside 7.5 of text at 2,000 rows by
# 30 columns, and 51.2 with every column held as its text objects.
_HELD_BEYOND_TEXT = 6.0


def _traced_held(loaded: contract.Profile) -> "tuple[int, generation.Twin]":
    """(the bytes `tracemalloc` sees held once `generate_held` returns, the twin).

    A full collection runs before the start and before the reading,
    because it empties Python's own free lists: a freed tuple or float
    kept for reuse is still counted as allocated where it was first
    made, about 0.6 MB of them after a run, whatever the twin's size.
    """
    gc.collect()
    tracemalloc.start()
    try:
        began = tracemalloc.get_traced_memory()[0]
        twin = generation.generate_held(loaded, SEED)
        gc.collect()
        held = tracemalloc.get_traced_memory()[0] - began
    finally:
        tracemalloc.stop()
    return held, twin


def _bound_case(folder: pathlib.Path) -> "tuple[contract.Profile, int, int]":
    """(the description, its twin's text bytes, its cells) of the bound's table."""
    loaded = _loaded(cases.described(folder, "wide.csv", cases.wide_table(2000, 30)))
    text = len(bytes(rendering.twin_csv(generation.generate(loaded, SEED)), "utf-8"))
    return loaded, text, loaded.n_rows * len(loaded.columns)


def test_the_held_twin_costs_its_text_and_a_few_bytes_a_cell(tmp_path: pathlib.Path) -> None:
    """At most `_HELD_BEYOND_TEXT` traced bytes a cell beyond the twin's own text."""
    loaded, text, cells = _bound_case(tmp_path)
    held, twin = _traced_held(loaded)
    assert twin.held_columns is not None
    assert held / cells <= text / cells + _HELD_BEYOND_TEXT, (held / cells, text / cells)


def test_a_column_held_as_text_objects_breaks_the_bound(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTANT: every column held as a tuple of its text objects, as before."""
    loaded, text, cells = _bound_case(tmp_path)
    monkeypatch.setattr(
        twinstore,
        "held_column",
        lambda found: twinstore.HeldColumn((), tuple(found), len(found)),
    )
    held, _twin = _traced_held(loaded)
    assert held / cells > text / cells + _HELD_BEYOND_TEXT, (held / cells, text / cells)


def test_a_generator_handing_back_the_twin_both_ways_breaks_the_bound(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTANT: the whole table materialised, the twin's cells handed back as before."""
    loaded, text, cells = _bound_case(tmp_path)
    shipped = generation.generate_held
    monkeypatch.setattr(
        generation,
        "generate_held",
        lambda profile, seed: generation.materialised(shipped(profile, seed)),
    )
    held, _twin = _traced_held(loaded)
    assert held / cells > text / cells + _HELD_BEYOND_TEXT, (held / cells, text / cells)


# -- 3. the whole table is never text objects at once -------------------------

# Writing holds one block of every column as text objects and one piece
# of text: under this many bytes a cell of one block, measured 127 at
# 6,000 rows by 12 columns (389 KB, a twin of 539 KB of text), the line
# endings' and the closings' lists of a word a row among them. The same
# twin's text made whole first held 1,085 KB, its rows made first more.
_WRITE_HELD_A_BLOCK_CELL = 200


def _traced_write(loaded: contract.Profile, folder: pathlib.Path) -> "tuple[int, int]":
    """(the most traced above the start of a streamed write, the bound)."""
    twin = generation.generate_held(loaded, SEED)
    width = generation.twin_width(twin)
    target = folder / "streamed.csv"
    tracemalloc.start()
    try:
        began = tracemalloc.get_traced_memory()[0]
        pieces = rendering.twin_csv_pieces(twin)
        with target.open("w", encoding="utf-8", newline="") as handle:
            for piece in pieces:
                handle.write(piece)
        peak = tracemalloc.get_traced_memory()[1] - began
    finally:
        tracemalloc.stop()
    return peak, width * twinstore.BLOCK_ROWS * _WRITE_HELD_A_BLOCK_CELL


def _write_case(folder: pathlib.Path) -> contract.Profile:
    return _loaded(cases.described(folder, "wide.csv", cases.wide_table(6000, 12)))


def test_writing_the_twin_holds_one_block_of_rows(tmp_path: pathlib.Path) -> None:
    """A streamed write holds a block of rows and a piece of text, never the twin."""
    peak, bound = _traced_write(_write_case(tmp_path), tmp_path)
    assert peak < bound, (peak, bound)


@pytest.mark.parametrize("mutant", ["rows_made_first", "text_made_whole"])
def test_a_writer_making_the_whole_twin_first_breaks_the_bound(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, mutant: str
) -> None:
    """MUTANTS: the rows made whole before the first line; the text made whole."""
    loaded = _write_case(tmp_path)
    if mutant == "rows_made_first":
        shipped_rows = generation.twin_rows

        def every_row(twin: generation.Twin) -> "typing.Iterator[tuple[str, ...]]":
            return iter(list(shipped_rows(twin)))

        monkeypatch.setattr(generation, "twin_rows", every_row)
    else:
        shipped_pieces = rendering.twin_csv_pieces
        monkeypatch.setattr(
            rendering,
            "twin_csv_pieces",
            lambda twin: iter(["".join(shipped_pieces(twin))]),
        )
    peak, bound = _traced_write(loaded, tmp_path)
    assert peak > bound, (mutant, peak, bound)


# -- 4. no temporary file -------------------------------------------------------

_WRITING_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC


def _written_paths(
    monkeypatch: pytest.MonkeyPatch, description: pathlib.Path, out: pathlib.Path
) -> "list[pathlib.Path]":
    """Every path a generate run opens for writing, by either door Python has."""
    opened: "list[pathlib.Path]" = []
    real_open = io.open
    real_os_open = os.open

    def watched_open(file: object, mode: str = "r", *args: object, **kwargs: object) -> object:
        if isinstance(file, (str, os.PathLike)) and any(flag in mode for flag in "wax+"):
            opened[len(opened):] = [pathlib.Path(os.fspath(file)).resolve()]
        return real_open(file, mode, *args, **kwargs)  # type: ignore[call-overload]

    def watched_os_open(path: object, flags: int, *args: object, **kwargs: object) -> int:
        if isinstance(path, (str, os.PathLike)) and flags & _WRITING_FLAGS:
            opened[len(opened):] = [pathlib.Path(os.fspath(path)).resolve()]
        return real_os_open(path, flags, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(io, "open", watched_open)
    monkeypatch.setattr(os, "open", watched_os_open)
    try:
        code = cases.run(
            ["generate", str(description), "--out-dir", str(out), "--seed", f"{SEED}", "--replace"]
        )
    finally:
        monkeypatch.undo()
    assert code == 0
    return opened


def test_a_generate_run_writes_only_its_two_files(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every write lands in the folder the run was told, on its two outputs' names."""
    description = cases.described(tmp_path / "in", "wide.csv", cases.wide_table(500, 10))
    out = tmp_path / "out"
    out.mkdir()
    opened = _written_paths(monkeypatch, description, out)
    assert opened
    folder = out.resolve()
    assert all(path.parent == folder for path in opened), opened
    left = sorted(path.name for path in out.iterdir())
    assert len(left) == 2 and any("-twin." in name for name in left), left


def test_a_column_spilled_to_a_temporary_file_is_caught(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTANT: each finished column written to a temporary file before it is held."""
    import tempfile

    shipped = twinstore.held_column

    def spilled(cells: "list[str]") -> twinstore.HeldColumn:
        with tempfile.TemporaryFile("w+", encoding="utf-8") as spill:
            spill.write("\n".join(cells))
        return shipped(cells)

    description = cases.described(tmp_path / "in", "wide.csv", cases.wide_table(500, 10))
    out = tmp_path / "out"
    out.mkdir()
    monkeypatch.setattr(twinstore, "held_column", spilled)
    opened = _written_paths(monkeypatch, description, out)
    folder = out.resolve()
    assert any(path.parent != folder for path in opened), opened
