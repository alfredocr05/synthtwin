"""The limit the ruling of 2026-08-14 makes the product state about itself.

THE QUESTION PUT TO THE OWNER was whether the validator should defend
against someone submitting hand-crafted descriptions to extract hidden
numbers, and the ruling was: no -- say so honestly instead. Plan
amendment A-P3-13 carries it; the validation method carries it as V5-A1.

WHAT THAT MAKES THIS FILE FOR. A withdrawn guarantee that nobody is told
about is worse than the guarantee, because WITHHELD goes on reading as a
promise it no longer makes. So the honest half of the ruling is a
shipped obligation and is held to like one:

* the quality report says it on EVERY run, at the default floor, beside
  the rule it qualifies -- not in a conditional section and not in a
  plan a reader of the report will never open;
* it says the two things a person can act on: that the rule is about
  what one report says, and that whoever can run the check on a file can
  read that file -- so the control that matters is who holds the file;
* and it does NOT do this by printing anything measured: the paragraph
  is the same words on every description and every file.

The two written surfaces a reader reaches before running anything --
`SECURITY.md`'s residual risks and the README's limits table -- carry it
too, because a person deciding whether the tool is safe to use reads
those and not a report they have not made yet.

THE RED CHECK, and it is two, because these tests read two kinds of
thing. `REINSTATE=A-P3-13-silent` in the environment puts the report
back to the version that stated the rule and not its limit, by dropping
the paragraph from the handling section: measured on the commit that
adds this file, **3 of the 5 fail**, which is every test that reads a
report. The other two read tracked files, so a monkeypatch cannot reach
them; run against copies of `SECURITY.md` and `README.md` with those
sentences taken out, **both fail**, measured the same way.
"""

import os
import pathlib

import pytest

import fixtures
from synthtwin import (
    contract,
    generation,
    profile,
    quality,
    reading,
    rendering,
    taxonomy,
    validation,
)

SEED = 20260814
REPOSITORY = pathlib.Path(__file__).resolve().parent.parent

# What the report owes, in substrings a person would read rather than in
# whole sentences: a test that pinned the paragraph word for word would
# be a second copy of it and would fail on any rewording, including a
# clearer one. Each of these is a load-bearing PART of the ruling, and
# the four together are what a researcher can act on -- the two halves
# of what the rule covers, and the two halves of what it does not.
_OWED = (
    (
        "a question about the one file it",
        "that the report answers about the file it was handed and no other",
    ),
    (
        "a number it does not",
        (
            "that a withheld number is one this report does not print -- "
            "not here, not on the screen, not in a message that stops the "
            "command"
        ),
    ),
    (
        "no copy of the file",
        (
            "that the page is therefore safe to hand to a reader who holds "
            "nothing, which is the whole of what the rule buys"
        ),
    ),
    (
        "again and again",
        (
            "the person it is NOT a barrier against: somebody who has the "
            "file and runs the check repeatedly with descriptions of their "
            "own"
        ),
    ),
    (
        "read the file",
        (
            "the actionable half -- whoever can run this check on a file "
            "can read that file, so who holds the file is the decision "
            "that matters"
        ),
    ),
)


_HEADING = "WHAT WITHHELD PROTECTS, AND WHAT IT DOES NOT"


@pytest.fixture(autouse=True)
def _reinstated(monkeypatch: pytest.MonkeyPatch) -> None:
    """Put back the report that stated the rule and not its limit.

    The paragraph runs from its heading to the end of the section, so
    dropping everything from the heading on is the report exactly as it
    stood before amendment A-P3-13 clause 4.
    """
    if os.environ.get("REINSTATE") != "A-P3-13-silent":
        return
    kept = quality._handling_lines

    def _without_the_limit(description: contract.Profile) -> "list[str]":
        lines = kept(description)
        for index, line in enumerate(lines):
            if _HEADING in line:
                return lines[: max(index - 1, 0)]
        return lines

    monkeypatch.setattr(quality, "_handling_lines", _without_the_limit)


def _quality(folder: pathlib.Path, values: "list[str]") -> str:
    """One ordinary run, at the default floor: describe, build, check."""
    table = fixtures.write(
        folder, "table.csv", fixtures.single_column_table("amount", values)
    )
    read = reading.read_table(
        f"{table}", first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(read, taxonomy.Settings(), [])
    described = contract.load_profile(
        f"{fixtures.write_profile(folder, 'table-profile.json', document)}"
    )
    twin = fixtures.write(
        folder,
        "twin.csv",
        rendering.twin_csv(generation.generate(described, SEED)),
    )
    return quality.quality_report(
        described, validation.measure(described, f"{twin}")
    )


_NUMBERS = [f"{index % 40 + 1}" for index in range(40)] + [
    f"{index % 20 + 1}.5" for index in range(20)
]
_LABELS = ["north" if index % 3 else "south" for index in range(60)]


@pytest.mark.parametrize(
    "values", (_NUMBERS, _LABELS), ids=("numbers", "labels")
)
def test_the_report_states_the_limit_on_an_ordinary_run(
    tmp_path: pathlib.Path, values: "list[str]"
) -> None:
    """Every run, at the default floor, whatever the column is.

    A limit true of every run is printed on every run, which is the rule
    the honest bounds are written under -- and the opposite of amendment
    A-P3-11's conditional lowered-floor section, which exists because it
    is false of an ordinary description. This one is true of all of them.
    """
    folder = tmp_path / "ordinary"
    folder.mkdir()
    report = _quality(folder, values)
    said = _the_paragraph(report)
    assert said, (
        "the quality report has no paragraph headed "
        f"{_HEADING!r} at all, so the limit the owner's ruling of "
        "2026-08-14 requires it to state is not in front of any reader"
    )
    # Read out of the PARAGRAPH and not out of the whole report: a phrase
    # that happens to appear somewhere else on the page is not this
    # paragraph saying it, and a test that accepted one would go green on
    # a report that had dropped the limit entirely.
    missing = [
        f"{owed!r} -- {what_it_is}"
        for owed, what_it_is in _OWED
        if owed not in said
    ]
    assert not missing, (
        "the quality report's own statement of what WITHHELD protects "
        "and what it does not is missing part of it:\n  "
        + "\n  ".join(missing)
        + "\n\nAll five parts are load-bearing. What the rule buys is "
        "worthless to a reader who is not told what it does not buy, "
        "and the reverse: a limit with no statement of the protection "
        "beside it reads as though nothing is protected at all."
    )


def test_the_limit_is_the_same_words_whatever_was_measured(
    tmp_path: pathlib.Path,
) -> None:
    """The paragraph is prose, not a measurement.

    It qualifies the disclosure rule, so it would be a poor joke if it
    carried something measured itself. Two runs on two different columns
    produce the same paragraph, character for character.
    """
    first_folder = tmp_path / "same-a"
    first_folder.mkdir()
    second_folder = tmp_path / "same-b"
    second_folder.mkdir()
    first = _quality(first_folder, _NUMBERS)
    second = _quality(second_folder, _LABELS)
    assert _the_paragraph(first), "the paragraph is not in the report at all"
    assert _the_paragraph(first) == _the_paragraph(second)


def _the_paragraph(report: str) -> str:
    """The limit's own words, from its heading to the end of the report.

    It is the last thing on the page, so the end of the report is the end
    of it -- rather than the first blank line, which would read only the
    first of its two blocks and would go green on a report that had lost
    the second.

    RUNS OF SPACE COLLAPSE, for the reason the claim inventory's own
    reader collapses them: the report is hard-wrapped, and where a line
    happens to break is not something anybody claimed. Without this a
    re-wrap that moved three words to the next line would fail the check
    below while the page said exactly what it said before.
    """
    lines = report.splitlines()
    for index, line in enumerate(lines):
        if _HEADING in line:
            return " ".join(" ".join(lines[index:]).split())
    return ""


def test_security_names_it_as_a_residual_risk() -> None:
    """A person deciding whether to use the tool reads this before a report."""
    text = " ".join(
        (REPOSITORY / "SECURITY.md").read_text(encoding="utf-8").split()
    )
    assert "Named residual risks" in text
    assert "it does not hide them from whoever holds the file" in text, (
        "`SECURITY.md` no longer names the withdrawn defence among the "
        "residual risks, so the one document an institution reads first "
        "does not carry it"
    )


def test_the_readme_limits_table_carries_a_row_for_it() -> None:
    """The limits table is where this project states a design bound."""
    text = (REPOSITORY / "README.md").read_text(encoding="utf-8")
    assert "## Honest limits" in text
    assert "protects the report, not the file" in text, (
        "the README's limits table no longer carries the row for the "
        "defence the owner withdrew"
    )
