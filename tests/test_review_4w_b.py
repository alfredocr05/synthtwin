"""Gate file of the batch 4w review's fix round, worker B: items 3 to 9, 17 and 18 of the outside review.

Each case rebuilds the reviewer's probe on an invented table at the table
floor (20,000 rows), through the real functions (`twin_checks.run_checks`,
`twin_checks.main`, `twin_checks.release`, `inside.place_refusal`,
`inside.write_record`, `inside.export_manifest`), and is red on the
integration head b9165d2d and on the mutant its docstring names:

* item 3: a short list of persons' names under a neutral heading is an
  identifier column, which C4 reads; service words stay labels;
* item 4: a real relative's name kept inside a remark worded another way
  is counted by C4; a capitalised phrase beside it is not;
* item 5: a date read at its calendar day: midnight added, a clock added,
  a clocked cell on a day the real table writes alone;
* item 6: a real person's history written twice is a copied patient;
* item 7: a temporary folder or a mount root spelled with other capitals
  is the same folder on a case-blind volume;
* item 8: the writer holds the loader's bound, and a marked file past it
  is still a marked file the export leaves behind;
* item 9: the report never writes over an input, and every place is
  validated before anything is read;
* item 17: very large finite numbers neither break nor flatten C2;
* item 18: `1e3` and `1000` are one spelling.

Every table, name and value here is invented.
"""

from __future__ import annotations

import csv
import math
import os
import pathlib
import random

import pytest

from synthtwin import inside, installation, twin_checks
from synthtwin.paths import PathValidationError

ROWS = 20000
WARDS = ["north", "south", "east"]
NAMES_REAL = ["Talvo Brisk", "Merin Oakhart", "Pellar Durrow"]
GIVEN_REAL = ["Talvo", "Merin", "Pellar", "Corvin", "Abelin", "Inkar"]
FAMILY_REAL = ["Brisk", "Oakhart", "Durrow", "Lindqvar", "Sorrell"]
GIVEN_TWIN = ["Darvel", "Velka", "Kasmir", "Lumen", "Orrin", "Senna"]
FAMILY_TWIN = ["Wendmar", "Haskel", "Tolvane", "Prendal", "Quillon"]


def _write(path: pathlib.Path, header: "list[str]", rows: "list[list[str]]") -> str:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    return f"{path}"


def _checked(folder: pathlib.Path, header: "list[str]", real: "list[list[str]]", twin: "list[list[str]]",
             name: str = "twin", **given: object) -> twin_checks.Outcome:
    real_path = _write(pathlib.Path(folder, "real.csv"), header, real)
    twin_path = _write(pathlib.Path(folder, name + ".csv"), header, twin)
    return twin_checks.run_checks(real_path, twin_path, **given)  # type: ignore[arg-type]


def _verdicts(outcome: twin_checks.Outcome) -> "dict[str, bool]":
    return {check.code: check.passed for check in outcome.checks}


# -- item 3: a short list of persons' names --------------------------------------------------------------


def test_item_3_a_short_list_of_persons_names_is_an_identifier_column(tmp_path: pathlib.Path) -> None:
    """Three persons' names cycled over 20,000 rows under a neutral heading, copied into the twin: C4 reads the column as an identifier and fails; the twin's own made-up names pass; the person's answer sets it aside; service words stay labels. Red on b9165d2d (read as labels, C4 not measured) and on two mutants: the short list accepted as labels unread (`if free:` made `if False:` in `_kind_of`), and a name read whole with no ordinary-name test (the control's service words then read as names)."""
    header = ["tag", "ward", "score"]
    assert not twin_checks.named_as_an_identifier("tag")
    rng = random.Random(1)
    real = [[NAMES_REAL[at % 3], rng.choice(WARDS), f"{rng.gauss(50, 10):.1f}"] for at in range(ROWS)]
    rng = random.Random(2)
    twin = [[NAMES_REAL[at % 3], rng.choice(WARDS), f"{rng.gauss(50, 10):.1f}"] for at in range(ROWS)]
    copied = _checked(tmp_path, header, real, twin)
    assert copied.kinds == ("identifier", "label", "number")
    assert copied.checks[3].measured and not copied.checks[3].passed
    assert "Identifier column tag: 20000 twin cells equal a real one." in copied.checks[3].lines
    others = ["Darvel Wendmar", "Velka Haskel", "Kasmir Tolvane"]
    made_up = [[others[at % 3]] + row[1:] for at, row in enumerate(twin)]
    assert _verdicts(_checked(tmp_path, header, real, made_up, "made-up")) == dict.fromkeys(("C1", "C2", "C3", "C4", "C5"), True)
    answered = _checked(tmp_path, header, real, twin, "answered", not_identifiers=("tag",))
    assert answered.kinds[0] == "label" and answered.passed
    services = ["Day Unit", "Intensive Care", "General Medicine"]
    labelled = _checked(tmp_path, header, [[services[at % 3]] + row[1:] for at, row in enumerate(real)],
                        [[services[(at + 1) % 3]] + row[1:] for at, row in enumerate(twin)], "services")
    assert labelled.kinds == ("label", "label", "number") and labelled.passed


def test_item_3_the_listed_reader() -> None:
    """The reader of a list's values: persons' names and identifier words count; service, flag and status words do not. Red on the mutant without the ordinary-name test."""
    for value in ("Talvo Brisk", "Merin Oakhart", "Dr. Okafor", "call 319-555-0142"):
        assert twin_checks.a_listed_detail(value), value
    for value in ("Day Unit", "Intensive Care", "General Medicine", "Not Recorded", "Never Smoker", "north", "Home"):
        assert not twin_checks.a_listed_detail(value), value


# -- item 4: a relative's name inside other words ----------------------------------------------------------


def _remarks(seed: int, prefix: str, given: "list[str]", family: "list[str]", beside: str = "") -> "list[list[str]]":
    """An invented table of 2,000 people by 10 rows: a person key, a pulse and a remark, about one remark in a hundred naming the person's son."""
    rng = random.Random(seed)
    rows: "list[list[str]]" = []
    for at in range(ROWS):
        draw = rng.random()
        if draw < 0.01:
            remark = f"son {rng.choice(given)} {rng.choice(family)} to call back{beside}"
        elif draw < 0.6:
            remark = "no change"
        else:
            remark = f"review in {rng.randint(1, 60)} days, plan {rng.randint(1, 9)}"
        rows += [[f"{prefix}{at // 10:05d}", f"{rng.gauss(70, 9):.1f}", remark]]
    return rows


REMARK_HEADER = ["patient_id", "pulse", "remark"]


def test_item_4_a_relatives_name_in_other_words_is_counted(tmp_path: pathlib.Path) -> None:
    """One twin remark keeps a real son's name in other words (`please ring son ... today`): C4 counts it and fails, where it counted 0 whole cells; a clean twin counts 0. Red on b9165d2d (C4 passed) and on the mutant whose element count is always 0 (`_cells_meeting` returning 0)."""
    real = _remarks(1, "P", GIVEN_REAL, FAMILY_REAL)
    twin = _remarks(2, "Q", GIVEN_TWIN, FAMILY_TWIN)
    clean = _checked(tmp_path, REMARK_HEADER, real, twin, person="patient_id")
    assert clean.passed
    assert "Text column remark: 0 twin cells hold a name or a number of a real cell holding a person's details." in clean.checks[3].lines
    held = next(row[2] for row in real if row[2].startswith("son "))
    name = held[len("son "): -len(" to call back")]
    twin[40][2] = f"please ring son {name} today"
    assert twin_checks.a_persons_detail(held) and twin_checks.a_persons_detail(twin[40][2])
    reworded = _checked(tmp_path, REMARK_HEADER, real, twin, "reworded", person="patient_id")
    assert not reworded.checks[3].passed
    assert "Text column remark: 0 twin cells equal a real cell holding a person's details." in reworded.checks[3].lines
    assert "Text column remark: 1 twin cells hold a name or a number of a real cell holding a person's details." in reworded.checks[3].lines
    twin[40][2] = f"{name.split()[1]}, {name.split()[0]} rang back"
    assert not _checked(tmp_path, REMARK_HEADER, real, twin, "family-first", person="patient_id").checks[3].passed


def test_item_4_a_capitalised_phrase_beside_a_name_is_no_element(tmp_path: pathlib.Path) -> None:
    """The real remarks name a son beside a capitalised phrase (`... at Blood Bank`); the twin's own remarks name other people beside the same phrase: no element is met and C4 passes. Red on the mutant that holds every capitalised stretch of a real remark (`held` read as not held in `_held_elements`)."""
    real = _remarks(1, "P", GIVEN_REAL, FAMILY_REAL, " at Blood Bank")
    twin = _remarks(2, "Q", GIVEN_TWIN, FAMILY_TWIN, " at Blood Bank")
    outcome = _checked(tmp_path, REMARK_HEADER, real, twin, person="patient_id")
    assert "Text column remark: 0 twin cells hold a name or a number of a real cell holding a person's details." in outcome.checks[3].lines
    assert outcome.checks[3].passed


def test_item_4_the_elements_of_a_cell() -> None:
    """What a held cell gives and what a looked-up cell meets: names after a relative word or a title, a comma's family name first, numbers of seven figures or more across their marks; one capitalised word alone is no held element."""
    assert twin_checks.elements("son Talvo Brisk to call back", True) == frozenset({"talvo brisk"})
    assert twin_checks.elements("Son Talvo Brisk called", True) == frozenset({"talvo brisk"})
    assert twin_checks.elements("Brisk, Talvo rang", True) == frozenset({"brisk talvo", "talvo brisk"})
    assert twin_checks.elements("son Talvo Brisk at Blood Bank", True) == frozenset({"talvo brisk"})
    assert twin_checks.elements("wife Mara notified", True) == frozenset()
    assert twin_checks.elements("call (319) 555-0142 today", True) == frozenset({"#3195550142"})
    assert twin_checks.elements("ring Talvo Brisk", False) >= frozenset({"talvo", "brisk", "talvo brisk"})
    assert twin_checks.elements("phone 319 555 0142", False) == frozenset({"#3195550142"})


# -- item 5: a date at its calendar day ---------------------------------------------------------------------


def _days(count: int, year: int) -> "list[str]":
    """`count` consecutive invented calendar days from 1 January of `year`."""
    lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    found: "list[str]" = []
    month, day = 1, 1
    for _ in range(count):
        found += [f"{year:04d}-{month:02d}-{day:02d}"]
        leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        day += 1
        if day > (29 if month == 2 and leap else lengths[month - 1]):
            day, month = 1, month + 1
            if month > 12:
                month, year = 1, year + 1
    return found


def test_item_5_midnight_or_a_clock_added_hides_no_real_day(tmp_path: pathlib.Path) -> None:
    """20,000 real days each held once, the twin repeating them with midnight added, then with a clock added, its label column changed: C4 counts every cell and fails. Red on b9165d2d (0 counted) and on the mutant without item 5's three readings (midnight read as a clock, no column read at its calendar day, no twin cell looked up by its day); each reading alone is pinned by the three cases below."""
    days = _days(ROWS, 1960)
    rng = random.Random(1)
    real = [[days[at], rng.choice(WARDS)] for at in range(ROWS)]
    for clock in (" 00:00:00", "T00:00", " 13:47"):
        outcome = _checked(tmp_path, ["event_date", "ward"], real, [[day + clock, "west"] for day in days])
        assert not outcome.checks[3].passed, clock
        assert outcome.checks[3].lines[0].startswith("Date column event_date: 20000 of 20000 "), clock


def test_item_5_midnight_stamps_and_plain_days_are_one_date(tmp_path: pathlib.Path) -> None:
    """A column of clocked stamps, half of them at midnight on days of their own; the twin writes those days plain: C4 counts them and fails. Red on b9165d2d and on the mutant reading midnight as a clock (`found if found > 0 else -1` made `found`)."""
    zero_clocks = [day + " 00:00" for day in _days(ROWS // 2, 1960)]
    stamps = [f"{day} {1 + (at * 7) % 23:02d}:{(at * 13) % 60:02d}" for at, day in enumerate(_days(ROWS // 2, 2001))]
    rng = random.Random(1)
    real = [[cell, rng.choice(WARDS)] for cell in zero_clocks + stamps]
    rng.shuffle(real)
    made = [f"{day} {1 + (at * 11) % 23:02d}:{(at * 17) % 60:02d}" for at, day in enumerate(_days(ROWS // 2, 2030))]
    twin = [[cell[:10] if cell[11:] == "00:00" else made[at % len(made)], "west"] for at, (cell, _ward) in enumerate(real)]
    outcome = _checked(tmp_path, ["event_date", "ward"], real, twin)
    assert not outcome.checks[3].passed
    assert outcome.checks[3].lines[0].startswith(f"Date column event_date: {ROWS // 2} of {ROWS} ")


def test_item_5_a_clocked_cell_on_a_day_written_alone(tmp_path: pathlib.Path) -> None:
    """A column whose real cells are days alone (one era) and clocked stamps (another): the twin adds a clock to each real day: C4 counts them by their calendar day and fails. Red on b9165d2d and on the mutant whose twin cells meet the rare values by their spelling alone (`day in rare[0]` and `day in rare[1]` dropped in `_walk_twin`)."""
    days = _days(ROWS // 2, 1960)
    stamps = [f"{day} {(at * 7) % 24:02d}:{(at * 13) % 60:02d}" for at, day in enumerate(_days(ROWS // 2, 2001))]
    rng = random.Random(1)
    real = [[cell, rng.choice(WARDS)] for cell in days + stamps]
    rng.shuffle(real)
    made = [f"{day} {(at * 11) % 24:02d}:{(at * 17) % 60:02d}" for at, day in enumerate(_days(ROWS // 2, 2030))]
    twin = [[cell + " 13:47" if len(cell) == 10 else made[at % len(made)], "west"] for at, (cell, _ward) in enumerate(real)]
    outcome = _checked(tmp_path, ["event_date", "ward"], real, twin)
    assert not outcome.checks[3].passed
    assert outcome.checks[3].lines[0].startswith(f"Date column event_date: {ROWS // 2} of {ROWS} ")


def test_item_5_a_patients_days_with_a_clock_added_are_a_copied_date_list(tmp_path: pathlib.Path) -> None:
    """1,000 people by 20 days written alone; one twin person holds a real person's 20 days with a clock added: C3 counts one copied date list and fails. Red on b9165d2d and on the mutant that never reads a column at its calendar day (`days=True` never set in `_walk_real`)."""
    rng = random.Random(1)
    span = _days(4000, 2010)
    real = [[f"P{at // 20:05d}", rng.choice(span), f"{rng.gauss(70, 9):.2f}"] for at in range(ROWS)]
    rng = random.Random(2)
    twin = [[f"Q{at // 20:05d}", rng.choice(span), f"{rng.gauss(70, 9):.2f}"] for at in range(ROWS)]
    source = [row for row in real if row[0] == "P00007"]
    twin = [row for row in twin if row[0] != "Q00007"] + [["Q00007", row[1] + " 09:30", f"{rng.gauss(70, 9):.2f}"] for row in source]
    outcome = _checked(tmp_path, ["patient_id", "visit_day", "pulse"], real, twin, person="patient_id")
    patient = outcome.checks[2]
    assert not patient.passed
    assert patient.lines[2].startswith("On dates: 1 of ")


# -- item 6: a history written twice ------------------------------------------------------------------------


def test_item_6_a_history_written_twice_is_a_copied_patient(tmp_path: pathlib.Path) -> None:
    """1,000 people by 20 readings; one twin person holds a real person's 20 readings twice (40 rows), labels changed; another holds a real history with three visits repeated: C3 counts each and fails. Red on b9165d2d (0 counted) and on the mutant reading a patient's rows as a sorted list (`sorted(set(...))` made `sorted(...)` in `_patients`)."""
    header = ["patient_id", "reading", "ward"]
    rng = random.Random(1)
    real = [[f"P{at // 20:05d}", f"{rng.gauss(70, 9):.2f}", rng.choice(WARDS)] for at in range(ROWS)]
    rng = random.Random(2)
    twin = [[f"Q{at // 20:05d}", f"{rng.gauss(70, 9):.2f}", rng.choice(WARDS)] for at in range(ROWS)]
    first = [row for row in real if row[0] == "P00007"]
    second = [row for row in real if row[0] == "P00011"]
    twin = [row for row in twin if row[0] not in ("Q00007", "Q00008", "Q00011")]
    twin += [["Q00007", row[1], "west"] for row in first + first]
    twin += [["Q00011", row[1], "west"] for row in second + second[:3]]
    patient = _checked(tmp_path, header, real, twin, person="patient_id").checks[2]
    assert not patient.passed
    assert patient.lines[0].startswith("On readings: 2 of ")


# -- item 7: one folder under two spellings ---------------------------------------------------------------


def _places(root: pathlib.Path, private: pathlib.Path) -> inside.Places:
    return inside.Places(private, (pathlib.Path(root, "tmp"),), (pathlib.Path(root, "home", "Downloads"),),
                         installation.system_name(), ())


def test_item_7_a_temporary_folder_under_other_capitals_is_refused(tmp_path: pathlib.Path) -> None:
    """The private folder lies under the temporary folder spelled with capitals (`TMP` for `tmp`): on a case-blind volume the two are one folder and the record is refused there, before anything is written; on a case-keeping volume they are two and it is written. Red on b9165d2d on a case-blind volume (the parts alone compared) and on the mutant without the identity walk (`_inside` returning after its parts)."""
    pathlib.Path(tmp_path, "tmp").mkdir()
    one_folder = pathlib.Path(tmp_path, "TMP").exists()
    private = pathlib.Path(tmp_path, "TMP", "home", "data", "synthtwin", "inside")
    places = _places(tmp_path, private)
    target = pathlib.Path(private, "cohort" + inside.SUFFIX)
    record = {"format": inside.FORMAT, "version": inside.VERSION, "mode": inside.MODE,
              "table": {"rows": 0, "columns": []}, "zones": {}}
    if one_folder:
        assert "temporary folder" in inside.place_refusal(target, places)
        assert inside.in_temporary(target, places)
        with pytest.raises(inside.InsideError):
            inside.write_record(record, target, places)
        assert not target.exists()
    else:
        assert inside.place_refusal(target, places) == ""
        assert inside.write_record(record, target, places).size > 0


@pytest.mark.skipif(installation.system_name() == "nt", reason="the mount roots are the POSIX side of the guard")
def test_item_7_a_mount_root_under_other_capitals_is_refused(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A private folder under a mount root spelled with capitals: refused on a case-blind volume as lying under a mount root. Red on b9165d2d on a case-blind volume and on the mutant reading the roots by their spelling alone (`or _inside(private, root)` dropped in `_network_mount`)."""
    pathlib.Path(tmp_path, "mnt").mkdir()
    monkeypatch.setattr(inside, "MOUNT_ROOTS", (str(pathlib.Path(tmp_path, "mnt").resolve()),))
    one_folder = pathlib.Path(tmp_path, "MNT").exists()
    private = pathlib.Path(tmp_path, "MNT", "share", "synthtwin", "inside")
    reason = inside.place_refusal(pathlib.Path(private, "cohort" + inside.SUFFIX), _places(tmp_path, private))
    assert ("network share or another disk" in reason) is one_folder


# -- item 8: the writer's bound and a marked file past it -------------------------------------------------


def test_item_8_the_writer_refuses_a_record_past_the_loaders_bound(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """With the bound at 4,096 bytes (a test device for 256 MiB), a record of about 11,000 bytes is refused before anything is written, and one under the bound is written and loads again. Red on b9165d2d (written, then unloadable) and on the mutant without the writer's bound."""
    monkeypatch.setattr(inside, "SIZE_CAP", 4096)
    private = pathlib.Path(tmp_path, "home", "data", "synthtwin", "inside")
    places = _places(tmp_path, private)
    big = {"format": inside.FORMAT, "version": inside.VERSION, "mode": inside.MODE,
           "table": {"rows": 0, "columns": ["c" + "x" * 50 for _ in range(200)]}, "zones": {}}
    target = pathlib.Path(private, "cohort" + inside.SUFFIX)
    with pytest.raises(inside.InsideError, match="more than the 4096 bytes"):
        inside.write_record(big, target, places)
    assert not target.exists()
    small = dict(big, table={"rows": 0, "columns": ["c1"]})
    assert inside.write_record(small, target, places).size <= 4096
    assert inside.load_record(target) == small


def test_item_8_a_marked_file_past_the_bound_stays_behind(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A marked file of 8,192 bytes named as a twin, past a bound of 4,096: it carries the marker, the manifest leaves it out and the export copies none of it. Red on b9165d2d (read as unmarked, on the manifest, copied) and on the mutant reading no file past the bound (`or here.stat().st_size > SIZE_CAP` restored in `carries_marker`)."""
    monkeypatch.setattr(inside, "SIZE_CAP", 4096)
    out = pathlib.Path(tmp_path, "out")
    out.mkdir()
    pathlib.Path(out, "cohort-twin.csv").write_text("person,age\nP1,40\n", encoding="utf-8", newline="\n")
    marked = pathlib.Path(out, "case-twin.csv")
    marked.write_bytes(inside.MARKER_BYTES + b"\n{}\n" + b"0" * 8192)
    assert marked.stat().st_size > inside.SIZE_CAP
    assert inside.carries_marker(marked)
    assert [path.name for path in inside.export_manifest(out)] == ["cohort-twin.csv"]
    outbox = pathlib.Path(tmp_path, "outbox")
    assert [path.name for path in inside.export(out, outbox)] == ["cohort-twin.csv"]
    assert sorted(path.name for path in outbox.iterdir()) == ["cohort-twin.csv"]


# -- item 9: the report's place ---------------------------------------------------------------------------


def _pair(folder: pathlib.Path) -> "tuple[str, str]":
    header = ["patient_id", "pulse", "ward"]
    rng = random.Random(1)
    real = [[f"P{at // 10:05d}", f"{rng.gauss(70, 9):.1f}", rng.choice(WARDS)] for at in range(ROWS)]
    rng = random.Random(2)
    twin = [[f"Q{at // 10:05d}", f"{rng.gauss(70, 9):.1f}", rng.choice(WARDS)] for at in range(ROWS)]
    return _write(pathlib.Path(folder, "real.csv"), header, real), _write(pathlib.Path(folder, "twin.csv"), header, twin)


def test_item_9_the_report_never_writes_over_an_input(tmp_path: pathlib.Path) -> None:
    """`--report` naming the real table, or a link to the twin: refused as an option (2), both tables unchanged. Red on b9165d2d (the real table and the twin overwritten with the report, exit 0) and on the mutant whose input test refuses nothing (`_refuse_an_input` returning at once)."""
    real_path, twin_path = _pair(tmp_path)
    kept = (pathlib.Path(real_path).read_bytes(), pathlib.Path(twin_path).read_bytes())
    assert twin_checks.main([real_path, twin_path, "--report", real_path]) == 2
    alias = pathlib.Path(tmp_path, "alias.csv")
    os.link(twin_path, alias)
    assert twin_checks.main([real_path, twin_path, "--report", f"{alias}"]) == 2
    assert (pathlib.Path(real_path).read_bytes(), pathlib.Path(twin_path).read_bytes()) == kept
    assert twin_checks.main([real_path, twin_path, "--report", f"{pathlib.Path(tmp_path, 'report.txt')}"]) == 0


def test_item_9_a_network_report_is_refused_before_anything_is_read(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`--report` in a network form: refused as an option (2) before either table is read, and nothing written. Red on b9165d2d (the checks ran and wrote a file of that name) and on the mutant validating the place only after the checks (`report_place` moved after `run_checks` in `main`)."""
    real_path, twin_path = _pair(tmp_path)

    def read(*_args: object, **_given: object) -> None:
        raise AssertionError("a table was read before the report's place was validated")

    monkeypatch.setattr(twin_checks, "run_checks", read)
    monkeypatch.chdir(tmp_path)
    assert twin_checks.main([real_path, twin_path, "--report", "\\\\server\\share\\checks.txt"]) == 2
    assert sorted(path.name for path in tmp_path.iterdir()) == ["real.csv", "twin.csv"]


def test_item_9_release_validates_its_folders_before_any_file_system_call(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A release folder in a network form: refused by the locality gate before any path is resolved. Red on b9165d2d (both folders resolved first) and on the mutant restoring that order."""
    real_path, twin_path = _pair(tmp_path)
    resolve = pathlib.Path.resolve

    def watched(self: pathlib.Path, strict: bool = False) -> pathlib.Path:
        if "server" in f"{self}":
            raise AssertionError("a network path was resolved before the locality gate")
        return resolve(self, strict)

    monkeypatch.setattr(pathlib.Path, "resolve", watched)
    with pytest.raises(PathValidationError):
        twin_checks.release(real_path, twin_path, "\\\\server\\share\\out", f"{pathlib.Path(tmp_path, 'held')}")
    with pytest.raises(PathValidationError):
        twin_checks.release(real_path, twin_path, f"{pathlib.Path(tmp_path, 'out')}", "//server/share/held")


# -- item 17: very large finite numbers --------------------------------------------------------------------


def test_item_17_very_large_finite_numbers_neither_break_nor_flatten_c2(tmp_path: pathlib.Path) -> None:
    """A column of repeated 1e308 values is checked (b9165d2d: an overflow raised); a twin cell of 1e308 beside ordinary real numbers is checked (b9165d2d: an overflow raised); a column about plus or minus 1e200 keeps its spread: rows whose large value is drawn anew are no near copies, rows moved by a hair are. Red on b9165d2d and on the mutant restoring the unscaled moments."""
    header = ["ward", "pulse", "assay"]
    rng = random.Random(1)
    real = [[rng.choice(WARDS), f"{rng.gauss(70, 9):.1f}", "1e308"] for _ in range(ROWS)]
    rng = random.Random(2)
    twin = [[rng.choice(WARDS), f"{rng.gauss(70, 9):.1f}", "1e308"] for _ in range(ROWS)]
    twin[3][2] = "1e307"
    assert _checked(tmp_path, header, real, twin).checks[1].measured
    rng = random.Random(3)
    ordinary = [[rng.choice(WARDS), f"{rng.gauss(70, 9):.1f}", f"{rng.gauss(5, 1):.3f}"] for _ in range(ROWS)]
    far = [list(row) for row in ordinary]
    far[7][2] = "1e308"
    assert _checked(tmp_path, header, ordinary, far, "far").checks[1].measured
    rng = random.Random(4)
    large = [[rng.choice(WARDS), f"{rng.gauss(70, 9):.1f}", f"{rng.gauss(0, 1):.6f}e200"] for _ in range(ROWS)]
    rng = random.Random(5)
    drawn = [[row[0], row[1], f"{rng.gauss(0, 1):.6f}e200"] for row in large]
    assert _verdicts(_checked(tmp_path, header, large, drawn, "drawn"))["C2"] is True
    moved = [[row[0], row[1], row[2].replace("e200", "1e200")] for row in large]
    assert _verdicts(_checked(tmp_path, header, large, moved, "moved"))["C2"] is False


def test_item_17_ordinary_columns_keep_their_codes() -> None:
    """On an ordinary column the scaled moments give the codes the unscaled ones gave, value for value (a division by a power of two is exact)."""
    rng = random.Random(6)
    values: "list[float | None]" = [rng.gauss(70, 9) for _ in range(5000)] + [None, 12.5, 130.25]
    present = [value for value in values if value is not None]
    mean = math.fsum(present) / len(present)
    spread = math.sqrt(math.fsum((value - mean) * (value - mean) for value in present) / (len(present) - 1))
    units = twin_checks._standard_units(values)
    for value in present + [0.0, -3.5, 1e6]:
        old = min(max(round((value - mean) / spread * twin_checks._SCALE) + twin_checks._MIDDLE, 0), twin_checks._TOP)
        assert twin_checks._encoded(value, units) == old
    assert twin_checks._encoded(1e308, units) == twin_checks._TOP
    assert twin_checks._encoded(-1e308, units) == 0
    constant = twin_checks._standard_units([7.0] * 10)
    assert [twin_checks._encoded(value, constant) for value in (7.0, 8.0, 6.5)] == [32768, 32768 + 2048, 32768 - 1024]


# -- item 18: one number, one spelling ----------------------------------------------------------------------


def test_item_18_an_exponent_is_written_out(tmp_path: pathlib.Path) -> None:
    """`1e3`, `1.0E+03` and `1000` are one spelling, and 200 real rows copied with their amount written as `2.5e3` are counted by C1. Red on b9165d2d (`1000.0` against `1000`; 0 counted) and on the mutant spelling an exponent's number by its float (`repr(value)`)."""
    for written, spelling, decimals in (("1e3", "1000", 0), ("1.0E+03", "1000", 0), ("1000", "1000", 0),
                                        ("2.5e3", "2500", 0), ("1.999e-6", "0.000001999", 9), ("-7.50e0", "-7.5", 2),
                                        ("0e999999", "0", 0), ("12.34e1", "123.4", 1)):
        read = twin_checks.read_number(written)
        assert read is not None and (read.spelling, read.decimals) == (spelling, decimals), written
    header = ["amount", "lab_value", "ward"]
    rng = random.Random(1)
    real = [[f"{rng.randrange(1, 51) * 100}", f"{rng.random():.9f}", rng.choice(WARDS)] for _ in range(ROWS)]
    rng = random.Random(2)
    twin = [[f"{rng.randrange(1, 51) * 100}", f"{rng.random():.9f}", rng.choice(WARDS)] for _ in range(ROWS)]
    for at in range(200):
        source = real[at * 97]
        twin[at * 90] = [f"{int(source[0]) / 1000:g}e3", source[1], source[2]]
    rows = _checked(tmp_path, header, real, twin).checks[0]
    assert not rows.passed
    assert rows.lines[0].startswith("200 of 20000 twin rows equal a real row")
