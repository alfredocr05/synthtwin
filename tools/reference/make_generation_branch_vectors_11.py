"""The thirteenth file of synthtwin's generation reference vectors.

This is the THIRTEENTH entry point of one oracle, not a thirteenth
oracle. It asks `make_generation_reference_vectors.py` for the two
cases the skeptic pass of the repair of the oracle's derived end adds
to method section G14.3 (stage 3's review, verdict item 10): G5.3b step
4's padded ceiling, on a column padded to four figures whose high end
is held at 999 (`tail_pad_ceiling`), and the rule that no spelling
clamp pulls a derived end inside the tail's own mean distance, on a
column whose width census pools nine four-figure cells into five and
whose low boundary rung is 10000 itself (`tail_width_stands_aside`).

**Why they are a thirteenth file.**  Plan P4-D295 sends the next case
to the twelfth while its output stands under 200000 bytes, and it did,
at 187091; but these two cost about 70000 bytes each, and the twelfth
with either of them passes the manifest's 250000-byte cap. No cap is
raised and no case is dropped, so they open this one. Every other
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

**WHERE THE NEXT CASE GOES** (plan P4-D295): the twelfth, if it fits
under the cap, and otherwise here, while this file's output stands
under 200000 bytes.

Usage:  python3 make_generation_branch_vectors_11.py --seed 0 --out <path>
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
    """Write the thirteenth case set to the path given by --out.

    Returns the oracle's own outcome, so a run that could not prove every
    number it would publish stops here exactly as it stops there.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv, part=oracle["ELEVENTH_BRANCH_PART"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
