"""A prefixed column's fold partners wear the layouts the census names.

Plan decision P4-D230, method G9.6a step 6. The merge of the owner's
rulings of 2026-09-17 into the repair of the carried items of landing 2b
put two rules in one column for the first time: item 1 publishes a
literal prefix per layout (plan P4-D202), and plan P4-D196 holds a
declared identifier's fold-collision partners to the cells the layout
census names.

WHAT WENT WRONG WHEN THEY MET. G9.3 step 4 walks the parents of the
asking slot's own family in a cyclic order and takes the FIRST that
supplies a partner at all; the member preference of G9.3 step 2 chooses
inside one parent's family, so it cannot reach past that parent. That
order was fixed where every parent of a family could supply a partner of
any layout the census names. A published prefix narrows it: every cell
of a prefixed layout opens with the same characters, so one parent's
family reaches one layout and no other. On the column below the first
parent of each partner's family was a hyphenated one, whose case flip
`s-12-A` wears a layout the census names no cell for -- so the twin wrote
twenty of those, `&%%%%` came back 7 of 26, and `validate` exited 3
naming both misses. The miss was never silent; it was a fidelity loss
this shape did not have before the two rules met.

WHAT IS PINNED HERE: on a column publishing a prefix the twin writes
every published layout count exactly and the quality report holds; and a
column publishing NO prefix asks nothing new, so the older shortfall of
one cell -- the limit P4-D196 named and left -- stands exactly as it
stood. The second half is the mutation guard: a pass widened to every
column would turn it red.
"""

import pathlib
import random

import pytest

from tests.test_stage2_round_trip import _round_trip

PUBLISHED = {"%%%%%": 28, "&%%%%": 26, "@%%%%": 214, "@-%%-@": 32}


def _shape(letters: str) -> "list[str]":
    """Record numbers of four layouts, drawn from one stream.

    ``letters`` are the capitals the lettered layouts open with. One
    capital gives every cell of a layout the same opening, which is what
    makes the column publish a prefix for each of the three; two give the
    same census and no prefix at all, because the opening the cells of a
    layout share is then no letter.
    """
    draw = random.Random(21)
    cells: "list[str]" = []
    for index in range(300):
        pick = draw.random()
        opening = letters[index % len(letters)]
        if pick < 0.7:
            cells += [f"{opening}{1000 + index}"]
        elif pick < 0.8:
            cells += [f"{opening.lower()}{1000 + index - draw.randrange(1, 5)}"]
        elif pick < 0.9:
            cells += [f"{draw.randrange(10000, 99999)}"]
        else:
            cells += [f"{opening}-{draw.randrange(10, 99)}-A"]
    return cells


def _layouts(written: "list[str]") -> "dict[str, int]":
    """The layout each written cell wears, counted, by the census's marks."""
    held: "dict[str, int]" = {}
    for cell in written:
        key = ""
        for mark in cell:
            if "A" <= mark <= "Z":
                key = key + "@"
            elif "a" <= mark <= "z":
                key = key + "&"
            elif "0" <= mark <= "9":
                key = key + "%"
            else:
                key = key + mark
        held[key] = (held[key] if key in held else 0) + 1
    return held


@pytest.mark.parametrize("seed", ["1", "4"])
def test_a_prefixed_column_writes_every_published_layout(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """Every count of the census is met, and the twin validates at 0."""
    first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path / seed, _shape("S"), ("--identifier", "value"), seed=seed
    )
    # THE PRECONDITION IS PINNED, so the test cannot pass vacuously: the
    # column publishes a prefix for each lettered layout AND owes
    # partners, which is the only shape this rule reaches.
    assert first["layout_prefixes"] == {
        "&%%%%": "s", "@%%%%": "S", "@-%%-@": "S-",
    }
    assert first["n_distinct_folded"] < first["n_distinct"]
    assert first["layout_forms"] == PUBLISHED
    assert _layouts(written) == PUBLISHED, (seed, _layouts(written))
    assert twin_exit == 0 and real_exit == 0


@pytest.mark.parametrize("seed", ["1", "4"])
def test_a_column_publishing_no_prefix_asks_nothing_new(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """The older limit stands where no prefix is published (P4-D196).

    The same census over two capitals publishes no prefix, so nothing
    narrows the families and the parent walk is G9.3 step 4's own. Its
    one-cell shortfall -- an identity carrying the published longest
    length whose partner can wear no named layout -- is the limit plan
    P4-D196 named and left, and it is pinned here rather than repaired,
    because repairing it would move the bytes of every column that owes
    a partner.
    """
    first, _second, written, twin_exit, _real_exit = _round_trip(
        tmp_path / seed, _shape("ST"), ("--identifier", "value"), seed=seed
    )
    assert first["layout_prefixes"] == {}
    assert first["layout_forms"] == PUBLISHED
    assert _layouts(written) == {
        "%%%%%": 28, "&%%%%": 26, "&-%%-@": 1, "@%%%%": 213, "@-%%-@": 32,
    }, (seed, _layouts(written))
    assert twin_exit == 3
