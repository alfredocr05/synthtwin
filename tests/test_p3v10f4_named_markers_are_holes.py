"""A word the description names as a hole is a hole (review P3-V10-F4).

THE DEFECT THIS FILE EXISTS TO KEEP CLOSED, and it is the plainest run
the product has. Profile one column of sixty numbers and twelve literal
`n/a` cells, with no options at all. The description publishes
`n_present: 60`, `n_missing: 12` and `missing_by_source: {"n/a": 12}`.
Validate that exact same CSV against that exact description: it was
re-described with every built-in missing word PINNED to data, measured
seventy-two present and zero missing, and reported TWENTY-EIGHT
obligations MISSED at exit 3 -- both presence counts, both distinctness
counts, `n_not_numeric`, eleven ladder rungs, three moments and the
rest, each with the pinned reading's number printed beside the
description's own.

WHY THE PIN WAS THERE, AND WHY IT DOES NOT REACH THIS. Residual R-P2-13:
a generated value can legitimately BE the text of one of synthtwin's own
missing markers, and no file may be failed for colliding with this
package's vocabulary. That reason covers a marker the description passes
no verdict on. It does not cover one the description NAMES: a key of
`missing_by_source` is the description saying which spelling twelve of
its holes wore, and reading that spelling as data measures the file
under a rule its description was not written under. Validation method
clause V2.4-A4 said as much in its own words and then pinned the
built-in table anyway; plan amendment A-P3-39 and clause V2.4-A10 settle
which of the two stands.

WHERE THE PIN STILL LIVES, asserted below so the narrowing cannot creep:
a built-in word NO column of the description publishes as a hole source
is still data on the measurement side, whatever the measured file holds.

WHAT IS STILL OPEN, and it is stated rather than implied. The two
presence COUNTS ask the weaker publication question of amendment
A-P3-5 clause 1 -- is the number of non-blank holes published, never
their spellings -- so a column whose holes are pooled below the floor
under two spellings of one built-in word still reports those two
counts by blankness. That is residual R-P3-11, it is bounded to exactly
those two obligations, and the last test here pins its size.

THE RED CHECK:

* `REINSTATE=P3-V10-F4` -- the description's published keys read as
  naming nothing, which is the pin as it stood. Reds the witness, the
  settings assertion and the census.

Every table here is built by the seeded neutral builders in
`fixtures.py` (plan D13), and every description by the REAL producer.
"""

import os
import pathlib

import pytest

import fixtures
from synthtwin import contract, parsing, validation
from synthtwin.cli import main

MARKER = "n/a"


def reinstate(monkeypatch: pytest.MonkeyPatch) -> None:
    """Pin every built-in missing word to data again, as it stood."""
    monkeypatch.setattr(
        validation,
        "_built_in_words_the_description_names_as_holes",
        lambda _description: (),
    )


@pytest.fixture(autouse=True)
def _reinstated(monkeypatch: pytest.MonkeyPatch) -> None:
    if os.environ.get("REINSTATE") == "P3-V10-F4":
        reinstate(monkeypatch)


def _readings(holes: int, ordinary: int = 60) -> "list[str]":
    """Ordinary decimals, with ``holes`` cells wearing the marker."""
    values = [f"{10 + index * 3}.5" for index in range(ordinary)]
    return values + [MARKER] * holes


def _table(
    folder: pathlib.Path, name: str, holes: int, ordinary: int = 60
) -> pathlib.Path:
    return fixtures.write(
        folder,
        name,
        fixtures.single_column_table("reading", _readings(holes, ordinary)),
    )


def _counts(report: str) -> "dict[str, int]":
    """The five verdict counts off a written quality report."""
    found: dict[str, int] = {}
    for line in report.splitlines():
        words = line.split()
        if len(words) > 2 and words[1].isupper() and words[0].isdigit():
            found[words[1]] = int(words[0])
    return found


def _described(
    folder: pathlib.Path, table: pathlib.Path, floor: "int | None" = None
) -> "tuple[pathlib.Path, contract.Profile]":
    """Describe one table; `floor` names a small-cell floor when it matters.

    The runs this file is really about are made with no options at
    all, which is the plainest run the product has. The two cases below whose SUBJECT
    is a pooled spelling have to say at what floor a spelling is pooled:
    since the owner's ruling (plan amendment A-P4-37) the default is 1,
    at which nothing is held back and no spelling is ever pooled, so
    those two name the floor of eleven they were written against.
    """
    options = [] if floor is None else ["--smallest-group", f"{floor}"]
    assert main(["profile", f"{table}"] + options) == 0
    written = folder / f"{table.stem}-profile.json"
    return written, contract.load_profile(f"{written}")


def test_the_description_names_the_spelling_its_holes_wore(
    tmp_path: pathlib.Path,
) -> None:
    """The premise: nothing has to be guessed about these twelve cells."""
    table = _table(tmp_path, "reading.csv", 12)
    _written, description = _described(tmp_path, table)
    column = description.columns[0]
    assert column.n_present == 60
    assert column.n_missing == 12
    assert column.missing_by_source == {MARKER: 12}
    assert column.n_missing_withheld == 0
    # ...and nobody typed an option: the marker is a hole because the
    # producer's own built-in table reads it as one.
    assert description.settings.declared_missing_values.n_declared == 0
    assert description.settings.kept_values.n_declared == 0


def test_the_table_its_own_description_came_from_misses_nothing(
    tmp_path: pathlib.Path,
) -> None:
    """Twenty-eight misses on a perfect match, and now none."""
    table = _table(tmp_path, "reading.csv", 12)
    written, _description = _described(tmp_path, table)
    assert main(["validate", f"{written}", "--twin", f"{table}"]) == 0
    report = (tmp_path / "reading-quality.txt").read_text("utf-8")
    counted = _counts(report)
    assert counted["MISSED"] == 0
    # And the two counts the wrong reading got wrong are HELD rather
    # than merely unreported.
    assert "presence.n_present [universal.n_present]: HELD" in report
    assert "presence.n_missing [universal.n_missing]: HELD" in report


def test_the_measurement_side_stops_pinning_only_the_named_words(
    tmp_path: pathlib.Path,
) -> None:
    """The narrowing reaches the named words, and the pin holds elsewhere."""
    table = _table(tmp_path, "reading.csv", 12)
    _written, description = _described(tmp_path, table)
    split = validation.settings_over_the_split(description)
    assert MARKER not in split.kept_values
    # Every OTHER built-in missing word is still data on this side,
    # which is the whole of what R-P2-13 asks for on a marker the
    # description passes no verdict about.
    for spelling in parsing.built_in_missing_texts():
        if spelling and spelling != MARKER:
            assert spelling in split.kept_values
    # ...and so is this one, on a description no column of which names
    # it. Five cells sit below the publication floor of eleven this run
    # declares, so the spelling is pooled and named nowhere.
    pooled = _table(tmp_path, "pooled.csv", 5)
    _elsewhere, other = _described(tmp_path, pooled, floor=11)
    assert other.columns[0].missing_by_source == {}
    assert MARKER in validation.settings_over_the_split(other).kept_values


def test_every_built_in_word_the_description_names_comes_off_the_pin(
    tmp_path: pathlib.Path,
) -> None:
    """One word is not a special case; the rule is the published map.

    Twelve cells of each non-blank built-in word, all above the floor,
    so the column names every one of them. What stays pinned is the
    three stand-in NUMBERS, whose verdict is a per-column matter the
    settings block answers for separately (A-P3-35).
    """
    # EVERY built-in word, the exact-spelling member included: it is
    # not a special case here either, and a version of this walk that
    # skipped it would leave the newest member of the vocabulary
    # unpinned (plan P4-D6.2).
    words = [
        spelling
        for spelling in parsing.built_in_missing_texts()
        if spelling
    ]
    values = [f"{10 + index * 3}.5" for index in range(60)]
    for word in words:
        values = values + [word] * 12
    table = fixtures.write(
        tmp_path,
        "many.csv",
        fixtures.single_column_table("reading", values),
    )
    written, description = _described(tmp_path, table)
    assert sorted(description.columns[0].missing_by_source) == sorted(words)
    kept = validation.settings_over_the_split(description).kept_values
    for word in words:
        assert word not in kept
    assert sorted(kept) == sorted(
        f"{value:g}" for value in parsing.NUMERIC_SENTINELS
    )
    assert main(["validate", f"{written}", "--twin", f"{table}"]) == 0
    assert (
        _counts((tmp_path / "many-quality.txt").read_text("utf-8"))["MISSED"]
        == 0
    )


def test_the_twin_of_that_description_still_measures_clean(
    tmp_path: pathlib.Path,
) -> None:
    """End to end, because a repair that breaks the twin is not one.

    The twin writes every absent cell empty, so its holes are blank and
    nothing in it wears the marker. This is the run that would catch a
    narrowing that reached further than the description's own words.
    """
    table = _table(tmp_path, "reading.csv", 12)
    written, _description = _described(tmp_path, table)
    assert main(["generate", f"{written}"]) == 0
    twin = tmp_path / "reading-twin.csv"
    assert twin.exists()
    assert main(["validate", f"{written}", "--twin", f"{twin}"]) == 0
    counted = _counts(
        (tmp_path / "reading-twin-quality.txt").read_text("utf-8")
    )
    assert counted["MISSED"] == 0


def test_what_is_still_open_is_two_counts_and_no_more(
    tmp_path: pathlib.Path,
) -> None:
    """Residual R-P3-11, pinned at its size so it cannot grow.

    Six cells spelled `n/a` and six spelled `N/A` are twelve holes of one
    built-in word under two spellings, and at the floor of eleven this
    run declares NEITHER spelling reaches the floor, so the column names
    no source at all. The floor is declared rather than assumed because
    the default is 1 since the owner's ruling (plan amendment A-P4-37),
    and at 1 both spellings are published and this residual is not
    reachable at all. `missing_by_class` still names twelve non-blank
    holes, which is the weaker publication amendment A-P3-5 clause 1
    lets the two presence counts be read over -- so those two are still
    measured by blankness and still miss. Nothing else does: every
    obligation that needs the spellings falls back to the file's own
    description.
    """
    values = [f"{10 + index * 3}.5" for index in range(60)]
    values = values + ["n/a"] * 6 + ["N/A"] * 6
    table = fixtures.write(
        tmp_path,
        "split.csv",
        fixtures.single_column_table("reading", values),
    )
    written, description = _described(tmp_path, table, floor=11)
    column = description.columns[0]
    assert column.missing_by_source == {}
    assert column.n_missing_withheld == 12
    assert column.missing_by_class.text_code == 12
    assert main(["validate", f"{written}", "--twin", f"{table}"]) == 3
    report = (tmp_path / "split-quality.txt").read_text("utf-8")
    assert _counts(report)["MISSED"] == 2
    assert "presence.n_present [universal.n_present]: MISSED" in report
    assert "presence.n_missing [universal.n_missing]: MISSED" in report
