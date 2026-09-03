"""Residual R-P4-13, landing L8: numbers and labels in ONE cell space.

THE COLUMN THIS ROLE EXISTS FOR is the long-format panel export, where
`7.2` sits beside `POSITIVE` in the same column. Before this role it
declined to `long_tail_labels`, and that decline is wrong in BOTH
directions -- which is measured here rather than asserted, because it
is the whole reason the role is worth its cost:

* at the DEFAULT floor of one every reading clears the detection line
  and is published as its own level, so the description carries the
  readings themselves and the twin reproduces them exactly;
* at a floor of ELEVEN the levels fall to the two markers and the twin
  holds NO numeric cell at all.

The protective setting destroys the numeric population and the
permissive one carries it verbatim. Neither DESCRIBES it.

WHAT THIS FILE PINS TODAY is the first step of the landing: which
columns take the role, and that the two published counts account for
every present cell. The numeric and label sub-blocks are the landing's
later steps and are NOT yet built -- the register says so, and this
file will grow with them.
"""

import pathlib
import random

import fixtures
from synthtwin import contract, profile, reading, taxonomy


def _described(
    folder: pathlib.Path, values: "list[str]", stem: str = "result", floor: int = 1
):
    """One column through the real reader and producer."""
    path = fixtures.write(
        folder, f"{stem}.csv", fixtures.single_column_table("result", values)
    )
    document = profile.build_document(
        reading.read_table(f"{path}"),
        taxonomy.Settings(small_cell_floor=floor),
        [],
    )
    return document, document["columns"][0]


def _panel(generator, rows, share, texts):
    """Numbers beside markers, in the shape a panel export writes."""
    made = []
    for _row in range(rows):
        if generator.random() < share:
            made.append(generator.choice(texts))
        else:
            made.append(f"{generator.uniform(0.1, 40.0):.1f}")
    return made


def test_a_panel_column_takes_the_role_at_every_floor(
    tmp_path: pathlib.Path,
) -> None:
    """The column the role exists for, and it must not move with the floor.

    The detection line is the publication floor or eleven, whichever is
    larger -- the same line the long tail uses -- so lowering the floor
    cannot widen which columns take this role, and raising it cannot
    take the role away from a column that had it at eleven.
    """
    generator = random.Random(20260903)
    values = _panel(generator, 300, 0.20, ("POSITIVE", "NEGATIVE"))
    for floor in (1, 11, 25):
        _document, block = _described(tmp_path, values, f"panel{floor}", floor)
        assert block["role"] == taxonomy.ROLE_COMPOUND, (floor, block["role"])


def test_every_present_cell_is_in_exactly_one_published_population(
    tmp_path: pathlib.Path,
) -> None:
    """The answer to review item P1-R6-F7, checkable by arithmetic.

    That item deleted a rule which published a distribution over SOME
    of a column's cells and said nothing about the rest, because
    outcome principle 5 forbids describing a column in part. This role
    publishes two counts of cells and they sum to `n_present`, so a
    reader can check that nothing was dropped without trusting the
    prose.
    """
    generator = random.Random(4)
    for share, texts in (
        (0.20, ("POSITIVE", "NEGATIVE")),
        (0.15, ("<0.5", "NOT DETECTED")),
        (0.70, ("POSITIVE", "NEGATIVE", "EQUIVOCAL")),
    ):
        values = _panel(generator, 300, share, texts)
        _document, block = _described(tmp_path, values, f"split{int(share*100)}")
        assert block["role"] == taxonomy.ROLE_COMPOUND, block["role"]
        numeric = block["n_numeric_cells"]
        labels = block["n_label_cells"]
        assert numeric + labels == block["n_present"], (
            numeric, labels, block["n_present"],
        )
        # AND NEITHER HALF IS EMPTY, which is what makes it a compound
        # column rather than one of the two roles it sits between.
        assert numeric > 0 and labels > 0, (numeric, labels)


def test_the_role_moves_no_column_that_already_read_well(
    tmp_path: pathlib.Path,
) -> None:
    """The no-regression side of an exception to the no-regression rule.

    Rule 7b sits above the long tail and free text ON PURPOSE and moves
    columns those two hold today -- that is the exception, and it is
    named in the plan rather than discovered. What it must NOT do is
    reach a column an earlier rule reads well, so the roles that read a
    column better than this one are asserted unchanged.
    """
    generator = random.Random(11)
    numbers = [f"{generator.uniform(1, 50):.1f}" for _each in range(300)]
    labels = [generator.choice(("A", "B", "C")) for _each in range(300)]
    for values, expected, stem in (
        (numbers, taxonomy.ROLE_CONTINUOUS, "numbers"),
        (labels, taxonomy.ROLE_CATEGORICAL, "labels"),
    ):
        for floor in (1, 11):
            _document, block = _described(
                tmp_path, values, f"{stem}{floor}", floor
            )
            assert block["role"] == expected, (stem, floor, block["role"])


def test_a_handful_of_markers_is_enough_and_that_is_the_whole_point(
    tmp_path: pathlib.Path,
) -> None:
    """The commonest lab column, which the first rule written REFUSED.

    A real result column is most often nearly all numeric with a
    HANDFUL of cells below the detection limit -- five `NOT DETECTED`
    in three hundred rows, not forty. The first writing of this rule
    asked the words to clear the same detection line the numbers clear,
    one word shared by eleven rows, which reads plausibly and is
    backwards: it refused exactly that column and went on describing
    none of its 295 readings.

    Measured then: five markers and nine markers both declined, eleven
    worked. A cliff at eleven, on the wrong side of the shape the role
    exists for.

    The words do not have to be publishable for the NUMBERS to deserve
    describing. What matters is that the words are a small SET rather
    than free prose.
    """
    generator = random.Random(5)
    for markers in (5, 9, 40):
        values = [
            f"{generator.uniform(0.1, 40.0):.1f}"
            for _each in range(300 - markers)
        ] + ["NOT DETECTED"] * markers
        generator.shuffle(values)
        _document, block = _described(tmp_path, values, f"rare{markers}")
        assert block["role"] == taxonomy.ROLE_COMPOUND, (markers, block["role"])
        assert block["n_label_cells"] == markers, block["n_label_cells"]


def test_numbers_beside_free_comments_are_still_free_text(
    tmp_path: pathlib.Path,
) -> None:
    """The other side of the same line, and what draws it.

    The close plan asks that "every other present cell folds to a label
    level", which is true of ANY column and so cannot tell a lab result
    from a number beside a free comment. What tells them apart is how
    many DIFFERENT words the text half holds: a small set is markers, a
    large one is prose. The line is the ceiling a set of categories may
    not pass -- the project's own, not one invented here.

    Measured on 300-row columns, holding the numbers steady and varying
    only the number of different words: three or fewer and the column
    is ordinary numbers, because 297 of 300 clears the numeric line;
    four to thirty and it is numbers with labels; thirty-one and up it
    is free text.
    """
    generator = random.Random(77)
    for distinct, expected in (
        (60, taxonomy.ROLE_TEXT),
        (100, taxonomy.ROLE_TEXT),
    ):
        values = [
            f"{generator.uniform(1, 50):.1f}"
            for _each in range(300 - distinct)
        ] + [f"note {number}" for number in range(distinct)]
        generator.shuffle(values)
        for floor in (1, 11):
            _document, block = _described(
                tmp_path, values, f"free{distinct}x{floor}", floor
            )
            assert block["role"] == expected, (distinct, floor, block["role"])


def test_a_word_that_appears_once_is_a_note_and_not_a_label(
    tmp_path: pathlib.Path,
) -> None:
    """A handful of notes is still prose, however small the handful.

    The rule asks whether the text half looks like labels. "A small
    set of different words" is one way of looking like labels -- and
    on its own it lets a FEW clinical notes through, because two or
    five is a small number by any ceiling. Those are not markers, and
    publishing them means publishing somebody's free text verbatim,
    which is the thing the label roles exist to avoid.

    So the text half must REPEAT somewhere: at least one word covering
    more than one row. Five `NOT DETECTED` repeat; five different
    notes do not.

    MEASURED on the policy fixture of P1-R6-F7, which is numbers
    beside all-different notes: at 95 numbers and at 98 the column was
    claimed and its notes would have been published, and it is free
    text at every count now.

    The counts here start at five because four non-numeric cells of
    three hundred is where the numeric line falls: with fewer, the
    column is ordinary numbers and a different rule reads it, which
    this test is not about.
    """
    # FIVE AND UP, because four cells of three hundred is where the
    # numeric line falls: fewer than that and the column is ordinary
    # numbers, which is a different rule reading it correctly.
    generator = random.Random(31)
    for notes in (5, 12, 20):
        values = [
            f"{generator.uniform(1, 50):.3f}"
            for _each in range(300 - notes)
        ] + [
            f"seen in clinic on visit {number}" for number in range(notes)
        ]
        generator.shuffle(values)
        _document, block = _described(tmp_path, values, f"notes{notes}")
        assert block["role"] == taxonomy.ROLE_TEXT, (notes, block["role"])

    # ...AND THE SAME COUNT OF CELLS, all wearing ONE word, is a marker
    # column. The difference is repetition and nothing else.
    for markers in (5, 12, 20):
        values = [
            f"{generator.uniform(1, 50):.3f}"
            for _each in range(300 - markers)
        ] + ["NOT DETECTED"] * markers
        generator.shuffle(values)
        _document, block = _described(tmp_path, values, f"marks{markers}")
        assert block["role"] == taxonomy.ROLE_COMPOUND, (markers, block["role"])


def test_a_coded_field_is_not_a_quantity_however_it_is_spelled(
    tmp_path: pathlib.Path,
) -> None:
    """The numeric half must be a QUANTITY, not a set of codes.

    `1`, `2`, `3` thirty times each beside five `unknown` is a coded
    field. The digits are labels; a mean of 2.0 over them is a sentence
    about nothing, and the suite has held that column as a set of
    categories since long before this role existed.

    The rule asks the text half to look like labels, and this test is
    the other half of the same question: the NUMBERS must look like a
    quantity. The line is the one already used on the words -- a
    population holding no more different values than a set of
    categories may IS a set of categories, whatever it is spelled with
    -- and it is asked of the numeric half over its OWN size, because a
    share of the whole column's rows asks the wrong question of a half.

    Found by the suite: making the category rule stand aside for a
    numeric half took this column with it, and the fix was to ask what
    the numeric half is before claiming it.
    """
    for values, expected in (
        (["1", "2", "3"] * 30 + ["unknown"] * 5, taxonomy.ROLE_CATEGORICAL),
        (
            [str(number) for number in range(1, 8)] * 20 + ["unknown"] * 10,
            taxonomy.ROLE_CATEGORICAL,
        ),
    ):
        _document, block = _described(tmp_path, values, f"codes{len(values)}")
        assert block["role"] == expected, block["role"]


def test_a_coarse_column_is_not_swallowed_by_the_category_rule(
    tmp_path: pathlib.Path,
) -> None:
    """The category rule stands aside for a real numeric half (owner, C).

    A result column recorded coarsely can hold few enough different
    values to pass the category ceiling, and that rule would then claim
    it and describe every reading as a LABEL -- the same defect this
    role exists to repair, arriving one rule earlier. Measured: the
    SAME 3,000 readings beside the same 60 organism names take this
    role at four decimals and were claimed by the category rule at one.

    The category rule now asks THIS rule's own question rather than a
    second one written beside it, so the two cannot come to disagree
    about what a compound column is.
    """
    generator = random.Random(5)
    organisms = [f"organism {number}" for number in range(60) for _each in range(50)]
    for figures in (1, 4):
        values = [
            f"{generator.uniform(0.1, 40.0):.{figures}f}"
            for _each in range(3000)
        ] + list(organisms)
        generator.shuffle(values)
        _document, block = _described(tmp_path, values, f"coarse{figures}")
        assert block["role"] == taxonomy.ROLE_COMPOUND, (figures, block["role"])

    # AND A COLUMN WITH NO NUMERIC HALF IS UNTOUCHED, which is what
    # keeps this an exception rather than a rewrite of the rule.
    labels = [generator.choice(("A", "B", "C")) for _each in range(300)]
    _document, block = _described(tmp_path, labels, "plain")
    assert block["role"] == taxonomy.ROLE_CATEGORICAL, block["role"]


def test_both_halves_are_described_and_not_merely_counted(
    tmp_path: pathlib.Path,
) -> None:
    """THE POINT OF THE ROLE, and the answer to review item P1-R6-F7.

    Two counts that add up say only that a column has two populations.
    They say nothing about either, which is the omission that item
    deleted a rule for, wearing a different hat. What answers it is
    describing BOTH: the numbers get the same quantitative block a
    column of numbers gets, and the words get the same levels a column
    of labels gets.

    Measured against the source: the numeric half's smallest and
    largest are the real ones, its mean sits inside them, and the
    marker is published as a level. Before this role, the same column
    published `levels` and nothing else -- every reading described as a
    label at floor one, and at floor eleven no numeric cell at all.
    """
    generator = random.Random(5)
    readings = [f"{generator.uniform(0.1, 40.0):.3f}" for _each in range(295)]
    values = readings + ["NOT DETECTED"] * 5
    generator.shuffle(values)
    _document, block = _described(tmp_path, values, "panel")
    assert block["role"] == taxonomy.ROLE_COMPOUND, block["role"]

    # THE COUNTS STILL ACCOUNT FOR EVERY CELL, which is what the two
    # descriptions are checked against.
    assert block["n_numeric_cells"] + block["n_label_cells"] == block["n_present"]

    # THE NUMERIC HALF IS THE READINGS AND NOTHING ELSE.
    numbers = [float(reading) for reading in readings]
    assert block["numbers"]["percentiles"]["min"] == min(numbers)
    assert block["numbers"]["percentiles"]["max"] == max(numbers)
    assert min(numbers) < block["numbers"]["mean"] < max(numbers)
    assert block["numbers"]["n_distinct_values"] == len(set(numbers))

    # AND THE LABEL HALF IS THE MARKER.
    assert [level["label"] for level in block["labels"]["levels"]] == [
        "not detected"
    ]


def test_the_described_column_survives_the_round_trip(
    tmp_path: pathlib.Path,
) -> None:
    """The loader reads both halves back, by the readers that wrote them.

    A description nothing can read is not a description. Each half is
    read by the reader for its own kind of column -- and the label half
    needed one of its OWN, because the two beside it ask a different
    role's entry question: the constant-and-binary reader demanded two
    different values of a half that has one, and the long-tail reader
    demanded a level covering eleven rows. Rule 7b decided what this
    half is; a loader re-asking another rule's question would refuse
    descriptions the producer correctly wrote.
    """
    generator = random.Random(5)
    values = [
        f"{generator.uniform(0.1, 40.0):.3f}" for _each in range(295)
    ] + ["NOT DETECTED"] * 5
    generator.shuffle(values)
    document, block = _described(tmp_path, values, "trip")
    written = fixtures.write_profile(tmp_path, "trip-profile.json", document)
    loaded = contract.load_profile(f"{written}")
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.CompoundFacts)
    assert facts.n_numeric_cells == block["n_numeric_cells"]
    assert facts.n_label_cells == block["n_label_cells"]
    assert facts.numbers.mean == block["numbers"]["mean"]
    assert [level.label for level in facts.labels.levels] == ["not detected"]


def test_the_role_is_the_fifteenth_and_names_its_own_shape() -> None:
    """The axes table is a bijection, and this role joins it as itself.

    A consumer routing on the type axis must not be told this column is
    a quantity, because a quarter of its cells are not, nor that it is
    a set of labels, because most of them are numbers.
    """
    assert len(taxonomy.ROLES) == 15, len(taxonomy.ROLES)
    assert taxonomy.ROLE_COMPOUND in taxonomy.ROLES
    shape, quality = taxonomy.ROLE_AXES[taxonomy.ROLE_COMPOUND]
    assert shape == taxonomy.ROLE_COMPOUND, shape
    assert quality == taxonomy.QUALITY_OK, quality
    assert taxonomy.ROLE_COMPOUND in taxonomy.STATISTICAL_TYPES
    # The table is TOTAL over the roles, which is what makes a missing
    # row a red test rather than a surprise at run time.
    assert set(taxonomy.ROLE_AXES) == set(taxonomy.ROLES)
