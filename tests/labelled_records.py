"""Record numbers beside labels, names joined to record numbers and one-word codes (plan P4-D469): invented look-alikes.

Every value here is made up by this module's own makers and seeds, with
generic column names; nothing is copied from anywhere. Three classes of
identifier spelling that batch 4q's checks measured publishing real
values, or writing them on the twin, while nothing was declared or
answered (lane CZ-A2):

1. A RECORD NUMBER BESIDE ITS LABEL, WRITTEN WITH A SIGN, A MARK OR A
   CHECK LETTER, one a row: `#MR1000013`, `* MR1000013`, `@mr1000013`,
   `MR.1000013`, `MR: 1000013`, `MR 1000013`, `MR1000013A`, `#1000013`
   (`label_spelling`). Read as an affixed number, `#MR` and the number
   wrote 19,999 of 20,000 twin cells equal to a real one.
2. A NAME AND A RECORD NUMBER JOINED BY ONE MARK: `Cedar,Abc,1000013`,
   with a semicolon, a bar, a tab, a caret or an underscore, spaces beside
   the mark or none, the number first or last (five figures or more, a flag
   after it), two to four parts of the name, empty parts among them or after
   them (`joined_name`). Read as an affixed number, or one a person as labels,
   the names were published and the twin wrote the real cells.
3. ONE-WORD CODES WITH A RUN OF FIVE FIGURES OR MORE, a label letter or an
   accession's capitals glued to the run (`MR1000013`, `S24-012345`,
   `24S-100000`), whose made-up values changed a letter and kept a real
   run whole (`ZM1004715` beside a real `MR1004715`).

`ITEMS` names each item and layout K-HZ-22 measures at 20,000 rows (1,000
people of 20 rows, nothing declared or answered), and `measure` runs one
through the command a person types and counts what is real in what it
wrote: whole real values in the description, its summary, the questions
file, the screen and the twin's report and quality files, twin cells equal
to a real cell, and twin cells holding a COMPLETE real run of five figures
or more inside a wider cell -- each by a counter linear in the data (the
real values and runs in sets, each different twin cell and each text read
once). The unit-level draws (`label_spellings`, `joined_names`,
`not_joined_names`, `not_labels`) draw thousands of spellings from a seed.
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import pathlib
import random
import re
import time

SEED = 20261109
ROWS = 20_000
ROWS_A_PERSON = 20
NUMBER_FROM = 1_000_000

# -- the unit-level draws ------------------------------------------------------

SIGNS = ("", "#", "*", "!", "@", "~", "^", "&", "=", "\u2116")
# ...and (lane CZ-A2's repair 1) spaces on both sides of the mark, several
# alone, a tab, an equals sign or a comma.
JOINS = ("", "-", "_", "#", ".", ":", "/", " ", "- ", ": ", "# ", ". ", " # ", " - ", " : ", "  ", "=", ",", "\t",
         " = ")
ENCLOSING = (("(", ")"), ("[", "]"), ("{", "}"))


def _letters(draw: random.Random, count: int) -> str:
    return "".join(draw.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _place in range(count))


def label_spelling(draw: random.Random) -> "tuple[str, str]":
    """One record number beside its label, drawn: the cell, and the figures a reader must take whole."""
    figures = f"{draw.randint(1, 9)}" + "".join(f"{draw.randint(0, 9)}" for _place in range(draw.randint(4, 11)))
    if draw.random() < 0.15:
        figures = "0" + figures[1:]
    label = _letters(draw, draw.randint(1, 4))
    if draw.random() < 0.3:
        label = label.lower()
    sign = draw.choice(SIGNS)
    if sign and draw.random() < 0.3:
        sign = sign + " " * draw.randint(1, 2)
    join = draw.choice(JOINS)
    check = draw.choice(("", "", "", _letters(draw, 1), "-" + _letters(draw, 1)))
    if not sign and not join and draw.random() < 0.1:
        return f"{draw.choice(('#', '#', chr(0x2116)))}{figures}", figures
    cell = f"{sign}{label}{join}{figures}{check}"
    if draw.random() < 0.12:
        # ...one enclosing pair around all of it (lane CZ-A2's repair 1).
        opening, closing = draw.choice(ENCLOSING)
        cell = f"{opening}{cell}{closing}"
    return cell, figures


def label_spellings(count: int, seed: int = SEED) -> "list[tuple[str, str]]":
    """``count`` drawn spellings of a record number beside its label (`label_spelling`)."""
    draw = random.Random(seed)
    return [label_spelling(draw) for _place in range(count)]


# Cells no label reader may take as a record number: a unit or a currency
# beside figures, a percent, a decimal, figures alone.
NOT_LABELS = (
    "12345mg", "12345 mg", "$12345", "€12345", "12345%", "%12345", "1234.5", "123456", "12,345",
    "MR12345mg", "+1 555 0123", "12345kg",
)

GIVEN_FROM = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
NAME_JOINERS = (",", ";", "|", "\t", "^", "_")
SUFFIXES = ("Jr", "Jr.", "Sr", "II", "III", "IV")
PARTICLES = ("van der", "de la", "de", "von")


def _name_word(draw: random.Random) -> str:
    word = draw.choice(GIVEN_FROM) + "".join(draw.choice("abcdefghijklmnopqrstuvwxyz")
                                              for _place in range(draw.randint(2, 9)))
    roll = draw.random()
    if roll < 0.08:
        word = "O'" + word
    elif roll < 0.12:
        word = "O’" + word
    elif roll < 0.18:
        word = word + "-" + draw.choice(GIVEN_FROM) + "abc"[: draw.randint(1, 3)]
    elif roll < 0.22:
        word = word[:1] + "é" + word[2:]
    return word.upper() if draw.random() < 0.1 else word


def joined_name(draw: random.Random) -> str:
    """A family name, given names or initials and a record number, joined by one mark (`Cedar,Abc,1000013`)."""
    family = _name_word(draw)
    if draw.random() < 0.08:
        family = draw.choice(PARTICLES) + " " + family
    parts = [family, _name_word(draw)]
    roll = draw.random()
    if roll < 0.2:
        parts += [draw.choice(GIVEN_FROM) + draw.choice(("", "."))]
    elif roll < 0.3:
        parts += [draw.choice(SUFFIXES)]
    elif roll < 0.4:
        parts[1] = parts[1] + " " + draw.choice(GIVEN_FROM)
    number = f"{draw.randint(100000, 9999999999)}"
    number = draw.choice(("", "", "", "MR", "#", "REC ")) + number + draw.choice(("", "", "", "A"))
    if draw.random() < 0.1:
        # ...five figures alone beside the name (lane CZ-A2's repair 1).
        number = f"{draw.randint(10000, 99999)}"
    joiner = draw.choice(NAME_JOINERS)
    spaced = draw.choice(("", "", " "))
    if draw.random() < 0.2:
        parts = [number] + parts
    else:
        parts = parts + [number]
        if draw.random() < 0.1:
            # ...a flag of one or two letters after the number.
            parts += [draw.choice(("F", "M", "U", "NA"))]
    if draw.random() < 0.15:
        # ...an empty part anywhere among them (lane CZ-A2's repair 1:
        # `Tarn,Ul,,1000013`).
        parts.insert(draw.randint(1, len(parts) - 1), "")
    cell = (joiner + spaced).join(parts)
    roll = draw.random()
    if roll < 0.05:
        return cell + joiner
    if roll < 0.1:
        # ...or empty parts after the last (`1000013^TARN^UL^^^`).
        return cell + joiner * draw.randint(2, 4)
    return cell


def joined_names(count: int, seed: int = SEED) -> "list[str]":
    """``count`` drawn names joined to record numbers (`joined_name`)."""
    draw = random.Random(seed + 1)
    return [joined_name(draw) for _place in range(count)]


def not_joined_names(count: int, seed: int = SEED) -> "list[str]":
    """Cells no joined-name reader may take: a code of four figures, words with figures, one name, two numbers."""
    draw = random.Random(seed + 2)
    found: "list[str]" = []
    for _place in range(count):
        word = _name_word(draw).replace("’", "").replace("'", "")
        roll = draw.random()
        if roll < 0.25:
            found += [f"{word},{_name_word(draw)},{draw.randint(1000, 9999)}"]
        elif roll < 0.5:
            found += [f"{word},{draw.randint(100000, 9999999)}"]
        elif roll < 0.75:
            found += [f"{word}{draw.randint(1, 9)},{_name_word(draw)},{draw.randint(100000, 9999999)}"]
        else:
            found += [f"{word},{draw.randint(100000, 9999999)},{draw.randint(100000, 9999999)}"]
    return found


# A record number of five figures or more beside words no label reader names
# (lane CZ-A2's repair 1, its skeptic's items 1 and 2): the affixed split
# reads it whatever follows the number.
FIELD_MARKS = (",", ";", "|", "^", "_", "\t")
FLAGS = ("F", "M", "U", "X", "NA")
SPACED_JOINS = (" # ", " - ", " : ", "  ", " #", "- ", " / ", " = ", " -", ": ")


def beside_words_spelling(draw: random.Random) -> "tuple[str, str]":
    """One record number beside words, drawn: the cell, and the figures a reader must take whole.

    Three families: a name's parts and the number joined by a mark that
    parts fields, in small letters or not, the number last (a flag of one
    or two letters after it or none) or first, an empty part among them or
    after them (`Tarn,Ul,,1000013`, `Tarn,Ul,1000013,F`,
    `1000013^TARN^UL^^^`); a label, spaces and a mark before the number,
    or several spaces, in an enclosing pair or not (`MR #1000013`,
    `(MR - 1000013)`); a label before the number and a word after it
    (`MR 1000013 AB`).
    """
    figures = f"{draw.randint(1, 9)}" + "".join(f"{draw.randint(0, 9)}" for _place in range(draw.randint(4, 9)))
    roll = draw.random()
    if roll < 0.55:
        mark = draw.choice(FIELD_MARKS)
        spaced = "" if mark == "\t" else draw.choice(("", "", " "))
        names = [_name_word(draw) for _place in range(draw.randint(2, 4))]
        if draw.random() < 0.25:
            names = [name.lower() for name in names]
        first = draw.random() < 0.25
        parts = [figures] + names if first else names + [figures]
        if draw.random() < 0.3:
            parts.insert(draw.randint(1, len(parts) - 1), "")
        if not first and draw.random() < 0.3:
            parts += [draw.choice(FLAGS)]
        cell = (mark + spaced).join(parts)
        if draw.random() < 0.2:
            cell = cell + mark * draw.randint(1, 3)
        return cell, figures
    label = _letters(draw, draw.randint(1, 4))
    if draw.random() < 0.3:
        label = label.lower()
    if roll < 0.85:
        cell = f"{label}{draw.choice(SPACED_JOINS)}{figures}"
        if draw.random() < 0.4:
            opening, closing = draw.choice(ENCLOSING)
            cell = f"{opening}{cell}{closing}"
        return cell, figures
    return f"{label} {figures} {_letters(draw, draw.randint(1, 3))}", figures


def beside_words_spellings(count: int, seed: int = SEED) -> "list[tuple[str, str]]":
    """``count`` drawn record numbers beside words (`beside_words_spelling`)."""
    draw = random.Random(seed + 3)
    return [beside_words_spelling(draw) for _place in range(count)]


# Cells no reader of a record number beside words may take: a unit or a
# currency after the figures, a label before few figures, a decimal, a
# date, a telephone number, a code of letters and few figures, figures
# alone or in brackets, a record number and one word after it (a status in a list), a list of record numbers.
NOT_BESIDE_WORDS = (
    "12345mg", "12345 mg", "12345 EUR", "$12345", "12345%", "Age 45", "Stage 2", "Grade 3",
    "Weight 72.5 kg", "2024-01-05", "(319) 555-0000", "I59.2", "123456", "12,345", "(12345)",
    "-12345", "12345 kg/m2", "12345/min", "185380;pending", "1000013,closed", "R100000;R100001",
    "[R123456;R234567]",
)


# -- the items K-HZ-22 measures at 20,000 rows ----------------------------------


def given_of(person: int) -> str:
    """A made-up given name of three letters for person ``person`` (`Aaa`, `Aab`, ...)."""
    return chr(65 + person // 676) + chr(97 + (person // 26) % 26) + chr(97 + person % 26)


def _n(row: int) -> int:
    return NUMBER_FROM + row


# Twenty thousand different numbers of seven figures drawn from a seed over the whole room.
_SPREAD = random.Random(SEED + 9).sample(range(10_000_000), ROWS)


# Each item: (class, how its cell of row ``row`` and person ``person`` is written).
ITEMS: "dict[str, tuple[str, object]]" = {
    "sign_label": ("1", lambda row, person: f"#MR{_n(row)}"),
    "sign_space_label": ("1", lambda row, person: f"* MR{_n(row)}"),
    "sign_lower_label": ("1", lambda row, person: f"@mr{_n(row)}"),
    "label_point": ("1", lambda row, person: f"MR.{_n(row)}"),
    "label_space": ("1", lambda row, person: f"MR {_n(row)}"),
    "check_letter": ("1", lambda row, person: f"MR{_n(row)}{chr(65 + row % 26)}"),
    "number_sign_alone": ("1", lambda row, person: f"#{_n(row)}"),
    "sign_on_a_few": ("1", lambda row, person: f"#MR{_n(row)}" if row % 20 == 7 else f"MR{_n(row)}"),
    "sign_twelve_figures": ("1", lambda row, person: f"#MR{100000000000 + 7 * row}"),
    "joined_by_commas": ("2", lambda row, person: f"Cedar,{given_of(person)},{_n(row)}"),
    "joined_one_a_person": ("2", lambda row, person: f"Cedar,{given_of(person)},{_n(person)}"),
    "joined_spaced_one_a_person": ("2", lambda row, person: f"Cedar, {given_of(person)}, {_n(person)}"),
    "joined_by_semicolons": ("2", lambda row, person: f"Cedar;{given_of(person)};{_n(row)}"),
    "joined_number_first": ("2", lambda row, person: f"{_n(row)},Cedar,{given_of(person)}"),
    "joined_three_parts": ("2", lambda row, person: f"Cedar,{given_of(person)},Q,{_n(row)}"),
    "one_word_label": ("3", lambda row, person: f"MR{_n(row)}"),
    "one_word_label_dashed": ("3", lambda row, person: f"MR-{_n(row)}"),
    # ...AND THE ITEMS OF LANE CZ-A2'S REPAIR 1 (its skeptic's items 1 to 4):
    # labels after spaces and a mark, or in brackets, one a row and one a
    # person; the labels route two of the person rule reads one a person
    # (`#MR`, `MR.`, `MR/`, `MR#`, `#`); names joined to a record number
    # with an empty part, the number first with empty parts after the
    # names, an underscore, five figures, a flag after the number, small
    # letters; and a declared column of two layouts whose runs share a width.
    "label_spaced_mark": ("1", lambda row, person: f"MR #{_n(row)}"),
    "label_spaced_dash": ("1", lambda row, person: f"MR - {_n(row)}"),
    "label_in_brackets": ("1", lambda row, person: f"(MR{_n(row)})"),
    "sign_label_one_a_person": ("1", lambda row, person: f"#MR{_n(person)}"),
    "label_point_one_a_person": ("1", lambda row, person: f"MR.{_n(person)}"),
    "label_slash_one_a_person": ("1", lambda row, person: f"MR/{_n(person)}"),
    "label_hash_one_a_person": ("1", lambda row, person: f"MR#{_n(person)}"),
    "number_sign_one_a_person": ("1", lambda row, person: f"#{_n(person)}"),
    "label_spaced_mark_one_a_person": ("1", lambda row, person: f"MR #{_n(person)}"),
    "label_in_brackets_one_a_person": ("1", lambda row, person: f"(MR{_n(person)})"),
    "joined_empty_part": ("2", lambda row, person: f"Cedar,{given_of(person)},,{_n(row)}"),
    "joined_number_first_empty_after": (
        "2", lambda row, person: f"{_n(row)}^CEDAR^{given_of(person).upper()}^^^"),
    "joined_underscore": ("2", lambda row, person: f"Cedar_{given_of(person)}_{_n(row)}"),
    # ...five figures from 60,000, above every count the reports print at 20,000 rows, so the counter that reads
    # a real number in any figure run of a text never takes a printed count for a real value.
    "joined_five_figures": ("2", lambda row, person: f"Cedar,{given_of(person)},{60000 + row}"),
    "joined_flag_after": ("2", lambda row, person: f"Cedar,{given_of(person)},{_n(row)},F"),
    "joined_small_letters": ("2", lambda row, person: f"cedar,{given_of(person).lower()},{_n(row)}"),
    "joined_empty_part_one_a_person": ("2", lambda row, person: f"Cedar,{given_of(person)},,{_n(person)}"),
    "two_layouts_declared": (
        "3", lambda row, person: f"#{9000000 + row}" if row % 4 == 0 else f"#MR{_n(row)}"),
    # ...and a one-word record number whose seven figures are drawn at random over their whole room, so the
    # openings of four figures are held by a few real runs each: rule (3)'s search finds no opening it may write,
    # and the twin is written as the spill, wider than every real cell, until answered (P4-D469's limit (f)).
    "one_word_label_spread": ("3", lambda row, person: f"RC{_SPREAD[row % len(_SPREAD)]:07d}"),
    # ...AND THE ITEMS OF LANE CZ-A2'S REPAIR 2 (its verify's items 1 to 3
    # and Codex's items 1, 2 and 4): a minus sign (U+2212) before the number of
    # a label or of a joined name, a zero-width space or an en dash after a
    # number written first; one person's twenty cells a word or a placeholder
    # beside labelled record numbers or a name in small letters, one a person;
    # two, three and four identifier families in one column; a declared column
    # whose exclusion writes a figure inside the run (Codex's construction).
    "label_minus": ("1", lambda row, person: f"MR−{_n(row)}"),
    "label_minus_one_a_person": ("1", lambda row, person: f"MR−{_n(person)}"),
    "joined_minus": ("2", lambda row, person: f"Cedar,{given_of(person)},−{_n(row)}"),
    "joined_minus_one_a_person": ("2", lambda row, person: f"Cedar,{given_of(person)},−{_n(person)}"),
    "joined_number_first_zero_width": ("2", lambda row, person: f"{_n(row)}​,Cedar,{given_of(person)}"),
    "joined_number_first_zero_width_one_a_person": (
        "2", lambda row, person: f"{_n(person)}​,Cedar,{given_of(person)}"),
    "joined_number_first_en_dash_one_a_person": (
        "2", lambda row, person: f"{_n(person)}–,Cedar,{given_of(person)}"),
    # ...and the name beside a bracketed record number with a zero-width
    # space after its comma, or an en dash before its bracket (the repair's
    # wider generated set over every spelling of the class).
    "brackets_zero_width_after_the_comma": (
        "2", lambda row, person: f"Cedar,\u200b{given_of(person)} ({_n(row)})"),
    "brackets_zero_width_after_the_comma_one_a_person": (
        "2", lambda row, person: f"Cedar,\u200b{given_of(person)} ({_n(person)})"),
    "brackets_en_dash_before_the_pair_one_a_person": (
        "2", lambda row, person: f"Cedar, {given_of(person)}\u2013({_n(person)})"),
    # ...a dash after the comma of that form, a number sign and a dash before
    # the figures, and a space after a number sign's figures.
    "brackets_dash_after_the_comma_one_a_person": (
        "2", lambda row, person: f"Cedar,-{given_of(person)} ({_n(person)})"),
    "number_sign_dash": ("1", lambda row, person: f"#-{_n(row)}"),
    "number_sign_dash_one_a_person": ("1", lambda row, person: f"#-{_n(person)}"),
    "number_sign_space_after_one_a_person": ("1", lambda row, person: f"#{_n(person)} "),
    "sign_label_beside_a_word_one_a_person": (
        "1", lambda row, person: "UNKNOWN" if person == 5 else f"#MR{_n(person)}"),
    "label_spaced_mark_beside_a_word_one_a_person": (
        "1", lambda row, person: "UNKNOWN" if person == 5 else f"MR #{_n(person)}"),
    "label_in_brackets_beside_a_word_one_a_person": (
        "1", lambda row, person: "UNKNOWN" if person == 5 else f"(MR{_n(person)})"),
    "label_point_beside_a_word_one_a_person": (
        "1", lambda row, person: "UNKNOWN" if person == 5 else f"MR.{_n(person)}"),
    "joined_small_letters_beside_a_word_one_a_person": (
        "2", lambda row, person: "UNKNOWN" if person == 5 else f"cedar,{given_of(person).lower()},{_n(person)}"),
    "sign_label_beside_minus_one_one_a_person": (
        "1", lambda row, person: "-1" if person == 5 else f"#MR{_n(person)}"),
    "label_spaced_mark_beside_minus_one_one_a_person": (
        "1", lambda row, person: "-1" if person == 5 else f"MR #{_n(person)}"),
    "label_in_brackets_beside_minus_one_one_a_person": (
        "1", lambda row, person: "-1" if person == 5 else f"(MR{_n(person)})"),
    "label_point_beside_minus_one_one_a_person": (
        "1", lambda row, person: "-1" if person == 5 else f"MR.{_n(person)}"),
    "joined_small_letters_beside_minus_one_one_a_person": (
        "2", lambda row, person: "-1" if person == 5 else f"cedar,{given_of(person).lower()},{_n(person)}"),
    "two_families_one_a_person": (
        "1", lambda row, person: f"#MR{_n(person)}" if person < 500 else f"Q4012 24 {100000 + person} X"),
    "three_families_one_a_person": (
        "1", lambda row, person: (f"#MR{_n(person)}", f"Q4012 24 {100000 + person} X",
                                  f"S24-{person:06d}")[person % 3]),
    "four_families_one_a_person": (
        "1", lambda row, person: (f"MR #{_n(person)}", f"Q4012 24 {100000 + person} X", f"S24-{person:06d}",
                                  f"{100000000000000 + person}")[person % 4]),
    "interior_figure_declared": (
        "3", lambda row, person: f"#{1900000 + row}" if row % 4 == 0 else f"#MR{(1 + row % 9) * 1000000 + row // 9}"),
    # ...AND THE ITEMS OF LANE CZ-A2'S FOLLOW-UP (LANE CZ-A2 RULINGS 9 (2), its verify 2's C1): a soft hyphen inside
    # the figures of a labelled record number one a person (`MR100` + U+00AD + `0013`), held; and a no-break space
    # there one a row, read as free text (its two groups one number to the readers since lane CZ-A2's follow-up 4).
    "label_soft_hyphen_inside_one_a_person": (
        "1", lambda row, person: f"MR{str(_n(person))[:3]}­{str(_n(person))[3:]}"),
    "label_no_break_space_inside": ("1", lambda row, person: f"MR{str(_n(row))[:3]} {str(_n(row))[3:]}"),
    # ...and (LANE CZ-A2 RULINGS 9 (2), its verify 2's C4) a label in a script with no capital outside repair 2's
    # twelve ranges, two Ethiopic letters before seven figures, one a row and one a person.
    "ethiopic_label": ("1", lambda row, person: f"\u1200\u1208{_n(row)}"),
    "ethiopic_label_one_a_person": ("1", lambda row, person: f"\u1200\u1208{_n(person)}"),
    # ...AND THE ITEMS OF LANE CZ-A2'S FOLLOW-UP 4 (LANE CZ-A2 RULINGS 10 (2)): a record number written in two groups
    # of figures after its label, one a person, the groups parted by a plain space (`MR100 0013`), a no-break space
    # after the fourth figure (`MR1000 013`) or a tab; and six figures in groups of three one a row (`MR100 000`).
    "label_two_groups_one_a_person": ("1", lambda row, person: two_group_cell("MR", _n(person), 3, " ")),
    "label_two_groups_no_break_space_one_a_person": (
        "1", lambda row, person: two_group_cell("MR", _n(person), 4, "\u00a0")),
    "label_two_groups_tab_one_a_person": ("1", lambda row, person: two_group_cell("MR", _n(person), 3, "\t")),
    "label_two_groups_six_figures": ("1", lambda row, person: two_group_cell("MR", 100_000 + row, 3, " ")),
}
COLUMN = "record_label"
# The items profiled with the column declared an identifier (`--identifier`):
# its published prefix leaves the exclusion to write inside the run.
DECLARED = frozenset({"two_layouts_declared", "interior_figure_declared"})

# THE FALSE ALARMS THE PRICE NAMES (recorded, never failing; lane CZ-A2's
# repair 1, its skeptic's item 6): labelled codes, rooms, lots and charges,
# a measurement beside a label and a unit, a dose beside its unit, codes of
# letters and few figures, nine-figure codes many people share; each one
# column of 20,000 rows, 1,000 people of 20 rows, its role and the answers
# its question offers recorded.
FALSE_ALARMS: "dict[str, object]" = {
    "codes_labelled": lambda row, person: f"QD {40001 + person % 60}",
    "rooms_labelled": lambda row, person: f"Room {10001 + row % 400}",
    "lots_shared": lambda row, person: f"LOT{80001 + person % 200}",
    "charges_labelled": lambda row, person: f"USD {10000 + (row * 7919) % 89000}",
    "volume_labelled": lambda row, person: f"Volume: {10000 + row} mL",
    "dose_beside_unit": lambda row, person: f"{10000 + (row * 7) % 30000} mg",
    "codes_of_few_figures": lambda row, person: f"{chr(65 + person % 20)}{10 + person % 89}.{row % 10}",
    "nine_figure_codes_shared": lambda row, person: f"{527057489 + 1013 * (row % 90)}",
    # ...and (lane CZ-A2's repair 2, LANE CZ-A2 RULINGS 7 (6)) a labelled dose of three levels that repeat beside
    # its unit: route two's register reads it beside words since repair 1 and holds it until answered.
    "dose_three_levels": lambda row, person: f"Cholecalciferol {(10000, 25000, 50000)[row % 3]} IU",
    # ...and (lane CZ-A2's follow-up 4) two periods that repeat, no record number in two groups: fiscal quarters and
    # weeks of the year, each a group of figures beside a year.
    "fiscal_quarters": lambda row, person: f"Q{1 + row % 4} {2023 + row // 4 % 2}",
    "weeks_of_the_year": lambda row, person: f"W{1 + row % 52:02d} {2023 + row // 52 % 2}",
}


def cells_of(item: str, rows: int = ROWS) -> "list[str]":
    """An item's column: row ``r`` of person ``r // ROWS_A_PERSON`` (1,000 people of 20 rows at 20,000)."""
    make = ITEMS[item][1] if item in ITEMS else FALSE_ALARMS[item]
    return [make(row, row // ROWS_A_PERSON) for row in range(rows)]  # type: ignore[operator]


DIGIT_RUN = re.compile(r"[0-9]{5,}")


def complete_runs(real: "list[str]", twin: "list[str]") -> int:
    """Twin cells holding a COMPLETE real run of five figures or more inside a wider cell, not equal to a real cell.

    A maximal run of figures of the twin cell equal to a maximal run of a
    real cell, the twin cell more than that run. The real runs in a set,
    each different twin cell read once: linear in the data.
    """
    real_set = {cell for cell in real if cell.strip()}
    runs: "set[str]" = set()
    for cell in real_set:
        runs.update(DIGIT_RUN.findall(cell))
    seen: "dict[str, int]" = {}
    count = 0
    for cell in twin:
        if cell not in seen:
            body = cell.strip()
            seen[cell] = int(cell not in real_set and any(run in runs and run != body
                                                         for run in DIGIT_RUN.findall(cell)))
        count += seen[cell]
    return count


def pattern_of(cell: str) -> str:
    """A cell's pattern: a capital as `A`, a small letter as `a`, a figure as `9`, every other character kept."""
    return "".join("A" if "A" <= character <= "Z" else "a" if "a" <= character <= "z"
                   else "9" if "0" <= character <= "9" else character for character in cell)


ANSWER_ROUNDS_AT_MOST = 3


def _one_round(folder: pathlib.Path, source: pathlib.Path, rows: int, extra: "list[str]") -> "dict[str, object]":
    """Profile (nobody at the keyboard), generate at seed 0 and validate; the exits, the seconds and the screen."""
    import unanswered_identifier_shapes as shapes
    from synthtwin import cli

    refused = rows >= ROWS
    screen = io.StringIO()
    seconds: "dict[str, float]" = {}
    with shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        started = time.process_time()
        profiled = cli.main(["profile", f"{source}", "--out-dir", f"{folder}", "--replace"] + extra,
                            small_tables_refused=refused)
        seconds["profile"] = time.process_time() - started
        started = time.process_time()
        generated = cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{folder}", "--seed", "0",
                              "--replace"], small_tables_refused=refused) if profiled == 0 else -1
        seconds["generate"] = time.process_time() - started
        started = time.process_time()
        validated = cli.main(["validate", f"{folder / 't-profile.json'}", "--twin", f"{folder / 't-twin.csv'}",
                              "--out-dir", f"{folder}", "--replace"], small_tables_refused=refused) \
            if generated == 0 else -1
        seconds["validate"] = time.process_time() - started
    return {"exits": (profiled, generated, validated), "seconds": seconds, "screen": screen.getvalue()}


def _counted(folder: pathlib.Path, cells: "list[str]", done: "dict[str, object]") -> "dict[str, object]":
    """What one round wrote, counted by the linear counters: values shown, real cells, complete runs, patterns."""
    import health_zoo as zoo
    import unanswered_identifier_shapes as shapes

    exits = tuple(done["exits"])  # type: ignore[arg-type]
    texts = [f"{done['screen']}"]
    for name in ("t-profile.json", "t-profile.txt", "t-questions.json", "t-twin-report.txt", "t-twin-quality.txt"):
        if (folder / name).is_file():
            texts += [(folder / name).read_text(encoding="utf-8")]
    twin: "list[str]" = []
    if exits[1] == 0:
        with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
            twin = [row[0] if row else "" for row in list(csv.reader(handle))[1:]]
    real = sorted({cell for cell in cells if cell.strip()})
    counted = shapes.count_real(real, texts, twin, linear=True)
    asked: "list[list[str]]" = []
    if (folder / "t-questions.json").is_file():
        for entry in zoo._entries(json.loads((folder / "t-questions.json").read_text(encoding="utf-8"))):
            if f"{entry.get('column', '')}" == COLUMN and not f"{entry.get('your_answer') or ''}":
                asked += [sorted(zoo._offered(entry))]
    role = ""
    if exits[0] == 0:
        role = f"{json.loads((folder / 't-profile.json').read_text(encoding='utf-8'))['columns'][0]['role']}"
    known = set(real)
    patterns = {pattern_of(cell) for cell in real}
    present = [cell for cell in twin if cell.strip()]
    return {
        "exits": exits, "role": role, "asked": asked,
        "real_values_shown": int(counted["description_values"]),
        "real_twin_cells": sum(1 for cell in twin if cell in known),
        "complete_runs_in_wider_cells": complete_runs(real, twin),
        # ...and the share of twin cells written in a real cell's pattern
        # (the statistics check of lane CZ-A2: a held value no layout
        # describes is written as stand-ins), recorded, never failing.
        "twin_in_a_real_pattern": round(sum(1 for cell in present if pattern_of(cell) in patterns)
                                        / len(present), 3) if present else 0.0,
        "seconds": {key: round(float(value), 1) for key, value in done["seconds"].items()},  # type: ignore[attr-defined]
    }


def _answered_truthfully(folder: pathlib.Path) -> bool:
    """Answer the column's open questions as the column truly is: `identifier` where offered, else Safe Harbor `yes`.

    Written into the questions file the round wrote, as the zoo answers
    (`health_zoo.run_table`); False where no question took an answer.
    """
    path = folder / "t-questions.json"
    if not path.is_file():
        return False
    import health_zoo as zoo

    document = json.loads(path.read_text(encoding="utf-8"))
    given = False
    for entry in zoo._entries(document):
        if f"{entry.get('column', '')}" != COLUMN or f"{entry.get('your_answer') or ''}":
            continue
        offered = zoo._offered(entry)
        for answer in ("identifier", "yes"):
            if answer in offered:
                entry["your_answer"] = answer
                given = True
                break
    if given:
        path.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
    return given


def measure(folder: pathlib.Path, item: str, rows: int = ROWS, answered: bool = True) -> "dict[str, object]":
    """One item through profile (nobody at the keyboard), generate at seed 0 and validate; its counts and seconds.

    The table floor is on at 20,000 rows and more (the shipped default);
    a smaller table is a test size under it (the library's switch). An
    item of `DECLARED` is profiled with its column declared an identifier.
    Where ``answered``, its questions are then answered as the column truly
    is, round by round (at most `ANSWER_ROUNDS_AT_MOST`), and the last
    round's twin is counted again under ``answered``.
    """
    folder.mkdir(parents=True, exist_ok=True)
    cells = cells_of(item, rows)
    source = folder / "t.csv"
    with open(source, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow([COLUMN])
        writer.writerows([[cell] for cell in cells])
    extra = ["--identifier", COLUMN] if item in DECLARED else []
    first = _counted(folder, cells, _one_round(folder, source, rows, extra))
    seen: "dict[str, object]" = {"item": item, "class": ITEMS[item][0] if item in ITEMS else "F", "rows": rows}
    seen.update(first)
    # ...a question offering `identifier` or the Safe Harbor question was
    # put, or the column was read as free text, which publishes nothing and
    # writes no real value (`taxonomy.ROLES_PUBLISHING_NOTHING`; lane HX5's
    # rule reads the number roles alone) -- the two told apart (lane CZ-A2's
    # repair 1, its skeptic's item 6 (b)).
    asked = first["asked"]
    seen["question_put"] = any("identifier" in one or one == ["no", "yes"] for one in asked) or bool(extra)  # type: ignore[attr-defined]
    seen["read_as_free_text"] = first["role"] == "free_text"
    if answered:
        rounds = 0
        last = first
        while rounds < ANSWER_ROUNDS_AT_MOST and _answered_truthfully(folder):
            rounds += 1
            last = _counted(folder, cells, _one_round(folder, source, rows,
                                                     extra + ["--answers", f"{folder / 't-questions.json'}"]))
        seen["answered"] = dict(last, rounds=rounds)
    return seen


# -- lane CZ-A2's repair 2: the generated columns of its classes (unit level) --------------------------------------
#
# Each column is read by the product's readers alone, as the gate reads them:
# the forms' rule (`taxonomy.identifier_form_hold`), lane HX5's arm read as an
# affixed number one a row, and route two of the person rule (its ceiling read
# at the table floor's 20,000 rows). One a row: ``rows`` different numbers; one
# a person: ``rows // ROWS_A_PERSON`` people of `ROWS_A_PERSON` rows.

_FAMILY_HEADS = ("Bar", "Cor", "Dun", "Fel", "Gar", "Hal", "Kir", "Lom", "Mer", "Nor")
_FAMILY_MIDDLES = ("ben", "dal", "fen", "gil", "hol", "kin", "lan", "mor", "ner", "ton")
_FAMILY_ENDS = ("by", "den", "ford", "ham", "ley", "more", "ridge", "son", "ton", "wick")


def family_of(person: int) -> str:
    """A made-up family name for person ``person``, a thousand different ones."""
    return _FAMILY_HEADS[person // 100 % 10] + _FAMILY_MIDDLES[person // 10 % 10] + _FAMILY_ENDS[person % 10]


def held_by_a_reader(cells: "list[str]", one_a_person: bool) -> str:
    """Which reader holds or asks a column: `forms`, `arm` (one a row), `route two`, or none."""
    from synthtwin import asking, taxonomy

    if taxonomy.identifier_form_hold(COLUMN, cells, frozenset()):
        return "forms"
    if not one_a_person and asking._whole_numbers_each_on_one_row(cells, taxonomy.ROLE_AFFIXED):
        return "arm"
    if asking._names_people_past_route_four(cells, taxonomy.ROLE_CATEGORICAL, ROWS, taxonomy.Settings()):
        return "route two"
    return ""


def _column(make: object, rows: int, one_a_person: bool) -> "list[str]":
    """A column of ``rows`` cells made by ``make(number, person)``: one number a person, or one a row."""
    if one_a_person:
        return [make(NUMBER_FROM + row // ROWS_A_PERSON, row // ROWS_A_PERSON) for row in range(rows)]  # type: ignore[operator]
    return [make(NUMBER_FROM + row, row // ROWS_A_PERSON) for row in range(rows)]  # type: ignore[operator]


# (1) EVERY SPACE AND DASH BESIDE THE LANE'S SPELLINGS (its verify's finding
# 1, LANE CZ-A2 RULINGS 7 (2)): the whitespace and zero-width characters of
# LANE CODES-2 RULINGS 6 (1) and the dashes U+2010 to U+2015, U+2212, U+FE58,
# U+FE63, U+FF0D and U+00AD, written out here, in nine places of a label or a
# joined name, one a row and one a person: 756 columns.
SPACES_AND_DASHES = (
    "\t\n\r\x0b\x0c\x85             ​"
    "‌‍‎‏    ⁠　﻿"
    "‐‑‒–—―−﹘﹣－­"
)
SPACED_SHAPES: "dict[str, object]" = {
    "label": lambda mark, number, person: f"MR{mark}{number}",
    "sign_label": lambda mark, number, person: f"#MR{mark}{number}",
    "after_a_comma": lambda mark, number, person: f"{family_of(person)},{mark}{given_of(person)},{number}",
    "before_the_number": lambda mark, number, person: f"{family_of(person)},{given_of(person)},{mark}{number}",
    "as_the_joiner": lambda mark, number, person: f"{family_of(person)}{mark}{given_of(person)}{mark}{number}",
    "number_first_before_its_comma": lambda mark, number, person: f"{number}{mark},{family_of(person)},{given_of(person)}",
    "number_first_after_its_comma": lambda mark, number, person: f"{number},{mark}{family_of(person)},{given_of(person)}",
    "at_the_head": lambda mark, number, person: f"{mark}{family_of(person)},{given_of(person)},{number}",
    "at_the_end": lambda mark, number, person: f"{family_of(person)},{given_of(person)},{number}{mark}",
}


def spaced_columns(rows: int) -> "list[tuple[str, list[str], bool]]":
    """Every shape of `SPACED_SHAPES` with every mark of `SPACES_AND_DASHES`, one a row and one a person."""
    found: "list[tuple[str, list[str], bool]]" = []
    for shape, make in SPACED_SHAPES.items():
        for mark in SPACES_AND_DASHES:
            for one_a_person in (False, True):
                cells = _column(lambda number, person, make=make, mark=mark: make(mark, number, person),  # type: ignore[operator]
                                rows, one_a_person)
                found += [(f"{shape} U+{ord(mark):04X} {'one a person' if one_a_person else 'one a row'}", cells,
                           one_a_person)]
    return found


# (2) TWO IDENTIFIER FAMILIES IN ONE COLUMN (Codex's item 1, LANE CZ-A2
# RULINGS 6 (1)): the lane's labelled and joined families and every form of the
# forms' rule, each pair at shares of the column from 5 to 95 per cent.
def _blood_unit(unit: int) -> str:
    return f"Q4012 24 {100000 + unit} X"


FAMILIES: "dict[str, object]" = {
    "sign_label": lambda unit: f"#MR{NUMBER_FROM + unit}",
    "label_spaced_mark": lambda unit: f"MR #{NUMBER_FROM + unit}",
    "label_in_brackets": lambda unit: f"(MR{NUMBER_FROM + unit})",
    "joined": lambda unit: f"{family_of(unit % 1000)},{given_of(unit % 1000)},{NUMBER_FROM + unit}",
    "joined_small_letters": lambda unit: f"{family_of(unit % 1000).lower()},{given_of(unit % 1000).lower()},"
                                         f"{NUMBER_FROM + unit}",
    "social_security": lambda unit: f"{100 + unit % 600:03d}-{10 + unit % 89:02d}-{1000 + unit:04d}",
    "beneficiary": lambda unit: (f"{1 + unit % 9}{'ACDEFGHJK'[unit % 9]}{'ACDEFGHJK'[unit // 9 % 9]}{unit % 10}"
                                 f"{'ACDEF'[unit % 5]}{'GHJKM'[unit // 5 % 5]}{unit // 10 % 10}{'NPQRT'[unit % 5]}"
                                 f"{'UVWXY'[unit // 3 % 5]}{unit // 100 % 10}{unit % 7}"),
    "token": lambda unit: f"{(unit * 2654435761) % (16 ** 32):032x}",
    "accession": lambda unit: f"S24-{unit:06d}",
    "blood_unit": _blood_unit,
    "fifteen_figures": lambda unit: f"{100000000000000 + unit}",
    "sixteen_figures": lambda unit: f"{1000000000000000 + unit}",
}
FAMILY_SHARES = (5, 20, 35, 50, 65, 80, 95)


def mixed_columns(rows: int) -> "list[tuple[str, list[str], bool]]":
    """Every pair of `FAMILIES` at every share of `FAMILY_SHARES` (the first family's), one a row and one a person."""
    names = list(FAMILIES)
    found: "list[tuple[str, list[str], bool]]" = []
    for first in range(len(names)):
        for second in names[first + 1:]:
            for share in FAMILY_SHARES:
                for one_a_person in (False, True):
                    def make(number: int, person: int, one: object = FAMILIES[names[first]],
                             other: object = FAMILIES[second], share: int = share,
                             one_a_person: bool = one_a_person) -> str:
                        unit = person if one_a_person else number - NUMBER_FROM
                        return (one if (unit * 37) % 100 < share else other)(unit)  # type: ignore[operator]
                    found += [(f"{names[first]} {share}% beside {second} "
                               f"{'one a person' if one_a_person else 'one a row'}",
                               _column(make, rows, one_a_person), one_a_person)]
    return found


# (3) A WORD OR A PLACEHOLDER BESIDE THE LANE'S HOLDS (its verify's finding 2,
# LANE CZ-A2 RULINGS 7 (3); the standing rule that sparse tokens never defeat
# a key hold): every form of the lane's holds beside every spelling of the
# product's own set-aside cells (`asking._set_aside_beside_keys`: a cell
# holding no figure; a minus sign and one to three figures; a lone `0`;
# nines alone), on one person's rows or on one person in twenty.
HOLD_FORMS: "dict[str, object]" = {
    "sign_label": lambda number, person: f"#MR{number}",
    "label_spaced_mark": lambda number, person: f"MR #{number}",
    "label_in_brackets": lambda number, person: f"(MR{number})",
    "label_point": lambda number, person: f"MR.{number}",
    "label_slash": lambda number, person: f"MR/{number}",
    "label_colon": lambda number, person: f"MR: {number}",
    "label_spaced_dash": lambda number, person: f"MR - {number}",
    "number_sign_alone": lambda number, person: f"#{number}",
    "joined": lambda number, person: f"{family_of(person)},{given_of(person)},{number}",
    "joined_number_first": lambda number, person: f"{number},{family_of(person)},{given_of(person)}",
    "joined_by_semicolons": lambda number, person: f"{family_of(person)};{given_of(person)};{number}",
    "joined_underscore": lambda number, person: f"{family_of(person)}_{given_of(person)}_{number}",
    "joined_flag_after": lambda number, person: f"{family_of(person)},{given_of(person)},{number},{'FM'[person % 2]}",
    "joined_empty_part": lambda number, person: f"{family_of(person)},{given_of(person)},,{number}",
    "joined_caret": lambda number, person: f"{number}^{family_of(person).upper()}^{given_of(person).upper()}^^^",
    "joined_small_letters": lambda number, person: f"{family_of(person).lower()},{given_of(person).lower()},{number}",
    "joined_small_letters_number_first": (
        lambda number, person: f"{number},{family_of(person).lower()},{given_of(person).lower()}"),
}
SET_ASIDE_SPELLINGS = (
    "UNKNOWN", "Unknown", "unknown", "N/A", "NA", "?", "-", "*", "Other (specify)", "Not known.", "NULL", "none",
    "PENDING", "n.k.", "-1", "-5", "-9", "-42", "-99", "-999", "0", "99", "999", "9999", "99999", "999999", "9999999",
)


def set_aside_columns(rows: int) -> "list[tuple[str, list[str], bool]]":
    """Every form of `HOLD_FORMS` beside every spelling of `SET_ASIDE_SPELLINGS`, on one person or one in twenty."""
    found: "list[tuple[str, list[str], bool]]" = []
    for form, make in HOLD_FORMS.items():
        for word in SET_ASIDE_SPELLINGS:
            for few in (False, True):
                for one_a_person in (False, True):
                    def cell(number: int, person: int, make: object = make, word: str = word, few: bool = few) -> str:
                        if (not few and person == 5) or (few and person % 20 == 3):
                            return word
                        return make(number, person)  # type: ignore[operator]
                    found += [(f"{form} beside {word!r} {'one in twenty' if few else 'one person'} "
                               f"{'one a person' if one_a_person else 'one a row'}",
                               _column(cell, rows, one_a_person), one_a_person)]
    return found


# (4) EVERY SPELLING THE LANE HOLDS, A SPACE OR A DASH IN EACH PLACE (lane
# CZ-A2's repair 2, LANE CZ-A2 RULINGS 7 (2): the three named readers and
# every other reader of the class read for the same gap): 25 spellings of
# labels, joined names and names beside a bracketed record number, each
# space, dash or joint of them written with each of `SPACES_AND_DASHES`, one
# a row and one a person: 2,100 columns, each beside its plain spelling --
# each dash written `-`, each mark of no width set aside, each other space
# written ` `, the tab kept -- written out here, not read from the product.
_NO_WIDTH = "\u200b\u200c\u200d\u200e\u200f\u2060\ufeff"
_DASHES = "\u2010\u2011\u2012\u2013\u2014\u2015\u2212\ufe58\ufe63\uff0d\u00ad"


def plain_mark(mark: str) -> str:
    """The plain spelling of one character of `SPACES_AND_DASHES`: `-` for a dash, nothing for a mark of no width, the tab kept, ` ` for any other space."""
    if mark in _DASHES:
        return "-"
    if mark in _NO_WIDTH:
        return ""
    return mark if mark == "\t" else " "


PLAIN_MARK_FORMS: "dict[str, object]" = {
    "label_spaced_mark_space": lambda mark, number, person: f"MR{mark}#{number}",
    "label_spaced_mark_joint": lambda mark, number, person: f"MR #{mark}{number}",
    "label_colon_space": lambda mark, number, person: f"MR:{mark}{number}",
    "label_spaced_dash_spaces": lambda mark, number, person: f"MR{mark}-{mark}{number}",
    "label_spaced_dash_dash": lambda mark, number, person: f"MR {mark} {number}",
    "label_dash": lambda mark, number, person: f"MR{mark}{number}",
    "label_point_joint": lambda mark, number, person: f"MR.{mark}{number}",
    "label_slash_joint": lambda mark, number, person: f"MR/{mark}{number}",
    "label_in_brackets_inside": lambda mark, number, person: f"({mark}MR{number}{mark})",
    "number_sign_joint": lambda mark, number, person: f"#{mark}{number}",
    "sign_label_head": lambda mark, number, person: f"{mark}#MR{number}",
    "sign_label_end": lambda mark, number, person: f"#MR{number}{mark}",
    "semicolons_joint": lambda mark, number, person: f"{family_of(person)};{mark}{given_of(person)};{number}",
    "underscore_joint": lambda mark, number, person: f"{family_of(person)}_{given_of(person)}_{mark}{number}",
    "flag_after_joint": lambda mark, number, person: (
        f"{family_of(person)},{given_of(person)},{number},{mark}{'FM'[person % 2]}"),
    "caret_joint": lambda mark, number, person: (
        f"{number}^{mark}{family_of(person).upper()}^{given_of(person).upper()}^^^"),
    "empty_part_joint": lambda mark, number, person: f"{family_of(person)},{given_of(person)},,{mark}{number}",
    "small_first_joint": lambda mark, number, person: (
        f"{number}{mark},{family_of(person).lower()},{given_of(person).lower()}"),
    "small_before_the_number": lambda mark, number, person: (
        f"{family_of(person).lower()},{given_of(person).lower()},{mark}{number}"),
    "small_as_the_joiner": lambda mark, number, person: (
        f"{family_of(person).lower()}{mark}{given_of(person).lower()}{mark}{number}"),
    "brackets_after_the_comma": lambda mark, number, person: f"{family_of(person)},{mark}{given_of(person)} ({number})",
    "brackets_before_the_pair": lambda mark, number, person: f"{family_of(person)}, {given_of(person)}{mark}({number})",
    "brackets_after_the_pair": lambda mark, number, person: f"{family_of(person)}, {given_of(person)} ({number}){mark}",
    "number_sign_after_the_comma": lambda mark, number, person: f"{family_of(person)},{mark}{given_of(person)} #{number}",
    "number_sign_before_the_sign": lambda mark, number, person: f"{family_of(person)}, {given_of(person)}{mark}#{number}",
}


def plain_mark_columns(rows: int) -> "list[tuple[str, list[str], list[str], bool]]":
    """Each form of `PLAIN_MARK_FORMS` with each mark of `SPACES_AND_DASHES`, both layouts, beside its plain spelling's column.

    The plain columns repeat (one a mark's plain spelling), so each is made
    once and shared.
    """
    found: "list[tuple[str, list[str], list[str], bool]]" = []
    plain_made: "dict[tuple[str, str, bool], list[str]]" = {}
    for form, make in PLAIN_MARK_FORMS.items():
        for one_a_person in (False, True):
            for mark in SPACES_AND_DASHES:
                plain = plain_mark(mark)
                key = (form, plain, one_a_person)
                if key not in plain_made:
                    plain_made[key] = _column(
                        lambda number, person, make=make, plain=plain: make(plain, number, person),  # type: ignore[operator]
                        rows, one_a_person)
                cells = _column(
                    lambda number, person, make=make, mark=mark: make(mark, number, person),  # type: ignore[operator]
                    rows, one_a_person)
                found += [(f"{form} U+{ord(mark):04X} {'one a person' if one_a_person else 'one a row'}", cells,
                           plain_made[key], one_a_person)]
    return found


# (4b) A MARK INSIDE A LABELLED RECORD NUMBER'S FIGURES (lane CZ-A2's
# follow-up, LANE CZ-A2 RULINGS 9 (2), its verify 2's C1): each of
# `SPACES_AND_DASHES` after each of the first six figures of `MR` and seven
# figures (`MR100` + a soft hyphen + `0013`), one a row and one a person,
# each beside its plain spelling (`plain_mark`): 504 columns, each held
# wherever its plain spelling is.
INSIDE_THE_FIGURES = (1, 2, 3, 4, 5, 6)


def inside_the_figures_columns(rows: int) -> "list[tuple[str, list[str], list[str], bool]]":
    """Each mark of `SPACES_AND_DASHES` after each place of `INSIDE_THE_FIGURES`, both layouts, beside its plain spelling's column."""
    found: "list[tuple[str, list[str], list[str], bool]]" = []
    plain_made: "dict[tuple[int, str, bool], list[str]]" = {}
    for place in INSIDE_THE_FIGURES:
        for one_a_person in (False, True):
            for mark in SPACES_AND_DASHES:
                plain = plain_mark(mark)
                key = (place, plain, one_a_person)
                if key not in plain_made:
                    plain_made[key] = _column(
                        lambda number, person, place=place, plain=plain: f"MR{str(number)[:place]}{plain}"
                                                                         f"{str(number)[place:]}",
                        rows, one_a_person)
                cells = _column(
                    lambda number, person, place=place, mark=mark: f"MR{str(number)[:place]}{mark}{str(number)[place:]}",
                    rows, one_a_person)
                found += [(f"inside the figures after {place} U+{ord(mark):04X} "
                           f"{'one a person' if one_a_person else 'one a row'}", cells, plain_made[key], one_a_person)]
    return found


# (5) A NAME BESIDE A BRACKETED RECORD NUMBER, AND A NUMBER SIGN ALONE, WITH
# EACH MARK IN EACH PLACE (lane CZ-A2's repair 2, LANE CZ-A2 RULINGS 5 (3)
# and 7 (2): any of the 42 marks in any position, each held, as the verify's
# set holds the joined names): at the head and the end, around the comma,
# before, inside and after the brackets, around the number sign, after a
# label's figures; one a row and one a person: 1,344 columns. And (lane
# CZ-A2's follow-up, LANE CZ-A2 RULINGS 9 (2)) the places of a labelled
# record number it lacked, between the label and the figures and at the
# head and both ends: nineteen places, 1,596 columns.
EVERY_MARK_FORMS: "dict[str, object]" = {
    "number_sign_joint": lambda mark, number, person: f"#{mark}{number}",
    "number_sign_end": lambda mark, number, person: f"#{number}{mark}",
    "label_end": lambda mark, number, person: f"MR{number}{mark}",
    "label_spaced_mark_end": lambda mark, number, person: f"MR #{number}{mark}",
    "label_point_end": lambda mark, number, person: f"MR.{number}{mark}",
    "label_in_brackets_end": lambda mark, number, person: f"(MR{number}){mark}",
    "brackets_at_the_head": lambda mark, number, person: f"{mark}{family_of(person)}, {given_of(person)} ({number})",
    "brackets_before_the_comma": lambda mark, number, person: f"{family_of(person)}{mark}, {given_of(person)} ({number})",
    "brackets_after_the_comma": lambda mark, number, person: f"{family_of(person)},{mark}{given_of(person)} ({number})",
    "brackets_before_the_pair": lambda mark, number, person: f"{family_of(person)}, {given_of(person)}{mark}({number})",
    "brackets_inside_the_pair": lambda mark, number, person: (
        f"{family_of(person)}, {given_of(person)} ({mark}{number}{mark})"),
    "brackets_after_the_pair": lambda mark, number, person: f"{family_of(person)}, {given_of(person)} ({number}){mark}",
    "number_sign_after_the_comma": lambda mark, number, person: f"{family_of(person)},{mark}{given_of(person)} #{number}",
    "number_sign_before_the_sign": lambda mark, number, person: f"{family_of(person)}, {given_of(person)}{mark}#{number}",
    "number_sign_after_the_sign": lambda mark, number, person: f"{family_of(person)}, {given_of(person)} #{mark}{number}",
    "number_sign_at_the_end": lambda mark, number, person: f"{family_of(person)}, {given_of(person)} #{number}{mark}",
    "label_joint": lambda mark, number, person: f"MR{mark}{number}",
    "label_at_the_head": lambda mark, number, person: f"{mark}MR{number}",
    "label_at_both_ends": lambda mark, number, person: f"{mark}MR{number}{mark}",
}


def every_mark_columns(rows: int) -> "list[tuple[str, list[str], bool]]":
    """Each form of `EVERY_MARK_FORMS` with each mark of `SPACES_AND_DASHES`, one a row and one a person."""
    found: "list[tuple[str, list[str], bool]]" = []
    for form, make in EVERY_MARK_FORMS.items():
        for one_a_person in (False, True):
            for mark in SPACES_AND_DASHES:
                found += [(f"{form} U+{ord(mark):04X} {'one a person' if one_a_person else 'one a row'}",
                           _column(lambda number, person, make=make, mark=mark: make(mark, number, person),  # type: ignore[operator]
                                   rows, one_a_person), one_a_person)]
    return found


# (6) A LABELLED RECORD NUMBER WRITTEN IN TWO GROUPS OF FIGURES (lane CZ-A2's
# follow-up 4, LANE CZ-A2 RULINGS 10 (2)): a label of one letter and of two
# letters, six figures (from 100,000) and seven (from 1,000,000), every split
# that leaves both groups two figures or more, the plain space and each space
# of `SPACES_AND_DASHES` (the lane's list before batch 4s's merge, written out
# here; the product's one definition is wider, `taxonomy._SCREEN_SPACE_RANGES`,
# and the gate file's agreement case reads every space of it) between the
# groups, one a row and one a person: 896 columns. And the near-miss controls
# no reading of a record number may take: fiscal quarters, fiscal years,
# versions, weeks and months, each a few values that repeat, and a group of
# one figure.
TWO_GROUP_LABELS = ("M", "MR")
TWO_GROUP_FIRST = {6: 100_000, 7: 1_000_000}
TWO_GROUP_SPACES = " " + "".join(mark for mark in SPACES_AND_DASHES if mark not in _DASHES)


def two_group_cell(label: str, number: int, opening: int, mark: str) -> str:
    """A record number of ``number``'s figures after ``label``, its first ``opening`` figures a group, then ``mark``."""
    figures = f"{number}"
    return f"{label}{figures[:opening]}{mark}{figures[opening:]}"


def two_group_columns(rows: int) -> "list[tuple[str, list[str], bool]]":
    """Every label, width, split and space of the set above, one a row and one a person (896 columns)."""
    found: "list[tuple[str, list[str], bool]]" = []
    for label in TWO_GROUP_LABELS:
        for width, first in TWO_GROUP_FIRST.items():
            for opening in range(2, width - 1):
                for mark in TWO_GROUP_SPACES:
                    for one_a_person in (False, True):
                        units = [row // ROWS_A_PERSON if one_a_person else row for row in range(rows)]
                        found += [(f"{label} {opening}+{width - opening} U+{ord(mark):04X} "
                                   f"{'one a person' if one_a_person else 'one a row'}",
                                   [two_group_cell(label, first + unit, opening, mark) for unit in units],
                                   one_a_person)]
    return found


_YEARS = (2023, 2024)
NEAR_MISS_CONTROLS: "dict[str, list[str]]" = {
    "fiscal quarters": [f"Q{quarter} {year}" for year in _YEARS for quarter in (1, 2, 3, 4)],
    "fiscal quarters of two letters": [f"FQ{quarter} {year}" for year in _YEARS for quarter in (1, 2, 3, 4)],
    "fiscal years": [f"FY {year}" for year in range(2015, 2025)],
    "fiscal years over two, the second short": [f"FY{year} {(year + 1) % 100:02d}" for year in range(2015, 2025)],
    "fiscal years over two, both whole": [f"FY{year} {year + 1}" for year in range(2015, 2025)],
    "fiscal years over two, both short": [f"FY{year % 100:02d} {(year + 1) % 100:02d}" for year in range(2015, 2025)],
    "versions": [f"v{major} {minor}" for major in range(1, 4) for minor in range(10)],
    "versions of two figures each": [f"v{major} {minor}" for major in range(10, 13) for minor in range(10, 20)],
    "versions by the year and month": [f"v{year} {month:02d}" for year in _YEARS for month in range(1, 13)],
    "weeks": [f"W{week:02d} {year}" for year in _YEARS for week in range(1, 53)],
    "weeks of two letters": [f"Wk{week:02d} {year}" for year in _YEARS for week in range(1, 53)],
    "weeks unpadded": [f"W{week} {year}" for year in _YEARS for week in range(1, 53)],
    "months": [f"M{month:02d} {year}" for year in _YEARS for month in range(1, 13)],
    "thousands parted by a space": [f"{number // 1000} {number % 1000:03d}" for number in range(100_000, 100_030)],
}
# ...and a group of one figure, first or last, one a person.
ONE_FIGURE_GROUPS = {
    "first": [two_group_cell("MR", NUMBER_FROM + person, 1, " ") for person in range(1_000)],
    "last": [two_group_cell("MR", NUMBER_FROM + person, 6, " ") for person in range(1_000)],
}
