"""Landing 2b.6's gate: every date is written in its source's own form.

The owner ruled on 2026-09-15 that the twin should always write anything
as the original source wrote it. That reverses owner decision 5 of the
Phase 2 plan, which had every twin datetime cell written in ISO at the
recorded precision, and it retires residual R-P2-7.

Each shape here is described, built, the TWIN IS DESCRIBED AGAIN under
the same declarations, and the twin and the real table must both meet
the description with nothing missed. Three things are asserted of every
shape, and the second is the one this landing is about:

1. the member comes back -- `format` re-describes as the member that
   read the real column;
2. THE EXPORT'S OWN PARSING CALL WORKS ON EVERY TWIN CELL, and the ISO
   call fails on the twin exactly where it fails on the real table. That
   is the goal in the owner's own terms: code developed on the twin runs
   unchanged on the real table;
3. every convention the description publishes comes back -- the key set
   of each written-form census, which is what those censuses owe.

The shapes are the commonest real exports first, at a few hundred rows
and on several seeds. Every table is built by seeded neutral code at
runtime (plan D13).
"""

import csv
import datetime
import io
import pathlib
import random

import pytest

from synthtwin import contract, generation, parsing, validation
from tests import fixtures
from tests.test_stage2_round_trip import _exit_of, _round_trip

ROWS = 240


def _days(count: int, seed: int, span: int = 900) -> "list[datetime.date]":
    """Days spread over a couple of years, in no order."""
    draw = random.Random(seed)
    start = datetime.date(2022, 1, 1)
    return [
        start + datetime.timedelta(days=draw.randrange(0, span))
        for _ in range(count)
    ]


def _births(count: int, seed: int) -> "list[datetime.date]":
    """Birth dates from 1940 to 1994: two-figure years across the pivot."""
    draw = random.Random(seed)
    start = datetime.date(1940, 1, 1)
    return [
        start + datetime.timedelta(days=draw.randrange(0, 20000))
        for _ in range(count)
    ]


def _cells(shape: str, seed: int) -> "list[str]":
    """One realistic export column, written the way that export writes it."""
    draw = random.Random(seed + 1)
    if shape == "birth m/d/yy across the pivot":
        return [
            f"{day.month}/{day.day:02d}/{day.year % 100:02d}"
            for day in _births(ROWS, seed)
        ]
    days = _days(ROWS, seed)
    if shape == "month-first 03/17/2024":
        return [day.strftime("%m/%d/%Y") for day in days]
    if shape == "Excel m/d/yyyy":
        return [f"{day.month}/{day.day}/{day.year}" for day in days]
    if shape == "padded and unpadded in one column":
        return [
            day.strftime("%m/%d/%Y")
            if draw.random() < 0.5
            else f"{day.month}/{day.day}/{day.year}"
            for day in days
        ]
    if shape == "day-first 17/03/2024":
        return [day.strftime("%d/%m/%Y") for day in days]
    if shape == "dotted day-first 17.03.2024":
        return [day.strftime("%d.%m.%Y") for day in days]
    if shape == "SAS DATE11 17-MAR-2024":
        return [day.strftime("%d-%b-%Y").upper() for day in days]
    if shape == "R lower case 17-mar-2024":
        return [day.strftime("%d-%b-%Y").lower() for day in days]
    if shape == "prose Mar 17, 2024":
        return [f"{day.strftime('%b')} {day.day}, {day.year}" for day in days]
    if shape == "full names 7 September 2024":
        return [f"{day.day} {day.strftime('%B')} {day.year}" for day in days]
    if shape == "hand entry mixing two textual styles":
        return [
            day.strftime("%d-%b-%Y").upper()
            if draw.random() < 0.6
            else f"{day.day} {day.strftime('%b')} {day.year}"
            for day in days
        ]
    if shape == "compact 20240317":
        return [day.strftime("%Y%m%d") for day in days]
    if shape == "slashed ISO 2024/03/17":
        return [day.strftime("%Y/%m/%d") for day in days]
    if shape == "lower case quarter 2024-q1":
        return [f"{day.year}-q{(day.month - 1) // 3 + 1}" for day in days]
    if shape == "lower case zulu 2024-03-17T08:57:57z":
        return [
            day.strftime("%Y-%m-%dT")
            + f"{draw.randrange(24):02d}:{draw.randrange(60):02d}"
            f":{draw.randrange(60):02d}z"
            for day in days
        ]
    if shape == "Epic mm/dd/yyyy hh:mm:ss":
        return [
            day.strftime("%m/%d/%Y ")
            + f"{draw.randrange(24):02d}:{draw.randrange(60):02d}"
            f":{draw.randrange(60):02d}"
            for day in days
        ]
    if shape == "year-first slashed stamp 2024/03/17 14:05":
        return [
            day.strftime("%Y/%m/%d ")
            + f"{draw.randrange(24):02d}:{draw.randrange(60):02d}"
            for day in days
        ]
    raise AssertionError(f"no such shape: {shape}")


# Name -> (the member that must come back, the census keys that must).
SHAPES = {
    "month-first 03/17/2024": ("month-first-date", ("date_field_widths",)),
    "Excel m/d/yyyy": ("month-first-date", ("date_field_widths",)),
    "padded and unpadded in one column": (
        "month-first-date",
        ("date_field_widths",),
    ),
    "day-first 17/03/2024": ("day-first-date", ("date_field_widths",)),
    "dotted day-first 17.03.2024": ("dotted-day-first-date", ()),
    "birth m/d/yy across the pivot": (
        "two-digit-month-first-date",
        ("date_field_widths",),
    ),
    "SAS DATE11 17-MAR-2024": (
        "textual-day-first-date",
        ("month_name_styles",),
    ),
    "R lower case 17-mar-2024": (
        "textual-day-first-date",
        ("month_name_styles",),
    ),
    "prose Mar 17, 2024": (
        "textual-month-first-date",
        ("month_name_styles",),
    ),
    "full names 7 September 2024": (
        "textual-day-first-date",
        ("month_name_styles",),
    ),
    "hand entry mixing two textual styles": (
        "textual-day-first-date",
        ("month_name_styles",),
    ),
    "compact 20240317": ("compact-date", ()),
    "slashed ISO 2024/03/17": ("slashed-iso-date", ()),
    "lower case quarter 2024-q1": ("year-quarter", ("quarter_marker_case",)),
    "lower case zulu 2024-03-17T08:57:57z": ("iso-datetime", ("zulu_case",)),
    "Epic mm/dd/yyyy hh:mm:ss": (
        "month-first-datetime",
        ("date_field_widths",),
    ),
    "year-first slashed stamp 2024/03/17 14:05": (
        "slashed-iso-datetime",
        (),
    ),
}

# The members whose cells no ISO reader accepts. `compact-date` is left
# out on purpose: `20240317` is eight digits, which no ISO member reads
# either, but it IS a number, and that is the fact its own test makes.
NOT_ISO = tuple(
    name
    for name in SHAPES
    if SHAPES[name][0]
    not in ("iso-date", "iso-datetime", "iso-mixed", "iso-month")
)


def _written(folder: pathlib.Path) -> "list[str]":
    """The twin's cells, read back off the file this run wrote."""
    text = (folder / "real-twin.csv").read_text(encoding="utf-8")
    return [row[0] for row in csv.reader(io.StringIO(text))][1:]


@pytest.mark.parametrize("seed", ["4", "11"])
@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_the_twin_is_written_in_the_source_s_own_form(
    tmp_path: pathlib.Path, shape: str, seed: str
) -> None:
    """The member comes back, the export's own parse works, both exit 0."""
    member, censuses = SHAPES[shape]
    cells = _cells(shape, int(seed))
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "written", cells, (), True, seed
    )
    assert first["format"] == member, first["format"]
    # 1. THE MEMBER COMES BACK. This is the fact owner decision 5 gave
    # up and the reversal buys: describing the twin again names the
    # member that read the real column.
    assert second["format"] == member, (first["format"], second["format"])
    assert second["resolution"] == first["resolution"]
    assert second["time_precision"] == first["time_precision"]
    # 2. THE EXPORT'S OWN PARSING CALL WORKS ON EVERY TWIN CELL.
    present = [cell for cell in written if cell]
    assert len(present) >= ROWS - 1
    for cell in present:
        assert parsing.parse_datetime(cell, member) is not None, cell
    # 3. EVERY CONVENTION THE DESCRIPTION PUBLISHES COMES BACK. The key
    # set and not the count: whether a cell can show a convention
    # depends on its own value, so a twin whose interior instants fall a
    # day either side of the real ones carries a different number of
    # them (contract C6-25d to C6-25g).
    for key in censuses:
        assert first[key], (key, first[key])
        assert sorted(second[key]) == sorted(first[key]), (
            key, first[key], second[key]
        )
    assert (twin_exit, real_exit) == (0, 0)


@pytest.mark.parametrize("shape", sorted(NOT_ISO))
def test_the_iso_reader_fails_on_the_twin_exactly_as_on_the_table(
    tmp_path: pathlib.Path, shape: str
) -> None:
    """The other half of the goal, and the half a member check cannot make.

    Code written against the real table has to work on the twin, and
    code written against the twin must not work where it would not work
    on the table. Before this landing an ISO call parsed every twin cell
    of every one of these shapes and no cell of the real column, which
    is the same defect read from the other end.
    """
    member, _censuses = SHAPES[shape]
    cells = _cells(shape, 7)
    _first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "iso", cells, (), True, "7"
    )
    iso = "iso-datetime" if "datetime" in member else "iso-date"
    real_iso = 0
    for cell in cells:
        if parsing.parse_datetime(cell, iso) is not None:
            real_iso = real_iso + 1
    twin_iso = 0
    for cell in written:
        if cell and parsing.parse_datetime(cell, iso) is not None:
            twin_iso = twin_iso + 1
    assert real_iso == 0, "this shape is not an ISO one to begin with"
    assert twin_iso == 0, f"{twin_iso} twin cells still read as ISO"
    assert (twin_exit, real_exit) == (0, 0)


def test_a_compact_date_column_no_longer_fails_its_own_validation(
    tmp_path: pathlib.Path,
) -> None:
    """DT-5 of the spelling audit, the one loss that was never silent.

    A column of `20240317` cells is a column of DATES and a column of
    NUMBERS at once, and the description publishes both facts. The ISO
    twin held neither: `synthtwin validate` exited 3 on synthtwin's own
    output with `counts.n_numeric` asking 240 and holding nothing, which
    reads as a fault in the tool rather than as a spelling choice.
    """
    cells = _cells("compact 20240317", 5)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "compact", cells, (), True, "5"
    )
    assert (first["format"], second["format"]) == ("compact-date", "compact-date")
    # The fact the ISO twin contradicted: these cells are numbers too.
    assert first["n_numeric"] == second["n_numeric"]
    assert first["n_not_numeric"] == second["n_not_numeric"] == 0
    for cell in written:
        if cell:
            assert len(cell) == 8 and cell.isdigit(), cell
    assert (twin_exit, real_exit) == (0, 0)


def test_a_column_mixing_two_width_conventions_keeps_both(
    tmp_path: pathlib.Path,
) -> None:
    """The joint width census, and the reason it is joint.

    Half the rows written `%m/%d/%Y` and half `m/d/yyyy`. Not one real
    cell mixes the two -- `03/5/2024` is a style no row uses -- so the
    census is one word per CELL and not one per field. The twin must
    hold both conventions and invent neither.
    """
    cells = _cells("padded and unpadded in one column", 3)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "widths", cells, (), True, "3"
    )
    # EACH CONVENTION IS COUNTED UNDER THE FIELDS THAT SHOWED IT (plan
    # P4-D132): both fields below ten, the first alone, the second alone.
    consistent = (
        "first-field-padded",
        "first-field-unpadded",
        "padded",
        "second-field-padded",
        "second-field-unpadded",
        "unpadded",
    )
    assert {"padded", "unpadded"} <= set(first["date_field_widths"])
    assert set(first["date_field_widths"]) <= set(consistent)
    assert {"padded", "unpadded"} <= set(second["date_field_widths"])
    # NEITHER CONVENTION IS INVENTED: no real cell pads one field and
    # not the other, so no twin cell may either.
    for cell in written:
        if not cell:
            continue
        style = parsing.date_field_style(cell, "month-first-date")
        assert style is None or style in consistent, (cell, style)
    assert (twin_exit, real_exit) == (0, 0)


def test_a_hand_entered_textual_column_keeps_both_of_its_styles(
    tmp_path: pathlib.Path,
) -> None:
    """The joint month-name census, and the reason it is joint.

    A column mixing `17-MAR-2024` with `17 Mar 2024` carries its case
    and its mark TOGETHER. Two independent censuses would let the twin
    write `17 MAR 2024`, a spelling no row of the real column holds.
    """
    cells = _cells("hand entry mixing two textual styles", 8)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "textual", cells, (), True, "8"
    )
    real_styles = sorted(first["month_name_styles"])
    # The two styles, each also as the `either` word its cells of May
    # showed (plan P4-D133), and no case paired with the other's mark.
    assert [style for style in real_styles if "-either-" not in style] == [
        "title-abbreviated-space-no-comma",
        "upper-abbreviated-hyphen-no-comma",
    ]
    assert set(real_styles) <= {
        "title-abbreviated-space-no-comma",
        "title-either-space-no-comma",
        "upper-abbreviated-hyphen-no-comma",
        "upper-either-hyphen-no-comma",
    }
    assert sorted(second["month_name_styles"]) == real_styles
    for cell in written:
        if not cell:
            continue
        style = parsing.month_name_style(cell, "textual-day-first-date")
        assert style in (None,) + tuple(real_styles), (cell, style)
    assert (twin_exit, real_exit) == (0, 0)


def test_two_figure_years_stay_two_figures(tmp_path: pathlib.Path) -> None:
    """DT-2: a birth column written `m/d/yy` keeps its two-figure year.

    The ISO twin wrote `1977-05-19` and `2050-...` for a column whose
    cells are `5/19/77`, so age code written on the twin met four-figure
    years the export never held and the tool's own pivot guess read as
    literal ones.
    """
    cells = _cells("birth m/d/yy across the pivot", 2)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "births", cells, (), True, "2"
    )
    assert first["format"] == second["format"] == "two-digit-month-first-date"
    for cell in written:
        if not cell:
            continue
        assert len(cell) <= 8, cell
        assert parsing.parse_datetime(
            cell, "two-digit-month-first-date"
        ) is not None, cell
    assert (twin_exit, real_exit) == (0, 0)


def test_a_lower_case_marker_is_not_written_as_a_capital(
    tmp_path: pathlib.Path,
) -> None:
    """DT-6 and DT-7: `2024-q1` stays `q`, and a zulu `z` stays `z`."""
    for shape, mark in (
        ("lower case quarter 2024-q1", "q"),
        ("lower case zulu 2024-03-17T08:57:57z", "z"),
    ):
        cells = _cells(shape, 6)
        folder = tmp_path / mark
        first, second, written, twin_exit, real_exit = _round_trip(
            folder, cells, (), True, "6"
        )
        key = "quarter_marker_case" if mark == "q" else "zulu_case"
        assert first[key] == {"lower": len(cells)}, first[key]
        assert second[key] == first[key]
        for cell in written:
            if cell:
                assert mark in cell, cell
                assert mark.upper() not in cell, cell
        assert (twin_exit, real_exit) == (0, 0)


def test_the_validator_notices_a_twin_that_goes_back_to_iso(
    tmp_path: pathlib.Path,
) -> None:
    """THE MUTATION PIN for the writer, run as a check rather than stated.

    A file written in ISO where the description names another member is
    what every twin of these shapes used to be. The quality report must
    call it MISSED -- on `format.member` -- or nothing in this suite
    shows the member check can fail at all.
    """
    folder = tmp_path / "reverted"
    folder.mkdir(parents=True, exist_ok=True)
    days = _days(ROWS, 12)
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(
            ["value"], [[day.strftime("%m/%d/%Y")] for day in days]
        ),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace"]
    ) == 0
    described = contract.load_profile(str(folder / "real-profile.json"))
    # The twin as the withdrawn rule wrote it: the same days, in ISO.
    iso = folder / "iso-twin.csv"
    iso.write_text(
        fixtures.rows_to_csv(
            ["value"], [[day.isoformat()] for day in sorted(days)]
        ),
        encoding="utf-8",
        newline="",
    )
    outcome = validation.measure(described, str(iso))
    missed = [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    ]
    assert "format.member" in missed, missed


def test_the_writer_is_the_only_place_a_date_cell_is_spelled() -> None:
    """One writer, so a producer and a generator cannot disagree.

    `parsing.written_date` is the inverse of `parsing.parse_datetime`
    under every member that names a day, and the generator reaches it
    through `_cell_of_ordinal` and nowhere else. Asserted over every
    member and every width and name style, so a member added later
    without a writing rule fails here rather than in somebody's table.
    """
    checked = 0
    for member in parsing.DATE_FORMATS:
        if member in ("iso-month", "year-quarter", "iso-mixed"):
            continue
        widths = parsing.FIELD_WIDTH_STYLES
        if member not in parsing.VARIABLE_WIDTH_MEMBERS:
            widths = parsing.FIELD_WIDTH_STYLES_ONE_FIELD
        names = (parsing.DEFAULT_NAME_STYLE,)
        if member in parsing.TEXTUAL_MEMBERS:
            names = parsing.MONTH_NAME_STYLES
            if member == "textual-day-first-date":
                names = parsing.MONTH_NAME_STYLES_NO_COMMA
        for width in widths:
            for style in names:
                for year, month, day in (
                    (2024, 3, 17), (2024, 3, 5), (2024, 11, 25), (1999, 5, 9)
                ):
                    half = parsing.written_date(
                        year, month, day, member, width, style
                    )
                    cell = half
                    if member in parsing.SLASHED_STAMPS:
                        cell = f"{half} 14:05"
                    if member == "iso-datetime":
                        cell = f"{half}T14:05:00"
                    found = parsing.parse_datetime(cell, member)
                    assert found is not None, (member, width, style, cell)
                    assert found[0][0:10] == f"{year:04d}-{month:02d}-{day:02d}", (
                        member, cell, found
                    )
                    checked = checked + 1
    # SIX HUNDRED AND NINETY-SIX, counted rather than guessed at, so a
    # member added later without a writing rule moves this number and is
    # noticed here rather than in somebody's table: six variable-width
    # members at eight widths (192), the day-first textual member at two
    # widths and eighteen styles (144), the month-first textual member at
    # two widths and thirty-six styles (288), and the nine fixed-width
    # members at two widths (72), each over four calendar dates. It was
    # 456 until the one-field width words and the `either` length of a
    # name of May joined the vocabularies (plans P4-D132 and P4-D133).
    assert checked == 696, checked


def test_the_generator_writes_through_the_member_and_not_around_it() -> None:
    """The oracle half: `_instant_written` reads under the PUBLISHED member.

    If it read under an ISO member, as it did until this landing, every
    end, every rung and every recount in the generator would go silently
    missing on a month-first column -- the twin's cells would read as no
    date at all.
    """
    style = generation._DateStyle("month-first-date")
    cell = generation._cell_of_ordinal(19800, "date", "date", 0, "T", style)
    assert cell.count("/") == 2, cell
    assert parsing.parse_datetime(cell, "iso-date") is None, cell
    assert parsing.parse_datetime(cell, "month-first-date") is not None, cell
