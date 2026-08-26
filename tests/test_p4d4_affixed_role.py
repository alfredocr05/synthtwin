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
    assert column["n_affixed"] == 60
    assert document["settings"]["minimum_parse_rate"] == 0.5
    loaded = _loaded(folder, document, "lowered")
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.AffixedFacts)
    assert facts.n_affixed == 60


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
    """The reviewer's scenario, from the CSV to the sentence.

    Ninety-eight cells wearing one pair and two wearing another: no pair
    clears the line, the column declines, and its owner is owed the
    count the closest reading reached. Before this, the remark named the
    numeric, date and categorical readings and said nothing at all about
    the one that came within two cells.
    """
    values = [f"${index}" for index in range(1, 99)]
    values = values + ["EUR99", "EUR100"]
    document = _document(tmp_path / "two-pairs", "price", values)
    column = document["columns"][0]
    assert column["role"] == "free_text"
    said = " ".join(column["remarks"])
    assert "98 of its values are numbers wearing one shared piece of text" in (
        said
    ), said
    assert "which is the reading that came closest" in said


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


def test_the_remark_carries_seven_arguments_and_the_grammar_says_so(
    tmp_path: pathlib.Path,
) -> None:
    """The arity is the contract's, and the note grammar is where it lives.

    A form whose rendering names two more things than its arity admits
    is a form the publication guard cannot check, so the count is
    asserted against the shipped grammar rather than against the
    sentence.
    """
    assert taxonomy.NOTE_ARITY[taxonomy.REMARK_NO_READING_FITS] == 7


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
    pair = [
        check
        for check in outcome.checks
        if check.subcheck.startswith("counts.affix")
    ]
    assert len(pair) == 2
    for check in pair:
        assert check.verdict == validation.MISSED
        assert check.achieved == ""


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
    theirs = fixtures.write(
        folder,
        "theirs.csv",
        fixtures.single_column_table(
            "note",
            [f"Alice Brown note {index}" for index in range(1, 56)]
            + [f"Chen Wu note {index}.5" for index in range(1, 6)],
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
