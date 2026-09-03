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


def test_numbers_beside_free_comments_are_still_free_text(
    tmp_path: pathlib.Path,
) -> None:
    """The condition the close plan left open, and what it decides.

    The plan asks that "every other present cell folds to a label
    level", which is true of ANY column and so cannot tell a lab result
    from a number beside a free comment. What tells them apart is
    asking the text half to be label-publishing IN ITS OWN RIGHT --
    at least one level reaching the same detection line the numbers
    must reach. A column of readings beside comments that never repeat
    has no such level and stays free text.
    """
    generator = random.Random(77)
    values = []
    for _row in range(300):
        if generator.random() < 0.2:
            values.append(f"note {generator.randint(1, 100000)}")
        else:
            values.append(f"{generator.uniform(1, 50):.1f}")
    for floor in (1, 11):
        _document, block = _described(tmp_path, values, f"free{floor}", floor)
        assert block["role"] == taxonomy.ROLE_TEXT, (floor, block["role"])


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
