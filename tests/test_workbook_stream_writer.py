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
  cut, the same package member by member -- every header field, every
  text -- with only the compressed bytes free (skeptic 1, item 3). The
  member-by-member check is red on a moved date, attribute, method, text
  or order, and a package deflated at another level stands in for
  zlib-ng's other stream.
* zip64 exactly where `writestr` used it: with zipfile's four-gigabyte
  line lowered, a sheet past it gets the zip64 header from both writers,
  the same bytes again, and a writer that does not tell the member its
  size goes red.
* The memory: a sheet of 100,000 rows of fifty columns is written with
  `tracemalloc`, over the last fifth of each pass, seeing at most a
  hundredth of the sheet's bytes held at once above what was held when
  it started; the writer of b075342a held the whole sheet's text, and
  its copies, before the zip writer saw a byte.
* The real route: `workbook_stream` makes the sheet once and hands the
  second pass on as an iterator nothing has drawn, and
  `write_workbook_file` draws all of it (skeptic 1, item 2).
* Mutants, each red: a row copied twice, two rows swapped, the member
  not told its size (never zip64), the sheet handed over whole, and in
  `_package` the second pass held before the zip writer sees a byte,
  `list(second)` or `("".join(second),)`.
"""

import io
import pathlib
import struct
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


# -- the memory -----------------------------------------------------------


def _windowed(
    pieces: "typing.Iterable[str]", start_at: int, readings: "list[int]"
) -> "typing.Iterator[str]":
    """``pieces`` as they are, `tracemalloc` started at piece ``start_at``.

    ``readings`` gains what was traced as held when it started (nought
    unless something else is tracing).
    """
    if start_at == 0:
        tracemalloc.start()
        readings += [tracemalloc.get_traced_memory()[0]]
    count = 0
    for piece in pieces:
        count += 1
        if count == start_at:
            tracemalloc.start()
            readings += [tracemalloc.get_traced_memory()[0]]
        yield piece


def _traced_write(folder: pathlib.Path, n_rows: int, window_from: int) -> "tuple[int, int]":
    """(the most traced as held above a window's start, the sheet's bytes).

    The sheet is written as `workbook_stream` writes the table's sheet:
    one pass counting its bytes and giving every text its place, then
    the pieces of a second pass handed to `writing.write_workbook_file`.
    Each pass is traced from its piece ``window_from`` to its end: a
    writer whose memory grows with the sheet grows inside the window by
    the window's share of the sheet, and tracing every row would only
    take four times as long (168 s at this size, measured).
    """
    arguments = cases.sheet_arguments(n_rows)
    items = arguments[14]
    held = 0
    readings: "list[int]" = []
    try:
        size = sheetwriting._bytes_of(
            _windowed(sheetwriting._sheet_pieces(*arguments), window_from, readings)
        )
        assert len(readings) == 1, "the first pass was never traced"
        held = max(held, tracemalloc.get_traced_memory()[1] - readings[-1])
    finally:
        tracemalloc.stop()
    try:
        second = sheetwriting._places_already_taken(
            _windowed(sheetwriting._sheet_pieces(*arguments), window_from, readings), items
        )
        writing.write_workbook_file(folder / f"sheet-{n_rows}.zip", [(SHEET, size, second)])
        assert len(readings) == 2, "the second pass was never traced"
        held = max(held, tracemalloc.get_traced_memory()[1] - readings[-1])
    finally:
        tracemalloc.stop()
    with zipfile.ZipFile(folder / f"sheet-{n_rows}.zip") as bundle:
        assert bundle.getinfo(SHEET).file_size == size
    return held, size


def test_a_100000_by_50_sheet_is_written_far_below_its_own_size(tmp_path: pathlib.Path) -> None:
    """At most a hundredth of the sheet held at once (measured: about 0.3 MB of 154 MB).

    Traced over the last 20,000 rows of each pass. b075342a's writer held
    the whole sheet's text before the zip writer saw a byte -- at least
    the sheet's own size, and a copy of it for every row, which the
    library study measured past 1.9 GB at this size.
    """
    held, size = _traced_write(tmp_path, 100_000, 80_000)
    assert size > 100_000_000, size
    assert held < size // 100, (held, size)


def test_mutant_the_sheet_handed_over_whole_goes_red(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A writer that joins the sheet before handing it on holds at least its size."""
    _pieces_mutated(monkeypatch, lambda pieces: ["".join(pieces)])
    held, size = _traced_write(tmp_path, 5_000, 0)
    assert held >= size, (held, size)


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
