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


def _described(
    folder: pathlib.Path, name: str, header: str, rows: "list[str]"
) -> "tuple[dict, contract.Profile]":
    """The real reader, the real producer and the real loader."""
    path = fixtures.write(
        folder, f"{name}.csv", header + "\n" + "\n".join(rows) + "\n"
    )
    table = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(table, taxonomy.Settings(), [])
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


def test_a_width_the_ladder_cannot_reach_is_named_on_both_pages(
    tmp_path: pathlib.Path,
) -> None:
    """REPORT-ONLY means reported, and residual R-P4-114's own column.

    Its three strata are given 12, 10 and 11 cells where the source
    holds eleven of each, so the eleventh padded cell has no value
    narrow enough to wear the padding and comes out `-099`. No move of
    a VALUE repairs a cell COUNT, so this column misses -- and the point
    of this test is that it is not silent about it.
    """
    document, loaded = _described(
        tmp_path, "signed", "reading", _signed_rows()
    )
    assert document["columns"][0]["field_widths"] == {"1": 11, "2": 22}
    for seed in SEEDS:
        cells, path, built = _twin_cells(tmp_path, "signed", loaded, seed)
        assert _field_widths_of(cells, "") != {1: 11, 2: 22}
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
