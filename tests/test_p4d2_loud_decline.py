"""Every surface that hands a person invented cells says so (plan P4-D2).

THE DEFECT THIS FILE EXISTS TO KEEP CLOSED. A column that matched no
detection rule became free text, which publishes no value of the table,
so the generator had nothing of the person's to write and made up every
cell of that column's twin. Nothing on any OUTCOME surface said so:
`profile`, `generate` and `validate` all exited 0, the quality report
certified the shape facts the filler meets by construction, and the one
sentence in the twin's report that called a cell invented lived inside
the spreadsheet warning and printed only when such a cell happened to
begin with a formula character. A person could read the whole report of
a twin whose column was pure invention and meet no sentence saying it.

WHAT REPLACES IT, AND WHY IT IS THREE SENTENCES AND NOT ONE. The plan
draws three classes, at the places where the truth changes:

* EVERYTHING -- a column whose role publishes no value of the table and
  whose cells are therefore all synthtwin's own: free text, a declared
  record-number column, and numbers no format can hold. A column with no
  present cell is NOT in this class however it was declared, because a
  twin that holds none of its values invented none of them either.
* HELD BACK -- a label column carrying its published labels plus neutral
  stand-ins for the labels and spellings the floor withheld.
* UNCARRIED -- a column whose description counts cells it carries no
  value for: the out-of-range, contradictory and non-numeric cells of a
  numeric column, and the cells of a datetime column that did not read
  as dates.

One sentence would have been false at both edges: "every value here is
invented" is a lie about a category column that carries its real labels,
and any invention sentence at all is a lie about an empty column.

WHAT IS ASSERTED BELOW. That each class gets its sentence; that the
sentence is UNCONDITIONAL -- it does not wait for a formula character,
which is the whole defect; that the counts in it are the description's
own; that a column in no class gets no sentence; that the page-foot
count and the screen line count BOTH kinds, because a line counting only
the outright-invented columns would read "0 of 1" over a twin whose one
column carries invented labels; and that the exit code does not move,
because a decline is not a failure.

THAT THESE ASSERTIONS CAN FAIL WAS MEASURED, not assumed, by putting
each defect back into `rendering.py` and running this file. What the
mutation was, and what it reddened:

* the empty-column carve-out deleted from `_made_up_class` -- five
  tests red, `test_an_empty_column_is_told_nothing_about_invention`
  among them. The measurement is why `blank` is DECLARED in the fixture
  below: on an undeclared empty column the same five tests pass with
  the carve-out gone, because such a column fails the class test on its
  role alone, and the whole file was briefly green against a defect it
  claimed to hold.
* the partly-invented arm deleted from `_made_up_totals` -- three
  tests red, the two count tests and the agreement test.

The remaining two defects of the plan's list are held by construction
rather than by mutation, and are named here so the difference is
visible: the sentence cannot go back inside the spreadsheet warning's
condition while `test_the_sentence_does_not_wait_for_a_formula_character`
asserts both halves of that condition's absence on one page, and the
exit code cannot move while `test_cli_generate` asserts 0 on a run this
file's fixture reaches.
"""

import pathlib

import pytest

import fixtures
from synthtwin import (
    contract,
    generation,
    profile,
    reading,
    rendering,
    taxonomy,
)

# The three classes as this file names them, so a rename in the product
# is a rename here and not a silently passing test.
EVERYTHING = rendering._MADE_UP_EVERYTHING
HELD_BACK = rendering._MADE_UP_HELD_BACK
UNCARRIED = rendering._MADE_UP_UNCARRIED
NOTHING = rendering._MADE_UP_NOTHING

SEED = 20260819


def _described(
    folder: pathlib.Path, text: str, declared: "list[str] | None" = None
) -> contract.Profile:
    """One table, described by the real producer and read back."""
    table_path = fixtures.write(folder, "table.csv", text)
    table = reading.read_table(str(table_path))
    document = profile.build_document(
        table, taxonomy.Settings(), declared or []
    )
    written = fixtures.write_profile(folder, "table-profile.json", document)
    return contract.load_profile(str(written))


def _column(loaded: contract.Profile, name: str) -> contract.ColumnBlock:
    for column in loaded.columns:
        if column.name == name:
            return column
    raise AssertionError(f"no column named {name}")


def _block(text: str, name: str) -> "list[str]":
    """The report's block for one column, as its own lines."""
    lines = text.splitlines()
    opened = -1
    for place in range(len(lines)):
        if lines[place].startswith(f"'{name}' -- "):
            opened = place
    assert opened >= 0, f"no report block for {name}"
    found: list[str] = []
    for line in lines[opened + 1 :]:
        if line.startswith("'") and " -- " in line:
            break
        if line.startswith("======"):
            break
        found = found + [line]
    return found


# -- the three classes, and the one that is no class ------------------


@pytest.fixture(scope="module")
def every_class(tmp_path_factory: pytest.TempPathFactory) -> contract.Profile:
    """One table reaching all three invention classes and neither edge.

    `code` is declared, which is the only route to the record-number
    role. `note` is free text. `region` is a set of categories with one
    label too rare to publish. `measure` is whole numbers with one cell
    that is not a number at all, inside the slack the numeric line
    allows. `seen` is dates with one cell that does not read as one.
    `flag` is a two-value column that publishes both of its labels and
    invents nothing.

    `blank` is the edge the carve-out exists for, and it is DECLARED: a
    column whose cells are all absent is settled as an empty column
    before any other rule runs, so it arrives carrying the role `empty`
    while `structural_role` still says its owner called it a record
    number. Every publishing-nothing test in this file would pass on an
    UNdeclared empty column for the wrong reason -- such a column fails
    the class test on its role alone -- so declaring it is what makes
    the carve-out the only thing standing between it and a sentence
    saying its 0 values were invented.
    """
    folder = tmp_path_factory.mktemp("p4d2-classes")
    header = ["code", "note", "region", "measure", "seen", "flag", "blank"]
    rows: list[list[str]] = []
    for place in range(240):
        rows = rows + [
            [
                f"K{place:04d}",
                f"free words {place}",
                # One label is worn by exactly seven rows, which the
                # default floor of eleven holds back; the other two are
                # worn by plenty and are published.
                (
                    "rare"
                    if place < 7
                    else ("north" if place % 2 else "south")
                ),
                "not recorded" if place == 3 else str(10 + place % 40),
                (
                    "sometime"
                    if place == 8
                    else f"2024-01-{1 + place % 28:02d}"
                ),
                "yes" if place % 2 else "no",
                "",
            ]
        ]
    return _described(
        folder, fixtures.rows_to_csv(header, rows), declared=["code", "blank"]
    )


def test_each_column_lands_in_the_class_the_plan_gives_it(
    every_class: contract.Profile,
) -> None:
    """The class is decided by role and published facts, nothing else."""
    expected = {
        "code": EVERYTHING,
        "note": EVERYTHING,
        "region": HELD_BACK,
        "measure": UNCARRIED,
        "seen": UNCARRIED,
        "flag": NOTHING,
        "blank": NOTHING,
    }
    for name in sorted(expected):
        column = _column(every_class, name)
        assert rendering._made_up_class(column) == expected[name], (
            f"{name} is role {column.role}, structural_role "
            f"{column.structural_role}, and landed in the wrong class"
        )


def test_an_empty_column_is_told_nothing_about_invention(
    every_class: contract.Profile,
) -> None:
    """A twin holding none of a column's values invented none of them.

    The carve-out is the plan's, and it is the reason the class test
    asks about `n_present` before it asks about the role: a column
    declared a record number and holding nothing but absent cells has
    the publishing-nothing role AND no cell to invent.
    """
    empty = _column(every_class, "blank")
    assert empty.n_present == 0
    # Declared, so every other route into the EVERYTHING class is open
    # to it and only the carve-out keeps it out.
    assert empty.structural_role == "identifier"
    assert empty.role == "empty"
    assert rendering._made_up_class(empty) == NOTHING
    assert rendering._made_up_lines(empty, 11) == []


def test_a_column_that_invents_nothing_is_told_nothing(
    every_class: contract.Profile,
) -> None:
    """A column carrying only published labels gets no sentence."""
    flag = _column(every_class, "flag")
    assert flag.n_present == 240
    assert rendering._made_up_lines(flag, 11) == []


# -- the sentences, on the page ---------------------------------------


@pytest.fixture(scope="module")
def page(every_class: contract.Profile) -> str:
    """The report for a twin of that description."""
    return rendering.report(
        every_class, generation.generate(every_class, SEED)
    )


def test_every_invented_column_says_so_in_its_own_block(page: str) -> None:
    """Once per column, in the block a reader looking for it opens."""
    for name in ("code", "note", "region", "measure", "seen"):
        said = [line for line in _block(page, name) if "MADE UP" in line]
        assert len(said) == 1, (
            f"{name} carries {len(said)} invention sentence(s); the plan "
            f"gives every invented column exactly one"
        )


def test_the_uninvented_columns_say_nothing_of_the_kind(page: str) -> None:
    for name in ("flag", "blank"):
        said = [line for line in _block(page, name) if "MADE UP" in line]
        assert said == [], f"{name} invents nothing and must claim nothing"


def test_the_sentence_carries_the_descriptions_own_counts(
    every_class: contract.Profile, page: str
) -> None:
    """Every count printed is one the description publishes."""
    note = _block(page, "note")
    assert any("MADE UP all 240 of this column's values" in one for one in note)
    region = _block(page, "region")
    assert any("MADE UP 7 of this column's 240 value(s)" in one for one in region)
    measure = _block(page, "measure")
    assert any("MADE UP 1 of this column's 240 value(s)" in one for one in measure)


def test_the_sentence_does_not_wait_for_a_formula_character(
    page: str,
) -> None:
    """The defect itself: the sentence used to be inside that condition.

    The spreadsheet warning below still names the columns whose invented
    cells a spreadsheet would read as a formula -- that is its own job --
    but the per-column sentence is now a property of the class, so a
    twin with no hazardous cell at all still says what it made up.
    """
    assert "no cell of this twin begins with one of those" in page.lower()
    assert "MADE UP all 240 of this column's values" in page


# -- the two counts ---------------------------------------------------


def test_the_page_foot_counts_both_kinds(
    every_class: contract.Profile, page: str
) -> None:
    """Two columns invented outright; three more invented in part."""
    assert "HOW MUCH OF THIS TWIN SYNTHTWIN MADE UP" in page
    assert "2 of the 7 column(s) hold nothing but values" in page
    assert "3 more column(s) hold some made-up cells beside" in page


def test_the_screen_line_counts_both_kinds(
    every_class: contract.Profile,
) -> None:
    """The one line a person reads before opening the twin."""
    said = rendering.made_up_warning(every_class)
    assert "2 of this twin's 7 column(s) hold nothing but values" in said
    assert "3 more column(s) hold some made-up cells" in said


def test_both_counts_print_when_a_twin_invents_nothing(
    tmp_path: pathlib.Path,
) -> None:
    """A count nobody sees until they suspect it is a count nobody sees.

    The same discipline the spreadsheet count keeps: it is printed on
    every run, whatever it is, so a reader is told what the number is
    rather than told only that somebody thought it worth printing.
    """
    header = ["flag"]
    rows = [["yes" if place % 2 else "no"] for place in range(60)]
    loaded = _described(tmp_path, fixtures.rows_to_csv(header, rows))
    page = rendering.report(loaded, generation.generate(loaded, SEED))
    assert "0 of the 1 column(s) hold nothing but values" in page
    assert "0 more column(s) hold some made-up cells beside" in page
    assert "0 of this twin's 1 column(s)" in rendering.made_up_warning(loaded)


def test_the_counts_agree_with_the_per_column_sentences(page: str) -> None:
    """The foot of the page cannot say one thing and the blocks another."""
    outright = 0
    partly = 0
    for line in page.splitlines():
        if "MADE UP all " in line:
            outright = outright + 1
        elif "MADE UP " in line and "of this column's" in line:
            partly = partly + 1
    assert f"{outright} of the 7 column(s) hold nothing but values" in page
    assert f"{partly} more column(s) hold some made-up cells beside" in page
