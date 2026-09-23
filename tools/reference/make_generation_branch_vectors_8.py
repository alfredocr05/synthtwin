"""The tenth file of synthtwin's generation reference vectors.

This is the TENTH entry point of one oracle, not a tenth oracle.  It asks
`make_generation_reference_vectors.py` for the four cases the tail
landing of stage 3 grew past the room their own files had (plan
P4-D328): the clock role's own case (`clock_ladder`), the column partly
at midnight (`partial_midnight`), the bare dates beside midnight moments
on a real offset (`midnight_bare_offsets`), and the day-unit case
(`midnight_days`).

**Why they are a tenth file.**  A column of dates or clock times needs
`2F + 1` cells to publish a tail at all, and a case whose rule lives
BETWEEN the two boundaries needs a body of several ranks besides, so
each of the three grew at that landing.  Grown in place they carried
`generation-branch-vectors-2.json` to 261857 bytes and
`generation-branch-vectors.json` to 258476 against the provenance
manifest's 250000-byte cap (G14.2), so the four move here whole and
both files fall back under it.  No case was dropped, no proof was
shortened and the cap was not raised -- which is the reason the fourth
to the ninth files exist, and it is written here rather than left to be
worked out from a byte count.

Everything the second entry point says holds for this one word for word:
the transform, the proof layer, the words-as-inputs rule and every case
builder live in `make_generation_reference_vectors.py` beside this file,
and two copies of a proof layer would be two things that can drift apart.

Usage:  python3 make_generation_branch_vectors_8.py --seed 0 --out <path>
"""

import os
import runpy
import sys

ORACLE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "make_generation_reference_vectors.py",
)


def main(argv=None):
    """Write the tenth case set to the path given by --out.

    Returns the oracle's own outcome, so a run that could not prove every
    number it would publish stops here exactly as it stops there.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv, part=oracle["EIGHTH_BRANCH_PART"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
