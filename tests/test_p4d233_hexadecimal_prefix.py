"""A hexadecimal column's literal prefix (plan P4-D233).

THE LIMIT P4-D202 PUT TO THE OWNER, closed. The owner's ruling of
2026-09-17, item 1, publishes the literal text every present cell of a
declared identifier opens with, and its twin writes it, so that a
starts-with test written against the twin selects the rows it selects
on the table. `parsing.literal_prefix` answered "" for any column whose
layout convention is not plain, and the loader refused a prefix beside
a hexadecimal census outright, so 800 cells of `DE-` and six
hexadecimal figures published `{}` and their twin wrote `d2-cfc8af`:
`DE-[0-9a-f]{6}` matched 800 real cells and 0 twin cells.

THE RULE IS THE SAME RULE. The four cuts of contract C6-139 stand, with
cut (3) -- no half a run of letters -- asked of the column's OWN
figures, which in a hexadecimal column is every letter of it. So a
hexadecimal prefix always ends in a mark, and `ab12` beside `ab34`
still publishes nothing.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import pathlib
import random
import re

import pytest

from synthtwin import contract
from synthtwin import errors
from synthtwin import parsing
from tests import fixtures
from tests.test_landing_2b18_identifier_layout import _round_trip

ROWS = 800


def _hex_tail(seed: int, prefix: str = "DE-", case: str = "x") -> "list[str]":
    """``ROWS`` cells of one prefix before six hexadecimal figures."""
    draw = random.Random(seed)
    pattern = "%06" + case
    return [prefix + (pattern % draw.randrange(0, 1 << 24)) for _row in range(ROWS)]


def _opening(values: "list[str]", prefix: str) -> int:
    return len([value for value in values if value[: len(prefix)] == prefix])


def _matching(values: "list[str]", pattern: str) -> int:
    rule = re.compile(pattern)
    return len([value for value in values if rule.fullmatch(value)])


# ------------------------------------------------------- the ruling's case


# BOTH FLOORS, NAMED (the repair pass of landing 3.1): this read
# `[None, 11]` when None meant a floor of one, and ran eleven twice once
# the default became 11 (plan P4-D316). One is asked for by name; None
# is the shipped default.
@pytest.mark.parametrize("floor", [1, None])
def test_a_hexadecimal_column_publishes_and_writes_its_prefix(
    floor: "int | None", tmp_path: pathlib.Path
) -> None:
    """The measured shape, as a round trip (plan P4-D233).

    Mutation: with `parsing.literal_prefix` barring a column whose
    convention is not plain, the prefix is `{}` and no twin cell opens
    with `DE-`.
    """
    cells = _hex_tail(5)
    got = _round_trip(tmp_path / f"hex-{floor}", cells, floor=floor)
    assert got["source"]["layout_forms"] == {"~~-~~~~~~": ROWS}
    assert got["source"]["layout_prefixes"] == {"(column)": "DE-"}
    # THE TWIN SAYS THE SAME THING BACK, which is what makes the prefix a
    # fact of the column rather than an accident of one description.
    assert got["twin_profile"]["layout_prefixes"] == {"(column)": "DE-"}
    assert got["twin_profile"]["layout_forms"] == got["source"]["layout_forms"]
    assert got["twin_exit"] == 0 and got["real_exit"] == 0
    twin = got["cells"]
    # ...and the whole point of the ruling, measured on both files.
    assert _opening(twin, "DE-") == _opening(cells, "DE-") == ROWS
    assert _matching(twin, r"DE-[0-9a-f]{6}") == ROWS
    assert _matching(cells, r"DE-[0-9a-f]{6}") == ROWS
    # ...and the made-up values stay as different as the table's.
    assert len(set(twin)) == len(set(cells))


def test_an_upper_case_hexadecimal_column_keeps_its_own_mark(
    tmp_path: pathlib.Path,
) -> None:
    """The other convention, so the mark is read and not assumed.

    A column of `CAFE-` and six upper-case hexadecimal figures wears
    `^` where the lower-case one wears `~`, and its prefix's own layout
    is `@@@@-` under a plain reading and `^^^^-` under this one. LP2
    asks the census's own marks, so a prefix marked by case would be
    refused by the loader as a document it could not have written.
    """
    cells = _hex_tail(9, "CAFE-", "X")
    got = _round_trip(tmp_path / "hex-upper", cells, floor=11)
    assert got["source"]["layout_forms"] == {"^^^^-^^^^^^": ROWS}
    assert got["source"]["layout_prefixes"] == {"(column)": "CAFE-"}
    assert got["twin_exit"] == 0 and got["real_exit"] == 0
    assert _opening(got["cells"], "CAFE-") == ROWS
    assert parsing.prefix_layout("CAFE-", parsing.LAYOUT_HEX_UPPER) == "^^^^-"
    assert parsing.prefix_layout("CAFE-", parsing.LAYOUT_PLAIN) == "@@@@-"


# ------------------------------------------------------------ the cut-back


def test_a_prefix_ending_in_a_hexadecimal_figure_is_cut_back() -> None:
    """Cut (3) asked of the column's own figures (contract C6-139).

    Every letter of a hexadecimal column is a figure of base sixteen, so
    an opening ending in one ends inside a number and is cut away. What
    survives always ends in a mark.

    Mutation: with the hexadecimal cut-back withdrawn, `ab12` beside
    `ab34` publishes `ab` -- half of every value's number.
    """
    lower = parsing.LAYOUT_HEX_LOWER
    upper = parsing.LAYOUT_HEX_UPPER
    assert parsing.literal_prefix(["ab12", "ab34"], lower) == ""
    assert parsing.literal_prefix(["AB12", "AB34"], upper) == ""
    assert parsing.literal_prefix(["DE-a1b2", "DE-c3d4"], lower) == "DE-"
    # ...and the cut eats a whole run, not one character of it.
    assert parsing.literal_prefix(["DE-aa1b", "DE-aa3d"], lower) == "DE-"
    # ...and a plain column is untouched by it.
    assert parsing.literal_prefix(["REC1", "REC2"], parsing.LAYOUT_PLAIN) == "REC"


def test_the_disclosure_rule_is_asked_of_a_hexadecimal_prefix(
    tmp_path: pathlib.Path,
) -> None:
    """A prefix four cells do not carry is not published (contract C6-140).

    796 cells of `DE-` and six hexadecimal figures beside four of `AC-`
    and six: the column shares no prefix, the four are counted under the
    same layout -- a hexadecimal mark hides which letters stood where --
    so no per-layout prefix stands either.
    """
    cells = _hex_tail(11)
    draw = random.Random(21)
    for place in range(4):
        cells[100 * place] = "AC-%06x" % draw.randrange(0, 1 << 24)
    got = _round_trip(tmp_path / "few-otherwise", cells, floor=11)
    assert got["source"]["layout_prefixes"] == {}
    assert got["twin_exit"] == 0 and got["real_exit"] == 0


# ----------------------------------------------------------- the loader


def test_the_loader_reads_a_prefix_under_the_census_own_convention(
    tmp_path: pathlib.Path,
) -> None:
    """LP2 asks the prefix's marks of the census's marks (contract C6-141).

    A prefix's own layout is `parsing.prefix_layout` under the census's
    own convention, read off the published keys exactly as
    `generation._layout_convention` reads it. Two halves are witnessed
    on the producer's OWN document: it loads, and a hand-edited prefix
    one mark too long for the same census is refused under LP2.

    Mutation: with the convention not read -- a letter marked by its case
    whatever the column -- `DE-` is `@@-`, which opens no hexadecimal
    layout, and the loader refuses the document the producer just wrote:
    `test_a_hexadecimal_column_publishes_and_writes_its_prefix` turns red
    with it, because `generate` loads what `profile` wrote.
    """
    import copy
    import json

    from tests.test_stage2_round_trip import _exit_of

    folder = tmp_path / "loaded"
    folder.mkdir()
    table = folder / "real.csv"
    cells = _hex_tail(13)
    table.write_text(
        fixtures.rows_to_csv(
            ["value", "other"],
            [[cells[index], f"row{index % 7}"] for index in range(ROWS)],
        ),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of(
        [
            "profile", str(table), "--out-dir", str(folder), "--replace",
            "--identifier", "value", "--smallest-group", "11",
        ]
    ) == 0
    written = folder / "real-profile.json"
    document = json.loads(written.read_text(encoding="utf-8"))
    loaded = contract.load_profile(str(written))
    first = loaded.columns[0].facts
    assert isinstance(first, contract.IdentifierFacts)
    assert first.layout_prefixes == {"(column)": "DE-"}
    assert first.layout_forms == {"~~-~~~~~~": ROWS}
    broken = copy.deepcopy(document)
    column = broken["columns"][0]
    assert isinstance(column, dict)
    column["layout_prefixes"] = {"(column)": "DEA-"}
    respelled = fixtures.write_profile(folder, "respelled.json", broken)
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(str(respelled))
    assert contract.INVARIANTS["LP2"] in f"{raised.value}"
