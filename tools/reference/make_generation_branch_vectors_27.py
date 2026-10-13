"""The twenty-seventh file of synthtwin's generation reference vectors.

This is the TWENTY-SEVENTH entry point of one oracle, not a second oracle.
It asks `make_generation_reference_vectors.py` for the cases landing
3b.5's second step adds to method section G14.3 (lane C2, plan P4-D374):
G7A.4c's layout of a column of clock times on its minute census --
`clock_minutes_slots`, `clock_minutes_seconds`,
`clock_minutes_all_different`, `clock_minutes_rung_pins`,
`clock_minutes_no_tails` and `clock_minutes_rounding`.

**Why a twenty-seventh file.**  Plan P4-D364's numbering table gave this
landing no file, its cases to stand in the twenty-first; that file stands
at 247,663 bytes against the manifest's 250,000-byte cap, and the six
cases are about 93,000. So they open the first number no lane holds: no
cap is raised and no case is dropped. Its account names every file beside
it; the others' accounts are left as they stand, as the seventeenth's and
eighteenth's are.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

Usage:  python3 make_generation_branch_vectors_27.py --seed 0 --out <path>
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
    """Write the twenty-seventh case set to the path given by --out.

    Returns the oracle's own outcome, so a run that could not prove every
    number it would publish stops here exactly as it stops there.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv,
        part=oracle["TWENTY_SEVENTH_BRANCH_PART"],
    )


if __name__ == "__main__":
    raise SystemExit(main())
