"""The health data zoo's catalogue holds what it says (lane E0a, plan P4-D399).

`tests/health_zoo.py` builds every kind of healthcare data the owner's
"all" of 2026-10-16 names, runs today's product on each end to end, and
reads the twin with the analyst's own code. The battery's verdicts are
the KPIs K-HZ-01 and K-HZ-02 (`tests/test_kpi_ledger.py`); this file
holds the battery itself to its word, cheaply:

* every kind the lane names is in the catalogue, and every column of
  every table serves exactly one kind;
* each table is the shape it claims -- a byte-order mark and CRLF, a
  Latin-1 file, semicolons and decimal commas, a real workbook with a
  typed date cell, Excel serial numbers -- and rebuilds byte for byte
  from its seed;
* each analyst script runs clean on its real table, so a failure on a
  twin is the twin's and never the script's;
* the comparison of the real table's results with the twin's catches a
  broken twin, red case by red case;
* the person's answers are general and only ever ones the file offers;
* one table runs end to end in this process;
* every kind that fails today names a lane of the December plan, or
  says it needs one.
"""

from __future__ import annotations

import io
import pathlib
import shutil
import zipfile

import pytest

import health_zoo as zoo

SMALL = 600
SEED = 20261016

# The lanes of the December plan a failing kind may be owned by, and the
# words for one no lane covers yet (the orchestrator names a new one).
PLAN_LANES = ("DST", "RT1", "RT2", "LM1", "LM2", "R7", "FM", "SCH", "G2T", zoo.NEEDS_OWNER)


def _written(name: str, folder: pathlib.Path, n: int = SMALL, seed: int = SEED) -> pathlib.Path:
    return zoo.write_table(zoo.table_named(name), folder, n, seed)


def test_every_kind_the_lane_names_is_in_the_catalogue() -> None:
    """Twenty-two kinds, each served by one table; every column by one kind."""
    named = set()
    for table in zoo.TABLES:
        header, _rows = table.build(150, SEED)
        served = [column for columns in table.kinds.values() for column in columns]
        assert sorted(served) == sorted(set(served)), f"{table.name}: a column serves two kinds"
        assert set(served) <= set(header), f"{table.name}: a kind names a column the table lacks"
        for column in header:
            assert zoo.kind_of(table, column) in zoo.KINDS, f"{table.name}.{column}"
        assert not named & set(table.kinds), f"{table.name}: a kind is served twice"
        named |= set(table.kinds)
    assert named == set(zoo.KINDS)
    assert len(zoo.KINDS) == 22
    assert set(zoo.FILE_KINDS) <= set(zoo.KINDS)


@pytest.mark.parametrize("name", [table.name for table in zoo.TABLES])
def test_each_table_rebuilds_byte_for_byte_from_its_seed(name: str, tmp_path: pathlib.Path) -> None:
    first = _written(name, tmp_path / "a", 150).read_bytes()
    again = _written(name, tmp_path / "b", 150).read_bytes()
    other = _written(name, tmp_path / "c", 150, SEED + 1).read_bytes()
    assert first == again
    assert first != other


def test_the_file_shapes_are_the_shapes_they_say(tmp_path: pathlib.Path) -> None:
    """The file-level kinds, read off the bytes."""
    encounters = _written("encounters", tmp_path).read_bytes()
    assert encounters.startswith(b"\xef\xbb\xbf")
    assert encounters.count(b"\r\n") == SMALL + 1 and b"\n" not in encounters.replace(b"\r\n", b"")
    claims = _written("claims", tmp_path).read_bytes()
    claims.decode("latin-1")
    with pytest.raises(UnicodeDecodeError):
        claims.decode("utf-8")
    patients = _written("patients", tmp_path).read_bytes().decode("utf-8")
    assert "São Paulo" in patients and "Español" in patients
    vitals = _written("vitals", tmp_path).read_text(encoding="utf-8")
    first_line, second_line = vitals.split("\n")[:2]
    assert first_line.count(";") == 8 and "," not in first_line
    assert " kg" in second_line and "," in second_line.split(";")[7]
    book = _written("surveys", tmp_path).read_bytes()
    with zipfile.ZipFile(io.BytesIO(book)) as bundle:
        assert "xl/worksheets/sheet1.xml" in bundle.namelist()
    import pandas

    frame = pandas.read_excel(tmp_path / "surveys.xlsx")
    assert str(frame["survey_date"].dtype).startswith("datetime64")
    imaging = pandas.read_csv(_written("imaging", tmp_path))
    assert imaging["study_date_serial"].between(44927, 45657).all()


def test_the_analyst_scripts_run_clean_on_every_real_table(tmp_path: pathlib.Path) -> None:
    """On the real table every check runs, every bad count is nought and every shape is there.

    So a check that fails on a twin is the twin's: the script that reads
    it is the one that read the real table without a fault.
    """
    for table in zoo.TABLES:
        path = zoo.write_table(table, tmp_path, SMALL, SEED)
        results = zoo.analyse(table, path)
        errors = {name: value for name, (status, value) in results.items() if status != "ok"}
        assert not errors, f"{table.name}: {errors}"
        for check in table.checks:
            value = results[check.name][1]
            if check.mode == "bad":
                assert value == 0, f"{table.name}: {check.name} reads {value} bad cells on the real"
            if check.mode == "present":
                assert value is True, f"{table.name}: {check.name} is absent from the real"


def _twin_like(source: pathlib.Path, folder: pathlib.Path, change: "tuple[str, str]") -> pathlib.Path:
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / source.name
    text = source.read_text(encoding="utf-8")
    old, new = change
    assert old in text
    target.write_text(text.replace(old, new, 1), encoding="utf-8", newline="")
    return target


def test_the_comparison_names_what_a_broken_twin_breaks(tmp_path: pathlib.Path) -> None:
    """Red cases: a code outside its pattern, a dtype that moved, a column gone, a shape lost."""
    table = zoo.table_named("diagnoses_procedures")
    source = _written(table.name, tmp_path)
    real = zoo.analyse(table, source)
    same = tmp_path / "same"
    same.mkdir()
    shutil.copy(source, same / source.name)
    assert zoo.analyst_failures(table, real, zoo.analyse(table, same / source.name)) == []

    header, rows = table.build(SMALL, SEED)
    nine = header.index("icd9")
    coded = _twin_like(source, tmp_path / "coded", (f",{rows[0][nine]},", ",group-1,"))
    failures = zoo.analyst_failures(table, real, zoo.analyse(table, coded))
    assert ("diagnoses", "ICD-9-CM", "1 bad cell(s) on the twin, none on the real") in failures

    seq = header.index("dx_seq")
    typed = _twin_like(source, tmp_path / "typed", (f",{rows[0][seq]},{rows[0][seq + 1]},", f",x,{rows[0][seq + 1]},"))
    names = [failure[1] for failure in zoo.analyst_failures(table, real, zoo.analyse(table, typed))]
    assert "dtype dx_seq" in names

    gone = _twin_like(source, tmp_path / "gone", ("icd10pcs", "pcs_code"))
    failures = zoo.analyst_failures(table, real, zoo.analyse(table, gone))
    assert ("procedures", "ICD-10-PCS") in [(kind, name) for kind, name, _why in failures]

    notes = zoo.table_named("notes")
    written = _written("notes", tmp_path / "notes")
    flat = tmp_path / "flat"
    flat.mkdir()
    (flat / written.name).write_text(
        written.read_text(encoding="utf-8").replace("\n", " ").replace(" note_id", "\nnote_id") + "\n",
        encoding="utf-8", newline="\n",
    )
    failures = zoo.analyst_failures(notes, zoo.analyse(notes, written), zoo.analyse(notes, flat / written.name))
    assert failures, "a twin whose notes lost their rows and line breaks must not pass"


def test_the_answers_are_general_and_only_ones_the_file_offers() -> None:
    table = zoo.table_named("labs")
    document = {
        "asked": [
            {"column": "loinc", "answers_you_can_give": [{"answer": "keep"}, {"answer": "code"}], "your_answer": ""},
            {"column": "result", "answers_you_can_give": [{"answer": "keep"}, {"answer": "identifier"}], "your_answer": ""},
            {"column": "viral_load", "answers_you_can_give": [{"answer": "measurement"}, {"answer": "excel-1900"}], "your_answer": ""},
        ],
        "checklist": {"columns": [
            {"column": "patient_id", "answers_you_can_give": [{"answer": "identifier"}], "your_answer": ""},
        ]},
    }
    asked, general = zoo.answer_generally(table, document)
    assert general
    given = {entry["column"]: entry["given"] for entry in asked}
    assert given == {"loinc": "code", "result": "", "viral_load": "measurement", "patient_id": "identifier"}
    assert document["checklist"]["columns"][0]["your_answer"] == "identifier"
    document["asked"][0]["answers_you_can_give"] += [{"answer": "outcome-of-interest"}]
    _asked, general = zoo.answer_generally(table, document)
    assert not general, "an answer about the analysis is not a general question"
    document["asked"][0]["answers_you_can_give"] = [{"answer": "code", "means": "the outcome of your model"}]
    _asked, general = zoo.answer_generally(table, document)
    assert not general


def test_one_table_runs_end_to_end_in_this_process(tmp_path: pathlib.Path) -> None:
    """The patients' export: profile, the answers, generate, validate, the analyst on both files."""
    result = zoo.run_table(zoo.table_named("patients"), tmp_path, SMALL, SEED)
    assert {step: done["exit"] for step, done in result["steps"].items()} == {
        "profile": 0, "answers": 0, "generate": 0, "validate": 0,
    }
    assert result["general"] is True
    assert {entry["column"] for entry in result["asked"]} >= {"patient_id", "zip5"}
    assert result["analyst_real_errors"] == []
    verdicts = zoo.per_kind([result])
    assert set(verdicts) == {"demographics", "utf8_accents"}
    assert verdicts["utf8_accents"]["passed"] is True


def test_every_owner_is_a_lane_of_the_plan_or_needs_one() -> None:
    for kind, owners in zoo.OWNERS.items():
        assert kind in zoo.KINDS, kind
        assert owners, kind
        for owner, gap in owners:
            assert owner in PLAN_LANES, f"{kind}: {owner}"
            assert gap, kind
