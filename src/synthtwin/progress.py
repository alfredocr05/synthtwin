"""Lines that tell a person at a terminal the run is still working (lane EZ-a, plan P4-D479).

THE USABILITY WALKTHROUGH'S ITEM 7. Describing a table of 20,000 rows
printed nothing for 8.6 seconds of computer work before its first line;
at 2,000,000 rows by 50 columns that silence is estimated at about fifty
minutes, and a person who sees nothing for that long closes the window
and loses the run. So, at a terminal only, `synthtwin profile`,
`generate` and `validate` print a line as each stage starts and, inside
the one long loop over the columns, ONE line that counts the columns as
they go, written over in place: a person sees the run moving, and the
screen does not fill with a line a column.

ONE SMALL SINK, SWITCHED ON BY THE COMMAND LINE ALONE. `cli` switches it
on where the run's screen is the terminal and the terminal shows it
(`cli._progress_at_a_terminal`), and off when the command ends; a piped,
captured or library run never switches it on, so nothing it would print
reaches a file, a log or a recorded screen. The three loops each make one
call (`column`) that hands over a position and a count -- never a cell, a
value or a name of the table -- and the call does nothing while the sink
is off.

NO CLOCK. The import allowlist (plan D6.2) admits no reading of a clock,
so the count is written over in place at every column rather than a line
a minute; what the description, the twin and the reports hold is the same
with the sink on or off, line for line and byte for byte.

Guarantees: prints to the error stream only, and only while switched on;
raises TypeError for a position, a count or words that are not of their
type; opens no file.
"""

import dataclasses
import sys


@dataclasses.dataclass
class _Sink:
    """Whether the lines are printed, what the count counts, and whether its line is still open."""

    on: bool = False
    what: str = ""
    counting: bool = False


_SINK = _Sink()


def switch_on(what: str) -> None:
    """Print the lines from now on; ``what`` names the work the count counts ('describing', 'building', 'checking')."""
    if not isinstance(what, str):
        raise TypeError("the work counted is named in words")
    _SINK.on = True
    _SINK.what = what
    _SINK.counting = False


def _closed() -> None:
    """End the count's line, where one is open, so the next line starts on its own."""
    if _SINK.counting:
        print("", file=sys.stderr)
        _SINK.counting = False


def switch_off() -> None:
    """Print nothing from now on, the count's line ended first."""
    _closed()
    _SINK.on = False
    _SINK.what = ""


def is_on() -> bool:
    """Whether the lines are printed."""
    return _SINK.on


def stage(text: str) -> None:
    """Say a stage has started (counting the people, writing), on a line of its own."""
    if not isinstance(text, str):
        raise TypeError("a stage is named in words")
    if not _SINK.on:
        return
    _closed()
    print(f"  ... {text}", file=sys.stderr)


def column(place: int, total: int) -> None:
    """Count the column the loop has reached, on the one line written over in place.

    ``place`` counts from 1. Called once a column by the loops over the
    columns of `profile.build_document`, `generation.generate` and
    `validation.measure`; a call while the sink is off costs one test.
    """
    if not _SINK.on:
        return
    if not isinstance(place, int) or not isinstance(total, int):
        raise TypeError("a column's place and the count of columns are whole numbers")
    print(f"\r  ... {_SINK.what} column {place} of {total}", end="", file=sys.stderr)
    _SINK.counting = True
    if place >= total:
        _closed()
