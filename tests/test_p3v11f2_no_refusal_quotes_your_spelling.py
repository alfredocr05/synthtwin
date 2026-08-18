"""The ordinary wrong-type refusal names no spelling of yours (P3-V11-F2).

WHAT WENT WRONG, AND IT IS THE THIRD DOOR OF ONE REPAIR. Version 5 ended
the confusion between a person's text and synthtwin's own field names in
the format; review item P3-V9-F2 ended it for a valid document; review
item P3-V10-F3 stopped the FLOOR's walk from descending through a key
the table decides, so a malformed value there meets the rule that reads
its TYPE instead of the rule about an edited file.

That repair stated its own boundary in as many words -- "naming the kind
and never the spelling (R15)" -- and did not deliver it. The refusal a
person now meets says:

    The entry called 'missing_by_source -> PRIVATE_DIAGNOSIS' in the
    block for the column named 'reading' holds a block of named
    entries, and it has to hold a whole number.

`PRIVATE_DIAGNOSIS` came out of somebody's cells. The earlier repair
closed the door the S13 message opened and left this one standing, and
its focused test asked for the marker's absence only where C5-S13 fired,
so the ordinary path was never measured at all. `levels[].variants`
behaves identically.

THE REPAIR. Naming an entry by its own key is right everywhere the
format keys a mapping on one of synthtwin's own published words -- a
percentile name, a UTC offset, a numeric style, a group size in figures.
In the two mappings `canonical.TABLE_TEXT_KEY_SPACES` names it is wrong,
and that tuple is the one answer both halves of the product already
share. So `contract._entry_named` asks it, and where the table decides
the keys the entry is named by WHAT ITS KEYS ARE.

The producer cannot write this shape and the loader refused it before
and refuses it now, so strict acceptance has not moved. What moved is
what the refusal puts on the screen.

THE RED CHECK. `REINSTATE=P3-V11-F2` puts back the naming that shipped
-- the key spelled out whatever mapping it stands in -- and reds every
assertion here except the two that hold the ordinary naming in place.

Every table is built by the seeded neutral builders in `fixtures.py`
(plan D13) and every description by the REAL producer.
"""

import ast
import json
import os
import pathlib

import pytest

import fixtures
from synthtwin import canonical, contract, errors, profile, reading, taxonomy

# A spelling no cell of any table here holds by accident, standing for
# the sensitive text a real cell would carry.
_MARKER = "MARKERWORD"

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _the_naming_that_shipped(
    path: "tuple[object, ...]", key: str, name: str
) -> str:
    """`contract._entry_named` as it shipped: the key, always.

    Written out rather than reconstructed. What shipped was not a
    function at all -- the caller composed `f"{key} -> {name}"` inline --
    so this is that expression, in the seat the repair put a decision in.
    """
    return f"{key} -> {name}"


@pytest.fixture(autouse=True)
def _reinstated(monkeypatch: pytest.MonkeyPatch) -> None:
    """The red check, driven from the environment."""
    if os.environ.get("REINSTATE") == "P3-V11-F2":
        monkeypatch.setattr(contract, "_entry_named", _the_naming_that_shipped)


# -- the documents ------------------------------------------------------


def _numbers_and_a_marker(folder: pathlib.Path) -> dict:
    """A counting column publishing the marker as a source spelling."""
    values = [str(row) for row in range(60)] + [_MARKER] * 2
    path = fixtures.write(
        folder, "reading.csv", fixtures.single_column_table("reading", values)
    )
    read = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    return profile.build_document(
        read,
        taxonomy.Settings(
            small_cell_floor=1, declared_missing_values=(_MARKER,)
        ),
        [],
    )


def _labels(folder: pathlib.Path) -> dict:
    """A categorical column, for the second mapping the table keys."""
    values = ["north"] * 12 + ["south"] * 12 + ["east"] * 12
    path = fixtures.write(
        folder, "region.csv", fixtures.single_column_table("region", values)
    )
    read = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    return profile.build_document(read, taxonomy.Settings(), [])


# Every shape a value under a table-decided key can wrongly take. The
# first four are review item P3-V10-F3's; the last two are the ordinary
# wrong kinds, which reach the same door without any field name in them
# at all -- so this file cannot be passing because a name happened to be
# recognised somewhere.
_MALFORMED = (
    ("a block naming the pooled remainder", {"n_missing_withheld": 2}),
    (
        "a block naming the unnamed tally",
        {"n_sentinel_candidates_unpublished": 2},
    ),
    ("a block naming the pooled word", {contract.WITHHELD: 2}),
    ("a list holding such a block", [{"n_missing_withheld": 2}]),
    ("a piece of text", "two"),
    ("a number with a point in it", 2.5),
)

# And the value that is the right KIND and the wrong SIZE, which is the
# other refusal that names the entry (R16 rather than R15).
_OUT_OF_RANGE = ("a count of zero", 0)


def _put(document: dict, where: str, value: object) -> dict:
    """Return the document with one malformed value under the marker."""
    broken = json.loads(json.dumps(document))
    block = broken["columns"][0]
    if where == "missing_by_source":
        block["missing_by_source"] = {_MARKER: value}
    else:
        block["levels"][0]["variants"] = {_MARKER: value}
    return broken


def _refusal(folder: pathlib.Path, document: dict) -> str:
    """Write a document and return what the loader says about it."""
    written = fixtures.write_profile(folder, "edited.json", document)
    with pytest.raises(errors.ProfileError) as caught:
        contract.load_profile(f"{written}")
    return f"{caught.value}"


# -- THE FINDING --------------------------------------------------------


@pytest.mark.parametrize(
    "shape", _MALFORMED + (_OUT_OF_RANGE,), ids=lambda shape: shape[0]
)
@pytest.mark.parametrize("mapping", ("missing_by_source", "variants"))
def test_no_refusal_about_a_table_keyed_entry_quotes_its_key(
    tmp_path: pathlib.Path, mapping: str, shape: tuple
) -> None:
    """THE FINDING. The marker is absent from the refusal, unconditionally.

    The earlier focused test asked for this only where C5-S13 fired,
    which is the one path the earlier repair had already closed. This
    asks it of whatever refusal the loader actually raises, so the next
    rule that fires here is measured the day it starts firing.
    """
    _label, value = shape
    document = (
        _numbers_and_a_marker(tmp_path)
        if mapping == "missing_by_source"
        else _labels(tmp_path)
    )
    said = _refusal(tmp_path, _put(document, mapping, value))
    assert _MARKER not in said, (
        "A refusal about an entry of a mapping the TABLE keys put that "
        f"key's own spelling on the screen:\n{said}\n\nThe key is a "
        "spelling some cell held, character for character. Name the "
        "entry by what its keys are, as `contract._entry_named` does "
        "from `canonical.TABLE_TEXT_KEY_SPACES` -- never by one of them."
    )


@pytest.mark.parametrize(
    "shape", _MALFORMED + (_OUT_OF_RANGE,), ids=lambda shape: shape[0]
)
@pytest.mark.parametrize("mapping", ("missing_by_source", "variants"))
def test_the_refusal_still_says_where_it_is_and_what_is_wrong(
    tmp_path: pathlib.Path, mapping: str, shape: tuple
) -> None:
    """Withholding the key may not cost the person the sentence.

    A refusal that named nothing would satisfy the assertion above and
    leave somebody with a file they cannot fix, so what the message must
    still carry is asserted beside it: the mapping's own field name, the
    column, and what the entry owes.
    """
    _label, value = shape
    document = (
        _numbers_and_a_marker(tmp_path)
        if mapping == "missing_by_source"
        else _labels(tmp_path)
    )
    said = _refusal(tmp_path, _put(document, mapping, value))
    assert mapping in said, (
        f"the refusal no longer says which block the entry is in:\n{said}"
    )
    assert contract._A_SPELLING_OF_YOURS in said, (
        "the refusal no longer says that the entry is named by a "
        f"spelling out of the person's table:\n{said}"
    )
    assert "whole number" in said, (
        f"the refusal no longer says what the entry owes:\n{said}"
    )
    assert "reading" in said or "region" in said, (
        f"the refusal no longer says which column it is about:\n{said}"
    )


# -- the naming rule itself, and where it must NOT reach ----------------


def test_an_entry_keyed_by_synthtwins_own_words_is_still_named() -> None:
    """The over-narrowing check, asserted rather than hoped.

    Most mappings of the format are keyed on a word synthtwin publishes,
    and a person fixing a file needs to be told WHICH percentile, WHICH
    numeric style, WHICH offset. A repair that hid every key would make
    every one of those refusals useless, so the two answers are held
    apart here.
    """
    assert (
        contract._entry_named(
            ("columns", canonical.EACH, "numeric_styles"), "numeric_styles",
            "decimal",
        )
        == "numeric_styles -> decimal"
    )
    assert contract._entry_named((), "utc_offsets", "+00:00") == (
        "utc_offsets -> +00:00"
    )
    for path in canonical.TABLE_TEXT_KEY_SPACES:
        named = contract._entry_named(path, str(path[-1]), _MARKER)
        assert _MARKER not in named, named
        assert named == f"{path[-1]} -> {contract._A_SPELLING_OF_YOURS}", named


def test_every_table_keyed_counts_caller_hands_over_its_path() -> None:
    """The derivation, so a third table-keyed mapping cannot be forgotten.

    `_counts` names an entry by its key unless the caller says where the
    mapping sits, which makes a caller that forgets its path fail open.
    So the callers are read out of the module's own syntax and each is
    required to pass a path -- and the paths passed anywhere in the
    module are required to be exactly `canonical`'s own key spaces, so
    a mapping added to that tuple has nowhere to hide either.
    """
    source = (REPO_ROOT / "src" / "synthtwin" / "contract.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    keyed = {path[-1] for path in canonical.TABLE_TEXT_KEY_SPACES}
    forgotten: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not (isinstance(node.func, ast.Name) and node.func.id == "_counts"):
            continue
        named = node.args[1]
        if not (isinstance(named, ast.Constant) and named.value in keyed):
            continue
        if len(node.args) < 5:
            forgotten.append(f"line {node.lineno}: _counts({named.value!r})")
    assert not forgotten, (
        "These calls read a mapping the TABLE keys and do not say where "
        "it sits, so every refusal about one of its entries quotes a "
        "spelling out of somebody's table:\n  " + "\n  ".join(forgotten)
    )
    passed = {
        found
        for name in dir(contract)
        for found in [getattr(contract, name)]
        if isinstance(found, tuple)
        and all(isinstance(step, str) for step in found)
        and canonical.EACH in found
    }
    assert passed == set(canonical.TABLE_TEXT_KEY_SPACES), (
        "The key spaces this module names are not `canonical`'s own:\n"
        f"  here: {sorted(passed)}\n  canonical: "
        f"{sorted(canonical.TABLE_TEXT_KEY_SPACES)}"
    )
