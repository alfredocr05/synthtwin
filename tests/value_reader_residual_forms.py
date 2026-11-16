"""Lane CZ-G's invented tables (plan P4-D493, K-HZ-41): the value readers' residuals at the owner's table floor.

Each table is an INVENTED look-alike with generic names, 20,000 rows and
1,000 people, 20 rows a person (a patient table) or the same rows counted
by a case number (a case table, `_cases`), its forms written from a
grammar written here:

- `adult_bands`: each adult's age (25 to 104) in age groups under neutral
  names: `25-44 ... 90-94, 95+` (`grp_k`), `16-24 ... 95-99, 100+` with
  nobody aged 16 to 24 (`grp_m`), three closed bands `18-64, 65-89,
  90-94, 95+` (`grp_n`), an older cohort `65-79, 80-89, 90-94, 95-99,
  100+` (`grp_old`), five-year groups written with the soft hyphen for
  the dash (`grp_shy`), and the strict bound `25-<45 ... 90-<95, 95+`
  written with a hyphen (`grp_lt`) and with `to` (`grp_lt_to`);
- `measure_bands_cases`: banded measures that are no ages, truthfully
  answered `no`: amounts `5-9 ... 100-199, 200+`, percentile classes,
  rate classes, saturation classes, days of stay, weights;
- `lettered_homes_cases`: each person's home on 20 rows written with its
  hemisphere letters as their own words: `home <lat> N <lon> W`, with
  degree marks, and with the letters first;
- `remark_ages_cases` and `remark_ages`: remarks holding an age past 89
  (`94 yo F, fall at home`, `aged 97, lives alone`), beside remarks holding
  an age under 90 and remarks holding scores, amounts with a unit and room
  numbers (the controls), one row a case and beside the patient column; a
  remark of an age of exactly 90, the top code's own form, is placed with
  no needle and never counted (batch 4t's fix round, item 9);
- `split_records`: one record number a person written with two spaces
  between its two groups of figures, a dash joining the label, in
  brackets, five figures in two groups, and two families half each;
- `phone_marks_cases`: telephone numbers whose groups are parted by
  ` . ` or `_`, and runs of figures with a zero-width character inside;
- `lang_bands`: the same age groups written in Spanish, Portuguese,
  French, German and Italian;
- `short_names`: a family name, a given name and four figures joined by
  commas, one a person (a price-first item).

THE FORMS each cell holds are kept in `value_readers_forms.META`, so
`value_readers_forms.measure` counts each form's real values in what the
commands write; `registered` installs these kinds into that module's
tables for the length of a `with` block and takes them out after it.
"""

from __future__ import annotations

import contextlib
import random

import health_zoo as zoo
import safe_harbor_forms as forms
import value_readers_forms as readers

SEED = 20261112
ROWS_A_PERSON = readers.ROWS_A_PERSON

KIND_ADULT_BANDS = "adult_bands"
KIND_MEASURE_BANDS = "measure_bands_cases"
KIND_LETTERED_HOMES = "lettered_homes_cases"
KIND_REMARK_AGES = "remark_ages"
KIND_REMARK_AGES_CASES = "remark_ages_cases"
KIND_SPLIT_RECORDS = "split_records"
KIND_SPLIT_RECORDS_CASES = "split_records_cases"
KIND_PHONE_MARKS = "phone_marks_cases"
KIND_LANG_BANDS = "lang_bands"
KIND_SHORT_NAMES = "short_names"

FORM_OVER_89 = readers.FORM_OVER_89
FORM_HOME = "home_lettered"
FORM_REMARK_AGE = "remark_age"
FORM_RECORD = "record_split"
FORM_PHONE = "phone_marked"
FORM_RUN = "run_marked"
FORM_SHORT = "name_short_number"


def _ages(draw: random.Random, count: int) -> "list[int]":
    """Each adult's age, 25 to 104: 55 % 25 to 89, 20 % 90 to 94, 15 % 95 to 99, 10 % 100 to 104."""
    found: "list[int]" = []
    for _person in range(count):
        roll = draw.random()
        low, high = (25, 89) if roll < 0.55 else (90, 94) if roll < 0.75 else (95, 99) if roll < 0.90 else (100, 104)
        found += [draw.randint(low, high)]
    return found


def _people(n: int, people: "int | None") -> int:
    return people if people else max(n // ROWS_A_PERSON, readers.SMOKE_PEOPLE)


def _grouped(age: int, cuts: "tuple[tuple[int, int], ...]", closed: str, top: str) -> str:
    """An age written as the group of ``cuts`` it falls in (``closed`` a format of the first and last age), or ``top`` from the age after the last cut."""
    for low, high in cuts:
        if low <= age <= high:
            return closed.format(low, high)
    return top


# The adult groups (`adult_bands`): each scheme's closed bands and its open top.
ADULT_SCHEMES = {
    "grp_k": (((25, 44), (45, 64), (65, 89), (90, 94)), "{}-{}", "95+"),
    "grp_m": (((16, 24), (25, 44), (45, 64), (65, 89), (90, 94), (95, 99)), "{}-{}", "100+"),
    "grp_n": (((18, 64), (65, 89), (90, 94)), "{}-{}", "95+"),
    "grp_old": (((65, 79), (80, 89), (90, 94), (95, 99)), "{}-{}", "100+"),
    # ...and (LANE CZ-G RULINGS 3 (1), X1) five-year groups written with the
    # soft hyphen U+00AD for the dash.
    "grp_shy": (tuple((low, low + 4) for low in range(20, 100, 5)), "{}\u00ad{}", "100+"),
}
# ...and the strict bound: each band's last age written as the next band's
# first after `<` (`25-<45` holds 25 to 44).
STRICT_SCHEMES = {
    "grp_lt": "{}-<{}",
    "grp_lt_to": "{} to <{}",
}
_STRICT_CUTS = ((25, 44), (45, 64), (65, 89), (90, 94))
# ...and `grp_k`'s groups with one person in twelve written as a stray cell
# holding figures but no age (`grp_ks`): a share the reach's numbers do not
# set aside (one in twenty at most), so only the band reader reads it.
STRAY_CELLS = ("see note 3", "code 00", "18-24 (est)")
STRAY_EVERY = 12


def adult_bands(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Each adult's age in seven schemes of groups under neutral names (`ADULT_SCHEMES`, `STRICT_SCHEMES`, and `grp_k` with stray cells, `grp_ks`), beside the patient column; a cell naming an age past 89 is noted `FORM_OVER_89`."""
    draw = random.Random(seed)
    count = _people(n, people)
    ages = _ages(draw, count)
    order = forms._person_rows(n, draw, count)
    meta: dict = {}
    columns = (*ADULT_SCHEMES, *STRICT_SCHEMES, "grp_ks")
    header = ["patient_ref", *columns, "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    for person in order:
        age = ages[person]
        cells = [_grouped(age, cuts, closed, top) for cuts, closed, top in ADULT_SCHEMES.values()]
        for written in STRICT_SCHEMES.values():
            cells += [_strict(age, written)]
        stray = person % STRAY_EVERY == 0
        cells += [STRAY_CELLS[person % len(STRAY_CELLS)] if stray else cells[0]]
        for column, cell in zip(columns, cells):
            past = age >= 90 and not (column == "grp_ks" and stray)
            readers._note(meta, column, cell, FORM_OVER_89 if past else "none", (cell,) if past else ())
        rows += [[forms.patient_ref(person)] + cells + forms._ordinary(draw)]
    readers.META[(KIND_ADULT_BANDS, n, seed, people)] = meta
    return header, rows


def _strict(age: int, written: str) -> str:
    """An age written as its group with a strict bound (``written`` a format of the first age and the next group's first: `25-<45` holds 25 to 44), `95+` from 95."""
    for low, high in _STRICT_CUTS:
        if low <= age <= high:
            return written.format(low, high + 1)
    return "95+"


# The banded measures (`measure_bands_cases`): each column's bands, every one
# drawn with its weight; none is an age, and the truthful answer to an age
# question is `no`.
MEASURE_SCHEMES = {
    "amount_band": (("5-9", 3), ("10-24", 4), ("25-49", 4), ("50-99", 3), ("100-199", 2), ("200+", 1)),
    "pctl_band": (("<5", 1), ("5-84", 8), ("85-94", 2), (">=95", 1)),
    "rate_band": (("<60", 2), ("60-89", 6), ("90-100", 2), (">100", 1)),
    "sat_band": (("<85", 1), ("85-89", 2), ("90-94", 4), ("95-100", 6)),
    "stay_band": (("0-1", 4), ("2-3", 4), ("4-7", 3), ("8-14", 2), ("15-30", 1), ("31-90", 1), ("91+", 1)),
    "wt_band": (("45-64", 3), ("65-84", 5), ("85-104", 3), ("105+", 1)),
}


def _weighted(draw: random.Random, bands: "tuple[tuple[str, int], ...]") -> str:
    total = sum(weight for _band, weight in bands)
    roll = draw.randrange(total)
    for band, weight in bands:
        if roll < weight:
            return band
        roll -= weight
    return bands[-1][0]


def _with_cases(kind: str, n: int, seed: int, people: "int | None", header: "list[str]", rows: "list[list[str]]",
                persons: "list[str]", meta: dict) -> "tuple[list[str], list[list[str]]]":
    """A case table: the case's own number first, each row's person kept in the forms' notes (`__persons__`)."""
    meta["__persons__"] = {f"{row}": (persons[row], ()) for row in range(len(rows))}
    readers.META[(kind, n, seed, people)] = meta
    return ["case_ref", *header], [[readers._case(row), *rows[row]] for row in range(len(rows))]


def measure_bands(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Banded measures that are no ages (`MEASURE_SCHEMES`), one row a case; each band noted as a price cell."""
    draw = random.Random(seed)
    count = _people(n, people)
    order = forms._person_rows(n, draw, count)
    meta: dict = {}
    header = [*MEASURE_SCHEMES, "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    persons: "list[str]" = []
    for person in order:
        cells = [_weighted(draw, bands) for bands in MEASURE_SCHEMES.values()]
        for column, cell in zip(MEASURE_SCHEMES, cells):
            readers._note(meta, column, cell, "none", ())
        rows += [cells + forms._ordinary(draw)]
        persons += [forms.patient_ref(person)]
    return _with_cases(KIND_MEASURE_BANDS, n, seed, people, header, rows, persons, meta)


def _decimals(draw: random.Random, low: float, high: float, places: int) -> str:
    return f"{draw.uniform(low, high):.{places}f}"


# The lettered homes: a latitude and a longitude, each with its hemisphere's
# letter as its own word (`41.78396 N 86.5934 W`).
HOME_FORMS = {
    "home_hw": "home {lat} N {lon} W",
    "home_hwd": "{lat}° N {lon}° W",
    "home_pre": "N {lat} W {lon}",
}


def lettered_homes(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Each person's own home on each of their rows in three lettered forms (`HOME_FORMS`), one row a case."""
    draw = random.Random(seed)
    count = _people(n, people)
    homes = [(_decimals(draw, 25.0, 48.9, draw.choice((4, 5))), _decimals(draw, 70.0, 122.9, draw.choice((4, 5))))
             for _person in range(count)]
    order = forms._person_rows(n, draw, count)
    meta: dict = {}
    header = [*HOME_FORMS, "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    persons: "list[str]" = []
    for person in order:
        lat, lon = homes[person]
        cells = [written.format(lat=lat, lon=lon) for written in HOME_FORMS.values()]
        for column, cell in zip(HOME_FORMS, cells):
            readers._note(meta, column, cell, FORM_HOME, (lat, lon))
        rows += [cells + forms._ordinary(draw)]
        persons += [forms.patient_ref(person)]
    return _with_cases(KIND_LETTERED_HOMES, n, seed, people, header, rows, persons, meta)


# The remarks holding an age (`remark_ages`): each written with an age past
# 89 (`REMARK_AGE_TEMPLATES`); beside them remarks with an age under 90 and
# the controls, which hold no age (`REMARK_CONTROLS`).
REMARK_AGE_TEMPLATES = (
    "{a} yo F, fall at home", "{a} yo M with cough", "{a} y/o F seen for rash", "aged {a}, lives alone",
    "pt is a {a} year old male", "{a}-year-old with chest pain", "{a} years old, here with daughter",
    "Age: {a}, ambulates with walker", "{a}yo F dizziness", "{a} y.o. M, follow up",
)
REMARK_CONTROLS = (
    "pain score {s} of 10, {m} mg given", "room {r} cleaned", "bed {r} ready", "glucose {g} mg/dL at noon",
    "weight {w} kg today", "BP {g}/60 sitting",
)
PLAIN_REMARKS = ("doing well", "seen in clinic", "no complaints today", "follow up in two weeks", "labs pending")


def _remarks(kind: str, n: int, seed: int, people: "int | None", shared: int, cases: bool) -> "tuple[list[str], list[list[str]]]":
    """Remarks holding an age past 89 (``shared`` of them, each on many rows or written for 30 people), remarks holding an age under 90 and the controls (price columns), plain remarks on the other rows."""
    draw = random.Random(seed)
    count = _people(n, people)
    order = forms._person_rows(n, draw, count)
    old = []
    # ...and each one's form under the top code, its age written 90 (`coded`):
    # a remark whose text IS that form -- an age of exactly 90 -- is the
    # category Safe Harbor allows, no exposure, so it is placed with no
    # needle and never counted (batch 4t's fix round, item 9; the
    # orchestrator's LANE I4t RULINGS 1, item 9: `90 yo F, fall at home` beside
    # its top-coded twins was 2,760 and 4,160 twin cells a mode).
    coded = []
    for place in range(shared):
        old += [REMARK_AGE_TEMPLATES[place % len(REMARK_AGE_TEMPLATES)].format(a=90 + (place * 7) % 16)]
        coded += [REMARK_AGE_TEMPLATES[place % len(REMARK_AGE_TEMPLATES)].format(a=90)]
    young = [REMARK_AGE_TEMPLATES[place % len(REMARK_AGE_TEMPLATES)].format(a=30 + (place * 11) % 59)
             for place in range(shared)]
    controls = [REMARK_CONTROLS[place % len(REMARK_CONTROLS)].format(
        s=1 + place % 9, m=90 + (place * 5) % 30, r=90 + (place * 3) % 30, g=90 + (place * 7) % 35,
        w=90 + (place * 2) % 30) for place in range(shared)]
    # ...each remark of an age past 89 is written for its own people: one person
    # in ``count // (3 * shared)`` (the patient table: about 30 people each).
    holder = [draw.randrange(shared) if draw.random() < 0.35 else -1 for _person in range(count)]
    meta: dict = {}
    header = ["remark_age", "remark_young", "remark_ctrl", "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    persons: "list[str]" = []
    for person in order:
        mine = holder[person]
        age_cell = old[mine] if mine >= 0 else draw.choice(PLAIN_REMARKS)
        young_cell = young[mine] if mine >= 0 else draw.choice(PLAIN_REMARKS)
        control_cell = controls[mine] if mine >= 0 else draw.choice(PLAIN_REMARKS)
        readers._note(meta, "remark_age", age_cell, FORM_REMARK_AGE if mine >= 0 else "plain",
                      (age_cell,) if mine >= 0 and age_cell != coded[mine] else ())
        readers._note(meta, "remark_young", young_cell, "plain", ())
        readers._note(meta, "remark_ctrl", control_cell, "plain", ())
        rows += [[age_cell, young_cell, control_cell] + forms._ordinary(draw)]
        persons += [forms.patient_ref(person)]
    if cases:
        return _with_cases(kind, n, seed, people, header, rows, persons, meta)
    readers.META[(kind, n, seed, people)] = meta
    return ["patient_ref", *header], [[persons[row], *rows[row]] for row in range(len(rows))]


def remark_ages(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Twelve remarks of an age past 89 beside the patient column, each written for about 30 people (`_remarks`)."""
    return _remarks(KIND_REMARK_AGES, n, seed, people, 12, False)


def remark_ages_cases(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Forty remarks of an age past 89, one row a case (`_remarks`)."""
    return _remarks(KIND_REMARK_AGES_CASES, n, seed, people, 40, True)


# The record numbers no reader knew (`split_records`), each a format of the
# person's own figures: two spaces between the two groups, a dash joining the
# label, the cell in brackets. (Five figures in two groups and two families
# half each stay stated limits of plan P4-D493, measured one column a table:
# beside these columns, held, a neighbour of their shape is held with them.)
RECORD_FORMS = {
    "rec_two": "MR{a}  {b}",
    "rec_dash": "MR-{a} {b}",
    "rec_brk": "(MR{a} {b})",
}


def split_records(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """One record number a person in three split forms (`RECORD_FORMS`), beside the patient column."""
    return _split_records(KIND_SPLIT_RECORDS, n, seed, people, False)


def split_records_cases(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """`split_records` one row a case, each person's record number on each of their rows (the table counted in rows)."""
    return _split_records(KIND_SPLIT_RECORDS_CASES, n, seed, people, True)


def _split_records(kind: str, n: int, seed: int, people: "int | None", cases: bool) -> "tuple[list[str], list[list[str]]]":
    draw = random.Random(seed)
    count = _people(n, people)
    numbers = [f"{1000000 + draw.randrange(9000000)}" for _person in range(count)]
    order = forms._person_rows(n, draw, count)
    meta: dict = {}
    header = [*RECORD_FORMS, "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    persons: "list[str]" = []
    for person in order:
        seven = numbers[person]
        cells = [written.format(a=seven[:3], b=seven[3:]) for written in RECORD_FORMS.values()]
        for column, cell in zip(RECORD_FORMS, cells):
            readers._note(meta, column, cell, FORM_RECORD, (cell,))
        rows += [cells + forms._ordinary(draw)]
        persons += [forms.patient_ref(person)]
    if cases:
        return _with_cases(kind, n, seed, people, header, rows, persons, meta)
    readers.META[(kind, n, seed, people)] = meta
    return ["patient_ref", *header], [[persons[row], *rows[row]] for row in range(len(rows))]


# Telephone numbers and runs of figures written with marks no reader knew,
# each inside a remark that many rows share (forty of them), beside plain
# remarks: the shape the identifier words read, a level the floor's rows hold.
PHONE_FORMS = {
    "phone_dot": "call {a} . {b} . {c} re results",
    "phone_under": "cb {a}_{b}_{c}",
    "run_zw": "ref {r1}\u200b{r2} on file",
}
PHONE_SHARED = 40


def phone_marks(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Forty remarks of each form (`PHONE_FORMS`), each written for its own people (one person in four holds one), plain remarks on the other rows, one row a case."""
    draw = random.Random(seed)
    count = _people(n, people)
    shared = []
    for _place in range(PHONE_SHARED):
        area = f"{draw.randint(2, 9)}{draw.randint(0, 9)}{draw.randint(0, 9)}"
        exchange = f"{draw.randint(2, 9)}{draw.randint(0, 9)}{draw.randint(0, 9)}"
        line = f"{draw.randrange(10000):04d}"
        run = f"{10000000 + draw.randrange(90000000)}"
        shared += [[written.format(a=area, b=exchange, c=line, r1=run[:4], r2=run[4:]) for written in PHONE_FORMS.values()]]
    holder = [draw.randrange(PHONE_SHARED) if draw.random() < 0.25 else -1 for _person in range(count)]
    order = forms._person_rows(n, draw, count)
    meta: dict = {}
    header = [*PHONE_FORMS, "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    persons: "list[str]" = []
    for person in order:
        mine = holder[person]
        cells = shared[mine] if mine >= 0 else [draw.choice(PLAIN_REMARKS) for _column in PHONE_FORMS]
        for column, cell in zip(PHONE_FORMS, cells):
            form = (FORM_RUN if column == "run_zw" else FORM_PHONE) if mine >= 0 else "plain"
            readers._note(meta, column, cell, form, (cell,) if mine >= 0 else ())
        rows += [cells + forms._ordinary(draw)]
        persons += [forms.patient_ref(person)]
    return _with_cases(KIND_PHONE_MARKS, n, seed, people, header, rows, persons, meta)


# The age groups in five other languages (`lang_bands`): each scheme's closed
# band, its open top, and the scheme's cuts.
LANG_SCHEMES = {
    "grp_es": ("{}-{} años", "95 años y más"),
    "grp_pt": ("{}-{} anos", "95 anos ou mais"),
    "grp_fr": ("{} à {} ans", "95 ans et plus"),
    "grp_de": ("{}-{} Jahre", "95 Jahre und älter"),
    "grp_it": ("{}-{} anni", "95 anni e oltre"),
}
_LANG_CUTS = ((25, 44), (45, 64), (65, 89), (90, 94))


def lang_bands(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Each adult's age group written in five languages (`LANG_SCHEMES`), beside the patient column."""
    draw = random.Random(seed)
    count = _people(n, people)
    ages = _ages(draw, count)
    order = forms._person_rows(n, draw, count)
    meta: dict = {}
    header = ["patient_ref", *LANG_SCHEMES, "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    for person in order:
        age = ages[person]
        cells = [_grouped(age, _LANG_CUTS, closed, top) for closed, top in LANG_SCHEMES.values()]
        for column, cell in zip(LANG_SCHEMES, cells):
            readers._note(meta, column, cell, FORM_OVER_89 if age >= 90 else "none", (cell,) if age >= 90 else ())
        rows += [[forms.patient_ref(person)] + cells + forms._ordinary(draw)]
    readers.META[(KIND_LANG_BANDS, n, seed, people)] = meta
    return header, rows


def short_names(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """A family name, a given name and four figures joined by commas (`Tarn,Ul,1234`), one a person, beside the patient column."""
    draw = random.Random(seed)
    count = _people(n, people)
    owned = [f"{readers.made_up_word(draw, 2)},{readers.made_up_word(draw, 1)},{1000 + draw.randrange(9000)}"
             for _person in range(count)]
    order = forms._person_rows(n, draw, count)
    meta: dict = {}
    header = ["patient_ref", "name_ref", "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    for person in order:
        cell = owned[person]
        family, given, _figures = cell.split(",")
        readers._note(meta, "name_ref", cell, FORM_SHORT, (cell, family, given))
        rows += [[forms.patient_ref(person), cell] + forms._ordinary(draw)]
    readers.META[(KIND_SHORT_NAMES, n, seed, people)] = meta
    return header, rows


MAKERS = {
    KIND_ADULT_BANDS: adult_bands,
    KIND_MEASURE_BANDS: measure_bands,
    KIND_LETTERED_HOMES: lettered_homes,
    KIND_REMARK_AGES: remark_ages,
    KIND_REMARK_AGES_CASES: remark_ages_cases,
    KIND_SPLIT_RECORDS: split_records,
    KIND_SPLIT_RECORDS_CASES: split_records_cases,
    KIND_PHONE_MARKS: phone_marks,
    KIND_LANG_BANDS: lang_bands,
    KIND_SHORT_NAMES: short_names,
}
# Each kind's columns the readers must hold, and those beside them that hold
# no identifier and must stay published (the price).
HELD = {
    KIND_ADULT_BANDS: (*ADULT_SCHEMES, *STRICT_SCHEMES, "grp_ks"),
    KIND_MEASURE_BANDS: (),
    KIND_LETTERED_HOMES: tuple(HOME_FORMS),
    KIND_REMARK_AGES: ("remark_age",),
    KIND_REMARK_AGES_CASES: ("remark_age",),
    KIND_SPLIT_RECORDS: tuple(RECORD_FORMS),
    KIND_SPLIT_RECORDS_CASES: tuple(RECORD_FORMS),
    KIND_PHONE_MARKS: tuple(PHONE_FORMS),
    KIND_LANG_BANDS: tuple(LANG_SCHEMES),
    KIND_SHORT_NAMES: ("name_ref",),
}
PRICE = {
    KIND_MEASURE_BANDS: tuple(MEASURE_SCHEMES),
    KIND_REMARK_AGES: ("remark_young", "remark_ctrl"),
    KIND_REMARK_AGES_CASES: ("remark_young", "remark_ctrl"),
}
# The truthful answer to a reading question (`value_readers_forms.KNOWS`): a
# column of one record number a person is an identifier; a remark (one that
# holds a telephone number or a reference too: its Safe Harbor question is
# answered `yes`), a band, a home point or a measure is kept as it was read.
KNOWN = {column: "identifier" for column in (*RECORD_FORMS, "name_ref")}
# The truthful answer to a price column's Safe Harbor question is `no`.
TRUTH_NO = (*MEASURE_SCHEMES, "remark_young", "remark_ctrl")
KINDS = tuple(MAKERS)
# The columns of age bands, whose published levels must name one category
# of 90 or older at most (`value_readers_forms.levels_past_89`).
BAND_COLUMNS = frozenset({*ADULT_SCHEMES, *STRICT_SCHEMES, "grp_ks", *LANG_SCHEMES})


@contextlib.contextmanager
def registered():  # type: ignore[no-untyped-def]
    """These kinds installed in `value_readers_forms`' tables (its makers, held, price, known answers and truthful `no`s) for the length of the block, and taken out after it."""
    added = [kind for kind in KINDS if kind not in readers.MAKERS]
    truth = readers.TRUTH_NO
    for kind in added:
        readers.MAKERS[kind] = MAKERS[kind]  # type: ignore[assignment]
        readers.HELD[kind] = HELD[kind]
        if kind in PRICE:
            readers.PRICE[kind] = PRICE[kind]
        readers.KNOWS[kind] = {"case_ref": "keep", **{column: KNOWN.get(column, "keep") for column in HELD[kind] + PRICE.get(kind, ())}}
    readers.TRUTH_NO = truth + TRUTH_NO
    try:
        yield
    finally:
        readers.TRUTH_NO = truth
        for kind in added:
            del readers.MAKERS[kind]
            del readers.HELD[kind]
            readers.PRICE.pop(kind, None)
            del readers.KNOWS[kind]


def table_of(kind: str) -> zoo.Table:
    """A kind's table in the zoo's form (`value_readers_forms.table_of`), inside `registered`."""
    with registered():
        return readers.table_of(kind)
