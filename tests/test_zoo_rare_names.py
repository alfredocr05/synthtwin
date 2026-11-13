"""THE GATE OF LANE CODES-2 (plan P4-D471): rare values of category and code columns written as real vocabulary.

The owner's answer Z1 = B (2026-10-16): a value fewer rows than the floor
hold is published by its NAME, never its count or its rows, beside the
pooled total ruling 2 already prints, and only on three paths -- (i) a
column the person declared a code AND answered `no` to its Safe Harbor
question; (ii) the words of a column of numbers with labels that pass the
word screen, a word holding a figure only after `no` (the stand-ins page's
ZS.3 (ii); the orchestrator's LANE CODES-2 RULINGS 3 (1)); (iii) any other
label column answered `no` to that question. Unanswered, path (i) and path
(iii) name nothing; `yes` holds the column. HIPAA FIRST: the gate's first
cases sweep every Safe Harbor class of 45 CFR 164.514(b)(2)(i) over
generated spellings on every path, and the families of words a column of
numbers with labels may hold (records, masked numbers, dates without a day
or a year, weeks, clocks, ages with a mark or a word, initials, web and
e-mail addresses), thousands of spellings, each rule red on its mutant;
then rule U (c) through the describe, the twin writes the names, the
validator judges the pool, the loader refuses a named pool that does not
add up, the oracle mirrors the writer, and ONE case at the owner's table
floor (20,000 rows) runs the commands a person types. Every table here is
an invented look-alike with generic names.
"""

import collections
import contextlib
import csv
import dataclasses
import io
import json
import pathlib
import random
import sys
import types

import pytest

import fixtures
from synthtwin import cli, contract, generation, parsing, profile, reading, taxonomy

ROOT = pathlib.Path(__file__).resolve().parents[1]
FLOOR = 11
SETTINGS = taxonomy.Settings(small_cell_floor=FLOOR)


# -- the Safe Harbor classes, generated ---------------------------------------

_SYLLABLES = ("bram", "cor", "dal", "fen", "gar", "hol", "kel", "lor", "mar", "nor", "pel", "quin", "ros",
              "sal", "tam", "vel", "wyn", "zor")
_ENDS = ("wick", "ton", "ley", "dane", "ford", "mere", "by", "stead", "well", "ham")


def _word(draw: random.Random) -> str:
    return (draw.choice(_SYLLABLES) + draw.choice(_SYLLABLES) + draw.choice(_ENDS)).capitalize()


def _spelling(kind: str, draw: random.Random) -> str:
    """One invented spelling of one Safe Harbor class (45 CFR 164.514(b)(2)(i), (A) to (R))."""
    figures = lambda count: "".join(draw.choice("0123456789") for _ in range(count))  # noqa: E731
    letters = lambda count: "".join(draw.choice("ABCDEFGHJKLMNPRSTUVWXYZ") for _ in range(count))  # noqa: E731
    if kind == "surname":
        return _word(draw)
    if kind == "full name":
        return f"{_word(draw)}, {_word(draw)}"
    if kind == "street address":
        return f"{draw.randint(10, 9999)} {_word(draw)} {draw.choice(('St', 'Ave', 'Rd', 'Lane'))}"
    if kind == "city":
        return f"{_word(draw)}{draw.choice(('ville', ' Ford', 'port', ' City'))}"
    if kind == "county":
        return f"{_word(draw)} County"
    if kind == "zip code":
        return figures(5)
    if kind == "birth date":
        return f"{draw.randint(1, 12):02d}/{draw.randint(1, 28):02d}/{draw.randint(1930, 2020)}"
    if kind == "date as words":
        return f"{draw.choice(('Jan', 'Mar', 'Jun', 'Sep', 'Nov'))} {draw.randint(1, 28)} {draw.randint(1930, 2020)}"
    if kind == "age over 89":
        return f"{draw.randint(90, 125)}{draw.choice(('', ' years', ' yrs', ' y'))}"
    if kind == "telephone":
        return f"({figures(3)}) {figures(3)}-{figures(4)}"
    if kind == "fax":
        return f"+1 {figures(3)} {figures(3)} {figures(4)}"
    if kind == "e-mail":
        return f"{_word(draw).lower()}.{_word(draw).lower()}@example.org"
    if kind == "social security":
        return f"{figures(3)}-{figures(2)}-{figures(4)}"
    if kind == "record number":
        return f"REC{figures(7)}"
    if kind == "plan number":
        return f"HP{letters(2)}{figures(8)}"
    if kind == "account number":
        return f"ACCT-{figures(8)}"
    if kind == "licence number":
        return f"LIC-{letters(2)}-{figures(6)}"
    if kind == "vehicle number":
        return f"{letters(3)}{figures(14)}"
    if kind == "device serial":
        return f"(01){figures(14)}(21){letters(2)}{figures(5)}"
    if kind == "web address":
        return f"https://www.example.org/p/{figures(6)}"
    if kind == "internet address":
        return f"{draw.randint(1, 254)}.{draw.randint(0, 254)}.{draw.randint(0, 254)}.{draw.randint(1, 254)}"
    if kind == "biometric reference":
        return "".join(draw.choice("0123456789abcdef") for _ in range(32))
    if kind == "other unique number":
        return f"ID{figures(9)}"
    raise KeyError(kind)


# The classes whose spellings no shape tells from a word: under `no` the
# person's answer names them, as the owner's answer Z1 = B says; under the
# word screen of path (ii) a lone name is the stated residual.
UNSHAPED = ("surname", "full name", "city", "county")
SHAPED = (
    "street address", "zip code", "birth date", "date as words", "age over 89", "telephone", "fax", "e-mail",
    "social security", "record number", "plan number", "account number", "licence number", "vehicle number",
    "device serial", "web address", "internet address", "biometric reference", "other unique number",
)
CLASSES = UNSHAPED + SHAPED
SWEEP_SPELLINGS = 160


def _rare_column(kind: str, seed: int, spellings: int = SWEEP_SPELLINGS) -> "list[str]":
    """Five common levels of 300 rows each beside ``spellings`` rare ones of one class, one to three rows each."""
    draw = random.Random(seed)
    cells: "list[str]" = []
    for common in ("Alpha group", "Beta group", "Gamma group", "Delta group", "Omega group"):
        cells += [common] * 300
    made: "dict[str, bool]" = {}
    for _attempt in range(50 * spellings):
        if len(made) >= spellings:
            break
        value = _spelling(kind, draw)
        if value.strip() and value not in made:
            made[value] = True
    for place, value in enumerate(sorted(made)):
        cells += [value] * (1 + place % 3)
    return cells


def _described(cells: "list[str]", how: str, code: bool = False) -> taxonomy.ColumnProfile:
    return taxonomy.profile_column(
        "column", 1, cells, len(cells), dataclasses.replace(SETTINGS, held_back_named=how), False, code
    )


def _held(described: taxonomy.ColumnProfile) -> int:
    """How many levels the column holds back, its label half's where it has one."""
    details = described.details
    half = details["labels"] if "labels" in details else details
    return int(half["suppressed_levels"])  # type: ignore[index, call-overload]


def _names(described: taxonomy.ColumnProfile) -> "list[str]":
    details = described.details
    if "held_back_names" in details:
        return list(details["held_back_names"])  # type: ignore[call-overload]
    half = details["labels"] if "labels" in details else {}
    if isinstance(half, dict) and "held_back_names" in half:
        return list(half["held_back_names"])
    return []


@contextlib.contextmanager
def _mutant(target: object, name: str, replacement: object) -> "object":
    """One mutant in force for the block: a name of a module replaced, restored after."""
    kept = getattr(target, name)
    setattr(target, name, replacement)
    try:
        yield
    finally:
        setattr(target, name, kept)


def _red(case: "object", target: object, name: str, replacement: object) -> None:
    """The case holds on the product and fails on its mutant."""
    case()  # type: ignore[operator]
    with _mutant(target, name, replacement), pytest.raises(AssertionError):
        case()  # type: ignore[operator]


def _red_together(case: "object", target: object, replacements: "dict[str, object]") -> None:
    """The case holds on the product and fails once SEVERAL rules that each refuse the same spellings are gone."""
    case()  # type: ignore[operator]
    with contextlib.ExitStack() as stack:
        for name, replacement in replacements.items():
            stack.enter_context(_mutant(target, name, replacement))  # type: ignore[arg-type]
        with pytest.raises(AssertionError):
            case()  # type: ignore[operator]


_REAL_NAMES_UNDER = taxonomy._names_under


def _names_whatever_the_road(how: str, names: "tuple[str, ...]", comma: bool, total: bool, code: bool) -> "tuple[str, ...]":
    """MUTANT: every road names the pool, answered or not."""
    return names if how else ()


def _the_builds_names_under(how: str, names: "tuple[str, ...]", comma: bool, total: bool, code: bool) -> "tuple[str, ...]":
    """MUTANT (skeptic 1's item 1): path (ii) as the lane's build wrote it, a word holding a figure named by the screen alone."""
    if how == taxonomy.HELD_BACK_NAMED_SCREENED and not total:
        return names if all(taxonomy.passes_the_word_screen(name) for name in names) else ()
    return _REAL_NAMES_UNDER(how, names, comma, total, code)


# -- the words a column of numbers with labels may hold, generated -------------
#
# Lane CODES-2's repair 1 (skeptic 1's items 1 and 6, the statistics
# skeptic's items 1 and 2, the orchestrator's LANE CODES-2 RULINGS 2 (1) and
# 3 (1)): each family is spelled many ways, and each lands where the
# stand-ins page's ZS.3 (ii) puts it. AFTER `no`: words of figures and marks
# the screen passes, named only after the person's `no`. NEVER: words the
# screen refuses, so a column holding one names none of its words even
# after `no`. LIMIT (a): words of letters and marks alone, which no shape
# tells from a result word -- named by the screen with no question, the
# stated limit of P4-D471, counted by K-HZ-24 apart.

AFTER_NO = ("short record", "masked number", "ratio or range")
NEVER = (
    "record beside letters", "age with a word", "age with more", "month and day", "month and year", "week",
    "clock", "initials", "web address", "e-mail or host with a path", "internet address v6", "masked identifier",
    "age with a mark",
)
LIMIT_A = ("name or place in letters", "bare host")
# ...and lane CODES-2's repair 2 (Codex's item 1; the verify of repair 1,
# items 3 and 7), appended so every family before keeps its seed: a record
# in another script's figures, named only after `no`; a note joined by
# spaces other than ASCII's, an age past 89 and a date in words, never.
REPAIR_2_AFTER_NO = ("record in another script",)
REPAIR_2_NEVER = ("note joined by other spaces", "age in words", "date in words")
# ...and lane CODES-2's follow-up (the verify of repair 2, items 1, 2 and 4;
# the orchestrator's LANE CODES-2 RULINGS 8 (2), (3) and (5)), appended so
# every family before keeps its seed: one character that prints nothing
# inside a word or a number of a refused shape, number words glued into one,
# and the neighbour families built (P4-D471) -- never named on path (ii), and
# refused after `no` by path (iii)'s net and path (i)'s screen too.
FOLLOW_UP_NEVER = (
    "nothing printed inside a number word", "nothing printed inside a month's name",
    "nothing printed inside a marked age", "nothing printed inside a clock", "number words glued into one",
    "month beside a day in figures", "about-word glued to an age", "decade past 89", "age with its marks apart",
)
WORD_FAMILIES = AFTER_NO + NEVER + LIMIT_A + REPAIR_2_AFTER_NO + REPAIR_2_NEVER + FOLLOW_UP_NEVER
WORD_SWEEP = 300
# The spaces a cell of a written table may hold inside it (no line break): the
# K-HZ-24 tables carry them through the command.
_SPACES_INSIDE_A_CELL = "\xa0\u1680" + "".join(chr(code) for code in range(0x2000, 0x2010)) + "\u202f\u205f\u2060\u3000\ufeff"
_SCRIPT_ZEROS = (0x0660, 0x06F0, 0x0966, 0x09E6, 0x0E50, 0xFF10)


def _printing_nothing() -> "list[str]":
    """Every character that prints nothing, as this Python reads them: each format character and each control that is not whitespace, every plane."""
    import unicodedata

    found: "list[str]" = []
    for code in range(0x110000):
        character = chr(code)
        kind = unicodedata.category(character)
        if kind == "Cf" or (kind == "Cc" and not character.isspace()):
            found += [character]
    return found


# ...of which a cell of a written table carries all but the null (the K-HZ-24
# tables and the case at the floor carry them through the command).
_NOTHING_PRINTED_IN_A_CELL = tuple(character for character in _printing_nothing() if character != "\x00")
_GLUED_TENS = ("ninety", "Ninety", "NINETY", "onehundred", "OneHundred", "hundred", "Hundred", "thousand")
_GLUED_ONES = ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
_ORDINAL_ENDS = {1: "st", 2: "nd", 3: "rd", 21: "st", 22: "nd", 23: "rd", 31: "st"}


def _inside_letters(word: str, mark: str, draw: random.Random) -> str:
    """``mark`` inside a run of three letters or more of ``word``, never at the run's ends."""
    runs: "list[tuple[int, int]]" = []
    start = -1
    for place, character in enumerate(word + " "):
        letter = "a" <= character.lower() <= "z"
        if letter and start < 0:
            start = place
        elif not letter and start >= 0:
            if place - start >= 3:
                runs += [(start, place)]
            start = -1
    first, end = draw.choice(runs)
    cut = draw.randint(first + 1, end - 1)
    return word[:cut] + mark + word[cut:]


def _inside_figures(word: str, mark: str, draw: random.Random, beside_marks: bool = False) -> str:
    """``mark`` between two figures of ``word`` (or, ``beside_marks``, between a figure and a mark)."""
    places = [place for place in range(1, len(word)) if (word[place].isdigit() and word[place - 1].isdigit())
              or (beside_marks and word[place].isdigit() != word[place - 1].isdigit())]
    cut = draw.choice(places)
    return word[:cut] + mark + word[cut:]


def _word_spelling(family: str, draw: random.Random) -> str:
    """One invented spelling of one family of words a column of numbers with labels may hold."""
    figures = lambda count: "".join(draw.choice("0123456789") for _ in range(count))  # noqa: E731
    letters = lambda count: "".join(draw.choice("ABCDEFGHJKLMNPRSTUVWXYZ") for _ in range(count))  # noqa: E731
    age = draw.randint(90, 125)
    month = draw.randint(1, 12)
    day = draw.randint(13, 31)
    year = draw.randint(1900, 2030)
    name = _word(draw)
    if family == "short record":
        return draw.choice((
            f"#{figures(draw.randint(1, 4))}", f"{figures(2)}-{figures(3)}", f"{draw.randint(3, 9)}{figures(3)}/{draw.randint(1, 9)}",
            f"#{figures(2)}-{figures(2)}", f"{figures(3)}-{figures(3)}",
        ))
    if family == "masked number":
        return draw.choice((f"***-{figures(4)}", f"**-**-{figures(2)}", f"#-##-{figures(3)}"))
    if family == "masked identifier":
        # Rule (8)'s shapes (LANE CODES-2 RULINGS 4 (3)): refused even after `no`.
        return draw.choice((
            f"***-**-{figures(4)}", f"XXX-XX-{figures(4)}", f"SSN {figures(4)}", f"{figures(3)}**", f"{figures(3)}xx",
            f"face_{figures(4)}.jpg", f"IMG_{figures(4)}.JPG",
        ))
    if family == "age with a mark":
        return draw.choice((f"~{age}", f"{age}?", f"~ {age}", f"≈{age}", f"c. {age}"))
    if family == "ratio or range":
        low = draw.randint(1, 11)
        return draw.choice((
            f"{draw.randint(100, 200)}/{draw.randint(40, 120)}", f"1:{draw.choice((2, 4, 8, 16, 40, 80, 160, 320, 640))}",
            f"{low}-{draw.randint(low + 1, 12)}",
        ))
    if family == "record beside letters":
        return draw.choice((
            f"REC {figures(draw.randint(1, 4))}", f"{letters(draw.randint(1, 3))}{figures(draw.randint(2, 4))}",
            f"{letters(1)}{figures(2)}-{figures(4)}", f"XXX-XX-{figures(4)}", f"{letters(2)}-{figures(4)}",
            f"{letters(1)}{figures(1)}{letters(1)} {figures(1)}{letters(1)}{figures(1)}", f"#{letters(2)}{figures(4)}",
        ))
    if family == "age with a word":
        unit = draw.choice(sorted(taxonomy.AGE_UNIT_WORDS))
        return draw.choice((
            f"{age} est", f"{age} (est)", f"approx {age}", f"aged {age}", f"age {age}", f"{age} {unit}", f"{age}{unit}",
        ))
    if family == "age with more":
        return draw.choice((f"{age}+", f">{age}", f"≥{age}", f"+{age}"))
    if family == "month and day":
        return draw.choice((
            f"{month:02d}-{day}", f"{day}-{month:02d}", f"{day}.{month:02d}", f"{day}/{month}", f"{month}/{draw.randint(1, 31)}",
            f"{month:02d}/{draw.randint(1, 31):02d}",
        ))
    if family == "month and year":
        return draw.choice((f"{year}-{month:02d}", f"{month:02d}/{year}", f"{month}.{year}", f"{year}/{month:02d}", f"{month}-{year}"))
    if family == "week":
        week = draw.randint(1, 53)
        return draw.choice((f"{year}-W{week:02d}", f"{year}W{week:02d}", f"W{week}-{year}", f"{year}-W{week:02d}-{draw.randint(1, 7)}"))
    if family == "clock":
        return draw.choice((
            f"{draw.randint(0, 23):02d}:{draw.randint(0, 59):02d}",
            f"{draw.randint(0, 23):02d}:{draw.randint(0, 59):02d}:{draw.randint(0, 59):02d}",
            f"{draw.randint(1, 12)}:{draw.randint(0, 59):02d}{draw.choice(('am', 'pm', 'AM', 'PM'))}",
            f"{draw.randint(1, 12)}{draw.choice(('am', 'pm'))}",
        ))
    if family == "initials":
        return draw.choice((f"{letters(1)}.{letters(1)}.", f"{letters(1)}. {name}", f"{letters(1)}.{letters(1)}.{letters(1)}."))
    if family == "web address":
        return draw.choice((f"www.{name.lower()}.org", f"https://{name.lower()}.example.org", f"http://{name.lower()}.org/p"))
    if family == "e-mail or host with a path":
        other = _word(draw).lower()
        return draw.choice((
            f"{name.lower()}(at){other}.org", f"{name.lower()}[at]{other}.com", f"{name.lower()}.org/{other}",
            f"{name.lower()}@{other}.org",
        ))
    if family == "internet address v6":
        hexes = lambda: "".join(draw.choice("0123456789abcdef") for _ in range(draw.randint(1, 4)))  # noqa: E731
        return draw.choice((f"fe80::{hexes()}", f"{hexes()}:{hexes()}:{hexes()}:{hexes()}", f"2001:db8::{hexes()}"))
    if family == "name or place in letters":
        return draw.choice((f"Dr {name}", f"{name} RN", f"per {name}", f"{name} County", f"{name} Street", name))
    if family == "bare host":
        return draw.choice((f"{name.lower()}.org", f"{name.lower()}.com"))
    if family == "record in another script":
        zero = draw.choice(_SCRIPT_ZEROS)
        record = draw.choice((f"#{figures(4)}", f"{figures(2)}-{figures(3)}", f"#{figures(2)}-{figures(2)}"))
        return "".join(chr(zero + int(mark)) if "0" <= mark <= "9" else mark for mark in record)
    if family == "note joined by other spaces":
        words = draw.sample(("Called", "patient", "spoke", "with", "left", "message", "daughter", "nurse", name), 4)
        return draw.choice(_SPACES_INSIDE_A_CELL).join(words)
    if family == "age in words":
        return (f"{draw.choice(('ninety', 'Ninety', 'one hundred', 'hundred', 'a hundred'))}"
                f"{draw.choice(('', '-one', '-two', '-five', '-nine', ' and one'))}{draw.choice(('', '+', '?', ' plus'))}")
    if family == "date in words":
        month = draw.choice(("January", "March", "April", "May", "June", "August", "October", "December"))
        day = draw.choice(("first", "second", "fifth", "twelfth", "twenty-first", "thirtieth"))
        return draw.choice((month, f"{month} {day}", f"{day} of {month}", f"{month[:3]} {day}"))
    mark = draw.choice(_NOTHING_PRINTED_IN_A_CELL)
    if family == "nothing printed inside a number word":
        return _inside_letters(draw.choice(("ninety", "Ninety-two", "ninety-five", "hundred", "hundred+", "a hundred and one",
                                            "nonagenarian", "centenarian", "thousand")), mark, draw)
    if family == "nothing printed inside a month's name":
        return _inside_letters(draw.choice(_MONTHS_WHOLE), mark, draw)
    if family == "nothing printed inside a marked age":
        return _inside_figures(draw.choice((f"{age}+", f"~{age}", f">{age}", f"{age}?", f"≥{age}")), mark, draw)
    if family == "nothing printed inside a clock":
        return _inside_figures(draw.choice((f"{draw.randint(10, 23)}:{draw.randint(10, 59)}",
                                            f"{draw.randint(10, 23)}:{draw.randint(10, 59)}:{draw.randint(10, 59)}")), mark, draw, True)
    if family == "number words glued into one":
        return f"{draw.choice(_GLUED_TENS)}{draw.choice(('',) + _GLUED_ONES)}{draw.choice(('', '+', '?'))}"
    if family == "month beside a day in figures":
        named_month = draw.choice(_MONTHS_WHOLE + ("Jan", "Mar", "Sept", "Dec"))
        day = draw.randint(1, 31)
        ordinal = f"{day}{_ORDINAL_ENDS.get(day, 'th')}"
        return draw.choice((f"{day} of {named_month}", f"the {ordinal} of {named_month}", f"{ordinal} {named_month}",
                            f"{named_month} {ordinal}", f"{named_month} the {ordinal}"))
    if family == "about-word glued to an age":
        about = draw.choice(("ca", "approx", "circa", "about", "est", "estimated"))
        return draw.choice((f"{about}{age}", f"{about}.{age}", f"{age}{about}", f"c.{age}", f"{age}c"))
    if family == "decade past 89":
        return f"{draw.choice(('', 'in his ', 'in her ', 'late ', 'early ', 'mid-'))}{draw.choice(('90s', '100s', '110s', '120s'))}"
    if family == "age with its marks apart":
        return draw.choice((f"age : {age}", f"{age} ( est )", f"age - {age}", f"approx . {age}", f"{age} ( approx )", f"aged : {age}"))
    raise KeyError(family)


def _family(family: str, seed: int, count: int = WORD_SWEEP) -> "list[str]":
    """``count`` different spellings of one family, drawn from ``seed``."""
    draw = random.Random(seed)
    made: "dict[str, bool]" = {}
    for _attempt in range(50 * count):
        if len(made) >= count:
            break
        made[_word_spelling(family, draw)] = True
    return sorted(made)


def _named_alone(how: str, word: str) -> bool:
    """Whether path (ii) names a pool holding this one word, read ``how``."""
    return bool(taxonomy._names_under(how, (word,), False, False, False))


# -- HIPAA first: every class, every path, unanswered and answered -------------


def test_unanswered_no_class_is_named_on_any_label_road() -> None:
    # Unanswered, a label column is read SCREENED (`profile._held_back_named_here`):
    # path (iii) and path (i) name nothing until the person's `no`.
    def case() -> None:
        for place, kind in enumerate(CLASSES):
            for code in (False, True):
                described = _described(_rare_column(kind, 100 + place), taxonomy.HELD_BACK_NAMED_SCREENED, code)
                assert _held(described) or described.role == taxonomy.ROLE_COMPOUND, kind
                assert _names(described) == [], (kind, code)

    _red(case, taxonomy, "_names_under", _names_whatever_the_road)


def test_answered_no_names_a_class_only_where_no_shape_says_identifier() -> None:
    # PATH (iii), answered `no`: the unshaped classes are named, as the person's
    # `no` says; every shaped class -- a ZIP code, a date, an age over 89, a
    # telephone, an e-mail, a record, plan, account, licence, vehicle or device
    # number, a web or internet address, a hash -- names nothing even then.
    def case() -> None:
        for place, kind in enumerate(CLASSES):
            described = _described(_rare_column(kind, 200 + place), taxonomy.HELD_BACK_NAMED_ANSWERED)
            held = _held(described)
            assert held or described.role == taxonomy.ROLE_COMPOUND, kind
            if kind in UNSHAPED:
                assert len({value.casefold().strip() for value in _names(described)}) == held, kind
                assert described.held_back_nameable, kind
            else:
                assert _names(described) == [], kind
                assert not described.held_back_nameable, kind

    def unscreened(how: str, names: "tuple[str, ...]", comma: bool, total: bool, code: bool) -> "tuple[str, ...]":
        return names if how == taxonomy.HELD_BACK_NAMED_ANSWERED or not total else ()

    _red(case, taxonomy, "_names_under", unscreened)


def test_path_i_code_alone_names_nothing_and_no_names_a_declared_code() -> None:
    # A ZIP code or a device number answered `code` names no rare value
    # without `no` (the zoo plan's 2.3 (i), v2.1 verify item 1); a declared
    # code answered `no` names its pool, numbers among it (ICD-9 `486`).
    def case() -> None:
        for kind in ("zip code", "device serial"):
            described = _described(_rare_column(kind, 300), taxonomy.HELD_BACK_NAMED_SCREENED, True)
            assert _names(described) == [], kind
        codes = [f"{400 + place}" for place in range(60)]
        cells = ["250"] * 400 + ["401"] * 400
        for place, code in enumerate(codes):
            cells += [code] * (1 + place % 4)
        described = _described(cells, taxonomy.HELD_BACK_NAMED_ANSWERED, True)
        assert sorted(_names(described)) == sorted(code for code in codes if code != "401")

    def code_alone(how: str, names: "tuple[str, ...]", comma: bool, total: bool, code: bool) -> "tuple[str, ...]":
        return names if code else _REAL_NAMES_UNDER(how, names, comma, total, code)

    _red(case, taxonomy, "_names_under", code_alone)


def test_path_iii_names_no_number_of_a_column_of_words() -> None:
    # A number few rows of a column of words hold is a measurement's tail, never
    # printed by name (the owner's rule: no one-row extreme printed directly).
    cells = ["negative"] * 500 + ["positive"] * 300
    for value in ("trace", "9.4", "equivocal"):
        cells += [value] * 2

    def case() -> None:
        assert _names(_described(cells, taxonomy.HELD_BACK_NAMED_ANSWERED)) == []

    def no_number_rule(how: str, names: "tuple[str, ...]", comma: bool, total: bool, code: bool) -> "tuple[str, ...]":
        return names if how == taxonomy.HELD_BACK_NAMED_ANSWERED else ()

    _red(case, taxonomy, "_names_under", no_number_rule)


def test_a_long_tail_not_declared_a_code_names_nothing() -> None:
    # SKEPTIC 1'S ITEM 4: the tail is written in LETTERS ONLY, two words a
    # phrase, so no figure rule of the screen refuses it and only the long
    # tail's own exclusion stands between `no` and 900 names (the zoo plan's
    # 2.3: a long tail is named only as a declared code). Red on mLONG.
    draw = random.Random(5)
    cells: "list[str]" = []
    for place in range(40):
        cells += [f"common {_word(draw).lower()} {place % 2 and 'a' or 'b'}"] * 30
    phrases: "dict[str, bool]" = {}
    while len(phrases) < 900:
        phrases[f"{_word(draw).lower()} {_word(draw).lower()}"] = True
    cells += sorted(phrases)

    def case() -> None:
        described = _described(cells, taxonomy.HELD_BACK_NAMED_ANSWERED)
        assert described.role == taxonomy.ROLE_LONG_TAIL
        assert _names(described) == []
        assert not described.held_back_nameable
        # ...and declared a code, the same tail answered `no` names its pool (path (i)).
        declared = _described(cells, taxonomy.HELD_BACK_NAMED_ANSWERED, True)
        assert len(_names(declared)) >= 900 and declared.held_back_nameable

    _red(case, taxonomy, "_long_tail_named_only_as_a_code", lambda levels, declared: levels)


def test_a_pool_counted_in_people_names_nothing() -> None:
    # The owner's answer Z1 = B names values fewer than 11 ROWS hold; a pool
    # counted in people (plan P4-D453) holds levels few PEOPLE hold on any
    # number of rows, which lane PL's K-HZ-19 holds named nowhere.
    cells = _rare_column("surname", 900)
    kept = frozenset(value.casefold() for value in ("Alpha group", "Beta group", "Gamma group"))
    pooled = taxonomy.profile_column(
        "column", 1, cells, len(cells),
        dataclasses.replace(SETTINGS, held_back_named=taxonomy.HELD_BACK_NAMED_ANSWERED, levels_kept=kept),
        False, True,
    )
    assert _held(pooled) and _names(pooled) == []
    assert not pooled.held_back_nameable


# -- path (ii): the word screen -----------------------------------------------


def _with_numbers(words: "list[str]", seed: int) -> "list[str]":
    """A column of numbers with labels: 1,500 readings to two places beside ``words``."""
    draw = random.Random(seed)
    cells = [f"{draw.uniform(1, 400):.2f}" for _ in range(1500)]
    cells += ["QNS"] * 120 + ["Pending"] * 90
    return cells + words


def test_path_ii_names_result_words_and_refuses_every_shaped_class_and_a_comment() -> None:
    def case() -> None:
        letters_only = ["TNP"] * 3 + ["HI"] * 2 + ["LO"] + ["N/A"] * 2 + ["."] + ["Not done"] * 2
        described = _described(_with_numbers(letters_only, 1), taxonomy.HELD_BACK_NAMED_SCREENED)
        assert described.role == taxonomy.ROLE_COMPOUND
        # (`N/A` and `.` are read as missing marks, which path (ii) does not
        # name yet: P4-D471's stated limit (b).)
        assert sorted(_names(described)) == sorted({"HI", "LO", "Not done", "TNP"})
        assert not described.held_back_nameable  # nothing for `no` to add: no question
        # A WORD HOLDING A FIGURE IS NAMED ONLY AFTER `no` (ZS.3 (ii)): beside
        # one, the pool stays pooled whole unanswered, its letters too (all
        # or none), and the column is put the Safe Harbor question.
        figured = letters_only + ["1:40"] * 2 + ["20/200"]
        unanswered = _described(_with_numbers(figured, 1), taxonomy.HELD_BACK_NAMED_SCREENED)
        assert _names(unanswered) == [] and unanswered.held_back_nameable
        answered = _described(_with_numbers(figured, 1), taxonomy.HELD_BACK_NAMED_ANSWERED)
        assert sorted(_names(answered)) == sorted({"1:40", "20/200", "HI", "LO", "Not done", "TNP"})
        commented = _described(
            _with_numbers(letters_only + ["Called to J. Smith RN at 14:32"], 1), taxonomy.HELD_BACK_NAMED_ANSWERED
        )
        assert _names(commented) == [] and not commented.held_back_nameable
        for place, kind in enumerate(SHAPED):
            draw = random.Random(500 + place)
            shaped = [_spelling(kind, draw) for _ in range(SWEEP_SPELLINGS)]
            words_only = [
                value for cell, value in zip(taxonomy._classify_all(shaped), shaped) if cell.kind == "text"
            ]
            assert not [value for value in words_only if taxonomy.passes_the_word_screen(value)], kind
            described = _described(_with_numbers(letters_only + shaped[:3], place), taxonomy.HELD_BACK_NAMED_ANSWERED)
            # A shape that reads as a number (a ZIP code) joins the numbers;
            # every other one is a word the screen refuses, and the column
            # names none of its words: all or none.
            assert not set(shaped[:3]) & set(_names(described)), kind

    def unscreened(how: str, names: "tuple[str, ...]", comma: bool, total: bool, code: bool) -> "tuple[str, ...]":
        return names if not total else _REAL_NAMES_UNDER(how, names, comma, total, code)

    _red(case, taxonomy, "_names_under", unscreened)
    _red(case, taxonomy, "_names_under", _the_builds_names_under)


def test_path_ii_names_no_word_holding_a_figure_without_no_whatever_its_family() -> None:
    # SKEPTIC 1'S ITEM 1 AND THE STATISTICS SKEPTIC'S ITEM 1 (BLOCKER), ruled in
    # LANE CODES-2 RULINGS 3 (1): the generated sweep, thousands of spellings.
    # Unanswered or after `yes` (`HELD_BACK_NAMED_SCREENED`) no word of any
    # family but the letters of limit (a) is named; after `no`, the figure
    # words the screen passes are, and the words it refuses never are.
    def case() -> None:
        for place, family in enumerate(WORD_FAMILIES):
            for word in _family(family, 9000 + place):
                screened = _named_alone(taxonomy.HELD_BACK_NAMED_SCREENED, word)
                answered = _named_alone(taxonomy.HELD_BACK_NAMED_ANSWERED, word)
                if family in LIMIT_A:
                    assert screened and answered and not taxonomy._a_word_holding_a_figure(word), (family, word)
                elif family in AFTER_NO + REPAIR_2_AFTER_NO:
                    assert not screened and answered and taxonomy._a_word_holding_a_figure(word), (family, word)
                else:
                    assert not screened and not answered, (family, word)
        for word in ("TNP", "HI", "LO", "Not done", "QNS"):
            assert _named_alone(taxonomy.HELD_BACK_NAMED_SCREENED, word), word
        # Codex's case and the skeptic's (RULINGS 2 (1) and 3 (1)): named only after `no`.
        for word in ("#4521", "12-345", "4521/7", "#45-21", "120/80", "1:40", "***-1234"):
            assert not _named_alone(taxonomy.HELD_BACK_NAMED_SCREENED, word), word
            assert _named_alone(taxonomy.HELD_BACK_NAMED_ANSWERED, word), word
        for word in ("REC 1234", "S12-3456", "aged 101", "101 (est)", "90 est", "approx 92", "age 97", "03-31", "14-03",
                     "2021-W14", "100+", "J.S.", "J. Smith", "1100 m", "5000 w", "***-**-1234", "522**", "~95", "95?"):
            assert not _named_alone(taxonomy.HELD_BACK_NAMED_ANSWERED, word), word

    _red(case, taxonomy, "_names_under", _the_builds_names_under)


# -- lane CODES-2's repair 2: Codex's item 1 and the verify of repair 1 ----------
#
# THE SPACES OF THE SCREEN (Codex's item 1, the orchestrator's LANE CODES-2
# RULINGS 6 (1), a HIPAA blocker): a note joined by no-break or em spaces was
# one word, passed the two-word rule and was named with no answer. The class
# is closed by a generated sweep over every space, control and format
# character the running interpreter knows on the Basic Multilingual Plane
# and the astral ones the screen lists, in every position, on every road,
# through publication and the question, red on the screen's old six ASCII
# spaces.

_ASCII_SPACES_ONLY = " \t\n\r\x0b\x0c"
_NOTE_WORDS = ("Called", "patient", "Cedar", "Grove", "spoke", "with", "Dr", "Holloway", "left", "message",
               "daughter", "Wellbrook", "Street", "nurse", "Ana", "Corwick")


def _spaces_of_the_interpreter() -> "list[str]":
    """Every space, separator, control and format character of the Basic Multilingual Plane, as this Python reads them."""
    import unicodedata

    found: "list[str]" = []
    for code in range(0x10000):
        character = chr(code)
        if character.isspace() or unicodedata.category(character) in ("Cc", "Cf", "Zs", "Zl", "Zp"):
            found += [character]
    return found + ["\U000e0020", "\U000e0001", "\U0001d173", "\U0001bca0", "\U00013430"]


def test_every_space_control_and_format_character_is_a_space_and_every_figure_a_figure_to_the_screen() -> None:
    # Pinned against the running interpreter's Unicode database, as
    # `parsing`'s display controls are: a character the table misses turns
    # this red. And every figure `str.isdigit` knows on the plane is one.
    for character in _spaces_of_the_interpreter():
        assert taxonomy._a_space_of_the_screen(character), hex(ord(character))
        assert taxonomy._words_of(f"Cedar{character}Grove") == ["Cedar", "Grove"], hex(ord(character))
    for code in range(0x10000):
        if chr(code).isdigit():
            assert taxonomy._a_figure_of_any_script(chr(code)), hex(code)
    assert not [code for code in range(0x10000) if taxonomy._a_figure_of_any_script(chr(code))
                and taxonomy._a_letter_of_any_script(chr(code))]


def _notes_joined_by(space: str, draw: random.Random) -> "list[str]":
    """Notes of three to six words joined by ``space``: between the words, leading, trailing, doubled, beside ASCII spaces."""
    made: "list[str]" = []
    for _ in range(2):
        words = draw.sample(_NOTE_WORDS, draw.randint(3, 6))
        joined = space.join(words)
        made += [joined, space + joined, joined + space, (space * 2).join(words),
                 " ".join(words[:2]) + space + space.join(words[2:]), space.join(words[:2] + ["4521"] + words[2:])]
    return made


def test_a_note_joined_by_any_unicode_space_is_named_on_no_road_before_no() -> None:
    spaces = _spaces_of_the_interpreter()
    notes = {space: _notes_joined_by(space, random.Random(ord(space))) for space in spaces}

    def case() -> None:
        for space in spaces:
            for note in notes[space]:
                for pool in ((note,), (note, "HI")):
                    for total, code in ((False, False), (True, False), (True, True)):
                        assert not taxonomy._names_under(taxonomy.HELD_BACK_NAMED_SCREENED, tuple(sorted(pool)), False,
                                                         total, code), (hex(ord(space)), note)
                    # ...and path (ii) after `no`: more than two words is a note, never a result word.
                    assert not taxonomy._names_under(taxonomy.HELD_BACK_NAMED_ANSWERED, tuple(sorted(pool)), False,
                                                     False, False), (hex(ord(space)), note)

    _red(case, taxonomy, "_a_space_of_the_screen", lambda character: character in _ASCII_SPACES_ONLY)


# The characters RULINGS 6 (1) names, with Codex's two.
_RULED_SPACES = "\t\n\r\x0c\x0b\x85\xa0 " + "".join(chr(code) for code in range(0x2000, 0x2010)) + (
    "    ⁠　﻿")


def test_codexs_note_is_published_by_no_description_and_puts_no_question_for_any_space() -> None:
    # Codex's shape through the describe (publication and question
    # production): readings, `Not done` on the floor's rows and more, and ONE
    # note joined by each ruled character -- named nowhere, unanswered or
    # after `no`, and no question offered whose answer could name it.
    draw = random.Random(20261110)
    readings = [f"{draw.uniform(1, 400):.2f}" for _ in range(450)]

    def case() -> None:
        for place, space in enumerate(_RULED_SPACES):
            note = space.join(("Called", "patient", "Cedar", "Grove"))
            cells = readings + ["Not done"] * 149 + [note]
            hows = (taxonomy.HELD_BACK_NAMED_SCREENED,) + ((taxonomy.HELD_BACK_NAMED_ANSWERED,) if place % 8 == 6 else ())
            for how in hows:
                described = _described(cells, how)
                assert note not in _names(described), hex(ord(space))
                assert not described.held_back_nameable, hex(ord(space))

    _red(case, taxonomy, "_a_space_of_the_screen", lambda character: character in _ASCII_SPACES_ONLY)


# THE VERIFY OF REPAIR 1: item 3, ages past 89 and dates written in words;
# item 4, path (i)'s shapes no public code wears; item 5, a code's letter
# after figures read as an age's unit only where the number is one; item 7,
# figures of other scripts. Each family is generated and red on its rule.
_TENS_PAST_89 = ("ninety", "Ninety", "one hundred", "hundred", "a hundred", "One Hundred", "a centenarian", "nonagenarian")
_ONES = ("", "-one", "-two", " three", "-five", "-seven", "-nine", " and one")
_MONTHS_WHOLE = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                 "November", "December")
_DAYS_IN_WORDS = ("first", "second", "fifth", "twelfth", "twenty-first", "thirtieth", "three", "twenty")


def _words_family(family: str, draw: random.Random) -> str:
    if family == "age in words":
        return f"{draw.choice(_TENS_PAST_89)}{draw.choice(_ONES)}{draw.choice(('', '+', '?', ' plus', ' (est)'))}"
    if family == "month by its name":
        month = draw.choice(_MONTHS_WHOLE)
        return draw.choice((month, month.lower(), month.upper()))
    if family == "month beside a day in words":
        month = draw.choice(_MONTHS_WHOLE + ("Jan", "Mar", "Dec", "Sept"))
        day = draw.choice(_DAYS_IN_WORDS)
        return draw.choice((f"{month} {day}", f"{day} of {month}", f"the {day} of {month}", f"{month}-{day}"))
    raise KeyError(family)


def test_ages_past_89_and_dates_written_in_words_are_named_on_no_road() -> None:
    families = ("age in words", "month by its name", "month beside a day in words")
    spelled = {family: sorted({_words_family(family, random.Random(place * 1000 + step)) for step in range(300)})
               for place, family in enumerate(families)}

    def case() -> None:
        for family in families:
            for word in spelled[family]:
                for how in (taxonomy.HELD_BACK_NAMED_SCREENED, taxonomy.HELD_BACK_NAMED_ANSWERED):
                    for total, code in ((False, False), (True, False), (True, True)):
                        assert not taxonomy._names_under(how, (word,), False, total, code), (family, word, how)
        # ...and the words beside them that are no date stay names after `no`.
        for word in ("Mar", "Dec", "May repeat", "second dose", "eighty-nine", "Not done"):
            assert taxonomy._names_under(taxonomy.HELD_BACK_NAMED_ANSWERED, (word,), False, True, False), word

    _red(case, taxonomy, "_a_date_or_an_age_in_words", lambda word: False)


def _shapes_no_code_wears(draw: random.Random) -> "dict[str, str]":
    """One spelling of each of the verify's families path (i) named after `no` (item 4)."""
    age = draw.randint(90, 125)
    figures = lambda count: "".join(draw.choice("0123456789") for _ in range(count))  # noqa: E731
    name = _word(draw).lower()
    return {
        "week with its year": draw.choice((f"{draw.randint(1990, 2026)}-W{draw.randint(1, 52):02d}",
                                           f"W{draw.randint(1, 52):02d}-{draw.randint(1990, 2026)}")),
        "age with a mark": draw.choice((f"~{age}", f"{age}+", f">{age}", f"{age}?")),
        "age with its unit": draw.choice((f"{age} yrs", f"{age}y", f"{age * 12 + 3} m", f"{age * 53} wks", f"{age} y/o")),
        "age with a word": draw.choice((f"age {age}", f"aged {age}", f"{age} years old")),
        "age in words": draw.choice(("ninety-five", "hundred+", "One hundred and one")),
        "month by its name": draw.choice(_MONTHS_WHOLE),
        "clock": f"{draw.randint(0, 23):02d}:{draw.randint(0, 59):02d}",
        "e-mail with at": draw.choice((f"{name} at {name}.org", f"{name}(at){name}.org", f"{name}@{name}.org")),
        "host with a path": f"{name}.org/{name}",
        "internet address v6": f"fe80::{figures(3)}",
        "masked social security number": draw.choice((f"XXX-XX-{figures(4)}", f"***-**-{figures(4)}")),
        "picture file name": f"IMG_{figures(4)}.jpg",
        "masked ZIP area": f"{figures(3)}**",
    }


def _public_code_tails(draw: random.Random) -> "dict[str, list[str]]":
    """Spellings of public code systems a declared code holds (the price of path (i)'s screen, measured 0)."""
    return {
        "ICD-10-CM with a seventh character": [
            f"{draw.choice('STV')}{draw.randint(0, 99):02d}.{draw.randint(0, 9)}{draw.choice('0123456789X')}"
            f"{draw.randint(0, 9)}{draw.choice('ADS')}" for _ in range(400)],
        "ICD-10-PCS": ["".join(draw.choice("0123456789ABCDEFGHJKLMNPQRSTUVWXYZ") for _ in range(7)) for _ in range(400)],
        "NDC": ["-".join("".join(draw.choice("0123456789") for _ in range(width))
                         for width in draw.choice(((4, 4, 2), (5, 3, 2), (5, 4, 1)))) for _ in range(400)],
        "LOINC": [f"{draw.randint(1, 99999)}-{draw.randint(0, 9)}" for _ in range(400)],
        "HCPCS": [f"{draw.choice('ABCDEGHJKLMPQRSTV')}{draw.randint(0, 9999):04d}" for _ in range(400)],
        "ICD-10-CM": [f"{draw.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{draw.randint(0, 99):02d}.{draw.randint(0, 99)}"
                      for _ in range(400)],
    }


def test_path_i_names_no_shape_a_public_code_never_wears_and_every_public_code_it_did() -> None:
    def case() -> None:
        for step in range(150):
            for family, word in _shapes_no_code_wears(random.Random(step)).items():
                assert not taxonomy._names_under(taxonomy.HELD_BACK_NAMED_ANSWERED, (word, "A10.1"), False, True, True), (
                    family, word)
        for system, codes in _public_code_tails(random.Random(7)).items():
            for code in codes:
                assert taxonomy._names_under(taxonomy.HELD_BACK_NAMED_ANSWERED, (code,), False, True, True), (system, code)

    _red(case, taxonomy, "_a_shape_no_code_wears", lambda name: False)


def test_a_codes_letter_after_its_figures_is_an_age_unit_only_where_the_number_is_an_age_past_89() -> None:
    # Item 5: path (iii)'s net read `S72.001D`'s `D` as days and refused the
    # column's pool; now a unit reads an age only from 90 years in its unit.
    tails = _public_code_tails(random.Random(5))
    # ...the codes with no run of five figures: such a run is the net's own
    # refusal of a record number's shape (rule (2)), whatever the letters.
    codes = [code for code in tails["ICD-10-CM with a seventh character"] + tails["ICD-10-PCS"]
             if all(length < 5 for _start, length in taxonomy._figure_runs(code))]

    def case() -> None:
        for code in codes:
            assert taxonomy.passes_the_word_screen(code, False), code
        for word in ("92 yrs", "101y", "1100 m", "4700 wks", "33000 days", "100 y/o", "95.5 years"):
            assert not taxonomy.passes_the_word_screen(word, False), word
        for word in ("12 yrs", "6 m", "89 years", "3 wks"):
            assert taxonomy.passes_the_word_screen(word, False), word

    def any_unit(token: str) -> bool:
        low = taxonomy._ascii_letters(token)
        return bool(taxonomy._figure_runs(token)) and bool(set(low.split()) & taxonomy._AGE_UNIT_WORDS)

    _red(case, taxonomy, "_an_age_past_89_in_a_unit", any_unit)


_OTHER_SCRIPTS = {
    "Arabic-Indic": 0x0660, "extended Arabic-Indic": 0x06F0, "Devanagari": 0x0966, "Bengali": 0x09E6, "Thai": 0x0E50,
    "fullwidth": 0xFF10, "mathematical bold": 0x1D7CE,
}
_SUPERSCRIPTS = "⁰¹²³⁴⁵⁶⁷⁸⁹"


def _in_script(text: str, zero: int) -> str:
    return "".join(chr(zero + int(character)) if "0" <= character <= "9" else character for character in text)


def test_figures_of_every_script_are_figures_to_the_screen() -> None:
    # Item 7 (M02 left the gate green): records, ratios and dates written in
    # other scripts' figures are named only after `no`, and the dates and ages
    # among them are refused after `no` too, as their ASCII spellings are.
    draw = random.Random(20261111)
    records = [f"#{draw.randint(1000, 9999)}" for _ in range(40)] + [f"{draw.randint(10, 99)}-{draw.randint(100, 999)}"
                                                                      for _ in range(40)]
    dated = ["2023-07", "11/2022", "2021-W14", "14-03", "~95", "100+"]

    def case() -> None:
        for script, zero in _OTHER_SCRIPTS.items():
            for word in records:
                written = _in_script(word, zero)
                assert not _named_alone(taxonomy.HELD_BACK_NAMED_SCREENED, written), (script, written)
                assert _named_alone(taxonomy.HELD_BACK_NAMED_ANSWERED, written), (script, written)
            for word in dated:
                written = _in_script(word, zero)
                assert not _named_alone(taxonomy.HELD_BACK_NAMED_ANSWERED, written), (script, written)
                assert not taxonomy.passes_the_word_screen(written, False), (script, written)
        for word in records:
            written = "".join(_SUPERSCRIPTS[int(c)] if "0" <= c <= "9" else c for c in word)
            assert not _named_alone(taxonomy.HELD_BACK_NAMED_SCREENED, written), written

    _red(case, taxonomy, "_a_figure_of_any_script", lambda character: "0" <= character <= "9")


# -- lane CODES-2's follow-up: the verify of repair 2, items 1 to 5 ------------
#
# ITEM 1 (a HIPAA blocker; the orchestrator's LANE CODES-2 RULINGS 8 (2)):
# repair 2 read every control and format character as a space, so ONE of
# them inside a word or a number cut it in two and no reader of the screen
# saw its shape (`Ap<U+00AD>ril`, `nine<U+200B>ty-five`, `9<U+200B>5+`). Every screen
# now reads a spelling twice, as written and with what prints nothing
# removed, and names it only where both readings pass. The class is closed
# by a generated case over EVERY character that prints nothing (each Cf,
# each Cc that is not whitespace, every plane: 218 under Unicode 14.0, 225
# under 15.1), inside each word and number the screens read, on every road,
# unanswered and after `no`, red on the single reading.

_DAY_WORDS_WRITTEN = ("first", "fifth", "twelfth", "twentieth", "thirty", "eleven")


def _hidden_inside(draw: random.Random, mark: str) -> "dict[str, str]":
    """One spelling of each shape the screens read, ``mark`` inside a word or between its figures (or beside a mark)."""
    age = draw.randint(90, 125)
    unit_age = draw.choice((f"{age} yrs", f"{age} years", f"{draw.randint(1080, 1511)} months",
                            f"{draw.randint(4695, 6572)} weeks", f"{draw.randint(32871, 46018)} days"))
    return {
        "a number word": _inside_letters(draw.choice(("ninety", "Ninety-one", "ninety-seven", "hundred+", "a hundred",
                                                      "one hundred and four", "thousand", "nonagenarian", "centenarian")), mark, draw),
        "a month's name": _inside_letters(draw.choice(_MONTHS_WHOLE), mark, draw),
        "a month beside a day word": _inside_letters(draw.choice((f"{draw.choice(_MONTHS_WHOLE)} {draw.choice(_DAY_WORDS_WRITTEN)}",
                                                                  f"the {draw.choice(_DAY_WORDS_WRITTEN)} of {draw.choice(_MONTHS_WHOLE)}")),
                                                     mark, draw),
        "an about or age word": _inside_letters(draw.choice((f"approx {age}", f"circa {age}", f"about {age}", f"age {age}",
                                                             f"aged {age}", f"{age} years old")), mark, draw),
        "a unit word": _inside_letters(unit_age, mark, draw),
        "a marked age": _inside_figures(draw.choice((f"~{age}", f"{age}+", f">{age}", f"{age}?", f"≥{age}")), mark, draw, True),
        "a clock": _inside_figures(draw.choice((f"{draw.randint(0, 23):02d}:{draw.randint(0, 59):02d}",
                                                f"{draw.randint(0, 23):02d}:{draw.randint(0, 59):02d}:{draw.randint(0, 59):02d}")),
                                   mark, draw, True),
        "a date": _inside_figures(draw.choice((f"{draw.randint(13, 28)}-{draw.randint(1, 12):02d}",
                                               f"{draw.randint(1990, 2026)}-{draw.randint(1, 12):02d}",
                                               f"{draw.randint(1, 12):02d}/{draw.randint(1990, 2026)}")), mark, draw, True),
        "a week": _inside_figures(draw.choice((f"{draw.randint(1990, 2026)}-W{draw.randint(10, 52)}",
                                               f"W{draw.randint(10, 52)}-{draw.randint(1990, 2026)}")), mark, draw, True),
        "a masked number": _inside_figures(draw.choice((f"XXX-XX-{draw.randint(1000, 9999)}", f"{draw.randint(100, 999)}**",
                                                        f"face_{draw.randint(1000, 9999)}.jpg")), mark, draw),
        # ...and the shapes some road names by design (a plain number, a run
        # of five figures, a date in figures on path (i)): named with the
        # character only where named without it.
        "a number": _inside_figures(f"{draw.randint(10, 99999)}", mark, draw),
    }


_NAMED_SOMEWHERE_BY_DESIGN = ("a date", "a number")


def test_a_character_that_prints_nothing_inside_a_word_or_a_number_hides_no_shape_on_any_road() -> None:
    every = _printing_nothing()
    spelled = [(mark, _hidden_inside(random.Random(ord(mark) * 2 + step), mark)) for mark in every for step in range(2)]

    def case() -> None:
        for mark, shapes in spelled:
            for shape, word in shapes.items():
                bare = word.replace(mark, "")
                for how in (taxonomy.HELD_BACK_NAMED_SCREENED, taxonomy.HELD_BACK_NAMED_ANSWERED):
                    for total, code in ((False, False), (True, False), (True, True)):
                        named = bool(taxonomy._names_under(how, (word,), False, total, code))
                        if shape in _NAMED_SOMEWHERE_BY_DESIGN:
                            assert not named or taxonomy._names_under(how, (bare,), False, total, code), (
                                shape, hex(ord(mark)), ascii(word), how, total, code)
                        else:
                            assert not named, (shape, hex(ord(mark)), ascii(word), how, total, code)

    _red(case, taxonomy, "_without_what_prints_nothing", lambda text: text)
    # ...and the fixed table holds every one, and no character `str.split()` cuts at.
    assert not [hex(ord(character)) for character in every if not taxonomy._prints_nothing(character)]
    assert not [hex(code) for code in range(0x110000) if chr(code).isspace() and taxonomy._prints_nothing(chr(code))]


# ITEM 2 (RULINGS 8 (3)): number words glued into one (`ninetyfive`,
# `NinetyTwo`, `HundredEight+`, `onehundredtwo?`) were named with no question.

def test_number_words_glued_into_one_are_an_age_in_words_on_every_road() -> None:
    glued = sorted({f"{tens}{one}{mark}" for tens in _GLUED_TENS for one in ("",) + _GLUED_ONES + tuple(
        word.capitalize() for word in _GLUED_ONES) for mark in ("", "+", "?")} | {
        "hundredandone", "onehundredandtwelve", "hundredten", "onehundredtwentyfive", "ahundred", "Hundredandten",
        "ninetyfiveyrs", "hundredplus", "ninetyish"})

    def case() -> None:
        for word in glued:
            for how in (taxonomy.HELD_BACK_NAMED_SCREENED, taxonomy.HELD_BACK_NAMED_ANSWERED):
                for total, code in ((False, False), (True, False), (True, True)):
                    assert not taxonomy._names_under(how, (word,), False, total, code), (word, how, total, code)
        # ...and a word that only begins so stays a name after `no`.
        for word in ("hundredweight", "thousandfold", "onehundredth", "Ninetysomething"):
            assert taxonomy._names_under(taxonomy.HELD_BACK_NAMED_ANSWERED, (word,), False, True, False), word

    _red(case, taxonomy, "_number_words_glued", lambda letters: False)


# THE GLUED GRAMMAR ENUMERATED (the micro-step on the follow-up's scoped
# verify, its item 1, a HIPAA blocker; the orchestrator's LANE CODES-2
# RULINGS 10 (1)): read longest first and never given back, `eight` before an
# end word in `y` was read `eighty` (`ninetyeightyrs`, `HundredEightYears`,
# `onehundredandeightyearsold`), so 819 of these 23,562 spellings were named
# on each road on the follow-up's head. THE NUMBER WORDS ARE WRITTEN HERE and
# never read from the reader's own list, so the case cannot pass by sharing
# the reader's mistake; the end words are written here too, and the reader's
# list is pinned to them.

_GRAMMAR_ONES = ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
_GRAMMAR_TEENS = ("ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
                  "nineteen")
_GRAMMAR_END_WORDS = ("yearsold", "yearold", "years", "year", "yrs", "plus", "odd", "ish", "old", "yr", "yo", "y", "s")
_GRAMMAR_NEAR_MISSES = ("hundredweight", "Thousandfold", "onehundredth", "Ninetysomething", "Hundredsville",
                        "nineteenseventy")
_FOUR_ROADS = {
    "path (ii) unanswered": (taxonomy.HELD_BACK_NAMED_SCREENED, False, False),
    "path (ii) after no": (taxonomy.HELD_BACK_NAMED_ANSWERED, False, False),
    "path (iii) after no": (taxonomy.HELD_BACK_NAMED_ANSWERED, True, False),
    "path (i) after no": (taxonomy.HELD_BACK_NAMED_ANSWERED, True, True),
}


def _the_glued_grammar() -> "list[str]":
    """Every spelling of the glued grammar, 23,562 in all.

    Each head (`ninety`, `hundred`, `onehundred`, `ahundred`, with and
    without `and`) and each number word after it up to 129; each end word or
    none; in small letters, in capitals and in capitalised words; a mark
    before, after or none.
    """
    small = [(one,) for one in _GRAMMAR_ONES] + [(teen,) for teen in _GRAMMAR_TEENS]
    small += [("twenty",)] + [("twenty", one) for one in _GRAMMAR_ONES]
    bodies: "list[tuple[str, ...]]" = [("ninety",)] + [("ninety", one) for one in _GRAMMAR_ONES]
    for head in (("hundred",), ("one", "hundred"), ("a", "hundred")):
        bodies += [head]
        for joint in ((), ("and",)):
            bodies += [head + joint + words for words in small]
    spellings: "list[str]" = []
    for words in bodies:
        for end in ("",) + _GRAMMAR_END_WORDS:
            lower = "".join(words) + end
            for cased in (lower, lower.upper(), "".join(word.capitalize() for word in words) + end.capitalize()):
                spellings += [before + cased + after for before, after in (("", ""), ("~", ""), ("", "+"))]
    return spellings


def _the_greedy_rest(rest: str) -> bool:
    """MUTANT: the follow-up's read, each number word taken longest first and never given back."""
    moved = True
    while rest and moved:
        moved = False
        for piece in taxonomy._GLUED_NUMBER_WORDS:
            if rest[: len(piece)] == piece:
                rest = rest[len(piece):]
                moved = True
                break
    return rest == "" or rest in taxonomy._GLUED_ENDS


def test_the_glued_grammar_enumerated_is_named_on_no_road_and_its_near_misses_stay_names() -> None:
    grammar = _the_glued_grammar()
    assert len(grammar) == len(set(grammar)) == 23_562
    assert sorted(taxonomy._GLUED_ENDS) == sorted(_GRAMMAR_END_WORDS)

    def case() -> None:
        for road, (how, total, code) in _FOUR_ROADS.items():
            named = [word for word in grammar if taxonomy._names_under(how, (word,), False, total, code)]
            assert not named, (road, len(named), named[:6])
        for word in _GRAMMAR_NEAR_MISSES:
            for road, (how, total, code) in _FOUR_ROADS.items():
                assert taxonomy._names_under(how, (word,), False, total, code), (road, word)

    _red(case, taxonomy, "_glued_rest_reads", _the_greedy_rest)


# ITEM 3 (RULINGS 8 (4)): the week reader read `W16.011` as week 1 of the
# year 6011, so path (i) refused ICD-10-CM codes of the W chapter written
# without their seventh character, and their column named nothing.

def _the_week_reader_of_repair_2(token: str) -> bool:
    """MUTANT: repair 2's week reader, its points dropped and its year unbounded."""
    low = "".join(character for character in token.casefold() if character not in "-/.")
    if low.count("w") != 1:
        return False
    before, after = low.split("w")
    if len(before) == 4 and before.isdigit() and after.isdigit() and 1 <= len(after) <= 3:
        return 1 <= int(after[:2]) <= 53
    if not before and after.isdigit() and len(after) in (5, 6):
        return 1 <= int(after[: len(after) - 4]) <= 53
    return False


def test_a_week_is_read_beside_a_year_of_1900_to_2100_and_the_w_chapters_codes_stay_named() -> None:
    draw = random.Random(20261111)
    codes = sorted({f"W{draw.randint(0, 99):02d}" + draw.choice((
        f".{draw.randint(0, 9)}", f".{draw.randint(0, 99):02d}", f".{draw.randint(0, 999):03d}", f"{draw.randint(0, 999):03d}",
        f".{draw.randint(0, 9)}X{draw.randint(0, 9)}")) for _ in range(3000)})
    weeks = ("2021-W14", "1990W11", "2021-W14-3", "W14-2021", "2021/W14", "W5-2021", "2021-W5", "2021W143", "W142021",
             "1999-W53", "2100-W01")

    def case() -> None:
        for code in codes:
            assert taxonomy._names_under(taxonomy.HELD_BACK_NAMED_ANSWERED, (code, "A10.1"), False, True, True), code
        for week in weeks:
            assert taxonomy._a_week_of_a_year(week), week
            for total, code_declared in ((False, False), (True, False), (True, True)):
                assert not taxonomy._names_under(taxonomy.HELD_BACK_NAMED_ANSWERED, (week,), False, total, code_declared), week
        # ...(`2021.W14` is a week since the micro-step, the case below).
        for spelled in ("W16.011", "1850-W14", "2150-W14", "2021-W54", "2021-W00", "W16011"):
            assert not taxonomy._a_week_of_a_year(spelled), spelled

    _red(case, taxonomy, "_a_week_of_a_year", _the_week_reader_of_repair_2)


# THE WEEK RE-RULED (the micro-step on the follow-up's scoped verify, its item
# 2; the orchestrator's LANE CODES-2 RULINGS 10 (2)): read never across a
# point, a week joined to its year by one was named after `no` on paths (iii)
# and (i) of the follow-up's head (30 of the verify's 30 on path (i), 24 on
# path (iii)). A point now joins where no code is written so: a four-figure
# year from 1900 to 2100 written first to its week and the week to its day
# (`2021.W14`, `2021-W14.3`), and a week written first to a four-figure year
# after its point (`W14.2021`) -- no code of the W chapter has four figures
# after its point (`W16.011` has three) and none begins with four figures and
# `W`. A week or a year outside those bounds is no week: named after `no`, the
# stated limit (m).

_REAL_WEEK_READER = taxonomy._a_week_of_a_year
_WEEKS_JOINED_BY_A_POINT = (
    "2021.W14", "2021-W14.3", "W14.2021", "1999.W05", "W05.1999", "1999-W52.3", "1999.W5", "W5.1999", "2021.W14.3",
    "2021/W14.3", "2021W14.3", "1900.W01", "2100.W53", "W53.2100", "W01.1900", "w14.2021",
)
_WEEKS_OUT_OF_BOUNDS = ("1899-W14", "2101-W14", "6011-W01", "2021-W54", "2021-W00", "W14-1899", "W14-2101")


def _refusing_every_point(token: str) -> bool:
    """MUTANT: the follow-up's week reader, which read no spelling holding a point as a week."""
    return "." not in token and _REAL_WEEK_READER(token)


def test_a_week_joined_by_a_point_to_a_year_of_1900_to_2100_is_refused_on_every_road() -> None:
    def case() -> None:
        for week in _WEEKS_JOINED_BY_A_POINT:
            assert taxonomy._a_week_of_a_year(week), week
            for road, (how, total, code) in _FOUR_ROADS.items():
                assert not taxonomy._names_under(how, (week,), False, total, code), (road, week)
        # ...and the W chapter's codes, at most three figures after their point, stay codes.
        for code in ("W16.011", "W16.01", "W16.0", "W14", "W19.XXXA", "W16.011A", "W22.041", "W10.1XXD", "W16011", "W22041"):
            assert not taxonomy._a_week_of_a_year(code), code
            assert taxonomy._names_under(taxonomy.HELD_BACK_NAMED_ANSWERED, (code, "A10.1"), False, True, True), code

    _red(case, taxonomy, "_a_week_of_a_year", _refusing_every_point)


def test_a_week_or_a_year_out_of_bounds_is_no_week_and_stays_named_after_no_the_stated_limit_m() -> None:
    # The bounds read the same with a point or without: 1900 and 2100, weeks 1
    # and 53, are read; one step past them is not.
    edges = ("1900.W14", "2100.W14", "2021.W01", "2021.W53", "W14.1900", "W14.2100", "1900-W14", "2100-W14", "W14-1900",
             "W14-2100")
    past = _WEEKS_OUT_OF_BOUNDS + ("1899.W14", "2101.W14", "6011.W01", "2021.W54", "2021.W00", "W14.1899", "W14.2101")

    def case() -> None:
        for week in edges:
            assert taxonomy._a_week_of_a_year(week), week
        for spelled in past:
            assert not taxonomy._a_week_of_a_year(spelled), spelled
            for total, code in ((True, False), (True, True)):
                assert taxonomy._names_under(taxonomy.HELD_BACK_NAMED_ANSWERED, (spelled,), False, total, code), (
                    spelled, total, code)

    _red(case, taxonomy, "_a_year_a_week_is_read_beside", lambda text: len(text) == 4 and text.isdigit())
    _red(case, taxonomy, "_the_figures_of_a_week", lambda text: 1 <= len(text) <= 2 and text.isdigit())


# ITEM 4 (RULINGS 8 (5)): after `no`, paths (i) and (iii) named a month beside
# a day in figures, a word of about glued to an age or joined to it by a
# point, a decade past 89 and an age whose marks stand apart. Each family was
# priced first (P4-D471): each costs no code of any public system, save `c`
# glued BEFORE the number, the ICD-10-CM categories C90 to C96 (limit (m)).

_NEIGHBOUR_READERS = {
    "month beside a day in figures": "_a_month_beside_a_day_in_figures",
    "about-word glued to an age": "_an_about_word_glued_to_an_age",
    "decade past 89": "_a_decade_past_89",
    "age with its marks apart": "_an_age_past_89_with_its_marks_apart",
}


@pytest.mark.parametrize("family", sorted(_NEIGHBOUR_READERS))
def test_each_neighbour_family_is_refused_after_no_on_every_road_and_red_without_its_reader(family: str) -> None:
    spellings = _family(family, 9200 + WORD_FAMILIES.index(family))

    def case() -> None:
        for word in spellings:
            for how in (taxonomy.HELD_BACK_NAMED_SCREENED, taxonomy.HELD_BACK_NAMED_ANSWERED):
                for total, code in ((False, False), (True, False), (True, True)):
                    assert not taxonomy._names_under(how, (word,), False, total, code), (family, word, how, total, code)

    _red(case, taxonomy, _NEIGHBOUR_READERS[family], lambda word: False)


def test_c_glued_before_an_age_stays_a_code_the_stated_limit_m() -> None:
    # The ICD-10-CM categories C90 to C96 are written so: path (i) names them
    # after `no`, while `c.95`, `95c` and `c 95` are refused.
    for code in ("C90", "C91", "C92", "C93", "C94", "C95", "C96", "C95.10", "C91.Z0"):
        assert taxonomy._names_under(taxonomy.HELD_BACK_NAMED_ANSWERED, (code,), False, True, True), code
    for word in ("c.95", "95c", "c. 95", "C.101"):
        assert not taxonomy._names_under(taxonomy.HELD_BACK_NAMED_ANSWERED, (word,), False, True, True), word


# ITEM 5 (RULINGS 8 (6)): repair 2 read `SSN` only apart from figures, so
# `SSN1234` was named after `no` on path (iii); paths (ii) and (iii) read it
# as repair 1 did, and path (i) keeps the narrowing (`0SSN123` is a code's).

def test_ssn_glued_to_figures_is_refused_on_paths_ii_and_iii_and_a_codes_letters_on_path_i() -> None:
    def case() -> None:
        for word in ("SSN1234", "ssn1234", "SSN1234X", "Ssn4410", "SSN#1234", "SSN 1234"):
            for total in (False, True):
                assert not taxonomy._names_under(taxonomy.HELD_BACK_NAMED_ANSWERED, (word,), False, total, False), word
        for code in ("0SSN123", "0SSN0ZZ", "0SSN04Z"):
            assert taxonomy._names_under(taxonomy.HELD_BACK_NAMED_ANSWERED, (code,), False, True, True), code

    _red(case, taxonomy, "_a_masked_social_security_number",
         lambda word: taxonomy._a_masked_social_security_number_of_a_code(word))


def _without(target: "object", name: str, kept: "object") -> "object":
    """A mutant of ``name``: the function as it is, save that it answers ``kept`` where the rule reads its token."""
    real = getattr(target, name)

    def mutant(token: str, *rest: "object") -> "object":
        return False if kept(token) else real(token, *rest)  # type: ignore[operator]

    return mutant


def _two_figure_parts(token: str) -> bool:
    parts = taxonomy._parts_between(token, "/-.")
    return len(parts) == 2 and all(taxonomy._all_figures(part) for part in parts)


_RULE_MUTANTS: "dict[str, tuple[bool, dict[str, object]]]" = {
    # family: (path (ii)'s screen, or path (iii)'s net; the rule's functions and their mutants)
    "record beside letters": (True, {"_letters_beside_figures": lambda word: False}),
    "initials": (True, {"_an_initial": lambda word: False}),
    "web address": (True, {"_an_internet_address": _without(
        taxonomy, "_an_internet_address", lambda word: "://" in word or "www." in word.casefold())}),
    "e-mail or host with a path": (True, {"_an_internet_address": _without(
        taxonomy, "_an_internet_address", lambda word: "@" not in word and "://" not in word)}),
    "internet address v6": (False, {"_an_internet_address": _without(
        taxonomy, "_an_internet_address", lambda word: ":" in word)}),
    "clock": (True, {"_reads_as_a_date_or_clock": _without(
        taxonomy, "_reads_as_a_date_or_clock", lambda token: ":" in token or token.casefold().endswith(("am", "pm")))}),
    "month and day": (True, {"_reads_as_a_date_or_clock": _without(taxonomy, "_reads_as_a_date_or_clock", _two_figure_parts)}),
    "month and year": (True, {"_reads_as_a_date_or_clock": _without(taxonomy, "_reads_as_a_date_or_clock", _two_figure_parts)}),
    # A week is refused twice over on path (iii)'s net: by its own rule and by
    # `w` beside figures, an age in weeks (both gone, it passes).
    "week": (False, {"_a_week_of_a_year": lambda token: False, "_AGE_UNIT_WORDS": taxonomy._AGE_UNIT_WORDS - {"w"}}),
    "age with more": (True, {"_reads_as_a_date_or_clock": _without(
        taxonomy, "_reads_as_a_date_or_clock", lambda token: "+" in token or ">" in token or "≥" in token)}),
    "age with a mark": (True, {"_an_age_past_89_with_a_mark": lambda token: False}),
    # An age with a word is refused by rule (6) on path (ii) and by the words
    # and units of an age on the net: every one of them gone, it passes.
    "age with a word": (True, {"_letters_beside_figures": lambda word: False, "_AGE_WORDS": frozenset(),
                               "_AGE_UNIT_WORDS": frozenset(), "_ABOUT_WORDS": frozenset()}),
    "masked identifier": (False, {"_an_identifier_shape": lambda word: False}),
}


@pytest.mark.parametrize("family", sorted(_RULE_MUTANTS))
def test_each_rule_of_the_screen_refuses_its_family_and_is_red_without_it(family: str) -> None:
    # Skeptic 1's item 6 (mWEB, mCLOCK and mSLASH survived the build's gate)
    # and the statistics skeptic's items 1 and 2: every family the screen
    # refuses is refused by a rule of its own, and the family passes once the
    # rule is gone. A family path (ii)'s rule (6) also refuses (a week holds a
    # letter, an internet address its hexadecimal letters) is read through
    # path (iii)'s net, which sets rule (6) aside.
    path_ii, mutants = _RULE_MUTANTS[family]
    spellings = _family(family, 9100 + WORD_FAMILIES.index(family))

    def case() -> None:
        passed = [word for word in spellings if taxonomy.passes_the_word_screen(word, path_ii)]
        assert passed == [], (family, passed[:5])

    _red_together(case, taxonomy, mutants)


def test_path_iii_net_refuses_dates_without_a_day_ages_and_addresses_and_states_what_it_passes() -> None:
    # The statistics skeptic's items 1 and 3: behind the person's `no` a label
    # column names its pool unless one held-back spelling reads as a number
    # or is shaped as an identifier (`passes_the_word_screen(word, False)`).
    # REFUSED, each red on its mutant above or here: a month beside a year, a
    # day above 12 beside a month, a week, an age past 89 with a mark, with
    # `age` or with a unit after its figures, a clock, an e-mail's `at`
    # written out, a host with a path, and rule (8)'s shapes (a masked social
    # security number, a picture's file name, a masked ZIP area).
    # PASSED, stated in P4-D471 (the person's `no` governs them): record-like
    # words of six figures or fewer with no run of five, letters beside
    # figures in a code's pattern, initials, bare host names, and a code
    # whose letter stands BEFORE its figures (`M54.5`: no age unit there).
    def case() -> None:
        for word in ("14-03", "2023-07", "11/2022", "13/01", "2021-W14", "100+", "age 101", "aged 95", "14:32",
                     "jsmith(at)wellbrook.org", "jsmith at wellbrook.org", "wellbrook.org/jsmith", "fe80::1",
                     "1100 m", "92 yrs", "***-**-1234", "XXX-XX-6789", "SSN 6789", "face_0012.jpg", "522**", "522xx", "~95",
                     "95 est", "approx 92", "101 (est)"):
            assert not taxonomy.passes_the_word_screen(word, False), word
        for word in ("REC 1234", "S12-3456", "#4521", "J.S.", "wellbrook.org", "3C-01A", "Type 2", "M54.5", "W19",
                     "D50.9", "Y92.009"):
            assert taxonomy.passes_the_word_screen(word, False), word

    _red(case, taxonomy, "_AGE_WORDS", frozenset())
    _red(case, taxonomy, "_AGE_UNIT_WORDS", taxonomy._AGE_UNIT_WORDS - {"m", "yrs"})
    _red(case, taxonomy, "_an_identifier_shape", lambda word: False)
    _red_together(case, taxonomy, {"_a_week_of_a_year": lambda token: False,
                                   "_AGE_UNIT_WORDS": taxonomy._AGE_UNIT_WORDS - {"w"}})


# THE STATISTICS SKEPTIC'S FAMILIES (wave6/CODES-2-stat/screen_sweep.py, the
# orchestrator's LANE CODES-2 RULINGS 4 (1): the families, not only his
# spellings), each spelled 400 ways here, and where each lands now: REFUSED by
# the screen on both roads it reads (named on none); (ii) REFUSES, a shape also
# a plain code's that path (iii) names after `no` alone (P4-D471's stated
# limit, its counts recorded); AFTER NO, figures and marks named only after
# `no`; LIMIT (a), letters and marks named by path (ii) with no question.
# Each family but limit (a)'s is red on the mutant of the rule that places it.

def _stat_families(draw: random.Random) -> "dict[str, object]":
    figures = lambda count: "".join(draw.choice("0123456789") for _ in range(count))  # noqa: E731
    letters = lambda count: "".join(draw.choice("ABCDEFGHJKLMNPRSTUVWXYZ") for _ in range(count))  # noqa: E731
    month_word = lambda: draw.choice(("Jan", "Feb", "Mar", "Apr", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"))  # noqa: E731
    who = lambda: draw.choice(("smith", "jones", "lee"))  # noqa: E731
    return {
        "date: YYYY-MM": lambda: f"{draw.randint(1990, 2026)}-{draw.randint(1, 12):02d}",
        "date: MM/YYYY": lambda: f"{draw.randint(1, 12):02d}/{draw.randint(1990, 2026)}",
        "date: YYYY/MM": lambda: f"{draw.randint(1990, 2026)}/{draw.randint(1, 12):02d}",
        "date: M-YYYY": lambda: f"{draw.randint(1, 12)}-{draw.randint(1990, 2026)}",
        "date: DD-MM": lambda: f"{draw.randint(13, 28):02d}-{draw.randint(1, 12):02d}",
        "date: MM-DD": lambda: f"{draw.randint(1, 12):02d}-{draw.randint(13, 28):02d}",
        "date: YYYY-Www": lambda: f"{draw.randint(1990, 2026)}-W{draw.randint(1, 52):02d}",
        "date: Mon YYYY": lambda: f"{month_word()} {draw.randint(1990, 2026)}",
        "date: Mon-YY": lambda: f"{month_word()}-{draw.randint(0, 99):02d}",
        "date: DDMonYYYY": lambda: f"{draw.randint(1, 28):02d}{month_word().upper()}{draw.randint(1990, 2026)}",
        "date: MM/DD/YY": lambda: f"{draw.randint(1, 12)}/{draw.randint(1, 28)}/{draw.randint(0, 99):02d}",
        "age: NN+": lambda: f"{draw.randint(90, 110)}+",
        "age: age NN": lambda: f"age {draw.randint(90, 110)}",
        "age: NN yo": lambda: f"{draw.randint(90, 110)} yo",
        "age: NNy": lambda: f"{draw.randint(90, 110)}y",
        "phone: NNN-NNNN": lambda: f"{figures(3)}-{figures(4)}",
        "phone: ext NNNN": lambda: f"ext {figures(4)}",
        "e-mail: user at host": lambda: f"{letters(1).lower()}{who()} at example.org",
        "e-mail: user(at)host": lambda: f"{letters(1).lower()}{who()}(at)example.org",
        "ssn: XXX-XX-NNNN": lambda: f"XXX-XX-{figures(4)}",
        "ssn: last four": lambda: f"SSN {figures(4)}",
        "record: REC-NNNN": lambda: f"REC-{figures(4)}",
        "record: NNN-NNN": lambda: f"{figures(3)}-{figures(3)}",
        "record: AANN-NNNN": lambda: f"{letters(2)}{figures(2)}-{figures(4)}",
        "record: #RCNNNN": lambda: f"#RC{figures(4)}",
        "plan: AAANNNANNN": lambda: f"{letters(3)}{figures(3)}{letters(1)}{figures(3)}",
        "account: ACCT NNNN": lambda: f"ACCT {figures(4)}",
        "licence: RN-NNNN": lambda: f"RN-{figures(4)}",
        "licence: AA NNNN": lambda: f"{letters(2)} {figures(4)}",
        "plate: AAA NNNN": lambda: f"{letters(3)} {figures(4)}",
        "plate: NAAANNN": lambda: f"{figures(1)}{letters(3)}{figures(3)}",
        "plate: AAA-NNN": lambda: f"{letters(3)}-{figures(3)}",
        "device: SN NNNN": lambda: f"SN {figures(4)}",
        "device: SN-AANNNN": lambda: f"SN-{letters(2)}{figures(4)}",
        "url: bare domain": lambda: f"{who()}{figures(2)}.example.org",
        "url: domain/path": lambda: f"example.org/{letters(1).lower()}{who()}",
        "ip: IPv6 short": lambda: f"fe80::{draw.randint(1, 9999):x}",
        "ip: IPv6 doc": lambda: f"2001:db8::{draw.randint(1, 255):x}",
        "image: face_NNNN.jpg": lambda: f"face_{figures(4)}.jpg",
        "image: IMG_NNNN.JPG": lambda: f"IMG_{figures(4)}.JPG",
        "hash: 12 hex": lambda: "".join(draw.choice("abcdef0123456789") for _ in range(12)),
        "zip3: NNN**": lambda: f"{figures(3)}**",
        "zip3: NNNxx": lambda: f"{figures(3)}xx",
        "street: Name St": lambda: f"{draw.choice(('Elm', 'Oak', 'Maple', 'Cedar'))} {draw.choice(('St', 'Ave', 'Rd'))}",
        "name: Surname": lambda: draw.choice(("Smith", "Okafor", "Lindqvist", "Nguyen", "Garcia")),
    }


_CODE_SHAPED = (
    "phone: ext NNNN", "record: REC-NNNN", "record: AANN-NNNN", "record: #RCNNNN", "plan: AAANNNANNN",
    "account: ACCT NNNN", "licence: RN-NNNN", "licence: AA NNNN", "plate: AAA NNNN", "plate: NAAANNN",
    "plate: AAA-NNN", "device: SN NNNN", "device: SN-AANNNN", "url: bare domain", "hash: 12 hex",
)
_STAT_LANDING = {
    **{family: "(ii) refuses" for family in _CODE_SHAPED},
    "record: NNN-NNN": "after no",
    "street: Name St": "limit (a)",
    "name: Surname": "limit (a)",
}
_TWO_PARTS = _without(taxonomy, "_reads_as_a_date_or_clock", _two_figure_parts)
_STAT_MUTANTS: "dict[str, dict[str, object]]" = {
    **{family: {"_a_year_beside_a_month": lambda year, month: False}
       for family in ("date: YYYY-MM", "date: MM/YYYY", "date: YYYY/MM", "date: M-YYYY")},
    "date: DD-MM": {"_reads_as_a_date_or_clock": _TWO_PARTS},
    "date: MM-DD": {"_reads_as_a_date_or_clock": _TWO_PARTS},
    "date: YYYY-Www": {"_a_week_of_a_year": lambda token: False, "_AGE_UNIT_WORDS": taxonomy._AGE_UNIT_WORDS - {"w"}},
    **{family: {"_MONTH_WORDS": frozenset()} for family in ("date: Mon YYYY", "date: Mon-YY", "date: DDMonYYYY")},
    "date: MM/DD/YY": {"_reads_as_a_date_or_clock": _without(
        taxonomy, "_reads_as_a_date_or_clock", lambda token: token.count("/") == 2)},
    "age: NN+": {"_reads_as_a_date_or_clock": _without(taxonomy, "_reads_as_a_date_or_clock", lambda token: "+" in token)},
    "age: age NN": {"_AGE_WORDS": frozenset()},
    "age: NN yo": {"_AGE_UNIT_WORDS": taxonomy._AGE_UNIT_WORDS - {"yo"}},
    "age: NNy": {"_AGE_UNIT_WORDS": taxonomy._AGE_UNIT_WORDS - {"y"}},
    "phone: NNN-NNNN": {"WORD_SCREEN_FIGURES_AT_MOST": 7},
    "e-mail: user at host": {"_an_e_mail_written_with_at": lambda word: False},
    "e-mail: user(at)host": {"_an_internet_address": _without(
        taxonomy, "_an_internet_address", lambda word: "(at)" in word.casefold())},
    "ssn: XXX-XX-NNNN": {"_a_masked_social_security_number": lambda word: False},
    "ssn: last four": {"_a_masked_social_security_number": lambda word: False},
    "url: domain/path": {"_an_internet_address": _without(taxonomy, "_an_internet_address", lambda word: "/" in word)},
    "ip: IPv6 short": {"_an_internet_address": _without(taxonomy, "_an_internet_address", lambda word: ":" in word)},
    "ip: IPv6 doc": {"_an_internet_address": _without(taxonomy, "_an_internet_address", lambda word: ":" in word)},
    "image: face_NNNN.jpg": {"_an_image_file_name": lambda word: False},
    "image: IMG_NNNN.JPG": {"_an_image_file_name": lambda word: False},
    "zip3: NNN**": {"_a_masked_zip_area": lambda word: False},
    "zip3: NNNxx": {"_a_masked_zip_area": lambda word: False},
    **{family: {"_letters_beside_figures": lambda word: False} for family in _CODE_SHAPED},
    "record: NNN-NNN": {"_names_under": _the_builds_names_under},
}


@pytest.mark.parametrize("family", sorted(_stat_families(random.Random(0))))
def test_the_statisticians_families_land_where_the_screen_puts_them(family: str) -> None:
    landing = _STAT_LANDING.get(family, "refused")
    draw = random.Random(20261109 + sorted(_stat_families(random.Random(0))).index(family))
    make = _stat_families(draw)[family]
    spellings = sorted({make() for _ in range(400)})  # type: ignore[operator]
    texts = [word for word, cell in zip(spellings, taxonomy._classify_all(spellings)) if cell.kind == "text"]

    def case() -> None:
        for word in texts:
            unanswered = _named_alone(taxonomy.HELD_BACK_NAMED_SCREENED, word)
            after_no = _named_alone(taxonomy.HELD_BACK_NAMED_ANSWERED, word)
            net = taxonomy.passes_the_word_screen(word, False)
            if landing == "refused":
                assert not unanswered and not after_no and not net, word
            elif landing == "(ii) refuses":
                assert not unanswered and not after_no, word
            elif landing == "after no":
                assert not unanswered and after_no and net, word
            else:
                assert unanswered and after_no and net, word

    if landing == "limit (a)":
        case()  # the stated limit: named with no question, no rule to remove
        return
    _red_together(case, taxonomy, _STAT_MUTANTS[family])


@pytest.mark.parametrize("rule", ["_a_masked_social_security_number", "_an_image_file_name", "_a_masked_zip_area",
                                  "_an_e_mail_written_with_at"])
def test_rule_8_each_identifier_shape_is_refused_and_red_without_it(rule: str) -> None:
    # The orchestrator's LANE CODES-2 RULINGS 4 (3): the shapes unmistakably an
    # identifier's, tightened after their price on K-HZ-17's code columns was
    # measured (P4-D471), each refused on both roads and red without its rule.
    shaped = {
        "_a_masked_social_security_number": ["XXX-XX-6789", "***-**-1234", "###-##-0001", "SSN 0055", "ssn#4410"],
        "_an_image_file_name": ["face_0012.jpg", "IMG_0008.JPG", "scan.dcm", "photo 12.png"],
        "_a_masked_zip_area": ["522**", "52***", "522xx", "0021X"],
        "_an_e_mail_written_with_at": ["jsmith at wellbrook.org", "a lee at example.com"],
    }[rule]

    def case() -> None:
        for word in shaped:
            assert not taxonomy.passes_the_word_screen(word, False), word
            assert not taxonomy._names_under(taxonomy.HELD_BACK_NAMED_ANSWERED, (word,), False, True, False), word

    _red(case, taxonomy, rule, lambda word: False)


def test_the_word_screen_passes_a_lone_name_the_stated_residual() -> None:
    # What the screen cannot tell, stated in its docstring and P4-D471's limit
    # (a): a lone one- or two-word name typed into a measurement column, or a
    # bare host name, has no shape; initials with a point (rule (7)) do.
    assert taxonomy.passes_the_word_screen("Wellbrook")
    assert taxonomy.passes_the_word_screen("Dr Wellbrook") and taxonomy.passes_the_word_screen("Elm Street")
    assert taxonomy.passes_the_word_screen("wellbrook.org")
    assert not taxonomy.passes_the_word_screen("J. Wellbrook")
    assert not taxonomy.passes_the_word_screen("called to J. Wellbrook RN")
    # ...and the all-or-none price, stated: metric acuity `6/9` and `6/12`
    # read as a month and a day, so a column holding one names none even
    # after `no` (skeptic 1's item 7).
    assert not taxonomy.passes_the_word_screen("6/12") and not taxonomy.passes_the_word_screen("6/9")
    assert taxonomy.passes_the_word_screen("20/40") and taxonomy.passes_the_word_screen("6/60")


# -- rule U (c) and HX's hold --------------------------------------------------


def test_no_name_while_an_identifier_question_is_open_or_the_column_is_held() -> None:
    def case() -> None:
        here = profile._held_back_named_here
        assert here("c", ["c"], True, [], [], None, True) == taxonomy.HELD_BACK_NAMED_ANSWERED
        assert here("c", ["c"], False, [], [], None, True) == ""
        assert here("c", ["c"], True, ["c"], [], None, True) == ""
        assert here("c", ["c"], True, [], ["c"], None, True) == ""
        assert here("c", [], True, [], [], None, True) == taxonomy.HELD_BACK_NAMED_SCREENED
        assert here("c", ["c"], True, [], [], ("d",), True) == ""
        # ...and the command's rule reaches the owner's floor only: below it
        # the library describes as before (point (3) amended).
        assert here("c", ["c"], True, [], [], None, False) == ""
        assert here("c", [], True, [], [], ("c",), False) == taxonomy.HELD_BACK_NAMED_CHECKED

    def released_always(name: str, answered: "list[str]", released: bool, held: "list[str]",
                        identifiers: "list[str]", checked: "tuple[str, ...] | None", floor: bool) -> str:
        return taxonomy.HELD_BACK_NAMED_ANSWERED if name in answered else taxonomy.HELD_BACK_NAMED_SCREENED

    _red(case, profile, "_held_back_named_here", released_always)


_REAL_NAMED_HERE = profile._held_back_named_here


def _route_table(folder: pathlib.Path) -> "object":
    """600 rows read as a table: a key of one value a row beside a route of three common and three rare levels."""
    lines = ["visit_ref,route"]
    rare = ["PR"] * 5 + ["TOP"] * 3 + ["NG"]
    for index in range(600):
        route = rare[index] if index < len(rare) else ("PO", "IV", "SC")[index % 3]
        lines += [f"V{7000000 + index},{route}"]
    path = fixtures.write(folder, "routes.csv", "\n".join(lines) + "\n")
    return reading.read_table(str(path), small_cell_floor=FLOOR)


def _route_names(table: "object", **given: "object") -> "list[str]":
    """The route's held-back names in the description `build_document` writes, under ``given``."""
    document = profile.build_document(table, SETTINGS, [], **given)  # type: ignore[arg-type]
    block = next(column for column in document["columns"] if column["name"] == "route")  # type: ignore[union-attr, index]
    return list(block.get("held_back_names", []))


def test_rule_u_c_through_the_describe_names_nothing_while_an_identifier_question_is_open(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    # SKEPTIC 1'S ITEM 3 (mW1 left the gate green): rule U (c) as WIRED, through
    # `profile.build_document`, the owner's condition "never while the person or
    # identifier question is unanswered". The command passes
    # `rare_values_released` False while a question offering `identifier` is
    # open (`cli._run_profile_body`); a route answered `no` then names nothing.
    # The table is 600 rows read with the floor's row count lowered to it, a
    # test device for speed (LANE I4m RULINGS 18 (4)); the gate's case at the
    # floor runs the same rule at 20,000 rows through the command.
    monkeypatch.setattr(parsing, "TABLE_ROW_FLOOR", 600)
    table = _route_table(tmp_path)

    def case() -> None:
        assert _route_names(table, safe_harbor_no=["route"], rare_values_released=False) == []
        # ...and released, the same `no` names the three: the case reads the road.
        assert _route_names(table, safe_harbor_no=["route"], rare_values_released=True) == ["NG", "PR", "TOP"]

    def released_always(name: str, answered: "list[str]", released: bool, *rest: "object") -> str:
        return _REAL_NAMED_HERE(name, answered, True, *rest)  # type: ignore[arg-type]

    _red(case, profile, "_held_back_named_here", released_always)


def test_rule_u_c_through_the_describe_names_nothing_of_a_column_an_open_question_holds(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    # ...and a column in `unanswered` (its own question open, HX's hold) names
    # nothing whatever else is answered (skeptic 1's item 3, its second case).
    # The hold is guarded twice: the describe reads a held column under no
    # naming at all (`described_from`'s `held`), and `_held_back_named_here`
    # names nothing of a column in the held list -- so the mutant of the list
    # alone leaves the case green (measured), and the mutant the skeptic named,
    # the describe reading `withheld_names` as empty, is the case's red: the
    # column then described as if no question held it.
    monkeypatch.setattr(parsing, "TABLE_ROW_FLOOR", 600)
    table = _route_table(tmp_path)

    def case(withheld: "list[str]") -> None:
        assert _route_names(table, safe_harbor_no=["route"], unanswered=withheld) == []

    case(["route"])
    with pytest.raises(AssertionError):
        case([])  # MUTANT: `withheld_names` read as []

    def held_ignored(name: str, answered: "list[str]", released: bool, held: "list[str]", *rest: "object") -> str:
        return _REAL_NAMED_HERE(name, answered, released, [], *rest)  # type: ignore[arg-type]

    with _mutant(profile, "_held_back_named_here", held_ignored):
        case(["route"])  # the second guard alone still holds it


# -- the loader ----------------------------------------------------------------


def _label_block(names: "list[str]", suppressed: int, rows: int, scale: "dict[str, object] | None" = None) -> dict:
    return {
        "held_back_names": names,
        "suppressed_numbers": scale if scale is not None else {"n_cells": 0, "mean": None},
    }


def test_the_loader_refuses_a_named_pool_that_does_not_add_up() -> None:
    entries = (contract.LevelEntry("po", 50, {"PO": 50}, {}, 0),)
    good = contract._held_back_names(_label_block(["PR", "TOP"], 2, 4), "c", entries, 2, 4)
    assert good == ("PR", "TOP")
    for block, suppressed, rows in (
        (_label_block(["TOP", "PR"], 2, 4), 2, 4),  # B4f: not sorted
        (_label_block(["PR", "PR"], 1, 4), 1, 4),  # B4f: twice
        (_label_block(["PR", "Po"], 2, 4), 2, 4),  # B4g: a published level
        (_label_block(["PR"], 2, 4), 2, 4),  # B4g: a held-back level unnamed
        (_label_block(["PR", "TOP"], 2, 1), 2, 1),  # B4g: more names than rows
        (_label_block(["PR", "TOP"], 2, 4, {"n_cells": 3, "mean": 2.0}), 2, 4),  # B4h: a scale
        (_label_block(["", "PR"], 2, 4), 2, 4),  # a blank name
    ):
        with pytest.raises(Exception) as refused:
            contract._held_back_names(block, "c", entries, suppressed, rows)
        assert "ProfileError" in type(refused.value).__name__
    # A pool counted in people is refused where the reader holds the key
    # beside the names (`_a_pool_in_people_names_none`), through the whole
    # loader below (Codex's item 4): the mapping this check is handed never
    # carries `pool_in_people`.


# -- the twin and the oracle ---------------------------------------------------


def _pool_block(names: "list[str]", rows: int, n_numeric: int = 0) -> "types.SimpleNamespace":
    """What the named pool's writer reads of a column: its counts of numbers and its pool."""
    facts = types.SimpleNamespace(held_back_names=tuple(sorted(names)), suppressed_rows=rows)
    return types.SimpleNamespace(
        name="c", n_numeric=n_numeric, n_out_of_range=0, n_contradictory=0, facts=facts
    )


def test_the_twin_writes_every_name_and_the_pool_total_and_the_oracle_agrees() -> None:
    sys.path.insert(0, str(ROOT / "tools" / "reference"))
    import make_generation_reference_vectors as oracle

    draw = random.Random(11)
    for trial in range(300):
        count = draw.randint(1, 40)
        names = sorted({f"{_word(draw)}{trial}-{place}" for place in range(count)})
        numbers = sorted({f"{draw.randint(1, 999)}" for _ in range(draw.randint(0, 6))} - set(names))
        every = sorted(names + numbers)
        rows = len(every) + draw.randint(0, 9 * len(every))
        number_rows = len(numbers) + (draw.randint(0, 9 * len(numbers)) if numbers else 0)
        number_rows = min(number_rows, rows - len(names)) if names else rows
        column = _pool_block(every, rows, n_numeric=number_rows)
        cells, fit = generation._with_named_pool(
            column, column.facts, ["PO"] * 400 + ["IV"] * 300, False, FLOOR  # type: ignore[arg-type]
        )
        written = cells[700:]
        assert len(written) == rows, trial
        assert sorted(set(written)) == every, trial
        held: "dict[str, int]" = {}
        for cell in written:
            held[cell.casefold()] = held.get(cell.casefold(), 0) + 1
        assert max(held.values()) < FLOOR or not fit, trial
        assert sum(1 for cell in written if cell in numbers) == number_rows or not fit, trial
        mirrored = oracle.named_pool_cells(
            {"held_back_names": every, "suppressed_rows": rows, "n_numeric": number_rows, "n_out_of_range": 0,
             "n_contradictory": 0}, ["PO"] * 400 + ["IV"] * 300, FLOOR,
        )
        assert mirrored == written, trial


# -- Codex's items 2 to 5 on the build (the orchestrator's LANE CODES-2 RULINGS 6 (2), (3)) --


def _the_builds_with_named_pool(
    column: "object", facts: "object", written: "list[str]", decimal_comma: bool, floor: int
) -> "tuple[list[str], bool]":
    """The build's writer, word for word: the search from the class's first name, the floor judged as it went."""
    owed = generation._classes_owed(column, written, decimal_comma)  # type: ignore[arg-type]
    debt_of = {parsing.NUMBER: "n", parsing.NUMBER_OUT_OF_RANGE: "o", parsing.NUMBER_CONTRADICTORY: "c"}
    order = ("n", "o", "c", "t")
    members: "dict[str, list[str]]" = {key: [] for key in order}
    for name in facts.held_back_names:  # type: ignore[attr-defined]
        found = parsing.classify_number(generation._read_in_grammar(name, decimal_comma))
        members[debt_of[found] if found in debt_of else "t"] += [name]
    keyed = {"n": generation._OWED_NUMBER, "o": generation._OWED_OUT_OF_RANGE, "c": generation._OWED_CONTRADICTORY}
    debts = {key: max(0, owed[keyed[key]]) for key in ("n", "o", "c")}
    left = facts.suppressed_rows - sum(debts.values())  # type: ignore[attr-defined]
    debts["t"] = max(0, left)
    fit = left >= 0
    sizes: "dict[str, int]" = {}
    for key in order:
        names = members[key]
        if not names:
            fit = fit and debts[key] == 0
            continue
        if debts[key] < len(names):
            fit = False
        each, odd = divmod(max(debts[key], len(names)), len(names))
        for place in range(len(names)):
            sizes[names[place]] = each + (1 if place < odd else 0)
    if floor > 1:
        held: "dict[str, int]" = {}
        for name in sorted(sizes):
            held[parsing.folded(name)] = held.get(parsing.folded(name), 0) + sizes[name]
        for key in order:
            for name in members[key]:
                level = parsing.folded(name)
                past = min(held[level] - (floor - 1), sizes[name] - 1)
                for other in members[key]:
                    if past <= 0:
                        break
                    room = (floor - 1) - held[parsing.folded(other)]
                    if other == name or room <= 0:
                        continue
                    moved = min(room, past)
                    sizes[name] -= moved
                    sizes[other] += moved
                    held[level] -= moved
                    held[parsing.folded(other)] += moved
                    past -= moved
                if held[level] >= floor:
                    fit = False
    cells = list(written)
    for name in facts.held_back_names:  # type: ignore[attr-defined]
        cells += [name] * sizes[name]
    return cells, fit


# Codex's item 3, at the gate's 600 rows: ten case spellings of one level on a
# row each and ten levels of ten rows, beside one common level.
_CASE_SPELLINGS = ("ABCD", "ABCd", "ABcD", "AbCD", "aBCD", "ABcd", "AbCd", "aBCd", "abCD", "abcd")


def _spelled_pool_table(folder: pathlib.Path) -> "object":
    cells = list(_CASE_SPELLINGS) + [f"Z{figure}" for figure in range(10) for _ in range(10)]
    cells += ["COMMON"] * (600 - len(cells))
    path = fixtures.write(folder, "spelled.csv", "c\n" + "".join(f"{cell}\n" for cell in cells))
    return reading.read_table(str(path), small_cell_floor=FLOOR)


def _spelled_pool_described(folder: pathlib.Path) -> "tuple[pathlib.Path, dict]":
    """The pool of `_spelled_pool_table` named after `no` (path (iii)), its description written and read back."""
    document = profile.build_document(_spelled_pool_table(folder), SETTINGS, [], safe_harbor_no=["c"])  # type: ignore[arg-type]
    path = fixtures.write_profile(folder, "spelled-profile.json", document)
    return pathlib.Path(path), json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def test_the_named_pool_judges_its_completed_allocation_and_writes_every_pooled_row(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Codex's item 3: the producer, the loader and the writer give exactly the
    # pool, every level under the floor, every name present -- and the build
    # called it a false deviation, judging each level before later names had
    # moved rows off it.
    monkeypatch.setattr(parsing, "TABLE_ROW_FLOOR", 600)
    path, document = _spelled_pool_described(tmp_path)
    block = next(column for column in document["columns"] if column["name"] == "c")
    assert len(block["held_back_names"]) == 20
    loaded = contract.load_profile(str(path))
    column = next(each for each in loaded.columns if each.name == "c")

    def case() -> None:
        cells, fit = generation._with_named_pool(column, column.facts, ["COMMON"] * 490, False, FLOOR)  # type: ignore[arg-type]
        assert fit
        assert len(cells) == 600
        pooled: "dict[str, int]" = {}
        for cell in cells[490:]:
            pooled[parsing.folded(cell)] = pooled.get(parsing.folded(cell), 0) + 1
        assert sorted(set(cells[490:])) == sorted(block["held_back_names"])
        assert max(pooled.values()) == FLOOR - 1 and len(pooled) == 11

    _red(case, generation, "_with_named_pool", _the_builds_with_named_pool)


def _codex_item_2_pool(count: int) -> "types.SimpleNamespace":
    """Codex's item 2: for each of ``count`` figures, four case spellings on a row each and one name on ten rows."""
    names: "list[str]" = []
    for place in range(count):
        names += [f"AA{place:06d}", f"Aa{place:06d}", f"aA{place:06d}", f"aa{place:06d}", f"Z{place:06d}"]
    return _pool_block(names, 14 * count)


def test_the_named_pool_moves_its_rows_past_the_floor_in_one_pass_and_writes_the_builds_twin() -> None:
    # Codex's item 2 (G4, time first): the build searched again from the
    # class's first name for every level over the line, so doubling the pool
    # about quadrupled the work. Counted, not timed: the folds the writer
    # asks at 400 and 800 figures (2,000 and 4,000 names) grow by the
    # doubling (within ten per cent), and by about four on the build's search.
    def folds(count: int) -> int:
        column = _codex_item_2_pool(count)
        asked = [0]
        real = parsing.folded

        def counted(text: str) -> str:
            asked[0] += 1
            return real(text)

        with _mutant(parsing, "folded", counted):
            generation._with_named_pool(column, column.facts, [], False, FLOOR)  # type: ignore[arg-type]
        return asked[0]

    def case() -> None:
        assert folds(800) <= 2.2 * folds(400)

    _red(case, generation, "_with_named_pool", _the_builds_with_named_pool)
    # ...AND THE SAME TWIN AS THE BUILD'S, byte for byte, on every pool the
    # build wrote whole: generated pools of case spellings of one level, levels
    # of several rows, words and numbers, each read by both writers.
    draw = random.Random(20261110)
    for trial in range(300):
        names: "list[str]" = []
        for place in range(draw.randint(1, 12)):
            stem = f"{_word(draw)}{place}"
            for flip in range(draw.randint(1, 4)):
                names += [stem.upper() if flip == 1 else stem.capitalize() if flip == 2 else stem.swapcase() if flip == 3 else stem]
        numbers = sorted({f"{draw.randint(1, 999)}" for _ in range(draw.randint(0, 4))})
        every = sorted(set(names) | set(numbers))
        rows = len(every) + draw.randint(0, 6 * len(every))
        number_rows = len(numbers) + (draw.randint(0, 3 * len(numbers)) if numbers else 0)
        number_rows = min(number_rows, rows - (len(every) - len(numbers)))
        column = _pool_block(every, rows, n_numeric=number_rows)
        mine = generation._with_named_pool(column, column.facts, ["PO"] * 40, False, FLOOR)  # type: ignore[arg-type]
        builds = _the_builds_with_named_pool(column, column.facts, ["PO"] * 40, False, FLOOR)
        assert mine[0] == builds[0], trial


def test_the_whole_loader_refuses_a_pool_whose_names_and_counts_disagree_or_one_counted_in_people(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Codex's items 4 and 5, through `contract.load_profile`, each red on its
    # mutant. Item 5: `Z0` replaced by `1` beside a published count of no
    # number -- the build loaded it and wrote 601 cells for 600 rows before
    # an internal error; now refused with B4g, and no writer path writes a
    # different total. Item 4: `pool_in_people` beside the named pool -- the
    # outer reader took the key off before the check saw it.
    monkeypatch.setattr(parsing, "TABLE_ROW_FLOOR", 600)
    path, document = _spelled_pool_described(tmp_path)

    def edited(change: "object") -> pathlib.Path:
        copied = json.loads(json.dumps(document))
        block = next(column for column in copied["columns"] if column["name"] == "c")
        change(block)  # type: ignore[operator]
        return pathlib.Path(fixtures.write_profile(tmp_path, "edited-profile.json", copied))

    def one_for_z0(block: dict) -> None:
        block["held_back_names"] = sorted("1" if name == "Z0" else name for name in block["held_back_names"])

    def counted_in_people(block: dict) -> None:
        block["pool_in_people"] = {"number_from": "", "word_from": "ZZ"}

    def refused(change: "object") -> None:
        try:
            contract.load_profile(str(edited(change)))
        except Exception as caught:  # noqa: BLE001 - the refusal is read whole
            assert "B4g" in str(caught)
            return
        raise AssertionError("the edited description was loaded")

    _red(lambda: refused(one_for_z0), contract, "_named_pools_add_up", lambda columns, settings: None)
    _red(lambda: refused(counted_in_people), contract, "_a_pool_in_people_names_none", lambda facts, where: None)
    # ...AND WITH THE LOADER'S CHECK GONE, THE WRITER STILL WRITES NO OTHER
    # TOTAL: its internal check stops it (synthtwin's own mistake, reported).
    with _mutant(contract, "_named_pools_add_up", lambda columns, settings: None):
        loaded = contract.load_profile(str(edited(one_for_z0)))
    column = next(each for each in loaded.columns if each.name == "c")
    with pytest.raises(Exception) as stopped:
        generation._with_named_pool(column, column.facts, ["COMMON"] * 490, False, FLOOR)  # type: ignore[arg-type]
    assert "internal check" in str(stopped.value)


# -- the measuring tool (Codex's item 6, the orchestrator's LANE CODES-2 RULINGS 6 (4)) --


def _rare_names_driver(monkeypatch: pytest.MonkeyPatch) -> "types.ModuleType":
    """tools/measurements/kpi_rare_names.py, imported as a module of its folder."""
    import importlib

    monkeypatch.syspath_prepend(str(ROOT / "tools" / "measurements"))
    monkeypatch.delitem(sys.modules, "kpi_rare_names", raising=False)
    return importlib.import_module("kpi_rare_names")


def test_the_driver_stops_on_a_twin_missing_a_column_a_failed_generate_or_a_rare_level(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Codex's probes, each read by the driver as nothing before this repair:
    # a twin with its `flow_key` removed (the closed-list check iterated an
    # empty list: 2,185 offending cells read as 0), a generate that exited 1
    # with no twin (zero exposure counted), and a rare spelling published as
    # a level (`_blocks` set the levels aside unread). Each now stops the
    # driver or is counted, red on the mutant that drops its check.
    driver = _rare_names_driver(monkeypatch)
    monkeypatch.setattr(driver, "ROWS", 40)
    header = ["visit_ref", "dx_code", "flow_key"]
    rows = [[f"V{index}", ("A10.1", "B20.2")[index % 2], ("F1", "F2")[index % 2]] for index in range(40)]

    def run_table(table: object, home: pathlib.Path, *rest: object, **given: object) -> dict:
        home.mkdir(parents=True, exist_ok=True)
        blocks = [{"name": name, "role": "categorical"} for name in header]
        (home / "fake-profile.json").write_text(json.dumps({"columns": blocks}), encoding="utf-8", newline="\n")
        kept = header[:2] if table.drop else header  # type: ignore[attr-defined]
        # ...a whole twin from an earlier run stands where `stale` says so,
        # though this generate exited 1 (the verify of repair 2, item 6).
        if table.exit == 0 or table.stale:  # type: ignore[attr-defined]
            lines = [",".join(kept)] + [",".join(row[: len(kept)]) for row in rows]
            (home / "fake-twin.csv").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        return {"steps": {"generate": {"exit": table.exit}}, "asked": [], "leaks": {}}  # type: ignore[attr-defined]

    def table(drop: bool, code: int, stale: bool = False) -> "types.SimpleNamespace":
        made = types.SimpleNamespace(name="fake", suffix=".csv", kinds={"key_value_answers": ("dx_code", "flow_key")},
                                     build=lambda n, seed: (header, rows), drop=drop, exit=code, stale=stale)
        made.read = lambda path: {"raw": _Frame(_cells_from(path))}
        return made

    monkeypatch.setattr(driver.health_zoo, "run_table", run_table)
    monkeypatch.setattr(driver.health_zoo, "runnable_tables", lambda tables: tables)
    monkeypatch.setattr(driver.health_zoo, "seed_of", lambda table: 0)
    monkeypatch.setattr(driver.health_zoo, "names_a_safe_harbor_element", lambda table, column: False)

    def stops(dropped: bool, code: int, stale: bool = False) -> None:
        monkeypatch.setattr(driver.health_zoo, "catalogue", lambda: (table(dropped, code, stale),))
        try:
            driver.closed_list(tmp_path / f"zoo-{dropped}-{code}-{stale}")
        except driver.RunNotComplete:
            return
        raise AssertionError("the driver read an incomplete run")

    monkeypatch.setattr(driver.health_zoo, "catalogue", lambda: (table(False, 0),))
    assert driver.closed_list(tmp_path / "zoo-whole")["failing"] == {}
    _red(lambda: stops(True, 0), driver, "_complete_columns", lambda *given: None)

    def generate_gone() -> None:
        try:
            stops(False, 1)
        except FileNotFoundError as missing:  # the twin read with no check before it
            raise AssertionError("read past a failed generate") from missing

    _red(generate_gone, driver, "_generated", lambda *given: None)

    # ...AND A FAILED GENERATE BESIDE A WHOLE STALE TWIN STOPS IT TOO (the verify
    # of repair 2, item 6: with the exit check gone, MC6a, the twin check alone
    # stopped the probe above, so no case was red on it): red on MC6a.
    def the_twin_check_alone(exit_code: object, twin_path: pathlib.Path, where: str) -> None:
        if not twin_path.is_file():
            raise driver.RunNotComplete(where)

    _red(lambda: stops(False, 1, True), driver, "_generated", the_twin_check_alone)
    # ...AND A RARE SPELLING PUBLISHED AS A LEVEL IS COUNTED, under the floor
    # or not; the top-code's own `90` is the one pooled spelling set aside.
    described = tmp_path / "levels-profile.json"
    described.write_text(json.dumps({"columns": [{"name": "c", "levels": [
        {"label": "Alpha group", "count": 4000, "variants": {"ALPHA group": 12}},
        {"label": "REC 1234", "count": 3},
        {"label": "90", "count": 40},
    ]}]}), encoding="utf-8", newline="\n")
    levels = driver._levels_published(described)["c"]
    assert driver.rare_as_levels(levels, {"REC 1234", "90"}, FLOOR) == 1
    assert driver.rare_as_levels(levels, {"Alpha group"}, FLOOR) == 2  # the level under the floor counts always
    assert driver.rare_as_levels({"Alpha group": 4000, "90": 40}, {"REC 1234", "90"}, FLOOR) == 0
    # ...the top-code's pooled category in the source's form is no rare age; a level of 95 is.
    assert driver.rare_as_levels({"90 years": 40, "90 yrs": 12, "90 y": 11}, {"90 years", "90 yrs", "90 y"}, FLOOR) == 0
    assert driver.rare_as_levels({"95 years": 40}, {"95 years"}, FLOOR) == 1


class _Frame:
    """A twin read as the zoo's readers read one: its column names, and each column's cells as a list."""

    def __init__(self, cells: "dict[str, list[str]]") -> None:
        self.columns = list(cells)
        self._cells = cells

    def __getitem__(self, name: str) -> "types.SimpleNamespace":
        return types.SimpleNamespace(tolist=lambda: list(self._cells[name]))


def _cells_from(path: pathlib.Path) -> "dict[str, list[str]]":
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    return {name: [row[place] for row in rows[1:]] for place, name in enumerate(rows[0])}


# -- a held column's layouts, met (the verify of repair 1, item 2) -----------------


def _held_surnames_at_the_floor() -> "list[str]":
    """The floor table's surname column (`at_the_floor_table`, its one source), 20,000 cells."""
    _header, table = at_the_floor_table(20_000, 20261109)
    return [row[3] for row in table]


def test_a_held_surname_column_wears_every_layout_it_publishes(tmp_path: pathlib.Path) -> None:
    # The surname a `yes` to the lane's question holds is described as a held
    # block: its repetition census made up (seven groups, 2 to 5,024 rows),
    # its layouts published exactly (`@&&&&&` 9,935, `@&&&&&&` 5,024,
    # `@&&&&&&&` 5,039). The writer's layout packing found the twin that
    # wears them only at its seventeenth question, past its bound of
    # sixteen, so the twin wore `@&&&&&` on 5,833 cells and validate exited
    # 3 at 20,000 rows; the same column held on the base missed the same
    # three. Red on the bound of sixteen.
    path = fixtures.write(tmp_path, "names.csv", fixtures.single_column_table("surname", _held_surnames_at_the_floor()))
    document = profile.build_document(reading.read_table(str(path)), SETTINGS, [], unanswered=["surname"])  # type: ignore[arg-type]
    column = contract.load_profile(str(fixtures.write_profile(tmp_path, "names-profile.json", document))).columns[0]
    facts = column.facts
    assert isinstance(facts, contract.IdentifierFacts)
    groups = generation._groups_of(facts.n_distinct_by_occurrences)
    convention = generation._layout_convention(facts)

    def case() -> None:
        cells, _notes = generation._identifier_cells(column, groups, (), FLOOR)
        worn: "dict[str, int]" = {}
        for cell in cells:
            form = parsing.layout_form(cell, convention)
            worn[form] = worn.get(form, 0) + 1
        for layout in generation._named_layouts(facts):
            assert worn.get(layout, 0) == facts.layout_forms[layout], (layout, worn)

    _red(case, generation, "_LAYOUT_PACKED_QUESTIONS_FEW_GROUPS", 16)


# -- lane CODES-3's mutants M2, R4 and M4, carried to this lane --------------------


def test_codes_3s_uid_root_caps_each_red_on_its_mutant() -> None:
    # The orchestrator's LANE CODES-2 RULINGS 1 (4): CODES-3's mutants M2 (a
    # cap of four arcs after the organisation arc), R4 (the cap without an
    # organisation arc applied one arc late) and the rewritten M4 (no
    # `2.16.840.1.` branch) were red on no case at today's code. Each shape
    # below is 20,000 instance UIDs of one study, read by `parsing.uid_root`
    # as the describe reads such a column; the root it publishes is the
    # organisation's, never a study arc, and each cap is red without itself.
    shapes = {
        "M2": ([f"1.2.840.113619.2.55.3.4.{k}" for k in range(1, 20001)], "1.2.840.113619.2.55.3."),
        "R4": ([f"1.2.276.0.12.34.56.{k}" for k in range(1, 20001)], "1.2.276.0.12."),
        "M4": ([f"2.16.840.1.113883.6.96.{k}" for k in range(1, 20001)], "2.16.840.1.113883.6.96."),
    }
    mutants = {
        "M2": ("_ARCS_AFTER_THE_ORGANISATION_AT_MOST", 4),
        "R4": ("_ARCS_WITHOUT_AN_ORGANISATION_AT_MOST", 6),
        "M4": ("_ORGANISATION_BRANCHES", (parsing._ANSI_BRANCH,)),
    }
    for mutant, (values, root) in shapes.items():

        def case() -> None:
            assert parsing.uid_root(values) == root, mutant  # noqa: B023 - read at once, in this pass

        name, value = mutants[mutant]
        _red(case, parsing, name, value)


# -- rule U (c)'s trigger in the command (the verify of repair 1, item 8) ------


def test_the_command_describes_again_naming_nothing_while_a_dates_question_offering_identifier_is_open(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    # M26 left the gate green: the command's re-describe condition names
    # `names_published`, so a table whose ONLY open question offering
    # `identifier` is a dates question (twelve figures, a day and a clock
    # read as a date; `identities_open`'s loop admits it, and no hold lists
    # the column) describes again with nothing named while a result column's
    # words would be named. At the gate's 600 rows with the floor's row count
    # lowered to them (a test device, LANE I4m RULINGS 18 (4)).
    monkeypatch.setattr(parsing, "TABLE_ROW_FLOOR", 600)
    draw = random.Random(20261112)
    source = tmp_path / "stamps.csv"
    with source.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["stamp", "result"])
        for index in range(600):
            stamp = f"2024{draw.randint(1, 12):02d}{draw.randint(1, 28):02d}{draw.randint(0, 23):02d}{draw.randint(0, 59):02d}"
            result = ("HI", "HI", "LO", "TNP")[index] if index < 4 else (
                f"{draw.uniform(1, 400):.2f}" if index % 5 else draw.choice(("QNS", "Pending")))
            writer.writerow([stamp, result])

    def case() -> None:
        assert _run(["profile", str(source), "--replace"], False) == 0
        document = json.loads((tmp_path / "stamps-profile.json").read_text(encoding="utf-8"))
        result = next(column for column in document["columns"] if column["name"] == "result")
        assert "held_back_names" not in json.dumps(result)

    case()
    # The table reaches the term: the stamp's question offers `identifier`,
    # and with every question answered no pool is held back from naming.
    asked = json.loads((tmp_path / "stamps-questions.json").read_text(encoding="utf-8"))
    offered = [[f"{choice.get('answer')}" for choice in entry["answers_you_can_give"]] for entry in _entries(asked)
               if entry.get("column") == "stamp"]
    assert any("identifier" in choices for choices in offered), offered

    def without_the_lanes_term(identities_open: bool, rare_listed: "list[str]", levels_pooled: "list[str]",
                               names_published: "list[str]") -> bool:
        return identities_open and bool(rare_listed or levels_pooled)

    _red(case, cli, "_released_while_a_question_is_open", without_the_lanes_term)


# -- through the commands a person types ----------------------------------------


def _run(arguments: "list[str]", floor_on: bool) -> int:
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        return int(cli.main(arguments, small_tables_refused=floor_on))


def _answer_rounds(
    source: pathlib.Path, folder: pathlib.Path, answers: "dict[str, str]", floor_on: bool, declared: "tuple[str, ...]" = ()
) -> None:
    """profile, then each round's questions answered as the person would, at most five rounds; ``declared`` the
    options every profile run takes (`--code` and a column's name)."""
    assert _run(["profile", str(source), "--replace", *declared], floor_on) == 0
    questions = folder / f"{source.stem}-questions.json"
    for _round in range(5):
        document = json.loads(questions.read_text(encoding="utf-8"))
        fresh = 0
        for entry in _entries(document):
            if f"{entry.get('your_answer') or ''}":
                continue
            offered = [f"{choice.get('answer')}" for choice in entry["answers_you_can_give"]]
            column = f"{entry.get('column', '')}"
            wanted = answers.get(column, "")
            # A Safe Harbor question offers `no` and `yes` (an age's also its
            # units, lane SH3): answered by the column's `harbor` answer.
            if "no" in offered and "yes" in offered:
                wanted = answers.get(f"{column} harbor", "")
            if wanted in offered:
                entry["your_answer"] = wanted
                fresh = fresh + 1
        if not fresh:
            return
        questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
        assert _run(["profile", str(source), "--replace", "--answers", str(questions), *declared], floor_on) == 0


def _entries(document: dict) -> "list[dict]":
    found: "list[dict]" = []
    for key in ("about_your_file", "asked"):
        for entry in document.get(key) or []:
            if isinstance(entry, dict) and "answers_you_can_give" in entry:
                found += [entry]
    for entry in (document.get("checklist") or {}).get("columns") or []:
        if isinstance(entry, dict) and "answers_you_can_give" in entry:
            found += [entry]
    return found


def at_the_floor_table(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """An invented export at the owner's floor: a code long tail, a route, a surname, ZIP codes, a result, an age."""
    draw = random.Random(seed)
    # THE AGE COLUMN DRAWS FROM THE TABLE'S ONE SOURCE (the verify of repair
    # 1, item 2): drawn so, the surname held by its `yes` met none of its
    # three published layouts on the repair 1 head (validate exit 3), which
    # the age's own source had hidden.
    ages = draw
    header = ["visit_ref", "dx_code", "route", "surname", "zip_area", "result", "reported_age"]
    common_codes = [f"{chr(65 + place // 20)}{10 + place % 20}.{place % 9}" for place in range(60)]
    rare_codes = [f"{chr(75 + place // 40)}{50 + place % 40}.{place % 7}" for place in range(160)]
    table: "list[list[str]]" = []
    for index in range(rows):
        table += [[
            f"V{7000000 + index}",
            common_codes[index % len(common_codes)],
            draw.choice(("PO", "PO", "PO", "IV", "IV", "SC")),
            draw.choice(("Corwick", "Dalton", "Ferris", "Holloway")),
            draw.choice(("11001", "11002", "11003", "11004")),
            f"{draw.uniform(1, 400):.2f}" if index % 10 else draw.choice(("QNS", "Pending")),
            # SKEPTIC 1'S ITEM 1 (d) AND (c): an age read to two places, 18 to
            # 99, beside `unknown` and `adult`; its rare words below.
            f"{ages.uniform(18, 99.99):.2f}" if index % 12 else ages.choice(("unknown", "unknown", "adult")),
        ]]
    spot = 1
    for place, code in enumerate(rare_codes):
        for _ in range(1 + place % 4):
            table[spot][1] = code
            spot = spot + 7
    for place, (route, count) in enumerate((("PR", 5), ("TOP", 3), ("NG", 1))):
        for step in range(count):
            table[3 + place * 50 + step * 3][2] = route
    for place, name in enumerate(("Quillford", "Abernath", "Yarrowby")):
        for step in range(2 + place):
            table[11 + place * 60 + step * 5][3] = name
    for place, area in enumerate(("12345", "54321", "60601")):
        for step in range(1 + place):
            table[13 + place * 70 + step * 3][4] = area
    for place, word in enumerate(("TNP", "HI", "LO")):
        for step in range(2 + place):
            table[21 + place * 80 + step * 10][5] = word
    for place, word in enumerate(AGE_WORDS_AT_THE_FLOOR):
        for step in range(1 + place):
            table[25 + place * 90 + step * 12][6] = word
    return header, table


# The age column's rare words (skeptic 1's item 1 (d)): ages past 89 a person
# typed with a mark, and written in words (the verify of repair 1, item 3);
# none is named before the column's own `no`.
AGE_WORDS_AT_THE_FLOOR = ("~95", "101 (est)", "95?", "ninety-five", "hundred+")
# Codex's notes (item 1) run at 20,000 rows in K-HZ-24's driver
# (`kpi_rare_names.codex_notes`): a note of four words makes its column a
# long tail, whose pooled numbers' mean the twin misses on the base too, so
# the case at the floor, which validates at exit 0, does not carry them.


def test_at_the_owner_floor_the_closed_list_analyst_runs_and_no_safe_harbor_column_is_named(
    tmp_path: pathlib.Path,
) -> None:
    # THE ONE 20,000-ROW CASE OF THIS FILE (THE SUITE'S TIME rule), through the
    # commands a person types with the owner's table floor on, answered as
    # the zoo answers, truthfully: the code and the route are no Safe Harbor
    # class (`no`), the surname is (`yes`), and the ZIP codes, answered `code`,
    # are put the Safe Harbor question their hold puts and answered `yes`.
    header, table = at_the_floor_table(20_000, 20261109)
    source = tmp_path / "visits.csv"
    with source.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(table)
    answers = {
        "visit_ref": "identifier", "dx_code": "code", "zip_area": "code", "result": "measurement",
        "dx_code harbor": "no", "route harbor": "no", "surname harbor": "yes", "zip_area harbor": "yes",
        "result harbor": "no",
        # ...and the age, truthfully `yes` (an age past 89): its name makes it
        # ages, so `yes` keeps its top-code (lane SH3) and the column is read
        # with no `no` of its own -- fix (c): no figure word is named.
        "reported_age harbor": "yes",
    }
    _answer_rounds(source, tmp_path, answers, True)
    described = {
        column["name"]: column
        for column in json.loads((tmp_path / "visits-profile.json").read_text(encoding="utf-8"))["columns"]
    }
    # PATH (ii) AT THE FLOOR (the statistics skeptic's item 6): the result's
    # letters are named with no question; the age's words, each holding a
    # figure, are named nowhere, after its `yes` as unanswered.
    assert described["result"]["labels"]["held_back_names"] == ["HI", "LO", "TNP"]
    assert "held_back_names" not in json.dumps(described["reported_age"])
    assert not [word for word in AGE_WORDS_AT_THE_FLOOR if json.dumps(word) in json.dumps(described["reported_age"])]
    real = {name: {row[place] for row in table} for place, name in enumerate(header)}
    rare = {
        name: {value for value in real[name] if sum(1 for row in table if row[header.index(name)] == value) < FLOOR}
        for name in ("dx_code", "route", "surname", "zip_area")
    }
    published = json.dumps(described)
    for name in ("surname", "zip_area"):
        assert not [value for value in rare[name] if f'"{value}"' in published], name
    assert sorted(described["dx_code"]["held_back_names"]) == sorted(rare["dx_code"])
    assert sorted(described["route"]["held_back_names"]) == ["NG", "PR", "TOP"]
    assert _run(["generate", str(tmp_path / "visits-profile.json"), "--replace", "--seed", "0"], True) == 0
    assert _run(["validate", str(tmp_path / "visits-profile.json"), "--replace"], True) == 0
    with (tmp_path / "visits-twin.csv").open(encoding="utf-8", newline="") as handle:
        twin = list(csv.reader(handle))
    for name in ("dx_code", "route"):
        place = twin[0].index(name)
        assert not [row[place] for row in twin[1:] if row[place] not in real[name]], name
    for name in ("surname", "zip_area"):
        place = twin[0].index(name)
        assert not [row[place] for row in twin[1:] if row[place] in rare[name]], name
    place = twin[0].index("reported_age")
    assert not [row[place] for row in twin[1:] if row[place] in AGE_WORDS_AT_THE_FLOOR]

    # ...AND THE SAME TWO COLUMNS RED ON THEIR MUTANT, through the command at
    # 20,000 rows: with every road naming its pool, the first run names the
    # age's words, so the assertion above fails on it (the statistics
    # skeptic's item 6, one mutant; one run, the product's being the case's own).
    sub = tmp_path / "ages.csv"
    with sub.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["result", "reported_age"])
        writer.writerows([row[5:7] for row in table])
    with _mutant(taxonomy, "_names_under", _names_whatever_the_road):
        assert _run(["profile", str(sub), "--replace"], True) == 0
    block = next(
        column for column in json.loads((tmp_path / "ages-profile.json").read_text(encoding="utf-8"))["columns"]
        if column["name"] == "reported_age"
    )
    assert [word for word in AGE_WORDS_AT_THE_FLOOR if json.dumps(word) in json.dumps(block)]


# THE FOLLOW-UP'S CASE AT THE OWNER'S FLOOR (the orchestrator's LANE CODES-2
# RULINGS 8 (2)): through the commands a person types, the shipped floor on,
# a column of numbers with labels whose rare words are month names and ages
# in words, each holding one character that prints nothing, left unanswered,
# and one whose rare words are marked ages and clocks holding one, answered
# `no` wherever the Safe Harbor question is put. On repair 2's head the first
# was named with no question and the second after `no`, and the twin wrote
# both; now neither column names a word and no twin cell equals one.

def _hidden_words_at_the_floor(draw: random.Random) -> "tuple[list[str], list[str]]":
    words: "dict[str, bool]" = {}
    while len(words) < 20:
        # ...each word one run of letters, so the character always splits the
        # word the screen reads (inside `two` of `Ninety-two` it would not).
        spelled = draw.choice((draw.choice(_MONTHS_WHOLE), draw.choice(("ninety", "Ninety", "NINETY", "hundred", "hundred+",
                                                                        "ninety?", "thousand", "centenarian", "nonagenarian"))))
        words[_inside_letters(spelled, draw.choice(_NOTHING_PRINTED_IN_A_CELL), draw)] = True
    marked: "dict[str, bool]" = {}
    while len(marked) < 20:
        age = draw.randint(90, 125)
        spelled = draw.choice((f"{age}+", f"~{age}", f"{age}?", f"{draw.randint(10, 23)}:{draw.randint(10, 59)}"))
        marked[_inside_figures(spelled, draw.choice(_NOTHING_PRINTED_IN_A_CELL), draw)] = True
    return sorted(words), sorted(marked)


def test_at_the_owner_floor_a_character_that_prints_nothing_names_no_word_through_the_commands(
    tmp_path: pathlib.Path,
) -> None:
    draw = random.Random(20261112)
    words, marked = _hidden_words_at_the_floor(draw)
    header = ["visit_ref", "result_words", "marked_result"]
    table = [[f"V{7100000 + index}",
              f"{draw.uniform(1, 400):.2f}" if index % 9 else draw.choice(("QNS", "Pending")),
              f"{draw.uniform(1, 400):.2f}" if index % 9 else draw.choice(("QNS", "Pending"))] for index in range(20_000)]
    spot = 4
    for column, spellings in ((1, words), (2, marked)):
        for place, spelled in enumerate(spellings):
            for _ in range(1 + place % 3):
                table[spot][column] = spelled
                spot = spot + 37
    source = tmp_path / "hidden.csv"
    with source.open("w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(table)
    _answer_rounds(source, tmp_path, {"visit_ref": "identifier", "marked_result harbor": "no"}, True)
    described = {column["name"]: column for column in
                 json.loads((tmp_path / "hidden-profile.json").read_text(encoding="utf-8"))["columns"]}
    assert _run(["generate", str(tmp_path / "hidden-profile.json"), "--replace", "--seed", "0"], True) == 0
    with (tmp_path / "hidden-twin.csv").open(encoding="utf-8", newline="") as handle:
        twin = list(csv.reader(handle))
    for name, spellings in (("result_words", words), ("marked_result", marked)):
        block = json.dumps(described[name], ensure_ascii=False)
        assert not [ascii(word) for word in spellings if json.dumps(word, ensure_ascii=False) in block
                    or json.dumps(word) in block], name
        place = twin[0].index(name)
        assert not [ascii(row[place]) for row in twin[1:] if row[place] in spellings], name

    # ...AND RED ON THE SINGLE READING, through the command at 20,000 rows: read
    # only as a space, the unanswered column's first run names its words (the
    # column alone, so no key's question is open; one run).
    sub = tmp_path / "words.csv"
    with sub.open("w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle)
        writer.writerow(["result_words"])
        writer.writerows([row[1:2] for row in table])
    with _mutant(taxonomy, "_without_what_prints_nothing", lambda text: text):
        assert _run(["profile", str(sub), "--replace"], True) == 0
    block = next(column for column in json.loads((tmp_path / "words-profile.json").read_text(encoding="utf-8"))["columns"]
                 if column["name"] == "result_words")
    assert [word for word in words if json.dumps(word, ensure_ascii=False) in json.dumps(block, ensure_ascii=False)]


# THE MICRO-STEP'S CASE AT THE OWNER'S FLOOR (the orchestrator's LANE CODES-2
# RULINGS 10 (1)): the scoped verify's table, 45 spellings of number words
# glued with `eight` before an end word in `y`, cased and marked as typed, on
# 90 rows beside common values, one column a road: the words of a column of
# numbers with labels left unanswered, and another answered `measurement`
# and `no`; a label column answered `no`; a column declared a code and
# answered `no`. On the follow-up's head each column named all 45 and the
# twin wrote them on 90 cells; now no column names one, nothing the commands
# write holds one, and no twin cell equals one. Its words are written here.

_GLUED_EIGHT_HEADS = ("ninety", "hundred", "onehundred", "ahundred", "hundredand", "onehundredand")
_Y_END_WORDS = ("yo", "yr", "yrs", "year", "years", "yearold", "yearsold")
_COMMON_GROUPS = ("Alpha group", "Beta group", "Gamma group", "Delta group", "Omega group")


def _glued_eights(draw: random.Random) -> "list[str]":
    """45 different spellings of `eight` glued between a head and an end word in `y`, each cased and marked as typed."""
    made: "dict[str, bool]" = {}
    while len(made) < 45:
        spelled = draw.choice(_GLUED_EIGHT_HEADS) + "eight" + draw.choice(_Y_END_WORDS)
        pick = draw.randrange(4)
        if pick == 1:
            spelled = spelled.upper()
        elif pick == 2:
            spelled = spelled.capitalize()
        elif pick == 3:
            spelled = "".join(letter.upper() if draw.random() < 0.5 else letter for letter in spelled)
        made[draw.choice(("", "", "~", ">")) + spelled + draw.choice(("", "", "+", "?"))] = True
    return sorted(made)


def _glued_eights_at_the_floor(seed: int) -> "tuple[list[str], list[list[str]], dict[str, list[str]]]":
    """The table: a key, two columns of numbers with labels and two label columns, each with its own 45 spellings."""
    draw = random.Random(seed)
    header = ["row_ref", "glued_result", "glued_measured", "glued_label", "glued_code"]
    rare = {name: _glued_eights(draw) for name in header[1:]}
    columns: "dict[str, list[str]]" = {}
    for name, spellings in rare.items():
        cells: "list[str]" = []
        for place, spelled in enumerate(spellings):
            cells += [spelled] * (1 + place % 3)
        if name in ("glued_result", "glued_measured"):
            cells += ["TNP"] * 1300 + ["Pending"] * 900
            cells += [f"{draw.uniform(2, 600):.1f}" for _ in range(20_000 - len(cells))]
        else:
            cells += [draw.choice(_COMMON_GROUPS) for _ in range(20_000 - len(cells))]
        draw.shuffle(cells)
        columns[name] = cells
    table = [[f"Q{8100000 + index}"] + [columns[name][index] for name in header[1:]] for index in range(20_000)]
    return header, table, rare


def test_at_the_owner_floor_number_words_glued_with_eight_name_nothing_on_any_road_through_the_commands(
    tmp_path: pathlib.Path,
) -> None:
    header, table, rare = _glued_eights_at_the_floor(20261111)
    assert sum(1 for row in table for cell in row[1:] if cell in rare["glued_result"] + rare["glued_measured"]
               + rare["glued_label"] + rare["glued_code"]) == 4 * 90
    source = tmp_path / "glued.csv"
    with source.open("w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(table)
    answers = {"row_ref": "identifier", "glued_measured": "measurement", "glued_measured harbor": "no",
               "glued_label harbor": "no", "glued_code harbor": "no"}
    _answer_rounds(source, tmp_path, answers, True, ("--code", "glued_code"))
    profile_path = tmp_path / "glued-profile.json"
    assert _run(["generate", str(profile_path), "--replace", "--seed", "0"], True) == 0
    described = {column["name"]: column for column in json.loads(profile_path.read_text(encoding="utf-8"))["columns"]}
    with (tmp_path / "glued-twin.csv").open(encoding="utf-8", newline="") as handle:
        twin = list(csv.reader(handle))
    # Each column's spellings published in its block, and the twin's cells (any column) equal to one of them.
    cells = collections.Counter(cell for row in twin[1:] for cell in row)
    found = {name: (sum(1 for word in rare[name] if json.dumps(word) in json.dumps(described[name])),
                    sum(cells[word] for word in set(rare[name]))) for name in rare}
    assert found == {name: (0, 0) for name in rare}, found
    every = {spelled for spellings in rare.values() for spelled in spellings}
    written = "".join(path.read_text(encoding="utf-8", errors="replace") for path in sorted(tmp_path.iterdir())
                      if path.is_file() and path.name not in ("glued.csv", "glued-twin.csv"))
    assert not [word for word in every if word in written]

    # ...AND RED ON THE GREEDY READ, through the command at 20,000 rows: the
    # unanswered column alone (so no key's question is open), read longest
    # first, names its spellings on its first run (one run).
    sub = tmp_path / "result.csv"
    with sub.open("w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle)
        writer.writerow(["glued_result"])
        writer.writerows([row[1:2] for row in table])
    with _mutant(taxonomy, "_glued_rest_reads", _the_greedy_rest):
        assert _run(["profile", str(sub), "--replace"], True) == 0
    block = next(column for column in json.loads((tmp_path / "result-profile.json").read_text(encoding="utf-8"))["columns"]
                 if column["name"] == "glued_result")
    assert [word for word in rare["glued_result"] if json.dumps(word) in json.dumps(block)]
