"""A label column's lone row read by subtraction is counted as missing.

Item 5 of the owner's rulings of 2026-09-17 (plan P4-D231, loader
invariant B4b). A label column publishes the levels the floor admits and
pools the rest as a count of levels and a count of rows -- and where
that pair is ONE level on ONE row it is a count of one outright, which
`n_present` less the published counts reads whether or not a key prints
it. So 480 `F`, 519 `M` and one `U` at a floor of eleven told every
reader that one row holds a third value, and the twin wrote an invented
label in exactly that person's row. That cell is now counted as MISSING,
spelled as nothing: the description is that of the table with it blank,
the twin writes a blank there, no count of one is left to be derived,
and no label that clears the floor is ever held back to hide it.

TWO WIDER READINGS WERE BUILT AND MEASURED BEFORE THIS ONE, and plan
P4-D231 puts both to the owner: one level of ANY size (53 witnesses
move), and a pool that does not reach `parsing.census_floor` (66 move,
and the held-back machinery of P4-D201 empties at every raised floor).
`test_one_level_of_several_rows_is_the_stated_limit` pins the first of
them as the limit it is.

Each rule is pinned by a round trip -- describe, build, describe the
twin again, validate the twin AND the table -- beside the fact it
decides, asserted on the files themselves.

THE RED CHECKS, each measured by withdrawing the rule in place:

* the pass itself (`counted_out` forced empty in
  `taxonomy.profile_column`) -- `test_a_pool_of_one_is_counted_as_missing`,
  `test_no_spelling_of_a_counted_out_cell_is_anywhere`,
  `test_the_smallest_raised_floor_reaches_it_too`, and the two pooled
  pairs of `tests/test_ruling_pooled_held_back_levels.py`;
* the rule widened -- `test_one_level_of_several_rows_is_the_stated_limit`
  and `test_a_pool_of_more_than_one_level_stands` go red under reading
  (a), and `test_a_pool_that_reaches_the_line_stands` under reading (b);
* the loader's own half -- the `B4b` entry of
  `tests/test_contract_loader.py`'s battery.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import json
import pathlib
import random

import pytest

from synthtwin import contract, errors, parsing, taxonomy
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


def test_a_pool_of_one_is_counted_as_missing(tmp_path: pathlib.Path) -> None:
    """F 480, M 519 and one U at a floor of eleven.

    The shape the rulings branch pinned as the limit this ruling closes.
    Two levels are published and cover every present cell, so the
    subtraction leaves nought; the column holds 999 values and one hole;
    and the twin writes 480, 519 and one blank.
    """
    cells = ["F"] * 480 + ["M"] * 519 + ["U"]
    random.Random(5).shuffle(cells)
    result = _round_trip(
        tmp_path, {"value": cells}, ("--smallest-group", "11")
    )
    column = _column(result)
    assert [level["label"] for level in column["levels"]] == ["m", "f"]
    covered = sum(level["count"] for level in column["levels"])
    assert (column["suppressed_levels"], column["suppressed_rows"]) == (0, 0)
    assert (column["n_present"], column["n_missing"]) == (999, 1)
    assert column["n_present"] - covered == 0
    # The role follows the levels that are left, and the twin describes
    # back to it: two values, ignoring case, is a binary column.
    assert column["role"] == "binary"
    assert _blank_cells(result) == 1
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_one_level_of_several_rows_is_the_stated_limit(
    tmp_path: pathlib.Path,
) -> None:
    """One held-back level covering FIVE rows stands, and is put to the owner.

    The pool is that level's own count, and five is below the floor --
    five people share a value the description will not name. The ruling
    names a LONE ROW and a count of ONE, so this is not counted out, and
    plan P4-D231 puts the wider reading to the owner with what it was
    measured to cost. Pinned here so that the limit is a fact of the
    suite rather than a sentence in a document.
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


def test_a_pool_of_more_than_one_level_stands(
    tmp_path: pathlib.Path,
) -> None:
    """Three held-back levels over five rows say nothing about any one.

    The line this ruling draws is a level's own COUNT, not the size of
    the pool: with three levels over five rows the sizes could be 1, 1,
    3 or 1, 2, 2, so no level's count is derived and the pool stands as
    P4-D201 writes it. What a reader CAN still take from such a pair --
    that at least one of them is a single row -- is the standing limit
    contract section 6.3 states, and it is true of every ordinary long
    tail, so the ruling does not reach it.
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
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_a_pool_that_reaches_the_line_stands(tmp_path: pathlib.Path) -> None:
    """A long tail's pool is a group, and the pass leaves it alone.

    The rule is the disclosure rule and not a ban on holding labels
    back: where the pool reaches `parsing.census_floor` no count of any
    one level can be read off it, so the column publishes it exactly as
    P4-D201 wrote it. A pass widened to every pool would take this
    column's whole tail.
    """
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
    """At the default floor no level is below it, so there is no pool.

    The gate in front of the pass asks that before anything else, so the
    ordinary run does not pay for a second reading and cannot lose a
    cell. The same column at a floor of one publishes all three levels
    and holds every row.
    """
    cells = ["F"] * 480 + ["M"] * 519 + ["U"]
    random.Random(5).shuffle(cells)
    result = _round_trip(tmp_path, {"value": cells})
    column = _column(result)
    assert [level["label"] for level in column["levels"]] == ["m", "f", "u"]
    assert (column["n_present"], column["n_missing"]) == (1000, 0)
    assert (column["suppressed_levels"], column["suppressed_rows"]) == (0, 0)
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_the_smallest_raised_floor_reaches_it_too(
    tmp_path: pathlib.Path,
) -> None:
    """At a floor of two, one held-back level is one row, and it goes.

    Every floor above one can hold a level back, and every such level
    publishes its own count where it is the only one. Two is the
    smallest floor that holds anything back at all.
    """
    cells = ["yes"] * 20 + ["no"] * 20 + ["maybe"]
    random.Random(3).shuffle(cells)
    result = _round_trip(
        tmp_path, {"value": cells}, ("--smallest-group", "2")
    )
    column = _column(result)
    assert [level["label"] for level in column["levels"]] == ["no", "yes"]
    assert (column["n_present"], column["n_missing"]) == (40, 1)
    assert _blank_cells(result) == 1
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_no_spelling_of_a_counted_out_cell_is_anywhere(
    tmp_path: pathlib.Path,
) -> None:
    """The text of the counted-out cells reaches no file of the run.

    A cell counted absent under its own spelling would put that spelling
    in `missing_by_source` or in the pool beside it, and a reader who
    can tell such a cell from an ordinary blank has been told the count
    the pass exists to withhold. The cells are counted as the empty
    spelling instead, so the description, the summary, the twin and the
    twin's report hold no character of them.
    """
    cells = ["alpha"] * 300 + ["beta"] * 200 + ["ZEBRAWORD"]
    random.Random(9).shuffle(cells)
    result = _round_trip(
        tmp_path, {"value": cells}, ("--smallest-group", "11")
    )
    column = _column(result)
    assert column["missing_by_source"] == {}
    assert column["n_missing_withheld"] == 1
    assert column["n_missing_blank"] == 0
    written = json.dumps(result["document"])
    assert "ZEBRAWORD" not in written and "zebraword" not in written
    assert "ZEBRAWORD" not in result["report"]
    assert "ZEBRAWORD" not in "".join(result["twin"]["value"])
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_the_loader_refuses_a_pool_a_reader_could_count(
    tmp_path: pathlib.Path,
) -> None:
    """B4b: a hand-edited description carrying such a pool is refused.

    The producer never writes one, so the loader's half of the rule
    needs a document written by hand. It names B4b and the group it
    refuses, and it prints no label.
    """
    cells = ["F"] * 480 + ["M"] * 519 + ["U"]
    random.Random(5).shuffle(cells)
    result = _round_trip(
        tmp_path / "trip", {"value": cells}, ("--smallest-group", "11")
    )
    document = json.loads(json.dumps(result["document"]))
    for block in document["columns"]:
        if block["name"] != "value":
            continue
        block["levels"][0]["count"] = 518
        block["levels"][0]["variants"] = {"M": 518}
        block["suppressed_levels"] = 1
        block["suppressed_rows"] = 1
        block["n_distinct"] = 3
        block["n_distinct_folded"] = 3
    written = fixtures.write_profile(tmp_path, "edited.json", document)
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(str(written))
    assert "B4b" in f"{refused.value}"
    assert "works out by subtraction" in f"{refused.value}"
    # ...and it prints no label of the table.
    assert "U" not in f"{refused.value}".split("B4b")[0].split("'value'")[1]


def test_the_question_is_a_count_of_one_and_nothing_wider() -> None:
    """`pool_names_a_level` asks about one level on one row and no more.

    Stated as a check rather than as a comment, because the two readings
    that were built and measured before this one are the ones a reader
    of this rule will reach for, and each is a live option the plan puts
    to the owner: one level of ANY size, and a pool that does not reach
    `parsing.census_floor`.
    """
    assert parsing.pool_names_a_level(1, 1)
    assert not parsing.pool_names_a_level(0, 0)
    # One level of more than one row: the wider reading (a), not built.
    for rows in (2, 5, 7, 10):
        assert not parsing.pool_names_a_level(1, rows)
    # More than one level: no level's own count is there to be read.
    for levels, rows in ((2, 2), (3, 5), (4, 10), (182, 217)):
        assert not parsing.pool_names_a_level(levels, rows)


def test_the_helper_answers_for_the_roles_that_publish_levels() -> None:
    """The four whole-column label roles are asked, and no other role is.

    A role that publishes no level list has no pool to read, so the pass
    must not touch it -- and `numbers_with_labels` is asked over its
    LABEL half, which is why it is not in this tuple.
    """
    assert taxonomy._LEVEL_ROLES == (
        taxonomy.ROLE_BINARY,
        taxonomy.ROLE_CATEGORICAL,
        taxonomy.ROLE_CONSTANT,
        taxonomy.ROLE_LONG_TAIL,
    )
    assert taxonomy.ROLE_COMPOUND not in taxonomy._LEVEL_ROLES
