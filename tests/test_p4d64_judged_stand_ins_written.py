"""Plan P4-D6.4: a judged pass's cells are written as the source wrote them.

THE OWNER'S RULING OF 2026-09-15 IS THAT THE TWIN WRITES EVERYTHING AS
THE SOURCE WROTE IT, and plan P4-D6.1's one exception predated it: a
`missing_by_source` key a JUDGED pass put there -- a stand-in number
such as `-999`, or a calendar placeholder such as `1900-01-01` -- was
written blank. A declared spelling came back at its count and a judged
one did not.

**What that cost, measured on e53d5f4.** The shared every-role table's
`reading` column holds thirteen `-999` cells and no blank. Its twin
held thirteen blanks, so `pandas.read_csv` read the real column as
`int64` and the twin's as `float64` at seeds 20260811, 1, 2 and 3 and at
floors 1 and 11. `df.reading.astype(int)` raised on the twin and not on
the table, and `df.reading == -999` selected thirteen rows of the table
and none of the twin: code developed on the twin did not run unchanged.

**Why it was blank, and what replaced the reason.** A twin's generated
values need not fire the producer's outlier-and-share rule a second
time. Measured with the cells written back and the rule asked again:
400 whole numbers whose fence stood a few units inside `-999`, with
twelve `-999` cells, gave five twins in eight whose twelve cells the
validator read as VALUES, missing obligations while the real table
passed. So the validator now hands the producer the candidates the
description judged missing in each column, and they are read as absent
there without the arithmetic (validation method V2.4-A8, amended).

Every table here is built by seeded neutral code at runtime (plan D13).
"""

import contextlib
import csv
import datetime
import io
import json
import pathlib
import random

import pandas
import pytest

from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)
from tests import crosscheck, fixtures, workbooks
from tests.test_stage2_round_trip import _exit_of

EVERY_ROLE_SEEDS = (20260811, 1, 2, 3)
FLOORS = (1, 11)


def _quietly(argv: "list[str]") -> int:
    """One command, its screen output kept off the test log."""
    with contextlib.redirect_stdout(io.StringIO()):
        return _exit_of(argv)


def _dtypes(frame: "pandas.DataFrame") -> "dict[str, str]":
    return {str(name): str(frame[name].dtype) for name in frame.columns}


# ------------------------------------------------------ the every-role table


@pytest.mark.parametrize("floor", FLOORS)
def test_every_role_twin_columns_read_with_the_real_dtypes(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """The KPI shape: every twin column has the dtype pandas gives the real one.

    Four seeds and both floors, on the table the critic measured. Before
    plan P4-D6.4 exactly one column parted, `reading`, `int64` against
    `float64`, at every seed and floor; after it none does.
    """
    table = fixtures.write(
        tmp_path, "t.csv", fixtures.every_role_and_joined_table()
    )
    document = profile.build_document(
        reading.read_table(str(table)),
        taxonomy.Settings(small_cell_floor=floor),
        ["record_code"],
        [],
        [fixtures.JOINED_COLUMN],
    )
    block = [one for one in document["columns"] if one["name"] == "reading"][0]
    assert block["missing_by_source"] == {"-999": 13}, (
        "the fixture must still publish the judged stand-in, or this "
        "test measures nothing"
    )
    loaded = contract.load_profile(
        str(fixtures.write_profile(tmp_path, "p.json", document))
    )
    real = pandas.read_csv(table)
    assert str(real["reading"].dtype) == "int64"
    for seed in EVERY_ROLE_SEEDS:
        text = rendering.twin_csv(generation.generate(loaded, seed))
        twin = pandas.read_csv(io.StringIO(text))
        assert list(twin.columns) == list(real.columns)
        assert _dtypes(twin) == _dtypes(real), (seed, floor)
        # ...and code a researcher writes against the stand-in behaves
        # the same way on both files.
        assert int((twin["reading"] == -999).sum()) == 13
        assert twin["reading"].astype(int).dtype == real["reading"].dtype


# -------------------------------------------- the KPI critic's eight shapes


def _delimited(
    path: pathlib.Path,
    names: "list[str]",
    rows: "list[list[str]]",
    delimiter: str = ",",
    newline: str = "\n",
    bom: bool = False,
) -> None:
    out = io.StringIO()
    writer = csv.writer(out, delimiter=delimiter, lineterminator=newline)
    writer.writerow(names)
    for row in rows:
        writer.writerow(row)
    data = out.getvalue().encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    path.write_bytes(data)


def _serial(day: str) -> str:
    """The spreadsheet's serial number for one ISO day."""
    count = (
        datetime.date.fromisoformat(day) - datetime.date(1899, 12, 30)
    ).days
    if day < "1900-03-01":
        count = count - 1
    return f"{count}"


def _book(
    path: pathlib.Path,
    names: "list[str]",
    rows: "list[list[str]]",
    numeric: "tuple[int, ...]" = (),
    dated: "tuple[int, ...]" = (),
) -> None:
    """One sheet: text as inline strings, the named columns as numbers.

    A column in `dated` holds ISO days written as date cells: the day's
    serial number under the sheet's `yyyy-mm-dd` style, counted the way
    the spreadsheet counts it, fictitious 29 February 1900 included.
    """
    body = [
        (
            1,
            [
                workbooks.cell(
                    f"{workbooks._column(index + 1)}1", name, kind="inlineStr"
                )
                for index, name in enumerate(names)
            ],
        )
    ]
    for place, row in enumerate(rows):
        number = place + 2
        cells = []
        for index, value in enumerate(row):
            if value == "":
                continue
            where = f"{workbooks._column(index + 1)}{number}"
            if index in dated:
                cells += [workbooks.cell(where, _serial(value), style=1)]
            elif index in numeric:
                cells += [workbooks.cell(where, value)]
            else:
                cells += [workbooks.cell(where, value, kind="inlineStr")]
        body += [(number, cells)]
    span = f"A1:{workbooks._column(len(names))}{len(rows) + 1}"
    path.write_bytes(
        workbooks.package(
            [
                (
                    "[Content_Types].xml",
                    workbooks._content_types(1, False, False, False),
                ),
                ("_rels/.rels", workbooks._root_rels()),
                ("xl/workbook.xml", workbooks._workbook([("Data", "")])),
                (
                    "xl/_rels/workbook.xml.rels",
                    workbooks._workbook_rels(1, False),
                ),
                ("xl/styles.xml", workbooks._styles()),
                ("xl/worksheets/sheet1.xml", workbooks.sheet(body, dimension=span)),
            ]
        )
    )


def _critic_shapes() -> "list[tuple[str, list[str], list[list[str]], tuple[str, ...]]]":
    """The four realistic shapes of the KPI critic's battery, 400 rows each.

    Files and dialect, dates, numbers, and labels beside a record number,
    exactly as its driver built them, with the same seeded draws.
    """
    draw = random.Random(9)
    shapes = []
    rows = [
        [
            f"A-{1000 + index}",
            draw.choice(["North", "South", "East", "West"]),
            f"visit {index % 9}",
        ]
        for index in range(400)
    ]
    shapes += [("A", ["record", "site", "note"], rows, ("--identifier", "record"))]
    start = datetime.date(2021, 1, 1)
    rows = []
    for index in range(400):
        day = start + datetime.timedelta(days=index % 250)
        stamp = day.strftime("%Y-%m-%dT%H:%M:%S").replace(
            "T00:00:00", f"T{8 + index % 9:02d}:{index % 60:02d}:00"
        ) + ("+01:00" if index % 2 else "Z")
        rows += [[day.strftime("%d-%b-%Y"), stamp, draw.choice(["North", "South"])]]
    shapes += [("B", ["taken_on", "seen_at", "site"], rows, ())]
    rows = []
    for index in range(400):
        amount = 1000 + index * 7.25
        text = f"{amount:,.2f}"
        if index % 37 == 0:
            text = f"({amount:,.2f})"
        rows += [
            [
                text,
                f"{(index % 40) + 0.5:.1f} mg",
                draw.choice(["North", "South", "East"]),
            ]
        ]
    shapes += [("C", ["amount", "dose", "site"], rows, ())]
    labels = (
        ["treated"] * 200
        + ["control"] * 180
        + ["withdrawn"] * 12
        + ["screen-fail"] * 3
        + ["Treated"] * 2
        + ["NA"] * 3
    )
    draw.shuffle(labels)
    rows = [
        [f"SUBJ{index:04d}", labels[index], draw.choice(["yes", "no", "n/a"])]
        for index in range(400)
    ]
    shapes += [("D", ["subject", "arm", "outcome"], rows, ("--identifier", "subject"))]
    return shapes


def _read(path: pathlib.Path, delimiter: str) -> "pandas.DataFrame":
    if path.suffix == ".xlsx":
        return crosscheck.read_excel(path)
    return pandas.read_csv(path, sep=delimiter, encoding="utf-8-sig")


@pytest.mark.parametrize("floor", FLOORS)
def test_the_critic_s_eight_shapes_read_with_the_real_dtypes(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """The same KPI over the eight files of the critic's battery.

    Four shapes, each as delimited text and as a workbook, at both
    floors. They agreed before this repair as well; they are here so a
    change that parts any reader's type on a realistic file turns this
    red whether or not it touches a judged pass.
    """
    runs = []
    for letter, names, rows, flags in _critic_shapes():
        for suffix in (".csv", ".xlsx"):
            folder = tmp_path / f"{letter}{suffix[1:]}"
            folder.mkdir()
            table = folder / f"real{suffix}"
            delimiter = ";" if letter == "A" else ","
            if suffix == ".csv":
                _delimited(
                    table,
                    names,
                    rows,
                    delimiter=delimiter,
                    newline="\r\n" if letter == "A" else "\n",
                    bom=letter == "A",
                )
            else:
                _book(table, names, rows)
            assert _quietly(
                [
                    "profile", str(table), "--out-dir", str(folder),
                    "--replace", "--smallest-group", str(floor), *flags,
                ]
            ) == 0
            assert _quietly(
                [
                    "generate", str(folder / "real-profile.json"),
                    "--out-dir", str(folder), "--seed", "4", "--replace",
                ]
            ) == 0
            runs += [(letter, suffix, table, folder / f"real-twin{suffix}", delimiter)]
    # EVERY file of the battery is written before any is read back, and
    # the delimited ones are read first: a missing cross-check reader
    # then takes the workbook readings alone, never a shape synthtwin
    # was never asked to build.
    for letter, suffix, table, made, delimiter in sorted(runs, key=lambda run: run[1]):
        real = _read(table, delimiter)
        twin = _read(made, delimiter)
        assert list(twin.columns) == list(real.columns), (letter, suffix)
        assert _dtypes(twin) == _dtypes(real), (letter, suffix, floor)


# ------------------------------------------------ the judged shapes, round trip


def _judged_shapes() -> "list[tuple[str, list[str], list[list[str]], tuple[int, ...], tuple[str, ...], str]]":
    """Five shapes a judged pass reaches, each with the spelling it takes.

    Whole numbers beside `-999`; dates beside the placeholder
    `1900-01-01`; an affixed `-999 mg`, judged over the cores; a declared
    decimal-comma column's `-999,0`; and a judged column beside one that
    holds `-999` as an ordinary value, because a judgement is one
    column's and must not reach the other.
    """
    draw = random.Random(5)
    shapes = []
    rows = [
        [
            "-999" if index % 33 == 0 else str(draw.randint(1, 400)),
            draw.choice(["North", "South"]),
        ]
        for index in range(400)
    ]
    shapes += [("numbers", ["reading", "site"], rows, (0,), (), "-999")]
    rows = [
        [
            "1900-01-01"
            if index % 20 == 0
            else (
                datetime.date(2021, 1, 1)
                + datetime.timedelta(days=draw.randrange(700))
            ).isoformat(),
            draw.choice(["a", "b"]),
        ]
        for index in range(400)
    ]
    shapes += [("placeholder", ["taken_on", "site"], rows, (), (), "1900-01-01")]
    rows = [
        [
            "-999 mg" if index % 25 == 0 else f"{draw.randint(5, 90)} mg",
            draw.choice(["a", "b"]),
        ]
        for index in range(400)
    ]
    shapes += [("affixed", ["dose", "site"], rows, (), (), "-999 mg")]
    rows = [
        [
            "-999,0"
            if index % 25 == 0
            else f"{draw.randint(5, 90)},{draw.randint(0, 9)}",
            draw.choice(["a", "b"]),
        ]
        for index in range(400)
    ]
    shapes += [
        ("comma", ["amount", "site"], rows, (), ("--decimal-comma", "amount"), "-999,0")
    ]
    rows = [
        [
            "-999" if index % 25 == 0 else str(draw.randint(1, 300)),
            "-999" if index % 10 == 0 else str(draw.randint(-2000, 2000)),
        ]
        for index in range(400)
    ]
    shapes += [("two_columns", ["judged", "data"], rows, (0, 1), (), "-999")]
    return shapes


def _cases() -> "list[tuple[str, str, int]]":
    found = []
    for shape in _judged_shapes():
        for suffix in (".csv", ".xlsx"):
            if suffix == ".xlsx" and shape[0] == "comma":
                # A workbook stores a number, not a comma: the decimal
                # comma is a property of delimited text alone.
                continue
            for floor in FLOORS:
                found += [(shape[0], suffix, floor)]
    return found


@pytest.mark.parametrize("name,suffix,floor", _cases())
def test_a_judged_spelling_comes_back_and_both_files_validate(
    tmp_path: pathlib.Path, name: str, suffix: str, floor: int
) -> None:
    """Profile, generate, describe the twin again, validate twin AND table.

    The twin holds the judged spelling at exactly its published count;
    describing the twin again publishes the same `missing_by_source`;
    both files validate at nought; and pandas reads every column of the
    twin as it reads the table's. Measured on e53d5f4: nine of these
    sixteen files parted a reader's type, and describing the twin again
    recovered `missing_by_source` on none.
    """
    shape = [one for one in _judged_shapes() if one[0] == name][0]
    _name, names, rows, numeric, flags, spelling = shape
    table = tmp_path / f"real{suffix}"
    if suffix == ".csv":
        _delimited(table, names, rows)
    else:
        _book(table, names, rows, numeric)
    assert _quietly(
        [
            "profile", str(table), "--out-dir", str(tmp_path), "--replace",
            "--smallest-group", str(floor), *flags,
        ]
    ) == 0
    described = json.loads(
        (tmp_path / "real-profile.json").read_text(encoding="utf-8")
    )
    judged = described["columns"][0]
    assert judged["sentinel_verdicts"][0]["verdict"] == contract.VERDICT_MISSING
    published = judged["missing_by_source"][spelling]
    assert published >= floor
    assert _quietly(
        [
            "generate", str(tmp_path / "real-profile.json"), "--out-dir",
            str(tmp_path), "--seed", "1", "--replace",
        ]
    ) == 0
    twin = tmp_path / f"real-twin{suffix}"
    again = tmp_path / "again"
    again.mkdir()
    copied = again / f"twin{suffix}"
    copied.write_bytes(twin.read_bytes())
    assert _quietly(
        [
            "profile", str(copied), "--out-dir", str(again), "--replace",
            "--smallest-group", str(floor), *flags,
        ]
    ) == 0
    redescribed = json.loads(
        (again / "twin-profile.json").read_text(encoding="utf-8")
    )
    for first, second in zip(described["columns"], redescribed["columns"]):
        assert first["missing_by_source"] == second["missing_by_source"], (
            first["name"]
        )
    for side, checked in (("twin", twin), ("real", table)):
        out = tmp_path / f"check-{side}"
        out.mkdir()
        assert _quietly(
            [
                "validate", str(tmp_path / "real-profile.json"), "--twin",
                str(checked), "--out-dir", str(out), "--replace",
            ]
        ) == 0, side
    if suffix == ".csv":
        real_frame = pandas.read_csv(table, dtype=str, keep_default_na=False)
        twin_frame = pandas.read_csv(twin, dtype=str, keep_default_na=False)
        assert int((twin_frame[names[0]] == spelling).sum()) == published
        assert int((real_frame[names[0]] == spelling).sum()) == published
        assert _dtypes(pandas.read_csv(twin)) == _dtypes(pandas.read_csv(table))
    else:
        # THE SHEET'S CENSUS COUNTS WHAT THE TWIN WRITES (plan P4-D174),
        # and the twin writes a judged cell as the value the sheet held,
        # so no cell of the column is counted `absent`: a census that
        # still counted them absent would describe a twin of blanks.
        for block in (described, redescribed):
            classes = block["source"]["workbook"]["columns"][0]["cell_classes"]
            assert classes["absent"] == 0, classes
        assert _dtypes(crosscheck.read_excel(twin)) == _dtypes(
            crosscheck.read_excel(table)
        )


# ------------------------------------------------- the judgement not re-fired


def _near_fence_column() -> "list[str]":
    """400 whole numbers whose fence stands a few units inside `-999`.

    The shape the hand-over exists for, found by walking seeded draws for
    a column whose interquartile fence lands between -999 and -996: the
    real column judges its twelve `-999` cells missing, and a twin's
    generated values can move the fence past them.
    """
    draw = random.Random(124)
    width = 200.0
    low = -999 + 1.75 * width * (1 + draw.uniform(-0.01, 0.01))
    values = [str(round(low + draw.random() * width)) for _each in range(400)]
    cells = values + ["-999"] * 12
    draw.shuffle(cells)
    return cells


# The seeds at which a twin of that column moves the fence to -999 or
# past it, measured on the tree before the hand-over: validating each
# of these twins exited 3 while the real table exited 0.
_UNFIRED_SEEDS = (3, 4, 5, 6, 8)


def test_a_twin_that_would_not_fire_the_judgement_again_still_validates(
    tmp_path: pathlib.Path,
) -> None:
    """The hand-over of V2.4-A8, amended by plan P4-D6.4.

    Each twin below holds the twelve `-999` cells as written, and its own
    values put the outlier fence at or past -999, so the producer's rule
    asked again would read those cells as values. The validator reads
    them as the description's own verdict says, and every twin passes.
    """
    table = fixtures.write(
        tmp_path,
        "real.csv",
        fixtures.single_column_table("value", _near_fence_column()),
    )
    assert _quietly(
        ["profile", str(table), "--out-dir", str(tmp_path), "--replace"]
    ) == 0
    described = contract.load_profile(str(tmp_path / "real-profile.json"))
    assert described.columns[0].missing_by_source == {"-999": 12}
    out = tmp_path / "check-real"
    out.mkdir()
    assert _quietly(
        [
            "validate", str(tmp_path / "real-profile.json"), "--twin",
            str(table), "--out-dir", str(out), "--replace",
        ]
    ) == 0
    unfired = 0
    for seed in _UNFIRED_SEEDS:
        text = rendering.twin_csv(generation.generate(described, seed))
        cells = [line for line in text.split("\n")[1:] if line]
        assert cells.count("-999") == 12
        others = sorted(float(cell) for cell in cells if cell != "-999")
        lower = taxonomy._quantile(others, 25, 100)
        upper = taxonomy._quantile(others, 75, 100)
        fence = lower - 4.0 * (upper - lower)
        if fence <= -999:
            unfired = unfired + 1
        twin = fixtures.write(tmp_path, f"twin-{seed}.csv", text)
        outcome = validation.measure(described, str(twin))
        assert not [
            one for one in outcome.checks if one.verdict == validation.MISSED
        ], seed
    assert unfired == len(_UNFIRED_SEEDS), (
        "the case must still reach the hand-over: every one of these "
        "twins puts its fence at or past -999"
    )


def _near_fence_cells(kind: str) -> "list[str]":
    """The near-fence recipe of `_near_fence_column`, for three passes.

    `number` is that column; `affixed` is the same cells with ` mg`
    after each, so the stand-in is `-999 mg` and the judgement runs over
    the cores; `date` draws 400 days from the band [P + 1.75w, P + 2.75w]
    after P = 1900-01-01, with w = 15000 days, beside twelve cells of the
    placeholder P itself, so the calendar placeholder pass is the one
    that judges them.
    """
    draw = random.Random(124)
    if kind in ("number", "affixed"):
        width = 200.0
        low = -999 + 1.75 * width * (1 + draw.uniform(-0.01, 0.01))
        values = [str(round(low + draw.random() * width)) for _each in range(400)]
        cells = values + ["-999"] * 12
        if kind == "affixed":
            cells = [f"{cell} mg" for cell in cells]
    else:
        span = 15000.0
        origin = datetime.date(1900, 1, 1).toordinal()
        low = origin + 1.75 * span * (1 + draw.uniform(-0.01, 0.01))
        values = [
            datetime.date.fromordinal(int(low + draw.random() * span)).isoformat()
            for _each in range(400)
        ]
        cells = values + ["1900-01-01"] * 12
    draw.shuffle(cells)
    return cells


# Each pass, the file it is written as, the spelling it judges, and the
# twin seeds whose own values move the judgement past that spelling.
# Measured with the validator's hand-over withdrawn (every candidate
# passed as unjudged): each listed twin exited 3 while the real table
# exited 0, and every twin exits 0 with the hand-over in place.
_UNFIRED_ELSEWHERE = (
    ("number", ".xlsx", "-999", (3, 4, 5, 6, 8)),
    ("affixed", ".csv", "-999 mg", (3, 4, 5, 6, 8)),
    ("date", ".csv", "1900-01-01", (2, 3, 5, 7)),
    ("date", ".xlsx", "1900-01-01", (2, 3, 5, 7)),
)


@pytest.mark.parametrize(
    "kind,suffix,spelling,seeds",
    _UNFIRED_ELSEWHERE,
    ids=[f"{one[0]}{one[1]}" for one in _UNFIRED_ELSEWHERE],
)
def test_every_judged_pass_is_handed_over_end_to_end(
    tmp_path: pathlib.Path,
    kind: str,
    suffix: str,
    spelling: str,
    seeds: "tuple[int, ...]",
) -> None:
    """The hand-over of V2.4-A8 reaches the core and placeholder passes too.

    The stand-in number pass is pinned above on delimited text. The pass
    over an affixed column's cores and the calendar placeholder pass are
    reached the same way, and so is a workbook's number and date cell:
    the real column judges its twelve cells missing, and at each listed
    seed describing the twin again with a plain `synthtwin profile` does
    NOT, because the twin's own values move the judgement past the
    spelling. That is the reach: the producer's rule asked of the twin
    reads those cells as values. The validator reads them as the
    description's verdict says, so the twin validates at nought, and so
    does the table.
    """
    rows = [
        [cell, random.Random(124 + place).choice(["a", "b"])]
        for place, cell in enumerate(_near_fence_cells(kind))
    ]
    table = tmp_path / f"real{suffix}"
    if suffix == ".csv":
        _delimited(table, ["value", "site"], rows)
    elif kind == "date":
        _book(table, ["value", "site"], rows, dated=(0,))
    else:
        _book(table, ["value", "site"], rows, numeric=(0,))
    assert _quietly(
        ["profile", str(table), "--out-dir", str(tmp_path), "--replace"]
    ) == 0
    described = json.loads(
        (tmp_path / "real-profile.json").read_text(encoding="utf-8")
    )
    judged = described["columns"][0]
    assert judged["missing_by_source"] == {spelling: 12}, judged["name"]
    assert [
        one["verdict"] for one in judged["sentinel_verdicts"]
    ] == [contract.VERDICT_MISSING]
    real_check = tmp_path / "check-real"
    real_check.mkdir()
    assert _quietly(
        [
            "validate", str(tmp_path / "real-profile.json"), "--twin",
            str(table), "--out-dir", str(real_check), "--replace",
        ]
    ) == 0
    for seed in seeds:
        folder = tmp_path / f"seed-{seed}"
        folder.mkdir()
        assert _quietly(
            [
                "generate", str(tmp_path / "real-profile.json"), "--out-dir",
                str(folder), "--seed", f"{seed}", "--replace",
            ]
        ) == 0
        twin = folder / f"real-twin{suffix}"
        again = folder / "again"
        again.mkdir()
        copied = again / f"twin{suffix}"
        copied.write_bytes(twin.read_bytes())
        assert _quietly(
            ["profile", str(copied), "--out-dir", str(again), "--replace"]
        ) == 0
        redescribed = json.loads(
            (again / "twin-profile.json").read_text(encoding="utf-8")
        )
        assert spelling not in redescribed["columns"][0]["missing_by_source"], (
            "the case must still reach the hand-over: the twin's own "
            "values keep this spelling as a value",
            seed,
        )
        checked = folder / "check-twin"
        checked.mkdir()
        assert _quietly(
            [
                "validate", str(tmp_path / "real-profile.json"), "--twin",
                str(twin), "--out-dir", str(checked), "--replace",
            ]
        ) == 0, seed


# ------------------------------------------------------ a table sorted by it


def test_a_table_sorted_by_a_column_with_stand_ins_keeps_its_order(
    tmp_path: pathlib.Path,
) -> None:
    """FD7 counts a judged key's cells as written, not empty.

    Twelve `-999` rows lead a table sorted by its readings. While the
    twin wrote those cells blank, the sort column had absent cells
    written empty outside the records holding nothing, so the order was
    not published and the twin's rows came back unsorted. They are
    written as the table wrote them now, the order is published, and the
    twin leads with the same twelve `-999` rows.
    """
    draw = random.Random(3)
    values = sorted(draw.randint(1, 400) for _each in range(388))
    lines = [f"-999,{draw.choice(['a', 'b'])}" for _each in range(12)]
    lines += [f"{value},{draw.choice(['a', 'b'])}" for value in values]
    table = fixtures.write(
        tmp_path, "real.csv", "reading,site\n" + "\n".join(lines) + "\n"
    )
    for floor in FLOORS:
        folder = tmp_path / f"floor-{floor}"
        folder.mkdir()
        assert _quietly(
            [
                "profile", str(table), "--out-dir", str(folder), "--replace",
                "--smallest-group", str(floor),
            ]
        ) == 0
        document = json.loads(
            (folder / "real-profile.json").read_text(encoding="utf-8")
        )
        order = document["source"]["dialect"]["row_order"]
        assert order is not None and order["column"] == 1, order
        assert _quietly(
            [
                "generate", str(folder / "real-profile.json"), "--out-dir",
                str(folder), "--seed", "4", "--replace",
            ]
        ) == 0
        twin = folder / "real-twin.csv"
        cells = [row[0] for row in csv.reader(io.StringIO(twin.read_text()))][1:]
        assert cells[:12] == ["-999"] * 12
        numbers = [int(cell) for cell in cells[12:]]
        assert numbers == sorted(numbers)
        for side, checked in (("twin", twin), ("real", table)):
            out = folder / f"check-{side}"
            out.mkdir()
            assert _quietly(
                [
                    "validate", str(folder / "real-profile.json"), "--twin",
                    str(checked), "--out-dir", str(out), "--replace",
                ]
            ) == 0, (side, floor)


# ------------------------------------ the producer's side of the hand-over


def _described(
    cells: "list[str]", judged: "tuple[str, ...]" = ()
) -> "taxonomy.ColumnProfile":
    return taxonomy.profile_column(
        "value",
        1,
        cells,
        len(cells),
        taxonomy.Settings(),
        judged_candidates=judged,
    )


def _verdict_of(described: "taxonomy.ColumnProfile") -> "list[object]":
    return [entry["verdict"] for entry in described.sentinel_verdicts]


@pytest.mark.parametrize(
    "cells,candidate,spelling",
    [
        # A stand-in number INSIDE the column's spread: asked again, the
        # rule keeps it as a number.
        (
            [str(-1200 + 10 * index) for index in range(200)] + ["-999"] * 12,
            "-999",
            "-999",
        ),
        # A placeholder day INSIDE the column's spread of dates.
        (
            [
                (datetime.date(1899, 6, 1) + datetime.timedelta(days=3 * index))
                .isoformat()
                for index in range(200)
            ]
            + ["1900-01-01"] * 12,
            "1900-01-01",
            "1900-01-01",
        ),
        # A stand-in core inside an affixed column's spread of cores.
        (
            [f"{-1200 + 10 * index} mg" for index in range(200)]
            + ["-999 mg"] * 12,
            "-999",
            "-999 mg",
        ),
    ],
)
def test_a_candidate_the_description_judged_is_read_as_missing(
    cells: "list[str]", candidate: str, spelling: str
) -> None:
    """Each of the three judged passes honours the description's verdict.

    Every column here holds its candidate INSIDE the spread of its other
    values, so the outlier rule asked on its own keeps the candidate as
    a value. Handed the description's verdict -- which only the
    validator does -- the producer reads the twelve cells as missing
    under their own spelling, whatever the arithmetic says. This is
    what pins each branch: the numeric pass, the placeholder pass and
    the pass over an affixed column's cores.
    """
    alone = _described(cells)
    assert contract.VERDICT_MISSING not in _verdict_of(alone)
    assert spelling not in alone.missing_by_source
    handed = _described(cells, (candidate,))
    assert _verdict_of(handed) == [contract.VERDICT_MISSING]
    assert handed.missing_by_source == {spelling: 12}
    assert handed.n_present == alone.n_present - 12


def test_a_kept_value_still_wins_over_the_hand_over() -> None:
    """C6-117: a `--keep-value` is data, whatever a verdict says."""
    cells = [str(-1200 + 10 * index) for index in range(200)] + ["-999"] * 12
    kept = taxonomy.profile_column(
        "value",
        1,
        cells,
        len(cells),
        taxonomy.Settings(kept_values=("-999",)),
        judged_candidates=("-999",),
    )
    assert contract.VERDICT_MISSING not in _verdict_of(kept)
    assert "-999" not in kept.missing_by_source


def test_the_report_s_window_counts_no_stand_in_as_a_spelling(
    tmp_path: pathlib.Path,
) -> None:
    """The twin's report and the validator draw one window.

    The report's envelope for a column of numbers counts the spellings
    the column's own cells can supply, and it asked every non-blank cell
    -- so once the twin wrote its thirteen judged `-999` cells back, the
    report printed `reading`'s window as 178 to 179 while the validator,
    over the same twin, drew 178 to 178. A cell wearing a published hole
    spelling is no value and supplies no spelling.
    """
    table = fixtures.write(
        tmp_path, "t.csv", fixtures.every_role_and_joined_table()
    )
    document = profile.build_document(
        reading.read_table(str(table)),
        taxonomy.Settings(small_cell_floor=11),
        ["record_code"],
        [],
        [fixtures.JOINED_COLUMN],
    )
    loaded = contract.load_profile(
        str(fixtures.write_profile(tmp_path, "p.json", document))
    )
    twin = generation.generate(loaded, 20260811)
    windows = [
        (found.lowest, found.highest)
        for found in twin.approximations
        if found.column == "reading"
        and found.fact in ("n_distinct", "n_distinct_folded")
    ]
    column = [one for one in loaded.columns if one.name == "reading"][0]
    assert windows == [(f"{column.n_distinct}", f"{column.n_distinct}")] * 2, (
        windows
    )


def test_the_report_s_count_line_counts_cells_with_no_value(
    tmp_path: pathlib.Path,
) -> None:
    """The column block's first count names what the twin's cells are.

    It said the twin "leaves 13 cell(s) empty" for `reading`, whose twin
    column holds thirteen `-999` cells and no blank, while the same block
    said a few lines later that the twin writes every one of them the
    way the table did. The count is every absent cell of the twin, blank
    or wearing a published hole spelling, and the line now calls them
    cells with no value; for every column of the every-role twin it is
    recounted here from the written file.
    """
    table = fixtures.write(
        tmp_path, "t.csv", fixtures.every_role_and_joined_table()
    )
    document = profile.build_document(
        reading.read_table(str(table)),
        taxonomy.Settings(small_cell_floor=11),
        ["record_code"],
        [],
        [fixtures.JOINED_COLUMN],
    )
    loaded = contract.load_profile(
        str(fixtures.write_profile(tmp_path, "p.json", document))
    )
    twin = generation.generate(loaded, 20260811)
    text = parsing.visible_lines(rendering.report(loaded, twin))
    for place in range(len(loaded.columns)):
        column = loaded.columns[place]
        holes = set(column.missing_by_source)
        cells = twin.columns[place]
        absent = len([cell for cell in cells if cell == "" or cell in holes])
        assert (
            f"The twin holds {len(cells) - absent} value(s) and {absent} "
            f"cell(s) with no value"
        ) in text, column.name
    block = [one for one in loaded.columns if one.name == "reading"][0]
    written = twin.columns[loaded.columns.index(block)]
    assert written.count("") == 0 and written.count("-999") == 13
    assert "cell(s) empty, counted" not in text
