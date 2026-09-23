"""The carried numbers pass of 2026-09-18: each defect, from its reproduction.

Four fix branches of the extra review round each ran their own area's
tests, and the merged tree went red where one branch's rule reached
another's ground. Every test here is built from the reproduction that
found the defect, states what was measured BEFORE the repair, and turns
red when the repair is withdrawn -- each one was run against the
withdrawn repair before it was committed, and the report of this pass
records which line was reverted and what the test said.

Every table is built by seeded neutral code at runtime (plan D13) and no
value here comes from any real table.
"""

import collections
import math
import pathlib
import random

import pytest

from synthtwin import contract, generation, parsing, profile, reading, taxonomy
from tests import fixtures
from tests.test_extra_round_numbers import _round_trip
from tests.test_generation import _described, _every_role_text


# -- the absorbed notation and the saturated band (the merge skeptic's
#    MAJOR finding 5) -------------------------------------------------


def _absorbed_notation_cells() -> "list[str]":
    """388 positive amounts, eleven in brackets and one written with a minus.

    The merge skeptic's own shape: the positive amounts run 100.00 to
    103.87 at two places, so their grid holds exactly 388 points.
    """
    cells = [f"{100 + index * 0.01:.2f}" for index in range(388)]
    cells += [f"({1.25 + index:.2f})" for index in range(11)]
    return cells + ["-12.25"]


def _boundary_rung(block: "dict", percent: int) -> float:
    """The rung one of a tail block's two boundary percents names.

    The eleven-rung ladder where the percent is one of its own and the
    finer ladder otherwise, which is where the tail rule's boundary
    usually lands (contract 6.7a).
    """
    names = {
        1: "p01", 5: "p05", 10: "p10", 25: "p25", 50: "p50",
        75: "p75", 90: "p90", 95: "p95", 99: "p99",
    }
    if percent in names:
        return block["percentiles"][names[percent]]
    return block["percentiles_between"][f"p{percent:02d}"]


@pytest.mark.parametrize("seed", ["4", "1", "2", "3"])
def test_an_absorbed_notation_leaves_the_twin_every_number(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """The twin held 400 spellings of 399 numbers, and validate exited 3.

    MEASURED before the repair, at seeds 4, 1, 2 and 3 alike: ruling 6
    counts the lone `-12.25` into the brackets, so the census names
    `{"brackets": 12}`; the ladder's third percentile falls inside the
    published empty pair `(-1.25, 100.00)` and put three positive strata
    below 100; the other 385 shared the 388 points of the positive grid,
    two of them on `101.88`, and G6.5 spelled the second one `0101.88`.
    The twin wrote 400 different spellings of 399 different numbers and
    `validate` MISSED `distinct.n_distinct_values` on it while the real
    table passed.

    THE TAIL RULE MOVED WHERE THOSE STRATA LAND (stage 3, landing 3.3).
    The eleven bracketed cells and the lone `-12.25` are the twelve rows
    beyond the low boundary, so the stretch of empty bins now REACHES
    bin 0 and no `empty_edges` pair is published for it: its lower
    neighbour would be a tail value (contract 7.11a as amended), and
    G6.7a walks such a stretch to its own BIN edges instead. The four
    strata the stretch holds therefore stop at the first bin the
    description says holds somebody, on the four hundredths above that
    bin's lower edge, instead of reaching the grid's own 100.00 -- and
    the twin writes 384 of the grid's 388 points beside them. The count
    this test was built for is untouched: 400 numbers, 400 spellings,
    none of them led by a nought.
    """
    block, written, twin_exit, real_exit = _round_trip(
        tmp_path / "absorbed", _absorbed_notation_cells(),
        ("--smallest-group", "11"), seed,
    )
    assert block["negative_notations"] == {"brackets": 11 + 1}
    assert block["n_distinct_values"] == 400
    numbers = collections.Counter(
        parsing.parse_number(cell) for cell in written
    )
    assert len(numbers) == 400, [n for n, k in numbers.items() if k > 1]
    # ...and not one number is written a second way to make up the count.
    assert not [cell for cell in written if cell[:1] == "0"], written
    # The positive band holds one number per positive cell, each on the
    # column's own hundredth, and none of them in a stretch the
    # description says is empty.
    positive = sorted(
        value for value in numbers if value is not None and value > 0
    )
    assert len(positive) == 388
    assert [value for value in positive if value != round(value, 2)] == []
    tails = block["tails"]
    low = _boundary_rung(block, tails["low"]["percent"])
    high = _boundary_rung(block, tails["high"]["percent"])
    assert block["empty_edges"] == []
    assert [
        value
        for value in positive
        if parsing.scale_bin(value, low, high) in block["empty_bins"]
    ] == []
    # The four strata that stretch pushed up stand on the four
    # hundredths above the first held bin's lower edge (G6.7a), and
    # every other value is a point of the source's own grid.
    edge = low + (high - low) * (
        max(block["empty_bins"]) + 1
    ) / parsing.HISTOGRAM_BINS
    pushed = [(math.ceil(edge * 100) + step) / 100 for step in range(4)]
    assert [value for value in positive if value < 100.0] == pushed
    grid = {float(f"{100 + index * 0.01:.2f}") for index in range(388)}
    # ...AND THE DERIVED HIGH END, which is off the source's grid by
    # construction and not by accident (stage 3, method G5.3b). The
    # column's largest value is held by ONE row, so the tail rule
    # publishes no maximum at all and the twin's top cell is derived
    # from what the high tail states -- moved OUTWARD from the boundary
    # and placed on the column's own hundredths, which is a hundredth
    # the source never wrote. It is the only value above the grid, it
    # is a hundredth, and it stands above every point of the grid: a
    # cell inside the source's range would be a value of the table, and
    # that is what this landing stops publishing.
    top = max(positive)
    assert sorted(set(positive) - grid) == pushed + [top]
    assert top == round(top, 2)
    assert top > max(grid)
    assert twin_exit == 0
    assert real_exit == 0


# -- the nearly full band and the push (the repair skeptic's first MAJOR
#    finding, 2026-09-19) --------------------------------------------


def _nearly_full_band_cells() -> "list[str]":
    """300 negative amounts, -5.00 to -7.99, beside 120 far positive ones.

    The repair skeptic's own shape: the positives are drawn by a seeded
    neutral generator between 10 and 900 at two places.
    """
    draw = random.Random(3)
    cells = [f"-{5 + index * 0.01:.2f}" for index in range(300)]
    return cells + [
        f"{value:.2f}"
        for value in draw.sample([unit / 100 for unit in range(1000, 90000)], 120)
    ]


@pytest.mark.parametrize("seed", ["0", "1", "4", "7", "13"])
def test_a_nearly_full_band_leaves_the_twin_every_number(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """The twin held 420 spellings of 419 numbers, and validate exited 3.

    MEASURED before the push, at ten seeds of ten, on this pass's parent
    and on e53d5f4 alike: the ladder put the negative band's last stratum
    at -0.01, so the band's 300 hundredths held 299 strata; two shared
    -5.90, eighty-nine points from the free -5.01 and -5.00, past the
    walk's reach, and G6.5 spelled the second one -05.90. The band fill
    stood aside, because the band has 799 points for 300 strata.
    """
    block, written, twin_exit, real_exit = _round_trip(
        tmp_path / "nearly", _nearly_full_band_cells(),
        ("--smallest-group", "11"), seed,
    )
    assert block["n_distinct_values"] == 300 + 120
    assert block["empty_edges"] == []
    numbers = collections.Counter(parsing.parse_number(cell) for cell in written)
    assert len(numbers) == 300 + 120, [n for n, k in numbers.items() if k > 1]
    # ...and not one number is written a second way to make up the count:
    # every cell is its own number at the column's two places.
    assert [
        cell for cell in written if cell != f"{parsing.parse_number(cell):.2f}"
    ] == []
    assert twin_exit == 0
    assert real_exit == 0


def test_the_push_is_what_holds_the_nearly_full_band(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant: the push withdrawn, and the one collision stays.

    Exactly one number short -- the one collision the walks leave, at
    -5.90 -- and validate names the count, while the real table passes.
    """
    monkeypatch.setattr(
        generation,
        "_pushed_apart",
        lambda facts, layout, rungs, moved, texts, held, figures, keep_whole: (
            moved, texts, held,
        ),
    )
    block, written, twin_exit, real_exit = _round_trip(
        tmp_path / "unpushed", _nearly_full_band_cells(),
        ("--smallest-group", "11"), "4",
    )
    numbers = collections.Counter(parsing.parse_number(cell) for cell in written)
    assert len(numbers) == 300 + 120 - 1
    assert [n for n, k in numbers.items() if k > 1] == [-5.9]
    assert twin_exit == 3
    assert real_exit == 0


# -- the column-wide fill where it alone answers (the repair skeptic's
#    second MAJOR finding) --------------------------------------------


def _point_free_tenths_cells() -> "list[str]":
    """102 one-place readings from -0.5 to 2.8, the whole numbers written bare.

    Every tenth of the range is written at least once, so the published
    ends hold exactly the column's thirty-four numbers; 0 is written once,
    1 twelve times and 2 once, fourteen point-free cells.

    THE TWO TAILS ARE LISTED ONES, and that is what changed for stage 3
    (landing 3.3). The twelve smallest rows hold `-0.5` and `-0.4` and
    the twelve largest hold `2.6`, `2.7` and `2.8`, so both tails are
    few-valued on this column's tenth grid and the description publishes
    the values themselves (contract 6.7a): the ends of the twin are the
    ends of the column, and the thirty-four points between them are the
    thirty-four numbers, which is the standing this witness needs. The
    column that was written here before carried `2.8` once and `-0.2`
    eleven times; its twelve largest rows then held NINE different
    values, no high end was published, the derived end reached 3.0 and
    the grid it left had thirty-six points for thirty-four numbers --
    room enough for the ordinary walks to answer, so the fill under test
    stopped being the one statement that does. The six cells the change
    needed came off `-0.2`, which is neither a tail nor point-free, so
    the census this test reads is the same: fourteen plain and
    eighty-eight decimal of one hundred and two.

    AND EVERY VALUE EITHER TAIL NAMES STANDS ON TWO CELLS OR MORE,
    which the listing rule of plan P4-D346 asks before any tail lists:
    the owner's ruling of 2026-09-22 is about values many people share,
    and it does not reach a value one row holds. `-0.5` and `2.6` held
    ONE cell each here, so the rule refused both tails and took this
    witness's two listed tails with them. One cell moved onto each from
    `-0.4` and `2.8` -- neither point-free, both already outside the
    plain census -- so the column is the same hundred and two cells over
    the same thirty-four numbers and both tails are listed ones again.
    """
    counts = {
        "-0.5": 2, "-0.4": 13, "-0.3": 11, "-0.2": 5, "-0.1": 1,
        "0": 1, "0.1": 1, "0.2": 1, "0.3": 1, "0.4": 1, "0.5": 1,
        "0.6": 1, "0.7": 1, "0.8": 8, "0.9": 1, "1": 12, "1.1": 1,
        "1.2": 1, "1.3": 1, "1.4": 1, "1.5": 4, "1.6": 12, "1.7": 1,
        "1.8": 1, "1.9": 1, "2": 1, "2.1": 1, "2.2": 1, "2.3": 1,
        "2.4": 1, "2.5": 1, "2.6": 2, "2.7": 4, "2.8": 6,
    }
    return [text for text in counts for _copy in range(counts[text])]


@pytest.mark.parametrize("seed", ["4", "7", "1", "0"])
def test_the_column_wide_fill_holds_a_point_free_grid_alone(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """Thirty-four numbers between ends holding exactly thirty-four tenths.

    Neither the band fill nor the push reaches this column -- withdrawn,
    the column-wide fill leaves it short, as the test below shows -- so
    the column-wide fill of plans P4-D147 and P4-D176 is the one
    statement that answers.
    """
    block, written, twin_exit, real_exit = _round_trip(
        tmp_path / "alone", _point_free_tenths_cells(),
        ("--smallest-group", "11"), seed,
    )
    assert block["n_distinct_values"] == 34
    assert block["numeric_styles"] == {
        "plain": 1 + 12 + 1, "decimal": 102 - 14,
    }
    assert block["tails"]["low"]["values"] == [-0.5, -0.4]
    assert block["tails"]["high"]["values"] == [2.6, 2.7, 2.8]
    numbers = collections.Counter(parsing.parse_number(cell) for cell in written)
    assert sorted(numbers) == [(index - 5) / 10 for index in range(34)]
    assert twin_exit == 0
    assert real_exit == 0


def test_the_column_wide_fill_is_what_holds_it(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant: the column-wide fill withdrawn and nothing else.

    Before this test existed the fill could be withdrawn with every test
    and every committed byte unchanged. Withdrawn here, the twin holds
    thirty-three numbers against thirty-four, and validate names it while
    the real table passes -- measured at seeds 4, 7, 1 and 0 alike,
    before stage 3 and again on the listed-tail witness above.
    """
    monkeypatch.setattr(generation, "_saturated_integers", lambda *arguments: None)
    _block, written, twin_exit, real_exit = _round_trip(
        tmp_path / "unfilled", _point_free_tenths_cells(),
        ("--smallest-group", "11"), "4",
    )
    numbers = collections.Counter(parsing.parse_number(cell) for cell in written)
    assert len(numbers) == 34 - 1
    assert twin_exit == 3
    assert real_exit == 0


# -- the compound column's own count (plan P4-D276, amended) -----------


def test_a_compound_column_counts_the_spellings_its_halves_speak_of(
    tmp_path: pathlib.Path,
) -> None:
    """The producer wrote a compound column its own loader refused.

    MEASURED before the repair, at a floor of eleven, on forty exponents
    beside `alpha` 6, `Alpha` 6, `beta` 5 and `Beta` 5: the label half
    published `n_distinct` 3 (P4-D276), the numeric half 40, and the
    column the raw 44 -- and `contract.load_profile` refused it, because
    contract 7.14 holds the column to the two halves added.
    """
    values = (
        [f"{index * 2}e0" for index in range(1, 41)]
        + ["alpha"] * 6 + ["Alpha"] * 6 + ["beta"] * 5 + ["Beta"] * 5
    )
    path = fixtures.write(
        tmp_path,
        "compound.csv",
        fixtures.rows_to_csv(["c"], [[value] for value in values]),
    )
    document = profile.build_document(
        reading.read_table(str(path), small_cell_floor=11),
        taxonomy.Settings(small_cell_floor=11),
        [],
    )
    block = document["columns"][0]
    assert block["role"] == "numbers_with_labels"
    assert block["n_numeric_distinct"] == 40
    assert block["labels"]["n_distinct"] == 1 + 2
    assert block["n_distinct"] == 40 + 1 + 2
    written = fixtures.write_profile(tmp_path, "compound.json", document)
    loaded = contract.load_profile(str(written))
    assert loaded.columns[0].n_distinct == 43


# -- the mode's plain-language note (plan P4-D267) --------------------


def test_the_mode_note_the_every_role_twin_carries_speaks_plainly(
    tmp_path: pathlib.Path,
) -> None:
    """The one note the round added spelled `str` inside a plain word.

    MEASURED before the repair: the every-role twin at seed 7 carries a
    `mode` deviation, and its note said "the stretches your table leaves
    empty" -- which the plain-language guard every deviation note answers
    to reads as the type name `str`. The guard keeps its strength; the
    sentence changed.
    """
    # FLOOR ONE (plan P4-D316): the mode this note is about is one held
    # by fewer than eleven cells, which the default floor withholds.
    described = _described(
        tmp_path,
        _every_role_text(),
        ["record_code"],
        [fixtures.JOINED_COLUMN],
        floor=1,
    )
    twin = generation.generate(described, 7)
    notes = [
        deviation.note
        for deviation in twin.deviations
        if deviation.fact == "mode"
    ]
    assert notes, "the every-role twin no longer reaches the mode's note"
    for note in notes:
        for jargon in ("null", "None", "int", "str", "dtype", "n_rows"):
            assert jargon not in note, (jargon, note)
