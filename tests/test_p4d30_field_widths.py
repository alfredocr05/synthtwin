"""P4-D30: a plain number carries a width, and the VALUE stage reads it.

WHAT THIS FILE PINS, AND WHY EACH PIECE IS HERE. `pad_widths` censuses
the cells written with a redundant zero and `fraction_widths` the
figures after a point, so a cell written `199` was in neither and its
width was published NOWHERE (residuals R-P4-30 and R-P4-35). The key
`field_widths` covers every cell written as a whole number, and method
G6.6 turns it and `pad_widths` together into demands on each stratum's
VALUE, which is what residual R-P4-27 asks for.

**The repair is in the VALUE DRAW and not in either width walk**, so
the witness has to be a whole run: build the CSV, describe it with the
real producer, load it with the real loader, generate, and recount the
twin's own finished cells. Every table here is built by the seeded
neutral builders of `fixtures.py` (plan D13); no committed data file is
read.

THE MEASUREMENT EACH WITNESS STANDS ON, taken on this tree before the
landing and after it, forty seeds each:

* the dental column, 14 seeds in 40 writing a core at a width the
  source never used and 56 cores misplaced in all, against 0 in 40;
* the vaccine column, 20 in 40 and SILENT, against 2 in 40 with the
  twin's own report naming both.

`test_the_dental_codes_keep_their_width_at_every_seed` is the one that
turns red when the pass alone is withdrawn.
"""

import pathlib

import fixtures
from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    summary,
    taxonomy,
    validation,
)

# THE SEEDS, FIXED AND WRITTEN OUT. A witness that draws its own seeds
# is a witness whose failure nobody can reproduce.
SEEDS = (3, 11, 29, 47, 101)

# `D` plus four figures. Thirty-one codes wear a redundant zero and
# fifty-four do not; all eighty-five are four figures wide, which is
# what a dental code column IS and is the shape R-P4-30 was opened on.
PADDED_CODES = (120, 140, 150, 170, 180, 185, 210, 220, 230, 240, 250,
                260, 270, 272, 274, 277, 330, 350, 351, 460, 470, 502,
                601, 602, 603, 701, 702, 703, 706, 707, 708)
PLAIN_CODES = (1110, 1120, 1206, 1208, 1351, 1354, 2140, 2150, 2160,
               2161, 2330, 2331, 2332, 2335, 2391, 2392, 2393, 2394,
               2740, 2750, 2751, 2752, 2790, 2791, 2792, 2910, 2915,
               2920, 2929, 2930, 2940, 2950, 2951, 2952, 2954, 2960,
               3220, 3310, 3320, 3330, 4210, 4211, 4240, 4241, 4260,
               4261, 4341, 4342, 4355, 4910, 5110, 5120, 5211, 5212)


def _dental_rows() -> "list[str]":
    """300 cells, 97 of them padded, every one four figures wide."""
    rows = ["D0%03d" % PADDED_CODES[index % len(PADDED_CODES)]
            for index in range(97)]
    rows = rows + ["D%04d" % PLAIN_CODES[index % len(PLAIN_CODES)]
                   for index in range(203)]
    # A FIXED INTERLEAVE RATHER THAN A SHUFFLE, so the table is a
    # function of this file and of nothing else.
    return [rows[(index * 97) % 300] for index in range(300)]


def _gap_rows() -> "list[str]":
    """300 four-figure codes with a WIDE GAP between the two halves.

    THE SHAPE THE PADDED CELLS' OWN DEMAND IS FOR, and the dental
    column above does not exercise it. There, the twin drew enough
    small values on its own and what was short was the count at four
    figures; here the two groups are `D0100`-`D0999` and
    `D5000`-`D9999`, so the ladder must interpolate across a gap four
    thousand wide and the ninety-seven cells that need a value below a
    thousand are what it comes up short of. That is R-P4-30's own
    measurement in the direction the entry recorded it -- "the twin
    drew only 78 values below 1000 where 97 are needed".

    Measured: as built, 0 of 20 seeds write a core at another width;
    with the ceiling demand withdrawn and every other rule left alone,
    20 of 20 do.
    """
    padded = ["D0%03d" % (100 + (index * 9) % 900) for index in range(97)]
    plain = ["D%04d" % (5000 + (index * 24) % 5000) for index in range(203)]
    rows = padded + plain
    return [rows[(index * 97) % 300] for index in range(300)]


def _vaccine_rows() -> "list[str]":
    """230 cells `000` to `199`: 127 padded, 103 needing no zero."""
    rows = ["%03d" % (index % 100) for index in range(127)]
    rows = rows + ["%03d" % (100 + index % 100) for index in range(103)]
    return [rows[(index * 97) % 230] for index in range(230)]


def _signed_rows() -> "list[str]":
    """R-P4-27's own column: eleven `+1`, eleven `-99`, eleven `-02`."""
    return ["+1"] * 11 + ["-99"] * 11 + ["-02"] * 11


def _uneven_signed_rows() -> "list[str]":
    """Three spellings held six, six and seven times.

    THE WITNESS FOR THE REPORTING PATH SINCE LANDING 2b.1, AND ITS THIRD
    SHAPE. The column above was that witness while its strata came out
    12, 10 and 11, until method G5.2a's stratum cap held every stratum at
    the published `mode_count`. The second shape, `+1`, `-99` and `-02`
    held eight, eight and nine times, stopped being one at landing 2b.7:
    measured at 158c811 its twin wrote `-99` nine times, `-02` eight and
    `+1` eight, and met `{1: 8, 2: 17}` on every seed while missing the
    padded count by one -- so the test that a missed width is named had
    nothing to name. Here the strata come out 7, 6 and 6 where the source
    holds 6, 6 and 7, the seventh padded cell has only a one-figure value
    to wear, and it is written `01`: fourteen two-figure cells against a
    published thirteen and five one-figure cells against six, on every
    seed.
    """
    return ["1"] * 6 + ["-99"] * 6 + ["-02"] * 7


def _described(
    folder: pathlib.Path,
    name: str,
    header: str,
    rows: "list[str]",
    floor: "int | None" = None,
) -> "tuple[dict, contract.Profile]":
    """The real reader, the real producer and the real loader.

    ``floor`` None is the shipped default (11 since plan P4-D316).
    """
    path = fixtures.write(
        folder, f"{name}.csv", header + "\n" + "\n".join(rows) + "\n"
    )
    settings = (
        taxonomy.Settings()
        if floor is None
        else taxonomy.Settings(small_cell_floor=floor)
    )
    table = reading.read_table(
        str(path),
        first_row=reading.FIRST_ROW_AUTOMATIC,
        small_cell_floor=settings.small_cell_floor,
    )
    document = profile.build_document(table, settings, [])
    loaded = contract.load_profile(
        str(fixtures.write_profile(folder, f"{name}-profile.json", document))
    )
    return document, loaded


def _field_widths_of(cells: "list[str]", prefix: str) -> "dict[int, int]":
    """Recount the census off finished text, the producer's own way."""
    counted: dict[int, int] = {}
    for cell in cells:
        body = parsing.trimmed(cell)
        if prefix:
            if not body.startswith(prefix):
                continue
            body = body[len(prefix):]
        if parsing.classify_number(body) != parsing.NUMBER:
            continue
        if parsing.numeric_style(body) not in taxonomy.POINT_FREE_STYLES:
            continue
        width = parsing.pad_width(body)
        counted[width] = counted.get(width, 0) + 1
    return counted


def _twin_cells(
    folder: pathlib.Path, name: str, loaded: contract.Profile, seed: int
) -> "tuple[list[str], pathlib.Path, generation.Twin]":
    built = generation.generate(loaded, seed)
    path = fixtures.write(
        folder, f"{name}-{seed}.csv", rendering.twin_csv(built)
    )
    lines = path.read_text(encoding="utf-8").splitlines()[1:]
    return [line for line in lines if line], path, built


# -- the producer -----------------------------------------------------


def test_the_census_covers_the_cells_the_other_two_leave_out(
    tmp_path: pathlib.Path,
) -> None:
    """A cell written `199` is in neither older census and in this one."""
    document, _loaded = _described(
        tmp_path, "vaccine", "code", _vaccine_rows()
    )
    block = document["columns"][0]
    # The padded census reaches 127 cells; the styles map calls the
    # other 103 `plain` and says nothing about how wide they are.
    assert block["pad_widths"] == {"3": 127}
    assert block["numeric_styles"] == {"plain": 103, "leading_zero": 127}
    assert block["fraction_widths"] == {}
    # ...and the new census reaches all two hundred and thirty.
    assert block["field_widths"] == {"3": 230}


def test_a_cell_written_with_a_point_is_counted_nowhere_in_it(
    tmp_path: pathlib.Path,
) -> None:
    """C6-28c's boundary, on a column that has cells of both kinds.

    Eleven cells carry a point and forty-four do not. The census counts
    the forty-four and does not reach for the eleven -- not by naming
    them and not by pooling them, `(withheld)` meaning a group too
    small to name and not a group this census has nothing to say about.
    """
    rows = ["%d" % (10 + index % 44) for index in range(44)]
    rows = rows + ["%d.5" % (10 + index % 11) for index in range(11)]
    document, _loaded = _described(tmp_path, "mixed", "reading", rows)
    block = document["columns"][0]
    assert block["numeric_styles"] == {"plain": 44, "decimal": 11}
    assert block["fraction_widths"] == {"1": 11}
    assert block["field_widths"] == {"2": 44}


def test_the_census_reads_the_cores_on_the_affixed_role(
    tmp_path: pathlib.Path,
) -> None:
    """AF7: every quantitative fact of that role answers for the cores."""
    document, _loaded = _described(
        tmp_path, "dental", "code", _dental_rows()
    )
    block = document["columns"][0]
    assert block["role"] == "affixed_number"
    # The CELLS are `D0120`, five characters. The census is over the
    # cores, so it says four.
    assert block["field_widths"] == {"4": 300}


# -- the value stage, which is what the landing actually changed ------


def test_the_dental_codes_keep_their_width_at_every_seed(
    tmp_path: pathlib.Path,
) -> None:
    """R-P4-30, and the one witness the repair itself is pinned by.

    Before method G6.6 the value stage read neither census: it drew from
    the ladder alone and handed the width walks whatever it had. On this
    column, 14 seeds in 40 then wrote a core at a width the source never
    used. Withdraw the pass and this test goes red on the first seed it
    reaches; nothing else in the suite does.
    """
    document, loaded = _described(
        tmp_path, "dental", "code", _dental_rows()
    )
    published = document["columns"][0]["field_widths"]
    assert published == {"4": 300}
    for seed in SEEDS:
        cells, _path, _built = _twin_cells(tmp_path, "dental", loaded, seed)
        assert _field_widths_of(cells, "D") == {4: 300}, (
            f"seed {seed}: the twin wrote a dental core at a width this "
            "column has nowhere, which is residual R-P4-30 back again"
        )


def test_the_padded_cells_get_values_narrow_enough_to_pad(
    tmp_path: pathlib.Path,
) -> None:
    """R-P4-30 in the direction that entry actually measured it.

    `pad_widths {4: 97}` says ninety-seven cells hold a value of at
    most THREE figures -- a leading zero is a figure of the field and
    not of the value -- and that is a constraint on magnitude the draw
    can honour with no wider disclosure at all. This column is built so
    that it BINDS: its two groups are a thousand and five thousand
    apart, so the ladder interpolating across the gap comes up short of
    small values exactly as the residual records.

    The dental column above does not pin this. Withdraw the ceiling
    demand and it stays green while this one goes red at every seed.
    """
    document, loaded = _described(tmp_path, "gap", "code", _gap_rows())
    block = document["columns"][0]
    assert block["pad_widths"] == {"4": 97}
    assert block["field_widths"] == {"4": 300}
    for seed in SEEDS:
        cells, _path, _built = _twin_cells(tmp_path, "gap", loaded, seed)
        assert _field_widths_of(cells, "D") == {4: 300}, (
            f"seed {seed}: the twin drew too few values below a "
            "thousand for the padded cells to be four figures wide, "
            "which is residual R-P4-30's own measurement"
        )


def test_the_unpadded_half_of_a_code_column_keeps_its_width(
    tmp_path: pathlib.Path,
) -> None:
    """R-P4-35, at the seeds where the ladder can carry it.

    TWO SEEDS IN FORTY CANNOT, and this file names them rather than
    quietly walking round them: over seeds 1 to 40 the twin writes a
    cell two figures wide at seed 10 and at seed 14 and at no other,
    because the ladder puts 128 cells below a hundred where the source
    holds 127 and at those two the repair would cost a value no other
    stratum holds. That is residual R-P4-114 and not this census, and
    the assertion below is over `SEEDS`, none of which is one of them.
    """
    assert 10 not in SEEDS and 14 not in SEEDS
    document, loaded = _described(
        tmp_path, "vaccine", "code", _vaccine_rows()
    )
    assert document["columns"][0]["field_widths"] == {"3": 230}
    for seed in SEEDS:
        cells, _path, _built = _twin_cells(tmp_path, "vaccine", loaded, seed)
        assert _field_widths_of(cells, "") == {3: 230}, (
            f"seed {seed}: the twin wrote a code at two figures, which "
            "the description says no cell of this column was written at"
        )


def test_residual_r_p4_114s_own_column_is_met_under_the_stratum_cap(
    tmp_path: pathlib.Path,
) -> None:
    """Eleven of each spelling, eleven cells to each stratum, every width met.

    Its strata were 12, 10 and 11 where the source holds eleven of each,
    so the eleventh padded cell had no value narrow enough and came out
    `-099` at every seed. Method G5.2a now caps every stratum at the
    published `mode_count` (landing 2b.1), which is eleven here, so the
    layout is 11, 11, 11 and the census comes back whole with nothing
    named against it.
    """
    document, loaded = _described(
        tmp_path, "signed-even", "reading", _signed_rows()
    )
    assert document["columns"][0]["field_widths"] == {"1": 11, "2": 22}
    for seed in SEEDS:
        cells, _path, built = _twin_cells(tmp_path, "signed-even", loaded, seed)
        assert _field_widths_of(cells, "") == {1: 11, 2: 22}, seed
        assert not [
            note for note in built.deviations if note.fact == "field_widths"
        ], seed


def test_a_width_the_ladder_cannot_reach_is_named_on_both_pages(
    tmp_path: pathlib.Path,
) -> None:
    """REPORT-ONLY means reported, and the witness moved at stage 3.

    RESIDUAL R-P4-114'S SHAPE NO LONGER MISSES. Its three strata were
    given 7, 6 and 6 cells where the source holds six, six and seven, so
    the seventh padded cell had no two-figure value to wear the padding
    and came out `01`, a one-figure value in a two-figure field. The tail
    rule places the rows beyond each boundary on their own grid points
    (method G5.3b), and that column now comes back whole -- `{1: 6, 2:
    13}` at every one of twenty seeds, with nothing named. It is
    asserted below in that form, because a census that stopped missing
    is a fact worth keeping.

    WHAT STILL MISSES, and what this test is for: sixty whole numbers
    from 1000 to 60000 publish the one width five, because the nine
    cells of four figures are fewer than the smallest group and the
    census counts them into the commonest (ruling 6 of 2026-09-17). The
    derived low end may not be held to that width -- no set of rows
    reaches the published mean distance from inside it (method G5.3b
    step 4) -- so the twin writes nine cells narrower than the census
    names, and the point of this test is that it is not silent about it.
    """
    # FLOOR ONE (plan P4-D316): widths held by six and thirteen cells.
    document, loaded = _described(
        tmp_path, "signed", "reading", _uneven_signed_rows(), floor=1
    )
    assert document["columns"][0]["field_widths"] == {"1": 6, "2": 13}
    for seed in SEEDS:
        cells, _path, built = _twin_cells(tmp_path, "signed", loaded, seed)
        assert _field_widths_of(cells, "") == {1: 6, 2: 13}, seed
        assert not [
            note for note in built.deviations if note.fact == "field_widths"
        ], seed

    stepped = tmp_path / "stepped"
    stepped.mkdir()
    document, loaded = _described(
        stepped, "measured", "reading",
        [f"{index * 1000}" for index in range(1, 61)],
    )
    assert document["columns"][0]["field_widths"] == {"5": 60}
    for seed in SEEDS:
        cells, path, built = _twin_cells(stepped, "measured", loaded, seed)
        assert _field_widths_of(cells, "") != {5: 60}
        # The twin's OWN report names it, with the published count
        # beside the achieved one.
        named = [
            note for note in built.deviations
            if note.fact == "field_widths" and note.column == "reading"
        ]
        assert named, f"seed {seed}: the twin missed a width and said nothing"
        assert "figure(s) wide as a whole number" in named[0].published
        # ...and the quality report LISTS the census, because the fact
        # is REPORT-ONLY: a file is not failed on it.
        outcome = validation.measure(loaded, str(path))
        listed = [
            entry for entry in outcome.listings
            if entry.fact == "numeric.field_widths"
        ]
        assert listed, "the census is published and the report is silent"
        assert not [
            check for check in outcome.checks
            if check.fact == "numeric.field_widths"
        ], "a REPORT-ONLY census may not file an executable subcheck"


def _eight_eight_nine_signed_rows() -> "list[str]":
    """`+1`, `-99` and `-02` held eight, eight and nine times (the second shape)."""
    return ["+1"] * 8 + ["-99"] * 8 + ["-02"] * 9


def test_a_padded_count_the_strata_cannot_hold_is_named_on_both_pages(
    tmp_path: pathlib.Path,
) -> None:
    """The second shape, kept beside the third at the merge of the numbers repair.

    The integration repair and the numbers repair each moved this file's
    witness when landing 2b.7 stopped it seeing a width miss: the numbers
    repair to a third shape that still misses a WIDTH (the test above),
    the integration repair to this second shape's PADDED miss. Both hold
    on the merged tree, so both are kept.

    Its three strata are given 9, 8 and 8 cells where the source holds
    eight, eight and nine, so the seventeenth two-figure cell has no
    value narrow enough to wear the padding and comes out three figures
    wide. No move of a VALUE repairs a cell COUNT, so this column misses
    -- and the point of this test is that it is not silent about it.

    WHERE THE MISS SHOWED (measured at the stage-2b integration).
    Landing 2b.7 spells each number the way the source spelled its own
    value, so the ninth padded cell was no longer forced three figures
    wide: the field-width census came back whole, `{1: 8, 2: 17}` at
    every seed, and the strata that still came out 9, 8 and 8 cost the
    PADDED count instead -- eight `-02` written against nine.

    AND IT STOPPED MISSING AT STAGE 3 (landing 3.3), which is recorded
    here rather than asserted away. The tail rule places the rows beyond
    each boundary on their own grid points, the strata come out 8, 8 and
    9 as the source holds them, and the twin writes nine `-02` at every
    one of twenty seeds with nothing named. What this test still holds
    is the SHAPE of the two censuses, which is what it was written for:
    the padded count is EXACT-OBSERVABLE and files a check, HELD here;
    the width census is REPORT-ONLY, listed and never checked. A twin
    that misses a width is the test above, whose witness moved to a
    column that still does.
    """
    # FLOOR ONE (plan P4-D316): a padded count of nine.
    document, loaded = _described(
        tmp_path, "signed", "reading", _eight_eight_nine_signed_rows(),
        floor=1,
    )
    assert document["columns"][0]["field_widths"] == {"1": 8, "2": 17}
    assert document["columns"][0]["pad_widths"] == {"2": 9}
    for seed in SEEDS:
        cells, path, built = _twin_cells(tmp_path, "signed", loaded, seed)
        assert _field_widths_of(cells, "") == {1: 8, 2: 17}
        assert sum(1 for cell in cells if cell == "-02") == 9, seed
        assert not [
            note for note in built.deviations
            if note.fact in ("pad_widths", "field_widths")
        ], seed
        # ...and the quality report LISTS the width census, because the
        # fact is REPORT-ONLY: a file is not failed on it.
        outcome = validation.measure(loaded, str(path))
        listed = [
            entry for entry in outcome.listings
            if entry.fact == "numeric.field_widths"
        ]
        assert listed, "the census is published and the report is silent"
        assert not [
            check for check in outcome.checks
            if check.fact == "numeric.field_widths"
        ], "a REPORT-ONLY census may not file an executable subcheck"
        held = [
            check for check in outcome.checks
            if check.fact == "numeric.pad_widths"
        ]
        assert held and all(
            check.verdict == "HELD" for check in held
        ), f"seed {seed}: {[check.verdict for check in held]}"


# -- the disclosure, in words -----------------------------------------


def test_the_summary_says_the_width_in_words(tmp_path: pathlib.Path) -> None:
    """R-P4-26's principle, applied to the census this landing adds.

    A width census a person cannot read about in words is a disclosure
    gap. The two older censuses were given a sentence when R-P4-26
    closed; this one is given the same sentence in the same place.
    """
    document, _loaded = _described(
        tmp_path, "vaccine", "code", _vaccine_rows()
    )
    said = summary.render(document, "")
    assert "figures written as a whole number: 3 character(s) in 230 cell(s)" in said
    assert "figures written with a leading zero: 3 character(s) in 127 cell(s)" in said
