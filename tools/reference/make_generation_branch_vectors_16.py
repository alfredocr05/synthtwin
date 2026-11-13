"""The sixteenth file of synthtwin's generation reference vectors.

This is the SIXTEENTH entry point of one oracle, not a sixteenth oracle.
It asks `make_generation_reference_vectors.py` for the states landing
3b.2-H (plan P4-D371) freezes method section G7.3g's own steps on --
SAMEDAY, the escape and its day standing and its last resort, SPLIT,
RELIEF, PUT BACK when the count is long and when it is short and its last
resort, the proportional order, the step off
midnight, the dial's half day for the tail ranks, and the whole pass;
the details no other state turned red -- PUT BACK off a written
midnight, its short count asking only a shared minute, a tail rank kept
inside its stratum, RELIEF's give-back, SAMEPARENT asking no place of
a hole, and step 3's later round, where a whole unit's leaving gave a
group room; since its Codex review, a rank written at a sixtieth second,
counted in its written hour, and the ranks between two pins of one such
second -- and, on a field of minutes whose parent is the hour, the one clock
pass's tier in its kin group for the escape and PUT BACK; since lane J
(plan P4-D367), the escape paid back beside a weekday census, its payer
keeping the count, its payers given back, a payer kept off a hole and the
whole pass, and the whole pass with the round given back where it costs
the count of different values, even where the count is still missed
without it, and kept where the count is no nearer without it (lane J's
skeptics), and a unit a payer took a rank of asked as it stands (lane J's
Codex review) -- and the
tails G7.3b step 10 takes onto the dial's half day, on a low
tail, a high tail and one whose ranks must all differ: each with what the
method's text makes of it.

**Why it is not a file of columns.**  The steps are frozen one at a time,
each on a state stated by hand, so that a mutant of one step turns its
own case red whatever the steps around it do; `tests/test_stage3b_hour.py`
holds the product to every answer, and turns each case red on its
mutant, and its battery puts whole columns through the generator. Plan
P4-D364's numbering table gives landing 3b.2-H this file.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

Usage:  python3 make_generation_branch_vectors_16.py --seed 0 --out <path>
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
    """Write the sixteenth case set to the path given by --out.

    Returns the oracle's own outcome.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv, part=oracle["SIXTEENTH_BRANCH_PART"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
