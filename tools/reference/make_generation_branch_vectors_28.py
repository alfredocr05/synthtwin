"""The twenty-eighth file of synthtwin's generation reference vectors.

This is the TWENTY-EIGHTH entry point of one oracle, not a second oracle.
It asks `make_generation_reference_vectors.py` for the cases layer L0's
rules add to method section G14.3a (lane BT, plan P4-D429, and its two
repairs): the cells of cases 1 (a), 1 (b), 2 and 7 (a), made by the
oracle's own number and date pipelines with layer L0 on them (G5.7c's
least move, G7.3l's edge runs) from each invented column's description
and the opening words of the stream at its seed, given as inputs; the
counts at each value of a sparse count short of today's count of
different values and over it, and of an age whose mode stands beside a
cut (G5.7c steps 3 and 4, the second repair); the heaps a ladder proves;
G7A.4d's halves of a cut census group, the boundary counted once; and
G4.2a's reserved cells by spelling in a text file and by class in a
workbook -- each frozen with the answer the method's text gives it.

**Why a twenty-eighth file.**  No branch file holds a case of layer L0,
and these are not cells of a column but answers of a rule, as the
fifteenth file's are, so they open the first number no lane holds.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

Usage:  python3 make_generation_branch_vectors_28.py --seed 0 --out <path>
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
    """Write the twenty-eighth case set to the path given by --out."""
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv,
        part=oracle["TWENTY_EIGHTH_BRANCH_PART"],
    )


if __name__ == "__main__":
    raise SystemExit(main())
