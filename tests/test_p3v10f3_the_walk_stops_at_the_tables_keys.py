"""The floor's walk stops at a key the table decides (review P3-V10-F3).

WHAT WENT WRONG, AND IT IS THE SECOND HALF OF ONE REPAIR. Version 5
ended the confusion between a person's text and synthtwin's own names in
the FORMAT, and review item P3-V9-F2 ended it for a VALID document: the
walk that enforces the floor stopped reading a key as one of this
package's words inside the two mappings the table keys. It went on
reading PAST such a key, though -- straight down into whatever stood
under it -- so the confusion came back one step lower the moment the
value was not a count:

    missing_by_source = {"PRIVATE_DIAGNOSIS": {"n_missing_withheld": 2}}

At a floor of one that document was refused for the wrong reason, in a
sentence carrying the table's own spelling:

    'missing_by_source -> PRIVATE_DIAGNOSIS -> n_missing_withheld'
    holds 2 row(s) back, and the smallest group size is 1
    ... so this file has been changed since it was written.

Two things are wrong with it. The person is told their file was EDITED,
which is what C5-S13 means, when what is actually wrong is that an entry
holds the wrong kind of value -- and the walk that composed it promises
in its own docstring that no value of the table is read or quoted, while
`PRIVATE_DIAGNOSIS` came out of somebody's cells. The same held under
`levels[].variants`, which the finding did not name.

THE REPAIR. What stands under a key the table decides is a COUNT
(contract 5, C5-N5). A count has nothing under it, so the walk stops at
such a mapping rather than reading its values, and a document that puts
a block there meets the rule that reads the entry's TYPE -- which names
the kind of value found and asks for the kind required.

The producer cannot write this shape and the loader refused it before
and refuses it now, so nothing here is about strict acceptance
loosening. What moved is WHICH refusal a person meets and what it says.

THE RED CHECK. `REINSTATE=P3-V10-F3` puts the shipped walk back, written
out below rather than described, and reds every assertion in this file
except the two that prove the floor's rule still bites.

Every table here is built by the seeded neutral builders in
`fixtures.py` (plan D13) and every description by the REAL producer.
"""

import json
import os
import pathlib

import pytest

import fixtures
from synthtwin import canonical, contract, errors, profile, reading, taxonomy

# A spelling no cell of any table here holds by accident, standing for
# the sensitive text a real cell would carry.
_MARKER = "MARKERWORD"


def _the_walk_that_shipped(
    node: object, path: "tuple[object, ...]"
) -> "list[tuple[tuple[object, ...], int, str]]":
    """`contract._held_back_in` exactly as it shipped, for the red check.

    It is written out rather than reconstructed from the current one: a
    reinstatement somebody has to work out is a reinstatement nobody
    runs. The one difference is the last line of the mapping branch --
    the shipped walk went on into the value under EVERY key, including a
    key the table decided.
    """
    found: list[tuple[tuple[object, ...], int, str]] = []
    if isinstance(node, dict):
        the_tables_own_text = canonical.keys_are_the_tables_own_text(path)
        for key in sorted(node):
            value = node[key]
            here = path + (key,)
            if not the_tables_own_text:
                if key == contract.WITHHELD and contract._is_a_row_count(value):
                    found = found + [(here, value, contract._POOLED)]
                if key == contract._NAMED_REMAINDER and contract._is_a_row_count(
                    value
                ):
                    found = found + [(here, value, contract._POOLED)]
                if key == contract._UNNAMED_TALLY and contract._is_a_row_count(
                    value
                ):
                    found = found + [(here, value, contract._TOO_RARE)]
            found = found + _the_walk_that_shipped(value, here)
    elif isinstance(node, list):
        place = 0
        for item in node:
            found = found + _the_walk_that_shipped(item, path + (place,))
            place = place + 1
    return found


@pytest.fixture(autouse=True)
def _reinstated(monkeypatch: pytest.MonkeyPatch) -> None:
    """Put the shipped walk back when REINSTATE asks for it."""
    if os.environ.get("REINSTATE") == "P3-V10-F3":
        monkeypatch.setattr(contract, "_held_back_in", _the_walk_that_shipped)


# -- the documents ------------------------------------------------------


def _numbers_and_a_marker(folder: pathlib.Path, floor: int) -> dict:
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
            small_cell_floor=floor, declared_missing_values=(_MARKER,)
        ),
        [],
    )


def _labels(folder: pathlib.Path, floor: int) -> dict:
    """A categorical column, for the second mapping the table keys."""
    values = ["north"] * 12 + ["south"] * 12 + ["east"] * 12
    path = fixtures.write(
        folder, "region.csv", fixtures.single_column_table("region", values)
    )
    read = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    return profile.build_document(
        read, taxonomy.Settings(small_cell_floor=floor), []
    )


# The four shapes a value under a table-decided key can wrongly take,
# each one carrying a name the walk used to read as its own.
_MALFORMED = (
    ("a block naming the pooled remainder", {"n_missing_withheld": 2}),
    (
        "a block naming the unnamed tally",
        {"n_sentinel_candidates_unpublished": 2},
    ),
    ("a block naming the pooled word", {contract.WITHHELD: 2}),
    ("a list holding such a block", [{"n_missing_withheld": 2}]),
)


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
    written = fixtures.write(
        folder, "edited.json", canonical.serialize(document)
    )
    with pytest.raises(errors.ProfileError) as caught:
        contract.load_profile(f"{written}")
    return f"{caught.value}"


# -- the walk itself ----------------------------------------------------


def _steps_through_a_key_the_table_decides(
    path: "tuple[object, ...]",
) -> bool:
    """Whether any step of this path stands inside a table-keyed mapping."""
    for length in range(len(path)):
        if canonical.keys_are_the_tables_own_text(path[:length]):
            return True
    return False


@pytest.mark.parametrize("floor", (1, 11))
@pytest.mark.parametrize("shape", _MALFORMED, ids=lambda shape: shape[0])
@pytest.mark.parametrize("mapping", ("missing_by_source", "variants"))
def test_the_walk_reports_nothing_under_a_key_the_table_decides(
    tmp_path: pathlib.Path, mapping: str, shape: tuple, floor: int
) -> None:
    """THE FINDING, at the walk. No path may step through the table's text.

    This is the assertion the repair turns on, and it is stated about
    the class rather than about the witness: whatever the walk returns,
    not one of its paths may have gone through a mapping whose keys the
    table decides. So a mapping added to `TABLE_TEXT_KEY_SPACES` is
    covered on the commit that adds it.
    """
    _label, value = shape
    document = (
        _numbers_and_a_marker(tmp_path, floor)
        if mapping == "missing_by_source"
        else _labels(tmp_path, floor)
    )
    broken = _put(document, mapping, value)
    walked = contract._held_back_in(broken, ())
    through = [
        path
        for path, _count, _kind in walked
        if _steps_through_a_key_the_table_decides(path)
    ]
    assert not through, (
        "The floor's walk read past a key the table decides and found "
        f"something under it: {through}. What stands under such a key is "
        "a count, a count has nothing under it, and a value that is not "
        "one belongs to the rule that reads its type -- which names the "
        "kind and never the spelling."
    )


# -- the refusal a person actually meets --------------------------------


@pytest.mark.parametrize("floor", (1, 11))
@pytest.mark.parametrize("shape", _MALFORMED, ids=lambda shape: shape[0])
@pytest.mark.parametrize("mapping", ("missing_by_source", "variants"))
def test_the_malformed_value_meets_the_wrong_type_refusal(
    tmp_path: pathlib.Path, mapping: str, shape: tuple, floor: int
) -> None:
    """It is refused for what is wrong with it, not for being edited.

    C5-S13 means one thing: a description made at a floor of one is
    holding rows back, which a description synthtwin wrote never does,
    so somebody changed the file. Saying that about an entry holding a
    block where a number belongs sends a person to look for an edit that
    is not the trouble.
    """
    _label, value = shape
    document = (
        _numbers_and_a_marker(tmp_path, floor)
        if mapping == "missing_by_source"
        else _labels(tmp_path, floor)
    )
    said = _refusal(tmp_path, _put(document, mapping, value))
    assert "C5-S13" not in said, (
        "the malformed value is refused as an edited file rather than as "
        f"an entry holding the wrong kind of value:\n{said}"
    )
    assert "has to hold a whole number" in said, (
        "the refusal no longer says what kind of value the entry owes:\n"
        f"{said}"
    )
    assert "holds a block of named entries" in said or "holds a list" in said, (
        f"the refusal no longer names the kind of value found:\n{said}"
    )


@pytest.mark.parametrize("shape", _MALFORMED, ids=lambda shape: shape[0])
@pytest.mark.parametrize("mapping", ("missing_by_source", "variants"))
def test_no_edited_file_refusal_ever_quotes_the_tables_own_spelling(
    tmp_path: pathlib.Path, mapping: str, shape: tuple
) -> None:
    """The boundary the walk states in its own docstring, measured.

    `_held_back_in` promises that no value of the table is read, and
    `_nothing_is_held_back` promises that none is quoted. A refusal
    carrying `MARKERWORD` here is that promise being broken, whatever
    else is true of the sentence.
    """
    _label, value = shape
    document = (
        _numbers_and_a_marker(tmp_path, 1)
        if mapping == "missing_by_source"
        else _labels(tmp_path, 1)
    )
    said = _refusal(tmp_path, _put(document, mapping, value))
    if "C5-S13" in said:
        assert _MARKER not in said, (
            "the floor's refusal put a spelling out of somebody's table "
            f"on the screen:\n{said}"
        )


# -- and the rule the walk exists for still bites -----------------------


def test_the_floor_still_refuses_a_structural_field_that_holds_rows_back(
    tmp_path: pathlib.Path,
) -> None:
    """The repair narrows WHERE the walk reads, and nothing about the rule.

    This is the over-narrowing check: stopping at the table's mappings
    must not stop the walk anywhere else. Both structural fields, in the
    same column block, still meet C5-S13 at a floor of one.
    """
    document = _numbers_and_a_marker(tmp_path, 1)
    for field in ("n_missing_withheld", "n_sentinel_candidates_unpublished"):
        edited = json.loads(json.dumps(document))
        edited["columns"][0][field] = 2
        said = _refusal(tmp_path, edited)
        assert "C5-S13" in said, (
            f"'{field}' holding rows back at a floor of one is exactly "
            f"what this rule is for, and it was accepted:\n{said}"
        )
        assert "smallest group size is 1" in said


def test_a_source_spelling_that_reads_like_one_of_our_names_still_loads(
    tmp_path: pathlib.Path,
) -> None:
    """And the valid case P3-V9-F2 opened is still open.

    A cell can say `n_missing_withheld`. The walk stopping earlier must
    not make that spelling refusable again, so the round trip is
    asserted here too rather than left to the neighbouring file.
    """
    values = [str(row) for row in range(60)] + ["n_missing_withheld"] * 2
    path = fixtures.write(
        tmp_path, "reading.csv", fixtures.single_column_table("reading", values)
    )
    read = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(
        read,
        taxonomy.Settings(
            small_cell_floor=1,
            declared_missing_values=("n_missing_withheld",),
        ),
        [],
    )
    written = fixtures.write_profile(tmp_path, "ok.json", document)
    loaded = contract.load_profile(f"{written}")
    assert loaded.columns[0].missing_by_source == {"n_missing_withheld": 2}
