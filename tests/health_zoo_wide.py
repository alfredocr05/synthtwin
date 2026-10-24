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

import datetime
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

# -- the catalogue's widening, in the order the report lists it --------------

WIDE_TABLES: "tuple[Table, ...]" = (
    *FAMILY_ROLES,
)
WIDE_KINDS: "tuple[str, ...]" = tuple(kind for table in WIDE_TABLES for kind in table.kinds)
WIDE_FILE_KINDS: "tuple[str, ...]" = (
    "tab_delimited",
)


def _packed(tables: "tuple[Table, ...]", most: int) -> "tuple[tuple[str, ...], ...]":
    """The tables in catalogue order, packed into shards of at most `most` kinds, a table's kinds together."""
    shards: "list[tuple[str, ...]]" = []
    shard: "list[str]" = []
    held = 0
    for table in tables:
        if shard and held + len(table.kinds) > most:
            shards += [tuple(shard)]
            shard, held = [], 0
        shard += [table.name]
        held += len(table.kinds)
    return tuple(shards + [tuple(shard)])


# The slow driver's shards (K-HZ-03's bound): each at most
# `health_zoo.SHARD_KINDS_AT_MOST` kinds, a table's kinds in one shard.
SHARDS: "tuple[tuple[str, ...], ...]" = _packed(zoo.TABLES + WIDE_TABLES, zoo.SHARD_KINDS_AT_MOST)

# Who owns each failure of these kinds, as `health_zoo.OWNERS` does for
# E0a's: filled from the measured runs at 600 and 20,000 rows.
WIDE_OWNERS: "dict[str, tuple[tuple[str, str, str], ...]]" = {}

_UNUSED = (JUNK, _bad_pattern, _i, _r, _zipf, covers)
