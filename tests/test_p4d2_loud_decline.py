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
    cli,
    contract,
    generation,
    profile,
    reading,
    rendering,
    summary,
    taxonomy,
)

# The three classes as this file names them, so a rename in the product
# is a rename here and not a silently passing test.
EVERYTHING = rendering._MADE_UP_EVERYTHING
HELD_BACK = rendering._MADE_UP_HELD_BACK
UNCARRIED = rendering._MADE_UP_UNCARRIED
NOTHING = rendering._MADE_UP_NOTHING

SEED = 20260819

# The floor these fixtures are read at, said out loud because pooling is
# what this file's subject rests on: a label column keeps the HELD BACK
# class only while the floor holds SOME of its spellings back, and
# reaches EVERYTHING only while the floor holds them ALL back. The
# product's default floor is now 1 (owner ruling, plan amendment
# A-P4-37), and at a floor of 1 nothing is ever held back, so a
# description built at the default reaches neither shape and the classes
# below would be asserted against a table that has no rare cell in it.
# Eleven is the floor every fixture in this file was built against -- the
# `rare` label worn by seven rows, the eleven case spellings worn by two
# rows each -- and the floor the exact-shape assertions spell out in
# words ("fewer than 11 rows share"), so it is pinned here rather than
# taken from whatever the default happens to be.
SETTINGS = taxonomy.Settings(small_cell_floor=11)


# A column no rule reads, for the tests about what a column NOBODY
# reads says about itself. It has to vary in shape and hold no number:
# `free words 0`, `free words 1` and the rest of that family stopped
# being free text when the affixed-number rule was built -- it reads
# them as a number wearing `free words `, which is the whole point of
# that rule -- so a template cannot stand for prose here any more.
#
# Thirty-six different sentences over 240 rows clears the categorical
# ceiling of a tenth, so no earlier rule claims it either.
_PROSE = [
    f"{opening} {middle} {ending}"
    for opening in ("seen", "review", "pending")
    for middle in ("in clinic", "by phone", "at home")
    for ending in ("no change", "improving", "worse", "unclear")
]


def _described(
    folder: pathlib.Path, text: str, declared: "list[str] | None" = None
) -> contract.Profile:
    """One table, described by the real producer and read back."""
    table_path = fixtures.write(folder, "table.csv", text)
    table = reading.read_table(str(table_path))
    document = profile.build_document(
        table, SETTINGS, declared or []
    )
    written = fixtures.write_profile(folder, "table-profile.json", document)
    return contract.load_profile(str(written))


def _cased(word: str, which: int) -> str:
    """One of the case spellings of ``word``, chosen by ``which``.

    Eleven of them fit in a four-letter word, which is what the
    variant-only fixtures need: spellings that all fold together while
    each is worn by too few rows to publish.
    """
    letters = ""
    for place in range(len(word)):
        letter = word[place]
        if (which >> place) % 2:
            letter = letter.upper()
        letters = letters + letter
    return letters


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
                _PROSE[place % len(_PROSE)],
                # One label is worn by exactly seven rows, which the
                # floor of eleven `SETTINGS` pins holds back; the other
                # two are worn by plenty and are published.
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
    assert any(
        "MADE UP all 240 of this column's present value(s)" in one
        for one in note
    )
    region = _block(page, "region")
    assert any(
        "MADE UP 7 of this column's 240 present value(s)" in one
        for one in region
    )
    measure = _block(page, "measure")
    assert any(
        "MADE UP 1 of this column's 240 present value(s)" in one
        for one in measure
    )


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
    assert "MADE UP all 240 of this column's present value(s)" in page


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


# -- the surfaces, reached the way a person reaches them ---------------
#
# Every assertion above this line calls a rendering function directly,
# so deleting the CLI's one call or the summary's four lines would leave
# the file green while the person met neither (review item P4-C1-F6).
# These reach the surfaces through the command and the producer.


def test_the_screen_line_reaches_a_person_running_the_command(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`synthtwin generate` says it on the screen, not only in the file."""
    header = ["note"]
    rows = [[_PROSE[place % len(_PROSE)]] for place in range(60)]
    table = fixtures.write(
        tmp_path, "table.csv", fixtures.rows_to_csv(header, rows)
    )
    assert cli.main(["profile", f"{table}", "--out-dir", f"{tmp_path}"]) == 0
    capsys.readouterr()
    description = tmp_path / "table-profile.json"
    assert cli.main(["generate", f"{description}"]) == 0
    told = capsys.readouterr()
    # The warning channel, because a person who reads one line before
    # opening the twin should read this one.
    assert "hold nothing but values synthtwin made up" in told.err
    assert "1 of this twin's 1 column(s)" in told.err


def test_the_summary_tells_a_person_before_they_generate_anything(
    tmp_path: pathlib.Path,
) -> None:
    """The producer's own page says what a twin of it would hold."""
    header = ["note"]
    rows = [[_PROSE[place % len(_PROSE)]] for place in range(60)]
    table = fixtures.write(
        tmp_path, "table.csv", fixtures.rows_to_csv(header, rows)
    )
    document = profile.build_document(
        reading.read_table(str(table)), SETTINGS, []
    )
    page = summary.render(document, "")
    # The whole sentence, line for line: "every value in" alone appears
    # elsewhere on this page, so asserting it would have passed with
    # this sentence deleted -- measured (review item P4-C1-F6).
    assert (
        "  If you build a twin from this description, every value in\n"
        "  these columns will be one synthtwin made up. Either the\n"
        "  column publishes no value at all, or its spellings were\n"
        "  each worn by too few rows to publish, and either way the\n"
        "  twin has to invent what it writes --\n"
        "    note\n"
        "  The twin's own report says so again, column by column."
    ) in page


# -- exact shapes, not substrings --------------------------------------


def test_each_class_prints_exactly_the_lines_it_owes(
    every_class: contract.Profile,
) -> None:
    """The whole sentence, line for line, for all three classes.

    Substring assertions let a continuation line be reworded or dropped
    without a test noticing; these pin every line the class emits.
    """
    assert rendering._made_up_lines(_column(every_class, "note"), 11) == [
        "  synthtwin MADE UP all 240 of this column's present value(s).",
        "  They were built to meet the facts your description",
        "  publishes and nothing else; the sections above name every",
        "  such fact the twin could not meet. A number you compute",
        "  from these cells describes synthtwin's invention and says",
        "  nothing about your table.",
    ]
    assert rendering._made_up_lines(_column(every_class, "region"), 11) == [
        "  synthtwin MADE UP 7 of this column's 240 present value(s):",
        "  the labels and spellings fewer than 11 rows share are not in",
        "  your description, so the twin carries neutral stand-ins at",
        "  their counts instead. The other 233 are value(s) your",
        "  description publishes. A number you compute from the",
        "  made-up cells describes synthtwin's invention and says",
        "  nothing about your table.",
    ]
    assert rendering._made_up_lines(_column(every_class, "measure"), 11) == [
        "  synthtwin MADE UP 1 of this column's 240 present value(s):",
        "  your description counts those cells but carries no value",
        "  for them, so the twin writes counted stand-ins in their",
        "  place. The other 239 were built from the facts your",
        "  description publishes. A number you compute from the",
        "  made-up cells describes synthtwin's invention and says",
        "  nothing about your table.",
    ]


def test_no_class_sentence_claims_the_twin_met_what_it_published(
    every_class: contract.Profile, page: str
) -> None:
    """The claim this page cannot make about itself (item P4-C1-F1).

    A twin does not always meet every published fact -- the deviation
    list two sections up is where it says which -- so a sentence
    asserting that the invented cells MEET the counts can contradict
    the same page. Every class sentence says what the cells were built
    to meet and points at the section that answers the other question.
    """
    for name in ("code", "note", "region", "measure", "seen"):
        said = _block(page, name)
        for line in said:
            assert "meets its counts" not in line
            assert "carry the counts" not in line
    assert "were built to meet the facts your" in page
    assert "the sections above name every" in page


# -- the shapes the first fixture did not reach ------------------------


def test_a_label_column_the_floor_withheld_entirely_is_all_invented(
    tmp_path: pathlib.Path,
) -> None:
    """Every level held back means no published spelling at all.

    The edge amendment A-P4-2 settles: reading the role alone put this
    column in the partly-invented class, and the page then told the
    reader some of its cells were values their description publishes.
    There are none -- the description publishes no label for it.
    """
    header = ["one"]
    rows = [["only"] for _place in range(4)] + [[""] for _place in range(40)]
    loaded = _described(tmp_path, fixtures.rows_to_csv(header, rows))
    column = _column(loaded, "one")
    facts = column.facts
    assert isinstance(facts, contract.LabelFacts)
    # The producer published no level and held the four rows back.
    assert facts.levels == ()
    assert facts.suppressed_rows == column.n_present == 4
    assert rendering._made_up_class(column) == EVERYTHING
    page = rendering.report(loaded, generation.generate(loaded, SEED))
    assert "MADE UP all 4 of this column's present value(s)" in page
    assert "1 of the 1 column(s) hold nothing but values" in page
    assert "0 more column(s) hold some made-up cells beside" in page


def test_a_numeric_column_counts_every_kind_of_uncarried_cell(
    tmp_path: pathlib.Path,
) -> None:
    """Out of range and contradictory count beside not-a-number.

    The first fixture reached only the last of the three, so the other
    two arms of `_uncarried_cells` were asserted by nobody.
    """
    header = ["measure"]
    rows: list[list[str]] = []
    for place in range(400):
        if place == 1:
            rows = rows + [["1e999"]]
        elif place == 2:
            rows = rows + [["(-7)"]]
        elif place == 3:
            rows = rows + [["not recorded"]]
        else:
            rows = rows + [[str(10 + place % 50)]]
    loaded = _described(tmp_path, fixtures.rows_to_csv(header, rows))
    column = _column(loaded, "measure")
    assert column.n_out_of_range == 1
    assert column.n_contradictory == 1
    assert column.n_not_numeric == 1
    assert rendering._uncarried_cells(column) == 3
    assert rendering._made_up_class(column) == UNCARRIED
    page = rendering.report(loaded, generation.generate(loaded, SEED))
    assert "MADE UP 3 of this column's 400 present value(s)" in page


# -- the screen sentence, pinned whole ---------------------------------


def test_the_screen_sentence_is_pinned_whole(
    every_class: contract.Profile,
) -> None:
    """Every word of the one line a person reads before the twin.

    P4-D2 asks for exact-shape tests, and the screen is the one surface
    with no golden behind it: the report, the description and the
    quality report all have their bytes pinned, the screen has only
    this. A substring assertion left the rest of the sentence free to
    say anything at all (review item P4-C2-F2), so the whole of it is
    written out here and a change to any word of it turns this red.
    """
    assert rendering.made_up_warning(every_class) == (
        "2 of this twin's 7 column(s) hold nothing but values synthtwin "
        "made up, and 3 more column(s) hold some made-up cells beside "
        "values your description publishes. The report says which, and "
        "how many, column by column."
    )


# -- the variant-only invention path -----------------------------------


def test_a_label_whose_every_spelling_is_below_the_floor_is_all_invented(
    tmp_path: pathlib.Path,
) -> None:
    """The second route amendment A-P4-2 names, and the one no test had.

    No level is suppressed here: one folded label covers every present
    row, so it is published. What the floor holds back is every
    SPELLING of it -- each written by too few rows to name -- so
    `variants` is empty, `variants_withheld` carries them all, and the
    generator invents every cell. Deleting the withheld-variant loop
    from `_held_back_cells` reds this test AND the producer/loaded
    agreement test below it -- two, not one: the summary's own helper
    keeps the right answer while the renderer's loses it, which is
    exactly the disagreement that test exists to catch (measured;
    review items P4-C2-F4 and P4-C3-F4).
    """
    header = ["sort_of"]
    rows: list[list[str]] = []
    # Twenty-two rows over eleven CASE spellings of one word: every
    # spelling folds to the same label, so one level is published, and
    # each spelling is worn by two rows -- far below the floor of
    # eleven -- so every spelling of it is held back.
    for place in range(22):
        rows = rows + [[_cased("kind", place // 2)]]
    loaded = _described(tmp_path, fixtures.rows_to_csv(header, rows))
    column = _column(loaded, "sort_of")
    facts = column.facts
    assert isinstance(facts, contract.LabelFacts)
    assert facts.suppressed_rows == 0, "no level is held back, only spellings"
    assert len(facts.levels) == 1
    assert facts.levels[0].variants == {}
    assert facts.levels[0].variants_withheld != {}
    assert rendering._held_back_cells(facts) == column.n_present == 22
    assert rendering._made_up_class(column) == EVERYTHING
    page = rendering.report(loaded, generation.generate(loaded, SEED))
    assert "MADE UP all 22 of this column's present value(s)" in page


# -- the two representations must agree --------------------------------


def test_the_producers_page_and_the_twins_page_agree_on_what_is_invented(
    tmp_path: pathlib.Path,
) -> None:
    """One rule, two representations, held to the same answer.

    `summary._all_labels_held_back` reads the document the producer is
    about to write; `rendering._held_back_cells` reads the typed
    profile a loader handed back. Neither representation is available
    where the other is, so the arithmetic is written twice -- and a
    change to one that is not a change to the other is caught here
    rather than by a person noticing two pages disagreeing.
    """
    header = ["all_held", "some_held", "none_held"]
    rows: list[list[str]] = []
    for place in range(44):
        rows = rows + [
            [
                # Every spelling below the floor, all folding to one
                # published label: fully invented.
                _cased("kind", place % 11),
                # One rare label beside two published ones: partly.
                (
                    "rare"
                    if place < 7
                    else ("north" if place % 2 else "south")
                ),
                # Two labels, both published: nothing invented.
                "yes" if place % 2 else "no",
            ]
        ]
    text = fixtures.rows_to_csv(header, rows)
    table_path = fixtures.write(tmp_path, "table.csv", text)
    table = reading.read_table(str(table_path))
    document = profile.build_document(table, SETTINGS, [])
    written = fixtures.write_profile(tmp_path, "table-profile.json", document)
    loaded = contract.load_profile(str(written))
    for entry in document["columns"]:
        name = entry["name"]
        column = _column(loaded, name)
        facts = column.facts
        assert isinstance(facts, contract.LabelFacts)
        producer_says = summary._all_labels_held_back(entry)
        twin_says = rendering._made_up_class(column) == EVERYTHING
        assert producer_says == twin_says, (
            f"the producer's page and the twin's page disagree about "
            f"{name}: {producer_says} against {twin_says}"
        )
    # And the fixture is not vacuous: it reaches both answers.
    answers = {
        summary._all_labels_held_back(entry)
        for entry in document["columns"]
    }
    assert answers == {True, False}


def test_the_summary_names_the_label_columns_a_twin_would_wholly_invent(
    tmp_path: pathlib.Path,
) -> None:
    """The rendered page, not the helper behind it (review item P4-C3-F2).

    `test_the_producers_page_and_the_twins_page_agree_on_what_is_invented`
    calls the summary's helper directly, so deleting the one line that
    puts a label column into the rendered list left every Stage 2 test
    green while the page went back to naming none of them -- the exact
    defect P4-C2-F1 reported. This asks the page.

    Three columns, three answers: a label column whose every spelling
    the floor held back IS named; one with a rare label beside two
    published ones is NOT, because its twin carries real labels too;
    and a declared column with no present cell is NOT, because its twin
    holds nothing to invent.
    """
    header = ["all_held", "some_held", "blank"]
    rows: list[list[str]] = []
    for place in range(44):
        rows = rows + [
            [
                _cased("kind", place % 11),
                (
                    "rare"
                    if place < 7
                    else ("north" if place % 2 else "south")
                ),
                "",
            ]
        ]
    table_path = fixtures.write(
        tmp_path, "table.csv", fixtures.rows_to_csv(header, rows)
    )
    document = profile.build_document(
        reading.read_table(str(table_path)), SETTINGS, ["blank"]
    )
    page = summary.render(document, "")
    opened = page.find("If you build a twin from this description")
    assert opened >= 0, "the forward sentence is missing from the page"
    named = page[opened : page.find("column by column.", opened)]
    assert "all_held" in named
    assert "some_held" not in named
    assert "blank" not in named
