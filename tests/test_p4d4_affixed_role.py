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

import pytest

import fixtures
from synthtwin import contract, errors, profile, reading, taxonomy


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
    built = "100 " + " ".join(parts)
    assert contract._is_the_affixed_remark(built, 100)
    assert not contract._is_the_affixed_remark(built, 99)
    for place in range(len(parts)):
        short = "100 " + " ".join(
            parts[index] for index in range(len(parts)) if index != place
        )
        assert not contract._is_the_affixed_remark(short, 100), parts[place]
    backwards = "100 " + " ".join(reversed(parts))
    assert not contract._is_the_affixed_remark(backwards, 100)


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
