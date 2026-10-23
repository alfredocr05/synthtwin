"""Lane R6, reading (plan P4-D387): a trailing delimiter closed `""`.

Codex's review of integration part 2c, outside its scope: a table whose
header is `site;dx`, whose first record is `0100;1E22;""` and whose next
119 records are `0100;1E22;` was read as ONE comma-delimited column, so
code written on its twin could not run on the real table. Landing R5
lined a reading up only by an empty last field written bare, because a
twin closing every line bare wrote `1;2;""` back as `1;2;`.

The twin now closes each line as its source closed it, and the closing
is published: `trailing_delimiter.header` and `.rows` are `true`
(closed bare), `"quoted"` (closed `""`) or, on the rows, the closings'
runs in file order, held to the census line as the line endings are
(`dialect.closing_runs_disclosed`). Detection lines a reading up by an
empty last field written either way (`dialect._ends_empty`), and the
walk reads a `""` closing in a second walk only where its first walk,
landing R5's, refuses a file that holds `""` (`survey`'s
``quoted_closing``), so every file read before is read as before.

Each test names the mutant it is red on.
"""

import contextlib
import io
import json
import pathlib
import sys

import pytest

import fixtures
from synthtwin import contract, dialect, errors
import lowered_floor  # a floor under 11 (plan P4-D426)

DELIMITERS = [",", ";", "\t", "|"]
IDS = ["comma", "semicolon", "tab", "bar"]


def _exit_of(argv: "list[str]") -> int:
    """Run one synthtwin command in this process, quietly, and return its exit code."""

    before = sys.argv
    sys.argv = ["synthtwin"] + argv
    sink = io.StringIO()
    try:
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            code = lowered_floor.main()
    except SystemExit as stop:
        return 0 if stop.code is None else int(stop.code)
    finally:
        sys.argv = before
    return code


def _codex_table(rows: int = 120) -> str:
    return "site;dx\n0100;1E22;\"\"\n" + "".join(["0100;1E22;\n" for _row in range(rows - 1)])


def _table(d: str, closed: "list[bool] | None", header_end: str = "", rows: int = 120) -> str:
    """A made-up two-column table; ``closed`` says which records close `""`
    (None: no trailing delimiter on the records)."""
    lines = [f"site{d}dx" + header_end]
    for index in range(rows):
        line = f"{100 + index % 7:04d}{d}{index % 3}E2{index % 5}"
        if closed is not None:
            line += d + ('""' if closed[index] else "")
        lines += [line]
    return "\n".join(lines) + "\n"


def _read(text: str, floor: int = 11) -> "dialect.Survey":
    return dialect.settle(text, "utf-8", False, False, "t.csv", small_cell_floor=floor)


def _round_trip(folder: pathlib.Path, text: str, floor: int = 11, headerless: bool = False) -> "dict[str, object]":
    """Describe, build, describe the twin again; validate twin and table.
    ``headerless`` describes both with `--first-row data`."""
    folder.mkdir(parents=True, exist_ok=True)
    real = folder / "real.csv"
    real.write_bytes(text.encode("utf-8"))
    floor_flag = ["--smallest-group", str(floor)] if floor != 11 else []
    floor_flag += ["--first-row", "data"] if headerless else []
    assert _exit_of(["profile", str(real), "--out-dir", str(folder), "--replace"] + floor_flag) == 0
    described = folder / "real-profile.json"
    assert _exit_of(["generate", str(described), "--out-dir", str(folder), "--seed", "4", "--replace"]) == 0
    twin = folder / "real-twin.csv"
    again = folder / "again"
    again.mkdir()
    (again / "twin.csv").write_bytes(twin.read_bytes())
    assert _exit_of(["profile", str(again / "twin.csv"), "--out-dir", str(again), "--replace"] + floor_flag) == 0
    exits = {}
    for label, target in (("twin", twin), ("real", real)):
        checked = folder / f"check-{label}"
        checked.mkdir()
        exits[label] = _exit_of(
            ["validate", str(described), "--twin", str(target), "--out-dir", str(checked), "--replace"]
        )
    first = json.loads(described.read_text(encoding="utf-8"))
    second = json.loads((again / "twin-profile.json").read_text(encoding="utf-8"))
    return {
        "names": [column["name"] for column in first["columns"]],
        "twin_names": [column["name"] for column in second["columns"]],
        "form": first["source"]["dialect"],
        "twin_form": second["source"]["dialect"],
        "twin": twin.read_bytes().decode("utf-8"),
        "exits": exits,
    }


def _closings(text: str, d: str) -> str:
    """Each line's closing: Q (`""`), B (bare delimiter), N (none)."""
    out = ""
    for line in text.split("\n"):
        line = line.rstrip("\r")
        if not line:
            continue
        out += "Q" if line.endswith(d + '""') else "B" if line.endswith(d) else "N"
    return out


def test_the_codex_table_is_read_as_its_two_columns(tmp_path: pathlib.Path) -> None:
    """THE FAULT. `site;dx` over `0100;1E22;""` and 119 records
    `0100;1E22;` is the semicolon's two columns closed by the semicolon;
    its one `""` is a count of one, below the census line, so the
    closings are published bare throughout, as the line endings are, and
    twin and table validate at 0. Red on 6a248e7 (one comma column), on
    the mutant whose detection lines up only a bare closing (`_ends_empty`
    as `_closes`), and on the mutant without the second walk."""
    text = _codex_table()
    assert dialect.delimiter_reading(text, 0) == (";", ())
    found = _read(text)
    assert list(found.header) == ["site", "dx"]
    assert found.n_rows == 120
    assert found.form.rows_trailing_delimiter and not found.form.header_trailing_delimiter
    assert not found.form.rows_closing_quoted and found.form.rows_closing_runs == ()
    result = _round_trip(tmp_path, text)
    assert result["names"] == ["site", "dx"]
    assert result["form"]["trailing_delimiter"] == {"header": False, "rows": True}
    assert result["twin_form"] == result["form"]
    assert _closings(result["twin"], ";") == "N" + "B" * 120
    assert result["exits"] == {"twin": 0, "real": 0}, result["exits"]


def test_at_a_floor_of_one_the_lone_quoted_closing_is_written_back(tmp_path: pathlib.Path) -> None:
    """At `--smallest-group 1`, where nothing is held to a line, the runs
    are published as the file has them and the twin's first record closes
    `""`. Red on the mutant whose twin closes every line bare."""
    result = _round_trip(tmp_path, _codex_table(), floor=1)
    assert result["form"]["trailing_delimiter"]["rows"] == [
        {"ending": "quoted", "lines": 1},
        {"ending": "bare", "lines": 119},
    ]
    assert _closings(result["twin"], ";") == "NQ" + "B" * 119
    assert result["twin_form"] == result["form"]
    assert result["exits"] == {"twin": 0, "real": 0}, result["exits"]


@pytest.mark.parametrize("d", DELIMITERS, ids=IDS)
def test_closings_that_stand_are_written_back_as_the_source_wrote_them(tmp_path: pathlib.Path, d: str) -> None:
    """Every record closed `""`; sixty `""` then sixty bare; and a header
    closed `""` over records closed bare. The twin writes each closing
    back, reads back to the same form, and twin and table validate at 0.
    Red on 6a248e7 (one column or refused) and on the mutant whose twin
    closes every line bare."""
    cases = {
        "quoted": (_table(d, [True] * 120), "N" + "Q" * 120, '"quoted"'),
        "half": (_table(d, [index < 60 for index in range(120)]), "N" + "Q" * 60 + "B" * 60, "runs"),
        "header": (_table(d, None, d + '""'), "Q" + "N" * 120, "header"),
    }
    for label, (text, ends, _said) in cases.items():
        result = _round_trip(tmp_path / label, text)
        assert result["names"] == ["site", "dx"], (label, result["names"])
        assert _closings(result["twin"], d) == ends, (label, _closings(result["twin"], d)[:12])
        assert result["twin_form"] == result["form"], label
        assert result["exits"] == {"twin": 0, "real": 0}, (label, result["exits"])
    trailing = _read(cases["half"][0]).form
    assert trailing.rows_closing_runs == (
        dialect.EndingRun(ending=dialect.CLOSING_QUOTED, lines=60),
        dialect.EndingRun(ending=dialect.CLOSING_BARE, lines=60),
    )


def test_the_closings_are_held_to_the_census_line() -> None:
    """`closing_runs_disclosed`: runs stand only where every run and each
    closing's total reach the line; otherwise the commonest closing, a
    tie going bare. Red on the mutant that publishes the runs as found."""
    q, b = dialect.CLOSING_QUOTED, dialect.CLOSING_BARE
    run = dialect.EndingRun
    assert dialect.closing_runs_disclosed([run(q, 1), run(b, 119)], 11) == (False, ())
    assert dialect.closing_runs_disclosed([run(b, 1), run(q, 119)], 11) == (True, ())
    assert dialect.closing_runs_disclosed([run(q, 120)], 11) == (True, ())
    assert dialect.closing_runs_disclosed([run(q, 60), run(b, 60)], 11) == (False, (run(q, 60), run(b, 60)))
    tenth: "list[dialect.EndingRun]" = []
    for _step in range(12):
        tenth += [run(q, 1), run(b, 9)]
    assert dialect.closing_runs_disclosed(tenth, 11) == (False, ())
    assert dialect.closing_runs_disclosed([run(q, 1), run(b, 119)], 1) == (False, (run(q, 1), run(b, 119)))
    many: "list[dialect.EndingRun]" = []
    for _step in range(40):
        many += [run(q, 20), run(b, 11)]
    assert dialect.closing_runs_disclosed(many, 11) == (True, ())


@pytest.mark.parametrize("d", DELIMITERS, ids=IDS)
def test_a_header_that_trails_too_keeps_the_records_bare(tmp_path: pathlib.Path, d: str) -> None:
    """`a;b;` over one record closed bare and 119 closed `""`: published
    closed `""` throughout, its twin -- every line ending in the
    delimiter, every record in `""` -- would be read as one column more,
    as such a table is read, and the twin missed its own description. So
    where the header trails too, a single closing is the bare one. Red
    on the mutant without that rule (the twin validates at 3)."""
    text = _table(d, [index != 0 for index in range(120)], d)
    found = _read(text)
    assert found.form.header_trailing_delimiter and found.form.rows_trailing_delimiter
    assert not found.form.rows_closing_quoted
    result = _round_trip(tmp_path, text)
    assert result["twin_form"] == result["form"]
    assert result["exits"] == {"twin": 0, "real": 0}, result["exits"]


@pytest.mark.parametrize("d", DELIMITERS, ids=IDS)
def test_tables_read_before_are_read_as_before(d: str) -> None:
    """A table the first walk reads is never walked again: `a;b;` over
    records all closed `""` is three columns, the last named blank, and
    so is `a;b;""` over them; a table closed bare publishes `true` as
    before. Red on the mutant that reads `""` closings in the first walk
    (``quoted_closing`` True from the start)."""
    for head in (d, d + '""'):
        found = _read(_table(d, [True] * 120, head))
        assert list(found.header) == ["site", "dx", ""], head
        assert not found.form.header_trailing_delimiter, head
        assert not found.form.rows_trailing_delimiter, head
    bare = dialect.document_of(_read(_table(d, [False] * 120)).form)
    assert bare["trailing_delimiter"] == {"header": False, "rows": True}


def test_a_file_the_second_walk_cannot_read_is_refused_in_the_first_walks_words() -> None:
    """Header `a,b,c,` over rows of three, row 51 `31,72,Q,""`: the second
    walk refuses it too, and the refusal is the first walk's, naming the
    row's four values (landing R5's item 4 sentence)."""
    lines = ["col_a,col_b,col_c,"] + ["31,72,Q"] * 120
    lines[51] = '31,72,Q,""'
    with pytest.raises(errors.ProfileError) as refused:
        _read("\n".join(lines) + "\n")
    said = " ".join(str(refused.value).split())
    assert "The first row names 3 columns, but row 51 has 4" in said, said


def _block(rows: object, header: object = False) -> dict:
    form = dialect.ordinary(2, 120, True)
    document = dialect.document_of(form)
    document["trailing_delimiter"] = {"header": header, "rows": rows}
    return document


def test_the_loader_reads_each_closing_and_refuses_what_the_producer_never_writes() -> None:
    """The block parses `true`, `"quoted"` and runs; any other word is
    refused, and the rules refuse runs a reader could point at a record
    with (below the line at the default floor) or that do not account
    for the records. Red on the mutant loader that reads `"quoted"` as
    no closing, and on the one without the runs rule."""
    assert contract._dialect_block(_block("quoted", "quoted")).rows_closing_quoted
    assert contract._dialect_block(_block("quoted", "quoted")).header_closing_quoted
    runs = [{"ending": "quoted", "lines": 60}, {"ending": "bare", "lines": 60}]
    form = contract._dialect_block(_block(runs))
    assert form.rows_trailing_delimiter and len(form.rows_closing_runs) == 2
    for wrong in ("bare", "QUOTED", 1, [], [{"ending": "lf", "lines": 1}]):
        with pytest.raises(errors.ProfileError):
            contract._dialect_block(_block(wrong))
    with pytest.raises(errors.ProfileError):
        contract._dialect_block(_block(runs[:1], [{"ending": "quoted", "lines": 1}]))


def test_the_loader_refuses_runs_a_reader_could_point_at_a_record_with(tmp_path: pathlib.Path) -> None:
    """A described table closed sixty `""` then sixty bare loads; the same
    description edited to one `""` then 119 bare -- a run below the
    census line --, to runs counting 119 records, or to runs that hold
    one closing only (sixty `""` twice, which the producer publishes as
    `"quoted"`), is refused under FD2, the rule the line endings are held
    to. Red on the mutant loader without the runs rule, and the last case
    on the one without its `len(kinds) < 2` half."""
    real = tmp_path / "real.csv"
    real.write_bytes(_table(";", [index < 60 for index in range(120)]).encode("utf-8"))
    assert _exit_of(["profile", str(real), "--out-dir", str(tmp_path), "--replace"]) == 0
    described = tmp_path / "real-profile.json"
    document = json.loads(described.read_text(encoding="utf-8"))
    contract.load_profile(str(described))
    for runs in (
        [{"ending": "quoted", "lines": 1}, {"ending": "bare", "lines": 119}],
        [{"ending": "quoted", "lines": 60}, {"ending": "bare", "lines": 59}],
        [{"ending": "quoted", "lines": 60}, {"ending": "quoted", "lines": 60}],
    ):
        document["source"]["dialect"]["trailing_delimiter"]["rows"] = runs
        edited = fixtures.write_profile(tmp_path, "edited-profile.json", document)
        with pytest.raises(errors.ProfileError) as refused:
            contract.load_profile(str(edited))
        assert "FD2" in str(refused.value), str(refused.value)[:300]


def test_the_producer_s_closings_always_load(tmp_path: pathlib.Path) -> None:
    """The producer-always-loads battery for the runs rule (FD2): every
    closing shape lane R6 reads, under each delimiter, at the default
    floor and at one, is described and its description loads (generate
    exits 0). Lane R6's full reading battery (planning notes, wave5/R6)
    ran 193 tables the same way, R5's 63 among them."""
    shapes = {
        "first": [index == 0 for index in range(120)],
        "last": [index == 119 for index in range(120)],
        "tenth": [index % 10 == 0 for index in range(120)],
        "half": [index < 60 for index in range(120)],
        "all": [True] * 120,
    }
    for d, word in zip(DELIMITERS, IDS):
        for label, closed in shapes.items():
            for floor in (11, 1):
                folder = tmp_path / f"{word}-{label}-{floor}"
                folder.mkdir()
                real = folder / "real.csv"
                real.write_bytes(_table(d, closed).encode("utf-8"))
                floor_flag = ["--smallest-group", str(floor)] if floor != 11 else []
                assert _exit_of(["profile", str(real), "--out-dir", str(folder), "--replace"] + floor_flag) == 0
                assert _exit_of(
                    ["generate", str(folder / "real-profile.json"), "--out-dir", str(folder), "--seed", "4", "--replace"]
                ) == 0, (word, label, floor)


class _CountedRuns(tuple):
    """A tuple of runs that counts how often it is walked."""

    walks = 0

    def __iter__(self):
        type(self).walks += 1
        return super().__iter__()


def test_the_closings_cost_the_rows_plus_the_runs_at_a_million_rows() -> None:
    """Machine-free operation counts. The twin's closings at 1,000,000
    rows walk the published runs once (`closings_in_turn`), and the walk
    keeps at most `MAXIMUM_ENDING_RUNS` + 1 runs whatever the rows: a
    table closed `""` and bare by turns builds as many closing runs at
    20,000 rows as at 2,000. Red on a writer that looks each record's
    run up from the start (one walk per record)."""
    runs = _CountedRuns(
        [dialect.EndingRun(dialect.CLOSING_QUOTED, 500_000), dialect.EndingRun(dialect.CLOSING_BARE, 500_000)]
    )
    form = dialect.Dialect(**{**dialect.ordinary(2, 1_000_000, True).__dict__, "rows_trailing_delimiter": True, "rows_closing_runs": runs})
    _CountedRuns.walks = 0
    quoted = dialect.closings_in_turn(form, 1_000_000)
    assert len(quoted) == 1_000_000 and quoted[0] and not quoted[999_999]
    assert _CountedRuns.walks == 1
    made: "list[int]" = []
    for rows in (2_000, 20_000):
        built = [0]
        real = dialect.EndingRun

        def counted(ending: str, lines: int, _real=real, _built=built) -> "dialect.EndingRun":
            if ending in dialect.CLOSINGS:
                _built[0] = _built[0] + 1
            return _real(ending=ending, lines=lines)

        dialect.EndingRun = counted  # type: ignore[assignment,misc]
        try:
            found = _read(_table(";", [index % 2 == 0 for index in range(rows)], rows=rows))
        finally:
            dialect.EndingRun = real  # type: ignore[misc]
        assert found.form.rows_trailing_delimiter
        made += [built[0]]
    assert made[0] == made[1] <= dialect.MAXIMUM_ENDING_RUNS + 4, made


def test_the_guard_refuses_runs_the_producer_never_publishes(tmp_path: pathlib.Path) -> None:
    """The publication guard (`profile.check_publication`) holds the runs
    to the producer's rule as the loader does: a finished description
    closed sixty `""` then sixty bare passes; the same document with its
    runs edited to one `""` then 119 bare (a run below the census line at
    the default floor) or to runs holding one closing only is refused.
    Red on the mutant guard without its runs rule (kinds and
    `endings_broken`)."""
    from synthtwin import profile, reading, taxonomy

    real = tmp_path / "real.csv"
    real.write_bytes(_table(";", [index < 60 for index in range(120)]).encode("utf-8"))
    table = reading.read_table(str(real), small_cell_floor=11)
    document = profile.build_document(table, taxonomy.Settings(small_cell_floor=11), [], [], [])
    assert len(document["source"]["dialect"]["trailing_delimiter"]["rows"]) == 2
    profile.check_publication(document)
    for runs in (
        [{"ending": "quoted", "lines": 1}, {"ending": "bare", "lines": 119}],
        [{"ending": "quoted", "lines": 60}, {"ending": "quoted", "lines": 60}],
    ):
        document["source"]["dialect"]["trailing_delimiter"]["rows"] = runs
        with pytest.raises(errors.ProfileError):
            profile.check_publication(document)


def test_a_record_past_the_published_runs_takes_the_last_run_s_closing() -> None:
    """`closings_in_turn`: the run holding a record says, and a record
    past the runs takes the last run's closing, `""` or bare. Red on the
    mutant that writes those records bare."""
    q, b = dialect.CLOSING_QUOTED, dialect.CLOSING_BARE
    base = dialect.ordinary(2, 40, True).__dict__
    for runs, expected in (
        ((dialect.EndingRun(q, 20), dialect.EndingRun(b, 11)), [True] * 20 + [False] * 20),
        ((dialect.EndingRun(b, 20), dialect.EndingRun(q, 11)), [False] * 20 + [True] * 20),
    ):
        form = dialect.Dialect(**{**base, "rows_trailing_delimiter": True, "rows_closing_runs": runs})
        assert dialect.closings_in_turn(form, 40) == expected, runs


def _checked(folder: pathlib.Path, described: pathlib.Path, data: bytes) -> "tuple[int, list[str]]":
    """Validate ``data`` against a description: the exit and the subchecks MISSED."""
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / "other.csv"
    target.write_bytes(data)
    checked = folder / "checked"
    checked.mkdir()
    code = _exit_of(["validate", str(described), "--twin", str(target), "--out-dir", str(checked), "--replace"])
    report = (checked / "other-quality.txt").read_text(encoding="utf-8")
    missed: "list[str]" = []
    for line in report.split("\n"):
        text = line.strip()
        if text.endswith(": MISSED") and " [" in text:
            missed += [text.split(" [")[0]]
    return code, missed


def test_a_file_closed_otherwise_than_its_description_misses_the_closing_rule(tmp_path: pathlib.Path) -> None:
    """The validator's closing rule (`validation._trailing_words`): each
    twin validates at 0 as built, and at 3, `bytes.trailing-delimiter`
    MISSED, once its `""` closings are rewritten bare -- the records
    published as runs (sixty `""`, sixty bare), the header published
    closed `""` (only the header rewritten), and the records published
    `"quoted"` (one bare then 119 `""`). Red on each of the three
    mutants that drop the runs sentence, the header's `""` and the
    rows' `"quoted"` from the rule's words."""
    d = ";"
    half = [index < 60 for index in range(120)]
    cases = {
        "runs": (_table(d, half), False, {"header": False, "rows": [
            {"ending": "quoted", "lines": 60}, {"ending": "bare", "lines": 60}]}),
        "header": (_table(d, half, d + '""'), True, {"header": "quoted", "rows": [
            {"ending": "quoted", "lines": 60}, {"ending": "bare", "lines": 60}]}),
        "quoted": (_table(d, [index != 0 for index in range(120)]), False, {"header": False, "rows": "quoted"}),
    }
    for label, (text, header_only, published) in cases.items():
        folder = tmp_path / label
        folder.mkdir()
        real = folder / "real.csv"
        real.write_bytes(text.encode("utf-8"))
        assert _exit_of(["profile", str(real), "--out-dir", str(folder), "--replace"]) == 0
        described = folder / "real-profile.json"
        document = json.loads(described.read_text(encoding="utf-8"))
        assert document["source"]["dialect"]["trailing_delimiter"] == published, label
        assert _exit_of(["generate", str(described), "--out-dir", str(folder), "--seed", "4", "--replace"]) == 0
        built = (folder / "real-twin.csv").read_bytes().decode("utf-8")
        assert _checked(folder / "as-built", described, built.encode("utf-8")) == (0, []), label
        lines = built.split("\n")
        for index in range(1 if header_only else len(lines)):
            if lines[index].endswith(d + '""'):
                lines[index] = lines[index][:-2]
        edited = "\n".join(lines)
        assert edited != built, label
        code, missed = _checked(folder / "rewritten", described, edited.encode("utf-8"))
        assert code == 3 and "bytes.trailing-delimiter" in missed, (label, code, missed)


def test_a_comma_space_table_s_closings_are_written_back(tmp_path: pathlib.Path) -> None:
    """The comma-space form: header `site, dx` over sixty records closed
    `, ""` then sixty closed `,`. The twin closes its first sixty records
    `, ""` (the space every field but the first takes, `_closing_quotes`),
    reads back to the same form, and twin and table validate at 0. Red on
    the mutant that writes the closing `""` without the space."""
    lines = ["site, dx"]
    for index in range(120):
        lines += [f"{100 + index % 7:04d}, {index % 3}E2{index % 5}," + (' ""' if index < 60 else "")]
    result = _round_trip(tmp_path, "\n".join(lines) + "\n")
    assert result["names"] == ["site", "dx"], result["names"]
    assert result["form"]["initial_space"] is True, result["form"]
    written = [line for line in str(result["twin"]).split("\n") if line]
    assert [line.endswith(', ""') for line in written[1:]] == [True] * 60 + [False] * 60
    assert [line.endswith(",") for line in written[61:]] == [True] * 60
    assert result["twin_form"] == result["form"]
    assert result["exits"] == {"twin": 0, "real": 0}, result["exits"]


def test_a_file_whose_closings_fall_on_other_records_misses_the_closing_rule(tmp_path: pathlib.Path) -> None:
    """The run lengths in the closing rule (`validation._trailing_words`):
    a table published as runs (sixty records closed `""`, sixty bare)
    validates at 0 as built, and at 3, `bytes.trailing-delimiter` MISSED,
    once its twin is rewritten so the first fifty records close `""` and
    the last seventy close bare -- both closings still present, both runs
    above the census line, only the records they fall on moved. Red on the
    mutant that drops the run lengths from the rule's runs sentence."""
    d = ";"
    folder = tmp_path / "runs"
    folder.mkdir()
    real = folder / "real.csv"
    real.write_bytes(_table(d, [index < 60 for index in range(120)]).encode("utf-8"))
    assert _exit_of(["profile", str(real), "--out-dir", str(folder), "--replace"]) == 0
    described = folder / "real-profile.json"
    document = json.loads(described.read_text(encoding="utf-8"))
    assert document["source"]["dialect"]["trailing_delimiter"] == {"header": False, "rows": [
        {"ending": "quoted", "lines": 60}, {"ending": "bare", "lines": 60}]}
    assert _exit_of(["generate", str(described), "--out-dir", str(folder), "--seed", "4", "--replace"]) == 0
    built = (folder / "real-twin.csv").read_bytes().decode("utf-8")
    assert _checked(folder / "as-built", described, built.encode("utf-8")) == (0, [])
    lines = built.split("\n")
    assert _closings(built, d) == "N" + "Q" * 60 + "B" * 60
    for index in range(1, 121):
        record = lines[index][:-2] if lines[index].endswith(d + '""') else lines[index]
        lines[index] = record + ('""' if index <= 50 else "")
    shifted = "\n".join(lines)
    assert _closings(shifted, d) == "N" + "Q" * 50 + "B" * 70
    code, missed = _checked(folder / "shifted", described, shifted.encode("utf-8"))
    assert code == 3 and "bytes.trailing-delimiter" in missed, (code, missed)


# -- Codex's review of landing R6 (head 0c921e1), four items ----------------

# A header `a;b|c;` over records `1;Y|Z|""`: 6a248e7 reads the semicolon's
# columns `a` and `b|c` (the header closed bare), and a reading lined up
# only by the `""` closing -- the bar's `a;b` and `c;` -- took it on
# 0c921e1. Each pair is (the delimiter 6a248e7 reads, the one it does not).
_CANDIDATE_PAIRS = [(";", "|"), (",", "\t"), ("\t", ";"), ("|", ","), (",", ";"), (";", ","), ("|", "\t"), ("\t", "|")]


@pytest.mark.parametrize("pair", _CANDIDATE_PAIRS, ids=["".join(map(repr, pair)) for pair in _CANDIDATE_PAIRS])
def test_a_reading_made_from_a_candidate_before_lane_r6_stands(pair: "tuple[str, str]") -> None:
    """Item 1 (HIGH). A reading lined up only by a closing written `""`
    -- the kind lane R6 admitted -- comes after every reading 6a248e7
    could make (straight, or lined up by a bare closing), so it never
    takes a file from one: the header `a;b|c;` over 120 records
    `1;Y|Z|""` is the semicolon's columns `a` and `b|c` holding `1` and
    `Y|Z|""`, with no question, as on 6a248e7. Red on 0c921e1 (the bar
    took it: `a;b` and `c;` holding `1;Y` and `Z`, a tie recorded)."""
    o, i = pair
    text = f"a{o}b{i}c{o}\n" + "".join([f'1{o}Y{i}Z{i}""\n' for _row in range(120)])
    assert dialect.delimiter_reading(text, 0) == (o, ())
    found = _read(text)
    assert list(found.header) == ["a", f"b{i}c"], found.header
    assert found.columns[0][0] == "1" and found.columns[1][0] == f'Y{i}Z{i}""'
    assert found.form.header_trailing_delimiter and not found.form.rows_trailing_delimiter
    assert dialect.trailing_published(found.form) == {"header": True, "rows": False}


@pytest.mark.parametrize("d", DELIMITERS, ids=IDS)
def test_the_escapings_are_tried_before_a_quoted_closing(d: str) -> None:
    """Item 2 (HIGH). `settle` tries the spacing and the escaping of
    6a248e7 before it reads a `""` as a closing: a header `a,b` over 120
    records `1,x\\,""` is read with backslash escapes, the second value
    `x,""`, as on 6a248e7. Red on 0c921e1, whose second walk ran inside
    the first `survey` and read `x\\` closed `""`, so the escaping was
    never tried. The codex table, which no escaping reads, is still read
    by the closing (`test_the_codex_table_is_read_as_its_two_columns`)."""
    text = f"a{d}b\n" + "".join([f'1{d}x\\{d}""\n' for _row in range(120)])
    found = _read(text)
    assert list(found.header) == ["a", "b"]
    assert found.form.escape == dialect.ESCAPE_BACKSLASH
    assert found.columns[1][0] == f'x{d}""', found.columns[1][0]
    assert not found.form.rows_trailing_delimiter
    assert dialect.trailing_published(found.form) == {"header": False, "rows": False}


def _described(
    folder: pathlib.Path, text: str, floor: int = 11, headerless: bool = False
) -> "tuple[pathlib.Path, dict]":
    """Describe a made-up table; the description's path and document.
    ``headerless`` describes it with `--first-row data`."""
    folder.mkdir(parents=True, exist_ok=True)
    real = folder / "real.csv"
    real.write_bytes(text.encode("utf-8"))
    floor_flag = ["--smallest-group", str(floor)] if floor != 11 else []
    floor_flag += ["--first-row", "data"] if headerless else []
    assert _exit_of(["profile", str(real), "--out-dir", str(folder), "--replace"] + floor_flag) == 0
    described = folder / "real-profile.json"
    return described, json.loads(described.read_text(encoding="utf-8"))


def _built(path: pathlib.Path, floor: int = 11, headerless: bool = False) -> dict:
    """The description the producer builds for a table, before the guard."""
    from synthtwin import profile, reading, taxonomy

    first_row = reading.FIRST_ROW_DATA if headerless else reading.FIRST_ROW_AUTOMATIC
    table = reading.read_table(str(path), first_row=first_row, small_cell_floor=floor)
    return profile.build_document(table, taxonomy.Settings(small_cell_floor=floor), [], [], [])


def _refused_by_both(
    folder: pathlib.Path, document: dict, trailing: dict, rule: str, floor: int = 11, headerless: bool = False
) -> None:
    """The loader refuses the described table's description with
    ``trailing`` under ``rule``, and the publication guard refuses the
    producer's document for it edited the same way (built at ``floor``,
    ``headerless`` with `--first-row data`)."""
    from synthtwin import profile

    edited = json.loads(json.dumps(document))
    edited["source"]["dialect"]["trailing_delimiter"] = trailing
    written = fixtures.write_profile(folder, "edited-profile.json", edited)
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(str(written))
    assert rule in str(refused.value), (trailing, str(refused.value)[:300])
    built = _built(folder / "real.csv", floor, headerless)
    profile.check_publication(built)
    built["source"]["dialect"]["trailing_delimiter"] = trailing
    with pytest.raises(errors.ProfileError):
        profile.check_publication(built)


def test_a_trailing_header_never_loads_over_records_all_closed_quoted(tmp_path: pathlib.Path) -> None:
    """Item 3 (MEDIUM). A header ending in its delimiter over records all
    closed `""` is a table with one column more, its last name blank,
    and is read so, so the producer never publishes it (`survey`: a
    header that trails too keeps the records bare). A valid 120-record
    two-column semicolon description edited to `{"header": true, "rows":
    "quoted"}` -- and to a header `"quoted"` over them -- wrote `site;dx;`
    over records ending `;""`, read back as three columns: both are now
    refused by the loader (FD10) and by the publication guard. Red on
    0c921e1, where both loaded."""
    described, document = _described(tmp_path / "source", _table(";", [False] * 120, ";"))
    assert document["source"]["dialect"]["trailing_delimiter"] == {"header": True, "rows": True}
    contract.load_profile(str(described))
    for header in (True, "quoted"):
        _refused_by_both(tmp_path / "source", document, {"header": header, "rows": "quoted"}, "FD10")


def test_a_trailing_header_s_closings_always_load_and_read_back(tmp_path: pathlib.Path) -> None:
    """Item 3's producer-always-loads battery. A header closed bare or
    `""` over records closed `""` throughout, one bare then `""`, `""`
    then one bare, half and half, and every tenth `""`, under each
    delimiter, at the default floor and at one: each is described, never
    as a trailing header over records all closed `""`, and its
    description loads (generate exits 0). Under the semicolon at the
    default floor each twin is also read back to the same form, and twin
    and table validate at 0."""
    shapes = {
        "all": [True] * 120,
        "first-bare": [index != 0 for index in range(120)],
        "last-bare": [index != 119 for index in range(120)],
        "half": [index < 60 for index in range(120)],
        "tenth": [index % 10 == 0 for index in range(120)],
    }
    for d, word in zip(DELIMITERS, IDS):
        for head, header_end in (("bare", d), ("quoted", d + '""')):
            for label, closed in shapes.items():
                for floor in (11, 1):
                    folder = tmp_path / f"{word}-{head}-{label}-{floor}"
                    text = _table(d, closed, header_end)
                    if d == ";" and floor == 11:
                        result = _round_trip(folder, text, floor)
                        assert result["exits"] == {"twin": 0, "real": 0}, (head, label, result["exits"])
                        again = dict(result["twin_form"])
                        if label == "all" and head == "quoted":
                            # Three straight columns, the last named blank
                            # and written bare by the twin: the header's
                            # quoting `mixed` is read back `needed` (the
                            # limit stated under P4-D387, as on 6a248e7).
                            again["header_quoting"] = result["form"]["header_quoting"]
                        assert again == result["form"], (head, label)
                        trailing = result["form"]["trailing_delimiter"]
                    else:
                        described, document = _described(folder, text, floor)
                        assert _exit_of(
                            ["generate", str(described), "--out-dir", str(folder), "--seed", "4", "--replace"]
                        ) == 0, (word, head, label, floor)
                        trailing = document["source"]["dialect"]["trailing_delimiter"]
                    assert not (trailing["header"] is not False and trailing["rows"] == "quoted"), trailing


def test_closing_runs_their_twin_cannot_measure_back_are_refused(tmp_path: pathlib.Path) -> None:
    """Item 4 (MEDIUM). The twin's closings are measured back as runs in
    file order, two runs of one closing side by side as one, and past
    `MAXIMUM_ENDING_RUNS` as the commonest closing; so runs `[quoted 30,
    quoted 30, bare 60]` (measured `[quoted 60, bare 60]`) and 80
    alternating runs of 11 over 880 records (measured bare throughout)
    described tables their own twins missed (`bytes.trailing-delimiter`).
    Both are now refused by the loader (FD2) and the publication guard.
    Red on 0c921e1, where both loaded and passed the guard."""
    q, b = "quoted", "bare"
    _, document = _described(tmp_path / "short", _table(";", [index < 60 for index in range(120)]))
    _refused_by_both(
        tmp_path / "short",
        document,
        {"header": False, "rows": [{"ending": q, "lines": 30}, {"ending": q, "lines": 30}, {"ending": b, "lines": 60}]},
        "FD2",
    )
    _, document = _described(tmp_path / "long", _table(";", [index < 440 for index in range(880)], rows=880))
    runs = [{"ending": q if index % 2 == 0 else b, "lines": 11} for index in range(80)]
    _refused_by_both(tmp_path / "long", document, {"header": False, "rows": runs}, "FD2")


def test_closing_runs_up_to_the_cap_are_published_measured_back_and_named(tmp_path: pathlib.Path) -> None:
    """Item 4's producer-always-loads battery and the validator's words.
    64 alternating runs of 11 records (the cap) are published as runs,
    load, build a twin read back to the same runs, and validate at 0,
    the closing rule naming all 64 runs and no more; 65 runs are
    published as the commonest closing and validate at 0 as well."""
    from synthtwin import validation

    cap = dialect.MAXIMUM_ENDING_RUNS
    for count in (cap, cap + 1):
        rows = 11 * count
        closed = [(index // 11) % 2 == 0 for index in range(rows)]
        result = _round_trip(tmp_path / f"runs-{count}", _table(";", closed, rows=rows))
        trailing = result["form"]["trailing_delimiter"]
        if count == cap:
            assert isinstance(trailing["rows"], list) and len(trailing["rows"]) == cap
            form = contract.load_profile(str(tmp_path / f"runs-{count}" / "real-profile.json")).source.dialect
            words = validation._trailing_words(form)
            assert words.count("11 with") == cap, words
        else:
            assert trailing["rows"] == "quoted", trailing
        assert result["twin_form"] == result["form"], count
        assert result["exits"] == {"twin": 0, "real": 0}, (count, result["exits"])


# -- The verifier of the Codex fix stream (head 8abdbbe), two open items -----


def _headerless(text: str) -> str:
    """A made-up table's records without its header line."""
    return text.split("\n", 1)[1]


def test_a_headerless_table_s_rows_never_load_with_a_trailing_delimiter(tmp_path: pathlib.Path) -> None:
    """Item 3's class, without a header (the verifier's open item 1).
    Under a header not read from the file the survey takes the width
    from the first record, so a delimiter ending it is one column more
    and the producer publishes the rows closed `false`. A valid
    120-record two-column semicolon description read with `--first-row
    data`, edited to rows `true`, `"quoted"` or `[quoted 60, bare 60]`,
    wrote `0106;2E+24;""` and was read back three columns wide
    (`columns.n_columns` MISSED): each is now refused by the loader
    (FD10) and by the publication guard. Red on 8abdbbe, where loader,
    guard and generate accepted all three."""
    q, b = "quoted", "bare"
    described, document = _described(tmp_path / "source", _headerless(_table(";", None)), headerless=True)
    assert document["source"]["header_source"] != "file"
    assert [column["name"] for column in document["columns"]] == ["column_1", "column_2"]
    assert document["source"]["dialect"]["trailing_delimiter"] == {"header": False, "rows": False}
    contract.load_profile(str(described))
    for rows in (True, q, [{"ending": q, "lines": 60}, {"ending": b, "lines": 60}]):
        _refused_by_both(tmp_path / "source", document, {"header": False, "rows": rows}, "FD10", headerless=True)


def test_a_headerless_table_s_closings_always_load_and_read_back(tmp_path: pathlib.Path) -> None:
    """The verifier's open item 1, the producer-always-loads battery.
    Headerless records closed bare throughout, `""` throughout, the
    first `""` and the rest bare, and half and half, under each
    delimiter at the default floor and at one: each is described with
    its rows closed `false` (the closing is the table's third column),
    loads, builds a twin, is read back to the same columns and the same
    form, and twin and table validate at 0. Green on 8abdbbe too: the
    producer never published such rows; the refusal above is the half
    this repair adds."""
    shapes = {
        "bare": [False] * 120,
        "quoted": [True] * 120,
        "first-quoted": [index == 0 for index in range(120)],
        "half": [index < 60 for index in range(120)],
    }
    for d, word in zip(DELIMITERS, IDS):
        for label, closed in shapes.items():
            for floor in (11, 1):
                folder = tmp_path / f"{word}-{label}-{floor}"
                result = _round_trip(folder, _headerless(_table(d, closed)), floor, headerless=True)
                where = (word, label, floor)
                assert result["form"]["trailing_delimiter"] == {"header": False, "rows": False}, where
                assert result["names"] == ["column_1", "column_2", "column_3"], (where, result["names"])
                assert result["twin_names"] == result["names"], (where, result["twin_names"])
                again = json.loads(json.dumps(result["twin_form"]))
                if label in ("first-quoted", "half"):
                    # The third column's empties, some written `""` and
                    # some bare, are quoted `mixed` and read back
                    # `needed` from the twin: a column's quoting, as on
                    # 6a248e7, and not its closing.
                    assert again["columns"][2]["quoting"]["empty"] == "needed", where
                    again["columns"][2]["quoting"]["empty"] = result["form"]["columns"][2]["quoting"]["empty"]
                assert again == result["form"], where
                assert result["exits"] == {"twin": 0, "real": 0}, (where, result["exits"])


def test_a_closing_run_of_no_records_is_refused_by_both(tmp_path: pathlib.Path) -> None:
    """Item 4's seam (the verifier's open item 2). At a floor of one the
    census line let a run of no records through the guard -- rows
    `[quoted 0, bare 60, quoted 60]` -- while the loader refused it
    (a run's `lines` is at least 1); `dialect.closing_runs_broken` now
    names any run of fewer than one record, so both refuse it. Red on
    8abdbbe, where the guard accepted it."""
    q, b = "quoted", "bare"
    assert dialect.closing_runs_broken(
        (dialect.EndingRun(ending=q, lines=0), dialect.EndingRun(ending=b, lines=60), dialect.EndingRun(ending=q, lines=60))
    )
    _, document = _described(tmp_path / "zero", _table(";", [index < 60 for index in range(120)]), floor=1)
    runs = [{"ending": q, "lines": 0}, {"ending": b, "lines": 60}, {"ending": q, "lines": 60}]
    _refused_by_both(tmp_path / "zero", document, {"header": False, "rows": runs}, "lines", floor=1)
