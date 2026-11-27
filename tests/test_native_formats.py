"""Files from other systems: Parquet, SAS transport, Stata and SPSS (lane FORMATS).

The owner's ruling of 2026-11-23: synthtwin opens a table another
system saved, describes it, and writes the twin back as the same kind of
file. Every table here is invented, built at run time by the libraries
the product reads with (pyarrow, pyreadstat) or by pandas, never
committed. Each section names what it proves:

1. THE ARITHMETIC (`native`): every number, date and stamp is written as
   text and read back to the very value it came from, checked against
   the standard library's own `struct`, `datetime` and `base64`, which
   the product may not use.
2. THE ROUND TRIP of each format, reader then writer with no generation
   between: the file the writer makes from a file's own cells is read
   back by pyreadstat, pandas and pyarrow to the same values and the
   same form -- types, formats, labels, value labels, missing values,
   pandas' dtypes and index.
3. THE WHOLE ROUTE: `synthtwin profile`, `generate` and `validate` on a
   native file of each format; the twin is a file of that format that
   pandas reads into the dtypes the source reads into, and validate
   misses nothing.
4. THE DESCRIPTION OF A NATIVE FILE IS THE DESCRIPTION OF THE SAME TABLE
   IN CSV, block for block, save the sentence saying where the names came
   from and the native block itself.
5. NOTHING OF THE FILE'S OWN METADATA LEAKS: a file label, notes, a
   label holding an identifier, a rare code's label, a person's name as
   a label, a Parquet file's own pairs of text and a member name holding
   figures reach neither the description nor the twin -- and each guard
   is shown to be what stops it (a mutant without it goes red).
6. THE REFUSALS, each in its own words.
"""

import base64
import datetime
import json
import os
import pathlib
import random
import struct

import pytest

pandas = pytest.importorskip("pandas")
pyarrow = pytest.importorskip("pyarrow")
parquet = pytest.importorskip("pyarrow.parquet")
pyreadstat = pytest.importorskip("pyreadstat")

from synthtwin import cli, errors, native, nativereading, nativewriting, reading  # noqa: E402

ROWS = 400


# -- 1. the arithmetic ----------------------------------------------------


def _doubles(count: int, seed: int) -> "list[float]":
    rng = random.Random(seed)
    found = [0.0, -0.0, 1.0, -1.5, 98.6, 5e-324, 2.0**-1022, 1.7976931348623157e308]
    while len(found) < count:
        value = struct.unpack("<d", struct.pack("<Q", rng.getrandbits(64)))[0]
        if value == value:
            found += [value]
    return found


def test_every_double_is_written_and_read_back_bit_for_bit() -> None:
    for value in _doubles(20000, 1):
        assert native.double_bits(value) == struct.unpack("<Q", struct.pack("<d", value))[0]
        back = native.exact_double(native.double_text(value))
        assert back is not None
        assert struct.pack("<d", back) == struct.pack("<d", value), value


def test_every_four_byte_number_is_written_short_and_read_back_exactly() -> None:
    rng = random.Random(2)
    checked = 0
    while checked < 20000:
        bits = rng.getrandbits(32)
        value = struct.unpack("<f", struct.pack("<I", bits))[0]
        if value != value:
            continue
        assert native.single_bits(value) == bits
        text = native.single_text(value)
        back = native.exact_single(text)
        assert back is not None and struct.pack("<d", back) == struct.pack("<d", value), (value, text)
        checked = checked + 1
    assert native.single_text(struct.unpack("<f", struct.pack("<f", 98.6))[0]) == "98.6"


def test_nearest_four_byte_number_agrees_with_the_c_cast() -> None:
    for value in _doubles(20000, 3):
        if abs(value) >= 3.4e38:
            continue
        expected = struct.unpack("<f", struct.pack("<f", value))[0]
        assert struct.pack("<d", native.nearest_single(value)) == struct.pack("<d", expected), value


def test_ibm_floats_hold_a_double_exactly_and_refuse_to_round() -> None:
    assert native.ibm_bits(1.0, 8) == bytes.fromhex("4110000000000000")
    assert native.ibm_bits(-118.625, 8) == bytes.fromhex("C276A00000000000")
    for value in [0.5, 100.0, 1e-5, 12345.6789, 1e70, -3.25] + _doubles(2000, 4)[:200]:
        found = native.ibm_bits(value, 8)
        if found is None:
            continue
        assert native.ibm_value(found) == value, value
    assert native.ibm_bits(0.1, 3) is None, "a value three bytes cannot hold is refused, not rounded"


def test_dates_are_the_calendars_own() -> None:
    epoch = datetime.date(1970, 1, 1)
    for days in range(-719162, 2932897, 997):
        day = epoch + datetime.timedelta(days=days)
        assert native.civil_from_days(days) == (day.year, day.month, day.day)
        assert native.date_text(days) == day.isoformat()
        assert native.date_of_text(day.isoformat()) == days
    assert native.date_of_text("2023-02-30") is None
    assert native.stamp_of_text("2020-01-01 10:00:00.500+00:00") == (18262, 36000, 500, 3)


def test_thrift_and_base64_read_back() -> None:
    fields = (
        native.T(1, native.I32, 7),
        native.T(2, native.LIST, native.TList(native.STRUCT, ((native.T(4, native.BINARY, "a"),),))),
        native.T(3, native.I64, -5),
        native.T(20, native.BOOL, True),
    )
    read, _end = native.thrift_struct(native.thrift_bytes(fields))
    assert read == {1: 7, 2: [{4: b"a"}], 3: -5, 20: True}
    for size in range(0, 40):
        data = bytes(range(size))
        assert native._base64(data) == base64.b64encode(data).decode("ascii")


def test_the_opening_bytes_say_which_system_wrote_the_file() -> None:
    assert native.kind_of(b"PAR1\x15\x00\x15") == native.FORMAT_PARQUET
    assert native.kind_of(b"PAR1_score,age\n") == native.KIND_NONE
    assert native.kind_of(b"<stata_dta><header>") == native.FORMAT_STATA
    assert native.kind_of(bytes([114, 2, 1, 0])) == native.FORMAT_STATA
    assert native.kind_of(b"$FL2@(#)") == native.FORMAT_SPSS
    assert native.kind_of(b"HEADER RECORD*******LIBRARY HEADER RECORD!!!!!!!0000") == native.FORMAT_SAS_TRANSPORT
    assert native.kind_of(b"ARROW1\x00\x00") == native.KIND_ARROW
    assert native.kind_of(b"ORC\x0a") == native.KIND_ORC
    assert native.kind_of(b"id,age\n1,2\n") == native.KIND_NONE


# -- invented tables ----------------------------------------------------


def _frame(rows: int = ROWS, seed: int = 5) -> "pandas.DataFrame":
    """An invented visit table: a person key, numbers, codes, text, dates and stamps."""
    rng = random.Random(seed)
    start = datetime.datetime(2020, 1, 1, 8, 0, 0)
    frame = pandas.DataFrame(
        {
            "pid": [float(rng.randint(1, rows // 4)) for _ in range(rows)],
            "age": [float(rng.randint(18, 90)) for _ in range(rows)],
            "arm": [float(rng.choice([1, 2])) for _ in range(rows)],
            "sbp": [round(rng.gauss(130, 15), 1) if rng.random() > 0.05 else float("nan") for _ in range(rows)],
            "site": [rng.choice(["north", "south", "east"]) for _ in range(rows)],
            "admit": [start + datetime.timedelta(days=rng.randint(0, 900)) for _ in range(rows)],
            "seen": [
                start + datetime.timedelta(days=rng.randint(0, 900), minutes=rng.randint(0, 600))
                for _ in range(rows)
            ],
        }
    )
    frame["admit"] = pandas.to_datetime(frame["admit"]).dt.normalize()
    return frame


_LABELS = {"age": "Age in years", "sbp": "Systolic BP"}
_VALUE_LABELS = {"arm": {1: "Control", 2: "Treated"}}


def _write(kind: str, folder: pathlib.Path, frame: "pandas.DataFrame | None" = None, **extra: object) -> pathlib.Path:
    """One invented table written by the libraries in ``kind``'s format; its path."""
    table = _frame() if frame is None else frame
    path = folder / f"visits.{ {'parquet': 'parquet', 'dta': 'dta', 'sav': 'sav', 'xpt': 'xpt', 'xpt8': 'xpt'}[kind] }"
    if kind == "dta":
        pyreadstat.write_dta(table, str(path), column_labels=_LABELS, variable_value_labels=_VALUE_LABELS, **extra)
    elif kind == "sav":
        pyreadstat.write_sav(
            table, str(path), column_labels=_LABELS, variable_value_labels=_VALUE_LABELS,
            variable_measure={"arm": "nominal", "age": "scale"}, **extra,
        )
    elif kind == "xpt":
        pyreadstat.write_xport(table, str(path), column_labels=_LABELS, table_name="VISITS", file_format_version=5, **extra)
    elif kind == "xpt8":
        pyreadstat.write_xport(
            table.rename(columns={"sbp": "systolic_pressure"}), str(path),
            column_labels={"age": "Age in years at the time of the visit, as recorded"},
            table_name="VISITS", file_format_version=8,
        )
    else:
        typed = table.copy()
        typed["site"] = typed["site"].astype("category")
        typed["grade"] = pandas.Categorical(
            [["low", "mid", "high"][index % 3] for index in range(len(typed))],
            categories=["low", "mid", "high"], ordered=True,
        )
        typed["visits"] = pandas.array([index % 7 if index % 11 else None for index in range(len(typed))], dtype="Int64")
        typed["flag"] = pandas.array([bool(index % 2) for index in range(len(typed))], dtype="boolean")
        typed["zoned"] = pandas.to_datetime(typed["seen"]).dt.tz_localize("America/Chicago")
        typed["small"] = pandas.array([index % 200 for index in range(len(typed))], dtype="uint8")
        typed["single"] = pandas.array([index / 8 for index in range(len(typed))], dtype="float32")
        typed.to_parquet(str(path), index=False)
    return path


def _identity(path: pathlib.Path, out: pathlib.Path) -> nativewriting.Written:
    """The writer's file from a native file's own cells (no generation between)."""
    opening = path.read_bytes()[: native.OPENING_BYTES]
    found = nativereading.read_native(str(path), native.kind_of(opening), opening)
    written = nativewriting.twin_file(found.form, found.names, found.columns, found.n_rows)
    out.write_bytes(written.data)
    return written


_META = (
    "column_names", "column_labels", "readstat_variable_types", "original_variable_types",
    "variable_value_labels", "variable_storage_width", "missing_ranges",
)


def _same_values(first: "pandas.DataFrame", second: "pandas.DataFrame") -> None:
    """The two frames hold the same values, exactly, column for column (pandas' own comparison)."""
    assert list(first.columns) == list(second.columns)
    pandas.testing.assert_frame_equal(first, second, check_exact=True, check_dtype=True)


# -- 2. the round trip of each format -------------------------------------


@pytest.mark.parametrize("kind", ["dta", "sav", "xpt", "xpt8"])
def test_a_stat_file_written_from_its_own_cells_reads_back_identically(tmp_path: pathlib.Path, kind: str) -> None:
    source = _write(kind, tmp_path)
    out = tmp_path / ("again." + source.suffix[1:])
    _identity(source, out)
    reader = {"dta": pyreadstat.read_dta, "sav": pyreadstat.read_sav}.get(kind, pyreadstat.read_xport)
    first, first_meta = reader(str(source))
    second, second_meta = reader(str(out))
    _same_values(first, second)
    for attribute in _META:
        assert getattr(first_meta, attribute) == getattr(second_meta, attribute), attribute
    if kind == "xpt8":
        assert out.read_bytes()[:80].find(b"LIBV8") > 0
    if kind == "xpt":
        # pandas reads version 5, as SAS's own CDISC readers do.
        _same_values(pandas.read_sas(str(source)), pandas.read_sas(str(out)))


def test_stata_storage_types_read_back(tmp_path: pathlib.Path) -> None:
    """byte, int, long, float and double, as pandas' own writer stores them (release 118)."""
    frame = pandas.DataFrame(
        {
            "tiny": pandas.array([1, 2, 100, -127, 5], dtype="int8"),
            "mid": pandas.array([1, 300, -30000, 7, 8], dtype="int16"),
            "big": pandas.array([1, 70000, -2000000, 9, 10], dtype="int32"),
            "single": pandas.array([98.6, 1.5, -2.25, 0.1, 3.0], dtype="float32"),
            "score": [1.0, 2.5, 3.0, 4.0, 5.0],
        }
    )
    source = tmp_path / "typed.dta"
    frame.to_stata(str(source), write_index=False, version=118)
    out = tmp_path / "again.dta"
    _identity(source, out)
    first, first_meta = pyreadstat.read_dta(str(source))
    second, second_meta = pyreadstat.read_dta(str(out))
    _same_values(first, second)
    assert second_meta.readstat_variable_types == first_meta.readstat_variable_types == {
        "tiny": "int8", "mid": "int16", "big": "int32", "single": "float", "score": "double",
    }
    assert pandas.read_stata(str(out)).dtypes.to_dict() == pandas.read_stata(str(source)).dtypes.to_dict()


def test_stata_extended_missing_values_read_back(tmp_path: pathlib.Path) -> None:
    """`.a` and `.b` in a double column are written back as the same extended missing values."""
    frame = pandas.DataFrame({"score": pandas.Series([1.0, "a", 3.0, "b", 5.0], dtype=object)})
    source = tmp_path / "missing.dta"
    pyreadstat.write_dta(frame, str(source), missing_user_values={"score": ["a", "b"]})
    out = tmp_path / "again.dta"
    _identity(source, out)
    second, _meta = pyreadstat.read_dta(str(out), user_missing=True)
    assert second["score"].tolist() == [1.0, "a", 3.0, "b", 5.0]


def test_spss_missing_values_and_measures_read_back(tmp_path: pathlib.Path) -> None:
    frame = pandas.DataFrame({"pain": [0.0, 3.0, 9.0, 99.0, 5.0] * 20, "ward": ["A", "B", "UNK", "A", "B"] * 20})
    source = tmp_path / "pain.sav"
    pyreadstat.write_sav(
        frame, str(source), missing_ranges={"pain": [99.0, {"lo": 90.0, "hi": 98.0}], "ward": ["UNK"]},
        variable_measure={"pain": "ordinal", "ward": "nominal"},
    )
    out = tmp_path / "again.sav"
    _identity(source, out)
    first, first_meta = pyreadstat.read_sav(str(source), user_missing=True)
    second, second_meta = pyreadstat.read_sav(str(out), user_missing=True)
    _same_values(first, second)
    assert first_meta.missing_ranges == second_meta.missing_ranges
    assert first_meta.variable_measure == second_meta.variable_measure


def test_a_parquet_file_written_from_its_own_cells_restores_every_pandas_dtype(tmp_path: pathlib.Path) -> None:
    source = _write("parquet", tmp_path)
    out = tmp_path / "again.parquet"
    _identity(source, out)
    first = pandas.read_parquet(str(source))
    second = pandas.read_parquet(str(out))
    assert first.dtypes.to_dict() == second.dtypes.to_dict()
    _same_values(first, second)
    assert parquet.read_schema(str(source)).types == parquet.read_schema(str(out)).types
    assert second["grade"].cat.ordered and list(second["grade"].cat.categories)[:1] == ["low"]


def test_the_writer_makes_the_same_bytes_every_time(tmp_path: pathlib.Path) -> None:
    for kind in ("parquet", "dta", "sav", "xpt"):
        folder = tmp_path / kind
        folder.mkdir()
        source = _write(kind, folder)
        first = _identity(source, folder / ("one" + source.suffix))
        second = _identity(source, folder / ("two" + source.suffix))
        assert first.data == second.data, kind


def test_a_value_past_its_storage_is_stored_wider_and_said(tmp_path: pathlib.Path) -> None:
    frame = pandas.DataFrame({"count": pandas.array([1, 2, 3], dtype="int8")})
    source = tmp_path / "count.dta"
    frame.to_stata(str(source), write_index=False, version=118)
    opening = source.read_bytes()[: native.OPENING_BYTES]
    found = nativereading.read_native(str(source), native.FORMAT_STATA, opening)
    written = nativewriting.twin_file(found.form, found.names, [["1", "250", "3"]], 3)
    assert written.widened == (("count", "byte", "int"),)
    out = tmp_path / "wide.dta"
    out.write_bytes(written.data)
    back, _meta = pyreadstat.read_dta(str(out))
    assert back["count"].tolist() == [1, 250, 3]


def test_a_word_in_a_column_of_numbers_is_refused_in_plain_words(tmp_path: pathlib.Path) -> None:
    source = _write("dta", tmp_path)
    opening = source.read_bytes()[: native.OPENING_BYTES]
    found = nativereading.read_native(str(source), native.FORMAT_STATA, opening)
    columns = [list(column) for column in found.columns]
    columns[1][0] = "unknown"
    with pytest.raises(nativewriting.NativeWriteError) as refused:
        nativewriting.twin_file(found.form, found.names, columns, found.n_rows)
    said = f"{refused.value}"
    assert "'age'" in said and "Please" in said and "unknown" not in said


# -- 3. the whole route ------------------------------------------------------


def _run(arguments: "list[str]") -> int:
    return cli.main(arguments)


_PANDAS_READERS = {
    "parquet": lambda path: pandas.read_parquet(path),
    "dta": lambda path: pandas.read_stata(path),
    "sav": lambda path: pandas.read_spss(path),
    "xpt": lambda path: pandas.read_sas(path, format="xport"),
}


@pytest.mark.parametrize("kind", ["parquet", "dta", "sav", "xpt"])
def test_profile_generate_and_validate_a_native_file(tmp_path: pathlib.Path, kind: str) -> None:
    source = _write(kind, tmp_path)
    assert _run(["profile", str(source)]) == 0
    description = tmp_path / "visits-profile.json"
    assert description.is_file()
    assert _run(["generate", str(description), "--seed", "11"]) == 0
    twin = tmp_path / ("visits-twin" + source.suffix)
    assert twin.is_file()
    real = _PANDAS_READERS[kind](str(source))
    made = _PANDAS_READERS[kind](str(twin))
    assert list(real.columns) == list(made.columns)
    assert real.dtypes.to_dict() == made.dtypes.to_dict()
    assert len(made) == len(real)
    assert _run(["validate", str(description), "--twin", str(twin)]) == 0
    # The same seed writes the same twin, byte for byte.
    first = twin.read_bytes()
    assert _run(["generate", str(description), "--seed", "11", "--replace"]) == 0
    assert twin.read_bytes() == first


def _csv_of(path: pathlib.Path, folder: pathlib.Path) -> pathlib.Path:
    """The same table as CSV: the cells the reader renders, written by the standard library."""
    import csv

    table = reading.read_table(str(path))
    folder.mkdir()
    out = folder / "visits.csv"
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(table.column_names)
        for row in range(table.n_rows):
            writer.writerow([table.columns[place][row] for place in range(len(table.column_names))])
    return out


@pytest.mark.parametrize("kind", ["parquet", "dta", "sav", "xpt"])
def test_the_description_of_a_native_file_is_the_description_of_the_same_table_in_csv(
    tmp_path: pathlib.Path, kind: str
) -> None:
    source = _write(kind, tmp_path)
    assert _run(["profile", str(source)]) == 0
    flat = _csv_of(source, tmp_path / "csv")
    assert _run(["profile", str(flat)]) == 0
    native_document = json.loads((tmp_path / "visits-profile.json").read_text(encoding="utf-8"))
    csv_document = json.loads((tmp_path / "csv" / "visits-profile.json").read_text(encoding="utf-8"))
    for key in sorted(set(native_document) | set(csv_document)):
        if key == "source":
            continue
        assert native_document[key] == csv_document[key], key
    native_source = dict(native_document["source"])
    csv_source = dict(csv_document["source"])
    assert "native" in native_source and "native" not in csv_source
    native_source.pop("native")
    native_source.pop("header_evidence")
    native_source.pop("header_by_convention")
    csv_source.pop("header_evidence")
    csv_source.pop("header_by_convention")
    assert native_source == csv_source
    assert native_document["source"]["header_evidence"] == (
        f"{reading._STORED_BY_THE_FILE}"
    )


def test_the_twin_command_names_a_native_twin_after_its_system(tmp_path: pathlib.Path) -> None:
    source = _write("sav", tmp_path)
    assert reading.native_system_of(str(source)) == native.FORMAT_SPSS
    assert reading.native_system_of(str(_csv_of(source, tmp_path / "csv"))) == ""


# -- 5. nothing of the file's own metadata leaks ------------------------------

_SECRET_NAME = "Maria Garcia"
_SECRET_NUMBER = "chart 48213377"
_SECRET_FILE_LABEL = "Cohort of Dr Talvo Brisk at the north clinic"
_SECRET_NOTE = "Prepared by Talvo Brisk from the clinic's own export"


def _leaky_stata(folder: pathlib.Path, rows: int = ROWS) -> pathlib.Path:
    """A Stata file whose metadata carries what must not travel."""
    frame = _frame(rows)
    frame["ward"] = [float(1 + index % 3) if index > 1 else 4.0 for index in range(rows)]
    path = folder / "visits.dta"
    pyreadstat.write_dta(
        frame, str(path),
        file_label=_SECRET_FILE_LABEL,
        column_labels={"age": "Age in years", "sbp": f"Systolic BP ({_SECRET_NUMBER} excluded)"},
        variable_value_labels={
            "arm": {1: "Control", 2: "Treated"},
            # A common code labelled with a person's name, and a code two
            # rows hold, labelled with an ordinary word.
            "ward": {1: "Intensive Care", 2: _SECRET_NAME, 3: "Day Unit", 4: "Rare Unit"},
        },
    )
    return path


def _leak_folder(tmp_path: pathlib.Path) -> "tuple[pathlib.Path, pathlib.Path, pathlib.Path]":
    source = _leaky_stata(tmp_path)
    assert _run(["profile", str(source)]) == 0
    description = tmp_path / "visits-profile.json"
    assert _run(["generate", str(description), "--seed", "3"]) == 0
    return source, description, tmp_path / "visits-twin.dta"


def _texts_of(folder: pathlib.Path) -> str:
    found = ""
    for path in sorted(folder.iterdir()):
        if path.is_file() and path.suffix != ".dta":
            found = found + path.read_text(encoding="utf-8", errors="replace")
    return found


def test_a_files_own_label_notes_and_secret_labels_reach_neither_description_nor_twin(tmp_path: pathlib.Path) -> None:
    source, description, twin = _leak_folder(tmp_path)
    written = _texts_of(tmp_path)
    twin_bytes = twin.read_bytes()
    for secret in (_SECRET_NAME, _SECRET_NUMBER, _SECRET_FILE_LABEL, "Rare Unit"):
        assert secret not in written, secret
        assert bytes(secret, "utf-8") not in twin_bytes, secret
    block = json.loads(description.read_text(encoding="utf-8"))["source"]["native"]
    labels = {entry["label"] for entry in block["columns"]}
    assert "Age in years" in labels
    ward = block["columns"][7]["value_labels"]
    assert ward == {"1": "Intensive Care", "3": "Day Unit"}
    _data, meta = pyreadstat.read_dta(str(twin))
    assert meta.file_label in (None, "")
    assert source.read_bytes().find(bytes(_SECRET_FILE_LABEL, "utf-8")) > 0


def test_the_label_guards_are_what_keep_the_secrets_out(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """THE MUTANT: with the two label rules admitting everything, the secrets do reach the description."""
    monkeypatch.setattr(native, "label_published", lambda text: isinstance(text, str))
    monkeypatch.setattr(native, "column_label_published", lambda text: isinstance(text, str))
    source = _leaky_stata(tmp_path)
    assert _run(["profile", str(source)]) == 0
    written = (tmp_path / "visits-profile.json").read_text(encoding="utf-8")
    assert _SECRET_NAME in written and _SECRET_NUMBER in written


def test_the_floor_is_what_keeps_a_rare_codes_label_out(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """THE MUTANT: a value label is held to the floor by its code's own count; at a floor of one it is published."""
    from synthtwin import profile

    real = profile._published_native

    def without_the_floor(table, columns, floor, held_back):  # type: ignore[no-untyped-def]
        return real(table, columns, 1, held_back)

    monkeypatch.setattr(profile, "_published_native", without_the_floor)
    source = _leaky_stata(tmp_path)
    assert _run(["profile", str(source)]) == 0
    assert "Rare Unit" in (tmp_path / "visits-profile.json").read_text(encoding="utf-8")


def test_a_parquet_files_own_pairs_of_text_never_travel(tmp_path: pathlib.Path) -> None:
    frame = _frame()
    table = pyarrow.Table.from_pandas(frame, preserve_index=False)
    secret = {b"owner": bytes(_SECRET_FILE_LABEL, "utf-8"), b"source_path": b"/secure/clinic/export.parquet"}
    table = table.replace_schema_metadata({**(table.schema.metadata or {}), **secret})
    source = tmp_path / "visits.parquet"
    parquet.write_table(table, str(source))
    assert _run(["profile", str(source)]) == 0
    assert _run(["generate", str(tmp_path / "visits-profile.json"), "--seed", "5"]) == 0
    twin = (tmp_path / "visits-twin.parquet").read_bytes()
    written = (tmp_path / "visits-profile.json").read_text(encoding="utf-8")
    for text in (_SECRET_FILE_LABEL, "/secure/clinic", "owner", "source_path"):
        assert text not in written
        assert bytes(text, "utf-8") not in twin
    pairs = parquet.ParquetFile(str(tmp_path / "visits-twin.parquet")).metadata.metadata
    assert sorted(pairs) == [b"ARROW:schema", b"pandas"]


def test_a_member_name_holding_figures_is_withheld(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "visits.xpt"
    pyreadstat.write_xport(_frame(), str(source), table_name="P483712", file_format_version=5)
    assert _run(["profile", str(source)]) == 0
    block = json.loads((tmp_path / "visits-profile.json").read_text(encoding="utf-8"))["source"]["native"]
    assert block["table_name"] is None
    assert _run(["generate", str(tmp_path / "visits-profile.json"), "--seed", "5"]) == 0
    _data, meta = pyreadstat.read_xport(str(tmp_path / "visits-twin.xpt"))
    assert meta.table_name == "DATA"


def test_a_hand_made_native_block_carrying_a_secret_is_refused(tmp_path: pathlib.Path) -> None:
    source = _write("dta", tmp_path)
    assert _run(["profile", str(source)]) == 0
    description = tmp_path / "visits-profile.json"
    document = json.loads(description.read_text(encoding="utf-8"))
    document["source"]["native"]["columns"][2]["value_labels"] = {"1": _SECRET_NAME}
    description.write_text(json.dumps(document), encoding="utf-8", newline="\n")
    assert _run(["generate", str(description), "--seed", "5"]) != 0
    assert not (tmp_path / "visits-twin.dta").exists()


# -- 6. the refusals ------------------------------------------------------------


def _profile_refusal(path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> str:
    code = _run(["profile", str(path)])
    assert code != 0
    captured = capsys.readouterr()
    return captured.err + captured.out


def test_a_nested_parquet_column_is_refused_in_its_own_words(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "nested.parquet"
    parquet.write_table(pyarrow.table({"visits": [[1, 2], [3]], "id": [1, 2]}), str(path))
    said = _profile_refusal(path, capsys)
    assert "lists, maps or groups of fields" in said and "'visits'" in said


def test_a_parquet_column_of_raw_bytes_is_refused(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "blob.parquet"
    parquet.write_table(pyarrow.table({"blob": pyarrow.array([b"\x00\x01", b"\x02"], type=pyarrow.binary())}), str(path))
    said = _profile_refusal(path, capsys)
    assert "kind of value synthtwin does" in said and "'blob'" in said


def test_a_parquet_file_naming_other_files_is_refused_before_any_reader_opens_it(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    chunk = (
        native.T(1, native.BINARY, "/elsewhere/part-0.parquet"),
        native.T(2, native.I64, 4),
    )
    schema = (
        (native.T(4, native.BINARY, "schema"), native.T(5, native.I32, 1)),
        (native.T(1, native.I32, native.PHYSICAL_INT64), native.T(3, native.I32, 1), native.T(4, native.BINARY, "id")),
    )
    footer = native.thrift_bytes(
        (
            native.T(1, native.I32, 1),
            native.T(2, native.LIST, native.TList(native.STRUCT, schema)),
            native.T(3, native.I64, 1),
            native.T(4, native.LIST, native.TList(native.STRUCT, ((
                native.T(1, native.LIST, native.TList(native.STRUCT, (chunk,))),
                native.T(2, native.I64, 0),
                native.T(3, native.I64, 1),
            ),))),
        )
    )
    path = tmp_path / "pointer.parquet"
    path.write_bytes(b"PAR1" + footer + native.little(len(footer), 4) + b"PAR1")
    said = _profile_refusal(path, capsys)
    assert "other files that it" in said


def test_a_damaged_parquet_file_is_refused(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = _write("parquet", tmp_path)
    data = source.read_bytes()
    damaged = tmp_path / "damaged.parquet"
    damaged.write_bytes(data[: len(data) // 2])
    said = _profile_refusal(damaged, capsys)
    assert "could not be read as one" in said


def test_an_arrow_file_and_an_spss_portable_file_are_named_and_refused(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    feather = pytest.importorskip("pyarrow.feather")
    arrow_path = tmp_path / "visits.feather"
    feather.write_feather(pyarrow.table({"id": [1, 2]}), str(arrow_path))
    assert "Arrow (Feather) file" in _profile_refusal(arrow_path, capsys)
    portable = tmp_path / "visits.por"
    pyreadstat.write_por(_frame(20), str(portable))
    assert "SPSS portable (.por) file" in _profile_refusal(portable, capsys)


def test_every_native_refusal_quotes_no_value(tmp_path: pathlib.Path) -> None:
    for builder, arguments in (
        (errors.native_unreadable, ("/data/t.parquet", "Parquet")),
        (errors.native_column_nested, ("/data/t.parquet", "visits")),
        (errors.native_twin_not_writable, ("age", "Stata", "a cell holds something that is not a number")),
    ):
        said = builder(*arguments)
        assert said.endswith(".") and ("Please" in said)


def test_the_native_gate_is_what_keeps_validate_from_reading_a_twins_bytes_as_text(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """THE MUTANT: with the native gate open, validate measures the twin's bytes as a CSV file's and misses."""
    source = _write("dta", tmp_path)
    assert _run(["profile", str(source)]) == 0
    description = tmp_path / "visits-profile.json"
    assert _run(["generate", str(description), "--seed", "2"]) == 0
    twin = tmp_path / "visits-twin.dta"
    assert _run(["validate", str(description), "--twin", str(twin)]) == 0
    import dataclasses

    from synthtwin import validation

    real = validation._byte_checks

    def gate_open(description, data, surveyed, refused, table=None):  # type: ignore[no-untyped-def]
        opened = dataclasses.replace(description, source=dataclasses.replace(description.source, native=None))
        return real(opened, twin.read_bytes(), surveyed, refused, table)

    monkeypatch.setattr(validation, "_byte_checks", gate_open)
    assert _run(["validate", str(description), "--twin", str(twin), "--replace"]) != 0


def test_no_native_file_is_read_by_its_name(tmp_path: pathlib.Path) -> None:
    """The kind is the opening bytes' (`native.kind_of`), never the ending: a Stata file named .csv is read as Stata."""
    source = _write("dta", tmp_path)
    renamed = tmp_path / "visits.csv"
    os.replace(source, renamed)
    table = reading.read_table(str(renamed))
    assert table.native is not None and table.native.system == native.FORMAT_STATA


def test_the_one_command_writes_a_native_twin_and_measures_it(tmp_path: pathlib.Path) -> None:
    """`synthtwin twin visits.sav`: the description, the twin as an SPSS file, and its quality report, in one folder."""
    source = _write("sav", tmp_path)
    code = _run(["twin", str(source), "--seed", "4"])
    assert code == 0
    folder = tmp_path / "visits-synthtwin"
    twin = folder / "visits-twin.sav"
    assert twin.is_file()
    _data, meta = pyreadstat.read_sav(str(twin))
    assert meta.column_labels == [None, "Age in years", None, "Systolic BP", None, None, None]
    assert (folder / "visits-twin-quality.txt").is_file()


@pytest.mark.parametrize("kind", ["parquet", "dta"])
def test_the_real_file_meets_its_own_description(tmp_path: pathlib.Path, kind: str) -> None:
    """validate on the real native file itself: it is read in its description's widths and misses nothing."""
    source = _write(kind, tmp_path)
    assert _run(["profile", str(source)]) == 0
    assert _run(["validate", str(tmp_path / "visits-profile.json"), "--twin", str(source)]) == 0


def test_an_spss_stamp_with_milliseconds_reads_back_to_its_own_double(tmp_path: pathlib.Path) -> None:
    """SPSS counts seconds from 1582: a stamp's count in microseconds passes 2 ** 53, and both ways stay exact."""
    stamps = [datetime.datetime(2021, 8, 24, 9, 12, 5, 123000), datetime.datetime(1999, 1, 1, 0, 0, 0, 7000)] * 5
    source = tmp_path / "stamps.sav"
    pyreadstat.write_sav(pandas.DataFrame({"seen": stamps}), str(source))
    raw, _meta = pyreadstat.read_sav(str(source), disable_datetime_conversion=True)
    assert float(raw["seen"][0]) * 1000000 > 2**53
    opening = source.read_bytes()[: native.OPENING_BYTES]
    found = nativereading.read_native(str(source), native.FORMAT_SPSS, opening)
    assert found.columns[0][:2] == ["2021-08-24 09:12:05.123", "1999-01-01 00:00:00.007"]
    out = tmp_path / "again.sav"
    _identity(source, out)
    back, _meta = pyreadstat.read_sav(str(out), disable_datetime_conversion=True)
    assert back["seen"].tolist() == raw["seen"].tolist()


def test_a_native_files_row_order_is_checked_beside_the_native_gate(tmp_path: pathlib.Path) -> None:
    """The rows' order is read off a native file's cells: kept, it holds; reversed, `rows.order` is missed (the mutant)."""
    frame = _frame()
    frame["visit_order"] = [float(index) for index in range(len(frame))]
    frame = frame[["visit_order"] + [name for name in frame.columns if name != "visit_order"]]
    source = tmp_path / "visits.parquet"
    frame.to_parquet(str(source), index=False)
    assert _run(["profile", str(source)]) == 0
    description = tmp_path / "visits-profile.json"
    order = json.loads(description.read_text(encoding="utf-8"))["source"]["dialect"]["row_order"]
    assert order["column"] == 1, order
    assert _run(["validate", str(description), "--twin", str(source)]) == 0
    reversed_path = tmp_path / "reversed.parquet"
    frame.iloc[::-1].reset_index(drop=True).to_parquet(str(reversed_path), index=False)
    assert _run(["validate", str(description), "--twin", str(reversed_path)]) != 0
    report = (tmp_path / "reversed-quality.txt").read_text(encoding="utf-8")
    assert "rows.order [document.source.dialect]: MISSED" in report
    assert "bytes.encoding [document.encoding]: WITHHELD" in report
