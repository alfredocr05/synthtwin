"""The affixed-number role's own invariants, each with its red case.

Three obligations of contract section 6.12 that shipped unenforced, and
the scenarios a reviewer wrote them against:

- **AF3.** `n_affixed` is at least the parse-line COUNT of `n_present`.
  A block whose pair never cleared the detection line describes a column
  the producer would have declined, and the loader took it (review item
  P4-AFX-F9).
- **AF-R.** Every column of this role carries the remark that names the
  pair, says how many cells wore it, and names `--identifier` as the
  route for a column of codes. The loader read remarks as arbitrary text
  and never related them to the role, so a profile with no remark at all
  loaded (review item P4-AFX-F11).
- **The competing-readings remark says how far the affix reading got**,
  and how many cells stand-in judging removed where removal moved the
  column across a line. Its form had five arguments and named only the
  numeric, date and categorical readings (review item P4-AFX-F12).

Each is asserted twice: that a conforming description passes, and that
the exact document the reviewer described is refused. An invariant with
only the first half is an invariant nothing shows can fail.
"""

import json
import pathlib
import random
import tempfile

import pytest

import fixtures
from synthtwin import (
    contract,
    errors,
    generation,
    parsing,
    profile,
    quality,
    reading,
    rendering,
    taxonomy,
    validation,
)


def _document(
    folder: pathlib.Path, name: str, values: "list[str]"
) -> "dict[str, object]":
    """One single-column table, described the way `profile` describes it."""
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(
        folder, f"{name}.csv", fixtures.single_column_table(name, values)
    )
    read = reading.read_table(f"{table}")
    return profile.build_document(read, taxonomy.Settings(), [])


def _loaded(
    folder: pathlib.Path, document: "dict[str, object]", stem: str
) -> contract.Profile:
    """One document written and read back through the strict loader."""
    written = fixtures.write_profile(folder, f"{stem}.json", document)
    return contract.load_profile(f"{written}")


# A hundred different words carrying no figure at all, so that a column
# built from them proposes no affix pair whatever: `note 1 of the batch`
# and its neighbours all wear the pair `note ` / ` of the batch`, which
# is the role, not the decline this file needs.
_WORDS = tuple(
    f"{one}{other}"
    for one in ("al", "be", "ce", "de", "ef", "ga", "ho", "in", "jo", "ka")
    for other in (
        "ndar", "rrow", "stle", "lta", "fort", "mma", "nest", "digo",
        "urney", "rmic",
    )
)


def _prices() -> "list[str]":
    """A hundred cells wearing one shared piece of text."""
    return [f"${index}" for index in range(1, 101)]


# -- AF3: the pair cleared the line, or the role was not this one -----


def test_a_column_of_prices_is_read_as_the_affixed_role(
    tmp_path: pathlib.Path,
) -> None:
    """The premise of the three tests below, asserted rather than assumed."""
    document = _document(tmp_path / "green", "price", _prices())
    column = document["columns"][0]
    assert column["role"] == "affixed_number"
    assert column["n_affixed"] == 100
    assert column["n_present"] == 100


def test_a_pair_that_never_cleared_the_line_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """AF3, on the reviewer's own document.

    A hundred present cells at the default parse rate need ninety-nine
    wearing the pair. The block below says fifty, with every core count
    moved to match so that AF4's own closure holds and nothing else can
    be what refuses it -- which is the point: before this invariant was
    enforced, that document loaded and a consumer read a distribution
    off a column whose pair described half of it.
    """
    document = _document(tmp_path / "af3", "price", _prices())
    column = document["columns"][0]
    column["n_affixed"] = 50
    column["n_core_numeric"] = 50
    column["n_used_in_statistics"] = 50
    column["n_left_out_of_statistics"] = column["n_present"] - 50
    with pytest.raises(errors.ProfileError) as raised:
        _loaded(tmp_path / "af3", document, "forged")
    said = f"{raised.value}"
    assert "n_affixed" in said
    assert "99" in said, said


def test_the_line_is_read_off_the_settings_the_document_carries(
    tmp_path: pathlib.Path,
) -> None:
    """...and not off a number this loader keeps to itself.

    A description written at a LOWER parse rate says so in its own
    settings, and AF3 is then a lower bar for it. A loader holding one
    fixed number would refuse a conforming document written by a run
    somebody had every right to make.
    """
    values = [f"${index}" for index in range(1, 61)]
    values = values + [f"{index}" for index in range(61, 101)]
    folder = tmp_path / "settings"
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(
        folder, "price.csv", fixtures.single_column_table("price", values)
    )
    read = reading.read_table(f"{table}")
    document = profile.build_document(
        read, taxonomy.Settings(minimum_parse_rate=0.5), []
    )
    column = document["columns"][0]
    assert column["role"] == "affixed_number"
    # ALL HUNDRED WEAR A WRAPPER, and sixty of them wear the `$`.
    # This read sixty until plan P4-D36: the forty bare numbers wore
    # nothing, so they were STRAGGLERS and the column published no
    # value of theirs at all. The bare wrapper is a member of the
    # vocabulary now, so a price column where some cells omit the sign
    # describes all hundred of its numbers.
    assert column["n_affixed"] == 100, column["n_affixed"]
    assert column["affix_prefix"] == "$", column["affix_prefix"]
    assert [
        (one["prefix"], one["suffix"], one["count"])
        for one in column["affix_variants"]
    ] == [("", "", 40)], column["affix_variants"]
    assert document["settings"]["minimum_parse_rate"] == 0.5
    loaded = _loaded(folder, document, "lowered")
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.AffixedFacts)
    assert facts.n_affixed == 100


# -- AF-R: the sentence this role always carries ----------------------


def test_the_phrase_the_loader_looks_for_is_the_phrase_that_is_written(
    tmp_path: pathlib.Path,
) -> None:
    """The two spellings of one sentence are held to agreeing.

    The loader may not import the profiler's taxonomy, so it cannot
    render the remark it requires and carries a phrase of it instead.
    That arrangement is only honest while the phrase is really in the
    sentence, which is what this asserts -- against the RENDERED form
    and not against another copy of the phrase.
    """
    said = taxonomy.rendered(taxonomy.REMARK_AFFIXED, ("$", "", 100))
    assert contract.AFFIXED_REMARK_MARK in said
    document = _document(tmp_path / "phrase", "price", _prices())
    carried = [
        remark
        for remark in document["columns"][0]["remarks"]
        if contract.AFFIXED_REMARK_MARK in remark
    ]
    assert len(carried) == 1, document["columns"][0]["remarks"]


def test_an_affixed_column_with_the_remark_taken_out_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """AF-R, on the reviewer's own document: remove every remark and load.

    The obligation is unconditional -- no test of the values separates a
    column of measurements from a column of account numbers -- so a
    description that dropped the sentence would publish an average and a
    spread over what may be codes, with nothing on the page saying so.
    """
    document = _document(tmp_path / "afr", "price", _prices())
    document["columns"][0]["remarks"] = []
    with pytest.raises(errors.ProfileError) as raised:
        _loaded(tmp_path / "afr", document, "silent")
    assert "remarks" in f"{raised.value}"


def test_a_remark_that_is_not_that_one_does_not_answer_for_it(
    tmp_path: pathlib.Path,
) -> None:
    """A column carrying SOME sentence is not a column carrying this one."""
    document = _document(tmp_path / "other", "price", _prices())
    document["columns"][0]["remarks"] = ["a sentence of some other kind"]
    with pytest.raises(errors.ProfileError):
        _loaded(tmp_path / "other", document, "other")


def test_a_sentence_holding_only_the_marker_does_not_answer_for_it(
    tmp_path: pathlib.Path,
) -> None:
    """An invariant is not a password (codex round 2, item P4-AFX2-F8).

    The loader cannot render the sentence -- it may not import the
    profiler's taxonomy -- so it holds a document to the sentence's
    SHAPE. Held to one fragment, it accepted a remark that was that
    fragment and nothing else: no pair, no count, no command, and a
    reader of that description told none of the three things AF-R
    exists to tell them.
    """
    document = _document(tmp_path / "marker", "price", _prices())
    document["columns"][0]["remarks"] = [contract.AFFIXED_REMARK_MARK]
    with pytest.raises(errors.ProfileError):
        _loaded(tmp_path / "marker", document, "marker")


def test_a_remark_naming_another_columns_count_does_not_answer_for_it(
    tmp_path: pathlib.Path,
) -> None:
    """...and the count in the sentence is THIS block's own.

    A sentence saying how many cells wore the pair is about a column
    that has that many; carrying one from a different column would
    misdescribe this one in the one place the reader is looking.
    """
    document = _document(tmp_path / "count", "price", _prices())
    remarks = document["columns"][0]["remarks"]
    moved = [
        remark.replace("100 of this column", "40 of this column", 1)
        for remark in remarks
    ]
    document["columns"][0]["remarks"] = moved
    with pytest.raises(errors.ProfileError):
        _loaded(tmp_path / "count", document, "count")


def test_every_fixed_fragment_the_loader_wants_is_in_the_real_sentence(
    tmp_path: pathlib.Path,
) -> None:
    """The whole skeleton, not one phrase, and it is really the sentence's."""
    said = taxonomy.rendered(taxonomy.REMARK_AFFIXED, ("$", "", 100))
    at = 0
    for part in contract.AFFIXED_REMARK_PARTS:
        found = said.find(part, at)
        assert found >= 0, part
        at = found + len(part)
    assert said.startswith("100 ")


def test_the_written_out_literals_are_the_tuple_beside_them(
    tmp_path: pathlib.Path,
) -> None:
    """The loader's own calls use literals; this holds them to the record.

    The offline audit refuses a method call whose argument it cannot
    resolve, so the fragment tests are written out one call at a time
    rather than walked out of `AFFIXED_REMARK_PARTS`. Two lists of the
    same four phrases is two lists that can stop being the same, so the
    tuple is checked against what the function actually accepts: a
    sentence built from the tuple passes, and one with any single
    fragment removed does not.
    """
    parts = contract.AFFIXED_REMARK_PARTS
    assert len(parts) == 4
    clause = contract._affix_clause("$", "")
    built = f"100 {parts[0]} {clause}, " + " ".join(parts[1:])
    assert contract._is_the_affixed_remark(built, 100, clause)
    assert not contract._is_the_affixed_remark(built, 99, clause)
    for place in range(len(parts)):
        short = "100 " + " ".join(
            parts[index] for index in range(len(parts)) if index != place
        )
        assert not contract._is_the_affixed_remark(
            f"{short} {clause}", 100, clause
        ), parts[place]
    backwards = "100 " + " ".join(reversed(parts))
    assert not contract._is_the_affixed_remark(
        f"{backwards} {clause}", 100, clause
    )
    # ...AND THE PAIR ITSELF. A sentence with every generic fragment in
    # order, the right count, and the WRONG pair is a required warning
    # that misdescribes the column it warns about.
    assert not contract._is_the_affixed_remark(
        built, 100, contract._affix_clause("kg", "")
    )


def test_a_remark_naming_another_pair_does_not_answer_for_this_block(
    tmp_path: pathlib.Path,
) -> None:
    """AF-R binds the two spellings positionally, character for character.

    The block publishes prefix `$` and no suffix. A remark saying its
    cells read `'kg' followed by a number` carries every generic
    fragment, the right count and the marker -- and describes a column
    nobody holds.
    """
    document = _document(tmp_path / "pair", "price", _prices())
    remarks = document["columns"][0]["remarks"]
    moved = [
        remark.replace("'$' followed by a number", "'kg' followed by a number")
        for remark in remarks
    ]
    assert moved != remarks
    document["columns"][0]["remarks"] = moved
    with pytest.raises(errors.ProfileError):
        _loaded(tmp_path / "pair", document, "pair")


# -- the stand-in pass may not re-run the rules that already declined --


def test_removal_over_the_cores_does_not_hand_the_column_to_an_earlier_rule(
    tmp_path: pathlib.Path,
) -> None:
    """Codex round 2, item P4-AFX2-F4, on its own cells.

    Eleven `-999 mg` cells beside eighty-nine cycling `1 mg` to `10 mg`
    hold eleven different spellings, so the categorical ceiling of ten
    declines and the affixed rule takes the column. The core pass then
    reads `-999` as a stand-in and removes those eleven cells -- and
    the column now holds ten different spellings, which the categorical
    rule WOULD take if it were allowed to run again.

    It is not allowed to: the contract lets removal be followed only by
    the rules after the ones that already declined. Otherwise a removal
    hands the column to a rule that declined it, the numbers inside the
    affixes vanish, the type a consumer routes on changes, and nothing
    on the page says why.
    """
    values = ["-999 mg"] * 11
    values = values + [f"{1 + index % 10} mg" for index in range(89)]
    document = _document(tmp_path / "judged", "dose", values)
    column = document["columns"][0]
    assert column["role"] == "affixed_number", column["role"]
    assert column["n_present"] == 89
    assert column["n_missing"] == 11
    assert column["n_affixed"] == 89
    assert "levels" not in column
    verdicts = column["sentinel_verdicts"]
    assert verdicts, "the removed stand-in is published as a verdict"
    assert verdicts[0]["candidate"] == "-999"
    assert column["percentiles"]["min"] == 1.0


# -- the competing-readings remark ------------------------------------


def test_a_column_of_two_pairs_says_how_far_the_affix_reading_got(
    tmp_path: pathlib.Path,
) -> None:
    """The reviewer's scenario, and what P4-D36's guard costs.

    Ninety-eight cells wearing one wrapper and two wearing another. No
    single wrapper clears the line, so this column declines and its
    owner is owed the count the closest reading reached.

    A column may wear a SET of wrappers since plan P4-D36 -- but every
    wrapper of a set must STAND APART from the number it wraps, and
    `EUR99` writes its letters flush against the digits. That guard is
    what keeps a set of code schemes from being read as a quantity, and
    a currency written without a space is what it costs. The column is free
    text here as it was before, so nothing anybody had is lost, and the
    sentence saying how far the reading got is still owed and still
    given.
    """
    values = [f"${index}" for index in range(1, 99)]
    values = values + ["EUR99", "EUR100"]
    document = _document(tmp_path / "two-pairs", "price", values)
    column = document["columns"][0]
    assert column["role"] == "free_text", column["role"]
    said = " ".join(column["remarks"])
    assert "98 of its values are numbers wearing one shared piece of text" in (
        said
    ), said
    assert "which is the reading that came closest" in said
    # ...and the same column with a SPACE between the currency and the
    # number IS read, which is what says the guard is about the flush
    # letters and not about the set.
    spaced = [f"$ {index}" for index in range(1, 99)] + ["EUR 99", "EUR 100"]
    apart = _document(tmp_path / "two-spaced", "price", spaced)
    assert apart["columns"][0]["role"] == "affixed_number", (
        apart["columns"][0]["role"]
    )


def test_a_column_no_pair_reaches_says_so_with_a_count_of_none(
    tmp_path: pathlib.Path,
) -> None:
    """...and the clause is a count, so it is there when the count is zero.

    A sentence that appeared only where the reading got somewhere would
    leave a reader unable to tell "this reading reached nothing" from
    "nobody tried it".
    """
    values = [
        f"batch {_WORDS[index % len(_WORDS)]} of the run for {word}"
        for index, word in enumerate(_WORDS)
    ]
    document = _document(tmp_path / "no-pair", "note", values)
    column = document["columns"][0]
    assert column["role"] == "free_text"
    said = " ".join(column["remarks"])
    assert "0 of its values are numbers wearing one shared piece of" in said


def test_the_removal_clause_is_silent_where_nothing_was_removed(
    tmp_path: pathlib.Path,
) -> None:
    """Naming a removal of none would say something happened."""
    values = [
        f"batch {_WORDS[index % len(_WORDS)]} of the run for {word}"
        for index, word in enumerate(_WORDS)
    ]
    document = _document(tmp_path / "unremoved", "note", values)
    said = " ".join(document["columns"][0]["remarks"])
    assert "were read as stand-ins for 'no value' and taken out" not in said


def test_the_remark_carries_nine_arguments_and_the_grammar_says_so(
    tmp_path: pathlib.Path,
) -> None:
    """The arity is the contract's, and the note grammar is where it lives.

    A form whose rendering names two more things than its arity admits
    is a form the publication guard cannot check, so the count is
    asserted against the shipped grammar rather than against the
    sentence.

    IT READ SEVEN UNTIL 2026-08-31. The affixed role's landing added
    the affix reach and what stand-in judging removed; the
    advisory-remark landing (residual R-P4-24) added the two the
    contract had already written down and the producer had never sent
    -- how far a CLOCK reading got, and the recoverable-distribution
    advice of amendment A-P4-1 item 4.
    """
    assert taxonomy.NOTE_ARITY[taxonomy.REMARK_NO_READING_FITS] == 9


def test_every_affixed_document_this_file_builds_round_trips(
    tmp_path: pathlib.Path,
) -> None:
    """The green direction for all of it: written, read back, unchanged.

    Every refusal above is a refusal of an EDITED document. This is the
    unedited one, so none of them can be passing because the producer
    writes something the loader refuses outright.
    """
    document = _document(tmp_path / "round", "price", _prices())
    loaded = _loaded(tmp_path / "round", document, "round")
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.AffixedFacts)
    assert facts.affix_prefix == "$"
    assert facts.affix_suffix == ""
    assert facts.n_affixed == 100
    assert json.loads(
        (tmp_path / "round" / "round.json").read_text(encoding="utf-8")
    )["columns"][0]["role"] == "affixed_number"

# -- what the internal audit found, each with the scenario it found it on --


def _kept(values: "list[str]", kept: "tuple[str, ...]") -> "dict[str, object]":
    """One dose column described with a `--keep-value` declaration."""
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "dose.csv", fixtures.single_column_table("dose", values)
    )
    read = reading.read_table(f"{table}")
    return profile.build_document(
        read, taxonomy.Settings(kept_values=kept), []
    )


_UNIT_CELLS = [f"{index} mg" for index in range(1, 90)] + ["-999 mg"] * 11


def test_a_kept_whole_cell_is_kept_on_the_affixed_role() -> None:
    """C6-117: a value named with `--keep-value` is data, and no judged
    pass may read it as a hole.

    The core pass compared declarations against the CORE, so the
    spelling the contract tells an owner to name -- the whole cell,
    `-999 mg` -- matched no core and was ignored. Eleven cells the
    owner declared to be data were published as holes, on the same page
    whose disclosure section said the owner had named that word.
    """
    column = _kept(_UNIT_CELLS, ("-999 mg",))["columns"][0]
    assert column["role"] == "affixed_number"
    assert column["n_present"] == 100
    assert column["n_missing"] == 0
    assert column["percentiles"]["min"] == -999.0
    assert column["missing_by_source"] == {}
    verdicts = column["sentinel_verdicts"]
    assert [entry["verdict"] for entry in verdicts] == ["kept_as_a_number"]
    assert verdicts[0]["reason"] == "kept_by_you"


def test_a_declaration_matching_no_cell_is_inert_on_the_affixed_role() -> None:
    """...and the same rule from the other side.

    `-999` matches no whole cell of a column of `-999 mg`, so it must
    change nothing. Compared against the core it matched every one, kept
    the stand-in in the statistics, and published no verdict at all --
    so the description said the smallest dose was -999 and said nothing
    anywhere about why.
    """
    column = _kept(_UNIT_CELLS, ("-999",))["columns"][0]
    plain = _kept(_UNIT_CELLS, ())["columns"][0]
    assert column["n_present"] == plain["n_present"] == 89
    assert column["percentiles"]["min"] == plain["percentiles"]["min"] == 1.0
    assert [entry["verdict"] for entry in column["sentinel_verdicts"]] == [
        "read_as_missing"
    ]


def test_a_straggler_that_wears_the_pair_is_counted_once() -> None:
    """The two populations overlap, and the arithmetic has to say so.

    A column of `1-01` to `1-99` wears the pair `1` / empty, and its
    hundredth cell `12` wears it too AND reads as a number. Subtracting
    the wearers from the text class alone and clamping at zero swallowed
    that overlap in a class that did not hold it, so the twin came out
    one cell too long and `generate` stopped with an internal-check
    message telling its user synthtwin has a bug.
    """
    folder = pathlib.Path(tempfile.mkdtemp())
    for tail in ("12", "1e999", "(5)"):
        values = [f"1-{index:02d}" for index in range(1, 100)] + [tail]
        table = fixtures.write(
            folder, "code.csv", fixtures.single_column_table("code", values)
        )
        document = profile.build_document(
            reading.read_table(f"{table}"), taxonomy.Settings(), []
        )
        if document["columns"][0]["role"] != "affixed_number":
            continue
        written = fixtures.write_profile(folder, "code.json", document)
        loaded = contract.load_profile(f"{written}")
        twin = generation.generate(loaded, 3)
        assert len(twin.columns[0]) == loaded.n_rows, tail


def test_no_affix_of_the_measured_file_reaches_the_report() -> None:
    """V5.4, on the one comparison in the module that was not routed.

    A milligram description checked against a file whose cells read
    `SECRET-5.16` printed `SECRET` on the achieved line of the quality
    report. Every sibling comparison over file text keeps the measured
    side back and prints the sentence saying why; the affix pair was the
    outlier, and the contract's publication-class carve-out is about the
    DESCRIPTION's own block, not about a report on somebody's file.
    """
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder,
        "dose.csv",
        fixtures.single_column_table(
            "dose", [f"{index} mg" for index in range(1, 101)]
        ),
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(), []
    )
    described = contract.load_profile(
        f"{fixtures.write_profile(folder, 'dose.json', document)}"
    )
    other = fixtures.write(
        folder,
        "other.csv",
        fixtures.single_column_table(
            "dose", [f"SECRET-{index}.16" for index in range(1, 101)]
        ),
    )
    outcome = validation.measure(described, f"{other}")
    report = parsing.visible_lines(quality.quality_report(described, outcome))
    assert "SECRET" not in report
    # THE TWO SPELLINGS, NAMED RATHER THAN MATCHED BY PREFIX. The set
    # of wrappers (plan P4-D36) put a THIRD `counts.affix` subcheck
    # beside these two, and a filter written over the shared first word
    # took it in and read `0 == ""` as a report that had leaked. That
    # entry is a COUNT of other wrappers, not a spelling of anybody's
    # file, so V5.4 does not reach it and it is asserted below on its
    # own terms.
    pair = [
        check
        for check in outcome.checks
        if check.subcheck
        in ("counts.affix_prefix", "counts.affix_suffix")
    ]
    assert len(pair) == 2
    for check in pair:
        assert check.verdict == validation.MISSED
        assert check.achieved == ""
    variants = [
        check
        for check in outcome.checks
        if check.subcheck == "counts.affix_variants"
    ]
    assert len(variants) == 1
    # THE SET IS COMPARED IN FULL AND ITS MEASURED SIDE IS KEPT BACK
    # too, for the reason the pair's is: a wrapper is text of the file
    # (review round 1, item 2).
    assert variants[0].achieved == ""


def test_a_snap_never_carries_a_cell_past_a_published_end() -> None:
    """The two ladder ends are exact, and pinning the CELL is not enough.

    A column publishing a minimum of 2.11 and a width of one figure had
    an interior cell -- not the endpoint cell, which is pinned -- snapped
    to 2.1, so the twin's own smallest value was a number the
    description does not publish and `validate` reported the exact
    minimum MISSED on a twin of that description.
    """
    folder = pathlib.Path(tempfile.mkdtemp())
    values = [f"2.{10 + index}" for index in range(1, 11)]
    values = values + [f"{3 + index // 10}.{index % 10}" for index in range(50)]
    table = fixtures.write(
        folder, "v.csv", fixtures.single_column_table("v", values)
    )
    # THE FLOOR IS DECLARED: the case wants a column whose narrower
    # fraction width is POOLED, and the default smallest group size
    # became one (owner ruling, plan amendment A-P4-37), at which
    # nothing is held back at all (contract C5-S13).
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(small_cell_floor=11),
        [],
    )
    column = document["columns"][0]
    assert column["fraction_widths"] == {"1": 50, "(withheld)": 10}
    assert column["percentiles"]["min"] == 2.11
    described = contract.load_profile(
        f"{fixtures.write_profile(folder, 'v.json', document)}"
    )
    for seed in range(6):
        twin = generation.generate(described, seed)
        target = fixtures.write(
            folder, f"twin-{seed}.csv", rendering.twin_csv(twin)
        )
        outcome = validation.measure(described, f"{target}")
        missed = [
            check.subcheck
            for check in outcome.checks
            if check.verdict == validation.MISSED
        ]
        # A WIDTH QUOTA MAY GO UNMET AND IS REPORTED (A-P4-15); no
        # other obligation may move, and the ladder ends least of all.
        other = [
            subcheck
            for subcheck in missed
            if not subcheck.startswith("widths.published.")
            # AND THE COUNT OF DIFFERENT NUMBERS, on the same terms as
            # the width quota beside it (amendment A-P4-55, residual
            # R-P4-154). This column publishes sixty different values
            # over sixty cells at two fraction widths and has never
            # held them: 52 to 57 at four seeds before the landing
            # that made the count an obligation and 53 to 57 after.
            # What this case is about is the SNAP, and it still
            # asserts that no snap carries a cell past a published
            # end.
            and subcheck != "distinct.n_distinct_values"
        ]
        assert other == [], (seed, missed)
        assert "ladder.min" not in missed
        assert "ladder.max" not in missed


def test_an_invented_straggler_is_not_a_spelling_this_column_calls_absent(
) -> None:
    """A present cell of a twin may not be a hole of its own description.

    A column of prices beside eleven cells spelled `1`, declared with
    `--missing-value 1`, publishes `missing_by_source {"1": 11}`. The
    straggler walk counted up from one and wrote `1`, so the twin's own
    description read that present cell as absent and five exact counts
    moved against the description the twin was built from.
    """
    folder = pathlib.Path(tempfile.mkdtemp())
    values = [f"${index}" for index in range(1, 100)] + ["1"] * 11 + ["7"]
    table = fixtures.write(
        folder, "price.csv", fixtures.single_column_table("price", values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(declared_missing_values=("1",)),
        [],
    )
    column = document["columns"][0]
    assert column["missing_by_source"] == {"1": 11}
    described = contract.load_profile(
        f"{fixtures.write_profile(folder, 'price.json', document)}"
    )
    twin = generation.generate(described, 5)
    target = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{target}")
    missed = [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    ]
    assert missed == [], missed


def test_the_all_different_remark_does_not_deny_the_distribution() -> None:
    """A block publishing a ladder may not say it publishes nothing.

    The free-text form of the all-different remark says "Nothing from
    this column is published either way -- no value of it, and no
    distribution", and tells the reader to rewrite the values so that
    their distribution will be described. Both clauses are false of an
    affixed column, which publishes the full distribution, and the
    column of `$1` to `$100` carried them.
    """
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "price.csv", fixtures.single_column_table("price", _prices())
    )
    column = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(), []
    )["columns"][0]
    assert column["role"] == "affixed_number"
    assert column["mean"] == 50.5
    said = " ".join(column["remarks"])
    assert "every value in this column is different" in said
    assert "which keeps its distribution" in said
    assert "Nothing from this column is published" not in said
    assert "write them as plain numbers" not in said


def test_an_affix_spelling_may_not_stand_in_the_header_sentence() -> None:
    """The fourth sentence path belongs to no column, so it binds to none.

    A note carrying an affix argument at `source.header_evidence` passed
    the whole publication guard while the same note on a column's own
    evidence was refused. Nothing writes one there today, which is not
    the same thing as a control.
    """
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "price.csv", fixtures.single_column_table("price", _prices())
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(), []
    )
    document["source"]["header_evidence"] = taxonomy.note(
        taxonomy.REMARK_AFFIXED, ("PATIENT-4471-SSN-", "", 40)
    )
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)

def test_a_kept_cell_leaves_the_column_saying_it_cannot_be_checked() -> None:
    """The rescue is recorded without the word that made it.

    `--keep-value "-999 mg"` names a WHOLE CELL; the description records
    the decision as a verdict about the CORE `-999`, and the pair is
    published beside it -- but the cell's own spelling is nowhere, so
    rebuilding the reading rule from the description judges those cells
    holes again. Checked against the very file it was written from, the
    column reported fifteen obligations MISSED, every one a number
    untrue of that file. It says it cannot be checked instead.
    """
    document = _kept(_UNIT_CELLS, ("-999 mg",))
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "dose.csv", fixtures.single_column_table("dose", _UNIT_CELLS)
    )
    described = contract.load_profile(
        f"{fixtures.write_profile(folder, 'dose.json', document)}"
    )
    unrebuildable = validation.unrebuildable_columns(described)
    assert "dose" in unrebuildable
    assert "kept as values by a word you named" in unrebuildable["dose"]
    outcome = validation.measure(described, f"{table}")
    missed = [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    ]
    assert missed == [], missed
    assert outcome.census.not_checkable > 0


def test_a_pool_bigger_than_the_forms_left_to_hold_it_is_refused() -> None:
    """Invariant P6: six forms, and a pooled one holds fewer than the floor.

    A column of two hundred and forty numbers naming `plain` and
    `decimal` could publish a remainder of sixty, which the four forms
    left can hold at most forty of. Nothing checked it, and `generate`
    then told its reader the TWIN had missed a published count -- the
    tool blaming its own output for an edit somebody made to the
    description.
    """
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder,
        "amount.csv",
        fixtures.single_column_table(
            "amount", [f"{index}" for index in range(1, 241)]
        ),
    )
    # THE FLOOR IS DECLARED, and this case cannot do without it: the
    # default smallest group size became one (owner ruling, plan
    # amendment A-P4-37), at which a pool of ANY size is refused by
    # C5-S13 before P6 is ever reached -- so the case would be answered
    # by the wrong rule and would stay green with P6 deleted.
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(small_cell_floor=11),
        [],
    )
    column = document["columns"][0]
    column["numeric_styles"] = {"plain": 160, "decimal": 20, "(withheld)": 60}
    column["fraction_widths"] = {"2": 20}
    with pytest.raises(errors.ProfileError):
        _loaded(folder, document, "pooled")


def test_the_class_writers_write_their_own_class() -> None:
    """Two published classes were unreachable, and this is the red case.

    The straggler writer filtered its candidates with `spelling in
    used` after the builder had already recorded every one of them
    there, so the test was always true and every cell fell through to
    an internal placeholder. A column of prices beside cells too large
    to hold and cells of contradictory notation wrote `(no pair 0)` for
    all of them: two exact published counts missed, and the deviation
    note blamed group granularity for cells that were never built.
    """
    for kind in (
        generation._CLASS_OUT_OF_RANGE,
        generation._CLASS_CONTRADICTORY,
        generation._CLASS_TEXT,
    ):
        written = generation._unaffixed_spellings(
            kind, 3, 3, 3, ("$", ""), {"$1.00": 1}
        )
        assert len(written) == 3, kind
        for cell in written:
            assert "no pair" not in cell, (kind, written)


def test_the_snap_may_not_turn_a_column_of_measurements_into_counts() -> None:
    """`integer_valued` is what a consumer routes on (AF6).

    Twenty-six cells written `1.`, twenty-five `2.` and twenty-nine at
    one figure publish `integer_valued: false` and a width of zero for
    fifty-one of them. The twin wrote every value whole and came back a
    column of COUNTS -- the type changed under a reader who had been
    told the column was continuous.
    """
    folder = pathlib.Path(tempfile.mkdtemp())
    values = ["1."] * 26 + ["2."] * 25
    values = values + [f"1.{index % 10}" for index in range(29)]
    table = fixtures.write(
        folder, "v.csv", fixtures.single_column_table("v", values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(), []
    )
    column = document["columns"][0]
    assert column["integer_valued"] is False
    assert column["fraction_widths"]["0"] == 51
    described = contract.load_profile(
        f"{fixtures.write_profile(folder, 'v.json', document)}"
    )
    for seed in range(4):
        twin = generation.generate(described, seed)
        target = fixtures.write(
            folder, f"twin-{seed}.csv", rendering.twin_csv(twin)
        )
        outcome = validation.measure(described, f"{target}")
        missed = [
            check.subcheck
            for check in outcome.checks
            if check.verdict == validation.MISSED
        ]
        for owed in ("axes.role", "axes.statistical_type", "type.integer_valued"):
            assert owed not in missed, (seed, missed)


def test_no_count_of_the_measured_file_is_printed_below_the_floor() -> None:
    """V5.1: this report says only what describing THAT file would publish.

    A description of one pair checked against a file of another counted
    the file's cells under the pair the DESCRIPTION's author chose and
    printed "found: 5" -- an exact count below the publication floor,
    about a file whose own description publishes no affixed fact at
    all, for a reader who may not hold that file.
    """
    folder = pathlib.Path(tempfile.mkdtemp())
    mine = fixtures.write(
        folder,
        "mine.csv",
        fixtures.single_column_table(
            "note", [f"Chen Wu note {index}.5" for index in range(1, 61)]
        ),
    )
    document = profile.build_document(
        reading.read_table(f"{mine}"), taxonomy.Settings(), []
    )
    assert document["columns"][0]["role"] == "affixed_number"
    described = contract.load_profile(
        f"{fixtures.write_profile(folder, 'note.json', document)}"
    )
    # THE MEASURED FILE CARRIES NO NUMBER AT ALL, so its own
    # description publishes no affixed fact and every count of this
    # role is WITHHELD. It used to hold five `Chen Wu note N.5` cells
    # beside fifty-five worded ones: since plan P4-D36 a column may
    # wear a SET of wrappers, so that file describes as this role in
    # its own right and the counts are held rather than withheld --
    # which is the right answer for it and the wrong fixture for this
    # question.
    theirs = fixtures.write(
        folder,
        "theirs.csv",
        fixtures.single_column_table(
            "note",
            [f"Alice Brown note {_WORDS[index % 5]}" for index in range(60)],
        ),
    )
    outcome = validation.measure(described, f"{theirs}")
    for check in outcome.checks:
        if not check.subcheck.startswith("counts.n_"):
            continue
        assert check.achieved != "5", check.subcheck
        if check.subcheck in (
            "counts.n_affixed",
            "counts.n_core_numeric",
            "counts.n_core_out_of_range",
            "counts.n_core_contradictory",
            "counts.n_core_not_numeric",
        ):
            assert check.verdict == validation.WITHHELD, check.subcheck

def test_an_ordinary_two_figure_column_has_a_twin_that_passes() -> None:
    """A description no seed can build is a broken feature (A-P4-18).

    Thirty cells written `5.` beside thirty written `5.01` to `5.30`
    publish a width of zero for half the column. The drawn values hold
    every window; the snap then rounded twenty-six of them onto 5.0 and
    the twin missed p50, p75, p90, p95, the mean and the spread at
    every seed. A conforming twin demonstrably exists -- the source
    column is one -- so the width gives way and the distribution does
    not.
    """
    folder = pathlib.Path(tempfile.mkdtemp())
    values = ["5."] * 30 + [f"5.{index:02d}" for index in range(1, 31)]
    table = fixtures.write(
        folder, "v.csv", fixtures.single_column_table("v", values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(), []
    )
    assert document["columns"][0]["fraction_widths"] == {"0": 30, "2": 30}
    described = contract.load_profile(
        f"{fixtures.write_profile(folder, 'v.json', document)}"
    )
    for seed in range(6):
        twin = generation.generate(described, seed)
        target = fixtures.write(
            folder, f"twin-{seed}.csv", rendering.twin_csv(twin)
        )
        outcome = validation.measure(described, f"{target}")
        missed = [
            check.subcheck
            for check in outcome.checks
            if check.verdict == validation.MISSED
        ]
        for owed in (
            "ladder.p50",
            "ladder.p75",
            "ladder.p90",
            "ladder.p95",
            "moments.mean",
            "moments.std",
        ):
            assert owed not in missed, (seed, missed)
        # ...and the width that gave way is NAMED rather than silent.
        spoken = [
            note for note in twin.deviations if note.fact == "fraction_widths"
        ]
        assert spoken, seed


def test_a_declaration_carried_across_the_pair_protects_the_number() -> None:
    """A-P4-19: every spelling of the candidate, and the count says so.

    Eleven `-999 mg` cells beside eleven `-999.0 mg` cells: naming
    either spelling keeps all twenty-two, because the pass counts and
    removes by NUMBER and one verdict per candidate number is all the
    wire can carry. Pinned here so the reach is witnessed rather than
    discovered, and so a later edit that narrows it is seen.
    """
    values = [f"{index} mg" for index in range(1, 79)]
    values = values + ["-999 mg"] * 11 + ["-999.0 mg"] * 11
    for named in ("-999 mg", "-999.0 mg"):
        column = _kept(values, (named,))["columns"][0]
        assert column["n_present"] == 100, named
        assert column["percentiles"]["min"] == -999.0, named
        verdicts = column["sentinel_verdicts"]
        assert len(verdicts) == 1, named
        assert verdicts[0]["reason"] == "kept_by_you", named
        assert verdicts[0]["n_occurrences"] == 22, named


def test_the_last_resort_straggler_refuses_a_published_hole() -> None:
    """A present cell may never be spelled the way a hole is spelled.

    `_unaffixed_spellings` walks candidates and refuses three things: a
    spelling already written, one that WEARS the affix pair, and one
    this column publishes as a hole. Where every candidate wears the
    pair the walk exhausts its ceiling and falls through to a last
    resort of the package's own -- and that branch kept only two of the
    three, so it could write a published hole as a PRESENT cell. The
    twin's own description then reads that cell as absent and its
    missing counts move against the description it was built from,
    which is the defect `_unaffixed_numbers` already records having
    been repaired for, in the same class of cell.

    Reaching this branch from the profiler was not achieved while the
    refusal was added, so this pins the branch directly rather than
    through a described column, and the rule it pins is the one the two
    sibling walks already keep.
    """
    holes = ("(no pair 0)", "(no pair 1)")
    built = generation._unaffixed_spellings(
        generation._CLASS_TEXT, 3, 1, 1, ("text-", ""), {}, holes
    )
    assert len(built) == 3
    assert len(set(built)) == 3, "the last resort repeated a cell"
    written_as_a_hole = [cell for cell in built if cell in holes]
    assert not written_as_a_hole, (
        "these present cells are spelled exactly the way this column "
        f"publishes a hole, so its twin reads them as absent: "
        f"{written_as_a_hole}"
    )


# -- a column wearing a SET of wrappers (plan P4-D36) -------------------


def _flagged_rows(n_rows: int = 200) -> "list[str]":
    """A laboratory column whose readings carry an abnormal flag.

    THE SHAPE THIS LANDING EXISTS FOR, and it is everywhere in real
    laboratory extracts: a value, and beside a third of them an `H` or
    an `L` saying the result is outside the reference range. Every cell
    holds a number; no single wrapper is worn by enough of them to
    reach the detection line on its own.
    """
    draw = random.Random(11)
    return [
        f"{round(draw.uniform(8, 18), 1)}"
        f"{draw.choice(['', ' H', ' L'])}"
        for _index in range(n_rows)
    ]


def test_a_column_wearing_three_wrappers_is_a_quantity(
    tmp_path: pathlib.Path,
) -> None:
    """THE WITNESS. Before this landing the column published NOTHING.

    No wrapper is worn by a third of the cells, so under the one-pair
    rule none reached the detection line and the column fell to
    `free_text` -- which publishes no ladder, no mean, no distribution
    and no count of anything a person analyses.
    """
    rows = _flagged_rows()
    document = _document(tmp_path, "flagged", rows)
    block = document["columns"][0]
    assert block["role"] == "affixed_number", block["role"]
    # THE WRAPPERS, all three of them, with the counts the column has.
    worn = [(block["affix_prefix"], block["affix_suffix"])] + [
        (one["prefix"], one["suffix"]) for one in block["affix_variants"]
    ]
    assert sorted(worn) == [("", ""), ("", " H"), ("", " L")], worn
    counted = {
        "": len([one for one in rows if not one.endswith(("H", "L"))]),
        " H": len([one for one in rows if one.endswith("H")]),
        " L": len([one for one in rows if one.endswith("L")]),
    }
    published = {
        one["suffix"]: one["count"] for one in block["affix_variants"]
    }
    published[block["affix_suffix"]] = block["n_affixed"] - sum(
        one["count"] for one in block["affix_variants"]
    )
    assert published == counted, (published, counted)
    # ...and the quantity itself, which is the whole point.
    assert block["percentiles"]["min"] == min(
        float(one.replace(" H", "").replace(" L", "")) for one in rows
    )
    assert block["n_core_numeric"] == 200, block["n_core_numeric"]


def test_a_column_whose_commonest_wrapper_is_BARE_describes_and_loads(
    tmp_path: pathlib.Path,
) -> None:
    """`profile` may not write a file `generate` refuses (amendment A-P3-11).

    THE SHAPE THE WRAPPER SET WAS WIDENED FOR HITS THIS ON ITS FIRST
    RUN. Most laboratory results carry no abnormal flag, so on a column
    of readings beside ` H` and ` L` the wrapper worn by MOST cells is
    no text at all -- and the bare wrapper became a member of the
    vocabulary in this landing. The sentence every column of this role
    carries had three shapes, all of them written when a pair could not
    be empty, so it rendered `written as a number followed by ''`; the
    loader holds the same three shapes and cannot import the module
    that renders them, so it refused the sentence its own producer had
    just written. `synthtwin profile` exited 0 and wrote both files,
    and `synthtwin generate` would not take them.
    """
    draw = random.Random(41)
    cores = [f"{round(draw.uniform(8, 18), 1)}" for _index in range(200)]
    values = [
        f"{core}{wrapper}"
        for core, wrapper in zip(
            cores, [""] * 100 + [" H"] * 50 + [" L"] * 50
        )
    ]
    document = _document(tmp_path, "unflagged-mostly", values)
    block = document["columns"][0]
    assert block["role"] == "affixed_number", block["role"]
    # THE COMMONEST WRAPPER IS THE BARE ONE, which is the premise.
    assert block["affix_prefix"] == "", block["affix_prefix"]
    assert block["affix_suffix"] == "", block["affix_suffix"]
    assert sorted(
        (one["suffix"], one["count"]) for one in block["affix_variants"]
    ) == [(" H", 50), (" L", 50)], block["affix_variants"]
    # ...and the document its own loader takes, which is the obligation.
    loaded = _loaded(tmp_path, document, "unflagged-mostly")
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.AffixedFacts)
    assert facts.n_affixed == 200
    # THE SENTENCE SAYS SOMETHING TRUE OF THE COLUMN, and not that its
    # cells are followed by nothing.
    said = document["columns"][0]["remarks"][0]
    assert "followed by ''" not in said, said
    assert "with others wearing text beside it" in said, said


def _flagged(draw: "random.Random", flag: str) -> "list[str]":
    """A laboratory column whose flags are written with `flag` before them.

    `flag` is `""` for the flush spelling -- `13.5H` -- and `" "` for
    the spaced one -- `13.5 H`. Everything else about the column is the
    same, which is the point of the test below.
    """
    return (
        [f"{round(draw.uniform(9, 11), 1)}" for _index in range(120)]
        + [f"{round(draw.uniform(13, 15), 1)}{flag}H" for _index in range(60)]
        + [f"{round(draw.uniform(4, 5), 1)}{flag}L" for _index in range(60)]
    )


def test_a_flush_flag_needs_the_person_to_say_it_is_a_measurement(
    tmp_path: pathlib.Path,
) -> None:
    """ROUNDS 1, 2 AND 3 — where the flush spelling settled.

    `13.5H` is an abnormal flag on a laboratory result. `1234F` is a
    category of procedure code. Nothing in the text tells them apart,
    and this landing wrote two automatic rules that tried:

    * refusing a flush letter outright sent every laboratory column
      whose flags are written flush to free text — no ladder, no mean,
      no distribution — which is the shape this role was widened for;
    * admitting it where the cores are not all of ONE WIDTH refused an
      ordinary column of two-digit readings, and admitted a register
      whose bare codes had lost their leading zeros to a spreadsheet.

    So the question goes to whoever holds the table. Undeclared, the
    column is read as it was before this landing; declared, its
    wrappers are read like any other — and a flag that STANDS APART
    needs no declaration at all, because a code register does not put a
    space before its category letter.
    """
    for seed in range(6):
        folder = tmp_path / f"draw{seed}"
        folder.mkdir(parents=True, exist_ok=True)
        table = fixtures.write(
            folder,
            "v.csv",
            fixtures.single_column_table("v", _flagged(random.Random(seed), "")),
        )
        read = reading.read_table(f"{table}")
        plain = profile.build_document(read, taxonomy.Settings(), [])
        # UNDECLARED IT IS NOT THIS ROLE. Which role it IS depends on
        # the draw -- free text on most, a long tail on some -- and
        # that is the reading it had before this landing; what this
        # pins is that no wrapper is published and no distribution is
        # taken over cores nobody has said are measurements.
        assert plain["columns"][0]["role"] != "affixed_number", (
            seed, plain["columns"][0]["role"]
        )
        declared = profile.build_document(
            read, taxonomy.Settings(), [], forced_measurements=["v"]
        )
        spaced_table = fixtures.write(
            folder,
            "spaced.csv",
            fixtures.single_column_table("v", _flagged(random.Random(seed), " ")),
        )
        spaced = profile.build_document(
            reading.read_table(f"{spaced_table}"),
            taxonomy.Settings(),
            [],
            forced_measurements=["v"],
        )
        # DECLARED, THE FLUSH SPELLING READS LIKE THE SPACED ONE, which
        # is the whole of what the declaration buys. Both are compared
        # DECLARED: the declaration answers two questions at once on
        # this shape -- whether a flush letter is a unit, and which of
        # two rules reads a column both can read (amendment A-P4-58) --
        # so an undeclared column on either side is answering neither.
        assert declared["columns"][0]["role"] == spaced["columns"][0]["role"], (
            seed,
            declared["columns"][0]["role"],
            spaced["columns"][0]["role"],
        )
        assert declared["columns"][0]["role"] == "affixed_number", seed


def test_every_wrapper_owes_its_own_records_on_the_twin_report(
    tmp_path: pathlib.Path,
) -> None:
    """REVIEW ROUND 3, ITEM 3. The report covered one wrapper of two.

    Generation builds each wrapper's cells from that wrapper's own
    layout and then threw the layouts away: the post-write recount
    split the written cells on the COMMONEST pair alone and reported
    the primary block only. A hundred kilograms beside a hundred pounds
    produced thirteen records, all of them the kilograms' — so every
    approximated fact of the pound block, which is approximated by
    construction, was on no page at all.
    """
    draw = random.Random(5)
    weights = [
        f"{60 + draw.random() * 9.9:.1f} kg" for _index in range(100)
    ] + [f"{132 + draw.random() * 9.9:.1f} lb" for _index in range(100)]
    loaded = _loaded(
        tmp_path, _document(tmp_path, "weight", weights), "weight"
    )
    twin = generation.generate(loaded, 5)
    named = [record.fact for record in twin.approximations]
    primary = [one for one in named if not one.startswith("affix_variants")]
    variant = [one for one in named if one.startswith("affix_variants")]
    assert primary, named
    # EACH WRAPPER OWES THE SAME FACTS, because each is a numeric block
    # of the same kind measured by the same code.
    assert len(variant) == len(primary), (len(primary), len(variant))
    # THE BLOCK'S OWN FIELDS TAKE `numbers.`; the two counts of
    # different cores sit BESIDE the block and take the wrapper's own
    # path (review round 4, item 4). A record naming
    # `affix_variants[0].numbers.n_distinct` named a field of neither.
    for one in variant:
        assert one.startswith("affix_variants[0]."), one
        if "n_core_distinct" in one:
            assert ".numbers." not in one, one
        else:
            assert ".numbers." in one, one


def test_a_flagged_column_is_read_by_one_of_TWO_rules(
    tmp_path: pathlib.Path,
) -> None:
    """RESIDUAL R-P4-157, recorded rather than guessed at.

    A column of readings beside spaced `H` and `L` flags satisfies the
    compound rule and the affix rule BOTH, and which it reaches depends
    on the values drawn: `affixed_number` on most and
    `numbers_with_labels` on the rest. The affix reading is the better
    of the two — under the compound one each flagged reading becomes a
    label LEVEL, so its number leaves the distribution and a level
    below the floor is suppressed on top.

    REVIEW ROUND 3 ASKED THE COMPOUND RULE TO STAND ASIDE and round 4
    measured what that cost: 280 numbers beside fifteen `Stage 1` and
    five `Stage 2` cells became an affixed column wearing the wrapper
    `Stage `, so a vocabulary of two labels was described as a quantity
    and the twin's counts moved from 15 and 5 to 16 and 4. A label
    whose spelling ends in a figure is not a number wearing a unit, and
    no rule written over the TEXT has told the two apart — each attempt
    has been measured wrong in the other direction.

    So this pins the tie itself: BOTH readings, and no third.
    """
    reached = set()
    for seed in range(12):
        reached.add(
            _document(
                tmp_path / f"d{seed}", "v", _flagged(random.Random(seed), " ")
            )["columns"][0]["role"]
        )
    assert reached <= {"affixed_number", "numbers_with_labels"}, sorted(reached)
    # ...AND A LABEL WHOSE SPELLING ENDS IN A FIGURE IS STILL A LABEL,
    # which is what the withdrawn condition took away.
    draw = random.Random(4)
    staged = (
        [f"{draw.randint(1, 500)}" for _index in range(280)]
        + ["Stage 1"] * 15
        + ["Stage 2"] * 5
    )
    block = _document(tmp_path / "staged", "stage", staged)["columns"][0]
    assert block["role"] != "affixed_number", block["role"]


def test_an_ambiguous_column_is_ASKED_about_and_not_guessed_at(
    tmp_path: pathlib.Path,
) -> None:
    """AMENDMENT A-P4-58, the owner's ruling of 2026-09-09.

    "It's better to ask the user than make wrong guesses. If there is a
    chance of wrong guess, it's better to ask the user for
    clarification. That is my decision!!!!"

    A column of readings beside `H` and `L` flags satisfies the
    compound rule and the affix rule both. Three rules were written
    over the TEXT to separate them and all three were measured wrong --
    the last turned `Stage 1` and `Stage 2` labels into a quantity --
    so the values do not carry the answer and the person is asked.

    WHERE BOTH READINGS FIT, THE CAUTIOUS ONE IS TAKEN and the column
    says what was not settled. The two errors are not the same size:
    read as labels, a measurement column publishes fewer numbers than
    it holds and every number it publishes is true; read as
    measurements, a label column publishes a mean of stage numbers,
    which is a quantity that does not exist.
    """
    asked = 0
    both = 0
    for seed in range(12):
        folder = tmp_path / f"ask{seed}"
        folder.mkdir(parents=True, exist_ok=True)
        table = fixtures.write(
            folder,
            "v.csv",
            fixtures.single_column_table("v", _flagged(random.Random(seed), " ")),
        )
        read = reading.read_table(f"{table}")
        plain = profile.build_document(read, taxonomy.Settings(), [])
        column = plain["columns"][0]
        carried = [
            remark
            for remark in column["remarks"]
            if "cannot tell from the values alone" in remark
        ]
        if column["role"] == "numbers_with_labels":
            both = both + 1
            # THE CAUTIOUS READING CARRIES THE QUESTION, every time.
            assert carried, (seed, column["remarks"])
            assert "--measurement" in carried[0], carried[0]
            asked = asked + 1
        # ...AND THE PERSON'S ANSWER SETTLES IT.
        answered = profile.build_document(
            read, taxonomy.Settings(), [], forced_measurements=["v"]
        )
        assert answered["columns"][0]["role"] == "affixed_number", seed
    assert both and asked == both, (both, asked)


def test_the_compound_role_keeps_the_column_it_was_written_for(
    tmp_path: pathlib.Path,
) -> None:
    """...and standing aside costs the compound role nothing (item 1).

    Its own motivating shape — readings beside `<0.5` and
    `NOT DETECTED` — has no affix reading at all, because `NOT
    DETECTED` holds no number for a wrapper to sit around. So the
    condition never fires on it and the column is compound exactly as
    it was. What moves is only the column BOTH rules can read.
    """
    draw = random.Random(3)
    values = (
        [f"{draw.uniform(1, 9):.2f}" for _index in range(280)]
        + ["<0.5"] * 10
        + ["NOT DETECTED"] * 10
    )
    block = _document(tmp_path / "compound", "assay", values)["columns"][0]
    assert block["role"] == "numbers_with_labels", block["role"]


def test_a_letter_in_FRONT_of_the_digits_is_still_refused(
    tmp_path: pathlib.Path,
) -> None:
    """...and the guard keeps the half that is worth keeping (item 6).

    A code scheme puts its letter in front. Relaxing the back of the
    number must not relax the front, or a column of `E10.0`, `I11.2`
    and `J44.9` is read as a quantity, publishes a ladder over its code
    numbers, and its twin writes codes nobody ever issued.
    """
    letters = ("E", "I", "J", "N", "K", "R")
    codes = [
        f"{letters[index % len(letters)]}{10 + index % 80}."
        f"{index % 10}"
        for index in range(240)
    ]
    reached = _document(tmp_path / "codes", "dx", codes)["columns"][0]["role"]
    assert reached != "affixed_number", reached


def test_a_mixed_procedure_code_column_is_not_a_quantity(
    tmp_path: pathlib.Path,
) -> None:
    """REVIEW ROUND 2, ITEM 4. A code register is not a measurement.

    Letting a flag be written flush behind the digits — which is what a
    laboratory column needs — admitted a shape that is not a
    measurement at all. A mixed register of procedure codes holds one category as
    five digits, a second as four digits and an `F`, and a third as
    four digits and a `T`; eighty of each reached this role with `F`
    and `T` as wrappers and a distribution published over the bare
    codes, whose twin would then write codes nobody issued.

    WHAT SEPARATES THEM IS THE CORES. A code register is written at a
    FIXED WIDTH with no point; a measurement is not — a haemoglobin
    carries a point, and an integer one runs across widths.
    """
    draw = random.Random(2)
    codes = (
        [f"{draw.randint(10000, 99999)}" for _index in range(80)]
        + [f"{draw.randint(1000, 9999)}F" for _index in range(80)]
        + [f"{draw.randint(1000, 9999)}T" for _index in range(80)]
    )
    reached = _document(tmp_path / "register", "code", codes)["columns"][0]["role"]
    assert reached != "affixed_number", reached
    # ...AND SO IS AN ORDINARY LABORATORY COLUMN WEARING THE SAME
    # SHAPE, undeclared, which is the price and is stated rather than
    # hidden: nothing in the text tells the two apart, so the safe
    # reading is the one that publishes no distribution, and the
    # person who knows which it is says so.
    again = random.Random(2)
    readings = (
        [f"{again.randint(70, 140)}" for _index in range(80)]
        + [f"{again.randint(141, 200)}H" for _index in range(80)]
        + [f"{again.randint(5, 69)}L" for _index in range(80)]
    )
    block = _document(tmp_path / "int", "bp", readings)["columns"][0]
    assert block["role"] != "affixed_number", block["role"]


def test_the_measurement_declaration_reaches_flush_units(
    tmp_path: pathlib.Path,
) -> None:
    """REVIEW ROUND 2, ITEM 5. The person may say these are measurements.

    A column of `60.0kg` beside `132.0lb` holds no bare cell, so the
    code-risk rule refused it — and the per-wrapper machinery written
    FOR mixed scales was out of reach of the very shape that motivated
    it. `--measurement` is this project's own answer to "these are
    measurements, not codes", and it is the answer here.

    Undeclared the column stays free text, which is what it was before
    this landing, so nothing anybody had is lost either way.
    """
    draw = random.Random(5)
    weights = [
        f"{60 + draw.random() * 9.9:.1f}kg" for _index in range(100)
    ] + [f"{132 + draw.random() * 9.9:.1f}lb" for _index in range(100)]
    folder = tmp_path / "flushunits"
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(
        folder, "w.csv", fixtures.single_column_table("w", weights)
    )
    read = reading.read_table(f"{table}")
    plain = profile.build_document(read, taxonomy.Settings(), [])
    assert plain["columns"][0]["role"] == "free_text", (
        plain["columns"][0]["role"]
    )
    declared = profile.build_document(
        read, taxonomy.Settings(), [], forced_measurements=["w"]
    )
    block = declared["columns"][0]
    assert block["role"] == "affixed_number", block["role"]
    assert len(block["affix_variants"]) == 1, block["affix_variants"]
    # ...and each unit keeps its own numbers, which is the point.
    assert block["percentiles"]["max"] < 100.0
    assert block["affix_variants"][0]["numbers"]["percentiles"]["min"] > 100.0


def test_a_wrapper_is_measured_against_its_OWN_spelling(
    tmp_path: pathlib.Path,
) -> None:
    """REVIEW ROUND 7, ITEM 1. The file's commonest wrapper need not be ours.

    Both sides publish their own commonest wrapper at the block's root
    and every other beside it, so a file whose dominance is FLIPPED
    puts the description's commonest wrapper among its own variants. A
    description of 120 kilograms and 80 pounds, checked against a file
    of 120 pounds and 80 kilograms whose kilograms are ten times
    heavier, compared the kilogram facts against the POUND block --
    because that is what the root held -- and reported them HELD, while
    the pound facts came back WITHHELD because nothing looked at the
    root for them. Both answers were about the wrong population and
    neither said so.

    A wrapper is found by its SPELLING across both shapes now.
    """
    draw = random.Random(11)
    described = _loaded(
        tmp_path,
        _document(
            tmp_path,
            "weight",
            [f"{28 + draw.random() * 5:.2f} kg" for _index in range(120)]
            + [f"{128 + draw.random() * 5:.2f} lb" for _index in range(80)],
        ),
        "weight",
    )
    block = described.columns[0].facts
    assert isinstance(block, contract.AffixedFacts)
    assert block.affix_suffix == " kg", block.affix_suffix
    again = random.Random(11)
    flipped = fixtures.write(
        tmp_path,
        "flipped.csv",
        fixtures.single_column_table(
            "weight",
            [f"{28 + again.random() * 5:.2f} lb" for _index in range(120)]
            + [f"{298 + again.random() * 5:.2f} kg" for _index in range(80)],
        ),
    )
    outcome = validation.measure(described, f"{flipped}")
    missed = [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    ]
    # THE KILOGRAM ENDS ARE COMPARED AGAINST KILOGRAMS, which in that
    # file run near 300, so they miss rather than holding.
    assert "ladder.min" in missed, missed[:10]
    assert "ladder.max" in missed, missed[:10]


def test_a_wrapper_whose_numbers_are_wrong_is_caught(
    tmp_path: pathlib.Path,
) -> None:
    """REVIEW ROUND 2, ITEM 1. Each wrapper's block was published and unread.

    Plan P4-D37 gave every published wrapper a quantitative block of its
    own, and the validator measured NONE of them. A description of a
    hundred weights in kilograms beside a hundred in pounds, checked
    against a file whose pounds are a hundred higher and whose
    kilograms, wrappers and counts are identical, reported zero
    obligations MISSED: the only wrapper-shaped check compared the
    set's spellings and counts, which that file meets exactly.

    Every fact a wrapper's block carries is now measured over that
    wrapper's own cores and named for that wrapper, so a report says
    WHICH one moved.
    """
    draw = random.Random(5)
    kilograms = [
        f"{60 + draw.random() * 9.9:.1f} kg" for _index in range(100)
    ]
    pounds = [
        f"{132 + draw.random() * 9.9:.1f} lb" for _index in range(100)
    ]
    described = _loaded(
        tmp_path, _document(tmp_path, "weight", kilograms + pounds), "weight"
    )
    again = random.Random(5)
    shifted = [
        f"{60 + again.random() * 9.9:.1f} kg" for _index in range(100)
    ] + [f"{232 + again.random() * 9.9:.1f} lb" for _index in range(100)]
    other = fixtures.write(
        tmp_path,
        "shifted.csv",
        fixtures.single_column_table("weight", shifted),
    )
    outcome = validation.measure(described, f"{other}")
    missed = [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    ]
    assert missed, "a file whose pounds are a hundred higher misses nothing"
    # ...AND EVERY MISS NAMES THE WRAPPER IT BELONGS TO.
    for subcheck in missed:
        assert subcheck.startswith("affix_variants[0]."), subcheck
    assert "affix_variants[0].ladder.min" in missed, missed


def _wearing_a_set(folder: pathlib.Path, stem: str) -> "dict[str, object]":
    """A document for a column wearing three wrappers, to be forged."""
    return _document(folder, stem, _flagged_rows())


def test_the_producer_never_writes_a_set_its_own_loader_refuses(
    tmp_path: pathlib.Path,
) -> None:
    """AF17 against the producer, on review round 5's own column (item 1).

    The commonest wrapper was chosen from what PROPOSED it — the cells
    that read as a NUMBER wearing it — while AF17 checks what WEARS it,
    cores that are no number included. A hundred distinct ` kg`
    numerals beside ninety-eight ` aa` numerals and two `many aa` cells
    proposes ` kg` and wears both a hundred times, so the loader's tie
    rule wants ` aa`: `synthtwin profile` exited 0 and wrote a file
    `synthtwin generate` would not take, which is the defect amendment
    A-P3-11 exists to keep closed.
    """
    draw = random.Random(3)
    values = (
        [
            f"{draw.randint(1, 999)}.{draw.randint(0, 9)} kg"
            for _index in range(100)
        ]
        + [
            f"{draw.randint(1, 999)}.{draw.randint(0, 9)} aa"
            for _index in range(98)
        ]
        + ["many aa"] * 2
    )
    document = _document(tmp_path / "tie", "v", values)
    block = document["columns"][0]
    assert block["role"] == "affixed_number", block["role"]
    # THE TIE GOES THE LOADER'S WAY: equal wear, and ` aa` sorts first.
    assert block["affix_suffix"] == " aa", block["affix_suffix"]
    # ...and the document its own loader takes, which is the obligation.
    loaded = _loaded(tmp_path / "tie", document, "tie")
    assert isinstance(loaded.columns[0].facts, contract.AffixedFacts)


def test_a_wrapper_named_twice_across_the_vocabulary_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """AF14, on review round 1's own document (item 8).

    AF9 orders the variants and so refuses a duplicate AMONG them; the
    commonest pair is read somewhere else entirely, so a variant
    repeating the pair the block already names passed both checks. Two
    entries for one wrapper are two counts of one thing, and the count
    of cells wearing the commonest is then the column's total less a
    slice of itself.
    """
    document = _wearing_a_set(tmp_path / "af14", "flagged")
    column = document["columns"][0]
    twin = dict(column["affix_variants"][0])
    twin["prefix"] = column["affix_prefix"]
    twin["suffix"] = column["affix_suffix"]
    column["affix_variants"] = sorted(
        column["affix_variants"] + [twin],
        key=lambda one: (one["prefix"], one["suffix"]),
    )
    with pytest.raises(errors.ProfileError) as raised:
        _loaded(tmp_path / "af14", document, "forged")
    assert "named twice" in f"{raised.value}", f"{raised.value}"


def test_more_wrappers_than_a_set_of_categories_may_hold_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """AF15: the wrappers are published text and something must bound them.

    A wrapper is a spelling taken from the table and printed in the
    description, so what bounds how many may be named is what bounds
    how many levels a categorical column may name. Without it a column
    of one-off units published a spelling per cell under a key nothing
    bounded.
    """
    document = _wearing_a_set(tmp_path / "af15", "flagged")
    column = document["columns"][0]
    many = []
    for index in range(60):
        many = many + [
            {
                "prefix": "",
                "suffix": f" x{index:02d}",
                "count": column["affix_variants"][0]["count"],
                "n_core_numeric": column["affix_variants"][0][
                    "n_core_numeric"
                ],
                "n_core_out_of_range": 0,
                "n_core_contradictory": 0,
                "n_core_not_numeric": 0,
                "n_core_distinct": column["affix_variants"][0][
                    "n_core_distinct"
                ],
                "n_core_distinct_folded": column["affix_variants"][0][
                    "n_core_distinct_folded"
                ],
                "numbers": column["affix_variants"][0]["numbers"],
            }
        ]
    column["affix_variants"] = many
    with pytest.raises(errors.ProfileError) as raised:
        _loaded(tmp_path / "af15", document, "forged")
    said = f"{raised.value}"
    assert "wrappers" in said, said


def test_more_different_cores_than_the_commonest_wrapper_has_cells(
    tmp_path: pathlib.Path,
) -> None:
    """AF10, rebounded by plan P4-D37 (review round 1, item 8).

    The two counts of different cores belong to the block above them,
    and that block is the COMMONEST wrapper's. Bounded by `n_affixed`
    they let a description say a wrapper worn by sixty cells holds two
    hundred different cores -- a budget the core stage would then be
    laid out from.
    """
    document = _wearing_a_set(tmp_path / "af10", "flagged")
    column = document["columns"][0]
    worn_elsewhere = sum(
        one["count"] for one in column["affix_variants"]
    )
    column["n_core_distinct"] = column["n_affixed"] - worn_elsewhere + 1
    column["n_core_distinct_folded"] = column["n_core_distinct"]
    with pytest.raises(errors.ProfileError) as raised:
        _loaded(tmp_path / "af10", document, "forged")
    assert "n_core_distinct" in f"{raised.value}", f"{raised.value}"


def test_a_block_holding_no_different_core_at_all_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """AF10's other end: a published zero is a description no column wrote.

    A block whose numbers a file is held to describes at least one
    core. The bound was zero, and a document saying a column holds no
    different cores at all loaded and was generated from.
    """
    document = _wearing_a_set(tmp_path / "af10b", "flagged")
    column = document["columns"][0]
    column["n_core_distinct"] = 0
    column["n_core_distinct_folded"] = 0
    with pytest.raises(errors.ProfileError) as raised:
        _loaded(tmp_path / "af10b", document, "forged")
    assert "n_core_distinct" in f"{raised.value}", f"{raised.value}"


def test_two_units_are_never_averaged_into_one_number(
    tmp_path: pathlib.Path,
) -> None:
    """THE WITNESS FOR P4-D37, and it is a number that should not exist.

    A hundred weights written `60.0 kg` to `69.9 kg` beside a hundred
    written `132.3 lb` to `153.8 lb` reached this role and published
    ONE ladder over every core it held: **mean 104.722**, an average of
    no quantity, with the column's ends running from 60 to 153.8. A
    person reading that column's average read a number their table does
    not hold, and code converting units against it was wrong in both
    directions.

    Every published wrapper carries its own numbers now, so what the
    description states about kilograms is stated over kilograms.
    """
    draw = random.Random(5)
    kilograms = [
        f"{60 + draw.random() * 9.9:.1f} kg" for _index in range(100)
    ]
    pounds = [
        f"{132 + draw.random() * 21.8:.1f} lb" for _index in range(100)
    ]
    block = _document(tmp_path, "weight", kilograms + pounds)["columns"][0]
    assert block["role"] == "affixed_number", block["role"]
    # THE COLUMN'S OWN BLOCK IS THE COMMONEST WRAPPER'S, so its ends
    # are that wrapper's ends and not the two ranges laid end to end.
    assert block["affix_suffix"] == " kg", block["affix_suffix"]
    assert block["percentiles"]["min"] >= 60.0
    assert block["percentiles"]["max"] <= 70.0
    assert 60.0 <= block["mean"] <= 70.0, block["mean"]
    # ...and the pounds are described as pounds, beside their wrapper.
    assert len(block["affix_variants"]) == 1, block["affix_variants"]
    other = block["affix_variants"][0]
    assert other["suffix"] == " lb", other["suffix"]
    assert other["count"] == 100, other["count"]
    assert other["numbers"]["percentiles"]["min"] >= 132.0
    assert other["numbers"]["percentiles"]["max"] <= 154.0
    assert 132.0 <= other["numbers"]["mean"] <= 154.0, other["numbers"]["mean"]
    # NO POOLED NUMBER SURVIVES ANYWHERE IN THE BLOCK: nothing in this
    # column's description sits between the two ranges, which is where
    # the average of the two used to be.
    assert not 100.0 <= block["mean"] <= 110.0


def test_the_twin_writes_each_wrapper_from_its_own_numbers(
    tmp_path: pathlib.Path,
) -> None:
    """A flag lands on the values that carried it (plan P4-D37).

    Nothing in the description said WHICH cores wore which wrapper, so
    a twin meeting the published counts handed ` H` to a low reading
    and ` L` to a high one -- and a person filtering the twin on its
    abnormal flag met a population their own table does not hold. Each
    wrapper's cells are drawn from that wrapper's own ladder now, so
    the tie is made by construction rather than arranged afterwards.
    """
    draw = random.Random(41)
    values = (
        [f"{round(draw.uniform(9, 11), 1)}" for _index in range(120)]
        + [f"{round(draw.uniform(13, 15), 1)} H" for _index in range(60)]
        + [f"{round(draw.uniform(4, 5), 1)} L" for _index in range(60)]
    )
    loaded = _loaded(
        tmp_path, _document(tmp_path, "hgb", values), "hgb"
    )
    for seed in (0, 3, 11):
        twin = generation.generate(loaded, seed)
        cells = [row[0] for row in twin.rows]
        high: "list[float]" = []
        low: "list[float]" = []
        bare: "list[float]" = []
        for cell in cells:
            if cell.endswith(" H"):
                high = high + [float(cell[:-2])]
            elif cell.endswith(" L"):
                low = low + [float(cell[:-2])]
            else:
                bare = bare + [float(cell)]
        assert len(high) == 60 and len(low) == 60 and len(bare) == 120
        # THE FLAGGED VALUES ARE WHERE THEIR FLAG SAYS, at every seed.
        assert min(high) >= 12.5, (seed, min(high))
        assert max(low) <= 5.5, (seed, max(low))
        assert 8.5 <= min(bare) and max(bare) <= 11.5, (seed, min(bare), max(bare))


def test_a_file_wearing_the_wrappers_in_OTHER_numbers_misses(
    tmp_path: pathlib.Path,
) -> None:
    """The wrapper set is an EXACT obligation, so its counts are checked.

    REVIEW ROUND 1 OF THIS LANDING, ITEM 2. The validator compared how
    MANY other wrappers the checked file wears and nothing else, while
    the sentence beside it said each wrapper's two sides were settled
    the way the commonest pair's are. A description publishing a
    hundred bare readings, fifty ` H` and fifty ` L`, checked against a
    file holding a hundred bare, EIGHTY ` H` and TWENTY ` L` -- the
    same numbers, the same cores, two other wrappers on both sides --
    was reported HELD, and a person filtering that file on its flag met
    a population the description does not describe.
    """
    draw = random.Random(23)
    cores = [f"{round(draw.uniform(8, 18), 1)}" for _index in range(200)]
    described = _loaded(
        tmp_path,
        _document(
            tmp_path,
            "flags-fifty",
            [
                f"{core}{wrapper}"
                for core, wrapper in zip(
                    cores, [""] * 100 + [" H"] * 50 + [" L"] * 50
                )
            ],
        ),
        "flags-fifty",
    )
    other = fixtures.write(
        tmp_path,
        "flags-eighty.csv",
        fixtures.single_column_table(
            "flags-fifty",
            [
                f"{core}{wrapper}"
                for core, wrapper in zip(
                    cores, [""] * 100 + [" H"] * 80 + [" L"] * 20
                )
            ],
        ),
    )
    outcome = validation.measure(described, f"{other}")
    # THE SET LINE COVERS MEMBERSHIP AND SPELLINGS; each wrapper's
    # COUNT is a published fact with a check of its own (round 4, item
    # 6). This file wears the right wrappers in the wrong numbers, so
    # the set holds and the counts miss.
    settled = [
        check
        for check in outcome.checks
        if check.subcheck == "counts.affix_variants"
    ]
    assert len(settled) == 1, settled
    assert settled[0].verdict == validation.HELD, settled[0]
    assert settled[0].achieved == ""
    counts = [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
        and check.subcheck.endswith(".count")
    ]
    assert counts, [
        (one.subcheck, one.verdict)
        for one in outcome.checks
        if one.verdict == validation.MISSED
    ]


def test_the_twin_wears_the_wrappers_in_their_published_numbers(
    tmp_path: pathlib.Path,
) -> None:
    """Every wrapper's count is met, and the values are still values."""
    rows = _flagged_rows()
    document = _document(tmp_path, "flagged-twin", rows)
    loaded = _loaded(tmp_path, document, "flagged-twin")
    for seed in (0, 3, 11, 29):
        twin = generation.generate(loaded, seed)
        cells = [row[0] for row in twin.rows]
        for suffix in (" H", " L"):
            assert len(
                [one for one in cells if one.endswith(suffix)]
            ) == len(
                [one for one in rows if one.endswith(suffix.strip())]
            ), (seed, suffix)
        # ...and the space between the number and its flag is THERE.
        # It was not: the split put the space in the CORE, the value
        # stage rewrote the core as a number, and `14.2 g/dL` came back
        # `12.7g/dL` on every column of this role.
        for one in cells:
            if one.endswith(("H", "L")):
                assert one[-2] == " ", one
        # ...and every cell still reads as a number under its wrapper.
        for one in cells:
            core = one
            for suffix in (" H", " L"):
                if core.endswith(suffix):
                    core = core[: -len(suffix)]
            assert parsing.parse_number(core) is not None, one


def test_the_space_before_a_unit_survives_the_twin(
    tmp_path: pathlib.Path,
) -> None:
    """A ONE-wrapper column too, which is where this was wrong first.

    `affixed_split` takes the longest span that reads as a number and
    `classify_number` trims its own argument, so `14.2 g/dL` split into
    a core of `14.2 ` and a suffix of `g/dL`. The value stage rewrites
    a core as a NUMBER and has no space to write, so every cell of
    every column of this role lost the space before its unit.
    """
    draw = random.Random(5)
    rows = [f"{round(draw.uniform(8, 18), 1)} g/dL" for _index in range(200)]
    document = _document(tmp_path, "spaced", rows)
    block = document["columns"][0]
    assert block["affix_suffix"] == " g/dL", block["affix_suffix"]
    loaded = _loaded(tmp_path, document, "spaced")
    cells = [row[0] for row in generation.generate(loaded, 3).rows]
    for one in cells:
        assert one.endswith(" g/dL"), one


def test_a_set_of_wrappers_that_differ_by_digits_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """The guard against a split that cut through a number.

    A column of feet and inches, `4'5"`, `5'11"` proposes one wrapper per inches
    value -- prefix nothing, suffix `'5"` -- and a dozen of them clear
    the floor and the ceiling together. The column then published a
    ladder over the FEET of some cells and the inches of others: a
    description saying something false, where before it said nothing.

    A wrapper worn by ONE column may carry digits -- `mL/min/1.73m2` is
    a real unit -- so the guard is asked only of a SET.
    """
    draw = random.Random(3)
    rows = [
        f"{draw.randint(4, 6)}'{draw.randint(0, 11)}\""
        for _index in range(200)
    ]
    document = _document(tmp_path, "feet-and-inches", rows)
    assert document["columns"][0]["role"] != "affixed_number", (
        document["columns"][0]["role"]
    )


def test_a_wrapper_too_rare_to_publish_leaves_stragglers(
    tmp_path: pathlib.Path,
) -> None:
    """A wrapper worn by fewer cells than may be named is not published.

    Its cells are STRAGGLERS -- the population this role already has
    and already writes -- so the set rule needs no held-back pool of
    its own.
    """
    draw = random.Random(7)
    rows = (
        [f"{round(draw.uniform(8, 18), 1)}" for _index in range(120)]
        + [f"{round(draw.uniform(8, 18), 1)} H" for _index in range(78)]
        + ["9.9 CRITICAL", "10.1 CRITICAL"]
    )
    draw.shuffle(rows)
    path = fixtures.write(
        tmp_path, "rare.csv", fixtures.single_column_table("v", rows)
    )
    document = profile.build_document(
        reading.read_table(f"{path}"),
        taxonomy.Settings(small_cell_floor=11),
        [],
    )
    block = document["columns"][0]
    assert block["role"] == "affixed_number", block["role"]
    worn = [(block["affix_prefix"], block["affix_suffix"])] + [
        (one["prefix"], one["suffix"]) for one in block["affix_variants"]
    ]
    assert (" ", "CRITICAL") not in worn and ("", " CRITICAL") not in worn, worn
    assert block["n_affixed"] == 198, block["n_affixed"]
