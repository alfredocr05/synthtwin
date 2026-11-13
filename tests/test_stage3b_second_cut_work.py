"""The second key cut's declarations are read in step with their entries (review of landing R2K, item 1).

WHAT WAS WRONG. Plan P4-D386 reserves three declarations of the settings
block and refuses each unless it is empty, once their shapes are read
and S8d is held. Two of those reads searched LISTS. `_declared_pairs`
asked, for every entry, whether its column stood among the columns read
before it; and S8d asked, for every counted column, whether it stood in
each of six other declarations, building the columns of the century
windows again each time. Both do work in the square of the entries, and
both did it before a description that had to be refused was: on
9cb2eb5 a 100-row table's description holding 80,000 different
`forced_date_counts` pairs, 4.5 MB, took 17.2 s to reach its refusal
(21.3 s where the review measured it), and every doubling of the pairs
took four times as long -- 0.27 s at 10,000 pairs, 1.09 s at 20,000 and
4.46 s at 40,000, the settings block read on its own.

THE MEASURE, WHICH NEEDS NO CLOCK. Every name handed to the reader here
is text of a kind that counts each comparison it takes part in and each
time its hash is asked for, which is every step of a search, whether
through a list or a set; the reader keeps the text it is handed, so each
step it takes over a name is counted. Doubling the entries doubles that
count where each name is looked up once, and quadruples it where a list
is searched for each name. The count is taken at N entries and at 2N and
the ratio must stay under 2.5; on 9cb2eb5 it is four. The two searches
as 9cb2eb5 shipped them are kept below, and the same measure must see
THEM grow as the square, so the measure is known to see the defect
rather than assumed to.

WHAT MUST NOT MOVE. The searches still take the entries in the order
written, so a refusal names the entry it named before: the first column
written twice, and the first counted column in the order written, under
the first other reading in S8d's own order. And S8d still stands before
the reserved-key refusal, however long the lists, so a counted column
named under another reading is refused for that pair and not for its key.

Every count here is taken whether the block is refused or read, so the
landings that fill the three keys (P4-D383, P4-D384) leave this file as
it is, and their own reading is held to the same growth.
"""

from __future__ import annotations

import pytest

from synthtwin import contract, errors, profile, taxonomy

# What a reader whose work grows with the entries may grow by when the
# entries double, and what the replaced searches must reach to show the
# measure can fail: linear work doubles, work in the square quadruples.
LINEAR_AT_MOST = 2.5
SQUARE_AT_LEAST = 3.0

# How many times a counted name was compared or hashed since the last reset.
_ASKED = [0]


class _Counted(str):
    """A column's name that counts every comparison and every hash asked of it."""

    def __eq__(self, other: object) -> bool:
        _ASKED[0] += 1
        return str.__eq__(self, other)

    def __ne__(self, other: object) -> bool:
        _ASKED[0] += 1
        return str.__ne__(self, other)

    def __hash__(self) -> int:
        _ASKED[0] += 1
        return str.__hash__(self)


def _block(**declarations: object) -> "dict[str, object]":
    """The producer's own settings block at its defaults, with ``declarations`` in place."""
    block = profile._settings_block(taxonomy.Settings(), [], [], [], [])
    for key, value in declarations.items():
        assert key in block, key
        block[key] = value
    return block


def _names(prefix: str, size: int) -> "list[_Counted]":
    """``size`` different counted names, in rising order, none shared with another prefix."""
    return [_Counted(f"{prefix}{place:06d}") for place in range(size)]


def _counts_alone(size: int) -> "dict[str, object]":
    """The review's own case: different `forced_date_counts` pairs, nothing else declared."""
    return _block(
        forced_date_counts=[[name, "excel-1900"] for name in _names("c", size)]
    )


def _windows_alone(size: int) -> "dict[str, object]":
    """The other declaration of pairs: different `century_windows`, nothing else declared."""
    return _block(century_windows=[[name, 1930] for name in _names("w", size)])


def _every_reading_filled(size: int) -> "dict[str, object]":
    """Counted columns beside every other declaration S8d reads, ``size`` each, none shared."""
    return _block(
        century_windows=[[name, 1930] for name in _names("w", size)],
        forced_date_columns=_names("d", size),
        forced_date_counts=[[name, "excel-1900"] for name in _names("c", size)],
        forced_twelve_hour_clocks=_names("t", size),
        forced_codes=_names("k", size),
        forced_identifiers=_names("i", size),
        forced_measurements=_names("m", size),
    )


_SHAPES = {
    "counts-alone": _counts_alone,
    "windows-alone": _windows_alone,
    "every-reading-filled": _every_reading_filled,
}


def _pairs_as_built(entries: "list[list[object]]") -> "list[tuple[object, object]]":
    """`contract._declared_pairs`'s search as 9cb2eb5 shipped it: a list of the names read."""
    pairs: "list[tuple[object, object]]" = []
    names: "list[object]" = []
    for name, other in entries:
        if name in names:
            break
        names += [name]
        pairs += [(name, other)]
    return pairs


def _searches_as_built(block: "dict[str, object]") -> None:
    """Both searches as 9cb2eb5 shipped them, over the same declarations."""
    windows = _pairs_as_built(block["century_windows"])  # type: ignore[arg-type]
    counted = _pairs_as_built(block["forced_date_counts"])  # type: ignore[arg-type]
    for name, _system in counted:
        for others in (
            block["forced_date_columns"],
            [column for column, _year in windows],
            block["forced_twelve_hour_clocks"],
            block["forced_codes"],
            block["forced_identifiers"],
            block["forced_measurements"],
        ):
            if name in others:  # type: ignore[operator]
                return


def _read(block: "dict[str, object]") -> None:
    """The settings reader the loader runs, refused or not."""
    try:
        contract._settings(block)
    except errors.ProfileError:
        pass


def _asked(shape: str, size: int, reader: "object" = _read) -> int:
    """Comparisons and hashes ``reader`` asks of the names of ``shape`` at ``size`` entries."""
    block = _SHAPES[shape](size)
    _ASKED[0] = 0
    reader(block)  # type: ignore[operator]
    return _ASKED[0]


@pytest.mark.parametrize("shape", sorted(_SHAPES))
def test_the_reserved_declarations_are_read_in_step_with_their_entries(shape: str) -> None:
    """Twice the entries ask about twice the look-ups; 9cb2eb5's searches asked four times as many.

    On 9cb2eb5 each of the three shapes reads at a ratio of four: the
    pairs' own search alone, the windows' alone, and S8d's search of
    every other reading for every counted column.
    """
    small, large = _asked(shape, 500), _asked(shape, 1000)
    assert small > 0, "no name was looked up: the measure saw nothing"
    assert large / small < LINEAR_AT_MOST, (shape, small, large)
    old_small = _asked(shape, 500, _searches_as_built)
    old_large = _asked(shape, 1000, _searches_as_built)
    assert old_large / old_small >= SQUARE_AT_LEAST, (shape, old_small, old_large)


def _refusal(block: "dict[str, object]") -> str:
    """What the settings reader says refusing ``block``."""
    with pytest.raises(errors.ProfileError) as refused:
        contract._settings(block)
    return str(refused.value)


@pytest.mark.parametrize(
    "key,value", [("century_windows", 1930), ("forced_date_counts", "excel-1900")]
)
def test_the_first_column_written_twice_is_the_one_named(key: str, value: object) -> None:
    """The first repeat in the order written is refused by its own name, as before.

    `visit_on` is repeated at the third entry and `admitted_on` at the
    fourth, so a search in any other order -- the names sorted, or the
    last repeat kept -- names `admitted_on`.
    """
    said = _refusal(
        _block(
            **{
                key: [
                    ["visit_on", value],
                    ["admitted_on", value],
                    ["visit_on", value],
                    ["admitted_on", value],
                ]
            }
        )
    )
    assert "'visit_on'" in said and "admitted_on" not in said, said
    assert "each column named once" in said, said


def test_s8d_names_the_first_counted_column_under_its_first_other_reading() -> None:
    """S8d takes the counted columns in the order written, then the readings in its own order.

    `visit_on`, written first, is also named as holding codes and as
    holding measurements; `admitted_on`, written second, is named as a
    column of dates read another way, the FIRST reading S8d asks about.
    So the refusal is `visit_on`'s, as holding codes: walking the
    readings first names `admitted_on`, and any other order of the
    readings names measurements.
    """
    said = _refusal(
        _block(
            forced_date_counts=[["visit_on", "excel-1900"], ["admitted_on", "excel-1900"]],
            forced_date_columns=["admitted_on"],
            forced_codes=["visit_on"],
            forced_measurements=["visit_on"],
        )
    )
    assert contract.INVARIANTS["S8d"] in said, said
    assert (
        "'visit_on' is named as writing its dates as counts and also as holding codes"
        in said
    ), said
    assert "admitted_on" not in said, said


def test_s8d_stands_before_the_reserved_key_refusal_however_long_the_lists() -> None:
    """The last of 5,000 counted columns, named also as holding measurements, is refused under S8d.

    Beside 5,000 century windows, whose own refusal comes first of the
    three and would be the one named were S8d moved after it.
    """
    size = 5000
    last = f"c{size - 1:06d}"
    said = _refusal(
        _block(
            century_windows=[[f"w{place:06d}", 1930] for place in range(size)],
            forced_date_counts=[[f"c{place:06d}", "excel-1900"] for place in range(size)],
            forced_measurements=[last],
        )
    )
    assert contract.INVARIANTS["S8d"] in said, said
    assert (
        f"'{last}' is named as writing its dates as counts and also as holding measurements"
        in said
    ), said
