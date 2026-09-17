"""Plan P4-D182: a record number's layout is packed with its family.

THE DEFECT. Method G9.6 packs every group of a declared identifier into a
class and an alphabet band so the four class counts and the two alphabet
counts are met exactly, and only THEN offers the census of layouts. A
layout is a fact about a cell's length, class and band at once, so a
packing blind to the census can put a group where no layout it owes can
be worn. The battery column of `tests/test_p2c4f1_disposition_registry.py`
-- 49 rows of `N_0` to `N_12`, `no!!`, `x-y`, `913` and `-3` -- publishes
`{"%%%": 12, "&-&": 8, "@_%": 10, "@_%%": 3}` and its twin wrote `&-&`
and `@_%%` nought times and `@_%` twice on every seed, while the table's
own values meet every count and every layout.

THE RULE. Where the first answer leaves a named layout short and no group
owes a fold-collision partner, the census is packed as a third margin of
the same grid, and every group is offered its packed layout alone.

Each shape here is described, built, the twin described AGAIN under the
same declaration, and both the twin and the real table validated, at
three seeds -- on the 49-row column and on its shapes twenty times over,
760 rows. The mutation named in
each test is the withdrawal of `generation._layout_packed`.
"""

import pathlib

import pytest

from synthtwin import generation
from tests.test_stage2_round_trip import _round_trip

SEEDS = ("1", "4", "7")


def _review_column() -> "list[str]":
    """The declared-identifier column of the disposition registry battery."""
    return (
        [f"N_{index}" for index in range(13)]
        + ["no!!"] * 5
        + ["x-y"] * 8
        + ["913"] * 12
        + ["-3"] * 11
    )


def _review_scaled(scale: int) -> "list[str]":
    """The review column's shapes, ``scale`` times over, on 38 rows each.

    A capital, an underscore and one figure, and the same with two; two
    lower-case letters around a hyphen on eight rows; three figures on
    twelve; a minus and one figure on eleven; and a lower-case pair beside
    two marks on five. At twenty times over -- 760 rows -- the first
    packing wrote `&-&` 150 times against 160 and `@_%%` 18 times against
    20, which is the large column the review column's limit reaches.
    """
    letters = "GHJKMNPQRSTUVWXYZ"
    values: "list[str]" = []
    for index in range(scale):
        head = letters[index % 17]
        values += [f"{head}_{index % 10}"]
        values += [f"{head}_{index % 100:02d}"]
        values += [f"{head.lower()}-{letters[(index * 3) % 17].lower()}"] * 8
        values += [f"{100 + index * 7 % 900}"] * 12
        values += [f"-{index % 10}"] * 11
        values += ["no" + chr(33 + index % 10) * 2] * 5
    return values


@pytest.mark.parametrize(
    "name,cells",
    [("review", _review_column()), ("scaled", _review_scaled(20))],
)
def test_the_layout_census_comes_back_exactly(
    name: str, cells: "list[str]", tmp_path: pathlib.Path
) -> None:
    """The twin's own description publishes the table's layout census.

    Mutation: with `_layout_packed` answering None, the review column's
    twin publishes no `&-&` and the scaled column's publishes `&-&` 150
    times against 160, and both twins miss at exit 3.
    """
    for seed in SEEDS:
        first, second, _written, twin_exit, real_exit = _round_trip(
            tmp_path / f"{name}-{seed}",
            cells,
            ("--identifier", "value"),
            seed=seed,
        )
        assert first["role"] == "identifier"
        assert first["layout_forms"], name
        # EVERY LAYOUT THE TABLE'S CENSUS NAMES, AT ITS COUNT. The twin may
        # wear a nameable layout on cells the table's census names none
        # for -- `-3` has too few spellings to be named, the made-up `4e5`
        # has enough -- and the contract publishes nothing about those.
        for layout, count in first["layout_forms"].items():
            assert second["layout_forms"].get(layout) == count, (
                name, seed, layout, second["layout_forms"],
            )
        for fact in (
            "n_numeric", "n_not_numeric", "n_all_digits", "n_code_alphabet",
            "min_length", "max_length", "n_distinct",
            "n_distinct_by_occurrences",
        ):
            assert second[fact] == first[fact], (name, seed, fact)
        assert twin_exit == 0, (name, seed)
        assert real_exit == 0, (name, seed)


def test_the_first_packing_alone_leaves_the_review_column_short(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    """The vacuity floor: without the packing the defect is still there."""
    monkeypatch.setattr(generation, "_layout_packed", lambda *_a: None)
    first, second, _written, twin_exit, _real = _round_trip(
        tmp_path / "withdrawn", _review_column(), ("--identifier", "value")
    )
    assert second["layout_forms"] != first["layout_forms"]
    assert twin_exit == 3
