"""`n_declared` counts declarations, so the head count stops making words up.

REVIEW ITEM P3-V9-F7; plan amendment A-P3-37; contract 5 C5-18 as
amended; validation method V2.4-A9.

WHAT WENT WRONG. `--missing-value n/a --missing-value " N/A "` names one
value twice. The producer folds the two spellings into ONE declaration
-- they take exactly the same cells of every column -- and writes one
entry in `built_in_texts`. `n_declared` counted the two KEYSTROKES. The
validator subtracts the vocabulary lists from that count to learn how
many words of the PERSON'S own were named, which is the whole reason
those lists exist, so it read one word of their own, found none in the
columns, and moved a FULLY RECONSTRUCTIBLE column's obligations off the
checked census with a printed reason about a word nobody typed.

WHY THE REPAIR IS THE PRODUCER'S AND COULD NOT BE THE VALIDATOR'S. From
the document alone, `n_declared: 2` beside `built_in_texts: ["n/a"]` is
the same document as one written by `--missing-value n/a
--missing-value WOMBAT`. There is nothing on the reading side to reason
from: the count and the list had to be made to answer the same question.

WHAT IS MEASURED HERE, all of it through the real producer:

* the count folds the spellings the producer's own rule folds -- case,
  spacing, and two spellings of one number -- and does not fold two
  values that are genuinely different;
* the folded pair no longer routes a rebuildable column, and every
  obligation of the file that description was written from is checked
  and held;
* the over-fire that REMAINS is asserted at its size, because it is a
  different shape and it does not close: two words of the person's own
  where the table holds one;
* reprofiling the witness under the recovered settings gives identical
  column facts, which is what "reconstructible" means and is what makes
  the retired behaviour a false alarm rather than a cautious one;
* and the count still consults no cell (contract 5 C5-16).

THE RED CHECK. `REINSTATE=P3-V9-F7` counts keystrokes again, exactly as
the producer did, and every assertion that depends on the fold goes red
-- including the one that measures the 43 obligations leaving the census.
"""

import json
import os
import pathlib
import typing

import pytest

import fixtures
from synthtwin import contract, profile, reading, taxonomy, validation


@pytest.fixture(scope="module", autouse=True)
def _reinstated() -> "typing.Iterator[None]":
    """Count keystrokes again when the red check asks for it.

    MODULE-SCOPED, because the descriptions below are built in
    module-scoped fixtures and a function-scoped patch would be applied
    after they were built -- a red check run against a patch nobody
    used.
    """
    monkeypatch = pytest.MonkeyPatch()
    if os.environ.get("REINSTATE") == "P3-V9-F7":
        monkeypatch.setattr(
            taxonomy, "declarations_named", lambda spellings: len(spellings)
        )
    yield
    monkeypatch.undo()


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


class Case(typing.NamedTuple):
    """One description, the table it was written from, and its path."""

    described: contract.Profile
    path: str
    document: dict


def _described(
    folder: pathlib.Path,
    stem: str,
    values: "list[str]",
    settings: taxonomy.Settings,
) -> Case:
    """One table through the real producer, loader and all."""
    path = fixtures.write(
        folder, f"{stem}.csv", fixtures.single_column_table("reading", values)
    )
    table = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(table, settings, [])
    loaded = contract.load_profile(
        str(fixtures.write_profile(folder, f"{stem}-profile.json", document))
    )
    return Case(loaded, str(path), document)


def _unsupported(outcome: validation.Outcome) -> "list[str]":
    """The subchecks one run named as ones this description cannot ask."""
    return sorted(
        {
            listing.subcheck
            for listing in outcome.listings
            if listing.reason.endswith(validation.UNREBUILDABLE_REASON_TAIL)
        }
    )


# -- 1. what the count folds, and what it does not ----------------------


FOLDED = (
    ("case and spacing", ("n/a", " N/A "), 1),
    ("two spellings of one word of your own", ("XX", "xx"), 1),
    ("the same thing typed twice", ("ZZZ", "ZZZ"), 1),
    ("two spellings of one number", ("-999", "-999.00"), 1),
    ("a blank named two ways", ("", "   "), 1),
)

SEPARATE = (
    ("two of this package's own words", ("n/a", "none"), 2),
    ("two words of your own", ("XX", "YY"), 2),
    ("two different numbers", ("-999", "-9999"), 2),
    ("a word and a number", ("XX", "-999"), 2),
)


@pytest.mark.parametrize("what,spellings,expected", FOLDED + SEPARATE)
def test_the_count_folds_what_the_producer_folds(
    what: str, spellings: "tuple[str, ...]", expected: int
) -> None:
    """The rule is the producer's own, not a second one written here.

    Two spellings are one declaration exactly when they take the same
    cells: the exact number where both read as one, else the trimmed and
    case-folded spelling. That is `settings.declaration_matching`'s one
    permitted value, and it is what decided which cells the declaration
    took in the first place.
    """
    assert taxonomy.declarations_named(spellings) == expected, what


def test_the_count_does_not_depend_on_the_order_they_were_typed() -> None:
    """A person who reorders their command line gets the same bytes."""
    one = taxonomy.declarations_named(("n/a", " N/A ", "XX"))
    other = taxonomy.declarations_named((" N/A ", "XX", "n/a"))
    assert one == other == 2


def test_the_count_still_reads_no_cell_of_any_table(
    tmp_path: pathlib.Path,
) -> None:
    """Contract 5 C5-16, which this amendment may not weaken.

    Two tables, one holding the named word in twelve cells and one
    holding it in none, described under the same command line. The
    whole declaration record must come out identical, so the field
    stays evidence about the command line and never about the table.
    """
    settings = taxonomy.Settings(declared_missing_values=("n/a", " N/A "))
    held = _described(tmp_path, "held", _numbers(60) + ["n/a"] * 12, settings)
    never = _described(tmp_path, "never", _numbers(72), settings)
    mine = held.document["settings"]["declared_missing_values"]  # type: ignore[index]
    theirs = never.document["settings"]["declared_missing_values"]  # type: ignore[index]
    assert mine == theirs
    assert json.loads(json.dumps(mine))["n_declared"] == 1


# -- 2. the finding's own witness, measured ------------------------------


@pytest.fixture(scope="module")
def folded_pair(
    tmp_path_factory: pytest.TempPathFactory,
) -> Case:
    """The review's witness: one built-in word named with two spellings."""
    folder = tmp_path_factory.mktemp("folded")
    return _described(
        folder,
        "folded",
        _numbers(60) + ["n/a"] * 12,
        taxonomy.Settings(declared_missing_values=("n/a", " N/A ")),
    )


def test_the_folded_pair_names_one_declaration_and_one_member(
    folded_pair: Case,
) -> None:
    """The two halves of the record now answer the same question."""
    record = folded_pair.described.settings.declared_missing_values
    assert record.built_in_texts == ("n/a",)
    assert record.built_in_numbers == ()
    assert record.n_declared == 1
    # ...so the shortfall the validator subtracts is exactly zero, where
    # it used to be one word of the person's own that nobody typed.
    assert validation._own_words_named(record) == 0


def test_the_folded_pair_leaves_the_column_checked_in_full(
    folded_pair: Case,
) -> None:
    """THE FINDING. A rebuildable column stops being routed away.

    Fifty-three obligations, all of them checked, none missed, against
    the table this description was written from -- where forty-three of
    them used to become listings under a reason about a word of the
    person's own that the command line never held.
    """
    assert validation.unrebuildable_columns(folded_pair.described) == {}
    outcome = validation.measure(
        folded_pair.described, folded_pair.path
    )
    assert _unsupported(outcome) == []
    assert outcome.census.missed == 0
    assert len(outcome.checks) == 53


def test_the_witness_really_is_reconstructible(
    folded_pair: Case, tmp_path: pathlib.Path
) -> None:
    """What "fully reconstructible" means, measured rather than asserted.

    The validator's job is to rebuild the reading rule from the
    description and describe the file again with it. Here that rule is
    recovered exactly -- the settings block names the member -- so
    describing the same table under the RECOVERED settings has to give
    the same column facts as describing it under the original ones. It
    does, which is what makes the retired routing a false alarm and not
    a cautious one.
    """
    recovered = validation.settings_for(folded_pair.described)
    assert recovered.declared_missing_values == ("n/a",)
    again = _described(
        tmp_path,
        "again",
        _numbers(60) + ["n/a"] * 12,
        recovered,
    )
    assert again.document["columns"] == folded_pair.document["columns"]


# -- 3. the over-fire that does NOT close --------------------------------


def test_the_other_over_fire_stays_and_is_a_different_shape(
    tmp_path: pathlib.Path,
) -> None:
    """Two words of the person's own, of which the table holds one.

    This one is not the same defect wearing another face and it does not
    close here. The description says two different words were named and
    carries one; whether the second was ever in a cell is a fact about
    the TABLE, and no count on the command line can settle it. So the
    union fires, in the safe direction, and it is asserted here so that
    a later reader does not mistake this file for a claim that the head
    count no longer over-fires at all.
    """
    case = _described(
        tmp_path,
        "two-words",
        _numbers(60) + ["XX"] * 12,
        taxonomy.Settings(declared_missing_values=("XX", "NEVERHERE")),
    )
    assert case.described.settings.declared_missing_values.n_declared == 2
    assert sorted(validation.unrebuildable_columns(case.described)) == [
        "reading"
    ]
    outcome = validation.measure(case.described, case.path)
    assert outcome.census.missed == 0
    assert len(_unsupported(outcome)) == 43


def test_two_words_of_your_own_spelled_two_ways_each_still_come_back(
    tmp_path: pathlib.Path,
) -> None:
    """The fold reaches the recovered side too, so the two agree.

    `XX` typed as `XX` and ` xx `, and a table wearing both spellings.
    One word named, one word back -- which is the pairing amendment
    A-P3-34 made possible and this amendment completes, since before it
    the named side counted two while the recovered side counted one.
    """
    case = _described(
        tmp_path,
        "both-sides",
        _numbers(60) + ["XX"] * 12 + [" XX "] * 12,
        taxonomy.Settings(declared_missing_values=("XX", " xx ")),
    )
    assert case.described.settings.declared_missing_values.n_declared == 1
    assert validation._own_declarations_recovered(case.described) == 1
    assert validation.unrebuildable_columns(case.described) == {}
    outcome = validation.measure(case.described, case.path)
    assert outcome.census.missed == 0
    assert _unsupported(outcome) == []


# -- 4. the page a person reads -----------------------------------------


def test_the_summary_says_different_values_rather_than_values(
    tmp_path: pathlib.Path,
) -> None:
    """A count that folds has to say it folds, on the page that prints it.

    A person who typed two things and reads "named as 'no value': 1"
    without an explanation is a person who thinks something was lost.
    """
    from synthtwin import summary

    case = _described(
        tmp_path,
        "page",
        _numbers(60) + ["n/a"] * 12,
        taxonomy.Settings(declared_missing_values=("n/a", " N/A ")),
    )
    page = " ".join(summary.render(case.document, "").split())
    assert "named as 'no value': 1" in page
    assert "how many DIFFERENT values you named" in page
    assert "counts once: synthtwin reads those as one value" in page
