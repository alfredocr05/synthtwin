"""Lane GG's shapes (plan P4-D440): few-valued numbers with a wide gap, beside controls with none.

Shared by the gate (`tests/test_zoo_few_valued_gap.py`) and K-HZ-12's
driver (`tools/measurements/kpi_few_valued_gap.py`), so the two measure
the same columns with the same counter. Each column is built by the
standard library's own seeded generator; no value comes from any real
table. Standard library only: the driver loads this before synthtwin.
"""

from __future__ import annotations

import collections
import contextlib
import io
import json
import pathlib
import random
import re
import typing


def _score(low: int, high: int, code: str, share: float) -> "typing.Callable[[random.Random], str]":
    return lambda draw: f"{draw.randint(low, high)}" if draw.random() > share else code


def _half_steps(code: str, share: float) -> "typing.Callable[[random.Random], str]":
    return lambda draw: f"{draw.randint(2, 10) / 2:.1f}" if draw.random() > share else code


def _weighted(pool: "tuple[tuple[int, float], ...]") -> "typing.Callable[[random.Random], str]":
    def pick(draw: random.Random) -> str:
        total = sum(weight for _value, weight in pool)
        left = draw.random() * total
        for value, weight in pool:
            left = left - weight
            if left < 0:
                return f"{value}"
        return f"{pool[-1][0]}"

    return pick


def _two_codes(draw: random.Random) -> str:
    if draw.random() > 0.1:
        return f"{draw.randint(1, 7)}"
    return "-99" if draw.random() < 0.5 else "-88"


# A days' supply (the zoo plan's row 54): common fills and rare ones, each
# rare value under one row in a hundred.
DAYS = ((30, 50.0), (90, 25.0), (7, 6.0), (14, 6.0), (28, 5.0), (60, 4.0),
        (5, 0.6), (10, 0.6), (21, 0.6), (84, 0.6))
QUANTITY = ((30, 40.0), (60, 20.0), (90, 25.0), (1, 2.0), (120, 5.0), (45, 0.05))

# Each a column of few values with a wide gap, beside two controls with
# none: a score of 1 to 5, a pain score of 0 to 10, half-step scores and
# a 1-to-7 scale, each beside -99; a days' supply.
SHAPES: "dict[str, typing.Callable[[random.Random], str]]" = {
    "score5": _score(1, 5, "-99", 0.08),
    "pain": _score(0, 10, "-99", 0.08),
    "dec_score": _half_steps("-99", 0.08),
    "scale7": _score(1, 7, "-99", 0.08),
    "days_supply": _weighted(DAYS),
    "contig": _score(-2, 2, "0", 0.0),
    "plain": _score(1, 5, "1", 0.0),
}
GAPPED = ("score5", "pain", "dec_score", "scale7", "days_supply")
GAPLESS = ("contig", "plain")
# ...and the sweep's other shapes (planning-notes wave6/GG/gg_probe.py):
# codes -9 and -1 below a scale, two codes below one, a code 99 above
# one, and a dispensed quantity whose mode holds two rows in five.
MORE: "dict[str, typing.Callable[[random.Random], str]]" = {
    "score9": _score(1, 5, "-9", 0.08),
    "score1": _score(1, 5, "-1", 0.08),
    "two_codes": _two_codes,
    "code99": _score(1, 5, "99", 0.08),
    "quantity": _weighted(QUANTITY),
}


def _lab(
    mean: float, spread: float, low: float, high: float, code: str, share: float, places: int = 0
) -> "typing.Callable[[random.Random], str]":
    """A rounded laboratory reading clipped to its range, beside a code on ``share`` of rows."""

    def one(draw: random.Random) -> str:
        if draw.random() < share:
            return code
        return f"{min(high, max(low, round(draw.gauss(mean, spread), places))):.{places}f}"

    return one


# ...and its repair 1's laboratory shapes (the statistics skeptic's items
# 1 and 2, planning-notes wave6/GG-stat-work): a heart rate of 61 values
# beside -99, a glucose of 46 beside 999, and a potassium to one decimal
# beside -99 whose tail holds values on one cell each.
LABS: "dict[str, typing.Callable[[random.Random], str]]" = {
    "hr61": _lab(78, 10, 50, 110, "-99", 0.03),
    "glu46": _lab(100, 8, 80, 125, "999", 0.02),
    "k_dec": _lab(4.2, 0.35, 3.0, 5.6, "-99", 0.03, 1),
}


def table(
    shapes: "dict[str, typing.Callable[[random.Random], str]]",
    rows: int,
    seed: int = 20261016,
) -> "tuple[list[str], list[list[str]]]":
    """A table of the given shapes, one column each, drawn in row order."""
    draw = random.Random(seed)
    header = list(shapes)
    body: "list[list[str]]" = []
    for _index in range(rows):
        body += [[shapes[name](draw) for name in header]]
    return header, body


WAREHOUSE_DEPARTMENTS = ("MED ONC", "CARDIOLOGY", "FAMILY MED", "EMERGENCY")


def keyed_export(rows: int, seed: int = 20261016) -> "tuple[list[str], list[list[str]]]":
    """The zoo critic's warehouse export (row 45): 60 patient keys beside `-1`, about 330 rows a key at 20,000."""
    draw = random.Random(seed)
    body: "list[list[str]]" = []
    for index in range(rows):
        key = "-1" if draw.random() < 0.02 else f"{draw.randint(100000, 100059)}"
        body += [[f"{9000000 + index}", key, WAREHOUSE_DEPARTMENTS[draw.randint(0, 3)]]]
    return ["EncounterKey", "patient_key", "department"], body


def keys_in_sequence(
    rows: int,
    count: int = 60,
    figures: int = 3,
    person: bool = False,
    seed: int = 20261028,
    placeholder: str = "-1",
    share: float = 0.02,
) -> "tuple[list[str], list[list[str]]]":
    """Lane GG skeptic 1's k60f3m (and, with ``person``, k60f3mp): patient keys in sequence beside `-1`.

    ``count`` keys of ``figures`` figures from ``10 ** (figures - 1)``,
    a warehouse key's `-1` on 2 % of rows, about 330 rows a key at 20,000; with
    ``person`` a declared person column `patient` of 2,500 people beside
    them. Its verify's k60f3m99 and k60f3m40 (repair 2, LANE GG RULINGS 3
    (1)) write ``placeholder`` `-99`, or `-1` on a ``share`` of 40 %.
    """
    draw = random.Random(seed)
    keys = [f"{10 ** (figures - 1) + index}" for index in range(count)]
    header = ["EncounterKey", "patient_key", "department"] + (["patient"] if person else [])
    body: "list[list[str]]" = []
    for index in range(rows):
        key = placeholder if draw.random() < share else keys[draw.randrange(count)]
        row = [f"{9000000 + index}", key, WAREHOUSE_DEPARTMENTS[draw.randrange(4)]]
        if person:
            row += [f"M{draw.randrange(2500):07d}"]
        body += [row]
    return header, body


def beside_a_key(rows: int, seed: int = 20261028) -> "tuple[list[str], list[list[str]]]":
    """Lane GG skeptic 1's `uc`: a score of 1 to 5 beside -99 and a `7` on 5 rows, beside 60 patient keys."""
    draw = random.Random(seed)
    keys = [f"{100000 + index}" for index in range(60)]
    rare = set(draw.sample(range(rows), 5))
    body: "list[list[str]]" = []
    for index in range(rows):
        score = "7" if index in rare else ("-99" if draw.random() < 0.08 else f"{draw.randint(1, 5)}")
        body += [[f"{9000000 + index}", keys[draw.randrange(60)], score]]
    return ["EncounterKey", "patient_key", "score"], body


def keys_beside_placeholders(
    rows: int, seed: int = 20261029, plain: bool = False
) -> "tuple[list[str], list[list[str]]]":
    """Lane GG verify's k60f3m99 and k60f3m40 in one table (repair 2, LANE GG RULINGS 3 (1)).

    `patient_key`: sixty three-figure keys in sequence beside `-99`
    on 2 % of rows; `PatientKeyB`: the same keys beside `-1` on 40 %.
    With ``plain``, skeptic 1's k60f3m beside them, `PatientKeyC`: the
    same keys beside `-1` on 2 %, drawn apart so the two columns before
    it keep their cells (the gate's one table; the KPI driver reads the
    two). And `PatientKeyD`, the lane's verify 2's `s1` (batch 4m's
    merge, AT GG'S MERGE (3) 1): sixty SIX-figure keys 100000 to 100059
    beside `-1` on 2 % and `-9999` on 2 %, whose `-9999` only the width
    route's second set-aside reads as a placeholder, drawn apart too.
    """
    draw = random.Random(seed)
    aside = random.Random(seed + 1)
    seams = random.Random(seed + 2)
    keys = [f"{100 + index}" for index in range(60)]
    wide = [f"{100000 + index}" for index in range(60)]
    body: "list[list[str]]" = []
    for index in range(rows):
        first = "-99" if draw.random() < 0.02 else keys[draw.randrange(60)]
        second = "-1" if draw.random() < 0.4 else keys[draw.randrange(60)]
        row = [f"{9000000 + index}", first, second, WAREHOUSE_DEPARTMENTS[draw.randrange(4)]]
        if plain:
            row += ["-1" if aside.random() < 0.02 else keys[aside.randrange(60)]]
            chance = seams.random()
            row += ["-1" if chance < 0.02 else "-9999" if chance < 0.04 else wide[seams.randrange(60)]]
        body += [row]
    header = ["EncounterKey", "patient_key", "PatientKeyB", "department"]
    return header + (["PatientKeyC", "PatientKeyD"] if plain else []), body


# REPAIR 2 (the orchestrator's LANE GG RULINGS 3, its verify's item 1 and
# Codex's review): a number on ONE cell standing at an edge of a published
# empty stretch -- a days' supply's `13` and `83`, a Likert score's stray
# `-77` between `-98` and `-44`, a potassium's `-50` between `-99` and 3.0.
def _likert_two_codes(draw: random.Random) -> str:
    chance = draw.random()
    if chance < 0.04:
        return "-98"
    if chance < 0.07:
        return "-44"
    return f"{draw.choice((1, 2, 2, 3, 3, 3, 4, 4, 5))}"


EDGES: "dict[str, typing.Callable[[random.Random], str]]" = {
    "days_edge": _weighted(DAYS),
    "likert_edge": _likert_two_codes,
    "k_edge": _lab(4.2, 0.35, 3.0, 5.6, "-99", 0.03, 1),
}
EDGE_STRAYS = {"days_edge": ("13", "83"), "likert_edge": ("-77",), "k_edge": ("-50",)}


def edge_strays(rows: int, seed: int = 20261029) -> "tuple[list[str], list[list[str]]]":
    """The three columns of `EDGES`, each with its strays of `EDGE_STRAYS` on one cell apiece."""
    header, body = table(EDGES, rows, seed)
    spots = random.Random(seed + 1).sample(range(rows), 8)
    for name in header:
        for stray in EDGE_STRAYS[name]:
            body[spots.pop()][header.index(name)] = stray
    return header, body


def pulse(rows: int) -> "tuple[list[str], list[list[str]]]":
    """Codex's item 2: a pulse cycling through 99 to 159, no gap, no placeholder."""
    return ["pulse"], [[f"{99 + index % 61}"] for index in range(rows)]


# Codex's item 3: seven spellings in three written forms, every one repeated.
FORMS = (("-99.00", 3663), ("1.0", 1595), ("2", 3689), ("3.0", 2564), ("4.00", 1132), ("5.0", 1606), ("6", 5751))


def counted(pairs: "tuple[tuple[str, int], ...]", seed: int = 20261029) -> "tuple[list[str], list[list[str]]]":
    """A column `score` holding each spelling as many times as given, in a seeded order."""
    cells = [text for text, held in pairs for _each in range(held)]
    random.Random(seed).shuffle(cells)
    return ["score"], [[cell] for cell in cells]


def mode_room(each: int) -> "tuple[list[str], list[list[str]]]":
    """Codex's item 4: `-100`, `-99` and 1 to 98, ``each`` cells apiece, beside one `50.5`."""
    pairs = tuple((f"{value}", each) for value in [-100, -99] + list(range(1, 99))) + (("50.5", 1),)
    return counted(pairs)


def one_patients_value(people: int = 1000, each: int = 20) -> "tuple[list[str], list[list[str]]]":
    """Codex's item 5: ``people`` declared patients, ``each`` rows apiece, a score cycling
    through -99 and 1 to 5, except the last patient's, `7` on every row."""
    cycle = ("-99", "1", "2", "3", "4", "5")
    body: "list[list[str]]" = []
    for person in range(people):
        for row in range(each):
            score = "7" if person == people - 1 else cycle[(person * each + row) % len(cycle)]
            body += [[f"P{person:05d}", score]]
    return ["patient", "score"], body


def starved(block: "dict[str, object]", real: "list[str]", twin: "list[str]", floor: int = 11) -> "list[str]":
    """The share measure (the statistics skeptic's item 1 (d)), linear in the cells.

    The listed values held by ``floor`` real cells or more, outside the
    published tails, that the twin writes on fewer than a quarter of their
    real count.
    """
    listed = block["few_values"] if isinstance(block.get("few_values"), list) else []
    tails = block["tails"] if isinstance(block.get("tails"), dict) else {}
    ladder: "dict[str, object]" = {}
    for key in ("percentiles", "percentiles_between"):
        part = block.get(key)
        if isinstance(part, dict):
            ladder.update(part)
    names = {0: "min", 100: "max"}

    def rung(side: str) -> "float | None":
        found = tails.get(side) if isinstance(tails, dict) else None
        if not isinstance(found, dict):
            return None
        percent = int(found["percent"])
        stood = ladder.get(names.get(percent, f"p{percent:02d}"))
        return float(stood) if isinstance(stood, (int, float)) else None

    low, high = rung("low"), rung("high")
    real_count = collections.Counter(real)
    twin_count = collections.Counter(twin)
    found_starved: "list[str]" = []
    for text in listed:  # type: ignore[union-attr]
        value = float(text)
        if (low is not None and value <= low) or (high is not None and value >= high):
            continue
        if real_count[text] >= floor and 4 * twin_count[text] < real_count[text]:
            found_starved += [text]
    return found_starved


def total_variation(real: "list[str]", twin: "list[str]") -> float:
    """Half the summed absolute gap between the two columns' shares of each spelling."""
    real_count = collections.Counter(real)
    twin_count = collections.Counter(twin)
    return sum(abs(real_count[key] / len(real) - twin_count[key] / len(twin)) for key in set(real_count) | set(twin_count)) / 2


def column_keys_shown(folder: pathlib.Path, keys: "set[float]", column: str) -> int:
    """Real keys printed in a column's own facts: its block, its questions and every text line naming it.

    A linear counter, as `keys_shown`, read where the column's values
    could stand: its block in the description, its entries in the
    questions file, and the lines of the written text files that name the
    column. Two- and three-figure keys collide with the numbers every
    file holds for other reasons -- `100 rows` in the floor's sentence,
    the declared person column's census of repetition -- which are no
    value of the column.
    """
    texts: "list[str]" = []
    document = json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))
    for block in document["columns"]:
        if block["name"] == column:
            texts += [json.dumps(block)]
    questions = folder / "t-questions.json"
    if questions.is_file():
        asked = json.loads(questions.read_text(encoding="utf-8"))
        for key in ("about_your_file", "asked"):
            texts += [json.dumps(one) for one in (asked.get(key) or []) if isinstance(one, dict) and one.get("column") == column]
        checklist = asked.get("checklist") or {}
        texts += [json.dumps(one) for one in (checklist.get("columns") or []) if isinstance(one, dict) and one.get("column") == column]
    for path in sorted(folder.iterdir()):
        if path.suffix == ".txt":
            texts += [line for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if column in line]
    shown: "set[float]" = set()
    for text in texts:
        for token in re.findall(r"-?\d+(?:\.\d+)?", text):
            if float(token) in keys:
                shown.add(float(token))
    return len(shown)


def number(text: str) -> "float | None":
    try:
        return float(text)
    except ValueError:
        return None


def faults(
    block: "dict[str, object]",
    real: "list[str]",
    twin: "list[str]",
    quantile: "typing.Callable[[list[float], int, int], float]",
) -> "dict[str, int]":
    """K-HZ-12's counter on one column, linear in its cells.

    Off a published block as the description file holds it, so the same
    counter reads a tree that publishes `few_values` and one that does
    not: `levels_lost`, real numbers no twin cell holds; `cells_in_gap`,
    twin cells strictly inside a published empty stretch;
    `cells_off_list`, twin cells written as a number but not as one of
    the published `few_values` -- or, where none is published, as one of
    the real column's own spellings (`-99.0` beside `-99` is off it);
    `mode_missed`, one where the twin's count at the published mode is
    not `mode_count`; and `rungs_off`, the published rungs the twin's own
    type-7 ladder does not stand on (``quantile`` is the producer's).
    """
    real_text = collections.Counter(real)
    real_numbers: "dict[float, int]" = collections.Counter()
    for text, count in real_text.items():
        found = number(text)
        if found is not None:
            real_numbers[found] += count
    twin_text = collections.Counter(twin)
    twin_numbers: "dict[float, int]" = collections.Counter()
    for text, count in twin_text.items():
        found = number(text)
        if found is not None:
            twin_numbers[found] += count
    published = block["few_values"] if "few_values" in block else None
    listed = set(published) if isinstance(published, list) and published else set(real_text)
    edges = block["empty_edges"] if isinstance(block.get("empty_edges"), list) else []
    in_gap = 0
    for value, count in twin_numbers.items():
        for below, above in edges:  # type: ignore[union-attr]
            if below < value < above:
                in_gap = in_gap + count
    mode = block.get("mode")
    mode_missed = 0
    if isinstance(mode, (int, float)) and twin_numbers.get(float(mode), 0) != block.get("mode_count"):
        mode_missed = 1
    ordered = sorted(value for value, count in twin_numbers.items() for _each in range(count))
    rungs: "dict[str, object]" = {}
    for key in ("percentiles", "percentiles_between"):
        part = block.get(key)
        if isinstance(part, dict):
            rungs.update(part)
    rungs_off = 0
    for name, rung in rungs.items():
        if not isinstance(rung, (int, float)) or not ordered:
            continue
        percent = 0 if name == "min" else 100 if name == "max" else int(name[1:])
        if quantile(ordered, percent, 100) != rung:
            rungs_off = rungs_off + 1
    return {
        "levels_lost": sum(1 for value in real_numbers if value not in twin_numbers),
        "cells_in_gap": in_gap,
        "cells_off_list": sum(
            count for text, count in twin_text.items() if number(text) is not None and text not in listed
        ),
        "mode_missed": mode_missed,
        "rungs_off": rungs_off,
    }


def quiet(main: "typing.Callable[..., int]", arguments: "list[str]", **switches: object) -> int:
    """One synthtwin command, its output kept off the screen."""
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return main(arguments, **switches)


def answered(
    main: "typing.Callable[..., int]",
    folder: pathlib.Path,
    source: pathlib.Path,
    answers: "dict[str, str]",
) -> None:
    """Every round of the questions file answered from ``answers``, `no` to any Safe Harbor question.

    As the zoo's general answers do (`health_zoo.answer_generally`): a
    column the person knows as anything but a record number or a place
    names nobody, so `no`.
    """
    questions = folder / f"{source.stem}-questions.json"
    for _round in range(4):
        if not questions.is_file():
            return
        document = json.loads(questions.read_text(encoding="utf-8"))
        entries: "list[dict[str, object]]" = []
        for key in ("about_your_file", "asked"):
            entries += [one for one in (document.get(key) or []) if isinstance(one, dict) and "answers_you_can_give" in one]
        checklist = document.get("checklist") or {}
        entries += [one for one in (checklist.get("columns") or []) if isinstance(one, dict) and "answers_you_can_give" in one]
        changed = False
        for entry in entries:
            offered = [f"{choice.get('answer')}" for choice in entry["answers_you_can_give"]]  # type: ignore[union-attr]
            given = ""
            for choice in (answers.get(f"{entry.get('column', '')}", ""), "no"):
                if choice and choice in offered:
                    given = choice
                    break
            if entry.get("your_answer", "") != given:
                changed = True
            entry["your_answer"] = given
        questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
        code = quiet(main, ["profile", f"{source}", "--replace", "--answers", f"{questions}"])
        assert code in (0, 3), code
        if not changed:
            return


def keys_shown(folder: pathlib.Path, keys: "set[float]") -> int:
    """Real keys printed in any file the commands wrote beside the table (a linear counter)."""
    shown: "set[float]" = set()
    for path in sorted(folder.iterdir()):
        if path.suffix in (".csv", ".xlsx"):
            continue
        for token in re.findall(r"-?\d+(?:\.\d+)?", path.read_text(encoding="utf-8", errors="replace")):
            value = float(token)
            if value in keys:
                shown.add(value)
    return len(shown)
