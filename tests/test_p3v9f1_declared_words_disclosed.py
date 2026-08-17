"""What synthtwin tells you about the words you typed (review P3-V9-F1).

THE DEFECT THIS FILE EXISTS TO KEEP CLOSED. `synthtwin profile t.csv
--missing-value <a marker of your own>` writes that marker into the
description -- exactly, as a key of the counting column's
`missing_by_source`, wherever at least `small_cell_floor` rows share it
and the column publishes values at all. That is right, and it is what
contract version 5 was built for: a description that does not record
how a cell was read cannot be read back, and a table checked against
its own genuine description came back with failures that were not real.

The profiler's summary page printed that marker in the column block --
`counted as missing: <the marker> (12)` -- and then, four screens lower,
told the reader that synthtwin would keep no record of any word they
typed outside its own thirteen. `SECURITY.md` and the governing
contract denied it too, flatly and with no place named. Every one of
those sentences was reaching for a true statement about the SETTINGS
BLOCK, and every one was written without saying so.

WHY THAT IS A SAFETY DEFECT. A description is safer to move than the
table because of what it holds back. A researcher who reads that a
diagnosis code or a patient identifier is absent from the file, and it
is not, hands the file on. A false assurance about withholding is worse
than no assurance, so this file asserts the three places the truth is
now said, in the order a person meets them:

1. BEFORE THEY TYPE -- the `--missing-value` help leads with it.
2. BEFORE EITHER FILE EXISTS -- a banded notice naming the word, its
   column and its count, on the lowered-floor warning's precedent and
   in its place.
3. ON THE PAGE THEY ARE HANDED -- the summary lists every word of
   theirs the description carries, so a person who opens only that file
   is told it.

...and one thing it does NOT do, asserted so that it stays deliberate:
nothing extra is said on a run where no word of the person's reached
the description. A paragraph printed on every ordinary run is a
paragraph people stop reading, which is the rule the lowered-floor
block is written under.

THE RED CHECKS. Each puts one piece of the pre-repair behaviour back in
memory, so that no assertion here is one that cannot fail:

* `REINSTATE=P3-V9-F1` -- the summary's retired closing sentence,
  replacing the section that names the words. Reds the summary tests.
* `REINSTATE=P3-V9-F1-quiet` -- the notice suppressed, which is the
  screen exactly as it stood. Reds the notice tests.
* `REINSTATE=P3-V9-F1-help` -- the `--missing-value` help as it read
  before, which mentioned the columns in a trailing clause and led with
  the settings. Reds the help test.
* `REINSTATE=P3-V9-F1-page` -- a summary that names no spelling at all
  while the description beside it holds one, which is the shape of the
  defect with the page silent instead of wrong. Reds the agreement
  test.

Every table here is built by the seeded neutral builders in
`fixtures.py` (plan D13: no data-format file is ever committed), and
every description by the REAL producer.
"""

import os
import pathlib

import pytest

import fixtures
from synthtwin import cli, summary, taxonomy
from synthtwin.cli import main

FLOOR = taxonomy.Settings().small_cell_floor

# A marker no vocabulary of synthtwin's holds and no fixture builder
# produces, so that finding it in a file means the producer put it
# there. It is neutral text: the decontamination manifest governs this
# file like any other.
MARKER = "a-marker-of-my-own"

# The wording the help carried before the repair. It named the columns
# only in a trailing clause, after the settings rule, so a person
# skimming for what they must not type met the reassurance first.
_THE_OLD_HELP = (
    "a value that means 'no value' in your table, even though synthtwin "
    "would otherwise treat it as data. The profile records how many "
    "values you named, the rule that matched them, and -- where what you "
    "named is one of synthtwin's own words for 'no value' -- which of "
    "those words it was; a word of your own is never written into the "
    "settings, though the column still lists the spellings it counted as "
    "missing, on the same rules as any other missing spelling."
)

# The sentence the summary closed with before the repair.
_THE_OLD_CLOSE = (
    "    For any other word you typed, keep a note of the command",
    "    you ran; synthtwin will not keep one for you.",
    "",
)


@pytest.fixture(autouse=True)
def _reinstated(monkeypatch: pytest.MonkeyPatch) -> None:
    """Put the pre-repair behaviour back when REINSTATE asks for it."""
    asked = os.environ.get("REINSTATE")
    if asked == "P3-V9-F1":
        monkeypatch.setattr(
            summary,
            "_your_own_words_lines",
            lambda _document: list(_THE_OLD_CLOSE),
        )
    if asked == "P3-V9-F1-quiet":
        monkeypatch.setattr(cli, "_declared_words_notice", lambda _named: "")
    if asked == "P3-V9-F1-help":
        monkeypatch.setattr(cli, "_MISSING_VALUE_HELP", _THE_OLD_HELP)
    if asked == "P3-V9-F1-page":
        monkeypatch.setattr(
            summary, "_your_own_words_lines", lambda _document: []
        )
        monkeypatch.setattr(
            summary,
            "_missing_spelling_words",
            lambda _column, _floor: [],
        )


def _table(folder: pathlib.Path, markers: int) -> pathlib.Path:
    """Sixty ordinary numbers and ``markers`` cells wearing MARKER."""
    values = [str(row) for row in range(60)] + [MARKER] * markers
    return fixtures.write(
        folder, "reading.csv", fixtures.single_column_table("reading", values)
    )


def _run(
    folder: pathlib.Path,
    markers: int,
    capsys: pytest.CaptureFixture[str],
) -> "tuple[str, str, str]":
    """One profile run; the screen, the warnings, and the written page."""
    table = _table(folder, markers)
    assert main(["profile", f"{table}", "--missing-value", MARKER]) == 0
    caught = capsys.readouterr()
    page = (folder / "reading-profile.txt").read_text(encoding="utf-8")
    return caught.out, caught.err, page


# -- 1. before they type -----------------------------------------------


def test_the_help_says_the_word_itself_is_written(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A person reads this before deciding what to name."""
    with pytest.raises(SystemExit) as caught:
        main(["profile", "--help"])
    assert caught.value.code == 0
    shown = " ".join(capsys.readouterr().out.split())
    assert "the word itself is written into the description" in shown
    # And it says what that means for the kind of word a researcher
    # would regret naming, in those words, because "a spelling" is not
    # what a person is deciding about.
    assert "a diagnosis, a code or an identifier named here travels" in shown
    # The bound is stated beside the exposure, not instead of it.
    assert f"at least {FLOOR} rows hold it" in shown


# -- 2. before either file exists --------------------------------------


def test_the_notice_names_the_word_its_column_and_its_count(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The screen says what went into the files, in words to act on."""
    _shown, warned, _page = _run(tmp_path, FLOOR + 1, capsys)
    assert "READ THIS BEFORE EITHER OF THESE FILES GOES ANYWHERE." in warned
    said = " ".join(warned.split())
    assert (
        "a word you typed after --missing-value is written into the "
        "description" in said.lower()
    )
    assert f"{MARKER} -- in the column reading, {FLOOR + 1} cell(s)" in said
    # A warning a person cannot act on is the same defect as no warning
    # (the lowered floor's own rule), so it says what to do.
    assert "WHAT TO DO." in warned
    assert "would not put in an email" in warned


def test_the_notice_comes_before_the_files_exist(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Plan P1-D6: a person weighs a file before it is on disk.

    The notice is a warning, so it is on the error stream while the
    confirmation is on the output stream; what is asserted is that the
    run had not yet written anything when it was composed. The two
    streams are ordered against each other by the one thing that is on
    both: nothing is written until after the disclosure, and the "these
    two files will be written" line precedes the "Written:" line.
    """
    table = _table(tmp_path, FLOOR + 1)
    profile_path = tmp_path / "reading-profile.json"
    assert not profile_path.exists()
    assert main(["profile", f"{table}", "--missing-value", MARKER]) == 0
    caught = capsys.readouterr()
    assert MARKER in caught.err
    will_write = caught.out.index("These two files will be written")
    written = caught.out.index("\nWritten:")
    assert will_write < written
    assert profile_path.exists()


def test_nothing_extra_is_said_when_no_word_of_yours_was_written(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Below the floor, nothing of theirs is written and nothing is said.

    A paragraph printed on every ordinary run is a paragraph people stop
    reading. This is the run where the fact is FALSE of the file in
    hand, so the screen says nothing extra -- and the summary's rule
    paragraph, which is printed on every declaring run, still tells the
    person what would have happened at the floor.
    """
    _shown, warned, page = _run(tmp_path, FLOOR - 1, capsys)
    assert "READ THIS BEFORE EITHER OF THESE FILES" not in warned
    assert MARKER not in warned
    assert MARKER not in page
    assert "no column of this one names a word of your own" in page
    # The rule is still stated, so the silence is not read as a promise.
    assert "THE WORD ITSELF is then written into that column's" in page


# -- 3. on the page they are handed ------------------------------------


def test_the_summary_names_the_words_of_yours_it_carries(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A person handed only this file is told which of their words it holds."""
    _shown, _warned, page = _run(tmp_path, FLOOR + 1, capsys)
    said = " ".join(page.split())
    assert "WORDS OF YOUR OWN THAT THIS DESCRIPTION NAMES" in said
    assert f"{MARKER} -- in reading ({FLOOR + 1} cell(s))" in said
    # The false assurance is gone, and its absence is asserted by shape
    # rather than by the sentence, so a reworded return of it is caught
    # by the claim inventory's sixth family and not silently by this.
    assert "will not keep one for you" not in said
    # The scoped claim it replaced is kept, because it is true and it is
    # the reason the settings block is safe to read.
    assert "not written into its settings" in said


def test_the_page_and_the_description_agree_about_the_word(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The words page and machine record cannot disagree about this.

    The summary is built from the description and never from the table,
    so the list it prints is the description's own content said in
    words. Asserted because the defect was exactly a page disagreeing
    with the file beside it.
    """
    _shown, _warned, page = _run(tmp_path, FLOOR + 1, capsys)
    document = (tmp_path / "reading-profile.json").read_text(encoding="utf-8")
    assert MARKER in document
    assert MARKER in page
    # And the settings block still holds none of it, which is the claim
    # the corrected sentences keep.
    settings = document[document.index('"settings"') :]
    assert MARKER not in settings[: settings.index('"source"')]
