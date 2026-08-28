"""The two normative documents say one thing about each question.

Review item P2-C1-F8. The profile contract and the generation method
were written in parallel and reviewed for the first time only after the
code existed. Four questions had two answers between them, and on each
one an independent implementer following one document would have built
something the other document refuses:

* HOW A NUMBER IS SPELLED IN THE PROFILE. The contract's serialization
  rules said numbers take "the shortest form that reads back as the same
  value, integers without a fractional part or exponent", its loader
  table said a trailing `.0` is changed by re-serialization, and its own
  type rule T1 said the opposite -- that `2.0` comes back unchanged.
  The shipped serializer agrees with T1. A loader written from the other
  two sentences refuses a genuine profile whose `mean` reads `2.0`.
* WHICH SPELLINGS A TWIN NUMERIC CELL MAY TAKE. The contract's closing
  paragraph on `numeric_styles` said the twin may write only owner
  decision 8's family -- the canonical spelling, leading zeros and a
  leading plus -- while the same section requires each published style
  to be written in its published count, and the six styles include
  `decimal`. Given eleven `decimal` cells, one document says write a
  point and the other says do not.
* WHAT A CELL'S STYLE IS. The contract counts a style by reading the
  finished text; the method assigned a style to a cell without asking
  whether that cell's value could be spelled that way. On a column of
  values that are not whole, every canonical spelling already carries a
  point, so a cell the generator called `plain` comes back `decimal`.
* WHAT HAPPENS TO A LADDER RUNG THAT HOLDS NOTHING. The contract accepts
  one and the loader does too; the method said it was a loader refusal,
  which left the rule to whichever module met it first.

The plan carried the same class of defect in its own record: several
passages miscounted the parser bounds where its revision 5 ruling and
the contract say two, and its closing sentence said no Phase 2 code
exists and nothing is ratified, which its own status block contradicts.

A first repair of that record banned the single phrase "four bounds",
which is not the defect. Three passages said the same thing in other
words and survived: acceptance criterion 2 asked for "the four fixed
limits" AND for "the producer bounds" that P2-D2 had withdrawn, the
closure trail said "four fixed numbers", and residual R-P2-10 still
said "three structural bounds" from before round 5 removed the
container-entry limit. The ban below is therefore on the COUNT beside
any noun these documents use for a bound, and it carries its own
vacuity floor built from the exact phrases that slipped through.

WHAT THIS FILE CHECKS, AND IN TWO DIRECTIONS. A one-directional check is
worth little: deleting a sentence satisfies a ban and adding an unread
sentence satisfies a requirement. So every rule below is checked both as
BEHAVIOUR -- what the shipped code does with a genuine description --
and as TEXT, positively (the reconciled rule is stated) and negatively
(the withdrawn wording is gone from both documents). A behaviour check
alone would pass while the documents still disagreed; a text check alone
would pass on prose nothing implements.
"""

import collections
import json
import pathlib

import fixtures
from synthtwin import (
    canonical,
    contract,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    taxonomy,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = REPO_ROOT / "docs" / "spec" / "profile-contract-v4.md"
METHOD = REPO_ROOT / "docs" / "spec" / "generation-method-v1.md"
PLAN = REPO_ROOT / "docs" / "plans" / "phase-2-generator.md"

# The float spellings both documents name as their boundary examples:
# the contract's section 3.2.1 for a number in the profile, the method's
# G6.2 for a numeric cell in the twin. One grammar, so one list.
BOUNDARY_FLOATS = (
    2.0,
    5.0,
    -2.5,
    0.1,
    0.0001,
    1e-05,
    1e15,
    1e16,
    1e100,
)


def _words(path: pathlib.Path) -> str:
    """One document as lower-case text with its line wrapping removed."""
    return " ".join(path.read_text(encoding="utf-8").lower().split())


def _described(
    folder: pathlib.Path, values: "list[str]"
) -> "tuple[dict, contract.Profile]":
    """Write a one-column table, describe it, and load the description.

    THE FLOOR IS NAMED, NOT TAKEN FROM THE DEFAULT. Two of the style
    questions below are about the `(withheld)` remainder -- what a
    description does with a spelling too few cells share to publish --
    and a remainder exists only above a floor. Since the owner's ruling
    (plan amendment A-P4-37) the default floor is 1, at which nothing
    is ever pooled and no `(withheld)` key is written at all, so every
    description here is built at the floor of eleven these cases were
    written against.
    """
    path = fixtures.write(
        folder, "table.csv", fixtures.single_column_table("amount", values)
    )
    document = profile.build_document(
        reading.read_table(str(path)),
        taxonomy.Settings(small_cell_floor=11),
        [],
    )
    target = fixtures.write_profile(folder, "table-profile.json", document)
    return document, contract.load_profile(str(target))


def _styles_written(twin: generation.Twin) -> "dict[str, int]":
    """Recount the first column's spelling styles from its own cells."""
    counted: collections.Counter[str] = collections.Counter()
    for cell in twin.columns[0]:
        if cell != "":
            counted[taxonomy.numeric_style(cell)] += 1
    return dict(counted)


# -- the canonical number grammar --------------------------------------


def test_a_whole_valued_statistic_keeps_its_point(
    tmp_path: pathlib.Path,
) -> None:
    """A genuine profile writes `6.0`, and its own loader accepts it.

    This is the sentence the contract now states in 3.2.1 and the one an
    independent loader was previously told to refuse.
    """
    document, loaded = _described(tmp_path, [str(n) for n in range(1, 12)])
    text = canonical.serialize(document)

    assert document["columns"][0]["mean"] == 6.0
    assert '"mean": 6.0' in text
    assert loaded.columns[0].name == "amount"
    assert loaded.columns[0].facts.mean == 6.0


def test_the_two_kinds_of_number_are_spelled_as_the_contract_says() -> None:
    """A whole number is `2`; the same value held as a fraction is `2.0`."""
    assert canonical.serialize({"x": 2}) == '{\n  "x": 2\n}\n'
    assert canonical.serialize({"x": 2.0}) == '{\n  "x": 2.0\n}\n'
    assert canonical.serialize({"x": 1e16}) == '{\n  "x": 1e+16\n}\n'
    assert canonical.serialize({"x": 1e-05}) == '{\n  "x": 1e-05\n}\n'
    assert canonical.serialize({"x": 1e15}) == (
        '{\n  "x": 1000000000000000.0\n}\n'
    )


def test_one_float_grammar_serves_the_profile_and_the_twin() -> None:
    """Contract 3.2.1 and method G6.2 are the same rule, checked as one.

    The profile writes a number through the canonical serializer and the
    twin writes a numeric cell through the method's canonical spelling.
    Both are "the shortest text that reads back as this value", so for
    every value either both are right or both are wrong -- which is the
    property that makes stating the rule twice safe.
    """
    for value in BOUNDARY_FLOATS:
        in_the_profile = json.loads(canonical.serialize({"x": value}))
        as_a_twin_cell = generation._canonical_number(value, False)
        assert in_the_profile["x"] == value
        assert as_a_twin_cell == repr(value)
        assert f'"x": {as_a_twin_cell}' in canonical.serialize({"x": value})


def test_the_round_trip_cannot_catch_a_trailing_point_zero() -> None:
    """`2.0` survives; `1.0e2` does not. The table now says both."""
    kept = '{\n  "x": 2.0\n}\n'
    assert canonical.serialize(json.loads(kept)) == kept

    changed = '{\n  "x": 1.0e2\n}\n'
    assert canonical.serialize(json.loads(changed)) != changed


def test_the_contract_states_the_number_grammar_once() -> None:
    """The grammar is stated, and the sentence that contradicted it is gone."""
    text = _words(CONTRACT)

    assert "the canonical number grammar" in text
    assert "is the canonical text of the float two" in text
    assert "a trailing `.0` on a whole-valued number passes this check" in text

    assert "integers without a fractional part or exponent" not in text
    assert "trailing `.0` on an integer" not in text


# -- the numeric spelling family ---------------------------------------


def test_both_documents_name_the_same_six_styles() -> None:
    """The six style names are one list in the code and both documents."""
    assert contract.NUMERIC_STYLES == (
        "plain",
        "leading_zero",
        "leading_plus",
        "decimal",
        "exponent_lower",
        "exponent_upper",
    )
    for document in (CONTRACT, METHOD):
        text = _words(document)
        for style in contract.NUMERIC_STYLES:
            assert f"`{style}`" in text


def test_neither_document_narrows_the_twin_to_three_styles() -> None:
    """The withdrawn family sentence is gone and the division is stated."""
    contract_text = _words(CONTRACT)
    method_text = _words(METHOD)
    plan_text = _words(PLAN)

    assert (
        "the styles it may write are exactly owner decision 8's family"
        not in contract_text
    )
    assert "the styles it may write are the six of section 7.5.3" in (
        contract_text
    )
    assert "the family the twin may invent from" in method_text
    assert "the first clause governs" in plan_text


def test_a_published_decimal_count_is_written_with_a_point(
    tmp_path: pathlib.Path,
) -> None:
    """Twelve `decimal` cells published, twelve decimal cells written.

    Under the withdrawn reading the twin would have written twenty-four
    plain cells and the reader's inferred type -- the whole reason owner
    decision 10 exists -- would have been lost.
    """
    values = [str(n) for n in range(1, 13)] + [f"{n}.0" for n in range(20, 32)]
    document, loaded = _described(tmp_path, values)

    assert document["columns"][0]["numeric_styles"] == {
        "plain": 12,
        "decimal": 12,
    }

    twin = generation.generate(loaded, 0)
    assert _styles_written(twin) == {"plain": 12, "decimal": 12}


def test_the_withheld_remainder_is_recounted_as_plain(
    tmp_path: pathlib.Path,
) -> None:
    """Thirty plain and three held back come back as thirty-three plain.

    TWO WORDINGS ARE WITHDRAWN, AND BOTH ARE BANNED HERE RATHER THAN
    REPEATED. The contract first called the remainder the cells "that
    fall in no published style", which nothing can satisfy while
    `plain` is itself published: every numeric cell text lands in one
    of the six. It then added the whole remainder to `plain`, which the
    Phase 3 plan withdrew in turn (P3-D8.1): a published end carrying a
    decimal point has a cell with no point-free spelling at all, so
    that rule owed a form no conforming generator could write.

    The rule now is that a pooled cell is spelled by its own value, and
    the recount is the identity of contract 7.5.7. On these values
    every pooled cell IS whole, so all three are written plainly and
    the column reads back exactly as it did -- which is the point: the
    amendment moved no byte of the ordinary case, only the obligation
    on the case that could not be met.
    """
    values = [str(n) for n in range(1, 31)] + ["+101", "+102", "+103"]
    document, loaded = _described(tmp_path, values)

    assert document["columns"][0]["numeric_styles"] == {
        "plain": 30,
        "(withheld)": 3,
    }

    twin = generation.generate(loaded, 0)
    assert _styles_written(twin) == {"plain": 33}
    assert [
        note for note in twin.deviations if note.fact == "numeric_styles"
    ] == []

    text = _words(CONTRACT)
    assert "a cell pooled into `(withheld)` is written by its own value" in text
    assert "that fall in no published style" not in text
    assert (
        "the published map with the `(withheld)` remainder added to"
        not in text
    )


def test_a_style_map_the_values_can_carry_is_written_exactly(
    tmp_path: pathlib.Path,
) -> None:
    """The half of G6.4 that PLACES, on the case round 2 named.

    A column of eleven values carrying a point and forty whole ones
    publishes `integer_valued: false` with a `plain` quota of forty. The
    twin used to write nought plain cells and fifty-one decimal ones and
    name both misses, which review item P2-C2-F2 refused: the source's
    own values prove the exact map is reachable -- plain on the forty
    whole values, a point on the eleven fractional ones -- and a named
    miss is not permission to leave a placeable form unplaced. The map
    now comes out exactly, so nothing about it reaches the report at
    all.
    """
    values = [f"{n}.5" for n in range(1, 12)] + [
        str(100 + n) for n in range(40)
    ]
    document, loaded = _described(tmp_path, values)

    assert document["columns"][0]["numeric_styles"] == {
        "plain": 40,
        "decimal": 11,
    }
    assert document["columns"][0]["integer_valued"] is False

    twin = generation.generate(loaded, 0)
    assert _styles_written(twin) == {"plain": 40, "decimal": 11}
    assert [
        note for note in twin.deviations if note.fact == "numeric_styles"
    ] == []


def test_a_style_the_twin_cannot_place_is_named_in_the_report(
    tmp_path: pathlib.Path,
) -> None:
    """The half of G6.4 that SPEAKS, exercised end to end.

    Placing a form is not always possible, and where it is not the
    report owes the reader a sentence. THE FIXTURE HERE HAS MOVED
    TWICE. Review item P2-C4-F3 moved it off the 51-cell column whose
    own values prove its map, which the twin writes exactly. The
    Phase 3 plan (P3-D8.1) moved it again: the producer column of forty
    named `plain` cells and six pooled ones, whose two published ends
    carry points, was a miss only because the withdrawn rule owed every
    pooled cell the plain form. A pooled cell has no published form, so
    it is now spelled by its own value, and that column meets its map.

    What still cannot be placed is a NAMED count, which no producer
    emits and a hand-written description can: forty-six `leading_plus`
    cells on a column two of whose cells must read back as numbers with
    no point-free spelling. Forty-four is the ceiling, the twin reaches
    it, and the report names the published count beside the achieved
    one.
    """
    values = ["0.5"] * 3 + ["7"] * 40 + ["9.25"] * 3
    document, loaded = _described(tmp_path, values)

    assert document["columns"][0]["numeric_styles"] == {
        "plain": 40,
        "(withheld)": 6,
    }
    assert document["columns"][0]["integer_valued"] is False

    twin = generation.generate(loaded, 0)
    assert _styles_written(twin) == {"plain": 44, "decimal": 2}
    quiet = [note for note in twin.deviations if note.fact == "numeric_styles"]
    assert quiet == [], [note.published for note in quiet]

    document["columns"][0]["numeric_styles"] = {"leading_plus": 46}
    # P5 ties the census to the forms map: a map naming no `decimal`
    # cells is a map whose census names no width, and a document that
    # kept the old census would be refused before this placement is
    # reached.
    document["columns"][0]["fraction_widths"] = {}
    target = fixtures.write_profile(tmp_path, "edited-profile.json", document)
    edited = contract.load_profile(str(target))
    twin = generation.generate(edited, 0)
    written = _styles_written(twin)
    assert written.get("leading_plus", 0) == 44, (
        "this fixture no longer reaches the corner it was built for"
    )

    named = [note for note in twin.deviations if note.fact == "numeric_styles"]
    assert named, "the twin missed its published style map and said nothing"
    assert any("leading_plus" in note.published for note in named), [
        note.published for note in named
    ]
    text = rendering.report(edited, twin)
    assert "leading_plus form" in text


def test_a_column_that_meets_its_style_map_is_left_unremarked(
    tmp_path: pathlib.Path,
) -> None:
    """The vacuity floor for the check above.

    A recount that named a miss on every column would be noise, and a
    reader who saw it every run would stop reading it. An ordinary
    whole-number column meets its map exactly, so the report says
    nothing about it.
    """
    values = [str(n) for n in range(1, 41)] + [f"0{n}" for n in range(1, 41)]
    _document, loaded = _described(tmp_path, values)

    twin = generation.generate(loaded, 0)

    assert [
        note for note in twin.deviations if note.fact == "numeric_styles"
    ] == []


def test_one_ladder_answers_the_style_question_on_both_sides() -> None:
    """The describer and the generator read a form off the same rule.

    The generator may not import the describing module, so before this
    the ladder existed where only the describer could reach it and the
    twin's own forms were never recounted. A copy would have drifted;
    this asserts there is one.
    """
    assert taxonomy.numeric_style is not parsing.numeric_style
    for text in ("012.5", "12.5", "012", "+5", "5", "1E5", "1e5", "-0.5"):
        assert taxonomy.numeric_style(text) == parsing.numeric_style(text)
    for name in (
        "STYLE_PLAIN",
        "STYLE_LEADING_ZERO",
        "STYLE_LEADING_PLUS",
        "STYLE_DECIMAL",
        "STYLE_EXPONENT_LOWER",
        "STYLE_EXPONENT_UPPER",
    ):
        assert getattr(taxonomy, name) == getattr(parsing, name)


def test_a_style_is_what_the_finished_text_classifies_as() -> None:
    """Both documents say a style is read off the cell, not remembered.

    `012.5` is a leading zero in front of a decimal point, and the
    contract's own first-match ladder calls it `decimal`. A generator
    that called it `leading_zero` would report a count nothing can
    recount.
    """
    assert taxonomy.numeric_style("012.5") == "decimal"
    assert taxonomy.numeric_style("12.5") == "decimal"
    assert taxonomy.numeric_style("012") == "leading_zero"

    contract_text = _words(CONTRACT)
    method_text = _words(METHOD)
    assert "this ladder is what a twin cell's style is" in contract_text
    assert "what \"this cell's value can wear\" means, in full" in (
        method_text
    )
    assert (
        "a quota that cannot be placed is a miss, and naming it is not a "
        "licence to leave it unplaced" in method_text
    )


# -- a ladder rung that holds nothing ----------------------------------


def test_a_rung_that_holds_nothing_loads_and_generates(
    tmp_path: pathlib.Path,
) -> None:
    """One rule, stated in the method, carried by the loader and the code."""
    document, _loaded = _described(tmp_path, [str(n) for n in range(1, 41)])
    document["columns"][0]["percentiles"]["p50"] = None
    target = fixtures.write_profile(tmp_path, "table-profile.json", document)

    loaded = contract.load_profile(str(target))
    twin = generation.generate(loaded, 0)
    written = [float(cell) for cell in twin.columns[0] if cell != ""]

    assert min(written) == 1.0
    assert max(written) == 40.0


def test_the_method_no_longer_calls_a_null_rung_a_refusal() -> None:
    """The withdrawn sentence is gone and the fill rule is in its place."""
    method_text = _words(METHOD)
    contract_text = _words(CONTRACT)

    assert "a null rung is not a refusal" in method_text
    assert "the nearest rung below it that holds a number" in method_text
    assert (
        "a null rung or a descending pair is a loader refusal"
        not in method_text
    )
    assert "the value a generator uses in its place is fixed by" in (
        contract_text
    )


def test_datetime_cardinality_has_one_envelope() -> None:
    """G12.5 owns it in both documents; G5.6 no longer claims it too.

    The contract half of this check read the METHOD file, so the
    contract was never consulted and the assertion could not fail for
    the reason it names.
    """
    method_text = _words(METHOD)
    contract_text = _words(CONTRACT)

    assert "approximated under **the envelope of g12.5**" in method_text
    assert "two-sided envelope of g5.6 with `g_max = 1`" not in method_text
    assert "g12.5" in contract_text
    # The contract must POINT at the method's envelope rather than fix a
    # second one of its own, which is what having two documents answer
    # one question meant in the first place.
    assert "generation-method-v1.md` g12.5" in contract_text


# -- the plan's own record ---------------------------------------------


# Every way the withdrawn count was actually written. Banning the one
# phrase "four bounds" left two passages standing that said the same
# thing in other words -- "the four fixed limits" in the acceptance
# criteria and "four fixed numbers" in the closure trail -- so the check
# passed while the plan still contradicted its own P2-D2 ruling. The ban
# is on the COUNT beside any of the nouns these documents use for it.
_BOUND_NOUNS = ("bounds", "limits", "numbers", "caps", "ceilings")
_WITHDRAWN_COUNTS = ("four", "three", "4", "3")


def _miscounted_bounds(text: str) -> "list[str]":
    """Every phrase in `text` that gives the parser bounds a stale count."""
    found: list[str] = []
    for count in _WITHDRAWN_COUNTS:
        for noun in _BOUND_NOUNS:
            for middle in ("", " fixed", " parser", " structural", " loader"):
                phrase = f"{count}{middle} {noun}"
                if phrase in text:
                    found = found + [phrase]
    return found


def test_the_plan_and_the_contract_count_two_parser_bounds() -> None:
    """Exactly two, in every passage of both documents.

    P2-D2 removed the container-entry limit and withdrew every
    producer-side cap, leaving nesting depth 32 and numeric-token length
    64. A passage still counting more is not a wording preference: an
    implementer reading the acceptance criteria would build limits the
    contract forbids, which is the defect P2-C1-F8 named.
    """
    plan_text = _words(PLAN)
    contract_text = _words(CONTRACT)

    assert _miscounted_bounds(plan_text) == [], _miscounted_bounds(plan_text)
    assert _miscounted_bounds(contract_text) == [], _miscounted_bounds(
        contract_text
    )
    assert "two bounds" in plan_text
    assert "two bounds" in contract_text
    # The two that remain are named, so a reader never has to count them.
    for text in (plan_text, contract_text):
        assert "32" in text and "64" in text


def test_the_bound_count_check_would_notice_the_wording_that_slipped() -> None:
    """The ban's own vacuity floor.

    These are the exact phrases that stood in the plan while a check
    banning only "four bounds" passed. If the ban ever narrows back to
    one spelling, this turns red.
    """
    for phrase in (
        "the four fixed limits and a catalogued failure surface",
        "p2-d2, four fixed numbers",
        "four bounds",
        "three structural bounds",
    ):
        assert _miscounted_bounds(phrase) != [], phrase
    assert _miscounted_bounds("the two bounds p2-d2 fixes") == []


def test_the_plan_no_longer_requires_a_producer_side_limit() -> None:
    """P2-D2 withdrew it; the acceptance criteria said it still ships.

    Round 4 ruled that limiting the producer narrows a range of tables
    Phase 1 had already undertaken to handle, and P2-D2 removed every
    such limit. Acceptance criterion 2 went on listing "the producer
    bounds" among the things profile v4 ships, so the plan required the
    very thing its own decision had taken out.
    """
    plan_text = _words(PLAN)

    assert "and the producer bounds" not in plan_text
    assert "no producer-side cap" in plan_text


def test_the_plan_records_what_is_built_and_what_is_ratified() -> None:
    """The closing record matches the status block instead of denying it.

    Round 5 found the record stopping at code review round 1 while four
    further rounds had run (item P2-C5-C1): an owner reading the
    canonical plan during a release decision would have seen eight
    round-1 blockers and none of the four the final round leaves open.
    So the history is asserted ROUND BY ROUND rather than through one
    round's phrasing, together with the verdict the last round reached.
    """
    plan_text = _words(PLAN)

    assert "no part of phase 2 is implemented" not in plan_text
    assert "neither the code nor either specification is ratified" in plan_text
    for said in (
        "round 1** (2026-08-11) — reject, eight blocking items, p2-c1-f1 to",
        "round 2** (2026-08-11) — reject, eight blocking items, p2-c2-f1 to",
        "round 3** (2026-08-11) — reject, blocked on p2-c3-f1 and",
        "round 4** (2026-08-12) — reject, blocked on p2-c4-f1 to p2-c4-f4",
        "round 5** (2026-08-12), the last authorized round",
        "blocked on p2-c5-f1, p2-c5-f2, p2-c5-f3 and p2-c5-f4",
        "with p2-c5-c1 alone carryable",
    ):
        assert said in plan_text, said
    # ...and the record may not turn a deferred control into a live one
    # while it is being brought up to date.
    assert "claims no control that `security.md` lists as deferred" in plan_text
    assert "repairs made after round 5 do not change that" in plan_text
