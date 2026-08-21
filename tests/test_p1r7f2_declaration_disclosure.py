"""P1-R7-F2: a declared value obeys the publication rules like any other.

The serialized settings recorded --keep-value and --missing-value
verbatim. A rare narrative value supplied as `--missing-value` was
therefore written into the profile even though the column holding it
was free text and published nothing at all, and the summary said
nothing about it: a real source value crossed the boundary through the
settings block, around every suppression rule.

The rule now, stated once and applied at the rule rather than at the
symptom: the SETTINGS BLOCK carries the POLICY and never a spelling --
how many values were named each way, and the matching rule in force. The
block still has a key for every field of Settings, so a profile still
says which rules produced it; what it no longer does is reproduce a
value out of every column at once.

The rule stops there, and this file states its boundary rather than
leaving it to be assumed. Declaring a value does not withdraw it from
its own column: a KEPT value is data from that point on and is described
wherever its column publishes values, and a value declared MISSING is
counted absent with its spelling listed by its column under the same
floor and role rules as any other missing spelling. The tests below that
touch a column's own publication say which of the two they are checking;
`test_p1r7f2_disclosure_is_true.py` holds the battery for the sentences
the person reads about it.

The disclosure battery here covers the COMPLETE serialized document and
the complete summary text, using the exact spelling the person typed --
which is what the older check did not do, because it looked at the
file's spelling of the same number and not at the raw setting.
"""

import json
import pathlib

import pytest

import fixtures
from synthtwin import profile, reading, summary, taxonomy
from synthtwin.cli import main

SETTINGS = taxonomy.Settings()

# The reviewer's own column and value.
NARRATIVE = fixtures.prose(60)
RARE_TOKEN = "withheld-token-417"


def _run(
    tmp_path: pathlib.Path,
    name: str,
    values: "list[str]",
    options: "list[str]",
    capsys: pytest.CaptureFixture[str],
) -> "tuple[dict, str, str]":
    """Profile one column through the command; return document, JSON, screen."""
    text = fixtures.single_column_table(name, values)
    table = fixtures.write(tmp_path, f"{name}.csv", text)
    assert main(["profile", f"{table}"] + options) == 0
    shown = capsys.readouterr().out
    written = (tmp_path / f"{name}-profile.json").read_text(encoding="utf-8")
    summary_text = (tmp_path / f"{name}-profile.txt").read_text(
        encoding="utf-8"
    )
    document = json.loads(written)
    assert isinstance(document, dict)
    # The screen and the written summary are one text, so checking the
    # spelling in one of them checks it in the other.
    assert summary_text in shown
    return (document, written, summary_text)


# -- the reviewer's exact case ----------------------------------------


def test_a_declared_value_never_reaches_the_settings_block(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    document, written, summary_text = _run(
        tmp_path,
        "narrative",
        NARRATIVE + [RARE_TOKEN],
        ["--missing-value", RARE_TOKEN],
        capsys,
    )
    column = document["columns"][0]
    assert column["role"] == taxonomy.ROLE_TEXT
    assert column["n_missing"] == 1
    assert column["missing_by_source"] == {}
    # The whole document, not the role block: this is where it escaped.
    assert RARE_TOKEN not in written
    assert RARE_TOKEN not in summary_text
    # The rare token is the person's own word, so neither vocabulary
    # list carries it and the count is still the whole of what the
    # settings block says (contract 5 C5-17).
    assert document["settings"]["declared_missing_values"] == {
        "built_in_numbers": [],
        "built_in_texts": [],
        "n_declared": 1,
        "values_recorded": False,
    }


def test_a_declaration_cannot_republish_a_below_floor_label(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The reviewer's second route: 99 `common` cells and one rare label.
    # Small-cell suppression keeps the rare spelling out of
    # missing_by_source; the setting used to put it back.
    values = ["common"] * 99 + ["rare-label"]
    document, written, summary_text = _run(
        tmp_path,
        "group",
        values,
        ["--missing-value", "rare-label"],
        capsys,
    )
    column = document["columns"][0]
    assert column["n_missing"] == 1
    assert "rare-label" not in json.dumps(column["missing_by_source"])
    assert "rare-label" not in written
    assert "rare-label" not in summary_text


def test_a_declaration_cannot_publish_a_value_of_a_named_identifier(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # A column the person declared with --identifier publishes no value
    # at all. A declaration naming one of its values must not be the way
    # round that.
    values = [f"CASE_REF-{index:05d}" for index in range(40)] + ["CASE_REF-99999"] * 5
    document, written, summary_text = _run(
        tmp_path,
        "record_code",
        values,
        ["--identifier", "record_code", "--missing-value", "CASE_REF-99999"],
        capsys,
    )
    assert document["columns"][0]["role"] == taxonomy.ROLE_IDENTIFIER
    assert "CASE_REF-99999" not in written
    assert "CASE_REF-99999" not in summary_text


def test_a_kept_value_stays_out_of_the_settings_and_stays_in_its_column(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # --keep-value goes the other way: it makes a value data rather than
    # a hole. The SETTINGS still record only the count -- that is this
    # item's rule -- while the column publishes the value as one of its
    # own labels, which is what --keep-value asked for and must not be
    # "repaired" away. The earlier name of this test said the value was
    # "withheld on the same rule"; the assertions below always showed
    # otherwise, and the name now says what they show.
    values = ["north"] * 40 + ["south"] * 40 + ["NA"] * 40
    document, written, summary_text = _run(
        tmp_path, "region", values, ["--keep-value", "NA"], capsys
    )
    column = document["columns"][0]
    assert column["role"] == taxonomy.ROLE_CATEGORICAL
    assert column["n_missing"] == 0
    # `NA` IS one of synthtwin's own ten words, so version 5 records
    # the member `na` here -- this package's spelling, never the
    # person's capitals (contract 5 C5-17). What that gives up is
    # written out in `profile.DECLARATION_PUBLICATION`.
    assert document["settings"]["kept_values"] == {
        "built_in_numbers": [],
        "built_in_texts": ["na"],
        "n_declared": 1,
        "values_recorded": False,
    }
    # 40 rows share it, which is above the floor, so it is a label of
    # this column like any other -- named in the column's own folded
    # spelling, with the capitals the file wrote recorded beside it as a
    # variant, because 40 rows wrote it that way and 40 clears the floor
    # (owner decisions 9 and 11).
    labels = [level["label"] for level in column["levels"]]
    assert sorted(labels) == ["na", "north", "south"]
    entry = next(level for level in column["levels"] if level["label"] == "na")
    assert entry["variants"] == {"NA": 40}
    # THE RULE THIS FILE IS ABOUT IS UNTOUCHED BY THAT. The spelling
    # reaches the document as a way of writing a label the column
    # already publishes, held to the same floor; it does not reach the
    # SETTINGS, which is where a declared value used to travel out of
    # every column at once.
    assert '"NA"' not in json.dumps(document["settings"])
    # And in the written file the spelling appears in exactly one place:
    # as a way of writing the label it is a way of writing.
    assert written.count('"NA"') == 1
    assert "--keep-value NA" not in summary_text


# -- what the profile records instead ---------------------------------


def test_the_policy_travels_with_the_profile(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    readings = [str(index) for index in range(1, 200)]
    document, _written, _summary_text = _run(
        tmp_path,
        "reading",
        readings + ["-999"] * 15,
        ["--keep-value", "-999", "--missing-value", "0"],
        capsys,
    )
    recorded = document["settings"]
    assert recorded["kept_values"]["n_declared"] == 1
    assert recorded["declared_missing_values"]["n_declared"] == 1
    assert recorded["declaration_matching"] == taxonomy.DECLARATION_MATCHING
    assert recorded["declaration_publication"] == (
        profile.DECLARATION_PUBLICATION
    )


def test_the_settings_block_still_names_every_setting() -> None:
    # The completeness rule is unchanged: a setting added to Settings and
    # forgotten in the block still fails. Two of the keys now carry a
    # policy record rather than the values, which is the whole change.
    recorded = profile._settings_block(
        taxonomy.Settings(
            kept_values=("NA", "-999"), declared_missing_values=("unknown",)
        ),
        [],
    )
    assert recorded["kept_values"] == {
        "built_in_numbers": [-999.0],
        "built_in_texts": ["na"],
        "n_declared": 2,
        "values_recorded": False,
    }
    assert recorded["declared_missing_values"] == {
        "built_in_numbers": [],
        "built_in_texts": [],
        "n_declared": 1,
        "values_recorded": False,
    }
    # The PERSON'S spelling is still nowhere IN THIS BLOCK, which is
    # what `recorded` is and the whole of what this asserts: `NA` was
    # typed and `na` is written, `-999` was typed and `-999.0` is
    # written, and `unknown` -- which is on no list of synthtwin's --
    # reaches neither list (contract 5 C5-17). Where `unknown` DOES go
    # is a column's `missing_by_source`, under the floor, and saying
    # this at document width was review item P3-V9-F1.
    assert "NA" not in json.dumps(recorded)
    assert "unknown" not in json.dumps(recorded)


def test_the_recorded_shape_can_be_told_from_the_older_one() -> None:
    # Dropping the key would have made a profile written under the older
    # rule indistinguishable from one written under this one. It is a
    # record, never a list, so a consumer can tell without guessing --
    # and the document says so in its version as well.
    recorded = profile._settings_block(taxonomy.Settings(), [])
    assert isinstance(recorded["kept_values"], dict)
    assert isinstance(recorded["declared_missing_values"], dict)
    assert recorded["kept_values"]["values_recorded"] is False
    # The version pin is what this test really needs: a consumer must be
    # able to tell the two shapes apart without inspecting them. It was
    # 2 when the declaration record arrived and is 3 since declared
    # identifier columns began carrying their repetition shape (review
    # item P1-R8-F4). What matters is that it ADVANCED past the profile
    # written under the older rule, so assert that rather than a number
    # that has to be edited every time the contract grows.
    assert profile.PROFILE_VERSION >= 3


# -- what the person is told, before the files exist -------------------


def test_the_summary_says_what_is_and_is_not_recorded(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _document, _written, summary_text = _run(
        tmp_path,
        "narrative",
        NARRATIVE + [RARE_TOKEN],
        ["--missing-value", RARE_TOKEN],
        capsys,
    )
    assert "Values you named yourself" in summary_text
    assert "named as real data: 0;   named as 'no value': 1" in summary_text
    # DIFFERENT values, since 2026-08-17: `n_declared` counts
    # declarations rather than keystrokes, so the page had to stop
    # saying "how many values you named" about a number that folds two
    # spellings of one value into one (review item P3-V9-F7, plan
    # amendment A-P3-37).
    assert "how many DIFFERENT values you named" in summary_text
    assert "the rule it used to match them" in summary_text
    assert "counts once: synthtwin reads those as one value" in summary_text
    # AND THE OPENING NAMES ITS OWN EXCEPTION (plan amendment A-P3-30).
    # It said flatly that the spellings YOU typed are not written into
    # the settings, and eight lines lower the same page told the person
    # who typed `n/a` that the description records which of synthtwin's
    # own words they named. Both were true; the pair was unreadable, and
    # the reader who has to act on this page is exactly the reader who
    # typed one of the thirteen. What is pinned is that the claim keeps
    # a word of the person's OWN as its subject and carries the
    # exception where it is made, so the contradiction cannot come back
    # by somebody shortening the sentence.
    said = " ".join(summary_text.split())
    assert "A word of YOUR OWN is not written into its settings" in said
    assert "which of those words it was" in said
    assert "The spellings YOU typed are not written" not in said
    # This test asserted "NOT written into the profile" until the claim
    # was checked against the code and found false: the sentence it came
    # from told the person that a value they typed is held back like
    # every other value, while `--keep-value -999` correctly publishes
    # -999 as a column's smallest number. The assertion was changed
    # rather than the behavior, and what it now pins is that no sentence
    # of that kind came back. The battery that checks the replacement
    # against what the code does is in
    # tests/test_p1r7f2_disclosure_is_true.py.
    assert "NOT written into the profile" not in summary_text
    assert "held back like" not in summary_text


def test_the_disclosure_comes_before_the_files_exist(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Plan P1-D6: the person sees what the profile carries BEFORE it is
    # on disk. A sentence about declarations that arrived afterwards
    # would be a report, not a disclosure.
    text = fixtures.single_column_table("narrative", NARRATIVE + [RARE_TOKEN])
    table = fixtures.write(tmp_path, "narrative.csv", text)
    assert main(["profile", f"{table}", "--missing-value", RARE_TOKEN]) == 0
    shown = capsys.readouterr().out
    said = shown.index("Values you named yourself")
    will_write = shown.index("These two files will be written")
    written = shown.index("\nWritten:")
    assert said < will_write < written


def test_nothing_is_said_when_nothing_was_declared(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # A paragraph printed on every ordinary run is a paragraph people
    # stop reading. The person who has to see this is the person who
    # typed a value.
    _document, _written, summary_text = _run(
        tmp_path, "narrative", NARRATIVE, [], capsys
    )
    assert "Values you named yourself" not in summary_text
    assert "WHAT THIS PROFILE CARRIES FROM YOUR TABLE" in summary_text


def test_the_summary_survives_a_document_written_under_the_older_shape(
    tmp_path: pathlib.Path,
) -> None:
    # The summary is rendered from the document. Handed the older shape,
    # where the key held a list of spellings, it must not fall over --
    # and it must not print a count it does not have.
    text = fixtures.single_column_table("narrative", NARRATIVE)
    table = reading.read_table(f"{fixtures.write(tmp_path, 'n.csv', text)}")
    document = profile.build_document(table, SETTINGS, [])
    settings = document["settings"]
    assert isinstance(settings, dict)
    settings["kept_values"] = ["NA"]
    settings["declared_missing_values"] = []
    rendered = summary.render(document, "read as UTF-8.")
    assert "Values you named yourself" not in rendered
    assert "named as real data" not in rendered
