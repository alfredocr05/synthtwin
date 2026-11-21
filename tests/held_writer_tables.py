"""Invented tables for the held writer's time (plan P4-D490, lane HB3-b part a).

Shared by `tests/test_held_writer_time.py` (the gate file's one
20,000-row case) and `tools/measurements/kpi_held_writer_time.py`
(ledger K-HZ-40), so the gate and the ledger measure the same tables
the same way. Every value here is made up from the short word lists
below; nothing is read from anywhere.

THE EXAM TABLE (`exam_rows`): a person column, an exam column and a
score. The exam column holds 120 names, each a two-capital code, a body
part and, on half of them, the words ` WO CONTRAST` -- fourteen layouts
in all (seven letter shapes of the body parts, each with and without the
two words). How often each name appears is the column's spread:

- ``drawn``: every row draws a name uniformly at random, so each name
  holds about rows / 120 rows and the counts spread over many sizes;
- ``equal``: the names in turn, so every count is the same or one more;
- ``long-tailed``: every row draws a name with weight 1 / (rank + 1).

One rare name stands on ``rare_people`` people, eight rows each, so a
column beside a person column is read as one whose rare levels few
people hold. The person column names ``rows // 20`` people (1,000 at
20,000 rows), each on every ``rows // 20``-th row.

THE HELD LIST (`held_list_rows`): one to three of 40 invented keys --
the letter R and six figures -- a cell, joined by a semicolon, a comma
or a vertical bar, beside a score.

THE NAMES TABLE (`names_rows`): a person column and a surname column of
``values`` invented surnames built from syllables, drawn with weight
1 / (rank + 1), beside a score.

THE BLOCKS TABLE (`blocks_rows`): one label column of invented names in
blocks of twelve rows, eleven names and one small spelling a block, drawn
as lane CZ-F's table that LANE HB3-b RULINGS 2 measured (many layouts
each on a few counts).

THE RARE EXAM TABLE (`rare_exam_rows`): the exam table with 150 rare
names on 1 to 10 rows each beside the common ones, whose exact walk sets
the layout pass's meter (LANE HB3-b RULINGS 4 (1)). THE WIDE EXAM TABLE
(`wide_exam_rows`): 240 names of four tails in 27 layouts, drawn, beside
the few-people name (lane HB3-b's statistics check).

Each maker yields its rows one at a time, so a table of millions of
rows is written without being held; `write_csv` writes one.

THE GENERATED CHECKS' MAKERS. `allocation_question` draws one packing
question small enough for the walk of `generation._allotted_over` (2 to
60 groups of 1 to 300 rows, 1 to 16 counts in the first margin, one to
three margins, random permissions, with an answer or, a quarter of the
time, with one count moved by one row); `layout_question` draws one of
the layout pass's own shape (four classes, three bands and the layouts
beside "no named layout") at up to `rows_most` rows; `met_exactly` is
the independent recount both are judged by, written apart from the
product, and `off_by` the same recount's distance for an answer that
misses. `held_column` draws one column of record numbers -- word, code
or figure layouts, equal, uniform, long-tailed or spread counts, 1 to 40
values a layout and values on 1 to 10 rows -- `held_label_rows` one
table whose label column is held while its Safe Harbor question is open
or after `yes`, and `column_misses` names what a twin fails to hold.
"""

from __future__ import annotations

import csv
import pathlib
import random
import typing

EXAM_CODES = ("XR", "CT", "MR", "US", "NM", "PT")
# Seven letter shapes: three, four, five, six, seven and eight letters,
# and two words of five and three.
BODY_PARTS = (
    "ARM",
    "FOOT",
    "WRIST",
    "ELBOW",
    "THORAX",
    "SACRUM",
    "FOREARM",
    "CLAVICLE",
    "LOWER LEG",
    "UPPER ARM",
)
WITHOUT = " WO CONTRAST"
RARE_EXAM = "QX HAND SINGLE VIEW"
SPREADS = ("drawn", "equal", "long-tailed")

SYLLABLES = (
    "bar", "del", "fin", "gor", "hal", "ket", "lom", "mar", "nev", "pol",
    "quin", "ros", "sal", "tor", "ul", "ven", "wes", "yar", "zan", "cor",
)


def exam_names(count: int = 120) -> "list[str]":
    """The invented exam names, in a fixed order: code, body part, then the two words or none."""
    names = [
        f"{code} {part}{tail}"
        for code in EXAM_CODES
        for part in BODY_PARTS
        for tail in ("", WITHOUT)
    ]
    return names[:count]


def exam_rows(
    rows: int,
    names: int = 120,
    spread: str = "drawn",
    rare_people: int = 3,
    seed: int = 7,
) -> "tuple[list[str], typing.Iterator[list[str]]]":
    """The exam table's header and its rows, one at a time (see the module's text)."""
    if spread not in SPREADS:
        raise ValueError(f"spread must be one of {SPREADS}")
    chosen = exam_names(names)
    people = max(rows // 20, 50)
    draw = random.Random(seed)
    weights = [1.0 / (rank + 1) for rank in range(len(chosen))]
    rare = draw.sample(range(people), rare_people) if rare_people else []

    def made() -> "typing.Iterator[list[str]]":
        for row in range(rows - 8 * len(rare)):
            if spread == "equal":
                name = chosen[row % len(chosen)]
            elif spread == "long-tailed":
                name = draw.choices(chosen, weights)[0]
            else:
                name = draw.choice(chosen)
            yield [f"P{100000 + row % people}", name, f"{draw.gauss(50, 10):.1f}"]
        for person in rare:
            for _each in range(8):
                yield [f"P{100000 + person}", RARE_EXAM, f"{draw.gauss(50, 10):.1f}"]

    return ["person_id", "exam", "score"], made()


RARE_CODES = ("QA", "QB", "QC", "QD", "QE", "QF", "QG", "QH", "QJ", "QK", "QL", "QM", "QN", "QP", "QR")


def rare_exam_rows(rows: int, seed: int = 424242) -> "tuple[list[str], typing.Iterator[list[str]]]":
    """The exam table with 150 rare names beside the 120 common ones (LANE HB3-b RULINGS 4 (1)).

    The common names are drawn on the rows left over, as ``drawn``; 150
    rare names in the same layouts -- a code of the second list, a body
    part and, on about half, the two words -- stand on 1 to 10 rows each,
    every row a person drawn at random; and the few-people name stands on
    3 people, 8 rows each, so the column is held while its Safe Harbor
    question is open. Its walk packs it exactly at 20,000 rows in 6,514
    steps (lane HB3-b's skeptic 1).
    """
    draw = random.Random(seed)
    common = exam_names(120)
    rare: "list[str]" = []
    for code in RARE_CODES:
        for part in BODY_PARTS:
            rare += [f"{code} {part}" + (WITHOUT if draw.random() < 0.5 else "")]
    rare = list(dict.fromkeys(rare))[:150]
    people = max(rows // 20, 50)
    made: "list[list[str]]" = []
    for name in rare:
        for _each in range(draw.randint(1, 10)):
            made += [[f"P{100000 + draw.randrange(people)}", name, f"{draw.gauss(50, 10):.1f}"]]
    for person in draw.sample(range(people), 3):
        for _each in range(8):
            made += [[f"P{100000 + person}", RARE_EXAM, f"{draw.gauss(50, 10):.1f}"]]
    while len(made) < rows:
        index = len(made)
        made += [[f"P{100000 + index % people}", draw.choice(common), f"{draw.gauss(50, 10):.1f}"]]
    draw.shuffle(made)
    return ["person_id", "exam", "score"], iter(made)


WIDE_CODES = ("XR", "CT", "MR", "US", "NM", "PT", "DX", "FL", "IR", "BD")
WIDE_TAILS = ("", " WO CONTRAST", " W CONTRAST", " BILATERAL")


def wide_exam_rows(
    rows: int, names: int = 240, spread: str = "drawn", seed: int = 7
) -> "tuple[list[str], typing.Iterator[list[str]]]":
    """240 invented exam names in 27 layouts beside the few-people name (lane HB3-b's statistics check).

    The names are a code of ten, a body part and one of four tails, in a
    fixed shuffled order; ``drawn`` draws each row's name uniformly,
    ``two-level`` every other name three times as often, ``long-tailed``
    with weight 1 / (rank + 1). The few-people name stands on 3 people, 8
    rows each, so the column is held while its Safe Harbor question is
    open.
    """
    made_names = [f"{code} {part}{tail}" for tail in WIDE_TAILS for code in WIDE_CODES for part in BODY_PARTS]
    random.Random(3).shuffle(made_names)
    chosen = made_names[:names]
    people = max(rows // 20, 50)
    draw = random.Random(seed)
    if spread == "long-tailed":
        weights = [1.0 / (rank + 1) for rank in range(len(chosen))]
    elif spread == "two-level":
        weights = [3.0 if rank % 2 == 0 else 1.0 for rank in range(len(chosen))]
    else:
        weights = [1.0 for _each in chosen]
    cumulative: "list[float]" = []
    total = 0.0
    for weight in weights:
        total = total + weight
        cumulative += [total]
    rare = draw.sample(range(people), 3)

    def made() -> "typing.Iterator[list[str]]":
        for row in range(rows - 24):
            name = draw.choices(chosen, cum_weights=cumulative)[0]
            yield [f"P{100000 + row % people}", name, f"{draw.gauss(50, 10):.1f}"]
        for person in rare:
            for _each in range(8):
                yield [f"P{100000 + person}", RARE_EXAM, f"{draw.gauss(50, 10):.1f}"]

    return ["person_id", "exam", "score"], made()


def held_list_rows(rows: int, seed: int = 5) -> "tuple[list[str], typing.Iterator[list[str]]]":
    """The held list's header and its rows, one at a time (see the module's text)."""
    draw = random.Random(seed)
    keys: "list[str]" = []
    while len(keys) < 40:
        key = f"R{draw.randint(100000, 999999)}"
        if key not in keys:
            keys += [key]

    def made() -> "typing.Iterator[list[str]]":
        for _row in range(rows):
            listed = draw.sample(keys, draw.randint(1, 3))
            joiner = (";", ",", "|")[draw.randrange(3)]
            yield [joiner.join(listed), f"{draw.uniform(3, 150):.1f}"]

    return ["registers", "score"], made()


def surnames(values: int, seed: int = 11) -> "list[str]":
    """``values`` different invented surnames of two to four syllables, in a fixed order."""
    draw = random.Random(seed)
    made: "dict[str, int]" = {}
    while len(made) < values:
        parts = draw.randint(2, 4)
        word = "".join(draw.choice(SYLLABLES) for _each in range(parts))
        made[word[0].upper() + word[1:]] = 1
    return list(made)


def names_rows(
    rows: int, values: int = 2000, seed: int = 11
) -> "tuple[list[str], typing.Iterator[list[str]]]":
    """The names table's header and its rows, one at a time (see the module's text)."""
    chosen = surnames(values, seed)
    people = max(rows // 20, 50)
    draw = random.Random(seed + 1)
    weights = [1.0 / (rank + 1) for rank in range(len(chosen))]
    cumulative: "list[float]" = []
    total = 0.0
    for weight in weights:
        total = total + weight
        cumulative += [total]

    def made() -> "typing.Iterator[list[str]]":
        for row in range(rows):
            name = draw.choices(chosen, cum_weights=cumulative)[0]
            yield [f"P{100000 + row % people}", name, f"{draw.gauss(50, 10):.1f}"]

    return ["person_id", "surname", "score"], made()


# THE BLOCKS TABLE'S SYLLABLES: an opening, a vowel and an ending, each
# drawn, so the made-up names take many lengths and so many layouts.
ONSETS = (
    "br", "ch", "dr", "fl", "gr", "kh", "pl", "qu", "sh", "st", "th", "tr", "v", "w", "y", "z", "j", "n", "m",
    "h", "cr", "sl", "sn", "bl",
)
VOWELS = ("a", "e", "i", "o", "u", "ai", "ou", "ea", "io", "ue")
ENDINGS = ("", "nd", "rk", "ss", "lt", "mb", "x", "ck", "rn", "sh", "ft", "")


def _syllables(draw: random.Random, count: int) -> str:
    """``count`` made-up syllables run together."""
    return "".join(draw.choice(ONSETS) + draw.choice(VOWELS) + draw.choice(ENDINGS) for _each in range(count))


def blocks_rows(rows: int, seed: str = "czfv-alias") -> "tuple[list[str], typing.Iterator[list[str]]]":
    """A label column of made-up names in blocks of twelve rows (LANE HB3-b RULINGS 2's measured cliff).

    Each block opens with one of about a third as many small spellings
    (lower case) and holds eleven rows of the names, every name on eleven
    rows in all: ``rows // 12`` names of two or three syllables, a comma
    and one or two more, drawn as lane CZ-F's measured table drew them
    (the same syllables, seed and draws), so at 49,152 rows the table is
    that one: 4,096 names on exactly 11 rows beside 1,400 small spellings
    on 2 or 3 rows, 5,496 values in about 244 letter layouts -- a census of
    many layouts each on a few counts, which took 1,670.2 CPU seconds to
    generate on the base of lane HB3-b and 1.2 published. A small spelling
    that folds onto a name is left out (a pair that folds together owes a
    fold-collision partner, and the layout pass steps aside for such a
    column, method G9.6); none does at 49,152 rows.
    """
    draw = random.Random(seed)
    blocks = rows // 12
    wanted_smalls = max(1, (blocks * 1400) // 4096)

    def family() -> str:
        return _syllables(draw, draw.choice((2, 3, 3))).capitalize()

    def given() -> str:
        return _syllables(draw, draw.choice((1, 2))).capitalize()

    named = list(dict.fromkeys(f"{family()}, {given()}" for _each in range(blocks + (blocks * 304) // 4096)))
    while len(named) < blocks:
        named = list(dict.fromkeys(named + [f"{family()}, {given()}"]))
    named = named[:blocks]
    drawn_smalls = list(dict.fromkeys(
        f"{family().lower()}, {given().lower()}" for _each in range(wanted_smalls + wanted_smalls // 14)
    ))[:wanted_smalls]
    folded = {name.casefold() for name in named}
    small = [spelling for spelling in drawn_smalls if spelling.casefold() not in folded] or ["zz, zz"]
    order = list(range(blocks * 11))
    random.Random(6).shuffle(order)

    def made() -> "typing.Iterator[list[str]]":
        cursor = 0
        for block in range(blocks):
            yield [small[block % len(small)]]
            for _each in range(11):
                yield [named[order[cursor] % blocks]]
                cursor = cursor + 1

    return ["label_text"], made()


def write_csv(
    path: pathlib.Path, header: "list[str]", rows: "typing.Iterable[list[str]]"
) -> int:
    """Write one table as a CSV file and return how many rows it holds."""
    written = 0
    with open(path, "w", newline="", encoding="utf-8") as handle:
        out = csv.writer(handle)
        out.writerow(header)
        for row in rows:
            out.writerow(row)
            written = written + 1
    return written


# -- the generated checks' makers (plan P4-D490, A3) ------------------------


def grid(parts: "list[int]") -> "tuple[int, list[list[int]]]":
    """The cells of a grid over margins of ``parts`` counts, and each cell's count in each margin."""
    cells = 1
    for count in parts:
        cells = cells * count
    part_of: "list[list[int]]" = []
    for margin in range(len(parts)):
        stride = 1
        for later in parts[margin + 1:]:
            stride = stride * later
        part_of += [[(cell // stride) % parts[margin] for cell in range(cells)]]
    return cells, part_of


def _sizes(draw: random.Random, groups: int, most: int) -> "list[int]":
    """``groups`` sizes of 1 to ``most`` rows, equal, uniform, long-tailed or spread around a centre."""
    shape = draw.choice(("equal", "uniform", "long-tailed", "spread"))
    if shape == "equal":
        return [draw.randint(1, most)] * groups
    if shape == "long-tailed":
        bend = draw.uniform(0.5, 1.5)
        return [max(1, int(most / (rank + 1) ** bend)) for rank in range(groups)]
    if shape == "spread":
        centre = draw.randint(max(1, most // 15), most)
        return [max(1, min(most, int(draw.gauss(centre, centre * 0.06)))) for _each in range(groups)]
    return [draw.randint(1, most) for _each in range(groups)]


def _margins_of(
    sizes: "list[int]", parts: "list[int]", part_of: "list[list[int]]", witness: "list[int]"
) -> "list[tuple[list[int], list[int]]]":
    """Every margin's counts as an assignment of the groups to cells makes them."""
    margins: "list[tuple[list[int], list[int]]]" = []
    for margin in range(len(parts)):
        quotas = [0] * parts[margin]
        for place in range(len(sizes)):
            quotas[part_of[margin][witness[place]]] += sizes[place]
        margins += [(quotas, part_of[margin])]
    return margins


def _moved_by_one(draw: random.Random, margins: "list[tuple[list[int], list[int]]]") -> None:
    """One row moved from one count of one margin to another: the question may then have no answer."""
    quotas = margins[draw.randrange(len(margins))][0]
    owing = [part for part in range(len(quotas)) if quotas[part] > 0]
    if len(quotas) > 1 and owing:
        taken = draw.choice(owing)
        given = draw.choice([part for part in range(len(quotas)) if part != taken])
        quotas[taken] -= 1
        quotas[given] += 1


def allocation_question(
    draw: random.Random,
) -> "tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int], bool]":
    """One packing question small enough for the walk (see the module's text), and whether one margin binds."""
    shaped = draw.random() < 0.35
    if shaped:
        parts = [4, 3, draw.randint(1, 16) + 1]
    else:
        parts = [draw.randint(1, 16)] + [draw.randint(1, 3) for _each in range(draw.choice((0, 1, 2)))]
    cells, part_of = grid(parts)
    groups = draw.randint(2, 60)
    sizes = _sizes(draw, groups, 300)
    if shaped:
        live = [cell for cell in range(cells) if part_of[0][cell] == 3 and part_of[1][cell] == 2]
        witness = [draw.choice(live) for _each in range(groups)]
    else:
        witness = [draw.randrange(cells) for _each in range(groups)]
    margins = _margins_of(sizes, parts, part_of, witness)
    density = draw.choice((0.0, 0.3, 1.0))
    allowed: "list[int]" = []
    for place in range(groups):
        bits = 1 << witness[place]
        for cell in range(cells):
            if draw.random() < density:
                bits |= 1 << cell
        allowed += [bits]
    if draw.random() < 0.25:
        _moved_by_one(draw, margins)
    return tuple(sizes), margins, allowed, shaped


def layout_question(
    draw: random.Random, rows_most: int
) -> "tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int], bool]":
    """One question of the layout pass's shape: one binding margin of 2 to 40 layouts, up to ``rows_most`` rows.

    Every group may take every layout, or each a random half of them
    beside its own; a fifth of the questions have one count moved by one
    row. Returns the question and whether it was drawn with an answer.
    """
    layouts = draw.randint(2, 40)
    parts = [4, 3, layouts + 1]
    cells, part_of = grid(parts)
    live = [cell for cell in range(cells) if part_of[0][cell] == 3 and part_of[1][cell] == 2]
    groups = draw.randint(layouts, max(layouts, min(1500, rows_most // 20)))
    sizes = _sizes(draw, groups, max(1, (2 * rows_most) // groups))
    witness = [draw.choice(live[:-1]) for _each in range(groups)]
    margins = _margins_of(sizes, parts, part_of, witness)
    half = draw.random() < 0.5
    allowed: "list[int]" = []
    for place in range(groups):
        bits = 1 << witness[place]
        for cell in live:
            if not half or draw.random() < 0.5:
                bits |= 1 << cell
        allowed += [bits]
    answered = True
    if draw.random() < 0.2:
        _moved_by_one(draw, margins)
        answered = False
    return tuple(sizes), margins, allowed, answered


def met_exactly(
    groups: "tuple[int, ...]",
    margins: "list[tuple[list[int], list[int]]]",
    allowed: "list[int]",
    chosen: "list[int]",
) -> bool:
    """The independent recount: every group in a cell it may take, every count of every margin met exactly."""
    return off_by(groups, margins, allowed, chosen) == 0


def off_by(
    groups: "tuple[int, ...]",
    margins: "list[tuple[list[int], list[int]]]",
    allowed: "list[int]",
    chosen: "list[int]",
) -> int:
    """The same recount's distance: the rows by which every count of every margin is missed, summed; -1 where a group is not in one cell it may take."""
    if len(chosen) != len(groups):
        return -1
    if any(cell < 0 or not (allowed[place] >> cell) & 1 for place, cell in enumerate(chosen)):
        return -1
    off = 0
    for quotas, part_of in margins:
        found = [0] * len(quotas)
        for place, cell in enumerate(chosen):
            found[part_of[cell]] += groups[place]
        off += sum(abs(found[part] - quotas[part]) for part in range(len(quotas)))
    return off


WORD_HEADS = ("AB", "CD", "EF", "GH", "JK", "LM")
WORD_TAILS = ("RUN", "WALK", "STAND", "LIFT", "PRESS", "TURN", "REACH", "CARRY", "PUSH UP")
CODE_LETTERS = "BCDFGHJKLMNPQRSTVWXZ"


def held_column(draw: random.Random) -> "tuple[str, list[str]]":
    """One invented column of record numbers and its cells (see the module's text).

    Word layouts (two capitals and a word, some two words), code layouts
    (capitals and figures) or figure layouts (four to nine figures); 2 to
    6 layouts of 1 to 40 values each, counts equal, uniform, long-tailed
    or spread; and 0 to 6 values held by 1 to 10 rows each, the rare
    values a twin cell must never equal.
    """
    family = draw.choice(("word", "code", "figure"))
    values: "list[str]" = []
    for layout in range(draw.randint(2, 6)):
        many = draw.randint(1, 40)
        for index in range(many):
            if family == "word":
                head = WORD_HEADS[(layout + index) % len(WORD_HEADS)]
                tail = WORD_TAILS[layout % len(WORD_TAILS)]
                values += [f"{head} {tail}" if index < len(WORD_HEADS) else f"{head}{index} {tail}"]
            elif family == "code":
                letters = "".join(draw.choice(CODE_LETTERS) for _each in range(1 + layout % 3))
                values += [letters + str(draw.randint(10 ** (2 + layout % 4), 10 ** (3 + layout % 4) - 1))]
            else:
                values += [str(draw.randint(10 ** (3 + layout), 10 ** (4 + layout) - 1))]
    values = list(dict.fromkeys(values))
    sizes = _sizes(draw, len(values), draw.choice((30, 120, 300)))
    sizes = [max(size, 11) for size in sizes]
    cells: "list[str]" = []
    for value, size in zip(values, sizes):
        cells += [value] * size
    for index in range(draw.randint(0, 6)):
        rare = f"{family[0].upper()}Q{index}{draw.randint(100, 999)}"
        cells += [rare] * draw.randint(1, 10)
    draw.shuffle(cells)
    return family, cells


def held_label_rows(draw: random.Random) -> "tuple[str, list[str], list[list[str]]]":
    """One invented table whose label column is held: its spread, its answer and its rows (see the module's text).

    A person column on 2,000 to 4,000 rows (one person every twentieth
    row), a label column of 20 to 120 names -- a code, a body part and
    one of four tails, as `wide_exam_rows` makes them -- drawn, equal,
    long-tailed or two-level, beside 0 to 30 rare names of a second list
    on 1 to 10 rows each and the few-people name on 3 people, so its Safe
    Harbor question is put; the answer is left open or `yes`.
    """
    spread = draw.choice(("drawn", "equal", "long-tailed", "two-level"))
    answer = draw.choice(("", "yes"))
    rows = draw.randint(2000, 4000)
    people = rows // 20
    made_names = [f"{code} {part}{tail}" for tail in WIDE_TAILS for code in WIDE_CODES for part in BODY_PARTS]
    draw.shuffle(made_names)
    chosen = made_names[: draw.randint(20, 120)]
    weights = [1.0 for _each in chosen]
    if spread == "long-tailed":
        weights = [1.0 / (rank + 1) for rank in range(len(chosen))]
    elif spread == "two-level":
        weights = [3.0 if rank % 2 == 0 else 1.0 for rank in range(len(chosen))]
    table: "list[list[str]]" = []
    rare_names = [f"{code} {part}" for code in RARE_CODES for part in BODY_PARTS]
    for name in draw.sample(rare_names, draw.randint(0, 30)):
        for _each in range(draw.randint(1, 10)):
            table += [[f"P{100000 + draw.randrange(people)}", name, f"{draw.gauss(50, 10):.1f}"]]
    for person in draw.sample(range(people), 3):
        for _each in range(8):
            table += [[f"P{100000 + person}", RARE_EXAM, f"{draw.gauss(50, 10):.1f}"]]
    while len(table) < rows:
        index = len(table)
        if spread == "equal":
            name = chosen[index % len(chosen)]
        else:
            name = draw.choices(chosen, weights)[0]
        table += [[f"P{100000 + index % people}", name, f"{draw.gauss(50, 10):.1f}"]]
    draw.shuffle(table)
    return spread, answer, table


def column_misses(
    real: "list[str]",
    twin: "list[str]",
    column: "typing.Any",
    filed: "dict[str, str]",
) -> "list[str]":
    """What a column's twin fails to hold of its description, each named; empty where nothing.

    ``column`` is the column's loaded description (`contract.ColumnBlock`
    of a record number), ``filed`` the twin's deviations of the column
    (fact to sentence). Read off the cells, by the product's own readers:
    every published layout at its count (in its window where a pool
    stands) or filed; the multiset of repeats; the counts of different
    values, raw and folded; the shortest and longest, unless a value was
    written wider than every real one (plan P4-D432, which the validator
    authorizes); and no twin cell equal -- exactly, folded or by the
    merged key -- to a real value 1 to 10 rows hold.
    """
    from synthtwin import parsing, taxonomy

    facts = column.facts
    misses: "list[str]" = []
    present = [cell for cell in twin if parsing.trimmed(cell)]
    census = taxonomy.layout_census(present, 1, len(set(present)))
    forms = dict(facts.layout_forms)
    pool = forms.get("(withheld)", 0)
    for layout, count in forms.items():
        if layout == "(withheld)":
            continue
        found = census.get(layout, 0)
        if not count <= found <= count + pool and f"layout_forms.{layout}" not in filed:
            misses += [f"layout {layout}: published {count}, written {found}, not filed"]
    counted: "dict[str, int]" = {}
    for cell in present:
        counted[cell] = counted.get(cell, 0) + 1
    repeats: "dict[int, int]" = {}
    for many in counted.values():
        repeats[many] = repeats.get(many, 0) + 1
    if repeats != {int(many): values for many, values in facts.n_distinct_by_occurrences.items()}:
        misses += ["the multiset of repeats"]
    if len(counted) != column.n_distinct:
        misses += [f"n_distinct {column.n_distinct} written {len(counted)}"]
    folded = {cell.casefold() for cell in counted}
    if len(folded) != column.n_distinct_folded and "n_distinct_folded" not in filed:
        misses += [f"n_distinct_folded {column.n_distinct_folded} written {len(folded)}"]
    wider = taxonomy.written_wider(facts.layout_exclusions, facts.layout_prefixes, present)
    if present and not wider and (min(len(cell) for cell in present), max(len(cell) for cell in present)) != (
        facts.min_length, facts.max_length
    ):
        misses += ["the shortest or longest length"]
    held: "dict[str, dict[str, int]]" = {"exact": {}, "folded": {}, "merged": {}}
    for cell in real:
        if not parsing.trimmed(cell):
            continue
        for kind, key in (("exact", cell), ("folded", cell.casefold()),
                          ("merged", str(parsing.merged_key(parsing.trimmed(cell))))):
            held[kind][key] = held[kind].get(key, 0) + 1
    for cell in present:
        for kind, key in (("exact", cell), ("folded", cell.casefold()),
                          ("merged", str(parsing.merged_key(parsing.trimmed(cell))))):
            if 1 <= held[kind].get(key, 0) <= 10:
                misses += [f"a twin cell equal ({kind}) to a value 1 to 10 rows hold"]
                break
    return misses

# THE CLIFF'S QUESTION: the first question the layout pass of the exam
# column (`exam_rows(20000)`, drawn, held unanswered) puts to the
# allocator, captured on the base 099671f1 -- 121 groups of 154 to 174
# rows, a class margin and an alphabet margin of one count each, and
# fourteen layout counts, every group free to take every one. The walk of
# `_allotted_over` passes 20,000 steps on it without an answer (38.8 CPU
# seconds, lane HB3-b's step 0).
CLIFF_GROUPS = (
    154, 155, 155, 155, 155, 155, 159, 159, 159, 159, 159, 159, 159, 159, 159, 159, 159, 159,
    159, 159, 159, 160, 160, 160, 160, 162, 162, 162, 162, 162, 163, 163, 163, 163, 163, 163,
    163, 163, 163, 164, 164, 164, 164, 164, 164, 164, 164, 164, 164, 164, 165, 165, 165, 165,
    165, 166, 166, 166, 166, 166, 166, 166, 166, 166, 166, 166, 166, 166, 166, 166, 166, 166,
    166, 166, 166, 167, 167, 167, 167, 167, 167, 167, 167, 168, 168, 168, 168, 168, 168, 168,
    168, 168, 168, 168, 168, 168, 168, 170, 170, 170, 170, 171, 171, 171, 171, 171, 171, 171,
    171, 173, 173, 173, 173, 174, 174, 174, 174, 174, 174, 174, 174,
)
CLIFF_COUNTS = (
    (0, 0, 0, 20000),
    (0, 0, 20000),
    (989, 1008, 1041, 1966, 2067, 1951, 1996, 1992, 2012, 958, 1024, 929, 1024, 1043),
)
# Every group's permitted cells, the same for each: the text class in the
# band outside the code alphabet, under every layout.
CLIFF_PERMITTED = 0xfffe00000020000000000800200000020008002000


def cliff_question() -> "tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int]]":
    """The cliff's question as `generation._allotted_over` takes it: groups, margins, permissions."""
    parts = [len(counts) for counts in CLIFF_COUNTS]
    _cells, part_of = grid(parts)
    margins = [(list(counts), part_of[place]) for place, counts in enumerate(CLIFF_COUNTS)]
    return CLIFF_GROUPS, margins, [CLIFF_PERMITTED] * len(CLIFF_GROUPS)


# THE WIDE COLUMN'S QUESTION (lane HB3-b's statistics check): the first
# question the layout pass of the wide exam column (`wide_exam_rows(20000,
# 240, "long-tailed")`, held unanswered) puts to the allocator, captured in
# lane HB3-b's repair 1 -- 241 groups of 69 to 97 rows (their sizes
# ascending, as runs of one size), a class margin and an alphabet margin of
# one count each, and 27 layout counts beside "no named layout", every
# group free to take every layout. An exact answer exists (that repair
# found one and recounted it), and the re-packing allocator stops 6 rows
# short of it: the third rung's question.
WIDE_RUNS = (
    (69, 1), (70, 1), (72, 2), (76, 3), (77, 2), (79, 6), (80, 17), (81, 27), (82, 57),
    (83, 32), (84, 27), (85, 31), (86, 12), (87, 8), (88, 10), (92, 2), (96, 2), (97, 1),
)
WIDE_COUNTS = (
    (0, 0, 0, 20000),
    (0, 0, 20000),
    (382, 184, 241, 322, 655, 289, 437, 687, 258, 704, 503, 2038, 3626, 433, 990, 658, 1713, 1686, 554, 166,
     144, 721, 338, 1052, 585, 174, 321, 139),
)
WIDE_PERMITTED = 0xfffffff80000000000000800000000000000000000800000080000000000000800000080000008000000


def wide_question() -> "tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int]]":
    """The wide column's question as `generation._allotted_over` takes it: groups, margins, permissions."""
    groups: "list[int]" = []
    for size, many in WIDE_RUNS:
        groups += [size] * many
    parts = [len(counts) for counts in WIDE_COUNTS]
    _cells, part_of = grid(parts)
    margins = [(list(counts), part_of[place]) for place, counts in enumerate(WIDE_COUNTS)]
    return tuple(groups), margins, [WIDE_PERMITTED] * len(groups)


# THE RARE COLUMN'S QUESTION (LANE HB3-b RULINGS 4 (1)): the first question the
# layout pass of the rare exam column (`rare_exam_rows(20000)`, held
# unanswered) puts to the allocator, captured in lane HB3-b's repair 1 -- 271
# groups of 71 to 77 rows (its census folded into seven classes, as runs of
# one size), a class margin and an alphabet margin of one count each and
# fourteen layout counts, every group free to take every layout, as the
# cliff's. The walk packs it exactly in 6,514 steps and 228,333 units of
# work; at the build's 604 steps it did not end, and the re-packing
# allocator stops 14 rows short of it.
RARE_RUNS = ((71, 10), (72, 24), (73, 84), (74, 70), (75, 62), (76, 17), (77, 4))
RARE_COUNTS = (
    (0, 0, 0, 20000),
    (0, 0, 20000),
    (1015, 983, 958, 1984, 1981, 2045, 1945, 2014, 2031, 992, 998, 971, 1046, 1037),
)


def rare_question() -> "tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int]]":
    """The rare column's question as `generation._allotted_over` takes it: groups, margins, permissions."""
    groups: "list[int]" = []
    for size, many in RARE_RUNS:
        groups += [size] * many
    parts = [len(counts) for counts in RARE_COUNTS]
    _cells, part_of = grid(parts)
    margins = [(list(counts), part_of[place]) for place, counts in enumerate(RARE_COUNTS)]
    return tuple(groups), margins, [CLIFF_PERMITTED] * len(groups)
