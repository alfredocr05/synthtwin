"""Held and unanswered columns written in their own valid layouts: the lane's hunt (plan P4-D442).

Shared by `tests/test_zoo_held_layouts.py` (the gate) and `tools/measurements/kpi_held_layouts.py`
(K-HZ-13's driver), so the gate and the ledger measure the same tables the same way.

THE SHAPES (`SHAPES`), each a table of one measured column beside a test and a value, gathered by
the orchestrator as 'CODES-1 part C' (planning-notes batch3-notes, items (1) to (16)): record
numbers beside `-1` and `-99` and their unheld pairs (the layout search beside a negative
placeholder, items (4) and (10)), a key exported as `100001.0` and whole years written `1932.0`
(items (8) and (13)), a telephone number opening `+` (item (4)), UIDs with no root and a held UID
(item (9)), the walk's persons (`pad_split`, a number beside its `.0`, a dotted pad: items (11) and
(15)), birth dates in mixed layouts and beside `UNKNOWN`, a column of two dates, three people's
`pending` (items (6), (7) and (2)), two-figure keys named as keys (item (14)) and quoted comma
lists of record numbers (item (12), at 600 rows, the internal smoke).

WHAT IS COUNTED (`run`): the three exits and the seconds of each step, the twin's present cells
that are no valid date in the source's own layouts (a date shape), off the UID grammar (a UID
shape), the real column's different persons -- merged keys (`parsing.merged_key`, the form
`profile.subject_keys` counts a person by) and values read as numbers -- against the twin's, the
twin cells equal to or merging with a real cell, and, in a list shape, the made-up keys inside list
cells whose merged key is a real key's. Every counter is linear in the cells: each real value and
each twin cell is read once, into a set.
"""

from __future__ import annotations

import contextlib
import csv
import datetime
import decimal
import io
import json
import pathlib
import random
import re
import time

from synthtwin import cli, parsing

import identifier_room_shapes as room
import unanswered_identifier_shapes as held_shapes

UID = re.compile(r"[012](\.(0|[1-9]\d*))+")
UID_AT_MOST = 64
SEED = 20261028
_TESTS = ("Sodium", "Potassium", "Glucose")


def _rows_with(cells: "list[str]", head: str, seed: int) -> "tuple[list[str], list[list[str]]]":
    """One measured column beside a test name and a value, as every shape here writes it."""
    draw = random.Random(seed)
    rows = [[cell, _TESTS[draw.randrange(3)], f"{draw.uniform(3, 150):.1f}"] for cell in cells]
    return [head, "test", "value"], rows


def _keys_beside(n: int, placeholder: str, share: int) -> "list[str]":
    """Record numbers of seven figures, three rows a person, `placeholder` on one row in ``share``."""
    return [placeholder if placeholder and k % share == 0 else f"{1000000 + k // 3}" for k in range(n)]


def _held_kind(kind: str, n: int) -> "list[str]":
    """A kind of `unanswered_identifier_shapes`' long tables (44 patients), its measured column."""
    import tempfile

    with tempfile.TemporaryDirectory() as scratch:
        path, _real = held_shapes.write_table(pathlib.Path(scratch), kind, n)
        with open(path, encoding="utf-8", newline="") as handle:
            table = list(csv.reader(handle))
    return [row[0] for row in table[1:]]


def _days(n: int, seed: int, share_unknown: float, mixed: bool) -> "list[str]":
    """Birth dates from 1930 to 1999: ISO, or ISO and US month-first mixed, beside `UNKNOWN` on a share."""
    draw = random.Random(seed)
    first = datetime.date(1930, 1, 1)
    cells: "list[str]" = []
    for _row in range(n):
        day = first + datetime.timedelta(days=draw.randrange(25567))
        if share_unknown and draw.random() < share_unknown:
            cells += ["UNKNOWN"]
        elif mixed and draw.random() >= 0.6:
            cells += [day.strftime("%m/%d/%Y")]
        else:
            cells += [day.isoformat()]
    return cells


def _days_beside(n: int, other: str) -> "list[str]":
    """Birth dates from 1930 to 1999, ISO on 60 % of rows and the layout ``other`` on 40 % (skeptic 1, item 4)."""
    draw = random.Random(4)
    first = datetime.date(1930, 1, 1)
    cells: "list[str]" = []
    for _row in range(n):
        day = first + datetime.timedelta(days=draw.randrange(25567))
        cells += [day.strftime(other) if draw.random() >= 0.6 else day.isoformat()]
    return cells


def _dates_beside_words(n: int) -> "list[str]":
    """CODES-1's verify, 'outside this lane' (LANE HB RULINGS 1, item (17)): two common dates, `pending`
    and `N/A` on 80 % of rows; rare dates of 2010 to 2023 and `note0` to `note299` on 20 %, read as labels."""
    draw = random.Random(7)
    common = ["2024-01-05", "2024-02-10", "pending", "N/A"]
    rare = [f"20{y:02d}-{mo:02d}-{d:02d}" for y in range(10, 24) for mo in range(1, 13) for d in (3, 17)]
    rare += [f"note{k}" for k in range(300)]
    return [draw.choice(common) if draw.random() > 0.2 else draw.choice(rare) for _row in range(n)]


def _two_ways(n: int, dashed: bool) -> "list[str]":
    """Skeptic 1, item 5: four rows a person, each row written two ways at random -- zero filled to nine
    figures or not (`001000007` beside `1000007`), or `P-` beside `P` -- one real person, two spellings."""
    draw = random.Random(5)
    cells: "list[str]" = []
    for row in range(n):
        key = 1000000 + 7 * (row // 4)
        if dashed:
            cells += [f"P-{key}" if draw.random() < 0.5 else f"P{key}"]
        else:
            cells += [f"{key:09d}" if draw.random() < 0.5 else f"{key}"]
    return cells


def _comma_lists(n: int, lettered: bool, mark: str = ",") -> "list[str]":
    """Skeptic 1, item 2: 4,000 record numbers (`1000000` to `1003999`, or `R100000` to `R103999`), one
    to three in a cell between commas (or ``mark``): read as free text, nothing published."""
    draw = random.Random(4000)
    keys = [f"R{100000 + k}" if lettered else f"{1000000 + k}" for k in range(4000)]
    return [mark.join(draw.sample(keys, 1 + draw.randrange(3))) for _row in range(n)]


_NOTE_WORDS = ("follow", "up", "in", "weeks", "seen", "by", "dr", "smith", "jones", "called", "patient", "no",
               "answer", "left", "message", "refill", "sent", "pharmacy", "labs", "ordered", "pending", "review")


def _keys_in_notes(n: int) -> "list[str]":
    """The verify of lane HB, finding 1: record numbers `1000000` upward, six rows a key, alone in every other
    cell of a column of notes (two to six words and a number below 100): read as free text."""
    draw = random.Random(17)
    cells: "list[str]" = []
    for k in range(n):
        if k % 2 == 0:
            cells += [f"{1000000 + k // 6}"]
        else:
            cells += [" ".join(draw.choice(_NOTE_WORDS) for _ in range(2 + draw.randrange(5))) + f" {draw.randrange(100)}"]
    return cells


def _keys_once(n: int) -> "list[str]":
    """The verify of lane HB, finding 1: linked order numbers `1000000` upward, each written ONCE, one to three
    a cell between commas (the keys never repeat, so the person question is not put): read as free text."""
    draw = random.Random(7)
    cells: "list[str]" = []
    after = 1000000
    for _row in range(n):
        many = 1 + draw.randrange(3)
        cells += [",".join(f"{after + k}" for k in range(many))]
        after = after + many
    return cells


def _random_lists(n: int, lettered: bool, mark: str = ",") -> "list[str]":
    """The verify of lane HB, finding 2: 4,000 keys `R` and six random figures, or 6,000 random keys of seven
    figures, one to three a cell between commas (rule 11 holds them as record numbers) or marks of a free text."""
    draw = random.Random(1 if lettered else 2)
    keys: "set[str]" = set()
    while len(keys) < (4000 if lettered else 6000):
        keys.add(f"R{draw.randint(100000, 999999)}" if lettered else f"{draw.randint(1000000, 9999999)}")
    ordered = sorted(keys)
    draw = random.Random(4000)
    return [mark.join(draw.sample(ordered, 1 + draw.randrange(3))) for _row in range(n)]


def _random_lists_two_widths(n: int) -> "list[str]":
    """Random keys `R` and five figures beside `R` and six, one to three a cell between commas: no figure opens
    off every key of both widths (Codex's review of lane HB, item 8, with no common opening)."""
    draw = random.Random(5)
    keys: "set[str]" = set()
    while len(keys) < 4000:
        keys.add(f"R{draw.randint(10000, 99999)}" if draw.randrange(2) else f"R{draw.randint(100000, 999999)}")
    ordered = sorted(keys)
    draw = random.Random(4000)
    return [",".join(draw.sample(ordered, 1 + draw.randrange(3))) for _row in range(n)]


def _two_dates(n: int) -> "list[str]":
    """One row a person: a vaccination day on every row but five, those five on the next day."""
    draw = random.Random(SEED)
    cells = ["2021-03-01"] * (n - 5) + ["2021-03-02"] * 5
    draw.shuffle(cells)
    return cells


def _pending(n: int) -> "list[str]":
    """Visit dates, ten a person; three people's first visit written `pending` (min_length 7 against 10)."""
    draw = random.Random(11)
    first = datetime.date(2022, 1, 1)
    cells: "list[str]" = []
    for row in range(n):
        person, visit = row // 10, row % 10
        cells += ["pending" if visit == 0 and person < 3 else
                  (first + datetime.timedelta(days=draw.randrange(730))).isoformat()]
    return cells


def _register_lists(n: int) -> "list[str]":
    """HX4's register lists as Codex built them: `R100000` to `R100039`, 40 singles, 240 pairs, 320 triples."""
    keys = [f"R{100000 + place}" for place in range(40)]
    cells = list(keys)
    for step in range(1, 7):
        cells += [f"{keys[i]},{keys[(i + step) % 40]}" for i in range(40)]
    for step in range(1, 9):
        cells += [f"{keys[i]},{keys[(i + step) % 40]},{keys[(i + step + 1) % 40]}" for i in range(40)]
    return [cells[k % len(cells)] for k in range(n)]


def _register_lists_mixed(n: int) -> "list[str]":
    """Lane HX4's `reglistmixR` (`tests/unanswered_identifier_shapes.py` on the merged line), drawn as it
    draws it: 40 keys `R` and six figures from the whole room, one to three a cell of 44 patients' rows,
    the mark `;`, `,` or `|` cell by cell (LANE HB RULINGS 3: at 20,000 rows the merged line's walk
    wrote 4 twin cells carrying a real key's six figures beside another letter)."""
    draw = random.Random(held_shapes.SEED + len("reglistmixR"))
    keys: "list[str]" = []
    while len(keys) < 40:
        one = f"R{draw.randint(100000, 999999)}"
        if one not in keys:
            keys += [one]
    weights = [1.0 + (place % 9) * 3 for place in range(44)]
    cells: "list[str]" = []
    for _row in range(n):
        draw.choices(range(44), weights)
        listed = draw.sample(keys, draw.randint(1, 3))
        cells += [(";", ",", "|")[draw.randrange(3)].join(listed)]
        draw.randrange(3)
        draw.uniform(3, 150)
    return cells


def _beside_a_word(n: int, cell: "object", share: float = 0.35, word: str = "pending") -> "list[str]":
    """Keys beside one word on ``share`` of the rows, read as labels (the verify of lane HB, 2, finding 1)."""
    draw = random.Random(11)
    cells: "list[str]" = []
    written = 0
    for _row in range(n):
        if draw.random() < share:
            cells += [word]
        else:
            cells += [cell(written)]  # type: ignore[operator]
            written = written + 1
    return cells


def _keys_of(count: int, low: int, high: int, prefix: str, seed: int) -> "list[str]":
    """``count`` different random keys, ``prefix`` and a number from ``low`` to ``high``, sorted."""
    draw = random.Random(seed)
    keys: "dict[str, bool]" = {}
    while len(keys) < count:
        keys[f"{prefix}{draw.randint(low, high)}"] = True
    return sorted(keys)


def _marked_lists(n: int, keys: "list[str]", mark: str) -> "list[str]":
    """One to three of ``keys`` a cell, joined by ``mark``."""
    draw = random.Random(4000)
    return [mark.join(draw.sample(keys, 1 + draw.randrange(3))) for _row in range(n)]


def _labelled_random(n: int) -> "list[str]":
    """Random keys `R` and six figures, once each, beside `pending` (finding 1's `lab_Rrand_once`)."""
    keys = _keys_of(15000, 100000, 999999, "R", 21)
    return _beside_a_word(n, lambda k: keys[k % len(keys)])


def _labelled_list(n: int, mark: str) -> "list[str]":
    """4,000 keys `R` and six figures, one to three a cell, beside `pending` (finding 1's lists)."""
    return _beside_a_word(
        n, lambda k: mark.join(f"R{100000 + (7 * k + j) % 4000}" for j in range(1 + k % 3))
    )


def _pad_alone_among_notes(n: int) -> "list[str]":
    """Keys `0001000` upward on six rows each in half the cells, beside notes holding a small number."""
    return [f"{(k // 6) + 1000:07d}" if k % 2 == 0 else f"seen by dr {k % 90} in clinic" for k in range(n)]


def _padded_once_among(n: int, note: "object", keys: "int | None" = None) -> "list[str]":
    """Keys `0001000` upward once each in the first ``keys`` cells (half the rows unless given), then notes."""
    count = n // 2 if keys is None else keys
    return [f"{1000 + k:07d}" for k in range(count)] + [note(k) for k in range(n - count)]  # type: ignore[operator]


def _two_runs_published(n: int) -> "list[str]":
    """One level holding two runs on two rows in five, beside `R100000` upward once each (Codex's review of lane
    HB's close round, item 1: the level's runs outnumbered the held rows' and the width named no opening)."""
    copies = 2 * n // 5
    return ["R100000X200000"] * copies + [f"R{100000 + k}" for k in range(n - copies)]


def _padded_inside_longer(n: int, short: int) -> "list[str]":
    """Runs `1` to `999` zero-filled to ``short`` figures and to three more, two letters after, on two rows in five
    each, beside `pending` (Codex's item 3 at ``short`` = 4: key `3` alone, so a longer made-up run held a real
    padded one)."""
    count = 2 * n // 5
    first = [f"{k % 999 + 1:0{short}d}{chr(65 + k // 999)}A" for k in range(count)]
    second = [f"{k % 999 + 1:0{short + 3}d}{chr(65 + k // 999)}A" for k in range(count)]
    return first + second + ["pending"] * (n - 2 * count)


def _rebuilt_as_absent(n: int) -> "list[str]":
    """`R100000` upward once each, `pending`, and eleven cells of a declared absent spelling `A900000` (Codex's
    item 4: a renamed run rebuilt a held-back cell as that spelling)."""
    keys = 13 * n // 20
    return [f"R{100000 + k}" for k in range(keys)] + ["pending"] * (n - keys - 11) + ["A900000"] * 11


def _room(name: str, n: int) -> "list[str]":
    header, rows, column, _declared = room.rows_of(name, n)
    return [row[header.index(column)] for row in rows]


def _dotted_pad(n: int) -> "list[str]":
    """ID-ROOM's verify 2: one number written `1000000.0`, `001000001` and `1000002` by turns."""
    return [f"{1000000 + k}.0" if k % 3 == 0 else (f"{1000000 + k:09d}" if k % 3 == 1 else f"{1000000 + k}")
            for k in range(n)]


def _durable_two_figures(n: int) -> "list[str]":
    """GG's skeptic 1, item 2 (`k60f2m`): sixty keys 10 to 69, `-1` for nobody on 2 % of rows."""
    draw = random.Random(20261028)
    return ["-1" if draw.random() < 0.02 else f"{10 + draw.randrange(60)}" for _k in range(n)]


# name: (the measured column's cells at n rows, its header, the options typed, what it is)
# what it is: "keys" (record numbers: persons counted), "dates" (with the source's layouts),
# "uid", "lists" (made-up keys inside list cells), "name" (a key by its name), "runs" (a held-back real cell's run
# as written inside a twin cell no published spelling names, `cells_holding_a_real_run`).
SHAPES: "dict[str, tuple[object, str, tuple[str, ...], str]]" = {
    # -- (4) and (10): the layout search beside a negative placeholder, and its unheld pair
    "keys_beside_minus_one": (lambda n: _keys_beside(n, "-1", 5), "record_no", (), "keys"),
    "keys_beside_minus_99": (lambda n: _keys_beside(n, "-99", 5), "record_no", (), "keys"),
    "keys_beside_blank": (lambda n: _keys_beside(n, "", 5), "record_no", (), "keys"),
    "durable": (lambda n: _held_kind("durable", n), "durable", (), "keys"),
    "key_m1_40": (lambda n: _held_kind("key_m1_40", n), "key_m1_40", (), "keys"),
    "phone_plus": (lambda n: _held_kind("phone_plus", n), "phone_plus", (), "keys"),
    # -- (8) and (13): whole numbers written with a point
    "key_point0": (lambda n: _held_kind("key_point0", n), "key_point0", (), "keys"),
    "years_point0": (lambda n: [f"{1850 + (k * 7) % 176}.0" for k in range(n)], "birth_year",
                     ("--identifier", "birth_year"), "keys"),
    # -- (9): UIDs with no root, and a held UID
    "uid_ge_and_siemens": (lambda n: _room("uid_ge_and_siemens", n), "target", ("--identifier", "target"), "uid"),
    "uid_hl7_and_dicom": (lambda n: _room("uid_hl7_and_dicom", n), "target", ("--identifier", "target"), "uid"),
    "uid_study_held": (lambda n: _room("uid_study_held", n), "target", (), "uid"),
    # -- (11) and (15): the walk's persons
    "pad_split": (lambda n: _room("pad_split", n), "target", ("--identifier", "target"), "keys"),
    "number_beside_its_decimal": (lambda n: _room("number_beside_its_decimal", n), "target",
                                  ("--identifier", "target"), "keys"),
    "x_dotted_pad": (_dotted_pad, "target", ("--identifier", "target"), "keys"),
    "dash_split": (lambda n: _room("dash_split", n), "target", ("--identifier", "target"), "keys"),
    # -- (6), (7) and (2): dates held or read as words
    "dob_mixed": (lambda n: _days(n, 1, 0.0, True), "birth_date", (), "dates"),
    "dob_unknown": (lambda n: _days(n, 1, 0.2, False), "birth_date", (), "dates"),
    "two_dates": (_two_dates, "vaccinated_on", (), "dates"),
    "pending": (_pending, "visit_date", (), "dates"),
    # -- skeptic 1, item 4: birth dates in other common layouts beside ISO, read as free text
    "dob_beside_short_years": (lambda n: _days_beside(n, "%m/%d/%y"), "birth_date", (), "dates"),
    "dob_beside_compact": (lambda n: _days_beside(n, "%Y%m%d"), "birth_date", (), "dates"),
    "dob_beside_month_words": (lambda n: _days_beside(n, "%d-%b-%Y"), "birth_date", (), "dates"),
    "dates_beside_month_years": (lambda n: _days_beside(n, "%m/%Y"), "diagnosed_on", (), "dates"),
    # -- LANE HB RULINGS 1, item (17): dates beside words, read as labels
    "dates_beside_words": (_dates_beside_words, "visit_date", (), "dates"),
    # -- the identifier walk's date layouts: birth dates in two layouts declared as identifiers
    "dob_mixed_declared": (lambda n: _days(n, 1, 0.0, True), "birth_date", ("--identifier", "birth_date"),
                           "dates"),
    # -- skeptic 1, item 5: one person written two ways (persons counted both ways)
    "zero_filled_or_not": (lambda n: _two_ways(n, False), "target", (), "keys"),
    "zero_filled_or_not_declared": (lambda n: _two_ways(n, False), "target", ("--identifier", "target"), "keys"),
    "dash_or_not": (lambda n: _two_ways(n, True), "target", ("--identifier", "target"), "keys"),
    # -- (14): a key by its name
    "durable_two_figures": (_durable_two_figures, "PatientStudyKey", (), "name"),
    # -- skeptic 1, item 3: a key named by a number word
    "patient_num_two_figures": (_durable_two_figures, "patient_num", (), "name"),
    "med_rec_no_two_figures": (_durable_two_figures, "med_rec_no", (), "name"),
    "person_nbr_two_figures": (_durable_two_figures, "PERSON_NBR", (), "name"),
    # -- Codex's review of lane HB, item 2: an acronym made plural (`patient_IDs`)
    "patient_ids_two_figures": (_durable_two_figures, "patient_IDs", (), "name"),
    # -- skeptic 1, item 2: record numbers between commas, read as free text
    "num4000_comma": (lambda n: _comma_lists(n, False), "registers", (), "lists"),
    "reg4000_comma": (lambda n: _comma_lists(n, True), "registers", (), "lists"),
    # -- the verify of lane HB, finding 1: keys in free text by other marks, alone among notes, once each
    "num4000_semicolon": (lambda n: _comma_lists(n, False, ";"), "registers", (), "lists"),
    "num4000_bar": (lambda n: _comma_lists(n, False, "|"), "registers", (), "lists"),
    "reg4000_semicolon": (lambda n: _comma_lists(n, True, ";"), "registers", (), "lists"),
    "keys_in_free_text": (_keys_in_notes, "note", (), "lists"),
    "seq_once_comma": (_keys_once, "linked_orders", (), "lists"),
    # -- the verify of lane HB, finding 2: random keys between commas, held (rule 11)
    "randR_comma": (lambda n: _random_lists(n, True), "registers", (), "lists"),
    "rand7_comma": (lambda n: _random_lists(n, False), "registers", (), "lists"),
    "randmix_comma": (_random_lists_two_widths, "registers", (), "lists"),
    "rand7_semicolon": (lambda n: _random_lists(n, False, ";"), "registers", (), "lists"),
    # -- LANE HB RULINGS 6: keys read as labels beside a word, once each or in lists (item 2), bare
    # five-figure lists (item 3), a register of four figures (item 4) and padded keys among notes (item 5)
    "lab_R_once": (lambda n: _beside_a_word(n, lambda k: f"R{100000 + k}"), "ref", (), "lists"),
    "lab_Rrand_once": (_labelled_random, "ref", (), "lists"),
    "lab_ABC_once": (lambda n: _beside_a_word(n, lambda k: f"ABC{100000 + k}"), "ref", (), "lists"),
    "lab_R_list_comma": (lambda n: _labelled_list(n, ","), "ref", (), "lists"),
    "lab_R_list_semi": (lambda n: _labelled_list(n, ";"), "ref", (), "lists"),
    "rand5_comma": (lambda n: _marked_lists(n, _keys_of(6000, 10000, 99999, "", 6), ","), "registers", (), "lists"),
    "rand5R_comma": (lambda n: _marked_lists(n, _keys_of(6000, 10000, 99999, "R", 5), ","), "registers", (), "lists"),
    "short4000_semi": (lambda n: _marked_lists(n, [f"{k}" for k in range(1000, 5000)], ";"), "registers", (), "lists"),
    "pad_alone_notes": (_pad_alone_among_notes, "note", (), "lists"),
    # -- LANE HB RULINGS 8 (Codex's review of the close round, items 1 to 4, and the round's own attacks): a level of
    # two runs beside keys once each; padded keys once each among notes in other scripts, and at the table's floor;
    # padded runs inside longer runs at every width from 4 to 9; a held-back cell rebuilt as a declared absent spelling
    "two_runs_published": (_two_runs_published, "ref", (), "runs"),
    "pad_notes_cjk": (lambda n: _padded_once_among(n, lambda k: "门诊 12"), "note", (), "runs"),
    "pad_notes_cyrillic": (lambda n: _padded_once_among(
        n, lambda k: f"осмотр врача {k % 90}"), "note", (), "runs"),
    "pad_notes_arabic": (lambda n: _padded_once_among(
        n, lambda k: f"مراجعة الطبيب {k % 90}"), "note", (),
        "runs"),
    "pad_notes_floor": (lambda n: _padded_once_among(n, lambda k: "门诊 12", 11), "note", (), "runs"),
    "padded_inside_4": (lambda n: _padded_inside_longer(n, 4), "ref", (), "runs"),
    "padded_inside_5": (lambda n: _padded_inside_longer(n, 5), "ref", (), "runs"),
    "padded_inside_6": (lambda n: _padded_inside_longer(n, 6), "ref", (), "runs"),
    "padded_inside_7": (lambda n: _padded_inside_longer(n, 7), "ref", (), "runs"),
    "padded_inside_8": (lambda n: _padded_inside_longer(n, 8), "ref", (), "runs"),
    "padded_inside_9": (lambda n: _padded_inside_longer(n, 9), "ref", (), "runs"),
    "rebuilt_as_absent": (_rebuilt_as_absent, "ref", ("--missing-value", "A900000"), "runs"),
    # ...the same held as record numbers (lane HX4's hold, P4-D424, reads such lists so on the merged line)
    "num4000_comma_held": (lambda n: _comma_lists(n, False), "registers", ("--identifier", "registers"),
                           "lists"),
    "reg4000_comma_held": (lambda n: _comma_lists(n, True), "registers", ("--identifier", "registers"),
                           "lists"),
    # -- (12): quoted comma lists of record numbers (600 rows: the internal smoke)
    "register_lists": (_register_lists, "registers", (), "lists"),
    # -- LANE HB RULINGS 3: HX4's lists of marks mixed cell by cell, held as record numbers as HX4's
    # hold (P4-D424) holds them on the merged line
    "reglistmixR": (_register_lists_mixed, "registers", ("--identifier", "registers"), "lists"),
}

# The layouts each date shape's source wrote its dates in.
DATE_LAYOUTS = {
    "dob_mixed": ("%Y-%m-%d", "%m/%d/%Y"),
    "dob_unknown": ("%Y-%m-%d",),
    "two_dates": ("%Y-%m-%d",),
    "pending": ("%Y-%m-%d",),
    "dob_beside_short_years": ("%Y-%m-%d", "%m/%d/%y"),
    "dob_beside_compact": ("%Y-%m-%d", "%Y%m%d"),
    "dob_beside_month_words": ("%Y-%m-%d", "%d-%b-%Y"),
    "dates_beside_month_years": ("%Y-%m-%d", "%m/%Y"),
    "dates_beside_words": ("%Y-%m-%d",),
    "dob_mixed_declared": ("%Y-%m-%d", "%m/%d/%Y"),
}
# The roles a held column takes: dates written by chance are counted only on them (the statistics
# skeptic's item 5: an unheld date column's twin draws its published dates).
HELD_ROLES = ("identifier", "free_text", "long_tail_labels")

# Each shape beside a negative placeholder, and the same column with the placeholder's cells blank.
PAIRS = {"keys_beside_minus_one": "keys_beside_blank", "keys_beside_minus_99": "keys_beside_blank"}

# The shapes read at 600 rows alone (the internal smoke): a construction, not a density.
AT_600 = ("register_lists",)

# The shapes generated at more than one seed (LANE HB RULINGS 3: a list cell's members kept off the
# real by construction, never by the luck of one draw).
SEEDS = {"reglistmixR": (0, 1)}

# The shapes whose own validation K-HZ-13 records apart, each a stated limit of P4-D442: linked order numbers
# once each, whose free text misses its published mean length by the walk's own lengths, as on the base (limit (t));
# and a register of four figures in free text whose made-up cells need more different runs than the room free of
# real runs holds at four figures, the rest written a figure wider (limit (y), LANE HB RULINGS 6, item 4).
RECORDED_APART = ("seq_once_comma", "short4000_semi")

# The held shapes whose list cells K-HZ-13 counts: each stays a list (the verify of lane HB, finding 2).
KEPT_AS_LISTS = ("randR_comma", "rand7_comma", "randmix_comma", "rand5_comma")
# ...and one more shape at 200,000 rows, in the slow leg (LANE HB RULINGS 6, item 3).
LARGE_LISTS = ("rand5R_comma",)


def table_of(name: str, n: int) -> "tuple[list[str], list[list[str]], str, tuple[str, ...]]":
    """One shape's table: its header, its rows, the measured column and the options typed."""
    make, head, typed, _what = SHAPES[name]
    cells = make(n)  # type: ignore[operator]
    header, rows = _rows_with(cells, head, SEED + len(name))
    return header, rows, head, typed


def as_a_number(cell: str) -> "str | None":
    """A cell read as a number, as a table reader reads a column of them (`1738886e6` too), exactly; else None."""
    if re.fullmatch(r"\s*[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?\s*", cell) is None:
        return None
    value = decimal.Decimal(cell.strip())
    return "0" if value == 0 else f"{value.normalize():E}"


def _is_a_date(cell: str, layouts: "tuple[str, ...]") -> bool:
    for layout in layouts:
        try:
            datetime.datetime.strptime(cell.strip(), layout)
        except ValueError:
            continue
        return True
    return False


def persons(cells: "list[str]", absent: "frozenset[str]") -> "dict[str, int]":
    """The different merged keys, and values read as numbers, of a column's present cells."""
    keys: "set[str]" = set()
    numbers: "set[str]" = set()
    for cell in cells:
        if not cell.strip() or cell in absent:
            continue
        keys.add(parsing.merged_key(cell))
        number = as_a_number(cell)
        if number is not None:
            numbers.add(number)
    return {"merged_keys": len(keys), "numbers": len(numbers)}


def _a_date_shape(cell: str) -> bool:
    """A cell a date could be: a figure, among marks alone or one run of three letters (a month word)."""
    return re.search(r"\d", cell) is not None and re.fullmatch(r"[^A-Za-z]*([A-Za-z]{3}[^A-Za-z]*)?", cell) is not None


def _in_e_notation(cell: str) -> bool:
    """A number written with a power of ten (`5646788e4`), as a table reader reads one."""
    return as_a_number(cell) is not None and re.search(r"[eE]", cell) is not None


def _a_key_token(token: str) -> bool:
    """A record number's token, as the walk reads one (`parsing.FIGURE_RUN_KEY_WIDTH`, LANE HB RULINGS 6, item 4):
    letters, at most three, then four figures or more."""
    found = re.fullmatch(r"([A-Za-z]{0,3})(\d+)", token)
    return found is not None and len(found.group(2)) >= parsing.FIGURE_RUN_KEY_WIDTH


def cells_carrying(tokens: "set[str]", cells: "list[str]") -> int:
    """The twin cells CARRYING a real key (LANE HB RULINGS 3 and 6, item 3): linear.

    A run of figures that is a real key's run of figures (`Q123456` beside a real `R123456`), read at each of
    its places at each real run's length, four figures or more, so one INSIDE a longer run counts; a whole run
    equal to a real key's, its noughts dropped, at any length; or a real key holding a letter found inside the
    cell as text, as lane HX4's counter finds it. Each cell read once through its runs and its places.
    """
    runs = {found.lstrip("0") for token in tokens for found in re.findall(r"\d+", token)} - {""}
    lettered = {token for token in tokens if re.search(r"[A-Za-z]", token)}
    lengths = sorted({len(token) for token in lettered})
    widths = sorted({len(found) for found in runs if len(found) >= parsing.FIGURE_RUN_KEY_WIDTH})
    return sum(
        1 for cell in cells
        if any(
            found.lstrip("0") in runs
            or any(found[at:at + size] in runs for size in widths for at in range(len(found) - size + 1))
            for found in re.findall(r"\d+", cell)
        )
        or any(cell[at:at + size] in lettered for size in lengths for at in range(len(cell) - size + 1))
    )


def cells_holding_a_real_run(real: "list[str]", twin: "list[str]", published: "frozenset[str]") -> int:
    """The twin cells, no published spelling, equal to a held-back real cell or holding one's run AS WRITTEN (LANE HB
    RULINGS 8): linear.

    A held-back real cell is one no published spelling names; its runs are its maximal runs of four figures or
    more, noughts kept, so a run led by noughts (`0206`) is one; each twin run is read at each of its places at
    each such length, once.
    """
    held = {cell for cell in real if cell not in published}
    runs = {found for cell in held for found in re.findall(r"\d+", cell) if len(found) >= parsing.FIGURE_RUN_KEY_WIDTH}
    lengths = sorted({len(found) for found in runs})
    return sum(
        1 for cell in twin
        if cell not in published and (
            cell in held and re.search(r"\d", cell) is not None
            or any(found[at:at + size] in runs for found in re.findall(r"\d+", cell)
                   for size in lengths for at in range(len(found) - size + 1))
        )
    )


def _spellings_of(node: object, into: "dict[str, bool]") -> None:
    """Every string a description block holds, keys and values, at any depth."""
    if isinstance(node, str):
        into[node] = True
    elif isinstance(node, dict):
        for key, inner in node.items():
            into[f"{key}"] = True
            _spellings_of(inner, into)
    elif isinstance(node, list):
        for inner in node:
            _spellings_of(inner, into)


def _list_tokens(cell: str) -> "list[str]":
    return [token.strip() for token in re.split(r"[,;|]", cell) if token.strip()]


def run(folder: pathlib.Path, name: str, n: int, validate: bool = True, seed: int = 0) -> "dict[str, object]":
    """Profile (nobody at the keyboard, nothing answered), generate at ``seed`` (0), validate; count."""
    header, rows, column, typed = table_of(name, n)
    what = SHAPES[name][3]
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "t.csv"
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    screen = io.StringIO()
    seconds: "dict[str, float]" = {}
    with held_shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            began = time.perf_counter()
            profiled = cli.main(["profile", f"{path}", "--out-dir", f"{folder}", "--replace"] + list(typed))
            seconds["profile"] = time.perf_counter() - began
            generated = validated = -1
            if profiled == 0:
                began = time.perf_counter()
                worked = time.process_time()
                generated = cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{folder}",
                                      "--seed", f"{seed}", "--replace"])
                seconds["generate"] = time.perf_counter() - began
                # ...and the processor's seconds, which a loaded machine moves far less than the clock's.
                seconds["generate_cpu"] = time.process_time() - worked
            if validate and generated == 0:
                began = time.perf_counter()
                validated = cli.main(["validate", f"{folder / 't-profile.json'}", "--twin",
                                      f"{folder / 't-twin.csv'}", "--out-dir", f"{folder}", "--replace"])
                seconds["validate"] = time.perf_counter() - began
    real = [row[header.index(column)] for row in rows]
    twin: "list[str]" = []
    if (folder / "t-twin.csv").is_file():
        with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
            table = list(csv.reader(handle))
        twin = [row[table[0].index(column)] for row in table[1:]]
    block: "dict[str, object]" = {}
    texts = ""
    if (folder / "t-profile.json").is_file():
        texts = (folder / "t-profile.json").read_text(encoding="utf-8")
        block = [one for one in json.loads(texts)["columns"] if one["name"] == column][0]
    absent = frozenset(block.get("missing_by_source") or {})  # type: ignore[arg-type]
    words = frozenset(cell for cell in real if cell.strip() and not any(c.isdigit() for c in cell))
    present = [cell for cell in twin if cell.strip() and cell not in absent and cell not in words]
    seen: "dict[str, object]" = {
        "exits": (profiled, generated, validated),
        "seconds": seconds,
        "role": block.get("role"),
        "real": real,
        "twin": twin,
        "equal": room.equal_cells(real, twin, absent | words),
        "merged": room.merged_equal_cells(real, twin, absent | words),
        "invalid_dates": 0,
        "off_the_grammar": 0,
        "persons_merged": 0,
        "persons_split": 0,
        "real_keys_in_lists": 0,
        "e_notation_the_source_never_wrote": 0,
    }
    # ...a number written with a power of ten where the source wrote none (the statistics skeptic's
    # item 1: a table reader then reads the column as fractions, not whole numbers).
    if not any(_in_e_notation(cell) for cell in real if cell.strip()):
        seen["e_notation_the_source_never_wrote"] = sum(1 for cell in present if _in_e_notation(cell))
    if what == "dates":
        # ...a cell written in figures and marks alone, as a date is: a stand-in word of letters
        # (`text-1` for a real `pending`) is no date string at all.
        layouts = DATE_LAYOUTS[name]
        seen["invalid_dates"] = sum(
            1 for cell in present
            if _a_date_shape(cell) and not _is_a_date(cell, layouts)
        )
        # ...and a made-up date equal to a real one BY CHANCE: a twin cell equal to a real cell
        # that the description does not publish (a published level is written as published).
        real_dates = {cell for cell in real if cell.strip() and cell not in absent}
        seen["dates_by_chance"] = sum(
            1 for cell in present if cell in real_dates and f'"{cell}"' not in texts
        ) if block.get("role") in HELD_ROLES else 0
    if what == "uid":
        seen["off_the_grammar"] = sum(
            1 for cell in present if UID.fullmatch(cell.strip()) is None or len(cell.strip()) > UID_AT_MOST
        )
    if what == "keys":
        before = persons(real, absent | words)
        after = persons(twin, absent | words)
        seen["persons"] = (before, after)
        seen["persons_merged"] = max(0, before["merged_keys"] - after["merged_keys"]) + max(
            0, before["numbers"] - after["numbers"]
        )
        # ...and the other way: one real person written as two twin persons (skeptic 1, item 5).
        seen["persons_split"] = max(0, after["merged_keys"] - before["merged_keys"]) + max(
            0, after["numbers"] - before["numbers"]
        )
        # ...and over the cells in the source's own layouts alone (the statistics skeptic's item 1).
        own = [cell for cell in real if cell.strip() and cell not in absent | words]
        convention = parsing.layout_convention(own) if own else parsing.LAYOUT_PLAIN
        kept = frozenset(parsing.layout_form(parsing.trimmed(cell), convention) for cell in own)
        inside = [cell for cell in present if parsing.layout_form(parsing.trimmed(cell), convention) in kept]
        seen["persons_in_the_source_layouts"] = (before, persons(inside, absent | words))
    if what == "lists":
        # ...the real KEYS among the tokens (a note's words beside keys are no key of the column).
        tokens = {token for cell in real for token in _list_tokens(cell) if _a_key_token(token)}
        keys = {parsing.merged_key(token) for token in tokens}
        seen["real_keys_in_lists"] = sum(
            1 for cell in present for token in _list_tokens(cell) if parsing.merged_key(token) in keys
        )
        seen["list_cells_carrying"] = cells_carrying(tokens, present)
    if what == "runs":
        # ...a held-back real cell's run as written, inside any twin cell no published spelling names (LANE HB
        # RULINGS 8): read with the list cells carrying a real key.
        spellings: "dict[str, bool]" = {}
        _spellings_of(block, spellings)
        seen["list_cells_carrying"] = cells_holding_a_real_run(
            [cell for cell in real if cell not in absent], present, frozenset(spellings))
    return seen
