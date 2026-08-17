"""A key the TABLE decides is not one of our words (review P3-V9-F2).

THE DEFECT THIS FILE EXISTS TO KEEP CLOSED. Contract version 5 exists to
end one confusion: the person's text and synthtwin's own names sharing a
namespace. It ended it in the FORMAT -- `missing_by_source` holds one
key space and the pooled remainder moved out to a field of its own --
and left it standing in the two walks that read the format.

Both walks looked for the words "held back" by NAME, anywhere in the
document, and both exempted exactly one mapping. So:

* sixty numbers and two cells literally spelled `n_missing_withheld`,
  described with `--smallest-group 1 --missing-value n_missing_withheld`,
  wrote `missing_by_source: {"n_missing_withheld": 2}` -- which is
  correct and which the producer's own rules permit -- and the loader
  then read that key as the structural field, refused the file under
  C5-S13, and told the person their untouched description had been
  changed since it was written;
* the same for a cell spelled `n_sentinel_candidates_unpublished`;
* a CATEGORICAL column with twelve rows labelled `n_missing_withheld`,
  at the same floor, failed identically -- and the reviewer's witness
  did not name this one, because the exemption was written about one
  field rather than about the class of place;
* and a categorical label reading `(withheld)` never got that far: the
  PRODUCER's own publication guard, holding the mirror of the same rule,
  stopped the run with an internal fault against a perfectly ordinary
  table.

THE REPAIR IS ONE TABLE, NOT TWO RULES. `canonical.TABLE_TEXT_KEY_SPACES`
names the mappings whose keys the table decides; the producer's guard
and the loader's walk both read it; and the first test below DERIVES
what that table must hold from `profile.PUBLICATION_RULES`, which gives
every path of the finished document a kind and says outright which of
them may carry a spelling. So a mapping added to the format with the
table's text for keys turns this suite red until somebody names it.

THE RED CHECKS:

* `REINSTATE=P3-V9-F2` -- the key-space table back to `missing_by_source`
  alone, which is what both walks held. Reds the derivation test and
  every label witness.
* `REINSTATE=P3-V9-F2-blind` -- the question answered "no" everywhere,
  which is what the walk did before any exemption existed. Reds every
  witness including the source-spelling one.
* `REINSTATE=P3-V9-F2-open` -- the question answered "yes" everywhere,
  which is the failure in the other direction. Reds the floor's own
  refusals, so the exemption cannot be widened into a hole.

Every table here is built by the seeded neutral builders in
`fixtures.py` (plan D13), and every description by the REAL producer.
"""

import json
import os
import pathlib

import pytest

import fixtures
from synthtwin import canonical, contract, errors, profile
from synthtwin.cli import main

# The two field names the walk looks for, and the format's one word for
# "held back". All three are things a cell of somebody's table can say,
# which is the whole of this file's subject.
SAYABLE = (
    "n_missing_withheld",
    "n_sentinel_candidates_unpublished",
    contract.WITHHELD,
)

_ONLY_THE_SOURCES = (("columns", canonical.EACH, "missing_by_source"),)


@pytest.fixture(autouse=True)
def _reinstated(monkeypatch: pytest.MonkeyPatch) -> None:
    """Put one of the pre-repair answers back when REINSTATE asks."""
    asked = os.environ.get("REINSTATE")
    if asked == "P3-V9-F2":
        monkeypatch.setattr(
            canonical, "TABLE_TEXT_KEY_SPACES", _ONLY_THE_SOURCES
        )
    if asked == "P3-V9-F2-blind":
        monkeypatch.setattr(
            canonical, "keys_are_the_tables_own_text", lambda _path: False
        )
    if asked == "P3-V9-F2-open":
        monkeypatch.setattr(
            canonical, "keys_are_the_tables_own_text", lambda _path: True
        )


# -- the table is derived from the producer's own rules ----------------


def _spelling_key_spaces() -> "tuple[tuple[str, ...], ...]":
    """Every mapping `PUBLICATION_RULES` lets a SPELLING be the key of.

    The producer's publication table gives every path of the finished
    document a kind, and a mapping whose keys the data decides carries a
    rule for the key itself. A key rule of `authorized-spelling` is that
    table saying, in the producer's own words, that a value of the real
    table may stand there -- which is exactly the question both walks
    have to answer, so it is asked of the rules rather than of a second
    list somebody keeps in step by hand.
    """
    found: list[tuple[str, ...]] = []
    for path in profile.PUBLICATION_RULES:
        if not path or path[len(path) - 1] != profile._KEY_OF:
            continue
        if profile.PUBLICATION_RULES[path] != profile._SPELLING:
            continue
        found = found + [tuple(path[: len(path) - 1])]
    return tuple(sorted(found))


def test_the_key_space_table_is_the_producers_own_answer() -> None:
    """One list, and it is the one the format already implies."""
    assert canonical.TABLE_TEXT_KEY_SPACES == _spelling_key_spaces()
    # And the producer's markers for "any list place" agree with this
    # module's, or the two path shapes would never meet.
    assert profile._EACH == canonical.EACH


def test_every_named_space_is_answered_yes_at_a_real_index() -> None:
    """The walk carries list indexes; the table carries a marker."""
    for space in canonical.TABLE_TEXT_KEY_SPACES:
        walked: list[object] = []
        for step in space:
            walked = walked + [3 if step == canonical.EACH else step]
        assert canonical.keys_are_the_tables_own_text(tuple(walked))
    # A path the format does not have answers no, which is the answer
    # that refuses a document rather than accepting one.
    assert not canonical.keys_are_the_tables_own_text(("columns", 0))
    assert not canonical.keys_are_the_tables_own_text(())


# -- the four witnesses, run end to end --------------------------------


def _described(
    folder: pathlib.Path, values: "list[str]", *declared: str
) -> "tuple[pathlib.Path, dict]":
    """Describe one column at a floor of one; return the path and document."""
    table = fixtures.write(
        folder,
        "reading.csv",
        fixtures.single_column_table("reading", values),
    )
    command = ["profile", f"{table}", "--smallest-group", "1"]
    for word in declared:
        command = command + ["--missing-value", word]
    assert main(command) == 0
    written = folder / "reading-profile.json"
    return written, json.loads(written.read_text(encoding="utf-8"))


@pytest.mark.parametrize("sayable", SAYABLE)
def test_a_declared_word_of_ours_spelled_by_a_cell_round_trips(
    tmp_path: pathlib.Path, sayable: str
) -> None:
    """The reviewer's own witness, and its two neighbours."""
    values = [str(row) for row in range(60)] + [sayable] * 2
    written, document = _described(tmp_path, values, sayable)
    block = document["columns"][0]
    assert block["missing_by_source"] == {sayable: 2}
    # The structural field of that name is zero, so the only thing in
    # the file wearing this text is the person's own cells.
    assert block["n_missing_withheld"] == 0
    assert block["n_sentinel_candidates_unpublished"] == 0
    # And the loader takes the file the producer just wrote.
    loaded = contract.load_profile(f"{written}")
    assert loaded.columns[0].missing_by_source == {sayable: 2}


@pytest.mark.parametrize("sayable", SAYABLE)
def test_a_label_spelled_like_one_of_our_names_round_trips(
    tmp_path: pathlib.Path, sayable: str
) -> None:
    """A categorical LABEL, which the cited witness did not reach.

    `levels[].variants` keys itself on the spelling rows wrote a label
    with, so it is the second mapping the table decides -- and the
    `(withheld)` case here is the one that stopped the PRODUCER, before
    any loader saw a file.
    """
    values = [sayable] * 12 + ["north"] * 12 + ["south"] * 12
    written, document = _described(tmp_path, values)
    block = document["columns"][0]
    assert block["role"] == "categorical"
    spellings: list[str] = []
    for level in block["levels"]:
        for spelling in level["variants"]:
            spellings = spellings + [spelling]
    assert sayable in spellings
    loaded = contract.load_profile(f"{written}")
    assert loaded.columns[0].name == "reading"


# -- and the floor's own rule still bites ------------------------------


def _refusal(written: pathlib.Path, folder: pathlib.Path, edit) -> str:
    """Edit a written description and return the loader's refusal."""
    document = json.loads(written.read_text(encoding="utf-8"))
    edit(document)
    changed = fixtures.write(
        folder, "edited.json", canonical.serialize(document)
    )
    with pytest.raises(errors.ProfileError) as caught:
        contract.load_profile(f"{changed}")
    return f"{caught.value}"


def test_a_floor_of_one_still_holds_nothing_back(
    tmp_path: pathlib.Path,
) -> None:
    """Every position the exemption does NOT reach is still refused.

    The repair narrows where a KEY is read as one of this package's
    words. It narrows nothing about the rule itself, so each of these
    five positions -- two field names, and the pooled word in the three
    mappings whose keys stay first-party -- must still stop the file.
    """
    values = [str(row) for row in range(60)]
    written, _document = _described(tmp_path, values)

    def field(name: str, value: int):
        def edit(document: dict) -> None:
            document["columns"][0][name] = value

        return edit

    def under(mapping: str, value: int):
        def edit(document: dict) -> None:
            block = document["columns"][0]
            block[mapping] = dict(block[mapping])
            block[mapping][contract.WITHHELD] = value

        return edit

    for edit in (
        field("n_missing_withheld", 2),
        field("n_sentinel_candidates_unpublished", 2),
        under("missing_by_class", 4),
        under("numeric_styles", 2),
    ):
        said = _refusal(written, tmp_path, edit)
        assert "C5-S13" in said
        assert "smallest group size is 1" in said
