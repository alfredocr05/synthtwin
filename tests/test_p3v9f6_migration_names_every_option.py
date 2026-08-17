"""The migration refusal names every option, because two of them disclose.

REVIEW ITEM P3-V9-F6; plan amendment A-P3-36; contract 5 section 10.2,
C5-26 as amended.

WHAT WENT WRONG. A version 4 description is refused and the person is
told to describe their table again. The wording that shipped named two
options to repeat -- `--keep-value` and `--missing-value` -- and a
person who does not program does exactly what the sentence says, because
the sentence is the whole of what they were given. Three other options
change what the description says about their table, and two of those
change what it PUBLISHES.

THE ONE THAT MATTERS IS `--smallest-group`, AND IT IS MEASURED BELOW,
not argued. A first run with `--smallest-group 20` over a table holding
a declared marker in twelve cells publishes nothing about that marker:
twelve is under the floor the person chose, so the spelling is pooled
and unnamed. Following the retired advice re-runs at the DEFAULT floor
of eleven, twelve clears it, and the new description names the marker
character for character. The old file withheld a word of the person's
own; the new one publishes it; nothing warned them. The plan called the
result merely "different".

`--identifier` is the same shape and reaches further -- a column named
there publishes no value of the table at all, and a re-run without it
describes those record numbers like any other column -- and it is
measured here too.

WHAT IS ASSERTED, AND THE FIRST OF IT IS NOT A LIST. The options the
message names are compared against the options the SHIPPED PARSER
offers, minus the ones written out below as not being about what a
description says. So an option added to `synthtwin profile` turns this
red on the commit that adds it, and nobody has to remember this file
exists. The two disclosures are then measured through the real
producer, and the message is compared word for word with the contract
clause that fixes it.

THE RED CHECK. `REINSTATE=P3-V9-F6` puts the two-option wording back,
exactly as it shipped, behind the one door every check here reads
through. Every assertion about what the message names goes red with it,
and so does the comparison with the loader's own refusal.
"""

import contextlib
import io
import json
import os
import pathlib
import re

import pytest

import fixtures
from synthtwin import cli, contract, errors, profile, reading, taxonomy

_FOUND = 4
_READS = 5

# The wording as it shipped, for the red check. It is written out rather
# than described, because a reinstatement somebody has to reconstruct is
# a reinstatement nobody runs.
_THE_TWO_OPTION_WORDING = (
    "This description was written by an older version of synthtwin: it "
    "says it is version {found}, and this synthtwin reads version "
    '{reads}. A version {reads} description records which of '
    "synthtwin's own words for \"no value\" you named on the command "
    "line, and a version {found} description does not, so this file "
    "cannot be read back exactly. Please make the description again by "
    "running 'synthtwin profile' on your table, giving the same "
    "--keep-value and --missing-value options you gave the first time, "
    "and use the file it writes exactly as it writes it."
)

# Every long option the shipped parser offers that does NOT change what
# a description says about a table, with the reason beside it. This is
# the only hand-written list here, it is the SUBTRACTION rather than the
# answer, and a new option is not in it -- so a new option lands in the
# set the message is required to name, and this file goes red until
# somebody either names it in the message or classifies it here.
_NOT_ABOUT_THE_DESCRIPTION = {
    "--help": "prints the help and exits; no table is read",
    "--version": "prints the version and exits; no table is read",
    "--twin": "names the file 'validate' measures; 'profile' never sees it",
    "--out-dir": "decides where this command's files go, not what they say",
    "--seed": "chooses which twin 'generate' builds; no description is made",
    "--replace": "lets a run write over names an earlier run left behind",
}


def _message(found: int = _FOUND, reads: int = _READS) -> str:
    """R11's message, or the wording that shipped when asked for it."""
    if os.environ.get("REINSTATE") == "P3-V9-F6":
        return _THE_TWO_OPTION_WORDING.format(found=found, reads=reads)
    return errors.profile_version_is_older(found, reads)


def _options_the_parser_offers() -> "set[str]":
    """Every long option `synthtwin` takes, read from the shipped parser.

    Read from the parser's own help rather than from a list here, for
    the reason the claim inventory reads the command words from it: the
    parser is what a person's typing meets. Only the lines argparse
    starts an option on are read, so an option NAMED in another option's
    help text cannot be mistaken for one the parser takes.
    """
    printed = io.StringIO()
    with (
        contextlib.redirect_stdout(printed),
        contextlib.suppress(SystemExit),
    ):
        cli._parse_arguments(["--help"])
    said = printed.getvalue()
    found = set()
    for line in said.split("\n"):
        if re.match(r"^ {2}-", line):
            found.update(re.findall(r"(?<![\w-])--[a-z][a-z-]*", line))
    assert len(found) >= 8, (
        "The shipped command line no longer lists its options in a form "
        "this test can read, so the comparison below would be made "
        f"against nothing. What it printed was:\n{said}\n"
        "Fix the reading -- never replace it with a hand-written list."
    )
    return found


def _options_the_message_names() -> "set[str]":
    """Every option named in R11's sentence."""
    return set(re.findall(r"(?<![\w-])--[a-z][a-z-]*", _message()))


def test_the_message_names_every_option_that_shapes_a_description() -> None:
    """The set is derived from the parser, so a new option reds this.

    This is the assertion the finding turns on. The message is a list of
    options and a list rots; what stops it rotting is that the list it
    is checked against is the shipped parser's own, minus a subtraction
    each of whose entries says why it is not about the description.
    """
    offered = _options_the_parser_offers()
    stale = sorted(set(_NOT_ABOUT_THE_DESCRIPTION) - offered)
    assert not stale, (
        f"These options are excused from the migration message and the "
        f"parser no longer offers them: {stale}. Take them out of "
        "`_NOT_ABOUT_THE_DESCRIPTION` so the subtraction stays honest."
    )
    owed = offered - set(_NOT_ABOUT_THE_DESCRIPTION)
    named = _options_the_message_names()
    assert named == owed, (
        "The refusal that turns away an older description must name "
        "every option that changes what the description says about the "
        f"table.\n  it names:  {sorted(named)}\n  it owes:   "
        f"{sorted(owed)}\n  missing:   {sorted(owed - named)}\n"
        "Following this message literally is what a person who does not "
        "program will do, and two of the options it owes change what "
        "the description PUBLISHES."
    )


def test_the_message_says_which_options_change_what_is_published() -> None:
    """Naming an option is not the same as saying what leaving it out costs.

    The two that can disclose are named in the sentence that says a left
    out option "can put something into the new description that the old
    one held back". A message that listed five options without that
    sentence would tell a careful person to be careful and a hurried one
    nothing at all.
    """
    said = _message()
    assert "held back" in said, (
        "the message names the options but never says that leaving one "
        "out can publish what the old description withheld"
    )
    for option in ("--smallest-group", "--identifier"):
        head = said.index("held back")
        assert option in said[head:], (
            f"{option} can change what the description publishes and is "
            "not named in the sentence that says so"
        )


def test_the_message_is_the_contract_clause_word_for_word() -> None:
    """C5-26 fixes this text; the two may not drift apart."""
    document = (
        pathlib.Path(__file__).resolve().parents[1]
        / "docs"
        / "spec"
        / "profile-contract-v5.md"
    ).read_text(encoding="utf-8")
    opening = "> This description was written by an older version"
    start = document.index(opening)
    quoted = " ".join(
        line.lstrip("> ").strip()
        for line in document[start : document.index("\n\n", start)].split("\n")
    )
    assert " ".join(quoted.split()) == " ".join(_message().split()), (
        "R11's message and the contract clause that fixes it word for "
        "word have drifted apart. Contract 5 section 10.2 is the "
        "governing text; change it by amendment, then change the code."
    )


def test_the_loader_really_raises_this_message(
    tmp_path: pathlib.Path,
) -> None:
    """The sentence checked above is the sentence a person meets."""
    table = fixtures.single_column_table(
        "reading", [f"{value}.5" for value in range(60)]
    )
    path = fixtures.write(tmp_path, "table.csv", table)
    read = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(read, taxonomy.Settings(), [])
    older = json.loads(json.dumps(document))
    older["profile_version"] = _FOUND
    written = fixtures.write_profile(tmp_path, "older.json", older)
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(f"{written}")
    assert f"{refused.value}" == _message(_FOUND, contract.PROFILE_VERSION)


# -- the two disclosures, measured through the real producer ------------

_MARKER = "MARKERWORD"
_RAISED_FLOOR = 20


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


def _described(
    folder: pathlib.Path,
    stem: str,
    values: "list[str]",
    settings: taxonomy.Settings,
    identifiers: "list[str]",
    name: str = "reading",
) -> dict:
    """One table through the real producer."""
    path = fixtures.write(
        folder, f"{stem}.csv", fixtures.single_column_table(name, values)
    )
    read = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    return profile.build_document(read, settings, identifiers)


def test_leaving_out_the_floor_publishes_what_the_first_run_withheld(
    tmp_path: pathlib.Path,
) -> None:
    """THE FINDING, MEASURED. Same table, same declaration, one option gone.

    Sixty readings and twelve cells wearing a word of the person's own.
    Described once at `--smallest-group 20`, the word is under the floor
    and the description names it nowhere. Described again with only the
    two options the retired message listed -- so at the default floor of
    eleven -- twelve clears it and the description carries the word,
    character for character.

    That is a disclosure and not a difference: the file the person is
    about to hand on now holds a word their first file held back.
    """
    values = _numbers(60) + [_MARKER] * 12
    declared = taxonomy.Settings(declared_missing_values=(_MARKER,))
    raised = taxonomy.Settings(
        small_cell_floor=_RAISED_FLOOR, declared_missing_values=(_MARKER,)
    )
    withheld = _described(tmp_path, "raised", values, raised, [])
    assert _MARKER not in json.dumps(withheld), (
        "the witness is wrong: the raised floor was supposed to pool "
        "this word, and the first description names it"
    )
    again = _described(tmp_path, "default", values, declared, [])
    published = json.loads(json.dumps(again))["columns"][0]
    assert published["missing_by_source"] == {_MARKER: 12}, (
        "the witness is wrong: the default floor was supposed to name "
        "this word, and the second description does not"
    )
    assert _MARKER in json.dumps(again)


def test_leaving_out_the_identifier_publishes_a_column_of_codes(
    tmp_path: pathlib.Path,
) -> None:
    """The second disclosure, at its own size.

    A column named with `--identifier` publishes no value of the table.
    The same column described without it is an ordinary column of
    labels, and its labels are the codes.
    """
    codes = [f"CODE-{value % 6:02d}" for value in range(66)]
    named = _described(
        tmp_path, "as-id", codes, taxonomy.Settings(), ["subject"], "subject"
    )
    assert "CODE-00" not in json.dumps(named), (
        "the witness is wrong: a declared identifier was supposed to "
        "publish no value of the table"
    )
    forgotten = _described(
        tmp_path, "as-labels", codes, taxonomy.Settings(), [], "subject"
    )
    assert "CODE-00" in json.dumps(forgotten)


def test_the_plan_records_this_as_closed_rather_than_open() -> None:
    """The residual it stood as is struck, not left standing beside it.

    An open residual that has been repaired is worse than one that has
    not: the next reader budgets for a defect nobody has any more.
    """
    plan = (
        pathlib.Path(__file__).resolve().parents[1]
        / "docs"
        / "plans"
        / "phase-3-product.md"
    ).read_text(encoding="utf-8")
    assert "Amendment A-P3-36" in plan, (
        "the amendment that took this ruling is not in the plan"
    )
    assert "~~**R-P3-9.**" in plan, (
        "residual R-P3-9 still stands open, and it is closed: strike it "
        "the way R-P3-10 was struck, with the closure recorded"
    )
