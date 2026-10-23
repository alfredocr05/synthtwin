"""The command at a smallest group size under 11, through the internal setting.

THE OWNER'S FLOOR OF 11 IS A MINIMUM (plan P4-D426, the owner's answer
of 2026-10-23): `--smallest-group` raises the floor and never lowers it,
and `generate` and `validate` refuse a description that records a floor
under 11. The suite was written at the floors its checks need -- 1, 2,
5, 10 and others -- and keeps them through ONE internal setting,
`cli.main`'s keyword-only `lowered_floor`, which no option, environment
variable, questions file or settings file reaches
(`tests/test_floor_is_a_minimum.py` proves each).

`main` here is the bridge, and it is the only one: a test or a helper
that runs the command at a floor under 11 calls it instead of
`cli.main`, keeping the argument list it was written with. A
`--smallest-group N` under 11 in that list (as two words, or as one
with `=`) is taken out and handed to the setting, so the typed option
never carries it; and `generate` and `validate` are given the setting
at 1, so they read the descriptions those runs wrote. Every other run
-- a floor of 11 or more, typed or not -- goes to `cli.main` exactly as
typed, so nothing it writes moves by a byte.
"""

import sys

from synthtwin import cli

_OPTION = "--smallest-group"
_MINIMUM = 11


def _moved(argv: "list[str]") -> "tuple[list[str], int | None]":
    """The arguments without a floor under 11, and that floor (or None)."""
    kept: "list[str]" = []
    floor: "int | None" = None
    index = 0
    while index < len(argv):
        word = argv[index]
        typed = None
        width = 1
        if word == _OPTION and index + 1 < len(argv):
            typed = argv[index + 1]
            width = 2
        elif word.startswith(f"{_OPTION}="):
            typed = word[len(_OPTION) + 1 :]
        number = None
        if typed is not None:
            try:
                number = int(typed)
            except ValueError:
                number = None
        if number is not None and number < _MINIMUM:
            floor = number
            index += width
            continue
        kept += argv[index : index + width]
        index += width
    return kept, floor


def main(argv: "list[str] | None" = None) -> int:
    """`cli.main`, with a floor under 11 moved to the internal setting.

    Guarantees: `argv` None reads `sys.argv[1:]`, as `cli.main` does. A
    run whose arguments name no floor under 11 and no `generate` or
    `validate` is `cli.main` called with the same argument (None kept as
    None); otherwise `cli.main` is called with the floor moved to
    `lowered_floor` (1 for `generate` and `validate`). Returns what it
    returns and lets what it raises through.
    """
    words = list(sys.argv[1:] if argv is None else argv)
    kept, floor = _moved(words)
    command = next((word for word in kept if not word.startswith("-")), "")
    reading = command in ("generate", "validate")
    if floor is None and not reading:
        return cli.main(argv)
    if floor is None:
        floor = 1
    return cli.main(kept, lowered_floor=floor)
