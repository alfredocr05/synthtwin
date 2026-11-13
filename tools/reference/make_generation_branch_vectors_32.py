"""The thirty-second file of synthtwin's generation reference vectors.

This is the THIRTY-SECOND entry point of one oracle, not a second oracle.
It asks `make_generation_reference_vectors.py` for the content lists method
section G8.3d requires of a pool counted in people and of a column of words
counted absent (lane PL, plan P4-D453; the orchestrator's LANE PL RULINGS 1
(3)): the countdown of a number pool and of a word pool, a pool of both
classes, the other member of a yes and a no and of a 0 and a 1, a clock, a
date, a closed alphabet, a unit kept as written, and the one word of a thin
column of words. The thirty-first is lane BT2's; the merge renumbers a clash.

**Why the oracle is loaded rather than imported by name.**  The provenance
guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path, so
a plain `import` of the module beside it would not resolve. Running it by
path is the same mechanism the guard runner itself uses, and it is permitted
in tools/ (the D6 restriction applies to src/ only). The oracle still imports
neither synthtwin, nor numpy, nor pandas.

Usage:  python3 make_generation_branch_vectors_32.py --seed 0 --out <path>
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
    """Write the thirty-second case set to the path given by --out."""
    oracle = runpy.run_path(ORACLE)
    return oracle["write_pool_in_people_vectors"](sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
