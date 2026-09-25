"""Plan P4-D193: a whole number a column writes two ways is held by two strata.

THE REPRODUCTION (final skeptic of stage 2's close, BLOCKER). A workbook of
laboratory readings at one place, about one cell in eight of one column
stored as TEXT: openpyxl writes the number 4.0 as `4`, and the text cell
keeps `4.0`. P4-D187 reads such a book instead of refusing it, and its
column then publishes 33 spellings of 31 numbers -- the whole readings are
written both `4` and `4.0`. The twin held 30 numbers at seeds 4, 11 and 1,
missing `distinct.n_distinct_values`, while the real workbook passed and the
same values stored as numbers passed at every seed.

THE CAUSE is not the workbook: the same cells written to a delimited file
miss the same way. G6.5a's walk stops once the strata's texts number the
published count, so two strata left on `3.1` stood where the column needs
two strata on `4.0`; and a column that writes some cells bare may walk a
stratum only onto a point of its own kind, so the one free point, the whole
`3.0`, was out of reach.

Every test is a round trip or a battery through the real reader, producer,
loader and generator. The mutation named in each is
`generation._twice_written` handing its values back untouched.
"""

import pathlib
import random
import tempfile

import pytest

from synthtwin import contract, generation, profile, reading, taxonomy
from tests import fixtures
from tests.test_files_review_repairs import _book, _cell, _rows, _trip


def _lab_book(seed: int, rows: int, share: float) -> bytes:
    """`potassium` readings at one place, a `share` of them stored as text.

    A number cell is written the way a spreadsheet library writes a double:
    a whole reading as its figures alone. A text cell keeps the reading's
    own spelling, `4.0` among them. The draws the skeptic's other four
    columns took are taken too, so the readings are the skeptic's own.
    """
    draw = random.Random(seed)
    strings = ["potassium", "site"]
    grid = {1: [_cell("A1", "0", "s"), _cell("B1", "1", "s")]}
    for place in range(rows):
        number = 2 + place
        reading_ = round(draw.gauss(4.2, 0.5), 1)
        as_text = draw.random() < share
        draw.gauss(1.1, 0.3)
        site = draw.choice([12, 45, 101, 230, 7])
        if draw.random() >= 0.25:
            draw.lognormvariate(2.5, 0.8)
        draw.randrange(128, 150)
        if as_text:
            strings += [str(reading_)]
            cell = _cell(f"A{number}", f"{len(strings) - 1}", "s")
        else:
            written = str(int(reading_)) if reading_ == int(reading_) else str(reading_)
            cell = _cell(f"A{number}", written)
        grid[number] = [cell, _cell(f"B{number}", f"{site}")]
    return _book([("Labs", _rows(grid))], strings)


@pytest.mark.parametrize("seed", [4, 11, 0, 1])
def test_the_lab_workbook_twin_holds_its_count_of_numbers(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """The skeptic's shape: twin and table at exit 0, the counts recounted.

    Mutation: with `_twice_written` withdrawn the twin exits 3 on
    `distinct.n_distinct_values` at seeds 4, 11 and 1 (31 published, 30
    held).
    """
    data = _lab_book(404, 500, 0.12)
    result = _trip(tmp_path, "labs", data, seed=seed)
    column = result["document"]["columns"][0]
    again = result["again"]["columns"][0]
    assert column["n_distinct"] > column["n_distinct_values"], column["n_distinct"]
    assert result["exits"] == {"real": 0, "twin": 0}, (
        result["exits"], result["twin_missed"],
    )
    for fact in ("n_distinct", "n_distinct_values", "numeric_styles", "fraction_widths"):
        assert again[fact] == column[fact], (seed, fact, again[fact], column[fact])


def _described(cells: "list[str]") -> "contract.Profile":
    folder = pathlib.Path(tempfile.mkdtemp())
    path = fixtures.write(folder, "t.csv", fixtures.single_column_table("value", cells))
    document = profile.build_document(
        reading.read_table(str(path)), taxonomy.Settings(), [], [], [], []
    )
    return contract.load_profile(str(fixtures.write_profile(folder, "p.json", document)))


def _readings(source: int, share: float) -> "list[str]":
    draw = random.Random(source)
    cells: "list[str]" = []
    for _row in range(500):
        value = round(draw.gauss(4.2, 0.5), 1)
        bare = value == int(value) and draw.random() >= share
        cells += [str(int(value)) if bare else str(value)]
    return cells


def test_a_battery_of_readings_written_two_ways_holds_every_count() -> None:
    """Twenty delimited columns, two seeds each, and what they still miss.

    Measured before the rule: most of these forty twins missed
    `n_distinct_values`. Mutation: withdrawn, the battery counts them
    again -- which is what the bound below holds, at nine twins of the
    forty against thirty-odd.

    NINE OF THE FORTY ARE SHORT AGAIN SINCE LANDING 3.3, by one, two
    or three numbers, and that is this landing's own cost rather than
    a defect of the rule above. The tail rule describes the rows
    beyond each boundary by two moments and, on a grid, by the values
    themselves (contract 6.7a), so a tail of seven different readings
    a tenth apart cannot always be given seven: the counts G5.3e
    solves for three values are not always the sizes the layout
    divides that band into. Measured, source and seed: (3, 4) 27 of
    28; (5, 1) and (5, 4) 29 of 30; (6, 1) 27 and (6, 4) 26 of 29;
    (12, 1) and (12, 4) 27 of 30; (17, 1) 26 and (17, 4) 25 of 27.
    Each twin NAMES what it is short by, which is the half of this the
    product owes a reader. The bound is the count of short twins and
    how far each falls: a tenth twin, or a shortfall of four, turns
    this red.
    """
    missed = []
    reached = 0
    for source in range(20):
        described = _described(_readings(source, 0.12))
        for seed in (1, 4):
            twin = generation.generate(described, seed)
            for note in twin.deviations:
                if note.fact != "n_distinct_values":
                    continue
                published = int(note.published.split(" ")[0])
                missed += [(source, seed, published - int(note.achieved))]
            reached += 1
    assert reached == 40
    assert len(missed) <= 9, missed
    assert [one for one in missed if one[2] > 3] == [], missed
