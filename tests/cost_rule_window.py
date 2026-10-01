"""The cost rule's question (plan P4-D353), asked of a PUBLISHED numeric block.

A withheld tail is read as its narrowest reading (method G5.3b), and the
windows of `moments.mean` and `moments.std` are drawn from that reading
(G12.3). The rule publishes a withheld pair only where the description
with it withheld would leave one of those windows short of its value.
This module asks that question the way the CHECKER asks it -- the
loader's own reading of the block (`contract.numeric_block_facts`), then
the name the checker draws its windows by (`validation._windows_of`) --
so a producer that asked anything else disagrees with it.

Every table is built at test time by the callers' seeded builders; no
data-format file enters the repository (plan D13).
"""

from __future__ import annotations

import copy

from synthtwin import contract, taxonomy, validation


def window_misses(block: "dict", floor: int) -> "dict[str, bool]":
    """Per moment: does this plain column block's own G12.3 window miss its value?"""
    settings = taxonomy.Settings(small_cell_floor=floor)
    # THE LOADER'S OWN COUNTS for a plain numeric column (contract, the
    # `ROLE_COUNT or ROLE_CONTINUOUS` branch of the role reading).
    facts = contract.numeric_block_facts(
        block,
        floor,
        settings.minimum_parse_rate,
        settings.categorical_share,
        settings.categorical_ceiling,
        settings.categorical_floor,
        block["n_present"],
        block["n_numeric"],
        block["n_out_of_range"],
        block["n_contradictory"],
    )
    drawn = validation._windows_of(None, facts, floor)
    found: "dict[str, bool]" = {}
    for name in ("mean", "std"):
        found[name] = name in drawn and not drawn[name][0] <= block[name] <= drawn[name][1]
    return found


def missed(block: "dict", floor: int) -> "list[str]":
    """The moments whose window misses, in the order mean, std."""
    return [name for name, short in window_misses(block, floor).items() if short]


def costs(block: "dict", floor: int) -> bool:
    """The rule's predicate: the mean window or the std window misses."""
    return bool(missed(block, floor))


def withheld(block: "dict", sides: "tuple[str, ...]") -> "dict":
    """The same block with the named sides' pairs withheld."""
    edited = copy.deepcopy(block)
    for side in sides:
        edited["tails"][side] = dict(
            edited["tails"][side], mean_distance=None, rms_distance=None
        )
    return edited


def with_pairs(block: "dict", opened: "dict", sides: "tuple[str, ...]") -> "dict":
    """``block`` with the real pairs of ``sides`` put back from ``opened``, every other withheld.

    ``opened`` is the same column described with the back-solve answering
    OPEN, so its pairs are the ones the producer held before withholding.
    """
    edited = copy.deepcopy(block)
    for side in ("low", "high"):
        tail = dict(edited["tails"][side])
        if side in sides:
            tail["mean_distance"] = opened["tails"][side]["mean_distance"]
            tail["rms_distance"] = opened["tails"][side]["rms_distance"]
        else:
            tail["mean_distance"] = None
            tail["rms_distance"] = None
        edited["tails"][side] = tail
    return edited


def published_where_it_costs_nothing(block: "dict", floor: int) -> "list[str]":
    """The published pairs whose withholding would cost the twin nothing.

    Asked only of a block BOTH of whose pairs the back-solve withholds
    (each caller states why its shape is one), where every pair published
    is the cost rule's: the owner's ruling 4 publishes such a pair only
    where withholding it again leaves a window short of its value.
    """
    found: "list[str]" = []
    for side in ("low", "high"):
        one = block["tails"][side]
        if one["mean_distance"] is None or one["values"]:
            continue
        if not costs(withheld(block, (side,)), floor):
            found += [side]
    return found
