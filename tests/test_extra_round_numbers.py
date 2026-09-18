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
    """The mean and spread move and the report has to say a statistic is not one.

    MEASURED by the review: the numeric subset's mean and population
    spread go from 187.083333 and 39.033017 to 100 and 3.027650, and both
    files pass all 99 executable checks. Generating this population from
    disclosure-safe aggregates is not built; what is built is the
    sentence that stops a reader trusting the numbers.
    """
    cells = ["alpha"] * 100 + ["100"] * 20
    for value in range(200, 210):
        cells += [str(value)] * 10
    folder = tmp_path / "anchored"
    _block, written, twin_exit, real_exit = _round_trip(
        folder, cells, ("--smallest-group", "11")
    )
    assert twin_exit == 0 and real_exit == 0
    real = _read(cells)
    twin = _read(written)
    assert round(statistics.fmean(real), 6) == 187.083333
    assert round(statistics.pstdev(real), 6) == 39.033017
    # The fidelity is still unmet; what the repair adds is the warning.
    assert abs(statistics.fmean(twin) - statistics.fmean(real)) > 50
    report = (folder / "real-twin-report.txt").read_text(encoding="utf-8")
    assert "is not a fact about your table" in report
    # All three held-back sentences end by warning about a statistic;
    # before this repair only the two unanchored ones did.
    for sentence, warning in (
        (generation._HELD_BACK_NUMBERS_REASON, "not a fact about your table"),
        (generation._HELD_BACK_UNPLACED_REASON, "means nothing about your table"),
        (generation._HELD_BACK_UNSPELLED_REASON, "not a fact about your table"),
    ):
        assert warning in sentence


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
