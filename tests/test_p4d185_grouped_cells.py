"""Plan P4-D185: as many cells reach a thousand as the marks census counts.

THE DEFECT. `thousands_marks` counts the cells written with a mark between
thousands, and a cell carries one exactly where its number reaches a
thousand. The values stage places the strata around a thousand by
interpolating the ladder and never read the census, so a rank or two
either side of it came out wrong: a semicolon export of 2,000 lognormal
amounts written `1.234,56` published `{".": 418}` and its twin wrote 416
at every seed. Over twelve such columns, sixteen of twenty-four twins wrote
one or two fewer and two wrote one more; the surplus was named nowhere,
because a surplus under the census line is written with the mark.

Each shape here is written by seeded neutral code, described, built, the
twin described AGAIN under the same declaration, and the twin and the
real table validated. The mutation named in each test is `_grouped_enough`
handing its values back untouched.
"""

import pathlib
import random

import pytest

from tests.test_stage2_round_trip import _round_trip


def _amounts(seed: int, rows: int, mu: float, sigma: float, comma: bool) -> "list[str]":
    """Lognormal amounts at two places, grouped, in either convention."""
    draw = random.Random(seed)
    cells: "list[str]" = []
    for _row in range(rows):
        text = f"{round(draw.lognormvariate(mu, sigma), 2):,.2f}"
        if comma:
            text = text.replace(",", "\x00").replace(".", ",").replace("\x00", ".")
        cells += [text]
    return cells


# (name, source seed, rows, mu, sigma, decimal comma): the first two twins
# wrote one or two grouped cells FEWER than the census, the third one MORE.
SHAPES = (
    ("short-by-two", 21, 300, 6.5, 0.8, True),
    ("short-by-one", 5, 2000, 6.5, 1.4, True),
    ("over-by-one", 8, 800, 7.0, 1.1, False),
)


@pytest.mark.parametrize("name,source,rows,mu,sigma,comma", SHAPES)
def test_the_marks_census_comes_back_exactly(
    name: str,
    source: int,
    rows: int,
    mu: float,
    sigma: float,
    comma: bool,
    tmp_path: pathlib.Path,
) -> None:
    """The twin's own description publishes the table's marks census.

    Mutation: with `_grouped_enough` returning its values untouched, the
    two short shapes come back 96 against 98 and 796 against 797, and the
    third 410 against 409.
    """
    cells = _amounts(source, rows, mu, sigma, comma)
    flags: "tuple[str, ...]" = ("--decimal-comma", "value") if comma else ()
    for seed in ("1", "4"):
        first, second, written, twin_exit, real_exit = _round_trip(
            tmp_path / f"{name}-{seed}", cells, flags, seed=seed
        )
        mark = "." if comma else ","
        assert first["thousands_marks"] == {mark: sum(mark in c for c in cells)}
        assert second["thousands_marks"] == first["thousands_marks"], (name, seed)
        assert sum(mark in c for c in written) == first["thousands_marks"][mark]
        for fact in ("n_distinct_values", "n_negative", "fraction_widths"):
            assert second[fact] == first[fact], (name, seed, fact)
        assert twin_exit == 0, (name, seed)
        assert real_exit == 0, (name, seed)
