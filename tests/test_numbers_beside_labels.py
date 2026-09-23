"""Landing 2b.4's gate: numbers beside labels keep their numbers.

A column of readings beside a few labels is the commonest mixed column a
real table has, and the floor that keeps a rare value out of the
description turned its held-back readings into words: 1,200 rows of
one-decimal readings beside two labels, at a floor of twenty, published
853 numbers and the twin held 359, and the twin failed its own
validation. Code converting the non-label cells to numbers crashed on the
twin and ran on the table. A column of text did worse in silence:
integers near 120 beside comments came back spelled `000...0001` with a
mean near twenty-three, and every check passed.

So every shape here is described, built, and the TWIN IS DESCRIBED
AGAIN; the two descriptions must agree on the class counts and the role,
the twin and the real table must meet the description with nothing
missed, and the numbers the twin writes must sit where the table's do
-- the mean within half of the table's own standard deviation, and that
standard deviation within a fifth. A twin can meet every count and fail
the second goal, and counter integers did exactly that, so the location
is asserted and not only the count.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import pathlib
import random
import statistics

import pytest

from synthtwin import contract, generation, parsing
from tests import fixtures
from tests.test_stage2_round_trip import (
    _exit_of,
    _round_trip,
    at_the_floor,
)

# How far the twin's numbers may sit from the table's: the mean within
# this many of the table's standard deviations, and the standard deviation
# within this share of its own value. Measured again at landing 2b.4's
# repair over the 222 runs of a column of labels that published a number:
# the mean never moved more than 0.42, and the spread stayed inside a fifth
# in 217; the five outside are amounts given and coded amounts beside one to five
# published numbers, named in method G8.3a and not gated here.
MEAN_SHIFT_IN_DEVIATIONS = 0.5
DEVIATION_SHARE = 0.20

COMMENT_WORDS = (
    "patient declined repeat tomorrow see chart result pending sample "
    "recollect called ward nurse informed doctor notified tube broken lab "
    "delay"
).split()
NOTE_WORDS = (
    "see note", "repeat", "clotted", "insufficient", "pending", "redraw",
    "not done", "lab error", "QNS", "cancelled",
)


def _readings(rows: int, draw: random.Random) -> "list[str]":
    """One-decimal readings near seven beside two censoring labels."""
    cells = []
    for _row in range(rows):
        if draw.random() < 0.3:
            cells += [">14.0" if draw.random() < 0.5 else "<4.0"]
        else:
            cells += [f"{draw.gauss(7.1, 1.4):.1f}"]
    return cells


def _potassium(rows: int, draw: random.Random) -> "list[str]":
    return [
        draw.choice(["Hemolyzed", "QNS"]) if draw.random() < 0.3
        else f"{draw.gauss(4.2, 0.5):.1f}"
        for _row in range(rows)
    ]


def _answers(rows: int, draw: random.Random) -> "list[str]":
    """Answers from one to five beside two refusals, mostly refusals."""
    return [
        draw.choice(["Refused", "Don't know"]) if draw.random() < 0.7
        else str(draw.choice([1, 2, 3, 4, 5]))
        for _row in range(rows)
    ]


def _ages(rows: int, draw: random.Random) -> "list[str]":
    return [
        "unknown" if draw.random() < 0.3 else str(int(draw.gauss(55, 15)))
        for _row in range(rows)
    ]


def _integers_beside_comments(
    rows: int, draw: random.Random, share: float = 0.6
) -> "list[str]":
    return [
        " ".join(draw.choice(COMMENT_WORDS) for _word in range(draw.randrange(2, 6)))
        if draw.random() < share
        else str(int(draw.gauss(120, 20)))
        for _row in range(rows)
    ]


def _coded_amounts(
    rows: int, draw: random.Random, share: float = 0.5
) -> "list[str]":
    return [
        draw.choice(["pending", "not given"]) if draw.random() < share
        else draw.choice(["5", "10", "2.5", "20", "7.5"])
        for _row in range(rows)
    ]


def _readings_beside_notes(rows: int, draw: random.Random) -> "list[str]":
    """Readings beside notes, some of which carry a number of their own."""
    cells = []
    for _row in range(rows):
        if draw.random() < 0.5:
            note = draw.choice(NOTE_WORDS)
            if draw.random() < 0.5:
                note = f"{note} {draw.randrange(100)}"
            cells += [note]
        else:
            cells += [f"{draw.gauss(7, 2):.1f}"]
    return cells


def _wide_readings(rows: int, draw: random.Random) -> "list[str]":
    """One-decimal readings near seven whose tail crosses ten, beside two labels.

    The commonest mixed column, and the one the gate shapes above did not
    reach: their readings rarely pass 10.0, so the census never named
    `%%.%` and the walk never had to step past it.
    """
    return [
        draw.choice(["POSITIVE", "NOT DETECTED"]) if draw.random() < 0.3
        else f"{draw.gauss(7, 2):.1f}"
        for _row in range(rows)
    ]


def _given_amounts(rows: int, draw: random.Random) -> "list[str]":
    """Amounts given, written `0.5`, `1`, `1.5` and so on, rare large ones, beside two words."""
    pool = (
        ["0.5"] * 20 + ["1"] * 30 + ["1.5"] * 10 + ["2"] * 25 + ["2.5"] * 5
        + ["3"] * 4 + ["4"] * 3 + ["5"] * 2 + ["10"]
    )
    return [
        draw.choice(["PRN", "held"]) if draw.random() < 0.4
        else draw.choice(pool)
        for _row in range(rows)
    ]


SHAPES = {
    "wide_readings": _wide_readings,
    "given_amounts": _given_amounts,
    "readings": _readings,
    "potassium": _potassium,
    "answers": _answers,
    "ages": _ages,
    "integers_beside_comments": _integers_beside_comments,
    "coded_amounts": _coded_amounts,
    "readings_beside_notes": _readings_beside_notes,
}

# The label cases: a shape, its rows, the floor it is described at and the
# seed that both draws the table and builds the twin. Floors of one, eleven
# and twenty; 150 to 2,500 rows; the commonest shape, readings beside two
# labels, first and most often.
LABEL_CASES = (
    # Landing 2b.4's repair: the census names `%%.%`, and before the rule
    # on what the census could hold the twin wrote `100.3` with a
    # standard deviation of its numbers 2.4 and 2.7 times the table's.
    ("wide_readings", 2500, "11", 3),
    ("wide_readings", 2500, "11", 9),
    # ...and amounts given publishing `0.5` and `1`, whose census names `%.%`,
    # came back as `10.2` with 2.4 to 4 times the spread.
    ("given_amounts", 150, "20", 5),
    ("given_amounts", 150, "20", 9),
    ("given_amounts", 400, "20", 5),
    ("readings", 1200, "20", 3),
    ("readings", 1200, "20", 21),
    # ...and readings whose census names `%.%` and pools a few cells of
    # `%%.%`: a rule refusing every counted form the census does not name
    # left sixteen and nineteen of their numbers written as words.
    ("readings", 1200, "20", 6),
    ("readings", 1200, "20", 7),
    ("readings", 2500, "11", 9),
    ("readings", 2500, "20", 3),
    ("potassium", 2500, "11", 9),
    ("potassium", 2500, "20", 21),
    ("answers", 150, "11", 3),
    ("ages", 1200, "20", 9),
    ("integers_beside_comments", 1000, "11", 3),
    ("coded_amounts", 200, "11", 3),
    ("coded_amounts", 200, "1", 1),
)


def _numbers(cells: "list[str]") -> "list[float]":
    return [
        float(cell) for cell in cells
        if parsing.classify_number(cell) == parsing.NUMBER
    ]


def _opens_with_an_invented_zero(cell: str) -> bool:
    body = cell[1:] if cell[:1] == "-" else cell
    return len(body) >= 2 and body[0] == "0" and body[1].isdigit()


@pytest.mark.parametrize(
    "shape,rows,floor,seed", LABEL_CASES,
    ids=[f"{case[0]}-{case[1]}-floor{case[2]}-seed{case[3]}" for case in LABEL_CASES],
)
def test_numbers_beside_labels_come_back_as_numbers_where_the_table_has_them(
    tmp_path: pathlib.Path, shape: str, rows: int, floor: str, seed: int
) -> None:
    """The class counts, the role and the location of the numbers return."""
    cells = SHAPES[shape](rows, random.Random(rows * 31 + seed))
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "labels", cells, ("--smallest-group", floor), True, str(seed)
    )
    assert first["role"] in ("categorical", "long_tail_labels"), first["role"]
    assert second["role"] == first["role"]
    assert second["n_numeric"] == first["n_numeric"]
    assert second["n_not_numeric"] == first["n_not_numeric"]
    assert twin_exit == 0
    assert real_exit == 0
    real = _numbers(cells)
    twin = _numbers(written)
    assert len(twin) == len(real) == first["n_numeric"]
    spread = statistics.pstdev(real)
    shift = abs(statistics.mean(twin) - statistics.mean(real))
    assert shift <= MEAN_SHIFT_IN_DEVIATIONS * spread, (shift, spread)
    assert abs(statistics.pstdev(twin) - spread) <= DEVIATION_SHARE * spread, (
        statistics.pstdev(twin), spread
    )
    if not any(_opens_with_an_invented_zero(cell) for cell in cells):
        assert not any(_opens_with_an_invented_zero(cell) for cell in written)
    # NO MADE-UP NUMBER IS A WHOLE FIGURE WIDER THAN THE TABLE'S WIDEST.
    assert max(_whole_figures(cell) for cell in _number_cells(written)) <= max(
        _whole_figures(cell) for cell in _number_cells(cells)
    )


def test_one_pooled_word_does_not_buy_a_whole_figure(
    tmp_path: pathlib.Path,
) -> None:
    """One text cell below the floor, beside readings whose tail crosses ten.

    The integration verdict's BLOCKER. The census pooled the one `ab-cd`,
    and the pool was read as permission for any counted form it does not
    name: the twin wrote `100.0` to `100.3`, the spread of its numbers was
    4.91 against the table's 2.01, and both validations passed. Without the
    one text cell the same column's twin had 2.02. The narrow walk comes
    first now.

    WHAT THIS NO LONGER CLAIMS (measured at the merge of the labels
    review's repair into the integration). It used to end by requiring
    the pooled column's twin to BE the twin of the column without the
    word. Plan P4-D160 then refused the pool of one that made the two
    descriptions alike: `{"%%.%": 134, "(withheld)": 1}` named the one
    `ab-cd` by subtraction, and the census now withholds every form,
    `{"(withheld)": 135}`, so the two columns are described differently
    and their twins are drawn differently. What the blocker was about
    is still asserted, and more of it: no made-up number is a whole
    figure wider, the spread holds, the mean holds (7.004 against the
    table's 7.000 at this seed), and every made-up number stands inside
    the table's own range.
    """
    readings = _wide_readings(2500, random.Random(77503))
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "pooled", readings + ["ab-cd"], ("--smallest-group", "11"),
        True, "125",
    )
    assert first["role"] == "categorical"
    assert second["n_numeric"] == first["n_numeric"]
    assert twin_exit == 0 and real_exit == 0
    real = _numbers(readings)
    twin = _numbers(written)
    spread = statistics.pstdev(real)
    assert abs(statistics.pstdev(twin) - spread) <= DEVIATION_SHARE * spread, (
        statistics.pstdev(twin), spread
    )
    assert max(_whole_figures(cell) for cell in _number_cells(written)) <= 2
    # ...AND THE ONE WORD IS NOT POOLED AT ALL SINCE INVARIANT B4c (Codex
    # blocker 2 of the extra round, 2026-09-18; plan P4-D261). The column
    # publishes `n_not_numeric` 770 and names words covering 769 of them,
    # so the one `ab-cd` was a count of one a reader took by subtraction
    # from a sibling total. It is counted as MISSING now, exactly as the
    # ruling's own pool of one is, and with it gone the form census names
    # its one form again -- the same census the control column below
    # writes, which is what P4-D160 refused to write while the word was
    # still in the column.
    assert first["shape_forms"] == {"%%.%": 134}, first["shape_forms"]
    assert first["n_missing"] == 1 and first["n_present"] == 2500
    shift = abs(statistics.mean(twin) - statistics.mean(real))
    assert shift <= MEAN_SHIFT_IN_DEVIATIONS * spread, (shift, spread)
    _f, _s, control, _t, _r = _round_trip(
        tmp_path / "control", readings, ("--smallest-group", "11"), False, "125"
    )
    assert _f["shape_forms"] == {"%%.%": 134}, _f["shape_forms"]
    # AND THE TWO COLUMNS ARE DESCRIBED ALIKE AGAIN, which is half of the
    # assertion this test opened with and lost to P4-D160's pool of one.
    # Invariant B4c counts the lone `ab-cd` as missing rather than pooling
    # it, so the word column's census is the control's census. The twins
    # are still not the same FILE and cannot be: the word column has one
    # row more, and that row is written blank, so the placement words are
    # spent differently. What is the same is every number either twin
    # writes.
    assert sorted(twin) == sorted(_numbers(control))
    # THE RANGE BOUND IT REPLACES WAS A COINCIDENCE AND IS MEASURED HERE
    # RATHER THAN ASSERTED. The stand-in walk of G8.3a steps OUTWARD from
    # the published levels, which run 3.7 to 10.4 on this column, and
    # nothing published bounds it by the table's own ends: both twins
    # reach 13.9 against the table's 13.4 and stop at 2.4 against its 0.8.
    # The assertion that the twin stayed inside the table's range held on
    # the pooled description alone, and held by accident; what is true of
    # both is that no made-up number is a whole figure wider, which is
    # asserted above and is what the blocker was about.
    assert min(twin) >= min(real)
    assert max(twin) == max(_numbers(control))


def _number_cells(cells: "list[str]") -> "list[str]":
    return [cell for cell in cells if parsing.classify_number(cell) == parsing.NUMBER]


def _whole_figures(cell: str) -> int:
    body = cell[1:] if cell[:1] == "-" else cell
    return len(body.partition(".")[0])


def test_the_readings_the_floor_held_back_are_numbers_at_the_published_places(
    tmp_path: pathlib.Path,
) -> None:
    """Every number the twin writes is spelled the way the table's are.

    Integers written into a column whose every number is `d.d` pass the
    form census, because a bare integer wears no form, and break a check
    written against the table's own spelling -- which is the first goal.
    """
    cells = _readings(1200, random.Random(1200 * 31 + 9))
    first, _second, written, _twin, _real = _round_trip(
        tmp_path / "places", cells, ("--smallest-group", "20"), True, "9"
    )
    assert first["role"] == "categorical"
    numbers = [cell for cell in written if parsing.classify_number(cell) == parsing.NUMBER]
    assert numbers
    for cell in numbers:
        whole, point, fraction = cell.partition(".")
        assert point == "." and len(fraction) == 1 and whole.isdigit(), cell


def test_a_column_of_counts_publishing_only_zero_gets_its_rare_counts(
    tmp_path: pathlib.Path,
) -> None:
    """The sign rule lets a published zero reach the positives, and no further."""
    draw = random.Random(77)
    # `none` is a spelling this format reads as absent, so the label here
    # is a word of the column's own.
    cells = (
        ["0"] * 300 + ["not tested"] * 600
        + [str(draw.randrange(1, 7)) for _each in range(60)]
    )
    draw.shuffle(cells)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "zeros", cells, ("--smallest-group", "20"), True, "5"
    )
    assert first["role"] == "categorical"
    assert second["n_numeric"] == first["n_numeric"]
    assert twin_exit == 0 and real_exit == 0
    assert min(_numbers(written)) == 0.0


def test_a_made_up_number_is_never_one_the_profiler_reads_as_absent(
    tmp_path: pathlib.Path,
) -> None:
    """`9999` is stepped past, and the walk takes the next step instead."""
    draw = random.Random(31)
    cells = (
        ["not done"] * 60 + ["9996"] * 12 + ["9997"] * 12 + ["9998"] * 12
        + ["9999"] * 3 + ["10000"] * 2 + ["9995"] * 1
    )
    draw.shuffle(cells)
    first, second, written, twin_exit, _real = _round_trip(
        tmp_path / "sentinel", cells, ("--smallest-group", "11"), False, "5"
    )
    assert first["role"] == "categorical"
    assert second["n_numeric"] == first["n_numeric"]
    assert "9999" not in written
    assert twin_exit == 0
    for refused in ("9999", "-999", "-9999", "9999.0"):
        assert not generation._is_a_usable_stand_in(refused, (), parsing.NUMBER)


def test_a_made_up_number_is_never_a_spelling_another_column_calls_absent(
    tmp_path: pathlib.Path,
) -> None:
    """`--missing-value 5` declared for the table reaches a column that never wrote it.

    The integration verdict: `value` holds labels and three published
    numbers, `other` holds eleven `5`s. The class stand-ins were refused
    only this column's absent spellings, so the twin wrote `5` four times
    in `value`, its description read four present cells fewer, and eight
    checks were missed while the real table passed.
    """
    folder = tmp_path / "holes"
    folder.mkdir()
    table = folder / "real.csv"
    value = ["alpha"] * 30 + ["4"] * 11 + ["6"] * 11 + ["7"] * 4
    other = ["5"] * 11 + ["beta"] * 45
    # AT THE POPULATION FLOOR (plan P4-D341): the command refuses a
    # smaller table and writes nothing. Both columns are padded with
    # `NA`, one of this format's own spellings for "no value", so the
    # PRESENT values of each -- which are the whole shape -- are what
    # they were, and the eleven `5`s the declaration reaches stay
    # eleven.
    value = at_the_floor(value)
    other = at_the_floor(other)
    table.write_text(
        fixtures.rows_to_csv(
            ["value", "other"], [[a, b] for a, b in zip(value, other)]
        ),
        encoding="utf-8",
        newline="",
    )
    flags = ["--smallest-group", "11", "--missing-value", "5"]
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace"] + flags
    ) == 0
    profile = folder / "real-profile.json"
    assert _exit_of(
        ["generate", str(profile), "--out-dir", str(folder), "--seed", "4",
         "--replace"]
    ) == 0
    twin = folder / "real-twin.csv"
    written = [
        line.split(",")[0]
        for line in twin.read_text(encoding="utf-8").splitlines()[1:]
    ]
    assert "5" not in written
    assert len(_number_cells(written)) == 26
    checked = folder / "checked"
    checked.mkdir()
    assert _exit_of(
        ["validate", str(profile), "--twin", str(twin), "--out-dir",
         str(checked), "--replace"]
    ) == 0


def test_a_made_up_number_is_never_a_spelling_the_column_calls_absent(
    tmp_path: pathlib.Path,
) -> None:
    """A declared absent spelling that is a number is stepped past too."""
    draw = random.Random(41)
    cells = (
        ["not done"] * 40 + ["10"] * 20
        + [str(value) for value in (3, 4, 5, 6, 7, 8) for _each in range(12)]
        + ["1"] + ["2"] * 3 + ["9"] * 2 + ["11"]
    )
    draw.shuffle(cells)
    first, second, written, twin_exit, _real = _round_trip(
        tmp_path / "hole", cells,
        ("--smallest-group", "11", "--missing-value", "10"), False, "5",
    )
    assert first["role"] == "categorical"
    assert second["n_numeric"] == first["n_numeric"]
    assert written.count("10") == cells.count("10")
    assert twin_exit == 0


def test_a_column_read_with_a_decimal_comma_writes_its_numbers_with_one(
    tmp_path: pathlib.Path,
) -> None:
    """The class is asked under the grammar the column is read with."""
    draw = random.Random(1200 * 31 + 5)
    cells = [
        cell.replace(".", ",") for cell in _readings(1200, draw)
    ]
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "comma", cells,
        ("--smallest-group", "20", "--decimal-comma", "value"), True, "5",
    )
    assert first["role"] == "categorical"
    assert second["role"] == first["role"]
    assert second["n_numeric"] == first["n_numeric"]
    assert twin_exit == 0 and real_exit == 0
    assert not any("." in cell for cell in written)


def test_numbers_nothing_published_places_are_named_as_such(
    tmp_path: pathlib.Path,
) -> None:
    """A long tail that published none of its readings: which sentence stands.

    RE-TARGETED THREE TIMES. The pooled-scale landing of 2026-09-21
    (plan P4-D301) held the PLACED sentence here, because section 6.3.3
    then published this column's held-back readings' mean and spread;
    the repair pass of the same day withdrew that publication on this
    shape, because a thousand readings on a tenth-of-a-unit grid are
    packed as closely as that grid allows and a pool at its own tightest
    arrangement is NAMED by its mean and its spread; and the owner's
    decision of the same day (plan P4-D302) withdrew the SPREAD, so a
    tight pool names nothing and this column publishes its mean again.

    What this test holds is that the report tells the reader the truth
    of whichever state it is in: the pool's average IS about their
    table and its spread is NOT, because nothing published says how far
    apart the held-back readings lay.
    """
    cells = _readings_beside_notes(1000, random.Random(1000 * 31 + 1))
    first, second, _written, twin_exit, _real = _round_trip(
        tmp_path / "unplaced", cells, ("--smallest-group", "20"), False, "1"
    )
    assert first["role"] == "long_tail_labels"
    assert second["n_numeric"] == first["n_numeric"]
    assert twin_exit == 0
    scale = first["suppressed_numbers"]
    assert sorted(scale) == ["mean", "n_cells"]
    assert scale["n_cells"] == 529
    report = (tmp_path / "unplaced" / "real-twin-report.txt").read_text(
        encoding="utf-8"
    )
    flat = " ".join(report.split())
    assert "IS about your table" in flat
    assert "A SPREAD IS NOT" in flat


@pytest.mark.parametrize("seed", (3, 4))
def test_amounts_nothing_published_places_are_whole_numbers_beside_their_form(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """A column publishing no number, whose census names `%.%`.

    Every one-place number wears the named form, so a number wearing no
    named form has no place to go at one place; it is written as a whole
    number, which wears none. Before the whole-number tier the walk wrote
    `10.0` -- a form the census proves the column never wore -- and
    withdrawn without a tier after it, twenty-four numbers became words.
    """
    cells = _coded_amounts(200, random.Random(200 * 31 + seed), 0.8)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "amounts", cells, ("--smallest-group", "11"), True, str(seed)
    )
    assert first["role"] == "categorical"
    assert not [
        level for level in first["levels"]
        if parsing.classify_number(level["label"]) == parsing.NUMBER
    ]
    assert second["n_numeric"] == first["n_numeric"]
    assert twin_exit == 0 and real_exit == 0
    forms = {parsing.shape_form(cell) for cell in _number_cells(written)}
    assert forms <= {"%.%", ""}, forms


def test_a_number_carrying_an_end_spends_a_spelling_of_its_length(
    tmp_path: pathlib.Path,
) -> None:
    """Twelve one-figure numbers against a family of ten, two carrying an end.

    The length rule places the numbers carrying no end; the two carrying
    the published ends keep theirs. Uncounted, ten more were placed at one
    figure beside the carriers already there, and a family of ten was
    asked for twelve.
    """
    folder = tmp_path / "carriers"
    folder.mkdir()
    table = folder / "real.csv"
    draw = random.Random(71)
    cells = at_the_floor(
        [str(draw.randrange(0, 10)) for _each in range(40)]
        + [
            " ".join(draw.choice(COMMENT_WORDS) for _word in range(3))
            for _each in range(40)
        ]
    )
    table.write_text(
        fixtures.rows_to_csv(["value"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace",
         "--smallest-group", "1"]
    ) == 0
    facts = contract.load_profile(str(folder / "real-profile.json")).columns[0].facts
    assert isinstance(facts, contract.TextFacts)
    assert facts.length.minimum == 1
    digits = generation._BANDS.index(generation._BAND_DIGITS)
    number = generation._CLASSES.index(generation._CLASS_NUMBER)
    fixed = generation._number_lengths(
        facts, tuple([1] * 12), [1] * 12, [number] * 12, [digits] * 12, (0, 1)
    )
    placed = [fixed[place] for place in range(2, 12)]
    assert placed.count(1) == 8, placed
    assert placed.count(2) == 2, placed


def test_the_label_half_of_a_compound_column_owes_no_class(
    tmp_path: pathlib.Path,
) -> None:
    """Pinned at nought, so a later change to the view cannot add numbers."""
    cells = _readings(400, random.Random(400 * 31 + 3))
    first, second, _written, _twin, _real = _round_trip(
        tmp_path / "compound", cells, ("--smallest-group", "1"), False, "3"
    )
    assert first["role"] == "numbers_with_labels"
    assert second["n_label_cells"] == first["n_label_cells"]
    profile = contract.load_profile(str(tmp_path / "compound" / "real-profile.json"))
    view = contract.compound_labels_view(profile.columns[0])
    assert (view.n_numeric, view.n_out_of_range, view.n_contradictory) == (0, 0, 0)
    owed = generation._classes_owed(view, [], False)
    assert max(owed.values()) <= 0


def _described_labels(tmp_path: pathlib.Path) -> "contract.Profile":
    folder = tmp_path / "described"
    folder.mkdir()
    table = folder / "real.csv"
    cells = _readings(1200, random.Random(1200 * 31 + 3))
    table.write_text(
        fixtures.rows_to_csv(["value"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace",
         "--smallest-group", "20"]
    ) == 0
    return contract.load_profile(str(folder / "real-profile.json"))


def _class_reasons(twin: "generation.Twin") -> "set[str]":
    return {
        deviation.note for deviation in twin.deviations
        if deviation.fact == "n_numeric"
    }


def test_a_count_missed_for_want_of_numbers_is_named_for_that(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Two reasons, and each is given only for its own cause."""
    profile = _described_labels(tmp_path)
    assert _class_reasons(generation.generate(profile, 3)) == set()
    monkeypatch.setattr(generation, "_LADDER_STEPS", 0)
    assert _class_reasons(generation.generate(profile, 3)) == {
        generation._CLASS_SUPPLY_REASON
    }


def test_a_count_missed_by_the_split_is_named_for_the_split(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    profile = _described_labels(tmp_path)
    monkeypatch.setattr(
        generation,
        "_class_split",
        # Landing 2b.13 widened the real signature with the census's
        # remaining form debt and the column's grammar, which G8.3a
        # step 1 consults before it accepts an arrangement. The
        # stand-in takes them and ignores them: what this test pins
        # is that a split covering NOTHING is named for the split,
        # which this landing does not touch.
        lambda sizes, debts, supply, owing=None, decimal_comma=False: {},
    )
    assert _class_reasons(generation.generate(profile, 3)) == {
        generation._CLASS_SPLIT_REASON
    }


def test_the_class_split_takes_an_exact_subset_before_the_one_pass_walk(
    tmp_path: pathlib.Path,
) -> None:
    """Six numbers owed by groups of five, three and three are `3 + 3`.

    Taken largest first in one pass, the group of five goes to the
    numbers, nothing else fits, and the column is one number short with
    a note on five rows written as a number. Reachable sums find the
    split the table itself had.
    """
    draw = random.Random(53)
    cells = (
        ["not done"] * 20 + ["5.1"] * 10 + ["5.3"] * 10
        + ["retest"] * 5 + ["5.2"] * 3 + ["5.0"] * 3
    )
    draw.shuffle(cells)
    # DESCRIBED BY THE PRODUCER (plan P4-D341): this shape's ROLE is
    # `long_tail_labels`, which a table grown to the population floor
    # would lose -- the categorical ceiling is a share of the ROWS, so
    # six different values in a hundred rows are a set of categories.
    # The command's floor is not what this test is about.
    first, second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "split",
        cells,
        ("--smallest-group", "6"),
        True,
        "5",
        by_command=False,
    )
    assert first["role"] == "long_tail_labels"
    # The pool the table's own 3, 3 and 5 make (plan P4-D201); the twin
    # writes it as 2, 4 and 5, and six numbers are `2 + 4`.
    assert (first["suppressed_levels"], first["suppressed_rows"]) == (3, 11)
    assert generation.held_back_sizes(3, 11, 6, (6,), (5,)) == (2, 4, 5)
    assert second["n_numeric"] == first["n_numeric"]
    assert twin_exit == 0 and real_exit == 0
    owed = {" number": 6, " out_of_range": 0, " contradictory": 0}
    room = {" number": 3, " out_of_range": 3, " contradictory": 3}
    assert generation._class_split((3, 3, 5), owed, room) == {
        0: " number", 1: " number"
    }


def test_a_form_is_offered_only_to_a_group_of_the_class_it_reads_as() -> None:
    """A word is not asked to wear `%.%`, and a number is not asked at all.

    A number's form is settled exactly beside the walk, so the offer
    skips a number group; and an offer a group could never meet would
    still spend the form's debt and the length budget.
    """
    owing = {"%.%": 10, "@@-@@": 2}
    assert generation._wanted_form(
        owing, 5, 1, False, 3, 9, [10, 10], 1, parsing.NOT_A_NUMBER
    ) == "@@-@@"
    assert generation._wanted_form(
        owing, 3, 1, False, 3, 9, [10, 10], 1, parsing.NUMBER
    ) == "%.%"
    number = generation._CLASSES.index(generation._CLASS_NUMBER)
    asks = generation._form_asks(
        {"%.%": 4}, (2, 2, 1), [3, 3, 3], [1, 1, 1], (2, 2), 3, 3, [0, 0],
        [number, number, number],
    )
    assert asks == ["", "", ""]


def test_the_neutrality_check_asks_the_class_the_stand_in_owes() -> None:
    """Text as it always was; a number must read as one."""
    usable = generation._is_a_usable_stand_in
    assert not usable("5.2")
    assert usable("5.2", (), parsing.NUMBER)
    assert usable("-0.5", (), parsing.NUMBER)
    assert not usable("group-1", (), parsing.NUMBER)
    assert not usable("=5", (), parsing.NUMBER)
    assert not usable("5,2", (), parsing.NUMBER)
    assert usable("5,2", (), parsing.NUMBER, True)
    assert not usable("5.2", ("5.2",), parsing.NUMBER)


# -- a column of text ---------------------------------------------------


def test_the_column_of_readings_beside_notes_that_was_refused_now_generates(
    tmp_path: pathlib.Path,
) -> None:
    """Twenty-five three-character numbers used to be ten too many."""
    cells = _readings_beside_notes(100, random.Random(100 * 31 + 1))
    first, second, _written, _twin, real_exit = _round_trip(
        tmp_path / "refused", cells, ("--smallest-group", "1"), True, "1"
    )
    assert first["role"] == "free_text"
    assert second["n_numeric"] == first["n_numeric"]
    assert real_exit == 0
    assert generation._family_room(
        generation._CLASS_NUMBER, generation._BAND_WIDE, 3, 1
    ) == 100
    spelled = {
        generation._number_at(generation._BAND_WIDE, 3, index)
        for index in range(100)
    }
    assert len(spelled) == 100


@pytest.mark.parametrize("seed", (2, 3))
def test_readings_beside_notes_at_a_high_floor_generate_and_stay_free_text(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """The refusal the triage listed, and the role its first repair lost.

    A thousand rows at a floor of fifty. Before landing 2b.4's repair the
    generator refused these columns -- a hundred and one different
    three-character numbers of the code band beside the one carrying the
    shortest length, where the family holds a hundred. Once built, the
    packing gave every value written once to the numbers, so the twin's
    words were a vocabulary and it was described again as numbers beside
    labels. Both halves are asserted: it generates, and the role returns.
    """
    cells = _readings_beside_notes(1000, random.Random(1000 * 31 + seed))
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "high", cells, ("--smallest-group", "50"), True, str(seed)
    )
    assert first["role"] == "free_text"
    assert second["role"] == first["role"]
    assert second["n_numeric"] == first["n_numeric"]
    assert second["n_not_numeric"] == first["n_not_numeric"]
    assert twin_exit == 0 and real_exit == 0
    assert not any(_opens_with_an_invented_zero(cell) for cell in _number_cells(written))


def test_a_label_of_five_thousand_figures_does_not_stop_the_command(
    tmp_path: pathlib.Path,
) -> None:
    """`1.` and five thousand noughts, beside notes and two readings.

    The integration verdict: the ladder read every published spelling as
    a plain number, and this interpreter refuses to read an integer of
    more than 4,300 figures from text, so `synthtwin generate` raised
    `ValueError` and wrote nothing. Such a spelling is not plain, so the
    ladder is built from the ones that are.
    """
    cells = (
        ["1." + "0" * 5000] * 12 + ["not done"] * 20
        + ["2.0"] * 3 + ["3.0"] * 2
    )
    # ...and described by the producer for the same reason: four
    # different values in a hundred rows are a set of categories, and
    # `long_tail_labels` is the role this test is about.
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "long",
        cells,
        ("--smallest-group", "11"),
        True,
        "1",
        by_command=False,
    )
    assert first["role"] == "long_tail_labels"
    assert len(written) == len(cells)
    assert second["n_numeric"] == first["n_numeric"]
    assert (twin_exit, real_exit) == (0, 0)


def test_a_code_band_number_is_never_multiplied_by_its_exponent(
    tmp_path: pathlib.Path,
) -> None:
    """Sixty integers from -10 to -69 beside sixty three-letter words.

    The integration verdict: the code band held ten `e0` numbers of three
    characters, the family was counted with all ten exponent figures, and
    the twin wrote `0e0` to `9e5` -- mean 83,333 against -39.5 -- with
    every check passing. The family is its `e0` spellings now, so a column
    needing more of them is refused, as it was before landing 2b.4, and a
    family never writes an exponent other than nought.
    """
    for length in (3, 4, 5):
        room = generation._family_room(
            generation._CLASS_NUMBER, generation._BAND_CODE, length, 1
        )
        assert room == generation._plain_number_room(generation._BAND_CODE, length)
        for index in range(min(room, 200)):
            spelled = generation._number_at(generation._BAND_CODE, length, index)
            assert spelled is not None and spelled.endswith("e0"), spelled
    folder = tmp_path / "exponents"
    folder.mkdir()
    table = folder / "real.csv"
    import itertools

    words = ["".join(p) for p in itertools.islice(itertools.product("abcde", repeat=3), 60)]
    cells = [str(-10 - i) for i in range(60)] + words
    table.write_text(
        fixtures.rows_to_csv(["value"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace",
         "--smallest-group", "11"]
    ) == 0
    assert _exit_of(
        ["generate", str(folder / "real-profile.json"), "--out-dir", str(folder),
         "--seed", "1", "--replace"]
    ) == 1
    assert not (folder / "real-twin.csv").exists()


def test_negative_integers_beside_comments_keep_their_size_and_are_named(
    tmp_path: pathlib.Path,
) -> None:
    """A number of the code band carries the exponent nought first.

    Integers near minus forty beside comments came back as `9e5` and
    `7e6`, a mean of 461,046, because the exponent's figure varied before
    the figures in front of it grew. Held to `e0`, a number of the code
    band is as large as its figures, and the report names the spelling.
    """
    # The table the verification of landing 2b.4 reproduced this on, word
    # for word; on it, a band exchange that ignores the census's own
    # `-%%%` misses that form.
    words = COMMENT_WORDS[:9] + ["hemolyzed"] + COMMENT_WORDS[9:]
    draw = random.Random(5205)
    cells = [
        " ".join(draw.choice(words) for _word in range(draw.randrange(2, 6)))
        if draw.random() < 0.4
        else str(int(draw.gauss(-40, 25)))
        for _row in range(400)
    ]
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "negative", cells, ("--smallest-group", "1"), True, "5"
    )
    assert first["role"] == "free_text"
    assert second["n_numeric"] == first["n_numeric"]
    assert twin_exit == 0 and real_exit == 0
    raised = [cell for cell in _number_cells(written) if "e" in cell]
    assert raised
    assert all(cell.endswith("e0") for cell in raised), raised
    assert max(abs(float(cell)) for cell in _number_cells(written)) < 1000
    report = (tmp_path / "negative" / "real-twin-report.txt").read_text(
        encoding="utf-8"
    )
    assert generation._TEXT_EXPONENT_SUBJECT in report


def test_a_number_keeps_its_own_length_where_no_shape_packs_the_counts(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The length rule of step 3a on the path taken where no joint packing exists.

    A description a real table produced always packs, so the path is
    reached here by withdrawing the joint packing; the families are then
    decided one after the other, and a number must still take its own
    length rather than a comment's.
    """
    folder = tmp_path / "fallback"
    folder.mkdir()
    table = folder / "real.csv"
    cells = _integers_beside_comments(150, random.Random(150 * 31 + 3), 0.3)
    table.write_text(
        fixtures.rows_to_csv(["value"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace",
         "--smallest-group", "1"]
    ) == 0
    profile = contract.load_profile(str(folder / "real-profile.json"))
    monkeypatch.setattr(generation, "_joint_allocation", lambda *_given: None)
    column = profile.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.TextFacts)
    groups = generation._groups_of(facts.n_distinct_by_occurrences)
    lengths, _counts, kinds, _bands, carriers, _notes = generation._text_plan(
        column, facts, groups, floor=profile.settings.small_cell_floor
    )
    numbered = [
        lengths[place] for place in range(len(groups))
        if generation._CLASSES[kinds[place]] == generation._CLASS_NUMBER
        and place not in carriers
    ]
    assert numbered
    assert max(numbered) <= 2, max(numbered)


def test_integers_beside_comments_are_short_and_plain_and_named(
    tmp_path: pathlib.Path,
) -> None:
    """No invented leading zero, a number's own length, and a report line."""
    cells = _integers_beside_comments(150, random.Random(150 * 31 + 3), 0.3)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "text", cells, ("--smallest-group", "1"), True, "3"
    )
    assert first["role"] == "free_text"
    assert second["n_numeric"] == first["n_numeric"]
    assert twin_exit == 0 and real_exit == 0
    numbers = [cell for cell in written if parsing.classify_number(cell) == parsing.NUMBER]
    assert len(numbers) == first["n_numeric"]
    assert not any(_opens_with_an_invented_zero(cell) for cell in numbers)
    assert max(len(cell) for cell in numbers) <= 3
    report = (tmp_path / "text" / "real-twin-report.txt").read_text(encoding="utf-8")
    assert generation._TEXT_NUMBERS_SUBJECT in report


def test_a_number_form_of_a_column_of_text_is_paid_in_its_own_band(
    tmp_path: pathlib.Path,
) -> None:
    """The band exchange and the exact form settlement, met with nothing missed."""
    cells = _readings_beside_notes(200, random.Random(200 * 31 + 2))
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "forms", cells, ("--smallest-group", "1"), True, "2"
    )
    assert first["role"] == "free_text"
    assert any(form != "(withheld)" for form in first["shape_forms"])
    assert second["n_numeric"] == first["n_numeric"]
    assert twin_exit == 0 and real_exit == 0
    for form in first["shape_forms"]:
        if form == "(withheld)":
            continue
        worn = sum(
            1 for cell in written
            if parsing.census_form(cell, first["shape_forms"]) == form
        )
        assert worn == first["shape_forms"][form], form
    # A form is filled from a counter, and `%%.%` at step zero is `00.0`.
    numbers = [cell for cell in written if parsing.classify_number(cell) == parsing.NUMBER]
    assert not any(_opens_with_an_invented_zero(cell) for cell in numbers)


def test_numbers_are_moved_into_the_band_their_forms_are_written_in(
    tmp_path: pathlib.Path,
) -> None:
    """The band exchange of G9.5 step 3b, on a column the packing misplaces.

    On this column the packing puts numbers written `7.2` in the code
    band, where no spelling is `%.%`, and the census is missed by fifteen
    cells. Exchanging text groups for number groups of the same number of
    cells brings the miss to one: the one single-cell group that could
    still move carries a published end. Across 113 such columns the
    exchange shrank the miss in 36, from between eight and twenty-five
    cells to between one and three, left the rest unchanged, and never
    made one worse; the cell or two left over is the named limit of that
    step, because a form is not a margin of the packing.
    """
    cells = _readings_beside_notes(100, random.Random(100 * 31 + 20))
    first, second, written, _twin_exit, real_exit = _round_trip(
        tmp_path / "exchange", cells, ("--smallest-group", "1"), True, "1"
    )
    assert first["role"] == "free_text"
    assert second["n_numeric"] == first["n_numeric"]
    assert real_exit == 0
    miss = 0
    for form in first["shape_forms"]:
        if form == "(withheld)":
            continue
        worn = sum(
            1 for cell in written
            if parsing.census_form(cell, first["shape_forms"]) == form
        )
        miss = miss + abs(worn - first["shape_forms"][form])
    assert miss <= 1, miss


def test_no_test_here_throws_away_what_a_command_returned() -> None:
    """Every call of the command runner is compared, as stage 2's are."""
    source = pathlib.Path(__file__).read_text(encoding="utf-8")
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("_exit_of("):
            raise AssertionError(f"a command's exit code is discarded: {stripped}")
