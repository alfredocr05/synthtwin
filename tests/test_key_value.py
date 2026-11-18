"""Values typed by a key (lane KV, plan P4-D487): the reading, the names, the key blocks, the writer, the recount.

A long table's value column, whose kind and scale a key column decides,
is read as a KEYED PAIR and described key by key; a keyed key column's
rare keys are named after the person's `no`, both floors read by the
condition itself, through every screen of its road, all or none. Unit
cases on small invented tables (the library path, below the table floor:
a test device), a GENERATED check of the screens over thousands of key
names, each HIPAA case red on its mutant, and ONE case at the table floor
through the commands a person types. Every table here is invented
(`key_value_tables`), its names generic.
"""

from __future__ import annotations

import contextlib
import csv
import dataclasses
import io
import json
import math
import pathlib
import random

import pytest

import fixtures
import health_zoo_wide
import key_value_tables
from synthtwin import asking, canonical, chain, chain_rules, cli, contract, errors, generation, parsing, patient_rules, profile, reading, summary, taxonomy, twinstore, validation

FLOOR = 11


# -- a small long table (a test device: below the owner's table floor) ------


def _small_long(people: int = 160, seed: int = 31) -> "tuple[list[str], list[list[str]]]":
    """A small invented long table: person, key, value; numeric keys of their own scales, a word key, a clock key, a date key, a pulse of a person's own level and a tail of rare keys."""
    draw = random.Random(seed)
    header = ["person_id", "item_key", "item_value"]
    rows: "list[list[str]]" = []
    for place in range(people):
        person = f"Q{7000 + 3 * place}"
        level = draw.gauss(0, 6)
        for _visit in range(4):
            rows += [[person, "pulse", f"{max(40, round(draw.gauss(78 + level, 8)))}"]]
            rows += [[person, "temp_c", f"{draw.gauss(36.9, 0.4):.1f}"]]
            rows += [[person, "glucose_mg", f"{max(50, round(draw.gauss(140, 40)))}"]]
            rows += [[person, "airway", draw.choice(("Clear", "Wheeze", "Crackles"))]]
            if draw.random() < 0.5:
                rows += [[person, "bed_time", f"{draw.randrange(24):02d}:{draw.randrange(60):02d}"]]
        if draw.random() < 0.3:
            day = 1 + draw.randrange(27)
            rows += [[person, "line_placed_on", f"03/{day:02d}/2024"]]
        if place % 9 == 0:
            rows += [[person, f"tail_check_{place:03d}", f"{draw.randint(1, 9)}"]] * 3
    return header, rows


def _csv(header: "list[str]", rows: "list[list[str]]") -> str:
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return out.getvalue()


def _table(tmp_path: pathlib.Path, header: "list[str]", rows: "list[list[str]]", name: str = "long.csv") -> reading.Table:
    path = fixtures.write(tmp_path, name, _csv(header, rows))
    return reading.read_table(str(path), small_cell_floor=FLOOR)


def _described(
    table: reading.Table, kept: "list[str] | None" = None, **given: object
) -> "dict[str, object]":
    """The table described as the command describes a long table: the person declared, the Safe Harbor rules on, the keyed reading on unless ``kept`` is None."""
    return profile.build_document(
        table,
        taxonomy.Settings(small_cell_floor=FLOOR),
        ["person_id"],
        subjects=["person_id"],
        top_code=True,
        harbor_year=taxonomy.SAFE_HARBOR_REFERENCE_YEAR,
        keyed_kept=kept,
        **given,  # type: ignore[arg-type]
    )


def _block(document: "dict[str, object]", name: str) -> "dict[str, object]":
    blocks = document["columns"]
    assert isinstance(blocks, list)
    for block in blocks:
        if block["name"] == name:
            return block
    raise KeyError(name)


def _key_blocks(document: "dict[str, object]", name: str) -> "dict[str, dict[str, object]]":
    by_key = _block(document, name)["by_key"]
    assert isinstance(by_key, dict)
    return {f"{entry['key']}": entry["block"] for entry in by_key["key_blocks"]}


@contextlib.contextmanager
def _mutant(target: object, name: str, replacement: object):  # type: ignore[no-untyped-def]
    kept = getattr(target, name)
    setattr(target, name, replacement)
    try:
        yield
    finally:
        setattr(target, name, kept)


def _red(case: "object", target: object, name: str, replacement: object) -> None:
    """The case holds on the product and fails on its mutant."""
    case()  # type: ignore[operator]
    with _mutant(target, name, replacement), pytest.raises(AssertionError):
        case()  # type: ignore[operator]


# -- the reading --------------------------------------------------------------


def test_the_readings_of_a_value_cell() -> None:
    seen = {
        "82": "numbers", "-3.5": "numbers", "120/80": "pairs of numbers", "14:32": "clock times",
        "2:05 pm": "clock times", "03/14/2024": "dates", "2024-03": "dates", "2024-01-05 09:15": "dates",
        "Normal": "words", "Room air": "words", "Tolerating sips today": "texts", "Mark-012": "texts",
    }
    for cell, reading_word in seen.items():
        assert profile.KEYED_READING_WORDS[profile.keyed_value_reading(cell)] == reading_word, cell
    assert profile.keyed_value_reading("  ") == profile._READ_NONE


def test_the_scale_step_is_the_eighths_of_an_octave_read_exactly() -> None:
    assert profile.keyed_scale_step("0") == 0
    assert profile.keyed_scale_step("1") == 8
    assert profile.keyed_scale_step("-1") == 8
    assert profile.keyed_scale_step("3") == 16
    assert profile.keyed_scale_step("Normal") is None
    draw = random.Random(5)
    for _case in range(2000):
        value = draw.choice((draw.uniform(0, 2), draw.uniform(0, 300), draw.uniform(0, 1e6)))
        text = f"{value:.3f}"
        step = profile.keyed_scale_step(text)
        exact = 8 * math.log2(1 + float(text))
        assert step is not None
        # Whole numbers decide it; the float log agrees but at its own last bit.
        assert step <= exact + 1e-9 and step > exact - 1 - 1e-9, text


def test_a_long_table_reads_as_keyed_and_a_key_column_is_no_value_column(tmp_path: pathlib.Path) -> None:
    header, rows = _small_long()
    found: "list[profile.KeyedPair]" = []
    _described(_table(tmp_path, header, rows), [], keyed_found=found)
    assert [(pair.key, pair.value) for pair in found] == [("item_key", "item_value")]
    assert "numbers" in found[0].readings and "words" in found[0].readings
    # ...A UNIT BESIDE A TEST reads as a key of the test names, which are the
    # key of the results: the key column is no pair's value column.
    draw = random.Random(3)
    lab: "list[list[str]]" = []
    for place in range(150):
        for test, unit, middle in (("Na", "mmol/L", 139), ("K", "mmol/L", 4), ("Gluc", "mg/dL", 110), ("Hgb", "g/dL", 13)):
            for _draw in range(3):
                lab += [[f"Q{place}", test, f"{draw.gauss(middle, middle / 20):.1f}", unit]]
    found = []
    _described(_table(tmp_path, ["person_id", "test", "result", "unit"], lab, "lab.csv"), [], keyed_found=found)
    assert [(pair.key, pair.value) for pair in found] == [("test", "result")]


def test_a_key_of_few_levels_that_its_values_decide_is_their_dependent(tmp_path: pathlib.Path) -> None:
    draw = random.Random(4)
    rows: "list[list[str]]" = []
    for place in range(300):
        for _row in range(3):
            kind = draw.choice(("9", "10"))
            code = f"{draw.randint(100, 999)}.{draw.randint(0, 99):02d}" if kind == "9" else f"E{draw.randint(10, 99)}.{draw.randint(0, 9)}"
            rows += [[f"Q{place}", kind, code]]
    found: "list[profile.KeyedPair]" = []
    _described(_table(tmp_path, ["person_id", "code_type", "code"], rows), [], keyed_found=found)
    assert found == []


def test_a_table_with_no_long_pair_reads_nothing_and_none_reads_no_pair(tmp_path: pathlib.Path) -> None:
    draw = random.Random(8)
    rows = [[f"Q{place}", f"{draw.randint(20, 90)}", draw.choice(("F", "M")), f"{draw.gauss(70, 10):.1f}"] for place in range(800)]
    found: "list[profile.KeyedPair]" = []
    document = _described(_table(tmp_path, ["person_id", "years", "group", "amount"], rows), [], keyed_found=found)
    assert found == []
    assert not any("by_key" in block for block in document["columns"])  # type: ignore[union-attr]


def _pairs_as_first_built(
    table: reading.Table,
    blocks: "list[dict[str, object]]",
    absent: "list[tuple[str, ...]]",
    people: "list[str] | None",
    excluded: "frozenset[str]",
    held_in_people: "frozenset[str]",
    floor: int,
) -> "list[profile.KeyedPair]":
    """The reading as first built, every column passed under every key column: the census's reference."""
    names = [f"{block['name']}" for block in blocks]
    keys = []
    for place, block in enumerate(blocks):
        if names[place] in excluded or (block["role"] not in profile._KEYED_KEY_ROLES and names[place] not in held_in_people):
            continue
        cells = reading.column_values(table, place)
        levels = profile._key_levels(cells, frozenset(absent[place]))
        common = profile._common_keys(levels, people, floor)
        if len(common) < 2 or (people is not None and not profile._varies_within_a_person(levels, people)):
            continue
        if profile._reads_as_dates_or_clocks(levels, cells):
            continue
        keys += [(place, levels, common)]
    read = []
    for place, block in enumerate(blocks):
        if names[place] in excluded or block["role"] == taxonomy.ROLE_EMPTY:
            continue
        memo: "dict[str, int]" = {}
        scales: "dict[str, int | None]" = {}
        cells = reading.column_values(table, place)
        for key_place, levels, common in keys:
            if key_place != place:
                got = profile._reads_as_a_key(levels, common, cells, frozenset(absent[place]), memo, scales)
                if got is not None:
                    read += [profile.KeyedPair(names[key_place], names[place], common, got)]
    keyed = {pair.key for pair in read}
    found = []
    for place in range(len(names)):
        best = None
        for pair in read:
            if pair.value == names[place] and pair.value not in keyed and (best is None or len(pair.common) > len(best.common)):
                best = pair
        if best is not None:
            found += [best]
    return found


def _mixed_long(draw: random.Random, people: int) -> "tuple[list[str], list[list[str]]]":
    """A long table of generated keys, each of its own reading or a mix, beside label and number columns no key types."""
    kinds = ("number", "pair", "word", "clock", "date", "text", "mix")
    keys = [(f"k{place:02d}", draw.choice(kinds), draw.randint(2, 40)) for place in range(draw.randint(3, 14))]
    rows: "list[list[str]]" = []
    for person in range(people):
        for _row in range(draw.randint(2, 7)):
            key, kind, spread = draw.choice(keys)
            if kind == "mix":
                kind = draw.choice(kinds[:-1])
            value = {
                "number": f"{draw.gauss(50, spread):.1f}", "pair": f"{draw.randint(90, 160)}/{draw.randint(50, 99)}",
                "word": draw.choice(("Clear", "Moist", "Dry", "Warm", "Cool", "Pale", "Flushed")),
                "clock": f"{draw.randrange(24):02d}:{draw.randrange(60):02d}",
                "date": f"0{draw.randint(1, 9)}/{draw.randint(10, 28)}/2024",
                "text": draw.choice(("Tolerating sips", "Up in chair", "Sleeping now")) + f" {draw.choice(('am', 'pm'))}",
            }[kind]
            rows += [[f"Q{person}", key, value, draw.choice(("A", "B", "C")), f"{draw.randint(1, 4)}"]]
    return ["person_id", "item_key", "item_value", "ward", "tier"], rows


def test_the_census_reads_the_pairs_the_reading_as_first_built_reads(tmp_path: pathlib.Path) -> None:
    """EXACT (`profile._value_census`): on generated long tables and the invented forms, the pairs read with the census are the pairs every column passed under every key column reads."""
    compared = 0

    def both(*arguments: object) -> "list[profile.KeyedPair]":
        nonlocal compared
        made = _REAL_READ(*arguments)  # type: ignore[arg-type]
        assert made == _pairs_as_first_built(*arguments), [block["name"] for block in arguments[1]]  # type: ignore[arg-type, attr-defined, index]
        compared = compared + 1
        return made

    draw = random.Random(20261112)
    tables = [_mixed_long(draw, draw.choice((60, 150, 300))) for _table_ in range(12)]
    tables += [([("person_id" if name == form.person else name) for name in form.header], [list(row) for row in form.rows])
               for form in (key_value_tables.recorded_items(people=120), key_value_tables.lab_results(), key_value_tables.question_answers())]
    with _mutant(profile, "keyed_pairs_read", both):
        for place, (header, rows) in enumerate(tables):
            _described(_table(tmp_path, header, rows, f"t{place}.csv"), [])
    assert compared == len(tables)


_REAL_READ = profile.keyed_pairs_read


def _wide_labels(draw: random.Random) -> "tuple[list[str], list[list[str]]]":
    """A wide export of 40 questionnaire items, five words each, and a free-text comment, several rows a person."""
    header = ["person_id", *[f"item_{place:02d}" for place in range(40)], "comment"]
    rows = []
    for person in range(150):
        for _visit in range(3):
            rows += [[f"Q{person}", *[draw.choice(("Never", "Rarely", "Sometimes", "Often", "Always")) for _item in range(40)],
                      draw.choice(("ok", "fine", "tired"))]]
    return header, rows


def test_a_wide_table_of_labels_no_key_types_makes_no_pass_under_a_key(tmp_path: pathlib.Path) -> None:
    """The price (G4): a column no key could type is read once and under no key (40 items made 1,640 passes)."""
    header, rows = _wide_labels(random.Random(5))
    table = _table(tmp_path, header, rows, "wide.csv")

    def passes() -> None:
        made = 0
        real = profile._reads_as_a_key

        def counted(*arguments: object) -> object:
            nonlocal made
            made = made + 1
            return real(*arguments)  # type: ignore[arg-type]

        found: "list[profile.KeyedPair]" = []
        with _mutant(profile, "_reads_as_a_key", counted):
            _described(table, [], keyed_found=found)
        assert found == [] and made == 0, made

    _red(passes, profile, "_value_census", lambda cells, absent, memo: len(cells))


def test_the_library_reads_no_pair_unless_asked_and_keep_reads_none(tmp_path: pathlib.Path) -> None:
    header, rows = _small_long()
    table = _table(tmp_path, header, rows)
    plain = _described(table, None)
    assert "by_key" not in _block(plain, "item_value") and "keyed" not in _block(plain, "item_key")
    kept = _described(table, ["item_value"])
    assert canonical.serialize(kept) == canonical.serialize(plain)


# -- the key blocks ---------------------------------------------------------


def test_the_pool_of_rare_keys_publishes_no_place_a_few_rare_keys_write(tmp_path: pathlib.Path) -> None:
    """K6, HIPAA first: twenty rare questions each answered by its own word (`Mark-020` to `Mark-039`, three people each) publish no place of those words, so no stand-in is drawn in them."""
    draw = random.Random(11)
    rows: "list[list[str]]" = []
    for person in range(400):
        for _visit in range(3):
            rows += [[f"Q{person}", "pulse", f"{draw.randint(50, 120)}"]]
            rows += [[f"Q{person}", "resp_rate", f"{draw.randint(8, 40)}"]]
            rows += [[f"Q{person}", "pain_score", f"{draw.randint(0, 10)}"]]
            rows += [[f"Q{person}", "mood", draw.choice(("calm", "low", "upbeat", "tense", "flat", "bright"))]]
            rows += [[f"Q{person}", "gait", draw.choice(("steady", "shuffling", "assisted", "unsteady", "brisk"))]]
            rows += [[f"Q{person}", "skin", draw.choice(("warm", "cool", "pale", "moist", "dry"))]]
        if person < 60:
            rows += [[f"Q{person}", f"rare_question_{person // 3:02d}", f"Mark-0{20 + person // 3:02d}"]]
    table = _table(tmp_path, ["person_id", "item_key", "item_value"], rows)

    def unplaced() -> None:
        # ...after the value column's `no`: the pool is counted in people (its
        # sixty people each on one row), and unanswered it is held whole.
        assert _block(_described(table, []), "item_value")["by_key"]["pool"]["role"] == taxonomy.ROLE_IDENTIFIER  # type: ignore[index]
        pool = _block(_described(table, [], safe_harbor_no=["item_value"]), "item_value")["by_key"]["pool"]  # type: ignore[index]
        assert isinstance(pool, dict) and "shape_forms" in pool
        assert "shape_form_places" not in pool and "shape_form_places" not in (pool.get("labels") or {})

    _red(unplaced, profile, "_without_the_places", lambda block: block)


def test_each_common_key_is_described_as_a_column_named_by_the_key(tmp_path: pathlib.Path) -> None:
    header, rows = _small_long()
    document = _described(_table(tmp_path, header, rows), [], safe_harbor_no=["item_value"], dated_values_no=["item_value"])
    blocks = _key_blocks(document, "item_value")
    assert sorted(blocks) == ["airway", "bed_time", "glucose_mg", "line_placed_on", "pulse", "temp_c"]
    assert blocks["pulse"]["name"] == "pulse" and blocks["pulse"]["role"] in (taxonomy.ROLE_COUNT, taxonomy.ROLE_CONTINUOUS)
    assert blocks["airway"]["role"] == taxonomy.ROLE_CATEGORICAL
    assert blocks["bed_time"]["role"] == taxonomy.ROLE_CLOCK
    assert _block(document, "item_key")["keyed"] == "item_value"
    by_key = _block(document, "item_value")["by_key"]
    assert isinstance(by_key, dict) and by_key["key"] == "item_key" and "pool" in by_key
    # ...each block holds exactly its key's rows (KV2), the pool the pooled rows (KV3).
    levels = {f"{entry['label']}": entry["count"] for entry in _block(document, "item_key")["levels"]}  # type: ignore[union-attr]
    for label, block in blocks.items():
        assert block["n_present"] + block["n_missing"] == levels[label]  # type: ignore[operator]
    pool = by_key["pool"]
    assert pool["n_present"] + pool["n_missing"] == _block(document, "item_key")["suppressed_rows"]  # type: ignore[index, operator]
    # ...and the value column's own block holds the rows of no key: none.
    assert _block(document, "item_value")["n_present"] == 0
    # The summary says so: the value column's counts read the keyed rows as
    # blank, the six measurements are described each as a column, and the
    # key column says which column its keys type.
    said = summary.render(document, "Read as UTF-8.")
    assert "read as blank every row on which the column item_key names a measurement" in said
    assert "6 measurements held by 11 people or more are described each as a column of its name" in said
    assert "which measurement each row of the column item_value holds" in said


def test_the_value_columns_answers_govern_its_key_blocks(tmp_path: pathlib.Path) -> None:
    header, rows = _small_long()
    table = _table(tmp_path, header, rows)
    # Unanswered: the dates block is held (the question about dates is open)...
    open_question = _key_blocks(_described(table, []), "item_value")
    assert open_question["line_placed_on"]["role"] == taxonomy.ROLE_IDENTIFIER
    # ...`no` to the question about dates frees it, and numbers are described either way.
    answered = _key_blocks(_described(table, [], dated_values_no=["item_value"]), "item_value")
    assert answered["line_placed_on"]["role"] != taxonomy.ROLE_IDENTIFIER
    assert open_question["pulse"]["role"] == answered["pulse"]["role"] != taxonomy.ROLE_IDENTIFIER


def test_each_question_put_to_the_value_column_frees_what_its_words_say(tmp_path: pathlib.Path) -> None:
    # A key of free text joins the small long table: a listed block.
    draw = random.Random(5)
    header, rows = _small_long()
    words = (
        "settled", "restless", "asked", "for", "water", "walked", "slept", "well", "pain", "eased",
        "the", "patient", "after", "dinner", "and", "before", "rounds",
    )
    for place in range(160):
        person = f"Q{7000 + 3 * place}"
        for _note in range(4):
            rows += [[person, "shift_note", " ".join(draw.choice(words) for _word in range(14)) + "."]]
        # ...and a key of words some of which one person holds on twelve rows.
        if place % 40 == 0:
            rows += [[person, "mood_word", f"Mood{place:03d}"]] * 12
        else:
            rows += [[person, "mood_word", draw.choice(("Calm", "Anxious", "Tearful"))] for _each in range(3)]
    table = _table(tmp_path, header, rows)
    # Unanswered, the free text, the dates and the words few people hold are held...
    held = _key_blocks(_described(table, []), "item_value")
    assert held["shift_note"]["role"] == held["line_placed_on"]["role"] == taxonomy.ROLE_IDENTIFIER
    assert held["mood_word"]["role"] == taxonomy.ROLE_IDENTIFIER
    # ...`no` to the question about values that read as dates frees them, as
    # its words (the Safe Harbor rule's) say when it carries the keyed clause,
    # the words few people hold pooled in people...
    freed = _key_blocks(_described(table, [], dated_values_no=["item_value"]), "item_value")
    assert freed["shift_note"]["role"] != taxonomy.ROLE_IDENTIFIER
    assert freed["line_placed_on"]["role"] != taxonomy.ROLE_IDENTIFIER
    assert "pool_in_people" in freed["mood_word"]
    # ...and `no` to the Safe Harbor question frees the free text while the
    # dates wait for their own question, which holds them while it is open.
    waiting = _key_blocks(
        _described(table, [], safe_harbor_no=["item_value"], dated_held=("item_value",)), "item_value"
    )
    assert waiting["shift_note"]["role"] != taxonomy.ROLE_IDENTIFIER
    assert waiting["line_placed_on"]["role"] == taxonomy.ROLE_IDENTIFIER
    assert "pool_in_people" in waiting["mood_word"]


def _identifier_answers(people: int = 220, seed: int = 41) -> "tuple[list[str], list[list[str]], dict[str, set[str]]]":
    """A small question-and-answer table whose answers include Safe Harbor identifiers, and each identifier key's values."""
    draw = random.Random(seed)
    cities = ["Alderford", "Brookmere", "Copperwick", "Dunholm", "Emberstead"]
    contacts = ["Arlen Corvane", "Brisa Hartwick", "Caddo Ingleby", "Delphine Joskin", "Eskil Abernaut"]
    held: "dict[str, set[str]]" = {"city": set(), "emergency_contact": set(), "age_in_years": set(), "home_zip5": set()}
    rows: "list[list[str]]" = []
    for place in range(people):
        person = f"Q{9100 + 7 * place}"
        age = draw.choice((92, 94, 95)) if place % 10 == 0 else draw.randint(30, 80)
        city, contact, zip_code = draw.choice(cities), draw.choice(contacts), f"{52000 + 37 * draw.randrange(8):05d}"
        for _form in range(3):
            rows += [[person, "pain_now", f"{draw.randint(0, 10)}"], [person, "sleep_hours", f"{draw.gauss(7, 1):.1f}"]]
            rows += [[person, "tobacco_use", draw.choice(("Current", "Former", "Never"))]]
            rows += [[person, "city", city], [person, "emergency_contact", contact]]
            rows += [[person, "age_in_years", f"{age}"], [person, "home_zip5", zip_code]]
        held["city"].add(city)
        held["emergency_contact"].add(contact)
        held["home_zip5"].add(zip_code)
        if age >= 90:
            held["age_in_years"].add(f"{age}")
    return ["person_id", "question_key", "answer"], rows, held


def _leaves(node: object, found: "set[str]") -> "set[str]":
    if isinstance(node, str):
        found.add(node)
    elif isinstance(node, bool):
        pass
    elif isinstance(node, int):
        found.add(f"{node}")
    elif isinstance(node, dict):
        for key in node:
            found.add(f"{key}")
            _leaves(node[key], found)
    elif isinstance(node, list):
        for item in node:
            _leaves(item, found)
    return found


def test_a_key_block_meets_every_safe_harbor_rule_its_name_brings(tmp_path: pathlib.Path) -> None:
    header, rows, held = _identifier_answers()
    table = _table(tmp_path, header, rows)
    for answers in ({}, {"safe_harbor_no": ["answer"]}):
        document = _described(table, [], **answers)
        blocks = _key_blocks(document, "answer")
        published = _leaves(_block(document, "answer"), set())
        # A city and a ZIP code are held by their key's name, whatever the answer;
        # ages past 89 are read as 90 by the key's name.
        assert blocks["city"]["role"] == taxonomy.ROLE_IDENTIFIER
        assert blocks["home_zip5"]["role"] == taxonomy.ROLE_IDENTIFIER
        assert "top_coded" in blocks["age_in_years"]
        assert not (published & (held["city"] | held["home_zip5"] | held["age_in_years"]))
        # ...persons' names: lane CZ-F's reader reads the block's levels as
        # names, so the block is held whatever is answered: a careless `no`
        # publishes no more than the column-wide reading held.
        assert blocks["emergency_contact"]["role"] == taxonomy.ROLE_IDENTIFIER
        assert not (published & held["emergency_contact"])


def _keyed_names_pass_mutant_identifier_words(names: "tuple[str, ...]", role: str, code: bool, comma: bool) -> bool:
    """MUTANT: lane CZ-E's identifier words not read."""
    with _mutant(taxonomy, "identifier_words_form", lambda text, dates=True, scores=frozenset(): ""):
        return _REAL_PASS(names, role, code, comma)


def _keyed_names_pass_mutant_persons_names(names: "tuple[str, ...]", role: str, code: bool, comma: bool) -> bool:
    """MUTANT: lane CZ-F's persons' names not read."""
    with _mutant(taxonomy, "a_persons_name", lambda text: False):
        return _REAL_PASS(names, role, code, comma)


def _keyed_names_pass_mutant_no_net(names: "tuple[str, ...]", role: str, code: bool, comma: bool) -> bool:
    """MUTANT: path (iii)'s net not read on a long tail or a declared code."""
    with _mutant(taxonomy, "passes_the_word_screen", lambda word, counting_words=True, counting_figures=True: True):
        return _REAL_PASS(names, role, code, comma)


_REAL_PASS = profile.keyed_names_pass


# -- the names: a GENERATED check of the screens at the unit level ------------

_GIVEN = ("Halett", "Mirela", "Oswin", "Tamsa", "Corlen", "Beatrix", "Jovan", "Saffi", "Kukun", "Fena")
_FAMILY = ("Bravstane", "Pelleth", "Quorne", "Ardane", "Tolliver", "Velegin", "Okafor", "Cassell", "Lindqvist", "Varga")
_OPENINGS = ("Was the visit with", "Called", "Seen by", "Spoke to", "Left a message for", "Ride home with")
_CLOSINGS = ("today", "about results", "on the ward", "before discharge", "", "again")


def _identifier_element(family: str, draw: random.Random) -> str:
    """One invented identifier element of one family, as a key's name could hold it."""
    given, surname = draw.choice(_GIVEN), draw.choice(_FAMILY)
    figures = lambda count: "".join(draw.choice("0123456789") for _ in range(count))  # noqa: E731
    month, day, year = draw.randint(1, 12), draw.randint(13, 28), draw.randint(1931, 2024)
    if family == "a title and a name":
        return f"{draw.choice(('Dr.', 'Dr', 'Mrs.', 'Mr', 'Ms.', 'Prof.'))} {surname}"
    if family == "a person's name":
        return f"{given} {surname}"
    if family == "a name family first":
        return f"{surname}, {given[0]}"
    if family == "a relative and a name":
        return f"{draw.choice(('son', 'daughter', 'wife', 'husband', 'mother'))} {given} {surname}"
    if family == "a date in figures":
        return draw.choice((f"{month:02d}/{day:02d}/{year}", f"{year}-{month:02d}-{day:02d}", f"{day}.{month}.{year}", f"{month}/{day}"))
    if family == "a date with a month's name":
        return draw.choice((f"{draw.choice(('Mar', 'June', 'Sept', 'Dec'))} {day} {year}", f"{day}-MAR-{year}", f"{day} March"))
    if family == "an age past 89":
        age = draw.randint(90, 115)
        return draw.choice((f"age {age}", f"aged {age}", f"{age} years old", f"{age}+", f"~{age}"))
    if family == "a telephone":
        return draw.choice((f"({figures(3)}) {figures(3)}-{figures(4)}", f"{figures(3)}-{figures(3)}-{figures(4)}", f"+44 20 {figures(4)} {figures(4)}"))
    if family == "a record number":
        return draw.choice((f"record {figures(7)}", f"acct {figures(8)}", f"REC{figures(7)}", f"#{figures(6)}"))
    if family == "an e-mail or web address":
        return draw.choice((f"{surname.lower()}@example.org", f"https://example.org/p/{figures(6)}", f"www.example.org/{surname.lower()}"))
    if family == "a network address":
        return f"{draw.randint(1, 254)}.{draw.randint(0, 254)}.{draw.randint(0, 254)}.{draw.randint(1, 254)}"
    if family == "a street address":
        return f"{draw.randint(10, 9999)} {surname} {draw.choice(('St', 'Ave', 'Rd', 'Lane'))}"
    raise KeyError(family)


_ELEMENT_FAMILIES = (
    "a title and a name", "a person's name", "a name family first", "a relative and a name",
    "a date in figures", "a date with a month's name", "an age past 89", "a telephone", "a record number",
    "an e-mail or web address", "a network address", "a street address",
)


def _key_name(family: str, draw: random.Random, space: str = " ") -> str:
    """A question text of 3 to 12 words holding one identifier element, its words joined by ``space``."""
    words = draw.choice(_OPENINGS).split() + _identifier_element(family, draw).split() + draw.choice(_CLOSINGS).split()
    while len(words) < 3:
        words += ["please"]
    return space.join(words[:12])


def _spaces() -> "list[str]":
    """Every character of the product's one definition of a space (`taxonomy._SCREEN_SPACE_RANGES`), the astral ones among them."""
    found: "list[str]" = []
    for low, high in taxonomy._SCREEN_SPACE_RANGES:
        for code in range(low, high + 1):
            if 0xD800 <= code <= 0xDFFF:
                continue
            found += [chr(code)]
    return found


_ORDINARY = ("pulse_rate", "temperature_c", "pain_score", "Factor VIII activity", "Vitamin B12", "Anti Xa level", "bed_check_state")


def _screened_anywhere(name: str) -> bool:
    """Whether ANY screen the roads use refuses the name on its own (the names the check counts)."""
    return (
        bool(taxonomy.identifier_words_form(name))
        or taxonomy.a_persons_name(name)
        or not taxonomy.passes_the_word_screen(name, False)
        or not taxonomy._names_under(taxonomy.HELD_BACK_NAMED_ANSWERED, (name,), False, True, True)
        or not taxonomy._names_under(taxonomy.HELD_BACK_NAMED_ANSWERED, (name,), False, True, False)
    )


def _generated_key_names() -> "list[tuple[str, str]]":
    draw = random.Random(20261112)
    spaces = _spaces()
    found: "list[tuple[str, str]]" = []
    for family in _ELEMENT_FAMILIES:
        for _case in range(120):
            found += [(family, _key_name(family, draw))]
        for space in spaces:
            found += [(family, _key_name(family, draw, space))]
            found += [(family, space + _key_name(family, draw) + space)]
    return found


_GENERATED = _generated_key_names()


def _no_screened_name_is_named() -> None:
    passing = (
        tuple(_ORDINARY),
    )
    for ordinary in passing:
        assert profile.keyed_names_pass(ordinary, taxonomy.ROLE_CATEGORICAL, False, False)
    caught: "dict[str, int]" = {family: 0 for family in _ELEMENT_FAMILIES}
    total: "dict[str, int]" = {family: 0 for family in _ELEMENT_FAMILIES}
    for family, name in _GENERATED:
        refused_alone = _screened_anywhere(name)
        for role, code in ((taxonomy.ROLE_CATEGORICAL, False), (taxonomy.ROLE_LONG_TAIL, False), (taxonomy.ROLE_CATEGORICAL, True)):
            named = profile.keyed_names_pass(_ORDINARY + (name,), role, code, False)
            # A name a screen reads is never named, ALL OR NONE: the whole pool stays unnamed.
            if refused_alone:
                assert not named, (family, repr(name), role, code)
        caught[family] = caught[family] + (1 if refused_alone else 0)
        total[family] = total[family] + 1
    # EVERY FAMILY IS WHOLLY REFUSED, every character of the one definition of
    # a space in every position, save ONE stated limit: a person's given and
    # family name inside a question text with no title, no relative's word
    # and no cue (`Was the visit with Saffi Cassell today`) is read by no
    # screen -- lane CZ-F's reader reads a name written whole, and any two
    # words in capitals as one (`Heart Rate` too), so no shape tells it from
    # a measurement's name: 943 of the family's 972 texts are named on some
    # road when probed on the lane's head (P4-D487's limit (l), lane CODES-2's
    # limit (a), for the owner's veto). The family is generated so that its
    # count is read, and each other family is held to all of its texts.
    for family in _ELEMENT_FAMILIES:
        if family != "a person's name":
            assert caught[family] == total[family], (family, caught[family], total[family])


def test_no_name_a_screen_reads_is_named_on_any_road_all_or_none() -> None:
    _red(_no_screened_name_is_named, profile, "keyed_names_pass", _keyed_names_pass_mutant_identifier_words)


def test_the_persons_names_reader_and_the_net_are_read_on_every_road() -> None:
    def persons() -> None:
        # Names only lane CZ-F's reader reads (no other screen refuses them).
        for name in ("Halett Bravstane", "Mirela Okafor", "Tamsa Ardane Velegin"):
            assert not profile.keyed_names_pass(_ORDINARY + (name,), taxonomy.ROLE_LONG_TAIL, True, False), name

    _red(persons, profile, "keyed_names_pass", _keyed_names_pass_mutant_persons_names)

    def net() -> None:
        # A street address only path (iii)'s net reads on the code's road.
        for name in ("Lives at 258 Elm St", "Stays at 12 Cedar Lane"):
            assert not profile.keyed_names_pass(_ORDINARY + (name,), taxonomy.ROLE_LONG_TAIL, False, False), name

    _red(net, profile, "keyed_names_pass", _keyed_names_pass_mutant_no_net)


def test_ordinary_test_and_question_names_stay_nameable_and_bare_numbers_go_path_i() -> None:
    assert profile.keyed_names_pass(_ORDINARY, taxonomy.ROLE_CATEGORICAL, False, False)
    numbers = tuple(f"{410000 + 13 * place}" for place in range(40))
    # Six figures can write a date (`410104`, 4 January 1941 as YYMMDD): lane
    # CZ-E reads it, and one such key leaves the whole pool unnamed (stated).
    dated = [name for name in numbers if taxonomy.identifier_words_form(name)]
    assert dated and not profile.keyed_names_pass(numbers, taxonomy.ROLE_CATEGORICAL, True, False)
    assert profile.keyed_names_pass(tuple(name for name in numbers if name not in dated), taxonomy.ROLE_CATEGORICAL, True, False)
    # A flow key's code shape is named on path (i); path (iii) names no code holding a run of five figures.
    assert profile.keyed_names_pass(tuple(f"F{place:05d}" for place in range(40)), taxonomy.ROLE_LONG_TAIL, True, False)
    assert not profile.keyed_names_pass(tuple(f"F{place:05d}" for place in range(40)), taxonomy.ROLE_CATEGORICAL, False, False)
    assert not profile.keyed_names_pass((), taxonomy.ROLE_CATEGORICAL, False, False)


def test_both_floors_and_rule_u_are_read_by_the_condition_itself() -> None:
    def case() -> None:
        assert profile.keyed_names_released(20000, 1000, True, True)
        assert not profile.keyed_names_released(19999, 1000, True, True)
        assert not profile.keyed_names_released(20000, 999, True, True)
        assert not profile.keyed_names_released(20000, 1000, False, True)
        assert not profile.keyed_names_released(20000, 1000, True, False)

    _red(case, parsing, "TABLE_PEOPLE_FLOOR", 0)


def test_a_small_table_names_no_rare_key_whatever_is_answered(tmp_path: pathlib.Path) -> None:
    header, rows = _small_long()
    document = _described(_table(tmp_path, header, rows), [], safe_harbor_no=["item_key"])
    assert "held_back_names" not in _block(document, "item_key")


# -- the loader ----------------------------------------------------------------


def _loaded(tmp_path: pathlib.Path, document: "dict[str, object]") -> contract.Profile:
    return contract.load_profile(str(fixtures.write_profile(tmp_path, "keyed-profile.json", document)))


def _refused(tmp_path: pathlib.Path, document: "dict[str, object]", rule: str) -> None:
    with pytest.raises(errors.ProfileError) as refusal:
        _loaded(tmp_path, document)
    assert contract.INVARIANTS[rule] in f"{refusal.value}"


@pytest.fixture(scope="module")
def keyed_document(tmp_path_factory: pytest.TempPathFactory) -> "dict[str, object]":
    folder = tmp_path_factory.mktemp("keyed")
    header, rows = _small_long()
    return _described(_table(folder, header, rows), [], safe_harbor_no=["item_value"], dated_values_no=["item_value"])


def test_a_keyed_description_loads_and_its_blocks_owe_the_key_column(tmp_path: pathlib.Path, keyed_document: "dict[str, object]") -> None:
    loaded = _loaded(tmp_path, keyed_document)
    value = [column for column in loaded.columns if column.name == "item_value"][0]
    key = [column for column in loaded.columns if column.name == "item_key"][0]
    assert value.keyed_by == "item_key" and key.keyed == "item_value"
    assert [label for label, _block in value.key_blocks] == sorted(label for label, _block in value.key_blocks)
    assert value.key_pool is not None
    broken = json.loads(json.dumps(keyed_document))
    _block(broken, "item_key").pop("keyed")
    _refused(tmp_path, broken, "KV1")
    broken = json.loads(json.dumps(keyed_document))
    entry = _block(broken, "item_value")["by_key"]["key_blocks"][-1]  # type: ignore[index]
    entry["key"] = "zzzz not a key"
    _refused(tmp_path, broken, "KV2")
    broken = json.loads(json.dumps(keyed_document))
    _block(broken, "item_value")["by_key"].pop("pool")  # type: ignore[union-attr]
    _refused(tmp_path, broken, "KV3")


def test_the_chain_and_the_patient_layer_read_a_keyed_value_column_as_a_row_column(tmp_path: pathlib.Path, keyed_document: "dict[str, object]") -> None:
    # THE TWO GUARDS: the chain's reason `keyed` (4.6b.1), and the patient
    # layer, which asks it, classing the value column ineligible -- a row
    # column, never an own-mean or derived-column source -- while its key
    # column stays a candidate.
    assert "keyed" in chain_rules.INELIGIBLE_REASONS
    assert chain.ineligible_reason(_block(keyed_document, "item_value"), False, False, set()) == "keyed"
    assert chain.ineligible_reason(_block(keyed_document, "item_key"), False, False, set()) is None
    header, rows = _small_long()
    table = _table(tmp_path, header, rows)
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=FLOOR), person_columns=("person_id",))
    document = profile.build_document(
        table, settings, ["person_id"], subjects=["person_id"], top_code=True,
        harbor_year=taxonomy.SAFE_HARBOR_REFERENCE_YEAR, keyed_kept=[],
        safe_harbor_no=["item_value"], dated_values_no=["item_value"],
    )
    chained = chain.describe(
        table, document, settings, chain.ChainSwitch("long", bytes(range(32)), rows_per_person=chain.ROWS_PERSON)
    )
    assert chained.grain is not None
    classes = {f"{entry['column']}": entry["class"] for entry in chained.grain["classes"]}  # type: ignore[union-attr]
    assert classes["item_value"] == patient_rules.CLASS_INELIGIBLE
    assert classes["item_key"] != patient_rules.CLASS_INELIGIBLE


# -- the writer and the recount ------------------------------------------------


def test_the_layout_takes_each_rows_value_from_its_keys_block() -> None:
    written, short = generation.keyed_value_column(
        ["a", "B", "", "zz", "a", "NA", "b"],
        ("a", "b"),
        frozenset({"NA"}),
        ["", "own-1", "", "", "", "", ""],
        [["a1", "a2"], ["b1", "b2"]],
        ["pool-1"],
    )
    assert written == ["a1", "b1", "own-1", "pool-1", "a2", "", "b2"] and short == 0
    _written, short = generation.keyed_value_column(["a", "a", "a"], ("a",), frozenset(), [], [["a1"]], [])
    assert short == 2
    # ...an all-empty record the arrangement placed is written blank and takes
    # no own cell, which goes to the next row holding no key (repair 1).
    written, short = generation.keyed_value_column(
        ["a", "", "", "b"], ("a", "b"), frozenset(), ["own-1", "", "", ""], [["a1"], ["b1"]], [], [False, True, False, False]
    )
    assert written == ["a1", "", "own-1", "b1"] and short == 0


def _oracle() -> object:
    """The generation oracle, `tools/reference/make_generation_reference_vectors.py`, loaded once (A-P4-59)."""
    import importlib.util

    place = pathlib.Path(__file__).resolve().parents[1] / "tools" / "reference" / "make_generation_reference_vectors.py"
    spec = importlib.util.spec_from_file_location("oracle_keyed", place)
    assert spec is not None and spec.loader is not None
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
    return oracle


def test_the_oracle_lays_the_rows_out_as_the_writer_does() -> None:
    oracle = _oracle()
    draw = random.Random(9)
    labels = ("a", "b", "c")
    for _case in range(200):
        keys = [draw.choice(("a", "B", "c", "", "NA", "rare1", "rare2")) for _row in range(30)]
        own = [draw.choice(("", "x1", "x2")) for _row in range(30)]
        blocks = [[f"{label}{place}" for place in range(draw.randint(0, 12))] for label in labels]
        pool = [f"p{place}" for place in range(draw.randint(0, 6))]
        empty = None if draw.random() < 0.5 else [draw.random() < 0.2 and keys[row] in ("", "NA") for row in range(30)]
        product = generation.keyed_value_column(keys, labels, frozenset({"NA"}), own, blocks, pool, empty)
        assert oracle.keyed_value_cells(keys, labels, {"NA"}, own, blocks, pool, empty) == product


def test_the_twin_writes_each_keys_values_from_its_own_block_and_validates(tmp_path: pathlib.Path, keyed_document: "dict[str, object]") -> None:
    loaded = _loaded(tmp_path, keyed_document)
    twin = generation.generate_held(loaded, 7)
    names = list(twin.names)
    cells = [twinstore.column_cells(column) for column in twin.held_columns]
    keys, values = cells[names.index("item_key")], cells[names.index("item_value")]
    pulses = [float(value) for key, value in zip(keys, values) if key == "pulse"]
    assert pulses and min(pulses) >= 40 and max(pulses) <= 120
    airway = {value for key, value in zip(keys, values) if key == "airway"}
    assert airway <= {"Clear", "Wheeze", "Crackles"}
    # ...and the twin meets its description, each key block recounted (V19).
    path = tmp_path / "twin.csv"
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(names)
    writer.writerows(zip(*cells))
    path.write_text(out.getvalue(), encoding="utf-8", newline="\n")
    outcome = validation.measure(loaded, str(path))
    lines = [check for check in outcome.checks if check.fact == "label.by_key"]
    assert lines and all(check.verdict == validation.HELD for check in lines)
    assert not [check for check in outcome.checks if check.verdict == validation.MISSED]


# -- question Q-KEYED ------------------------------------------------------------


def test_question_q_keyed_names_no_value_and_its_answers_are_kept() -> None:
    document: "dict[str, object]" = {"columns": [{"name": "item_key", "role": "categorical"}, {"name": "item_value", "role": "empty"}]}
    asked = asking.keyed_questions(document, [("item_key", "item_value", 36, ("numbers", "words"))], (), FLOOR)
    assert len(asked) == 1 and asked[0].reason == asking.BECAUSE_KEYED and asked[0].taken == asking.ANSWER_KEYED
    assert [choice.answer for choice in asked[0].choices] == [asking.ANSWER_KEYED, asking.ANSWER_KEEP]
    assert asking.keyed_questions(document, [("item_key", "item_value", 36, ("numbers",))], ("item_value",), FLOOR) == []
    entries = [
        {"column": "item_value", "your_answer": answer, "answers_you_can_give": [{"answer": "keyed"}, {"answer": "keep"}]}
        for answer in ("keyed",)
    ]
    read = asking.answers_in({"asked": entries, "checklist": {"columns": []}}, "questions.json")
    assert read.values_keyed == ("item_value",) and read.values_kept_whole == ()
    entries[0]["your_answer"] = "keep"
    read = asking.answers_in({"asked": entries, "checklist": {"columns": []}}, "questions.json")
    assert read.values_kept_whole == ("item_value",)
    kept = asking.answered_before(asking.Given(columns=("item_value",), values_kept_whole=("item_value",)))
    assert [entry["your_answer"] for entry in kept] == ["keep"]


# -- repair 1 (the orchestrator's LANE KV RULINGS 2 to 4): each hold, rule and
# reading pinned by a case red on its mutant ---------------------------------

# The functions each mutant below wraps, as shipped (read with `getattr` so that
# the cases run, and fail on their own assertions, on a tree that lacks one).
_REAL_BUILD = profile.build_document
_REAL_NAMES_OF = getattr(profile, "keyed_names_of", None)
_REAL_ASKED = profile._asked_as_an_identifier
_REAL_HELD = getattr(profile, "_keyed_value_held", None)
_REAL_COMMON = profile._common_keys
_REAL_WORDS = generation._keyed_word_counts
_REAL_COUNT_CHECK = validation._key_count_check


def _floor_lowered(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE OWNER'S TABLE FLOOR LOWERED to the fixture's size while it is described: naming is a command's rule at the floor, so the floor is lowered for the case, a test device (LANE I4m RULINGS 18 (4)); K-HZ-37's driver reads the same rules at 20,000 rows and 1,000 people."""
    monkeypatch.setattr(parsing, "TABLE_ROW_FLOOR", 1000)
    monkeypatch.setattr(parsing, "TABLE_PEOPLE_FLOOR", 50)


def _long(tmp_path: pathlib.Path, name: str, rows: "list[list[str]]", value: str = "item_value") -> reading.Table:
    return _table(tmp_path, ["person_id", "item_key", value], rows, f"{name}.csv")


def _pairs(table: reading.Table, **given: object) -> "list[tuple[str, str]]":
    """The pairs the describe reads, the person declared where the table holds `person_id`, no column declared where not."""
    found: "list[profile.KeyedPair]" = []
    if "person_id" in table.column_names:
        _described(table, [], keyed_found=found, **given)
    else:
        profile.build_document(
            table, taxonomy.Settings(small_cell_floor=FLOOR), [], top_code=True,
            harbor_year=taxonomy.SAFE_HARBOR_REFERENCE_YEAR, keyed_kept=[], keyed_found=found, **given,  # type: ignore[arg-type]
        )
    return [(pair.key, pair.value) for pair in found]


def _pooled_rows(kind: str) -> "list[list[str]]":
    """120 people, seven common keys, and the pool of rare keys ``kind`` names (skeptic 1's item 1).

    `one-n`, `one-w`, `one-c`: ONE rare key held by 4 people on 12 rows --
    numbers, one word, and one town under a key named `town_lived_in`; `few-1`:
    three rare keys held by three people on one row each; `wide`: eight rare
    keys of three people each, 24 people on one row each; `two-5`, `two-6`: TWO
    rare keys of five, or six, people each on three rows a person, ten
    people on thirty rows or twelve on thirty-six (repair 2, the scoped
    verify's item 3: the pool's people decide); `common-absent`: the rare
    keys of `wide` and a COMMON key, `skin_note`, on one row of each of the
    120 people, a word (`dry` or `warm`) on the rows of 5 of them and blank
    on the rest, so its block is counted absent (the lane's last step,
    LANE KV RULINGS 7 (2)).
    """
    draw = random.Random(7)
    rows: "list[list[str]]" = []
    for place in range(120):
        person = f"Q{5000 + 7 * place}"
        for _visit in range(3):
            rows += [
                [person, "pulse", f"{draw.randint(50, 120)}"], [person, "resp_rate", f"{draw.randint(8, 40)}"],
                [person, "pain_score", f"{draw.randint(0, 10)}"], [person, "mood", draw.choice(("calm", "low", "tense", "flat", "bright"))],
                [person, "temp_c", f"{draw.gauss(36.9, 0.4):.1f}"], [person, "skin", draw.choice(("warm", "cool", "pale", "moist"))],
                [person, "sleep_hours", f"{draw.gauss(7, 1.2):.1f}"],
            ]
        if kind.startswith("one") and place < 4:
            for _again in range(3):
                value = {"one-n": f"{draw.randint(1, 9)}", "one-w": "Positive", "one-c": "Alderford"}[kind]
                rows += [[person, "town_lived_in" if kind == "one-c" else "special_check", value]]
        if kind == "few-1" and place < 3:
            rows += [[person, f"rare_item_{place}", f"{draw.randint(1, 9)}"]]
        if kind in ("wide", "common-absent") and place < 24:
            rows += [[person, f"rare_item_{place // 3}", f"{draw.randint(1, 9)}"]]
        if kind == "common-absent":
            rows += [[person, "skin_note", draw.choice(("dry", "warm")) if place < 5 else ""]]
        if kind.startswith("two-") and place < 2 * int(kind[4:]):
            rows += [[person, "special_check" if place < int(kind[4:]) else "second_check", f"{draw.randint(1, 9)}"] for _again in range(3)]
    return rows


def test_a_pool_of_rare_keys_fewer_than_the_floors_people_hold_names_and_publishes_nothing(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """BLOCKER 1 of skeptic 1 (LANE KV RULINGS 3 (1)), HIPAA first: a pool of rare keys held by fewer than the floor's people is counted absent and names nothing.

    Measured on 1d89eb6e at the table floor: one rare key of 4 people was
    named beside its 12 rows and its pooled block published the real mean,
    deviation and kurtosis of its 12 values, a word of 4 people, or a town.
    Every key block, the pool included, counts its person column in people
    whatever their number and whether or not it repeats on the block's rows
    (`build_document`'s ``people_whatever_their_number``), and a pool of one
    rare key, or of fewer than the floor's people, names nothing
    (`keyed_names_of`). Three rare keys of one row and one person each are
    counted absent too; a pool of 24 people is described. TWO rare keys of
    five people each on three rows a person (ten people, thirty rows) name
    nothing either: the pool's PEOPLE decide, never its rows (repair 2, the
    scoped verify's item 3: no case was red on `_rare_pool` counting its
    holders by rows, nor on the condition `rare_people < floor` dropped).
    """
    _floor_lowered(monkeypatch)
    tables = {kind: _long(tmp_path, f"pool-{kind}", _pooled_rows(kind)) for kind in ("one-n", "one-w", "one-c", "few-1", "wide", "two-5", "two-6")}

    def described(kind: str) -> "dict[str, object]":
        return _described(tables[kind], [], safe_harbor_no=["item_key", "item_value"], dated_values_no=["item_value"])

    def counted_in_people() -> None:
        for kind in ("one-n", "one-w", "one-c", "few-1"):
            document = described(kind)
            pool = _block(document, "item_value")["by_key"]["pool"]  # type: ignore[index]
            assert pool["n_present"] == 0 and pool["role"] == taxonomy.ROLE_EMPTY, (kind, pool)
            assert not _leaves(_block(document, "item_value"), set()) & {"Alderford", "alderford", "Positive", "positive"}, kind
        assert _block(described("wide"), "item_value")["by_key"]["pool"]["n_present"] == 24  # type: ignore[index]

    def named_nothing() -> None:
        for kind in ("one-n", "one-w", "one-c", "two-5"):
            key = _block(described(kind), "item_key")
            assert "pool_in_people" in key and "held_back_names" not in key, kind

    def named_by_people() -> None:
        key = _block(described("two-5"), "item_key")
        assert "pool_in_people" in key and "held_back_names" not in key

    # ...twelve people on the same two keys name them: the floor's people decide.
    assert _block(described("two-6"), "item_key")["held_back_names"] == ["second_check", "special_check"]

    _red(counted_in_people, profile, "build_document", lambda *a, **k: _REAL_BUILD(*a, **{**k, "people_whatever_their_number": False}))
    _red(named_nothing, profile, "keyed_names_of", lambda pooled, spellings, _keys, _people, *rest: _REAL_NAMES_OF(pooled, spellings, 2, 10 ** 6, *rest))
    # ...the pool's holders counted by rows (the verify's SM08), and the
    # condition on the pool's people dropped, the count of its keys kept.
    _red(named_by_people, profile, "_rare_pool", lambda levels, people, common: (
        len({level for level in levels if level and level not in common}),
        len([level for level in levels if level and level not in common]),
    ))
    _red(named_by_people, profile, "keyed_names_of", lambda pooled, spellings, keys, _people, *rest: _REAL_NAMES_OF(pooled, spellings, keys, 10 ** 6, *rest))


_TOWN_PARTS = (("Alder", "Brook", "Copper", "Dun", "Ember", "Fern", "Gold", "Hazel", "Iron", "Juniper"), ("ford", "mere", "wick", "holm", "stead", "by"))
_SURNAME_PARTS = (("Aber", "Brindle", "Cor", "Della", "Ester", "Fenni", "Gallo", "Hart", "Ingle", "Jos"), ("naut", "combe", "vane", "croix", "hal", "more", "way", "wick"))
_GIVEN_PARTS = (("Ar", "Bri", "Cad", "Del", "Es", "Fio", "Gun", "Hes", "Il", "Ja"), ("len", "sa", "do", "phine", "kil", "ra", "nar", "per"))
_STREET_ENDS = ("Rd", "Lane", "Way", "Close", "")


def _coded_answers(seed: int, people: int = 150, each: int = 0) -> "tuple[list[str], list[list[str]], dict[str, set[str]]]":
    """A question-and-answer export of CODED question keys (`Q6101` ...), as the zoo's own kind writes them, whose answers to four keys are one-word towns, family names, given names and street names (skeptic 1's item 2): each vocabulary generated from ``seed``; and each such key's values.

    ``people`` persons, each drawing a word of each kind from twelve; with
    ``each``, a person's place decides the four words instead, over the
    first ``each`` of each kind, so every word is held by ``people`` /
    ``each`` people (the lane's last step, LANE KV RULINGS 7 (1): 300 over
    6, fifty people a word, no word fewer than the floor's people hold).
    """
    draw = random.Random(seed)

    def made(parts: "tuple[tuple[str, ...], tuple[str, ...]]", count: int) -> "list[str]":
        found: "list[str]" = []
        while len(found) < count:
            word = draw.choice(parts[0]) + draw.choice(parts[1])
            if word not in found:
                found += [word]
        return found

    towns, surnames, given = made(_TOWN_PARTS, 12), made(_SURNAME_PARTS, 12), made(_GIVEN_PARTS, 12)
    streets = [f"{name} {draw.choice(_STREET_ENDS)}".strip() for name in made(_TOWN_PARTS, 12)]
    words: "dict[str, set[str]]" = {"Q6105": set(), "Q6106": set(), "Q6107": set(), "Q6108": set()}
    rows: "list[list[str]]" = []
    for place in range(people):
        person = f"Q{9100 + 7 * place}"
        if each:
            own = (towns[place % each], surnames[place % each], given[place % each], streets[place % each])
        else:
            own = (draw.choice(towns), draw.choice(surnames), draw.choice(given), draw.choice(streets))
        for _form in range(3):
            rows += [[person, "Q6101", f"{draw.randint(0, 10)}"], [person, "Q6102", f"{draw.gauss(7, 1):.1f}"],
                     [person, "Q6103", draw.choice(("Current", "Former", "Never"))], [person, "Q6104", f"{draw.randint(10, 240)}"]]
            for key, value in zip(("Q6105", "Q6106", "Q6107", "Q6108"), own):
                rows += [[person, key, value]]
                words[key].add(value)
    return ["person_id", "question_key", "answer"], rows, words


def test_after_the_value_columns_yes_every_block_of_words_under_a_coded_key_is_held(tmp_path: pathlib.Path) -> None:
    """BLOCKER 2 of skeptic 1 (LANE KV RULINGS 3 (2)), HIPAA first: under the value column's Safe Harbor `yes`, and while that question is unanswered, every block of a label role, text or dates is held; only numbers, joined numbers and numbers with labels stay described.

    GENERATED over value kinds under coded keys: two vocabularies of
    one-word towns, family names, given names and street names, which pass
    every screen of a level as they do in a wide column -- on 1d89eb6e the
    truthful `yes` described them (25 towns and 10 family names on 1,939
    twin cells at the table floor). The careless `no` describes them (the
    bar: never more than the column-wide reading published).
    """

    def held() -> None:
        for seed in (1, 2):
            header, rows, words = _coded_answers(seed)
            table = _table(tmp_path, header, rows, f"coded-{seed}.csv")
            for answers in ({}, {"keyed_yes": ["answer"]}):
                document = _described(table, [], **answers)
                blocks = _key_blocks(document, "answer")
                for key in words:
                    assert blocks[key.casefold()]["role"] == taxonomy.ROLE_IDENTIFIER, (seed, answers, key)
                every_word: "set[str]" = set()
                for found in words.values():
                    every_word |= found
                assert not _leaves(_block(document, "answer"), set()) & every_word, (seed, answers)
                for key in ("q6101", "q6102", "q6104"):
                    assert blocks[key]["role"] in (taxonomy.ROLE_COUNT, taxonomy.ROLE_CONTINUOUS), (seed, key)
                assert blocks["q6103"]["role"] == taxonomy.ROLE_IDENTIFIER
            careless = _key_blocks(_described(table, [], safe_harbor_no=["answer"]), "answer")
            assert careless["q6105"]["role"] != taxonomy.ROLE_IDENTIFIER

    _red(held, profile, "_listed_by_the_answer", lambda block, name: profile._key_names_an_identifier(name))


def test_a_value_column_put_no_question_describes_its_blocks_of_labels(tmp_path: pathlib.Path) -> None:
    """The listed blocks wait for the value column's question only where it is put (repair 1): a value column the command puts neither its Safe Harbor question nor its question about values that read as dates describes its blocks of labels, as its wide column would be described; put the question, they wait for its `no`.

    Measured on the repair's first head: a lab table's blocks of labels were
    held with no question to answer (its chloride, a constant block, made up).
    """
    # ...a lab table whose results run past 125 and whose words are a urine
    # test's: no date, no age, no Safe Harbor reason puts it a question.
    draw = random.Random(13)
    rows: "list[list[str]]" = []
    for place in range(200):
        for _visit in range(3):
            for test, middle, spread in (("glucose", 140, 30), ("platelets", 260, 50), ("sodium", 139, 3), ("cholesterol", 190, 30), ("triglycerides", 150, 40)):
                rows += [[f"Q{place}", test, f"{draw.gauss(middle, spread):.0f}"]]
            rows += [[f"Q{place}", "urine_look", draw.choice(("Clear", "Cloudy", "Turbid"))]]
            rows += [[f"Q{place}", "urine_color", draw.choice(("Yellow", "Amber", "Straw", "Pale"))]]
    table = _long(tmp_path, "unasked", rows)

    def unasked() -> None:
        reasons: "dict[str, str]" = {}
        open_put = _key_blocks(_described(table, [], five_figures=["item_value"], harbor_reasons=reasons), "item_value")
        assert open_put["urine_look"]["role"] == taxonomy.ROLE_IDENTIFIER
        put: "list[str]" = []
        unput = _key_blocks(_described(table, [], five_figures=put, harbor_reasons=reasons), "item_value")
        assert "item_value" not in put, reasons
        assert unput["urine_look"]["role"] == taxonomy.ROLE_CATEGORICAL
        assert unput["glucose"]["role"] == open_put["glucose"]["role"] != taxonomy.ROLE_IDENTIFIER

    _red(unasked, profile, "_values_typed_by_key", lambda *a: _REAL_TYPED(*a[:-1], None))


_REAL_TYPED = profile._values_typed_by_key


def _what_prints_nothing() -> "list[str]":
    """Every character of the one definition of a space that prints nothing (`taxonomy._prints_nothing`): the format and control characters among them."""
    return [character for character in _spaces() if taxonomy._prints_nothing(character)]


def _hidden_inside(text: str, characters: "list[str]", turn: int) -> "list[str]":
    """The text with one character that prints nothing set at every place inside each of its words, the characters taken in turn from ``turn``."""
    words = text.split(" ")
    found: "list[str]" = []
    for at, word in enumerate(words):
        for cut in range(1, len(word)):
            hidden = word[:cut] + characters[turn % len(characters)] + word[cut:]
            found += [" ".join(words[:at] + [hidden] + words[at + 1:])]
            turn = turn + 1
    return found


def _hidden_names() -> "list[tuple[str, str]]":
    """GENERATED: the texts of the eleven families refused whole, and a person's name written alone or family first, each with a character that prints nothing at every place inside each word (skeptic 1's item 3); every such character met many times over."""
    draw = random.Random(20261113)
    characters = _what_prints_nothing()
    found: "list[tuple[str, str]]" = []
    turn = 0
    for family in _ELEMENT_FAMILIES:
        if family == "a person's name":
            continue
        for _case in range(6):
            found += [(family, name) for name in _hidden_inside(_key_name(family, draw), characters, turn)]
            turn = turn + 11
    for _case in range(6):
        given, surname = draw.choice(_GIVEN), draw.choice(_FAMILY)
        for written in (f"{given} {surname}", f"{surname}, {given[0]}"):
            found += [("a name alone", name) for name in _hidden_inside(written, characters, turn)]
            turn = turn + 11
    return found


def test_a_character_that_prints_nothing_inside_a_word_hides_no_name_from_any_road() -> None:
    """BLOCKER 3 of skeptic 1 (LANE KV RULINGS 3 (3)), HIPAA first: every reader reads a key's name and a key block's level twice, as written and with what prints nothing set aside, and refuses it where either reading is read.

    On 1d89eb6e one zero-width space inside `Dr.` or `wife` took 990 of
    5,870 titled names and 1,680 of 8,840 names beside a relative's word
    past every road. GENERATED: every character that prints nothing, at
    every place inside each word of the eleven families' texts and of a
    name written alone or family first, refused on the road of categories
    and on a declared code's; and the readers of a key's name and of a
    block's levels the value column's answers rest on.
    """
    hidden = _hidden_names()
    assert len({name[at] for _family, name in hidden for at in range(len(name)) if taxonomy._prints_nothing(name[at])}) == len(_what_prints_nothing())

    def refused() -> None:
        for family, name in hidden:
            for role, code in ((taxonomy.ROLE_CATEGORICAL, False), (taxonomy.ROLE_LONG_TAIL, True)):
                assert not profile.keyed_names_pass((name,), role, code, False), (family, repr(name), role)
        assert profile._key_names_an_identifier("home_z" + "\u200b" + "ip5")
        assert profile._read_as_identifiers({"levels": [{"label": "D" + "\u2060" + "r. Pelleth"}]}, "visit_with")
        assert profile._listed_by_the_answer({"role": taxonomy.ROLE_COUNT}, "record_" + "\u00ad" + "number")

    _red(refused, profile, "_both_readings", lambda text: (text,))


_QUESTION_WORDS = (
    "How", "often", "do", "you", "walk", "sleep", "eat", "feel", "rested", "outside", "since", "last", "visit",
    "today", "this", "week", "any", "falls", "pain", "rate", "your", "trouble", "with", "stairs", "meals",
)


def _sentences() -> "list[str]":
    """GENERATED: question texts of 3 to 10 words, each holding a mark of a sentence (every one of `profile._KEYED_SENTENCE_MARKS` in turn) after one of its words, a third of them joined by a character of the one definition of a space."""
    draw = random.Random(20261113)
    marks = list(getattr(profile, "_KEYED_SENTENCE_MARKS", ".?!:;"))
    spaces = _spaces()
    found: "list[str]" = []
    for turn in range(600):
        words = [draw.choice(_QUESTION_WORDS) for _word in range(draw.randint(3, 10))]
        at = draw.randrange(len(words))
        words[at] = words[at] + marks[turn % len(marks)]
        found += [(draw.choice(spaces) if turn % 3 == 0 else " ").join(words)]
    return found


def test_no_rare_key_that_reads_as_a_sentence_is_named(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """LANE KV RULINGS 2 (2), the rule of LANE NOTES RULINGS 8 (1), HIPAA first: a rare key that reads as a sentence -- a question text written out -- is named after no answer, on either road, a declared key or not; ALL OR NONE, so one such key leaves the pool unnamed.

    GENERATED over 600 question texts, every mark of a sentence in turn;
    and at the table floor's rule (lowered, `_floor_lowered`) a key column
    of eight rare question texts answered `no` names none, the same column
    of plain rare names naming its eight. The price: a question form's rare
    question texts come out under made-up names again (P4-D487).
    """
    sentences = _sentences()
    _floor_lowered(monkeypatch)
    asked: "dict[str, reading.Table]" = {}
    for kind in ("texts", "names"):
        rows = _pooled_rows("")
        for place in range(24):
            name = f"How often do you {_QUESTION_WORDS[4 + place // 3]} since rounds?" if kind == "texts" else f"rare_item_{place // 3}"
            # ...four rows a person, so each key's twelve rows pool in people.
            rows += [[f"Q{5000 + 7 * place}", name, f"{(place + visit) % 9}"] for visit in range(4)]
        asked[kind] = _long(tmp_path, f"asked-{kind}", rows)

    def refused() -> None:
        for name in sentences:
            for role, code in ((taxonomy.ROLE_CATEGORICAL, False), (taxonomy.ROLE_LONG_TAIL, True)):
                assert not profile.keyed_names_pass(_ORDINARY + (name,), role, code, False), (repr(name), role, code)
        named = _block(_described(asked["names"], [], safe_harbor_no=["item_key", "item_value"]), "item_key")
        assert "pool_in_people" in named and sorted(named["held_back_names"]) == [f"rare_item_{group}" for group in range(8)]
        texts = _block(_described(asked["texts"], [], safe_harbor_no=["item_key", "item_value"]), "item_key")
        assert "pool_in_people" in texts and "held_back_names" not in texts

    _red(refused, profile, "_reads_as_a_sentence", lambda name: False)


def _flow_codes(rare_rows: int, rare_people: int) -> "list[list[str]]":
    """A long table whose keys are codes (`F10001` ...): seven common codes and twelve rare ones, each rare code held by ``rare_people`` people on ``rare_rows`` rows."""
    draw = random.Random(17)
    rows: "list[list[str]]" = []
    for place in range(150):
        person = f"Q{6000 + 7 * place}"
        for _visit in range(3):
            rows += [[person, "F10001", f"{draw.randint(50, 120)}"], [person, "F10002", f"{draw.randint(8, 40)}"],
                     [person, "F10003", f"{draw.randint(0, 10)}"], [person, "F10004", draw.choice(("calm", "low", "tense", "flat"))],
                     [person, "F10005", f"{draw.gauss(36.9, 0.4):.1f}"], [person, "F10006", draw.choice(("warm", "cool", "pale"))],
                     [person, "F10007", f"{draw.gauss(7, 1.2):.1f}"]]
    for code in range(12):
        holders = [f"Q{6000 + 7 * ((code * rare_people + one) % 150)}" for one in range(rare_people)]
        for row in range(rare_rows):
            rows += [[holders[row % rare_people], f"F2{code:04d}", f"{draw.randint(1, 9)}"]]
    return rows


def test_the_six_holds_of_skeptic_1s_item_4_each_red_on_its_mutant(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MAJOR 4 of skeptic 1 (LANE KV RULINGS 3 (4)): six HIPAA conditions, each a case, five red on their mutants (M15, M16, M11, M14, M10) and the sixth's mutant (M09) equivalent.

    (a) the person declared, the key column NOT answered `no`: no name, though
    its pool is counted in people (a declared code's pool needs no answer);
    (b) a key column whose pool is counted in ROWS names exactly what lane
    CODES-2's own rule names, the keyed reading on or off, and the naming
    condition names no pool not counted in people; (c) a question offering
    `identifier` open on the table: a key block's pool in people stays held
    after the value column's `no`; (d) a value column held by an open
    question offering `identifier` is described under no key; (e) a key of
    figures of one width under a neutral name is held by the question a
    column of them would be put; (f) a key of ages a declared missing value
    90 holds is held (its mutant is equivalent, below). The floor lowered
    for (a) and (b) (`_floor_lowered`).
    """
    _floor_lowered(monkeypatch)
    coded = _long(tmp_path, "codes", _flow_codes(12, 2))

    def unanswered_key() -> None:
        document = _described(coded, [], forced_codes=["item_key"], safe_harbor_no=["item_value"])
        key = _block(document, "item_key")
        assert "pool_in_people" in key and "held_back_names" not in key
        named = _block(_described(coded, [], forced_codes=["item_key"], safe_harbor_no=["item_value", "item_key"]), "item_key")
        assert named["held_back_names"] == [f"F2{code:04d}" for code in range(12)]

    _red(unanswered_key, profile, "keyed_names_of", lambda *a: _REAL_NAMES_OF(*a[:7], True, *a[8:]))
    by_rows = _long(tmp_path, "rows", _flow_codes(2, 2))

    def row_pool() -> None:
        on = _block(_described(by_rows, [], forced_codes=["item_key"], safe_harbor_no=["item_value", "item_key"]), "item_key")
        off = _block(_described(by_rows, None, forced_codes=["item_key"], safe_harbor_no=["item_value", "item_key"]), "item_key")
        assert "pool_in_people" not in on and on.get("held_back_names") == off.get("held_back_names")
        assert profile.keyed_names_of(False, ("F20000", "F20001"), 2, 40, 30000, 2000, True, True, taxonomy.ROLE_LONG_TAIL, True, False, FLOOR) == ()

    _red(row_pool, profile, "keyed_names_of", lambda pooled, *rest: _REAL_NAMES_OF(True, *rest))
    header, rows = _small_long()
    draw = random.Random(5)
    for place in range(160):
        person = f"Q{7000 + 3 * place}"
        if place % 40 == 0:
            rows += [[person, "mood_word", f"Mood{place:03d}"]] * 12
        else:
            rows += [[person, "mood_word", draw.choice(("Calm", "Anxious", "Tearful"))] for _each in range(3)]
    moods = _table(tmp_path, header, rows, "moods.csv")

    def open_elsewhere() -> None:
        freed = _key_blocks(_described(moods, [], safe_harbor_no=["item_value"], dated_values_no=["item_value"]), "item_value")
        assert "pool_in_people" in freed["mood_word"]
        held = _key_blocks(
            _described(moods, [], safe_harbor_no=["item_value"], dated_values_no=["item_value"], rare_values_released=False), "item_value"
        )
        assert held["mood_word"]["role"] == taxonomy.ROLE_IDENTIFIER

    _red(open_elsewhere, profile, "_pool_released", lambda asked, pool_only: pool_only and (asked.safe_no or asked.dates_no))

    def value_held_open() -> None:
        document = _described(moods, [], keyed_open=["item_value"], unanswered=["item_value"])
        assert "by_key" not in _block(document, "item_value") and "keyed" not in _block(document, "item_key")

    _red(value_held_open, profile, "_keyed_value_held", lambda value, _open, *rest: _REAL_HELD(value, [], *rest))
    refs: "list[list[str]]" = []
    ages: "list[list[str]]" = []
    for place in range(220):
        person = f"Q{9100 + 7 * place}"
        age = draw.choice((91, 93, 95)) if place % 9 == 0 else draw.randint(20, 85)
        for _form in range(3):
            common = [[person, "q_pain", f"{draw.randint(0, 10)}"], [person, "q_sleep", f"{draw.gauss(7, 1):.1f}"],
                      [person, "q_tobacco", draw.choice(("Current", "Former", "Never"))], [person, "q_mood", draw.choice(("calm", "low", "tense", "flat"))],
                      [person, "q_steps", f"{draw.randint(10, 240)}"], [person, "q_weight", f"{draw.gauss(80, 12):.1f}"]]
            refs += common + [[person, "q_ref", f"{4000000 + 7919 * place}"], [person, "q_code", f"{draw.randint(100, 999)}"]]
            ages += common + [[person, "age_in_years", f"{age}"]]
    referenced = _long(tmp_path, "refs", refs)
    aged = _long(tmp_path, "ages", ages)

    def neutral_record_numbers() -> None:
        blocks = _key_blocks(_described(referenced, [], safe_harbor_no=["item_value"]), "item_value")
        # A key of unique seven-figure numbers is read as record numbers by
        # the block's own describe; a key of three figures is put the
        # question a column of fixed width is put, and held while it is open.
        assert blocks["q_ref"]["role"] == blocks["q_code"]["role"] == taxonomy.ROLE_IDENTIFIER
        assert blocks["q_pain"]["role"] == taxonomy.ROLE_COUNT

    _red(neutral_record_numbers, profile, "_asked_as_an_identifier", lambda *a, **k: False)

    # (f) A key of ages whose 90 is a declared missing value is held. Its
    # mutant M09 (the block's `ages_held` list set aside) is EQUIVALENT: the
    # block's own describe holds such a column whole, so the list adds no
    # hold the block lacks (measured on the repair's head: the same block,
    # role `identifier`, with and without the list); the case stands as the
    # product's check.
    document = profile.build_document(
        aged, dataclasses.replace(taxonomy.Settings(small_cell_floor=FLOOR), declared_missing_values=("90",)), ["person_id"],
        subjects=["person_id"], top_code=True, harbor_year=taxonomy.SAFE_HARBOR_REFERENCE_YEAR, keyed_kept=[], safe_harbor_no=["item_value"],
    )
    blocks = _key_blocks(document, "item_value")
    assert blocks["age_in_years"]["role"] == taxonomy.ROLE_IDENTIFIER
    assert not _leaves(blocks["age_in_years"], set()) & {"91", "93", "95"}


def test_a_table_of_one_row_a_person_or_a_key_fixed_per_person_reads_no_pair(tmp_path: pathlib.Path) -> None:
    """MAJOR 5 of skeptic 1 (LANE KV RULINGS 3 (4)) and the variation rule (its item 8's M01 and M02): no pair where no person holds two rows, where no column counts people that repeat, or where each person keeps one key.

    On 1d89eb6e a visit type setting a duration's scale on 1,600 rows of
    1,600 people was read as keyed, the person declared or not.
    """
    draw = random.Random(21)
    kinds = (("Phone", 6.0), ("Clinic", 20.0), ("Procedure", 75.0), ("Surgery", 210.0), ("Infusion", 160.0), ("Imaging", 35.0))
    once = [[f"P{800000 + place}", kind, f"{max(1, round(draw.gauss(minutes, minutes / 5)))}"] for place in range(1600) for kind, minutes in [draw.choice(kinds)]]
    one_row = _table(tmp_path, ["person_id", "visit_type", "duration_min"], once, "once.csv")
    assert _pairs(one_row) == []
    assert _pairs(_table(tmp_path, ["visit_ref", "visit_type", "duration_min"], once, "once-unnamed.csv")) == []
    fixed: "list[list[str]]" = []
    for place in range(300):
        kind, minutes = kinds[place % len(kinds)]
        fixed += [[f"Q{place}", kind, f"{max(1, round(draw.gauss(minutes, minutes / 5)))}"] for _visit in range(4)]
    fixed_table = _table(tmp_path, ["person_id", "visit_type", "duration_min"], fixed, "fixed.csv")

    def fixed_per_person() -> None:
        assert _pairs(fixed_table) == []

    _red(fixed_per_person, profile, "_varies_within_a_person", lambda levels, people: True)


def _bands_table(tmp_path: pathlib.Path, name: str, rows_a_person: int) -> reading.Table:
    """A number and the category worked out from it, ``rows_a_person`` rows a person (the statistics check's item 4)."""
    draw = random.Random(11)

    def band(age: int) -> str:
        return "90+" if age >= 90 else f"{age // 10 * 10}-{age // 10 * 10 + 9}"

    def group(age: int) -> str:
        return "0-17" if age < 18 else ("18-44" if age < 45 else ("45-64" if age < 65 else "65+"))

    def size(mass: float) -> str:
        return "Underweight" if mass < 18.5 else ("Normal" if mass < 25 else ("Overweight" if mass < 30 else "Obese"))

    rows: "list[list[str]]" = []
    for place in range(500):
        for _visit in range(rows_a_person):
            if name == "ratio":
                value = round(max(14.0, draw.gauss(27.5, 5.5)), 1)
                rows += [[f"P{700000 + 7 * place}", size(value), f"{value}"]]
            else:
                age = min(104, max(0, int(draw.gauss(52, 22))))
                rows += [[f"P{700000 + 7 * place}", band(age) if name == "age10" else group(age), f"{age}"]]
    return _table(tmp_path, ["person_id", "band", "value"], rows, f"{name}-{rows_a_person}.csv")


def test_a_number_and_the_category_worked_out_from_it_are_no_keyed_pair(tmp_path: pathlib.Path) -> None:
    """THE STATISTICS CHECK'S ITEM 4 (LANE KV RULINGS 4 (3)), THE DIRECTION RULE: where the value decides the key on 95 rows in 100 and the common keys' numeric ranges, ordered by their smallest number, do not overlap and touch, the key is the value's dependent at any number of keys.

    On 1d89eb6e an age and its ten-year band and a body mass and its four
    classes were read as keyed, one row and four rows a person, and the
    zoo's quarters and their times. A panel of tests whose scales stand
    apart (gaps far wider than a quarter of a test's span) stays keyed, as
    the six invented forms do (the reach, K-HZ-37).
    """
    tables = [_bands_table(tmp_path, name, rows) for name in ("age10", "age4", "ratio") for rows in (1, 4)]
    draw = random.Random(4)
    edges_header, edges_rows = health_zoo_wide.time_edges(2000, 7)
    edges = _table(tmp_path, edges_header, edges_rows, "edges.csv")
    panel: "list[list[str]]" = []
    for place in range(300):
        for _draw in range(3):
            for test, middle, spread in (("potassium", 4.2, 0.3), ("hemoglobin", 13.5, 1.0), ("sodium", 139.0, 2.5), ("platelets", 450.0, 30.0),
                                         ("albumin", 40.0, 2.0), ("ferritin", 900.0, 60.0)):
                panel += [[f"Q{place}", test, f"{draw.gauss(middle, spread):.1f}"]]
    apart = _long(tmp_path, "apart", panel)
    sample = _long(tmp_path, "sample", _pooled_rows("wide"))

    def dependent() -> None:
        for table in tables:
            assert _pairs(table) == [], table.column_names
        assert _pairs(edges) == []
        assert _pairs(apart) == [("item_key", "item_value")]
        assert _pairs(sample) == [("item_key", "item_value")]

    _red(dependent, profile, "_the_value_decides_the_key", lambda *a: False)


def test_each_rule_of_the_reading_is_red_on_its_mutant(tmp_path: pathlib.Path) -> None:
    """SKEPTIC 1'S ITEM 8: the reading's own rules, each a case red on its mutant -- a key of dates (M03), keys counted from one person (M04), the five values a key (M05), rule A's two readings (M07), rule B's four fifths (M08)."""
    draw = random.Random(31)
    dated: "list[list[str]]" = []
    for place in range(200):
        for day, centre in enumerate((0.0, 1.5, 3.0, 4.5, 6.0, 7.5)):
            # ...a day written `10-Mar`, which the describe reads as labels.
            dated += [[f"Q{place}", f"{day + 10}-Mar", f"{math.exp(draw.gauss(centre, 0.8)):.2f}"]]
    dates_table = _long(tmp_path, "dated", dated)

    def no_key_of_dates() -> None:
        assert _pairs(dates_table) == []

    _red(no_key_of_dates, profile, "_reads_as_dates_or_clocks", lambda levels, cells: False)
    # ...a key column of ONE key the floor's people hold and sixty keys of one
    # person each is no key: its keys are counted in people, never in rows.
    solo_rows: "list[list[str]]" = []
    for place in range(120):
        solo_rows += [[f"Q{place}", "pulse", f"{draw.uniform(50, 120):.2f}"] for _visit in range(3)]
        if place % 2 == 0:
            solo_rows += [[f"Q{place}", f"own_check_{place:03d}", draw.choice(("Clear", "Moist", "Dry", "Warm", "Cool", "Pale", "Flushed", "Calm", "Low", "Tense"))]
                          for _visit in range(3)]
    solo = _long(tmp_path, "solo", solo_rows)

    def no_block_of_one_person() -> None:
        assert _pairs(solo) == []

    _red(no_block_of_one_person, profile, "_common_keys", lambda levels, people, floor: _REAL_COMMON(levels, people, 1))
    # ...eight keys of three values each, scales apart: fewer than five
    # different values a key, so no key (a number of few levels is a code).
    answered: "list[list[str]]" = []
    for place in range(200):
        for power in range(8):
            answered += [[f"Q{place}", f"dose_{power}", f"{draw.choice((1.5, 2.5, 3.5)) * 10 ** power:.1f}"]]
    few_values = _long(tmp_path, "amounts", answered)

    def five_values_a_key() -> None:
        assert _pairs(few_values) == []

    _red(five_values_a_key, profile, "_five_values_a_key", lambda distinct, width: True)
    worded: "list[list[str]]" = []
    for place in range(200):
        for key, choices in enumerate((("Clear", "Wheeze", "Crackles"), ("Warm", "Cool", "Pale"), ("Calm", "Low", "Tense"), ("Steady", "Unsteady"),
                                       ("Moist", "Dry"), ("Alert", "Drowsy", "Asleep"), ("Pink", "Grey", "Dusky"))):
            worded += [[f"Q{place}", f"look_{key}", draw.choice(choices) + f" {draw.choice(('now', 'still', 'again'))}"]]
        if place % 4 == 0:
            worded += [[f"Q{place}", "look_count", f"{draw.randint(1, 30)}"]]
    one_reading = _long(tmp_path, "words", worded)

    def two_readings() -> None:
        assert _pairs(one_reading) == []

    _red(two_readings, profile, "_rule_a", lambda leaders, pure, covered: leaders >= 1 and 5 * pure >= 4 * covered)
    scaled: "list[list[str]]" = []
    for place in range(200):
        for _visit in range(3):
            for key, centre in enumerate((1.0, 1.6, 2.2, 2.8, 3.4, 4.0, 4.6)):
                scaled += [[f"Q{place}", f"k{key}", f"{math.exp(draw.gauss(centre, 0.8)):.2f}"]]
    loose = _long(tmp_path, "scales", scaled)

    def four_fifths() -> None:
        assert _pairs(loose) == []

    _red(four_fifths, profile, "_rule_b", lambda between, spread: spread > 0 and 5 * between >= 2 * spread)


def test_a_declared_measurement_frees_a_key_block_the_fixed_width_question_holds(tmp_path: pathlib.Path) -> None:
    """THE STATISTICS CHECK'S ITEM 3 (LANE KV RULINGS 4 (2)): the value column declared a measurement reaches each key block's hold test as it reaches a wide column, so sodium's three-figure results are described, not made up at 901 to 999; undeclared they are held."""
    draw = random.Random(3)
    rows: "list[list[str]]" = []
    for place in range(300):
        for _draw in range(3):
            for test, middle, spread, places in (("Sodium", 139, 3, 0), ("Potassium", 4.2, 0.4, 1), ("Glucose", 110, 25, 0),
                                                  ("Hemoglobin", 13.5, 1.5, 1), ("Albumin", 40, 3, 0), ("Creatinine", 1.0, 0.3, 2)):
                rows += [[f"Q{place}", test, f"{draw.gauss(middle, spread):.{places}f}"]]
    table = _long(tmp_path, "lab-declared", rows, "result")

    def declared() -> None:
        plain = _key_blocks(_described(table, [], safe_harbor_no=["result"]), "result")
        assert plain["sodium"]["role"] == taxonomy.ROLE_IDENTIFIER
        freed = _key_blocks(_described(table, [], safe_harbor_no=["result"], forced_measurements=["result"]), "result")
        assert freed["sodium"]["role"] in (taxonomy.ROLE_COUNT, taxonomy.ROLE_CONTINUOUS)

    _red(declared, profile, "_asked_as_an_identifier", lambda table, document, settings, people, name, declared=False: _REAL_ASKED(table, document, settings, people, name, False))


def test_the_summary_names_each_measurement_held_and_each_written_90_from_90(tmp_path: pathlib.Path) -> None:
    """THE STATISTICS CHECK'S ITEM 2 (d) (LANE KV RULINGS 4 (1)): the page names each held key block and each top-coded one in the person's words (the names of common keys are published already), so no analysis of them is run on the twin unawares. Since lane RX-1 (the fidelity plan's R3) a key whose name names a measurement (`Chloride`) is no age and keeps its values from 90 up; a key whose name says nothing (`Panel K`) is top-coded until its question is answered, and the page names it."""
    draw = random.Random(3)
    rows: "list[list[str]]" = []
    for place in range(300):
        for _draw in range(3):
            for test, middle, spread, places in (("Sodium", 139, 3, 0), ("Potassium", 4.2, 0.4, 1), ("Chloride", 103, 3, 0),
                                                  ("Hemoglobin", 13.5, 1.5, 1), ("Glucose", 110, 25, 0), ("Creatinine", 1.0, 0.3, 2),
                                                  ("Panel K", 103, 3, 0)):
                rows += [[f"Q{place}", test, f"{draw.gauss(middle, spread):.{places}f}"]]
    document = _described(_long(tmp_path, "lab-said", rows, "result"), [], safe_harbor_no=["result"])
    blocks = _key_blocks(document, "result")
    assert blocks["sodium"]["role"] == taxonomy.ROLE_IDENTIFIER and "top_coded" in blocks["panel k"]
    assert "top_coded" not in blocks["chloride"]

    def said() -> None:
        page = summary.render(document, "Read as UTF-8.")
        assert "measurements held, their values made up in the twin: Sodium" in page
        assert "measurements whose every value from 90 up is written as 90 (the rule for an age over 89): Panel K" in page

    _red(said, summary, "_names_in_a_list", lambda names: "")


def test_the_recount_misses_a_twin_whose_key_blocks_do_not_add_up(tmp_path: pathlib.Path, keyed_document: "dict[str, object]") -> None:
    """SKEPTIC 1'S ITEM 8, M19: a twin whose rows of a key do not match its block is MISSED by V19, its key named."""
    loaded = _loaded(tmp_path, keyed_document)
    twin = generation.generate_held(loaded, 7)
    names = list(twin.names)
    cells = [list(twinstore.column_cells(column)) for column in twin.held_columns]
    keys = cells[names.index("item_key")]
    moved = 0
    for place in range(len(keys)):
        if keys[place] == "pulse" and moved < 9:
            keys[place] = "airway"
            moved = moved + 1
    path = tmp_path / "twin-moved.csv"
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(names)
    writer.writerows(zip(*cells))
    path.write_text(out.getvalue(), encoding="utf-8", newline="\n")

    def missed() -> None:
        lines = [check for check in validation.measure(loaded, str(path)).checks if check.fact == "label.by_key"]
        assert [check for check in lines if check.verdict == validation.MISSED and "pulse" in f"{check}"]

    _red(missed, validation, "_key_count_check", lambda name, label, rows, _found_rows, cells, _found_cells, withheld=False: _REAL_COUNT_CHECK(name, label, rows, rows, cells, cells, withheld))


def test_the_word_plan_of_a_keyed_twin_is_the_oracles(tmp_path: pathlib.Path, keyed_document: "dict[str, object]") -> None:
    """SKEPTIC 1'S ITEM 8, M20 (A-P4-59): the words of the stream each keyed value column takes are the oracle's (`keyed_word_counts`): one a key block and one for the pooled block."""
    oracle = _oracle()
    loaded = _loaded(tmp_path, keyed_document)
    kept = _loaded(tmp_path, _described(_table(tmp_path, *_small_long(), "kept.csv"), ["item_value"]))

    def planned() -> None:
        for described in (loaded, kept):
            names = [column.name for column in described.columns]
            columns = [(bool(column.keyed_by) and column.keyed_by in names, len(column.key_blocks), column.key_pool is not None) for column in described.columns]
            assert generation._keyed_word_counts(described) == oracle.keyed_word_counts(columns)  # type: ignore[attr-defined]
        assert generation._keyed_word_counts(loaded) == [len(_block(keyed_document, "item_value")["by_key"]["key_blocks"]) + 1]  # type: ignore[index]

    _red(planned, generation, "_keyed_word_counts", lambda described: [count + 1 for count in _REAL_WORDS(described)])


# -- repair 2 (the orchestrator's LANE KV RULINGS 6): ANY YES HOLDS, and a key
# block counted absent recounted on its rows alone -----------------------------

_REAL_KEY_BLOCK = profile._key_block


def _key_block_without_the_yes(*arguments: object) -> object:
    """The mutant that drops the `yes` term: each key block described as though no question put to the value column had been answered `yes`."""
    head, asked, tail = arguments[:5], arguments[5], arguments[6:]
    return _REAL_KEY_BLOCK(*head, dataclasses.replace(asked, safe_yes=False), *tail)  # type: ignore[arg-type, type-var]


def _day_counts(rows: "list[list[str]]") -> "list[list[str]]":
    """The small long table's rows with a key of counts, about one cell in twelve a five-figure number that reads as a day: a date in disguise."""
    draw = random.Random(17)
    for place in range(160):
        person = f"Q{7000 + 3 * place}"
        for _visit in range(4):
            rows += [[person, "item_count", f"{draw.randint(45000, 45600)}" if draw.random() < 0.08 else f"{draw.randint(1, 40)}"]]
    return rows


def _largest_number(node: object) -> float:
    """The largest number a block holds anywhere, written as a number or as text that reads as one; 0 for none."""
    if isinstance(node, bool):
        return 0.0
    if isinstance(node, (int, float)):
        return float(node)
    if isinstance(node, str):
        try:
            return float(node) if math.isfinite(float(node)) else 0.0
        except ValueError:
            return 0.0
    if isinstance(node, dict):
        return max([0.0] + [_largest_number(key) for key in node] + [_largest_number(node[key]) for key in node])
    if isinstance(node, list):
        return max([0.0] + [_largest_number(item) for item in node])
    return 0.0


def _the_value_columns(given: "dict[str, object]", value: str) -> "dict[str, object]":
    """The same answers, each naming the value column ``value``."""
    return {key: ((value,) if isinstance(found, tuple) else [value]) for key, found in given.items()}


def test_a_pool_in_people_is_released_by_no_and_never_beside_a_yes() -> None:
    """ANY YES HOLDS THE POOL IN PEOPLE TOO (`_pool_released`, the orchestrator's LANE KV RULINGS 6 (1)): a key block held only because some of its values are held by too few people is counted in people after a `no` to either question put to the value column, never beside a `yes` to either, never while a question offering `identifier` is open (rule U (c))."""

    def asked(**given: bool) -> "profile._KeyedAsked":
        fields: "dict[str, object]" = {
            "safe_no": False, "safe_yes": False, "dates_no": False, "dates_held": False, "question_put": True, "code": False,
            "measurement": False, "comma": False, "kept_identity": False, "released": True,
            "harbor_year": taxonomy.SAFE_HARBOR_REFERENCE_YEAR,
        }
        return profile._KeyedAsked(**{**fields, **given})  # type: ignore[arg-type]

    def released() -> None:
        assert profile._pool_released(asked(safe_no=True), True)
        assert profile._pool_released(asked(dates_no=True), True)
        assert not profile._pool_released(asked(safe_no=True, safe_yes=True), True)
        assert not profile._pool_released(asked(dates_no=True, safe_yes=True), True)
        assert not profile._pool_released(asked(safe_no=True, released=False), True)
        assert not profile._pool_released(asked(safe_no=True), False)

    _red(released, profile, "_pool_released", lambda given, pool_only: pool_only and (given.safe_no or given.dates_no) and given.released)


def test_a_key_columns_yes_beside_its_no_names_no_rare_key(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """ANY YES HOLDS THE NAMES TOO (the orchestrator's LANE KV RULINGS 6 (1): every place that reads these answers checked): a keyed key column names its rare keys after its `no` only where no `yes` was given to a question put to it beside that `no`; the head read the `no` alone. Below the floor (a test device): two rare keys of six people each, pooled in people."""
    _floor_lowered(monkeypatch)
    table = _long(tmp_path, "names-beside-a-yes", _pooled_rows("two-6"))

    def names(**given: object) -> object:
        return _block(_described(table, [], dated_values_no=["item_value"], **given), "item_key").get("held_back_names")

    def held() -> None:
        assert names(safe_harbor_no=["item_key", "item_value"]), "premise: the key column's no names its rare keys"
        assert names(safe_harbor_no=["item_key", "item_value"], keyed_yes=["item_key"]) is None

    _red(held, profile, "keyed_names_of", lambda *given: _REAL_NAMES_OF(*given[:7], True, *given[8:]))


def _below_the_floor(arguments: "list[str]") -> int:
    """A command run with the owner's table floor lifted: a test device (LANE I4m RULINGS 18 (4))."""
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        return cli.main(arguments, small_tables_refused=False)


def _coded_with_dates(tmp_path: pathlib.Path) -> "tuple[pathlib.Path, str]":
    """The coded form's keys of words and one key of numbers, with a key of dates written as text, described once through the profile command; its source and its first questions file."""
    header, every_row, _words = _coded_answers(1)
    rows = [row for row in every_row if row[1] not in ("Q6102", "Q6103", "Q6104")]
    draw = random.Random(3)
    for person in sorted({row[0] for row in rows}):
        rows += [[person, "Q6109", f"{draw.randint(1930, 1990)}-{draw.randint(1, 12):02d}-{draw.randint(1, 28):02d}"]] * 3
    source = tmp_path / "coded.csv"
    source.write_text(_csv(header, rows), encoding="utf-8", newline="\n")
    assert _below_the_floor(["profile", f"{source}", "--replace"]) == 0
    return source, (tmp_path / "coded-questions.json").read_text(encoding="utf-8")


def _answered_through_the_command(source: pathlib.Path, first: str, harbor: str, dates: str) -> "dict[str, object]":
    """The first questions file answered -- the person column `identifier`, the key `keep`, the value column's question about values that read as dates ``dates``, and its Safe Harbor (age) question ``harbor``, written into the file as an earlier round's entry (the age reach puts it only at the table floor) -- and the table described again through the command."""
    questions = source.with_name("coded-questions.json")
    document = json.loads(first)
    put = 0
    for entry in document["asked"]:
        offered = [f"{choice['answer']}" for choice in entry["answers_you_can_give"]]
        if entry.get("column") == "person_id" and "identifier" in offered:
            entry["your_answer"] = "identifier"
        elif entry.get("column") == "answer" and asking.SAFE_HARBOR_DATES_SEEN in f"{entry.get('what_synthtwin_saw', '')}":
            entry["your_answer"] = dates
            put = put + 1
        elif "identifier" in offered and "keep" in offered:
            entry["your_answer"] = "keep"
    assert put == 1, "premise: the value column is put its question about values that read as dates"
    ages = asking._safe_harbor_question("answer", taxonomy.ROLE_CONTINUOUS, asking.BECAUSE_SAFE_HARBOR_AGES)
    document["asked"] += [{
        "column": "answer", "what_synthtwin_saw": ages.shape, "read_as_now": ages.taken,
        "answers_you_can_give": [{"answer": choice.answer, "means": "", "then_the_description_publishes": ""} for choice in ages.choices],
        "your_answer": harbor,
    }]
    questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
    assert _below_the_floor(["profile", f"{source}", "--replace", "--answers", f"{questions}"]) == 0
    described: "dict[str, object]" = json.loads(source.with_name("coded-profile.json").read_text(encoding="utf-8"))
    return described


def test_the_command_passes_a_yes_to_either_question_of_the_value_column(tmp_path: pathlib.Path) -> None:
    """ANY YES HOLDS THROUGH THE COMMAND (the orchestrator's LANE KV RULINGS 6 (1): every place that reads the value column's answers checked): the command passes the value column's `yes` to its question about values that read as dates beside its Safe Harbor `yes` (`keyed_yes`), so `yes` to either, beside `no` to the other, holds the blocks of words.

    On 46df4166 the Safe Harbor `yes` beside the dates `no` (C, the
    verify's corrected file) and the Safe Harbor `no` beside the dates
    `yes` (E) each described the four blocks of words and published their
    35 words: `_key_block` read no `yes`, and the command passed only the
    Safe Harbor `yes`. Below the floor (a test device): the age question is
    put only at the table floor, so its answer is written as an earlier
    round's entry, as a person's corrected file holds it.
    """
    words = _coded_answers(1)[2]
    every_word: "set[str]" = set()
    for found in words.values():
        every_word |= found
    source, first = _coded_with_dates(tmp_path)

    def held(answers: "tuple[tuple[str, str, str], ...]") -> None:
        for mode, harbor, dates in answers:
            described = _answered_through_the_command(source, first, harbor, dates)
            blocks = _key_blocks(described, "answer")
            for key in words:
                assert blocks[key.casefold()]["role"] == taxonomy.ROLE_IDENTIFIER, (mode, key)
            assert not _leaves(_block(described, "answer"), set()) & every_word, mode

    held((("C", "yes", "no"), ("E", "no", "yes")))
    # ...the mutant: the command passing the Safe Harbor `yes` alone, as the
    # head did (E then carries no `yes`; C's own term is the library case's).
    with _mutant(profile, "build_document", lambda *a, **k: _REAL_BUILD(*a, **{**k, "keyed_yes": [name for name in (k.get("keyed_yes") or []) if name != "answer"]})), pytest.raises(AssertionError):
        held((("E", "no", "yes"),))


# -- ONE case at the table floor, through the commands a person types ---------


def _run(arguments: "list[str]") -> int:
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        return cli.main(arguments, small_tables_refused=True)


def _answer(questions: pathlib.Path, given: "dict[tuple[str, str], str]") -> bool:
    """Answer the open entries the table's holder would answer; whether any was answered."""
    document = json.loads(questions.read_text(encoding="utf-8"))
    answered = False
    for section in ("asked", "about_your_file"):
        for entry in document.get(section) or []:
            offered = [f"{choice['answer']}" for choice in entry["answers_you_can_give"]]
            for (column, word), answer in given.items():
                if entry.get("column") == column and word in offered and not entry.get("your_answer"):
                    entry["your_answer"] = answer
                    answered = True
    questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
    return answered


def test_at_the_table_floor_the_rare_keys_are_named_only_after_no_and_each_key_keeps_its_values(tmp_path: pathlib.Path) -> None:
    form = key_value_tables.recorded_items()
    source = tmp_path / "items.csv"
    source.write_text(key_value_tables.csv_text(form), encoding="utf-8", newline="\n")
    rare = key_value_tables.rare_keys(form)
    assert _run(["profile", f"{source}", "--replace"]) == 0
    unanswered = (tmp_path / "items-profile.json").read_text(encoding="utf-8")
    assert not [key for key in rare if f'"{key}"' in unanswered]
    questions = tmp_path / "items-questions.json"
    given = {
        ("patient_id", "identifier"): "identifier", ("item_key", "no"): "no",
        ("item_value", "yes"): "yes", ("item_value", "keyed"): "keyed",
    }
    for _round in range(4):
        if not _answer(questions, given):
            break
        assert _run(["profile", f"{source}", "--replace", "--answers", f"{questions}"]) == 0
    described = json.loads((tmp_path / "items-profile.json").read_text(encoding="utf-8"))
    names = _block(described, "item_key")["held_back_names"]
    assert isinstance(names, list) and sorted(names) == sorted(rare)
    assert "by_key" in _block(described, "item_value")
    assert _run(["generate", f"{tmp_path / 'items-profile.json'}", "--replace", "--seed", "0"]) == 0
    with open(tmp_path / "items-twin.csv", newline="", encoding="utf-8") as handle:
        twin = list(csv.reader(handle))
    head = twin[0]
    key_at, value_at = head.index("item_key"), head.index("item_value")
    every_key = {row[2] for row in form.rows}
    assert not [row for row in twin[1:] if row[key_at] and row[key_at] not in every_key]
    real = sorted(float(row[3]) for row in form.rows if row[2] == "systolic_pressure")
    low, high = real[len(real) // 100], real[len(real) - 1 - len(real) // 100]
    made = [float(row[value_at]) for row in twin[1:] if row[key_at] == "systolic_pressure"]
    inside = len([value for value in made if low <= value <= high])
    assert made and 100 * inside >= 95 * len(made)
