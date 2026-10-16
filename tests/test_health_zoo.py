"""The health data zoo's catalogue holds what it says (lane E0a, plan P4-D399).

`tests/health_zoo.py` builds every kind of healthcare data the owner's
"all" of 2026-10-16 names, runs today's product on each end to end, and
reads the twin with the analyst's own code. The battery's verdicts are
the KPIs K-HZ-01 and K-HZ-02 (`tests/test_kpi_ledger.py`); this file
holds the battery itself to its word, cheaply:

* every kind the lane and its reviews name is in the catalogue, and
  every column of every table serves exactly one kind;
* each table is the shape it claims -- a byte-order mark and CRLF, a
  Latin-1 file, semicolons and decimal commas, a real workbook with a
  typed date cell, spreadsheet serial numbers, DICOM's dates as figures
  -- and rebuilds byte for byte from its seed;
* each analyst script runs clean on its real table, so a failure on a
  twin is the twin's and never the script's;
* EVERY check of every table goes red on a spoiled copy of its real
  table, so no check is blind;
* the comparison catches a twin unlike its source -- a blank where the
  real has none, a unit or a censoring mark dropped, a missing marker
  or a negative spelled another way, a file's bytes changed, repeated
  patients lost, a level lost, stamps cut to the minute, rows lost;
* the pass rule: a failed step, a question about the analysis, a
  validate miss, a fault of the script on the real table and an analyst
  failure each fail the kind, and each failure needs its own owner;
* the offsets the clocks skip and repeat are judged as the transition
  rules say;
* the person's answers are general and only ever ones the file offers,
  and every sentence that asks is read;
* one table runs end to end in this process, and the labs table's
  validate misses reach its verdict;
* the workbook is read through the suite's cross-check reader, so CI's
  `minimums` cell, which has no openpyxl, skips that part and only it;
* the slow driver loads where there is no `resource` module (Windows).
"""

from __future__ import annotations

import datetime
import io
import pathlib
import random
import re
import shutil
import zipfile

import pytest

import crosscheck
import health_zoo as zoo

SMALL = 600
SEED = 20261016

# The lanes of the December plan a failing kind may be owned by, and the
# words for one no lane covers yet (the orchestrator names a new one).
PLAN_LANES = ("DST", "RT1", "RT2", "LM1", "LM2", "R7", "FM", "SCH", "G2T", zoo.NEEDS_OWNER)

# The kinds the lane's step names, and the ones its first review found
# missing (skeptic 1, item 4; Codex, item 6): each must be in the catalogue.
REQUIRED_KINDS = (
    "demographics", "encounters", "diagnoses", "procedures", "labs", "medication_orders", "vitals",
    "flowsheet_long", "redcap", "claims", "clinical_notes", "surveys_pro", "wearables", "genomics",
    "imaging", "utf8_accents", "latin1", "byte_order_mark", "crlf_line_endings",
    "semicolon_decimal_comma", "excel_serial_dates", "excel_workbook",
    "perioperative", "clock_times", "multi_value_cells", "tumor_registry", "partial_dates",
    "us_unit_vitals", "dicom_metadata", "sql_server_export", "microbiology",
    "immunizations_providers", "empty_and_constant_columns", "mixed_results", "genomic_ids",
    "risk_and_comorbidity_codes",
)


def _written(name: str, folder: pathlib.Path, n: int = SMALL, seed: int = SEED) -> pathlib.Path:
    return zoo.write_table(zoo.table_named(name), folder, n, seed)


def _pair(
    name: str,
    folder: pathlib.Path,
    change: "object",
    write: "object" = None,
) -> "list[tuple[str, str, str]]":
    """The analyst's failures on a twin-like copy of a real table: `change(header, rows)` applied."""
    table = zoo.table_named(name)
    header, rows = table.build(SMALL, SEED)
    real = folder / "real" / f"{table.name}{table.suffix}"
    real.parent.mkdir(parents=True, exist_ok=True)
    real.write_bytes(table.write(header, rows))
    header, rows = table.build(SMALL, SEED)
    change(header, rows)  # type: ignore[operator]
    twin = folder / "twin" / f"{table.name}{table.suffix}"
    twin.parent.mkdir(parents=True, exist_ok=True)
    twin.write_bytes((write or table.write)(header, rows))  # type: ignore[operator]
    return zoo.analyst_failures(table, zoo.analyse(table, real), zoo.analyse(table, twin))


def _csv_tables() -> "list[str]":
    return [table.name for table in zoo.TABLES if table.suffix == ".csv"]


def test_every_kind_the_lane_names_is_in_the_catalogue() -> None:
    """Each kind served by one table; every column by one kind; the named kinds all there."""
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
        for check in table.checks:
            assert check.kind in table.kinds, f"{table.name}: {check.name}"
            assert not check.column or check.column in header, f"{table.name}: {check.name}"
    assert named == set(zoo.KINDS)
    assert set(REQUIRED_KINDS) == set(zoo.KINDS)
    assert set(zoo.FILE_KINDS) <= set(zoo.KINDS)


@pytest.mark.parametrize("name", [table.name for table in zoo.TABLES])
def test_each_table_rebuilds_byte_for_byte_from_its_seed(name: str, tmp_path: pathlib.Path) -> None:
    first = _written(name, tmp_path / "a", 150).read_bytes()
    again = _written(name, tmp_path / "b", 150).read_bytes()
    other = _written(name, tmp_path / "c", 150, SEED + 1).read_bytes()
    assert first == again
    assert first != other


def test_the_file_shapes_are_the_shapes_they_say(tmp_path: pathlib.Path) -> None:
    """The file-level kinds, read off the bytes; the workbook last, through the cross-check reader."""
    import pandas

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
    cases = pandas.read_csv(_written("perioperative", tmp_path))
    assert cases["case_date_serial"].between(44927, 45657).all()
    assert cases["incision_time"].str.fullmatch(r"\d\d:\d\d (AM|PM)").all()
    studies = pandas.read_csv(_written("imaging", tmp_path))
    assert str(studies["study_date"].dtype) == "int64", "DICOM's DA reads as figures"
    assert studies["study_time"].astype(str).str.fullmatch(r"\d{6}\.\d{1,6}").mean() > 0.3
    tumors = pandas.read_csv(_written("tumor_registry", tmp_path), dtype=str)
    assert tumors["dx_date"].str.fullmatch(r"\d{4}").any() and tumors["dx_date"].str.fullmatch(r"\d\d/\d{4}").any()
    labs = pandas.read_csv(_written("labs", tmp_path), dtype=str)
    assert "101284-8" in set(labs["loinc"])
    assert {"<5", "NEGATIVE"} <= set(labs["result_value"])
    edge = pandas.read_csv(_written("edge_columns", tmp_path))
    assert edge["middle_name"].isna().all() and set(edge["facility"]) == {"MAIN"}
    book = _written("surveys", tmp_path).read_bytes()
    with zipfile.ZipFile(io.BytesIO(book)) as bundle:
        assert "xl/worksheets/sheet1.xml" in bundle.namelist()
    frame = crosscheck.read_excel(tmp_path / "surveys.xlsx")
    assert str(frame["survey_date"].dtype).startswith("datetime64")  # type: ignore[index]


def _clean(table: "zoo.Table", folder: pathlib.Path) -> None:
    path = zoo.write_table(table, folder, SMALL, SEED)
    results = zoo.analyse(table, path)
    errors = {name: value for name, (status, value) in results.items() if status != "ok"}
    assert not errors, f"{table.name}: {errors}"
    assert zoo.real_faults(table, results) == [], table.name
    for check in table.checks:
        value = results[check.name][1]
        if check.mode == "bad":
            assert value == 0, f"{table.name}: {check.name} reads {value} bad cells on the real"
        if check.mode == "present":
            assert value is True, f"{table.name}: {check.name} is absent from the real"


def test_the_analyst_scripts_run_clean_on_every_real_table(tmp_path: pathlib.Path) -> None:
    """On the real table every check runs, every bad count is nought and every shape is there.

    So a check that fails on a twin is the twin's: the script that reads
    it is the one that read the real table without a fault. The workbook
    is read last, through the cross-check reader.
    """
    for table in zoo.TABLES:
        if table.suffix == ".csv":
            _clean(table, tmp_path / table.name)
    crosscheck.reader()
    for table in zoo.TABLES:
        if table.suffix == ".xlsx":
            _clean(table, tmp_path / table.name)


@pytest.mark.parametrize("name", [table.name for table in zoo.TABLES])
def test_every_check_goes_red_on_its_spoiled_table(name: str, tmp_path: pathlib.Path) -> None:
    """A spoiled copy of the real table makes each check fail: none of them can be blind.

    The spoil is the check's own (`health_zoo.spoil_of`): by default its
    column's first cell written as junk. A check blinded to return a
    constant -- skeptic 1's mutants of the offset, range and stature
    checks -- is red here.
    """
    table = zoo.table_named(name)
    if table.suffix == ".xlsx":
        crosscheck.reader()
    blind = []
    for place in range(len(table.checks)):
        check = table.checks[place]
        failures = _pair(name, tmp_path / f"{place}", zoo.spoil_of(check))
        if check.name not in [failure[1] for failure in failures]:
            blind += [check.name]
    assert not blind, f"{name}: these checks did not see their spoil: {blind}"


def _blank(column: str, share: float) -> "object":
    draw = random.Random(7)
    return zoo.spoil_every(column, lambda value: "" if draw.random() < share else value)


def _edit(column: str, how: "object", share: float = 1.0) -> "object":
    draw = random.Random(7)
    return zoo.spoil_every(column, lambda value: how(value) if draw.random() < share else value)  # type: ignore[operator]


def _nobody_repeats(header: "list[str]", rows: "list[list[str]]") -> None:
    zoo.spoil_unique("patient_id")(header, rows)


def _half(header: "list[str]", rows: "list[list[str]]") -> None:
    del rows[: len(rows) // 2]


def _leave(header: "list[str]", rows: "list[list[str]]") -> None:
    return None


# A twin unlike its source in one way each, as skeptic 1 built them
# (planning-notes wave6/E0a-sk1-work/broken_twins.py) and Codex named
# them, with the check that must name it. 16 of skeptic 1's 19 passed
# unseen before repair 1.
ATTACKS = {
    "blank ICD-10 codes": ("diagnoses_procedures", _blank("icd10_dotted", 0.05), None, "missing icd10_dotted"),
    "blank modality codes": ("imaging", _blank("modality", 0.05), None, "missing modality"),
    "blank HGVS strings": ("genomics", _blank("hgvs_c", 0.05), None, "missing hgvs_c"),
    "blank LOINC codes": ("labs", _blank("loinc", 0.05), None, "missing loinc"),
    "NULL in place of a code": ("diagnoses_procedures", _edit("icd10_dotted", lambda v: "NULL" if v == "I25.10" else v), None, "missing icd10_dotted"),
    "temperatures lose their unit": ("vitals", _edit("temp", lambda v: v.replace(" °C", ""), 0.1), None, "shapes temp"),
    "'>1000' written '1000'": ("labs", _edit("viral_load", lambda v: "1000" if v == ">1000" else v), None, "shapes viral_load"),
    "'<5' written '5'": ("labs", _edit("viral_load", lambda v: "5" if v == "<5" else v), None, "shapes viral_load"),
    "byte-order mark and CRLF dropped": ("encounters", _leave, lambda h, r: zoo.csv_bytes(h, r), "file: byte-order mark"),
    "CRLF dropped, the mark kept": ("encounters", _leave, lambda h, r: zoo.csv_bytes(h, r, mark=True), "file: line endings"),
    "negative adjustments as -$": ("claims", _edit("adjustment", lambda v: "-" + v[1:-1] if v.startswith("(") else v), None, "shapes adjustment"),
    "flags all blank": ("labs", _edit("abnormal_flag", lambda v: ""), None, "dtype abnormal_flag"),
    "nobody repeats in vitals": ("vitals", _nobody_repeats, None, "some patient has several rows"),
    "nobody repeats in labs": ("labs", _nobody_repeats, None, "some patient has several rows"),
    "nobody repeats in claims": ("claims", _nobody_repeats, None, "some patient has several rows"),
    "nobody repeats in the flowsheet": ("flowsheet", _nobody_repeats, None, "some patient has several rows"),
    "REDCap loses arm 2": ("redcap", _edit("redcap_event_name", lambda v: v.replace("arm_2", "arm_1")), None, "levels redcap_event_name"),
    "stamps cut to the minute": ("wearables", _edit("ts", lambda v: v[:17] + "00", 0.5), None, "stamps on the whole minute, as a share"),
    "half the rows": ("genomics", _half, None, "rows read"),
    "a range with one bound": ("labs", zoo.spoil_cell("ref_range", "70"), None, "reference ranges split into exactly two numbers"),
    "a range with three bounds": ("labs", zoo.spoil_cell("ref_range", "70-99-100"), None, "reference ranges split into exactly two numbers"),
    "a Latin-1 file written as UTF-8": ("claims", _leave, lambda h, r: zoo.csv_bytes(h, r), "file: decodes as UTF-8"),
}


@pytest.mark.parametrize("attack", sorted(ATTACKS))
def test_a_twin_unlike_its_source_is_named(attack: str, tmp_path: pathlib.Path) -> None:
    name, change, write, wanted = ATTACKS[attack]
    failures = _pair(name, tmp_path, change, write)
    assert wanted in [failure[1] for failure in failures], failures


def test_a_twin_unlike_its_source_is_named_in_the_workbook(tmp_path: pathlib.Path) -> None:
    """The survey's missing markers: 'Not asked' lost or spelled 'N/A', -99 written blank."""
    crosscheck.reader()
    lost = _pair("surveys", tmp_path / "lost", _edit("q4_status", lambda v: "NA" if v == "Not asked" else v))
    assert "levels q4_status" in [failure[1] for failure in lost], lost
    spelled = _pair("surveys", tmp_path / "spelled", _edit("q4_status", lambda v: "N/A" if v == "Not asked" else v))
    assert "missing spellings q4_status" in [failure[1] for failure in spelled], spelled
    blank = _pair("surveys", tmp_path / "blank", _edit("q2_score", lambda v: "" if v == "-99" else v))
    assert "missing q2_score" in [failure[1] for failure in blank], blank


def test_a_twin_like_its_source_passes(tmp_path: pathlib.Path) -> None:
    """The control: each delimited real table read as its own twin fails nothing."""
    for name in _csv_tables():
        assert _pair(name, tmp_path / name, _leave) == [], name


def test_the_comparison_names_what_a_broken_twin_breaks(tmp_path: pathlib.Path) -> None:
    """Red cases: a code outside its pattern, a dtype that moved, a column gone."""
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


def test_notes_flattened_with_their_rows_kept_lose_their_line_breaks(tmp_path: pathlib.Path) -> None:
    """The 'present' branch on its own: the rows read the same, only the line breaks went."""
    failures = _pair("notes", tmp_path, zoo.spoil_every("note_text", lambda v: v.replace("\n", " ")))
    names = [failure[1] for failure in failures]
    assert "some note runs over several lines" in names
    assert "rows read" not in names


def _twin_like(source: pathlib.Path, folder: pathlib.Path, change: "tuple[str, str]") -> pathlib.Path:
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / source.name
    text = source.read_text(encoding="utf-8")
    old, new = change
    assert old in text
    target.write_text(text.replace(old, new, 1), encoding="utf-8", newline="")
    return target


def test_the_offsets_the_clocks_skip_and_repeat() -> None:
    """US Eastern, by the transition rules: 02:00 to 02:59 never happens on the second Sunday
    of March, and 01:00 to 01:59 happens twice on the first Sunday of November."""
    import pandas

    def wrong(*stamps: str) -> int:
        return zoo._wrong_offsets(pandas.Series(list(stamps)))

    assert wrong("2024-03-10 02:30:00-04:00") == 1
    assert wrong("2024-03-10 02:30:00-05:00") == 1
    assert wrong("2024-03-10 01:59:00-05:00", "2024-03-10 03:00:00-04:00") == 0
    assert wrong("2024-11-03 01:30:00-04:00", "2024-11-03 01:30:00-05:00") == 0
    assert wrong("2024-11-03 00:59:00-04:00", "2024-11-03 02:00:00-05:00") == 0
    assert wrong("2024-11-03 02:30:00-04:00") == 1
    assert wrong("2024-07-01 10:00:00-05:00", "2024-01-15 10:00:00-04:00") == 2
    assert zoo.eastern_offsets(datetime.datetime(2023, 3, 12, 2, 15)) == ()
    assert zoo.eastern_offsets(datetime.datetime(2023, 11, 5, 1, 15)) == ("-04:00", "-05:00")
    try:
        import zoneinfo

        eastern = zoneinfo.ZoneInfo("America/New_York")
    except Exception:  # noqa: BLE001 -- no time-zone data on this machine: the cases above stand
        return
    for day in zoo.CHANGE_DAYS:
        for minutes in range(-120, 24 * 60 + 120, 15):
            local = datetime.datetime.combine(day, datetime.time()) + datetime.timedelta(minutes=minutes)
            seen = set()
            for fold in (0, 1):
                moment = local.replace(tzinfo=eastern, fold=fold)
                back = moment.astimezone(datetime.timezone.utc).astimezone(eastern).replace(tzinfo=None)
                if back == local:
                    offset = moment.utcoffset()
                    assert offset is not None
                    hours = int(offset.total_seconds() // 3600)
                    seen |= {f"-{-hours:02d}:00"}
            assert set(zoo.eastern_offsets(local)) == seen, local


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


def _plain() -> "dict":
    return {
        "what_this_is": "synthtwin could not settle these columns from their values alone.",
        "about_your_file": [
            {"subject": "the separator", "answers_you_can_give": [{"answer": "comma"}, {"answer": "semicolon"}],
             "your_answer": "", "then_the_description_publishes": "the columns as the file divides them"},
        ],
        "asked": [
            {"column": "loinc", "answers_you_can_give": [{"answer": "code"}], "your_answer": "",
             "read_as_now": "labels", "what_synthtwin_saw": "figures, a hyphen and a figure"},
        ],
        "checklist": {
            "question": "Is each column read the way it should be?",
            "why": "A column read wrongly is generated wrongly.",
            "columns": [{"column": "patient_id", "answers_you_can_give": [{"answer": "identifier"}], "your_answer": ""}],
        },
    }


@pytest.mark.parametrize(
    "where",
    ["checklist question", "checklist why", "read_as_now", "then_the_description_publishes", "what_this_is"],
)
def test_every_sentence_that_asks_is_read_for_the_analysis(where: str) -> None:
    """Codex's item 5: a question about the analysis in any of the file's sentences is not general."""
    table = zoo.table_named("labs")
    _asked, general = zoo.answer_generally(table, _plain())
    assert general
    document = _plain()
    asking = "Which columns predict the outcome of your analysis?"
    if where == "checklist question":
        document["checklist"]["question"] = asking
    elif where == "checklist why":
        document["checklist"]["why"] = asking
    elif where == "read_as_now":
        document["asked"][0]["read_as_now"] = asking
    elif where == "then_the_description_publishes":
        document["about_your_file"][0]["then_the_description_publishes"] = asking
    else:
        document["what_this_is"] = asking
    _asked, general = zoo.answer_generally(table, document)
    assert not general, where


def test_the_semicolon_file_says_semicolon() -> None:
    """Skeptic 1's item 6: the semicolon export answers 'semicolon' even where 'comma' is offered first."""
    entry = {"subject": "the separator", "answers_you_can_give": [{"answer": "comma"}, {"answer": "semicolon"}], "your_answer": ""}
    asked, _general = zoo.answer_generally(zoo.table_named("vitals"), {"about_your_file": [entry]})
    assert asked[0]["given"] == "semicolon"
    entry["your_answer"] = ""
    asked, _general = zoo.answer_generally(zoo.table_named("labs"), {"about_your_file": [entry]})
    assert asked[0]["given"] == "comma"


def test_one_table_runs_end_to_end_in_this_process(tmp_path: pathlib.Path) -> None:
    """The patients' export: profile, the answers, generate, validate, the analyst on both files."""
    result = zoo.run_table(zoo.table_named("patients"), tmp_path, SMALL, SEED)
    assert {step: done["exit"] for step, done in result["steps"].items()} == {
        "profile": 0, "answers": 0, "generate": 0, "validate": 0,
    }
    assert result["general"] is True
    assert {entry["column"] for entry in result["asked"]} >= {"patient_id", "zip5"}
    assert result["analyst_real_errors"] == []
    assert result["roles"]["patient_id"] == "identifier"
    verdicts = zoo.per_kind([result])
    assert set(verdicts) == {"demographics", "utf8_accents"}
    assert verdicts["utf8_accents"]["passed"] is True


def test_the_labs_misses_reach_its_verdict(tmp_path: pathlib.Path) -> None:
    """validate's MISSED checks are captured per column and fail the kind at validate."""
    result = zoo.run_table(zoo.table_named("labs"), tmp_path, SMALL, SEED)
    assert result["steps"]["validate"]["exit"] == 3
    assert result["misses"], "validate missed checks on the labs twin and none were captured"
    assert {miss[0] for miss in result["misses"]} == {"ref_range"}
    assert zoo.per_kind([result])["labs"]["failing_step"] == "validate"


def _result(table: str, **changes: object) -> "dict":
    done = {"exit": 0, "error": ""}
    result: "dict" = {
        "table": table, "rows": SMALL, "misses": [], "analyst": [], "asked": [], "general": True,
        "analyst_real_errors": [],
        "steps": {"profile": dict(done), "answers": dict(done), "generate": dict(done), "validate": dict(done)},
    }
    result.update(changes)
    return result


def test_the_pass_rule_fails_a_kind_on_every_prerequisite() -> None:
    """A failed step, a question about the analysis, a miss and a fault on the real table each fail."""
    assert all(verdict["passed"] for verdict in zoo.per_kind([_result("labs")]).values())

    stopped = _result("labs")
    stopped["steps"]["generate"] = {"exit": 1, "error": "raised"}
    del stopped["steps"]["validate"]
    verdicts = zoo.per_kind([stopped])
    assert {kind: verdict["failing_step"] for kind, verdict in verdicts.items()} == {
        "labs": "generate", "mixed_results": "generate",
    }

    missed = zoo.per_kind([_result("labs", misses=[["ref_range", "distinct.n_distinct"]])])
    assert missed["labs"]["failing_step"] == "validate" and missed["labs"]["passed"] is False
    assert missed["mixed_results"]["passed"] is True

    asked = [{"column": "loinc", "offered": ["outcome"], "given": "", "general": False}]
    verdicts = zoo.per_kind([_result("labs", asked=asked, general=False)])
    assert verdicts["labs"]["failing_step"] == "questions"
    assert verdicts["mixed_results"]["passed"] is True
    about_the_file = [{"column": "the separator", "offered": ["outcome"], "given": "", "general": False}]
    verdicts = zoo.per_kind([_result("labs", asked=about_the_file, general=False)])
    assert not any(verdict["passed"] for verdict in verdicts.values())

    faulty = zoo.per_kind([_result("labs", analyst_real_errors=["LOINC codes"])])
    assert faulty["labs"]["failing_step"] == "analyst on the real table"
    assert faulty["mixed_results"]["passed"] is True

    measured = zoo.zoo_measures([stopped])
    assert measured["K-HZ-01"]["kinds_passing_end_to_end"] == 0
    assert measured["K-HZ-01"]["tables_generated"] == 0


def test_a_fault_of_the_script_on_the_real_table_is_named(tmp_path: pathlib.Path) -> None:
    """Codex's items 4 and 7: a check that does not hold on the REAL table would disable its own
    comparison, so a raise, a bad count above nought or a missing shape on the real is a fault."""
    table = zoo.table_named("labs")
    header, rows = table.build(SMALL, SEED)
    zoo.spoil_cell("loinc", "101284-88")(header, rows)
    zoo.spoil_every("result_value", lambda v: v.lstrip("<>"))(header, rows)
    path = tmp_path / "labs.csv"
    path.write_bytes(table.write(header, rows))
    faults = zoo.real_faults(table, zoo.analyse(table, path))
    assert faults == ["LOINC codes", "some result is censored"]
    verdicts = zoo.per_kind([_result("labs", analyst_real_errors=faults)])
    assert verdicts["labs"]["failing_step"] == "analyst on the real table"
    assert verdicts["mixed_results"]["failing_step"] == "analyst on the real table"


def test_a_failed_command_is_never_read_as_success(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    """_quietly returns the command's own exit; a profile that exits 2 stops the run and fails every kind."""
    from synthtwin import cli

    monkeypatch.setattr(cli, "main", lambda arguments: 2)
    assert zoo._quietly(["profile", "x"])[0] == 2
    result = zoo.run_table(zoo.table_named("patients"), tmp_path, 150, SEED)
    assert result["steps"] == {"profile": {"exit": 2, "error": ""}}
    measured = zoo.zoo_measures([result])
    assert measured["K-HZ-01"]["tables_profiled"] == 0
    assert measured["K-HZ-01"]["kinds_passing_end_to_end"] == 0
    assert {verdict["failing_step"] for verdict in measured["kinds"].values()} == {"profile"}


def test_each_failure_needs_its_own_owner() -> None:
    """An owner of one failure of a kind does not own a new one: the new one is counted unowned."""
    surprise = [["labs", "a check nobody has seen fail", "why"]]
    verdicts = zoo.per_kind([_result("labs", analyst=surprise)])
    assert verdicts["labs"]["unowned"] == ["a check nobody has seen fail"]
    measured = zoo.zoo_measures([_result("labs", analyst=surprise)])
    assert measured["K-HZ-02"]["failures_without_owner"] == 1
    assert measured["K-HZ-02"]["failing_kinds_without_owner"] == 1


def test_every_owner_is_a_lane_of_the_plan_or_needs_one() -> None:
    assert zoo.OWNERS, "the baseline's failures are owned"
    for kind, owners in zoo.OWNERS.items():
        assert kind in zoo.KINDS, kind
        assert owners, kind
        for owner, gap, covers in owners:
            assert owner in PLAN_LANES, f"{kind}: {owner}"
            assert gap, kind
            for stranger in ("a check nobody has seen fail", "profile", "generate", "questions", "real read"):
                assert not re.fullmatch(covers, stranger), f"{kind}: {covers!r} covers {stranger!r}"


def test_the_workbook_is_left_out_where_its_reader_is_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    """CI's `minimums` cell has no openpyxl: the zoo runs every delimited export and names the rest."""
    monkeypatch.setattr(crosscheck, "present", lambda: False)
    names = [table.name for table in zoo.runnable_tables()]
    assert "surveys" not in names and len(names) == len(zoo.TABLES) - 1
    assert set(zoo.workbook_kinds()) == {"surveys_pro", "excel_workbook"}


def test_the_driver_starts_where_there_is_no_resource_module(monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 9: Windows has no `resource`; the slow driver still loads and leaves memory unmeasured."""
    import importlib.util
    import sys

    driver = pathlib.Path(__file__).resolve().parent.parent / "tools" / "measurements" / "kpi_health_zoo.py"
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setitem(sys.modules, "resource", None)
    spec = importlib.util.spec_from_file_location("kpi_health_zoo_without_resource", driver)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module._peak_megabytes() is None
