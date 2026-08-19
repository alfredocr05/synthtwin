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
* `REINSTATE=P3-V10-F7` -- the notice moved to AFTER the write and
  before the "Written:" confirmation, which is review item P3-V10-F7's
  own mutation. The screen it produces is the screen this file used to
  assert: the marker is on the error stream, "These two files will be
  written" still precedes "Written:", and the profile exists when the
  run returns. It reds only the check that watches the folder while the
  notice is being said.
* `REINSTATE=P3-V10-F9` -- the word count taken from the LENGTH of the
  list of spellings, which is what both surfaces counted. Reds the two
  attribution checks at the end of this file, and nothing else: the
  defect was never about which spellings are disclosed.

WHO TYPED WHICH OF THESE WORDS IS PART OF TELLING THE TRUTH ABOUT THEM
(review item P3-V10-F9). One `--missing-value XX` over a table holding
`XX` cells and `" xx "` cells publishes TWO spellings, because the cells
decide the spellings and the person decides the word. Both surfaces
counted the spellings and wrote the sentence about the person: "Words
you typed after --missing-value are written into the description", and
then told them to run again without naming "them". The disclosure was
complete and the attribution was wrong, which sends a careful reader
looking for an option they never gave.

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
    if asked == "P3-V10-F7":
        # The reviewer's own mutation, built rather than described: the
        # notice is held back at the point production composes it and
        # said again once both files are on disk. Nothing else about the
        # run changes -- same words, same stream, still before the
        # "Written:" line -- which is exactly why a check that reads the
        # finished screen cannot tell the two runs apart.
        from synthtwin import profile as producer

        held: list[str] = []
        compose = cli._declared_words_notice
        write = producer.write_both_files

        def _hold_it_back(named: "list[tuple[str, str, int]]") -> str:
            held.append(compose(named))
            return ""

        def _write_then_say(*given: object, **named: object) -> object:
            left_behind = write(*given, **named)  # type: ignore[arg-type]
            for message in held:
                cli._warn(message)
            return left_behind

        monkeypatch.setattr(cli, "_declared_words_notice", _hold_it_back)
        monkeypatch.setattr(producer, "write_both_files", _write_then_say)
    if asked == "P3-V10-F9":
        # The count as both surfaces took it: how many LINES there are,
        # which is how many spellings the description names.
        monkeypatch.setattr(summary, "words_behind", len)


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
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Plan P1-D6: a person weighs a file before it is on disk.

    THIS WATCHES THE FOLDER WHILE THE NOTICE IS BEING SAID, and review
    item P3-V10-F7 is why. The check this replaces read the finished
    screen: the marker was somewhere on the error stream, "These two
    files will be written" came before "Written:", and the profile
    existed when the run returned. Every one of those is still true of a
    run that writes both files FIRST and warns afterwards -- the notice
    and the confirmation are on different streams, so their order is not
    on the transcript at all, and the two lines that are ordered are
    both synthtwin's own words about what it is going to do. So the test
    asserted a promise it could not see, on the one screen where the
    promise matters: a watched or synchronised output folder has the
    real-derived files before the person has been told what is in them.

    What is observed instead is the folder itself, at the instant
    `_warn` is handed the notice. `REINSTATE=P3-V10-F7` builds the
    reviewer's mutation and this is the only assertion that moves.
    """
    table = _table(tmp_path, FLOOR + 1)
    profile_path = tmp_path / "reading-profile.json"
    summary_path = tmp_path / "reading-profile.txt"
    assert not profile_path.exists()

    seen: list[tuple[str, tuple[str, ...]]] = []
    warn = cli._warn

    def _watch(message: str) -> None:
        # The whole folder, not the two names: a run that had begun
        # writing under a working name would leave real-derived bytes in
        # the same place, and "the file does not exist yet" is not what
        # a person is promised. They are promised that nothing of theirs
        # is there yet.
        seen.append(
            (message, tuple(sorted(item.name for item in tmp_path.iterdir())))
        )
        warn(message)

    monkeypatch.setattr(cli, "_warn", _watch)
    assert main(["profile", f"{table}", "--missing-value", MARKER]) == 0

    # EVERYTHING THE OLD CHECK ASSERTED, ASSERTED FIRST AND ON PURPOSE.
    # All three are still true and still worth holding, and none of them
    # orders the notice against the write -- which is the whole of
    # P3-V10-F7. Under `REINSTATE=P3-V10-F7` these pass and the
    # observation below is the only thing that moves, so the red run is
    # itself the evidence that the old check could not see the defect.
    caught = capsys.readouterr()
    assert MARKER in caught.err
    will_write = caught.out.index("These two files will be written")
    written = caught.out.index("\nWritten:")
    assert will_write < written
    assert profile_path.exists() and summary_path.exists()

    at_the_notice = [holding for message, holding in seen if MARKER in message]
    assert len(at_the_notice) == 1, (
        "The notice naming the declared word was said "
        f"{len(at_the_notice)} time(s). It is said exactly once, before "
        "the write; a run that says it never has nothing to observe and "
        "a run that says it twice has stopped being the disclosure this "
        f"file asserts.\n  warnings seen: {[said for said, _ in seen]}"
    )
    assert at_the_notice[0] == (table.name,), (
        "When the declared-word notice was handed to the screen, the "
        "output folder already held more than the table it was built "
        f"from: {at_the_notice[0]}. Plan P1-D6 puts BOTH warnings before "
        "`write_both_files` for one reason -- a person weighs what a "
        "file carries before it exists, not after -- and a folder that "
        "is watched, synchronised or shared has the file the moment it "
        "is written. Move the notice back above the write."
    )


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


# -- 4. one word, two spellings: who typed which ------------------------


def _two_spellings(
    folder: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> "tuple[str, str]":
    """One declaration whose cells wore it two ways; the screen and the page.

    `--missing-value` is given ONCE. The table writes the marker plainly
    in one group of cells and with edge space and a different case in
    another, and both groups clear the floor, so the description names
    two spellings of one word.
    """
    values = (
        [str(row) for row in range(60)]
        + [MARKER] * FLOOR
        + [f" {MARKER.upper()} "] * FLOOR
    )
    table = fixtures.write(
        folder, "reading.csv", fixtures.single_column_table("reading", values)
    )
    assert main(["profile", f"{table}", "--missing-value", MARKER]) == 0
    caught = capsys.readouterr()
    return caught.err, (folder / "reading-profile.txt").read_text(
        encoding="utf-8"
    )


def test_the_notice_counts_the_words_you_typed_not_the_spellings(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """THE FINDING (review item P3-V10-F9). One word, two lines, one sentence.

    Both spellings are disclosed -- that half was never wrong and is
    asserted here so a repair cannot quietly drop one. What changes is
    that the notice speaks about the person in the singular, because one
    is the number of options they gave, and says outright where the
    second line came from.
    """
    warned, _page = _two_spellings(tmp_path, capsys)
    said = " ".join(warned.split())
    assert MARKER in said and MARKER.upper() in said, (
        "a spelling the description carries is missing from the notice"
    )
    assert (
        "a word you typed after --missing-value is written into the "
        "description" in said.lower()
    ), (
        "the notice counts the spellings the table wrote as though the "
        "person had typed each of them:\n" + warned
    )
    assert "You typed one word" in said, (
        "the notice lists two spellings and never says that one of them "
        "is the table's own"
    )
    assert "without naming that word" in said, (
        "the instruction still tells the person to stop naming several "
        "words when they named one"
    )


def test_the_page_counts_the_words_you_typed_not_the_spellings(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The same on the file a person is handed, which is the one they read."""
    _warned, page = _two_spellings(tmp_path, capsys)
    listed = [line for line in page.split("\n") if "-- in reading" in line]
    assert listed == [
        f"       {MARKER.upper()}  -- in reading ({FLOOR} cell(s))",
        f"      {MARKER} -- in reading ({FLOOR} cell(s))",
    ], (
        "the page no longer lists both spellings with their edge space "
        f"as the table wrote them:\n{listed}"
    )
    said = " ".join(page.split())
    assert "WORDS OF YOUR OWN THAT THIS DESCRIPTION NAMES" in said
    assert "this word of yours is written into it" in said, (
        "the page counts the spellings as words the person named:\n" + page
    )
    assert "more lines there than words you named" in said, (
        "the page lists two spellings of one word and does not say so"
    )


def test_two_real_declarations_are_still_counted_as_two(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The over-narrowing check: a plural sentence where it is true.

    Without this, a repair that made every notice singular would pass
    the two checks above.
    """
    second = "another-marker-of-my-own"
    values = (
        [str(row) for row in range(60)]
        + [MARKER] * FLOOR
        + [second] * FLOOR
    )
    table = fixtures.write(
        tmp_path, "reading.csv", fixtures.single_column_table("reading", values)
    )
    assert (
        main(
            [
                "profile",
                f"{table}",
                "--missing-value",
                MARKER,
                "--missing-value",
                second,
            ]
        )
        == 0
    )
    caught = capsys.readouterr()
    said = " ".join(caught.err.split())
    assert "2 words you typed after --missing-value are written" in said
    assert "without naming those words" in said
    assert "more lines than words" not in said, (
        "two words came back under two spellings, so nothing here is "
        "the table's own spelling of somebody else's word"
    )
    page = " ".join(
        (tmp_path / "reading-profile.txt").read_text(encoding="utf-8").split()
    )
    assert "these 2 words of yours are written into it" in page
