"""P4-D361: a reach NF36 compares is never a fragment; below the line the remark goes.

NF36 chooses its first clause by comparing the day-first reach with the
month-first one, reading both as whole numbers. Since P4-D347 a floored
count below the census line became a fragment everywhere, and at those
two positions `rendered` raised TypeError: 144 day-first dates beside
one to ten that a month-first reading also parses stopped `synthtwin
profile` at every floor, and `synthtwin validate` on a twin whose own
description reached the same shape (82b1f1a, d93fd43). Contract NF36
withdraws the remark there, and the producer now does.

MUTATION: delete the `_COMPARED_FLOORED_POSITIONS` branch of
`taxonomy._arguments_at_the_line` and every test here but the grammar's
own raises or fails; keep it only above a line of two and the floor-1
and floor-2 cases fail; withdraw at a compared position whatever the
count and the controls at the line fail.
"""

import datetime
import pathlib
import random

import pytest

import fixtures
import kpi_shapes
from synthtwin import contract, profile, reading, taxonomy

# -- the column that stopped the tool ------------------------------------


def _visit_days(low: int, floor: int) -> str:
    """13 to 24 June 2032 day first, twelve each, and ``low`` cells of 11 June."""
    cells: "list[str]" = []
    for day in range(13, 25):
        cells += [f"{day:02d}/06/2032"] * 12
    cells += ["11/06/2032"] * low
    random.Random(1000 * floor + low).shuffle(cells)
    return "visit_day\n" + "".join(f"{cell}\n" for cell in cells)


def _slashed_remarks(document: "dict") -> "list[object]":
    """The NF36 remarks of a one-column description."""
    return [
        remark
        for remark in document["columns"][0]["remarks"]
        if getattr(remark, "form", "") == taxonomy.REMARK_SLASHED_EVIDENCE
    ]


_BELOW_THE_LINE = [(11, low) for low in range(1, 11)] + [(30, low) for low in range(1, 30)]


@pytest.mark.parametrize(("floor", "low"), _BELOW_THE_LINE)
def test_the_column_is_described_generated_and_validated(
    tmp_path: pathlib.Path, floor: int, low: int
) -> None:
    """Every command ends as it does on any clean column, at two seeds."""
    table = fixtures.write(tmp_path, "visits.csv", _visit_days(low, floor))
    flags = ["--smallest-group", f"{floor}"]
    assert kpi_shapes.quiet_cli(
        ["profile", str(table), "--out-dir", str(tmp_path), "--replace", *flags]
    ) == 0
    description = tmp_path / "visits-profile.json"
    assert "month-first reading" not in description.read_text(encoding="utf-8")
    for seed in ("7", "13"):
        folder = tmp_path / f"seed-{seed}"
        folder.mkdir()
        assert kpi_shapes.quiet_cli(
            ["generate", str(description), "--out-dir", str(folder), "--seed", seed, "--replace"]
        ) == 0
        for checked in (folder / "visits-twin.csv", table):
            report = folder / f"report-{checked.parent.name}"
            report.mkdir()
            assert kpi_shapes.quiet_cli(
                ["validate", str(description), "--twin", str(checked),
                 "--out-dir", str(report), "--replace"]
            ) == 0, f"{checked.name} at seed {seed}"


@pytest.mark.parametrize("floor", (1, 2, 11, 30))
def test_the_remark_goes_below_the_line_and_stands_at_it(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """Withdrawn for every losing reach under the line; its digits at the line."""
    line = max(floor, 2)
    for low in range(1, line + 1):
        described = kpi_shapes.describe(
            tmp_path / f"low-{low}", "visits", _visit_days(low, floor), floor
        )
        remarks = _slashed_remarks(described.document)
        if low < line:
            assert remarks == [], f"low {low}: {remarks}"
            continue
        assert [remark.arguments for remark in remarks] == [
            (144 + low, low, 144, 0, taxonomy.READING_DAY_FIRST)
        ]


# -- every family, undeclared and declared --------------------------------

_FAMILIES = {
    "slashed": lambda first, second: f"{first:02d}/{second:02d}/2032",
    "stamp": lambda first, second: f"{first:02d}/{second:02d}/2032 10:30",
    "dotted": lambda first, second: f"{first:02d}.{second:02d}.2032",
    "two-figure": lambda first, second: f"{first:02d}/{second:02d}/32",
}


@pytest.mark.parametrize("family", sorted(_FAMILIES))
@pytest.mark.parametrize("declared", (False, True))
@pytest.mark.parametrize("floor", (1, 11, 30))
def test_every_ambiguous_family_withdraws_the_remark(
    tmp_path: pathlib.Path, family: str, declared: bool, floor: int
) -> None:
    """The losing reach at one and at the line less one, on both sides.

    Undeclared, the day-first reading wins and the month-first reach
    loses; declared day first, a column the month-first reading wins
    loses the day-first reach, the first argument.
    """
    spelled = _FAMILIES[family]
    line = max(floor, 2)
    for low in sorted({1, line - 1}):
        if declared:
            cells = [spelled(6, 13 + step % 12) for step in range(144)] + [spelled(6, 11)] * low
        else:
            cells = [spelled(13 + step % 12, 6) for step in range(144)] + [spelled(11, 6)] * low
        random.Random(low).shuffle(cells)
        table = fixtures.write(
            tmp_path, f"{family}-{low}.csv", "c\n" + "".join(f"{cell}\n" for cell in cells)
        )
        settings = taxonomy.Settings(small_cell_floor=floor, day_first=declared)
        document = profile.build_document(
            reading.read_table(str(table), small_cell_floor=floor), settings, [], [], []
        )
        block = document["columns"][0]
        assert block["role"] == taxonomy.ROLE_DATETIME, f"low {low}"
        assert _slashed_remarks(document) == [], f"low {low}"
        profile.check_publication(document)


# -- the grammar: which positions the rendering reads as whole numbers ----

_WORD = taxonomy.NOTE_ARGUMENT_WORDS[0]
_NUMBERS = (taxonomy.SAID_WRITTEN_AS_NUMBERS, (3, 400))
_DATES = (taxonomy.SAID_READ_AS_DATES, (2, _WORD))

# One legal argument tuple per form carrying a floored position. A form
# that gains one without an entry here fails the first test below.
_ARGUMENTS: "dict[str, tuple[object, ...]]" = {
    taxonomy.SAID_READ_AS_DATES: (40, _WORD),
    taxonomy.REMARK_SLASHED_EVIDENCE: (300, 200, 150, 50, taxonomy.READING_DAY_FIRST),
    taxonomy.REMARK_TWO_READINGS_FIT: (40,),
    taxonomy.REMARK_A_LETTER_NEEDS_A_DECLARATION: (40,),
    taxonomy.REMARK_NO_READING_FITS: (_NUMBERS, _DATES, 360, 90, 60, 40, 40, 40, 40),
    taxonomy.REMARK_GROUP_COMMAS: (40, 40),
}

_FRAGMENTS = (
    (taxonomy.SAID_FEWER_THAN_THE_LINE, (11,)),
    (taxonomy.SAID_SOME_BUT_NOT_ALL, ()),
    (taxonomy.SAID_SOME, ()),
)


def _with(form: str, place: int, argument: object) -> "tuple[object, ...]":
    built = list(_ARGUMENTS[form])
    built[place] = argument
    return tuple(built)


def test_only_the_compared_reaches_are_read_as_whole_numbers() -> None:
    """Every floored position takes each fragment, except the two NF36 compares.

    MUTATION: read any other floored position with `_whole` in
    `rendered`, or take a position out of `_COMPARED_FLOORED_POSITIONS`,
    and the two sets differ.
    """
    assert {form for form, _place in taxonomy.FLOORED_POSITIONS} == set(_ARGUMENTS)
    compared: "set[tuple[str, int]]" = set()
    for form, place in taxonomy.FLOORED_POSITIONS:
        assert taxonomy.rendered(form, _ARGUMENTS[form])
        for fragment in _FRAGMENTS:
            try:
                taxonomy.rendered(form, _with(form, place, fragment))
            except TypeError:
                compared |= {(form, place)}
    assert compared == set(taxonomy._COMPARED_FLOORED_POSITIONS)


@pytest.mark.parametrize("line", (2, 11, 30))
def test_a_compared_reach_under_the_line_withdraws_the_sentence(line: int) -> None:
    """None for every count from one to the line less one; the digits from the line."""
    for form, place in taxonomy._COMPARED_FLOORED_POSITIONS:
        for count in range(1, line):
            assert taxonomy._arguments_at_the_line(
                form, _with(form, place, count), line, 1000
            ) is None, f"{form} {place} at {count}"
        for count in (0, line, line + 1):
            arguments = _with(form, place, count)
            assert taxonomy._arguments_at_the_line(form, arguments, line, 1000) == arguments


# -- the batteries ---------------------------------------------------------


def test_sixty_padded_day_first_tables_describe_and_validate(tmp_path: pathlib.Path) -> None:
    """dd/mm/yyyy over 2024, 20 to 200 rows, the default floor, twins at 7 and 13.

    On 82b1f1a three raised describing (900000: 22 rows, 7 on a day of
    twelve or less) and three twins raised validating.
    """
    raised: "list[str]" = []
    for seed in range(900000, 900060):
        rng = random.Random(seed)
        rows = rng.randint(20, 200)
        days = [datetime.date(2024, 1, 1) + datetime.timedelta(days=rng.randint(0, 365)) for _ in range(rows)]
        text = "day\n" + "".join(f"{day.day:02d}/{day.month:02d}/{day.year}\n" for day in days)
        try:
            described = kpi_shapes.describe(tmp_path / f"{seed}", "dates", text)
        except TypeError as error:
            raised += [f"{seed} describing: {error}"]
            continue
        for twin_seed in (7, 13):
            try:
                twin = kpi_shapes.twin_text(described, twin_seed)
                kpi_shapes.measure(described, twin, f"twin-{twin_seed}.csv")
            except TypeError as error:
                raised += [f"{seed} at {twin_seed}: {error}"]
    assert raised == []


def _hole_column(index: int) -> "tuple[int, str, list[str]]":
    """One unpadded day-first column with one declared-missing day inside it."""
    rng = random.Random(800000 + index)
    floor = rng.choice((11, 15, 25, 30, 36))
    start = datetime.date(rng.randint(1950, 2020), rng.randint(1, 12), rng.randint(1, 28))
    days = [start + datetime.timedelta(days=step) for step in range(rng.randint(8, 90))]
    weights = [rng.random() ** 2 for _ in days]
    rows = rng.randint(110, 360)
    hole = days[rng.randint(1, len(days) - 2)]
    spelled = f"{hole.day}/{hole.month}/{hole.year}"
    cells = [
        f"{day.day}/{day.month}/{day.year}"
        for day in rng.choices(days, weights, k=rows)
        if day != hole
    ]
    cells += [spelled] * rng.randint(floor, 2 * floor)
    rng.shuffle(cells)
    return floor, spelled, cells


def test_three_hundred_day_first_columns_with_a_missing_day(tmp_path: pathlib.Path) -> None:
    """Each described at its floor with its hole declared, twins at 7 and 13 validated.

    On 82b1f1a eight raised describing and one column's two twins raised
    validating.
    """
    raised: "list[str]" = []
    for index in range(300):
        floor, spelled, cells = _hole_column(index)
        folder = tmp_path / f"{index}"
        folder.mkdir()
        table = fixtures.write(folder, "c.csv", "c\n" + "".join(f"{cell}\n" for cell in cells))
        settings = taxonomy.Settings(small_cell_floor=floor, declared_missing_values=(spelled,))
        try:
            document = profile.build_document(
                reading.read_table(str(table), small_cell_floor=floor), settings, [], [], []
            )
        except TypeError as error:
            raised += [f"{800000 + index} describing: {error}"]
            continue
        written = fixtures.write_profile(folder, "c-profile.json", document)
        described = kpi_shapes.Described(folder, table, document, contract.load_profile(str(written)))
        for seed in (7, 13):
            try:
                kpi_shapes.measure(described, kpi_shapes.twin_text(described, seed), f"twin-{seed}.csv")
            except TypeError as error:
                raised += [f"{800000 + index} at {seed}: {error}"]
    assert raised == []
