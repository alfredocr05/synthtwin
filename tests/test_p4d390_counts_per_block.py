"""Which keys of a column's block may print a count of one to ten 493f6f8 did not.

Plan P4-D390, its Codex review, item 1.

WHAT WAS WRONG. P4-D390 said "No block prints more counts of one to
ten than before", measured as a total over the measurement's tables:
the counts the retired level pass had reprinted as missing fell, so the
total fell. Codex compared the blocks one by one and found blocks that
print more. Twelve common words on a hundred rows each, `word0` to
`word5` on two rows each, and `77`, `1e999` and `(+5)` on one row each
(1,215 rows, a set of categories at a floor of eleven) print
`n_numeric` 1, `n_out_of_range` 1, `n_contradictory` 1 and two remarks
saying "1 value(s)", where 493f6f8 printed nought for all three and no
remark: the retired pass had blanked those three cells. The other way
round, codes 100 to 111 on a hundred rows each, 201 to 206 on two and
one `ordinary`, declared a code, print `n_not_numeric` 1 where 493f6f8
printed nought.

THE RULING. The orchestrator kept the counts and the rare cells and
corrected the claim, under the owner's principle of 2026-10-01: HIPAA
exposure is the only privacy concern, no reader is assumed to rebuild
the data, and statistics and code that runs unchanged come first. These
totals name no person, code or value, and withholding them would leave
the twin without the odd cell, so code would run on the twin and crash
on the real file -- the failure the landing exists to remove.

WHAT IS PINNED HERE. Every table below is described by the product as
it stands and compared, block by block and key by key, with what
493f6f8 printed for the same table (`p4d390_described_before.BEFORE`).
A count of one to ten the product prints that 493f6f8 did not print at
the same key -- counted as a multiset, so a key whose small count
changed is new too -- must be one of the keys `MAY_BE_NEW` names, and on
a column declared an identifier no new count of one to ten is allowed
at all. The tables are Codex's two, the lane's batteries (its five
seeded tables at floors of eleven and thirty-six, and three of them
again with columns declared identifiers) and the forty-six shapes of
the stage-3 battery `K-S3-12` counts.

Every table is built by seeded neutral code at runtime (plan D13); the
lane's batteries are the measurement's own generators at its own seeds,
with the words the decontamination manifest refuses replaced -- in
five column names, in the generators' own names, in one category and in
one prefix of ward names -- and nothing else changed.
"""

import bisect
import collections
import csv
import io
import itertools
import math
import pathlib
import random

import pytest

import fixtures
import p4d390_described_before
import stage3_battery
from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

# -- what a block may now print that 493f6f8 did not ---------------------

# THE KEYS THAT MAY CARRY A COUNT OF ONE TO TEN 493f6f8 DID NOT PRINT,
# on a column not declared an identifier, each counting cells or values
# the retired pass had blanked -- measured over every table this file
# describes, and stated in plan P4-D390:
#
# - the pool's own keys, which the landing exists to publish: a held-back
#   level is pooled whatever its size, so `suppressed_levels` and
#   `suppressed_rows` (and the notes restating them) count what 493f6f8
#   printed as missing, and the form census pools the forms those cells
#   wear under `(withheld)`;
# - the counts of different values, `n_distinct` and `n_distinct_folded`
#   (and the evidence restating them, or restating how many levels a long
#   tail publishes), which now count the values the pass had blanked;
# - and the four class totals, `n_numeric`, `n_out_of_range`,
#   `n_contradictory` and `n_not_numeric`, with the two remarks restating
#   the second and third (Codex's item).
#
# No other key does, and no key of a declared identifier does.
MAY_BE_NEW = (
    "n_numeric",
    "n_out_of_range",
    "n_contradictory",
    "n_not_numeric",
    "n_distinct",
    "n_distinct_folded",
    "suppressed_levels",
    "suppressed_rows",
    f"shape_forms/{contract.WITHHELD}",
)

# Counts that say where something is or which version wrote it, never
# how many rows did anything: `K-S3-12` leaves them out the same way.
_STRUCTURAL = (
    "position",
    "n_parts",
    "level_ceiling",
    "profile_version",
    "n_columns",
    "source/dialect/row_order/column",
    "source/dialect/written_names/[]/position",
)

# The bindings of a sentence argument that are counts. A setting, a
# column number, a place in a closed list, a value and the three
# argument classes that are not whole numbers are not.
_COUNTED_BINDINGS = (
    taxonomy.BIND_KEY,
    taxonomy.BIND_SUM,
    taxonomy.BIND_DIFFERENCE,
    taxonomy.BIND_DOCUMENT,
    taxonomy.BIND_MAIN_WRAPPER,
    taxonomy.BIND_LEVELS_AT_THE_LINE,
    taxonomy.BIND_POPULATION,
    taxonomy.BIND_FLOORED,
)


def _is_a_count_kind(kind: str) -> bool:
    """Whether a publication rule's kind is a count of rows, cells or groups."""
    return "count" in kind or kind == "one-group-size-below-the-floor"


def _small(value: object) -> bool:
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and 0 < value < 11
    )


def _leaves(node: object, path: "tuple[str, ...]", shown: "tuple[str, ...]"):
    """Every leaf the publication rules name, with its rule and its place."""
    rules = profile.PUBLICATION_RULES
    if path not in rules:
        return
    kind = rules[path]
    if kind == profile._MAYBE_OBJECT:
        if node is None:
            return
        kind = profile._OBJECT
    if kind == profile._MAYBE_ARRAY:
        if node is None:
            return
        kind = profile._ARRAY
    if kind == profile._OBJECT:
        free = path + (profile._ANY_KEY,)
        for name in sorted(node):
            yield from _leaves(
                node[name],
                free if free in rules else path + (name,),
                shown + (name,),
            )
        return
    if kind == profile._ARRAY:
        for place in range(len(node)):
            yield from _leaves(
                node[place], path + (profile._EACH,), shown + (f"{place}",)
            )
        return
    yield path, shown, kind, node


def _positions(form: str, arguments: "tuple[object, ...]"):
    """(form, place, argument) for every argument, nested forms walked."""
    found: "list[tuple[str, int, object]]" = []
    for place in range(len(arguments)):
        argument = arguments[place]
        nested = (
            isinstance(argument, tuple)
            and len(argument) == 2
            and isinstance(argument[0], str)
            and isinstance(argument[1], tuple)
        )
        if nested and argument[0] not in (
            taxonomy.SAID_FEWER_THAN_THE_LINE,
            taxonomy.SAID_SOME_BUT_NOT_ALL,
            taxonomy.SAID_SOME,
        ):
            found += _positions(argument[0], argument[1])
            continue
        found += [(form, place, argument)]
    return found


def small_counts(document: dict) -> "dict[str, list[tuple[object, ...]]]":
    """Every count of one to ten a description prints, block by block.

    A key is `("key", path, value)`, its path the block's own keys with
    a list's places written `[]`; a sentence argument is
    `("said", form, place, value)`. The table's own blocks are filed
    under `(table)` and a publication note under its column. Settings
    and structural counts are left out, as `K-S3-12` leaves them out.
    """
    found: "dict[str, list[tuple[object, ...]]]" = {"(table)": []}
    columns = document["columns"]
    for block in columns:
        found[block["name"]] = []
    for path, shown, kind, value in _leaves(document, (), ()):
        if path[:1] == ("settings",) or not _is_a_count_kind(kind):
            continue
        if not _small(value):
            continue
        owner = "(table)"
        steps = shown
        if shown[:1] == ("columns",):
            owner = columns[int(shown[1])]["name"]
            steps = shown[2:]
            path = path[2:]
        where = "/".join(
            [
                "[]" if path[place] == profile._EACH else steps[place]
                for place in range(len(steps))
            ]
        )
        if where in _STRUCTURAL:
            continue
        found[owner] += [("key", where, value)]
    said: "list[tuple[str, object]]" = []
    head = document["source"]["header_evidence"]
    if isinstance(head, taxonomy.Note):
        said += [("(table)", head)]
    for entry in document["publication_notes"]:
        if isinstance(entry["note"], taxonomy.Note):
            owner = entry["column"] if entry["column"] in found else "(table)"
            said += [(owner, entry["note"])]
    for block in columns:
        if isinstance(block["detection_evidence"], taxonomy.Note):
            said += [(block["name"], block["detection_evidence"])]
        for remark in block["remarks"]:
            if isinstance(remark, taxonomy.Note):
                said += [(block["name"], remark)]
    for owner, note in said:
        for form, place, argument in _positions(note.form, note.arguments):
            if not _small(argument):
                continue
            binding = taxonomy.argument_binding(form, place)
            if binding[:1] and binding[0] not in _COUNTED_BINDINGS:
                continue
            if binding[:1] == (taxonomy.BIND_KEY,) and binding[1] in _STRUCTURAL:
                continue
            found[owner] += [("said", form, place, argument)]
    for owner in found:
        found[owner] = sorted(found[owner], key=repr)
    return found


def new_small_counts(
    before: "dict[str, list[tuple[object, ...]]]",
    after: "dict[str, list[tuple[object, ...]]]",
) -> "dict[str, list[tuple[object, ...]]]":
    """What each block prints after that it did not print before, as a multiset."""
    new: "dict[str, list[tuple[object, ...]]]" = {}
    for owner in sorted(after):
        was = collections.Counter(before[owner] if owner in before else [])
        now = collections.Counter(after[owner])
        added = sorted((now - was).elements(), key=repr)
        if added:
            new[owner] = added
    return new


def may_be_new(entry: "tuple[object, ...]") -> bool:
    """Whether one new count is of a key `MAY_BE_NEW` names, or restates one."""
    if entry[0] == "key":
        return entry[1] in MAY_BE_NEW
    binding = taxonomy.argument_binding(f"{entry[1]}", int(f"{entry[2]}"))
    if binding[:1] == (taxonomy.BIND_LEVELS_AT_THE_LINE,):
        return True
    return binding[:1] == (taxonomy.BIND_KEY,) and binding[1] in MAY_BE_NEW


def outside_the_list(
    new: "dict[str, list[tuple[object, ...]]]", identifiers: "tuple[str, ...]"
) -> "dict[str, list[tuple[object, ...]]]":
    """The new counts no rule allows: any on an identifier or the table, and
    any of another key elsewhere."""
    refused: "dict[str, list[tuple[object, ...]]]" = {}
    for owner in sorted(new):
        if owner in identifiers or owner == "(table)":
            refused[owner] = new[owner]
            continue
        wrong = [entry for entry in new[owner] if not may_be_new(entry)]
        if wrong:
            refused[owner] = wrong
    return refused


# -- the tables --------------------------------------------------------


def _csv_text(header: "list[str]", columns: "dict[str, list[str]]") -> str:
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(header)
    for row in range(len(columns[header[0]])):
        writer.writerow([columns[name][row] for name in header])
    return out.getvalue()


def _one_column(name: str, cells: "list[str]") -> str:
    return _csv_text([name], {name: cells})


def codex_words() -> str:
    """Codex's first table: twelve words on a hundred rows each, six on two
    rows each, and a number, a number too large to hold and a sign inside
    brackets on one row each -- 1,215 rows."""
    cells: "list[str]" = []
    for word in (
        "calm", "cold", "dark", "deep", "dull", "fair",
        "firm", "flat", "full", "high", "kind", "late",
    ):
        cells += [word] * 100
    for place in range(6):
        cells += [f"word{place}"] * 2
    cells += ["77", "1e999", "(+5)"]
    random.Random(1).shuffle(cells)
    return _one_column("thing", cells)


def codex_codes() -> str:
    """Codex's second table: codes 100 to 111 on a hundred rows each, 201 to
    206 on two rows each, and one word -- 1,213 rows."""
    cells: "list[str]" = []
    for code in range(100, 112):
        cells += [f"{code}"] * 100
    for code in range(201, 207):
        cells += [f"{code}"] * 2
    cells += ["ordinary"]
    random.Random(2).shuffle(cells)
    return _one_column("thing", cells)


_LETTERS = "ABCDEFGHIJKLMNOPQRSTVWXYZ"
_SYLLABLES = (
    "ka", "lo", "mi", "ne", "ru", "ta", "vo", "si", "pe", "da", "go", "fu",
    "hi", "jo", "be", "zu", "wa", "xe", "qi", "yo", "ar", "el", "in", "on",
    "ul",
)


def _zipf_draw(levels: int, exponent: float, draw: random.Random):
    weights = [1.0 / (k + 1) ** exponent for k in range(levels)]
    totals = list(itertools.accumulate(weights))
    whole = totals[-1]

    def one() -> int:
        return bisect.bisect_left(totals, draw.random() * whole)

    return one


def _lettered_codes(n: int, seed: int) -> "list[str]":
    draw = random.Random(seed)
    seen: "dict[str, int]" = {}
    out: "list[str]" = []
    while len(out) < n:
        letter = draw.choice(_LETTERS)
        head = f"{letter}{draw.randrange(100):02d}"
        tail_length = draw.choice((0, 1, 1, 2, 2, 2, 3, 4))
        if tail_length == 0:
            code = head
        else:
            tail = "".join(
                draw.choice("0123456789") for _each in range(min(tail_length, 3))
            )
            if tail_length == 4:
                tail += draw.choice("ADS")
            code = head + "." + tail
        if code not in seen:
            seen[code] = 1
            out += [code]
    draw.shuffle(out)
    return out


def _three_character_codes(n: int, seed: int) -> "list[str]":
    draw = random.Random(seed)
    seen: "dict[str, int]" = {}
    out: "list[str]" = []
    while len(out) < n:
        code = f"{draw.choice(_LETTERS)}{draw.randrange(100):02d}"
        if code not in seen:
            seen[code] = 1
            out += [code]
    draw.shuffle(out)
    return out


def _names(
    n: int,
    seed: int,
    fewest: int = 2,
    most: int = 4,
    endings: "tuple[str, ...]" = ("", "", "ine", "ol", "ide", "mab", "pril", "statin"),
) -> "list[str]":
    draw = random.Random(seed)
    seen: "dict[str, int]" = {}
    out: "list[str]" = []
    while len(out) < n:
        word = "".join(
            draw.choice(_SYLLABLES) for _each in range(draw.randint(fewest, most))
        ) + draw.choice(endings)
        if word not in seen:
            seen[word] = 1
            out += [word]
    draw.shuffle(out)
    return out


def _product_strings(n: int, seed: int) -> "list[str]":
    draw = random.Random(seed)
    generics = _names(900, seed + 1)
    measures = [
        "5 mg", "10 mg", "20 mg", "25 mg", "40 mg", "50 mg", "100 mg",
        "250 mg", "500 mg", "1 g", "2 mg/mL", "10 mg/mL", "100 units/mL",
        "0.9 %", "1 mg",
    ]
    kinds = [
        "tablet", "capsule", "injection", "oral solution", "IV bag", "patch",
        "inhaler",
    ]
    seen: "dict[str, int]" = {}
    out: "list[str]" = []
    while len(out) < n:
        made = f"{draw.choice(generics)} {draw.choice(measures)} {draw.choice(kinds)}"
        if made not in seen:
            seen[made] = 1
            out += [made]
    draw.shuffle(out)
    return out


def _five_figure_codes(n: int, seed: int) -> "list[str]":
    draw = random.Random(seed)
    seen: "dict[str, int]" = {}
    out: "list[str]" = []
    while len(out) < n:
        code = f"{draw.randrange(10000, 100000)}"
        if code not in seen:
            seen[code] = 1
            out += [code]
    return out


_UNITS_COMMON = (
    "mg/dL", "mmol/L", "g/dL", "%", "mEq/L", "U/L", "x10^9/L", "x10^12/L",
    "fL", "pg", "ng/mL", "mL/min/1.73m2", "sec", "ratio", "mg/L", "umol/L",
    "IU/L", "pmol/L", "ng/dL", "mmHg", "bpm", "kg", "cm", "degC", "mL",
)
_UNITS_RARE = (
    "mOsm/kg", "copies/mL", "ug/dL", "nmol/L", "mcg/kg/min", "U/mL", "titer",
    "mIU/mL", "cells/uL", "mm/hr", "Ehrlich U", "g/24h",
)
_WARDS_CLOSED = ("Ward 9C (closed)", "Overflow Unit B", "Isolation Annex")


def registers(rows: int) -> str:
    """The measurement's eleven made-up columns (lane G4's first battery).

    Codes shaped like an all-diagnoses register (25,000, Zipf 1.0) and a
    principal one (12,000, Zipf 1.15), three-character categories,
    product strings, product names, test names, five-figure codes
    declared a code (`proc`), 25 common units beside 12 rare ones, 45
    wards beside 3 closed ones, a kind of F and M with rare U and X, and
    a 30,000-code register. Built at seed 1 exactly as the measurement
    built its tables of 10,000, 50,000 and 100,000 rows.
    """
    draw = random.Random(1 * 1000003 + rows)
    columns: "dict[str, list[str]]" = {}

    def drawn(name: str, levels: "list[str]", exponent: float) -> None:
        one = _zipf_draw(len(levels), exponent, draw)
        columns[name] = [levels[one()] for _row in range(rows)]

    drawn("dx_all", _lettered_codes(25000, 11), 1.0)
    drawn("dx_principal", _lettered_codes(12000, 12), 1.15)
    drawn("dx_category", _three_character_codes(1800, 13), 1.1)
    drawn("drug", _product_strings(4000, 14), 1.05)
    drawn("drug_generic", _names(1200, 15), 1.1)
    tests = _names(600, 16, 1, 3, ("", " panel", " level", ", serum"))
    drawn(
        "lab_test",
        [
            tests[place].upper() if place % 3 == 0 else tests[place].capitalize()
            for place in range(len(tests))
        ],
        1.2,
    )
    drawn("proc", _five_figure_codes(8000, 17), 1.1)
    common = _zipf_draw(len(_UNITS_COMMON), 0.9, draw)
    unit: "list[str]" = []
    for _row in range(rows):
        u = draw.random()
        if u < 0.00015 * len(_UNITS_RARE):
            unit += [_UNITS_RARE[int(u / 0.00015)]]
        else:
            unit += [_UNITS_COMMON[common()]]
    columns["unit"] = unit
    wards_drawn = random.Random(18)
    named = [
        f"{wards_drawn.choice(['Ward', 'Unit', 'Bay', 'Step-down'])} "
        f"{wards_drawn.randrange(1, 12)}{wards_drawn.choice('ABCDEFG')}"
        for _each in range(200)
    ]
    wards = sorted(set(named))[:45]
    weights = [math.exp(wards_drawn.gauss(0, 0.8)) for _each in wards]
    totals = list(itertools.accumulate(weights))
    ward: "list[str]" = []
    for _row in range(rows):
        u = draw.random()
        if u < 0.00012 * len(_WARDS_CLOSED):
            ward += [_WARDS_CLOSED[int(u / 0.00012)]]
        else:
            ward += [wards[bisect.bisect_left(totals, draw.random() * totals[-1])]]
    columns["ward"] = ward
    kind: "list[str]" = []
    for _row in range(rows):
        u = draw.random()
        kind += ["U" if u < 0.00005 else "X" if u < 0.00007 else "F" if u < 0.52 else "M"]
    columns["kind"] = kind
    register = sorted(
        {
            f"{random.Random(k).choice('ABCDEFGHJKLMNPRSTVWXYZ')}"
            f"{random.Random(k + 7).randrange(1000):03d}."
            f"{random.Random(k + 9).randrange(100):02d}"
            for k in range(40000)
        }
    )[:30000]
    drawn("bigcat", register, 1.1)
    return _csv_text(list(columns), columns)


def _with_rare(draw: random.Random, rows: int, common, rare) -> "list[str]":
    out = [common() for _row in range(rows - sum([count for _value, count in rare]))]
    for value, count in rare:
        out += [value] * count
    draw.shuffle(out)
    return out


def shapes(rows: int = 10000) -> str:
    """The measurement's nine columns aimed at the retired pass (seed 3)."""
    draw = random.Random(3)
    columns: "dict[str, list[str]]" = {}
    columns["lab_cr"] = _with_rare(
        draw, rows, lambda: f"{draw.lognormvariate(0, 0.35):.2f}", [("hemolyzed", 1)]
    )
    columns["lab_k"] = _with_rare(
        draw,
        rows,
        lambda: f"{draw.gauss(4.2, 0.45):.1f}",
        [("hemolyzed", 4), ("QNS", 1), ("clotted", 1)],
    )
    columns["lab_trop"] = _with_rare(
        draw,
        rows,
        lambda: "<0.01" if draw.random() < 0.4 else f"{draw.lognormvariate(-3, 1.2):.3f}",
        [("see note", 1)],
    )
    pool = [f"{draw.randrange(10000, 100000)}" for _each in range(300)]
    weights = [1.0 / (k + 1) ** 1.1 for k in range(300)]
    columns["proc_one_f"] = _with_rare(
        draw, rows, lambda: draw.choices(pool, weights)[0], [("0001F", 1)]
    )
    columns["proc_three_f"] = _with_rare(
        draw,
        rows,
        lambda: draw.choices(pool, weights)[0],
        [("0001F", 1), ("3074F", 2)],
    )
    injuries = sorted(
        {
            f"S{draw.randrange(10, 100)}.{draw.randrange(100, 1000)}{draw.choice('ADS')}"
            for _each in range(40)
        }
    )
    others = sorted(
        {f"{draw.choice('EIJKN')}{draw.randrange(10, 100)}.{draw.randrange(10)}" for _each in range(400)}
    )
    tail = [1.0 / (k + 1) ** 0.9 for k in range(len(others))]
    columns["dx7"] = _with_rare(
        draw,
        rows,
        lambda: draw.choice(injuries) if draw.random() < 0.5 else draw.choices(others, tail)[0],
        [("S99.999A", 1)],
    )
    groups = [
        "White", "Black or African American", "Asian", "Other",
        "American Indian or Alaska Native", "Unknown",
    ]
    columns["group"] = _with_rare(
        draw,
        rows,
        lambda: draw.choices(groups, [60, 18, 7, 10, 1.5, 3.5])[0],
        [("Native Hawaiian", 1), ("Other Pacific Islander", 1)],
    )
    endings = [
        "Home", "Home health", "SNF", "Rehab", "Expired", "AMA", "Hospice",
        "LTACH", "Transfer acute", "Psych",
    ]
    columns["disposition"] = _with_rare(
        draw,
        rows,
        lambda: draw.choices(endings, [55, 15, 10, 6, 3, 2, 3, 2, 3, 1])[0],
        [("Court/law enforcement", 1), ("Federal facility", 1), ("Shelter", 1)],
    )
    wards = [f"Ward {k}" for k in range(1, 41)]
    columns["ward_closed"] = _with_rare(
        draw,
        rows,
        lambda: draw.choice(wards),
        [("Ward 9C (closed)", 2), ("Isolation Annex", 3)],
    )
    return _csv_text(list(columns), columns)


def shapes2(rows: int = 10000) -> str:
    """The measurement's five columns for the paths the first shapes missed (seed 7)."""
    draw = random.Random(7)

    def glucose() -> str:
        return f"{max(2.0, draw.lognormvariate(4.6, 0.25)):.1f}"

    columns: "dict[str, list[str]]" = {}
    columns["glu_one"] = _with_rare(
        draw, rows, glucose, [("hemolyzed", 40), ("QNS", 25), ("see note", 1)]
    )
    columns["glu_band"] = _with_rare(
        draw,
        rows,
        glucose,
        [("hemolyzed", 40), ("QNS", 25), ("clotted", 1), ("lipemic", 1), ("icteric", 2)],
    )
    columns["consent"] = _with_rare(draw, rows, lambda: "Y", [("N", 1)])
    columns["smoker"] = _with_rare(
        draw,
        rows,
        lambda: draw.choices(["never", "former", "current"], [55, 30, 15])[0],
        [("unknown", 1)],
    )
    routes = [
        "oral", "IV", "IM", "SC", "inhaled", "topical", "PR", "SL",
        "intranasal", "transdermal", "ophthalmic", "otic",
    ]
    columns["route"] = _with_rare(
        draw,
        rows,
        lambda: draw.choices(routes, [50, 25, 6, 8, 3, 2, 1, 1, 1, 1, 1, 1])[0],
        [("intrathecal", 2), ("epidural", 2), ("intraosseous", 1), ("intravitreal", 1)],
    )
    return _csv_text(list(columns), columns)


# Every table: (builder, its argument, floor, declared codes, declared
# identifiers). The stage-3 battery's forty-six shapes are described by
# that battery's own helper, at a floor of eleven.
TABLES = {
    "codex_words": (codex_words, None, 11, (), ()),
    "codex_codes": (codex_codes, None, 11, ("thing",), ()),
    "codex_words_identifier": (codex_words, None, 11, (), ("thing",)),
    "codex_codes_identifier": (codex_codes, None, 11, (), ("thing",)),
    "registers_10000_f11": (registers, 10000, 11, ("proc",), ()),
    "registers_10000_f36": (registers, 10000, 36, ("proc",), ()),
    "registers_50000_f11": (registers, 50000, 11, ("proc",), ()),
    "registers_50000_f36": (registers, 50000, 36, ("proc",), ()),
    "registers_100000_f11": (registers, 100000, 11, ("proc",), ()),
    "registers_100000_f36": (registers, 100000, 36, ("proc",), ()),
    "shapes_f11": (shapes, 10000, 11, ("proc_one_f", "proc_three_f"), ()),
    "shapes_f36": (shapes, 10000, 36, ("proc_one_f", "proc_three_f"), ()),
    "shapes2_f11": (shapes2, 10000, 11, (), ()),
    "shapes2_f36": (shapes2, 10000, 36, (), ()),
    "registers_10000_identifiers_f11": (
        registers, 10000, 11, ("proc",), ("kind", "unit", "bigcat"),
    ),
    "shapes_identifiers_f11": (
        shapes, 10000, 11, (), ("proc_one_f", "proc_three_f", "dx7", "group"),
    ),
    "shapes2_identifiers_f11": (
        shapes2, 10000, 11, (), ("consent", "route", "glu_one"),
    ),
}

_TEXTS: "dict[tuple[object, object], str]" = {}


def described(folder: pathlib.Path, name: str) -> dict:
    """One table of `TABLES`, written to ``folder`` and described."""
    builder, argument, floor, codes, identifiers = TABLES[name]
    key = (builder, argument)
    if key not in _TEXTS:
        _TEXTS[key] = builder() if argument is None else builder(argument)
    path = fixtures.write(folder, f"{name}.csv", _TEXTS[key])
    return profile.build_document(
        reading.read_table(f"{path}", small_cell_floor=floor),
        taxonomy.Settings(small_cell_floor=floor),
        list(identifiers),
        forced_codes=list(codes) or None,
    )


def stage3_described(folder: pathlib.Path, name: str) -> "tuple[dict, tuple[str, ...]]":
    """One shape of the stage-3 battery at a floor of eleven, and its identifiers."""
    _cells, flags = stage3_battery.SHAPES[name](
        random.Random(stage3_battery.BATTERY_SEED)
    )
    identifiers = tuple(flags["identifiers"] if "identifiers" in flags else ())
    return stage3_battery.described(folder, name, 11), identifiers


# -- the checks ----------------------------------------------------------


@pytest.mark.parametrize("name", sorted(TABLES))
def test_no_block_prints_a_new_small_count_outside_the_list(
    tmp_path: pathlib.Path, name: str
) -> None:
    """Block by block against 493f6f8: only the listed keys, and nothing on
    a declared identifier.

    THE REGRESSION CHECK ITEM 1 ASKED FOR. The lane measured its claim as
    a total over the table, and a total lets one block's new count of one
    hide behind another block's count that went away. Here each column's
    counts of one to ten are compared with 493f6f8's for that same
    column, so a block that starts printing a count 493f6f8 did not --
    of a key the list does not name, or of any key on a column declared
    an identifier -- turns this red by name.
    """
    document = described(tmp_path, name)
    after = small_counts(document)
    before = p4d390_described_before.BEFORE[name]
    assert sorted(after) == sorted(before), name
    identifiers = TABLES[name][4]
    assert outside_the_list(new_small_counts(before, after), identifiers) == {}


def test_the_stage3_battery_prints_no_new_small_count_outside_the_list(
    tmp_path: pathlib.Path,
) -> None:
    """The same check over the forty-six shapes `K-S3-12` counts, at eleven.

    Two of them move: a column of 1,977 `NORTH`, 11 `SOUTH` and one
    `SITE_X`, whose pool is one level over one row and whose count of
    different values is three where 493f6f8 blanked the one row; and 300
    cells of three words beside a hundred codes written once, which reads
    as a long tail and says three levels reach its line where 493f6f8
    blanked the hundred and read three categories.
    """
    refused: "dict[str, dict[str, list[tuple[object, ...]]]]" = {}
    moved: "list[str]" = []
    for name in sorted(stage3_battery.SHAPES):
        document, identifiers = stage3_described(tmp_path, name)
        after = small_counts(document)
        before = p4d390_described_before.BEFORE[f"stage3_{name}"]
        assert sorted(after) == sorted(before), name
        new = new_small_counts(before, after)
        if new:
            moved += [name]
        wrong = outside_the_list(new, identifiers)
        if wrong:
            refused[name] = wrong
    assert refused == {}
    assert moved == ["labels_one_blank_pooled", "long_tail_labels"]


def _round_trip(
    folder: pathlib.Path, name: str
) -> "tuple[dict, contract.Profile, list[str], validation.Outcome]":
    document = described(folder, name)
    written = fixtures.write_profile(folder, f"{name}.json", document)
    loaded = contract.load_profile(f"{written}")
    twin = generation.generate(loaded, 7)
    twin_file = fixtures.write(folder, f"{name}-twin.csv", rendering.twin_csv(twin))
    return document, loaded, list(twin.columns[0]), validation.measure(loaded, f"{twin_file}")


def _classes(cells: "list[str]") -> "collections.Counter[str]":
    return collections.Counter(
        [parsing.classify_number(cell) for cell in cells if cell != ""]
    )


def test_codex_s_two_tables_print_the_class_totals_and_keep_the_odd_cells(
    tmp_path: pathlib.Path,
) -> None:
    """The ruling on Codex's two tables: the counts stay, and so do the cells.

    Against 493f6f8, the first table's block gains exactly the three
    class totals of one, the two remarks restating them and the pool's
    nine levels; the second gains `n_not_numeric` 1 and the pool's seven.
    The twin of each writes the odd cells the table holds -- one number,
    one number out of range and one contradiction among words; one word
    among codes -- so code that would crash on those cells of the real
    file crashes on the twin first, and every check of both twins is met.
    """
    expected = {
        "codex_words": [
            ("key", "n_contradictory", 1),
            ("key", "n_numeric", 1),
            ("key", "n_out_of_range", 1),
            ("key", "suppressed_levels", 9),
            ("said", taxonomy.NOTE_LABELS_POOLED, 0, 9),
            ("said", taxonomy.REMARK_CONTRADICTORY, 0, 1),
            ("said", taxonomy.REMARK_OUT_OF_RANGE, 0, 1),
        ],
        "codex_codes": [
            ("key", "n_not_numeric", 1),
            ("key", "suppressed_levels", 7),
            ("said", taxonomy.NOTE_LABELS_POOLED, 0, 7),
        ],
    }
    table_classes = {
        "codex_words": {
            parsing.NUMBER: 1,
            parsing.NUMBER_OUT_OF_RANGE: 1,
            parsing.NUMBER_CONTRADICTORY: 1,
            parsing.NOT_A_NUMBER: 1212,
        },
        "codex_codes": {parsing.NUMBER: 1212, parsing.NOT_A_NUMBER: 1},
    }
    for name in sorted(expected):
        document, _loaded, cells, outcome = _round_trip(tmp_path, name)
        new = new_small_counts(
            p4d390_described_before.BEFORE[name], small_counts(document)
        )
        assert new == {"thing": sorted(expected[name], key=repr)}, name
        block = document["columns"][0]
        assert (block["n_missing"], block["n_present"]) == (0, len(cells)), name
        assert _classes(cells) == table_classes[name], name
        assert [
            check.subcheck
            for check in outcome.checks
            if check.verdict == validation.MISSED
        ] == [], name
