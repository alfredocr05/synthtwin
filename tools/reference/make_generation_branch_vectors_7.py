"""The ninth file of synthtwin's generation reference vectors.

This is the NINTH entry point of one oracle, not a ninth oracle.  It asks
`make_generation_reference_vectors.py` for the two cases the carried
numbers repair pass of 2026-09-19 added to method section G14.3: G6.5a's
push of a collision the walks leave along its band to the nearest free
point, and G6.5a's column-wide fill of a grid with no spare point (plans
P4-D147 and P4-D176) on a column where the band fill and the push both
stand aside, so that each of the three statements of the fill is held up
by a case of its own.

**Why they are a ninth file.**  Plan P4-D295 draws the line: the eighth
file takes the next case until its output passes 200000 bytes, and then
a ninth entry point is written the way the eighth was.  The carried
numbers pass of 2026-09-18 left the eighth at 235440 bytes, past that
line, so these two cases open this file.  No case was dropped, no proof
was shortened and the cap was not raised.  Everything the second entry
point says holds for this one word for word: the transform, the proof
layer, the words-as-inputs rule and every case builder live in
`make_generation_reference_vectors.py` beside this file, and two copies of
a proof layer would be two things that can drift apart.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

**WHERE THE NEXT CASE GOES** (plan P4-D295): in this file, until its
output passes 200000 bytes, and then in a tenth entry point written the
way this one was.  The first three files are full and take no case.

Usage:  python3 make_generation_branch_vectors_7.py --seed 0 --out <path>
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
    """Write the ninth case set to the path given by --out.

    Returns the oracle's own outcome, so a run that could not prove every
    number it would publish stops here exactly as it stops there.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv, part=oracle["SEVENTH_BRANCH_PART"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
