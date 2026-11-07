"""The thirty-first file of synthtwin's generation reference vectors.

This is the THIRTY-FIRST entry point of one oracle, not a second oracle.
It asks `make_generation_reference_vectors.py` for the cases A-P4-59's
amendment for layer L0 adds to method section G14.3a (lane BT2, plan
P4-D448): the cells of cases 5 and 8, the least move on today's strata of
cases 3, 4, 14 and 15, case 17's room, case 7 (b)'s windows, the clock's
knots of case 9, the workbook's classes of case 12 and the interface of
case 13 -- each frozen with the answer the method's text gives it.

**Why a thirty-first file.**  The twenty-eighth stands near the provenance
guard's largest file, and these are a later landing's cases.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

Usage:  python3 make_generation_branch_vectors_31.py --seed 0 --out <path>
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
    """Write the thirty-first case set to the path given by --out."""
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv,
        part=oracle["THIRTY_FIRST_BRANCH_PART"],
    )


if __name__ == "__main__":
    raise SystemExit(main())
