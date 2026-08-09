"""The first-row decision: what is shown, and what is only assumed.

Review item P1-R6-F6 said that absence of evidence must not be counted
as evidence for the names reading. Two repairs tried to answer it by
proving the opposite -- that a first row IS a set of column names -- and
failed in opposite directions, one questioning ordinary headed files and
one publishing a headerless export's first record as schema. That proof
does not exist: nothing about the letters in ``site`` makes it the name
of a column rather than the name of a place.

The rule this file pins turns the question around. Only ONE side can be
shown positively, so only that side is tested for:

1. the file shows the first row is a RECORD -- in some column its value
   is a number among that column's numbers, a date among its dates, or a
   value the column repeats -- and synthtwin stops and asks, naming
   --first-row names and --first-row data;
2. nothing shows that, and the first row is taken as the column names BY
   CONVENTION: not blocked, but never unrecorded. The Table says
   ``header_by_convention`` and ``header_evidence`` says in plain words
   that the names were assumed, not proved, and how to take that back;
3. --first-row on the command line wins over both, in either direction.

The tests below are grouped by those three outcomes, and every one of
them asserts the number of records that survived. The headerless export

    alice,canada,34
    bob,usa,29
    carol,usa,41
    dan,usa,38

is the regression for the second repair, which deleted the numeric rule
and published a person's name, country and age as the column names of a
four-record file it reported as having three rows.

No data file is committed: every table here is built from bytes in the
test that needs it (plan D13).
"""

import json
import pathlib

import pytest

from synthtwin import cli, errors, profile, reading, taxonomy

# The regression for the second repair of this item. Column 3 is the
# one that speaks: 34 sits inside the range 29..41 written below it.
_HEADERLESS_EXPORT = (
    b"alice,canada,34\n"
    b"bob,usa,29\n"
    b"carol,usa,41\n"
    b"dan,usa,38\n"
)

# The file the review item itself named. Nothing in it belongs to the
# column below it, so it is READ AS HEADED, by convention -- see the
# outcome-2 section, where the cost of that is pinned along with the
# record of the assumption.
_WORDS_OVER_WORDS = (
    b"alpha note,red apple\n"
    b"beta observation,green pear\n"
    b"gamma record,blue berry\n"
)

# A number one step below the only number under it.
_ONE_DATA_ROW = b"P001,34\nP002,35\n"

# Dates under a date.
_DATES_UNDER_A_DATE = b"2024-03-01,north\n" + b"".join(
    b"2024-03-%02d,south\n" % index for index in range(2, 12)
)

# A label the column repeats: "site-1" appears nine more times below.
_A_REPEATED_LABEL = b"pa-001,site-1\n" + b"".join(
    b"pa-%03d,site-%d\n" % (index, index % 3) for index in range(2, 30)
)

# Every value of the first row reads as a number.
_ALL_NUMBERS = b"1,2\n3,4\n5,6\n"

# An ordinary pivoted year table: 2019 is nowhere near the values below
# it, so nothing in the file shows the first row is a record.
_PIVOTED_YEARS = b"region,2019,2020\n" + b"".join(
    b"place %d,3.1%d,3.2%d\n" % (index, index, index) for index in range(1, 13)
)


def _write(folder: pathlib.Path, body: bytes) -> pathlib.Path:
    target = folder / "table.csv"
    target.write_bytes(body)
    return target


def _run(folder: pathlib.Path, body: bytes, *extra: str) -> int:
    """Write ``body`` as the table and run `synthtwin profile` on it."""
    target = _write(folder, body)
    return cli.main(["profile", f"{target}", *extra])


def _written(folder: pathlib.Path) -> list[pathlib.Path]:
    return sorted(
        path for path in folder.iterdir() if path.suffix in (".json", ".txt")
    )


def _document(folder: pathlib.Path) -> dict:
    for path in _written(folder):
        if path.suffix == ".json":
            return json.loads(path.read_text(encoding="utf-8"))
    raise AssertionError("no profile document was written")


# --------------------------------------------------------------------
# outcome 1: the file shows the first row is a record
# --------------------------------------------------------------------


def test_the_headerless_export_stops_instead_of_publishing_a_person(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The verified regression of the second repair: this exited 0,
    # reported 3 rows for a 4-record file, and published alice, canada
    # and 34 as the column names and in publication_notes.
    code = _run(tmp_path, _HEADERLESS_EXPORT)
    streams = capsys.readouterr()
    assert code == 1, streams.out
    assert "cannot tell whether the first row" in streams.err, streams.err
    assert "--first-row names" in streams.err, streams.err
    assert "--first-row data" in streams.err, streams.err
    assert _written(tmp_path) == [], _written(tmp_path)


def test_the_headerless_export_keeps_all_four_records_as_data(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = _run(tmp_path, _HEADERLESS_EXPORT, "--first-row", "data")
    streams = capsys.readouterr()
    assert code == 0, streams.err
    document = _document(tmp_path)
    assert document["n_rows"] == 4, "not one record may be lost"
    assert [column["name"] for column in document["columns"]] == [
        "column_1",
        "column_2",
        "column_3",
    ]
    text = json.dumps(document)
    for word in ("alice", "canada"):
        assert f'"name": "{word}"' not in text, text


def test_the_number_that_speaks_is_the_one_inside_the_range() -> None:
    # The rule the second repair deleted, at the level it is produced.
    assert reading._numeric_fit("34", ["29", "41", "38"])
    spoken = reading._record_evidence(
        ["alice", "canada", "34"],
        [["bob", "carol", "dan"], ["usa", "usa", "usa"], ["29", "41", "38"]],
    )
    assert spoken is not None
    assert "column 3" in spoken, spoken


_SHOWS_A_RECORD = {
    "a number one step below its column": (_ONE_DATA_ROW, "number"),
    "a date among dates": (_DATES_UNDER_A_DATE, "date"),
    "a label the column repeats": (_A_REPEATED_LABEL, "appears"),
    # A number inside the range below it, in a table whose other
    # columns are worded text that says nothing either way.
    "a number inside the range below": (
        (
            b"aa bb,cc dd,120.50\n"
            b"ee ff,gg hh,89.9\n"
            b"ii jj,kk ll,1004.25\n"
            b"mm nn,oo pp,17.5\n"
        ),
        "number",
    ),
}


@pytest.mark.parametrize("name", sorted(_SHOWS_A_RECORD))
def test_evidence_of_a_record_stops_and_says_what_it_found(
    tmp_path: pathlib.Path, name: str
) -> None:
    body, reason = _SHOWS_A_RECORD[name]
    target = _write(tmp_path, body)
    with pytest.raises(errors.ProfileError) as caught:
        reading.read_table(f"{target}")
    message = f"{caught.value}"
    assert "cannot tell whether the first row" in message, name
    assert reason in message, message
    assert "--first-row names" in message and "--first-row data" in message


def test_the_question_never_prints_the_row_it_is_asking_about(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # If that row IS a record, printing it prints somebody's data in
    # order to ask a question about it -- and so does printing a value
    # from below it. The column is named by its position instead.
    _run(tmp_path, _HEADERLESS_EXPORT)
    streams = capsys.readouterr()
    for word in ("alice", "canada", "bob", "carol", "dan", "usa"):
        assert word not in streams.err, streams.err
        assert word not in streams.out, streams.out
    assert "column 3" in streams.err, streams.err


def test_the_slack_around_a_column_of_numbers_is_pinned_at_both_ends() -> None:
    # Both neighbouring values of _NEARBY_SHARE_OF_THE_RANGE break
    # something, so the two files that bound it are asserted here rather
    # than left to a comment. Narrower than about 0.4 of the range and
    # 140 above 3 ... 101 -- a headerless table whose first record holds
    # its largest number -- is published as schema. Wider than about
    # 0.7 and an ordinary pivoted year table is questioned.
    assert reading._NEARBY_SHARE_OF_THE_RANGE == 0.5
    below = ["99", "20", "7", "101", "3"]
    assert reading._numeric_fit("140", below), "the record must be seen"
    assert not reading._numeric_fit("199", below), "the slack has an end"
    counts = [f"{1000 + step * 30}" for step in range(1, 20)]
    assert not reading._numeric_fit("2019", counts), "an ordinary year label"


def test_the_three_record_rules_each_speak_where_they_should() -> None:
    # A number among numbers, and not a year above one-digit codes.
    assert reading._numeric_fit("34", ["35", "36", "37", "38", "39"])
    assert reading._numeric_fit("34", ["35"])
    assert not reading._numeric_fit("2019", ["1", "1", "1"])
    assert not reading._numeric_fit("2019", ["1234", "1234"])
    assert not reading._numeric_fit("2019", ["101", "112"])
    assert not reading._numeric_fit("age", ["31", "32"])
    assert not reading._numeric_fit("34", ["29", "x"])
    # A date among dates, and not a name above them.
    assert reading._date_fit("2024-01-03", ["2024-01-04", "2024-01-11"])
    assert not reading._date_fit("visit", ["2024-01-04", "2024-01-11"])
    assert not reading._date_fit("2024-01-03", ["2024-01-04", "north"])
    # A label the column repeats, and NOT a one-off code it happens to
    # hold once: every value of a column of unique codes is a one-off,
    # so a single match there is a coincidence.
    assert reading._repeats_a_value_below("site-1", ["site-1", "x", "site-1"])
    assert not reading._repeats_a_value_below("B10", ["B09", "B10", "B11"])
    assert not reading._repeats_a_value_below("hue", ["red", "tan"])


# --------------------------------------------------------------------
# outcome 2: nothing shows it, so the convention is followed and SAID
# --------------------------------------------------------------------

# Ordinary headed tables. None of them holds a first-row value that
# belongs to the column below it, so none is questioned. The row count
# says no record was eaten either way.
_ORDINARY = {
    "one row of two plain words": (b"name,note\nnorth,ok\n", 1),
    "numbers under a name": (
        b"age,site\n"
        + b"".join(b"%d,north\n" % (30 + index) for index in range(9)),
        9,
    ),
    "dates under a name": (
        b"visit,answer\n"
        + b"".join(b"2024-01-%02d,yes\n" % (index + 1) for index in range(9)),
        9,
    ),
    "codes under a name": (
        b"record_code,region\n"
        + b"".join(b"R%03d,north\n" % index for index in range(9)),
        9,
    ),
    "written notes under a name": (
        b"label,comment\n"
        + b"".join(
            b"alpha,a note written out %d\n" % index for index in range(9)
        ),
        9,
    ),
    "one repeated label under a name": (
        b"hue,batch\n"
        + b"".join(b"%s,one\n" % word for word in [b"red", b"tan", b"sky"] * 3),
        9,
    ),
    "names that look like their own codes": (
        b"visit1,visit2\n"
        + b"".join(b"a%d,b%d\n" % (index % 9, index % 9) for index in range(12)),
        12,
    ),
    "two-letter names over two-letter codes": (
        b"aa,bb\n" + b"".join(b"xy,zw\n" for _index in range(12)),
        12,
    ),
    "a pivoted year table": (_PIVOTED_YEARS, 12),
    # Measured, not argued: with a full range-width of slack instead of
    # half a one, the number rule reaches 2019 from sales counts in the
    # 1,000-1,600 range and questions this perfectly ordinary table.
    "a pivoted year table over four-digit counts": (
        b"region,2019,2020,2021\n"
        + b"".join(
            b"place %d,%d,%d,%d\n"
            % (index, 1000 + index * 30, 1100 + index * 25, 1050 + index * 28)
            for index in range(1, 20)
        ),
        19,
    ),
    "a name that is one of its column's unique codes": (
        b"age,B10\n"
        + b"".join(b"%d,B%02d\n" % (30 + index, index) for index in range(1, 20)),
        19,
    ),
}


@pytest.mark.parametrize("name", sorted(_ORDINARY))
def test_an_ordinary_headed_table_is_profiled_without_a_question(
    tmp_path: pathlib.Path, name: str, capsys: pytest.CaptureFixture[str]
) -> None:
    # The verified regression of the FIRST repair: `synthtwin profile`
    # on an ordinary headed file ended in the ambiguity refusal and exit
    # code 1. A tool that asks a question about every file cannot be
    # used by the person this one is written for.
    body, expected_rows = _ORDINARY[name]
    code = _run(tmp_path, body)
    streams = capsys.readouterr()
    assert code == 0, streams.err
    assert "cannot tell whether the first row" not in streams.err, streams.err
    document = _document(tmp_path)
    assert document["n_rows"] == expected_rows, name
    assert document["source"]["header_source"] == reading.HEADER_FROM_FILE
    first_name = body.split(b"\n")[0].split(b",")[0].decode()
    assert document["columns"][0]["name"] == first_name, name


@pytest.mark.parametrize("name", sorted(_ORDINARY))
def test_a_table_taken_by_convention_says_that_is_what_happened(
    tmp_path: pathlib.Path, name: str
) -> None:
    # Not blocked is not the same as not recorded. Each of these is read
    # as names; what differs is whether the file SHOWED that or the
    # reader assumed it, and the Table says which, both in the
    # machine-readable way and in words a person can act on.
    #
    # Two of these files show it: a column of numbers under a first-row
    # value that is not a number is a difference in kind, so nothing is
    # assumed and the summary stays quiet. The rest are assumptions and
    # must say so. Both readings keep every record -- the row count is
    # asserted either way, which is the property that actually matters.
    body, expected_rows = _ORDINARY[name]
    target = _write(tmp_path, body)
    table = reading.read_table(f"{target}")
    assert table.n_rows == expected_rows, name
    if table.header_by_convention:
        assert "by convention, not by evidence" in table.header_evidence, name
        assert "--first-row data" in table.header_evidence, name
    else:
        assert "is not a number" in table.header_evidence, name


def test_the_review_items_own_file_is_read_by_convention_and_says_so(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # This is the cost of the convention, pinned so it is never a
    # surprise: nothing in this file belongs to the column below it, so
    # its first record becomes the column names and 2 rows are described
    # instead of 3. What review item P1-R6-F6 asked for -- and what the
    # two earlier repairs could not give without breaking ordinary files
    # -- is that synthtwin claim no evidence for that reading. It does
    # not: it names the assumption and hands over the way to undo it.
    code = _run(tmp_path, _WORDS_OVER_WORDS)
    streams = capsys.readouterr()
    assert code == 0, streams.err
    document = _document(tmp_path)
    assert document["n_rows"] == 2
    table = reading.read_table(f"{tmp_path / 'table.csv'}")
    assert table.header_by_convention is True
    assert table.column_names == ["alpha note", "red apple"]
    evidence = table.header_evidence
    assert "by convention, not by evidence" in evidence, evidence
    assert "did not check" in evidence, evidence
    assert "--first-row data" in evidence, evidence


def test_the_convention_sentence_claims_nothing_about_the_file() -> None:
    # The exact defect of review item P1-R6-F6 was a sentence that
    # turned "we found nothing" into "the file says so". No form of
    # that claim may reappear in this sentence.
    evidence = reading._TAKEN_BY_CONVENTION
    for claim in ("evidence that", "because the file", "proves", "shows that"):
        assert claim not in evidence, evidence
    assert "not by evidence" in evidence


def test_no_record_rule_speaks_for_the_review_items_file() -> None:
    header = ["alpha note", "red apple"]
    columns = [
        ["beta observation", "gamma record"],
        ["green pear", "blue berry"],
    ]
    for index in range(len(header)):
        assert not reading._numeric_fit(header[index], columns[index])
        assert not reading._date_fit(header[index], columns[index])
        assert not reading._repeats_a_value_below(header[index], columns[index])
    assert reading._record_evidence(header, columns) is None


# --------------------------------------------------------------------
# outcome 3: what the caller says wins, in both directions
# --------------------------------------------------------------------


def test_answering_data_keeps_all_three_records(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = _run(tmp_path, _WORDS_OVER_WORDS, "--first-row", "data")
    streams = capsys.readouterr()
    assert code == 0, streams.err
    assert "3 rows" in streams.out, streams.out
    document = _document(tmp_path)
    assert document["n_rows"] == 3
    names = [column["name"] for column in document["columns"]]
    assert names == ["column_1", "column_2"]
    # The record the convention would consume is not schema anywhere.
    text = json.dumps(document)
    assert "alpha note" not in text, text
    assert document["source"]["header_source"] == reading.HEADER_GENERATED


def test_answering_data_keeps_the_first_record_as_a_value(
    tmp_path: pathlib.Path,
) -> None:
    target = _write(tmp_path, _WORDS_OVER_WORDS)
    table = reading.read_table(f"{target}", reading.FIRST_ROW_DATA)
    assert table.n_rows == 3, "not one record may be lost"
    assert table.columns[0][0] == "alpha note"
    assert table.column_names == ["column_1", "column_2"]
    assert "--first-row data" in table.header_evidence
    assert table.header_by_convention is False


def test_answering_names_reads_the_first_row_as_the_schema(
    tmp_path: pathlib.Path,
) -> None:
    target = _write(tmp_path, _WORDS_OVER_WORDS)
    table = reading.read_table(f"{target}", reading.FIRST_ROW_NAMES)
    assert table.n_rows == 2
    assert table.column_names == ["alpha note", "red apple"]
    assert table.header_source == reading.HEADER_FROM_FILE
    assert "--first-row names" in table.header_evidence
    assert table.header_by_convention is False


def test_the_caller_wins_over_evidence_the_file_did_hold(
    tmp_path: pathlib.Path,
) -> None:
    # The other direction, on a file the rules DO stop: --first-row
    # names accepts it without a question and keeps 3 rows of the 4.
    target = _write(tmp_path, _HEADERLESS_EXPORT)
    table = reading.read_table(f"{target}", reading.FIRST_ROW_NAMES)
    assert table.n_rows == 3
    assert table.column_names == ["alice", "canada", "34"]
    assert table.header_by_convention is False
    kept = reading.read_table(f"{target}", reading.FIRST_ROW_DATA)
    assert kept.n_rows == 4
    assert kept.columns[0][0] == "alice"


def test_answering_data_overrides_a_table_the_convention_would_take(
    tmp_path: pathlib.Path,
) -> None:
    # The convention is not an oracle either, so the person must be able
    # to overrule it. --first-row data keeps all 13 rows of a table the
    # convention would have read as headed.
    target = _write(tmp_path, _PIVOTED_YEARS)
    table = reading.read_table(f"{target}", reading.FIRST_ROW_DATA)
    assert table.n_rows == 13
    assert table.columns[0][0] == "region"
    assert table.header_source == reading.HEADER_GENERATED


# --------------------------------------------------------------------
# a first row that is entirely numbers
# --------------------------------------------------------------------


def test_a_first_row_of_numbers_stops_and_names_a_way_forward(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = _run(tmp_path, _ALL_NUMBERS)
    streams = capsys.readouterr()
    assert code == 1, streams.out
    assert "does not look like column names" in streams.err, streams.err
    assert "--first-row data" in streams.err, streams.err
    assert _written(tmp_path) == [], _written(tmp_path)


def test_a_first_row_of_numbers_answered_as_data_keeps_every_record(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = _run(tmp_path, _ALL_NUMBERS, "--first-row", "data")
    streams = capsys.readouterr()
    assert code == 0, streams.err
    document = _document(tmp_path)
    assert document["n_rows"] == 3
    assert [column["name"] for column in document["columns"]] == [
        "column_1",
        "column_2",
    ]


# --------------------------------------------------------------------
# what the question must never come before
# --------------------------------------------------------------------


def test_the_readers_disagreeing_is_reported_before_the_question(
    tmp_path: pathlib.Path,
) -> None:
    # R1-X3: the standard reader yields ["", "B"] here and pandas'
    # reader yields ["B", ""]. A file the two readers read differently
    # has no single right reading for a person to choose between, so
    # asking them to choose one would be asking a question about a file
    # whose meaning is not settled.
    target = _write(tmp_path, b"c0,c1\n\r,B\nz,w\n")
    with pytest.raises(errors.ProfileError) as caught:
        reading.read_table(f"{target}")
    assert "do not agree about the value" in f"{caught.value}"


def test_a_repeated_name_is_reported_as_itself(
    tmp_path: pathlib.Path,
) -> None:
    # The other side of that order: pandas renames a repeated column to
    # "a.1", so comparing the two readings first would report a name
    # disagreement for a file whose real problem is the repeat.
    target = _write(tmp_path, b"a,a\n1,2\n3,4\n")
    with pytest.raises(errors.ProfileError) as caught:
        reading.read_table(f"{target}")
    assert "repeats the same column name" in f"{caught.value}"


# --------------------------------------------------------------------
# the verdict travels with the table
# --------------------------------------------------------------------


def test_every_verdict_carries_its_reason_in_words(
    tmp_path: pathlib.Path,
) -> None:
    settled = _write(tmp_path, _PIVOTED_YEARS)
    for first_row in (
        reading.FIRST_ROW_AUTOMATIC,
        reading.FIRST_ROW_NAMES,
        reading.FIRST_ROW_DATA,
    ):
        table = reading.read_table(f"{settled}", first_row)
        assert table.header_evidence, first_row
        assert table.header_evidence.endswith("."), table.header_evidence
        # Written for a person: no code words, no shape notation.
        for jargon in ("_numeric_fit", "signature", "True", "None"):
            assert jargon not in table.header_evidence, table.header_evidence


def test_the_verdict_survives_the_profile_document(
    tmp_path: pathlib.Path,
) -> None:
    # The verdict itself is already published as source.header_source.
    # The two things that qualify it -- that it was an assumption, and
    # the sentence saying so -- live on the Table; profile.py is the
    # module that must publish them beside it.
    target = _write(tmp_path, _PIVOTED_YEARS)
    table = reading.read_table(f"{target}")
    document = profile.build_document(table, taxonomy.Settings(), [])
    assert document["source"]["header_source"] == reading.HEADER_FROM_FILE
    assert table.header_by_convention is True
    assert table.header_evidence


def test_the_refusal_message_states_only_what_was_found() -> None:
    # The wording this replaces claimed "at least one has exactly the
    # shape every other value in its column has", which the reader had
    # not checked and which could be false of every column in the file.
    message = errors.first_row_could_be_a_record(
        "/data/table.csv", 3, "in column 3 the value in that row is a number"
    )
    assert "in column 3 the value in that row is a number" in message
    assert "exactly the shape every other value" not in message
    assert "none of them stands out as a name" not in message
    plain = errors.first_row_could_be_a_record("/data/table.csv", 3)
    assert "belongs among the values" in plain
    assert "--first-row names" in plain and "--first-row data" in plain
