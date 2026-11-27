"""Gate file of lane W5-302: the invented 302-column table and its driver.

THE TABLE (`tests/wide_table.py`). 302 columns, every one in exactly one
family, the same bytes from the same seed, the person's key repeating
over one to twelve rows, and each relation `RELATIONS` names visible in
the cells: a response moves with its parent where a table drawn with the
relation cut would not. Mutants: a family dropped from the table; a
relation cut (the parent's effect set to nought).

THE KEY OF A WIDE TABLE (lane W5-302). A label is a key of a long table
only where it types a column whose cells its levels write: a column
empty on most rows holds levels with no written cell, which once made
any label beside it a key (a wide table of no key took its clock column
for one, then built the zone twice a round, about half an hour each at
20,000 rows). Mutant: `TYPED_WRITTEN_LEAST` nought. The key is read from
its sample rows alone, never from the table held whole as text, and is
the key `build_zone` finds. Mutant: the columns handed whole. The label
is read once a column for its typing and the moved columns counted only
for a label that types one: the same key as every pass found.

THE SCREEN OF A LABEL PARENT IN ONE PASS (lane W5-302). The relations
fit screens every earlier column of every response; a label parent's
levels against a fit of the intercept alone are read from sums a level
(`inside_relations.indicator_statistic`), the same statistic bit for bit,
and the zone of a wide table's first columns is the zone the old screen
fits, byte for byte. Mutants: two levels' product read as a sum; a
level's score read from its weights; the one-pass screen taken where
the fit holds more than its intercept.

THE QUESTIONS OF A WIDE TABLE, PUT IN GROUPS (lane W5-302). Past twelve
questions, the columns that raised the same question are put at the
keyboard as one question naming each of them, in the first prompts and in
the round that puts the questions file's entries (its checklist among
them: 244 entries one at a time on the 302-column table at 20,000 rows);
the answer typed, Enter included, is each one's answer; the person
question is always put on its own; twelve or fewer are put as before,
word for word. Mutants: no group past twelve; the person question
grouped.

THE TWIN'S FORMS READ ONCE AN ASK (lane W5-302). The free-text writer
reads each published form's words, class and band once for an ask, not
once a group: the same twin byte for byte for a table of codes of many
forms. Mutant: every form taken to read as the class asked.

THE HOLDER'S ANSWERS (`wide_table.holder_answer`, the driver's). The
holder answers a column's question by what is known of it: a key
`identifier`, a measurement `measurement`, the years' Safe Harbor
question `yes`, the person question `identifier` for the person's key
alone. Mutant: every key answered `keep`.
"""

from __future__ import annotations

import collections
import csv
import json
import math
import pathlib
import random

import pytest

import wide_table as W
from synthtwin import asking, cli, inside_keyed, reading, results, taxonomy
from synthtwin import inside_relations as relations
from test_inside_keyed import DATED, HELD, TYPED, long_table


def _column(rows: "list[list[str]]", name: str) -> "list[str]":
    place = W.NAMES.index(name)
    return [row[place] for row in rows]


def _numbers(cells: "list[str]") -> "list[float | None]":
    out: "list[float | None]" = []
    for cell in cells:
        try:
            out += [float(cell)]
        except ValueError:
            out += [None]
    return out


def _correlation(xs: "list[float | None]", ys: "list[float | None]") -> float:
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    mx = math.fsum(x for x, _y in pairs) / len(pairs)
    my = math.fsum(y for _x, y in pairs) / len(pairs)
    sxy = math.fsum((x - mx) * (y - my) for x, y in pairs)
    sxx = math.fsum((x - mx) ** 2 for x, _y in pairs)
    syy = math.fsum((y - my) ** 2 for _x, y in pairs)
    return sxy / math.sqrt(sxx * syy)


def _share(cells: "list[str]", given: "list[str]", value: str, condition: str) -> float:
    picked = [cell for cell, other in zip(cells, given) if other == condition]
    return sum(1 for cell in picked if cell == value) / len(picked)


@pytest.fixture(scope="module")
def rows() -> "list[list[str]]":
    return W.rows(3000, 1)


def test_every_column_is_in_exactly_one_family_and_the_table_is_302_wide(rows: "list[list[str]]") -> None:
    named = [name for family in W.FAMILIES.values() for name in family]
    assert len(named) == len(set(named)) == W.COLUMNS == 302
    assert sorted(named) == sorted(W.NAMES)
    assert {len(row) for row in rows} == {302}
    for response, parents in W.RELATIONS.items():
        assert all(W.NAMES.index(parent) < W.NAMES.index(response) for parent in parents)


def test_the_same_seed_writes_the_same_bytes_and_another_seed_others(tmp_path: pathlib.Path) -> None:
    first, again, other = tmp_path / "a.csv", tmp_path / "b.csv", tmp_path / "c.csv"
    assert W.write(first, 500, 7) == W.write(again, 500, 7)
    W.write(other, 500, 8)
    assert first.read_bytes() == again.read_bytes()
    assert first.read_bytes() != other.read_bytes()


def test_the_person_repeats_and_each_family_holds_its_kind(rows: "list[list[str]]") -> None:
    people = collections.Counter(_column(rows, W.PERSON))
    assert 1 < len(rows) / len(people) < 6 and max(people.values()) <= 12
    assert len(set(_column(rows, "col_002"))) == len(rows)
    for name in W.FAMILIES["flag"]:
        assert set(_column(rows, name)) == {"Y", "N"}
    for name in W.FAMILIES["sparse"]:
        assert sum(1 for cell in _column(rows, name) if cell == "") >= 0.8 * len(rows)
    for name in W.FAMILIES["chain"] + W.FAMILIES["series"]:
        assert sum(1 for value in _numbers(_column(rows, name)) if value is not None) >= 0.95 * len(rows)
    years = _column(rows, "col_007")
    first: "dict[str, str]" = {}
    for person, value in zip(_column(rows, W.PERSON), years):
        assert first.setdefault(person, value) == value
    assert max(int(value) for value in years) > 89


def test_every_relation_is_in_the_cells(rows: "list[list[str]]") -> None:
    assert _correlation(_numbers(_column(rows, "col_109")), _numbers(_column(rows, "col_108"))) > 0.4
    assert _correlation(_numbers(_column(rows, "col_298")), _numbers(_column(rows, "col_120"))) > 0.4
    assert _share(_column(rows, "col_013"), _column(rows, "col_009"), "Y", "Y") > 0.5
    assert _share(_column(rows, "col_013"), _column(rows, "col_009"), "Y", "N") < 0.3
    present = _column(rows, "col_208")
    given = _column(rows, "col_014")
    assert _share(["Y" if cell else "N" for cell in present], given, "Y", "Y") > 0.2
    assert _share(["Y" if cell else "N" for cell in present], given, "Y", "N") < 0.06
    x = _numbers(_column(rows, "col_130"))
    y = _numbers(_column(rows, "col_300"))
    flag = _column(rows, "col_015")
    with_flag = _correlation([a for a, f in zip(x, flag) if f == "Y"], [b for b, f in zip(y, flag) if f == "Y"])
    without = _correlation([a for a, f in zip(x, flag) if f == "N"], [b for b, f in zip(y, flag) if f == "N"])
    assert with_flag > 0.6 and without < 0.0


def test_the_holder_answers_each_column_by_what_is_known_of_it() -> None:
    answer = W.holder_answer
    assert answer("col_290", ["identifier", "keep"], False) == "identifier"
    assert answer("col_288", ["identifier", "keep"], True) == "keep"
    assert answer(W.PERSON, ["identifier", "keep"], True) == "identifier"
    assert answer("col_150", ["measurement", "code", "keep"], False) == "measurement"
    assert answer("col_007", ["yes", "no"], False) == "yes"
    assert answer("col_268", ["identifier", "keep"], False) == "keep"
    assert answer("col_268", ["yes", "no"], False) == "no"


# -- the keyed zone's key on a wide table (lane W5-302) ---------------------------------------------------------


def _slotted(rows: int, seed: int) -> "dict[str, list[str]]":
    """A table of no key: a person's rows, a clock of forty slots moving within a person, a number written on two rows
    in a hundred and a measurement on every row; no slot changes how any value is written."""
    draw = random.Random(seed)
    out: "dict[str, list[str]]" = {"person": [], "slot": [], "seldom": [], "level": []}
    person, left = 0, 0
    for _row in range(rows):
        if left == 0:
            person, left = person + 1, 1 + draw.randrange(6)
        left -= 1
        out["person"] += [f"P{1000 + person}"]
        slot = draw.randrange(40)
        out["slot"] += [f"{6 + slot // 4:02d}:{15 * (slot % 4):02d}"]
        out["seldom"] += [f"{draw.gauss(20.0, 4.0):.1f}" if draw.random() < 0.02 else ""]
        out["level"] += [f"{draw.gauss(50.0, 9.0):.1f}"]
    return out


def test_a_mostly_empty_column_makes_no_label_a_key() -> None:
    """Mutant: a level's reading counted with no written cell (`TYPED_WRITTEN_LEAST` 0) takes the slot for a key."""
    table = _slotted(1200, 3)
    owners, _count = inside_keyed._persons(table["person"])
    content = ["slot", "seldom", "level"]
    assert inside_keyed.key_of(table, content, owners) == ""
    assert inside_keyed.build_zone(table, "person") is None


def test_the_key_of_a_keyed_table_stands() -> None:
    """The battery's own long table keeps its key under the written-cells rule, and the zone it builds."""
    table = long_table(2000, 1)
    zone = inside_keyed.build_zone(table, "subject", (), DATED, {}, HELD, TYPED)
    assert zone is not None and zone["key"] == "item"


def _reference_key(columns: "dict[str, list[str]]", content: "list[str]", owners: "list[int]") -> str:
    """`key_of` before lane W5-302's one pass a label: every column's typing and moving read for every label."""
    sample = inside_keyed._spread_rows(len(owners), inside_keyed.KEY_SAMPLE)
    cut = {name: [inside_keyed._bare(columns[name][row]) for row in sample] for name in content}
    cut_owners = [owners[row] for row in sample]
    best, best_score = "", 0
    for key in content:
        cells = cut[key]
        if not inside_keyed.KEY_LEVELS_LEAST <= len(inside_keyed._counts(cells)) <= inside_keyed.KEY_LEVELS_MOST:
            continue
        if inside_keyed._numeric_share(cells) >= 0.5 or not inside_keyed._varies_within(cells, cut_owners):
            continue
        score, typed = 0, False
        for other in content:
            if other == key:
                continue
            if inside_keyed._typed_by(cells, cut[other], inside_keyed.TYPED_WRITTEN_LEAST):
                typed = True
            if inside_keyed._moved_by(cells, cut[other]):
                score += 1
        if typed and score > best_score:
            best, best_score = key, score
    return best


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_one_pass_a_label_finds_the_key_every_pass_found(seed: int) -> None:
    """The label read once a column for its typing, the moved columns counted only for a label that types one."""
    for table, person in ((long_table(1500, seed), "subject"), (_slotted(1200, seed), "person")):
        owners, _count = inside_keyed._persons(table[person])
        content = [name for name in table if name != person and name not in DATED]
        assert inside_keyed.key_of(table, content, owners) == _reference_key(table, content, owners)


def _written_table(tmp_path: pathlib.Path, table: "dict[str, list[str]]") -> reading.Table:
    path = tmp_path / "table.csv"
    names = list(table)
    with open(path, "w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out, lineterminator="\n")
        writer.writerow(names)
        writer.writerows(zip(*[table[name] for name in names]))
    return reading.read_table(str(path))


def test_the_key_is_read_from_its_sample_rows_alone(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Mutant: each column handed to the key whole; and the sampled key is `build_zone`'s, keyed table or not."""
    monkeypatch.setattr(inside_keyed, "KEY_SAMPLE", 700)
    seen: "list[int]" = []
    sampled_key = inside_keyed.sampled_key

    def spied(person_cells: "list[str]", sampled: "dict[str, list[str]]", *rest: object) -> str:
        seen.extend(len(cells) for cells in sampled.values())
        return sampled_key(person_cells, sampled, *rest)  # type: ignore[arg-type]

    monkeypatch.setattr(inside_keyed, "sampled_key", spied)
    keyed = long_table(1500, 2)
    read = _written_table(tmp_path, keyed)
    assert cli._keyed_sample_holds_a_key(read, "subject", (), DATED)
    assert set(seen) == {700}
    whole = {name: [str(cell) for cell in reading.column_values(read, place)] for place, name in enumerate(read.column_names)}
    assert inside_keyed.build_zone(whole, "subject", (), DATED) is not None
    plain = _slotted(1500, 2)
    assert not cli._keyed_sample_holds_a_key(_written_table(tmp_path, plain), "person", (), ())
    assert inside_keyed.build_zone(plain, "person") is None


@pytest.mark.parametrize("seed", [1, 2])
def test_a_column_read_once_is_typed_as_its_cells_are(seed: int) -> None:
    """`_typed_by_read` over a column read once (`_read`) answers as `_typed_by` over its cells, for every label and column.

    Mutant: a level's numeric share read over its rows rather than its written cells.
    """
    wide = W.rows(1500, seed)
    chosen = W.NAMES[5:30] + W.NAMES[205:225] + W.NAMES[265:270]
    tables = [long_table(1500, seed), _slotted(1500, seed),
              {name: [row[W.NAMES.index(name)] for row in wide] for name in chosen}]
    compared = 0
    for table in tables:
        cut = {name: [inside_keyed._bare(cell) for cell in cells] for name, cells in table.items()}
        reads = {name: inside_keyed._read(cells) for name, cells in cut.items()}
        for key, key_cells in cut.items():
            if not 3 <= len(set(key_cells)) <= 1000:
                continue
            places = inside_keyed._places_by_level(key_cells)
            for other, cells in cut.items():
                if other == key:
                    continue
                for least in (0, inside_keyed.TYPED_WRITTEN_LEAST):
                    assert inside_keyed._typed_by_read(places, reads[other], least) == inside_keyed._typed_by(
                        key_cells, cells, least), (key, other, least)
                    compared += 1
    assert compared > 1000


# -- the relations' screen of a label parent in one pass (lane W5-302) -------------------------------------------


def _bits(value: float) -> str:
    return value.hex()


@pytest.mark.parametrize("seed", [1, 2, 3, 4])
def test_a_label_parent_screened_in_one_pass_gives_the_same_statistic(seed: int) -> None:
    """`indicator_statistic` is `score_statistic` bit for bit, for a number's fit and a label's, a level of no rows among them.

    Mutant: two levels' product read as their weights' sum (the block's information not diagonal).
    """
    draw = random.Random(seed)
    rows = 400
    codes = [min(int(draw.expovariate(0.4)), 11) for _row in range(rows)]
    wanted = [1, 2, 3, 5, 7, 9, 11, 12]
    ones = [[1.0 for _row in range(rows)]]
    numbers = [draw.gauss(3.0, 2.0) + 0.7 * (code == 2) for code in codes]
    fits = [relations.least_squares(ones, numbers)]
    used = [row for row in range(rows) if draw.random() < 0.7]
    outcome = [1.0 if draw.random() < 0.2 + 0.1 * (codes[row] == 1) else 0.0 for row in used]
    fits += [relations.logistic([[1.0 for _row in used]], outcome)]
    for fit, on in ((fits[0], list(range(rows))), (fits[1], used)):
        block = [[1.0 if codes[row] == level else 0.0 for row in on] for level in wanted]
        columns = [[1.0 for _row in on]]
        assert _bits(relations.indicator_statistic(fit, codes, wanted, on)) == _bits(
            relations.score_statistic(fit, columns, block))


def _encoded_wide(table: "list[list[str]]", persons: "relations.Persons", sample: "list[int]") -> "list[relations.Encoded]":
    encoded: "list[relations.Encoded]" = []
    for place, name in enumerate(W.NAMES[:115]):
        family = W.FAMILY_OF[name]
        cells = [row[place] for row in table]
        if family in ("years", "series", "chain"):
            spec = relations.ColumnSpec(name, place, relations.NUMBER, 90 if name == "col_007" else 0, (), "")
        elif family in ("flag", "code"):
            spec = relations.ColumnSpec(name, place, relations.LABEL, 0, tuple(sorted(set(cells))), "")
        else:
            continue
        found = relations.encode(spec, cells, sample, persons)
        if found is not None:
            encoded += [found]
    return encoded


def test_the_screen_of_a_wide_table_keeps_its_zone(monkeypatch: pytest.MonkeyPatch) -> None:
    """The relations zone of the wide table's first 115 columns (letters, codes, numbers) is the zone the old screen fits.

    Mutant: a level's score read from its weights in place of its residuals.
    """
    table = W.rows(1000, 5)
    persons = relations.persons_of([row[0] for row in table])
    sample = relations.sample_rows(len(table), persons=persons)
    owners = [persons.person[row] for row in sample]
    fast = relations.fit_zone(_encoded_wide(table, persons, sample), len(sample), len(table), owners, W.PERSON)
    monkeypatch.setattr(relations, "_indicators_of", lambda *_args: None)
    slow = relations.fit_zone(_encoded_wide(table, persons, sample), len(sample), len(table), owners, W.PERSON)
    assert json.dumps(fast, sort_keys=True) == json.dumps(slow, sort_keys=True)


def test_a_fit_holding_more_than_its_intercept_is_screened_as_before() -> None:
    """A block of levels against a fit holding a second term is read the old way (`score_statistic`), not from sums."""
    draw = random.Random(9)
    rows = 300
    codes = [draw.randrange(5) for _row in range(rows)]
    other = [draw.gauss(0.0, 1.0) for _row in range(rows)]
    frames = {"parent": relations.Frame(relations.LABEL, [], [], codes),
              "other": relations.Frame(relations.NUMBER, other, [relations.PRESENT for _row in range(rows)], [])}
    response = [0.4 * x + (0.5 if code == 3 else 0.0) + draw.gauss(0.0, 1.0) for x, code in zip(other, codes)]
    target = relations.Target(relations.NUMBER, response, list(range(rows)), [], 0)
    chosen = [relations.Block((["z", "other"],), "other", "main")]
    design = relations._design(target, chosen, frames, rows)
    fits = relations._fits(target, design)
    block = relations.main_block("parent", frames["parent"])
    assert block is not None and len(design[0]) == 2
    statistic, freedom = relations._block_statistic(target, fits, design, block, frames, rows)
    values = relations._evaluated(block, frames, rows, None)
    fit = fits[0]
    assert fit is not None
    assert _bits(statistic) == _bits(relations.score_statistic(fit, design[0], values)) and freedom == len(values)


# -- the questions of a wide table, put in groups (lane W5-302) -------------------------------------------------


def _figures(name: str) -> asking.Question:
    return asking.Question(name, taxonomy.ROLE_CONTINUOUS, asking.BECAUSE_PADDED, "every value is written in figures",
                           asking._numeric_choices(asking.ANSWER_MEASUREMENT, taxonomy.ROLE_CONTINUOUS, 11),
                           asking.ANSWER_MEASUREMENT)


def _person_question(name: str) -> asking.Question:
    return asking.Question(name, taxonomy.ROLE_IDENTIFIER, asking.BECAUSE_REPEATS_AND_MANY, "repeats",
                           asking._person_choices(taxonomy.ROLE_IDENTIFIER, 11), asking.ANSWER_KEEP)


def _typing(monkeypatch: pytest.MonkeyPatch, typed: "list[str]") -> "list[str]":
    """The keys typed, one a prompt, and the screen said (every prompt counted)."""
    said: "list[str]" = []
    keys = iter(typed)
    monkeypatch.setattr(cli, "_say", lambda text, end="\n": said.append(text))
    monkeypatch.setattr("builtins.input", lambda _prompt: next(keys))
    return said


def test_a_wide_table_puts_the_same_question_once_for_its_columns(monkeypatch: pytest.MonkeyPatch) -> None:
    """Past twelve questions, the columns of one question are put as one; the answer is each one's, Enter each one's.

    Mutants: no group past twelve (every column put on its own); the person question grouped with another.
    """
    questions = [_figures(f"col_{k:03d}") for k in range(16)] + [_person_question("col_100"), _person_question("col_101")]
    groups = cli._question_groups(questions)
    assert [len(group) for group in groups] == [16, 1, 1]
    said = _typing(monkeypatch, ["3", "", ""])
    put = cli._put_the_questions(questions)
    assert put is not None
    assert put[1] == [f"col_{k:03d}" for k in range(16)]
    assert len(put[6]) == 2
    assert "3 questions for these 18 columns" in said[0]
    assert "Columns 1 to 16 of 18: 16 columns raised the same question" in said[1]
    said = _typing(monkeypatch, ["", "", ""])
    put = cli._put_the_questions(questions)
    assert put is not None and put[1] == [] and len(put[6]) == 18


def test_twelve_questions_or_fewer_are_put_each_on_its_own_as_before(monkeypatch: pytest.MonkeyPatch) -> None:
    """A table of twelve questions is asked as it always was: a prompt a column, the same screen word for word."""
    questions = [_figures(f"col_{k:03d}") for k in range(12)]
    assert [len(group) for group in cli._question_groups(questions)] == [1] * 12
    said = _typing(monkeypatch, [""] * 12)
    put = cli._put_the_questions(questions)
    assert put is not None and len(put[6]) == 12
    assert said[1:] == [cli._the_question(question, k + 1, 12) for k, question in enumerate(questions)]
    assert said[0].endswith("printed at the end.")


def test_the_fit_lets_each_number_go_once_its_frame_holds_it() -> None:
    """After the fit, no number column's positions are held (`Encoded.positions` empty), its frame's scores standing.

    Mutant: the positions kept through the fit.
    """
    table = W.rows(600, 6)
    persons = relations.persons_of([row[0] for row in table])
    sample = relations.sample_rows(len(table), persons=persons)
    encoded = _encoded_wide(table, persons, sample)[:40]
    frames: "dict[str, relations.Frame]" = {}
    relations.fit_zone(encoded, len(sample), len(table), [persons.person[row] for row in sample], W.PERSON, frames)
    numbers = [column for column in encoded if column.entry["kind"] == relations.NUMBER]
    assert numbers and all(column.positions == [] for column in numbers)
    assert all(len(frames[str(column.entry["name"])].scores) == len(sample) for column in numbers)


def _listed(column: str, order: int) -> results.Asked:
    offers = tuple(results.Offer(choice.answer, choice.means, choice.publishes)
                   for choice in asking._numeric_choices(asking.ANSWER_MEASUREMENT, taxonomy.ROLE_CONTINUOUS, 11))
    return results.Asked(results.SECTION_CHECKLIST, order, column, taxonomy.ROLE_CONTINUOUS, asking.BECAUSE_LISTED,
                         "numbers", asking.ANSWER_MEASUREMENT, offers, False, column)


def _person_entry(column: str, order: int) -> results.Asked:
    offers = tuple(results.Offer(choice.answer, choice.means, choice.publishes)
                   for choice in asking._person_choices(taxonomy.ROLE_IDENTIFIER, 11))
    return results.Asked(results.SECTION_ASKED, order, column, taxonomy.ROLE_IDENTIFIER, asking.BECAUSE_REPEATS_AND_MANY,
                         "repeats", asking.ANSWER_KEEP, offers, False, column)


def test_the_questions_files_round_at_the_keyboard_puts_the_same_entries_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """Past twelve entries, the entries of one question are put as one; the answer is each entry's; twelve put as before.

    Mutants: no group past twelve; the person question grouped with another.
    """
    entries = [_listed(f"col_{k:03d}", k + 1) for k in range(20)] + [_person_entry("col_200", 1), _person_entry("col_201", 2)]
    assert [len(group) for group in cli._entry_groups(entries)] == [20, 1, 1]
    said = _typing(monkeypatch, ["2", "", ""])
    given, ended = cli._put_the_entries(entries)
    assert not ended and len(given) == 22
    assert [answer for record, answer in given if record.section == results.SECTION_CHECKLIST] == ["code"] * 20
    assert "3 questions for these 22 entries" in "".join(said)
    assert "20 columns raised the same question (1 to 20 of 22 in this round)" in "".join(said)
    twelve = entries[:12]
    said = _typing(monkeypatch, [""] * 12)
    given, ended = cli._put_the_entries(twelve)
    assert not ended and len(given) == 12
    assert [text for text in said if "Question" in text or "of 12 in this round" in text] == [
        cli._the_entry(record, 0, k + 1, 12) for k, record in enumerate(twelve)]


def _harbor_question(name: str) -> asking.Question:
    return asking.Question(name, taxonomy.ROLE_COUNT, asking.BECAUSE_SAFE_HARBOR_AGES, "numbers from 0 to 125",
                           asking._numeric_choices(asking.ANSWER_MEASUREMENT, taxonomy.ROLE_COUNT, 11),
                           asking.ANSWER_MEASUREMENT)


def _harbor_entry(column: str, order: int) -> results.Asked:
    offers = (results.Offer("no", "not ages", "every value"), results.Offer("yes", "ages", "ages to 90"))
    return results.Asked(results.SECTION_ASKED, order, column, taxonomy.ROLE_COUNT, asking.BECAUSE_SAFE_HARBOR_AGES,
                         "numbers from 0 to 125", asking.SAFE_HARBOR_TOP_CODED, offers, False, column)


def _held_entry(column: str, order: int) -> results.Asked:
    offers = (results.Offer("keep", "labels", "its labels"), results.Offer("identifier", "record numbers", "nothing"))
    return results.Asked(results.SECTION_ASKED, order, column, taxonomy.ROLE_IDENTIFIER, asking.BECAUSE_PADDED,
                         "figures", asking.ANSWER_IDENTIFIER, offers, False, column)


def test_hipaa_first_a_question_that_could_release_a_hold_is_never_grouped() -> None:
    """Safe Harbor questions, a held column's question and a held or top-coded entry are put one a column, past twelve too.

    Mutants: Safe Harbor reasons grouped at the first prompts; a held column grouped; an entry held as record numbers
    grouped; a top-coded entry grouped.
    """
    harbor = [_harbor_question(f"col_{k:03d}") for k in range(14)]
    assert [len(group) for group in cli._question_groups(harbor)] == [1] * 14
    figures = [_figures(f"col_{k:03d}") for k in range(14)]
    held = tuple(f"col_{k:03d}" for k in range(7))
    assert [len(group) for group in cli._question_groups(figures, held)] == [1] * 7 + [7]
    entries = [_harbor_entry(f"col_{k:03d}", k + 1) for k in range(8)] + [_held_entry(f"col_{k:03d}", k + 9)
                                                                           for k in range(8, 16)]
    assert [len(group) for group in cli._entry_groups(entries)] == [1] * 16


# -- the twin's free-text forms read once an ask (lane W5-302) -----------------------------------------------------


def _coded(rows: int, seed: int) -> str:
    """A table of codes of many forms (letters and figures in mixed places, some all figures) beside a measurement."""
    draw = random.Random(seed)
    lines = ["code,level"]
    for row in range(rows):
        shape = draw.randrange(12)
        parts = []
        for place in range(6):
            parts += [chr(ord("A") + draw.randrange(20)) if (shape >> (place % 4)) & 1 else str(draw.randrange(10))]
        lines += [f"{''.join(parts)}{row % 7},{draw.gauss(50.0, 9.0):.1f}"]
    return "\n".join(lines) + "\n"


def _twin_of(folder: pathlib.Path, text: str) -> bytes:
    import contextlib
    import io

    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "codes.csv"
    table.write_text(text, encoding="utf-8", newline="\n")
    said = io.StringIO()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        assert cli.main(["profile", str(table), "--out-dir", str(folder), "--replace"], small_tables_refused=False) == 0
        assert cli.main(["generate", str(folder / "codes-profile.json"), "--out-dir", str(folder), "--seed", "3",
                         "--replace"], small_tables_refused=False) == 0
    return (folder / "codes-twin.csv").read_bytes()


def test_the_forms_read_once_an_ask_write_the_same_twin(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A column of codes of many published forms: the twin with each form read once an ask is the twin read every time.

    Mutant: every form taken to read as the class asked.
    """
    from synthtwin import generation

    text = _coded(3000, 4)
    once = _twin_of(tmp_path / "once", text)
    monkeypatch.setattr(generation, "_FormsRead", lambda: None)
    every = _twin_of(tmp_path / "every", text)
    assert once == every
