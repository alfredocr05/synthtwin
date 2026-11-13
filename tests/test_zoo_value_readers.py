"""P4-D472 (lane CZ-E): the value readers -- the readers that hold a column by what its values are; HIPAA first.

THE READERS (`taxonomy.value_reader_hold`, asked last by
`taxonomy.safe_harbor_hold` on a role that publishes a value, and the age
reach's bands): (A) a level the floor's rows hold, of two words or more,
holding a month and a day, a telephone number, a run of seven figures or
more, a title before a name, initials, a family name and an initial or
a given name, or a name after a word naming a relative
(`HELD_IDENTIFIER_WORDS`); (B) codes of an area smaller than a state on
two in three of the cells (`HELD_AREA_CODES`); (C) a latitude and a
longitude in one cell, or network addresses, on two in three
(`HELD_COORDINATE_PAIRS`, `HELD_NETWORK_ADDRESSES`); (E) devices' serial
numbers on two in three, 100 different or more in two makers' layouts or
more (`HELD_DEVICE_SERIALS`); each held whole and
put the one Safe Harbor question, freed only by `no` or `--identifier`;
and (D) a column of age bands holding a band past 89 is in the age reach,
its bands from 90 written as one band in the source's form
(`age_bands_past_89`, `pooled_band`, `top_coded_cells`), its age question
put, `no` freeing it.

THE GATE: each reader's GENERATED spellings (`tests/value_readers_forms.py`,
thousands a reader, every form from a grammar written there and never from
a reader's own list: the orchestrator's LANE CZ-E RULINGS 3 (6)) are read,
each red on its mutant, the product's odd dashes and spaces in every
position among them; the families left open are counted as stated
(`open_families`); the closed list of
plain levels is read by none; a closed list of codes, one layout's keys
and a second layout on fewer than one in ten of the cells are no column
of serials, red on the layout mutant; the description of each kind at 600 rows
names its columns for the command to hold and its price columns not, and
with the readers away names none; through the commands at 600 rows the
remarks, the area codes answered `code`, the coordinate pairs and the
network addresses answered `keep` on a table counted in rows, the age
bands, and the serials alone in their table answered truthfully show no
real value and write none in the twin; and ONE 20,000-row
case, the smallest remark table at the owner's floor, unanswered (THE
SUITE'S TIME rule), beside which the second repair validates one column
of 20,000 cells against the description the base wrote of it (Codex's
item 3: the validator alone, about five seconds) and reads its
column-level cases on 20,000 cells (dates sharing a day, values on the
floor's eleven rows). Every kind in every mode at 20,000 rows, and the
price over the whole zoo, are K-HZ-25's (`tools/measurements/
kpi_value_readers.py`, `kpi_run --slow`).
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import pathlib
import random

import pytest

import health_zoo as zoo
import value_readers_forms as readers
from synthtwin import asking, profile, reading, taxonomy


def _words(form: str) -> "object":
    return lambda text: taxonomy.identifier_words_form(text) == form


def _family(text: str) -> bool:
    return taxonomy.identifier_words_form(text) in (
        taxonomy.WORDS_FAMILY_AND_INITIAL, taxonomy.WORDS_FAMILY_AND_GIVEN, taxonomy.WORDS_INITIALS,
    )


def _a_number(text: str) -> bool:
    """A run of figures is held as a record's number or, ten figures opening 2 to 9, as a telephone number: either holds it."""
    return taxonomy.identifier_words_form(text) in (taxonomy.WORDS_FIGURES, taxonomy.WORDS_TELEPHONE)


def _any_form(text: str) -> bool:
    return taxonomy.identifier_words_form(text) != ""


def _an_address_cell(text: str) -> bool:
    """Whether the value readers' one pass counts a cell as a network address (`_value_forms_of_a_cell`'s first bit)."""
    bits = taxonomy._value_forms_of_a_cell(text)
    return bits > 0 and bits & 1 == 1


# Each reader's generated spellings, what reads them, and its mutant: the
# function the reader rests on, read as finding nothing (`MUTANT_OF`
# gives another where finding nothing is no mutant of it).
SPELLINGS = {
    "month and day": (readers.month_and_day_spellings, _words(taxonomy.WORDS_MONTH_AND_DAY),
                      ("_month_and_day_in_figures", "_month_and_day_in_words")),
    "telephone": (readers.telephone_spellings, _words(taxonomy.WORDS_TELEPHONE), ("_telephone_in",)),
    "figures": (readers.figure_run_spellings, _a_number, ("_figure_run_in", "_telephone_in")),
    "title": (readers.title_spellings, _words(taxonomy.WORDS_TITLE), ("_title_before_a_name",)),
    "initials": (readers.initials_spellings, _words(taxonomy.WORDS_INITIALS), ("_initials_in",)),
    "family name": (readers.family_spellings, _family, ("_family_name_then", "_initials_in")),
    "relative": (readers.relative_spellings, _words(taxonomy.WORDS_RELATIVE_NAME), ("_name_after_a_relative",)),
    "coordinate pair": (readers.coordinate_pair_spellings, lambda text: taxonomy.a_coordinate_pair(text),
                        ("a_coordinate_pair",)),
    "network address": (readers.network_address_spellings, lambda text: taxonomy.a_network_address(text),
                        ("a_network_address",)),
    "area code": (readers.area_code_spellings, lambda text: taxonomy.an_area_code(text), ("an_area_code",)),
    "serial number": (readers.serial_number_spellings, lambda text: taxonomy.a_serial_number(text),
                      ("a_serial_number",)),
    # ...an address or a point among words is held by an identifier form
    # (a hardware address's last groups read as a date too, `A8-26-25`).
    "network address in words": (readers.network_address_in_words_spellings, _any_form, ("_address_in_words",)),
    "coordinate pair in words": (readers.coordinate_pair_in_words_spellings, _any_form, ("_pair_in_words",)),
    "odd marks": (readers.odd_mark_spellings, lambda text: taxonomy.identifier_words_form(text) != "",
                  ("plain_marks",)),
    # ...the second repair's (the orchestrator's LANE CZ-E RULINGS 6): an
    # international number with a bracketed group; every form the address
    # reader admits, each a cell form whatever its letters or marks.
    "international telephone": (readers.international_telephone_spellings, _words(taxonomy.WORDS_TELEPHONE),
                                ("_international_telephone_in",)),
    "address forms": (readers.network_address_forms, lambda text: _an_address_cell(text), ("a_network_address",)),
}
# The mutant of a function whose finding nothing is no mutant: the odd
# marks read as written.
MUTANT_OF = {"plain_marks": lambda text: text}


def _misses(reader: str) -> "list[str]":
    make, read, _mutant = SPELLINGS[reader]
    return [text for text in make() if not read(text)]  # type: ignore[operator]


@pytest.mark.parametrize("reader", sorted(SPELLINGS))
def test_every_generated_spelling_is_read(reader: str) -> None:
    """Each reader's reach, closed at the unit level: every generated spelling, in thousands, is read."""
    make, _read, _mutant = SPELLINGS[reader]
    written = make()  # type: ignore[operator]
    assert len(written) >= 1000, (reader, len(written))
    missed = _misses(reader)
    assert not missed, (reader, len(missed), missed[:8])


@pytest.mark.parametrize("reader", sorted(SPELLINGS))
def test_each_reader_s_spellings_are_red_on_its_mutant(reader: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """The mutant: with the function a reader rests on finding nothing, its spellings go unread."""
    for name in SPELLINGS[reader][2]:
        monkeypatch.setattr(taxonomy, name, MUTANT_OF.get(name, lambda *arguments: False))
    assert _misses(reader), reader


def test_the_odd_marks_are_the_product_s_own() -> None:
    """Every dash and space of the product's own odd marks (`taxonomy._SSN_MARKS`), and every odd space and dash the sweep writes, is read plain."""
    for mark in taxonomy._SSN_MARKS + readers.ODD_SPACES + readers.ODD_DASHES:
        assert taxonomy.plain_marks(mark) in ("-", " "), repr(mark)


def test_the_open_families_stay_as_stated() -> None:
    """The families the readers leave open (plan P4-D472's stated limits) are read by none, as the records say."""
    readings = {
        "words": lambda text: taxonomy.identifier_words_form(text) != "", "pair": taxonomy.a_coordinate_pair,
        "address": taxonomy.a_network_address, "band": lambda text: taxonomy.an_age_band(text) is not None,
    }
    for family, spellings in readers.open_families().items():
        read = [text for text in spellings if readings[readers.OPEN_READERS.get(family, "words")](text)]
        assert not read, (family, read[:4])


def test_no_plain_level_is_read() -> None:
    """The price at the unit level: remarks and labels holding no identifier are read by no reader (`PLAIN_LEVELS`)."""
    read = {text: taxonomy.identifier_words_form(text) for text in readers.PLAIN_LEVELS}
    assert not {text: form for text, form in read.items() if form}, read


# A column of one layout's keys (a report's number, one a row), and one
# whose second layout stands on fewer than one in ten of its cells: the
# makers' layouts rule leaves each to the identifier rules.
_ONE_LAYOUT = [
    [f"RPT{300000 + place}" for place in range(600)],
    [f"C{5000000 + place}" if place % 20 else f"{4000000 + place}Q" for place in range(600)],
]


@pytest.mark.parametrize("cells", [
    [f"KIT{place % 40:04d}AB12" for place in range(600)],
    [f"{code}" for code in ("J1234", "0DTJ4ZZ", "C50.911", "12345-6") * 150],
    [f"P{1000000 + place}" for place in range(60)] * 10,
] + _ONE_LAYOUT)
def test_a_closed_list_of_codes_is_no_column_of_serials(cells: "list[str]") -> None:
    """Item (E)'s price at the unit level: a kit's codes (40 different), codes holding fewer than six figures, fewer than `SERIALS_AT_LEAST` different values, one layout's keys and a second layout on fewer than one in ten of the cells are read as no devices' serials."""
    assert taxonomy.value_reader_hold(taxonomy.ROLE_CATEGORICAL, cells, frozenset(), 11) != taxonomy.HELD_DEVICE_SERIALS


@pytest.mark.parametrize("cells", _ONE_LAYOUT)
def test_one_layout_s_keys_are_red_on_the_layout_mutant(cells: "list[str]", monkeypatch: pytest.MonkeyPatch) -> None:
    """The mutant of the makers' layouts: with any layouts taken for several makers', a column of one layout's keys is read as serials."""
    monkeypatch.setattr(taxonomy, "_makers_layouts", lambda layouts: True)
    assert taxonomy.value_reader_hold(taxonomy.ROLE_CATEGORICAL, cells, frozenset(), 11) == taxonomy.HELD_DEVICE_SERIALS


@pytest.mark.parametrize(("text", "form"), [
    ("half 1/2 tab", taxonomy.WORDS_MONTH_AND_DAY),
    ("Hepatitis, B", taxonomy.WORDS_FAMILY_AND_INITIAL),
])
def test_the_stated_false_alarms(text: str, form: str) -> None:
    """The readers' stated false alarms (plan P4-D472): a fraction of one or two figures, a category in title case after a comma; `no` frees each."""
    assert taxonomy.identifier_words_form(text) == form


def test_a_level_on_exactly_the_floor_s_rows_is_read() -> None:
    """The boundary: a remark on exactly the floor's rows is read, one on fewer is not (red where the floor's rows are passed over)."""
    cells = ["call (319) 555-0141 re refill"] * 11 + ["call (319) 555-0177 re ride"] * 10 + ["late arrival"] * 40
    assert taxonomy.levels_holding_identifier_words(cells, frozenset(), 11) == ["call (319) 555-0141 re refill"]


@pytest.mark.parametrize("form", ["address", "pair", "serial"])
def test_one_cell_in_three_of_another_form_hides_no_cell_form(form: str) -> None:
    """Two in three of the cells holding a figure of one cell form, one in three another label holding a figure (`Room 12`), each value on one row: held by the share (red where the share asks for every cell)."""
    if form == "address":
        values, hold = [f"10.{place // 250}.{place % 250}.7" for place in range(400)], taxonomy.HELD_NETWORK_ADDRESSES
    elif form == "pair":
        values = [f"{30 + place / 997:.5f},{-90 - place / 991:.5f}" for place in range(400)]
        hold = taxonomy.HELD_COORDINATE_PAIRS
    else:
        values = [f"KX{40000000 + place}" if place % 2 else f"{50000000 + place}Q" for place in range(400)]
        hold = taxonomy.HELD_DEVICE_SERIALS
    cells = values + ["Room 12"] * 200
    assert taxonomy.value_reader_hold(taxonomy.ROLE_CATEGORICAL, cells, frozenset(), 11) == hold


def test_a_one_word_level_is_never_read_for_identifier_words() -> None:
    """The price of two words: `K.T.` and `Dr.Gapesam` hold a form but are one word each, read by no level (red where one word is enough)."""
    assert taxonomy.identifier_words_form("K.T.") and taxonomy.identifier_words_form("Dr.Gapesam")
    cells = ["K.T."] * 20 + ["Dr.Gapesam"] * 20 + ["late arrival"] * 40
    assert taxonomy.levels_holding_identifier_words(cells, frozenset(), 11) == []


@pytest.mark.parametrize("form", ["address", "pair"])
def test_a_minority_of_addresses_or_points_among_labels_is_held(form: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """The orchestrator's LANE CZ-E RULINGS 3 (3): one person in twenty with their own device's address, or home point, on 20 rows among labels holding figures (`Bay 5`) is held, whatever the share; red on the mutant without the levels' cell forms."""
    labels = [f"{word} {place}" for word in ("Station", "Bay") for place in range(1, 11)] * 900
    if form == "address":
        seeded, hold = [f"192.0.2.{place}" for place in range(1, 51)], taxonomy.HELD_NETWORK_ADDRESSES
    else:
        seeded, hold = [f"{41 + place / 97:.5f},{-91 - place / 89:.5f}" for place in range(50)], \
            taxonomy.HELD_COORDINATE_PAIRS
    cells = labels + [value for value in seeded for _row in range(20)]
    assert taxonomy.value_reader_hold(taxonomy.ROLE_CATEGORICAL, cells, frozenset(), 11) == hold
    monkeypatch.setattr(taxonomy, "_levels_read", lambda cells, absent, floor, dates: ([], 0))
    assert taxonomy.value_reader_hold(taxonomy.ROLE_CATEGORICAL, cells, frozenset(), 11) == ""


def _at_the_floor(value: str, rows: int = 11) -> str:
    """The hold of a column of 20,000 cells: one value on ``rows`` rows beside one ordinary label holding a figure on all the others (a binary column, as Codex's cases are; a label holding no figure is set aside by the share of cell forms, where one address alone holds the column)."""
    cells = ["Bay 12"] * (20000 - rows) + [value] * rows
    return taxonomy.value_reader_hold(taxonomy.ROLE_BINARY, cells, frozenset(), 11)


def _the_figure_guard(cell: str) -> int:
    """Repair 1's dispatch, the mutant of Codex's item 4: a cell holding no figure is set aside before the address reader reads it."""
    if not taxonomy._holds_a_figure(cell):
        return -1
    return _REAL_FORMS(cell)


_REAL_FORMS = taxonomy._value_forms_of_a_cell


def test_every_address_form_holds_its_column_at_the_floor(monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 4 (the orchestrator's LANE CZ-E RULINGS 6 (4)): every form the address reader admits (`network_address_forms`: hardware addresses by colons, hyphens or points in letters, figures or both; colon addresses of letters alone, around `::`) on exactly the floor's 11 rows beside 19,989 ordinary labels holds the column, alone or after `login from`; on 10 rows it is no published level and holds nothing; RED on repair 1's dispatch (the figure guard), which published each address of letters alone."""
    forms_read = readers.network_address_forms()[::7]
    assert len(forms_read) >= 60
    assert [form for form in forms_read if _at_the_floor(form) != taxonomy.HELD_NETWORK_ADDRESSES] == []
    assert [form for form in forms_read if _at_the_floor(f"login from {form}") != taxonomy.HELD_IDENTIFIER_WORDS] == []
    assert [form for form in forms_read[:10] if _at_the_floor(form, 10)] == []
    monkeypatch.setattr(taxonomy, "_value_forms_of_a_cell", _the_figure_guard)
    letters = [form for form in forms_read if not taxonomy._holds_a_figure(form)]
    assert letters and [form for form in letters if _at_the_floor(form) != taxonomy.HELD_NETWORK_ADDRESSES] == letters


@pytest.mark.parametrize(("value", "words"), [
    ("home 41.66123\xb0 N, 91.53210\xb0 W", taxonomy.WORDS_COORDINATE_PAIR),
    ("home 41.66123 N, 91.53210 W", taxonomy.WORDS_COORDINATE_PAIR),
    ("lat=41.66123, lon=-91.53210", taxonomy.WORDS_COORDINATE_PAIR),
    ("seen at POINT (41.66123 -91.53210) today", taxonomy.WORDS_COORDINATE_PAIR),
    ("wife Jo notified", taxonomy.WORDS_RELATIVE_NAME),
    ("per wife Li today", taxonomy.WORDS_RELATIVE_NAME),
    ("Gapesam,   J scheduled", taxonomy.WORDS_FAMILY_AND_INITIAL),
    ("call +44 (0)20 7946 0958", taxonomy.WORDS_TELEPHONE),
    ("contact +44 (20) 7946 0958", taxonomy.WORDS_TELEPHONE),
])
def test_codex_s_text_forms_hold_their_column_at_the_floor(value: str, words: str) -> None:
    """Codex's items 5 and 6 (the orchestrator's LANE CZ-E RULINGS 6 (5) and (6)): a home point in an admitted spelling among words, a relative's name of two letters, a family name with three spaces after its comma, an international number with a bracketed group -- each read in its form and, on exactly the floor's 11 rows beside 19,989 ordinary labels, holding the column by its words (repair 1 published each, count 11)."""
    assert taxonomy.identifier_words_form(value) == words
    assert _at_the_floor(value) == taxonomy.HELD_IDENTIFIER_WORDS


def test_the_text_forms_are_red_on_their_mutants(monkeypatch: pytest.MonkeyPatch) -> None:
    """The mutants of Codex's items 5 and 6: a pair read over two words at most (`_PAIR_WINDOW` 2), a name after a relative's word of three letters at least, every run of spaces kept as written, and no bracketed group in an international number -- each leaves its form unread."""
    with monkeypatch.context() as patched:
        patched.setattr(taxonomy, "_PAIR_WINDOW", 2)
        patched.setattr(taxonomy, "_PAIR_OPENINGS_BACK", 0)
        assert taxonomy.identifier_words_form("home 41.66123\xb0 N, 91.53210\xb0 W") == ""
    with monkeypatch.context() as patched:
        patched.setattr(taxonomy, "_RELATIVE_NAME_LETTERS", 3)
        assert taxonomy.identifier_words_form("wife Jo notified") == ""
    with monkeypatch.context() as patched:
        patched.setattr(taxonomy, "_value_body", lambda text: taxonomy.parsing.trimmed(taxonomy.plain_marks(text)))
        assert taxonomy.identifier_words_form("Gapesam,   J scheduled") == ""
    with monkeypatch.context() as patched:
        patched.setattr(taxonomy, "_INTERNATIONAL_BRACKETED", 0)
        assert taxonomy.identifier_words_form("call +44 (0)20 7946 0958") == ""


def test_a_month_and_a_day_answered_no_dates_frees_the_identifier_words(tmp_path: pathlib.Path,
                                                                      monkeypatch: pytest.MonkeyPatch) -> None:
    """The combined verify's item 3 (d): a column whose question about dates in disguise was answered `no` (``dated_values_no``), holding `seen 3/14 in clinic` on many rows, is NOT held by the identifier words through `build_document` -- an answer is never asked again (RULINGS 4 (2)); red on the mutant wiring the dates switch on whatever the answer."""
    cells = ["seen 3/14 in clinic"] * 300 + ["late arrival"] * 300
    path = tmp_path / "remarks.csv"
    path.write_bytes(zoo.csv_bytes(["remark"], [[cell] for cell in cells]))

    def held(dated_no: "list[str]") -> str:
        reasons: "dict[str, str]" = {}
        profile.build_document(
            reading.read_table(f"{path}"), taxonomy.Settings(), [], top_code=True, five_figures=[], ages_held=[],
            harbor_year=taxonomy.SAFE_HARBOR_REFERENCE_YEAR, harbor_reasons=reasons, ages_established={},
            dated_values_no=dated_no,
        )
        return reasons.get("remark", "")

    assert held([]) == taxonomy.HELD_IDENTIFIER_WORDS
    assert held(["remark"]) != taxonomy.HELD_IDENTIFIER_WORDS
    real = taxonomy.value_reader_hold
    monkeypatch.setattr(taxonomy, "value_reader_hold",
                        lambda role, cells, absent, floor, dates=True: real(role, cells, absent, floor, True))
    assert held(["remark"]) == taxonomy.HELD_IDENTIFIER_WORDS


def test_every_state_s_codes_are_read_and_a_provider_s_number_is_not(monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 9 (the orchestrator's LANE CZ-E RULINGS 6 (7)): the area sweep reads the states' codes frozen in the test (`STATE_CODES_WRITTEN`) and the provider check written there (`provider_check_passes`), never the reader's own: every state's tract and block-group codes are read, ten figures that are a provider's number are not; red when a state is taken from the reader's list, when its provider check passes everything, and when it passes nothing."""
    codes = readers.area_code_spellings()
    providers = readers.provider_numbers_like_areas()
    assert [code for code in codes if not taxonomy.an_area_code(code)] == []
    assert [number for number in providers if taxonomy.an_area_code(number)] == []
    with monkeypatch.context() as patched:
        patched.setattr(taxonomy, "STATE_FIPS", taxonomy.STATE_FIPS - {"17"})
        assert [code for code in codes if not taxonomy.an_area_code(code)]
    with monkeypatch.context() as patched:
        patched.setattr(taxonomy, "a_provider_number", lambda figures: True)
        assert [code for code in codes if not taxonomy.an_area_code(code)]
    with monkeypatch.context() as patched:
        patched.setattr(taxonomy, "a_provider_number", lambda figures: False)
        assert [number for number in providers if taxonomy.an_area_code(number)]


@pytest.mark.parametrize("text", [
    "12 Jan", "2031-03-14 09:15", "2031-03-14 9:15 AM", "03/14/2031 9:15AM", "3/14/2031 9:15:30\u202fAM",
    "14/03/2031 09:15:30.123", "2031-03-14T9:15 AM", "Mar 14", "14-Mar",
])
def test_a_date_or_a_stamp_alone_is_the_date_rules(text: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """The statistics check of lane CZ-E, item 1: a level whose every word is a date or a clock part is the date rules', never read for a month and a day (red on the mutant without `date_counts.a_date_alone`); a remark holding a date beside other words still is, but not where the column's question about dates was answered."""
    from synthtwin import date_counts

    assert taxonomy.identifier_words_form(text) == ""
    assert taxonomy.identifier_words_form(f"seen {text} in clinic") == taxonomy.WORDS_MONTH_AND_DAY
    assert taxonomy.identifier_words_form(f"seen {text} in clinic", False) == ""
    monkeypatch.setattr(date_counts, "a_date_alone", lambda text: False)
    assert taxonomy.identifier_words_form(text) == taxonomy.WORDS_MONTH_AND_DAY


def _by_cells(serials: "dict[str, bool]", layouts: "dict[str, int]", cell: str) -> None:
    serials[cell] = True
    layout = taxonomy._serial_layout(cell)
    layouts[layout] = layouts.get(layout, 0) + 1


def test_keys_beside_one_repeated_level_are_no_serials(monkeypatch: pytest.MonkeyPatch) -> None:
    """The statistics check of lane CZ-E, item 2: a column of one layout's record keys beside ONE serial-shaped level repeated on half the rows is no column of serials -- a maker's layout is counted by different serials, never by cells (red on the mutant counting cells)."""
    cells = [f"K{1000000 + place}" for place in range(10000)] + ["R100000X200000"] * 10000
    assert taxonomy.value_reader_hold(taxonomy.ROLE_CATEGORICAL, cells, frozenset(), 11) == ""
    monkeypatch.setattr(taxonomy, "_count_a_serial", _by_cells)
    assert taxonomy.value_reader_hold(taxonomy.ROLE_CATEGORICAL, cells, frozenset(), 11) == taxonomy.HELD_DEVICE_SERIALS


def test_a_column_of_scores_is_no_column_of_dates(monkeypatch: pytest.MonkeyPatch) -> None:
    """The orchestrator's LANE CZ-E RULINGS 4 (3) (ii) as RULINGS 7 (2) narrows it: a pair over a figure is a score where the column writes the same words with 0 over that figure (`pain 7/10` beside `pain 0/10`), read as no month and a day -- the statistics check's family, 28 columns of every score of a scale; a date beside the scores stays read; red on the mutant reading no scores."""
    for column in readers.score_columns():
        cells = [level for level in column for _row in range(12)]
        assert taxonomy.levels_holding_identifier_words(cells, frozenset(), 11) == [], column[:3]
    beside = [level for level in readers.score_columns()[0] + ["seen 3/14 in clinic"] for _row in range(12)]
    assert taxonomy.levels_holding_identifier_words(beside, frozenset(), 11) == ["seen 3/14 in clinic"]
    monkeypatch.setattr(taxonomy, "score_templates", lambda levels: frozenset())
    cells = [level for level in readers.score_columns()[0] for _row in range(12)]
    assert taxonomy.levels_holding_identifier_words(cells, frozenset(), 11)


def _repair_1_scores(levels: "list[str]") -> "frozenset[str]":
    """Repair 1's score rule, the mutant of the second repair's item 1: every pair over a figure three different figures or more stand over is a score, whatever its words."""
    overs: "dict[str, set[str]]" = {}
    pairs: "list[tuple[str, int, int, str]]" = []
    for level in levels:
        body = taxonomy._value_body(level)
        for start, end, over, under in taxonomy._score_pairs(body):
            overs.setdefault(under, set()).add(over)
            pairs += [(body, start, end, under)]
    return frozenset(taxonomy._score_key(body, start, end, under) for body, start, end, under in pairs
                     if len(overs[under]) >= 3)


def _visits(months: "tuple[int, ...]", days: "tuple[int, ...]", day_first: bool = False) -> "list[str]":
    return [f"seen {day}/{month}" if day_first else f"seen {month}/{day}" for month in months for day in days]


def test_dates_sharing_a_day_are_held_and_never_scores(monkeypatch: pytest.MonkeyPatch) -> None:
    """The combined verify's item 1 (BLOCKER; the orchestrator's LANE CZ-E RULINGS 7 (2)): its two shapes at 20,000 cells -- 24 visit remarks `seen M/D` with no year, four days in six months, each on many rows, month first and day first; and each of 1,000 people's own `seen M/D` on 4 to 20 of their rows -- hold the column by their words; RED on repair 1's rule (`_repair_1_scores`), which read every such date as a score."""
    shared = _visits((1, 3, 5, 7, 9, 11), (3, 8, 14, 21))
    day_first = _visits((1, 3, 5, 7, 9, 11), (13, 18, 24, 28), True)
    own: "list[str]" = []
    for person in range(1000):
        own += [f"seen {person % 12 + 1}/{person % 28 + 1}"] * (4 + person % 17)
    columns = {
        "shared": [level for level in shared for _row in range(500)] + ["late arrival"] * 8000,
        "day first": [level for level in day_first for _row in range(500)] + ["late arrival"] * 8000,
        "own": own + ["late arrival"] * max(20000 - len(own), 0),
    }
    for name, cells in columns.items():
        assert taxonomy.value_reader_hold(taxonomy.ROLE_CATEGORICAL, cells, frozenset(), 11) == \
            taxonomy.HELD_IDENTIFIER_WORDS, name
    assert len(taxonomy.levels_holding_identifier_words(columns["shared"], frozenset(), 11)) == 24
    monkeypatch.setattr(taxonomy, "score_templates", _repair_1_scores)
    assert [name for name, cells in columns.items()
            if taxonomy.value_reader_hold(taxonomy.ROLE_CATEGORICAL, cells, frozenset(), 11)] == []


def test_no_date_remark_of_the_generated_columns_is_read_as_a_score() -> None:
    """The score rule's own check (RULINGS 7 (2): a rule that unreads any placed date remark is withdrawn): over every generated column of date remarks (`date_remark_columns`: the 48 dates of four days a month, 200 columns of 30 random dates, every spelling of the month-and-day sweep a template, dates beside scores sharing their figures), every remark read alone is read in its column too."""
    unread: "list[str]" = []
    for column, dates in readers.date_remark_columns():
        scores = taxonomy.score_templates(column)
        unread += [level for level in dates
                   if taxonomy.identifier_words_form(level) and not taxonomy.identifier_words_form(level, True, scores)]
    assert unread == [], (len(unread), unread[:6])
    assert sum(len(dates) for _column, dates in readers.date_remark_columns()) >= 10000


def test_the_clinical_abbreviations_are_no_initials(monkeypatch: pytest.MonkeyPatch) -> None:
    """The orchestrator's LANE CZ-E RULINGS 4 (3) (iii): the statistics check's dotted clinical abbreviations of three letters or more (132: `I.C.U. consult`, `A.M.A. eval`) are read as no initials, red on the mutant without them in the closed list; those of two letters (28: `P.T. eval`), a person's two initials' form, stay read (adding them left seeded initials unread: the ruling's bar)."""
    spelled = readers.dotted_abbreviation_spellings()
    assert len(spelled) == 132
    assert [text for text in spelled if taxonomy.identifier_words_form(text)] == []
    two = readers.dotted_abbreviation_spellings(readers.TWO_LETTER_ABBREVIATIONS)
    assert len([text for text in two if taxonomy.identifier_words_form(text) == taxonomy.WORDS_INITIALS]) == 28
    monkeypatch.setattr(taxonomy, "NOT_INITIALS", taxonomy.NOT_INITIALS - readers.abbreviation_capitals())
    assert len([text for text in spelled if taxonomy.identifier_words_form(text)]) == 132


@pytest.mark.parametrize("text", [
    "MR BRAIN WO CONTRAST", "CARDIPINE DR TABLET", "MS Clinic", "Doctor Note",
])
def test_the_stated_title_like_prefixes_are_read(text: str) -> None:
    """The families the title prefix rule would free stay read (plan P4-D472 (c)): that rule left 4 of 41 seeded titles of a remark column unread, so by RULINGS 4 (3)'s bar it is not taken; `no` frees each column."""
    assert taxonomy.identifier_words_form(text) == taxonomy.WORDS_TITLE


@pytest.mark.parametrize("text", [
    "Kukun Velegin to call back", "ride by Kukun Velegin", "Gapesam knee protocol", "Surname KT knee scope",
    "dr smith to review", "per KT today", "SMITH, JOHN; DOE, JANE", "Excision, Complete [62204]",
])
def test_the_residual_stays_unread(text: str) -> None:
    """What stays open (plan P4-D472): a name written first, after a verb or a preposition, a bare family name, initials with no points and no comma, a title and a name in small letters, a family name and a given name with no middle initial (a category in title case after a comma is written so)."""
    assert taxonomy.identifier_words_form(text) == ""


# -- (D) the bands -------------------------------------------------------------


def test_every_generated_band_reads_its_ages() -> None:
    """Every generated band reads its first and last age (-1 open upward), in thousands."""
    written = readers.age_band_spellings()
    assert len(written) >= 1000
    wrong = []
    for text, start, end in written:
        band = taxonomy.an_age_band(text)
        if band is None or (band.start, band.end) != (start, end):
            wrong += [(text, band)]
    assert not wrong, (len(wrong), wrong[:8])


def test_the_bands_are_red_on_their_mutant(monkeypatch: pytest.MonkeyPatch) -> None:
    """The mutant: with no band read, no band column is in the age reach."""
    cells = ["0-4", "85-89", "90-94", "95-99", "100-104"] * 30
    assert taxonomy.safe_harbor_reach(cells, False, frozenset(), 11) == taxonomy.SAFE_HARBOR_AGES
    monkeypatch.setattr(taxonomy, "an_age_band", lambda text: None)
    assert taxonomy.safe_harbor_reach(cells, False, frozenset(), 11) == ""


@pytest.mark.parametrize(("cells", "pooled"), [
    (["0-4", "85-89", "90-94", "95-99", "100-104"], ["0-4", "85-89", "90+", "90+", "90+"]),
    (["<18 yrs", "18-44 yrs", "85-89 yrs", "90-94 yrs", ">= 95 yrs"],
     ["<18 yrs", "18-44 yrs", "85-89 yrs", ">= 90 yrs", ">= 90 yrs"]),
    (["80-89", "90-99", "100+"], ["80-89", "90+", "90+"]),
    (["age 85-89", "age 90-94", "age 95 and over"], ["age 85-89", "age 90 and over", "age 90 and over"]),
    (["85-89 years", "90-94 years", "95-99 years"], ["85-89 years", "90+ years", "90+ years"]),
])
def test_bands_from_90_are_written_as_one_band_in_the_source_s_form(cells: "list[str]", pooled: "list[str]") -> None:
    """The top-code's band pooling: every band from 90 is the one band past 89, in the column's own form."""
    assert taxonomy.age_bands_past_89(cells * 20, frozenset())
    assert taxonomy.top_coded_cells(cells) == pooled


_FIVES = [f"{start}-{start + 4}" for start in range(0, 100, 5)]


@pytest.mark.parametrize("top", [
    "100 & over", "(100, 105]", "90 and up", "90 or above", "100 and up", "100 or above", "100 & older", "100up",
    "100 or greater", "100 and greater", "[100, 105)",
])
def test_each_top_spelling_leaves_one_category_past_89(top: str) -> None:
    """The orchestrator's LANE CZ-E RULINGS 3 (2): five-year groups topped by each spelling are in the band reach, and the top-code leaves exactly one category past 89."""
    cells = (_FIVES + [top]) * 20
    assert taxonomy.age_bands_past_89(cells, frozenset())
    written = set(taxonomy.top_coded_cells(cells))
    assert len([cell for cell in written if taxonomy._past_89_unread(cell)]) == 1, written


@pytest.mark.parametrize(("cells", "pooled"), [
    (["0-24", "25-49", "50-74", "75-99", "100+"], ["0-24", "25-49", "50-74", "75+", "75+"]),
    (["(0, 18]", "(18, 45]", "(45, 65]", "(65, 90]", "(90, 95]", "(95, 100]", "(100, 105]"],
     ["(0, 18]", "(18, 45]", "(45, 65]", "66+", "66+", "66+", "66+"]),
])
def test_a_band_holding_90_joins_the_one_band(cells: "list[str]", pooled: "list[str]") -> None:
    """A closed band holding 90 and starting before it joins the one band past 89, written from its own first age, so that band is never the older ages alone (`75-99` beside `90+` would say `90+` holds those of 100 and over)."""
    assert taxonomy.top_coded_cells(cells * 20)[: len(cells)] == pooled


@pytest.mark.parametrize("unread", ["100 a 104", "100 bis 104", "100-104 a\u00f1os"])
def test_an_unread_top_in_a_column_of_bands_is_pooled(unread: str) -> None:
    """A top group the band grammar does not read, in a column of bands past 89, is written as the one band too: it names an age past 89 by its first figures."""
    cells = (_FIVES + [unread]) * 20
    assert taxonomy.age_bands_past_89(cells, frozenset())
    written = set(taxonomy.top_coded_cells(cells))
    assert unread not in written and len([cell for cell in written if taxonomy._past_89_unread(cell)]) == 1


@pytest.mark.parametrize("cells", [
    ["0-17", "18-44", "45-64", "65-89", "90-94", "95-99", "100+"],
    ["0-17", "18-44", "45-64", "65-84", "85-89", "90-94", "95-99", "100 and up"],
    ["(0, 18]", "(18, 45]", "(45, 65]", "(65, 89]", "(89, 94]", "(94, 99]", "(99, 104]"],
    ["<18", "18-24"] + [f"{start}-{start + 4}" for start in range(25, 105, 5)],
    ["<18", "18-29"] + [f"{start}-{start + 9}" for start in range(30, 100, 10)] + ["100+"],
    ["[0, 5)"] + [f"({start - 1}, {start + 4}]" for start in range(5, 105, 5)],
])
def test_band_schemes_no_unit_word_names_are_ages(cells: "list[str]", monkeypatch: pytest.MonkeyPatch) -> None:
    """The orchestrator's LANE CZ-E RULINGS 3 (5) and the statistics check's item 5: groups of unequal widths chained from 0, intervals, five- or ten-year groups opening at 18 below `<18`: read as ages by their spans alone (red on the mutant reading no span)."""
    assert taxonomy.age_bands_past_89(cells * 20, frozenset())
    monkeypatch.setattr(taxonomy, "_bands_read_as_ages", lambda spans: False)
    assert not taxonomy.age_bands_past_89(cells * 20, frozenset())


@pytest.mark.parametrize(("name", "aged"), [
    ("agegrp", True), ("AGEGROUP", True), ("ageband", True), ("AGEGRP", True), ("age_group", True), ("agecat", True),
    ("agent", False), ("agency", False), ("stage", False), ("page", False),
])
def test_a_name_running_age_into_a_group_s_word_is_an_age(name: str, aged: bool) -> None:
    """The statistics check's item 5: `age` run together with a group's word names ages; `agent`, `agency`, `stage` do not."""
    assert taxonomy.named_as_an_age(name) is aged


@pytest.mark.parametrize("cells", [
    ["<60", "60-100", ">100"],
    ["0-17", "18-44", "45-64", "65-89", "90+"],
    ["100-200 mg", "200-300 mg"],
    ["1-2", "3-5", "6-10"],
    ["0-4", "85-89", "90-94", "12", "40", "71", "33", "58", "64"],
])
def test_no_column_is_read_as_age_bands_without_a_band_past_89_to_pool(cells: "list[str]") -> None:
    """Bands of another measure, `90+` alone, ranges of a dose or a count, and bands on fewer than two in three of the cells: no band reach."""
    assert not taxonomy.age_bands_past_89(cells * 20, frozenset())


@pytest.mark.parametrize(("cells", "start"), readers.ADULT_SCHEMES)
def test_adult_groups_under_a_neutral_name_are_ages(cells: "list[str]", start: int) -> None:
    """The combined verify's item 2 (BLOCKER; the orchestrator's LANE CZ-E RULINGS 7 (3)): groups of unequal widths opening at 16, 18, 20 or 21 under no unit word and no name of ages are read as ages -- four closed groups or more chained from an age of 21 or less -- and pooled into ONE band past 89 (the KPI's own reading, `label_reaches_90`), written from the first age of a group holding 90 where one does (`75-99` beside `100+` makes `75+`)."""
    assert taxonomy.age_bands_past_89(cells * 20, frozenset())
    written = sorted(set(taxonomy.top_coded_cells(cells * 20)))
    assert [label for label in written if readers.label_reaches_90(label)] == [f"{start}+"], written


def test_the_adult_groups_are_red_on_the_chain_opening_mutant(monkeypatch: pytest.MonkeyPatch) -> None:
    """The mutant: with a chain opening only at 0 or 1 (`_CHAIN_OPENS_BY` 1, repair 1's rule), the verify's four adult schemes are read as no ages -- three or more bands past 89 published on the first run."""
    monkeypatch.setattr(taxonomy, "_CHAIN_OPENS_BY", 1)
    assert [cells for cells, _start in readers.ADULT_SCHEMES[:4] if taxonomy.age_bands_past_89(cells * 20, frozenset())] == []


def test_a_measure_s_classes_are_no_ages(monkeypatch: pytest.MonkeyPatch) -> None:
    """The combined verify's item 3 (a): a measure's four classes (`<60`, `60-89`, `90-100`, `>100`), three of them closed, are no age bands -- a chain holds four closed bands at least; red on the mutant `_CHAIN_AT_LEAST` 3."""
    cells = ["<60", "60-89", "90-100", ">100"] * 30
    assert not taxonomy.age_bands_past_89(cells, frozenset())
    monkeypatch.setattr(taxonomy, "_CHAIN_AT_LEAST", 3)
    assert taxonomy.age_bands_past_89(cells, frozenset())


def test_two_in_three_of_the_bands_five_or_ten_years_wide_are_ages(monkeypatch: pytest.MonkeyPatch) -> None:
    """The combined verify's item 3 (b): the verify's groups opening `18-24` then five-year groups to `100-104` and `105+` are read as ages; and groups opening at 30, two in three of their cells five or ten years wide and one 20 wide, not chained from 21 or less, are read so by the two-in-three clause alone (red on the mutant asking every closed band to be five or ten years wide)."""
    verify = ["18-24"] + [f"{start}-{start + 4}" for start in range(25, 105, 5)] + ["105+"]
    assert taxonomy.age_bands_past_89(verify * 20, frozenset())
    spans = {(30, 34): 20, (35, 39): 20, (40, 44): 20, (45, 64): 20, (90, 94): 20, (95, 99): 20, (100, -1): 20}
    assert taxonomy._bands_read_as_ages(spans)
    monkeypatch.setattr(taxonomy, "_BULK_TAKEN", taxonomy._BULK_PARTS)
    assert not taxonomy._bands_read_as_ages(spans)


def test_a_band_from_nought_holding_its_bound_chains_on(monkeypatch: pytest.MonkeyPatch) -> None:
    """The combined verify's item 3 (c): a first band open downward reads its ages as written -- `<18` holds 0 to 17, so `18-39` chains on (the verify's groups are read as ages), and `<= 30` holds 30, so `30-49` chains on at its bound (red on the mutant chaining a band on only one past the last's end, `_chains_on`)."""
    verify = ["<18", "18-39", "40-64", "65-84", "85-94", "95+"]
    assert taxonomy.age_bands_past_89(verify * 20, frozenset())
    held_bound = ["<=30", "30-44", "45-59", "60-74", "75-89", "90-104", "105+"]
    assert taxonomy.age_bands_past_89(held_bound * 20, frozenset())
    monkeypatch.setattr(taxonomy, "_chains_on", lambda before, after: after[0] == before[1] + 1)
    assert not taxonomy.age_bands_past_89(held_bound * 20, frozenset())


@pytest.mark.parametrize("bound", ["<90", "< 90", "under 90", "below 90", "less than 90", "Under 90 yrs", "<=89"])
def test_a_strict_bound_keeps_the_younger_their_own_band(bound: str) -> None:
    """Codex's item 1 (the orchestrator's LANE CZ-E RULINGS 6 (1)): 18,000 people under 90 beside 1,000 of 90 to 94 and 1,000 of 95 and over keep their own band -- `<90` holds 0 to 89 -- and the 2,000 past 89 are the one band `90+` (repair 1 read `<90` as holding 90 and wrote one constant band of 20,000)."""
    cells = [bound] * 18000 + ["90-94"] * 1000 + ["95+"] * 1000
    assert taxonomy.age_bands_past_89(cells, frozenset(), True)
    counted: "dict[str, int]" = {}
    for cell in taxonomy.top_coded_cells(cells):
        counted[cell] = counted.get(cell, 0) + 1
    assert counted == {bound: 18000, "90+": 2000}, counted


def test_an_inclusive_bound_holding_90_joins_the_one_band() -> None:
    """...and an inclusive bound holding 90 (`<= 90`) is a band holding 90: it joins the one band past 89, written from its own first age (`0+`), so no category of 90 and older is split."""
    cells = ["<= 90"] * 18000 + ["91-94"] * 1000 + ["95+"] * 1000
    assert sorted(set(taxonomy.top_coded_cells(cells))) == ["0+"]


def test_the_strict_bounds_are_red_on_the_inclusive_mutant(monkeypatch: pytest.MonkeyPatch) -> None:
    """The mutant: with every bound open downward read as holding its age, the generated strict bounds (`downward_band_spellings`) read their last age one too far."""
    monkeypatch.setattr(taxonomy, "_BAND_DOWNWARD", tuple((mark, 0) for mark, _below in taxonomy._BAND_DOWNWARD))
    wrong = [text for text, start, end in readers.downward_band_spellings()
             if (taxonomy.an_age_band(text) or taxonomy.AgeBand(-9, -9, "", False, "")).end != end]
    assert wrong


@pytest.mark.parametrize("place", range(len(readers.unit_band_columns())))
def test_bands_are_read_in_their_unit(place: int) -> None:
    """Codex's item 2 (the orchestrator's LANE CZ-E RULINGS 6 (2)): a band with no unit word is read in the column's unit (its mark: 90 years, 1,080 months, 4,695 weeks, 32,871 days), so bands of months, weeks or days are never pooled at 90; a band writing a unit word of years is read in years in any column (`unit_band_columns`)."""
    cells, mark, past = readers.unit_band_columns()[place]
    assert taxonomy.age_bands_past_89(cells * 20, frozenset(), True, mark) is past
    assert (taxonomy.top_coded_cells(cells, False, frozenset(), mark) != cells) is past


def test_bands_in_months_are_red_on_the_unit_mutant(monkeypatch: pytest.MonkeyPatch) -> None:
    """The mutant: with every band read in years (`_band_cutoff` 90), childhood bands in months are pooled at 90 again (Codex's case: `80-89` to `105+` in a column of ages in months)."""
    cells = ["80-89", "90-94", "95-99", "100-104", "105+"] * 20
    assert not taxonomy.age_bands_past_89(cells, frozenset(), True, 1080)
    monkeypatch.setattr(taxonomy, "_band_cutoff", lambda band, mark=90: 90)
    assert taxonomy.age_bands_past_89(cells, frozenset(), True, 1080)


def test_a_description_made_before_the_band_reading_validates_as_it_did(tmp_path: pathlib.Path,
                                                                        monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 3 (the orchestrator's LANE CZ-E RULINGS 6 (3)): the description the base wrote of an age column declared a code, its band `95-99` published beside its 90 (`OLD_AGES_DESCRIPTION`, 20,000 rows), records no band reading (`top_coded_bands`), so the validator reads its band as written and the source meets every obligation, the band's own among them; RED on reading its band as one band past 89 (repair 1's rule: seven obligations missed)."""
    from synthtwin import contract, validation

    source = tmp_path / "ages.csv"
    source.write_text("age\n" + "\n".join(readers.old_ages_cells()) + "\n", encoding="utf-8", newline="\n")
    described = tmp_path / "ages-profile.json"
    described.write_text(readers.OLD_AGES_DESCRIPTION, encoding="utf-8", newline="\n")
    loaded = contract.load_profile(f"{described}")
    assert not loaded.columns[0].top_coded_bands and loaded.columns[0].top_coded == 90
    outcome = validation.measure(loaded, f"{source}")
    checked = [check for check in outcome.checks if "95-99" in f"{check.subcheck}"]
    assert checked and [check.subcheck for check in outcome.checks if check.verdict == validation.MISSED] == []
    real = taxonomy.top_coded_cells
    # ...the top-code's signature joined at batch 4s's merge (step 9): lane
    # HB2's words, then this lane's bands, which the mutant forces.
    monkeypatch.setattr(taxonomy, "top_coded_cells", lambda cells, comma=False, absent=frozenset(), mark=90,
                        words=True, bands=True: real(cells, comma, absent, mark, words, True))
    again = validation.measure(loaded, f"{source}")
    assert len([check for check in again.checks if check.verdict == validation.MISSED]) >= 6


# -- the description names each kind's columns for the command to hold ------------------------

# The holds each placed column may be named with: the value readers', the
# coordinate pair of two columns (lane SH2's), or the age reach's top-code.
_VALUE_HOLDS = frozenset(taxonomy.VALUE_READER_HOLDS) | {taxonomy.HELD_COORDINATES}
_TOP_CODED = "top-coded"


def _described(kind: str, folder: pathlib.Path, rows: int = zoo.SMOKE_ROWS) -> "dict[str, str]":
    """Each column of a kind's table named for the command to hold, with its hold, or `_TOP_CODED`: the command's first description."""
    header, body = readers.MAKERS[kind](rows, readers.SEED)  # type: ignore[operator]
    path = folder / f"{kind}.csv"
    path.write_bytes(zoo.csv_bytes(header, body))
    reasons: "dict[str, str]" = {}
    document = profile.build_document(
        reading.read_table(f"{path}"), taxonomy.Settings(), [], top_code=True, five_figures=[], ages_held=[],
        harbor_year=taxonomy.SAFE_HARBOR_REFERENCE_YEAR, harbor_reasons=reasons, ages_established={},
    )
    for block in document["columns"]:  # type: ignore[attr-defined]
        if "top_coded" in block and f"{block['name']}" not in reasons:
            reasons[f"{block['name']}"] = _TOP_CODED
        elif f"{block['role']}" in taxonomy.ROLES_PUBLISHING_NOTHING and f"{block['name']}" not in reasons:
            # ...or read as a role that publishes no value: free text.
            reasons[f"{block['name']}"] = f"{block['role']}"
    return reasons


# The kinds read at 600 rows: the sparse addresses' kind is read at 20,000
# rows alone (K-HZ-25), each person's six rows at 600 under the floor's rows.
_DESCRIBED_KINDS = readers.BASE_KINDS + tuple(
    kind for kind in readers.REPAIR_KINDS if kind not in (readers.KIND_SPARSE_NODES, readers.KIND_PLAIN_LABELS)
)


def test_the_price_kind_s_plain_labels_at_600_rows(tmp_path: pathlib.Path) -> None:
    """The price kind (RULINGS 4 (3) (iv)): its scores and dotted abbreviations are named for no hold (the score rule and the closed list free them); its imaging exams', medicines' and services' names are held, the families plan P4-D472 (c) states. On the line of batch 4s (its merge, step 9) the reader of persons' names (lane CZ-F, plan P4-D478) is asked before the value readers and holds the imaging exams' names first (`MR BRAIN` a title before a family name to both): held either way, freed by `no` either way."""
    named = _described(readers.KIND_PLAIN_LABELS, tmp_path)
    assert "score_note" not in named and "abbrev_note" not in named, named
    assert named.get("exam_name") in (taxonomy.HELD_IDENTIFIER_WORDS, taxonomy.HELD_PERSONS_NAMES), named
    for column in ("med_name", "service_name"):
        assert named.get(column) == taxonomy.HELD_IDENTIFIER_WORDS, (column, named)


@pytest.mark.parametrize("kind", _DESCRIBED_KINDS)
def test_each_kind_s_columns_are_named_for_the_command_to_hold(kind: str, tmp_path: pathlib.Path) -> None:
    """At 600 rows (the library path): every column the readers must hold is named, or publishes no value (free text); its price columns are neither."""
    named = _described(kind, tmp_path)
    for column in readers.HELD[kind]:
        assert named.get(column) in _VALUE_HOLDS | {_TOP_CODED} | set(taxonomy.ROLES_PUBLISHING_NOTHING), (
            kind, column, named,
        )
    for column in readers.PRICE.get(kind, ()):
        assert column not in named, (kind, column, named)


def test_with_the_readers_away_no_value_column_is_named(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The mutant of the description: with `value_reader_hold` and the band reach away, the remarks, areas and addresses go unnamed. Since batch 4s's merge (step 9) a band among an age column's numbers is an age of the reach too, so the band reach is away with the band reader away (`a_band_cell`)."""
    monkeypatch.setattr(taxonomy, "value_reader_hold", lambda role, cells, absent, floor, dates=True: "")
    monkeypatch.setattr(taxonomy, "age_bands_past_89", lambda cells, absent, named=False, mark=90: False)
    monkeypatch.setattr(taxonomy, "a_band_cell", lambda cell: None)
    for kind in (readers.KIND_REMARKS, readers.KIND_AREA_CODES, readers.KIND_NODE_ADDRESSES, readers.KIND_SERIALS):
        named = _described(kind, tmp_path)
        assert not [column for column in readers.HELD[kind] if named.get(column) in _VALUE_HOLDS], (kind, named)
    bands = _described(readers.KIND_AGE_BANDS, tmp_path)
    assert "band_text" not in bands and "age_band" not in bands, bands


# -- through the commands a person types ------------------------------------------------


def _bar(seen: "dict") -> None:
    """0 real values written, 0 twin cells equal to one or holding a complete real run, and each held column held or asked."""
    assert seen["profile"] == 0 and seen["generate"] == 0, seen.get("screen")
    for column in readers.HELD[seen["kind"]]:
        counted = seen["columns"][column]
        what = f"{seen['kind']}.{column}, {seen['mode']}: {counted}"
        for found in counted["forms"].values():
            assert found["shown"] == 0 and found["twin_equal"] == 0 and found["runs"] == 0, what
        asked = any("identifier" in one or one == ["no", "yes"] for one in counted["asked"])
        assert asked or counted["role"] in taxonomy.ROLES_PUBLISHING_NOTHING, what


@pytest.mark.parametrize(("kind", "mode"), [
    (readers.KIND_REMARKS, "unanswered"),
    (readers.KIND_AREA_CODES, "truthful"),
    (readers.KIND_POINT_PAIRS + readers.CASES, "truthful"),
    (readers.KIND_NODE_ADDRESSES + readers.CASES, "truthful"),
    (readers.KIND_AGE_BANDS, "unanswered"),
    (readers.SMALLEST[-1], "truthful"),
])
def test_the_bar_through_the_commands_at_600_rows(kind: str, mode: str, tmp_path: pathlib.Path) -> None:
    """Profile, its rounds of answers, generate and validate at 600 rows (a test size under the owner's floor)."""
    _bar(readers.measure(tmp_path / kind, kind, zoo.SMOKE_ROWS, mode, small_tables_refused=False))


def test_the_smallest_remark_table_at_20000_rows(tmp_path: pathlib.Path) -> None:
    """THE ONE 20,000-ROW CASE: a remark written for 11 people or more beside the patient column, unanswered, with the table floor on; every shared remark held by 11 people or more, so the question put is the value readers' (its words the identifier words'), never the few-people rule's (the statistics check of lane CZ-E, item 3: red with `value_reader_hold` away)."""
    seen = readers.measure(tmp_path / "a", readers.SMALLEST[0], zoo.KPI_ROWS, "unanswered")
    _bar(seen)
    counted = seen["columns"]["remark_shared"]
    assert ["no", "yes"] in counted["asked"]
    words = asking._value_reader_seen(asking.BECAUSE_SAFE_HARBOR_IDENTIFIER_WORDS)[:60]
    assert any(words in said for said in counted["saw"]), counted["saw"]


# -- the questions' words ---------------------------------------------------------------


@pytest.mark.parametrize(("hold", "words"), [
    (taxonomy.HELD_IDENTIFIER_WORDS, "a telephone number, a month and a day"),
    # ...its sole trigger may be an address or a point among words (Codex's
    # item 10 of lane CZ-E's review, the orchestrator's LANE CZ-E RULINGS 6 (7)).
    (taxonomy.HELD_IDENTIFIER_WORDS, "a network address, or a latitude and a longitude"),
    (taxonomy.HELD_AREA_CODES, "census tract or block group"),
    (taxonomy.HELD_COORDINATE_PAIRS, "a latitude and a longitude written in one cell"),
    # ...one level the floor's rows share holds a column of points or
    # addresses as most of its values do: the words say both (Codex's item 10).
    (taxonomy.HELD_COORDINATE_PAIRS, "most of them, or one value shared by enough rows to be published"),
    (taxonomy.HELD_NETWORK_ADDRESSES, "network addresses"),
    (taxonomy.HELD_NETWORK_ADDRESSES, "most of them, or one value shared by enough rows to be published"),
    (taxonomy.HELD_DEVICE_SERIALS, "a device's serial number"),
])
def test_each_hold_is_put_its_question_with_its_own_words(hold: str, words: str) -> None:
    """Each hold's reason and its sentence: what was seen, no value, `no` and `yes` offered, held until answered."""
    reason = asking._HELD_BECAUSE[hold]
    assert reason in asking.SH2_HELD_REASONS and reason in asking.SH2_SAFE_HARBOR_REASONS
    question = asking._safe_harbor_question("c", "categorical", reason, 1937)
    text = question.shape
    assert words in text and "held back" in text, text
    assert sorted(choice.answer for choice in question.choices) == ["no", "yes"]


def test_the_age_question_of_bands_says_bands() -> None:
    """A top-coded column of bands is asked in the words of bands: every band from 90 read as one."""
    question = asking._safe_harbor_question("c", "categorical", asking.BECAUSE_SAFE_HARBOR_AGES, 0, 90, False, True, True)
    assert "bands of ages" in question.shape and "one band" in question.shape
    block = {"levels": [{"label": label} for label in ("0-4", "85-89", "90+")]}
    assert asking._bands_published(block)
    assert not asking._bands_published({"levels": [{"label": label} for label in ("12", "45", "90")]})


def test_the_summary_says_a_column_of_bands_is_read_as_one_band(tmp_path: pathlib.Path,
                                                                monkeypatch: pytest.MonkeyPatch) -> None:
    """The summary of a top-coded column of bands says its bands past 89 are read as one band, never as the number 90 (skeptic 1's item 12; red on the mutant reading no level as a band)."""
    from synthtwin import summary

    header, body = readers.MAKERS[readers.KIND_AGE_BANDS](zoo.SMOKE_ROWS, readers.SEED)  # type: ignore[operator]
    path = tmp_path / "bands.csv"
    path.write_bytes(zoo.csv_bytes(header, body))
    document = profile.build_document(
        reading.read_table(f"{path}"), taxonomy.Settings(), [], top_code=True, five_figures=[], ages_held=[],
        harbor_year=taxonomy.SAFE_HARBOR_REFERENCE_YEAR, harbor_reasons={}, ages_established={},
    )
    words = "every band past 89, and a band holding 90, is read as one band"
    assert words in summary.render(document, "")
    monkeypatch.setattr(summary, "_levels_are_bands", lambda column: False)
    assert words not in summary.render(document, "")


def _kpi_driver() -> object:
    """K-HZ-25's driver, loaded as a module (its judge is read here, nothing measured)."""
    import importlib.util

    path = pathlib.Path(__file__).resolve().parents[1] / "tools" / "measurements" / "kpi_value_readers.py"
    spec = importlib.util.spec_from_file_location("kpi_value_readers_under_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(("shown", "twin", "key"), [
    (1, 0, "real_strings_shown"), (0, 200, "twin_cells_with_real_strings"),
])
def test_the_kpi_fails_an_identifier_shown_inside_a_cell(shown: int, twin: int, key: str) -> None:
    """Codex's item 7 (the orchestrator's LANE CZ-E RULINGS 6 (7)): a complete identifier inside a placed cell written in a file (`needles_shown`) or held by a twin cell (`twin_needles`) counts in K-HZ-25's verdict, every whole-cell and run count at 0 (`per Dr Bolumet` publishing `Bolumet` alone, or a twin cell `seen by Bolumet`)."""
    driver = _kpi_driver()
    words = asking._value_reader_seen(asking.BECAUSE_SAFE_HARBOR_IDENTIFIER_WORDS)
    found = {"title|many": {"shown": 0, "twin_equal": 0, "runs": 0, "needles_shown": shown, "twin_needles": twin}}
    seen = {"kind": readers.KIND_REMARKS, "mode": "unanswered", "columns": {
        column: {"forms": found if column == "remark_shared" else {}, "asked": [["no", "yes"]], "role": "categorical",
                 "saw": [words]}
        for column in readers.HELD[readers.KIND_REMARKS]
    }}
    counts = driver.judge(seen)  # type: ignore[attr-defined]
    assert counts[key] == shown + twin and key in driver.FAILING_ON  # type: ignore[attr-defined]


@pytest.mark.parametrize(("needle", "counted"), [
    ("Bolumet", True), ("Velegin", True), ("(201) 555-0123", True), ("03/14/31", True), ("2031-03-14", True),
    ("192.0.2.17", True), ("K.T.", False), ("4/5", False), ("Mar 14", False), ("90-94", False),
])
def test_the_kpi_reads_the_strings_no_made_up_value_writes_by_chance(needle: str, counted: bool) -> None:
    """...the strings the verdict reads are those a made-up twin cell does not write by chance (`distinctive`: a name of five letters or more, seven characters or more); two initials or a month and a day with no year stand inside made-up cells of their layout by chance (`zjvxue dz 10/14/58` holds `4/5`), and their whole cells stay counted."""
    assert readers.distinctive(needle) is counted


@pytest.mark.parametrize(("labels", "past"), [
    (["75-99", "90+"], 2), (["66+", "95-99"], 2), (["(65, 90]", "(90, 95]"], 2), (["0-17", "18-89", "90+"], 1),
    (["<90", "90+"], 1), (["[85, 90)", "90+"], 1), (["<= 90", "91+"], 2), (["100up", "85-89"], 1),
    (["18-44 yrs", ">= 90 yrs"], 1), (["age 85-89", "age 90 and over"], 1), (["Other", "Unknown"], 0),
])
def test_the_kpi_reads_a_category_past_89_on_its_own(labels: "list[str]", past: int,
                                                    monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 8 (the orchestrator's LANE CZ-E RULINGS 6 (7)): K-HZ-25 counts the published categories holding an age of 90 or more by its own reading of their figures and marks (`label_reaches_90`), a category crossing 90 among them (`75-99`, `66+`), with the product's band reader taken away."""
    monkeypatch.setattr(taxonomy, "an_age_band", lambda text: None)
    monkeypatch.setattr(taxonomy, "_past_89_unread", lambda cell, comma=False, mark=90: False)
    assert readers.levels_past_89({"levels": [{"label": label} for label in labels]}) == past


def test_the_zoo_answers_yes_for_a_clinician_s_name() -> None:
    """The zoo's reports table: a reader's name in a signed report is outside Safe Harbor's list but inside the no-real-name rule (plan P4-D445's item 9), so the zoo answers `yes`."""
    table = zoo.table_named("reports")
    assert zoo.names_a_safe_harbor_element(table, "report_text")


# -- BATCH 4s'S MERGE, STEP 9: THE LINE OF LANE HB2 JOINED (the orchestrator's step text, seams (1) to (4); LANE HB2
# RULINGS 7 (4); plan P4-D477 (4) and P4-D472's merge paragraph) -------------------------------------------------

# The lane's two lists before the merge, written out (`plain_marks` read them): its dashes and its spaces.
LANE_DASHES_BEFORE = "\u2013\u2014\u2010\u2011\u2012\u2212\ufe63\uff0d"
LANE_SPACES_BEFORE = (
    "\t\n\r\x0b\x0c\x85\xa0\u1680" + "".join(chr(code) for code in range(0x2000, 0x2010))
    + "\u2028\u2029\u202f\u205f\u2060\u3000\ufeff"
)
# ...and every code point the one definition reads otherwise: as written before and a space now (the space itself,
# read as it is either way; every other control and format character, the four information separators U+001C to
# U+001F and the soft hyphen among them; the lone surrogate code points of the definition's table)...
DEFINITION_SPACES_ADDED = (
    (0x0000, 0x0008), (0x000E, 0x0020), (0x007F, 0x0084), (0x0086, 0x009F), (0x00AD, 0x00AD), (0x0600, 0x0605),
    (0x061C, 0x061C), (0x06DD, 0x06DD), (0x070F, 0x070F), (0x0890, 0x0891), (0x08E2, 0x08E2), (0x180E, 0x180E),
    (0x202A, 0x202E), (0x2061, 0x206F), (0xD800, 0xDFFF), (0xFFF9, 0xFFFB), (0x110BD, 0x110BD), (0x110CD, 0x110CD),
    (0x13430, 0x1343F), (0x1BCA0, 0x1BCAF), (0x1D173, 0x1D17A), (0xE0000, 0xE00FF),
)
# ...and as written before and a dash now: the horizontal bar and the small em dash.
DEFINITION_DASHES_ADDED = ("\u2015", "\ufe58")


def _lane_plain_marks(text: str) -> str:
    """The lane's `plain_marks` before the merge (its two lists): the mutant of the one definition."""
    return "".join("-" if one in LANE_DASHES_BEFORE else " " if one in LANE_SPACES_BEFORE else one for one in text)


def test_the_value_readers_read_the_one_definition_of_a_space_and_a_dash() -> None:
    """THE ONE DEFINITION (the step's seam (4); LANE CZ-E RULINGS 7 (5), LANE CODES-2 RULINGS 7 (4)): over all 1,114,112 code points, `plain_marks` writes each dash of `_SCREEN_DASHES` as `-`, each space of `_SCREEN_SPACE_RANGES` as ` ` and every other character as it is, one by one and in one text of each of the 17 planes; no character is both; the lane's two lists lie inside the definition, which reads otherwise exactly the code points written out above, each as a space or a dash where the lane read it as written."""
    spaces: "set[str]" = set()
    dashes: "set[str]" = set()
    for start in range(0, 0x110000, 0x10000):
        # ...a plane at a time: each code point alone, then the plane in one text.
        expected: "list[str]" = []
        for code in range(start, start + 0x10000):
            character = chr(code)
            read = taxonomy.plain_marks(character)
            if character in taxonomy._SCREEN_DASHES:
                assert read == "-", hex(code)
                dashes.add(character)
            elif taxonomy._a_space_of_the_screen(character):
                assert read == " ", hex(code)
                spaces.add(character)
            else:
                assert read == character, hex(code)
            expected.append(read)
        assert taxonomy.plain_marks("".join(chr(code) for code in range(start, start + 0x10000))) == "".join(expected)
    assert not spaces & dashes
    assert set(LANE_SPACES_BEFORE) <= spaces and set(LANE_DASHES_BEFORE) <= dashes
    assert spaces - set(LANE_SPACES_BEFORE) == {
        chr(code) for start, end in DEFINITION_SPACES_ADDED for code in range(start, end + 1)
    }
    assert dashes - set(LANE_DASHES_BEFORE) - {"-"} == set(DEFINITION_DASHES_ADDED)


def _sampled(reader: str, most: int = 60) -> "list[str]":
    written = SPELLINGS[reader][0]()  # type: ignore[operator]
    return written[:: max(1, len(written) // most)][:most]


def test_every_space_and_dash_of_the_definition_reads_in_each_reader_s_places(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE ONE DEFINITION IN EVERY READER (seam (4); BATCH 4s OWES ADDED 1's class): each reader's generated spellings (60 of each), every ASCII space written as each first and last code point of each range of `_SCREEN_SPACE_RANGES` and every hyphen as each dash of `_SCREEN_DASHES`, are read as the spelling itself is; RED on the lane's lists before the merge, which read the information separators, the soft hyphen and the horizontal bar as written."""
    places = sorted({chr(edge) for start, end in taxonomy._SCREEN_SPACE_RANGES for edge in (start, end)} - {" "})
    variants = [(" ", space) for space in places] + [("-", dash) for dash in taxonomy._SCREEN_DASHES if dash != "-"]
    cells = {reader: _sampled(reader) for reader in sorted(SPELLINGS)}

    def misread() -> int:
        missed = 0
        for reader, spellings in cells.items():
            read = SPELLINGS[reader][1]
            for text in spellings:
                plain = bool(read(text))  # type: ignore[operator]
                for ascii_mark, odd in variants:
                    if ascii_mark in text and bool(read(text.replace(ascii_mark, odd))) != plain:  # type: ignore[operator]
                        missed += 1
        return missed

    assert misread() == 0
    monkeypatch.setattr(taxonomy, "plain_marks", _lane_plain_marks)
    assert misread() > 0


def test_the_two_dashes_the_lane_read_as_written_are_read_so_too(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE UNION (seam (4): reading a character as a dash may hold less): a value holding the horizontal bar or the small em dash is read again with it as written where the plain reading finds no form, so a family name glued by one to the word before it (`seen by<U+2015>Lanezon, A today`), which the lane read as written, is still read (46 of 151,884 generated cells were read so alone); RED without the second reading."""
    cells = [f"seen by{dash}Lanezon, A today" for dash in DEFINITION_DASHES_ADDED]
    assert [taxonomy.identifier_words_form(cell) for cell in cells] == [taxonomy.WORDS_FAMILY_AND_INITIAL] * 2
    monkeypatch.setattr(taxonomy, "_DASHES_KEPT_BEFORE", "")
    assert [taxonomy.identifier_words_form(cell) for cell in cells] == ["", ""]


# The age vocabulary's words before an age and `ages`, the marks after the word, the brackets, and the band forms
# with their first and last age (-1 open upward), for the bands written with the vocabulary (plan P4-D477 (4) (a)).
_BAND_WORD_MARKS = ("", " ", ":", ": ", " : ", "=", " = ", " - ", ":  ")
_BAND_BRACKETS = (("", ""), ("(", ")"), ("[", "]"))
_BAND_FORMS = (
    ("90-94", 90, 94), ("95 to 99", 95, 99), ("100\u2013104", 100, 104), (">= 95", 95, -1), ("95+", 95, -1),
    ("100 and over", 100, -1), ("=> 90", 90, -1), ("<= 17", 0, 17), ("<18", 0, 17), ("[90, 95)", 90, 94),
)


def _age_units() -> "list[str]":
    return sorted({unit for unit, _letter in taxonomy.AGE_VOCABULARY.units} | set(taxonomy.AGE_VOCABULARY.affixes))


def _band_families() -> "list[tuple[str, int, int, str]]":
    """Each word of the vocabulary and `ages` in three cases, each mark, each bracket around the whole and around the band, each band form, and a unit or affix of the vocabulary drawn for each (or none, a point after it or not): the cell, its first and last age, and the unit written."""
    draw = random.Random(4720)
    units = _age_units()
    found: "list[tuple[str, int, int, str]]" = []
    for word in taxonomy.AGE_VOCABULARY.before + taxonomy._BAND_WORDS_BEYOND:
        for case in (str.lower, str.upper, str.title):
            for mark in _BAND_WORD_MARKS:
                for outer_open, outer_close in _BAND_BRACKETS:
                    for inner_open, inner_close in _BAND_BRACKETS:
                        for band, first, last in _BAND_FORMS:
                            if band[:1] == "[" and inner_open:
                                continue
                            unit = draw.choice(("",) + tuple(units))
                            if unit and (unit in taxonomy.AGE_UNIT_WORDS and "/" not in unit) and draw.random() < 0.2:
                                unit += "."
                            tail = f" {unit}" if unit else ""
                            cell = f"{outer_open}{case(word)}{mark}{inner_open}{band}{inner_close}{tail}{outer_close}"
                            # ...the word's `=` glued to `<18` is the band's `=<`, which holds its age.
                            glued = mark == "=" and not inner_open and band == "<18"
                            found += [(cell, first, last + 1 if glued else last, unit)]
    return found


def test_the_band_reader_reads_the_age_vocabulary_and_the_screen_refuses_its_bands(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE VOCABULARY IN THE BAND READER (plan P4-D477 (4) (a); LANE HB2 RULINGS 1 (3) and 7 (2)): every band written with the vocabulary's words, marks and brackets and `ages` (`_band_families`, thousands) is read as the bare band, opened by its word, in the unit its unit word names by `_age_unit_of`; and the generated-families agreement case of P4-D477 (3) widened to the bands: every such band past 89 is refused by the word screen on its three roads. RED with the vocabulary's split away (`age_words_split` reading no word)."""
    vocabulary = taxonomy.AGE_VOCABULARY
    assert {opening for opening, _closing in vocabulary.brackets} <= set(taxonomy._BAND_FIRST_MARKS)
    assert {word[0] for word in vocabulary.before + taxonomy._BAND_WORDS_BEYOND} <= set(taxonomy._BAND_FIRST_LETTERS)
    assert set(taxonomy._BAND_UNITS) == {unit for unit, _letter in vocabulary.units} | set(vocabulary.affixes)
    assert [len(unit) for unit in taxonomy._BAND_UNITS] == sorted((len(unit) for unit in taxonomy._BAND_UNITS), reverse=True)
    families = _band_families()
    assert len(families) > 5000
    for cell, first, last, unit in families:
        band = taxonomy.an_age_band(cell)
        assert band is not None and (band.start, band.end) == (first, last) and band.opened, (cell, band)
        letter = taxonomy._age_unit_of(unit) if unit else ""
        assert (taxonomy._age_unit_of(band.unit) if band.unit else "") == letter, (cell, band.unit)
        if first >= 90 and letter in ("", "y"):
            assert taxonomy._band_is_past_89(band), cell
            assert not taxonomy.passes_the_word_screen(cell), cell
            assert not taxonomy.passes_the_word_screen(cell, False), cell
            assert taxonomy._a_shape_no_code_wears(cell), cell
    monkeypatch.setattr(taxonomy, "age_words_split", lambda cell: ("", cell))
    assert sum(1 for cell, _first, _last, _unit in families if taxonomy.an_age_band(cell) is not None) == 0


def test_one_unit_for_the_bands_and_the_ends(monkeypatch: pytest.MonkeyPatch) -> None:
    """ONE DEFINITION OF AN AGE'S UNIT (the step's seam (3)): for every unit word and affix of the vocabulary, with a point after it or not, the band `90-94 <unit>` and the number `95 <unit>` are read alike (both or neither) and in the same unit, the band's cut at 90 years the number's mark in every column's unit (`_band_cutoff`, `age_mark`), as the ends are pooled in it; a band with no unit word is read in the column's unit as a bare number is. RED on the lane's units before the merge (years alone): `90-94 months` was no band."""
    agreed = 0
    for unit in _age_units():
        for point in ("", "."):
            band = taxonomy.an_age_band(f"90-94 {unit}{point}")
            read = taxonomy.safe_harbor_number(f"95 {unit}{point}", False, True, True)
            assert (band is None) == (read is None), (unit, point)
            if band is None or read is None:
                continue
            assert taxonomy._age_unit_of(band.unit) == taxonomy._cell_age_unit(read), (unit, point)
            for mark in taxonomy.TOP_CODE_MARKS:
                assert taxonomy._band_cutoff(band, mark) == taxonomy.age_mark(read, mark), (unit, point, mark)
            agreed += 1
    assert agreed >= 90
    bare = taxonomy.an_age_band("90-94")
    plain = taxonomy.safe_harbor_number("95", False)
    assert bare is not None and plain is not None
    assert [taxonomy._band_cutoff(bare, mark) for mark in taxonomy.TOP_CODE_MARKS] == [
        taxonomy.age_mark(plain, mark) for mark in taxonomy.TOP_CODE_MARKS] == list(taxonomy.TOP_CODE_MARKS)
    monkeypatch.setattr(taxonomy, "_BAND_UNITS", (
        "years old", "year old", "yrs old", "years", "year", "y/o", "y.o.", "y.o", "yrs.", "yrs", "yr.", "yr", "yo", "y"))
    assert taxonomy.an_age_band("90-94 months") is None


# The split's generated cells of lane HB2's verify (C4): seven spellings of the two words, 21 separators, five outer
# frames, four inner brackets and 20 band forms, 58,800 cells.
_SPLIT_WORDS = ("age", "Age", "AGE", "aGe", "aged", "Aged", "AGED")
_SPLIT_SEPARATORS = ("", " ", "  ", ":", ": ", " : ", "=", " = ", "-", " - ", "\u00a0", ":\u2009", " \u2013 ", "\u2014",
                     "\u2212", "\u3000", "\u200b", "\ufeff", "\t", "\u2011", "\u202f:\u202f")
_SPLIT_FRAMES = (("", ""), ("(", ")"), ("[", "]"), ("( ", " )"), ("[\u00a0", "]"))
_SPLIT_INNER = (("", ""), ("(", ")"), ("[", "]"), ("( ", ")"))
_SPLIT_BANDS = ("90-94", "90\u201394", "90 - 94", "90 to 94", "95+", "100+", ">= 95", ">=95", "\u226595", "\u2265 95", "> 89",
                "<18", "+90", "90 and over", "90 or older", "90-94 yrs", "90+", "\u2264 17", "=> 90", "95")


def _split_cells() -> "list[str]":
    return [f"{outer[0]}{word}{separator}{inner[0]}{band}{inner[1]}{outer[1]}" for word in _SPLIT_WORDS
            for separator in _SPLIT_SEPARATORS for outer in _SPLIT_FRAMES for inner in _SPLIT_INNER for band in _SPLIT_BANDS]


def test_the_split_reads_a_band_s_two_marks_after_a_mark_or_a_bracket(monkeypatch: pytest.MonkeyPatch) -> None:
    """C4 (lane HB2's verify; plan P4-D477 (4) (b)): over the 58,800 generated cells the split gives every cell its word, the two parts joining to the cell, `=>` after a mark or an inner bracket among them (`Age: => 90`, `Age (=> 90)`), and the band reader reads each `=>` cell from 90; RED on the split that reads `=>` and `=<` as no band's mark (2,660 cells split as no word)."""
    cells = _split_cells()
    assert len(cells) == 58800
    for cell in cells:
        word, rest = taxonomy.age_words_split(cell)
        assert word and word + rest == cell, repr(cell)
    marked = [cell for cell in cells if "=> 90" in cell]
    assert marked and all(getattr(taxonomy.an_age_band(cell), "start", -1) == 90 for cell in marked)
    monkeypatch.setattr(taxonomy, "_AGE_BAND_TWO_MARKS", ())
    assert sum(1 for cell in cells if taxonomy.age_words_split(cell)[0] == "") == 2660


# THE COMBINED CASE (the orchestrator's LANE HB2 RULINGS 7 (4)): 1,000 people of 20 rows aged 18 to 104, each person's
# band in each column: lane CZ-E's bands with lane HB2's words (and without), and HB2's `Age NN` mixed with the bands.
COMBINED_PEOPLE = 1000
COMBINED_ROWS = 20


def _combined_ages() -> "list[int]":
    return [18 + (who * 7919) % 87 for who in range(COMBINED_PEOPLE)]


def _combined_band(age: int, written: str, top: str) -> str:
    for first, last in ((18, 44), (45, 64), (65, 89), (90, 94)):
        if first <= age <= last:
            return written.format(f"{first}-{last}")
    return top


COMBINED_COLUMNS = {
    # ...HB2's two spellings, as the verify wrote them: a column of bands with an age word, and `Age NN` beside them.
    "age_group": lambda age: _combined_band(age, "Age {}", "age >= 95"),
    "age_mixed": lambda age: f"Age {age}" if age < 90 else ("Age 90-94" if age < 95 else "age >= 95"),
    # ...and a bracketed word with a mark, the words with a unit, and bands with no word at all.
    "age_framed": lambda age: _combined_band(age, "[AGED: {}]", "[AGED: 95+]"),
    "band_years": lambda age: _combined_band(age, "ages {} years", "ages 95 years and over"),
    "age_bare": lambda age: f"{age}" if age < 90 else ("90-94" if age < 95 else "95+"),
}


def _combined_cells(column: str) -> "list[str]":
    return [COMBINED_COLUMNS[column](age) for age in _combined_ages() for _row in range(COMBINED_ROWS)]


def _past_89_spellings(column: str) -> "frozenset[str]":
    return frozenset(COMBINED_COLUMNS[column](age) for age in _combined_ages() if age >= 90)


def test_the_combined_case_of_bands_and_age_words_at_the_unit_level(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE COMBINED CASE, EVERY SPELLING (LANE HB2 RULINGS 7 (4)): each column of `COMBINED_COLUMNS` (20,000 cells) is in the age reach, and its top-code writes no real band past 89 and every younger cell as written; RED with lane CZ-E's band reader away (`a_band_cell` reading none) and with lane HB2's age words away (`age_words_split` and `_age_word_at` reading no word), each on the columns it reads."""

    def outcome() -> "dict[str, tuple[str, int]]":
        found = {}
        for column in COMBINED_COLUMNS:
            cells = _combined_cells(column)
            reach = taxonomy.safe_harbor_reach(cells, False, frozenset(), 11)
            coded = taxonomy.top_coded_cells(cells)
            past = _past_89_spellings(column)
            found[column] = (reach, sum(1 for cell in coded if cell in past))
        return found

    head = outcome()
    assert head == {column: (taxonomy.SAFE_HARBOR_AGES, 0) for column in COMBINED_COLUMNS}, head
    for column in COMBINED_COLUMNS:
        coded = taxonomy.top_coded_cells(_combined_cells(column))
        assert all(written == cell for written, cell in zip(coded, _combined_cells(column))
                   if cell not in _past_89_spellings(column)), column
    with monkeypatch.context() as away:
        away.setattr(taxonomy, "a_band_cell", lambda cell: None)
        without_bands = outcome()
    assert all(without_bands[column] != (taxonomy.SAFE_HARBOR_AGES, 0) for column in COMBINED_COLUMNS), without_bands
    with monkeypatch.context() as away:
        away.setattr(taxonomy, "age_words_split", lambda cell: ("", cell))
        away.setattr(taxonomy, "_age_word_at", lambda text: -1)
        without_words = outcome()
    for column in ("age_group", "age_mixed", "age_framed"):
        assert without_words[column] != (taxonomy.SAFE_HARBOR_AGES, 0), (column, without_words)


def _combined_run(folder: pathlib.Path, person: bool, answered: bool) -> "dict[str, object]":
    """The combined table (with the person column or not) through the commands a person types, nobody at the keyboard, the table floor on: profile, one round answering `yes` to every Safe Harbor question where ``answered``, and generate at seed 0; the texts written, the questions put to each column, and the twin's cells."""
    import unanswered_identifier_shapes as shapes
    from synthtwin import cli

    folder.mkdir(parents=True, exist_ok=True)
    header = (["sid"] if person else []) + list(COMBINED_COLUMNS)
    body = []
    for who, age in enumerate(_combined_ages()):
        for _row in range(COMBINED_ROWS):
            body += [([f"P{who:05d}"] if person else []) + [COMBINED_COLUMNS[column](age) for column in COMBINED_COLUMNS]]
    source = folder / "bands.csv"
    source.write_bytes(zoo.csv_bytes(header, body))
    described, questions = folder / "bands-profile.json", folder / "bands-questions.json"
    screen = io.StringIO()
    texts: "list[str]" = []
    asked: "dict[str, list[list[str]]]" = {}

    def read_round() -> None:
        texts.extend([described.read_text(encoding="utf-8"), questions.read_text(encoding="utf-8"),
                      (folder / "bands-profile.txt").read_text(encoding="utf-8")])
        for entry in zoo._entries(json.loads(questions.read_text(encoding="utf-8"))):
            asked.setdefault(f"{entry.get('column', '')}", []).append(sorted(zoo._offered(entry)))

    with shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        assert cli.main(["profile", f"{source}", "--replace"], small_tables_refused=True) == 0
        read_round()
        if answered:
            document = json.loads(questions.read_text(encoding="utf-8"))
            for entry in zoo._entries(document):
                offered = sorted(set(zoo._offered(entry)) - zoo.AGE_UNIT_ANSWERS)
                if f"{entry.get('column', '')}" in COMBINED_COLUMNS and offered == ["no", "yes"]:
                    entry["your_answer"] = "yes"
            questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
            assert cli.main(["profile", f"{source}", "--replace", "--answers", f"{questions}"], small_tables_refused=True) == 0
            read_round()
        assert cli.main(["generate", f"{described}", "--replace", "--seed", "0"], small_tables_refused=True) == 0
    texts += [screen.getvalue()] + [(folder / name).read_text(encoding="utf-8")
                                    for name in ("bands-twin-report.txt", "bands-twin-quality.txt") if (folder / name).is_file()]
    with open(folder / "bands-twin.csv", encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    twin = {name: [row[place] for row in rows[1:]] for place, name in enumerate(rows[0])}
    return {"texts": texts, "asked": asked, "twin": twin}


@pytest.mark.parametrize(("person", "answered"), [(True, False), (True, True), (False, False), (False, True)])
def test_the_combined_case_through_the_commands_at_20000_rows(person: bool, answered: bool, tmp_path: pathlib.Path) -> None:
    """THE COMBINED CASE THROUGH THE COMMANDS (LANE HB2 RULINGS 7 (4)): `Age 90-94` and `age >= 95` as a column of bands and beside `Age NN`, and the other spellings of `COMBINED_COLUMNS`, 1,000 people of 20 rows, with the person column and without, unanswered and answered `yes`: each column is put its Safe Harbor question, and no real band past 89 is shown in any file or on the screen or written by the twin (on the line before the merge, 1,080 and 360 real band cells were written, no question put)."""
    seen = _combined_run(tmp_path / "run", person, answered)
    for column in COMBINED_COLUMNS:
        assert ["no", "yes"] in [sorted(set(offered) - zoo.AGE_UNIT_ANSWERS) for offered in seen["asked"].get(column, [])], (
            column, seen["asked"].get(column))
        for spelling in _past_89_spellings(column):
            if not spelling.isdigit():
                assert not any(json.dumps(spelling)[1:-1] in text or spelling in text for text in seen["texts"]), (column, spelling)
        assert not set(seen["twin"][column]) & _past_89_spellings(column), (column, sorted(set(seen["twin"][column]) & _past_89_spellings(column))[:4])
