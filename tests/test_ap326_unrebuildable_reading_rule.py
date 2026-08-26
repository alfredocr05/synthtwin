"""A description that cannot be read back says so, and stops guessing.

THREE OF THE FIVE ROUTES ARE CLOSED AT THE ROOT SINCE CONTRACT VERSION
5, and this file is where that is measured (plan amendments A-P3-27,
A-P3-28 and A-P3-29). Routes 2 and 5 -- the escaped spelling and the two
key spaces in one map -- are gone: the description stores the spelling
character for character and keeps this package's own two counts in
fields of their own, so those witnesses are now measured in full, with
every obligation checked and nothing named unsupported. Route 1 is gone
in both halves: the description records which of this package's own
words were named, and the validator READS that record instead of
inferring the reading rule from levels and verdicts, so the rescued-word
witness is measured in full too. Routes 3 and 4 are the two contract 5
section 7 says no version of this format closes.

AND THE KEPT SIDE OF THE HEAD COUNT IS GONE WITH ROUTE 1, which is the
wider of the two costs amendment A-P3-26 wrote down. That amendment
asked its head count of EVERY column on the kept side, because no
published number said how many present cells were rescued. Contract 5
section 6.4 proves the settings block's two vocabulary lists are the
WHOLE of what a rescue can change, so the question is decided rather
than assumed and the question is not asked.

The rest of this docstring is the record of what the class was, kept as
written, because the routes that remain are the same routes.

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

THE RED CHECKS. `REINSTATE=A-P3-26` in the environment puts the
pre-ruling behaviour back -- no column is ever unrebuildable, so every
one of these witnesses re-describes the file under an incomplete rule
and reports the misses again. Every assertion below that says a witness
misses nothing goes red with it, and so does every assertion that names
an obligation as unsupported.

`REINSTATE=A-P3-29` makes the validator infer the kept side from levels
and verdicts again instead of reading the settings block, and puts the
kept-side head count back with it. The rescued witness stops being
measured in full and every column of a description that names a kept
value is flagged again, so every assertion that route 1 is closed goes
red.

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

# THE PUBLICATION FLOOR THIS FILE IS WRITTEN AT, declared rather than
# taken from the default. Route 3 is a statement ABOUT the floor -- a
# declared spelling worn by fewer cells than it is pooled, unnamed, into
# the withheld remainder -- so a witness for it only exists where the
# floor is above one. The shipped default is 1 since the owner ruling of
# 2026-08-25 (plan amendment A-P4-37), and at a floor of 1 nothing is
# ever held back at all (contract invariant C5-S13), so every witness
# below names the floor it is built against and every route is measured
# under the same rules it was written under.
_FLOOR = 11


def _kept_the_version_four_way(
    described: contract.Profile,
) -> "tuple[str, ...]":
    """`kept_spellings` as it stood before the settings block carried it."""
    found: dict[str, int] = {}
    for column in described.columns:
        for verdict in column.sentinel_verdicts:
            if verdict.reason == taxonomy.REASON_KEPT_BY_USER:
                found[verdict.candidate] = 1
        facts = column.facts
        if isinstance(facts, contract.LabelFacts):
            for level in facts.levels:
                found[level.label] = 1
                for spelling in level.variants:
                    found[spelling] = 1
    return tuple(sorted(found))


# The shipped rule, held before any patch replaces the name, so that the
# reinstatement below adds to it rather than calling itself.
_SHIPPED_UNREBUILDABLE = validation.unrebuildable_columns


def _rescued_the_version_four_way(
    described: contract.Profile,
) -> "tuple[str, ...]":
    """`rescued_spellings` as A-P3-26's kept-side head count counted it."""
    found: dict[str, int] = {}
    for column in described.columns:
        for verdict in column.sentinel_verdicts:
            if verdict.reason == taxonomy.REASON_KEPT_BY_USER:
                found[verdict.candidate] = 1
    return tuple(sorted(found))


def _with_the_kept_head_count(
    described: contract.Profile,
) -> "dict[str, str]":
    """`unrebuildable_columns` with amendment A-P3-26's kept-side half.

    Every column of a description that names more kept values than the
    one published route brought back, which under the version 4 settings
    was every column of any description naming one at all.
    """
    found = dict(_SHIPPED_UNREBUILDABLE(described))
    rescued = _rescued_the_version_four_way(described)
    named = described.settings.kept_values.n_declared
    if len(rescued) < named:
        for column in described.columns:
            if column.name not in found:
                found[column.name] = (
                    "the description says word(s) were named as meaning "
                    "real data when it was written and records fewer of "
                    "them, so " + validation.UNREBUILDABLE_REASON_TAIL
                )
    return found


@pytest.fixture(scope="module", autouse=True)
def _reinstated() -> "typing.Iterator[None]":
    """Put the pre-ruling behaviour back when REINSTATE asks for it.

    MODULE-SCOPED, because the descriptions and reports below are built
    in module-scoped fixtures and a function-scoped patch would be
    applied after they were built -- a red check run against a patch
    nobody used.
    """
    monkeypatch = pytest.MonkeyPatch()
    asked = os.environ.get("REINSTATE")
    if asked == "A-P3-26":
        monkeypatch.setattr(
            validation, "unrebuildable_columns", lambda _described: {}
        )
    if asked == "A-P3-29":
        monkeypatch.setattr(
            validation, "kept_spellings", _kept_the_version_four_way
        )
        monkeypatch.setattr(
            validation, "unrebuildable_columns", _with_the_kept_head_count
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
        taxonomy.Settings(small_cell_floor=_FLOOR, kept_values=("n/a",)),
        "n/a",
    )
    # Route 2: a declaration holding an invisible character.
    add(
        "escaped",
        "escaped",
        _numeric_table([_RAW] * 12),
        taxonomy.Settings(small_cell_floor=_FLOOR, declared_missing_values=(_RAW,)),
        _RAW,
    )
    # Route 3: declarations whose cells all sit below the floor.
    add(
        "pooled",
        "pooled",
        _numeric_table(["rare1"] * 3 + ["rare2"] * 3 + ["rare3"] * 3),
        taxonomy.Settings(
            small_cell_floor=_FLOOR,
            declared_missing_values=("rare1", "rare2", "rare3")
        ),
        "rare1",
    )
    # Route 4: a column whose publication class publishes no value.
    add(
        "free-text",
        "free-text",
        _text_table(["ZZZ"] * 12),
        taxonomy.Settings(small_cell_floor=_FLOOR, declared_missing_values=("ZZZ",)),
        "ZZZ",
    )
    # Route 5: the person's own text spelling one of this package's own
    # class words.
    add(
        "class-word",
        "class-word",
        _numeric_table([_CLASS_WORD] * 12),
        taxonomy.Settings(
            small_cell_floor=_FLOOR,
            declared_missing_values=(_CLASS_WORD,),
        ),
        _CLASS_WORD,
    )
    # Route 5, the confidentiality form: a cell literally spelling the
    # pooled remainder's own word.
    add(
        "pool-word",
        "pool-word",
        _numeric_table([_POOL_WORD] * 12),
        taxonomy.Settings(
            small_cell_floor=_FLOOR,
            declared_missing_values=(_POOL_WORD,),
        ),
        _POOL_WORD,
    )
    # The partial loss: one named word published, another pooled. This
    # is the one the structural question alone would walk past.
    add(
        "partial",
        "partial",
        _numeric_table(["XX"] * 12 + ["YY"] * 5),
        taxonomy.Settings(
            small_cell_floor=_FLOOR,
            declared_missing_values=("XX", "YY"),
        ),
        "YY",
    )
    # CONTROL: the spelling comes back cleanly.
    add(
        "recovered",
        "recovered",
        _numeric_table(["XX"] * 12),
        taxonomy.Settings(small_cell_floor=_FLOOR, declared_missing_values=("XX",)),
        "XX",
    )
    # CONTROL: no word named at all.
    add(
        "nothing-named",
        "nothing-named",
        _numeric_table([""] * 12),
        taxonomy.Settings(small_cell_floor=_FLOOR),
        "",
    )
    # THE OVER-FIRE, asserted rather than hoped away: a word named that
    # the table never held.
    add(
        "named-but-absent",
        "named-but-absent",
        _numeric_table(["XX"] * 12),
        taxonomy.Settings(
            small_cell_floor=_FLOOR,
            declared_missing_values=("XX", "NEVERHERE"),
        ),
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

# The routes a description still cannot be read back on. Three left
# this tuple at contract version 5 and are asserted closed below, which
# is why they are named there rather than deleted: a route that stopped
# being tested is a route nobody would notice reopening.
_ROUTES = (
    "pooled",
    "free-text",
    "partial",
)

# The three the format change closed, and what each one was.
_CLOSED_BY_VERSION_5 = (
    # Route 2: the key crossed the display boundary before it was
    # stored, so two tables described alike (contract 5 C5-1).
    "escaped",
    # Route 5: the person's text and this package's class words shared
    # one key space (contract 5 C5-11, C5-N5).
    "class-word",
    "pool-word",
)

# And the one the VALIDATOR stage closed, which is a route of the same
# five and is separated only because the format closed it one commit
# earlier than the validator read it (plan amendment A-P3-29). Route 1:
# the settings block carries which of this package's own words were
# named, and `kept_spellings` reads it instead of inferring the tuple
# from levels and verdicts.
_CLOSED_BY_THE_VALIDATOR = ("rescued",)

_CLOSED = _CLOSED_BY_VERSION_5 + _CLOSED_BY_THE_VALIDATOR


@pytest.mark.parametrize("route", _CLOSED)
def test_the_routes_version_five_closed_are_measured_in_full(
    witnesses: "dict[str, Witness]", route: str
) -> None:
    """No column is flagged, and every obligation is a check again.

    These four were listed as ones the description could not support
    asking. The description supports them now, so the not-checkable
    census holds only the REPORT-ONLY facts every run carries and the
    presence counts are measured against the file.
    """
    witness = witnesses[route]
    assert validation.unrebuildable_columns(witness.described) == {}, route
    outcome = validation.measure(witness.described, witness.path)
    assert _missed(outcome) == [], route
    assert _unsupported(outcome) == [], route
    for subcheck in ("presence.n_present", "presence.n_missing"):
        assert subcheck in _checked(outcome), f"{route}: {subcheck}"


@pytest.mark.parametrize("route", _CLOSED_BY_VERSION_5)
def test_the_spelling_those_routes_needed_is_in_the_description(
    witnesses: "dict[str, Witness]", route: str
) -> None:
    """And it is there exactly, which is what made the difference.

    Each of these three tables wears a marker version 4 could not write
    down: one holds a character the display boundary shows, and two hold
    text identical to one of this package's own class words. Version 5
    writes each of them as the cells wore it.
    """
    witness = witnesses[route]
    column = witness.described.columns[0]
    assert column.missing_by_source == {witness.marker: 12}, route
    assert validation.declared_spellings(witness.described) == (
        witness.marker,
    ), route


@pytest.mark.parametrize("route", _CLOSED_BY_THE_VALIDATOR)
def test_the_word_route_one_needed_is_in_the_settings_block(
    witnesses: "dict[str, Witness]", route: str
) -> None:
    """And no column of the description carries it, which was the point.

    Route 1's witness rescues one of this package's own ten words on a
    column of numbers. No level, no variant and no sentinel verdict can
    hold that word, so the three routes the validator used to infer the
    kept side from bring back nothing at all. The settings block names
    the vocabulary member, and the validator reads it there.

    THE KEPT-SIDE HEAD COUNT IS GONE WITH IT, and that is asserted by
    the flag list being empty rather than by the absence of a branch:
    under amendment A-P3-26 this description flagged EVERY column,
    because no published number said how many present cells were
    rescued. One does now.
    """
    witness = witnesses[route]
    assert _kept_the_version_four_way(witness.described) == (), route
    assert witness.described.settings.kept_values.built_in_texts == (
        witness.marker,
    ), route
    assert validation.kept_spellings(witness.described) == (
        witness.marker,
    ), route
    assert validation.unrebuildable_columns(witness.described) == {}, route


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
        taxonomy.Settings(small_cell_floor=_FLOOR, declared_missing_values=("ZZZ",)),
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


def test_the_two_worlds_of_the_pool_word_now_describe_differently(
    tmp_path: pathlib.Path,
) -> None:
    """The confidentiality form of the class-word collision, closed.

    World A holds twelve cells that literally read this package's word
    for the pooled remainder, under one declaration. World B holds
    twelve cells spread over rare spellings, every one of them below the
    floor and therefore pooled. Under version 4 both published
    `missing_by_source = {"(withheld)": 12}`, the two descriptions came
    out byte for byte alike, and the round-8 finding was that the two
    REPORTS were not: one printed a raw distinctness of 61 and the other
    72, off the same description.

    CONTRACT VERSION 5 GIVES THE MAP ONE KEY SPACE (its C5-11, C5-N5).
    World A's key is the table's own text and means twelve cells wore
    it; world B names no key at all and says twelve cells are pooled, in
    `n_missing_withheld`. The two descriptions are different files, and
    each is read under its own rule: A is measured in full, and B keeps
    the not-checkable treatment that the floor's own limit calls for
    (route 3, contract 5 section 7.2).
    """
    first, first_path, first_document = _described(
        tmp_path,
        "world-a",
        _numeric_table([_POOL_WORD] * 12),
        taxonomy.Settings(
            small_cell_floor=_FLOOR,
            declared_missing_values=(_POOL_WORD,),
        ),
    )
    second, second_path, second_document = _described(
        tmp_path,
        "world-b",
        # Twelve edge-space variants of one spelling: the declaration
        # matches every one of them, and each is worn by a single cell,
        # so every one is below the floor and all twelve are pooled.
        _numeric_table([" " * (index + 1) + _POOL_WORD for index in range(12)]),
        taxonomy.Settings(
            small_cell_floor=_FLOOR,
            declared_missing_values=(_POOL_WORD,),
        ),
    )
    assert canonical.serialize(first_document) != canonical.serialize(
        second_document
    )
    assert first.columns[0].missing_by_source == {_POOL_WORD: 12}
    assert first.columns[0].n_missing_withheld == 0
    assert second.columns[0].missing_by_source == {}
    assert second.columns[0].n_missing_withheld == 12
    # World A is read back exactly, so its own table is measured in
    # full and misses nothing.
    here = validation.measure(first, first_path)
    assert _missed(here) == []
    assert _unsupported(here) == []
    assert "presence.n_present" in _checked(here)
    # World B's twelve spellings are all below the floor, which is the
    # one thing no version of this format publishes, so its own
    # description still cannot support asking those obligations.
    there = validation.measure(second, second_path)
    assert _missed(there) == []
    assert "presence.n_present" in _unsupported(there)


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
    # THIRTY-FOUR, AND THE TWO THAT ARRIVED ARE NOT THIS RULING'S. The
    # census also carries every REPORT-ONLY fact of the description, and
    # contract version 5 added two of them to every column --
    # `n_missing_blank` and `n_missing_withheld`, which the twin owes
    # nothing (plan amendment A-P3-28). The numbers this ruling is
    # measured by are the two above: ten checks left, twenty-one moved.
    assert outcome.census.not_checkable == 34
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
    # THE POOLED REMAINDER IS A FIELD OF ITS OWN from contract version 5
    # (its section 5), so the map names nothing at all here and the
    # count says how many cells it does not name. What the floor does is
    # unchanged: nine cells, three spellings, none of them named.
    assert column.missing_by_source == {}
    assert column.n_missing_withheld == 9
    assert column.missing_by_class.withheld == 9
    assert column.missing_by_class.withheld < _FLOOR
