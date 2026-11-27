"""Batch 4t's fix round 5 (the orchestrator's LANE I4t RULINGS 6; round 4's scoped verify, item 1): a person's name
written whole before a word of the OLDER closed list of roles (`taxonomy._ROLE_AND_SERVICE_WORDS`,
`taxonomy._NOT_PERSONS_NAME_WORDS`) is held under every heading that says a person's name, as the public head 7804872f
held it under the staff headings lane CZ-G-b later made ones that say a person's name. HIPAA FIRST: names are Safe
Harbor identifiers.

THE VERIFY'S FOUR TABLES at 20,000 rows through the commands a person types, nobody answering, the table floor on, one
row a record beside a case number, 1,000 contacts on 20 rows each (`persons_names_forms.older_role_contacts`), each RED
on 8192e6ea: (V1) `Family Spouse` (six words of a relation) under `next_of_kin`; (V2) `Given Family, Spouse` under
`emergency_contact`; (V3) `Given Family, Nurse` (eight words of a clinician) under `witness`; (V4) `Given Family Nurse`
under `reviewer`. The public head read these headings as naming no person and held each column by its values; 8192e6ea
read every value as a role under them and published the 1,000 names with 20,000 of 20,000 twin cells real.

THE FIX (the verify's F1 in `taxonomy.persons_names_hold`): under a heading that says a person's name the value arm is
read a second time with the role test set aside -- by the sample, and past the sample's bound by the walk -- and the
hold is the value arm's where that reading reaches it; the heading arm keeps the role test, so a column of roles alone
is held by neither. Every name is made up.
"""

from __future__ import annotations

import pathlib
import random

import pytest

import persons_names_forms as names
from synthtwin import taxonomy

# The words of the older closed list of roles and flags (the 154 of the verify's class).
_OLDER = tuple(sorted(taxonomy._ROLE_AND_SERVICE_WORDS | taxonomy._NOT_PERSONS_NAME_WORDS))
# The three shapes of the verify's class: a family name, a given and a family name, and a given and a family name
# with a comma, before the word.
_SHAPES = ("{f} {w}", "{g} {f} {w}", "{g} {f}, {w}")
# The 18 staff headings lane CZ-G-b made ones that say a person's name (plan P4-D494 item 4), and six headings that
# said a person's name on both trees, where every tree published the class (the verify's carry C5, closed by F1's
# wide form).
_ADDED = tuple(names.STAFF_HEADINGS_ADDED)
_BOTH = ("emergency_contact_name", "contact_name", "kin_name", "attending", "surgeon_name", "provider_name")
# The contacts of one column of the class: more different values than the value arm's `taxonomy.NAMES_AT_LEAST`.
_CONTACTS = 200


def _hold(heading: str, cells: "list[str]") -> str:
    return taxonomy.persons_names_hold(heading, taxonomy.ROLE_CATEGORICAL, cells, frozenset())


def _made_up(count: int, seed: int, avoid: "frozenset[str]" = frozenset()) -> "list[str]":
    """``count`` different made-up names of three syllables, none a word of the reader's closed lists nor of ``avoid``."""
    draw = random.Random(seed)
    closed = (taxonomy._ROLE_QUALIFIER_WORDS | taxonomy._ROLE_AND_SERVICE_WORDS | taxonomy._NOT_PERSONS_NAME_WORDS
              | taxonomy._RELATIVES_READ_AS_FAMILY_NAMES | taxonomy._STATUS_AND_STAFFING_WORDS
              | taxonomy._CLINICIAN_ROLES_AS_VALUES)
    made: "dict[str, bool]" = {}
    while len(made) < count:
        word = names.made_up_word(draw, 3)
        if word.lower() not in closed and word not in avoid:
            made[word] = True
    return list(made)


_FAMILIES = _made_up(_CONTACTS, 5501)
_GIVEN = _made_up(_CONTACTS, 5502, frozenset(_FAMILIES))


def _class_column(word: str, shape: str) -> "list[str]":
    """One column of the class: ``_CONTACTS`` different contacts, each a made-up name in ``shape`` before ``word``."""
    written = word.capitalize()
    return [shape.format(f=_FAMILIES[place], g=_GIVEN[place], w=written) for place in range(_CONTACTS)]


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


# -- the verify's four tables through the commands -------------------------------------------------------------------


def test_v1_family_name_before_a_relation_under_next_of_kin_through_the_commands(tmp_path: pathlib.Path) -> None:
    """V1: 1,000 contacts `Family Spouse` (`Spouse`, `Parent`, `Guardian`, `Friend`, `Relative`, `Caregiver`) under `next_of_kin`, 20,000 rows, nobody answering: held, its question put, 0 real names shown, 0 twin cells equal to one or holding one (8192e6ea: categorical, 1,000 names shown, 20,000 of 20,000 twin cells real; the public head held it)."""
    seen = _measured(tmp_path / "v1", "older_role_kin")
    assert seen["different_names"] == 2000


def test_v2_given_and_family_name_a_comma_and_a_relation_under_emergency_contact(tmp_path: pathlib.Path) -> None:
    """V2: 1,000 contacts `Given Family, Spouse` (200 given names in turn) under `emergency_contact`, 20,000 rows, nobody answering: held, asked, 0 shown, 0 real twin cells (8192e6ea: 1,200 names and family names shown, 20,000 real twin cells)."""
    seen = _measured(tmp_path / "v2", "older_role_contact")
    assert seen["different_names"] == 3200


def test_v3_given_and_family_name_a_comma_and_a_clinician_under_witness(tmp_path: pathlib.Path) -> None:
    """V3: 1,000 contacts `Given Family, Nurse` (`Nurse`, `Physician`, `Resident`, `Pharmacist`, `Therapist`, `Technician`, `Surgeon`, `Attending`) under `witness`, 20,000 rows, nobody answering: held, asked, 0 shown, 0 real twin cells (8192e6ea: published, 20,000 real twin cells)."""
    seen = _measured(tmp_path / "v3", "older_role_witness")
    assert seen["different_names"] == 3200


def test_v4_given_and_family_name_before_a_clinician_under_reviewer(tmp_path: pathlib.Path) -> None:
    """V4: 1,000 contacts `Given Family Nurse` (the same eight words) under `reviewer`, 20,000 rows, nobody answering: held, asked, 0 shown, 0 real twin cells (8192e6ea: published, 20,000 real twin cells)."""
    seen = _measured(tmp_path / "v4", "older_role_reviewer")
    assert seen["different_names"] == 3200


# -- the generated class ----------------------------------------------------------------------------------------------


def test_every_older_role_word_after_a_name_is_held_under_every_person_heading() -> None:
    """THE CLASS, GENERATED (the verify's): each of the 154 words of the older closed list after 200 different made-up names in each of three shapes (`Family Word`, `Given Family Word`, `Given Family, Word`), each column under each of the 18 staff headings lane CZ-G-b added (8,316 columns: the public head held every one, 8192e6ea none) and the six headings that said a person's name on both trees (2,772 more, published by every tree before: carry C5): HELD by the value arm, every column."""
    assert len(_OLDER) == 154 and len(_ADDED) == 18
    assert all(taxonomy.named_as_persons_names(heading) for heading in _ADDED + _BOTH)
    unread: "list[str]" = []
    columns = 0
    for word in _OLDER:
        for shape in _SHAPES:
            cells = _class_column(word, shape)
            for heading in _ADDED + _BOTH:
                columns += 1
                if _hold(heading, cells) != taxonomy.HELD_PERSONS_NAMES:
                    unread += [f"{heading} {cells[0]}"]
    assert columns == 154 * 3 * 24
    assert unread == [], (len(unread), unread[:6])


def test_past_the_sample_the_walk_reads_the_names_with_the_role_test_set_aside() -> None:
    """PAST THE SAMPLE'S BOUND: 3,000 contacts `Given Family, Word` (the eight words of a clinician) on 30 rows each beside 3,500 labels of a ward and a number on one row each (93,500 rows, 6,500 different values) under `witness`: the sample of fixed rank reads under half of its values as names, with or without the role test, and the walk over the cells, which meets each value as often as its rows, reads two in three as names written whole once the role test is set aside: HELD, by the walk."""
    families = _made_up(3000, 5503)
    given = _made_up(300, 5504, frozenset(families))
    contacts = [f"{given[place % 300]} {families[place]}, {names.OLDER_ROLE_CLINICIANS[place % 8]}"
                for place in range(3000)]
    wards = [f"Ward {place:04d}" for place in range(3500)]
    cells = [contact for contact in contacts for _row in range(30)] + wards
    random.Random(5505).shuffle(cells)
    read = taxonomy._values_read(cells, frozenset())
    assert len(read) == taxonomy._SAFE_HARBOR_MEMO
    assert taxonomy._held_by_the_sample(read, False, {}) == ""
    assert taxonomy._held_by_the_sample(read, True, {}) == ""
    assert taxonomy._held_by_the_walk(cells, frozenset(), True, {}) == ""
    assert taxonomy._held_by_the_walk(cells, frozenset(), False, {}) == taxonomy.HELD_PERSONS_NAMES
    assert _hold("witness", cells) == taxonomy.HELD_PERSONS_NAMES


def test_columns_of_roles_alone_and_the_lanes_controls_stay_unheld() -> None:
    """NO NEW HOLD ON A COLUMN OF ROLES ALONE: the 154 words of the older list written alone (1 to 154 a column, as written and in capitals), the same words two by two (`Nurse Physician`) in columns of fewer different values than `taxonomy.NAMES_AT_LEAST` (the most the second reading never holds), and each staff heading's controls (the closed list's 40 labels, the three-label controls), under the 24 headings: none held."""
    held: "list[str]" = []
    draw = random.Random(5506)
    words = [word.capitalize() for word in _OLDER]
    for trial in range(60):
        size = 1 + (trial * 13) % len(words)
        alone = draw.sample(words, size)
        pairs = [f"{one} {two}" for one, two in zip(alone, reversed(alone))][:taxonomy.NAMES_AT_LEAST - 1]
        for values in (alone, [one.upper() for one in alone], pairs):
            heading = (_ADDED + _BOTH)[trial % 24]
            if _hold(heading, [values[row % len(values)] for row in range(max(400, len(values)))]):
                held += [f"{heading} {values[:3]}"]
    for heading, group in names.STAFF_HEADINGS_ADDED.items():
        for values in (names.control_labels(group), list(names.SMALL_CONTROLS[group])):
            if _hold(heading, [values[row % len(values)] for row in range(400)]):
                held += [f"{heading} {values[:3]}"]
    assert held == [], (len(held), held[:6])


# -- the mutants ------------------------------------------------------------------------------------------------------


def test_the_second_reading_is_red_on_its_mutants(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE MUTANTS. Every column read here stands under a heading that says a person's name, where the reader's first reading passes ``named`` true and only the second reading reads the values with the role test set aside, so a wrapper that answers nothing for that reading removes it alone. (MR) both readings removed: the verify's four tables' own cells (20,000 rows, read by `persons_names_hold`) and one column of the class for each word, unread; (MS) the sample's reading removed: the four tables unread (fewer different values than the bound: the walk is not read); (MW) the walk's reading removed: the four tables held, the column past the sample's bound unread."""
    tables = {layout: _table_cells(layout) for layout in names.OLDER_ROLE_FORMS}
    sample, walk = taxonomy._held_by_the_sample, taxonomy._held_by_the_walk

    def sample_first_only(read: "list[str]", named: bool, judged: "dict[str, int]") -> str:
        return sample(read, named, judged) if named else ""

    def walk_first_only(cells: "list[str]", absent: "frozenset[str]", named: bool, judged: "dict[str, int]") -> str:
        return walk(cells, absent, named, judged) if named else ""

    families = _made_up(3000, 5503)
    given = _made_up(300, 5504, frozenset(families))
    contacts = [f"{given[place % 300]} {families[place]}, {names.OLDER_ROLE_CLINICIANS[place % 8]}"
                for place in range(3000)]
    past = [contact for contact in contacts for _row in range(30)] + [f"Ward {place:04d}" for place in range(3500)]
    random.Random(5505).shuffle(past)
    class_columns = [((_ADDED + _BOTH)[place % 24], _class_column(word, _SHAPES[place % 3]))
                     for place, word in enumerate(_OLDER)]

    def held_tables() -> "list[bool]":
        return [bool(_hold(column, cells)) for column, cells in tables.values()]

    assert held_tables() == [True] * 4 and _hold("witness", past)
    assert all(_hold(heading, cells) for heading, cells in class_columns)
    with monkeypatch.context() as patched:
        patched.setattr(taxonomy, "_held_by_the_sample", sample_first_only)
        patched.setattr(taxonomy, "_held_by_the_walk", walk_first_only)
        assert held_tables() == [False] * 4 and not _hold("witness", past)
        assert not any(_hold(heading, cells) for heading, cells in class_columns)
    with monkeypatch.context() as patched:
        patched.setattr(taxonomy, "_held_by_the_sample", sample_first_only)
        assert held_tables() == [False] * 4 and _hold("witness", past)
    with monkeypatch.context() as patched:
        patched.setattr(taxonomy, "_held_by_the_walk", walk_first_only)
        assert held_tables() == [True] * 4 and not _hold("witness", past)


def test_the_early_settling_counts_the_words_kept_as_roles_alone(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE VERIFY'S CARRY C1 PINNED (round 4's early settling, `taxonomy._names_in_reach`): a `surgeon` column of 40 words kept as roles written alone, 20 labels that are no name (`Ward 1` to `Ward 20`) and 10 ordinary made-up family names, in that row order and in the reverse, is held (the public head held it too: the words read as family names alone there); on the mutant MF, whose early settling leaves out the words kept as roles alone, both orders are settled unheld before the ordinary family names settle the words."""
    kept = sorted(word.capitalize() for word in taxonomy._STATUS_AND_STAFFING_WORDS)[:40]
    labels = [f"Ward {number}" for number in range(1, 21)]
    ordinary = _made_up(10, 5507)
    orders = (kept + labels + ordinary, ordinary + labels + kept)
    assert [_hold("surgeon", cells) for cells in orders] == [taxonomy.HELD_NAMED_AS_PERSONS_NAMES] * 2
    with monkeypatch.context() as patched:
        patched.setattr(taxonomy, "_names_in_reach", lambda tally: tally[0] + tally[1] + tally[2])
        assert [_hold("surgeon", cells) for cells in orders] == ["", ""]
