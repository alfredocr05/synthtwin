"""The tenth file of synthtwin's generation reference vectors.

This is the TENTH entry point of one oracle, not a tenth oracle.  It asks
`make_generation_reference_vectors.py` for the six cases BOTH of stage
3's tail landings put here.  Four are the ones the DATE AND CLOCK tail
landing grew past the room their own files had (plan P4-D328): the clock
role's own case (`clock_ladder`), the column partly at midnight
(`partial_midnight`), the bare dates beside midnight moments on a real
offset (`midnight_bare_offsets`), and the day-unit case
(`midnight_days`).  Two are the NUMERIC tail rule's (landing 3.3, plans
P4-D322 to P4-D327 and P4-D344): the tail reading of G5.3b with its two derived ends
(`tail_shape_ends`) and the made-up ramp of G5.3d (`tail_made_up_ramp`).
The numeric rule's other three are the eleventh file beside this one.

**Why they are a tenth file.**  A column of dates or clock times needs
`2F + 1` cells to publish a tail at all, and a case whose rule lives
BETWEEN the two boundaries needs a body of several ranks besides, so each
of the date cases grew at that landing.  Grown in place they carried
`generation-branch-vectors-2.json` to 261857 bytes and
`generation-branch-vectors.json` to 258476 against the provenance
manifest's 250000-byte cap (G14.2), so the four move here whole and both
files fall back under it.  The numeric cases could not go in an earlier
file either: plan P4-D295 draws the line at 200000 bytes, and the
seventh, the eighth and the ninth all stand past it.  No case was
dropped, no proof was shortened and the cap was not raised -- which is
the reason the fourth to the eleventh files exist, and it is written
here rather than left to be worked out from a byte count.

**Why these six columns could not go in an earlier file on their own
terms.**  Each of them publishes NO rung outside its two boundary
percents -- the tail rule of contract 6.7a -- and no case committed
before stage 3 does.  Withdrawn from the oracle, the whole of either
rule would leave the other nine files byte-identical.

Everything the second entry point says holds for this one word for word:
the transform, the proof layer, the words-as-inputs rule and every case
builder live in `make_generation_reference_vectors.py` beside this file,
and two copies of a proof layer would be two things that can drift apart.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

**WHERE THE NEXT CASE GOES** (plan P4-D295): here, while this file's
output stands under 200000 bytes, and the eleventh after it; the first
three files are full and take no case, and the seventh, eighth and ninth
stand past that line.

Usage:  python3 make_generation_branch_vectors_8.py --seed 0 --out <path>
        (the command line the data-provenance guard uses; the seed is
        accepted and ignored, because these vectors are a fixed transform
        of given words rather than a random sample).
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
