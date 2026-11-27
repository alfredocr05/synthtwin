"""Batch 4t's fix round 4 (the orchestrator's LANE I4t RULINGS 5; push critic 24's B1): the words lane CZ-G-b keeps
as roles never publish the family names beside them that the public head 7804872f holds. HIPAA FIRST: names are Safe
Harbor identifiers.

THE CRITIC'S THREE TABLES at 20,000 rows through the commands a person types, nobody answering, the table floor on,
one row a record beside a case number (`persons_names_forms.table`), each RED on 34e9a218:

(a) 1,000 contacts written `Family Relation` (twelve relations, no mark), 20 rows each, under
    `emergency_contact_name`: the public head holds the column and asks; 34e9a218 read every value as a role and
    published the 1,000 with 20,000 of 20,000 twin cells real;
(b) 60 clinicians' family names alone under `surgeon`, 35 of them words lane CZ-G-b keeps as roles and 25 ordinary
    made-up family names: the public head holds; 34e9a218 published the 60 and wrote 20,000 real twin cells;
(c) 1,000 contacts written `Family-Relation` (a dash, no space) under `next_of_kin`: published by both trees (old),
    held now because the same rule reaches it.

THE FIX: a value the words kept as roles made a role on its own is read as lane CZ-G-b's base read it -- a family
name alone before such a word with no mark or a dash with no space (`Cedar Mother`, `CEDAR MOTHER`, `Cedar-Mother`),
none of its words one that qualifies a role (`taxonomy._a_family_name_beside_a_role`,
`taxonomy._ROLE_QUALIFIER_WORDS`: `Step Mother`, `Day Shift`, `Not Assigned` stay roles); a word kept as a role
written alone (`Witness`) where the column also holds an ordinary family name (`taxonomy._kinds_settled`,
`taxonomy._an_ordinary_family_name`). A column of roles alone is read as on 34e9a218: no new hold. Every name is made
up.
"""

from __future__ import annotations

import pathlib
import random

import pytest

import persons_names_forms as names
from synthtwin import taxonomy

# The person headings the generated cases read under: lane CZ-G-b's gate file's, the verify's and the staff headings
# lane CZ-G-b added, each a heading that says a person's name.
_PERSON_HEADINGS = tuple(sorted({
    "contact_full_name", "kin_name", "guardian_full_name", "staff_name", "provider_name", "surgeon",
    "anesthesia_provider", "patient_full_name", "crna", "anesthetist", "emergency_contact_name", "next_of_kin",
    "social_worker", "patient_name", "contact_name", "attending", "administered_by", "reviewed_by", "patient_surname",
    *names.STAFF_HEADINGS_ADDED,
}))
# The words lane CZ-G-b keeps as the last word of a role, the degree `crna` aside (after a family name alone it is that
# person's degree, read as a name before this round).
_KEPT = tuple(sorted(word for word in taxonomy._STATUS_AND_STAFFING_WORDS | taxonomy._CLINICIAN_ROLES_AS_VALUES
                     if word != "crna"))
# The shapes of a family name alone before such a word that the head left a role: no mark, in capitals, a dash with no
# space (the hyphen and the en dash, which the reader reads as one).
_BESIDE = ("{f} {w}", "{F} {W}", "{f}-{w}", "{F}-{W}", "{f}–{w}")


def _hold(values: "list[str]", name: str, rows: int = 400) -> str:
    cells = [values[place % len(values)] for place in range(max(rows, len(values)))]
    return taxonomy.persons_names_hold(name, taxonomy.ROLE_CATEGORICAL, cells, frozenset())


def _written(word: str) -> str:
    return word.upper() if word in ("crnas", "pcp") else word.capitalize()


def _families(count: int, seed: int) -> "list[str]":
    """``count`` different made-up family names, none a word of the reader's closed lists (a family name that is also a word qualifying a role, `Site`, is read as one: the stated price)."""
    draw = random.Random(seed)
    made: "dict[str, bool]" = {}
    closed = (taxonomy._ROLE_QUALIFIER_WORDS | taxonomy._ROLE_AND_SERVICE_WORDS | taxonomy._NOT_PERSONS_NAME_WORDS
              | taxonomy._RELATIVES_READ_AS_FAMILY_NAMES)
    while len(made) < count:
        word = names.made_up_word(draw, draw.choice((2, 3)))
        if word.lower() not in closed and not taxonomy._a_word_kept_as_a_role(word):
            made[word] = True
    return list(made)


def _table_cells(layout: str) -> "tuple[str, list[str]]":
    header, body, column, _real = names.table(layout, "family", 20000)
    place = header.index(column)
    return column, [row[place] for row in body]


def _measured(folder: pathlib.Path, layout: str) -> "dict[str, object]":
    seen = names.measure(folder, layout, "family", 20000)
    assert names.failures(seen) == [], seen
    assert seen["asked"], seen
    assert seen["shown"] == seen["shown_folded"] == 0, seen
    assert seen["twin_exact"] == seen["twin_folded"] == seen["twin_inside"] == 0, seen
    return seen


# -- the critic's three tables through the commands ----------------------------------------------------------------


def test_contacts_written_family_and_relation_with_no_mark_through_the_commands(tmp_path: pathlib.Path) -> None:
    """B1 (a): 1,000 contacts `Family Relation` under `emergency_contact_name`, 20,000 rows, nobody answering: held, its question put, 0 real values shown, 0 twin cells equal to one or holding one (34e9a218: categorical, 1,000 shown, 20,000 of 20,000 twin cells real)."""
    seen = _measured(tmp_path / "a", "relation_no_mark")
    assert seen["different_names"] == 2000


def test_surgeons_family_names_some_kept_as_roles_through_the_commands(tmp_path: pathlib.Path) -> None:
    """B1 (b): 60 surgeons' family names alone, 35 of them words kept as roles, 25 ordinary, 20,000 rows, nobody answering: held, its question put, 0 shown, 0 real twin cells (34e9a218: the 60 published, 20,000 real twin cells)."""
    seen = _measured(tmp_path / "b", "surnames_kept_as_roles")
    assert seen["different_names"] == 60


def test_next_of_kin_written_family_dash_relation_through_the_commands(tmp_path: pathlib.Path) -> None:
    """B1 (c): 1,000 contacts `Family-Relation` under `next_of_kin`, 20,000 rows, nobody answering: held, asked, 0 and 0 (both 34e9a218 and the public head published the 1,000 under this heading, which names no person on the public head)."""
    seen = _measured(tmp_path / "c", "relation_dash")
    assert seen["different_names"] == 2000


# -- the generated cases ---------------------------------------------------------------------------------------------


def test_every_word_kept_as_a_role_after_family_names_with_no_mark_is_held_whatever_their_number() -> None:
    """(a) and (c), GENERATED: each of the 77 words after a family name alone in the five shapes the head left a role (`_BESIDE`), one, two, ten and 60 different family names a column, each column under three person headings in turn (every heading of `_PERSON_HEADINGS` read): HELD, every column, as the base held them. The same words after each word that qualifies a role (`taxonomy._ROLE_QUALIFIER_WORDS`: `Day Shift`, `Step Mother`), one to 40 such phrases a column: none held."""
    families = _families(120, 4401)
    unread: "list[str]" = []
    held_roles: "list[str]" = []
    read_under: "dict[str, bool]" = {}
    qualifiers = sorted(taxonomy._ROLE_QUALIFIER_WORDS)
    columns = 0
    for place, word in enumerate(_KEPT):
        for turn, shape in enumerate(_BESIDE):
            headings = [_PERSON_HEADINGS[(3 * (5 * place + turn) + step) % len(_PERSON_HEADINGS)] for step in range(3)]
            for count in (1, 2, 10, 60):
                values = [shape.format(f=f, F=f.upper(), w=_written(word), W=word.upper()) for f in families[:count]]
                for heading in headings:
                    columns += 1
                    read_under[heading] = True
                    if not _hold(values, heading, rows=max(count, 20)):
                        unread += [f"{heading} {values[0]} ({count})"]
            first = (5 * place + turn) % len(qualifiers)
            phrases = [shape.format(f=q.capitalize(), F=q.upper(), w=_written(word), W=word.upper())
                       for q in (qualifiers * 2)[first:first + 1 + (place + turn) % 40]]
            if _hold(phrases, headings[0], rows=max(len(phrases), 20)):
                held_roles += [phrases[0]]
    assert len(_KEPT) == 77 and columns == 77 * len(_BESIDE) * 4 * 3
    assert sorted(read_under) == list(_PERSON_HEADINGS)
    assert unread == [], (len(unread), unread[:6])
    assert held_roles == [], (len(held_roles), held_roles[:6])


def test_more_family_names_than_the_sample_reads_are_held_by_both_readings() -> None:
    """(a) past the sample's bound: 5,000 contacts `Family Relation` (more different values than the reader reads), each on one row, under `emergency_contact_name`: the sample of fixed rank and the walk over the cells settle the column alike, held."""
    families = _families(5000, 4402)
    values = [f"{family} {names.RELATIONS_TWELVE[place % 12]}" for place, family in enumerate(families)]
    assert len(set(values)) > taxonomy._SAFE_HARBOR_MEMO
    cells = list(values)
    random.Random(4403).shuffle(cells)
    judged: "dict[str, int]" = {}
    assert taxonomy.persons_names_hold("emergency_contact_name", taxonomy.ROLE_CATEGORICAL, cells, frozenset())
    assert taxonomy._held_by_the_sample(taxonomy._values_read(cells, frozenset()), True, judged) == taxonomy.HELD_PERSONS_NAMES
    assert taxonomy._held_by_the_walk(cells, frozenset(), True, judged) == taxonomy.HELD_PERSONS_NAMES


def test_words_kept_as_roles_beside_ordinary_family_names_are_held() -> None:
    """(b), GENERATED: 300 columns of 1 to 35 words kept as roles written alone (as written and in capitals) beside 1 to 25 ordinary made-up family names, under each person heading: HELD, every column, as the base held them; the same words with no ordinary family name beside them are roles, and no column of them is held."""
    draw = random.Random(4404)
    families = _families(200, 4405)
    unread: "list[str]" = []
    roles_held: "list[str]" = []
    for trial in range(300):
        words = [_written(word) for word in draw.sample(_KEPT, 1 + trial % 35)]
        if trial % 3 == 0:
            words = [word.upper() for word in words]
        ordinary = draw.sample(families, 1 + trial % 25)
        for heading in _PERSON_HEADINGS[trial % 5::5]:
            if not _hold([*words, *ordinary], heading):
                unread += [f"{heading} {words[:2]} {ordinary[:1]}"]
            if _hold(words, heading):
                roles_held += [f"{heading} {words[:3]}"]
    assert unread == [], (len(unread), unread[:6])
    assert roles_held == [], (len(roles_held), roles_held[:6])


def test_a_column_of_roles_alone_is_read_as_before() -> None:
    """NO NEW HOLD ON A COLUMN OF ROLES ALONE (the lane's purpose): every control lane CZ-G-b reads under its staff headings (the closed list's 40 labels and the three-label controls, as written and in capitals), the words kept as roles alone and after the words that qualify a role (`Day Shift`, `Step Mother`, `Not Assigned`; 24 of them, any number a column), and a relatives' column whose other words are family names of their own (`Son`, `Cousin`, `Husband`, `Partner`, `Child`): none is held."""
    held: "list[str]" = []
    for heading, group in names.STAFF_HEADINGS_ADDED.items():
        for values in (names.control_labels(group), list(names.SMALL_CONTROLS[group]),
                       [value.upper() for value in names.SMALL_CONTROLS[group]]):
            if _hold(values, heading):
                held += [f"{heading} {values[:3]}"]
    qualifiers = ("Day", "Night", "Evening", "Swing", "Weekend", "Full", "Part", "On", "Not", "In", "Step", "Half",
                  "Great", "Birth", "Foster", "God", "Medical", "Clinical", "Program", "Senior", "Junior", "Peer",
                  "Initial", "Pending")
    draw = random.Random(4406)
    for trial in range(200):
        words = [_written(word) for word in draw.sample(_KEPT, 1 + trial % 40)]
        phrases = [f"{qualifiers[place % len(qualifiers)]} {word}" for place, word in enumerate(words)]
        for heading in _PERSON_HEADINGS[trial % 4::4]:
            for values in (words, phrases):
                if _hold(values, heading):
                    held += [f"{heading} {values[:3]}"]
    relatives = ["Mother", "Father", "Son", "Daughter", "Husband", "Wife", "Brother", "Sister", "Partner", "Cousin",
                 "Child", "Niece", "Nephew", "Aunt", "Uncle", "Grandmother", "Grandfather"]
    for size in range(3, len(relatives) + 1):
        for heading in ("next_of_kin", "emergency_contact", "nok", "kin_name", "contact_name"):
            if _hold(relatives[:size], heading):
                held += [f"{heading} {relatives[:size]}"]
    assert held == [], (len(held), held[:6])


# -- the mutants --------------------------------------------------------------------------------------------------


def test_the_readings_are_red_on_their_mutants(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE MUTANTS, on the critic's three tables' own cells (20,000 rows, read by `persons_names_hold`) and on the controls: (M1) no family name read beside a word kept as a role, the head's reading of (a) and (c): (c) unread, and ten contacts written as (a) are (since batch 4t's fix round 5 (a)'s 1,000 contacts are held all the same by the value arm's second reading, the role test set aside: 1,000 names written whole; ten are fewer than that reading needs); (M2) no ordinary family name ever met, (b) unread; (M3) no word that qualifies a role, the three-label staffing control (`Day Shift`, `Night Shift`, `Rotating`) held; (M4) no relatives' words set aside, a relatives' column held; (M5) the words kept as roles alone never settled, 34e9a218's reading of (b), unread."""
    tables = {layout: _table_cells(layout) for layout in ("relation_no_mark", "surnames_kept_as_roles", "relation_dash")}

    def held(layout: str) -> str:
        column, cells = tables[layout]
        return taxonomy.persons_names_hold(column, taxonomy.ROLE_CATEGORICAL, cells, frozenset())

    assert all(held(layout) for layout in tables)
    staffing = list(names.SMALL_CONTROLS["staffing"])
    relatives = ["Mother", "Father", "Son", "Daughter", "Husband"]
    assert not _hold(staffing, "er_md") and not _hold(relatives, "next_of_kin")
    ten = [f"{family} {names.RELATIONS_TWELVE[place]}" for place, family in enumerate(_families(10, 4407))]
    assert _hold(ten, "emergency_contact_name")
    with monkeypatch.context() as patched:
        patched.setattr(taxonomy, "_a_family_name_beside_a_role", lambda text: False)
        assert not held("relation_dash") and not _hold(ten, "emergency_contact_name") and held("surnames_kept_as_roles")
        assert held("relation_no_mark") == taxonomy.HELD_PERSONS_NAMES
    with monkeypatch.context() as patched:
        patched.setattr(taxonomy, "_an_ordinary_family_name", lambda text: False)
        assert not held("surnames_kept_as_roles") and held("relation_no_mark")
    with monkeypatch.context() as patched:
        patched.setattr(taxonomy, "_ROLE_QUALIFIER_WORDS", frozenset())
        assert _hold(staffing, "er_md")
    with monkeypatch.context() as patched:
        patched.setattr(taxonomy, "_RELATIVES_READ_AS_FAMILY_NAMES", frozenset())
        assert _hold(relatives, "next_of_kin")
    with monkeypatch.context() as patched:

        def as_on_the_head(tally: "list[int]", named: bool) -> "tuple[int, int, int, int]":
            return tally[0], tally[1], tally[2], tally[3] + tally[4]

        patched.setattr(taxonomy, "_kinds_settled", as_on_the_head)
        assert not held("surnames_kept_as_roles") and held("relation_no_mark") and held("relation_dash")
