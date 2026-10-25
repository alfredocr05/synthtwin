"""The health data zoo widened to every kind of the zoo plan's section 6 (b) (lane E0c, plan P4-D431).

The owner, 2026-10-16: "we should be able to ingest all, and when i say
all, i really mean all type of data that can come in a healthcare
database and reconstruct the twin"; the owner's answer (a) to Z2,
2026-10-24: "every kind of healthcare data" is the CSV and Excel exports
the zoo plan's section 6 lists, native formats deferred.

E0a's catalogue (`tests/health_zoo.py`, forty kinds over twenty-five
exports) stays as it is, byte for byte from its seeds; this module adds
the kinds of section 6 (b) it did not hold, grouped as the plan groups
them -- the roles the zoo never reached, the coding systems, the clinical
domains, the long and system-shaped exports, the file shapes, the HIPAA
and de-identified shapes and the time edge kinds -- and the cases the
repository's records name as this lane's (docs/plans/phase-4-columns.md,
ZR.7 and ZR.9: month-year `MM/YYYY` as its own column, military `HHMM`,
zone words, Caboodle's `DateKey` unanswered, the HL7 `^` component list,
the numeric multi-select, `39w2d` and `37+5`, rsIDs of several lengths,
and the click-order two-pick residual). A kind section 6 (b) names that
E0a's catalogue already holds is MERGED into E0a's, never counted twice
(`MERGED`).

Each kind's columns are read by an analyst check that can go red, and
each check has the spoil that turns it red (`tests/test_health_zoo.py`
runs every one on every table). Every several-rows-per-patient table
names its person column (`Table.person`) and holds at least 100 people
at the suite's 600 rows and 1,000 at the owner's table floor of 20,000
rows. The columns that name a person, a place or a record are read for
their real values in the description and the twin (`Table.leaks`,
HIPAA first).

THIS MODULE MEASURES; IT FIXES NOTHING. The vocabulary is made up for
the battery from the public systems' own shapes; no value comes from a
real table, and every name, address, telephone number, e-mail address
and social security number is invented (telephone numbers in the 555
exchange, social security numbers in the 900 area no person holds).
"""

from __future__ import annotations

import csv
import datetime
import io
import math
import random
import re

import health_zoo as zoo
from health_zoo import (
    JUNK,
    Check,
    Table,
    _bad,
    _bad_numbers,
    _bad_pattern,
    _bad_set,
    _csv_reader,
    _dated,
    _i,
    _levels,
    _listed,
    _pattern,
    _pick,
    _present,
    _r,
    _ranged,
    _repeats,
    _spread,
    _t,
    _zipf,
    csv_bytes,
    covers,
    spoil_cell,
    spoil_every,
    spoil_extra_column,
)

# -- what section 6 (b) names that E0a's catalogue already holds -----------

# Each item of section 6 (b) found in E0a's catalogue, with the kind that
# holds it: merged there, and not a kind of this module.
MERGED = {
    "a clock-only column": "clock_times",
    "an all-blank column (the empty role)": "empty_and_constant_columns",
    "CVX, MVX, NPI (Luhn) and UDI (GS1)": "immunizations_providers",
    "OMIM, HGNC, ClinVar and GA4GH": "genomic_ids",
    "CMS-HCC, APC, CDPS, Charlson, Elixhauser and the clinical classes": "risk_and_comorbidity_codes",
    "perioperative and anesthesia: in, incision and case times, durations, the physical status with its E": "perioperative",
    "problem list and allergies: list cells, NKDA": "multi_value_cells",
    "microbiology's MIC with <= and >=": "microbiology",
    "tumor registry TNM and partial dates": "tumor_registry",
    "long flowsheets (key-value)": "flowsheet_long",
    "a SQL Server export": "sql_server_export",
    "the registry mix of year, month and day": "partial_dates",
    "Safe Harbor age 90+ beside ages to 89": "demographics",
}


def _person(draw: random.Random, people: int) -> str:
    return f"PT{1000000 + draw.randrange(people):07d}"


def _people(n: int) -> int:
    """A several-rows table's people: four rows a person on average, so 150 at 600 rows and 5,000 at 20,000."""
    return max(n // 4, 1)


def _when(draw: random.Random) -> datetime.datetime:
    return datetime.datetime.combine(
        zoo._day(draw, datetime.date(2023, 1, 1), datetime.date(2024, 12, 31)),
        datetime.time(draw.randint(0, 23), draw.randint(0, 59), draw.randint(0, 59)),
    )


def _rare(
    kind: str, name: str, column: str, pattern: str,
    spoil: "object", crowd: "object",
) -> "tuple[Check, Check]":
    """A shape the real holds on a few rows, as two checks: present at all (red on `spoil`), and on its
    share of the rows (red on `crowd`, which writes the shape on many more rows than the real does:
    a shape on a twentieth of the rows taken away moves its share by less than the tolerance)."""
    present, share = _present(kind, name, column, pattern, spoil)  # type: ignore[arg-type]
    return present, Check(share.kind, share.name, share.mode, share.run, share.column, crowd)  # type: ignore[arg-type]


def crowd(column: str, value: str, every: int = 3) -> "object":
    """A spoil: every `every`-th cell of a column written as `value`."""

    def change(header: "list[str]", rows: "list[list[str]]") -> None:
        place = header.index(column)
        for index in range(0, len(rows), every):
            rows[index][place] = value

    return change


def _not_in(values: "tuple[str, ...]") -> "object":
    """The cells of a text column that are none of the words named."""

    def cells(series: object) -> object:
        present = series.dropna().astype(str)  # type: ignore[attr-defined]
        return present[~present.isin(list(values))]

    return cells


# -- family 1: the roles the zoo never reached -------------------------------

PROTEIN = (("NEG", 50.0), ("TRACE", 15.0), ("1+", 15.0), ("2+", 10.0), ("3+", 7.0), ("4+", 3.0))
SNELLEN = (
    ("20/20", 25.0), ("20/25", 20.0), ("20/30", 15.0), ("20/40", 12.0), ("20/50", 8.0), ("20/70", 7.0),
    ("20/100", 5.0), ("20/200", 4.0), ("CF", 2.0), ("HM", 2.0),
)
SNELLEN_LINES = {"20", "25", "30", "40", "50", "70", "100", "200"}
TITERS = (
    ("<1:40", 25.0), ("1:40", 15.0), ("1:80", 20.0), ("1:160", 18.0), ("1:320", 12.0), ("1:640", 7.0),
    (">1:1280", 3.0),
)
DILUTIONS = {"40", "80", "160", "320", "640", "1280"}


def bedside_results(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Results whose numbers stand beside words and marks: a meter's HI and LO, a dipstick, Snellen, titers, an instrument's exponents."""
    draw = random.Random(seed)
    people = _people(n)
    header = [
        "patient_id", "glucose", "urine_protein", "visual_acuity", "rubella_titer", "wbc_count", "hiv_rna",
    ]
    rows: "list[list[str]]" = []
    for _index in range(n):
        level = draw.random()
        glucose = "HI" if level < 0.03 else "LO" if level < 0.05 else f"{draw.randint(40, 400)}"
        load = draw.random()
        if load < 0.35:
            rna = "TND"
        elif load < 0.5:
            rna = "<20"
        else:
            rna = f"{min(10_000_000, 20 + int(draw.lognormvariate(8.0, 2.0)))}"
        rows += [[
            _person(draw, people),
            glucose,
            _pick(draw, PROTEIN),
            _pick(draw, SNELLEN),
            _pick(draw, TITERS),
            f"{draw.lognormvariate(math.log(7500.0), 0.35):.1E}",
            rna,
        ]]
    return header, rows


def _snellen_off(series: object) -> int:
    lines = series.dropna().astype(str)  # type: ignore[attr-defined]
    lines = lines[lines.str.startswith("20/")]
    return _bad_set(lines.str[3:], SNELLEN_LINES)


def _dilutions_off(series: object) -> int:
    figures = series.dropna().astype(str).str.replace(r"^[<>]?1:", "", regex=True)  # type: ignore[attr-defined]
    return _bad_set(figures, DILUTIONS)


def instrument_magnitudes(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """An instrument's export of magnitudes whose spread passes a double's range (the numeric_unrepresentable role)."""
    draw = random.Random(seed)
    header = ["sample_id", "magnitude", "instrument"]
    rows: "list[list[str]]" = []
    for index in range(n):
        rows += [[
            f"S{500000 + index}",
            f"{draw.uniform(1.0, 9.999):.3f}E+{draw.randint(300, 320)}",
            draw.choice(("A", "B")),
        ]]
    return header, rows


def _exponents(series: object) -> "tuple[float, float, float] | None":
    found: "list[float]" = []
    for text in series.dropna().astype(str):  # type: ignore[attr-defined]
        match = re.fullmatch(r"\d\.\d+E\+(\d+)", text)
        if match:
            found += [float(match.group(1))]
    return _spread(found)


def _past_a_double(series: object) -> float:
    """The share of the magnitudes past the largest finite double (about 1.8E+308)."""
    present = series.dropna().astype(str)  # type: ignore[attr-defined]
    if not len(present):
        return 0.0
    past = 0
    for text in present:
        match = re.fullmatch(r"(\d\.\d+)E\+(\d+)", text)
        past += 1 if match and (int(match.group(2)) > 308 or (int(match.group(2)) == 308 and float(match.group(1)) > 1.797)) else 0
    return round(past / len(present), 3)


def critical_care_charting(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A critical-care flowsheet saved from a spreadsheet as tab-delimited text: military times, a monitor's milliseconds, oxygen."""
    draw = random.Random(seed)
    people = _people(n)
    header = ["patient_id", "chart_date", "chart_time", "monitor_clock", "o2_delivery", "fio2", "peep", "vent_mode"]
    rows: "list[list[str]]" = []
    for _index in range(n):
        moment = _when(draw)
        on_vent = draw.random() < 0.45
        if on_vent:
            delivery, fio2 = "Ventilator", f"{draw.choice(range(30, 101, 5))}%"
            peep, mode = draw.choice(("5", "8", "10", "12", "14")), draw.choice(("AC/VC", "SIMV", "PSV", "CPAP"))
        elif draw.random() < 0.6:
            delivery, fio2, peep, mode = "RA", "21%", "", ""
        else:
            litres = draw.randint(1, 6)
            delivery, fio2, peep, mode = f"{litres} L/min", f"{21 + 4 * litres}%", "", ""
        rows += [[
            _person(draw, people),
            moment.date().isoformat(),
            moment.strftime("%H%M"),
            moment.strftime("%H:%M:%S") + f".{draw.randint(0, 999):03d}",
            delivery,
            fio2,
            peep,
            mode,
        ]]
    return header, rows


FAMILY_ROLES: "tuple[Table, ...]" = (
    Table(
        "bedside_results", ".csv", bedside_results,
        lambda header, rows: csv_bytes(header, rows),
        {
            "labelled_results": ("patient_id", "glucose", "urine_protein", "visual_acuity", "rubella_titer"),
            "lab_instrument_results": ("wbc_count", "hiv_rna"),
        },
        {"patient_id": "identifier", "glucose": "measurement", "wbc_count": "measurement", "hiv_rna": "measurement"},
        _csv_reader(),
        (
            *_repeats("labelled_results"),
            _pattern("labelled_results", "a glucose is a number, HI or LO", "glucose", r"\d{2,3}|HI|LO"),
            _bad("labelled_results", "the glucose numbers read past HI and LO", "glucose",
                 lambda f: _bad_numbers(_not_in(("HI", "LO"))(_t("glucose")(f)))),  # type: ignore[operator]
            *_rare("labelled_results", "some glucose is past the meter's range", "glucose", r"^(?:HI|LO)$",
                   spoil_every("glucose", lambda v: "600" if v == "HI" else "20" if v == "LO" else v),
                   crowd("glucose", "HI")),
            _ranged("labelled_results", "glucose", r"(?P<n>\d+)"),
            _listed("labelled_results", "dipstick protein grades", "urine_protein", _levels(PROTEIN)),
            _pattern("labelled_results", "visual acuity in Snellen, CF or HM", "visual_acuity", r"20/\d{2,3}|CF|HM"),
            _bad("labelled_results", "Snellen denominators are chart lines", "visual_acuity",
                 lambda f: _snellen_off(_t("visual_acuity")(f)), spoil_cell("visual_acuity", "20/33")),
            _pattern("labelled_results", "titers written 1:N", "rubella_titer", r"[<>]?1:\d+"),
            _bad("labelled_results", "titers are two-fold dilutions from 1:40", "rubella_titer",
                 lambda f: _dilutions_off(_t("rubella_titer")(f)), spoil_cell("rubella_titer", "1:100")),
            _pattern("lab_instrument_results", "counts in scientific notation", "wbc_count", r"\d\.\dE\+0\d"),
            _bad("lab_instrument_results", "the counts read as numbers", "wbc_count",
                 lambda f: _bad_numbers(_t("wbc_count")(f))),
            _ranged("lab_instrument_results", "wbc_count", r"(?P<n>\d\.\dE\+0\d)"),
            _pattern("lab_instrument_results", "a viral load is a number, TND or <20", "hiv_rna", r"TND|<20|\d+"),
            *_present("lab_instrument_results", "some load is target not detected", "hiv_rna", r"^TND$",
                      spoil_every("hiv_rna", lambda v: "20" if v == "TND" else v)),
            *_present("lab_instrument_results", "some load is below 20", "hiv_rna", r"^<20$",
                      spoil_every("hiv_rna", lambda v: "20" if v == "<20" else v)),
            _bad("lab_instrument_results", "the loads read past TND and <20", "hiv_rna",
                 lambda f: _bad_numbers(_not_in(("TND", "<20"))(_t("hiv_rna")(f)))),  # type: ignore[operator]
            _ranged("lab_instrument_results", "hiv_rna", r"(?P<n>\d+)", 1000.0),
        ),
        person="patient_id",
    ),
    Table(
        "instrument_magnitudes", ".csv", instrument_magnitudes,
        lambda header, rows: csv_bytes(header, rows),
        {"numeric_unrepresentable": ("sample_id", "magnitude", "instrument")},
        {"sample_id": "identifier", "magnitude": "measurement"},
        _csv_reader(),
        (
            _pattern("numeric_unrepresentable", "magnitudes written d.dddE+3dd", "magnitude", r"\d\.\d{3}E\+3[0-2]\d"),
            Check("numeric_unrepresentable", "the exponents keep their range", "range",
                  lambda f: _exponents(_t("magnitude")(f)), "magnitude",
                  spoil_every("magnitude", lambda v: re.sub(r"E\+3(\d\d)", lambda m: f"E+{int(m.group(1)) + 100}", v))),
            Check("numeric_unrepresentable", "magnitudes past a double's range, as a share", "share",
                  lambda f: _past_a_double(_t("magnitude")(f)), "magnitude",
                  spoil_every("magnitude", lambda v: v[:6] + "+300")),
            _listed("numeric_unrepresentable", "instruments", "instrument", {"A", "B"}),
        ),
    ),
    Table(
        "critical_care_charting", ".txt", critical_care_charting,
        lambda header, rows: csv_bytes(header, rows, delimiter="\t"),
        {
            "tab_delimited": (),
            "ventilator_settings": ("patient_id", "chart_date", "o2_delivery", "fio2", "peep", "vent_mode"),
            "compact_and_fraction_clocks": ("chart_time", "monitor_clock"),
        },
        {"patient_id": "identifier", "chart_time": "keep", "monitor_clock": "keep", "fio2": "measurement", "peep": "measurement"},
        _csv_reader(sep="\t"),
        (
            Check("tab_delimited", "the file splits into eight columns", "same",
                  lambda f: int(f["inferred"].shape[1]), "", spoil_extra_column),  # type: ignore[attr-defined]
            *_repeats("ventilator_settings"),
            _dated("ventilator_settings", "chart_date parses as %Y-%m-%d", "chart_date", "%Y-%m-%d"),
            _pattern("ventilator_settings", "oxygen is RA, litres a minute or a ventilator", "o2_delivery",
                     r"RA|[1-6] L/min|Ventilator"),
            *_present("ventilator_settings", "some patient breathes room air (RA)", "o2_delivery", r"^RA$",
                      spoil_every("o2_delivery", lambda v: "2 L/min" if v == "RA" else v)),
            _ranged("ventilator_settings", "o2_delivery", r"(?P<n>\d) L/min"),
            _pattern("ventilator_settings", "FiO2 with %", "fio2", r"\d{2,3}%"),
            _ranged("ventilator_settings", "fio2", r"(?P<n>\d+)%", 0.5),
            _listed("ventilator_settings", "PEEP settings", "peep", {"5", "8", "10", "12", "14"}),
            _listed("ventilator_settings", "ventilator modes", "vent_mode", {"AC/VC", "SIMV", "PSV", "CPAP"}),
            _pattern("compact_and_fraction_clocks", "military times HHMM", "chart_time", r"([01]\d|2[0-3])[0-5]\d"),
            _dated("compact_and_fraction_clocks", "chart_time parses as %H%M", "chart_time", "%H%M"),
            *_present("compact_and_fraction_clocks", "some time before ten keeps its leading nought", "chart_time", r"^0\d{3}$",
                      spoil_every("chart_time", lambda v: f"{int(v)}")),
            _dated("compact_and_fraction_clocks", "monitor_clock parses as %H:%M:%S.%f", "monitor_clock", "%H:%M:%S.%f"),
            _pattern("compact_and_fraction_clocks", "clocks keep three figures of milliseconds", "monitor_clock",
                     r"\d\d:\d\d:\d\d\.\d{3}"),
            *_present("compact_and_fraction_clocks", "some clock carries its milliseconds", "monitor_clock", r"\.(?!000$)\d{3}$",
                      spoil_every("monitor_clock", lambda v: v[:9] + "000")),
        ),
        separator="tab",
        person="patient_id",
    ),
)

# -- family 2: the clinical domains, part 1 -------------------------------------

MEDICINES = _zipf((
    "Metformin", "Lisinopril", "Acetaminophen", "Insulin glargine", "Heparin", "Ondansetron", "Morphine",
    "Vancomycin", "Furosemide", "Albuterol", "Pantoprazole", "Enoxaparin",
))
ATC_OF = {
    "Metformin": "A10BA02", "Lisinopril": "C09AA03", "Acetaminophen": "N02BE01", "Insulin glargine": "A10AE04",
    "Heparin": "B01AB01", "Ondansetron": "A04AA01", "Morphine": "N02AA01", "Vancomycin": "J01XA01",
    "Furosemide": "C03CA01", "Albuterol": "R03AC02", "Pantoprazole": "A02BC02", "Enoxaparin": "B01AB05",
}
DOSE_OF = {
    "Metformin": "500 mg", "Lisinopril": "10 mg", "Acetaminophen": "650 mg", "Insulin glargine": "20 units",
    "Heparin": "5000 units", "Ondansetron": "4 mg", "Morphine": "2 mg", "Vancomycin": "1 g",
    "Furosemide": "40 mg", "Albuterol": "2 puffs", "Pantoprazole": "40 mg", "Enoxaparin": "40 mg",
}
ADMIN_STATUS = (("Given", 80.0), ("Held", 10.0), ("Refused", 5.0), ("Not Given", 5.0))
HELD_REASONS = (("NPO", 40.0), ("Patient refused", 25.0), ("Hold parameters", 25.0), ("Not available", 10.0))


def medication_administration(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A medication administration record: dose and unit, given or held and why, PRN, the ATC class."""
    draw = random.Random(seed)
    people = _people(n)
    header = [
        "mar_id", "patient_id", "scheduled_at", "drug", "atc_code", "dose_given", "admin_status", "given_at",
        "prn", "held_reason",
    ]
    rows: "list[list[str]]" = []
    for index in range(n):
        drug = _pick(draw, MEDICINES)
        scheduled = _when(draw).replace(minute=0, second=0)
        status = _pick(draw, ADMIN_STATUS)
        given = status == "Given"
        rows += [[
            f"MAR{60000000 + index}",
            _person(draw, people),
            scheduled.strftime("%Y-%m-%d %H:%M"),
            drug,
            ATC_OF[drug],
            DOSE_OF[drug] if given else "",
            status,
            (scheduled + datetime.timedelta(minutes=draw.randint(0, 90))).strftime("%Y-%m-%d %H:%M") if given else "",
            "Y" if draw.random() < 0.2 else "N",
            "" if given else _pick(draw, HELD_REASONS),
        ]]
    return header, rows


def quoted_bytes(header: "list[str]", rows: "list[list[str]]") -> bytes:
    """A delimited table with every field inside quotes, as some exporters write every file."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n", quoting=csv.QUOTE_ALL)
    writer.writerow(header)
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def _every_field_quoted(data: object) -> bool:
    """Whether every field of every line opens and closes with a quote (no field holds a line break here)."""
    if not isinstance(data, bytes):
        return False
    for line in data.decode("utf-8").splitlines():
        for field in next(csv.reader([line], quoting=csv.QUOTE_NONE, escapechar=None)):
            if not (len(field) >= 2 and field.startswith('"') and field.endswith('"')):
                return False
    return True


NDC_FORMS = (
    ("0002-3227-30", 8.0), ("0006-0749-54", 7.0), ("0009-0090-01", 8.0), ("0013-2626-81", 7.0),
    ("50090-123-01", 8.0), ("60505-257-05", 7.0), ("00093-715-56", 8.0), ("68180-513-09", 7.0),
    ("00071-0155-2", 10.0), ("00378-0208-1", 10.0), ("00591-0405-1", 10.0), ("00904-6278-6", 10.0),
)
DAYS_SUPPLY = (
    ("30", 55.0), ("90", 25.0), ("7", 5.0), ("14", 4.0), ("10", 3.0), ("5", 2.0), ("21", 2.0), ("28", 2.0),
    ("84", 1.0), ("60", 1.0),
)
QUANTITIES = (("30", 30.0), ("60", 15.0), ("90", 20.0), ("15.5", 5.0), ("120", 10.0), ("28", 10.0), ("1", 10.0))
DAW = (("0", 82.0), ("1", 8.0), ("2", 4.0), ("3", 2.0), ("5", 2.0), ("7", 1.0), ("8", 1.0))


def pharmacy_fills(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A pharmacy's dispensing file: NDC in its three labeler forms, days supply, quantity, DAW codes."""
    draw = random.Random(seed)
    people = _people(n)
    header = ["rx_number", "patient_id", "fill_date", "ndc", "quantity", "days_supply", "daw_code"]
    rows: "list[list[str]]" = []
    for index in range(n):
        rows += [[
            f"RX{7000000 + index}",
            _person(draw, people),
            _when(draw).date().isoformat(),
            _pick(draw, NDC_FORMS),
            _pick(draw, QUANTITIES),
            _pick(draw, DAYS_SUPPLY),
            _pick(draw, DAW),
        ]]
    return header, rows


SMOKING = (
    ("Never smoker", 55.0), ("Former smoker", 25.0), ("Current every day smoker", 10.0),
    ("Current some day smoker", 5.0), ("Unknown if ever smoked", 5.0),
)
ALCOHOL = (("None", 50.0), ("Social", 35.0), ("Daily", 5.0), ("Declined", 10.0))


def prenatal_visits(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Prenatal visits: gestational age written 37+5 and 39w2d, gravida and para (G2P1), the social history."""
    draw = random.Random(seed)
    people = _people(n)
    header = [
        "patient_id", "visit_date", "gest_age_plus", "gest_age_wd", "gravida_para", "smoking_status",
        "pack_years", "alcohol_use",
    ]
    rows: "list[list[str]]" = []
    for _index in range(n):
        gravida = draw.choice((1, 1, 1, 2, 2, 2, 3, 3, 4, 5, 6))
        smoking = _pick(draw, SMOKING)
        rows += [[
            _person(draw, people),
            _when(draw).date().isoformat(),
            f"{draw.randint(6, 41)}+{draw.randint(0, 6)}",
            f"{draw.randint(6, 41)}w{draw.randint(0, 6)}d",
            f"G{gravida}P{draw.randint(0, gravida - 1)}",
            smoking,
            "" if smoking.startswith(("Never", "Unknown")) else f"{draw.uniform(0.5, 40.0):.1f}",
            _pick(draw, ALCOHOL),
        ]]
    return header, rows


def _gestation_days(series: object, mark: str) -> "tuple[float, float, float] | None":
    """A gestational age read as days: weeks times seven plus days, '37+5' or '37w5d'."""
    pattern = r"(\d{1,2})\+([0-6])" if mark == "+" else r"(\d{1,2})w([0-6])d"
    days: "list[float]" = []
    for text in series.dropna().astype(str):  # type: ignore[attr-defined]
        match = re.fullmatch(pattern, text)
        if match:
            days += [float(7 * int(match.group(1)) + int(match.group(2)))]
    return _spread(days)


def _doubled_weeks(value: str) -> str:
    match = re.fullmatch(r"(\d{1,2})([+w])(.*)", value)
    return f"{2 * int(match.group(1))}{match.group(2)}{match.group(3)}" if match else value


def _para_past_gravida(series: object) -> int:
    bad = 0
    for text in series.dropna().astype(str):  # type: ignore[attr-defined]
        match = re.fullmatch(r"G(\d+)P(\d+)", text)
        bad += 0 if match and int(match.group(2)) < int(match.group(1)) else 1
    return bad


def well_child(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Well-child visits: ages in days, months and years ('14 d', '3 mo', '2 yr'), growth percentiles with <1 and >99."""
    draw = random.Random(seed)
    people = _people(n)
    header = ["patient_id", "visit_date", "age_text", "wt_kg", "weight_pct", "head_circ"]
    rows: "list[list[str]]" = []
    for _index in range(n):
        days = draw.randint(3, 1800)
        if days < 30:
            age = f"{days} d"
        elif days < 730:
            age = f"{days // 30} mo"
        else:
            age = f"{days // 365} yr"
        level = draw.random()
        percentile = "<1" if level < 0.03 else ">99" if level < 0.06 else f"{draw.randint(1, 99)}"
        rows += [[
            _person(draw, people),
            _when(draw).date().isoformat(),
            age,
            f"{3.3 + days * 0.008 + draw.gauss(0, 0.6):.2f}",
            percentile,
            f"{34.5 + 12.0 * (1 - math.exp(-days / 300.0)) + draw.gauss(0, 0.8):.1f} cm",
        ]]
    return header, rows


AGE_UNITS = {"d": 1.0, "mo": 30.4, "yr": 365.25}


def _age_days(series: object) -> "tuple[float, float, float] | None":
    days: "list[float]" = []
    for text in series.dropna().astype(str):  # type: ignore[attr-defined]
        match = re.fullmatch(r"(\d{1,4}) (d|mo|yr)", text)
        if match:
            days += [round(int(match.group(1)) * AGE_UNITS[match.group(2)], 1)]
    return _spread(days)


RHYTHMS = (
    ("Sinus rhythm", 60.0), ("Sinus tachycardia", 12.0), ("Sinus bradycardia", 10.0),
    ("Atrial fibrillation", 12.0), ("Atrial flutter", 3.0), ("Paced rhythm", 3.0),
)


def ecg_reads(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """ECG reads: intervals in milliseconds (PR written '164 ms', blank in atrial fibrillation), QTc, rhythm, axis."""
    draw = random.Random(seed)
    people = _people(n)
    header = ["patient_id", "ecg_at", "vent_rate", "pr_interval", "qrs_duration", "qtc_interval", "rhythm", "axis"]
    rows: "list[list[str]]" = []
    for _index in range(n):
        rhythm = _pick(draw, RHYTHMS)
        rows += [[
            _person(draw, people),
            _when(draw).strftime("%Y-%m-%d %H:%M:%S"),
            f"{draw.randint(40, 150)}",
            "" if rhythm.startswith("Atrial") else f"{draw.randint(120, 220)} ms",
            f"{draw.randint(70, 160)}",
            f"{draw.randint(360, 520)}",
            rhythm,
            f"{draw.randint(-90, 180)}",
        ]]
    return header, rows


GENERA = (
    "Staphylococcus", "Streptococcus", "Enterococcus", "Escherichia", "Klebsiella", "Pseudomonas", "Enterobacter",
    "Proteus", "Serratia", "Acinetobacter", "Candida", "Bacteroides", "Clostridioides", "Haemophilus",
    "Neisseria", "Citrobacter", "Morganella", "Stenotrophomonas", "Corynebacterium", "Moraxella",
)
SPECIES = (
    "aureus", "epidermidis", "pneumoniae", "faecalis", "faecium", "coli", "aeruginosa", "cloacae", "mirabilis",
    "marcescens", "baumannii", "albicans", "glabrata", "fragilis", "difficile", "influenzae", "meningitidis",
    "freundii", "morganii", "maltophilia", "striatum", "catarrhalis", "agalactiae", "pyogenes", "lugdunensis",
    "oxytoca", "aerogenes", "vulgaris", "parapsilosis", "tropicalis",
)
# 150 organism names on a Zipf tail, beside the two words a culture
# writes when it grows nothing named.
ORGANISM_TAIL = _zipf(tuple(
    f"{GENERA[place % len(GENERA)]} {SPECIES[(place * 7 + place // len(GENERA)) % len(SPECIES)]}"
    for place in range(150)
))
SPECIMENS = (("Blood", 35.0), ("Urine", 35.0), ("Sputum", 15.0), ("Wound", 15.0))
GROWTH = (("Heavy", 30.0), ("Moderate", 30.0), ("Light", 25.0), ("Rare", 15.0))


def culture_results(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Culture results: organism names as a long tail, beside 'No growth' and 'Mixed flora'."""
    draw = random.Random(seed)
    people = _people(n)
    header = ["isolate_id", "patient_id", "specimen", "organism", "growth"]
    rows: "list[list[str]]" = []
    for index in range(n):
        level = draw.random()
        organism = "No growth" if level < 0.2 else "Mixed flora" if level < 0.25 else _pick(draw, ORGANISM_TAIL)
        rows += [[
            f"ISO{80000000 + index}",
            _person(draw, people),
            _pick(draw, SPECIMENS),
            organism,
            "" if organism == "No growth" else _pick(draw, GROWTH),
        ]]
    return header, rows


EXAMS = ("CT CHEST WITH CONTRAST", "MRI BRAIN WITHOUT CONTRAST", "XR CHEST 2 VIEWS", "US ABDOMEN COMPLETE")
READERS = (
    "Alan Brooks", "Maria Chen", "Samuel Ortiz", "Priya Raman", "Helen Novak", "David Okafor", "Laura Silva",
    "Tomas Weber",
)
OBSERVED = (
    "There is a 4 mm nodule in the right upper lobe.", "No pleural effusion.", "Mild degenerative change.",
    "The liver is normal in size.", "Small hiatal hernia.", "No acute intracranial hemorrhage.",
    "Scattered white matter hyperintensities.", "Heart size is normal.",
)
IMPRESSIONS = (
    "Stable compared with the prior study.", "Recommend follow-up in 12 months.", "No acute process.",
    "Result discussed with the ordering clinician.",
)
TEMPLATED = r"EXAM: [A-Z0-9 ]+\nOBSERVED: No acute abnormality\.\nIMPRESSION: Normal study\.\nElectronically signed by: Dr\. [A-Z][a-z]+ [A-Z][a-z]+"
EXCEL_CELL = 32_767


def reports(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Radiology and pathology reports under their headings, half of them a template that names its reader;
    an addendum column whose rare cells run past Excel's 32,767 characters."""
    draw = random.Random(seed)
    people = _people(n)
    header = ["report_id", "patient_id", "report_type", "report_text", "addendum"]
    rows: "list[list[str]]" = []
    for index in range(n):
        exam = draw.choice(EXAMS)
        reader = draw.choice(READERS)
        if draw.random() < 0.5:
            text = (
                f"EXAM: {exam}\nOBSERVED: No acute abnormality.\nIMPRESSION: Normal study.\n"
                f"Electronically signed by: Dr. {reader}"
            )
        else:
            found = " ".join(draw.sample(OBSERVED, draw.randint(1, 4)))
            text = f"EXAM: {exam}\nOBSERVED: {found}\nIMPRESSION: {draw.choice(IMPRESSIONS)}"
        level = draw.random()
        if level < 0.025:
            addendum = " ".join(draw.choice(OBSERVED) for _place in range(draw.randint(1100, 1300)))
        elif level < 0.05:
            addendum = "No addendum."
        else:
            addendum = ""
        rows += [[
            f"RPT{90000000 + index}",
            _person(draw, people),
            "Radiology" if draw.random() < 0.8 else "Pathology",
            text,
            addendum,
        ]]
    return header, rows


def _share_templated(series: object) -> float:
    cells = series.fillna("").astype(str)  # type: ignore[attr-defined]
    return round(float(cells.str.fullmatch(TEMPLATED).mean()), 3) if len(cells) else 0.0


def _past_excel(series: object) -> float:
    cells = series.fillna("").astype(str)  # type: ignore[attr-defined]
    return round(float((cells.str.len() > EXCEL_CELL).mean()), 3) if len(cells) else 0.0


def _any_past_excel(series: object) -> bool:
    cells = series.dropna().astype(str)  # type: ignore[attr-defined]
    return bool((cells.str.len() > EXCEL_CELL).any())


def _long_addendum(every: int) -> "object":
    def change(header: "list[str]", rows: "list[list[str]]") -> None:
        place = header.index("addendum")
        for index in range(0, len(rows), every):
            rows[index][place] = "No pleural effusion. " * 1700

    return change


DIAGNOSIS_SITES = _zipf(("C509", "C187", "C341", "C619", "C649", "C220"))
HISTOLOGY = _zipf(("8500", "8140", "8070", "8520", "9680", "8010"))
GRADES = (("1", 20.0), ("2", 35.0), ("3", 25.0), ("4", 5.0), ("9", 15.0))
PATH_T = (
    ("pT1mi", 3.0), ("pT1a", 8.0), ("pT1b", 10.0), ("pT1c", 20.0), ("pT2", 25.0), ("pT3", 15.0), ("pT4b", 4.0),
    ("pTX", 5.0), ("pTis", 10.0),
)
AIS_CODES = _zipf((
    "450203", "140651", "853422", "752100", "650616", "441002", "856100", "210402", "541822", "160806",
    "710402", "816001",
))


def registry_extract_naaccr(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A state registry's extract: NAACCR dates to the day, the month or the year (YYYYMMDD, YYYYMM, YYYY),
    site and histology without their marks, behaviour and grade, pT1mi, and a trauma registry's AIS codes."""
    draw = random.Random(seed)
    header = [
        "case_ref", "date_of_diagnosis", "primary_site", "histology", "behavior", "grade", "path_t", "ais_code",
        "injury_date",
    ]
    rows: "list[list[str]]" = []
    for index in range(n):
        known = zoo._day(draw, datetime.date(1995, 1, 1), datetime.date(2023, 12, 31))
        level = draw.random()
        when = known.strftime("%Y%m%d") if level < 0.6 else known.strftime("%Y%m") if level < 0.85 else f"{known.year}"
        rows += [[
            f"NC{30000000 + index}",
            when,
            _pick(draw, DIAGNOSIS_SITES),
            _pick(draw, HISTOLOGY),
            "3" if draw.random() < 0.9 else "2",
            _pick(draw, GRADES),
            _pick(draw, PATH_T),
            f"{_pick(draw, AIS_CODES)}.{draw.randint(1, 6)}",
            zoo._day(draw, datetime.date(2015, 1, 1), datetime.date(2024, 12, 31)).strftime("%Y%m%d"),
        ]]
    return header, rows


def _naaccr_dates_bad(series: object) -> int:
    bad = 0
    for text in series.dropna().astype(str):  # type: ignore[attr-defined]
        form = {8: "%Y%m%d", 6: "%Y%m", 4: "%Y"}.get(len(text))
        try:
            parsed = datetime.datetime.strptime(text, form) if form else None
        except ValueError:
            parsed = None
        bad += 0 if parsed and 1990 <= parsed.year <= 2030 else 1
    return bad


def _severity(series: object) -> "tuple[float, float, float] | None":
    found = [float(text[-1]) for text in series.dropna().astype(str) if re.fullmatch(r"\d{6}\.[1-6]", text)]  # type: ignore[attr-defined]
    return _spread(found)


APPOINTMENT_STATUS = (("Completed", 70.0), ("No Show", 12.0), ("Cancelled", 12.0), ("Rescheduled", 6.0))


def appointments(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Appointment slots on a quarter-hour grid, an evening clinic's slots ending at 24:00, no-shows."""
    draw = random.Random(seed)
    people = _people(n)
    header = ["appt_id", "patient_id", "appt_date", "slot_start", "slot_end", "slot_minutes", "appt_status", "no_show"]
    rows: "list[list[str]]" = []
    for index in range(n):
        minutes = draw.choice((15, 30, 30, 45, 60))
        if draw.random() < 0.15:
            start = 24 * 60 - minutes
        else:
            start = draw.randint(7 * 4, 22 * 4) * 15
        end = start + minutes
        status = _pick(draw, APPOINTMENT_STATUS)
        rows += [[
            f"APT{40000000 + index}",
            _person(draw, people),
            _when(draw).date().isoformat(),
            f"{start // 60:02d}:{start % 60:02d}",
            f"{end // 60:02d}:{end % 60:02d}",
            f"{minutes}",
            status,
            "Y" if status == "No Show" else "N",
        ]]
    return header, rows


FAMILY_CLINICAL_A: "tuple[Table, ...]" = (
    Table(
        "medication_administration", ".csv", medication_administration,
        quoted_bytes,
        {
            "all_fields_quoted": (),
            "medication_administration": (
                "mar_id", "patient_id", "scheduled_at", "drug", "atc_code", "dose_given", "admin_status",
                "given_at", "prn", "held_reason",
            ),
        },
        {"mar_id": "identifier", "patient_id": "identifier", "atc_code": "code"},
        _csv_reader(),
        (
            Check("all_fields_quoted", "every field of every line is quoted", "same",
                  lambda f: _every_field_quoted(f.get("bytes")), "", lambda header, rows: None,
                  lambda header, rows: csv_bytes(header, rows)),
            *_repeats("medication_administration"),
            _dated("medication_administration", "scheduled_at parses as %Y-%m-%d %H:%M", "scheduled_at", "%Y-%m-%d %H:%M"),
            _dated("medication_administration", "given_at parses as %Y-%m-%d %H:%M", "given_at", "%Y-%m-%d %H:%M"),
            _listed("medication_administration", "medicines", "drug", _levels(MEDICINES)),
            _pattern("medication_administration", "ATC codes", "atc_code", r"[A-Z]\d\d[A-Z]{2}\d\d"),
            _pattern("medication_administration", "a dose and its unit", "dose_given", r"\d+(\.\d+)? (mg|g|units|puffs)"),
            _listed("medication_administration", "given, held, refused or not given", "admin_status", _levels(ADMIN_STATUS)),
            _listed("medication_administration", "PRN Y or N", "prn", {"Y", "N"}),
            _listed("medication_administration", "reasons a dose is held", "held_reason", _levels(HELD_REASONS)),
        ),
        person="patient_id",
    ),
    Table(
        "pharmacy_fills", ".csv", pharmacy_fills,
        lambda header, rows: csv_bytes(header, rows),
        {"pharmacy_dispensing": ("rx_number", "patient_id", "fill_date", "ndc", "quantity", "days_supply", "daw_code")},
        {
            "rx_number": "identifier", "patient_id": "identifier", "ndc": "code", "quantity": "measurement",
            "days_supply": "measurement", "daw_code": "code",
        },
        _csv_reader(),
        (
            *_repeats("pharmacy_dispensing"),
            _dated("pharmacy_dispensing", "fill_date parses as %Y-%m-%d", "fill_date", "%Y-%m-%d"),
            _pattern("pharmacy_dispensing", "NDC in its 4-4-2, 5-3-2 and 5-4-1 forms", "ndc",
                     r"\d{4}-\d{4}-\d{2}|\d{5}-\d{3}-\d{2}|\d{5}-\d{4}-\d"),
            _bad("pharmacy_dispensing", "quantities read as numbers", "quantity", lambda f: _bad_numbers(_t("quantity")(f))),
            _ranged("pharmacy_dispensing", "quantity", r"(?P<n>\d+(\.\d+)?)"),
            _listed("pharmacy_dispensing", "days supply are the pharmacy's own", "days_supply", _levels(DAYS_SUPPLY)),
            _listed("pharmacy_dispensing", "DAW codes", "daw_code", _levels(DAW)),
        ),
        person="patient_id",
    ),
    Table(
        "prenatal_visits", ".csv", prenatal_visits,
        lambda header, rows: csv_bytes(header, rows),
        {
            "obstetrics": ("patient_id", "visit_date", "gest_age_plus", "gest_age_wd", "gravida_para"),
            "social_history": ("smoking_status", "pack_years", "alcohol_use"),
        },
        {
            "patient_id": "identifier", "pack_years": "measurement", "gest_age_plus": "keep", "gest_age_wd": "keep",
            "gravida_para": "keep",
        },
        _csv_reader(),
        (
            *_repeats("obstetrics"),
            _dated("obstetrics", "visit_date parses as %Y-%m-%d", "visit_date", "%Y-%m-%d"),
            _pattern("obstetrics", "gestational age written 37+5", "gest_age_plus", r"\d{1,2}\+[0-6]"),
            Check("obstetrics", "gestational ages written 37+5 keep their range in days", "range",
                  lambda f: _gestation_days(_t("gest_age_plus")(f), "+"), "gest_age_plus",
                  spoil_every("gest_age_plus", _doubled_weeks)),
            _pattern("obstetrics", "gestational age written 39w2d", "gest_age_wd", r"\d{1,2}w[0-6]d"),
            Check("obstetrics", "gestational ages written 39w2d keep their range in days", "range",
                  lambda f: _gestation_days(_t("gest_age_wd")(f), "w"), "gest_age_wd",
                  spoil_every("gest_age_wd", _doubled_weeks)),
            _pattern("obstetrics", "gravida and para (G2P1)", "gravida_para", r"G\d+P\d+"),
            _bad("obstetrics", "para below gravida", "gravida_para",
                 lambda f: _para_past_gravida(_t("gravida_para")(f)), spoil_cell("gravida_para", "G1P3")),
            _listed("social_history", "smoking status", "smoking_status", _levels(SMOKING)),
            _bad("social_history", "pack-years read as numbers", "pack_years", lambda f: _bad_numbers(_t("pack_years")(f))),
            _ranged("social_history", "pack_years", r"(?P<n>\d+\.\d)"),
            _listed("social_history", "alcohol use", "alcohol_use", _levels(ALCOHOL)),
        ),
        person="patient_id",
    ),
    Table(
        "well_child", ".csv", well_child,
        lambda header, rows: csv_bytes(header, rows),
        {"pediatrics": ("patient_id", "visit_date", "age_text", "wt_kg", "weight_pct", "head_circ")},
        {
            "patient_id": "identifier", "age_text": "keep", "wt_kg": "measurement", "weight_pct": "measurement",
            "head_circ": "measurement",
        },
        _csv_reader(),
        (
            *_repeats("pediatrics"),
            _dated("pediatrics", "visit_date parses as %Y-%m-%d", "visit_date", "%Y-%m-%d"),
            _pattern("pediatrics", "ages in days, months or years", "age_text", r"\d{1,2} (d|mo|yr)"),
            Check("pediatrics", "ages read as days keep their range", "range",
                  lambda f: _age_days(_t("age_text")(f)), "age_text",
                  spoil_every("age_text", lambda v: re.sub(r"^(\d+)", lambda m: f"{3 * int(m.group(1))}", v))),
            _bad("pediatrics", "weights read as numbers", "wt_kg", lambda f: _bad_numbers(_t("wt_kg")(f))),
            _ranged("pediatrics", "wt_kg", r"(?P<n>-?\d+\.\d\d)"),
            _pattern("pediatrics", "growth percentiles 1 to 99, <1 or >99", "weight_pct", r"<1|>99|\d{1,2}"),
            *_rare("pediatrics", "some percentile is past the chart (<1 or >99)", "weight_pct", r"^(?:<1|>99)$",
                   spoil_every("weight_pct", lambda v: "1" if v == "<1" else "99" if v == ">99" else v),
                   crowd("weight_pct", ">99")),
            _pattern("pediatrics", "head circumference in cm", "head_circ", r"\d{2}\.\d cm"),
            _ranged("pediatrics", "head_circ", r"(?P<n>\d+\.\d) cm", 2.0),
        ),
        person="patient_id",
    ),
    Table(
        "ecg_reads", ".csv", ecg_reads,
        lambda header, rows: csv_bytes(header, rows),
        {"cardiology_ecg": ("patient_id", "ecg_at", "vent_rate", "pr_interval", "qrs_duration", "qtc_interval", "rhythm", "axis")},
        {
            "patient_id": "identifier", "vent_rate": "measurement", "pr_interval": "measurement",
            "qrs_duration": "measurement", "qtc_interval": "measurement", "axis": "measurement",
        },
        _csv_reader(),
        (
            *_repeats("cardiology_ecg"),
            _dated("cardiology_ecg", "ecg_at parses as %Y-%m-%d %H:%M:%S", "ecg_at", "%Y-%m-%d %H:%M:%S"),
            _pattern("cardiology_ecg", "PR intervals in ms", "pr_interval", r"\d{3} ms"),
            _ranged("cardiology_ecg", "pr_interval", r"(?P<n>\d+) ms"),
            _ranged("cardiology_ecg", "qrs_duration", r"(?P<n>\d+)"),
            _ranged("cardiology_ecg", "qtc_interval", r"(?P<n>\d+)", 2.0),
            _listed("cardiology_ecg", "rhythms", "rhythm", _levels(RHYTHMS)),
            _bad("cardiology_ecg", "axes read as numbers", "axis", lambda f: _bad_numbers(_t("axis")(f))),
            _ranged("cardiology_ecg", "axis", r"(?P<n>-?\d+)", 3.0),
        ),
        person="patient_id",
    ),
    Table(
        "culture_results", ".csv", culture_results,
        lambda header, rows: csv_bytes(header, rows),
        {"organism_long_tail": ("isolate_id", "patient_id", "specimen", "organism", "growth")},
        {"isolate_id": "identifier", "patient_id": "identifier", "organism": "code"},
        _csv_reader(),
        (
            *_repeats("organism_long_tail"),
            _listed("organism_long_tail", "specimens", "specimen", _levels(SPECIMENS)),
            _pattern("organism_long_tail", "organisms named Genus species, or no growth or mixed flora", "organism",
                     r"[A-Z][a-z]+ [a-z]+|No growth|Mixed flora"),
            _listed("organism_long_tail", "organisms are named ones", "organism",
                    _levels(ORGANISM_TAIL) | {"No growth", "Mixed flora"}),
            _listed("organism_long_tail", "growth", "growth", _levels(GROWTH)),
        ),
        person="patient_id",
    ),
    Table(
        "reports", ".csv", reports,
        lambda header, rows: csv_bytes(header, rows),
        {
            "report_text_with_headings": ("report_id", "patient_id", "report_type", "report_text"),
            "long_cell": ("addendum",),
        },
        {"report_id": "identifier", "patient_id": "identifier", "report_text": "keep", "addendum": "keep"},
        _csv_reader(),
        (
            *_repeats("report_text_with_headings"),
            _listed("report_text_with_headings", "report types", "report_type", {"Radiology", "Pathology"}),
            *_present("report_text_with_headings", "some report keeps its IMPRESSION heading", "report_text", "\nIMPRESSION: ",
                      spoil_every("report_text", lambda v: v.replace("IMPRESSION: ", ""))),
            *_present("report_text_with_headings", "some report runs over several lines", "report_text", "\n",
                      spoil_every("report_text", lambda v: v.replace("\n", " "))),
            Check("report_text_with_headings", "the share of reports written from the template", "share",
                  lambda f: _share_templated(_t("report_text")(f)), "report_text",
                  spoil_every("report_text", lambda v: v.replace("Normal study.", "Normal."))),
            Check("report_text_with_headings", "report lengths at the 10th, 50th and 90th percentiles", "ratios",
                  lambda f: zoo._length_percentiles(_t("report_text")(f)), "report_text",
                  spoil_every("report_text", lambda v: v[:15])),
            Check("long_cell", "some addendum runs past Excel's 32,767 characters", "present",
                  lambda f: _any_past_excel(_t("addendum")(f)), "addendum",
                  spoil_every("addendum", lambda v: v[:EXCEL_CELL])),
            Check("long_cell", "addenda past Excel's 32,767 characters, as a share", "share",
                  lambda f: _past_excel(_t("addendum")(f)), "addendum", _long_addendum(4)),
        ),
        person="patient_id",
    ),
    Table(
        "registry_naaccr", ".csv", registry_extract_naaccr,
        lambda header, rows: csv_bytes(header, rows),
        {"naaccr_and_trauma_registry": (
            "case_ref", "date_of_diagnosis", "primary_site", "histology", "behavior", "grade", "path_t", "ais_code",
            "injury_date",
        )},
        {
            "case_ref": "identifier", "date_of_diagnosis": "dates", "primary_site": "code", "histology": "code",
            "behavior": "code", "grade": "code", "path_t": "code", "ais_code": "code", "injury_date": "dates",
        },
        _csv_reader(),
        (
            _pattern("naaccr_and_trauma_registry", "NAACCR dates YYYYMMDD, YYYYMM or YYYY", "date_of_diagnosis",
                     r"\d{8}|\d{6}|\d{4}"),
            _bad("naaccr_and_trauma_registry", "each NAACCR date parses at its own precision", "date_of_diagnosis",
                 lambda f: _naaccr_dates_bad(_t("date_of_diagnosis")(f))),
            *_present("naaccr_and_trauma_registry", "some diagnosis is known to the year only", "date_of_diagnosis",
                      r"^\d{4}$", spoil_every("date_of_diagnosis", lambda v: f"{v}0701" if len(v) == 4 else v)),
            *_present("naaccr_and_trauma_registry", "some diagnosis is known to the month only", "date_of_diagnosis",
                      r"^\d{6}$", spoil_every("date_of_diagnosis", lambda v: f"{v}15" if len(v) == 6 else v)),
            _pattern("naaccr_and_trauma_registry", "primary sites without the point", "primary_site", r"C\d{3}"),
            _pattern("naaccr_and_trauma_registry", "histology four figures", "histology", r"\d{4}"),
            _listed("naaccr_and_trauma_registry", "behaviour", "behavior", {"2", "3"}),
            _listed("naaccr_and_trauma_registry", "grades", "grade", _levels(GRADES)),
            _pattern("naaccr_and_trauma_registry", "pathologic T (pT1mi)", "path_t", r"pT(X|is|[1-4](mi|[a-d])?)"),
            _listed("naaccr_and_trauma_registry", "pathologic T categories", "path_t", _levels(PATH_T)),
            _pattern("naaccr_and_trauma_registry", "AIS codes with their severity", "ais_code", r"\d{6}\.[1-6]"),
            Check("naaccr_and_trauma_registry", "AIS severities keep their range", "range",
                  lambda f: _severity(_t("ais_code")(f)), "ais_code",
                  spoil_every("ais_code", lambda v: v[:-1] + "1")),
            _dated("naaccr_and_trauma_registry", "injury_date parses as %Y%m%d", "injury_date", "%Y%m%d"),
        ),
    ),
    Table(
        "appointments", ".csv", appointments,
        lambda header, rows: csv_bytes(header, rows),
        {"scheduling": ("appt_id", "patient_id", "appt_date", "slot_start", "slot_end", "slot_minutes", "appt_status", "no_show")},
        {"appt_id": "identifier", "patient_id": "identifier", "slot_end": "keep", "slot_minutes": "measurement"},
        _csv_reader(),
        (
            *_repeats("scheduling"),
            _dated("scheduling", "appt_date parses as %Y-%m-%d", "appt_date", "%Y-%m-%d"),
            _dated("scheduling", "slot_start parses as %H:%M", "slot_start", "%H:%M"),
            _pattern("scheduling", "slot ends are clocks or 24:00", "slot_end", r"([01]\d|2[0-3]):[0-5]\d|24:00"),
            *_rare("scheduling", "some slot ends at 24:00", "slot_end", r"^24:00$",
                   spoil_every("slot_end", lambda v: "23:59" if v == "24:00" else v), crowd("slot_end", "24:00")),
            _listed("scheduling", "slot lengths", "slot_minutes", {"15", "30", "45", "60"}),
            _listed("scheduling", "appointment status", "appt_status", _levels(APPOINTMENT_STATUS)),
            _listed("scheduling", "no-show Y or N", "no_show", {"Y", "N"}),
        ),
        person="patient_id",
    ),
)


# -- family 3: the clinical domains, part 2, and the coding systems -----------

PLACES_OF_SERVICE = (
    ("11", 50.0), ("21", 12.0), ("22", 15.0), ("23", 10.0), ("02", 5.0), ("19", 3.0), ("03", 2.0), ("04", 2.0),
    ("31", 1.0),
)
BILLED_PROCEDURES = _zipf(("99213", "99214", "93000", "71046", "80053", "85025", "36415", "99285", "97110", "G0439"))
CARC = (
    ("CO-45", 40.0), ("PR-1", 15.0), ("PR-2", 12.0), ("CO-97", 8.0), ("OA-23", 5.0), ("CO-16", 5.0),
    ("PR-3", 10.0), ("CO-4", 5.0),
)
REMARKS = (("", 70.0), ("N130", 10.0), ("MA130", 8.0), ("M15", 7.0), ("N381", 5.0))


def remittance_835(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """An 835 remittance flattened to pipe-delimited lines: CCYYMMDD dates, place of service with its leading
    nought, HC: procedures, charges and payments, CARC adjustments (CO-45), remark codes."""
    draw = random.Random(seed)
    people = _people(n)
    header = [
        "claim_control", "patient_id", "service_date", "place_of_service", "procedure", "charge", "paid",
        "adjustment", "remark",
    ]
    rows: "list[list[str]]" = []
    for index in range(n):
        charge = draw.lognormvariate(5.0, 0.9)
        rows += [[
            f"CLP{20000000 + index}",
            _person(draw, people),
            _when(draw).strftime("%Y%m%d"),
            _pick(draw, PLACES_OF_SERVICE),
            f"HC:{_pick(draw, BILLED_PROCEDURES)}",
            f"{charge:.2f}",
            f"{charge * draw.uniform(0.3, 0.9):.2f}",
            _pick(draw, CARC),
            _pick(draw, REMARKS),
        ]]
    return header, rows


def central_offsets(moment: datetime.datetime) -> "tuple[str, ...]":
    """Every offset a local US Central wall-clock moment may wear: the Eastern rule an hour west."""
    west = {"-04:00": "-05:00", "-05:00": "-06:00"}
    return tuple(west[offset] for offset in zoo.eastern_offsets(moment))


def _stamp_on_a_change_day(draw: random.Random) -> datetime.datetime:
    """A local moment, a quarter of them on a day the clocks change, never in the hour they skip."""
    if draw.random() < 0.25:
        day = draw.choice(zoo.CHANGE_DAYS)
    else:
        day = zoo._day(draw, datetime.date(2023, 1, 1), datetime.date(2024, 12, 31))
    moment = datetime.datetime.combine(day, datetime.time(draw.randint(0, 23), draw.randint(0, 59), draw.randint(0, 59)))
    if not zoo.eastern_offsets(moment):
        moment = moment.replace(hour=3)
    return moment


def _wrong_offsets_by(series: object, offsets: "object", form: str, cut: int, skip: int = 0) -> int:
    """Stamps whose written offset is not one in force on their local date and time (`offsets` of the moment)."""
    wrong = 0
    for text in series.dropna().astype(str):  # type: ignore[attr-defined]
        try:
            local = datetime.datetime.strptime(text[:cut], form)
        except ValueError:
            continue
        wrong += 0 if text[cut + skip:] in offsets(local) else 1  # type: ignore[operator]
    return wrong


UNITS_OF_CARE = (("4W", 20.0), ("5E", 20.0), ("6N", 15.0), ("ED", 20.0), ("OBS", 10.0), ("7S", 10.0), ("3C", 5.0))
ADT_EVENTS = (("A01", 25.0), ("A02", 45.0), ("A03", 25.0), ("A08", 5.0))


def adt_events(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """ADT bed movements: admit, transfer and discharge events, units and beds, in and out stamps with US Central
    offsets across the days the clocks change."""
    draw = random.Random(seed)
    people = _people(n)
    header = ["event_id", "patient_id", "event_type", "unit", "bed", "in_ts", "out_ts"]
    rows: "list[list[str]]" = []
    for index in range(n):
        unit = _pick(draw, UNITS_OF_CARE)
        arrived = _stamp_on_a_change_day(draw)
        left = arrived + datetime.timedelta(hours=draw.randint(1, 72), minutes=draw.randint(0, 59))
        if not zoo.eastern_offsets(left):
            left = left.replace(hour=3)
        rows += [[
            f"ADT{50000000 + index}",
            _person(draw, people),
            _pick(draw, ADT_EVENTS),
            unit,
            f"{unit}-{draw.randint(1, 40):02d}{draw.choice('AB')}",
            arrived.strftime("%Y-%m-%d %H:%M:%S") + central_offsets(arrived)[0],
            left.strftime("%Y-%m-%d %H:%M:%S") + central_offsets(left)[0],
        ]]
    return header, rows


PHQ_ITEM = (("0", 45.0), ("1", 30.0), ("2", 15.0), ("3", 10.0))
PHQ_COLUMNS = tuple(f"phq9_{item}" for item in range(1, 10))


def pro_scales(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Patient-reported outcomes: PROMIS T-scores beside -99 and 999, the nine PHQ-9 items and their total,
    a numeric multi-select ('1,3,5'), two picks of twelve sorted and in click order, and the click-order residual."""
    draw = random.Random(seed)
    people = _people(n)
    header = [
        "patient_id", "survey_date", "promis_t", *PHQ_COLUMNS, "phq9_total", "symptoms_multi", "pick_two_sorted",
        "pick_two_click", "pick_two_residual",
    ]
    rows: "list[list[str]]" = []
    for _index in range(n):
        level = draw.random()
        score = "-99" if level < 0.05 else "999" if level < 0.07 else f"{min(80.0, max(20.0, draw.gauss(50.0, 10.0))):.1f}"
        items = [_pick(draw, PHQ_ITEM) for _item in PHQ_COLUMNS]
        multi = sorted(draw.sample(range(1, 9), draw.randint(1, 4)))
        pair = draw.sample(range(1, 13), 1 if draw.random() < 0.15 else 2)
        click = draw.sample(range(1, 13), 1 if draw.random() < 0.15 else 2)
        rows += [[
            _person(draw, people),
            _when(draw).date().isoformat(),
            score,
            *items,
            f"{sum(int(item) for item in items)}",
            ",".join(f"{pick}" for pick in multi),
            ",".join(f"{pick}" for pick in sorted(pair)),
            ",".join(f"{pick}" for pick in click),
            f"{draw.randint(1, 6)},{draw.randint(7, 12)}",
        ]]
    return header, rows


def _picks(series: object) -> "list[list[int]]":
    found: "list[list[int]]" = []
    for text in series.dropna().astype(str):  # type: ignore[attr-defined]
        try:
            found += [[int(part) for part in text.split(",")]]
        except ValueError:
            found += [[-1]]
    return found


def _picks_bad(series: object, low: int, high: int, most: int, ordered: bool) -> int:
    """Cells with a pick outside low to high, more than `most` picks, a pick twice, or (ordered) out of order."""
    bad = 0
    for picks in _picks(series):
        wrong = any(pick < low or pick > high for pick in picks) or len(picks) > most or len(set(picks)) < len(picks)
        bad += 1 if wrong or (ordered and picks != sorted(picks)) else 0
    return bad


def _some_in_click_order(series: object) -> bool:
    return any(len(picks) == 2 and picks[0] > picks[1] for picks in _picks(series))


def _residual_bad(series: object) -> int:
    return sum(1 for picks in _picks(series) if not (len(picks) == 2 and 1 <= picks[0] <= 6 and 7 <= picks[1] <= 12))


def _sorted_picks(value: str) -> str:
    try:
        return ",".join(f"{pick}" for pick in sorted(int(part) for part in value.split(",")))
    except ValueError:
        return value


def _totals_bad(frame: object) -> int:
    import pandas

    items = frame[list(PHQ_COLUMNS)].apply(pandas.to_numeric, errors="coerce")  # type: ignore[index]
    total = pandas.to_numeric(frame["phq9_total"], errors="coerce")  # type: ignore[index]
    return int((items.sum(axis=1) != total).sum())


CHROMOSOMES = tuple((f"chr{place}", 25.0 - place) for place in range(1, 23)) + (("chrX", 4.0), ("chrY", 1.0))
GENOTYPES = (("0/1", 55.0), ("1/1", 25.0), ("0/0", 10.0), ("./.", 7.0), ("1/2", 3.0))
RS_FIGURES = ((4, 5.0), (5, 10.0), (6, 15.0), (7, 25.0), (8, 25.0), (9, 20.0))


def vcf_calls(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Variant calls flattened from a VCF: CHROM, POS, REF, ALT (and <DEL>), rsIDs of four to nine figures or '.',
    genotypes with './.', QUAL; several variants a sample."""
    draw = random.Random(seed)
    people = _people(n)
    header = ["sample_id", "chrom", "pos", "ref", "alt", "rsid", "gt", "qual"]
    bases = "ACGT"
    rows: "list[list[str]]" = []
    for _index in range(n):
        ref = draw.choice(bases) if draw.random() < 0.9 else "".join(draw.choice(bases) for _base in range(draw.randint(2, 3)))
        level = draw.random()
        if level < 0.05:
            alt = "<DEL>"
        elif level < 0.15:
            alt = "".join(draw.choice(bases) for _base in range(2))
        else:
            alt = draw.choice([base for base in bases if base != ref[0]])
        figures = draw.choices([width for width, _weight in RS_FIGURES], [weight for _width, weight in RS_FIGURES])[0]
        rows += [[
            f"SMP{4000000 + draw.randrange(people)}",
            _pick(draw, CHROMOSOMES),
            f"{draw.randint(10_000, 248_000_000)}",
            ref,
            alt,
            "." if draw.random() < 0.1 else f"rs{draw.randint(10 ** (figures - 1), 10 ** figures - 1)}",
            _pick(draw, GENOTYPES),
            f"{draw.uniform(20.0, 5000.0):.1f}",
        ]]
    return header, rows


def wearable_stream(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A wearable's export: local stamps with the offset after a space ('-0400', as Apple Health writes them)
    across daylight saving, and UTC stamps to the millisecond."""
    draw = random.Random(seed)
    people = _people(n)
    header = ["device_id", "recorded_local", "sample_ts", "heart_rate", "step_count"]
    rows: "list[list[str]]" = []
    for _index in range(n):
        local = _stamp_on_a_change_day(draw)
        offset = zoo.eastern_offset(local)
        utc = local - datetime.timedelta(hours=int(offset[:3]))
        rows += [[
            f"WD-{draw.randrange(people):05d}",
            local.strftime("%Y-%m-%d %H:%M:%S") + " " + offset.replace(":", ""),
            utc.strftime("%Y-%m-%dT%H:%M:%S") + f".{draw.randint(0, 999):03d}Z",
            f"{draw.randint(48, 170)}",
            f"{draw.randint(0, 40) if draw.random() > 0.4 else 0}",
        ]]
    return header, rows


def _compact_eastern(moment: datetime.datetime) -> "tuple[str, ...]":
    return tuple(offset.replace(":", "") for offset in zoo.eastern_offsets(moment))


# The coding systems' forms section 6 (b) names: ICD-10-CM's seventh
# character with its X placeholders, SNOMED CT ids with their Verhoeff
# check figure, a code and its name in one cell, procedure codes with
# chains of modifiers, APR-DRG with its severity of illness, and ICD-10-CM
# as a real export holds it, 600 codes on a Zipf tail.
SEVENTH = _zipf((
    "S72.001A", "S72.001D", "T81.4XXA", "S06.0X1A", "M80.08XA", "W19.XXXA", "S82.201A", "T84.84XA",
    "S52.501A", "S42.001S",
))
_VERHOEFF_D = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9), (1, 2, 3, 4, 0, 6, 7, 8, 9, 5), (2, 3, 4, 0, 1, 7, 8, 9, 5, 6),
    (3, 4, 0, 1, 2, 8, 9, 5, 6, 7), (4, 0, 1, 2, 3, 9, 5, 6, 7, 8), (5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
    (6, 5, 9, 8, 7, 1, 0, 4, 3, 2), (7, 6, 5, 9, 8, 2, 1, 0, 4, 3), (8, 7, 6, 5, 9, 3, 2, 1, 0, 4),
    (9, 8, 7, 6, 5, 4, 3, 2, 1, 0),
)
_VERHOEFF_P = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9), (1, 5, 7, 6, 2, 8, 3, 0, 9, 4), (5, 8, 0, 3, 7, 9, 6, 1, 4, 2),
    (8, 9, 1, 6, 0, 4, 3, 5, 2, 7), (9, 4, 5, 3, 1, 2, 6, 8, 7, 0), (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
    (2, 7, 9, 3, 8, 0, 6, 4, 1, 5), (7, 0, 4, 6, 9, 1, 3, 2, 5, 8),
)
_VERHOEFF_INV = (0, 4, 3, 2, 1, 5, 6, 7, 8, 9)


def verhoeff_check(figures: str) -> int:
    """The Verhoeff check figure to append to `figures`."""
    check = 0
    for place, figure in enumerate(reversed(figures)):
        check = _VERHOEFF_D[check][_VERHOEFF_P[(place + 1) % 8][int(figure)]]
    return _VERHOEFF_INV[check]


def verhoeff_valid(figures: str) -> bool:
    check = 0
    for place, figure in enumerate(reversed(figures)):
        check = _VERHOEFF_D[check][_VERHOEFF_P[place % 8][int(figure)]]
    return check == 0


def _snomed_ids() -> "tuple[str, ...]":
    draw = random.Random(31)
    found: "list[str]" = []
    while len(found) < 14:
        body = f"{draw.randint(10 ** 5, 10 ** 8 - 1)}10"
        code = body + f"{verhoeff_check(body)}"
        found += [code] if code not in found else []
    return tuple(found)


SNOMED_CHECKED = _zipf(_snomed_ids())
NAMED = (
    ("E11.9", "Type 2 diabetes mellitus without complications"), ("I10", "Essential (primary) hypertension"),
    ("E78.5", "Hyperlipidemia, unspecified"), ("J44.9", "Chronic obstructive pulmonary disease, unspecified"),
    ("N18.3", "Chronic kidney disease, stage 3"), ("F32.9", "Major depressive disorder, single episode, unspecified"),
    ("I48.91", "Unspecified atrial fibrillation"), ("K21.9", "Gastro-esophageal reflux disease without esophagitis"),
    ("M54.5", "Low back pain"), ("G47.33", "Obstructive sleep apnea"),
)
NAME_OF = dict(NAMED)
CODE_WITH_NAME = _zipf(tuple(f"{code} - {name}" for code, name in NAMED))
PROC_CHAINS = _zipf(("99214-25-59", "20610-RT-59", "97140-GP-59", "99213", "99213-25", "73030-LT-26", "93010-26", "96372-59-XU"))
PROC_MODIFIERS = {"25", "59", "RT", "LT", "GP", "26", "XU"}
APR_DRGS = _zipf(("194", "140", "720", "139", "201", "045", "053", "300"))
SOI = (("1", 30.0), ("2", 40.0), ("3", 22.0), ("4", 8.0))


def _icd10_tail() -> "tuple[str, ...]":
    draw = random.Random(5)
    codes: "list[str]" = []
    while len(codes) < 600:
        code = f"{draw.choice('ABCDEFGHIJKLMNOPQRSTVWXYZ')}{draw.randint(0, 99):02d}.{draw.randint(0, 99):d}"
        codes += [code] if code not in codes else []
    return tuple(codes)


ICD10_TAIL = _zipf(_icd10_tail())


def coded_forms(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Coded rows of an encounter: the coding systems' longer forms, and a realistic ICD-10-CM long tail."""
    draw = random.Random(seed)
    header = ["enc_id", "icd10_seventh", "snomed_checked", "dx_with_name", "proc_chain", "apr_drg", "icd10_tail"]
    rows: "list[list[str]]" = []
    for _index in range(n):
        rows += [[
            f"E{200000000 + draw.randrange(max(n // 2, 1))}",
            _pick(draw, SEVENTH),
            _pick(draw, SNOMED_CHECKED),
            _pick(draw, CODE_WITH_NAME),
            _pick(draw, PROC_CHAINS),
            f"{_pick(draw, APR_DRGS)}-{_pick(draw, SOI)}",
            _pick(draw, ICD10_TAIL),
        ]]
    return header, rows


def _verhoeff_bad(series: object) -> int:
    return sum(
        0 if re.fullmatch(r"\d{6,18}", text) and verhoeff_valid(text) else 1
        for text in series.dropna().astype(str)  # type: ignore[attr-defined]
    )


def _names_off(series: object) -> int:
    bad = 0
    for text in series.dropna().astype(str):  # type: ignore[attr-defined]
        code, _dash, name = text.partition(" - ")
        bad += 0 if NAME_OF.get(code) == name else 1
    return bad


def _modifiers_off(series: object) -> int:
    modifiers = [part for text in series.dropna().astype(str) for part in text.split("-")[1:]]  # type: ignore[attr-defined]
    return sum(1 for modifier in modifiers if modifier not in PROC_MODIFIERS)


def _soi(series: object) -> "tuple[float, float, float] | None":
    return _spread([float(text[-1]) for text in series.dropna().astype(str) if re.fullmatch(r"\d{3}-[1-4]", text)])  # type: ignore[attr-defined]


def _last_figure_moved(value: str) -> str:
    return value[:-1] + f"{(int(value[-1]) + 1) % 10}" if value[-1:].isdigit() else value


FAMILY_CLINICAL_B: "tuple[Table, ...]" = (
    Table(
        "remit_835", ".txt", remittance_835,
        lambda header, rows: csv_bytes(header, rows, delimiter="|"),
        {
            "pipe_delimited": (),
            "remittance_835": (
                "claim_control", "patient_id", "service_date", "place_of_service", "procedure", "charge", "paid",
                "adjustment", "remark",
            ),
        },
        {
            "claim_control": "identifier", "patient_id": "identifier", "place_of_service": "code", "procedure": "code",
            "adjustment": "code", "remark": "code", "charge": "measurement", "paid": "measurement", "service_date": "dates",
        },
        _csv_reader(sep="|"),
        (
            Check("pipe_delimited", "the file splits into nine columns", "same",
                  lambda f: int(f["inferred"].shape[1]), "", spoil_extra_column),  # type: ignore[attr-defined]
            *_repeats("remittance_835"),
            _dated("remittance_835", "service dates CCYYMMDD", "service_date", "%Y%m%d"),
            _listed("remittance_835", "places of service keep two figures", "place_of_service", _levels(PLACES_OF_SERVICE)),
            *_rare("remittance_835", "some place of service keeps its leading nought", "place_of_service", r"^0\d$",
                   spoil_every("place_of_service", lambda v: f"{int(v)}"), crowd("place_of_service", "02")),
            _pattern("remittance_835", "procedures written HC:code", "procedure", r"HC:[0-9A-Z]{5}"),
            _bad("remittance_835", "charges read as numbers", "charge", lambda f: _bad_numbers(_t("charge")(f))),
            _ranged("remittance_835", "charge", r"(?P<n>\d+\.\d\d)"),
            _ranged("remittance_835", "paid", r"(?P<n>\d+\.\d\d)"),
            _pattern("remittance_835", "adjustments as group and reason (CO-45)", "adjustment", r"(CO|PR|OA|PI|CR)-\d{1,3}"),
            _listed("remittance_835", "adjustment reasons are the payer's", "adjustment", _levels(CARC)),
            _listed("remittance_835", "remark codes", "remark", _levels(REMARKS) - {""}),
        ),
        separator="vertical-bar",
        person="patient_id",
    ),
    Table(
        "adt_events", ".csv", adt_events,
        lambda header, rows: csv_bytes(header, rows),
        {"adt_bed_movements": ("event_id", "patient_id", "event_type", "unit", "bed", "in_ts", "out_ts")},
        {"event_id": "identifier", "patient_id": "identifier", "event_type": "code", "unit": "code", "bed": "keep"},
        _csv_reader(),
        (
            *_repeats("adt_bed_movements"),
            _listed("adt_bed_movements", "ADT event types", "event_type", _levels(ADT_EVENTS)),
            _listed("adt_bed_movements", "units", "unit", _levels(UNITS_OF_CARE)),
            _pattern("adt_bed_movements", "beds named unit-number-letter", "bed", r"[0-9A-Z]{2,4}-\d{2}[AB]"),
            _dated("adt_bed_movements", "in_ts parses with its offset", "in_ts", "%Y-%m-%d %H:%M:%S%z", utc=True),
            _dated("adt_bed_movements", "out_ts parses with its offset", "out_ts", "%Y-%m-%d %H:%M:%S%z", utc=True),
            _bad("adt_bed_movements", "in_ts wears a Central offset in force on its date", "in_ts",
                 lambda f: _wrong_offsets_by(_t("in_ts")(f), central_offsets, "%Y-%m-%d %H:%M:%S", 19),
                 spoil_cell("in_ts", "2024-07-01 10:00:00-06:00")),
            _bad("adt_bed_movements", "out_ts wears a Central offset in force on its date", "out_ts",
                 lambda f: _wrong_offsets_by(_t("out_ts")(f), central_offsets, "%Y-%m-%d %H:%M:%S", 19),
                 spoil_cell("out_ts", "2024-01-15 10:00:00-05:00")),
        ),
        person="patient_id",
    ),
    Table(
        "pro_scales", ".csv", pro_scales,
        lambda header, rows: csv_bytes(header, rows),
        {
            "promis_phq9": ("patient_id", "survey_date", "promis_t", *PHQ_COLUMNS, "phq9_total"),
            "pro_multi_select": ("symptoms_multi", "pick_two_sorted", "pick_two_click", "pick_two_residual"),
        },
        {
            "patient_id": "identifier", "promis_t": "measurement", "phq9_total": "measurement",
            **{column: "measurement" for column in PHQ_COLUMNS},
            "symptoms_multi": "keep", "pick_two_sorted": "keep", "pick_two_click": "keep", "pick_two_residual": "keep",
        },
        _csv_reader(),
        (
            *_repeats("promis_phq9"),
            _dated("promis_phq9", "survey_date parses as %Y-%m-%d", "survey_date", "%Y-%m-%d"),
            _pattern("promis_phq9", "T-scores to one place, or -99 or 999", "promis_t", r"\d{2}\.\d|-99|999"),
            _ranged("promis_phq9", "promis_t", r"(?P<n>\d{2}\.\d)", 0.5),
            *_rare("promis_phq9", "some T-score is the missing code -99", "promis_t", r"^-99$",
                   spoil_every("promis_t", lambda v: "50.0" if v == "-99" else v), crowd("promis_t", "-99")),
            _bad("promis_phq9", "PHQ-9 items 0 to 3", "phq9_1",
                 lambda f: sum(_bad_set(_t(column)(f), {"0", "1", "2", "3"}) for column in PHQ_COLUMNS)),
            _listed("promis_phq9", "PHQ-9 totals 0 to 27", "phq9_total", {f"{k}" for k in range(28)}),
            _bad("promis_phq9", "the total is the sum of its nine items (between columns)", "phq9_total",
                 lambda f: _totals_bad(f["text"]), spoil_cell("phq9_total", "27")),
            _bad("pro_multi_select", "multi-select picks 1 to 8, each once, in order", "symptoms_multi",
                 lambda f: _picks_bad(_t("symptoms_multi")(f), 1, 8, 8, True), spoil_cell("symptoms_multi", "5,3")),
            *_present("pro_multi_select", "some multi-select holds several picks", "symptoms_multi", ",",
                      spoil_every("symptoms_multi", lambda v: v.split(",")[0])),
            _bad("pro_multi_select", "two picks of twelve, sorted", "pick_two_sorted",
                 lambda f: _picks_bad(_t("pick_two_sorted")(f), 1, 12, 2, True), spoil_cell("pick_two_sorted", "12,3")),
            *_present("pro_multi_select", "some sorted cell holds two picks", "pick_two_sorted", ",",
                      spoil_every("pick_two_sorted", lambda v: v.split(",")[0])),
            _bad("pro_multi_select", "two picks of twelve in click order", "pick_two_click",
                 lambda f: _picks_bad(_t("pick_two_click")(f), 1, 12, 2, False), spoil_cell("pick_two_click", "13,3")),
            Check("pro_multi_select", "some pair is written in click order, the larger first", "present",
                  lambda f: _some_in_click_order(_t("pick_two_click")(f)), "pick_two_click",
                  spoil_every("pick_two_click", _sorted_picks)),
            _bad("pro_multi_select", "the residual: a first pick of 1 to 6, then one of 7 to 12", "pick_two_residual",
                 lambda f: _residual_bad(_t("pick_two_residual")(f)), spoil_cell("pick_two_residual", "9,2")),
        ),
        person="patient_id",
    ),
    Table(
        "vcf_calls", ".csv", vcf_calls,
        lambda header, rows: csv_bytes(header, rows),
        {"vcf_flattened": ("sample_id", "chrom", "pos", "ref", "alt", "rsid", "gt", "qual")},
        {
            "sample_id": "identifier", "chrom": "code", "pos": "measurement", "ref": "code", "alt": "code",
            "rsid": "identifier", "gt": "code", "qual": "measurement",
        },
        _csv_reader(),
        (
            *_repeats("vcf_flattened", "sample_id"),
            _listed("vcf_flattened", "chromosomes", "chrom", _levels(CHROMOSOMES)),
            _bad("vcf_flattened", "positions read as numbers", "pos", lambda f: _bad_numbers(_t("pos")(f))),
            _ranged("vcf_flattened", "pos", r"(?P<n>\d+)", 0.1),
            _pattern("vcf_flattened", "REF alleles are bases", "ref", r"[ACGT]+"),
            _pattern("vcf_flattened", "ALT alleles are bases or <DEL>", "alt", r"[ACGT]+|<DEL>"),
            _pattern("vcf_flattened", "rsIDs of four to nine figures, or '.'", "rsid", r"rs\d{4,9}|\."),
            *_present("vcf_flattened", "some rsID is short (four to six figures)", "rsid", r"^rs\d{4,6}$",
                      spoil_every("rsid", lambda v: f"rs{int(v[2:]):07d}" if v.startswith("rs") else v)),
            _listed("vcf_flattened", "genotypes with ./.", "gt", _levels(GENOTYPES)),
            _ranged("vcf_flattened", "qual", r"(?P<n>\d+\.\d)"),
        ),
        person="sample_id",
    ),
    Table(
        "wearable_stream", ".csv", wearable_stream,
        lambda header, rows: csv_bytes(header, rows),
        {"wearable_offsets_subsecond": ("device_id", "recorded_local", "sample_ts", "heart_rate", "step_count")},
        {"device_id": "identifier", "heart_rate": "measurement", "step_count": "measurement"},
        _csv_reader(),
        (
            *_repeats("wearable_offsets_subsecond", "device_id"),
            _dated("wearable_offsets_subsecond", "local stamps parse with the offset after a space", "recorded_local",
                   "%Y-%m-%d %H:%M:%S %z", utc=True),
            _bad("wearable_offsets_subsecond", "the local offset is in force on its date", "recorded_local",
                 lambda f: _wrong_offsets_by(_t("recorded_local")(f), _compact_eastern, "%Y-%m-%d %H:%M:%S", 19, 1),
                 spoil_cell("recorded_local", "2024-07-01 10:00:00 -0500")),
            _dated("wearable_offsets_subsecond", "UTC stamps to the millisecond", "sample_ts", "%Y-%m-%dT%H:%M:%S.%fZ"),
            *_present("wearable_offsets_subsecond", "some stamp carries its milliseconds", "sample_ts", r"\.(?!000Z)\d{3}Z$",
                      spoil_every("sample_ts", lambda v: v[:20] + "000Z")),
            _ranged("wearable_offsets_subsecond", "heart_rate", r"(?P<n>\d+)", 2.0),
        ),
        person="device_id",
    ),
    Table(
        "coded_forms", ".csv", coded_forms,
        lambda header, rows: csv_bytes(header, rows),
        {
            "diagnosis_code_forms": ("enc_id", "icd10_seventh", "snomed_checked", "dx_with_name"),
            "procedure_and_drg_forms": ("proc_chain", "apr_drg"),
            "icd10_long_tail": ("icd10_tail",),
        },
        {
            "enc_id": "identifier", "icd10_seventh": "code", "snomed_checked": "code", "dx_with_name": "code",
            "proc_chain": "code", "apr_drg": "code", "icd10_tail": "code",
        },
        _csv_reader(),
        (
            _pattern("diagnosis_code_forms", "ICD-10-CM with its seventh character", "icd10_seventh", r"[A-Z]\d[0-9A-Z]\.[0-9X]{3}[ADS]"),
            *_present("diagnosis_code_forms", "some code keeps its X placeholder", "icd10_seventh", "X",
                      spoil_every("icd10_seventh", lambda v: v.replace("X", "0"))),
            _pattern("diagnosis_code_forms", "SNOMED CT ids", "snomed_checked", r"\d{6,18}"),
            _bad("diagnosis_code_forms", "SNOMED CT ids pass their Verhoeff check", "snomed_checked",
                 lambda f: _verhoeff_bad(_t("snomed_checked")(f)), spoil_every("snomed_checked", _last_figure_moved)),
            _pattern("diagnosis_code_forms", "a code and its name in one cell", "dx_with_name", zoo.ICD10_PATTERN + r" - .+"),
            _bad("diagnosis_code_forms", "each name is its code's own", "dx_with_name",
                 lambda f: _names_off(_t("dx_with_name")(f)), spoil_cell("dx_with_name", "E11.9 - Low back pain")),
            _pattern("procedure_and_drg_forms", "procedure codes with their modifier chains", "proc_chain",
                     r"\d{4}[0-9A-Z](-[0-9A-Z]{2})*"),
            _bad("procedure_and_drg_forms", "modifiers are listed ones", "proc_chain",
                 lambda f: _modifiers_off(_t("proc_chain")(f)), spoil_cell("proc_chain", "99214-25-Q9")),
            _pattern("procedure_and_drg_forms", "APR-DRG with its severity (194-3)", "apr_drg", r"\d{3}-[1-4]"),
            Check("procedure_and_drg_forms", "severities of illness keep their range", "range",
                  lambda f: _soi(_t("apr_drg")(f)), "apr_drg", spoil_every("apr_drg", lambda v: v[:-1] + "1")),
            _pattern("icd10_long_tail", "a long tail of ICD-10-CM codes", "icd10_tail", zoo.ICD10_PATTERN),
        ),
    ),
)


# -- family 4: the long and system-shaped exports -------------------------------

# OMOP's measurement table, long: each concept with its LOINC source
# value, its unit concept and its range; one concept valued by a concept.
OMOP_CONCEPTS = (
    ("3004410", "4548-4", "8554", 4.5, 12.0), ("3013682", "2160-0", "8840", 0.5, 3.0),
    ("3016723", "2345-7", "8840", 60.0, 300.0), ("3027018", "718-7", "8713", 8.0, 17.0),
    ("3020630", "2093-3", "8840", 120.0, 300.0), ("3003694", "882-1", "0", 0.0, 0.0),
)
OMOP_ANSWERS = (("45884084", 40.0), ("45878583", 55.0), ("45880296", 5.0))


def omop_measurement(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """An OMOP CDM measurement slice: concept ids read as numbers, value_as_number or value_as_concept_id, units."""
    draw = random.Random(seed)
    people = _people(n)
    header = [
        "measurement_id", "person_id", "measurement_concept_id", "measurement_date", "value_as_number",
        "value_as_concept_id", "unit_concept_id", "measurement_source_value",
    ]
    rows: "list[list[str]]" = []
    for index in range(n):
        concept, loinc, unit, low, high = draw.choice(OMOP_CONCEPTS)
        valued = unit != "0"
        rows += [[
            f"{90000000 + index}",
            f"{1 + draw.randrange(people)}",
            concept,
            _when(draw).date().isoformat(),
            f"{draw.uniform(low, high):.2f}" if valued else "",
            "" if valued else _pick(draw, OMOP_ANSWERS),
            unit,
            loinc,
        ]]
    return header, rows


def _units_off_their_concept(frame: object) -> int:
    """Rows whose unit concept is not their measurement concept's own (read by concept: between columns)."""
    own = {concept: unit for concept, _loinc, unit, _low, _high in OMOP_CONCEPTS}
    bad = 0
    for concept, unit in zip(frame["measurement_concept_id"], frame["unit_concept_id"]):  # type: ignore[index]
        bad += 0 if own.get(f"{concept}") == f"{unit}" else 1
    return bad


def _omop_valued(header: "list[str]", row: "list[str]") -> bool:
    return row[header.index("unit_concept_id")] != "0"


PCORNET_TYPES = (("10", 70.0), ("09", 15.0), ("SM", 10.0), ("NI", 5.0))
PCORNET_SOURCES = (("AD", 25.0), ("DI", 30.0), ("FI", 30.0), ("IN", 5.0), ("NI", 4.0), ("UN", 3.0), ("OT", 3.0))
PCORNET_PDX = (("P", 30.0), ("S", 60.0), ("X", 5.0), ("NI", 5.0))
RAW_TYPE_OF = {"10": "ICD10CM", "09": "ICD9CM", "SM": "SNOMED", "NI": ""}
DX_FORM_OF = {
    "10": zoo.ICD10_PATTERN, "09": r"V\d{2}(\.\d{1,2})?|E\d{3}(\.\d)?|\d{3}(\.\d{1,2})?", "SM": r"[1-9]\d{5,17}",
}


def pcornet_diagnosis(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A PCORnet CDM DIAGNOSIS slice: DX in the system its DX_TYPE names, DX_SOURCE and PDX with NI, the raw_ columns."""
    draw = random.Random(seed)
    people = _people(n)
    header = [
        "DIAGNOSISID", "PATID", "ENCOUNTERID", "ADMIT_DATE", "DX", "DX_TYPE", "DX_SOURCE", "PDX", "RAW_DX", "RAW_DX_TYPE",
    ]
    pools = {"10": zoo.ICD10, "09": zoo.ICD9, "SM": zoo.SNOMED}
    rows: "list[list[str]]" = []
    for index in range(n):
        kind = _pick(draw, PCORNET_TYPES)
        code = _pick(draw, pools[kind]) if kind in pools else ""
        patient = draw.randrange(people)
        rows += [[
            f"DX{80000000 + index}",
            f"P{100000 + patient}",
            f"ENC{60000000 + 10 * patient + draw.randint(0, 2)}",
            _when(draw).date().isoformat(),
            code,
            kind,
            _pick(draw, PCORNET_SOURCES),
            _pick(draw, PCORNET_PDX),
            code.replace(".", ""),
            RAW_TYPE_OF[kind],
        ]]
    return header, rows


def _dx_off_its_type(frame: object) -> int:
    """Codes not in the form their DX_TYPE names (read by type: between columns)."""
    bad = 0
    for code, kind in zip(frame["DX"], frame["DX_TYPE"]):  # type: ignore[index]
        form = DX_FORM_OF.get(f"{kind}")
        if form is not None:
            bad += 0 if isinstance(code, str) and re.fullmatch(form, code) else 1
    return bad


def _is_icd10_type(header: "list[str]", row: "list[str]") -> bool:
    return row[header.index("DX_TYPE")] == "10"


I2B2_LOINC = (("2345-7", "mg/dL", 60.0, 300.0), ("718-7", "g/dL", 8.0, 17.0), ("2160-0", "mg/dL", 0.5, 3.0))


def i2b2_facts(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """An i2b2 observation_fact slice (entity, attribute, value): ICD10CM:, LOINC: and DEM|GENDER: concepts, '@' members."""
    draw = random.Random(seed)
    people = _people(n)
    header = [
        "encounter_num", "patient_num", "concept_cd", "provider_id", "start_date", "modifier_cd", "instance_num",
        "valtype_cd", "tval_char", "nval_num", "units_cd",
    ]
    rows: "list[list[str]]" = []
    for _index in range(n):
        level = draw.random()
        valtype = tval = value = units = ""
        if level < 0.4:
            concept = f"ICD10CM:{_pick(draw, zoo.ICD10)}"
        elif level < 0.75:
            loinc, units, low, high = draw.choice(I2B2_LOINC)
            concept, valtype, tval, value = f"LOINC:{loinc}", "N", "E", f"{draw.uniform(low, high):.2f}"
        elif level < 0.9:
            concept = f"DEM|GENDER:{draw.choice('FM')}"
        else:
            concept = f"DEM|VITAL:{draw.choice('NY')}"
        moment = _when(draw)
        patient = draw.randrange(people)
        rows += [[
            f"{10 * patient + draw.randint(1, 3)}",
            f"{1 + patient}",
            concept,
            "@",
            moment.strftime("%Y-%m-%d %H:%M:%S") + ".000",
            "@",
            "1",
            valtype,
            tval,
            value,
            units,
        ]]
    return header, rows


def _prefixes_off(series: object) -> int:
    prefixes = {"ICD10CM", "LOINC", "DEM|GENDER", "DEM|VITAL"}
    return sum(1 for text in series.dropna().astype(str) if text.partition(":")[0] not in prefixes)  # type: ignore[attr-defined]


CDC_CATEGORY = (
    ("2106-3", 60.0), ("2054-5", 18.0), ("2028-9", 8.0), ("1002-5", 3.0), ("2076-8", 1.0), ("2131-1", 10.0),
)
CDC_ROOT = "urn:oid:2.16.840.1.113883.6.238|"
FHIR_CODES = (("2345-7", "mg/dL", 60.0, 300.0), ("718-7", "g/dL", 8.0, 17.0), ("4548-4", "%", 4.5, 12.0), ("2951-2", "mmol/L", 130.0, 150.0))
FHIR_STATUS = (("final", 85.0), ("amended", 10.0), ("preliminary", 5.0))


def fhir_observations(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """FHIR Observations flattened to CSV: references 'Patient/123', codings 'http://loinc.org|2345-7', quantities,
    instants with offsets, and the CDC's category code under its OMB coding."""
    draw = random.Random(seed)
    people = _people(n)
    header = [
        "id", "subject_reference", "code_coding", "value_quantity_value", "value_quantity_unit",
        "effective_date_time", "status", "omb_category",
    ]
    rows: "list[list[str]]" = []
    for index in range(n):
        loinc, unit, low, high = draw.choice(FHIR_CODES)
        moment = _stamp_on_a_change_day(draw)
        rows += [[
            f"obs-{70000000 + index}",
            f"Patient/{10000 + draw.randrange(people)}",
            f"http://loinc.org|{loinc}",
            f"{draw.uniform(low, high):.1f}",
            unit,
            moment.strftime("%Y-%m-%dT%H:%M:%S") + zoo.eastern_offset(moment),
            _pick(draw, FHIR_STATUS),
            CDC_ROOT + _pick(draw, CDC_CATEGORY),
        ]]
    return header, rows


HL7_TESTS = (
    ("2345-7", "Glucose", "mg/dL", 60.0, 300.0), ("2160-0", "Creatinine", "mg/dL", 0.5, 3.0),
    ("718-7", "Hemoglobin", "g/dL", 8.0, 17.0), ("4548-4", "Hemoglobin A1c", "%", 4.5, 12.0),
    ("2951-2", "Sodium", "mmol/L", 130.0, 150.0), ("2823-3", "Potassium", "mmol/L", 3.0, 6.0),
)
HL7_TEXT_OF = {code: text for code, text, _unit, _low, _high in HL7_TESTS}
HL7_FLAGS = (("N", 60.0), ("H", 15.0), ("L", 10.0), ("", 15.0))
HL7_STATUS = (("F", 85.0), ("C", 10.0), ("P", 5.0))


def hl7_obx(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """HL7 v2 results flattened a segment field a column: '^'-joined components (code^text^LN, PID-3's
    identifier list) and MSH-7 stamps YYYYMMDDHHMMSS-0400."""
    draw = random.Random(seed)
    people = _people(n)
    header = ["msh_7", "pid_3", "obx_3", "obx_5", "obx_6", "obx_8", "obx_11"]
    rows: "list[list[str]]" = []
    for _index in range(n):
        code, text, unit, low, high = draw.choice(HL7_TESTS)
        moment = _stamp_on_a_change_day(draw)
        rows += [[
            moment.strftime("%Y%m%d%H%M%S") + zoo.eastern_offset(moment).replace(":", ""),
            f"{3000000 + draw.randrange(people)}^^^HOSP^MR",
            f"{code}^{text}^LN",
            f"{draw.uniform(low, high):.1f}",
            f"{unit}^^UCUM",
            _pick(draw, HL7_FLAGS),
            _pick(draw, HL7_STATUS),
        ]]
    return header, rows


def _components_off(series: object) -> int:
    """OBX-3 cells that are not code^text^LN with the text the code names."""
    bad = 0
    for text in series.dropna().astype(str):  # type: ignore[attr-defined]
        parts = text.split("^")
        bad += 0 if len(parts) == 3 and parts[2] == "LN" and HL7_TEXT_OF.get(parts[0]) == parts[1] else 1
    return bad


CABOODLE_WORDS = (("Positive", 10.0), ("Negative", 20.0), ("See comment", 5.0), ("TNP", 5.0))
CABOODLE_FLAGS = (
    ("Normal", 60.0), ("Abnormal", 25.0), ("*Unspecified", 8.0), ("*Unknown", 4.0), ("*Not Applicable", 3.0),
)
CABOODLE_COMMENTS = (("NULL", 70.0), ("Hemolyzed", 10.0), ("Recollect", 10.0), ("Verified", 10.0))


def caboodle_export(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """An Epic Caboodle-style export: PatientDurableKey and DateKey with their -1 and -2 members, a result field of
    numbers and words, '*Unspecified' members, millisecond stamps and the literal NULL."""
    draw = random.Random(seed)
    people = _people(n)
    header = ["PatientDurableKey", "EncounterKey", "DateKey", "ResultValue", "AbnormalFlag", "LoadDttm", "CommentText"]
    rows: "list[list[str]]" = []
    for index in range(n):
        level = draw.random()
        key = "-1" if level < 0.02 else "-2" if level < 0.03 else f"{100000 + draw.randrange(people)}"
        level = draw.random()
        day = _when(draw)
        date_key = "-1" if level < 0.03 else "-2" if level < 0.045 else day.strftime("%Y%m%d")
        level = draw.random()
        result = f"{draw.uniform(0.5, 300.0):.1f}" if level < 0.6 else _pick(draw, CABOODLE_WORDS)
        rows += [[
            key,
            f"{700000000 + index}",
            date_key,
            result,
            _pick(draw, CABOODLE_FLAGS),
            day.strftime("%Y-%m-%d %H:%M:%S") + f".{draw.randint(0, 999):03d}",
            _pick(draw, CABOODLE_COMMENTS),
        ]]
    return header, rows


def _date_keys_bad(series: object) -> int:
    bad = 0
    for text in series.dropna().astype(str):  # type: ignore[attr-defined]
        if text in ("-1", "-2"):
            continue
        try:
            datetime.datetime.strptime(text, "%Y%m%d")
        except ValueError:
            bad += 1
    return bad


CERNER_EVENTS = _zipf(("2797130.00", "704641.00", "2700653.00", "5076214.00", "3410573.00"))
CERNER_WORDS = (("See Comment", 5.0), ("Positive", 10.0), ("Negative", 15.0))
CERNER_UNITS = (("mg/dL", 40.0), ("g/dL", 20.0), ("%", 20.0), ("mmol/L", 20.0))


def cerner_ccl(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A Cerner Millennium CCL export: record numbers written as floats ('31000000.00'), event codes likewise,
    upper-case stamps ('23-FEB-2024 16:40:00'), results with 'See Comment'."""
    draw = random.Random(seed)
    people = _people(n)
    header = ["ENCNTR_ID", "PERSON_ID", "EVENT_CD", "RESULT_VAL", "EVENT_END_DT_TM", "RESULT_UNITS_CD_DISP"]
    rows: "list[list[str]]" = []
    for index in range(n):
        level = draw.random()
        moment = _when(draw)
        rows += [[
            f"{31000000 + index}.00",
            f"{21000000 + draw.randrange(people)}.00",
            _pick(draw, CERNER_EVENTS),
            f"{draw.uniform(0.5, 300.0):.1f}" if level < 0.7 else _pick(draw, CERNER_WORDS),
            f"{moment.day:02d}-{zoo.MONTHS[moment.month - 1].upper()}-{moment.year} {moment.strftime('%H:%M:%S')}",
            _pick(draw, CERNER_UNITS),
        ]]
    return header, rows


FAMILY_SYSTEMS: "tuple[Table, ...]" = (
    Table(
        "omop_measurement", ".csv", omop_measurement,
        lambda header, rows: csv_bytes(header, rows),
        {"omop_cdm": (
            "measurement_id", "person_id", "measurement_concept_id", "measurement_date", "value_as_number",
            "value_as_concept_id", "unit_concept_id", "measurement_source_value",
        )},
        {
            "measurement_id": "identifier", "person_id": "identifier", "measurement_concept_id": "code",
            "value_as_number": "measurement", "value_as_concept_id": "code", "unit_concept_id": "code",
            "measurement_source_value": "code",
        },
        _csv_reader(),
        (
            *_repeats("omop_cdm", "person_id"),
            _listed("omop_cdm", "measurement concepts", "measurement_concept_id", {c for c, *_rest in OMOP_CONCEPTS}),
            _dated("omop_cdm", "measurement_date parses as %Y-%m-%d", "measurement_date", "%Y-%m-%d"),
            _bad("omop_cdm", "value_as_number reads as numbers", "value_as_number", lambda f: _bad_numbers(_t("value_as_number")(f))),
            _ranged("omop_cdm", "value_as_number", r"(?P<n>\d+\.\d\d)"),
            _listed("omop_cdm", "answer concepts", "value_as_concept_id", _levels(OMOP_ANSWERS)),
            _listed("omop_cdm", "unit concepts", "unit_concept_id", {u for _c, _l, u, _lo, _hi in OMOP_CONCEPTS}),
            _pattern("omop_cdm", "source values are LOINC codes", "measurement_source_value", r"\d{1,7}-\d"),
            _bad("omop_cdm", "each concept's unit is its own (read by concept)", "unit_concept_id",
                 lambda f: _units_off_their_concept(f["text"]),
                 zoo.spoil_first_where("unit_concept_id", _omop_valued, "9529")),
        ),
        person="person_id",
    ),
    Table(
        "pcornet_diagnosis", ".csv", pcornet_diagnosis,
        lambda header, rows: csv_bytes(header, rows),
        {"pcornet_cdm": (
            "DIAGNOSISID", "PATID", "ENCOUNTERID", "ADMIT_DATE", "DX", "DX_TYPE", "DX_SOURCE", "PDX", "RAW_DX",
            "RAW_DX_TYPE",
        )},
        {
            "DIAGNOSISID": "identifier", "PATID": "identifier", "ENCOUNTERID": "identifier", "DX": "code",
            "DX_TYPE": "code", "DX_SOURCE": "code", "PDX": "code", "RAW_DX": "code", "RAW_DX_TYPE": "code",
        },
        _csv_reader(),
        (
            *_repeats("pcornet_cdm", "PATID"),
            _dated("pcornet_cdm", "ADMIT_DATE parses as %Y-%m-%d", "ADMIT_DATE", "%Y-%m-%d"),
            _pattern("pcornet_cdm", "DX is ICD-10-CM, ICD-9-CM or SNOMED CT", "DX",
                     "|".join(f"(?:{form})" for form in DX_FORM_OF.values())),
            _bad("pcornet_cdm", "DX is in the system its DX_TYPE names (read by type)", "DX",
                 lambda f: _dx_off_its_type(f["text"]), zoo.spoil_first_where("DX", _is_icd10_type, "486")),
            _listed("pcornet_cdm", "DX_TYPE with NI", "DX_TYPE", _levels(PCORNET_TYPES)),
            _listed("pcornet_cdm", "DX_SOURCE with NI, UN and OT", "DX_SOURCE", _levels(PCORNET_SOURCES)),
            _listed("pcornet_cdm", "PDX with NI", "PDX", _levels(PCORNET_PDX)),
            _pattern("pcornet_cdm", "RAW_DX as the source wrote it, no point", "RAW_DX", r"[A-Z0-9]{3,18}"),
            _listed("pcornet_cdm", "RAW_DX_TYPE", "RAW_DX_TYPE", {"ICD10CM", "ICD9CM", "SNOMED"}),
        ),
        person="PATID",
    ),
    Table(
        "i2b2_facts", ".csv", i2b2_facts,
        lambda header, rows: csv_bytes(header, rows),
        {"i2b2_eav": (
            "encounter_num", "patient_num", "concept_cd", "provider_id", "start_date", "modifier_cd", "instance_num",
            "valtype_cd", "tval_char", "nval_num", "units_cd",
        )},
        {
            "encounter_num": "identifier", "patient_num": "identifier", "concept_cd": "code", "nval_num": "measurement",
            "units_cd": "code",
        },
        _csv_reader(),
        (
            *_repeats("i2b2_eav", "patient_num"),
            _pattern("i2b2_eav", "concepts with their vocabulary prefix", "concept_cd",
                     r"(ICD10CM|LOINC|DEM\|GENDER|DEM\|VITAL):[A-Z0-9.\-]+"),
            _bad("i2b2_eav", "the vocabulary prefixes are i2b2's", "concept_cd",
                 lambda f: _prefixes_off(_t("concept_cd")(f)), spoil_cell("concept_cd", "ICDX:E11.9")),
            *_present("i2b2_eav", "some fact is a demographic (DEM|GENDER:)", "concept_cd", r"^DEM\|GENDER:",
                      spoil_every("concept_cd", lambda v: v.replace("DEM|GENDER:", "DEM|VITAL:"))),
            _dated("i2b2_eav", "start_date parses to the millisecond", "start_date", "%Y-%m-%d %H:%M:%S.%f"),
            _listed("i2b2_eav", "provider '@'", "provider_id", {"@"}),
            _listed("i2b2_eav", "modifier '@'", "modifier_cd", {"@"}),
            _listed("i2b2_eav", "value types", "valtype_cd", {"N"}),
            _listed("i2b2_eav", "text values E", "tval_char", {"E"}),
            _bad("i2b2_eav", "numeric values read as numbers", "nval_num", lambda f: _bad_numbers(_t("nval_num")(f))),
            _ranged("i2b2_eav", "nval_num", r"(?P<n>\d+\.\d\d)"),
        ),
        person="patient_num",
    ),
    Table(
        "fhir_observations", ".csv", fhir_observations,
        lambda header, rows: csv_bytes(header, rows),
        {"fhir_flattened": (
            "id", "subject_reference", "code_coding", "value_quantity_value", "value_quantity_unit",
            "effective_date_time", "status", "omb_category",
        )},
        {
            "id": "identifier", "subject_reference": "identifier", "code_coding": "code",
            "value_quantity_value": "measurement", "value_quantity_unit": "code", "omb_category": "code",
        },
        _csv_reader(),
        (
            *_repeats("fhir_flattened", "subject_reference"),
            _pattern("fhir_flattened", "references Patient/123", "subject_reference", r"Patient/\d+"),
            _pattern("fhir_flattened", "codings system|code", "code_coding", r"http://loinc\.org\|\d{1,7}-\d"),
            _bad("fhir_flattened", "quantities read as numbers", "value_quantity_value",
                 lambda f: _bad_numbers(_t("value_quantity_value")(f))),
            _ranged("fhir_flattened", "value_quantity_value", r"(?P<n>\d+\.\d)"),
            _listed("fhir_flattened", "units", "value_quantity_unit", {u for _c, u, _lo, _hi in FHIR_CODES}),
            _dated("fhir_flattened", "instants parse with their offset", "effective_date_time", "%Y-%m-%dT%H:%M:%S%z", utc=True),
            _bad("fhir_flattened", "each instant wears an offset in force on its date", "effective_date_time",
                 lambda f: _wrong_offsets_by(_t("effective_date_time")(f), zoo.eastern_offsets, "%Y-%m-%dT%H:%M:%S", 19),
                 spoil_cell("effective_date_time", "2024-07-01T10:00:00-05:00")),
            _listed("fhir_flattened", "observation status", "status", _levels(FHIR_STATUS)),
            _pattern("fhir_flattened", "category codings under the CDC code system", "omb_category",
                     re.escape(CDC_ROOT) + r"\d{4}-\d"),
            _listed("fhir_flattened", "CDC category codes", "omb_category", {CDC_ROOT + code for code, _w in CDC_CATEGORY}),
        ),
        person="subject_reference",
    ),
    Table(
        "hl7_obx", ".csv", hl7_obx,
        lambda header, rows: csv_bytes(header, rows),
        {"hl7v2_flattened": ("msh_7", "pid_3", "obx_3", "obx_5", "obx_6", "obx_8", "obx_11")},
        {"pid_3": "identifier", "obx_3": "code", "obx_5": "measurement", "obx_6": "code", "obx_8": "code", "obx_11": "code"},
        _csv_reader(),
        (
            *_repeats("hl7v2_flattened", "pid_3"),
            _dated("hl7v2_flattened", "MSH-7 stamps YYYYMMDDHHMMSS-0400", "msh_7", "%Y%m%d%H%M%S%z", utc=True),
            _bad("hl7v2_flattened", "MSH-7 wears an offset in force on its date", "msh_7",
                 lambda f: _wrong_offsets_by(_t("msh_7")(f), _compact_eastern, "%Y%m%d%H%M%S", 14),
                 spoil_cell("msh_7", "20240701100000-0500")),
            _pattern("hl7v2_flattened", "PID-3 as id^^^HOSP^MR", "pid_3", r"\d{7}\^\^\^HOSP\^MR"),
            _bad("hl7v2_flattened", "OBX-3 is code^text^LN, the text its code's own", "obx_3",
                 lambda f: _components_off(_t("obx_3")(f)), spoil_cell("obx_3", "2345-7^Sodium^LN")),
            _bad("hl7v2_flattened", "OBX-5 reads as numbers", "obx_5", lambda f: _bad_numbers(_t("obx_5")(f))),
            _ranged("hl7v2_flattened", "obx_5", r"(?P<n>\d+\.\d)"),
            _pattern("hl7v2_flattened", "OBX-6 units as unit^^UCUM", "obx_6", r"[^\^]+\^\^UCUM"),
            _listed("hl7v2_flattened", "OBX-8 flags", "obx_8", _levels(HL7_FLAGS) - {""}),
            _listed("hl7v2_flattened", "OBX-11 result status", "obx_11", _levels(HL7_STATUS)),
        ),
        person="pid_3",
        leaks=(("pid_3", "values"),),
    ),
    Table(
        "caboodle_export", ".csv", caboodle_export,
        lambda header, rows: csv_bytes(header, rows),
        {"epic_caboodle": ("PatientDurableKey", "EncounterKey", "DateKey", "ResultValue", "AbnormalFlag", "LoadDttm", "CommentText")},
        {
            "PatientDurableKey": "identifier", "EncounterKey": "identifier", "ResultValue": "measurement",
            "AbnormalFlag": "code",
        },
        _csv_reader(),
        (
            *_repeats("epic_caboodle", "PatientDurableKey"),
            _pattern("epic_caboodle", "durable keys of six figures, or -1 and -2", "PatientDurableKey", r"-[12]|1\d{5}"),
            *_rare("epic_caboodle", "some row's durable key is the -1 member", "PatientDurableKey", r"^-1$",
                   spoil_every("PatientDurableKey", lambda v: "100000" if v == "-1" else v), crowd("PatientDurableKey", "-1")),
            _bad("epic_caboodle", "DateKeys are dates YYYYMMDD, or -1 and -2", "DateKey", lambda f: _date_keys_bad(_t("DateKey")(f))),
            *_rare("epic_caboodle", "some DateKey is the -1 member", "DateKey", r"^-1$",
                   spoil_every("DateKey", lambda v: "20240101" if v == "-1" else v), crowd("DateKey", "-1")),
            _pattern("epic_caboodle", "a result is a number or a word", "ResultValue",
                     r"\d+(\.\d+)?|Positive|Negative|See comment|TNP"),
            _bad("epic_caboodle", "the results read past their words", "ResultValue",
                 lambda f: _bad_numbers(_not_in(tuple(_levels(CABOODLE_WORDS)))(_t("ResultValue")(f)))),  # type: ignore[operator]
            _listed("epic_caboodle", "flags with the *Unspecified members", "AbnormalFlag", _levels(CABOODLE_FLAGS)),
            _dated("epic_caboodle", "LoadDttm to the millisecond", "LoadDttm", "%Y-%m-%d %H:%M:%S.%f"),
            _bad("epic_caboodle", "comments a word or the literal NULL", "CommentText",
                 lambda f: _bad_pattern(_r("CommentText")(f), r"NULL|Hemolyzed|Recollect|Verified")),
        ),
        person="PatientDurableKey",
        leaks=(("PatientDurableKey", "values"),),
    ),
    Table(
        "cerner_ccl", ".csv", cerner_ccl,
        lambda header, rows: csv_bytes(header, rows),
        {"cerner_ccl": ("ENCNTR_ID", "PERSON_ID", "EVENT_CD", "RESULT_VAL", "EVENT_END_DT_TM", "RESULT_UNITS_CD_DISP")},
        {"ENCNTR_ID": "identifier", "PERSON_ID": "identifier", "EVENT_CD": "code", "RESULT_VAL": "measurement"},
        _csv_reader(),
        (
            *_repeats("cerner_ccl", "PERSON_ID"),
            _pattern("cerner_ccl", "encounter numbers written 31000000.00", "ENCNTR_ID", r"\d{8}\.00"),
            _pattern("cerner_ccl", "person numbers written 21000000.00", "PERSON_ID", r"\d{8}\.00"),
            _listed("cerner_ccl", "event codes written as floats", "EVENT_CD", _levels(CERNER_EVENTS)),
            _pattern("cerner_ccl", "a result is a number or a word", "RESULT_VAL", r"\d+\.\d|See Comment|Positive|Negative"),
            _bad("cerner_ccl", "the results read past their words", "RESULT_VAL",
                 lambda f: _bad_numbers(_not_in(tuple(_levels(CERNER_WORDS)))(_t("RESULT_VAL")(f)))),  # type: ignore[operator]
            _dated("cerner_ccl", "stamps parse as %d-%b-%Y %H:%M:%S", "EVENT_END_DT_TM", "%d-%b-%Y %H:%M:%S"),
            _listed("cerner_ccl", "units", "RESULT_UNITS_CD_DISP", _levels(CERNER_UNITS)),
        ),
        person="PERSON_ID",
        leaks=(("ENCNTR_ID", "values"), ("PERSON_ID", "values")),
    ),
)


# -- family 5: the file shapes (Excel-readable CSV and workbook shapes) ---------

WARD_COMMENTS = (
    ("Évaluation faite", 25.0), ("Patient stable", 30.0), ("Reprise à domicile", 15.0), ("Ürin normal", 10.0),
    ("Contrôle demain", 10.0), ("Pas de fièvre", 10.0),
)
WARD_UNITS = (("Médecine", 40.0), ("Chirurgie", 35.0), ("Pédiatrie", 25.0))


def unicode_text(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A sheet saved as Excel's "Unicode Text": UTF-16 with its byte-order mark, tab-delimited, CRLF."""
    draw = random.Random(seed)
    header = ["ward_ref", "unit", "admit_date", "comment", "score"]
    rows: "list[list[str]]" = []
    for index in range(n):
        rows += [[
            f"W{600000 + index}",
            _pick(draw, WARD_UNITS),
            _when(draw).date().isoformat(),
            _pick(draw, WARD_COMMENTS),
            f"{draw.randint(0, 10)}",
        ]]
    return header, rows


def utf16_bytes(header: "list[str]", rows: "list[list[str]]") -> bytes:
    return csv_bytes(header, rows, delimiter="\t", newline="\r\n", encoding="utf-16")


SMART_COMMENTS = (
    ("Patient said “fine” today", 30.0), ("Family’s request noted", 20.0), ("Pain 3–4 at rest", 15.0),
    ("Follow-up — two weeks", 15.0), ("‘Do not resuscitate’ reviewed", 10.0), ("Wound clean…", 10.0),
)


def smart_quotes(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Comments typed in Word and saved from Excel as CSV in Windows-1252: curly quotes, dashes, an ellipsis."""
    draw = random.Random(seed)
    header = ["note_ref", "category", "comment"]
    rows: "list[list[str]]" = []
    for index in range(n):
        rows += [[f"NT{700000 + index}", draw.choice(("Nursing", "Social work", "Chaplain")), _pick(draw, SMART_COMMENTS)]]
    return header, rows


def _cp1252_mojibake(frame: object) -> int:
    """Cells showing Windows-1252 punctuation read as another encoding ('â€œ', 'â€™', '\\x93')."""
    bad = 0
    for name in frame.columns:  # type: ignore[attr-defined]
        values = frame[name].dropna().astype(str)  # type: ignore[index]
        bad += int(values.str.contains("â€|[\x91-\x97]|�", regex=True).sum())
    return bad


SAS_ARMS = (("A", 50.0), ("B", 50.0))
SAS_VISITS = (("BASELINE", 40.0), ("WEEK 4", 30.0), ("WEEK 12", 30.0))


def sas_export(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A SAS dataset exported to CSV: a lone '.' where a number is missing."""
    draw = random.Random(seed)
    people = _people(n)
    header = ["subjid", "visit", "arm", "sbp", "ldl"]
    rows: "list[list[str]]" = []
    for _index in range(n):
        rows += [[
            f"S-{draw.randrange(people):05d}",
            _pick(draw, SAS_VISITS),
            _pick(draw, SAS_ARMS),
            "." if draw.random() < 0.08 else f"{draw.randint(95, 180)}",
            "." if draw.random() < 0.12 else f"{draw.gauss(110.0, 30.0):.1f}",
        ]]
    return header, rows


WIDE_ITEMS = tuple(f"item_{place:03d}" for place in range(1, 301))
# The items as a survey tool's label export writes them. MEASURED on this
# lane's head (planning-notes wave6/E0c/probe-20k-slow.log): written as
# the raw codes 0 to 4, each of the 300 is put the measurement, code or
# identifier question (301 questions at 600 rows), and the table takes
# 46 s at 600 rows and 1,499 s at 20,000 -- over K-HZ-03's 900 s for a
# whole shard on its own; written as labels, it asks one.
ITEM_LEVELS = (("Never", 30.0), ("Rarely", 25.0), ("Sometimes", 20.0), ("Often", 15.0), ("Always", 7.0), ("", 3.0))
ITEM_WORDS = {"Never", "Rarely", "Sometimes", "Often", "Always"}


def wide_export(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A wide export: 300 questionnaire items, as labels, beside the patient and the date, 302 columns."""
    draw = random.Random(seed)
    header = ["patient_ref", "visit_date", *WIDE_ITEMS]
    values = [value for value, _weight in ITEM_LEVELS]
    weights = [weight for _value, weight in ITEM_LEVELS]
    rows: "list[list[str]]" = []
    for index in range(n):
        rows += [[f"PR{800000 + index}", _when(draw).date().isoformat(), *draw.choices(values, weights, k=len(WIDE_ITEMS))]]
    return header, rows


def _items_bad(frame: object) -> int:
    return sum(_bad_set(frame[column], ITEM_WORDS) for column in WIDE_ITEMS)  # type: ignore[index]


ORDER_TESTS = (("CBC", 35.0), ("BMP", 30.0), ("Lipid panel", 15.0), ("TSH", 10.0), ("HbA1c", 10.0))
ORDER_STATUS = (("Resulted", 75.0), ("Pending", 15.0), ("Cancelled", 10.0))


def trailing_comma(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Orders exported with a delimiter after the last field of every line."""
    draw = random.Random(seed)
    people = _people(n)
    header = ["order_ref", "patient_id", "order_date", "test", "status"]
    rows: "list[list[str]]" = []
    for index in range(n):
        rows += [[
            f"OR{900000 + index}", _person(draw, people), _when(draw).date().isoformat(),
            _pick(draw, ORDER_TESTS), _pick(draw, ORDER_STATUS),
        ]]
    return header, rows


def trailing_bytes(header: "list[str]", rows: "list[list[str]]") -> bytes:
    text = csv_bytes(header, rows).decode("utf-8")
    return "".join(line + ",\n" for line in text.split("\n") if line).encode("utf-8")


ZIPS_LOST = (
    ("2139", 12.0), ("6510", 10.0), ("1803", 9.0), ("7030", 9.0), ("8540", 8.0), ("2115", 8.0),
    ("10027", 12.0), ("19104", 10.0), ("60611", 8.0), ("94110", 7.0), ("33101", 7.0),
)


def excel_mangled(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Codes Excel mangled before the CSV was saved: long numbers shown in scientific notation, ZIPs that lost
    their leading nought."""
    draw = random.Random(seed)
    header = ["member_ref", "npi_shown", "zip_lost", "account_shown"]
    rows: "list[list[str]]" = []
    for index in range(n):
        rows += [[
            f"MB{100000 + index}",
            f"{draw.randint(1_000_000_000, 1_999_999_999):.5E}",
            _pick(draw, ZIPS_LOST),
            f"{draw.randint(100_000_000_000, 999_999_999_999):.5E}",
        ]]
    return header, rows


def workbook_1904(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Visits in a workbook kept in the 1904 date system (Excel for the Mac's old default): serial numbers from 1904."""
    draw = random.Random(seed)
    header = ["patient_ref", "visit_date", "score"]
    rows: "list[list[str]]" = []
    epoch = datetime.date(1904, 1, 1)
    for index in range(n):
        day = zoo._day(draw, datetime.date(2023, 1, 1), datetime.date(2024, 12, 31))
        rows += [[f"VB{300000 + index}", f"{(day - epoch).days}", f"{draw.randint(0, 100)}"]]
    return header, rows


def book_1904(header: "list[str]", rows: "list[list[str]]") -> bytes:
    """The visits as a workbook in the 1904 date system: date cells styled as dates, numbers typed, text inline."""
    import workbooks

    body: "list[tuple[int, list[str]]]" = [
        (1, [workbooks.cell(f"{zoo._letter(place)}1", header[place], "inlineStr") for place in range(len(header))])
    ]
    for index in range(len(rows)):
        number = index + 2
        cells: "list[str]" = []
        for place in range(len(header)):
            value = rows[index][place]
            where = f"{zoo._letter(place)}{number}"
            typed = re.fullmatch(r"-?\d+", value) is not None
            if header[place] == "visit_date" and typed:
                cells += [workbooks.cell(where, value, "", 1)]
            elif header[place] == "score" and typed:
                cells += [workbooks.cell(where, value)]
            else:
                cells += [workbooks.cell(where, value, "inlineStr")]
        body += [(number, cells)]
    last = f"{zoo._letter(len(header) - 1)}{len(rows) + 1}"
    return workbooks.package(
        [
            ("[Content_Types].xml", workbooks._content_types(1, False, False, False)),
            ("_rels/.rels", workbooks._root_rels()),
            ("xl/workbook.xml", workbooks._workbook([("Visits", "")], epoch_1904=True)),
            ("xl/_rels/workbook.xml.rels", workbooks._workbook_rels(1, False)),
            ("xl/styles.xml", workbooks._styles()),
            ("xl/worksheets/sheet1.xml", workbooks.sheet(body, dimension=f"A1:{last}")),
        ]
    )


def _visits_outside(series: object) -> int:
    """Visit dates read outside 2023 and 2024 (a 1904 serial read in the 1900 system lands four years early)."""
    import pandas

    days = pandas.to_datetime(series.dropna(), errors="coerce")  # type: ignore[attr-defined]
    return int((days.isna() | (days.dt.year < 2023) | (days.dt.year > 2024)).sum())


APOSTROPHE_CODES = _zipf(("'0450", "'0250", "'0300", "'0320", "'0360", "'0636"))


def apostrophe_codes(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A sheet whose codes were typed with Excel's leading apostrophe, saved as CSV with the apostrophe kept."""
    draw = random.Random(seed)
    header = ["record_ref", "rev_code", "amount"]
    rows: "list[list[str]]" = []
    for index in range(n):
        rows += [[f"'{100000 + index:06d}", _pick(draw, APOSTROPHE_CODES), f"{draw.lognormvariate(5.0, 1.0):.2f}"]]
    return header, rows


FAMILY_FILES: "tuple[Table, ...]" = (
    Table(
        "unicode_text", ".txt", unicode_text, utf16_bytes,
        {"utf16_text": ("ward_ref", "unit", "admit_date", "comment", "score")},
        {"ward_ref": "identifier", "score": "measurement"},
        _csv_reader(sep="\t", encoding="utf-16"),
        (
            Check("utf16_text", "the file is UTF-16 little-endian, as Excel writes it, with its byte-order mark", "same",
                  lambda f: bytes(f.get("bytes", b""))[:2] == b"\xff\xfe", "", lambda header, rows: None,  # type: ignore[call-overload]
                  lambda header, rows: csv_bytes(header, rows, delimiter="\t", newline="\r\n", encoding="utf-16-be", mark=True)),
            _listed("utf16_text", "units with their accents", "unit", _levels(WARD_UNITS)),
            _listed("utf16_text", "comments with their accents", "comment", _levels(WARD_COMMENTS)),
            _bad("utf16_text", "no cell reads as mojibake", "comment", lambda f: zoo._mojibake(f["text"]),
                 spoil_cell("comment", "Ã‰valuation faite")),
            _dated("utf16_text", "admit_date parses as %Y-%m-%d", "admit_date", "%Y-%m-%d"),
            _ranged("utf16_text", "score", r"(?P<n>\d+)", 3.0),
        ),
        separator="tab",
    ),
    Table(
        "smart_quotes", ".csv", smart_quotes,
        lambda header, rows: csv_bytes(header, rows, encoding="cp1252"),
        {"cp1252_smart_quotes": ("note_ref", "category", "comment")},
        {"note_ref": "identifier"},
        _csv_reader(encoding="cp1252"),
        (
            _listed("cp1252_smart_quotes", "comments with their curly quotes and dashes", "comment", _levels(SMART_COMMENTS)),
            _bad("cp1252_smart_quotes", "no Windows-1252 punctuation reads as mojibake", "comment",
                 lambda f: _cp1252_mojibake(f["text"]), spoil_cell("comment", "Patient said â€œfine today")),
            *_present("cp1252_smart_quotes", "some comment keeps its curly quotes", "comment", "[“”‘’]",
                      spoil_every("comment", lambda v: re.sub("[“”‘’]", "'", v))),
            _listed("cp1252_smart_quotes", "categories", "category", {"Nursing", "Social work", "Chaplain"}),
        ),
    ),
    Table(
        "sas_export", ".csv", sas_export,
        lambda header, rows: csv_bytes(header, rows),
        {"sas_dot_missing": ("subjid", "visit", "arm", "sbp", "ldl")},
        {"subjid": "identifier", "sbp": "measurement", "ldl": "measurement"},
        _csv_reader(),
        (
            *_repeats("sas_dot_missing", "subjid"),
            _listed("sas_dot_missing", "visits", "visit", _levels(SAS_VISITS)),
            _listed("sas_dot_missing", "arms", "arm", {"A", "B"}),
            _bad("sas_dot_missing", "sbp reads as numbers past SAS's '.'", "sbp",
                 lambda f: _bad_numbers(_not_in((".",))(_t("sbp")(f)))),  # type: ignore[operator]
            _ranged("sas_dot_missing", "sbp", r"(?P<n>\d+)"),
            *_rare("sas_dot_missing", "some sbp is SAS's '.' missing", "sbp", r"^\.$",
                   spoil_every("sbp", lambda v: "" if v == "." else v), crowd("sbp", ".")),
            _bad("sas_dot_missing", "ldl reads as numbers past SAS's '.'", "ldl",
                 lambda f: _bad_numbers(_not_in((".",))(_t("ldl")(f)))),  # type: ignore[operator]
            _ranged("sas_dot_missing", "ldl", r"(?P<n>-?\d+\.\d)"),
            *_rare("sas_dot_missing", "some ldl is SAS's '.' missing", "ldl", r"^\.$",
                   spoil_every("ldl", lambda v: "" if v == "." else v), crowd("ldl", ".")),
        ),
        person="subjid",
    ),
    Table(
        "wide_export", ".csv", wide_export,
        lambda header, rows: csv_bytes(header, rows),
        {"wide_table": ("patient_ref", "visit_date", *WIDE_ITEMS)},
        {"patient_ref": "identifier"},
        _csv_reader(),
        (
            Check("wide_table", "the file holds its 302 columns", "same",
                  lambda f: int(f["inferred"].shape[1]), "", spoil_extra_column),  # type: ignore[attr-defined]
            _bad("wide_table", "every item a listed label or blank", "item_001", lambda f: _items_bad(f["text"])),
            _dated("wide_table", "visit_date parses as %Y-%m-%d", "visit_date", "%Y-%m-%d"),
        ),
    ),
    Table(
        "trailing_comma", ".csv", trailing_comma, trailing_bytes,
        {"trailing_delimiter": ("order_ref", "patient_id", "order_date", "test", "status")},
        {"order_ref": "identifier", "patient_id": "identifier"},
        _csv_reader(),
        (
            Check("trailing_delimiter", "the file reads as its five columns and one unnamed", "same",
                  lambda f: list(f["inferred"].columns), "", lambda header, rows: None,  # type: ignore[attr-defined]
                  lambda header, rows: csv_bytes(header, rows)),
            *_repeats("trailing_delimiter"),
            _dated("trailing_delimiter", "order_date parses as %Y-%m-%d", "order_date", "%Y-%m-%d"),
            _listed("trailing_delimiter", "tests", "test", _levels(ORDER_TESTS)),
            _listed("trailing_delimiter", "status", "status", _levels(ORDER_STATUS)),
        ),
        person="patient_id",
    ),
    Table(
        "excel_mangled", ".csv", excel_mangled,
        lambda header, rows: csv_bytes(header, rows),
        {"excel_mangled_codes": ("member_ref", "npi_shown", "zip_lost", "account_shown")},
        {"member_ref": "identifier", "npi_shown": "identifier", "zip_lost": "code", "account_shown": "identifier"},
        _csv_reader(),
        (
            _pattern("excel_mangled_codes", "NPIs shown d.ddddDE+09", "npi_shown", r"\d\.\d{5}E\+09"),
            _pattern("excel_mangled_codes", "ZIPs of four or five figures", "zip_lost", r"\d{4,5}"),
            *_present("excel_mangled_codes", "some ZIP lost its leading nought (four figures)", "zip_lost", r"^\d{4}$",
                      spoil_every("zip_lost", lambda v: v.zfill(5))),
            _pattern("excel_mangled_codes", "account numbers shown d.dddddE+11", "account_shown", r"\d\.\d{5}E\+11"),
        ),
        leaks=(("zip_lost", "values"), ("account_shown", "values")),
    ),
    Table(
        "workbook_1904", ".xlsx", workbook_1904, book_1904,
        {"workbook_1904_dates": ("patient_ref", "visit_date", "score")},
        {"patient_ref": "identifier", "score": "measurement"},
        zoo._excel_reader,
        (
            Check("workbook_1904_dates", "visit_date reads as dates", "same",
                  lambda f: str(_i("visit_date")(f).dtype), "visit_date"),  # type: ignore[attr-defined]
            _bad("workbook_1904_dates", "visit dates fall in 2023 and 2024 (read in the 1904 system)", "visit_date",
                 lambda f: _visits_outside(_i("visit_date")(f)), spoil_every("visit_date", lambda v: f"{int(v) + 1462}")),
            _ranged("workbook_1904_dates", "score", r"(?P<n>\d+)", 3.0),
        ),
    ),
    Table(
        "apostrophe_codes", ".csv", apostrophe_codes,
        lambda header, rows: csv_bytes(header, rows),
        {"leading_apostrophe": ("record_ref", "rev_code", "amount")},
        {"record_ref": "identifier", "rev_code": "code", "amount": "measurement"},
        _csv_reader(),
        (
            _pattern("leading_apostrophe", "record references keep their apostrophe", "record_ref", r"'\d{6}"),
            _pattern("leading_apostrophe", "revenue codes keep their apostrophe and nought", "rev_code", r"'0\d{3}"),
            *_present("leading_apostrophe", "some code is written with Excel's apostrophe", "rev_code", r"^'",
                      spoil_every("rev_code", lambda v: v.lstrip("'"))),
            _ranged("leading_apostrophe", "amount", r"(?P<n>\d+\.\d\d)"),
        ),
    ),
)


# -- family 6: the HIPAA and de-identified shapes (HIPAA first) ----------------

FIRST_NAMES = (
    "Maria", "James", "Aisha", "Wei", "Olga", "Carlos", "Fatima", "John", "Priya", "Liam", "Sofia", "Kwame", "Hannah",
    "Mateo", "Yuki", "Omar", "Elena", "Noah", "Amara", "Lucas", "Mei", "Diego", "Zara", "Ethan", "Ines", "Tariq",
    "Grace", "Ivan", "Leila", "Samuel", "Nadia", "Jonah", "Rosa", "Arjun", "Clara", "Kofi", "Anya", "Felix", "Lina",
    "Hugo",
)
LAST_NAMES = (
    "Gonzalez", "Smith", "Okafor", "Zhang", "Ivanova", "Mendes", "Haddad", "Murphy", "Raman", "Walsh", "Rossi",
    "Mensah", "Becker", "Silva", "Tanaka", "Farouk", "Petrova", "Clarke", "Diallo", "Moreau", "Chen", "Ortiz", "Khan",
    "Novak", "Duarte", "Aziz", "Bennett", "Kowalski", "Rahimi", "Adeyemi", "Sato", "Lindqvist", "Vargas", "Iyer",
    "Hoffmann", "Boateng", "Sokolova", "Weber", "Nasser", "Laurent",
)
STREETS = ("Elm", "Maple", "Oak", "Cedar", "Pine", "Willow", "Harbor", "Lake", "Hill", "River", "Mill", "Park")
SUFFIXES = ("St", "Ave", "Rd", "Blvd", "Ln")
PHI_ZIPS = tuple(f"{52240 + 7 * place}" for place in range(59))


def phi_registry(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A registry export holding every direct identifier of HIPAA's Safe Harbor list a hospital file carries:
    names, street addresses, telephone numbers, e-mail addresses, social security numbers, ZIPs, birth dates, medical record numbers.
    Every value is invented: 555 numbers, the reserved example.org, social security numbers in the 900 area."""
    draw = random.Random(seed)
    header = ["med_rec_no", "patient_name", "street_address", "phone", "email", "ssn", "zip5", "birth_date"]
    rows: "list[list[str]]" = []
    for index in range(n):
        first, last = draw.choice(FIRST_NAMES), draw.choice(LAST_NAMES)
        born = zoo._day(draw, datetime.date(1930, 1, 1), datetime.date(2005, 12, 31))
        rows += [[
            f"MR{4000000 + index}",
            f"{first} {last}",
            f"{draw.randint(1, 9999)} {draw.choice(STREETS)} {draw.choice(SUFFIXES)}",
            f"({draw.randint(201, 989)}) 555-{draw.randint(0, 9999):04d}",
            f"{first.lower()}.{last.lower()}{draw.randint(1, 999)}@example.org",
            f"9{draw.randint(0, 99):02d}-{draw.randint(10, 99)}-{draw.randint(0, 9999):04d}",
            draw.choice(PHI_ZIPS),
            born.isoformat(),
        ]]
    return header, rows


PHI_COLUMNS = ("med_rec_no", "patient_name", "street_address", "phone", "email", "ssn", "zip5", "birth_date")
VISIT_DEPARTMENTS = (("Clinic A", 40.0), ("Clinic B", 30.0), ("Urgent care", 20.0), ("Telehealth", 10.0))


def long_visits_record_numbers(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Visits on a long table whose medical record number nobody declared: several rows a patient."""
    draw = random.Random(seed)
    people = _people(n)
    header = ["visit_ref", "med_rec_no", "visit_date", "department"]
    rows: "list[list[str]]" = []
    for index in range(n):
        rows += [[
            f"V{500000 + index}",
            f"A{1000000 + draw.randrange(people) * 37 % 9000000:07d}",
            _when(draw).date().isoformat(),
            _pick(draw, VISIT_DEPARTMENTS),
        ]]
    return header, rows


DURABLE_KEYS = tuple(f"{100001 + place}" for place in range(60))
NUMBER_ZIPS = tuple(f"{52240 + 3 * place}" for place in range(59))
UDI_NUMBERS = tuple(f"{10885403000000 + 7919 * place}" for place in range(49))


def numeric_identifiers(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Keys and Safe Harbor numbers that read as numbers, their question left unanswered: a Caboodle
    PatientDurableKey of 60 keys with its -1 and -2 members, five-figure ZIPs, 14-figure UDIs."""
    draw = random.Random(seed)
    header = ["durable_key", "zip_number", "udi_number", "sbp"]
    key_weights = [3.0 + (place * 7) % 18 for place in range(len(DURABLE_KEYS))]
    rows: "list[list[str]]" = []
    for _index in range(n):
        level = draw.random()
        key = "-1" if level < 0.02 else "-2" if level < 0.03 else draw.choices(DURABLE_KEYS, key_weights)[0]
        rows += [[key, draw.choice(NUMBER_ZIPS), draw.choice(UDI_NUMBERS), f"{draw.randint(95, 180)}"]]
    return header, rows


ZIP3_MASKED = (("021**", 20.0), ("100**", 18.0), ("191**", 14.0), ("606**", 12.0), ("941**", 10.0), ("331**", 10.0), ("000**", 16.0))


def safe_harbor(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A table de-identified under Safe Harbor: ages over 89 written '90+', ZIPs cut to three figures
    ('021**', '000**' where few live), birth years alone, dates shifted a century and more (as MIMIC shifts them)."""
    draw = random.Random(seed)
    header = ["person_ref", "age_top", "zip3", "birth_year", "shifted_admit"]
    rows: "list[list[str]]" = []
    for index in range(n):
        age = draw.randint(18, 104) if draw.random() < 0.3 else draw.randint(18, 89)
        rows += [[
            f"SH{200000 + index}",
            "90+" if age >= 90 else f"{age}",
            _pick(draw, ZIP3_MASKED),
            f"{2024 - age}",
            zoo._day(draw, datetime.date(2110, 1, 1), datetime.date(2190, 12, 31)).isoformat(),
        ]]
    return header, rows


def _ages_past_89(series: object) -> int:
    return sum(1 for text in series.dropna().astype(str) if text.isdigit() and int(text) > 89)  # type: ignore[attr-defined]


def _years_outside(series: object, low: int, high: int, form: str) -> int:
    import pandas

    days = pandas.to_datetime(series.dropna().astype(str), format=form, errors="coerce")  # type: ignore[attr-defined]
    return int((days.isna() | (days.dt.year < low) | (days.dt.year > high)).sum())


FAMILY_HIPAA: "tuple[Table, ...]" = (
    Table(
        "phi_registry", ".csv", phi_registry,
        lambda header, rows: csv_bytes(header, rows),
        {"phi_columns": PHI_COLUMNS},
        {
            "med_rec_no": "identifier", "patient_name": "identifier", "street_address": "identifier", "phone": "identifier",
            "email": "identifier", "ssn": "identifier",
        },
        _csv_reader(),
        (
            _pattern("phi_columns", "medical record numbers", "med_rec_no", r"MR\d{7}"),
            _pattern("phi_columns", "names, first and last", "patient_name", r"[A-Z][a-z]+ [A-Z][a-z]+"),
            _pattern("phi_columns", "street addresses", "street_address", r"\d{1,4} [A-Z][a-z]+ (St|Ave|Rd|Blvd|Ln)"),
            _pattern("phi_columns", "telephone numbers (NNN) 555-NNNN", "phone", r"\(\d{3}\) 555-\d{4}"),
            _pattern("phi_columns", "e-mail addresses", "email", r"[a-z]+\.[a-z]+\d*@example\.org"),
            _pattern("phi_columns", "social security numbers", "ssn", r"9\d{2}-\d{2}-\d{4}"),
            _pattern("phi_columns", "five-figure ZIPs", "zip5", r"\d{5}"),
            _dated("phi_columns", "birth dates parse as %Y-%m-%d", "birth_date", "%Y-%m-%d"),
        ),
        leaks=tuple((column, "printed values" if column == "birth_date" else "values") for column in PHI_COLUMNS),
    ),
    Table(
        "long_visits_record_numbers", ".csv", long_visits_record_numbers,
        lambda header, rows: csv_bytes(header, rows),
        {"undeclared_record_number_long": ("visit_ref", "med_rec_no", "visit_date", "department")},
        {"visit_ref": "identifier"},
        _csv_reader(),
        (
            _pattern("undeclared_record_number_long", "record numbers A and seven figures", "med_rec_no", r"A\d{7}"),
            *_repeats("undeclared_record_number_long", "med_rec_no"),
            _dated("undeclared_record_number_long", "visit_date parses as %Y-%m-%d", "visit_date", "%Y-%m-%d"),
            _listed("undeclared_record_number_long", "departments", "department", _levels(VISIT_DEPARTMENTS)),
        ),
        person="med_rec_no",
        leaks=(("med_rec_no", "values"),),
    ),
    Table(
        "numeric_identifiers", ".csv", numeric_identifiers,
        lambda header, rows: csv_bytes(header, rows),
        {"numeric_keys_unanswered": ("durable_key", "zip_number", "udi_number", "sbp")},
        {"sbp": "measurement"},
        _csv_reader(),
        (
            _pattern("numeric_keys_unanswered", "durable keys of six figures, or -1 and -2", "durable_key", r"-[12]|100\d{3}"),
            _pattern("numeric_keys_unanswered", "ZIPs of five figures", "zip_number", r"\d{5}"),
            _pattern("numeric_keys_unanswered", "UDIs of fourteen figures", "udi_number", r"\d{14}"),
            _ranged("numeric_keys_unanswered", "sbp", r"(?P<n>\d+)"),
        ),
        leaks=(("durable_key", "values"), ("zip_number", "values"), ("udi_number", "values")),
    ),
    Table(
        "safe_harbor", ".csv", safe_harbor,
        lambda header, rows: csv_bytes(header, rows),
        {"safe_harbor_shapes": ("person_ref", "age_top", "zip3", "birth_year", "shifted_admit")},
        {"person_ref": "identifier", "age_top": "measurement", "zip3": "code", "birth_year": "measurement"},
        _csv_reader(),
        (
            _pattern("safe_harbor_shapes", "an age is a number or 90+", "age_top", r"\d{1,2}|90\+"),
            _bad("safe_harbor_shapes", "no age past 89 is written as a number", "age_top",
                 lambda f: _ages_past_89(_t("age_top")(f)), spoil_cell("age_top", "93")),
            *_rare("safe_harbor_shapes", "some age is top-coded 90+", "age_top", r"^90\+$",
                   spoil_every("age_top", lambda v: "89" if v == "90+" else v), crowd("age_top", "90+")),
            _pattern("safe_harbor_shapes", "ZIPs cut to three figures", "zip3", r"\d{3}\*\*"),
            _listed("safe_harbor_shapes", "three-figure ZIPs", "zip3", _levels(ZIP3_MASKED)),
            _bad("safe_harbor_shapes", "birth years from 1920 to 2006", "birth_year",
                 lambda f: _years_outside(_t("birth_year")(f), 1920, 2006, "%Y"), spoil_cell("birth_year", "1890")),
            _bad("safe_harbor_shapes", "shifted dates parse and stay in their century", "shifted_admit",
                 lambda f: _years_outside(_t("shifted_admit")(f), 2100, 2200, "%Y-%m-%d"),
                 spoil_cell("shifted_admit", "2024-03-01")),
        ),
        leaks=(("age_top", "ages over 89"),),
    ),
)

# -- family 7: the time edge kinds ----------------------------------------------

EU_CHANGE_DAYS = (
    datetime.date(2023, 3, 26), datetime.date(2023, 10, 29), datetime.date(2024, 3, 31), datetime.date(2024, 10, 27),
)


def _last_sunday(year: int, month: int) -> datetime.date:
    last = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    return last - datetime.timedelta(days=(last.weekday() + 1) % 7)


def eu_offsets(moment: datetime.datetime) -> "tuple[str, ...]":
    """Every offset a local Central European wall-clock moment may wear: summer time from 02:00 on the last
    Sunday of March (02:00 to 02:59 never happens) to 03:00 on the last Sunday of October (02:00 to 02:59 twice)."""
    hour = datetime.timedelta(hours=1)
    start = datetime.datetime.combine(_last_sunday(moment.year, 3), datetime.time(2))
    end = datetime.datetime.combine(_last_sunday(moment.year, 10), datetime.time(3))
    if start <= moment < start + hour:
        return ()
    if end - hour <= moment < end:
        return ("+02:00", "+01:00")
    return ("+02:00",) if start <= moment < end else ("+01:00",)


def zoned_stamps(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Stamps across the days the clocks change in US Central and in Europe, UTC instants with their Z, and
    Eastern stamps followed by their zone word (EDT, EST)."""
    draw = random.Random(seed)
    header = ["event_ref", "central_ts", "eu_ts", "utc_instant", "zoned_word"]
    rows: "list[list[str]]" = []
    for index in range(n):
        central = _stamp_on_a_change_day(draw)
        if draw.random() < 0.25:
            eu_day = draw.choice(EU_CHANGE_DAYS)
        else:
            eu_day = zoo._day(draw, datetime.date(2023, 1, 1), datetime.date(2024, 12, 31))
        eu = datetime.datetime.combine(eu_day, datetime.time(draw.randint(0, 23), draw.randint(0, 59), draw.randint(0, 59)))
        if not eu_offsets(eu):
            eu = eu.replace(hour=3)
        eastern = _stamp_on_a_change_day(draw)
        rows += [[
            f"EV{600000 + index}",
            central.strftime("%Y-%m-%d %H:%M:%S") + central_offsets(central)[0],
            eu.strftime("%Y-%m-%d %H:%M:%S") + eu_offsets(eu)[0],
            _when(draw).strftime("%Y-%m-%dT%H:%M:%SZ"),
            eastern.strftime("%Y-%m-%d %H:%M:%S") + (" EDT" if zoo.eastern_offset(eastern) == "-04:00" else " EST"),
        ]]
    return header, rows


def _zone_words_in_force(moment: datetime.datetime) -> "tuple[str, ...]":
    return tuple(" EDT" if offset == "-04:00" else " EST" for offset in zoo.eastern_offsets(moment))


def time_edges(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """The time edge kinds: a month and year column of its own (MM/YYYY), durations in three spellings (48:15,
    PT48H15M, '2 days 00:15:00'), epochs in milliseconds and in seconds, an open end 9999-12-31, quarters 'Q1 2024'."""
    draw = random.Random(seed)
    header = [
        "row_ref", "onset_month", "elapsed_hhmm", "elapsed_iso", "elapsed_words", "epoch_ms", "epoch_s", "eff_start",
        "eff_end", "fiscal_quarter",
    ]
    rows: "list[list[str]]" = []
    for index in range(n):
        minutes = draw.randint(5, 120 * 60)
        moment = _when(draw)
        start = moment.date()
        instant = int((moment - datetime.datetime(1970, 1, 1)).total_seconds())
        seconds = draw.randint(0, 6 * 86400)
        rows += [[
            f"TE{700000 + index}",
            f"{draw.randint(1, 12):02d}/{draw.randint(2000, 2024)}",
            f"{minutes // 60}:{minutes % 60:02d}",
            f"PT{minutes // 60}H{minutes % 60}M",
            f"{seconds // 86400} days {seconds % 86400 // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}",
            f"{instant * 1000 + draw.randint(0, 999)}",
            f"{instant}",
            start.isoformat(),
            "9999-12-31" if draw.random() < 0.4 else (start + datetime.timedelta(days=draw.randint(1, 900))).isoformat(),
            f"Q{(moment.month - 1) // 3 + 1} {moment.year}",
        ]]
    return header, rows


def _hours_minutes(series: object) -> "tuple[float, float, float] | None":
    found: "list[float]" = []
    for text in series.dropna().astype(str):  # type: ignore[attr-defined]
        match = re.fullmatch(r"(\d{1,3}):([0-5]\d)", text) or re.fullmatch(r"PT(\d+)H(\d+)M", text)
        if match:
            found += [float(60 * int(match.group(1)) + int(match.group(2)))]
    return _spread(found)


def _hours_doubled(value: str) -> str:
    return re.sub(r"^(PT)?(\d+)", lambda m: f"{m.group(1) or ''}{2 * int(m.group(2)) + 1}", value)


def _durations_bad(series: object) -> int:
    import pandas

    present = series.dropna().astype(str)  # type: ignore[attr-defined]
    return int(pandas.to_timedelta(present, errors="coerce").isna().sum())


def _epochs_outside(series: object, unit: str) -> int:
    import pandas

    numbers = pandas.to_numeric(series.dropna(), errors="coerce")  # type: ignore[attr-defined]
    days = pandas.to_datetime(numbers, unit=unit, errors="coerce")
    return int((days.isna() | (days.dt.year < 2022) | (days.dt.year > 2025)).sum())


def _ends_bad(series: object) -> int:
    present = series.dropna().astype(str)  # type: ignore[attr-defined]
    closed = present[present != "9999-12-31"]
    return zoo._bad_dates(closed, "%Y-%m-%d")


QUARTERS = {f"Q{quarter} {year}" for quarter in range(1, 5) for year in (2023, 2024)}


FAMILY_TIME: "tuple[Table, ...]" = (
    Table(
        "zoned_stamps", ".csv", zoned_stamps,
        lambda header, rows: csv_bytes(header, rows),
        {"dst_zones_and_words": ("event_ref", "central_ts", "eu_ts", "utc_instant", "zoned_word")},
        {"event_ref": "identifier"},
        _csv_reader(),
        (
            _dated("dst_zones_and_words", "Central stamps parse with their offset", "central_ts", "%Y-%m-%d %H:%M:%S%z", utc=True),
            _bad("dst_zones_and_words", "each Central stamp wears an offset in force on its date", "central_ts",
                 lambda f: _wrong_offsets_by(_t("central_ts")(f), central_offsets, "%Y-%m-%d %H:%M:%S", 19),
                 spoil_cell("central_ts", "2024-07-01 10:00:00-06:00")),
            _dated("dst_zones_and_words", "European stamps parse with their offset", "eu_ts", "%Y-%m-%d %H:%M:%S%z", utc=True),
            _bad("dst_zones_and_words", "each European stamp wears an offset in force on its date", "eu_ts",
                 lambda f: _wrong_offsets_by(_t("eu_ts")(f), eu_offsets, "%Y-%m-%d %H:%M:%S", 19),
                 spoil_cell("eu_ts", "2024-07-01 10:00:00+01:00")),
            _dated("dst_zones_and_words", "UTC instants with their Z", "utc_instant", "%Y-%m-%dT%H:%M:%SZ"),
            _pattern("dst_zones_and_words", "Eastern stamps with their zone word", "zoned_word",
                     r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d (EDT|EST)"),
            _bad("dst_zones_and_words", "each zone word is the one in force on its date", "zoned_word",
                 lambda f: _wrong_offsets_by(_t("zoned_word")(f), _zone_words_in_force, "%Y-%m-%d %H:%M:%S", 19),
                 spoil_cell("zoned_word", "2024-07-01 10:00:00 EST")),
        ),
    ),
    Table(
        "time_edges", ".csv", time_edges,
        lambda header, rows: csv_bytes(header, rows),
        {
            "month_year": ("row_ref", "onset_month"),
            "durations": ("elapsed_hhmm", "elapsed_iso", "elapsed_words"),
            "epoch_stamps": ("epoch_ms", "epoch_s"),
            "open_end_dates": ("eff_start", "eff_end"),
            "quarters": ("fiscal_quarter",),
        },
        {
            "row_ref": "identifier", "onset_month": "dates", "elapsed_hhmm": "keep", "elapsed_iso": "keep",
            "elapsed_words": "keep", "epoch_ms": "milliseconds-since-1970", "epoch_s": "seconds-since-1970",
            "eff_end": "keep", "fiscal_quarter": "keep",
        },
        _csv_reader(),
        (
            _dated("month_year", "onset_month parses as %m/%Y", "onset_month", "%m/%Y"),
            _pattern("month_year", "month and year MM/YYYY", "onset_month", r"(0[1-9]|1[0-2])/\d{4}"),
            _pattern("durations", "hours and minutes, past 24 hours too", "elapsed_hhmm", r"\d{1,3}:[0-5]\d"),
            Check("durations", "hours and minutes keep their range", "range",
                  lambda f: _hours_minutes(_t("elapsed_hhmm")(f)), "elapsed_hhmm", spoil_every("elapsed_hhmm", _hours_doubled)),
            *_present("durations", "some duration passes 24 hours", "elapsed_hhmm", r"^(?:2[4-9]|[3-9]\d|\d{3}):",
                      spoil_every("elapsed_hhmm", lambda v: f"{int(v.split(':')[0]) % 24}:{v.split(':')[1]}")),
            _pattern("durations", "ISO 8601 durations PT48H15M", "elapsed_iso", r"PT\d+H\d+M"),
            Check("durations", "ISO durations keep their range", "range",
                  lambda f: _hours_minutes(_t("elapsed_iso")(f)), "elapsed_iso", spoil_every("elapsed_iso", _hours_doubled)),
            _pattern("durations", "durations written 'N days HH:MM:SS'", "elapsed_words", r"\d+ days \d\d:\d\d:\d\d"),
            _bad("durations", "those durations read with pandas.to_timedelta", "elapsed_words",
                 lambda f: _durations_bad(_t("elapsed_words")(f))),
            _bad("epoch_stamps", "epochs in milliseconds read as 2022 to 2025", "epoch_ms",
                 lambda f: _epochs_outside(_t("epoch_ms")(f), "ms"), spoil_cell("epoch_ms", "1704447300")),
            _bad("epoch_stamps", "epochs in seconds read as 2022 to 2025", "epoch_s",
                 lambda f: _epochs_outside(_t("epoch_s")(f), "s"), spoil_cell("epoch_s", "1704447300000")),
            _dated("open_end_dates", "eff_start parses as %Y-%m-%d", "eff_start", "%Y-%m-%d"),
            _bad("open_end_dates", "eff_end parses where it is not the open end", "eff_end", lambda f: _ends_bad(_t("eff_end")(f))),
            *_present("open_end_dates", "some end is the open 9999-12-31", "eff_end", r"^9999-12-31$",
                      spoil_every("eff_end", lambda v: "2099-12-31" if v == "9999-12-31" else v)),
            _pattern("quarters", "quarters written 'Q1 2024'", "fiscal_quarter", r"Q[1-4] \d{4}"),
            _listed("quarters", "the quarters of 2023 and 2024", "fiscal_quarter", QUARTERS),
        ),
    ),
)


# -- the catalogue's widening, in the order the report lists it --------------

WIDE_TABLES: "tuple[Table, ...]" = (
    *FAMILY_ROLES,
    *FAMILY_CLINICAL_A,
    *FAMILY_CLINICAL_B,
    *FAMILY_SYSTEMS,
    *FAMILY_FILES,
    *FAMILY_HIPAA,
    *FAMILY_TIME,
)
WIDE_KINDS: "tuple[str, ...]" = tuple(kind for table in WIDE_TABLES for kind in table.kinds)
WIDE_FILE_KINDS: "tuple[str, ...]" = (
    "tab_delimited", "all_fields_quoted", "pipe_delimited", "utf16_text", "cp1252_smart_quotes", "trailing_delimiter",
)


# The slow driver's shards (K-HZ-03's bound): each at most
# `health_zoo.SHARD_KINDS_AT_MOST` kinds, a table's kinds in one shard,
# balanced on the seconds each table took at 20,000 rows on this lane's
# head under the other lanes' load (planning-notes wave6/E0c,
# probe-20k-rest.log and probe-20k-slow.log): 690, 706, 773, 694 and 693 s,
# each under the bound of 900. Two tables carry most of the time: the
# mangled codes' scientific-notation record numbers (675 s, nearly all of
# it in `generate`'s identifier layouts) and the 302-column export (479 s).
SHARDS: "tuple[tuple[str, ...], ...]" = (
    (
        "patients", "encounters", "diagnoses_procedures", "labs", "prescriptions", "vitals", "flowsheet", "redcap",
        "claims", "notes", "surveys", "wearables", "genomics", "imaging",
    ),
    (
        "perioperative", "problem_list", "tumor_registry", "us_vitals", "sql_server", "microbiology", "immunizations",
        "risk_adjustment", "edge_columns", "titled_report", "registry_extract", "wide_export",
    ),
    (
        "excel_mangled", "unicode_text", "smart_quotes", "sas_export", "trailing_comma", "workbook_1904",
        "apostrophe_codes",
    ),
    (
        "caboodle_export", "cerner_ccl", "reports", "pro_scales", "phi_registry", "time_edges", "zoned_stamps",
        "medication_administration",
    ),
    (
        "bedside_results", "instrument_magnitudes", "critical_care_charting", "pharmacy_fills", "prenatal_visits",
        "well_child", "ecg_reads", "culture_results", "registry_naaccr", "appointments", "remit_835", "adt_events",
        "vcf_calls", "wearable_stream", "coded_forms", "omop_measurement", "pcornet_diagnosis", "i2b2_facts",
        "fhir_observations", "hl7_obx", "long_visits_record_numbers", "numeric_identifiers", "safe_harbor",
    ),
)

# Who owns each failure of these kinds, as `health_zoo.OWNERS` does for
# E0a's: filled from the measured runs at 600 and 20,000 rows (plan
# P4-D431), by the lanes of the zoo plan's sections 1 and 2 and of the
# December plan. A failure no lane covers is 'needs owner', with its
# measured cause stated, for the orchestrator to name one.
_REPEATS = "patients with two rows or more, and three or more, as shares"
IDENTIFIER_FORMS = (
    "a column answered `identifier` gets a twin of made-up record numbers that keeps neither its published layout "
    "nor its constant marks (a float's '.00', a component list's '^^^HOSP^MR', a leading apostrophe, scientific "
    "notation): lane CODES-3 (identifiers with numeric roots, float record numbers, prefixed ids)"
)
HELD_FORMS = (
    "a column held as record numbers (answered, unanswered or held in people) gets a twin that misses its published "
    "forms: the identifier generator's limit, P4-D406's stated limit 4 (lane CODES-1 part C, now CODES-3)"
)
HELD_UNANSWERED = (
    "a column whose identifier or person question is left unanswered is held as record numbers (plan P4-D401): "
    "no value is published and its twin writes made-up record numbers, the accepted price of HIPAA first until "
    "the question is answered (lane HX)"
)
WIDE_OWNERS: "dict[str, tuple[tuple[str, str, str], ...]]" = {
    # E0a's demographics, read for its real values since lane E0c.
    "demographics": (
        ("SH", "LIVE: a five-figure ZIP column answered `code` publishes its real ZIPs as levels and its twin writes "
               "them (Safe Harbor; the orchestrator's LANE SH ADDENDUM 7: an answer of `code` never releases the ZIP "
               "hold)", covers("leak zip5", "leak zip4")),
        ("CODES-3", "LIVE: a birth date column on a table of one row a person publishes real birth dates as its date "
                    "percentiles and tail boundaries, each one person's (Safe Harbor; full birth dates no question "
                    "flags are CODES-1 part C's, now CODES-3's: the orchestrator's LANE HX2 ruling of 2026-10-19, "
                    "item (4))", covers("leak dob_iso")),
    ),
    "labelled_results": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("CODES-2", zoo.WITHHELD, covers(
            "visual acuity in Snellen, CF or HM", "dipstick protein grades", "titers written 1:N",
            "titers are two-fold dilutions from 1:40", "Snellen denominators are chart lines",
            columns=("visual_acuity", "urine_protein", "rubella_titer"))),
        ("CODES-1", "a result's shape ('4+', '20/200', '<1:40') is filled from the whole alphabet", covers(
            "visual acuity in Snellen, CF or HM", "titers written 1:N", columns=("visual_acuity", "rubella_titer"))),
        ("CODES-2", "a meter's HI and LO beside numbers are held-back words (the zoo plan's row 21)", covers(
            "a glucose is a number, HI or LO", "some glucose is past the meter's range",
            "some glucose is past the meter's range, as a share", columns=("glucose",))),
    ),
    "lab_instrument_results": (
        ("PS2", zoo.HELD_VALUES, covers(
            "counts in scientific notation", "the counts read as numbers", "the numbers of wbc_count keep their range",
            "the numbers of hiv_rna keep their range", columns=("wbc_count", "hiv_rna"))),
        ("LM1", "the number part of a result written in scientific notation does not keep its exponent spelling "
                "(the zoo plan's row 52)", covers("counts in scientific notation", columns=("wbc_count",))),
    ),
    "numeric_unrepresentable": (
        (zoo.NEEDS_OWNER, "MEASURED, NO LANE NAMED (for the orchestrator): a column of magnitudes past a double's "
                          "range (role numeric_unrepresentable) publishes no statistic, by design, and its twin writes "
                          "made-up figures outside the source's form ('000067e400' for '8.732E+300'): no exponent "
                          "written d.dddE+3dd and no value past the range; lane LM1's 'written as the source wrote "
                          "them' is the nearest", covers(
            "magnitudes written d.dddE+3dd", "the exponents keep their range",
            "magnitudes past a double's range, as a share", columns=("magnitude",))),
    ),
    "ventilator_settings": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("UN-1a", zoo.UNITS_AS_LABELS, covers(
            "FiO2 with %", "the numbers of fio2 keep their range", "the numbers of o2_delivery keep their range",
            "oxygen is RA, litres a minute or a ventilator", columns=("fio2", "o2_delivery"))),
    ),
    "compact_and_fraction_clocks": (
        ("TR", "a military time 'HHMM' is read as a number, and unanswered held as record numbers (the zoo plan's "
               "row 32; ZR.9's stated limit, its answer `clock-figures`)", covers(
            "military times HHMM", "chart_time parses as %H%M", "some time before ten keeps its leading nought",
            "some time before ten keeps its leading nought, as a share", columns=("chart_time",))),
        ("TR", "a clock with milliseconds ('08:37:21.902') is read as free text (the zoo plan's row 33)", covers(
            "monitor_clock parses as %H:%M:%S.%f", "clocks keep three figures of milliseconds",
            "some clock carries its milliseconds", "some clock carries its milliseconds, as a share",
            columns=("monitor_clock",))),
        ("SS", "the twin writes a clock's fraction as nought ('.000'; the zoo plan's row 33)", covers(
            "some clock carries its milliseconds", "some clock carries its milliseconds, as a share")),
        ("CODES-3", HELD_FORMS, covers("miss chart_time")),
    ),
    "pharmacy_dispensing": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("CODES-2", zoo.WITHHELD, covers("DAW codes", "NDC in its 4-4-2, 5-3-2 and 5-4-1 forms", columns=("daw_code", "ndc"))),
        ("GG", "a count of few values with rare values (days supply 5, 21, 84 below 11 rows) is written as values "
               "no real row holds (the zoo plan's row 54)", covers("days supply are the pharmacy's own", columns=("days_supply",))),
        ("PS2", zoo.HELD_VALUES, covers("days supply are the pharmacy's own", "quantities read as numbers",
                                       "the numbers of quantity keep their range", columns=("days_supply", "quantity"))),
    ),
    "obstetrics": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("UN-2", "a gestational age '37+5' or '39w2d' is a template of two numbers (the zoo plan's row 35)", covers(
            "gestational age written 37+5", "gestational age written 39w2d",
            "gestational ages written 37+5 keep their range in days", "gestational ages written 39w2d keep their range in days",
            columns=("gest_age_plus", "gest_age_wd"))),
        ("CODES-1", "'G2P1' is filled character by character in its form (as GCS 'E4V5M6', the zoo plan's row 26)",
         covers("gravida and para (G2P1)", "para below gravida", columns=("gravida_para",))),
    ),
    "social_history": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("CODES-2", zoo.WITHHELD, covers("smoking status", "alcohol use", columns=("smoking_status", "alcohol_use"))),
        ("PS2", zoo.HELD_VALUES, covers("pack-years read as numbers", "the numbers of pack_years keep their range",
                                       columns=("pack_years",))),
    ),
    "pediatrics": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("UN-2", "an age written with its unit ('14 d', '3 mo', '2 yr') is a template of a number and a unit word",
         covers("ages in days, months or years", "ages read as days keep their range", columns=("age_text",))),
        ("PS2", zoo.HELD_VALUES, covers(
            "ages in days, months or years", "ages read as days keep their range", "weights read as numbers",
            "the numbers of wt_kg keep their range", "the numbers of head_circ keep their range",
            "growth percentiles 1 to 99, <1 or >99", "head circumference in cm",
            columns=("age_text", "wt_kg", "weight_pct", "head_circ"))),
        ("CODES-2", "a growth percentile's '<1' and '>99' are held-back words", covers(
            "some percentile is past the chart (<1 or >99)", "some percentile is past the chart (<1 or >99), as a share")),
    ),
    "cardiology_ecg": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("PS2", zoo.HELD_VALUES, covers(
            "PR intervals in ms", "the numbers of pr_interval keep their range", "the numbers of qrs_duration keep their range",
            "the numbers of qtc_interval keep their range", "axes read as numbers", "the numbers of axis keep their range",
            columns=("pr_interval", "qrs_duration", "qtc_interval", "axis", "vent_rate"))),
        ("CODES-2", zoo.WITHHELD, covers("rhythms", columns=("rhythm",))),
    ),
    "organism_long_tail": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("CODES-2", "an organism name held by fewer than 11 rows on a long tail is written as 'group-N' "
                    "(the zoo plan's row 46, under Z1)", covers(
            "organisms named Genus species, or no growth or mixed flora", "organisms are named ones",
            columns=("organism",))),
    ),
    "report_text_with_headings": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("NOTES", "free text publishes no line, heading, template or length facts: the twin's reports hold no line "
                  "break, no IMPRESSION heading and no template, and their lengths collapse", covers(
            "some report keeps its IMPRESSION heading", "some report keeps its IMPRESSION heading, as a share",
            "some report runs over several lines", "some report runs over several lines, as a share",
            "the share of reports written from the template", "report lengths at the 10th, 50th and 90th percentiles",
            columns=("report_text",))),
    ),
    "long_cell": (
        ("NOTES", "a free-text cell past Excel's 32,767 characters is a rare value the twin writes as a stand-in, "
                  "and no length fact is published", covers(
            "some addendum runs past Excel's 32,767 characters", "addenda past Excel's 32,767 characters, as a share",
            columns=("addendum",))),
    ),
    "naaccr_and_trauma_registry": (
        ("CODES-1", zoo.MADE_UP_CODES, covers(
            "AIS codes with their severity", "AIS severities keep their range", "pathologic T (pT1mi)",
            columns=("ais_code",))),
        ("CODES-2", zoo.WITHHELD, covers("pathologic T categories", "grades", columns=("ais_code", "path_t", "grade"))),
        ("TR", "a NAACCR date known to the month or the year (YYYYMM, YYYY) beside full dates is not read as a "
               "partial date (the zoo plan's row 17)", covers(
            "NAACCR dates YYYYMMDD, YYYYMM or YYYY", "each NAACCR date parses at its own precision",
            "some diagnosis is known to the year only", "some diagnosis is known to the month only",
            "some diagnosis is known to the year only, as a share", "some diagnosis is known to the month only, as a share",
            columns=("date_of_diagnosis",))),
    ),
    "scheduling": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("TR", "a clock column whose evening slots end at '24:00' is not read as clock times and is held",
         covers("slot ends are clocks or 24:00", "some slot ends at 24:00", "some slot ends at 24:00, as a share",
                columns=("slot_end",))),
    ),
    "remittance_835": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("CODES-2", zoo.WITHHELD + " (place of service '03', '04': the zoo plan's row 56)", covers(
            "places of service keep two figures", "adjustment reasons are the payer's", "remark codes",
            columns=("place_of_service", "adjustment", "remark"))),
    ),
    "adt_bed_movements": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("DST", "the twin writes an offset not in force on its date (US Central; the zoo plan's row 30)", covers(
            "in_ts wears a Central offset in force on its date", "out_ts wears a Central offset in force on its date")),
        ("CODES-1", zoo.MADE_UP_CODES + " (a bed 'unit-number-letter' read as free text)", covers(
            "beds named unit-number-letter", columns=("bed",))),
    ),
    "promis_phq9": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("GG", "decimal scores beside -99 and 999 are a few-valued number with a wide gap (the zoo plan's row 39)",
         covers("T-scores to one place, or -99 or 999", "some T-score is the missing code -99",
                "some T-score is the missing code -99, as a share", "the numbers of promis_t keep their range",
                columns=("promis_t",))),
        ("UN-2", "no question asks whether -99 and 999 mean missing", covers("some T-score is the missing code -99")),
        ("RD", "a total computed from its items is not carried (between columns; the zoo plan's row 51)",
         covers("the total is the sum of its nine items (between columns)")),
    ),
    "pro_multi_select": (
        ("LISTS", "a cell listing several picks ('1,3,5', '3,11') is read as one label or as a decimal: its rarer "
                  "combinations are 'group-N' or made-up figures, and click order and the residual are lost "
                  "(the zoo plan's rows 50 and 2.1b)", covers(
            "multi-select picks 1 to 8, each once, in order", "some multi-select holds several picks",
            "some multi-select holds several picks, as a share", "two picks of twelve, sorted",
            "some sorted cell holds two picks", "some sorted cell holds two picks, as a share",
            "two picks of twelve in click order", "some pair is written in click order, the larger first",
            "the residual: a first pick of 1 to 6, then one of 7 to 12",
            columns=("symptoms_multi", "pick_two_sorted", "pick_two_click", "pick_two_residual"))),
    ),
    "vcf_flattened": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("CODES-2", zoo.WITHHELD + " (REF, ALT, CHROM and GT './.': the zoo plan's row 56)", covers(
            "REF alleles are bases", "ALT alleles are bases or <DEL>", "chromosomes", "genotypes with ./.",
            columns=("ref", "alt", "chrom", "gt"))),
        ("CODES-1", "a held-back allele or chromosome is filled in its form from the whole alphabet", covers(
            "REF alleles are bases", "ALT alleles are bases or <DEL>", "chromosomes", columns=("ref", "alt", "chrom"))),
        ("CODES-3", "rsIDs of several lengths, declared identifiers, lose their 'rs' prefix or their widths "
                    "(the zoo plan's row 43)", covers(
            "rsIDs of four to nine figures, or '.'", "some rsID is short (four to six figures)",
            "some rsID is short (four to six figures), as a share", columns=("rsid",))),
        ("PS2", zoo.HELD_VALUES, covers("positions read as numbers", "the numbers of pos keep their range",
                                       "the numbers of qual keep their range", columns=("pos", "qual"))),
        ("CODES-3", HELD_FORMS, covers("miss ref", "miss alt", "miss chrom")),
    ),
    "wearable_offsets_subsecond": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("DST", "an offset written after a space ('-0400') is not one in force on its date (the zoo plan's row 55)",
         covers("the local offset is in force on its date")),
        ("SS", "a stamp's milliseconds are written as nought", covers(
            "some stamp carries its milliseconds", "some stamp carries its milliseconds, as a share")),
        ("CODES-3", HELD_FORMS, covers("miss step_count", "miss heart_rate")),
    ),
    "diagnosis_code_forms": (
        ("CODES-1", "a SNOMED CT id written for a held-back one fails its Verhoeff check (the zoo plan's row 2)", covers(
            "SNOMED CT ids pass their Verhoeff check", "SNOMED CT ids", columns=("snomed_checked",))),
        ("CODES-2", zoo.WITHHELD, covers(
            "ICD-10-CM with its seventh character", "a code and its name in one cell", "each name is its code's own",
            columns=("icd10_seventh", "dx_with_name", "snomed_checked"))),
    ),
    "procedure_and_drg_forms": (
        ("CODES-1", zoo.MADE_UP_CODES + " (APR-DRG '194-3')", covers(
            "APR-DRG with its severity (194-3)", "severities of illness keep their range", columns=("apr_drg",))),
        ("CODES-2", zoo.WITHHELD, covers(
            "procedure codes with their modifier chains", "modifiers are listed ones", columns=("proc_chain", "apr_drg"))),
    ),
    "icd10_long_tail": (
        ("CODES-2", "a realistic ICD-10-CM long tail (600 codes) is mostly held back: its twin writes codes the real "
                    "never writes (the zoo plan's row 46, under Z1)", covers(
            "a long tail of ICD-10-CM codes", columns=("icd10_tail",))),
    ),
    "omop_cdm": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("KV", "a long table's unit is read by its concept; the twin carries no relation between the two columns "
               "(the zoo plan's row 47)", covers("each concept's unit is its own (read by concept)")),
        ("CODES-2", zoo.WITHHELD, covers("answer concepts", columns=("value_as_concept_id",))),
    ),
    "pcornet_cdm": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("CODES-1", "mixed ICD-10, ICD-9 and SNOMED codes answered `code` are written as number-class stand-ins that "
                    "pay neither their forms nor their widths (the zoo plan's row 44, A3)", covers(
            "DX is ICD-10-CM, ICD-9-CM or SNOMED CT", "RAW_DX as the source wrote it, no point", "miss DX", "miss RAW_DX",
            columns=("DX", "RAW_DX"))),
        ("KV", "a code's form follows its DX_TYPE: between columns (the zoo plan's row 48)",
         covers("DX is in the system its DX_TYPE names (read by type)")),
        ("CODES-2", zoo.WITHHELD, covers("DX_TYPE with NI", "DX_SOURCE with NI, UN and OT", "PDX with NI",
                                        columns=("DX_TYPE", "DX_SOURCE", "PDX"))),
    ),
    "i2b2_eav": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("CODES-1", "a vocabulary prefix ('ICD10CM:', 'DEM|GENDER:') is rewritten by the full-alphabet fill "
                    "(the zoo plan's row 49)", covers(
            "concepts with their vocabulary prefix", "the vocabulary prefixes are i2b2's",
            "some fact is a demographic (DEM|GENDER:)", "some fact is a demographic (DEM|GENDER:), as a share",
            columns=("concept_cd",))),
        ("PS2", zoo.HELD_VALUES, covers("numeric values read as numbers", "the numbers of nval_num keep their range",
                                       columns=("nval_num",))),
    ),
    "fhir_flattened": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("DST", "the twin writes an offset not in force on its date (US Eastern, ISO 8601 instants)", covers(
            "each instant wears an offset in force on its date")),
        ("CODES-2", zoo.WITHHELD + " (the CDC's category codes, the zoo plan's row 25)", covers(
            "CDC category codes", "category codings under the CDC code system", "units", "observation status",
            columns=("omb_category", "value_quantity_unit", "status"))),
    ),
    "hl7v2_flattened": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("DST", "the twin writes an offset not in force on its date (HL7 'YYYYMMDDHHMMSS-0400'; the zoo plan's row 30)",
         covers("MSH-7 wears an offset in force on its date")),
        ("CODES-3", IDENTIFIER_FORMS, covers("PID-3 as id^^^HOSP^MR", columns=("pid_3",))),
        ("LISTS", "an HL7 '^' component list is read as one label: its rarer combinations are 'group-N'", covers(
            "OBX-3 is code^text^LN, the text its code's own", "OBX-6 units as unit^^UCUM", columns=("obx_3", "obx_6"))),
    ),
    "epic_caboodle": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("CODES-3", IDENTIFIER_FORMS + " (a durable key of six figures beside its -1 and -2 members)", covers(
            "durable keys of six figures, or -1 and -2", "some row's durable key is the -1 member",
            "some row's durable key is the -1 member, as a share", "miss PatientDurableKey",
            columns=("PatientDurableKey",))),
        ("TR", "a Caboodle DateKey (YYYYMMDD beside -1 and -2) left unanswered is read as a number and held "
               "(the zoo plan's row 57, item (e))", covers(
            "DateKeys are dates YYYYMMDD, or -1 and -2", "some DateKey is the -1 member",
            "some DateKey is the -1 member, as a share", "miss DateKey", columns=("DateKey",))),
        ("CODES-2", zoo.WITHHELD + " ('*Unspecified', '*Unknown', '*Not Applicable': the zoo plan's row 56)", covers(
            "flags with the *Unspecified members", "a result is a number or a word", "the results read past their words",
            columns=("AbnormalFlag", "ResultValue"))),
    ),
    "cerner_ccl": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("CODES-3", IDENTIFIER_FORMS + " (the zoo plan's row 42)", covers(
            "encounter numbers written 31000000.00", "person numbers written 21000000.00", "miss ENCNTR_ID",
            "miss PERSON_ID", columns=("ENCNTR_ID", "PERSON_ID"))),
        ("CODES-2", zoo.WITHHELD + " ('See Comment')", covers(
            "a result is a number or a word", "the results read past their words", "event codes written as floats",
            columns=("RESULT_VAL", "EVENT_CD"))),
    ),
    "excel_mangled_codes": (
        ("CODES-3", IDENTIFIER_FORMS, covers(
            "NPIs shown d.ddddDE+09", "account numbers shown d.dddddE+11", "miss npi_shown", "miss account_shown",
            columns=("npi_shown", "account_shown"))),
        ("SH", "LIVE: a ZIP column answered `code` publishes its real ZIPs as levels and its twin writes them "
               "(Safe Harbor; the orchestrator's LANE SH ADDENDUM 7: an answer of `code` never releases the ZIP hold)",
         covers("leak zip_lost")),
    ),
    "leading_apostrophe": (
        ("CODES-3", IDENTIFIER_FORMS, covers("record references keep their apostrophe", columns=("record_ref",))),
    ),
    "phi_columns": (
        ("CODES-3", IDENTIFIER_FORMS + " (telephone numbers, e-mail addresses, social security numbers, MR numbers)",
         covers("telephone numbers (NNN) 555-NNNN", "e-mail addresses", "social security numbers",
                "medical record numbers", columns=("phone", "email", "ssn", "med_rec_no"))),
        ("CODES-2", "names and street addresses answered `identifier` are written as made-up record numbers, not "
                    "names or addresses (the allowlist's limit, CODES-2)", covers(
            "names, first and last", "street addresses", columns=("patient_name", "street_address"))),
        ("CODES-3", "LIVE: a birth date column no question flags publishes real birth dates as its date percentiles "
                    "and tail boundaries, each one person's (Safe Harbor; full birth dates no question flags are "
                    "CODES-1 part C's, now CODES-3's: the orchestrator's LANE HX2 ruling of 2026-10-19, item (4))",
         covers("leak birth_date")),
    ),
    "undeclared_record_number_long": (
        ("MG", zoo.CENSUS_IN_PEOPLE, covers(_REPEATS)),
        ("HX", HELD_UNANSWERED, covers("record numbers A and seven figures", columns=("med_rec_no",))),
    ),
    "numeric_keys_unanswered": (
        ("HX", HELD_UNANSWERED, covers(
            "durable keys of six figures, or -1 and -2", "ZIPs of five figures", "UDIs of fourteen figures",
            columns=("durable_key", "zip_number", "udi_number"))),
        ("CODES-3", HELD_FORMS, covers("miss durable_key", "miss zip_number", "miss udi_number")),
    ),
    "safe_harbor_shapes": (
        ("LM1", "the tail rule extends a bounded scale past its withheld end: a birth year written past the real's "
                "range (the zoo plan's rows 13 and 53)", covers(
            "birth years from 1920 to 2006", "shifted dates parse and stay in their century", "no age past 89 is written as a number")),
        ("SH", "LIVE: an age past the top-code 90 printed or written as a number (Safe Harbor; lane SH, P4-D427)",
         covers("leak age_top")),
    ),
    "dst_zones_and_words": (
        ("DST", "the twin writes an offset not in force on its date (US Central and European rules; the zoo plan's row 30)",
         covers("each Central stamp wears an offset in force on its date",
                "each European stamp wears an offset in force on its date")),
        ("TR", "a stamp followed by a zone word ('EDT', 'EST') is not read: only UTC and GMT are (the zoo plan's row 31)",
         covers("Eastern stamps with their zone word", "each zone word is the one in force on its date", columns=("zoned_word",))),
    ),
    "month_year": (
        ("TR", "a month and year column of its own ('03/2019') has no reading (the zoo plan's row 17)", covers(
            "month and year MM/YYYY", "onset_month parses as %m/%Y", columns=("onset_month",))),
    ),
    "durations": (
        ("UN-2", "durations ('48:15', 'PT48H15M', '2 days 00:15:00') have no reading: templates in mixed radix "
                 "(the zoo plan's row 34)", covers(
            "hours and minutes, past 24 hours too", "hours and minutes keep their range", "some duration passes 24 hours",
            "some duration passes 24 hours, as a share", "ISO 8601 durations PT48H15M", "ISO durations keep their range",
            "durations written 'N days HH:MM:SS'", "those durations read with pandas.to_timedelta",
            columns=("elapsed_hhmm", "elapsed_iso", "elapsed_words"))),
    ),
}

_UNUSED = (JUNK, _bad_pattern, _i, _r, _zipf, covers)
