"""The twelfth file of synthtwin's generation reference vectors.

This is the TWELFTH entry point of one oracle, not a twelfth oracle.
It asks `make_generation_reference_vectors.py` for two of the three
cases the repair of the oracle's derived end adds to method section
G14.3 (stage 3's review, verdict item 10): the order of G5.3b step 4's
last three -- the sign rule, then the width clamps, then the mark
between thousands -- on a column whose one field width holds an end
the sign rule put at 1 (`tail_width_after_sign`), and both derived ends
of a column of numbers near 1e-200, which no grid of seventeen places
can hold (`tail_extreme_magnitude`). The third, `tail_mark_held`, is
the eleventh file beside it. The repair of the derived end's two
divergences adds `tail_marks_pooled`, the mark clamp counting a
census's named marks and its `(withheld)` pool together.

**Why they are a twelfth file.**  Plan P4-D295 draws the line: an entry
point takes the next case until its output passes 200000 bytes, and then
the next entry point is written the way the last one was.  The tenth
stood past that line and the eleventh passed it with `tail_mark_held`,
so the other two open this one. Every other file's own account names
this one, as each of them names all the others, so a reader who opens
any of the twelve is told at once that it is part of one artifact
rather than all of it.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

**WHERE THE NEXT CASE GOES** (plan P4-D295): not here, since
`tail_marks_pooled` took this file past 200000 bytes; the thirteenth.

Usage:  python3 make_generation_branch_vectors_10.py --seed 0 --out <path>
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
    """Write the twelfth case set to the path given by --out.

    Returns the oracle's own outcome, so a run that could not prove every
    number it would publish stops here exactly as it stops there.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv, part=oracle["TENTH_BRANCH_PART"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
