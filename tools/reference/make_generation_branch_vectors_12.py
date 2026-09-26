"""The fourteenth file of synthtwin's generation reference vectors.

This is the FOURTEENTH entry point of one oracle, not a fourteenth
oracle. It asks `make_generation_reference_vectors.py` for the case the
census of marks that is only a pool adds to method section G14.3 (plan
P4-D352): G6.1's seven marks spent over a pool by whole runs, each run
of one value going to the mark holding the fewest cells, on forty-four
whole numbers from 1001 to 1016 in runs of two to five
(`pool_alone_marks`); for the case that plan's second skeptic adds,
G6.1's trailing minus kept on figures with a point
(`trailing_minus_points`); and for the case the skeptic of its fifth
item adds, the exchange that gives a trailing minus its point
(`trailing_minus_exchange`).

**Why it is a fourteenth file.**  Plan P4-D295 sends the next case to a
file whose output stands under 200000 bytes, and the twelfth (227678
bytes) and the thirteenth (215303 bytes) both stand past that line, as
their own accounts said. No cap is raised and no case is dropped. Every
other file's own account names this one, as each of them names all the
others.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

**WHERE THE NEXT CASE GOES** (plan P4-D295): a fifteenth entry point,
`make_generation_branch_vectors_13.py` writing
tests/reference/generation-branch-vectors-13.json, because this, the
fourteenth, passed plan P4-D295's 200000-byte line at 213398 bytes with
`trailing_minus_exchange`, as the twelfth and thirteenth had before it.

Usage:  python3 make_generation_branch_vectors_12.py --seed 0 --out <path>
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
    """Write the fourteenth case set to the path given by --out.

    Returns the oracle's own outcome, so a run that could not prove every
    number it would publish stops here exactly as it stops there.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv, part=oracle["TWELFTH_BRANCH_PART"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
