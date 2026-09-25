"""A free-text form holding a COMMA is written like every other mark.

The final review of 2026-09-18 measured a 2,000-row free-text column of
a letter, three figures, one mark, two figures and a letter, once per
mark. With `.`, `/`, `:`, `-`, `_` and `#` the column published
`shape_forms {"@%%%<mark>%%@": 2000}` and its twin wrote `L338.78Y`,
`L338/78Y` and so on, meeting the census exactly at exit 0. With `,` the
same column published the same census and its twin wrote `?!!!!!"%`,
`|!!!!!!.` and `>!!!!!!B` -- not one of the 2,000 cells wearing the
published form -- and `synthtwin validate` exited 3 on the twin while the
real table exited 0. On a European export the whole amount column went
the same way: `shape_forms {"%%%,%%": 942, "%%,%%": 20, "%%.%%%,%%": 22,
"%.%%%,%%": 1016}` covering all 2,000 cells, every one MISSED.

THE CAUSE was `generation._is_a_usable_stand_in`, which refused any
made-up spelling carrying a comma. It is the same false rule landing
2b.2 removed from the thousands separator, whose docstring already says
so in terms: `rendering.twin_csv` quotes a cell holding a comma, and
this package's own reader reads it back unchanged. `parsing.SHAPE_MARKS`
holds the comma, so `parsing.census_form` published a form no walk could
ever write.

THE RED CHECK: restoring the refusal (`character == ","` beside the
quote) turns `test_a_comma_form_is_met_like_every_other_mark[,]` red at
both seeds, and `test_every_shape_mark_is_writable` with it.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import csv
import io
import pathlib
import random

import pytest

from synthtwin import generation, parsing
from tests import fixtures
from tests.test_stage2_round_trip import _exit_of

ROWS = 2000


def _round_trip(
    folder: pathlib.Path, mark: str, seed: str
) -> "tuple[dict, list[str], int, int]":
    """Describe, build and validate a column of one mark; hand it all back."""
    folder.mkdir(parents=True, exist_ok=True)
    rng = random.Random(11)
    values = []
    for _index in range(ROWS):
        letter = "ABCD"[rng.randrange(4)]
        tail = "ZYXW"[rng.randrange(4)]
        values += [
            f"{letter}{100 + rng.randrange(900)}{mark}"
            f"{10 + rng.randrange(90)}{tail}"
        ]
    rows = [[f"R{index:05d}", values[index]] for index in range(ROWS)]
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["id", "value"], rows),
        encoding="utf-8", newline="",
    )
    assert _exit_of(
        ["profile", f"{table}", "--out-dir", f"{folder}", "--replace"]
    ) == 0
    described = folder / "real-profile.json"
    import json

    document = json.loads(described.read_text("utf-8"))
    block = [
        column for column in document["columns"] if column["name"] == "value"
    ][0]
    assert _exit_of(
        ["generate", f"{described}", "--out-dir", f"{folder}", "--seed", seed,
         "--replace"]
    ) == 0
    twin = folder / "real-twin.csv"
    written = list(csv.reader(io.StringIO(twin.read_text("utf-8"))))
    place = written[0].index("value")
    cells = [row[place] for row in written[1:]]
    exits = []
    for side, target in (("twin", twin), ("real", table)):
        checked = folder / side
        checked.mkdir()
        exits += [
            _exit_of(
                ["validate", f"{described}", "--twin", f"{target}",
                 "--out-dir", f"{checked}", "--replace"]
            )
        ]
    return block, cells, exits[0], exits[1]


@pytest.mark.parametrize(
    "mark,seed",
    [(",", "4"), (",", "11"), (".", "4"), ("-", "4"), ("/", "4"),
     (":", "4"), ("_", "4"), ("#", "4")],
)
def test_a_comma_form_is_met_like_every_other_mark(
    tmp_path: pathlib.Path, mark: str, seed: str
) -> None:
    """Seven marks, one column, one census, one answer.

    The comma stands beside the six marks that always worked -- and at
    two seeds, because it is the one that was broken: each publishes one
    form over all 2,000 cells, each twin wears it on all 2,000, and both
    files validate.
    """
    block, cells, twin_exit, real_exit = _round_trip(tmp_path, mark, seed)
    form = f"@%%%{mark}%%@"
    assert block["shape_forms"] == {form: ROWS}
    worn = len([cell for cell in cells if parsing.shape_form(cell) == form])
    assert worn == ROWS, cells[:3]
    assert (twin_exit, real_exit) == (0, 0)


def test_every_shape_mark_is_writable() -> None:
    """No mark of the census vocabulary is one no stand-in may carry.

    Asked of the rule itself, because the defect was exactly a mark the
    census could NAME and the walk could never WRITE.
    """
    for mark in parsing.SHAPE_MARKS:
        candidate = f"A123{mark}45z"
        assert generation._is_a_usable_stand_in(candidate), mark


def test_a_quote_is_still_refused() -> None:
    """The one refusal that stands, and the two that always did."""
    assert not generation._is_a_usable_stand_in('A12"3')
    assert not generation._is_a_usable_stand_in("=A123")
    assert not generation._is_a_usable_stand_in("")


# ------------------------------- the European export the review found it on


def _german_amounts(rows: int = 600) -> "list[str]":
    """Amounts written the German way: point for thousands, comma for tenths."""
    rng = random.Random(29)
    made = []
    for index in range(rows):
        whole = rng.randrange(10, 9999)
        cents = rng.randrange(100)
        if whole >= 1000:
            made += [f"{whole // 1000}.{whole % 1000:03d},{cents:02d}"]
        else:
            made += [f"{whole},{cents:02d}"]
    return made


@pytest.mark.parametrize("seed", ["4", "11"])
def test_an_undeclared_german_amount_column_is_written(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """The column the review found the defect on, and its second cause.

    An undeclared German amount column is FREE TEXT -- nothing declares
    the decimal comma, so no cell of it reads as a number -- and every
    filling of its published form is a number under the OTHER grammar.
    The stand-in rule asked that question of every column, declared or
    not, so every candidate was refused and the twin wrote wide-band
    cells against a census covering all its cells. The question is the
    column's own grammar now, and the twin writes amounts.
    """
    import json

    folder = tmp_path
    folder.mkdir(parents=True, exist_ok=True)
    amounts = _german_amounts()
    rows = [
        [f"K{index:06d}", amounts[index]] for index in range(len(amounts))
    ]
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["Kundennummer", "Betrag"], rows),
        encoding="utf-8", newline="",
    )
    assert _exit_of(
        ["profile", f"{table}", "--out-dir", f"{folder}", "--replace"]
    ) == 0
    described = folder / "real-profile.json"
    document = json.loads(described.read_text("utf-8"))
    block = [
        column for column in document["columns"] if column["name"] == "Betrag"
    ][0]
    assert block["role"] == "free_text"
    assert sum(block["shape_forms"].values()) == len(amounts)
    assert _exit_of(
        ["generate", f"{described}", "--out-dir", f"{folder}", "--seed", seed,
         "--replace"]
    ) == 0
    written = list(
        csv.reader(io.StringIO((folder / "real-twin.csv").read_text("utf-8")))
    )
    place = written[0].index("Betrag")
    cells = [row[place] for row in written[1:]]
    worn: "dict[str, int]" = {}
    for cell in cells:
        form = parsing.shape_form(cell)
        worn[form] = (worn[form] if form in worn else 0) + 1
    # EVERY NAMED FORM AT ITS COUNT, AND THE POOL AS MANY CELLS WEARING NO
    # NAMED FORM (plan P4-D316). At the default floor of 11 the nine
    # amounts under a hundred (`%%,%%`) are a form fewer than eleven
    # cells wear, pooled as `(withheld)`, and the twin writes that many
    # neutral stand-ins wearing no named form.
    published = dict(block["shape_forms"])
    pooled = published.pop("(withheld)", 0)
    for form, count in published.items():
        assert worn.get(form, 0) == count, (form, cells[:3])
    unnamed = sum(count for form, count in worn.items() if form not in published)
    assert unnamed == pooled, (worn, block["shape_forms"])
    for side, target in (("twin", folder / "real-twin.csv"), ("real", table)):
        checked = folder / side
        checked.mkdir()
        assert _exit_of(
            ["validate", f"{described}", "--twin", f"{target}", "--out-dir",
             f"{checked}", "--replace"]
        ) == 0, side
