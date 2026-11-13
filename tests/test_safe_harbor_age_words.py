"""Ages written with their words: `Age 95`, `age: 95`, `(95 yrs)`, `95 (years)` (lane HB2, plan P4-D477).

The orchestrator's LANE HB2 RULINGS 1 (1) to (4): a label column whose levels
are `Age NN` (ages 18 to 95, one a person) was read as words with no number,
put no Safe Harbor question, published `Age 90` to `Age 95` and wrote them in
its twin; the age reach read a unit word after the number and nothing before
it. `taxonomy.AGE_VOCABULARY` is the one closed list of the words, marks,
brackets and units the reach, its question, the top-code, the validator and
the generator's bound read around one age's number. Every family is closed
by a GENERATED check at the unit level (each word in four cases, each mark
with its spaces, each bracket, each unit word and affix, thousands of
spellings), the words that are no age read as before, product and oracle
alike (A-P4-59); and one table at the owner's floor through the command,
whose 20,000-row legs per family live in `K-HZ-29`'s driver
(`tools/measurements/kpi_age_words.py`; THE SUITE'S TIME rule).
"""

from __future__ import annotations

import contextlib
import csv
import importlib.util
import io
import json
import pathlib
import random

from synthtwin import cli, contract, taxonomy, validation

ROWS = 20_000
PEOPLE = 1_000
CASES = ("lower", "upper", "title", "mixed")
# The spaces and marks a word may stand at before its number.
SEPARATORS = ("", " ", "  ", ":", ": ", " : ", "=", " = ", "-", " - ", ":  ")
# The units after the number and the mark each names (the vocabulary's).
UNITS_AFTER = (
    ("", 90), (" yrs", 90), (" years", 90), ("y", 90), (" Y", 90), (" years old", 90), ("-year-old", 90),
    (" y/o", 90), (" months", 1080), (" mo", 1080), (" m/o", 1080), (" wk", 4695), (" weeks", 4695),
    (" days", 32871), (" d", 32871), (" (years)", 90), (" (months)", 1080), (" [days]", 32871), ("(yrs)", 90),
)
NOT_AGES = ("Stage", "Grade", "Room", "Week", "Score", "Page", "Agent", "Ages", "Aging", "Wage", "MR", "Visit", "Bed")
# THE PRODUCT'S OWN SPACES AND DASHES (lane HB2's repair 1, skeptic 1's item
# 1; LANE HB2 RULINGS 3 (2)). SINCE BATCH 4s'S MERGE they are the product's
# ONE definition (`taxonomy._SCREEN_SPACE_RANGES` and the dashes named beside
# it, `taxonomy._SCREEN_DASHES`; the orchestrator's LANE HB2 RULINGS 7 (3) and
# 8 (3)), held over every code point by the agreement case below. The lane's
# list before the merge, written out: every character Python reads as
# whitespace to U+3000 and seven zero-width and format spaces.
LANE_SPACES_BEFORE = tuple(chr(code) for code in range(0x3001) if chr(code).isspace()) + (
    "\u200b", "\u200c", "\u200d", "\u200e", "\u200f", "\u2060", "\ufeff",
)
ONE_DEFINITION_SPACES = tuple(
    chr(code) for start, end in taxonomy._SCREEN_SPACE_RANGES for code in range(start, end + 1)
)
# ...the spaces the families read in every place of a frame: the lane's list
# and, of each range of the definition, its first and its last code point
# (the controls, the format characters, the soft hyphen and the lone
# surrogate code points among them); the whole definition is read in the
# frame's places by its own case below.
UNICODE_SPACES = LANE_SPACES_BEFORE + tuple(sorted(
    {chr(edge) for start, end in taxonomy._SCREEN_SPACE_RANGES for edge in (start, end)} - set(LANE_SPACES_BEFORE)
))
# ...and the dashes named beside it, written out: the hyphen-minus, the
# hyphen, the non-breaking hyphen, the figure dash, the en and em dashes,
# the horizontal bar, the minus sign, the small em dash and the small and
# full-width hyphen-minus (the soft hyphen, a dash of the identifier forms'
# marks, is a space of the definition, one that prints nothing).
DASHES = ("-", "\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u2015", "\u2212", "\ufe58", "\ufe63", "\uff0d")
# The marks a band opens with after an age word, for the split's generated case.
BANDS = ("90-94", "90 - 94", "90 to 94", "95+", "100+", ">= 95", ">=95", "> 89", "<18", "\u2265 95", "+90", "90")


def _cased(word: str, how: str) -> str:
    if how == "upper":
        return word.upper()
    if how == "title":
        return word.title()
    if how == "mixed":
        return "".join(letter.upper() if place % 2 else letter for place, letter in enumerate(word))
    return word


def _worded(draw: random.Random) -> "list[tuple[str, float, int, str]]":
    """The generated families: (cell, its number, its unit's mark, the cell with the number written as the mark)."""
    found: "list[tuple[str, float, int, str]]" = []
    vocabulary = taxonomy.AGE_VOCABULARY
    for word in vocabulary.before:
        for how in CASES:
            for separator in SEPARATORS:
                for unit, mark in UNITS_AFTER:
                    for frame in ("", "()", "[]", "after"):
                        number = draw.randint(0, 125)
                        written = f"{number:03d}" if draw.random() < 0.1 else f"{number}"
                        inner = f"{written}{unit}"
                        head = f"{_cased(word, how)}{separator}"
                        if frame == "after" and unit[-1:] not in (")", "]"):
                            cell, mark_cell = f"{head}({inner})", f"{head}({{}}{unit})"
                        elif frame in ("()", "[]") and unit[-1:] not in (")", "]"):
                            cell, mark_cell = f"{frame[0]}{head}{inner}{frame[1]}", f"{frame[0]}{head}{{}}{unit}{frame[1]}"
                        else:
                            cell, mark_cell = f"{head}{inner}", f"{head}{{}}{unit}"
                        found += [(cell, float(number), mark, mark_cell)]
    # ...and the bracketed forms with no word: `(95 yrs)`, `95 (years)`.
    for unit, mark in UNITS_AFTER:
        if not unit.strip():
            continue
        for _round in range(4):
            number = draw.randint(0, 125)
            for opening, closing in vocabulary.brackets:
                if unit[-1:] in (")", "]"):
                    found += [(f"{number}{unit}", float(number), mark, f"{{}}{unit}")]
                else:
                    found += [(f"{opening}{number}{unit}{closing}", float(number), mark, f"{opening}{{}}{unit}{closing}")]
    return found


def test_every_generated_age_word_family_is_read_with_its_number() -> None:
    """Each word, case, mark, bracket and unit of the vocabulary: the number read, its unit's mark, the frame kept."""
    draw = random.Random(4771)
    families = _worded(draw)
    assert len(families) > 3000
    for cell, number, mark, _mark_cell in families:
        read = taxonomy.safe_harbor_number(cell, False, True, True)
        assert read is not None, cell
        assert read.value == number, cell
        assert taxonomy.age_mark(read) == mark, cell
        assert read.head + read.number + read.tail == cell, cell
        # ...and with no words, none of them is a number read whole as before.
        before = taxonomy.safe_harbor_number(cell, False)
        assert before is None or before.number != read.number or before.head != read.head or before.tail == read.tail


def _unicode_families(draw: random.Random) -> "list[tuple[str, float, int, str]]":
    """Each listed space and dash in each place of an age word's frame (lane HB2's repair 1): (cell, its number, its unit's mark, the cell with the number written as the mark)."""
    found: "list[tuple[str, float, int, str]]" = []
    places = (
        ("{w}{s}{n}", 90), ("{w}{s}:{n}", 90), ("{w}:{s}{n}", 90), ("{w}{s}={s}{n}", 90), ("{w}{s}-{s}{n}", 90),
        ("({s}{w}{s}{n}{s})", 90), ("[{w}{s}{n}]", 90), ("{w}({s}{n}{s})", 90), ("{w}{s}[{n}]", 90),
        ("{w} {n}{s}yrs", 90), ("{w}{s}{n} months", 1080), ("({n}{s}yrs)", 90), ("{n}{s}(years)", 90),
        ("{s}{w} {n}{s}", 90), ("{w}{s}({n}{s}mo)", 1080),
    )
    for space in UNICODE_SPACES:
        for how in CASES:
            for pattern, mark in places:
                word = _cased(draw.choice(taxonomy.AGE_WORDS_BEFORE), how)
                number = draw.randint(0, 125 if mark == 90 else 1300)
                cell = pattern.format(w=word, s=space, n=number)
                found += [(cell, float(number), mark, pattern.format(w=word, s=space, n="{}"))]
    for dash in DASHES:
        for how in CASES:
            for pattern in ("{w}{d}{n}", "{w} {d} {n}", "{w}\u00a0{d}\u2009{n}", "{w}{d} {n}", "({w}{d}{n})", "{w}{d}({n})",
                            "{w}{d}{n} yrs"):
                word = _cased(draw.choice(taxonomy.AGE_WORDS_BEFORE), how)
                number = draw.randint(0, 125)
                cell = pattern.format(w=word, d=dash, n=number)
                found += [(cell, float(number), 90, pattern.format(w=word, d=dash, n="{}"))]
    return found


def test_every_space_and_dash_of_the_product_is_read_in_each_place_of_the_frame() -> None:
    """Each Unicode space and each dash, between the word and the number, the word and the mark, the mark and the number, inside a bracket, before a unit and at the edges: the number read, its frame kept as written, the top code written in the cell's own characters.

    Red on b61eaa4b, whose reader skipped the ASCII space alone and read
    `:`, `=` and `-` alone as marks: `Age<U+00A0>95`, `Age:<U+2009>95` and
    `Age<U+2013>95` were words, put no question and were published.
    """
    # ...the reader's dashes are the ones named beside the one definition (batch 4s's merge).
    assert set(taxonomy._SCREEN_DASHES) == set(DASHES)
    families = _unicode_families(random.Random(4781))
    assert len(families) > 2000
    for cell, number, mark, mark_cell in families:
        read = taxonomy.safe_harbor_number(cell, False, True, True)
        assert read is not None, repr(cell)
        assert read.value == number and taxonomy.age_mark(read) == mark, repr(cell)
        assert read.head + read.number + read.tail == cell, repr(cell)
        coded = taxonomy.top_coded_cells([cell])[0]
        years = number * 90 / mark
        if 90 <= years <= 125:
            assert coded == mark_cell.format(mark), (repr(cell), repr(coded))
        else:
            assert coded == cell, (repr(cell), repr(coded))
    # ...a dash after a space and before a figure is the number's sign, as `-` is (`Age -1`).
    for dash in DASHES:
        read = taxonomy.safe_harbor_number(f"Age {dash}1", False, True, True)
        assert read is not None and read.value == -1, repr(dash)
        assert taxonomy.safe_harbor_number(f"Age{dash}95", False, True, True).value == 95  # type: ignore[union-attr]


def test_the_readers_spaces_and_dashes_are_the_one_definition_over_every_code_point() -> None:
    """THE GENERATED AGREEMENT CASE (batch 4s's merge; the orchestrator's LANE HB2 RULINGS 7 (3) and 8 (3)): over all 1,114,112 code points the age words' reader (`taxonomy._age_plain`) writes a character ` ` exactly where the product's one definition reads a space (`_a_space_of_the_screen`, `_SCREEN_SPACE_RANGES`), `-` exactly where `_SCREEN_DASHES` names it and every other character as written, no character being both; the oracle (`_harbor_plain`) writes every code point as the product does, one by one and in one text; the lane's list before the merge lies inside the definition, and its dashes (the identifier forms' marks that are no `str.isspace()` space) are the named ones and the soft hyphen, which the definition reads as a space.

    Red on the lane's list before the merge (the controls and format
    characters it read as written), on a reader of the soft hyphen as a
    dash, on a reader that writes the dashes as written, and on the oracle's
    list before the merge.
    """
    oracle = _oracle()
    spaces = dashes = 0
    for code in range(0x110000):
        character = chr(code)
        is_space = taxonomy._a_space_of_the_screen(character)
        is_dash = character in taxonomy._SCREEN_DASHES
        assert not (is_space and is_dash), hex(code)
        written = taxonomy._age_plain(character)
        assert written == (" " if is_space else "-" if is_dash else character), hex(code)
        assert oracle._harbor_plain(character) == written, hex(code)  # type: ignore[attr-defined]
        spaces += int(is_space)
        dashes += int(is_dash)
    assert spaces == len(ONE_DEFINITION_SPACES) == 2474 and dashes == len(DASHES) == 11
    assert set(taxonomy._SCREEN_DASHES) == set(DASHES)
    assert set(LANE_SPACES_BEFORE) <= set(ONE_DEFINITION_SPACES) and len(LANE_SPACES_BEFORE) == 36
    before = {mark for mark in taxonomy._SSN_MARKS if not mark.isspace()}
    assert before - set(DASHES) == {"­"} and set(DASHES) <= before
    every = "".join(chr(code) for code in range(0x110000))
    plain = taxonomy._age_plain(every)
    assert len(plain) == len(every) == 1114112
    assert oracle._harbor_plain(every) == plain  # type: ignore[attr-defined]


def test_every_space_and_dash_of_the_one_definition_is_read_in_the_frames_places() -> None:
    """Each of the 2,474 spaces of the one definition and each of its 11 dashes, between the word and the number, between the mark and the number, before a unit word and inside the brackets around the number: read with its number, its frame kept as written, the top code written in the cell's own characters (batch 4s's merge).

    Red on the lane's list before the merge: a control or a format character
    beside the word, the mark or the unit left the cell no age with words,
    so its column put no Safe Harbor question; and on a reader that writes
    the dashes as written.
    """
    patterns = (("Age{s}95", 95.0, 90, "Age{s}90"), ("AGE:{s}97", 97.0, 90, "AGE:{s}90"),
                ("aged 101{s}yrs", 101.0, 90, "aged 90{s}yrs"), ("Age{s}({s}96{s})", 96.0, 90, "Age{s}({s}90{s})"),
                ("age{s}1100 months", 1100.0, 1080, "age{s}1080 months"))
    seen = 0
    for space in ONE_DEFINITION_SPACES:
        for pattern, number, mark, coded in patterns:
            cell = pattern.format(s=space)
            read = taxonomy.safe_harbor_number(cell, False, True, True)
            assert read is not None and read.value == number and taxonomy.age_mark(read) == mark, hex(ord(space))
            assert read.head + read.number + read.tail == cell, hex(ord(space))
            assert taxonomy.top_coded_cells([cell])[0] == coded.format(s=space), hex(ord(space))
            seen += 1
    for dash in DASHES:
        for pattern, coded in (("Age{d}95", "Age{d}90"), ("Age {d} 95", "Age {d} 90"), ("(Age{d}99)", "(Age{d}90)")):
            cell = pattern.format(d=dash)
            read = taxonomy.safe_harbor_number(cell, False, True, True)
            assert read is not None and read.value == float(cell.strip("()")[-2:]), repr(cell)
            assert taxonomy.top_coded_cells([cell])[0] == coded.format(d=dash), repr(cell)
            seen += 1
    assert seen == 2474 * 5 + 11 * 3


def test_the_word_screen_reads_the_shared_vocabulary_and_refuses_every_generated_family() -> None:
    """THE WORD SCREEN READS THE ONE SHARED CONSTANT (batch 4s's merge; the orchestrator's LANE HB2 RULINGS 2 (3) and 7 (3), LANE CODES-2 RULINGS 8 (5)): its words that say an age beside figures are the vocabulary's words before a number united with `ages` and `old`, and its unit words every unit of the vocabulary written in letters alone -- the two lists it held before the merge, written out here, equal to these -- and every generated family of the vocabulary whose age reaches its unit's mark (90 to 125 years) is refused on the three roads the screen reads: path (ii)'s word screen, path (iii)'s net after `no` and path (i)'s shapes no code wears; and each unit word after an age past 89 with no word before it.

    Red on a screen whose words leave the vocabulary's out (`_AGE_WORDS`
    without `age` and `aged`) and on one whose units leave a unit out
    (`_AGE_UNIT_WORDS` without `years`).
    """
    vocabulary = taxonomy.AGE_VOCABULARY
    assert taxonomy._AGE_WORDS == frozenset(vocabulary.before) | {"ages", "old"} == {"age", "aged", "ages", "old"}
    letters = {unit for unit, _letter in vocabulary.units if unit.isascii() and unit.isalpha()}
    assert taxonomy._AGE_UNIT_WORDS == letters == {
        "y", "yr", "yrs", "year", "years", "yo", "mo", "mos", "month", "months", "wk", "wks", "week", "weeks", "d", "day",
        "days", "m", "mth", "mths", "w", "dy", "dys",
    }
    draw = random.Random(4797)
    refused = 0
    for cell, number, mark, _pattern in _worded(draw) + _unicode_families(draw):
        if not 90 <= number * 90 / mark <= 125:
            continue
        assert not taxonomy.passes_the_word_screen(cell), repr(cell)
        assert not taxonomy.passes_the_word_screen(cell, False), repr(cell)
        assert taxonomy._a_shape_no_code_wears(cell), repr(cell)
        refused += 1
    assert refused > 1000
    for unit, letter in vocabulary.units:
        if not (unit.isascii() and unit.isalpha()):
            continue
        for written in (f"{taxonomy.AGE_MARKS[letter] + 1}{unit}", f"{taxonomy.AGE_MARKS[letter] + 1} {unit}"):
            assert not taxonomy.passes_the_word_screen(written, False), written
            assert taxonomy._a_shape_no_code_wears(written), written


def test_the_top_code_writes_the_pooled_level_in_the_cells_own_words() -> None:
    """Every cell at or past its unit's mark, to 125 years, is written as the mark in its own frame: `Age 95` is `Age 90`."""
    draw = random.Random(4772)
    for cell, number, mark, mark_cell in _worded(draw):
        coded = taxonomy.top_coded_cells([cell])[0]
        years = number * 90 / mark
        if 90 <= years <= 125:
            whole = taxonomy.safe_harbor_number(cell, False, True, True).whole  # type: ignore[union-attr]
            figures = f"{mark}"
            if whole[:1] == "0" and len(whole) > len(figures):
                # ...as wide as the cell pads its figures (`095` is `090`).
                figures = "0" * (len(whole) - len(figures)) + figures
            assert coded == mark_cell.format(figures), (cell, coded)
        elif years < 90:
            assert coded == cell, (cell, coded)
        # ...and, without words, as before them: kept whole.
        assert taxonomy.top_coded_cells([cell], words=False)[0] in (cell, coded)


def test_words_that_are_no_age_are_read_as_before() -> None:
    """`Stage 2`, `Grade 3`, `Room 101`, `Week 95`, `Score 95`, `Agent 5`, a label before a record number: read as without the words."""
    draw = random.Random(4773)
    seen = 0
    for word in NOT_AGES:
        for how in CASES:
            for separator in SEPARATORS:
                for unit, _mark in UNITS_AFTER:
                    for frame in ("", "()"):
                        cell = f"{_cased(word, how)}{separator}{draw.randint(0, 2000000)}{unit}"
                        cell = f"({cell})" if frame else cell
                        assert taxonomy.safe_harbor_number(cell, False, True, True) == taxonomy.safe_harbor_number(cell, False), cell
                        seen += 1
    assert seen > 10000
    # ...and with every space and dash of the product between the word and its number.
    for word in NOT_AGES + ("Age group", "Aged care", "Agency", "Average"):
        for separator in UNICODE_SPACES + DASHES:
            for frame in ("{}", "({})", "{} yrs"):
                cell = frame.format(f"{word}{separator}{draw.randint(0, 200)}")
                assert taxonomy.safe_harbor_number(cell, False, True, True) == taxonomy.safe_harbor_number(cell, False), repr(cell)
    # ...an amount in brackets alone is read as before (`(95)` is -95 to the number reader).
    for cell in ("(95)", "[95]", "(95.5)", "( 95 )"):
        assert taxonomy.safe_harbor_number(cell, False, True, True) == taxonomy.safe_harbor_number(cell, False), cell
    # ...and `Age -1` is the placeholder -1, a sign after a space, not a mark.
    read = taxonomy.safe_harbor_number("Age -1", False, True, True)
    assert read is not None and read.value == -1


def test_a_cell_with_no_age_word_reads_as_it_did() -> None:
    """Every cell the vocabulary does not frame is read byte for byte as before it, bare, with a unit or an affix."""
    draw = random.Random(4774)
    for _round in range(3000):
        number = draw.choice([f"{draw.randint(-20, 99999)}", f"{draw.uniform(0, 200):.{draw.randint(1, 3)}f}",
                              f"{draw.randint(0, 125):03d}", f"+{draw.randint(0, 125)}", f"{draw.randint(0, 9)},{draw.randint(0, 9)}"])
        cell = draw.choice(["", " ", "  "]) + number + draw.choice([
            "", " months", " d", "wk", " years", "Y", "O", " y/o", "-year-old", " m/o", " months old", " yo", " kg", " mmHg", "%",
        ]) + draw.choice(["", " "])
        assert taxonomy.safe_harbor_number(cell, False, True, True) == taxonomy.safe_harbor_number(cell, False), cell


def test_the_lists_agree_on_the_generated_families() -> None:
    """The one shared constant (LANE HB2 RULINGS 1 (3)): every word, mark, bracket and unit it names is read in the families, and `age_words_split` sets aside exactly the word before the number."""
    vocabulary = taxonomy.AGE_VOCABULARY
    assert vocabulary.before == taxonomy.AGE_WORDS_BEFORE == ("aged", "age")
    assert vocabulary.marks == taxonomy.AGE_WORD_MARKS == (":", "=", "-")
    assert vocabulary.brackets == taxonomy.AGE_WORD_BRACKETS == (("(", ")"), ("[", "]"))
    assert dict(vocabulary.units) == taxonomy.AGE_UNIT_WORDS
    assert set(dict(vocabulary.units).values()) == set(taxonomy.AGE_MARKS)
    families = _worded(random.Random(4775))
    words_read = {taxonomy.safe_harbor_number(cell, False, True, True).word.strip(" :=-(").lower()  # type: ignore[union-attr]
                  for cell, _n, _m, _c in families} - {""}
    assert words_read == set(vocabulary.before)
    for unit, _letter in vocabulary.units:
        read = taxonomy.safe_harbor_number(f"Age 95 {unit}", False, True, True)
        assert read is not None and taxonomy.age_mark(read) == taxonomy.AGE_MARKS[dict(vocabulary.units)[unit]], unit
    for cell, _n, _m, _c in families:
        word, rest = taxonomy.age_words_split(cell.strip("(["))
        assert word + rest == cell.strip("([")
    assert taxonomy.age_words_split("Age 90-94") == ("Age ", "90-94")
    assert taxonomy.age_words_split("age >= 95") == ("age ", ">= 95")
    assert taxonomy.age_words_split("Stage 2") == ("", "Stage 2")


def test_the_split_sets_aside_what_the_reader_reads_before_a_number_or_a_band() -> None:
    """`age_words_split`, the seam lane CZ-E's band reader reads at its merge (LANE HB2 RULINGS 3 (5)): over the words, the marks, every space and dash, the brackets and the band forms, the rest opens with a figure, a sign before one or a band's own mark, and the two parts join to the cell.

    Red on b61eaa4b, whose split set aside the word and its ASCII spaces
    alone: `Age: 90-94` was `('Age', ': 90-94')`, `[Age 90-94]` was not
    split, and `Age<U+00A0>90-94` handed the band reader a leading space.
    """
    draw = random.Random(4782)
    seen = 0
    for word in taxonomy.AGE_WORDS_BEFORE:
        for how in CASES:
            for space in UNICODE_SPACES:
                for mark in ("", ":", "=", "-", "\u2013", "\u2212", "\u2011"):
                    for frame in ("{}", "[{}]", "({})", "word ({})", "word [{}]"):
                        for band in BANDS:
                            head = f"{_cased(word, how)}{space}{mark}{space if mark and draw.random() < 0.5 else ''}"
                            if frame.startswith("word"):
                                cell = head + frame[5:].format(band)
                            else:
                                cell = frame.format(head + band)
                            before, rest = taxonomy.age_words_split(cell)
                            assert before + rest == cell, repr(cell)
                            assert rest[:1].isdigit() or rest[:1] in (">", "<", "+", "\u2265") or (
                                rest[:1] in DASHES and rest[1:2].isdigit()), (repr(cell), repr(before), repr(rest))
                            seen += 1
    assert seen > 5000
    for cell in ("Stage 2", "Age group 3", "Agent 5", "Ages 3", "Aged care", "(95 yrs)", "95"):
        assert taxonomy.age_words_split(cell) == ("", cell), cell


def _oracle() -> object:
    where = pathlib.Path(__file__).resolve().parents[1] / "tools" / "reference" / "make_generation_reference_vectors.py"
    spec = importlib.util.spec_from_file_location("oracle_age_words", where)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_oracle_bounds_worded_ages_as_the_product_does() -> None:
    """A-P4-59 for method G7.14 as lane HB2 widens it: `safe_harbor_ages_twin` and `at_most_the_top_code` write the same cells with the age words read and without them, the bound of a column described as numbers given both ways (lane HB2's repair 2, the combined verify's item 2: red on the oracle that drops it, V9), numbers past 125 with a unit no age has among them (`130.9 kg`)."""
    oracle = _oracle()
    draw = random.Random(4776)
    families = _worded(draw) + _unicode_families(draw)
    units = (" kg", " mg", " cm", " lb", " mmHg", "O", " years", "")
    for mark in contract.TOP_CODE_MARKS:
        for held, published, labels in (
            (False, None, False), (True, None, False), (False, False, False), (False, True, False),
            (False, None, True), (False, False, True),
        ):
            for _column in range(40):
                cells = [draw.choice(families)[0] for _cell in range(draw.randint(1, 20))]
                cells += [draw.choice(["Stage 3", "NA", "Age 95+", f"{draw.randint(0, 130)}", "130.9 kg", "88.0 kg"])]
                cells += [f"{draw.uniform(0, 400):.{draw.randint(0, 2)}f}{draw.choice(units)}"]
                for words in (True, False):
                    for bounded in (False, True):
                        assert taxonomy.at_most_the_top_code(
                            cells, frozenset({"NA"}), mark, held, published, labels, words, bounded
                        ) == oracle.safe_harbor_ages_twin(  # type: ignore[attr-defined]
                            cells, frozenset({"NA"}), mark, held, published, labels, words, bounded
                        ), (mark, held, published, labels, words, bounded, cells)
    # ...and the bound itself, product and oracle: a weight past 125 described as numbers.
    for bounded in (False, True):
        for twin in (taxonomy.at_most_the_top_code(["130.9 kg", "88.0 kg"], frozenset(), 90, False, None, False, False, bounded),
                     oracle.safe_harbor_ages_twin(["130.9 kg", "88.0 kg"], frozenset(), 90, False, None, False, False,  # type: ignore[attr-defined]
                                                  bounded)):
            assert twin[1] == "88.0 kg"
            assert (float(twin[0].split()[0]) <= 90) == bounded, (bounded, twin)


# THE NUMBER READER'S OWN FAMILIES (lane HB2's repair 2; Codex's item 3, the
# orchestrator's LANE HB2 RULINGS 5 (3)): the numbers the generator writes in
# its six styles (`generation._styled_number`: plain, leading zeros, a leading
# plus, decimals, exponents in either case, at each order of zeros), with each
# mark between thousands and each sign's notation, each set in every frame of
# the vocabulary beside the same text with no word and no bracket -- read by
# the number reader alone, the check's oracle. A number in brackets right after
# an age word or right before an age's unit is the frame's (`Age (95) years` is
# 95, Codex's case), so the bracket notation of a negative is set aside here.
FRAMED = (
    ("Age {}", "{}", 90), ("age: {}", "{}", 90), ("AGE={}", "{}", 90), ("Age - {}", "{}", 90), ("aged {}", "{}", 90),
    ("Age {} yrs", "{} yrs", 90), ("({} yrs)", "{} yrs", 90), ("{} (years)", "{} years", 90), ("Age ({})", "{}", 90),
    ("Age ({}) years", "{} years", 90), ("Age [{}] years", "{} years", 90), ("Age ( {} ) yrs", "{} yrs", 90),
    ("({}) yrs", "{} yrs", 90), ("[{}] months", "{} months", 1080), ("Age ({} months)", "{} months", 1080),
    ("(Age {})", "{}", 90), ("[Age {} days]", "{} days", 32871), ("Age\u00a0{}", "{}", 90), ("Age:\u2009{}", "{}", 90),
    ("Age\u2013{}", "{}", 90), ("Age {} wk", "{} wk", 4695), ("Age {}-year-old", "{}-year-old", 90),
    ("Age {} y/o", "{} y/o", 90), ("Age ({}) (years)", "{} years", 90), ("[Age ({}) years]", "{} years", 90),
    ("Age\u00a0[{}]\u00a0months", "{} months", 1080),
)


def _styled(draw: random.Random, mark: int) -> str:
    """One number of the generator's own families, within its frame unit's ages (lane HB2's repair 2)."""
    from synthtwin import generation, parsing

    top = {90: 125, 1080: 1500, 4695: 6600, 32871: 46000}[mark]
    value = float(draw.randint(0, top)) if draw.random() < 0.8 else round(draw.uniform(0, top), draw.randint(1, 2))
    notations = [form for form in parsing.NEGATIVE_FORMS if form != parsing.NEGATIVE_BRACKETS]
    return generation._styled_number(
        -value if draw.random() < 0.05 else value, draw.choice(contract.NUMERIC_STYLES), draw.randint(0, 2),
        draw.random() < 0.5, -1, -1, draw.choice(("",) + parsing.GROUP_MARKS), draw.choice(notations),
        draw.random() < 0.3,
    )


def test_every_number_the_number_reader_reads_is_read_in_every_frame() -> None:
    """Every number of the generator's own families, in every frame of the vocabulary, is read with the value and unit the number reader gives it with no word and no bracket, its frame kept as written; product and oracle write the same twin cells.

    Red on 3f542bc9 (lane HB2's repair 1): `Age (95) years` read as -95,
    `Age [95] years` and `Age .95e2` as no number, so a column of them put
    no question and published and wrote its ages past 89 (Codex's item 3);
    and on the two mutants that undo the repair (a number opening at a
    figure or a sign alone; no bracket around the number alone).
    """
    oracle = _oracle()
    draw = random.Random(4791)
    framed: "list[str]" = []
    for _round in range(12000):
        frame, bare, mark = draw.choice(FRAMED)
        number = _styled(draw, mark)
        alone = taxonomy.safe_harbor_number(bare.format(number), False)
        if alone is None:
            continue
        cell = frame.format(number)
        read = taxonomy.safe_harbor_number(cell, False, True, True)
        assert read is not None, repr(cell)
        assert read.value == alone.value and taxonomy.age_mark(read) == mark, (repr(cell), read.value, alone.value)
        assert read.head + read.number + read.tail == cell, repr(cell)
        framed += [cell]
    assert len(framed) > 10000
    # ...Codex's cells, each top-coded in its own frame; an amount in brackets beside no word and no unit as before.
    for cell, coded in (("Age (95) years", "Age (90) years"), ("Age [95] years", "Age [90] years"), ("(95) yrs", "(90) yrs"),
                        ("Age (95) (years)", "Age (90) (years)"), ("Age .95e2", "Age 90"), ("Age (.95e2) years", "Age (90) years"),
                        ("Age 9.5E+01", "Age 90"), ("[Age (95) years]", "[Age (90) years]"), ("Age\u00a0[95]\u00a0yrs", "Age\u00a0[90]\u00a0yrs")):
        assert taxonomy.safe_harbor_number(cell, False, True, True).value == 95, cell  # type: ignore[union-attr]
        assert taxonomy.top_coded_cells([cell])[0] == coded, cell
    for cell in ("(95)", "(95) kg", "[(95)]", "Stage (95) years", "(95)(96) yrs"):
        assert taxonomy.safe_harbor_number(cell, False, True, True) == taxonomy.safe_harbor_number(cell, False), cell
    for _column in range(150):
        cells = [draw.choice(framed) for _cell in range(draw.randint(1, 12))] + [draw.choice(["NA", "Stage 3", "130.9 kg"])]
        for mark in contract.TOP_CODE_MARKS:
            for held, published, labels in ((False, None, False), (True, None, False), (False, False, False),
                                            (False, True, False), (False, None, True)):
                for bounded in (False, True):
                    assert taxonomy.at_most_the_top_code(cells, frozenset({"NA"}), mark, held, published, labels, True, bounded) == \
                        oracle.safe_harbor_ages_twin(cells, frozenset({"NA"}), mark, held, published, labels, True, bounded), \
                        (mark, held, published, labels, bounded, cells)  # type: ignore[attr-defined]


def test_the_words_establish_a_column_as_ages(tmp_path: pathlib.Path) -> None:
    """A column at least half of whose numbers write an age word before them is established as ages as its name would (`AGE_NAMED`), so `yes` keeps it top-coded and never holds it (lane HB2's repair 1, skeptic 1's item 6, mutant M5)."""
    from synthtwin import profile, reading

    assert taxonomy.ages_written_with_words(["Age 95", "Age 45", "45"], False, frozenset())
    assert taxonomy.ages_written_with_words(["Age\u00a095", "Age\u201345", "NA"], False, frozenset({"NA"}))
    assert not taxonomy.ages_written_with_words(["95", "45", "Age 45"], False, frozenset())
    assert not taxonomy.ages_written_with_words(["Stage 3", "Grade 4", "45"], False, frozenset())
    draw = random.Random(4784)
    path = tmp_path / "ages.csv"
    path.write_text("record_label\n" + "".join(f"Age {draw.randint(18, 95)}\n" for _row in range(600)), encoding="utf-8",
                    newline="\n")
    table = reading.read_table(f"{path}")
    established: "dict[str, str]" = {}
    document = profile.build_document(table, taxonomy.Settings(), [], top_code=True, ages_established=established)
    block = next(one for one in document["columns"] if one["name"] == "record_label")  # type: ignore[index, union-attr]
    assert block["top_coded"] == 90 and established == {"record_label": taxonomy.AGE_NAMED}


def test_the_words_put_a_column_in_the_reach_under_every_heading(tmp_path: pathlib.Path) -> None:
    """The same cells under every heading -- an age, a neutral, a code-like, a label and a note heading -- are described exactly as under the age heading: top-coded 90 with their words, established as ages (lane HB2's repair 2, Codex's item 2: `Age 18` to `Age 105` on nine cells in ten and `Age 126` to `Age 225` on the tenth, under `record_label`, were taken out of the reach by their strays before the words were read, and published `Age 95`)."""
    from synthtwin import profile, reading

    cells = [f"Age {18 + row % 88}" for row in range(1800)] + [f"Age {126 + row % 100}" for row in range(200)]
    seen: "dict[str, tuple[str, str]]" = {}
    for heading in ("age", "subject_age", "value", "result", "measure", "item_code", "code", "dx_code", "record_label",
                    "label", "category", "note", "visit_note", "comment", "field_7"):
        path = tmp_path / f"{heading}.csv"
        path.write_text(heading + "\n" + "".join(cell + "\n" for cell in cells), encoding="utf-8", newline="\n")
        established: "dict[str, str]" = {}
        document = profile.build_document(reading.read_table(f"{path}"), taxonomy.Settings(), [], top_code=True,
                                          ages_established=established)
        block = {key: value for key, value in document["columns"][0].items() if key != "name"}  # type: ignore[index, union-attr]
        assert block["top_coded"] == 90 and block["top_coded_words"] is True, heading
        seen[heading] = (json.dumps(block, sort_keys=True), established[heading])
    assert len(set(seen.values())) == 1, {heading: seen[heading][1] for heading in seen}


def test_at_the_owner_floor_beside_a_declared_person_the_words_give_a_neutral_heading_the_age_headings_block(
    tmp_path: pathlib.Path,
) -> None:
    """1,000 people of 20 rows beside a declared person column: `Age 18` to `Age 105` one a person on 900 people and `Age 126` to `Age 225` on 100, under the heading `age` and under the neutral heading `visit_note`, give the same block byte for byte -- top-coded 90 with their words and the same ends (batch 4s's merge, the scoped verify 2 of lane HB2, item 1).

    The person-column half of Codex's item 2 (lane HB2's repair 2): the
    words reach the reach as the name would, so a column named `age` whose
    cells write the words is never `reached by its name alone`, and its ends
    are pooled in people as under any heading. Red on the verify's mutant X3
    (`reached_by_name`'s `and not words_named` removed): under `age` the
    column was then held whole as record numbers, where `visit_note` was
    top-coded with its ends [18, 38].
    """
    import dataclasses

    from synthtwin import profile, reading

    cells = [f"Age {18 + who % 88}" if who < 900 else f"Age {126 + who - 900}" for who in range(PEOPLE)]
    seen: "dict[str, str]" = {}
    for heading in ("age", "visit_note"):
        path = tmp_path / f"{heading}.csv"
        path.write_text(f"sid,{heading}\n" + "".join(f"P{who:06d},{cells[who]}\n" for who in range(PEOPLE) for _row in range(20)),
                        encoding="utf-8", newline="\n")
        table = reading.read_table(f"{path}", small_cell_floor=11)
        assert len(table.columns[0]) == ROWS
        settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=11), person_columns=("sid",))
        document = profile.build_document(table, settings, ["sid"], [], [], subjects=["sid"], top_code=True)
        block = next(one for one in document["columns"] if one["name"] == heading)  # type: ignore[union-attr]
        assert block["role"] != taxonomy.ROLE_IDENTIFIER, (heading, block["role"])
        assert block["top_coded"] == 90 and block["top_coded_words"] is True, heading
        low, high = block["top_coded_ends"]
        assert 18 <= low < high < 90, (heading, low, high)
        seen[heading] = json.dumps({key: value for key, value in block.items() if key != "name"}, sort_keys=True)
    assert seen["age"] == seen["visit_note"]


def test_the_description_records_the_words_only_where_a_cell_holds_them() -> None:
    """`top_coded_words` is written where a cell is read with age words, so every other block keeps its bytes; the contract reads it beside `top_coded` alone."""
    assert taxonomy.age_words_written(["Age 95", "Age 45"], False, frozenset())
    assert taxonomy.age_words_written(["95 (years)"], False, frozenset())
    assert not taxonomy.age_words_written(["95", "45 yrs", "92-year-old", "(95)", "Stage 3"], False, frozenset())
    column = taxonomy.profile_column("a", 1, ["Age 45", "Age 90"], 2, taxonomy.Settings())
    assert "top_coded_words" not in taxonomy.with_top_code(column, 90, 11).details
    assert taxonomy.with_top_code(column, 90, 11, (), True).details["top_coded_words"] is True


def test_a_description_written_before_the_words_validates_as_it_did() -> None:
    """The validator reads a column's age words only where its description records them (SH3 RULINGS 1 (2)'s pattern)."""
    from synthtwin import reading

    table = reading.Table(["age"], [["Age 95", "95", "Age 45"]], 3, "utf-8", False, reading.HEADER_FROM_FILE)
    # (a floor of 0: the top category pooled under no rule, as below the table floor.)
    old = validation._top_coded_table(table, {"age": 90}, {"age": (0, ())}, [], (), ())
    new = validation._top_coded_table(table, {"age": 90}, {"age": (0, ())}, [], (), (), ["age"])
    assert old.columns[0] == ["Age 95", "90", "Age 45"]
    assert new.columns[0] == ["Age 90", "90", "Age 45"]


def test_a_word_age_description_without_its_pool_marker_reads_its_words(tmp_path: pathlib.Path) -> None:
    """A description recording `top_coded_words` beside no `top_category_pooled` -- one the loader admits -- is read with its words by the validator, the generator and the chain's reader alike (lane HB2's repair 2, Codex's item 5): the real table meets it, `Age 95` reads as `Age 90`, and the twin's bound writes `Age 95` at or below 90 and keeps `Age 90`; the older reader, which left `Age 95` as it was, is kept for a description recording neither. Red on the mutants that read such a block with the older reader."""
    from synthtwin import generation, profile, reading

    import fixtures

    draw = random.Random(4792)
    path = tmp_path / "t.csv"
    path.write_text("age_text\n" + "".join(f"Age {draw.randint(18, 95)}\n" for _row in range(3000)), encoding="utf-8",
                    newline="\n")
    table = reading.read_table(f"{path}")
    document = profile.build_document(table, taxonomy.Settings(), [], top_code=True)
    block = document["columns"][0]  # type: ignore[index]
    assert block["top_coded_words"] is True and "top_category_pooled" in block  # type: ignore[index]
    del block["top_category_pooled"]  # type: ignore[attr-defined]
    block.pop("top_category_people", None)  # type: ignore[attr-defined]
    described = contract.load_profile(f"{fixtures.write_profile(tmp_path, 't-profile.json', document)}")
    column = described.columns[0]
    assert column.top_coded == 90 and column.top_coded_words and column.top_category_pooled < 0
    read = validation._top_coded_table(table, {"age_text": 90}, {}, [], (), (), ["age_text"])
    assert "Age 95" in table.columns[0] and "Age 95" not in read.columns[0] and "Age 90" in read.columns[0]
    # ...and the describe the validator runs again, handed the cells as written, reads the words too.
    again = profile.build_document(table, taxonomy.Settings(), [], top_coded_only={"age_text": 90}, top_pooled_only={},
                                   top_words_only=["age_text"])
    published = json.dumps(again["columns"][0])  # type: ignore[index]
    assert '"Age 95"' not in published and '"Age 90"' in published
    legacy = validation._top_coded_table(table, {"age_text": 90}, {}, [], (), ())
    assert "Age 95" in legacy.columns[0]
    written = generation._top_coded_twin(column, ["Age 95", "Age 90", "Age 45"])
    later = taxonomy.safe_harbor_number(written[0], False, True, True)
    assert later is not None and later.value <= 90 and written[1:] == ["Age 90", "Age 45"], written
    # ...and the chain's reader of a block (behind its switch) reads it the same.
    from synthtwin import chain

    chained = chain.described_cells(table, 0, block, taxonomy.Settings(), {"code": False, "measurement": False,  # type: ignore[arg-type]
                                                                            "decimal_comma": False}, "", True)
    assert "Age 95" not in chained and "Age 90" in chained
    (tmp_path / "checked").mkdir()
    with _nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["validate", f"{tmp_path / 't-profile.json'}", "--twin", f"{path}", "--out-dir",
                         f"{tmp_path / 'checked'}", "--replace"]) == 0


@contextlib.contextmanager
def _nobody_at_the_keyboard():  # type: ignore[no-untyped-def]
    asked = cli._there_is_somebody_to_ask
    cli._there_is_somebody_to_ask = lambda: False
    try:
        yield
    finally:
        cli._there_is_somebody_to_ask = asked


def test_at_the_owner_floor_an_age_word_column_is_asked_and_top_coded(tmp_path: pathlib.Path) -> None:
    """`Age NN` one a person, written with the product's own spaces and dashes (`Age<U+00A0>NN`, `Age:<U+202F>NN`, `Age<U+2013>NN`, ...), 1,000 people of 20 rows, alone, nobody at the keyboard: the Safe Harbor question put, no age past 89 shown or written, the top code `Age 90` in each cell's characters, the twin valid.

    Red on 820d55c3 (78 levels published, `Age 91` to `Age 95` among them,
    1,360 twin cells past 89), on b61eaa4b (the Unicode forms read as words:
    no question, their ages past 89 published and written; lane HB2's
    repair 1, skeptic 1's item 1) and on the mutant that reads no word
    (`taxonomy._age_word_at` returning -1).
    """
    import re

    forms = ("Age\u00a0{}", "Age:\u202f{}", "Age\u2013{}", "Age \u2014 {}", "Age\u2212{}", "Age\u2011{}", "Age\u200b{}",
             "Age\u2009{}")
    draw = random.Random(4777)
    ages = [draw.randint(18, 95) for _person in range(PEOPLE)]
    cells = [forms[(row // (ROWS // PEOPLE)) % len(forms)].format(ages[row // (ROWS // PEOPLE)]) for row in range(ROWS)]
    last = re.compile(r"(\d+)$")
    source = tmp_path / "t.csv"
    with open(source, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["record_label"])
        writer.writerows([cell] for cell in cells)
    screen = io.StringIO()
    with _nobody_at_the_keyboard(), contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        assert cli.main(["profile", f"{source}", "--out-dir", f"{tmp_path}", "--replace"]) == 0
        assert cli.main(["generate", f"{tmp_path / 't-profile.json'}", "--out-dir", f"{tmp_path}", "--seed", "0", "--replace"]) == 0
        assert cli.main(["validate", f"{tmp_path / 't-profile.json'}", "--twin", f"{tmp_path / 't-twin.csv'}",
                         "--out-dir", f"{tmp_path}", "--replace"]) == 0
    questions = json.loads((tmp_path / "t-questions.json").read_text(encoding="utf-8"))
    offered = [[one["answer"] for one in entry["answers_you_can_give"]] for entry in questions["asked"]
               if entry.get("column") == "record_label"]
    assert offered and "yes" in offered[0] and "no" in offered[0]
    described = (tmp_path / "t-profile.json").read_text(encoding="utf-8")
    block = json.loads(described)["columns"][0]
    assert block["top_coded"] == 90 and block["top_coded_words"] is True
    past = sorted({cell for cell in cells if int(last.search(cell).group(1)) > 90})  # type: ignore[union-attr]
    texts = [described, (tmp_path / "t-profile.txt").read_text(encoding="utf-8"), screen.getvalue(),
             (tmp_path / "t-questions.json").read_text(encoding="utf-8")]
    # ...as written, and as a description file or a printed line escapes them.
    escaped = [json.dumps(one)[1:-1] for one in past] + [one.encode("ascii", "backslashreplace").decode("ascii") for one in past]
    assert past and not [one for one in past + escaped if any(one in text for text in texts)]
    with open(tmp_path / "t-twin.csv", encoding="utf-8", newline="") as handle:
        twin = [row[0] for row in list(csv.reader(handle))[1:]]
    assert len(twin) == ROWS
    assert not [cell for cell in twin if int(last.search(cell).group(1)) > 90]  # type: ignore[union-attr]
    assert {form.format(90) for form in forms} <= set(twin)


def test_the_generator_reads_the_words_its_description_records(tmp_path: pathlib.Path) -> None:
    """A column of decimal ages written with the words (`Age 50.12 yrs`), described as numbers with the words as their affixes, top-coded with its words recorded: the generator's top-code step reads a twin cell `Age 95.12 yrs` as 95.12 and writes it at or below 90, words kept, and keeps one below 90 (lane HB2's repair 1, skeptic 1's item 6: red on the mutant that reads no words, M21)."""
    from synthtwin import generation, profile, reading

    import fixtures

    draw = random.Random(4786)
    path = tmp_path / "ages.csv"
    path.write_text("age_text\n" + "".join(f"Age {draw.uniform(18, 104):.2f} yrs\n" for _row in range(3000)), encoding="utf-8",
                    newline="\n")
    document = profile.build_document(reading.read_table(f"{path}"), taxonomy.Settings(), [], top_code=True)
    described = contract.load_profile(f"{fixtures.write_profile(tmp_path, 't-profile.json', document)}")
    column = described.columns[0]
    assert column.top_coded == 90 and column.top_coded_words and isinstance(column.facts, contract.AffixedFacts)
    written = generation._top_coded_twin(column, ["Age 95.12 yrs", "Age 45.00 yrs", "Age 130.00 yrs"])
    read = taxonomy.safe_harbor_number(written[0], False, True, True)
    assert read is not None and read.value <= 90 and written[0][:4] == "Age " and written[0][-4:] == " yrs", written
    assert written[1] == "Age 45.00 yrs"
    later = taxonomy.safe_harbor_number(written[2], False, True, True)
    assert later is not None and later.value <= 90, written


def test_at_the_owner_floor_bracketed_exponent_and_strayed_word_ages_are_asked_and_top_coded(tmp_path: pathlib.Path) -> None:
    """Codex's tables at 20,000 rows, one column each, nobody at the keyboard: `Age (NN) years` and `Age [NN] years` (ages 18 to 95), `Age 20` to `Age 89` beside 100 `Age .95e2` and 100 `Age 95`, and `Age 18` to `Age 105` beside 2,000 `Age 126` to `Age 225` under the heading `record_label`: each column put the Safe Harbor question and top-coded 90 with its words, no age past 89 shown in any file or on the screen, no twin cell past 90, the twin valid.

    Red on 3f542bc9 (lane HB2's repair 1; Codex's items 2 and 3): the first
    three were published with no question (256 `Age (95) years` cells, 100
    `Age .95e2`), the fourth taken out of the reach by its strays (204
    `Age 95` cells written).
    """
    columns = {
        "age_round": [f"Age ({18 + row % 78}) years" for row in range(ROWS)],
        "age_square": [f"Age [{18 + row % 78}] years" for row in range(ROWS)],
        "age_exponent": [f"Age {20 + row % 70}" for row in range(ROWS - 200)] + ["Age .95e2"] * 100 + ["Age 95"] * 100,
        "record_label": [f"Age {18 + row % 88}" for row in range(ROWS - 2000)] + [f"Age {126 + row % 100}" for row in range(2000)],
    }
    names = list(columns)
    source = tmp_path / "t.csv"
    with open(source, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(names)
        writer.writerows([columns[name][row] for name in names] for row in range(ROWS))
    screen = io.StringIO()
    with _nobody_at_the_keyboard(), contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        assert cli.main(["profile", f"{source}", "--out-dir", f"{tmp_path}", "--replace"]) == 0
        assert cli.main(["generate", f"{tmp_path / 't-profile.json'}", "--out-dir", f"{tmp_path}", "--seed", "0", "--replace"]) == 0
        assert cli.main(["validate", f"{tmp_path / 't-profile.json'}", "--twin", f"{tmp_path / 't-twin.csv'}",
                         "--out-dir", f"{tmp_path}", "--replace"]) == 0
    questions = json.loads((tmp_path / "t-questions.json").read_text(encoding="utf-8"))
    blocks = {block["name"]: block for block in json.loads((tmp_path / "t-profile.json").read_text(encoding="utf-8"))["columns"]}
    texts = [(tmp_path / name).read_text(encoding="utf-8") for name in ("t-profile.json", "t-profile.txt", "t-questions.json")]
    texts += [screen.getvalue()]
    with open(tmp_path / "t-twin.csv", encoding="utf-8", newline="") as handle:
        twin = list(csv.reader(handle))
    for place, name in enumerate(names):
        offered = [[one["answer"] for one in entry["answers_you_can_give"]] for entry in questions["asked"]
                   if entry.get("column") == name]
        assert offered and "yes" in offered[0] and "no" in offered[0], name
        assert blocks[name]["top_coded"] == 90 and blocks[name]["top_coded_words"] is True, name
        past = sorted({cell for cell in columns[name] if taxonomy.safe_harbor_number(cell, False, True, True).value > 90})  # type: ignore[union-attr]
        assert past and not [cell for cell in past if any(cell in text for text in texts)], name
        written = [row[place] for row in twin[1:]]
        assert len(written) == ROWS
        assert not [cell for cell in written if (taxonomy.safe_harbor_number(cell, False, True, True) or taxonomy.safe_harbor_number("0")).value > 90], name  # type: ignore[union-attr]
