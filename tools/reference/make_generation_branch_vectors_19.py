"""The nineteenth file of synthtwin's generation reference vectors.

This is the NINETEENTH entry point of one oracle, not a nineteenth
oracle. It asks `make_generation_reference_vectors.py` for the states
landing 3b.6 (plan P4-D369) freezes method section G7.3j, the dates that
stand out, on: steps 1 to 3, every body rank's gap -- a listed rank on
its own date, an ordinary rank in its part -- with the split repaired by a
flow to the censuses' groups and to the count's new days, and step 4,
each part's values drawn by key. Seven states -- a covered run, two
loose dates, a listed boundary day, two listed dates with a hole between
them, Monday and Thursday sessions over 104 weeks whose split the census
repair moves, sessions with stray rows whose split the repair moves for
the count's new days, and six Mays beside both censuses -- each with
what the method's text makes of it.

**Why it is not a file of columns.**  As the eighteenth file's states, a
case is the step's own input, stated as numbers so that each clause
stands beside its mutant: `tests/test_stage3b_heavy_dates.py` holds the
product to the answers and turns each red on its mutant, and holds whole
columns, through the whole generator, against the oracle's own content
beside them. Plan P4-D364's numbering table gives landing 3b.6 this
file.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

Usage:  python3 make_generation_branch_vectors_19.py --seed 0 --out <path>
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
    """Write the nineteenth case set to the path given by --out.

    Returns the oracle's own outcome.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv, part=oracle["NINETEENTH_BRANCH_PART"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
