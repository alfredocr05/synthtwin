"""Ages written inside free-text phrases, read generously (lane HB3-a, plan P4-D482).

The orchestrator's LANE HB3-a RULINGS 1 (2) and 4 (2): an age past 89
written inside a phrase -- `Age at diagnosis: 95`, `Age (yrs): 95`, `Pt
age: 95`, `Age ~95`, `95 years 3 months`, `95 y/o F`, `Age 95 M` -- put no
Safe Harbor question on the public head and only an accidental hold kept it
back; a column of `Age 0NN`, `Age -NN` or `Age<U+FF1A>NN` was published with
its ages past 90. `taxonomy.safe_harbor_number` now reads an age's phrase
(`taxonomy._phrase_age`): a word of `AGE_VOCABULARY` read whole anywhere in
the cell makes the first number after it within its clause and
`AGE_VOCABULARY.reach` characters the age, whatever stands between; a dash
after the word is a mark, never a sign; a capital M apart from the number is
a gender, never months; a smaller unit's part is written `0` by the top
code. Each class is closed by a GENERATED check at the unit level (thousands
of spellings: every placement of the word, every connector, bracket, mark
and approximation sign, unit, months part, gender letter and word, every
space and dash of the product's one definition and the characters beyond it
in every place), product and oracle alike (A-P4-59); the words that are no
age read as before; ONE table at the owner's floor through the command. The
20,000-row legs per family live in `K-HZ-35`'s driver
(`tools/measurements/kpi_age_phrases_key_rooms.py`; THE SUITE'S TIME rule).
"""

from __future__ import annotations

import contextlib
import csv
import importlib.util
import io
import json
import pathlib
import random
import re
import unicodedata

import age_phrase_counts
from synthtwin import cli, contract, generation, parsing, taxonomy

ROWS = 20_000
PEOPLE = 1_000
CASES = ("lower", "upper", "title")
# Words before the age word, none of them an age (the word may stand anywhere).
BEFORE = ("", "Pt ", "Subject ", "Person ", "Donor ", "Resident ", "Member's ", "Current ", "Reported ")
# What may stand between the age word and its number: words, brackets, marks
# and approximation signs, each written with ordinary spaces (the spaces and
# dashes of the one definition are put in their places below).
BETWEEN = (
    " ", ": ", " at diagnosis: ", " in years: ", " (yrs): ", " ~", " approx. ", " about ", " c. ", " #", ".", ", ",
    "_", "( ", " = ", " - ", " -", "–", "：", " [y] ", " (in years) ", " at last visit, ", " at dx ",
    " at onset: ", " at death: ", " (approx) ", " ≈ ", " (est.) ", "­", " | ", "\n", ";",
)
# The age's unit after the number, the unit's mark, and whether a months part may follow it.
UNITS = (
    ("", 90, False), (" years", 90, True), (" yrs", 90, True), (" y", 90, True), ("y", 90, False), (" y/o", 90, False),
    ("-year-old", 90, False), (" years old", 90, False), (" months", 1080, False), (" mo", 1080, False),
    (" weeks", 4695, False), (" days", 32871, False), (" (years)", 90, False), (" [yrs]", 90, False),
)
PARTS = ("", " 3 months", " 11 mos", ", 2 months", " and 6 months", " 3 months 2 days")
GENDERS = ("", " M", " F", ", male", ", female", " / F", " - M", " male", " woman", ", M", " girl")
ENDS = ("", "?", ".", " (approx)", " on file")
FRAMES = ("{}", "{{{{{}}}}}", "<{}>", "({})", "[{}]")
# The words that are no age, each read as it was read before (the eleven
# families of lane HB2's skeptic and more): no age word, or a group's word
# after it.
NOT_AGES = (
    "Stage {}", "Grade {}", "Room {}", "Week {}", "Score {}", "Age group {}", "Agent {}", "Ages {}", "({})", "Aged care {}",
    "Page {}", "Wage {}", "Average {}", "Agency {}", "Aging {}", "Visit {}", "Bed {}", "Dosage {}", "Image {}",
    "Age-group {}", "Age band {}", "Age range {}-{}", "Age category {}", "Age cohort {}", "Mileage {}",
)


def _cased(word: str, how: str) -> str:
    if how == "upper":
        return word.upper()
    if how == "title":
        return word.title()
    return word


def _oracle() -> object:
    where = pathlib.Path(__file__).resolve().parents[1] / "tools" / "reference" / "make_generation_reference_vectors.py"
    spec = importlib.util.spec_from_file_location("oracle_age_phrases", where)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _spaces_and_dashes() -> "tuple[tuple[str, ...], tuple[str, ...]]":
    """The product's one definition of a space and its dashes, then the characters beyond it: every other separator and
    control or format character, every other dash and the marks that look like the vocabulary's (RULINGS 4 (2), C1)."""
    spaces = tuple(chr(code) for start, end in taxonomy._SCREEN_SPACE_RANGES for code in range(start, end + 1)
                   if not 0xD800 <= code <= 0xDFFF)
    beyond = tuple(
        chr(code) for code in range(0x110000)
        if unicodedata.category(chr(code)) in ("Zs", "Zl", "Zp", "Cc", "Cf", "Pd")
        and chr(code) not in spaces and chr(code) not in taxonomy._SCREEN_DASHES
    ) + ("：", "﹕", "∶", "︓", "꞉", "ː", "＝", "﹦", "＃", "～", "〜",
         "≈", "∼", "⁓")
    return spaces, beyond


def _families(draw: random.Random) -> "list[tuple[str, float, int, str]]":
    """The generated phrases: (cell, its number, its unit's mark, the cell as the top code writes it at the mark)."""
    found: "list[tuple[str, float, int, str]]" = []
    for word in taxonomy.AGE_VOCABULARY.before:
        for how in CASES:
            for between in BETWEEN:
                for unit, mark, parted in UNITS:
                    before = draw.choice(BEFORE)
                    part = draw.choice(PARTS) if parted else ""
                    gender = draw.choice(GENDERS)
                    end = draw.choice(ENDS)
                    frame = draw.choice(FRAMES)
                    top = {90: 125, 1080: 1500, 4695: 6500, 32871: 45000}[mark]
                    value = draw.randint(0, top) if draw.random() < 0.85 else draw.randint(90 * mark // 90, top)
                    written = f"{value:03d}" if mark == 90 and draw.random() < 0.15 else f"{value}"
                    coded_part = part
                    for figures in ("3", "11", "2", "6"):
                        coded_part = coded_part.replace(f" {figures} ", " 0 ")
                    head = f"{before}{_cased(word, how)}{between}"
                    tail = f"{unit}{part}{gender}{end}"
                    cell = frame.format(head + written + tail)
                    figures_at_mark = f"{mark}".rjust(len(written), "0") if written[:1] == "0" else f"{mark}"
                    coded = frame.format(head + figures_at_mark + f"{unit}{coded_part}{gender}{end}")
                    found += [(cell, float(value), mark, coded)]
    return found


# The line breaks of the one definition are spaces to an age's clause, a
# letter after them or not (lane HB3-a's repair 2, the orchestrator's LANE
# HB3-a RULINGS 9 (1); only a semicolon before a letter ends one,
# `taxonomy._PHRASE_BREAK`), so the families put them wherever an ordinary
# space stands.
LINE_BREAKS = ("\n", "\r", "\u0085", "\u2028", "\u2029")


def _with_spaces(draw: random.Random, cell: str, spaces: "tuple[str, ...]") -> str:
    """A cell with each ordinary space written as one of ``spaces``, drawn anew for each, a line break before a letter too."""
    written = ""
    for character in cell:
        written += draw.choice(spaces) if character == " " else character
    return written


def test_every_generated_age_phrase_is_read_with_its_number_and_top_coded_in_its_own_form() -> None:
    """Every word placement, connector, bracket, mark, approximation sign, unit, months part, gender and frame: the age is the first number after the word, in its unit; the top code writes the mark in the cell's own form, a months part `0`; product and oracle read the same.

    Red on a6c50ae7 (no phrase read: `Age at diagnosis: 95` is no number,
    `Age 95 M` 95 months, `Age -95` -95) and on the mutants of the clause
    limit, the gender rule, the months part and the generous skip
    (`K-HZ-35`'s record names them).
    """
    oracle = _oracle()
    draw = random.Random(4821)
    spaces, beyond = _spaces_and_dashes()
    seen = 0
    for cell, value, mark, coded in _families(draw) + _families(draw) + _families(draw):
        for written, coded_written in ((cell, coded), (_with_spaces(draw, cell, spaces), None)):
            read = taxonomy.safe_harbor_number(written, False, True, True)
            assert read is not None, repr(written)
            assert read.value == value and taxonomy.age_mark(read) == mark, (repr(written), read.value, taxonomy.age_mark(read))
            assert read.head + read.number + read.tail == written, repr(written)
            other = oracle._harbor_read(written, True)  # type: ignore[attr-defined]
            assert other is not None and float(other[5]) == value and other[0] == read.head, repr(written)
            years = value * 90 / mark
            if coded_written is not None and 90 <= years <= 125:
                assert taxonomy.top_coded_cells([written])[0] == coded_written, (repr(written), coded_written)
            elif years < 90 and not (mark != 90 and value * 90 / mark >= 89.99):
                assert taxonomy.top_coded_cells([written])[0] == written, repr(written)
            seen += 1
    # ...and every character of the one definition in each place, then each
    # character beyond it, each other dash and each look-alike mark between the
    # word and its number (C1: a fullwidth colon or a soft hyphen put no
    # question on the public head; 20 other dashes and 8 marks were unread).
    for character in spaces + beyond:
        # ...a line break before a letter among them (lane HB3-a's repair 2: `Age at<LF>last visit: 95`).
        patterns = ("Age{}95", "Pt age:{}95 M", "95{}years 3 months", "Age at{}last visit: 95")
        if character not in spaces:
            patterns = ("Age{}95", "Age {}95", "Age{} 95", "Pt age{}95 M", "Age{}95 years 3 months")
        for pattern in patterns:
            written = pattern.format(character)
            read = taxonomy.safe_harbor_number(written, False, True, True)
            assert read is not None and read.value == 95 and taxonomy.age_mark(read) == 90, repr(written)
            seen += 1
    assert seen > 15000


def test_words_that_are_no_age_read_as_they_did() -> None:
    """The eleven families that are no age (lane HB2's skeptic) and their kin read as without the age words: no age word, a group's word after it, or a clause break before the number."""
    draw = random.Random(4822)
    spaces, _beyond = _spaces_and_dashes()
    for pattern in NOT_AGES:
        for how in CASES:
            for _round in range(30):
                cell = _cased(pattern, how).format(draw.randint(0, 200), draw.randint(0, 200))
                cell = _with_spaces(draw, cell, spaces) if draw.random() < 0.5 else cell
                assert taxonomy.safe_harbor_number(cell, False, True, True) == taxonomy.safe_harbor_number(cell, False), repr(cell)
    # ...and an age word whose clause a semicolon before a letter ends reads none; A LINE BREAK THERE IS A SPACE TO THE
    # CLAUSE (lane HB3-a's repair 2, the orchestrator's LANE HB3-a RULINGS 9 (1)), so the number after it is read as an
    # age: the generous reading's false alarm, priced in P4-D482 (`Age: not given<LF>Room 95` is 95).
    for lead in ("Age: n/a", "Age unknown", "Aged: none", "Age: not given", "Pt age: not recorded"):
        for label in ("weight 95", "Score 95", "Room 95", "Week 95", "Stage 95", "BP 130/95"):
            for semicolon in (";", "; ", " ;", ";\t", " ; "):
                cell = f"{lead}{semicolon}{label}"
                assert taxonomy.safe_harbor_number(cell, False, True, True) is None, repr(cell)
            for line_break in LINE_BREAKS + ("\r\n", " \n", "\n\n"):
                cell = f"{lead}{line_break}{label}"
                read = taxonomy.safe_harbor_number(cell, False, True, True)
                assert read is not None and read.value == 95 and taxonomy.age_mark(read) == 90, repr(cell)
    # ...and a number in a clock, a date or a word is passed over for the next one.
    for cell, age in (("Age at 10:30: 95", 95), ("Age at 2nd visit: 95", 95), ("Age on 5/1/2024: 95", 95), ("Age V2 95", 95)):
        read = taxonomy.safe_harbor_number(cell, False, True, True)
        assert read is not None and read.value == age, repr(cell)


def test_a_dash_after_the_word_is_a_mark_and_leading_zeros_after_it_are_the_forms() -> None:
    """C2 and C8 of RULINGS 4 (2): `Age -95` and `Age<dash>95` are 95, never -95; a column of `Age 018` to `Age 099` is in the age reach, not judged a code by its zeros; a column of each is reached and top-coded.

    Red on a6c50ae7 (the sign read: -95, no reach; the zeros: no reach) and
    on the mutants that read the dash as a sign and the zeros as a code's.
    """
    for dash in taxonomy._SCREEN_DASHES:
        for pattern in ("Age {}95", "Age:{}95", "Age {} {}95", "Age{}95"):
            cell = pattern.format(dash, dash) if pattern.count("{}") == 2 else pattern.format(dash)
            read = taxonomy.safe_harbor_number(cell, False, True, True)
            assert read is not None and read.value == 95, repr(cell)
        column = [f"Age {dash}{age}" for age in range(18, 100)] * 4
        assert taxonomy.safe_harbor_reach(column, False, frozenset(), 11) == taxonomy.SAFE_HARBOR_AGES, repr(dash)
        assert all(not taxonomy.safe_harbor_number(cell, False, True, True).value > 90  # type: ignore[union-attr]
                   for cell in taxonomy.top_coded_cells(column))
    padded = [f"Age {age:03d}" for age in range(18, 100)] * 4
    assert taxonomy.safe_harbor_reach(padded, False, frozenset(), 11) == taxonomy.SAFE_HARBOR_AGES
    assert "Age 090" in taxonomy.top_coded_cells(padded) and "Age 095" not in taxonomy.top_coded_cells(padded)
    # ...a bare column of zero-filled numbers stays judged by its zeros (no word: P4-D401's padded question).
    assert taxonomy.safe_harbor_reach([f"{age:03d}" for age in range(18, 100)] * 4, False, frozenset(), 11) == ""


def test_a_capital_m_apart_from_an_age_is_a_gender_and_a_months_part_is_written_nought() -> None:
    """`Age 95 M` is 95 years, never 95 months; `095M` (DICOM's) and `6 m` stay months; `95 years 3 months` is 95 years and is top-coded `90 years 0 months` (RULING H6)."""
    for cell in ("Age 95 M", "95 M", "Age 95, M", "Pt age: 95 M", "95 y/o M", "Age 95 - M"):
        read = taxonomy.safe_harbor_number(cell, False, True, True)
        assert read is not None and read.value == 95 and taxonomy.age_mark(read) == 90, repr(cell)
    # ...and beside no age word a letter after spaces alone is read as the bare number reads it: a temperature in
    # Fahrenheit (`100.0 F`, the zoo's vital signs) stays the number it was, its description's bytes kept.
    for cell in ("100.0 F", "98.4 F", "95 F", "101.2 f"):
        assert taxonomy.safe_harbor_number(cell, False, True, True) == taxonomy.safe_harbor_number(cell, False), cell
    for cell, mark in (("095M", 1080), ("6 m", 1080), ("Age 95M", 1080), ("Age 14 months M", 1080)):
        read = taxonomy.safe_harbor_number(cell, False, True, True)
        assert read is not None and taxonomy.age_mark(read) == mark, repr(cell)
    for cell, coded in (("95 years 3 months", "90 years 0 months"), ("Age 95 yrs 11 mos", "Age 90 yrs 0 mos"),
                        ("97 years, 2 months and 3 days", "90 years, 0 months and 0 days"),
                        ("Age 95, male", "Age 90, male"), ("Age: 95.", "Age: 90."), ("89 years 11 months", "89 years 11 months")):
        assert taxonomy.top_coded_cells([cell])[0] == coded, cell


def test_the_phrase_puts_a_column_in_the_reach_and_the_vocabulary_names_it() -> None:
    """A column of each family is in the age reach and its words are recorded (`age_words_written`); the vocabulary carries the phrase's reach, its group words and its genders in its one place."""
    vocabulary = taxonomy.AGE_VOCABULARY
    assert vocabulary.reach == 40 and "group" in vocabulary.grouped and "care" in vocabulary.grouped
    assert "m" in vocabulary.genders and "female" in vocabulary.genders
    for pattern in ("Age at diagnosis: {}", "Age (yrs): {}", "Pt age: {}", "Age ~{}", "{} years 4 months", "{} y/o F",
                    "Age {} M", "Age {}, male", "Age：{}", "{} years old", "Age approx. {}", "Age #{}", "Age.{}",
                    "{{{{Age {}}}}}", "<Age {}>", "Age {}?", "Age: {} (approx)", "Age in years: {}", "Age {} yrs 3 mos",
                    "Age_{}", "Age, {}"):
        column = [pattern.format(age) for age in range(18, 100)] * 4
        assert taxonomy.safe_harbor_reach(column, False, frozenset(), 11) == taxonomy.SAFE_HARBOR_AGES, pattern
        assert taxonomy.age_words_written(column, False, frozenset()), pattern


# -- LANE HB3-a's REPAIR 1 (the orchestrator's LANE HB3-a RULINGS 6 and 7) ------
#
# Each class a skeptic found, closed by a generated case: every expected cell is
# built here from the template with each age past its unit's mark written as the
# mark, never read back through the product; the oracle writes the same twin.


def _capped(value: int, mark: int) -> int:
    return mark if value >= mark else value


def _agrees_with_the_oracle(oracle: object, column: "list[str]") -> None:
    """The product's top-code bound of a twin and the oracle's write the same cells, labels or not (A-P4-59)."""
    for labels in (False, True):
        product = taxonomy.at_most_the_top_code(column, frozenset(), 90, False, None, labels, True)
        other = oracle.safe_harbor_ages_twin(column, frozenset(), 90, False, None, labels, True)  # type: ignore[attr-defined]
        assert product == other, [(cell, mine, theirs) for cell, mine, theirs in zip(column, product, other) if mine != theirs][:3]


# Item 1: where a column writes both gender letters after its ages, or a gender word, a lone `m` is a gender, never months.
GENDER_HEADS = ("", "Age ", "Age: ", "Pt age ", "Aged ")
GENDER_JOINTS = ((" ", ""), ("", ""), (" (", ")"), ("(", ")"), (" [", "]"), (", ", ""), ("/", ""))
GENDER_AFTER = ("", ".", "?", " (est.)")


def test_where_a_column_writes_both_gender_letters_a_lone_m_after_an_age_is_a_gender_never_months() -> None:
    """Skeptic 1's item 1: every head, joint (apart, glued, bracketed, after a mark), mark after and letter case, in a column of both letters: in the reach and top-coded at 90 in each cell's own form, the oracle alike; a capital M with a point or in brackets is a gender alone too; a column of `m` alone keeps its months.

    Red on 0f96daf0: `Age NN m` beside `Age NN f`, `Age NN M.`, `Age NN (M)` and
    `NN m` beside `NN f` were read as months and published 15 spellings past
    90 and 620 real twin cells each at 20,000 rows.
    """
    oracle = _oracle()
    draw = random.Random(4841)
    columns = 0
    for head in GENDER_HEADS:
        for opening, closing in GENDER_JOINTS:
            for after in GENDER_AFTER:
                for letters in ("mf", "MF"):
                    ages = [draw.randint(18, 112) for _cell in range(50)] + [95, 104, 120]
                    written_letters = [letters[place % 2] for place in range(len(ages))]
                    column = [f"{head}{age}{opening}{letter}{closing}{after}" for age, letter in zip(ages, written_letters)]
                    expected = [f"{head}{_capped(age, 90)}{opening}{letter}{closing}{after}" for age, letter in zip(ages, written_letters)]
                    assert taxonomy.genders_beside_ages(column), column[:2]
                    assert taxonomy.safe_harbor_reach(column, False, frozenset(), 11) == taxonomy.SAFE_HARBOR_AGES, column[:2]
                    assert taxonomy.top_coded_cells(column) == expected, [
                        (cell, coded) for cell, coded in zip(column, taxonomy.top_coded_cells(column)) if coded not in expected][:3]
                    if not after:
                        # ...the oracle on one mark after of four (its reader is slow; THE SUITE'S TIME rule).
                        _agrees_with_the_oracle(oracle, column)
                    columns += 1
    # ...a capital M with a point or alone in brackets is a gender in a column of men alone (items 1 (a) and (b)).
    for pattern in ("Age {} M.", "Age {} (M)", "Age: {} [M]", "{} (M)", "Pt age {} M."):
        column = [pattern.format(age) for age in range(18, 112)]
        assert taxonomy.top_coded_cells(column) == [pattern.format(_capped(age, 90)) for age in range(18, 112)], pattern
        columns += 1
    # ...and a column writing `m` alone, or DICOM's months, keeps its months.
    for column in ([f"{age} m" for age in range(1, 120)], [f"{age:03d}M" for age in range(1, 120)]):
        assert not taxonomy.genders_beside_ages(column)
        assert taxonomy.top_coded_cells(column) == column, column[:3]
    assert columns == len(GENDER_HEADS) * len(GENDER_JOINTS) * len(GENDER_AFTER) * 2 + 5


def test_every_gender_word_beside_a_lone_m_makes_it_a_gender_never_months() -> None:
    """The combined verify's item 1 (the orchestrator's LANE HB3-a RULINGS 9 (1)): a column whose men write a lone `m` or `M` after their ages and whose women write a gender word of `AGE_GENDERS` -- `girl` and `boy` among them, which hold neither an m nor an f -- every head, joint and word: in the reach and top-coded at 90 in each cell's own form, the oracle alike.

    Red on d6da969f: a spelling holding neither an m nor an f was passed over
    by the column's gender rule, so `Age NN m` beside `Age NN girl` read the
    men's ages as months and, alone at 20,000 rows, published 10 spellings
    past 90 and wrote 540 real twin cells past 90.
    """
    oracle = _oracle()
    draw = random.Random(4851)
    words = [word for word in taxonomy.AGE_GENDERS if len(word) > 1]
    assert "girl" in words and "boy" in words
    heads = GENDER_HEADS + ("Pt age: ",)
    columns = 0
    for head in heads:
        for opening, closing in GENDER_JOINTS:
            for word in words:
                for letter in ("m", "M"):
                    ages = [draw.randint(18, 112) for _cell in range(30)] + [95, 104, 120]
                    written = [letter if place % 2 else word for place in range(len(ages))]
                    column = [f"{head}{age}{opening}{one}{closing}" for age, one in zip(ages, written)]
                    expected = [f"{head}{_capped(age, 90)}{opening}{one}{closing}" for age, one in zip(ages, written)]
                    assert taxonomy.genders_beside_ages(column), column[:2]
                    assert taxonomy.safe_harbor_reach(column, False, frozenset(), 11) == taxonomy.SAFE_HARBOR_AGES, column[:2]
                    coded = taxonomy.top_coded_cells(column)
                    assert coded == expected, [(cell, one) for cell, one in zip(column, coded) if one not in expected][:3]
                    if word in ("girl", "boy") and letter == "m" and head == heads[(columns // 2) % len(heads)]:
                        # ...the oracle on one head a joint (its reader is slow; THE SUITE'S TIME rule).
                        _agrees_with_the_oracle(oracle, column)
                    columns += 1
    assert columns == len(heads) * len(GENDER_JOINTS) * len(words) * 2


# Item 2: every age word opens its own clause and every age in it is read; numbers between the word and the age.
SEVERAL_AGES = (
    "Onset age {a}, current age {b}", "Age {a} at dx, age {b} now", "Mother age {a}, father age {b}",
    "Age {a} (onset {b})", "Age at onset {a}; age at death {b}", "Age at dx {a}, at surgery {b}, now {c}",
    "Age {a}, {b} and {c}", "Aged {a} yrs; age at last visit {b} yrs", "age {a} / age {b} / age {c}",
)
NUMBERS_BETWEEN = (
    "Age at visit {k}: {a}", "Age in {y}: {a}", "Age (DOB {y}): {a}", "Age on {mm}/{y}: {a}", "Age (as of {y}): {a}",
    "Age at dx ({y}): {a}", "Age at encounter #{k}: {a}", "Age, visit {k} of {k2}: {a}",
)


def test_every_age_word_opens_its_own_clause_and_every_age_in_it_is_top_coded() -> None:
    """Skeptic 1's item 2: two and three ages a cell, and a visit number, a year, a birth year or a month and year between the word and its age: each age past 89 written 90 in its form, the largest read, the oracle alike.

    Red on 0f96daf0: the phrase read one number of one age word (`Onset age 90,
    current age 105` was published, `Age in 2024: 95` read the year).
    """
    oracle = _oracle()
    draw = random.Random(4842)
    cells = 0
    for template in SEVERAL_AGES + NUMBERS_BETWEEN:
        column: "list[str]" = []
        expected: "list[str]" = []
        largest: "list[int]" = []
        for _cell in range(120):
            ages = {name: draw.randint(18, 112) for name in ("a", "b", "c")}
            others = {"k": draw.randint(1, 30), "k2": draw.randint(31, 60), "y": draw.randint(1925, 2026),
                      "mm": f"{draw.randint(1, 12):02d}"}
            column += [template.format(**ages, **others)]
            expected += [template.format(**{name: _capped(age, 90) for name, age in ages.items()}, **others)]
            # ...the largest number of 125 or less the cell writes: every number in an age's clause is an age (a visit
            # number among them, the generous reading), a year past 125 is passed over.
            largest += [max(int(figures) for figures in re.findall(r"[0-9]+", column[-1]) if int(figures) <= 125)]
        assert taxonomy.top_coded_cells(column) == expected, [
            (cell, coded) for cell, coded in zip(column, taxonomy.top_coded_cells(column)) if coded not in expected][:3]
        for cell, age in zip(column, largest):
            assert taxonomy._safe_harbor_kind(cell, False)[2] == age, (cell, age)
            cells += 1
        assert taxonomy.safe_harbor_reach(column, False, frozenset(), 11) == taxonomy.SAFE_HARBOR_AGES, template
        _agrees_with_the_oracle(oracle, column)
    assert cells == 120 * (len(SEVERAL_AGES) + len(NUMBERS_BETWEEN))


# Item 3 (and the statistics check's item 7): a number its age's unit or affix follows is an age wherever it stands.
WORDS_BEFORE = ("A ", "Pt is ", "Pt is a ", "Female, ", "M, ", "Patient: ", "Seen today, ", "Reported as ")
GENDERS_AFTER = ("", " M", " F", " man", " woman", ", male", " (F)")


def _unit_cells(draw: random.Random) -> "list[tuple[str, int, int]]":
    """(unit as written after the number, its mark, the most a drawn value reaches) for every unit word and affix of the vocabulary."""
    found: "list[tuple[str, int, int]]" = []
    marks = {"y": 90, "m": 1080, "w": 4695, "d": 32871}
    for unit, letter in taxonomy.AGE_VOCABULARY.units:
        found += [(draw.choice((" ", "")) + unit, marks[letter], marks[letter] * 4 // 3)]
    for affix in taxonomy.AGE_VOCABULARY.affixes:
        unit = affix.split("-")[0].split(" ")[0].split("/")[0]
        letter = taxonomy.AGE_UNIT_WORDS[unit] if unit in taxonomy.AGE_UNIT_WORDS else "y"
        found += [((" " if affix[0] not in "-" else "") + affix, marks[letter], marks[letter] * 4 // 3)]
    return found


def test_a_number_its_age_unit_or_affix_follows_is_an_age_wherever_it_stands() -> None:
    """Skeptic 1's item 3: words before the number, every unit word and affix of the vocabulary, a gender after it; and a figure right after the age word (`Pt age96`, the statistics check's item 7): each read and top-coded at its unit's mark, the oracle alike.

    Red on 0f96daf0: `A NN-year-old man`, `Female, NN years old` and `Pt is NN
    years old` put no question and a column of each published 29 spellings
    past 90; `Pt age96` was passed over as a figure in a word.
    """
    oracle = _oracle()
    draw = random.Random(4843)
    columns = 0
    for before in WORDS_BEFORE:
        for unit, mark, most in _unit_cells(draw):
            gender = draw.choice(GENDERS_AFTER)
            values = [draw.randint(0, most) for _cell in range(40)] + [mark, mark + 1, most]
            column = [f"{before}{value}{unit}{gender}" for value in values]
            expected = [f"{before}{_capped(value, mark)}{unit}{gender}" for value in values]
            assert taxonomy.top_coded_cells(column, genders=False) == expected, [
                (cell, coded) for cell, coded in zip(column, taxonomy.top_coded_cells(column, genders=False))
                if coded not in expected][:3]
            assert taxonomy.safe_harbor_reach(column, False, frozenset(), 11, genders=False) == taxonomy.SAFE_HARBOR_AGES, column[:2]
            columns += 1
    for template in ("Pt age{}", "Pt age{} yrs", "Subject age{} M", "Pt age{}y", "Seen at age{}, well"):
        column = [template.format(age) for age in range(18, 112)]
        assert taxonomy.top_coded_cells(column) == [template.format(_capped(age, 90)) for age in range(18, 112)], template
        _agrees_with_the_oracle(oracle, column)
        columns += 1
    assert columns == len(WORDS_BEFORE) * len(_unit_cells(random.Random(0))) + 5


def test_an_age_unit_after_zero_filled_figures_makes_the_zeros_the_forms() -> None:
    """Skeptic 1's item 4: a zero-filled age with every unit word and affix of the vocabulary and no age word is in the reach and top-coded as wide as it writes (`090 years`), however many cells are padded.

    Red on 0f96daf0: `0NN years` and `0NN y/o F` put only the code question
    and a column of each published 15 and 29 spellings past 90.
    """
    draw = random.Random(4844)
    columns = 0
    for unit, mark, most in _unit_cells(draw):
        width = len(f"{most}") + 1
        values = [draw.randint(0, most) for _cell in range(60)] + [mark, most]
        column = [f"{value:0{width}d}{unit}" for value in values]
        expected = [f"{_capped(value, mark):0{width}d}{unit}" for value in values]
        assert taxonomy.safe_harbor_reach(column, False, frozenset(), 11) == taxonomy.SAFE_HARBOR_AGES, column[:2]
        assert taxonomy.top_coded_cells(column) == expected, [
            (cell, coded) for cell, coded in zip(column, taxonomy.top_coded_cells(column)) if coded not in expected][:3]
        columns += 1
    assert columns == len(_unit_cells(random.Random(0)))


# Item 5: a gender after a mark makes a number standing first an age.
GENDER_MARKS = (",", ", ", "/", " / ", "-", " - ", " (", "(")


def test_a_gender_after_a_mark_makes_a_number_standing_first_an_age() -> None:
    """Skeptic 1's item 5: each mark, both letter cases and the gender words after a number standing first: read as an age; a column of one letter (no column rule) in the reach and top-coded.

    Red on the mutant that reads no mark (`marked` never set in
    `taxonomy._a_gender_at`): `NN/F`, `NN - F` and `(NN, F)` left the reach.
    """
    for mark in GENDER_MARKS:
        closing = ")" if "(" in mark else ""
        for gender in ("F", "f", "M", "female", "Male", "woman"):
            for age in (17, 95, 104):
                for frame in ("{}", "({})", "[{}]"):
                    cell = frame.format(f"{age}{mark}{gender}{closing}")
                    read = taxonomy.safe_harbor_number(cell, False, True, True)
                    assert read is not None and read.value == age and taxonomy.age_mark(read) == 90, repr(cell)
        column = [f"{age}{mark}F{closing}" for age in range(18, 112)]
        assert not taxonomy.genders_beside_ages(column)
        assert taxonomy.safe_harbor_reach(column, False, frozenset(), 11) == taxonomy.SAFE_HARBOR_AGES, mark
        assert taxonomy.top_coded_cells(column) == [f"{_capped(age, 90)}{mark}F{closing}" for age in range(18, 112)], mark


def test_the_clause_reaches_forty_characters_and_no_further() -> None:
    """Skeptic 1's item 7: an age word and its number 40 characters apart are read, 41 apart not, a point before the number counted with it.

    Red on the mutant that drops the clause's reach (`AGE_PHRASE_REACH` read
    nowhere): the number 41 characters on is read.
    """
    for word in ("Age", "Pt age", "aged"):
        for filler in ("x", "y", "words "):
            gap = (" " + (filler * 40))[:39] + " "
            cell = f"{word}{gap}95"
            assert len(gap) == taxonomy.AGE_PHRASE_REACH
            read = taxonomy.safe_harbor_number(cell, False, True, True)
            assert read is not None and read.value == 95, repr(cell)
            assert taxonomy.safe_harbor_number(f"{word}{gap} 95", False, True, True) is None, repr(cell)
            assert taxonomy.safe_harbor_number(f"{word}{gap}.95", False, True, True) is None, repr(cell)


# The statistics check's items 1 and 2: a unit named between the word and its number; a gender after a unit and a slash.
NAMED_UNITS = (("months", 1080), ("weeks", 4695), ("days", 32871))
NAMINGS = ("Age ({u}): {v}", "Age in {u}: {v}", "Age, {u}: {v}", "Age [{u}] {v}", "Age ({s}.): {v}", "Pt age in {u} {v}")


def test_a_unit_named_after_the_age_word_is_its_numbers_unit() -> None:
    """The statistics check's item 1: months, weeks and days named in brackets, after `in`, as a word of its own or abbreviated: each number read in that unit and top-coded at its mark, the oracle alike.

    Red on 0f96daf0: `Age (months): NNNN` and `Age in days: NNNNN` were read in
    years, past 125, and a column of each published 59 and 70 ages past 89.
    """
    oracle = _oracle()
    draw = random.Random(4845)
    for unit, mark in NAMED_UNITS:
        short = {"months": "mos", "weeks": "wks", "days": "dys"}[unit]
        for naming in NAMINGS:
            values = [draw.randint(0, mark * 4 // 3) for _cell in range(80)] + [mark, mark + 1]
            column = [naming.format(u=unit, s=short, v=value) for value in values]
            expected = [naming.format(u=unit, s=short, v=_capped(value, mark)) for value in values]
            assert taxonomy.safe_harbor_reach(column, False, frozenset(), 11) == taxonomy.SAFE_HARBOR_AGES, naming
            assert taxonomy.top_coded_cells(column) == expected, [
                (cell, coded) for cell, coded in zip(column, taxonomy.top_coded_cells(column)) if coded not in expected][:3]
            _agrees_with_the_oracle(oracle, column)


def test_a_gender_after_a_unit_and_a_slash_or_against_a_unit_of_years_ends_the_unit() -> None:
    """The statistics check's item 2: `NNy/G`, `Age NNy/G`, `NN yrs/G`, `NN y/oG`, `Pt age: NNyG`, both cases: read in years and top-coded, the oracle alike; `NN mm` stays no age with a gender.

    Red on 0f96daf0: `NNy/G` and `Age NNy/G` were read as no number and a
    column of each published 29 ages past 89.
    """
    oracle = _oracle()
    for template in ("{a}y/{g}", "Age {a}y/{g}", "{a} yrs/{g}", "{a} y/o{g}", "Pt age: {a}y{g}", "{a}yr/{g}", "{a} y.o/{g}",
                     "{a} mo/{g}"):
        mark = 1080 if "mo/" in template else 90
        for letters in ("MF", "mf"):
            ages = list(range(18, 112)) + [mark, mark + 9]
            column = [template.format(a=age, g=letters[age % 2]) for age in ages]
            expected = [template.format(a=_capped(age, mark), g=letters[age % 2]) for age in ages]
            assert taxonomy.top_coded_cells(column) == expected, [
                (cell, coded) for cell, coded in zip(column, taxonomy.top_coded_cells(column)) if coded not in expected][:3]
            _agrees_with_the_oracle(oracle, column)
    assert taxonomy.safe_harbor_number("95 mm", False, True, True) == taxonomy.safe_harbor_number("95 mm", False)


# RULINGS 6 (1): X2 and X3, the characters of the one definition in every owed position, each against its control.
OWED_SPACES = (
    "\t", "\n", "\r", "\x0c", "\x0b", "\x85", "\xa0", "\u1680", *[chr(code) for code in range(0x2000, 0x2010)],
    "\u2028", "\u2029", "\u202f", "\u205f", "\u2060", "\u3000", "\ufeff",
)
OWED_CONTROLS = (
    "Age 95", "Age: 97 years", "97 years old", "95 y/o F", "Pt age 96", "Age at diagnosis: 99", "Age 95 yrs 3 mos",
    "93", "Age 104 M", "Seen at age 98 today", "A 95-year-old woman", "Age - 96",
)


def _variants(control: str, mark: str, dash: bool) -> "list[str]":
    """A control with ``mark`` put in each owed position: every ordinary space (a dash, for a dash) replaced, only the first, doubled, beside an ordinary one on either side, leading, trailing, and, for a character that prints nothing, inside the first word.

    A line break before a letter is an owed position like any other (lane
    HB3-a's repair 2, the orchestrator's LANE HB3-a RULINGS 9 (1)): the
    build's case left those placings out, and `Age<LF>at diagnosis: 95`
    alone published its ages past 90."""
    ordinary = "-" if dash else " "
    found: "list[str]" = []
    if ordinary in control:
        found += [control.replace(ordinary, mark), control.replace(ordinary, mark, 1), control.replace(ordinary, mark + mark, 1),
                  control.replace(ordinary, ordinary + mark, 1), control.replace(ordinary, mark + ordinary, 1)]
    if not dash:
        found += [mark + control, control + mark]
        first = control.split(" ")[0]
        if len(first) >= 2 and taxonomy._prints_nothing(mark):
            found += [first[:1] + mark + first[1:] + control[len(first):]]
    return found


def test_every_owed_space_dash_and_mark_that_prints_nothing_reads_as_its_control() -> None:
    """THE ORCHESTRATOR'S LANE HB3-a RULINGS 6 (1): the 31 owed spaces and format characters, the eleven dashes and the soft hyphen, in every owed position and inside the first word, each read by the age reach as its control written with the ordinary mark reads: the same age in years, top-coded where it is past 89.

    Red on 0f96daf0: X2, `<U+200B>95` and `95<U+200B>`, were cut at the cell's
    edges by Python's whitespace and read as no number (87 levels with every
    age 90 to 104 published and 3,220 twin cells past 90 at 20,000 rows); X3,
    `Ag<U+200B>e 95`, read no age word.
    """
    misses: "list[str]" = []
    variants = 0
    marks = [(mark, False) for mark in OWED_SPACES + ("\u00ad",)] + [(mark, True) for mark in taxonomy._SCREEN_DASHES]
    for control in OWED_CONTROLS:
        expected = taxonomy._safe_harbor_kind(control, False)
        assert expected[0] in (taxonomy._AGE_ABOVE, taxonomy._AGE_ABOVE_PADDED), control
        coded = taxonomy.top_coded_cells([control])[0]
        for mark, _dash in marks[: len(OWED_SPACES) + 1]:
            # ...a mark at the cell's edge is an edge space, kept where it stands: the top code writes the cell's form.
            if taxonomy.top_coded_cells([mark + control, control + mark]) != [mark + coded, coded + mark]:
                misses += ["edge not kept: " + repr(mark + control)]
        for mark, dash in marks:
            for variant in _variants(control, mark, dash):
                read = taxonomy._safe_harbor_kind(variant, False)
                if read[0] != expected[0] or read[2] != expected[2]:
                    misses += [repr(variant)]
                elif taxonomy.top_coded_cells([variant]) == [variant]:
                    misses += ["not top-coded: " + repr(variant)]
                variants += 1
    assert misses == [], misses[:10]
    assert variants > 2500


def _ages(seed: int) -> "list[int]":
    draw = random.Random(seed)
    ages: "list[int]" = []
    for person in range(PEOPLE):
        age = max(18, min(105, round(draw.gauss(60, 17))))
        ages += [draw.randint(90, 105) if person % 33 == 0 else age]
    return ages


def test_at_the_owner_floor_a_column_of_age_phrases_alone_is_asked_and_top_coded(tmp_path: pathlib.Path) -> None:
    """A column of age phrases alone in its table (20,000 rows, 1,000 made-up people of 20 rows, no other column), nobody at the keyboard: the Safe Harbor question is put, the top code 90 written in each cell's own form, no age past 89 shown in any file and none in the twin, and the twin validates.

    Red on a6c50ae7: the column put no Safe Harbor question and its ages
    past 90 were published as levels and written in the twin.
    """
    families = ("Age at diagnosis: {a}", "Age {a} {g}", "{a} years {m} months", "Pt age: {a}", "Age ~{a}", "{a} y/o {g}",
                "Age -{a}", "Age {a:03d}", "Age：{a}", "Age (yrs): {a}")
    draw = random.Random(4823)
    ages = _ages(4823)
    source = tmp_path / "phrases.csv"
    real_past: "set[str]" = set()
    with open(source, "w", newline="", encoding="utf-8") as handle:
        out = csv.writer(handle, lineterminator="\n")
        out.writerow(["label"])
        for person in range(PEOPLE):
            family = families[person % len(families)]
            gender = draw.choice("MF")
            months = draw.randint(0, 11)
            cell = family.format(a=ages[person], g=gender, m=months)
            if ages[person] > 90:
                real_past.add(cell)
            for _row in range(ROWS // PEOPLE):
                out.writerow([cell])
    assert len(real_past) >= 20
    sink = io.StringIO()
    keep = cli._there_is_somebody_to_ask
    cli._there_is_somebody_to_ask = lambda: False  # type: ignore[assignment]
    try:
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            assert cli.main(["profile", str(source), "--out-dir", str(tmp_path)]) == 0
            description = tmp_path / "phrases-profile.json"
            assert cli.main(["generate", str(description), "--out-dir", str(tmp_path), "--seed", "0"]) == 0
            code = cli.main(["validate", str(description), "--twin", str(tmp_path / "phrases-twin.csv"),
                             "--out-dir", str(tmp_path)])
    finally:
        cli._there_is_somebody_to_ask = keep  # type: ignore[assignment]
    assert code == 0, sink.getvalue()[-2000:]
    document = json.loads(description.read_text(encoding="utf-8"))
    block = next(column for column in document["columns"] if column["name"] == "label")
    assert block.get("top_coded") == 90 and block.get("top_coded_words"), block.get("role")
    questions = json.loads((tmp_path / "phrases-questions.json").read_text(encoding="utf-8"))
    offered = [[choice.get("answer") for choice in entry["answers_you_can_give"]]
               for entry in questions.get("asked") or [] if isinstance(entry, dict) and entry.get("column") == "label"]
    assert any("yes" in answers and "no" in answers for answers in offered), offered
    for name in ("phrases-profile.json", "phrases-questions.json", "phrases-profile.txt"):
        text = (tmp_path / name).read_text(encoding="utf-8")
        assert not [spelling for spelling in real_past if spelling in text], name
    assert not [spelling for spelling in real_past if spelling in sink.getvalue()]
    with open(tmp_path / "phrases-twin.csv", encoding="utf-8") as handle:
        cells = [row[0] for row in csv.reader(handle)][1:]
    # ...each twin cell's age read by this test on its own: the first run of figures (every family writes its age first).
    past = [cell for cell in cells if re.search(r"[0-9]+", cell) and int(re.search(r"[0-9]+", cell).group(0)) > 90]  # type: ignore[union-attr]
    assert not past, past[:5]


# -- THE KEY ROOM (part C: limits (ae) and (af)) -------------------------------


def _block_strings(node: object, into: "set[str]") -> None:
    """Every string a description block holds, keys and values, at any depth: what it publishes."""
    if isinstance(node, str):
        into.add(node)
    elif isinstance(node, dict):
        for key, inner in node.items():
            into.add(f"{key}")
            _block_strings(inner, into)
    elif isinstance(node, list):
        for inner in node:
            _block_strings(inner, into)


def _key_facts(openings: "dict[int, str]", noughts: "list[int]", forms: "dict[str, int]") -> contract.TextFacts:
    return contract.TextFacts(
        length=contract.LengthStats(minimum=4, maximum=40, mean=None, p50=None),
        words=contract.WordStats(minimum=1, maximum=3, mean=None), n_all_digits=3, n_code_alphabet=5,
        n_distinct_by_occurrences={"1": 7}, shape_forms=forms, figure_openings=openings, figure_noughts=tuple(noughts),
    )


def _runs(cell: str) -> "list[str]":
    """The maximal runs of figures of a cell, each with its noughts before it dropped (noughts alone kept as one nought)."""
    return [run.lstrip("0") or "0" for run in re.findall(r"[0-9]+", cell)]


def test_no_held_stand_in_is_a_real_key_or_holds_a_real_run_over_generated_key_shapes() -> None:
    """THE ROOM TEST at the held walk's write (`generation._figure_runs_off_the_real`), over generated key shapes: widths
    3 to 12, one and two letters before and after, keys of noughts alone, two forms in one column, lists of one to three
    keys, dense and sparse spans; stand-ins drawn INSIDE the real span (real keys themselves, their neighbours, noughts
    alone's neighbours at the key's width, the scale's numbers): no written cell equals a real key, exact or with its
    noughts dropped, and none holds a real run of four figures or more; beside a held key of noughts alone no run of
    noughts alone is written at a width such a key holds (each is renamed by the room at its own width, a filling no
    real run holds; only where every room of the width is spent are noughts written, then wider than every width
    named; the statistics check's item 6: this sentence said a one and noughts were written).

    Red on the mutant that writes noughts alone at a width a held key of noughts alone holds (limit (af): `Q00000`
    among `Q00001` upward, 497 twin cells at 20,000 rows on a6c50ae7).
    """
    draw = random.Random(4831)
    shapes = 0
    for _shape in range(1500):
        width = draw.randint(4, 12)
        letters = draw.choice(["", "R", "MR", "Q", "AB"])
        after = draw.choice(["", "", "X", "Z9"])
        dense = draw.random() < 0.6
        start = draw.randint(10 ** (width - 1), 10 ** width - 2000)
        count = draw.randint(30, 400)
        numbers = list(range(start, start + count)) if dense else draw.sample(range(10 ** (width - 1), 10 ** width), count)
        real = [f"{letters}{number}{after}" for number in numbers]
        if draw.random() < 0.5:
            # ...a second form in the same column: bare numbers beside the lettered ones (limit (ae)).
            real += [f"{number}" for number in numbers[: count // 2]]
        if draw.random() < 0.4:
            real += [f"{letters}{'0' * width}{after}"]
        openings = {int(key): value for key, value in taxonomy.figure_openings(real, 1).items()}
        noughts = taxonomy.noughts_widths(real, [])
        forms = {parsing.shape_form(cell): 5 for cell in real[:3]}
        facts = _key_facts(openings, noughts, forms)
        stand_ins = real[: count // 3] + [f"{letters}{number + 1}{after}" for number in numbers[: count // 3]]
        stand_ins += [f"{letters}{'0' * (width - 1)}1{after}", f"{letters}{'0' * (width - 2)}12{after}"]
        stand_ins += [";".join(draw.sample(real, min(len(real), draw.randint(1, 3)))) for _list in range(20)]
        written, _spent = generation._figure_runs_off_the_real(stand_ins, facts, ())
        real_cells = set(real)
        held_runs = {run for cell in real for run in _runs(cell) if len(run) >= 4}
        for cell in written:
            for token in cell.split(";"):
                assert token not in real_cells, (token, width, letters)
                assert not [run for run in _runs(token) if run in held_runs], token
                # ...and no run of noughts alone at a width a held key of noughts alone holds (the merged reading,
                # which reads every run of noughts alone as one, is the stated residue: P4-D482 (a)).
                assert not [run for run in re.findall(r"[0-9]+", token) if set(run) == {"0"} and len(run) in noughts], token
                assert not [run for run in held_runs if run in token and token not in real_cells], token
        shapes += 1
    assert shapes == 1500


def test_where_every_room_of_a_held_noughts_width_is_spent_a_wider_filling_is_written_never_noughts_alone() -> None:
    """The combined verify's item 3 (the orchestrator's LANE HB3-a RULINGS 9 (2)): beside a held key of noughts alone
    (`K0000` among keys `K1000` to `K2999`, the free opening `5` named at four figures), the walk's rooms are spent in
    turn -- the opening's thousand fillings by the first thousand stand-ins, the narrower widths' 999 by the next -- and
    the last stand-in and the key of noughts alone are written as the wider filling (`K55000`, `K55001`), never as
    noughts alone, which once each run's noughts are dropped reads as the held key (limit (af)'s merged reading).

    Red on the mutant that drops `barred` in `generation._renamed_run` (noughts alone passed over only where taken):
    the two-thousandth stand-in is written `K00000`.
    """
    real = [f"K{1000 + key}" for key in range(2000)] + ["K0000"]
    noughts = taxonomy.noughts_widths(real, [])
    assert noughts == [4]
    facts = _key_facts({4: "5"}, noughts, {parsing.shape_form("K1000"): 5})
    written, spent = generation._figure_runs_off_the_real(real, facts, ())
    merged_real = {_runs_merged(cell) for cell in real}
    # ...every stand-in renamed: a thousand at the free opening, 999 narrower, the last and the noughts' key wider.
    assert written[-2:] == ["K55000", "K55001"] and len(set(written)) == len(written), written[-2:]
    for cell in written:
        assert cell not in real and _runs_merged(cell) not in merged_real, cell
        assert not [run for run in re.findall(r"[0-9]+", cell) if set(run) == {"0"}], cell
    assert spent == [2, 0], spent


def _runs_merged(cell: str) -> str:
    """A key with the noughts before each run of figures dropped, a run of noughts alone kept as one nought."""
    return re.sub(r"(?<![0-9])0+(?=[0-9])", "", cell)


def test_the_description_names_the_noughts_widths_and_holds_back_a_mean_inside_the_keys() -> None:
    """`taxonomy.noughts_widths` names the widths of held runs of noughts alone (a width, never a value), the published
    levels set aside; `taxonomy._a_mean_inside_the_keys` says nothing of a scale whose mean lies inside the span of
    held-back numbers of four figures or more (limit (ae): a mean of `1003475.0` was a real key)."""
    assert taxonomy.noughts_widths(["Q00000", "Q00001", "A000-0000", "X00", "R0001"], ["Q00001"]) == [3, 4, 5]
    assert taxonomy.noughts_widths(["Q00000"], ["Q00000"]) == []
    held = [f"{1003000 + key}" for key in range(950)] + ["R1", "R2"]
    assert taxonomy._a_mean_inside_the_keys({"n_cells": 950, "mean": 1003475.0}, held, ["R1"])
    assert not taxonomy._a_mean_inside_the_keys({"n_cells": 950, "mean": 99.5}, held, [])
    assert not taxonomy._a_mean_inside_the_keys({"n_cells": 0, "mean": None}, held, [])
    assert not taxonomy._a_mean_inside_the_keys({"n_cells": 3, "mean": 50.0}, ["12", "88", "50"], [])


def test_at_the_owner_floor_held_keys_of_two_forms_and_of_noughts_alone_are_never_written(tmp_path: pathlib.Path) -> None:
    """One table at 20,000 rows, nobody at the keyboard: a label column of two key forms (`R` and six figures beside
    bare six figures, each once), one of keys zero-filled from nought (`Q00000` upward), and one of two key forms whose
    published numbers bracket the held numbers' span, each beside a word on 30 per cent of rows. No twin cell equals a
    real held key; the second column's width of noughts alone is named.

    Red on a6c50ae7 (2,800, 538 and 2,121 twin cells equal to a real held key: limits (ae) and (af)), on the mutant
    that keeps the classes' numbers as drawn (3,181 on the third column) and on the one that drops the noughts' width.
    """
    draw = random.Random(4836)
    refs: "list[str]" = []
    codes: "list[str]" = []
    spans: "list[str]" = []
    counter = [0, 0, 0]
    for row in range(ROWS):
        # ...and a column of two key forms whose published numbers bracket the held numbers' span (`500000` and
        # `510000`, 1,000 rows each), so the classes walk the held-back numbers inside it (limit (ae) on the ladder).
        if row % 10 == 0:
            spans += ["500000" if row % 20 == 0 else "510000"]
        elif draw.random() < 0.3:
            spans += ["pending"]
        else:
            k = counter[2]
            spans += [f"Z{300000 + k}" if k % 2 else f"{500001 + k // 2}"]
            counter[2] += 1
        if draw.random() < 0.3:
            refs += ["pending"]
        else:
            k = counter[0]
            refs += [f"R{100000 + k}" if k % 2 else f"{500000 + k}"]
            counter[0] += 1
        if draw.random() < 0.3:
            codes += ["pending"]
        else:
            codes += [f"Q{counter[1]:05d}"]
            counter[1] += 1
    source = tmp_path / "keys.csv"
    with open(source, "w", newline="", encoding="utf-8") as handle:
        out = csv.writer(handle, lineterminator="\n")
        out.writerow(["ref", "code", "span"])
        out.writerows(zip(refs, codes, spans))
    sink = io.StringIO()
    keep = cli._there_is_somebody_to_ask
    cli._there_is_somebody_to_ask = lambda: False  # type: ignore[assignment]
    try:
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            assert cli.main(["profile", str(source), "--out-dir", str(tmp_path)]) == 0
            assert cli.main(["generate", str(tmp_path / "keys-profile.json"), "--out-dir", str(tmp_path), "--seed", "0"]) == 0
    finally:
        cli._there_is_somebody_to_ask = keep  # type: ignore[assignment]
    document = json.loads((tmp_path / "keys-profile.json").read_text(encoding="utf-8"))
    blocks = {block["name"]: block for block in document["columns"]}
    with open(tmp_path / "keys-twin.csv", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))[1:]
    found: "dict[str, int]" = {}
    for place, (name, real) in enumerate((("ref", refs), ("code", codes), ("span", spans))):
        published: "set[str]" = set()
        _block_strings(blocks[name], published)
        held = {cell for cell in real if cell != "pending" and cell not in published}
        found[name] = sum(1 for row in rows if row[place] in held)
    assert found == {"ref": 0, "code": 0, "span": 0}, found
    assert blocks["code"].get("figure_noughts") == [5], blocks["code"].get("figure_noughts")
    # ...AND THE HELD-BACK SCALE PRINTS NO NUMBER INSIDE THE HELD KEYS' SPAN (skeptic 1's item 6; red on the call of
    # `taxonomy._a_mean_inside_the_keys` dropped from the label block, where `span` published the mean 503154.5, a
    # real key's neighbour, and `ref` 507069.0): its mean is withheld, and no number of either block lies in the span.
    for name, real in (("ref", refs), ("span", spans)):
        held_numbers = [int(cell) for cell in real if cell.isdigit() and cell not in ("500000", "510000")]
        least, most = min(held_numbers), max(held_numbers)
        assert blocks[name].get("suppressed_numbers") == {"n_cells": 0, "mean": None}, (name, blocks[name].get("suppressed_numbers"))
        numbers: "list[float]" = []
        _block_numbers(blocks[name], numbers)
        assert not [number for number in numbers if least <= number <= most], name


def _block_numbers(node: object, into: "list[float]") -> None:
    """Every number a description block holds, at any depth."""
    if isinstance(node, bool):
        return
    if isinstance(node, (int, float)):
        into.append(float(node))
    elif isinstance(node, dict):
        for inner in node.values():
            _block_numbers(inner, into)
    elif isinstance(node, list):
        for inner in node:
            _block_numbers(inner, into)


def test_the_phrase_legs_counter_reads_every_file_the_bar_names(tmp_path: pathlib.Path) -> None:
    """Skeptic 1's item 8: `K-HZ-35`'s counter (`tests/age_phrase_counts.py`) reads the screen, the description, its summary, the questions file, generate's twin report and validate's quality file: a spelling past 89 written in any of them alone is counted, the top code's own spelling aside.

    Red on the counter of 0f96daf0's driver, which read the first four alone.
    """
    twin = tmp_path / "twin"
    twin.mkdir()
    written_in = {"t-profile.json": "Age 91 M", "t-profile.txt": "Age 92 F", "t-questions.json": "Age 93 M"}
    for name, spelling in written_in.items():
        (tmp_path / name).write_text(f"... {spelling} ...", encoding="utf-8", newline="\n")
    (twin / "t-twin-report.txt").write_text("levels: Age 94 F (11)", encoding="utf-8", newline="\n")
    (twin / "t-twin-quality.txt").write_text("missed: Age 95 M", encoding="utf-8", newline="\n")
    texts = age_phrase_counts.texts_of(tmp_path, twin, "t", "screen: Age 96 F")
    past = {f"Age {age} {letter}" for age in range(90, 99) for letter in "MF"}
    assert age_phrase_counts.shown(past, texts, True) == {
        "Age 91 M", "Age 92 F", "Age 93 M", "Age 94 F", "Age 95 M", "Age 96 F"}
    # ...a spelling JSON writes escaped (a character that prints nothing) is counted too.
    (tmp_path / "t-profile.json").write_text(json.dumps({"levels": ["\u200b97"]}), encoding="utf-8", newline="\n")
    texts = age_phrase_counts.texts_of(tmp_path, twin, "t", "")
    assert age_phrase_counts.shown({"\u200b97"}, texts, True) == {"\u200b97"}
    # ...and one the text files show as the product shows a value, a line feed written out (lane HB3-a's repair 2: red
    # on the counter that looks for the spelling as written and as JSON writes it alone).
    (twin / "t-twin-report.txt").write_text(
        "levels: " + parsing.visible("Age\nat diagnosis: 98"), encoding="utf-8", newline="\n")
    texts = age_phrase_counts.texts_of(tmp_path, twin, "t", "")
    assert age_phrase_counts.shown({"Age\nat diagnosis: 98"}, texts, True) == {"Age\nat diagnosis: 98"}
    assert age_phrase_counts.years_of("Age (months): 1085", 12.0) == 1085 / 12
