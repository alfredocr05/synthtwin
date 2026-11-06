"""What the tail rule publishes, worked out from the rule (stage 3).

Landing 3.3 withholds every rung whose type-7 reading touches one of the
outermost `max(small_cell_floor, 3)` values of a column, on each side,
and publishes what those rows look like as a GROUP instead: how many
there are, how far from the last published rung they lie on average, the
root-mean-square of that distance, and, on a grid, their own values
(contract `docs/spec/profile-contract-v6.md` 6.7a, invariants TL1 to
TL6).

MANY TESTS USED TO NAME AN END. `percentiles.min` was the smallest value
of the column and a test that wanted to say "this number is in the
statistics and that one is not" said it that way. On a block that
carries `tails` the two ends are usually withheld, so those tests say it
through the facts that replaced them -- and the expectations are worked
out HERE, from the contract's own statement of the rule, rather than
copied from what the producer printed. The arithmetic is deliberately
the plainest reading of the text: the type-7 rung by the contract's own
formula, the distances as exact rationals, and one rounding at the end.

Nothing here imports the producer, and this module holds no rule of its
own: where it disagrees with `synthtwin.taxonomy` one of the two has
misread section 6.7a, which is what a test asking it is for.
"""

import fractions
import math

Fraction = fractions.Fraction


def units(floor: int) -> int:
    """`max(small_cell_floor, 3)`: the rows one tail withholds at least."""
    return floor if floor > 3 else 3


def percent_of(count: int, floor: int) -> "int | None":
    """The boundary percent of a column of `count` numbers, or None.

    The smallest whole percent from 1 to 50 whose type-7 reading leaves
    at least `units(floor)` values strictly outside it (TL1). None where
    no percent clears two tails at once, which is the block that
    publishes its moments alone (TL3).
    """
    wanted = units(floor)
    for percent in range(1, 51):
        if ((count - 1) * percent) // 100 >= wanted:
            return percent
    return None


def rows_of(count: int, percent: int, low: bool) -> int:
    """How many rows lie beyond one boundary percent (TL4)."""
    steps = (count - 1) * percent
    if low:
        return -((-steps) // 100)
    return count - 1 - steps // 100


def rung_at(values: "list[float]", percent: int) -> Fraction:
    """The type-7 rung at one whole percent, exactly.

    `h = (n - 1) * p / 100`, and the reading is
    `x[floor(h)] + (h - floor(h)) * (x[floor(h) + 1] - x[floor(h)])`,
    which is the contract's own formula (section 6.7) taken over exact
    rationals so no rounding of this helper's own can move an
    expectation.
    """
    ordered = sorted(Fraction(value) for value in values)
    place = Fraction((len(ordered) - 1) * percent, 100)
    under = int(place)
    if under >= len(ordered) - 1:
        return ordered[len(ordered) - 1]
    share = place - under
    return ordered[under] + share * (ordered[under + 1] - ordered[under])


# How many binary digits the whole-number square root below is grown to
# carry. Fifty-three decide the last place of a binary64 and the rest is
# headroom against the truncation of `math.isqrt`.
_GUARD_DIGITS = 128


def rounded_root(value: Fraction) -> float:
    """The binary64 nearest the square root of a rational.

    The rule computes a tail's root-mean-square exactly and rounds it
    ONCE (section 6.7a), so a helper that took `math.sqrt` of a rounded
    quotient would round twice and disagree in the last place. The
    square root is taken in whole numbers, and the guard is chosen FROM
    THE VALUE'S OWN SIZE rather than fixed, so the whole-number root
    carries at least `_GUARD_DIGITS` binary digits whatever the
    exponent.

    A FIXED GUARD IS NOT SCALE-SAFE, which is what this rounds. At
    sixty-four guard bits `(numerator << 128) // denominator` is NOUGHT
    for every value below about 1e-39, so `rounded_root(Fraction(1,
    10**40))` returned 0.0 where the root is 1e-20 -- a helper that
    certifies a published root-mean-square as nought is a helper that
    would pass a tail publishing nothing and fail one publishing the
    truth. The guard now grows with the exponent: the shift is raised
    until the whole-number root has the digits the rounding of the last
    place is decided at, so the answer is the same binary64 at 1e-200
    as at 1.
    """
    if value <= 0:
        return 0.0
    top = value.numerator
    bottom = value.denominator
    # `root` has about `(bits(top) - bits(bottom) + shift) / 2` digits,
    # and the last place of a binary64 is decided at 53 of them; the
    # rest is headroom, so a truncating `isqrt` cannot move the answer.
    shift = 2 * _GUARD_DIGITS + bottom.bit_length() - top.bit_length()
    if shift < 0:
        shift = 0
    if shift % 2:
        shift = shift + 1
    root = math.isqrt((top << shift) // bottom)
    return float(Fraction(root, 1) / Fraction(2) ** (shift // 2))


def facts_of(
    values: "list[float]",
    floor: int = 11,
    low: bool = True,
    boundary: "float | None" = None,
) -> "dict | None":
    """The `tails.low` or `tails.high` a column of these numbers publishes.

    Returns None where the block publishes no tail at all -- fewer
    numbers than one tail's own rows (TL2), or no percent clearing two
    tails at once (TL3). `values` are the numbers the statistics use.

    THE DISTANCES ARE MEASURED FROM THE RUNG THE DESCRIPTION PUBLISHES,
    which is a binary64 and not the exact reading behind it, so a caller
    that has the block passes `boundary` and gets the producer's own
    answer to the last place. Left out, the exact type-7 reading stands
    in, which is the same number wherever it is representable.
    """
    count = len(values)
    if count < units(floor):
        return None
    percent = percent_of(count, floor)
    if percent is None:
        return None
    if not low:
        percent = 100 - percent
    rows = rows_of(count, percent, low)
    stands = (
        rung_at(values, percent) if boundary is None else Fraction(boundary)
    )
    ordered = sorted(Fraction(value) for value in values)
    beyond = ordered[:rows] if low else ordered[count - rows:]
    away = [abs(stands - value) for value in beyond]
    summed = sum(away, Fraction(0))
    squared = sum((one * one for one in away), Fraction(0))
    return {
        "percent": percent,
        "rows": rows,
        "mean_distance": float(summed / rows),
        "rms_distance": rounded_root(squared / rows),
        "boundary": float(stands),
    }


def withheld(values: "list[float]", floor: int = 11, low: bool = True) -> bool:
    """Whether the tail rule withholds that end of a column.

    It publishes the end only where at least `units(floor)` rows hold it
    -- a HEAPED end, a value of a group (TL1) -- and withholds it
    otherwise, which is the ordinary case for a column of different
    numbers.
    """
    ordered = sorted(values)
    end = ordered[0] if low else ordered[len(ordered) - 1]
    held = len([value for value in ordered if value == end])
    return held < units(floor)


_NAME_AT_PERCENT = {
    0: "min", 1: "p01", 5: "p05", 10: "p10", 25: "p25", 50: "p50",
    75: "p75", 90: "p90", 95: "p95", 99: "p99", 100: "max",
}


def rung_of(block: dict, percent: int) -> "float | None":
    """One published rung of a block, from either half of its ladder."""
    name = _NAME_AT_PERCENT.get(percent)
    if name is not None:
        return block["percentiles"][name]
    return block["percentiles_between"][f"p{percent:02d}"]


def stated(side: dict) -> tuple:
    """The four numbers one published tail side states.

    Its boundary percent, the rows beyond it, and the two distances --
    everything about the group except the VALUES a listed tail names,
    which a test that is about the listing reads for itself.
    """
    return (
        side["percent"],
        side["rows"],
        side["mean_distance"],
        side["rms_distance"],
    )


def expected(
    block: dict, values: "list[float]", floor: int = 11, low: bool = True
) -> tuple:
    """The four numbers the rule says that side of `block` must state.

    Worked out from the numbers the statistics used and the floor, with
    the distances measured from the rung the block itself publishes at
    the boundary percent -- the same binary64 the producer measured
    them from.
    """
    percent = percent_of(len(values), floor)
    if percent is None:
        raise AssertionError(
            "this column publishes no tail at all: no percent leaves "
            f"{units(floor)} values outside on both sides at once, so its "
            "moments stand alone (contract TL3)"
        )
    if not low:
        percent = 100 - percent
    facts = facts_of(values, floor, low, rung_of(block, percent))
    return (
        facts["percent"],
        facts["rows"],
        facts["mean_distance"],
        facts["rms_distance"],
    )


def holds(
    side: dict,
    block: dict,
    values: "list[float]",
    floor: int = 11,
    low: bool = True,
) -> bool:
    """Whether one published tail side states what the rule says it must.

    THE THIRD ANSWER A TAIL CAN GIVE (plan P4-D349). Where its rows, its
    two distances, its grid, the space's edges and the column's own remark
    that every value in it is different leave ONE possible set of
    distances, that set names every outer cell exactly -- so the tail
    publishes NEITHER distance, and a caller comparing four numbers
    against four reads the third answer as a disagreement.

    WHAT IS COMPARED, AND WHY EACH: the boundary percent and the rows
    ALWAYS, because they follow from the count of values and the floor
    alone (TL1, TL4) and no back-solve can move them; the two distances
    only where the block publishes them, against the same arithmetic as
    before; and where it publishes neither, the shape the contract admits
    -- both null, never one of each (TL5).

    This module still holds no rule of its own: whether a tail is settled
    is the PRODUCER's question, asked with a budget, and a helper that
    tried to answer it here would be a second statement of it. What is
    asserted here is that a withheld pair is withheld on BOTH keys and
    that everything the back-solve cannot touch is unchanged.
    """
    percent, rows, mean, root = stated(side)
    wanted = expected(block, values, floor, low)
    if (percent, rows) != wanted[:2]:
        return False
    if mean is None:
        return root is None
    return (mean, root) == wanted[2:]
