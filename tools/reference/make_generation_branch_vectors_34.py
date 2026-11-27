"""The thirty-fourth file of synthtwin's generation reference vectors.

This is the THIRTY-FOURTH entry point of one oracle, not a second oracle.
It asks `make_generation_reference_vectors.py` for the cases of layer L0's
leftovers (lane BT3b, plan P4-D467; method G5.7a and G6.9): a column written
as its listed values meets its L0 bands' cut ranks before every other
published fact (G6.9 step 0), and G5.7a's (P6) lays it without its band
totals where a band holds cells and no listed value -- each frozen with the
answer the method's text gives it. The thirty-third is another lane's; the
merge renumbers a clash.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  The oracle
still imports neither synthtwin, nor numpy, nor pandas.

Usage:  python3 make_generation_branch_vectors_34.py --seed 0 --out <path>
        (the command line the data-provenance guard uses; the seed is
        accepted and ignored, because these vectors are a fixed transform
        of given cases rather than a random sample).
"""

import os
import runpy
import sys

ORACLE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "make_generation_reference_vectors.py",
)


def main(argv=None):
    """Write the thirty-fourth case set to the path given by --out."""
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv,
        part=oracle["THIRTY_FOURTH_BRANCH_PART"],
    )


if __name__ == "__main__":
    raise SystemExit(main())
