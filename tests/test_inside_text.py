"""The text zone of the inside record (lane TYPES-24): cells with a structure of their own written in the real column's templates.

Each case builds a made-up column, reads it into the zone as the describe
step does (`inside_text.entry_of`), and writes a twin column again from a
stand-in twin of the description's shape (`inside_text.write_column`):
the cells' structure must read back as an analyst reads the real one, every
count of the description's twin must stand, and the privacy rules -- a word
few people write is never kept, a record number never equals a real one, a
date's day of the month is made up -- must hold. Each guard has a mutant that
turns its case red.
"""

from __future__ import annotations

import collections
import json
import math
import random
import re
import uuid

import pytest

from synthtwin import date_counts, inside_text

ROWS = 6000
FLOOR = 11


def _people(rows: int = ROWS, seed: int = 3) -> "list[int]":
    draw = random.Random(seed)
    return [draw.randrange(rows // 4) for _ in range(rows)]


def _stand_in_twin(cells: "list[str]", keep: "tuple[str, ...]" = ()) -> "list[str]":
    """A stand-in for the description's twin of a column: one filler value for each real value, the rows sharing it as the real's do (a published spelling kept)."""
    names: "dict[str, str]" = {spelling: spelling for spelling in keep}
    out = []
    for cell in cells:
        if cell not in names:
            # The description's filler keeps a value's length and its words (its spaces where the value's are).
            mark = f"{len(names):x}"
            filler = re.sub(r"\S", "!", cell)
            names[cell] = filler[: max(0, len(cell) - len(mark))] + mark
        out += [names[cell]]
    return out


def _twin(cells: "list[str]", mode: str, people: "list[int] | None" = None, seed: int = 7,
          keep: "tuple[str, ...]" = ()) -> "list[str]":
    entry = inside_text.entry_of(cells, mode, list(keep), people if people is not None else _people(len(cells)), FLOOR)
    assert entry is not None
    zone = inside_text.zone_of({"c": entry})
    json.dumps(zone, allow_nan=False)
    written = inside_text.write_column(zone, "c", _stand_in_twin(cells, keep), seed)
    assert written is not None
    return written


def _census(cells: "list[str]") -> "collections.Counter[int]":
    return collections.Counter(collections.Counter(cells).values())


# -- structured text -------------------------------------------------------------------------------------


def _pairs(draw: random.Random) -> str:
    return f"sys={draw.randint(95, 170)};dia={draw.randint(55, 100)};hr={draw.randint(48, 130)}"


def test_key_value_pairs_read_back_inside_their_real_ranges() -> None:
    draw = random.Random(1)
    real = [_pairs(draw) for _ in range(ROWS)]
    twin = _twin(real, inside_text.MODE_FREE)
    for cell in twin:
        found = dict(part.split("=", 1) for part in cell.split(";"))
        assert set(found) == {"sys", "dia", "hr"}
        assert 95 <= int(found["sys"]) <= 170 and 55 <= int(found["dia"]) <= 100 and 48 <= int(found["hr"]) <= 130
    assert len(set(twin)) == len(set(real))
    assert _census(twin) == _census(real)


def test_json_cells_parse_with_their_keys() -> None:
    draw = random.Random(2)
    real = [json.dumps({"sys": draw.randint(95, 170), "dia": draw.randint(55, 100), "pos": draw.choice(["sit", "lie"])})
            for _ in range(ROWS)]
    twin = _twin(real, inside_text.MODE_FREE)
    positions = collections.Counter()
    for cell in twin:
        document = json.loads(cell)
        assert set(document) == {"sys", "dia", "pos"}
        positions[document["pos"]] += 1
    assert set(positions) == {"sit", "lie"}
    assert abs(positions["sit"] / ROWS - 0.5) < 0.05


def test_a_waveform_keeps_its_shape_across_the_cell() -> None:
    draw = random.Random(3)
    real = ["[" + ", ".join(f"{0.8 * math.sin(step / 2) + draw.gauss(0, 0.02):.3f}" for step in range(8)) + "]"
            for _ in range(ROWS)]
    twin = _twin(real, inside_text.MODE_FREE)
    means = [0.0] * 8
    for cell in twin:
        values = json.loads(cell)
        assert len(values) == 8 and all(isinstance(value, float) for value in values)
        for place in range(8):
            means[place] += values[place] / ROWS
    for place in range(8):
        assert abs(means[place] - 0.8 * math.sin(place / 2)) < 0.02


def test_a_comment_holding_a_pressure_keeps_its_words_and_a_pressure() -> None:
    draw = random.Random(4)
    real = [f"BP {draw.randint(95, 170)}/{draw.randint(55, 100)} {draw.choice(('L', 'R'))} arm"
            if draw.random() < 0.5 else draw.choice(("pt refused", "see note")) for _ in range(ROWS)]
    keep = ("pt refused", "see note")
    twin = _twin(real, inside_text.MODE_TAIL, keep=keep)
    for cell in twin:
        assert cell in keep or re.fullmatch(r"BP \d{2,3}/\d{2,3} (L|R) arm", cell), cell
    assert sum(1 for cell in twin if cell in keep) == sum(1 for cell in real if cell in keep)


def test_free_text_keeps_each_value_s_length_and_the_column_s_counts() -> None:
    draw = random.Random(5)
    sentences = ("The patient was seen today.", "No acute distress.", "Plan reviewed.", "Return in two weeks.")
    real = [" ".join(draw.choice(sentences) for _ in range(draw.randint(3, 9))) for _ in range(ROWS)]
    stand_in = _stand_in_twin(real)
    entry = inside_text.entry_of(real, inside_text.MODE_FREE, [], _people(), FLOOR)
    assert entry is not None
    twin = inside_text.write_column(inside_text.zone_of({"c": entry}), "c", stand_in, 11)
    assert twin is not None
    assert sum(len(cell) for cell in twin) == sum(len(cell) for cell in stand_in)
    assert min(len(cell) for cell in twin) == min(len(cell) for cell in stand_in)
    assert max(len(cell) for cell in twin) == max(len(cell) for cell in stand_in)
    assert len(set(twin)) == len(set(stand_in))
    words = {word for cell in twin for word in re.findall(r"[A-Za-z]+", cell)}
    assert words & {"patient", "distress", "Plan"}


# -- dates written as text -------------------------------------------------------------------------------


FRENCH = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre",
          "décembre")


def _french(draw: random.Random) -> str:
    day = 15
    month = draw.randrange(12)
    return f"{day} {FRENCH[month]} {draw.randint(2000, 2023)}"


def test_a_date_in_another_language_is_held_as_a_date_in_disguise() -> None:
    for cell in ("5 mars 2023", "5. März 2023", "5 de marzo de 2023", "1er janvier 2023", "12 maart 2022"):
        assert date_counts.date_in_disguise(cell), cell
    for cell in ("pt refused", "Mayo Clinic", "Mars 2 rover", "BP 141/74 L arm", "seen in May"):
        assert not date_counts.date_in_disguise(cell), cell


def test_a_date_in_french_is_written_with_a_made_up_day_and_the_column_s_own_months() -> None:
    draw = random.Random(6)
    real = [_french(draw) for _ in range(ROWS)]
    twin = _twin(real, inside_text.MODE_FREE)
    days = collections.Counter()
    for cell in twin:
        found = re.fullmatch(r"(\d{1,2}) (\w+) (\d{4})", cell)
        assert found, cell
        assert found.group(2) in FRENCH
        assert 2000 <= int(found.group(3)) <= 2023
        days[int(found.group(1))] += 1
    # Every real date falls on the 15th; the twin keeps each month's weekday and makes the day up among the days of
    # that weekday (the 1st, 8th, 15th, 22nd and 29th), so about one twin date in four or five falls on the 15th --
    # every one would, were the day copied.
    assert set(days) <= {1, 8, 15, 22, 29}
    assert len(days) >= 4
    assert days[15] < 0.5 * ROWS


def test_a_date_in_figures_inside_free_text_is_made_up_too() -> None:
    draw = random.Random(7)
    real = [f"seen {draw.randint(1, 12):02d}/15/{draw.randint(2000, 2023)}" for _ in range(ROWS)]
    twin = _twin(real, inside_text.MODE_FREE)
    fifteenth = sum(1 for cell in twin if re.fullmatch(r"seen \d{2}/15/\d{4}", cell))
    assert all(re.fullmatch(r"seen \d{2}/\d{1,2}/\d{4}", cell) for cell in twin)
    # Every real cell is fifteen characters long, so the twin keeps two figures of a day: the 15th, 22nd or 29th.
    assert fifteenth < 0.5 * ROWS


# -- record numbers --------------------------------------------------------------------------------------


def _luhn(figures: str) -> str:
    total = 0
    for place, figure in enumerate(reversed(figures)):
        value = int(figure) * (2 if place % 2 == 0 else 1)
        total += value - 9 if value > 9 else value
    return figures + f"{(10 - total % 10) % 10}"


def _passes_luhn(key: str) -> bool:
    return _luhn(key[:-1]) == key


def test_keys_with_a_check_figure_pass_it_and_none_is_a_real_key() -> None:
    real = [_luhn(f"{300000000 + row * 7:09d}") for row in range(ROWS)]
    twin = _twin(real, inside_text.MODE_IDENTIFIER, people=list(range(ROWS)))
    assert all(_passes_luhn(cell) and len(cell) == 10 for cell in twin)
    assert not set(twin) & set(real)
    assert len(set(twin)) == len(set(real))


def test_uuids_keep_their_version_and_variant_figures() -> None:
    draw = random.Random(8)
    real = [f"{uuid.UUID(int=draw.getrandbits(128), version=4)}" for _ in range(ROWS)]
    twin = _twin(real, inside_text.MODE_IDENTIFIER, people=list(range(ROWS)))
    pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"
    assert all(re.fullmatch(pattern, cell) for cell in twin)
    assert not set(twin) & set(real)


def test_ip_addresses_keep_their_octets_and_none_is_a_real_one() -> None:
    draw = random.Random(9)
    real = [f"192.0.2.{draw.randint(1, 254)}" if draw.random() < 0.5 else f"198.51.100.{draw.randint(1, 254)}"
            for _ in range(ROWS)]
    twin = _twin(real, inside_text.MODE_IDENTIFIER)
    for cell in twin:
        octets = [int(part) for part in cell.split(".")]
        assert len(octets) == 4 and all(0 <= octet <= 255 for octet in octets), cell
    assert not set(twin) & set(real)


def test_a_composite_key_keeps_its_letter_and_its_line_numbers() -> None:
    people = _people()
    draw = random.Random(10)
    real = [f"P{4000000 + people[row]:07d}-{draw.randint(1, 12):02d}" for row in range(ROWS)]
    twin = _twin(real, inside_text.MODE_IDENTIFIER, people=people)
    assert all(re.fullmatch(r"P\d{7}-(0[1-9]|1[0-2])", cell) for cell in twin)
    assert not set(twin) & set(real)
    assert _census(twin) == _census(real)


def test_a_url_keeps_its_path_and_none_is_a_real_one() -> None:
    people = _people()
    draw = random.Random(11)
    real = [f"https://records.example.org/chart/P{4000000 + people[row]:07d}/{draw.randint(100000, 999999)}"
            for row in range(ROWS)]
    twin = _twin(real, inside_text.MODE_IDENTIFIER, people=people)
    assert all(re.fullmatch(r"https://records\.example\.org/chart/P\d{7}/\d{6}", cell) for cell in twin)
    assert not set(twin) & set(real)


def test_base64_tokens_stay_base64_of_their_length() -> None:
    import base64

    draw = random.Random(12)
    real = [base64.b64encode(bytes(draw.getrandbits(8) for _ in range(24))).decode("ascii") for _ in range(ROWS)]
    twin = _twin(real, inside_text.MODE_FREE, people=list(range(ROWS)))
    assert all(re.fullmatch(r"[A-Za-z0-9+/]{32}", cell) for cell in twin)
    assert not set(twin) & set(real)


# -- privacy ---------------------------------------------------------------------------------------------


def test_a_word_fewer_than_the_floor_of_people_write_is_never_kept() -> None:
    draw = random.Random(13)
    people = _people()
    real = []
    for row in range(ROWS):
        # A made-up name the rows of five people hold, beside common words.
        name = "Quillanbrook" if people[row] < 5 else "nurse"
        real += [f"called {name} at {draw.randint(1, 12)} pm"]
    twin = _twin(real, inside_text.MODE_FREE, people=people)
    assert not any("Quillanbrook" in cell for cell in twin)
    assert any("nurse" in cell for cell in twin)


def test_a_note_writing_a_phone_number_gives_no_template() -> None:
    """Amended at batch 4zz's fix round (the outside review's item 4): a note's telephone number was drawn figure group
    by figure group from the real groups' census, and every draw was a real number; a note the twin checks read as
    writing one is now read into no template, and the column is left as the description's twin writes it."""
    draw = random.Random(14)
    real = [f"call 555-{draw.randint(1000, 9999)}" for _ in range(ROWS)]
    assert inside_text.entry_of(real, inside_text.MODE_FREE, [], _people(), FLOOR) is None


def test_the_zone_is_a_fixed_function_of_its_seed() -> None:
    draw = random.Random(15)
    real = [_pairs(draw) for _ in range(ROWS)]
    assert _twin(real, inside_text.MODE_FREE, seed=3) == _twin(real, inside_text.MODE_FREE, seed=3)
    assert _twin(real, inside_text.MODE_FREE, seed=3) != _twin(real, inside_text.MODE_FREE, seed=4)


def test_a_held_column_is_filled_as_the_real_column_held() -> None:
    draw = random.Random(16)
    real = [_french(draw) for _ in range(ROWS)]
    held = [True for _ in range(ROWS)]
    entry = inside_text.entry_of(real, inside_text.MODE_HELD, [], _people(), FLOOR, held)
    assert entry is not None
    zone = inside_text.zone_of({"c": entry})
    assert inside_text.held_of(zone) == {"c"}
    filled = inside_text.write_column(zone, "c", ["" for _ in range(ROWS)], 5)
    assert filled is not None
    assert sum(1 for cell in filled if cell) == ROWS
    assert all(re.fullmatch(r"\d{1,2} \w+ \d{4}", cell) for cell in filled)


def test_a_zone_of_another_version_is_refused() -> None:
    with pytest.raises(inside_text.TextError):
        inside_text.write_column({"version": 0, "columns": {}}, "c", ["a"], 1)


# -- the mutants: each guard above turns its case red when taken away ----------------------------------------


def test_mutant_a_floor_of_one_keeps_the_name(monkeypatch: pytest.MonkeyPatch) -> None:
    draw = random.Random(13)
    people = _people()
    real = [f"called {'Quillanbrook' if people[row] < 5 else 'nurse'} at {draw.randint(1, 12)} pm" for row in range(ROWS)]
    entry = inside_text.entry_of(real, inside_text.MODE_FREE, [], people, 1)
    assert entry is not None
    twin = inside_text.write_column(inside_text.zone_of({"c": entry}), "c", _stand_in_twin(real), 7)
    assert twin is not None and any("Quillanbrook" in cell for cell in twin)


def test_a_key_template_with_no_mark_and_little_room_is_left_as_the_description_s_twin_wrote_it() -> None:
    real = [_luhn(f"{300000000 + row * 7:09d}") for row in range(ROWS)]
    entry = inside_text.entry_of(real, inside_text.MODE_IDENTIFIER, [], list(range(ROWS)), FLOOR)
    assert entry is not None
    for key in entry["templates"]:  # type: ignore[union-attr]
        entry["templates"][key]["mark"] = []  # type: ignore[index]
    assert inside_text.write_column(inside_text.zone_of({"c": entry}), "c", _stand_in_twin(real), 7) is None


def test_mutant_no_mark_and_no_room_rule_lets_keys_equal_real_ones(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(inside_text, "ENTROPY_BITS", 0)
    real = [_luhn(f"{300000000 + row * 7:09d}") for row in range(ROWS)]
    entry = inside_text.entry_of(real, inside_text.MODE_IDENTIFIER, [], list(range(ROWS)), FLOOR)
    assert entry is not None
    for key in entry["templates"]:  # type: ignore[union-attr]
        entry["templates"][key]["mark"] = []  # type: ignore[index]
    twin = inside_text.write_column(inside_text.zone_of({"c": entry}), "c", _stand_in_twin(real), 7)
    assert twin is not None and set(twin) & set(real)


def test_mutant_no_check_figure_breaks_the_luhn_case() -> None:
    real = [_luhn(f"{300000000 + row * 7:09d}") for row in range(ROWS)]
    entry = inside_text.entry_of(real, inside_text.MODE_IDENTIFIER, [], list(range(ROWS)), FLOOR)
    assert entry is not None
    for key in entry["templates"]:  # type: ignore[union-attr]
        entry["templates"][key]["luhn"] = False  # type: ignore[index]
    twin = inside_text.write_column(inside_text.zone_of({"c": entry}), "c", _stand_in_twin(real), 7)
    assert twin is not None and not all(_passes_luhn(cell) for cell in twin)


def test_mutant_dates_read_as_plain_numbers_copy_the_real_day(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(inside_text, "dated", lambda tokens: tokens)
    draw = random.Random(7)
    real = [f"seen {draw.randint(1, 12):02d}/15/{draw.randint(2000, 2023)}" for _ in range(ROWS)]
    twin = _twin(real, inside_text.MODE_FREE)
    assert sum(1 for cell in twin if re.fullmatch(r"seen \d{2}/15/\d{4}", cell)) >= 0.9 * ROWS


def test_mutant_no_balance_misses_the_length_in_all(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(inside_text, "_balanced", lambda *arguments: None)
    draw = random.Random(1)
    real = [_pairs(draw) for _ in range(ROWS)]
    stand_in = _stand_in_twin(real)
    entry = inside_text.entry_of(real, inside_text.MODE_FREE, [], _people(), FLOOR)
    assert entry is not None
    twin = inside_text.write_column(inside_text.zone_of({"c": entry}), "c", stand_in, 7)
    assert twin is not None and sum(len(cell) for cell in twin) != sum(len(cell) for cell in stand_in)


def test_mutant_english_months_only_leaves_french_dates_unheld(monkeypatch: pytest.MonkeyPatch) -> None:
    for word in date_counts.FOREIGN_MONTH_WORDS:
        monkeypatch.delitem(date_counts._MONTH_WORDS, word)
    assert not date_counts.date_in_disguise("5 mars 2023")


# -- measurements dealt from the real census (`MODE_CENSUS`) --------------------------------------------------


def _percent(draw: random.Random) -> str:
    value = min(max(draw.gauss(45, 15), 0), 100)
    return f"{value:.1f}%" if draw.random() < 0.5 else f"{round(value)}%"


def _census_twin(real: "list[str]", stand_in: "list[str]") -> "list[str]":
    entry = inside_text.entry_of(real, inside_text.MODE_CENSUS, [], None, FLOOR)
    assert entry is not None
    zone = inside_text.zone_of({"c": entry})
    assert inside_text.dealt_in_order(zone, "c")
    written = inside_text.write_column(zone, "c", stand_in, 1)
    assert written is not None
    return written


def test_a_measurement_written_two_ways_keeps_the_real_spellings_and_the_order() -> None:
    draw = random.Random(21)
    real = [_percent(draw) for _ in range(ROWS)]
    # The description's twin: numbers of the column's shape, in an order a relations zone chose.
    stand_in = [f"{min(max(draw.gauss(45, 15), 0), 100):.1f}%" for _ in range(ROWS)]
    twin = _census_twin(real, stand_in)
    assert collections.Counter(twin) == collections.Counter(real)
    ranked = sorted(range(ROWS), key=lambda row: float(stand_in[row][:-1]))
    values = [float(twin[row][:-1]) for row in ranked]
    assert values == sorted(values)


def test_a_negative_zero_and_a_dose_s_unit_are_written_as_the_real_writes_them() -> None:
    draw = random.Random(22)
    real = [("-0.0" if draw.random() < 0.5 else "0.0") if abs(value) < 0.05 else f"{value:.1f}"
            for value in (draw.gauss(0, 0.4) for _ in range(ROWS))]
    twin = _census_twin(real, [f"{draw.gauss(0, 0.4):.1f}" for _ in range(ROWS)])
    assert twin.count("-0.0") == real.count("-0.0")
    amounts = [draw.choice(("5 mg", "12.5 mg", "500 mg", "2.5 mL", "1 g")) for _ in range(ROWS)]
    twin = _census_twin(amounts, [f"{draw.choice((5, 11, 499.5, 2.5, 1))} mg" for _ in range(ROWS)])
    assert collections.Counter(twin) == collections.Counter(amounts)


def test_the_census_keeps_blank_and_missing_cells_where_they_stand() -> None:
    real = ["5 mg", "", "NULL", "10 mg"] * 100
    entry = inside_text.entry_of(real, inside_text.MODE_CENSUS, ["NULL"], None, FLOOR)
    assert entry is not None
    twin = inside_text.write_column(inside_text.zone_of({"c": entry}), "c", ["7 mg", "", "NULL", "9 mg"] * 100, 1)
    assert twin is not None
    assert twin[1::4] == [""] * 100 and twin[2::4] == ["NULL"] * 100
    assert collections.Counter(twin[0::4] + twin[3::4]) == collections.Counter({"5 mg": 100, "10 mg": 100})


def test_the_census_is_refused_for_possible_ages_and_long_runs_of_figures() -> None:
    from synthtwin import cli

    ages = [f"{age}" for age in range(0, 110)] * 50
    assert not cli._census_allowed("years", ages, [])
    assert cli._census_allowed("systolic", [f"{value}" for value in range(80, 200)] * 50, [])
    assert not cli._census_allowed("result", ["52242", "52240", "4.5"] * 100, [])
    assert cli._census_allowed("dose", ["5 mg", "12.5 mg", "-0.0", "45%"] * 100, [])


def test_mutant_without_the_census_the_real_spellings_are_lost(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(inside_text, "_census_dealt", lambda entry, cells: [cell for cell in cells])
    draw = random.Random(22)
    real = [("-0.0" if draw.random() < 0.5 else "0.0") if abs(value) < 0.05 else f"{value:.1f}"
            for value in (draw.gauss(0, 0.4) for _ in range(ROWS))]
    twin = _census_twin(real, [f"{draw.gauss(0, 0.4):.1f}" for _ in range(ROWS)])
    assert twin.count("-0.0") != real.count("-0.0")


def test_mutant_no_age_screen_lets_ages_past_89_through(monkeypatch: pytest.MonkeyPatch) -> None:
    from synthtwin import cli

    monkeypatch.setattr(cli, "_CENSUS_AGE_MOST", -1)
    assert cli._census_allowed("years", [f"{age}" for age in range(0, 110)] * 50, [])


# -- the command's choice of each column's mode (`cli._text_zone_mode`) and the held column's excusal ---------------


def _block(name: str, role: str, **more: object) -> "dict[str, object]":
    block: "dict[str, object]" = {"name": name, "role": role, "missing_by_source": {"NULL": 3}}
    block.update(more)
    return block


def test_each_column_takes_the_mode_its_reading_calls_for() -> None:
    from synthtwin import cli, inside_relations

    assert cli._text_zone_mode(_block("note", "free_text"), "", ()) == (inside_text.MODE_FREE, ["NULL"])
    assert cli._text_zone_mode(_block("visit_line", "identifier"), inside_relations.AN_IDENTIFIER, ())[0] == \
        inside_text.MODE_IDENTIFIER
    assert cli._text_zone_mode(_block("person", "identifier"), inside_relations.NAMES_THE_PERSON, ()) == ("", [])
    assert cli._text_zone_mode(_block("seen", "empty"), "", ("seen",))[0] == inside_text.MODE_HELD
    tail = _block("comment", "long_tail_labels", suppressed_rows=40,
                  levels=[{"label": "see note", "variants": {"see note": 900, "See note": 12}}])
    assert cli._text_zone_mode(tail, "", ()) == (inside_text.MODE_TAIL, ["NULL", "see note", "See note"])
    assert cli._text_zone_mode(_block("comment", "long_tail_labels", suppressed_rows=0), "", ()) == ("", [])
    assert cli._text_zone_mode(_block("dose", "affixed_number"), "", ())[0] == inside_text.MODE_CENSUS
    assert cli._text_zone_mode(_block("years_old", "count"), "", ()) == ("", [])
    assert cli._text_zone_mode(_block("weight", "continuous", top_coded=90), "", ()) == ("", [])
    assert cli._text_zone_mode(_block("visit_day", "datetime"), "", ()) == ("", [])


def test_a_held_column_the_zone_fills_is_named_for_validate_s_excusal() -> None:
    from synthtwin import cli

    draw = random.Random(16)
    real = [_french(draw) for _ in range(ROWS)]
    entry = inside_text.entry_of(real, inside_text.MODE_HELD, [], _people(), FLOOR, [True] * ROWS)
    free = inside_text.entry_of([_pairs(draw) for _ in range(ROWS)], inside_text.MODE_FREE, [], _people(), FLOOR)
    assert entry is not None and free is not None
    zones = {inside_text.ZONE: inside_text.zone_of({"seen": entry, "note": free})}
    assert cli._text_held_filled(zones) == {"seen"}
    assert cli._text_held_filled({}) == set()


def test_mutant_a_zone_that_names_no_held_column_leaves_the_fill_unexcused(monkeypatch: pytest.MonkeyPatch) -> None:
    from synthtwin import cli

    monkeypatch.setattr(inside_text, "held_of", lambda zone: set())
    draw = random.Random(16)
    entry = inside_text.entry_of([_french(draw) for _ in range(ROWS)], inside_text.MODE_HELD, [], _people(), FLOOR,
                                 [True] * ROWS)
    assert cli._text_held_filled({inside_text.ZONE: inside_text.zone_of({"seen": entry})}) == set()


# -- keys written as free text are kept off the real (found by tests/test_inside_accounts.py on this lane) ----------


def _keys(draw: random.Random) -> str:
    return f"{draw.choice('PQ')}{draw.randint(1000000, 9999999)}"


def test_a_column_of_keys_read_as_free_text_never_writes_a_real_key() -> None:
    draw = random.Random(31)
    real = [_keys(draw) for _ in range(ROWS)]
    twin = _twin(real, inside_text.MODE_FREE, people=list(range(ROWS)))
    assert not set(twin) & set(real)
    assert all(re.fullmatch(r"[PQ]\d{7}", cell) for cell in twin)


def test_a_long_run_of_figures_in_a_note_whose_every_opening_is_real_is_written_wider() -> None:
    draw = random.Random(32)
    real = [f"call back {draw.randint(1000000, 9999999)} today" for _ in range(ROWS)]
    twin = _twin(real, inside_text.MODE_FREE)
    real_runs = {re.search(r"\d+", cell).group() for cell in real}  # type: ignore[union-attr]
    twin_runs = [re.search(r"\d+", cell).group() for cell in twin]  # type: ignore[union-attr]
    assert not set(twin_runs) & real_runs
    assert all(len(run) == 8 for run in twin_runs)


def _chart_links(draw: random.Random) -> str:
    return f"https://records.example.org/chart/P{draw.randint(1000, 1999):07d}/{draw.randint(100000, 999999)}"


def test_a_link_whose_first_run_is_off_the_real_keeps_its_last_run_of_six_figures() -> None:
    draw = random.Random(33)
    real = [_chart_links(draw) for _ in range(ROWS)]
    twin = _twin(real, inside_text.MODE_FREE, people=list(range(ROWS)))
    assert not set(twin) & set(real)
    assert all(re.fullmatch(r"https://records\.example\.org/chart/P\d{7}/\d{6}", cell) for cell in twin)


def test_mutant_every_run_left_on_a_real_opening_written_wider_breaks_the_link(monkeypatch: pytest.MonkeyPatch) -> None:
    original = inside_text._run_off

    def never_off(writer: object, written: str) -> "bool | None":
        return None if original(writer, written) is None else False  # type: ignore[arg-type]

    monkeypatch.setattr(inside_text, "_run_off", never_off)
    draw = random.Random(33)
    real = [_chart_links(draw) for _ in range(ROWS)]
    twin = _twin(real, inside_text.MODE_FREE, people=list(range(ROWS)))
    assert not all(re.fullmatch(r"https://records\.example\.org/chart/P\d{7}/\d{6}", cell) for cell in twin)


def test_mutant_keys_read_word_by_word_and_runs_left_as_drawn_copy_real_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(inside_text, "_key_shaped", lambda cells: False)
    monkeypatch.setattr(inside_text, "_opened_off", lambda writer, written, wider=True: written)
    draw = random.Random(31)
    real = [_keys(draw) for _ in range(ROWS)]
    twin = _twin(real, inside_text.MODE_FREE, people=list(range(ROWS)))
    assert set(twin) & set(real)


def _durations(draw: random.Random) -> str:
    hours = draw.choices((0, draw.randint(1, 23)), (40, 60))[0]
    minutes = draw.randint(1, 59)
    return f"{hours}h {minutes}m" if hours else f"{minutes}m"


def _duration_tail() -> "tuple[list[str], tuple[str, ...], list[str]]":
    """Durations whose minutes alone are published levels (held by many rows): the tail is the rarer pairs and minutes."""
    draw = random.Random(41)
    real = [_durations(draw) for _ in range(ROWS)]
    counts = collections.Counter(real)
    keep = tuple(sorted(cell for cell in counts if counts[cell] >= 40))
    names: "dict[str, str]" = {}
    stand_in = []
    for cell in real:
        if cell not in keep and cell not in names:
            names[cell] = f"group-{len(names)}"
        stand_in += [cell if cell in keep else names[cell]]
    return real, keep, stand_in


def _tail_twin(real: "list[str]", keep: "tuple[str, ...]", stand_in: "list[str]") -> "list[str]":
    entry = inside_text.entry_of(real, inside_text.MODE_TAIL, list(keep), _people(), FLOOR)
    assert entry is not None
    twin = inside_text.write_column(inside_text.zone_of({"c": entry}), "c", stand_in, 3)
    assert twin is not None
    return twin


def test_a_tail_whose_short_template_runs_out_writes_its_values_in_another() -> None:
    real, keep, stand_in = _duration_tail()
    twin = _tail_twin(real, keep, stand_in)
    assert not [cell for cell in twin if cell.startswith("group-")]
    assert all(re.fullmatch(r"(\d+h )?\d+m", cell) for cell in twin)


def test_mutant_without_the_hand_over_a_value_keeps_its_stand_in(monkeypatch: pytest.MonkeyPatch) -> None:
    original = inside_text._value_for
    failed: "set[str]" = set()

    def once(writer: object, cell: str, key: str, *rest: object) -> str:
        if cell in failed:
            return cell
        found = original(writer, cell, key, *rest)  # type: ignore[arg-type]
        if found == cell:
            failed.add(cell)
        return found

    monkeypatch.setattr(inside_text, "_value_for", once)
    real, keep, stand_in = _duration_tail()
    twin = _tail_twin(real, keep, stand_in)
    assert [cell for cell in twin if cell.startswith("group-")]


# -- several codes a cell (found by the battery's typed_clinical on this lane: 2,980 stand-ins before) ------------

_CODES = ("E66.9", "K21.9", "N18.3", "E11.9", "I48.91", "F32.9", "E78.5", "J44.9", "Z79.4", "G47.33", "M54.5",
          "R07.9", "J45.909", "I10")


def _code_tail() -> "tuple[list[str], tuple[str, ...], list[str]]":
    draw = random.Random(43)
    real = [";".join(draw.sample(_CODES, draw.choices((1, 2, 3), (50, 35, 15))[0])) for _ in range(ROWS)]
    counts = collections.Counter(real)
    keep = tuple(sorted(cell for cell in counts if counts[cell] >= FLOOR))
    names: "dict[str, str]" = {}
    stand_in = []
    for cell in real:
        if cell not in keep and cell not in names:
            names[cell] = f"group-{len(names)}"
        stand_in += [cell if cell in keep else names[cell]]
    return real, keep, stand_in


def test_a_tail_of_several_codes_a_cell_is_written_as_lists_of_the_real_codes() -> None:
    real, keep, stand_in = _code_tail()
    twin = _tail_twin(real, keep, stand_in)
    assert not [cell for cell in twin if cell.startswith("group-")]
    assert all(set(cell.split(";")) <= set(_CODES) and len(set(cell.split(";"))) == len(cell.split(";")) for cell in twin)
    assert len(set(twin)) == len(set(real))
    tail_sizes = collections.Counter(len(cell.split(";")) for cell in set(real) if cell not in keep)
    assert collections.Counter(len(cell.split(";")) for cell in set(twin) if cell not in keep) == tail_sizes
    assert [cell for cell in twin if cell in keep] == [cell for cell in real if cell in keep]


def test_mutant_a_tail_of_lists_read_as_templates_keeps_its_stand_ins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(inside_text, "_list_facts", lambda *args: None)
    real, keep, stand_in = _code_tail()
    entry = inside_text.entry_of(real, inside_text.MODE_TAIL, list(keep), _people(), FLOOR)
    twin = stand_in if entry is None else inside_text.write_column(inside_text.zone_of({"c": entry}), "c", stand_in, 3)
    assert twin is not None
    assert [cell for cell in twin if cell.startswith("group-") or not set(cell.split(";")) <= set(_CODES)]


# -- keys the description's twin writes wider than the real (found by tests/test_inside_links.py on this lane) -----


def _spilled_keys() -> "tuple[list[str], list[str]]":
    draw = random.Random(47)
    real = [f"P{key}" for key in draw.sample(range(1000000, 10000000), ROWS)]
    spilled = [f"P{key}" for key in draw.sample(range(100000000, 1000000000), ROWS)]
    return real, spilled


def _identifier_twin(real: "list[str]", described: "list[str]") -> "list[str] | None":
    entry = inside_text.entry_of(real, inside_text.MODE_IDENTIFIER, [], list(range(ROWS)), FLOOR)
    assert entry is not None
    return inside_text.write_column(inside_text.zone_of({"c": entry}), "c", described, 3)


def test_keys_the_description_s_twin_writes_wider_than_every_real_key_are_left_for_a_linked_twin() -> None:
    real, spilled = _spilled_keys()
    assert _identifier_twin(real, spilled) is None
    assert _identifier_twin(real, [f"Z{key[1:]}" for key in real]) is not None


def test_mutant_keys_written_again_at_the_real_width_drop_below_the_link_s_bound(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(inside_text, "_wider_than_real", lambda writer, cells: False)
    real, spilled = _spilled_keys()
    twin = _identifier_twin(real, spilled)
    assert twin is not None and min(len(cell) for cell in twin) <= max(len(cell) for cell in real)
