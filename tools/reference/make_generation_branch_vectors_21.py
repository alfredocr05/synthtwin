"""The twenty-first file of synthtwin's generation reference vectors.

This is the TWENTY-FIRST entry point of one oracle, not a second oracle.
It asks `make_generation_reference_vectors.py` for the cases landing 3b.5
adds to method section G14.3 (plan P4-D373): G7A.4b's rank rule for a
column of clock times publishing a census, heaps, a step and codes --
`clock_census_slots`, `clock_census_heap_splits_group`,
`clock_census_night`, `clock_census_seconds`, `clock_census_all_different`,
`clock_census_absent_inside`, `clock_census_boundary_below_heap`,
`clock_census_tail_heaps`, `clock_census_on_a_step`, `clock_census_codes`,
`clock_census_no_tails` and `clock_census_listed_tail_heap` -- and
G8.3's clock supply, `labels_clock_shaped`.

**Why a twenty-first file.**  Plan P4-D364's numbering table gives each
landing of stage 3b its own file, so lanes building at once never add to
one file's case set; this is landing 3b.5's. Every other file's own
account names this one, as each of them names all the others.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

Usage:  python3 make_generation_branch_vectors_21.py --seed 0 --out <path>
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
    """Write the twenty-first case set to the path given by --out.

    Returns the oracle's own outcome, so a run that could not prove every
    number it would publish stops here exactly as it stops there.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv,
        part=oracle["TWENTY_FIRST_BRANCH_PART"],
    )


if __name__ == "__main__":
    raise SystemExit(main())
