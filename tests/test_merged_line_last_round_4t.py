"""Batch 4t's last code round: the orchestrator's LANE I4t RULINGS 2, on the fix round's scoped verify.

(1) ITEM 1, the verify's carry 1, HIPAA first. Where a column of numbers too large or too small to hold is spelled one
letter or figure wider (contract NF139; method G10.5 step 8), its writer never ends a mantissa with a nought
(`generation._wider_mantissa_ends_with_a_nought`), and `synthtwin profile` reads the made-up spellings against the
real cells by the number each writes as well as by merged key (`profile._a_spelling_names_a_few` through
`parsing.exact_of_a_number`). On the fix round's head 50203b85 a long table's assay of codes one a person, spelled
wider, got 400 of its 4,000 cells back as the code of one person by value (`30e404` is the code `3e405`), two assays
and their pool 405, the same codes in a column of their own 2,000 of 20,000, and codes written with the minus sign
U+2212 were copied by value in 4,000 and 20,000 cells (the merged key keeps that sign, so it joined none of them).

(2) ITEM 2, the fix round's whole suite: `test_a_column_of_whole_numbers_each_on_one_row_is_held[refyear]` counted the
suite's own folder, named after its head (`suite-50203b85`), as a value of `refyear` published on the screen
(`S24-50203`): the helper now writes the run's folder out of what it counts
(`unanswered_identifier_shapes.without_the_folder`); the column was held on both trees. The floor check's two cases are
mended in tests/test_merged_line_review_items_4t.py.

Each item: the reviewer's own table as a case at the owner's floor (20,000 rows or more, 1,000 people where a person
column stands), red on 50203b85 and green here, a generated case and a mutant. Invented tables only; every table case
runs the commands a person types, nobody at the keyboard, the table floor on. Twin cells are read against the real
cells three ways -- as written, by merged key and by value -- the last by this file's own reader (Python's decimal
module, no context to round a long number).
"""

from __future__ import annotations

import contextlib
import csv
import decimal
import io
import json
import pathlib
import random

import pytest

import health_zoo as zoo
import unanswered_identifier_shapes as shapes
from synthtwin import cli, generation, parsing, profile, taxonomy

_MINUS = "\u2212"
_KEYS = ("assay_a", "pulse", "temp_c", "glucose_mg", "airway", "pain_score")


def _value(text: str) -> "tuple[object, ...] | None":
    """The number a cell writes, exact, or None: this file's own reader (the sign U+2212 read as a minus)."""
    try:
        number = decimal.Decimal(text.strip().replace(_MINUS, "-"))
    except (decimal.InvalidOperation, ValueError):
        return None
    if not number.is_finite() or not number:
        return None
    sign, digits, exponent = number.as_tuple()
    kept = len(digits)
    while kept > 1 and digits[kept - 1] == 0:
        kept -= 1
        exponent = int(exponent) + 1
    return (sign, tuple(digits[:kept]), exponent)


@contextlib.contextmanager
def _nobody_at_the_keyboard():  # type: ignore[no-untyped-def]
    asked = cli._there_is_somebody_to_ask
    cli._there_is_somebody_to_ask = lambda: False
    try:
        yield
    finally:
        cli._there_is_somebody_to_ask = asked


def _commands(folder: pathlib.Path, stem: str, header: "list[str]", rows: "list[list[str]]",
              generate: bool = True) -> "dict[str, object]":
    """Profile the table (nobody at the keyboard, the table floor on, the person column declared) and generate at
    seed 0: the description and the twin's columns."""
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / f"{stem}.csv"
    source.write_bytes(zoo.csv_bytes(header, rows))
    described = folder / f"{stem}-profile.json"
    with _nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["profile", f"{source}", "--replace", "--identifier", "person_id"], small_tables_refused=True) == 0
        if generate:
            assert cli.main(["generate", f"{described}", "--replace", "--seed", "0"], small_tables_refused=True) == 0
    seen: "dict[str, object]" = {"description": json.loads(described.read_text(encoding="utf-8"))}
    if generate:
        with open(folder / f"{stem}-twin.csv", encoding="utf-8", newline="") as handle:
            written = list(csv.reader(handle))
        seen["twin"] = {name: [row[place] for row in written[1:]] for place, name in enumerate(written[0])}
    return seen


def _block(document: "dict[str, object]", name: str) -> "dict[str, object]":
    return [block for block in document["columns"] if block["name"] == name][0]  # type: ignore[index,union-attr]


def _key_block(document: "dict[str, object]", key: str) -> "dict[str, object]":
    by_key = _block(document, "item_value")["by_key"]
    if key == "pool":
        return by_key["pool"]  # type: ignore[index,no-any-return]
    return [entry["block"] for entry in by_key["key_blocks"] if entry["key"] == key][0]  # type: ignore[index]


def _long_table(code: "object", keys: "tuple[str, ...]" = _KEYS, people: int = 1000, visits: int = 4,
                extra: "list[list[str]] | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Codex's long table: four visits of each person, six keys (24,000 rows); an assay key holds ``code(p, key)``
    for person p (Codex's `str(1 + p % 9) + "e" + str(400 + p // 9)`: one code a person), the others ordinary
    measurements and words."""
    draw = random.Random(5)
    rows: "list[list[str]]" = []
    for p in range(people):
        for visit in range(visits):
            for key in keys:
                if key.startswith("assay"):
                    value = code(p, key)  # type: ignore[operator]
                elif key == "pulse":
                    value = f"{draw.randint(52, 118)}"
                elif key == "temp_c":
                    value = f"{draw.gauss(36.8, 0.45):.1f}"
                elif key == "glucose_mg":
                    value = f"{max(55, round(draw.gauss(135, 38)))}"
                elif key == "airway":
                    value = draw.choice(("Clear", "Wheeze", "Crackles"))
                else:
                    value = f"{draw.randint(0, 10)}"
                rows += [[f"R{200000 + p}", f"{visit + 1}", key, value]]
    return ["person_id", "visit", "item_key", "item_value"], rows + (extra or [])


def _codes_few_hold(rows: "list[list[str]]", place: int, wanted: "object" = None) -> "dict[tuple[object, ...], int]":
    """Each real number 1 to 10 people hold in the column at ``place`` (the cells ``wanted`` keeps, by default the
    numbers too large or too small for a double), by value, with how many people hold it."""
    held: "dict[tuple[object, ...], set[str]]" = {}
    for row in rows:
        cell = row[place]
        number = _value(cell)
        if number is None:
            continue
        if wanted is None and parsing.classify_number(cell) != parsing.NUMBER_OUT_OF_RANGE:
            continue
        if wanted is not None and not wanted(row):  # type: ignore[operator]
            continue
        held.setdefault(number, set()).add(row[0])
    return {number: len(people) for number, people in held.items() if len(people) < 11}


def _equal(twin: "list[str]", rows: "list[list[str]]", place: int) -> "dict[str, int]":
    """Twin cells equal to a real code 1 to 10 people hold: as written, by merged key and by value."""
    few = _codes_few_hold(rows, place)
    spelled = {row[place] for row in rows if _value(row[place]) in few}
    merged = {parsing.merged_key(cell) for cell in spelled}
    return {
        "written": sum(1 for cell in twin if cell in spelled),
        "merged": sum(1 for cell in twin if parsing.merged_key(cell) in merged),
        "by_value": sum(1 for cell in twin if _value(cell) in few),
    }


def _assay_cells(seen: "dict[str, object]", key: str = "assay") -> "list[str]":
    twin = seen["twin"]
    return [value for item, value in zip(twin["item_key"], twin["item_value"]) if item.startswith(key)]  # type: ignore[index]


# -- (1) ITEM 1: THE WIDER SPELLINGS AND THE CHECK, BY VALUE -----------------------------------------------------------


def test_codex_s_assay_spelled_wider_holds_no_real_code_by_value(tmp_path: pathlib.Path) -> None:
    """Codex's table of the fix round (24,000 rows, 1,000 people, `assay_a` one code a person past a double's range):
    the assay keeps its block spelled wider (NF139) and its twin cells equal no real code as written, by merged key or
    by value (on 50203b85: 400 cells by value, 100 codes, one person each, `30e404` for the code `3e405`)."""
    header, rows = _long_table(lambda p, key: f"{1 + p % 9}e{400 + p // 9}")
    assert len(rows) == 24000 and len(_codes_few_hold(rows, 3)) == 1000
    seen = _commands(tmp_path, "assays", header, rows)
    block = _key_block(seen["description"], "assay_a")  # type: ignore[arg-type]
    assert block["role"] == taxonomy.ROLE_UNREPRESENTABLE
    assert block["detection_evidence"] == generation.SPELLED_WIDER_EVIDENCE
    assert _equal(_assay_cells(seen), rows, 3) == {"written": 0, "merged": 0, "by_value": 0}


def test_two_assays_and_their_pool_hold_no_real_code_by_value(tmp_path: pathlib.Path) -> None:
    """The verify's second table (24,500 rows): two assays of codes, `-de-NNN` beside Codex's, and 100 rare keys of
    one row of 500 people whose codes stand in the pooled block: every block spelled wider, 0 twin cells equal a real
    code by value (on 50203b85: 405)."""
    keys = ("assay_a", "assay_b", "pulse", "temp_c", "airway", "pain_score")
    extra = [[f"R{200000 + p}", "5", f"rare_{p % 100}", f"{1 + p % 9}e{900 + p}"] for p in range(0, 1000, 2)]
    header, rows = _long_table(
        lambda p, key: f"{1 + p % 9}e{400 + p // 9}" if key == "assay_a" else f"-{1 + p % 5}e-{450 + p // 5}",
        keys, extra=extra)
    seen = _commands(tmp_path, "two", header, rows)
    for key in ("assay_a", "assay_b", "pool"):
        block = _key_block(seen["description"], key)  # type: ignore[arg-type]
        assert block["role"] == taxonomy.ROLE_UNREPRESENTABLE, key
        assert block["detection_evidence"] == generation.SPELLED_WIDER_EVIDENCE, key
    twin = seen["twin"]
    cells = [value for item, value in zip(twin["item_key"], twin["item_value"])  # type: ignore[index]
             if item.startswith("assay") or item.startswith("rare")]
    assert _equal(cells, rows, 3)["by_value"] == 0


@pytest.mark.parametrize("people, rows_a_person", [(1000, 20), (5000, 4)])
def test_the_same_codes_in_a_column_of_their_own_hold_none_by_value(tmp_path: pathlib.Path, people: int,
                                                                     rows_a_person: int) -> None:
    """The verify's top-level column of the same codes (20,000 rows; one code a person at 20 or at 4 rows a person):
    spelled wider, 0 of 20,000 twin cells equal a real code by value (on 50203b85: 2,000 at both)."""
    rows = [[f"R{200000 + p}", f"{v + 1}", f"{1 + p % 9}e{400 + p // 9}"] for p in range(people)
            for v in range(rows_a_person)]
    seen = _commands(tmp_path, "top", ["person_id", "visit", "item_value"], rows)
    block = _block(seen["description"], "item_value")  # type: ignore[arg-type]
    assert block["role"] == taxonomy.ROLE_UNREPRESENTABLE
    assert block["detection_evidence"] == generation.SPELLED_WIDER_EVIDENCE
    assert _equal(seen["twin"]["item_value"], rows, 2) == {"written": 0, "merged": 0, "by_value": 0}  # type: ignore[index]


@pytest.mark.parametrize("where", ["keyed", "own column"])
def test_codes_written_with_the_minus_sign_are_read_by_value(tmp_path: pathlib.Path, where: str) -> None:
    """Codes past a double's range written with the minus sign U+2212 before `3e405`, one a person: the counters' own
    `-3e405` is that number, which no merged key joins (the merged key keeps the sign U+2212), so the check reads it
    by value and the block is spelled wider: 0 twin cells equal a real code by value (on 50203b85: 4,000 of the
    keyed assay's cells, 20,000 of the column's)."""
    def code(p: int, _key: str = "") -> str:
        return f"{_MINUS}{1 + p % 9}e{400 + p // 9}"
    if where == "keyed":
        header, rows = _long_table(code)
        seen = _commands(tmp_path, "minus", header, rows)
        block = _key_block(seen["description"], "assay_a")  # type: ignore[arg-type]
        cells = _assay_cells(seen)
        place = 3
    else:
        rows = [[f"R{200000 + p}", f"{v + 1}", code(p)] for p in range(1000) for v in range(20)]
        seen = _commands(tmp_path, "minus", ["person_id", "visit", "item_value"], rows)
        block = _block(seen["description"], "item_value")  # type: ignore[arg-type]
        cells = seen["twin"]["item_value"]  # type: ignore[index]
        place = 2
    assert len(_codes_few_hold(rows, place)) == 1000
    assert _equal(cells, rows, place)["by_value"] == 0
    assert block["detection_evidence"] == generation.SPELLED_WIDER_EVIDENCE


def test_a_whole_number_past_309_figures_beside_small_numbers_is_held_whole(tmp_path: pathlib.Path) -> None:
    """The one shape whose wider numbers are a figure and noughts by construction (a whole number this format holds,
    past 309 figures: `8` and 400 noughts, then `e-400`, is the number 8): codes one a person beside one person's
    number of 400 figures and nine people holding 1 to 9, 20 rows a person (20,000 rows). Read by value, the column's
    wider spellings meet those nine, so the command holds it whole as record numbers (NF139): 0 twin cells equal a
    real value 1 to 10 people hold by value (on 50203b85: 180, the nine numbers)."""
    def code(p: int) -> str:
        if p == 999:
            return "9" * 400
        return f"{p + 1}" if p < 9 else f"{1 + p % 9}e{400 + p // 9}"
    rows = [[f"R{200000 + p}", f"{v + 1}", code(p)] for p in range(1000) for v in range(20)]
    seen = _commands(tmp_path, "wide", ["person_id", "visit", "item_value"], rows)
    few = _codes_few_hold(rows, 2, wanted=lambda row: True)
    assert sum(1 for cell in seen["twin"]["item_value"] if _value(cell) in few) == 0  # type: ignore[index]
    block = _block(seen["description"], "item_value")  # type: ignore[arg-type]
    assert block["role"] == taxonomy.ROLE_IDENTIFIER
    assert block["detection_evidence"] == generation.SPELLED_WIDER_EVIDENCE


def _shortest(number: "tuple[object, ...]") -> int:
    """The fewest letters and figures any spelling of a number holds: its significant figures written plainly, or
    with `e` and an exponent, the point anywhere among them (marks such as a sign or a point are not counted)."""
    _sign, digits, exponent = number
    figures = len(digits)  # type: ignore[arg-type]
    power = int(exponent)  # type: ignore[call-overload]
    if power >= 0:
        plain = figures + power
    else:
        plain = max(figures, -power)
    written = [plain]
    for point in range(figures):
        for noughts in range(4):
            shown = power + point - noughts
            if shown:
                written += [figures + noughts + 1 + len(f"{abs(shown)}")]
    return min(written)


def _walked(kind: int, negative: bool, width: int, count: int) -> "list[str]":
    walked: "dict[tuple[int, bool], int]" = {}
    used: "dict[str, int]" = {}
    found: "list[str]" = []
    for _each in range(count):
        spelling = generation._wider_family_number(kind, negative, width, walked, used, ())
        if spelling is None:
            break
        found += [spelling]
    return found


def test_every_wider_number_needs_all_its_letters_and_figures() -> None:
    """GENERATED: every kind and sign of step 8's walk at widths 6 to 80 and around 309 figures, 150 numbers each:
    each number written needs at least as many letters and figures as it holds, so no real cell no wider than
    `max_length` (one fewer) can be that number; the whole numbers this format holds past 309 figures are the one
    exemption (a figure and noughts by construction, read by value by the profile). Red on 50203b85 (`10e400` is
    `1e401`, five letters and figures at a width of six; `1.10000` is `1.1`; `100000` is `1e5`) and on the mutant that
    steps no mantissa ending with a nought past."""
    draw = random.Random(83)
    widths = sorted({*draw.sample(range(6, 81), 18), 309, 310, 311, 330})
    met = 0
    for width in widths:
        for kind in (1, 2, 3, 4):
            for negative in (False, True):
                for spelling in _walked(kind, negative, width, 150):
                    number = _value(spelling)
                    assert number is not None, spelling
                    letters = sum(1 for character in spelling if character.isalnum())
                    if kind == 3 and width >= 310:
                        assert spelling.lstrip("-")[1:].split("e")[0].strip("0") == "", spelling
                        continue
                    assert _shortest(number) >= letters, (kind, width, spelling)
                    met += 1
    assert met > 15000


def test_the_check_meets_a_real_value_by_the_number_it_writes(tmp_path: pathlib.Path) -> None:
    """GENERATED, the check itself (`profile._a_spelling_names_a_few`): 2,000 made-up spellings of the role, each read
    against a real cell that writes the same number another way (`30e404` for `3e405`, `3.0E+405`, `+3e405`, a
    leading nought, the minus sign U+2212), held by 1 to 10 people (named) or by 11 (not named, by value as by
    merged key), beside a control that writes another number (never named). Red on 50203b85 (no reading by value)."""
    draw = random.Random(911)
    settings = taxonomy.Settings(small_cell_floor=11)
    named = 0
    for _case in range(2000):
        mantissa = draw.randint(1, 9)
        power = draw.randint(400, 999)
        sign = draw.choice(("", "-"))
        small = draw.random() < 0.3
        made = f"{sign}{mantissa}e{'-' if small else ''}{power}"
        lead = _MINUS if sign and draw.random() < 0.4 else sign
        shift = -1 if small else 1
        other = draw.choice((
            f"{lead}{mantissa}0e{'-' if small else ''}{power - shift}",
            f"{lead}{mantissa}.0E{'-' if small else '+'}{power}",
            f"{lead or '+'}{mantissa}e{'-' if small else ''}{power}" if lead != _MINUS else f"{lead}{mantissa}e{'-' if small else ''}{power}",
            f"{lead}0{mantissa}.00e{'-' if small else ''}{power}",
        ))
        assert _value(other) == _value(made), (made, other)
        control = f"{lead}{mantissa}e{'-' if small else ''}{power + 1}"
        holders = draw.randint(1, 11)
        cells = [other] * holders + [control] * 3 + ["1"] * 12
        people = [[f"P{place}" for place in range(len(cells))]]
        answer = profile._a_spelling_names_a_few(cells, (made,), people, settings)
        assert answer == (holders < 11), (made, other, holders)
        assert not profile._a_spelling_names_a_few([control] * 3 + ["1"] * 12, (made,), [[f"P{n}" for n in range(15)]],
                                                   settings)
        assert profile._a_spelling_names_a_few(cells, (made,), people, settings, True)
        named += int(answer)
    assert named > 1500


def _generated_codes(people: int, draw: random.Random) -> "list[str]":
    """One code a person, drawn dense enough that a number the writer makes is often a real one: a mantissa of one
    figure (one person in ten two figures, the second no nought) and an exponent from 400 to 560."""
    codes: "list[str]" = []
    for _p in range(people):
        mantissa = f"{draw.randint(1, 9)}" if draw.random() < 0.9 else f"{draw.randint(1, 9)}{draw.randint(1, 9)}"
        codes += [f"{mantissa}e{draw.randint(400, 560)}"]
    return codes


@pytest.mark.parametrize("seed", [2024, 7])
def test_a_generated_column_of_codes_holds_no_real_code_by_value(tmp_path: pathlib.Path, seed: int) -> None:
    """GENERATED at the floor: 20,000 rows of 1,000 people, 20 rows a person, one drawn code a person: the column is
    spelled wider and 0 twin cells equal a real code 1 to 10 people hold, as written, by merged key or by value (on
    50203b85 the wider spellings whose mantissa ends with noughts, `300e400` for a real `3e402`, wrote real codes
    by value)."""
    codes = _generated_codes(1000, random.Random(seed))
    rows = [[f"R{200000 + p}", f"{v + 1}", codes[p]] for p in range(1000) for v in range(20)]
    assert len(_codes_few_hold(rows, 2)) > 500
    seen = _commands(tmp_path, "drawn", ["person_id", "visit", "item_value"], rows)
    block = _block(seen["description"], "item_value")  # type: ignore[arg-type]
    assert block["detection_evidence"] == generation.SPELLED_WIDER_EVIDENCE
    assert _equal(seen["twin"]["item_value"], rows, 2) == {"written": 0, "merged": 0, "by_value": 0}  # type: ignore[index]


def test_mutant_the_mantissa_rule_removed_holds_codex_s_assay_whole(tmp_path: pathlib.Path, monkeypatch) -> None:
    """MUTANT (the nought rule removed): the wider spellings meet real codes by value again (`30e404`), the reading
    by value names the column once more, and the command holds the whole value column as record numbers where the
    rule keeps the assay's block (the price the rule removes), and the walk's own numbers fall short of their width."""
    monkeypatch.setattr(generation, "_wider_mantissa_ends_with_a_nought", lambda kind, candidate: False)
    assert any(_shortest(_value(spelling)) < 6 for spelling in _walked(1, False, 6, 40))  # type: ignore[arg-type]
    header, rows = _long_table(lambda p, key: f"{1 + p % 9}e{400 + p // 9}")
    seen = _commands(tmp_path, "mutant", header, rows, generate=False)
    assert _block(seen["description"], "item_value")["role"] == taxonomy.ROLE_IDENTIFIER  # type: ignore[arg-type]


def test_mutant_no_reading_by_value_copies_the_minus_sign_codes(tmp_path: pathlib.Path, monkeypatch) -> None:
    """MUTANT (the check reads by merged key only): the column of codes written with the sign U+2212 is not named,
    and the counters write their real numbers in every one of its 20,000 cells."""
    monkeypatch.setattr(parsing, "exact_of_a_number", lambda text: None)
    rows = [[f"R{200000 + p}", f"{v + 1}", f"{_MINUS}{1 + p % 9}e{400 + p // 9}"] for p in range(1000) for v in range(20)]
    seen = _commands(tmp_path, "mutant", ["person_id", "visit", "item_value"], rows)
    assert _equal(seen["twin"]["item_value"], rows, 2)["by_value"] == 20000  # type: ignore[index]


# -- (2) ITEM 2: THE RUN'S OWN FOLDER IS NO VALUE OF THE TABLE --------------------------------------------------------


def test_a_folder_named_after_a_head_is_no_published_value(tmp_path: pathlib.Path) -> None:
    """The fix round's red case, at its own size (600 rows, the test's device): `refyear` (`S24-50001` up) run in a
    folder named as the whole suite names its folders, after the head (`suite-50203b85`): held, 0 values published.
    On 50203b85's helper the screen's paths showed the figures `50203` of `S24-50203`, and the case read 1."""
    folder = tmp_path / "suite-50203b85" / "refyear"
    folder.mkdir(parents=True)
    seen = shapes.run(folder, "refyear", 600)
    assert seen["role"] == taxonomy.ROLE_IDENTIFIER
    assert seen["description_values"] == 0 and seen["description_fragments"] == 0, seen["description_values"]
    assert "suite-50203b85" in f"{seen['screen']}"


def test_generated_folders_holding_a_real_value_s_figures_are_written_out() -> None:
    """GENERATED: 500 folders whose names hold the figures of a real value (`<letters><figures>` up), each printed on
    a screen as the command prints the files it writes, beside a real value printed elsewhere on one screen in two:
    the count reads only that other value. Red on the mutant that keeps the folder (`without_the_folder` the
    identity)."""
    draw = random.Random(50203)
    printed = 0
    for _case in range(500):
        opening = "".join(draw.choice("ABCDEFGHJKLMNPRSTUVWXZ") for _each in range(draw.randint(1, 3)))
        first = draw.randint(10000, 90000)
        real = [f"{opening}{draw.randint(0, 99):02d}-{first + row}" for row in range(40)]
        figures = real[draw.randrange(40)].split("-")[1]
        folder = pathlib.Path(f"/scratch/run-{draw.randint(1, 9)}/suite-{figures}{draw.choice('abcdef')}{draw.randint(0, 99)}")
        other = draw.random() < 0.5
        screen = (f"These three files will be written:\n  {folder}/t-profile.json\n  {folder}/t-profile.txt\n"
                  + (f"the mode is {real[0]}\n" if other else ""))
        counted = shapes.count_real(real, [shapes.without_the_folder(screen, folder)], [])
        assert counted["description_values"] == (1 if other else 0), (folder, other)
        assert shapes.count_real(real, [screen], [])["description_values"] >= 1
        printed += int(other)
    assert 150 < printed < 350
