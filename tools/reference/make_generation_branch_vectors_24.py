"""The twenty-fourth file of synthtwin's generation reference vectors.

This is the TWENTY-FOURTH entry point of one oracle, not a twenty-fourth
oracle. It asks `make_generation_reference_vectors.py` for the cases
landing 3b.7 (plan P4-D378, the shared clock and the joint member)
freezes method sections G7.3k and G7.4 on: the field an instant
is WRITTEN at under its offset, a sixtieth second on the second before
its instant; the passes' frame taken back onto the shared clock run by
run; G7.4 step 1a's key for each block the layout fixes; and the form
step's bare dates on a clocked column of the joint member, capped per
gap and stood on midnights, on days of their own where the column is all
different.

**Why it is not a file of columns.**  Each case is one reading or one
state of ranks with the method's answer; `tests/test_stage3b_shared_clock.py`
holds the product to the answers and turns each case red on its mutant.
The number twenty-four was reserved for landing 3b.7 by plan P4-D364.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

Usage:  python3 make_generation_branch_vectors_24.py --seed 0 --out <path>
        (the command line the data-provenance guard uses; the seed is
        accepted and ignored, because these vectors are a fixed transform
        of stated cells rather than a random sample).
"""

import os
import runpy
import sys

ORACLE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "make_generation_reference_vectors.py",
)


def main(argv=None):
    """Write the twenty-fourth case set to the path given by --out.

    Returns the oracle's own outcome.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv, part=oracle["TWENTY_FOURTH_BRANCH_PART"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
