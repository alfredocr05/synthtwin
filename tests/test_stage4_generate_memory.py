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
import gc
import hashlib
import io
import os
import pathlib
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


# THE TWINS 8a02faa3 WROTE, by their sha256 (repair 1, skeptic 1 item 3
# and the statistics skeptic's item 4). The frozen assembly above takes
# the columns TODAY's generator makes, so a byte moved inside a column's
# own generation -- what lane SG's parts 4, 5 and 7 hold differently --
# would leave it green; these digests would not. Each is the twin
# 8a02faa3's `synthtwin generate` wrote at seed 7 from the description
# 8a02faa3's `synthtwin profile` made of the table, measured on Python
# 3.11.15 (the CI floor) and 3.13 alike (`wave6/SG/repair1/`), and equal
# to this lane's.
_BEFORE_SHA256 = {
    "latin": "c5a78f1a7c2980c4913bfe4e220cd321f70cb28d0305df1898b02ba4519bc09c",
    "sorted": "e8e29a4957738b708feb0460709b84a8ea8194bc54d5b144c9207cf1b34830cd",
    "sorted_floor_one": "2b9a8ad0672a409a26b9eb4f4260c280348ae0b553f744d78ee050c8fda41b46",
    "sparse": "829f54e6618b56cd54b38be8f1fedc660a4fa6c4f55037969ee802aa622b7e3e",
    "sparse_floor_one": "d32dc86c471fa47d5a7d68a8118ae7c2871540f18b7adf2fbcd170f830725b27",
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


# THE COMMAND'S OWN ROUTE (repair 1, skeptic 1 item 2): every bound above
# calls `generate_held` or `twin_csv_pieces` itself, so a command that
# went back to the whole twin, or made the whole text, kept them green.
# K-S4-09 measures the command, so the command is held here: the three
# routes that make the twin whole refuse, and the command must still
# write its twin.


def _refused(*_arguments: object, **_keywords: object) -> typing.NoReturn:
    raise AssertionError("the command made the twin whole")


def _command_route(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> int:
    """The generate command's exit code with every whole-twin route refusing."""
    description = cases.described(tmp_path / "in", "wide.csv", cases.wide_table(600, 12))
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
        assert any("-twin." in path.name for path in out.iterdir())
    return code


def test_the_command_never_makes_the_twin_whole(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`synthtwin generate` writes its twin with `materialised`, `twin_csv` and `twin_text` refusing."""
    assert _command_route(tmp_path, monkeypatch) == 0


@pytest.mark.parametrize("mutant", ["whole_twin_both_ways", "text_made_whole"])
def test_a_command_making_the_twin_whole_is_caught(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, mutant: str
) -> None:
    """MUTANTS: the command handed `generate`'s twin both ways round; its text made whole first."""
    if mutant == "whole_twin_both_ways":
        shipped = generation.generate_held
        monkeypatch.setattr(
            generation,
            "generate_held",
            lambda profile, seed: generation.materialised(shipped(profile, seed)),
        )
    else:
        monkeypatch.setattr(
            rendering, "twin_csv_pieces", lambda twin: iter([rendering.twin_csv(twin)])
        )
    assert _command_route(tmp_path, monkeypatch) != 0


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


@pytest.mark.parametrize("door", ["tempfile", "builtin_open"])
def test_a_column_spilled_to_a_temporary_file_is_caught(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, door: str
) -> None:
    """MUTANTS: each finished column written to a temporary file before it is held.

    By `tempfile`, and by the builtin `open` on a path of the run's own
    choosing, which only the builtin's own patch sees (skeptic 1, item 5).
    """
    import tempfile

    shipped = twinstore.held_column
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    def spilled(cells: "list[str]") -> twinstore.HeldColumn:
        if door == "tempfile":
            with tempfile.TemporaryFile("w+", encoding="utf-8") as spill:
                spill.write("\n".join(cells))
        else:
            with open(elsewhere / "spill.txt", "a", encoding="utf-8") as spill:
                spill.write("\n".join(cells))
        return shipped(cells)

    description = cases.described(tmp_path / "in", "wide.csv", cases.wide_table(500, 10))
    out = tmp_path / "out"
    out.mkdir()
    monkeypatch.setattr(twinstore, "held_column", spilled)
    opened = _written_paths(monkeypatch, description, out)
    folder = out.resolve()
    assert any(path.parent != folder for path in opened), opened


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
    """The twin of lane B0's mixed table at ``rows`` rows, generated by the command."""
    reader_memory = typing.cast(typing.Any, _measurements_module("kpi_reader_memory"))
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "mixed.csv"
    reader_memory.write_table(table, rows)
    description = cases.described(folder, "mixed.csv", table.read_bytes())
    return cases.after_bytes(description, SEED)


def test_the_gap_indexes_bound_moves_no_byte(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The weekday pass's indexes let go after every gap build the same twin as never let go."""
    roomy = _mixed_twin(tmp_path / "roomy", 3000)
    monkeypatch.setattr(generation, "_WEEKDAY_INDEX_UNITS_HELD", 1)
    let_go = _mixed_twin(tmp_path / "tight", 3000)
    assert let_go == roomy


def _index_states(
    folder: pathlib.Path, monkeypatch: pytest.MonkeyPatch, bounded: bool
) -> "list[tuple[int, int]]":
    """(units held, indexes held) after every gap index the mixed twin builds, the bound at 64 units."""
    states: "list[tuple[int, int]]" = []
    shipped = generation._weekday_indexes_bounded

    def watched(state: typing.Any) -> None:
        if bounded:
            shipped(state)
        held = state.indexed_units[0] if 0 in state.indexed_units else 0
        states[len(states):] = [(held, len(state.indexes))]

    monkeypatch.setattr(generation, "_weekday_indexes_bounded", watched)
    monkeypatch.setattr(generation, "_WEEKDAY_INDEX_UNITS_HELD", 64)
    _mixed_twin(folder, 3000)
    return states


def test_the_gap_indexes_hold_no_more_than_their_bound(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Past `_WEEKDAY_INDEX_UNITS_HELD` units only the gap asked last is kept."""
    states = _index_states(tmp_path, monkeypatch, True)
    assert states
    assert all(held <= 64 or count == 1 for held, count in states), max(states)


def test_indexes_never_let_go_break_the_bound(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTANT: every gap's index kept for the whole of steps 5 and 6, as before."""
    states = _index_states(tmp_path, monkeypatch, False)
    assert any(held > 64 and count > 1 for held, count in states), max(states)


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
