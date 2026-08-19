"""V4.2's comparison, built: the two corner classifiers, side by side.

REVIEW ITEMS P3-V7-F2, F3 AND F4 AND P3-V8-F3 AND F4, AND THE CLASS
THEY ALL BELONG TO.
Specification V4.2 says the corner classifier is written from the
validation method and compared against the generator's own in the suite,
where both may be imported. Round 6 discovered that no test had ever
done that and narrowed V4.2's claim to what ran -- one corner, one
direction. Round 7 then found three more divergences of one shape: the
validator's independent arithmetic disagrees with the generator's, and
the validator rejects or mis-classifies files THE SHIPPED GENERATOR
ITSELF WRITES.

Patching those one at a time is what failed: round 6's repair of the
identifier corner introduced two of them. So this file builds the
comparison V4.2 asks for and lets it find them, over EVERY corner the
validator classifies:

- `identifier-infeasible`, over all three alphabet bands, both
  whole-number readings and the family boundaries taken from both sides;
- `datetime-offsets-withheld`, over published, absent and withheld
  offset maps;
- `label-variants-short`, over withheld variants with multiplicity and
  levels the floor held back whole;
- `numeric-spellings-short`, over per-(value, style) groups, forced
  integers, floored style maps and the pooled `(withheld)` key.

THE FOUR THINGS IT ASSERTS, and why each is needed:

1. **The generator's own twin is not rejected.** For every description
   the space builds, the shipped generator writes a twin, the shipped
   validator measures it, and no corner-governed fact may be MISSED
   where the generation report's own account says the twin holds it.
   This is what catches a classifier that under-claims: a corner the
   generator needs and the classifier withholds.
2. **A corner is claimed only where the generator falls short.** The
   other direction, which a green suite is silent about: a corner
   claimed where none is needed removes or widens a check while the
   twin passes either way. That silence is how a false identifier
   corner lived under four green review rounds.
3. **The two capacity arithmetics agree, family by family.** The
   identifier corner's supply is method G9.4's FAMILY capacity, and the
   shipped generator's own family map is walked here and counted, so a
   validator counting a domain no family writes from is red -- at every
   band, every length the walk can be counted at, and both whole-number
   readings.
4. **No distinctness bar admits every count.** V3.4 forbids a subcheck
   that cannot fail and V3.5 decides it per entry. Where the corner's
   envelope is printed as a check, some file has to be able to miss it;
   where it would license every count a column of that description can
   hold, the entry is a LISTING instead.

A FIFTH THING IT FOUND, which is not a corner at all and is asserted
here because this comparison is what found it: a numeric column whose
style map the publication floor has partly pooled owes a named form AT
LEAST its published count and at most that count plus the pool, and the
exact bar refused the shipped generator's own twin on every such
description. A withheld ENDPOINT offset is the same shape and is a
listing now.

WHAT THIS DOES NOT REACH, said at its real width. Assertion 1 compares
the validator's verdict against the GENERATION REPORT's account of the
same fact, so it is only as strong as that report is honest: a fact the
generator neither meets nor mentions is invisible to it -- though a fact
that report is SILENT about is no longer skipped, because silence there
means the generator pinned it and assertion 2 now asks whether this
validator pinned it too (review item P3-V8-F3). Assertion 3 walks each
family's own index map, which is affordable at one and two characters
and truncated above that, so the three-character families are compared
at their published arithmetic and not by enumeration. And on a column of
NUMBERS the two envelopes are compared by containment rather than
equality. That containment is narrower than it was -- every class but
the numbers class is now settled exactly at both ends -- and what
remains open is one thing and is measured rather than described: how
many different VALUES the plain cells carry is decided by a construction
this module may not import, so a file one value short of a pinned count
is an AUTHORIZED DEVIATION here and `test_the_class_witness_gets_g12_8s
_second_summand` asserts exactly that (plan amendment A-P3-20 clause 3).

THE RED CHECK. Eight `REINSTATE` values put one piece of the pre-repair
behaviour back, so every guarantee here has a demonstrated red:

* `P3-V7-F2` -- the identifier supply above one character as it stood,
  counting every string the positional rules leave rather than the
  families that write them;
* `P3-V7-F2-bands` -- the summed reach alone, without the per-band
  question of whether a band can cover its own cells;
* `P3-V7-F3` -- a withheld-variant count read as row coverage instead
  of `key x count`;
* `P3-V7-F4` -- the numeric supply aggregated by style key, with the
  pooled `(withheld)` cells counted as leading-zero cells, and the
  corner asked in the short direction only;
* `P3-V7-F4-vacuity` -- the spelling envelope kept as a check where it
  licenses every count a file of that length can hold;
* `P3-V7-styles` -- a named style count compared exactly against a
  description whose style map the floor has pooled;
* `P3-V8-F3` -- the corner asked without the field, so G12.7's raw-only
  authorization lands on a folded count as well;
* `P3-V8-F4` -- G12.8's supply written with its first summand alone, and
  its ceiling counting the other classes' CELLS instead of their shares.

Every table is built at test time by seeded neutral builders; no
data-format file enters the repository (plan D13).
"""

import os
import pathlib
import random
import typing

import pytest

import fixtures
from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

SEED = 20260814
NAME = "col"


# -- the pre-repair arithmetic, kept only for the red check -------------


def _the_alphabet_ceiling(
    band: str, length: int, whole: bool, numbers: bool = True
) -> int:
    """The identifier supply as it stood: an alphabet, not a family.

    The whole-number branch is written out rather than delegated,
    because the name this stands in for is the one being replaced.
    """
    if not whole:
        return validation._capacity_at(band, length)
    ten = validation._DIGIT_SIZE
    if band == validation._BAND_DIGITS:
        return (ten - 1) * validation._to_the_power(ten, length - 1)
    if band == validation._BAND_CODE:
        if length == 2:
            return ten
        if length < 2:
            return 0
        return validation._to_the_power(ten, length - 2)
    if length < 2:
        return 0
    return validation._to_the_power(ten, length - 1)


def _the_supply_as_it_stood(
    column: contract.ColumnBlock,
    facts: contract.ColumnFacts,
    published: int,
) -> "int | None":
    """`_spelling_supply` before round 7: two readings, both too high.

    The classes G12.8's second summand counts are left out here as they
    were left out then, so this stand-in reinstates round 8's defect
    along with round 7's; `P3-V8-F4` below puts back that summand alone.
    """
    if isinstance(facts, contract.LabelFacts):
        supply = 0
        for level in facts.levels:
            named = 0
            for spelling in level.variants:
                supply = supply + 1
                named = named + level.variants[spelling]
            for spelling in level.variants_withheld:
                supply = supply + level.variants_withheld[spelling]
                named = named + level.variants_withheld[spelling]
            if named < level.count:
                supply = supply + 1
        return supply + facts.suppressed_levels
    if isinstance(facts, contract.NumericFacts):
        supply = 0
        for style in facts.numeric_styles:
            if style == parsing.STYLE_PLAIN:
                supply = supply + 1
            else:
                supply = supply + facts.numeric_styles[style]
        return supply
    return None


def _short_in_one_direction_only(
    column: contract.ColumnBlock, facts: contract.NumericFacts
) -> bool:
    """The numeric corner asked as it was: only where supply falls short."""
    supply = validation._spelling_supply(column, facts, column.n_distinct)
    if supply is None:
        return False
    if supply < column.n_distinct:
        return True
    return supply < column.n_distinct_folded


@pytest.fixture(scope="module", autouse=True)
def _reinstated() -> "typing.Iterator[None]":
    """Put one piece of the pre-repair behaviour back on request.

    MODULE-SCOPED ON PURPOSE. The comparison this file makes runs the
    whole producer/generator/validator chain once per description in a
    module-scoped fixture, and pytest builds a module-scoped fixture
    BEFORE any function-scoped one -- so a reinstatement written as the
    ordinary `monkeypatch` fixture would be applied after the runs it
    was meant to change, and the red check would be a green run with a
    patch nobody used.
    """
    monkeypatch = pytest.MonkeyPatch()
    asked = os.environ.get("REINSTATE")
    if asked == "P3-V7-F2":
        monkeypatch.setattr(
            validation, "_identifier_capacity_at", _the_alphabet_ceiling
        )
    if asked == "P3-V7-F2-bands":
        monkeypatch.setattr(
            validation,
            "_band_falls_short",
            lambda _cells, _widest, _room: False,
        )
    if asked in ("P3-V7-F3", "P3-V7-F4"):
        monkeypatch.setattr(
            validation, "_spelling_supply", _the_supply_as_it_stood
        )
    if asked == "P3-V7-F4":
        monkeypatch.setattr(
            validation,
            "_numeric_spellings_are_short",
            _short_in_one_direction_only,
        )
    if asked == "P3-V7-F4-vacuity":
        monkeypatch.setattr(
            validation,
            "_envelope_admits_every_count",
            lambda _column, _facts, _published: False,
        )
    if asked == "P3-V7-styles":
        monkeypatch.setattr(
            validation, "_floor_governed", _the_exact_bar_on_a_pooled_map
        )
    if asked == "P3-V8-F3":
        monkeypatch.setattr(
            validation, "_distinct_corner", _the_corner_asked_without_a_field
        )
    if asked == "P3-V8-F4":
        monkeypatch.setattr(
            validation, "_spelling_supply", _the_supply_without_its_classes
        )
        monkeypatch.setattr(
            validation,
            "_spelling_ceiling",
            _the_ceiling_counting_cells_not_shares,
        )
    yield
    monkeypatch.undo()


# Round 8's three, kept for the same reason as round 7's above.

_THE_CORNER = validation._distinct_corner
_THE_SUPPLY = validation._spelling_supply
_THE_CEILING = validation._spelling_ceiling


def _the_corner_asked_without_a_field(
    facts: contract.ColumnFacts, mine: "tuple[str, ...]", field: str
) -> str:
    """`_distinct_corner` as it stood: one answer for both counts.

    The raw question asked of the folded fact too, which is how G12.7's
    raw-only authorization came to sit on a folded count (review item
    P3-V8-F3).
    """
    return _THE_CORNER(facts, mine, validation._RAW_DISTINCT)


def _the_supply_without_its_classes(
    column: contract.ColumnBlock,
    facts: contract.ColumnFacts,
    published: int,
) -> "int | None":
    """G12.8's first summand alone, which is where the floor stood.

    The formula has two, and the second -- `min(cells, budget share)`
    for every class that is not the numbers class -- was never written
    (review item P3-V8-F4).
    """
    if not isinstance(facts, contract.NumericFacts):
        return _THE_SUPPLY(column, facts, published)
    supply = 0
    pooled = 0
    for style in facts.numeric_styles:
        if style in (parsing.STYLE_PLAIN, taxonomy.SUPPRESSED_LABEL):
            pooled = pooled + facts.numeric_styles[style]
        else:
            supply = supply + facts.numeric_styles[style]
    if pooled > 0:
        supply = supply + 1
    return supply


def _the_ceiling_counting_cells_not_shares(
    column: contract.ColumnBlock,
    facts: contract.ColumnFacts,
    published: int,
) -> "int | None":
    """The high end as it stood: every cell outside the numbers class.

    The comment beside it already said "their own share of the G6.5
    budget"; the arithmetic added their CELL COUNT, which is the same
    number only where the budget reaches every one of them.
    """
    if not isinstance(facts, contract.NumericFacts):
        return _THE_CEILING(column, facts, published)
    plain = 0
    others = 0
    for style in facts.numeric_styles:
        if style == parsing.STYLE_PLAIN:
            plain = plain + facts.numeric_styles[style]
        else:
            others = others + facts.numeric_styles[style]
    room = others + min(plain, column.n_distinct)
    return room + max(column.n_present - plain - others, 0)


def _the_exact_bar_on_a_pooled_map(
    name: str,
    fact: str,
    subcheck: str,
    published: int,
    measured: "dict[str, int] | None",
    key: str,
    floor: int,
    pooled: int = 0,
) -> validation.Check:
    """The named style count compared exactly, pooled cells and all."""
    return _AS_IT_STOOD(
        name, fact, subcheck, published, measured, key, floor, 0
    )


_AS_IT_STOOD = validation._floor_governed


# -- the neutral builders the space is written from --------------------


def _wide_singles(count: int) -> "list[str]":
    """``count`` different one-character values no code alphabet holds."""
    return [chr(0x100 + 2 * index) for index in range(count)]


def _letters() -> "list[str]":
    """The fifty-two one-character values with a case."""
    upper = [chr(code) for code in range(ord("A"), ord("Z") + 1)]
    lower = [chr(code) for code in range(ord("a"), ord("z") + 1)]
    return upper + lower


def _figures(low: int, high: int) -> "list[str]":
    """The whole numbers from ``low`` to ``high``, written in figures."""
    return [f"{number}" for number in range(low, high + 1)]


def _two_character_wide(count: int) -> "list[str]":
    """``count`` two-character values outside the code alphabet.

    None of them reads as a number, so the description gives the numbers
    class no cell and the widest band's ordinary-text family is the only
    one that can answer it. The head family is walked first and the
    code-led spellings after it, which is more values than any family
    holds and lets the boundary be taken from both sides.
    """
    printable = [chr(code) for code in range(33, 127)]
    heads = [
        letter
        for letter in printable
        if not parsing.is_code_text(letter) and letter not in "=+-@"
    ]
    coded = [
        letter
        for letter in printable
        if parsing.is_code_text(letter) and letter not in "=+-@"
    ]
    built: list[str] = []
    seen: dict[str, int] = {}
    for first, rest in [
        (one, two) for one in heads for two in printable
    ] + [(one, two) for one in coded for two in heads]:
        made = f"{first}{rest}"
        if made in seen or made.strip() != made:
            continue
        if parsing.classify_number(made) != parsing.NOT_A_NUMBER:
            continue
        if parsing.is_missing_text(made):
            continue
        seen[made] = 1
        built = built + [made]
        if len(built) >= count:
            return built
    return built


def _repeated(values: "list[str]", times: int) -> "list[str]":
    """Every value of ``values``, ``times`` rows each."""
    built: list[str] = []
    for value in values:
        for _step in range(times):
            built = built + [value]
    return built


# -- the description space, built by the real producer -----------------


class Entry(typing.NamedTuple):
    """One column of the space, before the producer has seen it.

    ``parse_rate`` is the producer's own `minimum_parse_rate`, which
    every entry but one leaves at the shipped default. The one that
    lowers it is round 8's witness: a numeric column needs cells that
    are NOT numbers standing beside its numbers before G12.8's second
    summand has anything to add, and the default line puts such a column
    in the free-text role instead (review item P3-V8-F4).
    """

    stem: str
    values: "tuple[str, ...]"
    declared: bool
    floor: int
    parse_rate: float = taxonomy.Settings().minimum_parse_rate


def _identifier_entries(rng: random.Random, how_many: int) -> "list[Entry]":
    """Random declared record-number columns over all three bands."""
    codes = tuple(
        "-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz"
    )
    wides = _wide_singles(25)
    printable = tuple(chr(code) for code in range(33, 127))
    built: list[Entry] = []
    for index in range(how_many):
        width = rng.choice([1, 1, 2, 2, 3])
        kind = rng.choice(["digits", "code", "wide", "mixed", "whole"])
        wanted = rng.randint(2, 30)
        pool: list[str] = []
        seen: dict[str, int] = {}
        for _step in range(4000):
            if len(pool) >= wanted:
                break
            length = rng.randint(1, width)
            if kind == "digits":
                made = "".join(
                    rng.choice("0123456789") for _place in range(length)
                )
            elif kind == "whole":
                made = f"{rng.randint(1, 10 ** width - 1)}"
            elif kind == "code":
                made = rng.choice(_letters()) + "".join(
                    rng.choice(codes) for _place in range(length - 1)
                )
            elif kind == "wide":
                made = rng.choice(wides) + "".join(
                    rng.choice(printable) for _place in range(length - 1)
                )
            else:
                made = "".join(
                    rng.choice(codes + tuple(wides))
                    for _place in range(length)
                )
            if made in seen or made.strip() != made or not made:
                continue
            if parsing.is_missing_text(made):
                continue
            seen[made] = 1
            pool = pool + [made]
        values: list[str] = []
        for value in pool:
            values = values + [value] * rng.choice([1, 1, 1, 2, 3])
        rng.shuffle(values)
        built = built + [
            Entry(f"id-{index}", tuple(values), True, 11)
        ]
    return built


_LABEL_WORDS = ("alpha", "beta", "gamma", "delta", "epsilon")


def _label_entries(rng: random.Random, how_many: int) -> "list[Entry]":
    """Random label columns, at both publication floors."""
    built: list[Entry] = []
    for index in range(how_many):
        values: list[str] = []
        for place in range(rng.randint(2, 5)):
            word = _LABEL_WORDS[place]
            for spot in range(rng.randint(1, 3)):
                spelling = word
                if spot == 1:
                    spelling = word.capitalize()
                if spot == 2:
                    spelling = word.upper()
                values = values + [spelling] * rng.randint(1, 14)
        rng.shuffle(values)
        built = built + [
            Entry(
                f"label-{index}",
                tuple(values),
                False,
                rng.choice([11, 11, 1]),
            )
        ]
    return built


def _numeric_entries(rng: random.Random, how_many: int) -> "list[Entry]":
    """Random numeric columns over the styles owner decisions 7 and 8 permit."""
    built: list[Entry] = []
    for index in range(how_many):
        values: list[str] = []
        shape = rng.choice(["plain", "mixed", "forced", "spelled"])
        for _step in range(rng.randint(20, 55)):
            number = rng.randint(0, 40)
            if shape == "plain":
                values = values + [f"{number}"]
            elif shape == "forced":
                values = values + [f"{rng.randint(1, 200)}"]
            elif shape == "spelled":
                values = values + [
                    rng.choice(
                        [
                            f"{number}",
                            f"{number}e0",
                            f"{number}E0",
                            f"0{number}",
                            f"{number}.0",
                            f"+{number}",
                        ]
                    )
                ]
            else:
                values = values + [
                    rng.choice([f"{number}", f"0{number}", f"{number}.0"])
                ]
        built = built + [
            Entry(f"number-{index}", tuple(values), False, rng.choice([11, 1]))
        ]
    return built


def _datetime_entries(rng: random.Random, how_many: int) -> "list[Entry]":
    """Random datetime columns: no offset, one offset, many, withheld."""
    built: list[Entry] = []
    for index in range(how_many):
        values: list[str] = []
        shape = rng.choice(["bare", "spread", "one", "few"])
        for step in range(rng.randint(12, 36)):
            stamp = f"2024-{1 + step % 12:02d}-{1 + step % 27:02d}"
            if shape == "spread":
                stamp = f"{stamp}T00:00:00+0{step % 6}:00"
            elif shape == "one":
                stamp = f"{stamp}T0{step % 9}:00:00Z"
            elif shape == "few":
                stamp = f"{stamp}T00:00:00+0{step % 2}:00"
            values = values + [stamp]
        built = built + [
            Entry(f"stamp-{index}", tuple(values), False, rng.choice([11, 1]))
        ]
    return built


# THE NAMED WITNESSES. Each is one review finding, written out so that
# the space cannot drift off the case that produced it.
def _named_entries() -> "list[Entry]":
    """The review items' own columns, and the boundaries beside them."""
    withheld = (
        ["alpha"] * 6 + ["Alpha"] * 6 + ["beta"] * 5 + ["Beta"] * 5
    )
    floored = (
        ["13"] * 10
        + ["10e0"]
        + ["2E0"] * 7
        + ["7.0"] * 6
        + ["11"] * 8
        + ["27e0"] * 6
        + ["02"] * 15
        + ["18e0"] * 2
        + ["0"] * 13
    )
    wide = _wide_singles(26)
    return [
        # P3-V7-F3: two withheld variants covering six rows each.
        Entry("witness-label-withheld", tuple(withheld), False, 11),
        # P3-V7-F4, the first half: a floored style map whose own
        # leading-zero cells force more identities than are published.
        Entry("witness-number-floored", tuple(floored), False, 11),
        # P3-V7-F4, the second half: forced integers, one style, and a
        # bar that would reach from one value to every value.
        Entry(
            "witness-number-forced",
            tuple(f"{number}" for number in range(1, 201)),
            False,
            11,
        ),
        # P3-V7-F2, the second half: fifty-one cells outside the code
        # alphabet in groups of two rows, short by exactly one spelling
        # while the summed reach reads twenty-eight against twenty-eight.
        Entry(
            "witness-identifier-bands",
            tuple(
                ["7", "7", "a", wide[0]]
                + _repeated(wide[1:], 2)
            ),
            True,
            11,
        ),
        # The one-character boundaries, taken from both sides.
        Entry(
            "boundary-wide-25", tuple(_wide_singles(25)), True, 11
        ),
        Entry(
            "boundary-wide-26", tuple(_wide_singles(26)), True, 11
        ),
        Entry(
            "boundary-figures-9", tuple(_figures(1, 9)), True, 11
        ),
        Entry(
            "boundary-figures-10", tuple(_figures(0, 9)), True, 11
        ),
        Entry(
            "boundary-code-53", tuple(_letters() + ["_"]), True, 11
        ),
        # P3-V8-F4: twenty whole numbers written one way, beside two
        # cells that are not numbers at all. G12.8's second summand --
        # the classes -- settles two of the twenty-two spellings this
        # description publishes, and the version that never wrote that
        # summand read a floor of ONE, which made both distinctness
        # entries bars that could not fail.
        Entry(
            "witness-number-classes",
            tuple(
                [f"{number}" for number in range(0, 2000, 100)]
                + ["alpha", "beta"]
            ),
            False,
            11,
            0.8,
        ),
    ]


def _space() -> "list[Entry]":
    """Every description this file compares the two classifiers over."""
    rng = random.Random(20260815)
    built = _identifier_entries(rng, 90)
    built = built + _label_entries(rng, 45)
    built = built + _numeric_entries(rng, 45)
    built = built + _datetime_entries(rng, 30)
    return built + _named_entries()


# -- one whole run, as the three commands build one --------------------


class Probe(typing.NamedTuple):
    """One description, its twin, and both accounts of that twin."""

    stem: str
    described: contract.Profile
    column: contract.ColumnBlock
    twin: generation.Twin
    outcome: validation.Outcome
    corners: "tuple[str, ...]"
    told: "dict[str, str]"


def _describe(
    folder: pathlib.Path, entry: Entry
) -> contract.Profile:
    """One column, through the real producer and the strict loader."""
    table = fixtures.write(
        folder,
        f"{entry.stem}.csv",
        fixtures.single_column_table(NAME, list(entry.values)),
    )
    read = reading.read_table(str(table))
    document = profile.build_document(
        read,
        taxonomy.Settings(
            small_cell_floor=entry.floor,
            minimum_parse_rate=entry.parse_rate,
        ),
        [NAME] if entry.declared else [],
    )
    written = fixtures.write_profile(
        folder, f"{entry.stem}-profile.json", document
    )
    return contract.load_profile(str(written))


def _account(twin: generation.Twin) -> "dict[str, str]":
    """What the generation report says about each fact of the twin.

    An APPROXIMATION OVERRIDES A DEVIATION and that order is the whole
    point: the generator files both for a fact it could not meet exactly
    but whose authorized envelope its own cells landed inside, and such
    a twin is CONFORMING. Reading the deviation alone would let every
    authorized outcome pass for a shortfall and this comparison would
    assert nothing.
    """
    told: dict[str, str] = {}
    for deviation in twin.deviations:
        told[deviation.fact] = "not-held"
    for approximation in twin.approximations:
        told[approximation.fact] = (
            "held" if approximation.inside else "not-held"
        )
    return told


# What each corner governs: the validator's subcheck against the fact
# the generation report files under.
GOVERNED = {
    "distinct.n_distinct": "n_distinct",
    "distinct.n_distinct_folded": "n_distinct_folded",
    "distinct.n_distinct_by_occurrences": "n_distinct_by_occurrences",
    "offsets.map": "utc_offsets",
    "offsets.earliest": "earliest_utc_offset",
    "offsets.latest": "latest_utc_offset",
    "offsets.read-at": "datetimes_read_at",
}


@pytest.fixture(scope="module")
def parity(
    tmp_path_factory: pytest.TempPathFactory,
) -> "tuple[Probe, ...]":
    """Every description of the space, described, built and measured."""
    folder = tmp_path_factory.mktemp("corner-parity")
    built: list[Probe] = []
    for entry in _space():
        described = _describe(folder, entry)
        if validation.refusal_of(described):
            # A description no twin exists for is V4.3's business and
            # never a corner; it is not compared here.
            continue
        twin = generation.generate(described, SEED)
        measured = fixtures.write(
            folder, f"{entry.stem}-twin.csv", rendering.twin_csv(twin)
        )
        outcome = validation.measure(described, str(measured))
        column = described.columns[0]
        built = built + [
            Probe(
                entry.stem,
                described,
                column,
                twin,
                outcome,
                validation.corners_of(described).get(column.name, ()),
                _account(twin),
            )
        ]
    return tuple(built)


# -- 1. the generator's own twin is not rejected -----------------------


def test_no_corner_governed_fact_is_missed_on_the_generators_own_twin(
    parity: "tuple[Probe, ...]",
) -> None:
    """V4.2's green direction, over every corner instead of one.

    The shipped generator writes a twin for each description and files
    its own account of every fact it could not meet exactly. Where that
    account says the twin HOLDS a fact -- exactly, or inside the
    envelope the ratified plan authorizes -- the validator may not
    report that same fact MISSED against that same file. A classifier
    that agrees with the generator's own classifier and disagrees with
    its output is still wrong, and this asks the output.
    """
    complaints: list[str] = []
    for probe in parity:
        for check in probe.outcome.checks:
            if check.subcheck not in GOVERNED:
                continue
            if check.verdict != validation.MISSED:
                continue
            if probe.told.get(GOVERNED[check.subcheck], "held") != "held":
                continue
            complaints = complaints + [
                (
                    f"{probe.stem}: {check.subcheck} reported MISSED "
                    f"(published {check.published}, achieved "
                    f"{check.achieved}) on the shipped generator's own "
                    f"twin, whose own report says that fact is held. "
                    f"Corners claimed: {probe.corners or 'none'}"
                )
            ]
    assert not complaints, "\n  ".join([""] + complaints)


# -- 2. a corner is claimed only where the generator falls short -------


def _generator_envelope(
    twin: generation.Twin, fact: str
) -> "tuple[int, int] | None":
    """The two ends of the bound the generation report printed for a fact.

    The report measures every APPROXIMATED fact on the finished cells
    against the envelope method G12 fixes for it, and prints both ends,
    so the generator's own answer to "what does this description pin?"
    is readable without importing its planner: a bound whose two ends
    MEET is a description the construction reads as exact.
    """
    for approximation in twin.approximations:
        if approximation.fact != fact:
            continue
        return (
            int(approximation.lowest),
            int(approximation.highest),
        )
    return None


def test_where_no_corner_is_claimed_the_generator_pins_the_count_too(
    parity: "tuple[Probe, ...]",
) -> None:
    """The classifier-level reverse direction, at the envelope's own ends.

    Where this classifier claims NO corner it puts the EXACT bar on the
    two distinctness counts, so it is saying the description pins them.
    The generator says the same thing in its own report, in the only
    words it has for it: the two ends of the bound it prints for that
    fact MEET, on the published count. Where they do not, the generator
    is authorized to write something else and the exact bar is a bar the
    product's own output can fail -- which is exactly what P3-V7-F3 and
    P3-V7-F4 were.
    """
    complaints: list[str] = []
    counted = 0
    for probe in parity:
        facts = probe.column.facts
        if not isinstance(
            facts, (contract.LabelFacts, contract.NumericFacts)
        ):
            continue
        if probe.corners:
            continue
        counted = counted + 1
        for field, published in (
            ("n_distinct", probe.column.n_distinct),
            ("n_distinct_folded", probe.column.n_distinct_folded),
        ):
            ends = _generator_envelope(probe.twin, field)
            if ends is None or ends == (published, published):
                continue
            complaints = complaints + [
                (
                    f"{probe.stem}: the classifier puts the exact bar on "
                    f"{field} at {published} while the generation report "
                    f"prints the bound {ends} for it, so the shipped "
                    f"generator may write a count that bar refuses"
                )
            ]
    assert not complaints, "\n  ".join([""] + complaints)
    assert counted >= 20, counted


def test_a_claimed_envelope_holds_every_count_the_generator_authorizes(
    parity: "tuple[Probe, ...]",
) -> None:
    """And where a corner IS claimed, the two envelopes are compared.

    The validator's envelope must HOLD the generator's, end for end: a
    count the generation report authorizes and this report refuses is a
    conforming twin reported MISSED. On a column of labels the two are
    the SAME envelope, because G12.7's `S` is settled by the published
    level blocks alone and both writings compute it; on a column of
    numbers the validator's is wider, and that is the boundary this
    module cannot cross -- how many different VALUES the plain cells
    carry is decided by a construction it may not import.

    AND A FACT THE GENERATION REPORT DOES NOT NAME IS NOT SKIPPED
    (review item P3-V8-F3). The report names every fact its construction
    could not meet exactly, so a corner-governed fact it is SILENT about
    is one the generator PINS -- and this validator has to pin it too.
    Reading silence as "nothing to compare" is what let G12.7's raw-only
    envelope sit on a label column's folded count through four green
    rounds: the generator meets that count exactly, files no
    approximation for it, and the comparison walked straight past the
    entry where the bar had been lowered.
    """
    labels = 0
    numbers = 0
    pinned = 0
    for probe in parity:
        facts = probe.column.facts
        if not probe.corners:
            continue
        if not isinstance(
            facts, (contract.LabelFacts, contract.NumericFacts)
        ):
            continue
        for field, published in (
            ("n_distinct", probe.column.n_distinct),
            ("n_distinct_folded", probe.column.n_distinct_folded),
        ):
            theirs = _generator_envelope(probe.twin, field)
            if theirs is None:
                lowered = validation._distinct_corner(
                    facts, probe.corners, field
                )
                assert not lowered, (
                    f"{probe.stem}/{field}: the generation report names "
                    f"no bound for this fact, so the generator meets it "
                    f"exactly -- and this validator has lowered it to "
                    f"the {lowered} envelope anyway"
                )
                pinned = pinned + 1
                continue
            mine = _mine(probe, published)
            assert mine[0] <= theirs[0] and mine[1] >= theirs[1], (
                f"{probe.stem}/{field}: this report's envelope {mine} "
                f"does not hold the generation report's {theirs}, so a "
                f"twin that report authorizes is refused here"
            )
            if isinstance(facts, contract.LabelFacts):
                labels = labels + 1
                assert mine == theirs, (probe.stem, field, mine, theirs)
            else:
                numbers = numbers + 1
    assert labels >= 4, labels
    assert numbers >= 40, numbers
    assert pinned >= 4, (
        "no corner-governed fact in this space is one the generation "
        "report leaves unnamed, so the rule about its silence is "
        "asserting nothing"
    )


def _mine(probe: Probe, published: int) -> "tuple[int, int]":
    """The two ends this validator draws for one distinctness count."""
    facts = probe.column.facts
    supply = validation._spelling_supply(probe.column, facts, published)
    ceiling = validation._spelling_ceiling(probe.column, facts, published)
    assert supply is not None and ceiling is not None
    return (min(supply, published), max(ceiling, published))


def test_the_space_reaches_every_corner_the_validator_classifies(
    parity: "tuple[Probe, ...]",
) -> None:
    """NOT VACUOUS: the walks above have to have something to walk."""
    seen = {corner for probe in parity for corner in probe.corners}
    assert seen == {
        validation.CORNER_IDENTIFIER_INFEASIBLE,
        validation.CORNER_DATETIME_OFFSETS_WITHHELD,
        validation.CORNER_LABEL_VARIANTS_SHORT,
        validation.CORNER_NUMERIC_SPELLINGS_SHORT,
    }, sorted(seen)


def test_the_identifier_corner_is_claimed_only_where_the_twin_repeats(
    parity: "tuple[Probe, ...]",
) -> None:
    """Owner decision 6's corner takes THREE checks off a column.

    So it is the one a wrong answer costs the most, and the only
    acceptable evidence for it is the shipped generator's own cells: a
    column whose twin holds as many different record numbers as the
    description publishes is a column no corner may be claimed over.
    This is A-P3-14 clause 1's assertion, walked over the wider space
    this file builds.
    """
    claimed = 0
    answered = 0
    for probe in parity:
        if not isinstance(probe.column.facts, contract.IdentifierFacts):
            continue
        held = len({
            cell for cell in probe.twin.columns[0] if cell != ""
        })
        short = held < probe.column.n_distinct
        if validation.CORNER_IDENTIFIER_INFEASIBLE in probe.corners:
            claimed = claimed + 1
            assert short, (
                f"{probe.stem}: the classifier calls this description "
                f"infeasible while the shipped generator wrote all "
                f"{held} of its published record numbers"
            )
            continue
        if not short:
            answered = answered + 1
    assert claimed >= 5, claimed
    assert answered >= 40, answered


def test_the_withheld_offset_corner_is_exactly_the_published_map(
    parity: "tuple[Probe, ...]",
) -> None:
    """The one corner both writings take from the description alone.

    P2-D9's corner is the single `(withheld)` key and nothing else, so
    the two writings can be compared directly rather than through a
    twin -- and they are, at every offset shape the producer publishes:
    no offset at all, one, several, and the withheld pool.
    """
    shapes: dict[str, int] = {}
    for probe in parity:
        facts = probe.column.facts
        if not isinstance(facts, contract.DatetimeFacts):
            continue
        keys = tuple(sorted(facts.utc_offsets))
        shapes["+".join(keys)] = shapes.get("+".join(keys), 0) + 1
        withheld = keys == (taxonomy.SUPPRESSED_LABEL,)
        claimed = (
            validation.CORNER_DATETIME_OFFSETS_WITHHELD in probe.corners
        )
        assert claimed == withheld, (probe.stem, keys, probe.corners)
        listed = sorted(
            listing.subcheck
            for listing in probe.outcome.listings
            if listing.subcheck.startswith("offsets.")
        )
        checked = sorted(
            check.subcheck
            for check in probe.outcome.checks
            if check.subcheck.startswith("offsets.")
        )
        if withheld:
            # The whole map is the withheld key: all four obligations
            # are listings and not one of them is checked.
            assert listed == [
                "offsets.earliest",
                "offsets.latest",
                "offsets.map",
                "offsets.read-at",
            ], (probe.stem, listed)
            assert not checked, (probe.stem, checked)
            continue
        # Otherwise the map is checked key by key, and the only listing
        # this fact can carry is an ENDPOINT the floor held back on its
        # own, which is a different shape from the corner and is
        # asserted against the published field rather than assumed.
        ends = {
            "offsets.earliest": facts.earliest_utc_offset,
            "offsets.latest": facts.latest_utc_offset,
        }
        assert listed == sorted(
            subcheck
            for subcheck in ends
            if ends[subcheck] == taxonomy.SUPPRESSED_LABEL
        ), (probe.stem, listed, ends)
        assert "offsets.read-at" in checked, (probe.stem, checked)
        for subcheck in listed:
            assert subcheck not in checked, (probe.stem, subcheck)
    assert len(shapes) >= 3, shapes
    # NOT VACUOUS: the withheld endpoint has to occur, or the branch
    # above is never taken.
    assert any(
        listing.subcheck in ("offsets.earliest", "offsets.latest")
        for probe in parity
        for listing in probe.outcome.listings
        if validation.CORNER_DATETIME_OFFSETS_WITHHELD not in probe.corners
    )


# -- 3. the two capacity arithmetics agree, family by family -----------

_WALKABLE = 20000


def _families_of(band: str, length: int, whole: bool) -> "dict[str, int]":
    """How many spellings each of the generator's own families writes.

    The shipped family map is WALKED -- index by index, through the
    generator's own `_identifier_at` and the same three rejections its
    walk makes -- so this is the number the construction can actually
    produce and not a second reading of the same formula. A family whose
    index map is larger than `_WALKABLE` is not counted, because
    enumerating it would cost more than the comparison is worth.
    """
    facts = contract.IdentifierFacts(
        min_length=length,
        max_length=length,
        all_whole_numbers=whole,
        n_all_digits=0,
        n_code_alphabet=0,
        n_distinct_by_occurrences={"1": 1},
    )
    found: dict[str, int] = {}
    for kind in generation._CLASSES:
        spellings: dict[str, int] = {}
        for signed in (False, True):
            room = generation._identifier_room(
                kind, band, facts, length, signed
            )
            if room > _WALKABLE:
                return {}
            for index in range(room):
                made = generation._identifier_at(
                    kind, band, facts, length, index, signed
                )
                if made is None or len(made) != length:
                    continue
                if parsing.classify_number(made) != generation._reads_as(
                    kind
                ):
                    continue
                if parsing.is_missing_text(made):
                    continue
                if generation._reads_as_a_date(made):
                    continue
                spellings[made] = 1
        found[kind] = len(spellings)
    return found


def test_every_band_supply_is_the_shipped_families_own_count(
) -> None:
    """V4.2 at the arithmetic, where both writings may be imported.

    The identifier corner's supply is method G9.4's FAMILY capacity: the
    walk `_identifier_at` actually makes, not the alphabet it draws
    from. So the shipped families are walked and counted here, and the
    validator's own number is held to two things at once -- it may never
    fall BELOW what the families write, which would claim a corner over
    a description the generator answers, and it may never stand above
    the families a description's own published class counts leave it,
    which is what reported a conforming twin MISSED.
    """
    walked = 0
    for whole in (False, True):
        for band in (
            validation._BAND_DIGITS,
            validation._BAND_CODE,
            validation._BAND_WIDE,
        ):
            for length in (1, 2):
                families = _families_of(band, length, whole)
                if not families:
                    continue
                walked = walked + 1
                for numbers in (False, True):
                    mine = validation._identifier_capacity_at(
                        band, length, whole, numbers
                    )
                    theirs = families[generation._CLASS_TEXT] + (
                        families[generation._CLASS_NUMBER] if numbers else 0
                    )
                    if whole:
                        # Every value reads as a whole number, so the
                        # ordinary-text family writes no cell of this
                        # column and G9.6's own family is the whole
                        # supply.
                        theirs = families[generation._CLASS_NUMBER]
                    assert mine >= theirs, (
                        f"{band}/{length}/whole={whole}/numbers={numbers}: "
                        f"the validator supplies {mine} where the shipped "
                        f"families write {theirs}, so a description the "
                        f"generator answers can be called a corner"
                    )
                    assert mine <= theirs + _slack(band, length, whole), (
                        f"{band}/{length}/whole={whole}/numbers={numbers}: "
                        f"the validator supplies {mine} against the "
                        f"shipped families' {theirs}, which is a domain "
                        f"no family writes from -- the gap a conforming "
                        f"twin is reported MISSED inside"
                    )
    assert walked >= 8, walked


def _slack(band: str, length: int, whole: bool) -> int:
    """How far above the walked count the published arithmetic may stand.

    G9.4 fixes the capacity as an UPPER bound on what the walk produces
    and says so: the positional rules can put two indices onto one
    spelling and the three rejections of G9.2 remove candidates. So the
    validator's number is allowed to stand above the walked count by the
    candidates those rejections take, and by nothing else. At one
    character the rejections are counted out exactly and the two numbers
    meet; above it the only candidates a walk of these families loses
    are the ones reading as a date or as "no value", which no length can
    hold more than a handful of.
    """
    if length < 2 or whole:
        return 0
    return 16


def test_the_wide_band_boundary_stands_where_the_family_ends(
    tmp_path: pathlib.Path,
) -> None:
    """P3-V7-F2's own witness, taken from both sides.

    The widest band's two-character ordinary-text family holds 2,538
    spellings -- twenty-seven leading characters against ninety-four for
    the second -- while the reading this replaced counted 8,460 of them.
    A producer-derived declared column of 2,538 such values is one the
    families answer and may not be called a corner; one more value is
    one they cannot, and owner decision 6 is what that description is
    owed. No twin is built here: at this width one costs minutes, and
    what the corner turns on is the arithmetic the test above holds to
    the shipped families.
    """
    folder = tmp_path / "wide-two"
    folder.mkdir()
    values = _two_character_wide(2539)
    assert len(values) == 2539
    for count, corner in ((2538, False), (2539, True)):
        entry = Entry(f"wide-{count}", tuple(values[:count]), True, 11)
        described = _describe(folder, entry)
        column = described.columns[0]
        facts = column.facts
        assert isinstance(facts, contract.IdentifierFacts)
        assert (facts.min_length, facts.max_length) == (1 + 1, 2)
        assert column.n_distinct == count
        assert column.n_numeric == 0
        assert facts.n_code_alphabet == 0
        assert validation.refusal_of(described) == ""
        claimed = validation.CORNER_IDENTIFIER_INFEASIBLE in (
            validation.corners_of(described).get(NAME, ())
        )
        assert claimed == corner, (count, corner)


# -- 4. no distinctness bar admits every count -------------------------


def test_every_distinctness_bar_this_space_prints_can_be_missed(
    parity: "tuple[Probe, ...]",
    tmp_path: pathlib.Path,
) -> None:
    """V3.4 and V3.5 on the two counts a spelling corner governs.

    Where a distinctness count is filed as a CHECK, some file has to be
    able to miss it, and the file is BUILT rather than argued: one that
    collapses the column onto a single repeated value, and one that
    gives every present cell its own. A bar that refuses neither refuses
    nothing a column of that description can hold, and the entry belongs
    in the not-checkable census with the sentence that says why.

    BOTH COUNTS, WHICH IS ROUND 8'S CORRECTION (review item P3-V8-F3).
    This asked the question of the raw count alone, so a folded bar the
    description does not authorize -- one lowered onto it by a corner
    written for raw distinctness -- was never put to a file that ought
    to miss it, and the registered red case stayed green while the hole
    stood open beside it.
    """
    folder = tmp_path / "teeth"
    folder.mkdir()
    toothless: list[str] = []
    checked = 0
    for probe in parity:
        cells = list(probe.twin.columns[0])
        flat = [cells[0] if cell != "" else "" for cell in cells]
        wide = [
            f"{place}" if cell != "" else ""
            for place, cell in enumerate(cells)
        ]
        for field, published in (
            ("n_distinct", probe.column.n_distinct),
            ("n_distinct_folded", probe.column.n_distinct_folded),
        ):
            subcheck = f"distinct.{field}"
            if not _files(probe.outcome, subcheck):
                continue
            checked = checked + 1
            refused = False
            for tag, made in (("flat", flat), ("wide", wide)):
                path = fixtures.write(
                    folder,
                    f"{probe.stem}-{field}-{tag}.csv",
                    fixtures.single_column_table(NAME, made),
                )
                outcome = validation.measure(probe.described, str(path))
                if validation.MISSED in _verdicts(outcome, subcheck):
                    refused = True
                    break
            if not refused:
                toothless = toothless + [
                    (
                        f"{probe.stem}: {subcheck} is filed as a "
                        f"check and neither a collapsed column nor an "
                        f"all-different one can miss it (published "
                        f"{published}, present "
                        f"{probe.column.n_present}, corners "
                        f"{probe.corners or 'none'})"
                    )
                ]
    assert not toothless, "\n  ".join([""] + toothless)
    assert checked >= 200, checked


def test_a_bar_that_admits_every_count_is_a_listing_and_not_a_check(
    parity: "tuple[Probe, ...]",
) -> None:
    """The other half of the same rule, asserted where it bites.

    The forced-integer witness publishes two hundred present cells, two
    hundred different values and one style, so its supply is one
    spelling and the envelope G12.8 authorizes runs from one value to
    two hundred. Every count a file of that length can hold is inside
    it. So the entry is a listing carrying the plan passage that
    authorizes the lesser outcome, the census counts it where it counts
    an obligation nothing settles, and no verdict pretends to have been
    passed.
    """
    found = [
        probe for probe in parity
        if probe.stem == "witness-number-forced"
    ]
    assert len(found) == 1
    probe = found[0]
    facts = probe.column.facts
    assert isinstance(facts, contract.NumericFacts)
    assert probe.column.n_present == 200
    assert probe.column.n_distinct == 200
    assert dict(facts.numeric_styles) == {parsing.STYLE_PLAIN: 200}
    assert validation._spelling_supply(
        probe.column, facts, probe.column.n_distinct
    ) == 1
    assert probe.corners == (validation.CORNER_NUMERIC_SPELLINGS_SHORT,)
    for field in ("n_distinct", "n_distinct_folded"):
        assert not _files(probe.outcome, f"distinct.{field}"), field
        listed = [
            listing
            for listing in probe.outcome.listings
            if listing.subcheck == f"distinct.{field}"
        ]
        assert len(listed) == 1, field
        assert "would prove nothing" in listed[0].reason
    # ...and the twin the generator wrote is neither passed nor failed
    # on it: nothing here reports a miss against the product's own file.
    assert probe.outcome.census.missed == 0


# -- the two supplies, compared directly where both are computable -----


def test_the_label_supply_is_the_generators_own_arithmetic(
    parity: "tuple[Probe, ...]",
) -> None:
    """G12.7's `S`, written twice and compared where both may be imported.

    This is the one spelling supply both sides compute from the
    description alone, so the comparison needs no twin at all: the
    validator's number must be the generator's, level by level, over
    published variants, withheld variants with multiplicity, levels the
    variants do not cover and levels the floor held back whole.
    """
    compared = 0
    withheld = 0
    for probe in parity:
        facts = probe.column.facts
        if not isinstance(facts, contract.LabelFacts):
            continue
        compared = compared + 1
        if any(level.variants_withheld for level in facts.levels):
            withheld = withheld + 1
        assert validation._spelling_supply(
            probe.column, facts, probe.column.n_distinct
        ) == generation._label_supply(facts), probe.stem
    assert compared >= 30, compared
    assert withheld >= 5, withheld


def test_the_withheld_variant_witness_reaches_the_generators_own_twin(
    parity: "tuple[Probe, ...]",
) -> None:
    """P3-V7-F3's own column, from the producer to the report.

    Four spellings over two levels, six and five rows each, under the
    floor of eleven: the description publishes raw distinctness four,
    one level whose two withheld variants cover it exactly, and one
    level held back whole. G12.7 supplies three spellings, the shipped
    generator writes three, and the arithmetic that counted the withheld
    COUNT as row coverage read four, invented a spelling, claimed no
    corner and reported the product's own twin MISSED.
    """
    found = [
        probe for probe in parity
        if probe.stem == "witness-label-withheld"
    ]
    assert len(found) == 1
    probe = found[0]
    facts = probe.column.facts
    assert isinstance(facts, contract.LabelFacts)
    assert probe.column.n_distinct == 4
    assert facts.suppressed_levels == 1
    assert [dict(level.variants_withheld) for level in facts.levels] == [
        {"6": 2}
    ]
    assert validation._spelling_supply(
        probe.column, facts, probe.column.n_distinct
    ) == 3
    assert generation._label_supply(facts) == 3
    assert probe.corners == (validation.CORNER_LABEL_VARIANTS_SHORT,)
    assert _verdicts(probe.outcome, "distinct.n_distinct") == [
        validation.AUTHORIZED_DEVIATION
    ]
    assert probe.outcome.census.missed == 0
    # AND THE FOLDED COUNT KEEPS THE EXACT BAR (review item P3-V8-F3).
    # G12.7's envelope is raw `n_distinct` and nothing else, in V4.1's
    # words and the registry's; the generator meets the folded count
    # exactly on this very description and files no bound for it.
    assert not validation._distinct_corner(
        facts, probe.corners, validation._FOLDED_DISTINCT
    )
    assert _generator_envelope(probe.twin, "n_distinct_folded") is None
    assert _verdicts(probe.outcome, "distinct.n_distinct_folded") == [
        validation.HELD
    ]


def test_the_floored_style_witness_reaches_the_generators_own_twin(
    parity: "tuple[Probe, ...]",
) -> None:
    """P3-V7-F4's first half, from the producer to the report.

    A floored style map naming fifteen leading-zero cells on a column
    publishing nine different values. Those cells each carry their own
    spelling, so the supply STANDS ABOVE the published count and G12.8's
    envelope opens upward -- which the version this replaces could not
    say, because it asked only whether the supply fell short. The
    shipped generator writes twelve identities, its own report calls
    that inside the bound, and the exact bar called it MISSED.
    """
    found = [
        probe for probe in parity
        if probe.stem == "witness-number-floored"
    ]
    assert len(found) == 1
    probe = found[0]
    facts = probe.column.facts
    assert isinstance(facts, contract.NumericFacts)
    assert probe.column.n_distinct == 9
    assert facts.numeric_styles[parsing.STYLE_LEADING_ZERO] == 15
    assert taxonomy.SUPPRESSED_LABEL in facts.numeric_styles
    assert validation._spelling_supply(
        probe.column, facts, probe.column.n_distinct
    ) == 16
    assert probe.corners == (validation.CORNER_NUMERIC_SPELLINGS_SHORT,)
    for field in ("n_distinct", "n_distinct_folded"):
        assert _verdicts(probe.outcome, f"distinct.{field}") == [
            validation.AUTHORIZED_DEVIATION
        ], field


def test_the_class_witness_gets_g12_8s_second_summand(
    parity: "tuple[Probe, ...]",
    tmp_path: pathlib.Path,
) -> None:
    """P3-V8-F4: the classes are counted, and what is still open is measured.

    Twenty whole numbers written one way beside two cells that are not
    numbers. G12.8's supply has two summands and only the first was ever
    written, so this description's floor read ONE spelling -- one value
    for all twenty plain cells and nothing at all for the two beside
    them. A floor of one with a ceiling at every present cell is a bar
    that cannot fail, so both distinctness entries left the checks
    altogether and became listings, and a file holding twenty-one
    different values against a published twenty-two was told that no
    checkable obligation was missed.

    The second summand is the budget of G6.5, which is arithmetic on
    four published cell counts and the published count itself, so it
    needs nothing this module may not import. It settles the two cells
    beside the numbers exactly: the floor is three, the entries are
    checks again, and the collapsed column a listing used to license
    now MISSES.

    AND THE PART THAT IS STILL OPEN IS ASSERTED HERE AT ITS SIZE rather
    than described (plan amendment A-P3-20 clause 3). How many different
    VALUES the twenty plain cells carry is decided by the value
    construction of G5, which V1.4 keeps out of this module, so the
    floor stays at three where the generation report prints twenty-two.
    A file one different value short of the published count therefore
    lands inside this validator's envelope and is reported an AUTHORIZED
    DEVIATION, not a MISS. That is the residue, it is exactly the plain
    cells' value count, and this test goes red the moment it changes in
    either direction.
    """
    found = [
        probe for probe in parity
        if probe.stem == "witness-number-classes"
    ]
    assert len(found) == 1
    probe = found[0]
    column = probe.column
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    assert column.n_present == 22
    assert column.n_distinct == 22
    assert column.n_numeric == 20
    assert column.n_not_numeric == 2
    assert dict(facts.numeric_styles) == {parsing.STYLE_PLAIN: 20}
    # The budget of G6.5, class by class, in that method's own order.
    assert validation._class_budget(column, column.n_distinct) == (
        20,
        0,
        0,
        2,
    )
    assert validation._other_class_spellings(column, column.n_distinct) == 2
    assert (
        validation._spelling_supply(column, facts, column.n_distinct) == 3
    )
    assert (
        validation._spelling_ceiling(column, facts, column.n_distinct) == 22
    )
    # Both entries are CHECKS now, and neither is a listing.
    for field in ("n_distinct", "n_distinct_folded"):
        assert _files(probe.outcome, f"distinct.{field}"), field
        assert not [
            listing
            for listing in probe.outcome.listings
            if listing.subcheck == f"distinct.{field}"
        ], field
    # The generator pins this description at twenty-two, and this
    # validator's envelope holds that -- containment, not equality.
    for field in ("n_distinct", "n_distinct_folded"):
        theirs = _generator_envelope(probe.twin, field)
        assert theirs == (22, 22), (field, theirs)
    assert probe.outcome.census.missed == 0

    folder = tmp_path / "classes"
    folder.mkdir()
    cells = list(probe.twin.columns[0])

    def _verdict_on(made: "list[str]", tag: str) -> str:
        path = fixtures.write(
            folder,
            f"{tag}.csv",
            fixtures.single_column_table(NAME, made),
        )
        outcome = validation.measure(probe.described, str(path))
        verdicts = _verdicts(outcome, "distinct.n_distinct")
        assert len(verdicts) == 1, (tag, verdicts)
        return verdicts[0]

    # A column collapsed onto one repeated value is below the floor of
    # three and MISSES. Under the bar as it stood there was no check at
    # all for it to miss.
    assert _verdict_on([cells[0]] * len(cells), "flat") == validation.MISSED
    # One value short of the published count is inside this validator's
    # envelope: the residue above, measured.
    one_short = list(cells)
    one_short[1] = one_short[0]
    assert _verdict_on(one_short, "one-short") == (
        validation.AUTHORIZED_DEVIATION
    )


def test_the_band_witness_is_short_where_the_summed_reach_is_not(
    parity: "tuple[Probe, ...]",
) -> None:
    """P3-V7-F2's second half, from the producer to the report.

    Fifty-four one-character cells: one repeated figure, one code value,
    and twenty-six values outside the code alphabet of which twenty-five
    stand in two rows each. The widest band answers for fifty-one cells
    in groups no wider than two, so it needs twenty-six spellings and
    holds twenty-five -- while the summed reach reads twenty-eight
    against twenty-eight, because it lets the two one-row groups answer
    for every band at once.
    """
    found = [
        probe for probe in parity
        if probe.stem == "witness-identifier-bands"
    ]
    assert len(found) == 1
    probe = found[0]
    facts = probe.column.facts
    assert isinstance(facts, contract.IdentifierFacts)
    assert probe.column.n_present == 54
    assert probe.column.n_distinct == 28
    assert (facts.min_length, facts.max_length) == (1, 1)
    assert facts.n_all_digits == 2
    assert facts.n_code_alphabet == 3
    assert dict(facts.n_distinct_by_occurrences) == {"1": 2, "2": 26}
    assert probe.corners == (validation.CORNER_IDENTIFIER_INFEASIBLE,)
    # The generator's own cells are the proof the corner is real.
    assert len({
        cell for cell in probe.twin.columns[0] if cell != ""
    }) == 27
    assert probe.outcome.census.missed == 0
    for field in ("n_distinct", "n_distinct_folded",
                  "n_distinct_by_occurrences"):
        assert not _files(probe.outcome, f"distinct.{field}"), field


# -- what the battery found that the review did not name ---------------


def test_a_pooled_style_map_does_not_refuse_the_generators_own_twin(
    parity: "tuple[Probe, ...]",
    tmp_path: pathlib.Path,
) -> None:
    """The fifth divergence, and it is not a corner at all.

    The publication floor pools every numeric form fewer cells wear than
    the floor into one withheld key and publishes no count for any of
    them, so a cell in that pool has no published form and a twin may
    give it any form the description permits -- `plain` among them. The
    exact bar compared the file's recount of a NAMED form against the
    published number as though the pool did not exist, so eleven plain
    cells published against forty-five written came back MISSED on the
    shipped generator's own output, on every description in this space
    whose style map the floor had pooled.

    The bar is a window now, and it still has teeth in the direction
    that matters: the published cells are owed, so a file writing fewer
    of them than the description names still misses.
    """
    pooled = 0
    for probe in parity:
        facts = probe.column.facts
        if not isinstance(facts, contract.NumericFacts):
            continue
        if taxonomy.SUPPRESSED_LABEL not in facts.numeric_styles:
            continue
        pooled = pooled + 1
        for check in probe.outcome.checks:
            if not check.subcheck.startswith("styles.published."):
                continue
            assert check.verdict != validation.MISSED, (
                f"{probe.stem}: {check.subcheck} reported MISSED "
                f"(published {check.published}, achieved {check.achieved}) "
                f"on the shipped generator's own twin, whose description "
                f"names no form for "
                f"{facts.numeric_styles[taxonomy.SUPPRESSED_LABEL]} of "
                f"its cells"
            )
    assert pooled >= 5, pooled
    # ...and the window still refuses a file that writes fewer of the
    # named form than the description publishes.
    folder = tmp_path / "pooled"
    folder.mkdir()
    found = [
        probe for probe in parity
        if probe.stem == "witness-number-floored"
    ]
    assert len(found) == 1
    probe = found[0]
    facts = probe.column.facts
    assert isinstance(facts, contract.NumericFacts)
    assert facts.numeric_styles[parsing.STYLE_LEADING_ZERO] == 15
    made = [
        f"{place}" for place in range(probe.column.n_present)
    ]
    path = fixtures.write(
        folder,
        "no-leading-zeros.csv",
        fixtures.single_column_table(NAME, made),
    )
    outcome = validation.measure(probe.described, str(path))
    assert validation.MISSED in _verdicts(
        outcome, f"styles.published.{parsing.STYLE_LEADING_ZERO}"
    )


# -- the space itself, so neither walk above can narrow ----------------


def test_the_described_columns_reach_every_case_asserted_above(
    parity: "tuple[Probe, ...]",
) -> None:
    """A coverage assertion: what the two walks are actually walking."""
    roles: dict[str, int] = {}
    bands = {"digits": 0, "code": 0, "wide": 0}
    whole = {True: 0, False: 0}
    widths: dict[int, int] = {}
    floors: dict[int, int] = {}
    styles: dict[str, int] = {}
    for probe in parity:
        column = probe.column
        facts = column.facts
        roles[column.role] = roles.get(column.role, 0) + 1
        floors[probe.described.settings.small_cell_floor] = 1
        if isinstance(facts, contract.IdentifierFacts):
            if facts.n_all_digits > 0:
                bands["digits"] = bands["digits"] + 1
            if facts.n_code_alphabet > facts.n_all_digits:
                bands["code"] = bands["code"] + 1
            if column.n_present > facts.n_code_alphabet:
                bands["wide"] = bands["wide"] + 1
            whole[facts.all_whole_numbers] = whole[facts.all_whole_numbers] + 1
            widths[facts.max_length] = widths.get(facts.max_length, 0) + 1
        if isinstance(facts, contract.NumericFacts):
            for style in facts.numeric_styles:
                styles[style] = styles.get(style, 0) + 1
    assert len(roles) >= 5, roles
    for band in sorted(bands):
        assert bands[band] >= 10, (band, bands)
    assert whole[True] >= 5, whole
    assert whole[False] >= 20, whole
    assert sorted(widths) == [1, 2, 3], widths
    assert sorted(floors) == [1, 11], floors
    for style in (
        parsing.STYLE_PLAIN,
        parsing.STYLE_LEADING_ZERO,
        parsing.STYLE_DECIMAL,
        taxonomy.SUPPRESSED_LABEL,
    ):
        assert styles.get(style, 0) >= 3, (style, styles)


# -- helpers -----------------------------------------------------------


def _files(outcome: validation.Outcome, subcheck: str) -> bool:
    """Whether this run filed ``subcheck`` as an executable check."""
    return any(check.subcheck == subcheck for check in outcome.checks)


def _verdicts(
    outcome: validation.Outcome, subcheck: str
) -> "list[str]":
    """Every verdict filed under one subcheck identity."""
    return [
        check.verdict
        for check in outcome.checks
        if check.subcheck == subcheck
    ]
