"""The thirty-third file of synthtwin's generation reference vectors.

This is the THIRTY-THIRD entry point of one oracle, not a second oracle.
It asks `make_generation_reference_vectors.py` for the content lists method
section G10.5 step 8 requires of a column of numbers too large or too small
to hold whose made-up spellings would be real values (lane ID-ROOM4, plan
P4-D489; the orchestrator's LANE ID-ROOM4 RULINGS 5 (2)): each cell one
letter or figure longer than the column's longest value, no run of figures
opened by a nought, the census, the shapes and the signs kept -- codes past
a double's range, a minus beside too-small fractions, a minus inside
brackets, codes beside numbers this format holds, and codes whose case
folds two spellings onto one. The merge renumbers a clash with another
lane's thirty-third.

**Why the oracle is loaded rather than imported by name.**  The provenance
guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path, so
a plain `import` of the module beside it would not resolve. Running it by
path is the same mechanism the guard runner itself uses, and it is permitted
in tools/ (the D6 restriction applies to src/ only). The oracle still imports
neither synthtwin, nor numpy, nor pandas.

Usage:  python3 make_generation_branch_vectors_33.py --seed 0 --out <path>
        (the seed is accepted and ignored: these vectors are a fixed
        transform of the blocks the oracle carries).
"""

import os
import runpy
import sys

ORACLE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "make_generation_reference_vectors.py",
)


def main(argv=None):
    """Write the thirty-third case set to the path given by --out."""
    oracle = runpy.run_path(ORACLE)
    return oracle["write_spelled_wider_vectors"](sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
