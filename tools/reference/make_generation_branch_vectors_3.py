"""The fifth file of synthtwin's generation reference vectors.

This is the FIFTH entry point of one oracle, not a fifth oracle.  It asks
`make_generation_reference_vectors.py` for the cases the repair of the
final Codex review of the number censuses added to method section G14.3
(plans P4-D142, P4-D145 and P4-D147), which live in a file of their own
only because the second and third files each stand within a few kilobytes
of the provenance manifest's 250000-byte cap (G14.2).  Everything the
second entry point says holds for this one word for word: the transform,
the proof layer, the words-as-inputs rule and every case builder live in
`make_generation_reference_vectors.py` beside this file, and two copies of
a proof layer would be two things that can drift apart.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

Usage:  python3 make_generation_branch_vectors_3.py --seed 0 --out <path>
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
    """Write the fifth case set to the path given by --out.

    Returns the oracle's own outcome, so a run that could not prove every
    number it would publish stops here exactly as it stops there.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv, part=oracle["THIRD_BRANCH_PART"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
