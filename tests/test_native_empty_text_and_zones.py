"""Parquet's two kinds of nothing in a text column, and a zone Arrow alone named (lane TOOLS).

The outside review of batch 4zz, items 10 and 11, both on files Arrow or
pandas write every day:

- ITEM 10. A text column alternating `""` and `"A"` over 20,000 rows holds
  no missing value; its twin held 10,000 missing values, because a cell
  held one spelling, "", for both an empty text and a missing one, and the
  writer wrote "" as missing. `df[col] == ""`, `isna()` and `fillna()` then
  count differently on the twin. Now the column's empty text has a cell of
  its own (`native.NativeColumn.empty_text`): "" itself where the column
  holds no missing value, else the shortest run of spaces no cell holds,
  and the writer writes each back as its own kind.
- ITEM 11. A `timestamp[us, America/Chicago]` column written by Arrow, with
  no pandas block, keeps its zone only in the file's `ARROW:schema` record;
  it was read as no zone, the twin was written in universal time, and
  18:00 on 31 December read back as 00:00 on 1 January. Now the zone is
  read from that record (`native.arrow_zones`) and the twin's own record
  names it again.

Each table is invented here, 400 rows (the suite's floor switch is off),
through `profile`, `generate` and `validate`; each guard is shown to be
what holds by a mutant named in the test's docstring.
"""

from __future__ import annotations

import datetime
import pathlib
import random

import pytest

pandas = pytest.importorskip("pandas")
pyarrow = pytest.importorskip("pyarrow")
parquet = pytest.importorskip("pyarrow.parquet")

from synthtwin import cli, native, nativereading, nativewriting  # noqa: E402

ROWS = 400


def _round_trip(table: "pyarrow.Table", folder: pathlib.Path) -> "tuple[pandas.DataFrame, pandas.DataFrame, pathlib.Path]":
    """The table written by Arrow, described, its twin generated and validated; (real, twin, description) as pandas reads them."""
    source = folder / "visits.parquet"
    parquet.write_table(table, str(source))
    assert cli.main(["profile", str(source)]) == 0
    description = folder / "visits-profile.json"
    assert cli.main(["generate", str(description), "--seed", "3"]) == 0
    twin = folder / "visits-twin.parquet"
    assert cli.main(["validate", str(description), "--twin", str(twin)]) == 0
    return pandas.read_parquet(str(source)), pandas.read_parquet(str(twin)), description


def _identity(source: pathlib.Path, out: pathlib.Path) -> None:
    """The writer's file from the file's own cells, no generation between."""
    opening = source.read_bytes()[: native.OPENING_BYTES]
    found = nativereading.read_native(str(source), native.kind_of(opening), opening)
    out.write_bytes(nativewriting.twin_file(found.form, found.names, found.columns, found.n_rows).data)


def _texts(rows: int, seed: int, missing_too: bool) -> "list[str | None]":
    rng = random.Random(seed)
    out: "list[str | None]" = []
    for index in range(rows):
        if missing_too and index % 4 == 3:
            out += [None]
        else:
            out += ["" if index % 2 else rng.choice(["A", "B", "C"])]
    return out


def test_empty_texts_with_no_missing_value_stay_empty_texts(tmp_path: pathlib.Path) -> None:
    """The reviewer's column: "" beside labels, no missing value. Real 0 missing, half empty; the twin the same.

    Red on: the writer writing the cell "" as missing whatever the column's
    empty text (the twin then holds 200 missing values).
    """
    table = pyarrow.table({"note": pyarrow.array(_texts(ROWS, 1, False), type=pyarrow.string()),
                           "n": pyarrow.array(list(range(ROWS)), type=pyarrow.int64())})
    real, twin, _ = _round_trip(table, tmp_path)
    assert int(real["note"].isna().sum()) == 0 and int((real["note"] == "").sum()) == ROWS // 2
    assert int(twin["note"].isna().sum()) == 0
    assert int((twin["note"] == "").sum()) == ROWS // 2


def test_empty_texts_and_missing_values_are_counted_apart(tmp_path: pathlib.Path) -> None:
    """Both kinds in one column: the description gives the empty text a run of spaces, and the twin holds each kind as often as the table.

    The identity round trip (reader, then writer) is exact, nulls and empty
    texts in their rows. Red on: the reader giving an empty text the cell ""
    (no `empty_text`: the twin's 100 empty texts become missing values).
    """
    values = _texts(ROWS, 2, True)
    table = pyarrow.table({"note": pyarrow.array(values, type=pyarrow.string())})
    real, twin, description = _round_trip(table, tmp_path)
    assert '"empty_text": " "' in description.read_text(encoding="utf-8")
    real_missing, real_empty = int(real["note"].isna().sum()), int((real["note"] == "").sum())
    assert (real_missing, real_empty) == (100, 100)
    assert int(twin["note"].isna().sum()) == real_missing
    assert int((twin["note"] == "").sum()) == real_empty
    out = tmp_path / "identity.parquet"
    _identity(tmp_path / "visits.parquet", out)
    again = parquet.read_table(str(out)).column("note").to_pylist()
    assert again == values


def test_a_column_holding_spaces_takes_a_longer_run(tmp_path: pathlib.Path) -> None:
    """Where a cell is one space, the empty text's cell is two: no real cell is taken for an empty one."""
    assert native.empty_text_for(["a", None, "", " "]) == "  "
    assert native.empty_text_for(["a", None, ""]) == " "
    assert native.empty_text_for(["a", ""]) == ""
    assert native.empty_text_for(["a", None]) is None
    assert native.empty_text_for([" " * length for length in range(1, native.EMPTY_TEXT_MOST + 1)] + ["", None]) is None
    values = ["x", None, "", " "] * (ROWS // 4)
    source = tmp_path / "spaces.parquet"
    parquet.write_table(pyarrow.table({"note": pyarrow.array(values, type=pyarrow.string())}), str(source))
    out = tmp_path / "identity.parquet"
    _identity(source, out)
    assert parquet.read_table(str(out)).column("note").to_pylist() == values


def test_a_description_without_the_key_still_loads_and_a_bad_cell_is_refused() -> None:
    """The key is written only where it says something: every older native block loads; a cell that is not spaces is refused."""
    column = native.NativeColumn(storage=native.STORE_STRING, written_as=native.WRITTEN_TEXT)
    form = native.NativeForm(system=native.FORMAT_PARQUET, version=1, columns=(column,))
    document = native.document_of(form)
    assert "empty_text" not in document["columns"][0]
    assert native.form_of(document, 1) == form
    marked = native.NativeForm(system=native.FORMAT_PARQUET, version=1,
                               columns=(native.NativeColumn(storage=native.STORE_STRING,
                                                            written_as=native.WRITTEN_TEXT, empty_text=" "),))
    document = native.document_of(marked)
    assert document["columns"][0]["empty_text"] == " "
    assert native.form_of(document, 1) == marked
    document["columns"][0]["empty_text"] = "Maria"
    with pytest.raises(native.NativeFormError):
        native.form_of(document, 1)


def _zoned(rows: int) -> "pyarrow.Table":
    """Arrow's own table, no pandas block: one stamp column in Chicago's zone, 18:00 on 31 December among its stamps."""
    start = datetime.datetime(2023, 12, 31, 18, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=-6)))
    stamps = [start + datetime.timedelta(hours=7 * index) for index in range(rows)]
    return pyarrow.table({
        "seen": pyarrow.array(stamps, type=pyarrow.timestamp("us", tz="America/Chicago")),
        "n": pyarrow.array([index % 9 for index in range(rows)], type=pyarrow.int64()),
    })


def test_a_zone_arrow_alone_named_is_read_and_written_again(tmp_path: pathlib.Path) -> None:
    """The source carries no pandas block; the zone is read from Arrow's record and the twin reads back in it.

    The identity round trip gives back the same stamps in the same zone
    (18:00 on 31 December is 18:00 on 31 December), and the generated twin's
    column is `America/Chicago`'s as the table's is. Red on: the reader
    ignoring Arrow's record (the twin reads back in UTC: 00:00 on 1 January).
    """
    table = _zoned(ROWS)
    source = tmp_path / "zoned.parquet"
    parquet.write_table(table, str(source))
    metadata = parquet.read_metadata(str(source)).metadata
    assert b"pandas" not in metadata, "premise: Arrow's own file, no pandas block"
    out = tmp_path / "identity.parquet"
    _identity(source, out)
    back = parquet.read_table(str(out))
    assert str(back.schema.field("seen").type) == "timestamp[us, tz=America/Chicago]"
    first = back.column("seen").to_pylist()[0]
    assert (first.year, first.month, first.day, first.hour) == (2023, 12, 31, 18)
    real, twin, description = _round_trip(table, tmp_path)
    assert '"zone": "America/Chicago"' in description.read_text(encoding="utf-8")
    assert str(twin["seen"].dtype) == str(real["seen"].dtype) == "datetime64[us, America/Chicago]"


def test_the_arrow_record_reader_never_raises() -> None:
    """Every damaged record gives what it read before the fault, never an error; base64 of pyarrow's own record gives its zones."""
    rng = random.Random(4)
    good = native.arrow_schema_text(
        native.NativeForm(system=native.FORMAT_PARQUET, version=1, columns=(
            native.NativeColumn(storage=native.STORE_TIMESTAMP_US, written_as=native.WRITTEN_STAMP, utc=True,
                                zone="Europe/Paris"),
        )),
        ("when",), (True,), "",
    )
    assert native.arrow_zones(good) == {"when": "Europe/Paris"}
    for _ in range(2000):
        cut = rng.randrange(len(good))
        damaged = good[:cut] + rng.choice("ABCxyz019+/=") + good[cut + 1:]
        assert isinstance(native.arrow_zones(damaged), dict)
        assert isinstance(native.arrow_zones(good[:cut]), dict)
    for text in ("", "====", "not base64 at all", "AAAAAAAAAAAA", "/////////////w=="):
        assert native.arrow_zones(text) == {}
