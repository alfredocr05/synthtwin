"""The identifier corner is method G9.4's capacity rule, written twice.

REVIEW ITEM P3-V6-F1. `identifier-infeasible` is the one corner that
takes THREE checks off a column -- raw distinctness, folded distinctness
and the occurrence multiset -- so a corner claimed where none exists is
the shape this whole product exists to prevent: a file whose identifier
column has collapsed to one repeated value loses every check that could
notice, and the report ends `NO CHECKABLE OBLIGATION WAS MISSED.`

That is what the version this replaces did. It summed `alphabet ** L`
over the published length range with the alphabet read off one published
count -- ten characters where `n_code_alphabet` is zero and thirty-six
otherwise -- and neither number is a domain synthtwin writes from. A
declared column of eleven one-character codes outside the code alphabet
was called infeasible by it while the shipped generator writes all
eleven, and eleven copies of one of them then passed.

**The classifier is now the method's own arithmetic** (G9.1's three
alphabets, G9.5 step 4's band split, G9.6's whole-number families,
G9.4's saturating capacity), and the two writings are compared HERE,
where both may be imported -- the arrangement V4.2 makes for exactly
this classifier. The comparison is CORRECTNESS and not merely agreement
of shape: the shipped generator is asked to build each description, and
a description it answers may not be called a corner. The corner test
that stood before this one asserted determinism and membership only,
which is why the defect lived under a green suite.

WHY THE THREE BANDS ARE ASKED TOGETHER. Reading one band at a time
misses a whole family of descriptions: a 115-row column of one-character
codes publishing 89 groups is short in no single band while ten,
fifty-three and twenty-five spellings are eighty-eight between them.
The battery below carries that boundary at 87 and 88.

Every table is built at test time by the seeded neutral builders in
`fixtures.py`; no data-format file enters the repository (plan D13).
"""

import pathlib

import pytest

import fixtures
from synthtwin import (
    contract,
    generation,
    profile,
    quality,
    reading,
    rendering,
    taxonomy,
    validation,
)

SEED = 20260814

_NAME = "record_id"


# -- the neutral builders the battery is written from ------------------


def _outside_the_code_alphabet(count: int) -> "list[str]":
    """``count`` different one-character values no code alphabet holds.

    The same construction the free-text domain boundary uses: a value
    per even code point above the Latin block, so the values are one
    character long, are outside every band but the widest, and carry no
    language at all.
    """
    return [chr(0x100 + 2 * index) for index in range(count)]


def _letters() -> "list[str]":
    """The fifty-two one-character values with a case."""
    upper = [chr(code) for code in range(ord("A"), ord("Z") + 1)]
    lower = [chr(code) for code in range(ord("a"), ord("z") + 1)]
    return upper + lower


def _figures(low: int, high: int) -> "list[str]":
    """The whole numbers from ``low`` to ``high``, written in figures."""
    return [f"{number}" for number in range(low, high + 1)]


def _padded(low: int, high: int) -> "list[str]":
    """The same, padded to two figures, so every value is two wide."""
    return [f"{number:02d}" for number in range(low, high + 1)]


def _repeated(values: "list[str]", times: int) -> "list[str]":
    """Every value of ``values``, ``times`` rows each."""
    built: list[str] = []
    for value in values:
        for _step in range(times):
            built = built + [value]
    return built


# THE BATTERY. Each entry is one declared column of record numbers, and
# between them they reach all three alphabet bands, both whole-number
# readings, one to three characters of published width, and repetition
# patterns from all-different to threefold. The four PAIRS are the ones
# that matter most: each is a boundary asserted from both sides, so a
# classifier that fires one value early is caught as surely as one that
# fires one value late.
_BATTERY: "tuple[tuple[str, list[str]], ...]" = (
    # The review's own witness: eleven one-character values outside the
    # code alphabet, which the old ceiling called infeasible.
    ("wide-eleven", list("!#$%&()*/:;")),
    # Boundary 1 -- the widest band holds twenty-five one-character
    # values (method G9.4 counts them out) and no more.
    ("wide-at-the-line", _outside_the_code_alphabet(25)),
    ("wide-over-the-line", _outside_the_code_alphabet(26)),
    # Boundary 2 -- whole numbers in figures alone open with a figure
    # that is not zero (G9.6), so one character spells nine and not ten.
    ("figures-at-the-line", _figures(1, 9)),
    ("figures-over-the-line", _figures(0, 9)),
    # Boundary 3 -- the same rule two characters wide.
    ("padded-at-the-line", _padded(10, 99)),
    ("padded-over-the-line", _padded(0, 99)),
    # Boundary 4 -- three bands at once, short in none of them alone.
    (
        "three-bands-at-the-line",
        _figures(0, 9) + _letters() + _outside_the_code_alphabet(25),
    ),
    (
        "three-bands-over-the-line",
        _figures(0, 9) + _letters() + _outside_the_code_alphabet(26),
    ),
    # Ordinary columns of every band and width, each of which the
    # generator answers and none of which may be called a corner.
    ("code-fifty-two", _letters()),
    ("code-fifty-three", _letters() + ["_"]),
    ("mixed-bands", ["7", "8", "a", "b", "!", "#", "$", "%"]),
    ("wide-two-characters", [f"!{letter}" for letter in _letters()[:30]]),
    ("code-three-characters", [f"a{number:02d}" for number in range(60)]),
    ("wide-doubled", _repeated(_outside_the_code_alphabet(12), 2)),
    ("wide-tripled", _repeated(list("!#$%&()*/:;"), 3)),
    ("padded-with-repeats", _repeated(_padded(10, 40), 2)),
)

# The pairs of `_BATTERY` entries that sit either side of one boundary.
_BOUNDARIES = (
    ("wide-at-the-line", "wide-over-the-line"),
    ("figures-at-the-line", "figures-over-the-line"),
    ("padded-at-the-line", "padded-over-the-line"),
    ("three-bands-at-the-line", "three-bands-over-the-line"),
)


# -- one whole run, as the three commands build one --------------------


def _describe(
    folder: pathlib.Path, values: "list[str]", stem: str
) -> contract.Profile:
    """One declared column of record numbers, through the real producer."""
    table = fixtures.write(
        folder, f"{stem}.csv", fixtures.single_column_table(_NAME, values)
    )
    read = reading.read_table(str(table))
    document = profile.build_document(read, taxonomy.Settings(), [_NAME])
    written = fixtures.write_profile(folder, f"{stem}-profile.json", document)
    return contract.load_profile(str(written))


def _twin(described: contract.Profile) -> generation.Twin:
    """The twin `synthtwin generate` would write for this description."""
    return generation.generate(described, SEED)


def _distinct_present(twin: generation.Twin) -> int:
    """How many different present values the twin's one column holds."""
    found: dict[str, int] = {}
    for cell in twin.columns[0]:
        if cell != "":
            found[cell] = 1
    return len(found)


def _generator_answers(
    described: contract.Profile, twin: generation.Twin
) -> bool:
    """Whether the shipped generator met this column's distinctness.

    The question the corner answers is whether the published values can
    be spelled at all, so the generator's OWN cells are the evidence:
    a column whose twin holds as many different values as the
    description publishes is a column no corner may be claimed over.
    """
    column = described.columns[0]
    return _distinct_present(twin) == column.n_distinct


def _has_corner(described: contract.Profile) -> bool:
    """Whether the validator claims owner decision 6's corner here."""
    corners = validation.corners_of(described)
    column = described.columns[0]
    if column.name not in corners:
        return False
    return validation.CORNER_IDENTIFIER_INFEASIBLE in corners[column.name]


def _measure(
    folder: pathlib.Path,
    described: contract.Profile,
    text: str,
    name: str,
) -> validation.Outcome:
    """Write one measured file and measure it against a description."""
    target = fixtures.write(folder, name, text)
    return validation.measure(described, str(target))


def _verdicts(outcome: validation.Outcome, subcheck: str) -> "list[str]":
    """Every verdict filed under one subcheck identity."""
    return [
        check.verdict
        for check in outcome.checks
        if check.subcheck == subcheck
    ]


_DISTINCTNESS = (
    "distinct.n_distinct",
    "distinct.n_distinct_folded",
    "distinct.n_distinct_by_occurrences",
)


@pytest.fixture(scope="module")
def battery(
    tmp_path_factory: pytest.TempPathFactory,
) -> "tuple[tuple[str, contract.Profile, generation.Twin], ...]":
    """Every battery description, with the twin the generator built.

    Built once for the module: the producer and the generator are both
    run per entry and nothing here depends on test order.
    """
    folder = tmp_path_factory.mktemp("identifier-battery")
    built: list[tuple[str, contract.Profile, generation.Twin]] = []
    for name, values in _BATTERY:
        described = _describe(folder, values, name)
        column = described.columns[0]
        assert isinstance(column.facts, contract.IdentifierFacts), name
        assert validation.refusal_of(described) == "", name
        built = built + [(name, described, _twin(described))]
    return tuple(built)


# -- V4.2, in the direction that was never asserted --------------------


def test_no_description_the_generator_answers_is_called_a_corner(
    battery: "tuple[tuple[str, contract.Profile, generation.Twin], ...]",
) -> None:
    """THE FINDING'S CLASS: a corner may not remove a checkable fact.

    For every description in the battery the shipped generator writes a
    twin. Where that twin holds as many different record numbers as the
    description publishes, the description is one a twin exists for, and
    calling it infeasible would take three checks off a column over
    nothing at all.
    """
    answered = 0
    for name, described, twin in battery:
        if not _generator_answers(described, twin):
            continue
        answered = answered + 1
        assert not _has_corner(described), (
            f"{name}: the generator wrote every published value and the "
            f"validator called the description infeasible"
        )
    # NOT VACUOUS: the battery has to contain descriptions the generator
    # answers, or the walk above asserts nothing.
    assert answered >= 12, answered


def test_the_corner_holds_where_the_published_width_truly_runs_out(
    battery: "tuple[tuple[str, contract.Profile, generation.Twin], ...]",
) -> None:
    """The other side of every boundary, so the rule is not one-way.

    A classifier that never claims the corner passes the test above by
    saying nothing. Each pair below sits either side of one capacity
    line: on the low side the generator writes every published value and
    no corner is claimed, and one value further on the generator repeats
    and the corner IS claimed, which is what owner decision 6 grants.
    """
    by_name = {name: (described, twin) for name, described, twin in battery}
    for inside, beyond in _BOUNDARIES:
        described, twin = by_name[inside]
        assert _generator_answers(described, twin), inside
        assert not _has_corner(described), inside
        described, twin = by_name[beyond]
        assert not _generator_answers(described, twin), beyond
        assert _has_corner(described), beyond


def test_the_battery_reaches_every_band_and_both_whole_number_readings(
    battery: "tuple[tuple[str, contract.Profile, generation.Twin], ...]",
) -> None:
    """A coverage assertion, so the two walks above cannot narrow.

    The corner divides the published cells between three alphabet bands
    and reads a different family into each where every value is a whole
    number, so a battery that reaches only one band tests one third of
    the rule.
    """
    bands = {"digits": 0, "code": 0, "wide": 0}
    whole = {True: 0, False: 0}
    widths = {}
    for _name, described, _twin in battery:
        column = described.columns[0]
        facts = column.facts
        assert isinstance(facts, contract.IdentifierFacts)
        if facts.n_all_digits > 0:
            bands["digits"] = bands["digits"] + 1
        if facts.n_code_alphabet > facts.n_all_digits:
            bands["code"] = bands["code"] + 1
        if column.n_present > facts.n_code_alphabet:
            bands["wide"] = bands["wide"] + 1
        whole[facts.all_whole_numbers] = whole[facts.all_whole_numbers] + 1
        widths[facts.max_length] = 1
    for band in sorted(bands):
        assert bands[band] >= 2, (band, bands)
    assert whole[True] >= 3, whole
    assert whole[False] >= 8, whole
    assert sorted(widths) == [1, 2, 3], widths


# -- the scenario the finding reported, end to end ---------------------


def test_a_collapsed_identifier_column_no_longer_receives_a_pass(
    tmp_path: pathlib.Path,
) -> None:
    """The review's own witness, from the producer to the report.

    Eleven different one-character values outside the code alphabet.
    The description publishes eleven present, eleven different, eleven
    different folded and one row per value; the shipped generator writes
    eleven different conforming values, so the description is plainly
    one a twin exists for. A candidate file holding one of those values
    eleven times misses all three distinctness facts, the census counts
    them, and the report may not end by saying nothing was missed.
    """
    folder = tmp_path / "collapsed"
    folder.mkdir()
    values = list("!#$%&()*/:;")
    described = _describe(folder, values, "wide-eleven")
    column = described.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.IdentifierFacts)
    # What the producer published, stated so the witness is checkable.
    assert column.n_present == 11
    assert column.n_distinct == 11
    assert column.n_distinct_folded == 11
    assert (facts.min_length, facts.max_length) == (1, 1)
    assert facts.n_code_alphabet == 0
    assert facts.n_distinct_by_occurrences == {"1": 11}
    # The generator's own answer is the proof the description is feasible.
    twin = _twin(described)
    assert _distinct_present(twin) == 11
    assert not _has_corner(described)

    # ...so a column that has collapsed to one value misses all three.
    collapsed = _measure(
        folder,
        described,
        fixtures.single_column_table(_NAME, [values[0]] * 11),
        "collapsed.csv",
    )
    for subcheck in _DISTINCTNESS:
        assert _verdicts(collapsed, subcheck) == [validation.MISSED], subcheck
        assert subcheck not in [
            listing.subcheck for listing in collapsed.listings
        ], subcheck
    assert collapsed.census.missed >= 3
    report = quality.quality_report(described, collapsed)
    assert "NO CHECKABLE OBLIGATION WAS MISSED." not in report
    assert "CHECKABLE OBLIGATION(S) WERE MISSED." in report

    # ...while the twin of that same description still passes, which is
    # the direction a repair to a check has to keep.
    green = _measure(
        folder, described, rendering.twin_csv(twin), "wide-eleven-twin.csv"
    )
    assert green.census.missed == 0
    for subcheck in _DISTINCTNESS:
        assert _verdicts(green, subcheck) == [validation.HELD], subcheck


def test_a_column_that_truly_runs_out_still_reaches_owner_decision_six(
    tmp_path: pathlib.Path,
) -> None:
    """The lesser outcome is still granted where the plan grants it.

    Ten one-character whole numbers. Figures alone open with a figure
    that is not zero (G9.6), so one character spells nine values and the
    shipped generator writes nine where ten are published -- the corner
    owner decision 6 names. Its twin therefore validates with nothing
    missed, and the three facts appear as listings rather than as
    checks: the achieved value is named beside the published one and no
    verdict pretends to have been passed.
    """
    folder = tmp_path / "figures"
    folder.mkdir()
    described = _describe(folder, _figures(0, 9), "figures-ten")
    column = described.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.IdentifierFacts)
    assert facts.all_whole_numbers
    assert (facts.min_length, facts.max_length) == (1, 1)
    assert column.n_distinct == 10
    twin = _twin(described)
    assert _distinct_present(twin) == 9
    assert _has_corner(described)
    outcome = _measure(
        folder, described, rendering.twin_csv(twin), "figures-twin.csv"
    )
    assert outcome.census.missed == 0
    listed = [listing.subcheck for listing in outcome.listings]
    for subcheck in _DISTINCTNESS:
        assert _verdicts(outcome, subcheck) == [], subcheck
        assert subcheck in listed, subcheck


# -- the numbers the method fixes, pinned where they are read ----------


def test_the_band_capacities_are_the_numbers_the_method_counts_out(
) -> None:
    """G9.4 and G9.6 name these, and a re-invented ceiling changes them.

    The defect this file repairs was an arithmetic nobody had checked
    against the method's own counting, so the counting is asserted here
    directly: the widest band's twenty-five one-character values are
    G9.4's own worked example, and the whole-number families of G9.6 are
    each one character wider than the figures they carry.
    """
    # G9.4, counted out in the method: ninety-five printable characters,
    # less the space at both ends, less the four a spreadsheet reads as
    # a formula, less the two that already mean "no value".
    assert validation._capacity_at(validation._BAND_WIDE, 1) == 25
    # The code alphabet at one character: never a figure, never the one
    # formula leader it holds.
    assert validation._capacity_at(validation._BAND_CODE, 1) == 53
    assert validation._capacity_at(validation._BAND_DIGITS, 1) == 10
    # G9.6's whole-number families. Figures alone lose the leading zero;
    # `<digits>e0` has nothing to write below three characters except
    # the ten spellings that open with a sign, which owner decision 9
    # permits at two; `<digits>.` has nothing to write at one.
    whole = validation._identifier_capacity_at
    assert whole(validation._BAND_DIGITS, 1, True) == 9
    assert whole(validation._BAND_DIGITS, 2, True) == 90
    assert whole(validation._BAND_CODE, 1, True) == 0
    assert whole(validation._BAND_CODE, 2, True) == 10
    assert whole(validation._BAND_CODE, 3, True) == 10
    assert whole(validation._BAND_WIDE, 1, True) == 0
    assert whole(validation._BAND_WIDE, 2, True) == 10


def test_the_classifier_reads_no_file_and_never_varies(
    tmp_path: pathlib.Path,
) -> None:
    """V4.2 again: a pure function of the description, on this path too.

    The repaired predicate reads four published numbers and one
    published map. Nothing here may make it depend on a measured file,
    so the same description is classified the same way twice and the
    classification is taken before any file exists.
    """
    folder = tmp_path / "pure"
    folder.mkdir()
    described = _describe(folder, _outside_the_code_alphabet(26), "beyond")
    once = validation.corners_of(described)
    again = validation.corners_of(described)
    assert once == again
    assert once[_NAME] == (validation.CORNER_IDENTIFIER_INFEASIBLE,)
