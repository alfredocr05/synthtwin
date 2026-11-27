"""The start-of-run check (lane SCALE; LANE I4m RULINGS 26 (5)).

Before any hour of work `synthtwin profile`, `generate` and `validate`
weigh what the run will need -- each step's hours and peak memory,
predicted from the table's rows and columns (`synthtwin.sizing`) --
against this computer's installed memory, and STOP before starting where
a step would pass the share of it one step may take, in plain words that
say why and what to do. These cases hold: the prediction against the
lane's measured points (never under a measured peak); the owner's proven
run (2,000,000 rows by 50 columns) let through on an ordinary computer of
8 GB; a table far past it stopped there and let through where the memory
is larger; the glance's estimate of a table's rows and columns from its
opening; and each command's refusal, which writes nothing, beside the run
it leaves unchanged where the memory is enough.
"""

import pathlib

import pytest

import fixtures
from synthtwin import cli, errors, reading, results, sizing
from synthtwin.cli import main

GIB = 1024 ** 3

# THE MEASURED POINTS (lane SCALE's report, dense shape of
# tools/measurements/kpi_inside_scale.py, one process a step on the base of
# the lane, peak resident memory in MiB and wall seconds): (rows, columns,
# step, peak MiB, seconds). The 2,000,000-row points are lane SPEED-2M's
# proof run (report 2), its describe at the 30-second watch's footprint
# and its generate at the guard's one-second sample (4,065 MB), the
# highest each was seen to hold.
MEASURED = (
    (20_000, 50, "profile", 450, 185),
    (20_000, 50, "generate", 144, 55),
    (20_000, 50, "validate", 240, 88),
    (20_000, 50, "checks", 243, 17),
    (100_000, 50, "profile", 817, 903),
    (100_000, 50, "generate", 297, 273),
    (100_000, 50, "validate", 494, 388),
    (100_000, 50, "checks", 539, 36),
    (200_000, 50, "profile", 1423, 1812),
    (200_000, 50, "generate", 640, 545),
    (200_000, 50, "validate", 674, 811),
    (200_000, 50, "checks", 836, 60),
    (500_000, 50, "profile", 1476, 3402),
    (500_000, 50, "generate", 1066, 1410),
    (500_000, 50, "validate", 814, 2168),
    (500_000, 50, "checks", 820, 207),
    (20_000, 150, "profile", 565, 3212),
    (20_000, 150, "generate", 292, 195),
    (20_000, 150, "validate", 430, 368),
    (2_000_000, 50, "profile", 2586, 12866),
    (2_000_000, 50, "generate", 4065, 12493),
    (2_000_000, 50, "validate", 2730, 8977),
    (2_000_000, 50, "checks", 2266, 1121),
)


def _step(name: str) -> sizing.Step:
    for step in sizing.STEPS:
        if step.name == name:
            return step
    raise AssertionError(name)


@pytest.mark.parametrize("rows,columns,name,peak_mib,seconds", MEASURED)
def test_no_measured_peak_is_above_its_prediction(rows, columns, name, peak_mib, seconds):
    need = sizing.need_of(_step(name), rows, columns)
    assert need.peak_bytes >= peak_mib * 1024 * 1024
    # ...and the time is the measured one's order: never under four fifths of it, never past twice and a half it.
    assert 0.8 * seconds <= need.seconds <= 2.5 * seconds


def test_the_prediction_grows_with_the_rows_and_the_columns():
    for step in sizing.STEPS:
        small = sizing.need_of(step, 20_000, 50)
        more_rows = sizing.need_of(step, 2_000_000, 50)
        more_columns = sizing.need_of(step, 20_000, 300)
        assert more_rows.seconds > small.seconds and more_rows.peak_bytes > small.peak_bytes
        assert more_columns.seconds > small.seconds and more_columns.peak_bytes > small.peak_bytes


def test_the_owners_proven_run_fits_an_ordinary_computer_of_eight_gigabytes():
    """2,000,000 rows by 50 columns ran end to end at 4.07 GB at most: an 8 GB computer is never refused it."""
    assert sizing.first_over(sizing.needs_of(2_000_000, 50), 8 * GIB) is None


def test_a_table_far_past_it_is_over_eight_gigabytes_and_fits_more():
    over = sizing.first_over(sizing.needs_of(50_000_000, 50), 8 * GIB)
    assert over is not None
    # ...and the step named is the one needing the most, so the words name what the whole run needs.
    assert over.peak_bytes == max(one.peak_bytes for one in sizing.needs_of(50_000_000, 50))
    assert sizing.first_over(sizing.needs_of(50_000_000, 50), 1024 * GIB) is None


def test_no_limit_is_decided_where_the_memory_was_not_read():
    assert sizing.budget_of(None) is None
    assert sizing.first_over(sizing.needs_of(500_000_000, 500), None) is None


def test_the_budget_is_three_quarters_of_the_installed_memory():
    assert sizing.budget_of(8 * GIB) == 6 * GIB


def test_counts_that_are_not_whole_numbers_are_refused():
    with pytest.raises(TypeError):
        sizing.need_of(sizing.STEPS[0], 2.5, 50)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        sizing.need_of(sizing.STEPS[0], 20_000, True)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        sizing.need_of(sizing.STEPS[0], -1, 50)


def test_the_words_of_a_size_and_a_time():
    assert sizing.gigabytes(6 * GIB) == "6.0 GB"
    assert sizing.hours(30.0) == "under a minute"
    assert sizing.hours(1500.0) == "about 25 minutes"
    assert sizing.hours(12_600.0) == "about 3.5 hours"


# -- the glance ----------------------------------------------------------------------------------


def _written(tmp_path: pathlib.Path, rows: int, columns: int, name: str = "wide.csv") -> pathlib.Path:
    header = ",".join(f"c{k}" for k in range(columns))
    body = "".join(",".join(f"{(row * 7 + k) % 1000}.5" for k in range(columns)) + "\n" for row in range(rows))
    return fixtures.write(tmp_path, name, header + "\n" + body)


def test_the_glance_reads_the_columns_and_about_the_rows(tmp_path):
    table = _written(tmp_path, 30_000, 12)
    seen = reading.glance(str(table))
    assert seen is not None
    assert seen.columns == 12
    assert seen.file_bytes == table.stat().st_size
    assert 29_000 <= seen.rows <= 31_500


def test_the_glance_counts_a_quoted_delimiter_as_no_field(tmp_path):
    table = fixtures.write(tmp_path, "q.csv", 'a,"b,c";d\n1,2\n3,4\n')
    seen = reading.glance(str(table))
    assert seen is not None and seen.columns == 2 and seen.rows == 2


def test_the_glance_gives_nothing_for_a_workbook_a_missing_file_or_one_line(tmp_path):
    package = tmp_path / "book.xlsx"
    package.write_bytes(b"PK\x03\x04,a,b\n1,2,3\n4,5,6\n")
    assert reading.glance(str(package)) is None
    assert reading.glance(str(tmp_path / "absent.csv")) is None
    assert reading.glance(str(fixtures.write(tmp_path, "one.csv", "a,b\n"))) is None


# -- the commands --------------------------------------------------------------------------------


def _tiny_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    """A computer of one megabyte: every step of every table is over its limit."""
    monkeypatch.setattr(cli, "_total_memory", lambda: 1024 * 1024)


def test_profile_stops_before_reading_on_a_computer_too_small_and_writes_nothing(tmp_path, monkeypatch, capsys):
    table = fixtures.write(tmp_path, "clinic.csv", fixtures.every_role_table())
    out = tmp_path / "out"
    out.mkdir()
    _tiny_memory(monkeypatch)
    read: "list[str]" = []
    real = reading.read_table

    def watched(*args, **kwargs):
        read.append("read")
        return real(*args, **kwargs)

    monkeypatch.setattr(reading, "read_table", watched)
    code = main(["profile", str(table), "--out-dir", str(out)])
    said = capsys.readouterr().err
    assert code == 1
    assert not read
    assert sorted(place.name for place in out.iterdir()) == []
    assert "stops here, before the work starts" in said
    assert "would need about" in said and "this computer has 0.0 GB in all" in said
    assert "Nothing was written." in said


def test_profile_runs_as_before_where_the_memory_is_enough(tmp_path, monkeypatch, capsys):
    table = fixtures.write(tmp_path, "clinic.csv", fixtures.every_role_table())
    monkeypatch.setattr(cli, "_total_memory", lambda: 64 * GIB)
    assert main(["profile", str(table)]) == 0
    assert "stops here" not in capsys.readouterr().err
    assert (tmp_path / "clinic-profile.json").is_file()


def test_generate_and_validate_stop_before_their_work_on_a_computer_too_small(tmp_path, monkeypatch, capsys):
    table = fixtures.write(tmp_path, "clinic.csv", fixtures.every_role_table())
    assert main(["profile", str(table)]) == 0
    description = tmp_path / "clinic-profile.json"
    assert main(["generate", str(description), "--seed", "1"]) == 0
    twin = tmp_path / "clinic-twin.csv"
    assert twin.is_file()
    capsys.readouterr()
    before = sorted(place.name for place in tmp_path.iterdir())
    twin_bytes = twin.read_bytes()
    _tiny_memory(monkeypatch)
    assert main(["generate", str(description), "--seed", "1", "--replace"]) == 1
    said = capsys.readouterr().err
    assert "Building the twin would need about" in said and "stops here" in said
    assert main(["validate", str(description), "--replace"]) == 1
    said = capsys.readouterr().err
    assert "Checking the twin would need about" in said and "stops here" in said
    assert sorted(place.name for place in tmp_path.iterdir()) == before
    assert twin.read_bytes() == twin_bytes


def test_the_refusal_is_recorded_as_a_refusal_at_the_memory_step(monkeypatch, capsys):
    monkeypatch.setattr(cli, "_total_memory", lambda: 8 * GIB)
    session = cli._Session(screen=None, ask=None)
    cli._OPEN.sessions.append(session)
    try:
        assert cli._weighed_before_starting("big.csv", 50_000_000, 50, True, cli._JOURNEY_STEPS) is False
    finally:
        cli._OPEN.sessions.remove(session)
    said = " ".join(session.refusal_words)
    assert session.step == results.STEP_MEMORY
    assert "The table big.csv holds about 50,000,000 rows and 50 columns (read from its first lines" in said
    assert "this computer has 8.0 GB in all" in said and "at most 6.0 GB" in said


def test_a_long_run_says_what_each_step_takes_at_a_terminal(monkeypatch, capsys):
    monkeypatch.setattr(cli, "_total_memory", lambda: 64 * GIB)
    monkeypatch.setattr(cli, "_progress_at_a_terminal", lambda stream=1: True)
    assert cli._weighed_before_starting("big.csv", 2_000_000, 50, False, cli._JOURNEY_STEPS) is True
    said = capsys.readouterr().out
    assert "The description big.csv is of a table of 2,000,000 rows and 50 columns." in said
    for step in sizing.STEPS:
        assert step.words in said
    assert "hours" in said and "could not be read" not in said
    monkeypatch.setattr(cli, "_total_memory", lambda: None)
    assert cli._weighed_before_starting("big.csv", 2_000_000, 50, False, cli._JOURNEY_STEPS) is True
    assert "This computer's memory could not be read: if it has less than" in capsys.readouterr().out


def test_a_short_run_says_nothing_more(monkeypatch, capsys):
    monkeypatch.setattr(cli, "_total_memory", lambda: 64 * GIB)
    monkeypatch.setattr(cli, "_progress_at_a_terminal", lambda stream=1: True)
    assert cli._weighed_before_starting("small.csv", 20_000, 12, False, cli._JOURNEY_STEPS) is True
    assert capsys.readouterr().out == ""


def test_an_estimate_is_said_as_one():
    said = errors.too_large_for_this_computer("t.csv", 51_234_567, 52, True, "describing the table", "9.0 GB",
                                              "8.0 GB", "6.0 GB", "12.0 GB", "Nothing was written.")
    assert "about 51,200,000 rows and 52 columns" in said
    said = errors.too_large_for_this_computer("t.csv", 51_234_567, 52, False, "building the twin", "9.0 GB",
                                              "8.0 GB", "6.0 GB", "12.0 GB", "Nothing was written.")
    assert "a table of 51,234,567 rows and 52 columns" in said and "Building the twin would need" in said


def test_every_peak_carries_its_margin(monkeypatch):
    """The predicted peak is a quarter more than the measured parts make it: the side the check errs on."""
    margined = sizing.need_of(sizing.STEPS[1], 2_000_000, 50).peak_bytes
    monkeypatch.setattr(sizing, "MEMORY_MARGIN_PERCENT", 0)
    bare = sizing.need_of(sizing.STEPS[1], 2_000_000, 50).peak_bytes
    assert margined >= bare * 1.24
