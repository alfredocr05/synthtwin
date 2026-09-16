"""The generation transform against an oracle it did not produce (P2-D7).

The charter forbids generated values being their own oracle. So
`tools/reference/make_generation_reference_vectors.py` implements
`docs/spec/generation-method-v1.md` from that document alone, importing
neither this package nor any numeric library, and its output is
committed as a provenance-manifest fixture: CI rebuilds it from the
generator and byte-compares it on every run, so the oracle cannot drift
towards the implementation without the provenance guard going red.

Two halves are tested here, and they are different claims.

**The implementation reproduces the committed cells.** The vectors are a
pure function of GIVEN words -- the oracle draws none and holds no
generator, because the fixture guard refuses an import of `ctypes` and
numpy imports `ctypes`. The words each case carries are the opening
words of the single stream at the seed named in `SEEDS` below, which is
what lets the same case be put through `generate` and compared cell for
cell. That binding is asserted here rather than assumed, and so is the
property section G3.3 rests on: the word sequence does not depend on how
the calls are cut.

**Every number the vector file publishes was proved.** The proof layer
is only worth what it refuses, so the tests at the bottom of this file
try to make it certify a lie, exactly as `tests/test_oracle_proof_layer.py`
does for the Phase 1 vectors: a number outside a wrapper, a whole number
under one, a number inside a tuple the JSON encoder writes as an array,
a container the walk has no rule for, and each of those driven through
the whole generator so that nothing is written.

All nine cases are asserted the same way. The identifier case once
disagreed and was carried as a strict expected failure while the
implementation was repaired to the oracle rather than the other way
round: it missed the fold collisions method section G9.3 requires and
wrote ten cells that were figures and nothing else against a published
count of none. The vectors were never adjusted to match the code they
exist to check, and `tests/test_generation.py` now holds a standing
check on both obligations for profiles the vectors do not cover.

`identifier_whole_numbers` is the ninth case, added when review item
P2-C2-F7 found the ORACLE carrying a rule the method had withdrawn --
that `all_whole_numbers` true means every group is written from the
figures -- with no frozen case reaching the branch, so byte equality
never tested it. The oracle was reconciled to method section G9.6 by
that tool's owner, from the specification alone, and the case exists so
that the branch is covered rather than merely corrected.

**The five branch cases are the same oracle's second file** (review
items P2-C3-F3 and P2-C4-C3). The nine above reached no unrepresentable
column, no joint class-and-alphabet packing of free text, no fold
collision that a case change cannot build, no cell carrying the literal
`decimal`, `leading_zero` or `leading_plus` style, and no published end
whose seconds field is 60, so a defect on any of those branches left
every committed byte unchanged. They live in a second fixture because a
committed fixture must stay under the provenance manifest's 100000-byte
cap and the nine already spend 88207 of it; they are one oracle, one
transform and one proof layer, and the tests below hold both files to
the same claims.

**Every one of the forty carries a mutant that removes or reverts the
branch it exists for** (G14.3; review item P2-C4-C2). They are one table
at the bottom of this file, `CASE_MUTANTS`, whose keys are asserted
equal to the whole case set, because four cases with a mutant and ten
without is the same gap in a quieter form: a case whose own rule can be
reverted with every committed byte unchanged tests nothing. Each entry
builds its case unmutated first, so a mutant cannot pass by refusing for
some reason of its own.

`identifier_edge_spacing` was carried as a strict expected failure for
one round while the oracle and the implementation disagreed about which
partner method section G9.3's family hands to which slot. It is bound
normally here now. The vectors were not adjusted: G9.3 states the
selection rule the two implementations had worked out differently
(review item P2-C4-F4), and it is the rule these committed bytes already
followed -- every slot walks its parent's family from that family's own
start and takes the first member the column has not written whose length
its own window admits.
"""

import importlib.util
import json
import pathlib
import sys
import typing

import numpy
import numpy.ctypeslib
import pytest

import fixtures
from synthtwin import (
    contract,
    dialect,
    generation,
    parsing,
    rendering,
    sheetwriting,
)

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
GENERATOR = REPOSITORY / "tools" / "reference" / "make_generation_reference_vectors.py"
BRANCH_GENERATOR = (
    REPOSITORY / "tools" / "reference" / "make_generation_branch_vectors.py"
)
SECOND_BRANCH_GENERATOR = (
    REPOSITORY / "tools" / "reference" / "make_generation_branch_vectors_2.py"
)
# THE FIFTH FILE (the repair of the final Codex review of the number
# censuses, plans P4-D142, P4-D145 and P4-D147).
THIRD_BRANCH_GENERATOR = (
    REPOSITORY / "tools" / "reference" / "make_generation_branch_vectors_3.py"
)
VECTORS = (
    pathlib.Path(__file__).resolve().parent
    / "reference"
    / "generation-reference-vectors.json"
)
BRANCH_VECTORS = (
    pathlib.Path(__file__).resolve().parent
    / "reference"
    / "generation-branch-vectors.json"
)
SECOND_BRANCH_VECTORS = (
    pathlib.Path(__file__).resolve().parent
    / "reference"
    / "generation-branch-vectors-2.json"
)
THIRD_BRANCH_VECTORS = (
    pathlib.Path(__file__).resolve().parent
    / "reference"
    / "generation-branch-vectors-3.json"
)
# THE FOURTH FILE (landing 2b.17): the cases for the transforms that
# produce a whole DOCUMENT rather than one column's cells.
DOCUMENT_GENERATOR = (
    REPOSITORY / "tools" / "reference" / "make_generation_document_vectors.py"
)
DOCUMENT_VECTORS = (
    pathlib.Path(__file__).resolve().parent
    / "reference"
    / "generation-document-vectors.json"
)


def _generator():
    """The vector generator, loaded from its path (it is not a package)."""
    spec = importlib.util.spec_from_file_location(
        "make_generation_reference_vectors", GENERATOR
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gen = _generator()

# The oracle's own filling and numeric content, held before any test
# patches them, so a mutant calls the rule it replaces rather than itself.
gen_filled_form = gen.filled_form
gen_numeric_content = gen._numeric_content



def _document() -> dict:
    return json.loads(VECTORS.read_text(encoding="utf-8"))


def _branch_document() -> dict:
    return json.loads(BRANCH_VECTORS.read_text(encoding="utf-8"))


def _second_branch_document() -> dict:
    return json.loads(SECOND_BRANCH_VECTORS.read_text(encoding="utf-8"))


def _third_branch_document() -> dict:
    return json.loads(THIRD_BRANCH_VECTORS.read_text(encoding="utf-8"))


# The nine cases method section G14.3 names.
REQUIRED_CASES = (
    "date_only",
    "identifier_fold_collisions",
    "identifier_whole_numbers",
    "label_variants",
    "mixed_parsed_unparsed",
    "numeric_decimal_styles",
    "numeric_integer",
    "offset_bearing",
    "quarter",
)

# The eight that section adds for the branches those nine leave
# unexercised (review items P2-C3-F3 and P2-C4-C3, and owner decision
# 11's pooled-spelling case), which are the second committed file of the
# same oracle.
BRANCH_CASES = (
    # THE THIRD FROZEN CASE FOR A ROLE PHASE 4 ADDED (residual
    # R-P4-17). It pins the rule the affixed role exists for: the
    # universal class counts answer for the CELLS and the quantitative
    # block for the CORES, and they are not the same set.
    "affixed_brackets",
    # THE SECOND FROZEN CASE FOR A ROLE PHASE 4 ADDED (residual
    # R-P4-17), and the first for a role whose method section did not
    # exist until 2026-08-27. Eleven seconds hold eleven parsed cells,
    # so the all-different repair of G7A.4 has no slack and every
    # interior rank must land on the one ordinal left for it.
    "clock_ladder",
    # THE CENSUS OF SPELLINGS OF A COUNT COLUMN (landing 2b.18 part 2,
    # plan P4-D123). Every count case before it wrote each number one
    # way, so it publishes an empty census and the rule could be
    # withdrawn with every committed byte unchanged.
    "count_spellings",
    "free_text_joint",
    "identifier_edge_spacing",
    # THE LAYOUT OF A RECORD NUMBER (contract 7.12, landing 2b.18). The
    # three identifier cases beside it publish an EMPTY census, so the
    # whole layout rule -- the seventh published key of the role, and
    # the generator walk that writes each cell to it -- could have been
    # withdrawn with every committed byte unchanged. This is the case
    # that holds it up.
    "identifier_layout",
    # THE FILL, THE SPACE AND THE MIXES OF A LAYOUT CENSUS (landing
    # 2b.18's repair pass, plans P4-D126 to P4-D128). `identifier_layout`
    # names two layouts that pay every cell, so a zero fill two noughts
    # deep, a space inside a layout and a pool written to mixes of the
    # named kinds could each be withdrawn with every committed byte
    # unchanged.
    "identifier_layout_mixes",
    # THE FOURTH AND LAST OF THE ROLES PHASE 4 ADDED (residual
    # R-P4-17). It pins the pairing walk of G6B.4, the only search in
    # the method and the only place synthtwin reproduces structure
    # between two quantities at all.
    "joined_readings",
    "leap_second_endpoint",
    # THE SHAPE OF A PUBLISHED LABEL (landing 2b.18 part 2, plan
    # P4-D122). No label case before it reaches a stand-in the census
    # owes no form, so the rule could be withdrawn with every committed
    # byte unchanged.
    "level_shape_stand_ins",
    # THE FIRST FROZEN CASE FOR A ROLE PHASE 4 ADDED (residual
    # R-P4-17). Every other case here exercises a role Phase 1 to 3
    # built; the four Phase 4 roles had no independent vector at all,
    # so their generator branches were checked only against
    # themselves. This is one of the four.
    "long_tail_levels",
    # THE CASE OF A LETTER (landing 2b.18 part 2, plan P4-D121). Every
    # label case before it publishes a census blind to case.
    "lower_case_stand_ins",
    # THE TWO CASES FOR THE SPELLING OF A MOMENT (plan P4-D39, stage 2).
    # One pins the day-unit rule of a column that stands wholly at
    # midnight; the other pins the evenly spread rotation of marks, its
    # tie rule and the withheld pool.
    "midnight_days",
    # THE ONE CASE IN ANY OF THE THREE FILES THAT NAMES MORE THAN ONE
    # CONVENTION (landing 2b.7, plan P4-D65.2). A census naming ONE
    # notation or ONE mark cannot pin the allocators that spend it: the
    # census path and the majority path write the same cell, so a
    # mutant that withdraws the census leaves every frozen byte where it
    # was, and both oracle mutants were GREEN against the nine spelling
    # cases already here. This one names two of each at eleven cells
    # apiece, so the cells divide and a mutant moves them.
    "mixed_conventions",
    "mixed_marks",
    # The month, added with the second SPAN resolution (plan P4-D4.3
    # item 2). A new transform reaching the twin without an independent
    # frozen case is a transform the generator and the validator agree
    # about with nobody else in the room (review item P4-DATE3-F1).
    "month_span",
    "numeric_point_free_styles",
    "numeric_pooled_spelling",
    # THE SECOND SPELLING FAMILY OF G10.5, added with revision 5
    # (residuals R-P4-48 and R-P4-68). `unrepresentable_joint` below
    # reaches this role, and every cell it freezes is a digit string
    # four hundred characters wide or the fixed contradictory
    # construction -- so the exponent family could have been withdrawn
    # entirely with both committed files byte-identical. This case is
    # six cells published at five and six characters, widths no digit
    # string can be written at.
    #
    # THE ORDER OF THIS TUPLE IS ITS SORTED ORDER, which one test below
    # compares against the committed file's own key order.
    "unrepresentable_exponent",
    "unrepresentable_joint",
)

# The third committed file: the cases the carried landings 2b.4, 2b.3 and
# 2b.2 added, split out when the second would have passed the provenance
# guard's byte cap (G14.2). The order of this tuple is its sorted order too.
SECOND_BRANCH_CASES = (
    # LANDING 2b.3'S REPAIR PASS left one case in this file, and landing 2b.6
    # withdrew it: an accidental value at midnight was moved off a column
    # publishing a count of nought, and no column publishes that nought any
    # more, because a reader able to tell it from a suppressed count of one had
    # been told that count. Its neighbour -- bare dates beside moments at local
    # midnight on a real offset, whose ranks with a published instant settle
    # their form and offset before the rotation -- is in the first file.
    # THE REST OF LANDING 2b.2'S MARKS AND NOTATIONS, frozen at the
    # integration of landings 2b.1 to 2b.5 once the branch cases had a file
    # with room: the apostrophe with the minus sign, U+2019 with the trailing
    # minus, U+00A0 on a declared decimal comma (whose mutant is the exchange),
    # U+202F and U+2009. Eleven rows each: at twenty-two the five carried
    # this file past the provenance guard's byte cap.
    "apostrophe_minus_sign",
    # THE SPELLINGS OF A NUMBER LANDING 2b.2 FREEZES, in their sorted
    # places: a comma between thousands beside signed decimals with
    # zeros spent past order nought, a point on a declared decimal-comma
    # column beside two absent cells, and a space with accounting
    # brackets. They were three and not four while every branch case
    # shared one file, whose byte cap a fourth would have passed; the
    # other five followed when this file was split out.
    "grouped_charges",
    "grouped_decimal_comma",
    # WHAT THE CENSUS COULD HOLD, AND THE PLACES A NUMBER MAY TAKE (method
    # G8.3a, landing 2b.4's repair). `label_numbers` pools two cells, so a
    # number stepping past every named `%.%` value may write `10.0` there;
    # this one pools none, and the rule that ends that side instead -- and
    # takes the published whole numbers' places -- could be withdrawn with
    # every other committed byte unchanged.
    "label_number_tiers",
    # THE CLASS DEBT OF A COLUMN OF LABELS (method G8.3a, landing 2b.4).
    # Every earlier label case publishes no number, so the rule that
    # writes a held-back number AS a number -- stepped from the published
    # numbers, gaps first -- could be withdrawn with every committed byte
    # unchanged.
    "label_numbers",
    "midnight_bare_offsets",
    # THE FIVE CASES OF LANDING 2b.3: bare dates beside midnight moments,
    # midnight on two offsets, a column partly at midnight, a withheld pool
    # spent on the unnamed marks, and a slashed stamp's one permitted mark.
    "midnight_mixed_forms",
    "midnight_two_offsets",
    "narrow_spaced",
    "partial_midnight",
    "pooled_marks",
    "quoted_trailing_minus",
    "slashed_pool",
    "spaced_brackets",
    "spaced_decimal_comma",
    "thin_spaced",
)

# The fifth committed file: the cases the repair of the final Codex review
# of the number censuses added (plans P4-D142, P4-D145, P4-D147), each of
# whose rules could otherwise be withdrawn with every committed byte
# unchanged. Sorted, like the tuples above.
THIRD_BRANCH_CASES = (
    "bare_mark_remainder",
    "plus_padded_field",
    "pooled_mark_cells",
    "saturated_integers",
    "unpublished_majority_marks",
)

ALL_CASES = tuple(
    sorted(REQUIRED_CASES + BRANCH_CASES + SECOND_BRANCH_CASES + THIRD_BRANCH_CASES)
)

# Which seed's opening words each case is given. This mapping lives here
# and not in the oracle: the oracle is a pure function of the words, and
# a seed inside it would be a random operation it is not allowed to hold.
SEEDS = {
    "date_only": 101,
    "quarter": 102,
    "offset_bearing": 103,
    "mixed_parsed_unparsed": 104,
    "numeric_integer": 105,
    "numeric_decimal_styles": 106,
    "label_variants": 107,
    "identifier_fold_collisions": 108,
    "identifier_whole_numbers": 109,
    "numeric_point_free_styles": 110,
    "unrepresentable_joint": 111,
    "unrepresentable_exponent": 121,
    "free_text_joint": 112,
    "identifier_edge_spacing": 113,
    "identifier_layout": 136,
    "identifier_layout_mixes": 140,
    "lower_case_stand_ins": 137,
    "level_shape_stand_ins": 138,
    "count_spellings": 139,
    "leap_second_endpoint": 114,
    "numeric_pooled_spelling": 115,
    "month_span": 116,
    "long_tail_levels": 117,
    "clock_ladder": 118,
    "affixed_brackets": 119,
    "joined_readings": 120,
    "midnight_days": 122,
    "mixed_marks": 123,
    # Landing 2b.7's own case takes the next seed after the carried
    # landings' block, which ran to 135.
    "mixed_conventions": 136,
    # The repair of the final Codex review of the number censuses takes
    # 160 onward, clear of every block the carried landings and their
    # repairs took.
    "bare_mark_remainder": 160,
    "plus_padded_field": 161,
    "pooled_mark_cells": 162,
    "saturated_integers": 163,
    "unpublished_majority_marks": 164,
    # Landings 2b.4, 2b.3 and 2b.2 were built side by side and each took
    # 124 onward for its own cases. A seed only names the opening words a
    # case is given, and each case's committed cells were chosen from
    # those words, so both keep their seed rather than move to new words.
    "label_numbers": 124,
    "label_number_tiers": 125,
    "pooled_marks": 124,
    "slashed_pool": 125,
    "midnight_mixed_forms": 126,
    "partial_midnight": 127,
    "midnight_two_offsets": 128,
    "midnight_bare_offsets": 129,
    "grouped_charges": 124,
    "grouped_decimal_comma": 125,
    "spaced_brackets": 126,
    "apostrophe_minus_sign": 131,
    "quoted_trailing_minus": 132,
    "spaced_decimal_comma": 133,
    "narrow_spaced": 134,
    "thin_spaced": 135,
}

# The cases whose column was declared with --decimal-comma, which the
# contract's invariant GS1 binds to settings.forced_decimal_commas.
DECLARED_DECIMAL_COMMAS = frozenset({"grouped_decimal_comma", "spaced_decimal_comma"})

# The cases whose column was declared with --identifier, which the
# contract's invariant A1 binds to settings.forced_identifiers.
DECLARED_IDENTIFIERS = frozenset(
    {
        "identifier_fold_collisions",
        "identifier_whole_numbers",
        "identifier_edge_spacing",
        "identifier_layout",
        "identifier_layout_mixes",
    }
)

def _case(name: str) -> dict:
    """One case, from whichever of the committed files carries it."""
    if name in THIRD_BRANCH_CASES:
        document = _third_branch_document()
    elif name in SECOND_BRANCH_CASES:
        document = _second_branch_document()
    elif name in BRANCH_CASES:
        document = _branch_document()
    else:
        document = _document()
    return document["cases"][name]


def _relationships() -> dict:
    return {
        key: None
        for key in (
            "deterministic",
            "grain",
            "hierarchy",
            "keys",
            "missing_data_process",
            "statistical",
            "temporal",
            "validation_targets",
        )
    }


def _settings(declared: list, commas: "list | None" = None) -> dict:
    return {
        "small_cell_floor": 11,
        "identifier_uniqueness": 0.95,
        "identifier_minimum_rows": 0,
        "minimum_parse_rate": 0.9,
        "categorical_share": 0.5,
        "categorical_ceiling": 50,
        "categorical_floor": 1,
        "sentinel_outlier_iqr_multiple": 1.5,
        "sentinel_minimum_share": 0.02,
        "kept_values": {
            "n_declared": 0,
            "values_recorded": False,
            "built_in_texts": [],
            "built_in_dates": [],
            "built_in_numbers": [],
        },
        "declared_missing_values": {
            "n_declared": 0,
            "values_recorded": False,
            "built_in_texts": [],
            "built_in_dates": [],
            "built_in_numbers": [],
        },
        "declaration_matching": "exact_number_when_it_reads_as_one_else_spelling",
        "declaration_publication": "settings_counts_only_columns_unchanged",
        "near_threshold_slack": 0,
        "day_first": False,
        "long_tail_minimum_level": 11,
        "forced_identifiers": declared,
        # The second declaration (plan P4-D19). The oracle declares no
        # code column: every case here is built from the generation
        # method's own text, and none of them turns on the reading a
        # declaration changes.
        "forced_codes": [],
        # The third declaration (plan P4-D21). The oracle declares no
        # measurement column: every case here is built from the
        # generation method's own text.
        "forced_measurements": [],
        # The fourth (plan P4-D26), named for the one case frozen with
        # it (landing 2b.2): its column is grouped with a point.
        "forced_decimal_commas": [] if commas is None else commas,
        # The fifth (plan P4-D81). The oracle declares no rows of column
        # descriptions: every case here is built from the generation
        # method's own text, and none of them has a header at all.
        "forced_metadata_rows": 0,
        # The sixth (plan P4-D110). The oracle declares no delimiter: the
        # delimited cases read their own published one.
        "forced_delimiter": "",
    }


def _unwrap(node):
    """The wire value of a case's column block.

    The oracle writes every published binary64 inside a `float64` wrapper
    carrying the exact rational it stands for, because a number in that
    file with nothing proving it is the one thing the file may not hold.
    The wire value is the wrapper's own `float64` field.
    """
    if isinstance(node, dict):
        inside = node.get("float64")
        if isinstance(inside, float):
            return inside
        return {key: _unwrap(value) for key, value in node.items()}
    if isinstance(node, list):
        return [_unwrap(value) for value in node]
    return node


def _profile_document(case: dict, name: str) -> dict:
    """A whole profile document carrying one case's column and nothing else."""
    column = _unwrap(case["column"])
    declared = [column["name"]] if name in DECLARED_IDENTIFIERS else []
    commas = [column["name"]] if name in DECLARED_DECIMAL_COMMAS else []
    return {
        "columns": [column],
        "created_with": "0+unknown",
        "n_columns": 1,
        "n_rows": len(case["cells"]),
        "profile_version": 6,
        "publication_notes": [],
        "relationships": _relationships(),
        "settings": _settings(declared, commas),
        "source": {
            "dialect": dialect.document_of(
                dialect.ordinary(1, len(case["cells"]), False)
            ),
            "encoding": "utf-8-sig",
            "used_fallback_encoding": False,
            "header_source": "generated",
            "header_by_convention": False,
            "header_evidence": "the file carried no names of its own, so the "
            "columns were named for it.",
            # Every frozen case is a DELIMITED file -- one column of
            # cells written as text -- so it carries no workbook block
            # (plan P4-D77, contract 4.3b). The key is required of every
            # description, and `null` is what a description of delimited
            # text says there.
            "workbook": None,
        },
    }


def _load(case: dict, name: str, folder: pathlib.Path) -> contract.Profile:
    path = fixtures.write_profile(
        folder, f"{name}.json", _profile_document(case, name)
    )
    return contract.load_profile(str(path))


def _words(count: int, seed: int) -> list:
    """The opening ``count`` words of the single stream at ``seed``.

    Exactly the draw form method section G3.2 fixes and no other: the
    whole of 0 .. 2**64 - 1 inclusive at both ends, the type named by the
    string "uint64", every element converted to a first-party whole
    number before any other use.
    """
    stream = numpy.random.default_rng(seed)
    return [
        int(word)
        for word in stream.integers(
            0, 18446744073709551615, size=count, dtype="uint64", endpoint=True
        )
    ]


# ----------------------------------------------- what the oracle says it is


def test_the_oracle_is_present_and_says_what_it_is() -> None:
    document = _document()
    assert document["never_imports"] == ["synthtwin", "numpy", "pandas"]
    assert document["method"] == "docs/spec/generation-method-v1.md"
    assert document["method_revision"] == 1
    assert tuple(sorted(document["cases"])) == REQUIRED_CASES


def test_the_branch_file_is_the_same_oracle_and_says_which_half_it_is() -> None:
    """No file may be read as the whole of the oracle.

    The three carry disjoint case sets and together carry every case
    method section G14.3 names, and each one's own account says where
    the other two live -- so a reader who opens any of them is told at
    once that it is part of one artifact rather than all of it.
    """
    named = _document()
    branch = _branch_document()
    second = _second_branch_document()
    third = _third_branch_document()
    papers = _document_document()
    assert tuple(sorted(branch["cases"])) == BRANCH_CASES
    assert tuple(sorted(second["cases"])) == SECOND_BRANCH_CASES
    assert tuple(sorted(third["cases"])) == THIRD_BRANCH_CASES
    assert tuple(sorted(papers["cases"])) == DOCUMENT_CASES
    every = (named, branch, second, third, papers)
    for index in range(len(every)):
        for other in range(index + 1, len(every)):
            assert not set(every[index]["cases"]) & set(every[other]["cases"])
    held: "set" = set()
    for one in every:
        held = held | set(one["cases"])
    assert tuple(sorted(held)) == EVERY_CASE
    files = (
        (named, VECTORS),
        (branch, BRANCH_VECTORS),
        (second, SECOND_BRANCH_VECTORS),
        (third, THIRD_BRANCH_VECTORS),
        (papers, DOCUMENT_VECTORS),
    )
    for document, own in files:
        assert document["never_imports"] == ["synthtwin", "numpy", "pandas"]
        assert document["method"] == "docs/spec/generation-method-v1.md"
        assert document["generated_by"] == (
            "tools/reference/make_generation_reference_vectors.py"
        )
        for _other, path in files:
            if path != own:
                assert f"tests/reference/{path.name}" in document["case_set"]


@pytest.mark.parametrize(
    "script",
    [
        GENERATOR,
        BRANCH_GENERATOR,
        SECOND_BRANCH_GENERATOR,
        THIRD_BRANCH_GENERATOR,
        DOCUMENT_GENERATOR,
    ],
)
def test_the_oracle_imports_none_of_the_code_it_checks(script) -> None:
    """The claim in the file's own header, held up against its source.

    An oracle that imported the package, or the library whose one random
    operation the method retains, would be recomputing a value beside the
    code it checks -- which is the defect the vectors exist to prevent.
    Both entry points are held to it, because the second one runs the
    first and a forbidden import in either would reach the vectors.
    """
    source = script.read_text(encoding="utf-8")
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped.startswith(("import ", "from ")):
            continue
        module = stripped.split()[1].partition(".")[0]
        assert module not in ("synthtwin", "numpy", "pandas"), stripped


def test_the_guard_refuses_the_import_that_shapes_the_oracle() -> None:
    """Why the oracle may not use numpy, checked rather than asserted.

    The reason is mechanical, not stylistic: every fixture generator runs
    under an audit hook that refuses `ctypes`, and numpy imports
    `ctypes`, so a generator that imported numpy would be stopped before
    it wrote a byte. Both halves are checked here, because the design of
    the whole vector file rests on them.
    """
    guard = importlib.util.spec_from_file_location(
        "guard_runner", REPOSITORY / "tools" / "provenance" / "guard_runner.py"
    )
    runner = importlib.util.module_from_spec(guard)
    guard.loader.exec_module(runner)
    assert "ctypes" in runner.BLOCKED_IMPORT_MODULES
    assert runner.import_is_blocked("ctypes")
    assert runner.import_is_blocked("ctypes.util")
    # And numpy really does reach for it: this module of numpy's own
    # holds the module object the guard refuses.
    assert numpy.ctypeslib.ctypes.__name__ == "ctypes"
    assert "ctypes" in sys.modules


# ------------------------------------------- the words the cases are given


@pytest.mark.parametrize("name", ALL_CASES)
def test_the_given_words_are_the_opening_words_of_one_stream(name: str) -> None:
    """The vectors take words as inputs; this is what binds them to a run.

    The oracle holds no generator, so nothing inside it could make this
    true. Asserting it here is what lets the same case be handed to
    `generate` and compared cell for cell.
    """
    case = _case(name)
    given = [int(word) for word in case["words"]]
    assert given == _words(len(given), SEEDS[name])


@pytest.mark.parametrize("name", ALL_CASES)
def test_the_word_sequence_does_not_depend_on_how_the_calls_are_cut(
    name: str,
) -> None:
    """The property method section G3.3 rests on, re-checked every run.

    The implementation makes one call per stage; the full-width range
    needs no rejection and no buffering, so drawing the content words and
    the placement words in two calls yields the same sequence as one. A
    library change that broke this would turn this test red rather than
    move a twin.
    """
    case = _case(name)
    budget = case["word_budget"]
    seed = SEEDS[name]
    together = _words(budget["content"] + budget["placement"], seed)
    stream = numpy.random.default_rng(seed)
    apart = []
    for size in (budget["content"], budget["placement"]):
        if not size:
            continue
        apart.extend(
            int(word)
            for word in stream.integers(
                0, 18446744073709551615, size=size, dtype="uint64", endpoint=True
            )
        )
    assert together == apart
    assert [int(word) for word in case["words"]] == together


# ------------------------------ the implementation against the committed cells


@pytest.mark.parametrize("name", ALL_CASES)
def test_the_implementation_writes_the_committed_cells(
    name: str, tmp_path: pathlib.Path
) -> None:
    """Cell for cell, and then byte for byte, against a value it did not make.

    All forty bind normally, with no exception of any kind. The one
    that once did not was `identifier_edge_spacing` (review item
    P2-C4-F4): the column publishes four raw spellings, one folded
    identity and the length range 1 to 3, in figures alone, so every
    partner comes from the edge spacing of method section G9.3. Both
    sides pinned the identity `1` at the shortest published length and
    the partner `1  ` at the longest, and parted company on the other
    two -- the oracle writing `1 ` and then ` 1`, the implementation
    ` 1` and then ` 1 `, leaving `1 ` unwritten. Both columns satisfy
    every published fact, so the loss was never fidelity: it was the
    property this whole artifact exists for, that an independent
    implementer working from the text alone writes the same bytes. G9.3
    step 2 now states which member of the family a slot takes -- the
    first one the column has not written whose length the slot's own
    window admits, with the family walked from its start for every slot
    -- and the committed bytes are what that rule produces. A strict
    expected failure was never a substitute for it: an expected failure
    records a disagreement, and this file exists to end one.
    """
    case = _case(name)
    profile = _load(case, name, tmp_path)
    twin = generation.generate(profile, SEEDS[name])
    written = [row[0] for row in twin.rows]
    assert written == case["cells"], (
        f"{name}: the twin's cells are not the ones the method requires. The "
        "oracle is the specification's answer; do not change it to match the "
        f"implementation. The content list this case requires, before "
        f"placement, is {case['content']}, and the written column is "
        f"{case['cells']}."
    )
    assert rendering.twin_csv(twin) == case["csv_bytes"]


@pytest.mark.parametrize("name", ALL_CASES)
def test_the_word_budget_of_the_method_is_the_budget_the_run_spends(
    name: str, tmp_path: pathlib.Path
) -> None:
    """Conformance item 3: the count per column matches G4.3 exactly.

    Asserted for every case as a claim of its own: a disagreement about
    which values a column holds is a different failure from a
    disagreement about how many words it consumes, and keeping them
    apart is what says the two are unrelated. The identifier case proved
    the point while it was still failing on its cells -- its word budget
    was right throughout, and the repair to its cells did not move it.
    """
    case = _case(name)
    budget = case["word_budget"]
    assert budget["content"] + budget["placement"] == len(case["words"])
    profile = _load(case, name, tmp_path)
    twin = generation.generate(profile, SEEDS[name])
    outcome = twin.outcomes[0]
    assert (outcome.content_words, outcome.placement_words) == (
        budget["content"],
        budget["placement"],
    )
    assert twin.words_drawn == len(case["words"])


@pytest.mark.parametrize("name", ALL_CASES)
def test_every_committed_cell_reads_back_as_the_class_it_was_built_for(
    name: str,
) -> None:
    """The class-preserving claim of G10.2, checked on the oracle's own text.

    Each of the four classes has its own construction, and each
    construction's output must classify back into its own class through
    the shipped classifier. That is a property of the cells the method
    requires, so it is asserted over the committed vectors rather than
    over whatever the implementation happened to write.
    """
    case = _case(name)
    column = _unwrap(case["column"])
    counted = dict.fromkeys(
        (
            parsing.NUMBER,
            parsing.NUMBER_OUT_OF_RANGE,
            parsing.NUMBER_CONTRADICTORY,
            parsing.NOT_A_NUMBER,
        ),
        0,
    )
    for cell in case["cells"]:
        if cell == "":
            continue
        # A declared column's cells read in its own grammar, as the
        # profiler read the column the case describes (P4-D26).
        if name in DECLARED_DECIMAL_COMMAS:
            cell = parsing.written_with_a_decimal_comma(cell)
        counted[parsing.classify_number(cell)] += 1
    assert counted[parsing.NUMBER] == column["n_numeric"]
    assert counted[parsing.NUMBER_OUT_OF_RANGE] == column["n_out_of_range"]
    assert counted[parsing.NUMBER_CONTRADICTORY] == column["n_contradictory"]
    assert counted[parsing.NOT_A_NUMBER] == column["n_not_numeric"]


@pytest.mark.parametrize("name", ALL_CASES)
def test_the_committed_cells_are_the_content_list_arranged(name: str) -> None:
    """G4.2, checked inside the vectors themselves.

    The written column is the content list plus the absent cells, placed
    by one arrangement. That makes the two lists the same multiset, which
    is a property no seed can change and the one thing a wrong
    arrangement cannot fake.
    """
    case = _case(name)
    column = _unwrap(case["column"])
    assert len(case["content"]) == column["n_present"]
    assert sorted(case["cells"]) == sorted(
        list(case["content"]) + [""] * column["n_missing"]
    )
    # A CELL HOLDING A COMMA IS QUOTED, which no committed cell did until
    # landing 2b.2 froze a column grouped with one: the rule is G2's, and
    # a quote inside a cell would be doubled, which no case writes.
    expected = "".join(
        ('""' if cell == "" else f'"{cell}"' if "," in cell else cell) + "\n"
        for cell in case["cells"]
    )
    assert case["csv_bytes"] == expected


# ---------------------------------------------------- the proof layer itself


PUBLISHED_NUMBERS = 210
NAMED_COUNTS = 270
BRANCH_PUBLISHED_NUMBERS = 23
BRANCH_NAMED_COUNTS = 121
SECOND_BRANCH_PUBLISHED_NUMBERS = 336
SECOND_BRANCH_NAMED_COUNTS = 370
THIRD_BRANCH_PUBLISHED_NUMBERS = 643
THIRD_BRANCH_NAMED_COUNTS = 198
# The document file publishes NO binary64 at all, and that is a fact
# about its transforms rather than a gap in its proof: the written form,
# the arrangement, the workbook writer, the shape of a line before a
# table and the reading of a delimiter produce bytes and counts and
# never a measurement. Its whole-number floor is what holds it: every
# count it publishes is named among the oracle's own whole-number
# fields, and a number at any other path stops the run.
DOCUMENT_PUBLISHED_NUMBERS = 0
DOCUMENT_NAMED_COUNTS = 70

# Each committed file, with the floors its own proof must clear and the
# case set the oracle writes it from.
COMMITTED_FILES = (
    (VECTORS, None, PUBLISHED_NUMBERS, NAMED_COUNTS),
    (BRANCH_VECTORS, gen.BRANCH_PART, BRANCH_PUBLISHED_NUMBERS, BRANCH_NAMED_COUNTS),
    (
        SECOND_BRANCH_VECTORS,
        gen.SECOND_BRANCH_PART,
        SECOND_BRANCH_PUBLISHED_NUMBERS,
        SECOND_BRANCH_NAMED_COUNTS,
    ),
    (
        THIRD_BRANCH_VECTORS,
        gen.THIRD_BRANCH_PART,
        THIRD_BRANCH_PUBLISHED_NUMBERS,
        THIRD_BRANCH_NAMED_COUNTS,
    ),
    (
        DOCUMENT_VECTORS,
        gen.DOCUMENT_PART,
        DOCUMENT_PUBLISHED_NUMBERS,
        DOCUMENT_NAMED_COUNTS,
    ),
)


def _fields(document: dict) -> frozenset:
    return gen.whole_number_fields(document)


@pytest.mark.parametrize(
    "committed,part,published,named", COMMITTED_FILES, ids=["named", "branches", "branches-2", "branches-3", "documents"]
)
def test_the_committed_file_publishes_no_number_that_escapes_the_proof(
    committed, part, published, named
) -> None:
    """Every number in the file, one by one, read back off the disk.

    The proof is only as wide as the walk that feeds it, so this reads
    the committed bytes and checks that nothing written as a number sits
    anywhere but in a `float64` wrapper holding a binary64 value or at
    one of the whole-number paths the generator names.
    """
    document = json.loads(committed.read_text(encoding="utf-8"))
    allowed = _fields(document)
    measurements = 0
    counts = 0
    for path, value in gen._published_numbers(document, (), gen.SECTION_FIELDS):
        if path in gen.DOCUMENT_TEXT_FIELDS:
            assert isinstance(value, str), gen._where(path)
            continue
        if path[-1] == "float64":
            assert isinstance(value, float), (
                f"{gen._where(path)} carries {value!r}, which is not a "
                "binary64 value, so the proof could not be applied to it"
            )
            measurements += 1
        else:
            assert path in allowed, (
                f"{gen._where(path)} publishes {value!r} outside a 'float64' "
                "field and is not one of the named counts"
            )
            assert isinstance(value, int) and not isinstance(value, bool)
            counts += 1
    assert measurements >= published, (
        f"the file now publishes {measurements} proved numbers, fewer than "
        f"the {published} it carried when this floor was written; a "
        "field has left the file"
    )
    assert counts >= named


@pytest.mark.parametrize(
    "committed,part,published,named", COMMITTED_FILES, ids=["named", "branches", "branches-2", "branches-3", "documents"]
)
def test_the_committed_bytes_are_proved_against_the_recorded_exact_values(
    committed, part, published, named
) -> None:
    """The file as it sits on disk, put through the proof it claims to carry."""
    _document_in_memory, claims = gen.build_document(part)
    document = json.loads(committed.read_text(encoding="utf-8"))
    proved = gen.prove_every_published_float(
        document,
        claims,
        _fields(document),
        gen.DOCUMENT_TEXT_FIELDS,
        gen.SECTION_FIELDS,
    )
    assert proved >= published


@pytest.mark.parametrize(
    "committed,part,published,named", COMMITTED_FILES, ids=["named", "branches", "branches-2", "branches-3", "documents"]
)
def test_the_generator_says_how_many_numbers_it_proved(
    tmp_path, capsys, committed, part, published, named
) -> None:
    """The count is reported, and it is the count of what the file holds.

    Tying the reported number to the rebuilt file is what stops the
    report from being a constant. The rebuilt bytes are compared with the
    committed ones as well -- the provenance guard's own check, restated
    here so that a change to the proof layer that moved a number is
    visible in this suite too.
    """
    rebuilt = tmp_path / committed.name
    assert gen.main(["--seed", "0", "--out", str(rebuilt)], part=part) == 0
    reported = capsys.readouterr().err
    document = json.loads(rebuilt.read_text(encoding="utf-8"))
    measurements = sum(
        1
        for path, _value in gen._published_numbers(document, (), gen.SECTION_FIELDS)
        if path[-1] == "float64" and path not in gen.DOCUMENT_TEXT_FIELDS
    )
    counts = sum(
        1
        for path, _value in gen._published_numbers(document, (), gen.SECTION_FIELDS)
        if path[-1] != "float64"
    )
    assert measurements >= published
    assert counts >= named
    assert f"proved {measurements} published numbers" in reported
    assert f"beside {counts} named whole-number counts" in reported
    assert rebuilt.read_bytes() == committed.read_bytes()


def test_a_value_past_the_overflow_boundary_is_not_certified() -> None:
    """The boundary the bracketing comparison cannot see on its own."""
    with pytest.raises(AssertionError) as refusal:
        gen.prove_nearest_float(gen.F(1 << 1024), sys.float_info.max)
    assert "infinity" in str(refusal.value)
    gen.prove_nearest_float(gen.F(sys.float_info.max), sys.float_info.max)


def test_the_sign_of_a_zero_is_read_from_its_bit() -> None:
    """`+0.0 == -0.0`, so a numeric sign test says nothing about which is which."""
    with pytest.raises(AssertionError) as refusal:
        gen.prove_nearest_float(gen.F(-1, 1 << 2000), 0.0)
    assert "sign" in str(refusal.value)
    gen.prove_nearest_float(gen.F(-1, 1 << 2000), -0.0)
    with pytest.raises(AssertionError):
        gen.prove_exact_float(gen.F(0), -0.0)
    assert gen.sign_bit_is_set(-0.0) is True
    assert gen.sign_bit_is_set(0.0) is False


def test_the_exact_claim_refuses_a_value_that_was_rounded() -> None:
    """`exact` is the stronger claim, and it is held to being stronger.

    A value the transform reaches without rounding must be published as
    exactly the rational recorded beside it. The weaker "nearest" claim
    would pass any float held up against its own exact value, so a field
    that quietly started rounding would go unnoticed.
    """
    gen.prove_exact_float(gen.F(5, 4), 1.25)
    with pytest.raises(AssertionError) as refusal:
        gen.prove_exact_float(gen.F(1, 3), 0.3333333333333333)
    assert "exactly" in str(refusal.value)


def test_the_walk_refuses_a_number_with_nothing_proving_it() -> None:
    published = {"value": {"float64": 1.0}, "loose": 2.0}
    claims = {("value",): (gen.NEAREST, gen.F(1))}
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float(published, claims)
    assert "nothing proved it" in str(refusal.value)


def test_the_walk_refuses_a_wrapper_with_no_exact_value_recorded() -> None:
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float({"value": {"float64": 1.0}}, {})
    assert "no exact value" in str(refusal.value)


def test_the_walk_refuses_a_whole_number_under_a_wrapper() -> None:
    """JSON writes a Python int and a float as the same kind of thing."""
    claims = {("value",): (gen.NEAREST, gen.F(1, 3))}
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float({"value": {"float64": 7}}, claims)
    assert "binary64" in str(refusal.value)


def test_the_walk_refuses_an_exact_value_that_nothing_spends() -> None:
    """The match is one-to-one, so a skipped field cannot hide behind a claim."""
    published = {"value": {"float64": 0.5}}
    claims = {
        ("value",): (gen.NEAREST, gen.F(1, 2)),
        ("absent",): (gen.NEAREST, gen.F(0)),
    }
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float(published, claims)
    assert "absent" in str(refusal.value)


def test_a_number_inside_a_tuple_is_not_skipped() -> None:
    """P1-R8-F3: the encoder writes a tuple as an array exactly as a list."""
    published = {"new_field": (7.0,)}
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float(published, {})
    assert "nothing proved it" in str(refusal.value)
    assert "new_field.0" in str(refusal.value)
    assert json.dumps(published, allow_nan=False) == '{"new_field": [7.0]}'


@pytest.mark.parametrize(
    "value",
    [{7.0}, frozenset({7.0}), b"\x07", bytearray(b"\x07"), 3 + 4j],
)
def test_a_shape_the_walk_has_no_rule_for_stops_the_run(value: object) -> None:
    """Fail closed: what the walk does not recognise is where a number hides."""
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float({"odd": value}, {})
    assert "no rule for" in str(refusal.value)


def test_a_key_that_is_not_text_stops_the_run() -> None:
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float({"a": {1.5: 0.5}}, {})
    assert "not text" in str(refusal.value)


def test_the_section_named_float64_is_still_walked_into() -> None:
    """The one exemption, and the mutant that would use it as a hiding place.

    A case's chain of interior values is published under the same word
    the value wrapper uses, so the walk is told to descend there instead
    of handing the section over. Descending is the point: a bare number
    put directly inside a section is still refused.
    """
    section = frozenset({("cases", "one", "float64")})
    document = {"cases": {"one": {"float64": [{"value": {"float64": 0.5}}]}}}
    claims = {("cases", "one", "float64", 0, "value"): (gen.NEAREST, gen.F(1, 2))}
    assert (
        gen.prove_every_published_float(
            document, claims, frozenset(), frozenset(), section
        )
        == 1
    )
    smuggled = {"cases": {"one": {"float64": [7.0]}}}
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float(
            smuggled, {}, frozenset(), frozenset(), section
        )
    assert "nothing proved it" in str(refusal.value)


# Each row is a field added to every case, and what the refusal must
# say. The encoder writes each of these tuples as a JSON array, so every
# one of them really would have reached the file.
GENERATOR_MUTANTS = (
    ((7.0,), "nothing proved it"),
    ((7,), "no rule for"),
    (({"float64": 7.0},), "no exact value"),
    (({"float64": 7},), "binary64"),
    ({7.0}, "no rule for"),
)


@pytest.mark.parametrize("added,refusal_says", GENERATOR_MUTANTS)
def test_a_field_added_to_every_case_stops_the_generator(
    tmp_path, monkeypatch, added: object, refusal_says: str
) -> None:
    """The mutant driven through the whole generator, where the review ran it.

    Checking the committed fixture after a rebuild would not catch this:
    the fixture holds no such field. So the mutant goes through `main`,
    and nothing may be written.
    """
    real = gen.build_case

    def with_one_more(name):
        case, claims = real(name)
        case["added_later"] = added
        return case, claims

    monkeypatch.setattr(gen, "build_case", with_one_more)
    out = tmp_path / "vectors.json"
    with pytest.raises(AssertionError) as refusal:
        gen.main(["--seed", "0", "--out", str(out)])
    assert refusal_says in str(refusal.value)
    assert not out.exists(), "the file was written although a number was unproved"


def test_the_generator_refuses_to_write_when_its_own_mutant_is_certified(
    tmp_path, monkeypatch
) -> None:
    """The self-check is not decoration: a proof layer that passes it stops.

    The run drives a full-generator mutant through the proof layer before
    it serializes anything. Weakening the layer so the mutant is
    certified must stop the run rather than produce a file whose claim is
    no longer true.
    """
    monkeypatch.setattr(
        gen,
        "prove_every_published_float",
        lambda *args, **kwargs: 0,
    )
    out = tmp_path / "vectors.json"
    with pytest.raises(AssertionError) as refusal:
        gen.main(["--seed", "0", "--out", str(out)])
    assert "certified by the proof layer" in str(refusal.value)
    assert not out.exists()


def test_the_generator_checks_its_own_calendar_and_its_own_digits(
    monkeypatch,
) -> None:
    """Two foundations no case can check, checked before any case is built.

    A wrong leap rule leaves a civil-date round trip self-consistent, and
    the shortest round-trip digits are the generator's own rather than
    the interpreter's, so each is held up against an outside answer. A
    check that cannot fail is a defect, so it is made to fail here.
    """
    gen._self_check_arithmetic()
    calendar = gen.days_from_civil
    monkeypatch.setattr(
        gen, "days_from_civil", lambda year, month, day: calendar(year, month, day) + 1
    )
    with pytest.raises(AssertionError) as refusal:
        gen._self_check_arithmetic()
    assert "proleptic Gregorian" in str(refusal.value)



# ------------------------------------ every case, with its own branch reverted


# G14.3 requires EVERY case to fail when the branch it exists for is
# removed or reverted, and review item P2-C4-C2 found four of thirteen
# carrying such a mutant and nine carrying none. Four with and ten
# without is the same gap in a quieter form: a case whose own rule can
# be withdrawn while every committed byte stays where it was proves
# nothing about that rule, and that is exactly how the ninth case's
# branch carried a withdrawn rule for two rounds.
#
# So the mutants are ONE TABLE. Its keys are asserted equal to the whole
# case set below, which is what stops a case from being added without
# one; each entry replaces one named piece of the oracle with the rule
# its case exists to rule out; and each must either move that case's
# cells or stop the oracle from building it. Every entry builds its case
# UNMUTATED first, so a mutant that would have refused for some reason
# of its own cannot pass by refusing.


CHANGES_THE_CELLS = "changes the cells"


class Mutant(typing.NamedTuple):
    """One case's own branch, put back the way the method rules out."""

    branch: str
    attribute: str
    replacement: object
    outcome: str


def _toward_the_later_instant(position, denominator, rungs):
    """G7.3's rounding turned over: ceiling instead of floor."""
    segment = gen.ladder_segment(position, denominator)
    above = 100 * position - gen.PCT[segment] * denominator
    width = (gen.PCT[segment + 1] - gen.PCT[segment]) * denominator
    return rungs[segment] - (
        (above * (rungs[segment + 1] - rungs[segment])) // -width
    )


def _stratified_ranks(rungs, parsed, words):
    """G7.3's WITHDRAWN placement: one cell per rank in its own stratum.

    THE RULE LANDING 2b.6 REPLACED, restored here so the case that pins
    the date form still fails when the placement rule is withdrawn. The
    two ends are pinned and no interior rung is: each interior rank is
    interpolated inside the band from `k / P` to `(k + 1) / P`, which is
    what gave every day almost exactly its expected count and put every
    published rung a day or more early.

    It spends one word per interior rank, exactly as the real rule does,
    so the mutant differs from it in WHERE the ranks land and in nothing
    else -- not in how many words the column draws, which would move
    every column generated after it and make the case fail for a second
    reason.
    """
    ordinals = []
    for rank in range(parsed):
        if rank == 0:
            ordinals.append(rungs[0])
        elif rank == parsed - 1 and parsed >= 2:
            ordinals.append(rungs[len(gen.PCT) - 1])
        else:
            ordinals.append(
                gen.interpolated_ordinal(
                    rank * gen.TWO64 + next(words), parsed * gen.TWO64, rungs
                )
            )
    return ordinals


_precision_form = gen.precision_form


def _zero_based_quarter(
    ordinal, resolution, time_precision, subsecond_digits, mark="T", **written
):
    """G7.5's quarter form off by one: `2024-Q0` for the first quarter.

    The keyword arguments the reversal of owner decision 5 added --
    which member the date half is written in, and at which conventions
    (landing 2b.6) -- ride through untouched, so this mutant still
    differs from the real rule in the quarter's own figure and in
    nothing else.
    """
    if resolution == "quarter":
        return f"{1970 + ordinal // 4:04d}-Q{ordinal % 4}"
    return _precision_form(
        ordinal, resolution, time_precision, subsecond_digits, mark, **written
    )


def _month_as_a_day(
    ordinal, resolution, time_precision, subsecond_digits, mark="T", **written
):
    """G7.1's month row withdrawn: the month read in the DAY space.

    The one mistake a month invites, because both spaces count from the
    same origin and both write four figures, a dash and two more: an
    implementation that let the month fall through to the day branch
    would put a value in the column that no cell of it holds. Every
    cell moves.
    """
    if resolution == "month":
        return f"{1970 + ordinal // 12:04d}-{ordinal % 12 + 1:02d}-01"
    return _precision_form(
        ordinal, resolution, time_precision, subsecond_digits, mark, **written
    )


_offset_form = gen.offset_form


def _no_clock_conversion(offset):
    """G7.4's clock conversion made optional: the suffix without the move."""
    suffix, _shift = _offset_form(offset)
    return suffix, 0


def _reproduce_instead_of_standing_in(used, wanted):
    """G10.4 withdrawn: an unparsed cell copied from a parsed one."""
    return [min(used)] * wanted


def _through_the_ordinal_space(
    text, resolution, time_precision, subsecond_digits, shift, mark="T",
    **written,
):
    """G7.5's endpoint route withdrawn: both ends back through G7.1.

    The mark rides through unchanged, and so do the arguments the
    reversal of owner decision 5 added -- which member the date half is
    written in, and at which conventions (landing 2b.6) -- so the mutant
    differs from the real rule only in the ROUTE and never in the
    separator or the spelling.
    """
    return gen.precision_form(
        gen.ordinal_of(text, resolution) + shift,
        resolution,
        time_precision,
        subsecond_digits,
        mark,
        **written,
    )


def _marks_from_the_first_rank(column, parsed):
    """P4-D39's rotation withdrawn: the names spent from the first rank up."""
    if column["resolution"] != "datetime" or parsed == 0:
        return ["T"] * parsed
    named = {
        name: count
        for name, count in column["datetime_separators"].items()
        if name != "(withheld)"
    }
    if not named:
        return ["T"] * parsed
    order = sorted(named)
    commonest = max(order, key=lambda name: (named[name], -order.index(name)))
    marks = []
    for name in order:
        marks += [gen.MARK_OF[name]] * named[name]
    marks += [gen.MARK_OF[commonest]] * (parsed - len(marks))
    return marks[:parsed]


def _named_counts_only(column):
    """Landing 2b.3's pool withdrawn: the withheld pool back on the commonest mark."""
    return {
        name: count
        for name, count in column.get("datetime_separators", {}).items()
        if name != "(withheld)"
    }


def _three_marks_everywhere(column):
    """Landing 2b.3's permitted marks withdrawn: a slashed stamp offered all three."""
    return gen.MARKS_BY_COMMONNESS


def _every_rank_a_moment(column, parsed):
    """Owner decision 4's narrowing withdrawn: every rank written with a clock."""
    return [False] * parsed


def _no_move_onto_midnight(column, ordinals, shifts):
    """Landing 2b.3's move onto a midnight withdrawn: the interpolated instants kept."""
    return list(ordinals)


def _ends_alone(column, parsed):
    """The repair pass withdrawn: only the two ends settle their form and offset."""
    fixed = {0: (column["earliest_utc_offset"],)}
    if parsed >= 2:
        fixed[parsed - 1] = (column["latest_utc_offset"],)
    return fixed


def _days_on_either_clock(column):
    """Landing 2b.3's shared-clock rule withdrawn: counted in days on either clock."""
    if column.get("all_at_midnight", False):
        return "date"
    return column["resolution"]


_REAL_STYLED_SPELLING = gen.styled_spelling


def _grouped_at_every_order(
    style, value, integer_valued, order, mark="", negative="minus", plus=False,
    pad=-1,
):
    """P4-D38's order rule withdrawn: a cell that spent zeros is grouped too."""
    text = _REAL_STYLED_SPELLING(
        style, value, integer_valued, order, "", negative, plus, pad
    )
    if style in ("plain", "leading_plus", "decimal"):
        return gen._group_thousands(text, mark)
    return text


def _exchange_withdrawn(content):
    """P4-D26's exchange withdrawn: a declared column keeps its point."""
    return list(content)


def _notation_withdrawn(text, notation):
    """Landing 2b.2's notation withdrawn: every negative keeps its minus."""
    return text


def _every_mark_a_comma(column):
    """Landing 2b.2's other marks withdrawn: every published mark is a comma."""
    return ","


def _plus_from_the_first_cell(count, styles, values):
    """Landing 2b.2's spread withdrawn: the plus taken from the first cell up."""
    carries = [False] * len(values)
    left = count
    for index, (style, value) in enumerate(zip(styles, values)):
        if left and style == "decimal" and not value < 0:
            carries[index] = True
            left -= 1
    return carries


def _ties_toward_zero(value):
    """G5.4's integer rule with the tie direction taken out."""
    whole = int(value)
    rest = value - float(whole)
    if rest > 0.5:
        return float(whole + 1)
    if rest < -0.5:
        return float(whole - 1)
    return float(whole)


def _a_one_digit_exponent(digits, decpt, marker):
    """G6.2's exponent form with the two-digit rule taken out."""
    body = digits[0] + ("." + digits[1:] if len(digits) > 1 else "")
    power = decpt - 1
    return f"{body}{marker}{'-' if power < 0 else '+'}{abs(power)}"


def _outward_without_the_gaps(ladder, places, position, low_ended=False, high_ended=False):
    """G8.3a's walk with its first part withdrawn: outward steps only.

    The method takes the values BETWEEN the published numbers that no
    published number holds before it steps beyond either end, because a
    held-back reading is as often inside the published span as outside
    it. This steps outward from the first position, so the largest
    held-back group is written below the smallest published number
    instead of in the gap beside it.
    """
    step = position // 2 + 1
    low = gen.rescaled(ladder["lowest"], ladder["places"], places, True) - step
    high = gen.rescaled(ladder["highest"], ladder["places"], places, False) + step
    if not ladder["anchored"]:
        low, high = -step, step
    low_held = not low_ended and gen.sign_held(low, ladder["signs"])
    high_held = not high_ended and gen.sign_held(high, ladder["signs"])
    if not low_held and not high_held:
        return ("end", None, None)
    if position % 2 == 0:
        return ("here", low, "low") if low_held else ("skip", None, "low")
    return ("here", high, "high") if high_held else ("skip", None, "high")


_NEXT_ON_THE_LADDER = gen.next_on_ladder


def _next_on_the_ladder_without_the_census(
    ladder, name, cursor, named, seen, folds, needed=0, pool=None, bounded=False
):
    """G8.3a's walk with the rule on what the census could hold withdrawn.

    A number wearing no named form may then wear any form the census does
    not name, whether or not the census could have counted and pooled it,
    so the level of two in `label_number_tiers` steps past every named
    `%.%` value and writes `10.0` -- the form the census proves the column
    never wore -- instead of ending that side and writing `6`. It ignores
    ``bounded`` with the rest, so the narrow walk of the integration
    repair -- which holds a made-up number to the widest number the column
    shows -- is withdrawn here too: withdrawn alone, the census rule left
    the narrow walk deciding these cells and the case no longer moved.
    """
    return _NEXT_ON_THE_LADDER(ladder, name, cursor, named, seen, folds)


def _levels_from_the_second_spelling(
    used, sizes, census=None, written=(), placed=None, level_shape=""
):
    """G8.3's stand-in walk, started one spelling along.

    The method enumerates a form's spellings IN ORDER and takes the
    first that survives the collision skips and the four neutrality
    tests. This starts at the second instead. Every other property of
    the walk is left exactly as stated -- the skips, the tests, the
    debt the census owes -- so what moves is which spelling each
    suppressed level gets, and nothing else.

    An earlier mutant here turned the LEVEL ORDER over instead, and the
    vacuity check caught it: the spelling comes from a running counter
    and not from the level's size, so reordering the levels changed no
    byte and the branch it named was not one this case holds up.
    """
    seen = set(used)
    folds = {gen.folded(text) for text in used}
    owing = gen.forms_owed(census or {}, written)
    produced: list = []
    counter = 0
    for size in sizes:
        form = gen.neediest_form(owing)
        while True:
            counter += 1
            if form:
                candidate = gen.filled_form(form, counter)
            else:
                candidate = f"group-{counter + 1}"
            if candidate in seen or gen.folded(candidate) in folds:
                continue
            if not gen.usable_stand_in(candidate):
                continue
            seen.add(candidate)
            folds.add(gen.folded(candidate))
            produced.append((candidate, size))
            break
        if form:
            owing[form] = max(0, owing[form] - size)
    return produced


def _spaces_before_flips(parent, used, _target):
    """G8.2's order turned over: the trailing spaces before the case flips.

    It ignores the target form G8.2a asks for, which is the point: the
    order and the form rule are one walk, and turning the order over
    loses the form as well as the spelling.
    """
    seen = set(used)
    spaces = 1
    while True:
        candidate = parent + " " * spaces
        spaces += 1
        if candidate not in seen:
            return candidate


def _no_length_pins(slot, low, high):
    """G9.2's two length pins withdrawn: every slot takes any length."""
    return tuple(range(low, high + 1))


_identifier_family = gen.identifier_family


def _every_band_from_the_figures(band, whole_numbers, length):
    """G9.6's withdrawn rule put back: `all_whole_numbers` means figures."""
    return _identifier_family(gen.FIGURES, whole_numbers, length)


def _no_layout_offered(column):
    """G9.6's layout offer withdrawn: the census is published and unread.

    This is the state landing 2b.18 found and closed -- a column that
    publishes what its record numbers look like and a generator that
    writes them from the band enumeration anyway.
    """
    return []


def _no_layout_mixed(column):
    """G9.6's mixes withdrawn: a group no named layout serves is not mixed.

    Every such group then falls to the band enumeration, which is what
    wrote `A-----5V` for a pooled record number before the mixes existed.
    """
    return []


def _no_layout_preferred(column, groups, families, bands, windows, pinned):
    """G9.6's smooth rotation withdrawn: every group takes the first layout.

    The layouts are then offered in sorted order alone, so the identities
    written once -- which the walk reaches first -- take the first layout
    and the identities written twice take the second.
    """
    return [""] * len(groups)


def _lower_filled_in_capitals(form, step):
    """C6-31a's lower-case key withdrawn: `&` is filled as `@` is."""
    return gen_filled_form(form.replace("&", "@"), step)


def _no_spelling_census(column):
    """G6.8 withdrawn: a count column's census of spellings is not read.

    The ladder walk of G5 and the style walk of G6 write the column, as
    they did before the census existed.
    """
    return gen_numeric_content(dict(column, number_spellings={}))


def _no_level_shape_trade(sizes, shared, level_shape, fixed, seen, folds):
    """G8.3b's trade withdrawn: the shape covers the places as settled.

    The named forms keep the places the census settlement gave them, so
    the places owed no form past the shape's supply take the neutral
    spelling -- which carries a figure, and this oracle refuses to reason
    about one.
    """
    free = [
        place for place in range(len(sizes))
        if place not in fixed and not shared[place]
    ]
    supply = gen.usable_room(level_shape, len(free), seen, folds)
    owed = sorted((-sizes[place], place) for place in free)
    return list(shared), {place for _size, place in owed[:supply]}


def _case_flips_only(parent, longest):
    """G9.3's partner family before edge spacing: case flips and nothing else."""
    for counter in range(1, 1 << sum(1 for c in parent if c.isalpha())):
        yield gen.case_flip(parent, counter)


_packed_grid = gen._packed_grid


def _one_margin_after_another(groups, margins, demanded=True):
    """G9.5 steps 3 and 4 as TWO walks, which the method calls not conforming.

    ``demanded`` is the shape rule's "does THIS shape pack" reading
    (review item P2-C4-F2). The mutant answers the same way whichever
    shape asks it, which is the point: packing one margin after another
    has no answer for this case under any shape the description leaves
    open.
    """
    answers: list = [() for _group in groups]
    placed = list(groups)
    for margin in margins:
        narrowed = [
            (
                size,
                frozenset(
                    name for name in {cell[len(answers[0])] for cell in permitted}
                ),
            )
            for size, permitted in placed
        ]
        taken = _packed_grid(
            [
                (size, frozenset((name,) for name in names))
                for size, names in narrowed
            ],
            (margin,),
        )
        answers = [answer + cell for answer, cell in zip(answers, taken)]
        placed = [
            (
                size,
                frozenset(
                    cell for cell in permitted if cell[: len(answer)] == answer
                ),
            )
            for (size, permitted), answer in zip(placed, answers)
        ]
    return answers


def _point_free_within_the_old_window(value, integer_valued):
    """The sixteen-figure ceiling owner decision 10 lifted, put back.

    The mutant for the pooled-spelling case, and it reverts exactly one
    sentence: a whole value wider than the canonical spelling's
    fixed-point window is told it has no point-free spelling, which is
    what used to send a column of very wide whole numbers back with a
    decimal point on cells its source had written in figures.
    """
    if integer_valued:
        return gen.canonical_spelling(value, True)
    digits, decpt = gen.shortest_round_trip(value)
    if not (-4 < decpt <= 16) or decpt < len(digits):
        return None
    sign = "-" if value < 0 else ""
    return sign + digits + "0" * (decpt - len(digits))


def _one_style_for_the_whole_map(published):
    """G6.4's placement withdrawn: every published form written as `plain`."""
    return {
        style: (sum(published.values()) if style == "plain" else 0)
        for style in gen.STYLE_ORDER
    }


def _clamp_without_the_step(ordinal, last, ceiling):
    """G7A.4's repair with its step-up withdrawn: the clamp alone.

    The clamp keeps a rank inside the published `latest` and does
    nothing whatever about two ranks landing on one time, so a column
    with no slack between its ends comes out holding a time twice.
    """
    if ordinal > ceiling:
        ordinal = ceiling
    return ordinal


def _the_cell_counts_as_if_they_were_the_cores(column):
    """G6A.2's core view withdrawn: the CELL counts handed over instead.

    An affixed column publishes `n_numeric` about its CELLS. On the
    bracket case no cell is itself a number, so that count is nought
    and handing it to the numeric machinery builds no values at all.
    That is a property of the CASE and not of the role: a column whose
    pair is `0` holds cells such as `0191` that wear the pair and read
    as numbers too, so this substitution is not nought everywhere.
    """
    core = dict(column)
    core["n_present"] = column["n_affixed"]
    return core


def _the_sorted_start_and_no_walk(drawn, column, wanted, words):
    """G6B.4 step 5 withdrawn: the sorted start kept, the walk removed.

    Steps 1 and 2 still run -- each position sorted, and the last one
    reversed, permuted or left rank for rank by the mean of the
    published agreements -- and nothing after them.

    The walk moves a rank-for-rank pairing, which agrees at about 1.0,
    TOWARD the agreement the column published. It does not arrive: on
    this column it stops at its try ceiling at 0.2226 against a
    published 0.4323, and calling that reaching the target would be a
    claim the committed bytes contradict.
    """
    total = column["n_joined"]
    last = column["n_parts"] - 1
    running = 0.0
    for value in column["part_agreements"]:
        running = running + gen._field_value(value)
    agreements = column["part_agreements"]
    average = running / float(len(agreements)) if agreements else 0.0
    held = []
    for place in range(column["n_parts"]):
        pairs = sorted((float(text), text) for text in drawn[place])
        held.append([pair[1] for pair in pairs])
    if average < -0.4:
        held[last] = [held[last][total - 1 - seat] for seat in range(total)]
    elif average < 0.4 and len(words) >= max(total - 1, 0):
        order = gen.permutation(total, list(words[: max(total - 1, 0)]))
        held[last] = [held[last][seat] for seat in order]
    return held


# Each row: the case, the branch it exists for, and the rule the method
# rules out put back in its place.
def _notations_from_the_majority(census, default, styles, values):
    """Landing 2b.7's notation census withdrawn from the oracle.

    The rule this puts back is the one the twin followed before plan
    P4-D65.2: `negative_form` publishes the column's MAJORITY and every
    negative cell is written that way, whatever mixture the column
    really held. On `mixed_conventions` that turns eleven cells written
    with a minus into eleven more written in brackets.
    """
    return [default] * len(values)


# The oracle's own rules the five cases of plans P4-D142, P4-D145 and
# P4-D147 pin, held before any test patches them.
gen_mark_places = gen.mark_places
gen_pad_places = gen.pad_places
gen_apart_values = gen.apart_values


def _marks_without_the_bare_remainder(
    census, published, groupable, floor=gen.CASE_SMALL_CELL_FLOOR
):
    """Plan P4-D142's bare remainder withdrawn: the leftover wears the mark."""
    worn = gen_mark_places(census, published, groupable, floor)
    return [
        published if groupable[index] and worn[index] == "" else worn[index]
        for index in range(len(worn))
    ]


def _pool_on_the_published_mark(
    census, published, groupable, floor=gen.CASE_SMALL_CELL_FLOOR
):
    """Plan P4-D142's pool mark withdrawn: the pool wears the published mark."""
    named = {gen.mark_written(mark) for mark, _count in gen.named_conventions(
        census, gen.GROUP_MARK_ORDER
    )}
    worn = gen_mark_places(census, published, groupable, floor)
    return [
        published if groupable[index] and worn[index] and worn[index] not in named
        else worn[index]
        for index in range(len(worn))
    ]


def _asked_with_the_published_mark(census, published):
    """Plan P4-D142's candidate withdrawn: groupability asked of the majority."""
    return published


def _pads_on_the_padded_form_alone(
    census, styles, values, integer_valued, forms=None
):
    """Plan P4-D145's second tier withdrawn: no plus-signed cell is padded."""
    masked = ["plain" if style == "leading_plus" else style for style in styles]
    return gen_pad_places(census, masked, values, integer_valued, forms)


def _apart_without_the_fill(
    wanted, figures, values, sizes, starts, bands, ladder, numeric
):
    """Plan P4-D147's fill withdrawn: the walk alone, as it ran before.

    The fill answers only where the strata number exactly ``wanted``;
    asking the rule with a count one larger keeps every step of the walk
    and stops the fill from recognising the grid, and the walk's own stop
    at the published count is never reached earlier by one more.
    """
    return gen_apart_values(
        wanted + 1 if wanted is not None else None,
        figures, values, sizes, starts, bands, ladder, numeric,
    )


CASE_MUTANTS = {
    "bare_mark_remainder": Mutant(
        branch="plan P4-D142's bare remainder; the mutant writes every "
        "groupable cell no named count covers with the published mark, as "
        "the twin did before that decision, and the eleven bare cells are "
        "grouped",
        attribute="mark_places",
        replacement=_marks_without_the_bare_remainder,
        outcome=CHANGES_THE_CELLS,
    ),
    "plus_padded_field": Mutant(
        branch="plan P4-D145's second tier of named field widths; the mutant "
        "serves the padded form alone and every plus-signed cell is written "
        "two figures short of its field",
        attribute="pad_places",
        replacement=_pads_on_the_padded_form_alone,
        outcome=CHANGES_THE_CELLS,
    ),
    "pooled_mark_cells": Mutant(
        branch="plan P4-D142's pool mark; the mutant writes the pooled "
        "remainder with the published comma, so the comma count passes the "
        "published one",
        attribute="mark_places",
        replacement=_pool_on_the_published_mark,
        outcome=CHANGES_THE_CELLS,
    ),
    "saturated_integers": Mutant(
        branch="plan P4-D147's fill of a saturated integer grid; the mutant "
        "runs the walk alone, which lands strata on points other strata "
        "still need",
        attribute="apart_values",
        replacement=_apart_without_the_fill,
        outcome=CHANGES_THE_CELLS,
    ),
    "unpublished_majority_marks": Mutant(
        branch="plan P4-D142's groupable cells asked with a mark that writes "
        "one; the mutant asks with the published mark, which is none, and "
        "no cell is grouped",
        attribute="candidate_mark",
        replacement=_asked_with_the_published_mark,
        outcome=CHANGES_THE_CELLS,
    ),
    "grouped_charges": Mutant(
        branch="landing 2b.2's spread of signed decimals; the mutant takes "
        "the plus from the first eligible cell upward, which ties a plus to "
        "the smallest values",
        attribute="plus_places",
        replacement=_plus_from_the_first_cell,
        outcome=CHANGES_THE_CELLS,
    ),
    "grouped_decimal_comma": Mutant(
        branch="P4-D38's rule that the mark reaches a cell at leading-zero "
        "order nought only; the mutant groups the cell that spent a zero as "
        "well, and after the exchange it wears a point inside its padding",
        attribute="styled_spelling",
        replacement=_grouped_at_every_order,
        outcome=CHANGES_THE_CELLS,
    ),
    "spaced_brackets": Mutant(
        branch="landing 2b.2's negative notation; the mutant withdraws it and "
        "every negative is written with a hyphen-minus in front",
        attribute="negative_spelled",
        replacement=_notation_withdrawn,
        outcome=CHANGES_THE_CELLS,
    ),
    "apostrophe_minus_sign": Mutant(
        branch="landing 2b.2's minus sign U+2212; the mutant withdraws the "
        "notation and every negative is written with a hyphen-minus in front",
        attribute="negative_spelled",
        replacement=_notation_withdrawn,
        outcome=CHANGES_THE_CELLS,
    ),
    "quoted_trailing_minus": Mutant(
        branch="the right single quotation mark between thousands; the mutant "
        "writes every published mark as a comma",
        attribute="grouping_mark_of",
        replacement=_every_mark_a_comma,
        outcome=CHANGES_THE_CELLS,
    ),
    "spaced_decimal_comma": Mutant(
        branch="P4-D26's exchange beside a no-break space, a mark neither decimal "
        "mark; the mutant withdraws the exchange and every present cell keeps "
        "its point",
        attribute="decimal_comma_spelled",
        replacement=_exchange_withdrawn,
        outcome=CHANGES_THE_CELLS,
    ),
    "narrow_spaced": Mutant(
        branch="the narrow no-break space between thousands; the mutant writes "
        "every published mark as a comma",
        attribute="grouping_mark_of",
        replacement=_every_mark_a_comma,
        outcome=CHANGES_THE_CELLS,
    ),
    "thin_spaced": Mutant(
        branch="the thin space between thousands; the mutant writes every "
        "published mark as a comma",
        attribute="grouping_mark_of",
        replacement=_every_mark_a_comma,
        outcome=CHANGES_THE_CELLS,
    ),
    "lower_case_stand_ins": Mutant(
        branch="C6-31a's lower-case key, filled from the lower-case "
        "alphabet at the positions a `@` takes; the mutant fills it in "
        "capitals, and every stand-in moves",
        attribute="filled_form",
        replacement=_lower_filled_in_capitals,
        outcome=CHANGES_THE_CELLS,
    ),
    "count_spellings": Mutant(
        branch="G6.8's census of spellings, which writes a count column "
        "that wrote one number more than one way as its published "
        "spellings; the mutant withdraws it, and the ladder and style walks "
        "write the column instead",
        attribute="_numeric_content",
        replacement=_no_spelling_census,
        outcome=CHANGES_THE_CELLS,
    ),
    "level_shape_stand_ins": Mutant(
        branch="G8.3b's trade, which moves a large held-back group paying a "
        "named form onto the published labels' shape and settles the form "
        "with single rows summing to it; the mutant withdraws the trade, "
        "and a place past the shape's supply is left the neutral spelling",
        attribute="level_shape_spent",
        replacement=_no_level_shape_trade,
        outcome="reasons only about stand-ins with no figure",
    ),
    "identifier_layout": Mutant(
        branch="G9.6's smooth weighted rotation of a layout census over the "
        "identities (contract 7.12); the mutant withdraws it, so every "
        "identity written once takes `@%%%%%` and every identity written "
        "twice takes `@@%%%%`, binding a layout to how often it recurs",
        attribute="layout_preferences",
        replacement=_no_layout_preferred,
        outcome=CHANGES_THE_CELLS,
    ),
    "identifier_layout_mixes": Mutant(
        branch="G9.6's mixes of a layout census's kinds, which write the "
        "cells no named layout serves (plan P4-D128); the mutant withdraws "
        "them, and the fourteen pooled cells fall to the band enumeration",
        attribute="layout_stand_in_bases",
        replacement=_no_layout_mixed,
        outcome=CHANGES_THE_CELLS,
    ),
    "date_only": Mutant(
        branch="G7.3's placement as landing 2b.6 rewrites it: the nine "
        "interior rungs pinned to their PUBLISHED values and every other "
        "rank drawn inside the gap between the pinned ranks either side "
        "of it; the mutant restores the withdrawn stratified placement, "
        "and the interior ranks move",
        attribute="spread_ordinals",
        replacement=_stratified_ranks,
        outcome=CHANGES_THE_CELLS,
    ),
    "free_text_joint": Mutant(
        branch="G9.5 steps 3 and 4 as ONE packing; the mutant walks the "
        "class counts first and the alphabet counts second, and no whole "
        "group can answer for what the second walk is left with",
        attribute="_packed_grid",
        replacement=_one_margin_after_another,
        outcome="no assignment of whole groups meets every quota",
    ),
    "identifier_edge_spacing": Mutant(
        branch="G9.3's partner family as a case flip, edge spacing, or "
        "both; the mutant is the case-flip-only construction, and this "
        "column is written in figures, so it supplies nothing at all",
        attribute="partner_family",
        replacement=_case_flips_only,
        outcome="infeasible corner",
    ),
    "identifier_fold_collisions": Mutant(
        branch="G9.2's two length pins, which are what make `min_length` "
        "and `max_length` exact at no cost in words; the mutant lets every "
        "slot take any length in the range",
        attribute="slot_lengths",
        replacement=_no_length_pins,
        outcome="recount max_length as 2 and the case publishes 4",
    ),
    "identifier_whole_numbers": Mutant(
        branch="G9.6's bands, which come from the two published alphabet "
        "counts; the mutant is revision 1's withdrawn rule, that "
        "`all_whole_numbers` true means every group is written from the "
        "figures",
        attribute="identifier_family",
        replacement=_every_band_from_the_figures,
        outcome="recount n_all_digits as 12 and the case publishes 4",
    ),
    "joined_readings": Mutant(
        branch="G6B.4 step 5, the pairing walk itself; the mutant keeps "
        "the sorted start of steps 1 and 2 and removes the search "
        "after it. A rank-for-rank start pairs largest with largest "
        "and agrees at about 1.0, while this column publishes 0.4323 "
        "and holds the earlier position above the later in only seven "
        "of twelve rows, so the walk has real work here -- measured, "
        "six of its twelve cells move. The walk does NOT reach the "
        "published agreement even so: it stops at its try ceiling at "
        "0.2226, which the case records rather than hides",
        attribute="repaired_pairing",
        replacement=_the_sorted_start_and_no_walk,
        outcome=CHANGES_THE_CELLS,
    ),
    "affixed_brackets": Mutant(
        branch="G6A.2's core view, which hands the numeric machinery "
        "the CORE class counts and not the cell counts; the mutant "
        "hands over the cell counts. On THIS column no cell is itself "
        "a number -- every one wears a bracket pair -- so the cell "
        "count is nought and the column comes out with nothing in it. "
        "The oracle stops at the WORD BUDGET, which is the first place "
        "the swap shows: G4.3 reads that budget over the cores too, so "
        "a nought cell count asks for no content words at all. This is "
        "a property of the CASE and not of the role: a column whose "
        "pair is `0` can hold cells such as `0191` that wear the pair "
        "AND read as numbers, so an affixed column's cell `n_numeric` "
        "is not nought in general",
        attribute="affixed_core_view",
        replacement=_the_cell_counts_as_if_they_were_the_cores,
        outcome="asks for 0 content words",
    ),
    "clock_ladder": Mutant(
        branch="G7A.4's all-different repair, which steps a rank that "
        "landed on the previous rank's time up to the next ordinal "
        "before clamping it to the published latest; the mutant keeps "
        "the clamp and withdraws the step, and this column has no "
        "slack to absorb it -- eleven seconds for eleven parsed cells "
        "-- so two times come out written twice",
        attribute="clock_repair",
        replacement=_clamp_without_the_step,
        outcome=CHANGES_THE_CELLS,
    ),
    "long_tail_levels": Mutant(
        branch="G8.3's stand-in walk, which enumerates a form's "
        "spellings IN ORDER and takes the first that survives the "
        "collision skips; the mutant starts one spelling along, so "
        "every one of the twenty suppressed levels gets a different "
        "stand-in",
        attribute="invented_levels",
        replacement=_levels_from_the_second_spelling,
        outcome=CHANGES_THE_CELLS,
    ),
    "label_numbers": Mutant(
        branch="G8.3a's walk for a held-back number, which fills the "
        "gaps between the published numbers before it steps beyond "
        "either end; the mutant steps outward from the start, so the "
        "largest held-back group leaves the gap and every number moves",
        attribute="outward_at",
        replacement=_outward_without_the_gaps,
        outcome=CHANGES_THE_CELLS,
    ),
    "label_number_tiers": Mutant(
        branch="G8.3a's rule on what the census could hold, which ends a "
        "side of the walk where the next form is one the census would have "
        "counted and pooled and it pooled nothing; the mutant writes that "
        "form, and the level of two moves from `6` to `10.0`",
        attribute="next_on_ladder",
        replacement=_next_on_the_ladder_without_the_census,
        outcome=CHANGES_THE_CELLS,
    ),
    "label_variants": Mutant(
        branch="G8.2's order, case flips before trailing spaces; the "
        "mutant goes straight to the spaces and every invented variant "
        "moves",
        attribute="invented_variant",
        replacement=_spaces_before_flips,
        outcome=CHANGES_THE_CELLS,
    ),
    # RETARGETED AT LANDING 2b.6 PART 2, and the reason is a coverage
    # loss named rather than hidden. This case used to withdraw P4-D39's
    # day-unit rule by counting a column wholly at midnight in seconds,
    # and its interior ranks then landed part-way through a day. They
    # still do -- measured: rank 3 moves from day 19846 to 19846 days
    # plus 25,374 seconds -- but the CELLS no longer move, because
    # counting in seconds also turns `snaps_to_midnight` on, and landing
    # 2b.3's snap pulls every rank back to the nearest midnight INSIDE
    # ITS OWN GAP. Since G7.3 now pins the rungs and confines each draw
    # to a gap, the snap reproduces the day-unit rule exactly, so
    # withdrawing either rule alone leaves the same twin. A mutant whose
    # branch is genuinely redundant cannot move a byte, and pretending
    # otherwise would be the "guard that passes" this file exists to
    # refuse. So this case now holds up the PLACEMENT rule, which is
    # load-bearing for it, and the day-unit rule's own frozen mutant is
    # recorded as withdrawn in G14.3.
    "midnight_days": Mutant(
        branch="G7.3's placement as landing 2b.6 rewrites it, on a column "
        "counted in whole days: the nine interior rungs pinned to their "
        "PUBLISHED values and every other rank drawn inside the gap "
        "between the pinned ranks either side of it; the mutant restores "
        "the withdrawn stratified placement and the interior days move",
        attribute="spread_ordinals",
        replacement=_stratified_ranks,
        outcome=CHANGES_THE_CELLS,
    ),
    "mixed_conventions": Mutant(
        branch="P4-D65.2's census of notations, spent cell by cell over the "
        "negative cells; the mutant writes every negative in the column's "
        "majority, brackets, which is what the twin wrote before that "
        "decision and is the defect it repairs",
        attribute="notation_places",
        replacement=_notations_from_the_majority,
        outcome=CHANGES_THE_CELLS,
    ),
    "mixed_marks": Mutant(
        branch="P4-D39's rotation, which spreads the census of marks evenly "
        "over the ranks; the mutant spends the names from the first rank "
        "upward, and the marks cluster by date",
        attribute="_separator_allocation",
        replacement=_marks_from_the_first_rank,
        outcome=CHANGES_THE_CELLS,
    ),
    "pooled_marks": Mutant(
        branch="landing 2b.3's withheld pool, which is written with the marks "
        "the census leaves unnamed; the mutant puts it back on the commonest "
        "named mark, and the space and the t the pool stood for are erased",
        attribute="mark_weights",
        replacement=_named_counts_only,
        outcome=CHANGES_THE_CELLS,
    ),
    "slashed_pool": Mutant(
        branch="landing 2b.3's permitted marks, a space alone on a slashed "
        "stamp; the mutant offers the pool all three, and the cells take marks "
        "no such table writes",
        attribute="permitted_marks",
        replacement=_three_marks_everywhere,
        outcome=CHANGES_THE_CELLS,
    ),
    "midnight_mixed_forms": Mutant(
        branch="the narrowing of owner decision 4, which writes the bare-date "
        "ranks of a joint column counted in days as bare dates; the mutant "
        "writes every rank as a moment",
        attribute="form_allocation",
        replacement=_every_rank_a_moment,
        outcome=CHANGES_THE_CELLS,
    ),
    "partial_midnight": Mutant(
        branch="landing 2b.3's move onto midnight; the mutant keeps the "
        "interpolated instants, and the values at midnight owed are not written",
        attribute="snapped_to_midnight",
        replacement=_no_move_onto_midnight,
        outcome=CHANGES_THE_CELLS,
    ),
    "midnight_two_offsets": Mutant(
        branch="landing 2b.3's reading of a column wholly at local midnight "
        "on the shared clock, counted in seconds and moved onto a midnight of "
        "each rank's own offset; the mutant counts it in days, and a rung "
        "published at 23:00 lands on the day before",
        attribute="ordinal_space",
        replacement=_days_on_either_clock,
        outcome=CHANGES_THE_CELLS,
    ),
    "midnight_bare_offsets": Mutant(
        branch="the repair pass of landing 2b.3, which settles the form and "
        "the offset of every rank whose instant the published tail fixes "
        "before the rotation; the mutant settles the two ends alone, and rung "
        "ranks are written as the day before and at T02:00:00+02:00",
        attribute="instant_offsets",
        replacement=_ends_alone,
        outcome=CHANGES_THE_CELLS,
    ),
    "leap_second_endpoint": Mutant(
        branch="G7.5's endpoint route, which builds the two ends from the "
        "published endpoint's own fields; the mutant sends them back "
        "through the ordinal space of G7.1, which has no place for a "
        "seconds field of 60",
        attribute="endpoint_cell",
        replacement=_through_the_ordinal_space,
        outcome=CHANGES_THE_CELLS,
    ),
    "mixed_parsed_unparsed": Mutant(
        branch="G10.4's stand-ins, which are counted rather than "
        "reproduced; the mutant copies a parsed cell into their place and "
        "the three unparsed cells read back as dates",
        attribute="text_stand_ins",
        replacement=_reproduce_instead_of_standing_in,
        outcome=CHANGES_THE_CELLS,
    ),
    "numeric_decimal_styles": Mutant(
        branch="G6.2's canonical spelling at the two boundaries of the "
        "fixed-point window; the mutant drops the two-digit exponent rule, "
        "and the pinned smallest value stops writing `1e-05`",
        attribute="_exponent_form",
        replacement=_a_one_digit_exponent,
        outcome=CHANGES_THE_CELLS,
    ),
    "numeric_integer": Mutant(
        branch="G5.4's integer rule, to nearest with ties toward POSITIVE "
        "INFINITY; the mutant rounds ties toward zero, and the four strata "
        "sitting on exactly 2.5 write 2 instead of 3",
        attribute="integer_rule",
        replacement=_ties_toward_zero,
        outcome=CHANGES_THE_CELLS,
    ),
    "numeric_pooled_spelling": Mutant(
        branch="owner decision 10's point-free spelling at any width, and "
        "the pooled cell spelled by its own value beside it; the mutant "
        "puts the sixteen-figure ceiling back, so a whole value wider than "
        "the canonical window is told it has no point-free spelling",
        attribute="point_free_spelling",
        replacement=_point_free_within_the_old_window,
        outcome=CHANGES_THE_CELLS,
    ),
    "numeric_point_free_styles": Mutant(
        branch="G6.1's literal placements, where a cell named `decimal` "
        "carries a point and one named `leading_plus` a `+`; the mutant "
        "sends the whole published map to one form",
        attribute="_effective_style_map",
        replacement=_one_style_for_the_whole_map,
        outcome=CHANGES_THE_CELLS,
    ),
    "offset_bearing": Mutant(
        branch="G7.4's clock conversion, which is not optional: a "
        "published instant is written on the wall clock of the offset its "
        "own cell carries; the mutant writes the instant itself",
        attribute="offset_form",
        replacement=_no_clock_conversion,
        outcome=CHANGES_THE_CELLS,
    ),
    "quarter": Mutant(
        branch="G7.5's quarter form and the quarter ordinal; the mutant "
        "counts the quarter from nought and every cell moves",
        attribute="precision_form",
        replacement=_zero_based_quarter,
        outcome=CHANGES_THE_CELLS,
    ),
    "month_span": Mutant(
        branch="G7.1's month ordinal and G7.5's month cell form; the "
        "mutant writes the month as the first day of that month, which "
        "is the day space the month must not fall into, and every cell "
        "moves",
        attribute="precision_form",
        replacement=_month_as_a_day,
        outcome=CHANGES_THE_CELLS,
    ),
    "unrepresentable_joint": Mutant(
        branch="G10.5's three margins packed together on the six-row "
        "column of its step 2; the mutant withdraws the too-small shape, "
        "which is what spending `n_whole` on the too-large cells amounts "
        "to, and the column has no packing at all",
        attribute="UNREPRESENTABLE_SHAPES",
        replacement=tuple(
            shape for shape in gen.UNREPRESENTABLE_SHAPES if shape[0] != "too_small"
        ),
        outcome="no assignment of whole groups meets every quota",
    ),
    "unrepresentable_exponent": Mutant(
        branch="G10.5 revision 5's exponent spelling family; the mutant "
        "puts the too-large shape's floor back to the digit string's own "
        "310 characters, which is the rule revision 4 carried, and the "
        "column published at five and six characters is then written "
        "three hundred and ten wide with neither published end held",
        attribute="EXPONENT_LARGE_ROOM",
        replacement=gen.OVERFLOW_FIGURES,
        outcome="recount min_length as 310",
    ),
}


def test_withdrawing_the_layout_offer_stops_the_oracle(monkeypatch) -> None:
    """The layout census is EXACT-OBSERVABLE, and the oracle holds itself to it.

    The registered mutant of `identifier_layout` withdraws the ROTATION,
    which moves cells. Withdrawing the OFFER altogether is a different
    reversal and is held up here: the twenty-four cells then come from
    the band enumeration, wear no published layout, and the recount of
    contract 7.12 stops the oracle before any byte could be written.
    """
    before, _claims = gen.build_case("identifier_layout")
    assert before["cells"]
    monkeypatch.setattr(gen, "layout_offer", _no_layout_offered)
    with pytest.raises(AssertionError) as refusal:
        gen.build_case("identifier_layout")
    assert "wear the layout '@%%%%%' 0 times" in str(refusal.value)


def test_the_mutant_table_names_every_case_and_nothing_else() -> None:
    """The keys ARE the case set, which is what closes the gap.

    Review item P2-C4-C2: four of thirteen cases carried an own-branch
    mutant, and the claim that all thirteen were covered rested on a
    sentence rather than on a check. This is the check. A case added to
    either committed file without a mutant beside it turns it red, and so
    does a mutant left behind by a case that has gone.
    """
    assert tuple(sorted(CASE_MUTANTS)) == ALL_CASES


@pytest.mark.parametrize("name", ALL_CASES)
def test_each_case_fails_when_its_own_branch_is_reverted(
    name: str, monkeypatch
) -> None:
    """Every case, put through the rule the method rules out for it.

    A case that would still be written after its own rule was withdrawn
    is a case that tests nothing (G14.3). Each mutant must therefore move
    its case's cells or stop the oracle from building it -- and the
    unmutated build above it is the vacuity check: a mutant that passed
    because the case cannot be built at all would prove nothing either.
    """
    mutant = CASE_MUTANTS[name]
    before, _claims = gen.build_case(name)
    assert before["cells"], f"{name} builds no cells unmutated"
    monkeypatch.setattr(gen, mutant.attribute, mutant.replacement)
    if mutant.outcome == CHANGES_THE_CELLS:
        after, _mutant_claims = gen.build_case(name)
        assert after["cells"] != before["cells"], (
            f"{name} is written the same way with its own branch reverted "
            f"({mutant.branch}), so no committed byte holds that branch up"
        )
    else:
        with pytest.raises(AssertionError) as refusal:
            gen.build_case(name)
        assert mutant.outcome in str(refusal.value), (
            f"{name}: the mutant of {mutant.branch} stopped the oracle for "
            "some other reason than its own"
        )


def test_the_style_case_writes_each_published_form_as_itself() -> None:
    """The claim `numeric_point_free_styles` freezes, beside its mutant.

    A cell named `decimal` carries a point, one named `leading_plus` a
    `+` and one named `leading_zero` a redundant `0`, each recounted by
    the contract's own first-match ladder. This is the affirmative half;
    the table above holds the mutant that sends the whole map to one
    form, which is the silent change of the reader's inferred type that
    owner decision 10 was taken to close.
    """
    case, _claims = gen.build_case("numeric_point_free_styles")
    written = dict.fromkeys(gen.STYLE_ORDER, 0)
    for cell in case["content"]:
        written[parsing.numeric_style(cell)] += 1
    published = _unwrap(case["column"])["numeric_styles"]
    assert {name: count for name, count in written.items() if count} == published


def _every_empty_record_at_the_top(form, n_rows):
    """G2.1's placing withdrawn: every record holding nothing leading.

    The rule puts `leading` at the top, `trailing` at the bottom and
    `interior` spread evenly between; this puts all of them at the top,
    which is the arrangement a reader would take for a table whose first
    rows were lost.
    """
    empties = form["empty_rows"]
    total = empties["interior"] + empties["leading"] + empties["trailing"]
    targets = [False for _row in range(n_rows)]
    for row in range(min(total, n_rows)):
        targets[row] = True
    return targets


def _one_reading_for_each_candidate(text, candidate, at):
    """CODEX-5 withdrawn: one reading per candidate, settings afterwards.

    The walk this replaced read each candidate ONE way -- no space after
    the delimiter, doubled quotes -- and left the spacing and the
    escaping to be settled from the delimiter it had already chosen.
    """
    sample = gen.doc_read_records(
        text, candidate, gen.DOC_ESCAPE_DOUBLED, False, at,
        gen.DOC_SAMPLE_RECORDS,
    )
    at_width, total, width = gen.width_share(sample)
    if width < 2:
        return None
    opening = 0
    while opening < len(sample) and gen.leads_the_table(sample[opening]):
        opening = opening + 1
    if opening < len(sample) and len(sample[opening]["fields"]) != width:
        return None
    return {"at_that_width": at_width, "records": total, "width": width}


def _classed_by_their_characters(census, cells):
    """G2.2 withdrawn: a cell's class read off the twin's own characters.

    This is the defect the whole seam exists to prevent: the census says
    the column held TEXT, its cells are digit strings, and a twin written
    this way hands a reader a column of numbers where the source had
    codes.
    """
    out = []
    for cell in cells:
        if cell == "":
            out += ["absent"]
            continue
        out += ["number" if gen.sheet_number_spelling(cell) else "text"]
    return out


# ----------------------------------------- the document cases, bound

# THE FIVE TRANSFORMS THAT PRODUCE A WHOLE DOCUMENT (landing 2b.17).
# Every case above answers "what does one COLUMN hold". These five
# answer "what does the FILE look like", and until this landing not one
# of them had a second implementation of any kind: landings 2b.9, 2b.10
# and 2b.11 built the written form, the row arrangement and the workbook
# writer, each recorded the gap in its own report, and none could close
# it -- the workbook writer's rules were stated in no specification at
# all, so there was nothing to write a second implementation FROM. Method
# section G2.2 was written at this landing for that reason, and these
# bind the oracle written from it to the shipped code.
#
# A document case carries no column, no words and no word budget, so it
# is NOT in `ALL_CASES` and the parametrized tests above do not reach it.
# Its own bindings are below, one per transform, and its own mutant table
# is at the foot of this file beside the other.
DOCUMENT_CASES = (
    "delimiter_reading",
    "row_arrangement",
    "withheld_line_marks",
    "workbook_sheet",
    "written_form_lines",
)

EVERY_CASE = tuple(sorted(ALL_CASES + DOCUMENT_CASES))


def _document_document() -> dict:
    return json.loads(DOCUMENT_VECTORS.read_text(encoding="utf-8"))


def _document_case(name: str) -> dict:
    return _document_document()["cases"][name]


def _form_of(case: dict) -> "dialect.Dialect":
    """One case's published dialect block, typed by the shipped loader.

    The block is the INPUT the written form and the arrangement really
    take, so the loader that reads it is the right way in: a block this
    oracle wrote that the loader would refuse is a block no description
    could carry, and that would be worth knowing here rather than later.
    """
    return contract._dialect_block(case["dialect"])


def test_the_written_form_is_the_file_the_method_requires() -> None:
    """Method G2, byte for byte, against a file the oracle wrote alone.

    The whole text is one assertion and the lines are another, and they
    are kept apart on purpose: a disagreement about the BYTES BETWEEN
    lines -- an ending, the mark, the end-of-file byte -- is a different
    defect from a disagreement about what a line holds, and a single
    comparison of the finished text would report either as the other.
    """
    case = _document_case("written_form_lines")
    form = _form_of(case)
    names = tuple(case["names"])
    rows = tuple(tuple(row) for row in case["rows"])
    assert dialect.twin_text(names, rows, case["write_header"], form) == (
        case["text"]
    ), (
        "the twin's bytes are not the ones method section G2 requires. The "
        "oracle is the specification's answer; do not change it to match "
        "the implementation."
    )
    # ...and each line, through the shipped writer's own parts, so that a
    # failure names which line rather than which file.
    lines = list(case["lines"])
    at = 0
    assert lines[at] == "sep=" + form.delimiter
    at = at + 1
    for run in form.preamble:
        for _line in range(run.lines):
            assert lines[at] == dialect.preamble_line(run)
            at = at + 1
    assert lines[at] == dialect.header_line(names, form)
    at = at + 1
    written = [line for line in lines[at:] if line != ""]
    for index in range(len(rows)):
        assert written[index] == dialect.data_line(rows[index], form)


def test_the_rows_stand_where_the_method_puts_them() -> None:
    """Method G2.1, both halves, against the shipped arrangement.

    Two arrangements, because no one file can carry both rules: contract
    FD5 refuses records holding nothing beside a row sequence, and a
    table with a row order publishes records holding nothing only where
    it has some.
    """
    case = _document_case("row_arrangement")
    for entry in case["arrangements"]:
        form = contract._dialect_block(entry["dialect"])
        columns = [tuple(column) for column in entry["columns"]]
        placed = dialect.arranged(columns, form, entry["n_rows"])
        assert [list(column) for column in placed] == entry["arranged"], (
            entry["why"]
        )


def test_the_lines_before_the_table_are_published_as_their_shape() -> None:
    """Contract FD11 and plan P4-D83, on the two marks a twin cannot write.

    Three rules in one case, asserted one at a time: what a line's shape
    is, what the mark is narrowed to, and what the twin writes for it.
    """
    case = _document_case("withheld_line_marks")
    delimiter = case["delimiter"]
    runs = dialect.preamble_runs(list(case["lines"]), delimiter)
    published = [
        {"kind": run.kind, "lines": run.lines, "mark": run.mark}
        for run in runs
    ]
    assert published == case["runs"]
    written: list = []
    for run in runs:
        for _line in range(run.lines):
            written += [dialect.preamble_line(run)]
    assert written == case["written"]
    # The narrowing itself, line by line, so that a failure names the
    # line whose mark the twin could not have written.
    for index in range(len(case["lines"])):
        line = case["lines"][index]
        kind, mark = dialect.writable_shape(
            *dialect.preamble_shape(line), delimiter
        )
        assert not dialect.mark_breaks_a_line(mark, delimiter), line
        assert written[index] == dialect.preamble_line(
            dialect.PreambleRun(kind=kind, lines=1, mark=mark)
        )


def test_the_delimiter_is_settled_the_way_the_method_settles_it() -> None:
    """Review item CODEX-5, on the file the item was measured on.

    Each candidate's own best reading is asserted before the choice
    between them, because the defect that item found was in the SCORING
    and not in the comparison: a candidate scored one way reads a
    two-column file as one column, and the comparison then picks
    correctly between two wrong answers.
    """
    case = _document_case("delimiter_reading")
    text = case["text"]
    for candidate in dialect.DELIMITERS:
        found = dialect._best_reading(text, candidate, 0)
        published = case["readings"][candidate]
        if published is None:
            assert found is None, candidate
            continue
        assert found is not None, candidate
        share, width, _sample = found
        assert width == published["width"], candidate
        assert share == published["at_that_width"] / published["records"], (
            candidate
        )
    assert dialect.detected_delimiter(text, 0) == case["delimiter"]


def _workbook_profile(case: dict, folder: pathlib.Path) -> contract.Profile:
    """A description carrying this case's workbook block, loaded.

    THE COLUMN BLOCKS ARE INERT HERE, and it is said rather than left to
    be discovered: `sheetwriting.workbook_members` reads
    `source.workbook` and the twin's own cells, and never a column
    block's published facts. Two are carried because a description must
    have one per column and the loader holds the workbook block to that
    count (contract WB1); they are one frozen case's own column, twice,
    so that nothing about them was invented here.
    """
    block = case["workbook"]
    borrowed = _unwrap(_case("spaced_brackets")["column"])
    columns = []
    for index in range(len(case["names"])):
        column = dict(borrowed)
        column["name"] = case["names"][index]
        column["position"] = index + 1
        columns += [column]
    document = {
        "columns": columns,
        "created_with": "0+unknown",
        "n_columns": len(columns),
        "n_rows": case["n_rows"],
        "profile_version": 6,
        "publication_notes": [],
        "relationships": _relationships(),
        "settings": _settings([]),
        "source": {
            "dialect": dialect.document_of(
                dialect.ordinary(len(columns), case["n_rows"], True)
            ),
            "encoding": "utf-8-sig",
            "used_fallback_encoding": False,
            "header_source": "file",
            "header_by_convention": False,
            "header_evidence": "the first row of the sheet held the "
            "columns' names.",
            "workbook": block,
        },
    }
    path = fixtures.write_profile(folder, "workbook.json", document)
    return contract.load_profile(str(path))


def test_the_workbook_twin_is_the_package_the_method_requires(
    tmp_path: pathlib.Path,
) -> None:
    """Method G2.2, part by part, against a package the oracle wrote alone.

    The twin is built by hand from the case's own cells rather than
    generated, and that is what the transform takes: the writer is
    handed a description and a twin's CELLS, and turns them into the
    parts of a package. Nothing about which cells a column generator
    would produce is in question here, and a case that generated them
    would be testing two transforms at once.
    """
    case = _document_case("workbook_sheet")
    profile = _workbook_profile(case, tmp_path)
    columns = tuple(tuple(column) for column in case["cells"])
    rows = tuple(
        tuple(columns[place][row] for place in range(len(columns)))
        for row in range(case["n_rows"])
    )
    twin = generation.Twin(
        names=tuple(case["names"]),
        write_header=case["write_header"],
        n_rows=case["n_rows"],
        columns=columns,
        rows=rows,
        outcomes=(),
        deviations=(),
        approximations=(),
        remarks=(),
        words_drawn=0,
        seed=0,
    )
    members = sheetwriting.workbook_members(profile, twin)
    assert [name for name, _text in members] == case["members"], (
        "the parts of the twin's package, or their order, are not the "
        "ones method section G2.2 requires"
    )
    for name, text in members:
        assert text == case["parts"][name], name


DOCUMENT_MUTANTS = {
    "written_form_lines": (
        Mutant(
            branch="G2's lines before the table; the mutant writes none "
            "of them, which is what withdrawing the stand-in amounts to, "
            "and the file loses four lines",
            attribute="preamble_lines_for",
            replacement=lambda form: [],
            outcome=CHANGES_THE_CELLS,
        ),
    ),
    "row_arrangement": (
        Mutant(
            branch="G2.1's rule that a row-sequence column is written in "
            "place LAST; the mutant withdraws that step and the sequence "
            "column keeps the generated cells the sort moved",
            attribute="sequence_columns_written",
            replacement=lambda grid, form, n_rows: None,
            outcome=CHANGES_THE_CELLS,
        ),
        Mutant(
            branch="G2.1's placing of the records holding nothing -- "
            "leading at the top, trailing at the bottom, interior spread "
            "evenly between; the mutant puts every one of them at the top",
            attribute="empty_record_targets",
            replacement=_every_empty_record_at_the_top,
            outcome=CHANGES_THE_CELLS,
        ),
    ),
    "withheld_line_marks": (
        Mutant(
            branch="plan P4-D83's narrowing of a mark the twin could not "
            "write; the mutant hands back the shape unchanged, and the "
            "twin's first line is then a quoted field nothing closes",
            attribute="writable_mark",
            replacement=lambda kind, mark, delimiter: (kind, mark),
            outcome=CHANGES_THE_CELLS,
        ),
    ),
    "delimiter_reading": (
        Mutant(
            branch="review item CODEX-5's rule that every setting is "
            "scored WITH the delimiter; the mutant scores each candidate "
            "one way -- no space skipped, doubled quotes -- which is the "
            "rule it replaced, and the file is read as one column",
            attribute="best_reading",
            replacement=_one_reading_for_each_candidate,
            outcome=CHANGES_THE_CELLS,
        ),
    ),
    "workbook_sheet": (
        Mutant(
            branch="G2.2's rule that a cell's class comes from the "
            "column's published census and never from the twin's own "
            "characters; the mutant classes each cell by what its "
            "characters could be read as, and a column of text whose "
            "cells are digit strings is written as numbers",
            attribute="sheet_cell_classes",
            replacement=_classed_by_their_characters,
            outcome=CHANGES_THE_CELLS,
        ),
    ),
}


def test_the_document_mutant_table_names_every_document_case() -> None:
    """The keys ARE the document case set, for the reason the other is.

    A document case added without a mutant beside it turns this red, and
    so does a mutant left behind by a case that has gone.
    """
    assert tuple(sorted(DOCUMENT_MUTANTS)) == DOCUMENT_CASES
    for name in DOCUMENT_CASES:
        assert DOCUMENT_MUTANTS[name], name


@pytest.mark.parametrize("name", DOCUMENT_CASES)
def test_each_document_case_fails_when_its_own_rule_is_reverted(
    name: str, monkeypatch
) -> None:
    """Every document case, put through the rule the method rules out.

    `row_arrangement` carries two, because it pins two rules that no one
    file can carry together, and a case with one mutant for two rules is
    a case whose second rule could be withdrawn with every committed
    byte where it was.
    """
    before, _claims = gen.build_document_case(name)
    for mutant in DOCUMENT_MUTANTS[name]:
        with monkeypatch.context() as patched:
            patched.setattr(gen, mutant.attribute, mutant.replacement)
            after, _mutant_claims = gen.build_document_case(name)
            assert after != before, (
                f"{name} is written the same way with its own branch "
                f"reverted ({mutant.branch}), so no committed byte holds "
                "that branch up"
            )
