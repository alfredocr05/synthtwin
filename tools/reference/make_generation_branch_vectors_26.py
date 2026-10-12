"""The twenty-sixth file of synthtwin's generation reference vectors.

This is the TWENTY-SIXTH entry point of one oracle, not a twenty-sixth
oracle. It asks `make_generation_reference_vectors.py` for the cases
landing R4 (plan P4-D384, numbers that are dates) freezes method section
G7.10 on: a cell written as a count read as the moment its counting
system names -- Excel's serials either side of its leap day, SAS and
Stata days, seconds and milliseconds before and after 1960, R's exponent
form, nanoseconds past 2**53, an Epic day with its contact number, a
comma for the point -- and a moment written back as its system's count,
spelled by a `count_form`: fifteen significant figures either side of
serial 10,000, one figure rounded half to even, six figures fixed and
trimmed, R's shorter form, a contact number and a comma.

**Why it is not a file of columns.**  A count is read and written cell by
cell, so each case is one cell or one moment and the method's answer;
`tests/test_stage3b_counted.py` holds the product to the answers and
turns each case red on its mutant. The integrator gave landing R4 this
file's number.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

Usage:  python3 make_generation_branch_vectors_26.py --seed 0 --out <path>
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
    """Write the twenty-sixth case set to the path given by --out.

    Returns the oracle's own outcome.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv, part=oracle["TWENTY_SIXTH_BRANCH_PART"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
