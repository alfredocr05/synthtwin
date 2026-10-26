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
# Lanes MG and PS own what lane HX2's count in people costs the zoo (plan
# P4-D406; batch 4e's integration); lane G2T2 the mixed result column's
# held-back mean at 20,000 rows (batch 4e's records); lane PS2, lane PS's
# follow-up, what PS left held or pooled (the orchestrator, 2026-10-23;
# batch 4g's records); lane ID-ROOM the record numbers its twin writes
# wider, by design (plan P4-D432).
PLAN_LANES = (
    "DST", "RT1", "RT2", "LM1", "LM2", "R7", "FM", "SCH", "G2T", "G2T2", "MG", "PS", "PS2", "ID-ROOM",
    *zoo.ZOO_LANES,
    zoo.NEEDS_OWNER,
)

# The kinds the lane's step names, and the ones its reviews found missing
# (skeptic 1, item 4; Codex, item 6; the tripwire of repair 1, item 6):
# each must be in the catalogue.
REQUIRED_KINDS = (
    "demographics", "encounters", "diagnoses", "procedures", "labs", "medication_orders", "vitals",
    "flowsheet_long", "redcap", "claims", "clinical_notes", "surveys_pro", "wearables", "genomics",
    "imaging", "utf8_accents", "latin1", "byte_order_mark", "crlf_line_endings",
    "semicolon_decimal_comma", "excel_serial_dates", "excel_workbook",
    "perioperative", "clock_times", "multi_value_cells", "tumor_registry", "partial_dates",
    "us_unit_vitals", "dicom_metadata", "sql_server_export", "microbiology",
    "immunizations_providers", "empty_and_constant_columns", "mixed_results", "genomic_ids",
    "risk_and_comorbidity_codes",
    # The repair-2 tripwire's item 6: shapes the product asks about that
    # no table seeded.
    "title_rows_above_header", "day_first_dates", "two_digit_years", "true_false_columns",
)


def _written(name: str, folder: pathlib.Path, n: int = SMALL, seed: int = SEED) -> pathlib.Path:
    return zoo.write_table(zoo.table_named(name), folder, n, seed)


def _pair(
    name: str,
    folder: pathlib.Path,
    change: "object",
    write: "object" = None,
    base: "object" = None,
) -> "list[tuple[str, str, str]]":
    """The analyst's failures on a twin-like copy of a real table: `change(header, rows)` applied.

    `base`, where given, first changes the real table and the copy alike.
    """
    table = zoo.table_named(name)
    header, rows = table.build(SMALL, SEED)
    if base is not None:
        base(header, rows)  # type: ignore[operator]
    real = folder / "real" / f"{table.name}{table.suffix}"
    real.parent.mkdir(parents=True, exist_ok=True)
    real.write_bytes(table.write(header, rows))
    header, rows = table.build(SMALL, SEED)
    if base is not None:
        base(header, rows)  # type: ignore[operator]
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
    titled = _written("titled_report", tmp_path).read_bytes().split(b"\n")
    assert titled[0] == b"Ward Activity Report" and titled[2].startswith(b"report_ref,")
    registry = pandas.read_csv(_written("registry_extract", tmp_path), dtype=str)
    assert (registry["referral_date"].str[:2].astype(int) > 12).any(), "a day past 12 shows the day comes first"
    assert registry["op_date"].str.fullmatch(r"\d\d-[A-Z]{3}-\d\d").all()
    assert registry["dob_short"].str.fullmatch(r"\d\d/\d\d/\d\d").all()
    assert str(pandas.read_csv(_written("registry_extract", tmp_path))["on_waiting_list"].dtype) == "bool"
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


def _unpad(text: str) -> str:
    """Every figure's leading nought dropped: '01/05/1950' as '1/5/1950', '07:42' as '7:42'."""
    return re.sub(r"(?<!\d)0(\d)", r"\1", text)


def _one_patient_repeats(header: "list[str]", rows: "list[list[str]]") -> None:
    zoo.spoil_unique("patient_id")(header, rows)
    place = header.index("patient_id")
    rows[1][place] = rows[0][place]


def _long_tail_codes(header: "list[str]", rows: "list[list[str]]") -> None:
    """ICD-10-CM as a real export holds it: 300 codes on a Zipf tail, most held by fewer than 11 rows."""
    draw = random.Random(5)
    codes: "list[str]" = []
    while len(codes) < 300:
        code = f"{draw.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{draw.randint(0, 99):02d}.{draw.randint(0, 99):02d}"
        codes += [code] if code not in codes else []
    pool = zoo._zipf(tuple(codes))
    pick = random.Random(6)
    place = header.index("icd10_dotted")
    for row in rows:
        row[place] = zoo._pick(pick, pool)


def _codes_in_their_form_not_the_real(header: "list[str]", rows: "list[list[str]]") -> None:
    """Each code's last figure moved by one: the same form, mostly a code the real never writes."""
    place = header.index("icd10_dotted")
    for row in rows:
        code = row[place]
        row[place] = code[:-1] + f"{(int(code[-1]) + 1) % 10}"


def _notes_as_stand_ins(header: "list[str]", rows: "list[list[str]]") -> None:
    """Notes as the 20,000-row twin writes them: 90 % 'group-N', and 1 % keeping a line break."""
    place = header.index("note_text")
    for index in range(len(rows)):
        if index % 10:
            rows[index][place] = f"group-{index % 7 + 1}"
        elif index % 100:
            rows[index][place] = rows[index][place].replace("\n", " ")


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
    # Repair 2. The tripwire's item 2: dates and clocks written unlike the
    # source, in figures' width or letters' case, which the run signature
    # and strptime both let through.
    "dob_us unpadded (1/5/1950)": ("patients", _edit("dob_us", _unpad), None, "forms dob_us"),
    "dob_iso unpadded (1950-1-5)": ("patients", _edit("dob_iso", _unpad), None, "forms dob_iso"),
    "dob_text in capitals (05-JAN-1950)": ("patients", _edit("dob_text", str.upper), None, "forms dob_text"),
    "collected_at unpadded (2024-1-5 9:5)": ("labs", _edit("collected_at", _unpad), None, "forms collected_at"),
    "service_date unpadded": ("claims", _edit("service_date", _unpad), None, "forms service_date"),
    "incision_time unpadded (8:30 PM)": ("perioperative", _edit("incision_time", _unpad), None, "forms incision_time"),
    "incision_time in small letters (08:30 pm)": ("perioperative", _edit("incision_time", str.lower), None, "forms incision_time"),
    "in_room unpadded (7:42)": ("perioperative", _edit("in_room", _unpad), None, "forms in_room"),
    "milliseconds cut to two figures": ("sql_server", _edit("created_dttm", lambda v: v[:-1]), None, "forms created_dttm"),
    "MEDICINE written Medicine, a form lost": ("encounters", _edit("department", lambda v: "Medicine" if v == "MEDICINE" else v), None, "forms department"),
    # The tripwire's item 3: a missing marker the twin drops altogether.
    "the literal NULL never written (middle_initial)": ("sql_server", _edit("middle_initial", lambda v: "A" if v == "NULL" else v), None, "missing spellings middle_initial"),
    "the literal NULL never written (death_date)": ("sql_server", _edit("death_date", lambda v: "2023-06-01" if v == "NULL" else v), None, "missing spellings death_date"),
    "the literal NULL written on a third as many rows": ("sql_server", _edit("middle_initial", lambda v: "A" if v == "NULL" else v, 0.7), None, "missing spellings middle_initial"),
    "REDCap's blank consent_date filled on its other rows": ("redcap", _edit("consent_date", lambda v: v or "2023-06-01"), None, "missing spellings consent_date"),
    # The tripwire's item 4: numbers beside a unit or a mark off by a factor.
    "stature halved": ("vitals", zoo.spoil_scaled("stature", r"(?P<n>\d+) cm", 0.5), None, "the numbers of stature keep their range"),
    "a weight in lb divided by ten": ("us_vitals", zoo.spoil_scaled("weight", r"(?P<n>\d+) lb", 0.1), None, "the numbers of weight keep their range"),
    "temperatures in F plus 100": ("us_vitals", _edit("temp_f", lambda v: f"{float(v.split()[0]) + 100:.1f} F"), None, "the numbers of temp_f keep their range"),
    "uncensored viral loads times 1,000": ("labs", _edit("viral_load", lambda v: v if v.startswith(("<", ">")) else f"{int(v) * 1000}"), None, "the numbers of viral_load keep their range"),
    "weights in lb crowded to the top, the ends kept inside": ("us_vitals", _edit("weight", lambda v: f"{260 - (260 - int(v.split()[0])) // 4} lb"), None, "the numbers of weight keep their range"),
    "the decimal-comma mass index times ten": ("vitals", _edit("mass_index", lambda v: v.replace(",", "") + ",0"), None, "the numbers of mass_index keep their range"),
    # The tripwire's item 1: notes mostly stand-ins; the verify's item 3:
    # quotes gone, and a share of patients lost while one still repeats.
    "notes 90 % 'group-N', 1 % keeping a break": ("notes", _notes_as_stand_ins, None, "stand-ins note_text"),
    "notes 90 % 'group-N', their breaks as a share": ("notes", _notes_as_stand_ins, None, "some note runs over several lines, as a share"),
    "notes' quotes dropped": ("notes", _edit("note_text", lambda v: v.replace('"', "")), None, "some note quotes a phrase"),
    "one patient repeats in encounters": ("encounters", _one_patient_repeats, None, "patients with two rows or more, and three or more, as shares"),
    "one patient repeats in claims": ("claims", _one_patient_repeats, None, "patients with two rows or more, and three or more, as shares"),
    "no patient over two rows in encounters": ("encounters", zoo.spoil_at_most_two("patient_id"), None, "patients with two rows or more, and three or more, as shares"),
    "no patient over two rows in claims": ("claims", zoo.spoil_at_most_two("patient_id"), None, "patients with two rows or more, and three or more, as shares"),
    # The tripwire's item 6: the four shapes no table seeded.
    "the title lines dropped": ("titled_report", _leave, lambda h, r: zoo.csv_bytes(h, r), "under its two title lines the header names report_ref first"),
    "day-first dates written month first": ("registry_extract", _edit("referral_date", lambda v: f"{v[3:5]}/{v[:2]}/{v[6:]}"), None, "referral_date parses as %d/%m/%Y"),
    "two-figure years written with four": ("registry_extract", _edit("op_date", lambda v: v[:7] + "20" + v[7:]), None, "forms op_date"),
    "true and false written as 1 and 0": ("registry_extract", _edit("on_waiting_list", lambda v: "1" if v == "TRUE" else "0"), None, "dtype on_waiting_list"),
}

# The tripwire's item 5: a long-tail code column, where `levels` turns off
# above 30 values, takes a code in its own form that the real never writes.
LONG_TAIL = ("diagnoses_procedures", _codes_in_their_form_not_the_real, None, "codes icd10_dotted", _long_tail_codes)


@pytest.mark.parametrize("attack", sorted(ATTACKS))
def test_a_twin_unlike_its_source_is_named(attack: str, tmp_path: pathlib.Path) -> None:
    name, change, write, wanted = ATTACKS[attack]
    failures = _pair(name, tmp_path, change, write)
    assert wanted in [failure[1] for failure in failures], failures


def test_the_repeat_shares_count_two_rows_and_three() -> None:
    """Each patient's rows: the share holding two or more, and the share holding three or more."""
    import pandas

    assert zoo._repeat_shares(pandas.Series(["a", "a", "a", "b", "b", "c"])) == (0.667, 0.333)
    assert zoo._share_failure((0.84, 0.6), (0.84, 0.0))
    assert not zoo._share_failure((0.84, 0.6), (0.8, 0.65))


def test_a_code_the_real_never_writes_is_named_on_a_long_tail(tmp_path: pathlib.Path) -> None:
    """Above 30 values `levels` says nothing, and a code in its own form passes the pattern and the forms."""
    name, change, write, wanted, base = LONG_TAIL
    control = _pair(name, tmp_path / "control", _leave, write, base)
    assert control == [], control
    failures = _pair(name, tmp_path / "twin", change, write, base)
    names = [failure[1] for failure in failures]
    assert wanted in names, failures
    assert "levels icd10_dotted" not in names and "ICD-10-CM with the dot" not in names


def test_a_twin_unlike_its_source_is_named_in_the_workbook(tmp_path: pathlib.Path) -> None:
    """The survey's missing markers: 'Not asked' lost or spelled 'N/A', -99 written blank."""
    crosscheck.reader()
    lost = _pair("surveys", tmp_path / "lost", _edit("q4_status", lambda v: "NA" if v == "Not asked" else v))
    assert "levels q4_status" in [failure[1] for failure in lost], lost
    spelled = _pair("surveys", tmp_path / "spelled", _edit("q4_status", lambda v: "N/A" if v == "Not asked" else v))
    assert "missing spellings q4_status" in [failure[1] for failure in spelled], spelled
    blank = _pair("surveys", tmp_path / "blank", _edit("q2_score", lambda v: "" if v == "-99" else v))
    assert "missing q2_score" in [failure[1] for failure in blank], blank
    # Repair 2: 'NA' never written (the tripwire's item 3), and a numeric
    # missing code never written (the verify's item 2: `levels` reads
    # every column, whatever dtype pandas infers).
    never = _pair("surveys", tmp_path / "never", _edit("q4_status", lambda v: "No" if v == "NA" else v))
    assert "missing spellings q4_status" in [failure[1] for failure in never], never
    scored = _pair("surveys", tmp_path / "scored", _edit("q2_score", lambda v: "3" if v == "-99" else v))
    assert "levels q2_score" in [failure[1] for failure in scored], scored
    totals = _pair("surveys", tmp_path / "totals", _edit("scale_total", lambda v: "10" if v == "999" else v))
    assert "levels scale_total" in [failure[1] for failure in totals], totals


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
    # `result` is offered `identifier` and not what the person knows of it:
    # since lane HX (plan P4-D401) a blank there would hold it as record
    # numbers, so the person answers `keep` (batch 4d's integration).
    assert given == {"loinc": "code", "result": "keep", "viral_load": "measurement", "patient_id": "identifier"}
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


def test_a_question_about_the_file_is_answered_by_its_subject() -> None:
    """The product names a question about the whole file under `column`, as its subject.

    Before repair 2 the person answered it only where the key was
    `subject`, so no question about the file was ever answered.
    """
    entry = {
        "column": "which row your column names are in",
        "answers_you_can_give": [{"answer": "first-record"}, {"answer": "names"}], "your_answer": "",
    }
    asked, general = zoo.answer_generally(zoo.table_named("titled_report"), {"about_your_file": [entry]})
    assert general and asked[0]["given"] == "names" and entry["your_answer"] == "names"
    entry = {
        "column": "the order of the day and the month in your dates",
        "answers_you_can_give": [{"answer": "month-first"}, {"answer": "day-first"}], "your_answer": "",
    }
    asked, _general = zoo.answer_generally(zoo.table_named("registry_extract"), {"about_your_file": [entry]})
    assert asked[0]["given"] == "day-first"
    asked, _general = zoo.answer_generally(zoo.table_named("claims"), {"about_your_file": [entry]})
    assert asked[0]["given"] == "month-first"


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


def test_a_twin_that_does_not_read_fails_every_kind_of_its_table(tmp_path: pathlib.Path) -> None:
    """The verify's item 1 (a): one ragged row and pandas stops; every kind of the table is failed at 'read'."""
    failures = _pair(
        "diagnoses_procedures", tmp_path, _leave,
        lambda h, r: zoo.csv_bytes(h, r) + b"a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p\n",
    )
    assert {(kind, name) for kind, name, _why in failures} == {("diagnoses", "read"), ("procedures", "read")}
    verdicts = zoo.per_kind([_result("diagnoses_procedures", analyst=[list(failure) for failure in failures])])
    assert not any(verdict["passed"] for verdict in verdicts.values())


def test_a_miss_of_the_whole_file_fails_its_file_kinds() -> None:
    """The verify's item 1 (b): a miss with no column fails the file-level kinds, or every kind of a table without one."""
    verdicts = zoo.per_kind([_result("encounters", misses=[["", "rows.count"]])])
    assert {kind: verdict["failing_step"] for kind, verdict in verdicts.items() if not verdict["passed"]} == {
        "byte_order_mark": "validate", "crlf_line_endings": "validate",
    }
    assert verdicts["encounters"]["passed"] is True
    verdicts = zoo.per_kind([_result("labs", misses=[["", "x"]])])
    assert {kind: verdict["failing_step"] for kind, verdict in verdicts.items()} == {
        "labs": "validate", "mixed_results": "validate",
    }


def test_a_command_that_stops_is_read_by_its_exit(monkeypatch: pytest.MonkeyPatch) -> None:
    """The verify's item 1 (c): a SystemExit(2) is exit 2, never success."""
    from synthtwin import cli

    def stops(arguments: "list[str]") -> int:
        raise SystemExit(2)

    monkeypatch.setattr(cli, "main", stops)
    assert zoo._quietly(["profile", "x"])[0] == 2


def test_the_measures_count_what_they_say() -> None:
    """The verify's item 4: each aggregate key of `zoo_measures`, on results made for it."""
    workbook = _result("surveys", analyst=[["surveys_pro", "Likert words", "why"]])
    delimited = _result("labs", analyst=[["labs", "LOINC codes", "why"]], roles={"a": "identifier", "b": "code"})
    asked = [
        {"column": "patient_id", "offered": ["identifier"], "given": "identifier", "general": True},
        {"column": "the character between your columns", "offered": ["outcome"], "given": "", "general": False},
    ]
    faulty = _result("patients", asked=asked, general=False, analyst_real_errors=["record numbers match PT#######"])
    measured = zoo.zoo_measures([workbook, delimited, faulty])
    first = measured["K-HZ-01"]
    assert first["kinds_passing_end_to_end"] == 2, first
    assert first["kinds_passing_csv"] == 1, "the passing workbook kind is not a delimited one"
    assert first["kinds_csv"] == 4
    assert first["questions_asked"] == 2 and first["questions_not_general"] == 1
    assert first["analyst_errors_on_real"] == 1
    assert first["roles_reached"] == 2 and first["roles"] == ["code", "identifier"]
    assert first["tables"] == 3 and first["tables_generated"] == 3


def test_a_failure_with_only_a_gap_stated_is_counted_apart(monkeypatch: pytest.MonkeyPatch) -> None:
    """The tripwire's item 7: 'needs owner' names a gap, not a lane, and K-HZ-02 counts it apart.

    The catalogue's one such line, the mixed result column's mean at
    20,000 rows, has lane G2T2 since batch 4e's records, so the gap is
    stated here on its own line, in place of that one, and the shipped
    line is held to its lane.
    """
    shipped = zoo.zoo_measures([_result("labs", misses=[["result_value", "mean"]])])
    assert shipped["K-HZ-02"]["failures_needing_owner"] == 0
    assert shipped["kinds"]["mixed_results"]["owners"] == ["G2T2"]
    gap = (zoo.NEEDS_OWNER, "a gap stated and no lane", zoo.covers("miss result_value"))
    lines = tuple(line for line in zoo.OWNERS["mixed_results"] if not re.fullmatch(line[2], "miss result_value"))
    monkeypatch.setitem(zoo.OWNERS, "mixed_results", (*lines, gap))
    owned = zoo.zoo_measures([_result("labs", misses=[["result_value", "mean"]])])
    assert owned["K-HZ-02"]["failures_without_owner"] == 0
    assert owned["K-HZ-02"]["failures_needing_owner"] == 1
    assert owned["kinds"]["mixed_results"]["needing_owner"] == ["miss result_value"]
    laned = zoo.zoo_measures([_result("labs", misses=[["ref_range", "styles"]])])
    assert laned["K-HZ-02"]["failures_needing_owner"] == 0
    assert laned["kinds"]["labs"]["owners"] == ["LM1"]


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


def _driver(monkeypatch: pytest.MonkeyPatch, name: str) -> "object":
    """The slow driver, loaded as a module of its own under `name`."""
    import importlib.util
    import sys

    driver = pathlib.Path(__file__).resolve().parent.parent / "tools" / "measurements" / "kpi_health_zoo.py"
    monkeypatch.setattr(sys, "path", list(sys.path))
    spec = importlib.util.spec_from_file_location(name, driver)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_driver_starts_where_there_is_no_resource_module(monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 9: Windows has no `resource`; the slow driver still loads and leaves memory unmeasured."""
    import sys

    monkeypatch.setitem(sys.modules, "resource", None)
    module = _driver(monkeypatch, "kpi_health_zoo_without_resource")
    assert module._peak_megabytes() is None  # type: ignore[attr-defined]


@pytest.mark.parametrize("reader", [True, False])
def test_the_driver_prints_only_what_it_measured(
    reader: bool, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """The verify's item 4: without the workbook reader the counts over every export are left out, never printed short.

    The judged keys are the delimited exports' own, measured everywhere.
    """
    import json

    module = _driver(monkeypatch, "kpi_health_zoo_printing")
    monkeypatch.setattr(crosscheck, "present", lambda: reader)
    monkeypatch.setattr(zoo, "run_zoo", lambda folder, n, seed=0: [_result(t.name) for t in zoo.runnable_tables()])
    module.main()  # type: ignore[attr-defined]
    printed = {}
    for line in capsys.readouterr().out.splitlines():
        if line.startswith("KPI "):
            record = json.loads(line[4:])
            printed[record["id"]] = record["value"]
    delimited = [table for table in zoo.TABLES if table.suffix == ".csv"]
    delimited_kinds = sum(len(table.kinds) for table in delimited)
    assert printed["K-HZ-01"]["kinds_passing_20000_rows_csv"] == delimited_kinds
    assert printed["K-HZ-03"]["tables_run_csv"] == 2 * len(delimited)
    if reader:
        assert printed["K-HZ-01"]["kinds_passing_20000_rows"] == len(zoo.KINDS)
        assert printed["K-HZ-03"]["tables_run"] == 2 * len(zoo.TABLES)
    else:
        assert "kinds_passing_20000_rows" not in printed["K-HZ-01"]
        assert "tables_run" not in printed["K-HZ-03"]
