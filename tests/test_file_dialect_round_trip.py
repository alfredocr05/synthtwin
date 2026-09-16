"""Plan P4-D75's gate: the twin is written the way its source file was.

The owner ruling of 2026-09-15 reads "Twin should always write anything
as the original source, without changes", and the audit of commit
53bb012 measured what that asked for: a semicolon file read as one
column of free text, CRLF and Latin-1 and byte-order-marked files
written back as LF UTF-8, quoted fields written bare, a missing final
newline added, blank lines and a sorted row order dropped, and index
columns, blank or repeated names, trailing delimiters, preambles and
short rows refused.

So every shape below is a file a real exporter writes -- Excel, R,
pandas, SAS, REDCap, Qualtrics, a European semicolon export and the
rest -- built by seeded neutral code at runtime (plan D13). Each is
described, a twin is built from the description, and then:

* the twin's own BYTES are asked the question the shape is about: its
  delimiter, quoting, line endings, mark, encoding, final newline,
  blank lines, index column, row order;
* the twin is DESCRIBED AGAIN and its written form must be the one the
  description published, fact for fact;
* `synthtwin validate` exits 0 on the twin AND on the real file.

A gate that only re-described the twin could pass with a form both
sides got wrong the same way, which is why each shape also reads the
bytes directly.
"""

import csv
import io
import json
import pathlib
import random
import sys

import pytest

ROWS = 120
SITES = ("North", "South", "East", "West")


def _exit_of(argv: "list[str]") -> int:
    """Run one synthtwin command in this process and return its exit code."""
    from synthtwin import cli

    before = sys.argv
    sys.argv = ["synthtwin"] + argv
    try:
        code = cli.main()
    except SystemExit as stop:
        return 0 if stop.code is None else int(stop.code)
    finally:
        sys.argv = before
    return code


def _round_trip(
    folder: pathlib.Path,
    data: bytes,
    flags: "tuple[str, ...]" = (),
    name: str = "real.csv",
) -> "dict[str, object]":
    """Describe, build, describe the twin; validate the twin and the table."""
    folder.mkdir(parents=True, exist_ok=True)
    real = folder / name
    real.write_bytes(data)
    stem = real.stem
    assert _exit_of(
        ["profile", str(real), "--out-dir", str(folder), "--replace"] + list(flags)
    ) == 0
    described = folder / f"{stem}-profile.json"
    assert _exit_of(
        [
            "generate", str(described), "--out-dir", str(folder),
            "--seed", "4", "--replace",
        ]
    ) == 0
    twin = folder / f"{stem}-twin.csv"
    again = folder / "again"
    again.mkdir()
    copied = again / "twin.csv"
    copied.write_bytes(twin.read_bytes())
    assert _exit_of(
        ["profile", str(copied), "--out-dir", str(again), "--replace"] + list(flags)
    ) == 0
    first = json.loads(described.read_text(encoding="utf-8"))
    second = json.loads((again / "twin-profile.json").read_text(encoding="utf-8"))
    exits = {}
    for label, target in (("twin", twin), ("real", real)):
        checked = folder / f"check-{label}"
        checked.mkdir()
        exits[label] = _exit_of(
            [
                "validate", str(described), "--twin", str(target),
                "--out-dir", str(checked), "--replace",
            ]
        )
    return {
        "real": data,
        "twin": twin.read_bytes(),
        "form": first["source"]["dialect"],
        "encoding": first["source"]["encoding"],
        "twin_form": second["source"]["dialect"],
        "twin_encoding": second["source"]["encoding"],
        "names": [column["name"] for column in first["columns"]],
        "exits": exits,
    }


def _held(result: "dict[str, object]") -> None:
    """The twin carries the description's form, and both files validate."""
    assert result["twin_form"] == result["form"], (
        result["form"], result["twin_form"],
    )
    assert result["twin_encoding"] == result["encoding"]
    assert result["exits"] == {"twin": 0, "real": 0}, result["exits"]


def _people(seed: int, rows: int = ROWS) -> "list[list[str]]":
    """Rows of a neutral extract: record id, age, arm, site, a reading."""
    draw = random.Random(seed)
    found = []
    for index in range(rows):
        found += [
            [
                f"P{index + 1:04d}",
                f"{draw.randint(18, 90)}",
                draw.choice(("F", "M")),
                draw.choice(SITES),
                f"{draw.randint(900, 1900) / 10:.1f}",
            ]
        ]
    draw.shuffle(found)
    return found


def _lines(rows: "list[list[str]]", delimiter: str = ",") -> "list[str]":
    return [delimiter.join(row) for row in rows]


def _records(data: bytes, encoding: str, **options: object) -> "list[list[str]]":
    text = data.decode(encoding)
    return list(csv.reader(io.StringIO(text, newline=""), **options))


# -- Excel -------------------------------------------------------------


def test_excel_csv_utf8_on_windows(tmp_path: pathlib.Path) -> None:
    """'CSV UTF-8': a byte-order mark, CRLF, a quoted comma and line
    feed inside cells, and the delimiter-only rows Excel leaves below the
    data."""
    rows = _people(1)
    body = ["record_id,age,arm,site,reading,note"]
    draw = random.Random(11)
    for row in rows:
        note = draw.choice(('"North, annex"', "plain", '"two\nlines"'))
        body += [",".join(row) + "," + note]
    body += [",,,,,", ",,,,,"]
    data = b"\xef\xbb\xbf" + ("\r\n".join(body) + "\r\n").encode("utf-8")
    result = _round_trip(tmp_path, data)
    twin = result["twin"]
    assert twin[:3] == b"\xef\xbb\xbf"
    assert twin.count(b"\r\n") == data.count(b"\r\n")
    assert twin.endswith(b"\r\n,,,,,\r\n,,,,,\r\n")
    assert result["form"]["empty_rows"] == {
        "interior": 0, "leading": 0, "trailing": 2
    }
    _held(result)


def test_european_excel_semicolon_with_a_separator_line(
    tmp_path: pathlib.Path,
) -> None:
    """European Excel: `sep=;`, semicolons, decimal commas, CRLF and
    Windows-1252 text (the euro sign and a curly apostrophe)."""
    draw = random.Random(2)
    body = ["sep=;", "record_id;amount;site;note"]
    for index in range(ROWS):
        weight = f"{draw.randint(400, 1100) / 10:.1f}".replace(".", ",")
        note = draw.choice(("€ 20", "O’Neill", "Zürich"))
        body += [f"R{index:04d};{weight};{draw.choice(SITES)};{note}"]
    data = ("\r\n".join(body) + "\r\n").encode("cp1252")
    result = _round_trip(tmp_path, data, ("--decimal-comma", "amount"))
    twin = result["twin"]
    assert result["encoding"] == "cp1252"
    assert twin.startswith(b"sep=;\r\nrecord_id;amount;site;note\r\n")
    assert twin.count(b";") == data.count(b";")
    with pytest.raises(UnicodeDecodeError):
        twin.decode("utf-8")
    assert "€ 20" in twin.decode("cp1252")
    assert result["form"]["delimiter"] == ";"
    assert result["form"]["separator_line"] is True
    _held(result)


def test_excel_unicode_text(tmp_path: pathlib.Path) -> None:
    """Excel's 'Unicode Text': UTF-16 little-endian behind its mark, tab
    separated, CRLF."""
    rows = _people(3)
    text = "\r\n".join(["record_id\tage\tarm\tsite\treading"] + _lines(rows, "\t"))
    data = b"\xff\xfe" + (text + "\r\n").encode("utf-16-le")
    result = _round_trip(tmp_path, data, name="real.txt")
    twin = result["twin"]
    assert result["encoding"] == "utf-16-le"
    assert twin[:2] == b"\xff\xfe"
    decoded = twin[2:].decode("utf-16-le")
    assert decoded.count("\t") == text.count("\t")
    assert decoded.count("\r\n") == ROWS + 1
    _held(result)


def test_old_macintosh_excel_writes_carriage_returns(
    tmp_path: pathlib.Path,
) -> None:
    rows = _people(4)
    data = ("\r".join(["record_id,age,arm,site,reading"] + _lines(rows)) + "\r").encode()
    result = _round_trip(tmp_path, data)
    assert result["twin"].count(b"\n") == 0
    assert result["twin"].count(b"\r") == ROWS + 1
    _held(result)


# -- R -----------------------------------------------------------------


def test_r_write_csv_with_row_names(tmp_path: pathlib.Path) -> None:
    """R's write.csv default: a quoted blank first name over quoted row
    names 1..n, strings quoted, numbers and NA bare."""
    draw = random.Random(5)
    body = ['"","record_id","age","arm","site"']
    for index in range(ROWS):
        age = f"{draw.randint(18, 90)}" if draw.random() < 0.9 else "NA"
        body += [
            f'"{index + 1}","S{draw.randint(1, 99999):05d}",{age},'
            f'"{draw.choice(("F", "M"))}","{draw.choice(SITES)}"'
        ]
    data = ("\n".join(body) + "\n").encode()
    result = _round_trip(tmp_path, data)
    twin = result["twin"]
    records = _records(twin, "utf-8")
    assert records[0][0] == ""
    assert [row[0] for row in records[1:]] == [f"{n}" for n in range(1, ROWS + 1)]
    assert twin.split(b"\n")[0] == b'"","record_id","age","arm","site"'
    for line in twin.split(b"\n")[1:-1]:
        cells = line.split(b",")
        assert cells[0][:1] == b'"' and cells[1][:1] == b'"'
        assert cells[2][:1] != b'"'
    assert result["names"][0] == "Unnamed: 0"
    assert result["form"]["columns"][0]["sequence_start"] == 1
    _held(result)


# -- pandas ------------------------------------------------------------


def test_pandas_to_csv_with_its_index(tmp_path: pathlib.Path) -> None:
    """pandas' to_csv default: a blank first name over the index 0..n-1."""
    rows = _people(6)
    body = [",record_id,age,arm,site,reading"]
    body += [f"{index}," + ",".join(row) for index, row in enumerate(rows)]
    data = ("\n".join(body) + "\n").encode()
    result = _round_trip(tmp_path, data)
    records = _records(result["twin"], "utf-8")
    assert records[0][0] == ""
    assert [row[0] for row in records[1:]] == [f"{n}" for n in range(ROWS)]
    _held(result)


def test_a_named_index_keeps_its_sequence(tmp_path: pathlib.Path) -> None:
    """A frame written, read and written again: `Unnamed: 0` holding
    0..n-1, which a count role would have drawn with repeats."""
    rows = _people(7)
    body = ["Unnamed: 0,record_id,age,arm,site,reading"]
    body += [f"{index}," + ",".join(row) for index, row in enumerate(rows)]
    data = ("\n".join(body) + "\n").encode()
    result = _round_trip(tmp_path, data)
    records = _records(result["twin"], "utf-8")
    assert [row[0] for row in records[1:]] == [f"{n}" for n in range(ROWS)]
    _held(result)


def test_repeated_and_blank_header_names(tmp_path: pathlib.Path) -> None:
    draw = random.Random(8)
    body = ["record_id,value,value,"]
    for index in range(ROWS):
        body += [
            f"S{draw.randint(1, 99999):05d},{draw.randint(1, 9)},"
            f"{draw.randint(1, 9)},{draw.choice(SITES)}"
        ]
    data = ("\n".join(body) + "\n").encode()
    result = _round_trip(tmp_path, data)
    assert result["names"] == ["record_id", "value", "value.1", "Unnamed: 3"]
    assert result["twin"].split(b"\n")[0] == b"record_id,value,value,"
    _held(result)


# -- SAS, REDCap, Qualtrics ---------------------------------------------


def test_a_table_of_declared_identifier_pairs_shares_no_row_with_its_twin(
    tmp_path: pathlib.Path,
) -> None:
    """The gate under plan P4-D76: no file-level fact rebuilds a declared
    identifier, and no twin row is a real row.

    THE DEFECT THIS PINS. A sequence published of a column is written
    back by the generator as the literal cells `0, 1, 2, ...`, so a
    table whose two declared identifier columns each step by one had
    BOTH republished -- and the twin then held all 120 of the real
    table's rows, byte for byte, with every value the declaration
    exists to withhold. The written form went around the withholding.

    Two halves, because one of them cannot be checked by comparison:
    the description publishes no sequence and no order for a declared
    identifier, which is exact; and the twin of a realistic identifier
    table shares no row with the source.

    WHY THE SECOND HALF IS PINNED ON WIDE IDENTIFIERS. The generator
    NEVER READS THE REAL TABLE, so it cannot exclude a real row by
    looking: clause 2 of the twin's definition is held structurally, by
    not carrying the values across, and never by comparison. On a table
    of 120 rows whose identifiers are the integers 0..120 a stand-in
    can therefore collide with a real pair by chance -- measured at 0
    to 3 rows of 120 across twelve seeds, varying with the seed, where
    the defect above gave 120 of 120 at every seed.
    """
    rows = [(f"S{index:05d}", f"T{index * 7 % 100000:05d}") for index in range(ROWS)]
    data = ("first_id,second_id\n" + "".join(f"{a},{b}\n" for a, b in rows)).encode()
    result = _round_trip(
        tmp_path, data,
        ("--identifier", "first_id", "--identifier", "second_id",
         "--smallest-group", "10"),
    )
    form = result["form"]
    assert [column["sequence_start"] for column in form["columns"]] == [None, None]
    assert form["row_order"] is None
    twin = _records(result["twin"], "utf-8")
    assert set(tuple(row) for row in twin[1:]) & set(rows) == set()
    _held(result)


def test_a_stepping_identifier_pair_publishes_nothing_that_rebuilds_it(
    tmp_path: pathlib.Path,
) -> None:
    """The review's own table, pinned on the facts rather than on chance.

    Its identifiers are the integers 0..120, where a stand-in may
    collide with a real pair by chance, so what is asserted here is
    what the description PUBLISHES -- which is what the defect was.
    """
    data = ("first_id,second_id\n" + "".join(f"{n},{n + 1}\n" for n in range(ROWS))).encode()
    result = _round_trip(
        tmp_path, data,
        ("--identifier", "first_id", "--identifier", "second_id",
         "--smallest-group", "10"),
    )
    form = result["form"]
    assert [column["sequence_start"] for column in form["columns"]] == [None, None]
    assert form["row_order"] is None
    twin = _records(result["twin"], "utf-8")
    assert [row[0] for row in twin[1:]] != [f"{n}" for n in range(ROWS)]
    _held(result)

def test_sas_padded_latin1_export(tmp_path: pathlib.Path) -> None:
    """A PUT-style export: ids right-padded, numbers left-padded, CRLF,
    Latin-1 labels."""
    draw = random.Random(9)
    body = ["record_id ,     age,site    "]
    for index in range(ROWS):
        ident = f"{'S' + f'{index:04d}':<10}"
        site = f"{draw.choice(('Malmö', 'Zürich', 'Kraków')):<8}"
        body += [f"{ident},{draw.randint(18, 90):>8},{site}"]
    draw.shuffle(body[1:])
    data = ("\r\n".join(body) + "\r\n").encode("latin-1")
    result = _round_trip(tmp_path, data)
    twin = result["twin"]
    assert result["encoding"] == "latin-1"
    lines = twin.split(b"\r\n")[1:-1]
    assert {len(line) for line in lines} == {len(body[1].encode("latin-1"))}
    assert all(line[11:19][:1] == b" " for line in lines)
    _held(result)


def test_redcap_export_sorted_by_record_id(tmp_path: pathlib.Path) -> None:
    """REDCap: a mark, CRLF, record_id 1..n in order, checkbox columns."""
    draw = random.Random(10)
    body = ["record_id,age,arm,condition___1,condition___2"]
    for index in range(ROWS):
        body += [
            f"{index + 1},{draw.randint(18, 90)},{draw.choice(('1', '2'))},"
            f"{draw.choice(('Checked', 'Unchecked'))},"
            f"{draw.choice(('Checked', 'Unchecked'))}"
        ]
    data = b"\xef\xbb\xbf" + ("\r\n".join(body) + "\r\n").encode()
    result = _round_trip(tmp_path, data)
    # `record_id` IS NOT A WRITTEN ROW INDEX (plan P4-D76). It is the
    # table's own first column, named by whoever built the export, and
    # until this landing its 1..n was published as the row sequence --
    # which told the generator to write those very values back. A
    # register's serial is exactly what a person declares with
    # `--identifier`, so publishing it was a disclosure and not a form.
    # Only the first column NAMED as pandas and R name theirs keeps a
    # sequence; the two tests above pin that half.
    assert result["form"]["columns"][0]["sequence_start"] is None
    _held(result)


def test_a_table_sorted_by_its_record_code_stays_sorted(
    tmp_path: pathlib.Path,
) -> None:
    rows = sorted(_people(12), key=lambda row: row[3])
    data = ("\n".join(["record_id,age,arm,site,reading"] + _lines(rows)) + "\n").encode()
    result = _round_trip(tmp_path, data)
    sites = [row[3] for row in _records(result["twin"], "utf-8")[1:]]
    assert sites == sorted(sites)
    assert result["form"]["row_order"]["column"] == 4
    _held(result)


def test_a_sort_column_holding_a_cell_of_spaces_publishes_no_order(
    tmp_path: pathlib.Path,
) -> None:
    """The survey reads the order off written cells, and a cell of spaces
    is written; the column's description counts that cell absent, and the
    twin writes it empty, which no published order could hold (contract
    FD7). The order is dropped, the description loads, and both files
    validate."""
    rows = sorted(_people(22), key=lambda row: row[0])
    rows[0] = ["   "] + rows[0][1:]
    data = ("\n".join(["record_id,age,arm,site,reading"] + _lines(rows)) + "\n").encode()
    result = _round_trip(tmp_path, data)
    assert result["form"]["row_order"] is None
    _held(result)


def test_qualtrics_metadata_rows(tmp_path: pathlib.Path) -> None:
    draw = random.Random(13)
    body = [
        "ResponseId,Q1_age,Q2_site",
        '"Response ID","How old are you?","Which site, main?"',
        '"{""ImportId"":""_recordId""}","{""ImportId"":""QID1_TEXT""}",'
        '"{""ImportId"":""QID2""}"',
    ]
    for index in range(ROWS):
        body += [f"R_{draw.randint(10**9, 10**10)},{draw.randint(18, 90)},{draw.choice(SITES)}"]
    data = b"\xef\xbb\xbf" + ("\r\n".join(body) + "\r\n").encode()

    # UNDECLARED, THE ROWS ARE THE TABLE'S (plan P4-D81, review item
    # CODEX-2). synthtwin sees the shape and does not act on it: both
    # rows are counted, described and twinned as records.
    plain = _round_trip(tmp_path / "undeclared", data)
    # Nothing leaves the table and nothing is published as schema: both
    # rows are records of the table, and they are counted.
    assert plain["form"]["header_rows"] == []
    assert plain["exits"]["real"] == 0, plain["exits"]

    # THE WRITTEN FORM COMES BACK, save one published fact that this
    # version says it does not keep. With the marker row left among the
    # records, the first column's cells are quoted in no single way --
    # `mixed` -- and a `mixed` column is written `needed` by design,
    # which the report states. Every other fact of the form is equal.
    assert plain["form"]["columns"][0]["quoting"]["text"] == "mixed"
    assert plain["twin_form"]["columns"][0]["quoting"]["text"] == "needed"
    asked = json.loads(json.dumps(plain["form"]))
    found = json.loads(json.dumps(plain["twin_form"]))
    asked["columns"][0]["quoting"]["text"] = "settled"
    found["columns"][0]["quoting"]["text"] = "settled"
    assert found == asked, (asked, found)

    # The twin of THIS shape misses one obligation, and it is not a
    # fact of the file's written form: `ResponseId` is read as free
    # text once those two rows rejoin its column, and the generator's
    # free-text lengths miss the published mean. Measured at this
    # landing (`free_text.length.mean`, one miss); it is a limit of how
    # free text is built, and it is named rather than asserted away.

    # DECLARED, THEY ARE THE COLUMNS' DESCRIPTIONS and are written back
    # unchanged, which is what the declaration is for.
    result = _round_trip(
        tmp_path / "declared", data, ("--metadata-rows", "2")
    )
    lines = result["twin"].split(b"\r\n")
    assert lines[1] == body[1].encode()
    assert lines[2] == body[2].encode()
    _held(result)


def test_a_guess_never_publishes_a_record_as_schema(
    tmp_path: pathlib.Path,
) -> None:
    """A row that a guess reads as export metadata is NOT taken out of
    the table and NOT published verbatim (plan P4-D81).

    THE REPRODUCTION THIS IS BUILT FROM (review item CODEX-2). Two rows
    under the names -- a person's own record, then a row of ImportId
    markers -- were recognised as a survey export's column
    descriptions. The description then counted 120 records rather than
    122 and published BOTH rows verbatim under
    `source.dialect.header_rows`, so `Person-ZETA-739` and
    `private-result-739` stood in the description and in the twin. The
    twin definition's third clause says the description reveals nothing
    about any individual, and a guess about a file's shape may not
    decide that it does.
    """
    body = [
        "person,result",
        "Person-ZETA-739,private-result-739",
        '"{""ImportId"":""person""}","{""ImportId"":""result""}"',
    ]
    for index in range(ROWS):
        body += [f"{SITES[index % 4]},{'A' if index % 2 else 'B'}"]
    data = ("\n".join(body) + "\n").encode()

    # NOTHING IS TAKEN OUT OF THE TABLE AND NOTHING IS PUBLISHED AS
    # SCHEMA. Both rows are counted: 122, not 120.
    result = _round_trip(tmp_path / "guessed", data)
    assert result["form"]["header_rows"] == []
    described = json.loads(
        (tmp_path / "guessed" / "real-profile.json").read_text(
            encoding="utf-8"
        )
    )
    assert described["n_rows"] == ROWS + 2, described["n_rows"]

    # AND BECAUSE THE ROW IS DATA, THE SMALLEST GROUP NOW GOVERNS IT.
    # That is the whole of the repair. Published as schema the row was
    # floor-EXEMPT: `header_rows` carried it whole at every floor, and
    # the twin wrote it back. As data it is a level of one row, so a
    # floor above one holds it back like any other.
    raised = _round_trip(
        tmp_path / "floored", data, ("--smallest-group", "10")
    )
    assert raised["form"]["header_rows"] == []
    assert b"Person-ZETA-739" not in raised["twin"]
    assert b"private-result-739" not in raised["twin"]
    lifted = json.loads(
        (tmp_path / "floored" / "real-profile.json").read_text(
            encoding="utf-8"
        )
    )
    assert lifted["n_rows"] == ROWS + 2
    assert "Person-ZETA-739" not in json.dumps(lifted)
    assert "private-result-739" not in json.dumps(lifted)


# -- other writers ---------------------------------------------------------


def test_python_csv_on_windows_quote_nonnumeric(tmp_path: pathlib.Path) -> None:
    """csv.writer in text mode on Windows writes \\r\\r\\n, and
    QUOTE_NONNUMERIC quotes a text code inside a numeric column."""
    draw = random.Random(14)
    body = ['"record_id","sbp","site"']
    for index in range(ROWS):
        sbp = f"{draw.randint(90, 180)}" if draw.random() < 0.9 else '"ND"'
        body += [f'"S{draw.randint(1, 99999):05d}",{sbp},"{draw.choice(SITES)}"']
    data = ("\r\r\n".join(body) + "\r\r\n").encode()
    result = _round_trip(tmp_path, data)
    twin = result["twin"]
    assert twin.count(b"\r\r\n") == ROWS + 1
    assert result["form"]["line_endings"] == [{"ending": "crcrlf", "lines": ROWS + 1}]
    if b"ND" in twin:
        assert b',"ND",' in twin
    _held(result)


def test_backslash_escaped_quotes(tmp_path: pathlib.Path) -> None:
    """A database export writing `\\"` inside quoted fields."""
    draw = random.Random(15)
    body = ["record_id\tlabel"]
    for index in range(ROWS):
        body += [f'S{draw.randint(1, 99999):05d}\t"Fall \\"{draw.choice(SITES)}\\""']
    data = ("\n".join(body) + "\n").encode()
    result = _round_trip(tmp_path, data)
    assert result["form"]["escape"] == "backslash"
    labels = [
        row[1]
        for row in _records(
            result["twin"], "utf-8", delimiter="\t", escapechar="\\", doublequote=False
        )[1:]
    ]
    assert all(label[:6] == 'Fall "' for label in labels), labels[:3]
    _held(result)


def test_comma_space_and_an_unquoted_inner_quote(tmp_path: pathlib.Path) -> None:
    draw = random.Random(16)
    body = ['"record_id", "age", "size"']
    for index in range(ROWS):
        body += [f'"S{draw.randint(1, 99999):05d}", {draw.randint(18, 90)}, "{draw.randint(1, 9)} wide"']
    data = ("\n".join(body) + "\n").encode()
    result = _round_trip(tmp_path, data)
    assert result["form"]["initial_space"] is True
    assert result["twin"].count(b", ") == data.count(b", ")
    _held(result)

    bare = ["record_id,size"]
    for index in range(ROWS):
        bare += [f'S{draw.randint(1, 99999):05d},Cyst {draw.randint(1, 9)}" wide']
    second = _round_trip(tmp_path / "bare", ("\n".join(bare) + "\n").encode())
    assert second["twin"].count(b'"') == second["real"].count(b'"')
    _held(second)


def test_a_hand_edited_file(tmp_path: pathlib.Path) -> None:
    """A title line, a comment, blank lines between and after the rows, a
    line of spaces, and no newline at the end."""
    rows = _people(17)
    text = "Report: cohort extract\n# exported by a tool\n"
    text += "\n".join(["record_id,age,arm,site,reading"] + _lines(rows[:40]))
    text += "\n\n   \n" + "\n".join(_lines(rows[40:])) + "\n\n"
    text = text.rstrip("\n")
    data = text.encode()
    result = _round_trip(tmp_path, data)
    twin = result["twin"]
    assert not twin.endswith(b"\n")
    lines = twin.split(b"\n")
    # NEITHER LINE'S TEXT IS IN THE TWIN (plan P4-D80, review item
    # CODEX-3). Each is written as a neutral line of its own shape: the
    # title line as two words, the comment keeping the mark that makes
    # a reader skip it.
    assert lines[0] == b"withheld line"
    assert lines[1] == b"# withheld line"
    assert b"Report: cohort extract" not in twin
    assert b"exported by a tool" not in twin
    assert lines[43] == b"" and lines[44] == b"   "
    assert result["form"]["final_line_ending"] is False
    _held(result)


def test_a_preamble_is_withheld_at_every_floor(
    tmp_path: pathlib.Path,
) -> None:
    """A line before the names publishes its SHAPE and never its text --
    at the DEFAULT floor of one as much as above it (plan P4-D80).

    THE REPRODUCTION THIS IS BUILT FROM (review item CODEX-3). At the
    default floor `Extract for unit 7` stood in the description under
    `source.dialect.preamble` and on the twin's own first line, because
    the rule held the text back only above a floor of one. A floor
    counts rows that share a value; one line of prose is not a group of
    rows, so it never protected this at all.
    """
    rows = _people(18)
    text = "Extract for unit 7\n" + "\n".join(["record_id,age,arm,site,reading"] + _lines(rows)) + "\n"
    for floor in ("1", "11"):
        result = _round_trip(
            tmp_path / f"floor-{floor}", text.encode(),
            ("--smallest-group", floor),
        )
        assert result["form"]["preamble"] == [
            {"kind": "text", "lines": 1, "mark": ""}
        ], result["form"]["preamble"]
        assert result["form"]["preamble_withheld"] is True
        assert result["twin"].split(b"\n")[0] == b"withheld line"
        assert b"Extract for unit 7" not in result["twin"]
        _held(result)


def test_seventeen_leading_blank_lines_are_one_run(
    tmp_path: pathlib.Path,
) -> None:
    """Leading blank lines are published as ONE RUN, so a file the
    baseline read is not refused by its own description (review item
    CODEX-11).

    THE REPRODUCTION. Seventeen blank lines above the header profiled at
    exit 0 and published seventeen preamble entries; the loader refused
    that document against FD11's cap of sixteen, so `generate` exited 1
    on a description synthtwin had just written. Sixteen worked.
    """
    rows = _people(23)
    body = "\n".join(["record_id,age,arm,site,reading"] + _lines(rows)) + "\n"
    for count in (16, 17, 40):
        result = _round_trip(
            tmp_path / f"blank-{count}", ("\n" * count + body).encode()
        )
        assert result["form"]["preamble"] == [
            {"kind": "blank", "lines": count, "mark": ""}
        ], result["form"]["preamble"]
        assert result["form"]["preamble_withheld"] is False
        assert result["twin"].split(b"\n")[:count] == [b""] * count
        _held(result)


def test_sql_rows_leave_out_trailing_empty_cells(tmp_path: pathlib.Path) -> None:
    draw = random.Random(19)
    body = ["record_id|age|site|note"]
    for index in range(ROWS):
        row = [f"S{draw.randint(1, 99999):05d}", f"{draw.randint(18, 90)}", draw.choice(SITES), "seen"]
        if draw.random() < 0.3:
            row = row[:3]
        body += ["|".join(row)]
    data = ("\n".join(body) + "\n").encode()
    result = _round_trip(tmp_path, data)
    assert result["form"]["short_rows"] is True
    widths = {line.count(b"|") for line in result["twin"].split(b"\n")[1:-1]}
    assert widths <= {2, 3}
    _held(result)


def test_every_line_ends_with_the_delimiter(tmp_path: pathlib.Path) -> None:
    rows = _people(20)
    data = ("\n".join([line + "," for line in ["record_id,age,arm,site,reading"] + _lines(rows)]) + "\n").encode()
    result = _round_trip(tmp_path, data)
    assert all(line.endswith(b",") for line in result["twin"].split(b"\n")[:-1])
    assert result["form"]["trailing_delimiter"] == {"header": True, "rows": True}
    _held(result)


def test_a_dos_end_of_file_mark_and_mixed_endings(tmp_path: pathlib.Path) -> None:
    rows = _people(21)
    text = "\r\n".join(["record_id,age,arm,site,reading"] + _lines(rows[:50])) + "\r\n"
    text += "\n".join(_lines(rows[50:])) + "\n\x1a"
    data = text.encode()
    result = _round_trip(tmp_path, data)
    twin = result["twin"]
    assert twin.endswith(b"\n\x1a")
    assert twin.count(b"\r\n") == 51
    assert result["form"]["line_endings"] == [
        {"ending": "crlf", "lines": 51}, {"ending": "lf", "lines": ROWS - 50},
    ]
    _held(result)


# -- the lexer is the standard reader's -----------------------------------


def test_the_survey_reads_every_record_the_standard_reader_reads() -> None:
    """480,000 comparisons were run while this was written; this keeps a
    seeded share of them in the suite, over every delimiter, both
    escapings and the skipped initial space."""
    from synthtwin import dialect

    alphabet = ["a", ",", ";", '"', "\r", "\n", " ", "\\", "\t", "|"]
    draw = random.Random(20260915)
    compared = 0
    for _trial in range(1500):
        text = "".join(draw.choice(alphabet) for _ in range(draw.randint(1, 18)))
        for delimiter in dialect.DELIMITERS:
            for escape in dialect.ESCAPES:
                for spaced in (False, True):
                    options: "dict[str, object]" = {
                        "delimiter": delimiter,
                        "skipinitialspace": spaced,
                    }
                    if escape == dialect.ESCAPE_BACKSLASH:
                        options.update(escapechar="\\", doublequote=False)
                    try:
                        expected = list(
                            csv.reader(io.StringIO(text, newline=""), **options)
                        )
                    except csv.Error:
                        continue
                    found = [
                        record.fields
                        for record in dialect.records(text, delimiter, escape, spaced)
                    ]
                    assert found == expected, (text, delimiter, escape, spaced)
                    compared += 1
    assert compared > 20000


def test_names_follow_pandas_for_blank_and_repeated_cells() -> None:
    from synthtwin import dialect

    assert dialect.named_columns(("", "a", "a", "Unnamed: 0", "a.1")) == (
        "Unnamed: 0.1", "a", "a.2", "Unnamed: 0", "a.1",
    )
    assert dialect.named_columns(("id", "  ", "id")) == ("id", "Unnamed: 1", "id.1")


# -- a rule that cannot fail is a defect ----------------------------------


def _missed(folder: pathlib.Path, described: pathlib.Path, data: bytes) -> "list[str]":
    """Validate ``data`` against a description; the subchecks it MISSED."""
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / "other.csv"
    target.write_bytes(data)
    checked = folder / "checked"
    checked.mkdir()
    code = _exit_of(
        [
            "validate", str(described), "--twin", str(target),
            "--out-dir", str(checked), "--replace",
        ]
    )
    report = (checked / "other-quality.txt").read_text(encoding="utf-8")
    found = []
    for line in report.split("\n"):
        text = line.strip()
        if text.endswith(": MISSED") and " [" in text:
            found += [text.split(" [")[0]]
    assert code == 3, report[-400:]
    return found


def _describe(folder: pathlib.Path, data: bytes, flags: "tuple[str, ...]" = ()) -> pathlib.Path:
    folder.mkdir(parents=True, exist_ok=True)
    real = folder / "real.csv"
    real.write_bytes(data)
    assert _exit_of(
        ["profile", str(real), "--out-dir", str(folder), "--replace"] + list(flags)
    ) == 0
    return folder / "real-profile.json"


def test_each_rule_of_the_written_form_can_miss(tmp_path: pathlib.Path) -> None:
    """Every rule the validator gained is shown failing on a file whose
    written form differs in that one respect, and on no other."""
    rows = _people(30)
    header = "record_id,age,arm,site,reading"
    plain = ("\n".join([header] + _lines(rows)) + "\n").encode()

    european = _describe(
        tmp_path / "semicolon",
        ("sep=;\r\n" + "\r\n".join([header.replace(",", ";")] + _lines(rows, ";")) + "\r\n").encode(),
    )
    missed = _missed(tmp_path / "semicolon-plain", european, plain)
    for rule in ("bytes.delimiter", "bytes.line-endings", "bytes.separator-line"):
        assert rule in missed, missed

    marked = _describe(tmp_path / "marked", b"\xef\xbb\xbf" + plain)
    assert "bytes.byte-order-mark" in _missed(tmp_path / "marked-plain", marked, plain)

    all_quoted = "\n".join(
        [",".join(f'"{name}"' for name in header.split(","))]
        + [",".join(f'"{cell}"' for cell in row) for row in rows]
    ) + "\n"
    every = _describe(tmp_path / "quoted", all_quoted.encode())
    missed = _missed(tmp_path / "quoted-plain", every, plain)
    assert "bytes.quoting" in missed and "bytes.header-quoting" in missed, missed

    ended = _describe(tmp_path / "unended", plain.rstrip(b"\n"))
    assert "bytes.terminal-newline" in _missed(tmp_path / "unended-plain", ended, plain)

    titled = _describe(tmp_path / "titled", b"Report of the extract\n" + plain)
    assert "bytes.preamble" in _missed(tmp_path / "titled-plain", titled, plain)

    lines = plain.split(b"\n")
    gapped = b"\n".join(lines[:10] + [b""] + lines[10:])
    spaced = _describe(tmp_path / "gapped", gapped)
    assert "bytes.blank-lines" in _missed(tmp_path / "gapped-plain", spaced, plain)

    trailing = b"\n".join([line + b"," for line in lines[:-1]]) + b"\n"
    delimited = _describe(tmp_path / "trailing", trailing)
    assert "bytes.trailing-delimiter" in _missed(tmp_path / "trailing-plain", delimited, plain)

    in_order = sorted(rows, key=lambda row: row[3])
    ordered = _describe(
        tmp_path / "ordered", ("\n".join([header] + _lines(in_order)) + "\n").encode()
    )
    assert "rows.order" in _missed(tmp_path / "ordered-plain", ordered, plain)

    indexed_text = "\n".join(
        ["," + header] + [f"{index}," + ",".join(row) for index, row in enumerate(rows)]
    ) + "\n"
    indexed = _describe(tmp_path / "indexed", indexed_text.encode())
    shuffled = "\n".join(
        ["," + header] + [f"{(index * 7) % ROWS}," + ",".join(row) for index, row in enumerate(rows)]
    ) + "\n"
    assert "rows.sequence" in _missed(tmp_path / "indexed-shuffled", indexed, shuffled.encode())

    padded_text = "\n".join(
        ["record_id ,age"] + [f"{row[0]:<10},{row[1]}" for row in rows]
    ) + "\n"
    padded = _describe(tmp_path / "padded", padded_text.encode())
    unpadded = ("\n".join(["record_id ,age"] + [f"{row[0]},{row[1]}" for row in rows]) + "\n").encode()
    assert "bytes.padding" in _missed(tmp_path / "padded-plain", padded, unpadded)

    accented = ("\n".join([header] + [",".join(row[:3] + [row[3] + "é", row[4]]) for row in rows]) + "\n")
    latin = _describe(tmp_path / "latin", accented.encode("latin-1"))
    assert "bytes.encoding" in _missed(tmp_path / "latin-utf8", latin, accented.encode("utf-8"))

    comma_space = ("\n".join([header.replace(",", ", ")] + _lines(rows, ", ")) + "\n").encode()
    spaced_out = _describe(tmp_path / "comma-space", comma_space)
    assert "bytes.initial-space" in _missed(tmp_path / "comma-space-plain", spaced_out, plain)

    def quoted_inner(escaped: str) -> bytes:
        body = [header] + [
            ",".join(row[:3] + [f'"{row[3]} {escaped}A{escaped}"', row[4]]) for row in rows
        ]
        return ("\n".join(body) + "\n").encode()

    backslashed = _describe(tmp_path / "backslash", quoted_inner('\\"'))
    assert "bytes.escape" in _missed(tmp_path / "backslash-doubled", backslashed, quoted_inner('""'))

    closed = _describe(tmp_path / "eof-mark", plain + b"\x1a")
    assert "bytes.end-of-file-mark" in _missed(tmp_path / "eof-mark-plain", closed, plain)

    surveyed_rows = [
        header,
        '"Record","Age","Arm","Site","Reading"',
        ",".join(f'"{{""ImportId"":""QID{index}""}}"' for index in range(5)),
    ]
    surveyed_text = ("\n".join(surveyed_rows + _lines(rows)) + "\n").encode()
    # THE ROWS ARE DECLARED (plan P4-D81). Undeclared they are records
    # of the table, so a description of this file would publish no rows
    # of column descriptions at all and this rule could not miss.
    metadata = _describe(
        tmp_path / "metadata", surveyed_text, ("--metadata-rows", "2")
    )
    assert "bytes.header-rows" in _missed(tmp_path / "metadata-plain", metadata, plain)
    bare_rows = [surveyed_rows[0], surveyed_rows[1].replace('"', ""), surveyed_rows[2]]
    bare_text = ("\n".join(bare_rows + _lines(rows)) + "\n").encode()
    assert "bytes.header-rows-quoting" in _missed(tmp_path / "metadata-bare", metadata, bare_text)

    repeated_header = "record_id,age,arm,site,age"
    renamed = "record_id,age,arm,site,age.1"
    repeated = _describe(
        tmp_path / "repeated", ("\n".join([repeated_header] + _lines(rows)) + "\n").encode()
    )
    assert "bytes.written-names" in _missed(
        tmp_path / "repeated-renamed", repeated, ("\n".join([renamed] + _lines(rows)) + "\n").encode()
    )

    holed = [row[:4] + ([""] if index % 3 == 0 else row[4:]) for index, row in enumerate(rows)]
    short_text = "\n".join(
        [header] + [",".join(row[:4]) if row[4] == "" else ",".join(row) for row in holed]
    ) + "\n"
    full_text = "\n".join([header] + _lines(holed)) + "\n"
    shortened = _describe(tmp_path / "short", short_text.encode())
    assert "bytes.short-rows" in _missed(tmp_path / "short-full", shortened, full_text.encode())

    emptied = [[""] * 5 if index == 7 else row for index, row in enumerate(rows)]
    nothing = _describe(
        tmp_path / "nothing", ("\n".join([header] + _lines(emptied)) + "\n").encode()
    )
    assert "bytes.empty-rows" in _missed(tmp_path / "nothing-plain", nothing, plain)


# -- the repair of this landing: shapes a skeptic found ---------------------
#
# Each test below is built from a reproduction the skeptic of landing
# 2b.9 ran against its first commit, and each failed there: a file
# 53bb012 twinned and the landing refused, a sort the landing lost beside
# Excel's empty records, a twin that failed its own description, a
# semicolon file read with the comma, and four rules no test held.


def test_a_utf8_table_with_a_stray_byte_in_an_identifier(
    tmp_path: pathlib.Path,
) -> None:
    """A UTF-8 table with one pasted Latin-1 byte, standing in an id cell.

    The table is read as Latin-1, so its accented labels are published as
    that reading gives them, and written back byte for byte. The byte
    that made it Latin-1 stood in a cell the twin writes a stand-in for,
    so the twin is valid UTF-8 -- and still exactly its description: the
    validator reads it in the published encoding and finds no character
    the description does not publish.
    """
    draw = random.Random(31)
    body = ["study_id,age,site"]
    for index in range(ROWS):
        body += [
            f"S{index + 1:05d},{draw.randint(18, 90)},"
            f"{draw.choice(('Zürich clinic', 'Malmö clinic', 'Healthy'))}"
        ]
    data = ("\n".join(body) + "\n").encode("utf-8").replace(b"S00007,", b"S0000\xe9,", 1)
    result = _round_trip(tmp_path, data, ("--identifier", "study_id"))
    assert result["encoding"] == "latin-1"
    twin = result["twin"]
    for label in ("Zürich clinic", "Malmö clinic"):
        assert twin.count(label.encode("utf-8")) == data.count(label.encode("utf-8"))
    assert result["exits"] == {"twin": 0, "real": 0}, result["exits"]
    assert result["twin_form"] == result["form"]


@pytest.mark.parametrize("between", ["", "   "], ids=["blank", "spaces"])
def test_a_double_spaced_export(tmp_path: pathlib.Path, between: str) -> None:
    """A blank line -- or a line of spaces -- after every record, in more
    places than the cap: the lines are published counted and written
    exactly where they were, and the reader's check against the standard
    reader still finds every one of them where it stands."""
    rows = _people(32)
    separator = "\n" + between + "\n"
    data = (separator.join(["record_id,age,arm,site,reading"] + _lines(rows)) + "\n").encode()
    result = _round_trip(tmp_path, data)
    assert result["form"]["blank_lines"] == []
    assert result["form"]["blank_lines_spread"] == {
        "first": 0, "last": ROWS - 1, "lines": ROWS, "text": between,
    }
    lines = result["twin"].split(b"\n")
    assert all(lines[index] == between.encode() for index in range(1, 2 * ROWS, 2))
    assert all(lines[index].strip() != b"" for index in range(0, 2 * ROWS + 1, 2))
    _held(result)


def test_line_endings_that_change_kind_past_the_cap(tmp_path: pathlib.Path) -> None:
    """Every third line ends with CRLF: eighty runs, so the endings are
    published counted and the twin ends as many lines each way."""
    rows = _people(33)
    text = "record_id,age,arm,site,reading\n"
    for index in range(ROWS):
        text += _lines([rows[index]])[0] + ("\r\n" if index % 3 == 0 else "\n")
    data = text.encode()
    result = _round_trip(tmp_path, data)
    assert result["form"]["line_endings"] == []
    assert result["form"]["line_endings_spread"] == [
        {"ending": "lf", "lines": ROWS + 1 - 40}, {"ending": "crlf", "lines": 40},
    ]
    assert result["twin"].count(b"\r\n") == data.count(b"\r\n")
    _held(result)


def test_a_sorted_excel_table_with_empty_records_below_it(
    tmp_path: pathlib.Path,
) -> None:
    """Excel CSV UTF-8 sorted by record_id with formatted-empty rows below:
    the order is read over the records that hold something and kept."""
    draw = random.Random(34)
    body = ["record_id,age,arm,site"]
    for index in range(ROWS):
        body += [f"P{index + 1:04d},{draw.randint(18, 90)},{draw.choice('AB')},{draw.choice(SITES)}"]
    body += [",,,"] * 5
    data = b"\xef\xbb\xbf" + ("\r\n".join(body) + "\r\n").encode()
    result = _round_trip(tmp_path, data)
    assert result["form"]["row_order"] == {
        "collation": "text", "column": 1, "direction": "ascending",
    }
    assert result["form"]["empty_rows"] == {"interior": 0, "leading": 0, "trailing": 5}
    records = _records(result["twin"], "utf-8-sig")
    ids = [row[0] for row in records[1 : ROWS + 1]]
    assert all(ids) and ids == sorted(ids)
    assert records[ROWS + 1 :] == [["", "", "", ""]] * 5
    _held(result)


def test_a_sorted_table_with_an_empty_record_inside(tmp_path: pathlib.Path) -> None:
    """The empty record keeps its place and the rows are sorted around it."""
    rows = sorted(_people(36), key=lambda row: row[0])
    body = ["record_id,age,arm,site,reading"] + _lines(rows[:60]) + [",,,,"] + _lines(rows[60:])
    data = ("\n".join(body) + "\n").encode()
    result = _round_trip(tmp_path, data)
    assert result["form"]["row_order"]["column"] == 1
    assert result["form"]["empty_rows"] == {"interior": 1, "leading": 0, "trailing": 0}
    records = _records(result["twin"], "utf-8")[1:]
    assert records[60] == ["", "", "", "", ""]
    ids = [row[0] for row in records if row[0]]
    assert len(ids) == ROWS and ids == sorted(ids)
    _held(result)


def test_a_semicolon_export_whose_names_hold_commas(tmp_path: pathlib.Path) -> None:
    """Comma and semicolon both read three fields a record; the cells read
    as numbers only under the semicolon, so it is the delimiter.

    What this holds is the written form, and the real file validating. The
    twin's decimal-comma columns miss `numeric.fraction_widths` at this
    seed -- a defect of how a declared decimal-comma column's widths are
    written, measured the same on the comma-written equivalent at commit
    53bb012, and the number-spelling lane's, not this one's.
    """
    draw = random.Random(35)
    body = ["id;Gewicht, kg;Größe, cm"]
    for _index in range(ROWS):
        body += [
            f"{draw.randint(10000, 99999)};{draw.randint(400, 1200) / 10:.1f};"
            f"{draw.randint(1500, 2000) / 10:.1f}".replace(".", ",")
        ]
    data = ("\r\n".join(body) + "\r\n").encode("cp1252")
    flags = ("--decimal-comma", "Gewicht, kg", "--decimal-comma", "Größe, cm")
    result = _round_trip(tmp_path, data, flags)
    assert result["form"]["delimiter"] == ";"
    assert result["names"] == ["id", "Gewicht, kg", "Größe, cm"]
    lines = result["twin"].split(b"\r\n")[:-1]
    assert len(lines) == ROWS + 1 and all(line.count(b";") == 2 for line in lines)
    assert result["twin_form"] == result["form"]
    assert result["twin_encoding"] == result["encoding"]
    assert result["exits"]["real"] == 0


def test_a_constant_column_is_passed_over_for_the_sort(tmp_path: pathlib.Path) -> None:
    """A study column holding one value says nothing about order; the
    sorted participant column beside it is the sort column."""
    draw = random.Random(37)
    pids = sorted(draw.sample(range(1, 9999), ROWS))
    body = ["study,pid,age"] + [f"STUDY01,P{pid:04d},{draw.randint(18, 90)}" for pid in pids]
    result = _round_trip(tmp_path, ("\n".join(body) + "\n").encode())
    assert result["form"]["row_order"] == {
        "collation": "text", "column": 2, "direction": "ascending",
    }
    written = [row[1] for row in _records(result["twin"], "utf-8")[1:]]
    assert written == sorted(written)
    _held(result)


def test_a_comma_space_guess_the_file_breaks_is_walked_again(
    tmp_path: pathlib.Path,
) -> None:
    """Every field follows `, ` but one, which begins with three spaces
    and stands past the first records the guess is made from: the
    comma-space reading would drop two spaces of a value, so the file is
    walked again without it and the spaces are kept."""
    draw = random.Random(38)
    body = ["id, note, site"]
    for index in range(450):
        note = "   indented" if index == 420 else " plain"
        body += [f"S{draw.randint(10000, 99999)},{note}, {draw.choice(SITES)}"]
    data = ("\n".join(body) + "\n").encode()
    result = _round_trip(tmp_path, data)
    assert result["form"]["initial_space"] is False
    assert result["twin"].count(b",   indented,") == 1
    _held(result)


def test_short_rows_beside_rows_ending_empty_are_refused(tmp_path: pathlib.Path) -> None:
    """A row leaving out its last cell beside a full row whose last cell is
    empty is not one writer's habit, so the file is refused as ragged."""
    draw = random.Random(39)
    body = ["id,age,note"]
    for index in range(ROWS):
        cells = [f"S{draw.randint(10000, 99999)}", f"{draw.randint(18, 90)}"]
        if index % 3 == 0:
            body += [",".join(cells)]
        elif index % 3 == 1:
            body += [",".join(cells) + ","]
        else:
            body += [",".join(cells) + ",seen"]
    real = tmp_path / "real.csv"
    real.write_bytes(("\n".join(body) + "\n").encode())
    assert _exit_of(["profile", str(real), "--out-dir", str(tmp_path), "--replace"]) == 1


def test_a_blank_last_name_is_a_column_when_a_row_fills_it(
    tmp_path: pathlib.Path,
) -> None:
    """`id,age,` above rows ending with a comma looks like a trailing
    delimiter until a row writes a value there; the file is walked again
    and the last column is `Unnamed: 2`."""
    draw = random.Random(40)
    body = ["id,age,"]
    for index in range(ROWS):
        tail = "y" if index % 4 == 3 else ""
        body += [f"S{draw.randint(10000, 99999)},{draw.randint(18, 90)},{tail}"]
    result = _round_trip(tmp_path, ("\n".join(body) + "\n").encode())
    assert result["names"] == ["id", "age", "Unnamed: 2"]
    assert result["form"]["trailing_delimiter"] == {"header": False, "rows": False}
    _held(result)


def test_the_counted_forms_can_miss(tmp_path: pathlib.Path) -> None:
    """Counted line endings and counted blank lines are each shown failing
    on a file that differs in that one respect."""
    rows = _people(41)
    header = "record_id,age,arm,site,reading"
    plain = ("\n".join([header] + _lines(rows)) + "\n").encode()
    text = header + "\n"
    for index in range(ROWS):
        text += _lines([rows[index]])[0] + ("\r\n" if index % 3 == 0 else "\n")
    counted = _describe(tmp_path / "counted-endings", text.encode())
    assert "bytes.line-endings" in _missed(tmp_path / "counted-endings-plain", counted, plain)
    fewer = text.replace("\r\n", "\n", 1).encode()
    assert "bytes.line-endings" in _missed(tmp_path / "counted-endings-fewer", counted, fewer)

    spaced = ("\n\n".join([header] + _lines(rows)) + "\n").encode()
    blanks = _describe(tmp_path / "counted-blanks", spaced)
    assert "bytes.blank-lines" in _missed(tmp_path / "counted-blanks-plain", blanks, plain)

    in_order = sorted(rows, key=lambda row: row[0])
    below = ("\n".join([header] + _lines(in_order) + [",,,,"] * 3) + "\n")
    ordered = _describe(tmp_path / "ordered-empties", below.encode())
    shuffled = ("\n".join([header] + _lines(rows) + [",,,,"] * 3) + "\n").encode()
    assert "rows.order" in _missed(tmp_path / "ordered-empties-shuffled", ordered, shuffled)


def test_the_summary_names_the_lines_before_the_names(
    tmp_path: pathlib.Path,
) -> None:
    """The summary says how many lines of text stand before the column
    names, and that none of their text is published -- at every floor.

    IT USED TO SAY THE OPPOSITE at the default floor: that those lines
    were "published in the description as written, because the smallest
    group is one", and it offered `--smallest-group` as the way to
    withhold them. Both sentences were true of the rule plan P4-D80
    replaced, and both are what review item CODEX-3 measured.
    """
    rows = _people(42)
    text = "Report: cohort extract 2026-09-01\n" + "\n".join(
        ["record_id,age,arm,site,reading"] + _lines(rows)
    ) + "\n"
    for floor in ("1", "11"):
        folder = tmp_path / f"floor-{floor}"
        folder.mkdir()
        real = folder / "real.csv"
        real.write_bytes(text.encode())
        assert _exit_of(
            [
                "profile", str(real), "--out-dir", str(folder), "--replace",
                "--smallest-group", floor,
            ]
        ) == 0
        said = (folder / "real-profile.txt").read_text(encoding="utf-8")
        assert "About the lines before your column names:" in said, said[:600]
        assert "--smallest-group above 1" not in said
        assert "Report: cohort extract 2026-09-01" not in said
