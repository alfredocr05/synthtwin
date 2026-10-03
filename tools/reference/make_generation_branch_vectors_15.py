"""The fifteenth file of synthtwin's generation reference vectors.

This is the FIFTEENTH entry point of one oracle, not a fifteenth oracle.
It asks `make_generation_reference_vectors.py` for the states of ranks
landing 3b.D0 (plan P4-D366) freezes method section G7.3f's shared steps
on: the pass over a unit of an hour with the day kept, over a day of
moments and through each gap's index, step 7b's chain, step 8.4's two
places, step 8.5's long pair, step 8.6's two-census trade and step 8.3's
bounded cycles, each with what the method's text makes of it.

**Why it is not a file of columns.**  Every other file freezes the cells
of a column put through the whole generator. On every date battery the
twins of landing 3b.D0 are the ones before it, so no column of whole
dates reaches these steps, and each is frozen on a state stated by hand:
`tests/test_stage3b_shared_steps.py` holds the product to the answers,
and turns each case red on its mutant. Plan P4-D364's numbering table
gives landing 3b.D0 this file.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

Usage:  python3 make_generation_branch_vectors_15.py --seed 0 --out <path>
        (the command line the data-provenance guard uses; the seed is
        accepted and ignored, because these vectors are a fixed transform
        of stated ranks rather than a random sample).
"""

import os
import runpy
import sys

ORACLE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "make_generation_reference_vectors.py",
)


def main(argv=None):
    """Write the fifteenth case set to the path given by --out.

    Returns the oracle's own outcome.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv, part=oracle["FIFTEENTH_BRANCH_PART"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
