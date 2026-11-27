"""Gate file of lane TEXTZONE: a person's details reach the twin in their real layouts, made up, and never real.

WHY. Release 36 closed a leak (lane LEDGER): the inside record's text zone wrote street addresses, e-mail addresses
and record numbers in their real templates, every word the floor's people write kept and every number drawn inside
the real ends, and 1,548 real addresses and 72 real e-mail addresses stood in the zoo's twin. It closed it by leaving
such a column the description's filler, so code parsing an address, an e-mail, a telephone number, a web address or a
record number holding a key found nothing (the type battery fell from 113 to 110 of 147).

WHAT IT HOLDS (each clause red on its mutant):

* a column of a person's details (`inside_text.MODE_DETAIL`) keeps every value's length and the column's count of
  different values, wears its real layout -- a house number, a street word and its suffix; `(NNN) NNN-NNNN`; a name, a
  dot, a name and figures at a domain; a chart link under its reserved host; a person key and a line number -- and
  holds no real value (mutant: the exact length not asked for);
* every word that could name somebody is made up: no street word, given or family name, mail domain or host label of
  the twin is a word of the real column (mutants: the floor's words kept as TYPES-24 kept them; the made-up words not
  screened against the real column's; the host and mail domain not told apart);
* a telephone number's area code and exchange are none a real number of the column holds, whatever its template
  (mutants: the telephone templates not read; their parts not pooled over the column's telephone templates), each
  area code left taken about evenly (mutant: the first one after a drawn start taken);
* a long run of figures opens with a figure no real run of its width opens with (mutant: the opening not moved);
* a run of figures standing as a word of its own (a house number read as a record number) never takes a nought as
  its mark (mutant: the rule withdrawn);
* a record number the description's twin wrote in a real layout keeps that layout, so a published layout's count
  stands (mutant: every value dealt by budget);
* a key of figures alone whose every opening figure is a real key's keeps its width, holds no real key read as a
  number and opens with no nought (mutant: the absent numbers not kept).
"""

from __future__ import annotations

import collections
import random
import re

from synthtwin import inside_text

ROWS = 20000
STREETS = ("Cedar", "Maple", "Walnut", "Birch", "Elm", "Oak", "Juniper", "Harbor", "Quartz", "Ember")
SUFFIXES = ("St", "Ave", "Rd")
GIVEN = ("anna", "ben", "carla", "dev", "elif", "farah", "gus", "hana", "ivo", "jun", "kemal", "lior", "mona")
FAMILY = ("okoro", "lindqvist", "tanaka", "moreau", "silva", "novak", "haddad", "petrova", "walsh", "iyer")


def _people(draw: random.Random) -> "list[str]":
    return [f"P{4000000 + draw.randrange(ROWS // 4):07d}" for _ in range(ROWS)]


def _columns() -> "dict[str, list[str]]":
    draw = random.Random(11)
    people = _people(draw)
    return {
        "street_address": [f"{draw.randint(1, 9999)} {draw.choice(STREETS)} {draw.choice(SUFFIXES)}"
                           for _ in range(ROWS)],
        # ...area codes over most of the range, line numbers a tenth of which open with a nought (two templates).
        "phone": [f"({draw.randint(201, 989)}) {draw.choice((335, 353, 356, 384))}-{draw.randint(0, 9999):04d}"
                  for _ in range(ROWS)],
        # ...an employer's mail domain most rows write (a domain names an employer: made up all the same).
        "email": [f"{draw.choice(GIVEN)}.{draw.choice(FAMILY)}{draw.randint(1, 99)}@"
                  f"{draw.choices(('acmeworks', 'northvale'), (7, 3))[0]}.com" for _ in range(ROWS)],
        "full_name": [f"{draw.choice(GIVEN).title()} {draw.choice(FAMILY).title()}" for _ in range(ROWS)],
        "chart_url": [f"https://records.example.org/chart/{person}/{draw.randint(100000, 999999)}"
                      for person in people],
        "visit_line": [f"{person}-{draw.randint(1, 12):02d}" for person in people],
    }


LAYOUTS = {
    "street_address": r"\d{1,4} [A-Z][a-z]+ (St|Ave|Rd)",
    "phone": r"\(\d{3}\) \d{3}-\d{4}",
    "email": r"[a-z]+\.[a-z]+\d{1,2}@[a-z]+\.com",
    "full_name": r"[A-Z][a-z]+ [A-Z][a-z]+",
    "chart_url": r"https://records\.example\.org/chart/P\d{7}/\d{6}",
    "visit_line": r"P\d{7}-\d{2}",
}
LAYOUT_WORDS = {"st", "ave", "rd", "com", "https", "records", "example", "org", "chart", "p"}


def _stand_in(cells: "list[str]") -> "list[str]":
    """The description's twin of a free-text column, in miniature: one made-up value a real value, as long as it, no
    layout at all (the filler release 36 left), the same rows sharing one."""
    names: "dict[str, str]" = {}
    for cell in cells:
        if cell not in names:
            tag = f"{len(names) + 1}"
            names[cell] = ("!" * max(0, len(cell) - len(tag))) + tag
    return [names[cell] for cell in cells]


def _written(name: str, cells: "list[str]") -> "tuple[list[str], list[str]]":
    persons = [row // 4 for row in range(len(cells))]
    entry = inside_text.entry_of(cells, inside_text.MODE_DETAIL, [], persons, 11)
    assert entry is not None, name
    stand_in = _stand_in(cells)
    written = inside_text.write_column(inside_text.zone_of({name: entry}), name, stand_in, 7)
    assert written is not None, name
    return stand_in, written


def _words(cells: "list[str]") -> "set[str]":
    found: "set[str]" = set()
    for cell in cells:
        found |= {word.lower() for word in re.findall(r"[A-Za-z]+", cell)}
    return found


def test_a_persons_details_wear_their_layouts_made_up_and_never_real() -> None:
    for name, real in _columns().items():
        stand_in, twin = _written(name, real)
        # No real value; each value as long as the description's, as many different values, the same rows sharing one.
        assert not set(twin) & set(real), name
        assert [len(cell) for cell in twin] == [len(cell) for cell in stand_in], name
        assert len(set(twin)) == len(set(stand_in)), name
        # The real layout, on every cell.
        pattern = re.compile(LAYOUTS[name])
        misfits = [cell for cell in twin if not pattern.fullmatch(cell)]
        assert not misfits, (name, misfits[:5])
        # Every word that could name somebody is made up: none of the twin's words is the real column's, beyond the
        # layout's own (a suffix, a scheme, the reserved host, `chart`, the key's letter).
        shared = (_words(twin) & _words(real)) - LAYOUT_WORDS
        assert not shared, (name, sorted(shared)[:8])


def test_a_telephone_numbers_area_code_and_exchange_are_no_real_ones() -> None:
    real = _columns()["phone"]
    _stand, twin = _written("phone", real)
    codes = {cell[1:4] for cell in real}
    exchanges = {cell[6:9] for cell in real}
    assert not {cell[1:4] for cell in twin} & codes
    assert not {cell[6:9] for cell in twin} & exchanges
    assert all(cell[1:2] not in "01" and cell[6:7] not in "01" and cell[2:4] != "11" for cell in twin)
    # ...each area code left taken, and about evenly (no one code the scan after the longest real run lands on).
    free = {f"{code}" for code in range(200, 1000) if f"{code}" not in codes and code % 100 != 11}
    taken = collections.Counter(cell[1:4] for cell in twin)
    assert set(taken) == free, (sorted(taken), sorted(free))
    assert max(taken.values()) <= 2 * len(twin) // len(free), taken.most_common(3)


def test_a_long_run_opens_off_every_real_run_of_its_width() -> None:
    real = _columns()["chart_url"]
    _stand, twin = _written("chart_url", real)
    openings = {cell.split("/")[4][1:2] for cell in real}
    assert not [cell for cell in twin if cell.split("/")[4][1:2] in openings]


def test_a_key_of_figures_alone_keeps_its_width_and_no_real_number() -> None:
    draw = random.Random(4)
    # The zoo's encounter numbers: ten a patient plus one to three, so every opening figure of the widths 2 to 4 is
    # a real key's (no mark keeps them off the real; release 36 wrote them all five figures wide).
    real = [f"{10 * draw.randrange(5000) + draw.randint(1, 3)}" for _ in range(ROWS)]
    names: "dict[str, str]" = {}
    for cell in real:
        names.setdefault(cell, f"Z{len(names) + 1:04d}")
    stand_in = [names[cell] for cell in real]
    entry = inside_text.entry_of(real, inside_text.MODE_IDENTIFIER, [], [int(cell) // 10 for cell in real], 11)
    assert entry is not None
    twin = inside_text.write_column(inside_text.zone_of({"c": entry}), "c", stand_in, 7)
    assert twin is not None
    numbers = {int(cell) for cell in real}
    assert not [cell for cell in twin if int(cell) in numbers]
    assert not [cell for cell in twin if len(cell) > 1 and cell.startswith("0")]
    real_widths = collections.Counter(len(cell) for cell in real)
    twin_widths = collections.Counter(len(cell) for cell in twin)
    # Each width the floor's people hold keeps its rows, to within one per cent of the table.
    for width in (3, 4, 5):
        assert abs(twin_widths[width] - real_widths[width]) <= ROWS // 100, (width, real_widths, twin_widths)


def test_a_house_number_read_as_a_record_number_never_takes_a_nought() -> None:
    """A column of addresses read as record numbers (`MODE_IDENTIFIER`): a run of figures standing as a word of its
    own takes no nought as its mark, for `0567 River Ave` is the real `567 River Ave` (mutant: the rule withdrawn)."""
    real = _columns()["street_address"]
    entry = inside_text.entry_of(real, inside_text.MODE_IDENTIFIER, [], [row // 4 for row in range(ROWS)], 11)
    assert entry is not None
    twin = inside_text.write_column(inside_text.zone_of({"c": entry}), "c", _stand_in(real), 7) or _stand_in(real)
    held = set(real)
    assert not [cell for cell in twin if cell in held or cell.lstrip("0") in held]


def test_the_made_up_words_are_everyday_words_and_nothing_else() -> None:
    """`NEUTRAL_WORDS`: small ASCII letters, each once, three letters or more, and none a word the column's layout keeps,
    a month, a telephone's, a title's or a relative's word, or a spelling of missing (mutant: a suffix added)."""
    from synthtwin import date_counts, parsing, taxonomy

    words = inside_text.NEUTRAL_WORDS
    assert len(words) == len(set(words)) and len(words) >= 500
    for word in words:
        assert re.fullmatch(r"[a-z]{3,}", word), word
        assert word not in inside_text.DETAIL_VOCABULARY and word not in inside_text.RESERVED_TOP, word
        assert not date_counts.month_word(word), word
        assert word not in taxonomy.TELEPHONE_WORDS | taxonomy.NAME_TITLES | taxonomy.RELATIVE_WORDS, word
        assert not parsing.is_missing_text(word), word
    # Every length a made-up word is drawn at from three to ten letters has a dozen words or more.
    lengths = collections.Counter(len(word) for word in words)
    assert all(lengths[size] >= 12 for size in range(3, 11)), lengths


def test_a_telephone_column_using_every_exchange_keeps_its_layout() -> None:
    """Where every exchange from 200 to 999 is a real number's, none is left to make up: the exchange is drawn as the
    slot's own number, the area code still none a real number holds, and every cell still wears the layout at its
    length (mutant: the empty choice written as nothing)."""
    draw = random.Random(12)
    real = [f"({draw.randint(201, 989)}) {200 + row % 800}-{draw.randint(0, 9999):04d}" for row in range(ROWS)]
    stand_in, twin = _written("phone", real)
    assert [len(cell) for cell in twin] == [len(cell) for cell in stand_in]
    assert all(re.fullmatch(LAYOUTS["phone"], cell) for cell in twin)
    assert not {cell[1:4] for cell in twin} & {cell[1:4] for cell in real}
    assert not set(twin) & set(real)


def test_a_key_the_descriptions_twin_wrote_in_a_real_layout_keeps_that_layout() -> None:
    """The description's twin holds each published layout's count exactly: its five-figure keys stay five figures, and
    the keys it wrote wider than every real one take the narrower templates (mutant: every value dealt by budget)."""
    draw = random.Random(4)
    real = [f"{10 * draw.randrange(5000) + draw.randint(1, 3)}" for _ in range(ROWS)]
    names: "dict[str, str]" = {}
    for cell in real:
        if cell not in names:
            names[cell] = f"{50000 + len(names)}" if len(cell) == 5 else f"{900000 + len(names)}"
    stand_in = [names[cell] for cell in real]
    entry = inside_text.entry_of(real, inside_text.MODE_IDENTIFIER, [], [int(cell) // 10 for cell in real], 11)
    assert entry is not None
    twin = inside_text.write_column(inside_text.zone_of({"c": entry}), "c", stand_in, 7)
    assert twin is not None
    assert sum(1 for cell in twin if len(cell) == 5) == sum(1 for cell in stand_in if len(cell) == 5)
    assert not [cell for cell in twin if len(cell) > 5]
    numbers = {int(cell) for cell in real}
    assert not [cell for cell in twin if int(cell) in numbers]
