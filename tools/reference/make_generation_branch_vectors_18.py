"""The eighteenth file of synthtwin's generation reference vectors.

This is the EIGHTEENTH entry point of one oracle, not an eighteenth
oracle. It asks `make_generation_reference_vectors.py` for the states of
ranks landing 3b.3 (plan P4-D368) freezes method section G7.3i, the joint
day plan, on: pass A, G7.3f over the day-of-month census's thirty-four
bins with the days of every weekday group the weekday census counts
nought added to the holes, then pass B, G7.3f over the weekday census
with every move keeping the rank's day-of-month group. Six states --
billing on the 1st and the 15th, a visit on the 10th beside a weekday
census of seven groups, month ends on each month's own last day, billing
rolled to business days beside an empty weekend, births with a weekend
dip, and the 1st heaped beside a hole on each 15th -- each with what the
method's text makes of it.

**Why it is not a file of columns.**  As the fifteenth and seventeenth
files' states, a case is the passes' own input, stated by hand so that
each clause stands beside its mutant: `tests/test_stage3b_day_of_month.py`
holds the product to the answers and turns each red on its mutant, and
holds whole columns, through the whole generator, against the oracle's
own passes beside them. Plan P4-D364's numbering table gives landing 3b.3
this file.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

Usage:  python3 make_generation_branch_vectors_18.py --seed 0 --out <path>
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
    """Write the eighteenth case set to the path given by --out.

    Returns the oracle's own outcome.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv, part=oracle["EIGHTEENTH_BRANCH_PART"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
