"""No document may state less than the ratified plan does.

Review items P2-C4-F1 and P2-C5-F1, and the four repairs behind them.

THE AUDIT TRAIL. Four repairs closed a review item by writing a quieter
sentence into a normative document instead of meeting the bar the
sentence had. Each was found by the NEXT adversarial review, which is
one round of the product's own quality later than it should have been.
From the review records in `docs/plans/reviews/`:

1. The repair of P2-C1-F6 (round 1) widened the canonical seconds field
   to 60, correctly, and then made `earliest` and `latest` REPORT-ONLY
   in the contract's 9.6 and named a leap second a permitted loss in the
   method's G7.5. Round 2 found it as P2-C2-F5: "the specifications
   silently weaken exact temporal endpoints".
2. The repair of P2-C2-F5 (round 2) restored the matrix row and the
   G7.5 headline where the reviewer had looked, and wrote the exception
   into the paragraph AFTER each: a description publishing an end no
   cell of its own recorded shape can show would have that end "met as
   far as it could be, recounted and named". The generator did it.
   Round 3 found it as P2-C3-F2.
3. The repair of P2-C1-F1 (rounds 1 and 2) put an exact-count fallback
   into the method's G9.5 -- an implementation "MAY still fall back to a
   deterministic assignment" and name the miss -- while G9.5's own rule
   says the counts are exact whenever an answer exists. Round 3 found it
   as P2-C3-F1 and round 4 reopened it as P2-C4-F2 on a producer
   profile. The repair of P2-C2-F2 put the same shape into G6.4 for
   `numeric_styles`, which round 4 found as P2-C4-F3.
4. The repair of P2-C3-F2 (round 3) refused the two pairs it had been
   given and left a third: a shared-clock end whose own offset carries
   its cell outside the years 0001 to 9999, which G7.5 and G12 called
   the calendar's own end and had the run name in the report. Its new
   wording guard listed that passage as a decided one, so the guard was
   green about the sentence it existed to catch. Round 4 found it as
   P2-C4-F1 -- the fourth time, on the same obligation.

AND THEN THE GUARD ITSELF WAS DEFEATED. Round 4's repair read the three
documents for a fixed tuple of lesser-outcome phrases standing near a
fact's name. Round 5 ran eight mutations against it in scratch copies
and SIX survived: a lowering reworded out of the phrase list; a lowering
placed beyond the attribution distance; a lowering captured by a nearer
report-only name; a lowering of a field name whose class depends on the
role, which the scan skipped entirely; an authorization added to the
registry and propped up with an unrelated but genuine plan sentence; and
an entry added to the escape hatch citing a review item the newest
record only MENTIONED. Reading prose for meaning is a contest a phrase
list loses, and patching six holes in it would have left the seventh.

WHAT CARRIES THE GUARANTEE NOW. Three comparisons, none of which asks
what a sentence means:

* `test_no_passage_of_a_governing_document_is_unsealed` digests every
  passage of the plan and both specifications and refuses any passage
  that is not in `disposition_seal.SEALED`. A sentence nobody has
  reviewed is red whatever it says -- so rewording, moving, distancing
  and role-ambiguity all fail at the same place, before anybody argues.
* `test_the_registry_judgment_is_sealed` does the same for the three
  surfaces of `tests/dispositions.py` on which a person exercises
  judgment: the class each fact carries, the plan text it is bound by,
  and every authorization. Round 5 walked through two of those three.
* `test_the_plan_states_every_registered_disposition` parses the plan's
  own regions and requires the registry's class to be one the plan
  writes beside that fact's name. It is a comparison against the
  ratified source, not a search for a quotation that exists somewhere.

Two further checks cover what a seal cannot see. A seal catches a
sentence somebody wrote; it does not catch a sentence somebody deleted,
so `test_the_sentences_that_raise_a_bar_are_still_there` requires the
raising text to still be present. And the contract matrix is compared
against the registry in both directions, so a deleted row is caught
there.

The phrase scan survives as a SECOND net, unchanged in reach: it names a
known lowering in terms a person can act on. Its four defeats are
covered by the seal, and
`test_the_three_names_prose_cannot_settle_are_named_and_no_others`
states the part of it that was never able to see a role-ambiguous name.

THE ESCAPE HATCH is deliberate, narrow and now four-way bound.
`dispositions.OPEN` may carry a lowering an adversarial review has
already called a defect, and every entry has to (1) cite an item of the
newest review record's OWN round, standing as one of that record's item
headings and named in its verdict; (2) excuse only prose that was
already in the seal, so no entry can cover a sentence somebody has just
written; (3) still have a lowering to excuse; and (4) be gone by the
time a review stops rejecting the phase.
"""

import functools
import pathlib
import re
import typing

import pytest

import disposition_seal
import dispositions
import fixtures
from synthtwin import (
    contract,
    generation,
    profile,
    reading,
    taxonomy,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = REPO_ROOT / "docs" / "spec" / "profile-contract-v4.md"
METHOD = REPO_ROOT / "docs" / "spec" / "generation-method-v1.md"
PLAN = REPO_ROOT / "docs" / "plans" / "phase-2-generator.md"
REVIEWS = REPO_ROOT / "docs" / "plans" / "reviews"

DOCUMENTS = (("contract", CONTRACT), ("method", METHOD), ("plan", PLAN))

# The governing documents under the names the seal files them by. The
# Phase 3 plan joined the set at its ratification (its P3-D5); the
# registry's obligation-parsing walks the three Phase 2 documents
# above, and the seal covers all four.
PLAN3 = REPO_ROOT / "docs" / "plans" / "phase-3-product.md"
PLAN4 = REPO_ROOT / "docs" / "plans" / "phase-4-columns.md"
PLAN4 = REPO_ROOT / "docs" / "plans" / "phase-4-columns.md"
VALIDATION = REPO_ROOT / "docs" / "spec" / "validation-method-v1.md"
CONTRACT5 = REPO_ROOT / "docs" / "spec" / "profile-contract-v5.md"
RELATIVE = {
    "docs/spec/profile-contract-v4.md": CONTRACT,
    "docs/spec/profile-contract-v5.md": CONTRACT5,
    "docs/spec/generation-method-v1.md": METHOD,
    "docs/spec/validation-method-v1.md": VALIDATION,
    "docs/plans/phase-2-generator.md": PLAN,
    "docs/plans/phase-3-product.md": PLAN3,
    "docs/plans/phase-4-columns.md": PLAN4,
}


# -- reading the three documents ---------------------------------------


def _flat(path: pathlib.Path) -> str:
    """One document with its line wrapping removed, case kept.

    Case is kept because the disposition names are written in capitals
    and a lower-cased reading cannot tell `REPORT-ONLY` the class from
    "report" the verb.
    """
    return " ".join(path.read_text(encoding="utf-8").split())


@functools.cache
def _statements(path: pathlib.Path) -> "tuple[str, ...]":
    """One document as the units a disposition is stated in.

    The split lives in `dispositions.passages` rather than here, because
    the seal is written from the same function: a splitter that
    disagreed with the one that sealed would call every passage
    unsealed. A table ROW is a unit of its own, a heading is a unit of
    its own, and everything else is a block between blank lines --
    because the two lowerings that mattered ran across a full stop and a
    dash inside one paragraph, and a sentence reader would have missed
    both.
    """
    return dispositions.passages(path)


def _plan_regions() -> "dict[str, str]":
    """Plan P2-D6 cut into the paragraph that states each group.

    One field name means different things on different roles --
    `n_distinct` above all -- so a group is looked for only in its own
    paragraph. The two owner decisions that settle a fact outside the
    matrix are regions too.

    AND THE PHASE 3 AMENDMENTS THAT DISPOSE A FIELD ARE REGIONS OF THEIR
    OWN. The Phase 2 matrix is the record of what Phase 2 ruled and is
    not edited to carry a field Phase 2 never had; a field a later
    amendment adds is disposed in that amendment, and is looked for
    there. Each such region runs from the amendment's own opening mark
    to the next heading, so a disposition written into the amendment
    after it and a disposition written into the section after that
    cannot prop this one up.
    """
    flat = _flat(PLAN)
    matrix = flat[flat.index("## P2-D6.") : flat.index("## P2-D7.")]
    marks = sorted(
        (matrix.index(mark), name)
        for name, mark in dispositions.PLAN_REGIONS.items()
        if mark in matrix
    )
    regions = {
        name: matrix[
            at : marks[place + 1][0] if place + 1 < len(marks) else len(matrix)
        ]
        for place, (at, name) in enumerate(marks)
    }
    for name in dispositions.PLAN_SECTIONS:
        at = flat.index(f"## {name}.")
        rest = flat.find("## P2-D", at + 8)
        regions[name] = flat[at : rest if rest > 0 else len(flat)]
    later = _flat(PLAN3)
    for name, mark in dispositions.PLAN3_REGIONS.items():
        at = later.index(mark)
        rest = later.find("## ", at + len(mark))
        regions[name] = later[at : rest if rest > 0 else len(later)]
    fourth = _flat(PLAN4)
    for name, mark in dispositions.PLAN4_REGIONS.items():
        at = fourth.index(mark)
        rest = fourth.find("### P4-D", at + len(mark))
        regions[name] = fourth[at : rest if rest > 0 else len(fourth)]
    return regions


def _bindings(region: str, phrases: "tuple[str, ...]") -> "dict[str, set[str]]":
    """Which disposition each name in ``region`` is written beside.

    The plan writes a matrix paragraph as lists: some names, then the
    class they share, then the next list. So every name since the last
    class binds to the class that follows it. ``phrases`` are the names
    the plan writes without backticks -- "the three axes", "`percentiles`
    endpoints" -- which are read as names too.

    A FULL STOP ENDS A LIST. Without that, "13.5 `variants` keys are
    stored exactly. `missing_by_source` is REPORT-ONLY" reads as a
    sentence disposing `variants`, which it plainly is not.
    """
    parts = [re.escape(phrase) for phrase in phrases]
    parts = parts + [r"`([^`]+)`"]
    parts = parts + ["|".join(re.escape(w) for w in dispositions.DISPOSITIONS)]
    parts = parts + [r"\. "]
    token = re.compile("(" + ")|(".join(parts) + ")")
    found: dict[str, set[str]] = {}
    pending: list[str] = []
    for match in token.finditer(region):
        text = match.group(0)
        if text in dispositions.DISPOSITIONS:
            for name in pending:
                found.setdefault(name, set()).add(text)
            pending = []
            continue
        if text == ". ":
            pending = []
            continue
        pending = pending + [text.strip("`")]
    return found


# A field name several groups publish with DIFFERENT dispositions --
# `n_distinct` is exact on a column of numbers and approximated on a
# column of dates -- cannot be read out of prose that does not say which
# role it is talking about. Those names are checked where the role is
# known instead: the contract's per-role tables and the plan's per-role
# paragraphs, both of which this file also reads, and the seal, which
# does not care what a passage is about. The set is computed, never
# listed, so a future field that acquires a second class joins it
# without anybody remembering to.
def _ambiguous() -> "set[str]":
    """Field names whose class depends on the role, in the registry."""
    classes: dict[str, set[str]] = {}
    for fact in dispositions.REGISTRY:
        classes.setdefault(fact.field, set()).add(fact.disposition)
    return {name for name, kinds in classes.items() if len(kinds) > 1}


AMBIGUOUS = _ambiguous()


# -- the first lock: the documents are sealed passage by passage -------


def _unsealed(
    documents: "dict[str, pathlib.Path] | None" = None,
    sealed: "dict[str, tuple[str, ...]] | None" = None,
) -> "dict[str, list[str]]":
    """Every passage of a governing document that nobody has sealed.

    ``documents`` maps the seal's own name for a document to the file to
    read, so a mutation battery can substitute a scratch copy for one
    document and leave the other two alone. Deterministic: a text read,
    a split and a set membership. Raises `KeyError` when a document has
    no entry in the seal at all, which is itself a defect.
    """
    documents = documents if documents is not None else dict(RELATIVE)
    sealed = sealed if sealed is not None else disposition_seal.SEALED
    loose: dict[str, list[str]] = {}
    for name, path in sorted(documents.items()):
        known = set(sealed[name])
        strange = [
            passage
            for passage in dispositions.passages(path)
            if dispositions.digest(passage) not in known
        ]
        if strange:
            loose[name] = strange
    return loose


def test_no_passage_of_a_governing_document_is_unsealed() -> None:
    """A sentence nobody reviewed cannot govern a published fact.

    THIS IS THE CHECK THAT REPLACED READING PROSE FOR MEANING. Round 5
    defeated the phrase scan by rewording a lowering, by standing it
    away from the fact's name, by letting a nearer name capture it, and
    by using a field name the scan could not settle. All four write or
    change a passage, and a passage that is not in the seal is refused
    without anybody deciding what it means.

    Re-sealing is the way through, and it is meant to be: it is a
    separate, counted edit to `tests/disposition_seal.py`, one line per
    passage, whose docstring says what running it asserts. The four
    lowerings in this file's history were each written inside a large
    repair where nothing went red. None of them could be now.
    """
    loose = _unsealed()
    assert not loose, (
        "these passages of the governing documents are not in the "
        "disposition seal, so nobody has reviewed them against the "
        "ratified plan. If they state no less than the plan states, run "
        "`.venv/bin/python tools/dispositions/seal.py --write` and the "
        "diff will show exactly which passages you signed for. If any "
        "of them states LESS, amend `docs/plans/phase-2-generator.md` "
        "in the open instead, or leave the obligation standing and name "
        "the deviation in the report: "
        + repr(
            {
                name: [passage[:220] for passage in passages]
                for name, passages in loose.items()
            }
        )
    )


def test_the_seal_covers_every_governing_document_and_is_not_empty() -> None:
    """The vacuity floor for the seal.

    A seal holding no digests, or naming a document the guard never
    opens, would pass the check above by having nothing to compare. Both
    directions are asserted: the seal names exactly the governing
    documents, each document really is opened and split, and each one
    has a serious number of passages behind it.
    """
    assert set(disposition_seal.SEALED) == set(dispositions.GOVERNING)
    assert set(RELATIVE) == set(dispositions.GOVERNING)
    for name, path in sorted(RELATIVE.items()):
        assert path.exists(), name
        # The floor is a vacuity check -- a seal over a handful of
        # passages would be a seal in name only. It is not a length
        # requirement on a specification: the three Phase 2 documents
        # each split into many hundreds, the Phase 3 plan into about
        # 150, and the validation method into about 70, which is a
        # document rather than a handful. What the floor exists to
        # catch is a seal built over nothing at all.
        assert len(dispositions.passages(path)) > 50, name
        assert len(disposition_seal.SEALED[name]) > 50, name


def test_no_fourth_governing_document_can_appear_unsealed() -> None:
    """A seal over three documents is a seal a fourth walks around.

    The guard reads the ratified plans and the specifications, and
    every check in this file is bounded by that list. So the list itself
    is asserted against the tree: `docs/spec/` holds exactly the
    specifications named here, and `docs/plans/` holds exactly this
    phase's plan beside the earlier phases' plans and the review
    records. A new normative document added beside them -- the obvious
    way to state a lesser outcome somewhere nobody sealed -- turns this
    red on the day it lands, and the answer is to seal it too. That is
    what happened when `profile-contract-v5.md` landed under plan
    amendment A-P3-27: the list below grew by one line, in the same
    commit as the document and its seal entry.
    """
    specifications = sorted(
        path.name for path in (REPO_ROOT / "docs" / "spec").glob("*.md")
    )
    assert specifications == [
        "generation-method-v1.md",
        "profile-contract-v4.md",
        "profile-contract-v5.md",
        # The version 6 contract, DRAFT under adversarial review. Listed
        # here so the tree stays green while the rounds run, on the
        # precedent of the Phase 4 plan; it joins GOVERNING and the seal
        # at its ratification.
        "profile-contract-v6.md",
        "validation-method-v1.md",
    ], specifications
    plans = sorted(
        path.name for path in (REPO_ROOT / "docs" / "plans").glob("*.md")
    )
    assert plans == [
        "phase-0-public-skeleton.md",
        "phase-1-profiler.md",
        "phase-2-generator.md",
        "phase-3-product.md",
        # The Phase 4 plan, DRAFT under adversarial review: listed here
        # so the tree stays green while the rounds run, on the phase-0/1
        # precedent of listed-but-not-governing plans. It joins
        # dispositions.GOVERNING (and the seal, and the claim
        # inventory's surfaces) at its ratification, per its own
        # sequencing item 1.
        "phase-4-columns.md",
    ], plans
    for relative in dispositions.GOVERNING:
        assert (REPO_ROOT / relative).exists(), relative


def test_the_seal_reddens_on_any_new_or_reworded_passage(
    tmp_path: pathlib.Path,
) -> None:
    """And the seal is watched failing, on a change with no vocabulary.

    A guard nobody has watched fail is a guard nobody knows the reach
    of. The sentence added here carries no phrase from
    `dispositions.LESSER`, names no fact and states no class, so the
    phrase scan cannot see it at all -- and the seal turns red on it
    anyway, which is the property the phrase scan never had.
    """
    for name, path in sorted(RELATIVE.items()):
        copy = tmp_path / f"{path.stem}-plain.md"
        copy.write_text(
            path.read_text(encoding="utf-8")
            + "\n\nThe generated form is permitted to differ from the "
            "described one where the ladder is crowded, and the "
            "generated form then governs.\n",
            encoding="utf-8", newline="\n",
        )
        substituted = dict(RELATIVE)
        substituted[name] = copy
        assert _unsealed(substituted), name


# -- the second lock: the registry's own judgment is sealed ------------


def test_the_registry_judgment_is_sealed() -> None:
    """What a published fact owes cannot be edited in one file alone.

    Round 5 changed `n_missing` to REPORT-ONLY in the registry, propped
    it up with an unrelated but genuine plan sentence, changed the
    contract row to agree, and all 19 guard tests passed. The three
    digests below are over the three surfaces on which somebody
    exercises judgment here -- the class each fact carries, the plan
    text each fact is bound by, and every authorized lesser outcome --
    so an edit to any of them has to be countersigned in a generated
    file whose only reason to change is that somebody decided to change
    what a fact owes.
    """
    assert dispositions.judgment(dispositions.REGISTRY) == (
        disposition_seal.JUDGMENT
    ), (
        "the registry's decisions are not the sealed ones. If the change "
        "is the plan's own ruling, run "
        "`.venv/bin/python tools/dispositions/seal.py --write`; if it "
        "lowers a bar, amend the ratified plan instead."
    )


def test_the_judgment_seal_separates_its_surfaces() -> None:
    """The vacuity floor for the judgment seal.

    Four digests rather than one, so a failure says WHICH kind of edit
    moved: a class, a binding, an authorization, or the two report lines
    that are notes rather than misses. A single digest would be strictly
    weaker at the same cost. This also proves the four are really
    different functions of the registry, which one copy-paste mistake in
    the generator would otherwise hide.
    """
    marks = dispositions.judgment(dispositions.REGISTRY)
    assert set(marks) == {
        "classes",
        "bindings",
        "authorizations",
        "reports",
    }
    assert len(set(marks.values())) == 4
    assert set(disposition_seal.JUDGMENT) == set(marks)


# -- the third lock: the plan is parsed, not searched -------------------


def _plan_violations(
    registry: "typing.Sequence[dispositions.Fact]",
) -> "list[str]":
    """Every registry entry the ratified plan does not state.

    Three rules, and the second is what round 5 walked through. First,
    a fact whose bar the plan states in a sentence has to carry that
    sentence, still in the plan, in its own region. Second, WHENEVER the
    plan's own region writes a class beside the fact's name, the
    registry's class has to be one of them -- a quoted sentence no
    longer excuses a class the plan does not write there, which is
    exactly how `n_missing` was made REPORT-ONLY in a scratch copy.
    Third, a WEAKER class written beside the same name is a lowering of
    the plan itself unless the plan also carries the authorization.
    """
    regions = _plan_regions()
    broken: list[str] = []
    for fact in registry:
        where = f"{fact.group}/{fact.field}"
        region = regions.get(fact.plan_region or fact.group)
        if region is None:
            broken.append(f"{where}: no such plan region")
            continue
        phrase = fact.plan_phrase or f"`{fact.field}`"
        bound = _bindings(region, (phrase,)).get(phrase.strip("`"), set())
        if fact.plan_words and fact.plan_words not in region:
            broken.append(f"{where}: plan words gone")
        if not fact.plan_words and fact.disposition not in bound:
            broken.append(
                f"{where}: the plan writes {sorted(bound)}, "
                f"the registry says {fact.disposition}"
            )
        if fact.plan_words and bound and fact.disposition not in bound:
            broken.append(
                f"{where}: the plan's own region writes {sorted(bound)} "
                f"beside this name; a quoted sentence does not make it "
                f"{fact.disposition}"
            )
        mine = dispositions.STRENGTH.get(fact.disposition)
        for other in bound:
            rank = dispositions.STRENGTH.get(other)
            if mine is None or rank is None or rank >= mine:
                continue
            if not any(words in region for _phrase, words in fact.authorized):
                broken.append(f"{where}: the plan also writes {other}")
        broken.extend(_authorization_violations(fact, regions))
    return broken


def _authorization_violations(
    fact: dispositions.Fact, regions: "dict[str, str]"
) -> "list[str]":
    """Every way one fact's authorizations fail to bind themselves.

    Three bindings, all three checked, because round 5 added one that
    had none of them. The authorization has to be DECLARED for this
    fact; the plan region it declares has to exist and carry its words;
    and the class it authorizes has to be genuinely weaker than the
    class the fact carries -- an "authorization" for an equal or
    stronger class is not an authorization at all.
    """
    where = f"{fact.group}/{fact.field}"
    broken: list[str] = []
    for phrase, words in fact.authorized:
        declared = dispositions.AUTHORIZED_BY.get(
            (fact.group, fact.field, phrase)
        )
        if declared is None:
            broken.append(
                f"{where}: the authorization '{phrase}' names no plan "
                f"region and no lesser class"
            )
            continue
        name, lesser = declared
        home = regions.get(name)
        if home is None:
            broken.append(f"{where}: no plan region called {name}")
        elif words not in home:
            broken.append(
                f"{where}: plan region {name} does not carry the words "
                f"this authorization rests on"
            )
        rank = dispositions.STRENGTH.get(lesser)
        mine = dispositions.STRENGTH.get(fact.disposition)
        if rank is None or mine is None or rank >= mine:
            broken.append(
                f"{where}: {lesser} is no lesser outcome than "
                f"{fact.disposition}"
            )
    return broken


def test_the_plan_states_every_registered_disposition() -> None:
    """Every entry of the registry is the plan's own ruling.

    Two mechanisms, because the plan states a disposition in two ways.
    Most facts are written beside their class in a list, and those are
    parsed. The rest are settled in a sentence, and the registry quotes
    that sentence; a sentence that is softened stops being found. Since
    round 5, quoting a sentence no longer BYPASSES the parse: where the
    plan writes any class beside the name, the registry has to carry one
    of them.
    """
    assert _plan_violations(dispositions.REGISTRY) == []


def test_every_authorization_quotes_the_plan() -> None:
    """A lesser outcome may be authorized only in the plan's own words.

    The registry can excuse a lesser outcome, and if it could do so on
    its own say-so it would be the fifth way to lower a bar quietly.
    Every authorization therefore carries the plan's sentence for it,
    that sentence has to still be in the plan, and -- since round 5 --
    the authorization list itself is sealed, so a genuine sentence
    quoted beside a fact it says nothing about no longer buys anything.
    """
    plan = _flat(PLAN)
    seen = 0
    for fact in dispositions.REGISTRY:
        for _phrase, words in fact.authorized:
            assert words in plan, f"{fact.group}/{fact.field}: {words[:60]}"
            seen = seen + 1
    assert seen >= 4, seen


def test_every_authorization_binds_a_fact_a_region_and_a_class() -> None:
    """The vacuity floor for the binding, and the inventory behind it.

    `dispositions.AUTHORIZED_BY` has to hold exactly the authorizations
    the registry carries -- no entry for an authorization nobody wrote,
    and no authorization without an entry. That equality is what makes
    "there is no default" true: an authorization added to a fact has to
    be declared here as well, and both files are sealed.
    """
    carried = {
        (fact.group, fact.field, phrase)
        for fact in dispositions.REGISTRY
        for phrase, _words in fact.authorized
    }
    assert set(dispositions.AUTHORIZED_BY) == carried
    assert len(carried) >= 4, sorted(carried)
    for (group, field, _phrase), (name, lesser) in sorted(
        dispositions.AUTHORIZED_BY.items()
    ):
        fact = dispositions.BY_KEY[(group, field)]
        assert lesser in dispositions.DISPOSITIONS
        assert dispositions.STRENGTH[lesser] < (
            dispositions.STRENGTH[fact.disposition]
        )
        assert name in _plan_regions(), name


def test_an_authorization_the_plan_does_not_carry_is_refused() -> None:
    """And the binding is watched failing, on round 5's own move.

    Three separate mutations of the same authorization, each of which
    the old check accepted: one that declares nothing, one whose words
    are genuine but live in another part of the plan, and one that
    claims a class no weaker than the fact's own.
    """
    regions = _plan_regions()
    fact = dispositions.BY_KEY[("universal", "n_missing")]
    invented = fact._replace(authorized=(("may miss", "Domains are widened"),))
    assert _authorization_violations(invented, regions) != []
    borrowed = dispositions.BY_KEY[("numeric", "n_distinct")]._replace(
        authorized=(("may miss", "Domains are widened"),)
    )
    assert _authorization_violations(borrowed, regions) != []


def test_the_registry_authorizes_nothing_for_the_two_ends() -> None:
    """The vacuity floor for the check above, on the disputed fact.

    An authorization list that was empty for every fact would make the
    scan below trivially strict and would pass whatever the plan said.
    These four are the ones the plan authorizes nothing for, and they
    are the four this item is about.
    """
    for field in (
        "earliest",
        "latest",
        "date_percentiles.min",
        "date_percentiles.max",
    ):
        fact = dispositions.BY_KEY[("datetime", field)]
        assert fact.authorized == (), field
        assert fact.disposition == dispositions.EXACT_OBSERVABLE, field
    assert dispositions.BY_KEY[("numeric", "n_distinct")].authorized != ()


# -- what a seal cannot see: a raising sentence that was deleted -------


def test_the_sentences_that_raise_a_bar_are_still_there() -> None:
    """A deletion is a lowering too, and the seal cannot see one.

    Sealing catches a passage somebody wrote or reworded. Removing a
    whole passage leaves every remaining digest sealed, so the sentences
    whose whole job is to CLOSE a corner are listed in
    `dispositions.ANCHORS` and required to still be present. Losing "no
    corner, no exception" from a matrix row leaves the row true and the
    corner open again, which is the shape of two of the four lowerings
    in this file's history.
    """
    for relative, sentence in dispositions.ANCHORS:
        flat = _flat(RELATIVE[relative])
        assert sentence in flat, (
            f"{relative} no longer carries a sentence that raises a bar. "
            f"Deleting it lowers the obligation as surely as rewriting "
            f"it would: {sentence[:120]}"
        )


def test_the_raising_sentences_are_a_real_inventory() -> None:
    """The vacuity floor for the anchors.

    An empty or one-sided anchor list would make the check above pass
    while protecting nothing. Both governing directions are asserted:
    the plan is anchored, the contract is anchored, and the list is long
    enough to cover the classes of raising sentence the four historical
    lowerings each removed or contradicted.
    """
    assert len(dispositions.ANCHORS) >= 8
    covered = {relative for relative, _sentence in dispositions.ANCHORS}
    assert "docs/plans/phase-2-generator.md" in covered
    assert "docs/spec/profile-contract-v4.md" in covered
    assert covered <= set(dispositions.GOVERNING)


# -- the contract's matrix is exactly the registry ---------------------


def _matrix() -> "dict[str, list[tuple[tuple[str, ...], str]]]":
    """The disposition matrix, read from both versions together.

    Version 4's section 9 is the whole matrix; version 5 carries it by
    reference and states only the rows it changes or adds, in its
    section 11 (its C5-30). Reading version 4 alone would leave every
    version 5 field undisposed, and reading version 5 alone would leave
    the other nine tables empty. `dispositions.CONTRACT5_SECTIONS` says
    which version 4 table each delta row belongs to, and a delta row it
    does not name stops this reader rather than being filed by guess.
    """
    text = CONTRACT.read_text(encoding="utf-8")
    start = text.index("## 9. The disposition matrix")
    body = text[start : text.index("\n## ", start + 10)]
    sections: dict[str, list[tuple[tuple[str, ...], str]]] = {}
    heading = ""
    for line in body.split("\n"):
        if line.startswith("### "):
            heading = line[4:].strip()
            sections[heading] = []
            continue
        if line.startswith("**`") and heading.startswith("9.7"):
            heading = f"9.7 {line.strip().strip('*').strip('`')}"
            sections[heading] = []
            continue
        if not line.startswith("|") or not heading:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2 or set(cells[0]) <= set("-: "):
            continue
        names = tuple(
            name
            for name in re.findall(r"`([^`]+)`", cells[0])
            if name not in dispositions.RUNGS
        )
        if names:
            sections[heading].append((names, cells[1]))
    for names, said in dispositions.contract5_delta(CONTRACT5):
        for name in names:
            where = dispositions.CONTRACT5_SECTIONS.get(name)
            if where is None:
                continue
            rows = sections[where]
            sections[where] = [
                (kept, text) for kept, text in rows if name not in kept
            ] + [((name,), said)]
    return sections


def _matrix_violations(
    registry: "typing.Sequence[dispositions.Fact]",
) -> "list[str]":
    """Every disagreement between the contract's matrix and ``registry``.

    All three directions matter. A missing row is an obligation nobody
    decided; an invented row is a claim the plan never made; and a
    weaker class in the row is the lowering this file exists for.
    """
    matrix = _matrix()
    by_key = {(fact.group, fact.field): fact for fact in registry}
    broken: list[str] = []
    for group, section in dispositions.CONTRACT_SECTIONS.items():
        rows = matrix[section]
        stated = {name for names, _text in rows for name in names}
        owed = {
            fact.field
            for fact in registry
            if fact.group == group
            and (fact.group, fact.field)
            not in dispositions.FACTS_OUTSIDE_THE_VERSION_4_MATRIX
        }
        if stated != owed:
            broken.append(
                f"{group}: the contract states {sorted(stated - owed)} that "
                f"the registry does not, and omits {sorted(owed - stated)}"
            )
        for names, text in rows:
            said = [word for word in dispositions.DISPOSITIONS if word in text]
            for name in names:
                fact = by_key.get((group, name))
                if fact is None:
                    continue
                if not said or said[0] != fact.disposition:
                    broken.append(
                        f"{group}/{name}: the contract row heads with "
                        f"{said[:1]}, the plan says {fact.disposition}"
                    )
                    continue
                mine = dispositions.STRENGTH.get(fact.disposition)
                for other in said[1:]:
                    rank = dispositions.STRENGTH.get(other)
                    if mine is None or rank is None or rank >= mine:
                        continue
                    if not _allowed(fact, text.lower()):
                        broken.append(
                            f"{group}/{name}: the contract row also writes "
                            f"{other} with nothing in the plan behind it"
                        )
                    elif not _clearing(text.lower()) and other not in (
                        _authorized_classes(fact, text.lower())
                    ):
                        broken.append(
                            f"{group}/{name}: the contract row writes "
                            f"{other}, which is not the class the plan's "
                            f"own authorization names"
                        )
    return broken


def _clearing(window: str) -> bool:
    """True when this window settles the description instead of paying it."""
    return any(word in window for word in dispositions.CLEARING)


def _authorized_classes(
    fact: dispositions.Fact, window: str
) -> "set[str]":
    """The lesser classes the plan authorizes for ``fact`` in this window.

    An authorization is not a licence to write any weaker class: it
    names one. The numeric envelope authorizes APPROXIMATED and owner
    decision 6's corner authorizes REPORT-ONLY, and a row that wrote the
    other one would be stating an outcome the plan never gave it.
    """
    return {
        dispositions.AUTHORIZED_BY[(fact.group, fact.field, phrase)][1]
        for phrase, _words in fact.authorized
        if phrase.lower() in window
        and (fact.group, fact.field, phrase) in dispositions.AUTHORIZED_BY
    }


def test_the_contract_matrix_is_exactly_the_registry() -> None:
    """No fact missing, no fact invented, no weaker class.

    This is also what catches a DELETED matrix row, which the seal
    cannot see: the two directions are compared as sets, so a row
    quietly removed leaves an obligation the contract no longer states.
    """
    assert _matrix_violations(dispositions.REGISTRY) == []


# -- the second net: a known lowering, named in terms a person can act on


def _mentions(fact: dispositions.Fact) -> "tuple[str, ...]":
    """The phrases by which a statement speaks about this fact."""
    return (f"`{fact.field}`",) + fact.aliases


def _allowed(fact: dispositions.Fact, window: str) -> bool:
    """True when this window carries an authorization or a clearing.

    A clearing is a statement that settles the description instead of
    paying for it in the twin -- a refusal -- or one that says the
    lesser outcome beside it reaches other fields and not this one.
    """
    if any(word in window for word in dispositions.CLEARING):
        return True
    return any(phrase.lower() in window for phrase, _words in fact.authorized)


def _lowerings(path: pathlib.Path, fact: dispositions.Fact) -> "list[str]":
    """Every statement in one document that gives ``fact`` a lesser outcome.

    Two ways of saying it, read two ways.

    A CLASS written beside the fact's own name is read by the same
    binding parse the plan is read with, not by nearness: these
    documents state many facts in one sentence, and "`n_rows` and
    `n_columns` are EXACT-OBSERVABLE; `source.encoding` is REPORT-ONLY"
    puts a weaker class forty characters from a fact it says nothing
    about. The parse binds each name to the class that follows it, which
    is what the sentence means.

    A lesser outcome written as PROSE is read by nearness, because there
    is no grammar to lean on and because that is the form all four
    lowerings took. What nearness cannot do is recognize wording nobody
    listed, and the seal above is what covers that.
    """
    return list(_read(path).get((fact.group, fact.field), ()))


@functools.cache
def _read(
    path: pathlib.Path,
) -> "dict[tuple[str, str], tuple[str, ...]]":
    """One document read once, as the lowerings it states, by fact.

    Read once because the mutation proofs below run the whole scan many
    times, and because a statement carrying no lesser vocabulary at all
    -- which is nearly every statement -- needs no work beyond that
    test.
    """
    scannable = [
        fact
        for fact in dispositions.REGISTRY
        if fact.disposition in dispositions.EXACT
        and fact.field not in AMBIGUOUS
    ]
    by_name: dict[str, list[dispositions.Fact]] = {}
    for fact in scannable:
        by_name.setdefault(fact.field, []).append(fact)
    caught: dict[tuple[str, str], list[str]] = {}
    for statement in _statements(path):
        body = statement.lower()
        held: set[dispositions.Fact] = set()
        if not _definitional(statement):
            for name, classes in _bindings(statement, ()).items():
                for fact in by_name.get(name, []):
                    mine = typing.cast(
                        int, dispositions.STRENGTH.get(fact.disposition)
                    )
                    for other in classes:
                        rank = dispositions.STRENGTH.get(other)
                        if rank is not None and rank < mine:
                            held.add(fact)
        if any(word in body for word in dispositions.LESSER):
            for _at, owners in _lesser_sites(body):
                held.update(fact for fact in owners if fact in set(scannable))
        for fact in held:
            if _allowed(fact, body):
                continue
            caught.setdefault((fact.group, fact.field), []).append(statement)
    return {key: tuple(value) for key, value in caught.items()}


def _definitional(statement: str) -> bool:
    """True of a statement that names the classes rather than using them.

    A statement naming four or more of the six is a definition or an
    inventory -- plan P2-D6 opens with one -- and disposes nothing, so
    the binding parse is not applied to it.
    """
    return sum(word in statement for word in dispositions.DISPOSITIONS) >= 4


def _lesser_sites(body: str) -> "list[tuple[int, list[dispositions.Fact]]]":
    """Every lesser-outcome phrase, against the fact it is nearest to.

    NEAREST, and that is the whole of the rule. These documents put many
    facts in one passage: G7.5's closing bullets say `time_precision` is
    exact and `format` is not reproduced, four lines apart. A per-fact
    window reads the second sentence as a statement about the first
    field. Distance settles it -- the phrase belongs to the name it
    stands beside -- and a phrase that stands beside no registered name
    within the window belongs to nobody and is not read as a lowering of
    anything. Round 5 defeated exactly this rule twice, by distance and
    by a nearer name; the seal is what covers both, and this stays as
    the net that says a known lowering in plain terms.
    """
    sites: list[tuple[int, int, dispositions.Fact]] = []
    for fact in dispositions.REGISTRY:
        for mention in _mentions(fact):
            at = body.find(mention.lower())
            while at >= 0:
                sites = sites + [(at, len(mention), fact)]
                at = body.find(mention.lower(), at + 1)
    caught: list[tuple[int, list[dispositions.Fact]]] = []
    for word in dispositions.LESSER:
        at = body.find(word)
        while at >= 0:
            spans = [
                (_distance(at, len(word), start, size), fact)
                for start, size, fact in sites
            ]
            near = min((gap for gap, _fact in spans), default=len(body))
            if near <= dispositions.WINDOW:
                # A LIST OF NAMES IS ONE PLACE. "`n_numeric`,
                # `n_not_numeric`, `n_all_digits`, `n_code_alphabet`" is
                # four names inside sixty characters, and a statement
                # standing beside the run is about all four, not about
                # whichever of them the comma put first.
                caught = caught + [
                    (
                        at,
                        [
                            fact
                            for gap, fact in spans
                            if gap <= near + dispositions.TOGETHER
                        ],
                    )
                ]
            at = body.find(word, at + 1)
    return caught


def _distance(at: int, size: int, start: int, span: int) -> int:
    """How far one phrase stands from one name, zero where they overlap."""
    if at < start + span and start < at + size:
        return 0
    if at >= start + span:
        return at - (start + span)
    return start - (at + size)


def _scan(
    documents: "tuple[tuple[str, pathlib.Path], ...]" = DOCUMENTS,
) -> "dict[tuple[str, str], list[str]]":
    """Every unauthorized lesser statement, by the fact it is about."""
    caught: dict[tuple[str, str], list[str]] = {}
    for fact in dispositions.REGISTRY:
        if fact.disposition not in dispositions.EXACT:
            continue
        for _name, path in documents:
            for statement in _lowerings(path, fact):
                caught.setdefault((fact.group, fact.field), []).append(
                    statement
                )
    return caught


def test_no_document_states_a_lesser_outcome_for_an_exact_fact() -> None:
    """The check the four repairs would each have failed.

    Every exact fact, every passage of all three documents, and a
    statement that gives one of them a lesser outcome has to be
    authorized by the plan -- or be a defect a reviewer has already
    named, which `dispositions.OPEN` carries with its item number.
    """
    caught = _scan()
    undecided = {
        key: statements
        for key, statements in caught.items()
        if key not in dispositions.OPEN
    }
    assert not undecided, {
        key: [one[:200] for one in statements]
        for key, statements in undecided.items()
    }


# -- the escape hatch, bound four ways ---------------------------------


REVIEW_NAME = re.compile(r"^phase-2-code-review-round-(\d+)\.md$")


def _newest_review() -> "tuple[int, str]":
    """The newest code review record, by ROUND NUMBER rather than by name.

    Sorted by the integer in the file name, because a lexicographic sort
    puts round 10 before round 2 and would silently start reading a
    stale record on the day a tenth round lands.
    """
    records = []
    for path in REVIEWS.glob("phase-2-code-review-round-*.md"):
        found = REVIEW_NAME.match(path.name)
        if found:
            records.append((int(found.group(1)), path))
    assert records, "no code review record"
    number, path = max(records)
    return number, path.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    """One `## ` section of a review record, or the empty string."""
    at = text.find(f"\n{heading}")
    if at < 0:
        return ""
    rest = text.find("\n## ", at + 1)
    return text[at : rest if rest > 0 else len(text)]


def _items_left_open(number: int, text: str) -> "set[str]":
    """The item identifiers this record leaves open, in its OWN round.

    Three conditions, and round 5 defeated a check that had none of
    them. The identifier has to carry this record's round number, so an
    item a later review CLOSED cannot be cited however often the record
    mentions it -- and a closure record necessarily mentions every item
    it closed. It has to stand as one of the record's own item
    headings, so a passing reference is not enough. And it has to be
    named in the verdict, so an item the record itself reports as closed
    in its round-by-round table does not qualify.
    """
    headed = set(
        re.findall(rf"^### (P2-C{number}-[FC]\d+)\b", text, flags=re.MULTILINE)
    )
    verdict = _section(text, "## Verdict")
    return {item for item in headed if item in verdict}


def _open_violations(
    entries: "dict[tuple[str, str], str]",
    number: "int | None" = None,
    text: "str | None" = None,
) -> "list[str]":
    """Every entry of the escape hatch the newest review does not carry."""
    if number is None or text is None:
        number, text = _newest_review()
    live = _items_left_open(number, text)
    broken: list[str] = []
    for key, item in sorted(entries.items()):
        if key not in dispositions.BY_KEY:
            broken.append(f"{key}: no such published fact")
        if item not in live:
            broken.append(
                f"{key}: {item} is not an item round {number} leaves open "
                f"({sorted(live)})"
            )
    return broken


def test_every_open_lowering_is_an_item_the_newest_review_leaves_open() -> None:
    """An open lowering belongs to a reviewer, and to the current round.

    Round 5 opened an entry in a scratch copy citing P2-C4-F1, an item
    that round CLOSED, and the check passed because the closure record
    necessarily names the item it closes. The item's own round number,
    its heading and the verdict are parsed now, so a closed item cannot
    carry an entry and an implementer cannot open one at all.
    """
    assert _open_violations(dispositions.OPEN) == []


def test_the_newest_review_really_leaves_items_open() -> None:
    """The vacuity floor for the check above.

    A parse that found no open item would make every entry fail, which
    is safe; a parse that found EVERY identifier in the file would make
    every entry pass, which is the defect round 5 exploited. So the set
    is asserted to be a real, bounded set of this round's own items, and
    to exclude the closed round-4 item the scratch attack used.
    """
    number, text = _newest_review()
    live = _items_left_open(number, text)
    assert live, f"round {number} leaves no item open"
    assert all(item.startswith(f"P2-C{number}-") for item in live)
    assert len(live) < 20, live
    assert f"P2-C{number - 1}-F1" not in live
    assert "P2-C4-F1" in text, "the closed item is mentioned, as expected"


def test_every_open_lowering_excuses_only_prose_that_was_already_sealed(
) -> None:
    """No entry may cover a sentence somebody has just written.

    This is what stops the escape hatch being a way in. An entry excuses
    a statement a reviewer has already read, and a statement a reviewer
    has already read is a statement in the seal. A newly written
    lowering is unsealed, so opening an entry for it does not help --
    the seal check is red before this one is consulted.
    """
    known: set[str] = set()
    for marks in disposition_seal.SEALED.values():
        known.update(marks)
    caught = _scan()
    for key in sorted(dispositions.OPEN):
        for statement in caught.get(key, ()):
            assert dispositions.digest(statement) in known, (
                f"{key} is carried as an open defect, but the statement it "
                f"excuses is not in the seal, so no reviewer has read it: "
                f"{statement[:200]}"
            )


def test_every_open_lowering_is_still_a_lowering() -> None:
    """And it does not go stale in the other direction either.

    An entry whose statement has been repaired is an entry that would
    silently permit the NEXT lowering of that fact. Finding nothing is
    therefore a failure that says so, and the fix is to delete the line.
    """
    caught = _scan()
    stale = [key for key in dispositions.OPEN if key not in caught]
    assert not stale, (
        "these facts carry no lesser statement any more, so their lines "
        f"in tests/dispositions.py OPEN have to be deleted: {sorted(stale)}"
    )


def _rejects(text: str) -> bool:
    """True when a review record's verdict still rejects the phase."""
    return "REJECT" in _section(text, "## Verdict")


def test_no_open_lowering_survives_a_review_that_stops_rejecting() -> None:
    """An open defect may not be carried into a ratified phase.

    `dispositions.OPEN` is a list of defects with owners and numbers, not
    a list of permissions. The moment a review record stops rejecting
    Phase 2 -- ratify, or ratify with conditions -- every one of them has
    to be closed or the phase is not what the record says it is.
    """
    _number, text = _newest_review()
    if not _rejects(text):
        assert dispositions.OPEN == {}, (
            "the newest review no longer rejects Phase 2, so these open "
            f"lowerings may not be carried: {sorted(dispositions.OPEN)}"
        )


def test_the_ratification_gate_is_not_vacuous() -> None:
    """The gate above is watched firing, on a record that ratifies.

    A gate whose condition never holds is a gate nobody knows the reach
    of, and today's record rejects, so the branch that matters would
    never run. Two synthetic verdicts are put through the same reader:
    the current one, which rejects, and a ratifying one, which does not.
    """
    _number, text = _newest_review()
    assert _rejects(text), "the current record is expected to reject"
    assert not _rejects(
        text.replace("**REJECT.** The blocking items", "**Ratify.** No item")
    )
    assert not _rejects("## Verdict\n\nRatify with conditions.\n")


# -- the executable half: a disposition drives a live assertion --------
#
# A seal stops a document saying less than the plan says. It does not by
# itself stop the PRODUCT doing less, and a guard that only reads text
# would leave the obligation resting on text. So every disposition also
# drives an assertion over the shipped generator: the run measures its
# own twin and files a line for each published fact it did not meet, and
# each line has to be one the plan allows. Softening a sentence changes
# nothing here -- the assertion is over the registry and the code -- so
# lowering a bar in prose alone now buys nothing at all.


def _described(
    folder: pathlib.Path, text: str, declared: "list[str] | None" = None
) -> contract.Profile:
    """Write a table, describe it with the REAL producer, load it back."""
    path = fixtures.write(folder, "table.csv", text)
    table = reading.read_table(str(path))
    document = profile.build_document(
        table, taxonomy.Settings(), declared if declared else []
    )
    target = fixtures.write_profile(folder, "table-profile.json", document)
    return contract.load_profile(str(target))


@pytest.fixture(scope="module")
def battery(
    tmp_path_factory: pytest.TempPathFactory,
) -> "list[tuple[str, contract.Profile]]":
    """Producer descriptions covering every role the taxonomy has.

    Built by the Phase 1 producer from seeded neutral tables, never
    hand-written, so what is exercised is the path a user's table takes.
    """
    folder = tmp_path_factory.mktemp("c5f1-battery")
    wide = folder / "wide"
    wide.mkdir()
    huge = folder / "huge"
    huge.mkdir()
    code = folder / "code"
    code.mkdir()
    return [
        (
            "every role",
            _described(wide, fixtures.every_role_table(), ["record_code"]),
        ),
        (
            "numbers too large to hold",
            _described(
                huge,
                fixtures.single_column_table(
                    "value",
                    ["9" * 320, "-" + "9" * 320, "0." + "0" * 400 + "1"] * 9,
                ),
            ),
        ),
        (
            "declared identifier",
            _described(
                code,
                fixtures.single_column_table(
                    "code",
                    [f"N_{index}" for index in range(13)]
                    + ["no!!"] * 5
                    + ["x-y"] * 8
                    + ["913"] * 12
                    + ["-3"] * 11,
                ),
                ["code"],
            ),
        ),
    ]


def _reported(
    battery: "list[tuple[str, contract.Profile]]",
) -> "list[tuple[str, str, str, str]]":
    """Every report line the battery produces: (case, role, fact, column)."""
    lines: list[tuple[str, str, str, str]] = []
    for case, loaded in battery:
        roles = {column.name: column.role for column in loaded.columns}
        for seed in (0, 17, 63):
            twin = generation.generate(loaded, seed)
            for note in twin.deviations:
                lines.append(
                    (case, roles.get(note.column, ""), note.fact, note.column)
                )
    return lines


def _permitted(role: str, fact: str) -> "str | None":
    """Why the plan allows a report line about this fact, or None.

    The lookup is the registry's own: a fact of the role's own group
    first, then the universal and top-level groups every role shares. A
    name none of them holds is a fact the profile does not publish, and
    those are named separately.
    """
    if fact in dispositions.UNPUBLISHED_NOTES:
        return "the profile publishes no such fact"
    group = dispositions.ROLE_GROUPS.get(role, "")
    for owner in (group, "universal", "document"):
        entry = dispositions.BY_KEY.get((owner, fact))
        if entry is None:
            continue
        if entry.disposition not in dispositions.EXACT:
            return f"{owner}/{fact} is {entry.disposition}"
        if entry.authorized:
            return f"{owner}/{fact} carries the plan's own authorization"
        if (owner, fact) in dispositions.OPEN:
            return f"{owner}/{fact} is open as {dispositions.OPEN[(owner, fact)]}"
        if (owner, fact) in dispositions.REPORTED_NOTES:
            return f"{owner}/{fact}: {dispositions.REPORTED_NOTES[(owner, fact)]}"
        return None
    return None


def test_the_shipped_generator_misses_no_exact_fact_the_plan_holds_it_to(
    battery: "list[tuple[str, contract.Profile]]",
) -> None:
    """Every report line has to be one the ratified plan allows.

    This is the assertion a quieter sentence cannot reach. A run that
    starts missing an exact count turns this red no matter what the
    method or the contract says about it, because the comparison is
    between the code's own measurement and the registry -- and the
    registry is the plan. To make this pass with a genuine miss in it,
    somebody has to weaken this assertion or the registry, and both of
    those are changes a reviewer reads in a diff.
    """
    refused = sorted(
        {
            (case, role, fact, column)
            for case, role, fact, column in _reported(battery)
            if _permitted(role, fact) is None
        }
    )
    assert not refused, (
        "the twin did not meet a published fact the ratified plan holds "
        "it to exactly, and the plan authorizes no lesser outcome for it. "
        "Naming the miss in the report is honest; it is not the "
        f"obligation: {refused}"
    )


def test_the_producer_battery_really_exercises_the_report(
    battery: "list[tuple[str, contract.Profile]]",
) -> None:
    """The vacuity floor for the check above.

    A battery whose twins met every fact would pass it while proving
    nothing, and a battery covering two roles would miss the paths that
    matter. Both are asserted: the roles the battery reaches, and the
    fact that real report lines come out of it and are individually
    accounted for.
    """
    roles = {
        column.role for _case, loaded in battery for column in loaded.columns
    }
    assert len(roles) >= 8, sorted(roles)
    assert roles <= set(dispositions.ROLE_GROUPS), sorted(roles)
    lines = _reported(battery)
    assert len(lines) >= 8, lines
    reasons = {_permitted(role, fact) for _case, role, fact, _name in lines}
    assert None not in reasons
    assert len(reasons) >= 4, reasons


def test_an_invented_miss_of_an_exact_fact_is_refused() -> None:
    """And the executable half is watched failing.

    `n_missing` is exact on every role and the plan authorizes nothing
    for it, so a run that filed a line about it would be refused. The
    same lookup that clears every real line above returns nothing here,
    which is what makes the check above a check rather than a formality.
    """
    assert _permitted("count", "n_missing") is None
    assert _permitted("datetime", "earliest") is None
    assert _permitted("free_text", "length.min") is None
    # ...while the lines the battery really produces are each cleared for
    # a reason the registry states.
    assert _permitted("count", "n_distinct") is not None
    assert _permitted("datetime", "n_distinct") is not None
    assert _permitted("categorical", "suppressed_levels") is not None


# -- and it goes red on every lowering this repository has made --------


# Each entry is (which document, the sentence, the fact it is about).
# The first four are the four lowerings, in the words the repository
# actually carried or in the same shape; the rest are the same move
# against obligations nobody has touched, so the guard is not a
# collection of special cases about one field.
LOWERINGS = (
    (
        "round 1, the endpoint made REPORT-ONLY",
        CONTRACT,
        (
            "| `earliest`, `latest` | REPORT-ONLY where the ordinal space has "
            "no room for the value |"
        ),
        ("datetime", "earliest"),
    ),
    (
        "round 2, the endpoint met as far as it could be",
        METHOD,
        (
            "**What remains.** A hand-made description can still publish an "
            "endpoint no cell of its own recorded shape can show, and there "
            "the generator meets what it can, recounts the endpoint from the "
            "written cell, and names it in the report."
        ),
        ("datetime", "latest"),
    ),
    (
        "round 3, the packing fallback, aimed at a fact it never reached",
        METHOD,
        (
            "An implementation MAY still fall back to a deterministic "
            "assignment for `n_whole` where no packing of whole groups meets "
            "every count, and name the miss in the report."
        ),
        ("numeric_unrepresentable", "n_whole"),
    ),
    (
        "round 4, the calendar's own end",
        METHOD,
        (
            "It still has one description the loader accepts and no cell can "
            "show: an endpoint within one offset's distance of either year "
            "the canonical form runs between. That one is recounted from the "
            "written cell and named in the report."
        ),
        ("datetime", "earliest"),
    ),
    (
        "a different obligation: the label levels",
        CONTRACT,
        (
            "Where the published counts leave no room, `levels` is "
            "APPROXIMATED for that column and the report names the achieved "
            "count."
        ),
        ("label", "levels"),
    ),
    (
        "a different obligation: the whole-number fact of a sign column",
        METHOD,
        (
            "Where the strata leave no cell for it, `n_positive` is not "
            "reproduced and the report says so."
        ),
        ("numeric_unrepresentable", "n_positive"),
    ),
    (
        "a different obligation: the column count of the document",
        CONTRACT,
        (
            "A document whose blocks disagree may have `n_columns` met as far "
            "as it can be, with the achieved count named in the report."
        ),
        ("document", "n_columns"),
    ),
    (
        "a different obligation: the offset a column of dates carries",
        METHOD,
        (
            "`time_precision` is REPORT-ONLY on a column the ladder cannot "
            "fill at that detail."
        ),
        ("datetime", "time_precision"),
    ),
)


@pytest.mark.parametrize(
    "why,path,added,key",
    LOWERINGS,
    ids=[entry[0] for entry in LOWERINGS],
)
def test_the_guard_reddens_on_every_lowering_this_repository_has_made(
    tmp_path: pathlib.Path,
    why: str,
    path: pathlib.Path,
    added: str,
    key: "tuple[str, str]",
) -> None:
    """Put each lowering back, in a scratch copy, and watch it go red.

    A guard nobody has watched fail is a guard nobody knows the reach
    of. Each sentence is written into a COPY of the document it belongs
    to, at the front, in the middle and at the end, and every placement
    has to come back as a statement about the fact it names. The three
    placements are the point: the round-2 lowering survived a guard that
    read one cell of one table because it stood four paragraphs below.
    """
    assert key not in dispositions.OPEN, (
        f"{why}: this fact is an open item, so the proof would be vacuous"
    )
    body = path.read_text(encoding="utf-8")
    blocks = body.split("\n\n")
    for place in (0, len(blocks) // 2, len(blocks)):
        mutated = tmp_path / f"{path.stem}-{place}.md"
        mutated.write_text(
            "\n\n".join(blocks[:place] + [added] + blocks[place:]),
            encoding="utf-8", newline="\n",
        )
        # The whole guard, not one helper: the mutated copy replaces its
        # own document in the scan, and the sentence has to come back as
        # a lowering nobody authorized -- which is what turns
        # `test_no_document_states_a_lesser_outcome_for_an_exact_fact`
        # red on the day such a sentence is written.
        caught = _scan(
            tuple(
                (name, mutated if other == path else other)
                for name, other in DOCUMENTS
            )
        )
        undecided = {
            found: statements
            for found, statements in caught.items()
            if found not in dispositions.OPEN
        }
        assert key in undecided, f"{why} at block {place}: nothing caught"


def test_the_guard_reddens_when_the_plan_itself_is_softened(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A future edit that quietly softens the ratified plan is caught.

    The registry is checked against P2-D6, so the last way to lower a
    bar without argument would be to lower P2-D6 and let everything
    agree with it again. Both mechanisms are exercised: a fact whose
    class the plan writes beside its name, and a fact whose bar the plan
    states in a sentence the registry quotes.
    """
    original = PLAN.read_text(encoding="utf-8")
    for before, after in [
        # The class beside the name.
        (
            "`n_zero`, `n_negative`, `std_unrepresentable`",
            "`n_zero` APPROXIMATED, `n_negative`, `std_unrepresentable`",
        ),
        # The sentence the registry quotes.
        (
            "`earliest`, `latest` EXACT-OBSERVABLE in the",
            (
                "`earliest`, `latest` REPORT-ONLY at the calendar's ends "
                "and EXACT-OBSERVABLE otherwise in the"
            ),
        ),
    ]:
        assert before in " ".join(original.split()), before
        softened = " ".join(original.split()).replace(before, after)

        # The real reader is captured before the patch: `_plan_regions`
        # now reads the Phase 3 plan as well, and a replacement that
        # reached for the patched name would call itself.
        def _softened(
            path: pathlib.Path,
            _body: str = softened,
            _real: "typing.Callable[[pathlib.Path], str]" = _flat,
        ) -> str:
            return _body if path == PLAN else _real(path)

        monkeypatch.setattr("test_p2c4f1_disposition_registry._flat", _softened)
        assert _plan_violations(dispositions.REGISTRY) != []
        monkeypatch.undo()


# -- round 5's eight scratch attacks, run against the new design -------
#
# Round 5 mutated a scratch copy eight ways and SIX survived all 19
# guard tests. Each one is reproduced below against the design that
# replaced the one it defeated, and each has to make at least one named
# check go red. The tests carry the reviewer's own descriptions so a
# reader can line them up with the attack table in
# `docs/plans/reviews/phase-2-code-review-round-5.md`.

# A genuine sentence of the ratified plan that says nothing whatever
# about `n_missing`. Round 5's two registry attacks each leaned on a
# quotation exactly like this one.
UNRELATED_PLAN_TEXT = "Domains are widened first"


def _with_document(
    tmp_path: pathlib.Path, relative: str, body: str
) -> "dict[str, pathlib.Path]":
    """The three documents, with one of them replaced by a scratch copy."""
    copy = tmp_path / pathlib.Path(relative).name
    copy.write_text(body, encoding="utf-8", newline="\n")
    substituted = dict(RELATIVE)
    substituted[relative] = copy
    return substituted


def _document_attack(
    tmp_path: pathlib.Path, relative: str, body: str
) -> "list[str]":
    """Which checks go red when one document is replaced by ``body``."""
    substituted = _with_document(tmp_path, relative, body)
    red: list[str] = []
    if _unsealed(substituted):
        red.append("the document seal")
    caught = _scan(
        tuple(
            (name, substituted[relative] if path == RELATIVE[relative] else path)
            for name, path in DOCUMENTS
        )
    )
    if any(key not in dispositions.OPEN for key in caught):
        red.append("the phrase scan")
    return red


CONTRACT_NAME = "docs/spec/profile-contract-v4.md"
METHOD_NAME = "docs/spec/generation-method-v1.md"
PLAN_NAME = "docs/plans/phase-2-generator.md"

# Eight hundred characters of ordinary specification prose, so a lesser
# statement can be stood further from a fact's name than the phrase
# scan's attribution window reaches.
FILLER = (
    "The rule above is stated once and applies to every column of the "
    "kind named, in the order the schema fixes, without regard to the "
    "seed the run was given or the order the rows were written in. "
) * 4


def test_attack_one_rephrasing_rather_than_keyword(
    tmp_path: pathlib.Path,
) -> None:
    """Round 5: a lesser outcome beside `latest`, in words nobody listed.

    "Added a sentence beside `latest` saying the generated value is
    permitted to differ and then governs, without using a `LESSER` tuple
    phrase." It survived, 19 passed. The sentence carries no listed
    vocabulary, so the phrase scan still cannot see it -- and it changes
    the matrix row it was written into, so the seal refuses the row.
    """
    body = CONTRACT.read_text(encoding="utf-8")
    mark = "which is the ratified plan's own wording."
    assert mark in body
    red = _document_attack(
        tmp_path,
        CONTRACT_NAME,
        body.replace(
            mark,
            mark
            + " Where the ordinal space is crowded the generated value is "
            "permitted to differ from the published one, and the "
            "generated value then governs.",
            1,
        ),
    )
    assert red, "the rephrased lowering was accepted"


def test_attack_two_moving_a_lowering_between_documents(
    tmp_path: pathlib.Path,
) -> None:
    """Round 5: a recognized lowering moved into the plan. It was caught.

    This one the old guard already stopped, and it still does -- by both
    checks now, since moving a sentence into a document also writes a
    passage nobody sealed.
    """
    red = _document_attack(
        tmp_path,
        PLAN_NAME,
        PLAN.read_text(encoding="utf-8")
        + "\n\nA description publishing an endpoint no cell of its own "
        "recorded shape can show has `latest` met as far as it could "
        "be, recounted from the written cell and named in the report.\n",
    )
    assert "the document seal" in red
    assert "the phrase scan" in red


def test_attack_three_distance_from_the_fact_name(
    tmp_path: pathlib.Path,
) -> None:
    """Round 5: `latest` stood more than the window from `may miss`.

    "Put `latest` more than 600 characters from a recognized `may miss`
    sentence." It survived, 19 passed. Distance is exactly what a seal
    does not measure.
    """
    red = _document_attack(
        tmp_path,
        METHOD_NAME,
        METHOD.read_text(encoding="utf-8")
        + f"\n\nG7.5 governs `latest` on every column. {FILLER} On such a "
        "column the published end may miss the written one, and the "
        "written one is what the report records.\n",
    )
    assert "the document seal" in red


def test_attack_four_nearest_name_attribution(
    tmp_path: pathlib.Path,
) -> None:
    """Round 5: a nearer report-only name captured the lowering.

    "Put a real lowering of `latest` beyond the 100-character together
    range and a closer `format may miss` phrase. The phrase was assigned
    to the report-only name." It survived, 19 passed. The seal does not
    attribute anything to anybody, so there is nothing to capture.
    """
    red = _document_attack(
        tmp_path,
        METHOD_NAME,
        METHOD.read_text(encoding="utf-8")
        + "\n\nG7.5 records that `latest` is written from the ordinal the "
        "interior ranks use, and the column's own `format` may miss the "
        "source family it named.\n",
    )
    assert "the document seal" in red


def test_attack_five_a_role_ambiguous_field_name(
    tmp_path: pathlib.Path,
) -> None:
    """Round 5: a class stated for a name whose class depends on the role.

    "Added 'For numeric roles, `n_distinct` is REPORT-ONLY when the
    ladder is crowded.'" It survived, 19 passed, because the phrase scan
    skips all three names that carry two classes between roles. The seal
    reads passages, not names, so the exclusion does not reach it.
    """
    red = _document_attack(
        tmp_path,
        CONTRACT_NAME,
        CONTRACT.read_text(encoding="utf-8")
        + "\n\nFor numeric roles, `n_distinct` is REPORT-ONLY when the "
        "ladder is crowded.\n",
    )
    assert "the document seal" in red


def _mutated_registry(**changes: object) -> "list[dispositions.Fact]":
    """The registry with one fact replaced, as a scratch copy in memory."""
    key = ("universal", "n_missing")
    return [
        fact._replace(**changes)  # type: ignore[arg-type]
        if (fact.group, fact.field) == key
        else fact
        for fact in dispositions.REGISTRY
    ]


def test_attack_six_editing_the_registrys_own_authorization() -> None:
    """Round 5: an authorization propped up by an unrelated plan sentence.

    "Authorized `n_missing` with the phrase `may miss` and quoted an
    unrelated exact sentence that already exists in the plan, then added
    '`n_missing` may miss'." It survived, 19 passed, because the
    authorization check only proved that some phrase and some plan text
    each existed. The authorization list is now one of the three sealed
    surfaces, so the edit is refused without anybody judging the
    quotation.
    """
    mutated = _mutated_registry(
        authorized=(("may miss", UNRELATED_PLAN_TEXT),)
    )
    assert UNRELATED_PLAN_TEXT in _flat(PLAN), "the quotation is genuine"
    marks = dispositions.judgment(mutated)
    assert marks != disposition_seal.JUDGMENT
    assert marks["authorizations"] != (
        disposition_seal.JUDGMENT["authorizations"]
    )
    # ...and a second, independent refusal: the authorization declares
    # no fact, no plan region and no lesser class, so the plan parse
    # rejects it whether or not anybody looks at the seal.
    assert any("n_missing" in line for line in _plan_violations(mutated))


def test_attack_seven_editing_the_registrys_own_disposition() -> None:
    """Round 5: a fact quietly moved to REPORT-ONLY in the registry.

    "Changed `n_missing` to REPORT-ONLY, supplied unrelated existing
    `plan_words`, and changed its contract row accordingly." It
    survived, 19 passed, because a quoted sentence bypassed the parse of
    the plan. Three independent checks refuse it now: the sealed class
    surface, the plan parse -- which no longer lets a quotation excuse a
    class the plan does not write beside that name -- and the contract
    matrix, which is compared against the registry in both directions.
    """
    mutated = _mutated_registry(
        disposition=dispositions.REPORT_ONLY,
        plan_words=UNRELATED_PLAN_TEXT,
    )
    marks = dispositions.judgment(mutated)
    assert marks["classes"] != disposition_seal.JUDGMENT["classes"]
    broken = _plan_violations(mutated)
    assert any("n_missing" in line for line in broken), broken
    # ...and the matrix disagrees, whichever side is edited: unchanged,
    # the contract still heads the row with the exact class.
    assert any("n_missing" in line for line in _matrix_violations(mutated))


def test_attack_eight_the_open_escape_hatch(
    tmp_path: pathlib.Path,
) -> None:
    """Round 5: an entry citing an item the newest record only mentions.

    "Added an `n_missing` lowering and OPEN[('universal', 'n_missing')] =
    'P2-C4-F1'. The lexicographically newest review already mentions that
    old item." It survived, 19 passed, and the reviewer noted it would
    survive again after the round-5 record landed, because a closure
    record has to name what it closed.

    Both halves are refused now. The item is parsed for its own round
    number, its heading and the verdict, so a closed item cannot carry an
    entry; and the lowering the entry would excuse is a passage nobody
    sealed.
    """
    number, text = _newest_review()
    assert "P2-C4-F1" in text, "the closure record names the closed item"
    stale = {("universal", "n_missing"): "P2-C4-F1"}
    assert _open_violations(stale, number, text) != []
    red = _document_attack(
        tmp_path,
        METHOD_NAME,
        METHOD.read_text(encoding="utf-8")
        + "\n\nOn a crowded column `n_missing` may miss the published "
        "count, and the report names it.\n",
    )
    assert "the document seal" in red


def test_attack_eight_again_with_an_item_of_the_current_round(
    tmp_path: pathlib.Path,
) -> None:
    """...and citing a CURRENT item does not open the hatch either.

    The round-number rule alone would still let somebody carry a new
    lowering under a genuinely open item of this round -- and the record
    that verifies closure necessarily names every open item. The second
    condition is what settles it: an entry may excuse only prose that
    was already sealed, and a lowering somebody has just written is not.
    """
    number, text = _newest_review()
    live = _items_left_open(number, text)
    assert live
    current = min(live)
    fresh = {("universal", "n_missing"): current}
    assert _open_violations(fresh, number, text) == []
    red = _document_attack(
        tmp_path,
        METHOD_NAME,
        METHOD.read_text(encoding="utf-8")
        + "\n\nOn a crowded column `n_missing` may miss the published "
        "count, and the report names it.\n",
    )
    assert "the document seal" in red
    assert "the phrase scan" in red


# -- what the guard covers, stated rather than left quiet ---------------


def test_the_three_names_prose_cannot_settle_are_named_and_no_others(
) -> None:
    """What the PHRASE SCAN does not cover, and what covers it instead.

    Three field names carry two classes between roles, so a sentence
    that does not say which role it means cannot be read: `n_distinct`
    and `n_distinct_folded` are exact on most roles and APPROXIMATED on
    a column of dates, and `n_rows` is the document's row count at the
    top level and a LOADER-ONLY echo inside a numeric block. Those three
    are checked where the role IS known -- the contract's per-role
    tables and the plan's per-role paragraphs, both read above -- and
    the seal covers them the same way it covers every other passage,
    which is what round 5's role-ambiguity attack goes through now. A
    fourth name joining them is a change in what the phrase scan can
    see, so the set is asserted rather than described.
    """
    assert AMBIGUOUS == {"n_distinct", "n_distinct_folded", "n_rows"}
    for name in sorted(AMBIGUOUS):
        holders = [
            fact for fact in dispositions.REGISTRY if fact.field == name
        ]
        assert len({fact.disposition for fact in holders}) > 1, name
        for group, section in dispositions.CONTRACT_SECTIONS.items():
            if (group, name) not in dispositions.BY_KEY:
                continue
            rows = _matrix()[section]
            assert any(name in names for names, _text in rows), (
                f"{group}/{name} is in no contract row"
            )


def test_the_scan_reaches_every_exact_fact_and_all_three_documents(
) -> None:
    """The vacuity floor for the scan itself.

    A scan that read no document, or covered a handful of fields, would
    pass every mutation above by accident. This asserts its reach: the
    two specifications and the plan, and a real inventory of facts whose
    class is exact.
    """
    exact = [
        fact
        for fact in dispositions.REGISTRY
        if fact.disposition in dispositions.EXACT
    ]
    assert len(exact) >= 70, len(exact)
    # Ten groups: Phase 2's nine, plus `affixed`, whose own facts the
    # Phase 4 plan disposes because the role did not exist when the
    # Phase 2 matrix was written.
    # Eleven since the clock role joined: its four exactly observable
    # facts are a group of their own, disposed by the Phase 4 plan
    # rather than by the version 4 matrix, which predates the role.
    assert len({fact.group for fact in exact}) == 11
    for _name, path in DOCUMENTS:
        assert len(_statements(path)) > 150, path.name
    # ...and every document is really opened by the scan, which a
    # mistyped path would otherwise hide.
    counted = _scan((("plan", PLAN),))
    assert isinstance(counted, dict)


def test_the_registry_reaches_every_key_the_producer_emits() -> None:
    """The registry is not a list of the fields somebody remembered.

    The chain is: `test_every_key_the_producer_emits_has_a_disposition`
    in `test_p2c1f4_approximation_bounds.py` asserts that every key a
    genuine producer description carries is disposed by the contract's
    matrix, and the matrix check above asserts that the matrix is
    exactly this registry. So a key the producer publishes and the
    registry does not hold is caught by the pair. This asserts the
    second link is really there -- that the two checks name the same
    tables -- because a registry checked against nothing would satisfy
    every other test in this file.
    """
    matrix = _matrix()
    for group, section in dispositions.CONTRACT_SECTIONS.items():
        assert matrix[section], f"{group}: {section} has no rows"
    assert set(dispositions.CONTRACT_SECTIONS) == {
        fact.group
        for fact in dispositions.REGISTRY
        if fact.group not in dispositions.GROUPS_OUTSIDE_THE_VERSION_4_MATRIX
    }
