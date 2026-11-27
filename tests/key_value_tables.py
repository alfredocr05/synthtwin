"""Invented long tables whose value column is typed by a key column (lane KV, plan P4-D487).

A health table often holds its measurements LONG: one column says which
measurement each row is (a key), another holds the measurement (a
value), whose kind and scale the key decides -- a vital-signs export, a
question-and-answer export, a lab-results export. These makers build six
such forms at the table floor, every name and value invented here, each
from its own seed, with generic column names:

- `recorded_items` (form fs): person, recorded time, item key, item
  value. A block of vital signs at each recording time (two pressures
  drawn as a pair, a pulse shifted by each person's own level), a pain
  score, word keys, a clock key, a date key, a comment key and a long
  tail of item keys, some held by a few people on many rows.
- `numbered_items` (form fsn): the same rows, each key written as a
  six-figure number (a key list exported by number).
- `question_answers` (form qa): person, form date, question key, answer.
- `lab_results` (form lab): person, collection time, test, result and a
  unit the test decides.
- `zoo_flow` (form zf): the zoo's own kind `values_typed_by_key`
  (`dates_in_disguise.flow_values`) at the zoo's seed.
- `answers_with_identifiers` (form qp): a question-and-answer export
  whose answers include Safe Harbor identifiers -- a ZIP code, a city, a
  contact's name, a telephone, a date of birth, an age past 89 and a
  record number -- beside ordinary answers.

Each maker returns a `Form`: the header, the rows, which column is the
person, the key, the value, the time and the unit, and the facts the
measurements read (the values only rare keys hold; the identifier
values each identifier key holds). Nothing here reads a file.
"""

from __future__ import annotations

import dataclasses
import datetime
import random

PEOPLE = 1000
FLOOR = 11


@dataclasses.dataclass(frozen=True)
class Form:
    """One invented long table and the facts its measurements read."""

    name: str
    header: "tuple[str, ...]"
    rows: "tuple[tuple[str, ...], ...]"
    person: str
    key: str
    value: str
    time: str = ""
    unit: str = ""
    key_is_code: bool = False
    value_holds_dates: bool = False
    # Per identifier key of form qp, the values it holds (HIPAA first).
    identifiers: "tuple[tuple[str, tuple[str, ...]], ...]" = ()
    # The keys whose values are ages, whatever their names read as.
    age_keys: "tuple[str, ...]" = ()


def _person(place: int) -> str:
    return f"S{510000 + 11 * place:06d}"


def _falling(count: int, steep: float) -> "list[float]":
    """Weights falling with rank: the long tail of a key list."""
    found: "list[float]" = []
    for rank in range(count):
        found += [1.0 / float(rank + 1) ** steep]
    return found


def census(form: Form) -> "dict[str, tuple[int, int]]":
    """Each key's rows and people."""
    k = form.header.index(form.key)
    p = form.header.index(form.person)
    rows: "dict[str, int]" = {}
    people: "dict[str, set[str]]" = {}
    for row in form.rows:
        rows[row[k]] = rows.get(row[k], 0) + 1
        people.setdefault(row[k], set()).add(row[p])
    return {key: (rows[key], len(people[key])) for key in rows}


def rare_keys(form: Form) -> "frozenset[str]":
    """The keys fewer than the floor's people hold."""
    return frozenset(key for key, (_rows, people) in census(form).items() if people < FLOOR)


def rare_only_values(form: Form) -> "frozenset[str]":
    """The values that only rare keys hold, of a word form a key alone writes (`Mark-NNN`)."""
    k = form.header.index(form.key)
    v = form.header.index(form.value)
    rare = rare_keys(form)
    holders: "dict[str, set[str]]" = {}
    for row in form.rows:
        holders.setdefault(row[v], set()).add(row[k])
    return frozenset(
        value for value, keys in holders.items() if keys <= rare and value.startswith("Mark-")
    )


_SITES = (
    "skin", "pupil_l", "pupil_r", "refill", "swelling_l", "swelling_r", "abdomen", "lung_ru", "lung_lu",
    "lung_rl", "lung_ll", "incision", "drain_one", "drain_two", "line_site", "tube_site", "feeding",
    "sore_sacrum", "sore_heel", "grip_ue", "grip_le", "cough", "sputum", "nausea", "gait", "diet",
    "rest", "affect", "fall_check", "turning",
)
_ASPECTS = ("score", "colour", "size_mm", "state", "volume_ml", "grade", "look", "pace", "depth", "smell")
_WORDS = (
    "Normal", "Abnormal", "Pink", "Pale", "Moist", "Dry", "Small", "Large", "Clear", "Cloudy", "Serous",
    "Bloody", "None", "Mild", "Moderate", "Severe", "Intact", "Reddened", "Warm", "Cool", "Brisk", "Slow",
    "Present", "Absent", "Equal", "Unequal",
)


def _tail(draw: random.Random, names: "list[str]", count: int, words: "tuple[str, ...]") -> "list[dict[str, object]]":
    found: "list[dict[str, object]]" = []
    draw.shuffle(names)
    for place, name in enumerate(names[:count]):
        roll = draw.random()
        if roll < 0.5:
            kind: "dict[str, object]" = {
                "kind": "number", "mid": round(draw.uniform(2, 900), 1), "places": draw.choice((0, 0, 1, 2)),
            }
        elif roll < 0.85:
            chosen = list(draw.sample(words, draw.randint(3, 5)))
            # ...and one word only this key writes: a value a rare key alone holds.
            chosen += [f"Mark-{place:03d}"]
            kind = {"kind": "words", "words": chosen}
        else:
            kind = {"kind": "yesno"}
        kind["name"] = name
        found += [kind]
    return found


def _tail_value(draw: random.Random, key: "dict[str, object]") -> str:
    if key["kind"] == "number":
        middle = float(f"{key['mid']}")
        return f"{max(0.0, draw.gauss(middle, middle / 6)):.{key['places']}f}"
    if key["kind"] == "words":
        words = key["words"]
        assert isinstance(words, list)
        return f"{draw.choice(words)}"
    return draw.choice(("Yes", "No"))


def recorded_items(seed: int = 20261201, people: int = PEOPLE) -> Form:
    """Form fs: patient, recorded time, item key, item value (see the module's text); ``people`` ten times over makes the price's table of about 200,000 rows."""
    draw = random.Random(seed)
    tails = _tail(draw, [f"{site}_{aspect}" for site in _SITES for aspect in _ASPECTS], 284, _WORDS)
    weights = _falling(len(tails), 1.25)
    rows: "list[tuple[str, ...]]" = []
    for place in range(people):
        person = _person(place)
        own_level = draw.gauss(0, 8)
        pain_level = draw.uniform(0, 6)
        start = datetime.datetime(2023, 1, 1) + datetime.timedelta(days=draw.randrange(700), hours=draw.choice((6, 8, 10)))
        times = 1 + min(12, int(draw.expovariate(1 / 1.7)))
        own: "set[int]" = set()
        for _each in range(int(draw.expovariate(1 / 1.2))):
            own.add(draw.choices(range(len(tails)), weights=weights)[0])
        device = draw.choices(("Room air", "Nasal cannula", "Face mask", "High flow"), weights=(6, 3, 1, 0.5))[0]
        for time in range(times):
            at = (start + datetime.timedelta(hours=4 * time)).strftime("%Y-%m-%d %H:%M")
            made: "list[tuple[str, str]]" = []
            upper = max(70, min(220, round(draw.gauss(128, 17))))
            lower = max(35, min(130, round(0.45 * upper + draw.gauss(19, 7))))
            if draw.random() < 0.96:
                made += [("systolic_pressure", f"{upper}"), ("diastolic_pressure", f"{lower}")]
            if draw.random() < 0.95:
                made += [("heart_rate", f"{max(35, round(draw.gauss(80 + own_level, 9)))}")]
            if draw.random() < 0.9:
                made += [("resp_rate", f"{max(8, round(draw.gauss(17, 3)))}")]
            if draw.random() < 0.9:
                made += [("oxygen_saturation", f"{min(100, max(82, round(draw.gauss(96.5, 2))))}")]
            if draw.random() < 0.85:
                made += [("temperature_c", f"{draw.gauss(36.9, 0.45):.1f}")]
            if draw.random() < 0.7:
                made += [("pain_score", f"{max(0, min(10, round(draw.gauss(pain_level, 1.5))))}")]
            if draw.random() < 0.3:
                made += [("sedation_level", draw.choices(("Alert", "Drowsy", "Sedated", "Unresponsive"), weights=(10, 4, 1, 0.3))[0])]
            if draw.random() < 0.5:
                made += [("oxygen_device", device)]
                if device != "Room air":
                    made += [("oxygen_flow_lpm", f"{draw.choice((1, 2, 2, 3, 4, 6, 10, 15))}")]
            if draw.random() < 0.15:
                made += [("coma_scale_total", f"{draw.choices(range(3, 16), weights=[0.2] * 9 + [1, 2, 4, 30])[0]}")]
            if draw.random() < 0.4:
                made += [("urine_output_ml", f"{max(0, round(draw.gauss(160, 70)))}")]
            if draw.random() < 0.1:
                made += [("intake_comment", draw.choice((
                    "Tolerating sips", "Refused breakfast", "Ate half of tray", "Nothing by mouth",
                    "Tolerating diet", "Nauseated after lunch",
                )))]
            if draw.random() < 0.05:
                made += [("last_void_time", f"{draw.randrange(24):02d}:{draw.randrange(60):02d}")]
            if draw.random() < 0.2:
                made += [("cuff_site", draw.choice(("Left arm", "Right arm", "Left leg")))]
            if time == 0 and draw.random() < 0.8:
                made += [("body_mass_kg", f"{draw.gauss(80, 17):.1f}")]
            if time == 0 and draw.random() < 0.1:
                day = start.date() - datetime.timedelta(days=draw.randrange(1, 9))
                made += [("line_placed_on", f"{day.month:02d}/{day.day:02d}/{day.year}")]
            for chosen in sorted(own):
                if draw.random() < 0.75:
                    made += [(f"{tails[chosen]['name']}", _tail_value(draw, tails[chosen]))]
            if draw.random() < 0.35:
                chosen = draw.choices(range(len(tails)), weights=weights)[0]
                made += [(f"{tails[chosen]['name']}", _tail_value(draw, tails[chosen]))]
            for key, value in made:
                rows += [(person, at, key, value)]
    return Form(
        "fs", ("patient_id", "recorded_at", "item_key", "item_value"), tuple(rows),
        "patient_id", "item_key", "item_value", time="recorded_at", value_holds_dates=True,
    )


def numbered_items(form: "Form | None" = None) -> Form:
    """Form fsn: form fs with each key written as a six-figure number, in the order of the sorted names."""
    base = recorded_items() if form is None else form
    names = sorted({row[2] for row in base.rows})
    number = {name: f"{410000 + 13 * place}" for place, name in enumerate(names)}
    rows = tuple((row[0], row[1], number[row[2]], row[3]) for row in base.rows)
    return Form(
        "fsn", ("patient_id", "recorded_at", "item_id", "item_value"), rows,
        "patient_id", "item_id", "item_value", time="recorded_at", key_is_code=True, value_holds_dates=True,
    )


_TOPICS = (
    "hearing", "vision", "teeth", "falls", "memory", "spirits", "meals", "rest", "skin", "bladder", "bowel",
    "breath", "chest", "joints", "feet", "travel", "job", "home", "carer", "transport", "money",
    "walking", "animals", "rash", "shots",
)
_ENDS = ("recent", "worse", "help", "days", "score", "since", "trouble", "aid", "change", "count")


def question_answers(seed: int = 20261202) -> Form:
    """Form qa: patient, form date, question key, answer."""
    draw = random.Random(seed)
    tails: "list[dict[str, object]]" = []
    names = [f"{topic}_{end}" for topic in _TOPICS for end in _ENDS]
    draw.shuffle(names)
    for place, name in enumerate(names[:160]):
        roll = draw.random()
        if roll < 0.4:
            kind: "dict[str, object]" = {"kind": "number", "mid": round(draw.uniform(1, 30), 1), "places": 0}
        elif roll < 0.75:
            kind = {"kind": "yesno"}
        else:
            chosen = list(draw.sample(("Never", "Rarely", "Sometimes", "Often", "Always", "Unsure"), 4))
            kind = {"kind": "words", "words": chosen + [f"Mark-{place:03d}"]}
        kind["name"] = name
        tails += [kind]
    weights = _falling(len(tails), 1.2)
    rows: "list[tuple[str, ...]]" = []
    for place in range(PEOPLE):
        person = _person(place)
        forms = 1 + min(6, int(draw.expovariate(1 / 0.9)))
        smoking = draw.choices(("Current", "Former", "Never"), weights=(2, 3, 5))[0]
        stature = draw.gauss(170, 10)
        first = datetime.date(2022, 1, 1) + datetime.timedelta(days=draw.randrange(900))
        own = {draw.choices(range(len(tails)), weights=weights)[0] for _each in range(int(draw.expovariate(1 / 1.5)))}
        for each in range(forms):
            day = first + datetime.timedelta(days=90 * each + draw.randrange(20))
            made: "list[tuple[str, str]]" = [
                ("tobacco_use", smoking),
            ]
            if smoking == "Current":
                made += [("cigarettes_per_day", f"{max(1, round(draw.gauss(12, 6)))}")]
            made += [
                ("alcohol_drinks_week", f"{max(0, round(draw.expovariate(1 / 4)))}"),
                ("exercise_days_week", f"{draw.randint(0, 7)}"),
                ("low_spirits_score", f"{draw.choices(range(7), weights=(30, 20, 12, 8, 5, 3, 2))[0]}"),
                ("sleep_hours", f"{min(12, max(3, draw.gauss(6.8, 1.2))):.1f}"),
                ("lives_alone", draw.choices(("Yes", "No"), weights=(1, 3))[0]),
                ("fall_last_year", draw.choices(("Yes", "No"), weights=(1, 4))[0]),
                ("pain_now", f"{max(0, min(10, round(draw.gauss(3, 2.5))))}"),
                ("walking_aid", draw.choices(("None", "Cane", "Walker", "Wheelchair"), weights=(12, 3, 2, 1))[0]),
                ("meal_plan", draw.choices(("Regular", "Diabetic", "Low salt", "Vegetarian"), weights=(10, 3, 2, 1))[0]),
                ("stature_cm", f"{stature:.0f}"),
                ("body_mass_kg", f"{draw.gauss(78, 16):.1f}"),
            ]
            if draw.random() < 0.5:
                made += [("care_wishes_on_file", draw.choice(("Yes", "No", "Unknown")))]
            if draw.random() < 0.6:
                made += [("main_concern", draw.choice((
                    "Knee pain", "Follow-up visit", "Refill needed", "Back pain", "Short of breath",
                    "Check blood pressure", "Feeling tired",
                )))]
            if draw.random() < 0.3:
                shot = day - datetime.timedelta(days=draw.randrange(30, 400))
                made += [("last_flu_shot", f"{shot.year}-{shot.month:02d}")]
            for chosen in sorted(own):
                if draw.random() < 0.8:
                    made += [(f"{tails[chosen]['name']}", _tail_value(draw, tails[chosen]))]
            if draw.random() < 0.3:
                chosen = draw.choices(range(len(tails)), weights=weights)[0]
                made += [(f"{tails[chosen]['name']}", _tail_value(draw, tails[chosen]))]
            for key, value in made:
                rows += [(person, day.isoformat(), key, value)]
    return Form(
        "qa", ("patient_id", "form_date", "question_key", "answer"), tuple(rows),
        "patient_id", "question_key", "answer", time="form_date", value_holds_dates=True,
    )


_PANEL = (  # test, unit, mean, spread, places
    ("Sodium", "mmol/L", 139.0, 3.5, 0), ("Potassium", "mmol/L", 4.2, 0.45, 1), ("Chloride", "mmol/L", 103.0, 3.5, 0),
    ("Bicarbonate", "mmol/L", 25.0, 3.0, 0), ("Urea nitrogen", "mg/dL", 16.0, 7.0, 0), ("Creatinine", "mg/dL", 1.0, 0.35, 2),
    ("Glucose", "mg/dL", 112.0, 35.0, 0), ("White cell count", "10*3/uL", 7.6, 2.6, 1), ("Hemoglobin", "g/dL", 13.1, 1.9, 1),
    ("Platelet count", "10*3/uL", 245.0, 70.0, 0),
)
_TEST_FIRST = ("Vitamin", "Factor", "Anti", "Serum", "Urine", "Plasma", "Free", "Total", "Ionized", "Random")
_TEST_SECOND = (
    "B12", "D 25-OH", "VIII activity", "Xa level", "copper", "zinc", "osmolality", "protein", "calcium",
    "cortisol", "ferritin", "folate", "lactate", "ammonia", "magnesium", "phosphate", "lipase", "amylase",
    "troponin", "fibrinogen",
)


def lab_results(seed: int = 20261203) -> Form:
    """Form lab: patient, collection time, test, result, and the unit the test decides."""
    draw = random.Random(seed)
    names = [f"{first} {second}" for first in _TEST_FIRST for second in _TEST_SECOND]
    draw.shuffle(names)
    tails: "list[dict[str, object]]" = []
    for name in names[:180]:
        if draw.random() < 0.75:
            kind: "dict[str, object]" = {
                "kind": "number", "mid": round(draw.uniform(0.2, 600), 2), "places": draw.choice((0, 1, 2)),
                "unit": draw.choice(("mg/dL", "ng/mL", "U/L", "pg/mL", "umol/L", "%", "mOsm/kg")),
                "below": draw.random() < 0.2,
            }
        else:
            kind = {"kind": "qual", "unit": ""}
        kind["name"] = name
        tails += [kind]
    weights = _falling(len(tails), 1.15)
    rows: "list[tuple[str, ...]]" = []
    for place in range(PEOPLE):
        person = _person(place)
        draws = 1 + min(12, int(draw.expovariate(1 / 1.9)))
        start = datetime.datetime(2023, 3, 1) + datetime.timedelta(days=draw.randrange(600), hours=draw.choice((5, 6, 7)))
        own = {draw.choices(range(len(tails)), weights=weights)[0] for _each in range(int(draw.expovariate(1 / 1.3)))}
        for day in range(draws):
            at = (start + datetime.timedelta(days=day)).strftime("%Y-%m-%d %H:%M")
            made: "list[tuple[str, str, str]]" = []
            sodium = draw.gauss(139, 3.5)
            chloride = 103 + 0.6 * (sodium - 139) + draw.gauss(0, 2.8)
            if draw.random() < 0.9 or day == 0:
                made += [("Sodium", f"{sodium:.0f}", "mmol/L"), ("Chloride", f"{chloride:.0f}", "mmol/L")]
                for test, unit, mean, spread, places in _PANEL[1:7]:
                    if test == "Chloride":
                        continue
                    made += [(test, f"{max(0.01, draw.gauss(mean, spread)):.{places}f}", unit)]
            if draw.random() < 0.6:
                for test, unit, mean, spread, places in _PANEL[7:]:
                    made += [(test, f"{max(0.1, draw.gauss(mean, spread)):.{places}f}", unit)]
            for chosen in sorted(own):
                if draw.random() < 0.7:
                    tail = tails[chosen]
                    if tail["kind"] == "qual":
                        made += [(f"{tail['name']}", draw.choices(("Negative", "Positive"), weights=(5, 1))[0], "")]
                    elif tail["below"] and draw.random() < 0.3:
                        made += [(f"{tail['name']}", "<0.5", f"{tail['unit']}")]
                    else:
                        middle = float(f"{tail['mid']}")
                        made += [(f"{tail['name']}", f"{max(0.01, draw.gauss(middle, middle / 5)):.{tail['places']}f}", f"{tail['unit']}")]
            for test, value, unit in made:
                rows += [(person, at, test, value, unit)]
    return Form(
        "lab", ("patient_id", "collected_at", "test_name", "result_value", "unit"), tuple(rows),
        "patient_id", "test_name", "result_value", time="collected_at", unit="unit",
    )


def zoo_flow(n: int = 20000) -> Form:
    """Form zf: the zoo's own kind `values_typed_by_key` at the zoo's seed (`dates_in_disguise.flow_values`)."""
    import dates_in_disguise
    import health_zoo

    table = dates_in_disguise.table_named("flow_values")
    header, rows = dates_in_disguise.flow_values(n, health_zoo.seed_of(table))
    return Form(
        "zf", tuple(header), tuple(tuple(row) for row in rows),
        "record_id", "flow_key", "result_value", key_is_code=True, value_holds_dates=True,
    )


_PLACES_FIRST = (
    "Alder", "Brook", "Copper", "Dune", "Ember", "Fern", "Garnet", "Harbor", "Iris", "Juniper",
    "Kestrel", "Linden", "Marsh", "Nettle", "Onyx", "Poplar", "Quarry", "Rowan", "Sorrel", "Thistle",
    "Umber", "Vale", "Willow", "Yarrow", "Zephyr",
)
_PLACES_LAST = ("ford", "mere", "wick", "holm", "stead")
_GIVEN = ("Arlen", "Brisa", "Caddo", "Delphine", "Eskil", "Fiora", "Gunnar", "Hesper", "Ilse", "Jarek")
_FAMILY = ("Abernaut", "Brindlecombe", "Corvane", "Dellacroix", "Esterhal", "Fennimore", "Galloway", "Hartwick", "Ingleby", "Joskin")


def answers_with_identifiers(seed: int = 20261204) -> Form:
    """Form qp: a question-and-answer export whose answers include Safe Harbor identifiers (HIPAA first)."""
    draw = random.Random(seed)
    zips = [f"{61000 + 37 * place:05d}" for place in range(60)]
    cities = [f"{_PLACES_FIRST[place]}{_PLACES_LAST[place // 5]}" for place in range(25)]
    contacts = [f"{_GIVEN[place % 10]} {_FAMILY[(place * 3 + place // 10) % 10]}" for place in range(30)]
    words = {
        "tobacco_use": ("Current", "Former", "Never"),
        "walking_aid": ("None", "Cane", "Walker"),
        "meal_plan": ("Regular", "Diabetic", "Low salt"),
    }
    held: "dict[str, set[str]]" = {
        "home_zip5": set(), "city": set(), "emergency_contact": set(), "callback_phone": set(),
        "date_of_birth": set(), "age_in_years_over_89": set(), "record_number": set(),
    }
    rows: "list[tuple[str, ...]]" = []
    for place in range(PEOPLE):
        person = _person(place)
        born = datetime.date(1928, 1, 1) + datetime.timedelta(days=draw.randrange(29000))
        age = min(97, max(18, (datetime.date(2024, 6, 1) - born).days // 365))
        zip_code, city, contact = draw.choice(zips), draw.choice(cities), draw.choice(contacts)
        phone = f"(319) 555-{draw.randrange(10000):04d}"
        record = f"R{4000000 + 41 * place:07d}"
        birth = f"{born.month:02d}/{born.day:02d}/{born.year}"
        first = datetime.date(2023, 1, 1) + datetime.timedelta(days=draw.randrange(400))
        for each in range(1 + min(5, int(draw.expovariate(1 / 1.4)))):
            at = (first + datetime.timedelta(days=60 * each)).isoformat()
            made: "list[tuple[str, str]]" = []
            for key in sorted(words):
                made += [(key, draw.choice(words[key]))]
            made += [
                ("pain_now", f"{draw.randint(0, 10)}"),
                ("sleep_hours", f"{draw.gauss(6.8, 1.1):.1f}"),
                ("home_zip5", zip_code),
                ("city", city),
                ("emergency_contact", contact),
                ("callback_phone", phone),
                ("date_of_birth", birth),
                ("age_in_years", f"{age}"),
                ("record_number", record),
            ]
            for key, value in made:
                rows += [(person, at, key, value)]
            held["home_zip5"].add(zip_code)
            held["city"].add(city)
            held["emergency_contact"].add(contact)
            held["callback_phone"].add(phone)
            held["date_of_birth"].add(birth)
            held["record_number"].add(record)
            if age >= 90:
                held["age_in_years_over_89"].add(f"{age}")
    return Form(
        "qp", ("patient_id", "form_date", "question_key", "answer"), tuple(rows),
        "patient_id", "question_key", "answer", time="form_date", value_holds_dates=True,
        identifiers=tuple((key, tuple(sorted(held[key]))) for key in sorted(held)), age_keys=("age_in_years",),
    )


def all_forms() -> "tuple[Form, ...]":
    """The six forms, in the planning's order."""
    fs = recorded_items()
    return (fs, numbered_items(fs), question_answers(), lab_results(), zoo_flow(), answers_with_identifiers())


# THE FORMS OF LANE KV'S REPAIR 1 (the orchestrator's LANE KV RULINGS 3 (1) to
# (3)): a pool of one rare key, the identifier form with its question keys
# written as codes, and rare keys whose names hide a cue word or a name behind
# a character that prints nothing.

_CODED = (
    ("tobacco_use", "Q6101"), ("walking_aid", "Q6102"), ("meal_plan", "Q6103"), ("pain_now", "Q6104"),
    ("sleep_hours", "Q6105"), ("home_zip5", "Q6106"), ("city", "Q6107"), ("emergency_contact", "Q6108"),
    ("callback_phone", "Q6109"), ("date_of_birth", "Q6110"), ("age_in_years", "Q6111"), ("record_number", "Q6112"),
)


def coded_identifiers(seed: int = 20261204) -> Form:
    """Form qpc: form qp with its question keys written as codes (`Q6101` to `Q6112`), as the zoo's own question-and-answer kind writes them, and one more key, `Q6113`, holding the contact's family name alone (skeptic 1's item 2)."""
    base = answers_with_identifiers(seed)
    code = dict(_CODED)
    rows: "list[tuple[str, ...]]" = []
    surnames: "set[str]" = set()
    for row in base.rows:
        rows += [(row[0], row[1], code[row[2]], row[3])]
        if row[2] == "emergency_contact":
            family = row[3].split(" ")[-1]
            rows += [(row[0], row[1], "Q6113", family)]
            surnames.add(family)
    held = dict(base.identifiers)
    held["family_name"] = tuple(sorted(surnames))
    return Form(
        "qpc", base.header, tuple(rows), base.person, base.key, base.value, time=base.time, value_holds_dates=True,
        identifiers=tuple((key, held[key]) for key in sorted(held)), age_keys=("Q6111",),
    )


def small_pool(form: "Form | None" = None) -> Form:
    """Form sp: form fs with its long tail of rare keys set aside and ONE rare key in their place, `town_lived_in`, held by four people on twelve rows, every one a town (skeptic 1's item 1)."""
    base = recorded_items() if form is None else form
    rare = rare_keys(base)
    k = base.header.index(base.key)
    rows = [row for row in base.rows if row[k] not in rare]
    people: "list[str]" = []
    for row in rows:
        if row[0] not in people:
            people += [row[0]]
        if len(people) == 4:
            break
    for person in people:
        stamp = [row[1] for row in rows if row[0] == person][0]
        rows += [(person, stamp, "town_lived_in", "Alderford")] * 3
    return Form(
        "sp", base.header, tuple(rows), base.person, base.key, base.value, time=base.time, value_holds_dates=True,
        identifiers=(("small_pool_town", ("Alderford",)),),
    )


# Rare keys' names holding a cue word or a name broken by a character that
# prints nothing (U+200B, U+2060, U+00AD, U+FEFF), and names written alone.
_HIDDEN = (
    "Ride home with w\u200bife Tamsa Quorne",
    "Spoke to s\u2060on Oswin Ardane",
    "Seen by D\u00adr Pelleth",
    "H\u200balett Bravstane",
    "P\ufeffelleth, H",
)


def hidden_names(form: "Form | None" = None) -> Form:
    """Form hf: form fs with five of its rare keys renamed to texts whose cue word or name a character that prints nothing breaks (skeptic 1's item 3)."""
    base = recorded_items() if form is None else form
    rare = sorted(rare_keys(base))
    renamed = {rare[place * 7]: _HIDDEN[place] for place in range(len(_HIDDEN))}
    k = base.header.index(base.key)
    rows = tuple(
        tuple(renamed[row[k]] if place == k and row[k] in renamed else cell for place, cell in enumerate(row))
        for row in base.rows
    )
    return Form("hf", base.header, rows, base.person, base.key, base.value, time=base.time, value_holds_dates=True)


def csv_text(form: Form) -> str:
    """The form as a comma-separated file's text, every cell quoted only where it must be."""
    import csv
    import io

    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(form.header)
    writer.writerows(form.rows)
    return out.getvalue()
