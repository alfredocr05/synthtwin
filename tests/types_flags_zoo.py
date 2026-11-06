"""Types, codes and flags: eight invented forms for the zoo (lane CZ-D, plan P4-D447).

Each form is a generic export written from scratch, with generic column
names, built at run time from the zoo's own makers and a seed. The forms:

1. ``codes``: sixteen category code columns, each with 2 to 52 levels and
   a tail (a few levels under 11 rows), blank on some rows; eleven of
   them whole numbers, five figures kept as text with a leading nought
   (``05``).
2. ``flags``: twenty-four Y/N flags holding Y, N and blank, a Y/N/U
   flag, a flag whose blank means No and one with no blanks, yes and no
   spelled three ways across columns (``1``/``0``, ``Y``/``N``,
   ``Yes``/``No``) and yes-only columns (a ``1`` or a blank).
3. ``wide_mart``: 180 columns, 70 of them 1-or-blank indicators (seven
   with their 1s on 1 to 7 rows), ten codes, eighteen date-times and
   thirty whole-number counts.
4. ``near_empty``: measures filled for 2, 5 and 9 people beside full
   columns, and a sparse code beside the value it qualifies.
5. ``frequency_route``: frequency and route words with a derived
   as-needed flag.
6. ``single_byte_units``: a Windows-1252 file whose unit column holds
   the micro and degree signs and whose comment holds accented words.
7. ``role_mix``: 60 columns of every role a health table holds: keys
   (three of them 18-figure whole numbers, a line number in a two-part
   key), whole-number codes and codes with a leading nought, Y/N flags,
   date-times (some dates at midnight), whole and decimal measurements,
   text and fixed two-decimal amounts.
8. ``person_held``: codes and flags with a level 1 to 10 PEOPLE hold on
   11 rows or more (a code that stays with a person), beside one code
   every level of which many people hold.

Every form is a `health_zoo.Table`, so `health_zoo.run_table` runs it end
to end the way the zoo runs its catalogue (profile, the general answers
round by round, generate, validate, the analyst's script on both files)
and `health_zoo.analyse` reads the generic checks (dtypes, blanks,
missing spellings, levels, stand-ins). `form_measures` adds this lane's
own reading of each form (K-HZ-17), every count linear in the cells.

The forms are NOT in the catalogue (`health_zoo.catalogue()`): they are
K-HZ-17's, measured by `tools/measurements/kpi_types_and_flags.py`.
"""

from __future__ import annotations

import datetime
import random
from typing import Callable

import health_zoo
from health_zoo import Check, Table, csv_bytes

# The forms, in the order the report lists them.
FORMS = ("codes", "flags", "wide_mart", "near_empty", "frequency_route", "single_byte_units", "role_mix", "person_held")

# Rows each person holds: about four, so 20,000 rows name 5,000 people
# and 600 rows 150 (the owner's table floor counts people, plan P4-D425).
ROWS_A_PERSON = 4
FIRST_DAY = datetime.date(2022, 1, 1)
DAYS = 900

def _draw(seed: int, place: int) -> random.Random:
    return random.Random(seed * 1_000 + place)


def _people(n: int) -> "list[str]":
    """The person key of each row: about ROWS_A_PERSON rows a person, in a shuffled order."""
    people = max(n // ROWS_A_PERSON, 1)
    return [f"{1_000_000 + (row * 7_919) % people:07d}" for row in range(n)]


def _with_tail(
    n: int, draw: random.Random, pool: "tuple[tuple[str, float], ...]", tail: "tuple[tuple[str, int], ...]", blank: float,
) -> "list[str]":
    """A column of n cells: the tail's values on exactly their counts, blanks on about `blank`, the pool elsewhere."""
    cells = [value for value, count in tail for _ in range(count)]
    values = [value for value, _weight in pool]
    weights = [weight for _value, weight in pool]
    left = n - len(cells)
    cells += ["" if draw.random() < blank else draw.choices(values, weights)[0] for _ in range(left)]
    draw.shuffle(cells)
    return cells


def _zipf_pool(values: "list[str]") -> "tuple[tuple[str, float], ...]":
    return tuple((value, 1.0 / (place + 1)) for place, value in enumerate(values))


def _columns_to_rows(header: "list[str]", columns: "list[list[str]]") -> "tuple[list[str], list[list[str]]]":
    return header, [list(row) for row in zip(*columns)]


def _midnight(name: str) -> bool:
    """Whether a date-time column writes dates at midnight: `event_01_dttm`, `event_04_dttm`, ... one in three."""
    return int(name.split("_")[1]) % 3 == 1


def _stamp(draw: random.Random, midnight: bool) -> str:
    """A date-time as a database export writes it: `2024-03-07 00:00:00.000` (a date) or to the minute."""
    day = FIRST_DAY + datetime.timedelta(days=draw.randint(0, DAYS))
    if midnight:
        return f"{day.isoformat()} 00:00:00.000"
    return f"{day.isoformat()} {draw.randint(0, 23):02d}:{draw.randint(0, 59):02d}:00.000"


# -- form 1: integer category codes ---------------------------------------

# (name, levels, tail, blank share, leading nought): the tail values sit on
# exactly their counts, under the floor of 11 at every size.
CODE_COLUMNS: "tuple[tuple[str, tuple[str, ...], tuple[tuple[str, int], ...], float, bool], ...]" = (
    ("status_code", ("1", "2", "3", "4", "5"), (("9", 4),), 0.0, False),
    ("visit_type_code", tuple(str(10 * k) for k in range(1, 13)), (("990", 3), ("991", 7)), 0.05, False),
    ("class_code", ("1", "2"), (), 0.02, False),
    ("source_code", tuple(str(k) for k in range(1, 38)), (("101", 2), ("102", 5), ("103", 9)), 0.1, False),
    ("disposition_code", tuple(str(k) for k in range(1, 21)), (("88", 6),), 0.15, False),
    ("priority_code", ("1", "2", "3", "4"), (), 0.0, False),
    ("service_code", tuple(str(100 + k) for k in range(28)), (("199", 1), ("198", 8)), 0.08, False),
    ("qualifier_code", ("1", "2", "3", "4", "5"), (("7", 3),), 0.75, False),
    ("payer_class_code", tuple(str(k) for k in range(1, 16)), (("77", 10),), 0.3, False),
    ("unit_code", tuple(f"{k:02d}" for k in range(1, 16)), (("27", 4),), 0.04, True),
    ("category_code", tuple(f"{k:03d}" for k in (1, 2, 5, 8, 14, 21, 33, 40)), (("099", 6),), 0.12, True),
    ("level_code", ("01", "02", "03", "04", "05", "06"), (("09", 2),), 0.0, True),
    ("ward_code", tuple(str(k) for k in range(1, 51)), (("97", 3), ("98", 8)), 0.06, False),
    ("form_code", tuple(f"{k:02d}" for k in range(1, 10)), (("12", 6),), 0.2, True),
    ("group_set_code", tuple(f"{k:03d}" for k in (3, 6, 9, 12, 15)), (("120", 2),), 0.03, True),
    # A tail on the next free number: its stand-in comes back as itself.
    ("adjacent_code", ("1", "2", "3", "4", "5"), (("6", 4),), 0.0, False),
)


def codes(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Sixteen category codes: whole numbers, and figures kept as text with a leading nought."""
    header = ["record_key", "patient_key"]
    columns = [[str(100_000 + row) for row in range(n)], _people(n)]
    for place, (name, levels, tail, blank, _nought) in enumerate(CODE_COLUMNS):
        header += [name]
        columns += [_with_tail(n, _draw(seed, place), _zipf_pool(list(levels)), tail, blank)]
    return _columns_to_rows(header, columns)


# -- form 2: dense Y/N flags ------------------------------------------------

FLAG_COUNT = 24


def _flag_names() -> "list[str]":
    return [f"hx_indicator_{place + 1:02d}" for place in range(FLAG_COUNT - 4)] + [
        "is_inpatient", "is_readmission", "prn_flag", "is_verified",
    ]


def flags(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Twenty-four Y/N/blank flags, a Y/N/U flag, a blank-means-No flag, a full flag, three spellings and yes-only columns."""
    header = ["record_key", "patient_key"]
    columns = [[str(200_000 + row) for row in range(n)], _people(n)]
    for place, name in enumerate(_flag_names()):
        draw = _draw(seed, place)
        yes = 0.05 + 0.6 * draw.random()
        blank = 0.02 + 0.3 * draw.random()
        header += [name]
        columns += [["" if (roll := draw.random()) < blank else "Y" if roll < blank + yes * (1 - blank) else "N" for _ in range(n)]]
    draw = _draw(seed, 50)
    header += ["consent_ynu", "is_deceased", "is_enrolled", "is_smoker_10", "has_alert_yesno", "screened_1", "followup_1"]
    columns += [
        [draw.choices(("Y", "N", "U", ""), (40, 45, 10, 5))[0] for _ in range(n)],
        # blank means No: only Y is written
        ["Y" if draw.random() < 0.04 else "" for _ in range(n)],
        # no blanks
        [draw.choices(("Y", "N"), (70, 30))[0] for _ in range(n)],
        [draw.choices(("1", "0", ""), (20, 70, 10))[0] for _ in range(n)],
        [draw.choices(("Yes", "No", ""), (35, 55, 10))[0] for _ in range(n)],
        # yes-only: a 1 or a blank
        ["1" if draw.random() < 0.3 else "" for _ in range(n)],
        ["1" if draw.random() < 0.08 else "" for _ in range(n)],
    ]
    return _columns_to_rows(header, columns)


# -- form 3: the wide mart --------------------------------------------------

WIDE_INDICATORS = 70
# The indicators whose 1s sit on 1 to 10 rows at every size.
RARE_INDICATORS = 7
WIDE_CODES = 10
WIDE_STAMPS = 18
WIDE_MEASURES = 30
WIDE_TEXT = 50


def wide_mart(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """180 columns: 70 1-or-blank indicators, ten codes, eighteen date-times, thirty counts and fifty word columns."""
    header = ["record_key", "patient_key"]
    columns = [[str(300_000 + row) for row in range(n)], _people(n)]
    for place in range(WIDE_INDICATORS):
        draw = _draw(seed, place)
        header += [f"hx_indicator_{place + 1:03d}"]
        if place < RARE_INDICATORS:
            ones = 1 + place  # 1 to 7 rows
            cells = ["1"] * ones + [""] * (n - ones)
            draw.shuffle(cells)
        else:
            share = 0.01 + 0.4 * draw.random()
            cells = ["1" if draw.random() < share else "" for _ in range(n)]
        columns += [cells]
    for place in range(WIDE_CODES):
        draw = _draw(seed, 1_000 + place)
        levels = [str(k) for k in range(1, 3 + 3 * place)]
        header += [f"group_{place + 1:02d}_code"]
        columns += [_with_tail(n, draw, _zipf_pool(levels), (("999", 3),), 0.05 * (place % 3))]
    for place in range(WIDE_STAMPS):
        draw = _draw(seed, 2_000 + place)
        header += [f"event_{place + 1:02d}_dttm"]
        midnight = _midnight(header[-1])
        blank = 0.1 * (place % 4)
        columns += [["" if draw.random() < blank else _stamp(draw, midnight) for _ in range(n)]]
    for place in range(WIDE_MEASURES):
        draw = _draw(seed, 3_000 + place)
        middle = 5 + 10 * place
        header += [f"count_{place + 1:02d}"]
        blank = 0.05 * (place % 3)
        columns += [["" if draw.random() < blank else str(max(0, int(draw.gauss(middle, middle / 3)))) for _ in range(n)]]
    words = ("pending", "complete", "reviewed", "in progress", "cancelled", "on hold")
    for place in range(WIDE_TEXT):
        draw = _draw(seed, 4_000 + place)
        header += [f"note_label_{place + 1:02d}"]
        columns += [[draw.choice(words) for _ in range(n)]]
    return _columns_to_rows(header, columns)


# -- form 4: near-empty measures and sparse codes ---------------------------

NEAR_EMPTY = ("rare_measure_a", "rare_measure_b", "rare_measure_c")


def near_empty(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Measures filled for 2, 5 and 9 people beside full columns; a sparse code beside the value it qualifies."""
    draw = _draw(seed, 0)
    people = _people(n)
    header = ["record_key", "patient_key", "full_measure", "full_count", "result_value", "result_qualifier_code"]
    header += list(NEAR_EMPTY)
    chosen = sorted(set(people))
    filled = [set(draw.sample(chosen, min(size, len(chosen)))) for size in (2, 5, 9)]
    rows: "list[list[str]]" = []
    for row in range(n):
        person = people[row]
        value = round(draw.gauss(5.0, 1.2), 1)
        qualifier = draw.choices(("", "1", "2"), (85, 10, 5))[0]
        rows += [[
            str(400_000 + row), person, f"{draw.gauss(80.0, 9.0):.1f}", str(draw.randint(0, 12)),
            f"{value}", qualifier,
        ] + [f"{draw.gauss(30.0 + 10 * k, 3.0):.1f}" if person in filled[k] else "" for k in range(3)]]
    return header, rows


# -- form 5: frequency and route words --------------------------------------

FREQUENCIES = (
    ("once daily", 30.0), ("twice daily", 20.0), ("every 6 hours as needed", 12.0), ("every 4 hours as needed", 8.0),
    ("at bedtime", 8.0), ("three times daily", 10.0), ("every 8 hours", 6.0), ("once as needed", 4.0), ("weekly", 2.0),
)
ROUTE_WORDS = (("oral", 60.0), ("intravenous", 20.0), ("subcutaneous", 8.0), ("inhalation", 6.0), ("topical", 4.0), ("rectal", 2.0))


def frequency_route(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Frequency and route words, with an as-needed flag derived from the frequency."""
    draw = _draw(seed, 0)
    header = ["record_key", "patient_key", "frequency_text", "route_text", "prn_flag"]
    rows: "list[list[str]]" = []
    for row, person in enumerate(_people(n)):
        frequency = health_zoo._pick(draw, FREQUENCIES)
        rows += [[str(500_000 + row), person, frequency, health_zoo._pick(draw, ROUTE_WORDS), "Y" if "as needed" in frequency else "N"]]
    return header, rows


# -- form 6: a single-byte file with micro and degree signs -----------------

UNIT_WORDS = (("µg/mL", 30.0), ("°C", 25.0), ("mg/dL", 25.0), ("µmol/L", 15.0), ("°F", 5.0))
COMMENTS = (
    ("", 50.0), ("café au lait", 10.0), ("résultat vérifié", 15.0), ("déjà traité", 10.0), ("naïve", 5.0),
    ("reçu à l'accueil", 10.0),
)


def single_byte_units(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Units holding the micro and degree signs and comments in accented words, for a Windows-1252 file."""
    draw = _draw(seed, 0)
    header = ["record_key", "patient_key", "result_value", "unit_text", "comment_text"]
    rows: "list[list[str]]" = []
    for row, person in enumerate(_people(n)):
        rows += [[
            str(600_000 + row), person, f"{draw.gauss(40.0, 8.0):.1f}",
            health_zoo._pick(draw, UNIT_WORDS), health_zoo._pick(draw, COMMENTS),
        ]]
    return header, rows


# -- form 7: every role a health table holds --------------------------------

# (name, role): 60 columns.
MIX: "tuple[tuple[str, str], ...]" = (
    tuple((f"entity_{place + 1:02d}_key", "key") for place in range(3))  # 18-figure whole numbers
    + tuple((f"ref_{place + 1:02d}_id", "key") for place in range(3))  # text keys
    + (("parent_key", "key"), ("line_no", "key"), ("patient_key", "key"))
    + tuple((f"type_{place + 1:02d}_code", "code") for place in range(10))  # whole numbers
    + tuple((f"kind_{place + 1:02d}_code", "code") for place in range(6))  # figures with a leading nought
    + tuple((f"is_flag_{place + 1:02d}", "flag") for place in range(6))
    + tuple((f"event_{place + 1:02d}_dttm", "datetime") for place in range(12))
    + tuple((f"count_{place + 1:02d}", "measurement") for place in range(5))
    + tuple((f"value_{place + 1:02d}", "measurement") for place in range(3))
    + tuple((f"label_{place + 1:02d}_text", "text") for place in range(6))
    + (("amount_01", "amount"), ("amount_02", "amount"), ("amount_03", "amount"))
)


def role_mix(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """60 columns of every role, with a (parent, line) two-part key."""
    people = _people(n)
    columns: "list[list[str]]" = []
    parents = [str(700_000_000 + row // 3) for row in range(n)]
    lines = [str(row % 3 + 1) for row in range(n)]
    for place, (name, role) in enumerate(MIX):
        draw = _draw(seed, place)
        if name == "parent_key":
            cells = parents
        elif name == "line_no":
            cells = lines
        elif name == "patient_key":
            cells = people
        elif role == "key" and name.endswith("_key"):
            # 18-figure whole numbers: a running key per entity, one a row, with gaps.
            start = 100_000_000_000_000_000 + place * 10_000_000_000
            cells = [str(start + 50 * row + draw.randint(0, 49)) for row in range(n)]
        elif role == "key":
            # Text keys, one a row: figures alone, or a letter before them.
            cells = [f"{10_000_000 + 40 * row + draw.randint(0, 39)}" if place % 2 else f"A{1_000_000 + 40 * row + draw.randint(0, 39)}" for row in range(n)]
        elif role == "code" and name.startswith("kind_"):
            levels = [f"{k:02d}" for k in range(1, 6 + 3 * place % 7)]
            cells = _with_tail(n, draw, _zipf_pool(levels), (("98", 5),), 0.05)
        elif role == "code":
            levels = [str(k) for k in range(1, 3 + (place * 5) % 30)]
            cells = _with_tail(n, draw, _zipf_pool(levels), (("999", 4),), 0.1 * (place % 3))
        elif role == "flag":
            cells = [draw.choices(("Y", "N", ""), (30, 60, 10))[0] for _ in range(n)]
        elif role == "datetime":
            midnight = _midnight(name)
            cells = ["" if draw.random() < 0.1 * (place % 3) else _stamp(draw, midnight) for _ in range(n)]
        elif role == "measurement" and name.startswith("count_"):
            cells = [str(draw.randint(0, 40)) for _ in range(n)]
        elif role == "measurement":
            cells = ["" if draw.random() < 0.05 else f"{draw.gauss(100.0, 15.0):.2f}" for _ in range(n)]
        elif role == "text":
            words = ("routine", "urgent", "follow up", "see note", "per protocol", "completed", "deferred")
            cells = [draw.choice(words) for _ in range(n)]
        else:  # amount: fixed two decimals, negative on about a fifth, zero on about a tenth, whole on most
            cells = []
            for _ in range(n):
                roll = draw.random()
                if roll < 0.1:
                    cells += ["0.00"]
                    continue
                value = draw.randint(1, 5_000) + (0 if draw.random() < 0.8 else draw.randint(1, 99) / 100)
                cells += [f"{-value if roll < 0.3 else value:.2f}"]
        columns += [cells]
    return _columns_to_rows([name for name, _role in MIX], columns)


def role_of(form: str, column: str) -> str:
    """The role a form's column plays: key, code, flag, date-time, measurement, text or amount."""
    if form == "role_mix":
        return dict(MIX)[column]
    if column in ("record_key", "patient_key"):
        return "key"
    if column.endswith("_code"):
        return "code"
    if column.endswith("_dttm"):
        return "datetime"
    if column.startswith(("hx_indicator", "ind_", "is_", "has_", "prn_", "consent_", "screened", "followup")):
        return "flag"
    if column.endswith("_text") or column.startswith("note_label"):
        return "text"
    return "measurement"


# -- form 8: levels 1 to 10 people hold on 11 rows or more ------------------


def person_held(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Codes and flags with a level a few people hold on all their rows, beside a code many people share."""
    draw = _draw(seed, 0)
    people = _people(n)
    everyone = sorted(set(people))

    def few(size: int) -> "set[str]":
        return set(draw.sample(everyone, min(size, len(everyone))))

    def zipf(levels: "list[str]") -> str:
        return draw.choices(levels, [1 / (place + 1) for place in range(len(levels))])[0]

    five = list("12345")
    noughts = [f"0{k}" for k in range(1, 6)]
    home = {person: str(draw.choices(range(1, 31), [1 / k for k in range(1, 31)])[0]) for person in everyone}
    home.update({person: "100" for person in everyone[:3]})
    home.update({person: "101" for person in everyone[3:9]})
    code, nought, flag, alert, smoker, indicator = few(5), few(5), few(8), few(5), few(8), few(5)
    header = [
        "record_key", "patient_key", "few_people_code", "few_people_nought_code", "person_home_code", "is_flag_p8", "has_alert_p5",
        "is_smoker_p8", "ind_5people", "common_code",
    ]
    rows: "list[list[str]]" = []
    for row, person in enumerate(people):
        rows += [[
            str(810_000 + row), person,
            "6" if person in code else zipf(five),
            "09" if person in nought else zipf(noughts),
            home[person],
            "Y" if person in flag else "" if draw.random() < 0.1 else "N",
            "Yes" if person in alert else "No",
            "1" if person in smoker else "0",
            "1" if person in indicator else "",
            zipf(five),
        ]]
    return header, rows


# -- the analyst's reading of each form (K-HZ-17) ---------------------------


def _share(series: object, test: "Callable[[object], object]") -> float:
    total = len(series)  # type: ignore[arg-type]
    return float(test(series).sum()) / max(total, 1)  # type: ignore[attr-defined]


def _filter_shares(column: str, levels: "tuple[str, ...]", nought: bool) -> "Callable[[dict[str, object]], object]":
    """An analyst's == and isin filters on a code column, as row shares of the inferred read."""
    first, top = levels[0], list(levels[:3])

    def shares(frames: "dict[str, object]") -> object:
        series = frames["text" if nought else "inferred"][column]  # type: ignore[index]
        if nought:
            return (_share(series, lambda s: s == first), _share(series, lambda s: s.isin(top)))
        return (
            _share(series, lambda s: s == int(first)),
            _share(series, lambda s: s.isin([int(value) for value in top])),
        )

    return shares


def _bad_spelling(column: str, pattern: str) -> "Callable[[dict[str, object]], object]":
    """Present cells off a spelling the form keeps (a code written 3.0, an indicator written 1.0)."""
    return lambda frames: int(
        (~frames["raw"][column].astype(str).str.fullmatch(pattern)).sum()  # type: ignore[index]
    )


def _blank_shares(column: str, values: "tuple[str, ...]") -> "Callable[[dict[str, object]], object]":
    """Each value's share of the rows and the blanks' share, read from the raw cells."""

    def shares(frames: "dict[str, object]") -> object:
        raw = frames["raw"][column].astype(str)  # type: ignore[index]
        return tuple(_share(raw, lambda s, v=value: s == v) for value in values + ("",))

    return shares


WHOLE = r"\d+|"
AT_MIDNIGHT = r"\d{4}-\d\d-\d\d 00:00:00\.000|"
TO_THE_MINUTE = r"\d{4}-\d\d-\d\d \d\d:\d\d:00\.000|"
TWO_DECIMALS = r"-?\d+\.\d\d|"


def _stamp_check(form: str, name: str, midnight: bool) -> Check:
    """A date-time keeps its midnight, or its whole minute, on every present cell."""
    ending = "00:00:00.000" if midnight else ":00.000"
    return Check(form, f"{name}: cells ending {ending} are written as the source spells them", "bad",
                 _bad_spelling(name, AT_MIDNIGHT if midnight else TO_THE_MINUTE), name)


def _code_checks() -> "tuple[Check, ...]":
    checks: "list[Check]" = []
    for name, levels, _tail, _blank, nought in CODE_COLUMNS:
        pattern = r"\d+|" if not nought else r"0\d+|\d+|"
        checks += [
            Check("codes", f"{name}: == and isin filters keep their row shares", "share", _filter_shares(name, levels, nought), name),
            Check("codes", f"{name}: written as whole figures, never 3.0", "bad", _bad_spelling(name, pattern), name),
        ]
    return tuple(checks)


def _flag_checks() -> "tuple[Check, ...]":
    checks: "list[Check]" = []
    for name in _flag_names():
        checks += [
            Check("flags", f"{name}: Y, N and blank shares", "share", _blank_shares(name, ("Y", "N")), name),
            Check("flags", f"{name}: written as the source spells it", "bad", _bad_spelling(name, "Y|N|"), name),
        ]
    for name, values in (
        ("consent_ynu", ("Y", "N", "U")), ("is_deceased", ("Y",)), ("is_enrolled", ("Y", "N")),
        ("is_smoker_10", ("1", "0")), ("has_alert_yesno", ("Yes", "No")), ("screened_1", ("1",)), ("followup_1", ("1",)),
    ):
        checks += [
            Check("flags", f"{name}: value and blank shares", "share", _blank_shares(name, values), name),
            Check("flags", f"{name}: written as the source spells it", "bad", _bad_spelling(name, "|".join(values) + "|"), name),
        ]
    return tuple(checks)


def _wide_checks() -> "tuple[Check, ...]":
    checks: "list[Check]" = []
    for place in range(WIDE_INDICATORS):
        name = f"hx_indicator_{place + 1:03d}"
        checks += [Check("wide_mart", f"{name}: written 1, never 1.0", "bad", _bad_spelling(name, "1|"), name)]
        if place >= RARE_INDICATORS:
            checks += [Check("wide_mart", f"{name}: 1 and blank shares", "share", _blank_shares(name, ("1",)), name)]
    for place in range(WIDE_CODES):
        name = f"group_{place + 1:02d}_code"
        checks += [
            Check("wide_mart", f"{name}: == filter keeps its row share", "share", _filter_shares(name, ("1",), False), name),
            Check("wide_mart", f"{name}: written as whole figures, never 3.0", "bad", _bad_spelling(name, WHOLE), name),
        ]
    for place in range(WIDE_STAMPS):
        name = f"event_{place + 1:02d}_dttm"
        checks += [_stamp_check("wide_mart", name, _midnight(name))]
    for place in range(WIDE_MEASURES):
        name = f"count_{place + 1:02d}"
        checks += [Check("wide_mart", f"{name}: written as whole figures, never 3.0", "bad", _bad_spelling(name, WHOLE), name)]
    return tuple(checks)


def _near_empty_checks() -> "tuple[Check, ...]":
    checks: "list[Check]" = [
        Check("near_empty", "result_qualifier_code: blank, 1 and 2 shares", "share", _blank_shares("result_qualifier_code", ("1", "2")), "result_qualifier_code"),
        Check("near_empty", "result_qualifier_code: written as whole figures, never 3.0", "bad", _bad_spelling("result_qualifier_code", WHOLE), "result_qualifier_code"),
        Check("near_empty", "full_count: written as whole figures, never 3.0", "bad", _bad_spelling("full_count", WHOLE), "full_count"),
    ]
    for name in NEAR_EMPTY:
        checks += [Check(
            "near_empty", f"{name}: written empty where the real is empty", "share",
            lambda frames, column=name: _share(frames["raw"][column].astype(str), lambda s: s == ""), name,  # type: ignore[index]
        )]
    return tuple(checks)


def _frequency_checks() -> "tuple[Check, ...]":
    return (
        Check(
            "frequency_route", "str.contains('as needed') keeps its row share", "share",
            lambda frames: _share(frames["text"]["frequency_text"].fillna(""), lambda s: s.str.contains("as needed")),  # type: ignore[index]
            "frequency_text",
        ),
        Check("frequency_route", "prn_flag Y and N shares", "share", _blank_shares("prn_flag", ("Y", "N")), "prn_flag"),
    )


def _single_byte_checks() -> "tuple[Check, ...]":
    return (
        Check("single_byte_units", "the micro sign survives as byte 0xB5", "present", lambda frames: b"\xb5" in frames["bytes"], "unit_text"),  # type: ignore[operator]
        Check("single_byte_units", "the degree sign survives as byte 0xB0", "present", lambda frames: b"\xb0" in frames["bytes"], "unit_text"),  # type: ignore[operator]
        Check("single_byte_units", "no cell reads as mojibake", "bad", lambda frames: health_zoo._mojibake(frames["text"]), "comment_text"),
        Check("single_byte_units", "the file is not rewritten as UTF-8", "bad",
              lambda frames: int(b"\xc2\xb5" in frames["bytes"] or b"\xc2\xb0" in frames["bytes"]), "unit_text"),  # type: ignore[operator]
    )


def _mix_checks() -> "tuple[Check, ...]":
    """Form 7: date-times keep their midnight and their whole minute; codes their == filter; every role its spelling."""
    checks: "list[Check]" = []
    for name, role in MIX:
        if role == "datetime":
            checks += [_stamp_check("role_mix", name, _midnight(name))]
        elif role == "code":
            first = "01" if name.startswith("kind_") else "1"
            checks += [
                Check(
                    "role_mix", f"{name}: == filter keeps its row share", "share",
                    _filter_shares(name, (first,), name.startswith("kind_")), name,
                ),
                Check("role_mix", f"{name}: written as whole figures, never 3.0", "bad", _bad_spelling(name, WHOLE), name),
            ]
        elif name.startswith("count_"):
            checks += [Check("role_mix", f"{name}: written as whole figures, never 3.0", "bad", _bad_spelling(name, WHOLE), name)]
        elif name.startswith(("value_", "amount_")):
            checks += [Check("role_mix", f"{name}: written to two decimals", "bad", _bad_spelling(name, TWO_DECIMALS), name)]
        elif name.startswith("entity_"):
            checks += [Check("role_mix", f"{name}: written as 18 whole figures", "bad", _bad_spelling(name, r"\d{18}|"), name)]
    return tuple(checks)


def _person_held_checks() -> "tuple[Check, ...]":
    """Form 8: every common level's filter or share, in columns where a few people hold one level."""
    five = ("1", "2", "3", "4", "5")
    checks: "list[Check]" = []
    for name, levels, nought in (
        ("few_people_code", five, False), ("few_people_nought_code", ("01", "02", "03", "04", "05"), True),
        ("person_home_code", five, False), ("common_code", five, False),
    ):
        checks += [
            Check("person_held", f"{name}: == and isin filters keep their row shares", "share", _filter_shares(name, levels, nought), name),
            Check("person_held", f"{name}: written as whole figures, never 3.0", "bad", _bad_spelling(name, WHOLE), name),
        ]
    for name, values in (("is_flag_p8", ("Y", "N")), ("has_alert_p5", ("Yes", "No")), ("is_smoker_p8", ("1", "0")), ("ind_5people", ("1",))):
        checks += [
            Check("person_held", f"{name}: value and blank shares", "share", _blank_shares(name, values), name),
            Check("person_held", f"{name}: written as the source spells it", "bad", _bad_spelling(name, "|".join(values) + "|"), name),
        ]
    return tuple(checks)


def _knows(header_of: "Callable[[int, int], tuple[list[str], list[list[str]]]]", form: str) -> "dict[str, str]":
    header, _rows = header_of(3, 0)
    known: "dict[str, str]" = {}
    for column in header:
        role = role_of(form, column)
        if role == "key" and column not in ("line_no", "parent_key"):
            known[column] = "identifier"
        elif role == "code":
            known[column] = "code"
        elif role in ("measurement", "amount"):
            known[column] = "measurement"
    return known


def _table(
    name: str, build: "Callable[[int, int], tuple[list[str], list[list[str]]]]", checks: "tuple[Check, ...]",
    encoding: str = "utf-8",
) -> Table:
    header, _rows = build(3, 0)
    return Table(
        name, ".csv", build,
        lambda head, rows: csv_bytes(head, rows, encoding=encoding),
        {name: tuple(header)},
        _knows(build, name),
        health_zoo._csv_reader(encoding=encoding),
        checks,
        person="patient_key",
        # The parent of a (parent, line) key repeats on its lines: it is
        # left unanswered, so P4-D401 holds it as record numbers, and its
        # values are read for leaks as an identifier's are.
        leaks=(("parent_key", "values"),) if "parent_key" in header else (),
    )


def tables() -> "tuple[Table, ...]":
    """The eight forms, each a zoo table."""
    return (
        _table("codes", codes, _code_checks()),
        _table("flags", flags, _flag_checks()),
        _table("wide_mart", wide_mart, _wide_checks()),
        _table("near_empty", near_empty, _near_empty_checks()),
        _table("frequency_route", frequency_route, _frequency_checks()),
        _table("single_byte_units", single_byte_units, _single_byte_checks(), encoding="cp1252"),
        _table("role_mix", role_mix, _mix_checks()),
        _table("person_held", person_held, _person_held_checks()),
    )


SEED = 20261030

# K-HZ-17's counts, per size; the ledger bounds all but those recorded apart.
COUNTS = (
    "steps_failing", "dtype", "spelling", "blank_share", "filter_share", "text_cells_in_number_columns",
    "group_n", "validate_misses", "leaks", "rare_values_published", "rare_counts_published", "made_up_codes",
    "codes_past_held", "source_check_errors", "file_wide", "other", "held_levels_met_cells",
)
RECORDED_APART = ("made_up_codes", "held_levels_met_cells")


def seed_of(table: Table) -> int:
    return SEED + FORMS.index(table.name)


# -- K-HZ-17: what one form's run measured -----------------------------------

GENERIC_PREFIXES = ("dtype ", "missing spellings ", "missing ", "shapes ", "forms ", "levels ", "stand-ins ", "codes ")


def failed_column(table: Table, name: str) -> str:
    """The column an analyst check reads: a generic check's own, or a table check's `column`."""
    for prefix in GENERIC_PREFIXES:
        if name.startswith(prefix):
            return name[len(prefix):]
    for check in table.checks:
        if check.name == name:
            return check.column
    return ""


def _class_of(name: str) -> str:
    """The K-HZ-17 class of a failing analyst check, by its name."""
    if name.startswith("dtype "):
        return "dtype"
    if name.startswith("codes "):
        # A held-back level written as a made-up code of the column's own
        # form: the floor's price (`health_zoo.WITHHELD`), counted apart
        # while it stays within the held population (`_codes_within_held`).
        return "made_up_codes"
    if name.startswith("stand-ins "):
        return "group_n"
    if "cells ending" in name:
        return "spelling"
    if "filter" in name or "contains" in name:
        return "filter_share"
    if "shares" in name or "written empty" in name or "keep their share" in name:
        return "blank_share"
    if "written" in name or "mojibake" in name or "byte" in name or "UTF-8" in name or "spells" in name:
        return "spelling"
    return "other"


def _number_read(text: str) -> bool:
    try:
        float(text)
    except ValueError:
        return False
    return True


def _block_of(described: "dict", column: str) -> "dict":
    for block in described.get("columns", []):
        if f"{block.get('name')}" == column:
            return block  # type: ignore[no-any-return]
    return {}


def _codes_within_held(block: "dict", real_cells: "list[str]", twin_cells: "list[str]") -> bool:
    """Whether a column's made-up codes are held-back levels' stand-ins: no more cells than the description holds back, each in the column's own form."""
    real = set(real_cells)
    widths = {len(cell) for cell in real if cell}
    made_up = [cell for cell in twin_cells if cell and cell not in real]
    held = block.get("suppressed_rows", 0)
    if len(made_up) > (held if isinstance(held, int) else 0):
        return False
    return all(cell.isascii() and cell.isdigit() and len(cell) in widths for cell in made_up)


def _thin_columns(table: Table, real: object) -> "list[tuple[str, int]]":
    """The columns whose present cells 1 to 10 people hold, each with those cells' count."""
    found: "list[tuple[str, int]]" = []
    person = real[table.person]  # type: ignore[index]
    for column in real.columns:  # type: ignore[attr-defined]
        if column == table.person:
            continue
        present = real[column] != ""  # type: ignore[index]
        rows = int(present.sum())
        if rows and rows < len(present) and person[present].nunique() <= THIN_AT_MOST:
            found += [(f"{column}", rows)]
    return found


# A group of 1 to 10 people: the owner's floor of 11, counted in people.
THIN_AT_MOST = 10
# The facts of a block that state how many cells a column holds, beside
# the rows less its `n_missing` (`_states_present_count`).
PRESENT_COUNTS = ("n_present", "n_numeric", "n_not_numeric", "suppressed_rows")


def _states_present_count(block: "dict", rows: int, total: int) -> bool:
    """Whether a block states how many cells a column holds, directly or as the rows less its missing cells."""
    missing = block.get("n_missing")
    return any(block.get(fact) == rows for fact in PRESENT_COUNTS) or (isinstance(missing, int) and total - missing == rows)


def _holders(cells: "list[str]", people: "list[str]") -> "dict[str, set[str]]":
    """Each present value of a column and the people who hold it, one pass over the cells."""
    holders: "dict[str, set[str]]" = {}
    for cell, who in zip(cells, people):
        if cell:
            holders.setdefault(cell, set()).add(who)
    return holders


def _few_held(holders: "dict[str, set[str]]") -> "set[str]":
    return {value for value, who in holders.items() if len(who) <= THIN_AT_MOST}


def _levels_few_hold_published(block: "dict", few: "set[str]") -> int:
    """The published levels naming a value 1 to 10 people hold: by the level's `label`, or a key of its `variants` or `variants_withheld`."""
    spelled = few | {health_zoo._normal(value) for value in few}
    shown = 0
    for level in block.get("levels") or []:
        said = {f"{level.get('label')}"} | {f"{key}" for key in level.get("variants") or ()} | {
            f"{key}" for key in level.get("variants_withheld") or ()
        }
        if said & spelled or {health_zoo._normal(text) for text in said} & spelled:
            shown = shown + 1
    return shown


def _code_levels_read(
    holders: "dict[str, set[str]]", real_cells: "list[str]", twin_cells: "list[str]"
) -> "tuple[bool, int]":
    """Whether the row share of any real level 11 or more people hold moved past SHARE_TOLERANCE, and the twin's cells on levels 1 to 10 people hold."""
    real_rows, twin_rows = max(len(real_cells), 1), max(len(twin_cells), 1)
    real_counts: "dict[str, int]" = {}
    for cell in real_cells:
        real_counts[cell] = real_counts.get(cell, 0) + 1
    twin_counts: "dict[str, int]" = {}
    for cell in twin_cells:
        twin_counts[cell] = twin_counts.get(cell, 0) + 1
    moved = False
    few_cells = 0
    for level, who in holders.items():
        if len(who) <= THIN_AT_MOST:
            few_cells = few_cells + twin_counts.get(level, 0)
        elif abs(real_counts.get(level, 0) / real_rows - twin_counts.get(level, 0) / twin_rows) > health_zoo.SHARE_TOLERANCE:
            moved = True
    return moved, few_cells


def _held_levels_met(table: Table, real: object, made: object) -> int:
    """Twin cells of a code column equal to a real level 1 to 10 people hold: a stand-in that came back as itself."""
    met = 0
    person = real[table.person].tolist()  # type: ignore[index]
    for column in real.columns:  # type: ignore[attr-defined]
        if role_of(table.name, column) != "code":
            continue
        few = _few_held(_holders(real[column].tolist(), person))  # type: ignore[index]
        if few:
            met = met + sum(1 for cell in made[column].tolist() if cell in few)  # type: ignore[index]
    return met


def form_measures(table: Table, result: "dict", folder: "object") -> "dict[str, object]":
    """One form's K-HZ-17 counts from `health_zoo.run_table`'s result and the files it left in `folder`.

    Every count is linear in the cells: each twin cell is read once, the
    real values of a column held in a set. A fault that names no column
    of the form (the read, the rows, the line endings, a validator's
    miss on the file) is the whole form's: `file_wide` counts it.
    """
    import json
    import pathlib

    import pandas

    where = pathlib.Path(f"{folder}")
    header = set(table.kinds[table.name])
    found: "dict[str, object]" = {
        "steps_failing": 0, "dtype": 0, "spelling": 0, "blank_share": 0, "filter_share": 0, "group_n": 0,
        "made_up_codes": 0, "codes_past_held": 0, "other": 0, "file_wide": 0, "source_check_errors": 0,
        "validate_misses": len(result.get("misses", [])), "leaks": 0,
        "text_cells_in_number_columns": 0, "rare_values_published": 0, "rare_counts_published": 0,
        "held_levels_met_cells": 0, "failing_columns": [],
    }
    steps = result.get("steps", {})
    if any(step not in steps or steps[step]["exit"] not in (0, 3) for step in ("profile", "answers", "generate", "validate")):
        found["steps_failing"] = 1
    failing: "set[str]" = set()

    def fails(column: str) -> None:
        nonlocal failing
        if column in header:
            failing |= {column}
        else:
            found["file_wide"] = int(found["file_wide"]) + 1  # type: ignore[call-overload]

    # A check that does not hold on the SOURCE compares nothing
    # (`analyst_failures` skips it), so it fails its column.
    for name in result.get("analyst_real_errors", []):
        found["source_check_errors"] = int(found["source_check_errors"]) + 1  # type: ignore[call-overload]
        fails(failed_column(table, name))
    for miss in result.get("misses", []):
        fails(f"{miss[0]}")
    for key, leak in result.get("leaks", {}).items():
        if leak.get("description") or leak.get("twin"):
            found["leaks"] = int(found["leaks"]) + 1  # type: ignore[call-overload]
            fails(f"{leak.get('column', key)}")
    source = where / f"{table.name}{table.suffix}"
    twin = where / f"{table.name}-twin{table.suffix}"
    if not twin.is_file():
        found["steps_failing"] = 1
        found["failing_columns"] = sorted(table.kinds[table.name])
        return found
    encoding = "cp1252" if table.name == "single_byte_units" else "utf-8"
    real = pandas.read_csv(source, encoding=encoding, dtype=str, keep_default_na=False)
    made = pandas.read_csv(twin, encoding=encoding, dtype=str, keep_default_na=False)
    described = json.loads((where / f"{table.name}-profile.json").read_text(encoding="utf-8"))
    filters_failed: "set[str]" = set()
    past_held: "set[str]" = set()
    for _kind, name, _why in result.get("analyst", []):
        kind = _class_of(name)
        column = failed_column(table, name)
        if kind == "made_up_codes" and not _codes_within_held(
            _block_of(described, column), real[column].tolist(), made[column].tolist()
        ):
            kind = "codes_past_held"
            past_held |= {column}
        if kind == "filter_share":
            filters_failed |= {column}
        found[kind] = int(found[kind]) + 1  # type: ignore[call-overload]
        if kind != "made_up_codes":
            fails(column)
    for column in real.columns:
        cells = real[column].tolist()
        if all(_number_read(cell) for cell in cells if cell):
            found["text_cells_in_number_columns"] = int(found["text_cells_in_number_columns"]) + sum(  # type: ignore[call-overload]
                1 for cell in made[column].tolist() if cell and not _number_read(cell)
            )
    found["held_levels_met_cells"] = _held_levels_met(table, real, made)
    thin = _thin_columns(table, real)
    thin_names = {column for column, _rows in thin}
    people = real[table.person].tolist()
    for column in real.columns:
        if column == table.person:
            continue
        cells = real[column].tolist()
        holders = _holders(cells, people)
        block = _block_of(described, column)
        # A LEVEL 1 TO 10 PEOPLE HOLD, PUBLISHED IN ANY COLUMN: a thin
        # column's levels are all of them, and are read below.
        if column not in thin_names:
            shown = _levels_few_hold_published(block, _few_held(holders))
            found["rare_values_published"] = int(found["rare_values_published"]) + shown  # type: ignore[call-overload]
            if shown:
                failing |= {column}
        if role_of(table.name, column) != "code":
            continue
        # EVERY LEVEL OF A CODE, not only those an analyst's filter names:
        # a common level's row share, and the cells of levels few people
        # hold within the rows the description holds back. A column counts
        # once under each, whatever its analyst checks already counted.
        moved, few_cells = _code_levels_read(holders, cells, made[column].tolist())
        if moved:
            failing |= {column}
            if column not in filters_failed:
                found["filter_share"] = int(found["filter_share"]) + 1  # type: ignore[call-overload]
        held = block.get("suppressed_rows", 0)
        if few_cells > (held if isinstance(held, int) else 0):
            failing |= {column}
            if column not in past_held:
                found["codes_past_held"] = int(found["codes_past_held"]) + 1  # type: ignore[call-overload]
    # NOTHING OF A RARE INDICATOR OR A NEAR-EMPTY MEASURE IS PUBLISHED: no
    # real value of one in the description's block or among the twin's
    # cells (an indicator's made-up stand-in is the first whole number,
    # 1, whatever the real one -- a column of 7s writes 1 too -- so the
    # indicator's twin cells are not read as the real's). AND ITS COUNT,
    # counted apart: a column 1 to 10 people fill, whose block states how
    # many cells it holds, publishes the size of that group
    # (`rare_counts_published`; plan P4-D447's limit (4), owner lane PL).
    for column, rows in thin:
        block = _block_of(described, column)
        shown = len(block.get("levels", []))
        if column in NEAR_EMPTY:
            # A measure's real values, read among the block's scalars and
            # the twin's cells (an indicator's one value, 1, would meet a
            # count of 1 among the scalars, so its levels alone are read).
            values = {health_zoo._normal(cell) for cell in real[column].tolist() if cell}
            said = {health_zoo._normal(text) for text in health_zoo._block(described, column)}
            written = {health_zoo._normal(cell) for cell in made[column].tolist() if cell}
            shown = shown + len(values & said) + len(values & written)
        found["rare_values_published"] = int(found["rare_values_published"]) + shown  # type: ignore[call-overload]
        if shown:
            failing |= {column}
        if _states_present_count(block, rows, len(real)):
            found["rare_counts_published"] = int(found["rare_counts_published"]) + 1  # type: ignore[call-overload]
            failing |= {column}
    found["failing_columns"] = sorted(failing)
    return found
