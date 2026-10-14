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

DELIMITERS = [",", ";", "\t", "|"]
IDS = ["comma", "semicolon", "tab", "bar"]


def _exit_of(argv: "list[str]") -> int:
    """Run one synthtwin command in this process, quietly, and return its exit code."""
    from synthtwin import cli

    before = sys.argv
    sys.argv = ["synthtwin"] + argv
    sink = io.StringIO()
    try:
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            code = cli.main()
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


def _round_trip(folder: pathlib.Path, text: str, floor: int = 11) -> "dict[str, object]":
    """Describe, build, describe the twin again; validate twin and table."""
    folder.mkdir(parents=True, exist_ok=True)
    real = folder / "real.csv"
    real.write_bytes(text.encode("utf-8"))
    floor_flag = ["--smallest-group", str(floor)] if floor != 11 else []
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
    census line -- or to runs counting 119 records, is refused under FD2,
    the rule the line endings are held to. Red on the mutant loader
    without the runs rule."""
    real = tmp_path / "real.csv"
    real.write_bytes(_table(";", [index < 60 for index in range(120)]).encode("utf-8"))
    assert _exit_of(["profile", str(real), "--out-dir", str(tmp_path), "--replace"]) == 0
    described = tmp_path / "real-profile.json"
    document = json.loads(described.read_text(encoding="utf-8"))
    contract.load_profile(str(described))
    for runs in (
        [{"ending": "quoted", "lines": 1}, {"ending": "bare", "lines": 119}],
        [{"ending": "quoted", "lines": 60}, {"ending": "bare", "lines": 59}],
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
