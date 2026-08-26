"""Escaping is for a screen, never for a comparison (review P3-V9-F3).

THE DEFECT THIS FILE EXISTS TO KEEP CLOSED. Contract version 4 rewrote a
declared spelling into its printable form before storing it, so the
validator's rule for "does this cell wear a declared word?" put the CELL
through the same boundary before comparing. Version 5 withdrew the
rewriting -- a source spelling is stored character for character and
escaped only where it is PRINTED -- and the comparison was not withdrawn
with it. One side of it had crossed the display boundary and the other
had not.

WHAT THAT COST, measured on a table whose declared marker holds one
invisible character. Sixty numbers, twelve holes spelled `X` U+0001 `Y`,
five blank cells pooled below the floor:

* the rule recognised ZERO of the twelve holes;
* so the column's cells were recounted as though its own description
  read every one of them as a value, and SEVEN style obligations were
  WITHHELD on the very table the description was written from -- seven
  checks that no file could then fail, which the charter calls a defect
  in as many words;
* and on a file that really does violate them -- the same sixty values
  with twelve written `0049` where the description publishes sixty
  plain -- TWO of the obligations it violates were withheld rather than
  MISSED. The report said less about a bad file than it had measured.

WHAT IS NOT CLAIMED. This did not, on any witness built here, let a
non-conforming file exit 0: `styles.exact.leading_zero` and
`styles.published.plain` missed either way. What it did was leave real
violations unevaluated, and leave a conforming file's seven style
obligations standing on a check that could not fail.

THE REPAIR IS TWO LINES AND ONE RULE. The comparison folds the raw
texts, and `validation.py` -- which states verdicts and prints nothing
-- now calls the display boundary NOWHERE. `quality.py` is what puts a
spelling on a screen, and the last test here holds the whole of
`validation.py` to that.

AND THE SWEEP FOUND A SECOND SITE, in code a day old.
`summary.words_of_your_own` escaped a published key before asking
whether it is one of synthtwin's own thirteen words, and returned the
escaped text under a docstring promising the raw one. No page moves a
byte either way -- the whole summary crosses the boundary once, in
`cli`, and crossing it twice changes nothing -- so nothing was visibly
wrong; what was wrong is that the question was put to text the
description does not hold, and the next consumer to compare that answer
with a description's own key would have been the one to find out.

THE RED CHECKS:

* `REINSTATE=P3-V9-F3` -- the comparison escaping the cell again, which
  is the line as it stood. Reds the three measured witnesses.
* `REINSTATE=P3-V9-F3-boundary` -- the source walk pointed at the module
  that legitimately DOES escape, `quality.py`. Reds the boundary test,
  which is how "the validator escapes nothing" is shown to be a
  measurement rather than a walk that cannot see.
* `REINSTATE=P3-V9-F3-summary` -- the summary asking its own vocabulary
  question of escaped text, which is the second site the sweep found.
  Reds the raw-answer test.

Every table here is built by the seeded neutral builders in
`fixtures.py` (plan D13), and every description by the REAL producer.
"""

import ast
import json
import os
import pathlib

import pytest

import fixtures
from synthtwin import contract, parsing, summary, validation
from synthtwin.cli import main

# THE FLOOR THIS FILE ASKS AT. The five blank cells are what pools the
# split below the publication floor, and a pooled split is what puts the
# rule under test on the verdict path at all. Eleven is the floor these
# witnesses were measured at; it used to be the default, and plan
# amendment A-P4-37 (the owner's ruling) moved the default to one, at
# which nothing is held back and no split is ever pooled (contract
# invariant C5-S13). So the floor is now named on the command line
# rather than inherited. The measurements below are unchanged.
FLOOR = 11

# A declared marker carrying a character the display boundary shows.
# Neutral text; the invisible character is written as an escape so that
# no line of this file carries a control character of its own.
MARKER = "X" + chr(1) + "Y"

# The module the last test walks. It is a name rather than a literal so
# that the red check can point the same walk at a module which DOES
# escape -- `quality.py`, whose whole job is putting a spelling on a
# screen -- and prove the walk finds a call when there is one.
WALKED = pathlib.Path(validation.__file__)
PRINTS = pathlib.Path(validation.__file__).parent / "quality.py"


@pytest.fixture(autouse=True)
def _reinstated(monkeypatch: pytest.MonkeyPatch) -> None:
    """Put the escaped comparison back when REINSTATE asks for it."""
    asked = os.environ.get("REINSTATE")
    if asked == "P3-V9-F3":
        monkeypatch.setattr(
            validation,
            "_spelled_alike",
            lambda cell, folded: parsing.folded(parsing.visible(cell))
            in folded,
        )
    if asked == "P3-V9-F3-boundary":
        monkeypatch.setitem(globals(), "WALKED", PRINTS)
    if asked == "P3-V9-F3-summary":
        monkeypatch.setattr(summary, "_raw_text_of", summary._text_of)


def _column(odd: int = 0) -> "list[str]":
    """Sixty numbers, twelve declared holes, five blanks below the floor.

    ``odd`` writes that many of the sixty with a leading zero, which is
    a spelling of the same value in a form the description does not
    publish.
    """
    plain = 60 - odd
    values = [f"{row + 1}" for row in range(plain)]
    values = values + [f"00{row + plain + 1}" for row in range(odd)]
    return values + [MARKER] * 12 + [""] * 5


def _table(folder: pathlib.Path, name: str, odd: int = 0) -> pathlib.Path:
    """The witness table, written out.

    TWO COLUMNS, and the second one is why. A blank cell in a
    one-column CSV is an empty LINE, which the reader drops before any
    column sees it -- and the five blanks are what pools the split below
    the publication floor, which is what puts this rule on the verdict
    path at all. A constant second column keeps every row a row.
    """
    rows = [[cell, "north"] for cell in _column(odd)]
    return fixtures.write(
        folder, name, fixtures.rows_to_csv(["reading", "batch"], rows)
    )


def _describe(folder: pathlib.Path) -> "tuple[pathlib.Path, contract.Profile]":
    """Describe the witness table; return the description path and profile."""
    table = _table(folder, "reading.csv")
    # THE LIST IS ONE LINE ON PURPOSE. `test_description_line_endings`
    # proves that a module handing a description to the loader got it
    # from the fixture or from a real run, and it recognises a real run
    # by the literal `["profile"` this module builds. Split across
    # lines that literal disappears, this module reads as one that
    # composed a description's bytes itself, and that test goes red.
    asked = ["profile", f"{table}", "--missing-value", MARKER,
             "--smallest-group", f"{FLOOR}"]
    assert main(asked) == 0
    written = folder / "reading-profile.json"
    return written, contract.load_profile(f"{written}")


def _counts(report: str) -> "dict[str, int]":
    """The five verdict counts off a written quality report."""
    found: dict[str, int] = {}
    for line in report.splitlines():
        words = line.split()
        if len(words) > 2 and words[1].isupper() and words[0].isdigit():
            found[words[1]] = int(words[0])
    return found


def test_the_rule_recognises_every_hole_the_description_names(
    tmp_path: pathlib.Path,
) -> None:
    """Twelve holes were published; twelve holes are read back."""
    written, description = _describe(tmp_path)
    document = json.loads(written.read_text(encoding="utf-8"))
    block = document["columns"][0]
    assert block["missing_by_source"] == {MARKER: 12}
    # Below the floor, so the split is a fact the description pools --
    # which is what puts this rule on the verdict path at all.
    assert block["n_missing_withheld"] == 5
    holes = validation._holes_by_the_description(
        block,
        _column(),
        validation.kept_spellings(description),
        validation.declared_spellings(description),
    )
    assert sum(1 for hole in holes if hole) == 12


def test_the_table_its_own_description_was_written_from_holds_it_all(
    tmp_path: pathlib.Path,
) -> None:
    """No miss, and nothing withheld: seven checks came back to life."""
    written, _description = _describe(tmp_path)
    table = _table(tmp_path, "same.csv")
    assert main(["validate", f"{written}", "--twin", f"{table}"]) == 0
    counted = _counts((tmp_path / "same-quality.txt").read_text("utf-8"))
    assert counted["MISSED"] == 0
    assert counted["WITHHELD"] == 0


def test_a_file_that_breaks_them_is_told_so(tmp_path: pathlib.Path) -> None:
    """The two obligations that were withheld now carry a verdict."""
    written, _description = _describe(tmp_path)
    other = _table(tmp_path, "other.csv", odd=12)
    assert main(["validate", f"{written}", "--twin", f"{other}"]) == 3
    report = (tmp_path / "other-quality.txt").read_text("utf-8")
    counted = _counts(report)
    assert counted["WITHHELD"] == 0
    assert counted["MISSED"] == 4
    for subcheck in (
        "styles.at-least.plain",
        "styles.remainder",
        "styles.exact.leading_zero",
        "styles.published.plain",
    ):
        assert f"{subcheck} [numeric.numeric_styles]: MISSED" in report


# -- and the rule itself, held to the whole module ---------------------


def _display_boundary_calls(source: str) -> "list[int]":
    """Every line of ``source`` that calls the display boundary."""
    found: list[int] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        named = node.func
        if isinstance(named, ast.Attribute) and named.attr in (
            "visible",
            "visible_lines",
        ):
            found = found + [named.lineno]
    return found


def test_the_validator_never_escapes_anything() -> None:
    """A comparison is not a screen, and this module has no screen.

    Read off the parsed source rather than off the text, so a mention in
    a docstring or a comment -- both of which this module has, and needs
    -- is not what turns the suite red. What would turn it red is a
    call, anywhere in the module, on either side of anything.
    """
    assert _display_boundary_calls(WALKED.read_text("utf-8")) == []
    # ...and the walk finds one when there is one to find, so "none
    # found" is a measurement rather than a walk that cannot see.
    sample = "from synthtwin import parsing\nshown = parsing.visible(text)\n"
    assert _display_boundary_calls(sample) == [2]


def test_the_summary_asks_its_question_of_the_raw_spelling(
    tmp_path: pathlib.Path,
) -> None:
    """The second site the sweep found, and what it promised.

    `summary.words_of_your_own` says in its own docstring that the
    spellings come back RAW, because every caller crosses the display
    boundary itself. It escaped them, and asked the vocabulary question
    of the escaped text. Nothing printed moved -- the boundary is
    idempotent and the page crosses it once -- so this asserts the
    contract the function states rather than the bytes it produces.
    """
    written, _description = _describe(tmp_path)
    document = json.loads(written.read_text(encoding="utf-8"))
    named = summary.words_of_your_own(document)
    assert [spelling for spelling, _column, _count in named] == [MARKER]
    assert named[0][1] == "reading"
    assert named[0][2] == 12
