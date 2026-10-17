"""A label column's lone row is held back in the pool, as every rare level is.

Item 5 of the owner's rulings of 2026-09-17 (plan P4-D231) counted as
MISSING every cell of a held-back level whose pool a reader could read a
count of one off by subtraction -- one level on one row first (480 `F`,
519 `M` and one `U` at a floor of eleven), then the whole forced band
(P4-D239), bounded by the published rows and the pinned pool (P4-D271)
-- and loader invariants B4b and B4c refused such a pool. Plan P4-D390
sets that ruling aside, the orchestrator's call under the owner's
principle of 2026-10-01: HIPAA is the only privacy concern, a count
worked out within one column is accepted (2026-09-30, plan P4-D363), and
the pass cost the twin what it is built for -- measured at a floor of
eleven on seeded health tables, 22 to 32 per cent of a code register
blank, long-tail code columns read as categories, and code written on
the twin that ran there and crashed on the real table.

These are the shapes the ruling was built on. Each is a round trip --
describe, build, describe the twin again, validate the twin AND the
table -- asserting what the pool publishes, that no label of it is
printed, and that the twin writes a value in every row the table holds
one.

THE RED CHECK: run this file on `493f6f8`, where the pass stood, and
every round trip here but the floor of one and the three pools the
ruling left standing goes red on its blank count or its pool.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import json
import pathlib
import random

from synthtwin import contract, parsing, taxonomy
from tests import fixtures
from tests.test_final_review_labels import _round_trip


def _column(result: dict, name: str = "value") -> dict:
    """The block of one column of the description this trip wrote."""
    for block in result["document"]["columns"]:
        if block["name"] == name:
            return block
    raise AssertionError(f"no column {name}")


def _blank_cells(result: dict, name: str = "value") -> int:
    """How many cells of that twin column hold nothing at all."""
    return len([cell for cell in result["twin"][name] if cell == ""])


def _distinct_written(result: dict, name: str = "value") -> int:
    """How many different values that twin column holds, blanks aside."""
    return len({cell for cell in result["twin"][name] if cell})


def test_a_pool_of_one_is_published_in_the_pool(tmp_path: pathlib.Path) -> None:
    """F 480, M 519 and one U at a floor of eleven.

    The one `U` is a held-back level like any other: the pool is one
    level over one row, the column holds every one of its 1,000 values,
    and the twin holds three different values as the table does -- so a
    0/1 coding of the two values the twin shows fails on the twin, where
    it is written, and not first on the real table.
    """
    cells = ["F"] * 480 + ["M"] * 519 + ["U"]
    random.Random(5).shuffle(cells)
    result = _round_trip(
        tmp_path, {"value": cells}, ("--smallest-group", "11")
    )
    column = _column(result)
    assert [level["label"] for level in column["levels"]] == ["m", "f"]
    covered = sum(level["count"] for level in column["levels"])
    assert (column["suppressed_levels"], column["suppressed_rows"]) == (1, 1)
    assert (column["n_present"], column["n_missing"]) == (1000, 0)
    assert column["n_present"] - covered == column["suppressed_rows"]
    # Three values ignoring case is a set of categories, as it was
    # before the level pass made it two.
    assert column["role"] == "categorical"
    assert _blank_cells(result) == 0
    assert _distinct_written(result) == 3
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_one_level_of_several_rows_is_the_stated_limit(
    tmp_path: pathlib.Path,
) -> None:
    """One held-back level covering FIVE rows publishes the pool (1, 5).

    The pool is that level's own count, and five is below the floor.
    It was the limit plan P4-D231 stated beside the pass; since plan
    P4-D390 every held-back level is published this way, so this shape
    is the rule rather than its exception, and it is pinned unmoved.
    """
    cells = ["north"] * 200 + ["south"] * 150 + ["west"] * 5
    random.Random(7).shuffle(cells)
    result = _round_trip(
        tmp_path, {"value": cells}, ("--smallest-group", "11")
    )
    column = _column(result)
    assert [level["label"] for level in column["levels"]] == ["north", "south"]
    assert (column["suppressed_levels"], column["suppressed_rows"]) == (1, 5)
    assert (column["n_present"], column["n_missing"]) == (355, 0)
    assert _blank_cells(result) == 0
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_a_pool_of_more_than_one_level_is_published_too(
    tmp_path: pathlib.Path,
) -> None:
    """Three held-back levels over five rows: one of them is a single row.

    Five is fewer than twice three, so at least one of the three covers
    exactly one row whichever way the rest falls -- the forced band plan
    P4-D239 counted as missing. It is the pool (3, 5) now, and the twin
    writes all five rows.
    """
    cells = (
        ["north"] * 200 + ["south"] * 150
        + ["west"] * 2 + ["east"] * 2 + ["inland"]
    )
    random.Random(7).shuffle(cells)
    result = _round_trip(
        tmp_path, {"value": cells}, ("--smallest-group", "11")
    )
    column = _column(result)
    assert [level["label"] for level in column["levels"]] == ["north", "south"]
    assert (column["suppressed_levels"], column["suppressed_rows"]) == (3, 5)
    assert (column["n_present"], column["n_missing"]) == (355, 0)
    assert _blank_cells(result) == 0
    assert _distinct_written(result) == 5
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_a_pool_that_is_not_an_exception_stands(
    tmp_path: pathlib.Path,
) -> None:
    """780 record numbers each written once beside one value of twenty rows.

    The pass left this pool standing even when it stood, because it is
    the column rather than an exception beside it; it stands now as
    every pool does, and every cell is written.
    """
    cells = [f"code-{index:05d}" for index in range(780)] + ["CODE-00999"] * 20
    result = _round_trip(
        tmp_path, {"value": cells},
        ("--code", "value", "--smallest-group", "11"),
    )
    column = _column(result)
    assert column["n_missing"] == 0
    assert column["suppressed_levels"] == 780
    assert _blank_cells(result) == 0
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_a_pool_that_reaches_the_line_stands(tmp_path: pathlib.Path) -> None:
    """A long tail's pool is a group, published exactly as P4-D201 wrote it."""
    draw = random.Random(11)
    pool = [f"{chr(65 + index % 26)}{index:02d}" for index in range(300)]
    weights = [1.0 / (rank + 1) ** 1.1 for rank in range(len(pool))]
    cells = draw.choices(pool, weights=weights, k=2000)
    result = _round_trip(
        tmp_path, {"value": cells}, ("--smallest-group", "11")
    )
    column = _column(result)
    assert column["suppressed_levels"] >= 2
    assert column["suppressed_rows"] >= parsing.census_floor(11)
    covered = sum(level["count"] for level in column["levels"])
    assert column["n_present"] - covered == column["suppressed_rows"]
    assert column["n_missing"] == 0
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_a_floor_of_one_moves_not_one_byte(tmp_path: pathlib.Path) -> None:
    """At a floor of one no level is below it, so there is no pool.

    The column publishes all three levels and holds every row.
    """
    cells = ["F"] * 480 + ["M"] * 519 + ["U"]
    random.Random(5).shuffle(cells)
    result = _round_trip(tmp_path, {"value": cells}, ("--smallest-group", "1"))
    column = _column(result)
    assert [level["label"] for level in column["levels"]] == ["m", "f", "u"]
    assert (column["n_present"], column["n_missing"]) == (1000, 0)
    assert (column["suppressed_levels"], column["suppressed_rows"]) == (0, 0)
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_the_smallest_raised_floor_holds_one_row_back_too(
    tmp_path: pathlib.Path,
) -> None:
    """At a floor of two, one held-back level is one row, and it is pooled.

    Two is the smallest floor that holds anything back at all. The table
    is written at the population floor (plan P4-D341): TWO published
    levels and ONE row held back, every count below derived from that.
    """
    held = 1
    yes = (parsing.POPULATION_FLOOR - held) // 2
    cells = (
        ["yes"] * yes
        + ["no"] * (parsing.POPULATION_FLOOR - held - yes)
        + ["maybe"] * held
    )
    random.Random(3).shuffle(cells)
    result = _round_trip(
        tmp_path, {"value": cells}, ("--smallest-group", "2")
    )
    column = _column(result)
    assert [level["label"] for level in column["levels"]] == ["no", "yes"]
    assert (column["suppressed_levels"], column["suppressed_rows"]) == (1, held)
    assert (column["n_present"], column["n_missing"]) == (
        parsing.POPULATION_FLOOR,
        0,
    )
    assert _blank_cells(result) == 0
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_no_spelling_of_a_held_back_level_is_anywhere(
    tmp_path: pathlib.Path,
) -> None:
    """The text of a held-back level reaches no file of the run.

    The floor's own rule, which the drop of the level pass leaves whole:
    the one `ZEBRAWORD` is counted into the pool and named nowhere --
    not in the description, the summary, the twin or the twin's report
    -- and nothing of it is counted as absent.
    """
    cells = ["alpha"] * 300 + ["beta"] * 200 + ["ZEBRAWORD"]
    random.Random(9).shuffle(cells)
    result = _round_trip(
        tmp_path, {"value": cells}, ("--smallest-group", "11")
    )
    column = _column(result)
    assert (column["suppressed_levels"], column["suppressed_rows"]) == (1, 1)
    assert column["missing_by_source"] == {}
    assert (column["n_missing"], column["n_missing_withheld"]) == (0, 0)
    written = json.dumps(result["document"])
    assert "ZEBRAWORD" not in written and "zebraword" not in written
    assert "ZEBRAWORD" not in result["report"]
    assert "ZEBRAWORD" not in "".join(result["twin"]["value"])
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_the_loader_takes_a_pool_of_one_label_on_one_row(
    tmp_path: pathlib.Path,
) -> None:
    """B4b and B4c are retired: a pool of one loads, written by hand or not.

    The producer writes the pool (1, 1) for the F/M/U column now, and a
    description edited to hold a pinned pool -- `F` one row fewer and a
    second level held back over that row, two levels over two rows --
    loads too, where B4b refused it.
    """
    for retired in ("B4b", "B4c"):
        assert retired not in contract.INVARIANTS, retired
    cells = ["F"] * 480 + ["M"] * 519 + ["U"]
    random.Random(5).shuffle(cells)
    result = _round_trip(
        tmp_path / "trip", {"value": cells}, ("--smallest-group", "11")
    )
    loaded = contract.load_profile(str(result["profile"]))
    assert [column.name for column in loaded.columns] == ["value", "other"]
    document = json.loads(json.dumps(result["document"]))
    for block in document["columns"]:
        if block["name"] != "value":
            continue
        block["levels"][1]["count"] = 479
        block["levels"][1]["variants"] = {"F": 479}
        block["levels"][1]["shape_form_cells"] = 0
        block["suppressed_levels"] = 2
        block["suppressed_rows"] = 2
        block["n_distinct"] = 4
        block["n_distinct_folded"] = 4
    written = fixtures.write_profile(tmp_path, "edited.json", document)
    edited = contract.load_profile(str(written))
    assert [column.name for column in edited.columns] == ["value", "other"]


def test_the_helper_answers_for_the_roles_that_publish_levels() -> None:
    """The four whole-column label roles count their levels over the column.

    `numbers_with_labels` counts its levels over its LABEL half, which
    is why it is not in this tuple; `_published_distinct` asks it.
    """
    assert taxonomy._LEVEL_ROLES == (
        taxonomy.ROLE_BINARY,
        taxonomy.ROLE_CATEGORICAL,
        taxonomy.ROLE_CONSTANT,
        taxonomy.ROLE_LONG_TAIL,
    )
    assert taxonomy.ROLE_COMPOUND not in taxonomy._LEVEL_ROLES
