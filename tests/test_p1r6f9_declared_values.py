"""P1-R6-F9: --keep-value and --missing-value, through the real command.

The settings and the docstrings promised that the person running the
tool has the last word about what is data and what is "no value". The
command exposed neither option, so a region column genuinely coded `NA`
lost every one of those rows and became a two-value column with no way
back. And the setting underneath did not work either: with
`kept_values=("-999.0",)` the candidate was turned into the spelling
`-999` before the declaration was looked at, the declared spelling was
missed, and every cell whose number equalled -999 was removed anyway.

The rule now, stated once and applied everywhere before any value is
removed:

* a declared value that reads as a number this format can hold matches
  every cell holding that EXACT NUMBER, whatever either of them is
  spelled like -- so `-999` covers a file that writes `-999.00`;
* any other declared value matches by SPELLING, after trimming and case
  folding -- so `NA` covers `na` and ` NA `;
* one value named both ways is refused with a message, never resolved.

Everything below goes through `cli.main` with the words a person would
type, because an option that only works when called as a library is the
defect this item is about.
"""

import json
import pathlib

import pytest

import fixtures
from synthtwin import parsing, profile, taxonomy
from synthtwin.cli import main

SETTINGS = taxonomy.Settings()

# The item's own two columns.
REGIONS = ["north"] * 40 + ["south"] * 40 + ["NA"] * 40
READINGS = [str(index) for index in range(1, 200)]


def _written(tmp_path: pathlib.Path, name: str, values: list[str]) -> str:
    """One column on disk, and its path as a person would type it."""
    text = fixtures.single_column_table(name, values)
    return f"{fixtures.write(tmp_path, f'{name}.csv', text)}"


def _profiled(tmp_path: pathlib.Path, name: str) -> dict:
    """Read the profile the command just wrote."""
    document = json.loads(
        (tmp_path / f"{name}-profile.json").read_text(encoding="utf-8")
    )
    assert isinstance(document, dict)
    return document


def _run(
    tmp_path: pathlib.Path,
    name: str,
    values: list[str],
    options: list[str],
    capsys: pytest.CaptureFixture[str],
) -> dict:
    """Profile one column through the command line; return the document."""
    table = _written(tmp_path, name, values)
    assert main(["profile", table] + options) == 0
    capsys.readouterr()
    return _profiled(tmp_path, name)


# -- a legitimate NA --------------------------------------------------


def test_a_genuine_na_is_lost_without_the_option(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The state of affairs the option exists to repair, stated first so
    # that the repair below means something.
    document = _run(tmp_path, "region", REGIONS, [], capsys)
    column = document["columns"][0]
    assert column["role"] == taxonomy.ROLE_BINARY
    assert column["n_missing"] == 40
    assert column["n_present"] == 80


def test_keep_value_makes_a_genuine_na_data_again(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    document = _run(
        tmp_path, "region", REGIONS, ["--keep-value", "NA"], capsys
    )
    column = document["columns"][0]
    assert column["role"] == taxonomy.ROLE_CATEGORICAL
    assert column["n_missing"] == 0
    assert column["n_present"] == 120
    labels = [level["label"] for level in column["levels"]]
    assert sorted(labels) == ["na", "north", "south"]
    # The profile records HOW MANY values were declared and under which
    # rules -- never the spelling the operator typed. A declaration is
    # typed BECAUSE the value is in the table, so republishing it in the
    # settings block carried a real source value around every per-column
    # suppression rule (review item P1-R7-F2).
    #
    # AND, FROM CONTRACT VERSION 5, WHICH OF SYNTHTWIN'S OWN WORDS WAS
    # NAMED (its section 6; plan amendment A-P3-27). `NA` is one of the
    # ten spellings this package publishes as meaning "no value", so the
    # record names the MEMBER `na` -- not the person's capitals, and not
    # any word of theirs that is not on that list.
    assert document["settings"]["kept_values"] == {
        "built_in_numbers": [],
        "built_in_texts": ["na"],
        "n_declared": 1,
        "values_recorded": False,
    }


@pytest.mark.parametrize("declared", ["NA", "na", " na "])
def test_a_kept_spelling_is_matched_after_trimming_and_case_folding(
    declared: str,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    document = _run(
        tmp_path, "region", REGIONS, ["--keep-value", declared], capsys
    )
    assert document["columns"][0]["n_missing"] == 0


def test_missing_value_makes_ordinary_text_a_hole(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    values = ["north"] * 40 + ["south"] * 40 + ["unknown"] * 40
    document = _run(
        tmp_path, "region", values, ["--missing-value", "unknown"], capsys
    )
    column = document["columns"][0]
    assert column["n_missing"] == 40
    assert column["missing_by_class"]["(declared-missing)"] == 40
    assert column["role"] == taxonomy.ROLE_BINARY
    # `unknown` is the person's own word, not one of synthtwin's ten,
    # so both lists stay empty and the count is the whole of what the
    # settings block says about it (contract 5 C5-17, C5-18).
    assert document["settings"]["declared_missing_values"] == {
        "built_in_numbers": [],
        "built_in_texts": [],
        "n_declared": 1,
        "values_recorded": False,
    }


# -- the same number, spelled four ways -------------------------------
#
# The item's second half: the file's spelling and the person's spelling
# need not agree, because the comparison is on the NUMBER.


@pytest.mark.parametrize("in_the_file", ["-999", "-999.0", "-999.00"])
@pytest.mark.parametrize("declared", ["-999", "-999.0", "-999.00"])
def test_a_kept_number_survives_however_either_side_spells_it(
    in_the_file: str,
    declared: str,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    values = READINGS + [in_the_file] * 15
    document = _run(
        tmp_path, "reading", values, ["--keep-value", declared], capsys
    )
    column = document["columns"][0]
    assert column["n_missing"] == 0, (
        "the person said this number is data; nothing may remove it"
    )
    assert column["percentiles"]["min"] == -999.0
    verdicts = column["sentinel_verdicts"]
    assert [entry["verdict"] for entry in verdicts] == ["kept_as_a_number"]
    assert [entry["reason"] for entry in verdicts] == ["kept_by_you"]


def test_the_same_column_without_the_option_loses_the_number(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The neighbour: with nothing declared, -999 is an outlying stand-in
    # for "no value" and is read as one, which is what makes the option
    # worth having.
    document = _run(
        tmp_path, "reading", READINGS + ["-999.0"] * 15, [], capsys
    )
    column = document["columns"][0]
    assert column["n_missing"] == 15
    assert column["percentiles"]["min"] == 1.0


@pytest.mark.parametrize("declared", ["-999", "-999.00"])
def test_a_declared_missing_number_matches_the_files_spelling(
    declared: str,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The other direction: the file writes -999.0 and the person writes
    # -999 or -999.00, and all three are one number. The rows are
    # counted as declared missing rather than as the rule's own
    # numeric-sentinel class, because the person decided them.
    values = [str(index) for index in range(1, 200)] + ["-999.0"] * 15
    document = _run(
        tmp_path, "reading", values, ["--missing-value", declared], capsys
    )
    column = document["columns"][0]
    assert column["n_missing"] == 15
    assert column["missing_by_class"]["(declared-missing)"] == 15
    assert column["percentiles"]["min"] == 1.0


def test_a_declared_missing_number_is_removed_before_any_rule_runs(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # -1 is an ordinary number: no rule would take it out, and its
    # presence makes the column continuous rather than a count. The
    # declaration has to be applied before the role is decided.
    values = [str(index) for index in range(1, 200)] + ["-1"] * 15
    document = _run(
        tmp_path, "reading", values, ["--missing-value", "-1.0"], capsys
    )
    column = document["columns"][0]
    assert column["role"] == taxonomy.ROLE_COUNT
    assert column["n_missing"] == 15
    assert column["percentiles"]["min"] == 1.0
    assert column["n_negative"] == 0


def test_a_number_declaration_does_not_match_by_spelling(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The rule cuts both ways, and this is the side that keeps it
    # honest: `-999` names a NUMBER, so it does not reach a cell that
    # merely reads like it. Nothing in this column is a number, so
    # nothing is declared away.
    values = [f"code-999-{index}" for index in range(60)]
    document = _run(
        tmp_path, "codes", values, ["--missing-value", "-999"], capsys
    )
    assert document["columns"][0]["n_missing"] == 0


# -- more than one candidate in one column ----------------------------


def test_one_candidate_can_be_kept_while_another_is_read_as_missing(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    values = READINGS + ["-999.0"] * 15 + ["9999"] * 15
    document = _run(
        tmp_path, "reading", values, ["--keep-value", "-999"], capsys
    )
    column = document["columns"][0]
    assert column["n_missing"] == 15, "only 9999 may go"
    assert column["percentiles"]["min"] == -999.0
    verdicts = {
        entry["candidate"]: entry["verdict"]
        for entry in column["sentinel_verdicts"]
    }
    assert verdicts == {
        "-999": "kept_as_a_number", "9999": "read_as_missing",
    }


def test_both_candidates_can_be_kept_at_once(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    values = READINGS + ["-999"] * 15 + ["9999"] * 15
    document = _run(
        tmp_path,
        "reading",
        values,
        ["--keep-value", "-999", "--keep-value", "9999"],
        capsys,
    )
    column = document["columns"][0]
    assert column["n_missing"] == 0
    assert column["percentiles"]["min"] == -999.0
    assert column["percentiles"]["max"] == 9999.0
    assert document["settings"]["kept_values"] == {
        "built_in_numbers": [-999.0, 9999.0],
        "built_in_texts": [],
        "n_declared": 2,
        "values_recorded": False,
    }


def test_both_candidates_can_be_declared_missing_at_once(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    values = READINGS + ["-999"] * 15 + ["9999"] * 15
    document = _run(
        tmp_path,
        "reading",
        values,
        ["--missing-value", "-999", "--missing-value", "9999"],
        capsys,
    )
    column = document["columns"][0]
    assert column["n_missing"] == 30
    assert column["missing_by_class"]["(declared-missing)"] == 30
    assert column["percentiles"]["min"] == 1.0
    assert column["percentiles"]["max"] == 199.0


def test_one_column_can_carry_a_kept_text_code_and_a_kept_number(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Both halves of the matching rule at once, in one column: a
    # spelling and a number.
    values = ["north"] * 40 + ["south"] * 40 + ["NA"] * 40 + ["-999"] * 40
    document = _run(
        tmp_path,
        "region",
        values,
        ["--keep-value", "NA", "--keep-value", "-999.00"],
        capsys,
    )
    column = document["columns"][0]
    assert column["n_missing"] == 0
    assert column["n_present"] == 160


# -- a declaration that contradicts itself ----------------------------


@pytest.mark.parametrize(
    ("kept", "declared_missing"),
    [
        ("-999", "-999"),
        ("-999", "-999.0"),
        ("-999.00", "-999"),
        ("NA", "na"),
        ("NA", " NA "),
    ],
)
def test_naming_one_value_both_ways_is_refused_with_a_message(
    kept: str,
    declared_missing: str,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    table = _written(tmp_path, "reading", READINGS + ["-999"] * 15)
    code = main(
        [
            "profile",
            table,
            "--keep-value",
            kept,
            "--missing-value",
            declared_missing,
        ]
    )
    assert code == 2
    told = capsys.readouterr().err
    assert "contradict each other" in told
    assert kept in told and declared_missing in told
    assert "Decide which one you meant" in told
    assert "run the command again" in told
    assert not (tmp_path / "reading-profile.json").exists(), (
        "nothing may be written when the options contradict each other"
    )


def test_two_declarations_that_are_not_the_same_value_are_accepted(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The neighbour: keeping one value and declaring a different one
    # missing is an ordinary, sensible pair of options.
    values = READINGS + ["-999"] * 15 + ["9999"] * 15
    document = _run(
        tmp_path,
        "reading",
        values,
        ["--keep-value", "-999", "--missing-value", "9999"],
        capsys,
    )
    column = document["columns"][0]
    assert column["n_missing"] == 15
    assert column["percentiles"]["min"] == -999.0
    assert column["percentiles"]["max"] == 199.0


def test_the_library_refuses_the_same_contradiction(
    tmp_path: pathlib.Path,
) -> None:
    # The command is one way in; the module is the other, and it must
    # not resolve silently what the command refuses.
    settings = taxonomy.Settings(
        kept_values=("-999",), declared_missing_values=("-999.0",)
    )
    with pytest.raises(ValueError) as caught:
        taxonomy.profile_column("c", 1, ["1", "2"], 2, settings)
    assert "cannot be both" in f"{caught.value}"


def test_the_check_names_the_pair_and_nothing_else() -> None:
    assert taxonomy.contradictory_declarations(("NA",), ("-999",)) == []
    assert taxonomy.contradictory_declarations((), ()) == []
    clashes = taxonomy.contradictory_declarations(("-999",), ("-999.00",))
    assert len(clashes) == 1
    assert "the same number" in clashes[0]
    spelled = taxonomy.contradictory_declarations(("NA",), ("na",))
    assert "the same spelling" in spelled[0]


# -- what the profile records about the declaration -------------------


def test_the_profile_records_the_declarations_and_the_rule(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    document = _run(
        tmp_path,
        "reading",
        READINGS + ["-999.0"] * 15,
        ["--keep-value", "-999", "--missing-value", "0"],
        capsys,
    )
    recorded = document["settings"]
    assert recorded["kept_values"]["n_declared"] == 1
    assert recorded["declared_missing_values"]["n_declared"] == 1
    assert recorded["declaration_publication"] == profile.DECLARATION_PUBLICATION
    assert recorded["declaration_matching"] == taxonomy.DECLARATION_MATCHING
    assert "number" in recorded["declaration_matching"]


def test_the_options_are_described_on_the_help_screen(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["--help"])
    assert caught.value.code == 0
    shown = capsys.readouterr().out
    assert "--keep-value" in shown
    assert "--missing-value" in shown
    for jargon in ("sentinel", "kept_values", "taxonomy", "None"):
        assert jargon not in shown


def test_the_declared_value_never_reaches_a_withholding_column(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # A declaration is still a value of the real table, so it obeys the
    # publication rule like every other: a column that publishes nothing
    # names no spelling, not even one the person typed.
    values = fixtures.prose(50)
    document = _run(
        tmp_path,
        "comment",
        values + ["-9.99e2"],
        ["--missing-value", "-999"],
        capsys,
    )
    column = document["columns"][0]
    assert column["role"] == taxonomy.ROLE_TEXT
    assert column["n_missing"] == 1
    assert column["missing_by_source"] == {}
    assert "-9.99e2" not in profile.serialize(document)


def test_a_documented_missing_spelling_never_reads_as_a_number() -> None:
    """The premise the two-step split rests on, stated as its own check.

    The spellings are compared before the cells are classified, and the
    numbers are compared after. That is only safe because nothing in the
    documented table of missing spellings reads as a number: if one ever
    did, a `--keep-value` naming that number could not rescue it.
    """
    for spelling in parsing.MISSING_TEXTS:
        assert parsing.classify_number(spelling) != parsing.NUMBER, (
            f"{spelling!r} reads as a number; the split order is unsafe"
        )
