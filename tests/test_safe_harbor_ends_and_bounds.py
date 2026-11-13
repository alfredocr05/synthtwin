"""An age column counted in people, the top code's bound, and a pool's start after `no` (lane HB2, plan P4-D477, parts 2 and 3).

(2) THE PEOPLE-COUNTED AGE READING (the orchestrator's LANE GRb RULINGS 2 (2)
and 3 (4)): a visit table's ages of about 3,000 patients beside its patient
column was held whole as record numbers, a value it published (its youngest
ages, its first and 99th percentiles, its largest) held by 4 to 10 patients,
so its twin wrote stand-ins a row and twin patients held two ages; its ends
are now pooled in people, each band held by the floor's people, never past
the top code, and the column is held as before only where that fails.
(3) THE TOP CODE'S BOUND (STATE's 'Lane HB2, its second item'): a column of
numbers whose description publishes the top code writes no twin cell past
it, whatever word follows its number (the vitals export's weight in `kg`
wrote 130.9 to 159.5). THE POOL'S START AFTER `no` (LANE I4m RULINGS 30
(1)): `8888` beside the key `8889`, and `88` beside levels `1` to `5`, each the
column's one rare value, were the pool's constant start and were written on
that person's 20 rows; P4-D442's stand-in rule now keeps the start off every
value the pool holds back. Unit cases generated in thousands; one table at
the owner's floor per writer, the others in `K-HZ-29`'s driver.
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import pathlib
import random

from synthtwin import cli, parsing, taxonomy

FLOOR = 11


def _people_of(cells: "list[str]", subjects: "list[str]") -> "dict[int, set[str]]":
    held: "dict[int, set[str]]" = {}
    for cell, subject in zip(cells, subjects):
        if cell.strip().lstrip("0").isdigit() or cell.strip() == "0":
            held.setdefault(int(cell), set()).add(subject)
    return held


def test_every_generated_end_band_holds_the_floors_people_and_stays_under_the_top_code() -> None:
    """Thousands of drawn age columns beside a patient column: each band and the value beside it hold the floor's people, no value moves past 90, the middle keeps its cells."""
    draw = random.Random(4778)
    pooled = 0
    for _column in range(400):
        patients = draw.randint(200, 3000)
        middle = draw.uniform(30, 70)
        spread = draw.uniform(4, 18)
        ages = [int(min(90, max(0, draw.gauss(middle, spread)))) for _patient in range(patients)]
        rows_a_patient = draw.randint(1, 6)
        subjects = [f"S{patient}" for patient in range(patients) for _row in range(rows_a_patient)]
        cells = [f"{ages[patient]}" for patient in range(patients) for _row in range(rows_a_patient)]
        ends = taxonomy.ends_pooled_in_people(cells, False, frozenset(), FLOOR, 90, [subjects])
        held = _people_of(cells, subjects)
        if ends is None:
            continue
        pooled += 1
        low, high = ends
        assert 0 <= low < high <= 90
        written = taxonomy.cells_within_the_ends(cells, False, frozenset(), low, high)
        after = _people_of(written, subjects)
        assert min(after) == low and max(after) == high
        assert len(after[low]) >= FLOOR and len(after[high]) >= FLOOR
        inside = sorted(value for value in after if low < value < high)
        if inside:
            assert len(after[inside[0]]) >= FLOOR and len(after[inside[-1]]) >= FLOOR
        for before, after_cell in zip(cells, written):
            if low <= int(before) <= high:
                assert after_cell == before
        # ...and the lowest value alone, and the highest, each held by fewer
        # than the floor's people or the band would not have been needed.
        assert len(held[min(held)]) < FLOOR or len(held[max(held)]) < FLOOR
    assert pooled > 100


UNIT_SETS = (("y",), ("m",), ("w",), ("d",), ("y", "m"), ("y", "w"), ("y", "d"), ("m", "w"), ("m", "d"), ("w", "d"))


def _in_unit(draw: random.Random, years: int, unit: str) -> str:
    """One whole age of ``years`` written in a unit the age reader reads: bare, `N years`, `N months`, `N wk`, `N days`."""
    if unit == "y":
        return draw.choice((f"{years}", f"{years} years", f"{years} yrs"))
    mark = taxonomy.AGE_MARKS[unit]
    lowest = -((-years * mark) // 90)
    value = min(mark, draw.randint(lowest, max(lowest, ((years + 1) * mark) // 90 - 1)))
    return f"{value} " + {"m": "months", "w": "wk", "d": "days"}[unit]


def test_every_generated_end_in_every_unit_is_the_columns_and_holds_the_floors_people() -> None:
    """Columns written in years, months, weeks, days and every mixed pair, a few people at each end and the top code itself: the two ends are whole numbers of the column's unit at most its mark -- what the loader admits beside `top_coded` -- each cell compared in that unit and written in its own, each band and the value beside it held by the floor's people (lane HB2's repair 2, Codex's item 1: `600 months` and `960 months` beside bare years drew the ends `[30, 960]`, refused beside the top code 90)."""
    draw = random.Random(4793)
    pooled = 0
    for units in UNIT_SETS:
        for _column in range(16):
            patients = draw.randint(300, 900)
            middle, spread = draw.uniform(35, 65), draw.uniform(4, 14)
            ages = [int(min(89, max(1, draw.gauss(middle, spread)))) for _patient in range(patients)]
            ages[:5] = [max(0, min(ages) - draw.randint(1, 5))] * 5
            ages[5:10] = [90] * 5
            mark = taxonomy.AGE_MARKS[units[0]] if len(units) == 1 and draw.random() < 0.5 else 90
            rows_a_patient = draw.randint(1, 4)
            subjects = [f"S{patient}" for patient in range(patients) for _row in range(rows_a_patient)]
            cells = [_in_unit(draw, ages[patient], draw.choice(units)) for patient in range(patients) for _row in range(rows_a_patient)]
            ends = taxonomy.ends_pooled_in_people(cells, False, frozenset(), FLOOR, mark, [subjects])
            if ends is None:
                continue
            pooled += 1
            low, high = ends
            assert 0 <= low <= high <= mark, (units, mark, ends)
            written = taxonomy.cells_within_the_ends(cells, False, frozenset(), low, high, mark)
            held: "dict[int, set[str]]" = {}
            checked: "dict[tuple[str, str], int]" = {}
            for before, after, subject in zip(cells, written, subjects):
                if (before, after) not in checked:
                    read_before = taxonomy.safe_harbor_number(before, False, True, True)
                    read_after = taxonomy.safe_harbor_number(after, False, True, True)
                    assert read_before is not None and read_after is not None
                    assert taxonomy._cell_age_unit(read_after) == taxonomy._cell_age_unit(read_before), (before, after)
                    checked[(before, after)] = taxonomy.age_in_the_columns_unit(read_after, mark)
                    assert low <= checked[(before, after)] <= high, (units, mark, ends, before, after)
                    if low <= taxonomy.age_in_the_columns_unit(read_before, mark) <= high:
                        assert after == before
                held.setdefault(checked[(before, after)], set()).add(subject)
            assert len(held[low]) >= FLOOR and len(held[high]) >= FLOOR, (units, mark, ends)
    assert pooled > 80


def test_the_ends_keep_each_cells_own_form_and_read_no_name_alone() -> None:
    """`Age 25` is written `Age 27`, `025` is `027`; a cell no age's form, a placeholder and a stray are kept; decimals pool nothing."""
    assert taxonomy.cells_within_the_ends(["Age 25", "025", "n/a", "Age 50", "92"], False, frozenset(), 27, 80) == [
        "Age 27", "027", "n/a", "Age 50", "92"]
    assert taxonomy.ends_pooled_in_people(["25.5", "40", "41"] * 30, False, frozenset(), FLOOR, 90, [[f"S{n}" for n in range(90)]]) is None
    assert taxonomy.ends_pooled_in_people(["25", "40"] * 30, False, frozenset(), FLOOR, 90, []) is None
    # `Age NN` labels: each of 40 people of two rows; the ends 20 and 21, and 70 and 71, five people each.
    cells: "list[str]" = []
    subjects: "list[str]" = []
    for who in range(40):
        age = (20, 21, 45, 46, 70, 71)[min(who // 5, 5)] if who < 30 else 45 + who % 2
        cells += [f"Age {age}"] * 2
        subjects += [f"S{who}"] * 2
    assert taxonomy.ends_pooled_in_people(cells, False, frozenset(), 5, 90, [subjects]) is None
    assert taxonomy.ends_pooled_in_people(cells, False, frozenset(), 6, 90, [subjects]) == (21, 70)
    assert taxonomy.ends_pooled_in_people(cells, False, frozenset(), 6, 90, [subjects], False) is None


def test_a_column_of_numbers_writes_no_cell_past_its_top_code() -> None:
    """`130.9 kg` in a column described as numbers whose description publishes the top code is written at or below 90; a held or label twin's made-up `126O` and `201 lb`, and placeholders, are kept."""
    cells = ["78.5 kg", "130.9 kg", "159.5 kg", "999 kg", "88.0 kg", "NA"]
    bounded = taxonomy.at_most_the_top_code(cells, frozenset({"NA"}), bounded=True)
    for cell in bounded[:3] + bounded[4:5]:
        assert float(cell.split()[0]) <= 90, bounded
    assert bounded[3] == "999 kg" and bounded[5] == "NA"
    assert taxonomy.at_most_the_top_code(["126O", "45"], frozenset(), labels=True)[0] == "126O"
    # ...a held column's made-up number past 125 keeps lane SH3's remainder by the mark.
    assert taxonomy.at_most_the_top_code(["126O", "45"], frozenset(), held=True)[0] == "036O"
    # ...and the bound is passed, never inferred (lane HB2's repair 1, skeptic 1's
    # item 2): the generator passes `held` for no column, so a held column's
    # made-up cells, its facts no column of numbers', keep their layouts.
    assert taxonomy.at_most_the_top_code(["201 lb", "150 mmHg", "126O", "45"], frozenset()) == [
        "201 lb", "150 mmHg", "126O", "45"]
    draw = random.Random(4779)
    for _round in range(3000):
        cell = f"{draw.uniform(0, 400):.{draw.randint(0, 2)}f}" + draw.choice([" kg", " mg", "kg", " cm", "", " years"])
        written = taxonomy.at_most_the_top_code([cell, "45"], frozenset(), bounded=True)[0]
        read = taxonomy.safe_harbor_number(written)
        assert read is not None
        placeholder = read.value == int(read.value) and (
            taxonomy._all_nines(read.value) or taxonomy._a_placeholder_spelling(read.value)
        )
        assert placeholder or taxonomy._in_years(read) <= 90, (cell, written)


def test_a_column_still_held_is_held_from_its_cells_before_the_ends() -> None:
    """The guard of a column the count in people holds once its ends were drawn: held from its cells as written, never from the bands, and a description checked again read as made (lane HB2's repair 1, skeptic 1's item 6, M20)."""
    from synthtwin import profile

    real = ["25", "26", "55", "89"]
    banded = ["27", "27", "55", "82"]
    assert profile._held_from(banded, real, (27, 82), False) == real
    assert profile._held_from(banded, real, (27, 82), True) == banded
    assert profile._held_from(real, [], None, False) == real


def test_the_ends_read_no_value_past_the_mark() -> None:
    """A placeholder past the mark (`999`) few people hold is no age to the ends: the ends drawn with its rows are those drawn without them (lane HB2's repair 1, skeptic 1's item 6, mutant M19)."""
    # ...where its people would fill the top band one value early: 30 and 90
    # each held by 5 people, 31 to 89 by 20 each, `999` by 6. Read as an age,
    # `999` and 90 together hold 11 people beside 89's 20, and the top band
    # would end at 90 where it ends at 89.
    cells: "list[str]" = []
    subjects: "list[str]" = []
    for value in range(30, 91):
        for who in range(5 if value in (30, 90) else 20):
            cells += [f"{value}"] * 2
            subjects += [f"S{value}-{who}"] * 2
    assert taxonomy.ends_pooled_in_people(cells, False, frozenset(), FLOOR, 90, [subjects]) == (31, 89)
    placeholders = ["999"] * 12
    holders = [f"X{who}" for who in range(6) for _row in range(2)]
    assert taxonomy.ends_pooled_in_people(cells + placeholders, False, frozenset(), FLOOR, 90, [subjects + holders]) == (31, 89)
    draw = random.Random(4783)
    for _round in range(60):
        patients = draw.randint(300, 1500)
        ages = [int(min(90, max(20, draw.gauss(55, 13)))) for _patient in range(patients)]
        cells = [f"{age}" for age in ages for _row in range(2)]
        subjects = [f"S{patient}" for patient in range(patients) for _row in range(2)]
        ends = taxonomy.ends_pooled_in_people(cells, False, frozenset(), FLOOR, 90, [subjects])
        placeholders = draw.randint(1, 10)
        cells_with = cells + ["999"] * (2 * placeholders)
        subjects_with = subjects + [f"X{one}" for one in range(placeholders) for _row in range(2)]
        assert taxonomy.ends_pooled_in_people(cells_with, False, frozenset(), FLOOR, 90, [subjects_with]) == ends, (
            patients, placeholders)
        if ends is not None:
            assert taxonomy.cells_within_the_ends(["999"], False, frozenset(), ends[0], ends[1]) == ["999"]


def test_a_pool_after_no_starts_wide_enough_and_off_its_openings() -> None:
    """The start's countdown is at least four figures wide after `no`, and takes an opening its width names where the plain countdown wears none (lane HB2's repair 1, skeptic 1's item 5)."""
    settings = taxonomy.Settings()
    levels = ["1", "2", "3", "4", "5"]
    assert taxonomy.pool_stand_in_starts(levels, levels, (1, 0), settings, frozenset()) == {"number_from": "88", "word_from": ""}
    assert taxonomy.pool_stand_in_starts(levels, levels, (1, 0), settings, frozenset(), False, None, 4) == {
        "number_from": "8888", "word_from": ""}
    codes = ["201", "202", "203", "204"]
    openings = {4: "9|7|6|5|4|3|2|1"}
    assert taxonomy.pool_stand_in_starts(codes, codes, (1, 0), settings, frozenset(), False, openings) is None
    # ...after `no`, a start the openings keep back takes the first free opening, never wider (b61eaa4b held the column).
    assert taxonomy.pool_stand_in_starts(codes, codes, (1, 0), settings, frozenset(), False, openings, 4) == {
        "number_from": "9888", "word_from": ""}
    assert taxonomy.pool_stand_in_starts(levels, levels, (1, 0), settings, frozenset(), False, openings, 4) == {
        "number_from": "9888", "word_from": ""}
    # ...and where its width names no opening it can take, held as before.
    assert taxonomy.pool_stand_in_starts(codes, codes, (1, 0), settings, frozenset(), False, {4: ""}, 4) is None
    # ...and a generated draw: the start is never a held-back number the openings keep back, nor narrower than four.
    draw = random.Random(4780)
    taken = 0
    for _round in range(2000):
        width = draw.randint(1, 3)
        # (two published levels at least: a two-valued column publishing one
        # member of a pair takes the other, which its published facts name.)
        published = sorted({f"{draw.randint(10 ** (width - 1) if width > 1 else 0, 10 ** width - 1)}" for _n in range(draw.randint(2, 6))})
        if len(published) < 2:
            continue
        held = f"{draw.randint(1000, 9999)}"
        kept = {4: "|".join(figure for figure in "987654321" if figure != held[0])}
        starts = taxonomy.pool_stand_in_starts(published, published, (1, 0), settings, frozenset(), False, kept, 4)
        assert starts is not None, (published, held)
        start = starts["number_from"]
        assert len(start) == 4 and start != held and start[0] != held[0] and start[0] in kept[4], (published, held, start)
        taken += int(held[0] == "8")
    assert taken > 100
    # ...IN EVERY FORM THE CODE READERS ACCEPT (lane HB2's repair 2, Codex's
    # item 4): signed, decimal and zero-padded levels beside one rare value
    # held back -- the old start (`+88`, `88.8`), the widened one (`+8888`,
    # `8888.8`) or any other -- the walk's first spellings are never that value,
    # as written or as a number, and the start is a spelling the loader admits.
    families = (
        lambda n: f"{n}", lambda n: f"+{n}", lambda n: f"-{n}", lambda n: f"{n}.1", lambda n: f"+{n}.5", lambda n: f"{n:03d}",
    )
    walked = 0
    for _round in range(3000):
        form = draw.choice(families)
        published = sorted({form(draw.randint(1, 9)) for _n in range(draw.randint(2, 6))})
        if len(published) < 2:
            continue
        rare = draw.choice((form(88), form(8888), form(888), form(draw.randint(1000, 99999)), "+88", "88.8", "8888.8"))
        cells = published * 20 + [rare] * 20
        openings = taxonomy.figure_openings_read(
            {"figure_openings": taxonomy.label_figure_openings(cells, list(published), FLOOR)})
        wanted = draw.randint(1, 3)
        starts = taxonomy.pool_stand_in_starts(published, published, (wanted, 0), settings, frozenset(), False, openings, 4)
        if starts is None:
            continue
        start = starts["number_from"]
        assert parsing.is_a_stand_in_start(start), start
        assert taxonomy._figures_before_the_point(start) >= 4, (published, rare, start)
        for spelling in parsing.stand_ins_from(start, wanted, frozenset(published)):
            assert spelling != rare and parsing.parse_number(spelling) != parsing.parse_number(rare), (published, rare, start)
            walked += 1
    assert walked > 3000


@contextlib.contextmanager
def _nobody_at_the_keyboard():  # type: ignore[no-untyped-def]
    asked = cli._there_is_somebody_to_ask
    cli._there_is_somebody_to_ask = lambda: False
    try:
        yield
    finally:
        cli._there_is_somebody_to_ask = asked


def test_at_the_owner_floor_a_rare_code_equal_to_the_start_is_not_written(tmp_path: pathlib.Path) -> None:
    """`88`, and in a second column `8888`, for person 0 beside levels `1` to `5`, 1,000 people of 20 rows, answered `no`: no rare value in the description or the twin, and the second column's five levels published with a start on a free opening.

    Red on 820d55c3 (the start `88` printed, 20 twin cells), on the mutant
    that drops the width after `no` (``figures_at_least`` 0), and on
    b61eaa4b and the mutant that takes no free opening (`8888`'s column held
    whole as record numbers where the line before published its five
    levels; lane HB2's repair 1, skeptic 1's item 5).
    """
    rows = [
        [f"{100000 + who}", "88" if who == 0 else f"{1 + (who * 20 + row) % 5}",
         "8888" if who == 0 else f"{1 + (who * 20 + row) % 5}"]
        for who in range(1000) for row in range(20)
    ]
    source = tmp_path / "t.csv"
    with open(source, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["patient_key", "kind", "kind_b"])
        writer.writerows(rows)
    screen = io.StringIO()
    declared = ["--identifier", "patient_key"]
    with _nobody_at_the_keyboard(), contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        assert cli.main(["profile", f"{source}", "--out-dir", f"{tmp_path}", "--replace"] + declared) == 0
        document = json.loads((tmp_path / "t-questions.json").read_text(encoding="utf-8"))
        for entry in document["asked"]:
            if entry.get("column") in ("kind", "kind_b"):
                entry["your_answer"] = "no"
        answers = tmp_path / "answers.json"
        answers.write_text(json.dumps(document), encoding="utf-8", newline="\n")
        assert cli.main(["profile", f"{source}", "--out-dir", f"{tmp_path}", "--replace", "--answers", f"{answers}"]
                        + declared) == 0
        assert cli.main(["generate", f"{tmp_path / 't-profile.json'}", "--out-dir", f"{tmp_path}", "--seed", "0", "--replace"]) == 0
    blocks = {one["name"]: one for one in json.loads((tmp_path / "t-profile.json").read_text(encoding="utf-8"))["columns"]}
    with open(tmp_path / "t-twin.csv", encoding="utf-8", newline="") as handle:
        twin = list(csv.reader(handle))
    for name, rare in (("kind", "88"), ("kind_b", "8888")):
        block = blocks[name]
        assert block["role"] == "categorical", (name, block["role"])
        start = block["pool_in_people"]["number_from"]
        assert start != rare, (name, start)
        assert f'"{rare}"' not in json.dumps(block), name
        place = twin[0].index(name)
        assert not [row for row in twin[1:] if row[place] == rare], name
    assert blocks["kind_b"]["pool_in_people"]["number_from"] == "9888"


def test_at_the_owner_floor_a_visit_tables_ages_are_pooled_at_their_ends_in_people(tmp_path: pathlib.Path) -> None:
    """`ST2-AGE` (ages about 55 +/- 12 clamped to 25 to 90, one a patient), seed 22, 3,020 patients and 20,065 rows, through the command: described with its ends pooled in people, every published number the floor's patients hold, its twin valid and the real table meeting its own description read through the ends (exit 0 each); the chain's patient layer classes it patient-fixed and publishes its block with the ends, no number past them.

    Red on 820d55c3 (held as record numbers, classed ineligible, validate
    exit 3), on the mutant that never pools the ends (`profile._END_ROUNDS`
    0), on the mutant that draws them once (`_END_ROUNDS` 1: a bin edge `30`
    six patients hold keeps the hold), and on the mutants of lane HB2's
    repair 1 (skeptic 1's item 6): the validator ignoring the ends (M8), the
    chain reading its cells without them (M9) and the patient layer dropping
    them (M22).
    """
    import dataclasses

    import patient_enumeration

    from synthtwin import chain, profile, reading

    patients = 3020
    header, rows = patient_enumeration.st2_rows(patients, 22, True)
    assert len(rows) == 20065
    path = tmp_path / "st2age.csv"
    path.write_text("\n".join([",".join(header)] + [",".join(row) for row in rows]) + "\n", encoding="utf-8", newline="\n")
    screen = io.StringIO()
    with _nobody_at_the_keyboard(), contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        exits = [cli.main(["profile", f"{path}", "--out-dir", f"{tmp_path}", "--replace", "--identifier", "sid"])]
        exits += [cli.main(["generate", f"{tmp_path / 'st2age-profile.json'}", "--out-dir", f"{tmp_path}", "--seed", "0",
                            "--replace"])]
        exits += [cli.main(["validate", f"{tmp_path / 'st2age-profile.json'}", "--twin", f"{tmp_path / 'st2age-twin.csv'}",
                            "--out-dir", f"{tmp_path}", "--replace"])]
        # ...and the real table checked against its own description, read through
        # the ends it records, as the description was made (validation V15).
        (tmp_path / "real").mkdir()
        exits += [cli.main(["validate", f"{tmp_path / 'st2age-profile.json'}", "--twin", f"{path}",
                            "--out-dir", f"{tmp_path / 'real'}", "--replace"])]
    assert exits == [0, 0, 0, 0], (exits, screen.getvalue()[-2000:])
    document = json.loads((tmp_path / "st2age-profile.json").read_text(encoding="utf-8"))
    block = next(one for one in document["columns"] if one["name"] == "age")
    assert block["role"] == taxonomy.ROLE_COUNT and block["top_coded"] == 90
    low, high = block["top_coded_ends"]
    assert 25 < low < high < 90
    patients_of: "dict[int, set[str]]" = {}
    for row in rows:
        patients_of.setdefault(min(max(int(row[2]), low), high), set()).add(row[0])
    for number in profile._published_in(block, True).numbers:
        if number == int(number) and int(number) in patients_of:
            assert len(patients_of[int(number)]) >= FLOOR, (number, block)
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=FLOOR), person_columns=("sid",))
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    chained = chain.describe(table, document, settings,
                             chain.ChainSwitch("st2age", bytes(range(32)), rows_per_person=chain.ROWS_PERSON))
    assert chained.grain is not None and chained.columns is not None
    classes = {entry["column"]: entry["class"] for entry in chained.grain["classes"]}  # type: ignore[index]
    assert classes["age"] == "patient_fixed"
    published = next(one for one in chained.columns if one["name"] == "age")
    assert published.get("top_coded_ends") == [low, high], published
    points = list(published["percentiles"].values()) + list(published.get("percentiles_between") or []) + [published.get("mode")]
    assert [point for point in points if isinstance(point, (int, float)) and not low <= point <= high] == [], published


def test_at_the_owner_floor_the_ends_take_a_remainder_few_people_hold(tmp_path: pathlib.Path) -> None:
    """Ages about 55 +/- 12 clamped to 25 to 90, one a person, 1,000 people of 20 rows (the statistics check's draw 12): its ends pooled in people and the column freed, every published value the floor's people hold.

    Red on b61eaa4b, whose second round drew the ends (37, 74) and stopped:
    the count in people held the column on its remainder alone -- one age no
    published point named, 140 rows of 7 people -- which the published
    values few people hold could not name, so it was held as record numbers
    (lane HB2's repair 1, the statistics check's item 3); and on the mutant
    that takes no remainder. Beside it, `age_at_entry`, whose name alone puts
    it in the age reach (one person in ten holds a number 126 to 999, which
    without the name takes the column out of it), is held from its cells as
    written and never pooled at its ends (LANE I4m RULINGS 21 (1)): red on the
    mutant that drops that guard (skeptic 1's item 6, M1), which described it
    as ages with its ends pooled and its numbers past 125 read as 90. And
    `age_b`, the check's draw 5, whose ends 36 and 72 left its bin groups of
    38 and of 39 each published with the 200 rows of 10 people (no published
    value names either, its remainder held by many): every bin group it
    publishes is held by the floor's people, the groups few people hold taken
    into the nearer band (LANE HB2 RULINGS 4 (4); red on the mutant that
    counts no group in people).
    """
    import dataclasses

    from synthtwin import parsing, profile, reading

    draw = random.Random(12 * 7919)
    ages = [min(90, max(25, int(round(draw.gauss(55, 12))))) for _person in range(1000)]
    strays = random.Random(101)
    entry = [f"{min(90, max(25, int(strays.gauss(55, 12))))}" if strays.random() < 0.9 else f"{strays.randint(126, 999)}"
             for _person in range(1000)]
    fifth = random.Random(5 * 7919)
    ages_b = [min(90, max(25, int(round(fifth.gauss(55, 12))))) for _person in range(1000)]
    path = tmp_path / "ages.csv"
    path.write_text("sid,age,age_at_entry,age_b\n" + "".join(f"P{who:06d},{ages[who]},{entry[who]},{ages_b[who]}\n"
                                                             for who in range(1000) for _row in range(20)),
                    encoding="utf-8", newline="\n")
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=FLOOR), person_columns=("sid",))
    document = profile.build_document(table, settings, ["sid"], [], [], subjects=["sid"], top_code=True)
    blocks = {one["name"]: one for one in document["columns"]}  # type: ignore[index, union-attr]
    block = blocks["age"]
    assert block["role"] == taxonomy.ROLE_COUNT, block["role"]
    low, high = block["top_coded_ends"]
    people: "dict[int, set[int]]" = {}
    for who in range(1000):
        people.setdefault(min(max(ages[who], low), high), set()).add(who)
    for number in profile._published_in(block, True).numbers:
        if number == int(number) and int(number) in people:
            assert len(people[int(number)]) >= FLOOR, (number, low, high)
    held = blocks["age_at_entry"]
    assert held["role"] == taxonomy.ROLE_IDENTIFIER and "top_coded_ends" not in held, held["role"]
    for name, cells in (("age", ages), ("age_b", ages_b)):
        block = blocks[name]
        assert block["role"] == taxonomy.ROLE_COUNT, (name, block["role"])
        low, high = block["top_coded_ends"]
        lowest = block["percentiles_between"]["p01"] if "p01" in block["percentiles_between"] else block["percentiles"]["p01"]
        highest = block["percentiles"]["p99"] if "p99" in block["percentiles"] else block["percentiles_between"]["p99"]
        assert block["tails"]["low"]["percent"] == 1 and block["tails"]["high"]["percent"] == 99, block["tails"]
        holders: "dict[int, set[int]]" = {}
        for who in range(1000):
            value = min(max(cells[who], low), high)
            if lowest <= value <= highest:
                holders.setdefault(parsing.histogram_bin(value, lowest, highest), set()).add(who)
        for group in block["bin_groups"]:
            union = set().union(*[holders.get(at, set()) for at in range(group["first"], group["last"] + 1)])
            assert not 0 < len(union) < FLOOR, (name, group, len(union))


def test_at_the_owner_floor_a_held_top_coded_column_keeps_its_layouts(tmp_path: pathlib.Path) -> None:
    """`NN.N kg`, one weight a person, 3 per cent past 125, beside a declared person column, 1,000 people of 20 rows, nobody at the keyboard: held and top-coded 90, its twin's made-up cells keep their layouts (three figures past 125 among them), none real, and the twin validates (exit 0).

    Red on b61eaa4b (the bound, inferred as neither held nor labels, reached
    the held column's made-up cells: 580 written 89.5 to 89.9, validate exit
    3 with its length and layout checks missed; lane HB2's repair 1,
    skeptic 1's item 2) and on the mutant that infers it again.
    """
    import re

    draw = random.Random(29)
    weights = [round(draw.uniform(40, 124.9), 1) if draw.random() < 0.97 else round(draw.uniform(126, 160), 1)
               for _person in range(1000)]
    rows = [[f"P{who:05d}", f"{weights[who]:.1f} kg"] for who in range(1000) for _row in range(20)]
    source = tmp_path / "t.csv"
    with open(source, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["pid", "weight"])
        writer.writerows(rows)
    screen = io.StringIO()
    with _nobody_at_the_keyboard(), contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        exits = [cli.main(["profile", f"{source}", "--out-dir", f"{tmp_path}", "--replace", "--identifier", "pid"])]
        exits += [cli.main(["generate", f"{tmp_path / 't-profile.json'}", "--out-dir", f"{tmp_path}", "--seed", "0", "--replace"])]
        exits += [cli.main(["validate", f"{tmp_path / 't-profile.json'}", "--twin", f"{tmp_path / 't-twin.csv'}",
                            "--out-dir", f"{tmp_path}", "--replace"])]
    assert exits == [0, 0, 0], (exits, screen.getvalue()[-2000:])
    block = next(one for one in json.loads((tmp_path / "t-profile.json").read_text(encoding="utf-8"))["columns"]
                 if one["name"] == "weight")
    assert block["role"] == taxonomy.ROLE_IDENTIFIER and block["top_coded"] == 90
    with open(tmp_path / "t-twin.csv", encoding="utf-8", newline="") as handle:
        twin = list(csv.reader(handle))
    place = twin[0].index("weight")
    cells = [row[place] for row in twin[1:]]
    real = {row[1] for row in rows}
    assert len(cells) == 20000 and not [cell for cell in cells if cell in real]
    wide = [cell for cell in cells if re.match(r"\d{3}\.\d ", cell)]
    assert wide, sorted(set(cells))[-5:]


def test_a_pool_after_no_names_the_openings_its_held_back_rare_value_keeps(tmp_path: pathlib.Path) -> None:
    """The library at a test size (LANE I4m RULINGS 18 (4)): `8888` person 0's rare value on 12 rows beside the key `8889`, the others `201` to `204` on 4 rows each, answered `no`: the block names the width's openings, so `8888` is no start and appears nowhere in it.

    Red on 820d55c3 (`number_from` `8888`) and on the mutant that names no
    openings after `no` (the start `8888` again, four figures wide).
    """
    from synthtwin import profile, reading

    lines = ["patient_key,kind"]
    for who in range(300):
        for row in range(12 if who == 0 else 4):
            lines += [f"{'8889' if who == 0 else 100000 + who},{'8888' if who == 0 else ('201', '202', '203', '204')[(who * 4 + row) % 4]}"]
    path = tmp_path / "rare.csv"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    document = profile.build_document(
        reading.read_table(f"{path}"), taxonomy.Settings(), ["patient_key"], subjects=["patient_key"],
        safe_harbor_no=["kind"],
    )
    block = next(one for one in document["columns"] if one["name"] == "kind")  # type: ignore[index, union-attr]
    assert "8888" not in json.dumps(block)
    assert "pool_in_people" not in block or block["pool_in_people"]["number_from"] != "8888"


def test_the_summary_says_the_ends_a_column_was_pooled_into(tmp_path: pathlib.Path) -> None:
    """The description's words name the two values its ends are read as, and only on a block that records them."""
    from synthtwin import profile, reading, summary

    path = tmp_path / "ages.csv"
    path.write_text("age\n" + "".join(f"{20 + row % 75}\n" for row in range(300)), encoding="utf-8", newline="\n")
    document = profile.build_document(reading.read_table(f"{path}"), taxonomy.Settings(), [], top_code=True)
    block = next(one for one in document["columns"] if one["name"] == "age")  # type: ignore[index, union-attr]
    assert block["top_coded"] == 90
    plain = summary._column_lines(block, FLOOR)
    ended = summary._column_lines({**block, "top_coded_ends": [30, 82]}, FLOOR)
    assert not [line for line in plain if "ages at its ends" in line]
    assert [line for line in ended if "every age below 30 is read as 30 and every age above 82 as 82" in line]
    assert len(ended) == len(plain) + 1


def test_at_the_owner_floor_ages_in_months_and_in_mixed_units_pool_their_ends_and_load(tmp_path: pathlib.Path) -> None:
    """Beside a declared person column, 1,000 people of 20 rows, through the command: `age` written in months (five people the youngest, five at `1080 months`), and Codex's `age_at_visit` (`25`, `30`, `50`, `600 months`, `960 months` and `1080 months`, held by 5, 300, 300, 300, 90 and 5 people): each described with its ends in years at most the top code 90, its description loaded, its twin generated and valid (exit 0 each).

    Red on 3f542bc9 (lane HB2's repair 1, Codex's item 1): the ends were
    recorded in the cells' own units (`[30, 960]` beside the top code 90),
    and the loader refused the description, so the twin was never written;
    and on the mutant that compares each cell as written.
    """
    draw = random.Random(4795)
    years = [25] * 5 + [90] * 5 + [min(85, max(30, int(round(draw.gauss(55, 12))))) for _person in range(990)]
    mixed = ["25"] * 5 + ["30"] * 300 + ["50"] * 300 + ["600 months"] * 300 + ["960 months"] * 90 + ["1080 months"] * 5
    draw.shuffle(mixed)
    source = tmp_path / "t.csv"
    with open(source, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["sid", "age", "age_at_visit"])
        writer.writerows([f"P{who:06d}", f"{12 * years[who]} months", mixed[who]] for who in range(1000) for _row in range(20))
    screen = io.StringIO()
    with _nobody_at_the_keyboard(), contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        assert cli.main(["profile", f"{source}", "--out-dir", f"{tmp_path}", "--replace", "--identifier", "sid"]) == 0
        assert cli.main(["generate", f"{tmp_path / 't-profile.json'}", "--out-dir", f"{tmp_path}", "--seed", "0", "--replace"]) == 0
        assert cli.main(["validate", f"{tmp_path / 't-profile.json'}", "--twin", f"{tmp_path / 't-twin.csv'}",
                         "--out-dir", f"{tmp_path}", "--replace"]) == 0
    blocks = {one["name"]: one for one in json.loads((tmp_path / "t-profile.json").read_text(encoding="utf-8"))["columns"]}
    for name in ("age", "age_at_visit"):
        block = blocks[name]
        assert block["top_coded"] == 90, (name, block.get("top_coded"))
        low, high = block["top_coded_ends"]
        assert 0 <= low <= high <= 90, (name, low, high)
    assert blocks["age_at_visit"]["top_coded_ends"] == [30, 80]


def test_the_groups_count_their_people_over_the_interior_rows() -> None:
    """A bin group's people are counted over the rows the block's group counts cover -- the interior, its tails' rows set aside by rank -- so a tail edge's value 15 people hold, 10 of them inside the 200-row low tail, whose 100 interior rows belong to 5, is a group few people hold (lane HB2's repair 2, the combined verify's item 1: red on the mutant that counts every row, V16)."""
    from synthtwin import profile

    ages = [25] * 15 + [90] * 15
    for value in range(28, 90):
        ages += [value] * (16 if value < 68 else 15)
    assert len(ages) == 1000
    cells = [f"{ages[who]}" for who in range(1000) for _row in range(20)]
    subjects = [f"P{who:04d}" for who in range(1000) for _row in range(20)]
    described = taxonomy.profile_column("age", 0, cells, len(cells), taxonomy.Settings(small_cell_floor=FLOOR))
    block = profile._column_block(described)
    assert block["tails"]["low"]["rows"] == 200 and block["bin_groups"][0]["first"] == 0, block["tails"]
    ages_read = taxonomy.ages_as_read(cells, False, frozenset(), 90)
    assert profile._groups_few(described, ages_read, [subjects], FLOOR) == [25]


def test_the_generators_bound_writes_a_weight_past_125_at_or_below_the_top_code(tmp_path: pathlib.Path) -> None:
    """`generation._top_coded_twin` on a column described as numbers with a unit (`NN.N kg`, top-coded 90): `130.9 kg` is written at or below 90 and `88.0 kg` kept (lane HB2's repair 2, the combined verify's item 2: red on the mutant that passes no bound, V8)."""
    from synthtwin import contract, generation, profile, reading

    import fixtures

    draw = random.Random(4796)
    path = tmp_path / "weights.csv"
    path.write_text("weight\n" + "".join(f"{draw.uniform(40, 124):.1f} kg\n" for _row in range(3000)), encoding="utf-8",
                    newline="\n")
    document = profile.build_document(reading.read_table(f"{path}"), taxonomy.Settings(), [], top_code=True)
    column = contract.load_profile(f"{fixtures.write_profile(tmp_path, 't-profile.json', document)}").columns[0]
    assert column.top_coded == 90 and isinstance(column.facts, (contract.NumericFacts, contract.AffixedFacts))
    written = generation._top_coded_twin(column, ["130.9 kg", "88.0 kg", "45.5 kg"])
    assert float(written[0].split()[0]) <= 90 and written[0].endswith(" kg"), written
    assert written[1:] == ["88.0 kg", "45.5 kg"]


def test_at_the_owner_floor_a_signed_or_decimal_rare_code_after_no_is_not_the_start(tmp_path: pathlib.Path) -> None:
    """Codex's tables, 1,000 people of 20 rows beside a declared person column: codes `+1` to `+5` with one person's `+88`, and `1.1` to `5.1` with one person's `88.8`, declared codes and answered Safe Harbor `no`: the pool's start is neither rare value, as written or as a number, and the twin writes neither (lane HB2's repair 2, Codex's item 4: red on 3f542bc9, whose starts were `+88` and `88.8`, each written on that person's 20 cells; and on the mutant that widens whole figures alone).

    Codex's probe was the describe's own: through the command these columns
    put no Safe Harbor question, so `no` is given as the describe takes it.
    """
    import dataclasses

    from synthtwin import contract, generation, profile, reading

    import fixtures

    path = tmp_path / "codes.csv"
    path.write_text("patient_key,kind_plus,kind_point\n" + "".join(
        f"{100000 + who},{'+88' if who == 0 else f'+{1 + (who * 20 + row) % 5}'},"
        f"{'88.8' if who == 0 else f'{1 + (who * 20 + row) % 5}.1'}\n"
        for who in range(1000) for row in range(20)), encoding="utf-8", newline="\n")
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=FLOOR), person_columns=("patient_key",))
    names = ["kind_plus", "kind_point"]
    document = profile.build_document(table, settings, ["patient_key"], names, [], subjects=["patient_key"],
                                      top_code=True, safe_harbor_no=names)
    blocks = {one["name"]: one for one in document["columns"]}  # type: ignore[index, union-attr]
    loaded = contract.load_profile(f"{fixtures.write_profile(tmp_path, 't-profile.json', document)}")
    twin = generation.generate(loaded, 0)
    for name, rare in (("kind_plus", "+88"), ("kind_point", "88.8")):
        block = blocks[name]
        assert block["role"] == "categorical", (name, block["role"])
        start = block["pool_in_people"]["number_from"]
        assert start != rare and float(start) != float(rare) and parsing.is_a_stand_in_start(start), (name, start)
        assert f'"{rare}"' not in json.dumps(block), name
        written = twin.columns[twin.names.index(name)]
        assert len(written) == 20000 and not [cell for cell in written if float(cell) == float(rare)], name


def test_a_signed_pool_start_after_no_keeps_its_sign_on_a_free_opening() -> None:
    """Levels `+1` to `+5` beside one person's rare `+8888`, after `no` (four figures at least): the start takes the free opening with the countdown's sign, `+9888`, and beside `+8888` and `+9888` held by two people `+7888`, each a start the loader admits (batch 4s's merge, the scoped verify 2 of lane HB2, item 1).

    Red on the verify's mutant X7 (`_class_starts` takes the free opening
    without the countdown's sign): no start was found and the column was held
    whole as record numbers.
    """
    settings = taxonomy.Settings()
    published = ["+1", "+2", "+3", "+4", "+5"]
    for rares, wanted in ((["+8888"], "+9888"), (["+8888", "+9888"], "+7888")):
        cells = published * 20 + [rare for rare in rares for _row in range(20)]
        openings = taxonomy.figure_openings_read(
            {"figure_openings": taxonomy.label_figure_openings(cells, list(published), FLOOR)})
        starts = taxonomy.pool_stand_in_starts(published, published, (1, 0), settings, frozenset(), False, openings, 4)
        assert starts is not None, rares
        assert starts["number_from"] == wanted and parsing.is_a_stand_in_start(wanted), (rares, starts)
        for spelling in parsing.stand_ins_from(wanted, 3, frozenset(published)):
            assert spelling not in rares and spelling[:1] == "+", (rares, spelling)


def test_the_validator_reads_the_ends_beside_no_pool_marker_and_no_words(tmp_path: pathlib.Path) -> None:
    """`validation._top_coded_table` with the ends (40, 67), no pooled entry and no words: the 25 cells `20` are read as 40 and the 25 cells `70` as 67, the 50 cells `50` kept (batch 4s's merge, the scoped verify 2 of lane HB2, item 1; Codex's item 5 on the lane's repair 1, the ends half).

    Red on the verify's mutant X4 (a column with its ends beside no pool
    marker read through the older reader): the 25 cells `20` and the 25 cells
    `70` were left as written.
    """
    import collections

    from synthtwin import reading, validation

    path = tmp_path / "ends.csv"
    path.write_text("age\n" + "20\n" * 25 + "50\n" * 50 + "70\n" * 25, encoding="utf-8", newline="\n")
    table = reading.read_table(f"{path}", small_cell_floor=FLOOR)
    assert table.source is None
    read = validation._top_coded_table(table, {"age": 90}, {}, [], (), (), None, {"age": (40, 67)})
    assert collections.Counter(read.columns[read.column_names.index("age")]) == {"40": 25, "50": 50, "67": 25}
