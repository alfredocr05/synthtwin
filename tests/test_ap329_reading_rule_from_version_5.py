"""The validator rebuilds the reading rule from what version 5 records.

PLAN AMENDMENT A-P3-29, carrying out the owner's ruling of 2026-08-17
on the half of it the producer stage left open. Contract version 5
records the reading rule; until this stage the validator still rebuilt
it the version 4 way, by INFERRING the declarations from facts a
description publishes for other reasons. This file measures the four
things that changed and the two that did not.

WHAT CHANGED.

1. **The kept side is READ, not inferred.** `kept_spellings` returns
   `settings.kept_values`'s two vocabulary lists and consults no column.
   Contract 5 section 6.4 proves those lists are the WHOLE of what a
   `--keep-value` can change about any cell's reading, so the three
   routes it replaced -- a `kept_by_you` verdict, a level's label, a
   level's `variants` keys -- are deleted rather than kept beside.
2. **The kept side of the head count is gone with them.** Amendment
   A-P3-26 asked it of EVERY column, "because no published number says
   how many present cells were rescued", and called it the wider of its
   two costs. One says now.
3. **The absence side reads the vocabulary lists too**, so a built-in
   word or a stand-in number somebody named as "no value" comes back
   whatever the floor did with its cells, and the head count asks only
   about words of the PERSON'S own.
4. **Two narrowings of the per-column structural test.** It is not
   asked on a column whose publication class empties its source
   accounting -- there is nothing there to read, and asking anyway made
   every declared hole of such a column look unattributable even where
   the word is in the settings block (contract 5 C5-N6). And it matches
   a published key to a recovered declaration at the PRODUCER'S own
   identity -- the exact number where both read as one, else the
   trimmed and folded spelling -- rather than by exact key lookup.

WHAT DID NOT CHANGE, and both are asserted here at the same width.
Contract 5 section 7's two limits stand: a word of the person's own
pooled below `small_cell_floor`, and a word of the person's own on a
column that publishes no value of the table. On those, A-P3-26's two
residual risks stand with them -- a file that really does violate a
moved obligation comes back at exit 0, and the TWIN of such a
description carries the same limit as the table.

THE RED CHECKS. Every test below goes red under one of six
reinstatements, each of which puts back exactly one thing this stage
changed:

    REINSTATE=A-P3-29-K   the kept side is inferred again, and the
                          kept-side head count comes back with it
    REINSTATE=A-P3-29-D   the absence side stops reading the two
                          vocabulary lists
    REINSTATE=A-P3-29-H   the head count counts every declared word
                          instead of the person's own
    REINSTATE=A-P3-29-S   the structural test is asked on a column whose
                          class empties its source accounting
    REINSTATE=A-P3-29-M   the structural test matches a key by exact
                          lookup instead of the producer's identity
    REINSTATE=A-P3-29-T   the structural test is not asked at all

Every table is built at test time by the seeded neutral builders in
`fixtures.py`; no data-format file enters the repository (plan D13).
"""

import os
import pathlib
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

_FLOOR = taxonomy.Settings().small_cell_floor

# The shipped rules, held before any patch replaces their names, so that
# a reinstatement can build on them instead of calling itself.
_SHIPPED_UNREBUILDABLE = validation.unrebuildable_columns
_SHIPPED_DECLARED = validation.declared_spellings
_SHIPPED_HOLES = validation._holes_no_spelling_accounts_for


# -- the reinstatements -------------------------------------------------


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


def _rescued_the_version_four_way(
    described: contract.Profile,
) -> "tuple[str, ...]":
    """`rescued_spellings` as amendment A-P3-26's head count counted it.

    The one published route that exists only where somebody rescued a
    value: a sentinel verdict reading `kept_by_you`. A rescue on a LABEL
    column reaches the description as a level and never as a verdict, so
    this undercounted, and the head count built on it fired on every
    column of any description naming a kept value at all.
    """
    found: dict[str, int] = {}
    for column in described.columns:
        for verdict in column.sentinel_verdicts:
            if verdict.reason == taxonomy.REASON_KEPT_BY_USER:
                found[verdict.candidate] = 1
    return tuple(sorted(found))


def _with_the_kept_head_count(
    described: contract.Profile,
) -> "dict[str, str]":
    """`unrebuildable_columns` with amendment A-P3-26's kept-side half."""
    found = dict(_SHIPPED_UNREBUILDABLE(described))
    rescued = _rescued_the_version_four_way(described)
    if len(rescued) < described.settings.kept_values.n_declared:
        for column in described.columns:
            if column.name not in found:
                found[column.name] = (
                    "the description says word(s) were named as meaning "
                    "real data when it was written and records fewer of "
                    "them, so " + validation.UNREBUILDABLE_REASON_TAIL
                )
    return found


def _declared_from_the_columns_only(
    described: contract.Profile,
) -> "tuple[str, ...]":
    """`declared_spellings` without version 5's settings-block route."""
    return validation._named_in_the_columns(described)


def _head_count_over_every_declared_word(
    described: contract.Profile,
) -> "dict[str, str]":
    """The head count asked about every named word, not the person's own."""
    found: dict[str, str] = {}
    recovered = _SHIPPED_DECLARED(described)
    named = described.settings.declared_missing_values.n_declared
    back = len(validation._named_in_the_columns(described))
    for column in described.columns:
        if not validation._publishes_no_source_accounting(column):
            unnamed = _SHIPPED_HOLES(column, recovered)
            if unnamed > 0:
                found[column.name] = validation._holes_no_word_accounts_for(
                    unnamed
                )
                continue
        if back < named and validation._a_declaration_could_reach(column):
            found[column.name] = validation._absence_words_not_recorded(
                named, back
            )
    return found


def _asked_on_every_column(described: contract.Profile) -> "dict[str, str]":
    """The structural test asked where the class empties the accounting."""
    found: dict[str, str] = {}
    recovered = _SHIPPED_DECLARED(described)
    named = validation._own_words_named(
        described.settings.declared_missing_values
    )
    back = len(validation._named_in_the_columns(described))
    for column in described.columns:
        unnamed = _SHIPPED_HOLES(column, recovered)
        if unnamed > 0:
            found[column.name] = validation._holes_no_word_accounts_for(
                unnamed
            )
            continue
        if back < named and validation._a_declaration_could_reach(column):
            found[column.name] = validation._absence_words_not_recorded(
                named, back
            )
    return found


def _matched_by_exact_lookup(
    column: contract.ColumnBlock, recovered: "tuple[str, ...]"
) -> int:
    """The structural test's version 4 arithmetic: look the key up."""
    accounted = 0
    for spelling in recovered:
        if spelling in column.missing_by_source:
            accounted = accounted + column.missing_by_source[spelling]
    return max(0, column.missing_by_class.declared_missing - accounted)


def _never_asked(
    _column: contract.ColumnBlock, _recovered: "tuple[str, ...]"
) -> int:
    """The structural test removed, leaving the head count alone."""
    return 0


@pytest.fixture(scope="module", autouse=True)
def _reinstated() -> "typing.Iterator[None]":
    """Put one part of the version 4 reconstruction back on request.

    MODULE-SCOPED, because the descriptions below are built in
    module-scoped fixtures and a function-scoped patch would be applied
    after they were built -- a red check run against a patch nobody
    used.
    """
    monkeypatch = pytest.MonkeyPatch()
    asked = os.environ.get("REINSTATE")
    if asked == "A-P3-29-K":
        monkeypatch.setattr(
            validation, "kept_spellings", _kept_the_version_four_way
        )
        monkeypatch.setattr(
            validation, "unrebuildable_columns", _with_the_kept_head_count
        )
    if asked == "A-P3-29-D":
        monkeypatch.setattr(
            validation, "declared_spellings", _declared_from_the_columns_only
        )
    if asked == "A-P3-29-H":
        monkeypatch.setattr(
            validation,
            "unrebuildable_columns",
            _head_count_over_every_declared_word,
        )
    if asked == "A-P3-29-S":
        monkeypatch.setattr(
            validation, "unrebuildable_columns", _asked_on_every_column
        )
    if asked == "A-P3-29-M":
        monkeypatch.setattr(
            validation,
            "_holes_no_spelling_accounts_for",
            _matched_by_exact_lookup,
        )
    if asked == "A-P3-29-T":
        monkeypatch.setattr(
            validation, "_holes_no_spelling_accounts_for", _never_asked
        )
    yield
    monkeypatch.undo()


# -- the builders -------------------------------------------------------


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


class Case(typing.NamedTuple):
    """One description, the table it was written from, and its path."""

    described: contract.Profile
    path: str
    folder: pathlib.Path


def _described(
    folder: pathlib.Path,
    stem: str,
    text: str,
    settings: taxonomy.Settings,
) -> Case:
    """One table through the real producer, loader and all."""
    path = fixtures.write(folder, f"{stem}.csv", text)
    table = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(table, settings, [])
    loaded = contract.load_profile(
        str(fixtures.write_profile(folder, f"{stem}-profile.json", document))
    )
    return Case(loaded, str(path), folder)


def _numeric(
    folder: pathlib.Path,
    stem: str,
    markers: "list[str]",
    settings: taxonomy.Settings,
) -> Case:
    """Sixty readings, then one cell per marker spelling given."""
    return _described(
        folder,
        stem,
        fixtures.single_column_table("reading", _numbers(60) + markers),
        settings,
    )


def _free_text(
    folder: pathlib.Path,
    stem: str,
    markers: "list[str]",
    settings: taxonomy.Settings,
) -> Case:
    """Sixty comments, then one cell per marker spelling given."""
    return _described(
        folder,
        stem,
        fixtures.single_column_table("note", _comments(60, 50) + markers),
        settings,
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


def _held(outcome: validation.Outcome) -> "set[str]":
    """The subchecks one run carried a HELD verdict on."""
    return {
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.HELD
    }


# -- 1. the kept side is read rather than inferred ----------------------


def test_the_rescued_word_is_read_out_of_the_settings_block(
    tmp_path: pathlib.Path,
) -> None:
    """The review's own witness, measured in full.

    Two hundred readings and one `n/a`, described `--keep-value n/a`.
    No level, no variant and no sentinel verdict of this description can
    carry the word, so the three routes the kept tuple used to be
    inferred from bring back nothing. The settings block names the
    vocabulary member, and that is what is read.
    """
    case = _described(
        tmp_path,
        "rescued",
        fixtures.single_column_table("reading", _numbers(200) + ["n/a"]),
        taxonomy.Settings(kept_values=("n/a",)),
    )
    assert _kept_the_version_four_way(case.described) == ()
    assert validation.kept_spellings(case.described) == ("n/a",)
    assert validation.settings_for(case.described).kept_values == ("n/a",)
    assert validation.unrebuildable_columns(case.described) == {}
    outcome = validation.measure(case.described, case.path)
    assert outcome.census.missed == 0
    assert _unsupported(outcome) == []
    assert "presence.n_present" in _held(outcome)


def test_a_rescued_number_needs_no_sentinel_verdict_to_come_back(
    tmp_path: pathlib.Path,
) -> None:
    """The `kept_by_you` route is a subset of what is read now.

    A candidate exists only for one of the three stand-in numbers, and
    it reads `kept_by_you` only where a `--keep-value` named it. So the
    route brought back nothing the two vocabulary lists do not, and the
    lists reach one case it never did: a rescued stand-in on a column
    that publishes no candidate at all, because no cell of it wore one.
    """
    case = _numeric(
        tmp_path, "kept-number", ["-999"] * 12, taxonomy.Settings(
            kept_values=("-999",)
        )
    )
    assert validation.kept_spellings(case.described) == ("-999",)
    assert case.described.settings.kept_values.built_in_numbers == (-999.0,)
    outcome = validation.measure(case.described, case.path)
    assert outcome.census.missed == 0
    assert _unsupported(outcome) == []
    # ...and where the table holds no such cell, the list is written all
    # the same, so nothing is flagged there either (contract 5 C5-16).
    absent = _numeric(
        tmp_path, "kept-number-absent", [], taxonomy.Settings(
            kept_values=("-999",)
        )
    )
    assert absent.described.columns[0].sentinel_verdicts == ()
    assert validation.kept_spellings(absent.described) == ("-999",)
    assert validation.unrebuildable_columns(absent.described) == {}


def test_the_kept_side_of_the_head_count_is_gone(
    tmp_path: pathlib.Path,
) -> None:
    """A-P3-26's wider cost, withdrawn because the question is decided.

    A rescued word on a LABEL column reached the description as a level
    and never as a verdict, so the count that head count compared was a
    LOWER bound and it fired on every column of the document. Contract 5
    section 6.4 proves the settings block carries the whole of the kept
    side, so there is nothing left to be short of.
    """
    case = _described(
        tmp_path,
        "kept-label",
        fixtures.single_column_table(
            "grade", ["alpha"] * 30 + ["bravo"] * 30 + ["n/a"] * 12
        ),
        taxonomy.Settings(kept_values=("n/a",)),
    )
    assert case.described.settings.kept_values.n_declared == 1
    assert validation.unrebuildable_columns(case.described) == {}
    outcome = validation.measure(case.described, case.path)
    assert outcome.census.missed == 0
    assert _unsupported(outcome) == []


# -- 2. the absence side reads the same record --------------------------


def test_a_named_built_in_word_comes_back_where_no_column_names_it(
    tmp_path: pathlib.Path,
) -> None:
    """Contract 5 C5-20, on the column class that publishes no value.

    A free-text column publishes an empty source accounting whatever
    made its cells absent, so a `--missing-value` on it is recoverable
    only from the settings block. Where the word is one of this
    package's own, it is there -- and the column is measured in full,
    which is the difference between naming `n/a` and naming `ZZZ`.
    """
    mine = _free_text(
        tmp_path, "text-vocab", ["n/a"] * 12, taxonomy.Settings(
            declared_missing_values=("n/a",)
        )
    )
    column = mine.described.columns[0]
    assert column.missing_by_source == {}
    assert column.missing_by_class.declared_missing == 12
    assert validation.declared_spellings(mine.described) == ("n/a",)
    assert validation.unrebuildable_columns(mine.described) == {}
    outcome = validation.measure(mine.described, mine.path)
    assert outcome.census.missed == 0
    assert _unsupported(outcome) == []
    # ...and the person's own word on the same column is contract 5
    # section 7.1's limit, which no version of the format closes.
    theirs = _free_text(
        tmp_path, "text-own", ["ZZZ"] * 12, taxonomy.Settings(
            declared_missing_values=("ZZZ",)
        )
    )
    assert validation.declared_spellings(theirs.described) == ()
    assert sorted(validation.unrebuildable_columns(theirs.described)) == [
        "note"
    ]


def test_a_named_stand_in_number_comes_back_as_a_declaration(
    tmp_path: pathlib.Path,
) -> None:
    """The skip that used to be a loss.

    A key reading as one of the three stand-ins is the sentinel
    machinery's business, so `declared_spellings` walks past it -- and
    under version 4 a DECLARED stand-in walked past with it. The
    settings block answers the question outright now, and the spelling
    this module hands the producer denotes the member exactly, which is
    all the producer's matching rule asks.
    """
    case = _numeric(
        tmp_path, "declared-number", ["-999"] * 12, taxonomy.Settings(
            declared_missing_values=("-999",)
        )
    )
    assert case.described.settings.declared_missing_values.built_in_numbers == (
        -999.0,
    )
    assert validation.declared_spellings(case.described) == ("-999",)
    assert validation.unrebuildable_columns(case.described) == {}
    outcome = validation.measure(case.described, case.path)
    assert outcome.census.missed == 0
    assert _unsupported(outcome) == []


def test_every_stand_in_spelling_denotes_its_own_member(
    tmp_path: pathlib.Path,
) -> None:
    """The table that turns a recorded NUMBER into a settings SPELLING.

    Contract 5 records `built_in_numbers` as numbers and the producer's
    settings take spellings, so this module pairs each of the three with
    a spelling. A pairing that denoted a different number would apply
    somebody's declaration to the wrong cells, and a pairing that missed
    a member would drop the declaration entirely.
    """
    paired = [value for value, _spelling in validation._STAND_IN_SPELLINGS]
    assert paired == list(parsing.NUMERIC_SENTINELS)
    for value, spelling in validation._STAND_IN_SPELLINGS:
        assert taxonomy.exact_of_spelling(
            spelling
        ) == taxonomy.exact_of_number(value)
    # ...and each of them, declared, is applied to the cells that wear
    # it however the file spells them.
    for value, _spelling in validation._STAND_IN_SPELLINGS:
        stem = f"stand-in-{paired.index(value)}"
        case = _numeric(
            tmp_path,
            stem,
            [f"{value:.1f}"] * 12,
            taxonomy.Settings(declared_missing_values=(f"{value:g}",)),
        )
        assert case.described.columns[0].missing_by_class.declared_missing == 12
        assert validation.unrebuildable_columns(case.described) == {}
        outcome = validation.measure(case.described, case.path)
        assert outcome.census.missed == 0, stem
        assert _unsupported(outcome) == [], stem


def test_the_head_count_asks_only_about_words_of_your_own(
    tmp_path: pathlib.Path,
) -> None:
    """A vocabulary word below the floor is still the whole rule.

    Five cells wearing a built-in word the person named as "no value".
    The class falls below the publication floor, so no spelling of it is
    named anywhere in the column -- and the reading rule is rebuilt
    exactly all the same, because the word is one of this package's own
    and the settings block says it was typed.
    """
    case = _numeric(
        tmp_path, "vocab-pooled", ["n/a"] * 5, taxonomy.Settings(
            declared_missing_values=("n/a",)
        )
    )
    column = case.described.columns[0]
    assert column.missing_by_source == {}
    assert column.n_missing_withheld == 5
    assert column.missing_by_class.withheld == 5
    assert 5 < _FLOOR
    assert validation._own_words_named(
        case.described.settings.declared_missing_values
    ) == 0
    assert validation.unrebuildable_columns(case.described) == {}
    outcome = validation.measure(case.described, case.path)
    assert outcome.census.missed == 0
    assert _unsupported(outcome) == []


# -- 3. the two narrowings of the structural test -----------------------


def test_the_structural_test_matches_at_the_producers_own_identity(
    tmp_path: pathlib.Path,
) -> None:
    """Both halves of `declaration_matching`, each with its own witness.

    A recovered declaration and a published key are the same when they
    denote the same NUMBER, and otherwise when their folded SPELLINGS
    are equal. Exact key lookup asked a narrower question than the
    producer asked and answered it wrongly on both halves: the number
    comes back from the settings block written `-999` while the file
    wrote `-999.00`, and a word typed `" N/A "` comes back as the member
    `n/a` while the file wrote `N/A`.
    """
    numeric = _numeric(
        tmp_path, "spelled-out", ["-999.0"] * 12, taxonomy.Settings(
            declared_missing_values=("-999",)
        )
    )
    assert numeric.described.columns[0].missing_by_source == {"-999.0": 12}
    assert validation.declared_spellings(numeric.described) == ("-999",)
    assert validation._holes_no_spelling_accounts_for(
        numeric.described.columns[0], ("-999",)
    ) == 0
    assert validation.unrebuildable_columns(numeric.described) == {}
    textual = _numeric(
        tmp_path, "cased", ["N/A"] * 12, taxonomy.Settings(
            declared_missing_values=(" N/A ",)
        )
    )
    assert textual.described.columns[0].missing_by_source == {"N/A": 12}
    assert validation.declared_spellings(textual.described) == ("n/a",)
    assert validation.unrebuildable_columns(textual.described) == {}
    for case in (numeric, textual):
        outcome = validation.measure(case.described, case.path)
        assert outcome.census.missed == 0
        assert _unsupported(outcome) == []


def test_the_structural_test_is_not_asked_where_the_class_empties_it(
    tmp_path: pathlib.Path,
) -> None:
    """Contract 5 C5-N6, applied where it is decidable and nowhere else.

    A column whose publication class permits no value of the table
    publishes no key, no blank count and no pooled count -- because of
    its CLASS and not because of its cells. There is nothing there for a
    count-against-count test to read, so it is not asked, and the head
    count answers for that column instead. Asking it anyway called every
    declared hole unattributable even where the word is in the settings
    block.
    """
    case = _free_text(
        tmp_path, "class-empty", ["n/a"] * 12, taxonomy.Settings(
            declared_missing_values=("n/a",)
        )
    )
    column = case.described.columns[0]
    assert validation._publishes_no_source_accounting(column)
    assert column.missing_by_source == {}
    assert column.n_missing_blank == 0
    assert column.n_missing_withheld == 0
    assert column.missing_by_class.declared_missing == 12
    # The test that is not asked would have found twelve unattributable
    # cells; the rule that is asked finds the word in the settings.
    assert validation._holes_no_spelling_accounts_for(column, ("n/a",)) == 12
    assert validation.unrebuildable_columns(case.described) == {}


def test_the_structural_test_still_catches_a_word_the_head_count_misses(
    tmp_path: pathlib.Path,
) -> None:
    """Why the union is still a union, and it is a soundness bound.

    A declaration is matched by its folded spelling, so ONE declared
    word can be worn by several different published keys. Here `XX` is
    worn by two -- with edge space and without -- so two keys come back
    for two words named and the head count comes out level, while `YY`
    is worn by five cells, pooled below the floor, and lost. The
    structural test counts CELLS and sees it.
    """
    case = _numeric(
        tmp_path,
        "masked",
        [" XX "] * 12 + ["XX"] * 12 + ["YY"] * 5,
        taxonomy.Settings(declared_missing_values=("XX", "YY")),
    )
    column = case.described.columns[0]
    assert sorted(column.missing_by_source) == [" XX ", "XX"]
    assert column.n_missing_withheld == 5
    assert column.missing_by_class.declared_missing == 29
    # The head count is satisfied: two words of the person's own named,
    # two spellings back.
    assert validation._own_words_named(
        case.described.settings.declared_missing_values
    ) == 2
    assert len(validation._named_in_the_columns(case.described)) == 2
    # ...and five cells no recovered word accounts for say otherwise.
    assert validation._holes_no_spelling_accounts_for(
        column, validation.declared_spellings(case.described)
    ) == 5
    assert sorted(validation.unrebuildable_columns(case.described)) == [
        "reading"
    ]
    outcome = validation.measure(case.described, case.path)
    assert outcome.census.missed == 0
    assert "presence.n_present" in _unsupported(outcome)


# -- 4. what did NOT change --------------------------------------------


def test_the_two_limits_contract_five_states_are_still_the_two(
    tmp_path: pathlib.Path,
) -> None:
    """Contract 5 section 7, unchanged by anything in this stage.

    A word of the person's own pooled below the floor, and a word of the
    person's own on a column that publishes no value of the table. Each
    still moves its column's cell-counted obligations to the
    not-checkable census, and each still leaves `position.at` a check.
    """
    pooled = _numeric(
        tmp_path,
        "pooled",
        ["rare1"] * 3 + ["rare2"] * 3 + ["rare3"] * 3,
        taxonomy.Settings(declared_missing_values=("rare1", "rare2", "rare3")),
    )
    text = _free_text(
        tmp_path, "own-word", ["ZZZ"] * 12, taxonomy.Settings(
            declared_missing_values=("ZZZ",)
        )
    )
    for case, name in ((pooled, "reading"), (text, "note")):
        assert sorted(validation.unrebuildable_columns(case.described)) == [
            name
        ]
        outcome = validation.measure(case.described, case.path)
        assert outcome.census.missed == 0, name
        assert "presence.n_present" in _unsupported(outcome), name
        mine = [
            check.subcheck
            for check in outcome.checks
            if check.column == name
        ]
        assert mine == ["position.at"], name


def test_the_over_fire_of_the_head_count_stays_and_says_whose_words(
    tmp_path: pathlib.Path,
) -> None:
    """The cost of the union, at its size, in the sentence a person reads.

    Two words of the person's own named, one of them in no cell of the
    table. The rule IS rebuilt and the head count reports a gap anyway,
    because the settings block says two and the description carries one.
    The direction is the safe one. What changed is the sentence: it
    counts the words that were the PERSON'S, because a word of this
    package's own is written down whatever the floor did and counting it
    here would report a shortfall that is not one.
    """
    case = _numeric(
        tmp_path, "never-here", ["XX"] * 12, taxonomy.Settings(
            declared_missing_values=("XX", "NEVERHERE")
        )
    )
    assert case.described.settings.declared_missing_values.n_declared == 2
    assert validation.declared_spellings(case.described) == ("XX",)
    flagged = validation.unrebuildable_columns(case.described)
    assert sorted(flagged) == ["reading"]
    assert "word(s) of your own" in flagged["reading"]
    outcome = validation.measure(case.described, case.path)
    assert outcome.census.missed == 0
    assert "presence.n_present" in _unsupported(outcome)


def test_the_quiet_exit_zero_construction_still_exists_on_what_is_left(
    tmp_path: pathlib.Path,
) -> None:
    """A-P3-26's first residual risk, checked rather than assumed closed.

    One description, two files it cannot tell apart, one of them
    conforming and one not. On the routes version 5 closed this is gone,
    because the two files no longer describe alike. On the two routes
    contract 5 section 7 leaves open it stands: the file that does NOT
    conform comes back at exit 0 with the obligations it would have
    missed named as ones this description cannot support asking.

    It is stated rather than repaired because repairing it here means
    reading the measured file to decide which of its own obligations
    run, which is what V5.1 forbids -- and the narrowings that would
    reach it, a distinct exit status or a bound drawn from the pooled
    count, are owner decisions neither taken here nor smuggled in.
    """
    case = _free_text(
        tmp_path, "quiet", ["ZZZ"] * 12, taxonomy.Settings(
            declared_missing_values=("ZZZ",)
        )
    )
    # A file that genuinely does not meet the description: twelve real
    # comments where the description says twelve cells are absent.
    other = fixtures.write(
        tmp_path,
        "quiet-other.csv",
        fixtures.single_column_table("note", _comments(72, 50)),
    )
    theirs = validation.measure(case.described, str(other))
    assert theirs.census.missed == 0
    assert "presence.n_missing" in _unsupported(theirs)
    # ...and the description's own producer does tell the two apart, so
    # the silence is a limit of what a report may say and not of what
    # the file is.
    mine = validation.measure(case.described, case.path)
    assert _unsupported(mine) == _unsupported(theirs)


def test_the_twin_of_a_description_that_still_cannot_be_read_moves_with_it(
    tmp_path: pathlib.Path,
) -> None:
    """A-P3-26's second residual risk, and what version 5 took off it.

    The twin writes every absent cell as an empty field, so no marker
    word survives into it. Which obligations a run can check is a
    function of the DESCRIPTION (V3.3) and the twin shares its
    description with the table, so on the routes that remain the twin
    carries the same limit. On the routes that closed it carries none --
    the description supports the question now, and the twin answers it.
    """
    open_route = _free_text(
        tmp_path, "still-open", ["ZZZ"] * 12, taxonomy.Settings(
            declared_missing_values=("ZZZ",)
        )
    )
    closed_route = _described(
        tmp_path,
        "now-closed",
        fixtures.single_column_table("reading", _numbers(200) + ["n/a"]),
        taxonomy.Settings(kept_values=("n/a",)),
    )
    for case, stem, moves in (
        (open_route, "still-open", True),
        (closed_route, "now-closed", False),
    ):
        twin = fixtures.write(
            tmp_path,
            f"{stem}-twin.csv",
            rendering.twin_csv(generation.generate(case.described, 0)),
        )
        table_run = validation.measure(case.described, case.path)
        twin_run = validation.measure(case.described, str(twin))
        assert twin_run.census.missed == 0, stem
        assert _unsupported(twin_run) == _unsupported(table_run), stem
        assert bool(_unsupported(twin_run)) is moves, stem
