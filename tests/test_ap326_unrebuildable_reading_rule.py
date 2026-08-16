"""A description that cannot be read back says so, and stops guessing.

OWNER RULING 2026-08-16, plan amendment A-P3-26. `validate` is defined
as: rebuild the reading rule from the description, re-describe the
measured file with it, compare (V2.2). That definition needs the
description to pin the reading rule. It does not. The settings block
records a declaration as a COUNT and never as text, and the one field
where a spelling survives -- a column's `missing_by_source` -- is
narrowed on the way out in four separate ways.

FOUR ROUTES, AND A FIFTH THAT IS A NAME CLASH. Each is a witness here:

1. the named spellings are never written into the settings block at
   all, so a `--keep-value` on a column publishing no level and no
   sentinel verdict is published nowhere;
2. a key crosses the DISPLAY BOUNDARY, so any spelling holding an
   invisible character is unrecoverable and two tables needing opposite
   rules are described byte for byte alike;
3. a spelling whose cells sit below the publication floor is pooled,
   unnamed, into the withheld remainder;
4. a column whose publication class publishes no value of the table --
   free text -- publishes an EMPTY source map, on purpose, so the
   marker word is nowhere at all;
5. and the map's keys are the person's text and this package's own
   class words in one list with nothing to tell them apart, so a table
   whose cells literally read `(withheld)` publishes the key the pooled
   remainder wears.

WHAT USED TO HAPPEN ON ALL FIVE. The validator re-described the file
under a rule the description was not written under, found the marker
cells reading as data, and reported the difference as a MISS -- on a
file that is its own description's perfect match. Seven, seven and
eleven obligations, printed with the numbers the wrong reading produced.
A confident falsehood is the worst output this project can write, and
these were confident, numeric and false.

WHAT HAPPENS NOW. The description is asked, before any file is read,
whether the rule can be rebuilt for each column. Where it cannot, that
column's cell-counted obligations go to the NOT-CHECKABLE census with a
sentence saying what the description does not record. Nothing about the
measured file decides it, so two files one description cannot tell apart
still get one report (V5.1), and the obligation set stays a function of
the description alone (V3.3).

THE TEST IS A UNION OF TWO, AND NEITHER ALONE WOULD DO. A structural
question per column -- are there declared holes no spelling brings back?
-- misses the table where one named word is published and another is
pooled. A head count per document -- were more words named than come
back? -- catches that one and reports a gap on a table where somebody
named a word the table never held. The union never misses a real gap.
Where it over-fires it moves obligations to not-checkable on a file that
would have passed anyway, which is the safe direction; the other one
prints a number about a file that is not true of it. The over-fire is
asserted here too, at its size, so that narrowing it later is a change
somebody chose rather than one nobody noticed.

WHAT THIS COSTS, AND IT IS NOT NOTHING. It LOWERS what is checked on an
affected column: on the free-text witness eleven of thirty-one checkable
obligations were misses and twenty-one of thirty-one are now
not-checkable, so ten checks remain. And in one construction it lowers
the verdict itself: the file that genuinely does not conform, measured
against the description of its indistinguishable twin, returns exit code
0 with the seven obligations named rather than exit 3 with seven misses.
That construction is `test_p3v7f1_escaped_declarations.py`'s, and it is
asserted there.

THE RED CHECK. `REINSTATE=A-P3-26` in the environment puts the
pre-ruling behaviour back -- no column is ever unrebuildable, so every
one of these witnesses re-describes the file under an incomplete rule
and reports the misses again. Every assertion below that says a witness
misses nothing goes red with it, and so does every assertion that names
an obligation as unsupported.

Every table is built at test time by seeded neutral builders; no
data-format file enters the repository (plan D13).
"""

import os
import pathlib
import typing

import pytest

import fixtures
from synthtwin import (
    canonical,
    contract,
    generation,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

# The two spellings of one published key: a real control character, and
# the printable characters the display boundary writes it as.
_RAW = "X\x01Y"
_SHOWN = "X\\x01Y"

# This package's own word for the pooled remainder, which a person's own
# cell can also literally spell (route 5).
_POOL_WORD = "(withheld)"
_CLASS_WORD = "(declared-missing)"

_FLOOR = taxonomy.Settings().small_cell_floor


@pytest.fixture(scope="module", autouse=True)
def _reinstated() -> "typing.Iterator[None]":
    """Put the pre-ruling behaviour back when REINSTATE asks for it.

    MODULE-SCOPED, because the descriptions and reports below are built
    in module-scoped fixtures and a function-scoped patch would be
    applied after they were built -- a red check run against a patch
    nobody used.
    """
    monkeypatch = pytest.MonkeyPatch()
    if os.environ.get("REINSTATE") == "A-P3-26":
        monkeypatch.setattr(
            validation, "unrebuildable_columns", lambda _described: {}
        )
    yield
    monkeypatch.undo()


# -- the builders ------------------------------------------------------


def _numbers(count: int) -> "list[str]":
    """Decimals whose written form is already the canonical one."""
    found: list[str] = []
    seen: dict[str, int] = {}
    step = 3
    while len(found) < count:
        step = step + 7
        text = f"{step / 10:.1f}"
        if text.endswith("0") or text in seen:
            continue
        seen[text] = 1
        found = found + [text]
    return found


def _comments(count: int, length: int) -> "list[str]":
    """Distinct sentences long enough to read as free text."""
    words = ("alpha", "bravo", "cedar", "delta", "eagle", "flint", "gamma")
    found: list[str] = []
    for index in range(count):
        built = f"note {index:03d}"
        step = index
        while len(built) < length:
            step = step + 1
            built = built + " " + words[step % len(words)]
        found = found + [built[:length]]
    return found


def _numeric_table(markers: "list[str]") -> str:
    """Sixty numbers, then one cell for each marker spelling given."""
    values = _numbers(60) + markers
    return fixtures.single_column_table("reading", values)


def _text_table(markers: "list[str]") -> str:
    """Sixty comments, then one cell for each marker spelling given."""
    values = _comments(60, 50) + markers
    return fixtures.single_column_table("note", values)


def _described(
    folder: pathlib.Path,
    stem: str,
    text: str,
    settings: taxonomy.Settings,
) -> "tuple[contract.Profile, str, dict]":
    """One table through the real producer, loader and all."""
    path = fixtures.write(folder, f"{stem}.csv", text)
    table = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(table, settings, [])
    loaded = contract.load_profile(
        str(fixtures.write_profile(folder, f"{stem}-profile.json", document))
    )
    return loaded, str(path), document


class Witness(typing.NamedTuple):
    """One route, built end to end: description, table, and the marker."""

    route: str
    described: contract.Profile
    path: str
    document: dict
    marker: str


def _witnesses(folder: pathlib.Path) -> "dict[str, Witness]":
    """One witness per route, plus the controls the union is judged on."""
    built: dict[str, Witness] = {}

    def add(route: str, stem: str, text: str, settings, marker: str) -> None:
        described, path, document = _described(folder, stem, text, settings)
        built[route] = Witness(route, described, path, document, marker)

    # Route 1: a rescued word on a column that publishes no spelling.
    add(
        "rescued",
        "rescued",
        fixtures.single_column_table("reading", _numbers(200) + ["n/a"]),
        taxonomy.Settings(kept_values=("n/a",)),
        "n/a",
    )
    # Route 2: a declaration holding an invisible character.
    add(
        "escaped",
        "escaped",
        _numeric_table([_RAW] * 12),
        taxonomy.Settings(declared_missing_values=(_RAW,)),
        _RAW,
    )
    # Route 3: declarations whose cells all sit below the floor.
    add(
        "pooled",
        "pooled",
        _numeric_table(["rare1"] * 3 + ["rare2"] * 3 + ["rare3"] * 3),
        taxonomy.Settings(
            declared_missing_values=("rare1", "rare2", "rare3")
        ),
        "rare1",
    )
    # Route 4: a column whose publication class publishes no value.
    add(
        "free-text",
        "free-text",
        _text_table(["ZZZ"] * 12),
        taxonomy.Settings(declared_missing_values=("ZZZ",)),
        "ZZZ",
    )
    # Route 5: the person's own text spelling one of this package's own
    # class words.
    add(
        "class-word",
        "class-word",
        _numeric_table([_CLASS_WORD] * 12),
        taxonomy.Settings(declared_missing_values=(_CLASS_WORD,)),
        _CLASS_WORD,
    )
    # Route 5, the confidentiality form: a cell literally spelling the
    # pooled remainder's own word.
    add(
        "pool-word",
        "pool-word",
        _numeric_table([_POOL_WORD] * 12),
        taxonomy.Settings(declared_missing_values=(_POOL_WORD,)),
        _POOL_WORD,
    )
    # The partial loss: one named word published, another pooled. This
    # is the one the structural question alone would walk past.
    add(
        "partial",
        "partial",
        _numeric_table(["XX"] * 12 + ["YY"] * 5),
        taxonomy.Settings(declared_missing_values=("XX", "YY")),
        "YY",
    )
    # CONTROL: the spelling comes back cleanly.
    add(
        "recovered",
        "recovered",
        _numeric_table(["XX"] * 12),
        taxonomy.Settings(declared_missing_values=("XX",)),
        "XX",
    )
    # CONTROL: no word named at all.
    add(
        "nothing-named",
        "nothing-named",
        _numeric_table([""] * 12),
        taxonomy.Settings(),
        "",
    )
    # THE OVER-FIRE, asserted rather than hoped away: a word named that
    # the table never held.
    add(
        "named-but-absent",
        "named-but-absent",
        _numeric_table(["XX"] * 12),
        taxonomy.Settings(declared_missing_values=("XX", "NEVERHERE")),
        "NEVERHERE",
    )
    return built


@pytest.fixture(scope="module")
def witnesses(
    tmp_path_factory: pytest.TempPathFactory,
) -> "dict[str, Witness]":
    """Every witness, built once."""
    return _witnesses(tmp_path_factory.mktemp("unrebuildable"))


# -- reading one outcome ----------------------------------------------


def _missed(outcome: validation.Outcome) -> "list[str]":
    """The subchecks one run reported MISSED, sorted."""
    return sorted(
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    )


def _unsupported(outcome: validation.Outcome) -> "list[str]":
    """The subchecks one run named as ones this description cannot ask."""
    return sorted(
        {
            listing.subcheck
            for listing in outcome.listings
            if listing.reason.endswith(validation.UNREBUILDABLE_REASON_TAIL)
        }
    )


def _checked(outcome: validation.Outcome) -> "list[str]":
    """The subchecks one run carried a verdict on, sorted."""
    return sorted(check.subcheck for check in outcome.checks)


# -- the routes --------------------------------------------------------

_ROUTES = (
    "rescued",
    "escaped",
    "pooled",
    "free-text",
    "class-word",
    "pool-word",
    "partial",
)


@pytest.mark.parametrize("route", _ROUTES)
def test_the_table_its_own_description_was_written_from_misses_nothing(
    witnesses: "dict[str, Witness]", route: str
) -> None:
    """The strongest case there is: a file against its own description.

    The answer has to be "everything matches", and on every one of
    these routes it was "some obligations were missed", with the numbers
    the wrong reading produced. Nothing here is missed now.
    """
    witness = witnesses[route]
    outcome = validation.measure(witness.described, witness.path)
    assert _missed(outcome) == [], route
    assert outcome.census.missed == 0, route


@pytest.mark.parametrize("route", _ROUTES)
def test_the_column_is_named_as_one_this_description_cannot_measure(
    witnesses: "dict[str, Witness]", route: str
) -> None:
    """Silence is not the repair: the limit is stated, per obligation."""
    witness = witnesses[route]
    flagged = validation.unrebuildable_columns(witness.described)
    assert sorted(flagged) == [witness.described.columns[0].name], route
    outcome = validation.measure(witness.described, witness.path)
    # The two presence counts are the obligations every one of these
    # routes reaches, so they are the ones asserted on all of them.
    for subcheck in ("presence.n_present", "presence.n_missing"):
        assert subcheck in _unsupported(outcome), f"{route}: {subcheck}"
    assert outcome.census.not_checkable == len(outcome.listings)


@pytest.mark.parametrize("route", _ROUTES)
def test_the_reason_says_what_is_missing_and_names_no_spelling(
    witnesses: "dict[str, Witness]", route: str
) -> None:
    """V5.4's rule, on the sentence this repair adds.

    The reason states counts the description publishes. It never states
    a spelling -- not the person's, whose text may be their data, and
    not this package's own, which would tell a reader which word the
    description's key is.
    """
    witness = witnesses[route]
    outcome = validation.measure(witness.described, witness.path)
    spoken = [
        listing.reason
        for listing in outcome.listings
        if listing.reason.endswith(validation.UNREBUILDABLE_REASON_TAIL)
    ]
    assert spoken, route
    whole = " ".join(spoken)
    assert witness.marker not in whole, route
    assert _POOL_WORD not in whole, route
    assert _SHOWN not in whole, route
    for reason in spoken:
        assert reason.startswith("the description "), reason


# -- the controls the union is judged on --------------------------------


@pytest.mark.parametrize("route", ["recovered", "nothing-named"])
def test_a_description_that_can_be_read_back_loses_nothing(
    witnesses: "dict[str, Witness]", route: str
) -> None:
    """The union is sound as well as complete, on the two clean cases.

    One table naming a word that comes back cleanly, and one naming no
    word at all. Neither is flagged, neither loses a check, and neither
    misses anything.
    """
    witness = witnesses[route]
    assert validation.unrebuildable_columns(witness.described) == {}, route
    outcome = validation.measure(witness.described, witness.path)
    assert _missed(outcome) == [], route
    assert _unsupported(outcome) == [], route
    assert "presence.n_present" in _checked(outcome), route


def test_the_head_count_over_fires_on_a_word_the_table_never_held(
    witnesses: "dict[str, Witness]",
) -> None:
    """THE COST OF THE UNION, asserted at its size rather than hoped away.

    Two words named, one of them in no cell of the table. The rule IS
    rebuilt -- every word the table held comes back -- and the head
    count reports a gap anyway, because the settings block says two and
    the description carries one. The column's obligations move.

    This is the over-fire the ruling was taken with its eyes open, and
    its direction is the safe one: obligations become not-checkable on a
    file that would have passed. Narrowing it needs the description to
    say which named words the table held, which is a change to what a
    description publishes and not a change to this module.
    """
    witness = witnesses["named-but-absent"]
    assert witness.described.settings.declared_missing_values.n_declared == 2
    assert validation.declared_spellings(witness.described) == ("XX",)
    flagged = validation.unrebuildable_columns(witness.described)
    assert sorted(flagged) == ["reading"]
    outcome = validation.measure(witness.described, witness.path)
    assert _missed(outcome) == []
    assert "presence.n_present" in _unsupported(outcome)


def test_a_column_no_declared_word_reached_keeps_every_check(
    tmp_path: pathlib.Path,
) -> None:
    """The one place the head count is held back, and it is a proof.

    Two columns, one word named. The notes hold it; the readings never
    do, and the description says so -- their `missing_by_class` publishes
    no declared hole and no pooled remainder, and the producer counts
    every absent cell into one of those. A word no cell of that column
    wore cannot change how that column reads, so its obligations stay
    checks.
    """
    rows = []
    numbers = _numbers(60)
    notes = _comments(60, 50)
    for index in range(72):
        first = numbers[index % len(numbers)]
        second = notes[index] if index < 60 else "ZZZ"
        rows = rows + [[first, second]]
    described, path, _document = _described(
        tmp_path,
        "two-columns",
        fixtures.rows_to_csv(["reading", "note"], rows),
        taxonomy.Settings(declared_missing_values=("ZZZ",)),
    )
    readings, note = described.columns
    assert readings.missing_by_class.declared_missing == 0
    assert readings.missing_by_class.withheld == 0
    assert sorted(validation.unrebuildable_columns(described)) == [note.name]
    outcome = validation.measure(described, path)
    assert _missed(outcome) == []
    kept = {
        check.subcheck for check in outcome.checks if check.column == readings.name
    }
    assert "presence.n_present" in kept
    assert "ladder.min" in kept
    moved = {
        listing.column
        for listing in outcome.listings
        if listing.reason.endswith(validation.UNREBUILDABLE_REASON_TAIL)
    }
    assert moved == {note.name}


# -- the rule is a function of the description, and of nothing else -----


def test_two_files_one_description_cannot_tell_apart_get_one_answer(
    tmp_path: pathlib.Path,
) -> None:
    """V5.1, on the confidentiality form of the class-word collision.

    World A holds twelve cells that literally read this package's word
    for the pooled remainder, under one declaration. World B holds
    twelve cells spread over four rare spellings, every one of them
    below the floor and therefore pooled into that same word. The two
    descriptions are byte for byte alike, and the round-8 finding is
    that the two REPORTS were not: one printed a raw distinctness of 61
    and the other 72, off the same description.

    Both reports are the same report now, achieved values and all,
    because the obligations that told them apart are obligations this
    description cannot support asking.
    """
    first, first_path, first_document = _described(
        tmp_path,
        "world-a",
        _numeric_table([_POOL_WORD] * 12),
        taxonomy.Settings(declared_missing_values=(_POOL_WORD,)),
    )
    second, second_path, second_document = _described(
        tmp_path,
        "world-b",
        # Twelve edge-space variants of one spelling: the declaration
        # matches every one of them, and each is worn by a single cell,
        # so every one is below the floor and all twelve are pooled.
        _numeric_table([" " * (index + 1) + _POOL_WORD for index in range(12)]),
        taxonomy.Settings(declared_missing_values=(_POOL_WORD,)),
    )
    assert canonical.serialize(first_document) == canonical.serialize(
        second_document
    )
    assert first.columns[0].missing_by_source == {_POOL_WORD: 12}
    assert second.columns[0].missing_by_source == {_POOL_WORD: 12}
    here = validation.measure(first, first_path)
    there = validation.measure(first, second_path)
    assert [
        (check.subcheck, check.verdict, check.published, check.achieved)
        for check in here.checks
    ] == [
        (check.subcheck, check.verdict, check.published, check.achieved)
        for check in there.checks
    ]
    assert [
        (listing.column, listing.fact, listing.subcheck, listing.reason)
        for listing in here.listings
    ] == [
        (listing.column, listing.fact, listing.subcheck, listing.reason)
        for listing in there.listings
    ]


def test_the_same_description_moves_the_same_obligations_on_any_file(
    witnesses: "dict[str, Witness]", tmp_path: pathlib.Path
) -> None:
    """V3.3: which obligations exist is the description's question.

    The free-text witness measured against its own table, against a
    table of the same shape holding no marker at all, and against its
    own twin. Three different files, one description, one split between
    what is checked and what is named -- because nothing about a
    measured file may decide which of its own obligations run.
    """
    witness = witnesses["free-text"]
    plain = fixtures.write(
        tmp_path, "plain.csv", _text_table(_comments(12, 50))
    )
    first = validation.measure(witness.described, witness.path)
    second = validation.measure(witness.described, str(plain))
    assert _unsupported(first) == _unsupported(second)
    assert _checked(first) == _checked(second)


def test_no_obligation_is_both_checked_and_named_unsupported(
    witnesses: "dict[str, Witness]",
) -> None:
    """V3.3's double-binding rule, on the entries this ruling adds.

    An identity that is both a verdict and a not-checkable line is
    counted twice, once in each census, and the two censuses then
    disagree about what the run did.
    """
    for route in _ROUTES:
        witness = witnesses[route]
        outcome = validation.measure(witness.described, witness.path)
        verdicted = {
            (check.column, check.fact, check.subcheck)
            for check in outcome.checks
        }
        seen: set[tuple[str, str, str]] = set()
        for listing in outcome.listings:
            identity = (listing.column, listing.fact, listing.subcheck)
            assert identity not in verdicted, f"{route}: {identity}"
            assert identity not in seen, f"{route}: listed twice {identity}"
            seen.add(identity)


def test_the_position_obligation_is_the_one_that_stays_a_check(
    witnesses: "dict[str, Witness]",
) -> None:
    """What a flagged column is still asked, and it is not nothing.

    `position.at` is measured from the file's own names and column
    count, not from any cell, so nothing the description failed to
    record can move it. It stays a check, and a file that drops the
    column still MISSES it.
    """
    witness = witnesses["free-text"]
    outcome = validation.measure(witness.described, witness.path)
    mine = [
        check.subcheck
        for check in outcome.checks
        if check.column == witness.described.columns[0].name
    ]
    assert mine == ["position.at"]
    assert outcome.checks[-1].verdict == validation.HELD


# -- what it costs, measured -------------------------------------------


def test_what_moves_on_the_free_text_witness_is_written_out(
    witnesses: "dict[str, Witness]",
) -> None:
    """THE SIZE OF THE LOWERING, so that a change to it is visible.

    The free-text witness sets thirty-one obligations a file can be
    measured against and eleven of them used to MISS. Twenty-one move
    to the not-checkable census -- every obligation of that column that
    is counted over its cells, and not only the eleven that happened to
    miss on this marker spelling. That width is the point: a longer
    marker moves `length.max` instead of `length.min`, so a rule that
    moved only the eleven would keep printing false failures for other
    spellings of the same gap.
    """
    witness = witnesses["free-text"]
    outcome = validation.measure(witness.described, witness.path)
    assert len(outcome.checks) == 10
    assert len(_unsupported(outcome)) == 21
    assert outcome.census.not_checkable == 32
    assert outcome.census.missed == 0


def test_the_twin_of_an_unreadable_description_moves_with_it(
    witnesses: "dict[str, Witness]",
) -> None:
    """THE OTHER HALF OF THE COST, and it is not avoidable here.

    The twin writes every absent cell as an empty field, so no marker
    word survives into it and the ordinary workflow was never broken by
    any of these routes. The twin's obligations move all the same,
    because which obligations a run can check is a function of the
    DESCRIPTION and the twin shares its description with the table.

    Reading the file to decide otherwise is exactly what V5.1 forbids:
    the file that conforms and the file that does not are the same file
    to this description. So the twin passes -- exit 0, nothing missed --
    with the same obligations named as unsupported, and that is stated
    rather than left to be found.
    """
    witness = witnesses["free-text"]
    table = validation.measure(witness.described, witness.path)
    folder = pathlib.Path(witness.path).parent
    twin = fixtures.write(
        folder,
        "as-a-twin.csv",
        rendering.twin_csv(generation.generate(witness.described, 0)),
    )
    twin_run = validation.measure(witness.described, str(twin))
    assert twin_run.census.missed == 0
    assert _unsupported(twin_run) == _unsupported(table)
    assert twin_run.census.not_checkable == table.census.not_checkable


def test_the_declaration_below_the_floor_is_bounded_by_the_floor(
    witnesses: "dict[str, Witness]",
) -> None:
    """Route 3's own arithmetic, so the witness is the class.

    Each of the three spellings is worn by fewer cells than the
    publication floor, which is exactly why none of them is published
    and none comes back.
    """
    witness = witnesses["pooled"]
    column = witness.described.columns[0]
    assert validation.declared_spellings(witness.described) == ()
    assert column.missing_by_source == {_POOL_WORD: 9}
    assert column.missing_by_class.withheld == 9
    assert column.missing_by_class.withheld < _FLOOR
