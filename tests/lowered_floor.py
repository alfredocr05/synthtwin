"""The command at a smallest group size under 11, through the internal setting.

THE OWNER'S FLOOR OF 11 IS A MINIMUM (plan P4-D426, the owner's answer
of 2026-10-23): `--smallest-group` raises the floor and never lowers it,
and `generate` and `validate` refuse a description that records a floor
under 11. The suite was written at the floors its checks need -- 1, 2,
5, 10 and others -- and keeps them through ONE internal setting,
`cli.main`'s keyword-only `internal_smallest_group`, which no option,
environment variable, questions file or settings file reaches
(`tests/test_floor_is_a_minimum.py` proves each).

`main` here is the bridge, and it is the only one: a test or a helper
that runs the command at a floor under 11 calls it instead of
`cli.main`, keeping the argument list it was written with. The option
is read as argparse reads it (Codex's review of lane MIN, items 4 and
5): under any spelling argparse takes for it (each prefix from `--sm`,
as two words or as one with `=`, never after `--`), the LAST of several
winning. Where that last value is a whole number under 11, every
occurrence is taken out and the number handed to the setting, so the
typed option never carries it; and `generate` and `validate` -- the
command found by the product's own parser, so an option's value is
never taken for it -- typed with no floor at all are given the setting
at 1, so they read the descriptions those runs wrote. Every other run
-- a last value of 11 or more, or text that is no number, on any
command, and no floor typed on the others -- goes to `cli.main` exactly
as typed, so nothing it writes moves by a byte and a refusal stays a
refusal.
"""

import contextlib
import io
import sys

from synthtwin import cli

_OPTION = "--smallest-group"
_MINIMUM = 11
# argparse takes any unambiguous prefix of a long option; `--sm` is the
# shortest no other option shares (`tests/test_floor_is_a_minimum.py`
# reads the spellings off the help screen and checks it).
_SHORTEST = "--sm"


def _spelled(word: str) -> bool:
    """Whether a word (before any `=`) is a spelling of the option."""
    name = word.split("=", 1)[0]
    return len(name) >= len(_SHORTEST) and _OPTION.startswith(name)


def _found(argv: "list[str]") -> "list[tuple[int, int, str]]":
    """Each place the option is typed: (its index, its words, its value).

    Empty when no floor is typed at all; the last entry is the value
    argparse keeps.
    """
    found: "list[tuple[int, int, str]]" = []
    index = 0
    while index < len(argv):
        word = argv[index]
        if word == "--":
            break
        if word.startswith("--") and _spelled(word):
            if "=" in word:
                found += [(index, 1, word.split("=", 1)[1])]
            elif index + 1 < len(argv):
                found += [(index, 2, argv[index + 1])]
                index += 2
                continue
        index += 1
    return found


def _moved(argv: "list[str]") -> "tuple[list[str], int | None]":
    """The arguments without a floor under 11, and that floor (or None).

    The floor is the LAST value given to the option, as argparse keeps
    it; only where that value is a whole number under 11 is anything
    moved, and then every occurrence goes.
    """
    found = _found(argv)
    if not found:
        return list(argv), None
    try:
        number = int(found[-1][2])
    except ValueError:
        return list(argv), None
    if number >= _MINIMUM:
        return list(argv), None
    taken = {
        place
        for start, width, _value in found
        for place in range(start, start + width)
    }
    kept = [word for place, word in enumerate(argv) if place not in taken]
    return kept, number


def _command(argv: "list[str]") -> "str | None":
    """The command word, as `cli`'s own parser finds it, or None.

    The parser is asked with the internal setting given, so the typed
    floor is not read; anything it would refuse or print (help, a word
    not understood) is swallowed here and left to `cli.main` itself.
    """
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
            io.StringIO()
        ):
            return cli._parse_arguments(list(argv), 1).command
    except SystemExit:
        return None


def main(argv: "list[str] | None" = None, **keywords: object) -> int:
    """`cli.main`, with a floor under 11 moved to the internal setting.

    Guarantees: `argv` None reads `sys.argv[1:]`, as `cli.main` does. A
    run whose arguments name no floor under 11 (by the last value given)
    is `cli.main` called with the same argument (None kept as None),
    except a `generate` or `validate` with no floor typed at all, which
    is given `internal_smallest_group` 1; a floor under 11 is moved to
    `internal_smallest_group`. So a typed floor of 11 or more, or text
    that is no number, reaches `generate` and `validate` as typed too
    (Codex's item 4, its "final `abc`"; lane MIN's verify of repair 1).
    Every other keyword -- lane CHa's `chain`, lane POP's
    `small_tables_refused` -- is handed to `cli.main` as given (batch
    4i's integration), so a test of either switch at a floor under 11
    runs through the bridge too.
    Returns what `cli.main` returns and lets what it raises through.
    """
    words = list(sys.argv[1:] if argv is None else argv)
    kept, floor = _moved(words)
    reading = _command(kept) in ("generate", "validate")
    if floor is None and (not reading or _found(words)):
        return cli.main(argv, **keywords)  # type: ignore[arg-type]
    if floor is None:
        floor = 1
    return cli.main(kept, internal_smallest_group=floor, **keywords)  # type: ignore[arg-type]
