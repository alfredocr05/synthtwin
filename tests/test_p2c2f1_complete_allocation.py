"""Review item P2-C2-F1: the exact packing is complete, and it is joint.

Round 1 found a greedy packing losing published counts in silence. The
repair added an exact search, bounded it with two constants, and kept
the greedy one behind them. Round 2 refused the bound and the split:

* a description the PRODUCER emits reached the depth constant -- a
  declared column of record numbers publishing 132 different group
  sizes made the depth expression 402 against a ceiling of 400 -- so an
  exact packing that the real column's own values prove exists was
  never looked for, and three published counts came out wrong;
* free text decided its numeric class in one walk and its alphabet in a
  second, and columns of numbers too large to hold decided their
  magnitude class and their sign the same way, so joint assignments
  that exist were thrown away.

WHAT THIS FILE HOLDS THE REPAIR TO:

1. no ceiling counts the SHAPE of a description any more, and the walk
   finds an exact packing wherever one exists -- including on the
   producer-emitted description that reached the withdrawn one, and
   checked against exhaustion rather than against a second walk;
2. the class and the alphabet of a column of free text are decided
   TOGETHER, on a five-row column whose joint answer two separate walks
   miss;
3. the magnitude class and the sign of a wide column are decided
   together, over every shape of a producer-emitted battery;
4. no ceiling of any kind remains. The work ceiling this file used to
   measure headroom against was reached by a producer description and
   is withdrawn (review item P2-C3-F1, whose own file holds that
   description and the guard on it); what is measured here is that the
   greedy fallback is unreachable from a description a real table
   produced, demonstrated by running every shape of two batteries and
   finding an exact packing every time.

Every description here is built by the REAL producer from a seeded
neutral table (plan D13: no data-format file is ever committed), so
what is exercised is the path from table to twin and not a document
this file made up.
"""

import itertools
import pathlib

import pytest

import fixtures
from synthtwin import (
    contract,
    generation,
    profile,
    reading,
    taxonomy,
)

EXACT_COUNTS = (
    "n_numeric",
    "n_not_numeric",
    "n_out_of_range",
    "n_contradictory",
    "n_all_digits",
    "n_code_alphabet",
    "n_whole",
    "n_fraction",
    "n_whole_unknown",
    "n_positive",
    "n_negative",
    "n_sign_unknown",
)


def _described(
    folder: pathlib.Path, values: "list[str]", name: str = "value",
    declared: "list[str] | None" = None,
) -> contract.Profile:
    """Write a one-column table, describe it, load the description."""
    path = fixtures.write(
        folder, "table.csv", fixtures.single_column_table(name, values)
    )
    table = reading.read_table(str(path))
    document = profile.build_document(
        table, taxonomy.Settings(), declared if declared else []
    )
    target = fixtures.write_profile(folder, "table-profile.json", document)
    return contract.load_profile(str(target))


def _missed(twin: generation.Twin) -> "list[tuple[str, str, str]]":
    """Every exact cell count the twin failed to meet, as it names them."""
    return [
        (note.fact, note.published, note.achieved)
        for note in twin.deviations
        if note.fact in EXACT_COUNTS
    ]


# -- 1. the ceiling a producer description reached --------------------


def _many_sizes() -> "list[str]":
    """A declared column of record numbers with 132 different group sizes.

    The shape round 2 built: enough different sizes that the withdrawn
    depth expression -- three quotas times the number of different
    (size, permission) keys plus two -- comes to 402 against a ceiling
    of 400. Two values of two rows each are written in figures alone and
    everything else carries a full stop, which the code alphabet does
    not hold, so the published figures-only count is four and the only
    packing that meets it is the two doubled groups. A packing offered
    groups largest-first takes the group of three and stops one short.
    """
    values: list[str] = []
    for value, size in (("0011", 2), ("0012", 2), ("K.0003", 3)):
        values = values + [value] * size
    for size in range(5, 135):
        values = values + [f"K.{size:04d}"] * size
    return values


def test_a_producer_description_past_the_old_ceiling_packs_exactly(
    tmp_path: pathlib.Path,
) -> None:
    """Point 1: the description that reached the ceiling now packs exactly.

    Before the repair this wrote five cells in figures alone against a
    published four, five numeric cells against four and 9,037 ordinary
    text cells against 9,038, and named all three. The counts are
    EXACT-OBSERVABLE and the real column's own values are a packing that
    meets them, so a search that stops before finding one loses facts
    rather than bounding a cost.
    """
    loaded = _described(tmp_path, _many_sizes(), "record", ["record"])
    block = loaded.columns[0]
    facts = block.facts
    assert isinstance(facts, contract.IdentifierFacts)
    assert len(facts.n_distinct_by_occurrences) == 132
    assert facts.n_all_digits == 4
    assert facts.n_code_alphabet == 4

    twin = generation.generate(loaded, 0)
    assert _missed(twin) == []


def test_the_exact_packing_finds_what_a_largest_first_rule_misses() -> None:
    """The packing rule's own worked example, on the shipped function.

    Groups of 2, 2 and 3 against a first quota of 4: offering the
    largest group that fits takes the three and then neither two, so the
    quota comes out at three. The exact packing takes the two twos.
    """
    groups = (2, 2, 3)
    quotas = [4, 3]
    allowed = [generation._every_bucket(2) for _each in groups]

    greedy, _left = generation._share_out(groups, quotas, allowed)
    assert sum(
        groups[place] for place in range(3) if greedy[place] == 0
    ) != 4

    exact = generation._allotted(groups, quotas, allowed)
    assert exact is not None
    assert sum(
        groups[place] for place in range(3) if exact[place] == 0
    ) == 4


def test_the_packing_says_no_only_when_there_is_no_packing() -> None:
    """The floor under point 1: None means none exists, not none was found.

    Three groups of two against a quota of three cannot be packed by
    whole groups at all, and that is the only shape of answer the search
    is allowed to refuse with.
    """
    groups = (2, 2, 2)
    allowed = [generation._every_bucket(2) for _each in groups]
    assert generation._allotted(groups, [3, 3], allowed) is None
    assert generation._allotted(groups, [2, 4], allowed) is not None


# -- 2. free text: the class and the alphabet are one question --------


def test_a_free_text_column_meets_its_class_and_alphabet_counts_together(
    tmp_path: pathlib.Path,
) -> None:
    """Point 2: the five-row column round 2 built.

    Three singleton groups that read as numbers and one doubled group
    of ordinary text, with four cells in the code alphabet. Deciding the
    classes first and the alphabets afterwards wrote five code-alphabet
    cells against the published four; one walk over the grid of pairs
    finds the assignment that meets both.
    """
    loaded = _described(tmp_path, ["7", "7", "42", "ab", "x!"])
    block = loaded.columns[0]
    facts = block.facts
    assert isinstance(facts, contract.TextFacts)
    assert block.n_numeric == 3
    assert block.n_not_numeric == 2
    assert facts.n_code_alphabet == 4

    twin = generation.generate(loaded, 0)
    assert _missed(twin) == []


def test_the_joint_walk_is_complete_over_a_producer_battery(
    tmp_path: pathlib.Path,
) -> None:
    """And it is not one lucky shape: a battery of five-row columns.

    Every four-value shape drawn from a neutral pool, with one value
    doubled, put through the producer. For each of them the joint walk's
    answer is checked against an EXHAUSTIVE one: every assignment of
    every group to every permitted pair is tried by hand, and the walk
    must return an answer exactly when one of them meets both margins.
    A completeness claim checked against a second implementation of the
    same walk would prove nothing; checked against exhaustion it proves
    what it says.

    The two margins are then recounted from the walk's own answer, so a
    walk that returned an assignment nobody can recount fails here too.
    """
    pool = ["7", "42", "913", "5.5", "ab", "q_z", "x!", "no!!"]
    reached = 0
    answered = 0
    for step, combination in enumerate(itertools.combinations(pool, 4)):
        for doubled in range(4):
            values: list[str] = []
            for place, value in enumerate(combination):
                values = values + [value] * (2 if place == doubled else 1)
            folder = tmp_path / f"case-{step}-{doubled}"
            folder.mkdir()
            loaded = _described(folder, values)
            block = loaded.columns[0]
            facts = block.facts
            if not isinstance(facts, contract.TextFacts):
                continue
            reached = reached + 1
            classes = [
                block.n_numeric, block.n_out_of_range,
                block.n_contradictory, block.n_not_numeric,
            ]
            alphabets = [
                facts.n_all_digits,
                facts.n_code_alphabet - facts.n_all_digits,
                block.n_present - facts.n_code_alphabet,
            ]
            groups = generation._groups_of(facts.n_distinct_by_occurrences)
            # ONE SHAPE, held still on purpose. WHICH groups carry the
            # published ends is itself part of the allocation now
            # (review item P2-C4-F2, proved in
            # tests/test_p2c4f2_text_shape.py); what this battery
            # checks is the other half -- that for a shape held still
            # the grid walk finds a joint answer exactly when one
            # exists. So it names the ends' carriers rather than
            # letting the search move them.
            held = (0, 1)
            lengths, counts, _notes = generation._text_shape(
                block, facts, groups, held
            )
            permitted = [
                generation._pair_permits(
                    lengths[place], counts[place], place in held
                )
                for place in range(len(groups))
            ]
            joint = generation._joint_allocation(
                groups, classes, alphabets, permitted
            )
            by_hand = _exhaustive(groups, classes, alphabets, permitted)
            assert (joint is not None) == by_hand, (
                f"{values}: the walk said {joint is not None} where "
                f"exhaustion says {by_hand}"
            )
            if joint is not None:
                answered = answered + 1
                _both_margins(groups, joint, classes, alphabets)
    assert reached > 20, "this battery reached too few columns of free text"
    assert answered > 0, "no shape of this battery had a joint answer at all"


def _exhaustive(
    groups: "tuple[int, ...]",
    classes: "list[int]",
    alphabets: "list[int]",
    permitted: "list[int]",
) -> bool:
    """Whether ANY assignment of these groups meets both margins.

    Written by hand and by exhaustion, so that it shares no rule with
    the walk it checks.
    """
    width = len(alphabets)
    cells = len(classes) * width
    for assignment in itertools.product(range(cells), repeat=len(groups)):
        rows = [0 for _each in classes]
        columns = [0 for _each in alphabets]
        allowed = True
        for place in range(len(groups)):
            cell = assignment[place]
            if (permitted[place] >> cell) & 1 == 0:
                allowed = False
                break
            rows[cell // width] = rows[cell // width] + groups[place]
            columns[cell % width] = columns[cell % width] + groups[place]
        if allowed and rows == classes and columns == alphabets:
            return True
    return False


def _both_margins(
    groups: "tuple[int, ...]",
    placed: "list[int]",
    classes: "list[int]",
    alphabets: "list[int]",
) -> None:
    """Every cell quota of both margins, recounted from an assignment."""
    width = len(alphabets)
    rows = [0 for _each in classes]
    columns = [0 for _each in alphabets]
    for place in range(len(groups)):
        rows[placed[place] // width] = (
            rows[placed[place] // width] + groups[place]
        )
        columns[placed[place] % width] = (
            columns[placed[place] % width] + groups[place]
        )
    assert rows == classes
    assert columns == alphabets


# -- 3 and 4. wide columns: the magnitude class and the sign ----------


def _wide_shapes() -> "list[list[str]]":
    """Four-value shapes over a neutral pool, two of them repeated.

    The pool mixes values too large to hold, values too small to hold,
    values the format holds, notation that conflicts with itself and
    ordinary text, so the six magnitude quotas and the three sign quotas
    are all reached.
    """
    huge = "9" * 320
    pool = [
        huge, "-" + huge, "0." + "0" * 320 + "7", "-0." + "0" * 320 + "7",
        "5", "-5", "2.5", "-2.5", "(-5)", "zz",
    ]
    shapes: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    for combination in itertools.combinations(pool, 4):
        for doubled in range(4):
            for third in range(4):
                values: list[str] = []
                for place, value in enumerate(combination):
                    times = 1
                    if place == doubled:
                        times = times + 1
                    if place == third:
                        times = times + 1
                    values = values + [value] * times
                key = tuple(sorted(values))
                if key in seen:
                    continue
                seen.add(key)
                shapes = shapes + [values]
    return shapes


@pytest.fixture(scope="module")
def wide_battery(
    tmp_path_factory: pytest.TempPathFactory,
) -> "list[tuple[contract.Profile, generation.Twin]]":
    """Every shape of the battery that the producer routes to the wide role."""
    folder = tmp_path_factory.mktemp("f1-wide")
    built: list[tuple[contract.Profile, generation.Twin]] = []
    for step, values in enumerate(_wide_shapes()):
        here = folder / f"case-{step}"
        here.mkdir()
        loaded = _described(here, values)
        if loaded.columns[0].role != "numeric_unrepresentable":
            continue
        built = built + [(loaded, generation.generate(loaded, 0))]
    return built


def test_the_wide_battery_reaches_the_role_it_is_built_for(
    wide_battery: "list[tuple[contract.Profile, generation.Twin]]",
) -> None:
    """The vacuity floor: a battery that reached no wide column proves none."""
    assert len(wide_battery) > 100


def test_every_wide_shape_meets_every_published_count(
    wide_battery: "list[tuple[contract.Profile, generation.Twin]]",
) -> None:
    """Points 3 and 4, on producer-emitted descriptions.

    Forty of these shapes lost a sign count before the repair -- writing
    two negative cells and none positive against one of each, and naming
    both -- because the magnitude classes were packed first and the
    signs afterwards. Every one of them now meets both margins, which is
    also the demonstration that the remaining fallback is unreachable
    from a description a real table produced: an exact packing was found
    every time.
    """
    for loaded, twin in wide_battery:
        assert _missed(twin) == [], loaded.columns[0].name


def test_nothing_counts_the_walk_s_trips_and_stops_it(
    tmp_path: pathlib.Path,
    wide_battery: "list[tuple[contract.Profile, generation.Twin]]",
) -> None:
    """Point 4, after the last ceiling was withdrawn.

    This test used to measure the states genuine descriptions enter and
    hold the largest of them to a hundredth of a 200,000 ceiling. Review
    item P2-C3-F1 built a producer description that needs more than that
    ceiling, so the headroom the measurement rested on was never there
    and the ceiling is gone: `_ALLOCATION_STATES` no longer exists and
    the walk takes nothing that counts its trips. The measurement stays
    because it is still worth knowing what genuine descriptions spend --
    every shape of the wide battery, the 132-size declared column that
    reached the first withdrawn ceiling, the free-text shapes and the
    whole shared table -- and the guard that a ceiling cannot come back
    is in `tests/test_p2c3f1_published_margins.py`, where a producer
    description walks past the withdrawn number and still answers.
    """
    assert not hasattr(generation, "_ALLOCATION_STATES")
    worst = [0]
    room = generation._cell_room

    def counted(*given):  # type: ignore[no-untyped-def]
        worst[0] = worst[0] + 1
        return room(*given)

    generation._cell_room = counted  # type: ignore[assignment]
    try:
        shared = tmp_path / "shared"
        shared.mkdir()
        path = fixtures.write(
            shared, "table.csv", fixtures.every_role_table()
        )
        table = reading.read_table(str(path))
        document = profile.build_document(
            table, taxonomy.Settings(), ["record_code"]
        )
        target = fixtures.write_profile(shared, "table-profile.json", document)
        generation.generate(contract.load_profile(str(target)), 20260811)

        folder = tmp_path / "many-sizes"
        folder.mkdir()
        generation.generate(
            _described(folder, _many_sizes(), "record", ["record"]), 0
        )

        for step, values in enumerate(
            (["7", "7", "42", "ab", "x!"], ["7", "42", "5.5", "ab", "ab"])
        ):
            here = tmp_path / f"text-{step}"
            here.mkdir()
            generation.generate(_described(here, values), 0)

        for loaded, _twin in wide_battery:
            generation.generate(loaded, 0)
    finally:
        generation._cell_room = room  # type: ignore[assignment]

    assert worst[0] > 0, "nothing was packed, so nothing was measured"


def test_a_sign_a_wide_cell_cannot_carry_is_not_offered_to_it() -> None:
    """The permission the grid carries, stated as its own assertion.

    Notation that conflicts with itself and ordinary text settle no
    sign, so those two magnitude classes answer only for the unknown
    count; every other class carries a sign of its own.
    """
    assert generation._sign_permits(0) == 0b100
    assert generation._sign_permits(5) == 0b100
    for kind in (1, 2, 3, 4):
        assert generation._sign_permits(kind) == 0b011
