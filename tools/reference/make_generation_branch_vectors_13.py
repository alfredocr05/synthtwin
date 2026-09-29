"""The fifteenth file of synthtwin's generation reference vectors.

This is the FIFTEENTH entry point of one oracle, not a fifteenth oracle.
It asks `make_generation_reference_vectors.py` for the cases the weekday
census of a column of dates adds to method section G14.3 (plan P4-D355):
G7.3f's day pass, one seeded column of 100 to 152 whole dates for each
of its steps (`weekday_count_put_back`, `weekday_days_moved`,
`weekday_gap_shares`, `weekday_hole_left`, `weekday_keeping_first`,
`weekday_runs_merged` and `weekday_whole_runs`).

**Why it is a fifteenth file.**  Landing 3b.1 froze these seven in the
fourteenth, which stood under plan P4-D295's 200000-byte line on that
landing's own branch. Stage 3's follow-up B had meanwhile taken the
fourteenth past that line (229836 bytes with landing 3b.0's case), and
with these seven beside it the fourteenth would pass the provenance
manifest's 250000-byte cap, so the integration of the two sends them
here, as plan P4-D295 sends the next case to a file whose output stands
under the line. No cap is raised and no case is dropped. Every other
file's own account names this one, as each of them names all the
others.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

**THE REVIEW OF LANDING 3b.0** (plan P4-D358) added six cases of the rule
that no count pass offers a day an absent spelling names:
`count_off_the_hole`, `every_day_absent`, `tail_end_off_the_hole`,
`tie_group_off_the_hole`, `stuck_day_counted` and `stuck_day_owed`.

**WHERE THE NEXT CASE GOES** (plan P4-D295): a sixteenth entry point. The
last three joined this file while its output stood under 200000 bytes,
and it stands past that line with them.

Usage:  python3 make_generation_branch_vectors_13.py --seed 0 --out <path>
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
    """Write the fifteenth case set to the path given by --out.

    Returns the oracle's own outcome, so a run that could not prove every
    number it would publish stops here exactly as it stops there.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv, part=oracle["THIRTEENTH_BRANCH_PART"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
