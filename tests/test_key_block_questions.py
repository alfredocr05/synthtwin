"""A long table's key block put its own question (lane IN-4c, plan P4-D514): asked only where the description cannot decide, freed only by `measurement` or `code`, held by `identifier`, never freed where its cells look like identifiers to the twin checks.

A key block -- one measurement's cells under the column that says which
measurement each row holds -- that a column of its name and values would
hold until a question offering `identifier` is answered (figures of one
width, two numbers joined by a slash) was held in that question's
unanswered state with nobody able to answer it (P4-D487, K7). The
questions file now puts such a block its own question, in a section of its
own. Unit cases on a small invented long table (the library path, below
the owner's table floor: a test device), the section written and read
back from the questions file and from a plain-text answers file, the
keyed zone's pairs joined again at the record's correlation, and a copy
left beside a source a level top-codes.
The commands at the table floor are `tests/test_inside_keyed.py`'s cases.
Every table here is invented, its names generic.
"""

from __future__ import annotations

import csv
import io
import json
import math
import pathlib
import random

import pytest

import fixtures
from synthtwin import asking, contract, errors, inside_keyed, parsing, profile, reading, taxonomy, twin_checks

FLOOR = 11
VALUE = "item_value"
KEY = "item_key"


def long_table(people: int = 160, seed: int = 7) -> "tuple[list[str], list[list[str]]]":
    """An invented long table: a pulse of a person's own level, pressures written `a/b`, a three-figure salt result,
    a run of six-figure chart sequence numbers (one a row), and a key named as an account number."""
    draw = random.Random(seed)
    header = ["person_id", KEY, VALUE]
    rows: "list[list[str]]" = []
    sequence = 400000
    for place in range(people):
        person = f"Q{7000 + 3 * place}"
        level = draw.gauss(0, 5)
        for _visit in range(4):
            rows += [[person, "pulse", f"{max(40, round(draw.gauss(78 + level, 9)))}"]]
            upper = round(draw.gauss(125 + level, 14))
            rows += [[person, "press", f"{upper}/{round(0.55 * upper + draw.gauss(12, 5))}"]]
            rows += [[person, "salt", f"{min(152, max(128, round(draw.gauss(140, 3))))}"]]
            sequence += 1 + draw.randrange(7)
            rows += [[person, "chart_seq", f"{sequence}"]]
            rows += [[person, "account_no", f"{min(152, max(128, round(draw.gauss(140, 3))))}"]]
    return header, rows


def _table(tmp_path: pathlib.Path) -> reading.Table:
    header, rows = long_table()
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    path = fixtures.write(tmp_path, "long.csv", out.getvalue())
    return reading.read_table(str(path), small_cell_floor=FLOOR)


def _described(
    table: reading.Table, answered: "tuple[tuple[str, str, str], ...]" = ()
) -> "tuple[dict[str, object], list[asking.MeasurementAsked]]":
    """The table described as the command describes a long table, the person declared and the keyed reading on, with
    the key blocks' own answers; and the blocks put their own question."""
    asked: "list[asking.MeasurementAsked]" = []
    document = profile.build_document(
        table,
        taxonomy.Settings(small_cell_floor=FLOOR),
        ["person_id"],
        subjects=["person_id"],
        top_code=True,
        harbor_year=taxonomy.SAFE_HARBOR_REFERENCE_YEAR,
        keyed_kept=[],
        keyed_answered=answered,
        keyed_asked=asked,
    )
    return document, asked


def _blocks(document: "dict[str, object]") -> "dict[str, dict[str, object]]":
    for block in document["columns"]:  # type: ignore[union-attr]
        if block["name"] == VALUE:  # type: ignore[index]
            return {f"{entry['key']}": entry["block"] for entry in block["by_key"]["key_blocks"]}  # type: ignore[index]
    raise KeyError(VALUE)


def _held(block: "dict[str, object]") -> bool:
    return block["role"] == taxonomy.ROLE_IDENTIFIER


@pytest.fixture(scope="module")
def table(tmp_path_factory: pytest.TempPathFactory) -> reading.Table:
    return _table(tmp_path_factory.mktemp("long"))


@pytest.fixture(scope="module")
def unanswered(table: reading.Table) -> "tuple[dict[str, object], list[asking.MeasurementAsked]]":
    return _described(table)


def test_a_held_block_is_put_its_own_question_only_where_an_answer_could_free_it(unanswered) -> None:  # type: ignore[no-untyped-def]
    """The pressures and the salt result, held by the question their values would be put, are each put one question offering `measurement`, with what it saw and the role it would describe; the chart sequence numbers (whose values cover the checks' key-like share) and the key named as an account number stay held and are asked nothing; the pulse is described and asked nothing (mutants: the key-like share not read; the question put where no answer frees the block)."""
    document, asked = unanswered
    blocks = _blocks(document)
    assert [(one.column, one.key, one.measurement) for one in asked] == [(VALUE, KEY, "press"), (VALUE, KEY, "salt")]
    by = {one.measurement: one for one in asked}
    assert by["press"].releases == ((asking.ANSWER_MEASUREMENT, taxonomy.ROLE_JOINED),)
    assert by["salt"].releases == ((asking.ANSWER_MEASUREMENT, taxonomy.ROLE_COUNT),)
    assert "'/'" in by["press"].shape and "3 characters wide" in by["salt"].shape
    for name in ("press", "salt", "chart_seq", "account_no"):
        assert _held(blocks[name]), name
    assert not _held(blocks["pulse"])


def test_measurement_frees_its_own_block_and_identifier_holds_it(table: reading.Table) -> None:
    """`measurement` to the salt result's own question describes that block as a count (its numbers published) and leaves the pressures held and still asked; `identifier` holds the pressures as a column so declared, asked no more; every other block and column is as the unanswered description writes it (mutants: an answer read for every block of the column; an answer not read)."""
    document, asked = _described(table, ((VALUE, "SALT", asking.ANSWER_MEASUREMENT), (VALUE, "press", asking.ANSWER_IDENTIFIER)))
    blocks = _blocks(document)
    assert blocks["salt"]["role"] == taxonomy.ROLE_COUNT and blocks["salt"]["structural_role"] == "data"
    assert "mean" in blocks["salt"]
    assert _held(blocks["press"]) and "you told synthtwin" in f"{blocks['press']['detection_evidence']}"
    assert asked == []
    alone, asked_alone = _described(table, ((VALUE, "salt", asking.ANSWER_MEASUREMENT),))
    assert [one.measurement for one in asked_alone] == ["press"]
    plain, _asked = _described(table)
    for name in ("press", "pulse", "chart_seq", "account_no"):
        assert _blocks(alone)[name] == _blocks(plain)[name], name
    for one, other in zip(alone["columns"], plain["columns"]):  # type: ignore[arg-type]
        if one["name"] != VALUE:  # type: ignore[index]
            assert one == other


def test_no_answer_frees_a_block_whose_cells_look_like_identifiers(table: reading.Table) -> None:
    """`measurement` written for the chart sequence numbers (six figures, a different one on every row) and for the key named as an account number frees neither: both stay held, as record numbers (mutants: the checks' reading not read before an answer; the key-like share not read)."""
    document, asked = _described(table, ((VALUE, "chart_seq", asking.ANSWER_MEASUREMENT),
                                         (VALUE, "account_no", asking.ANSWER_MEASUREMENT)))
    blocks = _blocks(document)
    assert _held(blocks["chart_seq"]) and _held(blocks["account_no"])
    assert [one.measurement for one in asked] == ["press", "salt"]
    assert profile._reads_as_identifiers_to_the_checks("chart_seq", ["400001", "400005", "400009"])
    assert twin_checks.reads_as_an_identifier("account_no", ["140", "141", "140"])
    assert not profile._reads_as_identifiers_to_the_checks("salt", ["140", "141", "140", "139"])


def _section(asked: "list[asking.MeasurementAsked]", answered: "tuple[tuple[str, str, str], ...]" = ()) -> "dict[str, object]":
    section = asking.measurement_section(asked, answered, FLOOR)
    assert section is not None
    return {asking.MEASUREMENTS_ASKED: section, "asked": [], "checklist": {"columns": []}}


def test_the_section_is_written_with_no_value_and_read_back(unanswered) -> None:  # type: ignore[no-untyped-def]
    """Each open block is one entry naming its column, its measurement and the column naming it, read as `identifier`, its offers `identifier` first; no value of the table is in it; an answer is read whatever its capitals and spaces, written back answered and asked no more; a blank answer is none (mutants: the entry's measurement not read; an answer written back open)."""
    _document, asked = unanswered
    file = _section(asked)
    entries = file[asking.MEASUREMENTS_ASKED][asking.MEASUREMENTS_ENTRIES]  # type: ignore[index]
    assert [(e["column"], e["measurement"], e["measurement_named_by"], e["read_as_now"], e["your_answer"])
            for e in entries] == [(VALUE, "press", KEY, "identifier", ""), (VALUE, "salt", KEY, "identifier", "")]
    assert [a["answer"] for a in entries[1]["answers_you_can_give"]] == ["identifier", "measurement"]
    header, rows = long_table()
    values = {row[2] for row in rows if row[1] in ("press", "salt")}
    words = f"{file}"
    assert not [value for value in values if f"'{value}'" in words or f" {value} " in words]
    assert asking.measurement_answers(file, "q.json") == ()
    entries[1]["your_answer"] = "  Measurement "
    read = asking.measurement_answers(file, "q.json")
    assert read == ((VALUE, "salt", asking.ANSWER_MEASUREMENT),)
    again = _section([one for one in asked if one.measurement == "press"], read)
    kept = again[asking.MEASUREMENTS_ASKED][asking.MEASUREMENTS_ENTRIES]  # type: ignore[index]
    assert [(e["measurement"], e["read_as_now"], e["your_answer"]) for e in kept] == [
        ("salt", "measurement", "measurement"), ("press", "identifier", "")]
    assert asking.measurement_answers(again, "q.json") == read


def test_an_answer_not_offered_or_given_two_ways_is_refused(unanswered) -> None:  # type: ignore[no-untyped-def]
    """An answer the entry does not offer (`code` where only `measurement` frees the block, or a word of one's own), an entry with no measurement named, and two entries giving one measurement different answers are each refused, naming the file (mutants: any offered word taken; two answers for one measurement taken)."""
    _document, asked = unanswered
    for word in ("code", "maybe"):
        file = _section(asked)
        file[asking.MEASUREMENTS_ASKED][asking.MEASUREMENTS_ENTRIES][1]["your_answer"] = word  # type: ignore[index]
        with pytest.raises(ValueError, match="q.json"):
            asking.measurement_answers(file, "q.json")
    file = _section(asked)
    entries = file[asking.MEASUREMENTS_ASKED][asking.MEASUREMENTS_ENTRIES]  # type: ignore[index]
    entries[1]["measurement"] = ""
    entries[1]["your_answer"] = "measurement"
    with pytest.raises(ValueError, match="no measurement"):
        asking.measurement_answers(file, "q.json")
    file = _section(asked)
    entries = file[asking.MEASUREMENTS_ASKED][asking.MEASUREMENTS_ENTRIES]  # type: ignore[index]
    entries += [dict(entries[1])]
    entries[1]["your_answer"] = "measurement"
    entries[2]["your_answer"] = "identifier"
    with pytest.raises(ValueError, match="two things"):
        asking.measurement_answers(file, "q.json")


def test_a_plain_text_line_answers_a_measurement_by_its_name(tmp_path: pathlib.Path, unanswered) -> None:  # type: ignore[no-untyped-def]
    """A plain-text answers file's line `salt = Measurement` answers the salt result's own question, read back as `measurement`; a line giving an answer the entry does not offer, and two lines for one measurement, are refused naming the line (mutant: a line not read as a measurement's)."""
    _document, asked = unanswered
    beside = tmp_path / "long-questions.json"
    beside.write_text(json.dumps(_section(asked), indent=2), encoding="utf-8", newline="\n")
    answers = tmp_path / "answers.txt"
    answers.write_text("# the measurements\nsalt = Measurement\n", encoding="utf-8", newline="\n")
    document = contract.load_answers(str(answers), str(beside))
    assert asking.measurement_answers(document, "answers.txt") == ((VALUE, "salt", asking.ANSWER_MEASUREMENT),)
    for lines, words in (("salt = code\n", "does not offer"), ("salt = measurement\nsalt = identifier\n", "line 1")):
        answers.write_text(lines, encoding="utf-8", newline="\n")
        with pytest.raises(errors.ProfileError, match=words):
            contract.load_answers(str(answers), str(beside))


# -- the keyed zone: a released block of pairs joined again at the record's correlation --------------------------


def _pair_table(rows: int, seed: int, tight: bool = False) -> "dict[str, list[str]]":
    """An invented long table of a person, an item and a reading: pairs `a/b` (the second part following the first and
    always well below it, or -- ``tight`` -- one to four below it), a pulse and a word."""
    draw = random.Random(f"pairs-{seed}")
    out: "dict[str, list[str]]" = {"subject": [], "item": [], "reading": []}
    person = 0
    while len(out["subject"]) < rows:
        person += 1
        level = draw.gauss(0.0, 12.0)
        for _row in range(draw.randint(3, 12)):
            item = draw.choice(("PRESS", "PRESS", "PULSE", "MOOD"))
            if item == "PRESS":
                upper = int(round(120.0 + level + draw.gauss(0.0, 10.0)))
                lower = upper - draw.randint(1, 4) if tight else int(round(0.3 * upper + draw.gauss(0.0, 3.0))) - 10
                reading_ = f"{upper}/{lower}"
            elif item == "PULSE":
                reading_ = str(int(round(80.0 + level / 2 + draw.gauss(0.0, 8.0))))
            else:
                reading_ = draw.choice(("calm", "restless", "asleep"))
            out["subject"] += [f"S{1000000 + person}"]
            out["item"] += [item]
            out["reading"] += [reading_]
    return out


def _apart(table: "dict[str, list[str]]") -> "dict[str, list[str]]":
    """A stand-in for the description's twin: the persons renamed, each item's readings permuted, and the pairs' second
    parts dealt apart from their first parts (a pairing that keeps neither part's own numbers from moving together)."""
    draw = random.Random(3)
    cells = {name: list(values) for name, values in table.items()}
    cells["subject"] = ["T" + cell[1:] for cell in table["subject"]]
    rows = [row for row in range(len(table["item"])) if table["item"][row] == "PRESS"]
    firsts = [table["reading"][row].split("/")[0] for row in rows]
    seconds = [table["reading"][row].split("/")[1] for row in rows]
    draw.shuffle(firsts)
    draw.shuffle(seconds)
    for row, first, second in zip(rows, firsts, seconds):
        cells["reading"][row] = f"{first}/{second}"
    return cells


def _parts(cells: "dict[str, list[str]]") -> "tuple[list[float], list[float]]":
    rows = [row for row in range(len(cells["item"])) if cells["item"][row] == "PRESS"]
    return ([float(cells["reading"][row].split("/")[0]) for row in rows],
            [float(cells["reading"][row].split("/")[1]) for row in rows])


def _corr(first: "list[float]", second: "list[float]") -> float:
    mean_a = sum(first) / len(first)
    mean_b = sum(second) / len(second)
    top = sum((a - mean_a) * (b - mean_b) for a, b in zip(first, second))
    return top / math.sqrt(sum((a - mean_a) ** 2 for a in first) * sum((b - mean_b) ** 2 for b in second))


def _zoned(table: "dict[str, list[str]]", stand: "dict[str, list[str]]") -> "tuple[dict[str, object], dict[str, list[str]]]":
    zone = inside_keyed.build_zone(table, "subject", (), (), {}, {}, {"reading": "item"})
    assert zone is not None
    cells = {name: list(values) for name, values in stand.items()}
    cells.update(inside_keyed.persons_and_labels(zone, cells, 0, None))
    cells.update(inside_keyed.numbers_and_rules(zone, cells, 0))
    return zone, cells


def test_a_pair_is_joined_again_at_the_records_correlation() -> None:
    """A level of pairs whose twin cells pair their parts apart is joined again: each part's spellings are the twin's own, the first part larger on as many cells as before, the two parts' correlation within 0.03 of the table's and their rank agreement within half the validator's window of the record's; a joining whose agreement would leave that window is not made (mutants: the pairs left as dealt; the agreement not read)."""
    table = _pair_table(6000, 1)
    stand = _apart(table)
    zone, twin = _zoned(table, stand)
    level = [entry for entry in zone["levels"] if entry["level"] == "PRESS"][0]  # type: ignore[union-attr, index]
    assert "reading" in level["pairs"]  # type: ignore[index]
    before = _parts(stand)
    after = _parts(twin)
    assert sorted(after[0]) == sorted(before[0]) and sorted(after[1]) == sorted(before[1])
    assert sum(a > b for a, b in zip(*after)) == sum(a > b for a, b in zip(*before))
    real = _corr(*_parts(table))
    assert real > 0.6 and abs(_corr(*before)) < 0.1
    assert abs(_corr(*after) - real) < 0.03, (real, _corr(*after))
    entry = level["pairs"]["reading"]  # type: ignore[index]
    assert abs(parsing.rank_agreement(*after) - entry["agreement"]) <= parsing.RANK_AGREEMENT_WINDOW / 2
    # ...and a joining whose rank agreement would leave half the validator's window of the record's is not made.
    rows = [row for row in range(len(stand["item"])) if stand["item"][row] == "PRESS"]
    kept = list(stand["reading"])
    inside_keyed._pairs_rejoined(kept, rows, dict(entry, agreement=0.2), 0, "press")
    assert kept == stand["reading"]
    inside_keyed._pairs_rejoined(kept, rows, dict(entry), 0, "press")
    assert kept != stand["reading"]


def test_a_joining_that_moves_which_part_is_larger_is_not_made() -> None:
    """Where the parts stand one to four apart, the first always the larger, a joining at the record's correlation would put the second above the first on some cells: the cells stay as dealt, every one the twin's own (mutant: the count of cells whose first part is the larger not read)."""
    table = _pair_table(6000, 2, tight=True)
    stand = _apart(table)
    rows = [row for row in range(len(stand["item"])) if stand["item"][row] == "PRESS"]
    firsts = sorted(float(stand["reading"][row].split("/")[0]) for row in rows)
    seconds = sorted(float(stand["reading"][row].split("/")[1]) for row in rows)
    for row, first, second in zip(rows, firsts, seconds):
        stand["reading"][row] = f"{int(first)}/{int(second)}"
    _zone, twin = _zoned(table, stand)
    assert sorted(twin["reading"][row] for row in rows) == sorted(stand["reading"][row] for row in rows)
    assert all(a > b for a, b in zip(*_parts(twin)))


def test_a_copy_is_not_written_from_a_source_a_level_top_codes() -> None:
    """A numeric copy whose source a level writes under the age top code, the copy itself uncapped, is not written: the twin keeps the copy's own cells (mutant: the top code not read)."""
    draw = random.Random(9)
    table: "dict[str, list[str]]" = {"subject": [], "item": [], "reading": [], "reading_num": []}
    for person in range(400):
        level = draw.gauss(0.0, 10.0)
        for _row in range(10):
            item = draw.choice(("PULSE", "PULSE", "SUGAR", "SUGAR", "MOOD"))
            if item == "MOOD":
                cell = draw.choice(("calm", "restless", "asleep"))
            else:
                cell = str(int(round((80.0 if item == "PULSE" else 110.0) + level + draw.gauss(0.0, 8.0))))
            table["subject"] += [f"S{1000000 + person}"]
            table["item"] += [item]
            table["reading"] += [cell]
            table["reading_num"] += [cell if inside_keyed.plain_number(cell) is not None else "-1"]
    stand = {name: list(values) for name, values in table.items()}
    stand["subject"] = ["T" + cell[1:] for cell in table["subject"]]
    draw.shuffle(stand["reading_num"])
    free = inside_keyed.build_zone(table, "subject", (), (), {}, {}, {"reading": "item"})
    capped = inside_keyed.build_zone(table, "subject", (), (), {}, {"reading": {"sugar": {"identifier": False, "top": 90}}},
                                     {"reading": "item"})
    assert free is not None and capped is not None and free["copies"] and capped["copies"]
    assert inside_keyed.capped_anywhere(capped, "reading") and not inside_keyed.capped_anywhere(free, "reading")
    cells = {name: list(values) for name, values in stand.items()}
    written = inside_keyed.numbers_and_rules(capped, cells, 0)
    assert "reading_num" not in written
    written = inside_keyed.numbers_and_rules(free, {name: list(values) for name, values in stand.items()}, 0)
    assert "reading_num" in written
