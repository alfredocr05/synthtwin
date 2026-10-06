"""The seventeenth file of synthtwin's generation reference vectors.

This is the SEVENTEENTH entry point of one oracle, not a seventeenth
oracle. It asks `make_generation_reference_vectors.py` for the states of
ranks landing 3b.D2 (plan P4-D367) freezes method section G7.3f's step 7c
on -- the escape of a moment to an end day of its gap at another clock,
where its own clock stands outside the gap there: three Wednesday
sessions through the whole pass, the count of different values kept, a
midnight kept, the nearer end day taken and a hole kept off -- each with
what the method's text makes of it.

**Why it is not a file of columns.**  As the fifteenth file's states, a
case is the pass's own input, stated by hand so that step 7c's every
clause stands beside its mutant: `tests/test_stage3b_weekday_moments.py`
holds the product to the answers and turns each red on its mutant, and
holds whole columns of moments, through the whole generator, against the
oracle's own pass beside them. Plan P4-D364's numbering table gives
landing 3b.D2 this file.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

Usage:  python3 make_generation_branch_vectors_17.py --seed 0 --out <path>
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
    """Write the seventeenth case set to the path given by --out.

    Returns the oracle's own outcome.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv, part=oracle["SEVENTEENTH_BRANCH_PART"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
