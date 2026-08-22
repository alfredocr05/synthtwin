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

**Every one of the fourteen carries a mutant that removes or reverts the
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
from synthtwin import contract, generation, parsing, rendering

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
GENERATOR = REPOSITORY / "tools" / "reference" / "make_generation_reference_vectors.py"
BRANCH_GENERATOR = (
    REPOSITORY / "tools" / "reference" / "make_generation_branch_vectors.py"
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


def _generator():
    """The vector generator, loaded from its path (it is not a package)."""
    spec = importlib.util.spec_from_file_location(
        "make_generation_reference_vectors", GENERATOR
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gen = _generator()


def _document() -> dict:
    return json.loads(VECTORS.read_text(encoding="utf-8"))


def _branch_document() -> dict:
    return json.loads(BRANCH_VECTORS.read_text(encoding="utf-8"))


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

# The seven that section adds for the branches those nine leave
# unexercised (review items P2-C3-F3 and P2-C4-C3, and owner decision
# 11's pooled-spelling case), which are the second committed file of the
# same oracle.
BRANCH_CASES = (
    "free_text_joint",
    "identifier_edge_spacing",
    "leap_second_endpoint",
    # The month, added with the second SPAN resolution (plan P4-D4.3
    # item 2). A new transform reaching the twin without an independent
    # frozen case is a transform the generator and the validator agree
    # about with nobody else in the room (review item P4-DATE3-F1).
    "month_span",
    "numeric_point_free_styles",
    "numeric_pooled_spelling",
    "unrepresentable_joint",
)

ALL_CASES = tuple(sorted(REQUIRED_CASES + BRANCH_CASES))

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
    "free_text_joint": 112,
    "identifier_edge_spacing": 113,
    "leap_second_endpoint": 114,
    "numeric_pooled_spelling": 115,
    "month_span": 116,
}

# The cases whose column was declared with --identifier, which the
# contract's invariant A1 binds to settings.forced_identifiers.
DECLARED_IDENTIFIERS = frozenset(
    {
        "identifier_fold_collisions",
        "identifier_whole_numbers",
        "identifier_edge_spacing",
    }
)

def _case(name: str) -> dict:
    """One case, from whichever of the two committed files carries it."""
    document = _branch_document() if name in BRANCH_CASES else _document()
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


def _settings(declared: list) -> dict:
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
            "built_in_numbers": [],
        },
        "declared_missing_values": {
            "n_declared": 0,
            "values_recorded": False,
            "built_in_texts": [],
            "built_in_numbers": [],
        },
        "declaration_matching": "exact_number_when_it_reads_as_one_else_spelling",
        "declaration_publication": "settings_counts_only_columns_unchanged",
        "near_threshold_slack": 0,
        "day_first": False,
        "forced_identifiers": declared,
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
    return {
        "columns": [column],
        "created_with": "0+unknown",
        "n_columns": 1,
        "n_rows": len(case["cells"]),
        "profile_version": 5,
        "publication_notes": [],
        "relationships": _relationships(),
        "settings": _settings(declared),
        "source": {
            "encoding": "utf-8-sig",
            "used_fallback_encoding": False,
            "header_source": "generated",
            "header_by_convention": False,
            "header_evidence": "the file carried no names of its own, so the "
            "columns were named for it.",
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
    """Neither file may be read as the whole of the oracle.

    The two carry disjoint case sets and together carry every case
    method section G14.3 names, and each one's own account says where
    the other lives -- so a reader who opens either is told at once that
    it is half of one artifact rather than all of it.
    """
    named = _document()
    branch = _branch_document()
    assert tuple(sorted(branch["cases"])) == BRANCH_CASES
    assert not set(named["cases"]) & set(branch["cases"])
    assert tuple(sorted(set(named["cases"]) | set(branch["cases"]))) == ALL_CASES
    for document, other in ((named, BRANCH_VECTORS), (branch, VECTORS)):
        assert document["never_imports"] == ["synthtwin", "numpy", "pandas"]
        assert document["method"] == "docs/spec/generation-method-v1.md"
        assert document["generated_by"] == (
            "tools/reference/make_generation_reference_vectors.py"
        )
        assert f"tests/reference/{other.name}" in document["case_set"]


@pytest.mark.parametrize("script", [GENERATOR, BRANCH_GENERATOR])
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

    All fourteen bind normally, with no exception of any kind. The one
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
    expected = "".join(
        ('""' if cell == "" else cell) + "\n" for cell in case["cells"]
    )
    assert case["csv_bytes"] == expected


# ---------------------------------------------------- the proof layer itself


PUBLISHED_NUMBERS = 210
NAMED_COUNTS = 270
BRANCH_PUBLISHED_NUMBERS = 23
BRANCH_NAMED_COUNTS = 121

# Each committed file, with the floors its own proof must clear and the
# case set the oracle writes it from.
COMMITTED_FILES = (
    (VECTORS, None, PUBLISHED_NUMBERS, NAMED_COUNTS),
    (BRANCH_VECTORS, gen.BRANCH_PART, BRANCH_PUBLISHED_NUMBERS, BRANCH_NAMED_COUNTS),
)


def _fields(document: dict) -> frozenset:
    return gen.whole_number_fields(document)


@pytest.mark.parametrize(
    "committed,part,published,named", COMMITTED_FILES, ids=["named", "branches"]
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
    "committed,part,published,named", COMMITTED_FILES, ids=["named", "branches"]
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
    "committed,part,published,named", COMMITTED_FILES, ids=["named", "branches"]
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


_precision_form = gen.precision_form


def _zero_based_quarter(ordinal, resolution, time_precision, subsecond_digits):
    """G7.5's quarter form off by one: `2024-Q0` for the first quarter."""
    if resolution == "quarter":
        return f"{1970 + ordinal // 4:04d}-Q{ordinal % 4}"
    return _precision_form(ordinal, resolution, time_precision, subsecond_digits)


def _month_as_a_day(ordinal, resolution, time_precision, subsecond_digits):
    """G7.1's month row withdrawn: the month read in the DAY space.

    The one mistake a month invites, because both spaces count from the
    same origin and both write four figures, a dash and two more: an
    implementation that let the month fall through to the day branch
    would put a value in the column that no cell of it holds. Every
    cell moves.
    """
    if resolution == "month":
        return f"{1970 + ordinal // 12:04d}-{ordinal % 12 + 1:02d}-01"
    return _precision_form(ordinal, resolution, time_precision, subsecond_digits)


_offset_form = gen.offset_form


def _no_clock_conversion(offset):
    """G7.4's clock conversion made optional: the suffix without the move."""
    suffix, _shift = _offset_form(offset)
    return suffix, 0


def _reproduce_instead_of_standing_in(used, wanted):
    """G10.4 withdrawn: an unparsed cell copied from a parsed one."""
    return [min(used)] * wanted


def _through_the_ordinal_space(
    text, resolution, time_precision, subsecond_digits, shift
):
    """G7.5's endpoint route withdrawn: both ends back through G7.1."""
    return gen.precision_form(
        gen.ordinal_of(text, resolution) + shift,
        resolution,
        time_precision,
        subsecond_digits,
    )


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


def _spaces_before_flips(parent, used, wanted):
    """G8.2's order turned over: the trailing spaces before the case flips."""
    produced: list = []
    seen = set(used)
    spaces = 1
    while len(produced) < wanted:
        candidate = parent + " " * spaces
        spaces += 1
        if candidate in seen:
            continue
        produced.append(candidate)
        seen.add(candidate)
    return produced


def _no_length_pins(slot, low, high):
    """G9.2's two length pins withdrawn: every slot takes any length."""
    return tuple(range(low, high + 1))


_identifier_family = gen.identifier_family


def _every_band_from_the_figures(band, whole_numbers, length):
    """G9.6's withdrawn rule put back: `all_whole_numbers` means figures."""
    return _identifier_family(gen.FIGURES, whole_numbers, length)


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


# Each row: the case, the branch it exists for, and the rule the method
# rules out put back in its place.
CASE_MUTANTS = {
    "date_only": Mutant(
        branch="G7.3's floor rounding, which rounds toward the EARLIER "
        "instant always; the mutant rounds toward the later one, and ten "
        "interior ranks move",
        attribute="interpolated_ordinal",
        replacement=_toward_the_later_instant,
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
    "label_variants": Mutant(
        branch="G8.2's order, case flips before trailing spaces; the "
        "mutant goes straight to the spaces and every invented variant "
        "moves",
        attribute="invented_variants",
        replacement=_spaces_before_flips,
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
}


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
