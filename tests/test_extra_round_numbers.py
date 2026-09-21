"""The extra review round of 2026-09-18, its number items, one test each.

Codex reviewed c5d09d5 once, in four passes. Ten of its items are about
the numbers a description publishes and the numbers a twin writes, and
every one of them is reproduced here from the review's own inputs and
its own figures, so that a later change that withdraws the repair turns
this file red rather than the suite green.

Each test states what the review measured BEFORE the repair, so a reader
comparing the two knows what moved. Every table is built by seeded
neutral code at runtime (plan D13) and no value here comes from any real
table.
"""

import collections
import csv
import io
import json
import pathlib
import statistics
import sys

import pytest

from synthtwin import generation, parsing
from tests import fixtures


def _exit_of(argv: "list[str]") -> int:
    """Run one synthtwin command in this process and return its exit code."""
    from synthtwin import cli

    before = sys.argv
    sys.argv = ["synthtwin"] + argv
    try:
        code = cli.main()
    except SystemExit as stop:
        return 0 if stop.code is None else int(stop.code)
    finally:
        sys.argv = before
    return code


def _round_trip(
    folder: pathlib.Path,
    cells: "list[str]",
    flags: "tuple[str, ...]" = (),
    seed: str = "4",
) -> "tuple[dict[str, object], list[str], int, int]":
    """Describe, build, and check the twin AND the real table at exit 0."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["value"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace", *flags]
    ) == 0
    description = folder / "real-profile.json"
    assert _exit_of(
        [
            "generate", str(description), "--out-dir", str(folder),
            "--seed", seed, "--replace",
        ]
    ) == 0
    twin = folder / "real-twin.csv"
    written = [
        row[0]
        for row in csv.reader(io.StringIO(twin.read_text(encoding="utf-8")))
        if row
    ][1:]
    checked = folder / "check-twin"
    checked.mkdir()
    twin_exit = _exit_of(
        [
            "validate", str(description), "--twin", str(twin),
            "--out-dir", str(checked), "--replace",
        ]
    )
    looked = folder / "check-real"
    looked.mkdir()
    real_exit = _exit_of(
        [
            "validate", str(description), "--twin", str(table),
            "--out-dir", str(looked), "--replace",
        ]
    )
    block = json.loads(description.read_text(encoding="utf-8"))["columns"][0]
    return block, written, twin_exit, real_exit


def _read(cells: "list[str]") -> "list[float]":
    """Every cell of a column that reads as an ordinary number."""
    found: "list[float]" = []
    for cell in cells:
        if parsing.classify_number(cell) != parsing.NUMBER:
            continue
        value = parsing.parse_number(cell)
        if value is not None:
            found += [value]
    return found


# -- blocker 1: the identifier capacity arithmetic (plan P4-D260) ------


def test_a_layout_is_not_named_when_its_own_supply_is_the_column(
    tmp_path: pathlib.Path,
) -> None:
    """900 three-figure record numbers published the layout every one wears.

    THE REVIEW'S FIRST BLOCKER. `layout_room("%%%")` is 1,000 and the
    small-supply rule asked for `n_distinct` plus the floor, 911, so the
    census published `{"%%%": 900}` beside `n_distinct` 900 -- and only
    100 to 999 can wear that key, because `012` wears `!%%`. The census
    therefore named every cell that could wear the layout, which is the
    source's own value set. The census-compatible supply is 900, which
    does not clear 911, so the layout is not named at all.
    """
    cells = [str(number) for number in range(100, 1000)]
    block, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "identifiers",
        cells,
        ("--identifier", "value", "--smallest-group", "11"),
    )
    assert block["role"] == "identifier"
    assert block["n_distinct"] == 900
    assert "%%%" not in block["layout_forms"], block["layout_forms"]
    assert twin_exit == 0 and real_exit == 0


def test_the_census_supply_of_a_key_of_figures_is_not_its_enumeration_room() -> None:
    """The rule itself, at the three shapes that make it a rule."""
    # A key of figures alone loses its leading noughts to the fill key.
    assert parsing.layout_room("%%%") == 1000
    assert parsing.layout_supply("%%%") == 900
    assert parsing.layout_supply("!%%") == 90
    # One figure alone is the last character, which the fill rule excepts.
    assert parsing.layout_supply("%") == parsing.layout_room("%") == 10
    assert parsing.layout_supply("!!%") == parsing.layout_room("!!%") == 10
    # Every other key answers exactly as the enumeration does.
    for key in ("@%%%%%", "%%-%%", "~~~~", "@@@-%%%%", "%%% %%%"):
        assert parsing.layout_supply(key) == parsing.layout_room(key), key


# -- blocker 2: a sibling total that leaves one row (plan P4-D261) -----


def test_a_class_total_never_leaves_one_held_back_row(
    tmp_path: pathlib.Path,
) -> None:
    """`n_not_numeric` less the published words said one row holds a word.

    THE REVIEW'S SECOND BLOCKER. The pool was three levels over twelve
    rows -- far outside the forced band B4b asks -- and every printed
    count cleared the floor, while 201 less 100 less 100 is one. The twin
    wrote one `group-1` and both files passed all 99 executable checks.
    """
    cells = (
        ["alpha"] * 100 + ["beta"] * 100
        + ["1"] * 5 + ["2"] * 6 + ["gamma"]
    )
    block, written, twin_exit, real_exit = _round_trip(
        tmp_path / "siblings", cells, ("--smallest-group", "11")
    )
    published = {level["label"]: level["count"] for level in block["levels"]}
    assert published == {"alpha": 100, "beta": 100}
    # The word that occurred once is counted as missing, so the sibling
    # total and the published words agree exactly.
    assert block["n_not_numeric"] - 200 == 0
    assert block["n_missing"] == 1 and block["n_present"] == 211
    # ...and the numbers below the floor are still POOLED, because their
    # own total leaves eleven rows over two levels and derives nothing.
    assert block["suppressed_levels"] == 2 and block["suppressed_rows"] == 11
    assert "group-1" not in written
    assert twin_exit == 0 and real_exit == 0


def test_the_loader_refuses_a_class_total_that_leaves_one_row() -> None:
    """B4c is asked of the one rule, `parsing.census_names_one_row`."""
    assert parsing.census_names_one_row({}, [(201, 200)]) == 0
    assert parsing.census_names_one_row({}, [(202, 200)]) == -1
    # A total no published level counts into is not read at all.
    assert parsing.census_names_one_row({}, [(1, 0)]) == -1


# -- item 3: the anchored sentence carries the warning (P4-D266) -------


def test_the_anchored_held_back_sentence_warns_about_statistics(
    tmp_path: pathlib.Path,
) -> None:
    """The sentence that stops a reader trusting this column's numbers.

    RE-TARGETED TWICE. It was written when generating the pooled
    population from disclosure-safe aggregates was not built: the
    numeric subset's mean and population spread go from 187.083333 and
    39.033017 to 100 and 3.027650, both files pass every executable
    check, and what the repair of that day added was the sentence that
    stopped a reader trusting the numbers.

    The pooled-scale landing of 2026-09-21 (plan P4-D301) re-targeted it
    to assert the opposite -- that the twin's numbers ARE the table's --
    and **the repair pass of the same day put it back**, because the
    block that made that true published this column's ten held-back
    values. Its spread, 2.8722813232690143, is exactly the smallest a
    pool of ten distinct whole numbers can have, so the pair names 200
    to 209 outright; contract 6.3.3's looseness rule refuses it, ledger
    K-2B-50 is OPEN again, and the warning sentence is the right one on
    this shape once more.
    """
    cells = ["alpha"] * 100 + ["100"] * 20
    for value in range(200, 210):
        cells += [str(value)] * 10
    folder = tmp_path / "anchored"
    block, written, twin_exit, real_exit = _round_trip(
        folder, cells, ("--smallest-group", "11")
    )
    assert twin_exit == 0 and real_exit == 0
    real = _read(cells)
    twin = _read(written)
    assert round(statistics.fmean(real), 6) == 187.083333
    assert round(statistics.pstdev(real), 6) == 39.033017
    # THE DEFECT IS BACK AND MEASURED, which is ledger K-2B-50's own
    # value: the pool publishes no scale, so the ladder has only the
    # published `100` to step from.
    assert block["suppressed_numbers"] == {
        "n_cells": 0, "mean": None, "spread": None
    }
    assert round(abs(statistics.fmean(twin) - statistics.fmean(real)), 6) == (
        87.083333
    )
    assert round(
        abs(statistics.pstdev(twin) - statistics.pstdev(real)), 6
    ) == 36.005366
    # Both files validate clean, which is why no miss count could ever
    # see this and why only the two numbers can.
    assert (twin_exit, real_exit) == (0, 0)
    report = (folder / "real-twin-report.txt").read_text(encoding="utf-8")
    assert "is not a fact about your table" in report
    # The three sentences that warn about a statistic are all still
    # there, for the three states that reach them: a pool with no
    # published scale, one the ladder cannot place, and one whose
    # column published a number it cannot step from.
    for sentence, warning in (
        (generation._HELD_BACK_NUMBERS_REASON, "not a fact about your table"),
        (generation._HELD_BACK_UNPLACED_REASON, "means nothing about your table"),
        (generation._HELD_BACK_UNSPELLED_REASON, "not a fact about your table"),
    ):
        assert warning in sentence
    # ...and the fourth says the opposite, for the pools that DO publish
    # a scale, which this shape is not one of.
    assert (
        "IS about your table" in generation._HELD_BACK_SCALED_REASON
    )


# -- item 4: the published mode (plan P4-D267) ------------------------


def test_the_published_mode_is_a_number_the_twin_holds(
    tmp_path: pathlib.Path,
) -> None:
    """The mode disappeared and took the median with it.

    MEASURED before the repair: the published mode -0.6 on 210 rows was
    written nowhere, the twin held -0.2 exactly 210 times, and the median
    moved from -0.6 to -0.2 -- accepted as WITHIN-BOUND inside
    [-1.35, 3.05] with no validation miss on either file.
    """
    values = [-1.7, -1.4, -1.3, -0.6, -0.2, 1.1, 3.0, 4.3, 5.5, 6.1, 6.9]
    counts = [150, 170, 150, 210, 10, 10, 160, 60, 40, 180, 60]
    cells: "list[str]" = []
    for value, count in zip(values, counts):
        cells += [f"{value:.1f}"] * count
    block, written, twin_exit, real_exit = _round_trip(
        tmp_path / "mode", cells, ("--smallest-group", "11")
    )
    assert block["mode"] == -0.6 and block["mode_count"] == 210
    tally = collections.Counter(written)
    assert tally["-0.6"] == 210, tally.most_common(5)
    assert statistics.median(_read(written)) == -0.6
    assert twin_exit == 0 and real_exit == 0


# -- item 5: a held-back number keeps its spelling (plan P4-D268) ------


@pytest.mark.parametrize(
    "spellings,form",
    [
        (("+10", "+11", "+12"), "+%%"),
        (("1,100", "1,101", "1,102"), "%,%%%"),
    ],
)
def test_a_held_back_number_is_written_through_its_published_form(
    tmp_path: pathlib.Path, spellings: "tuple[str, str, str]", form: str
) -> None:
    """The twin replaced `+11` and `+12` with `1` and `2`.

    MEASURED before the repair: the census requires forty cells of the
    form and the twin wrote twenty, the source passing its own
    description while the twin missed the count. The grouped column did
    the same, replacing numbers above a thousand with 1 and 2.
    """
    cells = (
        ["alpha"] * 100
        + [spellings[0]] * 20 + [spellings[1]] * 10 + [spellings[2]] * 10
    )
    block, written, twin_exit, real_exit = _round_trip(
        tmp_path / "forms", cells, ("--smallest-group", "11")
    )
    assert block["shape_forms"] == {form: 40}
    worn = 0
    for cell in written:
        if parsing.census_form(cell, block["shape_forms"]) == form:
            worn = worn + 1
    assert worn == 40, collections.Counter(written)
    # ...and the magnitudes are the published ones' own, not 1 and 2.
    for value in _read(written):
        assert abs(value) >= abs(_read([spellings[0]])[0]) - 10
    assert twin_exit == 0 and real_exit == 0


def test_a_number_is_dressed_only_into_a_form_of_its_own_value() -> None:
    """The dressing is built and then VERIFIED, which is what keeps it safe."""
    named = {"+%%": 40, "%,%%%": 40}
    assert generation._dressed_in_form("11", "+%%", named, False) == "+11"
    assert generation._dressed_in_form("1101", "%,%%%", named, False) == "1,101"
    # A form of a different figure count is refused rather than padded.
    assert generation._dressed_in_form("9", "+%%", named, False) == ""
    # ...and one that would change the value is refused by the check.
    assert generation._dressed_in_form("11", "%.%", {"%.%": 2}, False) == ""


# -- item 6: the thousands mark the repair removed (plan P4-D265) ------


@pytest.mark.parametrize("floor", ["1", "11"])
def test_a_distinct_spelling_repair_keeps_every_allocated_mark(
    tmp_path: pathlib.Path, floor: str
) -> None:
    """The twin wrote nineteen grouped cells and invented `+02387.27 kg`.

    MEASURED before the repair: the description requires twenty grouped
    cells and twenty plus signs, the twin wrote nineteen grouped, and
    validation missed 20 against 19 while `generation.deviations` was
    empty.
    """
    texts = [
        "2,387.27 kg", "+2387.27 kg", "3,705.85 kg",
        "+3705.85 kg", "5,446.85 kg", "+5446.85 kg",
    ]
    counts = [7, 5, 7, 10, 6, 5]
    cells: "list[str]" = []
    for text, count in zip(texts, counts):
        cells += [text] * count
    _block, written, twin_exit, real_exit = _round_trip(
        tmp_path / f"marks-{floor}", cells, ("--smallest-group", floor)
    )
    grouped = len([cell for cell in written if "," in cell])
    plussed = len([cell for cell in written if "+" in cell])
    assert grouped == 20 and plussed == 20, collections.Counter(written)
    for cell in written:
        assert "+0" not in cell, cell
    assert twin_exit == 0 and real_exit == 0


# -- item 7: the shape census over surviving cells (plan P4-D262) -----


def test_a_judged_removal_does_not_fail_the_real_table(
    tmp_path: pathlib.Path,
) -> None:
    """The source missed the shape census it was described by.

    MEASURED before the repair: the producer counts the lone `2.0` as
    missing and publishes `shape_forms {"%.%": 68}`; validation recounted
    all 69 written cells of that form and the REAL file had one MISSED
    check while its twin passed.
    """
    cells = ["0.0"] * 19 + ["1.0"] * 19 + ["2.0"] + ["3.0"] * 30 + ["alpha"] * 12
    block, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "judged", cells, ("--smallest-group", "5")
    )
    assert block["shape_forms"] == {"%.%": 68}
    assert block["n_present"] == 80 and block["n_missing"] == 1
    assert real_exit == 0 and twin_exit == 0


# -- item 8: an absorbed decimal spelling (plan P4-D263) --------------


@pytest.mark.parametrize("floor", ["1", "11"])
def test_an_absorbed_decimal_does_not_fail_its_own_source(
    tmp_path: pathlib.Path, floor: str
) -> None:
    """`styles.spelled` failed the original file at the default floor too.

    MEASURED before the repair: the profile absorbs the singleton decimal
    into `numeric_styles {"plain": 31}` with `fraction_widths {}`, the
    original file failed `styles.spelled`, and the seed-4 twin passed.
    """
    cells = [str(1000 + 3 * step) for step in range(30)] + ["1254.00"]
    block, _written, twin_exit, real_exit = _round_trip(
        tmp_path / f"absorbed-{floor}", cells, ("--smallest-group", floor)
    )
    assert block["numeric_styles"] == {"plain": 31}
    assert block["fraction_widths"] == {}
    assert real_exit == 0 and twin_exit == 0


# -- item 9: a pooled style census (plan P4-D264) ---------------------


def test_a_pooled_style_census_admits_its_own_source(
    tmp_path: pathlib.Path,
) -> None:
    """`styles.remainder` demanded the generator's own allocation.

    MEASURED before the repair: the producer publishes
    `numeric_styles {"(withheld)": 20}`, the source failed
    `styles.remainder` because the clause asked for canonical plain
    cells, and the canonical twin passed.
    """
    cells = (
        [f"+{step}.00" for step in range(100, 110)]
        + [f"{step}e0" for step in range(110, 120)]
    )
    block, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "pooled-styles", cells, ("--smallest-group", "11")
    )
    assert block["numeric_styles"] == {"(withheld)": 20}
    assert real_exit == 0 and twin_exit == 0


def test_the_pooled_band_is_a_band_and_not_a_point() -> None:
    """The window rule itself, at its three answers."""
    # Wholly inside the band: the recount's own verdict is reported.
    assert generation is not None
    from synthtwin import validation

    assert validation._window_between((0, 0), 0, 0, 20) is True
    # Wholly outside: reported, and false.
    assert validation._window_between((30, 30), 30, 0, 20) is False
    # Straddling an edge: nothing is said.
    assert validation._window_between((0, 30), 5, 0, 20) is None


# -- item 10: the saturated representable grid (plan P4-D269) ---------


def test_a_saturated_representable_grid_keeps_every_number(
    tmp_path: pathlib.Path,
) -> None:
    """The twin held 120 different texts and 95 different numbers.

    MEASURED before the repair: `[str(i*5e-324) for i in range(1,121)]` at
    a floor of eleven. All 120 source numbers enter the statistics and the
    source passes; the twin's cells were 120 different TEXTS and only 95
    different NUMBERS, correctly reported as MISSED. There is no
    decimal-width grid at this boundary, so the separation walk was
    skipped altogether and the ladder interpolated between rungs one
    representable step apart.
    """
    cells = [str(step * 5e-324) for step in range(1, 121)]
    _block, written, twin_exit, real_exit = _round_trip(
        tmp_path / "subnormal", cells, ("--smallest-group", "11")
    )
    held = {value for value in _read(written)}
    assert len(written) == 120
    assert len(held) == 120, len(held)
    assert twin_exit == 0 and real_exit == 0


def test_a_grid_the_ends_do_not_saturate_is_left_exactly_as_it_was() -> None:
    """The fill is withdrawn whole unless the ends are the strata's own count."""
    layout = generation._NumericLayout(
        sizes=(1, 1, 1),
        starts=(0, 1, 2),
        bands=(
            generation._BAND_POSITIVE,
            generation._BAND_POSITIVE,
            generation._BAND_POSITIVE,
        ),
        raw_budgets=(0, 0, 0, 0),
        folded_budgets=(0, 0, 0, 0),
    )
    # Ends a whole unit apart: an ordinary column, untouched.
    ordinary = [1.0, 1.0, 2.0]
    assert generation._apart_on_the_representable_grid(
        layout, ordinary
    ) == ordinary
    # Ends exactly two representable steps apart: the grid is saturated.
    low = 5e-324
    high = generation._next_representable(
        generation._next_representable(low)
    )
    filled = generation._apart_on_the_representable_grid(
        layout, [low, low, high]
    )
    assert len(set(filled)) == 3 and filled[0] == low and filled[2] == high
    # The step itself, against the grid's own arithmetic.
    assert generation._next_representable(5e-324) == 1e-323
    assert generation._next_representable(1.0) == 1.0 + 2.0 ** -52
    assert generation._next_representable(-1.0) == 0.0


# == the skeptic's pass over the round, 2026-09-18 =====================
#
# Every test below is built from the skeptic's own reproduction and its
# own figures, exactly as the ten above are built from Codex's. Each
# records what was measured BEFORE the repair, so a reader comparing the
# two knows what moved, and each has a mutation check recorded beside it
# in the report.


def _class_total_cells(last: str) -> "list[str]":
    """The skeptic's blocker: four labels and ONE cell of another class."""
    return (
        ["alpha"] * 100 + ["beta"] * 100 + ["gamma"] * 6 + ["delta"] * 5
        + [last]
    )


@pytest.mark.parametrize(
    "last,key",
    [("77", "n_numeric"), ("1e999", "n_out_of_range"), ("(+5)", "n_contradictory")],
)
def test_a_class_no_published_level_reads_into_never_leaves_one_row(
    tmp_path: pathlib.Path, last: str, key: str
) -> None:
    """The count of one survived in the three classes with no published level.

    THE SKEPTIC'S BLOCKER over the repair of Codex's blocker 2. Ruling 5
    was asked through `parsing.census_names_one_row` over the pair
    `(total, covered)` alone, and that pair answers NOTHING where the
    census covers none of the total -- an absent census leaves a reader
    nothing to subtract. A class whose every level the floor held back is
    exactly that shape.

    MEASURED before this repair, at a floor of eleven and seed 4, on all
    three of the classes no published WORD reads into: `alpha` and `beta`
    a hundred rows each, `gamma` six, `delta` five and ONE further cell.
    With `77` the block published `n_numeric` 1 beside two published
    words, `suppressed_levels` 3 over `suppressed_rows` 12 and
    `n_missing` 0 -- so exactly one row of the column reads as a number
    and its value is withheld. With `1e999` the same of `n_out_of_range`
    and with `(+5)` of `n_contradictory`, which names the accounting
    notation ONE individual's cell was written in. All three passed every
    executable check on twin and table alike, and the twin wrote the row.
    """
    block, written, twin_exit, real_exit = _round_trip(
        tmp_path / "class", _class_total_cells(last), ("--smallest-group", "11")
    )
    published = {level["label"]: level["count"] for level in block["levels"]}
    assert published == {"alpha": 100, "beta": 100}
    # The lone row of that class is counted as MISSING, so the class
    # total is nought and there is nothing left to subtract.
    assert block[key] == 0, (key, block[key])
    assert block["n_missing"] == 1 and block["n_missing_withheld"] == 1
    assert block["n_present"] == 211
    # ...and the words below the floor are still POOLED, because their
    # own total leaves eleven rows over two levels and derives nothing.
    assert block["suppressed_levels"] == 2 and block["suppressed_rows"] == 11
    # Nothing of that class is written into the twin.
    assert [cell for cell in written if parsing.classify_number(cell)
            != parsing.NOT_A_NUMBER and cell] == []
    assert twin_exit == 0 and real_exit == 0


def test_the_loader_refuses_a_class_total_of_one_with_no_published_level() -> None:
    """B4c reaches the class the published levels say nothing about.

    The one rule is asked of the class's own held-back rows as a POOL as
    well as of the pair, so the reading that needs no census beside it is
    refused too. The unit answer of `census_names_one_row` is unchanged:
    an absent census still leaves a reader nothing to SUBTRACT.
    """
    from synthtwin import contract, errors

    assert parsing.census_names_one_row({}, [(1, 0)]) == -1
    assert parsing.census_names_one_row({"x": 1}, [(1, 0)]) == -2
    assert parsing.census_names_one_row({"x": 12}, [(212, 200)]) == -1
    mapping = {
        "levels": [
            {"label": "alpha", "count": 100, "share": 0.47},
            {"label": "beta", "count": 100, "share": 0.47},
        ],
        "suppressed_levels": 3,
        "suppressed_rows": 12,
        "n_numeric": 1,
        "n_not_numeric": 211,
        "n_out_of_range": 0,
        "n_contradictory": 0,
    }
    entries = [
        contract.LevelEntry(
            label="alpha", count=100, variants={}, variants_withheld={},
            shape_form_cells=0,
        ),
        contract.LevelEntry(
            label="beta", count=100, variants={}, variants_withheld={},
            shape_form_cells=0,
        ),
    ]
    with pytest.raises(errors.ProfileError) as refusal:
        contract._levels_against_their_classes(
            mapping, "the column named 'value'", entries, False
        )
    assert "B4c" in str(refusal.value)


def test_a_held_back_number_in_an_exponent_form_is_written_through_it(
    tmp_path: pathlib.Path,
) -> None:
    """Every exponent shape of the skeptic's sweep left the twin at exit 3.

    THE SKEPTIC'S SECOND FINDING. `_dressed_in_form` refused any form
    carrying a letter place -- "an exponent is not a decoration" -- so
    item 5's repair reached five of the six spellings and not the sixth.

    MEASURED before this repair, at a floor of eleven and seed 4: a
    hundred and twenty `alpha` beside twenty-six `1235.00e0`, eight
    `1236.00e0`, five `1237.00e0` and nine `1238.00e0` publish
    `shape_forms {"%%%%.%%&%": 48}`; the twin wrote `1235.00e0` 26 times
    and then `1236`, `1234` and `1233` -- 26 cells wearing the form
    against 48 -- and validate exited 3 on the TWIN while the real table
    exited 0. Over thirty randomised held-back-number shapes built from
    Codex's own pattern the twin failed 17 of 30 on c5d09d5, 5 of 30
    after the round (every one of them an exponent), and 0 of 30 now.
    """
    cells = (
        ["alpha"] * 120 + ["1235.00e0"] * 26 + ["1236.00e0"] * 8
        + ["1237.00e0"] * 5 + ["1238.00e0"] * 9
    )
    block, written, twin_exit, real_exit = _round_trip(
        tmp_path / "exponent", cells, ("--smallest-group", "11")
    )
    assert block["shape_forms"] == {"%%%%.%%&%": 48}
    worn = 0
    for cell in written:
        if parsing.census_form(cell, block["shape_forms"]) == "%%%%.%%&%":
            worn = worn + 1
    assert worn == 48, collections.Counter(written).most_common()
    assert twin_exit == 0 and real_exit == 0


def test_a_form_with_a_letter_place_is_dressed_only_into_its_own_value() -> None:
    """The dressing rule at the shapes that make it a rule."""
    named = {"%%%%.%%&%": 48, "%%.%%&%": 47, "%,%%%": 40, "+%%": 40}
    # The figures are fitted and the noughts go at the end...
    assert generation._dressed_in_form(
        "1236", "%%%%.%%&%", named, False
    ) == "1236.00e0"
    # ...and at the front only where the form carries a letter place, so
    # the ladder's own grid can be aligned against the point.
    assert generation._dressed_in_form(
        "9.990", "%%.%%&%", named, False
    ) == "09.99e0"
    assert generation._dressed_in_form("11", "%,%%%", named, False) == ""
    # A dressing that would change the value is refused by the check and
    # not by the form.
    assert generation._dressed_in_form("9.999", "%%.%%&%", named, False) == ""
    assert generation._dressed_in_form("1101", "%,%%%", named, False) == "1,101"
    assert generation._dressed_in_form("11", "+%%", named, False) == "+11"
    # A form with TWO letter places is no number's form and is refused.
    assert generation._dressed_in_form("11", "%&%&%", {"%&%&%": 11}, False) == ""


def test_the_twin_reproduces_held_back_numbers_and_that_is_measured(
    tmp_path: pathlib.Path,
) -> None:
    """The skeptic's third finding, pinned as a measurement for the owner.

    Item 5's repair buys the published form at a price: the ladder is a
    public, deterministic convention over published facts, so on a small
    pool it can land on the source's own held-back values. MEASURED by
    the skeptic over thirty randomised shapes: 7 of 469 held-back cells
    reproduced with the source's own spelling on c5d09d5 against 85 of
    469 after, and 2 of 30 columns reconstructed exactly in values AND
    counts. Codex's own item-5 column is one of the two.

    NO CODE CHANGES ON THIS FINDING: reverting it would undo item 5,
    which Codex demanded. It is measured here so the tension is a fact a
    later reader can see rather than one to be rediscovered, and it is
    put to the owner in plan P4-D268.
    """
    cells = ["alpha"] * 100 + ["+10"] * 20 + ["+11"] * 10 + ["+12"] * 10
    block, written, twin_exit, real_exit = _round_trip(
        tmp_path / "reconstructed", cells, ("--smallest-group", "11")
    )
    published = {level["label"]: level["count"] for level in block["levels"]}
    assert published == {"alpha": 100, "+10": 20}
    assert block["suppressed_levels"] == 2 and block["suppressed_rows"] == 20
    tally = collections.Counter(written)
    # The twin holds the two held-back levels at their own counts, which
    # the description publishes only as a pool of two levels over twenty
    # rows. This assertion is the measurement, not an approval.
    assert tally["+11"] == 10 and tally["+12"] == 10
    assert twin_exit == 0 and real_exit == 0


@pytest.mark.parametrize("floor", ["1", "11"])
def test_an_absorbed_leading_zero_does_not_fail_its_grouped_source(
    tmp_path: pathlib.Path, floor: str
) -> None:
    """A real grouped table failed its own description at exit 3.

    THE SKEPTIC'S FIFTH FINDING, the item 7/8/9 family in a shape those
    three do not reach: item 8's allowance rides on the WIDTH pool and
    this cell's problem is its STYLE.

    MEASURED before this repair, at a floor of one and at eleven alike:
    thirty grouped counts `10,100` to `39,129` beside one `0,472`
    publish `numeric_styles {"plain": 31}`, `thousands_marks {}` and
    `pad_widths {}`; the seed-4 twin passed and validate on the REAL
    TABLE exited 3 with `styles.spelled` MISSED, because ruling 6 counted
    the one `leading_zero` cell into the commonest spelling and the
    recount then found a cell wearing no published style. The ungrouped
    equivalents passed, so it is the grouped column that breaks.
    """
    cells = ["%d,%03d" % (10 + step, 100 + step) for step in range(30)]
    cells += ["0,472"]
    block, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "grouped", cells, ("--smallest-group", floor)
    )
    assert block["numeric_styles"] == {"plain": 31}
    assert block["thousands_marks"] == {}
    assert twin_exit == 0 and real_exit == 0


def test_the_absorbed_style_allowance_is_a_bound_and_not_a_pardon() -> None:
    """Sixty cells outside the census still miss, and fifty do not.

    The allowance is `parsing.absorbed_room`'s own answer bounded by what
    a census of SIX names can hide -- five of the six can have been
    absorbed and each was below the line. On a three-hundred-cell column
    at a floor of eleven that is `min(289, 50)`, so the edge is exactly
    at fifty and the clause can still fail.
    """
    from synthtwin import validation

    assert parsing.absorbed_room({"plain": 300}, 11) == ("plain", 289)
    bound = min(289, 5 * (parsing.census_floor(11) - 1))
    assert bound == 50
    clean = ["%d,%03d" % (10 + step, 100 + (step % 900)) for step in range(300)]
    for spoiled, outside in ((0, 0), (1, 0), (40, 0), (50, 0), (51, 1), (60, 10)):
        cells = [
            "0,%03d" % (100 + place) if place < spoiled else text
            for place, text in enumerate(clean)
        ]
        assert validation._cells_outside_the_styles(
            cells, True, (), ",", 0, bound, ("plain",)
        ) == outside, spoiled


def test_a_band_that_excludes_no_file_is_withheld_and_not_held(
    tmp_path: pathlib.Path,
) -> None:
    """`styles.remainder` was HELD on a census that pools every cell.

    THE SKEPTIC'S SIXTH FINDING. With no named `plain` count the band is
    nought to the pool less the spill, and every numeric cell of the file
    is either counted plain or spilled, so no allocation of the pooled
    cells can fall outside it. MEASURED before this repair: the clause
    read HELD on all four of four hand-built allocations of the same
    twenty cells -- all plain, all exponent, all leading-plus and all
    leading-zero -- beside `0 MISSED` and NO CHECKABLE OBLIGATION WAS
    MISSED, although nothing about the file had been checked.
    """
    from synthtwin import validation

    # The rule itself, at its four answers.
    assert validation._window_between((0, 0), 0, 0, 20) is True
    assert validation._window_between((30, 30), 30, 0, 20) is False
    assert validation._window_between((0, 30), 5, 0, 20) is None
    # ...and the fourth: a band that reaches everything the file could
    # show says nothing at all.
    assert validation._window_between((0, 0), 0, 0, 20, 20) is None
    # A band that starts above nought is untouched, and can still fail.
    assert validation._window_between((30, 30), 55, 30, 50, 55) is False
    cells = ["+%d.00" % step for step in range(100, 110)]
    cells += ["%de0" % step for step in range(110, 120)]
    block, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "pooled", cells, ("--smallest-group", "11")
    )
    assert block["numeric_styles"] == {"(withheld)": 20}
    assert twin_exit == 0 and real_exit == 0
    report = (tmp_path / "pooled" / "check-real" / "real-quality.txt").read_text(
        encoding="utf-8"
    )
    said = [line.strip() for line in report.splitlines()
            if "styles.remainder" in line]
    assert said and all("WITHHELD" in line for line in said), said


def test_the_recount_names_the_marks_the_repair_could_not_keep(
    tmp_path: pathlib.Path,
) -> None:
    """Item 6's second clause ships with a test and a column that reaches it.

    THE SKEPTIC'S SEVENTH FINDING: the recount off the finished text was
    pinned by no test, and forty-eight shapes did not reach it, because
    the visiting order now keeps every allocated mark wherever a column
    holds an unmarked duplicate. A column whose EVERY cell carries the
    mark has none, so the walk must take a mark back and the recount is
    what says so. Three values written grouped-and-plain and
    grouped-and-plussed, forty cells at counts 7, 5, 7, 10, 6, 5: the
    twin writes 38 marked cells against a census of 40, and the
    deviation names the shortfall rather than leaving it silent.
    """
    texts = [
        "2,387.27 kg", "+2,387.27 kg", "3,705.85 kg",
        "+3,705.85 kg", "5,446.85 kg", "+5,446.85 kg",
    ]
    cells: "list[str]" = []
    for text, count in zip(texts, [7, 5, 7, 10, 6, 5]):
        cells += [text] * count
    folder = tmp_path / "all-marked"
    _block, written, _twin_exit, real_exit = _round_trip(
        folder, cells, ("--smallest-group", "11")
    )
    marked = len([cell for cell in written if "," in cell])
    assert marked == 38, collections.Counter(written).most_common()
    assert real_exit == 0
    report = (folder / "real-twin-report.txt").read_text(encoding="utf-8")
    assert "thousands_marks" in report
    assert "the description says: 40" in report
    assert "the twin holds:       38" in report


def test_the_representable_fill_is_withdrawn_where_a_band_would_not_hold() -> None:
    """The sign-band guard of the fill, made load-bearing.

    THE SKEPTIC'S EIGHTH FINDING: only one of the pass's three guards was
    covered. This covers the second. The third -- the early stop `step >
    ceiling` -- is an EQUIVALENT mutant with respect to the cells: the
    walk runs at most one step per stratum either way and
    `grid[total - 1] != ceiling` returns the values untouched, so no test
    of the output can kill it. It is a cost bound and is stated as one.
    """
    low = 5e-324
    high = generation._next_representable(generation._next_representable(low))
    holds = (
        generation._BAND_POSITIVE,
        generation._BAND_POSITIVE,
        generation._BAND_POSITIVE,
    )
    filled = generation._apart_on_the_representable_grid(
        generation._NumericLayout(
            sizes=(1, 1, 1), starts=(0, 1, 2), bands=holds,
            raw_budgets=(0, 0, 0, 0), folded_budgets=(0, 0, 0, 0),
        ),
        [low, low, high],
    )
    assert len(set(filled)) == 3
    # The same column, with one stratum's band saying something the grid's
    # own point would not answer: the pass is withdrawn WHOLE.
    for place, band in (
        (0, generation._BAND_ZERO),
        (1, generation._BAND_NEGATIVE),
        (2, generation._BAND_ZERO),
    ):
        bands = list(holds)
        bands[place] = band
        values = [low, low, high]
        assert generation._apart_on_the_representable_grid(
            generation._NumericLayout(
                sizes=(1, 1, 1), starts=(0, 1, 2), bands=tuple(bands),
                raw_budgets=(0, 0, 0, 0), folded_budgets=(0, 0, 0, 0),
            ),
            values,
        ) == values, band
