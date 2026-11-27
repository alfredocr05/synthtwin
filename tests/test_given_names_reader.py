"""Release 37, lane PRIVACY: the persons' names reader reads a name by its given name, from a built-in list.

THE EXPOSURE (measured on the shipped route at the owner's floor, the twin
drawn from the inside record): a column of 1,000 persons' names, each on 20
rows, written in small letters (`cedar, aaa`) put no question, was described
as labels, and its twin wrote 20,000 of 20,000 cells as real names; so did
names in capitals with no comma beside a given name the shapes read no
further, a given name alone and a given name beside its initial. Every
shape the reader reads (`taxonomy.a_persons_name`) asks for a capital.

THE FIX: a built-in list of common given names, generic public knowledge
the owner ruled for (`synthtwin.given_names`), read by
`taxonomy._a_name_by_its_given_name` inside the value arm of
`taxonomy.persons_names_hold` (`_persons_name_kind_read`): a value with no
figure, one to six runs of letters, one of them a listed given name, is a
name where it is that name alone or beside its initials, or, where it writes
no capital, where the same value with every word opening with a capital is a
name written whole. A column is held only as before: 100 such values and
half of the different values read.

Each class is closed by a GENERATED case whose names are written from this
file's grammar and from `persons_names_forms.COMMON_GIVEN`, a list of common
given names written apart from the product's and never read from it, each
red on its mutant; the price (control labels as written, in small letters
and in capitals, labels written in sentence case around a given name) holds
no new column; and two cases at 20,000 rows go through the commands a
person types on the shipped route.
"""

from __future__ import annotations

import contextlib
import io
import pathlib
import random

import pytest

import persons_names_forms as names
from synthtwin import given_names, inside, installation, taxonomy

# The months and weekdays and their short forms, written here: none is a given name on the list.
_CALENDAR = ("january february march april may june july august september october november december jan feb mar "
             "apr jun jul aug sep sept oct nov dec monday tuesday wednesday thursday friday saturday sunday mon tue "
             "tues wed thu thur thurs fri sat sun").split()


def _hold(cells: "list[str]", name: str = "patient_label") -> str:
    return taxonomy.persons_names_hold(name, taxonomy.ROLE_CATEGORICAL, cells, frozenset())


def _column(layout: str, shape: str, rows: int = 20000) -> "tuple[list[str], list[str]]":
    """The names column of a generated table and its different real names."""
    _header, body, _column_name, real = names.table(layout, shape, rows)
    return [row[0] for row in body], real


# -- the list ---------------------------------------------------------------------------------


def test_the_list_is_small_ascii_sorted_once_and_apart_from_its_stop_words() -> None:
    """Every listed name is three small ASCII letters or more, written once and in order in the module, none a word of its stop list or a month's or a weekday's name or short form."""
    written = given_names._LISTED.split()
    assert written == sorted(set(written))
    assert len(written) == len(given_names.GIVEN_NAMES) >= 2000
    assert all(len(name) >= 3 and name.isascii() and name.isalpha() and name.islower() for name in written)
    assert not given_names.GIVEN_NAMES & given_names.STOP
    assert not given_names.GIVEN_NAMES & set(_CALENDAR)


def test_the_common_given_names_written_apart_are_listed() -> None:
    """THE LIST'S REACH: each of the 162 common given names `persons_names_forms` writes apart from the product's list, folded, is on it."""
    assert len(names.COMMON_GIVEN) == 162
    assert [one for one in names.COMMON_GIVEN if given_names.fold(one) not in given_names.GIVEN_NAMES] == []


@pytest.mark.parametrize(("written", "folded"), [
    ("José", "jose"), ("ZOË", "zoe"), ("Bjørn", "bjorn"), ("Łukasz", "lukasz"), ("Raúl", "raul"), ("Inés", "ines"),
    ("José", "jose"), ("Ægir", "aegir"), ("Maria", "maria"),
])
def test_a_name_is_folded_to_small_plain_letters(written: str, folded: str) -> None:
    assert given_names.fold(written) == folded


# -- the values -------------------------------------------------------------------------------


def _forms(given: str, family: str, initial: str) -> "list[str]":
    """The forms a name holding a common given name is written in, by this file's grammar."""
    small_given, small_family = given.lower(), family.lower()
    return [
        f"{small_family}, {small_given}", f"{small_given} {small_family}", f"{small_given} {initial.lower()}.",
        f"{small_given} {initial.lower()}", f"{family.upper()} {given.upper()}", small_given, given, given.upper(),
        f"de la {small_family}, {small_given}", f"{small_given}-{small_given} {small_family}",
        f"{small_family} jr., {small_given}", f"dr. {small_given} {small_family}",
    ]


def test_each_form_holding_a_common_given_name_is_a_name_written_whole() -> None:
    """GENERATED: 162 common given names beside made-up family names, in twelve forms each -- small letters with and without a comma, an initial with and without its point, capitals with no comma, the given name alone in three cases, a particle, a doubled given name, a suffix and a title -- 1,944 values, each a name written whole under a neutral heading and under one that says a person's name."""
    draw = random.Random(37)
    values = [form for given in names.COMMON_GIVEN
              for form in _forms(given, names.made_up_word(draw, 3), draw.choice(names.INITIALS))]
    assert len(values) == 1944
    unread = [value for value in values if taxonomy._persons_name_kind(value, False) != taxonomy._A_NAME_WRITTEN_WHOLE]
    assert unread == []
    unread = [value for value in values if taxonomy._persons_name_kind(value, True) != taxonomy._A_NAME_WRITTEN_WHOLE]
    assert unread == []


def test_values_the_list_holds_no_word_of_are_not_read_by_it() -> None:
    """A made-up name in small letters, a label in small letters and a given name with a figure are not read by the list (the stated limit: a name whose given name the list lacks is read by its capitals alone)."""
    draw = random.Random(38)
    made_up = [f"{names.made_up_word(draw, 3).lower()}, {names.made_up_word(draw, 2).lower()}" for _ in range(200)]
    made_up = [one for one in made_up if not any(word in given_names.GIVEN_NAMES for word in one.replace(",", " ").split())]
    assert len(made_up) > 150
    others = ["left arm", "x-ray chest", "sinus rhythm", "pending", "unknown", "maria 2", "room 12 john", ""]
    assert [one for one in made_up + others if taxonomy._a_name_by_its_given_name(one)] == []


def test_a_value_written_with_a_capital_keeps_the_shapes_reading() -> None:
    """GENERATED: 162 labels in sentence case around a common given name (`Bado-Maria-Kitu disease`) are no name, where the same labels in small letters would read as given-name-first names: a value that writes a capital was read by its capitals."""
    draw = random.Random(39)
    labels = [f"{names.made_up_word(draw, 2)}-{given}-{names.made_up_word(draw, 2)} disease" for given in names.COMMON_GIVEN]
    assert [one for one in labels if taxonomy._a_name_by_its_given_name(one)] == []


# -- the columns ------------------------------------------------------------------------------


@pytest.mark.parametrize("shape", names.GIVEN_SHAPES)
def test_a_column_of_names_holding_common_given_names_is_held(shape: str) -> None:
    """GENERATED at the owner's floor: 1,000 people on 20 rows each, each written in one of the given-name shapes (`persons_names_forms.GIVEN_SHAPES`), under a neutral heading: held as names written whole."""
    cells, real = _column("alone", shape)
    assert len(real) == 1000
    assert _hold(cells) == taxonomy.HELD_PERSONS_NAMES


@pytest.mark.parametrize("layout", ["given_alone", "given_alone_small"])
def test_a_column_of_given_names_alone_is_held(layout: str) -> None:
    """GENERATED at the owner's floor: each person's common given name alone, as written and in small letters (162 different values): held as names written whole."""
    cells, real = _column(layout, "comma")
    assert len(real) >= taxonomy.NAMES_AT_LEAST
    assert _hold(cells) == taxonomy.HELD_PERSONS_NAMES


def test_the_given_name_reading_is_red_on_its_mutants(monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANTS: the reading switched off, the list emptied, or the given name alone not read -- each leaves a column the fix holds unheld."""
    cells, _real = _column("alone", "given_small")
    alone, _ = _column("given_alone_small", "comma")
    monkeypatch.setattr(taxonomy, "_a_name_by_its_given_name", lambda text: False)
    assert _hold(cells) == ""
    monkeypatch.undo()
    monkeypatch.setattr(given_names, "GIVEN_NAMES", frozenset())
    assert _hold(cells) == ""
    monkeypatch.undo()
    monkeypatch.setattr(taxonomy, "_INITIALS_AT_MOST", -1)
    assert _hold(alone) == ""
    monkeypatch.undo()
    assert _hold(cells) == _hold(alone) == taxonomy.HELD_PERSONS_NAMES


def test_the_capital_guard_is_red_on_its_mutant(monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: a value that writes a capital read again with a capital on every word -- labels in sentence case around a given name are read as names."""
    draw = random.Random(39)
    labels = [f"{names.made_up_word(draw, 2)}-{given}-{names.made_up_word(draw, 2)} disease" for given in names.COMMON_GIVEN]
    monkeypatch.setattr(taxonomy, "_writes_a_capital", lambda text: False)
    assert len([one for one in labels if taxonomy._a_name_by_its_given_name(one)]) == len(labels)


def test_the_price_no_control_column_is_newly_held() -> None:
    """THE PRICE: every control and price label column of `persons_names_forms` (40 ordinary labels a heading's column could hold, the held-out controls, the near-miss medicines, procedures and departments), as written, in small letters and in capitals, beside a case number of 20,000 rows: the given-name reading holds none the shapes left unheld."""
    groups: "dict[str, list[str]]" = {f"control:{group}": names.control_labels(group) for group in names.CONTROL_LABELS}
    for family in names.PRICE_FAMILIES:
        for column, labels in names.price_columns(family).items():
            groups[f"{family}:{column}"] = list(labels)
    draw = random.Random(40)
    newly: "list[str]" = []
    for key, labels in groups.items():
        for written in (labels, [one.lower() for one in labels], [one.upper() for one in labels]):
            cells = [written[draw.randrange(len(written))] for _row in range(4000)]
            held = _hold(cells, "label")
            if held:
                with pytest.MonkeyPatch.context() as patch:
                    patch.setattr(taxonomy, "_a_name_by_its_given_name", lambda text: False)
                    if not _hold(cells, "label"):
                        newly += [key]
    assert newly == []


# -- through the commands, on the shipped route ------------------------------------------------


@pytest.mark.parametrize(("layout", "shape"), [("alone", "given_small"), ("given_alone_small", "comma")])
def test_through_the_commands_no_real_name_reaches_the_twin(tmp_path: pathlib.Path, layout: str, shape: str) -> None:
    """THROUGH THE COMMANDS, the inside record written as on a person's computer (a private folder, no temporary root), nobody answering, at 20,000 rows: 1,000 names in small letters, and each person's given name alone in small letters -- the column is held, a question is put, no real name is written whole on any file or the screen, and no twin cell is one (the base wrote all 20,000)."""
    places = inside.Places(pathlib.Path(tmp_path, "installation", "synthtwin", "inside"), (), (),
                           installation.system_name(), ())
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inside, "default_places", lambda: places)
        with contextlib.redirect_stdout(io.StringIO()):
            seen = names.measure(tmp_path / "run", layout, shape, 20000, "unanswered", small_tables_refused=True)
    assert (seen["profile"], seen["generate"]) == (0, 0)
    assert seen["roles"] and seen["roles"][-1] in names.PUBLISHING_NOTHING
    assert any("yes" in offered for offered in seen["asked"])
    assert seen["shown_folded"] == 0
    assert (seen["twin_exact"], seen["twin_folded"], seen["twin_inside"]) == (0, 0, 0)
