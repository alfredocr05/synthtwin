"""The five twin-versus-real checks (`synthtwin.twin_checks`): each catches its own copy, and a clean twin passes all five.

Every table here is invented and drawn from its seed in this file: a
visit table of about 3,000 rows (5 to 8 visits a person), below the
owner's table floor and read with the checks' internal switch off, a
test device as the plan for checks run inside allows (one case shows the
floor refusing it with the switch on). The real table and its twins are
written as CSV files to the test's own folder.

Into a clean twin -- an independent draw of the same invented process,
its keys and record numbers made up under another prefix -- each case
puts one kind of copy and asks that its check fire: a copied row (C1), a
row moved by a hair (C2), a copied patient's readings or dates (C3), a
leaked record number, a leaked person key written another way, leaked
timestamps, an age past 90 and a copied remark naming a relative (C4),
and copied rare combinations (C5). The clean twin passes all five, and
no report prints a cell of the real table. Each case names the mutant
of `synthtwin.twin_checks` it is red on.
"""

from __future__ import annotations

import csv
import pathlib
import random

import pytest

from synthtwin import errors, twin_checks

HEADER = ["patient_id", "visit_time", "age", "ward", "outcome", "pulse", "lab_a", "record_no", "remark"]
PEOPLE = 500
WARDS = ["north", "south", "east", "west", "day unit"]
OUTCOMES = ["home", "transfer", "rehab"]
RELATIVES_REAL = ["Talvo Brisk", "Merin Oakhart", "Pell Durrow"]
RELATIVES_TWIN = ["Corva Lindt", "Abel Sorrow", "Inka Wendt"]
SECONDS_SPAN = 3 * 365 * 86400


def _stamp(rng: random.Random) -> str:
    second = rng.randrange(SECONDS_SPAN)
    day = second // 86400
    year = 2030 + day // 365
    day_of_year = day % 365
    month = min(day_of_year // 31 + 1, 12)
    day_of_month = day_of_year % 28 + 1
    clock = second % 86400
    return f"{year:04d}-{month:02d}-{day_of_month:02d} {clock // 3600:02d}:{clock // 60 % 60:02d}:{clock % 60:02d}"


def _visits(seed: int, prefix: str, relatives: "list[str]", ages: "tuple[int, int]" = (18, 88)) -> "list[list[str]]":
    """An invented visit table: a person's key, a visit stamp to the second, an age, two labels, two readings, a record number, a remark."""
    rng = random.Random(seed)
    rows: "list[list[str]]" = []
    for person in range(PEOPLE):
        key = f"{prefix}{person:06d}"
        age = rng.randint(*ages)
        ward = rng.choice(WARDS)
        level = 60 + rng.gauss(0, 8)
        for _ in range(rng.randint(5, 8)):
            if rng.random() < 0.01:
                remark = f"son {rng.choice(relatives)} to call back"
            elif rng.random() < 0.6:
                remark = "no change"
            else:
                remark = f"review in {rng.randint(1, 60)} days, plan {rng.randint(1, 9)}"
            rows += [
                [
                    key,
                    _stamp(rng),
                    str(age),
                    ward,
                    rng.choice(OUTCOMES),
                    f"{level + rng.gauss(0, 5):.1f}",
                    f"{rng.lognormvariate(0, 0.5):.3f}",
                    f"{prefix}R{rng.randrange(10**8, 10**9)}",
                    remark,
                ]
            ]
    return rows


def _write(path: pathlib.Path, rows: "list[list[str]]", header: "list[str]" = HEADER) -> str:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    return f"{path}"


def _checked(folder: pathlib.Path, real: "list[list[str]]", twin: "list[list[str]]", **given: object) -> twin_checks.Outcome:
    real_path = _write(folder / "real.csv", real)
    twin_path = _write(folder / "twin.csv", twin)
    return twin_checks.run_checks(real_path, twin_path, small_tables_refused=False, **given)


def _verdicts(outcome: twin_checks.Outcome) -> "dict[str, bool]":
    return {check.code: check.passed for check in outcome.checks}


@pytest.fixture(scope="module")
def real() -> "list[list[str]]":
    return _visits(1, "P", RELATIVES_REAL)


@pytest.fixture(scope="module")
def clean() -> "list[list[str]]":
    return _visits(2, "Q", RELATIVES_TWIN)


def _copy(rows: "list[list[str]]") -> "list[list[str]]":
    return [list(row) for row in rows]


def test_a_clean_twin_passes_every_check(tmp_path: pathlib.Path, real, clean) -> None:
    """An independent draw passes all five, each measured. Red on: C5's rare combination read as any combination (`counts[1][digest] == 1` made `>= 1`); the fresh rate read as 0."""
    outcome = _checked(tmp_path, real, clean)
    assert _verdicts(outcome) == {"C1": True, "C2": True, "C3": True, "C4": True, "C5": True}
    assert all(check.measured for check in outcome.checks)
    assert outcome.passed
    assert outcome.person_column == "patient_id"
    assert outcome.kinds == ("identifier", "date", "number", "label", "label", "number", "number", "identifier", "text")


def test_c1_counts_a_copied_row(tmp_path: pathlib.Path, real, clean) -> None:
    """Three real rows' content under the twin's own keys and record numbers: C1 fails. Red on: the fresh rate read from the twin's own rows (the baseline the wrong one)."""
    twin = _copy(clean)
    for at in range(3):
        twin[at * 50] = [twin[at * 50][0]] + real[at * 70][1:7] + [twin[at * 50][7], real[at * 70][8]]
    outcome = _checked(tmp_path, real, twin)
    assert _verdicts(outcome)["C1"] is False
    assert outcome.checks[0].lines[0].startswith("3 of ")


def test_c1_does_not_count_a_row_one_column_away(tmp_path: pathlib.Path, real, clean) -> None:
    """Real rows' content with the visit stamp moved by a day is no exact copy: C1 passes. Red on: the row's digest skipping the date columns (the hash skipping a column)."""
    twin = _copy(clean)
    for at in range(3):
        moved = real[at * 70][1].replace("-01 ", "-02 ") if "-01 " in real[at * 70][1] else "2033-01-01 00:00:01"
        twin[at * 50] = [twin[at * 50][0], moved] + real[at * 70][2:7] + [twin[at * 50][7], real[at * 70][8]]
    outcome = _checked(tmp_path, real, twin)
    assert _verdicts(outcome)["C1"] is True
    assert outcome.checks[0].lines[0].startswith("0 of ")


def test_c2_catches_rows_moved_by_a_hair(tmp_path: pathlib.Path, real, clean) -> None:
    """One twin row in fifty is a real row with its readings moved by a hair, so no row is an exact copy: C1 passes and C2 fails. Red on: the twin's nearest record sought in no half (its distances read as the fresh half's)."""
    twin = _copy(clean)
    for at in range(0, len(twin), 50):
        source = real[at % len(real)]
        pulse = f"{float(source[5]) + 0.1:.1f}"
        lab = f"{float(source[6]) + 0.001:.3f}"
        twin[at] = [twin[at][0], source[1], source[2], source[3], source[4], pulse, lab, twin[at][7], source[8]]
    outcome = _checked(tmp_path, real, twin)
    verdicts = _verdicts(outcome)
    assert verdicts["C1"] is True
    assert verdicts["C2"] is False


def test_c2_reads_the_dates(tmp_path: pathlib.Path, real, clean) -> None:
    """Real rows' readings and labels with their stamps moved by about two years are no near copy: C2 passes. Red on: the distance ignoring the date columns."""
    twin = _copy(clean)
    for at in range(0, len(twin), 50):
        source = real[at % len(real)]
        year = int(source[1][:4])
        moved = f"{year + 2 if year < 2031 else year - 2:04d}" + source[1][4:]
        twin[at] = [twin[at][0], moved] + source[2:7] + [twin[at][7], source[8]]
    outcome = _checked(tmp_path, real, twin)
    assert _verdicts(outcome)["C2"] is True


def _real_patient(real: "list[list[str]]", key: str) -> "list[list[str]]":
    return [row for row in real if row[0] == key]


def _swap_patient(clean: "list[list[str]]", key: str, rows: "list[list[str]]") -> "list[list[str]]":
    kept = [row for row in clean if row[0] != key]
    return kept + rows


def test_c3_catches_a_copied_patient_in_another_order(tmp_path: pathlib.Path, real, clean) -> None:
    """A real patient's readings and stamps, rows reversed, under a twin key and the twin's own labels and remarks: C3 fails on readings and on dates. Red on: a patient's rows read in their order rather than as a set."""
    source = _real_patient(real, "P000003")
    own = _real_patient(clean, "Q000003")
    made = []
    for at in range(len(source)):
        row = source[len(source) - 1 - at]
        mine = own[at % len(own)]
        made += [["Q000003", row[1], row[2], mine[3], mine[4], row[5], row[6], f"QR{900000000 + at}", mine[8]]]
    outcome = _checked(tmp_path, real, _swap_patient(clean, "Q000003", made))
    patient = outcome.checks[2]
    assert patient.passed is False
    assert patient.lines[0].startswith("On readings: 1 of ")
    assert patient.lines[2].startswith("On dates: 1 of ")


def test_c3_catches_a_copied_date_list_alone(tmp_path: pathlib.Path, real, clean) -> None:
    """A real patient's stamps alone, under a twin key with the twin's own readings: C3 fails on dates and passes on readings. Red on: the date digests left out of the patient's signature."""
    source = _real_patient(real, "P000007")
    own = _real_patient(clean, "Q000007")
    made = []
    for at in range(len(source)):
        mine = own[at % len(own)]
        made += [["Q000007", source[at][1]] + mine[2:7] + [f"QR{910000000 + at}", mine[8]]]
    outcome = _checked(tmp_path, real, _swap_patient(clean, "Q000007", made))
    patient = outcome.checks[2]
    assert patient.passed is False
    assert patient.lines[0].startswith("On readings: 0 of ")
    assert patient.lines[2].startswith("On dates: 1 of ")


def test_c4_catches_a_leaked_record_number(tmp_path: pathlib.Path, real, clean) -> None:
    """One twin record number equal to a real one: C4 fails and names one cell. Red on: identifier cells looked up in an empty set."""
    twin = _copy(clean)
    twin[10][7] = real[25][7]
    outcome = _checked(tmp_path, real, twin)
    identifiers = outcome.checks[3]
    assert identifiers.passed is False
    assert "Identifier column record_no: 1 twin cells equal a real one." in identifiers.lines


def test_c4_reads_a_person_key_written_another_way(tmp_path: pathlib.Path, real, clean) -> None:
    """A twin person key `p-000012` where the real table writes `P000012`: one key, so C4 fails. Red on: keys compared as folded text rather than by `parsing.merged_key`."""
    twin = [["p-000012"] + row[1:] if row[0] == "Q000012" else row for row in clean]
    outcome = _checked(tmp_path, real, twin)
    lines = outcome.checks[3].lines
    assert outcome.checks[3].passed is False
    assert any(line.startswith("Identifier column patient_id: ") and not line.endswith(": 0 twin cells equal a real one.") for line in lines)


def test_c4_catches_leaked_timestamps(tmp_path: pathlib.Path, real, clean) -> None:
    """One twin stamp in twenty copied from the real table, each held by one person: C4 fails on the date column. Red on: no date read as rare (held by at most 0 people)."""
    twin = _copy(clean)
    for at in range(0, len(twin), 20):
        twin[at][1] = real[at % len(real)][1]
    outcome = _checked(tmp_path, real, twin)
    dates = [line for line in outcome.checks[3].lines if line.startswith("Date column visit_time: ")]
    assert outcome.checks[3].passed is False
    assert dates and not dates[0].startswith("Date column visit_time: 0 of ")


def test_c4_catches_an_age_past_the_top_code(tmp_path: pathlib.Path, real, clean) -> None:
    """One twin age of 95 in a column named as an age: C4 fails. Red on: the top read as 100."""
    twin = _copy(clean)
    twin[5][2] = "95"
    outcome = _checked(tmp_path, real, twin)
    assert outcome.checks[3].passed is False
    assert "Age column age: 1 twin cells past 90." in outcome.checks[3].lines


def test_c4_catches_a_copied_remark_naming_a_relative(tmp_path: pathlib.Path, real, clean) -> None:
    """A real remark naming a relative, copied into the twin: C4 fails; the twin's own remarks name other people and pass. Red on: no text cell read as a person's details."""
    remark = next(row[8] for row in real if row[8].startswith("son "))
    twin = _copy(clean)
    twin[40][8] = remark
    outcome = _checked(tmp_path, real, twin)
    assert outcome.checks[3].passed is False
    assert "Text column remark: 1 twin cells equal a real cell holding a person's details." in outcome.checks[3].lines


RARE_HEADER = ["person", "age", "ward", "outcome", "unit", "pulse"]


def _rare_table(seed: int, prefix: str, rare: bool) -> "list[list[str]]":
    """An invented table of few combinations (ages 30 to 34, three wards, two outcomes, two units), and, where ``rare``, twelve rows each holding a unit no other row holds."""
    rng = random.Random(seed)
    rows: "list[list[str]]" = []
    for person in range(3000):
        rows += [
            [
                f"{prefix}{person:06d}",
                str(rng.randint(30, 34)),
                rng.choice(WARDS[:3]),
                rng.choice(OUTCOMES[:2]),
                rng.choice(["u1", "u2"]),
                f"{60 + rng.gauss(0, 8):.1f}",
            ]
        ]
    if rare:
        for at in range(12):
            rows[at * 200][4] = f"x{at:02d}"
    return rows


def test_c5_catches_copied_rare_combinations(tmp_path: pathlib.Path) -> None:
    """Thirty-six twin rows holding the twelve combinations one real row each holds: C5 fails; the clean twin passes. Red on: a twin row read against no half's unique combinations."""
    real = _rare_table(1, "P", True)
    clean = _rare_table(2, "Q", False)
    real_path = _write(tmp_path / "real.csv", real, RARE_HEADER)
    clean_path = _write(tmp_path / "clean.csv", clean, RARE_HEADER)
    passing = twin_checks.run_checks(real_path, clean_path, small_tables_refused=False)
    assert passing.checks[4].passed is True
    twin = _copy(clean)
    for at in range(36):
        source = real[(at % 12) * 200]
        twin[at * 50] = [twin[at * 50][0], source[1], source[2], source[3], source[4], twin[at * 50][5]]
    twin_path = _write(tmp_path / "twin.csv", twin, RARE_HEADER)
    failing = twin_checks.run_checks(real_path, twin_path, small_tables_refused=False)
    assert failing.checks[4].passed is False
    assert failing.checks[4].lines[0].startswith("12 combinations of 4 columns are held by one real row; 36 twin rows")


def test_no_report_prints_a_real_cell(tmp_path: pathlib.Path, real, clean) -> None:
    """The report of a twin with a leaked record number, leaked stamps and a copied row names no real key, record number, stamp or remark naming a relative."""
    twin = _copy(clean)
    twin[10][7] = real[25][7]
    for at in range(0, len(twin), 20):
        twin[at][1] = real[at % len(real)][1]
    twin[30] = [twin[30][0]] + real[31][1:7] + [twin[30][7], real[31][8]]
    text = twin_checks.report_text(_checked(tmp_path, real, twin))
    for row in real:
        for cell in (row[0], row[1], row[7]):
            assert cell not in text
        if row[8].startswith("son "):
            assert row[8] not in text


def test_the_floor_refuses_a_small_real_table(tmp_path: pathlib.Path, real, clean) -> None:
    """With the switch on, as the command runs, a real table under 20,000 rows is refused, one row a person or several, and nothing is checked. Red on: the floor's row test removed."""
    real_path = _write(tmp_path / "real.csv", real)
    twin_path = _write(tmp_path / "twin.csv", clean)
    with pytest.raises(errors.ProfileError, match="table floor"):
        twin_checks.run_checks(real_path, twin_path)
    single_path = _write(tmp_path / "single.csv", _rare_table(1, "P", False), RARE_HEADER)
    other_path = _write(tmp_path / "other.csv", _rare_table(2, "Q", False), RARE_HEADER)
    with pytest.raises(errors.ProfileError, match="table floor"):
        twin_checks.run_checks(single_path, other_path)


def test_the_floor_refuses_too_few_people(tmp_path: pathlib.Path) -> None:
    """With the switch on, 20,700 rows of 900 people are refused: where one person has several rows, the floor counts 1,000 people. Red on: the floor's people test removed."""
    rng = random.Random(5)
    rows = [[f"P{person:05d}", f"{rng.gauss(60, 8):.1f}", rng.choice(WARDS)] for person in range(900) for _ in range(23)]
    real_path = _write(tmp_path / "real.csv", rows, ["patient_id", "pulse", "ward"])
    with pytest.raises(errors.ProfileError, match="1,000 people"):
        twin_checks.run_checks(real_path, real_path)


def test_the_quarantine_takes_a_failing_twin_and_the_release_a_passing_one(tmp_path: pathlib.Path, real, clean) -> None:
    """A failing twin goes to the quarantine folder under its attempt's name with its report, never to the release folder; a redraw is allowed until the third; a passing twin is released. Red on: the two folders swapped."""
    real_path = _write(tmp_path / "real.csv", real)
    leaked = _copy(clean)
    leaked[10][7] = real[25][7]
    out = tmp_path / "out"
    held = tmp_path / "held"
    twin_path = _write(tmp_path / "twin.csv", leaked)
    done = twin_checks.release(real_path, twin_path, f"{out}", f"{held}", small_tables_refused=False)
    assert done.released == ""
    assert pathlib.Path(done.quarantined) == held / "twin-attempt-0.csv"
    assert (held / "twin-attempt-0-checks.txt").read_text(encoding="utf-8").endswith("The twin is not released.\n")
    assert done.redraw_allowed is True
    assert list(out.iterdir()) == [] if out.exists() else True
    third = _write(tmp_path / "twin.csv", leaked)
    last = twin_checks.release(real_path, third, f"{out}", f"{held}", attempt=3, small_tables_refused=False)
    assert last.redraw_allowed is False
    with pytest.raises(ValueError):
        twin_checks.release(real_path, third, f"{out}", f"{held}", attempt=4, small_tables_refused=False)
    with pytest.raises(ValueError):
        twin_checks.release(real_path, third, f"{held}", f"{held}", small_tables_refused=False)
    passing = _write(tmp_path / "twin.csv", clean)
    good = twin_checks.release(real_path, passing, f"{out}", f"{held}", attempt=1, small_tables_refused=False)
    assert pathlib.Path(good.released) == out / "twin.csv"
    assert (out / "twin-checks.txt").exists()
    assert not pathlib.Path(passing).exists()


def test_the_command_writes_the_report_and_says_the_verdict_by_its_code(tmp_path: pathlib.Path, real, clean) -> None:
    """`python -m synthtwin.twin_checks REAL TWIN --report FILE`: 0 for a clean twin, 3 for a leaked one, 2 for a seed in words; the report written. Red on: the exit code read from the first check alone."""
    real_path = _write(tmp_path / "real.csv", real)
    twin_path = _write(tmp_path / "twin.csv", clean)
    report = tmp_path / "report.txt"
    assert twin_checks.main([real_path, twin_path, "--report", f"{report}"], small_tables_refused=False) == 0
    assert report.read_text(encoding="utf-8").endswith("the twin may be released.\n")
    leaked = _copy(clean)
    leaked[5][2] = "97"
    leaked_path = _write(tmp_path / "leaked.csv", leaked)
    assert twin_checks.main([real_path, leaked_path], small_tables_refused=False) == 3
    assert (tmp_path / "leaked-checks.txt").read_text(encoding="utf-8").endswith("The twin is not released.\n")
    assert twin_checks.main([real_path, twin_path, "--seed", "one"], small_tables_refused=False) == 2


def test_a_plan_given_is_read_as_the_checks_read_one(tmp_path: pathlib.Path, real, clean) -> None:
    """THE SEAM: a plan made from roles a caller holds gives the read plan's outcome, and an answer that a column is no identifier is kept. Red on: a given plan's kinds set aside."""
    leaked = _copy(clean)
    leaked[10][7] = real[25][7]
    roles = {
        "patient_id": "identifier",
        "visit_time": "date",
        "age": "age",
        "ward": "label",
        "outcome": "label",
        "pulse": "number",
        "lab_a": "number",
        "record_no": "identifier",
        "remark": "text",
    }
    read = _checked(tmp_path, real, leaked)
    given = _checked(tmp_path, real, leaked, plan=twin_checks.plan_from_roles(HEADER, roles, "patient_id"))
    assert twin_checks.report_lines(given) == twin_checks.report_lines(read)
    roles["record_no"] = "not identifier"
    answered = _checked(tmp_path, real, leaked, plan=twin_checks.plan_from_roles(HEADER, roles, "patient_id"))
    assert not any(line.startswith("Identifier column record_no") for line in answered.checks[3].lines)
    with pytest.raises(ValueError):
        twin_checks.plan_from_roles(HEADER, {"ward": "colour"})


def test_the_same_files_give_the_same_report(tmp_path: pathlib.Path, real, clean) -> None:
    """Two runs on the same files and seed print the same bytes; another seed splits the halves another way."""
    first = twin_checks.report_text(_checked(tmp_path, real, clean))
    second = twin_checks.report_text(_checked(tmp_path, real, clean))
    third = twin_checks.report_text(_checked(tmp_path, real, clean, seed=7))
    assert first == second
    assert first != third


def test_readers_of_dates_and_numbers() -> None:
    """The normal spellings the checks compare by: a date with or without its clock, a number at its own places."""
    assert twin_checks.read_date("2031-03-14").spelling == "2031-03-14"
    assert twin_checks.read_date("03/14/2031 9:15 PM").spelling == "2031-03-14 76500"
    assert twin_checks.read_date("2031-03-14T21:15:00").spelling == "2031-03-14 76500"
    assert twin_checks.read_date("2031-02-30") is None
    assert twin_checks.read_date("14 March") is None
    assert twin_checks.read_number("007.50").spelling == "7.5"
    assert twin_checks.read_number("-0.0").spelling == "0"
    assert twin_checks.read_number("(1,234.50)").spelling == "-1234.5"
    assert twin_checks.read_number("12 kg") is None
    assert twin_checks.read_number("1e3").value == 1000.0
