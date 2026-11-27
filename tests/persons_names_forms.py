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
  Given` on 12 rows each (the values the reader reads are a sample free
  of the order of the rows);
- `share_edge`: 1,000 people on 20 rows, 520 of them written once in
  small letters (65.8 per cent of the different values names: under the
  two in three, a stated limit until lane CZ-G-b's half);
- `unlisted_role`: 60 clinicians under `social_worker`, a staff heading
  outside the reader's closed list (a stated limit until lane CZ-G-b
  added it);
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
  rows each after it (the combined verify's item 1);
- and from lane CZ-G-b (plan P4-D494): `share_half` and `share_beyond`,
  every person also written once in small letters (half of the different
  values names) and a third of them a second time with no space after the
  comma (past half); `cycled`, 60,000 rows whose every fourth row is one of
  1,400 names in small letters cycled in row order; `frequency`, 4,200
  names on 11 rows each beside 640 codes on 100 rows each (110,200 rows);
  `role_<heading>`, 60 clinicians under a staff heading it adds
  (`STAFF_HEADINGS_ADDED`) or leaves (`STAFF_HEADINGS_LEFT`); and
  `control_<heading>`, that heading's control of 40 ordinary labels
  (`control_labels`), no name among them;
- and from lane CZ-G-b's repair 1: `many_rows`, 2,800 names on 25 rows
  each beside 3,000 more people written once in small letters (73,000
  rows: the names under half of the different values, past the sample's
  bound, the walk's reading); and `crna_beside`, 60 clinicians written
  `Given Family CRNA` under `anesthesia_provider` beside 1,000 patients
  (`patient_ref`) on 20 rows each;
- and from lane CZ-G-b's repair 2: `relation_beside`, an emergency contact
  for each of 1,000 people on 20 rows each, written `Family, Relation`
  (`RELATIONS`) under `emergency_contact_name` beside a case number.
  `price_table` reads a table of several
  label columns, each named for what it holds, through the first profile
  run: which are held (`PRICE_FAMILIES`).

THE SHAPES: `comma` (`Family, Given`), `apostrophe` (`O'Family, Given`),
`given_first` (`Given Family`), `capitals` (`FAMILY, GIVEN`), `mixed`
(every family of spellings of `spellings`, drawn per person), `family`
(the family name alone), `caret` (a health message's name field,
`FAMILY^GIVEN^M`, one in three `Family^Given^^^`), `zero_width`
(`Family,` U+200B `Given`), `format_trailing` (`Family, Given` U+200E) and
`initials` (`Family J.`, read under a clinician's heading alone); two
the reader does not read, its stated limits: `small_letters` (`family,
given`) and `no_capitals` (made-up names in scripts with no capitals); and
lane CZ-G-b's residual spellings, read since: `caret_repeat`
(`FAMILY^GIVEN~FAMILY^GIVEN^M`), `caret_amp` (`van Family&van&Family^Given`),
`apostrophe_more` (the eight marks of `APOSTROPHES_MORE`), `title_particle`
(`Dr. de la Family`), `suffix_more` (`Family 2nd, Given`, `Given Family
Esq.`) and `inside_word` (`Fam` U+200B `ily, Given`: each mark of
`INSIDE_MARKS`, drawn as nothing, inside the family name in turn).

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
import signal
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
# RELEASE 37, LANE PRIVACY: common given names, written here apart from the
# product's list (`synthtwin.given_names`) and never read from it, each as a
# table writes it; the family names beside them stay made up. 162 names of
# several origins, eight with a mark (`José`).
COMMON_GIVEN = (
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",
    "Christopher", "Daniel", "Matthew", "Anthony", "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth",
    "Kevin", "Brian", "George", "Edward", "Ronald", "Timothy", "Jason", "Jeffrey", "Ryan", "Jacob", "Gary",
    "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon", "Benjamin", "Samuel",
    "Gregory", "Alexander", "Patrick", "Dennis", "Tyler", "Aaron", "Henry", "Douglas", "Peter", "Walter",
    "Ethan", "Harold", "Carl", "Arthur", "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan",
    "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra", "Ashley", "Kimberly", "Emily",
    "Donna", "Michelle", "Carol", "Amanda", "Dorothy", "Melissa", "Deborah", "Stephanie", "Rebecca", "Sharon",
    "Laura", "Cynthia", "Kathleen", "Amy", "Angela", "Shirley", "Anna", "Brenda", "Pamela", "Emma", "Nicole",
    "Helen", "Samantha", "Katherine", "Christine", "Debra", "Rachel", "Carolyn", "Janet", "Catherine", "Maria",
    "Diane", "Ruth", "Julie", "Olivia", "Joyce", "Victoria", "Kelly", "Lauren", "Christina", "Joan", "Evelyn",
    "Judith", "Megan", "Andrea", "Cheryl", "Hannah", "Martha", "Gloria", "Teresa", "Sara", "Frances", "Kathryn",
    "Jose", "Juan", "Luis", "Carlos", "Jorge", "Miguel", "Pedro", "Manuel", "Francisco", "Antonio", "Guadalupe",
    "Rosa", "Carmen", "Ana", "Mohammed", "Ahmed", "Fatima", "Aisha", "Wei", "Mei", "Minh", "Linh", "Priya",
    "Rahul", "Kwame", "Ngozi", "Hiroshi", "Yuki", "José", "María", "Zoë", "Chloé", "Renée", "Inés", "Raúl",
    "Héctor",
)


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
          "caret", "zero_width", "format_trailing", "initials",
          # ...and lane CZ-G-b's residual spellings (plan P4-D494 item 3):
          # the name field repeated after `~`, its family name in `&`
          # subcomponents, the apostrophe marks the one definition gained, a
          # title before a particle-led family name, and the suffix words it
          # gained after a name written whole.
          "caret_repeat", "caret_amp", "apostrophe_more", "title_particle", "suffix_more",
          # ...and a character drawn as nothing inside the family name
          # (`INSIDE_MARKS`, the orchestrator's LANE CZ-G-b RULINGS 2).
          "inside_word")
# The owed marks a display draws as nothing, written inside a family name in
# turn: the zero-width space, non-joiner and joiner, the two direction
# marks, the word joiner, the byte order mark and the soft hyphen.
INSIDE_MARKS = ("​", "‌", "‍", "‎", "‏", "⁠", "﻿", "­")
# The apostrophe marks lane CZ-G-b added to the one definition: the okina,
# the modifier letter prime, the prime, the full-width apostrophe, the
# modifier letter reversed comma, the high reversed quotation mark, the
# reversed prime and the full-width grave accent.
APOSTROPHES_MORE = ("ʻ", "ʹ", "′", "＇", "ʽ", "‛", "‵", "｀")
# The suffix words lane CZ-G-b added to the one definition, written as a
# name writes them.
SUFFIXES_MORE = ("Snr.", "Snr", "Jnr.", "Esq.", "Esq", "2nd", "3rd", "4th")
TITLED_PARTICLES = ("de la", "van der", "van", "de", "von", "del", "da", "du")


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
        elif shape == "caret_repeat":
            # `FAMILY^GIVEN~FAMILY^GIVEN^M`: the field repeated, a middle
            # initial in the second.
            name = f"{last.upper()}^{given.upper()}~{last.upper()}^{given.upper()}^{draw.choice(INITIALS)}"
        elif shape == "caret_amp":
            # `van Family&van&Family^Given`, or `FAMILY&&FAMILY^GIVEN^M`.
            name = (f"van {last}&van&{last}^{given}" if len(made) % 2
                    else f"{last.upper()}&&{last.upper()}^{given.upper()}^{draw.choice(INITIALS)}")
        elif shape == "apostrophe_more":
            mark = APOSTROPHES_MORE[len(made) % len(APOSTROPHES_MORE)]
            name = f"O{mark}{last}, {given}" if len(made) % 2 else f"{given} D{mark}{last}"
        elif shape == "title_particle":
            name = f"{draw.choice(TITLES)} {draw.choice(TITLED_PARTICLES)} {last}"
        elif shape == "suffix_more":
            suffix = SUFFIXES_MORE[len(made) % len(SUFFIXES_MORE)]
            name = f"{last} {suffix}, {given}" if len(made) % 2 else f"{given} {last} {suffix}"
        elif shape == "inside_word":
            mark = INSIDE_MARKS[len(made) % len(INSIDE_MARKS)]
            cut = f"{last[:len(last) // 2]}{mark}{last[len(last) // 2:]}"
            name = f"{cut}, {given}" if len(made) % 2 else f"{given} {cut}"
        elif shape in GIVEN_SHAPES:
            # ...release 37, lane PRIVACY: a common given name (`COMMON_GIVEN`)
            # beside a made-up family name, in small letters or capitals.
            common = draw.choice(COMMON_GIVEN)
            name = {
                "given_small": f"{last.lower()}, {common.lower()}",
                "given_first_small": f"{common.lower()} {last.lower()}",
                "given_initial_small": f"{common.lower()} {last[:1].lower()}.",
                "given_capitals_no_comma": f"{last.upper()} {common.upper()}",
                "given_small_particle": f"{draw.choice(('de la', 'van der', 'al-', 'o')).rstrip('-')} {last.lower()}, "
                                        f"{common.lower()}",
            }[shape]
        else:
            name = _spelling(draw.choice(FAMILIES_READ), draw)
        made[name] = True
    return list(made)


# RELEASE 37, LANE PRIVACY: the shapes of names that carry a common given
# name but no capital the reader's shapes read (`names_of`), each one a
# person; and the given name alone, which people share (`given_alone_cells`).
GIVEN_SHAPES = ("given_small", "given_first_small", "given_initial_small", "given_capitals_no_comma",
                "given_small_particle")


def given_alone_cells(rows: int, small: bool, seed: int = SEED) -> "list[str]":
    """Each person's given name alone on each of their rows (`ROWS_A_PERSON`), drawn from `COMMON_GIVEN`, written as the list writes it or in small letters: names people share, as a column of first names holds them."""
    persons = _persons("alone", rows, seed)
    draw = random.Random(f"{seed}:given_alone")
    given = [draw.choice(COMMON_GIVEN) for _person in range(max(persons) + 1)]
    return [given[person].lower() if small else given[person] for person in persons]


LAYOUTS = ("alone", "beside", "heading", "surname", "clinician", "one_a_row", "uneven", "staff", "person_name", "era",
           "share_edge", "unlisted_role", "run_together",
           # ...and lane CZ-F's repair 2: one, two, three or sixty family
           # names under three names that say a person's name, beside a case
           # number (`FEW`, Codex's item 1); 60 family names each with a
           # suffix under `patient_surname` beside a case number (Codex's item
           # 2); and 49,152 rows in blocks of 12 (`BLOCKS`, the combined
           # verify's item 1).
           "few_surname", "few_clinician", "few_run_together", "suffix_surname", "blocks",
           # ...and lane CZ-G-b (plan P4-D494): the share at half (`share_half`,
           # every person also written once in small letters) and past it
           # (`share_beyond`, a third of them a second time, with no space
           # after the comma); a spelling cycled in row order (`cycled`, 60,000
           # rows); names on fewer rows than codes (`frequency`, 110,200 rows);
           # 60 clinicians under each staff heading it adds or leaves
           # (`role_<heading>`), and each heading's control of 40 ordinary
           # labels (`control_<heading>`).
           "share_half", "share_beyond", "cycled", "frequency",
           "role_case_manager", "role_next_of_kin", "role_witness", "role_pharmacy_resident", "role_er_md",
           "role_second_reader", "role_np",
           "control_social_worker", "control_next_of_kin", "control_witness", "control_staff", "control_er_md",
           # ...and lane CZ-G-b's repair 1: names on many rows beside more
           # rare spellings (`many_rows`, 73,000 rows), and 60 clinicians
           # written with the degree after the name beside 1,000 patients
           # (`crna_beside`); and its repair 2: 1,000 emergency contacts
           # written `Family, Relation` beside a case number
           # (`relation_beside`).
           "many_rows", "crna_beside", "relation_beside",
           # ...and release 37's lane PRIVACY: each person's common given name
           # alone, as the list writes it and in small letters
           # (`given_alone_cells`).
           "given_alone", "given_alone_small")
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
    "share_half": "patient_label", "share_beyond": "patient_label", "cycled": "patient_label",
    "frequency": "patient_label",
    "role_case_manager": "case_manager", "role_next_of_kin": "next_of_kin", "role_witness": "witness",
    "role_pharmacy_resident": "pharmacy_resident", "role_er_md": "er_md", "role_second_reader": "second_reader",
    "role_np": "np",
    "control_social_worker": "social_worker", "control_next_of_kin": "next_of_kin", "control_witness": "witness",
    "control_staff": "staff", "control_er_md": "er_md",
    "many_rows": "patient_label", "crna_beside": "anesthesia_provider",
    "relation_beside": "emergency_contact_name",
    "relation_no_mark": "emergency_contact_name", "relation_dash": "next_of_kin", "surnames_kept_as_roles": "surgeon",
    "older_role_kin": "next_of_kin", "older_role_contact": "emergency_contact", "older_role_witness": "witness",
    "older_role_reviewer": "reviewer",
    "given_alone": "patient_label", "given_alone_small": "patient_label",
}
# THE STAFF HEADINGS OF LANE CZ-G-b (plan P4-D494 item 4), each with the
# group of its control: 40 ordinary labels such a column could hold. Those
# ADDED to the heading arm's closed list, their controls not held...
STAFF_HEADINGS_ADDED = {
    "social_worker": "social_and_case", "case_manager": "social_and_case", "scribe": "sign_off",
    "reviewer": "sign_off", "cosigner": "sign_off", "witness": "sign_off", "second_reader": "sign_off",
    "staff": "staff_and_employee", "employee": "staff_and_employee", "nok": "kin", "next_of_kin": "kin",
    "emergency_contact": "kin", "er_md": "staffing", "rad_tech": "staffing", "lab_resident": "staffing",
    "pharmacy_resident": "staffing", "lab_md": "staffing", "pharmacy_md": "staffing",
}
# ...and those LEFT OUT, whose controls a name that says a person's name
# would hold: a swab's results and a radiograph's views (`np`, `pa`), and
# organisations (`billing_provider`, `care_provider`, `procedure_provider`
# and a workplace's operator, reader and providers).
STAFF_HEADINGS_LEFT = {
    "np": "results_and_views", "pa": "results_and_views", "billing_provider": "organisations",
    "care_provider": "organisations", "procedure_provider": "organisations", "lab_operator": "organisations",
    "pharmacy_reader": "organisations", "lab_care_provider": "organisations",
    "pharmacy_care_provider": "organisations",
}
CONTROL_LABELS = {
    "results_and_views": (
        "Negative", "Positive", "Not Detected", "Detected", "Indeterminate", "Invalid", "Not Done", "Inconclusive",
        "Presumptive Positive", "Equivocal", "Reactive", "Nonreactive", "Borderline", "Abnormal", "Normal",
        "Upright", "Supine", "Lateral", "Portable", "Decubitus", "Oblique", "Erect", "Prone", "Left Lateral",
        "Right Lateral", "Expiration", "Inspiration", "Granted", "Denied", "Pending Approval", "Not Required",
        "Submitted", "Expired", "Peer Review", "Appealed", "Overturned", "Partial Approval", "Retro Review",
        "Withdrawn", "Cancelled",
    ),
    "social_and_case": (
        "Assigned", "Not Assigned", "Consulted", "Not Consulted", "Referred", "Declined", "Seen", "Not Seen",
        "Unassigned", "Inpatient Team", "Outpatient Team", "Not Needed", "Not Applicable", "Completed",
        "In Progress", "Initial Assessment", "Reassessment", "Transferred", "Closed", "Active", "Inactive",
        "Pending", "Unknown", "Other", "None", "Yes", "No", "Follow Up Needed", "Discharge Team", "Care Team",
        "Consult Placed", "On Hold", "Waitlist", "Weekend Coverage", "Covering", "Hospice", "Home Health",
        "Family Meeting", "Patient Declined", "Signed Off",
    ),
    "sign_off": (
        "Reviewed", "Not Reviewed", "Pending Review", "Auto Verified", "Interface", "System", "Signed", "Unsigned",
        "Cosigned", "Not Required", "Required", "Verbal", "Written", "Telephone", "Completed", "Declined", "Refused",
        "Present", "Not Present", "Unavailable", "Absent", "Waived", "Yes", "No", "Pending", "Unknown", "None",
        "Other", "Self", "Patient", "Family Member", "Staff", "Interpreter", "Nursing", "Physician", "Resident",
        "Attending", "Outside Provider", "Done", "Cancelled",
    ),
    "staff_and_employee": (
        "Full Time", "Part Time", "Per Diem", "Contract", "Contractor", "Agency", "Locum", "Float Pool", "Traveler",
        "Volunteer", "Student", "Temporary", "Permanent", "Active", "Inactive", "Terminated", "On Leave", "Retired",
        "Casual", "Seasonal", "Intern", "Resident", "Fellow", "Nursing", "Physician", "Pharmacist", "Technician",
        "Therapist", "Unknown", "Other", "None", "Pending", "Assigned", "Unassigned", "Day Shift", "Night Shift",
        "Rotating", "Supervisor", "Director", "Trainee",
    ),
    "kin": (
        "Mother", "Father", "Spouse", "Son", "Daughter", "Brother", "Sister", "Aunt", "Uncle", "Grandmother",
        "Grandfather", "Grandson", "Granddaughter", "Grandchild", "Niece", "Nephew", "Cousin", "Husband", "Wife",
        "Partner", "Fiance", "Friend", "Guardian", "Legal Guardian", "Caregiver", "Neighbor", "Stepmother",
        "Stepfather", "Parent", "Child", "Relative", "Self", "Other", "Unknown", "None", "Declined",
        "Not Applicable", "Significant Other", "Foster Parent", "Domestic Partner",
    ),
    "staffing": (
        "Rotating", "On Call", "Night Float", "Day Shift", "Night Shift", "Moonlighter", "Medical Director",
        "Pathologist", "Technologist", "Supervisor", "Lead", "Trainee", "Fellow", "Not Assigned", "Unassigned",
        "Pending", "Other", "Unknown", "None", "Resident", "Attending", "Locum", "Agency", "Senior Resident",
        "Junior Resident", "Chief Resident", "Staff", "Student", "Intern", "Supervising", "Covering", "Relief",
        "Backup", "Primary", "Float", "Observer", "Radiologist", "Technician", "Nursing", "Physician",
    ),
}
CONTROL_LAYOUT_HEADING = {layout: COLUMN[layout] for layout in COLUMN if layout.startswith("control_")}


def control_labels(group: str, seed: int = SEED) -> "list[str]":
    """The 40 ordinary labels of one control group (`CONTROL_LABELS`), or, for `organisations`, 40 made-up organisations' names of one word each, the shape the laboratories and pharmacies of lane CZ-F's combined verify item 2 were written in."""
    if group != "organisations":
        return list(CONTROL_LABELS[group])
    draw = random.Random(f"{seed}:organisations")
    made: "dict[str, bool]" = {}
    while len(made) < 40:
        made[made_up_word(draw, draw.choice((2, 3)))] = True
    return list(made)


# THE SMALL CONTROLS: three labels a column under each added heading's
# group may hold and nothing else (lane CZ-G-b): the closed list's words
# lane CZ-G-b added keep each from being read as one, two or three family
# names alone, which the heading arm holds whatever their number.
SMALL_CONTROLS = {
    "social_and_case": ("Consulted", "Not Consulted", "Assigned"),
    "sign_off": ("Verbal", "Written", "Telephone"),
    "staff_and_employee": ("Full Time", "Part Time", "Per Diem"),
    "kin": ("Mother", "Father", "Daughter"),
    "staffing": ("Day Shift", "Night Shift", "Rotating"),
}
# THE HELD-OUT CONTROLS (lane CZ-G-b's repair 1, the orchestrator's LANE
# CZ-G-b RULINGS 3 (3)): 40 ordinary labels of each group's kind that are
# OUTSIDE the closed list's words (the labels of `CONTROL_LABELS` narrowed
# that list, so they pass by construction). Read as names under a heading
# that says a person's name, most of them are held there: the stated price
# of keeping the staff headings (owner lane CZ-G-b2).
HELD_OUT_CONTROLS = {
    "social_and_case": (
        "Requested", "Scheduled", "Accepted", "Rejected", "Endorsed", "Notified", "Contacted", "Left Message",
        "No Answer", "Not Contacted", "Voicemail", "Initial Visit", "Follow Up", "Left Early", "Admitted", "Open",
        "Resolved", "Deferred", "Recommended", "Screened", "Not Screened", "Eligible", "Not Eligible", "Enrolled",
        "Not Enrolled", "High Risk", "Low Risk", "Moderate Risk", "Urgent", "Routine", "Same Day", "Next Day",
        "Telehealth", "In Person", "Phone Call", "Bedside", "Walk In", "Placement Search", "Housing Referral",
        "Transport Arranged",
    ),
    "sign_off": (
        "Countersigned", "Rejected", "Returned", "Amended", "Addended", "Finalized", "Preliminary", "Final", "Corrected",
        "Electronic", "Paper", "Wet Signature", "Remote", "On Site", "Video", "Audio Only", "Concur", "Disagree",
        "Discrepancy", "Agreed", "Overread", "No Change", "Major Discrepancy", "Minor Discrepancy", "Not Witnessed",
        "Witnessed", "Notary", "Translator", "Guardian Consent", "Accepted", "Locked", "Unlocked", "Draft", "Saved",
        "Submitted", "Released", "Not Released", "Expedited", "Urgent", "Routine",
    ),
    "staff_and_employee": (
        "Exempt", "Non Exempt", "Hourly", "Salaried", "Benefited", "Union", "Non Union", "Probation", "Onboarding",
        "Separated", "Rehire", "Hybrid", "Onsite", "Clinical", "Non Clinical", "Credentialed", "Not Credentialed",
        "Licensed", "Unlicensed", "Registered", "Certified", "Provisional", "Emeritus", "Adjunct", "Visiting",
        "Faculty", "Courtesy", "Affiliate", "Employed", "Independent", "Leased", "Outsourced", "Internal", "Day",
        "Evening", "Night", "Weekend", "Flex", "Benefits Eligible", "Short Notice",
    ),
    "kin": (
        "Stepson", "Stepdaughter", "Half Sibling", "Step Sibling", "Sibling", "Mother In Law", "Father In Law",
        "Son In Law", "Daughter In Law", "Brother In Law", "Sister In Law", "Godparent", "Godmother", "Godfather",
        "Ward", "Roommate", "Coworker", "Employer", "Landlord", "Attorney", "Power Of Attorney", "Health Proxy",
        "Conservator", "Clergy", "Pastor", "Former Partner", "Ex Husband", "Ex Partner", "Boyfriend", "Girlfriend",
        "Life Partner", "Companion", "Adopted Son", "Adopted Child", "Foster Child", "Great Grandparent",
        "Godchild", "Stepchild", "Other Kin", "Legal Representative",
    ),
    "staffing": (
        "Moonlighting", "Overnight Coverage", "Night Coverage", "Nighthawk", "Overnight", "Swing", "Evening Block",
        "Weekend Block", "Holiday", "Backup Call", "Home Call", "In House", "Off Site", "Remote Read",
        "Preliminary Read", "Final Read", "Senior", "Junior", "Chief", "Associate", "Section Head", "Lead Role",
        "Charge Lead", "Agency Pool", "Visiting", "Rotator", "Shadow", "Orientee", "Preceptor", "Mentor",
        "Supervised", "Unsupervised", "Independent", "Credentialed", "Day Pod", "Night Pod", "Gold Pod",
        "Blue Pod", "Red Pod", "Green Pod",
    ),
}
# THE NEAR-MISS LABELS (lane CZ-G-b's repair 1, the orchestrator's LANE
# CZ-G-b RULINGS 3 (4)): 300 made-up labels of a kind -- a medicine alone or
# with its salt, a procedure in one word or two, a department with a number
# or a word -- of which the share given are written in two capitalised words
# (a person's name written given name first has the same shape): at half or
# more the value arm holds such a column, a stated band (P4-D494 (1)).
NEAR_MISS_KINDS = ("medicine", "procedure", "department")
NEAR_MISS_SHARES = (45, 50, 55, 60, 66, 70)
NEAR_MISS_LABELS = 300
_SALTS = ("Sodium", "Potassium", "Chloride", "Sulfate", "Tartrate", "Succinate", "Acetate", "Citrate", "Phosphate",
          "Bromide", "Maleate", "Gluconate")
_PLACES = ("Unit", "Ward", "Wing", "Floor", "Annex", "Pavilion", "Tower", "Suite")
# ...and labels ending in an ordinal, the suffix words lane CZ-G-b gave the
# one definition (`Booster Dose 2nd`: read as a name written whole, the
# statistics check's item 8, stated in P4-D494 (3)).
_ORDINAL_KINDS = ("Dose", "Booster", "Nerve", "Opinion", "Cycle", "Round", "Visit", "Attempt")


def near_miss_labels(kind: str, share: int, capitals: bool, seed: int = SEED) -> "list[str]":
    """`NEAR_MISS_LABELS` made-up labels of one kind (`NEAR_MISS_KINDS`, or `ordinal`), ``share`` per cent of them written in two capitalised words (for `ordinal`, every one three words ending in an ordinal), in capitals where ``capitals`` says."""
    draw = random.Random(f"{seed}:{kind}:{share}")
    stems: "dict[str, bool]" = {}
    while len(stems) < NEAR_MISS_LABELS:
        stems[made_up_word(draw, draw.choice((3, 4)))] = True
    words = list(stems)
    two = NEAR_MISS_LABELS * share // 100
    labels: "list[str]" = []
    for place, stem in enumerate(words):
        if kind == "ordinal":
            labels += [f"{stem} {_ORDINAL_KINDS[place % len(_ORDINAL_KINDS)]} {('2nd', '3rd', '4th')[place % 3]}"]
        elif kind == "medicine":
            labels += [f"{stem} {_SALTS[place % len(_SALTS)]}" if place < two else stem]
        elif kind == "procedure":
            labels += [f"{stem} {words[(place * 7 + 3) % len(words)]}ectomy" if place < two else f"{stem}otomy"]
        else:
            labels += [f"{stem} {_PLACES[place % len(_PLACES)]}" if place < two else f"{stem} {place % 9 + 1}"]
    return [label.upper() for label in labels] if capitals else labels


# THE PRICE FAMILIES of K-HZ-42 (lane CZ-G-b's repair 1), each one table of
# several label columns beside a case number, read by `price_table`: the
# held-out controls under each staff heading added (`held_out`), the
# near-miss labels in mixed case and in capitals, and the ordinal labels.
PRICE_FAMILIES = ("held_out", "near_miss_mixed", "near_miss_capitals")


def price_columns(family: str, seed: int = SEED) -> "dict[str, list[str]]":
    """The label columns of one price family, by column name."""
    if family == "held_out":
        return {heading: list(HELD_OUT_CONTROLS[group]) for heading, group in sorted(STAFF_HEADINGS_ADDED.items())}
    capitals = family.endswith("capitals")
    columns = {f"{kind}_{share}": near_miss_labels(kind, share, capitals, seed)
               for kind in NEAR_MISS_KINDS for share in NEAR_MISS_SHARES}
    if not capitals:
        columns["dose_label"] = near_miss_labels("ordinal", 100, False, seed)
    return columns


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
    elif layout in ("clinician", "staff", "unlisted_role") or layout.startswith("role_"):
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


# Lane CZ-G-b's cells-built layouts: the cycled spelling's rows, its small
# spellings and its names; the frequency layout's names on 11 rows each and
# codes on 100 rows each; the share past half's people written a second
# time with no space after the comma.
CYCLED_ROWS, CYCLED_EVERY, CYCLED_SMALL, CYCLED_NAMES = 60000, 4, 1400, 3000
FREQUENCY_NAMES, FREQUENCY_NAME_ROWS, FREQUENCY_CODES, FREQUENCY_CODE_ROWS = 4200, 11, 640, 100
SHARE_BEYOND_SECOND = 300
# Lane CZ-G-b's repair 1: the names on many rows (`many_rows`, the
# statistics check's item 1: 48.3 per cent of the different values names,
# 95.9 per cent of the rows), and the clinicians written with a degree.
MANY_ROWS_NAMES, MANY_ROWS_EACH, MANY_ROWS_SMALL = 2800, 25, 3000
MANY_ROWS = MANY_ROWS_NAMES * MANY_ROWS_EACH + MANY_ROWS_SMALL
CRNA_DEGREE = "CRNA"
# Lane CZ-G-b's repair 2 (the combined verify's item 1): the relations an
# emergency contact is written with after the contact's family name and a
# comma, each a word lane CZ-G-b keeps as the last word of a role.
RELATIONS = ("Mother", "Father", "Daughter", "Brother", "Sister", "Wife", "Aunt", "Uncle", "Niece", "Nephew",
             "Grandmother", "Grandfather", "Neighbor", "Stepmother")
# Batch 4t's fix round 4 (the orchestrator's LANE I4t RULINGS 5, push critic 24's B1): the critic's three tables,
# one row a record beside a case number -- (a) 1,000 contacts written `Family Relation` (twelve relations, no mark)
# under `emergency_contact_name` and (c) written `Family-Relation` (a dash, no space) under `next_of_kin`, 20 rows
# each; (b) 60 clinicians' family names alone under `surgeon`, each on about 333 rows, 35 of them words lane CZ-G-b
# keeps as roles and 25 ordinary made-up family names.
RELATIONS_TWELVE = RELATIONS[:12]
ROLE_WORD_SURNAMES = (
    "Witness", "Supervisor", "Mother", "Intern", "Father", "Daughter", "Brother", "Sister", "Aunt", "Uncle",
    "Grandmother", "Grandfather", "Grandson", "Granddaughter", "Grandchild", "Niece", "Nephew", "Wife", "Fiance",
    "Stepmother", "Stepfather", "Neighbor", "Moonlighter", "Trainee", "Locum", "Pathologist", "Radiologist",
    "Cardiologist", "Hospitalist", "Intensivist", "Perfusionist", "Anesthesiologist", "Proceduralist", "Circulator",
    "Dentist",
)
ORDINARY_SURNAMES = 25
# Batch 4t's fix round 5 (the orchestrator's LANE I4t RULINGS 6; the scoped verify's item 1): a person's name before a
# word of the OLDER closed list of roles (`taxonomy._ROLE_AND_SERVICE_WORDS`), under the staff headings lane CZ-G-b
# made ones that say a person's name, one row a record beside a case number, 1,000 contacts on 20 rows each: the
# words of a relation after `Family` under `next_of_kin` (`older_role_kin`) and after `Given Family,` under
# `emergency_contact` (`older_role_contact`); the words of a clinician after `Given Family,` under `witness`
# (`older_role_witness`) and after `Given Family` under `reviewer` (`older_role_reviewer`); `OLDER_ROLE_GIVEN` given
# names in turn.
OLDER_ROLE_RELATIONS = ("Spouse", "Parent", "Guardian", "Friend", "Relative", "Caregiver")
OLDER_ROLE_CLINICIANS = ("Nurse", "Physician", "Resident", "Pharmacist", "Therapist", "Technician", "Surgeon",
                         "Attending")
OLDER_ROLE_FORMS = {
    "older_role_kin": ("{f} {w}", OLDER_ROLE_RELATIONS), "older_role_contact": ("{g} {f}, {w}", OLDER_ROLE_RELATIONS),
    "older_role_witness": ("{g} {f}, {w}", OLDER_ROLE_CLINICIANS),
    "older_role_reviewer": ("{g} {f} {w}", OLDER_ROLE_CLINICIANS),
}
OLDER_ROLE_GIVEN = 200


def older_role_contacts(layout: str, people: int, seed: int = SEED) -> "tuple[list[str], list[str]]":
    """One older-role layout's contacts, one a person (`OLDER_ROLE_FORMS`), and the real names they hold beside them: each family name alone and, where a given name stands first, each given name alone and each `Given Family`. Family and given names are made up, three syllables at least (`names_of`'s `family`), the given names apart from the family names."""
    form, words = OLDER_ROLE_FORMS[layout]
    families = names_of(people, "family", seed + 11)
    taken = set(families)
    given = [one for one in names_of(OLDER_ROLE_GIVEN + 60, "family", seed + 12) if one not in taken][:OLDER_ROLE_GIVEN]
    contacts: "list[str]" = []
    names: "dict[str, bool]" = dict.fromkeys(families, True)
    for place, family in enumerate(families):
        first = given[place % len(given)]
        contacts += [form.format(f=family, g=first, w=words[place % len(words)])]
        if "{g}" in form:
            names[first] = True
            names[f"{first} {family}"] = True
    return contacts, list(names)


def _many_rows_cells(seed: int) -> "list[str]":
    """The many-rows layout (73,000 rows): 2,800 names written `Family, Given` on 25 rows each and 3,000 more people written once in small letters, shuffled."""
    made = names_of(MANY_ROWS_NAMES + MANY_ROWS_SMALL, "comma", seed + 6)
    cells = [one for one in made[:MANY_ROWS_NAMES] for _row in range(MANY_ROWS_EACH)] + [
        one.lower() for one in made[MANY_ROWS_NAMES:]]
    random.Random(f"{seed}:many_rows").shuffle(cells)
    return cells


def _share_cells(layout: str, rows: int, seed: int) -> "list[str]":
    """The share at half (`share_half`: each person's name on 20 rows, one of them in small letters, 1,000 names and 1,000 small spellings) or past it (`share_beyond`: and the first `SHARE_BEYOND_SECOND` people once more in small letters with no space after the comma, 1,300 unread spellings)."""
    persons = _persons("alone", rows, seed)
    names = names_of(max(persons) + 1, "comma", seed)
    cells: "list[str]" = []
    lowered: "dict[int, int]" = {}
    for person in persons:
        times = lowered.get(person, 0)
        if times == 0:
            cells += [names[person].lower()]
        elif times == 1 and layout == "share_beyond" and person < SHARE_BEYOND_SECOND:
            cells += [names[person].lower().replace(", ", ",")]
        else:
            cells += [names[person]]
        lowered[person] = times + 1
    return cells


def _cycled_cells(seed: int) -> "list[str]":
    """The cycled layout (60,000 rows): every fourth row one of 1,400 names in small letters, cycled in row order; the others 3,000 names written `Family, Given` in a shuffled cycle (68.2 per cent of the different values names)."""
    made = names_of(CYCLED_NAMES + CYCLED_SMALL, "comma", seed + 4)
    whole, small = made[:CYCLED_NAMES], [one.lower() for one in made[CYCLED_NAMES:]]
    cycle = [whole[place % CYCLED_NAMES] for place in range(CYCLED_ROWS)]
    random.Random(f"{seed}:cycled").shuffle(cycle)
    cells: "list[str]" = []
    taken = lowered = 0
    for row in range(CYCLED_ROWS):
        if row % CYCLED_EVERY == 0:
            cells += [small[lowered % CYCLED_SMALL]]
            lowered += 1
        else:
            cells += [cycle[taken]]
            taken += 1
    return cells


def _frequency_cells(seed: int) -> "list[str]":
    """The frequency layout (110,200 rows): 4,200 names written `Family, Given` on 11 rows each and 640 codes on 100 rows each, shuffled (86.8 per cent of the different values names, 41.9 per cent of the cells)."""
    names = names_of(FREQUENCY_NAMES, "comma", seed + 5)
    codes = [f"code {place:04d}" for place in range(FREQUENCY_CODES)]
    cells = [one for one in names for _row in range(FREQUENCY_NAME_ROWS)] + [
        one for one in codes for _row in range(FREQUENCY_CODE_ROWS)]
    random.Random(f"{seed}:frequency").shuffle(cells)
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
    elif shape == "suffixes_more":
        # ...lane CZ-G-b's suffix words after a family name alone, and a
        # suffix with a degree after it (`Cedar Jr. MD`, `Cedar, Jr., MD`).
        written = [*SUFFIXES_MORE, "Jr. MD", "Sr. DO"]
        values = [f"{family} {written[place % len(written)]}" if place % 5 else f"{family}, Jr., MD"
                  for place, family in enumerate(families)]
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
    if layout in ("given_alone", "given_alone_small"):
        cells = given_alone_cells(rows, layout == "given_alone_small", seed)
        return [column], [[cell] for cell in cells], column, sorted(set(cells))
    if layout in ("era", "share_edge", "blocks"):
        cells = (_era_cells(seed) if layout == "era" else _share_edge_cells(rows, seed) if layout == "share_edge"
                 else _block_cells(seed))
        return [column], [[cell] for cell in cells], column, sorted(set(cells))
    if layout in ("share_half", "share_beyond", "cycled", "frequency", "many_rows"):
        cells = (_share_cells(layout, rows, seed) if layout.startswith("share_") else _cycled_cells(seed)
                 if layout == "cycled" else _many_rows_cells(seed) if layout == "many_rows" else _frequency_cells(seed))
        real = sorted({cell for cell in cells if not cell.startswith("code ")})
        return [column], [[cell] for cell in cells], column, real
    if layout == "crna_beside":
        # ...60 clinicians written with the degree after the name, one a row,
        # beside the patient each row belongs to (lane CZ-G-b's repair 1,
        # skeptic 1's item 1); the real names are the spellings and the
        # names without the degree.
        persons = _persons("alone", rows, seed)
        clinicians = names_of(CLINICIANS, "given_first", seed + 7)
        draw = random.Random(f"{seed}:{layout}")
        cells = [f"{clinicians[draw.randrange(CLINICIANS)]} {CRNA_DEGREE}" for _row in range(rows)]
        body = [[f"P{500000 + persons[row]}", cells[row]] for row in range(rows)]
        return [PERSON, column], body, column, sorted(set(cells) | set(clinicians))
    if layout in ("relation_no_mark", "relation_dash"):
        # ...push critic 24's B1 (a) and (c): each person's contact written
        # `Family Relation` or `Family-Relation`; the real names are the
        # spellings and the family names alone, as for `relation_beside`.
        persons = _persons("alone", rows, seed)
        families = names_of(max(persons) + 1, "family", seed + 9)
        mark = " " if layout == "relation_no_mark" else "-"
        contacts = [f"{family}{mark}{RELATIONS_TWELVE[place % len(RELATIONS_TWELVE)]}"
                    for place, family in enumerate(families)]
        cells = [contacts[person] for person in persons]
        body = [[f"C{700000 + row}", cells[row], f"Room {1 + row % 9}"] for row in range(rows)]
        return [CASE, column, "room"], body, column, sorted(set(cells) | set(families))
    if layout in OLDER_ROLE_FORMS:
        # ...batch 4t's fix round 5: each person's contact written with a word
        # of the older closed list of roles (`older_role_contacts`); the real
        # names are the spellings and the names they hold.
        persons = _persons("alone", rows, seed)
        contacts, held = older_role_contacts(layout, max(persons) + 1, seed)
        cells = [contacts[person] for person in persons]
        body = [[f"C{700000 + row}", cells[row], f"Room {1 + row % 9}"] for row in range(rows)]
        return [CASE, column, "room"], body, column, sorted(set(cells) | set(held))
    if layout == "surnames_kept_as_roles":
        # ...push critic 24's B1 (b): the 60 family names drawn row by row;
        # the real names are the 60.
        surnames = [*ROLE_WORD_SURNAMES, *names_of(ORDINARY_SURNAMES, "family", seed + 10)]
        draw = random.Random(f"{seed}:{layout}:rows")
        cells = [surnames[draw.randrange(len(surnames))] for _row in range(rows)]
        body = [[f"C{700000 + row}", cells[row], f"Room {1 + row % 9}"] for row in range(rows)]
        return [CASE, column, "room"], body, column, sorted(set(cells))
    if layout == "relation_beside":
        # ...an emergency contact for each of 1,000 people, on 20 rows each,
        # written `Family, Relation` beside a case number (lane CZ-G-b's
        # repair 2); the real names are the spellings and the family names
        # alone (three syllables at least, `names_of`'s `family`).
        persons = _persons("alone", rows, seed)
        families = names_of(max(persons) + 1, "family", seed + 8)
        contacts = [f"{family}, {RELATIONS[place % len(RELATIONS)]}" for place, family in enumerate(families)]
        cells = [contacts[person] for person in persons]
        body = [[f"C{700000 + row}", cells[row], f"Room {1 + row % 9}"] for row in range(rows)]
        return [CASE, column, "room"], body, column, sorted(set(cells) | set(families))
    if layout.startswith("control_"):
        # ...a heading's control: its 40 ordinary labels, no name among them,
        # beside a case number (lane CZ-G-b); its real names are none.
        group = {**STAFF_HEADINGS_ADDED, **STAFF_HEADINGS_LEFT}[column]
        labels = control_labels(group, seed)
        draw = random.Random(f"{seed}:{layout}")
        body = [[f"C{700000 + row}", labels[draw.randrange(len(labels))]] for row in range(rows)]
        return [CASE, column], body, column, []
    if layout in ("few_surname", "few_clinician", "few_run_together", "suffix_surname"):
        return _beside_a_case(layout, shape, rows, seed)
    persons = _persons(layout, rows, seed)
    names = names_of(max(persons) + 1, shape, seed)
    cells = [names[person] for person in persons]
    if layout == "beside":
        header = [PERSON, column]
        body = [[f"P{500000 + persons[row]}", cells[row]] for row in range(rows)]
    elif layout in ("clinician", "staff", "unlisted_role") or layout.startswith("role_"):
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


# The exit a generate run is given when it passes its bound of CPU seconds
# (`measure`'s ``generate_cpu_at_most``): the held writer's time cliff of
# STANDING NOTE ADDENDUM 2 (8), owner lane HB3-b, whose part a meters it.
GENERATE_STOPPED = -9


class _GenerateStopped(BaseException):
    """A generate run past its bound of CPU seconds."""


def _generate_within(arguments: "list[str]", refused: bool, seconds: "float | None") -> int:
    """Generate through the command, stopped after ``seconds`` of the process's CPU time where the platform has a profiling timer (`GENERATE_STOPPED`); unbounded where ``seconds`` is None."""
    from synthtwin import cli

    if not seconds or not hasattr(signal, "setitimer"):
        return cli.main(arguments, small_tables_refused=refused)

    def stop(_signum: int, _frame: object) -> None:
        raise _GenerateStopped()

    previous = signal.signal(signal.SIGPROF, stop)
    signal.setitimer(signal.ITIMER_PROF, seconds)
    try:
        return cli.main(arguments, small_tables_refused=refused)
    except _GenerateStopped:
        return GENERATE_STOPPED
    finally:
        signal.setitimer(signal.ITIMER_PROF, 0)
        signal.signal(signal.SIGPROF, previous)


def measure(
    folder: pathlib.Path, layout: str, shape: str, rows: int, mode: str = "unanswered", seed: int = SEED,
    small_tables_refused: "bool | None" = None, generate_cpu_at_most: "float | None" = None,
) -> "dict[str, object]":
    """One table through profile (and its rounds of answers), generate at seed 0 and validate, counted (`counted`).

    The commands a person types (`cli.main`), nobody at the keyboard, the
    table floor on at 20,000 rows or more unless ``small_tables_refused``
    says otherwise. Returns the exit codes, the names column's role at
    the first and the last description, the questions put to it, the
    counts and the product's own seconds apart from the counting. With
    ``generate_cpu_at_most`` (lane CZ-G-b), generate is stopped after that
    many seconds of the process's CPU time and its exit is
    `GENERATE_STOPPED`: no twin is read then, and the description, the
    questions and the screen are still counted.
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
            generated = _generate_within(["generate", f"{profile}", "--replace", "--seed", "0"], refused,
                                         generate_cpu_at_most)
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


def price_table(folder: pathlib.Path, family: str, rows: int, seed: int = SEED) -> "dict[str, object]":
    """ONE PRICE FAMILY (`PRICE_FAMILIES`) through the first profile run a person types, nobody answering, the table floor on at 20,000 rows or more: a case number and each label column of `price_columns`, each row a label drawn per column; returns the exit, each column's role and the questions put to it, and which columns publish nothing (held: a false alarm where no name is among them). Generate is not run: whether a column is held is the description's (the held writer's time cliff of STANDING NOTE ADDENDUM 2 (8) aside)."""
    import unanswered_identifier_shapes as shapes
    from synthtwin import cli

    columns = price_columns(family, seed)
    draw = random.Random(f"{seed}:{family}:rows")
    header = [CASE, *columns]
    body = [[f"C{700000 + row}", *(labels[draw.randrange(len(labels))] for labels in columns.values())]
            for row in range(rows)]
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / "names.csv"
    source.write_bytes(zoo.csv_bytes(header, body))
    screen = io.StringIO()
    started = time.perf_counter()
    with shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        code = cli.main(["profile", f"{source}", "--replace"], small_tables_refused=rows >= zoo.KPI_ROWS)
    found: "dict[str, object]" = {"family": family, "rows": rows, "profile": code, "columns": len(columns),
                                  "product_seconds": round(time.perf_counter() - started, 1)}
    if code != 0:
        found["screen"] = screen.getvalue()[-400:]
        return found
    roles = {f"{block.get('name')}": f"{block.get('role')}"
             for block in json.loads((folder / "names-profile.json").read_text(encoding="utf-8"))["columns"]}
    asked: "dict[str, list[str]]" = {}
    for entry in zoo._entries(json.loads((folder / "names-questions.json").read_text(encoding="utf-8"))):
        name = f"{entry.get('column', '')}"
        asked.setdefault(name, [])
        asked[name] += ["/".join(sorted(zoo._offered(entry)))]
    found["roles"] = {name: roles.get(name, "") for name in columns}
    found["asked"] = {name: asked.get(name, []) for name in columns}
    found["held"] = sorted(name for name in columns if roles.get(name, "") in PUBLISHING_NOTHING)
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
