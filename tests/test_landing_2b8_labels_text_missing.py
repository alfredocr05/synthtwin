"""Landing 2b.8: closing the review of landing 2b.4.

Every shape here is one of the review's own reproductions, written as it
was written there, and each is a ROUND TRIP: the table is described, a
twin is built, the twin is described again, and both the twin and the
real table are validated. The fact the item was about is asserted
directly -- a census count, a class count, the sentence the report
prints -- rather than a proxy for it, because each of these defects
passed every check that was being made at the time.

Four items of that review are fixed here and gated below. The reviewer's
own numbers are in each docstring, so a regression says what it broke.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import itertools
import pathlib
import random

import pytest

from synthtwin import parsing
from tests.test_stage2_round_trip import _round_trip


def _counted(cells: "list[str]") -> "dict[str, int]":
    seen: "dict[str, int]" = {}
    for cell in cells:
        seen[cell] = (seen[cell] if cell in seen else 0) + 1
    return seen


def _readings_beside_comments(seed: int) -> "list[str]":
    """The reviewer's own table: one-word comments beside `%%.%` readings."""
    draw = random.Random(seed)
    words = (
        "sample return tomorrow record pending comment result "
        "missing repeat review checked"
    ).split()
    return [
        " ".join(draw.choice(words) for _word in range(draw.randrange(1, 4)))
        if draw.random() < 0.55
        else f"{draw.gauss(10, 2):.1f}"
        for _row in range(800)
    ]


# -- item 4: a number given no form may not wear one the census names --


# The draws that give the free-text shape this item is about. A draw of
# the same generator can fall to `long_tail_labels` instead -- 24802 and
# 24806 do -- which is a different role with a different rule, so the
# shape is chosen rather than left to the seed.
@pytest.mark.parametrize("seed", (24801, 24803, 24804, 24805, 24807))
def test_a_number_given_no_form_does_not_overpay_the_census(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """The length rule knew nothing of the census and overpaid `%%.%`.

    The reviewer's reproduction: 800 rows of one-word comments beside
    readings written `10.4`, at a floor of twenty. The description
    publishes `%%.%` on 199 cells and the settlement covers exactly those
    199 -- and then the length rule gave forty-eight groups the census
    owed nothing a length of four, which in the wide band is written
    `%%.%`. The twin wore that form on 247 cells against the published
    199 and failed its own description while the table passed.
    """
    cells = _readings_beside_comments(seed)
    first, second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "forms", cells, ("--smallest-group", "20"), True, "1"
    )
    assert first["role"] == "free_text"
    assert second["role"] == first["role"]
    # THE CENSUS ITSELF, not a count that follows from it.
    for form in first["shape_forms"]:
        if form == "(withheld)":
            continue
        assert second["shape_forms"].get(form) == first["shape_forms"][form], (
            form, first["shape_forms"], second["shape_forms"]
        )
    assert second["n_numeric"] == first["n_numeric"]
    assert second["n_not_numeric"] == first["n_not_numeric"]
    assert (twin_exit, real_exit) == (0, 0)


# -- item 6: a whole-number tier where the published places cannot pay --


@pytest.mark.parametrize("seed", ("125", "4", "9"))
def test_a_rare_whole_number_beside_decimal_readings_stays_a_number(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """Decimal anchors stopped a held-back whole number being a number.

    The reviewer's reproduction, at a floor of eleven. The column
    publishes `5.1` and `5.3`, so the ladder offers one decimal place
    only; the census names `%.%`, so every candidate of that tier is
    stepped past for wearing a named form, and its unasked supply is
    empty. Two cells the table holds as numbers were written as words:
    twenty-five numeric against a published twenty-seven, two checks
    missed, and the table passing its own description.
    """
    cells = (
        ["ab-cd"] * 20 + ["5.1"] * 11 + ["5.3"] * 11
        + ["5.2"] * 3 + ["7"] * 2 + ["retest"] * 4 + ["hold"]
    )
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "tier", cells, ("--smallest-group", "11"), True, seed
    )
    assert first["n_numeric"] == 27
    assert second["n_numeric"] == first["n_numeric"]
    assert second["n_not_numeric"] == first["n_not_numeric"]
    assert (twin_exit, real_exit) == (0, 0)
    # The tier fired: some made-up number is a whole number, which is
    # what the published places could not supply.
    numbers = [
        cell for cell in written
        if parsing.classify_number(cell) == parsing.NUMBER
    ]
    assert len(numbers) == 27
    assert any("." not in cell for cell in numbers), _counted(written)


def test_the_whole_number_tier_is_not_taken_where_the_places_can_pay(
    tmp_path: pathlib.Path,
) -> None:
    """...and a column whose own places pay keeps the table's spelling.

    The tier is a last resort, asked for only where the finished walk
    left the number debt unpaid. A column of `d.d` readings whose
    held-back numbers are all `d.d` must never gain a bare integer: an
    integer in such a column passes the form census and breaks a check
    written against the table's own spelling, which is the first goal.
    """
    draw = random.Random(1200 * 31 + 9)
    cells = [
        draw.choice(["POSITIVE", "NOT DETECTED"]) if draw.random() < 0.3
        else f"{draw.gauss(7, 2):.1f}"
        for _row in range(1200)
    ]
    _first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "places", cells, ("--smallest-group", "20"), True, "9"
    )
    assert (twin_exit, real_exit) == (0, 0)
    for cell in written:
        if parsing.classify_number(cell) != parsing.NUMBER:
            continue
        whole, point, fraction = cell.partition(".")
        assert point == "." and len(fraction) == 1 and whole.isdigit(), cell


# -- item 7: the report may not say a published number was not published --


def test_a_column_publishing_exponents_is_not_told_it_published_none(
    tmp_path: pathlib.Path,
) -> None:
    """The remark said "this column published no number at all".

    It was false: the column publishes `1.1e6` and `1.2e6` on eleven
    rows each. The ladder is built from the PLAIN decimals among the
    published spellings, so an exponent leaves it unanchored -- and the
    sentence written for a column that published nothing was printed for
    a column that published two numbers on twenty-two rows. A reader who
    checks the description finds the numbers and stops believing the
    report.
    """
    folder = tmp_path / "exponents"
    cells = ["alpha"] * 30 + ["1.1e6"] * 11 + ["1.2e6"] * 11 + ["1.3e6"] * 4
    _first, _second, _written, _twin, _real = _round_trip(
        folder, cells, ("--smallest-group", "11"), True, "4"
    )
    reports = sorted(folder.glob("*report*"))
    assert reports, sorted(folder.iterdir())
    printed = reports[0].read_text(encoding="utf-8")
    assert "published no number at all" not in printed
    # ...and it says what IS true instead.
    assert "cannot step from" in printed, printed[-2000:]


# -- item 8: a text stand-in must read as no numeric class at all --


def test_a_text_stand_in_is_never_a_number_of_another_class(
    tmp_path: pathlib.Path,
) -> None:
    """A group owing ORDINARY TEXT was written `47E807`.

    The reviewer's reproduction. The neutrality guard asked only whether
    a candidate was a NUMBER, so the two other numeric classes walked
    through it: a spelling of the census form `%%@%%%` that is a
    well-formed number too large for binary64 was accepted for a text
    group. The twin came back with twenty-seven out-of-range cells
    against a published twenty-five and eighteen text against twenty,
    three checks missed, and the table passing its own description.
    """
    spec = {
        "12e400": 1, "14e400": 5, "15e400": 1, "16e400": 2,
        "17e400": 8, "18e400": 1, "19e400": 2, "20e400": 5,
        "label4": 1, "label5": 1, "label6": 4, "label7": 3, "ALPHA": 11,
    }
    cells: "list[str]" = []
    for value in spec:
        cells += [value] * spec[value]
    first, second, written, _twin_exit, real_exit = _round_trip(
        tmp_path / "standins", cells, ("--smallest-group", "11"), True, "4"
    )
    assert real_exit == 0
    # THE CLASS PARTITION ITSELF (G10.2), which is what the guard is for.
    assert second["n_out_of_range"] == first["n_out_of_range"] == 25
    assert second["n_not_numeric"] == first["n_not_numeric"] == 20
    assert second["n_numeric"] == first["n_numeric"]
    assert second["n_contradictory"] == first["n_contradictory"]
    # No cell written for the text class reads as any numeric class.
    for cell in written:
        if parsing.classify_number(cell) == parsing.NUMBER_OUT_OF_RANGE:
            assert cell.endswith("e999"), cell


# -- the items of that review this landing found already repaired ------


def test_a_fixed_width_label_column_is_refused_not_escalated(
    tmp_path: pathlib.Path,
) -> None:
    """Sixty integers beside sixty three-character words.

    The reviewer measured `0e0` to `9e5` written for this column, a mean
    of 83,333 against the table's -39.5, with validation reporting no
    miss. The integration repair held the code band to its `e0`
    spellings, so the column is REFUSED for want of capacity instead --
    loudly, naming the column and what to do -- which is the outcome the
    base had before landing 2b.4. This pins the refusal so that a later
    change cannot quietly turn it back into a silent widening.
    """
    from tests.test_stage2_round_trip import _exit_of
    from tests import fixtures

    labels = [
        "".join(triple)
        for triple in itertools.islice(
            itertools.product("abcde", repeat=3), 60
        )
    ]
    cells = [str(-10 - index) for index in range(60)] + labels
    folder = tmp_path / "fixed"
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["value"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of([
        "profile", str(table), "--out-dir", str(folder), "--replace",
        "--smallest-group", "11",
    ]) == 0
    # Refused, and not with a crash: exit 1 is the refusal code.
    assert _exit_of([
        "generate", str(folder / "real-profile.json"), "--out-dir",
        str(folder), "--seed", "1", "--replace",
    ]) == 1
    assert not (folder / "real-twin.csv").exists()


# == part 1: a cell of nothing but space wore a spelling (P4-D74) ======
#
# LTM-1 of the spelling audit, with its skeptic's corrections. Every
# shape here is one the audit measured, and each is a ROUND TRIP whose
# assertion is the fact itself: the spelling, at its count, in the twin.
#
# TWO COLUMNS, DELIBERATELY. A table of ONE column holding whitespace-
# only rows is refused today with a message about the file changing
# while it was read -- the streaming pass keeps such a line and
# `pandas.read_csv(skip_blank_lines=True)` drops it. That false refusal
# is named in P4-D74 as carried, not fixed, so these tables carry a
# second column, which is also the shape a real table has.


def _absent_spellings_round_trip(
    folder: pathlib.Path,
    cells: "list[str]",
    flags: "tuple[str, ...]" = (),
    seed: str = "4",
) -> "tuple[dict, dict, list[str], int, int]":
    """Describe, build, describe again, validate the twin and the table."""
    import csv
    import io
    import json

    from tests import fixtures
    from tests.test_stage2_round_trip import _exit_of

    folder.mkdir(parents=True, exist_ok=True)
    filler = [f"row{index}" for index in range(len(cells))]
    rows = [[cells[index], filler[index]] for index in range(len(cells))]
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["value", "other"], rows),
        encoding="utf-8",
        newline="",
    )
    described = ["profile", str(table), "--out-dir", str(folder), "--replace"]
    assert _exit_of(described + list(flags)) == 0
    profile_path = folder / "real-profile.json"
    assert _exit_of([
        "generate", str(profile_path), "--out-dir", str(folder),
        "--seed", seed, "--replace",
    ]) == 0
    twin = folder / "real-twin.csv"
    again = folder / "again"
    again.mkdir()
    copied = again / "twin.csv"
    copied.write_bytes(twin.read_bytes())
    assert _exit_of(
        ["profile", str(copied), "--out-dir", str(again), "--replace"]
        + list(flags)
    ) == 0
    first = json.loads(profile_path.read_text(encoding="utf-8"))["columns"][0]
    second = json.loads(
        (again / "twin-profile.json").read_text(encoding="utf-8")
    )["columns"][0]
    written = [
        row[0]
        for row in csv.reader(
            io.StringIO(twin.read_text(encoding="utf-8")), strict=False
        )
    ][1:]
    checked = folder / "check-twin"
    checked.mkdir()
    twin_exit = _exit_of([
        "validate", str(profile_path), "--twin", str(twin),
        "--out-dir", str(checked), "--replace",
    ])
    real_checked = folder / "check-real"
    real_checked.mkdir()
    real_exit = _exit_of([
        "validate", str(profile_path), "--twin", str(table),
        "--out-dir", str(real_checked), "--replace",
    ])
    return first, second, written, twin_exit, real_exit


def _readings_with_spaces(seed: int) -> "list[str]":
    """The audit's own shape: SPSS and fixed-width SAS write space."""
    draw = random.Random(seed)
    cells: "list[str]" = []
    for _row in range(500):
        pick = draw.random()
        if pick < 0.18:
            cells += [" "]
        elif pick < 0.36:
            cells += ["  "]
        elif pick < 0.50:
            cells += ["\xa0"]
        elif pick < 0.62:
            cells += [""]
        else:
            cells += [f"{draw.randrange(90, 180)}"]
    return cells


@pytest.mark.parametrize("seed", ("4", "7", "13"))
def test_a_column_of_readings_keeps_the_space_its_writer_put_there(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """A space is a mark the file holds, not an empty cell.

    The commonest real-world shape of this defect: SPSS and fixed-width
    SAS exports write system-missing as a single space. The audit
    measured 315 absent cells of a 500-row column of readings, 177 of
    them holding a space, two spaces or a no-break space -- all
    published as `n_missing_blank: 315`, all written empty by the twin,
    and no published fact able to tell the two files apart. Meanwhile
    `pandas.to_numeric` runs on the twin and raises on the table.
    """
    cells = _readings_with_spaces(11)
    first, second, written, twin_exit, real_exit = (
        _absent_spellings_round_trip(tmp_path / "readings", cells, (), seed)
    )
    held = _counted(cells)
    # THE SPELLING, AT ITS COUNT, published rather than merged.
    assert first["missing_by_source"] == {
        " ": held[" "], "  ": held["  "], "\xa0": held["\xa0"]
    }
    # ...and blank now means the EMPTY spelling and nothing else.
    assert first["n_missing_blank"] == held[""]
    assert first["n_missing_withheld"] == 0
    # The twin WRITES each one, at exactly its published count.
    twin_cells = _counted(written)
    for spelling in (" ", "  ", "\xa0"):
        assert twin_cells[spelling] == held[spelling], (spelling, twin_cells)
    assert twin_cells[""] == held[""]
    # The twin's own description says the same thing back.
    assert second["missing_by_source"] == first["missing_by_source"]
    assert second["n_missing_blank"] == first["n_missing_blank"]
    assert (twin_exit, real_exit) == (0, 0)


@pytest.mark.parametrize("seed", ("4", "9"))
def test_a_column_of_labels_keeps_a_tab_and_a_no_break_space(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """The same rule on a label column, with a tab and U+00A0.

    The skeptic's correction to the finder: the merge is not confined to
    numeric columns. A 600-row categorical column published
    `n_missing_blank: 324` where 249 of those cells held a tab, a space
    or a no-break space, and every one came back as an empty cell.
    """
    draw = random.Random(12)
    cells: "list[str]" = []
    for _row in range(600):
        pick = draw.random()
        if pick < 0.15:
            cells += [" "]
        elif pick < 0.28:
            cells += ["\t"]
        elif pick < 0.40:
            cells += ["\xa0"]
        elif pick < 0.52:
            cells += [""]
        else:
            cells += [draw.choice(["mild", "moderate", "severe"])]
    first, second, written, twin_exit, real_exit = (
        _absent_spellings_round_trip(tmp_path / "labels", cells, (), seed)
    )
    held = _counted(cells)
    assert first["role"] == "categorical"
    assert first["missing_by_source"] == {
        "\t": held["\t"], " ": held[" "], "\xa0": held["\xa0"]
    }
    assert first["n_missing_blank"] == held[""]
    twin_cells = _counted(written)
    for spelling in ("\t", " ", "\xa0"):
        assert twin_cells[spelling] == held[spelling], (spelling, twin_cells)
    assert second["missing_by_source"] == first["missing_by_source"]
    assert (twin_exit, real_exit) == (0, 0)


def test_a_whitespace_spelling_below_the_floor_is_pooled_and_not_named(
    tmp_path: pathlib.Path,
) -> None:
    """The floor governs a space exactly as it governs `NA`.

    The disclosure half of P4-D74: admitting these spellings must not
    admit a group too small to name. At a floor of eleven a tab worn by
    three cells is pooled into `n_missing_withheld`, named nowhere, and
    the twin writes those three cells empty rather than tabbed.
    """
    draw = random.Random(21)
    cells = (
        [" "] * 20 + ["\t"] * 3 + [""] * 15
        + [f"{draw.randrange(40, 90)}" for _row in range(400)]
    )
    first, _second, written, twin_exit, real_exit = (
        _absent_spellings_round_trip(
            tmp_path / "floored", cells, ("--smallest-group", "11"), "4"
        )
    )
    assert first["missing_by_source"] == {" ": 20}
    assert first["n_missing_blank"] == 15
    assert first["n_missing_withheld"] == 3
    twin_cells = _counted(written)
    assert twin_cells[" "] == 20
    assert "\t" not in twin_cells, twin_cells
    assert twin_cells[""] == 18
    assert (twin_exit, real_exit) == (0, 0)


def test_a_description_naming_an_empty_spelling_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """C5-N3: the empty spelling has a field, and is never a key.

    A document naming it both ways counts one blank cell twice. The
    mutation keeps the accounting closed -- one cell moved out of
    `n_missing_blank` and into a key of no characters -- so the only
    thing wrong with it is the key itself.
    """
    import json

    from tests import fixtures
    from synthtwin import contract, errors

    folder = tmp_path / "emptykey"
    cells = [" "] * 20 + [""] * 15 + [f"{index % 40}" for index in range(300)]
    _first, _second, _written, _twin, _real = _absent_spellings_round_trip(
        folder, cells, (), "4"
    )
    path = folder / "real-profile.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    column = document["columns"][0]
    assert column["n_missing_blank"] == 15
    column["missing_by_source"][""] = 1
    column["n_missing_blank"] = 14
    # THE BYTES COME FROM THE PRODUCT'S OWN SERIALIZER. A description
    # written any other way is refused one step earlier for not being in
    # the exact form synthtwin writes, and a gate that accepted that
    # refusal would be filing this mutation under the canonicity rule
    # rather than under the rule it is about.
    broken = fixtures.write_profile(folder, "broken-profile.json", document)
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(str(broken))
    said = f"{raised.value}"
    assert "no characters" in said, said
    assert "n_missing_blank" in said, said


def test_the_summary_tells_a_reader_which_cells_held_nothing(
    tmp_path: pathlib.Path,
) -> None:
    """The sentence was false of 195 cells, and the spelling was invisible.

    The plain-language summary said "324 cell(s) with nothing written in
    them" of a column where 249 of them held a tab, a space or a
    no-break space. It counts the EMPTY cells now -- and the whitespace
    spellings stand beside it written out character by character,
    because a report that prints a space shows a count beside nothing
    and a reader cannot tell one space from two.
    """
    cells = [" "] * 30 + ["  "] * 25 + ["\xa0"] * 22 + [""] * 18 + (
        [f"{index % 50 + 10}" for index in range(300)]
    )
    folder = tmp_path / "summary"
    _first, _second, _written, _twin, _real = _absent_spellings_round_trip(
        folder, cells, (), "4"
    )
    printed = (folder / "real-profile.txt").read_text(encoding="utf-8")
    assert "18 cell(s) with nothing written in them" in printed, printed
    assert "\\x20 (30)" in printed, printed
    assert "\\x20\\x20 (25)" in printed, printed
    assert "\\xa0 (22)" in printed, printed
    # ...and the raw no-break space is not what the reader is shown.
    lines = [
        line for line in printed.split("\n")
        if "nothing written in them" in line
    ]
    assert len(lines) == 1, lines
    assert "\xa0" not in lines[0], repr(lines[0])
