"""P1-R7-F2 (neighbour): every sentence of the disclosure is checked.

The repair for P1-R7-F2 kept the declared spellings out of the settings
block and added a paragraph telling the person so. The paragraph then
said more than that:

    "The values themselves are NOT written into the profile or into
    this summary. A value you typed is a value of your table -- that
    is why you typed it -- so it is held back like every other value."

That is false. A column of 200 readings with three cells of `-999`,
profiled with `--keep-value -999`, prints `smallest: -999.0` a few lines
above the paragraph that says the value is held back.

The publication is RIGHT and is not touched here. `--keep-value` means
"this is real data, not a missing marker", so `-999` becomes an ordinary
number of that column, and every column of numbers publishes a real
smallest and a real largest -- that is what a range is. Suppressing it,
or taking declared values out of the statistics, would misdescribe the
column and defeat the option.

What was wrong was the CLAIM, so the claim is what changed. Each test
below pins one statement of the replacement paragraph against what the
code actually does, in both directions:

* the settings record counts and the matching rule, never a spelling
  OF THE PERSON'S OWN -- and, from contract version 5, which members of
  synthtwin's own thirteen published words were among the values typed
  (that contract's section 6; plan amendment A-P3-27, which states the
  size of that lowering and prices it). The tests below check both
  halves: the member is written in SYNTHTWIN's spelling, and a word
  that is not on synthtwin's list is still written nowhere in the
  settings -- which is a claim about that block and about nothing else,
  because such a word DOES reach its column's `missing_by_source`
  (review item P3-V9-F1, plan amendment A-P3-31);
* a value declared MISSING is counted absent, and its spelling is listed
  by its column among the spellings counted as missing -- under the same
  small-cell floor, and only where that column publishes values at all;
* a value declared KEPT is data from that point on: it can be the
  smallest or largest number of a column of numbers HOWEVER FEW rows
  hold it, and it can be a LABEL of a column of categories only when at
  least `small_cell_floor` rows share it;
* a column that publishes nothing publishes nothing either way.

A person deciding whether to move this file has to be able to trust the
paragraph exactly. Overclaiming safety is worse than claiming less.
"""

import json
import pathlib

import pytest

import fixtures
from synthtwin import profile, taxonomy
from synthtwin.cli import main

FLOOR = taxonomy.Settings().small_cell_floor
SENTINEL = "-999"


def _run(
    tmp_path: pathlib.Path,
    name: str,
    values: "list[str]",
    options: "list[str]",
) -> "tuple[dict, str, str]":
    """Profile one column through the command; return document, JSON, summary."""
    text = fixtures.single_column_table(name, values)
    table = fixtures.write(tmp_path, f"{name}.csv", text)
    assert main(["profile", f"{table}"] + options) == 0
    written = (tmp_path / f"{name}-profile.json").read_text(encoding="utf-8")
    summary_text = (tmp_path / f"{name}-profile.txt").read_text(
        encoding="utf-8"
    )
    document = json.loads(written)
    assert isinstance(document, dict)
    return (document, written, summary_text)


def _declaration_paragraph(summary_text: str) -> str:
    """The block of the summary about the values the person named.

    The line breaks are taken out. What is checked here is what the
    paragraph SAYS; where its lines happen to end is layout, and a test
    that fails when a sentence is re-wrapped teaches its author to stop
    reading it.
    """
    start = summary_text.index("Values you named yourself")
    return " ".join(summary_text[start:].split())


# -- what version 5 added, and the bound on it -------------------------


def test_a_named_word_is_recorded_the_same_whether_or_not_it_occurs(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Contract 5 C5-16: the lists are a function of the command line.

    This is the property that keeps the two lists from being evidence
    ABOUT THE TABLE. A word somebody names but no cell wears is recorded
    exactly as one every cell wears, so a reader of the field sees what
    rule the run applied and nothing about the rows it ran over.
    """
    readings = [f"{index}" for index in range(1, 201)]
    (tmp_path / "held").mkdir()
    (tmp_path / "absent").mkdir()
    held, _written, _summary = _run(
        tmp_path / "held",
        "reading",
        readings + [SENTINEL] * 20,
        ["--missing-value", SENTINEL],
    )
    capsys.readouterr()
    absent, _written_two, _summary_two = _run(
        tmp_path / "absent",
        "reading",
        readings,
        ["--missing-value", SENTINEL],
    )
    capsys.readouterr()
    assert held["settings"]["declared_missing_values"] == (
        absent["settings"]["declared_missing_values"]
    )
    assert absent["settings"]["declared_missing_values"][
        "built_in_numbers"
    ] == [-999.0]


def test_only_a_member_of_synthtwins_own_list_is_ever_written(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Contract 5 C5-17 and C5-K1, from the other side.

    Three values are named: one of synthtwin's spellings typed with the
    person's own capitals and spacing, one of synthtwin's stand-in
    numbers typed with trailing zeros, and a word that is nobody's but
    the person's. The document holds the two MEMBERS, in synthtwin's
    spelling, and nothing at all of the third.
    """
    readings = [f"{index}" for index in range(1, 201)]
    document, written, _summary = _run(
        tmp_path,
        "reading",
        readings,
        [
            "--keep-value",
            " N/A ",
            "--keep-value",
            "-999.00",
            "--missing-value",
            "wombat",
        ],
    )
    capsys.readouterr()
    assert document["settings"]["kept_values"] == {
        "built_in_dates": [],
        "built_in_numbers": [-999.0],
        "built_in_texts": ["n/a"],
        "n_declared": 2,
        "values_recorded": False,
    }
    assert document["settings"]["declared_missing_values"] == {
        "built_in_dates": [],
        "built_in_numbers": [],
        "built_in_texts": [],
        "n_declared": 1,
        "values_recorded": False,
    }
    assert " N/A " not in written
    assert "-999.00" not in written
    assert "wombat" not in written


# -- the retired claim -------------------------------------------------


def test_the_paragraph_no_longer_says_a_declared_value_is_held_back(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    readings = [f"{index}" for index in range(1, 201)]
    _document, _written, summary_text = _run(
        tmp_path, "reading", readings + [SENTINEL] * 3, ["--keep-value", SENTINEL]
    )
    capsys.readouterr()
    said = _declaration_paragraph(summary_text)
    for retired in (
        "NOT written into the profile",
        "held back like",
        "is a value of your",
    ):
        assert retired not in said, (
            f"the paragraph claims {retired!r} again, and the run it is "
            f"printed in publishes the declared value as this column's "
            f"smallest number"
        )


# -- the kept direction ------------------------------------------------


def test_a_kept_number_is_published_as_the_smallest_and_the_words_say_so(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The reviewer's exact probe: three rows out of 203, far below the
    # floor, and the range is a real range so the value is in it.
    readings = [f"{index}" for index in range(1, 201)]
    document, _written, summary_text = _run(
        tmp_path, "reading", readings + [SENTINEL] * 3, ["--keep-value", SENTINEL]
    )
    capsys.readouterr()
    column = document["columns"][0]
    assert column["n_missing"] == 0
    assert column["percentiles"]["min"] == -999.0
    assert "smallest: -999.0" in summary_text
    assert 3 < FLOOR, "the point of this case is that it is below the floor"
    # And the paragraph the person reads describes exactly that.
    said = _declaration_paragraph(summary_text)
    assert "smallest or largest number" in said
    assert "however few rows hold it" in said


def test_a_kept_label_is_published_only_at_or_above_the_floor(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The categorical direction, asked in both halves. Above the floor
    # the kept value is an ordinary label of the column; below it, the
    # ordinary small-cell rule holds it back and counts it as withheld.
    plenty = ["north"] * 60 + ["south"] * 60 + ["NA"] * 20
    document, _written, summary_text = _run(
        tmp_path, "region", plenty, ["--keep-value", "NA"]
    )
    capsys.readouterr()
    column = document["columns"][0]
    assert column["role"] == taxonomy.ROLE_CATEGORICAL
    labels = [level["label"] for level in column["levels"]]
    assert "na" in labels, (
        "a kept value at or above the floor is a label of its column "
        "like any other, and the paragraph says so"
    )
    assert column["suppressed_levels"] == 0
    assert "na (20)" in summary_text
    said = _declaration_paragraph(summary_text)
    assert f"labels of a column of categories if at least {FLOOR} rows share it" in said


def test_a_kept_label_below_the_floor_is_withheld_like_any_other(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    scarce = ["north"] * 60 + ["south"] * 60 + ["NA"] * 3
    document, written, summary_text = _run(
        tmp_path, "region", scarce, ["--keep-value", "NA"]
    )
    capsys.readouterr()
    column = document["columns"][0]
    labels = [level["label"] for level in column["levels"]]
    assert labels == ["north", "south"]
    assert column["suppressed_levels"] == 1
    assert "na" not in json.dumps(column["levels"])
    assert '"NA"' not in written
    assert "values left out because too few rows share them: 1" in summary_text


# -- the declared-missing direction ------------------------------------


def test_a_declared_missing_spelling_is_listed_by_its_column(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # This is the half the first wording got wrong in the other
    # direction: a declared MISSING value is not silent either. Its rows
    # are counted, and its spelling is listed among the spellings the
    # column counted as missing, on the ordinary floor.
    readings = [f"{index}" for index in range(1, 201)]
    document, _written, summary_text = _run(
        tmp_path,
        "reading",
        readings + [SENTINEL] * 20,
        ["--missing-value", SENTINEL],
    )
    capsys.readouterr()
    column = document["columns"][0]
    assert column["n_missing"] == 20
    assert column["missing_by_source"] == {SENTINEL: 20}
    assert column["percentiles"]["min"] == 1.0, (
        "a value declared missing is absent, so it is not in the range"
    )
    assert f"counted as missing: {SENTINEL} (20)" in summary_text
    said = _declaration_paragraph(summary_text)
    assert "counted as absent" in said
    assert f"if at least {FLOOR} rows share that spelling" in said


def test_a_declared_missing_spelling_below_the_floor_is_pooled(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    readings = [f"{index}" for index in range(1, 201)]
    document, _written, summary_text = _run(
        tmp_path,
        "reading",
        readings + [SENTINEL] * 3,
        ["--missing-value", SENTINEL],
    )
    capsys.readouterr()
    column = document["columns"][0]
    assert column["n_missing"] == 3
    assert SENTINEL not in json.dumps(column["missing_by_source"])
    assert column["n_missing_withheld"] == 3
    # THE COLUMN NAMES IT NOWHERE, which is the floor doing its work and
    # is what this test is about. The settings block DOES record that
    # one of synthtwin's own three stand-in numbers was named, and that
    # is the stated lowering of contract version 5 rather than a leak:
    # it says which of thirteen fixed words was typed, and nothing about
    # this column, this count or these three rows.
    assert document["settings"]["declared_missing_values"][
        "built_in_numbers"
    ] == [-999.0]
    for block in document["columns"]:
        assert SENTINEL not in json.dumps(block)
    # The pooled group is counted and said to be pooled; the spelling is
    # not named and the pooled NAME is not printed as though it were one
    # (review of the shipped reports, 2026-08-15).
    assert "counted as missing: 3 cell(s) whose spelling is not named" in (
        summary_text
    )
    assert "(withheld)" not in summary_text


def test_a_column_that_publishes_nothing_publishes_nothing_either_way(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    narrative = fixtures.prose(60)
    token = "withheld-token-417"
    document, written, summary_text = _run(
        tmp_path,
        "narrative",
        narrative + [token] * 20,
        ["--missing-value", token],
    )
    capsys.readouterr()
    column = document["columns"][0]
    assert column["role"] == taxonomy.ROLE_TEXT
    assert column["n_missing"] == 20
    assert column["missing_by_source"] == {}, (
        "20 rows is above the floor, so the ROLE is what withholds this "
        "spelling -- which is the claim the paragraph makes"
    )
    assert token not in written
    assert token not in summary_text
    said = _declaration_paragraph(summary_text)
    assert "A column that publishes nothing" in said


# -- the settings, in every one of those runs --------------------------


@pytest.mark.parametrize(
    "options",
    [
        ["--keep-value", SENTINEL],
        ["--missing-value", SENTINEL],
        ["--keep-value", SENTINEL, "--missing-value", "unknown"],
    ],
)
def test_the_settings_carry_counts_and_never_a_spelling(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    options: "list[str]",
) -> None:
    readings = [f"{index}" for index in range(1, 201)]
    document, _written, _summary_text = _run(
        tmp_path, "reading", readings + [SENTINEL] * 20, options
    )
    capsys.readouterr()
    recorded = document["settings"]
    assert "values_recorded" in json.dumps(recorded["kept_values"])
    assert recorded["kept_values"]["values_recorded"] is False
    assert recorded["declared_missing_values"]["values_recorded"] is False
    # THE PERSON'S OWN WORD IS STILL NOWHERE. `unknown` is on no list of
    # synthtwin's, so no count, no list and no key carries it -- which
    # is the half of the Phase 1 rule contract version 5 does not touch.
    assert "unknown" not in json.dumps(recorded)
    # AND WHAT IS CARRIED IS ONE OF SYNTHTWIN'S OWN THIRTEEN, written in
    # synthtwin's own form. The person typed `-999`; the document holds
    # the number `-999.0`, which is the vocabulary member.
    named = (
        recorded["kept_values"]["built_in_numbers"]
        + recorded["declared_missing_values"]["built_in_numbers"]
    )
    assert named == [-999.0]


def test_the_recorded_policy_names_its_own_scope(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The machine-readable half of the same honesty. The token said
    # `counts_only_no_spellings`, which reads as a claim about the whole
    # document -- and the same document publishes the kept value as this
    # column's smallest number. A consumer or an auditor reading the
    # token must not be able to draw the wider conclusion.
    readings = [f"{index}" for index in range(1, 201)]
    document, _written, _summary_text = _run(
        tmp_path, "reading", readings + [SENTINEL] * 3, ["--keep-value", SENTINEL]
    )
    capsys.readouterr()
    assert document["columns"][0]["percentiles"]["min"] == -999.0
    token = document["settings"]["declaration_publication"]
    assert token == profile.DECLARATION_PUBLICATION
    assert token == "settings_counts_only_columns_unchanged"
    assert "no_spellings" not in token, (
        "the token sits in a document that publishes a declared value, "
        "so it may not read as a claim about the document"
    )


# -- only the direction that was used is described ---------------------


def test_only_the_direction_the_person_used_is_described(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    readings = [f"{index}" for index in range(1, 201)]
    _document, _written, kept_only = _run(
        tmp_path, "reading", readings + [SENTINEL] * 3, ["--keep-value", SENTINEL]
    )
    capsys.readouterr()
    said = _declaration_paragraph(kept_only)
    assert "named as real data IS data from then on" in said
    assert "counted as absent" not in said

    _document, _written, missing_only = _run(
        tmp_path,
        "other",
        readings + [SENTINEL] * 20,
        ["--missing-value", SENTINEL],
    )
    capsys.readouterr()
    said = _declaration_paragraph(missing_only)
    assert "counted as absent" in said
    assert "IS data from then on" not in said


def test_both_directions_are_described_when_both_were_used(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    readings = [f"{index}" for index in range(1, 201)]
    document, _written, summary_text = _run(
        tmp_path,
        "reading",
        readings + [SENTINEL] * 3 + ["0"] * 15,
        ["--keep-value", SENTINEL, "--missing-value", "0"],
    )
    capsys.readouterr()
    column = document["columns"][0]
    # One declaration put a value into the range; the other took 15 rows
    # out of it. The paragraph has to carry both rules, and say they are
    # two rules rather than one said twice.
    assert column["percentiles"]["min"] == -999.0
    assert column["missing_by_source"] == {"0": 15}
    said = _declaration_paragraph(summary_text)
    assert "the two directions do not work the same way" in said
    assert "counted as absent" in said
    assert "IS data from then on" in said


def test_nothing_of_this_is_printed_when_nothing_was_declared(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    readings = [f"{index}" for index in range(1, 201)]
    _document, _written, summary_text = _run(tmp_path, "reading", readings, [])
    capsys.readouterr()
    assert "Values you named yourself" not in summary_text


# -- the same claim on the help screen ---------------------------------


def test_the_option_help_does_not_claim_a_declared_value_is_withheld(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The help screen carried the same false sentence, in fewer words:
    # "The value you type is not written into the profile -- it is a
    # value of your table, so it is held back like any other."
    with pytest.raises(SystemExit) as caught:
        main(["profile", "--help"])
    assert caught.value.code == 0
    # argparse wraps the help text to the width of the screen, so the
    # sentences are checked with the line breaks taken out.
    shown = " ".join(capsys.readouterr().out.split())
    assert "--keep-value" in shown and "--missing-value" in shown
    assert "held back like any other" not in shown
    assert "not written into the profile" not in shown
    # DIFFERENT values since 2026-08-17, because the count folds two
    # spellings of one value into one declaration (review item
    # P3-V9-F7, plan amendment A-P3-37).
    assert "records how many different values you named" in shown
    assert "wherever its column publishes values" in shown
    # AND THE HELP STOPPED SAYING THE PROFILE RECORDS NO VALUE AT ALL
    # (plan amendment A-P3-30). Both options carried "never the values
    # themselves" for three stages after contract version 5 began
    # recording which of synthtwin's own thirteen words were typed --
    # so the screen a person reads BEFORE deciding what to type
    # contradicted `SECURITY.md`, the profile's own summary and the
    # settings block itself. The claim that survives is the one
    # contract 5 section 6 holds to: a word of the person's own is
    # never written into the settings.
    assert "never the values themselves" not in shown
    assert shown.count("a word of your own is never written") == 2
    assert shown.count("one of synthtwin's own words for 'no value'") == 2
