"""Landing 2b.2's gate: every way a number is spelled survives.

WHAT THIS FILE PINS. Before this landing four spellings of a number were
lost with NO ERROR RAISED, each measured on the triage of 2026-09-15:

1. A number grouped with a space, an apostrophe, the right single
   quotation mark, a no-break space or a narrow no-break space was read
   as FREE TEXT: 24 of 24 runs of a 600-row charge column published no
   number at all and the twin wrote stand-ins such as `0271.5`.
2. An accounting negative `(1,234.56)` came back `-1,234.56`, and the
   REAL table failed its own description (`styles.spelled` MISSED).
3. A plus on a decimal, `+12.5`, was dropped: 224 of 500 cells in the
   real column, none in the twin, and both validations passed.
4. A trailing minus `1,483.65-` and the minus sign `−6.09` were
   affixed numbers whose negatives were published as positive
   magnitudes: `n_negative` 0 on a column of 217 negatives.

And one gap in the quality report: a bare copy of a comma-grouped twin
validated with exit 0, because the mark was a listing and not a check.

THE GATE IS LITERAL. Each shape is described, built, and the TWIN IS
DESCRIBED AGAIN under the same declarations; the published spelling
facts must come back, the twin's cells must carry them, and both the
twin and the real table must validate with exit code 0, over several
seeds and at the sizes a person's table has.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import csv
import io
import json
import pathlib
import random
import sys

import pytest

from tests import fixtures
from tests.test_stage2_round_trip import _exit_of, _round_trip

FACTS = ("role", "group_separator", "negative_form", "decimal_plus", "n_negative")
SEEDS = (4, 11, 23)


def _charges(count: int, seed: int) -> "list[float]":
    """Costs as finance holds them: skewed, most below ten thousand."""
    draw = random.Random(seed)
    return [round(2.718281828 ** (6.9 + draw.gauss(0, 1.0)), 2) for _ in range(count)]


def _signed(count: int, seed: int, spread: float) -> "list[float]":
    """Amounts either side of nought, as a ledger of debits and credits holds them."""
    draw = random.Random(seed)
    return [round(draw.gauss(200, spread), 2) for _ in range(count)]


def _grouped(value: float, mark: str, decimals: int = 2) -> str:
    return f"{value:,.{decimals}f}".replace(",", mark)


def _shapes(seed: int) -> "dict[str, tuple[list[str], tuple[str, ...], dict[str, object]]]":
    """Name -> (cells, declarations, the facts the description must publish)."""
    draw = random.Random(seed * 7 + 1)
    whole = [draw.randint(18000, 160000) for _ in range(800)]
    ledger = _signed(600, seed, 1500)
    # Amounts either side of nought: about half of them negative, which is
    # what a notation needs to be published at all. SPREAD WIDE ON
    # PURPOSE: at a spread of 12 the same column written with an ordinary
    # minus already fails its own twin at 53bb012 -- `ladder.p90` at seed
    # 11, and one unrounded fraction missing the width census at seed 23
    # -- which are the percentile-rung and dense-decimal defects STATE
    # carries, not this landing's. At 300 all three seeds pass there.
    small_draw = random.Random(seed + 1)
    small_ledger = [round(small_draw.gauss(0, 300), 2) for _ in range(600)]
    # ONE generator drawn from six hundred times, so the changes differ.
    change_draw = random.Random(seed + 2)
    changes = [round(change_draw.gauss(0, 400), 2) for _ in range(600)]
    return {
        "charges grouped with a space": (
            [_grouped(value, " ") for value in _charges(600, seed)],
            (),
            {"group_separator": " "},
        ),
        "charges grouped with an apostrophe": (
            [_grouped(value, "'") for value in _charges(600, seed + 3)],
            (),
            {"group_separator": "'"},
        ),
        "salaries grouped with a right single quotation mark": (
            [f"{value:,}".replace(",", "’") for value in whole],
            (),
            {"group_separator": "’", "role": "count"},
        ),
        # The thin space U+2009, which the verification of this landing
        # measured still read as free text with nothing said.
        "salaries grouped with a thin space": (
            [f"{value:,}".replace(",", "\u2009") for value in whole],
            (),
            {"group_separator": "\u2009", "role": "count"},
        ),
        "charges grouped with a no-break space": (
            [_grouped(value, " ") for value in _charges(600, seed + 4)],
            (),
            {"group_separator": " "},
        ),
        "charges grouped with a narrow no-break space": (
            [_grouped(value, " ") for value in _charges(600, seed + 5)],
            (),
            {"group_separator": " "},
        ),
        "a declared decimal comma grouped with a space": (
            [_grouped(value, " ").replace(".", ",") for value in _charges(800, seed + 6)],
            ("--decimal-comma", "value"),
            {"group_separator": " "},
        ),
        "accounting brackets": (
            [
                f"({-value:,.2f})" if value < 0 else f"{value:,.2f}"
                for value in ledger
            ],
            (),
            {"group_separator": ",", "negative_form": "brackets"},
        ),
        "accounting brackets on whole numbers": (
            [
                f"({-round(value):,})" if round(value) < 0 else f"{round(value):,}"
                for value in ledger
            ],
            (),
            # A column holding negatives is not a count, so whole
            # numbers either side of nought are `continuous`.
            {"negative_form": "brackets", "role": "continuous"},
        ),
        "brackets inside a currency prefix": (
            [
                f"$({-value:,.2f})" if value < 0 else f"${value:,.2f}"
                for value in _signed(800, seed + 7, 4000)
            ],
            (),
            {"role": "affixed_number", "negative_form": "brackets"},
        ),
        "a trailing minus": (
            [
                f"{-value:,.2f}-" if value < 0 else f"{value:,.2f}"
                for value in ledger
            ],
            (),
            {"negative_form": "trailing_minus"},
        ),
        "the minus sign": (
            [
                f"−{-value:.2f}" if value < 0 else f"{value:.2f}"
                for value in small_ledger
            ],
            (),
            {"negative_form": "minus_sign", "group_separator": ""},
        ),
        "a plus on every rising change": (
            [f"+{value:.2f}" if value > 0 else f"{value:.2f}" for value in changes],
            (),
            {"negative_form": "minus"},
        ),
        "a declared decimal comma with brackets": (
            [
                (f"({-value:,.2f})" if value < 0 else f"{value:,.2f}")
                .replace(",", "_").replace(".", ",").replace("_", ".")
                for value in ledger
            ],
            ("--decimal-comma", "value"),
            {"group_separator": ".", "negative_form": "brackets"},
        ),
    }


def _shape_ids() -> "list[tuple[str, int]]":
    return [(name, seed) for name in sorted(_shapes(SEEDS[0])) for seed in SEEDS]


@pytest.mark.parametrize("shape,seed", _shape_ids())
def test_every_spelling_of_a_number_comes_back_from_the_twin(
    tmp_path: pathlib.Path, shape: str, seed: int
) -> None:
    """Described, built, described again: the spelling facts return and both files pass."""
    cells, flags, expected = _shapes(seed)[shape]
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "shape", cells, flags, True, seed=f"{seed}"
    )
    for key, value in expected.items():
        assert first.get(key) == value, (shape, seed, key, first.get(key))
    differ = {
        key: (first.get(key), second.get(key))
        for key in FACTS
        if first.get(key) != second.get(key)
    }
    assert differ == {}, (shape, seed, differ)
    assert twin_exit == 0, (shape, seed, "the twin missed an obligation")
    assert real_exit == 0, (shape, seed, "the real table missed its own description")
    # THE CELLS THEMSELVES, and not only the facts: a mark published on
    # both sides and written on no cell would agree while the defect stood.
    mark = expected.get("group_separator", "")
    if mark and mark != ".":
        assert any(mark in cell for cell in written), (shape, seed)
    notation = expected.get("negative_form", "minus")
    wearing = {
        "brackets": lambda cell: "(" in cell and ")" in cell,
        "trailing_minus": lambda cell: cell.endswith("-"),
        "minus_sign": lambda cell: "−" in cell,
        "minus": lambda cell: "-" in cell,
    }[notation]
    negatives = first["n_negative"]
    if negatives:
        assert sum(1 for cell in written if wearing(cell)) == negatives, (shape, seed)
        if notation != "minus":
            assert not any(cell.lstrip("$").startswith("-") for cell in written), (
                shape, seed
            )


@pytest.mark.parametrize("seed", SEEDS)
def test_a_plus_on_a_decimal_is_written_as_often_as_the_real_column_wrote_it(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """A plus on a third of the rising changes: the count comes back, not a majority."""
    draw = random.Random(seed)
    cells = []
    for _ in range(900):
        value = round(draw.gauss(0, 350), 2)
        signed = value > 0 and draw.random() < 0.35
        cells += [f"+{value:.2f}" if signed else f"{value:.2f}"]
    real = sum(1 for cell in cells if cell.startswith("+"))
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "plus", cells, (), True, seed=f"{seed}"
    )
    assert first["decimal_plus"] == {"+": real}
    assert second["decimal_plus"] == {"+": real}
    assert sum(1 for cell in written if cell.startswith("+")) == real
    assert (twin_exit, real_exit) == (0, 0)
    # ...AND SPREAD OVER THE VALUES, not taken from the smallest upward:
    # the plus cells' median sits inside the middle half of the positives.
    positives = sorted(float(cell) for cell in written if float(cell) >= 0)
    plussed = sorted(float(cell) for cell in written if cell.startswith("+"))
    middle = plussed[len(plussed) // 2]
    assert positives[len(positives) // 4] <= middle <= positives[3 * len(positives) // 4]


# -- the quality report holds the spellings -----------------------------


def _validate(folder: pathlib.Path, profile: pathlib.Path, file: pathlib.Path) -> "tuple[int, str]":
    checked = folder / f"check-{file.stem}"
    checked.mkdir()
    code = _exit_of(
        ["validate", str(profile), "--twin", str(file), "--out-dir", str(checked), "--replace"]
    )
    report = ""
    for path in sorted(checked.glob("*.txt")):
        report = report + path.read_text(encoding="utf-8")
    return code, report


def _rewritten(folder: pathlib.Path, twin: pathlib.Path, change: "dict[str, str]", name: str) -> pathlib.Path:
    rows = [row for row in csv.reader(io.StringIO(twin.read_text(encoding="utf-8")))]
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(rows[0])
    for row in rows[1:]:
        cell = row[0]
        for old, new in change.items():
            cell = cell.replace(old, new)
        writer.writerow([cell])
    path = folder / f"{name}.csv"
    path.write_text(out.getvalue(), encoding="utf-8", newline="")
    return path


@pytest.mark.parametrize(
    "shape,cells,flags,change,subcheck",
    [
        (
            "commas",
            [_grouped(value, ",") for value in _charges(600, 31)],
            (),
            {",": ""},
            "spelling.group_separator",
        ),
        (
            "spaces",
            [_grouped(value, " ") for value in _charges(600, 32)],
            (),
            {" ": ""},
            "spelling.group_separator",
        ),
        (
            "points on a declared decimal comma",
            [
                _grouped(value, "_").replace(".", ",").replace("_", ".")
                for value in _charges(600, 33)
            ],
            ("--decimal-comma", "value"),
            {".": ""},
            "spelling.group_separator",
        ),
        (
            "brackets",
            [
                f"({-value:.2f})" if value < 0 else f"{value:.2f}"
                for value in _signed(600, 34, 900)
            ],
            (),
            {"(": "-", ")": ""},
            "spelling.negative_form",
        ),
    ],
)
def test_a_copy_that_drops_the_spelling_is_missed(
    tmp_path: pathlib.Path,
    shape: str,
    cells: "list[str]",
    flags: "tuple[str, ...]",
    change: "dict[str, str]",
    subcheck: str,
) -> None:
    """The twin passes; the same twin with its spelling stripped misses the named check."""
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "held", cells, flags, True
    )
    assert (twin_exit, real_exit) == (0, 0)
    folder = tmp_path / "held"
    bare = _rewritten(folder, folder / "real-twin.csv", change, "bare")
    code, report = _validate(folder, folder / "real-profile.json", bare)
    assert code != 0, (shape, "a copy without the spelling passed")
    missed = [line for line in report.splitlines() if subcheck in line and "MISSED" in line]
    assert missed, (shape, subcheck)


def test_a_small_file_is_withheld_and_not_missed(tmp_path: pathlib.Path) -> None:
    """Too few four-figure numbers to show a mark at the group size: WITHHELD, exit 0."""
    # TWO READINGS AT ONE PLACE, so the column is on no single grid and plan
    # P4-D185's move across a thousand -- which would give the twin two
    # grouped cells, enough to show the mark -- does not reach it. It was
    # one until plan P4-D222 (stage 2 closed by the owner rulings of
    # 2026-09-17) counted a width one cell wrote into the commonest, which
    # put the column on one grid.
    cells = ["1,040.16", "1,091.80", "801.65", "766.75", "229.5",
             "540.78", "283.64", "180.77", "115.02", "222.4"]
    # DESCRIBED BY THE PRODUCER (plan P4-D341): TEN four-figure numbers
    # is the shape -- too few for the twin to show the mark at the group
    # size -- and a table at the population floor the command requires
    # has room to show it. The producer refuses no table for its size,
    # and the twin is still built and both files still checked by the
    # commands, which is where the WITHHELD verdict has to appear.
    first, second, _written, _twin_exit, real_exit = _round_trip(
        tmp_path / "small",
        cells,
        ("--smallest-group", "2"),
        True,
        by_command=False,
    )
    assert first["group_separator"] == ","
    assert real_exit == 0
    folder = tmp_path / "small"
    bare = _rewritten(folder, folder / "real-twin.csv", {",": ""}, "bare")
    code, report = _validate(folder, folder / "real-profile.json", bare)
    held = [line for line in report.splitlines() if "spelling.group_separator" in line]
    assert held and all("MISSED" not in line for line in held), held
    assert any("WITHHELD" in line for line in held), held
    assert code == 0


@pytest.mark.parametrize(
    "shape,cells,flags",
    [
        # A padded cell holding a mark withholds it from the column.
        (
            "a padded cell holding a comma",
            [_grouped(value, ",") for value in _charges(400, 41)] + ["01,234,000"] * 3,
            (),
        ),
        # Each wrapper of a set proves its own mark over its own cores.
        (
            "two currencies, each grouped",
            [
                (f"${value:,.2f}" if place % 3 else f"£{value:,.2f}".replace(",", " "))
                for place, value in enumerate(_charges(900, 42))
            ],
            (),
        ),
        # The numeric half of a column with labels proves its mark over its own cells.
        (
            "numbers grouped with a space beside labels",
            [_grouped(value, " ") for value in _charges(500, 43)]
            + ["not measured"] * 40
            + ["pending review"] * 40,
            (),
        ),
        # A declared decimal comma is read in its own grammar before any recount.
        (
            "a declared decimal comma beside an absent spelling",
            [
                _grouped(value, "_").replace(".", ",").replace("_", ".")
                for value in _charges(400, 44)
            ]
            + ["-999,000"] * 12,
            ("--decimal-comma", "value", "--missing-value", "-999"),
        ),
    ],
)
def test_the_real_table_meets_every_spelling_check_at_every_edge(
    tmp_path: pathlib.Path, shape: str, cells: "list[str]", flags: "tuple[str, ...]"
) -> None:
    """Every edge of the producer's rule reaches the check, so the real table passes."""
    _first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "edge", cells, flags, True
    )
    assert real_exit == 0, shape
    assert twin_exit == 0, shape


# -- what stays text, and what is asked ---------------------------------


@pytest.mark.parametrize(
    "shape,cells",
    [
        ("postcodes 123 45", [f"{random.Random(place).randint(100, 999)} {place % 90 + 10}" for place in range(600)]),
        (
            "telephone numbers 01 23 45 67 89",
            [" ".join(f"{(place * 7 + step * 13) % 100:02d}" for step in range(5)) for place in range(600)],
        ),
        ("the Indian grouping 12,34,567", [f"{place % 90 + 10},{place % 89 + 10:02d},{place % 900 + 100}" for place in range(600)]),
        ("two marks in one cell 1,234 567", [f"{place % 900 + 100},{place % 900 + 100} {place % 900 + 100}" for place in range(600)]),
    ],
)
def test_a_spelling_that_is_not_a_grouped_number_stays_text(
    tmp_path: pathlib.Path, shape: str, cells: "list[str]"
) -> None:
    """Groups of three, one mark: a postcode, a telephone number, lakh and mixed marks are refused."""
    from synthtwin import parsing

    for cell in cells[:50]:
        assert parsing.parse_number(cell) is None, (shape, cell)
    folder = tmp_path / "text"
    folder.mkdir()
    table = folder / "t.csv"
    table.write_text(fixtures.rows_to_csv(["v"], [[cell] for cell in cells]), encoding="utf-8", newline="")
    assert _exit_of(["profile", str(table), "--out-dir", str(folder), "--replace"]) == 0
    column = json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))["columns"][0]
    assert column["role"] not in ("count", "continuous"), (shape, column["role"])


def test_a_zero_led_group_reads_the_same_for_every_mark() -> None:
    """The comma always read `012,345` as 12345; every mark reads its zero-led group alike."""
    from synthtwin import parsing

    for mark in parsing.GROUP_MARKS:
        assert parsing.parse_number(f"012{mark}345") == 12345.0, mark
        assert parsing.numeric_style(f"012{mark}345") == parsing.STYLE_LEADING_ZERO, mark


def _questions(folder: pathlib.Path, cells: "list[str]", *flags: str) -> "dict[str, object]":
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "t.csv"
    table.write_text(fixtures.rows_to_csv(["v"], [[cell] for cell in cells]), encoding="utf-8", newline="")
    assert _exit_of(["profile", str(table), "--out-dir", str(folder), "--replace", *flags]) == 0
    loaded: "dict[str, object]" = json.loads((folder / "t-questions.json").read_text(encoding="utf-8"))
    return loaded


def test_an_identifier_grouped_with_spaces_is_asked_about(tmp_path: pathlib.Path) -> None:
    """`123 456 789` reads as a number since this landing, so its column is asked about."""
    draw = random.Random(5)
    cells = [f"{draw.randint(100, 999)} {draw.randint(100, 999)} {draw.randint(100, 999)}" for _ in range(600)]
    asked = _questions(tmp_path / "ids", cells)["asked"]
    assert isinstance(asked, list) and len(asked) == 1
    entry = asked[0]
    assert "grouped in threes" in entry["what_synthtwin_saw"]
    assert "9 figures" in entry["what_synthtwin_saw"]
    answers = [choice["answer"] for choice in entry["answers_you_can_give"]]
    assert "identifier" in answers and "code" in answers


def test_whole_numbers_with_a_point_between_thousands_are_asked_about(tmp_path: pathlib.Path) -> None:
    """`12.345` is read as twelve and a bit, and the person is asked, with --decimal-comma offered."""
    draw = random.Random(6)
    cells = [f"{draw.randint(1000, 99999):,}".replace(",", ".") for _ in range(800)]
    folder = tmp_path / "points"
    document = _questions(folder, cells)
    asked = document["asked"]
    assert isinstance(asked, list) and len(asked) == 1
    entry = asked[0]
    assert entry["read_as_now"] == "measurement"
    answers = [choice["answer"] for choice in entry["answers_you_can_give"]]
    assert answers[:2] == ["measurement", "decimal_comma"]
    column = json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))["columns"][0]
    assert column["role"] == "continuous"
    assert column["percentiles"]["max"] < 100
    # ANSWERED IN THE FILE, the column is read with a point between thousands.
    entry["your_answer"] = "decimal_comma"
    answers_path = folder / "answered.json"
    # The line ending is fixed rather than left to the platform, so the
    # bytes are the same on every one (tests/test_description_line_endings).
    answers_path.write_text(
        json.dumps(document), encoding="utf-8", newline="\n"
    )
    again = tmp_path / "answered"
    again.mkdir()
    table = folder / "t.csv"
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(again), "--replace", "--answers", str(answers_path)]
    ) == 0
    described = json.loads((again / "t-profile.json").read_text(encoding="utf-8"))
    assert described["settings"]["forced_decimal_commas"] == ["v"]
    column = described["columns"][0]
    assert column["group_separator"] == "."
    assert column["percentiles"]["max"] > 1000


def test_proportions_with_three_decimals_are_not_asked_about(tmp_path: pathlib.Path) -> None:
    """A thousands group never begins `0.`, so a column of `0.125` raises no question."""
    draw = random.Random(7)
    cells = [f"0.{draw.randint(100, 999)}" for _ in range(400)]
    assert _questions(tmp_path / "proportions", cells)["asked"] == []


def test_brackets_around_a_currency_are_named_not_read(tmp_path: pathlib.Path) -> None:
    """`($1,234.56)` keeps its spelling and the description says what its numbers are."""
    from synthtwin import taxonomy

    cells = [
        f"(${-value:,.2f})" if value < 0 else f"${value:,.2f}"
        for value in _signed(800, 51, 1500)
    ]
    first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "outer", cells, (), True
    )
    assert first["role"] == "affixed_number"
    said = taxonomy.rendered(taxonomy.REMARK_BRACKETS_AROUND_THE_AFFIX, ())
    assert said in first["remarks"]
    assert any(cell.startswith("($") and cell.endswith(")") for cell in written)
    assert (twin_exit, real_exit) == (0, 0)


# -- what the verification of this landing found --------------------------


@pytest.mark.parametrize("seed", (5, 8, 13))
def test_a_plus_on_decimals_beside_signed_whole_numbers_comes_back(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """Changes written `+12` and `+3.25`: the signed decimals are all written.

    Measured before the repair on these three seeds: the twin wrote 210,
    210 and 221 signed decimals where the real column wrote 213, 227 and
    228, and `spelling.decimal_plus` was MISSED, because the style walk
    put `plain` on small positive values that the plus needed.
    """
    draw = random.Random(seed)
    cells: "list[str]" = []
    for _ in range(900):
        if draw.random() < 0.5:
            cells += [f"{round(draw.gauss(0, 300)):+d}"]
        else:
            cells += [f"{round(draw.gauss(0, 300), 2):+.2f}"]
    real = sum(1 for cell in cells if cell.startswith("+") and "." in cell)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "changes", cells, (), True, seed=f"{seed}"
    )
    assert first["decimal_plus"] == {"+": real}
    assert second["decimal_plus"] == {"+": real}
    assert second["numeric_styles"] == first["numeric_styles"]
    assert second["fraction_widths"] == first["fraction_widths"]
    assert sum(1 for cell in written if cell.startswith("+") and "." in cell) == real
    assert (twin_exit, real_exit) == (0, 0)


@pytest.mark.parametrize("seed", (3, 8, 19))
def test_a_minus_after_whole_amounts_is_named_and_not_split_by_size(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """`1,234-` beside `500-`: both stay text, the column says so, both files pass.

    Before the repair a thousands mark let `1,234-` read as a negative
    number while `500-` stayed text, so the count of numbers depended on
    each value's size; at seed 3 the twin missed `n_numeric`.
    """
    from synthtwin import parsing, taxonomy

    assert parsing.parse_number("1,234-") is None
    assert parsing.parse_number("500-") is None
    assert parsing.parse_number("1,234.50-") == -1234.5
    draw = random.Random(seed)
    values = [round(draw.gauss(300, 3000)) for _ in range(800)]
    cells = [f"{-value:,}-" if value < 0 else f"{value:,}" for value in values]
    first, second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "ledger", cells, (), True, seed=f"{seed}"
    )
    assert first["role"] == "affixed_number"
    said = taxonomy.rendered(taxonomy.REMARK_MINUS_AFTER_THE_FIGURES, ())
    assert said in first["remarks"]
    # EVERY CELL WITH A MINUS AFTER IT IS TEXT, whatever its size.
    assert first["n_numeric"] == sum(1 for value in values if value >= 0)
    assert second["n_numeric"] == first["n_numeric"]
    assert (twin_exit, real_exit) == (0, 0)


@pytest.mark.parametrize("seed", (3, 8, 19))
def test_counts_with_a_point_between_thousands_are_asked_about_beside_small_ones(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """`523` beside `12.345`: the column is asked, and answering reads it right.

    Before the repair a third of such a column below a thousand silenced
    the question, and the description published a mean near 180 for a
    true mean in the thousands with nothing asked.
    """
    draw = random.Random(seed)
    values = [int(draw.lognormvariate(7.5, 1.3)) for _ in range(900)]
    assert sum(1 for value in values if value < 1000) > 200
    cells = [f"{value:,}".replace(",", ".") for value in values]
    folder = tmp_path / "counts"
    document = _questions(folder, cells)
    asked = document["asked"]
    assert isinstance(asked, list) and len(asked) == 1
    entry = asked[0]
    assert "below a thousand" in entry["what_synthtwin_saw"]
    assert [choice["answer"] for choice in entry["answers_you_can_give"]][:2] == [
        "measurement",
        "decimal_comma",
    ]
    entry["your_answer"] = "decimal_comma"
    answers_path = folder / "answered.json"
    # The line ending is fixed rather than left to the platform, so the
    # bytes are the same on every one (tests/test_description_line_endings).
    answers_path.write_text(
        json.dumps(document), encoding="utf-8", newline="\n"
    )
    again = tmp_path / "answered"
    again.mkdir()
    assert _exit_of(
        ["profile", str(folder / "t.csv"), "--out-dir", str(again), "--replace", "--answers", str(answers_path)]
    ) == 0
    column = json.loads((again / "t-profile.json").read_text(encoding="utf-8"))["columns"][0]
    assert column["role"] == "count"
    assert column["group_separator"] == "."
    assert column["mean"] == pytest.approx(sum(values) / len(values), rel=1e-12)
    # ...AND ANSWERED ONCE, NEVER ASKED AGAIN: declared, the column raises nothing.
    assert _questions(tmp_path / "declared", cells, "--decimal-comma", "v")["asked"] == []


_POINT_THOUSANDS = [f"1.{k:03d}" for k in range(200, 800)]


@pytest.mark.parametrize(
    "cells",
    [
        ["+" + cell for cell in _POINT_THOUSANDS],
        ["−" + cell for cell in _POINT_THOUSANDS],
        ["(" + cell + ")" for cell in _POINT_THOUSANDS],
        [cell + "-" for cell in _POINT_THOUSANDS],
        _POINT_THOUSANDS[:300] + ["+" + _POINT_THOUSANDS[300]] + _POINT_THOUSANDS[301:],
        _POINT_THOUSANDS[:300] + [" " + _POINT_THOUSANDS[300] + " "] + _POINT_THOUSANDS[301:],
    ],
    ids=["all plus", "all minus sign", "all brackets", "all trailing minus", "one plus", "one padded"],
)
def test_a_sign_or_a_padded_cell_does_not_silence_the_point_between_thousands(
    tmp_path: pathlib.Path, cells: "list[str]"
) -> None:
    """The integration verdict: the unsigned column was asked and none of these was.

    A sign or outer spaces say nothing about whether the point groups
    thousands, and each variant published a mean of 1.4995 for a column
    counted in thousands with nothing asked.
    """
    asked = _questions(tmp_path / "signed", cells)["asked"]
    assert isinstance(asked, list) and len(asked) == 1
    assert "below a thousand" in asked[0]["what_synthtwin_saw"]


@pytest.mark.parametrize(
    "extra",
    [["12.5"], ["1234"], ["0.125"], ["012"]],
    ids=["a point with one figure after it", "four figures and no point", "a proportion", "a padded small number"],
)
def test_a_value_the_point_reading_cannot_explain_keeps_the_column_unasked(
    tmp_path: pathlib.Path, extra: "list[str]"
) -> None:
    """One value written another way settles the reading, so nothing is asked about the point."""
    draw = random.Random(9)
    cells = [f"{int(draw.lognormvariate(7.5, 1.3)):,}".replace(",", ".") for _ in range(400)] + extra
    asked = _questions(tmp_path / "settled", cells)["asked"]
    assert isinstance(asked, list)
    assert all("below a thousand" not in entry["what_synthtwin_saw"] for entry in asked)


@pytest.mark.parametrize("seed", (1, 2, 3))
def test_a_rounded_negative_zero_in_a_real_ledger_meets_its_own_description(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """`(0)` and `-0` are how a ledger writes -0.3 rounded; the real table passes."""
    draw = random.Random(seed)
    values = [round(draw.gauss(0, 3000), 2) for _ in range(800)] + [-0.3, -0.2, 0.4] * 4
    for notation in ("brackets", "minus"):
        cells = [
            (f"({-value:,.0f})" if notation == "brackets" else f"-{-value:,.0f}")
            if value < 0
            else f"{value:,.0f}"
            for value in values
        ]
        assert "(0)" in cells or "-0" in cells
        _first, _second, _written, _twin_exit, real_exit = _round_trip(
            tmp_path / notation, cells, (), True, seed=f"{seed}"
        )
        assert real_exit == 0, (notation, seed)


@pytest.mark.parametrize("plus", ("+", ""), ids=["with plus", "without plus"])
def test_a_change_rounded_to_minus_nought_at_two_places_meets_its_own_description(
    tmp_path: pathlib.Path, plus: str
) -> None:
    """`-0.00` is how a change column writes -0.003 rounded to two places.

    The integration verdict: the whole-number `-0` passed, and a real
    column of signed or unsigned two-place changes holding one `-0.00`
    exited 3 on `styles.spelled`, because the unsigned cell was offered
    against spellings of -0.0, which a decimal style writes with its minus.
    """
    cells = (
        [f"{plus}1.25"] * 60 + ["-2.50"] * 60 + ["-0.00"] + [f"{plus}0.75"] * 40
    )
    _first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "change", cells, ("--measurement", "value"), True, seed="1"
    )
    assert real_exit == 0
    assert twin_exit == 0


@pytest.mark.parametrize("seed", ("4", "11"))
def test_padded_whole_numbers_beside_signed_decimals_keep_every_plus(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """`-001` beside `+2.00` and `+3.00`: all hundred pluses come back.

    The integration verdict: the style walk put `decimal` on the negatives
    and `leading_zero` on the positives, only `plain` cells were exchanged,
    and the twin wrote `-1.00`, `002` and `003` with no plus at all.
    """
    cells = ["-001"] * 100 + ["+2.00"] * 50 + ["+3.00"] * 50
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "padded", cells, ("--measurement", "value"), True, seed=seed
    )
    assert first["decimal_plus"] == {"+": 100}
    assert sum(1 for cell in written if cell[:1] == "+") == 100
    assert second["decimal_plus"] == first["decimal_plus"]
    assert (twin_exit, real_exit) == (0, 0)


@pytest.mark.parametrize("seed", ("4", "11"))
def test_a_plus_is_written_on_whole_values_so_no_spelling_is_invented(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """Three values written fifty times each, one with a plus: three spellings, not six.

    The integration verdict: the spread rule put pluses cell by cell, so
    one value came back both as `+100.25` and `100.25`, the twin held six
    spellings against three, and 900 signed changes 780 against 690, with
    every check passing.
    """
    cells = ["+100.25"] * 50 + ["200.25"] * 50 + ["300.25"] * 50
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "three", cells, ("--measurement", "value"), True, seed=seed
    )
    assert first["decimal_plus"] == {"+": 50}
    assert sum(1 for cell in written if cell[:1] == "+") == 50
    assert len(set(written)) == 3
    assert (twin_exit, real_exit) == (0, 0)
    draw = random.Random(3)
    changes = [
        f"{round(draw.gauss(0, 3), 2):+.2f}" if draw.random() < 0.5 else f"{round(draw.gauss(0, 3), 2):.2f}"
        for _ in range(900)
    ]
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "changes", changes, ("--measurement", "value"), True, seed=seed
    )
    assert second["n_distinct"] == first["n_distinct"]
    assert second["decimal_plus"] == first["decimal_plus"]
    assert (twin_exit, real_exit) == (0, 0)


def test_this_file_is_run_by_the_suite_it_belongs_to() -> None:
    """Every call here reads what the command returned (the stage 2 rule)."""
    assert sys.modules[__name__].__doc__
