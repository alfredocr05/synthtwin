"""The sixteenth file of synthtwin's generation reference vectors.

This is the SIXTEENTH entry point of one oracle, not a sixteenth oracle.
It asks `make_generation_reference_vectors.py` for the cases the end floor
of a date or clock tail adds to method section G14.3 (plan P4-D375):
G7.3b step 5's Bhatia-Davis reach, on 105 dates over 21 days
(`tail_end_least_reach`) and on 105 months over 21 months
(`tail_end_least_reach_months`).

**Why it is a sixteenth file.**  Every branch file stands past plan
P4-D295's 200000-byte line, so the next case opens a file of its own. No
cap is raised and no case is dropped. Every other file's own account
names this one, as each of them names all the others.

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
output stands under 200000 bytes; past it, a seventeenth entry point.

Usage:  python3 make_generation_branch_vectors_14.py --seed 0 --out <path>
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
    """Write the sixteenth case set to the path given by --out.

    Returns the oracle's own outcome, so a run that could not prove every
    number it would publish stops here exactly as it stops there.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv, part=oracle["FOURTEENTH_BRANCH_PART"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
