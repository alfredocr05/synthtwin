"""Batch 4t's fix round: the items of the outside review of the merged line (the orchestrator's LANE I4t RULINGS 1).

Each item has its case on the reviewer's own table at the owner's floor (20,000 rows or more; 1,000 people where a
person column stands beside), RED on the merged head 98467814 and green here, a generated case behind it, and a
mutant that turns it red, in the ruling's order:

(1) ITEM 1: a keyed value column's key blocks and pooled block of numbers too large or too small to hold are read by
the check of the made-up spellings against the real cells (`profile.made_up_dry_runs`,
`generation.made_up_spellings_keyed`): an assay of codes past a double's range, one code a person, nested under its
key, got 4,000 of its 4,000 cells back as real codes.
(2) ITEM 2: the reading of a cell with what prints nothing set aside is kept wherever it reads an age or a boundary
the first reading did not (`taxonomy._reads_what_the_first_did_not`), the top code reads such a cell again
(`taxonomy._coded_again`), and the residual publication check reads what prints nothing set aside: `Age 9<U+200B>1
age 110.00000` published nine levels showing 91 to 99, and `Age 1100 mon<U+00AD>ths` was written `90 months`.
(3) ITEM 3: the keyed recount writes each count it measures through the floor, in rows and people
(`validation._key_count_floored`): `4000 rows, 1 of them holding a value` named a value one person holds.
(4) ITEM 4: each key column types one value column (`profile._one_value_a_key`): a copy of the value column beside
the same key overwrote the key's `keyed`, and the loader refused the description the command wrote.
(5) ITEM 5: a table read in groups carries the keyed rows' mask as a rewrite of its columns
(`validation._keyed_rows_blank`): the grouped route described the value column over every row.
(6) ITEM 6: the keyed recount reads a cell absent as the producer does (`validation._read_as_absent`): three `NA`
cells the floor kept out of the published map were recounted as present.
(7) ITEM 7: the role reader asks itself again only through a name (`taxonomy._a_name_before_the_last_word`): `Mother, `
written 512 times raised RecursionError.
(9) ITEM 9, K-HZ-41's remark kinds: a remark of an age of exactly 90, the top code's own form, is no exposure and is
not counted (`value_reader_residual_forms._remarks`). Item 8 (lane ID-ROOM3's repair 3) keeps its own cases in
tests/test_counted_dates_room.py and tests/test_stage3b_counted_codex.py.

Invented tables only; every table case runs the commands a person types, nobody at the keyboard, the floor on.
"""

from __future__ import annotations

import contextlib
import csv
import dataclasses
import io
import json
import pathlib
import random
import re

import pytest

import health_zoo as zoo
from synthtwin import cli, contract, generation, parsing, profile, reading, taxonomy, validation


def _counts(values: "list[str]") -> "dict[str, int]":
    found: "dict[str, int]" = {}
    for value in values:
        found[value] = (found[value] if value in found else 0) + 1
    return found


@contextlib.contextmanager
def _nobody_at_the_keyboard():  # type: ignore[no-untyped-def]
    asked = cli._there_is_somebody_to_ask
    cli._there_is_somebody_to_ask = lambda: False
    try:
        yield
    finally:
        cli._there_is_somebody_to_ask = asked


def _twin_columns(path: pathlib.Path) -> "dict[str, list[str]]":
    with open(path, encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    return {name: [row[place] for row in rows[1:]] for place, name in enumerate(rows[0])}


def _commands(folder: pathlib.Path, stem: str, header: "list[str]", rows: "list[list[str]]",
              given: "tuple[str, ...]" = (), generate: bool = True) -> "dict[str, object]":
    """Profile the table (nobody at the keyboard, the table floor on, ``given`` the declarations typed) and generate
    at seed 0: the description, the source and the twin."""
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / f"{stem}.csv"
    source.write_bytes(zoo.csv_bytes(header, rows))
    described = folder / f"{stem}-profile.json"
    with _nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["profile", f"{source}", "--replace", *given], small_tables_refused=True) == 0
        if generate:
            assert cli.main(["generate", f"{described}", "--replace", "--seed", "0"], small_tables_refused=True) == 0
    seen: "dict[str, object]" = {"description": json.loads(described.read_text(encoding="utf-8")), "source": source,
                                 "described": described}
    if generate:
        seen["twin"] = _twin_columns(folder / f"{stem}-twin.csv")
    return seen


def _block(document: "dict[str, object]", name: str) -> "dict[str, object]":
    return [block for block in document["columns"] if block["name"] == name][0]  # type: ignore[index,union-attr]


# -- (1) ITEM 1: THE KEY BLOCKS OF NUMBERS TOO LARGE TO HOLD ARE READ AGAINST THE REAL CELLS ---------------------------

_KEYS = ("assay_a", "pulse", "temp_c", "glucose_mg", "airway", "pain_score")


def _assay_rows(code: "object" = None, people: int = 1000) -> "tuple[list[str], list[list[str]]]":
    """Codex's long table: 1,000 people, four visits, six keys (24,000 rows); `assay_a` holds the code ``code(p)`` of
    person p (Codex's `str(1 + p % 9) + "e" + str(400 + p // 9)`: one code a person), the other keys ordinary
    measurements and words."""
    spell = code if callable(code) else (lambda p: f"{1 + p % 9}e{400 + p // 9}")
    draw = random.Random(0)
    rows: "list[list[str]]" = []
    for p in range(people):
        person = f"P{100000 + p}"
        for visit in range(4):
            for key in _KEYS:
                if key == "assay_a":
                    value = spell(p)
                elif key == "pulse":
                    value = f"{draw.randint(50, 110)}"
                elif key == "temp_c":
                    value = f"{draw.gauss(36.9, 0.4):.1f}"
                elif key == "glucose_mg":
                    value = f"{max(50, round(draw.gauss(140, 40)))}"
                elif key == "airway":
                    value = draw.choice(("Clear", "Wheeze", "Crackles"))
                else:
                    value = f"{draw.randint(0, 10)}"
                rows += [[person, f"{visit + 1}", key, value]]
    return ["person_id", "visit", "item_key", "item_value"], rows


def _real_codes(rows: "list[list[str]]") -> "dict[str, set[str]]":
    """Each code past a double's range of the value column with the people who hold it."""
    found: "dict[str, set[str]]" = {}
    for row in rows:
        if parsing.classify_number(row[3]) not in (parsing.NUMBER, parsing.NOT_A_NUMBER):
            found.setdefault(row[3], set()).add(row[0])
    return found


def _real_codes_written(twin: "list[str]", real: "dict[str, set[str]]") -> int:
    """The twin cells equal to a real code 1 to 10 people hold, exactly or by merged key."""
    few = {parsing.merged_key(code) for code, people in real.items() if len(people) < 11}
    return sum(1 for cell in twin if parsing.merged_key(cell) in few)


def _writer_inside_the_check(seen: "dict[str, object]") -> int:
    """Every key block and pooled block of numbers too large to hold in the description is written by the writer
    (`_key_block_written`) only in spellings the check reads (`made_up_spellings_keyed`); the blocks so read."""
    typed = contract.checked_description(seen["described"].read_text(encoding="utf-8"))  # type: ignore[union-attr]
    at = [column.name for column in typed.columns].index("item_value")
    column = typed.columns[at]
    spellings, _wider = generation.made_up_spellings_keyed(typed, at)
    assert spellings is not None
    inner = [block for _label, block in column.key_blocks] + ([column.key_pool] if column.key_pool else [])
    read = 0
    for block in inner:
        if isinstance(block.facts, contract.UnrepresentableFacts):
            written = set(generation._key_block_written(typed, column, block, 7)) - {""}
            assert written and written <= set(spellings), (block.name, sorted(written - set(spellings))[:4])
            read += 1
    return read


def test_codex_s_nested_assay_of_codes_writes_no_real_code_at_the_table_floor(tmp_path: pathlib.Path) -> None:
    """Codex's item 1 (HIGH): 24,000 rows, 1,000 people, `assay_a` nested as a key block of numbers too large to hold.
    The block carries NF139 (spelled one letter or figure wider) and the twin writes 0 cells equal to a real code (on
    98467814: 4,000 cells, each code held by one person; on the public tree 653 by its long tail of labels); the
    writer writes there only spellings the check reads."""
    header, rows = _assay_rows()
    seen = _commands(tmp_path, "assays", header, rows, ("--identifier", "person_id"))
    real = _real_codes(rows)
    assert len(real) == 1000 and max(len(people) for people in real.values()) == 1
    assert _real_codes_written(seen["twin"]["item_value"], real) == 0  # type: ignore[index]
    by_key = _block(seen["description"], "item_value")["by_key"]  # type: ignore[arg-type,index]
    blocks = {f"{entry['key']}": entry["block"] for entry in by_key["key_blocks"]}  # type: ignore[index,union-attr]
    assert blocks["assay_a"]["role"] == taxonomy.ROLE_UNREPRESENTABLE
    assert blocks["assay_a"]["detection_evidence"] == generation.SPELLED_WIDER_EVIDENCE
    assert _writer_inside_the_check(seen) == 1


@pytest.mark.parametrize("form", ["negative", "pooled", "small-exponent"])
def test_the_pooled_block_and_other_forms_of_codes_write_no_real_code(tmp_path: pathlib.Path, form: str) -> None:
    """The same class on three more tables at the floor: the assay's codes negative (`-3e411`; 98467814 writes 4,000
    real codes), the assay's codes of another mantissa (`-7.25e612`) beside 50 rare keys of one row of 500 people
    (ten a key) whose codes, one a person, stand in the pooled block (536), and codes of a tiny size (`3e-411`;
    4,000): every block of the role is read, and 0 twin cells equal a real code."""
    if form == "negative":
        header, rows = _assay_rows(lambda p: f"-{1 + p % 9}e{400 + p // 9}")
    elif form == "pooled":
        header, rows = _assay_rows(lambda p: f"-{1 + p % 7}.25e{600 + p // 7}")
        rows += [[f"P{100000 + p}", "5", f"assay_rare_{p % 100}", f"{1 + p // 2 % 9}e{400 + p // 18}"]
                 for p in range(0, 1000, 2)]
    else:
        header, rows = _assay_rows(lambda p: f"{1 + p % 9}e-{400 + p // 9}")
    assert len(rows) >= 24000
    seen = _commands(tmp_path, form, header, rows, ("--identifier", "person_id"))
    assert _real_codes_written(seen["twin"]["item_value"], _real_codes(rows)) == 0  # type: ignore[index]
    by_key = _block(seen["description"], "item_value")["by_key"]  # type: ignore[arg-type,index]
    if form == "pooled":
        assert by_key["pool"]["role"] == taxonomy.ROLE_UNREPRESENTABLE  # type: ignore[index]
    assert _writer_inside_the_check(seen) >= 1


_ROLES = (taxonomy.ROLE_UNREPRESENTABLE, "count", "continuous", "categorical", "empty", taxonomy.ROLE_IDENTIFIER)


def _places_swept(tmp_path: pathlib.Path) -> int:
    """3,000 generated descriptions of one to four columns, each column's block of a drawn role and, half of them,
    typed by a key with one to six key blocks of drawn roles and sometimes a pooled block: the check hands over exactly
    the places whose block, key block or pooled block holds numbers too large to hold (the keyed ones counted)."""
    draw = random.Random(4871)
    source = tmp_path / "names.csv"
    source.write_bytes(zoo.csv_bytes(["c0", "c1", "c2", "c3"], [["1", "2", "3", "4"]]))
    settings = taxonomy.Settings(small_cell_floor=11)
    # ...the table read at the floor the case names (tests/test_stage3_default_floor.py: no test reads at the
    # default beside a floor of its own; batch 4t's last code round, item 2).
    table = reading.read_table(f"{source}", small_cell_floor=settings.small_cell_floor)
    nested = 0
    for _case in range(3000):
        columns: "list[dict[str, object]]" = []
        owed: "list[int]" = []
        for place in range(draw.randint(1, 4)):
            block: "dict[str, object]" = {"name": f"c{place}", "role": draw.choice(_ROLES)}
            coded = block["role"] == taxonomy.ROLE_UNREPRESENTABLE
            if draw.random() < 0.5:
                inner = [{"key": f"k{index}", "block": {"name": f"k{index}", "role": draw.choice(_ROLES)}}
                         for index in range(draw.randint(1, 6))]
                by_key: "dict[str, object]" = {"key": "c9", "key_blocks": inner}
                roles = [entry["block"]["role"] for entry in inner]  # type: ignore[index]
                if draw.random() < 0.4:
                    by_key["pool"] = {"name": f"c{place}", "role": draw.choice(_ROLES)}
                    roles += [by_key["pool"]["role"]]  # type: ignore[index]
                block["by_key"] = by_key
                if taxonomy.ROLE_UNREPRESENTABLE in roles:
                    nested += 1
                    coded = True
            if coded:
                owed += [place]
            columns += [block]
        runs = profile.made_up_dry_runs(table, {"columns": columns, "settings": {}}, settings)
        handed = sorted(place for _text, places in runs for place in places)
        assert handed == owed, (columns, handed)
    return nested


def test_every_generated_place_of_a_block_of_codes_is_handed_to_the_check(tmp_path: pathlib.Path) -> None:
    """The class behind item 1, generated (`_places_swept`): every place whose block, key block or pooled block holds
    numbers too large to hold, and no other, over 3,000 descriptions, more than 800 of them only through a key."""
    assert _places_swept(tmp_path) > 800


def test_item_1_is_red_on_the_mutant_that_reads_the_top_level_blocks_only(tmp_path: pathlib.Path,
                                                                         monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the check reads the top-level blocks only (`_a_key_block_unrepresentable` False, the merged head's
    reading): Codex's table writes real codes again, every one held by one person, and the generated places through a
    key are missed."""
    monkeypatch.setattr(profile, "_a_key_block_unrepresentable", lambda block: False)
    with pytest.raises(AssertionError):
        _places_swept(tmp_path)
    header, rows = _assay_rows()
    seen = _commands(tmp_path, "assays", header, rows, ("--identifier", "person_id"))
    assert _real_codes_written(seen["twin"]["item_value"], _real_codes(rows)) >= 3000  # type: ignore[index]


# -- (2) ITEM 2: THE READING WITH WHAT PRINTS NOTHING SET ASIDE IS KEPT WHERE IT READS MORE ----------------------------

_SILENT = ("​", "‌", "‍", "⁠", "﻿", "­")
_UNIT_MARKS = {"years": 90, "months": 1080, "weeks": 4695, "days": 32871}


def _plain(text: str) -> str:
    """A text with the characters that print nothing of `_SILENT` set aside (the test's own list, not the product's)."""
    for character in _SILENT:
        text = text.replace(character, "")
    return text


def _ages_past_90(text: str) -> "list[int]":
    """The numbers of two or three figures from 91 to 125 a text shows once what prints nothing is set aside."""
    found: "list[int]" = []
    for word in _plain(text).replace(".", " . ").split():
        if word.isdigit() and 2 <= len(word) <= 3 and 91 <= int(word) <= 125:
            found += [int(word)]
    return found


def _codex_s_ages() -> "list[str]":
    """Codex's column: 20,000 different cells `Age 9<U+200B>d age 110.xxxxx`, d from 1 to 9."""
    return [f"Age 9​{1 + index % 9} age {110 + index / 100000:.5f}" for index in range(20000)]


def test_codex_s_ages_split_by_what_prints_nothing_publish_no_age_past_90(tmp_path: pathlib.Path) -> None:
    """Codex's item 2 (HIGH), its first table, at the command's publication boundary: a column named `age` of 20,000
    different cells `Age 9<U+200B>1 age 110.00000` to `... 9<U+200B>9 ...`. No published level and no twin cell
    shows an age past 90 once what prints nothing is set aside (on 98467814 nine levels show 91 to 99 beside
    `90.00000`, on 2,223 rows twice and 2,222 rows seven times; the public tree publishes it as free text)."""
    seen = _commands(tmp_path, "ages", ["age"], [[cell] for cell in _codex_s_ages()])
    block = _block(seen["description"], "age")  # type: ignore[arg-type]
    shown = [f"{level['label']}" for level in block.get("levels", [])]  # type: ignore[union-attr]
    assert [label for label in shown if _ages_past_90(label)] == []
    assert sum(1 for cell in seen["twin"]["age"] if _ages_past_90(cell)) == 0  # type: ignore[index]


def test_codex_s_months_with_a_soft_hyphen_are_written_at_1080_months(tmp_path: pathlib.Path) -> None:
    """Codex's item 2, its second table: 10,000 cells `Age 1100 mon<U+00AD>ths` beside 10,000 `Age 1100 months`; both
    are 1,100 months (91.7 years) and both are written at the boundary in months, `Age 1080 ...`, in the
    description and the twin (98467814 wrote the soft-hyphen ones `90 months`, a group from seven and a half years;
    the public tree published them as written, an age past 89)."""
    cells = ["Age 1100 mon­ths"] * 10000 + ["Age 1100 months"] * 10000
    seen = _commands(tmp_path, "months", ["age"], [[cell] for cell in cells])
    block = _block(seen["description"], "age")  # type: ignore[arg-type]
    levels: "dict[str, int]" = {}
    for level in block["levels"]:  # type: ignore[index,union-attr]
        label = _plain(f"{level['label']}").lower()
        levels[label] = levels.get(label, 0) + int(level["count"])
    assert levels == {"age 1080 months": 20000}, levels
    assert {_plain(cell) for cell in seen["twin"]["age"]} == {"Age 1080 months"}  # type: ignore[index]


def _cut(text: str, draw: random.Random) -> str:
    """The text with one character that prints nothing at a drawn place strictly inside it."""
    at = draw.randint(1, len(text) - 1)
    return text[:at] + draw.choice(_SILENT) + text[at:]


def _generated_phrases(draw: random.Random, count: int) -> "list[tuple[str, str]]":
    """Age phrases with one character that prints nothing inside a figure beside a larger second age (`Age 9<cut>5 age
    110.5`), inside the unit word of one age (`Age 1100 mon<cut>ths`, months, weeks and days, below and at or past
    their unit's mark), inside the age word, or in two places each reading reads apart (`Age 9<cut>5 age
    104<cut>M`), each with the top code's expected writing read with what prints
    nothing set aside (the test's own arithmetic: every age of 90 years or more written as its unit's mark, its
    decimals written as noughts)."""
    found: "list[tuple[str, str]]" = []
    for _case in range(count):
        form = draw.randint(0, 3)
        if form == 0:
            first = draw.randint(10, 124)
            second = draw.randint(max(first, 91), 124)
            decimals = draw.choice(("", ".0", ".5", ".00000"))
            cell = f"Age {_cut(f'{first}', draw)} age {second}{decimals}"
            kept = first if first < 90 else 90
            found += [(cell, f"Age {kept} age 90{decimals[:1]}{'0' * len(decimals[1:])}")]
        elif form == 1:
            unit = draw.choice(("months", "weeks", "days"))
            mark = _UNIT_MARKS[unit]
            number = draw.choice((draw.randint(mark // 2, mark - 1), draw.randint(mark, mark * 125 // 90)))
            cell = f"Age {number} {_cut(unit, draw)}"
            found += [(cell, f"Age {number if number < mark else mark} {unit}")]
        elif form == 2:
            number = draw.randint(91, 125)
            found += [(f"{_cut('Age', draw)} {number} age {number + draw.randint(0, 125 - number)}", "Age 90 age 90")]
        else:
            # ...each reading reading an age the other does not: 95 across the cut, 104 years before a trailing M
            # that the reading with what prints nothing set aside reads as months.
            first, second = draw.randint(90, 124), draw.randint(90, 124)
            found += [(f"Age {_cut(f'{first}', draw)} age {second}{draw.choice(_SILENT)}M", "Age 90 age 90M")]
    return found


def _phrases_missed(phrases: "list[tuple[str, str]]") -> "list[tuple[str, str, str]]":
    """Each generated phrase whose top-coded writing (`taxonomy.top_coded_cells`, one column of each form's cells)
    reads otherwise than expected once what prints nothing is set aside."""
    cells = [cell for cell, _expected in phrases]
    coded = taxonomy.top_coded_cells(cells)
    return [(cell, written, expected) for (cell, expected), written in zip(phrases, coded)
            if _plain(written) != expected]


def test_every_generated_age_phrase_is_top_coded_on_its_reading_with_what_prints_nothing_set_aside() -> None:
    """The class behind item 2, generated: 6,000 age phrases with one character that prints nothing inside a figure
    beside a larger age, inside a unit word or inside the age word; each is written by the top code as the test's own
    arithmetic says (every age of 90 years or more as its unit's mark: 90, 1,080 months, 4,695 weeks, 32,871 days)."""
    phrases = _generated_phrases(random.Random(4872), 6000)
    missed = _phrases_missed(phrases)
    assert missed == [], (len(missed), [(_plain(cell), _plain(written), expected) for cell, written, expected in missed[:6]])


def test_the_residual_check_reads_an_age_left_across_what_prints_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    """The residual publication check reads what prints nothing set aside: a remark column whose top-coded levels
    still show `age 9<U+200B>1 years old` to `... 9<U+200B>9 ...` (a top code that writes nothing, for the case) is
    read as holding an age past 90, which holds the column whole (98467814's plain reading read `9` and `1`)."""
    cells = [f"Pt seen, age 9\u200b{1 + index % 9} years old" for index in range(2000)]
    monkeypatch.setattr(taxonomy, "top_coded_cells", lambda cells, *given, **named: list(cells))
    assert taxonomy._ages_left_after_the_top_code(cells, frozenset(), 11)
    assert not taxonomy._ages_left_after_the_top_code([_plain(cell).replace("age 9", "age ") for cell in cells],
                                                      frozenset(), 11)


def test_item_2_is_red_on_the_mutant_that_discards_the_alternate_reading_on_its_largest_number(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the alternate reading discarded wherever its largest number matches the first reading's (the merged
    head's rule): the generated phrases of a unit word cut are written at the boundary in years again (`90 months`);
    with the top code's second pass gone too, the ages split by what prints nothing show past 90 again (each of the
    two closes Codex's first table alone)."""
    phrases = _generated_phrases(random.Random(4872), 1500)
    monkeypatch.setattr(taxonomy, "_reads_what_the_first_did_not", lambda ages, places, first: False)
    missed = _phrases_missed(phrases)
    assert len(missed) > 100, len(missed)
    assert any(_plain(written).endswith((" 90 months", " 90 weeks", " 90 days")) for _cell, written, _e in missed)
    monkeypatch.setattr(taxonomy, "_coded_again", lambda coded, *given: coded)
    assert any(_ages_past_90(written) for _cell, written, _expected in _phrases_missed(phrases))


# -- (3) ITEM 3: THE KEYED RECOUNT PRINTS NO MEASURED COUNT UNDER THE FLOOR --------------------------------------------

def _keyed_lab_rows() -> "tuple[list[str], list[list[str]]]":
    """Codex's long table of ordinary measurements (its assay a sodium), and one key more, `pump_rate`, on four rows of
    each person whose values only five people hold, so its block is counted absent (24,000 + 4,000 rows)."""
    header, rows = _assay_rows(lambda p: f"{130 + p % 20}")
    for p in range(1000):
        rows += [[f"P{100000 + p}", f"{visit + 1}", "pump_rate", f"{40 + visit}" if p < 5 else ""] for visit in range(4)]
    return header, rows


@pytest.fixture(scope="module")
def keyed_lab(tmp_path_factory: pytest.TempPathFactory) -> "dict[str, object]":
    folder = tmp_path_factory.mktemp("keyed-lab")
    header, rows = _keyed_lab_rows()
    seen = _commands(folder, "lab", header, rows, ("--identifier", "person_id"), generate=False)
    seen["header"], seen["rows"], seen["folder"] = header, rows, folder
    seen["table"] = reading.read_table(f"{seen['source']}")
    seen["typed"] = contract.checked_description(seen["described"].read_text(encoding="utf-8"))  # type: ignore[union-attr]
    return seen


def _measured(seen: "dict[str, object]", stem: str, rows: "list[list[str]]") -> "list[object]":
    """The keyed recount's checks of a checked file holding ``rows``, against the lab's own description."""
    path = seen["folder"] / f"{stem}.csv"  # type: ignore[operator]
    path.write_bytes(zoo.csv_bytes(seen["header"], rows))  # type: ignore[arg-type]
    typed = contract.checked_description(seen["described"].read_text(encoding="utf-8"))  # type: ignore[union-attr]
    return [check for check in validation.measure(typed, f"{path}").checks if check.fact == "label.by_key"]


def _numbers_under_the_floor(text: str) -> "list[int]":
    return [int(word) for word in text.replace(",", " ").split() if word.isdigit() and 1 <= int(word) <= 10]


def test_codex_s_keyed_recount_prints_no_count_under_the_floor_at_the_command(keyed_lab: "dict[str, object]") -> None:
    """Codex's item 3 (HIGH): the lab's own description (4,000 pulse values of 1,000 people) checked against a file
    with every pulse value blank but one, by the command a person types: the quality files print no measured count
    of 1 to 10 (98467814 wrote `4000 rows, 1 of them holding a value`) and the check is still MISSED."""
    rows = [row if row[2] != "pulse" else row[:3] + [""] for row in keyed_lab["rows"]]  # type: ignore[union-attr]
    first = [place for place, row in enumerate(keyed_lab["rows"]) if row[2] == "pulse"][0]  # type: ignore[arg-type,index]
    rows[first] = keyed_lab["rows"][first]  # type: ignore[index]
    folder = keyed_lab["folder"] / "one-pulse"  # type: ignore[operator]
    (folder / "q").mkdir(parents=True)
    measured = folder / "measured.csv"
    measured.write_bytes(zoo.csv_bytes(keyed_lab["header"], rows))  # type: ignore[arg-type]
    with _nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["validate", f"{keyed_lab['described']}", "--twin", f"{measured}", "--out-dir",
                         f"{folder / 'q'}", "--replace"]) == 3
    texts = "".join(path.read_text(encoding="utf-8") for path in sorted((folder / "q").iterdir()) if path.is_file())
    assert "holding a value" in texts
    assert re.findall(r"(?<![0-9])(?:[1-9]|10) (?:rows|of them holding a value)", texts) == []
    assert "fewer than 11 of them holding a value" in texts
    pulse = [check for check in _measured(keyed_lab, "one-pulse-measured", rows) if check.subcheck == "by_key.pulse"]
    assert [check.verdict for check in pulse] == [validation.MISSED]
    assert _numbers_under_the_floor(pulse[0].achieved) == []


def test_the_withholding_branch_and_a_count_of_few_people_print_no_count_under_the_floor(
        keyed_lab: "dict[str, object]") -> None:
    """The withholding branch (`pump_rate`, counted absent) checked against a file holding 3 of its rows prints
    `fewer than 11 rows` (98467814: `3 rows`); fifteen pulse values of one person print as values of fewer than 11
    people, never `15` (98467814: `15 of them holding a value`)."""
    rows = [row for row in keyed_lab["rows"] if row[2] != "pump_rate"] + [  # type: ignore[union-attr]
        row for row in keyed_lab["rows"] if row[2] == "pump_rate"][:3]  # type: ignore[union-attr]
    pump = [check for check in _measured(keyed_lab, "few-pump", rows) if check.subcheck == "by_key.pump_rate"]
    assert [check.verdict for check in pump] == [validation.MISSED]
    assert pump[0].achieved == "fewer than 11 rows", pump[0].achieved
    one = "P100000"
    rows = [row if row[2] != "pulse" or row[0] == one else row[:3] + [""] for row in keyed_lab["rows"]]  # type: ignore[union-attr]
    rows += [[one, f"{visit + 5}", "pulse", f"{70 + visit}"] for visit in range(11)]
    pulse = [check for check in _measured(keyed_lab, "one-person", rows) if check.subcheck == "by_key.pulse"]
    assert [check.verdict for check in pulse] == [validation.MISSED]
    assert "15" not in pulse[0].achieved and "values among them of fewer than 11 people" in pulse[0].achieved


def _recounts_shown(keyed_lab: "dict[str, object]", draw: random.Random) -> "tuple[int, int]":
    """One generated checked file, in memory: the lab's rows with each key's values kept for a drawn number of people
    (none, one to ten, or eleven or more), some keys' rows cut to a drawn number, and some rows moved onto one person;
    every measured count the keyed recount prints (`_key_block_checks`) is 0 or of the floor's rows and the floor's
    people or more, counted by the test itself. The counts printed, and those owed a floor."""
    rows = [list(row) for row in keyed_lab["rows"]]  # type: ignore[union-attr]
    for key in ("pulse", "temp_c", "airway", "pump_rate"):
        kept = draw.choice((0, draw.randint(1, 10), draw.randint(11, 1000)))
        places = [place for place, row in enumerate(rows) if row[2] == key]
        for place in places:
            if int(rows[place][0][1:]) - 100000 >= kept:
                rows[place][3] = ""
        if draw.random() < 0.4:
            cut = set(places[draw.choice((draw.randint(1, 10), draw.randint(11, 3000))):])
            rows = [row for place, row in enumerate(rows) if place not in cut]
        if draw.random() < 0.3:
            for row in rows:
                if row[2] == key and row[3]:
                    row[0] = "P100000"
    table = keyed_lab["table"]
    columns = [[row[place] for row in rows] for place in range(4)]
    table = dataclasses.replace(table, columns=columns, n_rows=len(rows))  # type: ignore[type-var]
    printed, owed = 0, 0
    for check in validation._key_block_checks(keyed_lab["typed"], table):  # type: ignore[arg-type]
        key = check.subcheck[len("by_key."):]
        held = [row for row in rows if row[2] == key]
        filled = [row for row in held if row[3]]
        for words, of in (("rows", held), ("of them holding a value", filled)):
            if f" {words}" not in check.achieved:
                continue
            spoken = check.achieved.split(f" {words}")[0].split(", ")[-1]
            people = len({row[0] for row in of})
            if 1 <= len(of) < 11 or 1 <= people < 11:
                owed += 1
                assert not spoken.isdigit(), (check.achieved, len(of), people)
            elif spoken.isdigit():
                printed += 1
    return printed, owed


def test_every_generated_measured_count_goes_through_the_floor_in_rows_and_people(
        keyed_lab: "dict[str, object]") -> None:
    """The class behind item 3, generated: 120 checked files of the lab's keys (values kept for none, one to ten or
    more people, rows cut, rows moved onto one person); no measured count the keyed recount prints is held by 1 to
    10 rows or people, in both branches, and counts of the floor's rows and people still print."""
    draw = random.Random(4873)
    printed, owed = 0, 0
    for _case in range(120):
        shown, under = _recounts_shown(keyed_lab, draw)
        printed, owed = printed + shown, owed + under
    assert owed > 100 and printed > 50, (owed, printed)


def test_item_3_is_red_on_the_mutant_that_prints_the_measured_count(keyed_lab: "dict[str, object]",
                                                                    monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the measured count written out whatever it is (the merged head's line): one pulse value prints as 1."""
    monkeypatch.setattr(validation, "_key_count_shown", lambda count, floor, people, what: f"{count} {what}")
    rows = [row if row[2] != "pulse" else row[:3] + [""] for row in keyed_lab["rows"]]  # type: ignore[union-attr]
    first = [place for place, row in enumerate(keyed_lab["rows"]) if row[2] == "pulse"][0]  # type: ignore[arg-type,index]
    rows[first] = keyed_lab["rows"][first]  # type: ignore[index]
    pulse = [check for check in _measured(keyed_lab, "mutant", rows) if check.subcheck == "by_key.pulse"]
    assert _numbers_under_the_floor(pulse[0].achieved) == [1]


# -- (4) ITEM 4: ONE VALUE COLUMN A KEY COLUMN, SO THE DESCRIPTION LOADS ------------------------------------------------

def _two_values(form: str) -> "tuple[list[str], list[list[str]]]":
    """Codex's six-key long table of ordinary measurements (24,000 rows, 1,000 people) with a second value column:
    `secondary_value` a copy of `item_value` (Codex's), its numbers doubled and its words in capitals (`scaled`), or two
    copies (`three`)."""
    header, rows = _assay_rows(lambda p: f"{130 + p % 20}")

    def scaled(value: str) -> str:
        return f"{float(value) * 2:.1f}" if value[:1].isdigit() else value.upper()

    if form == "copy":
        return header + ["secondary_value"], [row + [row[3]] for row in rows]
    if form == "scaled":
        return header + ["secondary_value"], [row + [scaled(row[3])] for row in rows]
    return header + ["secondary_value", "third_value"], [row + [row[3], row[3]] for row in rows]


def _scalar_and_loading(seen: "dict[str, object]") -> "dict[str, str]":
    """The description loads strictly, and each key column's `keyed` names exactly the value column whose `by_key`
    names it: the pairs, value column to key column."""
    contract.checked_description(seen["described"].read_text(encoding="utf-8"))  # type: ignore[union-attr]
    blocks = {f"{block['name']}": block for block in seen["description"]["columns"]}  # type: ignore[index]
    pairs = {name: f"{block['by_key']['key']}" for name, block in blocks.items() if "by_key" in block}
    for name, block in blocks.items():
        if "keyed" in block:
            assert pairs.get(f"{block['keyed']}") == name, (name, block["keyed"], pairs)
    assert len(set(pairs.values())) == len(pairs), pairs
    return pairs


def test_codex_s_two_value_columns_on_one_key_write_a_description_that_loads(tmp_path: pathlib.Path) -> None:
    """Codex's item 4 (HIGH): the six-key table with `secondary_value` a copy of `item_value`, by the commands; the
    key column types the first value column only, the second is described as an ordinary column, the description
    loads and generates (on 98467814 `item_key.keyed` named `secondary_value`, the loader refused `item_value` under
    KV1 and `generate` exited 1 telling the person the file had been changed)."""
    header, rows = _two_values("copy")
    seen = _commands(tmp_path, "two", header, rows, ("--identifier", "person_id"))
    assert _scalar_and_loading(seen) == {"item_value": "item_key"}
    assert "by_key" not in _block(seen["description"], "secondary_value")  # type: ignore[arg-type]


@pytest.mark.parametrize("form", ["scaled", "three"])
def test_more_value_columns_beside_one_key_write_descriptions_that_load(tmp_path: pathlib.Path, form: str) -> None:
    """The same class on two more tables at the floor: a second value column of doubled numbers and capital words, and
    two copies of the value column: one value column a key column, every description loads and generates."""
    header, rows = _two_values(form)
    seen = _commands(tmp_path, form, header, rows, ("--identifier", "person_id"))
    assert _scalar_and_loading(seen) == {"item_value": "item_key"}


def test_every_generated_list_of_pairs_keeps_one_value_column_a_key() -> None:
    """The class behind item 4, generated: 5,000 lists of pairs read (one to eight, over one to four key columns, in the
    table's order); the selection keeps each key column's first pair, in order, and every key column once."""
    draw = random.Random(4875)
    shared = 0
    for _case in range(5000):
        pairs = [profile.KeyedPair(f"key_{draw.randint(0, 3)}", f"value_{index}", (), ())  # type: ignore[arg-type]
                 for index in range(draw.randint(1, 8))]
        kept = profile._one_value_a_key(pairs)
        keys = [pair.key for pair in pairs]
        assert [pair.key for pair in kept] == [key for place, key in enumerate(keys) if key not in keys[:place]]
        assert all(pair in pairs for pair in kept) and kept == sorted(kept, key=pairs.index)
        shared += len(kept) < len(pairs)
    assert shared > 2000, shared


def test_item_4_is_red_on_the_mutant_that_keys_every_pair(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: every pair read is kept (the merged head's selection): Codex's table writes a description its own
    loader refuses, so `generate` fails."""
    monkeypatch.setattr(profile, "_one_value_a_key", lambda pairs: pairs)
    header, rows = _two_values("copy")
    with pytest.raises(AssertionError):
        _commands(tmp_path, "two", header, rows, ("--identifier", "person_id"))


# -- (5) ITEM 5: THE KEYED ROWS' MASK READS THROUGH A TABLE READ IN GROUPS ---------------------------------------------

def _checks_by_route(seen: "dict[str, object]", path: "pathlib.Path", monkeypatch: pytest.MonkeyPatch,
                     ) -> "dict[str, list[tuple[str, str, str, str, str]]]":
    """Every check of the checked file against the lab's description, read whole and read in groups (the budget of
    a group lowered to one byte, as the reader's own tests lower it), each as (column, fact, subcheck, verdict,
    measured)."""
    found: "dict[str, list[tuple[str, str, str, str, str]]]" = {}
    for route, budget in (("whole", reading.GROUP_BYTES), ("grouped", 1)):
        monkeypatch.setattr(reading, "GROUP_BYTES", budget)
        outcome = validation.measure(seen["typed"], f"{path}")  # type: ignore[arg-type]
        found[route] = [(check.column, check.fact, check.subcheck, check.verdict, check.achieved)
                        for check in outcome.checks]
    return found


def test_codex_s_keyed_table_validates_alike_read_whole_and_in_groups(keyed_lab: "dict[str, object]",
                                                                      monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 5 (HIGH): the lab's real table checked against its own description, read whole and read in groups:
    the value column is read blank on its keyed rows on both routes (`empty`, 0 present) and every check is the same,
    the key recount read on the cells as written (on 98467814 the grouped route described it as labels, 24,000
    present, and missed the role, the presence and the counts)."""
    found = _checks_by_route(keyed_lab, keyed_lab["source"], monkeypatch)  # type: ignore[arg-type]
    assert found["grouped"] == found["whole"]
    value = [check for check in found["grouped"] if check[0] == "item_value"]
    assert [check for check in value if check[3] == validation.MISSED] == []
    assert ("item_value", "universal.n_present", "presence.n_present", validation.HELD, "0") in value
    recount = [check for check in found["grouped"] if check[1] == "label.by_key"]
    assert recount and all(check[3] == validation.HELD for check in recount)


def _generated_keyed_file(draw: random.Random, path: "pathlib.Path") -> None:
    """A small checked file of the lab's four columns (a test device): rows of the lab's keys, of rare keys, of no key
    (blank or an absent spelling), each value a number, a word, blank or an absent spelling."""
    keys = ("pulse", "temp_c", "airway", "assay_a", "pump_rate", "rare_one", "", "NA", "Pulse")
    rows = []
    for row in range(draw.randint(40, 160)):
        value = draw.choice(("72", "36.8", "Clear", "", "NA", "n/a", "9"))
        rows += [[f"P{100000 + draw.randint(0, 30)}", f"{1 + row % 4}", draw.choice(keys), value]]
    path.write_bytes(zoo.csv_bytes(["person_id", "visit", "item_key", "item_value"], rows))


def test_every_generated_checked_file_is_masked_alike_read_whole_and_in_groups(
        keyed_lab: "dict[str, object]", tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The class behind item 5, generated: 300 small checked files of the lab's columns; read whole and read in groups,
    the value column as the mask leaves it (`_keyed_rows_blank`, then `reading.column_values`) is the same cell for
    cell, and the key recount over the table as handed in is the same check for check."""
    draw = random.Random(4876)
    masked = 0
    for index in range(300):
        path = tmp_path / f"c{index}.csv"
        _generated_keyed_file(draw, path)
        seen: "dict[str, list[str] | list[object]]" = {}
        for route, budget in (("whole", reading.GROUP_BYTES), ("grouped", 1)):
            monkeypatch.setattr(reading, "GROUP_BYTES", budget)
            table = reading.read_table(f"{path}", in_groups=route == "grouped")
            assert (table.source is not None) == (route == "grouped")
            blanked = validation._keyed_rows_blank(table, keyed_lab["typed"])  # type: ignore[arg-type]
            seen[route] = reading.column_values(blanked, 3)
            seen[route + "-recount"] = [(c.subcheck, c.verdict, c.achieved)
                                        for c in validation._key_block_checks(keyed_lab["typed"], table)]  # type: ignore[arg-type]
        assert seen["grouped"] == seen["whole"], index
        assert seen["grouped-recount"] == seen["whole-recount"], index
        masked += sum(1 for cell in seen["whole"] if cell == "")  # type: ignore[union-attr]
    assert masked > 3000, masked


def test_item_5_is_red_on_the_mutant_that_drops_the_mask_in_groups(keyed_lab: "dict[str, object]",
                                                                    monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: a table read in groups returned unmasked (the merged head's line): the grouped route misses again."""
    real = validation._keyed_rows_blank
    monkeypatch.setattr(validation, "_keyed_rows_blank",
                        lambda table, description: table if table.source is not None else real(table, description))
    found = _checks_by_route(keyed_lab, keyed_lab["source"], monkeypatch)  # type: ignore[arg-type]
    assert found["grouped"] != found["whole"]
    assert any(check[0] == "item_value" and check[3] == validation.MISSED for check in found["grouped"])


# -- (6) ITEM 6: THE KEYED RECOUNT READS ABSENCE AS THE PRODUCER DOES ---------------------------------------------------

_NO_VALUE = ("NA", "n/a", "N/A", "null", "NULL", "-", ".", "?", "none", "nan")


def _with_three_absent(rows: "list[list[str]]", key: str) -> "list[list[str]]":
    """The rows with one value of the key for each of three people written `NA` (Codex's three)."""
    written = [list(row) for row in rows]
    done = 0
    for row in written:
        if row[2] == key and row[1] == "1" and done < 3 and (int(row[0][1:]) - 100000) % 300 == 0:
            row[3] = "NA"
            done += 1
    assert done == 3
    return written


def test_codex_s_three_rare_absent_spellings_are_recounted_absent(tmp_path: pathlib.Path) -> None:
    """Codex's item 6 (MEDIUM): three pulse values of three people written `NA` in the lab's 24,000 rows. The pulse
    block publishes 3,997 present cells, three missing and no absent spelling (the floor keeps `NA` out); the
    unchanged table checked against it recounts 3,997 and the check is HELD (98467814 recounted 4,000 and MISSED)."""
    header, rows = _assay_rows(lambda p: f"{130 + p % 20}")
    rows = _with_three_absent(rows, "pulse")
    seen = _commands(tmp_path, "three", header, rows, ("--identifier", "person_id"), generate=False)
    by_key = _block(seen["description"], "item_value")["by_key"]  # type: ignore[arg-type,index]
    pulse = [entry["block"] for entry in by_key["key_blocks"] if entry["key"] == "pulse"][0]  # type: ignore[index,union-attr]
    assert (pulse["n_present"], pulse["n_missing"], pulse["missing_by_source"]) == (3997, 3, {})
    typed = contract.checked_description(seen["described"].read_text(encoding="utf-8"))  # type: ignore[union-attr]
    checks = [check for check in validation.measure(typed, f"{seen['source']}").checks if check.fact == "label.by_key"]
    assert [check.verdict for check in checks if check.subcheck == "by_key.pulse"] == [validation.HELD]
    assert [check for check in checks if check.verdict == validation.MISSED] == []


def test_the_pooled_block_recounts_its_rare_absent_spellings_absent(tmp_path: pathlib.Path) -> None:
    """The pooled branch: Codex's table with 50 rare keys of ten people each pooled, three of the pool's values
    written `n/a`; the unchanged table checked against its description recounts the pool as published, HELD."""
    header, rows = _assay_rows(lambda p: f"{130 + p % 20}")
    rows += [[f"P{100000 + p}", "5", f"rare_check_{p % 100}", "n/a" if p in (0, 200, 400) else f"{p % 7}"]
             for p in range(0, 1000, 2)]
    seen = _commands(tmp_path, "pool", header, rows, ("--identifier", "person_id"), generate=False)
    by_key = _block(seen["description"], "item_value")["by_key"]  # type: ignore[arg-type,index]
    assert "pool" in by_key  # type: ignore[operator]
    typed = contract.checked_description(seen["described"].read_text(encoding="utf-8"))  # type: ignore[union-attr]
    checks = [check for check in validation.measure(typed, f"{seen['source']}").checks if check.fact == "label.by_key"]
    assert [check.verdict for check in checks if check.subcheck == "by_key.pool"] == [validation.HELD]
    assert [check for check in checks if check.verdict == validation.MISSED] == []


def test_every_generated_rare_absent_spelling_is_recounted_absent(keyed_lab: "dict[str, object]") -> None:
    """The class behind item 6, generated: 150 checked files of the lab's rows, in memory, each with one to ten cells
    of drawn keys written in one of the documented spellings of no value (`NA`, `null`, `-`, `?`, ...); the keyed
    recount counts each such cell absent, so a key's measured present cells are its own published 4,000 less them
    (the test's own count)."""
    draw = random.Random(4877)
    keys = ("pulse", "temp_c", "glucose_mg", "airway", "pain_score")
    read = 0
    for _case in range(150):
        rows = [list(row) for row in keyed_lab["rows"]]  # type: ignore[union-attr]
        written: "dict[str, int]" = {}
        for key in draw.sample(keys, draw.randint(1, 3)):
            places = [place for place, row in enumerate(rows) if row[2] == key]
            count = draw.randint(1, 10)
            for place in draw.sample(places, count):
                rows[place][3] = draw.choice(_NO_VALUE)
            written[key] = count
        table = dataclasses.replace(keyed_lab["table"], columns=[[row[place] for row in rows] for place in range(4)])  # type: ignore[type-var]
        for check in validation._key_block_checks(keyed_lab["typed"], table):  # type: ignore[arg-type]
            key = check.subcheck[len("by_key."):]
            if key not in written:
                assert check.verdict == validation.HELD, check
                continue
            assert check.verdict == validation.MISSED, check
            assert check.achieved == f"4000 rows, {4000 - written[key]} of them holding a value", check.achieved
            read += 1
    assert read > 250, read


def test_item_6_is_red_on_the_mutant_that_reads_the_published_spellings_only(keyed_lab: "dict[str, object]",
                                                                             monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the recount reads absence from the published spellings alone (the merged head's): three `NA` cells are
    recounted present."""
    monkeypatch.setattr(validation, "_read_as_absent", lambda values, settings: frozenset())
    rows = _with_three_absent(keyed_lab["rows"], "temp_c")  # type: ignore[arg-type]
    table = dataclasses.replace(keyed_lab["table"], columns=[[row[place] for row in rows] for place in range(4)])  # type: ignore[type-var]
    temp = [check for check in validation._key_block_checks(keyed_lab["typed"], table)  # type: ignore[arg-type]
            if check.subcheck == "by_key.temp_c"]
    assert [check.verdict for check in temp] == [validation.HELD]


# -- (7) ITEM 7: THE ROLE READER ASKS ITSELF AGAIN ONLY THROUGH A NAME ----------------------------------------------------

def _role_test_calls(text: str, monkeypatch: pytest.MonkeyPatch) -> "tuple[bool, int]":
    """The role reader's answer on one value and how many times it is asked (`taxonomy._a_role_or_a_service`)."""
    calls = [0]
    real = taxonomy._a_role_or_a_service

    def counted(value: str) -> bool:
        calls[0] += 1
        return real(value)

    monkeypatch.setattr(taxonomy, "_a_role_or_a_service", counted)
    answer = taxonomy._a_role_or_a_service(text)
    monkeypatch.setattr(taxonomy, "_a_role_or_a_service", real)
    return answer, calls[0]


def test_codex_s_repeated_relation_is_a_role_read_in_a_bounded_number_of_asks(monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 7 (MEDIUM), measured at 128, 256, 512 and 4,096 repetitions of `Mother, ` before `Mother`: a role,
    each read with at most two asks of the role reader whatever the length (98467814 asked it once a word: RecursionError
    from 512 repetitions, 0.03 and 0.12 CPU seconds at 128 and 256)."""
    for count in (128, 256, 512, 4096):
        answer, asks = _role_test_calls("Mother, " * count + "Mother", monkeypatch)
        assert answer is True and asks <= 2, (count, answer, asks)


def test_codex_s_column_of_a_repeated_relation_is_read_by_the_names_hold_at_the_floor() -> None:
    """Codex's 20,000-row `emergency_contact` column of `Mother, ` written 512 times before `Mother`, read by the persons'
    names hold the command asks of it (`taxonomy.persons_names_hold`): no hold, as at 128 repetitions (on 98467814 the
    hold raised RecursionError and the command refused the table)."""
    cells = ["Mother, " * 512 + "Mother"] * 20000
    shorter = ["Mother, " * 128 + "Mother"] * 20000
    assert taxonomy.persons_names_hold("emergency_contact", "constant", cells, frozenset()) == taxonomy.persons_names_hold(
        "emergency_contact", "constant", shorter, frozenset()) == ""


_RELATIONS_AND_ROLES = ("Mother", "Daughter", "Spouse", "Nurse", "Self", "Charge Nurse", "Day Shift", "CRNA", "Jr.", "MD")
_GENERATED_NAMES = ("Okafor", "Bopar", "Cedar, Aaa", "Aaa Cedar", "Ann Lee", "VAN DYKE", "Minh Do")
_JOINERS = (", ", " - ", " ", ",", " -", "- ")


def _name_first_reference(words: "list[str]") -> bool:
    """`_a_name_before_the_last_word` as the merged head wrote it, the role test read first (the test's copy)."""
    if len(words) < 2:
        return False
    before = " ".join(words[:-1])
    while before[-1:] == ",":
        before = before[:-1]
    if not before or taxonomy._a_role_or_a_service(before):
        return False
    return taxonomy.a_persons_name(before) or (
        taxonomy._without_points(words[-1]) in taxonomy._PERSONS_NAME_DEGREES and taxonomy._a_family_name_alone(before))


def test_every_generated_value_reads_as_the_role_test_first_read_it(monkeypatch: pytest.MonkeyPatch) -> None:
    """The class behind item 7, generated: 3,000 values of one to 120 relations, roles, degrees and names joined by
    commas, dashes and spaces, one in five a run of 40 to 120 relations and degrees alone (`Mother`, `CRNA`: 98467814
    asked the role reader once a word of it); each reads exactly as with the role test read first (the merged head's
    order, run with
    room to recurse), and the role reader is asked at most once a word of a name of 60 characters (never more than
    32 times) whatever the value's length."""
    import sys

    draw = random.Random(4878)
    values = []
    for case in range(3000):
        pool = ("Mother", "Daughter", "Father", "Sister", "CRNA") if case % 5 == 0 else _RELATIONS_AND_ROLES + _GENERATED_NAMES
        parts = [draw.choice(pool) for _part in range(draw.randint(1 if case % 5 else 40, 120))]
        text = parts[0]
        for part in parts[1:]:
            text += draw.choice(_JOINERS) + part
        values += [text]
    answers = []
    for text in values:
        answer, asks = _role_test_calls(text, monkeypatch)
        assert asks <= 32, (text[:80], asks)
        answers += [answer]
    limit = sys.getrecursionlimit()
    sys.setrecursionlimit(20000)
    try:
        monkeypatch.setattr(taxonomy, "_a_name_before_the_last_word", _name_first_reference)
        assert [taxonomy._a_role_or_a_service(text) for text in values] == answers
    finally:
        sys.setrecursionlimit(limit)
    assert sum(answers) > 300 and len(answers) - sum(answers) > 300, sum(answers)


def test_item_7_is_red_on_the_mutant_that_reads_the_role_test_first(monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the role test read first on the words before the last (the merged head's order): Codex's 512 repetitions
    raise RecursionError again, and 256 ask the role reader once a word."""
    monkeypatch.setattr(taxonomy, "_a_name_before_the_last_word", _name_first_reference)
    with pytest.raises(RecursionError):
        taxonomy._a_role_or_a_service("Mother, " * 512 + "Mother")
    assert _role_test_calls("Mother, " * 256 + "Mother", monkeypatch)[1] > 200


# -- (9) ITEM 9, K-HZ-41's REMARK KINDS: AN AGE OF EXACTLY THE TOP CODE IS NOT COUNTED ----------------------------------

def _remark_twin(tmp_path: pathlib.Path) -> "tuple[dict[str, object], list[str], set[str]]":
    """The remark kind of an age past 89 beside the patient column (`remark_ages`, 20,000 rows, 1,000 people)
    through the commands, unanswered, counted by the residual counter: its counts, the twin's remark cells and the
    real remark cells."""
    import value_reader_residual_forms as residual
    import value_readers_forms as readers

    with residual.registered():
        seen = readers.measure(tmp_path / "remarks", residual.KIND_REMARK_AGES, 20000, "unanswered", seed=residual.SEED)
    twin_path = [path for path in (tmp_path / "remarks").rglob("*twin*.csv")][0]
    source = (tmp_path / "remarks") / f"{residual.KIND_REMARK_AGES}.csv"
    columns = _twin_columns(twin_path)
    with open(source, encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    real = {row[rows[0].index("remark_age")] for row in rows[1:]}
    return seen, columns["remark_age"], real


def _ages_written(text: str) -> "list[int]":
    return [int(found) for found in re.findall(r"(?<![0-9])([0-9]{2,3})(?![0-9])", text) if 90 <= int(found) <= 125]


def test_k_hz_41_s_remarks_count_no_cell_once_the_top_code_s_own_form_is_set_aside(tmp_path: pathlib.Path) -> None:
    """K-HZ-41's remark kind (the orchestrator's ruling): every twin cell equal to a real remark is the real remark
    of an age of exactly 90, the top code's own form, and no twin cell shows an age past 90, so the counter, which
    places such a remark with no needle, counts 0 shown and 0 twin cells (98467814's counter counted these 1,380
    cells twice: 2,760 a mode, and 4,160 in the kind of one row a case)."""
    seen, twin, real = _remark_twin(tmp_path)
    forms = seen["columns"]["remark_age"]["forms"]  # type: ignore[index]
    counted = sum(int(form.get(key, 0)) for form in forms.values()
                  for key in ("shown", "needles_shown", "twin_equal", "twin_needles"))
    assert counted == 0, forms
    equal = [cell for cell in twin if cell in real and _ages_written(cell)]
    assert equal and {max(_ages_written(cell)) for cell in equal} == {90}
    assert [cell for cell in twin if any(age > 90 for age in _ages_written(cell))] == []


def test_k_hz_41_s_restated_counter_is_red_on_the_mutant_that_counts_the_top_code_s_own_form(
        tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the remark of an age of exactly 90 placed with its needle again (the counter as 98467814's driver read
    it): the kind counts its top-coded twin cells as real ones."""
    import value_reader_residual_forms as residual
    import value_readers_forms as readers

    real_note = readers._note

    def noted(meta: dict, column: str, cell: str, form: str, needles: "tuple[str, ...]") -> None:
        real_note(meta, column, cell, form, (cell,) if form == residual.FORM_REMARK_AGE and not needles else needles)

    monkeypatch.setattr(readers, "_note", noted)
    seen, _twin, _real = _remark_twin(tmp_path)
    forms = seen["columns"]["remark_age"]["forms"]  # type: ignore[index]
    assert sum(int(form.get("twin_equal", 0)) for form in forms.values()) > 1000, forms
