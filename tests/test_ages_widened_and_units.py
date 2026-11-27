"""Ages beside a repeating subject described as ages, bin groups counted in people, and measurements no longer asked as ages (lane HB3-a2, plan P4-D486).

The orchestrator's LANE HB3-a RULINGS 1 (2), 2 and 4 (3): (C5) a bin group of a
number column's interior published while 1 to 10 people hold it -- a top-coded
age of 1,000 people of 20 rows, 15 aged 25 and 10 of them inside the 200-row
low tail, published bin group 0 of 100 rows belonging to 5 people; (W (1)) a
column named as an age whose cells are plain whole ages from 0 to 89 beside a
repeating subject was held whole as record numbers where the count in people
held it, its twin writing made-up keys (mean 555.8 against a real 54.4); (R)
measurements written with a unit no age is written with (`72.4 kg`, `88 bpm`,
`78 mmHg`) were asked as ages and capped at 90 until answered. Each class is
closed by a GENERATED check at the unit level and one table at the owner's
floor; the 20,000- and 200,000-row legs per spelling live in `K-HZ-36`'s
driver (`tools/measurements/kpi_ages_widened.py`; THE SUITE'S TIME rule).
"""

from __future__ import annotations

import dataclasses
import importlib.util
import pathlib
import random

from synthtwin import asking, parsing, profile, reading, taxonomy

ROWS = 20_000
PEOPLE = 1_000
FLOOR = 11
SEPARATORS = ("", " ", "  ", "-", " - ", "\u2013", " \u2014 ", "\u00a0", "\u2009", "\u202f", "\t", "\u3000", "\u200b")
SPACES = tuple(chr(code) for code in range(0x3001) if chr(code).isspace()) + ("\u200b", "\u200c", "\u2060", "\ufeff")
DASHES = ("-", "\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u2015", "\u2212", "\ufe58", "\ufe63", "\uff0d")


def _cased(unit: str, how: int) -> str:
    return (unit.lower(), unit.upper(), unit.title(), unit)[how]


def _write(path: pathlib.Path, header: "list[str]", rows: "list[list[str]]") -> None:
    path.write_text(
        ",".join(header) + "\n" + "".join(",".join(row) + "\n" for row in rows), encoding="utf-8", newline="\n"
    )


def _described(path: pathlib.Path, person: str, **answers: object) -> "dict[str, dict[str, object]]":
    table = reading.read_table(f"{path}", small_cell_floor=FLOOR)
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=FLOOR), person_columns=(person,))
    document = profile.build_document(
        table, settings, [person], [], [], subjects=[person], top_code=True, **answers  # type: ignore[arg-type]
    )
    return {f"{block['name']}": block for block in document["columns"]}  # type: ignore[union-attr, index]


def _groups_people(block: "dict[str, object]", values: "list[float | None]", people: "list[str]") -> "list[int]":
    """The people of each bin group a block publishes, counted by this case's own reading: the interior rows by rank, the tails' published rows set aside at each end, ties in row order; a row the block does not read (None) set aside."""
    groups = block.get("bin_groups")
    tails = block.get("tails")
    if not isinstance(groups, list) or not groups or not isinstance(tails, dict) or not tails.get("low"):
        return []
    rungs = {**(block.get("percentiles") or {}), **(block.get("percentiles_between") or {})}  # type: ignore[dict-item]
    low, high = tails["low"], tails["high"]
    lowest, highest = rungs[f"p{low['percent']:02d}"], rungs[f"p{high['percent']:02d}"]
    ranked = sorted((value, place) for place, value in enumerate(values) if value is not None)
    interior = ranked[low["rows"]: len(ranked) - high["rows"]]
    found: "list[int]" = []
    for group in groups:
        holders = {
            people[place] for value, place in interior
            if group["first"] <= parsing.histogram_bin(value, lowest, highest) <= group["last"]
        }
        found += [len(holders)]
    return found


def _every_block_people(block: "dict[str, object]", read: "dict[str, list[float | None]]", people: "list[str]") -> "dict[str, list[int]]":
    """The people of each bin group of EVERY numeric block a column publishes (lane HB3-a2's repair 1, skeptic 1's item 1): its own block, each wrapper's `numbers`, the `numbers` of numbers with labels and each of its `parts`, each counted by `_groups_people` over the values this case reads for that block (``read``: `top`, the wrapper's suffix, `numbers`, `part0`, `part1`, ...)."""
    found: "dict[str, list[int]]" = {"top": _groups_people(block, read["top"], people)} if "top" in read else {}
    for variant in block.get("affix_variants") or []:  # type: ignore[attr-defined]
        found[variant["suffix"]] = _groups_people(variant["numbers"], read[variant["suffix"]], people)
    if isinstance(block.get("numbers"), dict):
        found["numbers"] = _groups_people(block["numbers"], read["numbers"], people)  # type: ignore[arg-type]
    for place, part in enumerate(block.get("parts") or []):  # type: ignore[arg-type]
        found[f"part{place}"] = _groups_people(part, read[f"part{place}"], people)
    return found


# -- C5: every bin group of a number column's interior held by the floor's people


def _c5_rows() -> "list[list[str]]":
    draw = random.Random(20261115)
    ages = [25] * 15 + [90] * 15 + [28 + place % 62 for place in range(PEOPLE - 30)]
    draw.shuffle(ages)
    return [[f"S{10000 + who}", f"{ages[who]}", f"{ages[who]}.0"] for who in range(PEOPLE) for _visit in range(20)]


def test_c5_at_the_owner_floor_no_bin_group_is_held_by_1_to_10_people(tmp_path: pathlib.Path) -> None:
    """1,000 people of 20 rows beside a declared person column: 15 people aged 25, 10 of them inside the 200-row low tail, the ages 28 to 89 each 15 or 16 people's, 15 aged 90; an age column and a one-decimal column of the same values (the orchestrator's LANE HB3-a RULINGS 4 (3) (i)).

    On the base bin group 0 (100 interior rows) belonged to 5 people on both
    columns, unanswered and answered; now every published group holds 11
    people or more, counted by this case's own reading, the column is still
    described (not held), and no value past 89 is published. Red where
    `profile._groups_in_people` hands the block back unchanged.
    """
    rows = _c5_rows()
    path = tmp_path / "c5.csv"
    _write(path, ["sid", "age", "level_dec"], rows)
    blocks = _described(path, "sid")
    people = [row[0] for row in rows]
    for name, place in (("age", 1), ("level_dec", 2)):
        block = blocks[name]
        assert block["role"] != taxonomy.ROLE_IDENTIFIER, (name, block["role"])
        values = [min(float(row[place]), 90.0) for row in rows]
        held = _groups_people(block, values, people)
        assert held, name
        assert min(held) >= FLOOR, (name, held)


def test_c5_generated_tails_people_and_groups_publish_no_group_fewer_than_the_floor_hold(tmp_path: pathlib.Path) -> None:
    """A GENERATED check over tail widths, people counts and group widths (the stopping rule): 600 people beside a person column whose rows a person holds 5, 10 or 20 at once, the lowest value held by 11 to 16 people -- so the low tail takes some of their rows and the interior keeps the rest -- and every other value by 25 or more; the column is described and every published bin group holds the floor's people by this case's own reading."""
    draw = random.Random(4861)
    checked = 0
    for per_person in (5, 10, 20):
        for lowest_people in (11, 12, 14, 16):
            for spread in (6, 12, 24):
                people = 600
                ages = [20] * lowest_people + [21 + draw.randrange(spread) for _who in range(people - lowest_people)]
                draw.shuffle(ages)
                cells = [f"{ages[who]}" for who in range(people) for _row in range(per_person)]
                persons = [f"P{who:05d}" for who in range(people) for _row in range(per_person)]
                path = tmp_path / f"g{per_person}-{lowest_people}-{spread}.csv"
                _write(path, ["sid", "level"], [[persons[place], cells[place]] for place in range(len(cells))])
                block = _described(path, "sid")["level"]
                assert block["role"] != taxonomy.ROLE_IDENTIFIER, (per_person, lowest_people, spread)
                held = _groups_people(block, [float(cell) for cell in cells], persons)
                assert not held or min(held) >= FLOOR, (per_person, lowest_people, spread, held)
                checked += 1
    assert checked == 36, checked


def test_c5_a_group_few_people_hold_joins_its_neighbour_and_a_column_all_few_hold_is_held() -> None:
    """The joining rule alone: groups each held by the floor's people keep their bytes; one held by 5 joins the next; where the whole interior is held by fewer the column is held (None)."""
    rows = [f"{value}" for value in range(30) for _row in range(20)]
    people = [f"P{value:03d}" for value in range(30) for _row in range(20)]
    column = taxonomy.profile_column("level", 1, rows, len(rows), taxonomy.Settings(small_cell_floor=FLOOR))
    groups = column.details["bin_groups"]
    assert isinstance(groups, list) and groups
    joined = profile._groups_in_people(column, rows, [people], FLOOR, None, None)
    assert joined is not None
    held = _groups_people(profile._column_block(joined), [float(cell) for cell in rows], people)
    assert min(held) >= FLOOR, held
    assert len(joined.details["bin_groups"]) < len(groups)  # type: ignore[arg-type]
    many = [f"P{place:05d}" for place in range(len(rows))]
    assert profile._groups_in_people(column, rows, [many], FLOOR, None, None) is column
    few = [f"P{place % 6:03d}" for place in range(len(rows))]
    assert profile._groups_in_people(column, rows, [few], FLOOR, None, None) is None


# -- C5 in every numeric block (lane HB3-a2's repair 1, skeptic 1's item 1)


def _two_units_rows(main: int, minor: int, rows_each: int, seed: int) -> "list[list[str]]":
    """A reading written `NNN.N mg/dL` by ``main`` people and `N.N mmol/L` by ``minor``, each person's values close to their own centre."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for who in range(main + minor):
        small = who >= main
        centre = draw.gauss(5.5, 1.2) if small else draw.gauss(100.0, 22.0)
        for _row in range(rows_each):
            value = centre + draw.gauss(0.0, 0.3 if small else 5.0)
            rows += [[f"S{10000 + who}", f"{value:.1f} mmol/L" if small else f"{value:.1f} mg/dL"]]
    return rows


def _unit_read(rows: "list[list[str]]", place: int, suffix: str) -> "list[float | None]":
    return [float(row[place][: len(row[place]) - len(suffix)]) if row[place].endswith(suffix) else None for row in rows]


def test_c5_every_numeric_block_counts_its_groups_in_people_at_the_owner_floor(
    tmp_path: pathlib.Path, monkeypatch: "object"
) -> None:
    """1,000 people of 20 rows beside a declared person column: a reading written `NNN.N mg/dL` by 900 people and `N.N mmol/L` by 100 (skeptic 1's item 1; the orchestrator's LANE HB3-a2 RULINGS 7 (1)).

    On 19aa0157 the minority unit's block published 30 bin groups, 11 of
    them held by 4 to 9 people, and the column's own block, counted over
    every cell, lost its rank and its 32 groups; now every group of both
    blocks holds 11 people or more by this case's own reading
    (`_every_block_people`), the column is described, and its own block
    keeps more than one group. The counter is shown able to see: with the
    count of groups withdrawn, it reads a group of the minority block held
    by fewer than the floor's people.
    """
    rows = _two_units_rows(900, 100, 20, 4875)
    path = tmp_path / "units.csv"
    _write(path, ["sid", "reading"], rows)
    people = [row[0] for row in rows]
    read = {"top": _unit_read(rows, 1, " mg/dL"), " mmol/L": _unit_read(rows, 1, " mmol/L")}
    block = _described(path, "sid")["reading"]
    assert block["role"] == taxonomy.ROLE_AFFIXED, block["role"]
    held = _every_block_people(block, read, people)
    assert set(held) == {"top", " mmol/L"} and all(held.values()), held
    assert min(min(groups) for groups in held.values()) >= FLOOR, held
    assert len(held["top"]) > 1, held
    monkeypatch.setattr(profile, "_groups_in_people", lambda described, *_args: described)  # type: ignore[attr-defined]
    blind = _every_block_people(_described(path, "sid")["reading"], read, people)
    assert min(blind[" mmol/L"]) < FLOOR, blind


def _layout_rows(layout: str, people: int, rows_each: int, seed: int) -> "tuple[list[list[str]], dict[str, list[float | None]]]":
    """One of the three nested layouts beside a person column, each person's values close to their own centre, and this case's own reading of each block."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    read: "dict[str, list[float | None]]" = {}
    if layout == "units":
        rows = _two_units_rows(people - people // 6, people // 6, rows_each, seed)
        return rows, {"top": _unit_read(rows, 1, " mg/dL"), " mmol/L": _unit_read(rows, 1, " mmol/L")}
    if layout == "labels":
        read = {"numbers": []}
        for who in range(people):
            centre = draw.gauss(140.0, 25.0)
            for _row in range(rows_each):
                if draw.random() < 0.06:
                    rows += [[f"S{10000 + who}", draw.choice(("PENDING", "NOT DONE"))]]
                    read["numbers"] += [None]
                    continue
                value = round(centre + draw.gauss(0.0, 2.0), 1)
                rows += [[f"S{10000 + who}", f"{value:.1f}"]]
                read["numbers"] += [value]
        return rows, read
    read = {"part0": [], "part1": []}
    for who in range(people):
        upper, lower = draw.gauss(130.0, 18.0), draw.gauss(80.0, 11.0)
        for _row in range(rows_each):
            first, second = int(round(upper + draw.gauss(0.0, 2.0))), int(round(lower + draw.gauss(0.0, 2.0)))
            rows += [[f"S{10000 + who}", f"{first}/{second}"]]
            read["part0"] += [float(first)]
            read["part1"] += [float(second)]
    return rows, read


def test_c5_generated_over_the_nested_layouts_publishes_no_group_fewer_than_the_floor_hold(tmp_path: pathlib.Path) -> None:
    """A GENERATED check over the three nested layouts (the stopping rule): two units of one reading (a wrapper's `numbers`), numbers beside two labels (`numbers`), and two whole numbers joined by a slash (`parts`), at 300 and 600 people of 5 and 10 rows, each person's values close to their own centre, so a group of rows can be one person's; every bin group of every block of a column described holds the floor's people by this case's own reading (a column the count in people holds as a record number publishes no group). On 19aa0157 the nested blocks' groups were counted nowhere."""
    described: "dict[str, int]" = {}
    for layout, role in (("units", taxonomy.ROLE_AFFIXED), ("labels", taxonomy.ROLE_COMPOUND), ("joined", taxonomy.ROLE_JOINED)):
        for people, rows_each in ((300, 10), (600, 5), (600, 10)):
            rows, read = _layout_rows(layout, people, rows_each, 4868 + people + rows_each)
            path = tmp_path / f"{layout}-{people}-{rows_each}.csv"
            _write(path, ["sid", "level"], rows)
            block = _described(path, "sid")["level"]
            if block["role"] == taxonomy.ROLE_IDENTIFIER:
                continue
            assert block["role"] == role, (layout, people, rows_each, block["role"])
            held = _every_block_people(block, read, [row[0] for row in rows])
            nested = [groups for name, groups in held.items() if name != "top"]
            assert nested and all(nested), (layout, people, rows_each, held)
            assert min(min(groups) for groups in held.values() if groups) >= FLOOR, (layout, people, rows_each, held)
            described[layout] = described.get(layout, 0) + 1
    assert set(described) == {"units", "labels", "joined"} and sum(described.values()) >= 6, described


def test_c5_a_number_column_whose_interior_ten_of_a_subjects_twelve_values_hold_is_held(tmp_path: pathlib.Path) -> None:
    """1,000 people of 20 rows beside two declared subject columns: the person, and a `site` of twelve values; a reading with three decimals whose 150 lowest rows are site 10's and 150 highest site 11's, inside the 200-row tails, every other row one of sites 0 to 9 (skeptic 1's item 6 (a)). Every value it publishes clears the count in people, but its interior, read by rank, is held by ten sites of the twelve: no run of its bin groups holds the floor's sites, so the column is held as a record number (`profile._groups_in_people` answers None). Red where the caller ignores that answer."""
    draw = random.Random(4869)
    rows: "list[list[str]]" = []
    lowest = set(draw.sample(range(ROWS), 300))
    highest = set(draw.sample(sorted(lowest), 150))
    for place in range(ROWS):
        who = place // 20
        if place in highest:
            rows += [[f"S{10000 + who}", "K11", f"{draw.uniform(900.0, 990.0):.3f}"]]
        elif place in lowest:
            rows += [[f"S{10000 + who}", "K10", f"{draw.uniform(1.0, 9.0):.3f}"]]
        else:
            rows += [[f"S{10000 + who}", f"K{draw.randrange(10):02d}", f"{draw.gauss(400.0, 60.0):.3f}"]]
    path = tmp_path / "sites.csv"
    _write(path, ["sid", "site", "reading"], rows)
    table = reading.read_table(f"{path}", small_cell_floor=FLOOR)
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=FLOOR), person_columns=("sid",))
    document = profile.build_document(table, settings, ["sid", "site"], [], [], subjects=["sid", "site"], top_code=True)
    blocks = {f"{block['name']}": block for block in document["columns"]}  # type: ignore[union-attr, index]
    assert blocks["reading"]["role"] == taxonomy.ROLE_IDENTIFIER, blocks["reading"]["role"]


# -- W (1): plain whole ages from 0 to 89 beside a repeating subject


def test_w1_plain_whole_ages_below_the_top_code_are_read_and_nothing_else() -> None:
    """A GENERATED check of `taxonomy.ages_whole_below_the_top_code`: every whole number 0 to 89 written bare, with blanks and absent spellings set aside, reads; one cell padded, signed, decimal, worded, with a unit, grouped or past 89 among them does not."""
    bare = [f"{age}" for age in range(90)]
    assert taxonomy.ages_whole_below_the_top_code(bare + ["", "  ", "NA"], False, frozenset({"NA"}))
    assert not taxonomy.ages_whole_below_the_top_code(["", "NA"], False, frozenset({"NA"}))
    for odd in ("07", "+7", "-7", "7.0", "7.5", "Age 7", "7 y", "7 years", "(7)", "90", "125", "1,000", "7e1", "7%", "7 kg"):
        assert not taxonomy.ages_whole_below_the_top_code(bare + [odd], False, frozenset()), odd


def _noted(who: int) -> str:
    """`Age 0` and `Age 1` 15 people each, `Age 2` 8 people, `Age 95` 15 people, `Age 30` to `Age 89` 15 or 16 people each."""
    if who < 30:
        return f"Age {who // 15}"
    if who < 38:
        return "Age 2"
    if who < 53:
        return "Age 95"
    return f"Age {30 + who % 60}"


def _capped_rows(seed: int) -> "list[list[str]]":
    """The capped table: `age` and `visit_code` (55 +/- 12 within 25 to 89), `age_note` (`_noted`), and two guards of W (1) (lane HB3-a2's repair 1, skeptic 1's item 6): `age_even`, 20 to 69 each held by 20 people, which the count in people does not hold; `age_thin`, two people in three at a multiple of 7 and one in three anywhere from 0 to 89, which it holds and no round of the ends frees."""
    draw = random.Random(seed)
    other = random.Random(seed + 1)
    rows: "list[list[str]]" = []
    for who in range(PEOPLE):
        age = int(min(89, max(25, round(draw.gauss(55, 12)))))
        thin = other.randrange(0, 90, 7) if who % 3 else other.randrange(90)
        rows += [[f"S{10000 + who}", f"{age}", f"{age}", _noted(who), f"{20 + who % 50}", f"{thin}"] for _visit in range(20)]
    return rows


def test_w1_ages_capped_at_89_beside_a_declared_person_are_described_with_their_ends(tmp_path: pathlib.Path) -> None:
    """1,000 people of 20 rows, ages 55 +/- 12 kept within 25 to 89, one a person, under `age` and under the neutral heading `visit_code` (LANE HB2 RULINGS 4 (3)'s gate case, moved here by LANE HB3-a RULINGS 1 (2)).

    On the base both were held whole as record numbers (the twin's mean
    555.8 against 54.4). Now the age is described with its ends pooled in
    people (top code 90, nothing past 89), every published value and bin
    group held by 11 people or more, while `visit_code`, which nothing names
    as an age, is held as before; answered `years`, the age is described the same; a column of `Age NN` with a value 8 people hold inside its two ends is described with its low band reaching it. Red where the widening, or the seeding of the first round, is withdrawn.
    """
    rows = _capped_rows(20261112)
    path = tmp_path / "capped.csv"
    _write(path, ["sid", "age", "visit_code", "age_note", "age_even", "age_thin"], rows)
    blocks = _described(path, "sid")
    age = blocks["age"]
    assert age["role"] != taxonomy.ROLE_IDENTIFIER, age["role"]
    assert age["top_coded"] == 90
    low, high = age["top_coded_ends"]  # type: ignore[misc]
    assert 25 <= low < high <= 89, (low, high)
    # ...each band written at the mean age of its rows where the block records
    # it (`top_coded_band_values`, lane RX-1), else at its edge.
    first, second = age.get("top_coded_band_values", [low, high])  # type: ignore[misc]
    values = [float(first if int(row[1]) <= low else second if int(row[1]) >= high else int(row[1])) for row in rows]
    people = [row[0] for row in rows]
    by_value: "dict[float, set[str]]" = {}
    for value, person in zip(values, people):
        by_value.setdefault(value, set()).add(person)
    for number in profile._published_in(age, True).numbers:
        if number in by_value:
            assert len(by_value[number]) >= FLOOR, number
    held = _groups_people(age, values, people)
    assert not held or min(held) >= FLOOR, held
    assert blocks["visit_code"]["role"] == taxonomy.ROLE_IDENTIFIER
    # ...and once its unit is answered (`years`) the same: an answer that
    # says it holds ages keeps the widening.
    answered = _described(path, "sid", ages_counted_in={"age": 90})["age"]
    assert answered["role"] != taxonomy.ROLE_IDENTIFIER and answered["top_coded_ends"] == age["top_coded_ends"]
    # ...and a column of `Age NN` whose two ends each hold the floor's people
    # but whose `Age 2` 8 people hold is described with its low band reaching
    # it (W (4); held whole on the base): every published level 11 people's.
    noted = blocks["age_note"]
    assert noted["role"] != taxonomy.ROLE_IDENTIFIER, noted["role"]
    assert noted["top_coded_ends"][0] == 2, noted["top_coded_ends"]  # type: ignore[index]
    # ...W (1) ONLY WHERE THE COUNT IN PEOPLE HOLDS THE COLUMN (skeptic 1's
    # item 6 (c)): ages 20 to 69 each held by 20 people are described as
    # before, with no top code and no ends.
    even = blocks["age_even"]
    assert even["role"] != taxonomy.ROLE_IDENTIFIER and "top_coded" not in even and "top_coded_ends" not in even, even
    # ...AND A WIDENED COLUMN NO ROUND FREES IS HELD AS BEFORE, from its own
    # cells, with no top code (item 6 (d)).
    thin = blocks["age_thin"]
    assert thin["role"] == taxonomy.ROLE_IDENTIFIER and "top_coded" not in thin, thin


def test_w1_never_reads_an_age_column_an_open_identifier_question_holds(tmp_path: pathlib.Path, monkeypatch: "object") -> None:
    """The capped table's `age` with its identifier question open (`unanswered`), the person declared beside it: held as an open question holds a column, never widened -- its name is not read (the orchestrator's LANE I4m RULINGS 21 (1), the `age_key` trap; skeptic 1's item 6 (b)): no top code and no ends, and its block byte for byte the one described with W (1) withdrawn, even where the count in people would hold it (answered so here for every column, as another draw would). Red where W (1) reads the name of a column such a question holds."""
    rows = _capped_rows(20261112)
    path = tmp_path / "open.csv"
    _write(path, ["sid", "age"], [row[:2] for row in rows])
    monkeypatch.setattr(profile, "_counted_in_subjects", lambda *_args, **_kwargs: True)  # type: ignore[attr-defined]
    age = _described(path, "sid", unanswered=["age"])["age"]
    assert age["role"] == taxonomy.ROLE_IDENTIFIER and "top_coded" not in age and "top_coded_ends" not in age, age
    monkeypatch.setattr(taxonomy, "ages_whole_below_the_top_code", lambda *_args: False)  # type: ignore[attr-defined]
    assert _described(path, "sid", unanswered=["age"])["age"] == age


# -- R: measurements written with a unit no age has leave the age reach


def _unit_cells(unit: str, separator: str, how: int, draw: random.Random) -> "list[str]":
    return [f"{draw.randint(40, 125)}{separator}{_cased(unit, how)}" for _cell in range(40)]


def test_r_every_unit_of_the_list_with_every_space_and_dash_leaves_the_reach() -> None:
    """A GENERATED check: each unit of `taxonomy.NO_AGE_UNITS`, glued or after every Unicode space and dash of the product's definition (and pairs of them), in four cases, on 40 cells from 40 to 125: the cell reads as that unit and a column of them leaves the age reach; the same cells under a name that says age, or with one age word, unit, affix or band in one cell, stay in it."""
    draw = random.Random(4862)
    separators = SEPARATORS + SPACES + DASHES + tuple(space + dash for space in (" ", "\u00a0") for dash in DASHES)
    checked = 0
    reached: "dict[str, int]" = {}
    for unit in taxonomy.NO_AGE_UNITS:
        for separator in separators:
            for how in range(4):
                cells = _unit_cells(unit, separator, how, draw)
                cells[0] = f"95{separator}{_cased(unit, how)}"
                assert all(taxonomy._a_unit_no_age_has(cell, False) for cell in cells), (unit, separator, how)
                assert taxonomy.safe_harbor_reach(cells, False, frozenset(), FLOOR) == "", (unit, separator, how)
                # ...where the reach read it before (as it reads it under a
                # name that says age), the rule is what set it out.
                if taxonomy.safe_harbor_reach(cells, False, frozenset(), FLOOR, said=True) == taxonomy.SAFE_HARBOR_AGES:
                    reached[unit] = reached.get(unit, 0) + 1
                checked += 1
    assert checked >= len(taxonomy.NO_AGE_UNITS) * 100, checked
    assert {"kg", "bpm", "mmhg", "mm hg", "lb"} <= set(reached), sorted(reached)


def test_r_one_cell_saying_age_keeps_a_column_of_units_in_the_reach() -> None:
    """A GENERATED check over the age vocabulary: one cell among 2,000 unit cells carrying an age word, unit word or letter, affix or band (each in four cases, before or after its number) keeps the column in the reach; so does a name that says age or a unit named."""
    draw = random.Random(4863)
    base = [f"{draw.randint(40, 125)} kg" for _cell in range(2000)]
    base[1] = "95 kg"
    sayings = (
        [f"{word} 95" for word in taxonomy.AGE_VOCABULARY.before]
        + [f"95 {unit}" for unit, _letter in taxonomy.AGE_VOCABULARY.units if unit]
        + [f"95{affix}" for affix in taxonomy.AGE_VOCABULARY.affixes]
        + ["95y", "95Y", ">89", "90+", "\u226590", "<18", "aged 95 kg", "95 kg (age)", "95 yrs kg"]
    )
    for saying in sayings:
        for how in range(4):
            cells = list(base)
            cells[draw.randrange(2, len(cells))] = _cased(saying, how)
            assert taxonomy.safe_harbor_reach(cells, False, frozenset(), FLOOR) == taxonomy.SAFE_HARBOR_AGES, saying
    for name in ("age", "Age", "age_in_months", "subject_age", "age_at_visit", "agemonths", "months_old", "ageyrs"):
        assert taxonomy.named_as_an_age(name), name
    months = [f"{draw.randint(480, 1500)} kg" for _cell in range(2000)]
    months[1] = "1100 kg"
    assert taxonomy.safe_harbor_reach(months, False, frozenset(), FLOOR, mark=1080) == taxonomy.SAFE_HARBOR_AGES
    assert taxonomy.safe_harbor_reach(base, False, frozenset(), FLOOR, named=True) == taxonomy.SAFE_HARBOR_AGES
    assert taxonomy.safe_harbor_reach(base, False, frozenset(), FLOOR) == ""


def test_r_one_letters_age_units_sexes_and_fewer_than_half_leave_the_reach_as_it_was() -> None:
    """What the list must not take: a temperature written `100.0 F`, a letter of an age's unit, a trailing M or F or the word male, and a column whose units stand on fewer than half its present cells stay in the reach, as on the base; blanks and absent spellings are no present cells. HALF bare beside half `kg` leaves only where no bare cell reads past 89 (the statistics check's item 1: a bare `95` among them is an age the reach keeps)."""
    draw = random.Random(4864)
    for tail in (" F", " C", "F", " M", " m", " y", " d", " w", " male", " female", " gm", " kgs", " Hg", " g", " l", " L"):
        cells = [f"{draw.randint(40, 125)}{tail}" for _cell in range(200)]
        cells[0] = f"95{tail}"
        assert not any(taxonomy._a_unit_no_age_has(cell, False) for cell in cells), tail
        assert taxonomy.ages_set_out_by_units(cells, False, frozenset()) is False, tail
    bare = [f"{draw.randint(40, 125)}" for _cell in range(200)]
    bare[0] = "95"
    half = bare[:100] + [f"{cell} kg" for cell in bare[100:]]
    young = [f"{draw.randint(18, 89)}" for _cell in range(100)] + [f"{cell} kg" for cell in bare[100:]]
    fewer = [f"{draw.randint(18, 89)}" for _cell in range(101)] + [f"{cell} kg" for cell in bare[101:]]
    assert taxonomy.ages_set_out_by_units(half, False, frozenset()) is False
    assert taxonomy.ages_set_out_by_units(young, False, frozenset())
    assert not taxonomy.ages_set_out_by_units(fewer, False, frozenset())
    assert taxonomy.safe_harbor_reach(fewer, False, frozenset(), FLOOR) == taxonomy.SAFE_HARBOR_AGES
    padded = fewer + [""] * 50 + ["NA"] * 50
    assert taxonomy.ages_set_out_by_units(padded, False, frozenset({"NA"})) is False
    assert taxonomy.ages_set_out_by_units(young + [""] * 50 + ["NA"] * 50, False, frozenset({"NA"}))


def test_r_the_letters_g_and_l_never_set_ages_out_of_the_reach() -> None:
    """A GENERATED check (skeptic 1's item 2; the orchestrator's LANE HB3-a2 RULINGS 7 (2)): ages 0 to 105 under no name, each written with g, l, G or L after it -- glued, after a space or a no-break space, with a point after or not, as years are abbreviated in other languages (`72 g.`, `72 l.`) -- write no unit of the list and stay in the age reach. On 19aa0157 every one of these columns left it and its twin wrote its ages past 90."""
    draw = random.Random(4870)
    checked = 0
    for letter in ("g", "l", "G", "L"):
        for separator in ("", " ", " "):
            for point in ("", "."):
                cells = [f"{draw.randint(0, 105)}{separator}{letter}{point}" for _cell in range(400)]
                cells[0] = f"95{separator}{letter}{point}"
                assert not any(taxonomy._a_unit_no_age_has(cell, False) for cell in cells), (letter, separator, point)
                assert not taxonomy.ages_set_out_by_units(cells, False, frozenset()), (letter, separator, point)
                assert taxonomy.safe_harbor_reach(cells, False, frozenset(), FLOOR) == taxonomy.safe_harbor_reach(
                    cells, False, frozenset(), FLOOR, said=True), (letter, separator, point)
                checked += 1
    assert checked == 24, checked
    assert "g" not in taxonomy.NO_AGE_UNITS and "l" not in taxonomy.NO_AGE_UNITS
    assert {"kg", "mg", "mcg", "ml", "dl", "g/dl", "mmol/l", "meq/l", "u/l"} <= set(taxonomy.NO_AGE_UNITS)


def test_r_a_bare_age_past_89_among_unit_cells_keeps_the_column_in_the_reach() -> None:
    """A GENERATED check (the statistics check's item 1): every unit of the list on 400 cells, beside bare ages on one cell to 49 per cent of them, each draw holding ONE bare age from 90 to 104: the column stays in the reach (it leaves only where its bare cells all read 89 or less); and where the reach read the column before the rule, it reads it still. On 19aa0157 every one left, and a column of observations, ages bare on one row in five beside weights, rates and pressures, had its ages past 89 published and written."""
    draw = random.Random(4871)
    checked = 0
    reached = 0
    for unit in taxonomy.NO_AGE_UNITS:
        for share in (1, 4, 40, 120, 196):
            cells = [f"{draw.randint(40, 125)} {unit}" for _cell in range(400 - share)]
            ages = [f"{draw.randint(18, 89)}" for _cell in range(share)]
            ages[draw.randrange(share)] = f"{draw.randint(90, 104)}"
            column = cells + ages
            draw.shuffle(column)
            assert not taxonomy.ages_set_out_by_units(column, False, frozenset()), (unit, share)
            if taxonomy.safe_harbor_reach(column, False, frozenset(), FLOOR, said=True) == taxonomy.SAFE_HARBOR_AGES:
                reached += 1
                assert taxonomy.safe_harbor_reach(column, False, frozenset(), FLOOR) == taxonomy.SAFE_HARBOR_AGES, (unit, share)
            young = cells + [f"{draw.randint(18, 89)}" for _cell in range(share)]
            assert taxonomy.ages_set_out_by_units(young, False, frozenset()), (unit, share)
            checked += 1
    assert checked == 5 * len(taxonomy.NO_AGE_UNITS), checked
    assert reached >= 5 * 5, reached


def test_r_a_column_named_as_an_age_whose_cells_write_kg_is_not_asked_its_unit(tmp_path: pathlib.Path) -> None:
    """Question Q-UNIT reads a column's name as the description does (skeptic 1's item 6 (e)): `age_scale`, written `NN kg` on 2,000 rows, stays in the age reach -- top-coded, and no unit question is put -- while the same cells under the neutral `scale_k` are asked it. Red where `asking.unit_questions` does not hand the name's evidence to the reach."""
    draw = random.Random(4872)
    cells = [f"{draw.choice(range(40, 121, 5))} kg" for _cell in range(2000)]
    header = ["age_scale", "scale_k"]
    columns = [cells, list(cells)]
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    path = tmp_path / "scales.csv"
    _write(path, header, [[cell, cell] for cell in cells])
    document = profile.build_document(reading.read_table(f"{path}", small_cell_floor=FLOOR), settings, [], [], [], top_code=True)
    asked, split = asking.questions_and_splits_for(document, columns, settings, [])
    units, _reached = asking.unit_questions(document, columns, settings, [], asked, split)
    named = [question.name for question in units]
    blocks = {f"{block['name']}": block for block in document["columns"]}  # type: ignore[union-attr, index]
    assert blocks["age_scale"].get("top_coded") == 90, blocks["age_scale"]
    assert "age_scale" not in named and "scale_k" in named, named


def test_r_at_the_owner_floor_measurements_with_their_units_are_described_with_their_own_values(
    tmp_path: pathlib.Path,
) -> None:
    """1,000 people of 20 rows beside a declared person column: a weight `NN.N kg`, a rate `NN bpm` and a pressure `NN mmHg`, each with values past 90, leave the age reach (no top code, every value from 90 published as itself); an age written bare under the neutral heading `level_k` stays top-coded, and the kilograms under a heading that says age stay in the reach. A column of observations, the person's age written bare on one row in five (18 to 104) beside the weights, rates and pressures written with their units, stays in the reach and is top-coded: nothing past 90 is published (the statistics check's item 1; on 19aa0157 it put no question at all). Red where `taxonomy.ages_set_out_by_units` answers no, where it answers yes beside a bare age past 89, and where the name's evidence is not handed to the reach."""
    draw = random.Random(20261114)
    rows: "list[list[str]]" = []
    for who in range(PEOPLE):
        weight, rate, pressure = draw.gauss(78, 18), draw.gauss(80, 12), draw.gauss(76, 11)
        neutral = max(0, min(105, int(round(draw.gauss(58, 17)))))
        aged = draw.randint(18, 104)
        for visit in range(20):
            kilos = f"{max(35.0, weight + draw.gauss(0, 2)):.1f} kg"
            beat = f"{int(max(35, rate + draw.gauss(0, 9)))} bpm"
            low = f"{int(max(35, min(125, pressure + draw.gauss(0, 7))))} mmHg"
            rows += [[
                f"S{10000 + who}", kilos, beat, low, f"{neutral}", kilos,
                f"{aged}" if visit % 5 == 0 else (kilos, beat, low, kilos)[visit % 4],
            ]]
    path = tmp_path / "units.csv"
    _write(path, ["sid", "weight", "rate", "pressure", "level_k", "age_on_the_scale", "obs_value"], rows)
    blocks = _described(path, "sid")
    observed = blocks["obs_value"]
    assert observed.get("top_coded") == 90, observed
    assert max(profile._published_in(observed, True).numbers) <= 90, observed
    # ...and the same kilograms under a name that says age stay in the reach:
    # the name is read whatever holds it, never the units its cells write.
    assert blocks["age_on_the_scale"].get("top_coded") == 90 or blocks["age_on_the_scale"]["role"] == taxonomy.ROLE_IDENTIFIER
    for name in ("weight", "rate", "pressure"):
        assert "top_coded" not in blocks[name], name
        assert blocks[name]["role"] != taxonomy.ROLE_IDENTIFIER, name
        largest = profile._published_in(blocks[name], True).numbers
        assert any(number > 90 for number in largest), name
    assert blocks["level_k"]["top_coded"] == 90


# -- THE ORACLE AND THE PRODUCT BOUND BRACKETED AGES ALIKE (lane HB3-a2's
# repair 1; the orchestrator's LANE HB3-a2 RULINGS 5 (2) and 7 (5))


def _oracle() -> object:
    where = pathlib.Path(__file__).resolve().parents[1] / "tools" / "reference" / "make_generation_reference_vectors.py"
    spec = importlib.util.spec_from_file_location("oracle_bracketed_ages", where)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _bracketed(draw: random.Random) -> str:
    """An age in brackets of one to six figures, leading zeros or not, a point and decimals or not, spaces inside the brackets or not, a unit word or letter after them or not."""
    width = draw.randint(1, 6)
    figures = "".join(draw.choice("0123456789") for _figure in range(width))
    if draw.random() < 0.5:
        figures = f"{draw.randint(0, 130):0{width}d}"[-max(width, 1):] if width <= 3 else figures
    places = draw.choice(("", "", ".", ".5", ".25"))
    inside = draw.choice(("", " ", "\t"))
    after = draw.choice(("", "", " ", "y", " y", "Y", " years", " yrs", " M", " kg", "  "))
    return f"{draw.choice(('', ' '))}({inside}{figures}{places}{draw.choice(('', ' '))}){after}"


def test_the_oracle_bounds_bracketed_ages_of_every_width_as_the_product_does() -> None:
    """A-P4-59 for method G7.14: a GENERATED check over ages in brackets of one to six figures (`(95)`, `(095)`, `( 100 ) years`, `(1000)`), leading zeros, decimals, spaces and unit words beside plain ages, a worded age and a missing value, under every unit's mark, held or not, published or not, read as labels or not, with the age words read and without, bounded and not: `taxonomy.at_most_the_top_code` and the oracle's `safe_harbor_ages_twin` write the same cells. The product reads a bracketed number as an accountant's negative and writes a whole one below -9 at or below 90; the oracle on 19aa0157 kept every one as written (the gap lane HB3-a's build named)."""
    from synthtwin import contract
    oracle = _oracle()
    draw = random.Random(4873)
    columns = 0
    bracketed = 0
    for mark in contract.TOP_CODE_MARKS:
        for held, published, labels in (
            (False, None, False), (True, None, False), (False, False, False), (False, True, False),
            (False, None, True), (False, False, True),
        ):
            for _column in range(30):
                cells = [_bracketed(draw) for _cell in range(draw.randint(1, 12))]
                cells += [f"{draw.randint(0, 120)}", draw.choice(("Age 95", "NA", "95", "(95)", "89"))]
                draw.shuffle(cells)
                bracketed += sum(1 for cell in cells if "(" in cell)
                for words in (True, False):
                    for bounded in (False, True):
                        assert taxonomy.at_most_the_top_code(
                            cells, frozenset({"NA"}), mark, held, published, labels, words, bounded
                        ) == oracle.safe_harbor_ages_twin(  # type: ignore[attr-defined]
                            cells, frozenset({"NA"}), mark, held, published, labels, words, bounded
                        ), (mark, held, published, labels, words, bounded, cells)
                columns += 1
    assert columns == 4 * 6 * 30 and bracketed > 2000, (columns, bracketed)
    # ...and the gap itself: `(95)` beside ages is written `89` by both.
    for twin in (taxonomy.at_most_the_top_code(["(95)", "50"]), oracle.safe_harbor_ages_twin(["(95)", "50"])):  # type: ignore[attr-defined]
        assert twin == ["89", "50"], twin
