"""P4-D457 (lane ID-ROOM2): a made-up date in a held date column kept off the real dates.

WHAT WAS MEASURED ON THE BASE (batch 4n's sealed head 2af926ce; K-HZ-06's driver, kept per column since
batch 4n). The birth-date columns lane SH2 holds as identifiers wrote made-up dates equal to a real date of
their column as often as chance gives: at 20,000 rows 733 cells of an ISO column equal and 761 merging,
758 / 786 month first, 747 / 747 with a month word, 756 / 782 of a second ISO column, 7,055 / 7,656 of a
column of two-figure years; the diagnosis dates held as record numbers 3,138 / 3,222. The G1 floor drew
them from 2000 on, the date pass from 1940 on, never reading a real value; a chance-equal made-up date is an
attribute, but a HELD date is held as an identifier, so the identifier rule binds it.

THE RULE (method G9.6c, contract 7.12c): ONE BLOCK OF YEARS A KIND OF YEAR. The producer reads every present
cell of a column of dates held as record numbers on its merged key, in every order a date of the column's
date layouts stands in, and holds every year a reading names; where the layouts write both a four-figure
and a two-figure year, each four-figure year held is held for the two-figure kind as its last two figures
and each two-figure year for the four-figure kind as 1900 and 2000 plus it. It publishes `made_up_years`:
for each kind one block, fixed by published facts alone -- four-figure years from 2028 (the year after the
release's reference year), two-figure years from `28` round past `99` -- as many years as hold twice the
layout's made-up values at its writer's own count a year, taken only where no year of it is held. Nothing
is stepped over and nothing is counted: a block one held year falls in is no room, and that kind's
made-up values are the walk's, off the real by the exclusion or the spill. The twin draws its made-up dates
from the block alone and checks each against it before it stands; a held column whose grain reads stamps,
clock times or counted dates publishes `[]` and is written as before. Since repair 2 every cell is also read in
its own layout's orders and a cell of a kind no named layout writes brings the cross rule; with no grain a named
stamp publishes `[]`, cells of figures alone are read as years alone, and each named layout takes its own share
of the block's first years, read in its own orders at the days the date pass writes.

The gate: this file holds the rule's parts, each case fast; the zoo's held date columns run through the
zoo (each at 600 rows, a test size the command refuses: 0 equal and 0 merging) are
tests/test_held_dates_off_the_real_zoo.py's, and one column a writer at 20,000 rows
tests/test_held_dates_off_the_real_writers.py's, both split from this file at repair 1 by the CPU-seconds
rule (LANE ID-ROOM2 RULINGS 3 (8)); repair 1's shapes at 20,000 rows are
tests/test_held_dates_off_the_real_shapes.py's, repair 2's are tests/test_held_dates_off_the_real_widths.py's
and tests/test_held_dates_off_the_real_typed.py's; the six columns at 20,000 rows are K-HZ-06's
(tools/measurements/kpi_identifier_room.py, kpi_run --slow). Each case is red on the mutant its docstring
names (wave6/ID-ROOM2/mutants.log, wave6/ID-ROOM2/r1/mutants.log, wave6/ID-ROOM2/r2/mutants.log).
"""

from __future__ import annotations

import dataclasses
import datetime
import json
import pathlib
import types

import pytest

from synthtwin import contract, errors, generation, grains, parsing, taxonomy

FLOOR = 11


# -- (1) the producer's reading: orders, years, rooms -------------------------------------------


def test_the_first_year_is_the_one_after_the_reference_year() -> None:
    """The contract's first year and the producer's are the year after the release's reference year.

    Mutant: contract.MADE_UP_FIRST_YEAR = 2027.
    """
    assert taxonomy.MADE_UP_FIRST_YEAR == taxonomy.SAFE_HARBOR_REFERENCE_YEAR + 1 == 2028
    assert contract.MADE_UP_FIRST_YEAR == taxonomy.MADE_UP_FIRST_YEAR
    assert contract.MADE_UP_LAST_YEAR == taxonomy.MADE_UP_LAST_YEAR == 9999


@pytest.mark.parametrize(
    ("form", "orders"),
    [
        ("%%%%-%%-%%", ("YMD",)),
        ("%%/%%/%%%%", ("MDY", "DMY")),
        ("%.%.%%%%", ("MDY", "DMY")),
        ("%%-@&&-%%%%", ("DWY",)),
        ("%%-@@@-%%", ("DWy",)),
        ("%%/%%/%%", ("MDy", "DMy")),
        ("%%%%", ("Y",)),
        ("%%/%%%%", ("MY",)),
        ("%%%%-%%", ("YM",)),
        ("%%%%%%%%", ("C",)),
        ("@%%%%%%", ()),
    ],
)
def test_a_date_form_names_the_orders_its_merged_key_reads(form: str, orders: "tuple[str, ...]") -> None:
    """Each date form's orders on the merged key; a year written last stands both month and day first."""
    assert taxonomy.date_merged_orders(form, True) == orders


@pytest.mark.parametrize(
    ("cell", "order", "years"),
    [
        ("1956-03-05", "YMD", (1956,)),
        ("1956-12-05", "YMD", (1956,)),
        ("03/05/1956", "MDY", (1956,)),
        ("3/5/1956", "DMY", (1956,)),
        ("20-Dec-1936", "DWY", (1936,)),
        ("13/03/77", "DMy", (77,)),
        ("15/01/00", "DMy", (0, 10)),
        ("19560305", "C", (1956,)),
        ("2016", "Y", (2016,)),
        ("05/2011", "MY", (2011,)),
        ("2028-02-30", "YMD", ()),
        ("1956-13-05", "YMD", ()),
        ("record 7", "YMD", ()),
    ],
)
def test_a_merged_key_names_the_years_of_its_dates(cell: str, order: str, years: "tuple[int, ...]") -> None:
    """The years every valid date of an order whose merged key is the cell's names; none where no date is written so.

    `15/01/00` merges to `1510`: day 1, month 5, year 10, or day 15, month 1, year 0, both counted.
    """
    assert taxonomy.years_of_merged_date(parsing.merged_key(cell), order) == years


def test_the_four_figure_room_is_one_block_no_real_date_takes() -> None:
    """From 2028, as many years as the facts ask, one at least, and none where a real date takes any of them.

    Nothing is stepped over and nothing counted: a year held past the block does not matter, one held
    inside it leaves no room. Mutant: the `if year in held: return None` line dropped.
    """
    assert taxonomy.made_up_year_room({}, 3) == [2028, 2029, 2030]
    assert taxonomy.made_up_year_room({}, 0) == [2028]
    assert taxonomy.made_up_year_room({2029: True}, 3) is None
    assert taxonomy.made_up_year_room({2031: True}, 3) == [2028, 2029, 2030]
    # ...years at or before the reference year are no part of the block at all.
    assert taxonomy.made_up_year_room({1956: True, 2027: True}, 2) == [2028, 2029]
    # ...and the calendar's last year ends the block short.
    assert len(taxonomy.made_up_year_room({}, 10**6) or []) == 9999 - 2028 + 1


def test_the_two_figure_room_is_one_block_from_28() -> None:
    """From `28`, round past `99`, as many as the facts ask; none where a real date takes any, or past a hundred.

    So no two-figure year at or before the Safe Harbor cut is ever named apart from the others, and a column
    of two-figure birth dates whose real years leave every block of the size its values need held writes
    the walk's values (at 20,000 rows, 13,838 values ask 76 years). Mutant: the `if figures in held:
    return None` line dropped.
    """
    assert taxonomy.short_year_room({}, 3) == [28, 29, 30]
    assert taxonomy.short_year_room({30: True}, 3) is None
    assert taxonomy.short_year_room({27: True}, 72) == list(range(28, 100))
    assert taxonomy.short_year_room({}, 74) == list(range(28, 100)) + [0, 1]
    births = {year: True for year in range(30, 100)}
    assert taxonomy.short_year_room(births, 2) == [28, 29]
    assert taxonomy.short_year_room(births, 76) is None


def test_more_than_a_hundred_two_figure_years_is_no_room() -> None:
    """A column whose values need more than a century of two-figure years has none. Mutant: the line dropped."""
    assert taxonomy.short_year_room({}, 100) == list(range(28, 100)) + list(range(0, 28))
    assert taxonomy.short_year_room({}, 101) is None


# -- (2) the contract -------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [[], [[2028, 2031]], [[0, 29]], [[0, 29], [2028, 2103]], [[2028, 2028], [2030, 9999]]],
)
def test_the_contract_reads_made_up_years(value: object) -> None:
    """Runs of two-figure years or four-figure years from 2028, in order and apart."""
    runs = contract._made_up_years(value, "column 1")
    assert [list(run) for run in runs] == value


@pytest.mark.parametrize(
    "value",
    [
        {"2028": 2031},
        [[2027, 2031]],
        [[1940, 2019]],
        [[2031, 2028]],
        [[2028, 2031], [2030, 2040]],
        [[0, 100]],
        [[True, 5]],
        [[2028]],
        [[2028, 10000]],
    ],
)
def test_the_contract_refuses_anything_else(value: object) -> None:
    """A year at or before the reference year, a run out of order or overlapping, anything not runs of whole years."""
    with pytest.raises(errors.ProfileError):
        contract._made_up_years(value, "column 1")


# -- (3) the twin's writers -------------------------------------------------------------------


def test_the_date_pass_writes_only_the_room_years() -> None:
    """`_room_filled_form` over a room of four and two-figure years writes only those years, each date valid."""
    room_years = ([2028, 2029, 2030], [0, 1, 2])
    for form in ("%%%%-%%-%%", "%%/%%/%%%%", "%%-@&&-%%%%", "%%/%%%%", "%%%%", "%%%%%%%%", "%%/%%/%%"):
        count = generation._room_form_dates(form, room_years)
        assert count > 0
        published = generation._room_published(room_years)
        named = {form: True}
        for step in range(0, count, max(count // 97, 1)):
            date = generation._room_filled_form(form, step, room_years)
            assert date is not None
            assert generation._off_the_real_years(date, named, parsing.LAYOUT_PLAIN, published), (form, step, date)
    assert generation._room_form_dates("%%/%%/%%", ([2028], [])) == 0


def test_a_date_of_another_year_does_not_stand() -> None:
    """The check refuses a date naming a year the room does not publish, or in a layout the column does not name."""
    published = generation._room_published(([2028, 2029], [5]))
    named = {"%%%%-%%-%%": True, "%%/%%/%%": True}
    assert generation._off_the_real_years("2028-03-04", named, parsing.LAYOUT_PLAIN, published)
    assert not generation._off_the_real_years("2027-03-04", named, parsing.LAYOUT_PLAIN, published)
    assert not generation._off_the_real_years("03/04/2028", named, parsing.LAYOUT_PLAIN, published)
    assert generation._off_the_real_years("13/04/05", named, parsing.LAYOUT_PLAIN, published)
    assert not generation._off_the_real_years("13/04/06", named, parsing.LAYOUT_PLAIN, published)


def test_the_g1_floor_spans_are_the_room_years() -> None:
    """A held column's spans are its room's runs: four-figure years, or two-figure years read from 2000."""
    iso = grains.Reading(grains.DATE, "iso-date")
    spans = generation._room_spans(([2028, 2029, 2031], []), iso)
    days = [(first // grains.date_counts.DAY, end // grains.date_counts.DAY) for first, end in spans]
    assert days == [
        (parsing.days_from_civil(2028, 1, 1), parsing.days_from_civil(2030, 1, 1)),
        (parsing.days_from_civil(2031, 1, 1), parsing.days_from_civil(2032, 1, 1)),
    ]
    short = grains.Reading(grains.DATE, "layout {DD}/{MM}/{YY1900}")
    spans = generation._room_spans(([2028], [3, 4]), short)
    assert [(first // grains.date_counts.DAY, end // grains.date_counts.DAY) for first, end in spans] == [
        (parsing.days_from_civil(2003, 1, 1), parsing.days_from_civil(2005, 1, 1))
    ]
    assert generation._room_spans(([2028], []), short) == []


def _the_oracle() -> "types.ModuleType":
    """The reference oracle, loaded from its committed file."""
    import importlib.util

    path = pathlib.Path(__file__).resolve().parents[1] / "tools" / "reference" / "make_generation_reference_vectors.py"
    spec = importlib.util.spec_from_file_location("oracle_id_room2", path)
    assert spec is not None and spec.loader is not None
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
    return oracle


def test_the_oracle_writes_the_room_as_the_date_pass_does() -> None:
    """The oracle's mirror (`room_count`, `room_date`, `years_merged`, `stands_off_the_real`) agrees with the product.

    Over every date form the pass writes, a room of four-figure years longer than one run of eighty
    and of two-figure years, step by step. Mutant: the oracle's runs of eighty read as runs of ten.
    """
    oracle = _the_oracle()
    room_years = ([year for year in range(2028, 2200)], [0, 1, 2, 3, 99])
    for form in ("%%%%-%%-%%", "%%/%%/%%%%", "%%-@&&-%%%%", "%%/%%%%", "%%%%-%%", "%%%%", "%%%%%%%%", "%%/%%/%%", "%-%-%%%%"):
        count = generation._room_form_dates(form, room_years)
        assert oracle.room_count(form, room_years) == count, form
        for step in range(0, count, max(count // 211, 1)):
            date = generation._room_filled_form(form, step, room_years)
            assert oracle.room_date(form, step, room_years) == date, (form, step)
            assert date is not None
            key = parsing.merged_key(date)
            for order in taxonomy.date_merged_orders(form, True):
                assert set(taxonomy.years_of_merged_date(key, order)) == oracle.years_merged(key, order)
            published = generation._room_published(room_years)
            assert oracle.stands_off_the_real(date, {form}, parsing.LAYOUT_PLAIN, room_years) == (
                generation._off_the_real_years(date, {form: True}, parsing.LAYOUT_PLAIN, published)
            )


# -- (5) repair 1: the writers' own counts, both widths of year, the readings served, the loader, G4 ------


def _held(forms: "dict[str, int]", distinct: int, grain: "dict[str, object] | None" = None) -> taxonomy.ColumnProfile:
    """A record-number block of dates naming ``forms``, ``distinct`` different values, a grain where given."""
    details: "dict[str, object]" = {"layout_forms": dict(forms), "n_code_alphabet": 0, "n_all_digits": 0}
    if grain is not None:
        details["time_grain"] = grain
    return taxonomy.ColumnProfile(
        name="dob", position=1, role=taxonomy.ROLE_IDENTIFIER, statistical_type="code",
        quality_state="ok", structural_role="identifier",
        detection_evidence=taxonomy.note(taxonomy.EVIDENCE_HELD_IN_PEOPLE),
        n_present=sum(forms.values()), n_missing=0, missing_by_source={},
        missing_by_class={}, n_missing_blank=0, n_missing_withheld=0,
        details=details, publication_notes=[], remarks=[], n_distinct=distinct,
    )


def _runs(column: taxonomy.ColumnProfile) -> "list[list[int]]":
    years = column.details["made_up_years"]
    assert isinstance(years, list)
    return years


@pytest.mark.parametrize(
    ("form", "grained", "a_year"),
    [
        ("%%/%%/%%%%", False, 144),
        ("%%/%%/%%%%", True, 365),
        # ...the G1 floor's year written last beside a field of one figure: the fewer of the two orders, month
        # first (9 months of up to 31 days, 273) or day first (12 months of days 1 to 9, 108): the verify of
        # repair 1, item 4 (X4: the more of the two survived every case).
        ("%/%%/%%%%", True, 108),
        ("%%/%/%%%%", True, 108),
        ("%/%/%%%%", False, 81),
        ("%%/%%/%%", False, 336),
        ("%%-@&&-%%%%", False, 336),
        ("%%-@&&-%%%%", True, 365),
        ("%%%%-%%-%%", False, 365),
        ("%%%%%%%%", True, 365),
        ("%%%%/%/%%", False, 273),
        ("%%/%%%%", False, 12),
        ("%%%%", True, 1),
        ("@%%%%%%", False, 0),
    ],
)
def test_each_writer_counts_its_own_dates_a_year(form: str, grained: bool, a_year: int) -> None:
    """Codex's review of lane ID-ROOM2, item 2: the block is sized by what each writer writes in a year.

    The date pass writes a year last in four figures with its other fields 1 to 12 (144 a year), not 366.
    Mutant: one count of 366 for every form of three fields (the build's `detail`).
    """
    assert taxonomy.made_up_dates_a_year(form, grained) == a_year


def test_codex_s_thousand_dates_ask_a_block_that_holds_them() -> None:
    """Codex's item 2: 1,000 different month-first dates from 1920, twenty rows each, asked [2028, 2033] (6 years,
    864 dates) of the date pass; at 144 a year twice them ask 14. Red on 18b17a9c's `detail`.
    """
    base = datetime.date(1920, 1, 1).toordinal()
    dates = [datetime.date.fromordinal(base + 9 * k).strftime("%m/%d/%Y") for k in range(1000)]
    held = taxonomy.with_made_up_years(_held({"%%/%%/%%%%": 20_000}, 1000), dates * 20)
    assert _runs(held) == [[2028, 2041]]
    # ...the skeptic's ten years of dates: 3,642 different ones ask 51 years, not 20.
    assert taxonomy._years_asked(3642, 144, 7972) == 51


def test_a_kind_whose_values_fit_no_block_has_no_room() -> None:
    """The year cap: two-figure years of one figure each side (81 a year) hold 8,100 dates in a century; 9,000
    different values fit none, so the kind is written as record numbers (NF137). Mutant: no cap.
    """
    assert taxonomy._years_asked(9000, 81, 100) == 0
    assert taxonomy._years_asked(5000, 81, 100) == 100
    held = taxonomy.with_made_up_years(_held({"%/%/%%": 9000}, 9000), ["1/2/03"] * 9000)
    assert _runs(held) == []
    assert [remark.form for remark in held.remarks] == [taxonomy.REMARK_MADE_UP_DATES_NOT_DATES]


def _both_widths(two_figure_45: bool) -> "tuple[list[str], dict[str, int]]":
    """Birth dates `dd-Mon-yyyy` of 1930 to 1999 and `dd-Mon-yy` of 2000 to 2025 (skeptic 1's variant B), and their census."""
    import random

    draw = random.Random(7)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    cells: "list[str]" = []
    for place in range(6000):
        if place % 10 < 7:
            day = datetime.date.fromordinal(draw.randint(datetime.date(1930, 1, 1).toordinal(),
                                                         datetime.date(1999, 12, 31).toordinal()))
            cells += [f"{day.day:02d}-{months[day.month - 1]}-{day.year}"]
        else:
            day = datetime.date.fromordinal(draw.randint(datetime.date(2000, 1, 1).toordinal(),
                                                         datetime.date(2025, 12, 31).toordinal()))
            cells += [f"{day.day:02d}-{months[day.month - 1]}-{day.year % 100:02d}"]
    if two_figure_45:
        cells[3] = "13-Mar-45"
    four = sum(1 for cell in cells if len(cell) == 11)
    return cells, {"%%-@&&-%%%%": four, "%%-@&&-%%": len(cells) - four}


def test_the_same_day_written_with_the_other_year_width_is_held() -> None:
    """Skeptic 1 of lane ID-ROOM2, item 1 (the BLOCKER): `06-Mar-1932` real and `06-Mar-32` made up.

    The four-figure years 1930 to 1999 hold `30` to `99` for the two-figure kind, so its block from `28`
    is no room and its cells are written as record numbers; the four-figure block from 2028 stands (no
    two-figure year 00 to 25 names 2028 on). And the reverse: a real `13-Mar-45` holds 2045, so a
    four-figure block reaching it is no room. Mutant: the two cross readings dropped (red: a two-figure
    run from 28, and a four-figure run through 2045).
    """
    cells, forms = _both_widths(False)
    held = taxonomy.with_made_up_years(_held(forms, len(set(cells))), cells)
    runs = _runs(held)
    assert all(first > 99 for first, _last in runs) and runs and runs[0][0] == 2028, runs
    forms_said = [remark.form for remark in held.remarks]
    assert taxonomy.REMARK_MADE_UP_DATES_NOT_DATES in forms_said
    assert taxonomy.REMARK_MADE_UP_DATES_OFF_THE_REAL in forms_said
    reverse, forms = _both_widths(True)
    held = taxonomy.with_made_up_years(_held(forms, len(set(reverse))), reverse)
    assert runs[0][1] >= 2045
    assert _runs(held) == [], _runs(held)


def _other_width_withheld(old: bool, first: int, last: int, layouts: int = 3) -> "tuple[list[str], dict[str, int]]":
    """The verify of repair 1's shapes F2 (``old``) and G2: 5,988 births of one width named, and four each of the
    other width, births of ``first`` to ``last``, in ``layouts`` layouts the census withholds, the spaced one
    (`dd Mon yyyy`) first."""
    import random

    draw = random.Random(11)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    def day(low: int, high: int, top: int) -> datetime.date:
        while True:
            found = datetime.date.fromordinal(draw.randint(datetime.date(low, 1, 1).toordinal(),
                                                           datetime.date(high, 12, 31).toordinal()))
            if found.day <= top:
                return found

    few: "list[str]" = []
    for _place in range(4):
        for shape in range(layouts):
            when = day(first, last, 9 if shape == 2 else 28)
            year = f"{when.year}" if old else f"{when.year % 100:02d}"
            if shape == 0:
                few += [f"{when.day:02d} {months[when.month - 1]} {year}"]
            elif shape == 1:
                few += [f"{when.day:02d}-{months[when.month - 1]}-{year}"]
            else:
                few += [f"{when.day}-{months[when.month - 1]}-{year}"]
    main: "list[str]" = []
    for _place in range(5988):
        when = day(1930, 1999, 31) if not old else day(2000, 2025, 31)
        main += [f"{when.day:02d}-{months[when.month - 1]}-{when.year % 100:02d}" if old
                 else f"{when.day:02d}-{months[when.month - 1]}-{when.year}"]
    named = "%%-@&&-%%" if old else "%%-@&&-%%%%"
    return main + few, {named: len(main), "(withheld)": len(few)}


def test_a_withheld_layout_of_the_other_width_is_read_in_its_own_orders() -> None:
    """The verify of repair 1, item 1 (the BLOCKER; LANE ID-ROOM2 RULINGS 6 (1)): a held column whose census
    withholds a pool of the OTHER year width -- two-figure births of 2000 to 2025 beside twelve four-figure ones of
    1928 to 1937 in three withheld layouts (F2), or the reverse (G2) -- read the pool in no order of its own, and
    20 and 7 twin cells named a real birth at 20,000 rows (9 and 6 with nobody at the keyboard). Each cell is now
    read in its own layout's orders too, and a cell reading in a kind no named layout writes brings the cross
    rule: F2 holds `28` to `37` and G2 2045 to 2060, so neither block is room (the price: the column's 5,988
    named values are written as record numbers, NF137). A pool of 1980 to 1985 beside two-figure births of 2000
    to 2025 holds `80` to `85`, past the block, which stays. The spaced layout alone (`01 Feb 1930`) is read as
    `01-Feb-1930`. Mutants: M14, the own layout's orders not read; M15, the cross rule only where both kinds
    are named; M16, the spaced layout not read with hyphens.
    """
    cells, forms = _other_width_withheld(True, 1928, 1937)
    held = taxonomy.with_made_up_years(_held(forms, len(set(cells))), cells)
    assert _runs(held) == []
    assert [remark.form for remark in held.remarks] == [taxonomy.REMARK_MADE_UP_DATES_NOT_DATES]
    cells, forms = _other_width_withheld(False, 1945, 1960)
    held = taxonomy.with_made_up_years(_held(forms, len(set(cells))), cells)
    assert _runs(held) == []
    cells, forms = _other_width_withheld(True, 1928, 1937, 1)
    assert all(" " in cell for cell in cells[5988:])
    held = taxonomy.with_made_up_years(_held(forms, len(set(cells))), cells)
    assert _runs(held) == []
    cells, forms = _other_width_withheld(True, 1980, 1985)
    held = taxonomy.with_made_up_years(_held(forms, len(set(cells))), cells)
    runs = _runs(held)
    assert runs and runs[0][0] == 28 and runs[-1][1] < 80, runs


@pytest.mark.parametrize("kind", ["stamp", "clock", "counted"])
def test_a_grain_reading_no_dates_publishes_no_room_and_keeps_its_remark(kind: str) -> None:
    """Codex's item 1: a held column read as stamps (ISO dates beside hourly stamps) gained a block its G1 floor
    could not draw from, and 0 of 20,000 twin cells parsed. Such a reading publishes `[]` and keeps the G1
    floor's remark; its twin is written as before (tests/test_held_dates_off_the_real_shapes.py). Mutant: the
    reading not looked at (red: a run, and NF136 in place of the G1 floor's remark).
    """
    grain = {"rung": "held", "finest": "second", "kind": kind, "reading": "iso-mixed", "mark": ".",
             "rows": 600, "people": 0, "spans": []}
    column = dataclasses.replace(
        _held({"%%%%-%%-%%": 12, "%%%%-%%-%%@%%:%%:%%": 588}, 600, grain),
        remarks=[taxonomy.note(taxonomy.REMARK_HELD_DATES_ARE_VALID)],
    )
    cells = [f"19{10 + k % 80}-01-02" for k in range(600)]
    held = taxonomy.with_made_up_years(column, cells)
    assert held.details["made_up_years"] == []
    assert [remark.form for remark in held.remarks] == [taxonomy.REMARK_HELD_DATES_ARE_VALID]
    assert taxonomy.MADE_UP_GRAIN_KIND == grains.DATE


def _held_iso_block(tmp_path: pathlib.Path, years: "tuple[tuple[int, int], ...]") -> contract.ColumnBlock:
    """A held ISO birth-date column's block (the G1 floor's), profiled with nobody at the keyboard from 600 rows (a
    test size the command refuses), its room set to ``years``."""
    import contextlib
    import io

    from synthtwin import cli

    import unanswered_identifier_shapes as held_shapes

    table = tmp_path / "t.csv"
    # ...births from 1925 on: a birth-date column with a date at or before the Safe Harbor cut is held whole.
    first = datetime.date(1925, 1, 1).toordinal()
    with open(table, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("person_key,dob,value\n")
        for row in range(600):
            handle.write(f"Q{700000 + row},{datetime.date.fromordinal(first + 37 * row).isoformat()},{row % 7}\n")
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()):
        assert cli.main(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace"],
                        small_tables_refused=False) == 0
    column = [one for one in contract.load_profile(f"{tmp_path / 't-profile.json'}").columns if one.name == "dob"][0]
    assert column.time_grain is not None and column.time_grain.reading.kind == grains.DATE
    assert isinstance(column.facts, contract.IdentifierFacts)
    return dataclasses.replace(column, facts=dataclasses.replace(column.facts, made_up_years=years))


def test_a_withheld_value_is_written_only_at_its_own_length(tmp_path: pathlib.Path) -> None:
    """The verify of repair 1, item 2 (LANE ID-ROOM2 RULINGS 6 (2)): the G1 floor wrote a value of a layout the census
    withholds at the room's width -- an eleven-character stand-in as a ten-character date, the other year width's
    pool as nine characters where eleven stood -- and validation exited 3 (`max_length`, `min_length`,
    `n_code_alphabet`). A withheld value is now written only in the member's own form at its own length and on its
    side of the code alphabet; otherwise the walk's value stands, as before repair 1, while one that has a date of
    its length is still written as one (Codex's item 3). Mutant M17: the withheld path's `grains.filled` restored.
    """
    column = _held_iso_block(tmp_path, ((2028, 2031),))
    cells = ["1234-56-78", "ABCDEFGHIJK", "AB-CD-EF-G", "1234-56-79"]
    found, _unwritten = generation._inside_the_grain(column, cells, [7, 11, 13, 17])
    assert found[1] == "ABCDEFGHIJK", found
    assert found[2] != "AB-CD-EF-G" and len(found[2]) == 10 and found[2][0:3] == "202", found
    for place in (0, 2, 3):
        assert datetime.date.fromisoformat(found[place]).year in (2028, 2029, 2030, 2031), found


def test_a_withheld_value_no_named_order_reads_keeps_the_walk_s_value(tmp_path: pathlib.Path) -> None:
    """The verify of repair 1, item 4 (X3; LANE ID-ROOM2 RULINGS 6 (4)): the withheld path's check survived every
    case. Under item 2's rule the path writes the member's own form at the value's length, so a value of the other
    year width is never written there; what the check still guards is a value of that form no named date order
    reads -- an ISO member's stamp at a sixteen-character stand-in's length, `2029-03-05 13:45`, whose merged key
    no `%%%%-%%-%%` reading names as a date of a published year -- which keeps the walk's value. Mutant X3: the
    check (`_off_the_real_years(..., True)`) dropped from the withheld path.
    """
    column = _held_iso_block(tmp_path, ((2028, 2031),))
    cells = ["1234-56-78", "AB-CD-EF GH:IJKL", "1234-56-79"]
    found, _unwritten = generation._inside_the_grain(column, cells, [7, 11, 17])
    assert found[1] == "AB-CD-EF GH:IJKL", found
    named = generation._named_date_layouts(column.facts)  # type: ignore[arg-type]
    published = generation._room_published(([2028, 2029, 2030, 2031], []))
    for cell in found:
        if cell not in cells:
            assert generation._off_the_real_years(cell, named, parsing.LAYOUT_PLAIN, published, True), cell


def test_a_withheld_value_whose_length_dates_only_the_other_side_keeps_the_walk_s_value(
    tmp_path: pathlib.Path,
) -> None:
    """The scoped verify of repair 2, item 2 (X6; LANE ID-ROOM2 RULINGS 7 (2)): `n_code_alphabet` rests on the
    withheld path writing a value on its own side of the code alphabet, and no case pinned that half. An ISO
    member writes a ten-character date only inside the code alphabet (`2000-01-01`) and a sixteen-character one
    only outside it (`2000-01-01 00:00`), so a ten-character stand-in outside it (`AB/CD/EF/G`) and a
    sixteen-character one inside it (`AB-CD-EF-GH-IJKL`) have no date of their own length on their own side:
    `grains.filled_at_its_length` gives None for each, and the G1 floor keeps the walk's value; the same lengths
    on their own sides are written as dates. Mutant X6: the side ignored, each written as a date of the other side.
    """
    reading = grains.Reading(grains.DATE, "iso-date")
    span = grains.fixed_span(grains.DATE)
    for other_side, own_side in (("AB/CD/EF/G", "AB-CD-EF-G"), ("AB-CD-EF-GH-IJKL", "AB/CD/EF GH:IJKL")):
        assert parsing.is_code_text(other_side) != parsing.is_code_text(own_side)
        assert grains.filled_at_its_length(other_side, reading, 7, span, {}) is None, other_side
        made = grains.filled_at_its_length(own_side, reading, 7, span, {})
        assert made is not None and len(made) == len(own_side), (own_side, made)
        assert parsing.is_code_text(made) == parsing.is_code_text(own_side), made
    column = _held_iso_block(tmp_path, ((2028, 2031),))
    cells = ["1234-56-78", "AB/CD/EF/G", "1234-56-79"]
    found, _unwritten = generation._inside_the_grain(column, cells, [7, 11, 17])
    assert found[1] == "AB/CD/EF/G", found
    assert found[0] != cells[0] and datetime.date.fromisoformat(found[0]).year in (2028, 2029, 2030, 2031), found


def test_a_date_pass_column_naming_a_stamp_publishes_no_room() -> None:
    """The verify of repair 1, item 3 (i) (LANE ID-ROOM2 RULINGS 6 (3)): a column held with `--identifier` whose named
    layouts include a stamp or a clock, which the date pass does not write (ISO dates beside hourly stamps: 19,600
    of 20,000 twin cells no date under NF136), publishes `[]` and keeps its remarks, so no remark says its twin's
    cells are dates; a column of dates alone keeps its block. Mutant M18: the stamp's layout not looked at.
    """
    cells = [f"19{10 + k % 80}-01-0{1 + k % 9}" for k in range(400)] + [
        f"19{10 + k % 80}-01-0{1 + k % 9}T0{k % 10}:00:00" for k in range(1600)
    ]
    held = taxonomy.with_made_up_years(_held({"%%%%-%%-%%": 400, "%%%%-%%-%%@%%:%%:%%": 1600}, 1200), cells)
    assert held.details["made_up_years"] == [] and held.remarks == []
    assert taxonomy._a_clock_layout("%%:%%") and taxonomy._a_clock_layout("%%%%-%%-%% %:%% @@")
    assert not taxonomy._a_clock_layout("%%%%-%%-%%") and not taxonomy._a_clock_layout("@@:@@")
    held = taxonomy.with_made_up_years(_held({"%%%%-%%-%%": 400}, 400), cells[0:400])
    assert _runs(held) == [[2028, 2030]]


def test_a_year_alone_is_read_where_the_column_holds_figures_alone() -> None:
    """The verify of repair 1, item 3 (iii): the date pass writes a held dated column's cells of figures alone (which
    the census does not name, `n_all_digits`) as years alone of the block -- 1,008 such cells of 20,000
    diagnosis dates were written as eleven-figure numbers under NF136 -- so the producer reads every cell as a year
    alone too: `2-0-30` merges as the year `2030` does, so the block from 2028 is no room; and the twin's check
    names the year alone beside the named layouts. Mutants: M19, no cell read as a year alone; M20, the year
    alone not named to the twin's check.
    """
    import copy

    cells = [f"19{50 + k % 40}-0{1 + k % 9}-1{k % 9}" for k in range(999)] + ["2-0-30"]
    column = _held({"%%%%-%%-%%": 999, "(withheld)": 1}, 1000)
    details = copy.copy(column.details)
    details["n_all_digits"] = 40
    held = taxonomy.with_made_up_years(dataclasses.replace(column, details=details), cells)
    assert _runs(held) == []
    held = taxonomy.with_made_up_years(column, cells)
    assert _runs(held) == [[2028, 2033]]
    facts = contract.IdentifierFacts(
        min_length=4, max_length=10, all_whole_numbers=False, n_all_digits=40, n_code_alphabet=40,
        n_distinct_by_occurrences={}, layout_forms={"%%%%-%%-%%": 960, contract.WITHHELD: 40},
        layout_prefixes={}, made_up_years=((2028, 2033),),
    )
    named = generation._named_date_layouts(facts)
    assert named == {"%%%%-%%-%%": True, "%%%%": True}
    published = generation._room_published(([2028, 2029, 2030, 2031, 2032, 2033], []))
    assert generation._off_the_real_years("2031", named, parsing.LAYOUT_PLAIN, published)
    assert not generation._off_the_real_years("2034", named, parsing.LAYOUT_PLAIN, published)
    assert generation._named_date_layouts(dataclasses.replace(facts, n_all_digits=0)) == {"%%%%-%%-%%": True}


def _iso_and_month_first(share_iso: float) -> "tuple[list[str], dict[str, int]]":
    """20,000 births of 1930 to 1999, ISO or month first (the suite's held column `birth_held`), and their census."""
    import random

    draw = random.Random(1)
    cells: "list[str]" = []
    for _place in range(20_000):
        day = datetime.date.fromordinal(draw.randint(datetime.date(1930, 1, 1).toordinal(),
                                                     datetime.date(1999, 12, 31).toordinal()))
        cells += [day.isoformat() if draw.random() < share_iso else day.strftime("%m/%d/%Y")]
    iso = sum(1 for cell in cells if "-" in cell)
    return cells, {"%%%%-%%-%%": iso, "%%/%%/%%%%": len(cells) - iso}


def test_the_date_pass_takes_each_layout_s_share_at_the_days_it_writes() -> None:
    """The suite of repair 1's head (tests/test_zoo_held_layouts.py, `birth_held`, 20,000 rows): ISO and month-first
    births of 1930 to 1999 held with `--identifier` were written as record numbers, every cell. Repair 1's own
    count of 144 month-first dates a year asked the block 2028 to 2138, and a month-first `02/01/1955` merges as
    `2119-05-05` does, and `1952-10-01` read day first as the 19th of May 2101 -- so the block was no room. On
    the date pass each layout's dates now take its own share of the block's first years (ISO 66, 2028 to 2093;
    month first 111), checked against the readings of its own orders at the days the date pass writes there (no
    day past 12 in a year written last), every real cell's own date and the cross rule: the room stands. The
    G1 floor, which draws over the whole block at any day, reads every order whole as before. Mutants: M21, no
    day cap; M22, the shares not looked at (the union over the whole block).
    """
    cells, forms = _iso_and_month_first(0.6)
    held = taxonomy.with_made_up_years(_held(forms, len(set(cells))), cells)
    assert _runs(held) == [[2028, 2138]], _runs(held)
    facts = contract.IdentifierFacts(
        min_length=10, max_length=10, all_whole_numbers=False, n_all_digits=0, n_code_alphabet=0,
        n_distinct_by_occurrences={}, layout_forms=forms, layout_prefixes={}, made_up_years=((2028, 2138),),
    )
    assert generation._room_shares(facts, len(set(cells))) == {"%%%%-%%-%%": 66, "%%/%%/%%%%": 111}
    assert taxonomy.years_of_merged_date(parsing.merged_key("1952-10-01"), "DMY") == (2101,)
    assert taxonomy.years_of_merged_date(parsing.merged_key("1952-10-01"), "DMY", 12) == ()
    assert taxonomy.years_of_merged_date(parsing.merged_key("02/01/1955"), "YMD") == (2119,)
    cells, forms = _iso_and_month_first(0.15)
    assert _runs(taxonomy.with_made_up_years(_held(forms, len(set(cells))), cells))[0][0] == 2028


def test_the_date_pass_writes_each_layout_in_its_own_share(tmp_path: pathlib.Path) -> None:
    """The twin's half (`_room_shares`, `_room_of_layout`): on a column of ISO and month-first dates whose block is
    2028 to 2138, the ISO layout's dates fall in 2028 to 2093 and the month-first layout's past 2093 too, and the
    oracle writes the same (its `pass_share` from the rule statement). Mutant M24: the whole block a layout.
    """
    from synthtwin import cli

    table = tmp_path / "t.csv"
    first = datetime.date(1940, 1, 1).toordinal()
    with open(table, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("dob,value\n")
        for row in range(600):
            day = datetime.date.fromordinal(first + 37 * row)
            handle.write(f"{day.isoformat() if row % 5 < 3 else day.strftime('%m/%d/%Y')},{row % 7}\n")
    assert cli.main(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace", "--identifier", "dob"],
                    small_tables_refused=False) == 0
    cells, forms = _iso_and_month_first(0.6)
    distinct = len(set(cells))
    column = [one for one in contract.load_profile(f"{tmp_path / 't-profile.json'}").columns if one.name == "dob"][0]
    assert isinstance(column.facts, contract.IdentifierFacts) and column.time_grain is None
    facts = dataclasses.replace(column.facts, layout_forms=forms, made_up_years=((2028, 2138),), n_all_digits=0)
    column = dataclasses.replace(column, facts=facts, n_distinct=distinct)
    walked = [f"{1000 + k:04d}-{10 + k % 90:02d}-{10 + k % 89:02d}" for k in range(500)] + [
        f"{10 + k % 90:02d}/{10 + k % 89:02d}/{1000 + k:04d}" for k in range(500)
    ]
    out = generation._dates_in_their_layouts(column, facts, walked, list(walked), ())
    iso_years = [int(cell[0:4]) for cell in out[0:500]]
    month_first_years = [int(cell[6:10]) for cell in out[500:]]
    assert min(iso_years) >= 2028 and max(iso_years) <= 2093, (min(iso_years), max(iso_years))
    assert min(month_first_years) >= 2028 and 2093 < max(month_first_years) <= 2138, max(month_first_years)
    oracle = _the_oracle()
    block = {"layout_forms": forms, "made_up_years": [[2028, 2138]], "n_distinct": distinct, "n_all_digits": 0,
             "missing_by_source": {}, "time_grain": None}
    assert oracle.dates_in_their_layouts(block, walked, list(walked)) == out


def test_a_year_first_layout_beside_month_first_writes_the_years_of_a_nought(tmp_path: pathlib.Path) -> None:
    """Batch 4q's merge (K-HZ-13's proof on b93f128a): beside a layout written year last, a year-first layout's share
    longer than the 72 years 2028 to 2099 takes the years whose second figure is a nought (`taxonomy.
    made_up_year_first_share`), as the producer published them: 18,000 ISO and 2,000 month-first values publish
    `[[2028, 2126], [3000, 3026]]`, the ISO share is 2028 to 2099 and 3000 to 3026, the month-first share the
    block's first 28 years. The oracle writes the same, from the rule statement (the case diagnostic A's report
    left owed: the oracle's mirror had been met only where the stepped share is the old one). MUTANTS: the twin's
    `_room_of_layout` taking the block's first years beside year-last layouts too (ISO dates of 2100 to 2126); the
    oracle's `room_for` doing so (the oracle and the product part).
    """
    from synthtwin import cli

    table = tmp_path / "t.csv"
    first = datetime.date(1940, 1, 1).toordinal()
    with open(table, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("dob,value\n")
        for row in range(600):
            day = datetime.date.fromordinal(first + 37 * row)
            handle.write(f"{day.isoformat() if row % 5 < 3 else day.strftime('%m/%d/%Y')},{row % 7}\n")
    assert cli.main(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace", "--identifier", "dob"],
                    small_tables_refused=False) == 0
    forms = {"%%%%-%%-%%": 18000, "%%/%%/%%%%": 2000}
    column = [one for one in contract.load_profile(f"{tmp_path / 't-profile.json'}").columns if one.name == "dob"][0]
    assert isinstance(column.facts, contract.IdentifierFacts) and column.time_grain is None
    facts = dataclasses.replace(
        column.facts, layout_forms=forms, made_up_years=((2028, 2126), (3000, 3026)), n_all_digits=0
    )
    column = dataclasses.replace(column, facts=facts, n_distinct=20000)
    assert generation._room_shares(facts, 20000) == {"%%%%-%%-%%": 99, "%%/%%/%%%%": 28}
    walked = [f"{1000 + k:04d}-{10 + k % 90:02d}-{10 + k % 89:02d}" for k in range(500)] + [
        f"{10 + k % 90:02d}/{10 + k % 89:02d}/{1000 + k:04d}" for k in range(500)
    ]
    out = generation._dates_in_their_layouts(column, facts, walked, list(walked), ())
    iso_years = [int(cell[0:4]) for cell in out[0:500]]
    month_first_years = [int(cell[6:10]) for cell in out[500:]]
    assert all((year // 100) % 10 == 0 for year in iso_years), sorted(set(iso_years))
    assert min(iso_years) >= 2028 and max(iso_years) >= 3000, (min(iso_years), max(iso_years))
    assert min(month_first_years) >= 2028 and max(month_first_years) <= 2055, max(month_first_years)
    oracle = _the_oracle()
    block = {"layout_forms": forms, "made_up_years": [[2028, 2126], [3000, 3026]], "n_distinct": 20000,
             "n_all_digits": 0, "missing_by_source": {}, "time_grain": None}
    assert oracle.dates_in_their_layouts(block, walked, list(walked)) == out


def test_the_compact_order_s_real_year_is_held() -> None:
    """Skeptic 1's item 3 (a): a held block naming `%%%%-%%-%%` and `%%%%%%%%` whose cells include a real
    `20300105` publishes no four-figure run (its block from 2028 takes 2030). Mutant J: the compact order
    `C` skipped in the producer's reading.
    """
    cells = [f"19{50 + k % 40}-0{k % 9 + 1}-1{k % 9}" for k in range(1199)] + ["20300105"]
    held = taxonomy.with_made_up_years(_held({"%%%%-%%-%%": 1199, "%%%%%%%%": 1}, 1200), cells)
    assert _runs(held) == []


def test_a_date_read_only_day_first_is_held() -> None:
    """Skeptic 1's item 3 (b): `%%/%%/%%%%` with a real `13/05/2030`, a date only read day first, publishes no
    four-figure run. Mutant K: each layout read in its first order alone.
    """
    cells = [f"0{k % 9 + 1}/1{k % 9}/19{50 + k % 40}" for k in range(1199)] + ["13/05/2030"]
    held = taxonomy.with_made_up_years(_held({"%%/%%/%%%%": 1200}, 1200), cells)
    assert _runs(held) == []


def test_an_explicit_null_is_refused(tmp_path: pathlib.Path) -> None:
    """Codex's item 5: `made_up_years: null` read as an omission let the twin write 368 cells equal to eleven
    real values under NF136. The loader refuses it in plain words; a real omission (a description written
    before the key) still loads. Mutant: the null let through.
    """
    from synthtwin import cli

    import fixtures

    table = tmp_path / "t.csv"
    first = datetime.date(1940, 1, 1).toordinal()
    with open(table, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("dob,value\n")
        for row in range(600):
            handle.write(f"{datetime.date.fromordinal(first + row % 600).isoformat()},{row % 7}\n")
    assert cli.main(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace", "--identifier", "dob"],
                    small_tables_refused=False) == 0
    path = tmp_path / "t-profile.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    block = [one for one in document["columns"] if one["name"] == "dob"][0]
    assert isinstance(block.get("made_up_years"), list)
    block["made_up_years"] = None
    fixtures.write_profile(tmp_path, "t-profile.json", document)
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(f"{path}")
    assert "made_up_years" in f"{refused.value}" and "nothing at all" in f"{refused.value}"
    del block["made_up_years"]
    fixtures.write_profile(tmp_path, "t-profile.json", document)
    contract.load_profile(f"{path}")


def test_a_step_of_the_date_pass_finds_its_run_directly(monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 4: every step rebuilt the runs of every published year (3.9, 11.6 and 36.7 CPU seconds for
    40,000, 80,000 and 160,000 values). A step now reads one year's count once, whatever the room holds.
    Mutant: the run-by-run search restored (red: 100 reads a step over 8,000 years).
    """
    calls = {"reads": 0}
    real = generation._room_dates_once

    def counted(form: str, years: "list[int]") -> int:
        calls["reads"] = calls["reads"] + 1
        return real(form, years)

    monkeypatch.setattr(generation, "_room_dates_once", counted)
    years = (list(range(2028, 10000)), [])
    count = generation._room_form_dates("%%%%-%%-%%", years)
    assert calls["reads"] == 1
    for step in (0, count // 2, count - 1):
        calls["reads"] = 0
        assert generation._room_filled_form("%%%%-%%-%%", step, years) is not None
        assert calls["reads"] == 1, (step, calls)
    assert generation._room_filled_form("%%%%-%%-%%", count, years) is None


def test_the_producer_keeps_no_record_a_key() -> None:
    """Codex's item 6: eleven copies of one date beside 999,989 different `R` and eight figures added 262,628,922
    traced bytes in the producer, a tuple and two dictionaries a merged key. At 100,000 keys it now holds the
    two bounded sets of years and at most `MADE_UP_KEYS_REMEMBERED` keys. Mutant: a record kept a key.
    """
    import tracemalloc

    cells = ["1970-01-01"] * 11 + [f"R{10_000_000 + k}" for k in range(99_989)]
    column = _held({"%%%%-%%-%%": 11, "@%%%%%%%%": 99_989}, 99_990)
    tracemalloc.start()
    try:
        before = tracemalloc.get_traced_memory()[0]
        tracemalloc.reset_peak()
        held = taxonomy.with_made_up_years(column, cells)
        added = tracemalloc.get_traced_memory()[1] - before
    finally:
        tracemalloc.stop()
    assert _runs(held) == [[2028, 2028]]
    assert added < 1_000_000, added


def test_c1_an_affixed_key_is_read_between_its_affixes() -> None:
    """C1 (LANE ID-ROOM2 RULINGS 2): `P200000Q4444` upward, each once, read as an affixed number, now meets lane
    HX5's rule as `P200000` upward does: every one different. A closing holding no figure (a unit, a currency)
    is still read by no arm, and a code that repeats on two rows a value or more is not reached. Mutant: the
    affixed reading not read between its affixes (`_a_whole_number_between_affixes` never asked).
    """
    from synthtwin import asking

    keys = [f"P{200000 + place}Q4444" for place in range(2000)]
    assert asking._a_whole_number_between_affixes("P200000Q4444") == ("P", "200000", "Q4444")
    assert asking._a_whole_number_between_affixes("ACC123456-2024") == ("ACC", "123456", "-2024")
    assert asking._a_whole_number_between_affixes("12345mg") is None
    assert asking._a_whole_number_between_affixes("12345 EUR") is None
    assert asking._whole_numbers_each_on_one_row(keys, taxonomy.ROLE_AFFIXED)
    assert asking._each_on_one_row_arm(keys, False, "ref", True) == ("different", False)
    assert not asking._whole_numbers_each_on_one_row([f"{100000 + 7 * place}mg" for place in range(2000)],
                                                    taxonomy.ROLE_AFFIXED)
    repeated = [f"L{10000 + place % 900}-7" for place in range(20_000)]
    assert not asking._whole_numbers_each_on_one_row(repeated, taxonomy.ROLE_AFFIXED)
    said = asking._each_on_one_row_said(keys, False, "ref", taxonomy.ROLE_AFFIXED)
    assert "every one is different" in said and "200000" not in said
