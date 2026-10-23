"""Plan P4-D411's gate: the workbook twin is written as a stream, byte for byte.

THE DEFECT. The workbook writer of b075342a grew the sheet as ONE text,
`text = text + f'<row r="{number}">' + line + "</row>"`, which copies the
whole sheet for every row, and handed the zip writer every part whole
(`writestr`). The library study measured it killed by its 1.9 GB guard at
19,999 rows of fifty columns after 44 s, and at 100,000 rows after 51 s
(lib-study/formats-probes/out-write.log); it is not run here at those sizes.

THE FIX. `sheetwriting._sheet_pieces` makes the same elements in the same
order and hands them on a row at a time; `sheetwriting.workbook_stream`
makes the sheet twice, the first pass giving every text its shared-string
place and counting the sheet's bytes, the second made as the zip writer
takes it; `writing.write_workbook_file` tells each member its size before
its first piece, so zipfile chooses the header `writestr` chose.

WHAT IS PINNED.

* The bytes: every workbook golden of method G2.2, the workbook battery,
  lane E0a's zoo workbook and a seeded wide table, each written by the
  frozen b075342a writer (`tests/workbook_stream_cases.py`) and by today's,
  are the same bytes (K-S4-22) on madler's zlib; on zlib-ng (CPython 3.14
  on Windows), whose deflate stream may move with where its input was
  cut, the same package member by member -- every header field but the
  compressed size and the offsets the zip64 field carries, every text --
  with only those free (skeptic 1, item 3; skeptic 2 and Codex). The
  member-by-member check is red on a moved date, attribute, method, text
  or order, and a package deflated at another level stands in for
  zlib-ng's other stream.
* zip64 exactly where `writestr` used it: with zipfile's line (its
  ZIP64_LIMIT, 2**31 - 1 bytes, over 1.05) lowered, a sheet past it gets the zip64 header from both writers,
  the same bytes again, and a writer that does not tell the member its
  size goes red.
* The memory: a sheet of 100,000 rows of fifty columns is written with
  `tracemalloc`, each pass traced from before its first piece, seeing
  at most a hundredth of the sheet's bytes held at once above what was
  held when it started; the writer of b075342a held the whole sheet's
  text, and its copies, before the zip writer saw a byte. A pass that
  lists its pieces on the call or on its first piece, or joins them,
  breaks the bound (Codex's item 1).
* The real route: `workbook_stream` makes the sheet once and hands the
  second pass on as an iterator nothing has drawn, and
  `write_workbook_file` draws all of it (skeptic 1, item 2).
* Mutants, each red: a row copied twice, two rows swapped, the member
  not told its size (never zip64), the sheet handed over whole, and in
  `_package` the second pass held before the zip writer sees a byte,
  `list(second)` or `("".join(second),)`.
"""

import importlib.util
import io
import pathlib
import random
import struct
import sys
import tracemalloc
import typing
import zipfile

import pytest

import workbook_stream_cases as cases
from synthtwin import generation, sheetwriting, writing

SHEET = "xl/worksheets/sheet1.xml"


def _described(folder: pathlib.Path, name: str) -> "tuple[object, generation.Twin]":
    """One battery case described by the real producer and generated at seed 0."""
    make, sheet = cases.BATTERY[name]
    described = cases.describe_book(folder / name, name, make(), sheet)
    return described, generation.generate(described, 0)


def _sheet_bytes(data: bytes) -> bytes:
    """The worksheet member of a written package, uncompressed."""
    with zipfile.ZipFile(_bytes_path(data)) as bundle:
        names = [name for name in bundle.namelist() if name.startswith("xl/worksheets/sheet")]
        return b"".join(bundle.read(name) for name in names)


_SCRATCH: "list[pathlib.Path]" = []


def _bytes_path(data: bytes) -> pathlib.Path:
    """``data`` written to this module's scratch file; its path."""
    target = _SCRATCH[0] / "read-back.zip"
    target.write_bytes(data)
    return target


@pytest.fixture(autouse=True)
def _scratch(tmp_path: pathlib.Path) -> typing.Iterator[None]:
    _SCRATCH[:] = [tmp_path]
    yield
    _SCRATCH[:] = []


# -- the bytes ------------------------------------------------------------


def test_every_workbook_golden_is_written_byte_for_byte_as_before(tmp_path: pathlib.Path) -> None:
    """Method G2.2's five workbook goldens: the same bytes, and the same part texts."""
    for name in cases.GOLDENS:
        described, twin = cases.golden(name, tmp_path / name)
        old, new = cases.both_files(tmp_path / name / "out", described, twin)
        assert cases.package_differences(old, new) == [], name
        texts = sheetwriting.workbook_members(described, twin)
        streamed = sheetwriting.workbook_stream(described, twin)
        assert [part[0] for part in streamed] == [part[0] for part in texts], name
        for (title, size, pieces), (_title, text) in zip(streamed, texts):
            joined = "".join(pieces)
            assert joined == text, (name, title)
            assert size == len(text.encode("utf-8")), (name, title)


@pytest.mark.parametrize("name", sorted(cases.BATTERY))
def test_every_battery_and_zoo_workbook_is_written_byte_for_byte_as_before(
    tmp_path: pathlib.Path, name: str
) -> None:
    """The workbook battery, the zoo's surveys.xlsx and the seeded wide table."""
    described, twin = _described(tmp_path, name)
    old, new = cases.both_files(tmp_path / "out", described, twin)
    assert cases.package_differences(old, new) == [], name


# -- zip64 exactly where writestr used it ---------------------------------


def _local_extra(data: bytes, member: str) -> bytes:
    """The extra field of ``member``'s LOCAL header in the package ``data``."""
    with zipfile.ZipFile(_bytes_path(data)) as bundle:
        offset = bundle.getinfo(member).header_offset
    assert data[offset : offset + 4] == b"PK\x03\x04"
    name_length, extra_length = struct.unpack("<HH", data[offset + 26 : offset + 30])
    start = offset + 30 + name_length
    return data[start : start + extra_length]


def test_a_sheet_past_the_zip64_line_is_zip64_as_writestr_made_it(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """zipfile's line lowered to 64 KiB: the sheet is zip64 from both writers, same bytes."""
    described, twin = _described(tmp_path, "wide")
    monkeypatch.setattr(zipfile, "ZIP64_LIMIT", 1 << 16)
    old, new = cases.both_files(tmp_path / "out", described, twin)
    monkeypatch.undo()
    assert cases.package_differences(old, new) == []
    # The zip64 extra field (header id 1) on the sheet, and on no small part.
    assert _local_extra(new, SHEET)[:2] == b"\x01\x00"
    assert _local_extra(new, "xl/styles.xml") == b""
    # Unlowered, nothing in this package is zip64.
    plain_old, plain_new = cases.both_files(tmp_path / "plain", described, twin)
    assert cases.package_differences(plain_old, plain_new) == []
    assert _local_extra(plain_new, SHEET) == b""
    assert _sheet_bytes(new) == _sheet_bytes(plain_new)


def test_mutant_the_member_not_told_its_size_is_never_zip64(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A writer that streams without declaring the size: zipfile never picks zip64, red."""
    described, twin = _described(tmp_path, "wide")
    monkeypatch.setattr(zipfile, "ZIP64_LIMIT", 1 << 16)
    old = cases.as_built_file(tmp_path / "old.xlsx", cases.as_built_members(described, twin))
    shipped = zipfile.ZipFile.open

    def untold(self: zipfile.ZipFile, name: object, mode: str = "r", *rest: object, **keywords: object) -> object:
        if mode == "w" and isinstance(name, zipfile.ZipInfo):
            name.file_size = 0
        return shipped(self, name, mode, *rest, **keywords)  # type: ignore[arg-type]

    monkeypatch.setattr(zipfile.ZipFile, "open", untold)
    red = False
    try:
        new = cases.streamed_file(tmp_path / "new.xlsx", described, twin)
        red = cases.package_differences(old, new) != []
    except (RuntimeError, zipfile.LargeZipFile):
        red = True
    assert red, "a member not told its size wrote writestr's bytes"


def _pieces_mutated(
    monkeypatch: pytest.MonkeyPatch, how: "typing.Callable[[list[str]], list[str]]"
) -> None:
    """Every sheet's pieces changed by ``how``, in both passes."""
    shipped = sheetwriting._sheet_pieces

    def mutated(*arguments: object) -> "typing.Iterator[str]":
        for piece in how(list(shipped(*arguments))):  # type: ignore[arg-type]
            yield piece

    monkeypatch.setattr(sheetwriting, "_sheet_pieces", mutated)


@pytest.mark.parametrize(
    "mutant",
    [
        ("a row copied twice", lambda pieces: pieces[:3] + pieces[2:]),
        ("two rows swapped", lambda pieces: pieces[:2] + [pieces[3], pieces[2]] + pieces[4:]),
    ],
    ids=["row_twice", "rows_swapped"],
)
def test_mutants_of_the_rows_go_red(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    mutant: "tuple[str, typing.Callable[[list[str]], list[str]]]",
) -> None:
    """The byte check reads the rows: each mutant's file differs from b075342a's."""
    described, twin = _described(tmp_path, "typed")
    old = cases.as_built_file(tmp_path / "old.xlsx", cases.as_built_members(described, twin))
    new = cases.streamed_file(tmp_path / "new.xlsx", described, twin)
    assert cases.package_differences(old, new) == []
    _pieces_mutated(monkeypatch, mutant[1])
    mutated = cases.streamed_file(tmp_path / "mutant.xlsx", described, twin)
    assert cases.member_differences(old, mutated) != [], mutant[0]


# -- what "the same file" means on each zlib ------------------------------


def _rewritten(
    data: bytes,
    level: int,
    change: "typing.Callable[[zipfile.ZipInfo, bytes], tuple[zipfile.ZipInfo, bytes]] | None" = None,
    order: "typing.Callable[[list[zipfile.ZipInfo]], list[zipfile.ZipInfo]] | None" = None,
) -> bytes:
    """``data``'s members written again by `writestr` at deflate ``level``, each
    first passed through ``change`` and the list through ``order``."""
    out = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as source, zipfile.ZipFile(out, "w") as bundle:
        entries = source.infolist()
        if order is not None:
            entries = order(entries)
        for entry in entries:
            copied = zipfile.ZipInfo(entry.filename, entry.date_time)
            copied.compress_type = entry.compress_type
            copied.external_attr = entry.external_attr
            text = source.read(entry)
            if change is not None:
                copied, text = change(copied, text)
            bundle.writestr(copied, text, compresslevel=level)
    return out.getvalue()


def test_a_package_deflated_another_way_is_the_same_package_member_by_member(
    tmp_path: pathlib.Path,
) -> None:
    """Skeptic 1 of lane XW, item 3: on zlib-ng the deflate stream may move.

    The typed battery's package written again at deflate level 1 stands in
    for zlib-ng's other stream: its bytes differ, so off zlib-ng the bytes
    check is red, and member by member it is the same package.
    """
    described, twin = _described(tmp_path, "typed")
    old = cases.streamed_file(tmp_path / "new.xlsx", described, twin)
    again = _rewritten(old, 6)
    other = _rewritten(old, 1)
    assert cases.package_differences(old, again) == []
    assert other != again
    assert cases.member_differences(again, other) == []
    assert cases.package_differences(again, other) == ([] if cases.ZLIB_NG else ["the bytes"])


@pytest.mark.parametrize(
    "mutant",
    [
        "date_time",
        "external_attr",
        "compress_type",
        "text",
        "order",
    ],
)
def test_mutants_of_a_member_go_red_member_by_member(tmp_path: pathlib.Path, mutant: str) -> None:
    """The member-by-member check reads every field it names: each mutant red."""
    described, twin = _described(tmp_path, "typed")
    old = _rewritten(cases.streamed_file(tmp_path / "new.xlsx", described, twin), 1)

    def change(entry: zipfile.ZipInfo, text: bytes) -> "tuple[zipfile.ZipInfo, bytes]":
        if entry.filename != SHEET:
            return entry, text
        if mutant == "date_time":
            entry.date_time = (1980, 1, 2, 0, 0, 0)
        if mutant == "external_attr":
            entry.external_attr = 0o644 << 16
        if mutant == "compress_type":
            entry.compress_type = zipfile.ZIP_STORED
        if mutant == "text":
            text = text.replace(b"<row ", b"<row  ", 1)
        return entry, text

    def swapped(entries: "list[zipfile.ZipInfo]") -> "list[zipfile.ZipInfo]":
        return entries[1:2] + entries[:1] + entries[2:]

    if mutant == "order":
        mutated = _rewritten(old, 1, order=swapped)
    else:
        mutated = _rewritten(old, 1, change)
    assert cases.member_differences(old, _rewritten(old, 1)) == []
    assert cases.member_differences(old, mutated) != [], mutant


def _raw_extras(monkeypatch: pytest.MonkeyPatch) -> None:
    """The comparator's mutant: the zip64 field compared as raw bytes again."""
    monkeypatch.setattr(cases, "_stream_free_extra", lambda extra: (extra, False))


def test_a_zip64_package_deflated_another_way_is_the_same_member_by_member(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Skeptic 2 of lane XW, finding 1, and Codex's item 2: past the zip64
    line the zip64 field carries the compressed size (local and central)
    and the offset (central), which move with the deflate stream.

    zipfile's line lowered to 64 KiB, the wide battery twin's package and
    the same package deflated at level 1 (zlib-ng's other stream, as
    above) are the same member by member; compared raw, the zip64 field
    is red.
    """
    described, twin = _described(tmp_path, "wide")
    monkeypatch.setattr(zipfile, "ZIP64_LIMIT", 1 << 16)
    new = cases.streamed_file(tmp_path / "new.xlsx", described, twin)
    again = _rewritten(new, 6)
    other = _rewritten(new, 1)
    assert _local_extra(other, SHEET)[:2] == b"\x01\x00"
    assert cases.package_differences(new, again) == []
    assert other != again
    assert cases.member_differences(again, other) == []
    _raw_extras(monkeypatch)
    raw = cases.member_differences(again, other)
    assert f"{SHEET}: extra" in raw and f"{SHEET}: the local header" in raw, raw


def _offsets_package(level: int) -> bytes:
    """Twelve members of 100,000 characters of repeated words, deflated at ``level``."""
    draw = random.Random(20261020)
    words = [f"word{index}" for index in range(300)]
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as bundle:
        for index in range(12):
            text = " ".join(draw.choice(words) for _ in range(16_000))[:100_000]
            entry = zipfile.ZipInfo(f"part{index:02d}.xml", (1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(entry, text, compresslevel=level)
    return out.getvalue()


def test_an_offset_past_the_zip64_line_in_one_stream_only_is_the_same_package(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Codex's item 2: the offset moves with the deflate stream, so one
    stream can put a member's header past the zip64 line where the other
    does not. The central record then carries a zip64 field with the
    offset alone, and zipfile raises its two version numbers to 45; the
    member is the same. Compared raw, red."""
    tight, loose = _offsets_package(9), _offsets_package(1)
    with zipfile.ZipFile(io.BytesIO(tight)) as one, zipfile.ZipFile(io.BytesIO(loose)) as two:
        near, far = one.infolist()[-1].header_offset, two.infolist()[-1].header_offset
        largest = max(entry.file_size for entry in one.infolist())
    line = (near + far) // 2
    assert near < line < far and largest * 1.05 < line, (near, far, largest)
    monkeypatch.setattr(zipfile, "ZIP64_LIMIT", line)
    tight, loose = _offsets_package(9), _offsets_package(1)
    with zipfile.ZipFile(io.BytesIO(tight)) as one, zipfile.ZipFile(io.BytesIO(loose)) as two:
        assert one.infolist()[-1].extra == b"" and two.infolist()[-1].extra[:2] == b"\x01\x00"
        assert (one.infolist()[-1].create_version, two.infolist()[-1].create_version) == (20, 45)
    assert cases.member_differences(tight, loose) == []
    _raw_extras(monkeypatch)
    raw = cases.member_differences(tight, loose)
    assert "part11.xml: extra" in raw, raw


# -- the memory -----------------------------------------------------------


def _traced_write(folder: pathlib.Path, n_rows: int) -> "tuple[int, int]":
    """(the most traced as held above a pass's start, the sheet's bytes).

    The sheet is written as `workbook_stream` writes the table's sheet:
    one pass counting its bytes and giving every text its place, then
    the pieces of a second pass handed to `writing.write_workbook_file`.
    Each pass is traced whole, `tracemalloc` started BEFORE its
    `_sheet_pieces` is called (Codex's review of lane XW, item 1): a
    pass that lists or joins its pieces on the call, or on its first
    piece, is traced doing it. Repair 1 traced the last fifth of each
    pass alone, and a `_sheet_pieces` that listed every piece before
    yielding the first held the whole sheet before the window opened,
    green.
    """
    arguments = cases.sheet_arguments(n_rows)
    items = arguments[14]
    held = 0
    try:
        tracemalloc.start()
        began = tracemalloc.get_traced_memory()[0]
        size = sheetwriting._bytes_of(sheetwriting._sheet_pieces(*arguments))
        held = max(held, tracemalloc.get_traced_memory()[1] - began)
    finally:
        tracemalloc.stop()
    try:
        tracemalloc.start()
        began = tracemalloc.get_traced_memory()[0]
        second = sheetwriting._places_already_taken(sheetwriting._sheet_pieces(*arguments), items)
        writing.write_workbook_file(folder / f"sheet-{n_rows}.zip", [(SHEET, size, second)])
        held = max(held, tracemalloc.get_traced_memory()[1] - began)
    finally:
        tracemalloc.stop()
    with zipfile.ZipFile(folder / f"sheet-{n_rows}.zip") as bundle:
        assert bundle.getinfo(SHEET).file_size == size
    return held, size


def _far_below(held: int, size: int) -> bool:
    """The memory case's bound: at most a hundredth of the sheet held at once."""
    return held < size // 100


def test_a_100000_by_50_sheet_is_written_far_below_its_own_size(tmp_path: pathlib.Path) -> None:
    """At most a hundredth of the sheet held at once (measured: 343,810 bytes of
    177,369,480, the zip writer's own buffers; 343,672 at 10,000 rows).

    Each pass traced from before its first piece to its end. b075342a's
    writer held the whole sheet's text before the zip writer saw a byte
    -- at least the sheet's own size, and a copy of it for every row,
    which the library study measured past 1.9 GB at this size.
    """
    held, size = _traced_write(tmp_path, 100_000)
    assert size > 100_000_000, size
    assert _far_below(held, size), (held, size)


def _listed_on_the_call(monkeypatch: pytest.MonkeyPatch) -> None:
    """`_sheet_pieces` made a function that lists every piece when called."""
    shipped = sheetwriting._sheet_pieces

    def listed(*arguments: object) -> "typing.Iterator[str]":
        return iter(list(shipped(*arguments)))  # type: ignore[arg-type]

    monkeypatch.setattr(sheetwriting, "_sheet_pieces", listed)


@pytest.mark.parametrize(
    "mutant",
    [
        # Codex's item 1 exactly: a lazy pass that lists every piece on
        # its first advance, then yields them one by one.
        ("listed on the first piece", lambda monkeypatch: _pieces_mutated(monkeypatch, lambda pieces: pieces)),
        ("listed on the call", _listed_on_the_call),
        ("handed over whole", lambda monkeypatch: _pieces_mutated(monkeypatch, lambda pieces: ["".join(pieces)])),
    ],
    ids=["listed_first_piece", "listed_on_call", "joined"],
)
def test_mutants_holding_the_sheet_break_the_memory_bound(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    mutant: "tuple[str, typing.Callable[[pytest.MonkeyPatch], None]]",
) -> None:
    """A pass that holds the whole sheet, however it holds it, breaks the bound."""
    mutant[1](monkeypatch)
    held, size = _traced_write(tmp_path, 5_000)
    assert not _far_below(held, size), (mutant[0], held, size)
    assert held >= size // 2, (mutant[0], held, size)


# -- the real route hands the second pass on unmade -----------------------


def _route_faults(folder: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> "list[str]":
    """What is wrong with the real route's second pass, on the wide battery twin.

    `sheetwriting.workbook_stream` must make the sheet ONCE (the first
    pass) and hand the second on as an iterator nothing has drawn from;
    `writing.write_workbook_file` then draws it, as many pieces as the
    first. Each call of `_sheet_pieces` is counted piece by piece.
    """
    described, twin = _described(folder, "wide")
    made: "list[int]" = []
    shipped = sheetwriting._sheet_pieces

    def counted(*arguments: object) -> "typing.Iterator[str]":
        nonlocal made
        call = len(made)
        made += [0]
        for piece in shipped(*arguments):  # type: ignore[arg-type]
            made[call] += 1
            yield piece

    monkeypatch.setattr(sheetwriting, "_sheet_pieces", counted)
    faults: "list[str]" = []
    members = sheetwriting.workbook_stream(described, twin)
    if len(made) != 1 or made[0] <= 600:
        faults += [f"passes made before the zip writer took one: {made}"]
    sheets = [part for part in members if part[0] == SHEET]
    if len(sheets) != 1 or iter(sheets[0][2]) is not sheets[0][2]:
        faults += ["the sheet's pieces are a container, not a stream"]
    writing.write_workbook_file(folder / "route.xlsx", members)
    if len(made) != 2 or made[1] != made[0]:
        faults += [f"the second pass was not drawn whole by the writer: {made}"]
    return faults


def test_the_real_route_hands_the_second_pass_on_unmade(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Skeptic 1 of lane XW, item 2: the memory case above drives the pieces
    by hand; this drives `workbook_stream` and `write_workbook_file`."""
    assert _route_faults(tmp_path, monkeypatch) == []


@pytest.mark.parametrize(
    "mutant",
    [
        ("the second pass made into a list", lambda pieces: list(pieces)),
        ("the second pass joined into one text", lambda pieces: ("".join(pieces),)),
    ],
    ids=["second_listed", "second_joined"],
)
def test_mutants_of_the_route_holding_the_second_pass_go_red(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    mutant: "tuple[str, typing.Callable[[typing.Iterator[str]], typing.Iterable[str]]]",
) -> None:
    """`_package` holding the whole second pass before the zip writer sees a
    byte -- `list(second)` or `("".join(second),)` -- goes red."""
    shipped = sheetwriting._places_already_taken

    def held(pieces: "typing.Iterator[str]", items: "list[str]") -> "typing.Iterable[str]":
        return mutant[1](shipped(pieces, items))

    monkeypatch.setattr(sheetwriting, "_places_already_taken", held)
    assert _route_faults(tmp_path, monkeypatch) != [], mutant[0]


# -- K-S4-22's driver runs where `resource` is not ------------------------


def test_the_kpi_driver_runs_where_resource_is_not(monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's review of lane XW, item 3: Windows has no `resource`.

    The driver imported with `resource` unimportable (as on Windows)
    loads, and one size is measured with its seconds and bytes and its
    memory recorded as null. An unconditional `import resource` is red.
    """
    monkeypatch.setitem(sys.modules, "resource", None)
    monkeypatch.setattr(sys, "path", list(sys.path))
    path = pathlib.Path(__file__).resolve().parents[1] / "tools" / "measurements" / "kpi_workbook_stream.py"
    spec = importlib.util.spec_from_file_location("kpi_workbook_stream_without_resource", path)
    assert spec is not None and spec.loader is not None
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    assert driver.resource is None
    measured = driver.one_size(300)
    assert measured["sheet_bytes"] > 0 and measured["file_bytes"] > 0, measured
    assert measured["seconds"] >= measured["seconds_write"] >= 0, measured
    for key in ("rss_mb_before_parts", "peak_rss_mb_after_parts", "peak_rss_mb"):
        assert measured[key] is None, (key, measured)


# -- the guards -------------------------------------------------------------


def test_a_part_not_the_size_it_was_declared_is_refused(tmp_path: pathlib.Path) -> None:
    """The member is told its size first, so a size that is wrong is a defect, refused."""
    with pytest.raises(TypeError, match="not the size it was declared"):
        writing.write_workbook_file(tmp_path / "wrong.zip", [("a.xml", 5, iter(["abc"]))])


def test_a_second_pass_meeting_new_text_is_refused() -> None:
    """The shared strings are written before the sheet: a text new to the second pass is refused."""
    items = ["kept"]
    pieces = sheetwriting._places_already_taken(iter(["<row/>"]), items)
    assert next(pieces) == "<row/>"
    items += ["new"]
    with pytest.raises(TypeError, match="second pass"):
        next(pieces)
