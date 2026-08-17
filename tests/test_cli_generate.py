"""`synthtwin generate` end to end (plan P2-D1, P2-D8, P2-D10).

Four properties of the command are checked here, and each one is checked
against what actually reached the disk rather than against what the code
meant to do.

1. THE SEED'S GRAMMAR. synthtwin states its own accepted spelling and
   its own range, because the library underneath accepts a wider set and
   refuses a negative number in words about bit widths that no
   researcher should ever be shown. Every boundary the plan freezes is
   here: the two ends of the range, one over the top, a sign, a
   separator, a leading space, a figure from another writing system, and
   leading zeros, which are accepted and change nothing.

2. A NAME THAT IS ALREADY TAKEN. There is no way to prove that a file
   sitting at one of the two output names is an earlier twin rather than
   somebody's own work, so no such proof is attempted: the run refuses,
   names both files, and teaches `--replace`. What is asserted is that
   the bytes that were there are still there afterwards.

3. THE HEADER ROW, both ways. It is written when the description says
   the names came from the table's own file and not written when the
   description says synthtwin made them up -- so a headerless table
   yields a headerless twin, and the row count is right in both.

4. THE BYTE-ORDER MARK. A first column name may validly begin with it,
   and writing that name unquoted would begin the twin with the mark's
   own bytes -- which the reader then eats, so the column comes back
   under a name the description never published. The round trip is run
   through the real reader and the bytes are checked directly.

The descriptions are built by the REAL producer from seeded neutral
tables (plan D13: no data-format file is ever committed), so these tests
run producer, loader, generator and command end to end.
"""

import builtins
import importlib
import pathlib
import sys
import typing

import pytest

import fixtures
from synthtwin import (
    cli,
    profile,
    reading,
    rendering,
    taxonomy,
)
from synthtwin.cli import main

# The byte-order mark, as text and as the bytes it is written in.
# Every non-ASCII character in this file is written as an escape, so
# nothing invisible hides in the source.
_MARK = "\ufeff"
_MARK_BYTES = b"\xef\xbb\xbf"


def _plain_table(rows: int = 48) -> str:
    """A neutral two-column table: labels beside whole numbers."""
    made = [[fixtures.REGIONS[index % 4], f"{index % 7}"] for index in range(rows)]
    return fixtures.rows_to_csv(["region", "visits"], made)


def _described(
    folder: pathlib.Path,
    text: str,
    name: str = "clinic.csv",
    first_row: str = reading.FIRST_ROW_AUTOMATIC,
) -> pathlib.Path:
    """Write a table, describe it with the real producer, return the path.

    The description is written exactly as `synthtwin profile` writes it,
    through the same serializer, so the loader sees a genuine document
    and not one this file made up.
    """
    table_path = fixtures.write(folder, name, text)
    table = reading.read_table(f"{table_path}", first_row)
    document = profile.build_document(table, taxonomy.Settings(), [])
    stem = f"{table_path.stem}"
    target = fixtures.write_profile(folder, f"{stem}-profile.json", document)
    return target


def _twin_of(description: pathlib.Path) -> pathlib.Path:
    return description.parent / "clinic-twin.csv"


def _report_of(description: pathlib.Path) -> pathlib.Path:
    return description.parent / "clinic-twin-report.txt"


def _watching_imports(
    monkeypatch: pytest.MonkeyPatch,
) -> "list[str]":
    """Record every module name imported from now on.

    The recorder sees the import statement itself, not the module cache,
    so a module another test has already imported is still recorded when
    this one reaches for it -- which is the whole point: the question is
    whether the generate path ASKS for the reader, not whether the reader
    happens to be in memory.
    """
    seen: list[str] = []
    real = builtins.__import__

    def watched(
        name: str,
        where: "dict[str, typing.Any] | None" = None,
        inside: "dict[str, typing.Any] | None" = None,
        fromlist: "tuple[str, ...] | None" = None,
        level: int = 0,
    ) -> object:
        seen.append(name)
        for extra in fromlist if fromlist else ():
            seen.append(f"{name}.{extra}")
        return real(name, where, inside, fromlist, level)  # type: ignore[arg-type]

    monkeypatch.setattr(builtins, "__import__", watched)
    return seen


# ---------------------------------------------------------------------
# 1. the seed's grammar and range (plan P2-D8)
# ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "given,value",
    [
        ("0", 0),
        ("1", 1),
        ("12345", 12345),
        # Leading zeros are accepted and change nothing.
        ("007", 7),
        ("0000", 0),
        ("000000000000000000000000012345", 12345),
        # Both ends of the stated range.
        ("18446744073709551615", 18446744073709551615),
        ("018446744073709551615", 18446744073709551615),
    ],
)
def test_a_seed_in_figures_is_read_as_the_number_it_spells(
    given: str, value: int
) -> None:
    assert cli._seed_or_refusal(given) == (value, "")


@pytest.mark.parametrize(
    "given",
    [
        "-1",
        "+1",
        "1_0",
        " 1",
        "1 ",
        "1.0",
        "1e5",
        "0x10",
        "",
        "seven",
        # An Arabic-Indic three. Python reads it as a number, so a
        # command that let the library convert the text would silently
        # take a seed the person did not type.
        "\u0663",
        # A figure with a zero-width space inside it.
        "1\u200b2",
    ],
)
def test_a_seed_spelled_any_other_way_is_refused_in_words(given: str) -> None:
    seed, refusal = cli._seed_or_refusal(given)
    assert seed is None
    assert "plain figures" in refusal
    assert "18446744073709551615" in refusal
    assert "Nothing was written." in refusal
    # The library's own vocabulary must never reach a person.
    for jargon in ("uint64", "bit", "dtype", "unsigned", "Traceback"):
        assert jargon not in refusal


@pytest.mark.parametrize(
    "given",
    [
        "18446744073709551616",
        "18446744073709551620",
        "99999999999999999999",
        "0018446744073709551616",
    ],
)
def test_a_seed_above_the_range_is_refused_in_words(given: str) -> None:
    seed, refusal = cli._seed_or_refusal(given)
    assert seed is None
    assert "larger than the largest seed" in refusal
    assert "18446744073709551615" in refusal


def test_a_seed_of_very_many_figures_is_refused_rather_than_crashing() -> None:
    """Python refuses to read a number written in thousands of figures.

    Its refusal is a traceback, so the length is settled before anything
    is converted. Five thousand figures is past Python's own limit.
    """
    seed, refusal = cli._seed_or_refusal("9" * 5000)
    assert seed is None
    assert "larger than the largest seed" in refusal


def test_the_command_refuses_a_bad_seed_before_it_writes_anything(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    description = _described(tmp_path, _plain_table())
    assert main(["generate", f"{description}", "--seed", "-1"]) == 2
    told = capsys.readouterr().err
    assert "plain figures" in told
    assert not _twin_of(description).exists()
    assert not _report_of(description).exists()


def test_the_command_accepts_the_largest_seed_in_the_range(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    description = _described(tmp_path, _plain_table())
    code = main(
        ["generate", f"{description}", "--seed", "18446744073709551615"]
    )
    assert code == 0
    capsys.readouterr()
    assert _twin_of(description).is_file()


def test_a_seed_of_leading_zeros_builds_the_same_twin(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """'007' is the seed 7, so it must give the seed 7's twin exactly."""
    description = _described(tmp_path, _plain_table())
    assert main(["generate", f"{description}", "--seed", "7"]) == 0
    plain = _twin_of(description).read_bytes()
    assert (
        main(["generate", f"{description}", "--seed", "007", "--replace"]) == 0
    )
    capsys.readouterr()
    assert _twin_of(description).read_bytes() == plain


def test_the_seed_and_the_run_are_named_in_the_report(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    description = _described(tmp_path, _plain_table())
    assert main(["generate", f"{description}", "--seed", "12345"]) == 0
    capsys.readouterr()
    written = _report_of(description).read_text(encoding="utf-8")
    assert "Seed: 12345." in written


# ---------------------------------------------------------------------
# 2. a name that is already taken (plan P2-D10; no ownership proof)
# ---------------------------------------------------------------------


def test_a_second_run_refuses_and_changes_nothing(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    description = _described(tmp_path, _plain_table())
    assert main(["generate", f"{description}"]) == 0
    capsys.readouterr()
    twin_before = _twin_of(description).read_bytes()
    report_before = _report_of(description).read_bytes()

    assert main(["generate", f"{description}", "--seed", "9"]) == 1
    told = capsys.readouterr().err
    # Both exact paths, whichever of them is in the way.
    assert f"{_twin_of(description)}" in told
    assert f"{_report_of(description)}" in told
    assert "--replace" in told
    assert _twin_of(description).read_bytes() == twin_before
    assert _report_of(description).read_bytes() == report_before


@pytest.mark.parametrize("which", ["twin", "report"])
def test_an_unrelated_file_at_either_name_is_left_untouched(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str], which: str
) -> None:
    """The ownership battery: a default run leaves every byte as it was.

    The file at the name is nobody's twin -- it is a researcher's own
    work that happens to be called that -- and synthtwin has no way of
    telling the two apart, which is exactly why it may not decide.
    """
    description = _described(tmp_path, _plain_table())
    target = (
        _twin_of(description) if which == "twin" else _report_of(description)
    )
    mine = "something of my own that took a week\n"
    target.write_text(mine, encoding="utf-8", newline="\n")

    assert main(["generate", f"{description}"]) == 1
    told = capsys.readouterr().err
    assert f"{target}" in told
    assert target.read_text(encoding="utf-8") == mine
    other = (
        _report_of(description) if which == "twin" else _twin_of(description)
    )
    assert not other.exists(), (
        "a refused run must write neither file, not one of the two"
    )


def test_replace_is_the_one_way_through(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    description = _described(tmp_path, _plain_table())
    _twin_of(description).write_text("older\n", encoding="utf-8", newline="\n")
    assert main(["generate", f"{description}", "--replace"]) == 0
    capsys.readouterr()
    written = _twin_of(description).read_text(encoding="utf-8")
    assert written != "older\n"
    assert _report_of(description).is_file()


def test_the_refusal_offers_no_route_but_replace(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """No proof-of-ownership route exists, so none may be suggested."""
    description = _described(tmp_path, _plain_table())
    _twin_of(description).write_text("older\n", encoding="utf-8", newline="\n")
    assert main(["generate", f"{description}"]) == 1
    told = capsys.readouterr().err
    assert "--replace" in told
    assert "--out-dir" in told
    for absent in ("marker", "recognised", "recognized", "belongs to"):
        assert absent not in told


def test_an_output_that_leads_back_to_the_description_is_refused(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The worst outcome here: writing the twin over what it is built from.

    The two names cannot spell their way onto the description -- one ends
    '-twin.csv' and the other '-twin-report.txt' -- so the route that
    matters is a link left at one of them, which resolves to a perfectly
    local path and passes every lexical check.

    TWO RULES CAN STOP IT, and which one does is the platform's
    business rather than this test's -- the same shape
    `test_a_link_pointing_at_the_table_is_refused` in
    `test_cli_profile.py` keeps for the profile command. On POSIX the
    link resolves to an ordinary local path and the run is stopped by
    the comparison that finds the twin's name and the description are
    one file. On Windows the locality check refuses the link itself,
    before that comparison is reached, because a link there can lead to
    a network location.

    This carried `skipif(sys.platform == "win32")` for two rounds, on
    the reasoning that a link an ordinary user can make is a POSIX
    thing (round 5 item 10). The cost was that the ONE command that
    writes a twin had nothing at all asserted about this route on
    Windows -- the platform with the stricter rule. What every platform
    asserts is the property that matters: the run stops, and the
    description comes out byte for byte what it went in as. Only the
    sentence differs, and each is pinned on the platform whose rule
    produced it.
    """
    description = _described(tmp_path, _plain_table())
    before = description.read_bytes()
    link = _twin_of(description)
    link.symlink_to(description)

    assert main(["generate", f"{description}"]) == 1
    told = capsys.readouterr().err

    assert description.read_bytes() == before, (
        "the description the twin is built from must come out of a "
        "refusal byte-for-byte what it went in as"
    )
    assert not _report_of(description).exists(), (
        "a refused run publishes neither of the two files"
    )
    assert "Traceback" not in told, "the reason must arrive as a sentence"

    if sys.platform == "win32":
        # The stricter rule, and the only place this command reaches it.
        assert "is a link" in told
        assert "network location" in told
        assert link.name in told, (
            "the person has to be told which name is the link"
        )
    else:
        assert f"{description}" in told
        assert "profile" in told, (
            "the refusal names the file THIS command reads"
        )


def test_out_dir_moves_both_files_and_leaves_the_folder_alone(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    description = _described(tmp_path, _plain_table())
    elsewhere = tmp_path / "twins"
    elsewhere.mkdir()
    assert main(["generate", f"{description}", "--out-dir", f"{elsewhere}"]) == 0
    capsys.readouterr()
    assert (elsewhere / "clinic-twin.csv").is_file()
    assert (elsewhere / "clinic-twin-report.txt").is_file()
    assert not _twin_of(description).exists()


def test_a_missing_out_dir_is_refused_in_the_generators_words(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    description = _described(tmp_path, _plain_table())
    assert main(["generate", f"{description}", "--out-dir", "no-such"]) == 1
    told = capsys.readouterr().err
    assert "does not exist" in told
    assert "twin" in told, "the refusal must name the file THIS command writes"


# ---------------------------------------------------------------------
# 3. the header row, both ways (plan P2-D10)
# ---------------------------------------------------------------------


def test_a_named_table_yields_a_twin_with_the_same_names(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    description = _described(tmp_path, _plain_table(rows=48))
    assert main(["generate", f"{description}"]) == 0
    capsys.readouterr()
    written = _twin_of(description).read_text(encoding="utf-8")
    lines = [line for line in written.split("\n") if line]
    assert lines[0] == "region,visits"
    assert len(lines) == 49, "one header row and one row per row of the table"
    # And the twin reads back as a table with those names.
    read = reading.read_table(f"{_twin_of(description)}")
    assert read.column_names == ["region", "visits"]
    assert read.n_rows == 48


def test_a_table_with_no_names_yields_a_twin_with_no_header(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`--first-row data` says the file had no names; the twin has none.

    Writing one anyway would give the twin a row the real table never
    had, and re-describing the twin would then count one row fewer.
    """
    description = _described(
        tmp_path,
        _plain_table(rows=48),
        first_row=reading.FIRST_ROW_DATA,
    )
    assert main(["generate", f"{description}"]) == 0
    capsys.readouterr()
    written = _twin_of(description).read_text(encoding="utf-8")
    lines = [line for line in written.split("\n") if line]
    assert lines[0] != "region,visits"
    assert len(lines) == 49, "no header row, and one row per row of the table"
    read = reading.read_table(
        f"{_twin_of(description)}", reading.FIRST_ROW_DATA
    )
    assert read.n_rows == 49
    written_report = _report_of(description).read_text(encoding="utf-8")
    assert "no line of column names" in written_report


def _words_table(rows: int = 48) -> str:
    """A table of words only, where nothing settles what the first row is.

    Every column holds words, so no column's first-row value stands out
    against the values below it: the reader takes the first row as names
    BY CONVENTION and says so, which is the case the report has to carry.
    """
    made = [
        [fixtures.REGIONS[index % 4], fixtures.LABELS[index % 5]]
        for index in range(rows)
    ]
    return fixtures.rows_to_csv(["region", "site"], made)


def test_a_header_taken_by_convention_is_said_so_in_the_report(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Phase 1's residual R1 travels into the twin, so it is said again.

    Where nothing in the file settled the question, what the twin carries
    as column names may in fact be somebody's first record -- and a
    report saying only "the names were written" would hide it.
    """
    description = _described(tmp_path, _words_table())
    assert main(["generate", f"{description}"]) == 0
    capsys.readouterr()
    written = _report_of(description).read_text(encoding="utf-8")
    assert "ASSUMED to be names" in written
    assert "--first-row data" in written


def test_a_header_read_from_evidence_is_not_called_an_assumption(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The other half: a warning that appears always teaches nothing."""
    description = _described(tmp_path, _plain_table())
    assert main(["generate", f"{description}"]) == 0
    capsys.readouterr()
    written = _report_of(description).read_text(encoding="utf-8")
    assert "ASSUMED to be names" not in written


# ---------------------------------------------------------------------
# 4. the byte-order mark, and the rest of the twin's bytes (method G2)
# ---------------------------------------------------------------------


def _marked_table() -> str:
    """A table whose first column name begins with the byte-order mark.

    The mark sits INSIDE a quoted first field, which is the only way a
    reader can see it as part of a name rather than eat it as the file's
    own mark. Phase 1 publishes such a name, so the generator has to be
    able to write it back.
    """
    rows = [[fixtures.REGIONS[index % 4], f"{index % 7}"] for index in range(24)]
    return fixtures.rows_to_csv([f'"{_MARK}region"', "visits"], rows)


def test_the_producer_really_publishes_the_marked_name(
    tmp_path: pathlib.Path,
) -> None:
    """The premise of the test below, asserted rather than assumed."""
    table_path = fixtures.write(tmp_path, "clinic.csv", _marked_table())
    table = reading.read_table(f"{table_path}")
    assert table.column_names[0] == f"{_MARK}region"


def test_a_marked_first_name_is_quoted_and_survives_the_round_trip(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    description = _described(tmp_path, _marked_table())
    assert main(["generate", f"{description}"]) == 0
    capsys.readouterr()
    raw = _twin_of(description).read_bytes()
    # The file may not BEGIN with the mark, or the reader eats it and
    # the column comes back under a name nobody published.
    assert not raw.startswith(_MARK_BYTES)
    assert raw.startswith(b'"' + _MARK_BYTES)
    # And the whole way round: the reader gives back the published name,
    # character for character.
    read = reading.read_table(f"{_twin_of(description)}")
    assert read.column_names[0] == f"{_MARK}region"


def test_the_twins_bytes_are_utf8_with_newline_endings(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    description = _described(tmp_path, _plain_table())
    assert main(["generate", f"{description}"]) == 0
    capsys.readouterr()
    raw = _twin_of(description).read_bytes()
    assert not raw.startswith(_MARK_BYTES), "no byte-order mark of our own"
    assert b"\r" not in raw, "line endings are newlines on every platform"
    assert raw.endswith(b"\n"), "the last row ends like every other"
    raw.decode("utf-8")


def test_only_a_cell_that_needs_quoting_is_quoted(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Minimal quoting, and a label holding a comma quoted all the same."""
    rows = []
    for index in range(48):
        rows.append(["north, east" if index % 2 else "south", f"{index % 5}"])
    description = _described(
        tmp_path, fixtures.rows_to_csv(["region", "visits"], rows)
    )
    assert main(["generate", f"{description}"]) == 0
    capsys.readouterr()
    written = _twin_of(description).read_text(encoding="utf-8")
    assert '"north, east"' in written
    assert "south," in written, "an ordinary label is written plainly"
    read = reading.read_table(f"{_twin_of(description)}")
    assert "north, east" in read.columns[0]


def test_the_report_names_the_cells_a_spreadsheet_reads_as_a_formula(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The label is written unchanged, counted, and warned about."""
    rows = []
    for index in range(48):
        rows.append(["=total" if index % 2 else "south", f"{index % 5}"])
    description = _described(
        tmp_path, fixtures.rows_to_csv(["region", "visits"], rows)
    )
    assert main(["generate", f"{description}"]) == 0
    printed = capsys.readouterr().out
    written = _twin_of(description).read_text(encoding="utf-8")
    told = _report_of(description).read_text(encoding="utf-8")
    assert "=total" in written, "a published label is never altered"
    assert "'region'" in told
    assert "24" in told
    assert "NOT protection" in told
    # The warning reaches the screen as well as the file, every run.
    assert "reads a cell that begins" in printed


# ---------------------------------------------------------------------
# what the report says on EVERY run (plan P2-D10, P2-D11)
# ---------------------------------------------------------------------


def test_the_report_states_the_same_things_every_run(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    description = _described(tmp_path, _plain_table())
    assert main(["generate", f"{description}"]) == 0
    printed = capsys.readouterr().out
    told = _report_of(description).read_text(encoding="utf-8")
    for wanted in (
        # the seed
        "Seed: 0.",
        # columns generated independently
        "EVERY COLUMN WAS BUILT ON ITS OWN",
        # rows independent, grain undescribed
        "EVERY ROW WAS BUILT ON ITS OWN",
        "never says",
        # not research results
        "NOT RESEARCH RESULTS",
        # the provenance claim, and its one qualification
        "read no",
        "It does NOT say that no row of the twin can equal a row of your",
        # every file a full run leaves behind, and institutional
        # handling (plan amendment A-P3-8: the profiler's summary
        # joined the list)
        "All five files",
        "the plain-language summary beside it",
        "institution",
        # the formula-context warning
        "reads a cell that begins",
        "NOT protection",
        # the teaching chain's middle link: this report passes no
        # verdict, and the command that produces one is named (plan
        # P3-D6). The sentence that used to sit here called a verdict
        # later work, and it is not later work any more.
        "This report passes NO verdict",
        "`synthtwin validate`",
    ):
        assert wanted in told, wanted
    # The same text reaches the screen and the file; neither can say
    # something the other does not.
    assert told in printed


def test_the_report_names_every_fact_the_twin_gave_up(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Achieved beside published, for every deviation the run measured.

    The list is the generator's own measurement, so this drives a real
    run and checks the report against what came back rather than against
    a list written here.
    """
    from synthtwin import contract, generation

    description = _described(tmp_path, _plain_table())
    loaded = contract.load_profile(f"{description}")
    twin = generation.generate(loaded, 0)
    assert main(["generate", f"{description}"]) == 0
    capsys.readouterr()
    told = _report_of(description).read_text(encoding="utf-8")
    for deviation in twin.deviations:
        assert f"'{deviation.column}'" in told
        assert deviation.fact in told
        assert deviation.published in told
        assert deviation.achieved in told
    if not twin.deviations:
        assert "Nothing was given up in this run" in told


def test_the_reports_column_counts_are_counted_from_the_written_twin(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The per-column line names the twin's own counts, so it can be wrong.

    A line restating the description's numbers back could never fail;
    these are recounted from the file that was written, and the check
    recounts them a third time from the same file.
    """
    rows = []
    for index in range(48):
        rows.append(
            [fixtures.REGIONS[index % 4], "" if index % 4 == 0 else f"{index}"]
        )
    description = _described(
        tmp_path, fixtures.rows_to_csv(["region", "visits"], rows)
    )
    assert main(["generate", f"{description}"]) == 0
    capsys.readouterr()
    told = _report_of(description).read_text(encoding="utf-8")
    read = reading.read_table(f"{_twin_of(description)}")
    for place in range(len(read.column_names)):
        cells = read.columns[place]
        present = len([cell for cell in cells if cell != ""])
        empty = len(cells) - present
        assert (
            f"The twin holds {present} value(s) and leaves {empty} cell(s) "
            f"empty" in told
        ), read.column_names[place]


def test_every_role_the_profiler_can_publish_survives_the_whole_command(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """One table carrying a column of nearly every shape, end to end.

    The point is the whole route -- producer, loader, generator, both
    renderers, the write transaction -- over the roles a report has to be
    able to describe: record numbers, categories, counts, measured
    numbers, dates, two-value columns, free text, an empty column, a
    repeated value, and numbers too large for the format to hold.
    """
    text = fixtures.every_role_table()
    lines = [line for line in text.split("\n") if line]
    widened = [f"{lines[0]},huge"]
    for index in range(len(lines) - 1):
        widened = widened + [
            lines[index + 1] + ("," + ("1e999" if index % 2 else "-2e400"))
        ]
    joined = ""
    for line in widened:
        joined = joined + line + "\n"
    description = _described(tmp_path, joined)
    assert main(["generate", f"{description}"]) == 0
    capsys.readouterr()
    read = reading.read_table(f"{_twin_of(description)}")
    assert read.n_rows == 240
    told = _report_of(description).read_text(encoding="utf-8")
    for name in read.column_names:
        assert f"'{name}'" in told, name


def test_a_hostile_name_is_shown_in_the_report_and_kept_in_the_twin(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The two sinks are different sinks, and this is where that shows.

    A column name can carry the bytes a terminal obeys instead of
    printing. The report is read by a person, so the name is SHOWN there
    as text. The twin is read by a program, so the same name is written
    into it exactly as the description publishes it -- escaping it would
    put a value in the twin that nobody ever published.
    """
    clear_the_screen = "\x1b[2J"
    rows = [
        [fixtures.REGIONS[index % 4], f"{index % 7}"] for index in range(48)
    ]
    description = _described(
        tmp_path,
        fixtures.rows_to_csv([f"region{clear_the_screen}", "visits"], rows),
    )
    assert main(["generate", f"{description}"]) == 0
    printed = capsys.readouterr().out
    told = _report_of(description).read_bytes()
    raw = _twin_of(description).read_bytes()
    assert b"\x1b" not in told
    assert b"\\x1b[2J" in told
    assert b"\x1b" not in printed.encode("utf-8", "surrogatepass")
    assert b"region\x1b[2J" in raw, (
        "the twin must hold the name the description publishes, not an "
        "escaped rewriting of it"
    )
    read = reading.read_table(f"{_twin_of(description)}")
    assert read.column_names[0] == f"region{clear_the_screen}"


def test_the_report_says_how_the_real_table_wrote_its_empty_cells(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Absent spellings are not reproduced, so they are named instead."""
    rows = []
    for index in range(48):
        rows.append(
            [fixtures.REGIONS[index % 4], "" if index % 4 == 0 else f"{index}"]
        )
    description = _described(
        tmp_path, fixtures.rows_to_csv(["region", "visits"], rows)
    )
    assert main(["generate", f"{description}"]) == 0
    capsys.readouterr()
    told = _report_of(description).read_text(encoding="utf-8")
    assert "writes every one of them as an empty cell" in told
    # THE BLANKS ARE A COUNT OF THEIR OWN from contract version 5, not a
    # key spelled `(blank)` inside the spellings map (its section 5), so
    # the report says what they were rather than printing one of this
    # package's own words where a spelling goes.
    assert "12 cell(s) with nothing written in them" in told, (
        "the spellings the description publishes are named, because the "
        "twin does not reproduce them"
    )


# ---------------------------------------------------------------------
# the boundary: a generate run never reaches the table reader (P2-D1)
# ---------------------------------------------------------------------


def test_importing_the_command_module_starts_no_reader(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Module initialization is inside the boundary, so it is checked.

    Python runs a module's top-level imports before any branch of it
    exists. While `cli` imported the reader at the top, a `generate` run
    had started pandas before the command word had been looked at, and no
    check drawn after the dispatch could have seen it.
    """
    seen = _watching_imports(monkeypatch)
    importlib.reload(cli)
    for forbidden in ("pandas", "synthtwin.reading", "synthtwin.profile"):
        assert forbidden not in seen, (
            f"importing synthtwin.cli started {forbidden}, so every run "
            f"begins inside the module the generator may never reach"
        )


def test_a_generate_run_never_asks_for_the_reader(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """And the run itself, from the command line to both written files."""
    description = _described(tmp_path, _plain_table())
    seen = _watching_imports(monkeypatch)
    assert main(["generate", f"{description}"]) == 0
    capsys.readouterr()
    for forbidden in ("pandas", "synthtwin.reading", "synthtwin.profile"):
        assert forbidden not in seen, (
            f"a generate run reached for {forbidden}, which is the module "
            f"boundary this command exists inside"
        )
    assert "synthtwin.generation" in seen, (
        "the recorder must be seeing this run's imports at all"
    )


def test_the_parsers_own_words_match_the_modules_that_own_them() -> None:
    """The constants the command line is built from cannot drift.

    They are written out in `cli` because the parser is built before any
    command word has been read and may not start the reader (plan
    P2-D1). That is only safe while they agree with the modules that own
    the values, which is what this checks.
    """
    assert cli._FIRST_ROW_AUTOMATIC == reading.FIRST_ROW_AUTOMATIC
    assert cli._FIRST_ROW_NAMES == reading.FIRST_ROW_NAMES
    assert cli._FIRST_ROW_DATA == reading.FIRST_ROW_DATA
    assert cli._SMALLEST_GROUP == taxonomy.Settings().small_cell_floor


# ---------------------------------------------------------------------
# the command line itself
# ---------------------------------------------------------------------


def test_the_command_word_is_offered_beside_profile(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "synthtwin generate" in out
    assert "synthtwin profile" in out


def test_generate_without_a_path_says_what_to_type(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["generate"])
    assert caught.value.code == 2
    told = capsys.readouterr().err
    assert "synthtwin generate my-table-profile.json" in told


def test_a_description_that_is_not_one_is_refused_in_words(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    not_a_description = fixtures.write(tmp_path, "clinic.csv", "a,b\n1,2\n")
    assert main(["generate", f"{not_a_description}"]) == 1
    told = capsys.readouterr().err
    assert "description" in told
    for jargon in ("Traceback", "JSONDecodeError", "None"):
        assert jargon not in told


def test_a_missing_description_is_refused_in_words(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["generate", f"{tmp_path / 'nothing-profile.json'}"]) == 1
    told = capsys.readouterr().err
    assert "no file" in told or "There is no" in told


# ---------------------------------------------------------------------
# the renderer's own rules, checked where a whole run cannot reach them
# ---------------------------------------------------------------------


def test_a_one_column_row_with_nothing_in_it_is_written_as_two_quotes(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Method G2's second canonical exception, end to end.

    A line with nothing on it is not a row any reader agrees about: the
    shipped reader refuses a one-column file holding one, because it
    cannot tell a record whose only value is missing from a blank line
    somebody left in the file. Two quote characters read back as an empty
    cell, which is what an absent value is.
    """
    # The source table writes its own empty cells as two quote marks,
    # because the reader refuses a one-column file with an empty line for
    # exactly the reason this exception exists.
    lines = "visits"
    for index in range(48):
        lines = lines + "\n" + ('""' if index % 4 == 0 else f"{index}")
    description = _described(tmp_path, lines + "\n")
    assert main(["generate", f"{description}"]) == 0
    capsys.readouterr()
    written = _twin_of(description).read_text(encoding="utf-8")
    assert '""\n' in written
    assert "\n\n" not in written, "an empty line would be refused on the way back"
    read = reading.read_table(f"{_twin_of(description)}")
    assert read.n_rows == 48


def test_the_renderer_quotes_only_what_the_format_requires() -> None:
    """The quoting rule itself, cell by cell, without building a twin."""
    assert rendering._field("plain", False) == "plain"
    assert rendering._field("a,b", False) == '"a,b"'
    assert rendering._field('say "yes"', False) == '"say ""yes"""'
    assert rendering._field("two\nlines", False) == '"two\nlines"'
    assert rendering._field("carriage\rreturn", False) == '"carriage\rreturn"'
    assert rendering._field("plain", True) == '"plain"'
