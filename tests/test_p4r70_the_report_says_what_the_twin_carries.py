"""The twin's report says which absent spellings the twin actually holds.

RESIDUAL R-P4-70, opened 2026-08-31 and closed by landing L19.

**THE DEFECT WAS A DISCLOSURE SENTENCE POINTING THE WRONG WAY.** The
report told every reader, for every column with an absent cell, that
"the twin writes every one of them as an empty cell, so how your table
wrote them is here rather than in the twin", and the section heading
above it named those spellings among the things "no twin can carry".
Both were true of contract version 5. **P4-D6.1 closed residual R-P2-2**
-- version 6 writes each published `missing_by_source` spelling into
the twin at its count, keeping blank only what a judged pass put there
(C6-115, C6-116) -- and neither sentence moved with the rule.

So a researcher was told their own `NA`, `-9.99` or `Not recorded` had
stayed behind in the description, while the twin they were about to
move held it at its published count, character for character. The
whole five-file handling rule this project states everywhere rests on
a person knowing which file carries what.

**WHY THE SPLIT IS ASKED OF THE GENERATOR.** Which of the two a
spelling is, is the WRITE rule -- `missing_by_source` against the
judged-pass exception -- so the report asks
`generation.spellings_the_twin_reproduces` rather than working the
same question out a second way. A report that re-derived it could
disagree with the file it describes.
"""

import pathlib

import fixtures
from synthtwin import contract, generation, parsing, rendering, taxonomy
from synthtwin import profile as profile_module


def _built(
    folder: pathlib.Path,
    values: "list[str]",
    declared: "list[str] | None" = None,
) -> "tuple[contract.Profile, generation.Twin]":
    table = fixtures.write(
        folder,
        "t.csv",
        fixtures.single_column_table("reading", values),
    )
    from synthtwin import reading as reading_module

    read = reading_module.read_table(f"{table}")
    settings = taxonomy.Settings(
        declared_missing_values=tuple(declared or ())
    )
    document = profile_module.build_document(read, settings, [])
    written = fixtures.write_profile(folder, "t-profile.json", document)
    loaded = contract.load_profile(f"{written}")
    return loaded, generation.generate(loaded, seed=7)


def _report(loaded: contract.Profile, twin: generation.Twin) -> str:
    return parsing.visible_lines(rendering.report(loaded, twin))


def _declared_column(folder: pathlib.Path) -> "tuple[contract.Profile, generation.Twin]":
    values = [
        "-9.99" if index % 6 == 0 else f"{10 + index % 80}.{index % 10}"
        for index in range(120)
    ]
    return _built(folder, values, ["-9.99"])


def _judged_column(folder: pathlib.Path) -> "tuple[contract.Profile, generation.Twin]":
    values = [
        "-999" if index % 6 == 0 else f"{10 + index % 80}"
        for index in range(120)
    ]
    return _built(folder, values)


def test_a_spelling_the_twin_carries_is_not_called_left_behind(
    tmp_path: pathlib.Path,
) -> None:
    """The measured case, and the one the defect was found on."""
    loaded, twin = _declared_column(tmp_path)
    column = loaded.columns[0]
    assert column.missing_by_source.get("-9.99") == 20, (
        "the fixture must publish the declared spelling, or this test "
        "is measuring nothing"
    )
    cells = rendering.twin_csv(twin)
    assert cells.count("-9.99") == 20, (
        "and the twin must actually hold it, which is the fact the "
        "report was contradicting"
    )
    said = _report(loaded, twin)
    assert "the twin writes every one of them as an empty cell" not in said
    assert "The twin WRITES every one of these cells the way your table" in said
    assert "-9.99: 20 cell(s) -- the twin writes this spelling in all of them" in said


def test_a_spelling_a_judged_pass_put_there_is_still_called_blank(
    tmp_path: pathlib.Path,
) -> None:
    """C6-116's case, which the old sentence fitted and still does.

    This is the half that kept the defect alive: the one shape the
    reports were usually read on was the one the sentence was true of.
    """
    loaded, twin = _judged_column(tmp_path)
    column = loaded.columns[0]
    assert column.missing_by_source.get("-999") == 20
    cells = rendering.twin_csv(twin)
    assert "-999" not in cells, "C6-116 keeps a judged stand-in blank"
    said = _report(loaded, twin)
    assert "The twin writes every one of them as an empty cell" in said
    assert "-999: 20 cell(s) -- the twin leaves these cells empty" in said


def test_the_report_and_the_write_rule_cannot_disagree(
    tmp_path: pathlib.Path,
) -> None:
    """One rule, two readers.

    The report does not re-derive which spellings travel; it asks the
    function the generator writes by. This holds the report's own
    marking against the twin's actual cells, spelling by spelling, so
    a change to either that left the other behind turns this red.
    """
    for build in (_declared_column, _judged_column):
        folder = tmp_path / build.__name__
        folder.mkdir()
        loaded, twin = build(folder)
        column = loaded.columns[0]
        cells = rendering.twin_csv(twin)
        reproduced, left_blank = generation.spellings_the_twin_reproduces(
            column, loaded
        )
        said = _report(loaded, twin)
        for spelling in reproduced:
            count = column.missing_by_source[spelling]
            assert cells.count(spelling) >= count, (
                f"the report says the twin writes {spelling!r} and the "
                f"twin does not hold it {count} times"
            )
            assert (
                f"{spelling}: {count} cell(s) -- the twin writes this "
                f"spelling in all of them"
            ) in said
        for spelling in left_blank:
            count = column.missing_by_source[spelling]
            assert (
                f"{spelling}: {count} cell(s) -- the twin leaves these "
                f"cells empty"
            ) in said
        assert set(reproduced) | set(left_blank) == set(
            column.missing_by_source
        ), "every published spelling is in exactly one of the two"


def test_the_section_heading_no_longer_calls_them_uncarried(
    tmp_path: pathlib.Path,
) -> None:
    """The other sentence, which said it about every column at once.

    Repairing only the per-column line would have left the page saying
    both things, which is what a reader meets first.
    """
    loaded, twin = _declared_column(tmp_path)
    said = _report(loaded, twin)
    assert (
        "What no twin can carry -- how your table wrote the cells it"
        not in said
    )
    assert "this twin CARRIES some of those spellings rather" in said


def test_the_heading_says_it_only_where_it_is_true(
    tmp_path: pathlib.Path,
) -> None:
    """One page may not give two answers to one question.

    Printed flatly, the carried-spellings paragraph would tell the
    reader of a table whose holes are all judged stand-ins that their
    twin carries spellings, while every column block under it said the
    opposite. It is printed only where some column of THIS description
    has a spelling the twin writes.
    """
    loaded, twin = _judged_column(tmp_path)
    said = _report(loaded, twin)
    assert "CARRIES some of those spellings" not in said, (
        "nothing travels out of this description, so the page may not "
        "say anything does"
    )
    assert "The twin writes every one of them as an empty cell" in said
