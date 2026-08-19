"""The migration refusal names every option, because every one discloses.

REVIEW ITEMS P3-V9-F6 AND P3-V10-F2; plan amendments A-P3-36 and
A-P3-42 clause 1; contract 5 section 10.2, C5-26 as amended twice.

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

AND THEN THE MESSAGE PRICED THE OTHER THREE AS FREE, WHICH IS THE
SECOND FINDING (review item P3-V10-F2). Naming five options and saying
that two of them change what the description PUBLISHES tells a hurried
reader which three they may safely forget. All three publish, and each
is measured below through the real producer, twice, with the two
descriptions compared:

* `--first-row data` on a headerless file whose first line holds a
  code. With the option, the column is `column_1` and the code is one
  free-text value, which a free-text column publishes nowhere. Without
  it, the first line is taken for the column NAMES by convention and
  the code IS the column's name -- published whole, under no floor at
  all, because a column name is not a value of the table.
* `--missing-value -100` where five cells hold `-100`. With it, five
  cells are absent, five is below the floor and the number reaches no
  field. Without it, `-100` is the smallest reading, so it is published
  as the column's minimum and as its first two percentiles.
* `--keep-value` on a word in a counting column. With it, twelve of the
  column's values are not numbers, the column reads as free text and
  publishes nothing at all. Without it, the word is one of synthtwin's
  own thirteen, the column reads as numbers, and the description
  publishes the whole distribution AND the word, character for
  character.

WHAT IS ASSERTED, AND THE FIRST OF IT IS NOT A LIST. The options the
message names are compared against the options the SHIPPED PARSER
offers, minus the ones written out below as not being about what a
description says. So an option added to `synthtwin profile` turns this
red on the commit that adds it, and nobody has to remember this file
exists. The same derived set is then held to the sentence that says
what leaving an option out COSTS, so an option can no longer be named
in the list and excused in the pricing. Every disclosure is then
measured through the real producer, and the message is compared word
for word with the contract clause that fixes it.

THE RED CHECKS. Both put a retired wording back, exactly as it shipped,
behind the one door every check here reads through.

* `REINSTATE=P3-V9-F6` -- the two-OPTION wording. Reds every assertion
  about what the message names and the comparison with the loader's own
  refusal.
* `REINSTATE=P3-V10-F2` -- the five-option wording that priced two of
  them, which is what shipped at HEAD. Reds the pricing assertion and
  the contract comparison, and leaves the naming assertion green --
  which is the finding: naming every option was never the same as
  pricing every option.
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


# The wording that shipped at HEAD: five options named, two priced. It
# is the whole message, written out for the same reason as the one above.
_THE_TWO_PRICED_WORDING = (
    "This description was written by an older version of synthtwin: it "
    "says it is version {found}, and this synthtwin reads version "
    '{reads}. A version {reads} description records which of '
    "synthtwin's own words for \"no value\" you named on the command "
    "line, and a version {found} description does not, so this file "
    "cannot be read back exactly. Please make the description again by "
    "running 'synthtwin profile' on your table, giving it every option "
    "you gave the first time: --keep-value, --missing-value, "
    "--identifier, --smallest-group and --first-row. Each of those "
    "changes how synthtwin reads your table, and two of them change "
    "what the description PUBLISHES about it, so an option you leave "
    "out can put something into the new description that the old one "
    "held back: without the --smallest-group you gave, a value that "
    "fewer rows share can be named, and without the --identifier you "
    "gave, a column of record numbers is described like any other "
    "column. Read the summary page synthtwin writes beside the new "
    "description before either file goes anywhere, and use the "
    "description exactly as synthtwin writes it."
)


def _message(found: int = _FOUND, reads: int = _READS) -> str:
    """R11's message, or the wording that shipped when asked for it."""
    if os.environ.get("REINSTATE") == "P3-V9-F6":
        return _THE_TWO_OPTION_WORDING.format(found=found, reads=reads)
    if os.environ.get("REINSTATE") == "P3-V10-F2":
        return _THE_TWO_PRICED_WORDING.format(found=found, reads=reads)
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


def test_the_message_says_what_leaving_out_each_option_costs() -> None:
    """THE SECOND FINDING (P3-V10-F2). Naming an option is not pricing it.

    The message used to name five options and then say that TWO of them
    change what the description publishes. A hurried reader takes that
    for permission to forget the other three, and all three publish --
    each measured below, through the real producer, on its own witness.

    So the set held to the pricing sentence is the SAME derived set the
    naming assertion above uses: the shipped parser's options minus the
    written-out subtraction. An option cannot now be named in the list
    and excused in the pricing, and a new option lands in both.
    """
    said = _message()
    assert "held back" in said, (
        "the message names the options but never says that leaving one "
        "out can publish what the old description withheld"
    )
    priced = said[said.index("held back") :]
    owed = _options_the_parser_offers() - set(_NOT_ABOUT_THE_DESCRIPTION)
    missing = sorted(option for option in owed if option not in priced)
    assert not missing, (
        "These options change what the description PUBLISHES, and the "
        "sentence that says what leaving an option out costs does not "
        f"mention them: {missing}\n\nEach was measured through the real "
        "producer before this assertion was written; if a new option is "
        "here, measure it the same way and either price it in the "
        "message or show that it changes only the reading."
    )
    # ...and the sentence must not tell the reader that some subset is
    # free. The retired wording's "two of them" is the shape of that.
    assert "two of them change" not in said, (
        "the message is back to pricing a subset of the options it "
        "names, which is what review item P3-V10-F2 found false"
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


# -- the five disclosures, measured through the real producer -----------

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


def _prose(count: int) -> "list[str]":
    """Distinct sentences, so a column of them reads as free text."""
    words = ("alpha", "bravo", "cedar", "delta", "eagle", "flint", "gamma")
    found: list[str] = []
    for index in range(count):
        built = f"the {words[index % len(words)]} reading number {index:03d}"
        found = found + [f"{built} was taken by hand"]
    return found


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


def test_leaving_out_the_first_row_publishes_a_cell_as_a_column_name(
    tmp_path: pathlib.Path,
) -> None:
    """The third disclosure, and it has no floor over it at all.

    A file with no header row whose first line holds a code. Described
    with `--first-row data`, synthtwin names the column itself and the
    code is one free-text value among sixty -- and a free-text column
    publishes no value of the table. Leaving the option out puts the
    first line back in the header, so automatic mode takes it for the
    column NAMES by convention: the code becomes the column's name and
    is published in full.

    It is the widest of the five, because a column NAME is not a value
    of the table and no floor governs one. One cell is enough.
    """
    headerless = "\n".join([_MARKER] + _prose(60)) + "\n"
    path = fixtures.write(tmp_path, "headerless.csv", headerless)
    as_data = profile.build_document(
        reading.read_table(str(path), first_row=reading.FIRST_ROW_DATA),
        taxonomy.Settings(),
        [],
    )
    assert as_data["columns"][0]["name"] == "column_1"
    assert as_data["columns"][0]["role"] == "free_text"
    assert _MARKER not in json.dumps(as_data), (
        "the witness is wrong: a free-text value was supposed to reach "
        "no field of the description"
    )
    forgotten = profile.build_document(
        reading.read_table(str(path), first_row=reading.FIRST_ROW_AUTOMATIC),
        taxonomy.Settings(),
        [],
    )
    assert forgotten["columns"][0]["name"] == _MARKER
    assert _MARKER in json.dumps(forgotten)


def test_leaving_out_the_missing_value_publishes_the_stand_in_number(
    tmp_path: pathlib.Path,
) -> None:
    """The fourth disclosure, and the floor does not stop this one either.

    Sixty readings and five cells holding `-100`, named as "no value".
    Named, the five are absent; five is below the floor, so no field of
    the description holds the number. Left out, `-100` is a reading and
    it is the smallest one, so the description publishes it as the
    column's minimum -- and a percentile is published whatever its count.
    """
    stand_in = "-100"
    values = _numbers(60) + [stand_in] * 5
    named = _described(
        tmp_path,
        "named",
        values,
        taxonomy.Settings(declared_missing_values=(stand_in,)),
        [],
    )
    column = named["columns"][0]
    assert column["n_present"] == 60
    assert column["missing_by_source"] == {}, (
        "the witness is wrong: five cells are under the floor, so the "
        "spelling was supposed to be pooled"
    )
    assert stand_in not in json.dumps(named)
    forgotten = _described(
        tmp_path, "forgotten", values, taxonomy.Settings(), []
    )
    forgotten_column = forgotten["columns"][0]
    assert forgotten_column["n_present"] == 65
    assert forgotten_column["percentiles"]["min"] == -100.0
    assert stand_in in json.dumps(forgotten)


def test_leaving_out_the_keep_value_publishes_a_whole_distribution(
    tmp_path: pathlib.Path,
) -> None:
    """The fifth disclosure, and it is the largest of them.

    Sixty readings and twelve cells holding one of synthtwin's own
    thirteen words, named as REAL DATA. Named, twelve of the column's
    values are not numbers, so the column reads as free text and the
    description publishes not one value of it -- no smallest, no
    largest, no percentile, and not the word. Left out, the word is read
    as "no value", the column reads as numbers, and the description
    publishes the whole distribution of the sixty readings AND the word
    itself, character for character.
    """
    word = " N/A "
    readings = _numbers(60)
    values = readings + [word] * 12
    kept = _described(
        tmp_path,
        "kept",
        values,
        taxonomy.Settings(kept_values=(word,)),
        [],
    )
    column = kept["columns"][0]
    assert column["role"] == "free_text"
    assert column["n_present"] == 72
    written = json.dumps(kept)
    assert word not in written
    assert readings[0] not in written, (
        "the witness is wrong: a free-text column was supposed to "
        "publish no value of the table"
    )
    forgotten = _described(
        tmp_path, "forgotten-keep", values, taxonomy.Settings(), []
    )
    forgotten_column = forgotten["columns"][0]
    assert forgotten_column["role"] == "continuous"
    assert forgotten_column["missing_by_source"] == {word: 12}
    written_again = json.dumps(forgotten)
    assert word in written_again
    assert forgotten_column["percentiles"]["max"] == float(max(
        float(value) for value in readings
    ))


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
