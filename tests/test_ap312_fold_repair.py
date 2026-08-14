"""The fold-collision layout is checked and repaired (amendment A-P3-12).

Owner ruling of 2026-08-14 on the recorded fidelity miss: repair the
fold feasibility. Method G9.3 step 5 is the rule; this file is what
holds the shipped generator to it.

WHAT WENT WRONG. G9.3 settles which slots carry a column's fold
collisions BEFORE any spelling exists, and what a family can SUPPLY is a
fact about spellings: its identities' own case positions, and whatever
edge spacing their lengths leave inside the taking slot's window. Edge
spacing only LENGTHENS, so an identity pinned to the longest published
length supplies no spaced partner at all. A layout could therefore ask
one family for more collisions than it holds while another family of
the same column had room to spare, and the twin wrote a fresh identity
where a partner was owed -- missing the published `n_distinct_folded`
on 3.7 per cent of a battery of descriptions a real producer wrote,
every one of which its own values answer exactly.

WHAT THIS FILE HOLDS TO:

* eight producer columns that the rule before this amendment got wrong,
  each named with the shape that defeated it, meet EVERY published fact
  and name no deviation at all;
* a battery of producer-built columns whose descriptions publish a fold
  collision meets the published folded count on every run, at four
  seeds, and files no deviation;
* the repair CANNOT REACH a column the earlier rule already answered:
  the handles it adds are inert when they are empty, which is checked
  against an independent restatement of the rule as it stood;
* the enumeration the repair walks is bounded by its stated budget and
  every packing it offers meets all four class counts and both alphabet
  counts, so nothing is traded for the folded count;
* where the folded count still cannot be held, the generation report
  NAMES it, and says something true about a column of record numbers
  rather than the sentence written for a column of dates.

THE RED CHECK, one per guarantee, so no test here is assumed to bite.
`REINSTATE` in the environment puts one piece of the old behaviour back
before every test in this file; measured on the commit that adds it:

* `REINSTATE=A-P3-12` -- the layout rule exactly as it stood, the first
  packing laid out once with no ceiling and no end-carrier ask: **36 of
  39 fail**, which is every witness at every seed and every battery
  seed;
* `REINSTATE=A-P3-12-note` -- the report sentence as it stood, the one
  written for a column of dates: **1 fails**, the report test;
* `REINSTATE=A-P3-12-inert` -- the repair's choice written so an empty
  ask still moves it: **1 fails**, the test that carries the licence
  for the whole change;
* `REINSTATE=A-P3-12-packings` -- the enumeration with one candidate
  that misses a published count: **37 fail**, the margin test and every
  witness, because a repair reaching for such a packing IS the trade
  this amendment exists not to make.

`_the_rule_before_the_repair` is built from the shipped walk itself
rather than from a copy of it, so it cannot drift away from what it
claims to restore.
"""

import os
import pathlib
import random

import pytest

import fixtures
from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    reading,
    taxonomy,
)

SEEDS = (0, 1, 17, 63)

# Eight producer columns the rule before amendment A-P3-12 got wrong.
# Every one was found by describing real values with the shipped
# producer, so the column's own multiset is a conforming assignment of
# every count its description publishes, and each is kept here with the
# shape that defeated the earlier rule.
SHAPE_PINNED_IDENTITY = (
    "the family's one identity is pinned to the longest length, and "
    "spacing only lengthens"
)
SHAPE_OVER_ASKED = (
    "one family is asked for two collisions and holds one, while another "
    "family with room to spare is asked for none"
)
SHAPE_END_ON_IDENTITY = (
    "the length end sits on the family's only identity, so its partners "
    "fold onto a spelling that has no room left"
)
SHAPE_CASELESS = (
    "the same, with the collision owed to a notation inside accounting "
    "parentheses, which never holds a case"
)
SHAPE_IDLE_FAMILY = (
    "three slots of one family, one identity, and a second family "
    "standing idle"
)
SHAPE_FLIPS_SPENT = (
    "three collisions owed and the flips of one parent spent"
)
SHAPE_ALL_ALONE = (
    "the first exact packing gives every group a family of its own, so "
    "no slot has a sibling to fold onto"
)
SHAPE_ALL_ALONE_TWICE = (
    "the same, with TWO collisions owed and both unbuildable in the "
    "first packing"
)

WITNESSES = (
    (
        SHAPE_PINNED_IDENTITY,
        ["(-9)"] * 20 + ["(-9) "] * 2 + ["hnJRDl"] * 2 + ["hnjrdl"] * 4,
    ),
    (
        SHAPE_OVER_ASKED,
        ["(-8)"] * 14 + ["3E999"] * 21 + ["3e999"] * 4
        + ["6E999"] * 4 + ["6e999"] * 5 + ["C9gU"] * 8,
    ),
    (
        SHAPE_END_ON_IDENTITY,
        ["-864"] * 16 + ["5E999"] * 19 + ["5e999"] * 3 + ["5e999 "] * 2,
    ),
    (
        SHAPE_CASELESS,
        ["(-7)"] * 10 + ["(-7) "] * 3 + ["267"] * 7,
    ),
    (
        SHAPE_IDLE_FAMILY,
        ["5E999"] * 18 + ["5E999 "] * 3 + ["5e999"] * 4 + ["nIs9"] * 17,
    ),
    (
        SHAPE_FLIPS_SPENT,
        ["7E999"] * 1 + ["7e999"] * 12 + ["aZR"] * 9 + ["azr"] * 2
        + ["azr "] * 2,
    ),
    (
        SHAPE_ALL_ALONE,
        ["(-0)"] * 15 + ["-9524"] * 6 + ["-995119"] * 2 + ["922"] * 13
        + ["^zOfJN"] * 12 + ["^zofjn"] * 2,
    ),
    (
        SHAPE_ALL_ALONE_TWICE,
        ["#C"] * 2 + ["#c"] * 12 + ["(-78)"] * 12 + ["-938"] * 15
        + ["-938 "] * 2 + ["44212"] * 2,
    ),
)


# -- the reinstatement, which is the red check -------------------------


def _the_rule_before_the_repair(
    column: contract.ColumnBlock, groups: "tuple[int, ...]"
) -> "tuple[list[str], list[generation.Deviation]]":
    """The layout rule exactly as it stood before amendment A-P3-12.

    One packing -- the first the shape search of G9.6 offers -- laid out
    once, with no per-family ceiling and no end-carrier ask, and
    whatever it produced kept. This is built by calling the shipped walk
    with both of the repair's handles empty rather than by copying its
    body, so it restores what it says it restores even after the walk
    itself is edited.
    """
    facts = column.facts
    assert isinstance(facts, contract.IdentifierFacts)
    total = len(groups)
    folded = min(column.n_distinct_folded, total)
    partners = total - folded
    shape = generation._identifier_families(
        column, facts, groups, folded, partners
    )
    caps = [
        -1
        for _cell in range(len(generation._CLASSES) * len(generation._BANDS))
    ]
    built, notes, _short, _supply = generation._laid_identifiers(
        column, facts, groups, folded, partners, shape, caps, ()
    )
    return built, notes


THE_SENTENCE_FOR_DATES = (
    "The twin holds MORE different values, ignoring case and edge "
    "spacing, than the description records, for the same reason: how "
    "often a value repeats is not a fact this column's rule holds on to."
)


def _a_choice_whose_handles_are_not_inert(
    cells: "list[int]",
    folded: int,
    partners: int,
    folds: "list[bool]",
    caps: "list[int]",
    asked: "tuple[int, ...]",
) -> "list[int]":
    """The repair's choice written so an EMPTY ask still changes it.

    The licence for amendment A-P3-12 is that its two handles do nothing
    at all when they are empty. This is the nearest wrong version --
    scanning forward rather than backward on the added pass -- and the
    guarantee test below turns red on it.
    """
    total = len(cells)
    if partners < 1 or partners >= total or folded < 1:
        return list(range(total))
    left = list(range(total))
    tail: list[int] = []
    for _step in range(partners):
        picked = -1
        for wanted in (True, False):
            for place in range(len(left)):
                if folds[left[place]] != wanted:
                    continue
                kept = len(
                    [one for one in left if cells[one] == cells[left[place]]]
                )
                if kept >= 2:
                    picked = place
                    break
            if picked >= 0:
                break
        if picked < 0:
            picked = len(left) - 1
        tail = [left[picked]] + tail
        left = left[:picked] + left[picked + 1:]
    return left + tail


def _packings_that_are_not_all_exact(
    column: contract.ColumnBlock,
    facts: contract.IdentifierFacts,
    groups: "tuple[int, ...]",
    folded: int,
    partners: int,
    budget: int,
) -> "list[tuple[list[int], tuple[int, int], bool]]":
    """The enumeration with one candidate that does NOT meet the margins.

    A repair that reached for a packing failing a class or an alphabet
    count would be trading one published fact for another, which is the
    design this amendment exists not to be. The guarantee test below
    turns red on it.
    """
    offered = generation._identifier_packings(
        column, facts, groups, folded, partners, budget
    )
    if not offered:
        return offered
    packed, carriers, signing = offered[0]
    moved = list(packed)
    moved[0] = (moved[0] + 1) % (len(generation._CLASSES)
                                 * len(generation._BANDS))
    return offered + [(moved, carriers, signing)]


@pytest.fixture(autouse=True)
def _reinstated(monkeypatch: pytest.MonkeyPatch) -> None:
    """Put the pre-amendment rule back when REINSTATE asks for it.

    Four values, one per guarantee this file carries, so every test here
    has a demonstrated red rather than an assumed one:

    * `A-P3-12` -- the layout rule as it stood: one packing, no ceiling,
      no end-carrier ask, one look;
    * `A-P3-12-note` -- the report sentence as it stood, which was
      written for a column of dates;
    * `A-P3-12-inert` -- the repair's choice written so an empty ask
      still moves it, which is the licence for the whole change;
    * `A-P3-12-packings` -- the enumeration with one candidate that
      misses a published count, which is the trade this amendment
      exists not to make.
    """
    asked_for = os.environ.get("REINSTATE")
    if asked_for == "A-P3-12":
        monkeypatch.setattr(
            generation, "_identifier_cells", _the_rule_before_the_repair
        )
    if asked_for == "A-P3-12-note":
        monkeypatch.setattr(
            generation,
            "_folded_excess_reason",
            lambda _column: THE_SENTENCE_FOR_DATES,
        )
    if asked_for == "A-P3-12-inert":
        monkeypatch.setattr(
            generation, "_collision_order",
            _a_choice_whose_handles_are_not_inert,
        )
    if asked_for == "A-P3-12-packings":
        monkeypatch.setattr(
            generation, "_identifier_packings",
            _packings_that_are_not_all_exact,
        )


# -- helpers -----------------------------------------------------------


def _described(
    folder: pathlib.Path, name: str, values: "list[str]"
) -> contract.Profile:
    """Write a one-column table, describe it, load the description.

    Every cell is quoted so a value carrying an edge space survives the
    round trip into the description the twin is then built from.
    """
    lines = ["key"]
    for value in values:
        lines = lines + ['"' + value.replace('"', '""') + '"']
    path = fixtures.write(folder, f"{name}.csv", "\n".join(lines) + "\n")
    table = reading.read_table(str(path))
    document = profile.build_document(table, taxonomy.Settings(), ["key"])
    target = fixtures.write_profile(folder, f"{name}-profile.json", document)
    return contract.load_profile(str(target))


def _recount(cells: "tuple[str, ...]") -> "dict[str, int]":
    """Every published count of a column of record numbers, remeasured."""
    present = [one for one in cells if one != ""]
    seen: dict[str, int] = {}
    for one in present:
        seen[one] = seen.get(one, 0) + 1
    sizes: dict[int, int] = {}
    for many in seen.values():
        sizes[many] = sizes.get(many, 0) + 1
    classes: dict[str, int] = {}
    for one in present:
        found = parsing.classify_number(one)
        classes[found] = classes.get(found, 0) + 1
    return {
        "n_present": len(present),
        "n_missing": len(cells) - len(present),
        "n_numeric": classes.get(parsing.NUMBER, 0),
        "n_out_of_range": classes.get(parsing.NUMBER_OUT_OF_RANGE, 0),
        "n_contradictory": classes.get(parsing.NUMBER_CONTRADICTORY, 0),
        "n_not_numeric": classes.get(parsing.NOT_A_NUMBER, 0),
        "n_all_digits": sum(
            1 for one in present
            if parsing.is_digit_text(parsing.trimmed(one))
        ),
        "n_code_alphabet": sum(
            1 for one in present
            if parsing.is_code_text(parsing.trimmed(one))
        ),
        "min_length": min((len(one) for one in present), default=0),
        "max_length": max((len(one) for one in present), default=0),
        "n_distinct": len(seen),
        "n_distinct_folded": len({parsing.folded(one) for one in present}),
        "sizes": sizes,
    }


def _published(column: contract.ColumnBlock) -> "dict[str, int]":
    """The same counts, as the description publishes them."""
    facts = column.facts
    assert isinstance(facts, contract.IdentifierFacts)
    return {
        "n_present": column.n_present,
        "n_missing": column.n_missing,
        "n_numeric": column.n_numeric,
        "n_out_of_range": column.n_out_of_range,
        "n_contradictory": column.n_contradictory,
        "n_not_numeric": column.n_not_numeric,
        "n_all_digits": facts.n_all_digits,
        "n_code_alphabet": facts.n_code_alphabet,
        "min_length": facts.min_length,
        "max_length": facts.max_length,
        "n_distinct": column.n_distinct,
        "n_distinct_folded": column.n_distinct_folded,
        "sizes": {
            int(key): value
            for key, value in facts.n_distinct_by_occurrences.items()
        },
    }


# -- the witnesses -----------------------------------------------------


@pytest.mark.parametrize("shape,values", WITNESSES)
@pytest.mark.parametrize("seed", SEEDS)
def test_a_column_the_earlier_rule_missed_now_meets_every_count(
    shape: str, values: "list[str]", seed: int, tmp_path: pathlib.Path
) -> None:
    """Each witness column's own values answer its own description.

    So owner decision 6's infeasible corner is not reached and the twin
    owes every count exactly, the published folded count included.
    """
    described = _described(tmp_path, "w", values)
    column = described.columns[0]
    assert column.role == "identifier", shape
    assert column.n_distinct > column.n_distinct_folded, (
        f"this witness has to publish a fold collision to be one: {shape}"
    )
    twin = generation.generate(described, seed=seed)
    got = _recount(twin.columns[0])
    want = _published(column)
    missed = {
        name: (want[name], got[name])
        for name in want
        if want[name] != got[name]
    }
    assert missed == {}, (
        f"the twin of a description whose own column answers it exactly "
        f"missed {sorted(missed)} -- {shape}"
    )
    assert [note.fact for note in twin.deviations] == [], (
        f"nothing is given up on this column, so nothing may be named: "
        f"{shape}"
    )


# -- the battery -------------------------------------------------------


def _a_value(rng: random.Random, length: int) -> str:
    """One made-up record number of one of the seven producer shapes."""
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    kind = rng.randrange(7)
    if kind == 0:
        return "-" + "".join(
            rng.choice("0123456789") for _step in range(max(length - 1, 1))
        )
    if kind == 1:
        return "".join(
            rng.choice("123456789") for _step in range(max(length - 4, 1))
        ) + "e999"
    if kind == 2:
        return "".join(
            rng.choice("123456789") for _step in range(max(length - 4, 1))
        ) + "E999"
    if kind == 3:
        return "(-" + "".join(
            rng.choice("0123456789") for _step in range(max(length - 3, 1))
        ) + ")"
    if kind == 4:
        return "".join(
            rng.choice("123456789") for _step in range(max(length, 1))
        )
    if kind == 5:
        return rng.choice(letters) + "".join(
            rng.choice(letters + "0123456789-_")
            for _step in range(max(length - 1, 0))
        )
    return rng.choice("!@#$%^&*") + "".join(
        rng.choice(letters + "!.") for _step in range(max(length - 1, 0))
    )


def _a_column(seed: int) -> "list[str]":
    """One producer column whose codes collide when case is ignored."""
    rng = random.Random(7_000_000 + seed)
    values: list[str] = []
    for _group in range(rng.randrange(2, 8)):
        text = _a_value(rng, rng.randrange(1, 8))
        values = values + [text] * rng.randrange(1, 22)
    pool = [one for one in sorted(set(values)) if one.lower() != one.upper()]
    for one in pool[: rng.randrange(0, 3)]:
        turned = one.upper() if one.islower() else one.lower()
        values = values + [turned] * rng.randrange(1, 5)
    if rng.random() < 0.35 and values:
        chosen = sorted(set(values))
        values = values + [
            chosen[rng.randrange(len(chosen))] + " "
        ] * rng.randrange(1, 4)
    rng.shuffle(values)
    if rng.random() < 0.2:
        values = values + [""] * rng.randrange(1, 5)
    return values


_BATTERY: "list[tuple[int, contract.Profile]]" = []


def _battery(
    tmp_path_factory: pytest.TempPathFactory,
) -> "list[tuple[int, contract.Profile]]":
    """The battery, built once per session through the real producer."""
    if _BATTERY:
        return _BATTERY
    root = tmp_path_factory.mktemp("fold-repair-battery")
    for seed in range(120):
        here = root / f"case-{seed}"
        here.mkdir()
        described = _described(here, "case", _a_column(seed))
        column = described.columns[0]
        if column.role != "identifier":
            continue
        if column.n_distinct <= column.n_distinct_folded:
            continue
        _BATTERY.append((seed, described))
    return _BATTERY


@pytest.mark.parametrize("seed", SEEDS)
def test_the_battery_holds_its_folded_count_on_every_run(
    seed: int, tmp_path_factory: pytest.TempPathFactory
) -> None:
    """Every description here publishes a fold collision its own column met.

    The battery asserts the folded count AND an empty deviation list,
    which is what makes a layout change that quietly gave one up visible
    to this suite at all.
    """
    battery = _battery(tmp_path_factory)
    assert len(battery) >= 60, (
        "the battery has to reach the shape it exists for; a producer "
        "change that stopped these columns publishing a fold collision "
        "would leave this file asserting nothing"
    )
    missed: list[tuple[int, int, int]] = []
    named: list[tuple[int, str]] = []
    for case, described in battery:
        column = described.columns[0]
        twin = generation.generate(described, seed=seed)
        cells = [one for one in twin.columns[0] if one != ""]
        folded = len({parsing.folded(one) for one in cells})
        if folded != column.n_distinct_folded:
            missed.append((case, column.n_distinct_folded, folded))
        for note in twin.deviations:
            named.append((case, note.fact))
    assert missed == [], (
        "every one of these descriptions was written by the producer from "
        "a real column, so that column's own values are a conforming "
        "assignment and the folded count is owed exactly"
    )
    assert named == [], (
        "nothing is given up on these columns, so nothing may be named"
    )


# -- the repair cannot reach a column the earlier rule answered ---------


def _the_choice_before_the_repair(
    cells: "list[int]", folded: int, partners: int, folds: "list[bool]"
) -> "list[int]":
    """G9.6's collision-slot rule as it stood, restated independently.

    Written from the specification's own sentence rather than from the
    shipped function, so that comparing the two compares two readings of
    one rule instead of one reading with itself.
    """
    total = len(cells)
    if partners < 1 or partners >= total or folded < 1:
        return list(range(total))
    left = list(range(total))
    tail: list[int] = []
    for _step in range(partners):
        picked = -1
        for wanted in (True, False):
            for place in range(len(left) - 1, -1, -1):
                if folds[left[place]] != wanted:
                    continue
                kept = len(
                    [one for one in left if cells[one] == cells[left[place]]]
                )
                if kept >= 2:
                    picked = place
                    break
            if picked >= 0:
                break
        if picked < 0:
            picked = len(left) - 1
        tail = [left[picked]] + tail
        left = left[:picked] + left[picked + 1:]
    return left + tail


def test_the_repairs_two_handles_are_inert_when_they_are_empty() -> None:
    """With no ceiling and no ask, the choice is the choice it always was.

    This is the whole licence for the repair: the first layout offered
    is the layout that shipped, so a description the earlier rule
    answered exactly is answered by it, byte for byte, and no column
    that met every published count can move.
    """
    rng = random.Random(20260814)
    room = len(generation._CLASSES) * len(generation._BANDS)
    empty = [-1 for _cell in range(room)]
    for _case in range(4000):
        total = rng.randrange(1, 9)
        cells = [rng.randrange(room) for _slot in range(total)]
        folds = [rng.random() < 0.5 for _slot in range(total)]
        folded = rng.randrange(0, total + 1)
        partners = total - folded
        assert generation._collision_order(
            cells, folded, partners, folds, empty, ()
        ) == _the_choice_before_the_repair(cells, folded, partners, folds), (
            f"cells={cells} folded={folded} folds={folds}"
        )


def test_every_packing_the_repair_offers_meets_every_published_count(
    tmp_path: pathlib.Path,
) -> None:
    """A repaired column is never a column that traded one count for another.

    Each candidate packing assigns whole groups to class-and-alphabet
    families; this checks the four class counts and the three alphabet
    counts of every candidate the enumeration offers, on the witnesses
    that need more than the first packing.
    """
    for shape, values in WITNESSES:
        here = tmp_path / _safe(shape)
        here.mkdir(parents=True, exist_ok=True)
        described = _described(here, "p", values)
        column = described.columns[0]
        facts = column.facts
        assert isinstance(facts, contract.IdentifierFacts)
        groups = generation._groups_of(facts.n_distinct_by_occurrences)
        total = len(groups)
        folded = min(column.n_distinct_folded, total)
        offered = generation._identifier_packings(
            column, facts, groups, folded, total - folded,
            generation._FOLD_PACKINGS,
        )
        assert offered, shape
        assert len(offered) <= generation._FOLD_PACKINGS, (
            f"the enumeration has to end inside its stated budget: {shape}"
        )
        width = len(generation._BANDS)
        for packed, _carriers, _signing in offered:
            classes = [0, 0, 0, 0]
            alphabets = [0, 0, 0]
            for place in range(total):
                cell = packed[place]
                classes[cell // width] += groups[place]
                alphabets[cell - (cell // width) * width] += groups[place]
            assert classes == [
                column.n_numeric,
                column.n_out_of_range,
                column.n_contradictory,
                column.n_not_numeric,
            ], shape
            assert alphabets == [
                facts.n_all_digits,
                facts.n_code_alphabet - facts.n_all_digits,
                column.n_present - facts.n_code_alphabet,
            ], shape


def _safe(shape: str) -> str:
    """A folder name from a witness description."""
    return "".join(
        one if one.isalnum() else "-" for one in shape
    )[:40]


# -- and where it still cannot be held, the report says so -------------


def test_a_folded_count_that_cannot_be_held_is_named_and_named_truly(
    tmp_path: pathlib.Path,
) -> None:
    """The deviation is filed, and its reason is true of THIS role.

    The sentence the report carried for a twin holding more folded
    identities than the description records was written for a column of
    dates -- "how often a value repeats is not a fact this column's rule
    holds on to" -- and a declared column of record numbers is the one
    role where that is false: the repetition pattern is a count that
    rule meets, and meets in the same run. A reader told the wrong cause
    cannot act on the line.
    """
    described = _described(
        tmp_path, "named", ["(-9)"] * 20 + ["(-9) "] * 2 + ["hnJRDl"] * 2
        + ["hnjrdl"] * 4,
    )
    column = described.columns[0]
    notes = generation._recount_notes(
        column,
        (
            column.n_present,
            column.n_missing,
            column.n_distinct,
            column.n_distinct_folded + 1,
        ),
    )
    assert [note.fact for note in notes] == ["n_distinct_folded"]
    said = notes[0].note
    assert notes[0].published == f"{column.n_distinct_folded}"
    assert notes[0].achieved == f"{column.n_distinct_folded + 1}"
    assert "how often a value repeats" not in said, (
        "that is the cause on a column of dates and it is false here: "
        "this rule meets the repetition pattern, and this very run does"
    )
    assert "no second way to spell" in said, (
        "the reader has to be told what actually happened -- the "
        "description asks for two spellings that come down to one value, "
        "and there was nowhere to write the second"
    )
