"""Held-back label levels publish a pooled total only (owner ruling of 2026-09-17).

Item 2 of the owner's rulings of 2026-09-17, option A (plan P4-D201): a
label column stops publishing the size of each level the floor held back
(`suppressed_level_counts`) and publishes only how many there were and
the rows they covered together; the generator writes the invented levels
at sizes read off that pool and the debts the published facts leave it,
each below the floor; the validator holds the pooled total. Each rule is
pinned here by a round trip -- describe, build, describe the twin again,
and validate the twin AND the table at exit 0 -- beside the fact it
decides, asserted on the files themselves.

THE RED CHECKS, each measured by withdrawing the rule in place:

* the producer's pool of one taking the smallest label back
  (`taxonomy._levels`) -- `test_a_pool_of_one_takes_the_smallest_label`;
* the loader's pool of one and its bound on the pool -- the two B4
  entries of `tests/test_contract_loader.py`'s battery;
* the debts handed to the sizes withdrawn -- the committed cells of
  frozen cases `label_numbers`, `label_number_tiers` and
  `level_shape_stand_ins` in `tests/test_generation_reference.py`. On
  the amounts given below the pool alone happens to share out exactly,
  so that round trip pins the ones-first rule's miss and not this one;
* the number debt stopping at the ramp's average -- the spread check of
  `test_numbers_beside_comments_keep_their_spread`;
* the square ramp shared evenly instead -- the spread check of
  `test_readings_beside_labels_keep_their_spread`, and the committed
  cells of five frozen cases.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import json
import pathlib
import random
import statistics

from synthtwin import contract, errors, generation, parsing
from tests import fixtures
from tests.test_final_review_labels import _round_trip
from tests.test_numbers_beside_labels import SHAPES, _numbers
from tests.test_stage2_round_trip import _round_trip as _one_column_trip


def _codes(rows: int, seed: int) -> "list[str]":
    """A long tail of codes: a letter, two figures, a point and a figure."""
    draw = random.Random(seed)
    pool = [
        f"{chr(65 + (index * 7) % 26)}{(index * 37) % 100:02d}.{index % 10}"
        for index in range(900)
    ]
    weights = [1.0 / (rank + 1) ** 1.1 for rank in range(len(pool))]
    return draw.choices(pool, weights=weights, k=rows)


def _column(result: dict) -> dict:
    document = json.loads(pathlib.Path(result["profile"]).read_text("utf-8"))
    return document["columns"][0]


def test_a_long_tail_publishes_its_pool_and_no_size(
    tmp_path: pathlib.Path,
) -> None:
    """2,000 codes at a floor of eleven: the pool, and every twin level under it.

    The table holds back 388 levels on 785 rows. The description carries
    those two counts and no size of any one level; the twin writes 388
    invented levels on exactly 785 rows, none of them reaching the floor,
    and the twin described again publishes the same levels and the same
    pool.
    """
    cells = _codes(2000, 4)
    result = _round_trip(
        tmp_path, {"code": cells}, ("--smallest-group", "11")
    )
    column = _column(result)
    assert column["role"] == "long_tail_labels"
    assert "suppressed_level_counts" not in column
    assert (column["suppressed_levels"], column["suppressed_rows"]) == (388, 785)
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)
    published = {level["label"] for level in column["levels"]}
    counted: "dict[str, int]" = {}
    for cell in result["twin"]["code"]:
        key = parsing.folded(cell)
        if key and key not in published:
            counted[key] = counted.get(key, 0) + 1
    assert len(counted) == 388
    assert sum(counted.values()) == 785
    assert max(counted.values()) < 11


def test_the_loader_refuses_the_withdrawn_key(tmp_path: pathlib.Path) -> None:
    """A description still carrying the sizes is refused, naming the key."""
    cells = ["north"] * 30 + ["south"] * 20 + ["west"] * 3 + ["east"] * 2
    result = _round_trip(tmp_path, {"value": cells}, ("--smallest-group", "11"))
    document = json.loads(pathlib.Path(result["profile"]).read_text("utf-8"))
    document["columns"][0]["suppressed_level_counts"] = [2, 3]
    forged = fixtures.write_profile(tmp_path, "forged.json", document)
    try:
        contract.load_profile(str(forged))
    except errors.ProfileError as refusal:
        assert "suppressed_level_counts" in str(refusal)
    else:
        raise AssertionError("a description carrying the sizes loaded")


def test_a_pool_of_one_takes_the_smallest_label(tmp_path: pathlib.Path) -> None:
    """400 `north`, 15 `south` and one `west` at a floor of eleven.

    A pool of one row names the one row whose value is neither published
    label, and `n_present` less the published counts reads it unprinted.
    Fifteen rows joined to it make sixteen, which two invented labels
    hold below the floor, so `south` is held back beside `west`.
    """
    cells = ["north"] * 400 + ["south"] * 15 + ["west"]
    random.Random(5).shuffle(cells)
    result = _round_trip(tmp_path, {"value": cells}, ("--smallest-group", "11"))
    column = _column(result)
    assert [level["label"] for level in column["levels"]] == ["north"]
    assert (column["suppressed_levels"], column["suppressed_rows"]) == (2, 16)
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_a_pool_of_one_no_label_can_join_stands(tmp_path: pathlib.Path) -> None:
    """The named limit: 400 `north`, 399 `south` and one `west` at eleven.

    Holding `south` back would make a pool of four hundred rows over two
    labels, which the twin can only write with a label the floor
    publishes. So the pool of one stands, at its size.
    """
    cells = ["north"] * 400 + ["south"] * 399 + ["west"]
    random.Random(5).shuffle(cells)
    result = _round_trip(tmp_path, {"value": cells}, ("--smallest-group", "11"))
    column = _column(result)
    assert len(column["levels"]) == 2
    assert (column["suppressed_levels"], column["suppressed_rows"]) == (1, 1)
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_the_sizes_follow_the_four_steps() -> None:
    """Method G8.3's rule on its own, at the sizes the plan records."""
    # One word debt: three labels pay twenty-one below eleven, two more
    # are handed out, and the rows rise by the square of each place.
    assert generation.held_back_sizes(5, 21, 11, (), (21,)) == (1, 2, 4, 6, 8)
    # Nine numbers, seven of them one form, and one word, over four labels.
    assert generation.held_back_sizes(4, 10, 11, (7, 2), (1,)) == (1, 2, 2, 5)
    # A number debt stops at the ramp's average and the words take the
    # rest, one label a cell at most: 332 numbers and 556 words over 619
    # labels at eleven give the numbers eighty-three labels, `3 * 332 / 12`
    # rounded up, and the words the other 536.
    sizes = generation.held_back_sizes(619, 888, 11, (332,), (556,))
    assert len(sizes) == 619 and sum(sizes) == 888 and max(sizes) == 10
    assert sizes.count(1) == 535
    # Debts that do not come to the pool are one debt.
    assert generation.held_back_sizes(2, 10, 11, (3,), (3,)) == (3, 7)
    assert generation.held_back_sizes(0, 0, 11, (), ()) == ()


def test_every_published_form_count_is_paid_exactly(
    tmp_path: pathlib.Path,
) -> None:
    """Amounts given beside `PRN` and `held` at a floor of twenty.

    Five held-back levels on twenty-two rows owe fourteen cells of `%.%`.
    Sizes read off the pool alone -- one row each and the rest to the last
    label -- are `1, 1, 1, 1, 18`, which no choice makes fourteen, and the
    twin missed `%.%` at 38 against 34. Under the rule of plan P4-D201 the
    twin holds every published count.
    """
    cells = SHAPES["given_amounts"](150, random.Random(150 * 31 + 5))
    first, second, _written, twin_exit, real_exit = _one_column_trip(
        tmp_path / "amounts", cells, ("--smallest-group", "20"), True, "5"
    )
    assert "suppressed_level_counts" not in first
    assert (twin_exit, real_exit) == (0, 0)
    assert second["shape_forms"] == first["shape_forms"]
    assert second["suppressed_rows"] == first["suppressed_rows"]


def _spread_ratio(tmp_path: pathlib.Path, shape: str, rows: int, floor: str, seed: int) -> float:
    cells = SHAPES[shape](rows, random.Random(rows * 31 + seed))
    _first, _second, written, twin_exit, real_exit = _one_column_trip(
        tmp_path / shape, cells, ("--smallest-group", floor), True, str(seed)
    )
    assert (twin_exit, real_exit) == (0, 0)
    return statistics.pstdev(_numbers(written)) / statistics.pstdev(_numbers(cells))


def test_numbers_beside_comments_keep_their_spread(tmp_path: pathlib.Path) -> None:
    """Integers beside free comments at a floor of eleven, seed 4.

    The table's own sizes gave the twin 0.89 of its spread; handing the
    labels left over to the words first gave 0.78 at this seed. At the
    ramp's average the twin holds 0.92.
    """
    ratio = _spread_ratio(tmp_path, "integers_beside_comments", 1000, "11", 4)
    assert 0.85 <= ratio <= 1.15, ratio


def test_readings_beside_labels_keep_their_spread(tmp_path: pathlib.Path) -> None:
    """Readings beside two labels at a floor of twenty, seed 3.

    Seventy-two held-back levels on 570 rows, every one a number. Shared
    evenly they are all eight rows wide and walk the twin out to 1.48 of
    the table's spread; rising by the square of their place, the large
    ones sit by the published numbers and the twin holds 1.06.
    """
    ratio = _spread_ratio(tmp_path, "readings", 1200, "20", 3)
    assert 0.9 <= ratio <= 1.12, ratio
