"""The cost rule's question (plan P4-D353), asked of a PUBLISHED numeric block.

A withheld tail is read as its narrowest reading (method G5.3b), and the
windows of `moments.mean` and `moments.std` are drawn from that reading
(G12.3). The rule published a withheld pair only where the description
with it withheld would leave one of those windows short of its value;
since plan P4-D375 every pair is published, and the suite asks the same
question of a description to say what a pair keeps. This module asks it
the way the CHECKER asks it -- the loader's own reading of the block
(`contract.numeric_block_facts`), then the name the checker draws its
windows by (`validation._windows_of`).

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
