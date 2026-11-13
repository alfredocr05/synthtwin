"""Columns of persons' names (plan P4-D478, lane CZ-F): invented look-alikes, the commands that read them, and the generated spellings of names.

Every value here is made up from this module's own syllables and seed
(`made_up_word`, `SEED`): no list of names, nothing copied from anywhere,
and the column names are generic. A TABLE is one names column in one
LAYOUT (`LAYOUTS`), its names in one SHAPE (`SHAPES`), one name a person,
1,000 people on 20 rows each at the KPI size (20,000 rows):

- `alone`: the column alone under a neutral name (`patient_label`): no
  record number in its cells and no person column beside it, so the
  command counts rows -- the shape the public head published whole;
- `beside`: the same column beside a person column (`patient_ref`): it is
  held in people, its bytes kept;
- `heading`: the column under a name that says a person's name
  (`patient_full_name`); `surname`: family names alone under `patient_surname`;
- `clinician`: 60 clinicians' names under a clinician's role (`surgeon`),
  one row a case beside its case number and a room (counted in rows); and
  `staff`, the same under a neutral name (`staff_label`): fewer names than
  the reader's count, a stated limit;
- `one_a_row`: one name a row, 20,000 people;
- `uneven`: about 5,000 people, 300 of them on 11 to 30 rows, the rest on
  one to five: only the few hundred names held by eleven rows or more
  would be published levels;
- `person_name`: the column alone under `person_name`;
- `era`: 116,400 rows in date order, an early era of 4,200 people written
  in small letters on 2 rows each, then 9,000 people written `Family,
  Given` on 12 rows each (the bound of different values the reader reads
  is drawn from cells spread over the whole column);
- `share_edge`: 1,000 people on 20 rows, 520 of them written once in
  small letters (65.8 per cent of the different values names: under the
  two in three, a stated limit);
- `unlisted_role`: 60 clinicians under `social_worker`, a staff heading
  outside the reader's closed list (a stated limit);
- `run_together`: family names alone under `PERSONLASTNAME`, a name for a
  family name in capitals with no mark between its words;
- and from lane CZ-F's repair 2: `few_surname`, `few_clinician` and
  `few_run_together`, one, two, three or sixty family names (`FEW`) under
  `patient_surname`, `surgeon` and `PERSONLASTNAME` beside a case number
  (Codex's item 1); `suffix_surname`, 60 family names each with a suffix
  under `patient_surname` beside a case number (Codex's item 2:
  `suffix_jr`, ` Jr.` after each, or `suffixes`, each written one of the
  ways of `suffix_forms`); and `blocks`, 49,152 rows in blocks of 12, a
  name in small letters first in each block and 11 of 4,096 names on 11
  rows each after it (the combined verify's item 1).

THE SHAPES: `comma` (`Family, Given`), `apostrophe` (`O'Family, Given`),
`given_first` (`Given Family`), `capitals` (`FAMILY, GIVEN`), `mixed`
(every family of spellings of `spellings`, drawn per person), `family`
(the family name alone), `caret` (a health message's name field,
`FAMILY^GIVEN^M`, one in three `Family^Given^^^`), `zero_width`
(`Family,` U+200B `Given`), `format_trailing` (`Family, Given` U+200E) and
`initials` (`Family J.`, read under a clinician's heading alone); and two
the reader does not read, its stated limits: `small_letters` (`family,
given`) and `no_capitals` (made-up names in scripts with no capitals).

`measure` runs a table through the commands a person types -- profile,
its rounds of answers by MODE (`MODES`), generate at seed 0 and validate,
nobody at the keyboard, the table floor on at 20,000 rows -- and counts,
by a counter linear in the data, the real names written whole in every
file the commands write and on the screen (exact, and folded: case and
spaces aside; each JSON file's strings read DECODED and each text for
the eye read again with its escapes decoded, `published_texts`), the
twin cells equal to a real name (exact and folded), the twin cells
holding a complete real name inside a wider value, and the questions put
to the column.

`spellings` writes the GENERATED names of each family, in thousands, for
the reader's unit-level check: those it must read (`FAMILIES_READ`) and
those it must not (`FAMILIES_NOT_READ`, each a stated limit or no name).
`CARET_PATTERNS` are the filled and empty parts 3 to 7 of the name field.
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
import unicodedata

import health_zoo as zoo
import safe_harbor_forms as forms

SEED = 20261110
ROWS_A_PERSON = 20
# The people of a table at the KPI size, and the clinicians of the
# clinician layout (fewer than `taxonomy.NAMES_AT_LEAST`).
PEOPLE = 1000
CLINICIANS = 60
_HEADS = "bdfgklmnprstvz"
_VOWELS = "aeiou"
_TAILS = ("", "", "l", "n", "r", "s", "t")
INITIALS = "ABCDEFGHJKLMNPRSTVW"
# Small letters past ASCII a made-up name may hold: accents and a stroke.
_PAST_ASCII = "éöáñüłçíøå"
# Greek and Cyrillic letters, capitals and small, for names in those scripts.
_GREEK = ("ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡ"
          "ΣΤΥΦΧΨΩ")
_CYRILLIC = ("АБВГДЕЖЗИКЛМНОПР"
             "СТУФХЦЧШЭЮЯ")
# Scripts with no capitals: CJK ideographs, Arabic, Hebrew and Devanagari
# letters, each a range of code points.
_NO_CAPITALS = ((0x4E00, 0x4FFF), (0x0627, 0x064A), (0x05D0, 0x05EA), (0x0915, 0x0939))
PARTICLES = ("van der", "de la", "van", "von", "de", "da", "di", "du", "del", "della", "der", "den", "la", "le",
             "bin", "ibn", "al", "el", "dos", "das", "ter", "ten")
JOINED = ("al-", "el-", "d'", "d’")
SUFFIXES = ("Jr.", "Jr", "Sr.", "II", "III", "IV")
INNER = ("Mc", "Mac", "De", "Le", "Di", "La")
TITLES = ("Dr.", "Dr", "Mr.", "Mrs.", "Ms", "Prof.")
DEGREES = ("MD", "M.D.", "DO", "RN", "NP", "PhD", "CRNA")


def made_up_word(draw: random.Random, syllables: int) -> str:
    """A made-up name of ``syllables`` syllables, capitalised: `Bolumet`."""
    written = ""
    for _place in range(syllables):
        written += draw.choice(_HEADS) + draw.choice(_VOWELS) + draw.choice(_TAILS)
    return written[:1].upper() + written[1:]


def _script_word(draw: random.Random, letters: str) -> str:
    """A made-up word in a script with capitals: a capital, then three to six small letters."""
    small = letters.lower()
    return draw.choice(letters) + "".join(draw.choice(small) for _place in range(draw.randint(3, 6)))


def _no_capitals_word(draw: random.Random) -> str:
    """A made-up word of two to five letters of a script without capitals."""
    low, high = draw.choice(_NO_CAPITALS)
    return "".join(chr(draw.randint(low, high)) for _place in range(draw.randint(2, 5)))


def _with_past_ascii(draw: random.Random, word: str) -> str:
    """A made-up word with one small letter past ASCII in place of one of its letters after the first."""
    place = draw.randrange(1, len(word))
    return word[:place] + draw.choice(_PAST_ASCII) + word[place + 1:]


# -- the generated spellings, family by family --------------------------------

FAMILIES_READ = (
    "family_comma_given", "given_family", "given_initial_family", "family_comma_given_initial", "capitals",
    "apostrophes", "hyphens", "particles", "joined_particles", "suffixes", "inner_capitals", "initials",
    "past_ascii", "greek_and_cyrillic", "spaces", "titles_and_degrees", "no_space_after_the_comma", "nicknames",
    # ...and those of lane CZ-F's repair (skeptic 1 items 1, 2 and 5 (d)).
    "caret", "odd_spaces", "odd_dashes", "apostrophe_variants", "decomposed_accents", "spaced_hyphens",
    "more_particles", "two_letter_family_given_first", "title_after_the_comma",
)
# The spaces and dashes a name may be written with past ASCII (the zero-width
# and format characters among them), each read as a space or a dash.
ODD_SPACES = (
    "\t", "\x0b", "\x0c", "\x85", "\xa0", "\u1680", "\u2000", "\u2001", "\u2002", "\u2003", "\u2004",
    "\u2005", "\u2006", "\u2007", "\u2008", "\u2009", "\u200a", "\u2028", "\u2029", "\u202f", "\u205f",
    "\u3000", "\u200b", "\u200c", "\u200d", "\u200e", "\u200f", "\u2060", "\ufeff",
)
ODD_DASHES = ("\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u2212", "\ufe58", "\ufe63", "\uff0d", "\u00ad")
APOSTROPHES = ("'", "\u2019", "\u02bc", "\u2018", "\u00b4", "`")
MORE_PARTICLES = ("de las", "y", "do", "e", "des", "von und zu", "af")
# The parts 3 to 7 of a health message's name field, each filled or empty:
# middle name or initial, suffix, title, degree, the name's type.
CARET_PATTERNS = tuple(tuple(bool(pattern >> place & 1) for place in range(5)) for pattern in range(32))
FAMILIES_NOT_READ = (
    "small_letters", "figures", "five_name_words", "joined_by_a_semicolon", "no_capitals", "one_word",
    "a_short_word_inside", "too_long",
)


def caret_spelling(draw: random.Random, pattern: "tuple[bool, ...]", capitals: bool) -> str:
    """A name written as a health message's name field: family name, given name, then parts 3 to 7 filled or empty by ``pattern``, and up to three empty parts after them."""
    last = made_up_word(draw, draw.choice((2, 2, 3)))
    if draw.random() < 0.2:
        last = f"{last} {made_up_word(draw, 2)}"
    given = draw.choice((made_up_word(draw, draw.choice((1, 2))), draw.choice(INITIALS)))
    filled = (
        draw.choice((draw.choice(INITIALS), made_up_word(draw, 2))),
        draw.choice(("Jr", "III", "Sr")),
        draw.choice(("Dr", "Mr", "Ms")),
        draw.choice(("MD", "PhD", "RN")),
        draw.choice(("L", "A", "M")),
    )
    parts = [last, given] + [filled[place] if pattern[place] else "" for place in range(5)]
    while parts and not parts[-1]:
        parts = parts[:-1]
    text = "^".join(parts) + "^" * draw.randint(0, 3)
    return text.upper() if capitals else text


def _spelling(family: str, draw: random.Random) -> str:
    """One generated spelling of a family of names (`FAMILIES_READ`, `FAMILIES_NOT_READ`)."""
    last = made_up_word(draw, draw.choice((2, 2, 3)))
    given = made_up_word(draw, draw.choice((1, 2, 2)))
    other = made_up_word(draw, 2)
    initial = draw.choice(INITIALS)
    if family == "caret":
        return caret_spelling(draw, draw.choice(CARET_PATTERNS), draw.random() < 0.5)
    if family == "odd_spaces":
        mark = draw.choice(ODD_SPACES)
        return draw.choice((f"{last},{mark}{given}", f"{given}{mark}{last}", f"{mark}{last}, {given}",
                            f"{last}, {given}{mark}", f"{last}, {mark} {given}"))
    if family == "odd_dashes":
        mark = draw.choice(ODD_DASHES)
        return draw.choice((f"{last}{mark}{other}, {given}", f"{given} {last}{mark}{other}"))
    if family == "apostrophe_variants":
        mark = draw.choice(APOSTROPHES)
        return draw.choice((f"O{mark}{last}, {given}", f"{given} D{mark}{last}"))
    if family == "decomposed_accents":
        return unicodedata.normalize("NFD", draw.choice((f"{_with_past_ascii(draw, last)}, {given}",
                                                         f"{given} {_with_past_ascii(draw, last)}")))
    if family == "spaced_hyphens":
        return draw.choice((f"{last} - {other}, {given}", f"{given} {last} - {other}", f"{last} -{other}, {given}",
                            f"{last}- {other}, {given}"))
    if family == "more_particles":
        particle = draw.choice(MORE_PARTICLES)
        return draw.choice((f"{given} {particle} {last}", f"{particle} {last}, {given}",
                            f"{last.upper()} Y {other.upper()}, {given.upper()}"))
    if family == "two_letter_family_given_first":
        return f"{given} {draw.choice(_HEADS).upper()}{draw.choice(_VOWELS)}"
    if family == "title_after_the_comma":
        return f"{last}, {draw.choice(TITLES)} {given}"
    if family == "family_comma_given":
        return draw.choice((f"{last}, {given}", f"{last}, {given} {other}", f"{last} {other}, {given}"))
    if family == "given_family":
        return draw.choice((f"{given} {last}", f"{given} {other} {last}", f"{given} {other} {last} {made_up_word(draw, 2)}"))
    if family == "given_initial_family":
        return draw.choice((f"{given} {initial}. {last}", f"{given} {initial} {last}"))
    if family == "family_comma_given_initial":
        return draw.choice((f"{last}, {given} {initial}.", f"{last}, {given} {initial}", f"{last}, {given} {initial}. {draw.choice(INITIALS)}."))
    if family == "capitals":
        return draw.choice((f"{last.upper()}, {given.upper()}", f"{given.upper()} {last.upper()}",
                            f"{last.upper()}, {given.upper()} {initial}"))
    if family == "apostrophes":
        mark = draw.choice(("'", "’"))
        return draw.choice((f"O{mark}{last}, {given}", f"{given} O{mark}{last}", f"D{mark}{last}, {given}"))
    if family == "hyphens":
        return draw.choice((f"{last}-{other}, {given}", f"{given}-{other} {last}", f"{given} {last}-{other}"))
    if family == "particles":
        particle = draw.choice(PARTICLES)
        return draw.choice((f"{particle} {last}, {given}", f"{given} {particle} {last}"))
    if family == "joined_particles":
        joined = draw.choice(JOINED)
        return draw.choice((f"{joined}{last}, {given}", f"{given} {joined}{last}"))
    if family == "suffixes":
        suffix = draw.choice(SUFFIXES)
        return draw.choice((f"{last} {suffix}, {given}", f"{given} {last} {suffix}", f"{last}, {given} {suffix}",
                            f"{last}, {given}, {suffix}"))
    if family == "inner_capitals":
        return draw.choice((f"{draw.choice(INNER)}{last}, {given}", f"{given} {draw.choice(INNER)}{last}"))
    if family == "initials":
        second = draw.choice(INITIALS)
        return draw.choice((f"{initial}. {last}", f"{initial}. {second}. {last}", f"{last}, {initial}.",
                            f"{last}, {initial}. {second}.", f"{initial}.{second}. {last}"))
    if family == "past_ascii":
        return draw.choice((f"{_with_past_ascii(draw, last)}, {given}", f"{given} {_with_past_ascii(draw, last)}",
                            f"{last}, {_with_past_ascii(draw, given)}"))
    if family == "greek_and_cyrillic":
        letters = draw.choice((_GREEK, _CYRILLIC))
        return draw.choice((f"{_script_word(draw, letters)}, {_script_word(draw, letters)}",
                            f"{_script_word(draw, letters)} {_script_word(draw, letters)}"))
    if family == "spaces":
        return draw.choice((f"{last},  {given}", f" {last}, {given} ", f"{given}  {last}", f"{last}, {given}  "))
    if family == "titles_and_degrees":
        return draw.choice((f"{draw.choice(TITLES)} {given} {last}", f"{draw.choice(TITLES)} {last}",
                            f"{given} {last}, {draw.choice(DEGREES)}", f"{given} {last} {draw.choice(DEGREES)}",
                            f"{last}, {given} {draw.choice(DEGREES)}"))
    if family == "no_space_after_the_comma":
        return draw.choice((f"{last},{given}", f"{last.upper()},{given.upper()}"))
    if family == "nicknames":
        return draw.choice((f"{last}, {given} ({other})", f'{given} "{other}" {last}', f"{given} {last} ({other})"))
    # ...and those it must not read.
    if family == "small_letters":
        return draw.choice((f"{last.lower()}, {given.lower()}", f"{given.lower()} {last.lower()}"))
    if family == "figures":
        return draw.choice((f"{last}, {given} {draw.randint(1, 99)}", f"{given} {last}{draw.randint(1, 9)}",
                            f"{last}, {given} [{draw.randint(1000000, 9999999)}]"))
    if family == "five_name_words":
        return " ".join(made_up_word(draw, 2) for _place in range(draw.randint(5, 7)))
    if family == "joined_by_a_semicolon":
        return draw.choice((f"{last}, {given}; {other}, {made_up_word(draw, 2)}", f"{given} {last};{other} {last}"))
    if family == "no_capitals":
        return draw.choice((f"{_no_capitals_word(draw)} {_no_capitals_word(draw)}",
                            f"{_no_capitals_word(draw)}, {_no_capitals_word(draw)}"))
    if family == "one_word":
        return draw.choice((last, last.upper(), f"{last},"))
    if family == "a_short_word_inside":
        return draw.choice((f"{last} or {given}", f"{last} of {given}", f"{given} and {last}", f"{last} with {given}"))
    return f"{last} {made_up_word(draw, 9)} {made_up_word(draw, 9)}, {made_up_word(draw, 9)}"


def suffix_forms() -> "list[tuple[str, str, str, bool, str]]":
    """EVERY WAY A SUFFIX IS WRITTEN AFTER A FAMILY NAME ALONE (lane CZ-F's repair 2, Codex's item 2): each word of the family-name reader's one definition (`taxonomy._PERSONS_NAME_SUFFIXES`) with a first capital, in capitals and in small letters, with its point and without, after the family name or after a comma, the family name in mixed case or in capitals, a particle before it or none -- each a (suffix, point, between, capitals, particle)."""
    from synthtwin import taxonomy

    made: "list[tuple[str, str, str, bool, str]]" = []
    for word in sorted(taxonomy._PERSONS_NAME_SUFFIXES):
        for written in sorted({word.capitalize(), word.upper(), word.lower()}):
            for point in ("", "."):
                for between in (" ", ", "):
                    for capitals in (False, True):
                        for particle in ("", "van "):
                            made.append((written, point, between, capitals, particle))
    return made


def with_suffix(family: str, form: "tuple[str, str, str, bool, str]") -> str:
    """A family name alone written with one of `suffix_forms`: `Cedar Jr.`, `van Cedar, iii`, `VAN CEDAR, JR`."""
    written, point, between, capitals, particle = form
    name = f"{particle}{family}"
    return f"{name.upper() if capitals else name}{between}{written}{point}"


def spellings(family: str, count: int = 1000, seed: int = SEED) -> "list[str]":
    """``count`` different generated spellings of one family of names."""
    draw = random.Random(f"{seed}:{family}")
    made: "dict[str, bool]" = {}
    tries = 0
    while len(made) < count and tries < count * 50:
        made[_spelling(family, draw)] = True
        tries += 1
    return list(made)


# -- the tables -----------------------------------------------------------------

SHAPES = ("comma", "apostrophe", "given_first", "capitals", "mixed", "family", "small_letters", "no_capitals",
          "caret", "zero_width", "format_trailing", "initials")


def names_of(count: int, shape: str, seed: int = SEED) -> "list[str]":
    """``count`` different made-up names in one shape (`SHAPES`), one a person."""
    draw = random.Random(f"{seed}:{shape}")
    made: "dict[str, bool]" = {}
    while len(made) < count:
        last = made_up_word(draw, draw.choice((2, 2, 3)))
        given = made_up_word(draw, draw.choice((1, 2, 2)))
        if shape == "comma":
            name = f"{last}, {given}"
        elif shape == "apostrophe":
            name = f"O'{last}, {given}"
        elif shape == "given_first":
            name = f"{given} {last}"
        elif shape == "capitals":
            name = f"{last.upper()}, {given.upper()}"
        elif shape == "family":
            # ...three syllables at least: a made-up name of two (`Name`,
            # `Data`) may be a word the product's own sentences write.
            name = last if len(last) > 6 else made_up_word(draw, 3)
        elif shape == "small_letters":
            name = f"{last.lower()}, {given.lower()}"
        elif shape == "no_capitals":
            name = f"{_no_capitals_word(draw)} {_no_capitals_word(draw)}"
        elif shape == "caret":
            # `FAMILY^GIVEN^M`, one in three `Family^Given^^^`.
            name = (f"{last}^{given}^^^" if len(made) % 3 == 2
                    else f"{last.upper()}^{given.upper()}^{draw.choice(INITIALS)}")
        elif shape == "zero_width":
            name = f"{last},\u200b{given}"
        elif shape == "format_trailing":
            name = f"{last}, {given}\u200e"
        elif shape == "initials":
            name = f"{last} {draw.choice(INITIALS)}."
        else:
            name = _spelling(draw.choice(FAMILIES_READ), draw)
        made[name] = True
    return list(made)


LAYOUTS = ("alone", "beside", "heading", "surname", "clinician", "one_a_row", "uneven", "staff", "person_name", "era",
           "share_edge", "unlisted_role", "run_together",
           # ...and lane CZ-F's repair 2: one, two, three or sixty family
           # names under three names that say a person's name, beside a case
           # number (`FEW`, Codex's item 1); 60 family names each with a
           # suffix under `patient_surname` beside a case number (Codex's item
           # 2); and 49,152 rows in blocks of 12 (`BLOCKS`, the combined
           # verify's item 1).
           "few_surname", "few_clinician", "few_run_together", "suffix_surname", "blocks")
# Each layout's names column: `staff` is the clinicians' layout under a
# neutral name (fewer names than `taxonomy.NAMES_AT_LEAST`: a stated limit),
# `unlisted_role` under a staff heading outside the reader's closed list,
# `run_together` under a name for a family name written in capitals with no
# mark between its words.
COLUMN = {
    "alone": "patient_label", "beside": "patient_label", "heading": "patient_full_name", "surname": "patient_surname",
    "clinician": "surgeon", "one_a_row": "patient_label", "uneven": "patient_label", "staff": "staff_label",
    "person_name": "person_name", "era": "patient_label", "share_edge": "patient_label",
    "unlisted_role": "social_worker",
    "run_together": "PERSONLASTNAME",
    "few_surname": "patient_surname", "few_clinician": "surgeon", "few_run_together": "PERSONLASTNAME",
    "suffix_surname": "patient_surname", "blocks": "patient_label",
}
# The few layouts' shapes: how many different family names each holds,
# every one on many rows.
FEW = {"one": 1, "two": 2, "three": 3, "sixty": 60}
# The suffix layout's shapes: ` Jr.` after each of 60 family names
# (`suffix_jr`), or each written with one of `suffix_forms` (`suffixes`).
SUFFIXED = 60
# The blocks layout: 4,096 blocks of 12 rows, the first cell of each one of
# 1,400 names written in small letters, the 11 others names written
# `Family, Given`, 4,096 people on 11 rows each.
BLOCKS, BLOCK_ROWS, BLOCK_SMALL = 4096, 12, 1400
# The era layout: the early era's people on 2 rows each, written in small
# letters, then the later era's on 12 rows each (116,400 rows).
ERA_EARLY, ERA_EARLY_ROWS, ERA_LATE, ERA_LATE_ROWS = 4200, 2, 9000, 12
# The share edge: of the 1,000 people, those written once in small letters.
SHARE_EDGE_SMALL = 520
PERSON = "patient_ref"
CASE = "case_no"


def _persons(layout: str, rows: int, seed: int) -> "list[int]":
    """The person (or clinician) each row belongs to."""
    draw = random.Random(f"{seed}:{layout}:rows")
    if layout == "one_a_row":
        order = list(range(rows))
    elif layout == "uneven":
        order = []
        person = 0
        while len(order) < rows:
            order += [person] * (draw.randint(11, 30) if person < rows // 66 else draw.randint(1, 5))
            person += 1
        order = order[:rows]
    elif layout in ("clinician", "staff", "unlisted_role"):
        return [draw.randrange(CLINICIANS) for _row in range(rows)]
    else:
        order = [row // ROWS_A_PERSON for row in range(rows)]
    draw.shuffle(order)
    return order


def _era_cells(seed: int) -> "list[str]":
    """The era layout's cells in date order: the early era's names in small letters, then the later era's (116,400 rows)."""
    names = names_of(ERA_EARLY + ERA_LATE, "comma", seed)
    early = [name.lower() for name in names[:ERA_EARLY]]
    return [one for one in early for _row in range(ERA_EARLY_ROWS)] + [
        one for one in names[ERA_EARLY:] for _row in range(ERA_LATE_ROWS)
    ]


def _share_edge_cells(rows: int, seed: int) -> "list[str]":
    """The share edge's cells: each person's name on 20 rows, one of them in small letters for `SHARE_EDGE_SMALL` people."""
    persons = _persons("alone", rows, seed)
    names = names_of(max(persons) + 1, "comma", seed)
    cells: "list[str]" = []
    lowered: "dict[int, bool]" = {}
    for person in persons:
        if person < SHARE_EDGE_SMALL and person not in lowered:
            lowered[person] = True
            cells += [names[person].lower()]
        else:
            cells += [names[person]]
    return cells


def _block_cells(seed: int) -> "list[str]":
    """The blocks layout's cells (49,152 rows): in each block of 12 a name written in small letters, then 11 names written `Family, Given`."""
    whole = names_of(BLOCKS + BLOCK_SMALL, "comma", seed)
    small = [one.lower() for one in whole[BLOCKS:]]
    people = [one for one in whole[:BLOCKS] for _row in range(BLOCK_ROWS - 1)]
    random.Random(f"{seed}:blocks").shuffle(people)
    cells: "list[str]" = []
    for block in range(BLOCKS):
        cells += [small[block % BLOCK_SMALL]] + people[block * (BLOCK_ROWS - 1): (block + 1) * (BLOCK_ROWS - 1)]
    return cells


def _beside_a_case(layout: str, shape: str, rows: int, seed: int) -> "tuple[list[str], list[list[str]], str, list[str]]":
    """A few or suffixed layout: the family names cycled over the rows beside a case number; the real names are the cells and, for a suffixed one, its family names alone too."""
    column = COLUMN[layout]
    families = names_of(SUFFIXED, "family", seed) if layout == "suffix_surname" else names_of(FEW[shape], "family", seed)
    if layout != "suffix_surname":
        values = families
    elif shape == "suffix_jr":
        values = [f"{family} Jr." for family in families]
    else:
        forms_made = suffix_forms()
        values = [with_suffix(family, forms_made[(place * 37) % len(forms_made)]) for place, family in enumerate(families)]
    draw = random.Random(f"{seed}:{layout}:{shape}")
    cells = [values[draw.randrange(len(values))] if len(values) > 2 else values[row % len(values)] for row in range(rows)]
    real = set(cells) | (set(families) if layout == "suffix_surname" else set())
    return [CASE, column], [[f"C{700000 + row}", cells[row]] for row in range(rows)], column, sorted(real)


def table(layout: str, shape: str, rows: int, seed: int = SEED) -> "tuple[list[str], list[list[str]], str, list[str]]":
    """One table: its header, its rows, the names column and that column's different real names."""
    column = COLUMN[layout]
    if layout in ("era", "share_edge", "blocks"):
        cells = (_era_cells(seed) if layout == "era" else _share_edge_cells(rows, seed) if layout == "share_edge"
                 else _block_cells(seed))
        return [column], [[cell] for cell in cells], column, sorted(set(cells))
    if layout in ("few_surname", "few_clinician", "few_run_together", "suffix_surname"):
        return _beside_a_case(layout, shape, rows, seed)
    persons = _persons(layout, rows, seed)
    names = names_of(max(persons) + 1, shape, seed)
    cells = [names[person] for person in persons]
    if layout == "beside":
        header = [PERSON, column]
        body = [[f"P{500000 + persons[row]}", cells[row]] for row in range(rows)]
    elif layout in ("clinician", "staff", "unlisted_role"):
        header = [CASE, column, "room"]
        body = [[f"C{700000 + row}", cells[row], f"Room {1 + row % 9}"] for row in range(rows)]
    else:
        header = [column]
        body = [[cell] for cell in cells]
    return header, body, column, sorted(set(cells))


def zoo_table(layout: str, header: "list[str]", body: "list[list[str]]") -> zoo.Table:
    """The table in the zoo's form, for the zoo's general answers: a record or person key is `identifier`."""
    knows = {name: "identifier" for name in header if name in (PERSON, CASE)}
    return zoo.Table(
        f"names_{layout}", ".csv", lambda n, seed: (header, body), zoo.csv_bytes,  # type: ignore[arg-type]
        {f"names_{layout}": tuple(header)}, knows, zoo._csv_reader(), (),
        person=PERSON if PERSON in header else "",
    )


# -- through the commands ---------------------------------------------------------

# How the questions are answered (as `safe_harbor_forms.MODES`): nobody
# answering; the zoo's general answers, `yes` to the names column's Safe
# Harbor question (`truthful`); the person question `keep` everywhere and
# the names column a reading that publishes values, its Safe Harbor
# question blank (`coded`); `no` to every Safe Harbor question, which
# says what that answer frees; and a reading TYPED on every profile call,
# `--code <names column>` (`typed`) or `--measurement <names column>`
# (`measured`), the zoo's general answers given round by round and the
# names column's Safe Harbor question left blank (lane CZ-F's repair, the
# statistics check's item 4).
MODES = ("unanswered", "truthful", "coded", "no", "typed", "measured")
# The flag each typed mode passes on every profile call.
TYPED_FLAGS = {"typed": "--code", "measured": "--measurement"}


def answer(table_here: zoo.Table, document: "dict", mode: str, column: str) -> None:
    """One round of answers by ``mode``."""
    zoo.answer_generally(table_here, document, frozenset())
    for entry in zoo._entries(document):
        offered = sorted(one for one in zoo._offered(entry) if one not in zoo.AGE_UNIT_ANSWERS)
        if f"{entry.get('column', '')}" == column and offered == ["no", "yes"]:
            entry["your_answer"] = "" if mode in TYPED_FLAGS else "yes"
    if mode == "no":
        forms._answer_no(document)
    if mode == "coded":
        forms._answer_coded(document, (column,))


def _fold(text: str) -> str:
    return " ".join(text.casefold().split())


def _json_strings(value: object) -> "list[str]":
    """Every string a decoded JSON value holds, keys and values, read recursively: each escape stands decoded."""
    found: "list[str]" = []
    waiting = [value]
    while waiting:
        one = waiting.pop()
        if isinstance(one, str):
            found.append(one)
        elif isinstance(one, dict):
            for key, inner in one.items():
                found.append(f"{key}")
                waiting.append(inner)
        elif isinstance(one, list):
            waiting.extend(one)
    return found


# An escape a text for the eye writes for a character it does not print:
# `\x09`, `​`, `\U0001f600`, and the one-letter ones (`\t`, `\n`).
_ESCAPE = re.compile(r"\\(?:x([0-9a-fA-F]{2})|u([0-9a-fA-F]{4})|U([0-9a-fA-F]{8})|([tnrfv\\]))")
_ONE_LETTER_ESCAPES = {"t": "\t", "n": "\n", "r": "\r", "f": "\f", "v": "\v", "\\": "\\"}


def _escapes_decoded(text: str) -> str:
    """A text for the eye with each escape of `_ESCAPE` read as its character."""

    def character(found: "re.Match[str]") -> str:
        figures = found.group(1) or found.group(2) or found.group(3)
        if figures is None:
            return _ONE_LETTER_ESCAPES[found.group(4)]
        code = int(figures, 16)
        return chr(code) if code <= 0x10FFFF else found.group(0)

    return _ESCAPE.sub(character, text)


def published_texts(text: str, json_file: bool) -> "list[str]":
    """The texts the counter reads of one file the commands wrote, or of the screen (lane CZ-F's repair 2, Codex's item 4).

    The text as written; for a JSON file, EVERY STRING it holds DECODED,
    keys and values, read recursively (a name holding a tab stands in the
    file as `\\t`, and once decoded as the tab it holds); for a text for
    the eye, a second reading with its escapes decoded (`\\x09` read as
    the tab), which the counter then folds as it folds every text. The
    re-encoding it replaces (`json.dumps(json.loads(text))`) kept every
    escape, so a name holding a tab, a line break or a character written
    `\\u....` was never found.
    """
    if json_file:
        return [text, *_json_strings(json.loads(text))]
    decoded = _escapes_decoded(text)
    return [text] if decoded == text else [text, decoded]


def _whole_words(text: str, start: int, end: int) -> bool:
    """Whether a stretch of a text is whole words: no letter just before it nor just after it."""
    return (start == 0 or not text[start - 1].isalpha()) and (end == len(text) or not text[end].isalpha())


def counted(real: "list[str]", texts: "list[str]", twin: "list[str]") -> "dict[str, int]":
    """The real names in what the commands wrote and in the twin's column, each text and each different twin cell read once.

    `shown`: the real names written whole in a text (the linear counter,
    `unanswered_identifier_shapes.count_real(..., linear=True)`);
    `shown_folded`: those found with case and spaces folded, as whole
    words (no letter before or after them: a family name of four letters
    stands inside other words of the description by chance); `twin_exact`
    and `twin_folded`: the twin cells equal to a real name; `twin_inside`:
    the twin cells holding a complete real name (folded, as whole words)
    inside a wider value; `twin_names`: the different real names the twin
    writes.
    """
    import unanswered_identifier_shapes as shapes

    linear = shapes.count_real(real, texts, twin, linear=True)
    folded = {_fold(value): True for value in real}
    sizes = sorted({len(key) for key in folded})
    shown: "dict[str, bool]" = {}
    for text in dict.fromkeys(_fold(one) for one in texts):
        for size in sizes:
            for start in range(len(text) - size + 1):
                if text[start:start + size] in folded and _whole_words(text, start, start + size):
                    shown[text[start:start + size]] = True
    exact = dict.fromkeys(real, True)
    seen: "dict[str, tuple[int, int, int]]" = {}
    found = {"twin_exact": 0, "twin_folded": 0, "twin_inside": 0}
    names: "dict[str, bool]" = {}
    for cell in twin:
        if cell not in seen:
            key = _fold(cell)
            equal = 1 if key in folded else 0
            inside = 0
            if not equal:
                for size in sizes:
                    if size >= len(key):
                        break
                    if any(
                        key[start:start + size] in folded and _whole_words(key, start, start + size)
                        for start in range(len(key) - size + 1)
                    ):
                        inside = 1
                        break
            seen[cell] = (1 if cell in exact else 0, equal, inside)
            if equal:
                names[key] = True
        one, equal, inside = seen[cell]
        found["twin_exact"] += one
        found["twin_folded"] += equal
        found["twin_inside"] += inside
    return {"shown": linear["description_values"], "shown_folded": len(shown), **found, "twin_names": len(names)}


def measure(
    folder: pathlib.Path, layout: str, shape: str, rows: int, mode: str = "unanswered", seed: int = SEED,
    small_tables_refused: "bool | None" = None,
) -> "dict[str, object]":
    """One table through profile (and its rounds of answers), generate at seed 0 and validate, counted (`counted`).

    The commands a person types (`cli.main`), nobody at the keyboard, the
    table floor on at 20,000 rows or more unless ``small_tables_refused``
    says otherwise. Returns the exit codes, the names column's role at
    the first and the last description, the questions put to it, the
    counts and the product's own seconds apart from the counting.
    """
    import unanswered_identifier_shapes as shapes
    from synthtwin import cli

    header, body, column, real = table(layout, shape, rows, seed)
    here = zoo_table(layout, header, body)
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / "names.csv"
    source.write_bytes(zoo.csv_bytes(header, body))
    refused = rows >= zoo.KPI_ROWS if small_tables_refused is None else small_tables_refused
    profile = folder / "names-profile.json"
    questions = folder / "names-questions.json"
    screen = io.StringIO()
    texts: "list[str]" = []
    roles: "list[str]" = []
    put: "list[list[str]]" = []

    def read_round() -> None:
        for path in (profile, questions, folder / "names-profile.txt"):
            if path.is_file():
                texts.extend(published_texts(path.read_text(encoding="utf-8"), path.suffix == ".json"))
        if questions.is_file():
            for entry in zoo._entries(json.loads(questions.read_text(encoding="utf-8"))):
                offered = sorted(zoo._offered(entry))
                if f"{entry.get('column', '')}" == column and offered not in put:
                    put.append(offered)
        if profile.is_file():
            for block in json.loads(profile.read_text(encoding="utf-8"))["columns"]:
                if block.get("name") == column:
                    roles.append(f"{block.get('role')}")

    found: "dict[str, object]" = {"layout": layout, "shape": shape, "mode": mode, "rows": rows, "column": column,
                                  "different_names": len(real)}
    started = time.perf_counter()
    generated = validated = -1
    rounds = 0
    typed = [TYPED_FLAGS[mode], column] if mode in TYPED_FLAGS else []
    with shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        code = cli.main(["profile", f"{source}", "--replace", *typed], small_tables_refused=refused)
        if code == 0:
            read_round()
        while mode != "unanswered" and code == 0 and rounds < forms.ANSWER_ROUNDS_AT_MOST:
            document = json.loads(questions.read_text(encoding="utf-8"))
            before = json.dumps(document, sort_keys=True)
            answer(here, document, mode, column)
            if json.dumps(document, sort_keys=True) == before:
                break
            questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
            code = cli.main(["profile", f"{source}", "--replace", "--answers", f"{questions}", *typed],
                            small_tables_refused=refused)
            rounds += 1
            if code == 0:
                read_round()
        found["profile_seconds"] = round(time.perf_counter() - started, 1)
        stage = time.perf_counter()
        if code == 0:
            generated = cli.main(["generate", f"{profile}", "--replace", "--seed", "0"], small_tables_refused=refused)
        found["generate_seconds"] = round(time.perf_counter() - stage, 1)
        stage = time.perf_counter()
        if generated == 0:
            validated = cli.main(["validate", f"{profile}", "--replace"], small_tables_refused=refused)
        found["validate_seconds"] = round(time.perf_counter() - stage, 1)
    found["product_seconds"] = round(time.perf_counter() - started, 1)
    found.update({"profile": code, "generate": generated, "validate": validated, "rounds": rounds,
                  "roles": roles, "asked": put})
    if code != 0:
        found["screen"] = screen.getvalue()[-400:]
    texts.extend(published_texts(screen.getvalue(), False))
    twin: "list[str]" = []
    if generated == 0:
        for written in ("names-twin-report.txt", "names-twin-quality.txt"):
            if (folder / written).is_file():
                texts.extend(published_texts((folder / written).read_text(encoding="utf-8"), False))
        with open(folder / "names-twin.csv", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            twin_header = next(reader)
            place = twin_header.index(column)
            twin = [row[place] if place < len(row) else "" for row in reader]
    found.update(counted(real, texts, twin))
    found["twin_sample"] = twin[:2]
    return found


# What one measured table must show in every mode but `no`: no real name
# written anywhere or in the twin, and the column held or asked.
BAR_KEYS = ("shown", "shown_folded", "twin_exact", "twin_folded", "twin_inside")
# The roles that publish no value (`taxonomy.ROLES_PUBLISHING_NOTHING`).
PUBLISHING_NOTHING = ("numeric_unrepresentable", "identifier", "free_text")


def failures(seen: "dict[str, object]") -> "list[str]":
    """What one measured table fails of the bar (an empty list where it holds); `no` is judged by what it frees, never failed."""
    failed: "list[str]" = []
    if seen.get("profile") != 0 or seen.get("generate") != 0:
        failed += [f"exits {seen.get('profile')} {seen.get('generate')}"]
    if seen.get("mode") == "no":
        return failed
    failed += [f"{key} {seen[key]}" for key in BAR_KEYS if seen.get(key)]
    asked = seen.get("asked") or []
    put = any(one == ["no", "yes"] or "identifier" in one for one in asked)  # type: ignore[union-attr]
    roles = seen.get("roles") or []
    held = bool(roles) and roles[-1] in PUBLISHING_NOTHING  # type: ignore[index]
    if not held:
        failed += [f"published as {roles[-1] if roles else 'nothing'}"]  # type: ignore[index]
    if (
        seen.get("mode") in ("unanswered", *TYPED_FLAGS) and not put and seen.get("layout") != "beside"
        and roles and roles[0] != "free_text"  # type: ignore[index]
    ):
        failed += ["no question put"]
    return failed
