"""The twentieth file of synthtwin's generation reference vectors.

This is the TWENTIETH entry point of one oracle, not a twentieth oracle.
It asks `make_generation_reference_vectors.py` for the states landing
3b.4 (plan P4-D372) freezes method section G7.3h's own steps on -- the
clock pass on a field of minutes and on a field of seconds with their
heaps and their kin groups, KIN SHARES over two hours, and keeping the
cells at midnight -- hour 0 not free to take a heap at minute 0, alone and beside
hour 1 -- the exchange off a written midnight (its
first answer in the kin group, a swap with a lone rank, and a rank that
stays), PUT BACK once more after it, SUBSTITUTE, SPREAD and the tails
keeping the count at midnight, in a stratum narrower than their drawing
unit by the written unit -- and the drawing units G7.3's drawing rule gives: a half-hour grid, a
column on the hour, a column whose seconds alone are pinned, one
census group holding minute 0 and heaps beside a withheld census of the
rest, which pin nothing; and a draw laid on its unit: each with what the
method's text makes of it.

**Why it is not a file of columns.**  The steps are frozen one at a time,
each on a state stated by hand, so that a mutant of one step turns its
own case red whatever the steps around it do; `tests/test_stage3b_minutes.py`
holds the product to every answer, and turns each case red on its
mutant, and its battery puts whole columns through the generator. Plan
P4-D364's numbering table gives landing 3b.4 this file.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

Usage:  python3 make_generation_branch_vectors_20.py --seed 0 --out <path>
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
    """Write the twentieth case set to the path given by --out.

    Returns the oracle's own outcome.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv, part=oracle["TWENTIETH_BRANCH_PART"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
