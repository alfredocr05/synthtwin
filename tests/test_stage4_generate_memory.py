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
   and on the health data zoo's delimited tables; and on the seeded
   tables, the twin 8a02faa3 itself wrote, by its sha256, so a byte
   moved inside a column's own generation is seen too. The arrangement
   a column at a time is 8a02faa3's on random sparse columns. The
   workbook route is held to lane XW's frozen writer on a held twin. The
   goldens, the generation reference vectors and lane XW's 31 workbooks
   have their own tests, unchanged.
2. A TRACED BOUND ON THE BYTES HELD A CELL: the held twin costs its
   text and at most a few bytes more a cell; a column held as text
   objects breaks it.
3. THE WHOLE TABLE IS NEVER TEXT OBJECTS AT ONCE: writing the twin holds
   one block of rows and one piece of text; a writer that makes the
   whole twin first breaks the bound, and so does a generator handing
   back the twin both ways round; and the command itself writes its
   twin with every route that makes the twin whole refusing.
4. NO TEMPORARY FILE: a generate run opens for writing only its two
   outputs' working names and the outputs, in the folder it was told; a
   column spilled to a temporary file is caught.
"""

import builtins
import csv
import gc
import hashlib
import io
import os
import pathlib
import re
import tracemalloc
import typing

import random

import pytest

import generate_memory_cases as cases
import health_zoo
import workbook_stream_cases as books
import workbooks
from synthtwin import (
    contract,
    dialect,
    errors,
    generation,
    rendering,
    sheetwriting,
    twinstore,
    writing,
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
    "texts": ("texts.csv", lambda: cases.text_table(600), ()),
}


# THE TWINS 8a02faa3 WROTE, by their sha256 (repair 1, skeptic 1 item 3
# and the statistics skeptic's item 4). The frozen assembly above takes
# the columns TODAY's generator makes, so a byte moved inside a column's
# own generation -- what lane SG's parts 4, 5 and 7 hold differently --
# would leave it green; these digests would not. Each is the twin
# 8a02faa3's `synthtwin generate` wrote at seed 7 from the description
# 8a02faa3's `synthtwin profile` made of the table, measured on Python
# 3.11.15 (the CI floor) and 3.13 alike (`wave6/SG/repair1/`), and equal
# to this lane's. The text table is the one whose columns take their
# cells from the column's plan: a plan's cells reversed moves none of
# the other six. A later landing that moves one of these twins ON
# PURPOSE (a description or a generation method changed) re-measures
# its digest from its own base and says so, as for the goldens.
#
# `sorted` RE-MEASURED AT BATCH 4H'S MERGE OF THIS LANE (2026-10-23): lane
# G2T's merge 15b433b5 (plan P4-D405, the shared staircase, batch 4e) moved
# that twin on purpose -- 64378477, the merge before it, writes 8a02faa3's
# e8e29a49... -- so the batch's base af69aaef, before this lane, writes the
# digest below, and the merged tree writes the same. The other seven are
# 8a02faa3's and af69aaef's alike (`planning-notes/work-2026-10/wave3/
# merge-4h/gate-digests-base.txt`).
_BEFORE_SHA256 = {
    "latin": "c5a78f1a7c2980c4913bfe4e220cd321f70cb28d0305df1898b02ba4519bc09c",
    "sorted": "f88db8f7772084ce124ba6569786b8313e6a59a1aa88bb53944e098847b50592",
    "sorted_floor_one": "2b9a8ad0672a409a26b9eb4f4260c280348ae0b553f744d78ee050c8fda41b46",
    "sparse": "829f54e6618b56cd54b38be8f1fedc660a4fa6c4f55037969ee802aa622b7e3e",
    "sparse_floor_one": "d32dc86c471fa47d5a7d68a8118ae7c2871540f18b7adf2fbcd170f830725b27",
    "texts": "2ac127f20cb24c19a4c3b92b2ebe90049df4dffdf5a5e8a7743c19ba6f65064d",
    "utf16": "dd69f4534646ca603000e5a98d1b76834c78c7b6b45b3757b29cfb21c3d26fde",
    "wide": "edaee2c842fa47c880123a55c7b195416b4a7d63334cf1165be690dfc5f84097",
}


@pytest.mark.parametrize("case", sorted(_TABLES))
def test_the_command_writes_the_bytes_the_frozen_assembly_writes(
    tmp_path: pathlib.Path, case: str
) -> None:
    """The twin on disk is 8a02faa3's assembly of the same columns, and 8a02faa3's twin, byte for byte."""
    name, build, flags = _TABLES[case]
    description = cases.described(tmp_path, name, build(), flags)
    loaded = _loaded(description)
    before = cases.before_bytes(loaded, SEED)
    after = cases.after_bytes(description, SEED)
    assert after == before, case
    assert hashlib.sha256(after).hexdigest() == _BEFORE_SHA256[case], case


def test_every_seeded_table_has_its_digest() -> None:
    """No seeded table goes without 8a02faa3's digest, and none is pinned that is not run."""
    assert sorted(_BEFORE_SHA256) == sorted(_TABLES)


def _random_columns(draw: random.Random, width: int, n_rows: int) -> "list[tuple[str, ...]]":
    """Columns mostly empty, some cells a space: records no column fills, givers of one or two cells."""
    share = draw.choice((0.3, 0.6, 0.85, 0.95, 0.99))
    holes = ("", " ") if draw.random() < 0.3 else ("",)
    columns: "list[tuple[str, ...]]" = []
    for _place in range(width):
        cells: "list[str]" = []
        for _row in range(n_rows):
            if draw.random() < share:
                cells += [draw.choice(holes)]
            else:
                cells += [f"v{draw.randrange(0, 50)}"]
        columns += [tuple(cells)]
    return columns


@pytest.mark.parametrize("case", ["sorted", "sparse"])
def test_the_arrangement_a_column_at_a_time_is_the_frozen_arrangement(
    tmp_path: pathlib.Path, case: str
) -> None:
    """`dialect.arranged` against 8a02faa3's own, on random sparse columns (skeptic 1, item 4).

    The sorted form sorts and places empty records; the sparse form
    places them with no sort. Most columns here are almost all empty, so
    records no column fills arise in most trials and the cell each is
    given must come from a record two columns or more fill -- the rule
    (`filled[source] < 2` in `_given_cells`) the seeded tables above
    cannot see, since dropping it moved none of their bytes.
    """
    name, build, flags = _TABLES[case]
    loaded = _loaded(cases.described(tmp_path, name, build(), flags))
    form = loaded.source.dialect
    n_rows = loaded.n_rows
    width = len(loaded.columns)
    needy_trials = 0
    for trial in range(40):
        columns = _random_columns(random.Random(trial * 7919 + n_rows), width, n_rows)
        state = dialect.arranging(form, n_rows, width)
        for column in columns:
            dialect.placed_column(state, list(column))
        if state.placing and any(
            not state.targets[row] and not state.filled[row] for row in range(n_rows)
        ):
            needy_trials = needy_trials + 1
        made = dialect.arranged(columns, form, n_rows)
        frozen = cases.AS_BUILT["arranged"]([list(column) for column in columns], form, n_rows)
        assert [tuple(column) for column in made] == [tuple(column) for column in frozen], (
            case,
            trial,
        )
    assert needy_trials >= 10, needy_trials


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


# -- the workbook's shared strings written as a stream ----------------------
#
# Repair 1 (the statistics skeptic's item 1): a real twin writes a new
# text on every row of a column of record numbers, so its shared-string
# table grows with the rows; made as one text it was held from the
# package's making to the end of the write, with a copy as bytes while
# its size was counted. `_shared_strings_pieces` makes it a piece at a
# time, the pieces joined being `_shared_strings_part`'s text.

_SHARED_AWKWARD = [
    "",
    "plain",
    " leading",
    "trailing ",
    "a & b < c > d",
    'quote " and \' apostrophe',
    "line\nbreak",
    "Montréal",
    "😀",
]


@pytest.mark.parametrize("count", [0, 1, 255, 256, 257, 700])
def test_the_shared_strings_in_pieces_are_the_one_text(count: int) -> None:
    """The streamed table joined is `_shared_strings_part`'s text, at every piece boundary."""
    items = [_SHARED_AWKWARD[index % len(_SHARED_AWKWARD)] + f"{index}" for index in range(count)]
    pieces = list(sheetwriting._shared_strings_pieces(items))
    assert "".join(pieces) == sheetwriting._shared_strings_part(items)
    a_piece = sheetwriting._SHARED_STRINGS_A_PIECE
    assert len(pieces) == 2 + (count + a_piece - 1) // a_piece


def _distinct_book(folder: pathlib.Path, n_rows: int) -> "tuple[contract.Profile, generation.Twin]":
    """A held workbook twin of ``n_rows`` rows whose first column writes a new text on every row.

    Lane XW's seeded wide book at two columns -- record numbers with
    leading zeros, written as text, and a category -- described at 300
    rows, its twin repeated in turn with the round of the repetition
    after each record number, as `tools/measurements/kpi_generate_memory.py`
    makes its stand-in as distinct as a real twin.
    """
    described = books.describe_book(folder, "codes", books.wide_book(300, 2))
    small = generation.generate_held(described, 0)
    held: "list[twinstore.HeldColumn]" = []
    for index in range(generation.twin_width(small)):
        column = generation.twin_column(small, index)
        cells: "list[str]" = []
        for row in range(n_rows):
            cell = column[row % small.n_rows]
            if index == 0 and row >= small.n_rows:
                cell = cell + f"{row // small.n_rows}"
            cells += [cell]
        held += [twinstore.held_column(cells)]
    twin = generation.Twin(
        names=small.names,
        write_header=small.write_header,
        n_rows=n_rows,
        columns=(),
        rows=(),
        outcomes=(),
        deviations=(),
        approximations=(),
        remarks=(),
        words_drawn=0,
        seed=small.seed,
        held_columns=tuple(held),
    )
    return described, twin


def _traced_package_write(folder: pathlib.Path) -> "tuple[int, int]":
    """(the most `tracemalloc` saw held above the write's start, the shared-string table's bytes)."""
    described, twin = _distinct_book(folder, 60000)
    parts = sheetwriting.workbook_stream(described, twin)
    table = [size for name, size, _pieces in parts if name == "xl/sharedStrings.xml"]
    gc.collect()
    tracemalloc.start()
    try:
        began = tracemalloc.get_traced_memory()[0]
        writing.write_workbook_file(folder / "twin.xlsx", parts)
        peak = tracemalloc.get_traced_memory()[1] - began
    finally:
        tracemalloc.stop()
    return peak, table[0]


def test_the_shared_strings_are_written_a_piece_at_a_time(tmp_path: pathlib.Path) -> None:
    """Writing the package holds less than half the shared-string table, never all of it."""
    peak, table = _traced_package_write(tmp_path)
    assert table > 1_000_000, table
    assert peak < table // 2, (peak, table)


def test_a_shared_string_table_made_whole_breaks_the_bound(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTANT: the table made as one text, as before, and written whole."""
    monkeypatch.setattr(
        sheetwriting,
        "_shared_strings_pieces",
        lambda items: iter([sheetwriting._shared_strings_part(items)]),
    )
    peak, table = _traced_package_write(tmp_path)
    assert peak >= table // 2, (peak, table)


# BOTH TRAVERSALS, MEASURED FROM THEIR MAKING (repair 2: the verify's new
# item 2 and the Codex review's item 4). The bound above starts at the
# write, after the package is made, so pieces made at the package's
# making and held to the write -- the second traversal taken as a list --
# were never seen. Each traversal of the pieces is measured here from the
# call that makes it to its last piece, the size count's at the package's
# making and the write's (14.5 KB and 0.9 KB above their calls against a
# table of 1.53 MB, floor 3.11.15), and the package's member must be a
# stream the write makes as it takes it.


def _traversals(
    folder: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> "tuple[list[int], int]":
    """(the most each traversal of the shared-string pieces held, from its making to its
    last piece, in the order they ended; the table's bytes), tracing from before the package."""
    held: "list[int]" = []
    made = sheetwriting._shared_strings_pieces

    def traced(items: "list[str]") -> "typing.Iterator[str]":
        tracemalloc.reset_peak()
        began = tracemalloc.get_traced_memory()[0]
        pieces = made(items)

        def walked() -> "typing.Iterator[str]":
            for piece in pieces:
                yield piece
            held[len(held):] = [tracemalloc.get_traced_memory()[1] - began]

        return walked()

    monkeypatch.setattr(sheetwriting, "_shared_strings_pieces", traced)
    described, twin = _distinct_book(folder, 60000)
    gc.collect()
    tracemalloc.start()
    try:
        parts = sheetwriting.workbook_stream(described, twin)
        table = [size for name, size, _pieces in parts if name == "xl/sharedStrings.xml"]
        writing.write_workbook_file(folder / "twin.xlsx", parts)
    finally:
        tracemalloc.stop()
    return held, table[0]


def test_each_traversal_of_the_shared_strings_holds_a_piece(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The size count and the write each hold less than half the table, from their making on."""
    held, table = _traversals(tmp_path, monkeypatch)
    assert table > 1_000_000, table
    assert len(held) == 2, held
    assert max(held) < table // 2, (held, table)


@pytest.mark.parametrize("mutant", ["fragments_made_first", "table_made_whole"])
def test_shared_strings_made_before_they_are_taken_break_the_bound(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, mutant: str
) -> None:
    """MUTANTS: every piece made when the package is made and held to the write; the table as one text."""
    shipped = sheetwriting._shared_strings_pieces
    if mutant == "fragments_made_first":
        monkeypatch.setattr(sheetwriting, "_shared_strings_pieces", lambda items: list(shipped(items)))
    else:
        monkeypatch.setattr(
            sheetwriting,
            "_shared_strings_pieces",
            lambda items: iter([sheetwriting._shared_strings_part(items)]),
        )
    held, table = _traversals(tmp_path, monkeypatch)
    assert max(held) >= table // 2, (mutant, held, table)


@pytest.mark.parametrize("mutant", ["", "fragments_made_first", "table_made_whole"])
def test_the_shared_string_member_is_made_as_the_write_takes_it(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, mutant: str
) -> None:
    """The package's shared-string member is a stream, never a held sequence of pieces (and its MUTANTS)."""
    shipped = sheetwriting._shared_strings_pieces
    if mutant == "fragments_made_first":
        monkeypatch.setattr(sheetwriting, "_shared_strings_pieces", lambda items: list(shipped(items)))
    elif mutant:
        monkeypatch.setattr(
            sheetwriting,
            "_shared_strings_pieces",
            lambda items: (sheetwriting._shared_strings_part(items),),
        )
    described, twin = _distinct_book(tmp_path, 3000)
    parts = sheetwriting.workbook_stream(described, twin)
    member = [pieces for name, _size, pieces in parts if name == "xl/sharedStrings.xml"][0]
    assert (iter(member) is member) == (not mutant), (mutant, type(member))


def test_a_distinct_workbook_twin_is_the_frozen_writers_file(tmp_path: pathlib.Path) -> None:
    """The streamed table's package, with thousands of shared strings, is lane XW's frozen writer's file."""
    described, twin = _distinct_book(tmp_path, 3000)
    whole = generation.materialised(twin)
    old = books.as_built_file(tmp_path / "as-built.xlsx", books.as_built_members(described, whole))
    new = books.streamed_file(tmp_path / "held.xlsx", described, twin)
    assert books.package_differences(old, new) == []


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


def _separator_twin(folder: pathlib.Path) -> "tuple[contract.Profile, generation.Twin]":
    """A held twin one of whose columns holds U+0000, so it is held as its cells.

    The Codex review's case (repair 2, item 1): 100 rows, half of one
    column's labels `=1+1`, which a spreadsheet reads as a formula, half a
    label holding U+0000. No table synthtwin reads holds that character,
    so the label is described as `plainqtext` and its spelling changed in
    the description, which the loader accepts.
    """
    data = "id,label\n" + "".join(
        f"{index},{'=1+1' if index % 2 else 'plainqtext'}\n" for index in range(100)
    )
    written = cases.described(folder, "labels.csv", data.encode("utf-8"))
    edited = folder / "edited-profile.json"
    edited.write_text(
        written.read_text(encoding="utf-8").replace("plainqtext", "plain\\u0000text"),
        encoding="utf-8",
        newline="\n",
    )
    loaded = _loaded(edited)
    return loaded, generation.generate_held(loaded, SEED)


def test_a_column_held_as_its_cells_is_read_a_block_at_a_time(tmp_path: pathlib.Path) -> None:
    """Both ways a column is held give back its cells a block at a time, and the report is the
    materialised twin's: its 50 cells beginning as a formula does are found (repair 2, Codex item 1)."""
    loaded, held = _separator_twin(tmp_path)
    assert held.held_columns is not None
    assert [column.blocks == () for column in held.held_columns] == [False, True]
    whole = generation.materialised(held)
    for place in range(generation.twin_width(held)):
        joined: "list[str]" = []
        for block in generation.twin_column_blocks(held, place):
            joined += block
        assert joined == list(whole.columns[place])
    assert rendering._formula_hazard(held) == rendering._formula_hazard(whole)
    assert rendering._formula_hazard(held)[0] == 50
    assert rendering.report(loaded, held) == rendering.report(loaded, whole)


def test_blocks_counted_from_the_packed_blocks_miss_a_column_held_as_its_cells(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTANT: a held column's blocks counted from its packed blocks, as before; the report
    found no cell beginning as a formula does in a column held as its cells."""
    loaded, held = _separator_twin(tmp_path)
    whole = generation.materialised(held)

    def packed_only(twin: generation.Twin, index: int) -> "typing.Iterator[list[str]]":
        if twin.held_columns is not None:
            column = twin.held_columns[index]
            for block in range(len(column.blocks)):
                yield twinstore.column_block(column, block)
            return
        yield list(twin.columns[index])

    monkeypatch.setattr(generation, "twin_column_blocks", packed_only)
    assert rendering._formula_hazard(held) != rendering._formula_hazard(whole)
    assert rendering.report(loaded, held) != rendering.report(loaded, whole)


# -- 2. a traced bound on the bytes held a cell -------------------------------

# A held cell costs its share of its block's PACKED bytes (zlib; about a
# third of its UTF-8 bytes and its separator) and the block's share of its
# bytes object and of the column's tuple; everything else `generate_held`
# hands back with the twin -- each column's outcome, its deviations and
# approximations, about eight kilobytes a column here -- grows with the
# columns and not the rows. So the twin held costs LESS than its own text.
# Measured at 2,000 rows by 30 columns: 6.2 traced bytes a cell beside 7.6
# of text; 11.1 with the blocks held unpacked, and 51.2 with every column
# held as its text objects.
_HELD_BEYOND_TEXT = 0.0


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
    """The held twin costs no more traced bytes a cell than its own text (`_HELD_BEYOND_TEXT`)."""
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


def test_blocks_held_unpacked_break_the_bound(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTANT: each block held as its UTF-8 bytes, unpacked, as lane SG's first part held it."""
    loaded, text, cells = _bound_case(tmp_path)
    monkeypatch.setattr(twinstore.zlib, "compress", lambda raw, level: bytes(raw))
    monkeypatch.setattr(twinstore.zlib, "decompress", lambda held: bytes(held))
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
# endings' and the closings' lists of a word a row among them, and 92
# (284 KB) since repair 2 walks those as the lines ask. The same twin's
# text made whole first held 1,085 KB, its rows made first more.
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


# THE FORM'S SCHEDULES WALKED AS THE LINES ASK (repair 2, the Codex
# review's item 2). The text's blank places, its line endings and its
# records' closings were laid out a line or a record at a time before the
# first piece -- a double-spaced file a place object a record, 80.6 MB at
# 500,000 rows before 2.5 MB of text -- and a run of blank lines or of
# preamble never ended a piece. Now each is walked as the lines ask, and
# counted endings are held at a byte a line; every piece holds at most
# `dialect._LINES_A_PIECE` lines, whatever kind they are; and the text is
# 8a02faa3's, whose schedules `generate_memory_cases.SCHEDULES` keeps.

_LINE_BREAK = re.compile("\r\r\n|\r\n|\n|\r")


def _random_form(draw: random.Random, width: int, n_rows: int) -> dialect.Dialect:
    """A form with a random choice of every schedule the text writer walks."""
    changes: "dict[str, object]" = {}
    if draw.random() < 0.5:
        changes["line_endings"] = tuple(
            dialect.EndingRun(ending=draw.choice(dialect.ENDINGS), lines=draw.randint(0, 400))
            for _run in range(draw.randint(1, 4))
        )
    if draw.random() < 0.4:
        changes["line_endings_spread"] = tuple(
            dialect.EndingRun(ending=name, lines=draw.randint(1, 900))
            for name in dialect.ENDINGS
            if draw.random() < 0.6
        )
    if draw.random() < 0.4:
        after = 0
        places: "list[dialect.BlankPlace]" = []
        for _place in range(draw.randint(1, 5)):
            after = after + draw.randint(0, 50)
            places += [dialect.BlankPlace(after=after, lines=draw.randint(1, 600), text=draw.choice(["", " ", "\t "]))]
        changes["blank_lines"] = tuple(places)
    if draw.random() < 0.4:
        first = draw.randint(0, max(n_rows, 1))
        changes["blank_lines_spread"] = dialect.BlankSpread(
            first=first,
            last=draw.randint(first, max(n_rows, first)),
            lines=draw.randint(1, 2 * max(n_rows, 1) + 5),
            text=draw.choice(["", "  "]),
        )
    if draw.random() < 0.3:
        changes["preamble"] = tuple(
            dialect.PreambleRun(
                kind=draw.choice(dialect.PREAMBLE_KINDS),
                lines=draw.randint(1, 600),
                mark=draw.choice(["", "# ", " "]),
            )
            for _run in range(draw.randint(1, 3))
        )
    if draw.random() < 0.4:
        changes["rows_trailing_delimiter"] = True
        if draw.random() < 0.5:
            changes["rows_closing_runs"] = tuple(
                dialect.EndingRun(ending=draw.choice(dialect.CLOSINGS), lines=draw.randint(0, 300))
                for _run in range(draw.randint(1, 4))
            )
        else:
            changes["rows_closing_quoted"] = draw.random() < 0.5
    changes["byte_order_mark"] = draw.random() < 0.3
    changes["end_of_file_mark"] = draw.random() < 0.3
    changes["final_line_ending"] = draw.random() < 0.7
    changes["separator_line"] = draw.random() < 0.2
    return dialect.Dialect(**{**dialect.ordinary(width, n_rows, True).__dict__, **changes})


def test_the_pieces_on_every_schedule_are_the_frozen_text() -> None:
    """On 300 random forms the pieces joined are 8a02faa3's text, and no piece holds more
    than `dialect._LINES_A_PIECE` lines."""
    draw = random.Random(20261023)
    for trial in range(300):
        n_rows = draw.choice([0, 1, 2, 5, 40, 300, 700])
        width = draw.choice([1, 2, 3])
        form = _random_form(draw, width, n_rows)
        names = tuple(f"c{place}" for place in range(width))
        rows = tuple(
            tuple(draw.choice(["", "a", "1", 'q"x', "b,c"]) for _place in range(width))
            for _row in range(n_rows)
        )
        header = draw.random() < 0.8
        pieces = list(dialect.twin_pieces(names, iter(rows), header, form, n_rows))
        assert "".join(pieces) == cases.AS_BUILT["twin_text"](names, rows, header, form), trial
        assert all(len(_LINE_BREAK.findall(piece)) <= dialect._LINES_A_PIECE for piece in pieces), trial


_SCHEDULED_ROWS = 100_000


def _scheduled_form(counted_endings: bool) -> dialect.Dialect:
    """A double-spaced file whose records close by turns: one blank line after every record,
    endings by the run or counted, the first five records closed `""`."""
    n_rows = _SCHEDULED_ROWS
    lines = 2 * n_rows + 1
    changes: "dict[str, object]" = {
        "blank_lines_spread": dialect.BlankSpread(first=1, last=n_rows, lines=n_rows, text=""),
        "rows_trailing_delimiter": True,
        "rows_closing_runs": (
            dialect.EndingRun(dialect.CLOSING_QUOTED, 5),
            dialect.EndingRun(dialect.CLOSING_BARE, n_rows - 5),
        ),
        "line_endings": (dialect.EndingRun("crlf", lines),),
    }
    if counted_endings:
        changes["line_endings_spread"] = (
            dialect.EndingRun("lf", lines - 1000),
            dialect.EndingRun("crlf", 600),
            dialect.EndingRun("cr", 400),
        )
    return dialect.Dialect(**{**dialect.ordinary(2, n_rows, True).__dict__, **changes})


def _first_piece_held(form: dialect.Dialect) -> int:
    """The most `tracemalloc` saw held from the writer's call to its first piece."""
    rows = ((f"{row}", "x") for row in range(_SCHEDULED_ROWS))
    gc.collect()
    tracemalloc.start()
    try:
        began = tracemalloc.get_traced_memory()[0]
        pieces = dialect.twin_pieces(("a", "b"), rows, True, form, _SCHEDULED_ROWS)
        next(pieces)
        peak = tracemalloc.get_traced_memory()[1] - began
    finally:
        tracemalloc.stop()
    return peak


# Before the first piece, the writer holds a piece and its schedules'
# state: under 64 KB, measured 15.7 KB with the endings by the run, and
# 215.4 KB with counted endings, 200,001 of them a byte a line; with the
# places, the closings and the endings laid out a line or a record at a
# time first, as before, it held 16.8 MB here (repair 2, floor 3.11.15).
_FIRST_PIECE_HELD = 64_000


@pytest.mark.parametrize("counted_endings", [False, True])
def test_the_first_piece_of_a_double_spaced_text_holds_its_schedules_small(counted_endings: bool) -> None:
    """Up to the first piece, a piece and the schedules' state: a byte a line for counted endings, nothing a record."""
    form = _scheduled_form(counted_endings)
    allowed = _FIRST_PIECE_HELD + (2 * _SCHEDULED_ROWS + 1 if counted_endings else 0)
    peak = _first_piece_held(form)
    assert peak < allowed, (peak, allowed)


@pytest.mark.parametrize("mutant", ["places", "closings", "endings", "counted_endings"])
def test_schedules_laid_out_first_break_the_bound(
    monkeypatch: pytest.MonkeyPatch, mutant: str
) -> None:
    """MUTANTS: one schedule laid out a line or a record at a time before the first piece, as before."""
    frozen = cases.AS_BUILT
    if mutant == "places":
        monkeypatch.setattr(
            dialect,
            "_blank_places_in_turn",
            lambda form: iter(frozen["spread_places"](form.blank_lines_spread)),
        )
    elif mutant == "closings":
        monkeypatch.setattr(
            dialect, "_closings_walked", lambda form, n_rows: iter(frozen["closings_in_turn"](form, n_rows))
        )
    elif mutant == "endings":
        shipped = dialect._endings_in_turn
        monkeypatch.setattr(dialect, "_endings_in_turn", lambda form: iter(list(shipped(form))))
    else:
        monkeypatch.setattr(
            dialect,
            "_endings_in_turn",
            lambda form: iter(
                [dialect.ENDING_TEXT[word] for word in frozen["spread_endings"](form.line_endings_spread)]
            ),
        )
    counted = mutant == "counted_endings"
    allowed = _FIRST_PIECE_HELD + (2 * _SCHEDULED_ROWS + 1 if counted else 0)
    peak = _first_piece_held(_scheduled_form(counted))
    assert peak >= allowed, (mutant, peak, allowed)


@pytest.mark.parametrize("kind", ["blank", "preamble"])
def test_a_long_run_of_blank_or_preamble_lines_is_cut_into_pieces(kind: str) -> None:
    """100,000 blank lines in one place, or 100,000 lines of preamble: every piece holds at most
    `dialect._LINES_A_PIECE` lines, and the text is 8a02faa3's."""
    run = 100_000
    changes: "dict[str, object]" = {}
    if kind == "blank":
        changes["blank_lines"] = (dialect.BlankPlace(after=1, lines=run, text=" "),)
    else:
        changes["preamble"] = (dialect.PreambleRun(kind=dialect.PREAMBLE_COMMENT, lines=run, mark="# "),)
    form = dialect.Dialect(**{**dialect.ordinary(2, 3, True).__dict__, **changes})
    rows = (("1", "a"), ("2", "b"), ("3", "c"))
    pieces = list(dialect.twin_pieces(("x", "y"), iter(rows), True, form, 3))
    assert max(len(_LINE_BREAK.findall(piece)) for piece in pieces) <= dialect._LINES_A_PIECE
    assert "".join(pieces) == cases.AS_BUILT["twin_text"](("x", "y"), rows, True, form)


# THE COMMAND'S OWN ROUTE (repair 1, skeptic 1 item 2): every bound above
# calls `generate_held` or `twin_csv_pieces` itself, so a command that
# went back to the whole twin, or made the whole text, kept them green.
# K-S4-09 measures the command, so the command is held here: the three
# routes that make the twin whole refuse, and the command must still
# write its twin. BOTH OF ITS BRANCHES (repair 2, the verify's new item
# 1): a workbook source too, where the command hands the held twin to
# `sheetwriting.workbook_stream`; a command that handed it the whole
# twin there passed every bound, each of which calls the writer itself.


def _refused(*_arguments: object, **_keywords: object) -> typing.NoReturn:
    raise AssertionError("the command made the twin whole")


_COMMAND_SOURCES: "dict[str, tuple[str, typing.Callable[[], bytes]]]" = {
    "delimited": ("wide.csv", lambda: cases.wide_table(600, 12)),
    "workbook": ("wide.xlsx", lambda: books.wide_book(600, 12)),
}


def _command_route(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, source: str = "delimited"
) -> int:
    """The generate command's exit code with every whole-twin route refusing."""
    name, made = _COMMAND_SOURCES[source]
    description = cases.described(tmp_path / "in", name, made())
    out = tmp_path / "out"
    out.mkdir()
    monkeypatch.setattr(generation, "materialised", _refused)
    monkeypatch.setattr(rendering, "twin_csv", _refused)
    monkeypatch.setattr(dialect, "twin_text", _refused)
    try:
        code = cases.run(
            ["generate", str(description), "--out-dir", str(out), "--seed", f"{SEED}", "--replace"]
        )
    except AssertionError:
        return -1
    if code == 0:
        suffix = pathlib.Path(name).suffix
        assert any("-twin." in path.name and path.suffix == suffix for path in out.iterdir())
    return code


@pytest.mark.parametrize("source", sorted(_COMMAND_SOURCES))
def test_the_command_never_makes_the_twin_whole(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, source: str
) -> None:
    """`synthtwin generate` writes its twin with `materialised`, `twin_csv` and `twin_text` refusing."""
    assert _command_route(tmp_path, monkeypatch, source) == 0


@pytest.mark.parametrize(
    ("source", "mutant"),
    [
        ("delimited", "whole_twin_both_ways"),
        ("delimited", "text_made_whole"),
        ("workbook", "whole_twin_both_ways"),
        ("workbook", "workbook_given_the_whole_twin"),
    ],
)
def test_a_command_making_the_twin_whole_is_caught(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, source: str, mutant: str
) -> None:
    """MUTANTS: the command handed `generate`'s twin both ways round; its text made whole first;
    the workbook writer handed the whole twin."""
    if mutant == "whole_twin_both_ways":
        shipped = generation.generate_held
        monkeypatch.setattr(
            generation,
            "generate_held",
            lambda profile, seed: generation.materialised(shipped(profile, seed)),
        )
    elif mutant == "text_made_whole":
        monkeypatch.setattr(
            rendering, "twin_csv_pieces", lambda twin: iter([rendering.twin_csv(twin)])
        )
    else:
        shipped_stream = sheetwriting.workbook_stream
        monkeypatch.setattr(
            sheetwriting,
            "workbook_stream",
            lambda profile, twin: shipped_stream(profile, generation.materialised(twin)),
        )
    assert _command_route(tmp_path, monkeypatch, source) != 0


# -- 4. no temporary file -------------------------------------------------------

_WRITING_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC


def _written_paths(
    monkeypatch: pytest.MonkeyPatch, description: pathlib.Path, out: pathlib.Path
) -> "list[pathlib.Path]":
    """Every path a generate run opens for writing, by any of the doors Python has.

    `io.open` (which `pathlib` and `tempfile` reach), `os.open`, and the
    builtin `open`, a binding of its own that patching `io.open` leaves
    alone (repair 1, skeptic 1 item 5).
    """
    opened: "list[pathlib.Path]" = []
    real_open = io.open
    real_builtin_open = builtins.open
    real_os_open = os.open

    def watched_open(file: object, mode: str = "r", *args: object, **kwargs: object) -> object:
        if isinstance(file, (str, os.PathLike)) and any(flag in mode for flag in "wax+"):
            opened[len(opened):] = [pathlib.Path(os.fspath(file)).resolve()]
        return real_open(file, mode, *args, **kwargs)  # type: ignore[call-overload]

    def watched_builtin_open(
        file: object, mode: str = "r", *args: object, **kwargs: object
    ) -> object:
        if isinstance(file, (str, os.PathLike)) and any(flag in mode for flag in "wax+"):
            opened[len(opened):] = [pathlib.Path(os.fspath(file)).resolve()]
        return real_builtin_open(file, mode, *args, **kwargs)  # type: ignore[call-overload]

    def watched_os_open(path: object, flags: int, *args: object, **kwargs: object) -> int:
        if isinstance(path, (str, os.PathLike)) and flags & _WRITING_FLAGS:
            opened[len(opened):] = [pathlib.Path(os.fspath(path)).resolve()]
        return real_os_open(path, flags, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(io, "open", watched_open)
    monkeypatch.setattr(builtins, "open", watched_builtin_open)
    monkeypatch.setattr(os, "open", watched_os_open)
    try:
        code = cases.run(
            ["generate", str(description), "--out-dir", str(out), "--seed", f"{SEED}", "--replace"]
        )
    finally:
        monkeypatch.undo()
    assert code == 0
    return opened


def _only_its_outputs(opened: "list[pathlib.Path]", out: pathlib.Path) -> bool:
    """Whether every path opened for writing is one of the two outputs left in ``out``
    or one of their working names (`writing.PART_SUFFIX`, `writing.KEPT_SUFFIX`).

    By name, not by folder alone (repair 2, the Codex review's item 5): a
    column written to a file of its own inside the output folder and
    deleted before the run ends leaves the folder as it should be.
    """
    folder = out.resolve()
    left = sorted(path.name for path in folder.iterdir())
    if len(left) != 2 or not any("-twin." in name for name in left):
        return False
    working = "|".join(re.escape(suffix) for suffix in (writing.PART_SUFFIX, writing.KEPT_SUFFIX))
    named = re.compile(
        "(" + "|".join(re.escape(name) for name in left) + ")((" + working + ")-[0-9]+)?"
    )
    return all(path.parent == folder and named.fullmatch(path.name) for path in opened)


def test_a_generate_run_writes_only_its_two_files(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every write lands in the folder the run was told, on its two outputs' names and their working names."""
    description = cases.described(tmp_path / "in", "wide.csv", cases.wide_table(500, 10))
    out = tmp_path / "out"
    out.mkdir()
    opened = _written_paths(monkeypatch, description, out)
    assert opened
    assert _only_its_outputs(opened, out), opened


@pytest.mark.parametrize("door", ["tempfile", "builtin_open", "inside_the_output_folder"])
def test_a_column_spilled_to_a_temporary_file_is_caught(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, door: str
) -> None:
    """MUTANTS: each finished column written to a temporary file before it is held.

    By `tempfile`; by the builtin `open` on a path of the run's own
    choosing, which only the builtin's own patch sees (skeptic 1, item 5);
    and inside the output folder, the file deleted once the column is held
    (the Codex review's item 5).
    """
    import tempfile

    shipped = twinstore.held_column
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    out = tmp_path / "out"
    out.mkdir()

    def spilled(cells: "list[str]") -> twinstore.HeldColumn:
        if door == "tempfile":
            with tempfile.TemporaryFile("w+", encoding="utf-8") as spill:
                spill.write("\n".join(cells))
        elif door == "builtin_open":
            with open(elsewhere / "spill.txt", "a", encoding="utf-8", newline="\n") as spill:
                spill.write("\n".join(cells))
        else:
            with open(out / "scratch.tmp", "w", encoding="utf-8", newline="\n") as spill:
                spill.write("\n".join(cells))
            os.remove(out / "scratch.tmp")
        return shipped(cells)

    description = cases.described(tmp_path / "in", "wide.csv", cases.wide_table(500, 10))
    monkeypatch.setattr(twinstore, "held_column", spilled)
    opened = _written_paths(monkeypatch, description, out)
    assert opened
    assert not _only_its_outputs(opened, out), opened


# -- 5. a column's working set held compactly, every byte as before ----------
#
# Lane SG's later parts change how a column's working set is held, never
# what it computes: the weekday pass's gap indexes are bounded and built
# again when let go, step 8.3's answers and the distinct pass's merge
# options are held as whole numbers, a tally keyed by folded spellings
# keeps the cell itself where folding leaves it, and each column's plan
# is let go with its column. Each is held here to the reading it
# replaces, and the twin of lane B0's mixed table -- five stamp columns,
# four date columns, three clocks, record numbers, codes and free text --
# to the same bytes however few units the indexes may hold.


def _measurements_module(name: str) -> object:
    """A module of `tools/measurements`, imported from this checkout."""
    import importlib
    import sys

    folder = str(pathlib.Path(__file__).resolve().parents[1] / "tools" / "measurements")
    if folder not in sys.path:
        sys.path.insert(0, folder)
    return importlib.import_module(name)


def _mixed_twin(folder: pathlib.Path, rows: int) -> bytes:
    """The twin of the date and stamp columns of lane B0's mixed table at ``rows`` rows, generated by the command.

    ITS DATES ALONE (batch 4h's merge of this lane, 2026-10-23): whole, the
    mixed table's dates stand beside the candidates of its open identifier
    questions, so lane HX2's count in people and lane PS's grain (plans
    P4-D406 and P4-D417, merged after 8a02faa3) pool them at the year and
    the weekday pass builds no gap index at all, which left the cases below
    green on nothing. Its nine date and stamp columns alone, no candidate
    beside them, are described per rows as 8a02faa3 described the whole
    table's, and the pass builds its indexes again (140 on the merged tree,
    the bound held at 15 units; the never-let-go mutant holds 27).
    """
    reader_memory = typing.cast(typing.Any, _measurements_module("kpi_reader_memory"))
    folder.mkdir(parents=True, exist_ok=True)
    whole = list(csv.reader(io.StringIO("\n".join(reader_memory.table_lines(rows)) + "\n")))
    kept = [place for place, name in enumerate(whole[0]) if name.endswith(("_date", "_at"))]
    assert len(kept) == 9, whole[0]
    text = io.StringIO()
    writer = csv.writer(text, lineterminator="\n")
    for row in whole:
        writer.writerow([row[place] for place in kept])
    description = cases.described(folder, "mixed.csv", text.getvalue().encode("utf-8"))
    return cases.after_bytes(description, SEED)


def test_the_gap_indexes_bound_moves_no_byte(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The weekday pass's indexes let go after every gap -- and, at a bound of one unit, no gap
    indexed at all, every one walked -- build the same twin as never let go."""
    roomy = _mixed_twin(tmp_path / "roomy", 3000)
    monkeypatch.setattr(generation, "_WEEKDAY_INDEX_UNITS_HELD", 1)
    let_go = _mixed_twin(tmp_path / "tight", 3000)
    assert let_go == roomy


# The bound the cases below set: small enough that the mixed twin's gaps
# of more units are walked and that the indexes of the rest, kept, would
# hold more than it.
_INDEX_BOUND = 16


def _index_states(
    folder: pathlib.Path, monkeypatch: pytest.MonkeyPatch, bounded: bool
) -> "list[tuple[int, int]]":
    """(units held, indexes held) after every gap index the mixed twin builds, the bound at `_INDEX_BOUND` units."""
    states: "list[tuple[int, int]]" = []
    shipped = generation._weekday_indexes_bounded

    def watched(state: typing.Any) -> None:
        if bounded:
            shipped(state)
        held = state.indexed_units[0] if 0 in state.indexed_units else 0
        states[len(states):] = [(held, len(state.indexes))]

    monkeypatch.setattr(generation, "_weekday_indexes_bounded", watched)
    monkeypatch.setattr(generation, "_WEEKDAY_INDEX_UNITS_HELD", _INDEX_BOUND)
    _mixed_twin(folder, 3000)
    return states


def test_the_gap_indexes_hold_no_more_than_their_bound(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The indexes never hold more than `_WEEKDAY_INDEX_UNITS_HELD` units, not even the gap
    asked last: a gap of more units is walked, never indexed (repair 2, the Codex review's
    item 3: one index of 100,000 units was kept whatever the bound)."""
    states = _index_states(tmp_path, monkeypatch, True)
    assert states
    assert all(held <= _INDEX_BOUND for held, _count in states), max(states)


def test_indexes_never_let_go_break_the_bound(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTANT: every gap's index kept for the whole of steps 5 and 6, as before."""
    states = _index_states(tmp_path, monkeypatch, False)
    assert any(held > _INDEX_BOUND and count > 1 for held, count in states), max(states)


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_merge_options_held_as_numbers_sort_as_their_tuples(seed: int) -> None:
    """`_option_packed` keeps the five-part tuples' order and `_option_read` gives them back."""
    import random

    draw = random.Random(seed)
    moved = [draw.randrange(-10**9, 10**9) for _rank in range(200)]
    lows = [value - draw.randrange(0, 10**6) for value in moved]
    highs = [value + draw.randrange(0, 10**6) for value in moved]
    radix = generation._option_radix(moved, lows, highs)
    options: "list[tuple[int, int, int, int, int]]" = []
    for _each in range(2000):
        first = draw.randrange(0, len(moved))
        target = draw.randrange(min(lows), max(highs) + 1)
        options += [
            (
                abs(target - moved[first]),
                draw.randrange(1, len(moved) + 1),
                first,
                target,
                draw.randrange(-1, len(moved)),
            )
        ]
    packed = [generation._option_packed(radix, *option) for option in options]
    assert [generation._option_read(radix, number) for number in sorted(packed)] == sorted(options)


def test_a_merge_option_outside_its_bases_is_refused() -> None:
    """An instant outside every rank's and gap's reach would misorder: the internal check."""
    radix = generation._option_radix([10, 20], [5, 15], [12, 25])
    with pytest.raises(errors.ProfileError):
        generation._option_packed(radix, 0, 1, 0, 26, -1)
    with pytest.raises(errors.ProfileError):
        generation._option_packed(radix, 0, 3, 0, 10, -1)


def test_a_reach_code_reads_back_as_its_group_and_gain() -> None:
    """`_reach_code` and `_reach_of` over every group of the widest census and both gains."""
    for taking in range(64):
        for gained in (0, 1):
            assert generation._reach_of(generation._reach_code(taking, gained)) == (taking, gained)


@pytest.mark.parametrize(
    "cell", ["12", "abc", "ABC", " x ", "Straße", "ǅ", "\ud800", "", "ß"]
)
def test_a_folded_tally_keeps_the_cell_where_folding_leaves_it(cell: str) -> None:
    """`_folded_or_itself` is `parsing.folded`'s text, and the cell's own object where they are equal."""
    from synthtwin import parsing

    made = generation._folded_or_itself(cell)
    assert made == parsing.folded(cell)
    if parsing.folded(cell) == cell:
        assert made is cell


def test_a_recount_is_the_count_it_replaces() -> None:
    """`_recounted` against the list-and-two-sets count it replaced, holes and folds included."""
    from synthtwin import parsing

    cells = ["A1", "a1", "", "-999", "B2", "A1", " b2", "NA", "c3"] * 40
    holes = ("-999", "NA")
    present = [cell for cell in cells if cell != "" and cell not in holes]
    expected = (
        len(present),
        len(cells) - len(present),
        len(set(present)),
        len({parsing.folded(cell) for cell in present}),
    )
    assert generation._recounted(cells, holes) == expected


# -- 6. the one placement hook ---------------------------------------------


def test_the_placement_hook_is_asked_once_a_column_and_moves_nothing(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`_row_placement` is asked once a column, in column order, with a drawn arrangement, and hands it back."""
    description = cases.described(tmp_path, "wide.csv", cases.wide_table(400, 8))
    before = cases.after_bytes(description, SEED)
    asked: "list[tuple[int, int, int]]" = []
    shipped = generation._row_placement

    def watched(
        step: int,
        profile: contract.Profile,
        content: "list[str]",
        drawn: "list[int]",
        finished: "list[twinstore.HeldColumn]",
    ) -> "list[int]":
        assert sorted(drawn) == list(range(profile.n_rows))
        asked[len(asked):] = [(step, len(finished), len(content))]
        placed = shipped(step, profile, content, drawn, finished)
        assert placed is drawn
        return placed

    monkeypatch.setattr(generation, "_row_placement", watched)
    after = cases.after_bytes(description, SEED)
    assert after == before
    loaded = _loaded(description)
    assert [(step, done) for step, done, _size in asked] == [
        (step, step) for step in range(len(loaded.columns))
    ]
    assert all(size == loaded.n_rows for _step, _done, size in asked)


def test_an_arrangement_the_hook_hands_back_is_the_one_written(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTANT: a hook putting each column's cells in reverse moves the twin -- the hook is where rows are placed."""
    description = cases.described(tmp_path, "wide.csv", cases.wide_table(400, 8))
    before = cases.after_bytes(description, SEED)
    monkeypatch.setattr(
        generation,
        "_row_placement",
        lambda step, profile, content, drawn, finished: drawn[::-1],
    )
    assert cases.after_bytes(description, SEED) != before


# -- 6. the memory driver ------------------------------------------------------
#
# Repair 2, the Codex review's items 6 and 7: the driver started each run
# under `nice`, which native Windows has not, so it stopped before it
# measured anything; and its K-S4-09 record wrote `rows_traced`, which
# the describe driver writes for the same KPI, so the merged record
# carried generate's 50,000 under describe's name beside describe's own
# measurements.


def test_the_driver_runs_where_the_system_has_no_nice_and_no_ps(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With nothing on the PATH, a run is started as Python itself and records what it measured."""
    driver = typing.cast(typing.Any, _measurements_module("kpi_generate_memory"))
    empty = tmp_path / "bin"
    empty.mkdir()
    monkeypatch.setenv("PATH", str(empty))
    assert driver.launcher() == [driver.sys.executable]
    found = driver._child(["run", "-", str(tmp_path)])
    assert found["exit"] == 0 and "peak_rss_bytes" in found, found


def test_a_driver_starting_its_runs_under_nice_alone_fails_there(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTANT: every run started under `nice`, as before: no run starts at all."""
    driver = typing.cast(typing.Any, _measurements_module("kpi_generate_memory"))
    empty = tmp_path / "bin"
    empty.mkdir()
    monkeypatch.setenv("PATH", str(empty))
    monkeypatch.setattr(driver, "launcher", lambda: ["nice", "-n", "10", driver.sys.executable])
    with pytest.raises(OSError):
        driver._child(["run", "-", str(tmp_path)])


def test_generate_and_describe_merge_into_one_record_without_a_clash() -> None:
    """`kpi_run.py`'s merge keeps describe's `rows_traced` and generate's own count beside it."""
    driver = typing.cast(typing.Any, _measurements_module("kpi_generate_memory"))
    runner = typing.cast(typing.Any, _measurements_module("kpi_run"))
    describe = {"rows_traced": 200_000, "sizes": [100_000, 250_000, 500_000], "imports_mb": 78.1}
    generate = driver.memory_record([50_000, 100_000])
    merged = runner._merge([describe, generate])
    assert merged["rows_traced"] == 200_000
    assert merged["generate_rows_traced"] == driver.TRACED_ROWS == 50_000
    assert all("generate" in key for key in generate), sorted(generate)
    assert not set(generate) & set(describe)
