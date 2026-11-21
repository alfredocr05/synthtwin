"""Batch 4t's last code round, the held writer: the orchestrator's LANE I4t RULINGS 3 (1), on the last code round's
scoped verify (its item 1, HIPAA first).

A column of codes past a double's range DECLARED record numbers beside a declared person column (`synthtwin profile
--person person_id --identifier code_value`; 20,000 rows, 1,000 people, 20 rows a person, one code a person) is held
whole, and the writer of a held column (method G9.6b, plan P4-D432: `generation._spelled_off_the_real` and every route
it takes) kept each twin value off the real by its merged key alone. Its excluded template `%0&%%%` wrote `10e451`,
the code `1e452` of one person by value: on 69b4e781 280 twin cells of 20,000, 10 codes of 13 people (the same on
98467814 and 50203b85). A value is now kept, and a spelling taken, only where its mantissa written with an exponent
ends with no nought (`generation._mantissa_ends_with_a_nought`) and every spelling of its number in a named layout of
the column is kept off the real by its merged key in turn (`generation._number_kept_off_the_real`, the number read as
the profile's check reads a made-up spelling, `parsing.exact_of_a_number`).

The cases: the verify's own table at the owner's floor with seed 7 beside it, red on 69b4e781 and green here;
generated cases (drawn columns of codes of mixed mantissa widths through the commands, red on 69b4e781 where no nought
ends the twin's mantissa, and the spellings of drawn numbers in drawn layouts against every filling of each layout);
the room the verify's description gives, read part by part; two mutants. Invented tables only; every table case runs
the commands a person types, nobody at the keyboard, the table floor on, and validates the twin and the real table.
Twin cells are read against the real cells three ways -- as written, by merged key and by value -- the last by this
file's own reader (Python's decimal module, no context to round a long number).
"""

from __future__ import annotations

import contextlib
import csv
import decimal
import io
import itertools
import json
import pathlib
import random
import re

import pytest

import health_zoo as zoo
from synthtwin import cli, contract, generation, parsing, taxonomy

_PERSON_ROWS = 20
_HELD = "you told synthtwin that this column holds record numbers rather than measurements"


def _value(text: str) -> "tuple[object, ...] | None":
    """The number a cell writes, exact, or None: this file's own reader."""
    try:
        number = decimal.Decimal(text.strip())
    except (decimal.InvalidOperation, ValueError):
        return None
    if not number.is_finite():
        return None
    if not number:
        return (0, (0,), 0)
    sign, digits, exponent = number.as_tuple()
    kept = len(digits)
    while kept > 1 and digits[kept - 1] == 0:
        kept -= 1
        exponent = int(exponent) + 1
    return (sign, tuple(digits[:kept]), exponent)


def _verify_s_codes(people: int, draw: random.Random) -> "list[str]":
    """The verify's drawn codes, one a person (the last code round's own draw, written again here): a mantissa of one
    figure, or for one person in ten two figures the second no nought, and an exponent from 400 to 560."""
    codes: "list[str]" = []
    for _person in range(people):
        mantissa = f"{draw.randint(1, 9)}" if draw.random() < 0.9 else f"{draw.randint(1, 9)}{draw.randint(1, 9)}"
        codes += [f"{mantissa}e{draw.randint(400, 560)}"]
    return codes


def _mixed_codes(people: int, draw: random.Random) -> "list[str]":
    """Codes of mixed mantissa widths, one a person, an exponent from 400 to 480: one figure from 1 to 8 for seven
    people in ten, and `90`, two figures the second any, or a figure, a point and a figure for one in ten each. The
    one-figure layout's exclusion then writes `9` first, and its twin `9e402` is the real `90e401` by value, with no
    nought ending its own mantissa."""
    codes: "list[str]" = []
    for _person in range(people):
        power = draw.randint(400, 480)
        kind = draw.random()
        if kind < 0.7:
            mantissa = f"{draw.randint(1, 8)}"
        elif kind < 0.8:
            mantissa = "90"
        elif kind < 0.9:
            mantissa = f"{draw.randint(1, 8)}{draw.randint(0, 9)}"
        else:
            mantissa = f"{draw.randint(1, 9)}.{draw.randint(0, 9)}"
        codes += [f"{mantissa}e{power}"]
    return codes


@contextlib.contextmanager
def _nobody_at_the_keyboard():  # type: ignore[no-untyped-def]
    asked = cli._there_is_somebody_to_ask
    cli._there_is_somebody_to_ask = lambda: False
    try:
        yield
    finally:
        cli._there_is_somebody_to_ask = asked


def _declared(folder: pathlib.Path, codes: "list[str]") -> "dict[str, object]":
    """One code a person, 20 rows a person: profiled with the person column and the codes declared, generated at seed
    0, the twin and the real table validated; the four exits, the codes' block, the rows and the twin's codes."""
    rows = [[f"R{200000 + person}", f"{visit + 1}", codes[person]]
            for person in range(len(codes)) for visit in range(_PERSON_ROWS)]
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / "codes.csv"
    source.write_bytes(zoo.csv_bytes(["person_id", "visit", "code_value"], rows))
    described = folder / "codes-profile.json"
    twin = folder / "codes-twin.csv"
    exits: "list[int]" = []
    with _nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        exits += [cli.main(["profile", f"{source}", "--replace", "--person", "person_id", "--identifier",
                            "code_value"], small_tables_refused=True)]
        exits += [cli.main(["generate", f"{described}", "--replace", "--seed", "0"], small_tables_refused=True)]
        for name, checked in (("twin", twin), ("real", source)):
            (folder / name).mkdir(exist_ok=True)
            exits += [cli.main(["validate", f"{described}", "--twin", f"{checked}", "--out-dir", f"{folder / name}",
                                "--replace"], small_tables_refused=True)]
    document = json.loads(described.read_text(encoding="utf-8"))
    with open(twin, encoding="utf-8", newline="") as handle:
        written = [row[2] for row in list(csv.reader(handle))[1:]]
    block = [one for one in document["columns"] if one["name"] == "code_value"][0]
    return {"exits": exits, "block": block, "rows": rows, "twin": written}


def _held_by_few(rows: "list[list[str]]") -> "dict[tuple[object, ...], int]":
    """Each real code 1 to 10 people hold, by value, with how many hold it."""
    people: "dict[tuple[object, ...], set[str]]" = {}
    for person, _visit, cell in rows:
        number = _value(cell)
        if number is not None:
            people.setdefault(number, set()).add(person)
    return {number: len(held) for number, held in people.items() if len(held) < 11}


def _equal(twin: "list[str]", rows: "list[list[str]]") -> "dict[str, int]":
    """Twin cells equal to a real code 1 to 10 people hold, as written, by merged key and by value; and twin cells
    equal by value to any real code."""
    few = _held_by_few(rows)
    spelled = {cell for _person, _visit, cell in rows if _value(cell) in few}
    merged = {parsing.merged_key(cell) for cell in spelled}
    every = {_value(cell) for _person, _visit, cell in rows}
    return {
        "written": sum(1 for cell in twin if cell in spelled),
        "merged": sum(1 for cell in twin if parsing.merged_key(cell) in merged),
        "by_value": sum(1 for cell in twin if _value(cell) in few),
        "any_real_by_value": sum(1 for cell in twin if _value(cell) in every),
    }


def _nought_ended(twin: "list[str]") -> int:
    """Twin cells written with an exponent whose mantissa ends with a nought (this file's own reading)."""
    ended = 0
    for cell in twin:
        found = re.fullmatch(r"[+-]?(\d*\.?\d*)[eE][+-]?\d+", cell.strip())
        if found and found.group(1).replace(".", "")[-1:] == "0":
            ended += 1
    return ended


# -- THE VERIFY'S TABLE ----------------------------------------------------------------------------------------------


@pytest.mark.parametrize("seed", [2024, 7])
def test_the_verify_s_declared_codes_hold_no_real_code_by_value(tmp_path: pathlib.Path, seed: int) -> None:
    """THE VERIFY'S TABLE, seed 2024 with seed 7 beside it: 20,000 rows of 1,000 people, the codes declared record
    numbers beside the declared person column, held whole. On 69b4e781 the twin wrote 280 cells equal by value to a
    real code 1 to 10 people hold at either seed (10 codes at seed 2024, 11 at seed 7: `10e451` for the real `1e452`),
    0 as written and 0 by merged key, and 3,620 and 3,880 cells whose mantissa ends with a nought. Here: 0 three ways,
    0 equal by value to any real code, no mantissa ending with a nought; the twin and the real table validate."""
    seen = _declared(tmp_path, _verify_s_codes(1000, random.Random(seed)))
    assert seen["exits"] == [0, 0, 0, 0]
    block = seen["block"]
    assert block["role"] == taxonomy.ROLE_IDENTIFIER and block["detection_evidence"] == _HELD  # type: ignore[index]
    assert len(seen["rows"]) == 20000 and len(_held_by_few(seen["rows"])) > 700  # type: ignore[arg-type]
    assert _equal(seen["twin"], seen["rows"]) == {  # type: ignore[arg-type]
        "written": 0, "merged": 0, "by_value": 0, "any_real_by_value": 0,
    }
    assert _nought_ended(seen["twin"]) == 0  # type: ignore[arg-type]


# -- GENERATED CASES -------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("seed", [11, 2024])
def test_a_drawn_column_of_mixed_widths_holds_no_real_code_by_value(tmp_path: pathlib.Path, seed: int) -> None:
    """GENERATED at the floor: drawn codes of one figure, two figures (`90` among them) and a figure, a point and a
    figure, declared record numbers beside the declared person column (20,000 rows, 1,000 people). On 69b4e781 the
    one-figure layout's excluded template `9&%%%` wrote `9e402` for the real `90e401`, no nought ending its mantissa:
    1,080 twin cells by value at seed 11, 1,280 at seed 2024. Here 0 three ways and 0 equal by value to any real code;
    the description describes its own table (the real table validates)."""
    seen = _declared(tmp_path, _mixed_codes(1000, random.Random(seed)))
    exits = seen["exits"]
    assert exits[0] == 0 and exits[1] == 0 and exits[3] == 0, exits  # type: ignore[index]
    assert seen["block"]["detection_evidence"] == _HELD  # type: ignore[index]
    assert len(_held_by_few(seen["rows"])) > 500  # type: ignore[arg-type]
    assert _equal(seen["twin"], seen["rows"]) == {  # type: ignore[arg-type]
        "written": 0, "merged": 0, "by_value": 0, "any_real_by_value": 0,
    }


# Layouts of numbers small enough to be filled every way, each mark from its own alphabet: a figure, the zero fill, a
# lower- or upper-case letter, and the marks themselves.
_SMALL_LAYOUTS = (
    "%&%%", "%%&%", "%.%&%", ".%%&%", "-%&-%", "+%&%", "%@%%", "%%&+%", "%%%", "!%%", "%%.%", "-%.%%", "%%%%",
)
_ALPHABETS = {"%": "0123456789", "!": "0", "&": "abcdefghijklmnopqrstuvwxyz", "@": "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}


def test_the_spellings_of_a_number_are_every_filling_of_its_layout_that_writes_it() -> None:
    """GENERATED at the unit level: for thirteen small layouts (exponents, points, signs, the zero fill), every
    filling of the layout, each mark from its own alphabet, read by the census's own reader and by the reader of
    record; for each number those fillings write, and for 1,950 drawn numbers besides, the held writer's spellings
    (`generation._number_spellings`) are exactly the fillings that wear the layout and write that number, and this
    file's own reader reads each as the same number. Zero, which a layout with an exponent writes at every power of
    ten, is listed by none of them there: the writer refuses it wherever such a layout is named."""
    draw = random.Random(31)
    compared = 0
    for layout in _SMALL_LAYOUTS:
        shape = generation._number_layout(layout, layout)
        assert shape is not None, layout
        written: "dict[tuple[int, tuple[str, ...], int], list[str]]" = {}
        for marks in itertools.product(*[_ALPHABETS.get(mark, mark) for mark in layout]):
            filling = "".join(marks)
            if parsing.layout_form(filling, parsing.LAYOUT_PLAIN) != layout:
                continue
            number = parsing.exact_of_a_number(filling)
            if number is not None:
                written.setdefault(number, []).append(filling)
        assert written, layout
        drawn = [parsing.exact_of_a_number(f"{draw.choice('-+')}{draw.randint(0, 999)}e{draw.randint(-12, 12)}")
                 for _each in range(150)]
        for number in list(written) + [one for one in drawn if one is not None]:
            spellings = generation._number_spellings(shape, number, parsing.LAYOUT_PLAIN)
            if shape.letter and not number[1]:
                assert spellings == [] and len(written.get(number, [])) > 1, (layout, number)
                continue
            assert sorted(spellings) == sorted(written.get(number, [])), (layout, number)
            for spelling in spellings:
                assert _value(spelling) == _value(spellings[0]), (layout, spelling)
            compared += 1
    assert compared > 3000, compared
    assert generation._number_layout("%,%%%", "%,%%%") is None and generation._number_layout("@@%%", "@@%%") is None


def test_the_verify_s_room_reads_each_value_by_the_number_it_writes() -> None:
    """The room the verify's description gives (its layouts, exclusions and spill, as the profile published them),
    read part by part: `10e451` is kept off the real by its merged key alone, which is all 69b4e781 read, and is now
    refused twice -- its mantissa ends with a nought, and its number's spelling `1e452` in the one-figure layout is one
    nothing published keeps off the real. `1001e449`, a wider spelling, is kept: no nought ends it, and no named layout
    spells its number. `0900e529`, as long merged as the spill, is refused both ways (`9e531` is its number)."""
    facts = contract.IdentifierFacts(
        min_length=5, max_length=6, all_whole_numbers=True, n_all_digits=0, n_code_alphabet=11,
        n_distinct_by_occurrences={"20": 772}, layout_forms={"%%&%%%": 1840, "%&%%%": 18160}, layout_prefixes={},
        layout_exclusions={"%%&%%%": ("%0&%%%",), "%&%%%": ("%z%%%",), parsing.EXCLUSION_SPILL: ("%%%%%%%",)},
    )
    room = generation._off_the_real_room(facts, ())
    assert [shape.layout for shape in room.numeric] == ["%%&%%%", "%&%%%"] and not room.figures_only
    assert generation._key_kept_off_the_real(room, "10e451")
    assert generation._mantissa_ends_with_a_nought("10e451")
    assert not generation._number_kept_off_the_real(room, "10e451")
    assert not generation._kept_off_the_real(room, "10e451")
    assert generation._kept_off_the_real(room, "1001e449")
    assert generation._key_kept_off_the_real(room, "0900e529") and not generation._kept_off_the_real(room, "0900e529")
    assert generation._number_kept_off_the_real(room, "0900e529") is False
    assert not generation._number_kept_off_the_real(room, "0e900")


# -- MUTANTS -------------------------------------------------------------------------------------------------------


def test_mutant_no_reading_by_value_writes_the_drawn_codes_back(tmp_path: pathlib.Path, monkeypatch) -> None:
    """MUTANT (the reading by value removed from the writer, the verify's own): the drawn column of mixed widths is
    written with real codes by value again (1,080 twin cells at seed 11, `9e402` for the real `90e401`), which the
    generated case above reads red: the nought rule alone does not close the class."""
    monkeypatch.setattr(generation, "_number_kept_off_the_real", lambda room, core: True)
    seen = _declared(tmp_path, _mixed_codes(1000, random.Random(11)))
    assert _equal(seen["twin"], seen["rows"])["by_value"] > 0  # type: ignore[arg-type]


def test_mutant_no_nought_rule_writes_mantissas_ending_with_a_nought(tmp_path: pathlib.Path, monkeypatch) -> None:
    """MUTANT (the nought rule removed): the verify's table is written with mantissas ending with a nought again
    (1,680 twin cells at seed 2024, each a number some shorter spelling writes), which the verify's case above reads
    red, though the reading by value keeps each of them off the codes the named layouts can hold."""
    monkeypatch.setattr(generation, "_mantissa_ends_with_a_nought", lambda core: False)
    seen = _declared(tmp_path, _verify_s_codes(1000, random.Random(2024)))
    assert _nought_ended(seen["twin"]) > 0  # type: ignore[arg-type]
