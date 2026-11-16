"""P4-D494 (lane CZ-G-b): the persons' names reader's residuals of plan P4-D478 (a), closed; HIPAA first.

THE SHARE (item 1): a column is held where HALF of its different values
read are names written whole, 100 of them or more (`taxonomy._NAMES_SHARE_TAKEN`
in `_NAMES_SHARE_PARTS`), where two in three were asked before -- 1,000 names
beside 520 small-letter spellings of them were published; narrowed once to
the value arm, the heading arm keeping two in three.

THE SAMPLE (item 2): past 4,096 different values, those read are the 4,096
of least fixed rank (`taxonomy._value_rank`, `_values_read`), a function
of each value alone, so no layout of the rows and no spelling standing on
more rows than the names moves it (lane CZ-F's walk left 20 of 112
regularly cycled layouts unheld, and names on fewer rows than codes).

THE RESIDUAL SPELLINGS (item 3), each through the reader's one definition:
the name field repeated after `~`, its family name in `&` subcomponents,
eight more apostrophe marks, a title before a particle-led family name,
and the short senior and junior, the esquire and the ordinals two to four
as words of the one definition of a suffix (a suffix and a degree after a
family name alone too).

THE STAFF HEADINGS (item 4): each heading added to the heading arm's closed
list holds 40 names, and its held-out control of 40 ordinary labels such a
column could hold, outside the closed list's words, is held too (the stated
price of keeping the headings); each heading left out names no person, its
control being what a name that says a person's name would hold.

AND LANE CZ-G-b'S REPAIR 1 (the orchestrator's LANE CZ-G-b RULINGS 3 and 4):
the walk over the cells kept beside the sample, a column held where either
reaches its share; no word made a role unreads a name written whole before
it, `husband` and `diem` no role, a clinician's role written as a value
read singular only; a mark drawn as nothing set aside only inside a word;
a repeated name field read by its strongest repetition; the ordinals in a
health message's name field. AND ITS REPAIR 2 (LANE CZ-G-b RULINGS 6 (1)):
a family name alone before a comma or a dash standing alone and a word kept
as a role is a person's name (`Family, Mother`, `Family - Daughter`). AND ITS
LAST STEP (RULINGS 8): that family name is read before the role test, so a
run of words kept as roles joined by a comma calls the role test once a word.

Every class is closed by a GENERATED case whose expectation is written from
a grammar of this file (never by calling the new code), each red on its
mutant; and two 20,000-row cases through the commands a person types (THE
SUITE'S TIME rule; the second ruled by RULINGS 6 (1)): 60 clinicians
written with a degree beside 1,000 patients, and 1,000 emergency contacts
written `Family, Relation` beside a case number.
"""

from __future__ import annotations

import math
import pathlib
import random

import pytest

import persons_names_forms as names
from synthtwin import taxonomy


def _hold(cells: "list[str]", name: str = "label", role: str = taxonomy.ROLE_CATEGORICAL) -> str:
    return taxonomy.persons_names_hold(name, role, cells, frozenset())


def _column(values: "list[str]", rows: int = 4000) -> "list[str]":
    """A column cycling through its values, every one on several rows."""
    return [values[row % len(values)] for row in range(max(rows, len(values)))]


# -- item 1: the share at half ------------------------------------------------------------


def _with_small_letters(count: int, small: int) -> "list[str]":
    """``count`` names written `Family, Given` on 20 rows each, ``small`` of them written once more in small letters."""
    whole = names.names_of(count, "comma", seed=61)
    return [one for one in whole for _row in range(20)] + [one.lower() for one in whole[:small]]


def test_the_value_arm_holds_at_half_of_the_values_read() -> None:
    """THE SHARE EDGE (lane CZ-F's skeptic 1 item 5 (a)): 1,000 names beside 520, 999 and 1,000 small-letter spellings of them are held; beside 1,000 small spellings and one code more, half is not reached."""
    for small in (520, 999, 1000):
        assert _hold(_with_small_letters(1000, small)) == taxonomy.HELD_PERSONS_NAMES, small
    assert _hold(_with_small_letters(1000, 1000) + ["code 1"]) == ""


def test_the_share_at_half_is_red_on_its_mutant(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE MUTANT: with two in three back, the share edge's 520 small spellings beside 1,000 names publish the column."""
    monkeypatch.setattr(taxonomy, "_NAMES_SHARE_PARTS", 3)
    monkeypatch.setattr(taxonomy, "_NAMES_SHARE_TAKEN", 2)
    assert _hold(_with_small_letters(1000, 520)) == ""


def test_the_heading_arm_keeps_two_in_three() -> None:
    """THE SHARE NARROWED ONCE TO THE VALUE ARM (the stopping rule's third clause): under `surgeon`, 30 clinicians beside 15 codes are held, beside 16 not; one capitalised word beside a flag's word (`Elective` and `Unknown`) is not held -- at half, 3,584 of 3,808 such columns of two values under 28 names that say a person's name were."""
    clinicians = names.names_of(30, "comma", seed=62)
    codes = [f"S{20000 + place}" for place in range(16)]
    assert _hold(_column(clinicians + codes[:15]), name="surgeon") == taxonomy.HELD_NAMED_AS_PERSONS_NAMES
    assert _hold(_column(clinicians + codes), name="surgeon") == ""
    for pair in (["Elective", "Unknown"], ["Local", "Pending"], ["Backup", "Unassigned"]):
        assert _hold(_column(pair), name="surgeon", role=taxonomy.ROLE_BINARY) == "", pair


def test_the_heading_arm_at_half_is_red_on_its_mutant(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE MUTANT: the heading arm at half holds `Elective` beside `Unknown` under `surgeon`."""
    monkeypatch.setattr(taxonomy, "_BULK_PARTS", 2)
    monkeypatch.setattr(taxonomy, "_BULK_TAKEN", 1)
    assert _hold(_column(["Elective", "Unknown"]), name="surgeon", role=taxonomy.ROLE_BINARY) != ""


# -- item 2: the sample by a fixed rank ----------------------------------------------------


def _cycled(rows: int, every: int, whole: "list[str]", small: "list[str]", seed: str) -> "list[str]":
    """Every ``every``-th row one of ``small`` cycled in row order, the others ``whole`` in a shuffled cycle."""
    cycle = [whole[place % len(whole)] for place in range(rows)]
    random.Random(seed).shuffle(cycle)
    cells: "list[str]" = []
    taken = lowered = 0
    for row in range(rows):
        if row % every == 0:
            cells += [small[lowered % len(small)]]
            lowered += 1
        else:
            cells += [cycle[taken]]
            taken += 1
    return cells


def test_no_layout_of_the_rows_moves_the_sample() -> None:
    """ONE GENERATED CASE (lane CZ-F's scoped verify 2, item 1): every p-th row (p 3, 4, 5, 6, 8, 12, 16) one of 1,400 names in small letters cycled in row order, the others 3,000 names (68.2 per cent of the different values names), at 20,000 to 100,000 rows: held, as the same cells shuffled are -- the walk over the cells left 20 of 112 such layouts unheld."""
    made = names.names_of(4400, "comma", seed=63)
    whole, small = made[:3000], [one.lower() for one in made[3000:]]
    unheld: "list[str]" = []
    for rows in (20000, 30000, 49152, 60000, 100000):
        for every in (3, 4, 5, 6, 8, 12, 16):
            cells = _cycled(rows, every, whole, small, f"{rows}:{every}")
            if _hold(cells) != taxonomy.HELD_PERSONS_NAMES:
                unheld += [f"{rows}/{every}"]
    assert not unheld, unheld


def test_the_sample_is_red_on_the_order_of_the_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE MUTANT: the first 4,096 different values in row order read in place of the least ranks, and the walk kept beside the sample away -- an era of 4,200 small spellings at the column's start fills them and the column is published."""
    made = names.names_of(4200 + 9000, "comma", seed=64)
    era = [one.lower() for one in made[:4200] for _row in range(2)] + [one for one in made[4200:] for _row in range(3)]
    assert _hold(era) == taxonomy.HELD_PERSONS_NAMES

    def in_row_order(cells: "list[str]", absent: "frozenset[str]") -> "list[str]":
        return list(dict.fromkeys(cell for cell in cells if cell and cell not in absent))[:4096]

    monkeypatch.setattr(taxonomy, "_values_read", in_row_order)
    monkeypatch.setattr(taxonomy, "_held_by_the_walk", lambda cells, absent, named, judged: "")
    assert _hold(era) == ""


def _walked_share_held(cells: "list[str]", whole: "frozenset[str]") -> bool:
    """THE ORACLE OF THE WALK (lane CZ-F's reading, the base's rule, written here from its description and never calling the product): the cells visited by a step of the count times the golden share, rounded and raised until coprime with the count; the first 4,096 different values met; held where the names among them (known by construction, ``whole``) are 100 or more and two in three."""
    total = len(cells)
    step = max(1, round(total * 0.6180339887498949))
    while total > 1 and math.gcd(step, total) != 1:
        step += 1
    met: "dict[str, bool]" = {}
    place = 0
    for _visit in range(total):
        cell = cells[place]
        place = (place + step) % total
        if cell not in met:
            met[cell] = cell in whole
            if len(met) == 4096:
                break
    named = sum(1 for one in met.values() if one)
    return named >= 100 and 3 * named >= 2 * len(met)


def _many_rows(count: int, each: int, rest: int, kind: str, seed: int) -> "tuple[list[str], frozenset[str]]":
    """``count`` names written `Family, Given` on ``each`` rows, beside ``rest`` more different values on one row each (the same grammar's people in small letters, or reference codes), shuffled; and the names."""
    made = names.names_of(count + rest, "comma", seed=seed)
    others = [one.lower() for one in made[count:]] if kind == "small" else [f"ref {place:07d}" for place in range(rest)]
    cells = [one for one in made[:count] for _row in range(each)] + others
    random.Random(seed).shuffle(cells)
    return cells, frozenset(made[:count])


def test_the_walk_kept_beside_the_sample_holds_names_on_many_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE FREQUENCY, BOTH WAYS (lane CZ-G-b's repair 1, the orchestrator's LANE CZ-G-b RULINGS 3 (1)): past 4,096 different values the sample weighs each value once, so names on many rows beside MORE rare spellings were read short of half; the walk, which meets a value as often as its rows, is kept beside it at two in three. ONE GENERATED FAMILY -- 4,200 to 6,000 names on 6 to 25 rows beside more different values on one row each (their people in small letters, or codes), 38 to 49 per cent of the different values names -- each column held wherever the walk's oracle holds it (every one here), and the 73,000-row table of the statistics check (2,800 names on 25 rows beside 3,000 people written once in small letters); THE MUTANT, the sample alone: every one published."""
    draw = random.Random(81)
    family: "list[list[str]]" = []
    for case in range(10):
        count = draw.randrange(4200, 6001)
        each = draw.choice((6, 8, 12, 20, 25))
        rest = round(count * draw.uniform(1.05, 1.6))
        cells, whole = _many_rows(count, each, rest, "small" if case % 2 else "codes", seed=900 + case)
        assert _walked_share_held(cells, whole) and len(whole) < len(set(cells)) / 2, case
        family += [cells]
    cells, _whole = _many_rows(2800, 25, 3000, "small", seed=920)
    family += [cells]
    assert [case for case, cells in enumerate(family) if _hold(cells, role=taxonomy.ROLE_LONG_TAIL) != taxonomy.HELD_PERSONS_NAMES] == []
    monkeypatch.setattr(taxonomy, "_held_by_the_walk", lambda cells, absent, named, judged: "")
    assert [case for case, cells in enumerate(family) if _hold(cells, role=taxonomy.ROLE_LONG_TAIL)] == []


def _in_eras(first: "list[str]", first_rows: int, then: "list[str]", then_rows: int) -> "list[str]":
    """One era of values each on ``first_rows`` rows, then another each on ``then_rows``, in row order."""
    return [one for one in first for _row in range(first_rows)] + [one for one in then for _row in range(then_rows)]


def test_the_walk_kept_is_lane_cz_f_s_walk_cell_for_cell(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE WALK KEPT IS THE BASE'S (lane CZ-G-b's repair 1, the orchestrator's LANE CZ-G-b RULINGS 3 (1): a column is held where the sample OR the base's walk holds it, so the walk must be the base's for no column the base held to be unread). It reads every cell once -- every count from 1 to 600 and a few to 4,095, cell by cell; its step shares no factor with the count at the layouts' counts and at 2,000,000 rows -- and decides as the walk's oracle, written from its description, over four columns past 4,096 different values whose order of rows moves a walk: small-letter spellings on one row each before names on ten rows each (the oracle holds), and names on two rows each before small-letter spellings on ten rows each (the oracle does not). THE MUTANTS: the walk in row order decides the other way on all four; a step not raised until it shares no factor with the count reads some cells twice and some never."""
    read: "list[str]" = []

    def reading(text: str, named: bool) -> int:
        read.append(text)
        return taxonomy._A_NAME_WRITTEN_WHOLE

    def counts_not_read_cell_by_cell() -> "list[int]":
        missed: "list[int]" = []
        with monkeypatch.context() as patched:
            patched.setattr(taxonomy, "_persons_name_kind", reading)
            for total in [*range(1, 601), 1009, 1024, 2048, 2187, 3000, 4095]:
                read.clear()
                cells = [f"v{place}" for place in range(total)]
                taxonomy._held_by_the_walk(cells, frozenset(), False, {})
                if sorted(read) != sorted(cells):
                    missed += [total]
        return missed

    assert counts_not_read_cell_by_cell() == []
    for total in (4096, 49152, 116400, 200000, 206000, 2000000):
        step = taxonomy._walk_step(total)
        assert 1 <= step < total and math.gcd(step, total) == 1, (total, step)
    made = names.names_of(9000, "comma", seed=93)
    family = [
        (_in_eras([one.lower() for one in made[4500:9000]], 1, made[:4500], 10), frozenset(made[:4500])),
        (_in_eras([one.lower() for one in made[5000:9000]], 1, made[:5000], 10), frozenset(made[:5000])),
        (_in_eras(made[:3000], 2, [one.lower() for one in made[3000:6000]], 10), frozenset(made[:3000])),
        (_in_eras(made[:3600], 2, [one.lower() for one in made[3600:6000]], 10), frozenset(made[:3600])),
    ]
    assert [len(set(cells)) > 4096 for cells, _whole in family] == [True] * 4
    oracle = [_walked_share_held(cells, whole) for cells, whole in family]
    assert oracle == [True, True, False, False]

    def walked() -> "list[bool]":
        return [taxonomy._held_by_the_walk(cells, frozenset(), False, {}) == taxonomy.HELD_PERSONS_NAMES
                for cells, _whole in family]

    assert walked() == oracle
    monkeypatch.setattr(taxonomy, "_walk_step", lambda total: 1)
    assert walked() == [False, False, True, True]
    monkeypatch.setattr(taxonomy, "_walk_step", lambda total: max(1, round(total * taxonomy._WALK_SHARE)))
    assert counts_not_read_cell_by_cell() != []


def test_the_rows_a_value_stands_on_move_no_sample() -> None:
    """THE FREQUENCY (P4-D478 (a)'s stated bias of the walk): 6,000 names on 11 rows each beside 2,500 codes on 100 rows each, shuffled (70.6 per cent of the different values names, 20.9 per cent of the cells): held."""
    made = names.names_of(6000, "comma", seed=65)
    cells = [one for one in made for _row in range(11)] + [f"code {place}" for place in range(2500) for _row in range(100)]
    random.Random(66).shuffle(cells)
    assert _hold(cells) == taxonomy.HELD_PERSONS_NAMES


def test_the_rank_is_a_fixed_function_of_the_value() -> None:
    """THE RANK (`taxonomy._value_rank`): SplitMix64's finalizer over the value's length and code points folded modulo 2**61 - 1 -- the empty value's rank is SplitMix64's first word from the seed 0 (0xE220A8397B1DCDAF, the published reference); a lone surrogate passes; a text past 256 characters is read by its length and its first and last 128; the same values give the same ranks on every computer and in every run (no hash of the interpreter)."""
    assert taxonomy._value_rank("") == 0xE220A8397B1DCDAF
    assert taxonomy._value_rank("Cedar, Aaa") == 1163934746064782665
    assert taxonomy._value_rank("cedar, aaa") == 17219968245419456284
    assert taxonomy._value_rank("Müller, Jürgen") == 7708045787722422066
    assert taxonomy._value_rank("\ud800x") == 5249703357280036598
    assert taxonomy._value_rank("x" * 100) == 18198605049025430971
    assert taxonomy._value_rank("y" * 1000) == 745085007678766284
    assert taxonomy._value_rank("a" + "y" * 998 + "b") != taxonomy._value_rank("y" * 1000)
    with pytest.raises(TypeError):
        taxonomy._value_rank(7)  # type: ignore[arg-type]


def test_a_value_cut_is_passed_over_where_it_stands_again(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE WORK OF THE SAMPLE (`taxonomy._values_read`): the values kept are cut back to the bound by rank when they reach twice it, and a value ranking above the last one kept is passed over from then on -- over 100,000 different labels, one row each, the kept values are sorted 5 times (four cuts and the last reading), where taking every value in again sorts them 24 times (the mutant: the same 4,096 values read, the work growing with the rows); the values read are the 4,096 of least rank, a tie by the value."""
    labels = [f"Label {place:06d}" for place in range(100_000)]
    sorts = [0]
    ranked = taxonomy._ranked

    def counted(kept: "dict[str, int]") -> "list[tuple[int, str]]":
        sorts[0] += 1
        return ranked(kept)

    monkeypatch.setattr(taxonomy, "_ranked", counted)
    read = taxonomy._values_read(labels, frozenset())
    assert sorts[0] <= 8, sorts[0]
    least = sorted(labels, key=lambda label: (taxonomy._value_rank(label), label))[: taxonomy.PERSONS_NAMES_READ_AT_MOST]
    assert read == least


# -- item 3: the residual spellings -------------------------------------------------------

# The grammar of this file: family names, given names and initials made up
# of syllables (`names.made_up_word`), every filled and empty pattern of a
# name field's parts 3 to 7, each apostrophe mark in three places, each
# title before each particle, each suffix word written as a name writes it.
_DRAW_SEED = 67


def _parts(draw: random.Random) -> "tuple[str, str, str]":
    return names.made_up_word(draw, 2), names.made_up_word(draw, draw.choice((1, 2))), draw.choice(names.INITIALS)


def _caret_repeats() -> "list[str]":
    """The name field repeated after `~`: two or three repetitions, every pattern of parts 3 to 7 in the first, capitals or mixed case, an empty repetition at the end or none."""
    draw = random.Random(_DRAW_SEED)
    written: "list[str]" = []
    for pattern in names.CARET_PATTERNS:
        for capitals in (False, True):
            first = names.caret_spelling(draw, pattern, capitals)
            family, given, initial = _parts(draw)
            second = f"{family}^{given}^{initial}"
            written += [f"{first}~{second.upper() if capitals else second}",
                        f"{first}~{second.upper() if capitals else second}~"]
    return written


def _caret_subcomponents() -> "list[str]":
    """A family name in `&` subcomponents: the family name, its own prefix and name, a partner's prefix and name, each filled or empty."""
    draw = random.Random(_DRAW_SEED + 1)
    written: "list[str]" = []
    for _round in range(3):
        for particle in ("van", "de", "von der", ""):
            for partner in (False, True):
                family, given, initial = _parts(draw)
                other = names.made_up_word(draw, 2)
                whole = f"{particle} {family}".strip()
                pieces = [whole, particle, family] + ([particle, other] if partner else [])
                written += [f"{'&'.join(pieces)}^{given}", f"{'&'.join(pieces)}^{given}^{initial}".upper()]
    return written


def _apostrophes() -> "list[str]":
    """Each apostrophe mark of the one definition (the straight one and its old and new neighbours), in three places of a name."""
    draw = random.Random(_DRAW_SEED + 2)
    written: "list[str]" = []
    for mark in ("'", "’", "ʼ", "‘", "´", "`", *names.APOSTROPHES_MORE):
        for _round in range(5):
            family, given, _initial = _parts(draw)
            written += [f"O{mark}{family}, {given}", f"{given} D{mark}{family}", f"{family[:3]}{mark}{family.lower()}, {given}"]
    return written


def _titled_particles() -> "list[str]":
    """Each title before each particle-led family name, no given name."""
    draw = random.Random(_DRAW_SEED + 3)
    return [f"{title} {particle} {names.made_up_word(draw, 2)}" for title in names.TITLES for particle in names.TITLED_PARTICLES]


def _new_suffixes() -> "list[str]":
    """Each suffix word the one definition gained, after a name written given name first and after a family name's comma, with its point or none; and (lane CZ-G-b's repair 1, skeptic 1's item 2) each ordinal as the fourth part of a health message's name field, in capitals and in mixed case (`FAMILY^GIVEN^^3RD`, `Family^Given^M^2nd`)."""
    draw = random.Random(_DRAW_SEED + 4)
    written: "list[str]" = []
    for suffix in names.SUFFIXES_MORE:
        for point in ("", "."):
            word = suffix.rstrip(".") + point
            family, given, _initial = _parts(draw)
            written += [f"{given} {family} {word}", f"{family} {word}, {given}", f"{family}, {given} {word}"]
    for ordinal in ("2nd", "3rd", "4th"):
        family, given, initial = _parts(draw)
        written += [f"{family}^{given}^^{ordinal}".upper(), f"{family}^{given}^{initial}^{ordinal}",
                    f"{family}^{given}^{initial}^{ordinal}^^^L".upper()]
    return written


@pytest.mark.parametrize("family", ["caret_repeats", "caret_subcomponents", "apostrophes", "titled_particles", "new_suffixes"])
def test_every_residual_spelling_is_read_whole(family: str) -> None:
    """ONE GENERATED FAMILY EACH (lane CZ-F's combined verify item 3 and scoped verify 2 item 3: 0 of 200 to 500 read each on the base): every spelling read as a person's name written whole."""
    written = {"caret_repeats": _caret_repeats, "caret_subcomponents": _caret_subcomponents, "apostrophes": _apostrophes,
               "titled_particles": _titled_particles, "new_suffixes": _new_suffixes}[family]()
    assert len(written) >= 40, (family, len(written))
    missed = [text for text in written if not taxonomy.a_persons_name(text)]
    assert not missed, (family, len(missed), missed[:6])


def test_a_suffix_and_a_degree_after_a_family_name_alone_are_read_under_a_heading() -> None:
    """Under `patient_surname`: each new suffix word after a family name, with its point or none, in capitals or not; and a suffix then a degree, after the name or after commas (`Cedar Jr. MD`, `Cedar, Jr., MD`) -- 60 names each, held."""
    families = names.names_of(60, "family", seed=68)
    unread: "list[str]" = []
    for written in (*names.SUFFIXES_MORE, "Jr. MD", "Sr. DO", "JR. MD"):
        for capitals in (False, True):
            values = [f"{family.upper() if capitals else family} {written}" for family in families]
            if _hold(_column(values, rows=600), name="patient_surname") != taxonomy.HELD_NAMED_AS_PERSONS_NAMES:
                unread += [values[0]]
    values = [f"{family}, Jr., MD" for family in families]
    if _hold(_column(values, rows=600), name="patient_surname") != taxonomy.HELD_NAMED_AS_PERSONS_NAMES:
        unread += [values[0]]
    # ...and a family name alone in a health message's name field, an
    # ordinal its fourth part (`FAMILY^^^4TH`; lane CZ-G-b's repair 1).
    for ordinal in ("2ND", "3RD", "4TH"):
        values = [f"{family.upper()}^^^{ordinal}" for family in families]
        if _hold(_column(values, rows=600), name="patient_surname") != taxonomy.HELD_NAMED_AS_PERSONS_NAMES:
            unread += [values[0]]
    assert not unread, unread


def test_the_residual_spellings_controls_are_no_name() -> None:
    """THE CONTROLS: a tilde, an ampersand or a figure outside the name field's grammar or a suffix word (`Left~Right`, `CEDAR^AAA&B`, `Cedar 2, Aaa`, `Cedar, Aaa 12`, `Grade 2nd Burn`), more repetitions of the name field than `_CARET_REPETITIONS_AT_MOST`, a title before particles alone (`Dr. de la`), and an apostrophe mark at a word's edge (`Oʻ, Aaa`): never a name written whole."""
    for text in ("Left~Right", "CEDAR^AAA&B", "Cedar 2, Aaa", "Cedar, Aaa 12", "Grade 2nd Burn", "Dr. de la", "Oʻ, Aaa",
                 "Cedar′, Aaa", "~".join(["CEDAR^AAA"] * 9), "van&van^Aaa", "LEFT^2ND~RIGHT^3RD"):
        assert not taxonomy.a_persons_name(text), text


def _names_of_two_types() -> "list[str]":
    """The name field repeated after `~`, a name written whole and a family name alone of another type (`FAMILY^GIVEN^^^^^L~OTHER^^^^^^M`, a maiden or former name beside the legal one), in capitals and in mixed case, the repetitions in either order."""
    draw = random.Random(_DRAW_SEED + 5)
    written: "list[str]" = []
    for _round in range(30):
        family, given, _initial = _parts(draw)
        other = names.made_up_word(draw, 2)
        legal, former = f"{family}^{given}^^^^^L", f"{other}^^^^^^M"
        written += [f"{legal}~{former}".upper(), f"{former}~{legal}", f"{legal}~{other}"]
    return written


def test_a_repeated_name_field_keeps_its_strongest_reading(monkeypatch: pytest.MonkeyPatch) -> None:
    """CARRY 5 OF SKEPTIC 1, BUILT (the orchestrator's LANE CZ-G-b RULINGS 4 (3)): a name field repeated after `~` is the STRONGEST reading of its repetitions, so a name beside a family name alone of another type is a name written whole and 1,000 such names under `patient_label` are held (the weakest reading published them; the base too); the control that pinned the weakest reading held a name written whole (`CEDAR^AAA~~~~~~~~~~~~~CEDAR`) and is read so. THE MUTANT, the weakest reading: unread."""
    written = _names_of_two_types()
    assert [text for text in written if not taxonomy.a_persons_name(text)] == []
    assert taxonomy.a_persons_name("CEDAR^AAA~~~~~~~~~~~~~CEDAR")
    draw = random.Random(_DRAW_SEED + 6)
    column: "dict[str, bool]" = {}
    while len(column) < 1000:
        family, given, _initial = _parts(draw)
        column[f"{family}^{given}^^^^^L~{names.made_up_word(draw, 3)}^^^^^^M".upper()] = True
    assert _hold(_column(list(column), rows=20000)) == taxonomy.HELD_PERSONS_NAMES
    caret_kind = taxonomy._caret_name_kind

    def weakest(text: str) -> int:
        read = taxonomy._name_read(text)
        if "~" not in read:
            return caret_kind(text)
        return min(caret_kind(one) for one in read.split("~") if one.strip())

    monkeypatch.setattr(taxonomy, "_caret_name_kind", weakest)
    assert [text for text in written if not taxonomy.a_persons_name(text)]
    assert _hold(_column(list(column), rows=20000)) == ""


def test_the_residual_spellings_are_red_on_their_mutants(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE MUTANTS: the apostrophes without the marks added, the suffixes without the words added, and the figure test back to any figure, each leaves its family unread; the repetitions and the subcomponents with their marks unread do too."""
    monkeypatch.setattr(taxonomy, "_PERSONS_NAME_APOSTROPHES", "'’ʼ‘´`")
    assert [text for text in _apostrophes() if not taxonomy.a_persons_name(text)]
    monkeypatch.undo()
    monkeypatch.setattr(taxonomy, "_PERSONS_NAME_SUFFIXES", frozenset({"jr", "sr", "ii", "iii", "iv"}))
    assert [text for text in _new_suffixes() if not taxonomy.a_persons_name(text)]
    monkeypatch.undo()
    monkeypatch.setattr(taxonomy, "_a_figure_outside_a_suffix", taxonomy._holds_a_figure)
    assert [text for text in _new_suffixes() if not taxonomy.a_persons_name(text)]
    monkeypatch.undo()

    def not_cut_at_carets(text: str) -> bool:
        # ...skeptic 1's mutant M10: the words not cut at `^`, so an ordinal
        # in a name field is a figure outside a suffix word.
        words = taxonomy._plain_words(taxonomy._name_read(text.replace(",", " ").replace("~", " ")))
        return any(taxonomy._holds_a_figure(word) and not taxonomy._a_name_suffix(word) for word in words)

    monkeypatch.setattr(taxonomy, "_a_figure_outside_a_suffix", not_cut_at_carets)
    assert [text for text in _new_suffixes() if "^" in text and not taxonomy.a_persons_name(text)]
    monkeypatch.undo()
    monkeypatch.setattr(taxonomy, "_CARET_REPETITIONS_AT_MOST", 0)
    assert [text for text in _caret_repeats() if not taxonomy.a_persons_name(text)]
    monkeypatch.undo()
    monkeypatch.setattr(taxonomy, "_FAMILY_SUBCOMPONENTS_AT_MOST", 1)
    assert [text for text in _caret_subcomponents() if not taxonomy.a_persons_name(text)]


# -- item 3, inside a word: the owed marks in every position, against their controls -------
#
# The orchestrator's LANE CZ-G-b RULINGS 2, from batch 4s's combined character
# sweep: the reader read the owed marks in the owed positions, but a character
# that prints nothing INSIDE a family name cut the word in two (1,632 of 2,880
# generated names read wrongly). Written afresh here: the 31 spaces and format
# characters, the 11 dashes and the soft hyphen, each in each position of
# generated names of seven shapes, each variant judged against its controls --
# the same spelling written with the ordinary marks the one definition reads
# the mark as (a space; for a mark that prints nothing a space and nothing; for
# a dash a hyphen; for the soft hyphen a space, nothing and a hyphen). A MISS is
# a control read as a name and the variant not.
_OWED_SPACES = ("\t", "\n", "\r", "\x0c", "\x0b", "\x85", "\xa0", " ",
                *(chr(code) for code in range(0x2000, 0x2010)),
                " ", " ", " ", " ", "⁠", "　", "﻿")
_OWED_DASHES = ("-", "‐", "‑", "‒", "–", "—", "―", "−", "﹘", "﹣", "－")
_SOFT = "­"
# The owed marks a display draws as nothing: the zero-width space, non-joiner
# and joiner, the two direction marks, the word joiner and the byte order mark.
_DRAWN_AS_NOTHING = frozenset({"​", "‌", "‍", "‎", "‏", "⁠", "﻿"})
_POSITIONS = ("all", "first", "doubled", "space_before", "space_after", "leading", "trailing", "inside")
_SWEPT_SHAPES = ("comma", "apostrophe", "given_first", "capitals", "caret", "initials", "mixed")


def _ordinary_marks(mark: str) -> "tuple[str, ...]":
    """The ordinary marks a mark is read as: its controls are the spelling written with each."""
    if mark == _SOFT:
        return (" ", "", "-")
    if mark in _OWED_DASHES:
        return ("-",)
    if mark in _DRAWN_AS_NOTHING:
        return (" ", "")
    return (" ",)


def _inside_the_first_word(text: str) -> int:
    """Where the middle of the text's first run of two letters or more is, or -1."""
    run = 0
    for place in range(len(text) + 1):
        if place < len(text) and text[place].isalpha():
            run += 1
            continue
        if run >= 2:
            return place - run // 2
        run = 0
    return -1


def _written_with(text: str, target: str, position: str, put: str) -> "str | None":
    """The spelling with ``put`` written where ``position`` says, for the ordinary mark ``target`` (a space, or a hyphen) the mark stands for; None where the spelling has no such place."""
    if position in ("all", "first", "doubled", "space_before", "space_after") and target not in text:
        return None
    written = {
        "all": lambda: text.replace(target, put),
        "first": lambda: text.replace(target, put, 1),
        "doubled": lambda: text.replace(target, put + put),
        "space_before": lambda: text.replace(target, " " + put),
        "space_after": lambda: text.replace(target, put + " "),
        "leading": lambda: put + text,
        "trailing": lambda: text + put,
    }
    if position == "inside":
        at = _inside_the_first_word(text)
        return None if at <= 0 else text[:at] + put + text[at:]
    return written[position]()


def _swept() -> "list[tuple[str, str, str, str, list[str]]]":
    """Every (spelling, mark, position, variant, controls) of the sweep: the inside position for the marks drawn as nothing and the soft hyphen, the positions beside a space for the spaces, a dash standing for a hyphen, and the soft hyphen standing for a space and for a hyphen."""
    cases: "list[tuple[str, str, str, str, list[str]]]" = []
    for shape in _SWEPT_SHAPES:
        for text in names.names_of(30, shape, seed=70):
            for mark in (*_OWED_SPACES, *_OWED_DASHES, _SOFT):
                targets = (" ", "-") if mark == _SOFT else ("-",) if mark in _OWED_DASHES else (" ",)
                for target in targets:
                    for position in _POSITIONS:
                        if position == "inside" and (target != " " or (mark not in _DRAWN_AS_NOTHING and mark != _SOFT)):
                            continue
                        if position in ("doubled", "space_before", "space_after") and target == "-":
                            continue
                        variant = _written_with(text, target, position, mark)
                        if variant is None:
                            continue
                        controls = [_written_with(text, target, position, put) for put in _ordinary_marks(mark)]
                        if position == "inside":
                            controls += [text]
                        cases += [(text, mark, position, variant, [one for one in controls if one is not None])]
    return cases


def _sweep_misses() -> "tuple[dict[str, int], list[str]]":
    """The cases with a control read as a name, by position, and the misses (a control read and the variant not)."""
    read: "dict[str, int]" = {}
    misses: "list[str]" = []
    for text, mark, position, variant, controls in _swept():
        if not any(taxonomy.a_persons_name(control) for control in controls):
            continue
        read[position] = read.get(position, 0) + 1
        if not taxonomy.a_persons_name(variant):
            misses += [f"{position} U+{ord(mark):04X} {text!r}"]
    return read, misses


def test_every_owed_mark_in_every_position_reads_as_its_control() -> None:
    """THE GENERATED SWEEP (LANE CZ-G-b RULINGS 2): 210 names of seven shapes, the 43 owed marks in the eight positions: 0 misses, inside a word included (every name of the grammar a control reads), each position judged on cases enough."""
    read, misses = _sweep_misses()
    assert not misses, (len(misses), misses[:8])
    assert read.get("inside", 0) >= 8 * 150, read
    for position in _POSITIONS:
        assert read.get(position, 0) >= 300, (position, read)


def _readings_before(text: str) -> "tuple[str, ...]":
    """The readings as batch 4s's merge left them: the soft hyphen as a space and as a hyphen, no character set aside."""
    if _SOFT not in text:
        return (text,)
    return (text.replace(_SOFT, " "), text.replace(_SOFT, "-"))


def test_the_sweep_is_red_on_the_readings_before(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE MUTANT: the readings without the one that sets aside what prints nothing leave names written with such a character inside the family name unread."""
    monkeypatch.setattr(taxonomy, "_name_readings", _readings_before)
    _read, misses = _sweep_misses()
    assert [one for one in misses if one.startswith("inside ")]


def _marked(values: "list[str]", mark: str, position: str) -> "list[str]":
    """Each value with ``mark`` written where ``position`` says (for a space), as it is where it has no such place."""
    return [_written_with(value, " ", position, mark) or value for value in values]


def test_a_mark_drawn_as_nothing_holds_no_control_its_plain_writing_does_not(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE PRICE AT THE UNIT LEVEL: every staff group's control of 40 ordinary labels (each heading added's, the organisations' and the swab's), each mark drawn as nothing written inside the first word of every label, for its first space and for every space, under each heading added and under a neutral name, is held exactly as the labels written plainly are -- not at all; 120 names written so under a neutral name are held, as written plainly. The soft hyphen: under a neutral name likewise; under a heading that names a person, a label of the closed list cut by it reads, as a hyphen, as a hyphenated family name (`Mot-her`) and its column is held, as with the readings before this lane (the hyphen's reading is lane CZ-F's: a stated false alarm, plan P4-D494 (a)), so the reading this lane adds holds nothing more."""
    groups = sorted({*names.STAFF_HEADINGS_ADDED.values(), *names.STAFF_HEADINGS_LEFT.values()})
    whole = names.names_of(120, "comma", seed=71)
    for mark in sorted(_DRAWN_AS_NOTHING):
        for position in ("inside", "first", "all"):
            for heading in sorted(names.STAFF_HEADINGS_ADDED):
                control = names.control_labels(names.STAFF_HEADINGS_ADDED[heading])
                assert _hold(_column(_marked(control, mark, position)), name=heading) == "", (heading, mark, position)
            for group in groups:
                assert _hold(_column(_marked(names.control_labels(group), mark, position))) == "", (group, mark, position)
            assert _hold(_column(_marked(whole, mark, position))) == taxonomy.HELD_PERSONS_NAMES, (mark, position)
    soft = {heading: _hold(_column(_marked(names.control_labels(names.STAFF_HEADINGS_ADDED[heading]), _SOFT, "inside")),
                           name=heading) for heading in sorted(names.STAFF_HEADINGS_ADDED)}
    for group in groups:
        assert _hold(_column(_marked(names.control_labels(group), _SOFT, "inside"))) == "", group
    assert _hold(_column(_marked(whole, _SOFT, "inside"))) == taxonomy.HELD_PERSONS_NAMES
    monkeypatch.setattr(taxonomy, "_name_readings", _readings_before)
    before = {heading: _hold(_column(_marked(names.control_labels(names.STAFF_HEADINGS_ADDED[heading]), _SOFT,
                                             "inside")), name=heading) for heading in sorted(names.STAFF_HEADINGS_ADDED)}
    # ...under `social_worker` and `case_manager` lane CZ-G-b's reading held
    # two more: `Fol<U+00AD>low Up Needed` read set aside is `Follow Up
    # Needed`, a name written whole before a word lane CZ-G-b made a role, so
    # it is a name (the one price of the orchestrator's LANE CZ-G-b RULINGS 4
    # (1), stated in P4-D494 (a)). Since batch 4t's fix round 4 the older
    # readings hold them too: `Ini-tial Assessment`, the qualifier cut by the
    # soft hyphen read as a hyphen, is a family name alone beside a word kept
    # as a role (`taxonomy._a_family_name_beside_a_role`), as the base read
    # it. The older false alarm reaches 18 of the 18 headings either way.
    assert sorted(heading for heading in soft if soft[heading] != before[heading]) == []
    assert all(soft.values()) and all(before.values()), (soft, before)


def _set_aside_everywhere(text: str) -> "tuple[str, ...]":
    """THE MUTANT, lane CZ-G-b's third reading before its repair 1: every character that prints nothing set aside, wherever it stands."""
    if not any(taxonomy._prints_nothing(character) for character in text):
        return (text,)
    spaced = "".join(" " if taxonomy._prints_nothing(character) else character for character in text)
    dashed = "".join(("-" if character == _SOFT else " ") if taxonomy._prints_nothing(character) else character
                     for character in text)
    gone = "".join("" if taxonomy._prints_nothing(character) else character for character in text)
    return tuple(dict.fromkeys((spaced, dashed, gone)))


def _set_aside_before_a_small_letter(text: str) -> "tuple[str, ...]":
    """THE MUTANT, the narrowed form without its guard: set aside only where the next letter is a small one."""
    if not any(taxonomy._prints_nothing(character) for character in text):
        return (text,)
    spaced = "".join(" " if taxonomy._prints_nothing(character) else character for character in text)
    dashed = "".join(("-" if character == _SOFT else " ") if taxonomy._prints_nothing(character) else character
                     for character in text)
    pieces: "list[str]" = []
    for place, character in enumerate(text):
        if not taxonomy._prints_nothing(character):
            pieces += [character]
            continue
        after = next((one for one in text[place + 1:] if not taxonomy._prints_nothing(one)), "")
        pieces += ["" if after.isalpha() and after.islower() else " "]
    return tuple(dict.fromkeys((spaced, dashed, "".join(pieces))))


# The headings whose small controls name a term of work or a shift, the two
# groups whose labels are two words each (`Full Time`, `Day Shift`).
_TWO_WORD_SMALL_CONTROLS = ("staff_and_employee", "staffing")


def test_a_mark_drawn_as_nothing_for_a_space_parts_the_words(monkeypatch: pytest.MonkeyPatch) -> None:
    """SKEPTIC 1'S ITEM 3 (the orchestrator's LANE CZ-G-b RULINGS 4 (2)): the three-label small control of each staff heading added (`SMALL_CONTROLS`), written with each mark drawn as nothing or the soft hyphen for every space and for the first one, as written and in capitals, is NOT held under any of the 18 headings: a mark is set aside only where the next letter is a small one, or a lone letter stands on one side of it (set aside everywhere, `Full<U+200B>Time` read as `FullTime`, one family name, and the controls of 8 headings were held). Written in sentence case (`Full<U+200B>time`) the mark stands where it stands inside a word, and the controls of those 8 headings ARE held: a stated false alarm (P4-D494 (a)). A name in capitals with a mark beside a lone letter of its family name (`C<U+200B>EDAR, AAA`, `AAA CEDA<U+200B>R`) is read, as written plainly. THE MUTANTS: set aside everywhere, the small controls are held; set aside only before a small letter, the names in capitals are unread."""
    marks = sorted(_DRAWN_AS_NOTHING | {_SOFT})

    def held_controls(case: str, first: bool) -> "list[str]":
        held: "list[str]" = []
        for mark in marks:
            for heading in sorted(names.STAFF_HEADINGS_ADDED):
                labels = list(names.SMALL_CONTROLS[names.STAFF_HEADINGS_ADDED[heading]])
                labels = ([one.upper() for one in labels] if case == "capitals" else
                          [one.lower().capitalize() for one in labels] if case == "sentence" else labels)
                written = [one.replace(" ", mark, 1) if first else one.replace(" ", mark) for one in labels]
                if _hold(_column(written), name=heading):
                    held += [f"U+{ord(mark):04X} {heading}"]
        return held

    draw = random.Random(_DRAW_SEED + 7)
    lone: "list[tuple[str, str]]" = []
    for _name in range(20):
        family, given, _initial = _parts(draw)
        family, given = family.upper(), given.upper()
        for mark in marks:
            for cut in (family[:1] + mark + family[1:], family[:-1] + mark + family[-1:]):
                lone += [(f"{family}, {given}", f"{cut}, {given}"), (f"{given} {family}", f"{given} {cut}")]
    assert all(taxonomy.a_persons_name(plain) for plain, _variant in lone)
    assert [variant for _plain, variant in lone if not taxonomy.a_persons_name(variant)] == []
    for case in ("as written", "capitals"):
        assert held_controls(case, False) == [] and held_controls(case, True) == [], case
    staffing = sorted(heading for heading, group in names.STAFF_HEADINGS_ADDED.items() if group in _TWO_WORD_SMALL_CONTROLS)
    assert len(staffing) == 8
    assert held_controls("sentence", False) == [f"U+{ord(mark):04X} {heading}" for mark in marks for heading in staffing]
    monkeypatch.setattr(taxonomy, "_name_readings", _set_aside_everywhere)
    assert len(held_controls("as written", False)) == len(marks) * 8
    monkeypatch.setattr(taxonomy, "_name_readings", _set_aside_before_a_small_letter)
    assert [variant for _plain, variant in lone if not taxonomy.a_persons_name(variant)]


# -- item 4: the staff headings and their controls ----------------------------------------


@pytest.mark.parametrize("heading", sorted(names.STAFF_HEADINGS_ADDED))
def test_each_staff_heading_added_holds_its_names_and_its_held_out_control(heading: str) -> None:
    """Each heading added (P4-D478's staff headings outside the closed list): it names a person's name, written apart and in capitals with no mark between its words; 40 names of every spelling under it are held. ITS CONTROL (the orchestrator's LANE CZ-G-b RULINGS 3 (3)), 40 ordinary labels of its kind drawn from OUTSIDE the closed list's words (`HELD_OUT_CONTROLS`), IS HELD under it and under no neutral name: the stated price of keeping the 18 headings, HIPAA first (P4-D494 (4), owner lane CZ-G-b2) -- where the labels the closed list was narrowed by (`control_labels`, three of them alone too) are not, by construction."""
    assert taxonomy.named_as_persons_names(heading)
    assert taxonomy.named_as_persons_names(heading.replace("_", "").upper()), heading
    assert taxonomy.named_as_persons_names(f"{heading}_name"), heading
    assert _hold(_column(names.names_of(40, "mixed", seed=69)), name=heading) == taxonomy.HELD_NAMED_AS_PERSONS_NAMES
    group = names.STAFF_HEADINGS_ADDED[heading]
    held_out = list(names.HELD_OUT_CONTROLS[group])
    closed = _NARROWED | taxonomy._ROLE_AND_SERVICE_WORDS | taxonomy._NOT_PERSONS_NAME_WORDS
    assert len(set(held_out)) == 40 and not [one for one in held_out if one.split()[-1].lower() in closed]
    assert _hold(_column(held_out), name=heading) == taxonomy.HELD_NAMED_AS_PERSONS_NAMES, heading
    assert _hold(_column(held_out)) == "", heading
    control = names.control_labels(group)
    assert len(set(control)) == 40
    assert _hold(_column(control), name=heading) == "", heading
    assert _hold(_column(list(names.SMALL_CONTROLS[group])), name=heading) == "", heading


@pytest.mark.parametrize("heading", sorted(names.STAFF_HEADINGS_LEFT))
def test_each_staff_heading_left_out_names_no_person_its_control_held_were_it_named(heading: str) -> None:
    """Each heading left out names no person; its control of 40 ordinary labels -- a swab's results and a radiograph's views, organisations written as one word -- is what a name that says a person's name would hold (under `surgeon`), so adding it would hold those labels."""
    assert not taxonomy.named_as_persons_names(heading)
    control = names.control_labels(names.STAFF_HEADINGS_LEFT[heading])
    assert len(set(control)) == 40
    assert _hold(_column(control), name=heading) == ""
    assert _hold(_column(control), name="surgeon") == taxonomy.HELD_NAMED_AS_PERSONS_NAMES, heading


def test_the_staff_headings_are_red_on_their_mutants(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE MUTANTS: with no run of words, `social_worker` and `next_of_kin` name no person; with the qualifiers of the old list, `second_reader` and `er_md` none; with a workplace's technicians alone, `pharmacy_resident` none; with the closed list of roles and services as it was, the small controls of every group added are held (three statuses, terms of work, relatives or shifts read as family names alone)."""
    monkeypatch.setattr(taxonomy, "_STAFF_ROLE_RUNS", ())
    assert not taxonomy.named_as_persons_names("social_worker") and not taxonomy.named_as_persons_names("next_of_kin")
    monkeypatch.undo()
    monkeypatch.setattr(taxonomy, "_CLINICIAN_QUALIFIERS", taxonomy._CLINICIAN_QUALIFIERS
                        - frozenset({"first", "second", "third", "er", "ed", "rad"}))
    assert not taxonomy.named_as_persons_names("second_reader") and not taxonomy.named_as_persons_names("er_md")
    monkeypatch.undo()
    monkeypatch.setattr(taxonomy, "_WORKPLACE_ROLE_WORDS", frozenset({"tech", "techs"}))
    assert not taxonomy.named_as_persons_names("pharmacy_resident")
    monkeypatch.undo()
    assert _NARROWED == taxonomy._STATUS_AND_STAFFING_WORDS
    assert not _NARROWED & taxonomy._ROLE_AND_SERVICE_WORDS
    monkeypatch.setattr(taxonomy, "_STATUS_AND_STAFFING_WORDS", frozenset())
    for heading in ("social_worker", "witness", "staff", "next_of_kin", "er_md"):
        small = list(names.SMALL_CONTROLS[names.STAFF_HEADINGS_ADDED[heading]])
        assert _hold(_column(small), name=heading) == taxonomy.HELD_NAMED_AS_PERSONS_NAMES, heading


# THE WORDS LANE CZ-G-b NARROWED THE CLOSED LIST BY (`taxonomy._STATUS_AND_STAFFING_WORDS`), written here
# whole: `husband` and `diem` left them at its repair 1, family names of their own as `son` and `cousin` are.
_NARROWED = frozenset({
    "assigned", "consulted", "seen", "needed", "applicable", "progress", "assessment", "reassessment",
    "transferred", "closed", "active", "inactive", "review", "present", "absent", "unavailable", "verbal",
    "written", "telephone", "time", "contract", "contractor", "locum", "traveler",
    "temporary", "permanent", "terminated", "leave", "retired", "casual", "seasonal", "intern", "mother",
    "father", "daughter", "brother", "sister", "aunt", "uncle", "grandmother", "grandfather", "grandson",
    "granddaughter", "grandchild", "niece", "nephew", "wife", "fiance", "fiancee", "stepmother",
    "stepfather", "neighbor", "neighbour", "rotating", "shift", "moonlighter", "director", "supervisor", "trainee",
})
# ...and every word lane CZ-G-b made the last word of a role at its build (the 59 above, `husband` and `diem`,
# and the clinicians' roles the closed list lacked, singular and plural, read as values): skeptic 1's family.
_MADE_ROLES = _NARROWED | frozenset({
    "husband", "diem", "anesthesiologist", "anesthesiologists", "anesthetist", "anesthetists", "attendings",
    "author", "authors", "cardiologist", "cardiologists", "circulator", "circulators", "consultant", "consultants",
    "cosigner", "cosigners", "crna", "crnas", "dentist", "fellows", "hospitalist", "hospitalists", "intensivist",
    "pathologist", "pathologists", "pcp", "perfusionist", "perfusionists", "prescriber", "prescribers",
    "proceduralist", "proceduralists", "radiologist", "radiologists", "reviewer", "reviewers", "scribes",
    "witness", "witnesses",
})
# ...of which, at the repair, these name a role only where no person's name written whole stands before them; the
# others (the plurals, `husband`, `diem`) never, as on the base.
_STILL_ROLES = _NARROWED | frozenset({
    "anesthesiologist", "anesthetist", "author", "cardiologist", "circulator", "consultant", "cosigner", "crna",
    "dentist", "hospitalist", "intensivist", "pathologist", "pcp", "perfusionist", "prescriber", "proceduralist",
    "radiologist", "reviewer", "witness",
})
# ...of which one is also a degree of the one definition: after a family name alone it is that person's degree
# (`Cedar CRNA`), never a role.
_DEGREES_MADE_ROLES = frozenset({"crna"})
# The person headings skeptic 1's family is read under: the base's and lane CZ-G-b's.
_PERSON_HEADINGS = ("contact_full_name", "kin_name", "guardian_full_name", "staff_name", "provider_name", "surgeon",
                    "anesthesia_provider", "patient_full_name", "crna", "anesthetist", "emergency_contact_name",
                    "next_of_kin", "social_worker")


def _written_as(word: str) -> str:
    return word.upper() if word in ("crna", "crnas", "pcp") else word.capitalize()


def test_a_word_made_a_role_never_unreads_a_name_written_whole_before_it(monkeypatch: pytest.MonkeyPatch) -> None:
    """SKEPTIC 1'S ITEM 1, THE BLOCKER (the orchestrator's LANE CZ-G-b RULINGS 4 (1)): every word lane CZ-G-b made the last word of a role (99), after a person's name written whole in four shapes (`Given Family, W`, `Family, Given - W`, `Given Family W`, `Family, Given W`: a person and that person's relation, status or degree), 6 names under each of 13 person headings, and 120 names under `patient_full_name`: held, as on the base (3,267 of 3,267 columns of the skeptic's family held on the base and 0 on the lane's build head). `Step Mother` and `Medical Radiologist` stay roles: one word before. THE MUTANT, no name written whole read before the word: every column unread but those of `Given Family, W`, whose two name words before the comma are also a family name alone of two words before a mark (`_a_family_name_before_a_mark`, lane CZ-G-b's repair 2), the 14 columns of each word that is still a role, and (batch 4t's fix round 4) those of `Given Family W`, a family name alone of two words beside the word with no mark, 13 of each; and with no family name alone read before a mark either, the column of 120 names of each word that is still a role under `patient_full_name` stays held (batch 4t's fix round 5: the value arm's second reading, the role test set aside, reads 120 names written whole)."""
    draw = random.Random(_DRAW_SEED + 8)
    people = [(names.made_up_word(draw, 2), names.made_up_word(draw, 3)) for _person in range(120)]
    shapes = ("{g} {f}, {w}", "{f}, {g} - {w}", "{g} {f} {w}", "{f}, {g} {w}")
    columns: "list[tuple[str, list[str]]]" = []
    for word in sorted(_MADE_ROLES):
        for shape in shapes:
            values = [shape.format(g=given, f=family, w=_written_as(word)) for given, family in people[:6]]
            columns += [(heading, values) for heading in _PERSON_HEADINGS]
        columns += [("patient_full_name", [shapes[0].format(g=given, f=family, w=_written_as(word)) for given, family in people])]
    assert len(columns) == len(_MADE_ROLES) * (4 * len(_PERSON_HEADINGS) + 1)
    assert [f"{heading} {values[0]}" for heading, values in columns if not _hold(_column(values, rows=120), name=heading)] == []
    assert taxonomy._a_role_or_a_service("Step Mother") and taxonomy._a_role_or_a_service("Medical Radiologist")
    # ...and a role before the word is no person's name: `Family Member, Daughter`, `Charge Nurse Mother`.
    assert taxonomy._a_role_or_a_service("Family Member, Daughter") and taxonomy._a_role_or_a_service("Charge Nurse Mother")
    monkeypatch.setattr(taxonomy, "_a_name_before_the_last_word", lambda words: False)
    still = [values[0] for heading, values in columns if _hold(_column(values, rows=120), name=heading)]
    # ...and, since batch 4t's fix round 4, the columns of `Given Family W` with no mark, whose two name words are a
    # family name alone beside a word kept as a role (`taxonomy._a_family_name_beside_a_role`), under both stubs.
    no_mark = len(_STILL_ROLES) * len(_PERSON_HEADINGS)
    assert len(still) == len([word for word in _MADE_ROLES if word not in _STILL_ROLES]) * (4 * len(_PERSON_HEADINGS) + 1) + (
        len(_STILL_ROLES) * (len(_PERSON_HEADINGS) + 1)) + no_mark
    # ...and with no family name alone read before a mark either, every column of six names of the words still roles
    # is unread but those of no mark; the column of 120 names of each stays held by the value arm's second reading
    # (batch 4t's fix round 5).
    monkeypatch.setattr(taxonomy, "_a_family_name_before_a_mark", lambda text, words: False)
    still = [values[0] for heading, values in columns if _hold(_column(values, rows=120), name=heading)]
    assert len(still) == len([word for word in _MADE_ROLES if word not in _STILL_ROLES]) * (
        4 * len(_PERSON_HEADINGS) + 1) + no_mark + len(_STILL_ROLES)


# The marks a family name alone stands before the word with, each a reading of the one definition: a comma, a
# comma in a cell in capitals, a dash standing alone, the en dash standing alone (`_name_read` reads it as one),
# and a dash at either edge of a word (the dashes `_words_of_a_name_part` joins words by).
_BEFORE_A_MARK = ("{f}, {w}", "{F}, {W}", "{f} - {w}", "{f} – {w}", "{f} -{w}", "{f}- {w}")


def test_a_family_name_alone_before_a_mark_and_a_word_kept_as_a_role_is_a_name(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE COMBINED VERIFY'S ITEM 1, THE BLOCKER OF REPAIR 1 (the orchestrator's LANE CZ-G-b RULINGS 6 (1)): each of the 77 words lane CZ-G-b keeps as the last word of a role (`_STILL_ROLES` but the degree `crna`), after a person's family name alone and a comma or a dash with a space beside it (`_BEFORE_A_MARK`: `Family, Word`, `FAMILY, WORD`, `Family - Word`, the en dash, `Family -Word`, `Family- Word` -- a person and that person's relation or role), 6 family names under each of the 13 person headings of this file and 120 under `emergency_contact_name`: held, as on the base, which read each as a name written whole or a family name alone (the verify's family: 3,850 columns of the comma, capitals and spaced-dash shapes the base held and repair 1's head read as roles). With no mark before the word, or a dash with no space beside it, it stays a role (`Family Word` has the shape of `Step Mother` and `Day Shift`, `Family-Word` that of `Part-Time`: the stated cost of plan P4-D494 (a)), and a role before the mark is no family name (`Parent - Mother`, `Family Member, Daughter`). THE MUTANT, no family name alone read before a mark: every column of six family names unread; the column of 120 of each word under `emergency_contact_name` stays held (batch 4t's fix round 5: `Family, Word` is a family name and a given name once the role test is set aside, and the value arm's second reading reads 120 names written whole)."""
    draw = random.Random(_DRAW_SEED + 11)
    families = list(dict.fromkeys(names.made_up_word(draw, 3) for _person in range(200)))[:120]
    kept = sorted(_STILL_ROLES - _DEGREES_MADE_ROLES)
    assert len(families) == 120 and len(kept) == 77
    columns: "list[tuple[str, list[str]]]" = []
    for word in kept:
        for shape in _BEFORE_A_MARK:
            values = [shape.format(f=family, F=family.upper(), w=_written_as(word), W=word.upper()) for family in families[:6]]
            columns += [(heading, values) for heading in _PERSON_HEADINGS]
        columns += [("emergency_contact_name", [_BEFORE_A_MARK[0].format(f=family, w=_written_as(word)) for family in families])]
    assert len(columns) == 77 * (len(_BEFORE_A_MARK) * len(_PERSON_HEADINGS) + 1)
    assert [f"{heading} {values[0]}" for heading, values in columns if not _hold(_column(values, rows=120), name=heading)] == []
    family = families[0]
    for text in (f"{family} Mother", f"{family.upper()} MOTHER", f"{family}-Mother", "Step Mother", "Day Shift",
                 "Part-Time", "Parent - Mother", "Family Member, Daughter", "Charge Nurse, Mother"):
        assert taxonomy._a_role_or_a_service(text), text
    monkeypatch.setattr(taxonomy, "_a_family_name_before_a_mark", lambda text, words: False)
    assert [f"{heading} {values[0]}" for heading, values in columns if _hold(_column(values, rows=120), name=heading)] == [
        f"emergency_contact_name {_BEFORE_A_MARK[0].format(f=families[0], w=_written_as(word))}" for word in kept]


def test_a_run_of_relations_joined_by_a_comma_calls_the_role_test_once_a_word(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE SCOPED VERIFY 2'S ITEM 1 (time, not HIPAA; the orchestrator's LANE CZ-G-b RULINGS 8): the 14 relations of `names.RELATIONS` joined by a comma, a role, are read by at most 15 calls of the role test (`taxonomy._a_role_or_a_service`): one a word, and one more where the words before the last are a family name alone, which `_a_family_name_before_a_mark` reads BEFORE the role test. Repair 2's head read the role test first, so each word called it twice on the words before it: 16,383 calls here, 65,535 for 16 relations, and the profile command over 1,000 different lists of 16 relations at 20,000 rows took 276 CPU seconds where repair 1 took 19.2. The answer is the same either way. THE MUTANT, the role test read first on the words before the mark (repair 2's order): more than 15 calls."""
    calls = [0]
    role_or_service = taxonomy._a_role_or_a_service
    family_name_before_a_mark = taxonomy._a_family_name_before_a_mark

    def counted(text: str) -> bool:
        calls[0] += 1
        return role_or_service(text)

    def role_test_first(text: str, words: "list[str]") -> bool:
        before = " ".join(words[:-1]).rstrip(",")
        return bool(before) and not taxonomy._a_role_or_a_service(before) and family_name_before_a_mark(text, words)

    run = ", ".join(names.RELATIONS)
    assert len(names.RELATIONS) == 14
    monkeypatch.setattr(taxonomy, "_a_role_or_a_service", counted)
    assert taxonomy._a_role_or_a_service(run)
    assert calls[0] <= 15, calls[0]
    monkeypatch.setattr(taxonomy, "_a_family_name_before_a_mark", role_test_first)
    calls[0] = 0
    assert taxonomy._a_role_or_a_service(run)
    assert calls[0] > 15, calls[0]


def test_the_titles_and_degrees_family_is_held_under_every_person_heading() -> None:
    """The product's own generated family `titles_and_degrees` (`Dr. Given Family`, `Given Family, CRNA`, `Family, Given MD`; skeptic 1's item 1: no case read it under a heading), 60 spellings under each person heading of this file and each staff heading added: held."""
    draw = random.Random(_DRAW_SEED + 9)
    spellings = list(dict.fromkeys(names._spelling("titles_and_degrees", draw) for _spelling in range(80)))[:60]
    headings = sorted({*_PERSON_HEADINGS, "attending", "patient_surname", *names.STAFF_HEADINGS_ADDED})
    assert [heading for heading in headings if not _hold(_column(spellings), name=heading)] == []


def test_every_word_made_a_role_written_as_a_family_name(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE STATISTICS CHECK'S ITEM 2 (the orchestrator's LANE CZ-G-b RULINGS 3 (2)): every word lane CZ-G-b made the last word of a role (99), written as a family name, one and two values under `patient_surname`, `surgeon`, `patient_full_name` and `name_last` (a family name's, a clinician's, a whole name's and a last name's headings). HELD, as on the base: after two given names (`Gg Hh Word`, a name written whole before it), family name first (`Word, Gg`), and in every shape the words that are no role again -- `husband` and `diem`, family names of their own, and the plurals of the clinicians' roles (`Fellows`), a role only written singular. AND, since batch 4t's fix round 4 (the orchestrator's LANE I4t RULINGS 5, push critic 24's B1), every word still made a role after one given name and two given-first (a family name alone before such a word, no word before it one that qualifies a role: `taxonomy._a_family_name_beside_a_role`) and BESIDE ANOTHER FAMILY NAME (an ordinary family name in the column makes the words kept as roles alone family names alone again: `taxonomy._kinds_settled`), as the base read them: 924 of the 1,240 columns of this case that 34e9a218 left unheld are held again. NOT HELD, the narrowing's stated price against the base (plan P4-D494 (4); owner lane CZ-G-b2): the 78 words still made roles written alone, the lane's purpose, and a given name that is also a word qualifying a role (`Non Dentist`: the 4 columns of `two_given_first` this draw makes). THE MUTANTS: `husband` and `diem` among the roles, or the plurals read as roles, unread them."""
    draw = random.Random(_DRAW_SEED + 10)
    headings = ("patient_surname", "surgeon", "patient_full_name", "name_last")
    wrong: "list[str]" = []
    cases: "list[tuple[str, str, list[str]]]" = []
    for word in sorted(_MADE_ROLES):
        written = _written_as(word)
        first, second, third, other = (names.made_up_word(draw, 2), names.made_up_word(draw, 2),
                                       names.made_up_word(draw, 1), names.made_up_word(draw, 3))
        shapes = {"alone": [written], "after_a_given_name": [f"{first} {written}"],
                  "after_two_given_names": [f"{first} {second} {written}"], "beside_a_family_name": [other, written],
                  "two_given_first": [f"{first} {written}", f"{third} {written}"], "family_first": [f"{written}, {first}"]}
        for shape, values in shapes.items():
            cases += [(word, shape, values)]
            qualified = shape in ("after_a_given_name", "two_given_first") and any(
                one.lower() in taxonomy._ROLE_QUALIFIER_WORDS for one in (first, third)[: 1 + (shape == "two_given_first")])
            expected = (shape != "alone" and not qualified) or word not in _STILL_ROLES
            for heading in headings:
                if bool(_hold(_column(values, rows=400), name=heading)) != expected:
                    wrong += [f"{heading} {values}"]
    assert wrong == [], (len(wrong), wrong[:6])
    monkeypatch.setattr(taxonomy, "_STATUS_AND_STAFFING_WORDS", taxonomy._STATUS_AND_STAFFING_WORDS | {"husband", "diem"})
    assert [values for word, _shape, values in cases if word in ("husband", "diem")
            and not _hold(_column(values, rows=400), name="patient_surname")]
    monkeypatch.undo()
    monkeypatch.setattr(taxonomy, "_CLINICIAN_ROLES_AS_VALUES", taxonomy._CLINICIAN_ROLE_WORDS - taxonomy._ROLE_AND_SERVICE_WORDS)
    assert [values for word, _shape, values in cases if word == "fellows"
            and not _hold(_column(values, rows=400), name="patient_surname")]


# One to three clinicians' roles written as values, alone or after a word
# that qualifies them, each last word a clinician's role and no other list's.
_ROLES_AS_VALUES = (
    ("Pathologist",), ("Pathologist", "Radiologist"), ("Anesthesiologist", "Perfusionist", "Hospitalist"),
    ("Medical Radiologist", "Senior Pathologist"), ("Intensivist", "Cardiologist"),
)


def test_a_clinician_s_role_written_as_a_value_names_the_role(monkeypatch: pytest.MonkeyPatch) -> None:
    """A CLINICIAN'S ROLE WRITTEN AS A VALUE names the role (`taxonomy._a_role_or_a_service`): one to three of them under a name that says a person's name -- `surgeon`, `attending`, `provider_name`, `patient_surname` and each staffing heading added -- are not held, where on the base the four older headings held each column (one to three family names alone are held whatever their number); THE MUTANT, the roles read as names: every one is held."""
    headings = ("surgeon", "attending", "provider_name", "patient_surname",
                *sorted(heading for heading, group in names.STAFF_HEADINGS_ADDED.items() if group == "staffing"))
    for roles in _ROLES_AS_VALUES:
        for role in roles:
            last = role.split()[-1].lower()
            assert last in taxonomy._CLINICIAN_ROLE_WORDS and last not in taxonomy._ROLE_AND_SERVICE_WORDS
            assert last not in taxonomy._NOT_PERSONS_NAME_WORDS
        for heading in headings:
            assert _hold(_column(list(roles)), name=heading) == "", (heading, roles)
    role_or_service = taxonomy._a_role_or_a_service

    def roles_unread(text: str) -> bool:
        return False if text.split()[-1].lower() in taxonomy._CLINICIAN_ROLE_WORDS else role_or_service(text)

    monkeypatch.setattr(taxonomy, "_a_role_or_a_service", roles_unread)
    for roles in _ROLES_AS_VALUES:
        for heading in headings:
            assert _hold(_column(list(roles)), name=heading) == taxonomy.HELD_NAMED_AS_PERSONS_NAMES, (heading, roles)


# -- ONE 20,000-row case through the commands -----------------------------------------------


def test_clinicians_written_with_a_degree_through_the_commands_at_twenty_thousand_rows(tmp_path: pathlib.Path) -> None:
    """SKEPTIC 1'S ITEM 1 AT THE OWNER'S FLOOR, nobody answering: 60 clinicians written `Given Family CRNA` under `anesthesia_provider` beside 1,000 patients on 20 rows each, through profile, generate (seed 0) and validate, the table floor on: held, its Safe Harbor question put, 0 real names shown, 0 real twin cells (the base held it; lane CZ-G-b's build head read `CRNA` as a role, published the 60 and wrote 20,000 real twin cells). The residual spellings at this size, and the share edge's own table, which meets the held writer's time cliff of this line (STANDING NOTE ADDENDUM 2 (8), owner lane HB3-b), are read at the unit level here and by `K-HZ-42` with a bound."""
    seen = names.measure(tmp_path / "crna", "crna_beside", "crna", 20000)
    assert names.failures(seen) == [], seen
    assert ["no", "yes"] in seen["asked"]  # type: ignore[operator]
    assert seen["shown"] == seen["shown_folded"] == seen["twin_folded"] == seen["twin_inside"] == 0


def test_contacts_written_family_name_and_relation_through_the_commands_at_twenty_thousand_rows(tmp_path: pathlib.Path) -> None:
    """THE COMBINED VERIFY'S ITEM 1 AT THE OWNER'S FLOOR (the orchestrator's LANE CZ-G-b RULINGS 6 (1)), nobody answering: an emergency contact for each of 1,000 people, written `Family, Relation` (`names.RELATIONS`, 14 words lane CZ-G-b keeps as roles) on 20 rows each beside a case number under `emergency_contact_name`, through profile, generate (seed 0) and validate, the table floor on: held, its Safe Harbor question put, 0 real values shown, 0 twin cells equal to one or holding one (the base held it; repair 1's head read every value as a role, published the 1,000 and wrote 20,000 real twin cells)."""
    seen = names.measure(tmp_path / "relation", "relation_beside", "relation", 20000)
    assert names.failures(seen) == [], seen
    assert ["no", "yes"] in seen["asked"]  # type: ignore[operator]
    assert seen["shown"] == seen["shown_folded"] == seen["twin_folded"] == seen["twin_inside"] == 0
